"""Nautobot Adapter for Infoblox integration with SSoT plugin."""

from diffsync import DiffSync
from nautobot_ssot_infoblox.diffsync.models import NautobotNetwork, NautobotIPAddress
from nautobot.ipam.models import Prefix
from nautobot_ssot_infoblox.diffsync.models.base import IPAddress


class NautobotAdapter(DiffSync):

    prefix = NautobotNetwork
    ipaddr = NautobotIPAddress

    top_level = "prefix"

    def __init__(self, *args, job=None, **kwargs):
        """Instantiate this class, but do not load data immediately from the local system."""
        super().__init__(*args, **kwargs)
        self.job = job

    def load_prefixs(self):
        for prefix in Prefix.objects.all():
            _prefix = self.prefix(network=str(prefix.prefix))
            self.add(_prefix)

    def load_ipaddresses(self):
        for ipaddress in IPAddress.objects.all():
            pass

    def load(self):
        self.load_prefixs()
