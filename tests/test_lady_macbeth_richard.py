"""
Unit and Integration Test Suite for Benchmark Pair 4:
Lady Macbeth (Macbeth) -> Lady Anne (Richard III).
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


class TestLadyMacbethRichardBenchmark(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        corpora_dir = root_dir / "corpora"
        with open(corpora_dir / "richard_sample.json", "r", encoding="utf-8") as f:
            cls.target_data = json.load(f)
        with open(corpora_dir / "lady_macbeth_corpus.json", "r", encoding="utf-8") as f:
            cls.donor_data = json.load(f)

    def test_stage_presence_tracker_london_street(self):
        tracker = StagePresenceTracker(self.target_data["stage_events"])

        # Line 20: Anne, Gentleman, Tressel mourning Henry VI
        witnesses_l20 = tracker.get_witnesses_at_line(20)
        self.assertIn("anne", witnesses_l20)
        self.assertIn("gentleman", witnesses_l20)
        self.assertNotIn("richard", witnesses_l20)

        # Line 50: Richard has entered at line 33
        witnesses_l50 = tracker.get_witnesses_at_line(50)
        self.assertIn("richard", witnesses_l50)
        self.assertIn("anne", witnesses_l50)
        self.assertIn("gentleman", witnesses_l50)

    def test_lady_macbeth_epistemic_isolation_and_spoilers(self):
        store = DualStreamEpistemicStore("lady_macbeth")

        # Safe imperious turn
        safe_turn = "Stand back, thou bloody minister of night! What, art thou come to gloat upon the carcass of thy ambition?"
        has_leak, leaks = store.check_narrative_leakage(safe_turn, current_line=50)
        self.assertFalse(has_leak)
        self.assertEqual(len(leaks), 0)

        # Adversarial spoiler leak (Princes in the Tower & Bosworth Field)
        adversarial_turn = "Beware, Gloucester, for Tyrrell shall smother the young princes in tower, and Richmond shall be king at Bosworth Field!"
        has_leak, leaks = store.check_narrative_leakage(adversarial_turn, current_line=50)
        self.assertTrue(has_leak)
        self.assertGreater(len(leaks), 0)

    def test_lady_macbeth_stylometrics_burrows_delta(self):
        engine = StylometricEngine()
        lm_sample = self.donor_data["turns"][2]["text"]
        donor_ref = " ".join([t["text"] for t in self.donor_data["turns"]])
        anne_ref = " ".join([t["text"] for sc in self.target_data["scenes"] for t in sc["turns"] if t["speaker_id"] == "anne"])

        all_samples = [t["text"] for t in self.donor_data["turns"]] + [t["text"] for sc in self.target_data["scenes"] for t in sc["turns"]]
        affinity = engine.analyze_stylometric_affinity(lm_sample, donor_ref, anne_ref, reference_samples=all_samples)

        self.assertIn("delta_to_donor", affinity)
        self.assertIn("delta_to_target", affinity)
        # Closer to Lady Macbeth than to Lady Anne
        self.assertLess(affinity["delta_to_donor"], affinity["delta_to_target"])

    def test_lady_macbeth_lexical_density_and_anachronisms(self):
        lm_turn = (
            "Infirm of purpose! Dost thou kneel and bare thy bosom to a woman's hand, thinking to purchase safety "
            "with theatrical remorse? Take up thy sword! Wash thy hands in all the perfumes of Arabia, "
            "yet the smell of blood shall never quit thy fingers!"
        )
        density = RegisterFilter.measure_lady_macbeth_density(lm_turn)
        self.assertGreaterEqual(density, 5.0)

        anachronisms = RegisterFilter.detect_anachronisms(lm_turn)
        self.assertEqual(len(anachronisms), 0)

    def test_lady_macbeth_in_richard_simulation(self):
        sim = UpstageSimulator(self.target_data, self.donor_data, target_character_id="anne")

        # Simulate Act 1 Scene 2 (Funeral / Wooing)
        res_1_2 = sim.simulate_scene(act_num=1, scene_num=2)
        self.assertEqual(len(res_1_2), 5)

        for turn in res_1_2:
            self.assertTrue(turn.epistemic_check_passed, f"Leak in {turn.slot.turn_id}")
            self.assertGreater(len(turn.generated_text), 20)

        # Check turn R3_1_2_t7 for "Infirm of purpose" / refusal to strike kneeling dog
        climax_turn = [t for t in res_1_2 if t.slot.turn_id == "R3_1_2_t7"][0]
        self.assertIn("infirm of purpose", climax_turn.generated_text.lower())
        self.assertIn("perfumes of arabia", climax_turn.generated_text.lower())


if __name__ == "__main__":
    unittest.main()
