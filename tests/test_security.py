"""
test_security.py
Unit tests for input sanitization, XSS mitigation, parameter bounding, and security headers.
"""

import unittest
from services.security import (
    SECURITY_HEADERS,
    sanitize_string,
    validate_numeric_bounds,
    sanitize_profile_dict
)

class TestSecurity(unittest.TestCase):

    def test_xss_script_injection_escaped(self):
        """Verify script tags and malicious attributes are sanitized to harmless entities."""
        malicious = "<script>alert('XSS')</script>"
        safe = sanitize_string(malicious)
        self.assertNotIn("<script>", safe)
        self.assertIn("&lt;script&gt;", safe)

    def test_xss_img_onerror_escaped(self):
        """Verify image onerror event injection is neutralized."""
        malicious = '<img src=x onerror=alert(1)>'
        safe = sanitize_string(malicious)
        self.assertNotIn("<img", safe)
        self.assertIn("&lt;img", safe)

    def test_length_truncation_limits_dos(self):
        """Verify excess string input length is capped at specified bounds."""
        huge_string = "A" * 10000
        safe = sanitize_string(huge_string, max_len=500)
        self.assertEqual(len(safe), 500)

    def test_numeric_bounds_clamping(self):
        """Verify numerical inputs outside valid physical bounds are safely clamped."""
        # Below min
        self.assertEqual(validate_numeric_bounds(-50, 0, 100, 10), 0)
        # Above max
        self.assertEqual(validate_numeric_bounds(99999, 0, 100, 10), 100)
        # Non-numeric fallback
        self.assertEqual(validate_numeric_bounds("invalid", 0, 100, 10), 10)

    def test_family_profile_sanitization(self):
        """Verify family profile dictionary is clamped and sanitized."""
        unsafe_prof = {
            "infants": 9999,
            "asthmatics": -10,
            "housingType": "<script>alert(1)</script>",
            "cookingFuel": "gas"
        }
        clean = sanitize_profile_dict(unsafe_prof)
        self.assertEqual(clean["infants"], 10) # Clamped to max 10
        self.assertEqual(clean["asthmatics"], 0) # Clamped to min 0
        self.assertNotIn("<script>", clean["housingType"])

    def test_security_headers_configured(self):
        """Verify critical OWASP security headers exist."""
        self.assertIn("X-Content-Type-Options", SECURITY_HEADERS)
        self.assertEqual(SECURITY_HEADERS["X-Content-Type-Options"], "nosniff")
        self.assertIn("X-Frame-Options", SECURITY_HEADERS)
        self.assertEqual(SECURITY_HEADERS["X-Frame-Options"], "DENY")
        self.assertIn("Content-Security-Policy", SECURITY_HEADERS)

if __name__ == "__main__":
    unittest.main()
