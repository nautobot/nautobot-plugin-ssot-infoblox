"""Infoblox Adapter for Infoblox integration with SSoT plugin."""
from diffsync import DiffSync
from nautobot_ssot_infoblox.diffsync.client import InfobloxApi
from nautobot_ssot_infoblox.diffsync.models import NautobotIPAddress, NautobotNetwork


class InfobloxAdapter(DiffSync):
    """DiffSync adapter using requests to communicate to Infoblox server."""

    prefix = NautobotNetwork
    ipaddress = NautobotIPAddress

    top_level = ["prefix", "ipaddress"]

    def __init__(self, *args, job=None, sync=None, **kwargs):
        """Initialize Infoblox.

        Args:
            job (object, optional): Infoblox job. Defaults to None.
            sync (object, optional): Infoblox DiffSync. Defaults to None.
        """
        super().__init__(*args, **kwargs)
        self.job = job
        self.sync = sync
        self.conn = InfobloxApi()
        self.subnets = []

    def load_prefixes(self):
        """Method to load NautobotNetwork DiffSync model."""
        for _pf in self.conn.get_all_subnets():
            self.subnets.append(_pf["network"])
            new_pf = self.prefix(
                prefix=_pf["network"],
                description=_pf["comment"] if _pf.get("comment") else "",
            )
            self.add(new_pf)

    def load_ipaddresses(self):
        """Method to load NautobotIPAddress DiffSync model."""
        for _prefix in self.subnets:
            for _ip in self.conn.get_all_ipv4address_networks(prefix=_prefix):
                new_ip = self.ipaddress(
                    address=_ip["ip_address"],
                    prefix=_ip["network"],
                    status=self.conn.get_ipaddr_status(_ip),
                    description=_ip["comment"],
                )
                self.add(new_ip)

    def load(self):
        """Method for one stop shop loading of all models."""
        self.load_prefixes()
        self.load_ipaddresses()
