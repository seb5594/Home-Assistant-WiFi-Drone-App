ARG BUILD_FROM=ghcr.io/seb5594/home-assistant-base:3.24-2026.11.0

FROM ${BUILD_FROM}

# renovate: datasource=repology depName=alpine_3_24/python3
ARG PYTHON_VERSION=3.14.10-r2
# renovate: datasource=repology depName=alpine_3_24/py3-aiohttp
ARG AIOHTTP_VERSION=3.13.5-r0
# renovate: datasource=repology depName=alpine_3_24/ffmpeg
ARG FFMPEG_VERSION=8.1.3-r0
# renovate: datasource=repology depName=alpine_3_24/iproute2
ARG IPROUTE2_VERSION=7.0.0-r0
# renovate: datasource=repology depName=alpine_3_24/iw
ARG IW_VERSION=6.17-r0
# renovate: datasource=repology depName=alpine_3_24/wpa_supplicant
ARG WPA_SUPPLICANT_VERSION=2.11-r4
RUN apk add --no-cache python3="${PYTHON_VERSION}" py3-aiohttp="${AIOHTTP_VERSION}" ffmpeg="${FFMPEG_VERSION}" \
    iproute2="${IPROUTE2_VERSION}" iw="${IW_VERSION}" wpa_supplicant="${WPA_SUPPLICANT_VERSION}"

ARG SDK_COMMIT=c24f6b404821747e1a6b1d790718c5730c174e64
ADD --checksum=sha256:6085ae929acc869211575a1c67df9bc9384bc5f0672fa7d5d49c122829e6ddf1 https://codeload.github.com/seb5594/wifi-drone-connect/tar.gz/${SDK_COMMIT} /tmp/sdk.tar.gz
ARG HELPER_COMMIT=e440f92c4d75f6d5e51d45623a7155b197f16be6
ADD --checksum=sha256:338a4c74041d8e27e2274475fa3650b376db30a92fa24db0a8b12e7c03d5f0ba https://codeload.github.com/seb5594/Home-Assistant-WiFi-Helper-App/tar.gz/${HELPER_COMMIT} /tmp/helper.tar.gz
WORKDIR /opt/wifi-drone
RUN tar -xzf /tmp/sdk.tar.gz --strip-components=2 "wifi-drone-connect-${SDK_COMMIT}/src/wifi_drone_connect" \
    && mkdir -p /usr/share/licenses/wifi-drone-connect \
    && tar -xzf /tmp/sdk.tar.gz --strip-components=1 -C /usr/share/licenses/wifi-drone-connect "wifi-drone-connect-${SDK_COMMIT}/LICENSE" \
    && tar -xzf /tmp/helper.tar.gz --strip-components=2 "Home-Assistant-WiFi-Helper-App-${HELPER_COMMIT}/sdk/wifi_helper" \
    && mkdir -p /usr/share/licenses/ha-wifi-helper-client \
    && tar -xzf /tmp/helper.tar.gz --strip-components=2 -C /usr/share/licenses/ha-wifi-helper-client "Home-Assistant-WiFi-Helper-App-${HELPER_COMMIT}/sdk/LICENSE" \
    && rm /tmp/sdk.tar.gz /tmp/helper.tar.gz

ARG BUILD_VERSION=2026.11.26.1
ARG BUILD_ARCH=amd64
LABEL io.hass.version="${BUILD_VERSION}" \
    io.hass.type="addon" \
    io.hass.arch="${BUILD_ARCH}" \
    org.opencontainers.image.source="https://github.com/seb5594/Home-Assistant-WiFi-Drone-App"

COPY bridge/ ./bridge/
COPY run.sh entrypoint.sh /
RUN chmod a+x /run.sh /entrypoint.sh ./bridge/station_dhcp.py

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
CMD ["/run.sh"]
