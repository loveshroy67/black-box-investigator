def build_investigation(
    incident: dict,
    hypotheses: list[dict]
) -> dict:

    events = incident.get("events", [])

    relationships = []

    for hypothesis in hypotheses:

        hypothesis_id = hypothesis.get("id")

        for event_id in hypothesis.get(
            "supporting_evidence",
            []
        ):
            relationships.append({
                "hypothesis_id": hypothesis_id,
                "event_id": event_id,
                "relationship": "supports"
            })

        for event_id in hypothesis.get(
            "contradicting_evidence",
            []
        ):
            relationships.append({
                "hypothesis_id": hypothesis_id,
                "event_id": event_id,
                "relationship": "contradicts"
            })

    return {
        "incident_id": incident.get("incident_id"),
        "timeline": events,
        "hypotheses": hypotheses,
        "relationships": relationships
    }