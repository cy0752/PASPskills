#!/usr/bin/env python3
"""Full-ID L3 conversion and checked publication. Standard library; never runs PASP.

See the L3 state machine S7 for deferred-test native freeze/evaluation;
README.md describes the generic manifests and source assumptions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
from pathlib import Path
import sys

SPLITS = ("train", "selection", "test")
# The consumer contract for the frozen effective-Hamiltonian model manifest.
# Keep this check at publication time: a valid fit is still undeliverable when
# the controller cannot parse its model handoff.
MODEL_MANIFEST_KEYS = frozenset((
    "basis_file", "lm_file", "fit_report", "fit_log", "feature_matrix",
    "row_ids", "encoding_root", "encoding_template", "energy_divisor",
))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def number(value):
    require(not isinstance(value, bool), "boolean is not a numeric value")
    result = float(str(value).replace("D", "E").replace("d", "e"))
    require(math.isfinite(result), f"nonfinite value: {value}")
    return result


def identifier(value):
    require(type(value) is int, f"sample id must be a JSON integer: {value!r}")
    return value


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(data):
    return (json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)


def records(path):
    return [line.split("#", 1)[0].split("!", 1)[0].split()
            for line in Path(path).read_text().splitlines()
            if line.split("#", 1)[0].split("!", 1)[0].strip()]


def energies(path, header):
    require(header in ("none", "one"), "energy_header must be none or one")
    rows = records(path)
    require(bool(rows), "empty energy table")
    if header == "one":
        # Refuse to silently discard a valid first data record.
        try:
            int(rows[0][0])
            number(rows[0][1])
        except (ValueError, IndexError):
            pass
        else:
            raise ValueError("energy_header=one would discard a data record")
        rows = rows[1:]
    result = {}
    for row in rows:
        require(len(row) == 2, f"energy row must be id energy: {row}")
        sid = int(row[0])
        require(sid not in result, f"duplicate energy id: {sid}")
        result[sid] = number(row[1])
    require(bool(result), "no energy records")
    return result


def features(path):
    rows = records(path)
    require(bool(rows) and len(rows[0]) == 1, f"invalid feature header: {path}")
    count = int(rows[0][0])
    require(count > 0 and len(rows) == count + 1, f"feature count mismatch: {path}")
    result = []
    for index, row in enumerate(rows[1:], 1):
        require(len(row) == 2 and int(row[0]) == index,
                f"feature indices must be exactly 1..n in order: {path}")
        result.append(number(row[1]))
    return result


def split_ids(path, expected):
    data = load(path)
    splits = data["splits"]
    require(set(splits) == set(SPLITS), "need train, selection and held-out test splits")
    ids = []
    for name in SPLITS:
        require(isinstance(splits[name], list) and bool(splits[name]), f"empty/invalid split: {name}")
        ids.extend(identifier(sid) for sid in splits[name])
    require(len(ids) == len(set(ids)), "duplicate id within/across splits")
    require(set(ids) == set(expected), "split union must equal the entire energy table")
    return splits


def source(base, name):
    require(isinstance(name, str) and bool(name), "source path must be nonempty text")
    path = (base / name).resolve()
    require(path.is_file(), f"missing source file: {path}")
    require(not (base / name).is_symlink(), f"source artifact is a symlink: {base / name}")
    return path


def destination(root, name):
    require(isinstance(name, str) and bool(name), "destination must be nonempty text")
    rel = Path(name)
    require(not rel.is_absolute() and ".." not in rel.parts and str(rel) == name,
            f"destination must be a normalized relative path: {name}")
    path = root / rel
    require(path.resolve().is_relative_to(root.resolve()), f"destination escapes root: {name}")
    require(not any(p.is_symlink() for p in [path, *path.parents]),
            f"destination uses a symlink: {name}")
    return path


def validate_model_manifest(raw, name, base, destinations):
    """Validate the exact controller-facing model JSON before publication.

    Model paths are consumer-root-relative.  The source run may contain the
    referenced files already, while directory-valued paths (encodes/templates)
    need only be represented by an existing source path or a published child.
    """
    try:
        model = load_bytes(raw)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{name}: model manifest must be a JSON object") from exc
    require(isinstance(model, dict), f"{name}: model manifest must be a JSON object")
    require(set(model) == MODEL_MANIFEST_KEYS,
            f"{name}: model manifest fields must be exactly "
            f"{', '.join(sorted(MODEL_MANIFEST_KEYS))}")
    for key in MODEL_MANIFEST_KEYS - {"energy_divisor"}:
        value = model[key]
        require(isinstance(value, str) and bool(value),
                f"{name}: {key} must be a nonempty relative path")
        rel = Path(value)
        require(not rel.is_absolute() and ".." not in rel.parts and str(rel) == value,
                f"{name}: {key} must be a normalized consumer-relative path: {value}")
        require((base / rel).exists() or any(
            dest == value or Path(dest).is_relative_to(rel) for dest in destinations
        ), f"{name}: {key} points to a missing published/source path: {value}")
    divisor = model["energy_divisor"]
    require(type(divisor) is int and divisor > 0,
            f"{name}: energy_divisor must be a positive JSON integer")
    return model


def load_bytes(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique)


def write_package(root, files, receipt_name, receipt):
    """Validate everything before writing; keep old artifacts, commit receipt last.

    A filesystem interruption can leave partial files, never a new passing receipt.
    Existing identical files allow an interrupted publication to be resumed.
    """
    require(receipt_name not in files, "receipt cannot overwrite a published artifact")
    receipt["sha256"] = {name: digest(data) for name, data in files.items()}
    all_files = dict(files)
    all_files[receipt_name] = json_bytes(receipt)
    paths = {name: destination(root, name) for name in all_files}
    for name, path in paths.items():
        require(not any(p in paths.values() for p in path.parents), "destination file/directory collision")
        require(not any(p.exists() and not p.is_dir() for p in path.parents), "destination parent is a file")
        if path.exists():
            require(path.is_file() and path.read_bytes() == all_files[name],
                    f"refusing to overwrite changed artifact: {path}; use a new destination or versioned names")
    for name, path in paths.items():
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                handle.write(all_files[name])
        require(path.read_bytes() == all_files[name], f"published bytes differ: {path}")
    return receipt


def study(manifest):
    manifest = Path(manifest).resolve()
    spec = load(manifest)
    base = manifest.parent
    energy = source(base, spec["energy_file"])
    targets = energies(energy, spec["energy_header"])
    split = source(base, spec["split_file"])
    splits = split_ids(split, targets)
    provenance = {"manifest_sha256": digest(manifest.read_bytes()),
                  "energy_sha256": digest(energy.read_bytes()),
                  "split_sha256": digest(split.read_bytes())}
    return spec, base, targets, splits, provenance


def source_identity(base, sample, target, atol):
    """Check original identity and actual encoding input bytes against a source ledger."""
    from prepare_path_b_inputs import parse_last_toten

    src = source(base, sample["source_identity"])
    enc = source(base, sample["encoding_identity"])
    expected, used = load(src), load(enc)
    frozen = used["sha256"]
    original = identifier(sample.get("original_id", sample["id"]))
    require(identifier(expected["original_id"]) == original and
            identifier(used["original_id"]) == original, "original sample identity mismatch")
    outcar = source(src.parent, expected["outcar"])
    energy = number(parse_last_toten(outcar.read_text(errors="replace").splitlines(), outcar))
    require(abs(energy - target) <= atol, "energy differs from original sample final TOTEN")
    evidence = {"original_id": original, "source_record_sha256": digest(src.read_bytes()),
                "encoding_record_sha256": digest(enc.read_bytes()),
                "outcar": {"path": str(outcar), "sha256": digest(outcar.read_bytes())}}
    for role in ("structure", "magnetic_state"):
        expected_path = source(src.parent, expected[role])
        used_path = source(enc.parent, used[role])
        expected_data, used_data = expected_path.read_bytes(), used_path.read_bytes()
        require(bool(expected_data.strip()) and expected_data == used_data,
                f"encoding {role} differs from original final-state package")
        require(frozen[role] == digest(used_data),
                f"encoding {role} changed after input capture; regenerate features")
        evidence[role] = {"source_path": str(expected_path), "used_path": str(used_path),
                          "sha256": digest(used_data)}
    for role, key in (("features", "features"), ("basis", "basis_file")):
        path = source(base, sample[key])
        require(frozen[role] == digest(path.read_bytes()),
                f"{role} differs from captured encoding output; stale/mixed ene_symbol")
        evidence[role] = {"path": str(path), "sha256": frozen[role]}
    return evidence


def convert(manifest, root):
    spec, base, targets, splits, provenance = study(manifest)
    divisor = number(spec["energy_divisor"])
    require(divisor > 0, "energy_divisor must be positive and source-supported")
    basis_data = source(base, spec["basis_file"]).read_bytes()
    require(bool(basis_data.strip()), "empty shared basis")
    basis_hash = digest(basis_data)
    require(isinstance(spec["samples"], list), "samples must be a list")
    identity_required = spec.get("require_source_identity", False)
    require(type(identity_required) is bool, "require_source_identity must be boolean")
    identity_atol = number(spec.get("source_energy_atol", 0))
    require(identity_atol >= 0, "source_energy_atol must be nonnegative")
    data, evidence, feature_paths = {}, {}, set()
    original_ids = set()
    width = None
    for sample in spec["samples"]:
        sid = identifier(sample["id"])
        require(sid in targets and sid not in data, f"unexpected/duplicate sample: {sid}")
        paths = {k: source(base, sample[k]) for k in ("features", "basis_file", "log", "exit_code_file")}
        require(paths["features"] not in feature_paths, f"feature source reused for another sample: {sid}")
        feature_paths.add(paths["features"])
        require(int(paths["exit_code_file"].read_text().strip()) == 0, f"failed PASP sample: {sid}")
        require("PASP is finished gracefully" in paths["log"].read_text(errors="replace"),
                f"missing PASP completion evidence: {sid}")
        require(digest(paths["basis_file"].read_bytes()) == basis_hash, f"mixed basis: {sid}")
        values = features(paths["features"])
        if width is None:
            width = len(values)
        require(len(values) == width, f"feature width mismatch: {sid}")
        data[sid] = values
        evidence[sid] = {k: {"path": str(p), "sha256": digest(p.read_bytes())} for k, p in paths.items()}
        if identity_required or "source_identity" in sample or "encoding_identity" in sample:
            identity = source_identity(base, sample, targets[sid], identity_atol)
            require(identity["original_id"] not in original_ids, "original sample reused under another id")
            original_ids.add(identity["original_id"])
            evidence[sid]["source_identity"] = identity
    require(set(data) == set(targets), "samples must cover the entire energy table")
    files = {}
    for name, ids in splits.items():
        if name == "test":
            continue  # No test matrix is exposed during automatic exploration.
        rows = []
        for sid in ids:
            row = data[sid] + [number(targets[sid] / divisor)]
            rows.append(" ".join(f"{v:.16E}" for v in row))
        files[name + ".txt"] = ("\n".join(rows) + "\n").encode()
        files[name + ".ids.json"] = json_bytes(ids)
    receipt = {"scope": "full-ID conversion; not scientific or runtime acceptance",
               **provenance, "manifest_path": str(Path(manifest).resolve()),
               "basis_sha256": basis_hash, "energy_divisor": divisor,
               "feature_count": width, "splits": splits, "samples": evidence,
               "source_identity_checked": identity_required or len(original_ids) == len(data),
               "test_matrix": "deferred until native freeze"}
    return write_package(Path(root).resolve(), files, "conversion.json", receipt)


def freeze_native(conversion, handoff, root):
    """Validate and persist the native model BEFORE opening final test features.

    The conversion emits only train/selection matrices. Arbitrary raw-source
    access outside this pipeline still needs a history audit; this is no sandbox.
    """
    from fit_handoff import check

    conversion, handoff = Path(conversion).resolve(), Path(handoff).resolve()
    converted = load(conversion)
    require(converted.get("test_matrix") == "deferred until native freeze",
            "conversion already exposed a test matrix; clean isolation is unsupported")
    verify(conversion.parent, conversion.name)
    require(not (conversion.parent / "test.txt").exists(),
            "test matrix exists before freeze; inspect prior access, do not delete evidence")
    spec = load(handoff)
    require("fit_log" in spec and "fit_exit_code_file" in spec,
            "freeze requires native fit log and exit evidence")
    checked, _ = check(handoff)
    native_log = source(handoff.parent, spec["fit_log"]).read_text(errors="replace")
    require(not re.search(r"forrtl:|SIGSEGV|SIGABRT|BAD TERMINATION|MPI_ABORT|^\s*(ERROR|FATAL)\b|\bNaN\b",
                          native_log, re.I | re.M), "native fit log contains a runtime failure")
    require(checked["sources"]["basis_file"]["sha256"] == converted["basis_sha256"],
            "native handoff basis differs from conversion")
    for name in ("train", "selection"):
        require(checked["sources"][name + "_matrix"]["sha256"] ==
                converted["sha256"][name + ".txt"],
                f"{name}: native handoff differs from pristine conversion")
    # Source manifest identity is captured by convert; do not infer it from CWD.
    manifest_path = converted.get("manifest_path")
    require(isinstance(manifest_path, str), "conversion lacks source manifest path")
    manifest = source(conversion.parent, manifest_path)
    require(digest(manifest.read_bytes()) == converted["manifest_sha256"],
            "study manifest changed before freeze")
    study_spec = load(manifest)
    split_path = source(manifest.parent, study_spec["split_file"])
    require(digest(split_path.read_bytes()) == converted["split_sha256"], "split changed before freeze")
    require(digest(source(manifest.parent, study_spec["energy_file"]).read_bytes()) == converted["energy_sha256"],
            "energy table changed before freeze")
    require(not (split_path.parent / (".test-opened-" + converted["split_sha256"] + ".json")).exists(),
            "final test already opened for this split; no further native selection/freeze allowed")
    files = {}
    for key, name in (("lm_file", "native_LM.txt"), ("fit_report", "native_fit.txt"),
                      ("basis_file", "local_mode_PM.dat"), ("fit_log", "log.out")):
        path = source(handoff.parent, spec[key])
        raw = path.read_bytes()
        require(digest(raw) == checked["sources"][key]["sha256"], "native input changed during freeze")
        files[name] = raw
    receipt = {"scope": "native freeze before final evaluation; not proof of no raw-source bypass",
               "conversion": {"path": str(conversion), "sha256": digest(conversion.read_bytes())},
               "manifest": {"path": str(manifest), "sha256": digest(manifest.read_bytes())},
               "split_sha256": converted["split_sha256"], "basis_sha256": converted["basis_sha256"],
               "energy_offset": checked["energy_offset"], "handoff": checked}
    return write_package(Path(root).resolve(), files, "native-freeze.json", receipt)


def evaluate_frozen(freeze, root):
    """One final evaluation from frozen native bytes; never fits/selects a model."""
    from fit_handoff import parameters

    freeze = Path(freeze).resolve()
    receipt = load(freeze)
    verify(freeze.parent, freeze.name)
    for key in ("conversion", "manifest"):
        path = source(freeze.parent, receipt[key]["path"])
        require(digest(path.read_bytes()) == receipt[key]["sha256"], f"frozen {key} changed")
    conversion = load(receipt["conversion"]["path"])
    spec, base, targets, splits, provenance = study(receipt["manifest"]["path"])
    require(provenance["split_sha256"] == receipt["split_sha256"] and
            splits == conversion["splits"], "frozen split mismatch")
    require(provenance["energy_sha256"] == conversion["energy_sha256"], "energy table changed")
    split_path = source(base, spec["split_file"])
    write_package(split_path.parent, {}, ".test-opened-" + receipt["split_sha256"] + ".json",
                  {"freeze_sha256": digest(freeze.read_bytes()),
                   "split_sha256": receipt["split_sha256"],
                   "scope": "terminal test evaluation started; retained even if evaluation fails"})
    width, terms = parameters(freeze.parent / "native_LM.txt")
    require(width == conversion["feature_count"], "frozen model width mismatch")
    require(digest(source(base, spec["basis_file"]).read_bytes()) == receipt["basis_sha256"],
            "source basis changed since freeze")
    data = {}
    divisor = number(conversion["energy_divisor"])
    for sid in sorted(targets):
        evidence = conversion["samples"][str(sid)]
        feature = source(base, evidence["features"]["path"])
        require(digest(feature.read_bytes()) == evidence["features"]["sha256"],
                f"sample {sid}: features changed since conversion")
        values = features(feature)
        require(len(values) == width, f"sample {sid}: feature width mismatch")
        data[sid] = values + [number(targets[sid] / divisor)]
    files, metrics = {}, {}
    for name, ids in splits.items():
        rows = ["sample_id,target,prediction"]
        for sid in ids:
            values = data[sid]
            pred = number(math.fsum([receipt["energy_offset"]] +
                                   [coef * values[pid - 1] for pid, coef in terms.items()]))
            rows.append(f"{sid},{values[-1]:.16E},{pred:.16E}")
        raw = ("\n".join(rows) + "\n").encode()
        files[name + "_predictions.csv"] = raw
        metrics[name] = csv_metrics(raw, ids, {sid: data[sid][-1] for sid in data}, 1, 0)
    files["full-pristine-matrix.txt"] = ("".join(
        " ".join(f"{v:.16E}" for v in data[sid]) + "\n" for sid in sorted(data))).encode()
    files["full-row-ids.json"] = json_bytes(sorted(data))
    return write_package(Path(root).resolve(), files, "final-evaluation.json",
                         {"scope": "all-ID frozen native predictions; no post-test selection",
                          "freeze_sha256": digest(freeze.read_bytes()), "metrics": metrics,
                          "split_sha256": receipt["split_sha256"], "basis_sha256": receipt["basis_sha256"]})


def csv_metrics(data, ids, targets, scale, atol):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8")))
    require(reader.fieldnames == ["sample_id", "target", "prediction"], "CSV needs sample_id,target,prediction")
    seen, actual, errors = set(), [], []
    for row in reader:
        require(None not in row and None not in row.values(), "malformed CSV row")
        sid = int(row["sample_id"])
        require(sid in targets and sid not in seen, f"unexpected/duplicate CSV id: {sid}")
        y, prediction = number(row["target"]), number(row["prediction"])
        expected = number(targets[sid] * scale)
        require(abs(y - expected) <= atol, f"target/units mismatch: {sid}")
        seen.add(sid)
        actual.append(y)
        errors.append(number(prediction - y))
    require(seen == set(ids), "CSV ids do not match the frozen split")
    n = len(actual)
    mse = number(math.fsum((e * e) / n for e in errors))
    mean = number(math.fsum(y / n for y in actual))
    variance = number(math.fsum(((y - mean) ** 2) / n for y in actual))
    return {"count": n, "rmse": math.sqrt(mse), "mae": number(math.fsum(abs(e) / n for e in errors)),
            "r2": number(1 - mse / variance) if variance else None}


def publish(manifest, root, receipt_name):
    spec, base, targets, splits, provenance = study(manifest)
    scale, atol = number(spec["target_scale"]), number(spec["target_atol"])
    require(scale > 0 and atol >= 0, "positive target_scale and nonnegative target_atol required")
    require(set(spec["csv_paths"]) == set(SPLITS), "csv_paths must name all three splits")
    require(len(set(spec["csv_paths"].values())) == len(SPLITS), "split CSV paths must differ")
    files = {name: source(base, path).read_bytes() for name, path in spec["artifacts"].items()}
    model_names = spec.get("model_manifest")
    if model_names is None:
        model_names = [name for name in files
                       if Path(name).name in ("fgt-model.json", "model.json")]
    elif isinstance(model_names, str):
        model_names = [model_names]
    require(isinstance(model_names, list), "model_manifest must be a path or list of paths")
    for name in model_names:
        require(name in files, f"model manifest is not published: {name}")
        validate_model_manifest(files[name], name, base, files)
    if "native_freeze" in spec:
        frozen = source(base, spec["native_freeze"])
        freeze_record = load(frozen)
        verify(frozen.parent, frozen.name)
        evaluated = source(base, spec["final_evaluation"])
        evaluation = load(evaluated)
        verify(evaluated.parent, evaluated.name)
        require(evaluation["freeze_sha256"] == digest(frozen.read_bytes()),
                "evaluation belongs to another native freeze")
        require(freeze_record["split_sha256"] == provenance["split_sha256"], "publication split changed")
        for name, expected in freeze_record["sha256"].items():
            require(name in files and digest(files[name]) == expected,
                    f"publication omits/changes frozen native artifact: {name}")
        for name, expected in evaluation["sha256"].items():
            require(name in files and digest(files[name]) == expected,
                    f"publication omits/changes frozen evaluation artifact: {name}")
    # The controller consumes a declared set of files from the publication root.
    # Requiring this declaration catches nested-run handoffs before a receipt can
    # make an incomplete delivery look complete.
    root_artifacts = spec.get("root_artifacts")
    require(isinstance(root_artifacts, list) and bool(root_artifacts),
            "root_artifacts must declare required consumer-root files")
    require(all(isinstance(name, str) and name in files and
                Path(name).parent == Path(".") for name in root_artifacts),
            "root_artifacts must name existing top-level published files")
    require(len(set(root_artifacts)) == len(root_artifacts),
            "root_artifacts must not contain duplicates")
    metrics = {name: csv_metrics(files[path], splits[name], targets, scale, atol)
               for name, path in spec["csv_paths"].items()}
    # Explicit JSON pointer checks keep consumer paths valid after publication.
    # Paths are interpreted relative to the publication root, not the run directory.
    for ref in spec.get("references", []):
        obj = json.loads(files[ref["artifact"]])
        for key in ref["keys"]:
            obj = obj[key]
        require(isinstance(obj, str) and obj in files, f"unpublished consumer path: {obj}")
    receipt = {"scope": "published bytes, full-ID coverage, targets and metrics only; not scientific acceptance",
               **provenance, "target_scale": scale, "target_atol": atol,
               "csv_paths": spec["csv_paths"], "metrics": metrics}
    return write_package(Path(root).resolve(), files, receipt_name, receipt)


def verify(root, receipt_name):
    root = Path(root).resolve()
    receipt = load(destination(root, receipt_name))
    require(bool(receipt["sha256"]), "empty receipt")
    for name, expected in receipt["sha256"].items():
        require(digest(destination(root, name).read_bytes()) == expected, f"artifact changed: {name}")
    return {"scope": "byte identity to receipt only", "count": len(receipt["sha256"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("freeze-native")
    p.add_argument("--conversion", required=True, type=Path)
    p.add_argument("--handoff", required=True, type=Path)
    p.add_argument("--root", required=True, type=Path)
    p = sub.add_parser("evaluate-frozen")
    p.add_argument("--freeze", required=True, type=Path)
    p.add_argument("--root", required=True, type=Path)
    for command in ("convert", "publish", "verify"):
        p = sub.add_parser(command)
        p.add_argument("--root", required=True, type=Path, help="explicit output/consumer directory")
        if command != "verify":
            p.add_argument("--manifest", required=True, type=Path)
        if command != "convert":
            p.add_argument("--receipt", required=True, help="relative path outside the reviewed report")
    args = parser.parse_args()
    if args.command == "freeze-native":
        result = freeze_native(args.conversion, args.handoff, args.root)
    elif args.command == "evaluate-frozen":
        result = evaluate_frozen(args.freeze, args.root)
    elif args.command == "convert":
        result = convert(args.manifest, args.root)
    elif args.command == "publish":
        result = publish(args.manifest, args.root, args.receipt)
    else:
        result = verify(args.root, args.receipt)
    print(json.dumps({k: v for k, v in result.items() if k not in ("samples", "splits", "sha256")}, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, IndexError, OverflowError, csv.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
