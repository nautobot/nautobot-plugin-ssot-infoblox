"""Infoblox Adapter for Infoblox integration with SSoT plugin."""
import ipaddress
import re

from diffsync import DiffSync
from diffsync.enum import DiffSyncFlags
from nautobot_ssot_infoblox.diffsync.client import InfobloxApi
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

    top_level = ["prefix", "ipaddress", "vlangroup", "vlan"]

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
        """Method to load InfobloxNetwork DiffSync model."""
        # Need to load containers here to prevent duplicates when syncing back to Infoblox
        containers = self.conn.get_network_containers()
        subnets = self.conn.get_all_subnets()
        self.subnets = [x["network"] for x in subnets]
        all_networks = containers + subnets
        for _pf in all_networks:
            new_pf = self.prefix(
                network=_pf["network"],
                description=_pf.get("comment", ""),
                status=_pf.get("status", "active"),
            )
            self.add(new_pf)

    def load_ipaddresses(self):
        """Method to load InfobloxIPAddress DiffSync model."""
        for _prefix in self.subnets:
            for _ip in self.conn.get_all_ipv4address_networks(prefix=_prefix):
                _, prefix_length = _ip["network"].split("/")
                if _ip["names"]:
                    new_ip = self.ipaddress(
                        address=_ip["ip_address"],
                        prefix=_ip["network"],
                        prefix_length=prefix_length,
                        dns_name=_ip["names"][0],
                        status=self.conn.get_ipaddr_status(_ip),
                        description=_ip["comment"],
                    )
                    self.add(new_ip)

    def load_vlanviews(self):
        """Method to load InfobloxVLANView DiffSync model."""
        for _vv in self.conn.get_vlanviews():
            new_vv = self.vlangroup(
                name=_vv["name"],
                description=_vv["comment"] if _vv.get("comment") else "",
            )
            self.add(new_vv)

    def load_vlans(self):
        """Method to load InfoblocVlan DiffSync model."""
        for _vlan in self.conn.get_vlans():
            vlan_group = re.search(r"(?:.+\:)(\S+)(?:\/\S+\/.+)", _vlan["_ref"])
            new_vlan = self.vlan(
                name=_vlan["name"],
                vid=_vlan["id"],
                status=_vlan["status"],
                vlangroup=vlan_group.group(1) if vlan_group else "",
                description=_vlan["comment"] if _vlan.get("comment") else "",
            )
            self.add(new_vlan)

    def load(self):
        """Method for one stop shop loading of all models."""
        self.load_prefixes()
        self.load_ipaddresses()
        # self.load_vlanviews()
        # self.load_vlans()

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
        """Method for loading aggregate models."""
        for container in self.conn.get_network_containers():
            network = ipaddress.ip_network(container["network"])
            if network.is_private and container["network"] in ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]:
                new_aggregate = self.aggregate(
                    network=container["network"],
                    description=container["comment"] if container.get("comment") else "",
                )
                self.add(new_aggregate)
