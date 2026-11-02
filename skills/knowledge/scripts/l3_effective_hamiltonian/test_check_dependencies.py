"""Synthetic regression tests for the dependency audit."""
import sys
import tempfile
import unittest
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_dependencies as audit


class DependencyAuditTest(unittest.TestCase):
    def _write(self, root, train, selection):
        def rows(path, values):
            path.write_text("\n".join(" ".join(map(str, row)) for row in values) + "\n")
        rows(root / "train.txt", train)
        rows(root / "selection.txt", selection)

    def test_keeps_first_and_records_affine_dependencies_with_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            rows = [[1, 2, 3, 4, 9], [2, 3, 5, 6, 16],
                    [3, 5, 8, 10, 26], [4, 7, 11, 14, 39]]
            self._write(root, rows[:3], rows[3:])
            result = audit.audit(root / "train.txt", root / "selection.txt", 1e-12, 1e-12)
            self.assertEqual(result["kept_columns"], [1, 2])
            self.assertEqual([row["column"] for row in result["dependent_columns"]], [3, 4])
            self.assertEqual(result["rank_with_offset"], 3)
            self.assertTrue(all(row["max_residual"] <= row["tolerance"] for row in result["dependent_columns"]))

    def test_constant_column_is_affine_to_the_intercept(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            rows = [[1, 7, 2], [2, 7, 3], [3, 7, 4]]
            self._write(root, rows[:2], rows[2:])
            result = audit.audit(root / "train.txt", root / "selection.txt", 1e-10, 1e-10)
            self.assertEqual(result["kept_columns"], [1])
            self.assertEqual(result["dependent_columns"][0]["column"], 2)
            self.assertAlmostEqual(result["dependent_columns"][0]["intercept"], 7.0)

    def test_near_independent_column_is_retained_and_invalid_tolerance_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            rows = [[1, 2, 3], [2, 4.1, 6], [3, 6, 9], [4, 8, 12]]
            self._write(root, rows[:3], rows[3:])
            result = audit.audit(root / "train.txt", root / "selection.txt", 1e-12, 1e-12)
            self.assertEqual(result["kept_columns"], [1, 2])
            with self.assertRaisesRegex(ValueError, "positive total"):
                audit.audit(root / "train.txt", root / "selection.txt", 0, 0)

    def test_rejects_nonfinite_and_ragged_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "train.txt").write_text("1 2\n3 NaN\n")
            (root / "selection.txt").write_text("1 2\n")
            with self.assertRaisesRegex(ValueError, "nonfinite"):
                audit.audit(root / "train.txt", root / "selection.txt", 1e-8, 1e-8)
            (root / "train.txt").write_text("1 2 3\n4 5\n")
            with self.assertRaisesRegex(ValueError, "ragged"):
                audit.audit(root / "train.txt", root / "selection.txt", 1e-8, 1e-8)

    def test_prepare_binds_conversion_hashes_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); converted = root / "converted"
            converted.mkdir()
            train = [[1, 2, 9], [2, 4, 16]]
            selection = [[3, 6, 25]]
            self._write(converted, train, selection)
            (converted / "train.ids.json").write_text("[0, 1]\n")
            (converted / "selection.ids.json").write_text("[2]\n")
            from study_contract import digest
            receipt = {"sha256": {}, "splits": {"train": [0, 1], "selection": [2], "test": [3]},
                       "feature_count": 2, "basis_sha256": "basis", "split_sha256": "split"}
            for name in ("train.txt", "selection.txt", "train.ids.json", "selection.ids.json"):
                receipt["sha256"][name] = digest((converted / name).read_bytes())
            (converted / "conversion.json").write_text(json.dumps(receipt))
            result = audit.prepare(converted / "conversion.json", root / "audit", 1e-10, 1e-10)
            self.assertEqual(result["input_sha256"]["train.txt"], receipt["sha256"]["train.txt"])
            (converted / "train.txt").write_text("1 2 9\n2 4 17\n")
            with self.assertRaisesRegex(ValueError, "artifact changed"):
                audit.prepare(converted / "conversion.json", root / "tampered", 1e-10, 1e-10)


if __name__ == "__main__":
    unittest.main()
