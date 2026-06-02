# Template: `l3_invariant`

This is a starter `Model Invariant` input package, not a confirmed shared-basis setup for a user material.

Before promoting a derived package to formal input:
- confirm all shared-basis parameters with the user, including magnetic elements, `fig.maxk`, `fig.mdist`, expansion powers, SOC scope, representative spin sites, sample count, and structure route;
- treat the included `%block local_mode.special_SOC` in `PASP.input` as an example of an explicit restricted / prioritized SOC strategy, not as a requirement of `Invariant.SOC T`;
- remove `local_mode.special_SOC` when the user wants default full SOC enumeration and has not requested restricted SOC terms;
- keep `local_mode.special_SOC` only when the user or another confirmed workflow condition requires restricted / prioritized SOC, and verify the interaction-type indices from reference-backed or same-basis evidence before writing;
- run the L3 input-preflight gate before creating formal `input/`, deriving `runs/<run-id>/`, preparing submission artifacts, or submitting.

For `Model Invariant` shared-basis / interaction-basis runs, default to single-process execution. If MPI is requested, require evidence that the current PASP build and workflow branch are MPI-safe; with `local_mode.special_SOC`, treat MPI as unsafe unless that path has been explicitly validated.
