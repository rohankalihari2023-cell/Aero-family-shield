"""
server.py
AeroFamily - Smog & Clean Air AI Guardian
Main FastAPI REST application server providing endpoints for atmospheric monitoring,
GenAI clinical copilot advisory, 24-hour routine synthesis, IAQ engineering calculations,
and citizen community incident coordination.
"""

import os
import time
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings, SECURITY_HEADERS, get_logger
from core.exceptions import AeroFamilyError, CityNotFoundError
from models.schemas import (
    FamilyProfileSchema,
    ChatRequestSchema,
    RoutineRequestSchema,
    CADRRequestSchema,
    ImpactSimRequestSchema,
    CurrentLocationSchema,
    CustomCitySchema,
    IncidentReportSchema,
    StatusResponseSchema,
    IncidentResponseSchema,
)
from services.smog_service import (
    CITIES_REGISTRY,
    get_city_data,
    register_custom_city,
    process_current_location_weather,
)
from services.ai_engine import generate_ai_response
from services.routine_service import generate_daily_routine
from services.iaq_service import calculate_cadr_requirements, evaluate_humidifier_safety
from services.impact_service import simulate_lifestyle_impact
from services.security import (
    sanitize_string,
    validate_numeric_bounds,
    sanitize_profile_dict,
)
from services.community_service import get_community_feed, create_incident_report

logger = get_logger(__name__)

# FastAPI Application Factory with comprehensive OpenAPI metadata
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "System", "description": "System health and diagnostic endpoints."},
        {"name": "Atmospheric Smog", "description": "Meteorological observation, diurnal curves, and GPS sync."},
        {"name": "AI Guardian", "description": "GenAI contextual clinical and environmental advice."},
        {"name": "Routine Planner", "description": "24-hour diurnal low-emission schedule generator."},
        {"name": "IAQ Engineering", "description": "CADR, ACH, and Corsi-Rosenthal Box specifications."},
        {"name": "Lifestyle Impact", "description": "Inhalation dosage and Berkeley Earth cigarette equivalence math."},
        {"name": "Community Hub", "description": "Citizen pollution spotters and neighborhood incident reports."},
    ]
)

# CORS Middleware with restricted origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)


# Security Response Headers Middleware
@app.middleware("http")
async def apply_security_headers(request: Request, call_next):
    """Enforces OWASP security headers on all HTTP responses."""
    response = await call_next(request)
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response


# Global Domain Exception Handlers
@app.exception_handler(AeroFamilyError)
async def aerofamily_exception_handler(request: Request, exc: AeroFamilyError):
    """Translates typed domain errors into structured JSON responses."""
    logger.warning("Domain exception at %s: %s", request.url.path, exc.message)
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


@app.exception_handler(Exception)
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


# ----------------------------------------------------------------------
# 1. System & Diagnostic Endpoints
# ----------------------------------------------------------------------
@app.get("/api/status", response_model=StatusResponseSchema, tags=["System"])
def get_system_status() -> Dict[str, Any]:
    """Returns application diagnostic health, version, and active capability flags."""
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
            "Corsi-Rosenthal-CADR"
        ],
        "timestamp": time.time()
    }


# ----------------------------------------------------------------------
# 2. Atmospheric Smog & Location Endpoints
# ----------------------------------------------------------------------
@app.get("/api/cities", tags=["Atmospheric Smog"])
def list_cities() -> Dict[str, Any]:
    """Returns catalog of all registered winter smog hotspots with diurnal curves."""
    results: Dict[str, Any] = {}
    for cid in CITIES_REGISTRY:
        data = get_city_data(cid)
        if data:
            results[cid] = data
    return results


@app.get("/api/city/{city_id}", tags=["Atmospheric Smog"])
def get_single_city(city_id: str) -> Dict[str, Any]:
    """Retrieves full environmental data and 24-hr diurnal curve for a single city.

    Args:
        city_id (str): Identifier key of the city.

    Raises:
        CityNotFoundError: If city is not registered in the database.
    """
    clean_id = sanitize_string(city_id, 50)
    data = get_city_data(clean_id)
    if not data:
        raise CityNotFoundError(clean_id)
    return data


@app.post("/api/location/current", tags=["Atmospheric Smog"])
def set_current_location(payload: CurrentLocationSchema) -> Dict[str, Any]:
    """Ingests client device GPS coordinates, weather readings, and computes localized inversion metrics.

    Args:
        payload (CurrentLocationSchema): User coordinates and observed weather parameters.

    Returns:
        Dict[str, Any]: Synthesized city record stored under 'current_location'.
    """
    clean_name = sanitize_string(payload.name, 120) if payload.name else None
    return process_current_location_weather(
        lat=payload.lat,
        lon=payload.lon,
        location_name=clean_name,
        live_pm25=payload.pm25,
        live_temperature=payload.temperature,
        live_humidity=payload.humidity,
        live_wind_speed=payload.windSpeed
    )


@app.post("/api/custom-city", tags=["Atmospheric Smog"])
def add_custom_city(payload: CustomCitySchema) -> Dict[str, Any]:
    """Registers a user-defined localized microclimate into the session registry.

    Args:
        payload (CustomCitySchema): Microclimate definition parameters.

    Returns:
        Dict[str, Any]: The registered microclimate record with diurnal curve.
    """
    clean_name = sanitize_string(payload.name, 80)
    clean_country = sanitize_string(payload.country, 80)
    return register_custom_city(
        name=clean_name,
        pm25=payload.pm25,
        aqi=payload.aqi,
        temperature=payload.temperature,
        country=clean_country,
        humidity=payload.humidity,
        wind_speed=payload.windSpeed
    )


# ----------------------------------------------------------------------
# 3. AI Guardian Advisor Endpoints
# ----------------------------------------------------------------------
@app.post("/api/advisor/chat", tags=["AI Advisor"])
def chat_with_advisor(req: ChatRequestSchema) -> Dict[str, Any]:
    """Generates conversational guidance grounded in real-time smog conditions and family vulnerabilities.

    Args:
        req (ChatRequestSchema): User query, city key, optional family profile, and optional API key.

    Returns:
        Dict[str, Any]: Clinical advice markdown with source attribution.
    """
    city_data = get_city_data(req.cityKey) or get_city_data("delhi") or {}
    prof_dict = req.familyProfile.to_dict() if req.familyProfile else None
    clean_message = sanitize_string(req.message, 3000)

    return generate_ai_response(
        message=clean_message,
        city=city_data,
        profile=prof_dict,
        api_key=req.apiKey
    )


# ----------------------------------------------------------------------
# 4. 24-Hour Daily Routine Planner Endpoints
# ----------------------------------------------------------------------
@app.post("/api/routine/generate", tags=["Routine Planner"])
def create_routine(req: RoutineRequestSchema) -> Dict[str, Any]:
    """Synthesizes a 24-hour diurnal low-emission schedule and calculates personal impact.

    Args:
        req (RoutineRequestSchema): Target city and household profile.

    Returns:
        Dict[str, Any]: Daily schedule with exposure reductions and cigarette equivalents avoided.
    """
    city_data = get_city_data(req.cityKey) or get_city_data("delhi") or {}
    prof_dict = sanitize_profile_dict(req.familyProfile.to_dict())
    return generate_daily_routine(city=city_data, profile=prof_dict)


# ----------------------------------------------------------------------
# 5. Indoor Air Quality (IAQ) Lab Endpoints
# ----------------------------------------------------------------------
@app.post("/api/iaq/cadr-calculator", tags=["IAQ Engineering"])
def compute_cadr(req: CADRRequestSchema) -> Dict[str, Any]:
    """Computes room volume, required CADR in CFM, and Corsi-Rosenthal unit specifications.

    Args:
        req (CADRRequestSchema): Room dimensions and desired air changes per hour (ACH).

    Returns:
        Dict[str, Any]: Recommended units, fan speed, filter replacement cycles, and money saved in ₹.
    """
    return calculate_cadr_requirements(
        length_ft=req.roomLengthFt,
        width_ft=req.roomWidthFt,
        height_ft=req.ceilingHeightFt,
        desired_ach=req.desiredACH
    )


@app.post("/api/iaq/humidifier-check", tags=["IAQ Engineering"])
def check_humidifier(water_type: str) -> Dict[str, Any]:
    """Analyzes ultrasonic humidifier mineral aerosol hazard based on water supply type.

    Args:
        water_type (str): Type of water utilized ('tap', 'distilled', 'ro', 'evaporative').

    Returns:
        Dict[str, Any]: Particulate emission risk and safety recommendations.
    """
    clean_type = sanitize_string(water_type, 30)
    return evaluate_humidifier_safety(clean_type)


# ----------------------------------------------------------------------
# 6. Lifestyle Impact Simulator Endpoints
# ----------------------------------------------------------------------
@app.post("/api/impact/simulate", tags=["Lifestyle Impact"])
def calculate_lifestyle_impact(req: ImpactSimRequestSchema) -> Dict[str, Any]:
    """Simulates real-time respiratory protection and CO2e savings from lifestyle choices.

    Args:
        req (ImpactSimRequestSchema): Commute, mask, purifier runtime, and home sealing choices.

    Returns:
        Dict[str, Any]: Inhaled microgram dosage, reduction percentage, and carbon spared.
    """
    city_data = get_city_data(req.cityKey) or get_city_data("delhi") or {"pm25": 100.0}
    return simulate_lifestyle_impact(
        outdoor_pm25=city_data.get("pm25", 100.0),
        commute_mode=req.commuteChoice,
        mask_type=req.maskChoice,
        purifier_hours=req.airPurifierHours,
        home_sealing=req.homeSealing,
        cooking_mode=req.cookingMode,
        household_size=req.householdSize
    )


# ----------------------------------------------------------------------
# 7. Community Hub Endpoints
# ----------------------------------------------------------------------
@app.get("/api/community/reports", tags=["Community Hub"])
def fetch_community_reports() -> List[Dict[str, Any]]:
    """Returns active list of citizen pollution and open-burning incident reports."""
    return get_community_feed()


@app.post("/api/community/report-smoke", response_model=IncidentResponseSchema, tags=["Community Hub"])
def submit_incident_report(report: IncidentReportSchema) -> Dict[str, Any]:
    """Registers an open burning or toxic dust violation and alerts rapid response dispatch.

    Args:
        report (IncidentReportSchema): Citizen incident details.

    Returns:
        Dict[str, Any]: Incident confirmation ticket.
    """
    new_ticket = create_incident_report(
        location=report.location,
        city_key=report.cityKey,
        incident_type=report.incidentType,
        details=report.details
    )
    return {
        "success": True,
        "ticketId": new_ticket["id"],
        "message": "Incident logged and broadcasted to local Clean Air Action Squad.",
        "report": new_ticket
    }


# ----------------------------------------------------------------------
# 8. Static Web Application Delivery
# ----------------------------------------------------------------------
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=FileResponse, tags=["System"])
def serve_home():
    """Serves the main AeroFamily single-page dashboard."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>AeroFamily Guardian Online</h1>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
