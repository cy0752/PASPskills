# L7 Tight-Binding State Machine

本文件是 L7 `Model TB` workflow 的运行门禁。runtime agent 必须先执行这里的状态机；`l7_tight_binding.md` 只补充当前状态和分支所需的细节，不能覆盖本文件的 STOP 条件。

## 核心原则

- L7 uses explicit `Model TB`. If `Model` is absent or not `TB`, do not assume the package is an L7 tight-binding run.
- Lecture-7 examples and run notes are historical observations. Their hopping values, orbital energies, spin/SOC settings, `TB.U`, cutoff radii, eigenvalues, submission helpers and output examples are not defaults.
- Custom TB, SKTB, additional-H, GSDTB, CLS, MLWF and advanced topology/TBPM branches have different dependencies. Do not flatten them into one generic file list.
- `继续`、`ok`、`按例子来`、`去提交` do not confirm TB branch, orbital basis, hopping values, SK integrals, additional Hamiltonian matrix, spin/SOC strategy, CLS target eigenvalue, run environment, or submission authorization.
- `可以使用 subagent` only permits read-only fact collection when the runtime supports it. It does not confirm scientific parameters, promote files, create run directories, prepare submission artifacts, or submit jobs.
- Read-only verifier tasks use `skills/subskills/pasp-verifier/skill.md`. The verifier cannot edit files, choose physical parameters, promote inputs, create runs, prepare submissions, submit jobs, or produce the final user answer.
- Input preflight is not output validation. Preflight controls whether a candidate package can become formal input or a run; output validation controls whether completed outputs can be used.
- `drafts/`, `notes/`, candidate package, formal `input/`, and `runs/<run-id>/` are separate states. Promotion requires explicit flags.
- Do not copy stale outputs such as `PASP.used_info`, `TB.bands`, `band.agr`, `plot.dat`, `gnuplot.dat`, `Eg.dat`, `energy.dat`, `dos.dat`, `wf_kpt_*-band_*.xsf`, `H*.dat`, `WF*.dat`, `cluster-*.Hform`, `local_cluster.xyz`, `local_cluster.vesta`, old logs or scheduler outputs into a fresh input package.

## README / PROGRESS Contract

When creating, promoting, deriving or validating an L7 directory, update README / PROGRESS with at least:
- `Status`: draft / candidate / formal input / run / output-validated / handoff-ready.
- `Branch`: custom TB / SKTB / additional-H / GSDTB / CLS / MLWF or advanced / output validation / mixed / uncertain.
- `File Roles`: `PASP.input`, direct includes, structure route, hopping blocks, extra Hamiltonian files, logs, outputs and helper scripts.
- `Confirmed Settings`: user-confirmed branch, structure route, species order, orbital basis, hopping/SK/additional-H/GSDTB/CLS settings, smoke-test vs production, expected outputs and run environment.
- `Reference Inventory`: every explicit keyword, block, `%include`, dependent file format and known reference gap.
- `Gate Evidence`: user confirmation, read-only preflight / output validation conclusion and evidence paths.
- `Blocked / TODO`: missing confirmations, missing reference coverage, shape/format uncertainty, stale-output cleanup and next allowed action.

Without these records, do not describe a directory as submit-ready, formal input, validated output or handoff-ready.

## 状态机

### S0：目标目录与 workflow 定位

允许自动执行：
- Inventory the user-specified target directory only: files, directories, inputs, includes, logs, scripts, outputs and stale residues.
- Tentatively classify whether the request is L7 TB, another PASP workflow, source/reference research, output validation or pure parameter lookup.
- Identify likely branch clues without making final scientific decisions.

L7 classifiers:
- `PASP.input`, `lattice_model.fdf`, `PASP.used_info`, or user goal contains `Model TB`, `TB`, `SKTB`, `GSDTB`, `Slater_Koster_Hop_Parameters`, `Hop_Parameters`, `TB.additional_H`, `TB.find_H_form`, `TB.localized_state`, flat band, CLS, `TB.bands`, `Htot.dat`, `cluster-*.Hform`, or `local_cluster.*`.

禁止：
- Write or overwrite PASP inputs.
- Create formal `input/`, `runs/<run-id>/`, submit scripts or external task configuration.
- Use sibling examples or run notes as current-directory facts.

### S1：Branch and File-Role Inventory

允许自动执行：
- Classify likely branch: custom TB, SKTB, additional-H, GSDTB, CLS, MLWF/advanced, output validation, or uncertain.
- Build a file-role table for actual files in the target/candidate directory.
- Mark files as hard-required, conditional, environment helper, generated output, stale residue, or unknown.
- Draft a reference inventory for every explicit keyword, block, `%include`, dependent file format and numbering rule.

必须记录：
- Whether input explicitly selects `Model TB`.
- Structure route and direct `%include` targets.
- `Orbitals` presence and current basis intent.
- Which hopping/Slater-Koster/additional-H/GSDTB/CLS controls are present.
- Whether old TB outputs or old Hamiltonian artifacts are present in a directory intended as candidate input.

禁止：
- Promote candidate files to formal `input/`.
- Derive a run directory.
- Create or edit submit-ready helper artifacts.

### S2：Candidate Input Package

允许生成或整理 candidate 包，但必须标注 candidate / not submit-ready。

Candidate package should include or explicitly mark missing:
- `PASP.input` with draft `Model TB` route and branch controls.
- Direct `%include` targets and structure route files.
- `Orbitals`, `Z_values`, `SuperCell` and branch-specific controls.
- Branch-specific files such as `H_add.dat` / `Hmat_add.dat` when `TB.additional_H` is active.
- README / PROGRESS with file roles, user-confirmation status, reference inventory and blocked items.

Agent-derivable artifacts are limited to:
- README / PROGRESS, file inventory, reference inventory notes and candidate labels.
- Draft settings tables for user confirmation.
- Clearly labeled smoke-test candidates when the user accepts smoke-test intent and exact writes are reference-backed.

禁止：
- Promote to formal `input/`.
- Derive `runs/<run-id>/`.
- Create submission artifacts as submit-ready.
- Fill production orbital energies, hopping values, SK integrals, U, SOC strengths, GSDTB independent variables or CLS eigenvalues from examples.

### S3：L7 TB Settings Confirmation（STOP REQUIRED）

Before formal input, run derivation, submission-preparation or submission, the user must confirm or explicitly accept a settings table.

必须确认：
- Workflow branch and stage.
- Structure route, species order and `SuperCell` / structure relationship.
- Orbital basis: `Orbitals`, `Z_values` TB meaning, and `orbitals_nl` when SKTB/GSDTB/CLS needs it.
- Branch-specific scientific settings:
  - custom TB: hopping path interpretation, `Different_hop_path`, real vs complex hopping, matrix values and basis order.
  - SKTB: SK path interpretation, shell pairs, SK integrals, `use_rotation_matrix`, spin/SOC/Hubbard intent.
  - additional-H: whether `H_add.dat`, `Hmat_add.dat` or both are active, matrix dimensions, basis order and hermiticity expectations.
  - GSDTB: spin/SOC strategy, `fig.maxk`, `fig.mdist`, spin directions and `TB.H_indep_var` source.
  - CLS: target flat-band evidence, center atom, cutoff radius and target eigenvalue.
- Smoke-test vs production intent.
- Expected outputs and output-validation target.
- Run environment and whether submission is requested.

确认后记录：
- `USER_CONFIRMED_L7_TB_SETTINGS=true`
- settings table, source, and remaining reference / preflight gaps.

未满足时允许的唯一下一步：list missing confirmations or continue drafting candidate notes. Do not promote formal input, derive run, prepare submission or submit.

### S4：Input Preflight（STOP ON FAIL）

Candidate package promotion, formal input overwrite, run derivation, submit-ready helper editing, external task preparation and submission all require read-only input preflight first.

执行方式：
- Use `skills/subskills/pasp-verifier/skill.md`, `mode: input-preflight`.
- Inputs must name workflow `L7 tight-binding`, target branch, exact candidate directory, user-confirmation record and reference inventory.
- Preflight checks the actual candidate package, not sibling examples or run notes.

L7 checklist minimum:
- `PASP.input` structural parse, direct include graph, duplicate first-wins behavior and explicit `Model TB`.
- Structure route and direct include files present and same-package.
- `Orbitals`, `Z_values`, `SuperCell`, branch controls and branch-specific files align with user-confirmed current-material facts.
- Every explicit keyword, block, include target, file format and numbering rule has reference/user-authoritative coverage.
- Branch-specific dependencies are present or marked blocked.
- No stale TB / Hamiltonian / CLS outputs are mixed into fresh candidate / formal input.
- README / PROGRESS does not claim submit-ready unless gates have passed.

通过后记录：
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`
- evidence path and remaining limitations.

Fail or blocked means the only allowed next action is fixing candidate files, asking for missing confirmation, or recording blocked evidence. Do not proceed to S5.

### S5：Formal Input / Run / Submission Preparation

Allowed only when all flags exist:
- `USER_CONFIRMED_L7_TB_SETTINGS=true`
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`

S5 才允许：
- Promote or overwrite formal `input/`.
- Derive `runs/<run-id>/` from formal `input/`.
- Add current-run helper scripts, executable path, stdout / stderr plan and scheduler facts inside the run directory.
- Prepare external task configuration.

进入 S5 必须记录：
- formal `input/README.md`: source candidate, preflight evidence, reference inventory and confirmation flags.
- `runs/<run-id>/README.md`: source input, helper files, command / scheduler facts, expected outputs, stdout / stderr, smoke-test vs production label.

Submission remains separate. Even with S5 flags, actual job submission needs explicit user submission authorization.

### S6：Output Validation（STOP ON FAIL）

After a run completes and before reporting band gaps, plots, DOS, wavefunctions, Hamiltonian matrices, GSDTB forms, CLS files or downstream handoff, run output validation.

执行方式：
- Prefer `skills/subskills/pasp-verifier/skill.md`, `mode: output-validation`.
- Inputs must name exact run/output directory, expected output files, logs and branch.

L7 validation minimum:
- PASP stdout / scheduler log normal completion or first decisive failure.
- `PASP.used_info` when present confirms same-run `Model TB` and effective branch settings.
- Generic band/DOS outputs are present when expected: `TB.bands`, `Eg.dat`, `energy.dat`, `dos.dat`, `band.agr`, `plot.dat`, `gnuplot.dat`.
- `wf_kpt_*-band_*.xsf` exists only when `TB.write_wf` was active and should be tied to the same run.
- Additional-H outputs such as `Htot.dat` or equivalent Hamiltonian artifacts are same-run and tied to current `H_add.dat` / `Hmat_add.dat`.
- GSDTB outputs such as `cluster-*.Hform`, `H*.dat` and `WF*.dat` are same-run before independent-parameter results are reported.
- CLS outputs require `lgood: T` or equivalent success evidence plus same-run `local_cluster.xyz` and `local_cluster.vesta`.
- Output evidence is not used to retroactively authorize input package promotion or settings.

通过后记录：
- `OUTPUT_VALIDATION_PASS=true`
- validated run id, allowed handoff files and remaining caveats.

Fail or blocked means the only allowed next action is failure summary, missing-output list, log/helper diagnosis, or returning to candidate preparation.

### S7：Handoff / Analysis

Allowed only when:
- `OUTPUT_VALIDATION_PASS=true`
- handoff or analysis target is named.

Allowed actions:
- Summarize validated band/DOS/gap files with source run id.
- Report wavefunction XSF files only from validated same-run output.
- Report additional-H/GSDTB matrix or form outputs only with same-run provenance.
- Report CLS output only from validated `local_cluster.*` and success evidence.

禁止：
- Claim production convergence, physical correctness, magnetic anisotropy or flat-band proof from unvalidated outputs.
- Treat historical energies, hopping values, cutoff radii, eigenvalues or plots as current results.
- Reuse output validation as input preflight for a new run.

