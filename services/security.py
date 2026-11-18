"""
security.py
Security infrastructure for input validation, sanitization, XSS mitigation,
security response headers, and request bounding.
"""

import html
import re
from typing import Dict, Any, Optional

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": (
        "default-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://fonts.googleapis.com https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://generativelanguage.googleapis.com;"
    )
}

def sanitize_string(text: Optional[str], max_len: int = 2000) -> str:
    """Escapes HTML entities and truncates excess lengths to prevent XSS and DoS."""
    if not text:
        return ""
    truncated = str(text)[:max_len].strip()
    return html.escape(truncated)

def validate_numeric_bounds(val: float, min_val: float, max_val: float, default_val: float) -> float:
    """Clamps numeric inputs securely within physical boundaries."""
    try:
        f = float(val)
        if f < min_val:
            return min_val
        if f > max_val:
            return max_val
        return f
    except (ValueError, TypeError):
        return default_val

def sanitize_profile_dict(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Validates and clamps family profile parameters."""
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
