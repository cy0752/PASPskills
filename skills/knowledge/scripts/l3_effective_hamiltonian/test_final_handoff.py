import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parent))
import final_handoff


class FinalHandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        model = {key: ("encodes" if key == "encoding_root" else
                       "method6-inputs" if key == "encoding_template" else
                       f"{key}.dat") for key in final_handoff.MODEL_KEYS if key != "energy_divisor"}
        model["energy_divisor"] = 2
        self.write("fgt-model.json", model)
        self.write("fgt-coverage.json", {"status": "qualifying", "passed": True})
        self.write("report.md", "native handoff\n")
        for name in model.values():
            if not isinstance(name, str):
                continue
            if name in ("encodes", "method6-inputs"):
                (self.root / name).mkdir()
                self.write(f"{name}/PASP.input", "synthetic\n")
            else:
                self.write(name, "synthetic\n")
        for split in final_handoff.SPLITS:
            self.write(f"{split}_predictions.csv", "sample_id,target,prediction\n0,1,1\n")

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")

    def test_valid_qualifying_package(self):
        receipt = final_handoff.validate(self.root)
        self.assertEqual(receipt["status"], "qualifying")
        self.assertEqual(receipt["artifacts"]["predictions"]["train"]["count"], 1)

    def test_cli_writes_and_reuses_receipt(self):
        self.assertEqual(final_handoff.main(["--root", str(self.root)]), 0)
        receipt = self.root / "final-handoff.json"
        self.assertTrue(receipt.is_file())
        self.assertEqual(final_handoff.main(["--root", str(self.root)]), 0)

    def test_nonqualifying_status_preserves_failure(self):
        self.write("fgt-coverage.json", {
            "status": "nonqualifying", "fgt_search_checks": {
                "passed": False, "errors": ["pooled_r2"]
            }
        })
        self.assertEqual(final_handoff.validate(self.root)["status"], "nonqualifying")

    def test_missing_native_artifact_fails(self):
        (self.root / "lm_file.dat").unlink()
        with self.assertRaises(ValueError):
            final_handoff.validate(self.root)

    def test_symlinked_artifact_fails(self):
        target = self.root / "outside.dat"
        target.write_text("outside\n", encoding="utf-8")
        (self.root / "lm_file.dat").unlink()
        (self.root / "lm_file.dat").symlink_to(target)
        with self.assertRaises(ValueError):
            final_handoff.validate(self.root)

    def test_symlinked_root_fails(self):
        link = self.root.parent / (self.root.name + "-link")
        link.symlink_to(self.root, target_is_directory=True)
        self.addCleanup(link.unlink)
        with self.assertRaises(ValueError):
            final_handoff.validate(link)


if __name__ == "__main__":
    unittest.main()
