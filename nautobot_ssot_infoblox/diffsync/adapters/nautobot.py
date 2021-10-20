"""Nautobot Adapter for Infoblox integration with SSoT plugin."""
from diffsync import DiffSync
import re
from nautobot.ipam.models import Prefix
from nautobot_ssot_infoblox.diffsync.models.base import IPAddress
from nautobot_ssot_infoblox.diffsync.models import NautobotNetwork, NautobotIPAddress


class NautobotAdapter(DiffSync):
    """DiffSync adapter using ORM to communicate to Nautobot."""

    prefix = NautobotNetwork
    ipaddress = NautobotIPAddress

    top_level = ["prefix", "ipaddress"]

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
        """Method to load Prefixes from Infoblox."""
        for prefix in Prefix.objects.all():
            _prefix = self.prefix(
                network=str(prefix.prefix),
                description=prefix.description,
            )
            self.add(_prefix)

    def load_ipaddresses(self):
        """Method to load IP Addresses from Infoblox."""
        for ipaddr in IPAddress.objects.all():
            addr = re.sub(ipaddr.address, "")
            _pf = Prefix.objects.net_contains(addr)
            # the last Prefix is the most specific and is assumed the one the IP address resides in
            prefix = _pf[len(_pf) - 1]
            _ip = self.ipaddress(
                address=addr,
                prefix=prefix,
                status=ipaddr.status.name,
                
                )
            print(self.ipaddress)

    def load(self):
        """Method to load models with data from Infoblox."""
        self.load_prefixes()
