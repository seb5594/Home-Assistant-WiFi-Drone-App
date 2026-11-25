ARG BUILD_FROM=ghcr.io/seb5594/home-assistant-base:3.24-2026.11.0@sha256:d116b9e5b612e6fcd997c86642d21b61953fcbe390c39c9b03443a577ed5e2a6

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

ARG SDK_COMMIT=1e19ecd54890c15217cd39ab2f2f109f57db5f87
ADD --checksum=sha256:dd344f6635e8bf606c77c8d712b732328c7c166767dcef4d8e6e74246a5fb0fb https://codeload.github.com/seb5594/wifi-drone-connect/tar.gz/${SDK_COMMIT} /tmp/sdk.tar.gz
ARG HELPER_COMMIT=95bf63088182eaad055aebd3ee933d249bf7a521
ADD --checksum=sha256:3c828e925a4680ae4f641b9be4d4b79d9e14dbd8290aa2c86fdecf9cb80a3e08 https://codeload.github.com/seb5594/Home-Assistant-WiFi-Helper-App/tar.gz/${HELPER_COMMIT} /tmp/helper.tar.gz
WORKDIR /opt/wifi-drone
RUN tar -xzf /tmp/sdk.tar.gz --strip-components=2 "wifi-drone-connect-${SDK_COMMIT}/src/wifi_drone_connect" \
    && mkdir -p /usr/share/licenses/wifi-drone-connect \
    && tar -xzf /tmp/sdk.tar.gz --strip-components=1 -C /usr/share/licenses/wifi-drone-connect "wifi-drone-connect-${SDK_COMMIT}/LICENSE" \
    && tar -xzf /tmp/helper.tar.gz --strip-components=2 "Home-Assistant-WiFi-Helper-App-${HELPER_COMMIT}/sdk/wifi_helper" \
    && mkdir -p /usr/share/licenses/ha-wifi-helper-client \
    && tar -xzf /tmp/helper.tar.gz --strip-components=2 -C /usr/share/licenses/ha-wifi-helper-client "Home-Assistant-WiFi-Helper-App-${HELPER_COMMIT}/sdk/LICENSE" \
    && rm /tmp/sdk.tar.gz /tmp/helper.tar.gz

ARG BUILD_VERSION=0.3.0
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
