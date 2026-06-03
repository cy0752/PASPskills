---
name: workflow-l7-tight-binding
description: Guide PASP tight-binding model construction and analysis.
---

Read `../../knowledge/workflows/l7_tight_binding_state_machine.md` first. Only read the relevant section of `../../knowledge/workflows/l7_tight_binding.md` after the current state and branch are known.

Use `../../knowledge/workflows/l7_tight_binding_run_notes.md` only for historical Lecture-7 example observations, output-family orientation, source-audit lessons, or identifying reference gaps. It cannot authorize current parameters, formal inputs, run derivation, plotting, Hamiltonian analysis, CLS claims, or submission.

## State Machine First
Always classify the current state using S0-S7 from the state-machine file first. The long workflow can only add details for the current state; it cannot bypass:
- S3 user-confirmed L7 TB settings STOP.
- S4 read-only input preflight STOP ON FAIL.
- S5 explicit submission authorization.
- S6 output validation STOP ON FAIL before band/DOS/gap reporting, wavefunction handoff, Hamiltonian-form claims, CLS reporting, plotting, or downstream analysis.

## Responsibilities
- Identify the user's current tight-binding stage.
- Distinguish common branches such as custom TB, SKTB, additional Hamiltonian, GSDTB / spin-dependent Hamiltonian search, flat-band CLS search, MLWF/advanced, and output validation.
- Explain which input package, structure route, orbital basis, hopping/SK/additional-H/GSDTB/CLS settings, run metadata, helper scripts, generated outputs, or validation checks are needed next.
- When the user, Claude, or Codex is modifying current-stage inputs, identify the state and branch first, then list settings normally adjustable at that stage.
- Explain adjustable items at workflow-control level only; route exact syntax, defaults, file formats, matrix dimensions, numbering rules, conditional dependencies, or limitations to reference.
- Treat user authorization to use subagents as read-only fact-collection authorization only. It does not confirm TB settings and does not authorize submission.

## Runtime Hard Rules
- Before promoting an L7 candidate package to formal `input/`, overwriting formal input, deriving `runs/<run-id>/`, creating or editing submit-ready helper artifacts, preparing external task configuration, or submitting a job, run a read-only input preflight through `../pasp-verifier/skill.md` with `mode: input-preflight`.
- Required markers before any formal input / run / submission-preparation action: `USER_CONFIRMED_L7_TB_SETTINGS=true`, `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`, and `STAGE_PREFLIGHT_PASS=true`.
- Directory inventory, template comparison, log review, and output validation are not input preflight.
- Before reporting `TB.bands`, `Eg.dat`, `energy.dat`, `dos.dat`, `wf_kpt_*-band_*.xsf`, `Htot.dat`, `cluster-*.Hform`, `local_cluster.*`, plotting files, or Hamiltonian/CLS conclusions as usable, run output validation through `../pasp-verifier/skill.md` with `mode: output-validation`.
- The read-only verifier must not edit files, choose physical parameters, promote inputs, create run directories, prepare submission artifacts, or submit jobs.
- Actual job submission still needs explicit user submission authorization after preflight passes.
- Do not use Lecture-7 example values as defaults for a current material. Example packages provide file-role orientation only until current-material provenance, user-confirmed settings, and reference-backed exact writes exist.

## Route To Reference When
- The user asks for a single TB field definition.
- The user asks about parameters such as `Model`, `USE_Slater_Koster_Model`, `Different_hop_path`, `Hop_Parameters_specified_using_site`, `Hop_Parameters_specified_using_dis`, `TB.complex_hop`, `TB.write_wf`, `TB.distance_tiny`, `TB.additional_H`, `TB.localized_state`, `TB.center_atom_localized`, `TB.rcut_localized`, `TB.eigen_localized`, `TB.find_H_form`, `TB.full_SOC`, `TB.H_spin_expand`, `TB.U`, `use_rotation_matrix`, `Ylm_form`, `overlap.distance`, `Sn_basis`, or `fig.maxk`.
- The user asks for exact formats of `PASP.input`, `%include`, `%block`, `cell.str`, `SuperCell`, `Z_values`, `Orbitals`, `orbitals_nl`, `Hop_Parameters`, `Slater_Koster_Hop_Parameters`, `GSD_TB_Spin_direction`, `TB.H_indep_var`, `H_add.dat`, or `Hmat_add.dat`.
- The user asks whether a branch needs `H_add.dat`, `Hmat_add.dat`, `cluster-*.Hform`, `local_cluster.*`, wavefunction XSF files, DOS/band plotting files, or any other conditionally required input/output.
- A write depends on exact PASP field syntax, block row counts, matrix dimensions, defaults, file formats, numbering rules, model-specific output files, or setting-dependent dependencies.
