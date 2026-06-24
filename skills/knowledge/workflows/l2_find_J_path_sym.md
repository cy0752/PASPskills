# Workflow: `Model find_J_path_sym`

> 找出材料中对称性不等价的磁性原子对（pair），并为后续四态法 DFT 计算准备结构与磁矩约束。

---

## 适用问题

- 我想找出材料中所有不等价的磁性原子对，以便用四态法拟合交换参数
- 给定一个晶体结构，需要知道前 N 近邻 pair 各自属于哪一组对称等价类
- 准备 VASP 端四态法 DFT 计算的完整输入素材（POSCAR + MAGMOM/M_CONSTR）
- 已经跑了一次 `find_J_path_sym`，需要判断超胞够不够大、第 N 近邻是否可信
- 排查 `find_J_path_sym` 给出的近邻距离与材料晶体结构不一致的原因

> 本文档不解决：
> - **拟合**交换参数（这是 Stage 3 完成 DFT 后的下游工作；属于用户和 VASP 的范畴）
> - 后续 `Spin_lattice_interaction` MC 寻找磁基态（见 `workflows/l2_spin_lattice_interaction.md`）
> - 自旋波色散（见 `workflows/l2_magnon.md`）
> - 字段逐项定义、默认值、单位、block 精确语法（这些转给 `skills/knowledge/reference/`）

---

## Pre-flight：路由与确认

在进入正式 stage 之前，主 agent 必须先确认下列三点。如果用户没有明确给出，必须**先问、再写**任何输入文件。

### Pre-flight 1：边界确认

| 问题 | 用户必须给出的明确答案 |
|---|---|
| 想把哪些磁性元素纳入相互作用分析？ | 例如 "Ni"、"Fe"、"Mn+Fe"。两个不同元素会直接对应 `isaAB = A B`，并在相关 pair / cluster 搜索中覆盖 A-A、A-B、B-B，不是只覆盖交叉 pair |
| 是各向同性（标量 J）还是矩阵形式（含 SOC、DM、Kitaev）？ | 决定下游 DFT 计算是 4 次 per pair 还是 9 × 4 = 36 次 per pair |
| 起始结构来源？ | (a) 已有 `cell.str` / `unit_cell.str`；(b) 只有 `POSCAR`；(c) 只有材料名 / 化学式（这种情况不接受，必须先要结构文件） |

### Pre-flight 2：结构文件路线

如果用户已有 `cell.str` / `unit_cell.str` → 直接进入 Stage 1。

如果用户只有 `POSCAR`：先查 `topics/structure_from_poscar.md` 决定 primitive 还原与轴向修正策略，再生成 `cell.str` / `unit_cell.str`，**不要**自动切换到 `READ_POSCAR T` / `READ_POSCAR_UC T` 路线，除非用户明确同意。

如果只有超胞 `POSCAR`、原胞信息缺失 → 不接受跳过原胞；按 `topics/structure_from_poscar.md` 推导 primitive 后再继续。

`find_J_path_sym` 对 `cell.str` 的原子顺序有额外硬约束：`%block AtomicCoordinatesAndAtomicSpecies` 必须按第四列 `species_id` 分组并保持非递减顺序，即所有 species 1 原子连续写完，再写 species 2，依次类推。不要在把 `unit_cell.str` 或 POSCAR 扩成 supercell-style `cell.str` 时按 tile / unit-cell copy 输出 `Ni I I Ni I I ...` 这类交错顺序；应先生成全部坐标，再按 species id 分组输出，同时保留每个原子的正确坐标、species id、元素符号，以及有效唯一的 atom index / 映射说明。这里的检查对象是第四列读入的全局 `isa`，不是第六列 atom index。

对多 species 的 `Model find_J_path_sym`，不要依赖 PASP 用非单位 `%block SuperCell` 从 primitive / 交错排序的 `cell.str` 自动扩胞，除非已经证明扩胞后的全局 `isa` 仍非递减。源码中的 `coor.F` 会按 cell copy 复制 `isa`，因此 primitive 顺序如 `1,2,2` 会扩成 `1,2,2,1,2,2...`，随后在 `find_J_path_sym` 入口触发 species-order stop。稳妥路线是直接把完整目标分析超胞写成 `cell.str`，按第四列 species id 分组，并在 `cell.str` 已经是目标超胞时让 `%block SuperCell` 保持单位阵。

### Pre-flight 3：subagent 授权与 L2 input-preflight 硬门禁

如果当前任务包含以下任一项，且当前 runtime 支持子 agent，按 `pasp-orchestrator` 的授权规则向用户征求授权：

- 跨多个 example 目录的对比检查
- 长 log（数千行）的解析摘要
- `template-compare` / `directory-inventory` / `output-validation`
- 正式 input 提升、覆盖正式 input、派生 `runs/<run-id>/`、创建 / 修改提交脚本或提交配置、提交任务前的 `input-preflight`

授权只允许 read-only fact collection；不确认物理参数、不允许写入 PASP / VASP 输入、不允许提升正式 input、不允许准备提交，也不授权提交任务。

对 `input-preflight`，L2 是硬门禁：在提升正式 `input/`、覆盖正式 input、派生 `runs/<run-id>/`、创建或编辑提交脚本 / 外部任务配置、提交 PASP 或 DFT 任务前，必须通过 `pasp-verifier` `mode: input-preflight` 的只读检查，并记录：

- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`

如果用户已授权但 verifier / subagent 不可用，流程 blocked。只有用户明确豁免 L2 hard gate 时，主 agent 才能按同一 checklist 本地检查；此时必须记录 `L2_PREFLIGHT_HARD_GATE_WAIVED=true`、`LOCAL_PREFLIGHT_DONE=true` 和本地检查证据。

---

## Stage 1：结构与建模准备

把用户提供的结构信息和建模意图，转写为完整的 `cell.str` + `unit_cell.str` + `PASP.input`（含所有必填字段）。

### 当前阶段输入文件

| 来源 | 文件 | 是否硬性必需 |
|---|---|---|
| 用户 / 上游 | `cell.str`（最终用于分析的晶胞或超胞） | 硬性必需 |
| 用户 / 上游 | `unit_cell.str`（最小原胞） | 硬性必需 |
| 模板 | `templates/l2_find_J_path_sym/PASP.input` | 起点骨架；用户可直接复制为 `PASP.input` 后逐字段填值 |
| 模板 | `templates/l2_find_J_path_sym/cell.str` 占位 | 仅含说明 comment，**不能直接跑**——用户必须替换为真实晶胞 |
| 模板 | `templates/l2_find_J_path_sym/unit_cell.str` 占位 | 仅含说明 comment，**不能直接跑**——用户必须替换为真实原胞 |

### 当前阶段已知输出

| 输出 | 角色 |
|---|---|
| 填好的 `cell.str` | 进入 Stage 2 的硬性输入 |
| 填好的 `unit_cell.str` | 进入 Stage 2 的硬性输入 |
| 填好的 `PASP.input` | 进入 Stage 2 的硬性输入；包含 `Model`、`SuperCell`、`Z_values`、`isaAB`、`Spin_values`、`magnetic_or_ligand`、`fig.maxk`、`fig.mdist` 全部字段 |

### 待运行验证的依赖

- 用户起始 `POSCAR` 是原胞还是超胞（如果用户没有显式说明，必须先确认）
- 用户希望的"分析超胞"具体规模——决定 `cell.str` 的最终尺寸
- pymatgen 自动 primitive 后是否需要轴向修正（参考 `topics/structure_from_poscar.md` §"自动 primitive 后的轴向修正规则"）

### 上游依赖

- 用户提供的结构信息（POSCAR / 已有 .str / 化学式 + 文献结构）
- 用户的物理建模意图（关心 Pre-flight 1 的三个问题的答案）

### 下游去向

- Stage 2 直接消费本阶段三份文件，提交 PASP 计算

### 本阶段使用的脚本

| 何时 | 脚本 |
|---|---|
| 只有 `POSCAR` 且不确定是否原胞 | `pymatgen` primitive reduction（见 `topics/structure_from_poscar.md`） |
| primitive 还原后需要轴向核对 | `pymatgen` `SpacegroupAnalyzer` 等价原子分组检查 |
| 没有现成 `.str` 转写工具 | `ase.io.read` + 手写 `LatticeVectors` / `AtomicCoordinatesAndAtomicSpecies` block |

PASP **不**附带 POSCAR → cell.str 的官方转写脚本；这是用户侧的责任。

### 当前阶段可调整项

- `cell.str` 中的 `LatticeVectors` 与原子排布（决定分析超胞大小）
- `%block SuperCell` 矩阵（在 `cell.str` 基础上是否进一步扩胞）
- `%block Z_values`（元素顺序）
- `%block isaAB`（要纳入相互作用搜索的活动磁性元素集合）
- `%block Spin_values`（自旋尺度，每元素一项）
- `%block magnetic_or_ligand`（角色：磁性 / 配位 / 其他）
- `fig.maxk`（最高考虑几体）
- `%block fig.mdist`（每体数对应的截断距离，单位 **Bohr**）

### 这些项控制什么

- `cell.str` + `SuperCell`：确定真正用于对称性分析的超胞规模——直接影响远近邻识别能力
- `Z_values`：建立"元素编号 ↔ 化学元素"的内部映射；后续 `isaAB` / `Spin_values` / `magnetic_or_ligand` 全部按这个编号解释
- `isaAB`：限定本次分析关注的活动磁性元素集合；`1 2` 在相关 pair / cluster 搜索中表示 species 1 和 species 2 均参与，通常会覆盖 1-1、1-2、2-2 相互作用
- `Spin_values`：自旋尺度；非磁性元素必须显式写 0
- `magnetic_or_ligand`：在 PASP 内部区分磁性 / 配位 / 旁观角色，影响哪些原子被纳入 pair 搜索
- `fig.maxk` + `fig.mdist`：相互作用的体数与每体的距离截断；体数越高、截断越大，pair 数量增长越快

### 任务目标 → 推荐调整方向

| 目标 | 调整方向 |
|---|---|
| 只要前几近邻的二体 pair | `fig.maxk = 2`，`fig.mdist` 给一个比目标 N 近邻略大的值 |
| 想稳健覆盖 5+ 近邻 | 先把 `cell.str` 加大到能容纳 `fig.mdist`，再设 `fig.maxk = 2` |
| 需要三体或四体 cluster | `fig.maxk = 3` 或 `4`，并在 `fig.mdist` 中追加对应体数的截断；项数会显著增加 |
| 第一次试跑、求快 | 用较小 `cell.str` + 较小 `fig.mdist`，跑通流程后再放大复跑 |

### 什么时候必须先查 reference

任何**写入 / 覆盖 / 转换**下列内容时，先查对应 reference 卡（`reference-before-write` 硬性约束）：

| 写哪里 | 先查 |
|---|---|
| `cell.str` | `files/cell.str.md` |
| `unit_cell.str` | `files/unit_cell.str.md` |
| `PASP.input` 的整体结构 | `topics/PASP.input.md` |
| `Model` 行 | `params/Model.md` |
| `%block SuperCell` | `params/SuperCell.md` |
| `%block Z_values` | `params/Z_values.md` |
| `%block isaAB` | `params/isaAB.md` |
| `%block Spin_values` | `params/Spin_values.md` |
| `%block magnetic_or_ligand` | `params/magnetic_or_ligand.md` |
| `fig.maxk` | `params/fig.maxk.md` |
| `%block fig.mdist` | `params/fig.mdist.md` |
| 从 POSCAR 推导原胞 / 修正轴向 | `topics/structure_from_poscar.md` |

不允许凭模板、example、记忆直接写入。

### 修改后要检查什么

- `cell.str` 的 `number_of_species` = `Z_values` 项数 = `Spin_values` 项数 = `magnetic_or_ligand` 项数
- `cell.str` 的 `%block AtomicCoordinatesAndAtomicSpecies` 按 species id 分组且第四列非递减；任何 `1,2,2,1,2,2...` 或 `Ni I I Ni I I...` 这类 interleaved supercell 输出必须在运行前重排，否则 `find_J_path_sym` 会停止并报 `find_J_path_sym: species are not ordered!`
- `cell.str` 中元素**首次出现顺序** = `Z_values` 顺序（前后不一致会让 `isaAB` 选错对象）
- `isaAB` 两个值都在 `[1, number_of_species]` 内，且对应到用户想纳入活动磁性集合的元素；多磁性元素不要用 `0 0` 冒充“所有磁对”
- 非磁性元素在 `Spin_values` 中显式写 `0`（不是省略）
- `magnetic_or_ligand` 中磁性原子写 `1`，配位原子写 `2`，其他写 `0`
- `fig.mdist` 第一位为 `1`（占位，无物理含义），第二位起为各体数的截断（**单位 Bohr**，1 Bohr ≈ 0.529 Å）
- `fig.mdist` 第二位（二体截断）应小于 `cell.str` 在最短方向上的最大原子间距，否则 PASP 会报错或给出不可信结果
- 对多 species 的 `find_J_path_sym`，如果 `cell.str` 仍是 primitive 或按 unit-cell copy 排列的结构，不要用非单位 `%block SuperCell` 让 PASP 自动扩成目标分析超胞，除非已证明扩胞后的 `isa` 全局非递减。优先直接写完整目标超胞版 `cell.str`，按第四列 species id 分组；此时 `%block SuperCell` 通常保持单位阵。
- 如果 `cell.str` 已经是大超胞，`%block SuperCell` 通常应保持单位阵；不要在已扩胞的 `cell.str` 之上再用非单位阵 SuperCell 重复扩胞

### 服务器实跑后应补录的信息

记录到 `l2_find_J_path_sym_run_notes.md`：

- 用户实际选定的 primitive cell vs 起始 POSCAR 的关系
- 用户实际选定的分析超胞 `cell.str` 尺寸
- 是否需要 `%block SuperCell` 进一步扩胞
- 用户的元素 / `isaAB` / `Spin_values` 选择是否一次填对，或经历过哪些修正

---

## Stage 2：运行 find_J_path_sym + 超胞收敛检查

把 Stage 1 的输入包提交给 PASP，得到 pair 列表与 DFT 输入素材；然后通过近邻距离与超胞规模对照判断结果是否可信。

### Stage 2 pre-submit input-preflight gate

在把 Stage 1 候选输入包提升为正式 `input/`、覆盖既有正式 input、派生 `runs/<run-id>/`、创建或编辑 `run.sh` / 外部任务配置、或提交 PASP 前，必须先运行 `pasp-verifier` `mode: input-preflight` 的 read-only subagent 检查。

给 verifier 的边界必须命名本 workflow 和目标 stage、候选 `cell.str` / `unit_cell.str` / `PASP.input`、用户对 `isaAB` / 标量或矩阵 J / 结构路线的确认、以及 Stage 1 reference-before-write 清单。verifier 只返回 pass / fail / blocked 与证据路径；它不能选择 `Spin_values`、`fig.mdist`、Sc POTCAR 策略，不能修改文件，不能创建 run 目录或提交任务。

Stage 2 preflight 必须逐行读取候选 `cell.str` 的 `%block AtomicCoordinatesAndAtomicSpecies`，确认第四列 species id 按非递减顺序排列并按 species 分组。若看到 tile-by-tile 或 unit-cell-copy 顺序导致 species 交错，例如 `1,2,2,1,2,2...`，结论必须是 fail / blocked，要求先重排为 species 1 全部原子、species 2 全部原子……后再运行 PASP。

如果候选 `PASP.input` 对多 species `find_J_path_sym` 使用非单位 `%block SuperCell`，preflight 还必须判断 `cell.str` 是否已经是完整目标分析超胞。若它仍是 primitive / unit-cell-copy 顺序，且无法证明 PASP 自动扩胞后的全局 `isa` 仍非递减，结论必须是 blocked：先生成完整目标超胞 `cell.str`、按 species id 分组，并把 `%block SuperCell` 改回单位阵或等价的不再扩胞设置。

只有同时满足以下记录，才允许正式 input / run / submission 动作：

- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`

如果用户已授权但 verifier / subagent 不可用，Stage 2 blocked；除非用户明确豁免 L2 hard gate，主 agent 不得用本地检查替代。被豁免时，主 agent 必须按同一 checklist 本地检查，并记录 `L2_PREFLIGHT_HARD_GATE_WAIVED=true`、`LOCAL_PREFLIGHT_DONE=true` 和本地证据。

### 当前阶段输入文件

| 来源 | 文件 | 角色 |
|---|---|---|
| Stage 1 | `cell.str`、`unit_cell.str`、`PASP.input` | 完整输入包 |
| 环境 | 提交脚本（如 `run.sh`） | 仅环境助手；不是 PASP 输入。`pasp_examples/Lecture-2/find_J_path_sym/inputs/` 不附带 `run.sh`，可参考 `Spin_lattice_interaction/inputs/run.sh` 写法 |
| 用户 | `seed.in`（可选） | 固定随机种子；`find_J_path_sym` 通常不需要随机性，可不提供 |

### 当前阶段已知输出

由 PASP 源码 `Latticemodel/src/J_path_sym.f90` 静态确认的输出：

| 输出 | 数量 | 角色 |
|---|---|---|
| `log.out` | 1 | PASP 标准输出；包含 pair 列表、近邻距离、`#@upup` / `#@updn` / `#@dnup` / `#@dndn` MAGMOM 行、`#@DM_*` M_CONSTR 行 |
| `PASP.used_info` | 1 | 实际生效的输入参数；用于核对 `Z_values` 等是否被默认值覆盖 |
| `J.POS` | 1 | 与输入 cell 对应的 POSCAR；详见 `files/J.POS.md` |
| `pair_POS.NNN` | 每个不等价 pair 1 份 | 把 pair 中两个原子打成 `Z+25` 和 `Z+35` 的可视化 POSCAR；不直接给 VASP 用 |
| `atat.NNN_Y` | 仅对 PASP 内部判定为 `SE_xc=3` 或 `SE_xc=4` 的 pair 写 4 份（Y=1..4）；`SE_xc=1` 或 `SE_xc=2` 的 pair 不写 atat。npair 与 atat 数量的关系 **不是** 简单的 4:1（NiI₂ 5×5 实测 npair=31，但只 7 对 pair 写 atat = 28 个文件） | 可选 / advanced 的占位元素 POSCAR 族，含 Sc placeholder 与 POTCAR 风险；普通用户默认不要把它当作 VASP POSCAR |
| `seed_used.in` | 1 | 实际使用的随机种子；`find_J_path_sym` 内基本无随机性影响，仅记录 |

### 待运行验证的依赖

- 不同 PASP 编译版本下 `pair_POS.NNN` / `atat.NNN_Y` 文件名约定是否一致——目前根据源码 `WRITE(fname,'(a,I3.3,a,I1)')` 静态确认为 3 位零填充 NNN + 单位整数 Y
- 体系是金属性 / 巡游磁性时，`magnetic_or_ligand` 的"磁性 / 配位"二分是否还合理（这属于建模选择层面，不属于流程问题）
- 大型体系（几千原子）下 PASP 的内存与运行时长——目前没有归档基准数据

### 上游依赖

Stage 1 的完整输入包；**特别**依赖：

- `cell.str` 的尺寸足够大，能容纳 `fig.mdist` 中给定的最大截断距离
- `cell.str` 的原子坐标块已按 species id 分组且非递减；PASP 源码 `Latticemodel/src/J_path_sym.f90` 会在 `find_J_path_sym` 开始时检查该条件，失败时停止并报 `find_J_path_sym: species are not ordered!`
- 多 species 输入没有依赖 PASP 从 primitive / interleaved `cell.str` 通过非单位 `%block SuperCell` 自动扩胞，除非已证明扩胞后的全局 `isa` 仍非递减；安全输入是完整目标超胞版 `cell.str` + species 分组 + identity `SuperCell`
- `Z_values` 顺序与 `cell.str` 元素首次出现顺序一致
- `Spin_values` / `magnetic_or_ligand` 项数等于 `number_of_species`

### 下游去向

- 默认 handoff：`J.POS` 作为四态 DFT 的结构 POSCAR，`log.out` 中的 `MAGMOM` / `M_CONSTR` 块作为四个磁态约束 → Stage 3 的 DFT 输入交接
- 可选 advanced handoff：只有用户明确接受 Sc placeholder / POTCAR 处理策略时，才考虑 `atat.NNN_Y` POSCAR 族
- `log.out` 中近邻距离表 → 用户进行物理判断（哪些是有效近邻、哪些是超胞效应假象）

### 本阶段使用的脚本

| 何时 | 脚本 |
|---|---|
| HPC 提交 | 用户根据集群环境写的 `run.sh`（PASP 不提供） |
| 隔离运行目录 | 推荐：`mkdir -p runs/<run-id>/` 后把 Stage 1 输入包 `cp -r` 进去再跑（参考 `.trellis/spec/guides/workflow-skill-design-guide.md` §6 "stage 输入包 vs 隔离运行目录") |
| 多次扩胞试跑 | 没有 PASP 内置脚本；用户复制不同尺寸的 `cell.str_*` 到同一 `runs/<run-id>/` 重新跑 |

`pasp_examples/Lecture-2/find_J_path_sym/inputs/` 同时提供了 `cell.str_NiI2_5x5` 和 `cell.str_NiI2_6x6` 两份不同规模的 `cell.str` 以便对比；这是 example 写法约定，不是 PASP 自动产物。

### 当前阶段可调整项

- 是否在 `runs/<run-id>/` 中跑，还是就地在 stage `input/` 跑（默认推荐前者）
- 提交脚本的 `--ntasks-per-node` / `--nodes` 等环境参数
- 出现报错或可疑结果时，回到 Stage 1 调 `cell.str` / `fig.mdist` 后重跑

### 这些项控制什么

- 隔离运行目录：保护 stage `input/` 不被运行时输出污染、覆盖；多次试跑时也便于对比
- 资源参数：决定运行时长与排队等待
- `cell.str` / `fig.mdist`：直接决定 PASP 是否能正确识别远近邻

### 任务目标 → 推荐调整方向

| 症状 / 目标 | 优先调整方向 |
|---|---|
| PASP 报"截断距离超出超胞最大原子间距" | 先减小 `fig.mdist` 第二位；如果近邻 N 因此被截断，再去 Stage 1 增大 `cell.str` |
| 前几近邻距离合理，第 N 突然不对 | 典型超胞过小症状；增大 `cell.str` 后重跑（参考 NiI₂ example：5×5 时第 5 近邻为 8.000 Å 错误，6×6 时为 12.000 Å 正确） |
| 想确认结果稳定 | 选两种不同 supercell 大小分别跑；如果壳层距离一致则稳定 |
| 想加速 | 先用小 `cell.str` + 小 `fig.mdist` 跑通流程，再用大 supercell 跑生产结果 |

### 什么时候必须先查 reference

| 改哪里 | 先查 |
|---|---|
| `cell.str` 尺寸或 `%block SuperCell` 矩阵 | `params/SuperCell.md` + `files/cell.str.md` |
| `fig.mdist` | `params/fig.mdist.md` |
| 解读 `log.out` 中 MAGMOM / M_CONSTR 注释行的语义 | `topics/four_state_method.md` + `files/atat.NNN_Y.md` |
| 出现意外的输出文件名 | 直接确认当前 run 的 PASP 版本和实际文件清单；先按当前目录事实标记为待运行验证差异并记录到 run notes。只有在开发 / 修订 skills 时才通过 `pasp-verifier` `mode: source-audit` 做源码审计，runtime agent 不要求用户或自己读取 PASP source |

### 修改后要检查什么

- `log.out` 的 pair 列表数量与材料对称性的预期是否一致（例如 D3d 群 NiI₂ 在前 5 近邻范围内有约 5 个不等价 pair）
- 各近邻 pair 的 `pair_dist` 是否与简单结构计算（晶格参数 × 几何系数）一致
- `J.POS` 的原子总数 = `cell.str` 的 `NumberOfAtoms` × `det(SuperCell)`；默认 DFT handoff 使用它作为 POSCAR
- 如果用户明确走 advanced `atat.NNN_Y` 路线，再检查每个 pair 的 4 份 `atat.NNN_Y`：Y=1 内容应与 `J.POS` 完全一致；Y=2 / Y=3 应有 1 个 Sc 占位；Y=4 应有 2 个 Sc 占位
- `pair_POS.NNN` 中 pair 原子的元素标记是否符合 `Z+25` / `Z+35` 规则（仅做合理性检查；该文件不直接进 VASP）
- 如果同一 pair 在两种不同 supercell 下给出明显不同的近邻分组 → 还没有收敛，需要更大 supercell

### 服务器实跑后应补录的信息

记录到 `l2_find_J_path_sym_run_notes.md`：

- 用户实际跑通的 supercell 大小、PASP 报告的不等价 pair 数、log.out 中的近邻距离表
- 是否经历过"超胞过小→重跑"循环；具体是从哪一近邻开始失真
- 当前 PASP 版本下输出文件名是否与本文档描述一致；任何与源码 `J_path_sym.f90` 描述不符的地方
- 实际运行时长与资源消耗（用于后续估算）

---

## Stage 3：四态 DFT 输入交接

把 Stage 2 输出的 `J.POS` 与 `log.out` 中的 MAGMOM / M_CONSTR 块，组织成完整 VASP 输入包，交付给用户的 DFT 流水线。默认不要把 `atat.NNN_Y` 当作普通用户的 POSCAR；它是含 Sc placeholder 的 advanced / internal 路线，只有用户确认 Sc 与 POTCAR 策略时才使用。

> 这一阶段的产出**不是** PASP 输入，而是一份"DFT 计算清单 + 每对 pair 每状态的 VASP 输入目录蓝图"。具体的 VASP 计算是用户和 DFT 系统的事情。

### 当前阶段输入文件

| 来源 | 文件 | 角色 |
|---|---|---|
| Stage 2 | `J.POS` | 结构基准 |
| Stage 2 | `atat.NNN_Y`（NNN = pair index, Y = 1..4） | 可选 advanced POSCAR 族；含 Sc placeholder，默认不作为普通 handoff |
| Stage 2 | `log.out` 中 `#@upup` / `#@updn` / `#@dnup` / `#@dndn` 行 | 每 pair 4 行 MAGMOM（共线情形） |
| Stage 2 | `log.out` 中 `#@DM_up_up` / `#@DM_up_dn` / `#@DM_dn_up` / `#@DM_dn_dn` 行 | 每 pair 4 行 M_CONSTR（矩阵 J / SOC 情形） |
| 用户 | `INCAR` 模板 | 用户提供或逐项确认的基础 INCAR；PASP 输出只负责注入 MAGMOM / M_CONSTR |
| 用户 | `KPOINTS` | 用户根据收敛性决定；agent 不能替用户发明生产 k-mesh |
| 用户 | `POTCAR` | 用户提供或确认；默认 `J.POS` 路线不需要 Sc，占位 Sc 只属于 advanced `atat.NNN_Y` 路线 |

### 当前阶段已知输出

每个不等价 pair 4 个 VASP 计算目录，组织约定为：

```text
runs/<dft-run-id>/
├── pair_001/
│   ├── upup/         (POSCAR=J.POS, INCAR with #@upup MAGMOM or #@DM_up_up M_CONSTR, confirmed KPOINTS/POTCAR)
│   ├── updn/         (POSCAR=J.POS, INCAR with #@updn MAGMOM or #@DM_up_dn M_CONSTR, ...)
│   ├── dnup/
│   └── dndn/
├── pair_002/
│   ├── upup/
│   ...
```

或更紧凑的 `pair_001_upup/` 平铺命名——具体由用户的提交系统决定。

### 待运行验证的依赖

- 用户体系是否真的需要矩阵 J / SOC（决定 4 次 vs 36 次 per pair）
- VASP 编译版本对 `LSORBIT = T` 的支持
- 若用户选择 advanced `atat.NNN_Y` 路线，POTCAR 中 Sc 是否使用磁性元素的赝势拷贝；不同体系可能需要不同处理

### 上游依赖

- Stage 2 完整输出
- 用户已确认本次目标是标量 J 还是矩阵 J（Pre-flight 1 的第二个问题）

### 下游去向

- 用户的 VASP 计算流水线（4 × n_pairs 或 36 × n_pairs 个 DFT 计算）
- 后续从 4 个状态能量按 `topics/four_state_method.md` 的线性组合公式拟合 J（如果继续到 `Spin_lattice_interaction` 工作流，得到的 J 矩阵会汇总为 `spin_exchange.dat`，参见 `workflows/l2_spin_lattice_interaction.md`）
- 如果继续到 L3/L5 `atomic_effective_H` pure-spin local-mode 路线，四态法 J 需要先按 `topics/four_state_method.md` 换算到目标 `Spin_values` / normalized spin basis，再按 `files/J_best.dat.md` 写成 fitted-parameter handoff；不能把物理自旋尺度下的原始 J 直接交给 L5 dynamics

### 本阶段使用的脚本

PASP **不**附带这部分脚本。用户侧的工作量包括：

| 工作 | 工具 |
|---|---|
| 把 `log.out` 中带 `#@` 注释的 MAGMOM / M_CONSTR 行抽取出来并按 pair / Y 分发 | 用户 grep 或 awk 脚本 |
| 默认：把 `J.POS` 复制为 4 个状态的 POSCAR，并把对应 `MAGMOM` / `M_CONSTR` 行追加到用户确认的 INCAR | 用户 grep / awk / organizer 脚本 |
| 可选 advanced：把 4 个 `atat.NNN_Y` 与对应 INCAR 拼成 4 个 VASP 工作目录 | 仅在用户确认 Sc placeholder / POTCAR 策略后使用 |
| 4 状态能量 → J 拟合 | 用户写的 J 拟合脚本（能量抽取见 `files/OUTCAR.md`，线性组合和归一化换算见 `topics/four_state_method.md`） |
| 把若干 pair 的 J 汇总为 `spin_exchange.dat` | Stage 4（即 `Spin_lattice_interaction` 工作流的输入准备） |
| 把若干 pair 的 J 映射为 `J_best.dat` | L3/L5 bridge；必须有同一 `local_mode_PM.dat` / interaction list 的 parameter id、最终 `TOTEN` 能量证据、J 归一化换算记录和 `J_best.dat` 格式检查 |

注意：本仓库 `skills/knowledge/scripts/l3_effective_hamiltonian/` 下的脚本面向 L3 effective Hamiltonian fitting，不能直接复用到 `find_J_path_sym` 的四态 DFT 整理。

### 当前阶段可调整项

- 是否做矩阵 J（含 SOC）：决定使用 MAGMOM 还是 M_CONSTR、4 次还是 36 次计算
- 是否使用默认 `J.POS` handoff，还是用户明确选择 advanced `atat.NNN_Y` / Sc placeholder handoff
- 4 个状态使用的 KPOINTS 与收敛参数（应由用户确认，并在四态间保持一致以便差分）

### 这些项控制什么

- 标量 vs 矩阵 J：决定是否能描述各向异性、DM、Kitaev；决定计算量
- advanced `atat.NNN_Y` 路线的 Sc POTCAR 选择：直接影响 pair 原子的电子结构；用磁性元素拷贝可以保证 pair 原子物理一致，用真实 Sc 会引入电子数 / 价态错误。默认 `J.POS` 路线避免这个 placeholder 风险
- KPOINTS 一致性：4 个状态间的能量必须可线性组合；不同 KPOINTS 会引入数值噪声

### 任务目标 → 推荐调整方向

| 目标 | 调整方向 |
|---|---|
| 各向同性 Heisenberg J | 标量 J 路径，4 计算 per pair；MAGMOM 即足够 |
| 含 DM、Kitaev、各向异性 | 矩阵 J 路径，9 × 4 = 36 计算 per pair；必须 `LSORBIT = T` 与 M_CONSTR |
| 想先快速确认 J 量级 | 标量 J + 较粗 KPOINTS 跑一次代表 pair；不要把它当作生产结果 |
| 后续要用于 `Spin_lattice_interaction` 拟合 | 直接走矩阵 J，因为 `Spin_lattice_interaction` 默认 `spin_lat.general_J = T`（即矩阵形式） |

### 什么时候必须先查 reference

| 写哪里 | 先查 |
|---|---|
| INCAR 中 MAGMOM / M_CONSTR 行 | `topics/four_state_method.md`；只能追加到用户确认的基础 INCAR |
| 处理 atat.NNN_Y 文件结构 | `files/atat.NNN_Y.md` |
| 验证 J.POS 与 atat.NNN_Y 的关系 | `files/J.POS.md` |
| 拼装 POTCAR 顺序 | `files/atat.NNN_Y.md` "注意事项" 段 + VASP 官方文档 |
| 写 `spin_exchange.dat` 把 J 矩阵汇总 | `files/spin_exchange.dat.md` |
| 从 VASP `OUTCAR` 提取四态能量 | `files/OUTCAR.md` |
| 写 `J_best.dat` 交给 `atomic_effective_H` | `files/J_best.dat.md` + `topics/four_state_method.md` |
| 解读 `log.out` 中的 `#@` 注释行 | `topics/four_state_method.md` |

### 修改后要检查什么

- 默认 `J.POS` 路线：4 个状态都使用同一份 `J.POS` 结构，只有 INCAR 中追加的 `MAGMOM` / `M_CONSTR` 行随状态变化
- 基础 `INCAR`、`KPOINTS`、`POTCAR` 已由用户提供或确认；所有 4 个状态的 KPOINTS、ENCUT、ISMEAR、SIGMA、IBRION、NSW 等均一致
- 矩阵 J 情形：NCL / SOC 相关 INCAR 设置必须由用户确认，agent 只追加 PASP 生成的 `M_CONSTR`
- advanced `atat.NNN_Y` 路线：POTCAR 元素顺序与 `atat.NNN_Y` 第 1 行严格一致（包括占位 Sc 的位置），且 INCAR 中 MAGMOM / M_CONSTR 的原子总数 = `atat.NNN_Y` 中所有元素的原子计数之和
- 用 `topics/four_state_method.md` 的线性组合公式核对：`J = (E_↑↑ + E_↓↓ - E_↑↓ - E_↓↑) / (4 S²)` 数值是否合理（先看符号；铁磁基态下 J 应为负）
- 每个 VASP 状态的能量来自最后一条 `free energy TOTEN`，并有收敛 / 正常结束证据；脚本不得读第一条 `TOTEN`
- 若输出给 `J_best.dat`，确认 J 已按目标模型自旋尺度换算，例如物理 `S=5/2` 到 `Spin_values=2` 的 normalized spin 模型需要乘以 6.25，并且 `J_best.dat` 每个 retained row 为 `<parameter_id> <value>`、无数据行注释、无无意义零值 retained row

### 服务器实跑后应补录的信息

记录到 `l2_find_J_path_sym_run_notes.md`：

- 实际选定的 POTCAR 策略（Sc 用磁性元素拷贝 / 真实 Sc 赝势 / 其他）
- 4 状态能量与拟合 J 的具体数值，以及与文献值的对比（已知材料如 NiI₂ / CrI₃ 等）
- VASP 端遇到的常见报错（如 NELM 不收敛、磁矩漂移）及解决办法
- 单次 pair 的 4 状态计算总耗时；用于后续估计

---

## 常见坑

### 坑 1：`Z_values` 顺序与 `cell.str` 元素首次出现顺序错位

症状：PASP 跑通，但 `isaAB` 选错了元素。
预防：写 `cell.str` 时严格按"先磁性元素、再配位元素"或与 reference 例子一致的顺序；写完后核对 `Z_values` 第一项 = `cell.str` 中第一种元素。

### 坑 2：`cell.str` 太小，第 N 近邻假性失真

症状：前 N-1 近邻距离正确，第 N 突然不合理。
预防：第一次跑用一种 supercell，加大一档再跑一次，对比；不一致就再放大。

### 坑 3：`fig.mdist` 单位混淆

`fig.mdist` 是 **Bohr**，不是 Å。
预防：算好你需要的 N 近邻最大距离（Å），再乘以 1/0.529 得到 Bohr 值，**再加一些余量**。

### 坑 4：把 Sc 真实赝势用作占位

PASP 用 Sc 只是元素标记；如果 POTCAR 用了真实 Sc，pair 原子的化学环境会被严重污染。
预防：普通 handoff 默认使用 `J.POS` + `log.out` 的 `MAGMOM` / `M_CONSTR`，避免引入 Sc placeholder；只有用户明确选择 advanced `atat.NNN_Y` 路线时，才讨论 Sc POTCAR，并要求用户确认是复制磁性元素 POTCAR、真实 Sc POTCAR 还是其他策略。

### 坑 5：把 `pair_POS.NNN` 误传给 VASP

`pair_POS.NNN` 是可视化文件，元素被打上 `Z+25` / `Z+35`，VASP 读了会找不到对应 POTCAR。
预防：VASP 端默认用 `J.POS` 作为结构 POSCAR，并从 `log.out` 追加对应状态的 `MAGMOM` / `M_CONSTR`；`pair_POS.NNN` 只用 VESTA 看。`atat.NNN_Y` 只在用户确认 advanced Sc-placeholder 路线时使用。

### 坑 6：在 stage `input/` 中跑导致输出污染

PASP 会在当前目录写大量 `pair_POS.NNN` / `atat.NNN_Y`，覆盖或夹杂在 stage `input/` 里。
预防：先完成 Stage 2 `pasp-verifier` `mode: input-preflight`，记录 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true` 和 `STAGE_PREFLIGHT_PASS=true`，再 `cp -r input/ runs/<run-id>/` 并进入 `runs/<run-id>/` 跑。

### 坑 7：把 `Spin_values` 中非磁性元素省略

`Spin_values` 必须有 `number_of_species` 项；漏掉一项会让 PASP 把后续 block 行当数值读，触发 Fortran list-directed I/O 错误。
预防：每个非磁性元素显式写 `0`。

### 坑 7a：误解 `isaAB = 1 2`

`isaAB = 1 2` 表示 species 1 和 species 2 都属于活动磁性集合；在多磁性元素体系中，它通常覆盖 1-1、1-2、2-2 相互作用，而不是只分析交叉 pair。`0 0` 是默认行为，不是“明确分析所有磁对”的安全写法。

### 坑 7b：四态能量 / J bridge 没有记录最终 `TOTEN` 和自旋归一化

从 `OUTCAR` 读第一条 `TOTEN` 会得到未收敛能量；把物理 `S` 下的四态 J 直接写入 normalized spin 的 `J_best.dat` 会把温标和动力学能量尺度弄错。
预防：每个状态取最后一条 converged `free energy TOTEN`，记录四态公式、单位、物理 `S`、目标 `S_model` 和换算因子，再写 `J_best.dat`。

### 坑 8：扩超胞时按 unit-cell copy 交错输出 `cell.str`

症状：PASP 启动后立即停止并报 `find_J_path_sym: species are not ordered!`。
原因：`find_J_path_sym` 要求 `cell.str` 的 `%block AtomicCoordinatesAndAtomicSpecies` 第四列 species id 非递减；如果从 `unit_cell.str` 扩成超胞时逐个 tile 输出 `Ni I I Ni I I ...`，species 顺序会从 2 回到 1，触发源码检查。同样，对多 species 输入，PASP 的非单位 `%block SuperCell` 自动扩胞也会在 `coor.F` 中按 cell copy 复制 `isa`，primitive 顺序 `1,2,2` 会变成 `1,2,2,1,2,2...`。
预防：扩胞时先保留所有原子坐标和 species 信息，再按 species id 分组写出完整目标超胞版 `cell.str`：所有 species 1 原子、所有 species 2 原子、依次类推。第六列 atom index 虽不被 PASP 读取，但应保持有效唯一并与输出顺序或映射说明一致；当 `cell.str` 已经是目标超胞时，`%block SuperCell` 保持单位阵或等价不扩胞设置。

---

## Reference index for this workflow

按使用频率：

- **Files**: `cell.str` / `unit_cell.str` / `J.POS` / `atat.NNN_Y` / `OUTCAR` / `J_best.dat` / `PASP.used_info` / `seed.in`
- **Params**: `Model` / `SuperCell` / `Z_values` / `isaAB` / `Spin_values` / `magnetic_or_ligand` / `fig.maxk` / `fig.mdist`
- **Topics**: `PASP.input` / `four_state_method` / `structure_from_poscar` / `symmetry_representative_sites`（如需对称性代表位点辅助）

完整路径：均在 `skills/knowledge/reference/` 下。

---

## 不负责回答的内容

下列问题不在本 workflow 内回答，请转给对应位置：

| 问题类型 | 转给 |
|---|---|
| 字段精确语法 / 默认值 / 单位 / 取值范围 | 对应 reference 卡 |
| 后续 MC 寻找磁基态 | `workflows/l2_spin_lattice_interaction.md` |
| 自旋波色散 | `workflows/l2_magnon.md` |
| L3 effective Hamiltonian fitting（一般有效哈密顿量、含畸变 / 应变 / 声子） | `workflows/l3_effective_hamiltonian.md` |
| 用户特定 HPC 环境的 `run.sh` 写法 | 用户自行决定 |
| VASP INCAR 通用参数 / SCF 收敛技巧 | VASP 官方文档 |
| 不等价 pair 的对称性代表位点（用于 `Invariant` 等其他模型） | `topics/symmetry_representative_sites.md` |

---

## 历史观察

具体跑过哪些例子、什么 supercell 收敛、哪些 J 值与文献对比 → 见 sibling `l2_find_J_path_sym_run_notes.md`。

run notes 是历史观察记录，**不是当前用户工作区的事实**。当前用户的真实状态必须以用户实际目录中的文件为准。
