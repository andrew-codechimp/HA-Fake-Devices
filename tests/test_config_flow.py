"""Test creation and reconfiguration with MAC addresses."""

from typing import Any

import pytest
import voluptuous as vol
from custom_components.fake_devices.const import CONF_ADVANCED, CONF_URL, DOMAIN
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


async def test_user_form(hass: HomeAssistant) -> None:
    """The MAC field appears as an optional field in the advanced section."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}
    mac_field = next(
        field
        for field in result["data_schema"].schema[CONF_ADVANCED].schema.schema
        if field.schema == CONF_MAC
    )
    assert isinstance(mac_field, vol.Optional)
    assert CONF_MAC not in result["data_schema"].schema


@pytest.mark.parametrize(
    "mac_address",
    ["aa:bb:cc:dd:ee:ff", "AA-BB-CC-DD-EE-FF", "aabb.ccdd.eeff", " aabbccddeeff "],
)
async def test_create_with_mac(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    mac_address: str,
) -> None:
    """Creating a device saves uppercase and registers a native connection."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "Test Device", CONF_ADVANCED: {CONF_MAC: mac_address}},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_ADVANCED][CONF_MAC] == "AA:BB:CC:DD:EE:FF"
    entry = result["result"]
    devices = dr.async_entries_for_config_entry(device_registry, entry.entry_id)
    assert len(devices) == 1
    assert devices[0].identifiers == {(DOMAIN, entry.entry_id)}
    assert devices[0].connections == {(dr.CONNECTION_NETWORK_MAC, "aa:bb:cc:dd:ee:ff")}


@pytest.mark.parametrize("mac_address", [None, "", " \t "])
async def test_create_without_mac(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    mac_address: str | None,
) -> None:
    """Omitted and blank addresses are not saved or registered."""
    user_input = {CONF_NAME: "Test Device", CONF_ADVANCED: {}}
    if mac_address is not None:
        user_input[CONF_ADVANCED][CONF_MAC] = mac_address
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert CONF_MAC not in result["data"][CONF_ADVANCED]
    devices = dr.async_entries_for_config_entry(
        device_registry, result["result"].entry_id
    )
    assert len(devices) == 1
    assert devices[0].connections == set()


@pytest.mark.parametrize("source", ["user", "reconfigure"])
async def test_invalid_form_input(hass: HomeAssistant, source: str) -> None:
    """Both forms report MAC and URL errors without changing saved data."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_NAME: "Original", CONF_ADVANCED: {CONF_MAC: "AA:BB:CC:DD:EE:FF"}},
    )
    entry.add_to_hass(hass)
    context = {"source": source}
    if source == "reconfigure":
        context["entry_id"] = entry.entry_id
    result = await hass.config_entries.flow.async_init(DOMAIN, context=context)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Changed",
            CONF_ADVANCED: {
                CONF_MAC: "GG:BB:CC:DD:EE:FF",
                CONF_URL: "ftp://example.com",
            },
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_url", CONF_ADVANCED: "invalid_mac"}
    assert entry.data == {
        CONF_NAME: "Original",
        CONF_ADVANCED: {CONF_MAC: "AA:BB:CC:DD:EE:FF"},
    }

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "Changed", CONF_ADVANCED: {CONF_MAC: "GG:BB:CC:DD:EE:FF"}},
    )
    assert result["errors"] == {CONF_ADVANCED: "invalid_mac"}


@pytest.mark.parametrize(
    ("old_mac", "new_mac", "expected_mac"),
    [
        (None, "aabb.ccdd.eeff", "AA:BB:CC:DD:EE:FF"),
        ("AA:BB:CC:DD:EE:FF", "112233445566", "11:22:33:44:55:66"),
        (" aabb.ccdd.eeff ", "112233445566", "11:22:33:44:55:66"),
        ("AA:BB:CC:DD:EE:FF", "aa-bb-cc-dd-ee-ff", "AA:BB:CC:DD:EE:FF"),
        ("AA:BB:CC:DD:EE:FF", "", None),
        ("AA:BB:CC:DD:EE:FF", " \t ", None),
        ("AA:BB:CC:DD:EE:FF", None, None),
    ],
)
async def test_reconfigure_mac(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    old_mac: str | None,
    new_mac: str | None,
    expected_mac: str | None,
) -> None:
    """Reconfiguration changes only the configured MAC and preserves identity."""
    data = {CONF_NAME: "Original", CONF_ADVANCED: {}}
    if old_mac:
        data[CONF_ADVANCED][CONF_MAC] = old_mac
    entry = MockConfigEntry(domain=DOMAIN, data=data)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    device = dr.async_entries_for_config_entry(device_registry, entry.entry_id)[0]
    other_connections = {
        (dr.CONNECTION_NETWORK_MAC, "99:88:77:66:55:44"),
        (dr.CONNECTION_UPNP, "unrelated-device"),
    }
    device_registry.async_update_device(
        device.id, new_connections=device.connections | other_connections
    )

    result = await entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    mac_field = next(
        field
        for field in result["data_schema"].schema[CONF_ADVANCED].schema.schema
        if field.schema == CONF_MAC
    )
    if old_mac:
        assert mac_field.description == {"suggested_value": old_mac}
    user_input: dict[str, Any] = {
        CONF_NAME: "Changed",
        CONF_ADVANCED: {CONF_URL: "https://example.com/device"},
    }
    if new_mac is not None:
        user_input[CONF_ADVANCED][CONF_MAC] = new_mac
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_ADVANCED].get(CONF_MAC) == expected_mac
    if expected_mac is None:
        assert CONF_MAC not in entry.data[CONF_ADVANCED]
    devices = dr.async_entries_for_config_entry(device_registry, entry.entry_id)
    assert len(devices) == 1
    assert devices[0].id == device.id
    assert devices[0].identifiers == device.identifiers
    assert devices[0].name == "Changed"
    assert devices[0].configuration_url == "https://example.com/device"
    expected_connections = set(other_connections)
    if expected_mac:
        expected_connections.add((dr.CONNECTION_NETWORK_MAC, expected_mac.lower()))
    assert devices[0].connections == expected_connections


async def test_reconfigure_native_collision(
    hass: HomeAssistant, device_registry: dr.DeviceRegistry
) -> None:
    """A native collision leaves the previous address and saved data intact."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_NAME: "Original", CONF_ADVANCED: {CONF_MAC: "AA:BB:CC:DD:EE:FF"}},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    other_entry = MockConfigEntry(domain=DOMAIN)
    other_entry.add_to_hass(hass)
    device_registry.async_get_or_create(
        config_entry_id=other_entry.entry_id,
        identifiers={(DOMAIN, other_entry.entry_id)},
        connections={(dr.CONNECTION_NETWORK_MAC, "11:22:33:44:55:66")},
    )
    result = await entry.start_reconfigure_flow(hass)

    with pytest.raises(dr.DeviceConnectionCollisionError):
        await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_NAME: "Changed", CONF_ADVANCED: {CONF_MAC: "112233445566"}},
        )

    assert entry.data == {
        CONF_NAME: "Original",
        CONF_ADVANCED: {CONF_MAC: "AA:BB:CC:DD:EE:FF"},
    }
    device = dr.async_entries_for_config_entry(device_registry, entry.entry_id)[0]
    assert device.connections == {(dr.CONNECTION_NETWORK_MAC, "aa:bb:cc:dd:ee:ff")}
