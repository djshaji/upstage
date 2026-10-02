"""
Stage Presence Tracker for Upstage.
"""

from typing import List, Dict, Set, Optional
from upstage.src.dramaturgy.models import StageEvent


class StagePresenceTracker:
    def __init__(self, stage_events: Optional[List[Dict]] = None):
        self.events: List[StageEvent] = []
        if stage_events:
            for ev in stage_events:
                self.add_event(
                    line_number=ev["line_number"],
                    event_type=ev["event_type"],
                    characters=ev["characters"],
                    description=ev.get("description", "")
                )

    def add_event(self, line_number: int, event_type: str, characters: List[str], description: str = ""):
        self.events.append(
            StageEvent(
                line_number=line_number,
                event_type=event_type.upper(),
                characters=[c.lower() for c in characters],
                description=description
            )
        )
        self.events.sort(key=lambda x: x.line_number)

    def get_witnesses_at_line(self, query_line: int) -> Set[str]:
        active_characters: Set[str] = set()
        for ev in self.events:
            if ev.line_number > query_line:
                break
            if ev.event_type == "ENTER":
                for c in ev.characters:
                    active_characters.add(c)
            elif ev.event_type in ("EXIT", "EXEUNT"):
                if ev.characters:
                    for c in ev.characters:
                        active_characters.discard(c)
                else:
                    active_characters.clear()
        return active_characters

    def is_present(self, character_id: str, line_number: int) -> bool:
        witnesses = self.get_witnesses_at_line(line_number)
        return character_id.lower() in witnesses

    def build_witness_lookup_table(self, max_line: int = 2000) -> Dict[int, Set[str]]:
        lookup = {}
        for line in range(1, max_line + 1):
            lookup[line] = self.get_witnesses_at_line(line)
        return lookup
