#!/usr/bin/env bash
PASP_PATH="/data/app/sh2025/pasp/bin/PASP.x"
Gamma="0.0 0.0 0.0"
M="0.5 0.0 0.0"
X="0.6666666667 -0.3333333333 0.0"

modify_qpoints() {
    local qpoints="$1"
    line_a=$(grep -n "%block qpoints.magnon" PASP.input | cut -d: -f1)
    line_b=$(grep -n "%endblock qpoints.magnon" PASP.input | cut -d: -f1)

    sed -i "${line_a},${line_b}d" PASP.input
    sed -i "$((line_a - 1))a\\%block qpoints.magnon\n${qpoints}\n%endblock qpoints.magnon" PASP.input
}

modify_qpoints "$Gamma\n$M"
$PASP_PATH >log.out
cat "spin_wave_E.dat" >"spin_wave_E_all.dat"
# delete last line to avoid duplication
sed -i '$d' "spin_wave_E_all.dat"

modify_qpoints "$M\n$X"
$PASP_PATH >>log.out
cat "spin_wave_E.dat" >>"spin_wave_E_all.dat"
# delete last line to avoid duplication
sed -i '$d' "spin_wave_E_all.dat"

modify_qpoints "$X\n$Gamma"
$PASP_PATH >>log.out
cat "spin_wave_E.dat" >>"spin_wave_E_all.dat"

echo "Spin wave calculation completed. Results are in spin_wave_E_all.dat"

