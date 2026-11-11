import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sdn_slicing.config import load_config, validate_config


class ConfigTests(unittest.TestCase):
    def test_project_config_is_valid(self):
        self.assertTrue(validate_config(load_config()))

    def test_rejects_minimum_over_capacity(self):
        config = load_config()
        config["slices"][0]["min_mbps"] = 90
        with self.assertRaises(ValueError):
            validate_config(config)


if __name__ == "__main__":
    unittest.main()
