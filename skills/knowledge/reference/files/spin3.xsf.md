# spin3.xsf

## 文件作用
`spin3.xsf` 是 PASP 将当前结构和自旋 / 向量场写成 XSF 的可视化输出。在 L8 pure electronic KNB / gKNB 分支中，它用于显示同 run 采用的 spin configuration。

## 何时出现
- `Model KNB` 的 inter-site KNB / gKNB path 当前会写出 `spin3.xsf`。
- 其他 PASP 模块也可能通过同一个 XSF writer 写出不同名称的 spin / vector XSF；本卡只说明 L8 `spin3.xsf` 用法。

## 关键字段或内容
当前 PASP writer 使用 XSF `CRYSTAL` / `PRIMVEC` / `PRIMCOORD` 结构：
- 坐标单位是 Angstrom。
- 每个 `PRIMCOORD` 行包含 atomic type、x/y/z 坐标和 3 个向量分量。
- 对 L8 KNB `spin3.xsf`，最后 3 个分量是该 atom 的 spin vector。

## 验证用途
- 可作为 KNB / gKNB run 的同 run spin-configuration 可视化证据。
- 不能替代 `spin3.in` 行序 provenance；它是运行后输出，不是输入确认。
- 不能单独证明 KNB run 成功；必须结合 `log.out` 正常完成和分支极化摘要。
- 如果目标目录已有历史 `spin3.xsf`，必须通过 run 目录、mtime 或日志产物链确认它属于当前 run。

## 来源
- PASP source audit: `KNB.f90` `inter_site_P`; `xsf.f90` `write_xsf_spin_gen`
- L8 runtime observation: fresh pure electronic KNB runs produced same-run `spin3.xsf`
