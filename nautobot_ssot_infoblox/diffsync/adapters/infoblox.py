"""Infoblox Adapter for Infoblox integration with SSoT plugin."""
from diffsync import DiffSync
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
