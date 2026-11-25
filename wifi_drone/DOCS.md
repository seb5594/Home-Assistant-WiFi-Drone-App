# WiFi Drone Connect

The app runs a local bridge between an RTSP or HTTP(S) camera source and Home Assistant.

1. Connect the Home Assistant host to a network that can reach the camera. If the drone provides its own WiFi network, the host can use a second network interface to keep its regular connection.
2. Set `source_url` to the camera's known RTSP or HTTP(S) stream. Select TCP or UDP for RTSP. Enable `copy_mjpeg` only when the source already uses MJPEG.
3. Start the app and open its Web UI for live video and JPEG snapshots.
4. To use the independent WiFi Drone integration, set an `api_token` of at least 16 printable ASCII characters without spaces and restart the app. The bridge API operates over port 8099. An empty token disables API access while the Ingress view remains available.

For a direct install of this app repository, the internal address is `http://c3b88628-wifi-drone:8099`. If installed through another app catalog, use the app's hostname from the Info tab. The port is not published to the LAN unless you map it in the configuration. For a bridge on another host, use its reachable address and HTTPS when the connection crosses a network you do not control.

## Bridge API

All these endpoints on port 8099 require `Authorization: Bearer <api_token>`.

| Endpoint | Response |
| --- | --- |
| `GET /api/v1/status` | API version, bridge state and media capabilities |
| `GET /api/v1/snapshot.jpg` | Latest JPEG, or 503 while a frame is unavailable |
| `GET /api/v1/stream.mjpg` | Multipart MJPEG, or 503 when a frame cannot be obtained |

There is one camera session per app instance. The bridge reconnects on loss of the source and clears stale frames. The live preview contains video only. The Gear2Play Sky Cam's stream endpoint still needs to be verified on hardware.
