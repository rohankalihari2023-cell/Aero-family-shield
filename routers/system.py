"""
system.py
Diagnostic health check, system telemetry, and root web delivery endpoints.
"""

import os
import time
from typing import Dict, Any

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse

from core.config import settings
from models.schemas import StatusResponseSchema

router = APIRouter(tags=["System"])

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")


@router.get(
    "/api/status",
    response_model=StatusResponseSchema,
    summary="Retrieve application health and active capability matrix",
    description="Returns real-time telemetry confirming operational readiness, version metadata, and active feature sets."
)
def get_system_status() -> Dict[str, Any]:
    """Retrieves operational telemetry, deployment version, and enabled subsystems.

    Returns:
        Dict[str, Any]: Diagnostic report containing status, app name, version,
            active feature flags, and current Unix epoch timestamp.

    Examples:
        >>> status = get_system_status()
        >>> status["status"]
        'online'
    """
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "features": [
            "Geolocation-Weather-API",
            "Open-Meteo-Sync",
            "WCAG-2.1-AAA",
            "WHO-2021-AQG",
            "Berkeley-Earth-Model",
            "Corsi-Rosenthal-CADR",
        ],
        "timestamp": time.time(),
    }


@router.get(
    "/",
    response_class=FileResponse,
    summary="Deliver single-page web dashboard",
    description="Serves the high-contrast, accessible HTML5 dashboard interface."
)
def serve_home() -> FileResponse:
    """Delivers the primary single-page application dashboard.

    Returns:
        FileResponse: The compiled static index.html or fallback HTML response.
    """
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>AeroFamily Guardian Online</h1>")
