#!/usr/bin/env python3
"""Fit fixed-geometry VASP electronic dipoles and export PASP GKNB blocks."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

try:
    import numpy as np
except ModuleNotFoundError:
    raise SystemExit("fit_l8_polarization.py requires NumPy. Install with: python -m pip install numpy")


PAIR_AXES = tuple(a + b for a in "xyz" for b in "xyz")
PAIR_SIGNS = ("++", "+-", "-+", "--")
STATE_NAMES = dict(zip(PAIR_SIGNS, ("upup", "updn", "dnup", "dndn")))
SITE_ROWS = ("xx", "yy", "zz", "xy", "xz", "yz")
DIRECTIONS = {
    "x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1),
    "xpy": (1, 1, 0), "xmy": (1, -1, 0), "xpz": (1, 0, 1),
    "xmz": (1, 0, -1), "ypz": (0, 1, 1), "ymz": (0, 1, -1),
}
GEOMETRY_TOL = 2e-5  # OUTCAR position blocks are rounded to five decimals.
CONVERGED = "aborting loop because EDIFF is reached"


def template(kind):
    manifest = {}
    if kind in ("pij", "both"):
        manifest["pij"] = {
            "sites": [1, 2],
            "image_j": [0, 0, 0],
            "states": {
                axes: {sign: f"pij/{axes}/{name}" for sign, name in STATE_NAMES.items()}
                for axes in PAIR_AXES
            },
        }
    if kind in ("pi", "both"):
        manifest["pi"] = {
            "site": 1,
            "states": {
                direction: {sign: f"pi/{direction}/{sign}" for sign in ("plus", "minus")}
                for direction in DIRECTIONS
            },
        }
    return manifest


def vector(tokens):
    result = np.array([float(token.lower().replace("d", "e")) for token in tokens])
    if result.shape != (3,) or not np.isfinite(result).all():
        raise ValueError("expected three finite Cartesian components")
    return result


def read_poscar(path):
    lines = path.read_text().splitlines()
    lattice = np.array([vector(line.split()[:3]) for line in lines[2:5]])
    volume = abs(np.linalg.det(lattice))
    if not math.isfinite(volume) or volume == 0:
        raise ValueError(f"{path}: singular lattice")
    scale = [float(token) for token in lines[1].split()]
    if len(scale) == 1 and scale[0] < 0:
        scale = [(-scale[0] / volume) ** (1 / 3)]
    if len(scale) not in (1, 3) or not all(math.isfinite(s) and s > 0 for s in scale):
        raise ValueError(f"{path}: invalid POSCAR scale")
    lattice *= scale

    species = lines[5].split()
    counts = [int(token) for token in lines[6].split()]
    if (not species or not all(symbol.isalpha() for symbol in species)
            or len(counts) != len(species) or not all(count > 0 for count in counts)):
        raise ValueError(f"{path}: expected VASP 5 element symbols and matching atom counts")
    natoms = sum(counts)
    start = 7 + lines[7].lower().lstrip().startswith("s")
    mode = lines[start].lower().lstrip()
    positions = np.array([vector(line.split()[:3]) for line in lines[start + 1:start + 1 + natoms]])
    if positions.shape != (natoms, 3) or not mode.startswith(("d", "c", "k")):
        raise ValueError(f"{path}: expected Direct or Cartesian positions for {natoms} atoms")
    cartesian = positions @ lattice if mode.startswith("d") else positions * scale
    return lattice, list(zip(species, counts)), cartesian


def read_state(directory, reference):
    lattice, species, positions = read_poscar(directory / "POSCAR")
    if reference is not None:
        ref_lattice, ref_species, ref_positions = reference
        if (species != ref_species or not np.allclose(lattice, ref_lattice, atol=1e-8, rtol=0)
                or not np.allclose(positions, ref_positions, atol=1e-8, rtol=0)):
            raise ValueError(f"{directory}: POSCAR differs from the fixed reference geometry or atom order")

    path = directory / "OUTCAR"
    text = path.read_text(encoding="utf-8", errors="replace")
    steps = re.findall(r"^\s*NSW\s*=\s*(\d+)", text, re.MULTILINE)
    if not steps or int(steps[-1]) != 0:
        raise ValueError(f"{path}: expected a static run (NSW = 0)")
    iterations = list(re.finditer(r"^\s*-+\s+Iteration\s+\d+\s*\(", text, re.MULTILINE))
    last_iteration = iterations[-1].start() if iterations else -1
    convergence = text.rfind(CONVERGED)
    electronic = list(re.finditer(r"p\[elc\]\s*=\s*\(([^\n)]+)\)", text))
    ionic = list(re.finditer(r"p\[ion\]\s*=\s*\(([^\n)]+)\)", text))
    if (convergence <= last_iteration or not electronic or not ionic
            or min(electronic[-1].start(), ionic[-1].start()) < convergence):
        raise ValueError(f"{path}: missing final EDIFF convergence or dipole from the converged state")

    lines = text.splitlines()
    lattice_headers = [i for i, line in enumerate(lines) if "direct lattice vectors" in line]
    position_headers = [i for i, line in enumerate(lines) if "POSITION" in line and "TOTAL-FORCE" in line]
    if not lattice_headers or not position_headers:
        raise ValueError(f"{path}: missing lattice or final POSITION/TOTAL-FORCE block")
    lattice_start = lattice_headers[-1] + 1
    position_start = position_headers[-1] + 2
    run_lattice = np.array([vector(line.split()[:3]) for line in lines[lattice_start:lattice_start + 3]])
    run_positions = np.array([
        vector(line.split()[:3]) for line in lines[position_start:position_start + len(positions)]
    ])
    if (run_lattice.shape != lattice.shape or run_positions.shape != positions.shape
            or not np.allclose(run_lattice, lattice, atol=GEOMETRY_TOL, rtol=0)
            or not np.allclose(run_positions, positions, atol=GEOMETRY_TOL, rtol=0)):
        raise ValueError(f"{path}: lattice or positions disagree with POSCAR")

    return (lattice, species, positions), {
        "directory": str(directory),
        "electronic_raw_eA": vector(electronic[-1][1].split()).tolist(),
        "ionic_eA": vector(ionic[-1][1].split()).tolist(),
        "ediff_reached": True,
        "timing_footer_present": "General timing and accounting" in text[convergence:],
    }


def integer_vector(value, label):
    if not isinstance(value, list) or len(value) != 3 or any(type(x) is not int for x in value):
        raise ValueError(f"{label} must be a list of three integers")
    return np.array(value, dtype=int)


def read_group(root, entries, labels, reference=None):
    if set(entries) != set(labels):
        raise ValueError(f"expected states {', '.join(labels)}, got {', '.join(entries)}")
    records = {}
    for label in labels:
        entry = entries[label]
        if isinstance(entry, str):
            entry = {"directory": entry}
        directory = (root / entry["directory"]).resolve(strict=True)
        if any(record["directory"] == str(directory) for record in records.values()):
            raise ValueError(f"{label}: reused state directory {directory}")
        reference, record = read_state(directory, reference)
        if "berry_shift" in entry:
            record["berry_shift"] = integer_vector(entry["berry_shift"], label).tolist()
        records[label] = record
    return reference, records


def align(records, lattice, label):
    first = next(iter(records.values()))
    manual_count = sum("berry_shift" in state for state in records.values())
    if manual_count not in (0, len(records)):
        raise ValueError(f"{label}: provide explicit Berry shifts for every state in this group")
    inverse = np.linalg.inv(lattice)
    anchor = np.array(first["electronic_raw_eA"])
    # Every nonzero lattice vector has length at least the shortest cell height.
    # Accept an automatic branch only inside half this conservative bound.
    branch_radius = 0.5 / np.linalg.norm(inverse, axis=0).max()
    for key, state in records.items():
        if not np.allclose(state["ionic_eA"], first["ionic_eA"], atol=GEOMETRY_TOL, rtol=0):
            raise ValueError(f"{label}/{key}: ionic dipole changed in a fixed-geometry group")
        raw = np.array(state["electronic_raw_eA"])
        if manual_count:
            shift = np.array(state["berry_shift"], dtype=int)
        else:
            shift = np.rint((raw - anchor) @ inverse).astype(int)
        corrected = raw - shift @ lattice
        if not manual_count and np.linalg.norm(corrected - anchor) >= branch_radius - GEOMETRY_TOL:
            raise ValueError(f"{label}/{key}: ambiguous automatic Berry branch; supply explicit berry_shift values")
        state["berry_shift"] = shift.tolist()
        state["electronic_corrected_eA"] = corrected.tolist()
    return "explicit" if manual_count else "small_change_from_first_state"


def site_position(positions, index):
    if type(index) is not int or not 1 <= index <= len(positions):
        raise ValueError(f"invalid 1-based site number: {index!r}")
    return positions[index - 1]


def extract_pair(root, entry):
    groups = entry["states"]
    if set(groups) != set(PAIR_AXES):
        raise ValueError(f"pij requires nine axis pairs: {', '.join(PAIR_AXES)}")
    reference = None
    rows, evidence = {}, {}
    used_dirs = set()
    for axes in PAIR_AXES:
        reference, states = read_group(root, groups[axes], PAIR_SIGNS, reference)
        directories = {state["directory"] for state in states.values()}
        if directories & used_dirs:
            raise ValueError(f"pij/{axes}: DFT state directory reused across axis pairs")
        used_dirs.update(directories)
        mode = align(states, reference[0], f"pij/{axes}")
        dipoles = [np.array(states[sign]["electronic_corrected_eA"]) for sign in PAIR_SIGNS]
        pp, pm, mp, mm = dipoles
        rows[axes] = ((pp - pm - mp + mm) / 4).tolist()
        evidence[axes] = {"branch_alignment": mode, "states": states}

    lattice, _, positions = reference
    i, j = entry["sites"]
    image = integer_vector(entry.get("image_j", [0, 0, 0]), "pij.image_j")
    if i == j:
        raise ValueError("pij.sites must be two distinct DFT atoms that can be flipped independently")
    points = [site_position(positions, i), site_position(positions, j) + image @ lattice]
    return points, rows, {
        "sites": [i, j], "image_j": image.tolist(), "lattice_A": lattice.tolist(), "groups": evidence,
    }


def fit_site(root, entry):
    groups = entry["states"]
    if not groups or not set(groups) <= DIRECTIONS.keys():
        raise ValueError(f"pi direction labels must come from {', '.join(DIRECTIONS)}")
    labels = tuple(f"{direction}/{sign}" for direction in groups for sign in ("plus", "minus"))
    entries = {}
    for direction, group in groups.items():
        if set(group) != {"plus", "minus"}:
            raise ValueError(f"pi/{direction}: expected one plus and one minus state")
        entries.update({f"{direction}/{sign}": item for sign, item in group.items()})
    reference, states = read_group(root, entries, labels)
    mode = align(states, reference[0], "pi")

    design, means = [], []
    for direction in groups:
        n = np.array(DIRECTIONS[direction])
        x, y, z = n / np.linalg.norm(n)
        design.append([1, x*x - z*z, y*y - z*z, 2*x*y, 2*x*z, 2*y*z])
        means.append(np.mean([
            states[f"{direction}/{sign}"]["electronic_corrected_eA"] for sign in ("plus", "minus")
        ], axis=0))
    design = np.asarray(design)
    parameters, _, rank, singular_values = np.linalg.lstsq(design, means, rcond=None)
    if rank != 6:
        raise ValueError(f"pi fit design rank is {rank}, expected 6; add independent direction pairs")
    background, xx, yy, xy, xz, yz = parameters
    rows = {key: row.tolist() for key, row in zip(SITE_ROWS, (xx, yy, -(xx + yy), xy, xz, yz))}
    residual = np.asarray(means) - design @ parameters
    return [site_position(reference[2], entry["site"])], rows, {
        "site": entry["site"], "lattice_A": reference[0].tolist(), "branch_alignment": mode, "states": states,
        "rank": int(rank), "singular_values": singular_values.tolist(),
        "background_eA": background.tolist(),
        "component_rmse_eA": float(np.sqrt(np.mean(residual**2))),
        "residuals_eA": {key: row.tolist() for key, row in zip(groups, residual)},
    }


def render_block(name, positions, rows):
    lines = [f"%block {name}", "1"]
    lines.extend(" ".join(f"{x:.12f}" for x in point) for point in positions)
    lines.extend(("1 0 0", "0 1 0", "0 0 1"))
    lines.extend(" ".join(f"{x:.12e}" for x in row) + f"  # {key}" for key, row in rows.items())
    return "\n".join([*lines, f"%endblock {name}"])


def fit_manifest(manifest_path, output):
    if output.exists():
        raise FileExistsError(f"output directory already exists: {output}")
    manifest = json.loads(manifest_path.read_text())
    if not manifest or not isinstance(manifest, dict) or not manifest.keys() <= {"pij", "pi"}:
        raise ValueError("manifest must contain pij, pi, or both")
    report = {"manifest": str(manifest_path), "dipole_unit": "e Angstrom", "spin_length": 1,
              "frame": "global Cartesian", "status": "candidate"}
    blocks = []
    for key, extract, name in (("pij", extract_pair, "GKNB_inter_site"), ("pi", fit_site, "GKNB_single_site")):
        if key not in manifest:
            continue
        positions, rows, evidence = extract(manifest_path.parent, manifest[key])
        evidence["positions_A"] = [point.tolist() for point in positions]
        evidence["coefficients_eA"] = rows
        report[key] = evidence
        blocks.append(render_block(name, positions, rows))
    pair_groups = report.get("pij", {}).get("groups", {}).values()
    records = [state for group in pair_groups for state in group["states"].values()]
    records.extend(report.get("pi", {}).get("states", {}).values())
    report["missing_timing_footers"] = [state["directory"] for state in records if not state["timing_footer_present"]]

    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".l8-fit-", dir=output.parent) as temporary:
        staged = Path(temporary) / "fit"
        staged.mkdir()
        (staged / "GKNB.fdf").write_text(
            "# Candidate GKNB blocks from fixed-geometry DFT\n\n" + "\n\n".join(blocks) + "\n"
        )
        (staged / "fit_report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        output.mkdir()
        try:
            staged.replace(output)
        except OSError:
            output.rmdir()
            raise
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    make = subcommands.add_parser("template", help="print an editable JSON manifest")
    make.add_argument("kind", choices=("pij", "pi", "both"))
    fit = subcommands.add_parser("fit", help="read a manifest and write candidate blocks and a fit report")
    fit.add_argument("manifest", type=Path)
    fit.add_argument("output", type=Path, help="a new output directory")
    args = parser.parse_args(argv)
    if args.command == "template":
        print(json.dumps(template(args.kind), indent=2))
        return 0

    try:
        report = fit_manifest(args.manifest.resolve(), args.output)
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError, OverflowError, np.linalg.LinAlgError) as exc:
        print(f"L8 fit: {exc}", file=sys.stderr)
        return 1
    if report["missing_timing_footers"]:
        count = len(report["missing_timing_footers"])
        print(f"Warning: {count} OUTCARs lack a normal timing footer. Review fit_report.json before PASP handoff.",
              file=sys.stderr)
    print(f"Wrote {args.output / 'GKNB.fdf'} and {args.output / 'fit_report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
