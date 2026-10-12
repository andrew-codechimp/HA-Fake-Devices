"""Common functions."""

import re
from urllib.parse import urlparse

from homeassistant.helpers import device_registry as dr

_MAC_ADDRESS_PATTERN = re.compile(
    r"(?:[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}"
    r"|[0-9a-fA-F]{2}(?:-[0-9a-fA-F]{2}){5}"
    r"|[0-9a-fA-F]{4}(?:\.[0-9a-fA-F]{4}){2}"
    r"|[0-9a-fA-F]{12})"
)


def is_valid_url(url: str) -> bool:
    """Return True if the string is a valid HTTP/HTTPS URL."""
    result = urlparse(url)
    return result.scheme in {"http", "https"} and bool(result.netloc)


def normalize_mac_address(mac_address: str | None) -> str | None:
    """Validate a MAC address and return uppercase, colon-separated pairs."""
    if mac_address is None:
        return None
    if not isinstance(mac_address, str):
        raise ValueError("MAC address must be a string")

    mac_address = mac_address.strip()
    if not mac_address:
        return None
    if not _MAC_ADDRESS_PATTERN.fullmatch(mac_address):
        raise ValueError("Invalid MAC address")

    # Home Assistant formats addresses but does not validate hexadecimal input.
    return dr.format_mac(mac_address).upper()
