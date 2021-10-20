"""Initialize models for Nautobot and Infoblox."""
from .nautobot import NautobotNetwork, NautobotIPAddress
from .infoblox import InfobloxNetwork


__all__ = [
    "NautobotNetwork",
    "NautobotIPAddress",
    "InfobloxNetwork",
]
