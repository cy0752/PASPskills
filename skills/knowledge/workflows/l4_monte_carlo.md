# Workflow: L4 Monte Carlo / PTMC / CG

> 本 workflow 面向 `Model atomic_effective_H` 的 MC / PTMC / CG / lowest-state 运行。正式写 input、派生 run、准备提交或提交前，必须先读 sibling `l4_monte_carlo_state_machine.md` 并执行其 STOP gate。

## 目标
使用已经建立并拟合好的 effective Hamiltonian 进行 Monte Carlo、parallel tempering Monte Carlo 或局域优化，得到温度相关统计曲线、末态构型、lowest-state 构型或后续 workflow 的 handoff 文件。

## 适用问题
- 我已经有 `local_mode_PM.dat` 和 `J_best.dat`，想做 `atomic_effective_H` 的 PTMC。
- 我想扫描温度区间，分析能量 / 比热 / 极化 / 磁化 / 晶格参数随温度变化。
- 我想读取已有 local-mode 初态，继续做 MC 或 lowest-state 搜索。
- 我想确认一个 L4 run 的输出能不能拿去画图或作为下游初态。
- 我想在 MC 后做 CG / relax，并判断 relaxed output 是否可信。

本文档不解决：
- effective Hamiltonian 的 shared-basis 构建、样本生成、DFT 数据整理或拟合；这些属于 L3。
- `spin_exchange.dat` + `Model Spin_lattice_interaction` 的磁基态 / magnon handoff；这些属于 L2。
- 单个字段的默认值、单位、格式、编号规则；这些属于 `skills/knowledge/reference/`。

## 来源边界
本 workflow 是基于 Lecture-4、L3/L2 workflow、reference cards、examples 和源码审计整理出的稳定运行契约。运行时只依赖：
- `skills/knowledge/workflows/`
- `skills/knowledge/reference/`
- `skills/subskills/pasp-verifier/skill.md`

Lecture examples、旧 run 和源码路径只能作为 authoring 证据；不得把其中的 `SuperCell`、`PT.M`、温度、步数、cutoff、`Spin_values`、`Z_values` 或输出文件全集当成当前用户任务的默认值。

历史 example 观察、输出家族和待补 reference gaps 见：
- `./l4_monte_carlo_run_notes.md`

运行时解释当前 workflow 时，应优先使用本文件中的稳定契约；不要把 run-notes 中的历史实例值直接当成用户当前 workspace 的实时结果。

## 运行状态机（优先级最高）
运行时先读：
- `./l4_monte_carlo_state_machine.md`

本长文档只补充当前状态所需细节。任何后文步骤、表格、输出清单都不能绕过这些 STOP 条件：
- S3：`USER_CONFIRMED_L4_MC_SETTINGS=true`
- S4：`READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- S4：`STAGE_PREFLIGHT_PASS=true`
- S6：output validation pass before handoff

## 输入包与运行目录契约
- `input/`：干净、已 preflight 的正式输入基线。`PASP.input` 直接 `%include` 或运行时读取的文件必须在此齐全，或在 README 中明确标注为由上游接入。
- `candidate/`、`notes/`、`drafts/`：待确认 / 待 preflight 的候选材料。不能描述为 submit-ready。
- `runs/<run-id>/`：实际运行目录。每次运行从正式 `input/` 完整复制，再接入上游产物和提交 helper，只在 run 目录中运行。

不要在 baseline `input/` 里直接跑 PASP。L4 会写出大量 `T_*`、`final_*`、`lowest_ene.*`、`*_PTMC*`、`PASP.used_info`、`seed_used.in` 等输出，容易污染输入基线。

派生 run 目录时要避免把历史输出残留带入新 run。若 `input/` 或 candidate 是从旧 example / complete / previous run 复制来的，先清点文件角色；新 run 只复制当前需要的 `PASP.input`、`MC.input`、direct `%include` 文件、`local_mode_PM.dat`、`J_best.dat`、条件输入文件和运行 helper。旧 `PASP.used_info`、`log.out`、`T.dat`、`*_used.dat`、`T_*`、`final_*`、`lowest_ene.*`、`*_PTMC*` 等文件不得进入新 run。

## Preflight 硬门禁
候选输入包在提升为正式 `input/`、覆盖正式 input、派生 `runs/<run-id>/`、创建或编辑提交 artifacts、准备外部任务配置或提交任务前，必须使用 `skills/subskills/pasp-verifier/skill.md`：

```text
mode: input-preflight
Workflow / stage: L4 Monte Carlo / <current stage>
```

preflight 是 read-only subagent 任务。主 agent 本地检查、目录盘点、模板对比、日志摘要和 output validation 都不能替代它。通过后才可记录：
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`

在此之前只能写 draft / candidate notes，不能生成 submit-ready 输入或提交准备。真正提交外部任务前还需要用户明确提交授权。

## Stage 1：候选输入包准备

### 当前阶段输入文件

| 来源 | 文件 | 是否硬性必需 | 说明 |
|---|---|---|---|
| 用户 / 上游 | `PASP.input` | 必需 | 选择 `Model atomic_effective_H`，包含结构、模式、相互作用读取、`%include MC.input` 或等价设置 |
| 用户 / 上游 | `MC.input` | 必需 | 控制 MC / PTMC / CG、温度、副本数、步数、初始态、strain / relax、输出覆盖 |
| 用户 / 上游 | `cell.str` | 通常必需 | 当前模拟基底结构；具体路线按 `PASP.input` reference 判断 |
| 用户 / 上游 | `unit_cell.str` | 通常必需 | 原胞 / reference cell；若不使用也要在 README 中说明结构路线 |
| L3 / 上游模型 | `local_mode_PM.dat` | `atomic_effective_H` 通常必需 | interaction basis / local-mode basis；应与当前 `J_best.dat` 同源 |
| L3 / 上游拟合 | `J_best.dat` | `atomic_effective_H` 通常必需 | fitted interaction parameter values；编号必须匹配 `local_mode_PM.dat` 或对应 interaction list |
| 用户 / 上游 | direct include files | 条件必需 | 例如 split 出来的 `mode_def.input`；凡是 `%include` 的文件都要进入候选包 |
| 用户 / 上游 | `amp_local_mode.in` | 条件必需 | `Read_init_spin T` 且 `atomic_effective_H` 读取初态时使用 |
| 用户 / 上游 | `amp_local_mode.in_unitcell` | 谨慎条件项 | `MC.init_spin_unitcell T` 时读取；需按 source-audited reference 检查，并确认文件来源和格式 |
| 用户 / 上游 | `Zeff.dat` | 条件必需 | 需要极化输出时检查，尤其 `atom_Heff.getP T` |
| 用户 | `seed.in` | 可选 | 固定随机种子；运行后记录 `seed_used.in` |
| 环境 | `run.sh` / scheduler helper | 提交时需要 | 环境 helper，不是科学输入；submit-ready 前仍需 preflight 和提交授权 |

### 上游依赖
- L3 或等价流程产出的 same-basis `local_mode_PM.dat`。
- 拟合得到并与 interaction 编号匹配的 `J_best.dat`。
- 用户确认的模型目标、超胞、温度区间、PT 副本数、步数、初始态策略、strain / CG 和输出需求。

### 当前阶段已知输出
- 一个明确标注 candidate / draft 的 L4 输入包。
- README / PROGRESS 记录文件角色、上游来源、缺失项、reference inventory、不得提交的原因和下一 gate。

### 待运行验证的依赖
- `PASP.used_info` 中实际解析的 include、默认值和生效开关只能在运行后确认。
- `local_mode_PM_used.dat`、`seed_used.in`、`T_*`、`final_*`、`lowest_ene.*`、`*_PTMC*` 等实际输出集合取决于模型、开关、PASP 版本和运行是否完成。
- scheduler stdout / stderr 文件名、`mpirun` 实际 `-np`、module / image / executable 路径是环境事实；候选包阶段只能记录预期，不能声称已经验证。

### 下游去向
- 通过 S3 用户确认和 S4 input preflight 后，candidate 包才能提升为 formal `input/`。
- formal `input/` 后续被完整复制到 `runs/<run-id>/`，再接入提交 helper 和运行环境信息。
- 如果 preflight fail / blocked，本阶段输出只能作为 draft / candidate notes，不得交给提交或绘图。

### 本阶段使用的脚本 / helpers
- `run.sh`、`sub_pasp`、scheduler 脚本只作为环境 helper；候选阶段可记录需求和草稿，但不得标为 submit-ready。
- 若 helper 中的 `mpirun -np` 来自 `SLURM_NTASKS` 或等价变量，S4 preflight 必须把该任务数纳入 `PT.M` 整除检查。
- 任何 helper 改动如果影响 PASP 读取的 input file、include file 或运行工作目录，必须回到 reference-before-write 和 input-preflight gate。

### 当前阶段可调整项

这些是 workflow 层可以帮助定位的调整类别；具体写法、默认值、单位、block 行数和条件依赖仍必须查 reference：

| 类别 | 常见对象 | 调整前必须确认 |
|---|---|---|
| workflow branch | 普通 MC、PTMC、CG / lowest-state、output-validation-only、handoff-only | 用户目标和当前目录是否已经有可验证输出 |
| 上游模型消费 | `local_mode.read_interaction`、`local_mode_PM.dat`、`J_best.dat` | 文件是否来自同一 L3 / 上游模型基底 |
| 结构与体系规模 | `SuperCell`、结构 include、`Z_values`、`Spin_values` | 目标物理周期、内存 / wall time、结构路线 |
| 温度与采样 | `MC`、`Parallel_Tempering`、`Temperature`、`PT.*`、`nblk`、`nbeg_blk` | smoke test 还是 production，planned MPI ranks |
| 初始态 | `Read_init_spin`、`MC.init_spin_unitcell`、`amp_local_mode.in` | 初态文件来源、模型分支、文件格式证据 |
| 自由度 / relax | strain flags、`local_mode.MC_mode_range`、`atom_Heff.relax_str`、`opt.*` | 允许哪些自由度变化，是否要 CG / lowest-state handoff |
| 输出覆盖 | `atom_Heff.getP`、`atom_Heff.cal_mag`、统计输出 cadence | 下游需要能量、比热、极化、磁化、晶格还是位移数据 |
| 运行环境 | `mpirun` / `mpiexec`、MPI ranks、scheduler helper、stdout / stderr | preflight 通过后的实际运行命令和提交授权 |

### 这些项控制什么

- workflow branch 决定后续是采样统计、局域优化 / lowest-state 搜索、已有 run 验证，还是只做 handoff。
- 上游模型消费决定当前 L4 是否只读取 fitted interaction，而不是重新进入 L3 拟合。
- 结构与体系规模影响物理周期、自由度数量、内存、进程数和输出体量。
- 温度与采样设置控制温度网格、parallel tempering 副本、热化 / 统计长度和 smoke-test 风险。
- 初始态设置决定是否从已有 local-mode amplitude 或 unit-cell 初态复制进入超胞。
- 自由度 / relax 设置决定 local-mode、strain、spin-mode 或 CG 路径是否参与更新。
- 输出覆盖设置决定运行后哪些 observable family 可用于 validation 和 handoff。
- 运行环境设置只控制如何运行已 preflight 的 formal input；它不能替代 input preflight 或提交授权。

### 什么时候不要直接改、先查 reference

- 写入或修改任何 `PASP.input` / `MC.input` keyword、block、`%include`、文件格式、编号规则或条件依赖前。
- 改 `PT.M`、温度网格、block / iteration / measurement 设置，并且需要判断与 MPI ranks 或统计质量的关系时。
- 启用 `Read_init_spin T`、`MC.init_spin_unitcell T`、`atom_Heff.getP T`、`atom_Heff.cal_mag`、`atom_Heff.relax_str` 或 `local_mode.MC_mode_range` 时。
- 判断 `cell.str`、`unit_cell.str`、`local_mode_PM.dat`、`J_best.dat`、`amp_local_mode.in`、`Zeff.dat`、`seed.in` 是否硬必需或条件必需时。
- reference 没有覆盖的写法只能保留为 draft / candidate，并记录 blocked 或需要用户权威来源。

### 修改后要检查什么
- `PASP.input` 的所有 `%include` 在候选包中存在，或 README 明确说明运行时由上游接入。
- `local_mode_PM.dat` 与 `J_best.dat` 的来源、结构、mode definition、编号体系没有混用。
- `MC.input` 中 MC / PTMC / CG / MD 开关不互相冲突；`MC` 与 `MD` 不能同时开启。
- `PT.M` 能在 submission 前和 planned MPI ranks 对齐。
- `Read_init_spin T` 时，初态文件与模型分支一致。
- 候选目录名、README、脚本注释没有把未 preflight 的包描述成可提交。

## Reference-before-write

准备写入或修改任何 PASP 字段、block、文件格式、编号规则时，必须先读对应 reference。常见入口：

| 对象 | Reference |
|---|---|
| `PASP.input` include、结构、`SuperCell`、`Z_values`、`Spin_values`、外场 | `skills/knowledge/reference/topics/PASP.input.md` |
| MC / PTMC / CG 总览 | `skills/knowledge/reference/topics/MC.input.md` |
| `local_mode_PM.dat` | `skills/knowledge/reference/files/local_mode_PM.dat.md` |
| `J_best.dat` | `skills/knowledge/reference/files/J_best.dat.md` |
| `amp_local_mode.in` | `skills/knowledge/reference/files/amp_local_mode.in.md` |
| `Zeff.dat` | `skills/knowledge/reference/files/Zeff.dat.md` |
| `seed.in` | `skills/knowledge/reference/files/seed.in.md` |
| `PT.M`、`PT.low_temp`、`PT.high_temp`、`PT.Tmesh`、`PT.nblk_T`、`PT.niter` | `skills/knowledge/reference/params/` |
| `nblk`、`nbeg_blk` | `skills/knowledge/reference/params/` |
| `MC`、`Parallel_Tempering`、`Temperature`、`global.heat_bath` | `skills/knowledge/reference/params/` |
| `Read_init_spin` | `skills/knowledge/reference/params/Read_init_spin.md` |
| `MC.init_spin_unitcell` | `skills/knowledge/reference/params/MC.init_spin_unitcell.md` |
| `local_mode.read_interaction` | `skills/knowledge/reference/params/local_mode.read_interaction.md` |
| `local_mode.mode_definition` | `skills/knowledge/reference/params/local_mode.mode_definition.md` |
| `local_mode.MC_mode_range` | `skills/knowledge/reference/params/local_mode.MC_mode_range.md` |
| `atom_Heff.getP` | `skills/knowledge/reference/params/atom_Heff.getP.md` |
| `atom_Heff.cal_mag` | `skills/knowledge/reference/params/atom_Heff.cal_mag.md` |
| `atom_Heff.homogeneous_strain`、`atom_Heff.inhomogeneous_strain`、`atom_Heff.relax_str` | `skills/knowledge/reference/params/` |
| `atom_Heff.auto_adjust_try_amp`、`atom_Heff.try_amp.change_rate` | `skills/knowledge/reference/params/` |
| CG / relax controls such as `opt.NSW`、`opt.EDIFFG` | `skills/knowledge/reference/params/` |

如果 reference 没覆盖某个写法，最多写 draft / candidate，并标注需要用户权威来源或 read-only verifier blocked 结论；不得进入 formal input 或 submission preparation。

## 任务目标 -> 推荐调整方向

| 目标 | 优先考虑 | 不要先做 |
|---|---|---|
| 打通流程 / smoke test | 使用用户确认的较小步数与明确 smoke-test README；先验证 include、输入读取、输出产生 | 把 smoke-test 步数写成 production 设置 |
| 生产 PTMC 统计曲线 | 确认温度范围、`PT.M`、MPI ranks、`PT.nblk_T`、`nblk`、`nbeg_blk`、采样输出 | 直接套 Lecture-4 example 的温度和步数 |
| 能量 / 比热曲线 | 确认 `E_PTMC_K.dat`、`C_PTMC_K.dat` 输出目标和 sample count | 只看 run 结束就认为统计充分 |
| 极化 / 晶格趋势 | 确认 `atom_Heff.getP`、`Zeff.dat`、strain / lattice output 设置 | 运行后才发现缺 `Zeff.dat` 或输出覆盖没开 |
| 磁化趋势 | 确认模型中有磁自由度并确认 `atom_Heff.cal_mag` 等输出覆盖 | 磁化文件缺失时直接改画图脚本 |
| lowest-state / CG handoff | 确认 relax flags、`opt.*`、lowest outputs 和日志 `CG finish` 检查 | 把 `T_*_final*` 自动当成 global lowest state |
| 复现实例 | 先锁定当前目标目录与用户目标，再参考 run notes / examples 的文件家族 | 把旧 example 的 `SuperCell`、`PT.M`、`Z_values` 当默认值 |

## Stage 2：正式 input 与 run 准备

进入本阶段前必须已经满足：
- `USER_CONFIRMED_L4_MC_SETTINGS=true`
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`

### 当前阶段输入文件
- 通过 S4 的 candidate 输入包及其 preflight 结论。
- 用户确认的 L4 设置表和 reference inventory。
- 上游 `local_mode_PM.dat`、`J_best.dat`、结构文件、初始态文件和条件输入。
- 运行环境信息：计划命令、MPI ranks、scheduler / image / executable、stdout / stderr 路径。

### 当前阶段已知输出
- formal `input/` 基线及 `input/README.md`。
- `runs/<run-id>/` 运行目录及 `runs/<run-id>/README.md`。
- run 目录内的提交 helper 或外部任务配置草案；真正提交仍需用户明确提交授权。

### 待运行验证的依赖
- PASP 是否正常解析全部 include、默认值和条件文件，需要运行后从 `PASP.used_info` 确认。
- scheduler 实际分配的 MPI ranks、stdout / stderr 名称、PASP build / image 版本，需要提交系统或运行日志确认。
- 预期输出家族能否产生，需要 Stage 4 output validation 确认。

### 上游依赖
- Stage 1 candidate 包必须已经通过 S3 / S4 gate。
- `local_mode_PM.dat`、`J_best.dat`、结构和初始态文件仍必须保持和 preflight 时相同；若替换，回到 candidate。

### 下游去向
- `runs/<run-id>/` 是 Stage 3 唯一推荐执行位置。
- 运行完成后进入 Stage 4 output validation；不得直接 handoff 给绘图或后续 workflow。

### 本阶段使用的脚本 / helpers
- scheduler helper、`run.sh`、`sub_pasp`、module setup、`mpirun` / `mpiexec` 命令只负责运行已 preflight 的 formal input。
- helper 应记录工作目录、`-np` 来源、PASP executable / image 和 stdout / stderr；它不能改变 PASP input gate 结论。

正式 `input/README.md` 至少记录：
- candidate 来源和 preflight 证据路径。
- 上游 `local_mode_PM.dat`、`J_best.dat`、初始态文件、结构文件来源。
- 已确认的 temperature / PT / step / strain / output 设置表。
- 哪些文件是科学输入，哪些只是环境 helper。

`runs/<run-id>/README.md` 至少记录：
- 从哪个 formal `input/` 派生。
- 实际命令、MPI ranks、scheduler、image / executable / PASP version、工作目录。
- stdout / stderr / `log.out` 路径。
- run 类型：MC、PTMC、CG / relax、output-validation-only。
- 预期输出家族和下游 handoff 文件。
- 若是 small-cell / short-step smoke run，记录被缩小的 `SuperCell`、`PT.M`、`PT.niter`、`PT.nblk_T`、`nbeg_blk`、`nblk` 等关键设置，并明确这些设置只用于快速 workflow 验证。

提交 helper 可以在 run 目录中按环境调整，但如果改动影响 `PASP.input` / `MC.input` 或被 PASP 读取的文件，必须回到 candidate + input-preflight gate。

### MC / PTMC 的 `mpirun` 启动方式

Lecture-4 和 `sub_pasp` examples 都显示 MC / PTMC 可以通过 MPI 方式启动 PASP。典型形态是：

```bash
mpirun -np "$SLURM_NTASKS" "${BIN_DIR}/PASP.x"
```

也可以在本地或非 scheduler 环境中使用固定进程数，例如：

```bash
mpirun -np 8 /path/to/PASP.x >log.out 2>>log.error
```

workflow 处理提交 helper 时应记录：
- `mpirun` / `mpiexec` 命令和实际 `-np`。
- scheduler 中的 `SLURM_NTASKS`、`--ntasks` 或等价进程数来源。
- `BIN_DIR` / `PASP.x` 路径、module 环境、`OMP_NUM_THREADS`。
- stdout / stderr 是否重定向到 `log.out`、`pasp.%j.out`、`pasp.%j.err` 或其他文件。
- `PT.M` 是否能被实际 MPI 进程数整除。

`mpirun` 命令本身不能替代 L4 input preflight，也不是提交授权。它只是在 preflight 通过后、用户明确授权提交时可用的运行方式。

## Stage 3：运行与运行中证据

### 当前阶段输入文件
- `runs/<run-id>/` 中从 formal `input/` 派生的完整输入包。
- 已接入 run 目录的上游模型文件、初始态文件、条件输入和提交 helper。
- 用户明确提交授权或本地运行授权记录。

### 当前阶段已知输出
典型运行证据：
- `log.out` 或 scheduler stdout / stderr。
- `PASP.used_info`：实际生效参数、默认值、include 解析记录。
- `seed_used.in`：实际随机种子。
- PTMC 日志中的温度 / block / iteration 进度和 `End of PTMC`。
- CG / relax 路径中的 `CG finish` 或等价收敛证据。

### 待运行验证的依赖
- 实际输出文件集合、warning / error、sample count、bin-size 诊断和 final / lowest-state 文件语义，必须等运行结束后验证。
- 如果作业只产生 scheduler 成功状态而没有 PASP 完成 marker，不能视为 PASP 成功。

### 上游依赖
- 本阶段只能从 Stage 2 的 formal `input/` 和对应 run README 推进；不得混入 sibling run 输出。

### 下游去向
- 运行结束后进入 Stage 4 output validation。
- 未完成或缺少日志证据的 run 只能进入 debug / rerun 处理，不能 handoff。

### 本阶段使用的脚本 / helpers
- 只在 `runs/<run-id>/` 内执行 `mpirun` / `mpiexec`、scheduler 脚本或本地 wrapper。
- 不要在 baseline `input/` 中运行 PASP；如需修改 PASP 读取文件，返回 candidate + S4 preflight。

不要用“作业状态成功”单独判断 PASP 运行成功；必须结合日志和输出文件验证。

## Stage 4：Output Validation

运行完成后、绘图或 handoff 前，必须单独做 output validation。优先使用 `pasp-verifier`：

```text
mode: output-validation
Workflow / stage: L4 Monte Carlo / output validation
```

### 当前阶段输入文件
- 指定的 `runs/<run-id>/` 目录。
- formal `input/README.md`、`runs/<run-id>/README.md`、运行命令 / ranks / scheduler 记录。
- `PASP.input`、`MC.input`、`PASP.used_info`、日志、stdout / stderr 和实际输出文件。

### 当前阶段已知输出
- `OUTPUT_VALIDATION_PASS=true`、fail 或 blocked 结论。
- 可 handoff 的具体文件清单、证据路径和不确定项。
- 若验证失败，输出需要重跑、补证据或人工接受统计风险的阻断原因。

### 待运行验证的依赖
- output validation 本身必须读取当前 run 的实际产物；不能用 run-notes、旧 output 或 sibling run 替代。
- 统计充分性、CG / relax 收敛和 final / lowest-state 语义必须以当前 run 日志和文件为准。

### 上游依赖
- Stage 2 / Stage 3 的 formal input、run metadata 和实际运行日志。
- 如果 run 目录不能证明来自对应 formal input，结论应 blocked。

### 下游去向
- 只有 output validation pass 后才能进入 Stage 5 handoff。
- fail / blocked 只能进入 rerun、debug、补证据或用户风险确认，不能直接绘图或传给后续 workflow。

### 本阶段使用的脚本 / helpers
- 优先使用 `skills/subskills/pasp-verifier/skill.md` 的 `mode: output-validation` 做只读事实检查。
- 可使用用户提供的只读分析脚本辅助检查输出形状或列数，但脚本结果不能覆盖日志和 `PASP.used_info` 证据。

### 通用检查
- 日志有正常完成证据，例如 `PASP is finished gracefully.`。
- PTMC 任务有 `End of PTMC` 或等价完成 marker。
- `PASP.used_info` 与 formal input 中关键设置一致。
- 输出来自同一个 run，不混用 sibling output 或旧 run。
- warning / error 已被读取并判断是否影响当前 handoff。

### 统计输出家族
按目标和启用设置检查，不要求所有文件都存在：

| 输出 | 角色 |
|---|---|
| `E_PTMC.dat` / `E_PTMC_K.dat` | 能量随温度 |
| `C_PTMC.dat` / `C_PTMC_K.dat` | 比热随温度 |
| `M_PTMC.dat` / `M_PTMC_K.dat`、`Mabs_PTMC*`、`M2_PTMC*` | 磁化相关输出，需确认磁化输出覆盖已启用 |
| `P_abs.dat` | 极化相关输出，通常需要 `Zeff.dat` 和对应输出设置 |
| `abc_cell_str_K.dat`、`strain_K.dat` | 晶格 / strain 统计 |
| `u_sort_K.dat`、`u_sep_K.dat`、`u_abs_sep_K.dat`、`u2_sep_K.dat` | local-mode / displacement 统计 |
| `nsample_PTMC.dat`、`Eachstatstep_T*.dat` | 采样量和逐步诊断 |

若 `C_PTMC*`、`X_PTMC*` 或诊断文件提示 bin-size / block 数不足，应把 output validation 结论降级为 fail 或 blocked，直到用户接受统计风险或重跑。

### final-state 与 lowest-state

不要混淆这些输出家族：
- `T_*_final*`、`T_*_final_.amp`、`final_amp_ptmc.*`、`final_ene.*`：每温度或每副本末态 / 汇总文件，不自动保证是全局最低态。
- `lowest_ene.ene_allnode`、`lowest_ene.ene_node*`、`lowest_ene.amp_local_mode`、`lowest_ene.str_mode_amp`、`lowest_ene.pos`、`lowest_ene.ene`、`lowest_ene.convergence`、`lowest_ene.ene_symbol`：lowest-state 家族。
- `relax-lowest_ene.*`：relax / CG 路径输出；必须同时有日志收敛证据，才能称为 relaxed result。

## Stage 5：下游 handoff

handoff 必须在 output validation pass 后进行，并记录 provenance：
- run id
- formal input 来源
- `local_mode_PM.dat` / `J_best.dat` 来源
- 命令、MPI ranks、PASP build / image
- validation 证据路径
- 下游应该消费的具体文件

### 当前阶段输入文件
- Stage 4 validation pass 结论和允许 handoff 的文件清单。
- 当前 run 的 provenance：formal input、上游模型文件、命令 / ranks、PASP build / image 和日志证据。

### 当前阶段已知输出
- 面向绘图、继续 MC/MD、结构分析或其他 workflow 的 handoff 说明。
- 仅包含已验证、语义清楚的文件路径；不把 final-state 文件误写成 lowest-state。

### 待运行验证的依赖
- 下游工具是否接受这些文件格式，属于下游 workflow 或用户工具验证范围。
- 如果下游要求额外转换脚本、坐标格式或编号规则，必须先查对应 reference 或下游 workflow。

### 上游依赖
- 本阶段严格依赖 Stage 4 output validation pass。
- 若用户改选其他 run、其他温度或其他 final-state 文件，必须重新验证该文件语义。

### 下游去向
- 统计曲线、结构 / 位移分析、后续初态、或模型诊断；具体去向由用户目标和已验证文件决定。

### 本阶段使用的脚本 / helpers
- 绘图、转换或下游启动脚本只消费 Stage 4 允许 handoff 的文件。
- 脚本不能反向改变 input preflight 或 output validation 结论；如发现文件语义不匹配，应回到 Stage 4 或相应下游 workflow。

常见 handoff：
- 画温度曲线：`E_PTMC_K.dat`、`C_PTMC_K.dat`、`M_PTMC_K.dat`、`P_abs.dat`、`abc_cell_str_K.dat`、`strain_K.dat`、`u_*_K.dat`。
- 继续 atomic effective-Hamiltonian 初态：经验证的 `lowest_ene.amp_local_mode` 或用户明确选择的 `T_*_final_.amp`。
- 结构 / 位移分析：经验证的 `lowest_ene.pos`、`lowest_ene.str_mode_amp` 或相关 XSF 文件。
- 拟合 / 模型诊断：`lowest_ene.ene_symbol`、`lowest_ene.ene`、`PASP.used_info`。

如果用户要求把 L4 输出接回 L3 / L2 / magnon，需要先说明文件语义是否匹配。`atomic_effective_H` 的 `amp_local_mode` handoff 不能直接当成 L2 `spin3.in`。

## 不负责回答的内容
- `PT.M`、`Temperature`、`local_mode.MC_mode_range`、`atom_Heff.*` 等字段的精确定义、默认值、单位或限制。
- `J_best.dat`、`local_mode_PM.dat`、`amp_local_mode.in`、`Zeff.dat` 的完整格式。
- 任何从 Lecture-4 examples 或旧 run 中继承的材料特定参数是否适合当前体系。

这些问题应转到 `skills/knowledge/reference/` 或由用户提供当前任务的权威来源。
