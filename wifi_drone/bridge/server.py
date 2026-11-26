"""Home Assistant Ingress and authenticated camera API."""

import asyncio
from contextlib import suppress, aclosing
import hmac
from ipaddress import IPv4Address
import json
import logging
import os
from pathlib import Path
import signal
from urllib.parse import urlsplit

from aiohttp import web
from wifi_drone_connect import camera_for_url, mjpeg_part

from .hub import FrameHub
from .wifi import WifiConnection, WifiSettings, stop_task

INGRESS_PROXY = "172.30.32.2"
WEB = Path(__file__).parent / "web"
HUB = web.AppKey("hub", FrameHub)
WIFI = web.AppKey("wifi", WifiConnection)
NO_CACHE = {"Cache-Control": "no-store"}
FRAME_WAIT = 20


async def status(request: web.Request) -> web.Response:
    payload = {"api_version": 1, "state": request.app[HUB].state,
               "capabilities": ["snapshot", "mjpeg"]}
    if wifi := request.app.get(WIFI):
        payload["wifi_state"] = wifi.state
        if wifi.capture_name:
            payload["capture"] = wifi.capture_name
    return web.json_response(payload, headers=NO_CACHE)


async def snapshot(request: web.Request) -> web.Response:
    frame = request.app[HUB].latest
    if frame is None:
        raise web.HTTPServiceUnavailable(text="Camera frame unavailable", headers=NO_CACHE)
    return web.Response(body=frame, content_type="image/jpeg", headers=NO_CACHE)


async def stream(request: web.Request) -> web.StreamResponse:
    hub = request.app[HUB]
    if hub.camera is None:
        raise web.HTTPServiceUnavailable(text="Camera source unconfigured", headers=NO_CACHE)
    async with aclosing(hub.frames()) as frames:
        try:
            frame = await asyncio.wait_for(anext(frames), FRAME_WAIT)
        except TimeoutError:
            raise web.HTTPServiceUnavailable(text="Camera frame unavailable", headers=NO_CACHE) from None
        response = web.StreamResponse(headers={
            **NO_CACHE, "Content-Type": "multipart/x-mixed-replace; boundary=frame",
            "X-Accel-Buffering": "no",
        })
        await response.prepare(request)
        with suppress(ConnectionError, TimeoutError):
            while True:
                await asyncio.wait_for(response.write(mjpeg_part(frame)), 5)
                frame = await asyncio.wait_for(anext(frames), FRAME_WAIT)
        return response


async def index(_: web.Request) -> web.FileResponse:
    return web.FileResponse(WEB / "index.html", headers=NO_CACHE)


def application(
    hub: FrameHub, *, token: str | None = None, ingress: bool = False,
    wifi: WifiConnection | None = None,
) -> web.Application:
    @web.middleware
    async def authenticate(request: web.Request, handler):
        if ingress and request.remote != INGRESS_PROXY:
            raise web.HTTPForbidden()
        if token is not None:
            supplied = request.headers.get("Authorization", "").encode()
            if not token or not hmac.compare_digest(supplied, f"Bearer {token}".encode()):
                raise web.HTTPUnauthorized(headers={"WWW-Authenticate": "Bearer"})
        return await handler(request)

    app = web.Application(middlewares=[authenticate])
    app[HUB] = hub
    if wifi is not None:
        app[WIFI] = wifi
    if token is None:
        app.router.add_get("/", index)
        app.router.add_static("/assets", WEB)
    app.router.add_get("/api/v1/status", status)
    app.router.add_get("/api/v1/snapshot.jpg", snapshot)
    app.router.add_get("/api/v1/stream.mjpg", stream, allow_head=False)
    return app


def options() -> tuple[FrameHub, str, bool, WifiConnection | None]:
    config_path = Path(os.environ.get("OPTIONS_FILE", "/data/options.json"))
    config = json.loads(config_path.read_text()) if config_path.is_file() else {}
    source = config.get("source_url", os.environ.get("DRONE_SOURCE_URL", "")).strip()
    transport = config.get("rtsp_transport", os.environ.get("DRONE_RTSP_TRANSPORT", "tcp"))
    copy = config.get("copy_mjpeg", os.environ.get("DRONE_COPY_MJPEG") == "1")
    token = config.get("api_token", os.environ.get("DRONE_API_TOKEN", ""))
    if token and (len(token) < 16 or any(not 33 <= ord(char) <= 126 for char in token)):
        raise ValueError("API token must contain at least 16 printable ASCII characters without spaces")
    camera = camera_for_url(source, transport, copy) if source else None
    wifi = None
    if ssid := config.get("wifi_ssid"):
        try:
            address = IPv4Address(urlsplit(source).hostname or "")
        except ValueError:
            raise ValueError("WiFi Helper mode requires a camera URL with a literal IPv4 address") from None
        wifi = WifiConnection(WifiSettings(
            ssid, config.get("wifi_password") or "", config.get("wifi_helper_host") or "",
            config.get("wifi_interface") or "", address, bool(config.get("record_traffic")),
        ))
    return FrameHub(camera), token, os.environ.get("DRONE_HA_INGRESS") == "1", wifi


async def serve() -> None:
    hub, token, ingress, wifi = options()
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)
    api = web.AppRunner(application(hub, token=token, wifi=wifi), handler_cancellation=True, access_log=None, shutdown_timeout=5)
    ui = web.AppRunner(application(hub, ingress=ingress, wifi=wifi), handler_cancellation=True, access_log=None, shutdown_timeout=5)
    try:
        await api.setup()
        await ui.setup()
        bind_host = "0.0.0.0" if ingress else "127.0.0.1"
        api_host = os.environ.get("DRONE_API_BIND", bind_host)
        await web.TCPSite(api, api_host, 8099).start()
        await web.TCPSite(ui, bind_host, 8098).start()
        if wifi is not None:
            await wifi.run(hub, stop)
        else:
            task = asyncio.create_task(hub.run())
            try:
                await stop.wait()
            finally:
                await stop_task(task)
    finally:
        await asyncio.gather(api.cleanup(), ui.cleanup())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
