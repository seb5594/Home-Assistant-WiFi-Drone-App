"""Exercise WiFi setup and teardown without hardware or host networking."""

import asyncio
import os
from pathlib import Path
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
            "DRONE", "", "4c7fee11-wifi-helper", "", IPv4Address("192.168.80.1")
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

    async def run_connected_session(self, record, recorder_factory):
        """Run one connected session; ``self.events`` records the order in which resources are released."""
        self.events = events = []
        stop = asyncio.Event()
        radio = Mock(interface="wlan1")
        radio.release.side_effect = lambda: events.append("return")
        hub = Mock(clear=AsyncMock())

        async def capture():
            stop.set()
            await asyncio.Event().wait()

        async def worker(resources, executable, *args, **kwargs):
            resources.callback(events.append, executable + " stopped")
            return Mock(returncode=None)

        hub.run = capture
        self.connection.settings = wifi.WifiSettings("DRONE", "", "4c7fee11-wifi-helper", "", IPv4Address("192.168.80.1"), record)
        with (
            patch.object(self.connection, "acquire", return_value=radio),
            patch.object(self.connection, "worker", side_effect=worker),
            patch.object(self.connection, "associated", return_value=True),
            patch.object(self.connection, "routed", return_value=True),
            patch.object(wifi, "command"),
            patch.object(wifi, "PcapRecorder", side_effect=recorder_factory) as recorder,
        ):
            await self.connection.run_once(hub, stop)
        return events, recorder

    async def test_traffic_recording_is_off_unless_requested(self):
        _, recorder = await self.run_connected_session(False, lambda *a, **k: Mock())
        recorder.assert_not_called()
        self.assertIsNone(self.connection.capture_name)

    async def test_recording_starts_with_the_link_and_stops_before_the_radio_returns(self):
        def factory(interface, label):
            handle = Mock(path=Path("/share/wifi-helper-private/captures/drone-20261126-101500.pcap"))
            handle.start.return_value = handle
            handle.stop.side_effect = lambda: self.events.append("recorder stopped")
            return handle

        events, recorder = await self.run_connected_session(True, factory)
        recorder.assert_called_once_with("wlan1", "drone")
        self.assertEqual(self.connection.capture_name, "drone-20261126-101500.pcap")
        # The recorder opened first, so it closes after the workers but before the radio goes back.
        self.assertEqual(events[-2:], ["recorder stopped", "return"])

    async def test_recording_failure_never_stops_the_camera(self):
        events, _ = await self.run_connected_session(True, PermissionError("NET_RAW missing"))
        self.assertEqual(events[-1], "return")
        self.assertIsNone(self.connection.capture_name)

    async def test_helper_problems_become_readable_states(self):
        for error, state in ((wifi.HelperUnavailable("down"), "waiting_helper"), (wifi.HelperRejected("no"), "helper_rejected"),
                             (wifi.ProtocolMismatch("old"), "helper_protocol")):
            stop = asyncio.Event()
            with patch.object(self.connection, "run_once", side_effect=error), patch.object(wifi, "wait_for_stop", side_effect=lambda *_: stop.set()):
                await self.connection.run(Mock(), stop)
            self.assertEqual(self.connection.state, state)

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
