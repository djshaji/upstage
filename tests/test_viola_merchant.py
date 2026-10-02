"""
Unit and Integration Test Suite for Benchmark Pair 3:
Viola (Twelfth Night) -> Portia/Doctor Balthazar (The Merchant of Venice).
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


class TestViolaMerchantBenchmark(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        corpora_dir = root_dir / "corpora"
        with open(corpora_dir / "merchant_sample.json", "r", encoding="utf-8") as f:
            cls.target_data = json.load(f)
        with open(corpora_dir / "viola_corpus.json", "r", encoding="utf-8") as f:
            cls.donor_data = json.load(f)

    def test_stage_presence_tracker_venice_court(self):
        tracker = StagePresenceTracker(self.target_data["stage_events"])

        # Line 50: Duke, Antonio, Bassanio, Gratiano, Shylock in court
        witnesses_l50 = tracker.get_witnesses_at_line(50)
        self.assertIn("duke", witnesses_l50)
        self.assertIn("antonio", witnesses_l50)
        self.assertIn("shylock", witnesses_l50)
        self.assertNotIn("portia", witnesses_l50)

        # Line 200: Portia/Balthazar has entered at line 166
        witnesses_l200 = tracker.get_witnesses_at_line(200)
        self.assertIn("portia", witnesses_l200)
        self.assertIn("shylock", witnesses_l200)
        self.assertIn("bassanio", witnesses_l200)
        self.assertIn("duke", witnesses_l200)

    def test_viola_epistemic_isolation_and_spoilers(self):
        store = DualStreamEpistemicStore("viola")

        # Safe empathetic turn
        safe_turn = "Mercy is no compulsion of the court, sir, but the silent sorrow of the soul that seeth another's wound."
        has_leak, leaks = store.check_narrative_leakage(safe_turn, current_line=200)
        self.assertFalse(has_leak)
        self.assertEqual(len(leaks), 0)

        # Adversarial spoiler leak (Antonio's argosies safe return in Act 5)
        adversarial_turn = "Grieve not, fair sir, for three argosies are richly come to harbor and your merchant ships rich!"
        has_leak, leaks = store.check_narrative_leakage(adversarial_turn, current_line=200)
        self.assertTrue(has_leak)
        self.assertGreater(len(leaks), 0)

    def test_viola_stylometrics_burrows_delta(self):
        engine = StylometricEngine()
        viola_sample = self.donor_data["turns"][1]["text"]
        donor_ref = " ".join([t["text"] for t in self.donor_data["turns"]])
        portia_ref = " ".join([t["text"] for sc in self.target_data["scenes"] for t in sc["turns"] if t["speaker_id"] == "portia"])

        all_samples = [t["text"] for t in self.donor_data["turns"]] + [t["text"] for sc in self.target_data["scenes"] for t in sc["turns"]]
        affinity = engine.analyze_stylometric_affinity(viola_sample, donor_ref, portia_ref, reference_samples=all_samples)

        self.assertIn("delta_to_donor", affinity)
        self.assertIn("delta_to_target", affinity)
        # Closer to Viola than to Portia
        self.assertLess(affinity["delta_to_donor"], affinity["delta_to_target"])

    def test_viola_lexical_density_and_anachronisms(self):
        viola_turn = (
            "She that I knew—a sister lost beneath the salt and raging surge—would tell you that "
            "an unpitied wound turns the sea itself to bitterness. I pray you, take the gold, "
            "and let this living sorrow walk in peace."
        )
        density = RegisterFilter.measure_viola_density(viola_turn)
        self.assertGreaterEqual(density, 5.0)

        anachronisms = RegisterFilter.detect_anachronisms(viola_turn)
        self.assertEqual(len(anachronisms), 0)

    def test_viola_in_merchant_simulation(self):
        sim = UpstageSimulator(self.target_data, self.donor_data, target_character_id="portia")

        # Simulate Act 4 Scene 1 (Venice Courtroom)
        res_4_1 = sim.simulate_scene(act_num=4, scene_num=1)
        self.assertEqual(len(res_4_1), 6)

        for turn in res_4_1:
            self.assertTrue(turn.epistemic_check_passed, f"Leak in {turn.slot.turn_id}")
            self.assertGreater(len(turn.generated_text), 20)

        # Check self-sacrificial offer in turn MV_4_1_t9
        climax_turn = [t for t in res_4_1 if t.slot.turn_id == "MV_4_1_t9"][0]
        self.assertTrue(any(w in climax_turn.generated_text.lower() for w in ["strike into this breast", "turn the point hither", "thousand deaths", "my blood answer"]))


if __name__ == "__main__":
    unittest.main()
