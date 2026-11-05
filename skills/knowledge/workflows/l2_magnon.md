# Workflow: `Model magnon`

> 给定 spin Hamiltonian + 磁基态自旋构型，沿一段 BZ 路径计算线性自旋波（LSWT）色散。

> **先读 gate**：正式写输入、提交或解释失败前，先读 sibling `l2_magnon_state_machine.md`。本文件补充输入合同、可调项、reference 查证点、输出格式和运行后验证规则；不能覆盖 gate 中的 STOP 条件。

---

## 适用问题

- 我有 spin Hamiltonian（`spin_exchange.dat`）和磁基态（`spin3.in`），想沿一段 BZ 算 magnon 色散
- 我想算多段路径拼成一条 Γ→M→X→Γ 的色散图
- 我想验证磁基态是否稳定（虚频暗示基态错了）

> 本文档不解决：
> - 找磁基态（见 `workflows/l2_spin_lattice_interaction.md`）
> - 拟合 `spin_exchange.dat`（见 `workflows/l2_find_J_path_sym.md`）
> - 高阶 magnon-magnon 散射 / 有限温度色散

---

## Pre-flight：确认

正式写入、覆盖、派生 run 目录或提交前，必须先完成只读 preflight。

必须确认：
1. **基态来源**：`spin3.in` 是手动构造的 FM/AFM/spiral，还是来自 `Spin_lattice_interaction` 的 `spin3_lowest.out` / `relax-spin3_lowest.out` / `node_N_spin.out`。
2. **SuperCell 与 spin3.in 行数一致**：非空数据行数必须等于 `NumberOfAtoms(cell.str) * det(SuperCell)`。源码写出的 `spin3_lowest.out` 末尾可能有空行，校验时要忽略空行。
3. **`spin_exchange.dat` 的四阶项必须为 0**：最后的 higher-order / fourth-order count 不能非零。
4. **q 路径**：`qpoints.magnon` 的两行端点和 `number_of_qpoints` 已由用户确认。默认 `spinw` legacy 路径每次只表达一段直线；多段路径要分段跑或由脚本分段改端点后拼接。
5. **`number_of_qpoints >= 2`**：线段模式需要起点和终点；不要依赖源码默认值 1。

## 输入包与运行目录契约

- `inputs/magnon/<case>/` 或 stage `input/` 是干净输入基线。
- 每次实际运行都应新建 `runs/<run-id>/`，把输入包完整复制进去，再只在 run 目录里执行 PASP 或路径拼接脚本。
- `run.sh` 可以改提交环境和多段路径端点，但不能绕过 `PASP.input` / `spin3.in` / `spin_exchange.dat` preflight。
- 不要在 baseline `inputs/` 中直接跑多段脚本；脚本会覆盖 `spin_wave_E.dat` 并生成拼接文件，容易污染模板。

## Reference-before-write

准备写入或修改任何 PASP 字段、block、文件格式、编号规则时，必须先读对应 `knowledge/reference/` 卡片。

高风险字段：
- 结构与编号：`cell.str`、`unit_cell.str`、`SuperCell`、`Z_values`、`isaAB`、`Spin_values`
- 基态：`Read_init_spin`、`spin3.in`、`spin3_lowest.out`
- Hamiltonian：`spin_exchange.dat`、`spin_lat.general_J`
- q 路径：`number_of_qpoints`、`qpoints.magnon`、可选 `spinw.use_block_BandLines`
- 输出诊断：`spinw.write_detail`

## 任务目标 -> 推荐调整方向

| 目标 | 优先考虑 | 不要先做 |
|---|---|---|
| 算 FM/collinear 色散 | 确认 `spin3.in` 全原子行数、四阶项为 0、q 路径端点 | 借 spiral 例子的 `SuperCell` |
| 算 spiral / 大周期色散 | 先确认磁周期和 `SuperCell`，再生成/复制匹配的 `spin3.in` | 只为了匹配行数而改 `SuperCell` |
| 多段高对称路径 | 分段运行并拼接，处理重复端点 | 在一个 `qpoints.magnon` block 里写多段端点 |
| 输出文件太大 | 经用户确认后关 `spinw.write_detail` | 删除 `spin_wave_E.dat` 以外的日志证据 |
| 色散有虚频 | 回查基态来源、`SuperCell`、`spin_exchange.dat` | 通过删 q 点或改画图范围掩盖 |

---

## Stage 1：输入包准备

### 当前阶段输入文件

| 来源 | 文件 | 是否硬性必需 | 说明 |
|---|---|---|---|
| 用户 / 上游 | `cell.str` | 必需 | 结构原胞或较小超胞 |
| 用户 / 上游 | `unit_cell.str` | 必需 | 最小原胞 |
| 用户 | `PASP.input` | 必需 | `Model magnon` + `%include unit_cell.str` + `%include cell.str` + `spin_lat.general_J` + `Read_init_spin T` + `number_of_qpoints` + `%block qpoints.magnon` + `%block Z_values` / `isaAB` / `Spin_values` / `fig.maxk` / `fig.mdist` / `%block SuperCell` |
| **上游（find_J + DFT 拟合 / 手动）** | `spin_exchange.dat` | **必需** | 文本格式；**最后一行的高阶项计数必须为 0**（见 R5） |
| **上游（`Spin_lattice_interaction` 或手动）** | `spin3.in` | **必需**（因 `Read_init_spin T`） | 4 列 `ia sx sy sz`；行数 = `det(SuperCell) × NumberOfAtoms_in_cell.str` |
| 环境 | `run.sh` | 必需（提交时） | 仓库 inputs/magnon/{FM,spiral}/run.sh 演示了多段路径拼接 |

### 当前阶段已知输出

`PASP.input` 的 q 路径 / `SuperCell` / `spin3.in` 三者一致性已通过 Pre-flight 2 / 3 检查。

### 待运行验证的依赖

- `cell.str` 在原胞（1 原子单胞）vs 较小超胞 形式下，是否都被 magnon 正确处理
- 多段路径拼接时，相邻段的端点是否真的对齐（`run.sh` 用 `sed -i '$d'` 删末尾行避免重复）

### 上游依赖

- `spin_exchange.dat`：来自 `find_J_path_sym` + DFT 拟合，**或** 手动构造（已知材料文献参数）
- `spin3.in`：优先来自 `Spin_lattice_interaction` 的 `spin3_lowest.out`（4 列与 spin3.in 同格式），备选为最低节点的 `node_N_spin.out`，**或** 手动按已知磁序写

### 下游去向

Stage 2 直接消费。

### 本阶段使用的脚本

| 何时 | 脚本 |
|---|---|
| 校验 spin3.in 行数 | 统计 `spin3.in` 的**非空数据行**，与 `det(SuperCell) × cell.str 原子数` 对比 |
| 校验 spin_exchange.dat 四阶项 | `tail -n 1 spin_exchange.dat` 必须以 `0` 开头 |
| 隔离运行目录 | `mkdir -p runs/<run-id>/` 并 `cp -r inputs/<sub>/* runs/<run-id>/` |

### 任务目标 -> 推荐调整方向

- 改 `SuperCell`：只在用户确认磁周期后改；改后必须重新校验 `spin3.in` 行数。
- 改 `spin3.in`：优先从当前上游 run 的 `spin3_lowest.out` / `relax-spin3_lowest.out` 复制；手写时必须保留非磁性原子零向量行。
- 改 `spin_exchange.dat`：只允许使用四阶项为 0 的版本；如果上游 Spin_lattice 文件含四阶项，应回到用户/上游拟合阶段生成适合 LSWT 的文件，不要在 magnon stage 静默删物理项。
- 改 q 路径：每次只写一段起点/终点；多段由脚本循环改端点并拼接。

### 修改后要检查什么

- `PASP.input` 是 `Model magnon`，且 `Read_init_spin T` 时 `spin3.in` 存在。
- `%block qpoints.magnon` 有且只有当前线段的起点、终点两行。
- `number_of_qpoints >= 2`。
- `spin3.in` 非空数据行数等于 `NumberOfAtoms(cell.str) * det(SuperCell)`。
- `spin_exchange.dat` 最后一段 higher-order / fourth-order count 是 0。

---

## Stage 2：运行 magnon（spinw 路径）

> 主程序入口：`main.F90:520–527`。默认走 `spinw` 路径（即 LSWT），除非 `lspinw=F` 显式切到旧 `magnon` 路径（旧路径输出文件不同，本 L2 magnon workflow 当前只覆盖默认 `spinw` 路径）。本仓库 inputs 不设 `lspinw`，即默认 spinw 路径。

### 当前阶段输入文件

Stage 1 完整输入包。

### 当前阶段已知输出（spinw 路径）

由 PASP 源码（`spinw.f90` / `read_input.F90`）静态确认：

| 输出 | 数量 | 角色 |
|---|---|---|
| `log.out`（stdout 重定向） | 1 | PASP 标准输出，含 `init_spin_lat_MC` 读 `spin_exchange.dat` 摘要、`spin3.in` 读取确认、每 q 点本征求解信息 |
| `PASP.used_info` | 1 | 实际生效的输入参数 |
| **`spin_wave_E.dat`** | 1 | **核心物理输出**：每行 `iq` + `na_spin` 个本征值，格式 `(I3, na_spin × f20.12)`；`na_spin = 磁性原子数 × det(SuperCell)` |
| `spin_wave_H_wf.dat` | 0 或 1 | H 矩阵 + 波函数详情；条件 `lwrite_detail=T` |

> magnon **不重写** `spin3.in`（源码静态扫描确认无 WRITE 到 spin3.in）。

### 待运行验证的依赖

- `spin_wave_E.dat` 中每行的本征值数量是否与 `det(SuperCell) × N_magnetic_atoms` 一致
- 不同 PASP 版本下本征值单位（meV vs Ha）；`log.out` 里通常会有提示
- 多段路径拼接的连续性（仅外部 `run.sh` 的责任）
- 2026-05-10 的 FM / spiral NiI2 run 已确认 `PASP is finished gracefully`，见 `l2_magnon_run_notes.md`

### 上游依赖

Stage 1 完整输入包。

### 下游去向

- `spin_wave_E.dat` → 用户的画图脚本（matplotlib），生成色散图
- 多段路径拼接 → 由 `run.sh` 拼成 `spin_wave_E_all.dat`（文本拼接，不是 PASP 输出；本仓库 inputs/magnon/{FM,spiral}/run.sh 用 `cat` + `sed -i '$d'` 去重边界）
- 虚频检测 → 用户判断基态是否稳定；不稳定则回 `Spin_lattice_interaction` 重找基态

### 本阶段使用的脚本

| 何时 | 脚本 |
|---|---|
| HPC 提交 | inputs/magnon/{FM,spiral}/run.sh：单核串行（PASP magnon 通常不需要并行）+ 三段路径拼接 |
| 改 q 路径 | `run.sh` 中的 `modify_qpoints` 函数（用 `sed` 改 PASP.input 的 `%block qpoints.magnon`） |

### 任务目标 -> 推荐调整方向

- 单段路径：直接运行一次，检查 `spin_wave_E.dat` 行数等于 `number_of_qpoints`。
- 多段路径：每段单独运行并保存片段，拼接时删除相邻段重复端点。
- 需要诊断虚频：保留 `spin_wave_H_wf.dat` 和完整 `log.out`。
- 只需要快速出图：经用户确认可设置 `spinw.write_detail F` 减少详细输出，但仍必须保留 `spin_wave_E.dat` 和 `log.out`。

### 修改后要检查什么

- `log.out` 不含 `SIGSEGV`、`abort`、明显 `Error`。
- `log.out` 含正常完成标志，例如 `PASP is finished gracefully.`。
- `spin_wave_E.dat` 存在，非空行数等于本段 `number_of_qpoints`。
- 每行列数为 `1 + na_spin`；第一列是 q 点编号。
- 若期望详细输出，`spin_wave_H_wf.dat` 存在；若不存在，先查 `spinw.write_detail` 实际值。

### 服务器实跑后应补录的信息

- run 目录、提交镜像、PASP build、job id。
- 每段 q 路径端点、`number_of_qpoints`、是否删除重复端点。
- `spin_wave_E.dat` 行数、每行本征值数量、是否存在虚频。
- `spin_wave_H_wf.dat` 是否生成及 `spinw.write_detail` 实际值。

---

## Stage 3：色散图与诊断

### 当前阶段输入文件

| 来源 | 文件 | 角色 |
|---|---|---|
| Stage 2 | `spin_wave_E.dat`（每段一份） | 本征值 vs q 索引 |
| Stage 2 | `spin_wave_E_all.dat`（拼接版） | 多段拼接的总色散 |
| Stage 2 | `spin_wave_H_wf.dat`（可选） | H 矩阵详情，用于排查 |

### 当前阶段已知输出

非 PASP 输出，由用户脚本完成：

- 色散图 `dispersion.png`
- 虚频清单（如有）

### 下游去向

- 与文献 / 实验中子散射数据对比
- 如发现虚频 → 触发 `Spin_lattice_interaction` 重新找基态的 feedback loop

---

## 关键 magnon 失败模式（来自 R5）

`spin3.in` 行数 vs `det(SuperCell) × NumberOfAtoms_in_cell.str` 不一致，是 magnon 最常见失败模式：

| 子例 | cell.str 原子数 | SuperCell det | spin3.in 应有行数 |
|---|---|---|---|
| FM | N | 1 | N |
| spiral / 大磁周期 | N | k | N × k |

**任何不一致都会导致 magnon 静默给出错误结果**（不一定崩溃）。Pre-flight 2 必须确认。

更多 collinear / spiral 差异见 `knowledge/reference/topics/magnon_collinear_vs_spiral.md`。

---

## Reference index for this workflow

按使用频率：

- **Files**: `cell.str` / `unit_cell.str` / `spin_exchange.dat` / `spin3.in` / `spin3_lowest.out` / `spin_wave_E.dat` / `spin_wave_H_wf.dat`
- **Params**: `Model` / `SuperCell` / `Z_values` / `isaAB` / `Spin_values` / `fig.maxk` / `fig.mdist` / `spin_lat.general_J` / `Read_init_spin` / `qpoints.magnon` / `number_of_qpoints` / `spin_noncollinear`
- **Topics**: `magnon_collinear_vs_spiral`

完整路径：均在 `knowledge/reference/`。

---

## 不负责回答的内容

| 问题类型 | 转给 |
|---|---|
| 字段精确语法 / 默认值 / 单位 | 对应 reference 卡 |
| 长流程的 STOP gate / 用户确认序列 | `l2_magnon_state_machine.md` |
| 拟合 `spin_exchange.dat` | `workflows/l2_find_J_path_sym.md` |
| 找磁基态 | `workflows/l2_spin_lattice_interaction.md` |
| 高阶 magnon-magnon 散射 / 有限温度色散 | 不在本仓库 PASP 工作流范围 |

---

## 历史观察

具体跑过哪些材料、哪些 q 路径、哪些 SuperCell 配 spiral 周期成功 → 见 sibling `l2_magnon_run_notes.md`。

run notes 是历史观察记录，**不是当前用户工作区的事实**。当前用户的真实状态必须以用户实际目录中的文件为准。
