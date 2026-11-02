# L3 Model Integrity and Simulation Handoff

Read the current-stage section before preparing magnetic DFT samples, full-study
conversion, interpreting fitted interactions, or passing an L3 model to MC/MD.
Scripts are under `../scripts/l3_effective_hamiltonian/`; their README defines
supported formats.

## Prescribed-spin dataset construction

Record whether the study generates energies for prescribed spin configurations,
explicitly studies magnetic relaxation, or ingests existing DFT data. Path A/B
describes sample provenance; it does not replace this scientific distinction.

When generating prescribed-spin DFT datasets for a magnetic effective Hamiltonian,
**constrain the target local-spin directions during DFT**. This applies to random
and symmetry-generated configurations alike. Electronic self-consistency must be
reached while retaining those directions; allowing spin directions to relax freely
changes the sampled configurations. Direction constraints do not require fixing
moment magnitudes: that is a separate modeling choice.

Before a new DFT handoff, check the actual effective input against the intended
per-site directions. `MAGMOM` initializes moments; it does not constrain them.
The presence of `M_CONSTR` alone does not activate constraints. Establish an active,
direction-appropriate constraint mode and strength (including `I_CONSTRAINED_M`
and `LAMBDA` for VASP) from supported project settings and version-appropriate
source documentation. Check target vectors, active magnetic sites, atom order and
coordinate frame consistently across PASP, DFT inputs and final-moment comparison.
Missing or inactive constraint settings block the prescribed-spin DFT handoff;
do not invent production values. `createINCAR.sh` only appends moment records and
does not perform these checks. These are agent/reviewer obligations.

After DFT, check electronic convergence separately from final per-site direction
agreement with the targets. Record a study-justified direction tolerance; the
`extract_magmoms.py` cosine default is a diagnostic, not universal acceptance.
Investigate undefined directions on intended magnetic sites. Direction drift
requires investigating/fixing constraints and recalculating affected samples when
needed to meet the prescribed sampling contract. Same-basis method-6 re-encoding
repairs final-state/feature identity, but cannot alone approve the loss of intended
configurations or establish retained sampling coverage. A changed sampling plan
requires an explicit scientific decision, not a silent switch to Path B.

Constraints are a sampling requirement, not a fallback after some SCF-failure
percentage. Different random seeds or different final energies do not establish
preserved directions or coverage. A residual plateau proves neither convergence
nor metastability; unconstrained SCF is not guaranteed to find the nearest spin
minimum or preserve magnetic barriers. Do not reject constrained sampling on the
blanket claim that it necessarily defines an unphysical energy surface.

Existing unconstrained Path B data remain eligible for scientific suitability
review using their actual converged states and same-basis encoding. Record the
known constraint/relaxation protocol and missing evidence; assess suitability for
the intended model and sampling comparison. Do not retroactively assume that
initial directions were retained, or reject all such data solely for being
unconstrained. Explicit magnetic-relaxation studies are a separate objective.

## Original sample identity and final physical state

Keep original IDs even when failed samples leave gaps. If an adapter requires new
IDs, freeze one new-to-original map and use it for structures, final moments,
features, energies and splits. Matching new filenames alone does not prove identity.
Use the final converged OUTCAR state with its energy; a recorded agreement of initial
and final directions is required before using initial-state features instead.
DFT can change the magnetic state while leaving the sample ID and atomic positions
unchanged. Then the pre-DFT ene_symbol can be stale: re-encode the final state with
method 6 against the same frozen basis, and pair that output with final TOTEN. Replacing
distortion.MAGMOM alone does not update ene_symbol. Archive old features separately;
unchanged structure, SCF convergence or a good fit score does not establish reuse.
For newly prescribed-spin samples, also apply the direction/drift rule above;
re-encoding alone does not satisfy the dataset-construction requirement.
If initial features are reused, justify both state agreement and feature equivalence
at source/encoding precision; there is no universal angular tolerance for all models.

For a full-study spin/OUTCAR conversion, use `study_contract.py convert` with
`require_source_identity: true` and a source-supported `source_energy_atol`.
Each sample supplies `source_identity`, `encoding_identity`, and `original_id` when
renumbered. The source ledger names the original OUTCAR and final-state input package;
the encoding record names the inputs actually consumed by that sample's runtime.
Capture these records during preparation/runtime, not by reconstructing expected
paths after fitting. Freeze the structure/magnetic-state/basis hashes before PASP
and the output feature hash after successful encoding in the same runtime record.
Conversion must match all four hashes, not just the current input filenames.
See the scripts README for schemas.

The check compares original IDs, final TOTEN and structure/magnetic-input bytes;
it records source hashes. It does not prove DFT convergence or that an agent-written
record describes the actual execution. Build the canonical final-state package with
the bundled OUTCAR parsers and inspect convergence/atom mapping separately. Unsupported
DFT formats or nonspin routes require explicit equivalent provenance review; legacy
conversion without identity records must retain its uncovered scope in the receipt.

## Basis strategy and periodic identifiability

Honor the user's SOC/body-order/cutoff strategy. `local_mode.special_SOC` restricts
enumerated invariants in the shared-basis run; fitting keep terms only constrain
selection from the existing basis. Keep/skip files and MC retained terms are separate
decisions. Neither full SOC nor a parameter count below the sample count is universal.
p>n can be appropriate for sparse fitting, but correlated columns can violate the
assumptions required for recovery. Check conditioning, residuals and parameter stability.

Before expensive DFT generation, check whether distinct interaction orbits fold onto
the same periodic atom tuples in the training cell. After encoding, inspect rank,
zero-variance columns and dependencies on train/selection only; keep final test untouched.
Distinguish infinite-lattice symmetry equivalence, finite-cell aliasing, and correlations
specific to the sampled states. Numerical correlation does not establish physical identity.

For a diagonal primitive-to-training relation and supplied two-body orbits,
`periodic_alias.py --manifest pairs.json` compares periodic undirected pair multisets,
including relative multiplicities, in training and target cells. Obtain primitive
site IDs and integer translations from same-basis cluster geometry and symmetry
expansion. Do not supply only one representative when the full orbit differs.
The target shape is relative to the primitive, including any extra PASP `SuperCell`
expansion of `cell.str`. Unsupported skew cells, SOC component transformations,
multi-body dependencies or incomplete orbit inventories need additional analysis.
Exit 2 means unresolved geometric aliasing, not permission to delete a term.

Example mechanism: in a period-3 direction, 2a is congruent to -a; symmetric a/2a
pair sums can coincide. This relation does not hold in period 6. Training data then
identify a combination of couplings, not both separately. A physically justified
short-range assumption or discriminating additional cells/configurations can resolve
the modeling choice. Record that assumption and validate transfer to the target cell.
Never claim the long-range coupling is zero merely because a solver skipped its column.

## Fit to MC/MD parameter transfer

Prefer the selected PASP **native `*_LM.txt`** output as the source for `J_best.dat`.
For the supported `Fitting_one_order` report, the leading numbered table contains
physical parameter IDs, including 0 for the energy offset. Internal `XM` values
index the fitting representation, which includes a constant column and can undergo
column rewriting. Do not copy internal XM directly or infer a universal XM-minus-one
rule. The native LM exporter uses PASP's original-to-reduced mapping and excludes
the constant. Retained count is the number of actual nonzero interactions, not the
fit report's total including its intercept.

Use `fit_handoff.py --manifest handoff.json --root NEW_CANDIDATE_DIR` for supported
native reports. It checks native LM physical IDs/coefficients against the selected
report and same-basis `ipara_gb`, then reconstructs **every train and selection
prediction** using the pristine full-basis matrices plus the separate energy offset.
Add `j_file` to check an already prepared J_best; do this against the actual candidate,
not only a different run's parameter file. It never accesses final test. Preserve
pristine matrices before I_CHECK_DATA rewrites run inputs. Unsupported reports,
additional fixed/dependent terms or missing original matrices need equivalent
source-backed mapping and numerical checks; never claim a script pass for them.

The optional export copies native LM bytes into a new candidate package and records
the offset separately in `fit-handoff.json`. It refuses to overwrite changed files.
Retain basis, input/report hashes, unit/divisor evidence and both split checks in
the L3-to-simulation handoff. Changing any of these invalidates the affected checks.
Hash/range checks alone cannot catch a constant exported as a valid interaction ID.

Keep the energy zero separate when interpreting coefficients. A roughly total-DFT
energy-sized coefficient labeled as anisotropy requires mapping/offset investigation;
spin normalization alone is not evidence that the label is correct. Resolve each
term to its actual polynomial before assigning Heisenberg, Ising or DMI language.
SzSz alone is not isotropic S dot S; symmetric cross-component exchange is not
automatically DMI.

## Scientific and runtime acceptance

PASP's prediction set used to select terms/lambda is a selection set, even if named
holdout. Preserve its role across retries. Evaluate final test only after freezing
the model and disclose prior test access. High selection R2 does not establish
identifiability, correct parameter transfer, physical stability or MC validity.
Mechanical receipts certify only their explicit scopes.

L4 input preflight must check mandatory controls even with `read_interaction T`:
mode definition, `fig.maxk`/`fig.mdist`, expansion/SOC settings and required includes,
with effective first declarations and stage-specific exceptions. Reading an existing
basis does not imply these input readers are bypassed. Preserve upstream settings
unless the current build/reference supports an intentional stage change.

Runtime helpers must propagate solver failures, fail on required write probes, and
check normal completion and intended outputs. An unconditional `exit 0` after PASP
invalidates scheduler success as runtime evidence. Patch only the authorized task
launcher; do not change a shared external executable or infer disk quotas from pool
capacity. New counterevidence must update current conclusions/handoffs; retain old
failures as history rather than leaving their causal claims active.
