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
import math
import os
import re
from pathlib import Path

from extract_magmoms import normalize
from study_contract import digest, json_bytes, require, write_package


TOTEN_RE = re.compile(r"TOTEN\s*=\s*(\S+)")


def finite(token: str) -> float:
    value = float(token.replace('D', 'E').replace('d', 'e'))
    require(math.isfinite(value), 'nonfinite OUTCAR value')
    return value


def parse_args(argv=None) -> argparse.Namespace:
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
        default=None,
        help="Optional flat-file glob; IDs still come from <id>.OUTCAR or OUTCAR.<id>. By default both are found.",
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
    return parser.parse_args(argv)


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
    require(counts and all(c > 0 for c in counts), f'invalid POSCAR counts in {path}')
    return comment, species, counts, natoms


def parse_outcar_species_counts(path: Path, lines=None) -> tuple[str, list[str], list[int], int]:
    lines = read_lines(path) if lines is None else lines

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
    require(counts and all(c > 0 for c in counts), f'invalid species counts in {path}')
    comment = " ".join(species)
    return comment, species, counts, natoms


def parse_last_lattice(lines: list[str], outcar: Path) -> list[list[float]]:
    indices = [index for index, line in enumerate(lines) if "direct lattice vectors" in line]
    if not indices:
        raise ValueError(f"No lattice-vector block found in {outcar}")

    start = indices[-1] + 1
    lattice: list[list[float]] = []
    for line in lines[start : start + 3]:
        values = [finite(token) for token in line.split()[:3]]
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
        values = [finite(token) for token in line.split()[:3]]
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
            energy = finite(match.group(1))
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


def to_direct_positions(lattice: list[list[float]], cart_positions: list[list[float]]) -> list[list[float]]:
    inverse = invert_3x3(lattice)
    # OUTCAR lattice vectors are rows: Cartesian = fractional @ lattice.
    return [[sum(position[j] * inverse[j][i] for j in range(3)) for i in range(3)]
            for position in cart_positions]


def sample_id(path: Path) -> str:
    if path.name == 'OUTCAR':
        sid = path.parent.name
    elif path.name.startswith('OUTCAR.'):
        sid = path.name[len('OUTCAR.'):]
    elif path.name.endswith('.OUTCAR'):
        sid = path.name[:-len('.OUTCAR')]
    else:
        raise ValueError(f'unsupported OUTCAR filename: {path}')
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', sid), f'unsafe sample ID: {sid}')
    return str(int(sid)) if sid.isdigit() else sid


def discover_outcars(source: Path, pattern: str | None = None) -> list[tuple[str, Path]]:
    if source.is_file():
        return [(sample_id(source), source)]

    if not source.is_dir():
        raise ValueError(f"{source} does not exist")

    numbered_dirs = sorted(
        [path for path in source.iterdir() if path.is_dir() and path.name.isdigit()],
        key=lambda path: int(path.name),
    )
    paths = []
    for directory in numbered_dirs:
        outcar = directory / 'OUTCAR'
        require(outcar.is_file(), f'missing numbered sample OUTCAR: {outcar}')
        paths.append(outcar)
    patterns = [pattern] if pattern else ['*.OUTCAR', 'OUTCAR.*']
    paths.extend(sorted({p for glob in patterns for p in source.glob(glob) if p.is_file()}))
    if not paths:
        raise ValueError(f"No OUTCAR files found under {source}")
    outcars, ids, sources = [], set(), set()
    for path in paths:
        sid = sample_id(path)
        require(sid not in ids, f'duplicate/ambiguous sample ID: {sid}')
        require(path.resolve() not in sources, f'source reused under multiple IDs: {path}')
        ids.add(sid)
        sources.add(path.resolve())
        outcars.append((sid, path))
    return sorted(outcars, key=lambda item: (0, int(item[0])) if item[0].isdigit() else (1, item[0]))


def final_moments(lines, natoms):
    """Reject incomplete final axes rather than falling back to an earlier state."""
    axes, last_starts = {}, {}
    for axis in 'xyz':
        starts = [i for i, line in enumerate(lines) if line.strip() == f'magnetization ({axis})']
        if not starts:
            continue
        last_starts[axis] = starts[-1]
        rows, header, complete = [], False, False
        for raw in lines[starts[-1] + 1:]:
            text = raw.strip()
            if text.startswith('magnetization ('):
                break
            if text.startswith('# of ion'):
                header = True
            elif header and text.startswith('tot'):
                complete = True
                break
            elif header and re.match(r'^\d+\s', text):
                t = text.split()
                require(int(t[0]) == len(rows) + 1, 'magnetization ion ordering mismatch')
                rows.append(finite(t[-1]))
        require(complete and len(rows) == natoms, f'incomplete final magnetization ({axis})')
        axes[axis] = rows
    require(set(axes) in ({'x'}, {'x', 'y', 'z'}), 'missing/partial magnetization axes')
    if len(axes) == 1:
        return [(v, 0.0, 0.0) for v in axes['x']], 'collinear-x'
    require(last_starts['x'] < last_starts['y'] < last_starts['z'],
            'final magnetization axes belong to different snapshots')
    return list(zip(axes['x'], axes['y'], axes['z'])), 'noncollinear'


def distortion_pos(
    comment: str,
    sample_id: str,
    species: list[str],
    counts: list[int],
    lattice: list[list[float]],
    positions: list[list[float]],
    coordinate_mode: str,
) -> bytes:
    lines = [f"{comment} | sample {sample_id}", "1.0"]
    lines.extend(" ".join(f"{value: .16f}" for value in vector) for vector in lattice)
    lines.append(" ".join(species))
    lines.append(" ".join(str(count) for count in counts))
    lines.append(coordinate_mode)
    lines.extend(" ".join(f"{value: .16f}" for value in vector) for vector in positions)
    return ("\n".join(lines) + "\n").encode()


def distortion_magmom(
    vectors: list[tuple[float, float, float]],
    normalize_output: bool,
) -> bytes:
    rows = []
    for vector in vectors:
        output = normalize(vector) if normalize_output else vector
        rows.append(" ".join(f"{value: .10f}" for value in output))
    return ("\n".join(rows) + "\n").encode()


def main(argv=None) -> int:
    args = parse_args(argv)
    source = Path(args.source).resolve()
    output_dir = Path(args.output_dir).resolve()
    outcars = discover_outcars(source, args.pattern)
    require(not output_dir.exists(), 'use a new output directory; preserve earlier attempts')
    require(args.primitive_cells is None or args.primitive_cells > 0, 'primitive cell count must be positive')
    energy_rows: list[tuple[str, float]] = []
    files, samples = {}, []

    if args.poscar_reference:
        poscar_reference = Path(args.poscar_reference).resolve()
        comment, species, counts, natoms = parse_poscar_reference(poscar_reference)
    else:
        comment = species = counts = natoms = None

    for sample_id, outcar in outcars:
        raw = outcar.read_bytes()
        lines = raw.decode('utf-8').splitlines()
        out_comment, out_species, out_counts, out_natoms = parse_outcar_species_counts(outcar, lines)
        if species is None:
            comment, species, counts, natoms = out_comment, out_species, out_counts, out_natoms
        require((species, counts) == (out_species, out_counts), f'species/order/count changed: {outcar}')
        lattice = parse_last_lattice(lines, outcar)
        invert_3x3(lattice)
        cart_positions = parse_last_positions(lines, outcar, natoms)
        positions = (
            to_direct_positions(lattice, cart_positions)
            if args.coordinate_mode == "Direct"
            else cart_positions
        )

        pos = distortion_pos(
            comment,
            sample_id,
            species,
            counts,
            lattice,
            positions,
            args.coordinate_mode,
        )

        magmoms, mode = final_moments(lines, natoms)
        mag = distortion_magmom(magmoms, args.normalize_magmoms)
        energy = parse_last_toten(lines, outcar)
        prefix = sample_id + '/'
        files[prefix + 'distortion.pos'] = pos
        files[prefix + 'distortion.MAGMOM'] = mag
        original_id = int(sample_id) if sample_id.isdigit() else sample_id
        ledger = {'original_id': original_id,
                  'outcar': os.path.relpath(outcar.resolve(), output_dir / sample_id),
                  'outcar_sha256': digest(raw), 'structure': 'distortion.pos',
                  'magnetic_state': 'distortion.MAGMOM'}
        files[prefix + 'source_identity.json'] = json_bytes(ledger)
        samples.append({'id': original_id, 'source_identity': prefix + 'source_identity.json',
                        'energy_ev': energy, 'atom_count': natoms, 'magnetic_format': mode})

        if args.primitive_cells is not None:
            require(sample_id.isdigit(), 'legacy Energy.dat needs integer IDs')
            energy_rows.append((sample_id, energy))

    if args.primitive_cells is not None:
        require(args.energy_out not in files and args.energy_out != 'manifest.json', 'energy output collides with package')
        files[args.energy_out] = (f'{args.primitive_cells}\n' + ''.join(
            f'{sid} {energy:.16g}\n' for sid, energy in energy_rows)).encode()

    write_package(output_dir, files, 'manifest.json', {
        'scope': 'OUTCAR ID inventory and final-block extraction; not DFT convergence or scientific acceptance',
        'samples': samples, 'sample_count': len(samples), 'species': species, 'counts': counts,
        'coordinate_mode': args.coordinate_mode, 'normalized_moments': args.normalize_magmoms,
        'primitive_cells': args.primitive_cells,
        'unresolved': ['DFT convergence', 'energy-table reconciliation', 'primitive mapping',
                       'basis suitability', 'direction uncertainty near zero moments']})

    print(
        f"Prepared {len(outcars)} path-B sample packages under {output_dir}"
    )
    if args.primitive_cells is not None:
        print(f"Wrote shared Energy.dat to {output_dir / args.energy_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
