#!/usr/bin/env python3
"""Generate matching chemical primitive PASP structures from a VASP 5 POSCAR.

The report deliberately leaves exchange_map and spin_map empty: the user must
remap and audit those physical inputs before check_four_state_native.py passes.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import spglib


TOLERANCES = (1e-5, 1e-4, 1e-3)


def poscar(file):
    lines = [line.strip() for line in file.read_text().splitlines() if line.strip()]
    scale = float(lines[1])
    if scale <= 0:
        raise ValueError("POSCAR requires a positive length scale")
    lattice = np.array([[float(x) for x in line.split()[:3]] for line in lines[2:5]]) * scale
    if lattice.shape != (3, 3) or np.linalg.det(lattice) <= 0:
        raise ValueError("source lattice must be right-handed and nonsingular")
    symbols = lines[5].split()
    if not all(token.isalpha() for token in symbols):
        raise ValueError("VASP 5 POSCAR element-symbol line required")
    if len(set(symbols)) != len(symbols):
        raise ValueError("duplicate element symbols would hide chemical translations; merge equivalent columns before primitive reduction")
    counts = [int(x) for x in lines[6].split()]
    if len(counts) != len(symbols) or any(n < 1 for n in counts):
        raise ValueError("POSCAR species/count mismatch")
    cursor = 7 + (lines[7].lower().startswith("s"))
    mode = lines[cursor].lower()
    if not mode.startswith(("d", "c", "k")):
        raise ValueError("POSCAR coordinate mode must be Direct or Cartesian")
    n = sum(counts)
    xyz = np.array([[float(x) for x in line.split()[:3]] for line in lines[cursor+1:cursor+1+n]])
    if xyz.shape != (n, 3):
        raise ValueError("POSCAR atom count mismatch")
    frac = xyz if mode.startswith("d") else (xyz * scale) @ np.linalg.inv(lattice)
    species = [i for i, count in enumerate(counts, 1) for _ in range(count)]
    return lattice, frac % 1, species, symbols


def generate(source, output, symprec):
    source_lattice, source_frac, source_species, symbols = poscar(source)
    primitive = spglib.find_primitive((source_lattice, source_frac, source_species), symprec=symprec)
    if primitive is None:
        raise ValueError("spglib could not identify a chemical primitive cell")
    lattice, frac, species = primitive
    lattice, frac, species = np.asarray(lattice), np.asarray(frac), list(species)
    if np.linalg.det(lattice) < 0:
        lattice[0] *= -1
        frac[:, 0] *= -1
    order = sorted(range(len(species)), key=lambda i: species[i])
    frac, species = frac[order] % 1, [species[i] for i in order]
    cart = frac @ lattice
    for tol in TOLERANCES:
        reduced = spglib.find_primitive((lattice, frac, species), symprec=tol)
        if reduced is None or len(reduced[2]) != len(species):
            raise ValueError(f"generated cell is chemically reducible or invalid at {tol} Ang")

    site_map, image_map, residuals = [], [], []
    inverse = np.linalg.inv(lattice)
    for i, (position, sid) in enumerate(zip(source_frac @ source_lattice, source_species), 1):
        candidates = []
        for j, (target, final_sid) in enumerate(zip(frac, species), 1):
            if sid != final_sid:
                continue
            delta = position @ inverse - target
            center = np.rint(delta).astype(int)
            for offset in itertools.product((-1, 0, 1), repeat=3):
                image = center + offset
                residual = np.linalg.norm((delta - image) @ lattice)
                candidates.append((residual, j, image.tolist()))
        distance, j, image = min(candidates)
        if distance > 2 * symprec:
            raise ValueError(f"source site {i} has no primitive match ({distance:g} Ang)")
        site_map.append({"source_site": i, "primitive_site": j})
        image_map.append({"source_site": i, "image": image})
        residuals.append(float(distance))
    if set(item["primitive_site"] for item in site_map) != set(range(1, len(species)+1)):
        raise ValueError("source sites do not cover every primitive site")

    def vec(rows):
        return "\n".join(" ".join(f"{x:.16f}" for x in row) for row in rows)

    atom_rows = "\n".join(f"{vec([point])} {sid} {symbols[sid-1]} {i}"
                          for i, (point, sid) in enumerate(zip(cart, species), 1))
    cell = (f"NumberOfAtoms {len(species)}\nnumber_of_species {len(symbols)}\n"
            "LatticeConstant 1 Ang\n%block LatticeVectors\n" + vec(lattice) +
            "\n%endblock LatticeVectors\nAtomicCoordinatesFormat NotScaledCartesianAng\n"
            "%block AtomicCoordinatesAndAtomicSpecies\n" + atom_rows +
            "\n%endblock AtomicCoordinatesAndAtomicSpecies\n")
    unit = (f"unit_cell.na {len(species)}\n%block unit_cell_in_Ang\n" + vec(lattice) +
            "\n%endblock unit_cell_in_Ang\n%block Atoms_in_unit_cell_Ang\n" + atom_rows +
            "\n%endblock Atoms_in_unit_cell_Ang\n")
    report = {
        "source_cell": str(source), "source_lattice_ang": source_lattice.tolist(),
        "transformation": (lattice @ np.linalg.inv(source_lattice)).tolist(),
        "source_atom_count": len(source_species), "primitive_atom_count": len(species),
        "source_volume_ang3": float(np.linalg.det(source_lattice)),
        "primitive_volume_ang3": float(np.linalg.det(lattice)),
        "symprec_angstrom": list(TOLERANCES), "generation_symprec_angstrom": symprec,
        "species_map": [{"species_id": i, "element": symbol} for i, symbol in enumerate(symbols, 1)],
        "site_map": site_map, "image_map": image_map,
        "maximum_site_residual_angstrom": max(residuals),
        "exchange_map": [], "spin_map": [],
        "remapping_status": "incomplete: audit exchange endpoints/images, spin order and q basis",
    }
    if output.exists() and any((output / name).exists() for name in ("cell.str", "unit_cell.str", "primitive_cell_report.json")):
        raise FileExistsError("output already contains generated structures or report")
    output.mkdir(parents=True, exist_ok=True)
    (output / "cell.str").write_text(cell)
    (output / "unit_cell.str").write_text(unit)
    (output / "primitive_cell_report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path, help="VASP 5 POSCAR with chemical species")
    parser.add_argument("output", type=Path, help="new directory for dual structures and report")
    parser.add_argument("--symprec", type=float, default=1e-4)
    args = parser.parse_args()
    if not 0 < args.symprec <= 1e-3:
        parser.error("symprec must be in (0, 1e-3] Ang")
    result = generate(args.source.resolve(), args.output.resolve(), args.symprec)
    print(json.dumps({"primitive_atom_count": result["primitive_atom_count"],
                      "maximum_site_residual_angstrom": result["maximum_site_residual_angstrom"],
                      "remapping_status": result["remapping_status"]}, indent=2))


if __name__ == "__main__":
    main()
