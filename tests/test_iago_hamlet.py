"""
Unit and Integration Test Suite for Benchmark Pair 2:
Iago (Othello) -> Polonius (Hamlet).
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
from upstage.src.kg.stage_tracker import StagePresenceTracker
from upstage.src.kg.epistemic_store import DualStreamEpistemicStore
from upstage.src.engine.stylometrics import StylometricEngine
from upstage.src.engine.register_filter import RegisterFilter
from upstage.src.engine.simulator import UpstageSimulator


class TestIagoHamletBenchmark(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_dir = root_dir / "data"
        with open(data_dir / "hamlet_sample.json", "r", encoding="utf-8") as f:
            cls.target_data = json.load(f)
        with open(data_dir / "iago_corpus.json", "r", encoding="utf-8") as f:
            cls.donor_data = json.load(f)

    def test_stage_presence_tracker_hamlet(self):
        tracker = StagePresenceTracker(self.target_data["stage_events"])

        # Line 50: King, Queen, and Polonius on stage
        witnesses_l50 = tracker.get_witnesses_at_line(50)
        self.assertIn("claudius", witnesses_l50)
        self.assertIn("gertrude", witnesses_l50)
        self.assertIn("polonius", witnesses_l50)
        self.assertNotIn("hamlet", witnesses_l50)

        # Line 170: Hamlet and Polonius on stage (King and Queen exeunt at line 168)
        witnesses_l170 = tracker.get_witnesses_at_line(170)
        self.assertIn("hamlet", witnesses_l170)
        self.assertIn("polonius", witnesses_l170)
        self.assertNotIn("claudius", witnesses_l170)

    def test_iago_epistemic_isolation_and_spoilers(self):
        store = DualStreamEpistemicStore("iago")

        # Safe Machiavellian turn
        safe_turn = "Men should be what they seem, my lord; or those that be not, would they might seem none!"
        has_leak, leaks = store.check_narrative_leakage(safe_turn, current_line=170)
        self.assertFalse(has_leak)
        self.assertEqual(len(leaks), 0)

        # Adversarial spoiler leak (Hamlet Act 5 duel poison)
        adversarial_turn = "Beware, my prince, for Claudius hath prepared a poisoned cup and Gertrude will carouse!"
        has_leak, leaks = store.check_narrative_leakage(adversarial_turn, current_line=170)
        self.assertTrue(has_leak)
        self.assertGreater(len(leaks), 0)

    def test_iago_stylometrics_burrows_delta(self):
        engine = StylometricEngine()
        iago_sample = self.donor_data["turns"][0]["text"]
        donor_ref = " ".join([t["text"] for t in self.donor_data["turns"]])
        polonius_ref = " ".join([t["text"] for sc in self.target_data["scenes"] for t in sc["turns"] if t["speaker_id"] == "polonius"])

        all_samples = [t["text"] for t in self.donor_data["turns"]] + [t["text"] for sc in self.target_data["scenes"] for t in sc["turns"]]
        affinity = engine.analyze_stylometric_affinity(iago_sample, donor_ref, polonius_ref, reference_samples=all_samples)

        self.assertIn("delta_to_donor", affinity)
        self.assertIn("delta_to_target", affinity)
        # Closer to Iago than to Polonius
        self.assertLess(affinity["delta_to_donor"], affinity["delta_to_target"])

    def test_iago_in_hamlet_simulation(self):
        sim = UpstageSimulator(self.target_data, self.donor_data, target_character_id="polonius")

        # Simulate Act 2 Scene 2 (Hamlet & Iago)
        res_2_2 = sim.simulate_scene(act_num=2, scene_num=2)
        self.assertEqual(len(res_2_2), 6)
        for turn in res_2_2:
            self.assertTrue(turn.epistemic_check_passed, f"Leak in {turn.slot.turn_id}")
            self.assertGreater(len(turn.generated_text), 20)

        # Simulate Act 3 Scene 1 (Before the Nunnery Scene)
        res_3_1 = sim.simulate_scene(act_num=3, scene_num=1)
        self.assertEqual(len(res_3_1), 2)
        for turn in res_3_1:
            self.assertTrue(turn.epistemic_check_passed)
        self.assertTrue(any("devotion" in (t.generated_text.lower() + t.slot.original_text.lower()) for t in res_3_1))


if __name__ == "__main__":
    unittest.main()
