"""
enums.py
Domain enumeration types enforcing strict category constraints across AeroFamily.
Replaces error-prone magic strings with type-safe Python Enum definitions.
"""

from enum import Enum


class MaskType(str, Enum):
    """Respiratory face protection grades and filter classifications."""
    NONE = "none"
    CLOTH = "cloth"
    SURGICAL = "surgical"
    N95 = "n95"


class CommuteMode(str, Enum):
    """Urban daily transit modes and associated vehicular tailpipe exposure levels."""
    METRO = "metro"
    CARPOOL = "carpool"
    SOLO_CAR = "solo_car"
    CYCLING = "cycling"


class HomeSealing(str, Enum):
    """Building envelope weatherization and outdoor particulate infiltration resistance."""
    SEALED = "sealed"
    AVERAGE = "average"
    LEAKY = "leaky"


class CookingFuel(str, Enum):
    """Kitchen cooking combustion fuel types and indoor particulate emission sources."""
    GAS_UNVENTED = "gas_unvented"
    GAS_VENTED = "gas_vented"
    INDUCTION_VENTED = "induction_vented"
    GAS = "gas"
    INDUCTION = "induction"
    ELECTRIC = "electric"


class HousingType(str, Enum):
    """Residential building structural envelope classifications."""
    APARTMENT = "apartment"
    INDEPENDENT_HOUSE = "independent_house"
    VILLA = "villa"


class HumidifierWaterType(str, Enum):
    """Water feed sources evaluated for ultrasonic mineral aerosolization risk."""
    TAP = "tap"
    HARD_WATER = "hard_water"
    DISTILLED = "distilled"
    RO = "ro"
    EVAPORATIVE = "evaporative"


class AirQualityCategory(str, Enum):
    """WHO and EPA categorized atmospheric air quality hazard tiers."""
    GOOD = "good"
    MODERATE = "moderate"
    SENSITIVE = "sensitive"
    UNHEALTHY = "unhealthy"
    VERY_UNHEALTHY = "very-unhealthy"
    HAZARDOUS = "hazardous"


class IncidentSeverity(str, Enum):
    """Community incident urgency and rapid-response escalation levels."""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    SEVERE = "Severe"
