"""
Slot Excision and Actantial Intent Mapper for Upstage.
"""

from typing import List, Dict, Optional, Set
from upstage.src.dramaturgy.models import (
    SpeechTurn, ExcisedSlot, ActantialIntent, CharacterProfile
)


class SlotMapper:
    def __init__(self, donor_profile: CharacterProfile):
        self.donor_profile = donor_profile

    @staticmethod
    def infer_actantial_intent(text: str) -> ActantialIntent:
        text_lower = text.lower()
        if any(w in text_lower for w in ["sing", "rhyme", "song", "wind and the rain"]):
            return ActantialIntent.RIDDLE_PARADOX
        if any(w in text_lower for w in ["coxcomb", "riddle", "fool", "wit"]):
            return ActantialIntent.RIDDLE_PARADOX
        if any(w in text_lower for w in ["thou hast pared", "madest thy daughters", "give away", "folly"]):
            return ActantialIntent.ADMONITION
        if any(w in text_lower for w in ["blow, wind", "puddle", "weep", "shiver", "cold"]):
            return ActantialIntent.CHORIC_LAMENT
        if any(w in text_lower for w in ["what is", "why", "honour", "nature", "justice"]):
            return ActantialIntent.PHILOSOPHICAL_INQUIRY
        if any(w in text_lower for w in ["drink", "cup", "sack", "sherris", "welcome", "friend"]):
            return ActantialIntent.SOCIABILITY_BONDING
        if any(w in text_lower for w in ["run", "hide", "fly", "cold night", "house", "shelter"]):
            return ActantialIntent.EVASION_SELF_PRESERVATION
        return ActantialIntent.COMIC_DEFLECTION

    def excise_character_slots(
        self,
        scene_turns: List[SpeechTurn],
        target_character_id: str,
        witness_lookup: Optional[Dict[int, Set[str]]] = None,
        context_window: int = 4
    ) -> List[ExcisedSlot]:
        excised_slots = []
        for i, turn in enumerate(scene_turns):
            if turn.speaker_id.lower() == target_character_id.lower():
                preceding = scene_turns[max(0, i - context_window):i]
                interlocutor = preceding[-1].speaker_id if preceding else None
                witnesses = witness_lookup.get(turn.line_start, set()) if witness_lookup else set()
                intent = turn.actantial_intent or self.infer_actantial_intent(turn.text)

                slot = ExcisedSlot(
                    target_character_id=target_character_id,
                    turn_id=turn.turn_id,
                    act=turn.act,
                    scene=turn.scene,
                    line_index=turn.line_start,
                    original_text=turn.text,
                    original_intent=intent,
                    interlocutor_id=interlocutor,
                    active_witnesses=witnesses,
                    preceding_context=preceding
                )
                excised_slots.append(slot)
        return excised_slots

    def project_intent_to_donor(self, slot: ExcisedSlot) -> Dict[str, str]:
        intent = slot.original_intent
        donor_name = self.donor_profile.canonical_name

        if "falstaff" in donor_name.lower():
            transposition_rules = {
                ActantialIntent.ADMONITION: (
                    "Reframe admonition through materialist common sense: chastise Lear not for "
                    "sacred majesty broken, but for the catastrophic blunder of parting with his rent, "
                    "land, and cellar. He who gives his meat to others must go begging for bones."
                ),
                ActantialIntent.RIDDLE_PARADOX: (
                    "Replace cryptic riddles with expansive, mock-solemn parables and tavern syllogisms. "
                    "Use mock-legal reasoning and hyperbole to demonstrate that an abdicated king "
                    "is less substantial than a bladder of lard without tallow."
                ),
                ActantialIntent.CHORIC_LAMENT: (
                    "Transform ascetic lamentation into visceral protest against physical misery: "
                    "rail against the wet heath, curse cold rain that dilutes a man's liver, "
                    "and insist that any hovel with dry straw and a cup of sack outshines heroic majesty."
                ),
                ActantialIntent.COMIC_DEFLECTION: (
                    "Employ brazen evasions, witty self-deprecation, and sudden comic reversals. "
                    "Feign injury, plead age and gross belly, and deflect royal rage into tavern mirth."
                ),
                ActantialIntent.EVASION_SELF_PRESERVATION: (
                    "Unabashed defense of cowardice as discretion: mock martyrdom, question the value "
                    "of freezing to death for pride, and demand an immediate retreat to dry shelter."
                ),
                ActantialIntent.PHILOSOPHICAL_INQUIRY: (
                    "Deliver a catechism on kingship akin to the catechism on honour: what is majesty? "
                    "Can majesty warm a cold knee? Can a crown fend off the rheum? No."
                ),
                ActantialIntent.SOCIABILITY_BONDING: (
                    "Attempt to induct the brooding Lear into the fraternity of old topers: offer imaginary "
                    "sherris-sack and propose that both of them are wronged gentlemen betrayed by ungrateful young knaves."
                ),
                ActantialIntent.DISPUTE_REPROACH: (
                    "Defend personal nobility with wounded pride: remind the company that Sir John is a gentleman "
                    "of ancient house, not a capering fool to be scolded by surly dukes or ill-tempered daughters."
                )
            }
            guidance = transposition_rules.get(
                intent,
                "Respond with Falstaffian wit, prioritizing bodily preservation, dry warmth, and witty self-interest."
            )
        else:
            guidance = f"Project {intent.value} through {donor_name}'s idiosyncratic dramatic worldview."

        return {
            "original_intent": intent.value,
            "projected_guidance": guidance,
            "donor_voice": donor_name,
            "target_role": slot.target_character_id
        }
