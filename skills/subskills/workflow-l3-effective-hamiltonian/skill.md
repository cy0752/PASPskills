---
name: workflow-l3-effective-hamiltonian
description: Prepare and validate effective Hamiltonian construction and fitting workflows.
---

Read `../../knowledge/workflows/l3_effective_hamiltonian_state_machine.md` first.
It owns L3 execution, authorization, preflight and completion. Read only the
current-stage sections of `../../knowledge/workflows/l3_effective_hamiltonian.md`
for scientific/file details, and only the needed reference cards. Cache a short
field-to-source inventory with input hashes; unchanged fields need no repeat lookup.
Its mandatory automatic SOC and launch policy takes precedence over generic
full/off examples in script README files, templates and older workflow sections.
Such examples require the separately recorded manual-study authorization.

## Route from the actual data
- Path A: generate configurations/features in PASP from a shared basis, then pair
  external DFT energies with those configurations. The first method-1 run generates
  the requested samples and naturally writes `local_mode_PM.dat`; do not add a run
  solely to obtain that file.
- Path B: encode existing final DFT structures/magnetic states with method 6.
  Completed OUTCAR/OSZICAR files without a prior generation chain are this route.
  A missing primitive or shared basis is a prerequisite to prepare, not a reason
  to rename the route Path A. A separate POSCAR is useful but not mandatory if
  OUTCAR establishes the structure/species.
- Fitting-only: require existing, provenance-linked same-basis features and targets.
- Routing post-mortem questions require an explanation, not automatic execution.

For newly generated magnetic-Hamiltonian datasets, constrain the prescribed spin
directions during DFT, whether random or symmetry-generated. `MAGMOM` is an initial
guess; `M_CONSTR` alone does not establish active constraints. Follow
[the prescribed-spin contract](../../knowledge/workflows/l3_model_integrity.md#prescribed-spin-dataset-construction)
before DFT handoff and final-state acceptance. Direction constraints do not mandate
fixed magnitudes. Re-encoding drifted states does not by itself preserve the
sampling plan; existing Path B data remain subject to suitability review.

## Prepare first, communicate together
Use the user's existing facts and authorization. Prepare everything supported by
those facts in a clearly marked candidate package. Record values, source, effect,
and whether each is user-provided, derived, or an agent-selected modeling choice.
When the user authorizes model selection, choose and document a defensible bounded
candidate; do not pretend the chosen values were user-confirmed. Group unresolved
choices that affect validity into one question after independent preparation.
Missing physical quantities, unproved primitive mappings and upstream outputs
cannot be invented. Explicit task constraints always control.

## Implementation and handoff
The coordinator delegates actual L3 implementation to the native `pasp-helper`
(same execution provider/model and effort when configured). The helper is a writer,
not a read-only verifier; it must not spawn children. Persist the work order before
dispatch, including absolute workspace, stage, source files, known facts, unresolved
choices, runtime owner, output filenames and **consumer root**, return path, and
bounded completion criterion. Pass that file's absolute path in the actual native
tool payload. Save the returned child/session identifier and completion result.

Use foreground native Agent execution in Claude Code for dependent work when
available. In Codex use the native spawn/follow-up/wait tools actually exposed.
Do not use fabricated tool names, shell-launched replacement agents, or a background
launch followed by a final answer while work is pending. Reuse an available helper
for material repairs; do not require a fresh helper merely to acknowledge a verdict.
Prefer bounded stage handoffs (prepare basis, consume returned encoding results,
fit and publish) over an unobserved whole-workflow background job. Checkpoint before
runtime handoff and return to the same saved state when results arrive.

## Required scientific checks
The state machine gives the stage checklist. In particular:
- At `S3b` freeze the active keep/skip strategy only after checking the complete
  feature matrix produced from `ene_symbol` for exact duplicate, proportional,
  or affine-linearly dependent columns. Run this before `Model Fitting_one_order`
  and even when `I_CHECK_DATA=1` is enabled. Include all train and selection
  rows, exclude the final energy column, and record the source basis, feature
  count, fitted slope/intercept, correlation, residual tolerance, and the
  feature source/basis used for the check.
  Prefer the portable `knowledge/scripts/l3_effective_hamiltonian/check_dependencies.py`
  for this mechanical audit. It records train/selection counts, original feature
  numbers, and generated skip text; retain independent review of physical meaning
  and the native mapping.
- In free exploration or any authorized automatic evolution, enforce a hard
  cap of 150 retained fitting terms before entering PASP fitting. This cap is
  additional to the parameter-count guard `parameter_count <= 1.5 *
  fitting_data_point_count`, so the effective limit is the smaller of 150 and
  `floor(1.5 * fitting_data_point_count)`. If a candidate exceeds the limit,
  reduce it using the documented model-selection criteria before fitting;
  never fit an oversized candidate and truncate it afterward. Record the
  retained count, both limits, and the reduction rationale in the candidate
  provenance. This automatic cap does not silently alter a user-directed
  manual search, which must still stop for confirmation under the rule below.
- Before term selection can reach PASP, enforce the same size rule on the full
  candidate feature matrix: `candidate_feature_count <= floor(1.5 *
  fitting_data_point_count)`. Candidate width is the number of columns in the
  complete `ene_symbol`-derived matrix, excluding the final energy column; it
  is not the number of terms retained after fitting. A 700-row fit with 1857
  candidate columns must be rejected before PASP is launched, even if a later
  fit would retain fewer than 150 terms. Record the candidate width, fitting
  row count, integer limit, and pre-fit rejection in the provenance receipt.
- For automatic exploration, set every `Nc_p_s(I)` in `Fitting_Set_Lambda.txt`
  to at most `min(candidate_feature_count, 150, floor(1.5 * fitting_data_point_count))`.
  This is the per-round retained-parameter cap, not the candidate feature width.
  Enforce it before runtime, including probes and rehearsal fits; never search
  with a larger cap and truncate the final result afterward.
- Each `LAMBDAS(I)` is a successive multiplication factor for the growing
  regularization/search threshold, not an additive ridge penalty. Every factor
  must be finite and strictly greater than 1 in automatic exploration. A factor
  below 1 decreases the threshold and 1 leaves it unchanged. Factors themselves
  need not increase between rows. Before each fitting invocation, run
  `prepare_l3.py check-fit --input <actual-fit-directory>/PASP.input`, persist
  the receipt and stop on failure. Independent verification must inspect actual
  caps, factors and logs, not accept a written promise or staging receipt alone.
- At `S4/S5` derive skip-term numbers from the current run's
  `Data_Special_Properties_*` and `Data_Variables_Mapping_*` files; raw dataset
  column numbers are not skip-term numbers and must not be reused across runs,
  bases, or splits. Validate that train/selection widths and mappings remain
  consistent after the decision.
- In an authorized automatic run, preserve the original `ene_symbol` and
  dataset files, keep the first representative of each dependent feature
  group, generate `Fitting_Set_Term_Skip.txt` for later redundant terms, enable
  `I_HAVE_SKIP_TERM=1`, and record the detected relation and skip list in the
  fit provenance. Skipping a term addresses fitting identifiability; it does
  not establish that the physical interaction is zero.
- In a user-directed manual run, stop before changing the fit search space.
  Show the dependent feature pairs, numerical evidence, proposed representative
  and skipped terms, and the exact proposed `Fitting_Set_Term_Skip.txt` and
  `Fitting_Settings.txt` changes. Ask the user to confirm. If declined, retain
  the original data and continue only with an explicitly acknowledged
  ill-conditioned fit. Never delete or rewrite upstream `ene_symbol` files.
- Before full-study conversion, interpreting interactions or MC/MD transfer, read
  `../../knowledge/workflows/l3_model_integrity.md` for original-ID/final-state
  evidence, periodic identifiability and native parameter export/round-trip checks.
- Establish species, primitive/supercell mapping, representative sites and units
  before generating modes; use `reference/topics/symmetry_representative_sites.md`.
  Do not enumerate every supercell magnetic atom as an inequivalent site without evidence.
  Once those facts are established, `prepare_geometry.py` can render repeated
  cell/unit-cell/mode files deterministically. Its manifest is evidence supplied
  by the caller, not a symmetry or primitive-cell discovery tool.
- `Spin_values` contains one value per species, including zeros. Preserve the user's
  unit-direction convention. Variation of DFT moment magnitudes alone does not
  invalidate a direction-only model. Check undefined/poorly determined directions,
  actual mapping errors and model residuals; report limitations without inventing
  amplitude degrees of freedom.
- Automatic source-SOC-on exploration **must use restricted SOC**. Inspect explicit
  `LSORBIT` in every source OUTCAR; `LNONCOLLINEAR` is insufficient. Mixed, missing
  or contradictory evidence blocks preparation. SOC-off sources stay off. Do not
  authorize automatic full/off as an alternative for SOC-on data in helper work
  orders, probes, rehearsals, copied templates or hand-prepared inputs.
- For single-atom spin modes, use `prepare_l3.py spin --input ... --request ...
  --root ...`, followed by `check-spin --input ... --request <policy.json>`.
  Requests declare representatives, `soc`, complete `source_outcars`, flat `files`
  (actual cell/unit-cell and every dependency), and `soc_mapping` for restricted
  SOC. The state machine below defines the mapping/launch schemas. Restriction
  tuples come from compatible completed SOC=T native enumeration, never species,
  representative or fitted-column numbers. The initial automatic candidate must
  select approximately ten REAL eligible single/pair types TOTAL, covering suitable
  single-ion environments and near-range pair anisotropy, at maximum SOC order TWO.
  Default min(10, available single/pair types); count deviations need actual mapping,
  width and symmetry evidence, never silent reduction to only two singles. Twelve
  suitable types are not intrinsically wrong. Pin physical identities before first
  launch and remap native IDs for each changed basis. Execute representative body/
  radius comparisons before higher SOC orders: 15-Bohr pairs first, progressively
  smaller three/four starts, selected radius comparisons up to 15 Bohr each. Fourth-
  order pairs remain two-body. Stop after qualifying success and disclose controls
  untested. Higher SOC needs executed low-order comparisons with actual native
  train/selection residuals and physical motivation. Missing maps block explicitly.
- Before every helper-owned basis execution, including copied/manual packages,
  use `search_inputs.py --launch-request <launch.json>` with the supplied launcher
  argv and bounded timeout. It invokes the mandatory actual-input gate, records
  immutable resolved input/package/policy hashes and the process/output receipt.
  Automatic first cutoff is the positional pair `1 15`; a smaller radius requires
  an execution-backed larger-radius predecessor ledger with documented outcome,
  reason and intact input/gate/process/log hashes and initial-15 lineage. Merely
  generating a larger input or writing `status=executed` cannot authorize reduction.
  Included controls resolve before the check; duplicates/shadows of cutoff and SOC
  controls fail. Three/four starts are smaller than 15; all radii are at most 15
  Bohr and body/expansion at most four. Gates and snapshots must predate execution;
  post-hoc mirror receipts cannot authorize an earlier launch.
- TASK RUNTIME remains controller-owned: preflight the **actual handoff package**
  with `--check-launch-input ... --policy-request ... --receipt ...`, then hand it
  off without a competing run. Uninstrumented controller/raw-shell execution is
  not supported as automatic predecessor or method-6 provenance; report the
  missing same-run execution protocol precisely rather than fabricating receipts
  or bypassing the gate. Do not modify the controller to implement this skill.
- `Invariant.SOC T` plus the restriction must appear in the **same basis run**.
  `method6.py prepare` defaults to automatic enforcement, requires that run's
  `basis_execution_receipt`, compatible mapping, complete source corpus and exact
  declared dependencies. Its template and per-ID identities pin the SOC policy
  hash/tuples and native basis. Changes require a fresh basis and all encodings;
  native reconstruction still uses that hash-pinned basis and original mapping.
  Omitted types follow the source-confirmed non-SOC path; no appended zero rows.
- Explicitly authorized manual studies use a separate `manual_study` JSON record
  with mode, SOC, authorization and reason. This is not a default exploration
  escape; `automatic:false` alone fails. They also require actual externally
  supplied read-only PASP_MANUAL_AUTHORITY outside the study root as described in
  the state machine. Never create that authority in automatic work. Bare `check-spin --soc full|off` checks
  format only and never authorizes an automatic launch.
- `cell.str` is the configuration cell; PASP `SuperCell` expands that cell and is
  not the unit-cell-to-configuration relation. Check the entire transformed atom map.
- For conversion/publication read `../../knowledge/scripts/l3_effective_hamiltonian/README.md`
  under “Full-study contract”. Use `study_contract.py` for explicit full-ID splits,
  indexed features, units, runtime record checks and publication. The automatic
  isolated-test route is defined in the state machine S7: convert emits only
  train/selection, then prepare_l3.py fit-data stages those matrices with an
  explicit growing lambda schedule. Before each native fit persist check-fit and
  dependency/skip receipts. Use PASP Model Fitting_one_order; Python does not fit.
  Rehearsals obey the same split and gates. Work orders must name conversion.json,
  the native handoff JSON, frozen and evaluated output directories, and mandate
  study_contract.py freeze-native then evaluate-frozen only after train/selection
  selection ends. Publish with native_freeze/final_evaluation references and all
  required consumer-root artifacts. Never score raw test data in probes, OLS
  diagnostics or SOC selection. Prior contamination is disclosed, never undone.
  A native rewrite warning alone is not fatal: retain the reduction mapping and
  original physical model/reconstruction evidence; if the existing handoff parser
  cannot handle it, report unsupported automation rather than refitting solely to
  suppress the warning. Preserve helper delegation and controller-owned runtime.


## Runtime and final delivery
Follow the runtime owner and launcher supplied by the task. TASK RUNTIME means
prepare preflighted inputs and hand them to the controller, then inspect its actual
logs/results and repair in the same workspace. A local launcher uses no scheduler;
invoke it directly only when execution is assigned to the helper. Use the supplied
single-process environment; do not add mpirun or TCP/OFI overrides. MPI transport
initialization failure is an environment failure, not evidence of bad scientific input.
Draft-only tasks stop at checked inputs and never claim an executed calculation.

For an accuracy search, make termination and delivery observable before starting a
long PASP run. Persist one checkpoint per basis/encode/fit attempt with the exact
command, positive timeout, expected IDs, output root and status (`planned`,
`running`, `succeeded`, `failed`, or `abandoned`). Poll a foreground process or the
supported batch wrapper; never background a command and then leave the workspace
without a resumable status record. After each completed probe, stop candidates that
fail the required feature width, basis identity, finite-data or train/selection
screen. Stop the search at the first candidate that meets the authorized accuracy
and native handoff checks, or return a bounded failure with the best recorded result;
do not spend the remaining budget on unbounded retries or verifier loops.

Close the handoff at the declared consumer root in either termination state. For a
qualifying candidate, publish the frozen model, predictions, report, split and
full-ID `fgt-coverage.json`, then run `study_contract.py verify` and re-read its
receipt. For a bounded scientific failure, publish and verify every coverage or
prediction artifact that is actually complete and permitted by the task contract,
with an explicit nonqualifying status and the failed gate; never invent a model,
prediction, or coverage count. If the schema requires a qualifying model before
publication, preserve the verified coverage receipt and return an explicit `no
qualifying model` handoff instead of weakening the accuracy gate. Dispatch a
verifier only after the applicable consumer-root `publish` and `verify` receipts
exist. Missing coverage or a missing receipt is a coordinator handoff failure to
repair, not a verifier task and not evidence that the model physics failed.

Before requesting any read-only review, the coordinator must write and re-read the
consumer-root handoff: full-ID `fgt-coverage.json`, all split predictions, the
native LM/report/log, the pristine feature matrix, source/basis hashes and the
machine-readable fit handoff receipt. Run `study_contract.py publish` and
`fit_handoff.py` against those consumer-root paths first. If any artifact or
coverage record is missing, return a handoff failure with the exact path and resume
from the last checkpoint; a verifier must not reconstruct the model or assume the
coordinator's role. When candidate manifests provide
`coefficient_abs_limit`, pass it to `fit_handoff.py` so large cancelling retained
coefficients are rejected before publication. Freeze the bytes and persist the
review verdict separately; cosmetic receipt rechecks do not trigger another full
search.

Run `knowledge/scripts/l3_effective_hamiltonian/final_handoff.py --root <consumer-root>`
after publication and after `fit_handoff.py`; re-read its `final-handoff.json`.
This deterministic check covers only consumer-root paths, regular-file/directory
and symlink safety, model-manifest references, prediction-table shape, and an
explicit `qualifying` or `nonqualifying` coverage status. It does not replace
physical review, native output checks, or accuracy gates. A nonqualifying native
model is still a valid completed handoff when all mechanically complete artifacts
are present and the failed gate or limitation is preserved in `fgt-coverage.json`.
Return workflow completion separately from scientific qualification. Use `blocked`
only for a missing/incomplete handoff, interrupted runtime, or unresolved required
work; never turn a submitted model into an absent-model failure solely because an
independent accuracy gate failed.

Freeze predictions, model, manifests and report at the requested consumer paths
before final review. Store the review verdict in a separate notes file, outside the
reviewed report. After the requested checks pass, report the evidence and finish.
Cosmetic corrections, external verdict bookkeeping and byte-identical publication
need only the relevant diff/hash checks, not another full review. Scientific changes
invalidate the affected checks. Never treat a verifier pass, workflow completion or
local script tests as independent scientific acceptance.
