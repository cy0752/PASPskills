"""Synthetic regression tests; no PASP execution or scientific acceptance."""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import check_delivery as delivery
import l2_validate_inputs as l2


CELL = """NumberOfAtoms 1
number_of_species 1
%block LatticeVectors
2 0 0
0 2 0
0 0 2
%endblock LatticeVectors
%block AtomicCoordinatesAndAtomicSpecies
0 0 0 1
%endblock AtomicCoordinatesAndAtomicSpecies
"""
UNIT = """%block unit_cell_in_Ang
2 0 0
0 2 0
0 0 2
%endblock unit_cell_in_Ang
"""
INPUT = """Model magnon
%include cell.str
%include unit_cell.str
Read_init_spin T
spin_lat.general_J T
number_of_qpoints 3
%block qpoints.magnon
0 0 0
0.5 0 0
%endblock qpoints.magnon
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
EXCHANGE = "1\n2 0 0\n0 2 0\n0 0 2\n1 0.01 0 0 0 0.01 0 0 0 0.01 1 1 0 0 0 2 0 0\n0\n0\n0\n0\n"


class Workspace(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value if isinstance(value, str) else json.dumps(value))
        return path


class Inputs(Workspace):
    def setUp(self):
        super().setUp()
        for name, text in {"PASP.input": INPUT, "cell.str": CELL, "unit_cell.str": UNIT,
                           "spin_exchange.dat": EXCHANGE, "spin3.in": "1 0 0 1\n\n"}.items():
            self.write(name, text)

    def check(self):
        return l2.validate(self.root, "magnon")

    def test_valid(self):
        self.assertEqual(self.check().errors, [])

    def test_left_handed_primitive(self):
        self.write("unit_cell.str", UNIT.replace("2 0 0", "-2 0 0"))
        self.assertIn("right-handed", " ".join(self.check().errors))

    def test_singular_primitive(self):
        self.write("unit_cell.str", UNIT.replace("2 0 0", "0 0 0"))
        self.assertIn("nonsingular", " ".join(self.check().errors))

    def test_noninteger_positive_volume(self):
        self.write("unit_cell.str", UNIT.replace("2 0 0", "2.125 0 0"))
        self.write("spin_exchange.dat", EXCHANGE.replace("2 0 0\n", "2.125 0 0\n", 1))
        self.assertEqual(self.check().errors, [])

    def test_raw_comments_and_internal_blank(self):
        for mark in ("# comment", "! comment", "; comment", ""):
            with self.subTest(mark=mark):
                self.write("spin_exchange.dat", EXCHANGE.replace("\n0\n0\n0\n0\n", "\n" + mark + "\n0\n0\n0\n0\n"))
                self.assertTrue(self.check().errors)

    def test_missing_derivative_count(self):
        self.write("spin_exchange.dat", "\n".join(EXCHANGE.splitlines()[:5]) + "\n")
        self.assertIn("dJ/du", " ".join(self.check().errors))

    def test_optional_trailing_counts(self):
        self.write("spin_exchange.dat", "\n".join(EXCHANGE.splitlines()[:6]) + "\n")
        result = self.check()
        self.assertEqual(result.errors, [])
        self.assertEqual(len(result.warnings), 3)

    def test_spin_raw_and_finite(self):
        for text in ("# comment\n1 0 0 1\n", "1 0 nan 1\n", "2 0 0 1\n", "1 0 0 1\n2 0 0 1\n"):
            with self.subTest(text=text):
                self.write("spin3.in", text)
                self.assertTrue(self.check().errors)

    def test_include_relative_to_run_root(self):
        self.write("sub/control.fdf", "%include leaf.fdf\n")
        self.write("leaf.fdf", "number_of_qpoints 4\n")
        self.write("sub/leaf.fdf", "number_of_qpoints 1\n")
        self.write("PASP.input", "%include sub/control.fdf\n" + INPUT)
        result = self.check()
        self.assertEqual(result.errors, [])
        self.assertTrue(result.warnings)

    def test_include_cycle(self):
        self.write("cell.str", "%include PASP.input\n")
        self.assertIn("cycle", " ".join(self.check().errors))

    def test_effective_first_declaration(self):
        self.write("PASP.input", "number_of_qpoints 1\n" + INPUT)
        self.assertIn("at least 2", " ".join(self.check().errors))

    def test_wrong_kind_not_masked_by_later(self):
        self.write("PASP.input", "qpoints.magnon 0\n" + INPUT)
        self.assertIn("wrong scalar/block kind", " ".join(self.check().errors))

    def test_bad_boolean_and_nonfinite_exchange(self):
        self.write("PASP.input", INPUT.replace("general_J T", "general_J perhaps"))
        self.assertIn("boolean", " ".join(self.check().errors))
        self.write("PASP.input", INPUT)
        self.write("spin_exchange.dat", EXCHANGE.replace("0.01", "NaN"))
        self.assertIn("non-finite", " ".join(self.check().errors))

    def test_spin_lattice_mode_width(self):
        self.write("PASP.input", INPUT.replace("Model magnon", "Model Spin_lattice_interaction"))
        self.assertEqual(l2.validate(self.root, "spin-lattice").errors, [])
        self.write("PASP.input", INPUT.replace("Model magnon", "Model Spin_lattice_interaction").replace("general_J T", "general_J F"))
        self.assertIn("expects 10", " ".join(l2.validate(self.root, "spin-lattice").errors))

    def test_derivative_missing_j(self):
        prefix = "\n".join(EXCHANGE.splitlines()[:5])
        self.write("spin_exchange.dat", prefix + "\n1\n1 2\n")
        self.assertIn("missing J", " ".join(self.check().errors))


class Delivery(Workspace):
    def setUp(self):
        super().setUp()
        self.write("run/log.txt", "synthetic log, not a PASP run")
        self.value = {"systems": [{"name": "sample", "log": "run/log.txt", "pairs": ["nested/p"]}],
                      "pairs": [{"system": "sample", "pair": "nested/p", "delta": 0.25}]}
        self.schema = {"type": "object", "required": ["systems", "pairs"], "properties": {
            "systems": {"type": "array", "uniqueBy": ["name"], "expectedKeys": [["sample"]],
                        "items": {"type": "object", "required": ["name", "log", "pairs"], "properties": {
                            "name": {"type": "string"}, "log": {"type": "string", "pathKind": "file"},
                            "pairs": {"type": "array", "uniqueBy": [], "expectedKeys": ["nested/p"],
                                      "items": {"type": "string"}}}}},
            "pairs": {"type": "array", "uniqueBy": ["system", "pair"], "expectedKeys": [["sample", "nested/p"]],
                      "items": {"type": "object", "required": ["system", "pair", "delta"], "properties": {
                          "system": {"type": "string"}, "pair": {"type": "string"}, "delta": {"type": "number"}}}}}}

    def run_check(self, *extra):
        self.write("delivery.json", self.value)
        self.write("contract.json", self.schema)
        argv = ["check_delivery.py", str(self.root / "delivery.json"), str(self.root / "contract.json"),
                "--root", str(self.root), *extra]
        with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as out:
            code = delivery.main()
        return code, json.loads(out.getvalue())

    def test_valid_cli(self):
        self.assertEqual(self.run_check()[0], 0)

    def test_object_instead_of_array(self):
        self.value["systems"] = {"sample": self.value["systems"][0]}
        self.assertEqual(self.run_check()[0], 1)

    def test_missing_duplicate_extra_coverage(self):
        original = copy.deepcopy(self.value)
        for records in ([], original["pairs"] * 2, original["pairs"] + [{"system": "sample", "pair": "extra", "delta": 1}]):
            with self.subTest(records=records):
                self.value["pairs"] = records
                self.assertEqual(self.run_check()[0], 1)

    def test_required_missing_and_boolean_number(self):
        del self.value["systems"][0]["name"]
        self.value["pairs"][0]["delta"] = True
        code, report = self.run_check()
        self.assertEqual(code, 1)
        self.assertGreaterEqual(len(report["errors"]), 2)

    def test_missing_empty_escape_and_directory_as_file(self):
        self.write("empty", "")
        for path in ("missing", "empty", "../outside", "run"):
            with self.subTest(path=path):
                self.value["systems"][0]["log"] = path
                self.assertEqual(self.run_check()[0], 1)

    def test_symlink_escape(self):
        (self.root / "link").symlink_to(self.root.parent)
        self.value["systems"][0]["log"] = "link/check_delivery.py"
        self.assertEqual(self.run_check()[0], 1)

    def test_duplicate_nonfinite_and_overflow_json(self):
        for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":1e999}'):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    delivery.load(self.write("bad.json", raw))

    def test_unknown_contract_keyword(self):
        self.schema["requiredFields"] = []
        self.assertEqual(self.run_check()[0], 1)

    def test_manifest_and_changed_artifact(self):
        manifest = self.write("hashes.json", {"run/log.txt": delivery.digest(self.root / "run/log.txt")})
        self.assertEqual(self.run_check("--hashes", str(manifest))[0], 0)
        self.write("run/log.txt", "modified")
        self.assertEqual(self.run_check("--hashes", str(manifest))[0], 1)

    def test_container_repair_zero_drift(self):
        old = copy.deepcopy(self.value)
        old["systems"] = {v["name"]: v for v in old["systems"]}
        previous = self.write("previous.json", old)
        flags = ("--previous", str(previous), "--array-repair", "/systems:name")
        self.assertEqual(self.run_check(*flags)[0], 0)
        self.value["pairs"][0]["delta"] = 0.5
        self.assertEqual(self.run_check(*flags)[0], 1)

    def test_repair_identity_not_silently_dropped(self):
        old = copy.deepcopy(self.value)
        old["systems"] = {"different": old["systems"][0]}
        previous = self.write("previous.json", old)
        self.assertEqual(self.run_check("--previous", str(previous), "--array-repair", "/systems:name")[0], 1)

    def test_duplicate_expected_inventory_rejected(self):
        self.schema["properties"]["systems"]["expectedKeys"] *= 2
        self.assertEqual(self.run_check()[0], 1)

    def test_exact_previous_comparison_and_const(self):
        previous = self.write("previous.json", self.value)
        self.assertEqual(self.run_check("--previous", str(previous))[0], 0)
        self.schema["properties"]["systems"]["items"]["properties"]["name"]["const"] = "other"
        self.assertEqual(self.run_check()[0], 1)

    def test_directory_and_repair_requires_previous(self):
        self.schema["properties"]["systems"]["items"]["properties"]["log"]["pathKind"] = "directory"
        self.value["systems"][0]["log"] = "run"
        self.assertEqual(self.run_check()[0], 0)
        self.assertEqual(self.run_check("--array-repair", "/systems:name")[0], 1)


if __name__ == "__main__":
    unittest.main()
