"""Base Shared Models for Infoblox integration with SSoT plugin."""

from typing import Optional, List
from diffsync import DiffSyncModel

<<<<<<< HEAD
from nautobot.ipam.models import IPAddress as OrmIPAddress
from nautobot.ipam.models import Prefix as OrmPrefix
from nautobot.ipam.models import VLAN as OrmVlan
from nautobot.extras.models import Status as OrmStatus

=======
>>>>>>> main


class Network(DiffSyncModel):
    """Network model for DiffSync"""

    _modelname = "prefix"
    _identifiers = ("network",)

    network: str

class Vlan(DiffSyncModel):
    """VLAN model for DiffSync."""

    _modelname = "vlan"
    _identifiers = ("vid", )
    _attributes = ("name", "description")

    vid: int
    name: str
    description: Optional[str]
    status: Optional[str]
    

class IPAddress(DiffSyncModel):
    """IPAddress model for DiffSync"""

    _modelname = "ipaddress"
    _identifiers = ("address", "prefix")
    _shortname = ("address",)
    _attributes = ("status", "dns_name")

    address: str
    prefix: str
    status: Optional[str]
    dns_name: Optional[str]
