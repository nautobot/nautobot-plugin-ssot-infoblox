"""Initialize models for Nautobot and Infoblox."""
from .base import Network, IPAddress
from .nautobot import NautobotNetwork, NautobotIPAddress
from .infoblox import InfobloxNetwork


__all__ = [
    "Network",
    "IPAddress",
    "NautobotNetwork",
    "NautobotIPAddress",
    "InfobloxNetwork",
]
