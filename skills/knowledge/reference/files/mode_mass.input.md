# mode_mass.input

## 文件作用
`mode_mass.input` 是常见的 split include 文件，用来把 `%block atom_Heff.MASS_local_mode` 从根 `PASP.input` 或 `MD.input` 相关配置中拆出来维护。它为当前 local-mode basis 中的各个 local modes 提供等效相对质量。

本文件卡只说明 `mode_mass.input` 作为文件的角色和检查契约。`%block atom_Heff.MASS_local_mode` 的精确定义、默认值、取值范围和质量含义必须继续查 `knowledge/reference/params/atom_Heff.MASS_local_mode.md`。

## 何时需要
- 当 `PASP.input` 中直接写了 `%include mode_mass.input` 时，该文件就是输入包的必需 direct include file。
- 当 `Model atomic_effective_H` 的 MD / SLD 运行需要显式设置 local-mode masses 时，可内联 `%block atom_Heff.MASS_local_mode`，或通过 `mode_mass.input` 这类 split include 文件提供。
- 在 L5 Cr2O3 SLD historical example 中，stage 1 / 2 / 3 的 `PASP.input` 都直接 include `mode_mass.input`；因此这些 example packages 中它是 stage-stable input role。历史质量数值不能推广为其他材料默认值。

## 与 PASP.input 的关系
典型写法是在根 `PASP.input` 中保留一行：

```text
%include mode_mass.input
```

preflight 应从根 `PASP.input` 遍历 include graph，确认：
- `mode_mass.input` 能从候选 input package 解析到普通文件；
- include 顺序不会让另一个 `%block atom_Heff.MASS_local_mode` 先于它生效；
- 如果存在重复 mass block，按 `PASP.input` first-one-wins 规则标出真正生效的位置；
- 该文件属于当前 stage package，不是从另一个材料、另一个 local-mode basis 或 completed-run residue 中无说明复制来的。

## 包含的 block
`mode_mass.input` 应包含一个完整的：

```text
%block atom_Heff.MASS_local_mode
mass_1 mass_2 ... mass_N
%endblock atom_Heff.MASS_local_mode
```

推荐把所有质量值写在同一数据行，按当前 local-mode 顺序形成一个连续列表。不要在本文件卡中复制具体质量值。写入或修改该 block 前，必须先查 `knowledge/reference/params/atom_Heff.MASS_local_mode.md`。

## Row-count / order 一致性检查
preflight 至少应检查：
- mass 条目数量与当前 local-mode count 一致；
- mass 顺序与 `mode_def.input` / `%block local_mode.mode_definition` 的 mode 顺序一致；
- 如果实际 local modes 由上游程序扩展或以 `local_mode-*.xsf` 编号为准，质量顺序应有当前 workspace evidence 支持；
- 每个质量值是正实数，并且其来源是用户确认、材料数据、上游文件或其他权威证据；
- `mode_mass.input`、`mode_def.input`、`local_mode_PM.dat`、`J_best.dat` 和 `amp_local_mode.in` 属于同一 local-mode basis。

对于 L5 stage 2 / 3，mass basis 还必须与上游 `amp_local_mode.out -> amp_local_mode.in` handoff 的 stage identity 一致。不能只因为文件名相同就认为 mass ordering 可复用。

## L5 Cr2O3 用法
Lecture-5 Cr2O3 SLD historical example 中，`mode_mass.input` 是三阶段共同的 split include file。该 example 为其 local-mode definitions 提供一组质量值，并与同 package 的 `mode_def.input` 保持同一顺序。

这些 facts 只说明文件角色和一致性检查方向。运行时 agent 不得把 Cr2O3 example 的 mode 数、Cr / O 质量值排列、stage package 布局或材料自由度当作当前用户任务的默认设置。

## Reference-before-write
准备创建、覆盖或修改 `mode_mass.input` 时：
- 先确认当前 `mode_def.input` 或内联 `local_mode.mode_definition` 的有效版本和 mode 顺序；
- 先读 `params/atom_Heff.MASS_local_mode.md`，确认质量条目的语义和取值规则；
- 若质量值来自材料相对原子质量、有效质量计算或用户提供表，应在 candidate README / preflight evidence 中记录来源；
- 如果质量个数、顺序或来源无法确认，只能保留为 draft / candidate，不能提升为 formal `input/` 或派生 run。

## 常见误区
- 只按元素种类写少数几个质量值，而不是按 local-mode count 逐 mode 提供。
- 把质量值写成每行一个 mode，但没有当前 PASP build / reference 证明这种写法被正确读取；本 skill 的 canonical 写法是同一数据行连续列出。
- 修改 `mode_def.input` 后没有同步修改 mass 条目数量或顺序。
- 把 Cr2O3 example 的质量值、mode 数或排列顺序当作其他材料默认值。
- 在 `PASP.input` 或 include graph 中保留多个 `atom_Heff.MASS_local_mode` block，导致修改了不可达重复项。
- 复用旧 `mode_mass.input`，但当前 `local_mode_PM.dat`、`J_best.dat` 或 `amp_local_mode.in` 来自另一套 local-mode basis。

## Verifier expectations
read-only `input-preflight` 对包含 `mode_mass.input` 的 package 应报告：
- `PASP.input` include graph 中 `mode_mass.input` 的解析路径和生效位置；
- 文件中是否存在完整 `%block atom_Heff.MASS_local_mode`；
- mass 条目数量、正实数取值、来源证据和顺序检查结果；
- 与 `mode_def.input`、`local_mode_PM.dat`、`J_best.dat`、`amp_local_mode.in` 的同基底风险；
- 哪些结论来自当前 workspace evidence，哪些仍需要用户确认。

Verifier 不应替用户选择质量值、有效质量计算方法、local-mode order 或材料参数。

## 相关条目
- `params/atom_Heff.MASS_local_mode.md`
- `topics/PASP.input.md`
- `topics/MD.input.md`
- `files/mode_def.input.md`
- `files/local_mode_PM.dat.md`
- `files/J_best.dat.md`
- `files/amp_local_mode.in.md`

## 来源章节
- 3.1.6 附属文件 MD.input：分子动力学模拟相关设置 (`block atom_Heff.MASS_local_mode`)
- `mode_mass.input` 文件名来自本仓库 Lecture-5 examples 的 split include pattern；官方语法权威仍是 `atom_Heff.MASS_local_mode` block reference。
