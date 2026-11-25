#!/usr/bin/env python3
"""Apply a DHCP lease and a single host route on the dedicated drone radio."""

from ipaddress import IPv4Address, IPv4Network
import json
import os
import subprocess
import sys


def ip(*args: str) -> str:
    return subprocess.check_output(("ip", "-4", *args), text=True, timeout=4)


def deconfigure(interface: str) -> None:
    ip("address", "flush", "dev", interface, "scope", "global")
    ip("route", "flush", "dev", interface)


def configure(event: str) -> None:
    interface = os.environ["DRONE_WIFI_INTERFACE"]
    if os.environ.get("interface") != interface:
        raise ValueError("Unexpected DHCP interface")
    camera = IPv4Address(os.environ["DRONE_CAMERA_IP"])
    if event == "deconfig":
        deconfigure(interface)
        return
    if event not in {"bound", "renew"}:
        return
    address = IPv4Address(os.environ["ip"])
    subnet = IPv4Network(f"{address}/{os.environ['subnet']}", strict=False)
    if camera not in subnet or camera in {address, subnet.network_address, subnet.broadcast_address}:
        deconfigure(interface)
        raise ValueError("Camera address is not reachable on the DHCP subnet")
    routes = json.loads(ip("-j", "route", "show", "exact", f"{camera}/32"))
    if any(route.get("dev") != interface for route in routes):
        raise ValueError("The camera address already has a host route on a different interface")
    routes = json.loads(ip("-j", "route", "show", "match", f"{camera}/32", "scope", "link"))
    if any(route.get("dev") != interface for route in routes):
        raise ValueError("The camera address overlaps the container's directly connected network")
    if event == "bound":
        ip("address", "flush", "dev", interface, "scope", "global")
    ip("address", "replace", f"{address}/32", "dev", interface)
    # A DHCP offer must not replace the container's default route or its DNS.
    ip("route", "replace", f"{camera}/32", "dev", interface, "scope", "link", "src", str(address))
    for info in json.loads(ip("-j", "address", "show", "dev", interface))[0]["addr_info"]:
        if info["family"] == "inet" and info["local"] != str(address):
            ip("address", "del", f"{info['local']}/{info['prefixlen']}", "dev", interface)


if __name__ == "__main__":
    configure(sys.argv[1])
