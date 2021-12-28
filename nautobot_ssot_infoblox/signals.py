"""Post Migrate Welcome Wizard Script."""


def infoblox_create_tag(apps, **kwargs):
    """Add a tag for Infoblox SSOT."""
    tag = apps.get_model("extras", "Tag")
    tag.objects.update_or_create(
        name="Created By Infoblox",
        slug="created-by-infoblox",
        color="40bfae",
    )
