"""Jobs for Infoblox integration with SSoT plugin."""

from django.templatetags.static import static
from django.urls import reverse
from nautobot.extras.jobs import BooleanVar, Job
from nautobot_ssot.jobs.base import DataMapping, DataSource, DataTarget

from diffsync import DiffSyncFlags
from diffsync.exceptions import ObjectNotCreated
from nautobot_ssot_infoblox.diffsync.adapters import infoblox, nautobot


class InfobloxDataSource(DataSource, Job):
    """Infoblox SSoT Data Source."""

    debug = BooleanVar(description="Enable for verbose debug logging.")

    class Meta:  # pylint: disable=too-few-public-methods
        """Information about the Job."""

        name = "Infoblox"
        data_source = "Infoblox"
        data_source_icon = static("nautobot_ssot_infoblox/infoblox_logo.png")
        description = "Sync infomation from Infoblox to Nautobot"

    @classmethod
    def data_mappings(cls):
        """Shows mapping of models between Infoblox and Nautobot."""
        return (
            DataMapping("network", None, "Prefix", reverse("ipam:prefix_list")),
            DataMapping("ipaddress", None, "IP Address", reverse("ipam:ip_addresses")),
        )

    def sync_data(self):
        """Method to handle synchronization of data to Nautobot."""
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
    """Infoblox SSoT Data Target."""

    debug = BooleanVar(description="Enable for verbose debug logging.")

    class Meta:  # pylint: disable=too-few-public-methods
        """Information about the Job."""

        name = "Infoblox"
        data_target = "Infoblox"
        data_target_icon = static("nautobot_ssot_infoblox/infoblox_logo.png")
        description = "Sync infomation from Nautobot to Infoblox"

    @classmethod
    def data_mappings(cls):
        """Shows mapping of models between Nautobot and Infoblox."""
        return (
            DataMapping("Prefix", reverse("ipam:prefix_list"), "network", None),
            DataMapping("IP Address", reverse("ipam:ip_addresses"), "ipaddress", None),
        )

    def sync_data(self):
        """Method to handle synchronization of data to Infoblox."""
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
