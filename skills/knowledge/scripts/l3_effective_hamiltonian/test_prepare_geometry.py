"""Synthetic valid/invalid checks for the geometry package builder."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepare_geometry as geometry


def manifest():
    return {"lattice_angstrom": [[2, 0, 0], [0, 2, 0], [0, 0, 2]],
            "species": [{"element": "Fe", "z_value": 26},
                        {"element": "O", "z_value": 8}],
            "spin_values": [1, 0], "tolerance_angstrom": 1e-6,
            "sites": [{"position_angstrom": [0, 0, 0], "species_id": 1, "element": "Fe"},
                      {"position_angstrom": [1, 1, 1], "species_id": 2, "element": "O"}],
            "representatives": [{"species_id": 1, "position_angstrom": [0, 0, 0]}]}


class GeometryPackageTest(unittest.TestCase):
    def test_valid_package_is_deterministic_and_separates_inactive_species(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / "manifest.json"
            source.write_text(json.dumps(manifest()))
            first = geometry.build(source, root / "one")
            second = geometry.build(source, root / "two")
            self.assertEqual(first, second)
            self.assertEqual((root / "one/cell.str").read_bytes(), (root / "two/cell.str").read_bytes())
            receipt = json.loads((root / "one/geometry-package.json").read_text())
            self.assertEqual(receipt["mode_count"], 3)
            self.assertEqual((root / "one/mode_definition.fdf").read_text().count("1 spin"), 3)
            self.assertIn("AtomicCoordinatesFormat NotScaledCartesianAng", (root / "one/cell.str").read_text())

    def test_relation_and_representative_checks_reject_bad_inputs_without_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / "manifest.json"
            bad = manifest(); bad["sites"][1]["element"] = "Fe"; source.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError, "element/species_id"):
                geometry.build(source, root / "bad")
            bad = manifest(); bad["representatives"] = [{"species_id": 2, "position_angstrom": [0, 0, 0]}]
            source.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError, "active"):
                geometry.build(source, root / "bad2")
            bad = manifest(); bad["lattice_angstrom"] = [[1, 0, 0], [2, 0, 0], [0, 0, 1]]
            source.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError, "nonsingular"):
                geometry.build(source, root / "bad3")
            self.assertFalse((root / "bad").exists())
            self.assertFalse((root / "bad2").exists())
            self.assertFalse((root / "bad3").exists())

    def test_configuration_relation_is_checked_before_rendering(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / "manifest.json"
            spec = {"lattice_angstrom": [[2, 0, 0], [0, 2, 0], [0, 0, 2]],
                    "species": [{"element": "Fe", "z_value": 26}],
                    "spin_values": [1], "tolerance_angstrom": 1e-6,
                    "sites": [{"position_angstrom": [0, 0, 0], "species_id": 1, "element": "Fe"},
                              {"position_angstrom": [1, 0, 0], "species_id": 1, "element": "Fe"}],
                    "representatives": [{"species_id": 1, "position_angstrom": [0, 0, 0]}]}
            spec["reference_cell"] = {"lattice_angstrom": [[1, 0, 0], [0, 2, 0], [0, 0, 2]],
                                       "sites": [{"position_angstrom": [0, 0, 0], "species_id": 1, "element": "Fe"}]}
            spec["relation"] = [[2, 0, 0], [0, 1, 0], [0, 0, 1]]
            source.write_text(json.dumps(spec))
            receipt = geometry.build(source, root / "mapped")
            self.assertEqual(receipt["mapping"]["status"], "pass")
            spec["lattice_angstrom"][0][0] = 3
            source.write_text(json.dumps(spec))
            with self.assertRaisesRegex(ValueError, "lattice"):
                geometry.build(source, root / "mismatch")

    def test_cli_publishes_a_valid_package(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / "manifest.json"
            source.write_text(json.dumps(manifest()))
            result = subprocess.run([sys.executable, str(Path(geometry.__file__)),
                                     "--manifest", str(source), "--output", str(root / "cli")],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"site_count": 2', result.stdout)


if __name__ == "__main__":
    unittest.main()
