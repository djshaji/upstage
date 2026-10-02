"""
Unit Test Suite for Upstage Interactive Local UI Server & REST API.
"""

import json
import time
import threading
import unittest
import urllib.request
import urllib.error
from pathlib import Path
from http.server import HTTPServer
from upstage_ui import UpstageHTTPHandler


class TestUpstageUIServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.port = 8899
        cls.server = HTTPServer(("localhost", cls.port), UpstageHTTPHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_root_html_application(self):
        url = f"http://localhost:{self.port}/"
        with urllib.request.urlopen(url, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            html = resp.read().decode("utf-8")
            self.assertIn("UPSTAGE: Shakespearean Character Transplantation Studio", html)
            self.assertIn("Benchmark Studio", html)
            self.assertIn("37-Play Canon Explorer", html)

    def test_api_benchmarks(self):
        url = f"http://localhost:{self.port}/api/benchmarks"
        with urllib.request.urlopen(url, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("benchmarks", data)
            benchmarks = data["benchmarks"]
            self.assertEqual(len(benchmarks), 4)

            donor_names = [b["donor"] for b in benchmarks]
            self.assertIn("Sir John Falstaff", donor_names)
            self.assertIn("Iago", donor_names)
            self.assertIn("Viola (Cesario)", donor_names)
            self.assertIn("Lady Macbeth", donor_names)

    def test_api_recommender(self):
        url = f"http://localhost:{self.port}/api/recommender?donor=Falstaff"
        with urllib.request.urlopen(url, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("recommendations", data)

    def test_api_simulate_turn(self):
        url = f"http://localhost:{self.port}/api/simulate_turn"
        payload = json.dumps({"donor": "iago", "mode": "clean"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("text", data)
            self.assertIn("delta_donor", data)
            self.assertIn("anachronisms", data)
            self.assertEqual(len(data["anachronisms"]), 0)


if __name__ == "__main__":
    unittest.main()
