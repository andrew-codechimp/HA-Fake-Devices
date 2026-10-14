"""Test MAC address validation and normalisation."""

import pytest
from custom_components.fake_devices.common import normalize_mac_address


@pytest.mark.parametrize(
    "mac_address",
    [
        "AA:BB:CC:DD:EE:FF",
        "aa:bb:cc:dd:ee:ff",
        "Aa:bB:Cc:dD:Ee:fF",
        "aa-bb-cc-dd-ee-ff",
        "aabb.ccdd.eeff",
        "aabbccddeeff",
        "  aabb.ccdd.eeff\n",
    ],
)
def test_normalize_mac_address(mac_address: str) -> None:
    """Common formats produce uppercase, colon-separated addresses."""
    assert normalize_mac_address(mac_address) == "AA:BB:CC:DD:EE:FF"


@pytest.mark.parametrize("mac_address", [None, "", " \t\n"])
def test_empty_mac_address(mac_address: str | None) -> None:
    """An absent or blank address remains optional."""
    assert normalize_mac_address(mac_address) is None


@pytest.mark.parametrize(
    "mac_address",
    [
        "AA:BB:CC:DD:EE",
        "AA:BB:CC:DD:EE:FF:00",
        "GG:BB:CC:DD:EE:FF",
        "AA:BB-CC:DD:EE:FF",
        "A:BBB:CC:DD:EE:FF",
        "AABB.CCDD.EEFG",
        "AAB.CCDD.EEFFF",
        "AABBCCDDEEF",
        "AABBCCDDEEFF00",
        "AA BB CC DD EE FF",
        "AA:BB:CC: DD:EE:FF",
        123,
    ],
)
def test_invalid_mac_address(mac_address: str) -> None:
    """Malformed addresses fail before native formatting."""
    with pytest.raises(ValueError, match="MAC address"):
        normalize_mac_address(mac_address)
