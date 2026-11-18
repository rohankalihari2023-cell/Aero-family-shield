"""
smog_service.py
Module for atmospheric inversion modeling, winter smog diurnal curves,
pollutant data structures, WHO air quality guideline evaluation,
and real-time current location weather & air quality integration.
"""

from functools import lru_cache
from typing import Dict, Any, List, Optional
import math
import time

WHO_GUIDELINES = {
    "pm25_24h_annual": 5.0,    # WHO 2021 Annual Target (µg/m³)
    "pm25_24h_daily": 15.0,    # WHO 2021 24-hr Air Quality Guideline (µg/m³)
    "pm10_24h_daily": 45.0,    # WHO 2021 24-hr Guideline (µg/m³)
    "no2_24h_daily": 25.0,     # WHO 2021 24-hr Guideline (µg/m³)
    "berkeley_muller_factor": 22.0  # 22 µg/m³ of PM2.5 24h exposure ~ 1 cigarette
}

DIURNAL_INVERSION_MULTIPLIERS = {
    0: 1.15, 1: 1.20, 2: 1.25, 3: 1.30, 4: 1.35, 5: 1.40,
    6: 1.45, 7: 1.48, 8: 1.42, 9: 1.25, 10: 1.05, 11: 0.85,
    12: 0.70, 13: 0.65, 14: 0.68, 15: 0.75, 16: 0.90, 17: 1.10,
    18: 1.28, 19: 1.35, 20: 1.38, 21: 1.35, 22: 1.28, 23: 1.20
}

CITIES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "delhi": {
        "id": "delhi",
        "name": "Delhi NCR, India",
        "country": "India",
        "aqi": 418,
        "status": "Severe / Hazardous",
        "category": "hazardous",
        "pm25": 342.0,
        "pm10": 486.0,
        "no2": 74.0,
        "co": 2.8,
        "temperature": 15.0,
        "humidity": 68.0,
        "inversionStrength": "High (Surface Inversion 80m)",
        "windSpeed": "3.2 km/h (Stagnant Calm)",
        "ventilationWindow": "12:30 PM - 2:30 PM",
        "grapStage": "Stage IV (Severe+ Emergency)",
        "dominantSources": [
            "Vehicular exhaust",
            "Stubble burning smoke transport",
            "Road & construction dust",
            "Secondary inorganic aerosols in winter fog"
        ],
        "advisory": "Hazardous winter inversion trapping toxic micro-particulates at ground level. Avoid all unessential outdoor physical activities. Keep indoor HEPA systems running."
    },
    "lahore": {
        "id": "lahore",
        "name": "Lahore, Pakistan",
        "country": "Pakistan",
        "aqi": 435,
        "status": "Hazardous Crisis",
        "category": "hazardous",
        "pm25": 388.0,
        "pm10": 520.0,
        "no2": 82.0,
        "co": 3.1,
        "temperature": 14.0,
        "humidity": 72.0,
        "inversionStrength": "Extreme (Mixing Layer <70m)",
        "windSpeed": "2.8 km/h (Calm)",
        "ventilationWindow": "1:00 PM - 2:30 PM",
        "grapStage": "Green Lockdown / Smog Emergency",
        "dominantSources": [
            "Low-grade fuel combustion",
            "Brick kilns without zigzag technology",
            "Transboundary agricultural smoke",
            "Cold winter fog condensation"
        ],
        "advisory": "Dense winter smog blanket with zero nocturnal dispersal. Vulnerable individuals must strictly stay indoors with sealed windows."
    },
    "beijing": {
        "id": "beijing",
        "name": "Beijing, China",
        "country": "China",
        "aqi": 172,
        "status": "Unhealthy",
        "category": "unhealthy",
        "pm25": 98.0,
        "pm10": 165.0,
        "no2": 44.0,
        "co": 1.4,
        "temperature": 2.0,
        "humidity": 42.0,
        "inversionStrength": "Moderate (Valley Orographic Trapping)",
        "windSpeed": "6.5 km/h",
        "ventilationWindow": "11:30 AM - 3:00 PM",
        "grapStage": "Orange Air Alert",
        "dominantSources": [
            "Winter centralized heating plants",
            "Regional industrial haze from Hebei basin",
            "Automotive diesel corridors"
        ],
        "advisory": "Typical Northern China winter heating smog. Wear KN95/FFP2 outdoors and stagger commute hours away from morning stagnation."
    },
    "saltlake": {
        "id": "saltlake",
        "name": "Salt Lake City, UT, USA",
        "country": "United States",
        "aqi": 148,
        "status": "Unhealthy for Sensitive Groups",
        "category": "sensitive",
        "pm25": 56.0,
        "pm10": 84.0,
        "no2": 32.0,
        "co": 0.9,
        "temperature": -2.0,
        "humidity": 58.0,
        "inversionStrength": "Strong (Wasatch Basin Thermal Cap)",
        "windSpeed": "4.1 km/h",
        "ventilationWindow": "1:30 PM - 3:30 PM",
        "grapStage": "Mandatory No-Burn Action Day",
        "dominantSources": [
            "Great Basin winter temperature inversion",
            "Residential woodstoves and fireplaces",
            "Mobile emissions in trapped valley cold pool"
        ],
        "advisory": "Cold valley pool holding vehicle exhaust beneath warm mountain lid. Limit prolonged outdoor workouts and avoid all wood burning."
    },
    "ulaanbaatar": {
        "id": "ulaanbaatar",
        "name": "Ulaanbaatar, Mongolia",
        "country": "Mongolia",
        "aqi": 365,
        "status": "Hazardous Winter Peak",
        "category": "hazardous",
        "pm25": 315.0,
        "pm10": 440.0,
        "no2": 66.0,
        "co": 3.5,
        "temperature": -19.0,
        "humidity": 74.0,
        "inversionStrength": "Severe (Siberian High Anticyclone)",
        "windSpeed": "2.1 km/h",
        "ventilationWindow": "1:00 PM - 2:00 PM (Brief)",
        "grapStage": "Winter Emergency Plan",
        "dominantSources": [
            "Ger district raw coal & briquette stoves",
            "Low thermal insulation of housing",
            "Extreme cold-induced valley inversion"
        ],
        "advisory": "Extreme sub-zero inversion. Thick coal smoke hanging in Tuul River basin. Maximize internal air filtration and use thermal draft curtains."
    },
    "katowice": {
        "id": "katowice",
        "name": "Katowice / Silesia, Poland",
        "country": "Poland",
        "aqi": 168,
        "status": "Unhealthy",
        "category": "unhealthy",
        "pm25": 88.0,
        "pm10": 142.0,
        "no2": 38.0,
        "co": 1.2,
        "temperature": 1.0,
        "humidity": 82.0,
        "inversionStrength": "Moderate (Foggy Valley Stagnation)",
        "windSpeed": "5.0 km/h",
        "ventilationWindow": "12:00 PM - 2:30 PM",
        "grapStage": "Smog Alert Level 2",
        "dominantSources": [
            "Old residential coal/wood boilers ('Kopciuchy')",
            "Low-stack domestic emissions",
            "Cold damp atmospheric stagnation"
        ],
        "advisory": "Elevated benzo(a)pyrene and PM2.5 from domestic heating. Seal window leaks and switch from fireplace to electric/heat pump where possible."
    },
    "milan": {
        "id": "milan",
        "name": "Milan / Po Valley, Italy",
        "country": "Italy",
        "aqi": 154,
        "status": "Unhealthy",
        "category": "unhealthy",
        "pm25": 62.0,
        "pm10": 89.0,
        "no2": 48.0,
        "co": 1.1,
        "temperature": 5.0,
        "humidity": 79.0,
        "inversionStrength": "Persistent (Po Basin Topographic Trap)",
        "windSpeed": "3.0 km/h",
        "ventilationWindow": "1:00 PM - 3:30 PM",
        "grapStage": "Anti-Smog Traffic Restrictions",
        "dominantSources": [
            "Dense diesel road transport",
            "Intensive agriculture ammonia reacting to fine PM",
            "Stagnant Alpine foothills basin"
        ],
        "advisory": "Winter microclimate trapping particulates in Lombardy basin. Shift to public transit and postpone outdoor jogging to mid-afternoon."
    }
}

# Type aliases for enhanced readability and strict type safety
CityRecord = Dict[str, Any]
HourlyEntry = Dict[str, Any]
HourlyCurve = List[HourlyEntry]


@lru_cache(maxsize=64)
def calculate_diurnal_curve(base_pm25: float) -> HourlyCurve:
    """Computes a 24-hour diurnal cycle of PM2.5 based on atmospheric inversion dynamics.

    In cold winter months, solar radiation heats the ground layer at midday (12:00-14:00),
    breaking the nocturnal thermal lid and enabling atmospheric convective mixing.
    At night and early morning (05:00-09:00), radiant cooling traps particulates.

    Args:
        base_pm25 (float): The baseline 24-hour mean PM2.5 concentration in µg/m³.

    Returns:
        HourlyCurve: A 24-element list of hourly records with timestamp, particulate value,
            WHO color coding, category, and ventilation window flags.

    Example:
        >>> curve = calculate_diurnal_curve(100.0)
        >>> len(curve)
        24
    """
    safe_base = max(1.0, float(base_pm25))
    curve: HourlyCurve = []
    for h in range(24):
        mult = DIURNAL_INVERSION_MULTIPLIERS.get(h, 1.0)
        pm_val = round(safe_base * mult, 1)
        time_label = f"{h:02d}:00"

        if pm_val < 35.0:
            cat = "Moderate"
            color = "#10b981"
        elif pm_val < 75.0:
            cat = "Unhealthy for Sensitive"
            color = "#f59e0b"
        elif pm_val < 150.0:
            cat = "Unhealthy"
            color = "#ef4444"
        elif pm_val < 250.0:
            cat = "Very Unhealthy"
            color = "#8b5cf6"
        else:
            cat = "Hazardous"
            color = "#701a75"

        is_vent_window = (12 <= h <= 14)
        inversion_state = "Trapping Layer Active" if (h <= 10 or h >= 17) else "Convective Mixing Active"

        curve.append({
            "hour": h,
            "time": time_label,
            "pm25": pm_val,
            "category": cat,
            "color": color,
            "isVentilationWindow": is_vent_window,
            "inversionState": inversion_state
        })
    return curve


def get_city_data(city_id: str) -> Optional[CityRecord]:
    """Retrieves full environmental and inversion profile for a registered city.

    Args:
        city_id (str): The unique city identifier key (e.g. 'delhi', 'lahore', 'current_location').

    Returns:
        Optional[CityRecord]: Full city profile dictionary including 24-hour diurnal curve,
            or None if the city is not registered in the database.
    """
    if not city_id or city_id not in CITIES_REGISTRY:
        return None
    city = CITIES_REGISTRY[city_id]
    hourly = calculate_diurnal_curve(city["pm25"])
    return {**city, "hourly": hourly}


def register_custom_city(
    name: str,
    pm25: float,
    aqi: Optional[int] = None,
    temperature: float = 10.0,
    country: str = "Custom Region",
    humidity: float = 65.0,
    wind_speed: float = 4.0
) -> CityRecord:
    """Adds a new user-defined localized microclimate to the in-memory registry.

    Args:
        name (str): The human-readable name of the microclimate or neighborhood.
        pm25 (float): Baseline particulate concentration in µg/m³.
        aqi (Optional[int], optional): Air Quality Index. Computed automatically if omitted.
        temperature (float, optional): Ambient temperature in Celsius. Defaults to 10.0.
        country (str, optional): Country or jurisdiction name. Defaults to "Custom Region".
        humidity (float, optional): Relative humidity percentage. Defaults to 65.0.
        wind_speed (float, optional): Wind speed in km/h. Defaults to 4.0.

    Returns:
        CityRecord: The registered city record complete with 24-hour diurnal curve.
    """
    cid = f"custom_{abs(hash(name)) % 100000}"
    safe_pm25 = max(1.0, float(pm25))
    computed_aqi = int(aqi) if aqi is not None else int(safe_pm25 * 1.25)

    if safe_pm25 > 250:
        cat = "hazardous"
        status = "Severe / Hazardous"
    elif safe_pm25 > 150:
        cat = "very-unhealthy"
        status = "Very Unhealthy"
    elif safe_pm25 > 75:
        cat = "unhealthy"
        status = "Unhealthy"
    elif safe_pm25 > 35:
        cat = "sensitive"
        status = "Unhealthy for Sensitive Groups"
    else:
        cat = "moderate"
        status = "Moderate"

    new_city: CityRecord = {
        "id": cid,
        "name": name,
        "country": country,
        "aqi": computed_aqi,
        "status": status,
        "category": cat,
        "pm25": float(safe_pm25),
        "pm10": float(round(safe_pm25 * 1.45, 1)),
        "no2": 42.0,
        "co": 1.5,
        "temperature": float(temperature),
        "humidity": float(humidity),
        "inversionStrength": "Moderate Winter Inversion",
        "windSpeed": f"{wind_speed:.1f} km/h",
        "ventilationWindow": "12:30 PM - 2:30 PM",
        "grapStage": "Winter Smog Advisory",
        "dominantSources": ["Local combustion", "Vehicular emissions", "Topographic cold pool"],
        "advisory": f"Custom microclimate for {name}. Maintain indoor air defense during cold morning stagnation."
    }
    CITIES_REGISTRY[cid] = new_city
    return {**new_city, "hourly": calculate_diurnal_curve(new_city["pm25"])}


def process_current_location_weather(
    lat: float,
    lon: float,
    location_name: Optional[str] = None,
    live_pm25: Optional[float] = None,
    live_temperature: Optional[float] = None,
    live_humidity: Optional[float] = None,
    live_wind_speed: Optional[float] = None
) -> CityRecord:
    """Synthesizes and registers real-time meteorological & air sensor data for user GPS coordinates.

    Args:
        lat (float): User device latitude.
        lon (float): User device longitude.
        location_name (Optional[str], optional): Reverse-geocoded locality name.
        live_pm25 (Optional[float], optional): Sensor-observed PM2.5 in µg/m³.
        live_temperature (Optional[float], optional): Sensor-observed temperature in °C.
        live_humidity (Optional[float], optional): Sensor-observed relative humidity in %.
        live_wind_speed (Optional[float], optional): Sensor-observed wind speed in km/h.

    Returns:
        CityRecord: Complete city profile stored under 'current_location' with diurnal curve.
    """
    city_name = location_name or f"Current Location ({lat:.2f}°, {lon:.2f}°)"

    temp = float(live_temperature) if live_temperature is not None else 12.0
    humid = float(live_humidity) if live_humidity is not None else 65.0
    wind = float(live_wind_speed) if live_wind_speed is not None else 4.2

    # Calculate PM2.5: use live reading or atmospheric stagnation heuristic
    if live_pm25 is not None:
        pm25 = float(live_pm25)
    else:
        thermal_cold_bonus = 40.0 if temp < 5.0 else 0.0
        pm25 = max(25.0, round(120.0 - (wind * 8.0) + thermal_cold_bonus, 1))

    aqi = int(pm25 * 1.25)

    if pm25 > 250:
        cat = "hazardous"
        status = "Severe / Hazardous"
        grap = "Stage IV Emergency"
    elif pm25 > 150:
        cat = "very-unhealthy"
        status = "Very Unhealthy"
        grap = "Stage III Severe"
    elif pm25 > 75:
        cat = "unhealthy"
        status = "Unhealthy"
        grap = "Stage II Alert"
    elif pm25 > 35:
        cat = "sensitive"
        status = "Unhealthy for Sensitive Groups"
        grap = "Stage I Moderate"
    else:
        cat = "moderate"
        status = "Moderate / Fair"
        grap = "Normal Clean Air Protocol"

    inversion_desc = (
        "High Ground Stagnation (Inversion Trapping <90m)"
        if wind < 5.0
        else "Moderate Mixing Layer"
    )

    current_loc_data: CityRecord = {
        "id": "current_location",
        "name": f"📍 {city_name}",
        "country": "Local Observation",
        "lat": lat,
        "lon": lon,
        "aqi": aqi,
        "status": status,
        "category": cat,
        "pm25": pm25,
        "pm10": round(pm25 * 1.45, 1),
        "no2": 38.0,
        "co": 1.2,
        "temperature": round(temp, 1),
        "humidity": round(humid, 1),
        "windSpeed": f"{wind:.1f} km/h",
        "inversionStrength": inversion_desc,
        "ventilationWindow": "12:30 PM - 2:30 PM",
        "grapStage": grap,
        "dominantSources": [
            "Local vehicular emissions",
            "Winter nocturnal inversion",
            "Localized domestic heating"
        ],
        "advisory": (
            f"Real-time localized meteorological & smog reading for {city_name}. "
            "Stagger outdoor commutes away from morning boundary layer compression."
        )
    }

    CITIES_REGISTRY["current_location"] = current_loc_data
    return {**current_loc_data, "hourly": calculate_diurnal_curve(pm25)}
