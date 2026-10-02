"""
Unit and Integration Test Suite for the Upstage Core Python Engine.
"""

import sys
import json
import unittest
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
import src as upstage
sys.modules['upstage'] = upstage
sys.modules['upstage.src'] = upstage

from upstage.src.dramaturgy.models import MeterType, ActantialIntent
from upstage.src.dramaturgy.slot_mapper import SlotMapper
from upstage.src.kg.stage_tracker import StagePresenceTracker
from upstage.src.kg.epistemic_store import DualStreamEpistemicStore
from upstage.src.engine.stylometrics import StylometricEngine
from upstage.src.engine.register_filter import RegisterFilter
from upstage.src.engine.simulator import UpstageSimulator


class TestUpstageEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_dir = root_dir / "data"
        with open(data_dir / "king_lear_sample.json", "r", encoding="utf-8") as f:
            cls.target_data = json.load(f)
        with open(data_dir / "falstaff_corpus.json", "r", encoding="utf-8") as f:
            cls.donor_data = json.load(f)

    def test_stage_presence_tracker(self):
        tracker = StagePresenceTracker(self.target_data["stage_events"])

        # Line 5: Only Kent on stage
        witnesses_l5 = tracker.get_witnesses_at_line(5)
        self.assertIn("kent", witnesses_l5)
        self.assertNotIn("lear", witnesses_l5)

        # Line 10: Lear and Kent on stage
        witnesses_l10 = tracker.get_witnesses_at_line(10)
        self.assertIn("lear", witnesses_l10)
        self.assertIn("kent", witnesses_l10)
        self.assertNotIn("fool", witnesses_l10)

        # Line 100: Fool has entered
        witnesses_l100 = tracker.get_witnesses_at_line(100)
        self.assertIn("fool", witnesses_l100)

    def test_epistemic_boundary_and_leakage(self):
        store = DualStreamEpistemicStore("falstaff")

        # Safe turn
        safe_turn = "Give me a cup of sack, boy! This rain will drown an old man's liver."
        has_leak, leaks = store.check_narrative_leakage(safe_turn, current_line=100)
        self.assertFalse(has_leak)
        self.assertEqual(len(leaks), 0)

        # Adversarial future spoiler turn
        adversarial_turn = "Alas, poor Lear, thy Cordelia shall be hanged in prison and Gloucester blind!"
        has_leak, leaks = store.check_narrative_leakage(adversarial_turn, current_line=100)
        self.assertTrue(has_leak)
        self.assertGreater(len(leaks), 0)

    def test_stylometrics_burrows_delta(self):
        engine = StylometricEngine()
        falstaff_sample = (
            "Give me a cup of sack, boy. A plague of all cowards! There is nothing but roguery "
            "to be found in villainous man, and one of them is fat and grows old."
        )
        donor_ref = " ".join([t["text"] for t in self.donor_data["turns"]])
        fool_ref = "Fools had ne'er less grace in a year; For wise men are grown foppish."

        all_samples = [t['text'] for t in self.donor_data['turns']] + [t['text'] for sc in self.target_data['scenes'] for t in sc['turns']]
        affinity = engine.analyze_stylometric_affinity(falstaff_sample, donor_ref, fool_ref, reference_samples=all_samples)
        self.assertIn("delta_to_donor", affinity)
        self.assertIn("delta_to_target", affinity)
        self.assertLess(affinity["delta_to_donor"], affinity["delta_to_target"])

    def test_register_and_anachronism_filter(self):
        modern_text = "Sir, thy daughter shows toxic narcissistic trauma and lacks coping mechanisms."
        anachronisms = RegisterFilter.detect_anachronisms(modern_text)
        self.assertIn("toxic", anachronisms)
        self.assertIn("narcissistic", anachronisms)
        self.assertIn("trauma", anachronisms)

        period_text = "Fie, my good lord, a cup of sherris-sack is the only sovereign cure for an old knight's sorrow."
        period_anachronisms = RegisterFilter.detect_anachronisms(period_text)
        self.assertEqual(len(period_anachronisms), 0)
        self.assertGreater(RegisterFilter.measure_falstaffian_density(period_text), 0.0)

    def test_full_scene_simulation(self):
        sim = UpstageSimulator(self.target_data, self.donor_data)

        # Act 1 Scene 4
        res_1_4 = sim.simulate_scene(act_num=1, scene_num=4)
        self.assertEqual(len(res_1_4), 4)
        for turn in res_1_4:
            self.assertTrue(turn.epistemic_check_passed, f"Epistemic leak in {turn.slot.turn_id}")
            self.assertEqual(turn.applied_meter, MeterType.PROSE)
            self.assertGreater(len(turn.generated_text), 20)

        # Act 3 Scene 2 (Storm)
        res_3_2 = sim.simulate_scene(act_num=3, scene_num=2)
        self.assertEqual(len(res_3_2), 2)
        for turn in res_3_2:
            self.assertTrue(turn.epistemic_check_passed)
            self.assertGreater(RegisterFilter.measure_falstaffian_density(turn.generated_text), 0.0)


if __name__ == "__main__":
    unittest.main()
