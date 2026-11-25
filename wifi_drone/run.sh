#!/usr/bin/env bash
set -Eeuo pipefail
cd /opt/wifi-drone
exec python3 -m bridge.server
