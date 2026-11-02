"""Synthetic contract tests; no PASP execution or scientific acceptance claims."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import study_contract as contract


class ContractTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write("Energy.dat", "19 -4D0\n0 -8\n7 -6\n25 -2\n")
        self.write("split.json", {"seed": 23, "splits": {"train": [7, 0], "selection": [25], "test": [19]}})
        self.write("basis.dat", "synthetic basis; not a PASP model\n")
        self.spec = {"energy_file": "Energy.dat", "energy_header": "none", "split_file": "split.json",
                     "energy_divisor": 2, "basis_file": "basis.dat", "samples": []}
        for sid in [0, 7, 19, 25]:
            self.write(f"{sid}.ene_symbol", f"2 #npara\n1 1.0\n2 {sid}.0D0\n")
            self.write(f"{sid}.log", "synthetic fixture: PASP is finished gracefully\n")
            self.write(f"{sid}.exit", "0\n")
            self.spec["samples"].append({"id": sid, "features": f"{sid}.ene_symbol", "basis_file": "basis.dat",
                                         "log": f"{sid}.log", "exit_code_file": f"{sid}.exit"})
        self.manifest = self.root / "study.json"

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value if isinstance(value, str) else json.dumps(value))
        return path

    def convert(self):
        self.write("study.json", self.spec)
        return contract.convert(self.manifest, self.root / "converted")

    def invalid_convert(self):
        with self.assertRaises((ValueError, OSError)):
            self.convert()
        self.assertFalse((self.root / "converted").exists())

    def delivery(self):
        self.write("train.csv", "sample_id,target,prediction\n0,-8,-7\n7,-6,-7\n")
        self.write("selection.csv", "sample_id,target,prediction\n25,-2,-1\n")
        self.write("test.csv", "sample_id,target,prediction\n19,-4,-3\n")
        self.write("report.md", "Synthetic report.\n")
        self.write("coverage.json", {"tables": [{"path": f"delivery/{s}.csv"} for s in contract.SPLITS]})
        spec = {k: self.spec[k] for k in ("energy_file", "energy_header", "split_file")}
        spec.update({"target_scale": 1, "target_atol": 0,
                     "artifacts": {f"delivery/{s}.csv": f"{s}.csv" for s in contract.SPLITS},
                     "csv_paths": {s: f"delivery/{s}.csv" for s in contract.SPLITS},
                     "root_artifacts": ["report.md", "coverage.json"],
                     "references": [{"artifact": "coverage.json", "keys": ["tables", i, "path"]} for i in range(3)]})
        spec["artifacts"].update({"report.md": "report.md", "coverage.json": "coverage.json"})
        return spec

    def model_delivery(self):
        spec = self.delivery()
        model = {
            "basis_file": "local_mode_PM.dat", "lm_file": "native_LM.txt",
            "fit_report": "native_fit.txt", "fit_log": "log.out",
            "feature_matrix": "full-pristine-matrix.txt", "row_ids": "full-row-ids.json",
            "encoding_root": "encodes", "encoding_template": "method6-inputs",
            "energy_divisor": 9,
        }
        self.write("model.json", model)
        for name in ("local_mode_PM.dat", "native_LM.txt", "native_fit.txt", "log.out",
                     "full-pristine-matrix.txt", "full-row-ids.json"):
            self.write(name, name + "\n")
        self.write("method6-inputs/PASP.input", "method 6\n")
        self.write("encodes/0/exit.code", "0\n")
        spec["artifacts"].update({
            "fgt-model.json": "model.json",
            "local_mode_PM.dat": "local_mode_PM.dat", "native_LM.txt": "native_LM.txt",
            "native_fit.txt": "native_fit.txt", "log.out": "log.out",
            "full-pristine-matrix.txt": "full-pristine-matrix.txt",
            "full-row-ids.json": "full-row-ids.json",
            "method6-inputs/PASP.input": "method6-inputs/PASP.input",
            "encodes/0/exit.code": "encodes/0/exit.code",
        })
        spec["root_artifacts"] += ["fgt-model.json"]
        return spec

    def publish(self, spec):
        self.write("delivery.json", spec)
        return contract.publish(self.root / "delivery.json", self.root / "consumer", "notes/receipt.json")

    def test_conversion_order_units_and_complete_features(self):
        result = self.convert()
        rows = [[float(v) for v in line.split()] for line in (self.root / "converted/train.txt").read_text().splitlines()]
        self.assertEqual(rows, [[1, 7, -3], [1, 0, -4]])
        self.assertEqual(result["feature_count"], 2)
        self.assertFalse(result["source_identity_checked"])
        self.assertEqual(json.loads((self.root / "converted/train.ids.json").read_text()), [7, 0])
        self.assertEqual(contract.verify(self.root / "converted", "conversion.json")["count"], 4)
        self.assertFalse((self.root / "converted/test.txt").exists())

    def native_fixture(self):
        self.write("basis.dat", "1 1 2 1 3 0 F #ipara,ipara_gb,power,n,nmode,im_read,lonebody\n"
                   "2 2 2 1 3 0 F #ipara,ipara_gb,power,n,nmode,im_read,lonebody\n")
        self.convert()
        self.write("native.lm", "2 1\n2 0.5\n")
        self.write("native.report", "2\n1 0\n2 2\nB(1)=-1\nB(2)=0.5\n")
        self.write("native.log", "Nn,Nd: 2 2\nFITTING FINISHED\nPASP is finished gracefully\n")
        self.write("native.exit", "0\n")
        handoff = {"basis_file": "basis.dat", "lm_file": "native.lm", "fit_report": "native.report",
                   "fit_log": "native.log", "fit_exit_code_file": "native.exit",
                   "prediction_atol": 1e-10, "coefficient_atol": 1e-12, "datasets": []}
        for name in ("train", "selection"):
            rows = contract.records(self.root / "converted" / (name + ".txt"))
            self.write(name + ".native", "".join(
                f"{i} {row[-1]} {-1 + .5 * float(row[1])} 0 0\n"
                for i, row in enumerate(rows, 1)))
            handoff["datasets"].append({"name": name, "matrix": f"converted/{name}.txt",
                                        "predictions": name + ".native"})
        return self.write("handoff.json", handoff)

    def test_native_freeze_then_batch_evaluate_all_ids_and_terminal_lock(self):
        handoff = self.native_fixture()
        frozen = self.root / "frozen"
        result = contract.freeze_native(self.root / "converted/conversion.json", handoff, frozen)
        self.assertEqual(result["handoff"]["retained_count"], 1)
        self.assertFalse((self.root / "converted/test.txt").exists())
        evaluated = self.root / "evaluation"
        scores = contract.evaluate_frozen(frozen / "native-freeze.json", evaluated)
        self.assertEqual(sum(m["count"] for m in scores["metrics"].values()), 4)
        self.assertEqual(json.loads((evaluated / "full-row-ids.json").read_text()), [0, 7, 19, 25])
        self.assertIn("19,-2.0000000000000000E+00,8.5000000000000000E+00",
                      (evaluated / "test_predictions.csv").read_text())
        self.assertEqual(scores, contract.evaluate_frozen(frozen / "native-freeze.json", evaluated))
        with self.assertRaisesRegex(ValueError, "test already opened"):
            contract.freeze_native(self.root / "converted/conversion.json", handoff, self.root / "retuned")

    def test_freeze_requires_native_completion_and_reconstruction(self):
        handoff = self.native_fixture()
        for filename, bad in (("native.exit", "1\n"), ("native.lm", "2 1\n2 2.0\n"),
                              ("native.log", "Nn,Nd: 2 2\n"),
                              ("split.json", "{}\n"), ("Energy.dat", "19 -1\n"),
                              ("native.log", "Nn,Nd: 2 2\nFATAL bad fit\nFITTING FINISHED\nPASP is finished gracefully\n")):
            path = self.root / filename
            good = path.read_bytes()
            path.write_text(bad)
            with self.subTest(filename=filename), self.assertRaises(ValueError):
                contract.freeze_native(self.root / "converted/conversion.json", handoff, self.root / "bad")
            self.assertFalse((self.root / "bad").exists())
            path.write_bytes(good)

    def test_preexisting_test_matrix_and_changed_features_are_not_hidden(self):
        handoff = self.native_fixture()
        test = self.write("converted/test.txt", "prior test data\n")
        with self.assertRaisesRegex(ValueError, "test matrix exists"):
            contract.freeze_native(self.root / "converted/conversion.json", handoff, self.root / "bad")
        test.unlink()  # Synthetic fixture cleanup; runtime must retain/disclose real prior exposure.
        contract.freeze_native(self.root / "converted/conversion.json", handoff, self.root / "frozen")
        self.write("19.ene_symbol", "2\n1 1\n2 20\n")
        with self.assertRaisesRegex(ValueError, "features changed"):
            contract.evaluate_frozen(self.root / "frozen/native-freeze.json", self.root / "bad-evaluation")
        self.assertFalse((self.root / "bad-evaluation").exists())

    def test_native_publication_binds_evaluation_and_model_bytes(self):
        handoff = self.native_fixture()
        contract.freeze_native(self.root / "converted/conversion.json", handoff, self.root / "frozen")
        contract.evaluate_frozen(self.root / "frozen/native-freeze.json", self.root / "evaluation")
        spec = self.delivery()
        spec.update(native_freeze="frozen/native-freeze.json", final_evaluation="evaluation/final-evaluation.json")
        frozen = json.loads((self.root / spec["native_freeze"]).read_text())
        evaluated = json.loads((self.root / spec["final_evaluation"]).read_text())
        spec["artifacts"].update({name: "frozen/" + name for name in frozen["sha256"]})
        spec["artifacts"].update({name: "evaluation/" + name for name in evaluated["sha256"]})
        spec["csv_paths"] = {name: name + "_predictions.csv" for name in contract.SPLITS}
        spec["target_scale"] = .5
        self.publish(spec)
        del spec["artifacts"]["native_LM.txt"]
        with self.assertRaisesRegex(ValueError, "omits/changes frozen native"):
            self.publish(spec)

    def test_freeze_and_evaluate_cli_from_other_directory(self):
        handoff = self.native_fixture()
        script = str(Path(contract.__file__).resolve())
        def run(*args):
            return subprocess.run([sys.executable, "-B", script, *map(str, args)],
                                  cwd=self.root, capture_output=True, text=True)
        frozen = self.root / "frozen"
        result = run("freeze-native", "--conversion", self.root / "converted/conversion.json",
                     "--handoff", handoff, "--root", frozen)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = run("evaluate-frozen", "--freeze", frozen / "native-freeze.json",
                     "--root", self.root / "evaluated")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.write("frozen/native_LM.txt", "2 1\n2 9\n")
        result = run("evaluate-frozen", "--freeze", frozen / "native-freeze.json",
                     "--root", self.root / "tampered")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("artifact changed", result.stderr)
        self.assertFalse((self.root / "tampered").exists())

    def test_evaluation_rejects_changed_split_or_energy(self):
        handoff = self.native_fixture()
        contract.freeze_native(self.root / "converted/conversion.json", handoff, self.root / "frozen")
        for name, content in (("split.json", {"seed": 23, "splits": {"train": [0, 7], "selection": [19], "test": [25]}}),
                              ("Energy.dat", "19 -5\n0 -8\n7 -6\n25 -2\n")):
            good = (self.root / name).read_bytes()
            self.write(name, content)
            with self.subTest(name=name), self.assertRaises(ValueError):
                contract.evaluate_frozen(self.root / "frozen/native-freeze.json", self.root / "bad-evaluation")
            self.assertFalse((self.root / "bad-evaluation").exists())
            (self.root / name).write_bytes(good)

    def test_explicit_text_header(self):
        self.spec["energy_header"] = "one"
        self.write("Energy.dat", "id energy\n19 -4\n0 -8\n7 -6\n25 -2\n")
        self.convert()

    def test_header_cannot_skip_first_sample(self):
        self.spec["energy_header"] = "one"
        self.invalid_convert()

    def test_duplicate_energy_id(self):
        self.write("Energy.dat", "0 -8\n0 -6\n")
        self.invalid_convert()

    def test_nonfinite_and_invalid_divisors(self):
        for value in [0, -1, float("nan"), float("inf"), True]:
            with self.subTest(value=value):
                self.spec["energy_divisor"] = value
                self.invalid_convert()

    def test_nonfinite_energy(self):
        self.write("Energy.dat", "0 NaN\n7 -6\n19 -4\n25 -2\n")
        self.invalid_convert()

    def test_malformed_features(self):
        for text in ["0\n", "2\n1 1\n", "1\n1 1\n2 2\n", "2\n2 1\n1 2\n",
                     "2\n1 1\n1 2\n", "2\n1 1\n2 inf\n", "2\n1 1 extra\n2 2\n"]:
            with self.subTest(text=text):
                self.write("25.ene_symbol", text)
                self.invalid_convert()

    def test_width_mismatch(self):
        self.write("25.ene_symbol", "1 #npara\n1 1\n")
        self.invalid_convert()

    def test_missing_or_duplicate_samples(self):
        original = copy.deepcopy(self.spec["samples"])
        for samples in [original[:-1], original + [original[0]]]:
            self.spec["samples"] = samples
            self.invalid_convert()

    def test_failed_or_incomplete_run(self):
        self.write("25.exit", "1\n")
        self.invalid_convert()
        self.write("25.exit", "0\n")
        self.write("25.log", "stopped early\n")
        self.invalid_convert()

    def test_mixed_basis(self):
        self.write("other_basis.dat", "different\n")
        self.spec["samples"][-1]["basis_file"] = "other_basis.dat"
        self.invalid_convert()

    def test_empty_basis(self):
        self.write("basis.dat", "\n")
        self.invalid_convert()

    def test_accidental_feature_source_reuse(self):
        self.spec["samples"][-1]["features"] = self.spec["samples"][0]["features"]
        self.invalid_convert()

    def identity_records(self):
        self.spec["require_source_identity"] = True
        self.spec["source_energy_atol"] = 1e-8
        for sample in self.spec["samples"]:
            sid = sample["id"]
            self.write(f"raw/{sid}/OUTCAR", f"TOTEN = {dict(contract.energies(self.root / 'Energy.dat', 'none'))[sid]}\n")
            self.write(f"raw/{sid}/pos", f"final positions of original {sid}\n")
            self.write(f"raw/{sid}/spin", f"final spins of original {sid}\n")
            sample["source_identity"] = f"raw/{sid}/source.json"
            self.write(sample["source_identity"], {"original_id": sid, "outcar": "OUTCAR",
                       "structure": "pos", "magnetic_state": "spin"})
            sample["encoding_identity"] = f"encoded-{sid}.json"
            self.write(sample["encoding_identity"], {"original_id": sid,
                       "structure": f"raw/{sid}/pos", "magnetic_state": f"raw/{sid}/spin",
                       "sha256": {role: contract.digest((self.root / path).read_bytes()) for role, path in
                                  {"structure": f"raw/{sid}/pos", "magnetic_state": f"raw/{sid}/spin",
                                   "features": sample["features"], "basis": sample["basis_file"]}.items()}})

    def test_original_identity_and_final_inputs(self):
        self.identity_records()
        self.assertTrue(self.convert()["source_identity_checked"])

    def test_renumbered_wrong_original_sample_rejected(self):
        self.identity_records()
        self.spec["samples"][0]["original_id"] = 7
        self.invalid_convert()

    def test_initial_spin_used_instead_of_final_rejected(self):
        self.identity_records()
        self.write("initial_spin", "initial magnetic state\n")
        path = self.spec["samples"][0]["encoding_identity"]
        record = json.loads((self.root / path).read_text())
        record["magnetic_state"] = "initial_spin"
        self.write(path, record)
        self.invalid_convert()

    def test_energy_from_another_original_outcar_rejected(self):
        self.identity_records()
        self.write("raw/0/OUTCAR", "TOTEN = -99\n")
        self.invalid_convert()

    def test_final_spins_overwritten_after_initial_encoding_rejected(self):
        self.identity_records()
        # Source and live encoding inputs agree, but the feature run used an older state.
        self.write("raw/0/spin", "new final magnetic state after DFT\n")
        self.invalid_convert()

    def test_old_ene_symbol_cannot_pair_with_final_encoding_record(self):
        self.identity_records()
        self.write("0.ene_symbol", "2\n1 0.125\n2 0.25\n")
        self.invalid_convert()

    def test_basis_change_invalidates_encoding_capture(self):
        self.identity_records()
        self.write("basis.dat", "new basis copied to every sample\n")
        self.invalid_convert()

    def test_identity_requirement_cannot_silently_fall_back(self):
        self.spec["require_source_identity"] = True
        with self.assertRaises(KeyError):
            self.convert()
        self.assertFalse((self.root / "converted").exists())

    def test_duplicate_manifest_keys(self):
        self.write("split.json", '{"splits": {}, "splits": {}}')
        self.invalid_convert()

    def test_split_isolation_and_full_coverage(self):
        for splits in [{"train": [0, 7], "selection": [7], "test": [19]},
                       {"train": [0], "selection": [25], "test": [19]},
                       {"train": [0, 7], "selection": [], "test": [19, 25]},
                       {"train": [False, 7], "selection": [25], "test": [19]}]:
            self.write("split.json", {"splits": splits})
            self.invalid_convert()

    def test_missing_features(self):
        (self.root / "25.ene_symbol").unlink()
        self.invalid_convert()

    def test_publication_metrics_and_idempotence(self):
        spec = self.delivery()
        result = self.publish(spec)
        self.assertEqual(result["metrics"]["train"], {"count": 2, "rmse": 1, "mae": 1, "r2": 0})
        self.assertIsNone(result["metrics"]["test"]["r2"])
        self.assertEqual(result, self.publish(spec))
        for dest, src in spec["artifacts"].items():
            self.assertEqual((self.root / "consumer" / dest).read_bytes(), (self.root / src).read_bytes())
        contract.verify(self.root / "consumer", "notes/receipt.json")

    def test_model_manifest_exact_schema_and_paths(self):
        spec = self.model_delivery()
        result = self.publish(spec)
        self.assertEqual(result["metrics"]["test"]["count"], 1)
        contract.verify(self.root / "consumer", "notes/receipt.json")

    def test_model_manifest_extra_field_rejected_before_publication(self):
        spec = self.model_delivery()
        model = json.loads((self.root / "model.json").read_text())
        model["model_selection"] = {"reason": "diagnostic metadata"}
        self.write("model.json", model)
        with self.assertRaisesRegex(ValueError, "exactly"):
            self.publish(spec)
        self.assertFalse((self.root / "consumer").exists())

    def test_model_manifest_missing_path_and_invalid_path_rejected(self):
        for field, value in (("fit_log", "missing.log"), ("basis_file", "../basis.dat"),
                             ("energy_divisor", 0)):
            with self.subTest(field=field):
                spec = self.model_delivery()
                model = json.loads((self.root / "model.json").read_text())
                model[field] = value
                self.write("model.json", model)
                with self.assertRaises(ValueError):
                    self.publish(spec)
                self.assertFalse((self.root / "consumer").exists())

    def test_nonqualifying_coverage_publication_preserves_failure(self):
        # Mechanical completeness does not certify a native model or accuracy.
        spec = self.delivery()
        coverage = json.loads((self.root / "coverage.json").read_text())
        coverage.update({"status": "nonqualifying", "failed_gate": "accuracy",
                         "native_model": None})
        self.write("coverage.json", coverage)
        self.write("report.md", "Synthetic bounded failure: no qualifying native model.\n")
        result = self.publish(spec)
        self.assertEqual(sum(row["count"] for row in result["metrics"].values()), 4)
        self.assertEqual(result["metrics"]["train"]["r2"], 0)
        published = json.loads((self.root / "consumer/coverage.json").read_text())
        self.assertEqual(published, coverage)
        self.assertIsNone(published["native_model"])
        self.assertEqual(contract.verify(self.root / "consumer", "notes/receipt.json")["count"], 5)
        # Nonqualifying status must never permit omitted samples or fabricated targets.
        self.write("test.csv", "sample_id,target,prediction\n")
        with self.assertRaises(ValueError):
            self.publish(spec)
        contract.verify(self.root / "consumer", "notes/receipt.json")

    def test_publication_requires_declared_top_level_consumer_files(self):
        spec = self.delivery()
        for root_artifacts in ([], ["delivery/report.md"], ["missing.md"], ["report.md", "report.md"]):
            changed = copy.deepcopy(spec)
            changed["root_artifacts"] = root_artifacts
            with self.subTest(root_artifacts=root_artifacts), self.assertRaises(ValueError):
                self.publish(changed)
            self.assertFalse((self.root / "consumer").exists())

    def test_bad_csvs_rejected_before_publication(self):
        spec = self.delivery()
        for csv in ["sample_id,target,prediction\n19,-4,nan\n", "sample_id,target,prediction\n19,-2,-3\n",
                    "sample_id,target,prediction\n19,-4,-3\n19,-4,-3\n",
                    "sample_id,target,prediction\n25,-2,-1\n", "sample_id,target,prediction\n",
                    "sample_id,target,prediction\n19,-4,-3,extra\n"]:
            self.write("test.csv", csv)
            with self.assertRaises(ValueError):
                self.publish(spec)
            self.assertFalse((self.root / "consumer").exists())

    def test_published_consumer_references(self):
        spec = self.delivery()
        self.write("coverage.json", {"tables": [{"path": "run/private/train.csv"}]})
        with self.assertRaises(ValueError):
            self.publish(spec)
        self.assertFalse((self.root / "consumer").exists())

    def test_safe_destinations_and_conflicts(self):
        spec = self.delivery()
        for name in ["../escape", "/absolute", "delivery//alias", "delivery"]:
            changed = copy.deepcopy(spec)
            changed["artifacts"][name] = "report.md"
            with self.assertRaises(ValueError):
                self.publish(changed)
            self.assertFalse((self.root / "consumer").exists())
        self.write("consumer/report.md", "previous scientific record\n")
        with self.assertRaises(ValueError):
            self.publish(spec)
        self.assertFalse((self.root / "consumer/delivery").exists())

    def test_symlink_destination_rejected(self):
        spec = self.delivery()
        (self.root / "consumer").mkdir()
        (self.root / "consumer/delivery").symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.publish(spec)

    def test_symlink_source_rejected(self):
        spec = self.delivery()
        (self.root / "alias.csv").symlink_to(self.root / "train.csv")
        spec["artifacts"]["delivery/train.csv"] = "alias.csv"
        with self.assertRaisesRegex(ValueError, "source artifact is a symlink"):
            self.publish(spec)
        self.assertFalse((self.root / "consumer/delivery").exists())

    def test_changed_artifact_invalidates_receipt(self):
        self.publish(self.delivery())
        self.write("consumer/delivery/test.csv", "tampered\n")
        with self.assertRaises(ValueError):
            contract.verify(self.root / "consumer", "notes/receipt.json")

    def test_receipt_cannot_replace_artifact(self):
        self.write("delivery.json", self.delivery())
        with self.assertRaises(ValueError):
            contract.publish(self.root / "delivery.json", self.root / "consumer", "report.md")

    def test_cli_and_no_cwd_dependency(self):
        self.write("study.json", self.spec)
        script = Path(contract.__file__).resolve()
        result = subprocess.run([sys.executable, "-B", str(script), "convert", "--manifest", str(self.manifest),
                                 "--root", str(self.root / "converted")], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["feature_count"], 2)

    def test_cli_failure_is_nonzero_without_outputs(self):
        self.spec["samples"] = self.spec["samples"][:-1]
        self.write("study.json", self.spec)
        result = subprocess.run([sys.executable, "-B", str(Path(contract.__file__).resolve()), "convert",
                                 "--manifest", str(self.manifest), "--root", str(self.root / "converted")],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("entire energy table", result.stderr)
        self.assertFalse((self.root / "converted").exists())


if __name__ == "__main__":
    unittest.main()
