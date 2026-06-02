---
name: workflow-l5-dynamics
description: Guide PASP MD, spin dynamics, and LLG workflows.
---

Read `../../knowledge/workflows/l5_dynamics_state_machine.md` first. Only read the relevant section of `../../knowledge/workflows/l5_dynamics.md` after the current state and branch are known.

For a short user-facing checklist, read `../../knowledge/workflows/l5_dynamics_user_checklist.md` after the state-machine gate is understood. The checklist is only an operational summary; it cannot replace STOP gates or reference-before-write checks.

Use `../../knowledge/workflows/l5_dynamics_run_notes.md` only for historical Lecture-5 example observations, output-family orientation, or identifying reference gaps. It contains both Cr2O3 and BaTiO3 observations, but it cannot authorize current parameters, formal inputs, run derivation, plotting, or submission.

## State Machine First
Always classify the current state using S0-S7 from the state-machine file first. The long workflow can only add details for the current state; it cannot bypass:
- S3 user-confirmed L5 dynamics settings STOP.
- S4 read-only input preflight STOP ON FAIL.
- S5 explicit submission authorization.
- S6 output validation STOP ON FAIL before plotting or downstream handoff.

## Responsibilities
- Identify the user's current branch and stage in `Model atomic_effective_H` MD / ASD / LLG / SLD work.
- For a generic or new-material branch, classify the intended dynamics path before preparing inputs: plain MD / LLG / ASD / SLD, electric-field / polarization response, smoke test, equilibration, production run, output validation, or downstream handoff.
- For the MVP Cr2O3 branch, classify the stage as lattice heating (`SLD.mode 1`), spin heating (`SLD.mode 2`), coupled SLD relaxation (`SLD.mode 3`), output validation, or handoff.
- For the BaTiO3 electric-hysteresis branch, classify it as a single-stage `Model atomic_effective_H` MD electric-field run using `field.dat` plus `P_abs.dat` validation, not as a Cr2O3 three-stage handoff sequence.
- Explain which input package, upstream model files, `amp_local_mode` handoff, run metadata, or output validation checks are needed next.
- For new materials, treat `local_mode_PM.dat`, `J_best.dat`, mode definition / mass definition, structure files, optional `Zeff.dat`, and first-stage `amp_local_mode.in` as user-provided or upstream PASP-stage provenance requirements unless the user provides authoritative generation evidence.
- When the user, Claude, or Codex is modifying current-stage inputs, identify the stage first, then list settings normally adjustable at that stage.
- Explain adjustable items at workflow-control level only; route exact syntax, defaults, file formats, numbering rules, or limitations to reference.
- Treat user authorization to use subagents as read-only fact-collection authorization only. It does not confirm physical settings and does not authorize submission.

## Runtime Hard Rules
- Before promoting an L5 candidate package to formal `input/`, overwriting formal input, deriving `runs/<run-id>/`, creating or editing submission artifacts, preparing external task configuration, or submitting a job, run a read-only input preflight through `../pasp-verifier/skill.md` with `mode: input-preflight`.
- Required markers before any formal input / run / submission-preparation action: `USER_CONFIRMED_L5_DYNAMICS_SETTINGS=true`, `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`, and `STAGE_PREFLIGHT_PASS=true`.
- Before stage 2 or stage 3 uses `amp_local_mode.in`, the upstream completed run must have output validation evidence for `amp_local_mode.out`; record upstream run identity before any downstream overwrite.
- Directory inventory, template comparison, log review, and output validation are not input preflight.
- The read-only verifier must not edit files, choose physical parameters, promote inputs, create run directories, prepare submission artifacts, or submit jobs.
- Actual job submission still needs explicit user submission authorization after preflight passes.
- Do not use BaTiO3 example values or electric-field gates to drive the Cr2O3 branch. Do not use Cr2O3 `SLD.mode 1/2/3` handoff gates as the BaTiO3 electric-hysteresis checklist.
- Do not use Cr2O3 or BaTiO3 historical values as defaults for a generic/new-material branch. Example packages can only provide file-role orientation until current-material provenance, user-confirmed settings, and reference-backed exact writes exist.

## Route To Reference When
- The user asks for a single `MD.input` field definition.
- The user asks about parameters such as `MD.Delta_t`, `atom_Heff.MD_time`, `SLD.mode`, `LLG.method`, `LLG.damping`, `MD.damping`, `MD.temperature`, `MD.init_velocity_temp`, `MD.aft_step`, `MD.int_step`, or `MD.output_amp_lm`.
- The user asks about BaTiO3 electric-field controls such as `MD.E_type`, `MD.E_x`, `MD.E_y`, `MD.E_z`, `MD.E_omega`, `MD.E_phi`, `Field_for_Electrocaloric`, `local_mode.MD_mode_range`, or `atom_Heff.getP`.
- The user asks about files such as `amp_local_mode.in`, `local_mode_PM.dat`, `J_best.dat`, `Zeff.dat`, `elastic.dat`, `spin_strain.dat`, `cell.str`, or `unit_cell.str`.
- The user asks whether a new-material package needs `Zeff.dat`, `elastic.dat`, `spin_strain.dat`, split mode files, inline mode blocks, or any other conditionally required file.
- The user asks about output files such as `field.dat`, `P_abs.dat`, `temperature.dat`, `energy.dat`, or `PASP.used_info`.
- A write depends on exact PASP field syntax, block row counts, defaults, file formats, numbering rules, or model-specific conditional dependencies.
