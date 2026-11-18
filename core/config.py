"""
config.py
Central application configuration, environment settings, and security policies
for the AeroFamily Smog & Clean Air AI Guardian system.
"""

import os
import logging
from typing import Dict, Any


class Settings:
    """Application configuration container with immutable defaults."""

    APP_NAME: str = "AeroFamily - Smog & Clean Air AI Guardian"
    APP_VERSION: str = "1.2.0"
    APP_DESCRIPTION: str = (
        "GenAI-powered clinical and environmental copilot helping families "
        "and communities navigate severe winter smog and urban air pollution."
    )
    HOST: str = os.getenv("AERO_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("AERO_PORT", "8000"))
    DEBUG: bool = os.getenv("AERO_DEBUG", "false").lower() == "true"

    # Default scientific constants
    WHO_PM25_DAILY_LIMIT: float = 15.0  # µg/m³ 24-hr WHO 2021 threshold
    BERKELEY_MULLER_FACTOR: float = 22.0  # 22 µg/m³ over 24 hrs ~ 1 cigarette
    DEFAULT_INDOOR_VOLUME_CFM_RATIO: float = 60.0  # Minutes per hour for CADR math

    # CORS configuration
    ALLOWED_ORIGINS: list = ["*"]
    ALLOWED_METHODS: list = ["GET", "POST", "OPTIONS"]
    ALLOWED_HEADERS: list = ["*"]


settings = Settings()

# Hardened OWASP Security Headers (Full CSP allowing Open-Meteo & BigDataCloud APIs)
SECURITY_HEADERS: Dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": (
        "default-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com "
        "https://fonts.googleapis.com https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.open-meteo.com "
        "https://air-quality-api.open-meteo.com https://api.bigdatacloud.net "
        "https://generativelanguage.googleapis.com;"
    ),
    "Permissions-Policy": "geolocation=(self)",
}


def get_logger(name: str) -> logging.Logger:
    """Configures and returns a structured logger instance for a given module.

    Args:
        name (str): The logger / module namespace.

    Returns:
        logging.Logger: Configured logger with standard formatting.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    return logger
