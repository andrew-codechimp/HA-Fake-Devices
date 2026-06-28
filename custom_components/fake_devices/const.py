"""Constants for fake_devices."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "fake_devices"
MIN_HA_VERSION = "2026.4.0"

CONF_MANUFACTURER = "manufacturer"
CONF_MODEL = "model"
CONF_MODEL_ID = "model_id"
CONF_SERIAL_NUMBER = "serial_number"
CONF_ADVANCED = "advanced"
CONF_HW_VERSION = "hw_version"
CONF_SW_VERION = "sw_version"
CONF_URL = "url"
