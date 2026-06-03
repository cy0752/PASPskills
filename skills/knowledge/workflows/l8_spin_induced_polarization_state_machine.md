# L8 Spin-Induced Polarization State Machine

本文件是 L8 spin-induced polarization workflow 的运行门禁。runtime agent 必须先执行这里的状态机；`l8_spin_induced_polarization.md` 只补充当前状态和分支所需的细节，不能覆盖本文件的 STOP 条件。

## 核心原则

- L8 当前覆盖两条实用分支：`Model KNB` 的 pure electronic KNB / gKNB 极化，以及 `Model Spin_lattice_interaction` 的 ion / lattice / strain contribution。
- `Model Spin_lattice_interaction` 在 L2 中也用于 PTMC / CG 找磁基态；L8 只处理已经给定或读入自旋构型后，由 spin force / stress / Born charge / force constants 等计算极化贡献的分支。不要把 L2 找基态流程自动改判成 L8。
- Lecture-8 examples 和 run notes 是历史观察。它们的 `Spin_values`、`GKNB_inter_site` 张量、`GKNB.local_axis`、`fig.maxk`、`fig.mdist`、结构、Born charge、force constants、elastic constants 和提交脚本都不是当前材料默认值。
- `继续`、`ok`、`按例子来`、`去提交` 不确认 L8 分支、坐标系、局域轴、GKNB 张量、spin3 行序、Born charge / force-constant provenance、应变/应力策略或提交授权。
- `可以使用 subagent` only permits read-only fact collection when the runtime supports it. It does not confirm scientific parameters, promote files, create run directories, prepare submission artifacts, or submit jobs.
- Read-only verifier tasks use `skills/subskills/pasp-verifier/skill.md`. The verifier cannot edit files, choose physical parameters, promote inputs, create runs, prepare submissions, submit jobs, or produce the final user answer.
- Input preflight is not output validation. Preflight controls whether a candidate package can become formal input or a run; output validation controls whether completed outputs can be used.
- `drafts/`, `notes/`, candidate package, formal `input/`, and `runs/<run-id>/` are separate states. Promotion requires explicit flags.
- Do not copy stale outputs such as `PASP.used_info`, `spin3.xsf`, `Ppair.xsf`, `GKNB_data.*`, `1.xsf`, `2.xsf`, `3.xsf`, `*dJ.xsf`, old logs or scheduler outputs into a fresh input package.

## README / PROGRESS Contract

When creating, promoting, deriving or validating an L8 directory, update README / PROGRESS with at least:
- `Status`: draft / candidate / formal input / run / output-validated / handoff-ready.
- `Branch`: KNB pure electronic / spin-lattice ion-strain / output validation / mixed / uncertain.
- `File Roles`: `PASP.input`, structure files, direct includes, `spin3.in`, GKNB parameter files, spin-lattice coupling files, force constants, Born charge / elastic files, logs, outputs and helper scripts.
- `Confirmed Settings`: user-confirmed branch, structure route, species / magnetic atom order, `spin3.in` provenance and row order, local axes or coordinate frame, GKNB tensor source, spin-force / stress / strain strategy, smoke-test vs production, expected outputs and run environment.
- `Reference Inventory`: every explicit keyword, block, `%include`, dependent file format and known reference gap.
- `Gate Evidence`: user confirmation, read-only preflight / output validation conclusion and evidence paths.
- `Blocked / TODO`: missing confirmations, missing reference coverage, format uncertainty, stale-output cleanup and next allowed action.

Without these records, do not describe a directory as submit-ready, formal input, validated output or handoff-ready.

## 状态机

### S0：目标目录与 workflow 定位

允许自动执行：
- Inventory the user-specified target directory only: files, directories, inputs, includes, logs, scripts, outputs and stale residues.
- Tentatively classify whether the request is L8 spin-induced polarization, L2 spin-lattice ground-state search, reference lookup, output validation, or source/reference research.
- Identify likely branch clues without making final scientific decisions.

L8 classifiers:
- `PASP.input`, `lattice_model.fdf`, `PASP.used_info`, or user goal contains `Model KNB`, KNB, gKNB, unified polarization model, spin-induced polarization, spiral magnetic-order polarization, `GKNB_inter_site`, `GKNB_single_site`, `GKNB.local_axis`, `Ppair.xsf`, `GKNB_data.*`.
- `Model Spin_lattice_interaction` plus L8-specific polarization clues such as `spin_lat.spin_force`, `spin_lat.spin_int_stress`, `spin_lat.Lspin_int_only`, `spin_strain.dat`, `Zeff.dat`, `elastic.dat`, `FORCE_CONSTANTS`, `SPOSCAR`, `Total P_{ion+lattice}`, `P due to spin force`, or `P due to spin stress`.

禁止：
- Write or overwrite PASP inputs.
- Create formal `input/`, `runs/<run-id>/`, submit scripts or external task configuration.
- Use sibling examples or run notes as current-directory facts.

### S1：Branch and File-Role Inventory

允许自动执行：
- Classify likely branch: KNB pure electronic, spin-lattice ion-strain contribution, output validation, mixed, or uncertain.
- Build a file-role table for actual files in the target/candidate directory.
- Mark files as hard-required, conditional, environment helper, generated output, stale residue, or unknown.
- Draft a reference inventory for every explicit keyword, block, `%include`, dependent file format and numbering rule.

必须记录：
- Whether input explicitly selects `Model KNB` or `Model Spin_lattice_interaction`.
- Structure route and direct `%include` targets.
- `spin3.in` presence, source, expected row order, and whether `Read_init_spin T` is active when using spin-lattice branch.
- For KNB: which GKNB controls are present, including inter-site / single-site tensors, local axes, symmetry polarization, and optional spiral controls.
- For spin-lattice ion-strain: which coupling / response files are present, including `spin_exchange.dat`, `spin_strain.dat`, `FORCE_CONSTANTS`, `SPOSCAR`, `Zeff.dat`, and `elastic.dat`.
- Whether old L8 outputs are present in a directory intended as candidate or formal input.

禁止：
- Promote candidate files to formal `input/`.
- Derive a run directory.
- Create or edit submit-ready helper artifacts.

### S2：Candidate Input Package

允许生成或整理 candidate 包，但必须标注 candidate / not submit-ready。

Candidate package should include or explicitly mark missing:
- `PASP.input` with draft L8 route and branch controls.
- Direct `%include` targets and structure route files.
- `spin3.in` when the branch reads an explicit spin configuration.
- Common structure / species / visualization controls such as `SuperCell`, `Z_values`, `isaAB`, `SYMPREC`, `fig.maxk`, `fig.mdist`, and `Spin_values` when current branch needs them.
- For KNB: branch-confirmed GKNB parameter files / blocks and local-axis data.
- For spin-lattice ion-strain: branch-confirmed `spin_exchange.dat`, `spin_strain.dat`, `FORCE_CONSTANTS`, `SPOSCAR`, `Zeff.dat`, `elastic.dat`, and spin-lattice / phonon controls.
- README / PROGRESS with file roles, user-confirmation status, reference inventory and blocked items.

Agent-derivable artifacts are limited to:
- README / PROGRESS, file inventory, reference inventory notes and candidate labels.
- Draft settings tables for user confirmation.
- Clearly labeled smoke-test candidates when the user accepts smoke-test intent and exact writes are reference-backed.

禁止：
- Promote to formal `input/`.
- Derive `runs/<run-id>/`.
- Create submission artifacts as submit-ready.
- Fill production GKNB tensors, local axes, Born charges, force constants, elastic constants, spin-strain derivatives, spin configurations, `fig.maxk`, or `fig.mdist` from examples.

### S3：L8 Settings Confirmation（STOP REQUIRED）

Before formal input, run derivation, submission-preparation or submission, the user must confirm or explicitly accept a settings table.

必须确认：
- Workflow branch and stage.
- Structure route, species / atom order, magnetic atom set, and `SuperCell` / structure relationship.
- `spin3.in` source, row order, and whether it corresponds to the current calculation cell.
- For KNB: pure electronic objective, GKNB tensor provenance, local-axis convention, symmetry polarization strategy, optional spiral `qvec` / plane-vector strategy, and expected output family.
- For spin-lattice ion-strain: whether the target is spin-force, spin-stress / strain, ion displacement, lattice contribution, or a combined summary; provenance for `spin_exchange.dat`, `spin_strain.dat`, `FORCE_CONSTANTS`, `SPOSCAR`, `Zeff.dat`, and `elastic.dat`; phonon / Born-charge / elastic flags; and whether this is a smoke test or production run.
- For spin-lattice ion-strain with `spin_lat.spin_int_stress T`: planned MPI rank count. Current validated source/runtime only supports the `read_spin_stress` path with one MPI rank; planned ranks greater than 1 require explicit fixed-source evidence or must be changed to a one-task diagnostic / serial run before submission preparation.
- Expected outputs and output-validation target.
- Run environment and whether submission is requested.

确认后记录：
- `USER_CONFIRMED_L8_POLARIZATION_SETTINGS=true`
- settings table, source, and remaining reference / preflight gaps.

未满足时允许的唯一下一步：list missing confirmations or continue drafting candidate notes. Do not promote formal input, derive run, prepare submission or submit.

### S4：Input Preflight（STOP ON FAIL）

Candidate package promotion, formal input overwrite, run derivation, submit-ready helper editing, external task preparation and submission all require read-only input preflight first.

执行方式：
- Use `skills/subskills/pasp-verifier/skill.md`, `mode: input-preflight`.
- Inputs must name workflow `L8 spin-induced polarization`, target branch, exact candidate directory, user-confirmation record and reference inventory.
- Preflight checks the actual candidate package, not sibling examples or run notes.

L8 checklist minimum:
- `PASP.input` structural parse, direct include graph, duplicate first-wins behavior and explicit `Model KNB` or `Model Spin_lattice_interaction`.
- Structure route and direct include files present and same-package.
- `spin3.in` exists when required and has current-structure row-order provenance.
- Common controls such as `SuperCell`, `Z_values`, `isaAB`, `Spin_values`, `fig.maxk`, `fig.mdist`, and `SYMPREC` align with user-confirmed current-material facts when present.
- KNB branch dependencies and GKNB controls are present or marked blocked.
- Spin-lattice ion-strain branch dependencies are present or marked blocked.
- Every explicit keyword, block, include target, file format and numbering rule has reference/user-authoritative coverage.
- No stale L8 outputs are mixed into fresh candidate / formal input.
- README / PROGRESS does not claim submit-ready unless gates have passed.

通过后记录：
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`
- evidence path and remaining limitations.

Fail or blocked means the only allowed next action is fixing candidate files, asking for missing confirmation, or recording blocked evidence. Do not proceed to S5.

### S5：Formal Input / Run / Submission Preparation

Allowed only when all flags exist:
- `USER_CONFIRMED_L8_POLARIZATION_SETTINGS=true`
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`

S5 才允许：
- Promote or overwrite formal `input/`.
- Derive `runs/<run-id>/` from formal `input/`.
- Add current-run helper scripts, executable path, stdout / stderr plan and scheduler facts inside the run directory.
- Prepare external task configuration.

S5 run-environment gate:
- If branch is spin-lattice ion-strain and `spin_lat.spin_int_stress T` is active, planned MPI ranks must be `1`, unless the README / PROGRESS records explicit fixed-source evidence that `read_spin_stress` MPI support exists. Multi-rank submission preparation is blocked for the current validated PASP image.

进入 S5 必须记录：
- formal `input/README.md`: source candidate, preflight evidence, reference inventory and confirmation flags.
- `runs/<run-id>/README.md`: source input, helper files, command / scheduler facts, expected outputs, stdout / stderr, smoke-test vs production label.

Submission remains separate. Even with S5 flags, actual job submission needs explicit user submission authorization.

### S6：Output Validation（STOP ON FAIL）

After a run completes and before reporting polarization components, visualizations, force/stress contributions or downstream handoff, run output validation.

执行方式：
- Prefer `skills/subskills/pasp-verifier/skill.md`, `mode: output-validation`.
- Inputs must name exact run/output directory, expected output files, logs and branch.

L8 validation minimum:
- PASP stdout / scheduler log normal completion or first decisive failure.
- `PASP.used_info` when present confirms same-run model and effective branch settings, but do not rely on it alone if the file is minimal.
- For pure electronic KNB: normal completion plus branch-consistent polarization summaries, and same-run `spin3.xsf`, `Ppair.xsf`, and `GKNB_data.*` when expected by current settings.
- For spin-lattice ion-strain: normal completion plus summaries such as `Pion,Pcell`, `Total P_{ion+lattice}`, `P due to spin force`, and `P due to spin stress`; reported displacements / strain / induced stress must be tied to same-run inputs.
- If `log.out` contains `read_spin_stress: MPI version not implemented yet`, validation fails for that run even when the platform scheduler status is successful. Record it as a multi-rank source/runtime limitation and do not hand off `P due to spin stress` from that failed run.
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
- Summarize validated pure electronic polarization contributions with source run id.
- Summarize validated ion / lattice / strain polarization contributions with source run id.
- Compare KNB and spin-lattice contribution runs only when both outputs have validation evidence and the structure / spin configuration relationship is recorded.
- Report visualization files only from validated same-run output.

禁止：
- Claim total physical polarization, production convergence, or coordinate-frame correctness from unvalidated outputs.
- Treat historical GKNB tensors, local axes, Born charges, force constants, elastic constants, or polarization numbers as current results.
- Reuse output validation as input preflight for a new run.
