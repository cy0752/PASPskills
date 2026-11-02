---
name: pasp-orchestrator
description: Classify a PASP user task and route it to the best workflow subskill or reference subskill.
---

You handle task-level routing for PASP questions.

This file is a local instruction file. Do not invoke it, or any workflow file below, through a colon-qualified `Skill` tool name such as `pasp-helper:pasp-orchestrator`. When a route below matches, read and follow the referenced `skill.md` file directly.

## Classify the Request First
Route the request into one of these types:

1. workflow
- The user wants to complete a task.
- The user asks how to start, how to proceed, or what the next step is.
- The user wants to continue from a structure, model, or existing files.

2. reference
- The user asks for the meaning or syntax of a specific field, file, parameter, block, or `Model`.
- The user asks about defaults, allowed values, or caveats.

3. mixed
- The user asks both about a task and about a field or file inside the current step.
- The user, Claude, or Codex is modifying workflow inputs and asks which settings are adjustable or what they control.
- Identify the workflow first, then add only the reference detail needed for that step.

## L3 early route
For effective-Hamiltonian construction/fitting, read
`../workflow-l3-effective-hamiltonian/skill.md` now and follow its state machine.
Completed four-state DFT data that is intended to produce `spin_exchange.dat` or a
magnon belongs to the L2 spin-model route below; do not send it to the unrelated L3
local-mode workflow merely because the data came from DFT. The L3 helper is distinct
from the read-only verifier.
Persist actual handoffs and consumer paths before dispatch. Under TASK RUNTIME the
controller executes the local stage; a local launcher does not require a scheduler.

For completed four-state DFT data targeting exchange and dispersion, read
`../../knowledge/workflows/l2_four_state_delivery.md` with the L2 route. Its
prepare-first, receipt reuse and bounded-review rules specialize the generic
confirmation/reference-delegation rules below for this route. Preserve genuine
native `pasp-helper` writer delegation and scientific verifier review. Do not
restart a reference or verifier delegation solely for a deterministic mechanical
check already covered by a current receipt. Keep all supplied quartets in scope.

## Early Confirmation When Multiple Paths Are Plausible
If two or more workflows or branches are plausible, and the choice would change:
- downstream file dependencies
- directory organization
- whether formal inputs can be generated
- whether scripts, runs, or submissions may proceed

the main agent must not spend a long time deciding alone and then act as if the path is confirmed.

Correct behavior:
- state the current tentative interpretation;
- ask one short confirmation question immediately;
- before confirmation, only do lightweight fact collection such as directory inventory, energy/moment extraction, missing-file checks, or template-difference summaries;
- do not generate formal `PASP.input`, formal `cell.str` / `unit_cell.str`, batch scripts, submission scripts, or stage inputs that look ready to run.

Workflow-specific branch logic, stage logic, shared-basis confirmation, and blocking rules belong in the corresponding workflow subskill. Do not expand workflow-specific details in this outer router.

## Guardrail for "Run PASP Directly" From Only Structure Files or `OUTCAR + POSCAR`
If the user only provides `POSCAR` / an equivalent structure file, or a batch of `OUTCAR + POSCAR`, and asks to:
- generate `PASP.input` directly
- start PASP directly
- submit a job directly

do not treat this as a pure reference/template-fill task.

Stop and confirm at least two layers:

1. Target workflow / `Model`
- `find_J_path_sym`
- `Invariant`
- MC / MD / GA / TB / another workflow

2. Minimal modeling decisions for the current workflow
- which items still need confirmation in the relevant workflow subskill
- whether only a clearly marked draft can be generated
- whether multiple internal branches are plausible and need workflow-level routing

Before these are confirmed:
- do not treat template defaults as accepted formal settings;
- you may create an editable `PASP.input` skeleton or a clearly marked draft, but do not package it as a confirmed formal input;
- only proceed with template defaults if the user explicitly says this is a smoke test and accepts those defaults only to test the chain. Even then, clearly mark which key settings are not scientifically confirmed.

If the chosen workflow still has plausible internal paths, structure-input routes, or shared-basis options:
- the outer router only identifies that workflow-internal judgment is needed;
- do not decide the internal path at this layer;
- do not expand workflow-specific parameter lists at this layer;
- let the corresponding workflow subskill decide the current stage, confirmation questions, and which files may only be drafts.

## Mixed Questions and Subagent Rules
- `mixed` is only a routing order. It is not "not reference".
- If a mixed answer needs actual lookup in `skills/knowledge/reference/`, handle subagent authorization as a reference lookup.
- If the runtime requires explicit user authorization for subagents, ask whether reference lookup may be delegated before reading reference cards, file docs, topics, or modules.
- Do not skip this just because the request first went through workflow routing.

## Workflow Routing
### 1. Spin-model workflows and linear spin-wave (L2)
Route here when the user mentions:
- inequivalent magnetic atom pairs
- exchange path
- `find_J_path_sym`
- exchange-path analysis
- four-state method, J matrix from DFT
- magnetic interaction model construction
- spin-lattice interaction simulation
- `Spin_lattice_interaction`, parallel tempering MC, conjugate-gradient relaxation, magnetic ground state
- linear spin-wave dispersion
- `magnon`, spin-wave energy along q-path
- `spin_exchange.dat`, `spin3.in`

Next file to read and follow: `../workflow-l2-spin-models/skill.md`

### 2. Effective Hamiltonian construction and fitting
Route here when the user mentions:
- effective Hamiltonian
- `Invariant`
- `ene_symbol`
- fitting an effective Hamiltonian
- constructing a model from DFT data

Next file to read and follow: `../workflow-l3-effective-hamiltonian/skill.md`

### 3. Monte Carlo simulation
Route here when the user mentions:
- MC
- PTMC
- CG
- Monte Carlo
- temperature scan
- phase-transition calculation

Next file to read and follow: `../workflow-l4-monte-carlo/skill.md`

### 4. Dynamics simulation
Route here when the user mentions:
- MD
- LLG
- dynamics
- hysteresis loop
- relaxation process
- time evolution

Next file to read and follow: `../workflow-l5-dynamics/skill.md`

### 5. GA global structure search
Route here when the user mentions:
- GA
- genetic algorithm
- global structure search
- low-energy structure search
- magnetic structure search

Next file to read and follow: `../workflow-l6-ga-search/skill.md`

### 6. Tight-binding model
Route here when the user mentions:
- TB
- SKTB
- GSDTB
- hopping
- tight-binding
- flat band
- CLS

Next file to read and follow: `../workflow-l7-tight-binding/skill.md`

### 7. Spin-induced polarization
Route here when the user mentions:
- KNB
- unified polarization model
- spin-induced polarization
- magnetoelectric coupling
- spiral magnetic-order polarization

Next file to read and follow: `../workflow-l8-spin-induced-polarization/skill.md`

## Reference Routing
Read and follow `../pasp-reference/skill.md` only when the user explicitly asks for exact definitions, syntax, or source:
- meaning, default, or allowed values of a field, file, parameter, block, or `Model`
- file format, numbering rules, exact block syntax
- module definition questions such as "what is TB" or "what does GA do"
- official section coverage, source location, or reference directory lookup

Do not route directly to reference just because the request mentions `PASP.input`, `cell.str`, `Model`, `fig.maxk`, or similar names. If the user is doing a task and asks how to modify inputs or parameters in the current step, it is mixed: route to the workflow first, identify the stage and adjustable items, then use reference only for exact semantics, defaults, numbering, or format details.

## Input Modification and Parameter-Tuning Requests
- If the request is inside an identified workflow and asks which settings are adjustable now, stay workflow-first.
- Workflow answers should include:
  - current stage
  - settings adjustable at this stage
  - what each setting controls
  - the reference coverage required before editing
- Switch focus to reference only when the user needs field definitions, defaults, exact formats, or advanced semantics.
- Before writing, overwriting, or modifying any PASP field, block, file format, or numbering rule in the user directory, reference lookup is mandatory. Workflow decides what to consider; reference confirms how to write it.
- Before generating or promoting a formal PASP input file, build a field inventory for every explicit keyword, block, include, file format, and numbering rule in that file. Every item in the inventory must have a reference source or a user-provided source file that establishes its syntax and conditional dependencies. If any item is unverified, the file can only remain a draft / candidate and must not be placed in a formal input directory or run directory.
- If reference does not establish the exact syntax, conditional dependency, or numbering rule, stop and ask the user. Do not infer from templates, historical examples, similar fields, or memory.
- Once you decide reference lookup is needed, apply the subagent authorization rule above even if the original request is mixed.

## Minimal Confirmation From Structure Files
If the user starts only from `POSCAR`, `cell.str`, `unit_cell.str`, or equivalent structural files and asks to start a PASP workflow, do not skip the workflow's "confirm before starting" stage.

At minimum, confirm:
- which PASP task the user wants
- whether the structure is primitive or supercell
- which elements participate in magnetism or mode definitions
- whether cutoffs, body order, expansion order, and related modeling decisions have a scientific target

If these are not known, route to the relevant workflow and list the decisions that must be confirmed. Do not directly fill a template and prepare a run.

## Run Directory Isolation
When the user is preparing to run PASP, DFT, or workflow postprocessing scripts, default to:
- keep the clean input package in `inputs/<name>/` or another user-specified baseline directory;
- copy the whole input package into `runs/<run-id>/` before each run;
- run programs and scripts only inside `runs/<run-id>/`;
- create a new run directory for parameter changes or reruns.

Only recommend in-place execution if the user explicitly accepts overwrite risk or is doing a temporary trial. In that case, remind them to back up key inputs.

## Delegating Context-Heavy Work
When a task requires reading a lot of material, delegate bounded fact-collection tasks to a subagent when allowed so the main context stays focused. Use `../pasp-verifier/skill.md` as the common read-only contract for PASP verification tasks.

If the runtime requires explicit user authorization for subagents:
- if the request is routed as reference, ask before delegating reference lookup;
- for input preflight, output validation, structure analysis, directory inventory, log summarization, template comparison, or development-time source checks, ask before delegation when you judge it useful.

Do not say subagents can only be used when the user explicitly requests them.

If asking, use one short action question, for example:
- "I can ask a subagent to check the reference source for this field and then summarize it; should I do that?"
- "I can delegate this directory inventory to a subagent for fact collection first; should I do that?"

Good delegated tasks:
- `pasp-verifier` `mode: reference-check` for one or a few reference files, parameters, topics, or modules
- `pasp-verifier` `mode: input-preflight` for a named candidate input package and stage checklist
- `pasp-verifier` `mode: directory-inventory` for a user run directory and identification of files, likely stage clues, missing items, and uncertain residues
- `pasp-verifier` `mode: output-validation` for a named completed run or output directory
- `pasp-verifier` `mode: structure-analysis` for named `POSCAR`, `POSCAR_UC`, `cell.str`, `unit_cell.str`, or `SuperCell` relationships
- `pasp-verifier` `mode: log-summary` for long PASP, DFT, or helper-script logs
- `pasp-verifier` `mode: template-compare` for user input files against `skills/knowledge/templates/`
- `pasp-verifier` `mode: source-audit` during skill development, while runtime skills must not depend on source code

Do not delegate:
- final judgment of the user's scientific goal
- final workflow selection or cross-workflow routing
- high-risk parameter decisions without reference support
- file modification, formal input promotion, run-directory derivation, submission artifact creation, or job submission **to the read-only verifier**; a native `pasp-helper` writer follows its authorized workflow scope
- final user-facing response generation
