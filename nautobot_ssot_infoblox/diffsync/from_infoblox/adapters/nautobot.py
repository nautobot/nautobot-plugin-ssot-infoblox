"""Adapters for Infoblox integration with SSoT plugin."""

from diffsync import DiffSync
from nautobot_ssot_infoblox.diffsync.from_infoblox.models import ipam


class NautobotAdapter(DiffSync):
    """Nautobot adapter for DiffSync."""

    network = ipam.Network
    ipaddr = ipam.IPAddress

    top_level = ["network", "ipaddress"]

    def __init__(self, *args, job=None, sync=None, **kwargs):
        """Initialize the Infoblox DiffSync adapter.

        Args:
            job (object, optional): Nautobot job. Defaults to None.
            sync (object, optional): Nautobot DiffSync. Defaults to None.
        """
        super().__init__(*args, **kwargs)
        self.job = job
        self.sync = sync
