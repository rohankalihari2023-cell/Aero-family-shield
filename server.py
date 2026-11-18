"""
server.py
AeroFamily - Smog & Clean Air AI Guardian
Main web application server with REST endpoints, static asset delivery,
security headers, and real-time current location weather & air quality integration.
"""

import os
import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.smog_service import (
    CITIES_REGISTRY,
    get_city_data,
    register_custom_city,
    process_current_location_weather
)
from services.ai_engine import generate_ai_response
from services.routine_service import generate_daily_routine
from services.iaq_service import calculate_cadr_requirements, evaluate_humidifier_safety
from services.impact_service import simulate_lifestyle_impact
from services.security import (
    SECURITY_HEADERS,
    sanitize_string,
    validate_numeric_bounds,
    sanitize_profile_dict
)

app = FastAPI(
    title="AeroFamily - Smog & Clean Air AI Guardian",
    description="GenAI-powered family & community assistant for navigating severe winter smog.",
    version="1.1.0"
)

# CORS Middleware with restricted allowed methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Security Headers Middleware
@app.middleware("http")
async def apply_security_headers(request: Request, call_next):
    response = await call_next(request)
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

# Pydantic Schemas with strict validation
class FamilyProfileSchema(BaseModel):
    infants: int = Field(default=0, ge=0, le=10)
    asthmatics: int = Field(default=0, ge=0, le=10)
    seniors: int = Field(default=0, ge=0, le=10)
    pets: int = Field(default=0, ge=0, le=15)
    healthyAdults: int = Field(default=2, ge=1, le=20)
    housingType: str = Field(default="apartment", max_length=50)
    cookingFuel: str = Field(default="gas", max_length=50)
    commuteMode: str = Field(default="car", max_length=50)

class ChatRequestSchema(BaseModel):
    message: str = Field(..., min_length=1, max_length=3000)
    cityKey: str = Field(default="delhi", max_length=50)
    familyProfile: Optional[FamilyProfileSchema] = None
    apiKey: Optional[str] = Field(default=None, max_length=150)

class RoutineRequestSchema(BaseModel):
    cityKey: str = Field(default="delhi", max_length=50)
    familyProfile: FamilyProfileSchema

class CADRRequestSchema(BaseModel):
    roomLengthFt: float = Field(default=18.0, ge=2.0, le=150.0)
    roomWidthFt: float = Field(default=15.0, ge=2.0, le=150.0)
    ceilingHeightFt: float = Field(default=9.0, ge=5.0, le=30.0)
    desiredACH: float = Field(default=5.0, ge=1.0, le=12.0)

class ImpactSimRequestSchema(BaseModel):
    cityKey: str = Field(default="delhi", max_length=50)
    commuteChoice: str = Field(default="metro", max_length=50)
    maskChoice: str = Field(default="n95", max_length=50)
    airPurifierHours: float = Field(default=16.0, ge=0.0, le=24.0)
    homeSealing: str = Field(default="sealed", max_length=50)
    cookingMode: str = Field(default="induction_vented", max_length=50)
    householdSize: int = Field(default=3, ge=1, le=25)

class IncidentReportSchema(BaseModel):
    cityKey: str = Field(default="delhi", max_length=50)
    location: str = Field(..., min_length=2, max_length=200)
    incidentType: str = Field(..., min_length=2, max_length=100)
    details: str = Field(default="", max_length=1000)

class CurrentLocationSchema(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lon: float = Field(..., ge=-180.0, le=180.0)
    name: Optional[str] = Field(default=None, max_length=150)
    pm25: Optional[float] = Field(default=None, ge=0.0, le=2000.0)
    temperature: Optional[float] = Field(default=None, ge=-60.0, le=60.0)
    humidity: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    windSpeed: Optional[float] = Field(default=None, ge=0.0, le=200.0)

COMMUNITY_FEED: List[Dict[str, Any]] = [
    {
        "id": "rep-101",
        "location": "North Ring Sector 4",
        "city": "delhi",
        "type": "Municipal Leaf & Waste Burning",
        "timestamp": "25 mins ago",
        "severity": "High",
        "status": "Dispatched to Flying Squad",
        "reportedBy": "Citizen Watch #402"
    },
    {
        "id": "rep-102",
        "location": "Industrial Bypass Crossroad",
        "city": "lahore",
        "type": "Heavy Diesel Truck Idling & Black Smoke",
        "timestamp": "1 hour ago",
        "severity": "Severe",
        "status": "Traffic Police Alerted",
        "reportedBy": "AeroPod Member #18"
    },
    {
        "id": "rep-103",
        "location": "South Hills Construction Pit",
        "city": "saltlake",
        "type": "Uncovered Dry Earthworks (Dust Plume)",
        "timestamp": "3 hours ago",
        "severity": "Moderate",
        "status": "Water Sprinkler Requested",
        "reportedBy": "EcoNeighbor #91"
    }
]

# API Endpoints
@app.get("/api/status")
def get_system_status():
    """System health check and diagnostic endpoint."""
    return {
        "status": "online",
        "app": "AeroFamily Smog & Clean Air AI Guardian",
        "version": "1.1.0",
        "features": ["Geolocation-Weather-API", "WCAG-2.1-AAA", "WHO-2021-AQG", "Berkeley-Earth-Model"],
        "timestamp": time.time()
    }

@app.get("/api/cities")
def list_cities():
    """Returns database of monitored smog hotspots with diurnal curves."""
    results = {}
    for cid in CITIES_REGISTRY:
        data = get_city_data(cid)
        if data:
            results[cid] = data
    return results

@app.get("/api/city/{city_id}")
def get_single_city(city_id: str):
    """Returns detailed real-time air quality & inversion data for a single city."""
    clean_id = sanitize_string(city_id, 50)
    data = get_city_data(clean_id)
    if not data:
        raise HTTPException(status_code=404, detail="City not registered in knowledge base")
    return data

@app.post("/api/location/current")
def set_current_location(payload: CurrentLocationSchema):
    """
    Receives current GPS coordinates and live weather/air sensor readings
    and registers the user's live current location.
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

@app.post("/api/custom-city")
def add_custom_city(payload: Dict[str, Any]):
    """Registers a user-defined localized microclimate."""
    name = sanitize_string(payload.get("name", "Custom Region"), 80)
    pm25 = validate_numeric_bounds(payload.get("pm25", 150), 1.0, 1000.0, 150.0)
    aqi_raw = payload.get("aqi")
    aqi = int(validate_numeric_bounds(aqi_raw, 1.0, 1500.0, pm25 * 1.25)) if aqi_raw else None
    temp = validate_numeric_bounds(payload.get("temperature", 10), -50.0, 60.0, 10.0)
    return register_custom_city(name=name, pm25=pm25, aqi=aqi, temperature=temp)

@app.post("/api/advisor/chat")
def chat_with_advisor(req: ChatRequestSchema):
    """GenAI conversational guidance tailored to family vulnerabilities and city conditions."""
    city_data = get_city_data(req.cityKey) or get_city_data("delhi")
    prof_dict = req.familyProfile.dict() if req.familyProfile else None
    clean_message = sanitize_string(req.message, 3000)
    
    return generate_ai_response(
        message=clean_message,
        city=city_data,
        profile=prof_dict,
        api_key=req.apiKey
    )

@app.post("/api/routine/generate")
def create_routine(req: RoutineRequestSchema):
    """Synthesizes a 24-hr low-emission schedule and calculates personal & community impact."""
    city_data = get_city_data(req.cityKey) or get_city_data("delhi")
    prof_dict = sanitize_profile_dict(req.familyProfile.dict())
    return generate_daily_routine(city=city_data, profile=prof_dict)

@app.post("/api/iaq/cadr-calculator")
def compute_cadr(req: CADRRequestSchema):
    """Computes room volume, required CADR, and DIY Corsi-Rosenthal unit specifications."""
    return calculate_cadr_requirements(
        length_ft=req.roomLengthFt,
        width_ft=req.roomWidthFt,
        height_ft=req.ceilingHeightFt,
        desired_ach=req.desiredACH
    )

@app.post("/api/iaq/humidifier-check")
def check_humidifier(water_type: str):
    """Analyzes ultrasonic tap water mineral aerosol hazard."""
    clean_type = sanitize_string(water_type, 30)
    return evaluate_humidifier_safety(clean_type)

@app.post("/api/impact/simulate")
def calculate_lifestyle_impact(req: ImpactSimRequestSchema):
    """Simulates real-time respiratory protection and CO2e savings from lifestyle choices."""
    city_data = get_city_data(req.cityKey) or get_city_data("delhi")
    return simulate_lifestyle_impact(
        outdoor_pm25=city_data["pm25"],
        commute_mode=req.commuteChoice,
        mask_type=req.maskChoice,
        purifier_hours=req.airPurifierHours,
        home_sealing=req.homeSealing,
        cooking_mode=req.cookingMode,
        household_size=req.householdSize
    )

@app.get("/api/community/reports")
def get_community_feed():
    """Returns real-time list of community smoke and pollution incident reports."""
    return COMMUNITY_FEED

@app.post("/api/community/report-smoke")
def submit_incident_report(report: IncidentReportSchema):
    """Logs open burning or dust plume violation and alerts rapid response dispatch."""
    new_ticket = {
        "id": f"rep-{int(time.time())}",
        "location": sanitize_string(report.location, 200),
        "city": sanitize_string(report.cityKey, 50),
        "type": sanitize_string(report.incidentType, 100),
        "timestamp": "Just now",
        "severity": "High",
        "status": "Logged & Queued to Local Control Room",
        "details": sanitize_string(report.details, 1000),
        "reportedBy": "AeroFamily Citizen Guardian"
    }
    COMMUNITY_FEED.insert(0, new_ticket)
    return {
        "success": True,
        "ticketId": new_ticket["id"],
        "message": "Incident logged and broadcasted to local Clean Air Action Squad.",
        "report": new_ticket
    }

# Static file mount
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_home():
    """Serves the main application page."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>AeroFamily Guardian Online</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
