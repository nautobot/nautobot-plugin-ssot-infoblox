"""Nautobot Adapter for Infoblox integration with SSoT plugin."""
from diffsync import DiffSync
from nautobot_ssot_infoblox.diffsync.models import NautobotIPAddress, NautobotNetwork


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
