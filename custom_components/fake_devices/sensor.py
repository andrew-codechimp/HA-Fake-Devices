"""Sensor platform for fake_devices."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME, CONF_UNIT_OF_MEASUREMENT, EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo

from .const import (
    CONF_ENTITY_CATEGORY,
    CONF_ICON,
    CONF_STATE,
    DOMAIN,
    SUBENTRY_STATIC_SENSOR,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from subentries."""
    async_add_entities(
        [
            FakeStaticSensor(config_entry, subentry.subentry_id)
            for subentry in config_entry.subentries.values()
            if subentry.subentry_type == SUBENTRY_STATIC_SENSOR
        ]
    )


class FakeStaticSensor(SensorEntity):
    """Representation of a fake static sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        config_entry: ConfigEntry,
        subentry_id: str,
    ) -> None:
        """Initialize the sensor."""
        self._config_entry = config_entry
        self._subentry_id = subentry_id
        subentry_data = config_entry.subentries[subentry_id].data
        self._attr_name = subentry_data[CONF_NAME]
        self._attr_native_unit_of_measurement = subentry_data.get(
            CONF_UNIT_OF_MEASUREMENT
        )
        if icon := subentry_data.get(CONF_ICON):
            self._attr_icon = icon

        # Set entity category based on configuration
        if subentry_data.get(CONF_ENTITY_CATEGORY, "sensor") == "diagnostic":
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

        # Create unique ID from entry and subentry
        self._attr_unique_id = f"{config_entry.entry_id}_{subentry_id}_sensor"

        # Associate with parent device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
        )

    @property
    def native_value(self) -> str:
        """Return the configured state from the subentry data."""
        return self._config_entry.subentries[self._subentry_id].data[CONF_STATE]
