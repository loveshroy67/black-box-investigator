import json

from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEY


# ============================================================
# GEMINI CONFIG
# ============================================================

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not loaded")

client = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL = "gemini-3.6-flash"


# ============================================================
# HELPERS
# ============================================================

def event_ids(events):
    return [
        event.get("event_id")
        for event in events
        if event.get("event_id")
    ]


def find_events(events, keywords):
    results = []

    for event in events:

        text = str(
            event.get("event", "")
        ).lower()

        if any(
            keyword.lower() in text
            for keyword in keywords
        ):
            results.append(event)

    return results


def remove_duplicates(events):
    result = []
    seen = set()

    for event in events:

        event_id = event.get("event_id")

        if event_id and event_id not in seen:
            seen.add(event_id)
            result.append(event)

    return result


# ============================================================
# LOCAL HYPOTHESIS ENGINE
# ============================================================

def generate_local_hypotheses(
    events: list[dict]
) -> dict:

    if not events:
        return {
            "source": "local",
            "hypotheses": []
        }

    valid_ids = {
        event.get("event_id")
        for event in events
        if event.get("event_id")
    }

    # --------------------------------------------------------
    # Event groups
    # --------------------------------------------------------

    deployment_events = find_events(
        events,
        ["deployment", "deploy"]
    )

    migration_events = find_events(
        events,
        ["migration"]
    )

    database_events = find_events(
        events,
        [
            "database",
            "migration",
            "connection",
            "timeout",
            "latency"
        ]
    )

    application_events = find_events(
        events,
        [
            "api",
            "http 500",
            "application",
            "payment"
        ]
    )

    infrastructure_events = find_events(
        events,
        [
            "restart",
            "server",
            "infrastructure"
        ]
    )

    critical_events = [
        event
        for event in events
        if event.get("severity") == "critical"
    ]

    hypotheses = []

    # ========================================================
    # H1 - DATABASE / MIGRATION
    # ========================================================

    if database_events:

        supporting = event_ids(
            database_events
        )

        hypotheses.append({

            "id": "H1",

            "title":
                "Database Performance or Migration Issue",

            "description": (
                "Database migration or database-related activity "
                "may have caused increased latency, connection "
                "timeouts, and downstream application failures."
            ),

            "confidence": 0.65,

            "reasoning": (
                "Database migration completed shortly before "
                "database connection latency increased. The "
                "latency was followed by a connection timeout "
                "and downstream API failures, making a "
                "database-related issue the strongest current "
                "hypothesis."
            ),

            "supporting_evidence": [
                x
                for x in supporting
                if x in valid_ids
            ],

            "contradicting_evidence": [],

            "insufficient_evidence_notes": (
                "Database metrics, query performance data, "
                "schema changes, lock information, connection "
                "pool metrics, CPU, memory, and disk metrics "
                "are required to confirm the exact root cause."
            )
        })

    # ========================================================
    # H2 - APPLICATION DEPLOYMENT
    # ========================================================

    if deployment_events:

        supporting = event_ids(
            deployment_events
        )

        hypotheses.append({

            "id": "H2",

            "title":
                "Application Defect Introduced During Deployment",

            "description": (
                "The deployment may have introduced an "
                "application problem affecting database "
                "connectivity, request handling, or resource usage."
            ),

            "confidence": 0.40,

            "reasoning": (
                "A deployment completed before the incident "
                "symptoms appeared. However, the available "
                "evidence does not directly demonstrate that "
                "the deployed application code caused the "
                "database degradation."
            ),

            "supporting_evidence": [
                x
                for x in supporting
                if x in valid_ids
            ],

            "contradicting_evidence": [],

            "insufficient_evidence_notes": (
                "Deployment commit details, application stack "
                "traces, connection pool metrics, database "
                "query metrics, and application performance "
                "metrics are required."
            )
        })

    # ========================================================
    # H3 - INDEPENDENT INFRASTRUCTURE
    # ========================================================

    infrastructure_support = remove_duplicates(
        database_events
        + application_events
        + critical_events
    )

    if infrastructure_support:

        supporting = event_ids(
            infrastructure_support
        )

        hypotheses.append({

            "id": "H3",

            "title":
                "Independent Infrastructure Degradation",

            "description": (
                "An underlying database, network, host, or "
                "infrastructure problem may have caused the "
                "connection failures independently of the "
                "deployment or migration."
            ),

            "confidence": 0.25,

            "reasoning": (
                "The logs show database connection problems "
                "followed by application and payment failures. "
                "However, there is insufficient infrastructure "
                "telemetry to determine whether the degradation "
                "was independent of the release activities."
            ),

            "supporting_evidence": [
                x
                for x in supporting
                if x in valid_ids
            ],

            "contradicting_evidence": [],

            "insufficient_evidence_notes": (
                "Infrastructure health metrics, network logs, "
                "database host metrics, CPU, memory, disk, "
                "network latency, and connection statistics "
                "are required."
            )
        })

    print(
        f"Local hypothesis generation complete: "
        f"{len(hypotheses)} hypotheses."
    )

    return {
        "source": "local",
        "hypotheses": hypotheses[:4]
    }


# ============================================================
# GEMINI HYPOTHESIS GENERATION
# ============================================================

def generate_gemini_hypotheses(
    events: list[dict]
) -> dict:

    evidence = []

    for event in events:

        evidence.append({
            "event_id": event.get("event_id"),
            "timestamp": event.get("timestamp"),
            "source": event.get("source"),
            "event": event.get("event"),
            "type": event.get("type"),
            "severity": event.get("severity")
        })

    prompt = f"""
You are the hypothesis engine of an AI incident investigator.

Analyze the incident events and generate 2-4 competing
hypotheses.

RULES:

1. Use ONLY the provided events.
2. Do not assume any hypothesis is true.
3. Every evidence reference MUST be an event_id.
4. Never invent event IDs.
5. Never use evidence_id in evidence arrays.
6. Confidence must be between 0 and 1.
7. Confidence represents evidence strength, not certainty.
8. Every hypothesis MUST contain "id".
9. IDs MUST be H1, H2, H3, etc.
10. Never use "hypothesis_id" inside hypotheses.
11. An event cannot appear in both evidence arrays.
12. Do not classify recovery actions such as "Service restarted"
    as contradicting evidence unless they genuinely contradict
    the hypothesis.
13. If evidence is insufficient, explicitly say so.
14. Do not claim a definitive root cause.
15. Return ONLY valid JSON.

FORMAT:

{{
    "hypotheses": [
        {{
            "id": "H1",
            "title": "Short title",
            "description": "Explanation",
            "confidence": 0.65,
            "reasoning": "Reasoning",
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "insufficient_evidence_notes": "Missing evidence"
        }}
    ]
}}

INCIDENT EVENTS:

{json.dumps(evidence, indent=2)}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response"
        )

    return json.loads(
        response.text
    )


# ============================================================
# VALIDATE GEMINI RESULT
# ============================================================

def validate_hypotheses(
    result: dict,
    events: list[dict]
) -> dict:

    valid_event_ids = {
        event.get("event_id")
        for event in events
        if event.get("event_id")
    }

    normalized = []

    raw_hypotheses = result.get(
        "hypotheses",
        []
    )

    if not isinstance(
        raw_hypotheses,
        list
    ):
        return {
            "hypotheses": []
        }

    for index, hypothesis in enumerate(
        raw_hypotheses[:4],
        start=1
    ):

        if not isinstance(
            hypothesis,
            dict
        ):
            continue

        hypothesis_id = (
            hypothesis.get("id")
            or hypothesis.get("hypothesis_id")
            or f"H{index}"
        )

        supporting = hypothesis.get(
            "supporting_evidence",
            []
        )

        contradicting = hypothesis.get(
            "contradicting_evidence",
            []
        )

        if not isinstance(
            supporting,
            list
        ):
            supporting = []

        if not isinstance(
            contradicting,
            list
        ):
            contradicting = []

        supporting = [
            str(x)
            for x in supporting
            if str(x) in valid_event_ids
        ]

        contradicting = [
            str(x)
            for x in contradicting
            if str(x) in valid_event_ids
        ]

        # Same event cannot support and contradict
        contradicting = [
            x
            for x in contradicting
            if x not in supporting
        ]

        try:

            confidence = float(
                hypothesis.get(
                    "confidence",
                    0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            confidence = 0.0

        confidence = max(
            0.0,
            min(
                1.0,
                confidence
            )
        )

        normalized.append({

            "id":
                str(hypothesis_id),

            "title":
                str(
                    hypothesis.get(
                        "title",
                        "Unnamed hypothesis"
                    )
                ),

            "description":
                str(
                    hypothesis.get(
                        "description",
                        ""
                    )
                ),

            "confidence":
                confidence,

            "reasoning":
                str(
                    hypothesis.get(
                        "reasoning",
                        ""
                    )
                ),

            "supporting_evidence":
                supporting,

            "contradicting_evidence":
                contradicting,

            "insufficient_evidence_notes":
                str(
                    hypothesis.get(
                        "insufficient_evidence_notes",
                        ""
                    )
                )
        })

    return {
        "hypotheses": normalized
    }


# ============================================================
# MAIN HYPOTHESIS ENGINE
# ============================================================

def generate_hypotheses(
    events: list[dict]
) -> dict:

    if not events:

        return {
            "source": "local",
            "hypotheses": []
        }

    # ========================================================
    # TRY GEMINI ONCE
    # ========================================================

    try:

        print(
            "Attempting Gemini hypothesis generation..."
        )

        result = generate_gemini_hypotheses(
            events
        )

        result = validate_hypotheses(
            result,
            events
        )

        if result["hypotheses"]:

            print(
                "Gemini hypothesis generation successful."
            )

            return {
                "source": "gemini",
                "hypotheses":
                    result["hypotheses"]
            }

        print(
            "Gemini returned no valid hypotheses."
        )

    except Exception as error:

        error_code = getattr(
            error,
            "code",
            None
        )

        error_text = str(error)

        print(
            f"Gemini hypothesis generation failed: "
            f"{error}"
        )

        # ----------------------------------------------------
        # 429 QUOTA
        # ----------------------------------------------------

        if (
            error_code == 429
            or "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
        ):

            print(
                "Gemini quota exhausted."
            )

        # ----------------------------------------------------
        # 503
        # ----------------------------------------------------

        elif (
            error_code == 503
            or "503" in error_text
            or "UNAVAILABLE" in error_text
        ):

            print(
                "Gemini temporarily unavailable."
            )

        else:

            print(
                "Gemini unavailable."
            )

    # ========================================================
    # LOCAL FALLBACK
    # ========================================================

    print(
        "Using local hypothesis engine."
    )

    result = generate_local_hypotheses(
        events
    )

    return {
        "source": "local",
        "hypotheses": result.get(
            "hypotheses",
            []
        )
    }