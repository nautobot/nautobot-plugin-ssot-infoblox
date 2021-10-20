"""Nautobot Models for Infoblox integration with SSoT plugin."""
from nautobot.extras.models import Status as OrmStatus
from nautobot.ipam.models import IPAddress as OrmIPAddress
from nautobot.ipam.models import Prefix as OrmPrefix
from nautobot.ipam.models import VLAN as OrmVlan
from nautobot_ssot_infoblox.diffsync.models.base import Network, IPAddress, Vlan


class NautobotNetwork(Network):
    """Nautobot implementation of the Network Model."""

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


class NautobotIPAddress(IPAddress):
    """Nautobot implementation of the IPAddress Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create IPAddress object in Nautobot."""
        _pf = OrmPrefix.objects.get(prefix=attrs["network"])
        _ip = OrmIPAddress(
            address=f"{ids['address']}/{_pf.prefix_length}",
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


class NautobotVlan(Vlan):
    """Nautobot implementation of the Vlan model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create VLAN object in Nautobot."""
        _vlan = OrmVlan(
            vid=ids["vid"],
            name=attrs["name"],
            status=OrmStatus.objects.get(name="Active")
            if not attrs.get("status")
            else OrmStatus.objects.get(name=attrs["status"]),
        )
        _vlan.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update VLAN object in Nautobot."""
        _vlan = OrmVlan.objects.get(vid=self.vid)
        if attrs.get("status"):
            _vlan.status = OrmStatus.objects.get(name=attrs["status"])
        _vlan.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete VLAN object in Nautobot."""
        self.diffsync.job.log_warning(f"VLAN {self.vid} will be deleted.")
        _vlan = OrmVlan.objects.get(vid=self.get_identifiers()["vid"])
        _vlan.delete()
        return super().delete()
