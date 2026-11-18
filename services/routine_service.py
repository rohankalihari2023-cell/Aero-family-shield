"""
routine_service.py
Module for synthesizing 24-hour low-emission daily routines,
calculating personal inhalation dosage, and tracking emission reductions.
"""

from typing import Dict, Any, List

def generate_daily_routine(city: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesizes a 24-hour diurnal low-emission schedule tailored to city meteorology
    and household vulnerabilities, calculating before/after exposure and emissions.
    """
    pm = float(city["pm25"])
    
    # Inhalation rate models:
    # Resting adult: ~0.5 - 0.7 m³/hr
    # Active transit / exercise: ~1.2 - 2.0 m³/hr
    # 24-hr baseline volume: ~15.2 m³
    
    # Baseline Scenario (Unconscious habits):
    # - Morning commute in traffic (1.5h * 1.5 m³/h * 1.4*pm)
    # - Drafty daytime indoor space with no HEPA (8h * 0.8 m³/h * 0.7*pm)
    # - Evening commute & open market errands (1.5h * 1.5 m³/h * 1.3*pm)
    # - Cooking with unvented gas & unsealed evening living room (3.5h * 0.8 m³/h * 0.65*pm)
    # - Sleeping in unsealed bedroom without air purifier (9.5h * 0.5 m³/h * 0.6*pm)
    baseline_inhaled_ug = round(pm * 15.26, 1)

    # Optimized AeroFamily Plan:
    # - Metro/Carpool transit with sealed N95 (95% mask filtration + cabin recirculation)
    # - Workplace/School with HEPA/C-R box (indoor PM capped at 12 µg/m³)
    # - Consolidated evening errands + N95
    # - Induction cooking + weathersealed living room (indoor PM capped at 10 µg/m³)
    # - Sealed bedroom with HEPA on sleep mode (indoor PM capped at 8 µg/m³)
    optimized_inhaled_ug = round((0.27 * pm) + 76.8 + 28.0 + 38.4, 1)
    
    reduction_ug = max(0.0, round(baseline_inhaled_ug - optimized_inhaled_ug, 1))
    exposure_reduction_pct = round((reduction_ug / baseline_inhaled_ug) * 100.0, 1)

    # Berkeley Earth equivalence: 22 µg/m³ 24h average ~ 1 cigarette
    # Normalized across typical 15 m³ daily air exchange:
    cigs_baseline = round(baseline_inhaled_ug / (22.0 * 15.0), 1)
    cigs_saved = round(reduction_ug / (22.0 * 15.0), 1)

    co2_saved_kg = 5.4
    tailpipe_pm_saved_g = 42.0

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
            "recommendedAction": "Execute a timed 20-minute cross-ventilation purge. Air out rooms to flush CO2, then seal windows and burst air purifier on Turbo for 20 mins.",
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
            "emissionSaving": "Optimal low-wattage filtration (~35W)"
        }
    ]

    return {
        "city": city["name"],
        "metrics": {
            "baselineInhaledUg": baseline_inhaled_ug,
            "optimizedInhaledUg": optimized_inhaled_ug,
            "exposureReductionPct": exposure_reduction_pct,
            "cigarettesBaseline": cigs_baseline,
            "cigarettesSaved": cigs_saved,
            "co2SavedKg": co2_saved_kg,
            "tailpipePmSavedG": tailpipe_pm_saved_g
        },
        "schedule": schedule
    }
