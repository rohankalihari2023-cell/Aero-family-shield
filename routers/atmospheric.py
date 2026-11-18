"""
atmospheric.py
Atmospheric monitoring, meteorological inversion observations, and GPS geolocation endpoints.
"""

from typing import Dict, Any

from fastapi import APIRouter

from core.exceptions import CityNotFoundError
from models.schemas import CurrentLocationSchema, CustomCitySchema
from services.smog_service import (
    CITIES_REGISTRY,
    get_city_data,
    register_custom_city,
    process_current_location_weather,
)
from services.security import sanitize_string

router = APIRouter(tags=["Atmospheric Smog"])


@router.get(
    "/api/cities",
    summary="Catalog of winter smog hotspots",
    description="Returns verified baseline environmental records and 24-hr diurnal curves for monitored urban centers."
)
def list_cities() -> Dict[str, Any]:
    """Retrieves full catalog of registered metropolitan smog regions.

    Returns:
        Dict[str, Any]: Dictionary mapping city keys to detailed meteorological records.

    Examples:
        >>> cities = list_cities()
        >>> "delhi" in cities
        True
    """
    results: Dict[str, Any] = {}
    for cid in CITIES_REGISTRY:
        data = get_city_data(cid)
        if data:
            results[cid] = data
    return results


@router.get(
    "/api/city/{city_id}",
    summary="Retrieve single urban microclimate profile",
    description="Fetches real-time sensor observations, stagnation status, and 24-hour diurnal curve for a specific city."
)
def get_single_city(city_id: str) -> Dict[str, Any]:
    """Retrieves environmental metrics and diurnal curve for a specific city.

    Args:
        city_id (str): Unique city identifier key (e.g., 'delhi', 'lahore').

    Returns:
        Dict[str, Any]: Comprehensive city profile including PM2.5, AQI, and hourly curves.

    Raises:
        CityNotFoundError: If the requested city key is not present in the registry.

    Examples:
        >>> city = get_single_city("delhi")
        >>> city["name"]
        'Delhi NCR'
    """
    clean_id = sanitize_string(city_id, max_len=50)
    data = get_city_data(clean_id)
    if not data:
        raise CityNotFoundError(clean_id)
    return data


@router.post(
    "/api/location/current",
    summary="Sync user GPS coordinates and microclimate sensor data",
    description="Ingests device telemetry, performs elevation/temperature lapse rate modeling, and creates a localized microclimate."
)
def set_current_location(payload: CurrentLocationSchema) -> Dict[str, Any]:
    """Processes real-time user GPS coordinates and live atmospheric sensor readings.

    Args:
        payload (CurrentLocationSchema): Validated geographic coordinates and weather observations.

    Returns:
        Dict[str, Any]: Synthesized city record stored under the 'current_location' key.
    """
    clean_name = sanitize_string(payload.name, max_len=120) if payload.name else None
    return process_current_location_weather(
        lat=payload.lat,
        lon=payload.lon,
        location_name=clean_name,
        live_pm25=payload.pm25,
        live_temperature=payload.temperature,
        live_humidity=payload.humidity,
        live_wind_speed=payload.windSpeed,
    )


@router.post(
    "/api/custom-city",
    summary="Register custom geographic microclimate",
    description="Allows citizen scientists to register unmonitored neighborhoods or rural microclimates into the active session."
)
def add_custom_city(payload: CustomCitySchema) -> Dict[str, Any]:
    """Registers a user-defined atmospheric microclimate into the session registry.

    Args:
        payload (CustomCitySchema): Microclimate definition parameters including particulate and meteorological values.

    Returns:
        Dict[str, Any]: Newly created city record with synthesized 24-hour diurnal inversion curve.
    """
    clean_name = sanitize_string(payload.name, max_len=80)
    clean_country = sanitize_string(payload.country, max_len=80)
    return register_custom_city(
        name=clean_name,
        pm25=payload.pm25,
        aqi=payload.aqi,
        temperature=payload.temperature,
        country=clean_country,
        humidity=payload.humidity,
        wind_speed=payload.windSpeed,
    )
