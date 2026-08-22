import json
import re
import time
import uuid

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
# LOCAL EVENT CLASSIFICATION
# ============================================================

def classify_event(event_text: str, level: str) -> tuple[str, str]:

    text = event_text.lower()

    # Severity
    if level == "error":
        if any(word in text for word in [
            "payment service unavailable",
            "service unavailable",
            "critical"
        ]):
            severity = "critical"
        else:
            severity = "high"

    elif level == "warn":
        severity = "medium"

    else:
        severity = "info"

    # Event type
    if any(word in text for word in [
        "deployment",
        "deploy"
    ]):
        event_type = "deployment"

    elif any(word in text for word in [
        "database",
        "migration",
        "sql",
        "connection"
    ]):
        event_type = "database"

    elif any(word in text for word in [
        "api",
        "http",
        "500",
        "request"
    ]):
        event_type = "application"

    elif any(word in text for word in [
        "restart",
        "server",
        "infrastructure"
    ]):
        event_type = "infrastructure"

    else:
        event_type = "other"

    return event_type, severity


# ============================================================
# LOCAL LOG PARSER
# ============================================================

def local_extract_events(
    text: str,
    filename: str
) -> dict:

    events = []

    # Supports:
    #
    # 2026-08-21 09:41:02 INFO Deployment completed
    #
    # and:
    #
    # 2026-08-21T09:41:02Z ERROR Something happened

    pattern = re.compile(
        r"^"
        r"(\d{4}-\d{2}-\d{2})"
        r"[ T]"
        r"(\d{2}:\d{2}:\d{2})"
        r"(?:Z)?"
        r"\s+"
        r"(INFO|WARN|WARNING|ERROR|CRITICAL|DEBUG)"
        r"\s+"
        r"(.*)"
        r"$",
        re.IGNORECASE
    )

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        match = pattern.match(line)

        if not match:
            continue

        date_part = match.group(1)
        time_part = match.group(2)
        level = match.group(3).upper()
        message = match.group(4).strip()

        timestamp = f"{date_part}T{time_part}Z"

        normalized_level = level.lower()

        if normalized_level == "warning":
            normalized_level = "warn"

        event_type, severity = classify_event(
            message,
            normalized_level
        )

        events.append({
            "event_id": str(uuid.uuid4()),
            "timestamp": timestamp,
            "source": filename,
            "event": message,
            "type": event_type,
            "severity": severity
        })

    return {
        "events": events
    }


# ============================================================
# GEMINI EXTRACTION
# ============================================================

def gemini_extract_events(
    text: str,
    filename: str
) -> dict:

    prompt = f"""
You are the event extraction engine of an AI incident investigator.

Extract structured incident events from the provided log.

RULES:

1. Extract only events explicitly present in the log.
2. Do not invent events.
3. Preserve timestamps.
4. Preserve the original event meaning.
5. Generate one unique event_id for every event.
6. event_id must be a UUID string.
7. source must be "{filename}".
8. type must be one of:
   deployment
   database
   application
   infrastructure
   security
   network
   other
9. severity must be one of:
   info
   medium
   high
   critical
10. Return ONLY valid JSON.
11. The JSON must have this structure:

{{
    "events": [
        {{
            "event_id": "uuid",
            "timestamp": "ISO-8601 timestamp",
            "source": "{filename}",
            "event": "event description",
            "type": "database",
            "severity": "high"
        }}
    ]
}}

LOG:

{text}
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

    result = json.loads(response.text)

    if "events" not in result:
        raise ValueError(
            "Gemini response does not contain 'events'"
        )

    return result


# ============================================================
# MAIN EVENT EXTRACTION
# ============================================================

def extract_events(
    text: str,
    filename: str
) -> dict:

    if not text or not text.strip():
        return {
            "events": []
        }

    # --------------------------------------------------------
    # Try Gemini
    # --------------------------------------------------------

    for attempt in range(2):

        try:

            print(
                f"Gemini event extraction "
                f"attempt {attempt + 1}/2"
            )

            result = gemini_extract_events(
                text,
                filename
            )

            # Validate returned events
            valid_events = []

            for event in result.get("events", []):

                if not event.get("event_id"):
                    event["event_id"] = str(uuid.uuid4())

                if not event.get("timestamp"):
                    continue

                if not event.get("source"):
                    event["source"] = filename

                if not event.get("event"):
                    continue

                if not event.get("type"):
                    event["type"] = "other"

                if not event.get("severity"):
                    event["severity"] = "info"

                valid_events.append(event)

            return {
                "events": valid_events
            }

        except Exception as error:

            error_code = getattr(error, "code", None)

            error_text = str(error)

            print(
                f"Gemini event extraction failed: {error}"
            )

            # ------------------------------------------------
            # 429 = quota exhausted
            #
            # DO NOT RETRY.
            # Switch immediately to local parser.
            # ------------------------------------------------

            if (
                error_code == 429
                or "RESOURCE_EXHAUSTED" in error_text
                or "quota" in error_text.lower()
            ):

                print(
                    "Gemini quota exhausted. "
                    "Using local event extraction."
                )

                break

            # ------------------------------------------------
            # 503 = temporary Gemini problem
            # Retry once.
            # ------------------------------------------------

            if (
                error_code == 503
                or "503" in error_text
                or "UNAVAILABLE" in error_text
            ):

                if attempt < 1:

                    print(
                        "Gemini temporarily unavailable. "
                        "Retrying in 2 seconds..."
                    )

                    time.sleep(2)

                    continue

                break

            # ------------------------------------------------
            # Other Gemini errors
            #
            # Don't kill evidence upload.
            # Fall back to local parser.
            # ------------------------------------------------

            break

    # ========================================================
    # LOCAL FALLBACK
    # ========================================================

    print(
        "Using local log parser as fallback."
    )

    result = local_extract_events(
        text,
        filename
    )

    print(
        f"Local parser extracted "
        f"{len(result['events'])} events."
    )

    return result