"""
iaq_service.py
Module for Indoor Air Quality (IAQ) engineering calculations:
Corsi-Rosenthal Box sizing, ACH (Air Changes per Hour), Clean Air Delivery Rate (CADR) physics,
ultrasonic humidifier mineral dust hazard simulations, and thermal envelope sealing.
"""

import math
from typing import Dict, Any


def calculate_cadr_requirements(
    length_ft: float,
    width_ft: float,
    height_ft: float = 9.0,
    desired_ach: float = 5.0
) -> Dict[str, Any]:
    """Computes room volume and required Clean Air Delivery Rate (CADR) in CFM.

    Uses the fundamental mass balance ventilation equation:
        CADR = (Room Volume in cu. ft. * Desired ACH) / 60 minutes

    Evaluates DIY Corsi-Rosenthal (C-R) box fan specifications (MERV 13 filtration cubes),
    quantifying units needed and economic savings compared to commercial HEPA purifiers.

    Args:
        length_ft (float): Room length in feet.
        width_ft (float): Room width in feet.
        height_ft (float, optional): Ceiling height in feet. Defaults to 9.0.
        desired_ach (float, optional): Target Air Changes per Hour. Defaults to 5.0.

    Returns:
        Dict[str, Any]: Structured dictionary with room geometry, CADR requirements,
            and Corsi-Rosenthal configuration recommendations.

    Example:
        >>> res = calculate_cadr_requirements(20, 15, 10, 6.0)
        >>> res["requiredCadrCFM"]
        300.0
    """
    length = max(1.0, float(length_ft))
    width = max(1.0, float(width_ft))
    height = max(1.0, float(height_ft))
    ach = max(1.0, float(desired_ach))

    room_area_sqft = round(length * width, 1)
    room_vol_cuft = round(length * width * height, 1)
    required_cadr_cfm = round((room_vol_cuft * ach) / 60.0, 1)

    # 20-inch Box Fan with 4x MERV 13 Filters (Standard Corsi-Rosenthal Box)
    # Speed 1: ~220 CFM (Whisper quiet)
    # Speed 2: ~340 CFM (Optimal balance)
    # Speed 3: ~450 CFM (High performance burst)
    cadr_speed2 = 340.0
    units_needed = max(1, math.ceil(required_cadr_cfm / cadr_speed2))

    total_effective_cadr = cadr_speed2 * units_needed
    effective_ach = round((total_effective_cadr * 60.0) / room_vol_cuft, 1)

    cr_cost_usd = 75.0 * units_needed
    commercial_hepa_cost_usd = 380.0 * units_needed
    savings_usd = commercial_hepa_cost_usd - cr_cost_usd

    cr_cost_inr = 6000.0 * units_needed
    commercial_hepa_cost_inr = 31500.0 * units_needed
    savings_inr = commercial_hepa_cost_inr - cr_cost_inr

    filter_cycle_days = 90 if ach >= 5.0 else 120

    return {
        "roomAreaSqFt": room_area_sqft,
        "roomVolumeCuFt": room_vol_cuft,
        "desiredACH": ach,
        "requiredCadrCFM": required_cadr_cfm,
        "crBoxRecommendation": {
            "unitsNeeded": units_needed,
            "recommendedSpeed": "Speed 2 (Quiet Medium)",
            "estimatedCadrCFM": total_effective_cadr,
            "effectiveACH": effective_ach,
            "estimatedCostUSD": cr_cost_usd,
            "commercialHepaCostUSD": commercial_hepa_cost_usd,
            "savingsUSD": savings_usd,
            "estimatedCostINR": cr_cost_inr,
            "commercialHepaCostINR": commercial_hepa_cost_inr,
            "savingsINR": savings_inr,
            "filterReplacementCycleDays": filter_cycle_days,
            "noiseLevel": "38 - 44 dB (Conversational / Library Quiet)",
            "shroudEfficiencyBoost": "+35% CFM via circular 15-inch cardboard shroud"
        }
    }


def evaluate_humidifier_safety(water_type: str) -> Dict[str, Any]:
    """Analyzes particulate emission risk and respiratory safety for humidifier water types.

    Explains how ultrasonic cool-mist atomizers shatter dissolved mineral salts into
    inhalable synthetic PM2.5 white dust when filled with untreated hard tap water.

    Args:
        water_type (str): Type of water utilized ('tap', 'hard_water', 'distilled', 'ro', 'evaporative').

    Returns:
        Dict[str, Any]: Clinical evaluation containing safety boolean, hazard classification,
            expected PM2.5 spike, and mitigation guidance.

    Example:
        >>> res = evaluate_humidifier_safety("tap")
        >>> res["isSafe"]
        False
    """
    wtype = (water_type or "").strip().lower()
    if wtype in ["tap", "hard_water"]:
        return {
            "status": "hazard",
            "isSafe": False,
            "hazardType": "Synthetic PM2.5 Mineral White Dust",
            "expectedPM25SpikeUg": 220.0,
            "explanation": (
                "Ultrasonic transducer discs oscillate at 1.7 MHz, atomizing water droplets along with "
                "dissolved calcium, magnesium, and chloride salts into fine aerosols <2.5 µm that penetrate deep into lung alveoli."
            ),
            "recommendation": (
                "Switch immediately to distilled water, reverse osmosis (RO) water, "
                "or replace with a natural evaporative wick humidifier."
            )
        }
    elif wtype in ["distilled", "ro"]:
        return {
            "status": "safe",
            "isSafe": True,
            "hazardType": "None (Pure H2O Vapor)",
            "expectedPM25SpikeUg": 0.0,
            "explanation": (
                "Zero dissolved mineral salts. Pure distilled water generates zero particulate microdust, "
                "maintaining protective airway mucosal hydration."
            ),
            "recommendation": "Optimal configuration for ultrasonic humidifiers. Clean tank weekly to avoid biofilm."
        }
    else:  # Evaporative
        return {
            "status": "gold_standard",
            "isSafe": True,
            "hazardType": "None (Evaporative Moisture)",
            "expectedPM25SpikeUg": 0.0,
            "explanation": (
                "Evaporative wick humidifiers draw air through a moist paper filter wick. Water evaporates molecularly, "
                "leaving 100% of minerals and deposits trapped safely inside the paper cartridge."
            ),
            "recommendation": "Safest and most cost-effective method to achieve 40-50% relative humidity using standard tap water."
        }
