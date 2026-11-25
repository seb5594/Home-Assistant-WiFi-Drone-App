# WiFi Drone Connect für Home Assistant

[English](README.md)

Lokale Kamera-Bridge für RTSP, HTTP(S), KY UFO, JieLi/HF und Lewei. Die Home-Assistant-App bietet ein Livebild über Ingress, JPEG-Schnappschüsse und eine authentifizierte API für die separate Integration.

1. Füge [dieses App-Repository](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fseb5594%2FHome-Assistant-WiFi-Drone-App) in Home Assistant hinzu.
2. Installiere **WiFi Drone Connect**. Für das WLAN der Drohne starte [WiFi App Helper](https://github.com/seb5594/Home-Assistant-WiFi-Helper-App) und trage SSID, Kopplungsgeheimnis und Kamera-URL in der Drone App ein.
3. Öffne die Weboberfläche der App oder installiere die [WiFi-Drone-Integration](https://github.com/seb5594/hass-wifi_drone-integration) für Kamera und Verbindungsstatus als Entitäten.

[Konfiguration und API](wifi_drone/DOCS.md) · [Python-SDK](https://github.com/seb5594/wifi-drone-connect)

Das konkrete Stream-Protokoll und die Kamera-Adresse der Gear2Play Sky Cam müssen noch an einem Gerät bestätigt werden.

## Lizenz

Veröffentlicht unter der [MIT-Lizenz](LICENSE).
