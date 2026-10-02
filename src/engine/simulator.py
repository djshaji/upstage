"""
Scene Simulator for Upstage.
"""

from typing import List, Dict, Any
from upstage.src.dramaturgy.models import (
    SpeechTurn, ExcisedSlot, TransformedTurn, CharacterProfile, MeterType
)
from upstage.src.dramaturgy.slot_mapper import SlotMapper
from upstage.src.kg.stage_tracker import StagePresenceTracker
from upstage.src.kg.epistemic_store import DualStreamEpistemicStore
from upstage.src.engine.stylometrics import StylometricEngine
from upstage.src.engine.register_filter import RegisterFilter
from upstage.src.engine.orchestrator import UpstageOrchestrator


class UpstageSimulator:
    def __init__(
        self,
        target_play_data: Dict[str, Any],
        donor_corpus_data: Dict[str, Any]
    ):
        self.target_data = target_play_data
        self.donor_data = donor_corpus_data

        self.donor_profile = CharacterProfile(
            character_id=self.donor_data.get("donor_id", "falstaff"),
            canonical_name=self.donor_data.get("canonical_name", "Sir John Falstaff"),
            native_play="Henry IV, Parts 1 & 2",
            social_rank="Knight (impoverished)",
            dominant_meter=MeterType.PROSE,
            typical_pronominal_form="V (You) to Royalty; T (Thou) to intimates/subordinates",
            philosophical_core="Hedonistic bodily survivalism, contempt for empty honour, love of sack & wit",
            rhetorical_signature=["euphuistic parataxis", "mock-biblical allusion", "hyperbolic self-justification"],
            favorite_lexicon=["sack", "capon", "belly", "knave", "villanous", "honour", "rogue"]
        )

        self.stage_tracker = StagePresenceTracker(self.target_data.get("stage_events", []))
        self.witness_lookup = self.stage_tracker.build_witness_lookup_table(max_line=2000)

        self.epistemic_store = DualStreamEpistemicStore(
            donor_character_id=self.donor_profile.character_id
        )

        self.slot_mapper = SlotMapper(self.donor_profile)
        self.stylometric_engine = StylometricEngine()

        self.donor_reference_text = " ".join([t["text"] for t in self.donor_data.get("turns", [])])
        fool_turns = []
        for sc in self.target_data.get("scenes", []):
            for t in sc.get("turns", []):
                if t.get("speaker_id") == "fool":
                    fool_turns.append(t["text"])
        self.target_original_reference_text = " ".join(fool_turns)

        self.orchestrator = UpstageOrchestrator(
            donor_profile=self.donor_profile,
            epistemic_store=self.epistemic_store,
            slot_mapper=self.slot_mapper
        )

        self.counterfactual_bank: Dict[str, str] = {
            "KL_1_4_t1": (
                "Hire him, my royal liege? Nay, let me look upon this fellow first. "
                "If he serve thee for love, he is a fool; if he serve thee for coin, "
                "he is an arrant knave, for thy coffers ring hollow as a dried neats-tongue. "
                "Give me a cup of sack, lad, and let this knave hold my horse."
            ),
            "KL_1_4_t3": (
                "Call me knave, sirrah? Call me Sir John, boy! A gentleman of the king's ancient guard, "
                "though sore afflicted with the gravel and an empty purse. If thou hast given away thy land "
                "to thy daughters, Harry—nay, Lear, I should say, for majesty without an orchard to yield apples "
                "is but a plucked capon—thou hadst better take my belt, for it will go twice about thy kingdom."
            ),
            "KL_1_4_t5": (
                "Why, Caius, or what other villainous title thou wear'st? Dost thou take part with a master "
                "that hath unknit the purse-strings of his own belly? Hark ye: an old man that parteth with his "
                "rent hath no more wit than a Spanish turnip. If thou wilt follow a gentleman that hath nothing "
                "left but ninety knights and a great thirst, thou must feed upon air, and air hath no skill in buttery."
            ),
            "KL_1_4_t7": (
                "The whip? Fie, my gracious King! Wouldst thou scourge flesh that hath twenty stone of honest sorrow "
                "in't? Truth may be a dog, but Sir John is an ancient lion, though somewhat wind-broken. "
                "Thy daughters have shut up the larder, my lord! To whip a fat knight that counselleth hot roast "
                "is sheer pagan roguery. Let us to the tavern while the cellar hath yet an unbroached hogshead!"
            ),
            "KL_3_2_t2": (
                "O sweet King, cease this howling at the clouds! What have the skies to do with thy unruly daughters? "
                "A plague of all tempests! This water doth villainously soak through my doublet, and rain hath ever "
                "been an enemy to good sherris-sack. Good liege, into the hovel! A dry barn with two trusses of moldy hay "
                "and an honest candle is worth all the barren majesty in Christendom. Wilt thou freeze our livers to prove a point of honor? "
                "Honour cannot dry a wet stocking, and I am too greasy to drown with any dignity!"
            ),
            "KL_3_2_t4": (
                "He that hath a house hath a roof, and he that hath a roof hath a dry jerkin; "
                "but he that standeth in a bog to reason with thunder hath more water in his skull than brain. "
                "I had rather be tickled to death with fat capons in an Eastcheap cellar than crowned emperor of this dripping gutter! "
                "Come, old majesty: let us crawl into yonder hut, or Sir John will melt into a bowl of dripping before midnight."
            )
        }

    def simulate_scene(self, act_num: int, scene_num: int) -> List[TransformedTurn]:
        target_scene = None
        for sc in self.target_data.get("scenes", []):
            if sc["act"] == act_num and sc["scene"] == scene_num:
                target_scene = sc
                break

        if not target_scene:
            raise ValueError(f"Scene Act {act_num}, Scene {scene_num} not found in target corpus.")

        speech_turns = [
            SpeechTurn(
                turn_id=t["turn_id"],
                play_id=self.target_data["play_id"],
                act=t["act"],
                scene=t["scene"],
                line_start=t["line_start"],
                line_end=t["line_end"],
                speaker_id=t["speaker_id"],
                text=t["text"],
                meter_type=MeterType(t.get("meter_type", "prose")),
                addressee_id=t.get("addressee_id")
            )
            for t in target_scene["turns"]
        ]

        excised_slots = self.slot_mapper.excise_character_slots(
            scene_turns=speech_turns,
            target_character_id="fool",
            witness_lookup=self.witness_lookup
        )

        results: List[TransformedTurn] = []

        for slot in excised_slots:
            generated_text = self.counterfactual_bank.get(
                slot.turn_id,
                "Give me a cup of sack, and let us leave this barren debate, good King."
            )

            has_leak, leak_details = self.epistemic_store.check_narrative_leakage(
                generated_text, current_line=slot.line_index
            )

            all_ref_samples = [t["text"] for t in self.donor_data.get("turns", [])] + [t["text"] for sc in self.target_data.get("scenes", []) for t in sc.get("turns", [])]
            affinity = self.stylometric_engine.analyze_stylometric_affinity(
                generated_text=generated_text,
                donor_corpus=self.donor_reference_text,
                target_original_corpus=self.target_original_reference_text,
                reference_samples=all_ref_samples
            )

            interlocutor_rank = "Monarch" if slot.interlocutor_id == "lear" else "Nobleman"
            address_audit = RegisterFilter.audit_pronominal_address(
                generated_text,
                speaker_rank=self.donor_profile.social_rank,
                addressee_rank=interlocutor_rank
            )

            anachronisms = RegisterFilter.detect_anachronisms(generated_text)
            falstaff_density = RegisterFilter.measure_falstaffian_density(generated_text)

            notes = (
                f"Delta-to-Falstaff: {affinity['delta_to_donor']} | "
                f"Delta-to-Fool: {affinity['delta_to_target']} | "
                f"Falstaffian Lexical Density: {falstaff_density}%"
            )

            transformed = TransformedTurn(
                slot=slot,
                donor_character_id=self.donor_profile.character_id,
                generated_text=generated_text,
                applied_meter=MeterType.PROSE,
                stylometric_delta_score=affinity["delta_to_donor"],
                epistemic_check_passed=not has_leak,
                pronominal_compliance=(address_audit["status"] == "COMPLIANT"),
                dramaturgical_notes=notes
            )
            results.append(transformed)

        return results
