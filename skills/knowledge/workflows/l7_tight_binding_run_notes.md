# L7 Tight-Binding Run Notes

本文件记录 Lecture-7 examples、historical output and source-audit observations exposed for tight-binding workflows. It is historical evidence and reference-gap orientation, not current user directory fact and not a parameter default source.

Runtime agents must prioritize:
- `l7_tight_binding_state_machine.md`
- `l7_tight_binding.md`
- `skills/knowledge/reference/`

Do not copy this file's hopping values, orbital energies, `TB.U`, SOC strengths, cutoff radii, target eigenvalues, helper scripts or output examples into a current task.

## Example Inventory

| Example | Branch shape | Input clues | Output / helper clues |
|---|---|---|---|
| `pasp_examples/Lecture-7/TB_cases/case1_TB/` | custom TB | `Model TB`, `Orbitals`, `Different_hop_path`, `TB.complex_hop`, `Hop_Parameters`, band/DOS settings | `sub_pasp`, `sub_gnuplot`, `TB.write_wf` example |
| `pasp_examples/Lecture-7/TB_cases/case2_SKTB/` | SKTB | `USE_Slater_Koster_Model`, `use_rotation_matrix`, `Z_values`, `overlap.distance`, `Slater_Koster_Hop_Parameters`, `Orbitals`, `orbitals_nl`, spin/SOC settings, `TB.U` | SKTB path and spin/SOC orientation |
| `pasp_examples/Lecture-7/TB_cases/case3_extended_H/` | SKTB plus additional Hamiltonian | SKTB base plus `TB.additional_H T`, `H_add.dat`, `Hmat_add.dat` | historical added-matrix example |
| `pasp_examples/Lecture-7/TB_cases/case4_spin_dependent_H/` | GSDTB | `TB.find_H_form T`, `TB.full_SOC T`, `TB.H_spin_expand T`, `GSD_TB_Spin_direction`, `TB.H_indep_var`, `fig.maxk`, `fig.mdist` | spin-dependent Hamiltonian form search |
| `pasp_examples/Lecture-7/TB_cases/case5_flatband_CLS/` | SKTB plus CLS | SKTB base, `TB.distance_tiny`, optional `TB.localized_state`, `TB.center_atom_localized`, `TB.rcut_localized`, `TB.eigen_localized` | flat-band/CLS orientation and plotting helpers |
| `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/example/TB_graphene/` | source-tree TB example | `lattice_model.fdf`, graphene structure and TB outputs | `TB.bands`, `Eg.dat`, `energy.dat`, `plot.dat`, `gnuplot.dat`, `hopping.dat` examples |
| `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/example/TB_MLWF/` | MLWF branch | `TB.MLWF`-style outputs including `hr.dat` | out of MVP; future extension |
| `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/example/NiO6_find_H/` | GSDTB / find-H orientation | `lattice_model.fdf`, `TB.find_H_form`, `TB.full_SOC`, spin/SOC settings | `cluster-*.Hform`, `H*.dat`, `WF*.dat`, `Htot.dat` |

## Stable Lessons From Examples

- Lecture-style L7 packages use explicit `Model TB`.
- `Orbitals` is central: it controls orbital basis, hopping matrix dimensions and output matrix dimensions.
- `Z_values` has a TB-specific meaning in curated reference: in the TB module it usually represents the number of considered orbitals/electrons for each element, not a generic copy of non-TB atomic-number assumptions.
- Custom TB and SKTB both support site/vector vs species-distance path descriptions; these are not interchangeable without checking structure and numbering.
- `TB.complex_hop` changes the expected value format in custom hopping matrices.
- `TB.distance_tiny` is used by source as a distance-matching tolerance for SK path recognition.
- `TB.write_wf` is optional and controls wavefunction XSF output.
- `TB.additional_H` needs current-branch `H_add.dat` and/or `Hmat_add.dat` evidence; old `Htot.dat` is output, not input proof.
- GSDTB and CLS are separate run targets. `TB.localized_state T` calls localized-state search and source then stops rather than continuing ordinary band/DOS workflow.

## Source-Audit Lessons Curated Into Workflow

Source root:

```text
/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/
```

Key files:
- `read_input.F90`: `read_TB_para` reads `Orbitals`, selects SKTB / MLWF / custom hopping branches, and reads `TB.distance_tiny`.
- `TB_data.f90`: `read_all_TB_hop` reads custom `Hop_Parameters`; `Different_hop_path` default is `0`, `TB.complex_hop` default is false.
- `SK_TB_data.f90`: `read_SK_TB` reads `Slater_Koster_Hop_Parameters`; `Ylm_form` must be `2`; `Different_hop_path` default is `1`; source comments warn about same-species shell-order cases when not using site format.
- `SK_TB.f90`: distance-based SK matching uses `dist_tiny`.
- `TB.f90`: reads `TB.write_wf`, `TB.localized_state`, `TB.find_H_form` and writes `Eg.dat` / `energy.dat`; calls DOS and wavefunction output paths.
- `plotband.f90`: writes `TB.bands`.
- `dos.f90`: writes `dos.dat`.
- `TB_flat_band.f90`: reads CLS controls and writes `local_cluster.xyz` / `local_cluster.vesta` when `lgood` is true.
- `noncol_diag.f90`: `TB.additional_H` reads `H_add.dat` and `Hmat_add.dat`.
- `TB_H_symmetry.f90`: GSDTB form-search branch writes `cluster-*.Hform`-style files.

## Historical Output Families

| Family | Example names | Validation use |
|---|---|---|
| effective settings | `PASP.used_info`, `out.fdf` | Confirms same-run settings when available |
| band / plot | `TB.bands`, `band.agr`, `plot.dat`, `gnuplot.dat` | Band-structure handoff and plotting |
| gap / energy / DOS | `Eg.dat`, `energy.dat`, `dos.dat` | Numerical summary; must be same-run |
| wavefunction | `wf_kpt_*-band_*.xsf` | Only expected when `TB.write_wf` was active |
| custom/SK hopping diagnostics | stdout hopping path table, `hopping.dat` in some examples | Path and matrix sanity checks |
| additional-H / Hamiltonian artifacts | `H_add.dat`, `Hmat_add.dat`, `Htot.dat`, `H.dat`, `H_R.dat`, `H_I.dat` | Inputs vs outputs must not be mixed |
| GSDTB form search | `cluster-*.Hform`, `H_ik_*_i_*_m_*.dat`, `H*.dat`, `WF*.dat` | Independent-parameter form evidence; exact families depend on branch/version |
| CLS search | `local_cluster.xyz`, `local_cluster.vesta`, log `lgood: T` | CLS handoff evidence |

## Runtime Validation: 2026-06-03 L7 Copied Cases

Runtime directory:

```text
/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/workflow/l7/runs/run_20260603T081912Z
```

These are historical run observations from one copied input set and one Inspire PASP image, not current user-directory facts for future tasks.

- Inputs were copied into isolated run directories. Baseline `workflow/l7/TB_cases/case*` input directories were not polluted with runtime outputs.
- `case2_SKTB`, `case3_extended_H`, and `case5_flatband_CLS` completed with `PASP is finished gracefully` and no `BAD TERMINATION` / signal-kill messages.
- `case1_TB` produced `TB.bands`, `Eg.dat`, `energy.dat`, `dos.dat`, and `wf_kpt_*-band_*.xsf`, but strict output validation failed: the 20-task run ended with MPI rank kill messages, and the 1-task rerun still ended with `Error, graph already allocated.`.
- `case3_extended_H` confirmed `H_add.dat` / `Hmat_add.dat` as same-run input files and generated Hamiltonian / wavefunction artifacts including `Htot.dat`, `H.dat`, `H_R.dat`, `H_I.dat`, `WF*.dat`.
- `case4_spin_dependent_H` with 20 tasks produced GSDTB artifacts but ended with MPI rank kill messages. A 1-task rerun removed the bad termination and ended with `TB_H_symmetry done`, producing `H_ik_*_i_*_m_*.dat` files; no `cluster-*.Hform` appeared in this run.
- `case5_flatband_CLS` validated only the SKTB flat-band band/wavefunction run. The `TB.localized_state`, `TB.center_atom_localized`, `TB.rcut_localized`, and `TB.eigen_localized` lines were commented in the copied input, so no `local_cluster.*` CLS search was run.
- `PASP.used_info` existed in every run but only contained a minimal FDF-open/default record in this environment. Treat it as useful when populated, not as guaranteed effective-setting evidence.

## Reference Gaps To Preserve

Some L7 cards were added for the MVP, but dedicated file cards are still missing for several output/input artifacts:
- `TB.bands`
- `H_add.dat`
- `Hmat_add.dat`
- `Htot.dat`
- `H_ik_*_i_*_m_*.dat`
- `cluster-*.Hform`
- `local_cluster.xyz`
- `local_cluster.vesta`
- `wf_kpt_*-band_*.xsf`

Workflow docs may mention them as branch dependencies or validation targets, but agents must not write exact line formats for missing cards without user authority or new reference coverage.

## Validation Caveats

- Historical output filenames show stable families, but actual presence depends on PASP version, branch flags and run completion.
- Scheduler / platform success is not output validation. Always inspect `log.out` for the branch's expected completion marker and for `BAD TERMINATION`, signal-kill, or decisive error text.
- `PASP.used_info` may be minimal in some runs; do not rely on it alone for effective TB branch settings.
- `Eg.dat` and `energy.dat` prove only that source wrote summary values for that run; they do not prove the TB model is physically appropriate.
- `Htot.dat` / `cluster-*.Hform` must be tied to the same run before used for GSDTB/additional-H conclusions.
- For GSDTB, some current runs may produce `H_ik_*_i_*_m_*.dat` and `TB_H_symmetry done` instead of `cluster-*.Hform`.
- `local_cluster.*` must be paired with success evidence such as `lgood: T`; file presence alone is not enough.
- Plotting files are convenience outputs; `TB.bands` and logs are usually stronger validation anchors.
