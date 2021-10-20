"""Models for Infoblox integration with SSoT plugin."""

from typing import Optional, List
from diffsync import DiffSyncModel

from nautobot.ipam.models import IPAddress as OrmIPAddress
from nautobot.ipam.models import Prefix as OrmPrefix
from nautobot.extras.models import Status as OrmStatus


class Network(DiffSyncModel):
    """Infoblox Network model."""

    _modelname = "prefix"
    _identifiers = ("network",)
    _attributes = ("comment",)
    _children = {"ipaddress": "ipaddrs"}
    network: str
    comment: Optional[str]
    ipaddrs: Optional[List["IPAddress"]]

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Prefix object in Nautobot."""
        _prefix = OrmPrefix(
            prefix=ids["network"],
            description=attrs["comment"] if attrs.get("comment") else "",
            status=OrmStatus.objects.get(name="Active"),
        )
        _prefix.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update Prefix object in Nautobot."""
        _prefix = OrmPrefix.objects.get(prefix=self.network)
        if attrs.get("comment"):
            _prefix.description = attrs["comment"]
        return super().update(attrs)

    def delete(self):
        """Delete Prefix object in Nautobot."""
        self.diffsync.job.log_warning(f"Prefix {self.network} will be deleted.")
        _prefix = OrmPrefix.objects.get(prefix=self.get_identifiers()["network"])
        _prefix.delete()
        return super().delete()


class IPAddress(DiffSyncModel):
    """Infoblox IPAddress model."""

    _modelname = "ipaddress"
    _identifiers = ("address", "network")
    _shortname = ("address",)
    _attributes = ("status",)
    _children = {}

    address: str
    network: str
    status: bool

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create IPAddress object in Nautobot."""
        _ip = OrmIPAddress(
            address=ids["address"],
            status=OrmStatus.objects.get(name="Active")
            if not attrs.get("status")
            else OrmStatus.objects.get(name="Reserved"),
        )
        _ip.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update IPAddress object in Nautobot."""
        _ipaddr = OrmIPAddress.objects.get(address=self.address)
        if attrs.get("status"):
            _ipaddr.status = (
                OrmStatus.objects.get(name="Active")
                if not attrs.get("status")
                else OrmStatus.objects.get(name="Reserved"),
            )
        _ipaddr.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete IPAddress object in Nautobot."""
        self.diffsync.job.log_warning(f"IP Address {self.address} will be deleted.")
        _prefix = OrmPrefix.objects.get(address=self.get_identifiers()["address"])
        _prefix.delete()
        return super().delete()
