"""
Unit and Integration Test Suite for Live LLM Inference Integration in Upstage.
Tests:
1. Four-Tier Prompt Envelope Construction
2. Provider Client Response Generation (Falstaff, Iago, Viola, Lady Macbeth)
3. Critic-Reflection Loop & Self-Healing Runtime Audits
4. End-to-End Live Transplantation with Stylometric & Epistemic Verification
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))
import src as upstage
sys.modules['upstage'] = upstage
sys.modules['upstage.src'] = upstage

from upstage.src.dramaturgy.models import (
    CharacterProfile, ExcisedSlot, ActantialIntent, MeterType, SpeechTurn
)
from upstage.src.kg.epistemic_store import DualStreamEpistemicStore
from upstage.src.dramaturgy.slot_mapper import SlotMapper
from upstage.src.engine.stylometrics import StylometricEngine
from upstage.src.engine.register_filter import RegisterFilter
from llm_inference_engine import (
    BaseLLMClient, MockLocalLLMClient, PromptEnvelopeBuilder,
    LiveLLMTransplantationEngine, AuditReport
)


class TestLiveLLMInferenceIntegration(unittest.TestCase):

    def setUp(self):
        self.donor_profile = CharacterProfile(
            character_id="falstaff",
            canonical_name="Sir John Falstaff",
            native_play="Henry IV",
            social_rank="Knight (impoverished)",
            dominant_meter=MeterType.PROSE,
            typical_pronominal_form="V (You) to Royalty; T (Thou) to intimates/subordinates",
            philosophical_core="Hedonistic bodily survivalism, contempt for empty honour, love of sack & wit",
            rhetorical_signature=["euphuistic parataxis", "mock-biblical allusion", "hyperbolic self-justification"],
            favorite_lexicon=["sack", "capon", "belly", "knave", "villanous", "honour", "rogue"]
        )
        self.epistemic_store = DualStreamEpistemicStore("falstaff")
        self.slot_mapper = SlotMapper(self.donor_profile)
        self.stylometric_engine = StylometricEngine()
        self.register_filter = RegisterFilter()

        self.slot = ExcisedSlot(
            target_character_id="fool",
            turn_id="KL_1_4_t1",
            act=1,
            scene=4,
            line_index=96,
            original_text="Let me hire him too: here's my coxcomb.",
            original_intent=ActantialIntent.RIDDLE_PARADOX,
            interlocutor_id="lear",
            active_witnesses={"lear", "kent", "fool"},
            preceding_context=[
                SpeechTurn(
                    turn_id="KL_1_4_pre", play_id="king_lear", act=1, scene=4,
                    line_start=90, line_end=95, speaker_id="lear",
                    text="Follow me; thou shalt serve me: if I like thee no worse after dinner.",
                    meter_type=MeterType.PROSE
                )
            ]
        )

    def test_prompt_envelope_builder(self):
        guidance = self.slot_mapper.project_intent_to_donor(self.slot)["projected_guidance"]
        messages = PromptEnvelopeBuilder.build_envelope(
            donor_profile=self.donor_profile,
            epistemic_store=self.epistemic_store,
            slot=self.slot,
            transposition_guidance=guidance,
            current_line=96
        )

        self.assertEqual(len(messages), 2)
        system_msg = messages[0]["content"]
        user_msg = messages[1]["content"]

        self.assertIn("Sir John Falstaff", system_msg)
        self.assertIn("Hedonistic bodily survivalism", system_msg)
        self.assertIn("EPISTEMIC BOUNDARY CONSTRAINTS", user_msg)
        self.assertIn("FORBIDDEN SPOILERS", user_msg)
        self.assertIn("Let me hire him too", user_msg)
        self.assertIn("ZERO modern vocabulary", user_msg)

    def test_mock_llm_multi_donor_generation(self):
        f_client = MockLocalLLMClient("falstaff")
        f_res = f_client.generate([{"role": "user", "content": "hire him and coxcomb"}])
        self.assertIn("sack", f_res.lower())

        i_client = MockLocalLLMClient("iago")
        i_res = i_client.generate([{"role": "user", "content": "fishmonger and honesty"}])
        self.assertIn("fishmonger", i_res.lower())

        v_client = MockLocalLLMClient("viola")
        v_res = v_client.generate([{"role": "user", "content": "the quality of mercy"}])
        self.assertIn("mercy", v_res.lower())

        lm_client = MockLocalLLMClient("lady_macbeth")
        lm_res = lm_client.generate([{"role": "user", "content": "sword and bared bosom"}])
        self.assertIn("infirm of purpose", lm_res.lower())

    def test_live_engine_clean_turn_execution(self):
        client = MockLocalLLMClient("falstaff")
        engine = LiveLLMTransplantationEngine(
            llm_client=client,
            donor_profile=self.donor_profile,
            epistemic_store=self.epistemic_store,
            slot_mapper=self.slot_mapper,
            stylometric_engine=self.stylometric_engine,
            register_filter=self.register_filter,
            donor_reference_corpus="Give me a cup of sack, boy! Honour is a word.",
            target_reference_corpus="Truth's a dog must to kennel; court holy-water."
        )

        turn_text, report = engine.generate_turn(self.slot)
        self.assertTrue(report.passed)
        self.assertEqual(len(report.epistemic_violations), 0)
        self.assertEqual(len(report.anachronisms), 0)
        self.assertIn("sack", turn_text.lower())

    def test_adversarial_critic_reflection_loop(self):
        class FlawedThenHealedClient(BaseLLMClient):
            def __init__(self):
                self.calls = 0

            def generate(self, messages, temperature=0.7, max_tokens=500):
                self.calls += 1
                user_content = messages[-1]["content"]
                if "CRITIQUE & REVISION REQUIRED" in user_content:
                    return "Nay, call me Sir John! Give me a cup of sack, and let this knave hold my horse."
                return "This is basic psychology, sir, and Cordelia is dead in arms!"

        engine = LiveLLMTransplantationEngine(
            llm_client=FlawedThenHealedClient(),
            donor_profile=self.donor_profile,
            epistemic_store=self.epistemic_store,
            slot_mapper=self.slot_mapper,
            stylometric_engine=self.stylometric_engine,
            register_filter=self.register_filter,
            donor_reference_corpus="Give me a cup of sack, boy!",
            target_reference_corpus="Truth's a dog must to kennel."
        )

        turn_text, report = engine.generate_turn(self.slot)

        self.assertEqual(report.reflection_count, 1)
        self.assertTrue(report.passed)
        self.assertNotIn("psychology", turn_text.lower())
        self.assertNotIn("cordelia", turn_text.lower())
        self.assertIn("sack", turn_text.lower())


if __name__ == "__main__":
    unittest.main()
