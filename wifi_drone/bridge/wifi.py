"""Run the camera on a station-mode radio leased from WiFi App Helper."""

import asyncio
from contextlib import AsyncExitStack, suppress
from dataclasses import dataclass
import hashlib
from ipaddress import IPv4Address
import json
import logging
import os
from pathlib import Path
import tempfile
import threading

from wifi_helper import Client, HelperRejected, HelperUnavailable, ProtocolMismatch
from wifi_helper.capture import PcapRecorder

from .hub import FrameHub

LOGGER = logging.getLogger(__name__)
DHCP_HOOK = Path(__file__).with_name("station_dhcp.py")


class RetryWifi(Exception):
    """The app may retry after the leased radio has been returned."""


class RadioRecoveryRequired(RuntimeError):
    """The container must exit so the helper can recover the radio."""


async def command(*args: str) -> str:
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
    )
    try:
        async with asyncio.timeout(5):
            stdout, _ = await process.communicate()
    except (TimeoutError, asyncio.CancelledError):
        await stop_worker(process)
        raise
    if process.returncode != 0:
        raise RetryWifi(f"{args[0]} failed")
    return stdout.decode(errors="replace")


async def stop_worker(process: asyncio.subprocess.Process) -> None:
    if process.returncode is not None:
        return
    with suppress(ProcessLookupError):
        process.terminate()
    try:
        await asyncio.wait_for(process.communicate(), 2)
    except TimeoutError:
        with suppress(ProcessLookupError):
            process.kill()
        await process.communicate()


async def wait_for_stop(stop: asyncio.Event, seconds: float) -> None:
    with suppress(TimeoutError):
        await asyncio.wait_for(stop.wait(), seconds)


async def stop_task(task: asyncio.Task) -> None:
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


def supplicant_config(ssid: str, password: str, control: str) -> str:
    network = ssid.encode("utf-8")
    if not 1 <= len(network) <= 32:
        raise ValueError("Drone SSID must contain 1 to 32 UTF-8 bytes")
    if password:
        secret = password.encode("utf-8")
        if not 8 <= len(secret) <= 63:
            raise ValueError("WPA2 password must contain 8 to 63 UTF-8 bytes")
        psk = hashlib.pbkdf2_hmac("sha1", secret, network, 4096, 32).hex()
        security = f"key_mgmt=WPA-PSK\n    proto=RSN\n    psk={psk}"
    else:
        security = "key_mgmt=NONE"
    return f"ctrl_interface={control}\nnetwork={{\n    ssid={network.hex()}\n    {security}\n}}\n"


@dataclass(frozen=True, slots=True)
class WifiSettings:
    ssid: str
    password: str
    helper_host: str
    interface: str
    camera_ip: IPv4Address
    record_traffic: bool = False

    def __post_init__(self) -> None:
        supplicant_config(self.ssid, self.password, "/run")
        if (
            self.camera_ip.is_unspecified or self.camera_ip.is_loopback
            or self.camera_ip.is_multicast or self.camera_ip.is_reserved
        ):
            raise ValueError("WiFi Helper mode requires a unicast IPv4 camera address")


class WifiConnection:
    def __init__(self, settings: WifiSettings) -> None:
        self.settings = settings
        self.state = "waiting_helper"
        self.lost = threading.Event()
        self.capture_name: str | None = None  # Newest pcap of the drone radio, when recording is on.

    def check_lease(self) -> None:
        if self.lost.is_set():
            raise RadioRecoveryRequired("WiFi Helper lease lost. Exiting for radio recovery.")

    def acquire(self):
        client = Client(self.settings.helper_host, lost=self.lost)
        adapters = [item["name"] for item in client.inventory()["adapters"] if item["eligible"]]
        selected = self.settings.interface
        if not selected and len(adapters) == 1:
            selected = adapters[0]
        if selected not in adapters:
            if not selected and adapters:
                LOGGER.info("Eligible WiFi Helper adapters: %s", ", ".join(adapters))
            raise RetryWifi("Select one eligible adapter in the app configuration")
        return client.acquire(selected)

    async def run(self, hub: FrameHub, stop: asyncio.Event) -> None:
        while not stop.is_set():
            self.state = "waiting_helper"
            try:
                await self.run_once(hub, stop)
            except (HelperUnavailable, HelperRejected, ProtocolMismatch) as error:
                self.check_lease()
                self.state = {
                    HelperUnavailable: "waiting_helper",
                    HelperRejected: "helper_rejected",
                    ProtocolMismatch: "helper_protocol",
                }[type(error)]
            except (RetryWifi, OSError, TimeoutError, ValueError, RuntimeError) as error:
                self.check_lease()
                if isinstance(error, RadioRecoveryRequired):
                    raise
                if self.state == "waiting_helper":
                    self.state = "adapter_unavailable"
                else:
                    self.state = "joining_failed"
                if isinstance(error, RetryWifi):
                    LOGGER.info("Drone WiFi: %s", error)
                else:
                    LOGGER.info("Drone WiFi failed during setup (%s)", type(error).__name__)
            await wait_for_stop(stop, 8)

    async def run_once(self, hub: FrameHub, stop: asyncio.Event) -> None:
        radio = await asyncio.to_thread(self.acquire)
        try:
            async with AsyncExitStack() as resources:
                if stop.is_set():
                    return
                self.state = "joining"
                directory = Path(resources.enter_context(tempfile.TemporaryDirectory(prefix="drone-wifi-")))
                control = directory / "control"
                config = directory / "wpa.conf"
                config.write_text(supplicant_config(self.settings.ssid, self.settings.password, str(control)))
                interface = radio.interface
                # The camera route uses IPv4; do not generate IPv6 addresses on this radio.
                await command("ip", "link", "set", "dev", interface, "addrgenmode", "none")
                await command("ip", "link", "set", "dev", interface, "up")
                self.start_recording(resources, interface)
                wpa = await self.worker(resources, "wpa_supplicant", "-D", "nl80211",
                                        "-i", interface, "-c", str(config))
                await self.await_ready(stop, (wpa,), self.associated, interface, control)
                if stop.is_set():
                    return
                self.state = "dhcp"
                dhcp = await self.worker(
                    resources, "udhcpc", "-f", "-n", "-i", interface, "-s", str(DHCP_HOOK),
                    env={**os.environ, "DRONE_CAMERA_IP": str(self.settings.camera_ip),
                         "DRONE_WIFI_INTERFACE": interface},
                )
                await self.await_ready(stop, (wpa, dhcp), self.routed, interface)
                if stop.is_set():
                    return
                self.state = "connected"
                capture = asyncio.create_task(hub.run())
                resources.push_async_callback(stop_task, capture)
                while not stop.is_set():
                    self.check_lease()
                    if any(worker.returncode is not None for worker in (wpa, dhcp)):
                        raise RetryWifi("WiFi association or DHCP worker stopped")
                    if not await self.associated(interface, control) or not await self.routed(interface):
                        raise RetryWifi("WiFi association or camera route lost")
                    if capture.done():
                        capture.result()
                    await wait_for_stop(stop, 1)
        finally:
            await hub.clear()
            self.check_lease()
            try:
                await asyncio.to_thread(radio.release)
            except Exception as error:
                raise RadioRecoveryRequired("Radio return unconfirmed. Exiting for helper recovery.") from error

    def start_recording(self, resources: AsyncExitStack, interface: str) -> None:
        """Record everything the drone radio sees (association, DHCP, camera control and video) for Wireshark.

        Recording is a diagnostic aid and must never stop the camera, so every failure is only logged.
        """
        if not self.settings.record_traffic:
            return
        try:
            recorder = PcapRecorder(interface, "drone").start()
        except OSError as error:
            LOGGER.warning("Traffic recording unavailable (%s). The app needs NET_RAW.", type(error).__name__)
            return
        self.capture_name = recorder.path.name
        resources.callback(recorder.stop)
        LOGGER.info("Recording drone traffic to %s", recorder.path)

    @staticmethod
    async def worker(resources: AsyncExitStack, *args: str, env=None) -> asyncio.subprocess.Process:
        process = await asyncio.create_subprocess_exec(
            *args, env=env, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
        )
        resources.push_async_callback(stop_worker, process)
        return process

    async def await_ready(self, stop, workers, check, *args) -> None:
        deadline = asyncio.get_running_loop().time() + 25
        while not stop.is_set():
            self.check_lease()
            if any(worker.returncode is not None for worker in workers):
                raise RetryWifi(f"WiFi worker exited during {self.state}")
            if await check(*args):
                return
            if asyncio.get_running_loop().time() >= deadline:
                raise RetryWifi(f"Timed out during {self.state}")
            await wait_for_stop(stop, 0.5)

    async def associated(self, interface: str, control: Path) -> bool:
        try:
            status = await command("wpa_cli", "-p", str(control), "-i", interface, "status")
        except RetryWifi:
            return False
        return "wpa_state=COMPLETED" in status.splitlines()

    async def routed(self, interface: str) -> bool:
        try:
            routes = json.loads(await command("ip", "-j", "-4", "route", "get", str(self.settings.camera_ip)))
        except RetryWifi:
            return False
        return len(routes) == 1 and routes[0].get("dev") == interface
