"""
test_routers.py
Unit tests verifying the modular FastAPI APIRouters, routing tables, and endpoints.
"""

import unittest
from routers import (
    system_router,
    atmospheric_router,
    advisor_router,
    routine_router,
    iaq_router,
    impact_router,
    community_router,
)
from server import create_app


class TestRouters(unittest.TestCase):
    """Verifies that all domain APIRouters are configured with appropriate paths, methods, and tags."""

    def setUp(self):
        """Build a clean application instance for inspection."""
        self.app = create_app()
        self.openapi = self.app.openapi()
        self.paths = list(self.openapi.get("paths", {}).keys())

    def test_all_routers_included(self):
        """Verify that all core routes are mounted in the FastAPI application."""
        expected_routes = [
            "/api/status",
            "/api/cities",
            "/api/city/{city_id}",
            "/api/location/current",
            "/api/custom-city",
            "/api/advisor/chat",
            "/api/routine/generate",
            "/api/iaq/cadr-calculator",
            "/api/iaq/humidifier-check",
            "/api/impact/simulate",
            "/api/community/reports",
            "/api/community/report-smoke",
            "/",
        ]
        for route in expected_routes:
            self.assertIn(route, self.paths, f"Route {route} not found in OpenAPI paths")

    def test_router_tags_configured(self):
        """Verify router tags correspond to OpenAPI taxonomy."""
        self.assertEqual(system_router.tags, ["System"])
        self.assertEqual(atmospheric_router.tags, ["Atmospheric Smog"])
        self.assertEqual(advisor_router.tags, ["AI Advisor"])
        self.assertEqual(routine_router.tags, ["Routine Planner"])
        self.assertEqual(iaq_router.tags, ["IAQ Engineering"])
        self.assertEqual(impact_router.tags, ["Lifestyle Impact"])
        self.assertEqual(community_router.tags, ["Community Hub"])
