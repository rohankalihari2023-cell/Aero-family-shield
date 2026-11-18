"""
routine.py
24-hour diurnal low-emission schedule generator and exposure avoidance planner endpoint.
"""

from typing import Dict, Any

from fastapi import APIRouter

from models.schemas import RoutineRequestSchema
from services.routine_service import generate_daily_routine
from services.smog_service import get_city_data
from services.security import sanitize_profile_dict

router = APIRouter(tags=["Routine Planner"])


@router.post(
    "/api/routine/generate",
    summary="Synthesize 24-hour personalized clean-air routine",
    description="Calculates diurnal inversion exposure windows and shifts high-risk activities into optimal atmospheric intervals."
)
def create_routine(req: RoutineRequestSchema) -> Dict[str, Any]:
    """Generates an optimized diurnal schedule contrasting baseline exposure with protected alternatives.

    Args:
        req (RoutineRequestSchema): Target city key and validated household vulnerability profile.

    Returns:
        Dict[str, Any]: 6-interval daily timeline with particulate exposure metrics, cumulative reduction, and avoided cigarette counts.

    Examples:
        >>> from models.schemas import FamilyProfileSchema
        >>> req = RoutineRequestSchema(cityKey="delhi", familyProfile=FamilyProfileSchema(asthmatics=1))
        >>> plan = create_routine(req)
        >>> len(plan["schedule"])
        6
    """
    city_data = get_city_data(req.cityKey) or get_city_data("delhi") or {}
    prof_dict = sanitize_profile_dict(req.familyProfile.to_dict())
    return generate_daily_routine(city=city_data, profile=prof_dict)
