# WiFi Drone Connect

The app provides live camera video, JPEG snapshots and a local API for the independent Home Assistant integration.

## Join the drone's access point

1. Install and start [WiFi App Helper](https://github.com/seb5594/Home-Assistant-WiFi-Helper-App). Reserve a spare adapter using the helper's setup instructions. The driver must advertise both AP and managed modes, and the helper must list the adapter as eligible.
2. Leave `wifi_helper_host` at its default (`4c7fee11-wifi-helper`); change it only if the helper comes from another app repository, for example `local-wifi-helper`. There is no pairing secret. `api_token` is independent and authenticates the camera API.
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
| Gear2Play Sky Cam | `jieli://192.168.80.1?ver=2` matches the camera-control address and access version seen in a hardware capture. Incoming video still needs a hardware check. |
| JieLi / some `HF_…` models | `jieli://192.168.80.1` starts the JPEG stream over CTP and receives fragmented JPEG on UDP 2224 or whole JPEG datagrams on UDP 6666. |
| Lewei / some `WiFi-720P-…` models | `lewei://192.168.0.1` receives H.264 camera video on TCP 7060. The adapter handles stream types 0 and 1. |

Select TCP or UDP for RTSP. Enable `copy_mjpeg` only for MJPEG sources, with `?rotate=0` for KY UFO passthrough. Close the vendor camera preview if the drone accepts only one viewer. For Sky Cam, enter the full SSID from Android's network details, including the suffix after `SKY CAM DRONE`. The examples come from the [OpenIPC toy camera notes](https://github.com/OpenIPC/decoder/blob/v2/docs/toys.md).

## Diagnose a missing JieLi picture

Open the app log after the first video timeout. The log shows whether the camera answered `APP_ACCESS` and `OPEN_RT_STREAM` and counts packets and complete JPEGs from the camera separately for UDP 2224 and 6666. For UDP 6666 it also reports possible RTP payload types. A count of zero covers only those listeners.

## Record the drone's traffic for Wireshark

If the picture stays black, the camera may send its video somewhere the app does not listen. Switch on **Record drone traffic** (`record_traffic`) and restart the app. From the moment the radio comes up, everything it sends and receives (association, DHCP, camera control, video) is written to a pcap file under `/share/wifi-helper-private/captures/`. The file name is in `GET /api/v1/status` as `capture` and in the app log. Only the newest ten files are kept.

To read the file from Windows, enable *Packet capture* and a *Capture token* in WiFi App Helper and follow its [Wireshark guide](https://github.com/seb5594/Home-Assistant-WiFi-Helper-App/blob/main/docs/wireshark.en.md). The fastest first look needs no Wireshark: open `/v1/captures/<file>/summary` on the helper for a table of who talked to whom on which port. In Wireshark, filter `ip.addr == 192.168.80.1` (your camera address) and look at which UDP or TCP ports carry large, steady packets after the stream request. Report that port, the payload start (first bytes in hex) and the packet size; it is what the adapter needs.

Recordings contain device identifiers and video. Delete them afterwards and do not post them unredacted. Turn the option off again when you are done.

## Bridge API

To use the independent WiFi Drone integration, set an `api_token` of at least 16 printable ASCII characters without spaces and restart the app. A blank token disables API access while the Ingress view remains available.

For a direct install from this app repository, the address is `http://c3b88628-wifi-drone:8099`. If installed through another app catalog, use the app's hostname from the Info tab. Port 8099 is only published to the host if you set a port mapping. For a bridge on another host, use its reachable address and HTTPS when the connection crosses a network you do not control.

All these endpoints on port 8099 require `Authorization: Bearer <api_token>`.

| Endpoint | Response |
| --- | --- |
| `GET /api/v1/status` | API version, camera state, capabilities and, in WiFi Helper mode, `wifi_state` and, while recording, `capture` |
| `GET /api/v1/snapshot.jpg` | Latest JPEG, or 503 while a frame is unavailable |
| `GET /api/v1/stream.mjpg` | Multipart MJPEG, or 503 while a frame is unavailable |

All viewers share one camera connection. The bridge reconnects and clears stale frames when the source disconnects. The preview carries video only.

The container bundles the WiFi Helper SDK from the pinned release revision in the Dockerfile, with the upstream SDK license and archive checksum. The app and helper use protocol 4.
