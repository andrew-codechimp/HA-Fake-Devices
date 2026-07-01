"""Adds config flow for fake_devices."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import section
from homeassistant.helpers.selector import IconSelector

from .common import is_valid_url
from .const import (
    CONF_ADVANCED,
    CONF_ENTITY_CATEGORY,
    CONF_HW_VERSION,
    CONF_ICON,
    CONF_INPUT_NUMBER_MAX,
    CONF_INPUT_NUMBER_MIN,
    CONF_MANUFACTURER,
    CONF_MODEL,
    CONF_MODEL_ID,
    CONF_SERIAL_NUMBER,
    CONF_SW_VERION,
    CONF_URL,
    CONF_VALUE,
    DOMAIN,
    SUBENTRY_INPUT_NUMBER,
    SUBENTRY_SENSOR,
)

USER_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): str,
    vol.Optional(CONF_MANUFACTURER): str,
    vol.Optional(CONF_MODEL): str,
    vol.Optional(CONF_SERIAL_NUMBER): str,
    vol.Required(CONF_ADVANCED): section(
        vol.Schema({
            vol.Optional(CONF_MODEL_ID): str,
            vol.Optional(CONF_HW_VERSION): str,
            vol.Optional(CONF_SW_VERION): str,
            vol.Optional(CONF_URL): str,
        }),
        {"collapsed": True},
    ),
})

INPUT_NUMBER_SUBENTRY_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): str,
    vol.Required(CONF_INPUT_NUMBER_MIN): vol.Coerce(float),
    vol.Required(CONF_INPUT_NUMBER_MAX, default=100): vol.Coerce(float),
    vol.Required(CONF_ENTITY_CATEGORY, default="sensor"): vol.In([
        "sensor",
        "diagnostic",
    ]),
    vol.Optional(CONF_ICON): IconSelector(),
})

SENSOR_SUBENTRY_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): str,
    vol.Required(CONF_VALUE): str,
    vol.Required(CONF_ENTITY_CATEGORY, default="sensor"): vol.In([
        "sensor",
        "diagnostic",
    ]),
    vol.Optional(CONF_ICON): IconSelector(),
})


class FakeDevicesFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Fake Devices."""

    VERSION = 1

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, _config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this handler."""
        return {
            SUBENTRY_INPUT_NUMBER: InputNumberSubentryFlowHandler,
            SUBENTRY_SENSOR: SensorSubentryFlowHandler,
        }

    async def check_url(self, url: str) -> dict[str, str]:
        """Check URL is valid."""
        if not is_valid_url(url):
            return {"base": "invalid_url"}
        return {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input:
            url = user_input.get(CONF_ADVANCED, {}).get(CONF_URL)
            if url:
                errors = await self.check_url(url)
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
            url = user_input.get(CONF_ADVANCED, {}).get(CONF_URL)
            if url:
                errors = await self.check_url(url)
        if user_input and not errors:
            self.hass.config_entries.async_update_entry(
                config_entry,
                title=user_input[CONF_NAME],
                data={
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_MANUFACTURER: user_input.get(CONF_MANUFACTURER),
                    CONF_MODEL: user_input.get(CONF_MODEL),
                    CONF_SERIAL_NUMBER: user_input.get(CONF_SERIAL_NUMBER),
                    CONF_ADVANCED: {
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


class InputNumberSubentryFlowHandler(ConfigSubentryFlow):
    """Handle subentry flow for adding an input number."""

    @staticmethod
    def _validate_min_max(data: dict[str, Any]) -> dict[str, str]:
        """Validate input number range."""
        if data[CONF_INPUT_NUMBER_MIN] > data[CONF_INPUT_NUMBER_MAX]:
            return {"base": "invalid_min_max"}
        return {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Add a input number subentry."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = self._validate_min_max(user_input)
            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                INPUT_NUMBER_SUBENTRY_SCHEMA,
                user_input,
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Reconfigure an input number subentry."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = self._validate_min_max(user_input)
            if not errors:
                return self.async_update_and_abort(
                    self._get_entry(),
                    self._get_reconfigure_subentry(),
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

        reconfigure_subentry = self._get_reconfigure_subentry()
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                INPUT_NUMBER_SUBENTRY_SCHEMA,
                reconfigure_subentry.data if user_input is None else user_input,
            ),
            errors=errors,
        )


class SensorSubentryFlowHandler(ConfigSubentryFlow):
    """Handle subentry flow for adding a sensor."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Add a sensor subentry."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                SENSOR_SUBENTRY_SCHEMA,
                user_input,
            ),
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Reconfigure a sensor subentry."""
        if user_input is not None:
            return self.async_update_and_abort(
                self._get_entry(),
                self._get_reconfigure_subentry(),
                title=user_input[CONF_NAME],
                data=user_input,
            )

        reconfigure_subentry = self._get_reconfigure_subentry()
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                SENSOR_SUBENTRY_SCHEMA,
                reconfigure_subentry.data if user_input is None else user_input,
            ),
        )
