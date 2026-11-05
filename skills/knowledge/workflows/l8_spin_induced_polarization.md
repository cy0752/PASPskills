# L8 Spin-Induced Polarization Workflow

本文件是 L8 spin-induced polarization workflow 的稳定运行契约。runtime agent 必须先读 `l8_spin_induced_polarization_state_machine.md` 判定状态和 STOP gate；本文件只补充当前状态所需的输入、输出、可调项和 reference handoff。Lecture-8 examples 和 `l8_spin_induced_polarization_run_notes.md` 是历史观察，不是当前用户目录事实，也不是参数默认值。

## 目标

基于给定自旋构型、自旋-晶格耦合、Born 电荷 / 力常数 / 弹性响应和 KNB / gKNB 统一极化模型，计算或分析自旋序诱导极化与相关磁电耦合现象。

当前 MVP 覆盖两条分支：
- B1：`Model KNB` 的 pure electronic KNB / gKNB 极化贡献。
- B2：`Model Spin_lattice_interaction` 的 ion / lattice / strain contribution through spin-lattice coupling。

## 适用问题

- 我想根据自旋构型计算自旋诱导极化。
- 我想做 KNB / gKNB / unified polarization model。
- 我想分析螺旋磁序诱导极化。
- 我想把纯电子贡献和离子 / 晶格 / 应变贡献分开算。
- 我已经有 `spin3.in`、GKNB 参数、`Zeff.dat`、`FORCE_CONSTANTS`、`elastic.dat` 或 `spin_strain.dat`，想检查下一步。

## 不适用 / 应转路由

- 用 `spin_exchange.dat` 做 PTMC / CG 找磁基态，或准备 `spin3_lowest.out` / `node_N_spin.out`：转 L2 `Spin_lattice_interaction` workflow。
- 只问某个参数、block 或文件格式的精确定义：转 reference。
- 从结构出发拟合有效哈密顿量、做 MD/MC/GA/TB：转对应 L3-L7 workflow。

## 核心输入包

所有 L8 candidate input package 至少需要：
- `PASP.input`，显式写 `Model KNB` 或 `Model Spin_lattice_interaction`。
- 结构路线：`cell.str` / `unit_cell.str`、直接 `%include` 目标，或 reference/user-authoritative source 支持的等价路线。
- `spin3.in` when the branch reads an explicit spin configuration, with row-order provenance for the current calculation cell.
- `SuperCell`, `Z_values`, `isaAB`, `Spin_values`, `fig.maxk`, `fig.mdist`, `SYMPREC` 等当前分支使用到的结构 / species / visualization / symmetry controls。
- README / PROGRESS，记录 branch、file roles、user confirmation、reference inventory、preflight evidence 和 blocked items。

Environment helpers such as scheduler scripts or plotting helpers are helpers, not portable PASP input defaults.

## Branches

### B1：Pure Electronic KNB / gKNB

Use when the user wants electronic spin-order-induced polarization from a supplied spin configuration and GKNB / KNB parameters.

Hard inputs:
- `PASP.input`
- structure include/route
- `spin3.in` or an explicitly confirmed spiral / spin-configuration route
- `SuperCell`, `Z_values`, `isaAB`, `Spin_values` when current branch needs them
- GKNB parameter controls such as `GKNB.symP`, `GKNB_inter_site`, `GKNB_single_site`, and `GKNB.local_axis` as required by the selected model

Conditionally important:
- `GKNB.spiral`, `GKNB.qvec`, and `GKNB.spiral_plane_vec` when the branch constructs or modifies a spiral spin order.
- `fig.maxk` and `fig.mdist` when the branch uses symmetry / pair-search style scope controls.

Important checks:
- `Model KNB` is explicit.
- `spin3.in` row order and magnetic/nonmagnetic rows correspond to the current calculation cell.
- GKNB tensor and local-axis provenance are current-material facts or user-confirmed; do not copy example tensors.
- Local axes, tensor components, spin vector convention and reported polarization frame are all treated as high-risk. Exact syntax and row order must come from reference or user-authoritative files before writing.
- If `GKNB.spiral T` is active, `qvec` and `spiral_plane_vec` must be confirmed together; do not infer a spiral plane from material name or example.

Typical outputs / validation anchors:
- log / stdout normal completion, ideally `PASP is finished gracefully`.
- polarization summaries such as `Intersite P`, `Intersite P (Exchange striction)`, `spin_FE: Dipole is`, or `spin_FE: P is` when present.
- `spin3.xsf`
- `Ppair.xsf`
- `GKNB_data.*`

### B2：Ion / Lattice / Strain Contribution Through Spin-Lattice Interaction

Use when the user wants polarization contribution from spin-lattice force, induced displacement, stress / strain, Born charge, force constants or elastic response.

Hard inputs observed for this branch:
- `PASP.input`
- structure include/route
- `spin3.in` when `Read_init_spin T`
- `spin_exchange.dat`
- `spin_strain.dat` when strain derivatives are active
- `FORCE_CONSTANTS` and `SPOSCAR` when phonopy force constants are active
- `Zeff.dat` for Born-charge polarization support
- `elastic.dat` when elastic / piezoelectric / strain response is active
- `SuperCell`, `Z_values`, `isaAB`, `Spin_values`, `fig.maxk`, `fig.mdist`, `SYMPREC` when current settings use them

Conditionally important controls:
- `spin_lat.spin_force`
- `spin_lat.Lspin_int_only`
- `spin_lat.spin_int_stress`
- `Read_init_spin`
- `phonopy_force_constant`
- `phon.lasr`
- `phon.sym_born_chg`

Important checks:
- This branch uses `Model Spin_lattice_interaction`, but the task goal must be L8 polarization contribution rather than L2 PTMC / CG ground-state search.
- `spin3.in` is current, ordered correctly, and intentionally read by the run when `Read_init_spin T`.
- `spin_exchange.dat` and `spin_strain.dat` are same-material and consistent with each other; `spin_strain.dat` derivative indices must match `spin_exchange.dat`.
- `Zeff.dat`, `FORCE_CONSTANTS`, `SPOSCAR`, and `elastic.dat` must have current-material / current-basis provenance. Do not reuse files only because names match.
- Reference cards now document the basic roles and minimal format/validation constraints for `FORCE_CONSTANTS` and `SPOSCAR`; they do not authorize copying example material values or generating force constants without user/source authority.
- Runtime caveat: `spin_lat.spin_int_stress T` currently routes through `read_spin_stress`, whose validated source path stops when MPI `nodes != 1`. In the current PASP image this L8 spin-stress case failed under 20 MPI tasks with `read_spin_stress: MPI version not implemented yet`, while the same input completed as a one-task diagnostic. Treat planned MPI ranks greater than 1 as blocked for this sub-branch unless the user provides fixed-source evidence; validate from a completed one-task diagnostic or future fixed-source MPI run.
- Do not mix this branch's candidate input with old `Ppair.xsf`, `GKNB_data.*`, old displacement XSF files or old logs.

Typical outputs / validation anchors:
- log / stdout normal completion, ideally `PASP is finished gracefully`.
- log evidence that `spin3.in` was read when expected.
- induced stress, unit-cell displacement and induced strain summaries when the branch computes them.
- polarization summaries such as `Pion,Pcell`, `Total P_{ion+lattice}`, `P due to spin force`, and `P due to spin stress`.
- visualization families such as `1.xsf`, `2.xsf`, `3.xsf`, or `*dJ.xsf` may appear depending on branch/settings/version; treat exact file families as runtime-verified outputs.

## Stages

### S0 / S1：inventory and branch classification

Use the state machine first. Inspect only the user-specified target directory and `knowledge/` unless the user explicitly authorizes cross-example comparison.

Classify:
- branch: B1 pure electronic KNB, B2 spin-lattice ion-strain contribution, output validation, mixed, or uncertain.
- actual files and stale outputs.
- direct `%include` graph.
- exact reference cards needed before any write.

### S2 / S3：candidate package and settings confirmation

Candidate packages can be drafted, but they are not submit-ready. Before formal input or run derivation, record:
- `USER_CONFIRMED_L8_POLARIZATION_SETTINGS=true`
- branch target and stage
- structure route, species order and magnetic atom order
- `spin3.in` provenance and row-order evidence
- GKNB tensor / local-axis / spiral settings for B1, or spin-lattice / Born-charge / force-constant / elastic provenance for B2
- smoke-test vs production intent
- expected outputs and validation target
- reference gaps

### S4：input preflight

Before promoting candidate files, overwriting formal input, deriving a run directory, preparing external submission artifacts, or submitting a job, use `subskills/pasp-verifier/skill.md` with `mode: input-preflight`.

Minimum L8 preflight:
- `PASP.input` parses structurally and explicitly selects `Model KNB` or `Model Spin_lattice_interaction`.
- Direct includes resolve inside the candidate package.
- Branch B1/B2 is explicit and user-confirmed.
- `spin3.in` is present when required and has current cell row-order provenance.
- Common structure / species controls align with current-material facts.
- Branch-specific files are present or blocked.
- Every explicit keyword/block/file has reference or user-authoritative coverage.
- Candidate package has no stale L8 outputs.
- README / PROGRESS does not claim submit-ready before gates pass.

### S5：formal input / run / submission preparation

Allowed only after:
- `USER_CONFIRMED_L8_POLARIZATION_SETTINGS=true`
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`

Then formal `input/`, `runs/<run-id>/`, helper files and submission artifacts may be prepared. Actual submission still requires explicit user submission authorization.

Run-environment rule:
- For B2 with `spin_lat.spin_int_stress T`, the current validated source/runtime supports only one MPI rank for the `read_spin_stress` path. Do not prepare or submit a multi-rank PASP job for this sub-branch unless fixed-source evidence is explicitly recorded. One-task runs are acceptable diagnostics when the user authorizes execution.

### S6 / S7：output validation and handoff

Before reporting polarization components, output visualizations, spin-force/stress decomposition, ion / lattice / strain contributions, or combined comparison as usable, run output validation on the exact completed run/output directory.

Validation targets:
- pure electronic KNB: normal completion evidence, branch-consistent polarization summaries, `spin3.xsf`, `Ppair.xsf`, and `GKNB_data.*` when expected.
- spin-lattice ion-strain: normal completion evidence, `spin3.in` read evidence when expected, induced stress / displacement / strain summaries when active, and polarization summaries such as `Pion,Pcell`, `Total P_{ion+lattice}`, `P due to spin force`, and `P due to spin stress`.

Output validation cannot retroactively authorize an input package.

Do not treat scheduler / platform success alone as output validation. If `log.out` contains `BAD TERMINATION`, `KILLED BY SIGNAL`, `Error, ...`, or lacks the branch's expected completion evidence, mark outputs as dirty / diagnostic even when expected files exist.
If an L8 spin-lattice ion-strain run contains `read_spin_stress: MPI version not implemented yet`, mark it as failed / MPI-limited even when the scheduler status is successful. The next allowed runtime action is a one-task diagnostic run or a future fixed-source MPI rerun, not downstream polarization handoff from the failed multi-rank output.

## Reference Handoff

Route exact definitions, defaults, syntax, row formats or conditional dependencies to reference, especially:
- `modules/knb.md`
- `topics/PASP.input.md`
- `params/Model.md`
- `params/SuperCell.md`
- `params/Z_values.md`
- `params/isaAB.md`
- `params/Spin_values.md`
- `params/SYMPREC.md`
- `params/fig.maxk.md`
- `params/fig.mdist.md`
- `files/spin3.in.md`
- `params/GKNB.symP.md`
- `params/GKNB_inter_site.md`
- `params/GKNB_single_site.md`
- `params/GKNB_local_axis.md`
- `params/GKNB.spiral.md`
- `params/GKNB.qvec.md`
- `params/GKNB.spiral_plane_vec.md`
- `files/spin_exchange.dat.md`
- `files/spin_strain.dat.md`
- `files/Zeff.dat.md`
- `files/elastic.dat.md`
- `files/FORCE_CONSTANTS.md`
- `files/SPOSCAR.md`
- `files/Ppair.xsf.md`
- `files/spin3.xsf.md`
- `files/GKNB_data.NNNNN.md`
- `files/l8_ion_strain_xsf_outputs.md`
- `params/Read_init_spin.md`
- `params/spin_lat.spin_force.md`
- `params/spin_lat.Lspin_int_only.md`
- `params/spin_lat.spin_int_stress.md`
- `params/phonopy_force_constant.md`
- `params/phon.lasr.md`
- `params/phon.sym_born_chg.md`

Basic reference cards now exist for `Ppair.xsf`, `spin3.xsf`, `GKNB_data.*`, `FORCE_CONSTANTS`, `SPOSCAR`, L8 ion/strain visualization output families, and `SYMPREC`. These cards document file roles, writer/reader behavior, parameter roles, and minimal validation boundaries; they are not material-specific data-generation authority. If a future task needs exact physical values, tensor components, force constants, local axes, row-order provenance, or a file detail not covered by the card, record a remaining reference gap and ask for user/source authority before writing exact content.
