"""Jobs for Infoblox integration with SSoT plugin."""

from diffsync.exceptions import ObjectNotCreated
from django.urls import reverse
from django.templatetags.static import static
from nautobot.extras.jobs import Job, BooleanVar
from nautobot_ssot.jobs.base import DataSource, DataTarget, DataMapping
from diffsync import DiffSyncFlags
# from nautobot_ssot_infoblox.diffsync.adapters import NautobotAdapter
# from nautobot_ssot_infoblox import PluginConfig


class InfobloxDataSource(DataSource, Job):

    debug = BooleanVar(description="Enable for verbose debug logging.")

    class Meta:
        
        name = "Infoblox"
        data_source = "Infoblox"
        data_source_icon = static("nautobot_ssot_infoblox/infoblox_logo.png")
        description = "Sync infomation from Infoblox to Nautobot"

    @classmethod
    def data_mappings(cls):
        return (
            DataMapping("network", None, "Prefix", reverse("ipam:prefix_list"))
        )

    def sync_data(self):
        self.log_info(message="Connecting to Infoblox")
