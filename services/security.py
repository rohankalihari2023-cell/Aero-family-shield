"""
security.py
Security infrastructure for input validation, sanitization, XSS mitigation,
security response headers, and request bounding for AeroFamily.
"""

import html
from typing import Dict, Any, Optional
from core.config import SECURITY_HEADERS, get_logger

logger = get_logger(__name__)


def sanitize_string(text: Optional[str], max_len: int = 2000) -> str:
    """Escapes HTML entities and truncates excess lengths to prevent XSS and DoS attacks.

    Args:
        text (Optional[str]): Raw untrusted user input string.
        max_len (int, optional): Maximum permitted string length. Defaults to 2000.

    Returns:
        str: Safe, HTML-escaped and bounded string. Returns empty string if input is None or empty.

    Example:
        >>> sanitize_string("<script>alert(1)</script>", 100)
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if not text:
        return ""
    truncated = str(text)[:max_len].strip()
    return html.escape(truncated)


def validate_numeric_bounds(
    val: Any,
    min_val: float,
    max_val: float,
    default_val: float
) -> float:
    """Clamps numeric inputs safely within physically plausible domain boundaries.

    Protects against negative room dimensions, infinite ACH rates, or absurd coordinates.

    Args:
        val (Any): Input value to parse and clamp.
        min_val (float): Minimum allowable bound.
        max_val (float): Maximum allowable bound.
        default_val (float): Fallback value if casting fails.

    Returns:
        float: Clamped numeric value within [min_val, max_val].

    Example:
        >>> validate_numeric_bounds(-5.0, 1.0, 100.0, 10.0)
        1.0
        >>> validate_numeric_bounds("invalid", 1.0, 100.0, 10.0)
        10.0
    """
    try:
        f = float(val)
        if f < min_val:
            return min_val
        if f > max_val:
            return max_val
        return f
    except (ValueError, TypeError):
        logger.debug("Non-numeric input %r clamped to default %r", val, default_val)
        return default_val


def sanitize_profile_dict(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Validates, sanitizes, and clamps all keys within a household profile dictionary.

    Args:
        profile (Dict[str, Any]): Raw family demographic input dictionary.

    Returns:
        Dict[str, Any]: Sanitized dictionary safe for storage and mathematical modeling.
    """
    return {
        "infants": int(validate_numeric_bounds(profile.get("infants", 0), 0, 10, 0)),
        "asthmatics": int(validate_numeric_bounds(profile.get("asthmatics", 0), 0, 10, 0)),
        "seniors": int(validate_numeric_bounds(profile.get("seniors", 0), 0, 10, 0)),
        "pets": int(validate_numeric_bounds(profile.get("pets", 0), 0, 15, 0)),
        "healthyAdults": int(validate_numeric_bounds(profile.get("healthyAdults", 2), 1, 20, 2)),
        "housingType": sanitize_string(profile.get("housingType", "apartment"), 50),
        "cookingFuel": sanitize_string(profile.get("cookingFuel", "gas"), 50),
        "commuteMode": sanitize_string(profile.get("commuteMode", "car"), 50)
    }
