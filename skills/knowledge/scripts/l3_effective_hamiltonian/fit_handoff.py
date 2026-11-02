#!/usr/bin/env python3
"""Check native PASP LM parameters against pristine features and fit predictions."""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import re
import sys

from study_contract import digest, json_bytes, load, number, records, require, source, write_package
from fit_limits import check_candidate_width, check_retained_count


def parameters(path):
    lines = path.read_text().splitlines()
    require(all(line.strip() and "#" not in line and "!" not in line for line in lines),
            "LM/J_best must not contain blank records or comments")
    rows = [line.split() for line in lines]
    require(bool(rows) and len(rows[0]) == 2, "LM/J_best header must be nfeatures nkept")
    width, count = map(int, rows[0])
    require(width > 0 and 0 <= count <= width and len(rows) == count + 1,
            "invalid LM/J_best counts")
    terms = {}
    for row in rows[1:]:
        require(len(row) == 2, "parameter row must be id value")
        pid = int(row[0])
        require(1 <= pid <= width and pid not in terms, "invalid/duplicate physical parameter id")
        terms[pid] = number(row[1])
        require(terms[pid] != 0, "zero parameter must not be a retained row")
    return width, terms


def physical_report(path):
    text = path.read_text()
    lines = text.splitlines()
    require(bool(lines), "empty fit report")
    count = int(lines[0].split()[0])
    require(count > 0 and len(lines) > count, "invalid fit report term count")
    ids = []
    for ordinal, line in enumerate(lines[1:count + 1], 1):
        row = line.split()
        require(len(row) == 2 and int(row[0]) == ordinal, "invalid physical term table")
        ids.append(int(row[1]))
    require(all(pid >= 0 for pid in ids) and len(set(ids)) == count, "invalid physical term ids")
    coefficients = re.findall(r"B\(\s*(\d+)\s*\)\s*=\s*([-+\d.eEdD]+)", text)
    require([int(i) for i, _ in coefficients] == list(range(1, count + 1)),
            "fit report needs exactly one ordered B coefficient per physical term")
    return dict(zip(ids, (number(v) for _, v in coefficients)))


def check(manifest):
    manifest = Path(manifest).resolve()
    spec = load(manifest)
    base = manifest.parent
    paths = {key: source(base, spec[key]) for key in ("basis_file", "lm_file", "fit_report")}
    width, terms = parameters(paths["lm_file"])
    if "fit_log" in spec:
        paths["fit_log"] = source(base, spec["fit_log"])
        log = paths["fit_log"].read_text(errors="replace")
        require(not re.search(r'forrtl:|SIGSEGV|SIGABRT|MPI_ABORT|^\s*(ERROR|FATAL)\b', log, re.I | re.M),
                'native fit failure diagnostic')
        dimensions = re.findall(r"Nn,Nd:\s+(\d+)\s+(\d+)", log)
        require(dimensions, 'fit log lacks native dimensions')
        widths = [int(nd) for _, nd in dimensions]
        if "NEED TO REWRITE DATA" in log:
            require(widths[0] == width and all(0 < nd <= width for nd in widths),
                    'rewrote data: dimensions do not start at pristine native width')
            mappings = spec.get('rewrite_mappings')
            require(isinstance(mappings, list) and mappings, 'rewrote data without preserved native mappings')
            current = width
            original_ids = list(range(1, width + 1))
            for ordinal, name in enumerate(mappings):
                path = source(base, name)
                require(path.parent == paths['fit_log'].parent and path.name ==
                        f'Data_Variables_Mapping_(1st Reducing)_{current}.txt',
                        'mapping must be from actual fit run and current native width')
                rows = [re.fullmatch(r'\s*(\d+)\s*:\s*(\d+)\s*', line)
                        for line in path.read_text().splitlines()]
                require(rows and all(rows), 'unsupported native rewrite mapping')
                pairs = [(int(m[1]), int(m[2])) for m in rows]
                ids = [i for _, i in pairs]
                require([i for i, _ in pairs] == list(range(1, len(rows) + 1)) and
                        len(set(ids)) == len(ids) and all(1 <= i <= current for i in ids),
                        'invalid native reduced-to-original mapping')
                original_ids = [original_ids[i - 1] for i in ids]
                current = len(rows)
                paths[f'rewrite_mapping_{ordinal}'] = path
            require(current == widths[-1] and set(terms) <= set(original_ids),
                    'rewrite mapping differs from final width/original exported IDs')
            require('fit_exit_code_file' in spec, 'rewritten fit needs native exit evidence')
        else:
            require(all(nd == width for nd in widths), 'fit log width does not match native LM')
        require("FITTING FINISHED" in log and "PASP is finished gracefully" in log,
                "fit log lacks native completion evidence")
    if "fit_exit_code_file" in spec:
        paths["fit_exit_code_file"] = source(base, spec["fit_exit_code_file"])
        require(paths["fit_exit_code_file"].read_text().strip() == "0",
                "native fit exit code is not zero")
    basis_ids = [int(match.group(1)) for match in re.finditer(
        r"^\s*\d+\s+(\d+)\s+.*#ipara,ipara_gb,power,n,nmode,im_read,lonebody\s*$",
        paths["basis_file"].read_text(), re.MULTILINE | re.IGNORECASE)]
    require(sorted(basis_ids) == list(range(1, width + 1)),
            "unsupported/mismatched basis: need unique ipara_gb 1..nfeatures")
    atol = number(spec["prediction_atol"])
    coeff_atol = number(spec["coefficient_atol"])
    require(atol >= 0 and coeff_atol >= 0, "tolerances must be nonnegative")
    coefficient_abs_limit = spec.get("coefficient_abs_limit")
    if coefficient_abs_limit is not None:
        coefficient_abs_limit = number(coefficient_abs_limit)
        require(coefficient_abs_limit > 0, "coefficient_abs_limit must be positive")
    report = physical_report(paths["fit_report"])
    offset = report.pop(0, 0.0)
    # Use the physical table, not internal XM indices (which include the intercept).
    report = {pid: value for pid, value in report.items() if value != 0}
    require(set(report) == set(terms), "LM terms differ from fit report physical ids")
    require(all(abs(report[pid] - terms[pid]) <= coeff_atol for pid in terms),
            "LM coefficients differ from selected fit report")
    max_abs_coefficient = max((abs(value) for value in terms.values()), default=0.0)
    if coefficient_abs_limit is not None:
        require(max_abs_coefficient <= coefficient_abs_limit,
                "retained coefficient scale exceeds coefficient_abs_limit; reject unstable cancelling fit")
    if "j_file" in spec:
        paths["j_file"] = source(base, spec["j_file"])
        j_width, j_terms = parameters(paths["j_file"])
        require(j_width == width and set(j_terms) == set(terms),
                "J_best differs from native LM physical ids (constant/XM shift suspected)")
        require(all(abs(j_terms[pid] - terms[pid]) <= coeff_atol for pid in terms),
                "J_best coefficients differ from native LM")
    datasets = spec["datasets"]
    require(isinstance(datasets, list) and len(datasets) == 2 and
            {d["name"] for d in datasets} == {"train", "selection"},
            "handoff needs train and selection only; do not access final test here")
    results = {}
    train_point_count = None
    for dataset in datasets:
        name = dataset["name"]
        matrix = source(base, dataset["matrix"])
        predictions = source(base, dataset["predictions"])
        paths[name + "_matrix"] = matrix
        paths[name + "_predictions"] = predictions
        data, predicted = records(matrix), records(predictions)
        require(bool(data) and len(data) == len(predicted), f"{name}: row count mismatch")
        if name == "train":
            train_point_count = len(data)
        deviations = []
        for ordinal, (row, prow) in enumerate(zip(data, predicted), 1):
            require(len(row) == width + 1, f"{name}: need pristine full-basis feature matrix")
            require(len(prow) == 5 and int(prow[0]) == ordinal,
                    f"{name}: unsupported PASP prediction row/order")
            values = [number(v) for v in row]
            target, estimate, _, _ = (number(v) for v in prow[1:])
            require(abs(values[-1] - target) <= atol, f"{name}: target/row identity mismatch")
            recovered = math.fsum([offset] + [terms[pid] * values[pid - 1] for pid in terms])
            require(math.isfinite(recovered), f"{name}: nonfinite reconstruction")
            deviations.append(abs(recovered - estimate))
        require(max(deviations) <= atol,
                f"{name}: exported model fails prediction round-trip (max error {max(deviations):.6g})")
        results[name] = {"count": len(data), "max_abs_prediction_difference": max(deviations)}
    require(train_point_count is not None, "handoff needs train data")
    width_gate = check_candidate_width(width, train_point_count)
    retained_gate = check_retained_count(len(terms), train_point_count)
    return {"scope": "physical parameter and prediction round-trip; not scientific acceptance",
            "manifest_sha256": digest(manifest.read_bytes()), "feature_count": width,
            "retained_count": len(terms), "energy_offset": offset,
            "fitting_data_point_count": train_point_count,
            "candidate_feature_limit": width_gate["candidate_feature_limit"],
            "retained_parameter_limit": retained_gate["retained_limit"],
            "max_abs_coefficient": max_abs_coefficient,
            "coefficient_abs_limit": coefficient_abs_limit,
            "prediction_atol": atol, "coefficient_atol": coeff_atol, "datasets": results,
            "sources": {k: {"path": str(p), "sha256": digest(p.read_bytes())} for k, p in paths.items()}}, paths["lm_file"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, help="Optional NEW candidate export directory")
    args = parser.parse_args()
    try:
        receipt, lm = check(args.manifest)
        if args.root:
            receipt = write_package(args.root.resolve(), {"J_best.dat": lm.read_bytes()},
                                    "fit-handoff.json", receipt)
        print(json_bytes(receipt).decode(), end="")
        return 0
    except (ValueError, OSError, KeyError, TypeError, IndexError, OverflowError) as exc:
        print(f"fit-handoff: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
