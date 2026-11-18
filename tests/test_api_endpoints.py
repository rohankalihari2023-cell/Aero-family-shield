"""
test_api_endpoints.py
Direct functional unit tests for FastAPI route handler functions in server.py.
Validates HTTP payload handling, business logic execution, and response schemas.
"""

import unittest
from server import (
    get_system_status,
    list_cities,
    get_single_city,
    set_current_location,
    add_custom_city,
    chat_with_advisor,
    create_routine,
    compute_cadr,
    check_humidifier,
    calculate_lifestyle_impact,
    fetch_community_reports,
    submit_incident_report,
)
from models.schemas import (
    FamilyProfileSchema,
    ChatRequestSchema,
    RoutineRequestSchema,
    CADRRequestSchema,
    ImpactSimRequestSchema,
    CurrentLocationSchema,
    CustomCitySchema,
    IncidentReportSchema,
)
from core.exceptions import CityNotFoundError


class TestAPIEndpoints(unittest.TestCase):
    """Verifies that all server.py route handler functions execute reliably with expected outputs."""

    def test_status_endpoint(self):
        """Verify system diagnostic health check returns online status and features."""
        res = get_system_status()
        self.assertEqual(res["status"], "online")
        self.assertIn("AeroFamily", res["app"])
        self.assertIn("Geolocation-Weather-API", res["features"])

    def test_list_cities_endpoint(self):
        """Verify list_cities returns dictionary of major winter smog hotspots."""
        cities = list_cities()
        self.assertIsInstance(cities, dict)
        self.assertIn("delhi", cities)
        self.assertIn("lahore", cities)
        self.assertIn("hourly", cities["delhi"])

    def test_single_city_endpoint(self):
        """Verify single city retrieval returns full city profile with diurnal curves."""
        delhi = get_single_city("delhi")
        self.assertEqual(delhi["id"], "delhi")
        self.assertGreater(delhi["pm25"], 300)

    def test_single_city_not_found(self):
        """Verify requesting unregistered city raises typed CityNotFoundError."""
        with self.assertRaises(CityNotFoundError):
            get_single_city("nonexistent_city_xyz")

    def test_set_current_location_endpoint(self):
        """Verify setting current location coordinates and sensor data registers current_location."""
        payload = CurrentLocationSchema(
            lat=28.6139,
            lon=77.2090,
            name="Delhi Test Ward",
            pm25=185.0,
            temperature=14.0,
            humidity=72.0,
            windSpeed=3.5
        )
        res = set_current_location(payload)
        self.assertEqual(res["id"], "current_location")
        self.assertIn("Delhi Test Ward", res["name"])
        self.assertEqual(res["pm25"], 185.0)

    def test_add_custom_city_endpoint(self):
        """Verify registering a custom user microclimate via API."""
        payload = CustomCitySchema(
            name="Highland Basin",
            pm25=95.0,
            temperature=8.0,
            country="Test Country"
        )
        res = add_custom_city(payload)
        self.assertIsNotNone(res["id"])
        self.assertEqual(res["name"], "Highland Basin")
        self.assertEqual(res["pm25"], 95.0)

    def test_advisor_chat_endpoint(self):
        """Verify advisor chat route dispatches query and returns structured response."""
        req = ChatRequestSchema(
            message="What mask should my child wear in smog?",
            cityKey="delhi",
            familyProfile=FamilyProfileSchema(infants=1)
        )
        res = chat_with_advisor(req)
        self.assertIn("reply", res)
        self.assertIn("source", res)
        self.assertIn("KF94", res["reply"])

    def test_create_routine_endpoint(self):
        """Verify 24-hr daily routine synthesizer returns schedule and impact metrics."""
        req = RoutineRequestSchema(
            cityKey="delhi",
            familyProfile=FamilyProfileSchema(infants=1, asthmatics=1)
        )
        res = create_routine(req)
        self.assertIn("schedule", res)
        self.assertIn("metrics", res)
        self.assertGreater(res["metrics"]["exposureReductionPct"], 50.0)

    def test_cadr_calculator_endpoint(self):
        """Verify CADR calculation route returns Corsi-Rosenthal unit recommendations."""
        req = CADRRequestSchema(roomLengthFt=20, roomWidthFt=15, ceilingHeightFt=10, desiredACH=5.0)
        res = compute_cadr(req)
        self.assertEqual(res["requiredCadrCFM"], 250.0)
        self.assertIn("crBoxRecommendation", res)
        self.assertIn("savingsINR", res["crBoxRecommendation"])

    def test_humidifier_check_endpoint(self):
        """Verify humidifier safety evaluation flags tap water hazards."""
        res_tap = check_humidifier("tap")
        self.assertFalse(res_tap["isSafe"])
        self.assertEqual(res_tap["status"], "hazard")

        res_dist = check_humidifier("distilled")
        self.assertTrue(res_dist["isSafe"])

    def test_lifestyle_impact_endpoint(self):
        """Verify lifestyle impact simulation computes reduction percentages."""
        req = ImpactSimRequestSchema(
            cityKey="delhi",
            commuteChoice="metro",
            maskChoice="n95",
            airPurifierHours=18.0,
            homeSealing="sealed"
        )
        res = calculate_lifestyle_impact(req)
        self.assertIn("exposureReductionPct", res)
        self.assertGreater(res["exposureReductionPct"], 60.0)

    def test_community_feed_and_reporting_endpoints(self):
        """Verify fetching community reports and posting a new citizen incident."""
        initial_reports = fetch_community_reports()
        initial_count = len(initial_reports)

        report_req = IncidentReportSchema(
            cityKey="delhi",
            location="East Bypass Toll Plaza",
            incidentType="Heavy Diesel Soot & Trash Burning",
            details="Smog plume crossing residential boundary."
        )
        res = submit_incident_report(report_req)
        self.assertTrue(res["success"])
        self.assertIn("ticketId", res)

        updated_reports = fetch_community_reports()
        self.assertEqual(len(updated_reports), initial_count + 1)
        self.assertEqual(updated_reports[0]["location"], "East Bypass Toll Plaza")


if __name__ == "__main__":
    unittest.main()
