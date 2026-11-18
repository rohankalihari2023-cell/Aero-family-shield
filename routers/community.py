"""
community.py
Citizen incident reporting, open-burning violations, and community feed endpoints.
"""

from typing import Dict, Any, List

from fastapi import APIRouter

from models.schemas import IncidentReportSchema, IncidentResponseSchema
from services.community_service import get_community_feed, create_incident_report

router = APIRouter(tags=["Community Hub"])


@router.get(
    "/api/community/reports",
    summary="List active citizen pollution and open-burning incident reports",
    description="Returns verified community reports filed across monitored wards to inform neighborhood action."
)
def fetch_community_reports() -> List[Dict[str, Any]]:
    """Retrieves list of active community-reported pollution incidents.

    Returns:
        List[Dict[str, Any]]: Chronological list of verified pollution incidents.

    Examples:
        >>> reports = fetch_community_reports()
        >>> len(reports) >= 1
        True
    """
    return get_community_feed()


@router.post(
    "/api/community/report-smoke",
    response_model=IncidentResponseSchema,
    summary="Submit citizen violation or illegal open-burning report",
    description="Broadcasts verified localized smoke violations to Clean Air Action squads and generates an incident ticket."
)
def submit_incident_report(report: IncidentReportSchema) -> Dict[str, Any]:
    """Logs a citizen smoke, biomass, or toxic dust incident and creates a tracking ticket.

    Args:
        report (IncidentReportSchema): Validated location, category, severity, and observational notes.

    Returns:
        Dict[str, Any]: Confirmation ticket with unique identifier and broadcast status.

    Examples:
        >>> report = IncidentReportSchema(location="Anand Vihar Ward 4", cityKey="delhi", incidentType="Garbage Burning")
        >>> res = submit_incident_report(report)
        >>> res["success"]
        True
    """
    new_ticket = create_incident_report(
        location=report.location,
        city_key=report.cityKey,
        incident_type=report.incidentType,
        details=report.details,
    )
    return {
        "success": True,
        "ticketId": new_ticket["id"],
        "message": "Incident logged and broadcasted to local Clean Air Action Squad.",
        "report": new_ticket,
    }
