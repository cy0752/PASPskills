# L8 Spin-Induced Polarization Run Notes

本文件记录 Lecture-8 examples 和 source-audit observations exposed for spin-induced polarization workflows. It is historical evidence and reference-gap orientation, not current user directory fact and not a parameter default source.

Runtime agents must prioritize:
- `l8_spin_induced_polarization_state_machine.md`
- `l8_spin_induced_polarization.md`
- `knowledge/reference/`

Do not copy this file's spin configurations, GKNB tensors, local axes, Born charges, force constants, elastic constants, spin-strain derivatives, `fig.maxk`, `fig.mdist`, structures, helper scripts or output examples into a current task.

## Example Inventory

| Example | Branch shape | Input clues | Output / helper clues |
|---|---|---|---|
| `pasp_examples/Lecture-8/P_by_spin_order/NiI2/pure_electronic/proper_screw/` | pure electronic KNB / gKNB | `Model KNB`, `spin3.in`, `GKNB_inter_site`, `GKNB.local_axis`, `GKNB.symP`, `SuperCell`, `Z_values`, `isaAB`, `Spin_values`, `fig.maxk`, `fig.mdist` | `Ppair.xsf`, `spin3.xsf`, `GKNB_data.*`, polarization summary lines |
| `pasp_examples/Lecture-8/P_by_spin_order/BiFeO3/pure_electronic/` | pure electronic KNB / exchange-striction-style electronic contribution | `Model KNB`, `spin3.in`, inter-site GKNB tensor data and structure controls | `Ppair.xsf`, `spin3.xsf`, `GKNB_data.*`, `Intersite P` summaries |
| `pasp_examples/Lecture-8/P_by_spin_order/BiFeO3/ion_strain/` | spin-lattice ion / lattice / strain contribution | `Model Spin_lattice_interaction`, `Read_init_spin T`, `spin3.in`, `spin_exchange.dat`, `spin_strain.dat`, `FORCE_CONSTANTS`, `SPOSCAR`, `Zeff.dat`, `elastic.dat`, `spin_lat.spin_force`, `spin_lat.spin_int_stress`, `phonopy_force_constant`, `phon.sym_born_chg` | log summaries for induced stress, displacement, strain, `Pion,Pcell`, `Total P_{ion+lattice}`, `P due to spin force`, `P due to spin stress` |

## Stable Lessons From Examples

- L8 pure electronic and ion/strain branches are separate run targets. A user may need both for a total analysis, but preflight and output validation should keep their input provenance separate.
- Pure electronic KNB uses explicit `Model KNB` and reads a spin configuration through `spin3.in` or branch settings; output validation should check completion and log polarization summaries, not only visualization files.
- `spin3.in` row order must match the actual calculation-cell atom order. If `SuperCell` expands `cell.str`, row order may be difficult to infer; prefer explicit current target `cell.str` when the user can provide it.
- GKNB tensor values and local-axis definitions are material- and convention-specific. Examples are format / branch orientation only until current-material provenance and user confirmation exist.
- The spin-lattice ion/strain branch is `Model Spin_lattice_interaction`, but L8 use is not the same as L2 PTMC / CG magnetic-ground-state search. L8 validation focuses on polarization contribution summaries and provenance for Born charge, force constants, elastic and spin-strain inputs.
- `FORCE_CONSTANTS` and `SPOSCAR` are observed in the L8 ion/strain example as phonopy-related inputs. Basic reference cards now document their PASP/phonopy file roles and minimal validation constraints; exact material data generation still requires user/source authority.

## Source-Audit Lessons Curated Into Workflow

Source root:

```text
/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/
```

Key files:
- `main.F90`: `CASE ("KNB")` routes to `CALL KNB`.
- `KNB.f90`: KNB / gKNB path reads GKNB data, writes `spin3.xsf` and `Ppair.xsf`, and prints polarization summaries.
- `KNB_data.F90`: reads `GKNB_inter_site`, `GKNB_single_site`, `GKNB.local_axis`, `GKNB.symP`, `GKNB.spiral`, `GKNB.qvec`, and `GKNB.spiral_plane_vec`.
- `KNB.f90`: `Dipole_GKNB` writes pair diagnostics and `GKNB_data.<ia>` files in observed source path.

## Historical Output Families

| Family | Example names / log clues | Validation use |
|---|---|---|
| effective settings | `PASP.used_info`, stdout / scheduler log | Confirms same-run settings when populated |
| KNB visualizations | `spin3.xsf`, `Ppair.xsf` | Visual evidence for spin / pair-polarization fields; not sufficient alone |
| KNB diagnostics | `GKNB_data.*`, `Intersite P`, `Intersite P (Exchange striction)`, `spin_FE: Dipole is`, `spin_FE: P is` | Pure electronic contribution evidence |
| spin-lattice contribution summaries | `Pion,Pcell`, `Total P_{ion+lattice}`, `P due to spin force`, `P due to spin stress` | Ion / lattice / strain contribution evidence |
| spin-lattice diagnostic fields | `1.xsf`, `2.xsf`, `3.xsf`, `01dJ.xsf`, `02dJ.xsf`, `03dJ.xsf` in examples | Historical visualization family; exact presence depends on settings/version |

## Runtime Validation: 2026-06-03 L8 Copied Cases

Runtime directory:

```text
/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/workflow/l8/runs/20260603T110603Z
```

These are historical run observations from one copied input set and one Inspire PASP image, not current user-directory facts for future tasks.

Resource profile:

```text
CPU资源空间 / CPU资源-2 / 20核100GB / paspmpi:v2
nodes=1, tasks=20, cpus-per-task=1, memory-per-cpu=4G
```

Fresh run summary:

| Case | Branch | Result | Evidence |
|---|---|---|---|
| `BiFeO3_pure_electronic` | pure electronic KNB | pass | `PASP is finished gracefully.`, `spin_FE: P is`, `Intersite P`, `Intersite P (Exchange striction)`, `Ppair.xsf`, `spin3.xsf` |
| `NiI2_pure_electronic_cycloid` | pure electronic KNB | pass | `PASP is finished gracefully.`, `spin_FE: P is`, `Intersite P`, `Ppair.xsf`, `spin3.xsf` |
| `NiI2_pure_electronic_fm` | pure electronic KNB | pass | `PASP is finished gracefully.`, zero-valued `spin_FE: P is`, `Intersite P`, `Ppair.xsf`, `spin3.xsf` |
| `NiI2_pure_electronic_proper_screw` | pure electronic KNB | pass | `PASP is finished gracefully.`, `spin_FE: P is`, `Intersite P`, `Ppair.xsf`, `spin3.xsf` |
| `BiFeO3_ion_strain` | spin-lattice ion / lattice / strain | fail | Inspire status reached `SUCCEEDED_RETAINING`, but `log.out` contains repeated `read_spin_stress: MPI version not implemented yet`, then `BAD TERMINATION` and `KILLED BY SIGNAL: 9` |

Additional 1-task diagnostic:

```text
BiFeO3_ion_strain_1task
job id: hpc-job-c817ad18-fae6-46be-a74f-b857a29adaa8
```

It was submitted after the 20-task ion/strain failure to test whether the failure is MPI-specific. The diagnostic completed successfully. Its `log.out` contains `PASP is finished gracefully.`, `Induced stress`, `Induced strain`, `Pion,Pcell`, `Total P_{ion+lattice}`, `P due to spin force`, and `P due to spin stress`; same-run diagnostics include `1.xsf`, `2.xsf`, `3.xsf`, `01dJ.xsf`, `02dJ.xsf`, and `03dJ.xsf`.

Stable lessons:

- Scheduler success is not output validation. `BiFeO3_ion_strain` reached `SUCCEEDED_RETAINING` on Inspire while PASP itself failed in `log.out`.
- For pure electronic KNB in this PASP image, `Ppair.xsf` and `spin3.xsf` appeared in all four fresh runs, but no `GKNB_data.*` files appeared. Treat `GKNB_data.*` as optional / version- or setting-dependent unless a current run actually writes it.
- Pure electronic KNB validation should require `log.out` completion plus polarization summaries. Visualization file presence alone is not enough.
- `BiFeO3_pure_electronic/input` already contained `Ppair.xsf` before running; the fresh run rewrote it with an mtime matching `log.out`, but future validators should still treat pre-existing visualization files as stale until tied to the current run.
- The ion/strain branch with `spin_lat.spin_int_stress T` hit `read_spin_stress: MPI version not implemented yet` under 20 MPI tasks, while the same copied input passed as a one-task diagnostic run. This indicates a PASP MPI implementation/runtime limitation for the spin-stress read path, not a bad input package.
- For this PASP image, L8 ion/strain spin-stress output should be validated from a completed serial/one-task diagnostic or from a future fixed-source MPI run. Do not treat the failed 20-task MPI run as successful just because Inspire reports scheduler success.
- Parallel Inspire HPC helper submissions can trigger HTTP 429 on `hpc_jobs/detail`. The job may already exist; query `hpc_jobs/list` by job name before retrying to avoid duplicate jobs.

## Skill Dry-Run: 2026-06-03

Development dry-run used read-only verifier-style checks against the copied L8 target directories and the fresh run directory above.

Observed skill behavior:
- `NiI2/pure_electronic/proper_screw/input` is classified as S1 / B1 pure electronic KNB. It has `PASP.input`, `cell.str`, `unit_cell.str`, `spin3.in`, and helper `sub_pasp`; no stale L8 outputs were found in that input package. Inventory alone still correctly blocks run-directory derivation until S3 user confirmation and S4 input preflight pass.
- `BiFeO3/ion_strain/input` is classified as S4 / B2 spin-lattice ion/strain. It has the expected branch files and `sub_pasp` records one planned task, so the `spin_lat.spin_int_stress T` MPI gate is satisfiable for that helper. Presence alone still does not prove current-material provenance for `spin_exchange.dat`, `spin_strain.dat`, `FORCE_CONSTANTS`, `SPOSCAR`, `Zeff.dat`, `elastic.dat`, or `spin3.in` row order.
- `BiFeO3_ion_strain` 20-task output validation fails because `log.out` contains `read_spin_stress: MPI version not implemented yet`, `BAD TERMINATION`, and `KILLED BY SIGNAL`; same-run XSF diagnostics do not override the failed log.
- `BiFeO3_ion_strain_1task` output validation passes for diagnostic handoff: `log.out` contains normal completion, induced stress/strain, `Pion,Pcell`, `Total P_{ion+lattice}`, `P due to spin force`, and `P due to spin stress`; same-run `1.xsf`, `2.xsf`, `3.xsf`, `01dJ.xsf`, `02dJ.xsf`, and `03dJ.xsf` are diagnostics, not standalone validation.

Dry-run correction:
- The first B2 preflight dry-run over-reported a hard failure for missing trailing fourth-order count in `spin_exchange.dat`. Source audit showed `read_exchange_para` treats EOF before trailing optional SIA / DMI / fourth-order counts as zero-count sections. The `spin_exchange.dat` reference and verifier contract were corrected to treat omitted trailing optional count lines as non-canonical warnings, not hard fails by themselves.
- `SYMPREC` appeared in L8 inputs and verifier requirements. A source-backed parameter card now exists, so exact semantics should route to `params/SYMPREC.md`; the actual value still needs current-structure / current-workflow confirmation before editing.

## Reference Coverage Added / Remaining Limits

Dedicated file cards now cover the basic L8 artifacts that were previously listed as gaps:
- `Ppair.xsf`
- `spin3.xsf`
- `GKNB_data.*`
- `FORCE_CONSTANTS`
- `SPOSCAR`
- L8-specific ion/strain visualization families such as `1.xsf`, `2.xsf`, `3.xsf`, and `*dJ.xsf`

The cards are intentionally minimal. They document file roles, same-run validation requirements, source/runtime observations and known conditional behavior; they do not authorize agents to invent material-specific `FORCE_CONSTANTS`, GKNB tensors, local axes, Born charges, elastic constants, spin-strain derivatives, or coordinate-frame conventions. If a task needs exact physical content beyond the curated cards, keep it as a reference gap and ask for user/source authority.

## Validation Caveats

- Historical output filenames show stable families, but actual presence depends on PASP version, branch flags and run completion.
- Scheduler / platform success is not output validation. Always inspect logs for `PASP is finished gracefully`, branch-specific polarization summaries, and decisive errors such as `BAD TERMINATION`, signal kills, or `Error, ...`.
- `PASP.used_info` may be minimal in some runs; do not rely on it alone for effective branch settings.
- Visualization files prove that a writer path ran; they do not prove coordinate-frame correctness or physical appropriateness.
- Pure electronic and ion/strain contribution numbers should not be combined unless both runs have same-material, same-structure / compatible spin-configuration provenance and output validation evidence.
