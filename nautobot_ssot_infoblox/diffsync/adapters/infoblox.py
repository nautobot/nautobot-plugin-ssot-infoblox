"""Infoblox Adapter for Infoblox integration with SSoT plugin."""
import ipaddress
import re

from diffsync import DiffSync
from diffsync.enum import DiffSyncFlags
from nautobot.extras.plugins.exceptions import PluginImproperlyConfigured
from nautobot_ssot_infoblox.utils.client import InfobloxApi
from nautobot_ssot_infoblox.utils.diffsync import get_ext_attr_dict, build_vlan_map
from nautobot_ssot_infoblox.diffsync.models.infoblox import (
    InfobloxAggregate,
    InfobloxIPAddress,
    InfobloxNetwork,
    InfobloxVLANView,
    InfobloxVLAN,
)


class InfobloxAdapter(DiffSync):
    """DiffSync adapter using requests to communicate to Infoblox server."""

    prefix = InfobloxNetwork
    ipaddress = InfobloxIPAddress
    vlangroup = InfobloxVLANView
    vlan = InfobloxVLAN

    top_level = ["vlangroup", "vlan", "prefix", "ipaddress"]

    def __init__(self, *args, job=None, sync=None, conn=None, **kwargs):
        """Initialize Infoblox.

        Args:
            job (object, optional): Infoblox job. Defaults to None.
            sync (object, optional): Infoblox DiffSync. Defaults to None.
            conn (object, optional): InfobloxAPI connection. Defaults to None.
        """
        super().__init__(*args, **kwargs)
        self.job = job
        self.sync = sync
        self.conn = conn
        self.subnets = []

        if self.conn in [None, False]:
            self.job.log_failure(
                message="Improperly configured settings for communicating to Infoblox. Please validate accuracy."
            )
            raise PluginImproperlyConfigured

    def load_prefixes(self):
        """Load InfobloxNetwork DiffSync model."""
        # Need to load containers here to prevent duplicates when syncing back to Infoblox
        containers = self.conn.get_network_containers()
        subnets = self.conn.get_all_subnets()
        self.subnets = [(x["network"], x["network_view"]) for x in subnets]
        all_networks = containers + subnets
        for _pf in all_networks:
            new_pf = self.prefix(
                network=_pf["network"],
                description=_pf.get("comment", ""),
                status=_pf.get("status", "active"),
                ext_attrs=get_ext_attr_dict(extattrs=_pf.get("extattrs", {})),
                vlans=build_vlan_map(vlans=_pf["vlans"]) if _pf.get("vlans") else {},
            )
            self.add(new_pf)

    def load_ipaddresses(self):
        """Load InfobloxIPAddress DiffSync model."""
        for _ip in self.conn.get_all_ipv4address_networks(prefixes=self.subnets):
            _, prefix_length = _ip["network"].split("/")
            if _ip["names"]:
                new_ip = self.ipaddress(
                    address=_ip["ip_address"],
                    prefix=_ip["network"],
                    prefix_length=prefix_length,
                    dns_name=_ip["names"][0],
                    status=self.conn.get_ipaddr_status(_ip),
                    description=_ip["comment"],
                    ext_attrs=get_ext_attr_dict(extattrs=_ip.get("extattrs", {})),
                )
                self.add(new_ip)

    def load_vlanviews(self):
        """Load InfobloxVLANView DiffSync model."""
        for _vv in self.conn.get_vlanviews():
            new_vv = self.vlangroup(
                name=_vv["name"],
                description=_vv["comment"] if _vv.get("comment") else "",
                ext_attrs=get_ext_attr_dict(extattrs=_vv.get("extattrs", {})),
            )
            self.add(new_vv)

    def load_vlans(self):
        """Load InfobloxVlan DiffSync model."""
        for _vlan in self.conn.get_vlans():
            vlan_group = re.search(r"(?:.+\:)(\S+)(?:\/\S+\/.+)", _vlan["_ref"])
            new_vlan = self.vlan(
                name=_vlan["name"],
                vid=_vlan["id"],
                status=_vlan["status"],
                vlangroup=vlan_group.group(1) if vlan_group else "",
                description=_vlan["comment"] if _vlan.get("comment") else "",
                ext_attrs=get_ext_attr_dict(extattrs=_vlan.get("extattrs", {})),
            )
            self.add(new_vlan)

    def load(self):
        """Load all models by calling other methods."""
        self.load_prefixes()
        self.load_ipaddresses()
        self.load_vlanviews()
        self.load_vlans()

    def sync_complete(self, source, diff, flags=DiffSyncFlags.NONE, logger=None):
        """Add tags and custom fields to synced objects."""
        source.tag_involved_objects(target=self)


class InfobloxAggregateAdapter(DiffSync):
    """DiffSync adapter using requests to communicate to Infoblox server."""

    aggregate = InfobloxAggregate

    top_level = ["aggregate"]

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

    def load(self):
        """Load aggregate models."""
        for container in self.conn.get_network_containers():
            network = ipaddress.ip_network(container["network"])
            if network.is_private and container["network"] in ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]:
                new_aggregate = self.aggregate(
                    network=container["network"],
                    description=container["comment"] if container.get("comment") else "",
                    ext_attrs=container.get("extattrs", {}),
                )
                self.add(new_aggregate)
