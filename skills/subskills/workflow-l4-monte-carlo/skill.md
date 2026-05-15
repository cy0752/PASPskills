---
name: workflow-l4-monte-carlo
description: Guide PASP L4 atomic effective-Hamiltonian Monte Carlo, PTMC, and CG workflows.
---

Read `../../knowledge/workflows/l4_monte_carlo_state_machine.md` first. Only read the relevant section of `../../knowledge/workflows/l4_monte_carlo.md` after the current state is known.

Use `../../knowledge/workflows/l4_monte_carlo_run_notes.md` only for historical Lecture-4 example observations, output-family orientation, or identifying reference gaps. It cannot authorize current parameters, formal inputs, run derivation, or submission.

## State Machine First
Always classify the current state using S0-S7 from the state-machine file first. The long workflow can only add details for the current state; it cannot bypass:
- S3 L4 model / sampling settings confirmation STOP.
- S4 read-only subagent input preflight STOP ON FAIL.
- S6 output validation STOP ON FAIL.

## Responsibilities
- Identify the user's current stage in the L4 `Model atomic_effective_H` MC / PTMC / CG workflow.
- Route L2 `Model Spin_lattice_interaction` questions to the L2 spin-lattice workflow when the target is a spin-exchange Hamiltonian.
- Explain which input package, upstream model files, run metadata, or output validation checks are needed next.
- When the user, Claude, or Codex is modifying current-stage inputs, identify the stage first, then list settings normally adjustable at that stage.
- Explain adjustable items at workflow-control level only; route exact syntax, defaults, file formats, numbering rules, or limitations to reference.
- Treat user authorization to use subagents as read-only fact-collection authorization only. It does not confirm physical settings and does not authorize submission.

## Runtime Hard Rules
- Before promoting an L4 candidate package to formal `input/`, overwriting formal input, deriving `runs/<run-id>/`, creating or editing submission artifacts, preparing external task configuration, or submitting a job, run a read-only subagent preflight through `../pasp-verifier/skill.md` with `mode: input-preflight`.
- Required markers before any formal input / run / submission-preparation action: `USER_CONFIRMED_L4_MC_SETTINGS=true`, `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`, and `STAGE_PREFLIGHT_PASS=true`.
- Directory inventory, template comparison, log review, and output validation are not input preflight.
- The read-only subagent must not edit files, choose physical parameters, promote inputs, create run directories, prepare submission artifacts, or submit jobs.
- Actual job submission still needs explicit user submission authorization after preflight passes.

## Route To Reference When
- The user asks for the definition, default, or limitation of a single `MC.input` field.
- The user asks for file explanations such as `J_best.dat`, `local_mode_PM.dat`, `Zeff.dat`, `seed.in`, or `amp_local_mode.in`.
- A write depends on exact PASP field syntax, block row counts, defaults, file formats, numbering rules, or model-specific conditional dependencies.
