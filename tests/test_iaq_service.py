"""
test_iaq_service.py
Unit tests for IAQ engineering calculations, CADR formula, and humidifier analysis.
"""

import unittest
from services.iaq_service import calculate_cadr_requirements, evaluate_humidifier_safety

class TestIAQService(unittest.TestCase):

    def test_cadr_calculation_accuracy(self):
        """Verify CADR formula: CADR = (RoomVolume * ACH) / 60."""
        # 20ft x 15ft x 10ft room = 3000 cu ft
        # Desired ACH = 6.0
        # Expected CADR = (3000 * 6) / 60 = 300 CFM
        res = calculate_cadr_requirements(length_ft=20, width_ft=15, height_ft=10, desired_ach=6.0)
        self.assertEqual(res["roomVolumeCuFt"], 3000.0)
        self.assertEqual(res["requiredCadrCFM"], 300.0)
        self.assertEqual(res["crBoxRecommendation"]["unitsNeeded"], 1)

    def test_cadr_large_room_multiple_units(self):
        """Verify multiple C-R boxes recommended for large community or school spaces."""
        # 40ft x 30ft x 12ft room = 14400 cu ft
        # Desired ACH = 5.0
        # Expected CADR = (14400 * 5) / 60 = 1200 CFM
        # At 340 CFM per unit -> ceil(1200 / 340) = 4 units
        res = calculate_cadr_requirements(length_ft=40, width_ft=30, height_ft=12, desired_ach=5.0)
        self.assertEqual(res["crBoxRecommendation"]["unitsNeeded"], 4)
        self.assertGreater(res["crBoxRecommendation"]["savingsUSD"], 800)

    def test_humidifier_tap_water_hazard(self):
        """Verify tap water in ultrasonic humidifier is flagged as hazardous mineral PM2.5."""
        res = evaluate_humidifier_safety("tap")
        self.assertFalse(res["isSafe"])
        self.assertEqual(res["status"], "hazard")
        self.assertIn("Synthetic PM2.5", res["hazardType"])
        self.assertGreater(res["expectedPM25SpikeUg"], 100)

    def test_humidifier_distilled_water_safe(self):
        """Verify distilled water is marked safe with zero mineral emission."""
        res = evaluate_humidifier_safety("distilled")
        self.assertTrue(res["isSafe"])
        self.assertEqual(res["status"], "safe")
        self.assertEqual(res["expectedPM25SpikeUg"], 0.0)

    def test_humidifier_evaporative_gold_standard(self):
        """Verify evaporative wick humidifier is marked as gold standard."""
        res = evaluate_humidifier_safety("evaporative")
        self.assertTrue(res["isSafe"])
        self.assertEqual(res["status"], "gold_standard")

if __name__ == "__main__":
    unittest.main()
