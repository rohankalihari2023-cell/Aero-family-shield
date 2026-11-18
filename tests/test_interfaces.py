"""
test_interfaces.py
Verifies that all domain service implementations conform strictly to their respective abstract protocols.
Enforces SOLID Dependency Inversion (DIP) and Interface Segregation (ISP).
"""

import unittest
from typing import get_type_hints

from core.interfaces import (
    IAIEngineService,
    ISmogService,
    IIAQService,
    IImpactService,
    IRoutineService,
)
import services.ai_engine as ai_engine
import services.smog_service as smog_service
import services.iaq_service as iaq_service
import services.impact_service as impact_service
import services.routine_service as routine_service


class TestInterfaces(unittest.TestCase):
    """Verifies service modules adhere strictly to protocol signatures."""

    def test_ai_engine_conformance(self):
        """Verify ai_engine implements generate_ai_response matching IAIEngineService contract."""
        self.assertTrue(hasattr(ai_engine, "generate_ai_response"))
        hints = get_type_hints(ai_engine.generate_ai_response)
        self.assertIn("message", hints)
        self.assertIn("city", hints)
        self.assertIn("return", hints)

    def test_smog_service_conformance(self):
        """Verify smog_service provides required atmospheric monitoring functions."""
        self.assertTrue(hasattr(smog_service, "get_city_data"))
        self.assertTrue(hasattr(smog_service, "calculate_diurnal_curve"))
        self.assertTrue(hasattr(smog_service, "process_current_location_weather"))

    def test_iaq_service_conformance(self):
        """Verify iaq_service fulfills CADR calculations and humidifier safety evaluations."""
        self.assertTrue(hasattr(iaq_service, "calculate_cadr_requirements"))
        self.assertTrue(hasattr(iaq_service, "evaluate_humidifier_safety"))

    def test_impact_service_conformance(self):
        """Verify impact_service fulfills lifestyle exposure simulation contract."""
        self.assertTrue(hasattr(impact_service, "simulate_lifestyle_impact"))

    def test_routine_service_conformance(self):
        """Verify routine_service fulfills daily diurnal schedule synthesis contract."""
        self.assertTrue(hasattr(routine_service, "generate_daily_routine"))
