"""Exercise WiFi setup and teardown without hardware or host networking."""

import asyncio
import os
import unittest
from unittest.mock import AsyncMock, Mock, patch
from ipaddress import IPv4Address

from bridge import station_dhcp, wifi


class DHCPTests(unittest.TestCase):
    def test_dhcp_installs_only_the_camera_host_route_and_leased_address(self):
        env = {
            "DRONE_WIFI_INTERFACE": "wlan1", "interface": "wlan1",
            "DRONE_CAMERA_IP": "192.168.80.1", "ip": "192.168.80.45",
            "subnet": "255.255.255.0", "router": "192.168.80.254", "dns": "192.168.80.254",
        }
        outputs = ["[]", "[]", "", "", "", '[{"addr_info":[{"family":"inet","local":"192.168.80.45","prefixlen":32}]}]']
        with patch.dict(os.environ, env), patch.object(station_dhcp, "ip", side_effect=outputs) as ip:
            station_dhcp.configure("bound")
        calls = [call.args for call in ip.call_args_list]
        self.assertIn(("address", "replace", "192.168.80.45/32", "dev", "wlan1"), calls)
        self.assertIn(("route", "replace", "192.168.80.1/32", "dev", "wlan1",
                       "scope", "link", "src", "192.168.80.45"), calls)
        self.assertNotIn("default", str(calls))
        self.assertNotIn("192.168.80.254", str(calls))

    def test_dhcp_refuses_to_overwrite_a_route_on_the_uplink(self):
        env = {
            "DRONE_WIFI_INTERFACE": "wlan1", "interface": "wlan1",
            "DRONE_CAMERA_IP": "192.168.80.1", "ip": "192.168.80.45", "subnet": "24",
        }
        with patch.dict(os.environ, env), patch.object(
            station_dhcp, "ip", return_value='[{"dev":"eth0"}]'
        ) as ip:
            with self.assertRaisesRegex(ValueError, "different interface"):
                station_dhcp.configure("bound")
            self.assertEqual(ip.call_count, 1)

    def test_supplicant_config_keeps_password_and_ssid_out_of_command_syntax(self):
        config = wifi.supplicant_config('D"rone\n', "valid-password", "/tmp/path")
        self.assertIn("ssid=" + b'D"rone\n'.hex(), config)
        self.assertNotIn("valid-password", config)
        self.assertIn("key_mgmt=NONE", wifi.supplicant_config("Open drone", "", "/tmp/path"))


class WifiLifecycleTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.settings = wifi.WifiSettings(
            "DRONE", "", "test-secret-for-wifi-helper", "", IPv4Address("192.168.80.1")
        )
        self.connection = wifi.WifiConnection(self.settings)

    def test_selects_only_one_eligible_radio(self):
        with patch.object(wifi, "Client") as factory:
            client = factory.return_value
            client.inventory.return_value = {"adapters": [
                {"name": "wlan0", "eligible": False}, {"name": "wlan1", "eligible": True},
            ]}
            self.connection.acquire()
            client.acquire.assert_called_once_with("wlan1")
            client.inventory.return_value["adapters"].append({"name": "wlan2", "eligible": True})
            with self.assertRaises(wifi.RetryWifi):
                self.connection.acquire()

    async def test_capture_and_workers_stop_before_return(self):
        events = []
        stop = asyncio.Event()
        radio = Mock(interface="wlan1")
        radio.release.side_effect = lambda: events.append("return")
        hub = Mock(clear=AsyncMock())

        async def capture():
            try:
                stop.set()
                await asyncio.Event().wait()
            finally:
                events.append("camera stopped")

        async def worker(resources, executable, *args, **kwargs):
            resources.callback(events.append, executable + " stopped")
            return Mock(returncode=None)

        hub.run = capture
        with (
            patch.object(self.connection, "acquire", return_value=radio),
            patch.object(self.connection, "worker", side_effect=worker),
            patch.object(self.connection, "associated", return_value=True),
            patch.object(self.connection, "routed", return_value=True),
            patch.object(wifi, "command"),
        ):
            await self.connection.run_once(hub, stop)
        self.assertEqual(events, ["camera stopped", "udhcpc stopped", "wpa_supplicant stopped", "return"])

    async def test_lease_loss_requires_exit(self):
        def uncertain():
            self.connection.lost.set()
            raise RuntimeError("uncertain assignment")

        hub = Mock()
        with patch.object(self.connection, "acquire", side_effect=uncertain):
            with self.assertRaises(wifi.RadioRecoveryRequired):
                await self.connection.run(hub, asyncio.Event())
        hub.run.assert_not_called()

    async def test_failed_return_requires_exit(self):
        radio = Mock(interface="wlan1")
        radio.release.side_effect = RuntimeError("return not confirmed")
        stop = asyncio.Event()
        stop.set()
        with patch.object(self.connection, "acquire", return_value=radio):
            with self.assertRaises(wifi.RadioRecoveryRequired):
                await self.connection.run_once(Mock(clear=AsyncMock()), stop)


if __name__ == "__main__":
    unittest.main()
