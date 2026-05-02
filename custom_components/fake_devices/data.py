"""Custom types for fake_devices."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

type FakeDevicesConfigEntry = ConfigEntry[FakeDevicesData]


@dataclass
class FakeDevicesData:
    """Data for the FakeDevices integration."""

    name: str
    manufacturer: str
    model: str | None
    serial_number: str | None
