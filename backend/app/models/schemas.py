from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class EvidenceEvent(BaseModel):
    event_id: str
    timestamp: datetime | None = None
    source: str
    event: str
    evidence_id: str
    type: str = "other"
    severity: str = "info"


class IncidentResponse(BaseModel):
    incident_id: str
    status: str
    events: List[EvidenceEvent] = Field(default_factory=list)


class EvidenceResponse(BaseModel):
    evidence_id: str
    incident_id: str
    filename: str
    file_type: str
    status: str
    extracted_text: str = ""
    events: List[EvidenceEvent] = Field(default_factory=list)


class TimelineResponse(BaseModel):
    incident_id: str
    total_events: int
    events: List[EvidenceEvent] = Field(default_factory=list)

class Hypothesis(BaseModel):
    id: str
    title: str
    confidence: float
    reasoning: str
    supporting_evidence: List[str] = Field(default_factory=list)
    contradicting_evidence: List[str] = Field(default_factory=list)


class InvestigationResponse(BaseModel):
    incident_id: str
    status: str
    source: str
    hypotheses: List[Hypothesis] = Field(default_factory=list)

class InvestigationRelationship(BaseModel):
    hypothesis_id: str
    event_id: str
    relationship: str


class InvestigationDetailResponse(BaseModel):
    incident_id: str
    timeline: list[dict]
    hypotheses: list[dict]
    relationships: list[InvestigationRelationship]