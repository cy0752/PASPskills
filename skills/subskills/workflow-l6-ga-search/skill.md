---
name: workflow-l6-ga-search
description: Guide PASP GA global structure search workflows.
---

Read `../../knowledge/workflows/l6_ga_search_state_machine.md` first. Only read the relevant section of `../../knowledge/workflows/l6_ga_search.md` after the current state and branch are known.

Use `../../knowledge/workflows/l6_ga_search_run_notes.md` only for historical Lecture-6 example observations, output-family orientation, source-audit lessons, or identifying reference gaps. It cannot authorize current parameters, formal inputs, run derivation, plotting, post-GA optimization, or submission.

## State Machine First
Always classify the current state using S0-S7 from the state-machine file first. The long workflow can only add details for the current state; it cannot bypass:
- S3 user-confirmed L6 GA settings STOP.
- S4 read-only input preflight STOP ON FAIL.
- S5 explicit submission authorization.
- S6 output validation STOP ON FAIL before low-energy handoff, post-GA optimization claims, plotting, symmetry reporting, or restart.

## Responsibilities
- Identify the user's current GA search stage.
- Distinguish common branches such as plain random search, random space group, perturbation search, magnetic GA, restart, fixed / constrained cell, interface, parallel external evaluation, and output validation.
- Explain which input package, external evaluator files, run metadata, helper scripts, generated outputs, or output validation checks are needed next.
- When the user, Claude, or Codex is modifying current-stage inputs, identify the state and branch first, then list settings normally adjustable at that stage.
- Explain adjustable items at workflow-control level only; route exact syntax, defaults, file formats, numbering rules, conditional dependencies, or limitations to reference.
- Treat user authorization to use subagents as read-only fact-collection authorization only. It does not confirm GA settings and does not authorize submission.

## Runtime Hard Rules
- Before promoting an L6 candidate package to formal `input/`, overwriting formal input, deriving `runs/<run-id>/`, creating or editing submit-ready helper artifacts, preparing external task configuration, or submitting a job, run a read-only input preflight through `../pasp-verifier/skill.md` with `mode: input-preflight`.
- Required markers before any formal input / run / submission-preparation action: `USER_CONFIRMED_L6_GA_SETTINGS=true`, `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`, and `STAGE_PREFLIGHT_PASS=true`.
- Directory inventory, template comparison, log review, and output validation are not input preflight.
- Before reporting `Saved_*.POS`, low-energy summaries, post-GA optimized energies, symmetry labels, or restart artifacts as usable, run output validation through `../pasp-verifier/skill.md` with `mode: output-validation`.
- The read-only verifier must not edit files, choose physical parameters, promote inputs, create run directories, prepare submission artifacts, or submit jobs.
- Actual job submission still needs explicit user submission authorization after preflight passes.
- Do not use Lecture-6 example values as defaults for a current material. Example packages provide file-role orientation only until current-material provenance, user-confirmed settings, and reference-backed exact writes exist.

## Route To Reference When
- The user asks for a single GA field definition.
- The user asks about parameters such as `Model`, `GA.population_size`, `GA.max_generation`, `save_str.nsave_str`, `GA.Pher`, `GA.Pmut`, `GA.perturbation`, `GA.parallel`, `GA.gen_ran_str_sym`, `GA.spg_front`, `GA.spg_rear`, `GA.magnetic`, `GA.random_magnetic`, `GA.lAFM_GA`, `GA.lmut_mag_GA`, `GA.flip_spin_rate`, `GA.ldiff_str_with_mag_GA`, `GA.lread_OUTCAR_mag`, `GA.fixlattice`, `GA.fix_cell`, `GA.biaxial_strain`, or `GA.lat_fix_2D_Ang`.
- The user asks for exact formats of `PASP.input`, `%include`, `%block`, `seed.in`, `cell.str`, `unit_cell.str`, `SuperCell`, `Z_values`, or `Spin_values`.
- The user asks whether a branch needs an external evaluator helper, `run_pvasp.sh`, `MAGMOM_*`, `OUTCAR`, `strs_saved.dat`, restart artifacts, interface surfaces, or any other conditionally required file.
- A write depends on exact PASP field syntax, block row counts, defaults, file formats, numbering rules, model-specific output files, or setting-dependent dependencies.
