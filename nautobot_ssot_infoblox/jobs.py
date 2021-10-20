"""Jobs for Infoblox integration with SSoT plugin."""

from diffsync.exceptions import ObjectNotCreated
from django.urls import reverse
from django.templatetags.static import static
from nautobot.extras.jobs import Job, BooleanVar
from nautobot_ssot.jobs.base import DataSource, DataTarget, DataMapping
from diffsync import DiffSyncFlags
from nautobot_ssot_infoblox.diffsync.adapters import infoblox, nautobot

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
            DataMapping("network", None, "Prefix", reverse("ipam:prefix_list")),
            DataMapping("ipaddress", None, "IP Address", reverse("ipam:ip_addresses")),
        )

    def sync_data(self):
        self.log_info(message="Connecting to Infoblox")
        infoblox_adapter = infoblox.InfobloxAdapter(job=self, sync=self.sync)
        self.log_info(message="Loading data from Infoblox...")
        infoblox_adapter.load()
        self.log_info(message="Connecting to Nautobot...")
        nb_adapter = nautobot.NautobotAdapter(job=self, sync=self.sync)
        self.log_info(message="Loading data from Nautobot...")
        nb_adapter.load()
        self.log_info(message="Performing diff of data between Infoblox and Nautobot.")
        diff = nb_adapter.diff_from(infoblox_adapter, flags=DiffSyncFlags.CONTINUE_ON_FAILURE)
        self.sync.diff = diff.dict()
        self.sync.save()
        self.log_info(message=diff.summary())
        if not self.kwargs["dry_run"]:
            self.log_info(message="Performing data synchronization from Infoblox to Nautobot.")
            try:
                nb_adapter.sync_from(infoblox_adapter, flags=DiffSyncFlags.CONTINUE_ON_FAILURE)
            except ObjectNotCreated as err:
                self.log_debug(f"Unable to create object. {err}")
            self.log_success(message="Sync complete.")


class InfobloxDataTarget(DataTarget, Job):

    debug = BooleanVar(description="Enable for verbose debug logging.")

    class Meta:

        name = "Infoblox"
        data_target = "Infoblox"
        data_target_icon = static("nautobot_ssot_infoblox/infoblox_logo.png")
        description = "Sync infomation from Nautobot to Infoblox"

    @classmethod
    def data_mappings(cls):
        return (
            DataMapping("Prefix", reverse("ipam:prefix_list"), "network", None),
            DataMapping("IP Address", reverse("ipam:ip_addresses"), "ipaddress", None),
        )

    def sync_data(self):
        self.log_info(message="Connecting to Infoblox")
        infoblox_adapter = infoblox.InfobloxAdapter(job=self, sync=self.sync)
        self.log_info(message="Loading data from Infoblox...")
        infoblox_adapter.load()
        self.log_info(message="Connecting to Nautobot...")
        nb_adapter = nautobot.NautobotAdapter(job=self, sync=self.sync)
        self.log_info(message="Loading data from Nautobot...")
        nb_adapter.load()
        self.log_info(message="Performing diff of data between Infoblox and Nautobot.")
        diff = infoblox_adapter.diff_from(nb_adapter, flags=DiffSyncFlags.CONTINUE_ON_FAILURE)
        self.sync.diff = diff.dict()
        self.sync.save()
        self.log_info(message=diff.summary())
        if not self.kwargs["dry_run"]:
            self.log_info(message="Performing data synchronization to Infoblox from Nautobot.")
            try:
                infoblox_adapter.sync_from(nb_adapter, flags=DiffSyncFlags.CONTINUE_ON_FAILURE)
            except ObjectNotCreated as err:
                self.log_debug(f"Unable to create object. {err}")
            self.log_success(message="Sync complete.")


jobs = [InfobloxDataSource, InfobloxDataTarget]
