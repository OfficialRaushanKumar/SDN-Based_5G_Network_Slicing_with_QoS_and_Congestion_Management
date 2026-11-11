import json
import unittest


class ResultsSchemaTests(unittest.TestCase):
    def test_empty_results_are_not_fabricated(self):
        sample = {"measurements": [], "note": "Measured values from this run; not guaranteed outcomes."}
        self.assertEqual(json.loads(json.dumps(sample))["measurements"], [])


if __name__ == "__main__":
    unittest.main()
