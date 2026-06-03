# Ppair.xsf

## 文件作用
`Ppair.xsf` 是 L8 pure electronic KNB / gKNB 分支的同 run 可视化输出，用于显示 pair-center 上的 pair polarization vectors。

## 何时出现
- `Model KNB` 的 inter-site KNB / gKNB path 计算 pair polarization 时。
- 当前源码中 `inter_site_P` 会调用 `write_Ppair(..., 'Ppair.xsf')`。

## 关键字段或内容
`Ppair.xsf` 使用 XSF `CRYSTAL` / `PRIMVEC` / `PRIMCOORD` 结构：
- `PRIMVEC`：当前结构晶格矢量，单位 Angstrom。
- `PRIMCOORD`：原子/伪原子数量和坐标。
- 每个坐标行后带 3 个向量分量。

当前源码写法：
- 真实原子坐标来自当前结构，向量分量置为 `0 0 0`。
- 额外加入的 pair-center 伪原子坐标位于匹配 pair 的中心。
- pair-center 行的最后 3 个数是该 pair 的 polarization vector。
- 伪原子的 atomic type 使用 `max(iza)+1`，只是为了可视化区分，不代表真实元素。

## 验证用途
- 可作为 pure electronic KNB / gKNB pair-polarization 可视化证据。
- 不能单独证明 run 成功；必须结合 `log.out` 中 `PASP is finished gracefully` 和 `spin_FE: P is` / `Intersite P` 等分支极化摘要。
- 如果 input 目录已有旧 `Ppair.xsf`，不能把它当成当前 run 证据；必须确认它位于 run 目录且 mtime / 产物链与同一 run 日志一致。

## 来源
- PASP source audit: `KNB.f90` `inter_site_P`, `write_Ppair`
- L8 runtime observation: fresh pure electronic KNB runs produced same-run `Ppair.xsf`
