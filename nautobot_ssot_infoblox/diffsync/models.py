"""Models for Infoblox integration with SSoT plugin."""

from typing import Optional, List
from diffsync import DiffSyncModel

from nautobot.ipam.models import Prefix as OrmPrefix
from nautobot.extras.models import Status as OrmStatus


class Prefix(DiffSyncModel):

    _modelname = "prefix"
    _identifiers = ("prefix")
    _shortname = ("network")


class IPAddress(DiffSyncModel):

    _modelname = "ipaddress"
    _identifiers = ("address",)
    _shortname = ("address",)
    _attributes = ("status", "dns_name")

    address: str
    status: Optional[str]
    dns_name: Optional[str]


class NautobotPrefix(Prefix):

    @classmethod
    def create(cls, diffsync, ids, attrs):
        _prefix = OrmPrefix(
            prefix = ids['prefix'],
            status = OrmStatus.objects.get(name="Active"),
        )
        _prefix.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def delete(self):
        self.diffsync.job.log_warning(f"Subnet {self.name} will be deleted.")
        _prefix = OrmPrefix.objects.get(**self.get_identifiers())
        _prefix.delete()
        return super().delete()