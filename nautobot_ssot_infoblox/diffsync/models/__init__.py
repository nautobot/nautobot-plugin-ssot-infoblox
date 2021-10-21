"""Initialize models for Nautobot and Infoblox."""
from .nautobot import NautobotNetwork, NautobotIPAddress, NautobotVlan
from .infoblox import InfobloxNetwork, InfobloxIPAddress, InfobloxVLAN


__all__ = [
    "NautobotNetwork",
    "NautobotIPAddress",
    "NautobotVlan",
    "InfobloxNetwork",
    "InfobloxIPAddress",
    "InfobloxVLAN",
]
