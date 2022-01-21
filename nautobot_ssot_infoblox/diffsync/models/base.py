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


class VlanView(DiffSyncModel):
    """VLANView model for DiffSync."""

    _modelname = "vlangroup"
    _identifiers = ("name",)
    _attributes = ("description",)

    name: str
    description: Optional[str]


class Vlan(DiffSyncModel):
    """VLAN model for DiffSync."""

    _modelname = "vlan"
    _identifiers = ("vid",)
    _attributes = ("name", "description", "status", "vlangroup")

    vid: int
    name: str
    status: str
    description: Optional[str]
    vlangroup: Optional[str]


class IPAddress(DiffSyncModel):
    """IPAddress model for DiffSync."""

    _modelname = "ipaddress"
    _identifiers = ("address", "prefix", "prefix_length")
    _shortname = ("address",)
    _attributes = ("description", "dns_name", "status")

    address: str
    dns_name: str
    prefix: str
    prefix_length: int
    status: Optional[str]
    description: Optional[str]


class Aggregate(DiffSyncModel):
    """Aggregate model for DiffSync."""

    _modelname = "aggregate"
    _identifiers = ("network",)
    _attributes = ("description",)

    network: str
    description: Optional[str]
