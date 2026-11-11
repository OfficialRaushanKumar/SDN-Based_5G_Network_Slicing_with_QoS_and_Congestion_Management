import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TopologySourceTests(unittest.TestCase):
    def test_topology_declares_six_hosts_and_single_shared_link(self):
        source = (ROOT / "sdn_slicing" / "topology.py").read_text(encoding="utf-8")
        self.assertIn("range(1, 7)", source)
        self.assertEqual(source.count("self.addLink(left, right"), 1)


if __name__ == "__main__":
    unittest.main()
