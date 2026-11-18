"""
community_service.py
Service managing community-driven air quality reports, citizen smoke spotters,
and neighborhood collective incident feeds for AeroFamily.
"""

import time
from typing import List, Dict, Any
from core.config import get_logger
from services.security import sanitize_string

logger = get_logger(__name__)

# Preloaded community incident logs
_COMMUNITY_FEED: List[Dict[str, Any]] = [
    {
        "id": "rep-101",
        "location": "North Ring Sector 4",
        "city": "delhi",
        "type": "Municipal Leaf & Waste Burning",
        "timestamp": "25 mins ago",
        "severity": "High",
        "status": "Dispatched to Flying Squad",
        "reportedBy": "Citizen Watch #402"
    },
    {
        "id": "rep-102",
        "location": "Industrial Bypass Crossroad",
        "city": "lahore",
        "type": "Heavy Diesel Truck Idling & Black Smoke",
        "timestamp": "1 hour ago",
        "severity": "Severe",
        "status": "Traffic Police Alerted",
        "reportedBy": "AeroPod Member #18"
    },
    {
        "id": "rep-103",
        "location": "South Hills Construction Pit",
        "city": "saltlake",
        "type": "Uncovered Dry Earthworks (Dust Plume)",
        "timestamp": "3 hours ago",
        "severity": "Moderate",
        "status": "Water Sprinkler Requested",
        "reportedBy": "EcoNeighbor #91"
    }
]


def get_community_feed() -> List[Dict[str, Any]]:
    """Retrieves all active community pollution and open-burning incident reports.

    Returns:
        List[Dict[str, Any]]: Chronologically ordered list of incident reports.
    """
    return list(_COMMUNITY_FEED)


def create_incident_report(
    location: str,
    city_key: str,
    incident_type: str,
    details: str = ""
) -> Dict[str, Any]:
    """Records a new citizen-reported pollution event and registers it in the live feed.

    Args:
        location (str): Exact location, street, or intersection of the violation.
        city_key (str): Monitored city identifier.
        incident_type (str): Category (e.g. Leaf Burning, Diesel Idling, Dust Plume).
        details (str, optional): Additional witness context or observations.

    Returns:
        Dict[str, Any]: The newly created and validated incident record.
    """
    clean_location = sanitize_string(location, 200)
    clean_city = sanitize_string(city_key, 50)
    clean_type = sanitize_string(incident_type, 100)
    clean_details = sanitize_string(details, 1000)

    ticket_id = f"rep-{int(time.time())}"
    new_ticket: Dict[str, Any] = {
        "id": ticket_id,
        "location": clean_location,
        "city": clean_city,
        "type": clean_type,
        "timestamp": "Just now",
        "severity": "High",
        "status": "Logged & Queued to Local Control Room",
        "details": clean_details,
        "reportedBy": "AeroFamily Citizen Guardian"
    }

    _COMMUNITY_FEED.insert(0, new_ticket)
    logger.info("Recorded new citizen incident ticket %s in %s", ticket_id, clean_city)

    return new_ticket
