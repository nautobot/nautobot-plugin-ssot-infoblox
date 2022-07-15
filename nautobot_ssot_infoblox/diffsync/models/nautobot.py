"""Nautobot Models for Infoblox integration with SSoT plugin."""
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot.extras.models import CustomField as OrmCF
from nautobot.extras.models import Status as OrmStatus
from nautobot.dcim.models import Site
from nautobot.ipam.choices import IPAddressRoleChoices
from nautobot.ipam.models import RIR
from nautobot.ipam.models import Aggregate as OrmAggregate
from nautobot.ipam.models import IPAddress as OrmIPAddress
from nautobot.ipam.models import Prefix as OrmPrefix
from nautobot.ipam.models import Role as OrmPrefixRole
from nautobot.ipam.models import VLAN as OrmVlan
from nautobot.ipam.models import VLANGroup as OrmVlanGroup
from nautobot.ipam.models import VRF as OrmVRF
from nautobot.tenancy.models import Tenant as OrmTenant
from nautobot_ssot_infoblox.diffsync.models.base import Aggregate, Network, IPAddress, Vlan, VlanView
from nautobot_ssot_infoblox.utils.utilities import create_tag_sync_from_infoblox


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
        if attrs.get("ext_attrs"):
            cls.process_ext_attrs(diffsync=diffsync, prefix=_prefix, extattrs=attrs["ext_attrs"])
        _prefix.tags.add(create_tag_sync_from_infoblox())
        _prefix.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update Prefix object in Nautobot."""
        _pf = OrmPrefix.objects.get(prefix=self.network)
        if "description" in attrs:
            _pf.description = attrs["description"]
        if "status" in attrs:
            _pf.status = OrmStatus.objects.get(slug=attrs["status"])
        if "ext_attrs" in attrs:
            self.process_ext_attrs(diffsync=self.diffsync, prefix=_pf, extattrs=attrs["ext_attrs"])
        _pf.validated_save()
        return super().update(attrs)

    # def delete(self):
    #     """Delete Prefix object in Nautobot."""
    #     self.diffsync.job.log_warning(f"Prefix {self.network} will be deleted.")
    #     _prefix = OrmPrefix.objects.get(prefix=self.get_identifiers()["network"])
    #     _prefix.delete()
    #     return super().delete()

    @staticmethod
    def process_ext_attrs(diffsync, prefix: OrmPrefix, extattrs: dict):
        """Process Extensibility Attributes into Custom Fields or link to found objects.

        Args:
            diffsync (object): DiffSync Job
            prefix (OrmPrefix): The prefix that's being created or updated and needs processing.
            extattrs (dict): The Extensibility Attributes to be analyzed and applied to passed `prefix`.
        """
        for attr, attr_value in extattrs.items():
            if attr.lower() in ["site", "facility"]:
                try:
                    prefix.site = Site.objects.get(name=attr_value)
                except Site.DoesNotExist as err:
                    diffsync.job.log_warning(
                        f"Unable to find Site {attr_value} for prefix {prefix.prefix} found in Extensibility Attributes '{attr}'. {err}"
                    )
            if attr.lower() == "vrf":
                try:
                    prefix.vrf = OrmVRF.objects.get(name=attr_value)
                except OrmVRF.DoesNotExist as err:
                    diffsync.job.log_warning(
                        f"Unable to find VRF {attr_value} for prefix {prefix.prefix} found in Extensibility Attributes '{attr}'. {err}"
                    )
            if "role" in attr.lower():
                try:
                    prefix.role = OrmPrefixRole.objects.get(name=attr_value)
                except OrmPrefixRole.DoesNotExist as err:
                    diffsync.job.log_warning(
                        f"Unable to find Role {attr_value} for prefix {prefix.prefix} found in Extensibility Attributes '{attr}'. {err}"
                    )
            if attr.lower() in ["tenant", "dept", "department"]:
                try:
                    prefix.tenant = OrmTenant.objects.get(name=attr_value)
                except OrmTenant.DoesNotExist as err:
                    diffsync.job.log_warning(
                        f"Unable to find Tenant {attr_value} for prefix {prefix.prefix} found in Extensibility Attributes '{attr}'. {err}"
                    )
            _cf_dict = {
                "name": slugify(attr),
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": attr,
            }
            field, _ = OrmCF.objects.get_or_create(name=_cf_dict["name"], defaults=_cf_dict)
            field.content_types.add(ContentType.objects.get_for_model(OrmPrefix).id)
            prefix.custom_field_data.update({_cf_dict["name"]: attr_value})


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
        _ip.tags.add(create_tag_sync_from_infoblox())
        if attrs.get("ext_attrs"):
            cls.process_ext_attrs(diffsync=diffsync, ipaddr=_ip, extattrs=attrs["ext_attrs"])
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
        if "ext_attrs" in attrs:
            self.process_ext_attrs(diffsync=self.diffsync, ipaddr=_ipaddr, extattrs=attrs["ext_attrs"])
        _ipaddr.validated_save()
        return super().update(attrs)

    # def delete(self):
    #     """Delete IPAddress object in Nautobot."""
    #     self.diffsync.job.log_warning(self, message=f"IP Address {self.address} will be deleted.")
    #     ip_ids = self.get_identifiers()
    #     _ipaddr = OrmIPAddress.objects.get(address=f"{ip_ids['address']}/{ip_ids['prefix_length']}")
    #     _ipaddr.delete()
    #     return super().delete()

    @staticmethod
    def process_ext_attrs(diffsync, ipaddr: OrmIPAddress, extattrs: dict):
        """Process Extensibility Attributes into Custom Fields or link to found objects.

        Args:
            diffsync (object): DiffSync Job
            ipaddr (OrmIPAddress): The IP Address that's being created or updated and needs processing.
            extattrs (dict): The Extensibility Attributes to be analyzed and applied to passed `prefix`.
        """
        for attr, attr_value in extattrs.items():
            if attr.lower() == "vrf":
                try:
                    ipaddr.vrf = OrmVRF.objects.get(name=attr_value)
                except OrmVRF.DoesNotExist as err:
                    diffsync.job.log_warning(
                        f"Unable to find VRF {attr_value} for IP Address {ipaddr.address} found in Extensibility Attributes '{attr}'. {err}"
                    )
            if "role" in attr.lower():
                if attr_value.lower() in IPAddressRoleChoices.as_dict():
                    ipaddr.role = attr_value.lower()
                else:
                    diffsync.job.log_warning(
                        f"Unable to find Role {attr_value} for IP Address {ipaddr.address} found in Extensibility Attributes '{attr}'."
                    )
            if attr.lower() in ["tenant", "dept", "department"]:
                try:
                    ipaddr.tenant = OrmTenant.objects.get(name=attr_value)
                except OrmTenant.DoesNotExist as err:
                    diffsync.job.log_warning(
                        f"Unable to find Tenant {attr_value} for IP Address {ipaddr.address} found in Extensibility Attributes '{attr}'. {err}"
                    )
            _cf_dict = {
                "name": slugify(attr),
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": attr,
            }
            field, _ = OrmCF.objects.get_or_create(name=_cf_dict["name"], defaults=_cf_dict)
            field.content_types.add(ContentType.objects.get_for_model(OrmIPAddress).id)
            ipaddr.custom_field_data.update({_cf_dict["name"]: attr_value})


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
        if attrs.get("ext_attrs"):
            cls.process_ext_attrs(diffsync=diffsync, vlan_group=_vg, extattrs=attrs["ext_attrs"])
        _vg.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update VLANGroup object in Nautobot."""
        _vg = OrmVlanGroup.objects.get(id=self.pk)
        if "ext_attrs" in attrs:
            self.process_ext_attrs(diffsync=self.diffsync, vlan_group=_vg, extattrs=attrs["ext_attrs"])
        return super().update(attrs)

    def delete(self):
        """Delete VLANGroup object in Nautobot."""
        self.diffsync.job.log_warning(message=f"VLAN Group {self.name} will be deleted.")
        _vg = OrmVlanGroup.objects.get(**self.get_identifiers())
        _vg.delete()
        return super().delete()

    @staticmethod
    def process_ext_attrs(diffsync, vlan_group: OrmVlanGroup, extattrs: dict):
        """Process Extensibility Attributes into Custom Fields or link to found objects.

        Args:
            diffsync (object): DiffSync Job
            vlan_group (OrmVlanGroup): The VLAN Group that's being created or updated and needs processing.
            extattrs (dict): The Extensibility Attributes to be analyzed and applied to passed `prefix`.
        """
        for attr, attr_value in extattrs.items():
            if attr.lower() in ["site", "facility"]:
                try:
                    vlan_group.site = Site.objects.get(name=attr_value)
                except Site.DoesNotExist as err:
                    diffsync.job.log_warning(
                        f"Unable to find Site {attr_value} for VLAN Group {vlan_group.name} found in Extensibility Attributes '{attr}'. {err}"
                    )
            _cf_dict = {
                "name": slugify(attr),
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": attr,
            }
            field, _ = OrmCF.objects.get_or_create(name=_cf_dict["name"], defaults=_cf_dict)
            field.content_types.add(ContentType.objects.get_for_model(OrmVlanGroup).id)
            vlan_group.custom_field_data.update({_cf_dict["name"]: attr_value})


class NautobotVlan(Vlan):
    """Nautobot implementation of the Vlan model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create VLAN object in Nautobot."""
        _vlan = OrmVlan(
            vid=ids["vid"],
            name=ids["name"],
            status=OrmStatus.objects.get(name=cls.get_vlan_status(attrs["status"])),
            group=OrmVlanGroup.objects.get(name=ids["vlangroup"]) if ids["vlangroup"] else None,
            description=attrs["description"],
        )
        if "ext_attrs" in attrs:
            cls.process_ext_attrs(diffsync=diffsync, vlan=_vlan, extattrs=attrs["ext_attrs"])
        _vlan.tags.add("SSoT Synced to Infoblox")
        # ensure that the VLAN Group and VLAN have the same Site
        if not _vlan.site and _vlan.group.site:
            _vlan.site = _vlan.group.site
        if not _vlan.group.site and _vlan.site:
            _vlan.group.site = _vlan.site
            _vlan.group.validated_save()
        try:
            _vlan.validated_save()
        except ValidationError as err:
            diffsync.job.log_warning(f"Unable to create VLAN {ids['name']} {ids['vid']}. {err}")
            return False
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    @staticmethod
    def get_vlan_status(status: str) -> str:
        """Return VLAN Status from mapping."""
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
        if "ext_attrs" in attrs:
            self.process_ext_attrs(diffsync=self.diffsync, vlan=_vlan, extattrs=attrs["ext_attrs"])
        if not _vlan.group.site and _vlan.site:
            _vlan.group.site = _vlan.site
            _vlan.group.validated_save()
        try:
            _vlan.validated_save()
        except ValidationError as err:
            self.diffsync.job.log_warning(f"Unable to update VLAN {_vlan.name} {_vlan.vid}. {err}")
            return False
        return super().update(attrs)

    def delete(self):
        """Delete VLAN object in Nautobot."""
        self.diffsync.job.log_warning(message=f"VLAN {self.vid} will be deleted.")
        _vlan = OrmVlan.objects.get(vid=self.get_identifiers()["vid"])
        _vlan.delete()
        return super().delete()

    @staticmethod
    def process_ext_attrs(diffsync, vlan: OrmVlan, extattrs: dict):
        """Process Extensibility Attributes into Custom Fields or link to found objects.

        Args:
            diffsync (object): DiffSync Job
            vlan (OrmVlan): The VLAN that's being created or updated and needs processing.
            extattrs (dict): The Extensibility Attributes to be analyzed and applied to passed `prefix`.
        """
        for attr, attr_value in extattrs.items():
            if attr.lower() in ["site", "facility"]:
                try:
                    vlan.site = Site.objects.get(name=attr_value)
                except Site.DoesNotExist as err:
                    diffsync.job.log_warning(
                        f"Unable to find Site {attr_value} for VLAN {vlan.vid} {vlan.name} found in Extensibility Attributes '{attr}'. {err}"
                    )
            if attr.lower() in ["tenant", "dept", "department"]:
                try:
                    vlan.tenant = OrmTenant.objects.get(name=attr_value)
                except OrmTenant.DoesNotExist as err:
                    diffsync.job.log_warning(
                        f"Unable to find Tenant {attr_value} for VLAN {vlan.vid} {vlan.name} found in Extensibility Attributes '{attr}'. {err}"
                    )
            if attr.lower() == "role":
                try:
                    vlan.role = OrmPrefixRole.objects.get(name=attr_value)
                except OrmPrefixRole.DoesNotExist as err:
                    diffsync.job.log_warning(
                        f"Unable to find Role {attr_value} for VLAN {vlan.vid} {vlan.name} found in Extensibility Attributes '{attr}'. {err}"
                    )
            _cf_dict = {
                "name": slugify(attr),
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": attr,
            }
            field, _ = OrmCF.objects.get_or_create(name=_cf_dict["name"], defaults=_cf_dict)
            field.content_types.add(ContentType.objects.get_for_model(OrmVlan).id)
            vlan.custom_field_data.update({_cf_dict["name"]: attr_value})


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
        if "ext_attrs" in attrs["ext_attrs"]:
            cls.process_ext_attrs(diffsync=diffsync, aggregate=_aggregate, extattrs=attrs["ext_attrs"])
        _aggregate.tags.add("SSoT Synced to Infoblox")
        _aggregate.validated_save()
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)

    def update(self, attrs):
        """Update Aggregate object in Nautobot."""
        _aggregate = OrmAggregate.objects.get(prefix=self.network)
        if attrs.get("description"):
            _aggregate.description = attrs["description"]
        if "ext_attrs" in attrs["ext_attrs"]:
            self.process_ext_attrs(diffsync=self.diffsync, aggregate=_aggregate, extattrs=attrs["ext_attrs"])
        _aggregate.validated_save()
        return super().update(attrs)

    # def delete(self):
    #     """Delete Aggregate object in Nautobot."""
    #     self.diffsync.job.log_warning(message=f"Aggregate {self.network} will be deleted.")
    #     _aggregate = OrmAggregate.objects.get(prefix=self.get_identifiers()["network"])
    #     _aggregate.delete()
    #     return super().delete()

    @staticmethod
    def process_ext_attrs(diffsync, aggregate: OrmAggregate, extattrs: dict):
        """Process Extensibility Attributes into Custom Fields or link to found objects.

        Args:
            diffsync (object): DiffSync Job
            aggregate (OrmAggregate): The Aggregate that's being created or updated and needs processing.
            extattrs (dict): The Extensibility Attributes to be analyzed and applied to passed `prefix`.
        """
        for attr, attr_value in extattrs.items():
            if attr.lower() in ["tenant", "dept", "department"]:
                try:
                    aggregate.tenant = OrmTenant.objects.get(name=attr_value)
                except OrmTenant.DoesNotExist as err:
                    diffsync.job.log_warning(
                        f"Unable to find Tenant {attr_value} for Aggregate {aggregate.network} found in Extensibility Attributes '{attr}'. {err}"
                    )
            _cf_dict = {
                "name": slugify(attr),
                "type": CustomFieldTypeChoices.TYPE_TEXT,
                "label": attr,
            }
            field, _ = OrmCF.objects.get_or_create(name=_cf_dict["name"], defaults=_cf_dict)
            field.content_types.add(ContentType.objects.get_for_model(OrmAggregate).id)
            aggregate.custom_field_data.update({_cf_dict["name"]: attr_value})
