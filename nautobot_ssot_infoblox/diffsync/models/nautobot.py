"""Nautobot Models for Infoblox integration with SSoT plugin."""
from django.utils.text import slugify
from nautobot.extras.models import Status as OrmStatus
from nautobot.extras.models import Tag
from nautobot.ipam.models import RIR
from nautobot.ipam.models import Aggregate as OrmAggregate
from nautobot.ipam.models import IPAddress as OrmIPAddress
from nautobot.ipam.models import Prefix as OrmPrefix
from nautobot.ipam.models import VLAN as OrmVlan
from nautobot.ipam.models import VLANGroup as OrmVlanGroup
from nautobot_ssot_infoblox.diffsync.models.base import Aggregate, Network, IPAddress, Vlan, VlanView


class NautobotNetwork(Network):
    """Nautobot implementation of the Network Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Prefix object in Nautobot."""
        try:
            status = OrmStatus.objects.get(slug=attrs.get("status", "active"))
        except OrmStatus.DoesNotExist:
            status = OrmStatus.objects.get(slug="active")

        _prefix = OrmPrefix(
            prefix=ids["network"],
            status=status,
            description=attrs.get("description", ""),
        )
        _prefix.tags.add(Tag.objects.get(slug="ssot-synced-from-infoblox"))
        _prefix.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update Prefix object in Nautobot."""
        _pf = OrmPrefix.objects.get(prefix=self.network)
        if attrs.get("description"):
            _pf.description = attrs["description"]
        _pf.validated_save()
        return super().update(attrs)

    # def delete(self):
    #     """Delete Prefix object in Nautobot."""
    #     self.diffsync.job.log_warning(f"Prefix {self.network} will be deleted.")
    #     _prefix = OrmPrefix.objects.get(prefix=self.get_identifiers()["network"])
    #     _prefix.delete()
    #     return super().delete()


class NautobotIPAddress(IPAddress):
    """Nautobot implementation of the IPAddress Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create IPAddress object in Nautobot."""
        _pf = OrmPrefix.objects.get(prefix=ids["prefix"])
        _ip = OrmIPAddress(
            address=f"{ids['address']}/{_pf.prefix_length}",
            status=OrmStatus.objects.get(name="Active")
            if not attrs.get("status")
            else OrmStatus.objects.get(name=attrs["status"]),
            description=attrs.get("description", ""),
            dns_name=attrs.get("dns_name", ""),
        )
        _ip.tags.add(Tag.objects.get(slug="ssot-synced-from-infoblox"))
        _ip.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update IPAddress object in Nautobot."""
        _ipaddr = OrmIPAddress.objects.get(address=f"{self.address}/{self.prefix_length}")
        if attrs.get("status"):
            _ipaddr.status = OrmStatus.objects.get(name=attrs["status"])
        if attrs.get("description"):
            _ipaddr.description = attrs["description"]
        if attrs.get("dns_name"):
            _ipaddr.dns_name = attrs["dns_name"]
        _ipaddr.validated_save()
        return super().update(attrs)

    # def delete(self):
    #     """Delete IPAddress object in Nautobot."""
    #     self.diffsync.job.log_warning(self, message=f"IP Address {self.address} will be deleted.")
    #     ip_ids = self.get_identifiers()
    #     _ipaddr = OrmIPAddress.objects.get(address=f"{ip_ids['address']}/{ip_ids['prefix_length']}")
    #     _ipaddr.delete()
    #     return super().delete()


class NautobotVlanGroup(VlanView):
    """Nautobot implementation of the VLANView model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create VLANGroup object in Nautobot."""
        _vg = OrmVlanGroup(
            name=ids["name"],
            slug=slugify(ids["name"]),
            description=attrs["description"],
        )
        _vg.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def delete(self):
        """Delete VLANGroup object in Nautobot."""
        self.diffsync.job.log_warning(message=f"VLAN Group {self.name} will be deleted.")
        _vg = OrmVlanGroup.objects.get(**self.get_identifiers())
        _vg.delete()
        return super().delete()


class NautobotVlan(Vlan):
    """Nautobot implementation of the Vlan model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create VLAN object in Nautobot."""
        _vlan = OrmVlan(
            vid=ids["vid"],
            name=attrs["name"],
            status=OrmStatus.objects.get(name=cls.get_vlan_status(attrs["status"])),
            group=OrmVlanGroup.objects.get(name=attrs["vlangroup"]) if attrs["vlangroup"] else None,
            description=attrs["description"],
        )
        _vlan.tags.add(Tag.objects.get(slug="ssot-synced-from-infoblox"))
        _vlan.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    @staticmethod
    def get_vlan_status(status: str) -> str:
        """Method to return VLAN Status from mapping."""
        statuses = {
            "ASSIGNED": "Active",
            "UNASSIGNED": "Deprecated",
            "RESERVED": "Reserved",
        }
        return statuses[status]

    def update(self, attrs):
        """Update VLAN object in Nautobot."""
        _vlan = OrmVlan.objects.get(vid=self.vid)
        if attrs.get("status"):
            _vlan.status = OrmStatus.objects.get(name=self.get_vlan_status(attrs["status"]))
        if attrs.get("description"):
            _vlan.description = attrs["description"]
        if attrs.get("vlangroup"):
            _vlan.group = OrmVlanGroup.objects.get(name=attrs["vlangroup"])
        _vlan.validated_save()
        return super().update(attrs)

    def delete(self):
        """Delete VLAN object in Nautobot."""
        self.diffsync.job.log_warning(message=f"VLAN {self.vid} will be deleted.")
        _vlan = OrmVlan.objects.get(vid=self.get_identifiers()["vid"])
        _vlan.delete()
        return super().delete()


class NautobotAggregate(Aggregate):
    """Nautobot implementation of the Aggregate Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Aggregate object in Nautobot."""
        rir, _ = RIR.objects.get_or_create(name="RFC1918", slug="rfc1918", is_private=True)
        _aggregate = OrmAggregate(
            prefix=ids["network"],
            rir=rir,
            description=attrs["description"] if attrs.get("description") else "",
        )
        _aggregate.tags.add(Tag.objects.get(slug="ssot-synced-from-infoblox"))
        _aggregate.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update Aggregate object in Nautobot."""
        _aggregate = OrmAggregate.objects.get(prefix=self.network)
        if attrs.get("description"):
            _aggregate.description = attrs["description"]
        _aggregate.validated_save()
        return super().update(attrs)

    # def delete(self):
    #     """Delete Aggregate object in Nautobot."""
    #     self.diffsync.job.log_warning(message=f"Aggregate {self.network} will be deleted.")
    #     _aggregate = OrmAggregate.objects.get(prefix=self.get_identifiers()["network"])
    #     _aggregate.delete()
    #     return super().delete()
