# WiFi Drone Connect für Home Assistant

[English](README.md)

Lokale Kamera-Bridge für RTSP, HTTP(S), KY UFO, JieLi/HF und Lewei. Die Home-Assistant-App bietet ein Livebild über Ingress, JPEG-Schnappschüsse und eine authentifizierte API für die separate Integration.

1. Füge [dieses App-Repository](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fseb5594%2FHome-Assistant-WiFi-Drone-App) in Home Assistant hinzu.
2. Installiere **WiFi Drone Connect**. Für das WLAN der Drohne starte [WiFi App Helper](https://github.com/seb5594/Home-Assistant-WiFi-Helper-App) und trage SSID und Kamera-URL in der Drone App ein. Der Helper wird über seinen Hostnamen gefunden; ein Kopplungsgeheimnis gibt es nicht.
3. Öffne die Weboberfläche der App oder installiere die [WiFi-Drone-Integration](https://github.com/seb5594/hass-wifi_drone-integration) für Kamera und Verbindungsstatus als Entitäten.

[Konfiguration und API](wifi_drone/DOCS.md) · [Python-SDK](https://github.com/seb5594/wifi-drone-connect)

Ein Mitschnitt der Gear2Play Sky Cam bestätigt die Kamerasteuerung unter `192.168.80.1:3333`. Das Livebild muss noch am Gerät geprüft werden: Die App kann den Verkehr der Drohne als pcap-Datei für Wireshark aufzeichnen (Option *Drohnen-Verkehr aufzeichnen*, Anleitung in der [Dokumentation](wifi_drone/DOCS.md#record-the-drones-traffic-for-wireshark), englisch).

## Lizenz

Veröffentlicht unter der [MIT-Lizenz](LICENSE).
