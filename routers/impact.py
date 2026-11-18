"""
impact.py
Personal lung particulate dosage simulation and Berkeley Earth cigarette equivalence math endpoint.
"""

from typing import Dict, Any

from fastapi import APIRouter

from models.schemas import ImpactSimRequestSchema
from services.impact_service import simulate_lifestyle_impact
from services.smog_service import get_city_data

router = APIRouter(tags=["Lifestyle Impact"])


@router.post(
    "/api/impact/simulate",
    summary="Simulate lifestyle decisions and lung particulate burden",
    description="Calculates exact microgram inhalation exposure, filtration reduction %, avoided cigarette equivalents, and greenhouse gas abatement."
)
def calculate_lifestyle_impact(req: ImpactSimRequestSchema) -> Dict[str, Any]:
    """Calculates comparative respiratory exposure and particulate reduction between baseline and protected habits.

    Args:
        req (ImpactSimRequestSchema): Validated commuter, mask, air purifier, cooking, and home sealing parameters.

    Returns:
        Dict[str, Any]: Dosage reduction metrics, microgram exposure totals, and avoided cigarette counts.

    Examples:
        >>> req = ImpactSimRequestSchema(cityKey="delhi", commuteChoice="metro", maskChoice="n95")
        >>> impact = calculate_lifestyle_impact(req)
        >>> impact["reduction_pct"] > 50.0
        True
    """
    city_data = get_city_data(req.cityKey) or get_city_data("delhi") or {"pm25": 100.0}
    return simulate_lifestyle_impact(
        outdoor_pm25=city_data.get("pm25", 100.0),
        commute_mode=req.commuteChoice,
        mask_type=req.maskChoice,
        purifier_hours=req.airPurifierHours,
        home_sealing=req.homeSealing,
        cooking_mode=req.cookingMode,
        household_size=req.householdSize,
    )
