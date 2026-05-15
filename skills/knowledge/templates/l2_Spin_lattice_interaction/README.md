# Template: `l2_Spin_lattice_interaction`

Lecture-2 NiI2 `Model Spin_lattice_interaction` input package.

Files:
- `PASP.input`
- `MC.input`
- `cell.str`
- `unit_cell.str`
- `spin_exchange.dat`
- `seed.in`
- `run.sh`

Use this only as a starting template. Before running:
- confirm the physical source of `spin_exchange.dat`;
- confirm `SuperCell` is large enough for the target magnetic period;
- set `PT.M` to an integer multiple of the MPI rank count;
- decide whether `spin_lat.relax_str` should be `T` or `F`.

Observed on 2026-05-10: the NiI2 template with `spin_lat.relax_str T` completed PTMC and wrote `spin3_lowest.out`, but then hit `SIGSEGV` in the CG / post-processing path. For a first reproducible handoff to `magnon`, use `spin_lat.relax_str F` unless the user explicitly wants CG testing.

