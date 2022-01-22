"""Nautobot Adapter for Infoblox integration with SSoT plugin."""
from itertools import chain
from diffsync import DiffSync
from diffsync.exceptions import ObjectAlreadyExists
from nautobot.ipam.models import Aggregate, IPAddress, Prefix, VLAN, VLANGroup
from nautobot_ssot_infoblox.diffsync.models import (
    NautobotAggregate,
    NautobotNetwork,
    NautobotIPAddress,
    NautobotVlanGroup,
    NautobotVlan,
)
from nautobot_ssot_infoblox.utils import nautobot_vlan_status


class NautobotAdapter(DiffSync):
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
            )
            try:
                self.add(_prefix)
            except ObjectAlreadyExists:
                self.job.log_warning(f"Found duplicate prefix: {prefix.prefix}.")

    def load_ipaddresses(self):
        """Method to load IP Addresses from Nautobot."""
        for ipaddr in IPAddress.objects.all():
            addr = ipaddr.host
            # the last Prefix is the most specific and is assumed the one the IP address resides in
            prefix = Prefix.objects.net_contains(addr).last()
            _ip = self.ipaddress(
                address=addr,
                prefix=str(prefix),
                status=ipaddr.status.name if ipaddr.status else None,
                prefix_length=prefix.prefix_length if prefix else ipaddr.prefix_length,
                dns_name=ipaddr.dns_name,
                description=ipaddr.description,
            )
            try:
                self.add(_ip)
            except ObjectAlreadyExists:
                self.remove(_ip)
                self.job.log_warning(
                    f"Duplicate IP Address detected: {addr}, removing existing IP Address from adapter."
                )

    def load_vlangroups(self):
        """Method to load VLAN Groups from Nautobot."""
        for grp in VLANGroup.objects.all():
            _vg = self.vlangroup(
                name=grp.name,
                description=grp.description,
            )
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
            )
            self.add(_vlan)

    def load(self):
        """Method to load models with data from Nautobot."""
        self.load_prefixes()
        self.load_ipaddresses()
        # self.load_vlangroups()
        # self.load_vlans()


class NautobotAggregateAdapter(DiffSync):
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
                network=str(aggregate.prefix),
                description=aggregate.description,
            )
            self.add(_aggregate)
