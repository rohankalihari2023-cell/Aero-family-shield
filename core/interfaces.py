"""
interfaces.py
Abstract base protocols defining service contracts across AeroFamily.
Implements the Dependency Inversion Principle (DIP) and Interface Segregation (ISP)
to enable decoupled testing, swappable AI backends, and modular extensibility.
"""

from typing import Protocol, Dict, Any, List, Optional
from models.enums import HumidifierWaterType, MaskType, CommuteMode, HomeSealing


class IAIEngineService(Protocol):
    """Contract for conversational GenAI and clinical environmental reasoning engines."""

    def generate_ai_response(
        self,
        message: str,
        city: Dict[str, Any],
        profile: Optional[Dict[str, Any]],
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synthesizes clinical and atmospheric advice tailored to user context."""
        ...


class ISmogService(Protocol):
    """Contract for atmospheric temperature inversion and particulate modeling."""

    def get_city_data(self, city_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves verified environmental metrics for a registered city."""
        ...

    def calculate_diurnal_curve(self, base_pm25: float) -> List[Dict[str, Any]]:
        """Calculates 24-hour diurnal particulate inversion curve."""
        ...

    def process_current_location_weather(
        self,
        lat: float,
        lon: float,
        location_name: Optional[str] = None,
        live_pm25: Optional[float] = None,
        live_temperature: Optional[float] = None,
        live_humidity: Optional[float] = None,
        live_wind_speed: Optional[float] = None
    ) -> Dict[str, Any]:
        """Ingests live GPS observations and computes localized stagnation indices."""
        ...


class IIAQService(Protocol):
    """Contract for Indoor Air Quality engineering calculations."""

    def calculate_cadr_requirements(
        self,
        length_ft: float,
        width_ft: float,
        height_ft: float,
        desired_ach: float
    ) -> Dict[str, Any]:
        """Computes CADR requirements and Corsi-Rosenthal unit specifications."""
        ...

    def evaluate_humidifier_safety(self, water_type: str) -> Dict[str, Any]:
        """Evaluates mineral aerosolization hazard for humidifier water feeds."""
        ...


class IImpactService(Protocol):
    """Contract for personal exposure and community carbon emissions modeling."""

    def simulate_lifestyle_impact(
        self,
        outdoor_pm25: float,
        commute_mode: str,
        mask_type: str,
        purifier_hours: float,
        home_sealing: str,
        cooking_mode: str,
        household_size: int
    ) -> Dict[str, Any]:
        """Simulates lung particulate deposition and avoided cigarette equivalencies."""
        ...


class IRoutineService(Protocol):
    """Contract for 24-hour low-emission schedule synthesis."""

    def generate_daily_routine(
        self,
        city: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesizes daily schedule shifting outdoor activities to convective windows."""
        ...
