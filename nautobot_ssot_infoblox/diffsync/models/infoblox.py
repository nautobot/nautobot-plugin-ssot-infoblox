"""Infoblox Models for Infoblox integration with SSoT plugin."""
from nautobot_ssot_infoblox.diffsync.models.base import *


class InfobloxNetwork(Network):
    """Infoblox Implementation of the Network Model."""

    @classmethod
    def create(cls, diffsync, ids, attrs):
        """Create Network object in Infoblox."""
        # TODO call Infoblox Network Create.
        pass


# Not sure we will sync IPAddress to Infoblox as that would be creating a reservation.
# We would need a mac address to do that with, which would mean checking for the interface
# associated with the ip address in Nautobot. This will currently be out of scope, but neat
# to add if time.
# class InfobloxIPAdress(IPAddress):
