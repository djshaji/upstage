"""
Dual-Stream Epistemic Knowledge Store for Upstage.
"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Proposition:
    subject: str
    predicate: str
    obj: str
    line_introduced: int
    witnesses: Set[str]
    is_spoiler: bool = False
    spoiler_topic: Optional[str] = None


class DualStreamEpistemicStore:
    def __init__(self, donor_character_id: str, donor_priors: Optional[List[str]] = None):
        self.donor_character_id = donor_character_id.lower()
        self.donor_priors: List[str] = donor_priors or [
            "Sir John Falstaff is an old, corpulent knight who frequents the Boar's Head Tavern in Eastcheap.",
            "Falstaff has a close, riotous companionship with Prince Hal (Harry Monmouth).",
            "Falstaff values sack (Spanish white wine), roasted capons, sugar, and warm beds above all things.",
            "Falstaff holds an infamous catechism debunking military honour: honour cannot set a broken leg.",
            "Falstaff owes debts to Mistress Quickly and borrows money from anyone he can bamboozle.",
            "Falstaff despises cold water, marching on foot, and unnecessary peril."
        ]
        self.target_propositions: List[Proposition] = []
        self.known_spoilers: Dict[str, List[str]] = {
            "cordelia_death": ["cordelia", "hanged", "dead in arms", "prison murder"],
            "gloucester_blinding": ["gloucester", "eyes plucked", "blind", "cornwall gouged"],
            "edmund_treason": ["edmund", "forged letter", "betrayed edgar", "gloucester title"],
            "daughters_poison": ["goneril", "poisoned regan", "suicide", "dagger"],
            "lear_death": ["lear dies", "heart breaks", "dead king"]
        }

    def register_target_proposition(
        self,
        subject: str,
        predicate: str,
        obj: str,
        line_introduced: int,
        witnesses: Set[str],
        is_spoiler: bool = False,
        spoiler_topic: Optional[str] = None
    ):
        self.target_propositions.append(
            Proposition(
                subject=subject,
                predicate=predicate,
                obj=obj,
                line_introduced=line_introduced,
                witnesses={w.lower() for w in witnesses},
                is_spoiler=is_spoiler,
                spoiler_topic=spoiler_topic
            )
        )

    def get_accessible_target_knowledge(self, current_line: int) -> List[str]:
        accessible = []
        for prop in self.target_propositions:
            if prop.line_introduced <= current_line:
                if self.donor_character_id in prop.witnesses:
                    accessible.append(f"{prop.subject} {prop.predicate} {prop.obj}")
        return accessible

    def get_full_epistemic_context(self, current_line: int) -> Dict[str, List[str]]:
        return {
            "donor_priors": list(self.donor_priors),
            "witnessed_target_facts": self.get_accessible_target_knowledge(current_line)
        }

    def check_narrative_leakage(self, generated_text: str, current_line: int) -> Tuple[bool, List[str]]:
        text_lower = generated_text.lower()
        violations = []
        for topic, keywords in self.known_spoilers.items():
            matched_count = sum(1 for kw in keywords if kw in text_lower)
            if matched_count >= 2:
                violations.append(f"Forbidden spoiler leakage: '{topic}' detected in text.")
        for prop in self.target_propositions:
            if prop.is_spoiler or prop.line_introduced > current_line or (self.donor_character_id not in prop.witnesses):
                fact_tokens = [prop.subject.lower(), prop.obj.lower()]
                if all(tok in text_lower for tok in fact_tokens if len(tok) > 3):
                    violations.append(
                        f"Unwitnessed target fact leakage: '{prop.subject} {prop.predicate} {prop.obj}'"
                    )
        return (len(violations) > 0, violations)
