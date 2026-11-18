"""
schemas.py
Pydantic validation schemas with typed field constraints, schema descriptions,
and OpenAPI documentation metadata for all AeroFamily endpoints.
"""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field
from models.enums import (
    MaskType,
    CommuteMode,
    HomeSealing,
    CookingFuel,
    HousingType,
    HumidifierWaterType,
    IncidentSeverity,
)


class FamilyProfileSchema(BaseModel):
    """Household vulnerability profile capturing respiratory risk factors."""

    infants: int = Field(
        default=0,
        ge=0,
        le=10,
        description="Number of infants/toddlers (0-4 yrs) with vulnerable alveolar development.",
        examples=[1]
    )
    asthmatics: int = Field(
        default=0,
        ge=0,
        le=10,
        description="Number of household members diagnosed with asthma, COPD, or hyper-reactive airways.",
        examples=[1]
    )
    seniors: int = Field(
        default=0,
        ge=0,
        le=10,
        description="Number of elderly family members (65+ yrs) susceptible to cardiovascular smog stress.",
        examples=[0]
    )
    pets: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Number of household domestic pets exposed to ground-level particulate stagnation.",
        examples=[1]
    )
    healthyAdults: int = Field(
        default=2,
        ge=1,
        le=20,
        description="Number of healthy adults in the household.",
        examples=[2]
    )
    housingType: str = Field(
        default=HousingType.APARTMENT.value,
        max_length=50,
        description="Building envelope type: 'apartment', 'independent_house', or 'villa'.",
        examples=["apartment"]
    )
    cookingFuel: str = Field(
        default=CookingFuel.GAS.value,
        max_length=50,
        description="Primary kitchen fuel: 'gas', 'induction', or 'electric'.",
        examples=["gas"]
    )
    commuteMode: str = Field(
        default="car",
        max_length=50,
        description="Typical daily transit choice: 'metro', 'carpool', 'solo_car', 'bus', or 'cycling'.",
        examples=["car"]
    )

    def to_dict(self) -> Dict[str, Any]:
        """Provides unified dictionary serialization across Pydantic v1 & v2."""
        if hasattr(self, "model_dump"):
            return self.model_dump()
        return self.dict()


class ChatRequestSchema(BaseModel):
    """Request payload for multi-turn GenAI advisor conversations."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=3000,
        description="User question or inquiry regarding smog, symptoms, or protective protocols.",
        examples=["Can my toddler play in the park this afternoon?"]
    )
    cityKey: str = Field(
        default="delhi",
        max_length=50,
        description="Monitored hotspot identifier or 'current_location'.",
        examples=["delhi"]
    )
    familyProfile: Optional[FamilyProfileSchema] = Field(
        default=None,
        description="Optional active household vulnerability configuration."
    )
    apiKey: Optional[str] = Field(
        default=None,
        max_length=150,
        description="Optional user-supplied Google Gemini API key."
    )


class RoutineRequestSchema(BaseModel):
    """Request payload for synthesizing a low-emission 24-hour diurnal schedule."""

    cityKey: str = Field(
        default="delhi",
        max_length=50,
        description="Active city or microclimate identifier.",
        examples=["delhi"]
    )
    familyProfile: FamilyProfileSchema = Field(
        ...,
        description="Target family profile for which to customize daily intervals."
    )


class CADRRequestSchema(BaseModel):
    """Room parameters for Clean Air Delivery Rate (CADR) & ACH engineering calculation."""

    roomLengthFt: float = Field(
        default=18.0,
        ge=2.0,
        le=150.0,
        description="Room length in feet.",
        examples=[18.0]
    )
    roomWidthFt: float = Field(
        default=15.0,
        ge=2.0,
        le=150.0,
        description="Room width in feet.",
        examples=[15.0]
    )
    ceilingHeightFt: float = Field(
        default=9.0,
        ge=5.0,
        le=30.0,
        description="Ceiling height in feet.",
        examples=[9.0]
    )
    desiredACH: float = Field(
        default=5.0,
        ge=1.0,
        le=12.0,
        description="Target Air Changes per Hour (e.g. 2=Standard, 5=Asthma/Smog defense, 8=Clinical).",
        examples=[5.0]
    )


class ImpactSimRequestSchema(BaseModel):
    """Lifestyle choices input for real-time respiratory exposure and CO2 simulation."""

    cityKey: str = Field(default="delhi", max_length=50)
    commuteChoice: str = Field(
        default=CommuteMode.METRO.value,
        max_length=50,
        description="'metro', 'carpool', 'solo_car', or 'cycling'."
    )
    maskChoice: str = Field(
        default=MaskType.N95.value,
        max_length=50,
        description="'none', 'cloth', 'surgical', or 'n95'."
    )
    airPurifierHours: float = Field(
        default=16.0,
        ge=0.0,
        le=24.0,
        description="Daily hours air purifier is active inside the residence."
    )
    homeSealing: str = Field(
        default=HomeSealing.SEALED.value,
        max_length=50,
        description="'sealed', 'average', or 'leaky'."
    )
    cookingMode: str = Field(
        default=CookingFuel.INDUCTION_VENTED.value,
        max_length=50,
        description="'gas_unvented', 'gas_vented', or 'induction_vented'."
    )
    householdSize: int = Field(
        default=3,
        ge=1,
        le=25,
        description="Number of persons residing in the household."
    )


class CurrentLocationSchema(BaseModel):
    """Live GPS coordinates and meteorological readings captured from client device."""

    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees.")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees.")
    name: Optional[str] = Field(default=None, max_length=150, description="Reverse-geocoded locality name.")
    pm25: Optional[float] = Field(default=None, ge=0.0, le=2000.0, description="Observed PM2.5 in µg/m³.")
    temperature: Optional[float] = Field(default=None, ge=-60.0, le=60.0, description="Observed temperature in °C.")
    humidity: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Observed relative humidity in %.")
    windSpeed: Optional[float] = Field(default=None, ge=0.0, le=200.0, description="Wind speed in km/h.")


class CustomCitySchema(BaseModel):
    """User-defined localized microclimate parameters."""

    name: str = Field(..., min_length=2, max_length=100, description="Microclimate or neighborhood name.")
    pm25: float = Field(default=120.0, ge=1.0, le=1500.0, description="Baseline PM2.5 concentration.")
    aqi: Optional[int] = Field(default=None, ge=1, le=2000, description="Air Quality Index (optional).")
    temperature: float = Field(default=12.0, ge=-50.0, le=60.0, description="Local temperature in °C.")
    country: str = Field(default="Custom Region", max_length=80)
    humidity: float = Field(default=65.0, ge=0.0, le=100.0)
    windSpeed: float = Field(default=4.0, ge=0.0, le=200.0)


class IncidentReportSchema(BaseModel):
    """Citizen smoke or open burning spotter report."""

    cityKey: str = Field(default="delhi", max_length=50)
    location: str = Field(..., min_length=2, max_length=200, description="Physical street or intersection.")
    incidentType: str = Field(..., min_length=2, max_length=100, description="Type of pollution event.")
    details: str = Field(default="", max_length=1000, description="Additional context or observations.")


class StatusResponseSchema(BaseModel):
    """System health check diagnostic response."""

    status: str
    app: str
    version: str
    features: List[str]
    timestamp: float


class IncidentResponseSchema(BaseModel):
    """Confirmation payload returned after submitting an incident report."""

    success: bool
    ticketId: str
    message: str
    report: Dict[str, Any]
