# L3 Effective Hamiltonian State Machine

This file owns L3 stage progression and verification. The long workflow supplies
scientific and format details for the current stage. A passed stage requires actual
files and evidence, not just a boolean written by an agent.

## Roles and persistent state

The coordinator owns routing, unresolved questions, runtime handoffs and the final
response. A real native `pasp-helper` performs implementation. A `pasp-verifier` is
an optional read-only sibling with a bounded checklist, never a coordinator/writer.
Use the native tools present in the execution environment and retain the configured
provider/model/effort. Existing authorization persists. No shell replacement agents.

Before delegation, save a work order with stage, exact input paths and known hashes,
reusable facts/reference inventory, current choices and sources, unresolved scope,
write boundaries, runtime owner, expected outputs at the **consumer root**, return
path and stop condition. Send its absolute path in the actual tool payload. Record
child/session id, result path and pending/completed/failed status in a handoff ledger.
A missing work order is a handoff error: the parent repairs it; a verifier must not
invent a task, assume coordination, or spawn a writer.

For dependent Claude Code work use foreground Agent mode when available. For Codex,
use available native wait/resume/follow-up operations. Stay active while a child is
pending; a dispatch is not completion. If interrupted by the environment, checkpoint
pending id and stage for resumption and report the actual interruption, not a
scientific failure or a completed run. Skill changes cannot remove a harness limit.
Prefer bounded stage returns before runtime handoff and after results. Do not repeat
inventory, structure analysis or reference reads if saved evidence and hashes remain valid.

Maintain one root PROGRESS file: stage/status, file roles, upstream/downstream paths,
checks/evidence, pending work and failed attempts. Stage records may link to it.
Preserve raw results, run logs, failures, retries and original input baselines.

## Verification policy and coverage

Input preflight and output validation remain distinct required checks. Each check
records target stage, actual paths/hashes, scope, result and uncertainty.

- The tested `study_contract.py` replaces routine verifier calls ONLY for full-ID
  conversion and publication: finite numbers, indexed feature rows/width, split
  disjointness/full energy-table coverage, explicit positive divisor, byte-identical
  basis copies, recorded exit code/completion marker, CSV targets/units/metrics,
  declared consumer JSON path references, published bytes and receipt identity.
- `prepare_l3.py` adds tested checks for ordinary FDF include/first-declaration
  resolution, single-atom spin mode format/count/numbers/species activity and explicit
  source-aware restricted/off automatic SOC (separate recorded manual full/off), plus conversion-pinned full train/selection staging and lambda shape.
  See the scripts README for supported syntax and limits. These receipt-covered
  checks need no duplicate verifier call; unsupported cases retain explicit review.
- These checks do not prove convergence, species/primitive/site identity, general
  FDF semantics/dependencies, scientific suitability, coefficient mapping, lack of
  prior test leakage, or truth of a report. Review those against source evidence. Use a bounded
  native verifier for uncovered format/semantic checks, scientific ambiguity/source
  conflicts, or an explicitly requested independent check. Bundle related known
  preflight questions (including planned fitting settings) in one work order rather
  than one verifier per field. Resolve validity blockers before dependent execution.
- New runtime results still need output/log inspection, including warnings/errors;
  a zero exit code and completion marker alone are insufficient scientific validation.
- `fit_handoff.py` covers native LM/report physical IDs and full train/selection
  prediction round-trips for its supported formats. `periodic_alias.py` diagnoses
  only supplied two-body orbit geometry in diagonal cells. Read
  `l3_model_integrity.md` and the scripts README before using these scopes.
- `prepare_geometry.py` covers deterministic rendering of a caller-supplied
  Cartesian cell/site/representative manifest, including finite-value, species,
  active-spin, and new-output guards. `check_dependencies.py` covers the
  train+selection matrix dependency audit and original-column skip-file rendering.
  These scripts replace repeated handwritten generation and ad hoc rank probes
  only within their recorded scopes; they do not choose physics, establish
  symmetry, prove primitive mappings, or replace native fit/output review.
- Reuse a check only for its recorded scope and unchanged inputs/dependencies.
  Changed basis, structure, effective settings, targets, feature map or splits require
  affected checks again. Never label an unsupported check as script-covered.
- An unavailable required native review remains unperformed; report its exact scope.
  Do not repeatedly ask for authorization already supplied by the task.

## S0 — Route and delegate

Inspect the target directory, not sibling examples. Existing final DFT results
without a generation chain imply Path B/method 6. Path A means PASP generates the
samples before DFT; missing shared-basis files do not change Path B to Path A.
Record the runtime owner: controller-managed, explicitly helper-run, or draft-only.
Delegate implementation promptly after this small inventory; do not duplicate all
helper analyses in the coordinator before dispatch.

## S1 — Inventory all samples and establish the structure

Record the full expected ID set from the supplied data, file naming convention,
final converged TOTEN and moment/position source for every ID, convergence evidence,
and species order. Reconcile energy-table values with final DFT values using a
precision-justified tolerance. Preserve original data; if a parser expects a different
filename layout, create an explicit ID-to-source staging manifest, never reindex by
glob order. Report every missing, failed or unconverged sample; do not silently drop it.
For supported OUTCAR data, use `prepare_path_b_inputs.py` directly: prefix/suffix
files and numbered directories share a duplicate-checked inventory, final-state
packages and source ledgers. Read its bounded contract once. Compare manifest IDs
against the independently expected corpus before advancing; the extraction count
is not proof that the task's full dataset or DFT convergence was covered.
For full-study spin/OUTCAR conversion require source/encoding identity records as
specified in `l3_model_integrity.md`: same original ID, final TOTEN, and actual
structure/magnetic-input bytes. Unsupported sources need equivalent provenance review.
After DFT, a changed magnetic state requires same-basis method-6 feature re-encoding.
The encoding record pins pre-run structure/moments/basis and post-run ene_symbol;
updating an input file alone must not make a stale pre-DFT feature reusable.
Inventory the source constraint/relaxation protocol and any missing evidence.
Existing unconstrained Path B samples are not automatically invalid; assess their
suitability using the actual states under
[the prescribed-spin contract](./l3_model_integrity.md#prescribed-spin-dataset-construction).
For new prescribed-spin samples, re-encoding alone cannot approve direction drift
or silently replace the sampling plan.

Establish primitive lattice and configuration-cell relation with integer matrix,
determinant, volume and species-count ratios, and periodic atom mapping/residual.
Record tolerance and coordinate conventions. Transform fractional coordinates with
the correct matrix direction when changing lattice; verify Cartesian positions.
For structured primitive/configuration inputs, run the portable
`knowledge/scripts/l3_effective_hamiltonian/structure_mapping.py` check and retain
its receipt before selecting an energy divisor or generating modes. A failed or
ambiguous mapping blocks dependent input generation; the receipt does not discover
symmetry or establish scientific suitability.
Use existing `rebase_unit_cell.py --relation ...` for a supplied candidate mapping;
it does not discover the primitive or prove site equivalence. PASP `SuperCell`
expands `cell.str`; it is not this relation matrix. Evidence must justify energy
normalization separately. Ambiguous mapping blocks dependent input generation.

## S2/S3 — Model choices and representative sites

Prepare a candidate table: magnetic species/Spin_values, body order and per-order
cutoffs in Bohr, expansion/strain/phonon powers, SOC strategy, configuration cell,
primitive/mode frame, mode representatives and provenance, and method controls.
Each value is user-provided, derived, or an agent-selected candidate with rationale.
Use existing model-selection authorization; do not require field-by-field approval
of supported routine choices. Group genuinely unresolved scientific conventions in
one question, while completing independent preparation. Do not invent missing
quantities or upstream results; unresolved inputs remain candidates, never confirmed models.

Use symmetry-inequivalent sites with element mapping, multiplicity, tolerance and
source. Each single-atom spin mode starts with `1 spin`, then a species-id line,
then position and vector; x/y/z modes give three per representative. No blank line
between the count and first mode. Multi-atom displacement modes use N_atom, a separate
species list, then one x y z dx dy dz row per atom; displacement vectors are Cartesian.
All magnetic atoms may be representatives only with evidence they are inequivalent
in the mode primitive. Read the specific mode/structure reference cards before writing.

For automatic exploration, every explicit source LSORBIT=T requires Invariant.SOC T
and a same-run special_SOC restriction. Full SOC is only a separately recorded,
explicitly authorized manual study. Source LSORBIT=F stays off; missing/mixed
LSORBIT blocks. Resolve current-basis interaction-type indices (including one-body
indices) from compatible completed SOC=T native evidence; never use species or
representative ids or an SOC=F enumeration. Never launch unrestricted SOC to get
past an unsupported mapping. Spin_values has one entry per species including explicit inactive zeros.

Automatic SOC starts at maximum order TWO on approximately ten REAL eligible
interaction types TOTAL, generally covering inequivalent single-ion environments
and suitable near-range pairs. Count native types, not species, powers or fitted
coefficients. The default count is min(10, available single/pair types). Deviations
(including twelve suitable types) need a hash-pinned count assessment with actual
selection, width, training rows, symmetry evidence and physical rationale. Two
single-body types alone do not fulfill the policy when eligible pairs exist.

Pin physical orbit/environment identities before the first launch. For a changed
basis, obtain compatible native SOC=T evidence and remap tuples to those same
physical keys; never copy stale IDs or run unrestricted enumeration for discovery.
First execute 15-Bohr pairs, then progressively include smaller three/four-body
starts (6/4 Bohr are suggestions), and compare representative radii up to 15 Bohr.
A fourth-order pair remains two-body. Keep SOC selection/order and expansion fixed
across comparisons; record unavoidable confounders. Stop early after a qualifying
model; disclose untested controls. No exhaustive grid is required.

Before higher SOC order or family expansion, supply executed bounded body/radius
comparisons, actual native train/selection predictions and pristine reconstruction,
width/conditioning evidence and physical operator/symmetry motivation. Infeasible
branches need concrete mapping, symmetry, width or runtime evidence. Pooled R2
alone cannot justify broad SOC. Inspect actual operators and hashes; identical PM
bytes do not establish reduction. Initial symmetry exceptions do not silently
permit fourth order: the higher-order gate still requires comparison evidence.
Honor user unit-vector semantics; moment magnitudes alone do not establish invalidity.
Retain norm diagnostics and investigate undefined active directions and residuals.
Check training-cell periodic aliasing before costly sample generation. Later column
correlation cannot establish infinite-lattice equivalence; record identifiable
coupling combinations and target-cell limitations before dropping correlated terms.

Path A needs a supported target DFT cell and sample count. Its first method-1 run
should generate the requested samples while producing the reusable basis; do not
insert a basis-only pre-run. Displacement amplitudes need physical/mode evidence.
Production DFT INCAR/KPOINTS/POTCAR settings must come from the user or project.
New prescribed-spin magnetic datasets require active direction constraints before
DFT handoff, for random and symmetry-generated samples alike. Follow the linked
prescribed-spin contract for effective activation, target/site/frame checks and
direction-versus-magnitude semantics. `MAGMOM` initialization or `M_CONSTR` presence
without active constraints fails this preflight. Missing supported settings block
the handoff; this is not a fallback triggered by SCF failure.

## S3b — Freeze study design before fitting

Record full IDs, split method/seed or explicit IDs, divisor with structure evidence,
units, candidate bases, lambda schedule, I_CHECK_DATA and active keep/skip strategy.
For automatic exploration each lambda factor must be finite and greater than 1;
it successively multiplies the regularization/search threshold, rather than adding
a ridge penalty. A factor below 1 reduces the threshold and 1 keeps it unchanged.
The factors need not increase between rows. Set every `Nc_p_s(I)` to at most
`min(candidate_feature_count, 150, floor(1.5 * fitting_data_point_count))`.
The candidate-width limit is separate: 740 features may be admissible, but 740
retained terms are not. Probes and rehearsal fits obey the same cap.
For model selection use nonempty disjoint train/selection/test partitions covering
all samples. Group related samples when needed to avoid leakage; no fixed ratio is
scientifically universal. Freeze the split file before fitting any candidate.
Only train fits coefficients; selection chooses models/hyperparameters. Keep test
out of PASP's prediction set while selecting. Inspect test only after freezing the
model; do not tune again from test results. This applies to **every rehearsal or
pilot fit**, not only the delivered pipeline. Freeze first, then use train/selection
for all fitting trials. Prior test access is contamination to disclose; discarding
a model or restaging files does not restore an untouched holdout. A different user-requested study design
needs an explicit design and appropriate checks; the three-split script does not
claim to support it. Keep/skip files are active only when the corresponding flag is on.

## S4/S5 — Generate candidates and preflight

For automatic single-atom spin searches, batch the repeated basis input edits with
`search_inputs.py --manifest /work/search.json --root /work/basis-inputs` (sibling
of `prepare_l3.py`). The manifest declares `input`, explicit source-consistent `soc` (`restricted`/`off` for automatic exploration),
`files` mapping package names to input sources (including `cell.str`, `unit_cell.str`),
`one_body_cutoff_bohr`, `higher_body_cutoffs_bohr` with keys `3` and `4`, and a
bounded `candidates` list with `body_order`, `expansion_order`,
`two_body_cutoff_bohr`, with an optional candidate-specific `soc_mapping`.
Start with body two and pair radius 15 Bohr, expansion at most four. Add body
three then four at smaller radii; per-candidate `higher_body_cutoffs_bohr` can
vary those radii. All radii must be positive and at most 15 Bohr. The field named
`one_body_cutoff_bohr` is retained for compatibility but must be 1: it is the
fig.mdist control flag. Prepare at most twelve candidates, keeping expansion and
physical SOC policy fixed. Multiple body/radius changes require `confounders`.
The generator removes shadowed controls and produces all inputs deterministically;
prepared configurations never authorize execution or demonstrate comparisons.
Evaluate each predecessor before running a lower-radius candidate. At each step
regenerate the native basis, re-encode all IDs, repeat width/dependency/skip checks,
run actual-package `check-fit`, and refit. Preserve the generator receipt unchanged;
copy its candidate entries to a separate attempt ledger and fill that ledger's feature and
parameter counts, conditioning, train/selection metrics, skip mapping, failures
and qualified timing from actual evidence. Hashes include physics, flattened FDF
and declared dependency bytes; equal dimensions never authorize reuse.

This tested replacement covers only deterministic input construction and sequence
guards; do not ask a verifier to repeat those fields for unchanged hashes. It does
not cover physical choice of higher-body radii, source/site identity, dependency
analysis, actual native outputs, cache reuse, or accuracy. Start SOC exploration
with the single/pair total-type order-two policy above. Restricted support cannot invent mappings: without
compatible verified evidence, block and record the exact missing evidence. Each
changed candidate needs its own compatible mapping; batch generation fails closed
if one shared mapping is incompatible with a different cutoff/body/order. Automatic routes remain within body/order four and all radius maxima 15 Bohr.

### Mandatory automatic policy and launch records

The coordinator must copy these constraints into the actual helper work order:
complete LSORBIT inspection; restricted SOC when source SOC is on; verified actual
body/type mapping; same-run mapped single/pair order-two special_SOC (or supported
hashed exception/extension); first pair `1 15`; launch wrapper and
receipt; unchanged physics in method-6, pristine fitting and native reconstruction.
Neither scientific suitability nor speed excuses full/off fallback.

Spin/policy request fields: `soc`, `source_outcars` (complete source corpus),
`files` (flat package-name -> source path; include cell.str and unit_cell.str),
`soc_mapping` (restricted only), plus `representatives` for spin generation.
The mapping JSON has these required fields, plus the optional stage fields shown:

```json
{
  "basis_input": "verified-run/PASP.input",
  "basis_log": "verified-run/log.out",
  "basis_exit_code_file": "verified-run/exit.code",
  "files": {"cell.str": "verified-run/cell.str", "unit_cell.str": "verified-run/unit_cell.str"},
  "selected": [["actual body", "actual type", "justified maximum order"]],
  "type_limit": "declared small integer",
  "order_bound": "declared low-order integer",
  "order_rationale": ["reference and current-basis justification for each tuple"],
  "stage": "initial",
  "cap_convention": "selected_rows"
}
```

Replace explanatory strings with justified integers; the example is a schema,
not runnable physics. `selected` is a unique targeted subsequence of eligible
native cluster ordering, not a required prefix. Counts/identities are verified against the complete native log table;
maximum orders cannot exceed the declared bound or expansion order. All
basis-defining effective controls and declared dependency hashes must match the
verified run, excluding documented method/read/nstr/seed and restriction controls.
One SOC=F run, a partial table, invented IDs or equal matrix dimensions is not a
mapping. The reusable script does not choose a scientifically valid order from
an arbitrary rationale string; review that decision with the reference cards
`Invariant.SOC.md` and `local_mode.special_SOC.md` once, and persist the rationale.

Omitted `stage` defaults to `initial`. Every initial selected row has body one
or two and maximum order two, with `order_bound: 2` and `type_limit: len(selected)`.
Default count is min(10, eligible single/pair types). Any deviation needs
`stage_evidence` pinning a JSON with `selected`, `reason`, `symmetry_evidence`,
`feature_count`, `training_rows` and pinned `references`; width must pass before
fitting. Both available body families must be represented or explicitly justified.
Every automatic map needs `policy_identity: {path, sha256}` pinning JSON with
`selected`, `basis_definition_sha256`, `basis_log_sha256`, unique `physical_keys`
and pinned `references`. These are scientific orbit identities, not index aliases.

Higher-order `symmetry_exception` and `extension` evidence contains `reason`,
`operator_interpretation`, `symmetry_evidence`, `references` and
`radius_body_comparisons` (2–12 entries). Each comparison pins `execution` and
`assessment`. The assessment pins `fit_manifest` accepted by fit_handoff,
`fit_preflight` from actual check-fit, matching `basis_sha256`, `feature_count`,
actual `train_r2`, `selection_r2`, `train_residual`, `selection_residual`,
`conditioning`, `identifiability`, `directional_deficiency`, `controls_comparison`
and `test_used_for_selection: false`. Metrics are recomputed from native
predictions. The preflight must match actual settings and pristine matrices even
when PASP subsequently rewrites its working matrix. Comparisons include 15-Bohr
pairs, multi-body evidence for bodies three/four (or evidenced infeasibility),
and more than one radius within a body (or concrete infeasibility).
`pruned_controls` declares body, category (width/symmetry/mapping/runtime), reason
and pinned references; width/runtime branches additionally pin `execution`.
Only concrete inability to compare radii permits `radius_comparison_infeasible`.
An extension pins `predecessor`, `assessment`, and `family` (pair_bilinear,
single_fourth, advanced), preserving previous operators and non-SOC controls.
Advanced targeted orders at most four require `lower_stages_exhausted: true`;
counts above ten need `cap_extension_reason`. A symmetry exception also pins
`second_order_forbidden_or_absent` and `lowest_allowed_tuples`. Parser integrity
cannot decide whether these physical interpretations are warranted; review them.

Helper-owned launch request:

```json
{"input":"run/PASP.input", "policy_request":"policy.json",
 "command":["bash", "supplied-local-launcher.sh"], "timeout_seconds":600}
```

Run `search_inputs.py --launch-request launch.json`. For a documented reduction,
add `predecessor_ledger` pointing to a list (or object with `attempts`) of entries
with `status: executed`, `cutoff_bohr`, `effective_input_sha256`, `receipt` pointing
to the wrapper's `basis-execution.json`, and `reduction_reason` describing the
actual previous outcome and reason. Receipt paths resolve against the ledger.
The wrapper consumes the same PASP.input and writes read-only `basis-gate.json`,
`basis-effective.input`, `basis-process.json`, `basis-execution.json`, `exit.code`
and hashes the log/native PM. Fresh runs cannot inherit native PM caches. Failed
or timed-out attempts remain recorded but do not certify native outputs. A real
larger-radius attempted process may justify a documented reduction; generated-only,
missing, changed or standalone self-attested receipts fail. Full evidence-tree
fabrication by an actor able to rewrite all hashes is not cryptographically
prevented; inspect the supplied process/timing provenance independently. Launcher
intervals are not direct PASP intervals and cannot qualify a speed measurement.

For `method6.py prepare`, additionally supply `basis_input`, `basis_file`,
`basis_log`, `basis_exit_code_file`, `basis_execution_receipt`, `policy` (`reuse`
or `rebuild`), and `dependencies` matching `files`. Automatic is the default;
source set/hashes must match the complete inventory at staging, the actual native
PM must match execution, and restriction/policy identities must agree. Encoding
checks template bytes before each helper process and afterward, and carries SOC
policy hash/tuples in template, batch, pre-run and per-ID encoding records. Preserve
those records with the freeze manifest; the existing native reconstruction gate
still independently validates basis/column IDs, intercept and predictions.

Genuinely manual studies require `automatic: false`, a `manual_study` record
(mode, matching SOC, actual user authorization and reason), and externally
provided `PASP_MANUAL_AUTHORITY`. That environment path must be a regular read-only
file outside `study_root`, with `mode: explicit_user_manual`, matching `soc`,
`authorization`, and the actual `study_root`. It is supplied by the user/runtime,
never created by the executor. The file check is not cryptographic authentication.
This automatic experiment has no such user decision; helpers may not manufacture
one, chmod their own authorization or reinterpret autonomous choices as manual.

Supported launch coverage is the helper wrapper and controller preflight handoff.
TASK RUNTIME remains controller-owned: call `--check-launch-input` with
`--policy-request` on the actual package, hand off, and inspect returned outputs.
Uninstrumented controller/raw-shell launches cannot provide this same-run execution
protocol for automatic method-6 or reductions and are blocked there; report that
precise limitation. Unsupported FDF redirects, quoted/include syntaxes, multi-atom
mode routes and undeclared conditional dependencies require a supported extension,
not a bypass. Flat dependency completeness is caller-declared and still a reviewer
responsibility outside known script scope. Earlier/frozen full-SOC artifacts are
historical evidence; do not mutate or retrospectively relabel their acceptance.

Regression coverage: `test_prepare_l3.py`, `test_search_inputs.py` and
`test_method6.py` exercise valid restricted preparation -> actual synthetic argv
launch -> full synthetic encoding, source-SOC-on full/off rejection, missing/mixed
LSORBIT, mapping/order/geometry mismatch, omitted/mismatched restriction, included
and shadowed controls, first 15 vs initial 8, fabricated/missing/mismatched receipts,
legitimate recorded reduction, complete source corpus and policy/cache identities.
These replace repeated verifier checks only for unchanged covered input bytes and
receipt fields. Physical order justification, geometry, aliasing, native restricted
output correctness, stability, full-data accuracy and remaining output risks still
need their existing independent checks. Synthetic launches are not PASP acceptance.

Historical parent validation record (superseded by the revision record below): `python3 -B -m unittest discover -s
candidate/knowledge/scripts/l3_effective_hamiltonian -p 'test_*.py'` completed
124 tests in 4.128 seconds with `OK`, including missing mandatory execution hashes
and unrecorded native-output rejection, explicit SOC-off source preservation, mixed-corpus rejection and glued three-digit native type parsing. A launcher log without the native header/start cannot authorize a reduction. A separate read-only parser check accepted
the complete interaction tables from three captured successful native basis logs;
their different type lists reinforce the need for current-basis mapping. No native
calculation was submitted during these checks. Controller evaluation must establish
native restricted execution, full-data accuracy and model acceptance; no measured
workflow speedup or new executor-profile pass is established by this local record.

Source assumptions (read-only inspection, no runtime source-tree dependency):
`Latticemodel/src/local_mode_SOC.F90::set_special_SOC` reads count +
(body,type,max_order); `special_SOC_clus` passes max_order+1 to
`adjust_no_SOC_term`, while omitted types use the ordinary non-SOC path.
`local_mode.F90` applies this during the same basis generation.
`local_mode_para.F90::print_lm_interaction` emits `I5,2I3,4I5`; the parser uses
fixed widths so glued three-digit type IDs are handled. Require complete native
cluster count/numbering and completion/exit evidence. A reader-format change blocks
parsing until the implementation and discriminating tests are updated. References
and mapping/input/log/exit evidence hashes are pinned into policy identity; installed
executable equivalence and actual native restricted outputs remain runtime checks.

Reader assumptions: `fig_data.F90::read_fig_data` reads `md_a(1:maxk)` from
`fig.mdist`; `mode_coupling.f90::read_invariant` reads `Invariant.power` (default 4).
Inspected source SHA256s respectively
`9b38ceb56ec8b99e5a0bfd8f458bf709fb46f580574f7489de65913d9274e80c`,
`f00f5b803389e60d4fe6c82b48bf88b0e442826f30b2e2fabe7110a2f67cf575`.
Scripts need no source tree; synthetic tests do not prove equivalence to the
installed executable. The controller validates actual PASP results.

Prepare a complete candidate package using reference-backed formats. Keep a field
inventory for every explicit effective keyword, block, include and conditional file.
Resolve duplicate/inactive declarations and includes according to the reader;
preserve unrelated settings. For the supported single-atom spin route, use
`prepare_l3.py spin` with established representatives and explicit SOC policy, then
`check-spin --request <policy.json>`; it handles ordinary includes and removes shadowed replaced fields.
Read its bounded contract once; cache receipts and inventory instead of re-reading
all cards for unchanged fields. Other FDF/dependency checks remain source-backed.
Check scientific provenance and cross-file consistency before promoting inputs.

Shared basis: real nonzero-volume cell/unit-cell files, mapped axes/species/sites,
Z_values (element labels, not species ordinals), Spin_values length, correct mode
count/shape, fig.mdist positional values, SOC dependencies, method and process count.
Method 6: current same-basis local_mode_PM.dat, unchanged basis-defining settings,
per-ID distortion.pos and conditional distortion.MAGMOM, atom order and cell match.
For supported source-aware single-atom spin SOC, use `method6.py prepare` from the
actual successful basis run, not its earlier draft. It preserves the established
model and changes only method/read/nstr_random controls with FDF include precedence.
Use the README's `stage`/`collect` route for controller-owned runtime, or `batch`
only for explicitly helper-owned execution. Pin native PM and pre-run state hashes.
Probe before the full batch; zero modes/features, mismatched native PM, failed
launcher or unresolved warnings block dependent work. A same-input rebuild policy
is a bounded explicit recovery, never a reason to alter SOC or call equal counts
proof of basis identity. Record each attempt and stop if the single rebuild probe
does not establish native basis identity. Unsupported routes retain reference-backed
preparation and independent checks. Receipts replace only their named mechanical
scopes, not geometry, modeling, aliasing or independent scientific acceptance.
Fitting: real cell.str (never an empty placeholder), positional Fitting_Settings.txt,
Fitting_Set_Lambda.txt, active keep/skip files with current feature numbering,
finite equal-width train/selection matrices and matching row maps; keep test separate.
Use the full-study script README for conversion. It preserves every feature and
normalizes targets once; do not delete columns to mimic an old example. Pin the
conversion receipt and use `prepare_l3.py fit-data` to stage full train/selection
rows and explicitly chosen lambdas; it never stages test. Complete the remaining
fitting inputs/settings preflight before runtime. The fitting engine is PASP
`Model Fitting_one_order`, not a substitute external Python regression.
For every automatic fitting invocation, run `prepare_l3.py check-fit` against
the actual `PASP.input` and persist its receipt after all edits. Failure blocks
runtime. This checks actual matrices, per-round parameter caps and factors;
dependency/skip strategy and scientific checks remain separate required scopes.

Record passed script scopes and source-backed/independent remainder checks. Any
failed required item blocks that dependent stage until repaired. Draft-only tasks
finish here with checked inputs and remaining uncertainty, without runtime claims.

## S6 — Runtime handoff

Promote passed inputs to an immutable baseline and derive an isolated run directory.
For TASK RUNTIME, save exact input path, stage, expected outputs and dependencies;
the controller invokes the supplied local launcher and returns logs/results for
inspection and repair. Do not launch a competing calculation. If the task instead
explicitly assigns execution to the helper, invoke that launcher directly in the
run directory. No scheduler is required by a local task. Default to one process;
MPI/special-SOC paths require build-specific evidence before extra ranks.
Never replace the maintained environment with mpirun or TCP/OFI overrides.

## S7 — Validate results, publish, review, finish

Check actual completion, warnings/errors, expected outputs and provenance at each
stage. A basis run must produce the expected nonzero modes and parameters;
exit zero/graceful finish alone does not prove the mode block was read correctly.
Record failed IDs and repair only affected work. Aggregate by explicit IDs,
not filename position. Conversion requires every expected ID with matching basis
and feature width. Repeated full encoding merely for reassurance is unnecessary
once required checks pass; new changes or discrepancies justify additional runs.
For newly generated prescribed-spin DFT samples, check electronic convergence and
final per-site target-direction agreement separately under
[the prescribed-spin contract](./l3_model_integrity.md#prescribed-spin-dataset-construction).
Investigate/fix constraint failures and recalculate affected samples as needed;
method-6 identity repair alone does not accept lost sampling configurations.

If I_CHECK_DATA rewrites columns, preserve pristine converted matrices and the
PASP variable mapping. Freeze coefficients, intercept convention and original-to-
reduced feature mapping. Reproduce PASP training/selection predictions from that
frozen representation before evaluating test; never guess XM or report indices.
Report per-split counts, units, RMSE/MAE/R², residual evidence, model/basis and limitations.
No fitting completion claim implies readiness for MC/MD: that handoff separately
needs same-basis parameters, modes/masses, initialization, conditional charges and
production simulation settings.
For L3 interaction analysis or MC/MD transfer, follow `l3_model_integrity.md`:
prefer the selected native `_LM.txt`, exclude the energy constant, and check the
actual J_best against all train/selection predictions using preserved full features.
Use `fit_handoff.py` for supported files; do not copy internal XM indices. When
the manifest supplies `fit_log` (and, when available, `fit_exit_code_file`), the
handoff requires explicit native completion and rejects actual fatal diagnostics.
`NEED TO REWRITE DATA` alone is not fatal. Supply `rewrite_mappings` as an ordered
list of the actual run's `Data_Variables_Mapping_(1st Reducing)_<width>.txt` files,
plus `fit_exit_code_file`. Mapping rows are native `reduced:original` records;
counts, original IDs and chain must match logged widths. Preserve pristine full
train/selection matrices. Handoff verifies original nonzero LM IDs, coefficients,
separate offset and reconstruction. Never refit just to remove the warning or
insert ID zero into LM/J. Method-6 retains its separate failure check.
Earlier test
access remains contamination regardless of representation repairs.
Prior causal claims contradicted by new outputs must be corrected in active notes
and downstream handoffs, with failed attempts retained as history.

Publish the exact task-required filenames at the agreed consumer root using
`study_contract.py publish`, including predictions, report and any coverage manifest.
Include the frozen model/split and evidence or explicit provenance links. Check all
consumer-manifest path fields through the publication manifest's `references` list;
validate other task-specific schema fields separately. At the task-schema boundary,
require the exact allowed/required keys and container/value types; keep metadata
in a separate receipt when extra fields are forbidden. Relative path values must
resolve literally from the consumer root, without placeholder prefixes. Validate
these contract facts before claiming delivery, independently of model acceptance. Re-read the published copies,
not only the run directory. A receipt records byte identity and mechanical checks,
not a scientific verdict. Do not embed this receipt or a future verdict in its own
hash inputs.

For automatic fitting with an isolated final split, use the deterministic native
pipeline instead of hand-writing split predictions or a self-asserted isolation
boolean. `convert` validates all expected samples but emits train/selection only;
`test.txt` is deliberately absent. Fit and choose candidates on those two splits.
The conversion still validates test encoding/source identity and features for
coverage; that validation is not permission to score test targets.

```
python "$PASP_SKILL_ROOT/knowledge/scripts/l3_effective_hamiltonian/study_contract.py" convert --manifest study.json --root conversion
# fit-data, complete dependency/skip audit, check-fit BEFORE each native fit;
# native PASP execution remains with the authorized executor/controller.
python "$PASP_SKILL_ROOT/knowledge/scripts/l3_effective_hamiltonian/study_contract.py" freeze-native --conversion conversion/conversion.json --handoff handoff.json --root frozen
python "$PASP_SKILL_ROOT/knowledge/scripts/l3_effective_hamiltonian/study_contract.py" evaluate-frozen --freeze frozen/native-freeze.json --root evaluated
```

`handoff.json` uses the existing fit_handoff schema: basis_file, lm_file,
fit_report, fit_log, fit_exit_code_file, prediction_atol, coefficient_atol,
optional coefficient_abs_limit, and datasets for train/selection with matrix and
native predictions paths. Paths resolve relative to that JSON, not CWD. Freeze
executes the native handoff check, binds pristine train/selection matrices to the
conversion, then writes native_LM.txt, native_fit.txt, local_mode_PM.dat, log.out and
native-freeze.json. Evaluation uses original native physical IDs and a separate
offset, verifies source/basis/feature/split hashes, and produces every split CSV,
full-pristine-matrix.txt, full-row-ids.json and final-evaluation.json in one batch.
No Python fit replaces PASP. A terminal `.test-opened-<split hash>.json` lock next
to the supplied split binds the first evaluation to frozen bytes. Failed evaluation
retains the lock; byte-identical retry is allowed, another freeze is rejected.
Do not remove/copy around this lock or redraw a mandated split to resume search.

In the native automatic publication manifest, declare `native_freeze` and
`final_evaluation` paths, list all frozen native and evaluation files in `artifacts`
at the required consumer names, and include the task-required root_artifacts and
references. The publisher checks unchanged model/evaluation bytes and freeze/split
identity in addition to coverage, target units and metrics. Generic publication
remains available for other contracts and honest coverage-only failure delivery;
it does not certify a native model or isolation. Preserve native-freeze.json and
final-evaluation.json as provenance artifacts. Reports and external verdicts are
separate from the frozen byte set; bookkeeping never authorizes another search.

Replacement-check scope: deterministic indexed-feature parsing, full-ID splits,
finite numbers, target conversion, native physical-ID/coefficient agreement,
train/selection reconstruction, retained/width caps, native completion, frozen
prediction generation and publication byte identity are tested locally. Do not
send those unchanged covered facts through another verifier. Review physical
assumptions, symmetry/operator meaning, source mapping, residuals, uncertainty,
encoding replays, native outputs beyond the supported parser and actual chronology
independently. Arbitrary raw-source reads/copied split files are outside this
script's access control: history audit must still detect contamination, as it did
in the recorded failed search. No receipt boolean can erase it. Tests are synthetic;
controller-owned scientific/accuracy gates and actual execution remain mandatory.

The publication handoff is a hard boundary for review: first write the publication
manifest with paths relative to the consumer root, run `publish`, then run
`verify` against that same root and receipt. Give a verifier the absolute consumer
root, receipt path, and the exact frozen artifact list. Do not dispatch review with
private nested-run paths, a missing receipt, a missing `root_artifacts` declaration,
or a manifest whose path references
have not passed `publish`; those are coordinator handoff failures to repair. A
verifier reports the missing handoff and stops rather than rebuilding the study,
rewriting the report, or spawning another writer.

After `publish`, `verify`, and `fit_handoff.py`, run the portable
`knowledge/scripts/l3_effective_hamiltonian/final_handoff.py --root <consumer-root>`
and preserve its `final-handoff.json` at that exact root. This mechanical validator
checks the declared `fgt-model.json` references, regular files/directories,
symlink/path safety, report, and all three prediction tables. It does not assess
physics, PASP correctness, or an accuracy threshold, so those independent gates
remain mandatory. The coverage manifest must state `qualifying` or
`nonqualifying` (a legacy boolean `passed` may be normalized); nonqualifying
status must retain its failed gate or limitation. Submit the native model and
complete artifacts in either status. A mechanically valid nonqualifying result is
workflow-complete with a separate scientific failure; reserve `blocked` for
missing/incomplete artifacts, interrupted execution, or unresolved required work.
Do not ask a verifier to reconstruct a missing handoff or infer submission from
files outside the declared consumer root.

This boundary applies when the bounded search fails as well as when it qualifies.
On a scientific failure, preserve the best actual result and publish/verify the
coverage and prediction files that the task contract permits, with an explicit
nonqualifying status and the missing-gate reason. Never fabricate a model or fill
missing IDs so that `fgt-coverage.json` appears complete. If publication of a
coverage-only failure is not allowed by the task schema, write the verified
coverage receipt and an explicit coordinator handoff failure at the consumer root,
then finish without dispatching a verifier. A missing consumer-root coverage file
is therefore a handoff defect to repair. When a native fit exists, submit it with
its nonqualifying status; do not relabel a submitted model as absent merely because
the independent accuracy gate failed.

Freeze the delivered report/artifacts before a consolidated final review of the
uncovered scientific claims/coefficient map/test isolation and any requested
independent checks. Parent persists the read-only verifier return in a separate
notes file linked to reviewed hashes. No verifier writes the report or spawns children.
After pass, finish. Cosmetic corrections use a bounded diff; byte-identical copying
uses hash/consumer-path checks. Neither requires a fresh helper acknowledgement or
full recursive verification. Scientific changes require only the affected review
and checks again, retaining earlier evidence and failures.

Timing: preserve stage/tool/runtime records. Tool intervals nest in agent time and
parallel spans overlap. Compare preparation time only with complete equal sample
coverage and reliable excluded PASP intervals. Missing/incomplete timing is not zero;
unattributed delay is not pure reasoning or a scientific stage. Report accuracy and
model changes separately; workflow completion is not scientific acceptance or speed proof.

### Revision validation and limits

Local command `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s candidate/knowledge/scripts/l3_effective_hamiltonian -p 'test_*.py'`
completed with `Ran 136 tests in 5.162s` and `OK`. No PASP process was launched.
The local validation command is:
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s candidate/knowledge/scripts/l3_effective_hamiltonian -p 'test_*.py' -q`.
Round-two local result: 141 tests passed. Coverage includes valid mixed single/pair
initial SOC, nonsequential native types, physical identity mismatch, absent
comparison evidence, executed synthetic body/radius comparisons with actual
preflight/native reconstruction, radius maxima and pair start, externally
supplied manual-format fixtures versus automatic bypass rejection, post-hoc gate
rejection, native rewrite mapping failures and pristine reconstruction mismatch.
The existing width/cap/lambda, method-6 identity, split isolation, freeze and
publication tests also passed. Do not reassign covered unchanged parser facts to
pasp-verifier; retain review of physical choices, mapping/operator interpretation,
outputs, risks and evidence outside this tested scope.

Read-only source assumption: Latticemodel/src/Fitting_one_order.f90,
REWRITE_DATA and REDUCE_DATA_LOG (lines 3222–3275, inspected 2026-10-10) emit
reduced:original mappings; the warning around lines 832–846 can trigger native
rerun. local_mode_SOC.F90 set_special_SOC and special_SOC_clus document maximum
SOC order and omitted non-SOC types. Scripts need no source checkout; the actual
PASP executable must still validate operators, encodings and reconstruction.
Unsupported compatible maps block explicitly. Evidence integrity is not proof of
physical suitability or authenticated execution against full-tree fabrication.
No local test establishes scientific acceptance, independent generalization or
qualified workflow-time improvement. Historical GLM timing is unavailable;
DeepSeek's qualified metric is diagnostic, not a matched new speed comparison.
