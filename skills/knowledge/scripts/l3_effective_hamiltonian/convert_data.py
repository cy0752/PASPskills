#!/usr/bin/env python3
"""Convert L3 ene_symbol and Energy.dat files into PASP fitting datasets.

This is a no-compiler replacement for the example-derived convert_data.f90.
It keeps the default contract used by the L3 all_data example:

- convert_info.txt line 1: number of training samples
- convert_info.txt line 2: number of prediction/test samples
- convert_info.txt line 3: number of primitive cells contained in each DFT supercell,
  used to normalize energies. This is NOT the number of atoms in the primitive cell.
- ene_symbol/<id>.ene_symbol: consecutive sample feature files
- Energy.dat: one ignored header line, then "<id> <energy>" records

When generating convert_info.txt for L3, the skill default is a 90/10 split
over the available consecutive samples unless the user specifies otherwise:
Ntrain=floor(0.9*N), Ntest=N-Ntrain.

By default, sample ids 1..Ntrain are written to Fitting_Dataset.txt and
sample ids Ntrain+1..Ntrain+Npredict are written to
Fitting_Data_for_prediction.txt.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable


def _first_data_token(line: str) -> str:
    """Return the first token before an inline comment."""
    return line.split("!", 1)[0].split("#", 1)[0].split()[0]


def _read_convert_info(path: Path) -> tuple[int, int, float]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3:
        raise ValueError(f"{path} must contain at least three lines")

    try:
        n_train = int(_first_data_token(lines[0]))
        n_predict = int(_first_data_token(lines[1]))
        energy_divisor = float(_first_data_token(lines[2]))
    except (IndexError, ValueError) as exc:
        raise ValueError(
            f"{path} must start with train count, prediction count, and energy divisor"
        ) from exc

    if n_train < 0 or n_predict < 0:
        raise ValueError("train and prediction counts must be non-negative")
    if energy_divisor == 0:
        raise ValueError("energy divisor must not be zero")

    return n_train, n_predict, energy_divisor


def _read_ene_symbol(path: Path) -> list[float]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError(f"{path} is empty")

    try:
        n_features = int(lines[0].split()[0])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"{path} first line must start with feature count") from exc

    values: list[float] = []
    for line_number, line in enumerate(lines[1:], start=2):
        stripped = line.strip()
        if not stripped:
            continue

        parts = stripped.split()
        if len(parts) < 2:
            raise ValueError(f"{path}:{line_number} must contain '<index> <value>'")

        try:
            values.append(float(parts[1]))
        except ValueError as exc:
            raise ValueError(f"{path}:{line_number} has non-numeric feature value") from exc

        if len(values) == n_features:
            break

    if len(values) != n_features:
        raise ValueError(f"{path} declares {n_features} features but contains {len(values)}")

    return values


def _read_energy_table(path: Path) -> dict[int, float]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError(f"{path} is empty")

    energies: dict[int, float] = {}
    for line_number, line in enumerate(lines[1:], start=2):
        stripped = line.strip()
        if not stripped:
            continue

        parts = stripped.split()
        if len(parts) < 2:
            raise ValueError(f"{path}:{line_number} must contain '<sample_id> <energy>'")

        try:
            sample_id = int(parts[0])
            energy = float(parts[1])
        except ValueError as exc:
            raise ValueError(f"{path}:{line_number} has invalid sample id or energy") from exc

        if sample_id in energies:
            raise ValueError(f"{path}:{line_number} duplicates sample id {sample_id}")
        energies[sample_id] = energy

    return energies


def _format_value(value: float, exponent: str) -> str:
    text = f"{value:.16E}"
    if exponent == "D":
        return text.replace("E", "D")
    return text


def _write_dataset(
    output_path: Path,
    sample_ids: Iterable[int],
    symbol_dir: Path,
    energies: dict[int, float],
    energy_divisor: float,
    *,
    divide_energy: bool,
    divide_symbols: bool,
    exponent: str,
) -> int:
    count = 0
    with output_path.open("w", encoding="utf-8") as output:
        for sample_id in sample_ids:
            symbol_path = symbol_dir / f"{sample_id}.ene_symbol"
            if not symbol_path.is_file():
                raise FileNotFoundError(f"missing ene_symbol file: {symbol_path}")
            if sample_id not in energies:
                raise KeyError(f"missing energy record for sample id {sample_id}")

            features = _read_ene_symbol(symbol_path)
            if divide_symbols:
                features = [value / energy_divisor for value in features]

            energy = energies[sample_id]
            if divide_energy:
                energy /= energy_divisor

            row = features + [energy]
            output.write(" ".join(_format_value(value, exponent) for value in row))
            output.write("\n")
            count += 1

    return count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert L3 ene_symbol and Energy.dat files into fitting datasets."
    )
    parser.add_argument(
        "--workdir",
        type=Path,
        default=Path("."),
        help="Directory containing convert_info.txt, Energy.dat, and ene_symbol/.",
    )
    parser.add_argument(
        "--start-id",
        type=int,
        default=1,
        help="First sample id for the training set. Default: 1.",
    )
    parser.add_argument(
        "--info-file",
        default="convert_info.txt",
        help="convert_info file name relative to workdir. Line 3 is the primitive-cell multiplicity of the DFT supercell, not primitive atom count.",
    )
    parser.add_argument(
        "--energy-file",
        default="Energy.dat",
        help="Energy table file name relative to workdir.",
    )
    parser.add_argument(
        "--symbol-dir",
        default="ene_symbol",
        help="ene_symbol directory name relative to workdir.",
    )
    parser.add_argument(
        "--train-output",
        default="Fitting_Dataset.txt",
        help="Training dataset output file name relative to workdir.",
    )
    parser.add_argument(
        "--prediction-output",
        default="Fitting_Data_for_prediction.txt",
        help="Prediction/test dataset output file name relative to workdir.",
    )
    parser.add_argument(
        "--no-energy-divide",
        action="store_true",
        help="Do not divide energies by the third line of convert_info.txt.",
    )
    parser.add_argument(
        "--symbol-divide",
        action="store_true",
        help="Also divide ene_symbol feature values by the third line of convert_info.txt.",
    )
    parser.add_argument(
        "--exponent",
        choices=("D", "E"),
        default="D",
        help="Floating-point exponent marker for output values. Default: D.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workdir = args.workdir.resolve()
    symbol_dir = workdir / args.symbol_dir

    if args.start_id < 0:
        raise ValueError("--start-id must be >= 0")
    if not symbol_dir.is_dir():
        raise FileNotFoundError(f"missing symbol directory: {symbol_dir}")

    n_train, n_predict, energy_divisor = _read_convert_info(workdir / args.info_file)
    energies = _read_energy_table(workdir / args.energy_file)

    train_start = args.start_id
    prediction_start = train_start + n_train
    train_ids = range(train_start, train_start + n_train)
    prediction_ids = range(prediction_start, prediction_start + n_predict)

    train_count = _write_dataset(
        workdir / args.train_output,
        train_ids,
        symbol_dir,
        energies,
        energy_divisor,
        divide_energy=not args.no_energy_divide,
        divide_symbols=args.symbol_divide,
        exponent=args.exponent,
    )
    prediction_count = _write_dataset(
        workdir / args.prediction_output,
        prediction_ids,
        symbol_dir,
        energies,
        energy_divisor,
        divide_energy=not args.no_energy_divide,
        divide_symbols=args.symbol_divide,
        exponent=args.exponent,
    )

    print(
        f"Wrote {train_count} rows to {args.train_output} and "
        f"{prediction_count} rows to {args.prediction_output}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
