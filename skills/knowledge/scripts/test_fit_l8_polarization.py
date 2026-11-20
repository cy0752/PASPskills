import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HAS_NUMPY = importlib.util.find_spec("numpy") is not None
SCRIPT = Path(__file__).with_name("fit_l8_polarization.py")


@unittest.skipUnless(HAS_NUMPY, "NumPy required for L8 fitting")
class L8FitTest(unittest.TestCase):
    def write_state(self, directory, dipole, *, converged=True):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "POSCAR").write_text(
            "test\n1\n10 0 0\n1 9 0\n0 0 8\nFe\n2\nDirect\n0 0 0\n0.2 0 0\n"
        )
        convergence = "aborting loop because EDIFF is reached" if converged else "EDIFF was not reached"
        (directory / "OUTCAR").write_text(
            " NSW = 0\n direct lattice vectors                  reciprocal lattice vectors\n"
            " 10 0 0 0.1 0 0\n 1 9 0 0 0.1 0\n 0 0 8 0 0 0.1\n"
            " ---- Iteration 1(10) ----\n"
            f" {convergence}\n Ionic dipole moment: p[ion]=(0 0 0)\n"
            f" Total electronic dipole moment: p[elc]=({dipole[0]} {dipole[1]} {dipole[2]})\n"
            " POSITION                       TOTAL-FORCE (eV/Angst)\n -----\n"
            " 0 0 0 0 0 0\n 2 0 0 0 0 0\n -----\n General timing and accounting\n"
        )

    def fit(self, workspace, manifest, output="fit"):
        manifest_path = workspace / "states.json"
        manifest_path.write_text(json.dumps(manifest))
        return subprocess.run(
            [sys.executable, SCRIPT, "fit", manifest_path, workspace / output],
            check=False, capture_output=True, text=True,
        )

    def test_cli_recovers_both_tensors_and_writes_pasp_row_order(self):
        import numpy as np

        manifest = json.loads(subprocess.check_output([sys.executable, SCRIPT, "template", "both"]))
        manifest["pij"]["image_j"] = [1, 0, 0]
        site_tensor = np.array([[0.1, 0.3, -0.4], [-0.05, 0.06, 0.07], [-0.05, -0.36, 0.33],
                                [0.1, -0.05, 0.07], [0.05, 0.02, 0.02], [-0.02, 0.01, 0.09]])
        directions = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1),
                      "xpy": (1, 1, 0), "xmy": (1, -1, 0), "xpz": (1, 0, 1),
                      "xmz": (1, 0, -1), "ypz": (0, 1, 1), "ymz": (0, 1, -1)}
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            expected_pairs = []
            for index, states in enumerate(manifest["pij"]["states"].values(), 1):
                tensor = np.array([0.01, 0.015, -0.02]) * index
                expected_pairs.append(tensor)
                for signs, directory in states.items():
                    i, j = (1 if sign == "+" else -1 for sign in signs)
                    dipole = 2.0 + i * 0.12 + j * 0.08 + i * j * tensor
                    if signs == "+-":
                        dipole += [1, 9, 0]  # A Berry quantum in the skew cell.
                    self.write_state(work / directory, dipole)

            for label, states in manifest["pi"]["states"].items():
                direction = np.asarray(directions[label])
                x, y, z = direction / np.linalg.norm(direction)
                even = np.array([x*x, y*y, z*z, 2*x*y, 2*x*z, 2*y*z]) @ site_tensor
                for sign, directory in states.items():
                    self.write_state(work / directory, 2.5 + even + (0.16 if sign == "plus" else -0.16))

            result = self.fit(work, manifest)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((work / "fit/fit_report.json").read_text())
            self.assertEqual(report["pij"]["groups"]["xx"]["states"]["+-"]["berry_shift"], [0, 1, 0])
            self.assertEqual(report["pi"]["rank"], 6)
            lines = (work / "fit/GKNB.fdf").read_text().splitlines()
            pair = lines.index("%block GKNB_inter_site")
            single = lines.index("%block GKNB_single_site")
            self.assertEqual([float(x) for x in lines[pair + 3].split()], [12.0, 0.0, 0.0])
            np.testing.assert_allclose(
                [[float(x) for x in row.split("#")[0].split()] for row in lines[pair+7:pair+16]], expected_pairs,
            )
            np.testing.assert_allclose(
                [[float(x) for x in row.split("#")[0].split()] for row in lines[single+6:single+12]], site_tensor,
            )
            repeated = self.fit(work, manifest)
            self.assertNotEqual(repeated.returncode, 0)
            self.assertIn("already exists", repeated.stderr)

    def test_refuses_unconverged_or_ambiguous_inputs(self):
        manifest = {"pi": {"site": 1, "states": {"x": {"plus": "plus", "minus": "minus"}}}}
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            self.write_state(work / "plus", [1, 2, 3])
            self.write_state(work / "minus", [1, 2, 7], converged=False)
            result = self.fit(work, manifest)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing final EDIFF convergence", result.stderr)
            self.assertFalse((work / "fit").exists())

            self.write_state(work / "minus", [1, 2, 7])
            result = self.fit(work, manifest)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ambiguous automatic Berry branch", result.stderr)
            self.assertFalse((work / "fit").exists())


if __name__ == "__main__":
    unittest.main()
