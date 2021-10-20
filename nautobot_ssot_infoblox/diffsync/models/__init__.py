"""Initialize models for Nautobot and Infoblox."""
from nautobot_ssot_infoblox.diffsync.models.base import Network, IPAddress
from nautobot_ssot_infoblox.diffsync.models.nautobot import NautobotNetwork, NautobotIPAddress
from nautobot_ssot_infoblox.diffsync.models.infoblox import InfobloxNetwork


__all__ = [
    "Network",
    "IPAddress",
    "NautobotNetwork",
    "NautobotIPAddress",
    "InfobloxNetwork",
]
