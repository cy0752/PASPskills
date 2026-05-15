#!/usr/bin/env python3
"""Extract final per-atom magnetic moments from VASP OUTCAR.

This helper is intended for the L3 effective-Hamiltonian workflow:
- compare the converged VASP magnetic directions against the input MAGMOM
- export a path-B-ready distortion.MAGMOM file
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path


VECTOR_EPS = 1e-12


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract final per-atom magnetic moments from VASP OUTCAR, optionally "
            "compare against an input MAGMOM file, and optionally write "
            "distortion.MAGMOM."
        )
    )
    parser.add_argument("outcar", help="Path to OUTCAR")
    parser.add_argument(
        "--reference",
        help=(
            "Reference magnetic input file. Supports VASP MAGMOM files containing "
            "'MAGMOM=' or PASP-style distortion.MAGMOM files with one 'x y z' "
            "vector per atom."
        ),
    )
    parser.add_argument(
        "--distortion-out",
        help="Write the extracted final magnetic moments to this distortion.MAGMOM path.",
    )
    parser.add_argument(
        "--min-norm",
        type=float,
        default=0.1,
        help=(
            "Vectors with norm below this threshold are treated as nonmagnetic for "
            "comparison. Default: 0.1"
        ),
    )
    parser.add_argument(
        "--cos-threshold",
        type=float,
        default=0.95,
        help=(
            "Per-atom directions are considered consistent when cos(theta) is at "
            "least this threshold. Default: 0.95"
        ),
    )
    parser.add_argument(
        "--normalize-output",
        action="store_true",
        help=(
            "Normalize nonzero output vectors before writing distortion.MAGMOM. "
            "Useful when only direction matters."
        ),
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help=(
            "Print a per-atom table for all atoms. By default only mismatches are "
            "printed when --reference is provided."
        ),
    )
    return parser.parse_args()


def read_text(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}") from None


def parse_magnetization_block(lines: list[str], axis: str) -> list[float]:
    current_block: list[float] = []
    last_complete_block: list[float] = []
    reading = False
    header_seen = False
    target = f"magnetization ({axis})"

    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped == target:
            current_block = []
            reading = True
            header_seen = False
            continue

        if not reading:
            continue

        if not stripped or set(stripped) == {"-"}:
            continue

        if stripped.startswith("# of ion"):
            header_seen = True
            continue

        if not header_seen:
            continue

        if stripped.startswith("tot"):
            last_complete_block = current_block[:]
            reading = False
            continue

        if re.match(r"^\d+\s+", stripped):
            tokens = stripped.split()
            if len(tokens) < 2:
                continue
            try:
                current_block.append(float(tokens[-1]))
            except ValueError:
                continue

    return last_complete_block


def parse_outcar_magmoms(path: Path) -> tuple[list[tuple[float, float, float]], str]:
    lines = read_text(path)
    mag_x = parse_magnetization_block(lines, "x")
    mag_y = parse_magnetization_block(lines, "y")
    mag_z = parse_magnetization_block(lines, "z")

    if mag_x and mag_y and mag_z:
        if not (len(mag_x) == len(mag_y) == len(mag_z)):
            raise SystemExit(
                "Failed to parse OUTCAR magnetization blocks: x/y/z atom counts differ."
            )
        vectors = list(zip(mag_x, mag_y, mag_z))
        return vectors, "noncollinear"

    if mag_x:
        # Collinear OUTCAR commonly exposes only one component block.
        vectors = [(value, 0.0, 0.0) for value in mag_x]
        return vectors, "collinear"

    raise SystemExit(
        "No final 'magnetization (x/y/z)' blocks were found in OUTCAR. "
        "Check that VASP wrote site magnetizations (e.g. LORBIT)."
    )


def expand_vasp_magmom_tokens(text: str) -> list[float]:
    floats: list[float] = []
    for token in text.replace(",", " ").split():
        if "*" in token:
            count_text, value_text = token.split("*", 1)
            try:
                count = int(count_text)
                value = float(value_text)
            except ValueError as exc:
                raise SystemExit(f"Invalid MAGMOM token: {token}") from exc
            floats.extend([value] * count)
        else:
            try:
                floats.append(float(token))
            except ValueError as exc:
                raise SystemExit(f"Invalid MAGMOM token: {token}") from exc
    return floats


def parse_reference_file(path: Path) -> list[tuple[float, float, float]]:
    lines = read_text(path)
    magmom_text = None

    for line in lines:
        if "MAGMOM" in line and "=" in line:
            magmom_text = line.split("=", 1)[1]
            break

    if magmom_text is not None:
        values = expand_vasp_magmom_tokens(magmom_text)
        if len(values) % 3 != 0:
            raise SystemExit(
                f"Reference MAGMOM from {path} does not contain a multiple of 3 numbers."
            )
        return [
            (values[index], values[index + 1], values[index + 2])
            for index in range(0, len(values), 3)
        ]

    vectors: list[tuple[float, float, float]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        tokens = stripped.split()
        if len(tokens) != 3:
            raise SystemExit(
                f"Expected 3 columns per line in distortion.MAGMOM-style file: {path}"
            )
        try:
            vectors.append((float(tokens[0]), float(tokens[1]), float(tokens[2])))
        except ValueError as exc:
            raise SystemExit(f"Failed to parse vector line in {path}: {line}") from exc

    if not vectors:
        raise SystemExit(f"No magnetic vectors were parsed from reference file: {path}")

    return vectors


def vector_norm(vector: tuple[float, float, float]) -> float:
    return math.sqrt(sum(component * component for component in vector))


def normalize(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    norm = vector_norm(vector)
    if norm < VECTOR_EPS:
        return (0.0, 0.0, 0.0)
    return tuple(component / norm for component in vector)


def dot(vec_a: tuple[float, float, float], vec_b: tuple[float, float, float]) -> float:
    return sum(component_a * component_b for component_a, component_b in zip(vec_a, vec_b))


def angle_deg(vec_a: tuple[float, float, float], vec_b: tuple[float, float, float]) -> float:
    unit_a = normalize(vec_a)
    unit_b = normalize(vec_b)
    cosine = max(-1.0, min(1.0, dot(unit_a, unit_b)))
    return math.degrees(math.acos(cosine))


def format_vector(vector: tuple[float, float, float]) -> str:
    return f"{vector[0]: .6f} {vector[1]: .6f} {vector[2]: .6f}"


def compare_vectors(
    reference: list[tuple[float, float, float]],
    actual: list[tuple[float, float, float]],
    min_norm: float,
    cos_threshold: float,
) -> tuple[list[str], bool]:
    if len(reference) != len(actual):
        raise SystemExit(
            f"Atom count mismatch: reference has {len(reference)} atoms, "
            f"OUTCAR has {len(actual)} atoms."
        )

    rows: list[str] = []
    all_consistent = True
    for index, (ref_vec, out_vec) in enumerate(zip(reference, actual), start=1):
        ref_norm = vector_norm(ref_vec)
        out_norm = vector_norm(out_vec)
        ref_mag = ref_norm >= min_norm
        out_mag = out_norm >= min_norm

        if not ref_mag and not out_mag:
            status = "ok-both-small"
            cosine_text = "nan"
            angle_text = "nan"
            consistent = True
        elif ref_mag and out_mag:
            cosine = dot(normalize(ref_vec), normalize(out_vec))
            angle = angle_deg(ref_vec, out_vec)
            consistent = cosine >= cos_threshold
            status = "ok" if consistent else "mismatch-direction"
            cosine_text = f"{cosine: .6f}"
            angle_text = f"{angle: .3f}"
        elif ref_mag and not out_mag:
            status = "mismatch-lost-moment"
            cosine_text = "nan"
            angle_text = "nan"
            consistent = False
        else:
            status = "mismatch-unexpected-moment"
            cosine_text = "nan"
            angle_text = "nan"
            consistent = False

        if not consistent:
            all_consistent = False

        rows.append(
            f"{index:4d}  {status:25s}  {ref_norm:9.4f}  {out_norm:9.4f}  "
            f"{cosine_text:>9s}  {angle_text:>8s}"
        )

    return rows, all_consistent


def write_distortion_magmom(
    path: Path,
    vectors: list[tuple[float, float, float]],
    normalize_output: bool,
) -> None:
    output_lines = []
    for vector in vectors:
        final_vector = normalize(vector) if normalize_output else vector
        output_lines.append(
            f"{final_vector[0]: .10f} {final_vector[1]: .10f} {final_vector[2]: .10f}"
        )
    path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    outcar_path = Path(args.outcar)
    actual_vectors, mode = parse_outcar_magmoms(outcar_path)

    print(f"Parsed {len(actual_vectors)} atoms from {outcar_path}")
    print(f"Detected OUTCAR mode: {mode}")
    if mode == "collinear":
        print(
            "Warning: only one magnetization component block was found in OUTCAR. "
            "The extracted vectors are stored as (m, 0, 0)."
        )

    if args.distortion_out:
        distortion_path = Path(args.distortion_out)
        write_distortion_magmom(
            distortion_path,
            actual_vectors,
            normalize_output=args.normalize_output,
        )
        print(f"Wrote distortion.MAGMOM-style output to {distortion_path}")

    if args.reference:
        reference_path = Path(args.reference)
        reference_vectors = parse_reference_file(reference_path)
        rows, all_consistent = compare_vectors(
            reference_vectors,
            actual_vectors,
            min_norm=args.min_norm,
            cos_threshold=args.cos_threshold,
        )
        print("")
        print(
            "atom  status                     |ref|      |out|        cos     angle"
        )
        print(
            "----  -------------------------  ---------  ---------  ---------  --------"
        )
        if args.show_all:
            for row in rows:
                print(row)
        else:
            mismatches = [
                row for row in rows if "mismatch" in row or "ok-both-small" in row
            ]
            if mismatches:
                for row in mismatches:
                    print(row)
            else:
                print("(all atoms passed the direction consistency check)")

        print("")
        if all_consistent:
            print(
                "Overall result: consistent. Final per-atom magnetic directions remain "
                "compatible with the input threshold."
            )
            return 0

        print(
            "Overall result: inconsistent. At least one atom no longer matches the "
            "input magnetic direction threshold."
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
