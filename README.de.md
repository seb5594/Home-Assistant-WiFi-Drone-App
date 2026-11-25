# Vorlage für Home-Assistant-Apps

[🇬🇧 English](README.md) · **🇩🇪 Deutsch**

Aus dieser Vorlage entsteht eine Supervisor-App mit Image-Builds für mehrere Architekturen, Laufzeittests und Veröffentlichung auf GHCR.

1. Erstelle aus der Vorlage ein Repository mit dem Namen `Home-Assistant-<Projekt>-App`, damit der App-Katalog es findet.
2. Benenne `example-app/` nach deinem Slug. Passe in `config.yaml` den Slug, Namen, die Beschreibung, URL und Optionen an.
3. Aktualisiere das Repository-Label im Dockerfile und ersetze die Beispielausgabe in `run.sh`. Für ältere Architekturen wie `armv7` verwendet das Dockerfile eigene `*_LEGACY`-Paketversionen.
4. Passe `.github/tests/runtime.sh` an. Die Pipeline führt das Skript im gebauten Image aus.
5. Hinterlege `ORCHESTRATION_PAT` für den Zugriff auf die private Workflow-Engine. Mit einem lokalen Checkout unter `.engine/` erzeugt `python .engine/.scripts/readme.py` den Titel und die Badges der englischen README.
6. Erhöhe für ein Release `version` in `config.yaml` und `BUILD_VERSION` im Dockerfile gemeinsam. Beschreibe im [Changelog](example-app/CHANGELOG.md), was sich für Nutzer ändert.
