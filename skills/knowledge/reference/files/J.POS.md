# J.POS

## 文件作用

`Model find_J_path_sym` 输出的 POSCAR，作为后续四态法 DFT 计算的统一结构基准。

文件内容是**输入 cell（即 PASP.input 中 `%include cell.str` 提供的、再经 `%block SuperCell` 扩胞后的最终晶胞）**直接转写为 VASP POSCAR 格式（Direct 分数坐标）。元素符号与原子顺序与 `Z_values` 中给出的元素一致，原子坐标顺序与 PASP 内部统一后的顺序一致（与 `cell.str` 中第一次出现的元素顺序对应）。

它**不**包含任何 pair 标记、Sc 占位元素或磁性元数据。pair 信息由配套的 `pair_POS.NNN` 与 `atat.NNN_Y` 文件携带。

---

## 何时产出

- 仅由 `Model find_J_path_sym` 产出
- 在每次正常退出的 `find_J_path_sym` 运行结束时写入工作目录
- 文件名固定为 `J.POS`

---

## 何时使用

- 作为四态法 DFT 计算的默认结构 POSCAR：普通 handoff 使用同一份 `J.POS` 配合 `log.out` 中每个 pair / 状态的 `MAGMOM` 或 `M_CONSTR` 行；所有状态的几何结构保持一致
- 作为 advanced `atat.NNN_Y` 路线的结构基准：`atat.NNN_Y` 的晶格、原子总数和几何坐标来自 `J.POS`，但其中部分 pair 原子会改成 Sc placeholder 并改变元素分组
- 当 `atat.NNN_Y` 文件因为占位 Sc 让 VASP 端文件管理变复杂时，可以以 `J.POS` 为参考确认正确的原子总数和坐标顺序
- 当用户后续要把不同 `i, j` pair 的四态结果汇总回 PASP 时，可以用 `J.POS` 验证 `Spin_values` / `Z_values` / `cell.str` 的一致性

---

## 关键字段 / 结构

POSCAR 标准格式：

```text
<species_symbols>           # 第 1 行：元素符号，按 Z_values 顺序
<scale_factor>              # 第 2 行：统一比例因子（PASP 总是写 1.0）
<a1_x> <a1_y> <a1_z>        # 第 3-5 行：3×3 晶格矢量（单位 Å）
<a2_x> <a2_y> <a2_z>
<a3_x> <a3_y> <a3_z>
<NITYP_1> <NITYP_2> ...     # 第 6 行：每个元素的原子数
Direct                      # 第 7 行：坐标格式（PASP 总是写 Direct = 分数坐标）
<x_1> <y_1> <z_1>           # 第 8 行起：每个原子的分数坐标，按元素分组连续排列
...
```

所有 `atat.NNN_Y` 在前 5 行（元素符号、比例、晶格矢量）与 `J.POS` 完全一致，区别仅在第 1 行的元素符号集合、第 6 行的原子数计数、以及个别原子的位置（具体规则见 `files/atat.NNN_Y.md`）。

---

## 注意事项

- `J.POS` 是 **Direct（分数）坐标**，不是 Cartesian。如果需要 Cartesian 坐标，需要做坐标变换或重新让 VASP / pymatgen 转换
- `J.POS` 的晶格 = `cell.str × SuperCell`，不等于 `cell.str` 本身。如果 `%block SuperCell` 不是单位阵，`J.POS` 会比 `cell.str` 更大；`pair_POS.NNN` 与 `atat.NNN_Y` 的晶格也会跟着是这个扩胞后的尺寸
- `Z_values` 中的元素顺序如果与 `cell.str` 中元素首次出现顺序不一致，会被 PASP 内部统一；最终 `J.POS` 中元素的顺序以这个统一后的顺序为准
- 如果上一次运行残留了旧的 `J.POS`，新运行会**覆盖**它；多次运行不会自动归档
- 默认 `J.POS` 路线中，POTCAR 的元素顺序必须与 `J.POS` 第 1 行一致；不一致会导致 VASP 报错或赝势错配
- 不要把 `J.POS` 当成完整 VASP 输入：它只提供 POSCAR，`INCAR` / `KPOINTS` / `POTCAR` 必须由用户提供或确认，`MAGMOM` / `M_CONSTR` 从 `log.out` 对应状态追加
- `atat.NNN_Y` 是可选 advanced 路线，不是普通 handoff 的默认 POSCAR；选择它时必须额外处理 Sc placeholder 和 POTCAR 风险

---

## 与其他文件的关系

| 文件 | 关系 |
|---|---|
| `cell.str` + `unit_cell.str` + `%block SuperCell` | `J.POS` 的来源 |
| `atat.NNN_Y` (Y=1..4) | 在 `J.POS` 基础上把指定 pair 中的两个原子改写为 Sc（除 Y=1 外） |
| `pair_POS.NNN` | 在 `J.POS` 基础上把 pair 中两个原子分别打成 `Z+25` 和 `Z+35` 的元素标记，用于 VESTA 可视化；不直接给 VASP 用 |
| `PASP.used_info` | 包含本次运行实际生效的 `Z_values` / `cell.str` / `SuperCell` 信息，用于交叉验证 `J.POS` 是否符合预期 |

---

## 来源

- PASP 源码: `Latticemodel/src/J_path_sym.f90` 第 194 行 `CALL write_xa_POS(na, ns, xa, cell, isa, iza, 'J.POS')`
- 工具子例程: `write_xa_POS`（标准 POSCAR 写出器，写 Direct 坐标，比例因子固定为 1.0）
- `topics/four_state_method.md`
- `files/atat.NNN_Y.md`
