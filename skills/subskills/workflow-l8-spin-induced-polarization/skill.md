---
name: workflow-l8-spin-induced-polarization
description: Guide spin-induced polarization and KNB-related PASP workflows.
---

Read `../../knowledge/workflows/l8_spin_induced_polarization_state_machine.md` first. Only read the relevant section of `../../knowledge/workflows/l8_spin_induced_polarization.md` after the current state and branch are known.

Use `../../knowledge/workflows/l8_spin_induced_polarization_run_notes.md` only for historical Lecture-8 example observations, output-family orientation, source-audit lessons, or identifying reference gaps. It cannot authorize current parameters, formal inputs, run derivation, contribution comparison, plotting, or submission.

## State Machine First
Always classify the current state using S0-S7 from the state-machine file first. The long workflow can only add details for the current state; it cannot bypass:
- S3 user-confirmed L8 polarization settings STOP.
- S4 read-only input preflight STOP ON FAIL.
- S5 explicit submission authorization.
- S6 output validation STOP ON FAIL before reporting polarization components, visualizations, force/stress contributions, ion/lattice/strain contributions, or combined analysis.

## Responsibilities
- Identify whether the user is working on pure electronic KNB / gKNB polarization or ion / lattice / strain contribution through spin-lattice coupling.
- Distinguish L8 `Model Spin_lattice_interaction` polarization-contribution runs from L2 `Model Spin_lattice_interaction` PTMC / CG magnetic-ground-state workflows.
- Explain which input package, spin configuration, local-axis / tensor data, force-constant / Born-charge / elastic files, logs or outputs are needed next.
- When the user, Claude, or Codex is modifying current-stage inputs, identify the state and branch first, then list settings normally adjustable at that stage.
- Explain adjustable items at workflow-control level only; route exact syntax, defaults, file formats, numbering rules, conditional dependencies, tensor row order, or limitations to reference.
- Treat user authorization to use subagents as read-only fact-collection authorization only. It does not confirm L8 settings and does not authorize submission.

## Runtime Hard Rules
- Before promoting an L8 candidate package to formal `input/`, overwriting formal input, deriving `runs/<run-id>/`, creating or editing submit-ready helper artifacts, preparing external task configuration, or submitting a job, run a read-only input preflight through `../pasp-verifier/skill.md` with `mode: input-preflight`.
- Required markers before any formal input / run / submission-preparation action: `USER_CONFIRMED_L8_POLARIZATION_SETTINGS=true`, `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`, and `STAGE_PREFLIGHT_PASS=true`.
- Directory inventory, template comparison, log review, and output validation are not input preflight.
- Before reporting `Ppair.xsf`, `spin3.xsf`, `GKNB_data.*`, `Total P_{ion+lattice}`, `P due to spin force`, `P due to spin stress`, or any polarization decomposition as usable, run output validation through `../pasp-verifier/skill.md` with `mode: output-validation`.
- The read-only verifier must not edit files, choose physical parameters, promote inputs, create run directories, prepare submission artifacts, or submit jobs.
- Actual job submission still needs explicit user submission authorization after preflight passes.
- Do not use Lecture-8 example values as defaults for a current material. Example packages provide file-role orientation only until current-material provenance, user-confirmed settings, and reference-backed exact writes exist.

## Route To Reference When
- The user asks for a single KNB / GKNB / spin-lattice field definition.
- The user asks about parameters such as `Model`, `GKNB.symP`, `GKNB_inter_site`, `GKNB_single_site`, `GKNB.local_axis`, `GKNB.spiral`, `GKNB.qvec`, `GKNB.spiral_plane_vec`, `SYMPREC`, `spin_lat.spin_force`, `spin_lat.Lspin_int_only`, `spin_lat.spin_int_stress`, `Read_init_spin`, `phonopy_force_constant`, `phon.lasr`, or `phon.sym_born_chg`.
- The user asks for exact formats of `PASP.input`, `%include`, `%block`, `spin3.in`, `spin_exchange.dat`, `spin_strain.dat`, `Zeff.dat`, `elastic.dat`, `cell.str`, `unit_cell.str`, `SuperCell`, `Z_values`, `isaAB`, `Spin_values`, `fig.maxk`, or `fig.mdist`.
- The user asks whether `FORCE_CONSTANTS`, `SPOSCAR`, `Ppair.xsf`, `spin3.xsf`, `GKNB_data.*`, or branch-specific XSF outputs have a precise file format or are conditionally required. Use the dedicated file cards when they cover the question; if the card does not establish an exact write rule or material-specific value, report the remaining gap and ask for user/source authority before writing exact content.
- A write depends on exact PASP field syntax, block row counts, defaults, file formats, numbering rules, tensor coordinate conventions, model-specific output files, or setting-dependent dependencies.
