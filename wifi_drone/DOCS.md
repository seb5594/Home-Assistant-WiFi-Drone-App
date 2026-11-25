# WiFi Drone Connect

The app provides live camera video, JPEG snapshots and a local API for the independent Home Assistant integration.

## Join the drone's access point

1. Install and start [WiFi App Helper](https://github.com/seb5594/Home-Assistant-WiFi-Helper-App). Reserve a spare adapter using the helper's setup instructions. The driver must advertise both AP and managed modes, and the helper must list the adapter as eligible.
2. Set the same private `pairing_token` in both apps. This is independent of `api_token`, which authenticates the camera API.
3. Set `wifi_ssid` to the exact WiFi name of the drone. For an open access point, leave `wifi_password` empty. For WPA2-Personal, enter its passphrase. Specify `wifi_interface` if the helper has multiple eligible radios.
4. Set `source_url` to a camera URL with the drone's IPv4 address and start the app. Open **Web UI** to follow the connection and view the result.

The helper leases the spare adapter to the app's isolated network namespace. DHCP configures the leased IPv4 address and a host route for the camera. The app ignores DHCP offers for the default route and DNS. The radio is returned on shutdown. If the helper connection is lost or the return cannot be confirmed, the app stops so the helper can recover the adapter.

For cameras already reachable from the app, leave `wifi_ssid` empty. This preserves the direct network mode.

## Camera URLs

| Camera | Source example |
| --- | --- |
| Standard RTSP | `rtsp://192.168.1.1:554/live` |
| HTTP MJPEG | `http://192.168.1.1:8080/?action=stream` |
| KY UFO / some `FLY-UFO-…` models | `kyufo://192.168.1.1` sends a video heartbeat and reads RTSP. Add `?rotate=0` if the camera is upright. |
| JieLi / some `HF_…` models | `jieli://192.168.80.1` starts the JPEG stream over CTP and receives fragmented JPEG on UDP 2224 or whole JPEG datagrams on UDP 6666. |

Select TCP or UDP for RTSP. Enable `copy_mjpeg` only for MJPEG sources, with `?rotate=0` for KY UFO passthrough. Close the vendor camera preview if the drone accepts only one viewer. The Gear2Play Sky Cam's SSID is `SKY CAM DRONE`. Its camera address and transport still need to be confirmed on the actual unit. The examples come from the [OpenIPC toy camera notes](https://github.com/OpenIPC/decoder/blob/v2/docs/toys.md).

## Bridge API

To use the independent WiFi Drone integration, set an `api_token` of at least 16 printable ASCII characters without spaces and restart the app. A blank token disables API access while the Ingress view remains available.

For a direct install from this app repository, the address is `http://c3b88628-wifi-drone:8099`. If installed through another app catalog, use the app's hostname from the Info tab. Port 8099 is only published to the host if you set a port mapping. For a bridge on another host, use its reachable address and HTTPS when the connection crosses a network you do not control.

All these endpoints on port 8099 require `Authorization: Bearer <api_token>`.

| Endpoint | Response |
| --- | --- |
| `GET /api/v1/status` | API version, camera state, capabilities and, in WiFi Helper mode, `wifi_state` |
| `GET /api/v1/snapshot.jpg` | Latest JPEG, or 503 while a frame is unavailable |
| `GET /api/v1/stream.mjpg` | Multipart MJPEG, or 503 while a frame is unavailable |

All viewers share one camera connection. The bridge reconnects and clears stale frames when the source disconnects. The preview carries video only.

The container bundles the WiFi Helper SDK from the pinned release revision in the Dockerfile, with the upstream SDK license and archive checksum. The app and helper use protocol 3.
