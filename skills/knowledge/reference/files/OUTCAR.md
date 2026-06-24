# OUTCAR

## 文件作用
`OUTCAR` 是 VASP 输出文件，不是 PASP 原生输入 / 输出文件。在 PASP skills 中，它主要作为 L2 four-state exchange、L3 Path B / DFT-data整理、GA 外部优化等流程的上游 DFT 证据。

本卡只记录 PASP workflow 会消费的稳定抽取规则；VASP INCAR 设置、电子步收敛和物理可靠性仍由用户 / DFT workflow 负责。

## 何时需要
- L2 `find_J_path_sym` 后做四态法 DFT，并从 4 个状态的 `OUTCAR` 提取总能来计算 J。
- L3 effective Hamiltonian 中，从已有 DFT 结果整理 `Energy.dat`、最终结构、最终逐原子磁矩或 Path B `distortion.*`。
- 其他 workflow 明确需要从 VASP 输出读取磁矩、结构或能量时。

## 总能量抽取规则
从 VASP `OUTCAR` 提取总能时，应使用最后一次出现的 converged `free energy TOTEN` 记录，而不是第一次出现的 `TOTEN`。

常见 shell 形态：

```text
grep "free  energy   TOTEN" OUTCAR | tail -1
```

如果匹配模式写得更宽，例如 `grep "TOTEN" OUTCAR`，仍必须取最后一条，而不是循环中见到第一条就 `break`。

## 四态法 J 的额外要求
- 同一 pair 的四个状态必须使用可比较的 DFT 设置、同一结构基准和同一能量抽取规则。
- 每个状态的 `OUTCAR` 应有收敛证据；如果最后一条 `TOTEN` 来自未收敛或异常终止的 run，不能直接进入 J 拟合。
- 计算出的 four-state J 若要写入归一化 spin 的 PASP effective-H 模型，还要按 `topics/four_state_method.md` 中的模型自旋尺度规则换算，不能直接把物理自旋尺度下的 J 写进 `J_best.dat`。

## 常见误区
- 读取第一条 `TOTEN`，得到的是初始 SCF 迭代附近的能量，可能与最终能量相差几个数量级。
- 只保存 `OSZICAR` 或脚本摘要，却没有保留足够证据说明每个 `OUTCAR` 的最终能量和收敛状态。
- 把 `OUTCAR` 最终磁矩大小直接当成 `Spin_values` 正式设置；它只能作为给用户确认的候选信息。

## 相关条目
- `topics/four_state_method.md`
- `workflows/l2_find_J_path_sym.md`
- `workflows/l3_effective_hamiltonian.md`
- `files/J_best.dat.md`
