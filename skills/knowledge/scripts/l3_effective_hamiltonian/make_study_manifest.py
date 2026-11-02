#!/usr/bin/env python3
"""Build a full-study conversion manifest from a completed method-6 batch.

The batch root and the manifest root are allowed to be siblings.  Every source
path is resolved from the file that owns it and then written relative to the
manifest, so a nested helper cannot accidentally prefix an absolute workspace
path or call ``Path.relative_to`` on unrelated directories.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

from study_contract import json_bytes, load, require


def finite_positive(value: str) -> float:
    result = float(value.replace("D", "E").replace("d", "e"))
    require(math.isfinite(result) and result > 0, "energy divisor must be positive and finite")
    return result


def resolve(anchor: Path, value: str) -> Path:
    require(isinstance(value, str) and value, "source path must be nonempty text")
    path = Path(value)
    return (path if path.is_absolute() else anchor / path).resolve()


def relpath(path: Path, base: Path) -> str:
    # relpath, unlike Path.relative_to, is defined for sibling roots as well.
    return os.path.relpath(path, base).replace(os.sep, "/")


def checked_source(path: Path, label: str) -> Path:
    require(path.is_file(), f"missing {label}: {path}")
    return path


def build(batch_path: Path, output: Path, energy: str, split: str, basis: str,
          energy_header: str, divisor: float, require_identity: bool,
          source_energy_atol: float | None) -> dict:
    batch_path = batch_path.resolve()
    output = output.resolve()
    base = output.parent
    batch_root = batch_path.parent
    batch = load(batch_path)
    require(batch.get("complete") is True, "method-6 batch is not complete")
    rows = batch.get("results")
    samples = batch.get("samples")
    require(isinstance(rows, list) and isinstance(samples, list) and rows and
            len(rows) == len(samples), "batch results/samples are missing or inconsistent")
    statuses = {}
    for row in rows:
        require(isinstance(row, dict) and type(row.get("id")) is int,
                "batch result IDs must be JSON integers")
        require(row["id"] not in statuses, "batch result IDs must be unique")
        statuses[row["id"]] = row.get("status")
    require(all(status == "ok" for status in statuses.values()),
            "every batch sample must have status ok")

    entries = []
    seen = set()
    for sample in samples:
        sid = sample.get("id")
        require(type(sid) is int and sid not in seen, "batch sample IDs must be unique JSON integers")
        seen.add(sid)
        require(statuses.get(sid) == "ok", f"batch result missing successful sample: {sid}")
        original_id = sample.get("original_id", sid)
        require(type(original_id) is int, f"sample {sid} original_id must be a JSON integer")
        entry = {"id": sid, "original_id": original_id}
        for key in ("features", "basis_file", "log", "exit_code_file"):
            checked = checked_source(resolve(batch_root, sample[key]), f"sample {sid} {key}")
            entry[key] = relpath(checked, base)
        for key in ("source_identity", "encoding_identity"):
            if key in sample:
                checked = checked_source(resolve(batch_root, sample[key]), f"sample {sid} {key}")
                entry[key] = relpath(checked, base)
        if require_identity:
            require("source_identity" in entry and "encoding_identity" in entry,
                    f"sample {sid} lacks source/encoding identity records")
        entries.append(entry)
    require(seen == set(statuses), "batch result/sample ID sets differ")

    checked_source(resolve(Path.cwd(), energy), "energy table")
    checked_source(resolve(Path.cwd(), split), "split file")
    checked_source(resolve(Path.cwd(), basis), "shared basis")
    if require_identity:
        require(source_energy_atol is not None and source_energy_atol >= 0 and
                math.isfinite(source_energy_atol),
                "source_energy_atol is required for source identity")

    manifest = {
        "energy_file": relpath(resolve(Path.cwd(), energy), base),
        "energy_header": energy_header,
        "split_file": relpath(resolve(Path.cwd(), split), base),
        "energy_divisor": divisor,
        "basis_file": relpath(resolve(Path.cwd(), basis), base),
        "samples": entries,
        "require_source_identity": require_identity,
    }
    if source_energy_atol is not None:
        manifest["source_energy_atol"] = source_energy_atol
    require(not output.exists(), f"refusing to overwrite existing manifest: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as handle:
        handle.write(json_bytes(manifest))
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--energy", required=True)
    parser.add_argument("--split", required=True)
    parser.add_argument("--basis", required=True)
    parser.add_argument("--energy-header", choices=("none", "one"), default="none")
    parser.add_argument("--energy-divisor", required=True, type=finite_positive)
    parser.add_argument("--require-source-identity", action="store_true")
    parser.add_argument("--source-energy-atol", type=float)
    args = parser.parse_args(argv)
    result = build(args.batch, args.output, args.energy, args.split, args.basis,
                   args.energy_header, args.energy_divisor,
                   args.require_source_identity, args.source_energy_atol)
    print(json.dumps({"output": str(args.output.resolve()), "sample_count": len(result["samples"])}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}")
        raise SystemExit(1)
