"""
iaq.py
Indoor Air Quality (IAQ) engineering, Clean Air Delivery Rate (CADR), and humidifier safety endpoints.
"""

from typing import Dict, Any

from fastapi import APIRouter

from models.schemas import CADRRequestSchema
from services.iaq_service import calculate_cadr_requirements, evaluate_humidifier_safety
from services.security import sanitize_string

router = APIRouter(tags=["IAQ Engineering"])


@router.post(
    "/api/iaq/cadr-calculator",
    summary="Calculate CADR, ACH, and Corsi-Rosenthal unit specifications",
    description="Applies EPA & ASHRAE 62.2 mass-balance formulas to compute CFM requirements, DIY box designs, and cost savings in ₹."
)
def compute_cadr(req: CADRRequestSchema) -> Dict[str, Any]:
    """Computes room volume, required clean air delivery rate, and DIY purification requirements.

    Args:
        req (CADRRequestSchema): Dimensional room parameters and target air changes per hour (ACH).

    Returns:
        Dict[str, Any]: CADR requirements in CFM, recommended Corsi-Rosenthal box units, fan speeds,
            MERV-13 filter specifications, and rupee savings compared to commercial HEPA units.

    Examples:
        >>> req = CADRRequestSchema(roomLengthFt=15, roomWidthFt=12, ceilingHeightFt=10, desiredACH=5)
        >>> res = compute_cadr(req)
        >>> res["required_cadr_cfm"]
        150.0
    """
    return calculate_cadr_requirements(
        length_ft=req.roomLengthFt,
        width_ft=req.roomWidthFt,
        height_ft=req.ceilingHeightFt,
        desired_ach=req.desiredACH,
    )


@router.post(
    "/api/iaq/humidifier-check",
    summary="Evaluate ultrasonic humidifier mineral aerosolization risk",
    description="Analyzes tap vs distilled vs RO water minerals that ultrasonic humidifiers shatter into breathable PM2.5 aerosols."
)
def check_humidifier(water_type: str) -> Dict[str, Any]:
    """Evaluates the particulate emission hazard of ultrasonic humidifier water sources.

    Args:
        water_type (str): Type of water utilized ('tap', 'hard_water', 'distilled', 'ro', 'evaporative').

    Returns:
        Dict[str, Any]: Particulate hazard level, safety grade, clinical mechanism, and safe recommendations.

    Examples:
        >>> res = check_humidifier("tap")
        >>> res["hazard_level"]
        'HIGH'
    """
    clean_type = sanitize_string(water_type, max_len=30)
    return evaluate_humidifier_safety(clean_type)
