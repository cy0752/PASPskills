#!/usr/bin/env python3
"""Read-only four-state native-J and dual-primitive delivery preflight.

Usage: python check_four_state_native.py DELIVERY --workspace ROOT --source INPUTS
Requires spglib for the symmetry check. No PASP executable or source tree is used.
This verifies receipts and geometry, not physical pair equivalence or a ground state.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from l2_validate_inputs import CheckFailure, FDF, block_rows, data_tokens, finite, integer, norm, raw_rows, volume


STATES = ("upup", "updn", "dnup", "dndn")
SOURCE_STATES = ("up_up", "up_dn", "dn_up", "dn_dn")
TOLERANCES = (1e-5, 1e-4, 1e-3)
ELEMENTS = ("X H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn "
            "Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce "
            "Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn "
            "Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og").split()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def path(root, name, kind="file"):
    require(isinstance(name, str) and name and not Path(name).is_absolute(), f"invalid relative path: {name}")
    target = (root / name).resolve()
    require(target.is_relative_to(root.resolve()), f"path escapes root: {name}")
    require(target.is_file() and target.stat().st_size > 0 if kind == "file" else target.is_dir(), f"missing {kind}: {name}")
    return target


def close(a, b, atol=2e-10):
    return math.isclose(a, b, rel_tol=1e-7, abs_tol=atol)


def exchange(file):
    rows = [data_tokens(line) for line in file.read_text().splitlines()]
    rows = [row for row in rows if row]
    require(rows and len(rows[0]) == 1, f"invalid exchange count: {file}")
    n = integer(rows[0][0])
    require(n > 0 and len(rows) >= n + 5, f"incomplete exchange: {file}")
    lattice = np.array([[finite(v) for v in row] for row in rows[1:4]], float)
    require(lattice.shape == (3, 3), f"invalid exchange lattice: {file}")
    entries = rows[4:4+n]
    require(all(len(row) in (10, 18) for row in entries), f"invalid exchange row width: {file}")
    require(all(integer(row[0]) == i for i, row in enumerate(entries, 1)), f"exchange ids out of order: {file}")
    require(all(math.isfinite(finite(token)) for row in entries for token in row), f"invalid exchange values: {file}")
    require(rows[4+n][0] == "0", f"nonzero or missing dJ/du section: {file}")
    return lattice, entries


def effective(input_file):
    return FDF(input_file)


def first_origin(fdf, key, expected):
    record = fdf.required(key)
    require(record.origin.split(":", 1)[0] == str(expected), f"{key} not first read from {expected}")


def structure(fdf, unit=False):
    if unit:
        lattice = np.array([[finite(v) for v in row] for row in block_rows(fdf, "unit_cell_in_Ang")], float)
        n = integer(data_tokens(fdf.required("unit_cell.na", False).body[0])[0])
        coords = block_rows(fdf, "Atoms_in_unit_cell_Ang")
        fmt = "cart"
    else:
        lattice = np.array([[finite(v) for v in row] for row in block_rows(fdf, "LatticeVectors")], float)
        n = integer(data_tokens(fdf.required("NumberOfAtoms", False).body[0])[0])
        coords = block_rows(fdf, "AtomicCoordinatesAndAtomicSpecies")
        format_record = fdf.first("AtomicCoordinatesFormat", False)
        fmt = norm(data_tokens(format_record.body[0])[0]) if format_record else "notscaledcartesianang"
        constant = fdf.first("LatticeConstant", False)
        if constant:
            tokens = data_tokens(constant.body[0])
            require(len(tokens) >= 2 and close(finite(tokens[0]), 1) and norm(tokens[1]) == "ang", "cell LatticeConstant must be 1 Ang")
    require(lattice.shape == (3, 3) and volume(lattice.tolist()) > 0, "invalid structure lattice")
    require(len(coords) == n and all(len(row) >= 4 for row in coords), "structure atom count/row mismatch")
    xyz = np.array([[finite(v) for v in row[:3]] for row in coords], float)
    species = [integer(row[3]) for row in coords]
    if fmt == "fractional":
        frac = xyz
    else:
        require(fmt in ("cart", "notscaledcartesianang"), f"unsupported coordinate format: {fmt}")
        frac = xyz @ np.linalg.inv(lattice)
    return lattice, frac % 1, species


def map_endpoint(point, species_id, lattice, frac, species, tolerance=1e-6):
    """Map a Cartesian exchange endpoint to one species site and integer image.

    The image is solved from the full fractional displacement, rather than by
    independently wrapping both endpoints to a minimum image.  This keeps a
    long source bond's relative lattice translation observable and rejects
    ambiguous same-species matches.
    """
    inverse = np.linalg.inv(lattice)
    require(np.all(tolerance * np.linalg.norm(inverse, axis=0) < 0.5),
            "lattice too ill-conditioned for unique endpoint images at this tolerance")
    point_frac = np.asarray(point, dtype=float) @ inverse
    matches = []
    for index, (site_frac, site_species) in enumerate(zip(frac, species), 1):
        if site_species != species_id:
            continue
        image = np.rint(point_frac - site_frac).astype(int)
        residual = float(np.linalg.norm((point_frac - site_frac - image) @ lattice))
        if residual <= tolerance:
            matches.append({"site": index, "image": image.tolist(), "residual": residual})
    require(len(matches) == 1,
            f"exchange endpoint needs one unique primitive {species_id} site/image; "
            f"found {len(matches)}")
    return matches[0]


def report_endpoint_geometry(entry):
    """Read the supported explicit endpoint/site-image fields from a report."""
    sites = entry.get("final_sites_1based", entry.get("endpoint_sites_1based"))
    require(isinstance(sites, list) and len(sites) == 2 and all(type(x) is int for x in sites),
            "exchange_map must declare final endpoint sites")
    images = entry.get("image_cells")
    if images is None:
        require("endpoint_b_image" in entry, "exchange_map must declare endpoint images")
        images = [entry.get("endpoint_a_image", [0, 0, 0]), entry["endpoint_b_image"]]
    require(isinstance(images, list) and len(images) == 2 and
            all(isinstance(image, list) and len(image) == 3 and
                all(type(x) is int for x in image) for image in images),
            "exchange_map must declare integer endpoint images")
    return sites, images


def native_structure_compatibility(fdf):
    """Check that a native analysis cell is an integer supercell of unit_cell.

    Native extraction may use a larger analysis cell, so atom counts need not
    match.  The lattice relation and every species/site image must still be
    reproducible from the declared unit cell.  This catches a common late
    replay failure where two independently generated, non-commensurate cells
    are paired in one native input.
    """
    cell_lattice, cell_frac, cell_species = structure(fdf)
    unit_lattice, unit_frac, unit_species = structure(fdf, unit=True)
    relation = cell_lattice @ np.linalg.inv(unit_lattice)
    require(np.isfinite(relation).all(), "native cell/unit_cell relation is non-finite")
    integer_relation = np.rint(relation)
    require(np.allclose(relation, integer_relation, atol=1e-5, rtol=0),
            "native cell/unit_cell incompatible: lattice ratio is not integer")
    determinant = float(np.linalg.det(integer_relation))
    require(determinant > 0 and close(determinant, round(determinant), 1e-5),
            "native cell/unit_cell incompatible: invalid supercell determinant")
    require(len(cell_species) == len(unit_species) * round(determinant),
            "native cell/unit_cell incompatible: atom count does not match supercell")
    for species in sorted(set(unit_species) | set(cell_species)):
        cell_count = cell_species.count(species)
        unit_count = unit_species.count(species)
        require(cell_count == unit_count * round(determinant),
                "native cell/unit_cell incompatible: species counts do not match supercell")

    unit_inverse = np.linalg.inv(unit_lattice)
    for frac, species in zip(cell_frac, cell_species):
        cart = frac @ cell_lattice
        candidate = [np.linalg.norm(((((cart @ unit_inverse - other) + 0.5) % 1 - 0.5) @ unit_lattice))
                     for other, other_species in zip(unit_frac, unit_species) if other_species == species]
        require(candidate and min(candidate) <= 1e-5,
                "native cell/unit_cell incompatible: site/species image is unmapped")
    return {"supercell_matrix": integer_relation.tolist(), "determinant": round(determinant)}


def primitive_check(material, workspace):
    import spglib

    run = path(workspace, material["run_dir"], "directory")
    inputs = material["inputs"]
    require(isinstance(inputs, list), "materials[].inputs must be a list relative to run_dir")
    listed = {str(x) for x in inputs}
    require({"PASP.input", "cell.str", "unit_cell.str", "spin_exchange.dat", "spin3.in"} <= listed,
            "final input list missing mandatory files")
    for item in listed:
        path(run, item)
    input_file, cell_file, unit_file = (path(run, item) for item in ("PASP.input", "cell.str", "unit_cell.str"))
    fdf = effective(input_file)
    require({str(Path(record.origin.rsplit(":", 1)[0]).relative_to(run)) for record in fdf.records} <= listed,
            "final input list omits an effective include")
    first_origin(fdf, "LatticeVectors", cell_file)
    first_origin(fdf, "AtomicCoordinatesAndAtomicSpecies", cell_file)
    first_origin(fdf, "unit_cell_in_Ang", unit_file)
    first_origin(fdf, "Atoms_in_unit_cell_Ang", unit_file)
    require(norm(data_tokens(fdf.required("Model", False).body[0])[0]) == "magnon", "final Model is not magnon")
    supercell = [[integer(v) for v in row] for row in block_rows(fdf, "SuperCell")]
    require(supercell == [[1, 0, 0], [0, 1, 0], [0, 0, 1]], "final SuperCell must be identity")
    z = [integer(v) for row in block_rows(fdf, "Z_values") for v in row]
    a, af, asp = structure(fdf)
    u, uf, usp = structure(fdf, unit=True)
    require(np.allclose(a, u, atol=1e-7, rtol=0), "cell and unit_cell lattice mismatch")
    require(asp == usp and len(af) == len(uf), "cell and unit_cell site/species order mismatch")
    require(np.allclose((af-uf+0.5) % 1-0.5, 0, atol=1e-6, rtol=0), "cell and unit_cell coordinates mismatch")
    require(all(1 <= sid <= len(z) for sid in asp), "species outside Z_values")
    chemical = [z[sid-1] for sid in asp]
    counts = {}
    for tol in TOLERANCES:
        for label, lattice, frac in (("cell", a, af), ("unit_cell", u, uf)):
            reduced = spglib.find_primitive((lattice, frac, chemical), symprec=tol)
            require(reduced is not None, f"{label}: spglib failed at {tol}")
            counts[f"{label}@{tol}"] = len(reduced[2])
            require(len(reduced[2]) == len(chemical), f"{label}: chemical translation reduction at {tol}")
    spin = raw_rows(path(run, "spin3.in"))
    require(len(spin) == len(asp) and all(integer(row[0]) == i and len(row) == 4 for i, row in enumerate(spin, 1)),
            "spin3.in site order/count mismatch")
    ex_lattice, entries = exchange(path(run, "spin_exchange.dat"))
    require(np.allclose(ex_lattice, a, atol=1e-5, rtol=0), "final exchange lattice differs from primitive")
    endpoint_maps = []
    for row in entries:
        p, q = (np.array([finite(v) for v in row[start:start+3]]) for start in ((12, 15) if len(row) == 18 else (4, 7)))
        s1, s2 = (integer(row[10]), integer(row[11])) if len(row) == 18 else (integer(row[2]), integer(row[3]))
        require(1 <= s1 <= len(z) and 1 <= s2 <= len(z), "exchange species out of range")
        mapped = [map_endpoint(point, sid, a, af, asp) for point, sid in ((p, s1), (q, s2))]
        endpoint_maps.append(mapped)
    report = path(workspace, material["primitive_cell_report"])
    proof = json.loads(report.read_text())
    fields = ("source_cell", "source_lattice_ang", "transformation", "source_atom_count", "primitive_atom_count",
              "source_volume_ang3", "primitive_volume_ang3", "symprec_angstrom",
              "site_map", "species_map", "image_map", "exchange_map", "spin_map")
    require(all(key in proof for key in fields), "primitive report lacks source-to-final mapping fields")
    require(proof["primitive_atom_count"] == len(asp) and proof["site_map"] and
            proof["exchange_map"] and proof["spin_map"], "primitive report mapping/count incomplete")
    require(isinstance(proof["exchange_map"], list) and len(proof["exchange_map"]) == len(entries)
            and all(isinstance(entry, dict) and type(entry.get("final_row")) is int
                    for entry in proof["exchange_map"]),
            "primitive report exchange_map must contain one object per final row")
    report_rows = {entry["final_row"]: entry for entry in proof["exchange_map"]}
    require(set(report_rows) == set(range(1, len(entries) + 1)),
            "primitive report exchange_map does not cover final rows exactly")
    for row, mapped in zip(entries, endpoint_maps):
        entry = report_rows[int(row[0])]
        sites, images = report_endpoint_geometry(entry)
        row_species = ((integer(row[10]), integer(row[11])) if len(row) == 18 else
                       (integer(row[2]), integer(row[3])))
        if "endpoint_species_ids" in entry:
            require(entry["endpoint_species_ids"] == list(row_species),
                    f"exchange_map endpoint species id mismatch: row {row[0]}")
        reported_species = entry.get("endpoint_species")
        if reported_species is not None:
            require(isinstance(reported_species, list) and len(reported_species) == 2,
                    "exchange_map endpoint_species must have two entries")
            require(all(0 < z[sid - 1] < len(ELEMENTS) for sid in row_species) and
                    reported_species == [ELEMENTS[z[sid - 1]] for sid in row_species],
                    f"exchange_map endpoint species mismatch: row {row[0]}")
        require([mapped[0]["site"], mapped[1]["site"]] == sites,
                f"exchange_map endpoint site mismatch: row {row[0]}")
        require([mapped[0]["image"], mapped[1]["image"]] == images,
                f"exchange_map endpoint image mismatch: row {row[0]}")
    transform = np.asarray(proof["transformation"], dtype=float)
    require(transform.shape == (3, 3) and np.isfinite(transform).all() and abs(np.linalg.det(transform)) > 0,
            "primitive transformation must be a nonsingular 3x3 matrix")
    source_lattice = np.asarray(proof["source_lattice_ang"], dtype=float)
    require(source_lattice.shape == (3, 3) and np.isfinite(source_lattice).all() and
            np.allclose(transform @ source_lattice, a, atol=1e-5, rtol=0),
            "source-to-primitive lattice transformation disagrees with final cell")
    require(close(proof["source_volume_ang3"], abs(np.linalg.det(source_lattice)), 1e-4),
            "primitive report source volume differs from source lattice")
    ratio = finite(str(proof["source_volume_ang3"])) / finite(str(proof["primitive_volume_ang3"]))
    require(close(ratio, proof["source_atom_count"] / len(asp), 1e-4) and ratio >= 1,
            "source/final volume and atom-count ratios disagree")
    require(close(proof["primitive_volume_ang3"], abs(np.linalg.det(a)), 1e-4),
            "primitive report volume differs from final cell")
    return counts


def check(delivery, workspace, source):
    record = json.loads(delivery.read_text())
    materials = record["materials"]
    require(isinstance(materials, list) and materials, "materials must be a nonempty array")
    covered = set()
    findings = {}
    for material in materials:
        native = material["j_extraction"]
        require(native["method"] == "pasp_native", "J method must be pasp_native")
        path(workspace, native["evidence_report"])
        final = path(workspace, native["final_exchange"])
        run_dir = path(workspace, material["run_dir"], "directory")
        require(final == path(run_dir, "spin_exchange.dat") and "spin_exchange.dat" in material["inputs"],
                "final_exchange does not name the consumed final input")
        final_lattice, final_rows = exchange(final)
        native_rows = {}
        for run in native["runs"]:
            input_file = path(workspace, run["input"])
            base = input_file.parent
            log = path(workspace, run["log"])
            output = path(workspace, run["output"])
            fdf = effective(input_file)
            require(norm(data_tokens(fdf.required("Model", False).body[0])[0]) == "findjpathsym", "native Model mismatch")
            require(norm(data_tokens(fdf.required("cal_spin_exchange", False).body[0])[0]) in ("t", "true", "yes"),
                    "native calculation flag absent")
            listed = set(run["inputs"])
            require("PASP.input" in listed and all(not item.endswith(("spin_exchange.dat", "log.out")) for item in listed),
                    "native input list missing PASP.input or includes output")
            for item in listed:
                path(base, item)
            require({str(Path(record.origin.rsplit(":", 1)[0]).relative_to(base)) for record in fdf.records} <= listed,
                    "native input list omits an effective include")
            native_structure_compatibility(fdf)
            require(output == path(base, "spin_exchange.dat"), "native output path not generated in input directory")
            _, rows = exchange(output)
            require(all(len(row) == 10 for row in rows), "native output must have scalar 10-field rows")
            require(len(run["quartet_map"]) == len(rows), "native row/map count mismatch")
            seen_pairs = set()
            for item in run["quartet_map"]:
                i = item["native_pair"]
                require(type(i) is int and 1 <= i <= len(rows), "native_pair out of range")
                require(i not in seen_pairs, "duplicate native row mapping")
                seen_pairs.add(i)
                pair = item["source_pair"]
                require(pair not in covered, f"quartet mapped twice: {pair}")
                require(set(item["states"]) == set(STATES) and set(item["states"].values()) == set(SOURCE_STATES),
                        "state mapping must be a four-state bijection")
                for target, original in item["states"].items():
                    staged = path(base, f"J{i}/{target}/OSZICAR")
                    raw = path(source, f"{pair}/{original}/OSZICAR")
                    require(staged.read_bytes() == raw.read_bytes(), f"OSZICAR bytes differ: {pair}/{original}")
                    require(f"J{i}/{target}/OSZICAR" in listed, "native input list omits OSZICAR")
                covered.add(pair)
                native_rows.setdefault(str(output), {})[i] = rows[i-1]
            log_text = log.read_text()
            for i in seen_pairs:
                for state in STATES:
                    require(f"J{i}/{state}/OSZICAR" in log_text,
                            f"native log lacks OSZICAR read: J{i}/{state}")
            require("read_four_state_result: VASP calculation is not converged" not in log_text and
                    "read_four_state_result: no OSZICAR is found" not in log_text,
                    "native log reports failed four-state read")
        require(len(native["lineage"]) == len(final_rows), "final/native lineage row count mismatch")
        seen_final = set()
        for item in native["lineage"]:
            i = item["final_row"]
            require(type(i) is int and 1 <= i <= len(final_rows), "final_row out of range")
            require(i not in seen_final, "duplicate final lineage row")
            seen_final.add(i)
            output = str(path(workspace, item["native_output"]))
            row = native_rows.get(output, {}).get(item["native_row"])
            require(row is not None, "lineage references unmapped native row")
            scale = item.get("scale", 1)
            require(type(scale) in (float, int) and math.isfinite(scale) and scale != 0, "invalid scale")
            require(close(scale, 1) or item.get("reason"), "scale change needs reason")
            target_j = finite(row[1]) * scale
            dest = final_rows[i-1]
            values = [finite(dest[j]) for j in (1, 5, 9)] if len(dest) == 18 else [finite(dest[1])]
            require(all(close(value, target_j) for value in values), "final J differs from native lineage")
            if len(dest) == 18:
                require(all(close(finite(dest[j]), 0) for j in (2, 3, 4, 6, 7, 8)), "final J matrix is anisotropic")
        findings[material.get("name", material.get("material", str(len(findings))))] = primitive_check(material, workspace)
    expected = {str(p.relative_to(source)) for p in source.rglob("*") if p.is_dir() and
                all((p / state / "OSZICAR").is_file() for state in SOURCE_STATES)}
    require(covered == expected, f"quartet coverage mismatch: missing={sorted(expected-covered)}, extra={sorted(covered-expected)}")
    return {"status": "pass", "quartets": len(covered), "primitive_counts": findings,
            "scope": "receipt bytes, native numeric lineage, effective dual primitive; no physical-model certification"}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("delivery", type=Path)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = check(args.delivery, args.workspace.resolve(), args.source.resolve())
    except (ValueError, KeyError, IndexError, OSError, CheckFailure, ImportError, TypeError) as exc:
        result = {"status": "fail", "error": str(exc)}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
