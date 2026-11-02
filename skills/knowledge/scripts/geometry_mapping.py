#!/usr/bin/env python3
"""Audit four-state bond identity and source-image-preserving primitive maps.

The input is deliberately small and material agnostic.  It contains a source
row-vector lattice, fractional sites, endpoint records (site, species and an
explicit integer image), optional row-vector space-group operations, and an
optional final lattice/sites object.  No exchange values or class labels are
used.  Endpoint matching is done in Cartesian space and returns the integer
image in the final basis; a minimum-image reduction is never applied.

This script is portable and has no PASP/source-tree dependency.  The row-vector
convention is ``cartesian = fractional @ lattice`` and operations are
``fractional' = fractional @ rotation + translation``.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


class GeometryError(ValueError):
    pass


def _matrix(value, name):
    rows = [[float(x) for x in row] for row in value]
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise GeometryError(f"{name} must be a 3x3 matrix")
    if any(not math.isfinite(x) for row in rows for x in row):
        raise GeometryError(f"{name} contains a non-finite value")
    return rows


def _det(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def _inverse(m):
    d = _det(m)
    if abs(d) < 1e-14:
        raise GeometryError("lattice is singular")
    return [[(m[(j + 1) % 3][(i + 1) % 3] * m[(j + 2) % 3][(i + 2) % 3]
              - m[(j + 1) % 3][(i + 2) % 3] * m[(j + 2) % 3][(i + 1) % 3]) / d
             for j in range(3)] for i in range(3)]


def _row_times_matrix(row, matrix):
    return [sum(row[k] * matrix[k][j] for k in range(3)) for j in range(3)]


def _norm(v):
    return math.sqrt(sum(x * x for x in v))


def _rounded(v, digits=9):
    return tuple(round(float(x), digits) for x in v)


def _validate_endpoint(endpoint, sites, label, lattice, tolerance):
    try:
        site = endpoint["site"]
        image = endpoint["image"]
        frac = [float(x) for x in endpoint["frac"]]
        species = endpoint["species"]
    except (KeyError, TypeError, ValueError) as exc:
        raise GeometryError(f"{label}: endpoint requires site, frac, species and integer image") from exc
    if (not isinstance(site, int) or isinstance(site, bool)
            or len(frac) != 3 or not isinstance(image, list) or len(image) != 3
            or any(not isinstance(x, int) or isinstance(x, bool) for x in image)
            or any(not math.isfinite(x) for x in frac)):
        raise GeometryError(f"{label}: malformed frac/image")
    if site < 0 or site >= len(sites):
        raise GeometryError(f"{label}: site index out of range")
    if sites[site]["species"] != species:
        raise GeometryError(f"{label}: species disagrees with site table")
    site_residual = _norm(_row_times_matrix(
        [frac[i] - sites[site]["frac"][i] for i in range(3)], lattice))
    if site_residual > tolerance:
        raise GeometryError(f"{label}: frac disagrees with claimed source site by {site_residual:.9g} Ang")
    return {"site": site, "frac": frac, "species": species, "image": image}


def endpoint_cart(endpoint, lattice):
    return _row_times_matrix([endpoint["frac"][i] + endpoint["image"][i] for i in range(3)], lattice)


def map_endpoint(endpoint, source_lattice, final_lattice, final_sites, tolerance=1e-5):
    """Map one source endpoint without changing its relative lattice image."""
    source_lattice = _matrix(source_lattice, "source_lattice")
    final_lattice = _matrix(final_lattice, "final_lattice")
    source_cart = endpoint_cart(endpoint, source_lattice)
    inv_final = _inverse(final_lattice)
    raw = _row_times_matrix(source_cart, inv_final)
    candidates = []
    for index, site in enumerate(final_sites):
        if site["species"] != endpoint["species"]:
            continue
        frac = [float(x) for x in site["frac"]]
        if len(frac) != 3:
            raise GeometryError("final site has malformed frac")
        image = [int(round(raw[i] - frac[i])) for i in range(3)]
        residual = _norm(_row_times_matrix(
            [raw[i] - frac[i] - image[i] for i in range(3)], final_lattice))
        candidates.append((residual, index, image))
    if not candidates:
        raise GeometryError(f"no final site with species {endpoint['species']!r}")
    candidates.sort(key=lambda item: item[0])
    if candidates[0][0] > tolerance:
        raise GeometryError(f"final endpoint residual {candidates[0][0]:.9g} exceeds {tolerance:g} Ang")
    if len(candidates) > 1 and candidates[1][0] <= tolerance:
        raise GeometryError("final endpoint mapping is not unique")
    residual, index, image = candidates[0]
    reconstructed = _row_times_matrix(
        [final_sites[index]["frac"][i] + image[i] for i in range(3)], final_lattice)
    return {"final_site": index, "final_image": image, "residual_angstrom": residual,
            "cartesian": source_cart, "reconstructed_cartesian": reconstructed}


def map_pair(endpoints, source_lattice, final_lattice, final_sites, tolerance=1e-5):
    """Map both endpoints, then validate their unwrapped bond as one object.

    Mapping endpoints independently is useful for locating sites, but it can
    hide a lost relative lattice image when a later caller applies a
    minimum-image reduction.  This pair-level result keeps the two Cartesian
    positions and rejects any final reconstruction that does not reproduce the
    source bond vector within the requested tolerance.
    """
    if len(endpoints) != 2:
        raise GeometryError("an exchange pair needs exactly two endpoints")
    mapped = [map_endpoint(endpoint, source_lattice, final_lattice, final_sites, tolerance)
              for endpoint in endpoints]
    source_bond = [mapped[1]["cartesian"][i] - mapped[0]["cartesian"][i] for i in range(3)]
    final_bond = [mapped[1]["reconstructed_cartesian"][i]
                  - mapped[0]["reconstructed_cartesian"][i] for i in range(3)]
    residual = _norm([source_bond[i] - final_bond[i] for i in range(3)])
    if residual > 2 * tolerance:
        raise GeometryError(f"bond reconstruction residual {residual:.9g} exceeds {2 * tolerance:g} Ang")
    return {"endpoints": mapped, "source_bond_cartesian": source_bond,
            "final_bond_cartesian": final_bond, "bond_residual_angstrom": residual}


def orbit_signature(endpoints, operations=(), digits=8):
    """Return a geometry-only signature invariant under supplied operations.

    Absolute endpoint-1 fractional position modulo a lattice translation and
    the unwrapped endpoint-2 minus endpoint-1 vector are retained.  Both
    endpoint orders are considered, so equal distances do not collapse
    distinct endpoint-pair orbits.
    """
    if len(endpoints) != 2:
        raise GeometryError("an exchange pair needs exactly two endpoints")
    ops = operations or [{"rotation": [[1, 0, 0], [0, 1, 0], [0, 0, 1]], "translation": [0, 0, 0]}]
    values = []
    for op in ops:
        rotation = _matrix(op["rotation"], "operation rotation")
        translation = [float(x) for x in op.get("translation", [0, 0, 0])]
        if len(translation) != 3:
            raise GeometryError("operation translation must have three values")
        transformed = []
        for endpoint in endpoints:
            x = [endpoint["frac"][i] + endpoint["image"][i] for i in range(3)]
            y = _row_times_matrix(x, rotation)
            transformed.append([y[i] + translation[i] for i in range(3)])
        for first, second in ((0, 1), (1, 0)):
            anchor = [transformed[first][i] - math.floor(transformed[first][i]) for i in range(3)]
            delta = [transformed[second][i] - transformed[first][i] for i in range(3)]
            values.append((endpoints[first]["species"], endpoints[second]["species"],
                           _rounded(anchor, digits), _rounded(delta, digits)))
    return min(values)


def orbit_groups(pairs, operations=(), digits=8):
    groups = defaultdict(list)
    for index, pair in enumerate(pairs):
        groups[orbit_signature(pair, operations, digits)].append(index)
    return {str(signature): members for signature, members in sorted(groups.items(), key=lambda item: str(item[0]))}


def audit(payload):
    source_lattice = _matrix(payload["source_lattice"], "source_lattice")
    tolerance = float(payload.get("tolerance_angstrom", 1e-5))
    if not math.isfinite(tolerance) or tolerance <= 0:
        raise GeometryError("tolerance_angstrom must be finite and positive")
    source_sites = payload["source_sites"]
    if not source_sites:
        raise GeometryError("source_sites must not be empty")
    sites = []
    for i, site in enumerate(source_sites):
        frac = [float(x) for x in site["frac"]]
        if len(frac) != 3:
            raise GeometryError(f"source site {i} has malformed frac")
        sites.append({"frac": frac, "species": site["species"]})
    operations = payload.get("operations", [])
    pairs = []
    for pair_index, raw_pair in enumerate(payload.get("pairs", [])):
        if len(raw_pair) != 2:
            raise GeometryError(f"pair {pair_index} must contain two endpoints")
        pair = [_validate_endpoint(raw_pair[i], sites, f"pair {pair_index} endpoint {i}",
                                   source_lattice, tolerance) for i in range(2)]
        pairs.append(pair)
    result = {"orbit_groups": orbit_groups(pairs, operations), "pairs": []}
    final = payload.get("final")
    if final is not None:
        final_lattice = _matrix(final["lattice"], "final lattice")
        final_sites = [{"frac": [float(x) for x in site["frac"]], "species": site["species"]}
                       for site in final["sites"]]
    else:
        final_lattice = final_sites = None
    for pair in pairs:
        row = {"source": [{"site": e["site"], "species": e["species"], "image": e["image"]} for e in pair],
               "orbit_signature": orbit_signature(pair, operations)}
        if final is not None:
            mapped_pair = map_pair(pair, source_lattice, final_lattice, final_sites, tolerance)
            row["final"] = mapped_pair["endpoints"]
            row["source_bond_cartesian"] = mapped_pair["source_bond_cartesian"]
            row["final_bond_cartesian"] = mapped_pair["final_bond_cartesian"]
            row["bond_residual_angstrom"] = mapped_pair["bond_residual_angstrom"]
        result["pairs"].append(row)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("geometry", type=Path, help="JSON geometry audit input")
    args = parser.parse_args()
    try:
        result = audit(json.loads(args.geometry.read_text()))
    except (OSError, KeyError, TypeError, ValueError, GeometryError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({"status": "pass", **result}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
