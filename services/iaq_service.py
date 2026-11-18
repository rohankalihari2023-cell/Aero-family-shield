"""
iaq_service.py
Module for Indoor Air Quality (IAQ) engineering calculations:
Corsi-Rosenthal Box sizing, ACH (Air Changes per Hour), CADR physics,
humidity mineral dust danger analysis, and window draft infiltration.
"""

import math
from typing import Dict, Any

def calculate_cadr_requirements(
    length_ft: float,
    width_ft: float,
    height_ft: float = 9.0,
    desired_ach: float = 5.0
) -> Dict[str, Any]:
    """
    Computes room volume and required CADR (Clean Air Delivery Rate in CFM)
    to achieve desired Air Changes per Hour (ACH).
    Formula: CADR = (Room Volume in cu ft * ACH) / 60
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

    cr_cost = 75.0 * units_needed
    commercial_hepa_cost = 380.0 * units_needed
    savings = commercial_hepa_cost - cr_cost

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
            "estimatedCostUSD": cr_cost,
            "commercialHepaCostUSD": commercial_hepa_cost,
            "savingsUSD": savings,
            "estimatedCostINR": cr_cost_inr,
            "commercialHepaCostINR": commercial_hepa_cost_inr,
            "savingsINR": savings_inr,
            "filterReplacementCycleDays": filter_cycle_days,
            "noiseLevel": "38 - 44 dB (Conversational / Library Quiet)",
            "shroudEfficiencyBoost": "+35% CFM via circular 15-inch cardboard shroud"
        }
    }

def evaluate_humidifier_safety(water_type: str) -> Dict[str, Any]:
    """Analyzes aerosol risk of humidifier configurations."""
    wtype = water_type.lower()
    if wtype in ["tap", "hard_water"]:
        return {
            "status": "hazard",
            "isSafe": False,
            "hazardType": "Synthetic PM2.5 Mineral White Dust",
            "expectedPM25SpikeUg": 220.0,
            "explanation": "Ultrasonic discs shatter mineral salts (calcium, magnesium) into fine particles <2.5µm.",
            "recommendation": "Switch immediately to distilled water, reverse osmosis (RO) water, or use an evaporative wick unit."
        }
    elif wtype in ["distilled", "ro"]:
        return {
            "status": "safe",
            "isSafe": True,
            "hazardType": "None (Pure H2O Vapor)",
            "expectedPM25SpikeUg": 0.0,
            "explanation": "Zero dissolved mineral salts. Safe pure moisture maintains airway mucosal hydration.",
            "recommendation": "Optimal configuration for ultrasonic humidifiers."
        }
    else: # Evaporative
        return {
            "status": "gold_standard",
            "isSafe": True,
            "hazardType": "None (Evaporative Trapping)",
            "expectedPM25SpikeUg": 0.0,
            "explanation": "Natural evaporation leaves all tap minerals deposited in the paper wick cartridge.",
            "recommendation": "Safest and most cost-effective method to achieve 40-50% relative humidity."
        }
