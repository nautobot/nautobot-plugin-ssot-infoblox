"""Utilities."""


def get_vlan_view_name(reference):
    """Get the Infoblox vlanview name by the reference resource string.

    Args:
        reference (str): Vlan view Reference resource.

    Returns:
        (str): Vlan view name.

    Returns Response:
        "Nautobot"
    """
    return reference.split("/")[1].split(":")[-1]


def nautobot_vlan_status(status: str) -> str:
    """Method to return VLAN Status from mapping."""
    statuses = {
        "Active": "ASSIGNED",
        "Deprecated": "UNASSIGNED",
        "Reserved": "RESERVED",
    }
    return statuses[status]
