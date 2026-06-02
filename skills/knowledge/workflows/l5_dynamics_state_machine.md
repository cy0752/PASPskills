# L5 Dynamics State Machine

本文件是 L5 dynamics workflow 的运行门禁。runtime agent 必须先执行这里的状态机；`l5_dynamics.md` 只补充当前状态所需的输入、输出、可调项和检查细节，不能覆盖本文件的 STOP 条件。

## 核心原则
- L5 MVP 默认指 `Model atomic_effective_H` 的 Cr2O3 spin-lattice relaxation branch：stage 1 lattice heating (`SLD.mode 1`)、stage 2 spin heating (`SLD.mode 2`)、stage 3 coupled SLD relaxation (`SLD.mode 3`)。
- BaTiO3 electric hysteresis 是独立 L5 branch：single-stage `Model atomic_effective_H` MD electric-field run，核心输出验证对象是 `field.dat` 和 `P_abs.dat`。它不是 Cr2O3 `SLD.mode 1/2/3` handoff sequence。
- BaTiO3 lecture/example values can identify historical `MD-1` context, but they are not defaults and cannot authorize production settings.
- Generic / new-material L5 branch 是 material-neutral `Model atomic_effective_H` dynamics input preparation。它要求用户或上游 PASP 阶段提供当前材料的 structure, model products, mode basis, initial state, and conditional physics files；不能从 Cr2O3 / BaTiO3 examples 自动派生这些物理文件或 production settings。
- `继续`、`ok`、`按例子来`、`去提交` 不等于确认 dynamics 设置、`amp_local_mode` handoff 来源、运行环境或提交授权。
- Lecture-5 examples 和 run notes 只提供历史观察；其中的温度、阻尼、时间步、总时长、超胞、mode 数、Slurm 设置、PASP 路径都不是 production default。
- `可以使用 subagent` 只表示允许委派只读事实检查，不等于确认科学设置、不等于允许提交、不等于允许 agent 代填物理参数。
- read-only verifier 任务统一使用 `skills/subskills/pasp-verifier/skill.md` 的契约；subagent 不能改文件、不能创建 run、不能准备提交、不能提交任务、不能决定科学参数。
- input preflight 不是 output validation。运行前用 preflight 判断输入能否进入 run；运行后用 output validation 判断输出能否 handoff。
- `notes/`、`drafts/`、`*.draft` 是草稿区；candidate 目录是待 preflight 候选区；`input/` 是正式输入基线；`runs/<run-id>/` 是实际运行目录。这四类不能混用。
- 不要把 `complete/` 历史快照、旧 `PASP.used_info`、旧 `*_used.dat`、旧日志、旧 `temperature.dat`、旧 `energy.dat` 复制进新 run。

## README / PROGRESS 契约
创建、提升、派生或完成 L5 关键目录时，应同步写入或更新 README / PROGRESS。最低字段：
- `Status`：当前阶段，是否 draft / candidate / formal input / run / output-validated / handoff-ready。
- `Branch and Stage`：generic new-material MD / LLG / ASD / SLD、Cr2O3 SLD stage 1 / 2 / 3、BaTiO3 electric hysteresis single-stage MD、output validation 或 handoff。
- `File Roles`：`PASP.input`、`MD.input`、结构文件、上游模型文件、`amp_local_mode.in` / `.out`、提交 helper、输出文件分别是什么。
- `Confirmed Settings`：用户确认过的 workflow branch、generic active degrees of freedom、`SLD.mode` intent 或 BaTiO3 electric-field / polarization intent、supercell / model provenance、time-step / run length、damping、temperature、initial velocity、output cadence、run environment。
- `Upstream` / `Downstream`：`local_mode_PM.dat`、`J_best.dat`、`amp_local_mode` handoff 或 BaTiO3 `field.dat` / `P_abs.dat` analysis handoff 的来源、run id、验证证据和去向。
- `Gate Evidence`：用户确认记录、reference inventory、read-only preflight / output validation 结论和证据路径。
- `Blocked / TODO`：缺哪些确认、哪些文件不可提交、哪些输出不可 handoff、下一步允许做什么。

没有这些记录时，不得把目录描述为 submit-ready、formal input、validated output 或 handoff-ready。

## 状态机

### S0：目标目录与 workflow 定位
允许自动执行：
- 盘点用户给定目标目录自己的文件、阶段目录、输入、输出、日志和提交 helper。
- 暂定判断是 Cr2O3 three-stage SLD、BaTiO3 electric hysteresis single-stage MD、generic new-material MD / ASD / LLG / SLD / electric-field response、已有输出验证，还是其他 workflow。
- 记录当前事实和不确定项；不能用 sibling examples 或 run notes 覆盖目标目录事实。

Cr2O3 L5 MVP 判据：
- `PASP.input` / `MD.input` 指向 `Model atomic_effective_H` 和 `atom_Heff.MD T`。
- `MD.input` 或 included content 包含 `SLD.mode 1`、`SLD.mode 2` 或 `SLD.mode 3`。
- 输入包依赖 `local_mode_PM.dat`、`J_best.dat`、`amp_local_mode.in`、结构文件和 local-mode / mass definition split files。
- 目录或用户目标描述 lattice heating、spin heating、spin-lattice relaxation、subsystem temperature evolution, or `temperature.dat` spin / lattice columns。

BaTiO3 electric-hysteresis branch 判据：
- 用户目标描述 BaTiO3、electric hysteresis、electric-field MD、polarization-vs-field、`field.dat` / `P_abs.dat` analysis, or Lecture-5 `MD-1`.
- `PASP.input` / `MD.input` points to `Model atomic_effective_H` and `atom_Heff.MD T`.
- `MD.input` or included content uses time-dependent electric-field controls such as `MD.E_type`, `MD.E_x/y/z`, `MD.E_omega`, `MD.E_phi`, or `Field_for_Electrocaloric`.
- Polarization path is expected through `atom_Heff.getP T` or `MD.E_type > 0` source-backed behavior, with `Zeff.dat` provenance checked before accepting `P_abs.dat`.
- Branch output intent is `field.dat` plus `P_abs.dat`; `temperature.dat` and `energy.dat` are diagnostics, not the primary hysteresis handoff.

BaTiO3 branch classification must not import Cr2O3 stage meanings from `SLD.mode`. `SLD.mode 1` can appear in the BaTiO3 MD driver, but the branch is classified by electric-field/polarization intent and output targets.

Generic / new-material branch 判据：
- 用户目标描述 new material, arbitrary material, generic `atomic_effective_H` dynamics, smoke-test input preparation, plain MD, LLG / ASD, SLD, electric-field response, or output validation without tying the package to the Cr2O3 / BaTiO3 historical branches.
- `PASP.input` / `MD.input` 或用户说明指向 `Model atomic_effective_H` and dynamics under `atom_Heff.MD` / LLG / ASD / SLD controls.
- Candidate package contains or expects upstream `local_mode_PM.dat`, `J_best.dat`, structures, mode definition / mass definition, `amp_local_mode.in` when current settings read an initial state, and conditional files according to current settings.
- Branch classification depends on current model controls, active degrees of freedom, user goal, and expected outputs, not on copying a historical material name.

禁止：
- 写正式 `PASP.input` / `MD.input`。
- 创建或覆盖正式 `input/`。
- 创建 `runs/<run-id>/`、提交脚本或外部任务配置。

### S1：上游模型与候选材料整理
允许自动执行：
- 清点候选输入包是否包含 `PASP.input`、`MD.input`、结构文件、`local_mode_PM.dat`、`J_best.dat`、current settings 读取 initial state 时的 `amp_local_mode.in`、direct `%include` split files 和环境 helper。
- 标出 `Zeff.dat`、`elastic.dat`、`spin_strain.dat` 等条件文件：只有当前设置或 reference 建立依赖时才列为该 stage 必需。
- 整理缺失项、来源疑问、reference inventory 草表。
- 在 `notes/`、`drafts/` 或 candidate 目录保存明确标注“不可提交 / 待 preflight”的候选材料。

必须确认或记录的上游事实：
- `local_mode_PM.dat` 和 `J_best.dat` 是否来自同一材料、同一结构、同一 local-mode / interaction basis。
- 如果上游来源是 L3，记录 L3 Step 6 / Step 7 output-validation README / PROGRESS 路径；它应说明 `local_mode_PM.dat`、拟交给 L5 的 fitted-parameter file（通常是 runtime-validated `J_best.dat` 或等价选择记录）、结构 route、`SuperCell`、`Z_values`、`Spin_values`、mode / mass definition、fitting dataset / settings provenance 和 known gaps。不能用 L3 template、Lecture-5 example 或 run notes 替代当前材料的 handoff record。
- 当前 workflow 是消费已建立的 `atomic_effective_H` model 做 dynamics，而不是回到 L3 重新拟合。
- Generic / new-material branch 中，`cell.str` / `unit_cell.str` or equivalent structure route、`SuperCell`、species / spin values、mode definition、mass definition、`local_mode_PM.dat`、`J_best.dat`、以及 current settings 读取 initial state 时的 `amp_local_mode.in` 是否来自同一 current-material effective-H basis。
- Generic / new-material branch 中，`Zeff.dat`、`elastic.dat`、`spin_strain.dat`、`Field_for_Electrocaloric` 等 conditional inputs / dependencies 只有在 current settings, reference, or user authority 建立依赖时才作为硬检查对象。
- stage 2 的 `amp_local_mode.in` 是否来自已验证 stage 1 `amp_local_mode.out`。
- stage 3 的 `amp_local_mode.in` 是否来自已验证 stage 2 `amp_local_mode.out`。
- BaTiO3 branch 中，`cell.str`、`unit_cell.str`、`local_mode_PM.dat`、`J_best.dat`、`amp_local_mode.in`、`local_mode.mode_definition` / split definition、`atom_Heff.MASS_local_mode`、`Zeff.dat` 是否来自同一 BaTiO3 effective-H / unit-cell / local-mode basis。
- BaTiO3 branch 中，`Zeff.dat` 只有在 polarization path active 时作为硬检查对象；`atom_Heff.getP T` 或 active electric field path 都需要检查它与当前 `unit_cell.str` / mode basis 的一致性。

禁止：
- 把候选材料放进正式 `input/` 并称为可提交。
- 静默覆盖 downstream `amp_local_mode.in`。
- 生成 submit-ready 脚本或外部任务配置。

### S2：候选 stage 输入包
允许生成或整理 candidate 包，但必须清楚标注 candidate / 待 preflight。

候选包至少应覆盖：
- `PASP.input`：模型、结构 include、`MD.input` include、local-mode / interaction-reuse 控制、stage-stable model settings。
- `MD.input`：`atom_Heff.MD`、`SLD.mode`、time-step / run length、LLG and MD damping、temperature / initial velocity、output cadence。
- 结构和上游模型文件：`cell.str`、`unit_cell.str` 或等价结构输入，`local_mode_PM.dat`、`J_best.dat`。
- local-mode definition / mass files：凡是 `PASP.input` 直接 `%include` 的 split files 都要进入候选包；`mode_def.input` / `mode_mass.input` 的文件角色见 `skills/knowledge/reference/files/mode_def.input.md` 和 `skills/knowledge/reference/files/mode_mass.input.md`，exact block syntax 仍由 param reference 确认。
- `amp_local_mode.in`：stage initial state；stage 2 / 3 必须记录 upstream completed run identity and output-validation evidence。
- README：说明文件角色、上游来源、待确认设置、reference inventory 状态、为什么当前还不能提交。

BaTiO3 electric-hysteresis candidate package should cover:
- `PASP.input`: `Model atomic_effective_H`, direct `%include` graph, structure route, `SuperCell`, `Z_values`, local-mode / interaction-reuse controls, mode definition, mass definition, and model provenance.
- `MD.input`: `atom_Heff.MD`, time-step / run length, damping / temperature, output cadence, electric-field controls, `atom_Heff.getP`, and `local_mode.MD_mode_range` when used.
- Hard-required current-run inputs: `PASP.input`, `MD.input`, `cell.str`, `unit_cell.str`, `local_mode_PM.dat`, `J_best.dat`, `amp_local_mode.in`, and every direct `%include` target.
- Conditional polarization input: `Zeff.dat` when `atom_Heff.getP T` or active electric-field behavior requires BEC polarization support.
- Environment helper: `run.sh`, `sub_pasp`, scheduler config, executable path, MPI rank count, stdout / stderr routing. These are not scientific defaults.
- README: mark the package as candidate / not submit-ready, record field/polarization intent, local-model provenance, `Zeff.dat` provenance status, planned MPI ranks, and reference gaps.

Generic new-material `atomic_effective_H` candidate package should cover:
- `PASP.input`: `Model atomic_effective_H`, direct `%include` graph, structure route, `SuperCell`, species / spin values when applicable, model-consumption controls, mode definition, mass definition, and provenance notes.
- `MD.input`: active dynamics branch, time-step / run length, damping / temperature / ensemble intent, output cadence, optional LLG / ASD / SLD / electric-field controls, and expected output targets.
- Hard-required current-route inputs: `PASP.input`, `MD.input` when used, structure files or documented equivalent, `local_mode_PM.dat`, `J_best.dat`, `amp_local_mode.in` when initial state is read, and every direct `%include` target.
- Conditional inputs: `Zeff.dat`, `elastic.dat`, `spin_strain.dat`, `Field_for_Electrocaloric`, `local_mode.MD_mode_range`, or branch-specific files only when current settings/reference/user authority establish dependency.
- Environment helper: command, scheduler config, executable path, MPI rank count, stdout / stderr routing. These are run-environment facts only.
- README: mark the package as candidate / not submit-ready, record current-material provenance, active degrees of freedom, user-confirmed branch intent, smoke-test vs production label, planned MPI ranks, reference gaps, and blocked items.

禁止：
- 提升为正式 `input/`。
- 派生 `runs/<run-id>/`。
- 创建或编辑提交脚本作为 submit-ready artifact。

### S3：L5 dynamics 设置确认（STOP REQUIRED）
进入 formal input、run derivation 或 submission preparation 前，必须有用户确认或用户明确接受一份逐项设置表。

必须确认：
- workflow branch：generic new-material MD / LLG / ASD / SLD / electric-field response、Cr2O3 stage 1 lattice heating、stage 2 spin heating、stage 3 coupled SLD relaxation、BaTiO3 electric hysteresis single-stage MD、已有输出验证，或其他 out-of-scope branch。
- 上游模型来源：`local_mode_PM.dat`、`J_best.dat`、结构、`mode_def.input` / mode definition、`mode_mass.input` / mass definition、拟合数据链是否来自同一模型基底。
- `amp_local_mode` handoff：stage 1 初始态来源；stage 2 来自哪个 validated stage 1 run；stage 3 来自哪个 validated stage 2 run。
- `SuperCell` / 系统尺寸与目标物理周期、内存和时间预算是否合适；如果是 smoke-test reduction 且 current settings read an initial state，`amp_local_mode.in` row count 是否匹配 reduced simulation cell；planned MPI ranks 是否兼容 `SuperCell` determinant / workflow requirement。
- Generic / new-material branch active degrees of freedom：plain MD、LLG / ASD、SLD、electric-field / polarization response、smoke-test, equilibration, production, output validation, or downstream handoff；expected primary outputs and validation target.
- dynamics 设置意图：`SLD.mode`、`LLG.method`、`MD.Delta_t`、`atom_Heff.MD_time`、`LLG.damping`、`MD.damping`、`MD.temperature`、`MD.init_velocity_temp`、`MD.aft_step`、`MD.int_step`、`MD.output_amp_lm`。
- BaTiO3 electric-field / polarization intent when that branch is active：`MD.E_type`、`MD.E_x/y/z`、`MD.E_omega`、`MD.E_phi`、`Field_for_Electrocaloric` if used、`atom_Heff.getP`、`Zeff.dat` provenance、`local_mode.MD_mode_range` intent、which `P_*` vs `E_*` components the user wants to plot.
- BaTiO3 periodic/cosine-field planning when that branch is active：whether `atom_Heff.MD_time` covers the intended field period(s); for cosine field use `T = 2*pi / MD.E_omega` only after current input/reference confirms units and semantics. Confirm whether `MD.aft_step` is demonstration-style recording or production equilibration, and that it leaves a nonempty sampled window before the total MD steps are exhausted.
- ensemble / thermostat intent：stage 1 / 2 是否为受热 bath dynamics；stage 3 是否为 coupled relaxation / NVE-like run；exact semantics still require reference.
- 输出与 handoff 目标：是否需要 `temperature.dat`、`energy.dat`、`amp_local_mode.out`、spin / lattice temperature trend、energy conservation, or downstream stage input。
- 运行环境信息：计划命令、MPI ranks、scheduler / image / executable、stdout / stderr 路径。

确认后记录：
- `USER_CONFIRMED_L5_DYNAMICS_SETTINGS=true`
- 设置表、来源、仍需 reference 或 preflight 检查的项。

未满足时允许的唯一下一步：列出缺失确认项或继续写 draft / candidate notes；不得提升正式 input、派生 run、准备提交或提交。

### S4：Input Preflight（STOP ON FAIL）
候选输入包提升为正式 `input/`、覆盖 input、派生 `runs/<run-id>/`、创建或编辑 submission artifacts、准备外部任务配置、提交任务前，必须先做 read-only input preflight。

执行方式：
- 使用 `skills/subskills/pasp-verifier/skill.md`，`mode: input-preflight`。
- preflight 必须点名 workflow、target stage、候选输入文件 / 目录、stage-specific checklist、用户确认记录、reference inventory。
- 对 PASP 输入文件，preflight 必须检查每个显式 keyword、block、`%include`、依赖文件格式和编号规则是否有 `skills/knowledge/reference/` 或用户权威来源覆盖。
- 主 agent 本地检查、目录盘点、模板对比、日志检查不能替代这一步。
- 若 read-only verifier 无法执行，L5 formal input / run / submission preparation 必须 blocked；`NO_SUBAGENT_PREFLIGHT_AVAILABLE=true` 不足以继续。

L5 Cr2O3 preflight checklist 至少包括：
- 文件齐备：`PASP.input`、`MD.input`、结构文件、`local_mode_PM.dat`、`J_best.dat`、`amp_local_mode.in`、所有 direct `%include` files。
- 上游一致性：模型基底、结构、`mode_def.input` / mode definition、`mode_mass.input` / mass definition、`Z_values` / `Spin_values`、`local_mode.read_interaction`、`Read_init_spin` 没有无说明混用。
- stage / `SLD.mode` 一致：stage 1 -> `SLD.mode 1`，stage 2 -> `SLD.mode 2`，stage 3 -> `SLD.mode 3`。
- 如果候选包降低了 `SuperCell` 做 smoke test，`amp_local_mode.in` row count 必须匹配 reduced simulation cell；planned MPI ranks 必须与 `SuperCell` determinant / workflow requirement 兼容，unknown 或 incompatible ranks 在提交准备前 blocked。
- damping / temperature / initial-velocity intent 与用户确认表一致；不把 historical example values 当默认值。
- stage 2 / 3 `amp_local_mode.in` 的 upstream run id、source path、output-validation evidence 和 copy/rename action 已记录。
- `PASP.input` direct includes 在候选包中可解析；重复 setting / block 不让后续 inactive declaration 被误改。
- 条件文件只按 reference 或用户设置要求列为必需；不能因历史 example 出现就推广。
- README、脚本、目录名没有把 candidate 写成 submit-ready。

L5 generic / new-material preflight checklist 至少包括：
- 文件齐备：`PASP.input`、`MD.input` when used、structure files or documented equivalent route、`local_mode_PM.dat`、`J_best.dat`、`amp_local_mode.in` when current settings read an initial state、所有 direct `%include` files。
- Include resolution starts at the candidate package root; duplicate settings / inactive declarations are reported rather than silently edited.
- Branch consistency：`Model atomic_effective_H` and current dynamics controls match the user-confirmed branch target: MD, LLG / ASD, SLD, electric-field / polarization response, smoke test, production, output validation, or handoff.
- L3 handoff evidence when applicable：the candidate README / PROGRESS cites the current-material L3 output-validation record, not a historical example; any missing `J_best.dat`, mode mass, initial state, `Zeff.dat`, or production dynamics setting is reported as blocked / user-owned instead of silently filled.
- Upstream same-basis provenance：structure route、`SuperCell`、species / spin values、mode definition、mass definition、`local_mode_PM.dat`、`J_best.dat`、`local_mode.read_interaction`、`Read_init_spin`、and `amp_local_mode.in` when current settings read an initial state have same-material evidence or are blocked for user confirmation.
- Conditional inputs / dependencies：`Zeff.dat`、`elastic.dat`、`spin_strain.dat`、`Field_for_Electrocaloric`、`local_mode.MD_mode_range` or other branch-specific dependencies are required only when current settings/reference/user authority establish dependency.
- `SuperCell` vs `amp_local_mode.in` consistency when current settings read an initial state：row count and current local-mode/site basis match. Smoke-test reductions must keep `SuperCell`, initial state, and planned MPI ranks compatible.
- Dynamics settings：`MD.Delta_t`、`atom_Heff.MD_time`、`SLD.mode` when active、`LLG.method`、`LLG.damping`、`MD.damping`、`MD.temperature`、`MD.init_velocity_temp`、`MD.aft_step`、`MD.int_step`、`MD.output_amp_lm`, and branch-specific controls have user-confirmation or authoritative evidence.
- No historical Cr2O3 / BaTiO3 numeric values, model files, mode counts, field schedules, or scheduler settings are presented as current-material defaults.
- Planned MPI ranks / scheduler helper / executable path are treated as environment facts and checked for compatibility before submission preparation; unknown or incompatible ranks block submission preparation.
- No stale outputs, historical `complete/` residues, old `PASP.used_info`, old `*_used.dat`, old logs, old `temperature.dat`, old `energy.dat`, old `field.dat`, or old `P_abs.dat` are mixed into a new run package.
- README、脚本、目录名没有把 candidate 写成 submit-ready。

L5 BaTiO3 electric-hysteresis preflight checklist 至少包括：
- 文件齐备：`PASP.input`、`MD.input`、`cell.str`、`unit_cell.str`、`local_mode_PM.dat`、`J_best.dat`、`amp_local_mode.in`、所有 direct `%include` files。
- Include resolution starts at the candidate package root; duplicate settings / inactive declarations are reported rather than silently edited.
- Branch consistency：`Model atomic_effective_H`、`atom_Heff.MD T`、electric-field controls present for an electric-hysteresis run, and the branch is not treated as a Cr2O3 `SLD.mode 1/2/3` stage sequence.
- `atom_Heff.getP` / electric-field / `Zeff.dat` consistency：if polarization output is requested or active electric field requires BEC support, `Zeff.dat` exists and its provenance is compatible with current `unit_cell.str`, species order, and local-mode basis.
- Local model provenance：`local_mode_PM.dat`、`J_best.dat`、structure files, `Z_values`, mode definition, mass definition, `local_mode.read_interaction`, and `Read_init_spin` have same-basis evidence or are blocked for user confirmation.
- `SuperCell` vs `amp_local_mode.in` consistency：row count and current local-mode/site basis match. If the run is a smoke-test reduction, both `SuperCell` and initial amplitudes must be reduced/regenerated consistently.
- Period/window consistency：for periodic/cosine field intent, planned `atom_Heff.MD_time` covers the user-confirmed period count, and `MD.aft_step` is less than total MD steps so `field.dat` / `P_abs.dat` can record a useful window. If `MD.aft_step >= total_steps`, demonstration plotting is blocked; production equilibration intent must be explicitly user-confirmed and paired with a longer run or different analysis window.
- `local_mode.MD_mode_range`, when present, has reference/user-authority coverage, row count / component scope compatible with the current local-mode basis, and lower bound not greater than upper bound.
- Planned MPI ranks / scheduler helper / executable path are treated as environment facts and checked for compatibility before submission preparation; unknown or incompatible ranks block submission preparation.
- No stale outputs, historical `complete/` residues, old `PASP.used_info`, old `field.dat`, old `P_abs.dat`, old `*_used.dat`, or old logs are mixed into a new run package.
- README、脚本、目录名没有把 candidate 写成 submit-ready，也没有把 MD-1 historical values 写成 production defaults。

通过后记录：
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`
- pass / fail / blocked 结论、证据路径、仍不可做的动作。

fail 或 blocked 时允许的唯一下一步：输出阻断原因、证据路径和需要修正 / 确认的项。

### S5：正式 input / run / 提交准备
只有全部前置 flag 存在，才允许进入 S5：
- `USER_CONFIRMED_L5_DYNAMICS_SETTINGS=true`
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`

S5 才允许：
- 提升或覆盖正式 `input/`。
- 从正式 `input/` 派生 `runs/<run-id>/`。
- 在 run 目录内接入上游 handoff 文件、提交 helper、实际运行命令。
- 准备外部任务配置。

进入 S5 必须同步记录：
- formal `input/README.md`：来源 candidate、preflight 证据、关键确认 flag、字段/reference inventory。
- `runs/<run-id>/README.md`：派生自哪个 input、接入哪些 upstream products、计划命令 / MPI ranks / scheduler / executable / image、stdout / stderr、预期输出。

派生 `runs/<run-id>/` 时：
- 只复制当前运行需要的科学输入、direct `%include` 文件、条件输入文件和提交 helper。
- 不复制旧输出、旧日志、旧 `PASP.used_info`、旧 `*_used.dat`、旧 `temperature.dat`、旧 `energy.dat` 或历史 XSF / diagnostic outputs。
- 如果为了快速验证 workflow 创建短时长 run，必须在 README 和最终答复中明确标为 `smoke-test`，不能描述成 production relaxation。

即使 S5 前置 flag 齐全，真正提交外部任务前仍必须得到用户明确提交授权。`继续`、`ok`、`可以使用 subagent` 都不是提交授权。

### S6：Output Validation（STOP ON FAIL）
运行完成后、绘图或 downstream handoff 前，必须做 output validation。优先委派给 `pasp-verifier` `mode: output-validation`。

检查至少包括：
- 日志正常结束证据，例如 `PASP is finished gracefully` 或用户环境中等价的 PASP 完成 marker。
- `PASP.used_info` 若存在应检查其中的 effective-setting evidence；若缺失、稀疏或不完整，记录为限制，不自动 pass / fail。
- 通过 `MD.input`、`PASP.input`、completion log evidence 和输出文件交叉确认实际 `Model`、`atom_Heff.MD`、`SLD.mode`、`LLG.*`、`MD.*`、`local_mode.read_interaction`、`Read_init_spin` 是否与 formal input 和确认表一致；只有 combined evidence 不足或互相矛盾时才 fail / blocked。
- `temperature.dat` 存在，header / columns 能支持 `spin (K)` and `latt (K)` subsystem checks。
- `energy.dat` 存在，header / columns 能支持 energy time-series check；stage 3 若被用户定义为 NVE-like coupled relaxation，应检查是否有能量漂移风险证据。
- `temperature.dat` / `energy.dat` sampled rows should be monotonic in step / time and consistent with the observed output cadence. Do not fail solely because the last sampled row is before the final MD step when completion evidence shows the run reached the final step.
- `amp_local_mode.out` 存在且可作为该 stage final state；stage 1 / 2 的 downstream handoff 必须记录 exact file path and run id。
- branch-consistent qualitative outputs：stage 1 重点检查 lattice column behavior，stage 2 重点检查 spin column behavior，stage 3 检查 both subsystem columns evolve。具体科学阈值由用户 / 科学负责人确认，不由 workflow 自动判定。
- scheduler stdout / stderr、PASP stderr、warning / error 是否影响 handoff。

Generic / new-material output validation uses the user-confirmed primary target:
- For thermal / relaxation / SLD targets, validate completion evidence, formal input provenance, `temperature.dat`, `energy.dat`, and `amp_local_mode.out` when it is a declared handoff file.
- For electric-field / polarization targets, validate same-run field / polarization outputs before plotting, and record `Zeff.dat` / BEC provenance limitations when relevant.
- For any other declared target, report which files support the target and which acceptance criteria remain user-owned. Do not infer production acceptance from mere file presence.

BaTiO3 electric-hysteresis output validation additionally checks:
- completion evidence in log / stdout / stderr, preferably graceful PASP completion.
- `PASP.used_info` effective-setting evidence when available. If it is missing or sparse, combined evidence from formal `PASP.input`, `MD.input`, logs, and outputs may be used; contradictions block validation.
- Actual run evidence for `Model atomic_effective_H`, `atom_Heff.MD T`, electric-field controls, `atom_Heff.getP` / BEC path, and `local_mode.read_interaction` / `Read_init_spin` consistency with the formal input.
- `field.dat` exists, has a header exposing `step`, `time (ps)`, and electric-field component columns, and has monotonic sampled rows compatible with the run cadence.
- `P_abs.dat` exists, has a header exposing `step`, `time (ps)`, polarization component columns and magnitude, and has monotonic sampled rows compatible with the run cadence.
- `field.dat` and `P_abs.dat` are from the same run provenance. Do not pair a curated `output/field.dat` with a different `complete/P_abs.dat` or stale previous-run file.
- `field.dat` and `P_abs.dat` sampled rows align by `step` and `time (ps)` before plotting; matching filenames or row counts alone are insufficient.
- `energy.dat` and `temperature.dat` may be checked as optional diagnostics, but their presence does not replace `field.dat` / `P_abs.dat` for hysteresis validation.
- Hysteresis plotting is allowed only after same-run `field.dat` + `P_abs.dat` validation; plot selected `P_*` versus selected `E_*` components with user-confirmed component choice.
- Validation reports must label one-period / short demonstration loops as workflow and plotting evidence only, not convergence or production scientific acceptance.

output validation 不能反向授权 formal input、run derivation、submission preparation 或 unconfirmed parameter choices。

通过后记录：
- `OUTPUT_VALIDATION_PASS=true`
- 输出验证范围、证据路径、允许 handoff 的文件。

fail 或 blocked 时允许的唯一下一步：输出阻断原因和需要重跑 / 补证据 / 人工确认的项。

### S7：下游 handoff
只有 output validation pass 后，才能把 L5 输出交给绘图、后续 stage、后续 MD/MC、结构分析或其他 workflow。

Cr2O3 MVP handoff：
- Stage 1 -> Stage 2：validated stage 1 `amp_local_mode.out` copied/renamed as stage 2 `amp_local_mode.in`，并记录 upstream run id、source path、validation evidence、destination path。
- Stage 2 -> Stage 3：validated stage 2 `amp_local_mode.out` copied/renamed as stage 3 `amp_local_mode.in`，并记录 upstream run id、source path、validation evidence、destination path。
- Stage 3 -> analysis：validated `temperature.dat`、`energy.dat`、`amp_local_mode.out` and logs can be used for relaxation plots or scientific review.

BaTiO3 electric-hysteresis handoff:
- Single run -> analysis：validated same-run `field.dat` and `P_abs.dat` can be used for polarization-vs-field plotting.
- Record run id, formal input provenance, `Zeff.dat` provenance status, effective field settings evidence, component choice for plotting, and output-validation evidence.
- Do not create downstream stage `amp_local_mode.in` handoffs unless the user explicitly defines a separate follow-up dynamics workflow and it passes its own gates.

Generic / new-material handoff:
- Handoff target follows the user-confirmed branch: validated `amp_local_mode.out` for downstream dynamics, validated `temperature.dat` / `energy.dat` for thermal / relaxation review, validated same-run field / polarization outputs for electric-response plotting, or other user-defined outputs.
- Record current-material model provenance, formal input path, run id, command / ranks, output-validation evidence, and explicit downstream consumer.
- Do not claim production scientific acceptance, convergence, or parameter adequacy unless the user supplied acceptance thresholds and the output validation checked them.

handoff 说明必须记录 run id、formal input 来源、上游模型文件、命令 / ranks、validation 证据和下游应该消费的具体文件。

## Verifier Handoff Prompt Families

这些 prompt 只定义只读事实检查边界。主 agent 仍负责用户目标、最终判断、是否继续推进和用户沟通。

### L5 Cr2O3 input-preflight checker

```text
你是 read-only PASP input preflight checker。不要修改文件，不要创建 run，不要准备或提交任务，不要决定物理参数。
Mode: input-preflight
Workflow / stage: L5 Dynamics / Cr2O3 <stage 1 lattice heating | stage 2 spin heating | stage 3 coupled SLD relaxation>
Target package: <candidate path>
User confirmation record: <settings table or path>
Reference inventory: <reference files checked or gaps>

检查：
- PASP.input、MD.input、结构文件、local_mode_PM.dat、J_best.dat、amp_local_mode.in、所有 direct %include files 是否齐备。
- 每个显式 keyword、block、文件格式、编号规则和条件依赖是否有 skills/knowledge/reference/ 或用户权威来源覆盖。
- local_mode_PM.dat、J_best.dat、结构、mode definition、mass definition、Z_values / Spin_values 是否存在无说明混用。
- stage 与 SLD.mode 是否一致：stage 1 -> 1，stage 2 -> 2，stage 3 -> 3。
- smoke-test reduction 是否保持 SuperCell、amp_local_mode.in row count、planned MPI ranks 之间的一致性；unknown 或 incompatible ranks 是否在提交准备前 blocked。
- MD.Delta_t、atom_Heff.MD_time、LLG.method、LLG.damping、MD.damping、MD.temperature、MD.init_velocity_temp、MD.aft_step、MD.int_step、MD.output_amp_lm 是否与用户确认表一致。
- stage 2 / 3 amp_local_mode.in 是否有 upstream run id、source path、output-validation evidence 和 copy/rename 记录。
- README、脚本、目录名是否错误声称 candidate 已 submit-ready。

返回：Scope、Findings、Sources、Uncertain、Needs main-agent decision、Conclusion(pass/fail/blocked)。
```

### L5 Cr2O3 output-validation checker

```text
你是 read-only PASP output validation checker。不要修改文件，不要提交任务，不要决定物理参数。
Mode: output-validation
Workflow / stage: L5 Dynamics / Cr2O3 <stage>
Target run: <runs/run-id path>
Formal input provenance: <input README or path>
Expected branch and handoff target: <stage 2 amp_local_mode.in | stage 3 amp_local_mode.in | plotting / relaxation analysis>

检查：
- 日志是否有 PASP 正常结束证据，stderr / warning 是否影响 handoff。
- PASP.used_info 若存在，检查其 effective-setting evidence；若缺失、稀疏或不完整，记录为限制，不自动 pass / fail。
- 通过 MD.input、PASP.input、completion log evidence 和输出文件交叉确认实际 Model、atom_Heff.MD、SLD.mode、LLG.*、MD.*、local_mode.read_interaction、Read_init_spin 是否匹配 formal input；combined evidence 不足或互相矛盾时才 fail / blocked。
- temperature.dat 是否存在并包含 step/time/spin/latt temperature columns；sampled rows 是否 step/time monotonic；按 stage 检查 branch-consistent qualitative behavior。
- energy.dat 是否存在并可用于 energy time-series check；sampled rows 是否 step/time monotonic；stage 3 若是 NVE-like relaxation，标出能量漂移风险证据。
- 不要仅因为 sampled temperature.dat / energy.dat 没有包含 final MD step exact row 而判 fail；结合 completion evidence 和实际 sampled cadence 判断。
- amp_local_mode.out 是否存在，可否作为 downstream handoff；stage 1 / 2 handoff 需要 exact source path and run id。
- 输出是否来自同一个 run，未混用 sibling output、historical complete snapshot 或旧 run 残留。

返回：Scope、Findings、Sources、Uncertain、Needs main-agent decision、Conclusion(pass/fail/blocked)、Allowed handoff files。
```

### L5 BaTiO3 input-preflight checker

```text
你是 read-only PASP input preflight checker。不要修改文件，不要创建 run，不要准备或提交任务，不要决定物理参数。
Mode: input-preflight
Workflow / stage: L5 Dynamics / BaTiO3 electric hysteresis single-stage MD
Target package: <candidate path>
User confirmation record: <settings table or path>
Reference inventory: <reference files checked or gaps>

检查：
- PASP.input、MD.input、cell.str、unit_cell.str、local_mode_PM.dat、J_best.dat、amp_local_mode.in、所有 direct %include files 是否齐备且可解析。
- Branch 是否为 Model atomic_effective_H + atom_Heff.MD T + electric-field / polarization intent，而不是 Cr2O3 SLD stage sequence。
- 每个显式 keyword、block、文件格式、编号规则和条件依赖是否有 skills/knowledge/reference/ 或用户权威来源覆盖。
- atom_Heff.getP / active electric field / Zeff.dat 的一致性；Zeff.dat 是否与 current unit_cell.str、species order、mode basis provenance 对应。
- local_mode_PM.dat、J_best.dat、结构、mode definition、mass definition、Z_values、local_mode.read_interaction、Read_init_spin 是否有 same-basis evidence。
- SuperCell 与 amp_local_mode.in row count / current local-mode basis 是否一致；smoke-test reduction 是否同步处理。
- 对 periodic/cosine field，atom_Heff.MD_time 是否覆盖用户确认的周期数；MD.aft_step 是否小于 total MD steps 并留下可记录的 field/P_abs window；若是 production equilibration window，是否有用户明确确认。
- MD.E_type、MD.E_x/y/z、MD.E_omega、MD.E_phi、Field_for_Electrocaloric（若使用）、local_mode.MD_mode_range、MD.Delta_t、atom_Heff.MD_time、damping、temperature、output cadence 是否与用户确认表一致；reference gap 是否阻断正式写入。
- planned MPI ranks / scheduler helper 是否只是环境事实，且提交准备前没有 unknown 或 incompatible rank issue。
- candidate 中没有 stale output、historical complete residue、old PASP.used_info、old field.dat、old P_abs.dat、old logs；README 未把 candidate 或 MD-1 values 写成 submit-ready/default。

返回：Scope、Findings、Sources、Uncertain、Needs main-agent decision、Conclusion(pass/fail/blocked)。
```

### L5 generic/new-material input-preflight checker

```text
你是 read-only PASP input preflight checker。不要修改文件，不要创建 run，不要准备或提交任务，不要决定物理参数。
Mode: input-preflight
Workflow / stage: L5 Dynamics / generic new-material <MD | LLG/ASD | SLD | electric-field response | smoke test | production | handoff>
Target package: <candidate path>
User confirmation record: <settings table or path>
Reference inventory: <reference files checked or gaps>

检查：
- PASP.input、MD.input when used、structure files or documented equivalent route、local_mode_PM.dat、J_best.dat、amp_local_mode.in when current settings read an initial state、所有 direct %include files 是否齐备且可解析。
- Branch 是否为 user-confirmed generic/new-material atomic_effective_H dynamics path，并且 active degrees of freedom、expected outputs、smoke-test/production label 与确认表一致。
- 每个显式 keyword、block、文件格式、编号规则和条件依赖是否有 skills/knowledge/reference/ 或用户权威来源覆盖。
- 如果 upstream 是 L3，candidate README / PROGRESS 是否引用当前材料的 L3 output-validation / handoff record；该 record 是否覆盖 local_mode_PM.dat、拟交给 L5 的 J_best.dat 或等价 fitted-parameter selection、structure route、mode / mass definition、species / spin values、fitting provenance 和 known gaps。
- local_mode_PM.dat、J_best.dat、structure route、SuperCell、species / spin values、mode definition、mass definition、local_mode.read_interaction、Read_init_spin、amp_local_mode.in when current settings read an initial state 是否有 same-material / same-basis provenance。
- Zeff.dat、elastic.dat、spin_strain.dat、Field_for_Electrocaloric、local_mode.MD_mode_range 或其他 conditional inputs / dependencies 是否只在 current settings/reference/user authority 建立依赖时列为必需。
- 如果 current settings read an initial state，SuperCell 与 amp_local_mode.in row count / current local-mode basis 是否一致；smoke-test reduction 是否同步处理并保持 planned MPI ranks compatible。
- MD.Delta_t、atom_Heff.MD_time、SLD.mode when active、LLG.method、LLG.damping、MD.damping、MD.temperature、MD.init_velocity_temp、MD.aft_step、MD.int_step、MD.output_amp_lm 和 branch-specific controls 是否与用户确认表一致；reference gap 是否阻断正式写入。
- candidate 中没有 stale output、historical complete residue、old PASP.used_info、old *_used.dat、old temperature.dat、old energy.dat、old field.dat、old P_abs.dat、old logs。
- README、脚本、目录名是否错误声称 candidate 已 submit-ready，或把 Cr2O3 / BaTiO3 historical values 写成 current-material defaults。

返回：Scope、Findings、Sources、Uncertain、Needs main-agent decision、Conclusion(pass/fail/blocked)。
```

### L5 BaTiO3 output-validation checker

```text
你是 read-only PASP output validation checker。不要修改文件，不要提交任务，不要决定物理参数。
Mode: output-validation
Workflow / stage: L5 Dynamics / BaTiO3 electric hysteresis single-stage MD
Target run: <runs/run-id path>
Formal input provenance: <input README or path>
Expected analysis target: field.dat + P_abs.dat hysteresis plotting

检查：
- 日志是否有 PASP 正常结束证据，stderr / warning 是否影响分析。
- PASP.used_info 若存在，检查 effective Model、atom_Heff.MD、electric-field controls、atom_Heff.getP、local-mode/model settings；若缺失或稀疏，记录限制并用 MD.input、PASP.input、log 和输出文件做 combined evidence。
- field.dat 是否存在，header 是否包含 step/time/electric-field components，数据行 step/time 是否单调且 cadence 合理。
- P_abs.dat 是否存在，header 是否包含 step/time/polarization components/P_abs，数据行 step/time 是否单调且 cadence 合理。
- field.dat 和 P_abs.dat 是否来自同一个 run provenance，且 sampled rows 是否按 step/time 对齐；不得混用 sibling output、historical output subset、complete snapshot 或旧 run 残留。
- energy.dat、temperature.dat 可作为 diagnostics 检查，但不能替代 field/P_abs validation。
- 只有 validation pass 后才允许 P vs E plotting；component choice 交给 main agent / user确认。
- 若是 one-period / short demonstration loop，结论必须说明它只验证 workflow/plotting mechanics，不代表 production convergence 或 scientific acceptance。

返回：Scope、Findings、Sources、Uncertain、Needs main-agent decision、Conclusion(pass/fail/blocked)、Allowed analysis files。
```
