#!/usr/bin/env python3
"""Deterministic preflight for PASP L2 spin-model input packages.

This checker reads only the supplied package and uses the effective FDF records
after ordinary ``%include`` expansion.  It catches shape, count, finite-number,
and cross-file dependency mistakes before a verifier or PASP run.  It does not
judge pair provenance, magnetic ground states, exchange mapping, spin scale, or
any other scientific choice.

Usage::

    python l2_validate_inputs.py RUN_DIR --workflow magnon

Exit status is non-zero when an error is found.  The JSON report is written to
stdout so both Claude Code and Codex can consume the same result without a
third-party dependency.

The contracts mirror the PASP source snapshot inspected on 2026-09-24:
``Latticemodel/src/spin_lat.F90`` ``read_exchange_para`` (J -> dJ/du -> SIA ->
DMI -> quadratic sections), ``spinw.f90`` ``read_spinw`` and
``read_spin3.f90``; ``read_input.F90:read_unit_cell_str`` (handedness) and
``fdf/fdf.f:fdf_open`` (includes relative to process working directory).
These are source-snapshot assumptions, not proof of the installed binary version.
The script remains standalone when that source tree is
absent; source inspection is not a runtime dependency.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path


class CheckFailure(Exception):
    pass


def norm(label: str) -> str:
    # FDF labels are punctuation-insensitive, including the leading % on
    # directives (see the PASP fdf lexer).  Keep this local and predictable.
    return re.sub(r"[_.%\-]", "", label).lower()


def finite(token: str) -> float:
    value = float(token.replace("D", "E").replace("d", "e"))
    if not math.isfinite(value):
        raise ValueError("non-finite number")
    return value


def integer(token: str) -> int:
    if not re.fullmatch(r"[+-]?\d+", token):
        raise ValueError("integer required")
    return int(token)


def data_tokens(line: str) -> list[str]:
    # PASP's FDF lexer treats !, # and ; as comment starts.
    return re.split(r"[!#;]", line, maxsplit=1)[0].split()


@dataclass
class Record:
    key: str
    block: bool
    body: list[str]
    origin: str


class FDF:
    """Small, conservative reader for the ordinary FDF subset used here."""

    def __init__(self, path: Path):
        self.records: list[Record] = []
        self.root = path.resolve().parent
        self._read(path.resolve(), ())

    def _read(self, path: Path, stack: tuple[Path, ...]) -> None:
        if path in stack:
            raise CheckFailure("include cycle: " + " -> ".join(map(str, stack + (path,))))
        if len(stack) >= 32:
            raise CheckFailure("include depth exceeds 32")
        try:
            lines = path.read_text().splitlines()
        except OSError as exc:
            raise CheckFailure(f"cannot read {path}: {exc}") from exc
        i = 0
        while i < len(lines):
            tokens = data_tokens(lines[i])
            if not tokens:
                i += 1
                continue
            tag = norm(tokens[0])
            origin = f"{path}:{i + 1}"
            if tag == "include":
                if len(tokens) != 2:
                    raise CheckFailure(f"{origin}: %include needs one filename")
                self._read((self.root / tokens[1]).resolve(), stack + (path,))
                i += 1
                continue
            if tokens[0].startswith("%"):
                if tag != "block" or len(tokens) != 2:
                    raise CheckFailure(f"{origin}: unsupported FDF directive")
                key = norm(tokens[1])
                body: list[str] = []
                i += 1
                closed = False
                while i < len(lines):
                    row = data_tokens(lines[i])
                    if row and norm(row[0]) == "endblock":
                        if len(row) != 2 or norm(row[1]) != key:
                            raise CheckFailure(f"{origin}: mismatched %endblock")
                        closed = True
                        break
                    if row and row[0].startswith("%"):
                        raise CheckFailure(f"{path}:{i + 1}: nested directive in block")
                    body.append(lines[i])
                    i += 1
                if not closed:
                    raise CheckFailure(f"{origin}: unclosed block")
                self.records.append(Record(key, True, body, origin))
                i += 1
                continue
            self.records.append(Record(tag, False, [" ".join(tokens[1:])], origin))
            i += 1

    def first(self, key: str, block: bool | None = None) -> Record | None:
        wanted = norm(key)
        for record in self.records:
            if record.key == wanted:
                if block is not None and record.block != block:
                    raise CheckFailure(f"{record.origin}: first effective {key} has wrong scalar/block kind")
                return record
        return None

    def required(self, key: str, block: bool | None = None) -> Record:
        found = self.first(key, block)
        if found is None:
            raise CheckFailure(f"missing {key}")
        return found


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checks: list[str] = []

    def check(self, name: str, fn) -> None:
        try:
            fn()
        except (CheckFailure, ValueError, OSError, IndexError) as exc:
            self.errors.append(f"{name}: {exc}")
        else:
            self.checks.append(name)


def rows(record: Record) -> list[list[str]]:
    return [data_tokens(line) for line in record.body if data_tokens(line)]


def scalar(fdf: FDF, key: str) -> list[str]:
    return data_tokens(fdf.required(key, False).body[0])


def block_rows(fdf: FDF, key: str) -> list[list[str]]:
    return rows(fdf.required(key, True))


def matrix3(name: str, records: list[list[str]], integer_only: bool = False) -> list[list[float]]:
    if len(records) != 3 or any(len(row) != 3 for row in records):
        raise CheckFailure(f"{name} must contain exactly three rows of three values")
    out: list[list[float]] = []
    for row in records:
        vals = []
        for token in row:
            if integer_only:
                integer(token)
                vals.append(float(int(token)))
            else:
                vals.append(finite(token))
        out.append(vals)
    return out


def volume(m: list[list[float]]) -> float:
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
         - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
         + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def determinant(m: list[list[float]]) -> int:
    d = volume(m)
    if abs(d - round(d)) > 1e-9:
        raise CheckFailure("SuperCell determinant is not integral")
    return int(round(d))


def raw_rows(path: Path) -> list[list[str]]:
    """Conservative numeric-record subset, not an FDF comment parser.

    Trailing blanks are harmless. Internal blanks/comments are rejected rather
    than silently removed: dJ/du uses a physical character record. Other Fortran
    forms (commas, repetition, slash terminators) are outside this checker.
    """
    lines = path.read_text().splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    result = []
    for index, line in enumerate(lines, 1):
        if not line.strip() or re.search(r"[!#;,/*]", line):
            raise CheckFailure(f"{path.name}:{index}: use a complete numeric record without comments or internal blanks")
        result.append(line.split())
    return result


def parse_exchange(path: Path, workflow: str, unit_lattice: list[list[float]], report: Report,
                   general_j: bool = False) -> None:
    tokens = raw_rows(path)
    cursor = 0

    def take(label: str) -> list[str]:
        nonlocal cursor
        if cursor >= len(tokens):
            raise CheckFailure(f"spin_exchange.dat ended while reading {label}")
        row = tokens[cursor]
        cursor += 1
        return row

    def count(label: str) -> int:
        row = take(label)
        if len(row) != 1:
            raise CheckFailure(f"{label} count must be one integer")
        n = integer(row[0])
        if n < 0:
            raise CheckFailure(f"{label} count is negative")
        return n

    def optional_count(label: str) -> int:
        # PASP's reader treats EOF in the trailing optional sections as count 0.
        # Accept that compatible form, but expose it so callers can canonicalize
        # the file before promotion.
        if cursor >= len(tokens):
            report.warnings.append(f"{label} count omitted at EOF; PASP treats it as 0")
            return 0
        return count(label)

    n_j = count("J")
    lattice = [take("J lattice") for _ in range(3)]
    lattice = matrix3("spin_exchange J lattice", lattice)
    for a, b in zip(lattice, unit_lattice):
        if any(abs(x - y) > 1e-5 for x, y in zip(a, b)):
            raise CheckFailure("J lattice differs from unit_cell lattice")
    expected_width = 18 if general_j else 10
    for expected_id in range(1, n_j + 1):
        row = take(f"J entry {expected_id}")
        width = len(row)
        if width != expected_width and not (workflow == "magnon" and width == 10):
            raise CheckFailure(f"J entry {expected_id} has {width} fields; effective J mode expects {expected_width}")
        if integer(row[0]) != expected_id:
            raise CheckFailure(f"J entry id {row[0]} is not {expected_id}")
        for token in row[1:]:
            finite(token)
        if width == 18:
            integer(row[10]); integer(row[11])
        else:
            integer(row[2]); integer(row[3])

    ndj = count("dJ/du")
    for group in range(1, ndj + 1):
        head = take(f"dJ/du group {group}")
        if len(head) != 2 or integer(head[0]) != group:
            raise CheckFailure(f"dJ/du group {group} header must be `id J_id`")
        if not 1 <= integer(head[1]) <= n_j:
            raise CheckFailure("dJ/du refers to a missing J entry")
        matrix3("dJ/du cell", [take("dJ/du cell") for _ in range(3)])
        nebrow = take("dJ/du atom count")
        if len(nebrow) != 1 or integer(nebrow[0]) < 0:
            raise CheckFailure("dJ/du atom count must be non-negative")
        neb = integer(nebrow[0])
        for _ in range(2 * neb):
            row = take("dJ/du coordinate/derivative")
            if len(row) != 3:
                raise CheckFailure("dJ/du coordinate/derivative needs three values")
            for token in row:
                finite(token)

    nsia = optional_count("SIA")
    for group in range(nsia):
        head = take("SIA id")
        if len(head) != 1:
            raise CheckFailure("SIA id needs one integer")
        integer(head[0])
        matrix3("SIA local basis", [take("SIA local basis") for _ in range(3)])
        row = take("SIA parameter")
        if len(row) != 5:
            raise CheckFailure("SIA parameter needs five values")
        for token in row:
            finite(token)

    ndm = optional_count("DMI")
    for group in range(ndm):
        row = take("DMI entry")
        if len(row) != 12:
            raise CheckFailure("DMI entry needs 12 values")
        for token in row:
            finite(token)
        integer(row[0]); integer(row[4]); integer(row[5])

    nquad = optional_count("fourth-order")
    for group in range(nquad):
        row = take("fourth-order header")
        if len(row) != 5:
            raise CheckFailure("fourth-order header needs five values")
        integer(row[0]); kind = integer(row[1])
        if kind not in (1, 2, 3):
            raise CheckFailure("fourth-order type must be 1, 2, or 3")
        finite(row[2]); integer(row[3]); integer(row[4])
        coords = take("fourth-order coordinates")
        if len(coords) != 3 * (kind + 1):
            raise CheckFailure("fourth-order coordinate width disagrees with type")
        for token in coords:
            finite(token)
    if cursor != len(tokens):
        raise CheckFailure(f"unexpected data after fifth exchange section ({len(tokens) - cursor} rows)")
    if workflow == "magnon" and nquad != 0:
        raise CheckFailure("magnon requires fourth-order count 0")


def validate(run: Path, workflow: str) -> Report:
    report = Report()
    if workflow not in ("magnon", "spin-lattice"):
        report.errors.append("workflow: must be magnon or spin-lattice")
        return report
    try:
        fdf = FDF(run / "PASP.input")
    except CheckFailure as exc:
        report.errors.append(f"PASP.input: {exc}")
        return report
    report.check("FDF includes and block delimiters", lambda: None)
    seen = {}
    for record in fdf.records:
        if record.key in seen:
            report.warnings.append(f"{record.origin}: inactive duplicate {record.key}; first at {seen[record.key]}")
        else:
            seen[record.key] = record.origin

    def model_check() -> None:
        value = scalar(fdf, "Model")
        if not value or norm(value[0]) != norm(workflow if workflow == "magnon" else "Spin_lattice_interaction"):
            raise CheckFailure(f"Model must be {workflow}")
    report.check("Model route", model_check)

    species_count = [0]
    lattice: list[list[float]] = []
    natoms = [0]
    det = [1]

    def cell_check() -> None:
        natoms[0] = integer(scalar(fdf, "NumberOfAtoms")[0])
        if natoms[0] <= 0:
            raise CheckFailure("NumberOfAtoms must be positive")
        nsp = integer(scalar(fdf, "number_of_species")[0])
        species_count[0] = nsp
        if nsp <= 0:
            raise CheckFailure("number_of_species must be positive")
        lattice[:] = matrix3("cell lattice", block_rows(fdf, "LatticeVectors"))
        if volume(lattice) == 0:
            raise CheckFailure("cell lattice is singular")
        coords = block_rows(fdf, "AtomicCoordinatesAndAtomicSpecies")
        if len(coords) != natoms[0]:
            raise CheckFailure(f"coordinate rows {len(coords)} != NumberOfAtoms {natoms[0]}")
        for row in coords:
            if len(row) < 4:
                raise CheckFailure("coordinate row needs x y z species_id")
            for token in row[:3]:
                finite(token)
            sid = integer(row[3])
            if not 1 <= sid <= nsp:
                raise CheckFailure(f"species id {sid} outside 1..{nsp}")
    report.check("cell geometry and species", cell_check)

    def unit_structure_check() -> None:
        # When unit_cell.str is included, validate its optional atom contract
        # too.  PASP falls back to cell.str only when the primitive atom count
        # equals the analysis-cell count; do not silently accept a partial block.
        rec = fdf.first("unit_cell.na", False)
        atoms = fdf.first("Atoms_in_unit_cell_Ang", True)
        if rec is None and atoms is None:
            return
        if rec is None:
            raise CheckFailure("Atoms_in_unit_cell_Ang is present without unit_cell.na")
        uc_n = integer(data_tokens(rec.body[0])[0])
        if uc_n <= 0:
            raise CheckFailure("unit_cell.na must be positive")
        if atoms is None:
            if uc_n != natoms[0]:
                raise CheckFailure("unit_cell.na differs from NumberOfAtoms but primitive atom block is absent")
            return
        atom_rows = rows(atoms)
        if len(atom_rows) != uc_n:
            raise CheckFailure(f"unit-cell atom rows {len(atom_rows)} != unit_cell.na {uc_n}")
        for row in atom_rows:
            if len(row) < 4:
                raise CheckFailure("unit-cell atom row needs x y z species_id")
            for token in row[:3]:
                finite(token)
            sid = integer(row[3])
            if not 1 <= sid <= species_count[0]:
                raise CheckFailure("unit-cell species id outside Z_values")
    report.check("unit-cell atom shape", unit_structure_check)

    values: list[float] = []
    def species_check() -> None:
        z = block_rows(fdf, "Z_values")
        s = block_rows(fdf, "Spin_values")
        zvals = [integer(v) for row in z for v in row]
        values[:] = [finite(v) for row in s for v in row]
        if len(zvals) != species_count[0] or len(values) != species_count[0]:
            raise CheckFailure("Z_values and Spin_values must each have one value per species")
        if any(v < 0 for v in values) or any(v <= 0 or v > 118 for v in zvals):
            raise CheckFailure("invalid Z_values or negative Spin_values")
    report.check("species value lengths", species_check)

    def isa_check() -> None:
        data = [v for row in block_rows(fdf, "isaAB") for v in row]
        if len(data) != 2:
            raise CheckFailure("isaAB must be exactly one row with two species ids")
        ids = [integer(v) for v in data]
        if any(v < 1 or v > species_count[0] for v in ids):
            raise CheckFailure("isaAB species id outside Z_values")
        if any(values[v - 1] <= 0 for v in ids):
            raise CheckFailure("isaAB includes a species with Spin_values <= 0")
    report.check("isaAB shape and active species", isa_check)

    def supercell_check() -> None:
        det[0] = determinant(matrix3("SuperCell", block_rows(fdf, "SuperCell"), True))
        if det[0] == 0:
            raise CheckFailure("SuperCell determinant is zero")
    report.check("SuperCell geometry", supercell_check)

    def spin_check() -> None:
        read_init = fdf.first("Read_init_spin", False)
        if read_init is not None:
            enabled = norm(data_tokens(read_init.body[0])[0]) in ("t", "true", ".true.", "yes")
            if workflow != "magnon" and not enabled:
                return
        path = run / "spin3.in"
        if not path.is_file():
            raise CheckFailure("spin3.in is missing")
        expected = natoms[0] * abs(det[0])
        rows_ = raw_rows(path)
        if len(rows_) != expected:
            raise CheckFailure(f"spin3.in rows {len(rows_)} != |det(SuperCell)|*NumberOfAtoms {expected}")
        for i, row in enumerate(rows_, 1):
            if len(row) != 4 or integer(row[0]) != i:
                raise CheckFailure(f"spin3.in row {i} must be `index sx sy sz`")
            for token in row[1:]:
                finite(token)
    report.check("spin3 row count, indices, and finite values", spin_check)

    def unit_check() -> None:
        unit = block_rows(fdf, "unit_cell_in_Ang") if fdf.first("unit_cell_in_Ang", True) else block_rows(fdf, "LatticeVectors")
        unit = matrix3("unit lattice", unit)
        if volume(unit) <= 0:
            raise CheckFailure("unit lattice must be nonsingular and right-handed; transform coordinates and mapping with the basis")
        flag = fdf.first("spin_lat.general_J", False)
        enabled = False
        if flag is not None:
            value = data_tokens(flag.body[0])
            if len(value) != 1 or norm(value[0]) not in ("t", "true", "yes", "f", "false", "no"):
                raise CheckFailure("spin_lat.general_J must be a boolean")
            enabled = norm(value[0]) in ("t", "true", "yes")
        parse_exchange(run / "spin_exchange.dat", workflow, unit, report, enabled)
    report.check("spin_exchange structure and dependencies", unit_check)

    if workflow == "magnon":
        def magnon_check() -> None:
            read_init = scalar(fdf, "Read_init_spin")
            if not read_init or norm(read_init[0]) not in ("t", "true", ".true.", "yes"):
                raise CheckFailure("magnon requires Read_init_spin T")
            flag = scalar(fdf, "spin_lat.general_J")
            if not flag or norm(flag[0]) not in ("t", "true", ".true.", "yes"):
                raise CheckFailure("magnon packages must set spin_lat.general_J T")
            band_flag = fdf.first("spinw.use_block_BandLines", False)
            use_band = bool(band_flag and norm(data_tokens(band_flag.body[0])[0]) in ("t", "true", "yes"))
            if use_band:
                scale = scalar(fdf, "BandLinesScale")
                if not scale or norm(scale[0]) != "reciprocallatticevectors":
                    raise CheckFailure("BandLinesScale must use the final reciprocal lattice basis")
                q = block_rows(fdf, "BandLines")
                if len(q) < 2 or any(len(row) not in (4, 5) for row in q):
                    raise CheckFailure("BandLines needs at least two count/coordinate rows")
                counts = [integer(row[0]) for row in q]
                if counts[0] != 1 or any(n < 1 for n in counts):
                    raise CheckFailure("BandLines first count must be 1 and all counts positive")
                for row in q:
                    for token in row[1:4]:
                        finite(token)
            else:
                nq = integer(scalar(fdf, "number_of_qpoints")[0])
                if nq < 2:
                    raise CheckFailure("number_of_qpoints must be at least 2")
                q = block_rows(fdf, "qpoints.magnon")
                if len(q) != 2 or any(len(row) != 3 for row in q):
                    raise CheckFailure("qpoints.magnon must contain exactly two 3-value endpoints")
                for row in q:
                    for token in row:
                        finite(token)
        report.check("magnon matrix mode and q path", magnon_check)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--workflow", choices=("magnon", "spin-lattice"), default="magnon")
    args = parser.parse_args()
    report = validate(args.run_dir.resolve(), args.workflow)
    payload = {"status": "pass" if not report.errors else "fail",
               "workflow": args.workflow, "run_dir": str(args.run_dir.resolve()),
               "checks": report.checks, "warnings": report.warnings,
               "errors": report.errors}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not report.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
