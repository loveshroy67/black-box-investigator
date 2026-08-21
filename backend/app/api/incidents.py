import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.schemas import EvidenceResponse
from app.services.parser import detect_file_type, extract_text


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


UPLOAD_DIR = "uploads"


@router.post("/{incident_id}/evidence", response_model=EvidenceResponse)
async def upload_evidence(
    incident_id: str,
    file: UploadFile = File(...)
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    evidence_id = str(uuid.uuid4())

    filename = file.filename or "unknown"

    file_type = detect_file_type(filename)

    if file_type == "unknown":
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )

    file_path = os.path.join(
        UPLOAD_DIR,
        f"{evidence_id}_{filename}"
    )

    content = await file.read()

    with open(file_path, "wb") as output:
        output.write(content)

    extracted_text = extract_text(
        file_path,
        file_type
    )

    return {
        "evidence_id": evidence_id,
        "incident_id": incident_id,
        "filename": filename,
        "file_type": file_type,
        "status": "processed",
        "extracted_text": extracted_text,
        "events": []
    }