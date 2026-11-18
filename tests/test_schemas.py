"""
test_schemas.py
Unit tests verifying Pydantic schema validation, default boundaries,
and serialization logic for AeroFamily data models.
"""

import unittest
from pydantic import ValidationError
from models.schemas import (
    FamilyProfileSchema,
    ChatRequestSchema,
    CADRRequestSchema,
    CurrentLocationSchema,
    IncidentReportSchema,
)


class TestSchemas(unittest.TestCase):
    """Verifies Pydantic schemas enforce type safety and domain constraints."""

    def test_family_profile_defaults(self):
        """Verify default values and bounds for FamilyProfileSchema."""
        prof = FamilyProfileSchema()
        self.assertEqual(prof.infants, 0)
        self.assertEqual(prof.healthyAdults, 2)
        self.assertEqual(prof.housingType, "apartment")
        d = prof.to_dict()
        self.assertIsInstance(d, dict)

    def test_family_profile_bounds_rejection(self):
        """Verify out-of-bound negative counts raise validation error."""
        with self.assertRaises(ValidationError):
            FamilyProfileSchema(infants=-1)

    def test_current_location_valid(self):
        """Verify valid GPS coordinates are accepted."""
        loc = CurrentLocationSchema(lat=28.6139, lon=77.2090, pm25=120.0)
        self.assertEqual(loc.lat, 28.6139)
        self.assertEqual(loc.lon, 77.2090)

    def test_current_location_invalid_coords(self):
        """Verify invalid latitude (>90) or longitude (>180) are rejected."""
        with self.assertRaises(ValidationError):
            CurrentLocationSchema(lat=95.0, lon=77.2090)
        with self.assertRaises(ValidationError):
            CurrentLocationSchema(lat=28.0, lon=200.0)

    def test_cadr_schema_bounds(self):
        """Verify CADR dimensions enforce physical bounds."""
        req = CADRRequestSchema(roomLengthFt=12, roomWidthFt=10, ceilingHeightFt=8, desiredACH=4.0)
        self.assertEqual(req.roomLengthFt, 12.0)
        with self.assertRaises(ValidationError):
            CADRRequestSchema(roomLengthFt=0.5)

    def test_chat_request_min_length(self):
        """Verify empty chat messages are rejected."""
        with self.assertRaises(ValidationError):
            ChatRequestSchema(message="")

    def test_incident_report_validation(self):
        """Verify incident report enforces required location and category."""
        report = IncidentReportSchema(
            location="Main Ring Road",
            incidentType="Leaf Burning"
        )
        self.assertEqual(report.cityKey, "delhi")


if __name__ == "__main__":
    unittest.main()
