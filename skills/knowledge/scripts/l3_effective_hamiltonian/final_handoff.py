#!/usr/bin/env python3
"""Validate and receipt a published L3 native-model consumer package.

This is a mechanical handoff check.  It proves that the declared model and
coverage/prediction artifacts are present at the requested consumer root and
that references do not escape through symlinks.  It deliberately does not
judge physical assumptions, PASP output quality, or an accuracy threshold.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys


MODEL_KEYS = frozenset((
    "basis_file", "lm_file", "fit_report", "fit_log", "feature_matrix",
    "row_ids", "encoding_root", "encoding_template", "energy_divisor",
))
SPLITS = ("train", "selection", "test")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON: {path}: {exc}") from exc


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_relative(value, label: str) -> Path:
    require(isinstance(value, str) and value, f"{label} must be a nonempty path")
    rel = Path(value)
    require(not rel.is_absolute() and ".." not in rel.parts and str(rel) == value,
            f"{label} must be normalized and consumer-root-relative: {value!r}")
    return rel


def checked_path(root: Path, value, label: str, *, directory: bool = False) -> Path:
    rel = safe_relative(value, label)
    path = root / rel
    require(path.exists(), f"{label} is missing: {rel}")
    require(not path.is_symlink(), f"{label} is a symlink: {rel}")
    require(path.resolve().is_relative_to(root), f"{label} escapes consumer root: {rel}")
    require(path.is_dir() if directory else path.is_file(),
            f"{label} has wrong type: {rel}")
    for parent in path.parents:
        if parent == root:
            break
        require(not parent.is_symlink(), f"{label} uses a symlinked parent: {rel}")
    if directory:
        entries = list(path.rglob("*"))
        require(entries, f"{label} is empty: {rel}")
        for entry in entries:
            require(not entry.is_symlink(), f"{label} contains a symlink: {entry.relative_to(root)}")
            require(entry.is_file() or entry.is_dir(), f"{label} contains a special file: {entry.relative_to(root)}")
    return path


def _status(coverage: dict) -> str:
    status = coverage.get("status")
    if status is None and isinstance(coverage.get("passed"), bool):
        status = "qualifying" if coverage["passed"] else "nonqualifying"
    require(status in ("qualifying", "nonqualifying"),
            "fgt-coverage.json must declare status qualifying/nonqualifying (or boolean passed)")
    return status


def _has_failure_marker(value) -> bool:
    keys = {"failed_gate", "failed_gates", "errors", "failure", "limitation", "limitations"}
    if isinstance(value, dict):
        for key, item in value.items():
            if key in keys and item not in (None, [], ""):
                return True
            if key == "passed" and item is False:
                return True
            if _has_failure_marker(item):
                return True
    elif isinstance(value, list):
        return any(_has_failure_marker(item) for item in value)
    return False


def _validate_predictions(root: Path) -> dict:
    result = {}
    for split in SPLITS:
        name = f"{split}_predictions.csv"
        path = checked_path(root, name, name)
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        require(rows, f"{name} has no prediction rows")
        require(set(rows[0]) >= {"sample_id", "target", "prediction"},
                f"{name} needs sample_id,target,prediction columns")
        for ordinal, row in enumerate(rows, 1):
            require(row.get("sample_id", "") != "" and row.get("target", "") != "" and
                    row.get("prediction", "") != "", f"{name} row {ordinal} is incomplete")
        result[split] = {"path": name, "count": len(rows), "sha256": digest(path)}
    return result


def validate(root: Path, model_name: str = "fgt-model.json") -> dict:
    root = Path(root)
    require(root.is_dir() and not root.is_symlink(), f"consumer root is not a real directory: {root}")
    root = root.resolve()
    model_path = checked_path(root, model_name, "model manifest")
    model = load_json(model_path)
    require(isinstance(model, dict) and set(model) == MODEL_KEYS,
            "model manifest has the wrong fields")
    require(type(model["energy_divisor"]) is int and model["energy_divisor"] > 0,
            "model energy_divisor must be a positive integer")
    references = {}
    for key in sorted(MODEL_KEYS - {"energy_divisor"}):
        is_dir = key in {"encoding_root", "encoding_template"}
        references[key] = checked_path(root, model[key], f"model.{key}", directory=is_dir)

    coverage_path = checked_path(root, "fgt-coverage.json", "coverage manifest")
    coverage = load_json(coverage_path)
    require(isinstance(coverage, dict), "fgt-coverage.json must be an object")
    status = _status(coverage)
    if status == "nonqualifying":
        require(_has_failure_marker(coverage),
                "nonqualifying coverage must preserve its failed gate or limitation")

    report = checked_path(root, "report.md", "report")
    predictions = _validate_predictions(root)
    # Optional receipts are checked when present, so a stale or malformed receipt
    # cannot be mistaken for a completed handoff.
    optional = {}
    for name in ("publication-receipt.json", "native-freeze.json", "final-evaluation.json", "fit-handoff.json"):
        path = root / name
        if path.exists():
            require(not path.is_symlink() and path.is_file(), f"optional receipt is not a regular file: {name}")
            load_json(path)
            optional[name] = digest(path)

    files = {"model": digest(model_path), "coverage": digest(coverage_path), "report": digest(report),
             "references": {key: digest(path) if path.is_file() else None for key, path in references.items()},
             "predictions": predictions, "optional_receipts": optional}
    return {"schema_version": 1,
            "scope": "consumer-root presence, path safety and prediction-table shape; not scientific acceptance",
            "status": status, "consumer_root": str(root), "model_manifest": model_name,
            "artifacts": files}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--model", default="fgt-model.json")
    args = parser.parse_args(argv)
    try:
        receipt = validate(args.root, args.model)
        out = args.root.resolve() / "final-handoff.json"
        encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        if out.exists():
            require(not out.is_symlink() and out.read_text(encoding="utf-8") == encoded,
                    "existing final-handoff.json differs; use a new consumer root")
        else:
            out.write_text(encoded, encoding="utf-8")
        print(encoded, end="")
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"final-handoff: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
