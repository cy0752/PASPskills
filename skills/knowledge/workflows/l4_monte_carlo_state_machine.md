# L4 Monte Carlo State Machine

本文件是 L4 Monte Carlo workflow 的运行门禁。runtime agent 必须先执行这里的状态机；`l4_monte_carlo.md` 只补充当前状态所需的输入、输出、可调项和检查细节，不能覆盖本文件的 STOP 条件。

## 核心原则
- L4 默认指 `Model atomic_effective_H` 的 MC / PTMC / CG / lowest-state workflow；`Model Spin_lattice_interaction` 应转到 L2 spin-lattice workflow。
- `继续`、`ok`、`按计划执行`、`去提交` 不等于确认温度网格、步数、超胞、初始态、strain / CG、输出覆盖或提交授权。
- `可以使用 subagent` 只表示允许委派只读事实检查，不等于确认 L4 科学设置，不等于允许提交，不等于允许 agent 代填物理参数。
- subagent 只能做只读事实检查；不能改文件、不能创建 run、不能准备提交、不能提交任务、不能决定科学参数。
- read-only subagent 任务统一使用 `skills/subskills/pasp-verifier/skill.md` 的契约；本文件只指定 L4 阶段门禁和 checklist。
- inventory 不是 preflight。目录盘点、模板对比、日志摘要、输出清点都不能替代输入文件 preflight。
- input preflight 不是 output validation。运行后若要把结果交给下游，必须单独做 output validation。
- `notes/`、`drafts/`、`*.draft` 是草稿区；candidate 目录是待 preflight 候选区；`input/` 是正式输入基线；`runs/<run-id>/` 是实际运行目录。这四类不能混用。
- 从 example、旧 `input/` 或历史 run 派生 smoke-test 时，candidate 可以用于整理和缩小参数，但真正的 `runs/<run-id>/` 必须是干净运行目录。不要把旧 `PASP.used_info`、`log.out`、`T.dat`、`*_used.dat`、`T_*`、`final_*`、`lowest_ene.*`、`*_PTMC*` 等输出残留复制进新 run。

## README / PROGRESS 契约
创建、提升、派生或完成 L4 关键目录时，应同步写入或更新 README / PROGRESS。最低字段：
- `Status`：当前阶段，是否 draft / candidate / formal input / run / output-validated / handoff-ready。
- `File Roles`：`PASP.input`、`MC.input`、结构文件、上游模型文件、提交 helper、输出文件分别是什么。
- `Upstream` / `Downstream`：`local_mode_PM.dat`、`J_best.dat`、初始态文件、统计输出或 lowest-state handoff 的来源和去向。
- `Gate Evidence`：用户确认记录、reference inventory、read-only subagent preflight / output validation 结论和证据路径。
- `Blocked / TODO`：缺哪些确认、哪些文件不可提交、哪些输出不可 handoff、下一步允许做什么。

没有这些记录时，不得把目录描述为 submit-ready、formal input、validated output 或 handoff-ready。

## 状态机

### S0：目标目录与 workflow 定位
允许自动执行：
- 盘点用户给定目标目录自己的文件、阶段目录、输入、输出、日志和提交 helper。
- 暂定判断是 L4 `atomic_effective_H` MC/PTMC、CG / lowest-state、已有输出验证，还是 L2 `Spin_lattice_interaction`。
- 记录当前事实和不确定项；不能用 sibling examples 或旧 run 覆盖目标目录事实。

L4 判据：
- `PASP.input` 或 `MC.input` 指向 `Model atomic_effective_H`，并依赖 `local_mode_PM.dat`、`J_best.dat`、`local_mode.read_interaction T`、local-mode / spin-mode definition、`amp_local_mode.in` 等文件或设置。
- 若目标是 `spin_exchange.dat` + `Model Spin_lattice_interaction` 的 PTMC / CG / magnon handoff，应转到 L2 workflow。

禁止：
- 写正式 `PASP.input` / `MC.input`。
- 创建或覆盖正式 `input/`。
- 创建 `runs/<run-id>/`、提交脚本或外部任务配置。

### S1：上游模型与候选材料整理
允许自动执行：
- 清点候选输入包是否包含 `PASP.input`、`MC.input`、`cell.str`、`unit_cell.str` 或等价结构文件、`local_mode_PM.dat`、`J_best.dat`、直接 `%include` 的 split files。
- 标出可选但受条件约束的文件：`amp_local_mode.in`、谨慎处理的 `amp_local_mode.in_unitcell`、`Zeff.dat`、`seed.in`、提交 helper。
- 生成缺失项、来源疑问、reference inventory 草表。
- 在 `notes/`、`drafts/` 或 candidate 目录保存明确标注“不可提交 / 待 preflight”的候选材料。

必须确认或记录的上游事实：
- `local_mode_PM.dat` 和 `J_best.dat` 是否来自同一材料、同一 shared basis / interaction basis、同一结构和同一模式定义。
- 当前 `PASP.input` 是否只是消费已拟合模型做 MC / PTMC / CG，而不是重新拟合 effective Hamiltonian。
- 任何来自 Lecture-4 examples、旧 run 或 sibling directory 的数值都只是参考，不能成为当前正式设置。

禁止：
- 把候选材料放进正式 `input/` 并称为可提交。
- 生成提交准备或外部任务配置。

### S2：候选输入包
允许生成或整理 candidate 包，但必须清楚标注 candidate / 待 preflight。

候选包至少应覆盖：
- `PASP.input`：模型、结构 include、`MC.input` include、supercell / species / mode / interaction-reuse 控制。
- `MC.input`：MC / PTMC / CG、初始态、温度网格、步数、strain / relax、输出覆盖设置。
- 结构和上游模型文件：`cell.str`、`unit_cell.str` 或等价结构输入，`local_mode_PM.dat`、`J_best.dat`。
- 条件文件：`amp_local_mode.in` 或明确支持的 unit-cell 初态文件、`Zeff.dat`、`seed.in`、split include files。
- README：说明文件角色、上游来源、待确认设置、reference inventory 状态、为什么当前还不能提交。

禁止：
- 提升为正式 `input/`。
- 派生 `runs/<run-id>/`。
- 创建或编辑提交脚本作为 submit-ready artifact。

### S3：L4 模型与采样设置确认（STOP REQUIRED）
进入 formal input、run derivation 或 submission preparation 前，必须有用户确认或用户明确接受一份逐项设置表。

必须确认：
- workflow branch：普通 MC、PTMC 统计、CG / lowest-state search、已有输出验证、或下游 handoff。
- 上游模型来源：`local_mode_PM.dat`、`J_best.dat`、结构、模式定义、拟合数据链是否来自同一模型基底。
- `SuperCell` / 系统尺寸与目标物理周期、内存和时间预算是否合适。
- 初始态策略：是否读取初始态；若读取，`atomic_effective_H` 默认查 `amp_local_mode.in`，unit-cell variant 按 `MC.init_spin_unitcell` reference 检查，并确认 `amp_local_mode.in_unitcell` 来源和格式。
- MC / PTMC 设置意图：温度区间、`PT.M`、planned MPI ranks、温度网格、步数、热化和统计长度、smoke-test 还是 production。
- strain / local-mode / spin-mode 约束和 CG / relax 目标。
- 输出覆盖：是否需要能量 / 比热、极化、磁化、晶格参数、位移、lowest-state handoff。
- 运行环境信息：计划命令、MPI ranks、scheduler / image / executable、stdout / stderr 路径。
- 若使用 `mpirun` / `mpiexec` 启动，记录 `-np` 来源；在 scheduler 脚本中通常来自 `SLURM_NTASKS` 或等价任务数。

确认后记录：
- `USER_CONFIRMED_L4_MC_SETTINGS=true`
- 设置表、来源、仍需 reference 或 preflight 检查的项。

未满足时允许的唯一下一步：列出缺失确认项或继续写 draft / candidate notes；不得提升正式 input、派生 run、准备提交或提交。

### S4：Input Preflight（STOP ON FAIL）
候选输入包提升为正式 `input/`、覆盖 input、派生 `runs/<run-id>/`、创建或编辑提交 artifacts、准备外部任务配置、提交任务前，必须先做 read-only subagent input preflight。

执行方式：
- 使用 `skills/subskills/pasp-verifier/skill.md`，`mode: input-preflight`。
- preflight 必须点名 workflow、target stage、候选输入文件 / 目录、stage-specific checklist、用户确认记录、reference inventory。
- 对 PASP 输入文件，preflight 必须检查每个显式 keyword、block、`%include`、依赖文件格式和编号规则是否有 `skills/knowledge/reference/` 或用户权威来源覆盖。
- 主 agent 本地检查、目录盘点、模板对比、日志检查不能替代这一步。
- 若 read-only subagent 无法执行，L4 formal input / run / submission preparation 必须 blocked；`NO_SUBAGENT_PREFLIGHT_AVAILABLE=true` 不足以继续。

L4 preflight checklist 至少包括：
- 文件齐备：`PASP.input`、`MC.input`、结构文件、`local_mode_PM.dat`、`J_best.dat`、所有 direct include files。
- 上游一致性：模型基底、结构、模式定义、参数编号、`Z_values` / `Spin_values`、SOC / cutoff / powers 等未被无说明地混用。
- `PT.M` 与 planned MPI ranks 的整数倍关系；若 submission ranks 未知，结论至少应标为 blocked 或需要提交前复查。
- 若候选提交 helper 使用 `mpirun -np $SLURM_NTASKS` 或等价命令，preflight 必须把 scheduler task count 当作 planned MPI ranks 来检查。
- `nbeg_blk`、`nblk`、`PT.nblk_T`、`PT.niter` 是否留下统计采样空间；smoke-test 设置不得被描述成 production。
- `Read_init_spin T` 时，模型对应的初态文件存在且来源清楚。
- `atom_Heff.getP T` 时，`Zeff.dat` 存在且与结构基底对应。
- `local_mode.MC_mode_range`、`local_mode.mode_definition` 或 split include 的行数 / mode 数有 reference-backed 检查。
- CG / relax 开启时，relax flag、`opt.*`、输出验证计划和 wall-time 风险已经确认。
- README / 脚本 / 目录名没有把 candidate 写成 submit-ready。

通过后记录：
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`
- pass / fail / blocked 结论、证据路径、仍不可做的动作。

fail 或 blocked 时允许的唯一下一步：输出阻断原因、证据路径和需要修正 / 确认的项。

### S5：正式 input / run / 提交准备
只有全部前置 flag 存在，才允许进入 S5：
- `USER_CONFIRMED_L4_MC_SETTINGS=true`
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`

S5 才允许：
- 提升或覆盖正式 `input/`。
- 从正式 `input/` 派生 `runs/<run-id>/`。
- 在 run 目录内接入上游产物、提交 helper、实际运行命令。
- 准备外部任务配置。

进入 S5 必须同步记录：
- formal `input/README.md`：来源 candidate、preflight 证据、关键确认 flag、字段/reference inventory。
- `runs/<run-id>/README.md`：派生自哪个 input、接入哪些上游产物、计划命令 / MPI ranks / scheduler / executable / image、stdout / stderr、预期输出。

派生 `runs/<run-id>/` 时：
- 只复制当前运行需要的科学输入、direct `%include` 文件、条件输入文件和提交 helper。
- 不复制旧输出、旧日志、旧 `PASP.used_info`、旧 `*_used.dat` 或历史统计文件；这些只能作为 provenance / comparison 证据记录在 README 中。
- 如果为了快速完善 workflow 创建小超胞 / 短步数 run，必须在 README 和最终答复中明确标为 `smoke-test`，不能描述成 production 统计结果。

即使 S5 前置 flag 齐全，真正提交外部任务前仍必须得到用户明确提交授权。`继续`、`ok`、`可以使用 subagent` 都不是提交授权。

### S6：Output Validation（STOP ON FAIL）
运行完成后、绘图或下游 handoff 前，必须做 output validation。优先委派给 `pasp-verifier` `mode: output-validation`。

检查至少包括：
- 日志正常结束证据，如 `PASP is finished gracefully.`；PTMC 还要检查 `End of PTMC` 或等价 stage marker。
- `PASP.used_info` 中实际生效的 `Model`、`MC`、`Parallel_Tempering`、PT 设置、`local_mode.read_interaction`、relax flags、`atom_Heff.getP`、`atom_Heff.cal_mag` 是否与 formal input 匹配。
- 统计输出是否符合目标：`E_PTMC_K.dat`、`C_PTMC_K.dat`、`M_PTMC_K.dat`、`P_abs.dat`、`abc_cell_str_K.dat`、`strain_K.dat`、`u_*_K.dat` 等只按已启用分支期待。
- sample count / 统计质量证据：`nsample_PTMC.dat`、`Eachstatstep_T*.dat`、`C_PTMC*.dat` / `X_PTMC*.dat` 内的 bin-size 警告。
- final-state 文件与 lowest-state 文件不要混淆：`T_*_final*`、`final_amp_ptmc.*`、`final_ene.*` 是 final-state 家族；`lowest_ene.*` 才是 lowest-state 家族。
- CG / relax 成功必须同时有日志证据（如 `CG finish`）和对应输出；不能只凭文件存在声称 relaxed。

output validation 不能反向授权 formal input、run derivation 或提交准备。

通过后记录：
- `OUTPUT_VALIDATION_PASS=true`
- 输出验证范围、证据路径、允许 handoff 的文件。

fail 或 blocked 时允许的唯一下一步：输出阻断原因和需要重跑 / 人工确认的项。

### S7：下游 handoff
只有 output validation pass 后，才能把 L4 输出交给绘图、后续 MC/MD、结构分析或其他 workflow。

常见 handoff：
- 统计曲线：`E_PTMC_K.dat`、`C_PTMC_K.dat`、`M_PTMC_K.dat`、`P_abs.dat`、`abc_cell_str_K.dat`、`strain_K.dat`、`u_*_K.dat`。
- atomic effective-Hamiltonian lowest-state：`lowest_ene.amp_local_mode`、`lowest_ene.str_mode_amp`、`lowest_ene.pos`、`lowest_ene.ene`、`lowest_ene.ene_symbol`、`lowest_ene.convergence`。
- 每温度末态：`T_*_final_.amp`、`final_amp_ptmc.*`、相关 XSF 文件；只能描述为末态，不能自动描述为全局最低态。

handoff 说明必须记录 run id、formal input 来源、上游模型文件、命令 / ranks、validation 证据和下游应该消费的具体文件。

## Verifier Handoff Prompt Families

这些 prompt 只定义只读事实检查边界。主 agent 仍负责用户目标、最终判断、是否继续推进和用户沟通。

### L4 input-preflight checker

```text
你是 read-only PASP input preflight checker。不要修改文件，不要创建 run，不要准备或提交任务，不要决定物理参数。
Mode: input-preflight
Workflow / stage: L4 Monte Carlo / <candidate stage>
Target package: <candidate path>
User confirmation record: <settings table or path>
Reference inventory: <reference files checked or gaps>

检查：
- PASP.input、MC.input、结构文件、local_mode_PM.dat、J_best.dat、所有 direct %include 和条件输入是否齐备。
- 每个显式 keyword、block、文件格式、编号规则和条件依赖是否有 skills/knowledge/reference/ 或用户权威来源覆盖。
- local_mode_PM.dat、J_best.dat、结构、mode definition、Z_values / Spin_values、SOC / cutoff / powers 是否存在无说明混用。
- PT.M 与 planned MPI ranks / scheduler task count 是否匹配；unknown ranks 必须 blocked 或提交前复查。
- nblk、nbeg_blk、PT.nblk_T、PT.niter 是否符合用户确认的 smoke-test / production 意图。
- Read_init_spin、MC.init_spin_unitcell、atom_Heff.getP、atom_Heff.cal_mag、CG / relax 开关是否有对应文件和验证计划。
- README、脚本、目录名是否错误声称 candidate 已 submit-ready。

返回：Scope、Findings、Sources、Uncertain、Needs main-agent decision、Conclusion(pass/fail/blocked)。
```

### L4 output-validation checker

```text
你是 read-only PASP output validation checker。不要修改文件，不要提交任务，不要决定物理参数。
Mode: output-validation
Workflow / stage: L4 Monte Carlo / output validation
Target run: <runs/run-id path>
Formal input provenance: <input README or path>
Expected branch and handoff target: <PTMC / CG / lowest-state / plotting / other>

检查：
- 日志是否有 PASP 正常结束证据；PTMC 是否有 End of PTMC 或等价 marker；CG / relax 是否有收敛证据。
- PASP.used_info 中实际 Model、MC、Parallel_Tempering、PT、local_mode.read_interaction、relax flags、atom_Heff.getP、atom_Heff.cal_mag 是否匹配 formal input。
- 只按启用分支检查统计、极化、磁化、晶格、strain、local-mode、final-state、lowest-state 输出。
- sample count、Eachstatstep、C_PTMC* / X_PTMC* bin-size 或 block 警告是否影响 handoff。
- final-state 与 lowest-state 文件是否被混淆；当前 run 证据是否足够支持 handoff。

返回：Scope、Findings、Sources、Uncertain、Needs main-agent decision、Conclusion(pass/fail/blocked)、Allowed handoff files。
```
