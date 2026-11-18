"""
test_smog_service.py
Unit tests for atmospheric inversion models, diurnal curves, and WHO thresholds.
"""

import unittest
from services.smog_service import (
    CITIES_REGISTRY,
    WHO_GUIDELINES,
    calculate_diurnal_curve,
    get_city_data,
    register_custom_city,
    process_current_location_weather
)

class TestSmogService(unittest.TestCase):

    def test_city_registry_contains_major_winter_hotspots(self):
        """Verify global winter smog cities are present in database."""
        self.assertIn("delhi", CITIES_REGISTRY)
        self.assertIn("lahore", CITIES_REGISTRY)
        self.assertIn("beijing", CITIES_REGISTRY)
        self.assertIn("saltlake", CITIES_REGISTRY)
        self.assertIn("ulaanbaatar", CITIES_REGISTRY)
        self.assertIn("katowice", CITIES_REGISTRY)
        self.assertIn("milan", CITIES_REGISTRY)

    def test_city_data_structure(self):
        """Verify all required smog & meteorological attributes exist."""
        delhi = get_city_data("delhi")
        self.assertIsNotNone(delhi)
        self.assertEqual(delhi["id"], "delhi")
        self.assertGreater(delhi["pm25"], 300)
        self.assertIn("hourly", delhi)
        self.assertEqual(len(delhi["hourly"]), 24)
        self.assertIn("inversionStrength", delhi)
        self.assertIn("ventilationWindow", delhi)

    def test_diurnal_inversion_curve_dynamics(self):
        """Verify that morning inversion has peak smog while midday has ventilation drop."""
        curve = calculate_diurnal_curve(100.0)
        self.assertEqual(len(curve), 24)
        
        # Morning peak (06:00 - 08:00) should be higher than baseline
        morning_val = curve[7]["pm25"]
        self.assertGreater(morning_val, 100.0)

        # Midday window (13:00) should be significantly lower than morning
        midday_val = curve[13]["pm25"]
        self.assertLess(midday_val, morning_val)
        self.assertTrue(curve[13]["isVentilationWindow"])

    def test_custom_city_registration(self):
        """Verify registering a custom microclimate works accurately."""
        custom = register_custom_city("Salt Lake Sub-Basin", pm25=120.0, temperature=-4.0)
        self.assertIsNotNone(custom["id"])
        self.assertEqual(custom["name"], "Salt Lake Sub-Basin")
        self.assertEqual(custom["pm25"], 120.0)
        self.assertEqual(custom["temperature"], -4.0)
        self.assertEqual(len(custom["hourly"]), 24)

    def test_who_guidelines_defined(self):
        """Verify WHO 2021 guideline constants."""
        self.assertEqual(WHO_GUIDELINES["pm25_24h_daily"], 15.0)
        self.assertEqual(WHO_GUIDELINES["berkeley_muller_factor"], 22.0)

    def test_current_location_weather_processing_with_live_data(self):
        """Verify processing live weather & air quality API inputs for user GPS location."""
        loc = process_current_location_weather(
            lat=40.7608,
            lon=-111.8910,
            location_name="Salt Lake Downtown",
            live_pm25=58.5,
            live_temperature=-2.0,
            live_humidity=75.0,
            live_wind_speed=3.2
        )
        self.assertIsNotNone(loc)
        self.assertEqual(loc["id"], "current_location")
        self.assertIn("Salt Lake Downtown", loc["name"])
        self.assertEqual(loc["pm25"], 58.5)
        self.assertEqual(loc["temperature"], -2.0)
        self.assertEqual(loc["humidity"], 75.0)
        self.assertEqual(loc["category"], "sensitive")
        self.assertEqual(len(loc["hourly"]), 24)
        self.assertIn("current_location", CITIES_REGISTRY)

    def test_current_location_weather_processing_coordinates_fallback(self):
        """Verify atmospheric inversion heuristic fallback when live API sensor is offline."""
        loc = process_current_location_weather(
            lat=28.6139,
            lon=77.2090
        )
        self.assertIsNotNone(loc)
        self.assertEqual(loc["id"], "current_location")
        self.assertGreater(loc["pm25"], 0)
        self.assertEqual(len(loc["hourly"]), 24)
        self.assertIn("hourly", loc)

if __name__ == "__main__":
    unittest.main()
