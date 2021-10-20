"""Base Shared Models for Infoblox integration with SSoT plugin."""
from typing import Optional
from diffsync import DiffSyncModel


class Network(DiffSyncModel):
    """Network model for DiffSync."""

    _modelname = "prefix"
    _identifiers = ("network",)
    _attributes = ("description",)

    network: str
    description: Optional[str]


class Vlan(DiffSyncModel):
    """VLAN model for DiffSync."""

    _modelname = "vlan"
    _identifiers = ("vid",)
    _attributes = ("name", "description", "status")

    vid: int
    name: str
    status: str
    description: Optional[str]


class IPAddress(DiffSyncModel):
    """IPAddress model for DiffSync."""

    _modelname = "ipaddress"
    _identifiers = ("address", "prefix")
    _shortname = ("address",)
    _attributes = ("status", "description", "dns_name")

    address: str
    prefix: str
    status: str
    description: Optional[str]
    dns_name: Optional[str]
