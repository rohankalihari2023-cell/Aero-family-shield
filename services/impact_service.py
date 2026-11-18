"""
impact_service.py
Module for quantitative environmental and personal exposure impact modeling:
inhalation microgram dosage, Berkeley Earth cigarette equivalence math,
and community greenhouse gas (CO2e) avoidance.
"""

from typing import Dict, Any


def simulate_lifestyle_impact(
    outdoor_pm25: float,
    commute_mode: str = "metro",
    mask_type: str = "n95",
    purifier_hours: float = 16.0,
    home_sealing: str = "sealed",
    cooking_mode: str = "induction_vented",
    household_size: int = 3
) -> Dict[str, Any]:
    """Simulates daily particulate mass deposited in human lungs and emissions averted.

    Applies the Berkeley Earth inhalation model (Muller et al.):
        Cigarettes Inhaled = (24-hr Mean PM2.5 in µg/m³) / 22.0 µg/m³
    Coupled with human minute ventilation rates (~0.8 m³/hr resting, ~1.2 m³/hr active transit)
    and building envelope infiltration dynamics.

    Args:
        outdoor_pm25 (float): Ambient outdoor PM2.5 concentration in µg/m³.
        commute_mode (str, optional): Commute choice ('metro', 'carpool', 'solo_car', 'cycling'). Defaults to "metro".
        mask_type (str, optional): Mask type ('none', 'cloth', 'surgical', 'n95'). Defaults to "n95".
        purifier_hours (float, optional): Purifier daily runtime in hours [0, 24]. Defaults to 16.0.
        home_sealing (str, optional): Envelope sealing ('sealed', 'average', 'leaky'). Defaults to "sealed".
        cooking_mode (str, optional): Kitchen setup ('gas_unvented', 'gas_vented', 'induction_vented'). Defaults to "induction_vented".
        household_size (int, optional): Number of individuals residing in the home. Defaults to 3.

    Returns:
        Dict[str, Any]: Simulated exposure reduction metrics, particulate micrograms avoided,
            cigarette equivalents spared, and community carbon savings.

    Example:
        >>> res = simulate_lifestyle_impact(300.0, "metro", "n95", 16.0, "sealed", "induction_vented", 3)
        >>> res["exposureReductionPct"] > 50.0
        True
    """
    out_pm = max(1.0, float(outdoor_pm25))
    hours = min(24.0, max(0.0, float(purifier_hours)))
    size = max(1, int(household_size))

    # Building envelope infiltration factors
    infil_map = {"leaky": 0.75, "average": 0.50, "sealed": 0.25}
    infil = infil_map.get((home_sealing or "").strip().lower(), 0.50)

    # Indoor cooking combustion emission factors
    cook_map = {"gas_unvented": 45.0, "gas_vented": 15.0, "induction_vented": 3.0}
    cook_pm = cook_map.get((cooking_mode or "").strip().lower(), 15.0)

    # HEPA / C-R purifier volumetric scrubbing efficiency
    purifier_eff = (hours / 24.0) * 0.88
    indoor_ambient_pm = max(5.0, (out_pm * infil + cook_pm) * (1.0 - purifier_eff))

    # Mask particulate penetration fraction
    mask_map = {"none": 1.0, "cloth": 0.70, "surgical": 0.55, "n95": 0.05}
    mask_factor = mask_map.get((mask_type or "").strip().lower(), 1.0)

    # Daily human respiratory deposition volume
    indoor_hours = 21.5
    outdoor_hours = 2.5
    inhale_rate_rest = 0.8    # m³/hr
    inhale_rate_active = 1.2  # m³/hr

    daily_inhaled_ug = (indoor_hours * inhale_rate_rest * indoor_ambient_pm) + \
                       (outdoor_hours * inhale_rate_active * out_pm * mask_factor)
    daily_inhaled_ug = round(daily_inhaled_ug, 1)

    # Baseline comparison (leaky building, unvented gas, no mask, zero purifier)
    worst_indoor = out_pm * 0.75 + 45.0
    worst_daily = (indoor_hours * inhale_rate_rest * worst_indoor) + (outdoor_hours * inhale_rate_active * out_pm * 1.0)
    worst_daily = round(worst_daily, 1)

    ug_avoided_daily = max(0.0, round(worst_daily - daily_inhaled_ug, 1))
    pct_reduction = round((ug_avoided_daily / worst_daily) * 100.0, 1) if worst_daily > 0 else 0.0

    # Berkeley Earth equivalence: 22 µg/m³ 24h average inhaled across standard 15 m³ = 330 µg ~ 1 cigarette
    cigs_avoided_daily = round(ug_avoided_daily / (22.0 * 15.0), 1)
    monthly_cigs_avoided = round(cigs_avoided_daily * 30.0, 1)
    household_monthly_cigs_avoided = round(monthly_cigs_avoided * size, 1)

    # Commute emissions avoided vs solo combustion vehicle
    commute_co2_kg = {"solo_car": 6.8, "carpool": 2.2, "metro": 0.9, "cycling": 0.0}
    co2_saved_kg = round(6.8 - commute_co2_kg.get((commute_mode or "").strip().lower(), 2.2), 1)
    monthly_co2_saved_kg = round(co2_saved_kg * 30.0, 1)

    return {
        "outdoorPM25": out_pm,
        "indoorCalculatedPM25": round(indoor_ambient_pm, 1),
        "dailyInhaledUg": daily_inhaled_ug,
        "worstCaseDailyUg": worst_daily,
        "ugAvoidedPerDay": ug_avoided_daily,
        "exposureReductionPct": pct_reduction,
        "cigarettesAvoidedDaily": cigs_avoided_daily,
        "monthlyCigarettesAvoided": monthly_cigs_avoided,
        "householdMonthlyCigarettesAvoided": household_monthly_cigs_avoided,
        "co2SavedKgPerDay": co2_saved_kg,
        "monthlyCo2SavedKg": monthly_co2_saved_kg
    }
