"""
test_routine_service.py
Unit tests for 24-hr daily routine generation and exposure math.
"""

import unittest
from services.routine_service import generate_daily_routine
from services.smog_service import get_city_data

class TestRoutineService(unittest.TestCase):

    def setUp(self):
        self.delhi = get_city_data("delhi")
        self.profile = {
            "infants": 1,
            "asthmatics": 1,
            "seniors": 0,
            "pets": 1,
            "healthyAdults": 2,
            "housingType": "apartment",
            "cookingFuel": "gas",
            "commuteMode": "car"
        }

    def test_daily_routine_structure(self):
        """Verify schedule contains 6 distinct diurnal intervals with metrics."""
        res = generate_daily_routine(self.delhi, self.profile)
        self.assertIn("metrics", res)
        self.assertIn("schedule", res)
        self.assertEqual(len(res["schedule"]), 6)

    def test_exposure_reduction_calculation(self):
        """Verify AeroFamily plan reduces inhaled PM2.5 by more than 50%."""
        res = generate_daily_routine(self.delhi, self.profile)
        metrics = res["metrics"]
        
        baseline = metrics["baselineInhaledUg"]
        optimized = metrics["optimizedInhaledUg"]
        pct_reduction = metrics["exposureReductionPct"]

        self.assertGreater(baseline, optimized)
        self.assertGreater(pct_reduction, 50.0)
        self.assertLessEqual(pct_reduction, 100.0)

    def test_cigarettes_and_co2_savings(self):
        """Verify cigarette equivalency and greenhouse gas tracking."""
        res = generate_daily_routine(self.delhi, self.profile)
        metrics = res["metrics"]

        self.assertGreater(metrics["cigarettesSaved"], 0.0)
        self.assertGreater(metrics["co2SavedKg"], 0.0)
        self.assertGreater(metrics["tailpipePmSavedG"], 0.0)

    def test_schedule_items_contain_alternatives_and_impact(self):
        """Verify each slot contrasts baseline habit with smog-safe alternative."""
        res = generate_daily_routine(self.delhi, self.profile)
        for slot in res["schedule"]:
            self.assertIn("timeSlot", slot)
            self.assertIn("baselineAction", slot)
            self.assertIn("recommendedAction", slot)
            self.assertIn("directImpact", slot)
            self.assertIn("emissionSaving", slot)

if __name__ == "__main__":
    unittest.main()
