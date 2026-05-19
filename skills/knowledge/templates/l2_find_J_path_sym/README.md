# L2 find_J_path_sym Template

> Minimal input package for `Model find_J_path_sym`. Used by `skills/knowledge/workflows/l2_find_J_path_sym.md` Stage 1 as the starting baseline.

---

## Status

| 文件 | 角色 | 是否可直接拿去跑 |
|---|---|---|
| `PASP.input` | 三个必填 block + 三个必填 line 的最小骨架 | 字段值与 NiI₂ 例子一致；**结构文件占位为空**，不能直接跑 |
| `cell.str` | 占位骨架，仅含注释 | **不可**直接使用，必须填入用户实际晶胞结构 |
| `unit_cell.str` | 占位骨架，仅含注释 | **不可**直接使用，必须填入用户实际原胞结构 |

> 这是有意设计：让用户被迫提供真实结构，而不是把模板默认值当作科研输入。

---

## File Roles

### `PASP.input`
- 包含 `Model find_J_path_sym` 的完整必填字段集合（`SuperCell`、`Z_values`、`isaAB`、`Spin_values`、`magnetic_or_ligand`、`fig.maxk`、`fig.mdist`）
- 头部 comment 列出每字段对应的 reference 卡，写入前应当查
- 以 NiI₂（Z=28, Z=53）的字段值为示例；改用其他体系时必须同步修改 `Z_values`、`Spin_values`、`magnetic_or_ligand` 三组

### `cell.str`
- 仅含说明性 comment，没有真实 lattice / 原子坐标
- 用户必须替换为：
  - 真实的 `LatticeConstant`、`%block LatticeVectors`、`%block AtomicCoordinatesAndAtomicSpecies` 完整内容
  - 元素出现顺序需与 `PASP.input` 中 `Z_values` / `Spin_values` / `magnetic_or_ligand` 一致
  - `AtomicCoordinatesAndAtomicSpecies` 必须按 species id 分组：全部 species 1、全部 species 2……；从原胞扩超胞时不要写成 `Ni I I Ni I I ...` 这类 tile-by-tile interleaved 顺序
  - 对多 species `find_J_path_sym`，不要依赖非单位 `%block SuperCell` 从 primitive / interleaved `cell.str` 自动扩胞；安全模板用法是把完整目标分析超胞直接写进 `cell.str` 并按 species id 分组，此时 `SuperCell` 保持单位阵
- 可参考 `pasp_examples/Lecture-2/find_J_path_sym/inputs/cell.str` 与 `cell.str_NiI2_5x5` / `cell.str_NiI2_6x6` 的实际格式
- 详细字段定义见 `files/cell.str.md`

### `unit_cell.str`
- 仅含说明性 comment，没有真实 primitive cell
- 用户必须替换为真正的最小原胞；不要把已经扩大的 supercell 误写到这里
- 字段：`unit_cell.na`、`%block unit_cell_in_Ang`、`%block Atoms_in_unit_cell_Ang`
- 详细字段定义见 `files/unit_cell.str.md`

---

## Upstream

无 — 本 template 是 L2 find_J workflow 的起点。

## Downstream

- `workflows/l2_find_J_path_sym.md` Stage 1 → Stage 2（用户在 `runs/<run-id>/` 中复制本 template 作为运行起点）
- 跑出来的 `J.POS` + `log.out` 中的 MAGMOM/M_CONSTR 块 → 用户的四态法 DFT 流程

---

## Gate Evidence

- `PASP.input` 字段集合与 `pasp_examples/Lecture-2/find_J_path_sym/inputs/PASP.input` 实测 input 一致（Iter 1 验证）
- 头部 reference 卡列表覆盖了写入每个字段时必须查的 reference

---

## Blocked / TODO

- 服务器实跑后，到 `workflows/l2_find_J_path_sym_run_notes.md` 记录：
  - 当前 PASP 版本下输出文件名是否与 README 描述一致
  - 不同 supercell 大小（5×5 / 6×6 / 7×7）对结果稳定性的影响

---

## 不要做的事

- 不要把 `cell.str` / `unit_cell.str` 占位文件直接拿去跑
- 不要把从 `unit_cell.str` 扩出的 supercell 原子按 tile 顺序交错写入 `cell.str`；`find_J_path_sym` 会要求 species id 非递减并在交错时停止
- 不要在多 species `find_J_path_sym` 中把 primitive / interleaved `cell.str` 留给非单位 `%block SuperCell` 自动扩胞，除非已证明扩胞后的全局 `isa` 仍非递减
- 不要在改 `Z_values` 元素时只改 `Z_values` 不改 `Spin_values` / `magnetic_or_ligand`
- 不要把示例的 `fig.mdist 1 30` 直接套用到任意尺寸的 `cell.str`；30 Bohr ≈ 15.87 Å，过小或过大都需要按当前 `cell.str` 尺寸调整
- 不要在 stage `input/` 中直接跑 PASP；按 workflow 文档的约定，在 `runs/<run-id>/` 中跑
