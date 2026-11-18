"""
server.py
AeroFamily - Smog & Clean Air AI Guardian
Main FastAPI REST application server providing enterprise-grade endpoints for atmospheric monitoring,
GenAI clinical copilot advisory, 24-hour routine synthesis, IAQ engineering calculations,
and citizen community incident coordination.

Architectural Pattern:
    - Application Factory (`create_app`)
    - Decoupled Domain APIRouters (`routers/`)
    - Global Domain Exception Translation (`core.exceptions`)
    - OWASP Hardened Security Middleware & CSP (`core.config`)
"""

import os
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings, SECURITY_HEADERS, get_logger
from core.exceptions import AeroFamilyError
from routers import (
    system_router,
    atmospheric_router,
    advisor_router,
    routine_router,
    iaq_router,
    impact_router,
    community_router,
)
import routers.system as system
import routers.atmospheric as atmospheric
import routers.advisor as advisor
import routers.routine as routine
import routers.iaq as iaq
import routers.impact as impact
import routers.community as community

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """FastAPI Application Factory constructing a hardened, modular REST application instance.

    Configures:
        - OpenAPI / Swagger documentation schema
        - Cross-Origin Resource Sharing (CORS) policy
        - OWASP defense-in-depth security response headers
        - Global domain exception handlers
        - Domain-driven APIRouters
        - Static frontend dashboard delivery

    Returns:
        FastAPI: Fully initialized and configured web service application.
    """
    application = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
            {"name": "System", "description": "System health, diagnostics, and static web app delivery."},
            {"name": "Atmospheric Smog", "description": "Meteorological observation, diurnal inversion curves, and GPS sync."},
            {"name": "AI Advisor", "description": "GenAI contextual clinical and environmental advice."},
            {"name": "Routine Planner", "description": "24-hour diurnal low-emission schedule generator."},
            {"name": "IAQ Engineering", "description": "CADR, ACH, and Corsi-Rosenthal Box specifications."},
            {"name": "Lifestyle Impact", "description": "Inhalation dosage and Berkeley Earth cigarette equivalence math."},
            {"name": "Community Hub", "description": "Citizen pollution spotters and neighborhood incident reports."},
        ]
    )

    # CORS Middleware with restricted origins and methods
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )

    # Security Response Headers Middleware
    @application.middleware("http")
    async def apply_security_headers(request: Request, call_next):
        """Enforces OWASP security headers on all HTTP responses."""
        response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        return response

    # Global Domain Exception Handlers
    @application.exception_handler(AeroFamilyError)
    async def aerofamily_exception_handler(request: Request, exc: AeroFamilyError):
        """Translates typed domain errors into structured JSON responses."""
        logger.warning("Domain exception at %s: %s", request.url.path, exc.message)
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @application.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Catches unhandled server errors safely without leaking internal stack traces."""
        logger.error("Unhandled error at %s: %s", request.url.path, str(exc), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "status_code": 500,
                "message": "Internal server error. Our engineering team has been alerted.",
            }
        )

    # Mount Domain Routers
    application.include_router(system_router)
    application.include_router(atmospheric_router)
    application.include_router(advisor_router)
    application.include_router(routine_router)
    application.include_router(iaq_router)
    application.include_router(impact_router)
    application.include_router(community_router)

    # Static Web Application Delivery
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        application.mount("/static", StaticFiles(directory=static_dir), name="static")

    return application


# Global application instance for ASGI servers (uvicorn, gunicorn)
app = create_app()

# Functional exports for direct functional testing and decoupled controller execution
get_system_status = system.get_system_status
serve_home = system.serve_home
list_cities = atmospheric.list_cities
get_single_city = atmospheric.get_single_city
set_current_location = atmospheric.set_current_location
add_custom_city = atmospheric.add_custom_city
chat_with_advisor = advisor.chat_with_advisor
create_routine = routine.create_routine
compute_cadr = iaq.compute_cadr
check_humidifier = iaq.check_humidifier
calculate_lifestyle_impact = impact.calculate_lifestyle_impact
fetch_community_reports = community.fetch_community_reports
submit_incident_report = community.submit_incident_report

__all__ = [
    "app",
    "create_app",
    "get_system_status",
    "serve_home",
    "list_cities",
    "get_single_city",
    "set_current_location",
    "add_custom_city",
    "chat_with_advisor",
    "create_routine",
    "compute_cadr",
    "check_humidifier",
    "calculate_lifestyle_impact",
    "fetch_community_reports",
    "submit_incident_report",
]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
