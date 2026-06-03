# FORCE_CONSTANTS

## 文件作用
`FORCE_CONSTANTS` 提供 phonopy 风格的实空间二阶力常数矩阵。在 L8 spin-lattice ion / strain 分支中，当 `phonopy_force_constant T` 且不是 `spin_lat.strain_only` 路径时，PASP 会与 `SPOSCAR` 一起读取它，用于构造 phonon / force-constant 响应。

## 何时需要
- `Model Spin_lattice_interaction` 中需要 phonopy force constants。
- L8 ion / lattice / strain contribution 需要由力常数把 spin force 转成位移 / 极化贡献。
- 其他 phonon / local-mode 路径显式使用 phonopy force constants 时。

## 关键字段或内容
PASP 当前读取的是 phonopy text `FORCE_CONSTANTS` 形状：
- 第一行：超胞原子数 `na_sc`。
- 随后对每个有序原子对 `(ia, ja)`，按 `ia = 1..na_sc`、`ja = 1..na_sc` 顺序出现：
  - 一行两个整数：`ia ja`。
  - 三行、每行三个数：该 pair 的 3 x 3 force-constant matrix。

PASP 写出同类文件时，每个 3 x 3 block 单位注释为 `eV/Ang^2`。

## 注意事项
- `FORCE_CONSTANTS` 必须与同目录 `SPOSCAR` 的超胞原子数、原子顺序和坐标基底一致。PASP 会检查第一行原子数是否等于从 `SPOSCAR` 读到的 `na_sc`。
- pair header 必须严格按 `(ia, ja)` 双循环顺序排列；如果读到的 pair index 不是当前期望值，PASP 会报 `read_FORCE_CONSTANTS: wrong format in FORCE_CONSTANTS`。
- 该文件是当前材料 / 当前结构 / 当前超胞的上游物理数据。不要从 Lecture-8 BiFeO3 示例或其他材料复制为默认值。
- preflight 应同时检查 `phonopy_force_constant`、`SPOSCAR`、`FORCE_CONSTANTS`、`cell.str` / `unit_cell.str` 的结构关系和来源记录。

## 来源
- PASP source audit: `phonopy.F90` `read_phonopy`, `read_FORCE_CONSTANTS`, `write_FORCE_CONSTANTS`
- L8 runtime observation: `BiFeO3_ion_strain` input packages contain `FORCE_CONSTANTS` and PASP reads them when `phonopy_force_constant T`
