"""Adds config flow for fake_devices."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.data_entry_flow import section
from homeassistant.helpers import device_registry as dr

from .common import is_valid_url, normalize_mac_address
from .const import (
    CONF_ADVANCED,
    CONF_HW_VERSION,
    CONF_MANUFACTURER,
    CONF_MODEL,
    CONF_MODEL_ID,
    CONF_SERIAL_NUMBER,
    CONF_SW_VERION,
    CONF_URL,
    DOMAIN,
)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Optional(CONF_MANUFACTURER): str,
        vol.Optional(CONF_MODEL): str,
        vol.Optional(CONF_SERIAL_NUMBER): str,
        vol.Required(CONF_ADVANCED): section(
            vol.Schema(
                {
                    vol.Optional(CONF_MODEL_ID): str,
                    vol.Optional(CONF_HW_VERSION): str,
                    vol.Optional(CONF_SW_VERION): str,
                    vol.Optional(CONF_URL): str,
                    vol.Optional(CONF_MAC): str,
                }
            ),
            {"collapsed": True},
        ),
    }
)


class FakeDevicesFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Fake Devices."""

    VERSION = 1

    async def check_url(self, url: str) -> dict[str, str]:
        """Check URL is valid."""
        if not is_valid_url(url):
            return {"base": "invalid_url"}
        return {}

    async def check_input(self, user_input: dict[str, Any]) -> dict[str, str]:
        """Validate form input and normalise an optional MAC address."""
        errors: dict[str, str] = {}
        advanced = user_input[CONF_ADVANCED]
        url = advanced.get(CONF_URL)
        if url:
            errors = await self.check_url(url)

        try:
            mac_address = normalize_mac_address(advanced.get(CONF_MAC))
        except ValueError:
            errors[CONF_ADVANCED] = "invalid_mac"
        else:
            if mac_address:
                advanced[CONF_MAC] = mac_address
            else:
                advanced.pop(CONF_MAC, None)

        return errors

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input:
            errors = await self.check_input(user_input)
        if user_input and not errors:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the integration."""
        config_entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input:
            errors = await self.check_input(user_input)
        if user_input and not errors:
            old_mac = config_entry.data.get(CONF_ADVANCED, {}).get(CONF_MAC)
            mac_address = user_input[CONF_ADVANCED].get(CONF_MAC)
            if old_mac != mac_address:
                device_registry = dr.async_get(self.hass)
                for device in dr.async_entries_for_config_entry(
                    device_registry, config_entry.entry_id
                ):
                    if (DOMAIN, config_entry.entry_id) not in device.identifiers:
                        continue
                    connections = set(device.connections)
                    if isinstance(old_mac, str) and old_mac:
                        connections.discard(
                            (
                                dr.CONNECTION_NETWORK_MAC,
                                dr.format_mac(old_mac.strip()),
                            )
                        )
                    if mac_address:
                        connections.add(
                            (
                                dr.CONNECTION_NETWORK_MAC,
                                dr.format_mac(mac_address),
                            )
                        )
                    # Registration merges connections, so remove the previous MAC explicitly.
                    if connections != device.connections:
                        device_registry.async_update_device(
                            device.id, new_connections=connections
                        )
                    break

            self.hass.config_entries.async_update_entry(
                config_entry,
                title=user_input[CONF_NAME],
                data={
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_MANUFACTURER: user_input.get(CONF_MANUFACTURER),
                    CONF_MODEL: user_input.get(CONF_MODEL),
                    CONF_SERIAL_NUMBER: user_input.get(CONF_SERIAL_NUMBER),
                    CONF_ADVANCED: {
                        **({CONF_MAC: mac_address} if mac_address else {}),
                        CONF_MODEL_ID: user_input.get(CONF_ADVANCED, {}).get(
                            CONF_MODEL_ID
                        ),
                        CONF_HW_VERSION: user_input.get(CONF_ADVANCED, {}).get(
                            CONF_HW_VERSION
                        ),
                        CONF_SW_VERION: user_input.get(CONF_ADVANCED, {}).get(
                            CONF_SW_VERION
                        ),
                        CONF_URL: user_input.get(CONF_ADVANCED, {}).get(CONF_URL),
                    },
                },
            )
            await self.hass.config_entries.async_reload(config_entry.entry_id)
            return self.async_abort(reason="reconfigure_successful")
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                USER_SCHEMA, config_entry.data
            ),
            errors=errors,
        )
