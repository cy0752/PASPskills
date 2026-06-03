# SYMPREC

## 含义
`SYMPREC` 设置 PASP 内部对称性判断使用的数值容差。源码中全局读取后会进入 `sym_prec` 模块的 `tiny`，运行日志通常会打印：

```text
tiny in sym_prec is set to be: ...
```

它会影响依赖结构对称性、等价位点、代表相互作用、对称化或空间群/点群识别的流程。

## 写法
```text
SYMPREC 1.0d-5
```

## 默认值
通用输入读取路径中默认值为 `1.0d-5`。

注意：GA 结构初始化相关路径中存在特殊处理，若未显式写 `SYMPREC`，源码会以 `tol_len_structure` 作为 fallback，并按当前长度尺度归一化后更新 `sym_prec.tiny`。因此 GA 相关任务不能把通用默认值机械套到所有内部路径。

## 取值
正实数或非负实数容差值。实际应按当前结构精度、畸变幅度和工作流目标确认。

## 何时使用
- 当 workflow 需要识别结构对称性、等价位点、pair / group 代表元、对称化或空间群/点群相关信息时。
- L8 KNB / spin-lattice ion-strain 输入中若显式出现 `SYMPREC`，preflight 应把它作为结构 / symmetry control 检查。
- L3 / structure-analysis 场景中若使用外部对称性工具，也应记录所用 `symprec`，但外部工具的 `symprec` 不是自动等同于 PASP 的运行值，除非用户明确要求一致。

## 注意事项
- 不要把例子里的 `SYMPREC` 当成当前材料默认值。它控制容差，过紧可能找不到应有对称关系，过松可能错误合并本应不同的结构/位点。
- 修改前应确认当前任务是想更严格地区分微小畸变，还是想容忍数值噪声。
- 输出验证时可以用 `log.out` 中的 `tiny in sym_prec is set to be:` 和 `PASP.used_info` 中的 `SYMPREC` 辅助确认同 run 生效值，但 `PASP.used_info` 在部分 run 中可能很简略，不能单独作为完整验证证据。
- 如果对称性判断变化会影响 GKNB local axis、pair 搜索、`fig.mdist` 范围、spin-lattice response 文件对应关系或 representative-site mapping，应把 `SYMPREC` 取值作为用户确认项记录。

## 相关条目
- `topics/PASP.input.md`
- `params/SuperCell.md`
- `params/fig.maxk.md`
- `params/fig.mdist.md`
- `topics/symmetry_representative_sites.md`

## 来源
- PASP source audit: `read_input.F90` reads `SYMPREC` with default `1.0d-5`.
- PASP source audit: `init_sym_prec.f90` passes the read value to `update_sym_prec`.
- PASP source audit: `update_sym_prec.f90` updates `sym_prec.tiny` and prints `tiny in sym_prec is set to be:`.
- PASP source audit: `GA_str_init.f90` has a GA-specific fallback / normalization path.
