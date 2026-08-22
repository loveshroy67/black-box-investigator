from typing import List

from app.models.schemas import EvidenceEvent


def build_timeline(events: List[dict]) -> List[dict]:
    """
    Sort investigation events chronologically.
    """

    valid_events = [
        event
        for event in events
        if event.get("timestamp") is not None
    ]

    valid_events.sort(
        key=lambda event: event["timestamp"]
    )

    return valid_events