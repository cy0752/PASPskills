# def_local_modes.dat

## 文件作用
`def_local_modes.dat` 是 PASP 在 local-mode setup 后写出的 local mode 定义/检查文件。它记录当前运行实际采用的 local-mode basis，可用于核对 `local_mode.mode_definition` 被 PASP 约化、归一化或扩展后的结果。

## 何时出现
- L3 `Model Invariant` / shared-basis 运行完成 local-mode setup 后可能生成。
- 当 L5 `Model atomic_effective_H` 需要复用同一 local-mode basis 时，可作为 mode order、mode ratio、mass order、`local_mode_PM.dat` / `J_best.dat` 同基底检查的辅助证据。

## 字段理解
文件开头通常包含 local-mode 总数和 unit-cell 信息；随后按 local mode 输出原子类型、位置和位移向量。

重要单位/坐标规则：
- `#ucell (in Ang)` 对应的晶格矩阵单位是 Angstrom。
- `pos` 和 `disp` 是不同语义的列，不要因为 `pos` 可能表现为内部坐标就把 `disp` 也当作 fractional 坐标。
- `disp` 列是 Cartesian local-mode displacement vector components，不是 lattice-vector fractional displacement。对 PTO 这类集体铁电软模，反馈验证要求按 Bohr-style Cartesian displacement 来理解，不要把 `0.2554` 之类数值解释为 `0.2554` 个晶格矢量。
- PASP 会对位移向量做归一化；使用该文件时应关注同一 mode 内不同原子位移的比例、方向和实际 reduced mode 分量，而不是把它直接当作原始输入 block 的逐字副本。

## 用法
- 核对 `local_mode.mode_definition` 是否按预期读入，例如 Ti / O / Pb 位移比例是否保留。
- 估算 `local_mode.mode_range` 时，用目标物理位移除以 `def_local_modes.dat` 中对应原子的 reduced displacement component，得到 local-mode amplitude 的量级；再由用户确认安全裕度和最小原子间距 smoke-test。
- 写 `atom_Heff.MASS_local_mode` 时，用它确认当前实际 local-mode 个数和顺序；质量值仍需来自用户、材料数据或有效质量计算。
- 进入 L5 前，作为 `mode_def.input` / inline mode definition、`mode_mass.input`、`local_mode_PM.dat`、`J_best.dat` 和 `amp_local_mode.in` 是否同基底的辅助证据。

## 常见误区
- 把 `disp` 当成 fractional / lattice-vector coordinate，导致 mode amplitude 和 `mode_range` 被严重放大。
- 只看输入的 `local_mode.mode_definition`，不看 `def_local_modes.dat` / `local_mode-*.xsf`，从而漏掉 PASP 实际生成的 local-mode 个数或顺序。
- 把某个历史 PTO / BaTiO3 / Cr2O3 的 `def_local_modes.dat` 当作当前材料证据。只有当前工作目录或用户授权来源中的同材料、同结构、同 mode definition 文件才能用于同基底检查。

## Verifier expectations
read-only verifier 在 L3/L5 preflight 或 handoff 检查中看到 `def_local_modes.dat` 时，应报告：
- 文件来自哪个 run / stage；
- local-mode 个数和 mode 顺序能否支持当前 `mode_mass` / `amp_local_mode` / `local_mode_PM.dat` 的顺序判断；
- `disp` 是否被正确作为 Cartesian displacement vector components 使用；
- 哪些结论只来自该辅助文件，仍需要用户确认或上游运行记录支撑。

## 相关条目
- `params/local_mode.mode_definition.md`
- `params/local_mode.mode_range.md`
- `params/atom_Heff.MASS_local_mode.md`
- `files/mode_def.input.md`
- `files/mode_mass.input.md`
- `files/local_mode_PM.dat.md`
