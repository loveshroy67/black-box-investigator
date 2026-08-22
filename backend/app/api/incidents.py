import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.schemas import (
    EvidenceResponse,
    InvestigationDetailResponse,
    TimelineResponse,
    InvestigationResponse
)

from app.services.hypothesis import generate_hypotheses
from app.services.local_hypothesis import generate_local_hypotheses

from app.services.parser import detect_file_type, extract_text
from app.services.reasoning import extract_events

from app.services.store import (
    add_evidence,
    add_hypotheses,
    get_incident
)

from app.services.timeline import build_timeline
from app.services.investigation import build_investigation


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


UPLOAD_DIR = "uploads"


# ============================================================
# UPLOAD EVIDENCE
# ============================================================

@router.post(
    "/{incident_id}/evidence",
    response_model=EvidenceResponse
)
async def upload_evidence(
    incident_id: str,
    file: UploadFile = File(...)
):

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    evidence_id = str(uuid.uuid4())

    filename = file.filename or "unknown"

    # --------------------------------------------------------
    # Detect file type
    # --------------------------------------------------------

    file_type = detect_file_type(filename)

    if file_type == "unknown":
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )

    # --------------------------------------------------------
    # Save uploaded file
    # --------------------------------------------------------

    file_path = os.path.join(
        UPLOAD_DIR,
        f"{evidence_id}_{filename}"
    )

    content = await file.read()

    with open(file_path, "wb") as output:
        output.write(content)

    # --------------------------------------------------------
    # Extract text
    # --------------------------------------------------------

    extracted_text = extract_text(
        file_path,
        file_type
    )

    # --------------------------------------------------------
    # Extract structured events
    # --------------------------------------------------------

    events = []

    if extracted_text:

        try:

            print("Attempting Gemini event extraction...")

            result = extract_events(
                extracted_text,
                filename
            )

            extracted_events = result.get(
                "events",
                []
            )

            for event in extracted_events:

                event_id = str(uuid.uuid4())

                events.append(
                    {
                        "event_id": event_id,
                        "timestamp": event.get(
                            "timestamp"
                        ),
                        "source": filename,
                        "event": event.get(
                            "event",
                            ""
                        ),
                        "evidence_id": evidence_id,
                        "type": event.get(
                            "type",
                            "other"
                        ),
                        "severity": event.get(
                            "severity",
                            "info"
                        )
                    }
                )

            print(
                f"Extracted {len(events)} events."
            )

        except Exception as error:

            import traceback

            print(
                "AI EVENT EXTRACTION FAILED"
            )

            traceback.print_exc()

            raise HTTPException(
                status_code=500,
                detail=(
                    f"AI extraction failed: "
                    f"{str(error)}"
                )
            )

    # --------------------------------------------------------
    # Create evidence object
    # --------------------------------------------------------

    evidence = {
        "evidence_id": evidence_id,
        "incident_id": incident_id,
        "filename": filename,
        "file_type": file_type,
        "status": "processed",
        "extracted_text": extracted_text,
        "events": events
    }

    # --------------------------------------------------------
    # Store evidence and events
    # --------------------------------------------------------

    add_evidence(
        incident_id,
        evidence
    )

    return evidence


# ============================================================
# GET TIMELINE
# ============================================================

@router.get(
    "/{incident_id}/timeline",
    response_model=TimelineResponse
)
def get_timeline(
    incident_id: str
):

    incident = get_incident(
        incident_id
    )

    if not incident:

        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    timeline = build_timeline(
        incident.get(
            "events",
            []
        )
    )

    return {
        "incident_id": incident_id,
        "total_events": len(timeline),
        "events": timeline
    }


# ============================================================
# POST - INVESTIGATE INCIDENT
# ============================================================

@router.post(
    "/{incident_id}/investigate",
    response_model=InvestigationResponse
)
def investigate_incident(incident_id: str):

    incident = get_incident(incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    events = build_timeline(
        incident.get("events", [])
    )

    if not events:
        raise HTTPException(
            status_code=400,
            detail="No evidence events available for investigation"
        )

    hypotheses = []
    source = "local"

    try:
        result = generate_hypotheses(events)

        source = result.get(
            "source",
            "local"
        )

        hypotheses = result.get(
            "hypotheses",
            []
        )

        print(
            f"{source.capitalize()} generated "
            f"{len(hypotheses)} hypotheses."
        )

    except Exception as error:

        print(
            f"Gemini hypothesis generation failed: {error}"
        )

        print(
            "Using local hypothesis engine."
        )

        result = generate_local_hypotheses(events)

        hypotheses = result.get(
            "hypotheses",
            []
        )

        source = result.get(
            "source",
            "local"
        )

        print(
            f"Local hypothesis generation complete: "
            f"{len(hypotheses)} hypotheses."
        )

    if not hypotheses:

        print(
            "Gemini returned no hypotheses."
        )

        print(
            "Using local hypothesis engine."
        )

        result = generate_local_hypotheses(events)

        hypotheses = result.get(
            "hypotheses",
            []
        )

        source = result.get(
            "source",
            "local"
        )

        print(
            f"Local hypothesis generation complete: "
            f"{len(hypotheses)} hypotheses."
        )

    if not hypotheses:

        raise HTTPException(
            status_code=500,
            detail="Unable to generate investigation hypotheses"
        )

    add_hypotheses(
        incident_id,
        hypotheses
    )

    investigation = build_investigation(
        incident,
        hypotheses
    )

    print(
        f"Investigation complete using {source}."
    )

    return {
        "incident_id": incident_id,
        "status": "investigation_complete",
        "source": source,
        "hypotheses": hypotheses
    }

# ============================================================
# GET - INVESTIGATION DETAILS
# ============================================================

@router.get(
    "/{incident_id}/investigation",
    response_model=InvestigationDetailResponse
)
def get_investigation(
    incident_id: str
):

    incident = get_incident(
        incident_id
    )

    if not incident:

        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    # --------------------------------------------------------
    # Build timeline
    # --------------------------------------------------------

    events = build_timeline(
        incident.get(
            "events",
            []
        )
    )

    if not events:

        raise HTTPException(
            status_code=400,
            detail="No evidence events available"
        )

    # --------------------------------------------------------
    # Get stored hypotheses
    # --------------------------------------------------------

    hypotheses = incident.get(
        "hypotheses",
        []
    )

    if not hypotheses:

        raise HTTPException(
            status_code=404,
            detail="Investigation has not been run yet"
        )

    # --------------------------------------------------------
    # Build full investigation
    # --------------------------------------------------------

    investigation = build_investigation(
        incident,
        hypotheses
    )

    return investigation