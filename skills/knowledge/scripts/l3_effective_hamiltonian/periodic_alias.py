#!/usr/bin/env python3
"""Diagnose pair-orbit aliasing for a supplied diagonal training supercell."""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import product
import math
from pathlib import Path
import sys

from study_contract import identifier, json_bytes, load, require


def signature(shape, pairs):
    require(isinstance(shape, list) and len(shape) == 3 and
            all(type(n) is int and n > 0 for n in shape), "supercell needs three positive integers")
    require(isinstance(pairs, list) and bool(pairs), "pair orbit must not be empty")
    edges = Counter()
    for pair in pairs:
        require(set(pair) == {"sites", "shift"}, "pair needs sites and shift")
        sites, shift = pair["sites"], pair["shift"]
        require(isinstance(sites, list) and len(sites) == 2 and
                all(identifier(s) >= 0 for s in sites), "invalid primitive site ids")
        require(isinstance(shift, list) and len(shift) == 3 and
                all(type(n) is int for n in shift), "shift needs three integers")
        for cell in product(*(range(n) for n in shape)):
            other = tuple((i + d) % n for i, d, n in zip(cell, shift, shape))
            edge = tuple(sorted(((sites[0], *cell), (sites[1], *other))))
            edges[edge] += 1
    # Orbit size can change feature normalization; retain relative multiplicities.
    scale = math.gcd(*edges.values())
    return tuple(sorted((edge, count // scale) for edge, count in edges.items()))


def check(spec):
    orbits = spec["pair_orbits"]
    require(isinstance(orbits, list) and len(orbits) >= 2, "need at least two supplied pair orbits")
    names = [o["name"] for o in orbits]
    require(all(isinstance(n, str) and n for n in names) and len(set(names)) == len(names),
            "orbit names must be unique text")
    train = [signature(spec["training_supercell"], o["pairs"]) for o in orbits]
    target = [signature(spec["target_supercell"], o["pairs"]) for o in orbits]
    collisions = []
    for i, a in enumerate(train):
        for j in range(i + 1, len(train)):
            if a == train[j]:
                collisions.append({"orbits": [names[i], names[j]],
                                   "target_distinguishes": target[i] != target[j]})
    return {"scope": "supplied pair-orbit geometry; not full Hamiltonian identifiability",
            "training_supercell": spec["training_supercell"],
            "target_supercell": spec["target_supercell"], "collisions": collisions,
            "status": "unresolved_aliasing" if collisions else "no_supplied_pair_alias_found"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = check(load(args.manifest))
        print(json_bytes(result).decode(), end="")
        return 2 if result["collisions"] else 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"periodic-alias: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
