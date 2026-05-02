"""Adds config flow for fake_devices."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME

from .const import (
    CONF_MANUFACTURER,
    CONF_MODEL,
    CONF_SERIAL_NUMBER,
    DOMAIN,
)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_MANUFACTURER): str,
        vol.Optional(CONF_MODEL): str,
        vol.Optional(CONF_SERIAL_NUMBER): str,
    }
)


class FakeDevicesFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for FakeDevices."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
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
        if user_input and not errors:
            self.hass.config_entries.async_update_entry(
                config_entry,
                title=user_input[CONF_NAME],
                data={
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_MANUFACTURER: user_input[CONF_MANUFACTURER],
                    CONF_MODEL: user_input.get(CONF_MODEL),
                    CONF_SERIAL_NUMBER: user_input.get(CONF_SERIAL_NUMBER),
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
