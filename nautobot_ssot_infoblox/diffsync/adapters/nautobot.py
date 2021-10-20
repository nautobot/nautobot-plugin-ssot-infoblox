"""Nautobot Adapter for Infoblox integration with SSoT plugin."""
from diffsync import DiffSync
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
            _prefix = self.prefix(network=str(prefix.prefix))
            self.add(_prefix)

    def load_ipaddresses(self):
        """Method to load IP Addresses from Infoblox."""
        for ipaddress in IPAddress.objects.all():
            print(ipaddress)
            print(self.ipaddress)

    def load(self):
        """Method to load models with data from Infoblox."""
        self.load_prefixes()
