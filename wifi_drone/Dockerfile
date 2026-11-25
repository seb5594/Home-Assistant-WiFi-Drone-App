ARG BUILD_FROM=ghcr.io/seb5594/home-assistant-base:3.24-2026.11.0@sha256:d116b9e5b612e6fcd997c86642d21b61953fcbe390c39c9b03443a577ed5e2a6

FROM ${BUILD_FROM}

# renovate: datasource=repology depName=alpine_3_24/python3
ARG PYTHON_VERSION=3.14.10-r2
# renovate: datasource=repology depName=alpine_3_24/py3-aiohttp
ARG AIOHTTP_VERSION=3.13.5-r0
# renovate: datasource=repology depName=alpine_3_24/ffmpeg
ARG FFMPEG_VERSION=8.1.3-r0
RUN apk add --no-cache python3="${PYTHON_VERSION}" py3-aiohttp="${AIOHTTP_VERSION}" ffmpeg="${FFMPEG_VERSION}"

ARG SDK_COMMIT=0864a988362d4e204f285f908c3b0a31c6c51375
ADD --checksum=sha256:85aa307d7f1eb611e26c96dccebd189754f0a6cb3d23bf52baf6c04178ad1960 https://codeload.github.com/seb5594/wifi-drone-connect/tar.gz/${SDK_COMMIT} /tmp/sdk.tar.gz
WORKDIR /opt/wifi-drone
RUN tar -xzf /tmp/sdk.tar.gz --strip-components=2 "wifi-drone-connect-${SDK_COMMIT}/src/wifi_drone_connect" \
    && mkdir -p /usr/share/licenses/wifi-drone-connect \
    && tar -xzf /tmp/sdk.tar.gz --strip-components=1 -C /usr/share/licenses/wifi-drone-connect "wifi-drone-connect-${SDK_COMMIT}/LICENSE" \
    && rm /tmp/sdk.tar.gz

ARG BUILD_VERSION=0.1.0
ARG BUILD_ARCH=amd64
LABEL io.hass.version="${BUILD_VERSION}" \
    io.hass.type="addon" \
    io.hass.arch="${BUILD_ARCH}" \
    org.opencontainers.image.source="https://github.com/seb5594/Home-Assistant-WiFi-Drone-App"

COPY bridge/ ./bridge/
COPY run.sh entrypoint.sh /
RUN chmod a+x /run.sh /entrypoint.sh

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
CMD ["/run.sh"]
