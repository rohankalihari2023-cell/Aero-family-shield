"""
routers package
Modular API router definitions for AeroFamily.
Decouples endpoint transport, payload validation, and service orchestration
into cohesive domain-driven controllers.
"""

from routers.system import router as system_router
from routers.atmospheric import router as atmospheric_router
from routers.advisor import router as advisor_router
from routers.routine import router as routine_router
from routers.iaq import router as iaq_router
from routers.impact import router as impact_router
from routers.community import router as community_router

__all__ = [
    "system_router",
    "atmospheric_router",
    "advisor_router",
    "routine_router",
    "iaq_router",
    "impact_router",
    "community_router",
]
