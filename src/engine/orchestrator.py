"""
Dialogue Orchestration Engine for Upstage.
"""

from typing import Dict, Any, List
from upstage.src.dramaturgy.models import ExcisedSlot, CharacterProfile
from upstage.src.dramaturgy.slot_mapper import SlotMapper
from upstage.src.kg.epistemic_store import DualStreamEpistemicStore


class UpstageOrchestrator:
    def __init__(
        self,
        donor_profile: CharacterProfile,
        epistemic_store: DualStreamEpistemicStore,
        slot_mapper: SlotMapper,
        exemplars: List[Dict[str, str]] = None
    ):
        self.donor_profile = donor_profile
        self.epistemic_store = epistemic_store
        self.slot_mapper = slot_mapper
        self.exemplars = exemplars or []

    def construct_synthesis_prompt(self, slot: ExcisedSlot) -> Dict[str, Any]:
        projected = self.slot_mapper.project_intent_to_donor(slot)
        epistemic_context = self.epistemic_store.get_full_epistemic_context(slot.line_index)
        dialogue_history = []
        for prev in slot.preceding_context[-3:]:
            dialogue_history.append(f"{prev.speaker_id.upper()}: {prev.text}")

        system_instruction = (
            f"You are {self.donor_profile.canonical_name}, transplanted from your native play "
            f"({self.donor_profile.native_play}) into the target drama at Act {slot.act}, Scene {slot.scene}.\n"
            f"Social Status: {self.donor_profile.social_rank}.\n"
            f"Philosophical Core: {self.donor_profile.philosophical_core}.\n"
            f"Dominant Form: {self.donor_profile.dominant_meter.value}.\n"
            f"Rules of Dramatic Engagement:\n"
            f"1. You speak strictly in authentic Early Modern English (c. 1590-1610). No modern idioms.\n"
            f"2. You possess NO omniscient knowledge of this tragedy's plot, murders, or ending.\n"
            f"3. You must fulfill the structural dramatic slot vacated by {slot.target_character_id.upper()},\n"
            f"   reinterpreted through your own voice: {projected['projected_guidance']}\n"
            f"4. Maintain your characteristic wit: mock-biblical allusions, self-defense of gross belly,\n"
            f"   contempt for cold water and empty honour, and love of sack and warm fires."
        )

        user_prompt = (
            f"TARGET DRAMATIC SLOT TO FILL:\n"
            f"- Original Speaker: {slot.target_character_id.upper()}\n"
            f"- Original Intent: {slot.original_intent.value}\n"
            f"- Active Stage Witnesses: {', '.join(sorted(slot.active_witnesses)) or 'None recorded'}\n"
            f"- Immediate Interlocutor: {slot.interlocutor_id.upper() if slot.interlocutor_id else 'General Stage'}\n\n"
            f"RECENT DIALOGUE LEADING TO YOUR TURN:\n" + "\n".join(dialogue_history) + "\n\n"
            f"YOUR WITNESSED FACTS SO FAR IN THIS PLAY:\n" +
            ("\n".join(f"- {f}" for f in epistemic_context["witnessed_target_facts"]) or "- Just arrived on stage; no prior plot witnessed.") + "\n\n"
            f"FALSTAFFIAN TRANSFORMATION TASK:\n"
            f"Deliver Sir John Falstaff's turn in this slot. Respond to {slot.interlocutor_id or 'the stage'}."
        )

        return {
            "system_instruction": system_instruction,
            "user_prompt": user_prompt,
            "projected_intent": projected,
            "epistemic_bounds": epistemic_context,
            "slot_id": slot.turn_id
        }
