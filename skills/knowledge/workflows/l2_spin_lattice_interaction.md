# Workflow: `Model Spin_lattice_interaction`

> 给定材料的 spin Hamiltonian（J 矩阵 + SIA + DM + 可选四阶项），用并行回火 Monte Carlo 找到磁基态构型，并可选共轭梯度松弛。

> **先读 gate**：正式写输入、提交或解释失败前，先读 sibling `l2_spin_lattice_interaction_state_machine.md`。本文件补充每个 stage 的输入、输出、可调项、reference 查证点和运行后验证规则；不能覆盖 gate 中的 STOP 条件。

---

## 适用问题

- 我已经有 `spin_exchange.dat`，想找到这个 Hamiltonian 的磁基态
- 我想用并行回火 MC 扫一个温度区间，分析磁化强度 / 比热 / 磁化率随温度的演化
- 我想找到 spin 基态作为后续 magnon 计算的初始构型
- 跑过一次但磁基态明显错了，想排查温度网格 / 步数 / 副本数是否够

> 本文档不解决：
> - 从 DFT 拟合得到 `spin_exchange.dat`（由 `find_J_path_sym` + 用户的 VASP 流程完成，见 `workflows/l2_find_J_path_sym.md`）
> - 给定基态算磁子色散（见 `workflows/l2_magnon.md`）
> - 字段语法 / 默认值 / 单位（见 `reference/`）

---

## Pre-flight：确认

正式写入、覆盖、派生 run 目录或提交前，必须先完成只读 preflight。

必须确认：
- `spin_exchange.dat` 的来源：DFT 四态法拟合、文献参数、还是手工构造。
- `spin_exchange.dat` 的格式可读：`nJ`、3 行晶格矢量、`nJ` 行 J 矩阵、`dJ/du`、SIA、DM、四阶项计数顺序完整。
- `SuperCell` 能容纳用户预期的磁周期；不能从 NiI2 讲义例子直接借。
- `PT.M`、`PT.low_temp`、`PT.high_temp`、`PT.Tmesh`、`PT.nblk_T`、`nblk`、`nbeg_blk` 的物理意图和算力预算已确认。
- 是否需要 `spin_lat.relax_str T`。开启后会增加 wall time，且只有日志同时出现 `CG finish` 与 `PASP is finished gracefully.` 并写出 `relax-spin3_lowest.out`，才能把结果称为 CG-relaxed ground state。
- 当前提交镜像 / PASP build。2026-05-10 已验证 `docker.sii.shaipower.online/inspire-studio/paspmpi:v2` 能让 NiI2 Spin_lattice 例子完成 CG；但当前任务仍必须以自己的 `log.out` 为准。

## 输入包与运行目录契约

- `inputs/` 或 stage `input/` 是干净输入基线，只放可复用的 PASP 输入和环境模板。
- 每次实际运行都应新建 `runs/<run-id>/`，把输入包完整复制进去，再只在 run 目录内提交。
- 除非用户明确接受污染风险，不要在 baseline `inputs/` 里直接跑 PASP；`Spin_lattice_interaction` 会写大量 `T_*`、`node_*`、`final*`、`*_PTMC*` 输出，容易污染模板。
- 提交脚本是环境 helper，不是科学输入。改镜像、队列、核数可以在 run 目录里做；改 `PASP.input` / `MC.input` 数值必须先按 reference 和用户确认执行。

## Reference-before-write

准备写入或修改任何 PASP 字段、block、文件格式、编号规则时，必须先读对应 `skills/knowledge/reference/` 卡片。模板和历史 run notes 只能提供写法参考，不能授权当前任务的物理数值。

高风险字段：
- 结构与编号：`cell.str`、`unit_cell.str`、`SuperCell`、`Z_values`、`isaAB`、`Spin_values`
- Hamiltonian：`spin_exchange.dat`、`spin_lat.general_J`、`spin_lat.LJmatSym`
- PTMC：`MC`、`Parallel_Tempering`、`PT.M`、`PT.low_temp`、`PT.high_temp`、`PT.Tmesh`、`PT.nblk_T`、`nblk`、`nbeg_blk`
- 初始态 / 松弛：`Read_init_spin`、`spin3.in`、`spin_lat.relax_str`、`opt.NSW`、`opt.EDIFFG`
- 外场：`ExternalMagneticField`

## 任务目标 -> 推荐调整方向

| 目标 | 优先考虑 | 不要先做 |
|---|---|---|
| 找基态但结果不稳定 | 增大 `SuperCell` 或重新确认磁周期；再增加 `PT.nblk_T` / `nblk` / `PT.M` | 直接把 magnon 的异常归因于 q 路径 |
| 统计曲线噪声大 | 增大 `PT.nblk_T`、`nblk`，检查 `nbeg_blk` 后有效样本数 | 只改画图脚本平滑 |
| 温度交换不充分 | 调整 `PT.M`、温度上下限、`PT.Tmesh`；检查日志交换率 | 盲目扩大 MC 步数但温度网格仍不合理 |
| 需要 CG-relaxed 基态 | 开 `spin_lat.relax_str T`，设置 `opt.NSW` / `opt.EDIFFG`，使用已验证 PASP build | 只看到 `spin3_lowest.out` 就声称 relaxed |
| 给 magnon 准备初态 | 优先 `spin3_lowest.out`；CG 成功且用户需要时用 `relax-spin3_lowest.out` | 默认用 `node_N_finalspin.out` |
| 重现实例 | 先锁定当前目录文件和用户目标，再参考 run notes | 把 NiI2 讲义数值当成当前材料默认值 |

---

## Stage 1：输入包准备

### 当前阶段输入文件

| 来源 | 文件 | 是否硬性必需 | 说明 |
|---|---|---|---|
| 用户 / 上游 | `cell.str` | 必需 | 在 `SuperCell` 扩胞前的最小晶胞或较小超胞 |
| 用户 / 上游 | `unit_cell.str` | 必需 | 最小原胞，用于内部坐标参考 |
| 用户 | `PASP.input` | 必需 | 含 `Model Spin_lattice_interaction`、`%include MC.input`、`%block SuperCell`、`Z_values`、`isaAB`、`Spin_values`、`fig.maxk`、`fig.mdist` |
| 用户 | `MC.input` | 必需（被 `%include` 引入） | PT 与 MC 步数 / 温度网格 / 共轭梯度参数；典型字段：`MC`、`Parallel_Tempering`、`spin_lat.general_J`、`spin_lat.LJmatSym`、`Read_init_spin`、`PT.M`、`PT.low_temp`、`PT.high_temp`、`PT.Tmesh`、`PT.nblk_T`、`nbeg_blk`、`nblk`、`spin_lat.relax_str`、`opt.NSW`、`opt.EDIFFG`、`ExternalMagneticField` |
| **上游（find_J + DFT 拟合）** | `spin_exchange.dat` | **必需** | 文本格式（不是二进制，尽管编辑器或 Read 工具可能因长行误判）；第一段 3 行 lattice vector 必须来自 `unit_cell.str` / `unit_cell_in_Ang`，J pair 坐标应来自 `find_J_path_sym` 的 nearest-image `pair_coord` 或等价上游输出；由 `spin_lat_subs.f90:113 write_spin_exchange_file` 写出，由 `spin_lat.F90:1999–2012 read_exchange_para` 读取 |
| 用户 | `seed.in` | 可选 | 固定随机种子；不写则 PASP 用默认 |
| 环境 | `run.sh` 或等价提交脚本 | 必需（提交时） | 不属于 PASP 输入；按 HPC 环境写 |

### 当前阶段已知输出

`PASP.input` + `MC.input` + `spin_exchange.dat` 全部齐备并通过基本一致性检查（npair、unit-cell 晶格向量、nearest-image pair 坐标 provenance、npair 行 J-matrix、4 个尾部相互作用计数）。

### 待运行验证的依赖

- `spin_exchange.dat` 的 npair 是否与用户对体系的物理理解一致
- `SuperCell` det 与 unit_cell 原子数的乘积是否落在 PASP 内存预算内
- `PT.M` 必须能被 planned MPI rank 数整除；若 `PT.M < rank_count` 或不能整除，会出现空闲 / 不匹配的 rank 分配风险。提交 rank 未知时，preflight 至少应标为 blocked 或要求提交前复查。

### 上游依赖

- `find_J_path_sym` workflow 末尾的 DFT 四态法拟合产物 `spin_exchange.dat`
- 用户对温度区间 / PT 副本数 / 步数的物理判断

### 下游去向

- Stage 2 直接消费

### 本阶段使用的脚本

| 何时 | 脚本 |
|---|---|
| `spin_exchange.dat` 文本格式校核 | 检查文件结构：1 行 `npair # units in eV and Ang` → 3 行 `unit_cell.str` / `unit_cell_in_Ang` 原胞晶格向量（仅 npair ≥ 1 时存在）→ npair 行 J-matrix（每行 `i J is1 is2 coord1(3) coord2(3)`，coord 应为 `find_J_path_sym` nearest-image `pair_coord` / 等价上游输出）→ 1 行 dJ/du 计数 → 1 行 SIA 计数 → 1 行 DM 计数 → 1 行四阶计数；后 4 行计数若为 0 表示无该类项 |
| 隔离运行目录 | 推荐：`mkdir -p runs/<run-id>/` 并 `cp -r inputs/* runs/<run-id>/` |

### 任务目标 -> 推荐调整方向

- 改 `SuperCell`：仅用于容纳磁周期或控制体系尺寸；改前检查行列式、原子数和资源预算。
- 改 `spin_exchange.dat`：只接受明确上游拟合/文献/手工来源；不要在本 stage 里临时“修”J 值。
- 改 `Read_init_spin`：若设为 `T`，必须提供与当前超胞全原子顺序一致的 `spin3.in`。
- 改 `spin_lat.LJmatSym`：用于控制是否对 J 矩阵做对称化/约简；需先查 reference 并确认用户意图。

### 修改后要检查什么

- `PASP.input` 中的 `%include MC.input` 指向当前 run 目录内存在的文件。
- `cell.str` / `unit_cell.str` / `SuperCell` 对应的原子数与后续 handoff 行数规则一致；注意 `cell.str` / `SuperCell` 定义 MC 模拟胞扩展，不能替代 `spin_exchange.dat` 第一段的 `unit_cell` 基矢。
- `spin_exchange.dat` 的 J 矩阵行数、4 个尾部计数块完整；第一段晶格向量来自 `unit_cell.str`，J pair 坐标来自 nearest-image `pair_coord` / 等价上游输出，不能由 agent 手工平移或调整。
- 如果 `Read_init_spin T`，`spin3.in` 非空数据行数等于当前超胞全原子数。

---

## Stage 2：运行 PT MC + 共轭梯度

### 当前阶段输入文件

Stage 1 完整输入包。

### 当前阶段已知输出

由 PASP 源码（`PTMC.F90` / `PTMC_common.F90` / `PTMC_measure.F90`）静态确认。

#### A. 通用元数据

| 输出 | 数量 | 角色 |
|---|---|---|
| `log.out`（来自 `run.sh` 的 stdout 重定向） | 1 | PASP 标准输出，含 `init_spin_lat_MC` 读 `spin_exchange.dat` 摘要、PT 进度、CG 收敛信息 |
| `PASP.used_info` | 1 | 实际生效的输入参数；用于核对默认值是否覆盖 |

#### B. 每温度的最终自旋构型（`T_*` 系列，文件名嵌入温度浮点值，格式 `E18.12`）

| 输出 | 数量 | 角色 |
|---|---|---|
| `T_<temp>_final.all_atoms_spin.xsf` | 每 PT 副本 1 份 | 末态 XSF 可视化（含全部原子 + spin 矢量） |
| `T_<temp>_final.onlyspin.xsf` | 每 PT 副本 1 份 | 仅磁性原子 |
| `T_<temp>_final_actual.all_atoms_spin.xsf` | 每 PT 副本 1 份 | 实际位置（含 CG 弛豫位移） |
| `T_<temp>_final_originalpos.all_atoms_spin.xsf` | 每 PT 副本 1 份 | 原始位置 + 末态 spin |
| `T_<temp>_final_originalpos.onlyspin.xsf` | 每 PT 副本 1 份 | 同上仅磁性原子 |
| `T_<temp>_final_actual.displacement_car.xsf` | 每 PT 副本 1 份 | CG 位移（笛卡尔） |
| `T_<temp>_final_originalpos.displacement_car.xsf` | 每 PT 副本 1 份 | CG 位移（原始位置） |
| `T_<temp>_final_originalpos.displacement_dir.xsf` | 每 PT 副本 1 份 | CG 位移（直接坐标） |
| `T_<temp>_spin_q.dat` | 每 PT 副本 1 份 | 自旋结构因子 S(q)；条件 `lcal_spin_str` |
| `T.dat` / `new_T.dat` | 各 1 | 温度网格记录与自适应调整 |

#### C. 每节点 / 全局最低态自旋（`*node*` + `spin3_lowest` 系列）— **下游接力的关键**

| 输出 | 数量 | 角色 |
|---|---|---|
| **`spin3_lowest.out`** | 全局最低能量节点 1 份 | **4 列 `ia sx sy sz`；优先作为 magnon 的 `spin3.in` 来源** |
| **`relax-spin3_lowest.out`** | `spin_lat.relax_str T` 且 CG 成功时 1 份 | CG-relaxed 全局最低能量 spin3；当用户要用松弛后的基态接给 magnon 时优先考虑 |
| `node_N_spin.out` | 每 MPI rank 1 份 | 该 rank 在 MC 历史中保存的最低能量 spin3；当 `spin3_lowest.out` 缺失时，可结合 `final_ene.all` 选最低节点作为备选 handoff |
| `node_N_final_spin.out` | 每 MPI rank 1 份 | `output.F90` 在 PTMC 后写出的该 rank 末态 spin3；不保证是最低能量态 |
| `node_N_finalspin.out` | 每 MPI rank 1 份 | `PTMC.F90` 在 PTMC 结束时写出的该 rank 末态 spin3；不保证是最低能量态 |
| `final_spin_str_node_NNN_pt_NNN.dat` | 每节点 × 每 PT 副本 1 份 | 节点 PT 末态自旋结构因子 |
| `avg_spin_str_NNN.dat` | 每节点 1 份 | 该节点统计平均的结构因子 |

#### D. 统计步逐步记录（`Each*` 系列）

| 输出 | 数量 | 角色 |
|---|---|---|
| `Eachstatstep_T<idx>.dat` | 每温度索引 1 份 | 每统计步 `node stat_step E(Hartree) M(a.u.)` |

#### E. 末态汇总（`final*` 系列）

| 输出 | 数量 | 角色 |
|---|---|---|
| `final_pt_spin3.<idx>` | 每温度 1 份 | 该温度末态 spin3（向量） |
| `final_pt_spin.<idx>` | 每温度 1 份 | 该温度末态 spin（标量） |
| `final_amp_ptmc.<idx>` | 每温度 1 份 | amp 数据 |
| `final_ene.<idx>` | 每温度 1 份 | 该温度末态能量 |
| `final_ene.all` | 1 | 所有温度的末态能量汇总；用于挑选哪个温度的末态最低 |

#### F. 物理观察量随温度的曲线（**实际生产意义最大**）

| 输出 | 含义 |
|---|---|
| `M_PTMC.dat` / `M_PTMC_K.dat` | 磁化强度 vs T |
| `Mz_PTMC.dat` / `Mz_PTMC_K.dat` | M_z 分量 |
| `Mabs_PTMC.dat` / `Mabs_PTMC_K.dat` | \|M\| |
| `M2_PTMC.dat` / `M2_PTMC_K.dat` | <M²> |
| `E_PTMC.dat` / `E_PTMC_K.dat` | 能量 vs T |
| `E2_PTMC.dat` / `E2_PTMC_K.dat` | <E²> |
| `C_PTMC.dat` / `C_PTMC_K.dat` | 比热 vs T（峰位 ≈ T_C / T_N） |
| `X_PTMC.dat` / `X_PTMC_K.dat` / `X_PTMC_K_SI.dat` | 磁化率 vs T |
| `MCE.dat` | 磁热效应 |
| `nsample_PTMC.dat` / `EEt_MMt_PTMC.dat` / `check_C.dat` | 采样诊断 |
| `initial_ene.all` / `E_<NNNN>` | 初始能量与各 rank 能量 |

后缀 `_K` 是温度以 Kelvin 为横坐标；不带后缀的横坐标是 Hartree 内部温度。

### 待运行验证的依赖

- 当前 PASP 版本对 `T_<temp>` 浮点编码（`E18.12`）的精度——文件名长度可能在不同 build 间略有差异
- `lcal_spin_str` 默认值；如果用户未设，`T_*_spin_q.dat` 是否产生需运行后核对
- `lwrite_lowest`（单温度 MC 路径专用）在 PT 路径下是否被忽略

### 上游依赖

Stage 1 完整输入包。

### 下游去向

- **`spin3_lowest.out` → 用户拷贝改名为 `spin3.in` → 喂给 `Model magnon`** 作为 MC 最低态初始构型。复制前必须检查行数是否等于 `det(SuperCell) × cell.str 原子数`。
- 若 `spin_lat.relax_str T` 且 `relax-spin3_lowest.out` 存在，可按用户意图优先使用 `relax-spin3_lowest.out` 作为 CG-relaxed handoff；同样必须先做行数校验。
- 若 `spin3_lowest.out` 不存在，可用 `final_ene.all` 找最低节点，再用对应 `node_N_spin.out` 作为备选；不要默认用 `node_N_finalspin.out`，因为它是 PTMC 末态，不保证是最低态。
- 物理观察量曲线（`*_PTMC_K.dat`） → 用户的画图脚本，分析 T_C / T_N / 磁化平台
- `T_*_final.*.xsf` → VESTA / OVITO 可视化基态构型
- `final_ene.all` → 用户检查不同温度副本的能量是否单调递增

### 本阶段使用的脚本

| 何时 | 脚本 |
|---|---|
| HPC 提交 | `run.sh`（按 HPC 环境，仓库 inputs 中是 32 核 Slurm 模板，单节点 mpirun + Intel oneAPI） |
| 跑完整理输出 | `mv T_* *node* Each* final* node_data/` 把巨量输出归到子目录（参见 inputs 中 run.sh 末尾） |
| 后处理 | 用户自写：从 `*_PTMC_K.dat` 画 T-曲线；从 `spin3_lowest.out`（优先）或 `node_N_spin.out`（备选）提 `spin3.in` 给 magnon |

### 任务目标 -> 推荐调整方向

- 想减少失败风险：先用较小 `PT.nblk_T` 做 smoke test，确认 `spin_exchange.dat` 可读、PTMC 能进入循环、输出文件路径正常；正式科学结果再扩大采样。
- 想提高统计质量：优先增加 `PT.nblk_T` 和 `nblk`，并检查 `nbeg_blk` 后是否有足够 measurement。
- 想检查相变温度：关注 `C_PTMC_K.dat`、`X_PTMC_K.dat`、`M*_PTMC_K.dat`，不要只看最低能态文件。
- 想接给 magnon：先保证 `spin3_lowest.out` 或 `relax-spin3_lowest.out` 存在且行数正确，再复制为 `spin3.in`。

### 修改后要检查什么

- `log.out` 必须出现 `End of PTMC` 才能说 MC 主循环完成。
- `log.out` 若出现 `SIGSEGV` / `forrtl: severe`，不得说 run 完全成功；只能根据已写文件标注部分成功。
- 若 crash 发生在 `M,Mdir:` 之后且 `spin3_lowest.out` 存在，可标注为"PTMC 完成，最低态文件已生成；CG / 后处理未干净结束"。
- `spin_lat.relax_str T` 时必须额外检查是否出现 `CG finish`、`PASP is finished gracefully.` 和 `relax-spin3_lowest.out`；缺任一项时不能声称 CG relaxed ground state 可用。
- `spin3_lowest.out` / `relax-spin3_lowest.out` 校验时统计非空数据行；源码会在末尾写一个空行。
- 如果 `PT.n_binsize` 相关 warning 提示 bin method 不可用，应记录 warning，并考虑更小 `PT.n_binsize` 或更大的 `PT.nblk_T`。

### 服务器实跑后应补录的信息

- run 目录、提交镜像、PASP build、job id、MPI ranks。
- `log.out` 中的 `PT_niter,ns_blk,nblk,nblk_T`、是否 `End of PTMC`、是否 `CG finish`、是否 graceful finish。
- `spin3_lowest.out` / `relax-spin3_lowest.out` 的非空数据行数和选择哪个文件接给下游。
- 若有异常，记录最后 50 行日志、是否已经写出 handoff 文件、哪些输出只算部分成功。

---

## Stage 3：把基态接力给下游

> 这一阶段的产物**不是** PASP 输入，而是把 Stage 2 输出按下游消费者的契约整理。

### 当前阶段输入文件

| 来源 | 文件 | 角色 |
|---|---|---|
| Stage 2 | `spin3_lowest.out`（优先） | 4 列 `ia sx sy sz`，与 magnon 的 `spin3.in` 同格式；全局最低节点产物 |
| Stage 2 | `relax-spin3_lowest.out`（CG 成功时） | CG-relaxed 4 列 `ia sx sy sz`；用户需要松弛基态时优先 |
| Stage 2 | `node_N_spin.out`（备选） | 单个 MPI rank 的最低态；仅在 `spin3_lowest.out` 缺失时使用 |
| Stage 2 | `final_ene.all` | 用于挑选哪个 node 是最低能量末态 |
| Stage 2 | `T_<lowest_temp>_final.*.xsf` | 可视化最低温末态 |

### 当前阶段已知输出

| 输出 | 角色 |
|---|---|
| `spin3.in`（拷自 `spin3_lowest.out` 或备选 `node_N_spin.out`） | magnon workflow Stage 1 的硬性输入 |
| 用户的能量挑选记录 | 哪个 node 的能量最低、对应温度是多少 |

### 下游去向

- `workflows/l2_magnon.md` Stage 1（spiral 子例尤其敏感于 spin3.in 的真实磁周期是否在 SuperCell 中合理表达）

### 修改后要检查什么

- `spin3.in` 来源文件、来源 run、是否 MC-lowest 或 CG-relaxed 已记录。
- `spin3.in` 非空数据行数等于 magnon 目标输入中的 `NumberOfAtoms(cell.str) * det(SuperCell)`。
- 如果 magnon 使用的 `cell.str` / `SuperCell` 与 Spin_lattice 上游 run 不同，必须重新确认原子顺序和磁周期；不能直接复制。

---

## Reference index for this workflow

按使用频率：

- **Files**: `cell.str` / `unit_cell.str` / `spin_exchange.dat` / `seed.in` / `spin3.in` / `spin3_lowest.out`
- **Params**: `Model` / `SuperCell` / `Z_values` / `isaAB` / `Spin_values` / `fig.maxk` / `fig.mdist` / `MC` / `Parallel_Tempering` / `spin_lat.general_J` / `spin_lat.LJmatSym` / `spin_lat.relax_str` / `Read_init_spin` / `PT.M` / `PT.low_temp` / `PT.high_temp` / `PT.Tmesh` / `PT.nblk_T` / `nbeg_blk` / `nblk` / `opt.NSW` / `opt.EDIFFG` / `ExternalMagneticField`
- **Topics**: `PASP.input` / `four_state_method`（链回 find_J 拟合）

完整路径：均在 `skills/knowledge/reference/`。若 reference 中缺某个输出家族的专门卡片，以本 workflow 的输出表作为 L2 当前稳定合同，并把缺口记入后续 reference audit。

---

## 不负责回答的内容

| 问题类型 | 转给 |
|---|---|
| 字段精确语法 / 默认值 / 单位 | 对应 reference 卡 |
| MC 长流程的 STOP gate / 用户确认序列 | `l2_spin_lattice_interaction_state_machine.md` |
| `find_J_path_sym` 流程 | `workflows/l2_find_J_path_sym.md` |
| 磁子色散 | `workflows/l2_magnon.md` |
| HPC 集群环境的 `run.sh` 写法 | 用户自定 |

---

## 历史观察

具体跑过哪些材料、哪些温度网格收敛、哪些 SuperCell 才能容纳磁基态周期、哪些版本化 build 异常 / 修复已观察到 → 见 sibling `l2_spin_lattice_interaction_run_notes.md`。

run notes 是历史观察记录，**不是当前用户工作区的事实**。当前用户的真实状态必须以用户实际目录中的文件为准。
