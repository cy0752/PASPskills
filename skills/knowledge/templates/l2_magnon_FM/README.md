# Template: `l2_magnon_FM`

Lecture-2 NiI2 ferromagnetic `Model magnon` input package.

Files:
- `PASP.input`
- `cell.str`
- `unit_cell.str`
- `spin_exchange.dat`
- `spin3.in`
- `run.sh`

Preflight:
- `spin_exchange.dat` fourth-order count must be `0`;
- `spin3.in` non-empty data-row count must equal `det(SuperCell) × NumberOfAtoms_in_cell.str`;
- q-path endpoints in `run.sh` must match the user's requested path.

Observed on 2026-05-10: this template ran to `PASP is finished gracefully` and produced `spin_wave_E.dat` plus `spin_wave_H_wf.dat`.
