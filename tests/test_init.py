"""Test native MAC registration during integration setup."""

import pytest
from custom_components.fake_devices.const import CONF_ADVANCED, CONF_URL, DOMAIN
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


@pytest.mark.parametrize(
    "mac_address", [None, "", " \t ", "AABB.CCDD.EEFF", " aabb.ccdd.eeff "]
)
async def test_setup_and_reload(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    mac_address: str | None,
) -> None:
    """Existing entries and repeated setup preserve a single device."""
    data = {CONF_NAME: "Test Device", CONF_ADVANCED: {}}
    if mac_address is not None:
        data[CONF_ADVANCED][CONF_MAC] = mac_address
    entry = MockConfigEntry(domain=DOMAIN, data=data)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    device = dr.async_entries_for_config_entry(device_registry, entry.entry_id)[0]
    assert device.identifiers == {(DOMAIN, entry.entry_id)}
    expected_connections = (
        {(dr.CONNECTION_NETWORK_MAC, "aa:bb:cc:dd:ee:ff")}
        if mac_address and mac_address.strip()
        else set()
    )
    assert device.connections == expected_connections

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    devices = dr.async_entries_for_config_entry(device_registry, entry.entry_id)
    assert len(devices) == 1
    assert devices[0].id == device.id
    assert devices[0].connections == expected_connections


@pytest.mark.parametrize("mac_address", ["GG:BB:CC:DD:EE:FF", "aabbccddee", 123])
async def test_invalid_saved_mac(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    mac_address: str,
) -> None:
    """Malformed saved addresses produce a translated setup failure."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_NAME: "Test Device", CONF_ADVANCED: {CONF_MAC: mac_address}},
    )
    entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_ERROR
    assert entry.error_reason_translation_key == "invalid_mac"
    assert dr.async_entries_for_config_entry(device_registry, entry.entry_id) == []


async def test_native_mac_matching(
    hass: HomeAssistant, device_registry: dr.DeviceRegistry
) -> None:
    """A matching MAC reuses the existing device through native registration."""
    other_entry = MockConfigEntry()
    other_entry.add_to_hass(hass)
    existing_device = device_registry.async_get_or_create(
        config_entry_id=other_entry.entry_id,
        identifiers={("test", "existing-device")},
        connections={(dr.CONNECTION_NETWORK_MAC, "aa:bb:cc:dd:ee:ff")},
    )
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_NAME: "Test Device", CONF_ADVANCED: {CONF_MAC: "AABBCCDDEEFF"}},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    devices = dr.async_entries_for_config_entry(device_registry, entry.entry_id)
    assert len(devices) == 1
    assert devices[0].id == existing_device.id
    assert devices[0].identifiers == {
        ("test", "existing-device"),
        (DOMAIN, entry.entry_id),
    }
    assert devices[0].config_entries == {other_entry.entry_id, entry.entry_id}
    assert devices[0].connections == {(dr.CONNECTION_NETWORK_MAC, "aa:bb:cc:dd:ee:ff")}


async def test_invalid_saved_url(hass: HomeAssistant) -> None:
    """Adding MAC validation preserves URL validation during setup."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "Test Device",
            CONF_ADVANCED: {
                CONF_MAC: "AA:BB:CC:DD:EE:FF",
                CONF_URL: "ftp://example.com",
            },
        },
    )
    entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_ERROR
    assert entry.error_reason_translation_key == "invalid_url"
