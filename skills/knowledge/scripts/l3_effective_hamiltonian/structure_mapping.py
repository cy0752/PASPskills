#!/usr/bin/env python3
"""Check an integer primitive-to-configuration cell relation and atom map.

The JSON input uses row-vector coordinates: ``cartesian = fractional @ lattice``.
For relation ``M``, the expected configuration lattice is ``M @ primitive`` and
configuration fractional coordinates map to the primitive frame as ``f_conf @ M``.
This is a geometry/provenance check only; it does not discover a primitive cell
or decide whether a model is scientifically suitable.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path


class MappingError(ValueError):
    pass


def _matrix(value, name):
    if not isinstance(value, list) or len(value) != 3 or any(not isinstance(row, list) or len(row) != 3 for row in value):
        raise MappingError(f"{name} must be a 3x3 matrix")
    matrix = [[float(x) for x in row] for row in value]
    if any(not math.isfinite(x) for row in matrix for x in row):
        raise MappingError(f"{name} contains a non-finite value")
    return matrix


def _det(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def _inverse(m):
    d = _det(m)
    if abs(d) < 1e-14:
        raise MappingError("lattice or relation is singular")
    return [[(m[(j + 1) % 3][(i + 1) % 3] * m[(j + 2) % 3][(i + 2) % 3]
              - m[(j + 1) % 3][(i + 2) % 3] * m[(j + 2) % 3][(i + 1) % 3]) / d
             for j in range(3)] for i in range(3)]


def _row_matrix(row, matrix):
    return [sum(row[k] * matrix[k][j] for k in range(3)) for j in range(3)]


def _norm(row):
    return math.sqrt(sum(x * x for x in row))


def _sites(value, name):
    if not isinstance(value, list) or not value:
        raise MappingError(f"{name} sites must be a non-empty list")
    sites = []
    for index, site in enumerate(value):
        if not isinstance(site, dict) or not isinstance(site.get("species"), str):
            raise MappingError(f"{name} site {index} needs a species")
        frac = site.get("frac")
        if not isinstance(frac, list) or len(frac) != 3:
            raise MappingError(f"{name} site {index} needs three fractional coordinates")
        coords = [float(x) for x in frac]
        if any(not math.isfinite(x) for x in coords):
            raise MappingError(f"{name} site {index} has non-finite coordinates")
        sites.append({"species": site["species"], "frac": coords})
    return sites


def check(payload):
    tolerance = float(payload.get("tolerance_angstrom", 1e-5))
    if not math.isfinite(tolerance) or tolerance <= 0:
        raise MappingError("tolerance_angstrom must be finite and positive")
    primitive, configuration = payload["primitive"], payload["configuration"]
    primitive_lattice = _matrix(primitive["lattice"], "primitive lattice")
    configuration_lattice = _matrix(configuration["lattice"], "configuration lattice")
    relation = _matrix(payload["relation"], "relation")
    integer_relation = [[int(round(x)) for x in row] for row in relation]
    if any(abs(relation[i][j] - integer_relation[i][j]) > 1e-8 for i in range(3) for j in range(3)):
        raise MappingError("relation must contain integers")
    relation_det = _det(integer_relation)
    if relation_det <= 0 or abs(relation_det - round(relation_det)) > 1e-8:
        raise MappingError("relation determinant must be a positive integer")
    determinant = int(round(relation_det))
    expected_lattice = [_row_matrix(row, primitive_lattice) for row in integer_relation]
    lattice_residual = max(_norm([configuration_lattice[i][j] - expected_lattice[i][j] for j in range(3)])
                           for i in range(3))
    if lattice_residual > tolerance:
        raise MappingError(f"configuration lattice disagrees with relation by {lattice_residual:.9g} Ang")
    primitive_sites = _sites(primitive["sites"], "primitive")
    configuration_sites = _sites(configuration["sites"], "configuration")
    if len(configuration_sites) != determinant * len(primitive_sites):
        raise MappingError("configuration site count is not determinant times primitive count")
    counts = Counter(site["species"] for site in primitive_sites)
    configuration_counts = Counter(site["species"] for site in configuration_sites)
    if configuration_counts != Counter({species: count * determinant for species, count in counts.items()}):
        raise MappingError("configuration species counts do not follow the relation")
    mapping, multiplicities = [], Counter()
    for index, site in enumerate(configuration_sites):
        mapped = _row_matrix(site["frac"], integer_relation)
        candidates = []
        for primitive_index, primitive_site in enumerate(primitive_sites):
            if primitive_site["species"] != site["species"]:
                continue
            delta = [mapped[j] - primitive_site["frac"][j] - round(mapped[j] - primitive_site["frac"][j]) for j in range(3)]
            residual = _norm(_row_matrix(delta, primitive_lattice))
            if residual <= tolerance:
                candidates.append((residual, primitive_index))
        if not candidates:
            raise MappingError(f"configuration site {index} has no primitive match")
        candidates.sort()
        if len(candidates) > 1 and candidates[1][0] <= tolerance:
            raise MappingError(f"configuration site {index} maps ambiguously")
        residual, primitive_index = candidates[0]
        mapping.append({"configuration_site": index, "primitive_site": primitive_index,
                        "residual_angstrom": residual})
        multiplicities[primitive_index] += 1
    if any(multiplicities[i] != determinant for i in range(len(primitive_sites))):
        raise MappingError("primitive site multiplicities are inconsistent")
    return {"status": "pass", "relation": integer_relation, "determinant": determinant,
            "volume_ratio": abs(_det(configuration_lattice) / _det(primitive_lattice)),
            "lattice_residual_angstrom": lattice_residual,
            "species_counts": {key: configuration_counts[key] for key in sorted(configuration_counts)},
            "max_site_residual_angstrom": max(row["residual_angstrom"] for row in mapping),
            "mapping": mapping}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("geometry", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(check(json.loads(args.geometry.read_text())), indent=2, sort_keys=True))
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
