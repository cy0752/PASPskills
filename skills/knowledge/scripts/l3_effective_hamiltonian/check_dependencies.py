#!/usr/bin/env python3
"""Hash-bound train/selection affine dependency audit; no fit or PASP launch."""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from study_contract import digest, identifier, json_bytes, load, number, require, write_package


def _read(path):
    rows = [[number(v) for v in line.split()]
            for line in Path(path).read_text().splitlines() if line.strip()]
    require(rows and len(rows[0]) >= 2 and all(len(r) == len(rows[0]) for r in rows),
            f'empty/ragged feature+target matrix: {path}')
    return rows


def _dot(a, b):
    return math.fsum(x * y for x, y in zip(a, b))


def _norm(a):
    return math.sqrt(_dot(a, a))


def _orthogonal_residual(basis, vector):
    """Two-pass modified Gram-Schmidt, retaining projections for replay."""
    residual = list(vector)
    coefficients = [0.0] * len(basis)
    for _ in range(2):
        for index, q in enumerate(basis):
            coefficient = _dot(q, residual)
            coefficients[index] += coefficient
            residual = [x - coefficient * y for x, y in zip(residual, q)]
    return residual, coefficients


def _backsolve(triangle, rhs):
    result = [0.0] * len(rhs)
    for i in reversed(range(len(rhs))):
        result[i] = (rhs[i] - math.fsum(triangle[j][i] * result[j]
                                       for j in range(i + 1, len(rhs)))) / triangle[i][i]
    return result


def audit(train_path, selection_path, rtol, atol):
    rtol, atol = number(rtol), number(atol)
    require(rtol >= 0 and atol >= 0 and rtol + atol > 0,
            'finite nonnegative tolerances with a positive total required')
    train, selection = _read(train_path), _read(selection_path)
    require(len(train[0]) == len(selection[0]), 'train/selection feature widths differ')
    rows, width = train + selection, len(train[0]) - 1
    columns = [[r[i] for r in rows] for i in range(width)]
    # Separate offset is always retained; constants cannot cause a NaN correlation.
    length = math.sqrt(len(rows))
    basis, triangle = [[1 / length] * len(rows)], [[length]]
    kept, scales, dependent, pivots = [], [1.0], [], []
    for index, column in enumerate(columns):
        scale = max(abs(v) for v in column) or 1.0
        scaled = [v / scale for v in column]
        residual, projections = _orthogonal_residual(basis, scaled)
        tolerance = atol + rtol * scale
        maximum = max(abs(v * scale) for v in residual)
        if maximum > tolerance:
            norm = _norm(residual)
            require(norm > 0, 'unstable orthogonal residual')
            triangle.append(projections + [norm])
            basis.append([v / norm for v in residual])
            kept.append(index + 1)
            scales.append(scale)
            pivots.append(norm / _norm(scaled))
            continue
        weights = _backsolve(triangle, projections)
        intercept = weights[0] * scale
        terms = [{'column': k, 'coefficient': weights[i + 1] * scale / scales[i + 1]}
                 for i, k in enumerate(kept) if weights[i + 1] != 0.0]
        replay = [intercept + math.fsum(t['coefficient'] * columns[t['column'] - 1][r]
                                       for t in terms) for r in range(len(rows))]
        replay_error = max(abs(a - b) for a, b in zip(column, replay))
        # A numerically unstable relation is retained, never silently skipped.
        if replay_error > tolerance:
            norm = _norm(residual)
            require(norm > 0, 'unstable zero residual during replay')
            triangle.append(projections + [norm])
            basis.append([v / norm for v in residual])
            kept.append(index + 1)
            scales.append(scale)
            pivots.append(norm / _norm(scaled))
            continue
        dependent.append({'column': index + 1, 'kind': 'affine_linear_combination',
                          'intercept': intercept, 'terms': terms,
                          'max_residual': replay_error, 'tolerance': tolerance})
    skip = [str(len(dependent))] + [f"{i} {r['column']}" for i, r in enumerate(dependent, 1)]
    return {'scope': 'complete train+selection affine dependencies; energy target excluded',
            'train_rows': len(train), 'selection_rows': len(selection), 'rows_total': len(rows),
            'feature_width': width, 'kept_columns': kept, 'kept_count': len(kept),
            'dependent_columns': dependent, 'rank_with_offset': len(kept) + 1,
            'normalized_independence_pivots': pivots,
            'rtol': rtol, 'atol': atol, 'skip_text': '\n'.join(skip) + '\n',
            'not_covered': ['physical equivalence or zero interactions', 'infinite-lattice aliasing',
                            'exact spectral condition number', 'native reductions/skip activation',
                            'accuracy', 'unlogged test access']}


def prepare(conversion, root, rtol, atol):
    conversion, root = Path(conversion).resolve(), Path(root).absolute()
    require(not root.exists(), 'use a new audit root; preserve previous attempts')
    receipt = load(conversion)
    paths, hashes, row_ids = {}, {}, {}
    for name in ('train', 'selection'):
        for suffix in ('.txt', '.ids.json'):
            filename = name + suffix
            path = conversion.parent / filename
            require(path.is_file() and not path.is_symlink(), f'missing/aliased converted artifact: {filename}')
            hashes[filename] = digest(path.read_bytes())
            require(hashes[filename] == receipt['sha256'][filename], f'conversion artifact changed: {filename}')
        ids = load(conversion.parent / (name + '.ids.json'))
        require(ids == receipt['splits'][name] and ids and all(identifier(i) >= 0 for i in ids),
                f'row identities differ from conversion: {name}')
        row_ids[name] = ids
        paths[name] = conversion.parent / (name + '.txt')
    all_ids = row_ids['train'] + row_ids['selection']
    require(len(all_ids) == len(set(all_ids)) and not set(all_ids) & set(receipt['splits']['test']),
            'train/selection duplicate or held-out test leakage')
    result = audit(paths['train'], paths['selection'], rtol, atol)
    require(result['feature_width'] == receipt['feature_count'] and
            result['train_rows'] == len(row_ids['train']) and
            result['selection_rows'] == len(row_ids['selection']), 'conversion dimensions differ')
    skip = result.pop('skip_text').encode()
    result.update(conversion_sha256=digest(conversion.read_bytes()),
                  basis_sha256=receipt['basis_sha256'], split_sha256=receipt['split_sha256'],
                  input_sha256=hashes, row_ids=row_ids,
                  original_columns=list(range(1, result['feature_width'] + 1)),
                  skip_numbering='pristine original columns; compose native reduction maps before use')
    return write_package(root, {'Fitting_Set_Term_Skip.txt': skip}, 'dependency-audit.json', result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--conversion', type=Path, required=True)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--rtol', type=float, required=True)
    parser.add_argument('--atol', type=float, required=True)
    args = parser.parse_args()
    print(json_bytes(prepare(args.conversion, args.root, args.rtol, args.atol)).decode(), end='')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
        raise SystemExit(f'error: {exc}')
