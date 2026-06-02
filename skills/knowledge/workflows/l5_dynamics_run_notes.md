# L5 Dynamics Run Notes

本文件记录 Lecture-5 Cr2O3 dynamics example 和 BaTiO3 electric-hysteresis example 的历史观察。它不是当前用户 workspace 的实时证据，也不是 production 参数授权。runtime agent 默认应使用 `l5_dynamics_state_machine.md` 和 `l5_dynamics.md` 的稳定契约；只有用户需要历史样例、输出家族或 reference gap 线索时，才引用本文件。

## Scope
- Historical source: Lecture-5 Cr2O3 spin-lattice relaxation example.
- Historical source: Lecture-5 BaTiO3 electric-hysteresis example.
- Example directory observed during authoring: `pasp_examples/Lecture-5/MD-2/`.
- BaTiO3 example directory observed during authoring: `pasp_examples/Lecture-5/MD-1/`.
- External lectureexamples copy was observed as equivalent for this branch at authoring time.

Do not require runtime users or deployed agents to open these source directories. The reusable knowledge has been curated into the workflow and state-machine files.

## Historical Cr2O3 workflow shape

The Cr2O3 example is organized as three sequential dynamics stages:

| Historical stage | Directory | Stage intent | Classifier |
|---|---|---|---|
| Stage 1 | `MD-2/step-1/` | lattice heating while spin subsystem is frozen by stage intent | `SLD.mode 1` |
| Stage 2 | `MD-2/step-2/` | spin heating while lattice subsystem is frozen by stage intent | `SLD.mode 2` |
| Stage 3 | `MD-2/step-3/` | coupled spin-lattice relaxation | `SLD.mode 3` |

Each stage in the historical example contains:
- `input/`: baseline stage package;
- `output/`: small curated output subset;
- `complete/`: full completed-run snapshot.

`complete/` is historical evidence only. It should not be copied wholesale into a fresh run directory.

## Historical input package observations

Each observed Cr2O3 stage input package contains:
- `PASP.input`
- `MD.input`
- `cell.str`
- `unit_cell.str`
- `local_mode_PM.dat`
- `J_best.dat`
- `amp_local_mode.in`
- `mode_def.input`
- `mode_mass.input`
- `sub_pasp`

The observed `PASP.input` includes:
- `%include cell.str`
- `%include unit_cell.str`
- `%include MD.input`
- `%include mode_def.input`
- `%include mode_mass.input`

The split files `mode_def.input` and `mode_mass.input` are example file roles. File-level checks route to `skills/knowledge/reference/files/mode_def.input.md` and `skills/knowledge/reference/files/mode_mass.input.md`; exact block syntax still routes to the relevant param reference before writing.

## Historical `MD.input` settings observed

These values are historical example settings, not defaults and not production recommendations.

| Stage | Observed classifier | Historical settings observed |
|---|---|---|
| Stage 1 lattice heating | `SLD.mode 1` | Example used a lattice bath / damping setup and a low lattice target temperature. |
| Stage 2 spin heating | `SLD.mode 2` | Example used spin damping and a higher spin target temperature. |
| Stage 3 coupled relaxation | `SLD.mode 3` | Example used coupled spin-lattice dynamics with zero damping terms for an NVE-like relaxation intent. |

Exact values such as target temperatures, time steps, total times, damping constants, output cadence, `LLG.method`, `SuperCell`, species settings, mode count, mass values, and scheduler settings are example-instance observations only. A runtime agent must ask the user to confirm current settings and must check reference before writing fields.

## Historical `amp_local_mode` handoff

The example shows a stage-to-stage handoff through `amp_local_mode`:
- stage 2 `amp_local_mode.in` was derived from stage 1 `amp_local_mode.out`;
- stage 3 `amp_local_mode.in` was derived from stage 2 `amp_local_mode.out`.

During authoring, hashes confirmed the observed upstream `amp_local_mode.out` and downstream `amp_local_mode.in` matched for both handoffs. That supports the stable workflow contract that downstream stages must record upstream run identity and output-validation evidence before using a copied/renamed `amp_local_mode.out`.

The hash values themselves are historical example facts and should not be used as runtime validation for a user's current run.

## Historical output observations

The small `output/` folders and full `complete/` snapshots contain the key MVP validation files:
- `temperature.dat`
- `energy.dat`
- `amp_local_mode.out`

Full `complete/` snapshots also contain historical diagnostic / evidence files such as:
- `PASP.used_info`
- scheduler stdout / stderr files
- `seed_used.in`
- `S_abs.dat`
- `angular_momentum.dat`
- `momentum.dat`
- `field.dat`
- `atoms_all_spin.xsf`
- `def_local_modes.dat`
- `local_mode_PM_used.dat`
- `all_interaction_type_used.dat`
- `all_interaction_type_Spin_xyzform_used.dat`
- `interaction_type_used.dat`
- local-mode XSF files

Only `temperature.dat`, `energy.dat`, `amp_local_mode.out`, completion evidence, and `PASP.used_info` are part of the MVP validation target. Other files are useful diagnostic observations but not guaranteed workflow requirements unless reference or current-run evidence establishes them.

## Historical output headers

Authoring source audit confirmed these core output families:
- `temperature.dat` includes subsystem temperature columns for spin and lattice.
- `energy.dat` includes step / time / potential / kinetic / total energy columns.
- `amp_local_mode.out` is written from the final local-mode state.

Runtime validation should check the actual current run files and logs. It should not assume the current output length, exact numerical values, or convergence behavior from the historical example.

## Historical smoke-test observation

A short stage-1 Cr2O3 smoke test was observed during authoring in:

```text
/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/workflow/l5/2/runs/smoke_stage1_2x2x1_50fs
```

This run is historical evidence only. It is not production validation, not a recommended production parameter set, and not a default for future users.

Observed smoke-test setup:
- `SuperCell` was reduced from the lecture-scale `4 x 8 x 5` example to `2 x 2 x 1`.
- `amp_local_mode.in` was reduced from 14400 rows to 360 rows to match the reduced simulation cell.
- `atom_Heff.MD_time` was shortened to 50 fs and `MD.int_step` was set to 10.
- The run used 4 MPI tasks and finished successfully; the Inspire job id `hpc-job-81e02c73-2b00-42df-949d-678d355ca4eb` is historical evidence only, not a runtime contract.

Observed smoke-test outputs:
- `log.out` reached MD step 100 and reported `PASP is finished gracefully`.
- `amp_local_mode.out` contained 360 rows.
- `temperature.dat` and `energy.dat` each contained a header plus sampled rows for steps 0, 10, ..., 90.
- In this stage-1 smoke run, the spin temperature remained zero while the lattice temperature rose and then evolved over the short sampled window.

Stable lessons from this smoke test:
- If a smoke test reduces `SuperCell`, the initial-state file must be resized or regenerated so `amp_local_mode.in` row count matches the reduced simulation cell. Planned MPI ranks must still be compatible with the `SuperCell` determinant and workflow/runtime requirement.
- Output validation should check headers, monotonic sampled rows, branch-consistent qualitative behavior, and successful completion. It should not require sampled `temperature.dat` / `energy.dat` to include the final MD step exactly.

## Historical stage-2 smoke-test observation

A short stage-2 Cr2O3 smoke test was observed during authoring in:

```text
/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/workflow/l5/2/runs/smoke_stage2_2x2x1_50fs
```

This run is historical evidence only. It is not production validation, not a recommended production parameter set, and not a default for future users.

Observed smoke-test setup:
- The run was derived from the successful stage-1 smoke run in `smoke_stage1_2x2x1_50fs`.
- Stage-1 `amp_local_mode.out` was copied to stage-2 `amp_local_mode.in`.
- `SuperCell` remained `2 x 2 x 1`, `atom_Heff.MD_time` was 50 fs, and `MD.int_step` was 10.
- The run used 4 MPI tasks and finished successfully; the Inspire job id `hpc-job-d4817e56-f501-42b0-9c3f-1c9c044cb8cb` is historical evidence only, not a runtime contract.

Observed smoke-test outputs:
- `log.out` reached MD step 100 and reported `PASP is finished gracefully`.
- `amp_local_mode.out` contained 360 rows.
- `temperature.dat` and `energy.dat` each contained a header plus sampled rows for steps 0, 10, ..., 90.
- In this stage-2 smoke run, the spin temperature evolved while the lattice temperature remained zero.
- `energy.dat` kinetic energy remained zero for this spin-only stage.
- `amp_local_mode.out` was not byte-identical to `amp_local_mode.in`: spin-vector fields changed, while local-mode / lattice fields remained unchanged in this run.

Stable lessons from this smoke test:
- Stage-2 output validation must not require `amp_local_mode.out` to be byte-identical to `amp_local_mode.in`; the stage output is the spin-heated final state for downstream handoff.
- For `SLD.mode 2`, branch-consistent smoke evidence is spin evolution with frozen lattice indicators, not frozen spin vectors.

## Historical stage-3 smoke-test observation

A short stage-3 Cr2O3 smoke test was observed during authoring in:

```text
/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/workflow/l5/2/runs/smoke_stage3_2x2x1_50fs
```

This run is historical evidence only. It is not production validation, not a recommended production parameter set, and not a default for future users.

Observed smoke-test setup:
- The run was derived from the successful stage-2 smoke run in `smoke_stage2_2x2x1_50fs`.
- Stage-2 `amp_local_mode.out` was copied to stage-3 `amp_local_mode.in`.
- `SuperCell` remained `2 x 2 x 1`, `atom_Heff.MD_time` was 50 fs, and `MD.int_step` was 10.
- The coupled SLD smoke run used `SLD.mode 3`, zero `LLG.damping`, zero `MD.damping`, and `MD.temperature 0.0`.
- A smaller coupled-stage time step was used for this smoke run than in stages 1 and 2, consistent with the NVE energy-conservation caution in the MD reference.
- The run used 4 MPI tasks and finished successfully; the Inspire job id `hpc-job-fe3367da-67f9-4cf6-8941-c03cc9f678cb` is historical evidence only, not a runtime contract.

Observed smoke-test outputs:
- `log.out` reached MD step 250 and reported `PASP is finished gracefully`.
- `amp_local_mode.out` contained 360 rows.
- `amp_local_mode.out` differed from `amp_local_mode.in`, as expected for coupled spin-lattice dynamics.
- `temperature.dat` and `energy.dat` each contained a header plus sampled rows for steps 0, 10, ..., 240.
- In this stage-3 smoke run, both spin and lattice temperature columns evolved during the sampled window. One sampled comparison showed spin temperature changing from 47.49 K to 36.50 K and lattice temperature changing from 30.47 K to 24.23 K.
- `energy.dat` total energy stayed nearly constant over the sampled window for this short NVE-like smoke run, changing from `-2.829687E-01` H to `-2.829679E-01` H.
- `PASP.used_info` existed but was sparse in this run: it only recorded FDF open / default machine-code lines, not a full effective-setting summary.

Stable lessons from this smoke test:
- Stage-3 output validation should check both subsystem temperature / diagnostic columns for coupled-stage evolution or evaluate both subsystems together when the run is configured as coupled SLD.
- If `PASP.used_info` is sparse or incomplete, record that fact and cross-check effective settings through `MD.input`, `PASP.input`, completion log evidence, and output files instead of failing solely on `PASP.used_info`.
- For NVE-like coupled relaxation, report `energy.dat` drift / range as evidence. Do not apply a hidden acceptance threshold unless the user provides one.
- For short smoke tests, successful completion and monotonic sampled rows are sufficient workflow evidence; scientific acceptance of relaxation quality or energy drift thresholds remains user-owned.

## Example-specific details not to generalize

Do not generalize the historical example's:
- Cr2O3 supercell and atom count;
- target temperatures;
- damping constants;
- time steps and total times;
- `LLG.method`;
- output cadence;
- local-mode count and mass values;
- `fig.*` and `Invariant.*` settings;
- Slurm partition, task count, walltime, module, PASP executable path, or `sub_pasp` layout.

These may be useful for recognizing the example, but they are not current-workspace evidence and not production defaults.

## Historical BaTiO3 electric-hysteresis observation

The Lecture-5 `MD-1` example is a single BaTiO3 electric-field MD run under `Model atomic_effective_H`. It is not a Cr2O3 three-stage `SLD.mode 1/2/3` handoff workflow.

Observed `MD-1/input/` files:
- `PASP.input`
- `MD.input`
- `cell.str`
- `unit_cell.str`
- `local_mode_PM.dat`
- `J_best.dat`
- `amp_local_mode.in`
- `Zeff.dat`
- `sub_pasp`

Observed stable lessons:
- `PASP.input` includes `MD.input`, `cell.str`, and `unit_cell.str`.
- The branch consumes a pre-existing effective-H / local-mode model through `local_mode_PM.dat` and `J_best.dat`.
- `atom_Heff.getP T` and the electric-field path require checking `Zeff.dat` against the current unit-cell / mode basis before trusting `P_abs.dat`.
- `amp_local_mode.in` is the initial local-mode amplitude state. In the historical `MD-1` example it had 1440 rows, matching `10 * 12 * 12`, but this is example evidence only; a current run must check row count against its own `SuperCell` and basis.
- `sub_pasp` is an environment helper. Its partition, task count, module setup, executable path, and walltime are not workflow defaults.

Historical `MD-1` values observed:
- `SuperCell` was `10 x 12 x 12`.
- `MD.temperature` was `90.0`.
- `MD.Delta_t` was `0.5 fs`.
- `atom_Heff.MD_time` was `2.0d5 fs`.
- `MD.aft_step` was `200000`.
- `MD.int_step` was `100`.
- `MD.E_type` was `3`, with the example comment identifying a cosine function.
- `MD.E_x`, `MD.E_y`, and `MD.E_z` were each `0.05` in the lecture/example notation.
- `MD.E_omega` was `6.283d-5`.
- `MD.E_phi` was `-1.571`.
- `local_mode.MD_mode_range` had three rows of `-0.42450 0.42450`.

These are historical tutorial settings, not production recommendations. A runtime agent must get user confirmation and reference coverage before writing or changing them.

Historical `MD-1` outputs observed:
- `output/field.dat` had a header with `step`, `time (ps)`, `E_x`, `E_y`, `E_z`, `B_x`, `B_y`, and `B_z`, followed by 2001 sampled rows.
- `output/P_abs.dat` had a header with `step`, `time (ps)`, `P_x`, `P_y`, `P_z`, and `P_abs`, followed by 2001 sampled rows.
- `complete/field.dat` matched `output/field.dat` in the authoring audit.
- `complete/P_abs.dat` had the same shape as `output/P_abs.dat` but differed numerically from `output/P_abs.dat`.
- `complete/energy.dat` and `complete/temperature.dat` existed as diagnostics.
- `complete/pasp.1068704.out` showed normal completion, including `atom_Heff_MD_main done` and graceful PASP finish evidence.

Stable lesson from the `P_abs.dat` mismatch:
- Do not assume a curated `output/` subset and a `complete/` snapshot are same-run paired evidence just because filenames and row counts match.
- Runtime output validation must establish same-run provenance for `field.dat` and `P_abs.dat` before plotting hysteresis curves.
- Hysteresis analysis should plot user-confirmed polarization component versus corresponding electric-field component only after validation passes.

## Historical BaTiO3 one-period demonstration observation

A one-period BaTiO3 hysteresis demonstration was observed during authoring in:

```text
/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/workflow/l5/1/runs/demo_batio3_hysteresis_1period
```

This run is historical evidence only. It validates workflow mechanics and same-run plotting for a short demonstration; it is not production convergence evidence, not a scientific acceptance threshold, and not a recommended default parameter set.

Observed demonstration setup:
- Inspire job id was `hpc-job-a504cf51-205c-4c24-af3f-b07ccc72c8e0`; final status was `SUCCEEDED_RETAINING`.
- The run-local `MD.input` changed `atom_Heff.MD_time` from `2.0d5` fs to `1.0d5` fs and `MD.aft_step` from `200000` to `0`.
- `MD.int_step` remained `100`, `MD.Delta_t` remained `0.5`, and the BaTiO3 electric branch settings were preserved from the historical MD-1 demonstration input.
- `MD.E_omega` was `6.283d-5 1/fs`; using the observed cosine-branch relation `T = 2*pi / omega`, the field period is about `1.0d5 fs`, so this run recorded one period.
- The historical run used 20 MPI ranks for its environment. This is environment evidence only, not a default.

Observed demonstration outputs:
- `log.out` contained `atom_Heff_MD_main done`, reported `MD Elapsed Time (minute): 18.434`, and ended with `PASP is finished gracefully.`
- `field.dat` and `P_abs.dat` each had 2001 lines: one header plus 2000 aligned sampled rows.
- The first aligned sample was step `99`, time `0.0495` ps; the last aligned sample was step `199999`, time `99.9995` ps.
- The generated plot was `hysteresis_E_x_vs_P_x.png`.
- The plotted same-run data range was `E_x` from `-9.723447E-04` to `9.723447E-04`, and `P_x` from `-4055.849` to `4045.551` e*Bohr.
- `PASP.used_info` existed but was sparse again: 5 lines with only FDF/default header-style content. Validation relied on same-run inputs, outputs, and completion log evidence.

Stable lessons from this demonstration:
- For periodic/cosine electric-field demonstrations, the run length must cover the intended field period(s); `T = 2*pi / MD.E_omega` is useful only when units and branch semantics are confirmed from the current input/reference.
- `MD.aft_step` must leave a recorded window within the total MD steps. In a one-period demonstration, carrying over an equilibration offset greater than or equal to total steps would leave no useful `field.dat` / `P_abs.dat` plotting window.
- `field.dat` and `P_abs.dat` must be validated as same-run, step/time-aligned series before plotting.
- Sparse `PASP.used_info` should be recorded as a limitation and cross-checked with run-local inputs, logs, and generated outputs rather than treated as a standalone failure.

## Reference gaps / future work

Potential future improvements:
- Build a reusable Cr2O3 template only if placeholders, reference coverage, and user-confirmation gates can prevent historical values from becoming implicit defaults.
- Improve BaTiO3 reference coverage if source/docs clarify exact electric-field units for `MD.E_x/y/z` and row-count semantics for `local_mode.MD_mode_range`.
