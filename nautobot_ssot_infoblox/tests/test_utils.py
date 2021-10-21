"""Util tests that do not require Django."""
import unittest

from nautobot_ssot_infoblox.utils import get_vlan_view_name, nautobot_vlan_status


class TestUtils(unittest.TestCase):
    """Test Utils."""

    def test_vlan_view_name(self):  # pylint: disable=no-self-use
        """Test vlan_view_name util."""
        name = get_vlan_view_name(
            "vlan/ZG5zLnZsYW4kLmNvbS5pbmZvYmxveC5kbnMudmxhbl92aWV3JFZMVmlldzEuMTAuMjAuMTA:VLView1/VL10/10"
        )
        self.assertEqual(name, "VLView1")

    def nautobot_vlan_status(self):  # pylint: disable=no-self-use
        """Test nautobot_vlan_status."""
        status = nautobot_vlan_status("Active")
        self.assertEqual(status, "ASSIGNED")
