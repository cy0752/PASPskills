# atat.NNN_Y

## 文件作用

`Model find_J_path_sym` 输出的 POSCAR 族，属于四态法 DFT 的 optional / advanced handoff。普通用户默认应使用 `J.POS` 作为 POSCAR，并从 `log.out` 追加对应状态的 `MAGMOM` / `M_CONSTR`；只有用户确认 Sc placeholder 与 POTCAR 策略时，才把 `atat.NNN_Y` 当作 VASP POSCAR。

当 PASP 对某个不等价 pair 写出 advanced Sc-placeholder POSCAR 时，会为该 pair 产生 4 个文件，对应四态法的 4 种自旋固定组态（↑↑ / ↑↓ / ↓↑ / ↓↓）。并非每个 pair 都一定有 `atat.NNN_Y`；普通 DFT handoff 不能用 `npair × 4` 反推文件数量。文件命名约定：

```text
atat.<NNN>_<Y>
```

- `<NNN>`：pair 编号，3 位零填充，从 `001` 开始
- `<Y>`：状态编号，单位整数 `1` ~ `4`

例如 `atat.001_1`、`atat.001_2`、`atat.001_3`、`atat.001_4` 是第 1 个 pair 的 4 个 POSCAR；`atat.007_3` 是第 7 个 pair 的 ↓↑ 状态 POSCAR。

---

## 何时产出

- 仅由 `Model find_J_path_sym` 产出
- 仅对 PASP 内部判定需要写出 Sc-placeholder advanced POSCAR 的 pair 产生文件；当前源码审计中该路径对应 `SE_xc=3` 或 `SE_xc=4` 的 pair
- 对每个被写出的 pair，产生 4 个文件（Y=1..4）
- 总数 = 被写出 advanced POSCAR 的 pair 数 × 4，不一定等于不等价 pair 总数 × 4

---

## 何时使用

- 可作为四态法 DFT 计算的 advanced VASP POSCAR，但不是普通默认路径
- 与 `log.out` 中的 `MAGMOM` / `M_CONSTR` 行配套使用：每对 `atat.NNN_Y` 都有一行带 `#@upup` / `#@updn` / `#@dnup` / `#@dndn` 注释的初始磁矩或非共线约束行；`#@DM_*` 系列对应矩阵形式 J（含 SOC）的 M_CONSTR
- 4 个状态的 DFT 总能量按四态线性组合（见 `topics/four_state_method.md`），即可得到该 pair 的交换参数

---

## 与状态 `Y` 的对应关系

| `Y` | 物理状态 | pair 原子 1 元素标记 | pair 原子 2 元素标记 | 元素行规则 |
|---|---|---|---|---|
| `1` | ↑↑ (upup) | 保留磁性元素 | 保留磁性元素 | 元素行 = 原始 `cell.str` 元素列表（无 Sc） |
| `2` | ↑↓ (updn) | 保留磁性元素 | Sc (Z=21) | 元素行 = 原始 `cell.str` 元素列表 + `Sc` |
| `3` | ↓↑ (dnup) | Sc (Z=21) | 保留磁性元素 | 元素行 = 原始 `cell.str` 元素列表 + `Sc` |
| `4` | ↓↓ (dndn) | Sc (Z=21) | Sc (Z=21) | 元素行 = 原始 `cell.str` 元素列表 + `Sc` |

`Y=1` 的文件中两个 pair 原子都保持原磁性元素标记，因此该文件**结构上与 `J.POS` 完全一致**（元素行、计数行、坐标列表全部相同）。这不是 bug，而是为了让 VASP 端对 4 个状态使用统一的工作流（4 份 POSCAR + 4 份 INCAR）。

`Y=2` 与 `Y=3` 的文件都是 `<n_mag - 1>` 个磁性原子 + 其他物种 + 1 个 Sc 占位原子，两者只是把 pair 中的哪一个原子改为 Sc 不同。

`Y=4` 的文件包含 `<n_mag - 2>` 个磁性原子 + 2 个 Sc 占位原子。

Sc 是 PASP 选定的占位元素（原子序数 21），与 pair 中磁性元素的化学元素**无关**。它的作用是让 VASP 把 pair 中需要独立约束的原子和其他同元素原子分开处理，从而在 INCAR 的 `MAGMOM` 与 `M_CONSTR` 中能给这两个原子独立的分量。详见 `topics/four_state_method.md`。

---

## 关键字段 / 结构

`atat.NNN_Y` 是标准 POSCAR（Direct 分数坐标）：

```text
<species_symbols>           # 第 1 行：元素符号；Y∈{2,3,4} 时末尾会多一个 Sc
<scale_factor>              # 第 2 行：1.0
<a1_x> <a1_y> <a1_z>        # 第 3-5 行：晶格矢量（与 J.POS 完全一致）
<a2_x> <a2_y> <a2_z>
<a3_x> <a3_y> <a3_z>
<NITYP_1> <NITYP_2> ...     # 第 6 行：每个元素的原子数
Direct                      # 第 7 行
<x_1> <y_1> <z_1>           # 第 8 行起：原子坐标
...
```

注意事项：

- 第 8 行起的原子坐标顺序**不一定**与 `J.POS` 一一对应：被改成 Sc 的 pair 原子会被移到该元素分组的末尾。例如在 `atat.001_2` 中，pair 中第二个原子（原本是 J.POS 中第 21 号 Ni 原子）会从 Ni 列表中移除，并出现在文件末尾的 Sc 段
- 当 `Y∈{2,3,4}` 时，第 1 行末尾会追加 ` Sc`；第 6 行末尾会追加对应的 Sc 原子数（1 或 2）
- 晶格矢量、比例因子、其他原子的坐标都与 `J.POS` 一致——只有 pair 中两个原子的元素标签和位置顺序会随 `Y` 改变

---

## 注意事项

- 普通 handoff 不需要读取或复制这些文件作为 POSCAR；用 `J.POS` + `log.out` 磁约束即可组织四个状态
- 这 4 个文件的**几何结构完全相同**：所有原子的笛卡尔坐标都没动，只是给 pair 中两个原子换了元素标签并把它们移到对应元素的末尾。不要因为 `Y` 不同就以为它们是 4 种结构畸变
- VASP 端 `POTCAR` 的拼接顺序**必须**严格按照 `atat.NNN_Y` 第 1 行元素符号顺序：`POTCAR_<元素1> + POTCAR_<元素2> + ... + POTCAR_Sc`。如果 4 个状态用同一个 POTCAR 顺序，需要在 `Y=1` 的 POTCAR 末尾也补一段（例如复制磁性元素 POTCAR 改名为 Sc）以保持顺序对齐——更稳妥的做法是为每个 `Y` 分别准备 POTCAR
- Sc 的 POTCAR 来源是 DFT 端的责任。常见做法：把磁性元素的 POTCAR 复制一份用作 Sc，确保 4 个状态的 pair 原子使用相同价电子数与赝势设置；不要随便用真实 Sc 赝势，否则 pair 原子的物理性质会被 Sc 真实赝势污染
- 4 个状态对应的 `MAGMOM` 与 `M_CONSTR` 行从 `log.out` 中的 `#@upup` / `#@updn` / `#@dnup` / `#@dndn` 与 `#@DM_up_up` / `#@DM_up_dn` / `#@DM_dn_up` / `#@DM_dn_dn` 注释行中提取
- 在矩阵形式 J（含 SOC）情形，必须使用 `M_CONSTR` 行（非共线约束）；纯各向同性海森堡情形下使用 `MAGMOM` 行（共线初值）即可
- pair 编号 `NNN` 的物理含义在 `log.out` 的 pair 描述行中给出（`Atoms: J_pair(1) J_pair(2)  SE_SSE: ...  pair_dist: ...  pair_coord: ...`）
- 与同一 pair 配套的 `pair_POS.NNN` 文件用元素 `Z+25`、`Z+35` 标记 pair 原子，仅供 VESTA 可视化；不要把它误传给 VASP

---

## 与其他文件的关系

| 文件 | 关系 |
|---|---|
| `J.POS` | 默认 POSCAR / 结构基准；`atat.NNN_Y` 只在 advanced 路线中在它基础上替换部分元素标签 |
| `pair_POS.NNN` | 同一 pair 的可视化版本（VESTA 用）；不参与 DFT |
| `log.out` 的 `#@upup` / `#@updn` / `#@dnup` / `#@dndn` 行 | 对应 `atat.NNN_1` / `_2` / `_3` / `_4` 的初始 `MAGMOM` |
| `log.out` 的 `#@DM_up_up` / `#@DM_up_dn` / `#@DM_dn_up` / `#@DM_dn_dn` 行 | 矩阵形式 J 用的 `M_CONSTR` 行 |
| `Z_values`、`Spin_values` | 决定每个 pair 中磁性元素是哪一个、磁矩尺度多大；间接决定 `MAGMOM` 行中的数值 |
| `topics/four_state_method.md` | 四态法物理原理与 4 状态 → J 的线性组合 |

---

## 来源

- PASP 源码: `Latticemodel/src/J_path_sym.f90` 第 219-246 行（`atat.NNN_Y` 写出循环）以及第 247-350 行（配套 `MAGMOM` / `M_CONSTR` 输出）
- `topics/four_state_method.md`
- `files/J.POS.md`
- `params/Model.md`（`find_J_path_sym` 选项）
