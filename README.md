<!-- header:begin (generated from project metadata) -->
<h1 align="center">
  <img src="https://raw.githubusercontent.com/seb5594/Home-Assistant-WiFi-Drone-App/dev/wifi_drone/logo.png" alt="WiFi Drone Connect" width="360" height="90">
  <br>
  WiFi Drone Connect
</h1>

<p align="center">
  <a href="https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fseb5594%2FHome-Assistant-Apps"><img src="https://img.shields.io/static/v1?label=Home%20Assistant&amp;message=Add%20app%20repository&amp;color=18BCF2&amp;logo=homeassistant&amp;logoColor=white&amp;style=for-the-badge" alt="Home Assistant" height="28"></a><br>
  <a href="https://github.com/seb5594/Home-Assistant-WiFi-Drone-App/releases/tag/v0.3.0"><img src="https://img.shields.io/static/v1?label=app%20version&amp;message=0.3.0&amp;color=1877A5&amp;style=for-the-badge" alt="app version" height="28"></a>
  <img src="https://img.shields.io/static/v1?label=image%20pulls&amp;message=12&amp;color=1877A5&amp;style=for-the-badge" alt="image pulls" height="28"><br>
  <img src="https://img.shields.io/static/v1?label=stage&amp;message=stable&amp;color=2F855A&amp;style=flat" alt="stage" height="20">
  <img src="https://img.shields.io/static/v1?label=ingress&amp;message=enabled&amp;color=7C3AED&amp;style=flat" alt="ingress" height="20">
  <img src="https://img.shields.io/static/v1?label=arch%20%26%20size&amp;message=amd64%2083.7%20%C2%B7%20aarch64%2080.8%20MiB&amp;color=157F71&amp;style=flat" alt="arch &amp; size" height="20">
  <a href="https://github.com/seb5594/home-assistant-base-multi-arch"><img src="https://img.shields.io/static/v1?label=base%20image&amp;message=3.24-2026.11.0&amp;color=1877A5&amp;style=flat" alt="base image" height="20"></a>
  <img src="https://img.shields.io/static/v1?label=mounts%20%28read-write%29&amp;message=share&amp;color=B45309&amp;style=flat" alt="mounts (read-write)" height="20">
  <img src="https://img.shields.io/static/v1?label=privileged&amp;message=NET_ADMIN%2C%20NET_RAW&amp;color=B45309&amp;style=flat" alt="privileged" height="20"><br>
  <a href="https://github.com/seb5594/Home-Assistant-WiFi-Drone-App/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/seb5594/Home-Assistant-WiFi-Drone-App/ci.yml?branch=dev&amp;label=checks&amp;style=flat" alt="checks" height="20"></a>
  <img src="https://img.shields.io/static/v1?label=runtime%20tests&amp;message=2%20passed&amp;color=2F855A&amp;style=flat" alt="runtime tests" height="20">
  <a href="https://github.com/seb5594/Home-Assistant-Apps/issues"><img src="https://img.shields.io/github/issues/seb5594/Home-Assistant-WiFi-Drone-App?label=issues&amp;style=flat" alt="issues" height="20"></a><br>
  <a href="https://paypal.me/seb5594"><img src="https://img.shields.io/static/v1?label=Support&amp;message=PayPal&amp;color=0070BA&amp;logo=paypal&amp;logoColor=white&amp;style=for-the-badge" alt="PayPal" height="24"></a>
  <a href="https://buymeacoffee.com/seb5594"><img src="https://raw.githubusercontent.com/seb5594/Home-Assistant-Apps/473dc258f963096745aac327df54950eb9b59066/.github/assets/support-beer.svg" alt="Buy me a beer" height="24"></a><br>
  <a href="https://github.com/seb5594/Home-Assistant-Apps#license"><img src="https://img.shields.io/github/license/seb5594/Home-Assistant-WiFi-Drone-App?label=license&amp;style=flat" alt="license" height="20"></a>
</p>
<!-- header:end -->

[Deutsch](README.de.md)

Local camera bridge for RTSP, HTTP(S), KY UFO, JieLi/HF and Lewei video sources. The Home Assistant app provides an Ingress live view, JPEG snapshots and an authenticated API for the companion integration.

1. Add [this app repository](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fseb5594%2FHome-Assistant-WiFi-Drone-App) in Home Assistant.
2. Install **WiFi Drone Connect**. For a drone access point, start [WiFi App Helper](https://github.com/seb5594/Home-Assistant-WiFi-Helper-App) and set the SSID, pairing secret and camera URL in the Drone app.
3. Open the app's Web UI or install the [WiFi Drone integration](https://github.com/seb5594/hass-wifi_drone-integration) for native camera and connectivity entities.

[Configuration and API](wifi_drone/DOCS.md) · [Python SDK](https://github.com/seb5594/wifi-drone-connect)

The Gear2Play Sky Cam's actual stream protocol and endpoint still need to be verified on hardware.

<!-- support:begin (generated, shared text) -->
## Say thanks

All my projects are built in my spare time, just for the fun of it. Still, they take a lot of time and care, and many of the smart home gadgets I buy end up here because I want to make them cloud-free and smart-home ready. Every bit of support means a lot to me.

If my work helped you or turned out to be useful, show your appreciation with a hot drink for my next sleepless night.

[![PayPal](https://img.shields.io/static/v1?label=Support&message=PayPal&color=0070BA&logo=paypal&logoColor=white&style=for-the-badge)](https://paypal.me/seb5594) [![Buy me a beer](https://raw.githubusercontent.com/seb5594/Home-Assistant-Apps/473dc258f963096745aac327df54950eb9b59066/.github/assets/support-beer.svg)](https://buymeacoffee.com/seb5594)
<!-- support:end -->

<!-- license:begin (generated from the license file) -->
## License

[![license](https://img.shields.io/static/v1?label=license&message=MIT&color=5B6770&style=flat)](LICENSE)

Published under the [MIT License](LICENSE).
<!-- license:end -->
