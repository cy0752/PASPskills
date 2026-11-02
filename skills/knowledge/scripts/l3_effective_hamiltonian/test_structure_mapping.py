"""Regression tests for integer primitive/configuration mapping checks."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import structure_mapping as mapping


class StructureMappingTest(unittest.TestCase):
    def setUp(self):
        primitive = {"lattice": [[2.0, 0, 0], [0.4, 2.2, 0], [0, 0, 3.0]],
                     "sites": [{"species": "Fe", "frac": [0, 0, 0]},
                               {"species": "X", "frac": [0.25, 0.5, 0.2]}]}
        relation = [[2, 0, 0], [0, 1, 0], [0, 0, 1]]
        configuration = {"lattice": [[4.0, 0, 0], [0.4, 2.2, 0], [0, 0, 3.0]],
                        "sites": [{"species": "Fe", "frac": [0, 0, 0]},
                                  {"species": "Fe", "frac": [0.5, 0, 0]},
                                  {"species": "X", "frac": [0.125, 0.5, 0.2]},
                                  {"species": "X", "frac": [0.625, 0.5, 0.2]}]}
        self.payload = {"primitive": primitive, "configuration": configuration, "relation": relation}

    def test_skew_cell_maps_with_row_vector_relation(self):
        result = mapping.check(self.payload)
        self.assertEqual(result["determinant"], 2)
        self.assertAlmostEqual(result["volume_ratio"], 2.0)
        self.assertEqual([row["primitive_site"] for row in result["mapping"]], [0, 0, 1, 1])
        self.assertLessEqual(result["max_site_residual_angstrom"], 1e-12)

    def test_inverted_relation_is_rejected(self):
        bad = copy.deepcopy(self.payload)
        bad["relation"] = [[1, 0, 0], [0, 2, 0], [0, 0, 1]]
        with self.assertRaisesRegex(mapping.MappingError, "lattice|site count"):
            mapping.check(bad)

    def test_species_or_duplicate_mapping_is_rejected(self):
        bad = copy.deepcopy(self.payload)
        bad["configuration"]["sites"][3]["species"] = "Fe"
        with self.assertRaisesRegex(mapping.MappingError, "species counts"):
            mapping.check(bad)

    def test_cli_returns_failure_for_malformed_relation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "geometry.json"
            bad = copy.deepcopy(self.payload)
            bad["relation"][0][0] = 1.25
            path.write_text(json.dumps(bad))
            proc = subprocess.run([sys.executable, "-B", str(Path(mapping.__file__).resolve()), str(path)],
                                  cwd=folder, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(json.loads(proc.stdout)["status"], "fail")


if __name__ == "__main__":
    unittest.main()
