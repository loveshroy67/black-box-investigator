incidents = {}


def create_incident(incident_id: str):
    if incident_id not in incidents:
        incidents[incident_id] = {
            "incident_id": incident_id,
            "evidence": [],
            "events": [],
            "hypotheses": []
        }

    return incidents[incident_id]


def add_evidence(incident_id: str, evidence: dict):
    incident = create_incident(incident_id)

    incident["evidence"].append(evidence)
    incident["events"].extend(
        evidence.get("events", [])
    )

    return incident


def add_hypotheses(
    incident_id: str,
    hypotheses: list[dict]
):
    incident = create_incident(incident_id)

    incident["hypotheses"] = hypotheses

    return incident


def get_incident(incident_id: str):
    return incidents.get(incident_id)