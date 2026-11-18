"""
AeroFamily Core Package
Central configuration, settings, and custom exception hierarchies.
"""

from .config import settings, SECURITY_HEADERS, get_logger
from .exceptions import (
    AeroFamilyError,
    CityNotFoundError,
    ValidationError,
    ExternalAPIError,
)

__all__ = [
    "settings",
    "SECURITY_HEADERS",
    "get_logger",
    "AeroFamilyError",
    "CityNotFoundError",
    "ValidationError",
    "ExternalAPIError",
]
