"""Utilities for DiffSync related stuff."""

from django.utils.text import slugify
from nautobot.extras.models import Tag
from nautobot_ssot_infoblox.constant import TAG_COLOR


def create_tag_sync_from_infoblox():
    """Create tag for tagging objects that have been created by Infoblox."""
    tag, _ = Tag.objects.get_or_create(
        slug="ssot-synced-from-infoblox",
        defaults={
            "name": "SSoT Synced from Infoblox",
            "description": "Object synced at some point from Infoblox",
            "color": TAG_COLOR,
        },
    )
    return tag


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
    """Return VLAN Status from mapping."""
    statuses = {
        "Active": "ASSIGNED",
        "Deprecated": "UNASSIGNED",
        "Reserved": "RESERVED",
    }
    return statuses[status]


def get_ext_attr_dict(extattrs: dict):
    """Rebuild Extensibility Attributes dict into standard k/v pattern.

    The standard extattrs dict pattern is to have the dict look like so:

    {<attribute_key>: {"value": <actual_value>}}

    Args:
        extattrs (dict): Extensibility Attributes dict for object.

    Returns:
        dict: Standardized dictionary for Extensibility Attributes.
    """
    fixed_dict = {}
    for key, value in extattrs.items():
        fixed_dict[slugify(key)] = value["value"]
    return fixed_dict
