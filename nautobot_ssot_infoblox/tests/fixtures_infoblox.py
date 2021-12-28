"""Infoblox Fixtures."""
# Ignoring docstrings on fixtures  pylint: disable=missing-function-docstring
# Ignoring using fixtures in other fixtures  pylint: disable=redefined-outer-name
import json
import os


from nautobot_ssot_infoblox.diffsync import client

FIXTURES = os.environ.get("FIXTURE_DIR", "nautobot_ssot_infoblox/tests/fixtures")

LOCALHOST = os.environ.get("TEST_LOCALHOST_URL", "http://localhost:4440/wapi/v2.12")


def _json_read_fixture(name):
    """Return JSON fixture."""
    with open(f"{FIXTURES}/{name}", encoding="utf8") as fixture:
        return json.load(fixture)


def localhost_client_infoblox(localhost_url):
    return client.InfobloxApi(  # nosec
        url=localhost_url, username="test-user", password="test-password", verify_ssl=False, cookie=None
    )


def get_all_ipv4address_networks():
    return _json_read_fixture("get_all_ipv4address_networks.json")


def create_ptr_record():
    return _json_read_fixture("create_ptr_record.json")


def create_a_record():
    return _json_read_fixture("create_a_record.json")


def create_host_record():
    return _json_read_fixture("create_host_record.json")


def get_host_by_ip():
    return _json_read_fixture("get_host_by_ip.json")


def get_a_record_by_ip():
    return _json_read_fixture("get_a_record_by_ip.json")


def get_a_record_by_name():
    return _json_read_fixture("get_a_record_by_name.json")


def get_host_record_by_name():
    return _json_read_fixture("get_host_record_by_name.json")


def get_all_dns_views():
    return _json_read_fixture("get_all_dns_views.json")


def get_dhcp_lease_from_ipv4():
    return _json_read_fixture("get_dhcp_lease_from_ipv4.json")


def get_dhcp_lease_from_hostname():
    return _json_read_fixture("get_dhcp_lease_from_hostname.json")


def get_all_subnets():
    return _json_read_fixture("get_all_subnets.json")


def get_authoritative_zone():
    return _json_read_fixture("get_authoritative_zone.json")


def find_network_reference():
    return _json_read_fixture("find_network_reference.json")


def get_ptr_record_by_name():
    return _json_read_fixture("get_ptr_record_by_name.json")


def find_next_available_ip():
    return _json_read_fixture("find_next_available_ip.json")


def search_ipv4_address():
    return _json_read_fixture("search_ipv4_address.json")
