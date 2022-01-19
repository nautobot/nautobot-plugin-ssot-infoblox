"""Nautobot Adapter for Infoblox integration with SSoT plugin."""
from diffsync import DiffSync
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
        for prefix in Prefix.objects.all():
            _prefix = self.prefix(
                network=str(prefix.prefix),
                description=prefix.description,
            )
            self.add(_prefix)

    def load_ipaddresses(self):
        """Method to load IP Addresses from Nautobot."""
        for ipaddr in IPAddress.objects.all():
            addr = ipaddr.host
            # _pf = Prefix.objects.net_contains(addr)
            prefix = Prefix.objects.net_contains(addr).last()
            # the last Prefix is the most specific and is assumed the one the IP address resides in
            # prefix = _pf[len(_pf) - 1]
            _ip = self.ipaddress(
                address=addr,
                prefix=str(prefix),
                status=ipaddr.status.name,
                prefix_length=ipaddr.prefix_length,
                dns_name=ipaddr.dns_name,
                description=ipaddr.description,
            )
            self.add(_ip)

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
        self.load_vlangroups()
        self.load_vlans()


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
