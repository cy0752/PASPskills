#!/usr/bin/env python3
"""Rebase or validate PASP unit_cell.str against cell.str.

This helper is intentionally conservative. It can:
- reorder unit-cell lattice rows and Cartesian atom-coordinate components together;
- optionally reorder only atom-coordinate components to repair a known bad candidate;
- validate that cell.str and unit_cell.str share a consistent primitive/supercell
  relation under a user-provided relation matrix.

It does not decide the physical primitive cell. Use it after the primitive / axis
mapping has been confirmed by the user, a read-only structure-analysis subagent,
or another authoritative source.
"""

from __future__ import annotations

import argparse
import itertools
import math
from dataclasses import dataclass
from pathlib import Path


AXIS_INDEX = {"x": 0, "y": 1, "z": 2}


@dataclass
class Atom:
    coord: list[float]
    species_id: int
    symbol: str
    label: str | None = None


@dataclass
class CellStr:
    natoms: int
    nspecies: int
    lattice: list[list[float]]
    atoms: list[Atom]


@dataclass
class UnitCellStr:
    natoms: int
    lattice: list[list[float]]
    atoms: list[Atom]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebase/validate PASP unit_cell.str while keeping lattice and coordinates synchronized."
    )
    parser.add_argument("--cell", required=True, help="Reference cell.str path")
    parser.add_argument("--unit", required=True, help="Candidate unit_cell.str path")
    parser.add_argument("--output", help="Write rebased unit_cell.str to this path")
    parser.add_argument(
        "--relation",
        default="1 0 0;0 1 0;0 0 1",
        help=(
            "3x3 integer matrix mapping unit_cell lattice rows to cell.str lattice rows, "
            "used only for validation. This is NOT PASP's %block SuperCell. Default: identity"
        ),
    )
    parser.add_argument(
        "--supercell",
        help=(
            "Deprecated alias for --relation. Do not confuse this validation relation with "
            "PASP's %block SuperCell, which expands cell.str rather than unit_cell.str."
        ),
    )
    parser.add_argument(
        "--reorder-axes",
        help=(
            "Reorder BOTH unit-cell lattice rows and atom coordinate components. "
            "Example: y,z,x writes new x=old y, new y=old z, new z=old x."
        ),
    )
    parser.add_argument(
        "--reorder-atom-coords",
        help=(
            "Reorder ONLY atom coordinate components. Use only to repair a known candidate "
            "where lattice was already rebased but atom coordinates were left in another axis order."
        ),
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-4,
        help="Direct-coordinate matching tolerance. Default: 1e-4",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only report validation; do not require --output even if reorder options are given.",
    )
    return parser.parse_args()


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def block(lines: list[str], start: str, end: str) -> list[str]:
    found = False
    values: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.lower() == start.lower():
            found = True
            continue
        if stripped.lower() == end.lower():
            if found:
                return values
        if found and stripped:
            values.append(stripped)
    raise ValueError(f"Missing block {start} ... {end}")


def first_value(lines: list[str], key: str) -> str:
    key_lower = key.lower()
    for line in lines:
        parts = line.split()
        if parts and parts[0].lower() == key_lower and len(parts) >= 2:
            return parts[1]
    raise ValueError(f"Missing required key {key}")


def parse_matrix_rows(rows: list[str], name: str) -> list[list[float]]:
    matrix = []
    for row in rows:
        parts = row.split()
        if len(parts) < 3:
            raise ValueError(f"{name} row has fewer than 3 values: {row}")
        matrix.append([float(parts[0]), float(parts[1]), float(parts[2])])
    if len(matrix) != 3:
        raise ValueError(f"{name} must have exactly 3 rows; got {len(matrix)}")
    return matrix


def parse_cell(path: Path) -> CellStr:
    lines = read_lines(path)
    natoms = int(first_value(lines, "NumberOfAtoms"))
    nspecies = int(first_value(lines, "number_of_species"))
    lattice = parse_matrix_rows(block(lines, "%block LatticeVectors", "%endblock LatticeVectors"), "LatticeVectors")
    atom_rows = block(lines, "%block AtomicCoordinatesAndAtomicSpecies", "%endblock AtomicCoordinatesAndAtomicSpecies")
    atoms = []
    for row in atom_rows:
        parts = row.split()
        if len(parts) < 5:
            raise ValueError(f"Bad cell atom row: {row}")
        atoms.append(
            Atom(
                coord=[float(parts[0]), float(parts[1]), float(parts[2])],
                species_id=int(parts[3]),
                symbol=parts[4],
                label=parts[5] if len(parts) >= 6 else None,
            )
        )
    if len(atoms) != natoms:
        raise ValueError(f"cell.str declares {natoms} atoms but has {len(atoms)} atom rows")
    return CellStr(natoms=natoms, nspecies=nspecies, lattice=lattice, atoms=atoms)


def parse_unit(path: Path) -> UnitCellStr:
    lines = read_lines(path)
    natoms = int(first_value(lines, "unit_cell.na"))
    lattice = parse_matrix_rows(block(lines, "%block unit_cell_in_Ang", "%endblock unit_cell_in_Ang"), "unit_cell_in_Ang")
    atom_rows = block(lines, "%block Atoms_in_unit_cell_Ang", "%endblock Atoms_in_unit_cell_Ang")
    atoms = []
    for row in atom_rows:
        parts = row.split()
        if len(parts) < 4:
            raise ValueError(f"Bad unit-cell atom row: {row}")
        atoms.append(
            Atom(
                coord=[float(parts[0]), float(parts[1]), float(parts[2])],
                species_id=int(parts[3]),
                symbol=parts[4] if len(parts) >= 5 else f"S{parts[3]}",
                label=parts[5] if len(parts) >= 6 else None,
            )
        )
    if len(atoms) != natoms:
        raise ValueError(f"unit_cell.str declares {natoms} atoms but has {len(atoms)} atom rows")
    return UnitCellStr(natoms=natoms, lattice=lattice, atoms=atoms)


def parse_supercell(text: str) -> list[list[int]]:
    rows = [row.strip() for row in text.split(";") if row.strip()]
    matrix = []
    for row in rows:
        parts = row.split()
        if len(parts) != 3:
            raise ValueError(f"SuperCell row must have 3 integer values: {row}")
        matrix.append([int(part) for part in parts])
    if len(matrix) != 3:
        raise ValueError(f"SuperCell must have exactly 3 rows; got {len(matrix)}")
    return matrix


def parse_order(order: str) -> list[int]:
    axes = [axis.strip().lower() for axis in order.replace(",", " ").split()]
    if len(axes) == 1 and len(axes[0]) == 3:
        axes = list(axes[0])
    if len(axes) != 3 or set(axes) != {"x", "y", "z"}:
        raise ValueError("Axis order must be a permutation of x,y,z, e.g. y,z,x")
    return [AXIS_INDEX[axis] for axis in axes]


def reorder_vector(vector: list[float], order: list[int]) -> list[float]:
    return [vector[index] for index in order]


def reorder_unit(unit: UnitCellStr, lattice_order: list[int] | None, atom_order: list[int] | None) -> UnitCellStr:
    lattice = [row[:] for row in unit.lattice]
    atoms = [Atom(atom.coord[:], atom.species_id, atom.symbol, atom.label) for atom in unit.atoms]
    if lattice_order is not None:
        lattice = [reorder_vector(unit.lattice[index], lattice_order) for index in lattice_order]
        atoms = [Atom(reorder_vector(atom.coord, lattice_order), atom.species_id, atom.symbol, atom.label) for atom in atoms]
    if atom_order is not None:
        atoms = [Atom(reorder_vector(atom.coord, atom_order), atom.species_id, atom.symbol, atom.label) for atom in atoms]
    return UnitCellStr(unit.natoms, lattice, atoms)


def determinant_3x3(matrix: list[list[float]]) -> float:
    a = matrix
    return (
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    )


def matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [
        [sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)]
        for i in range(3)
    ]


def transpose(matrix: list[list[float]]) -> list[list[float]]:
    return [[matrix[j][i] for j in range(3)] for i in range(3)]


def inverse_3x3(matrix: list[list[float]]) -> list[list[float]]:
    det = determinant_3x3(matrix)
    if abs(det) < 1e-12:
        raise ValueError("Matrix is singular")
    a = matrix
    cof = [
        [a[1][1] * a[2][2] - a[1][2] * a[2][1], -(a[1][0] * a[2][2] - a[1][2] * a[2][0]), a[1][0] * a[2][1] - a[1][1] * a[2][0]],
        [-(a[0][1] * a[2][2] - a[0][2] * a[2][1]), a[0][0] * a[2][2] - a[0][2] * a[2][0], -(a[0][0] * a[2][1] - a[0][1] * a[2][0])],
        [a[0][1] * a[1][2] - a[0][2] * a[1][1], -(a[0][0] * a[1][2] - a[0][2] * a[1][0]), a[0][0] * a[1][1] - a[0][1] * a[1][0]],
    ]
    adj = transpose(cof)
    return [[adj[i][j] / det for j in range(3)] for i in range(3)]


def mat_vec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(matrix[i][j] * vector[j] for j in range(3)) for i in range(3)]


def cart_to_direct(coord: list[float], lattice_rows: list[list[float]]) -> list[float]:
    inv_transposed = inverse_3x3(transpose(lattice_rows))
    return mat_vec(inv_transposed, coord)


def fractional_delta(a: list[float], b: list[float]) -> list[float]:
    return [component - round(component) for component in [a[i] - b[i] for i in range(3)]]


def norm(vector: list[float]) -> float:
    return math.sqrt(sum(value * value for value in vector))


def validate(cell: CellStr, unit: UnitCellStr, relation: list[list[int]], tolerance: float) -> tuple[bool, list[str]]:
    messages: list[str] = []
    expected_lattice = matmul([[float(value) for value in row] for row in relation], unit.lattice)
    max_lattice_error = max(
        abs(expected_lattice[i][j] - cell.lattice[i][j]) for i in range(3) for j in range(3)
    )
    messages.append(f"max_lattice_error_ang = {max_lattice_error:.8g}")

    det = round(abs(determinant_3x3([[float(value) for value in row] for row in relation])))
    expected_atoms = unit.natoms * det
    messages.append(f"relation_det = {det}; expected_atoms = {expected_atoms}; cell_atoms = {cell.natoms}")
    if expected_atoms != cell.natoms:
        messages.append("FAIL: atom count does not match det(relation) * unit_cell.na")
        return False, messages

    unit_direct_by_species: dict[int, list[list[float]]] = {}
    for atom in unit.atoms:
        unit_direct_by_species.setdefault(atom.species_id, []).append(cart_to_direct(atom.coord, unit.lattice))

    max_direct_error = 0.0
    worst: str | None = None
    unmatched = 0
    for index, atom in enumerate(cell.atoms, start=1):
        direct = cart_to_direct(atom.coord, unit.lattice)
        candidates = unit_direct_by_species.get(atom.species_id, [])
        if not candidates:
            unmatched += 1
            if worst is None:
                worst = f"cell atom {index}: no unit atom with species {atom.species_id}"
            continue
        best = min(norm(fractional_delta(direct, candidate)) for candidate in candidates)
        max_direct_error = max(max_direct_error, best)
        if best > tolerance:
            unmatched += 1
            if worst is None:
                worst = f"cell atom {index}: direct error {best:.8g} exceeds tolerance {tolerance}"
    messages.append(f"max_direct_modulo_error = {max_direct_error:.8g}")
    if unmatched:
        messages.append(f"FAIL: {unmatched} cell atoms did not map to unit_cell atoms")
        if worst:
            messages.append(f"first_unmatched = {worst}")
        return False, messages

    if max_lattice_error > 1e-6:
        messages.append("FAIL: relation * unit lattice does not match cell lattice")
        return False, messages

    messages.append("PASS: cell.str is compatible with unit_cell.str under the provided relation")
    return True, messages


def write_unit(path: Path, unit: UnitCellStr) -> None:
    lines: list[str] = []
    lines.append(f"unit_cell.na {unit.natoms}")
    lines.append("")
    lines.append("%block unit_cell_in_Ang")
    for row in unit.lattice:
        lines.append("  " + "  ".join(f"{value:.12f}" for value in row))
    lines.append("%endblock unit_cell_in_Ang")
    lines.append("")
    lines.append("%block Atoms_in_unit_cell_Ang")
    for index, atom in enumerate(unit.atoms, start=1):
        label = atom.label if atom.label is not None else str(index)
        lines.append(
            "  "
            + "  ".join(f"{value:.12f}" for value in atom.coord)
            + f"  {atom.species_id}  {atom.symbol}  {label}"
        )
    lines.append("%endblock Atoms_in_unit_cell_Ang")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    cell = parse_cell(Path(args.cell))
    unit = parse_unit(Path(args.unit))
    relation_text = args.relation
    if args.supercell:
        relation_text = args.supercell
        print("WARNING: --supercell is deprecated; use --relation. This is a validation relation, not PASP %block SuperCell.")
    relation = parse_supercell(relation_text)

    lattice_order = parse_order(args.reorder_axes) if args.reorder_axes else None
    atom_order = parse_order(args.reorder_atom_coords) if args.reorder_atom_coords else None
    rebased = reorder_unit(unit, lattice_order, atom_order)

    ok, messages = validate(cell, rebased, relation, args.tolerance)
    for message in messages:
        print(message)

    if (lattice_order is not None or atom_order is not None) and not args.report_only:
        if not args.output:
            raise SystemExit("--output is required when reordering unless --report-only is set")
        write_unit(Path(args.output), rebased)
        print(f"wrote {args.output}")

    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
