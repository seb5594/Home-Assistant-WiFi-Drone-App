#!/usr/bin/env bash
set -Eeuo pipefail

fixture=$(mktemp -d)
cleanup() {
    if [ -n "${bridge_pid:-}" ]; then kill "$bridge_pid" 2>/dev/null || true; fi
    if [ -n "${source_pid:-}" ]; then kill "$source_pid" 2>/dev/null || true; fi
    rm -rf "$fixture"
}
trap cleanup EXIT

ffmpeg -hide_banner -loglevel error -re -f lavfi -i testsrc2=size=160x120:rate=10 \
    -c:v mjpeg -threads 1 -f mpjpeg -listen 1 http://127.0.0.1:18080/camera &
source_pid=$!
printf '%s\n' '{"source_url":"http://127.0.0.1:18080/camera","api_token":"test-token-only-123456","copy_mjpeg":true}' > "$fixture/options.json"
OPTIONS_FILE="$fixture/options.json" /run.sh &
bridge_pid=$!

python3 - <<'PY'
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

base = "http://127.0.0.1:8099/api/v1"
headers = {"Authorization": "Bearer test-token-only-123456"}

for attempt in range(120):
    try:
        with urlopen(Request(base + "/status", headers=headers), timeout=2) as response:
            status = json.load(response)
        if status["state"] == "streaming":
            break
    except URLError:
        pass
    time.sleep(0.2)
else:
    raise AssertionError("The bridge did not connect to the test camera")

assert status["api_version"] == 1
try:
    urlopen(base + "/status", timeout=2)
except HTTPError as error:
    assert error.code == 401, error
else:
    raise AssertionError("Status must require authentication")

with urlopen(Request(base + "/snapshot.jpg", headers=headers), timeout=4) as response:
    assert response.headers.get_content_type() == "image/jpeg"
    jpeg = response.read()
    assert jpeg.startswith(b"\xff\xd8") and jpeg.endswith(b"\xff\xd9")

with urlopen(Request(base + "/stream.mjpg", headers=headers), timeout=4) as response:
    assert response.headers.get_content_type() == "multipart/x-mixed-replace"
    assert response.readline() == b"--frame\r\n"
    assert response.readline() == b"Content-Type: image/jpeg\r\n"
    length = int(response.readline().split(b":")[1])
    assert response.readline() == b"\r\n"
    jpeg = response.read(length)
    assert jpeg.startswith(b"\xff\xd8") and jpeg.endswith(b"\xff\xd9")

with urlopen("http://127.0.0.1:8098/", timeout=4) as response:
    assert b"WiFi Drone Connect" in response.read()
PY
echo 'PASS: authenticated API, HTTP MJPEG snapshot and stream, and web view'
PYTHONPATH=/opt/wifi-drone python3 /tests/test_wifi.py
echo 'PASS: WiFi Helper selection, scoped DHCP and radio recovery'
