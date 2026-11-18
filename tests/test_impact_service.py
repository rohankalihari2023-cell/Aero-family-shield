"""
test_impact_service.py
Unit tests for quantitative lifestyle impact modeling and cigarette equivalence.
"""

import unittest
from services.impact_service import simulate_lifestyle_impact

class TestImpactService(unittest.TestCase):

    def test_impact_simulation_shielded_vs_unshielded(self):
        """Verify that N95 + sealed home + air purifier dramatically reduces PM2.5 inhalation."""
        res = simulate_lifestyle_impact(
            outdoor_pm25=300.0,
            commute_mode="metro",
            mask_type="n95",
            purifier_hours=18.0,
            home_sealing="sealed",
            cooking_mode="induction_vented",
            household_size=3
        )

        self.assertLess(res["indoorCalculatedPM25"], 35.0)
        self.assertGreater(res["exposureReductionPct"], 70.0)
        self.assertGreater(res["cigarettesAvoidedDaily"], 5.0)
        self.assertGreater(res["monthlyCigarettesAvoided"], 150.0)
        self.assertGreater(res["co2SavedKgPerDay"], 3.0)

    def test_mask_filtration_differential(self):
        """Verify N95 yields higher reduction than cloth mask."""
        res_n95 = simulate_lifestyle_impact(outdoor_pm25=200.0, mask_type="n95")
        res_cloth = simulate_lifestyle_impact(outdoor_pm25=200.0, mask_type="cloth")

        self.assertLess(res_n95["dailyInhaledUg"], res_cloth["dailyInhaledUg"])
        self.assertGreater(res_n95["exposureReductionPct"], res_cloth["exposureReductionPct"])

    def test_home_sealing_differential(self):
        """Verify weathersealed envelope reduces indoor PM vs leaky envelope."""
        res_sealed = simulate_lifestyle_impact(outdoor_pm25=250.0, home_sealing="sealed")
        res_leaky = simulate_lifestyle_impact(outdoor_pm25=250.0, home_sealing="leaky")

        self.assertLess(res_sealed["indoorCalculatedPM25"], res_leaky["indoorCalculatedPM25"])

if __name__ == "__main__":
    unittest.main()
