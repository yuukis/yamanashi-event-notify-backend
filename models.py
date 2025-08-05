from typing import Optional
from dataclasses import dataclass


@dataclass
class Event:
    uid: str
    title: str
    event_url: str
    started_at: str

    @staticmethod
    def from_json(json: dict):
        events = []

        for item in json:
            events.append(
                Event(
                    uid=item["uid"],
                    title=item["title"],
                    event_url=item["event_url"],
                    started_at=item["started_at"],
                )
            )
        return events
