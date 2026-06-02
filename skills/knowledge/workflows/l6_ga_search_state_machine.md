# L6 GA Search State Machine

本文件是 L6 GA global structure search workflow 的运行门禁。runtime agent 必须先执行这里的状态机；`l6_ga_search.md` 只补充当前状态所需的输入、输出、可调项和检查细节，不能覆盖本文件的 STOP 条件。

## 核心原则
- L6 uses explicit `Model GA`. If `Model` is absent or not `GA`, do not assume the package is an L6 GA run.
- Lecture-6 examples and run notes are historical observations. Their population size, generations, `SuperCell`, `Pher` / `Pmut`, VASP inputs, Slurm settings, job ids, energies and symmetry labels are not defaults.
- Random-spacegroup, perturbation, magnetic, restart, fixed-lattice / constrained-cell, interface and parallel-external-evaluator branches have different dependencies. Do not flatten them into one generic file list.
- `继续`、`ok`、`按例子来`、`去提交` do not confirm GA settings, external-evaluator settings, magnetic policy, run environment, or submission authorization.
- `可以使用 subagent` only permits read-only fact collection when the runtime supports it. It does not confirm scientific parameters, promote files, create run directories, prepare submission artifacts, or submit jobs.
- Read-only verifier tasks use `skills/subskills/pasp-verifier/skill.md`. The verifier cannot edit files, choose parameters, promote inputs, create runs, prepare submissions, or produce the final user answer.
- Input preflight is not output validation. Preflight controls whether a candidate package can become formal input or a run; output validation controls whether completed outputs can be handed downstream.
- `drafts/`, `notes/`, candidate package, formal `input/`, and `runs/<run-id>/` are separate states. Promotion requires explicit flags.
- Do not copy stale `PASP.used_info`, `Saved_*.POS`, `low_ene_strs.dat`, `pc_low_ene_strs.dat`, `strs_saved.dat`, generation-suffixed DFT artifacts, `vasp_N/`, old logs, or old `opt/` outputs into a fresh input package.

## README / PROGRESS Contract
When creating, promoting, deriving or validating an L6 directory, update README / PROGRESS with at least:
- `Status`: draft / candidate / formal input / run / output-validated / handoff-ready.
- `Branch`: plain random, random-spacegroup, perturbation, magnetic, restart, fixed / constrained, interface, output validation, or mixed / uncertain.
- `File Roles`: `PASP.input`, direct includes, structure files, seed, external evaluator inputs, helper scripts, generated outputs and post-GA optimization files.
- `Confirmed Settings`: user-confirmed composition, structure route, branch, search objective, smoke-test vs production, GA scale, external evaluator, magnetic policy, constraints, run environment.
- `Reference Inventory`: every explicit keyword, block, `%include`, dependent file and known reference gap.
- `Gate Evidence`: user confirmation, read-only preflight / output validation conclusion and evidence paths.
- `Blocked / TODO`: missing confirmations, unsafe helper assumptions, unavailable reference, missing outputs or next allowed action.

Without these records, do not describe a directory as submit-ready, formal input, validated output or handoff-ready.

## 状态机

### S0：目标目录与 workflow 定位
允许自动执行：
- Inventory the user-specified target directory only: files, subdirectories, logs, scripts, inputs, outputs and stale residues.
- Tentatively classify whether the request is L6 GA, another PASP workflow, source/reference research, or pure parameter lookup.
- Identify likely branch clues without making final scientific decisions.
- Record uncertainty and missing evidence.

L6 classifiers:
- `PASP.input` or `PASP.used_info` contains `Model GA`.
- User goal mentions GA, genetic algorithm, global structure search, low-energy structure search, random space group, perturbation search, magnetic structure search, saved GA structures, `Saved_*.POS`, `low_ene_strs.dat`, `strs_saved.dat`, `run_pvasp.sh`, `vasp_N/`, `POSCAR.NNN.GGG`, `CONTCAR.NNN.GGG`, `OSZICAR.NNN.GGG`, or GA generation logs.

禁止：
- Write or overwrite PASP inputs.
- Create formal `input/`, `runs/<run-id>/`, submit scripts or external task configuration.
- Use sibling examples or run notes as current-directory facts.

### S1：Branch and File-Role Inventory
允许自动执行：
- Classify likely branch: plain random, random-spacegroup, perturbation, magnetic, restart, fixed / constrained, interface, parallel external evaluation or output validation.
- Build a file-role table for actual files in the target or candidate directory.
- Mark files as hard-required for the current route, conditional, environment helper, generated output, stale residue, or unknown.
- Draft a reference inventory for every explicit keyword, block, `%include`, dependent file format and numbering rule.

必须记录：
- Whether `PASP.input` explicitly selects `Model GA`.
- Structure route: `cell.str` / `unit_cell.str`, inline structure, POSCAR route, or unknown.
- Direct `%include` targets.
- External evaluator plan: serial command / `GA.VASPCMD`, parallel `run_pvasp.sh`, VASP / GULP files, scheduler helpers, stdout / stderr.
- Magnetic policy if any: `GA.magnetic`, `Spin_values`, `MAGMOM_*`, `OUTCAR` magnetic read, spin-polarized DFT.
- Whether old generated outputs are present in a directory intended as candidate or formal input.

禁止：
- Promote candidate files to formal `input/`.
- Derive a run directory.
- Create or edit submit-ready helper artifacts.

### S2：Candidate Input Package
允许生成或整理 candidate 包，但必须标注 candidate / not submit-ready。

Candidate package should include or explicitly mark missing:
- `PASP.input` with draft `Model GA` route and branch controls.
- Direct `%include` targets and structure route files.
- Material species / spin / supercell blocks when current route needs them.
- Optional `seed.in` only when reproducibility is intended.
- External evaluator inputs and helper scripts only as environment-specific candidate artifacts.
- README / PROGRESS with file roles, user-confirmation status, reference inventory and blocked items.

Agent-derivable artifacts are limited to:
- README / PROGRESS, file inventory, reference inventory notes and candidate labels.
- Draft settings tables for user confirmation.
- Clearly labeled smoke-test candidates when the user accepts smoke-test intent and exact writes are reference-backed.

禁止：
- Promote to formal `input/`.
- Derive `runs/<run-id>/`.
- Create submission artifacts as submit-ready.
- Fill production physical settings, VASP settings, magnetic policy, `SuperCell`, search ranges or constraints from examples.

### S3：L6 GA Settings Confirmation（STOP REQUIRED）
Before formal input, run derivation, submission-preparation or submission, the user must confirm or explicitly accept a settings table.

必须确认：
- Workflow branch and stage.
- Composition, structure route, species order, `SuperCell` / structure relationship and whether the run is smoke-test or production.
- Search objective: broad global search, known-framework perturbation, magnetic order search, restart, constrained search, interface / surface search, or output validation.
- GA scale and search controls at workflow level: population, generations, saved-structure target, heredity / mutation balance, duplicate / symmetry handling.
- External evaluator: VASP / GULP / other, serial vs parallel, command / helper, required input family, convergence responsibility, stdout / stderr and scheduler environment.
- Magnetic policy when active: random magnetic vs magnetic-spacegroup generation, AFM / FM restrictions, mutation, OUTCAR magnetic read, spin-polarized DFT support.
- Constraint policy when active: pressure, fixed lattice, fixed cell, strain, fixed atom / axis, interface surfaces.
- Restart provenance when active: saved files and generation id.
- Handoff target: raw saved structures, second-pass optimization, symmetry analysis, plotting, or restart.

确认后记录：
- `USER_CONFIRMED_L6_GA_SETTINGS=true`
- settings table, source, and remaining reference / preflight gaps.

未满足时允许的唯一下一步：list missing confirmations or continue drafting candidate notes. Do not promote formal input, derive run, prepare submission or submit.

### S4：Input Preflight（STOP ON FAIL）
Candidate package promotion, formal input overwrite, run derivation, submit-ready helper editing, external task preparation and submission all require read-only input preflight first.

执行方式：
- Use `skills/subskills/pasp-verifier/skill.md`, `mode: input-preflight`.
- Inputs must name workflow `L6 GA search`, target stage / branch, exact candidate directory, user-confirmation record and reference inventory.
- Preflight checks the actual candidate package, not sibling examples or run notes.

L6 checklist minimum:
- `PASP.input` structural parse, direct include graph, duplicate first-wins behavior and explicit `Model GA`.
- Structure route and direct include files present and same-package.
- `Z_values`, `Spin_values`, `SuperCell` and branch controls align with user-confirmed current-material facts.
- Every explicit keyword, block, include target, file format and numbering rule has reference/user-authoritative coverage.
- Branch-specific dependencies are present or marked blocked: random-spacegroup range, perturbation source structure, magnetic helper / MAGMOM / OUTCAR read, restart artifacts, interface `GA.surfaces`, external evaluator helper.
- Environment helpers are not treated as portable defaults.
- No stale outputs are mixed into fresh candidate / formal input.
- README / PROGRESS does not claim submit-ready unless gates have passed.

通过后记录：
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`
- evidence path and remaining limitations.

Fail or blocked means the only allowed next action is fixing candidate files, asking for missing confirmation, or recording blocked evidence. Do not proceed to S5.

### S5：Formal Input / Run / Submission Preparation
Allowed only when all flags exist:
- `USER_CONFIRMED_L6_GA_SETTINGS=true`
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`

S5 才允许：
- Promote or overwrite formal `input/`.
- Derive `runs/<run-id>/` from formal `input/`.
- Add current-run external evaluator helper, scheduler script, executable path, stdout / stderr plan and environment facts inside the run directory.
- Prepare external task configuration.

进入 S5 必须记录：
- formal `input/README.md`: source candidate, preflight evidence, reference inventory and confirmation flags.
- `runs/<run-id>/README.md`: source input, helper files, command / scheduler facts, expected outputs, stdout / stderr, smoke-test vs production label.

Submission remains separate. Even with S5 flags, actual job submission needs explicit user submission authorization.

禁止：
- Copy old generated outputs into a new run as inputs unless the branch is explicitly restart and preflight has validated same-run provenance.
- Use example Slurm paths or VASP inputs as current environment facts without user confirmation.

### S6：Output Validation（STOP ON FAIL）
After a run completes and before low-energy handoff, second-pass optimization claims, plotting, symmetry reporting or restart from outputs, run output validation.

执行方式：
- Prefer `skills/subskills/pasp-verifier/skill.md`, `mode: output-validation`.
- Inputs must name exact run/output directory, expected handoff files, logs and branch.

L6 validation minimum:
- PASP stdout / scheduler log normal completion or first decisive failure.
- `PASP.used_info` when present confirms same-run `Model GA` and effective branch settings.
- External evaluator artifacts are present and consistent with branch; missing / incomplete candidate DFT outputs are reported by candidate.
- Low-energy structures and summaries exist before handoff: `Saved_NNN.POS`, `Saved_gen.dat`, `low_ene_strs.dat`, `pc_low_ene_strs.dat` or equivalent current-run output.
- `strs_saved.dat` is same-run if restart / continuation is planned.
- Magnetic branch validates required `MAGMOM` / `OUTCAR` evidence when current settings depend on it.
- Post-GA `opt/` outputs are separately validated before optimized energies or symmetries are reported.
- Output evidence is not used to retroactively authorize input package promotion or settings.

通过后记录：
- `OUTPUT_VALIDATION_PASS=true`
- validated run id, allowed handoff files, failed / skipped candidates and remaining caveats.

Fail or blocked means the only allowed next action is failure summary, missing-output list, log/helper diagnosis, or returning to candidate preparation.

### S7：Handoff / Post-GA Processing
Allowed only when:
- `OUTPUT_VALIDATION_PASS=true`
- handoff target is named.

Allowed actions:
- Summarize validated `Saved_NNN.POS` / low-energy structure candidates with source run id.
- Prepare second-pass optimization only as a new candidate / run process with its own environment helper checks.
- Report symmetry-analysis results only when the postprocessing run/tool/output is validated.
- Prepare restart candidate only from validated same-run artifacts.

禁止：
- Claim GA convergence, production stability, optimized energy or symmetry from unvalidated raw outputs.
- Treat historical energies, job ids or symmetry labels as current results.
- Reuse output validation as input preflight for a new run.
