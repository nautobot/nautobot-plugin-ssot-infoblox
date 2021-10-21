"""Nautobot Adapter for Infoblox integration with SSoT plugin."""
from diffsync import DiffSync
import re
from nautobot.ipam.models import IPAddress, Prefix, VLAN
from nautobot_ssot_infoblox.diffsync.models import NautobotNetwork, NautobotIPAddress, NautobotVlan


class NautobotAdapter(DiffSync):
    """DiffSync adapter using ORM to communicate to Nautobot."""

    prefix = NautobotNetwork
    ipaddress = NautobotIPAddress
    vlan = NautobotVlan

    top_level = ["prefix", "ipaddress", "vlan"]

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
            addr = re.sub(ipaddr.address, "")
            _pf = Prefix.objects.net_contains(addr)
            # the last Prefix is the most specific and is assumed the one the IP address resides in
            prefix = _pf[len(_pf) - 1]
            _ip = self.ipaddress(
                address=addr,
                prefix=prefix,
                status=ipaddr.status.name,
                description=ipaddr.description,
                dns_name=ipaddr.dns_name,
            )
            self.add(_ip)

    def load_vlans(self):
        """Method to load VLANs from Nautobot."""
        for vlan in VLAN.objects.all():
            _vlan = self.vlan(vid=vlan.vid, name=vlan.name, description=vlan.description)
            self.add(_vlan)

    def load(self):
        """Method to load models with data from Nautobot."""
        self.load_prefixes()
        self.load_ipaddresses()
        self.load_vlans
