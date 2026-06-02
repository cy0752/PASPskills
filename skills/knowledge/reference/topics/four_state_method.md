# Four-State Method for Magnetic Exchange Parameters

## 适用问题

`Model find_J_path_sym` 给出对称性不等价磁性原子对（pair）后，需要通过 DFT 计算得到每对的交换参数。最常用的方法是**四态法（four-state method）**：对每个不等价 pair，做 4 次固定磁序的 DFT 计算，由 4 个能量线性组合解出交换参数。

本主题描述四态法的物理原理、PASP 在 `find_J_path_sym` 阶段提供的 DFT 输入素材，以及 DFT 端的常见约定。它不替代具体 workflow 文档，只为输出层和 DFT 衔接层提供共同语义。

---

## 各向同性海森堡情形

考虑一对自旋 \(S_i, S_j\) 形成的总能量：

```text
E_ij = J_ij · S_i · S_j  +  S_i · A  +  S_j · B  +  C
```

其中 `A`, `B`, `C` 包含了第三方磁原子和常数项。固定 `i, j` 自旋分别 ↑ 或 ↓（其余自旋方向**任意但保持不变且与 i, j 自旋方向垂直**），得到 4 种能量：

```text
E_↑↑ = +J·S²  + A + B + C
E_↑↓ = -J·S²  + A − B + C
E_↓↑ = -J·S²  − A + B + C
E_↓↓ = +J·S²  − A − B + C
```

线性组合即可消去 `A`, `B`, `C`：

```text
J_ij = ( E_↑↑ + E_↓↓ − E_↑↓ − E_↓↑ ) / (4 S²)
```

`S` 是磁性原子的自旋量子数（与 `Spin_values` 中除以 2 后得到的值一致）。

---

## 矩阵形式（含 SOC、各向异性、DM、Kitaev）

\(J_{ij}\) 退化为 3×3 矩阵，共 9 个分量：

```text
                   ┌                          ┐
                   │ J_xx   J_xy   J_xz       │
        J_ij  =    │ J_yx   J_yy   J_yz       │
                   │ J_zx   J_zy   J_zz       │
                   └                          ┘
```

对每个分量 `(a, b)`，固定 `i, j` 自旋分别沿 ±a 和 ±b 方向，得到：

```text
J_ij,ab = ( E_ij,ab,↑↑ + E_ij,ab,↓↓ − E_ij,ab,↑↓ − E_ij,ab,↓↑ ) / (4 S²)
```

约束条件：
- VASP 必须开启 SOC 与非共线磁矩
- `i, j` 之外的自旋方向应与 `i, j` 自旋方向**垂直**，以避免高阶项干扰
- 同一思路也可用于单离子各向异性矩阵 \(\mathbb{A}_i\) 和双二次相互作用 \(B_{ij}\)，但四态的具体取法略有不同（详见原始文献或 PASP 文档）

---

## PASP `find_J_path_sym` 提供的 DFT 输入素材

对每个不等价 pair `i`，PASP 写出：

| 文件 / 输出 | 数量 | 内容 |
|---|---|---|
| `J.POS` | 1 | 一份与输入 cell 相同的 POSCAR；普通 handoff 默认把它作为四态 DFT 的 POSCAR |
| `pair_POS.NNN` | 每 pair 1 个 | 用于可视化：把 pair 中两个原子分别打成 `Z+25` 和 `Z+35` 的元素标记，便于在 VESTA 中直接看出哪两个是 pair 原子。**不直接给 VASP 用** |
| `atat.NNN_Y` | 仅对 PASP 内部写出 advanced Sc-placeholder POSCAR 的 pair 产生；每个被写出的 pair 有 4 个（Y=1..4） | 可选 advanced POSCAR 族，含 Sc placeholder；普通用户默认不要把它当作 POSCAR，也不要用 `npair × 4` 反推数量，命名规则见 `files/atat.NNN_Y.md` |
| log.out 中的 MAGMOM 行 | 每 pair 4 行 | 共线或矩阵形式标量 J 的初始磁矩；带 `#@upup` / `#@updn` / `#@dnup` / `#@dndn` 注释 |
| log.out 中的 M_CONSTR 行 | 每 pair 4 行 | 矩阵形式 J 用的非共线约束；带 `#@DM_up_up` / `#@DM_up_dn` / `#@DM_dn_up` / `#@DM_dn_dn` 注释 |

`NNN` 是 pair 编号（3 位零填充）。

`Y` 与四态对应关系：

| `Y` | 物理状态 | atat 文件中 pair 原子标记 |
|---|---|---|
| `1` | ↑↑ (upup) | 两个 pair 原子都保留磁性元素标记，文件结构与 `J.POS` 一致 |
| `2` | ↑↓ (updn) | pair 原子 1 保留磁性元素标记，pair 原子 2 改写为占位元素 Sc (Z=21) |
| `3` | ↓↑ (dnup) | pair 原子 1 改写为 Sc，pair 原子 2 保留磁性元素标记 |
| `4` | ↓↓ (dndn) | 两个 pair 原子都改写为 Sc |

为什么用 Sc：在 VASP 的 INCAR 中，`MAGMOM` 与 `M_CONSTR` 是**按元素分组**的；只有把 pair 中需要独立约束的原子改成另一个元素符号，才能给它们独立的磁矩 / 约束分量，而不会把同一化学元素的所有原子一起影响。Sc 只是一个无干扰的占位选择，并非实际化学含义。

---

## DFT 端用户必须自备 / 确认的内容

PASP `find_J_path_sym` **不**生成完整的 VASP 输入。下列由用户负责：

| 文件 | 备注 |
|---|---|
| `POSCAR` | 默认复制 `J.POS`；只有用户明确选择 advanced Sc-placeholder 路线时才使用 `atat.NNN_Y` |
| `INCAR` | 必须由用户提供或逐项确认基础 DFT 设置；agent 只能把 PASP log 中对应状态的 `MAGMOM` / `M_CONSTR` 行追加进去，不能发明生产 INCAR 参数 |
| `KPOINTS` | 用户根据收敛性自行决定并确认 |
| `POTCAR` | 默认 `J.POS` 路线按 `J.POS` 元素行准备；advanced `atat.NNN_Y` 路线中所有出现的元素都必须有对应 `POTCAR`，包括占位 Sc。Sc 的赝势选择是 DFT 端责任，必须由用户确认 |

---

## 注意事项

- 自旋值 `spin_val(isa(ia))` 来自 PASP 的 `Spin_values` 块；MAGMOM 中写出的是这个值的整数倍（已经是 `2S` 量级）
- 非 pair 的磁性原子在 MAGMOM 中按 `spin3.in` 的 z 分量写出（值 = `spin3(3, ia) * 2`）；这意味着如果用户希望非 pair 自旋"任意但与 pair 垂直"，需要确保 `spin3.in` 中第三方自旋方向已正确设置
- 非磁性物种的 MAGMOM 段会写成 `<NITYP>*0`；M_CONSTR 段会写成 `<3*NITYP>*0`
- 在 M_CONSTR 中：pair 原子 1 沿 x 轴约束，pair 原子 2 沿 y 轴约束。这是矩阵 J 计算的标准设置（确保两个 pair 自旋方向相互垂直）
- 不要把矩阵情形的 4 状态当作各向同性情形来用：矩阵情形需要 9 组（每组 4 状态）共 36 次 DFT 计算才能拟合完整 J 矩阵；各向同性只需 4 次

---

## 当四态法不适用的情况

- 体系存在**长程**或显著的**多体**相互作用，使得 `A`, `B`, `C` 不再是常数（应改用更高 SuperCell 或更复杂的拟合策略）
- pair 距离过近，pair 自旋的局域翻转会显著扰动周围磁结构（应增大 pair 之间的有效隔离）
- 体系为金属性 / 巡游磁性，固定自旋构型在 DFT 中不易稳定收敛

这些情况不属于 `find_J_path_sym` 的失败模式，而属于物理建模选择。出现可疑结果时优先检查 `Spin_values` 是否合理、SuperCell 是否够大、pair 之间是否有第三方自旋干扰。

---

## 来源

- PASP 源码: `Latticemodel/src/J_path_sym.f90` 第 194-350 行（`atat.NNN_Y` 与 MAGMOM/M_CONSTR 输出的实现）
- PASP 网页文档: `3.1.7 Model find_J_path_sym 相关设置项` 章节
- `params/Model.md`（`find_J_path_sym` 选项）
- `files/J.POS.md`
- `files/atat.NNN_Y.md`
