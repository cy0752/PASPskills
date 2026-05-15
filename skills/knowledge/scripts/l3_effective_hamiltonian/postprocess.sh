#!/bin/bash
set -euo pipefail

mkdir -p ene_symbol vasp_MAGMOM

source_dir="${1:-input}"

rm -f ene_symbol/*.ene_symbol vasp_MAGMOM/*.vasp_MAGMOM

shopt -s nullglob

count=0
for ene_path in "${source_dir}"/*.ene_symbol; do
    sample_id=$(basename "${ene_path}" .ene_symbol)
    magmom_path="${source_dir}/${sample_id}.vasp_MAGMOM"

    if [[ ! -f "${magmom_path}" ]]; then
        printf 'Missing paired file: %s\n' "${magmom_path}" >&2
        exit 1
    fi

    cp "${ene_path}" "ene_symbol/${sample_id}.ene_symbol"
    cp "${magmom_path}" "vasp_MAGMOM/${sample_id}.vasp_MAGMOM"
    count=$((count + 1))
done

if ((count == 0)); then
    printf 'No *.ene_symbol files found in %s\n' "${source_dir}" >&2
    exit 1
fi

printf 'Copied %d sample pairs from %s\n' "${count}" "${source_dir}"
