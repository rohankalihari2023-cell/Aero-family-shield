"""
exceptions.py
Custom application exception hierarchy for AeroFamily.
Enables precise error handling, predictable REST responses, and reliable debugging.
"""

from typing import Optional, Dict, Any


class AeroFamilyError(Exception):
    """Base exception class for all AeroFamily domain errors."""

    def __init__(self, message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Serializes error to a consistent API response dictionary."""
        return {
            "error": True,
            "status_code": self.status_code,
            "message": self.message,
            "details": self.details,
        }


class CityNotFoundError(AeroFamilyError):
    """Raised when a requested city or microclimate identifier is not found."""

    def __init__(self, city_id: str):
        super().__init__(
            message=f"City '{city_id}' is not registered in the atmospheric knowledge base.",
            status_code=404,
            details={"city_id": city_id}
        )


class ValidationError(AeroFamilyError):
    """Raised when an input fails domain-specific validation constraints."""

    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation failed for field '{field}': {message}",
            status_code=422,
            details={"field": field, "reason": message}
        )


class ExternalAPIError(AeroFamilyError):
    """Raised when an external API (e.g. Gemini, Open-Meteo) fails or times out."""

    def __init__(self, service_name: str, message: str):
        super().__init__(
            message=f"External service '{service_name}' error: {message}",
            status_code=502,
            details={"service": service_name, "reason": message}
        )
