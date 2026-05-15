#!/usr/bin/env python3
"""Prepare method-6 path-B inputs from VASP OUTCAR files.

This helper targets the common L3 starting point where the user already has:
- one or more converged OUTCAR files named either <id>.OUTCAR or stored under <id>/OUTCAR
- optionally one shared POSCAR describing the supercell comment/species/count order

For each sample, it writes a reusable input package:
- distortion.pos
- distortion.MAGMOM

Optionally it also writes a shared Energy.dat table for downstream fitting.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from extract_magmoms import normalize, parse_outcar_magmoms


TOTEN_RE = re.compile(r"TOTEN\s*=\s*([-+0-9.Ee]+)")
FLOAT_RE = re.compile(r"[-+]?\d+(?:\.\d*)?(?:[Ee][-+]?\d+)?|[-+]?\.\d+(?:[Ee][-+]?\d+)?")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract per-sample distortion.pos/distortion.MAGMOM packages from one "
            "OUTCAR or a directory of OUTCAR files for L3 method-6 path-B runs."
        )
    )
    parser.add_argument(
        "source",
        help="One OUTCAR file, a directory containing flat <id>.OUTCAR files, or numbered sample directories.",
    )
    parser.add_argument(
        "--poscar-reference",
        help=(
            "Optional reference POSCAR providing comment, species order, and atom counts. "
            "If omitted, species/counts are inferred from OUTCAR."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default="path_b_inputs",
        help="Directory that will receive per-sample subdirectories. Default: path_b_inputs",
    )
    parser.add_argument(
        "--pattern",
        default="*.OUTCAR",
        help="Glob used when source is a directory without numbered subdirectories. Default: *.OUTCAR",
    )
    parser.add_argument(
        "--primitive-cells",
        type=int,
        help="If set, also write Energy.dat with this first-line primitive-cell count.",
    )
    parser.add_argument(
        "--energy-out",
        default="Energy.dat",
        help="Energy table path relative to output-dir when --primitive-cells is set. Default: Energy.dat",
    )
    parser.add_argument(
        "--normalize-magmoms",
        action="store_true",
        help="Normalize nonzero magnetic vectors before writing distortion.MAGMOM.",
    )
    parser.add_argument(
        "--coordinate-mode",
        choices=("Cartesian", "Direct"),
        default="Cartesian",
        help="Coordinate mode used in written distortion.pos files. Default: Cartesian",
    )
    return parser.parse_args()


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def parse_poscar_reference(path: Path) -> tuple[str, list[str], list[int], int]:
    lines = read_lines(path)
    if len(lines) < 7:
        raise ValueError(f"{path} is too short to be a POSCAR reference")

    comment = lines[0].strip() or "Generated from POSCAR reference"
    species = lines[5].split()
    if not species:
        raise ValueError(f"{path} is missing species symbols on line 6")

    try:
        counts = [int(token) for token in lines[6].split()]
    except ValueError as exc:
        raise ValueError(f"{path} is missing integer species counts on line 7") from exc

    if len(species) != len(counts):
        raise ValueError(
            f"{path} has {len(species)} species symbols but {len(counts)} count entries"
        )

    natoms = sum(counts)
    return comment, species, counts, natoms


def parse_outcar_species_counts(path: Path) -> tuple[str, list[str], list[int], int]:
    lines = read_lines(path)

    counts: list[int] | None = None
    for line in lines:
        if "ions per type" in line:
            count_text = line.split("=", 1)[1]
            counts = [int(token) for token in count_text.split()]
            break
    if counts is None:
        raise ValueError(f"Failed to find 'ions per type' in {path}")

    species: list[str] = []
    seen: set[str] = set()
    for line in lines:
        match = re.search(r"VRHFIN\s*=\s*([A-Z][a-z]?)", line)
        if match:
            symbol = match.group(1)
            if symbol not in seen:
                seen.add(symbol)
                species.append(symbol)
            if len(species) == len(counts):
                break

    if len(species) != len(counts):
        raise ValueError(
            f"Failed to infer {len(counts)} species symbols from {path}; got {species}"
        )

    natoms = sum(counts)
    comment = " ".join(species)
    return comment, species, counts, natoms


def parse_last_lattice(lines: list[str], outcar: Path) -> list[list[float]]:
    indices = [index for index, line in enumerate(lines) if "direct lattice vectors" in line]
    if not indices:
        raise ValueError(f"No lattice-vector block found in {outcar}")

    start = indices[-1] + 1
    lattice: list[list[float]] = []
    for line in lines[start : start + 3]:
        values = [float(token) for token in FLOAT_RE.findall(line[:48])]
        if len(values) < 3:
            raise ValueError(f"Failed to parse lattice vector in {outcar}: {line}")
        lattice.append(values[:3])

    if len(lattice) != 3:
        raise ValueError(f"Failed to parse 3 lattice vectors from {outcar}")
    return lattice


def parse_last_positions(lines: list[str], outcar: Path, natoms: int) -> list[list[float]]:
    indices = [
        index
        for index, line in enumerate(lines)
        if "POSITION" in line and "TOTAL-FORCE" in line
    ]
    if not indices:
        raise ValueError(f"No POSITION/TOTAL-FORCE block found in {outcar}")

    start = indices[-1] + 2
    positions: list[list[float]] = []
    for line in lines[start : start + natoms]:
        values = [float(token) for token in FLOAT_RE.findall(line)]
        if len(values) < 3:
            raise ValueError(f"Failed to parse atomic position in {outcar}: {line}")
        positions.append(values[:3])

    if len(positions) != natoms:
        raise ValueError(
            f"{outcar} yielded {len(positions)} positions but reference POSCAR expects {natoms}"
        )
    return positions


def parse_last_toten(lines: list[str], outcar: Path) -> float:
    energy: float | None = None
    for line in lines:
        match = TOTEN_RE.search(line)
        if match:
            energy = float(match.group(1))
    if energy is None:
        raise ValueError(f"No TOTEN line found in {outcar}")
    return energy


def invert_3x3(matrix: list[list[float]]) -> list[list[float]]:
    a00, a01, a02 = matrix[0]
    a10, a11, a12 = matrix[1]
    a20, a21, a22 = matrix[2]

    c00 = a11 * a22 - a12 * a21
    c01 = -(a10 * a22 - a12 * a20)
    c02 = a10 * a21 - a11 * a20
    c10 = -(a01 * a22 - a02 * a21)
    c11 = a00 * a22 - a02 * a20
    c12 = -(a00 * a21 - a01 * a20)
    c20 = a01 * a12 - a02 * a11
    c21 = -(a00 * a12 - a02 * a10)
    c22 = a00 * a11 - a01 * a10

    det = a00 * c00 + a01 * c01 + a02 * c02
    if abs(det) < 1e-12:
        raise ValueError("Lattice matrix is singular; cannot convert to Direct coordinates")

    return [
        [c00 / det, c10 / det, c20 / det],
        [c01 / det, c11 / det, c21 / det],
        [c02 / det, c12 / det, c22 / det],
    ]


def mat_vec_mul(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1] + matrix[0][2] * vector[2],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1] + matrix[1][2] * vector[2],
        matrix[2][0] * vector[0] + matrix[2][1] * vector[1] + matrix[2][2] * vector[2],
    ]


def to_direct_positions(lattice: list[list[float]], cart_positions: list[list[float]]) -> list[list[float]]:
    inverse = invert_3x3(lattice)
    return [mat_vec_mul(inverse, position) for position in cart_positions]


def discover_outcars(source: Path, pattern: str) -> list[tuple[str, Path]]:
    if source.is_file():
        if source.name.endswith(".OUTCAR"):
            return [(source.stem, source)]
        if source.name == "OUTCAR":
            return [(source.parent.name, source)]
        raise ValueError(f"{source} is not an OUTCAR file")

    if not source.is_dir():
        raise ValueError(f"{source} does not exist")

    numbered_dirs = sorted(
        [path for path in source.iterdir() if path.is_dir() and path.name.isdigit()],
        key=lambda path: int(path.name),
    )
    if numbered_dirs:
        outcars: list[tuple[str, Path]] = []
        for directory in numbered_dirs:
            outcar = directory / "OUTCAR"
            if outcar.is_file():
                outcars.append((directory.name, outcar))
        if outcars:
            return outcars

    flat_outcars = [path for path in source.glob(pattern) if path.is_file()]
    if not flat_outcars:
        raise ValueError(f"No OUTCAR files found under {source}")

    def sort_key(path: Path) -> tuple[int, int | str]:
        stem = path.stem
        if stem.isdigit():
            return (0, int(stem))
        return (1, stem)

    return [(path.stem, path) for path in sorted(flat_outcars, key=sort_key)]


def write_distortion_pos(
    path: Path,
    comment: str,
    sample_id: str,
    species: list[str],
    counts: list[int],
    lattice: list[list[float]],
    positions: list[list[float]],
    coordinate_mode: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{comment} | sample {sample_id}", "1.0"]
    lines.extend(" ".join(f"{value: .16f}" for value in vector) for vector in lattice)
    lines.append(" ".join(species))
    lines.append(" ".join(str(count) for count in counts))
    lines.append(coordinate_mode)
    lines.extend(" ".join(f"{value: .16f}" for value in vector) for vector in positions)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_distortion_magmom(
    path: Path,
    vectors: list[tuple[float, float, float]],
    normalize_output: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for vector in vectors:
        output = normalize(vector) if normalize_output else vector
        rows.append(" ".join(f"{value: .10f}" for value in output))
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    source = Path(args.source).resolve()
    output_dir = Path(args.output_dir).resolve()
    outcars = discover_outcars(source, args.pattern)
    energy_rows: list[tuple[str, float]] = []

    if args.poscar_reference:
        poscar_reference = Path(args.poscar_reference).resolve()
        comment, species, counts, natoms = parse_poscar_reference(poscar_reference)
    else:
        _first_sample_id, first_outcar = outcars[0]
        comment, species, counts, natoms = parse_outcar_species_counts(first_outcar)

    for sample_id, outcar in outcars:
        lines = read_lines(outcar)
        lattice = parse_last_lattice(lines, outcar)
        cart_positions = parse_last_positions(lines, outcar, natoms)
        positions = (
            to_direct_positions(lattice, cart_positions)
            if args.coordinate_mode == "Direct"
            else cart_positions
        )

        sample_dir = output_dir / sample_id
        write_distortion_pos(
            sample_dir / "distortion.pos",
            comment,
            sample_id,
            species,
            counts,
            lattice,
            positions,
            args.coordinate_mode,
        )

        magmoms, _mode = parse_outcar_magmoms(outcar)
        if len(magmoms) != natoms:
            raise ValueError(
                f"{outcar} yielded {len(magmoms)} magnetic vectors but reference POSCAR expects {natoms}"
            )
        write_distortion_magmom(
            sample_dir / "distortion.MAGMOM",
            magmoms,
            args.normalize_magmoms,
        )

        if args.primitive_cells is not None:
            energy_rows.append((sample_id, parse_last_toten(lines, outcar)))

    if args.primitive_cells is not None:
        energy_path = output_dir / args.energy_out
        energy_path.parent.mkdir(parents=True, exist_ok=True)
        with energy_path.open("w", encoding="utf-8") as handle:
            handle.write(f"{args.primitive_cells}\n")
            for sample_id, energy in energy_rows:
                handle.write(f"{sample_id} {energy: .8f}\n")

    print(
        f"Prepared {len(outcars)} path-B sample packages under {output_dir}"
    )
    if args.primitive_cells is not None:
        print(f"Wrote shared Energy.dat to {output_dir / args.energy_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
