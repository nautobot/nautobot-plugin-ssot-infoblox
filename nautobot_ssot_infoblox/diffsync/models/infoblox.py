"""Infoblox Models for Infoblox integration with SSoT plugin."""
from nautobot_ssot_infoblox.diffsync.models.base import Network, IPAddress, Vlan


class InfobloxNetwork(Network):
    """Infoblox implementation of the Network Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Network object in Infoblox."""
        new_net = None
        new_net.validated_save()
        # TODO call Infoblox Network Create.
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)


class InfobloxVLAN(Vlan):
    """Infoblox implementation of the VLAN Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create VLAN object in Infoblox."""
        new_vlan = None
        new_vlan.validated_save()
        # TODO call Infoblox VLAN Create.
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)


class InfobloxIPAddress(IPAddress):
    """Infoblox implementation of the VLAN Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create VLAN object in Infoblox."""
        new_ip = None
        new_ip.validated_save()
        # TODO call Infoblox VLAN Create.
        return super().create(ids=ids, diffsync=diffsync, attrs=attrs)
