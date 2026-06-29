"""Common functions."""

from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """Return True if the string is a valid HTTP/HTTPS URL."""
    result = urlparse(url)
    return result.scheme in {"http", "https"} and bool(result.netloc)
