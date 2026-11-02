"""Regression tests for sibling-root study-manifest construction."""
import json
from pathlib import Path
import tempfile
import unittest

import make_study_manifest as builder


class ManifestBuilderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.encodes = self.root / "encodes" / "batch-1"
        self.fit = self.root / "fit"
        self.encodes.mkdir(parents=True)
        (self.root / "Energy.dat").write_text("1 -4\n2 -3\n")
        (self.root / "split.json").write_text(json.dumps(
            {"splits": {"train": [1], "selection": [2], "test": [1, 2]}}))
        (self.root / "basis.dat").write_text("basis\n")
        samples = []
        results = []
        for sid in (1, 2):
            run = self.encodes / str(sid)
            run.mkdir()
            (run / "features").write_text("1 #npara\n1 0\n")
            (run / "log").write_text("PASP is finished gracefully\n")
            (run / "exit").write_text("0\n")
            samples.append({"id": sid, "features": f"{sid}/features", "basis_file": "../../basis.dat",
                            "log": f"{sid}/log", "exit_code_file": f"{sid}/exit"})
            results.append({"id": sid, "status": "ok"})
        self.batch = self.encodes / "batch.json"
        self.batch.write_text(json.dumps({"complete": True, "results": results, "samples": samples}))

    def test_sibling_roots_are_normalized_from_batch_root(self):
        out = self.fit / "study.json"
        result = builder.build(self.batch, out, str(self.root / "Energy.dat"),
                               str(self.root / "split.json"), str(self.root / "basis.dat"),
                               "none", 1.0, False, None)
        self.assertEqual(len(result["samples"]), 2)
        manifest = json.loads(out.read_text())
        self.assertTrue(manifest["samples"][0]["features"].startswith("../encodes/"))
        self.assertFalse(manifest["samples"][0]["features"].startswith("/"))
        self.assertEqual(json.loads(out.read_text()), result)

    def test_failed_batch_and_existing_output_are_blocked(self):
        data = json.loads(self.batch.read_text())
        data["results"][0]["status"] = "failed"
        self.batch.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            builder.build(self.batch, self.fit / "study.json", str(self.root / "Energy.dat"),
                          str(self.root / "split.json"), str(self.root / "basis.dat"),
                          "none", 1.0, False, None)
        self.batch.write_text(json.dumps({"complete": True, "results": [{"id": 1, "status": "ok"},
                                                                      {"id": 2, "status": "ok"}],
                                         "samples": data["samples"]}))
        out = self.fit / "study.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text("existing\n")
        with self.assertRaises(ValueError):
            builder.build(self.batch, out, str(self.root / "Energy.dat"),
                          str(self.root / "split.json"), str(self.root / "basis.dat"),
                          "none", 1.0, False, None)


if __name__ == "__main__":
    unittest.main()
