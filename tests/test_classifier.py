import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sdn_slicing.config import load_config
from sdn_slicing.classifier import classify_pair


class ClassifierTests(unittest.TestCase):
    def test_classifies_both_directions(self):
        cfg = load_config()
        hosts = {f"h{i}": {"ip": f"10.0.0.{i}"} for i in range(1, 7)}
        self.assertEqual(classify_pair("10.0.0.4", "10.0.0.3", hosts, cfg["slices"])["id"], "healthcare")

    def test_unrelated_flow_is_unclassified(self):
        cfg = load_config()
        hosts = {f"h{i}": {"ip": f"10.0.0.{i}"} for i in range(1, 7)}
        self.assertIsNone(classify_pair("10.0.0.1", "10.0.0.6", hosts, cfg["slices"]))


if __name__ == "__main__":
    unittest.main()
