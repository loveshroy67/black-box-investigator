from fastapi import APIRouter
from app.models.schemas import IncidentResponse

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


@router.post("/{incident_id}", response_model=IncidentResponse)
def create_incident(incident_id: str):

    return {
        "incident_id": incident_id,
        "status": "created",
        "events": []
    }