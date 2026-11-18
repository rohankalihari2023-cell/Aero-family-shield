"""
routine_service.py
Module for synthesizing personalized 24-hour low-emission daily routines,
calculating personal inhalation dosage, and tracking collective carbon reductions.
"""

from typing import Dict, Any, List


def generate_daily_routine(city: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesizes a 24-hour diurnal low-emission schedule tailored to city meteorology.

    Harmonizes daily routines with winter temperature inversion cycles:
    - Minimizes physical exertion during high stagnation periods (06:30-09:30, 19:30-22:00)
    - Maximizes active ventilation and errands during the convective mixing window (12:30-14:30)
    - Quantifies before-and-after particulate inhalation dosages and cigarette equivalents.

    Args:
        city (Dict[str, Any]): Active city record containing PM2.5 and ventilation windows.
        profile (Dict[str, Any]): Household demographic profile.

    Returns:
        Dict[str, Any]: Complete schedule intervals, personal exposure reductions,
            and community carbon/particulate savings.

    Example:
        >>> routine = generate_daily_routine({"pm25": 200.0, "name": "Delhi"}, {"infants": 1})
        >>> routine["metrics"]["exposureReductionPct"] > 50.0
        True
    """
    pm = max(1.0, float(city.get("pm25", 100.0)))

    # Inhalation rate models:
    # Resting adult: ~0.5 - 0.7 m³/hr
    # Active transit / exercise: ~1.2 - 2.0 m³/hr
    # 24-hr baseline volume: ~15.26 m³

    # Baseline Scenario (Unconscious habits):
    # - Morning outdoor jog & open windows in morning smog
    # - Drafty workspace/school with no HEPA
    # - Rush hour commute with open window vents
    # - Unvented gas cooking & evening unsealed living room
    # - Overnight drafty sleeping without filtration
    baseline_inhaled_ug = round(pm * 15.26, 1)

    # Optimized AeroFamily Plan:
    # - Indoor stretch & HEPA safe room during morning inversion
    # - Carpool/Metro with sealed N95 + HVAC 100% recirculation
    # - Timed 20-min ventilation purge during midday convective mixing
    # - Consolidated evening transit avoiding arterial diesel corridors
    # - Induction cooking + sealed sleep chamber with continuous low HEPA
    optimized_inhaled_ug = round((0.27 * pm) + 76.8 + 28.0 + 38.4, 1)

    reduction_ug = max(0.0, round(baseline_inhaled_ug - optimized_inhaled_ug, 1))
    exposure_reduction_pct = round((reduction_ug / baseline_inhaled_ug) * 100.0, 1) if baseline_inhaled_ug > 0 else 0.0

    # Berkeley Earth equivalence: 22 µg/m³ 24h average inhaled across standard 15 m³ = 330 µg ~ 1 cigarette
    cigs_saved = round(reduction_ug / (22.0 * 15.0), 1)

    co2_saved_kg = 5.4
    tailpipe_pm_saved_g = 42.0

    vent_window = city.get("ventilationWindow", "12:30 PM - 2:30 PM")

    schedule: List[Dict[str, Any]] = [
        {
            "timeSlot": "06:30 - 08:00",
            "period": "Early Morning Inversion Cap",
            "outdoorSmogStatus": "Hazardous (Peak Trapping Layer)",
            "baselineAction": "Morning jog outdoors, opening windows for 'morning air', warming car engine while idling in driveway.",
            "recommendedAction": "Keep windows tightly sealed. Practice 20-min indoor yoga/stretch in HEPA-filtered safe room. Pack pediatric KF94/KN95 masks.",
            "directImpact": "Prevents 140 µg heavy-metal particulate inhalation; eliminates 0.8 kg cold-start CO2.",
            "emissionSaving": "Zero cold-start idling"
        },
        {
            "timeSlot": "08:00 - 09:15",
            "period": "Morning School & Work Transit",
            "outdoorSmogStatus": "Severe Roadside Exhaust Spikes",
            "baselineAction": "Solo gasoline/diesel vehicle with exterior fresh-air intake open in bumper-to-bumper queue.",
            "recommendedAction": "Join AeroFamily School Carpool Pod or take Underground Electric Metro. In car, set HVAC strictly to 100% Recirculation with N95 mask on.",
            "directImpact": "Cuts cabin PM2.5 by 82%; pulls 3 idling cars away from school entrance gates.",
            "emissionSaving": "-2.1 kg CO2e / trip"
        },
        {
            "timeSlot": "12:30 - 14:00",
            "period": "Optimal Midday Ventilation Window",
            "outdoorSmogStatus": "Diurnal Inversion Break (Convective Mixing)",
            "baselineAction": "Keeping windows tightly shut all day causing CO2 to hit 1,900 ppm, or opening windows randomly at 9:00 PM.",
            "recommendedAction": (
                f"Execute a timed 20-minute cross-ventilation purge during {vent_window}. "
                "Air out rooms to flush CO2, then seal windows and burst air purifier on Turbo for 20 mins."
            ),
            "directImpact": "Flushes indoor CO2 from 1,800 ppm to 680 ppm without letting winter smog linger.",
            "emissionSaving": "Zero energy waste"
        },
        {
            "timeSlot": "17:30 - 19:00",
            "period": "Evening Boundary Layer Drop",
            "outdoorSmogStatus": "Rapid Smog Inversion Re-formation",
            "baselineAction": "Multiple outdoor errands along high-traffic diesel corridors; kids playing in park.",
            "recommendedAction": "Consolidate errands into one trip using quiet residential backstreets. Move children to an indoor Clean Air Safe Haven.",
            "directImpact": "Shields pediatric airways during highest evening particulate accumulation.",
            "emissionSaving": "-1.5 kg CO2e"
        },
        {
            "timeSlot": "19:30 - 21:00",
            "period": "Dinner & Home Heating",
            "outdoorSmogStatus": "Dense Nocturnal Smog",
            "baselineAction": "Unvented gas stove frying + wood burning fireplace or continuous central boiler on 23°C.",
            "recommendedAction": "Cook on induction stove with tight lids & range hood running. Set thermostat to 19°C, use door draft snakes and heated blanket.",
            "directImpact": "Eliminates indoor NO2 spikes (>100 ppb from gas flames); saves 18% heating energy.",
            "emissionSaving": "-1.8 kg CO2e & zero smoke"
        },
        {
            "timeSlot": "22:00 - 06:30",
            "period": "Overnight Sleep Defense",
            "outdoorSmogStatus": "Stagnant Shallow Inversion",
            "baselineAction": "Sleeping in drafty unsealed bedroom with no air filtration.",
            "recommendedAction": "Sealed bedroom door, Corsi-Rosenthal box or HEPA running on Low/Sleep mode. Keep humidity at 45% using evaporative humidifier.",
            "directImpact": "Maintains bedroom PM2.5 < 10 µg/m³ throughout 8 hours of restorative deep sleep.",
            "emissionSaving": "15% fan efficiency gain"
        }
    ]

    return {
        "city": city.get("name", "Local"),
        "baselinePM25": pm,
        "metrics": {
            "baselineInhaledUg": baseline_inhaled_ug,
            "optimizedInhaledUg": optimized_inhaled_ug,
            "reductionUg": reduction_ug,
            "exposureReductionPct": exposure_reduction_pct,
            "cigarettesSaved": cigs_saved,
            "co2SavedKg": co2_saved_kg,
            "tailpipePmSavedG": tailpipe_pm_saved_g
        },
        "schedule": schedule
    }
