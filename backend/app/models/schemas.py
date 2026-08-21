from pydantic import BaseModel
from datetime import datetime
from typing import List


class EvidenceEvent(BaseModel):
    timestamp: datetime | None = None
    source: str
    event: str
    evidence_id: str


class IncidentResponse(BaseModel):
    incident_id: str
    status: str
    events: List[EvidenceEvent]