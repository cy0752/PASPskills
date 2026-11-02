"""Synthetic receipt checks only; no PASP run or scientific acceptance."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

import check_four_state_native as native
import l2_validate_inputs as l2
import make_primitive_pair as primitive


CELL = """NumberOfAtoms 1
number_of_species 1
LatticeConstant 1 Ang
%block LatticeVectors
2 0 0
0 2 0
0 0 2
%endblock LatticeVectors
AtomicCoordinatesFormat NotScaledCartesianAng
%block AtomicCoordinatesAndAtomicSpecies
0 0 0 1 Fe 1
%endblock AtomicCoordinatesAndAtomicSpecies
"""
UNIT = """unit_cell.na 1
%block unit_cell_in_Ang
2 0 0
0 2 0
0 0 2
%endblock unit_cell_in_Ang
%block Atoms_in_unit_cell_Ang
0 0 0 1 Fe 1
%endblock Atoms_in_unit_cell_Ang
"""
MAGNON = """Model magnon
%include cell.str
%include unit_cell.str
Read_init_spin T
spin_lat.general_J T
spinw.use_block_BandLines T
BandLinesScale ReciprocalLatticeVectors
%block BandLines
1 0 0 0 G
2 0.5 0 0 X
2 0 0 0 G
%endblock BandLines
%block SuperCell
1 0 0
0 1 0
0 0 1
%endblock SuperCell
%block Z_values
26
%endblock Z_values
%block Spin_values
2
%endblock Spin_values
%block isaAB
1 1
%endblock isaAB
"""
LATTICE = "2 0 0\n0 2 0\n0 0 2\n"
NATIVE = "1 # units in eV and Ang\n" + LATTICE + "1 0.01 1 1 0 0 0 2 0 0\n0 # no dJ/du\n0\n0\n0\n"
FINAL = "1\n" + LATTICE + "1 0.01 0 0 0 0.01 0 0 0 0.01 1 1 0 0 0 2 0 0\n0\n0\n0\n0\n"
STATES = {"upup": "up_up", "updn": "up_dn", "dnup": "dn_up", "dndn": "dn_dn"}


class NativeReceipt(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.work = self.root / "work"
        self.work.mkdir()
        self.base = self.work / "extract"
        self.final = self.work / "final"
        for folder in (self.base, self.final):
            folder.mkdir()
        for target, original in STATES.items():
            payload = f"original {original}\n"
            self.put(self.source / "Material/pair-a" / original / "OSZICAR", payload)
            self.put(self.base / "J1" / target / "OSZICAR", payload)
        self.put(self.base / "cell.str", CELL)
        self.put(self.base / "unit_cell.str", UNIT)
        self.put(self.base / "PASP.input", "Model find_J_path_sym\ncal_spin_exchange T\n%include cell.str\n%include unit_cell.str\n")
        self.put(self.base / "spin_exchange.dat", NATIVE)
        self.put(self.base / "log.out", "\n".join(f"Reading file: J1/{s}/OSZICAR" for s in STATES))
        for name, content in {"PASP.input": MAGNON, "cell.str": CELL, "unit_cell.str": UNIT,
                              "spin_exchange.dat": FINAL, "spin3.in": "1 0 0 1\n"}.items():
            self.put(self.final / name, content)
        self.put(self.work / "evidence.txt", "one class, one member")
        self.put(self.work / "primitive.json", json.dumps({
            "source_cell": "source/Material/POSCAR", "source_lattice_ang": [[4, 0, 0], [0, 2, 0], [0, 0, 2]],
            "transformation": [[0.5, 0, 0], [0, 1, 0], [0, 0, 1]], "source_atom_count": 2,
            "primitive_atom_count": 1, "source_volume_ang3": 16, "primitive_volume_ang3": 8,
            "symprec_angstrom": [1e-5, 1e-4, 1e-3], "site_map": [1, 1], "species_map": [1],
            "image_map": [0, 1], "exchange_map": [{"final_row": 1,
                "endpoint_sites_1based": [1, 1], "endpoint_a_image": [0, 0, 0],
                "endpoint_b_image": [1, 0, 0], "endpoint_species": ["Fe", "Fe"]}],
            "spin_map": [1]}))
        self.delivery = {"materials": [{
            "name": "Material", "run_dir": "final", "inputs": list(("PASP.input", "cell.str", "unit_cell.str",
                "spin_exchange.dat", "spin3.in")), "primitive_cell_report": "primitive.json",
            "j_extraction": {"method": "pasp_native", "evidence_report": "evidence.txt",
                "final_exchange": "final/spin_exchange.dat", "runs": [{"input": "extract/PASP.input",
                    "log": "extract/log.out", "output": "extract/spin_exchange.dat",
                    "inputs": ["PASP.input", "cell.str", "unit_cell.str"] + [f"J1/{s}/OSZICAR" for s in STATES],
                    "quartet_map": [{"native_pair": 1, "source_pair": "Material/pair-a", "states": STATES}]}],
                "lineage": [{"final_row": 1, "native_output": "extract/spin_exchange.dat", "native_row": 1}]
            }}]}

    def put(self, target, content):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def check(self):
        self.put(self.work / "delivery.json", json.dumps(self.delivery))
        return native.check(self.work / "delivery.json", self.work, self.source)

    def test_valid_native_and_bandlines(self):
        self.assertEqual(self.check()["status"], "pass")
        self.assertEqual(l2.validate(self.final, "magnon").errors, [])

    def test_oszicar_byte_mismatch(self):
        self.put(self.base / "J1/updn/OSZICAR", "rewritten\n")
        with self.assertRaisesRegex(ValueError, "OSZICAR bytes differ"):
            self.check()

    def test_native_noncommensurate_cell_is_rejected(self):
        original = (self.base / "unit_cell.str").read_text()
        self.put(self.base / "unit_cell.str", original.replace("2 0 0", "2.1 0 0", 1))
        with self.assertRaisesRegex(ValueError, "native cell/unit_cell incompatible"):
            self.check()
        self.put(self.base / "unit_cell.str", original)

    def test_duplicate_lineage(self):
        self.delivery["materials"][0]["j_extraction"]["lineage"].append(copy.deepcopy(
            self.delivery["materials"][0]["j_extraction"]["lineage"][0]))
        with self.assertRaisesRegex(ValueError, "lineage row count mismatch"):
            self.check()

    def test_nonprimitive_cell_or_unit(self):
        for name in ("cell.str", "unit_cell.str"):
            with self.subTest(name=name):
                original = (self.final / name).read_text()
                if name == "cell.str":
                    changed = original.replace("NumberOfAtoms 1", "NumberOfAtoms 2").replace(
                        "0 0 0 1 Fe 1", "0 0 0 1 Fe 1\n1 0 0 1 Fe 2")
                else:
                    changed = original.replace("unit_cell.na 1", "unit_cell.na 2").replace(
                        "0 0 0 1 Fe 1", "0 0 0 1 Fe 1\n1 0 0 1 Fe 2")
                self.put(self.final / name, changed)
                with self.assertRaisesRegex(ValueError, "site/species order mismatch"):
                    self.check()
                self.put(self.final / name, original)

    def test_both_nonprimitive_despite_matching_inputs(self):
        self.put(self.final / "cell.str", CELL.replace("NumberOfAtoms 1", "NumberOfAtoms 2").replace(
            "0 0 0 1 Fe 1", "0 0 0 1 Fe 1\n1 0 0 1 Fe 2"))
        self.put(self.final / "unit_cell.str", UNIT.replace("unit_cell.na 1", "unit_cell.na 2").replace(
            "0 0 0 1 Fe 1", "0 0 0 1 Fe 1\n1 0 0 1 Fe 2"))
        with self.assertRaisesRegex(ValueError, "chemical translation reduction"):
            self.check()

    def test_bandlines_format_failure(self):
        self.put(self.final / "PASP.input", MAGNON.replace("1 0 0 0 G", "0 0 0 0 G"))
        self.assertIn("BandLines first count", " ".join(l2.validate(self.final, "magnon").errors))

    def test_scalar_delivery_lineage(self):
        self.put(self.final / "spin_exchange.dat", NATIVE.replace(" # units in eV and Ang", ""))
        self.assertEqual(self.check()["status"], "pass")

    def edit_exchange_map(self, **updates):
        file = self.work / "primitive.json"
        proof = json.loads(file.read_text())
        proof["exchange_map"][0].update(updates)
        self.put(file, json.dumps(proof))

    def test_long_image_cannot_be_replaced_by_minimum_image(self):
        # Both 0 and 2 Ang are exact images of the same site. Only one is
        # consistent with the report of the physical unwrapped bond.
        self.put(self.final / "spin_exchange.dat", FINAL.replace("0 0 0 2 0 0\n", "0 0 0 0 0 0\n"))
        with self.assertRaisesRegex(ValueError, "endpoint image mismatch"):
            self.check()

    def test_cross_lattice_endpoint_rejected_then_exact_rebuild_passes(self):
        native_before = (self.base / "spin_exchange.dat").read_bytes()
        self.put(self.final / "spin_exchange.dat", FINAL.replace("0 0 0 2 0 0\n", "0 0 0 2.0002 0 0\n"))
        with self.assertRaisesRegex(ValueError, "one unique primitive"):
            self.check()
        # Rebuild coordinates from the final site + integer image; J is not
        # recomputed or rescaled by this repair.
        self.put(self.final / "spin_exchange.dat", FINAL)
        self.assertEqual(self.check()["status"], "pass")
        self.assertEqual((self.base / "spin_exchange.dat").read_bytes(), native_before)

    def test_report_site_species_and_image_must_match_real_row(self):
        for update, message in [({"endpoint_sites_1based": [1, 2]}, "site mismatch"),
                                ({"endpoint_species": ["Fe", "Mn"]}, "species mismatch"),
                                ({"endpoint_b_image": [0, 0, 0]}, "image mismatch")]:
            with self.subTest(update=update):
                old = (self.work / "primitive.json").read_text()
                self.edit_exchange_map(**update)
                with self.assertRaisesRegex(ValueError, message):
                    self.check()
                self.put(self.work / "primitive.json", old)

    def test_explicit_two_image_report_with_common_translation(self):
        self.put(self.final / "spin_exchange.dat", FINAL.replace("0 0 0 2 0 0\n", "2 0 0 4 0 0\n"))
        self.edit_exchange_map(image_cells=[[1, 0, 0], [2, 0, 0]], final_sites_1based=[1, 1])
        self.assertEqual(self.check()["status"], "pass")

    def test_ambiguous_same_species_endpoint_rejected(self):
        with self.assertRaisesRegex(ValueError, "found 2"):
            native.map_endpoint([0, 0, 0], 1, np.eye(3) * 2,
                                np.array([[0, 0, 0], [0.0000001, 0, 0]]), [1, 1])

    def test_endpoint_maps_nonorthogonal_lattice_and_species(self):
        lattice = np.array([[2., 0, 0], [1, 3, 0], [.3, .4, 4]])
        frac = np.array([[.1, .2, .3], [.1, .2, .3]])
        image = np.array([2, -3, 1])
        mapped = native.map_endpoint((frac[1] + image) @ lattice, 2, lattice, frac, [1, 2])
        self.assertEqual(mapped["site"], 2)
        self.assertEqual(mapped["image"], image.tolist())
        self.assertLess(mapped["residual"], 1e-12)

    def test_incomplete_and_duplicate_report_rows_rejected(self):
        self.edit_exchange_map(final_row=2)
        with self.assertRaisesRegex(ValueError, "cover final rows exactly"):
            self.check()
        self.edit_exchange_map(final_row=1)
        file = self.work / "primitive.json"
        proof = json.loads(file.read_text())
        proof["exchange_map"].append(copy.deepcopy(proof["exchange_map"][0]))
        self.put(file, json.dumps(proof))
        with self.assertRaisesRegex(ValueError, "one object per final row"):
            self.check()

    def test_generate_dual_primitive_from_poscar(self):
        source = self.work / "POSCAR"
        self.put(source, """synthetic doubled cell
1
4 0 0
0 2 0
0 0 2
Fe
2
Direct
0 0 0
0.5 0 0
""")
        output = self.work / "generated"
        report = primitive.generate(source, output, 1e-4)
        self.assertEqual(report["source_atom_count"], 2)
        self.assertEqual(report["primitive_atom_count"], 1)
        self.assertEqual(report["exchange_map"], [])
        self.assertEqual({item["primitive_site"] for item in report["site_map"]}, {1})
        self.assertEqual(len({tuple(item["image"]) for item in report["image_map"]}), 2)
        self.assertIn("NumberOfAtoms 1", (output / "cell.str").read_text())
        self.assertIn("unit_cell.na 1", (output / "unit_cell.str").read_text())
        with self.assertRaises(FileExistsError):
            primitive.generate(source, output, 1e-4)

    def test_generator_rejects_split_chemical_species(self):
        source = self.work / "split.POSCAR"
        self.put(source, """synthetic doubled cell
1
4 0 0
0 2 0
0 0 2
Fe Fe
1 1
Direct
0 0 0
0.5 0 0
""")
        with self.assertRaisesRegex(ValueError, "duplicate element symbols"):
            primitive.generate(source, self.work / "split-output", 1e-4)


if __name__ == "__main__":
    unittest.main()
