"""Models for Infoblox integration with SSoT plugin."""

from typing import Optional, List
from diffsync import DiffSyncModel

from nautobot.ipam.models import IPAddress as OrmIPAddress
from nautobot.ipam.models import Prefix as OrmPrefix
from nautobot.extras.models import Status as OrmStatus


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

class IPAddress(DiffSyncModel):
    """IPAddress model for DiffSync"""

    _modelname = "ipaddress"
    _identifiers = ("address",)
    _shortname = ("address",)
    _attributes = ("status", "dns_name")

    address: str
    status: Optional[str]
    dns_name: Optional[str]


class NautobotNetwork(Network):
    """Nautobot Implementation of the Network Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Prefix object in Nautobot."""
        _prefix = OrmPrefix(
            prefix=ids["network"],
            status=OrmStatus.objects.get(name="Active"),
        )
        _prefix.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def delete(self):
        """Delete Prefix object in Nautobot."""
        self.diffsync.job.log_warning(f"Prefix {self.network} will be deleted.")
        _prefix = OrmPrefix.objects.get(prefix=self.get_identifiers()["network"])
        _prefix.delete()
        return super().delete()


class InfobloxNetwork(Network):
    """Infoblox Implementation of the Network Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Network object in Infoblox."""
        # TODO call Infoblox Network Create.
        pass


class NautobotIPAddress(IPAddress):
    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create IPAddress object in Nautobot."""
        _ip = OrmIPAddress(
            address=ids["address"],
            status=OrmStatus.objects.get(name="Active")
            if not attrs.get("status")
            else OrmStatus.objects.get(name=attrs["status"]),
        )
        _ip.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update IPAddress object in Nautobot."""
        _ipaddr = OrmIPAddress.objects.get(address=self.address)
        if attrs.get("status"):
            _ipaddr.status = OrmStatus.objects.get(name=attrs["status"])
        _ipaddr.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete IPAddress object in Nautobot."""
        self.diffsync.job.log_warning(f"IP Address {self.address} will be deleted.")
        _ipaddr = OrmPrefix.objects.get(address=self.get_identifiers()["address"])
        _ipaddr.delete()
        return super().delete()


# Not sure we will sync IPAddress to Infoblox as that would be creating a reservation.
# We would need a mac address to do that with, which would mean checking for the interface
# associated with the ip address in Nautobot. This will currently be out of scope, but neat
# to add if time.
# class InfobloxIPAdress(IPAddress):
