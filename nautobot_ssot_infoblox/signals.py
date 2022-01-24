"""Signal handlers for nautobot_ssot_infoblox."""


from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot_ssot_infoblox.constant import TAG_COLOR


def nautobot_database_ready_callback(sender, *, apps, **kwargs):  # pylint: disable=unused-argument
    """Callback function triggered by the nautobot_database_ready signal when the Nautobot database is fully ready."""
    # pylint: disable=invalid-name
    ContentType = apps.get_model("contenttypes", "ContentType")
    CustomField = apps.get_model("extras", "CustomField")
    Prefix = apps.get_model("ipam", "Prefix")
    IPAddress = apps.get_model("ipam", "IPAddress")
    Aggregate = apps.get_model("ipam", "Aggregate")
    Tag = apps.get_model("extras", "Tag")

    Tag.objects.get_or_create(
        slug="ssot-synced-from-infoblox",
        defaults={
            "name": "SSoT Synced from Infoblox",
            "description": "Object synced at some point from Infoblox",
            "color": TAG_COLOR,
        },
    )
    Tag.objects.get_or_create(
        slug="ssot-synced-to-infoblox",
        defaults={
            "name": "SSoT Synced to Infoblox",
            "description": "Object synced at some point to Infoblox",
            "color": TAG_COLOR,
        },
    )
    custom_field, _ = CustomField.objects.get_or_create(
        type=CustomFieldTypeChoices.TYPE_DATE,
        name="ssot-synced-to-infoblox",
        defaults={
            "label": "Last synced to Infoblox on",
        },
    )
    for content_type in [
        ContentType.objects.get_for_model(Prefix),
        ContentType.objects.get_for_model(IPAddress),
        ContentType.objects.get_for_model(Aggregate),
    ]:
        custom_field.content_types.add(content_type)
