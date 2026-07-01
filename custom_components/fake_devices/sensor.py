"""Sensor platform for fake_devices."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME, EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo

from .const import CONF_ENTITY_CATEGORY, CONF_ICON, CONF_VALUE, DOMAIN, SUBENTRY_SENSOR

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
    entities = []

    for subentry in config_entry.subentries.values():
        if subentry.subentry_type == SUBENTRY_SENSOR:
            subentry_data = subentry.data
            entity = FakeSensor(
                entry_id=config_entry.entry_id,
                subentry_id=subentry.subentry_id,
                name=subentry_data.get(CONF_NAME),
                state=subentry_data.get(CONF_VALUE),
                entity_category=subentry_data.get(CONF_ENTITY_CATEGORY, "sensor"),
                icon=subentry_data.get(CONF_ICON),
            )
            entities.append(entity)

    async_add_entities(entities)


class FakeSensor(SensorEntity):
    """Representation of a fake sensor."""

    _attr_has_entity_name = True

    def __init__(  # noqa: PLR0913
        self,
        entry_id: str,
        subentry_id: str,
        name: str,
        state: str,
        entity_category: str,
        icon: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        self._entry_id = entry_id
        self._subentry_id = subentry_id
        self._attr_native_value = state
        self._attr_name = name
        if icon:
            self._attr_icon = icon

        # Set entity category based on configuration
        if entity_category == "diagnostic":
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

        # Create unique ID from entry and subentry
        self._attr_unique_id = f"{entry_id}_{subentry_id}_sensor"

        # Associate with parent device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
        )
