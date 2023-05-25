"""Test utility methods for Nautobot."""
from django.contrib.contenttypes.models import ContentType
from nautobot.extras.models import Relationship, RelationshipAssociation, Status
from nautobot.ipam.models import Prefix, VLAN, VLANGroup
from nautobot.utilities.testing import TransactionTestCase
from nautobot_ssot_infoblox.utils.nautobot import build_vlan_map_from_relations, get_prefix_vlans


class TestNautobotUtils(TransactionTestCase):
    """Test Nautobot Utility methods."""

    def setUp(self):
        """Configure common objects for tests."""
        super().setUp()
        self.status_active = Status.objects.get(name="Active")
        self.test_pf = Prefix.objects.get_or_create(prefix="192.168.1.0/24")[0]
        self.vlan_group = VLANGroup.objects.create(name="Test")
        self.test_vlan1 = VLAN.objects.create(name="Test1", vid=1, status=self.status_active, group=self.vlan_group)
        self.test_vlan1.validated_save()
        self.test_vlan2 = VLAN.objects.create(name="Test2", vid=2, status=self.status_active, group=self.vlan_group)
        self.test_vlan2.validated_save()

    def test_build_vlan_map_from_relations(self):
        """Validate functionality of the build_vlan_map_from_relations() function."""
        test_list = [self.test_vlan1, self.test_vlan2]
        actual = build_vlan_map_from_relations(vlans=test_list)
        expected = {1: {"vid": 1, "name": "Test1", "group": "Test"}, 2: {"vid": 2, "name": "Test2", "group": "Test"}}
        self.assertEqual(actual, expected)

    def test_get_prefix_vlans_success(self):
        """Validate functionality of the get_prefix_vlans() function success."""
        pf_vlan_rel = Relationship.objects.get(slug="prefix_to_vlan")
        rel_assoc1 = RelationshipAssociation.objects.create(
            relationship_id=pf_vlan_rel.id,
            source_type=ContentType.objects.get_for_model(Prefix),
            source_id=self.test_pf.id,
            destination_type=ContentType.objects.get_for_model(VLAN),
            destination_id=self.test_vlan1.id,
        )
        rel_assoc1.validated_save()
        rel_assoc2 = RelationshipAssociation.objects.create(
            relationship_id=pf_vlan_rel.id,
            source_type=ContentType.objects.get_for_model(Prefix),
            source_id=self.test_pf.id,
            destination_type=ContentType.objects.get_for_model(VLAN),
            destination_id=self.test_vlan2.id,
        )
        rel_assoc2.validated_save()
        expected = [self.test_vlan1, self.test_vlan2]
        actual = get_prefix_vlans(self.test_pf)
        self.assertEqual(actual, expected)

    def test_get_prefix_vlans_failure(self):
        """Validate functionality of the get_prefix_vlans() function failure where Prefix has no RelationshipAssocations to VLANs."""
        expected = []
        actual = get_prefix_vlans(self.test_pf)
        self.assertEqual(actual, expected)
