# GKNB_data.NNNNN

## 文件作用
`GKNB_data.NNNNN` 是 KNB / gKNB path 可写出的 per-atom pair diagnostic 文件。文件名中的 `NNNNN` 是 5 位补零 atom index，例如 `GKNB_data.00001`。

## 何时出现
- 当前源码中 `Dipole_GKNB` 和 spiral polarization path 会为参与计算的磁性 / alloy-site atom 调用 `write_GKNB`。
- 是否实际写出取决于 PASP 版本、分支和当前设置；L8 2026-06-03 fresh pure-electronic validation 中没有出现 `GKNB_data.*`，所以 verifier 不应把它作为所有 KNB runs 的硬性输出。

## 关键字段或内容
当前 `write_GKNB` 输出包含：
- `ia`：中心 atom index。
- `pos_ia`：中心 atom position。
- `cell`：用于该 diagnostic 的 cell。
- `npairKNB`：该 atom 的 KNB pair 数。
- 每个 `#Pair` 段记录：
  - `ja,ja_cell,pos_ja`
  - `GKNB` / `crd_pair`
  - `local_axis`
  - 两个 ion 的 `P_single x/y/z` 3 x 3 数据块
  - `Pint` 3 x 3 数据块
  - 当前 `Si`、`Sj`、`Si X Sj`
  - `Pint` contribution

## 验证用途
- 可用于排查 KNB / gKNB tensor、local-axis、pair mapping 和 per-pair dipole 贡献。
- 如果当前设置和 PASP 版本预期写出 `GKNB_data.*`，output validation 应确认文件属于同一 run。
- 若当前 run 未写出，但日志已有正常完成和 `spin_FE: P is` / `Intersite P` 等分支摘要，不应仅因缺少 `GKNB_data.*` 判失败，除非当前任务明确要求该 diagnostic。

## 来源
- PASP source audit: `KNB.f90` `Dipole_GKNB`, `pol_spiral`, `write_GKNB`
- L8 runtime observation: `GKNB_data.*` is version- / setting-dependent in current fresh runs
