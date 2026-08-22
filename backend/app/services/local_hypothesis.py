def generate_local_hypotheses(
    events: list[dict]
) -> dict:

    deployment_events = []
    database_events = []
    application_events = []
    infrastructure_events = []

    for event in events:

        event_type = (
            event.get("type", "")
            .lower()
        )

        if event_type == "deployment":
            deployment_events.append(event)

        elif event_type == "database":
            database_events.append(event)

        elif event_type == "application":
            application_events.append(event)

        elif event_type == "infrastructure":
            infrastructure_events.append(event)

    hypotheses = []

    # ========================================================
    # H1 - DATABASE ISSUE
    # ========================================================

    database_supporting = [
        event["event_id"]
        for event in database_events
        if event.get("event_id")
    ]

    database_contradicting = [
        event["event_id"]
        for event in infrastructure_events
        if event.get("event_id")
    ]

    if database_events:

        hypotheses.append({

            "id": "H1",

            "title":
                "Database Performance or Migration Issue",

            "description": (
                "Database migration or database-related "
                "activity may have caused increased latency, "
                "connection timeouts, and downstream "
                "application failures."
            ),

            "confidence": 0.65,

            "reasoning": (
                "Database-related events occur before the "
                "connection timeout and subsequent application "
                "failures. The temporal relationship makes a "
                "database-related problem a plausible "
                "explanation."
            ),

            "supporting_evidence":
                database_supporting,

            "contradicting_evidence":
                database_contradicting,

            "insufficient_evidence_notes": (
                "Database metrics, query performance data, "
                "schema changes, lock information, and "
                "database resource metrics are required "
                "to confirm the specific root cause."
            )
        })

    # ========================================================
    # H2 - DEPLOYMENT ISSUE
    # ========================================================

    deployment_supporting = [
        event["event_id"]
        for event in deployment_events
        if event.get("event_id")
    ]

    deployment_contradicting = [
        event["event_id"]
        for event in database_events
        if event.get("event_id")
    ]

    if deployment_events:

        hypotheses.append({

            "id": "H2",

            "title":
                "Application Defect Introduced During Deployment",

            "description": (
                "The deployment may have introduced an "
                "application problem that affected database "
                "connectivity or request handling."
            ),

            "confidence": 0.40,

            "reasoning": (
                "A deployment occurred before the database "
                "and application failures. However, the "
                "available evidence does not directly show "
                "that the deployed code caused the database "
                "degradation."
            ),

            "supporting_evidence":
                deployment_supporting,

            "contradicting_evidence":
                deployment_contradicting,

            "insufficient_evidence_notes": (
                "Deployment commit details, application "
                "stack traces, connection pool metrics, "
                "and application performance metrics "
                "are needed."
            )
        })

    # ========================================================
    # H3 - INFRASTRUCTURE ISSUE
    # ========================================================

    infrastructure_supporting = []

    for event in events:

        if event.get("type") in (
            "database",
            "application",
            "infrastructure"
        ):

            if event.get("event_id"):

                infrastructure_supporting.append(
                    event["event_id"]
                )

    infrastructure_contradicting = (
        deployment_supporting
    )

    if infrastructure_supporting:

        hypotheses.append({

            "id": "H3",

            "title":
                "Independent Infrastructure Degradation",

            "description": (
                "An underlying database, network, or "
                "infrastructure problem may have caused "
                "the connection failures independently "
                "of the deployment or migration."
            ),

            "confidence": 0.25,

            "reasoning": (
                "The evidence shows database connection "
                "problems followed by application failures. "
                "However, the available logs do not contain "
                "enough infrastructure information to "
                "determine whether the underlying cause "
                "was independent of release activities."
            ),

            "supporting_evidence":
                infrastructure_supporting,

            "contradicting_evidence":
                infrastructure_contradicting,

            "insufficient_evidence_notes": (
                "Infrastructure health metrics, network "
                "logs, database host metrics, CPU, memory, "
                "disk, and connection statistics are "
                "required."
            )
        })

    return {
    "source": "local",
    "hypotheses": hypotheses
}