---
name: workflow-l2-spin-models
description: Route between three independent L2 PASP spin-model workflows — find_J_path_sym (inequivalent magnetic pair search + four-state DFT input handoff), Spin_lattice_interaction (PTMC + CG ground-state search), and magnon (linear spin-wave dispersion) — and guide each through its workflow doc.
---

This subskill covers three independent L2 spin-model PASP `Model` values that share a common structural input layer (`cell.str`, `unit_cell.str`) and a common downstream data contract (`spin_exchange.dat` for the latter two), but otherwise have completely different stage chains, STOP gates, and outputs.

Do not collapse the three Models into one workflow. Each has its own workflow doc; this subskill only routes intent and enforces cross-Model contracts.

For a high-level relationship map, read `../../knowledge/workflows/l2_overview.md`.

## Inter-Model Dispatch

Classify the user's intent into one of:

| Model | When to choose |
|---|---|
| `find_J_path_sym` | User wants to find inequivalent magnetic pairs, prepare four-state DFT inputs, or fit exchange parameters from scratch |
| `Spin_lattice_interaction` | User has `spin_exchange.dat` (or just-extracted J/K/B/A parameters) and wants PTMC + CG to find the magnetic ground state |
| `magnon` | User has the magnetic ground state (in `spin3.in` form) and `spin_exchange.dat`, and wants the linear spin-wave dispersion along a Brillouin-zone segment |

If the user's intent is ambiguous (e.g., "I want to study magnetism in this material"), ask one short clarification question before routing — do not start any workflow doc cold.

If the user's request spans more than one Model (e.g., "I want to fit J and then run MC"), route to the **earliest** Model first. Cross-Model handoffs are documented in each workflow doc's `下游去向` section, not in this subskill.

## Routing Targets

- `find_J_path_sym` → `../../knowledge/workflows/l2_find_J_path_sym.md` *(full 9-section workflow; Iter 1 delivered)*
- `Spin_lattice_interaction` → read `../../knowledge/workflows/l2_spin_lattice_interaction_state_machine.md` first, then `../../knowledge/workflows/l2_spin_lattice_interaction.md`
- `magnon` → read `../../knowledge/workflows/l2_magnon_state_machine.md` first, then `../../knowledge/workflows/l2_magnon.md`

For all three Models, after dispatching, the agent should also review:
- The relevant section of `../../knowledge/reference/` for any field about to be written
- `../pasp-verifier/skill.md` when a mandatory read-only `mode: input-preflight` gate is required
- Per-Model run notes (`l2_*_run_notes.md`) only as historical observations, not current-workspace evidence

## Responsibilities

- Identify which of the three Models the user's task is about, or ask one targeted question to disambiguate.
- Once routed, identify the user's stage within that Model's workflow.
- Explain which inputs, outputs, scripts, and confirmation gates apply to that stage.
- Send the agent to reference for any planned write of a PASP input field, block, file format, numbering rule, or setting-dependent dependency, even when a workflow doc, template, example, or memory appears to show the answer.
- Block any cross-Model parameter borrowing that would silently change the physics of the run (see Cross-Model Hard Rules).

## Cross-Model Hard Rules

These rules apply across all three Models and cannot be overridden by any single Model's workflow doc:

- The structural input layer (`cell.str`, `unit_cell.str`) is shared. Changes there propagate; do not edit it without re-checking the consequences for whichever Model is currently active.
- The `spin_exchange.dat` data contract is shared between `Spin_lattice_interaction` and `magnon`, but **not identical**: this L2 `magnon` workflow does not support fourth-order pure spin-spin interactions. Do not silently inject a `Spin_lattice_interaction`-style `spin_exchange.dat` with non-zero fourth-order count into a `magnon` run. Verify the trailing fourth-order count is 0 and consult `topics/magnon_collinear_vs_spiral.md` plus `files/spin_exchange.dat.md` before writing or borrowing the file.
- The four-state method described in `topics/four_state_method.md` is the canonical handoff between `find_J_path_sym` and `Spin_lattice_interaction` (or `magnon`). It is also the reference for any `MAGMOM` / `M_CONSTR` writing the agent does. Do not write VASP `MAGMOM` / `M_CONSTR` from memory or templates without consulting that topic.
- `find_J_path_sym` produces `J.POS`, `pair_POS.NNN`, and optional `atat.NNN_Y` files; these are not interchangeable. The default four-state DFT handoff uses `J.POS` as the POSCAR and appends the matching `log.out` `MAGMOM` / `M_CONSTR` line to a user-confirmed INCAR. `pair_POS.NNN` is only for visualizing which two atoms form the pair. `atat.NNN_Y` is an advanced / internal Sc-placeholder POSCAR path and should only feed VASP when the user explicitly accepts the Sc placeholder and POTCAR strategy (see `files/atat.NNN_Y.md`).
- L2 verifier preflight hard gate: before promoting any candidate package to formal `input/`, overwriting formal input, deriving `runs/<run-id>/`, creating or editing submission artifacts / scripts, preparing external task configuration, or submitting PASP / DFT jobs for any of the three Models, run `pasp-verifier` `mode: input-preflight` as a read-only subagent check. Record `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true` and `STAGE_PREFLIGHT_PASS=true` before proceeding.
- Subagent authorization: when the runtime requires user authorization to use subagents, ask before delegation. Authorization is only for read-only fact collection; it does not confirm physical parameters, promote inputs, create run directories, prepare submission artifacts, configure external tasks, or authorize submission.
- If the verifier / subagent is unavailable after authorization, the L2 preflight gate is blocked unless the user explicitly waives the L2 hard gate. If waived, the main agent must run the same checklist locally and record the waiver, `LOCAL_PREFLIGHT_DONE=true`, and local evidence paths before any formal / run / submission action.

## find_J_path_sym Specific Rules

These apply only when the user's task has been routed to `find_J_path_sym`.

- The workflow has three stages: structural & modeling preparation → run + supercell convergence → four-state DFT handoff. Identify the stage before suggesting any change.
- Before writing any field of `PASP.input`, `cell.str`, or `unit_cell.str`, consult the corresponding reference card. The reference index for this workflow is in `../../knowledge/workflows/l2_find_J_path_sym.md` § "Reference index for this workflow."
- `Z_values`, `Spin_values`, and `magnetic_or_ligand` must each have exactly `number_of_species` entries. Non-magnetic species **must** explicitly take `0` in `Spin_values`; do not omit them.
- `cell.str` element first-occurrence order must match `Z_values` order. If the user's `cell.str` is auto-generated from POSCAR or pymatgen, verify this after generation.
- `find_J_path_sym` requires `cell.str` `%block AtomicCoordinatesAndAtomicSpecies` to be grouped by fourth-column `species_id` in nondecreasing order. The checked value is the fourth-column species id loaded into `isa`, not the optional sixth-column atom index. When expanding a primitive / unit-cell structure into a supercell-style `cell.str`, do not emit tile-by-tile interleaved atoms such as `Ni I I Ni I I ...`; group all species 1 atoms first, then species 2, and so on, while preserving correct coordinates, species ids, symbols, and valid atom indices / mapping.
- For multi-species `find_J_path_sym`, do not rely on PASP non-identity `%block SuperCell` auto-expansion from a primitive or interleaved `cell.str` unless the expanded global `isa` order is proven nondecreasing. `coor.F` expands species by cell copy, so a primitive order like `1,2,2` can become `1,2,2,1,2,2...` and fail the `find_J_path_sym` entry check. The safe route is a complete target-supercell `cell.str`, grouped by fourth-column species id, with identity `SuperCell` when that file already is the intended analysis supercell.
- The `find_J_path_sym` stage does not need its own state-machine file. Its mandatory gates are captured directly in Stage 2 of the workflow doc: read-only verifier input-preflight before run / submission actions, then the supercell convergence check after outputs exist.
- `find_J_path_sym` does **not** consume `spin_exchange.dat` and does **not** write `spin3.in`. If the user mentions either file in connection with `find_J_path_sym`, they may actually be asking about the next Model (`Spin_lattice_interaction` or `magnon`); ask for clarification.
- Output filenames (`J.POS`, `pair_POS.NNN`, optional `atat.NNN_Y`) and the `#@upup` / `#@updn` / `#@dnup` / `#@dndn` / `#@DM_*` log markers are confirmed against PASP source `Latticemodel/src/J_path_sym.f90` lines 194-350. Treat the contract as static unless a runtime observation contradicts it; in that case, record the discrepancy in `l2_find_J_path_sym_run_notes.md`.

## Spin_lattice_interaction Specific Rules

These apply only when the user's task has been routed to `Spin_lattice_interaction`. Read the state-machine before the long workflow doc.

- The workflow has three stages: input package preparation → PT MC + CG run → ground-state handoff. Identify the stage before suggesting any change, then apply the state-machine gate.
- Required inputs (must all exist before submission): `cell.str`, `unit_cell.str`, `PASP.input` (with `Model Spin_lattice_interaction` + `%include MC.input` + `SuperCell` + `Z_values` + `isaAB` + `Spin_values` + `fig.maxk` + `fig.mdist`), `MC.input` (with PT / MC / CG fields), `spin_exchange.dat` (text, from upstream `find_J_path_sym` + DFT). `seed.in` is optional. Verify all are present in the run directory before submitting.
- Key outputs the agent must know about (source-confirmed against `PTMC.F90` / `PTMC_common.F90` / `PTMC_measure.F90`):
  - `log.out`, `PASP.used_info` — metadata
  - `T_<temp>_final.*.xsf` (per PT replica) — XSF visualization of each temperature's final spin configuration
  - **`spin3_lowest.out`** (4 columns `ia sx sy sz`) — preferred downstream handoff to `magnon` when present; copy or rename to `spin3.in` after row-count validation.
  - `node_N_spin.out` — per MPI rank lowest-energy spin3 on that rank; fallback handoff if global `spin3_lowest.out` is absent.
  - `node_N_final_spin.out` / `node_N_finalspin.out` — final PTMC state on that rank, not necessarily that rank's lowest-energy state.
  - `final_ene.all` — used to identify the lowest-energy node / temperature history; do not assume the final state and lowest state are identical.
  - `*_PTMC_K.dat` family (M, Mz, Mabs, M2, E, E2, C, X, MCE, etc.) — per-temperature physical observables for the user's plotting script
- Versioned build caveat: older NiI2 lecture runs with `spin_lat.relax_str T` finished PTMC and wrote `spin3_lowest.out`, but then hit `SIGSEGV` during the CG / lowest-state post-processing path. The 2026-05-10 `paspmpi:v2` run of the same input finished gracefully and wrote `relax-spin3_lowest.out`; for current PASP submissions, still verify `log.out` for `CG finish` / `PASP is finished gracefully` before claiming CG success.
- The `inputs/Spin_lattice_interaction/run.sh` template runs `mpirun PASP.x > log.out` then `mv T_* *node* Each* final* node_data/`; the agent should preserve this convention so post-run cleanup matches downstream expectations.
- Always use an isolated `runs/<run-id>/` directory unless the user explicitly accepts baseline pollution risk. Do not submit directly from `inputs/`.
- Reference cards now cover the main Spin_lattice handoff and PTMC controls, including `PT.nblk_T`, `nblk`, `nbeg_blk`, `spin_lat.relax_str`, `opt.NSW`, `opt.EDIFFG`, and `spin3_lowest.out`. Treat exact field writes as reference-owned, not template-owned.

## magnon Specific Rules

These apply only when the user's task has been routed to `magnon`. Read the state-machine before the long workflow doc.

- The workflow has three stages: input package preparation → spinw run → dispersion plotting & diagnostic. Identify the stage before suggesting any change, then apply the state-machine gate.
- Required inputs (must all exist before submission): `cell.str`, `unit_cell.str`, `PASP.input` (with `Model magnon` + `Read_init_spin T` + `number_of_qpoints` + `%block qpoints.magnon` + `%block SuperCell` + standard `Z_values` / `isaAB` / `Spin_values` / `fig.maxk` / `fig.mdist`), `spin_exchange.dat` (text, fourth-order count **must be 0**), `spin3.in` (4 columns, row count = `det(SuperCell) × NumberOfAtoms_in_cell.str`).
- Key outputs (source-confirmed against `spinw.f90`):
  - `log.out`, `PASP.used_info` — metadata
  - **`spin_wave_E.dat`** — core physical output: each line `iq` + `na_spin` eigenvalues. Format `(I3, na_spin × f20.12)`. `na_spin = N_magnetic × det(SuperCell)`.
  - `spin_wave_H_wf.dat` — H-matrix + wavefunction details, only if `lwrite_detail=T`.
  - magnon does **not** rewrite `spin3.in`.
- The `inputs/magnon/{FM,spiral}/run.sh` template runs PASP three times (Γ→M, M→X, X→Γ), uses `sed` to rewrite `%block qpoints.magnon` between runs, then concatenates `spin_wave_E.dat` segments into `spin_wave_E_all.dat` (with `sed -i '$d'` to remove duplicate boundary points). The agent should preserve this multi-segment pattern when the user's path has more than one segment.
- Cross-Model contracts:
  - **Fourth-order spin-spin interactions are unsupported by this L2 `magnon` workflow.** Any `spin_exchange.dat` written or borrowed for a `magnon` run must have its trailing fourth-order count = 0. Verify with `tail -n 1 spin_exchange.dat` or by reading the full structure.
  - **`spin3.in` row count must equal `det(SuperCell) × NumberOfAtoms_in_cell.str`.** Count nonempty rows, because PASP-generated spin files may contain a trailing blank line. Mismatch causes silent wrong results, not necessarily a crash.
  - Default `spinw` legacy path reads two q-path endpoints and interpolates `number_of_qpoints`; use at least 2 q points for a line segment.
- Reference cards now cover `magnon_collinear_vs_spiral`, `spin_wave_E.dat`, and `spin_wave_H_wf.dat`. Treat exact `SuperCell` / `spin3.in` / `qpoints.magnon` writes as reference-owned and user-confirmed.

## Route To Reference When

- The user asks for itemized field definitions, default values, or block syntax (e.g., `Z_values`, `isaAB`, `Spin_values`, `magnetic_or_ligand`, `SuperCell`, `fig.maxk`, `fig.mdist`).
- The user asks for the exact format of `cell.str`, `unit_cell.str`, `J.POS`, `atat.NNN_Y`, or `spin_exchange.dat`.
- The user asks how the four-state method maps DFT energies to J — route to `topics/four_state_method.md`.
- The user asks how to derive `cell.str` and `unit_cell.str` from a POSCAR — route to `topics/structure_from_poscar.md`.
- The user asks about symmetry representative sites — route to `topics/symmetry_representative_sites.md` (mostly relevant when the user is preparing a downstream `Model Invariant` task, but can also help cross-check `find_J_path_sym` pair counts against expected symmetry equivalence classes).

## What This Subskill Does Not Do

- It does not answer four-state DFT VASP convergence questions; that is a VASP-side topic.
- It does not write the user's HPC submission scripts.
- It does not run subagents on its own; subagent invocation requires runtime support and (when configured) user authorization.
- It does not execute or submit any PASP / VASP job.
- It does not author or modify reference cards; reference is owned by the reference layer, not by workflow subskills.
