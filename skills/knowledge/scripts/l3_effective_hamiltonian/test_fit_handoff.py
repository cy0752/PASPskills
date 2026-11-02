"""Regression fixtures for physical parameter export; no solver or scientific verdict."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import fit_handoff
import periodic_alias


class HandoffTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write("basis", "1 1 2 1 3 0 F #ipara,ipara_gb,power,n,nmode,im_read,lonebody\n"
                   "2 2 2 1 3 0 F #ipara,ipara_gb,power,n,nmode,im_read,lonebody\n")
        self.write("LM", "2 1\n2 2D0\n")
        self.write("report", "2 (Number of terms)\n1 0\n2 2\n"
                   "XM(1,1)=1;\nXM(2,1)=3;\nB(1)= -35 +- 0.1\nB(2)=2 +- 0.1\n")
        self.write("matrix", "1 3 -29\n2 4 -27\n")
        self.write("predictions", "# Y Y_ESTIMATE Y_UNCERTAINTY Y_ERROR\n"
                   "1 -29 -29 0 0\n2 -27 -27 0 0\n")
        self.spec = {"basis_file": "basis", "lm_file": "LM", "fit_report": "report",
                     "prediction_atol": 1e-10, "coefficient_atol": 1e-12,
                     "datasets": [{"name": name, "matrix": "matrix", "predictions": "predictions"}
                                  for name in ("train", "selection")]}

    def write(self, name, data):
        path = self.root / name
        path.write_text(data if isinstance(data, str) else json.dumps(data))
        return path

    def check(self):
        return fit_handoff.check(self.write("manifest.json", self.spec))[0]

    def test_native_lm_excludes_offset_and_reconstructs(self):
        result = self.check()
        self.assertEqual(result["retained_count"], 1)
        self.assertEqual(result["energy_offset"], -35)
        self.assertEqual(result["datasets"]["train"]["max_abs_prediction_difference"], 0)
        self.assertEqual(result["max_abs_coefficient"], 2)

    def test_optional_coefficient_scale_gate_rejects_cancelling_fit(self):
        self.spec["coefficient_abs_limit"] = 1
        with self.assertRaisesRegex(ValueError, "coefficient_abs_limit"):
            self.check()
        self.spec["coefficient_abs_limit"] = 2
        self.assertEqual(self.check()["coefficient_abs_limit"], 2)

    def test_old_xm_export_rejected_even_when_ids_in_range(self):
        self.spec["j_file"] = "J_best"
        self.write("J_best", "2 2\n1 -35\n2 2\n")
        with self.assertRaisesRegex(ValueError, "J_best differs"):
            self.check()

    def test_wrong_physical_mapping_rejected_by_predictions(self):
        self.write("LM", "2 1\n1 2\n")
        self.write("report", "2\n1 0\n2 1\nB(1)=-35\nB(2)=2\n")
        with self.assertRaisesRegex(ValueError, "round-trip"):
            self.check()

    def test_row_order_and_units_mismatch(self):
        for predictions in ("2 -29 -29 0 0\n1 -27 -27 0 0\n",
                            "1 -58 -58 0 0\n2 -54 -54 0 0\n"):
            with self.subTest(predictions=predictions):
                self.write("predictions", predictions)
                with self.assertRaises(ValueError):
                    self.check()

    def test_unsupported_reduced_matrix_and_test_access(self):
        self.write("matrix", "3 -29\n4 -27\n")
        with self.assertRaisesRegex(ValueError, "pristine"):
            self.check()
        self.spec["datasets"][1]["name"] = "test"
        with self.assertRaisesRegex(ValueError, "final test"):
            self.check()

    def test_malformed_parameters_and_basis(self):
        for text in ("2 1\n0 -35\n", "2 2\n2 2\n2 3\n", "2 1\n2 nan\n",
                     "2 1\n2 0\n", "2 1\n2 2\n1 3\n",
                     "2 1\n2 2 # comment\n", "2 1\n\n2 2\n"):
            self.write("LM", text)
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.check()
        self.write("LM", "2 1\n2 2\n")
        self.write("basis", "unknown basis format\n")
        with self.assertRaisesRegex(ValueError, "basis"):
            self.check()

    def test_cli_exports_native_bytes_and_preserves_old_artifacts(self):
        manifest = self.write("manifest.json", self.spec)
        script = str(Path(fit_handoff.__file__).resolve())
        command = [sys.executable, "-B", script, "--manifest", str(manifest),
                   "--root", str(self.root / "candidate")]
        proc = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((self.root / "candidate/J_best.dat").read_bytes(), (self.root / "LM").read_bytes())
        self.write("candidate/J_best.dat", "existing result\n")
        proc = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual((self.root / "candidate/J_best.dat").read_text(), "existing result\n")

    def test_native_completion_rejects_rewritten_or_incomplete_fit(self):
        self.write("fit.log", "Nn,Nd: 2 1\nNEED TO REWRITE DATA\nFITTING FINISHED\nPASP is finished gracefully\n")
        self.spec["fit_log"] = "fit.log"
        with self.assertRaisesRegex(ValueError, "rewrote"):
            self.check()
        self.write("fit.log", "Nn,Nd: 2 2\nFITTING FINISHED\nPASP is finished gracefully\n")
        self.spec["fit_exit_code_file"] = "fit.exit"
        self.write("fit.exit", "1\n")
        with self.assertRaisesRegex(ValueError, "exit code"):
            self.check()

    def test_clean_native_completion_passes(self):
        self.spec["fit_log"] = "fit.log"
        self.spec["fit_exit_code_file"] = "fit.exit"
        self.write("fit.log", "Nn,Nd: 2 2\nFITTING FINISHED\nPASP is finished gracefully\n")
        self.write("fit.exit", "0\n")
        self.assertEqual(self.check()["feature_count"], 2)

    def test_missing_native_completion_rejected(self):
        self.spec["fit_log"] = "fit.log"
        for text in ("Nn,Nd: 2 2\n", "Nn,Nd: 2 2\nFITTING FINISHED\n",
                     "Nn,Nd: 2 2\nPASP is finished gracefully\n"):
            with self.subTest(text=text):
                self.write("fit.log", text)
                with self.assertRaisesRegex(ValueError, "completion"):
                    self.check()

    def test_every_logged_width_must_match_native_lm(self):
        self.spec["fit_log"] = "fit.log"
        for dimensions in ("Nn,Nd: 2 1\n", "Nn,Nd: 2 3\nNn,Nd: 2 2\n"):
            with self.subTest(dimensions=dimensions):
                self.write("fit.log", dimensions + "FITTING FINISHED\nPASP is finished gracefully\n")
                with self.assertRaisesRegex(ValueError, "width"):
                    self.check()

    def test_clean_reduced_refit_still_rejects_original_wider_basis(self):
        # Internally consistent reduced files do not prove same-basis delivery.
        self.write("LM", "1 1\n1 2\n")
        self.write("report", "2\n1 0\n2 1\nB(1)=-35\nB(2)=2\n")
        self.write("matrix", "3 -29\n4 -27\n")
        self.spec["fit_log"] = "fit.log"
        self.write("fit.log", "Nn,Nd: 2 1\nFITTING FINISHED\nPASP is finished gracefully\n")
        with self.assertRaisesRegex(ValueError, "mismatched basis"):
            self.check()


class AliasTest(unittest.TestCase):
    def spec(self):
        return {"training_supercell": [3, 3, 1], "target_supercell": [6, 6, 1],
                "pair_orbits": [{"name": str(step), "pairs": [
                    {"sites": [0, 0], "shift": [step * a, step * b, 0]}
                    for a, b in [(1, 0), (0, 1), (1, 1)]]} for step in [1, 2]]}

    def test_three_cell_shell_alias_disappears_in_six_cell(self):
        result = periodic_alias.check(self.spec())
        self.assertEqual(result["status"], "unresolved_aliasing")
        self.assertEqual(result["collisions"], [{"orbits": ["1", "2"], "target_distinguishes": True}])

    def test_no_claim_of_physical_identity_when_target_also_aliases(self):
        spec = self.spec()
        spec["target_supercell"] = [3, 3, 1]
        self.assertFalse(periodic_alias.check(spec)["collisions"][0]["target_distinguishes"])

    def test_site_ids_and_relative_multiplicities_are_preserved(self):
        spec = self.spec()
        spec["pair_orbits"][1]["pairs"][0]["sites"] = [0, 1]
        self.assertFalse(periodic_alias.check(spec)["collisions"])
        spec = self.spec()
        spec["pair_orbits"][1]["pairs"] += spec["pair_orbits"][1]["pairs"][:1]
        self.assertFalse(periodic_alias.check(spec)["collisions"])

    def test_non_diagonal_and_invalid_cell_rejected(self):
        for shape in ([[3, 0, 0], [0, 3, 0], [0, 0, 1]], [3, 0, 1], [True, 3, 1]):
            with self.subTest(shape=shape), self.assertRaises(ValueError):
                periodic_alias.signature(shape, self.spec()["pair_orbits"][0]["pairs"])

    def test_cli_collision_is_nonzero_with_actionable_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "pairs.json"
            path.write_text(json.dumps(self.spec()))
            proc = subprocess.run([sys.executable, "-B", str(Path(periodic_alias.__file__).resolve()),
                                   "--manifest", str(path)], cwd=folder, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertTrue(json.loads(proc.stdout)["collisions"][0]["target_distinguishes"])


if __name__ == "__main__":
    unittest.main()
