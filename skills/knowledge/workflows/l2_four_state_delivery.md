# Completed four-state data: preparation and delivery contract

Use this route when four-state DFT outputs already exist and the goal is exchange
extraction followed by spin-wave dispersion. Do not restart DFT preparation or
enter the L3 effective-Hamiltonian workflow. Keep the entire supplied collection
in scope, including nested pair directories and different cells of one material.

## Prepare once, delegate bounded work

Use the runtime's real native `pasp-helper` writer delegation. Give it the data
root, requested deliverables, current stage, known conventions, unresolved choices,
and artifact paths. Do not simulate a helper in coordinator prose. This contract
does not authorize delegation when the current user explicitly forbids it.

The helper saves one source inventory, one field/source inventory, and one
machine-readable extraction/mapping record. Reuse these paths in later handoffs;
read each needed reference once and reread only for changed fields, contradictions,
or missing coverage. Do not send the whole task through a new reference subagent
at each field edit. Exact field semantics still require reference evidence.

Prepare the most complete candidate supported by the data before asking for
scientific decisions. Bundle unresolved choices with current values, sources,
editable fields and effects. A recommended or assumed spin scale, reference state
or q path is not user confirmation. Resolve missing choices that affect validity
before treating the candidate as an authorized model. Prior task authorization and
provided facts persist; do not ask for them again.

Use the existing four-state topic and magnon contracts for scientific work. Keep
an explicit audit of final energies and convergence, actual flipped sites and all
four sign combinations, species-preserving cell/site mappings, periodic images,
Hamiltonian sign, bond counting and energy units. A quartet can constrain a sum
of image exchanges; `Delta/(4*m)` needs a justified single-class assumption.
Record rank, residuals and unresolved parameters where classes mix. Unit-vector
exchange does not fix quantum S; local DFT moments do not by themselves supply it.
Non-SOC collinear data do not identify DMI or anisotropy. Zero terms are model
truncations, not measured zeros.

### Deterministic geometry gate

Before native extraction, write a small JSON geometry fixture for the source
cell, every quartet endpoint, supplied space-group operations (when known), and
the proposed final primitive cell. From the workspace root run
`python knowledge/scripts/geometry_mapping.py geometry.json > geometry_receipt.json`
and retain the receipt with the delivery evidence. The portable helper checks
endpoint species/site identity, distinguishes equal-distance pairs by full orbit
geometry, and maps endpoints in Cartesian space while retaining explicit integer
lattice images. Treat a residual above tolerance, ambiguous candidate, or species
mismatch as a hard stop. Never replace an image with a minimum-image vector after
this check. The receipt must show unique mappings, reconstructed final endpoints,
`source_bond_cartesian`, `final_bond_cartesian` and `bond_residual_angstrom` at the
tolerance used for the primitive report. A native run or final magnon promotion
without it is incomplete. This prepares evidence only and never calculates or
replaces PASP J.

Treat the receipt as a handoff artifact, not a one-time suggestion. Reuse the
same receipt and input hash for native extraction, then emit a second receipt
after the primitive cell, exchange endpoints, spin ordering and q basis are
frozen and immediately before magnon promotion. The second fixture must contain
the exact final `cell.str`/`unit_cell.str` sites and every retained exchange
endpoint; it must pass with the same or stricter tolerance and its bond vectors
must be compared with the native-stage receipt. If either receipt is stale after
a coordinate, lattice, site or image edit, rerun the geometry gate before any
PASP launch. This explicit handoff prevents a late minimum-image conversion or
cross-lattice copy from silently invalidating an earlier mapping.

## Native J extraction and final primitive model

For completed four-state data, `Model find_J_path_sym` with
`cal_spin_exchange T` must actually read the mapped `Jn/{upup,updn,dnup,dndn}/OSZICAR`
files and produce `spin_exchange.dat`. Pair discovery alone and a magnon run do
not extract J. First audit each source quartet: structure, two flipped atoms,
state sign convention, pair geometry, chemical species, periodic images and
symmetry orbit. `isaAB` selects species, not atom ids; `local_mode_PM.dat` is not
a pair-map override. Copy every OSZICAR byte-for-byte, never synthesize E0 from
OUTCAR TOTEN. Save each native PASP input, complete input closure, log and
unchanged output. Use separate native runs when needed to retain every quartet.
If a pair cannot be mapped, preserve the failed run and explain the blocker;
do not silently use script-computed J as a fallback.

Native-run search is deliberately bounded. Start with each supplied source cell
and the smallest cutoff that contains the audited quartet; add only a finite set
of symmetry/periodic-image expansions justified by a missing class or an explicit
cell-size requirement. Before launching PASP, check that `cell.str` and
`unit_cell.str` are commensurate (an integer supercell relation with matching
species/site images); the delivery checker performs the same check. Give every
candidate a launcher timeout and preserve its input, log and failure signature.
Stop a branch after two identical failure signatures, after a timeout with no new
coverage, or once all supplied quartets and equivalent representatives are
covered. Do not spend unbounded scans over arbitrary supercells/cutoffs, and do
not attribute waiting or unattributed tool time to scientific reasoning. A
failed or incomplete branch remains evidence and cannot be replaced by a script
J value.

Independently calculate the four-state combination as an audit, using the E0
that PASP actually reads. PASP's native output is a 10-field scalar J row in eV;
the denominator uses `Spin_values` of the two species divided by two each.
Document the Hamiltonian sign and any unit, spin or periodic-image scale applied
after extraction. The chosen quantum spin for LSWT remains an editable physical
assumption, not a consequence of a unit-vector J or MAGMOM initialization.
Group all quartets into chemical-symmetry exchange classes before choosing final
representatives. For each class record all members, native rows, J spread,
periodic multiplicities/image counts, identifiability, selection rule and any
conflict. One representative per physical class may enter the final model;
equivalent quartet measurements remain audit evidence, not extra bonds. Never
adjust J to match a reference dispersion. Missing shells are truncations.

The final magnon `cell.str` **and** `unit_cell.str` must both be crystallographic
primitive cells in the same basis, site/species order and coordinates; both must
be read by the final `PASP.input`, with identity `SuperCell`. The DFT and native-J
workspaces may retain their original supercells. Reduce the chemical structure
with spglib and independently check both final structures at 1e-5, 1e-4 and
1e-3 Angstrom for any remaining translation reduction. Preserve a source-to-final
transformation, volumes, atom counts, site/species and periodic-image maps.
For a VASP 5 POSCAR, `python knowledge/scripts/make_primitive_pair.py POSCAR
<new-output-dir> --symprec 1e-4` writes matched structure files and a JSON
source-site/image map. Inspect the tolerance sensitivity and atom residuals.
The generated report deliberately leaves `exchange_map` and `spin_map` empty;
complete those from the audited bond and magnetic-site mapping before handoff.
The script does not construct final J, spin3.in or a q path.
Transform exchange lattice/endpoints, `spin3.in` ordering and q coordinates in
the final reciprocal basis. Audit nonzero-distance bond mismatches separately
from PASP's zero-distance self-pair warnings. Chemical symmetry must not be
hidden by spin signs or artificial species splitting. If magnetic order requires
a larger cell, report the primitive-cell result as conditional and disclose the
magnetic-period limitation; do not substitute a magnetic supercell for either
required final structure.

For a multi-leg q path, freeze one final input that specifies every point of the
claimed path. `qpoints.magnon` is a two-endpoint interpolator in the inspected
source; `spinw.use_block_BandLines T`, `BandLinesScale ReciprocalLatticeVectors`
and explicit `%block BandLines` can describe the full path in one run. Confirm
the saved spectrum's row count and endpoints against that input after runtime.

## Machine-readable native receipt

Add `materials[].j_extraction` with `method: "pasp_native"`, nonempty
workspace-relative `evidence_report`, `runs` and `lineage`, plus
`final_exchange` naming the final magnon `spin_exchange.dat`. Each `runs[]`
contains workspace-relative `input`, `log`, `output`; `inputs` is the complete
list relative to that extraction input's directory, including `PASP.input`,
includes and every mapped OSZICAR, excluding outputs/logs/scripts. Each
`quartet_map[]` entry identifies one native output row by 1-based `native_pair`,
`source_pair` relative to the original input data root, and a bijective `states`
object from `upup/updn/dnup/dndn` to `up_up/up_dn/dn_up/dn_dn`. Infer the mapping
from actual flip sites and pair geometry, not folder names. Across native runs,
cover every supplied quartet. Each `lineage[]` entry names a 1-based `final_row`,
workspace-relative unchanged `native_output`, 1-based `native_row`, and `scale`
(default 1; nonunit scales require `reason`). The final J is that native scalar
times scale. Isotropic 18-field final rows are allowed: all three diagonal
elements equal the scaled native J and off-diagonal elements are zero. A scalar
final row is allowed by the delivery format, but the inspected magnon reader
switches to matrix mode; establish compatibility with the actual PASP executable
before using scalar final rows. Keep unsupported DMI/anisotropy at zero.

`materials[].inputs` is relative to its final `run_dir` (for example
`PASP.input`), unlike extraction paths. List both final structure files and the
consumed exchange file. Set `materials[].primitive_cell_report` to a nonempty
workspace-relative JSON report with `source_cell`, `source_lattice_ang`,
`transformation` (row-vector convention: primitive lattice = transformation
times source lattice), source and
primitive atom counts/volumes, `symprec_angstrom`, `site_map`, `species_map`,
`image_map`, `exchange_map`, and `spin_map`; record all tested tolerances and
ambiguities. Before handoff run:

Complete each `exchange_map` entry with `final_row`,
`endpoint_sites_1based: [a,b]`, `endpoint_a_image: [ia,ja,ka]` and
`endpoint_b_image: [ib,jb,kb]`. Sites refer to the final structure's fractional
coordinates reduced into [0,1); images are exact integers in that lattice basis.
The alias form `final_sites_1based` plus `image_cells: [[ia,ja,ka],[ib,jb,kb]]`
is also supported. In the endpoint form only, omitted `endpoint_a_image` means
zero; `endpoint_b_image` is required. Optional `endpoint_species` uses chemical
symbols and `endpoint_species_ids` uses final PASP species ids.
Generate final coordinates as `(final_fractional_site + image) @ final_lattice`;
never copy coordinates from a slightly different source lattice or wrap each
endpoint separately. Preserve the native J and record any source/final strain
and bond-vector residual separately. A source-mapping tolerance does not relax
the final file's reconstruction precision.

```text
python knowledge/scripts/check_four_state_native.py <delivery.json> --workspace <workspace> --source <original-input-root>
```

This receipt check verifies path bases, OSZICAR bytes, effective inputs, native
numeric lineage and dual primitive geometry. It now also reads the **actual**
final exchange file: each endpoint must have exactly one same-species site/image
within 1e-6 Ang (coordinate reconstruction precision), and the report must cover
every final row once with exactly those sites and images. Missing, ambiguous,
stale or collapsed-image mappings fail even when J lineage passes. Run it on the
frozen files before magnon promotion and delivery, not just on a separately
authored geometry fixture. It is not PASP replay or proof of
pair equivalence, normalization, quantum spin, magnetic ground state, or physical
stability. The independent read-only verifier reviews those unresolved scientific
questions and the source-to-primitive maps. The controller runs PASP after the
package is handed off; do not claim a run before it returns runtime evidence.

Read-only source basis (snapshot inspected 2026-09-30; executable may differ):
`Latticemodel/src/J_path_sym.f90:find_J_path_sym/cal_spin_exchange` selects the
native branch; `spin_lat_subs.f90:read_four_state_result` reads the four Jn
OSZICARs and computes J, and `write_spin_exchange_file` writes eV/Ang scalar
rows; `VASP_OSZICAR.f90:get_VASP_ene_EDIFF` reads the last E0 after its EDIFF
test; `spin_lat.F90:read_exchange_para` switches magnon to matrix J; and
`spinw.f90:read_spinw` selects BandLines. Portable scripts have no source-tree
dependency. Source inspection does not replace validation against PASP.

Before LSWT, retain a reference-state provenance and stability assessment on the
actual represented bond network. Check basis handedness before writing, and carry
any basis change through coordinates and the site map. Do not fix handedness by
changing a lattice sign alone. `spin_exchange.dat` representatives must correspond
to actual upstream pairs. Inspect runtime bond-assignment warnings and compare
the expanded-network energy to PASP's initial energy with an explicit cell scale;
never multiply an already expanded energy by the cell multiplicity again.
Cholesky failure can come from bond mapping or the reference, not just q sampling.
Changing cutoffs or spin directions to obtain a spectrum does not prove the model.

## Deterministic input coverage and source assumptions

Run `knowledge/scripts/l2_validate_inputs.py <package> --workflow magnon` before
promotion. Save its JSON receipt. The portable checker now additionally covers:

- Nonsingular, right-handed primitive lattice, including noninteger volumes.
- Raw numeric exchange/spin records distinct from FDF comments. Emit one complete
  numeric record per line, no internal blank or comment records; trailing blank
  lines are allowed. This is a conservative canonical subset, not every syntax
  accepted by Fortran. Do not automatically strip comments or shift records.
- Mandatory dJ/du count, derivative-to-J references, and scalar/matrix J widths
  under the effective mode. Explicit trailing zero counts remain preferred;
  missing SIA/DMI/fourth-order sections at EOF produce warnings.
- `%include` paths relative to the run working directory, first effective
  declarations, inactive-duplicate diagnostics and wrong scalar/block kinds.

Read-only source reference: snapshot inspected 2026-09-24, relative to the PASP
source root, `Latticemodel/src/read_input.F90:read_unit_cell_str` (negative-volume
stop); `spin_lat.F90:read_exchange_para` (J numeric records, required character
record for dJ/du, effective matrix mode, optional trailing section EOF);
`read_spin3.f90:read_spin3_array/read_spin3_file` (numeric records);
`fdf/fdf.f:fdf_open` (process-relative include paths). The installed executable
may differ from this source snapshot. Source inspection is not a PASP run.
The scripts neither read nor require that source tree at execution time.

Coverage remains bounded: no primitive reduction, symmetry/orbit proof, exchange
normalization, physical spin scale, ground-state search, bond assignment or result
verification is certified by input-format pass. Advanced FDF redirection and
noncanonical raw Fortran records need explicit review; alloy or higher derivative
formats are outside this preflight's supported exchange subset. Do not claim
those were validated merely because a simpler package passes.

## Build the delivery contract before the final report

Translate the user's current interface into a small JSON contract before writing
the delivery generator. Preserve the requested array/object distinction: a list
of per-material objects is an array even when an internal analysis uses a name-keyed
dictionary. Keep the requested field names and nesting. Do not infer the public
interface from an internal serialization. No fixed task interface is built into
the checker.

`knowledge/scripts/check_delivery.py` accepts a deliberately limited contract
language. Every node needs `type` (object, array, string, number, integer, boolean,
null). Objects use `required` and `properties`; every required field needs a typed
property. Arrays need `items`; `uniqueBy` is an array of identity field names
(`[]` means the whole scalar/item); `expectedKeys` is an exact inventory, using
tuples for identity fields. `minItems` is optional. `const` compares an exact value.
Strings may use `pathKind: file` (nonempty) or `directory`. Unknown contract keywords
fail rather than silently disabling a check. Extra object fields are preserved
and allowed; this is not a full JSON Schema implementation.

For example, this synthetic fragment describes an array of named records:

```json
{"type":"array", "uniqueBy":["name"], "expectedKeys":[["sample"]],
 "items":{"type":"object", "required":["name","log"], "properties":{
   "name":{"type":"string"}, "log":{"type":"string","pathKind":"file"}}}}
```

Generate expected material and pair keys by recursively inventorying the actual
source data, not by copying the delivery being checked. Use the observed state
layout to identify quartet leaves and report missing states; never hardcode a
number of pairs or assume one directory depth. Save inventory provenance beside
the contract. Define composite identities where pair names repeat across systems.
Check material-to-pair membership and raw energies separately: `expectedKeys`
checks the configured arrays, not arbitrary joins or scientific arithmetic.

```text
python knowledge/scripts/check_delivery.py <delivery.json> <contract.json> --root <workspace>
```

After an actual run, preserve a SHA256 map `{ "relative/artifact/path": "sha256" }`
for the complete input include closure, directly read input files, raw spectrum,
log and any other delivered artifacts. Hashing an already modified file is not
evidence that it stayed unchanged. Add `--hashes <checkpoint.json>` to compare
against a saved checkpoint. Paths are resolved against `--root`, including symlinks;
missing, empty file paths and paths escaping that root fail. An input/result
checkpoint establishes byte integrity, not physical accuracy or run success.

For a container-only repair, preserve the rejected delivery first, then run:

```text
python knowledge/scripts/check_delivery.py <delivery.json> <contract.json> --root <workspace> --hashes <checkpoint.json> --previous <before.json> --array-repair /<container>:<identity-field>
```

Only the named container is normalized to identity keys for comparison; every
other leaf remains subject to exact equality, including numbers, paths, arrays
and assumptions. Duplicate identities or mismatching old dictionary keys fail.
`--previous` without `--array-repair` requires full content equality. This command
does not edit or repair files. Preserve the receipt outside frozen packages.

## Review and runtime handoff

For completed-four-state delivery, these rules specialize the generic L2 verifier
gate and the verifier's broad checklists. The coordinator supplies the scientific
verifier an explicit unresolved checklist, saved reference inventory, deterministic
receipts and evidence paths. Retain native verifier review of scientific ambiguity,
source contradictions, mapping, normalization, reference validity and any explicitly
requested independent check. A verifier's review of an assumption does not make
the assumption a measured fact. The external result/replay checks are unchanged.

Do not dispatch a verifier solely to repeat tested type/count/include/path/hash
checks. For a strictly container-only repair after scientific review, the helper
may write the correction and run the contract, checkpoint and zero-drift checks
above. Their pass replaces only that mechanical repair review. Record
`DETERMINISTIC_DELIVERY_CHECK_DONE=true`, covered scope and receipt paths; do not
invent `READ_ONLY_SUBAGENT_PREFLIGHT_DONE` or a new scientific verdict. If a
scientific leaf or input changes, return the affected delta to scientific review
and rerun affected preparation/runtime checks. Checks not configured (including
cross-array membership and proof that no run occurred) must not be claimed.

Under TASK RUNTIME, prepare the complete isolated package and hand it to the
controller; the controller runs PASP and returns evidence for repair. The provided
local launcher needs no scheduler, `mpirun`, alternative MPI transport or new
cluster authorization. Draft-only tasks stop at input delivery and never claim a
run. After runtime returns, retain completion/error logs, raw spectrum shape,
q endpoints and interpolation checks, same-run provenance and instability
diagnostics. Independent replay demonstrates reproducibility, not a physically
correct exchange mapping or ground state. Report unresolved scientific limits.

Save each failed attempt. New physical inputs require a fresh run directory;
report/container repairs with unchanged inputs and outputs do not require a new
PASP calculation. Report actual helper/verifier scope and per-stage timing from
available evidence. Tool spans nest in agent time and concurrent spans overlap;
do not add them or call unattributed latency reasoning time. Incomplete timing is
unavailable, never zero. No speed claim follows from a local script benchmark.
