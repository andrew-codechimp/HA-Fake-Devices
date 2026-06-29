"""
Custom integration to create fake devices in Home Assistant.

For more details about this integration, please refer to
https://github.com/andrew-codechimp/ha-fake-devices
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from awesomeversion.awesomeversion import AwesomeVersion
from homeassistant.const import (
    CONF_NAME,
    Platform,
)
from homeassistant.const import __version__ as HA_VERSION  # noqa: N812
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers import device_registry as dr

from .common import is_valid_url
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
    MIN_HA_VERSION,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:  # noqa: ARG001
    """Integration setup."""
    if AwesomeVersion(HA_VERSION) < AwesomeVersion(MIN_HA_VERSION):  # pragma: no cover
        msg = (
            "This integration requires at least Home Assistant version "
            f"{MIN_HA_VERSION}, you are running version {HA_VERSION}. "
            "Please upgrade Home Assistant to continue using this integration."
        )
        _LOGGER.critical(msg)
        return False

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    url = entry.data.get(CONF_ADVANCED, {}).get(CONF_URL)

    if url and not is_valid_url(url):
        raise ConfigEntryError(
            translation_domain=DOMAIN,
            translation_key="invalid_url",
        )
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.data[CONF_NAME],
        manufacturer=entry.data.get(CONF_MANUFACTURER),
        model=entry.data.get(CONF_MODEL),
        serial_number=entry.data.get(CONF_SERIAL_NUMBER),
        model_id=entry.data.get(CONF_ADVANCED, {}).get(CONF_MODEL_ID),
        hw_version=entry.data.get(CONF_ADVANCED, {}).get(CONF_HW_VERSION),
        sw_version=entry.data.get(CONF_ADVANCED, {}).get(CONF_SW_VERION),
        configuration_url=url,
    )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
