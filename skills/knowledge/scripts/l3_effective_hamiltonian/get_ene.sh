#!/bin/bash
set -euo pipefail

num_of_primitive_cell="${1:-9}"

printf '%s\n' "$num_of_primitive_cell" > Energy.dat

shopt -s nullglob

count=0
for outcar_path in [0-9]*/OUTCAR; do
    dirname=$(dirname "${outcar_path}")
    sample_id=$(basename "${dirname}")
    E=$(grep "TOTEN" "${outcar_path}" | tail -1 | awk '{printf "%20.8f\n",$5}')
    printf '%s %s\n' "${sample_id}" "${E}" >> Energy.dat
    count=$((count + 1))
done

if ((count == 0)); then
    for outcar_path in [0-9]*.OUTCAR; do
        filename=$(basename "${outcar_path}")
        sample_id="${filename%.OUTCAR}"
        E=$(grep "TOTEN" "${outcar_path}" | tail -1 | awk '{printf "%20.8f\n",$5}')
        printf '%s %s\n' "${sample_id}" "${E}" >> Energy.dat
        count=$((count + 1))
    done
fi

if ((count == 0)); then
    printf 'No numbered sample directories or flat <id>.OUTCAR files were found.\n' >&2
    exit 1
fi

printf 'Wrote Energy.dat for %d samples\n' "${count}"
