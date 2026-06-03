# SPOSCAR

## 文件作用
`SPOSCAR` 是 phonopy 生成/使用的超胞结构文件。在 PASP 中，`phonopy_force_constant T` 路径会读取同目录 `SPOSCAR`，再读取同一超胞顺序下的 `FORCE_CONSTANTS`。

## 何时需要
- `Model Spin_lattice_interaction` 中使用 phonopy force constants。
- L8 ion / lattice / strain contribution 需要通过 `FORCE_CONSTANTS` 建立 phonon / force-constant 响应。

## 关键字段或内容
PASP 通过 POSCAR reader 读取 `SPOSCAR` 头部和坐标，因此它应是 VASP POSCAR / phonopy SPOSCAR 风格结构文件，通常包含：
- 元素或标题行。
- 全局缩放因子。
- 三行晶格矢量。
- 元素计数。
- 坐标类型，如 `Direct`。
- 每个超胞原子的坐标，顺序必须与 `FORCE_CONSTANTS` 的 atom index 一致。

## 注意事项
- `SPOSCAR` 描述的是 force-constant 超胞，不一定等同于 L8 计算中 `cell.str` 的显示超胞。PASP 会检查 `SPOSCAR` cell 是否是当前 `cell_fig` 的 supercell；不匹配时会报 `read_phonopy: cell_sc is not a supercell of cell, check SPOSCAR`。
- `SPOSCAR` 与 `FORCE_CONSTANTS` 是一组上游数据。不能只因为文件名匹配就混用不同材料、不同超胞、不同原子顺序的文件。
- preflight 应记录 `SPOSCAR` 的上游来源、生成结构、元素顺序、原子数以及它与当前 PASP 结构路线的关系。

## 来源
- PASP source audit: `phonopy.F90` `read_SPOSCAR`, `read_phonopy`
- L8 runtime observation: `BiFeO3_ion_strain` uses `SPOSCAR` together with `FORCE_CONSTANTS`
