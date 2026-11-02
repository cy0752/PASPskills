#!/usr/bin/env python3
"""Read-only JSON delivery contract, file integrity and container-repair checks.

Standard library only. This is a deliberately small contract language, NOT full
JSON Schema. No PASP model, material names, task interface or scientific defaults
are built in. Derive the contract and expected keys from the current user request
and independently enumerated source inventory. See l2_four_state_delivery.md.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError(f"non-finite JSON number: {value}")

    result = json.loads(Path(path).read_text(), object_pairs_hook=pairs, parse_constant=invalid)
    canonical(result)  # Also reject overflow such as 1e999.
    return result


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inside(root, value):
    if not isinstance(value, str) or not value:
        raise ValueError("path must be a nonempty string")
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"path escapes artifact root: {value}")
    return path


TYPES = {
    "object": lambda x: isinstance(x, dict),
    "array": lambda x: isinstance(x, list),
    "string": lambda x: isinstance(x, str),
    "integer": lambda x: type(x) is int,
    "number": lambda x: type(x) is int or (type(x) is float and math.isfinite(x)),
    "boolean": lambda x: type(x) is bool,
    "null": lambda x: x is None,
}
KEYS = {"type", "required", "properties", "items", "uniqueBy", "expectedKeys",
        "pathKind", "const", "minItems"}


def check_schema(schema):
    if not isinstance(schema, dict) or set(schema) - KEYS:
        raise ValueError("unsupported contract; allowed keys: " + ", ".join(sorted(KEYS)))
    kind = schema.get("type")
    if kind not in TYPES:
        raise ValueError("every contract node needs a supported type")
    for key in ("required", "properties"):
        if key in schema and kind != "object":
            raise ValueError(f"{key} requires object type")
    required = schema.get("required", [])
    props = schema.get("properties", {})
    if not isinstance(required, list) or any(not isinstance(k, str) for k in required):
        raise ValueError("required must be an array of field names")
    if not isinstance(props, dict) or set(required) - set(props):
        raise ValueError("every required field needs a properties contract")
    for child in props.values():
        check_schema(child)
    for key in ("items", "uniqueBy", "expectedKeys", "minItems"):
        if key in schema and kind != "array":
            raise ValueError(f"{key} requires array type")
    if kind == "array":
        check_schema(schema.get("items"))
    if "minItems" in schema and (type(schema["minItems"]) is not int or schema["minItems"] < 0):
        raise ValueError("minItems must be a nonnegative integer")
    if "uniqueBy" in schema:
        fields = schema["uniqueBy"]
        if not isinstance(fields, list) or any(not isinstance(k, str) for k in fields):
            raise ValueError("uniqueBy must be an array of field names; [] means whole item")
    if "expectedKeys" in schema:
        if "uniqueBy" not in schema or not isinstance(schema["expectedKeys"], list):
            raise ValueError("expectedKeys requires uniqueBy and an array of keys")
        expected = schema["expectedKeys"]
        fields = schema["uniqueBy"]
        if fields and any(not isinstance(k, list) or len(k) != len(fields) for k in expected):
            raise ValueError("expectedKeys entries must match the uniqueBy tuple width")
        if len({canonical(k) for k in expected}) != len(expected):
            raise ValueError("duplicate expected inventory keys")
    if "pathKind" in schema and (kind != "string" or schema["pathKind"] not in ("file", "directory")):
        raise ValueError("pathKind requires string type and file or directory")


def validate(value, schema, root, where="$", errors=None):
    if errors is None:
        errors = []
    kind = schema["type"]
    if not TYPES[kind](value):
        errors.append(f"{where}: expected {kind}, got {type(value).__name__}")
        return errors
    if "const" in schema and canonical(value) != canonical(schema["const"]):
        errors.append(f"{where}: differs from required constant")
    if kind == "object":
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{where}: missing {key}")
        for key, child in schema.get("properties", {}).items():
            if key in value:
                validate(value[key], child, root, where + "/" + key, errors)
    if kind == "array":
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{where}: too few items")
        for index, item in enumerate(value):
            validate(item, schema["items"], root, f"{where}/{index}", errors)
        if "uniqueBy" in schema:
            fields = schema["uniqueBy"]
            try:
                keys = [canonical([item[k] for k in fields] if fields else item) for item in value]
                if len(set(keys)) != len(keys):
                    errors.append(f"{where}: duplicate inventory key")
                if "expectedKeys" in schema:
                    expected = {canonical(k) for k in schema["expectedKeys"]}
                    missing, extra = expected - set(keys), set(keys) - expected
                    if missing or extra:
                        errors.append(f"{where}: missing keys {sorted(missing)}; extra keys {sorted(extra)}")
            except (KeyError, TypeError):
                errors.append(f"{where}: missing identity fields {fields}")
    if "pathKind" in schema:
        try:
            path = inside(root, value)
            if schema["pathKind"] == "file":
                if not path.is_file() or path.stat().st_size == 0:
                    raise ValueError("missing or empty file")
            elif not path.is_dir():
                raise ValueError("missing directory")
        except (ValueError, OSError) as exc:
            errors.append(f"{where}: {exc}")
    return errors


def normalized(value, pointer, identity):
    """Normalize exactly one object/array container; preserve every other leaf."""
    result = copy.deepcopy(value)
    if not pointer.startswith("/"):
        raise ValueError("array-repair must be a JSON pointer followed by :identity_field")
    parts = [p.replace("~1", "/").replace("~0", "~") for p in pointer[1:].split("/")]
    parent = result
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
    container = parent[key]
    if isinstance(container, dict):
        items = list(container.values())
        if any(not isinstance(v, dict) or v.get(identity) != k for k, v in container.items()):
            raise ValueError("object keys disagree with identity fields")
    elif isinstance(container, list):
        items = container
    else:
        raise ValueError("repair target must be object or array")
    mapped = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get(identity), str):
            raise ValueError("repair items need string identity fields")
        name = item[identity]
        if name in mapped:
            raise ValueError("duplicate identity in repair target")
        mapped[name] = item
    parent[key] = mapped
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("delivery", type=Path)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--root", type=Path, required=True, help="artifact workspace; relative paths resolve here")
    parser.add_argument("--hashes", type=Path, help="previously saved JSON mapping of artifact paths to SHA256")
    parser.add_argument("--previous", type=Path, help="pre-repair delivery; compare all leaves")
    parser.add_argument("--array-repair", help="only permitted normalization, e.g. /systems:name")
    args = parser.parse_args()
    errors, checks, receipts = [], [], {}
    try:
        root = args.root.resolve()
        schema, value = load(args.contract), load(args.delivery)
        check_schema(schema)
        errors.extend(validate(value, schema, root))
        checks.append("contract types, required fields, configured inventory and paths")
        receipts = {"delivery_sha256": digest(args.delivery), "contract_sha256": digest(args.contract)}
        if args.hashes:
            hashes = load(args.hashes)
            if not isinstance(hashes, dict) or not hashes:
                raise ValueError("hash manifest must be a nonempty object")
            receipts["manifest_sha256"] = digest(args.hashes)
            for name, expected in hashes.items():
                if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
                    raise ValueError(f"invalid SHA256 for {name}")
                if digest(inside(root, name)) != expected:
                    errors.append(f"{name}: changed since hash checkpoint")
            checks.append(f"{len(hashes)} artifact hashes")
        if args.array_repair and not args.previous:
            raise ValueError("array-repair requires previous delivery")
        if args.previous:
            before, after = load(args.previous), value
            receipts["previous_sha256"] = digest(args.previous)
            if args.array_repair:
                pointer, identity = args.array_repair.rsplit(":", 1)
                before = normalized(before, pointer, identity)
                after = normalized(after, pointer, identity)
            if canonical(before) != canonical(after):
                errors.append("delivery content changed beyond the permitted container normalization")
            checks.append("all delivery leaves compared with previous")
    except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        errors.append(str(exc))
    print(json.dumps({"status": "fail" if errors else "pass", "errors": errors,
                      "checks": checks, "receipts": receipts,
                      "scope": "configured mechanical checks only; no scientific or PASP runtime verdict"}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
