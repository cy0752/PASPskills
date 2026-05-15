#!/bin/bash
set -euo pipefail

mkdir -p INCAR_all

source_dir="${1:-../0.generaterandomspin/vasp_MAGMOM}"
base_incar="${2:-INCAR}"

rm -f INCAR_all/INCAR_*

shopt -s nullglob

count=0
for magmom_path in "${source_dir}"/*.vasp_MAGMOM; do
    sample_id=$(basename "${magmom_path}" .vasp_MAGMOM)
    MAGMOMstr=$(grep 'MAGMOM' "${magmom_path}")
    M_CONSTRstr=${MAGMOMstr/"MAGMOM"/"M_CONSTR"}

    cp "${base_incar}" "INCAR_all/INCAR_${sample_id}"
    printf '%s\n' "${MAGMOMstr}" >> "INCAR_all/INCAR_${sample_id}"
    printf '%s\n' "${M_CONSTRstr}" >> "INCAR_all/INCAR_${sample_id}"
    count=$((count + 1))
done

if ((count == 0)); then
    printf 'No *.vasp_MAGMOM files found in %s\n' "${source_dir}" >&2
    exit 1
fi

printf 'Created %d INCAR files from %s\n' "${count}" "${source_dir}"
