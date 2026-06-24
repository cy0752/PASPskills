# mode_def.input

## 文件作用
`mode_def.input` 是常见的 split include 文件，用来把 `%block local_mode.mode_definition` 从根 `PASP.input` 中拆出来维护。它定义当前 `Model Invariant` / `Model atomic_effective_H` 数据链使用的 local modes，例如自旋模式、局域位移 / 声子模式，或混合自由度。

本文件卡只说明 `mode_def.input` 作为文件的角色和检查契约。`%block local_mode.mode_definition` 的精确 block 语法、mode 段格式、空行规则和代表位点规则必须继续查 `skills/knowledge/reference/params/local_mode.mode_definition.md`。

## 何时需要
- 当 `PASP.input` 中直接写了 `%include mode_def.input` 时，该文件就是输入包的必需 direct include file。
- 当 `local_mode.general_model T` 且当前模型依赖自定义 local modes 时，通常需要在 `PASP.input` 内联 `%block local_mode.mode_definition`，或通过 `mode_def.input` 这类 split include 文件提供同一 block。
- 在 L5 Cr2O3 SLD 历史 example 中，stage 1 / 2 / 3 的 `PASP.input` 都直接 include `mode_def.input`；因此这些 example packages 中它是 stage-stable input role。这个事实不能把 Cr2O3 的 mode 数、坐标或物种设置推广为默认值。

## 与 PASP.input 的关系
典型写法是在根 `PASP.input` 中保留一行：

```text
%include mode_def.input
```

preflight 应从根 `PASP.input` 遍历 include graph，确认：
- `mode_def.input` 能从候选 input package 解析到普通文件；
- 文件不是缺失、目录、空文件或来自不明 stage 的残留；
- include 顺序不会让另一个内联或 included `%block local_mode.mode_definition` 先于它生效；
- 如果存在重复 block，按 `PASP.input` first-one-wins 规则标出真正生效的位置，不能修改不可达重复项后声称输入已改变。

## 包含的 block
`mode_def.input` 应包含一个完整的：

```text
%block local_mode.mode_definition
2
N_mode
...
%endblock local_mode.mode_definition
```

不要在本文件卡中按历史 example 复制具体 mode 内容。写入或修改该 block 前，必须先查：
- `skills/knowledge/reference/params/local_mode.mode_definition.md`
- 对纯自旋 mode 的代表点位分析，还应查 `skills/knowledge/reference/topics/symmetry_representative_sites.md`
- 对多原子位移 / 声子 mode，必须确认 `N_atom` 后存在独立 species-id 列表行，后续才是逐原子的 `x y z dx dy dz` 行；不要把 species id 混写进坐标行第一列。

## Row-count / order 一致性检查
preflight 至少应检查：
- block 声明的 mode 总数 `N` 与实际 mode 定义段数一致；
- `N` 后面直接接第一段 mode 定义，不插入额外空行；
- 不同 mode 定义之间的空白分隔行符合 `local_mode.mode_definition` reference；
- 每个 mode 的 species id、坐标系和方向定义与当前 `cell.str` / `unit_cell.str`、`Z_values`、`Spin_values` 和用户确认的建模自由度一致；
- 对多原子位移 / 声子 mode，位移向量是 Cartesian components，不是 fractional / lattice-vector coordinates；
- mode 顺序与同一数据链中的 `mode_mass.input` / `%block atom_Heff.MASS_local_mode` 顺序一致；
- mode basis 与 `local_mode_PM.dat`、`J_best.dat`、`amp_local_mode.in` 属于同一上游模型，不混用其他材料、其他 supercell 或其他 stage 的文件。

如果已有 `local_mode-*.xsf`、`def_local_modes.dat` 或上游 run evidence，可把它们作为当前 workspace 的一致性证据；没有这些证据时，不要从 lecture example 推断当前 mode 数。

## L5 Cr2O3 用法
Lecture-5 Cr2O3 SLD historical example 中，`mode_def.input` 是三阶段共同的 split include file。它承载 Cr2O3 example 的 spin and displacement local-mode definitions，并与同 package 的 `mode_mass.input`、`local_mode_PM.dat`、`J_best.dat` 和 `amp_local_mode.in` 共同形成同一 local-mode basis。

这些 example 事实只用于识别文件角色和 preflight 检查方向。运行时 agent 不得把历史 example 中的 mode 数、原子坐标、species id、mode 顺序或材料自由度当作当前用户任务的默认设置。

## Reference-before-write
准备创建、覆盖或修改 `mode_def.input` 时：
- 先确认当前 workflow stage、材料、结构基准、参与自由度和上游模型 provenance；
- 先读 `params/local_mode.mode_definition.md`，必要时读 `topics/symmetry_representative_sites.md`；
- 如果 `mode_def.input` 是 L5 stage 2 / 3 的输入包组成部分，还要确认它没有与 upstream `amp_local_mode` handoff 所属的 local-mode basis 冲突；
- 若 reference 或用户权威来源不能覆盖 mode 内容，只能保留为 draft / candidate，不能提升为 formal `input/` 或派生 run。

## 常见误区
- 只把文件放进目录，但忘记在 `PASP.input` 中 `%include mode_def.input`。
- `PASP.input` 中既 include 了 `mode_def.input`，又在别处内联重复 `%block local_mode.mode_definition`，导致 agent 修改了不生效的版本。
- 把 Cr2O3 example 的 42 个 modes、坐标或 species id 当作其他体系默认值。
- 把 PTO / soft-mode 多原子位移 mode 写成每行七列 `species_id x y z dx dy dz`，漏掉独立 species-id 列表行。
- 把 `def_local_modes.dat` 的 displacement components 当作 fractional displacement 来反推 `mode_range`。
- 修改 mode 定义后，没有同步检查 `mode_mass.input` 的质量个数和顺序。
- 修改 mode 定义后，继续复用旧的 `local_mode_PM.dat`、`J_best.dat` 或 `amp_local_mode.in`，造成 local-mode basis 混用。
- 忽略 `local_mode.mode_definition` 的空行 / 分隔行规则，导致 Fortran 读取错位或 EOF / syntax error。

## Verifier expectations
read-only `input-preflight` 对包含 `mode_def.input` 的 package 应报告：
- `PASP.input` include graph 中 `mode_def.input` 的解析路径和生效位置；
- 文件中是否存在完整 `%block local_mode.mode_definition`；
- mode 数、mode 段数、分隔行、species id、坐标系和 mode 顺序的一致性检查结果；
- 与 `mode_mass.input`、`local_mode_PM.dat`、`J_best.dat`、`amp_local_mode.in`、`Z_values`、`Spin_values` 的同基底风险；
- 哪些检查来自当前 workspace evidence，哪些仍需要用户确认或上游 provenance。

Verifier 不应替用户选择参与自由度、代表点位、mode 数或材料参数。

## 相关条目
- `params/local_mode.mode_definition.md`
- `topics/PASP.input.md`
- `topics/symmetry_representative_sites.md`
- `files/mode_mass.input.md`
- `files/local_mode_PM.dat.md`
- `files/J_best.dat.md`
- `files/amp_local_mode.in.md`

## 来源章节
- 3.1.7.5 自定义局域模式 (`block local_mode.mode_definition`)
- `mode_def.input` 文件名来自本仓库 Lecture-5 / Lecture-4 examples 的 split include pattern；官方语法权威仍是 `local_mode.mode_definition` block reference。
