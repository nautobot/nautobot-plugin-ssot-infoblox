"""Utilities for diffsync related stuff."""

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
