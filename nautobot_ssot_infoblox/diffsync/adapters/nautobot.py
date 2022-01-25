"""Nautobot Adapter for Infoblox integration with SSoT plugin."""
import datetime
from itertools import chain
from diffsync import DiffSync
from diffsync.exceptions import ObjectAlreadyExists, ObjectNotFound
from django.contrib.contenttypes.models import ContentType
from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot.extras.models import Tag, CustomField
from nautobot.ipam.models import Aggregate, IPAddress, Prefix, VLAN, VLANGroup
from nautobot_ssot_infoblox.diffsync.models import (
    NautobotAggregate,
    NautobotNetwork,
    NautobotIPAddress,
    NautobotVlanGroup,
    NautobotVlan,
)
from nautobot_ssot_infoblox.constant import TAG_COLOR
from nautobot_ssot_infoblox.utils import nautobot_vlan_status


class NautobotMixin:
    """Add specific objects onto Nautobot objects to provide information on sync status with Infoblox."""

    def tag_involved_objects(self, target):
        """Tag all objects that were successfully synced to the target."""
        # The ssot-synced-to-infoblox tag *should* have been created automatically during plugin installation
        # (see nautobot_ssot_infoblox/signals.py) but maybe a user deleted it inadvertently, so be safe:
        tag, _ = Tag.objects.get_or_create(
            slug="ssot-synced-to-infoblox",
            defaults={
                "name": "SSoT Synced to Infoblox",
                "description": "Object synced at some point to Infoblox",
                "color": TAG_COLOR,
            },
        )
        # Ensure that the "ssot-synced-to-infoblox" custom field is present; as above, it *should* already exist.
        custom_field, _ = CustomField.objects.get_or_create(
            type=CustomFieldTypeChoices.TYPE_DATE,
            name="ssot-synced-to-infoblox",
            defaults={
                "label": "Last synced to Infoblox on",
            },
        )
        for model in [Aggregate, IPAddress, Prefix]:
            custom_field.content_types.add(ContentType.objects.get_for_model(model))

        for modelname in ["ipaddress", "prefix"]:
            for local_instance in self.get_all(modelname):
                unique_id = local_instance.get_unique_id()
                # Verify that the object now has a counterpart in the target DiffSync
                try:
                    target.get(modelname, unique_id)
                except ObjectNotFound:
                    continue

                self.tag_object(modelname, unique_id, tag, custom_field)

    def tag_object(self, modelname, unique_id, tag, custom_field):
        """Apply the given tag and custom field to the identified object."""
        model_instance = self.get(modelname, unique_id)
        today = datetime.date.today().isoformat()

        def _tag_object(nautobot_object):
            """Apply custom field and tag to object, if applicable."""
            if hasattr(nautobot_object, "tags"):
                nautobot_object.tags.add(tag)
            if hasattr(nautobot_object, "cf"):
                nautobot_object.cf[custom_field.name] = today
            nautobot_object.validated_save()

        if modelname == "aggregate":
            _tag_object(Aggregate.objects.get(pk=model_instance.pk))
        elif modelname == "ipaddress":
            _tag_object(IPAddress.objects.get(pk=model_instance.pk))
        elif modelname == "prefix":
            _tag_object(Prefix.objects.get(pk=model_instance.pk))


class NautobotAdapter(NautobotMixin, DiffSync):
    """DiffSync adapter using ORM to communicate to Nautobot."""

    prefix = NautobotNetwork
    ipaddress = NautobotIPAddress
    vlangroup = NautobotVlanGroup
    vlan = NautobotVlan

    top_level = ["prefix", "ipaddress", "vlangroup", "vlan"]

    def __init__(self, *args, job=None, sync=None, **kwargs):
        """Initialize Nautobot.

        Args:
            job (object, optional): Nautobot job. Defaults to None.
            sync (object, optional): Nautobot DiffSync. Defaults to None.
        """
        super().__init__(*args, **kwargs)
        self.job = job
        self.sync = sync

    def load_prefixes(self):
        """Method to load Prefixes from Nautobot."""
        all_prefixes = list(chain(Prefix.objects.all(), Aggregate.objects.all()))
        for prefix in all_prefixes:
            _prefix = self.prefix(
                network=str(prefix.prefix),
                description=prefix.description,
                status=prefix.status.slug if hasattr(prefix, "status") else "container",
                pk=prefix.id,
            )
            try:
                self.add(_prefix)
            except ObjectAlreadyExists:
                self.job.log_warning(_prefix, message=f"Found duplicate prefix: {prefix.prefix}.")

    def load_ipaddresses(self):
        """Method to load IP Addresses from Nautobot."""
        for ipaddr in IPAddress.objects.all():
            addr = ipaddr.host
            # the last Prefix is the most specific and is assumed the one the IP address resides in
            prefix = Prefix.objects.net_contains(addr).last()

            # The IP address must have a parent prefix
            if not prefix:
                self.job.log_warning(f"IP Address {addr} does not have a parent prefix and will not be synced.")
                continue
            # IP address must be part of a prefix that is not a container
            # This means the IP cannot be associated with an IPv4 Network within Infoblox
            if prefix.status.slug == "container":
                self.job.log_warning(
                    f"IP Address {addr}'s arent prefix is a container. The parent prefix must not be a container."
                )
                continue

            if ipaddr.dns_name:
                _ip = self.ipaddress(
                    address=addr,
                    prefix=str(prefix),
                    status=ipaddr.status.name if ipaddr.status else None,
                    prefix_length=prefix.prefix_length if prefix else ipaddr.prefix_length,
                    dns_name=ipaddr.dns_name,
                    description=ipaddr.description,
                    pk=ipaddr.id,
                )
                try:
                    self.add(_ip)
                except ObjectAlreadyExists:
                    self.job.log_warning(f"Duplicate IP Address detected: {addr}.")

    def load_vlangroups(self):
        """Method to load VLAN Groups from Nautobot."""
        for grp in VLANGroup.objects.all():
            _vg = self.vlangroup(name=grp.name, description=grp.description, pk=grp.id)
            self.add(_vg)

    def load_vlans(self):
        """Method to load VLANs from Nautobot."""
        for vlan in VLAN.objects.all():
            _vlan = self.vlan(
                vid=vlan.vid,
                name=vlan.name,
                description=vlan.description,
                vlangroup=vlan.group.name if vlan.group else "",
                status=nautobot_vlan_status(vlan.status.name),
                pk=vlan.id,
            )
            self.add(_vlan)

    def load(self):
        """Method to load models with data from Nautobot."""
        self.load_prefixes()
        self.load_ipaddresses()
        # self.load_vlangroups()
        # self.load_vlans()


class NautobotAggregateAdapter(NautobotMixin, DiffSync):
    """DiffSync adapter using ORM to communicate to Nautobot Aggregrates."""

    aggregate = NautobotAggregate

    top_level = ["aggregate"]

    def __init__(self, *args, job=None, sync=None, **kwargs):
        """Initialize Nautobot.

        Args:
            job (object, optional): Nautobot job. Defaults to None.
            sync (object, optional): Nautobot DiffSync. Defaults to None.
        """
        super().__init__(*args, **kwargs)
        self.job = job
        self.sync = sync

    def load(self):
        """Method to load aggregate models from Nautobot."""
        for aggregate in Aggregate.objects.all():
            _aggregate = self.aggregate(
                network=str(aggregate.prefix), description=aggregate.description, pk=aggregate.id
            )
            self.add(_aggregate)
