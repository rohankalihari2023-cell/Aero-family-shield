"""
test_ai_engine.py
Unit tests for GenAI assistant reasoning, prompt synthesis, and clinical vulnerability heuristics.
"""

import unittest
from services.ai_engine import (
    build_vulnerability_summary,
    generate_offline_reasoning,
    generate_ai_response
)
from services.smog_service import get_city_data

class TestAIEngine(unittest.TestCase):

    def setUp(self):
        self.delhi = get_city_data("delhi")
        self.profile = {
            "infants": 1,
            "asthmatics": 1,
            "seniors": 1,
            "pets": 1,
            "healthyAdults": 2
        }

    def test_vulnerability_summary_builder(self):
        """Verify household vulnerabilities are properly identified in prompts."""
        summary = build_vulnerability_summary(self.profile)
        self.assertIn("Toddler/Infant", summary)
        self.assertIn("Asthmatic", summary)
        self.assertIn("Elderly", summary)
        self.assertIn("Pet", summary)

    def test_vulnerability_summary_empty(self):
        """Verify empty profile defaults gracefully."""
        summary = build_vulnerability_summary({})
        self.assertEqual(summary, "Standard Adult Risk Profile")

    def test_pediatric_safety_inquiry(self):
        """Verify advice for child outdoor play warns against exposure."""
        res = generate_offline_reasoning(
            message="Can my toddler play in the park today during smog?",
            city=self.delhi,
            profile=self.profile
        )
        self.assertIn("Pediatric", res)
        self.assertIn("KF94", res)
        self.assertIn("Direct Impact", res)
        self.assertIn("alveolar", res.lower())

    def test_corsi_rosenthal_inquiry(self):
        """Verify advice for DIY purifiers explains fan, filters, and shroud."""
        res = generate_offline_reasoning(
            message="How do I build a DIY Corsi-Rosenthal box fan purifier?",
            city=self.delhi,
            profile=self.profile
        )
        self.assertIn("Corsi-Rosenthal", res)
        self.assertIn("MERV 13", res)
        self.assertIn("Shroud", res)
        self.assertIn("CADR", res)

    def test_ventilation_window_inquiry(self):
        """Verify advice for ventilation specifies the midday purge protocol."""
        res = generate_offline_reasoning(
            message="When can I open windows to ventilate stale CO2?",
            city=self.delhi,
            profile=self.profile
        )
        self.assertIn("Midday", res)
        self.assertIn("20-Minute", res)
        self.assertIn(self.delhi["ventilationWindow"], res)

    def test_ai_response_orchestrator(self):
        """Verify full response generation returns reply, source, and city."""
        output = generate_ai_response(
            message="What is the air status today?",
            city=self.delhi,
            profile=self.profile,
            api_key=None
        )
        self.assertIn("reply", output)
        self.assertIn("source", output)
        self.assertEqual(output["city"], self.delhi["name"])
        self.assertGreater(len(output["reply"]), 200)

if __name__ == "__main__":
    unittest.main()
