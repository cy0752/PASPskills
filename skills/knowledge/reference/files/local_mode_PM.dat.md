# local_mode_PM.dat

## 文件作用
保存不等价相互作用分析结果，可作为后续 `Model atomic_effective_H` 的输入文件，用于 MC、MD 等模拟，避免重复分析相互作用。

## 何时需要
- 先用 `Model Invariant` 做一次不等价相互作用分析后，供后续 MC 或 MD 使用
- 反复调用 `Model Invariant` 处理不同构型时，作为输入继续生成所需的 `*.ene_symbol`
- L3 Path B / method 6 或后续复用同一相互作用基底时，需要来自当前材料、当前共享基底的一次成功运行

## 关键字段/内容
- 通常由程序自动生成
- 作为输入使用时，需要在 `PASP.input` 中设置：`local_mode.read_interaction T`

## 注意事项
- 通常不需要手动修改，直接使用程序生成版本
- 这是一个既可输出也可再输入的中间结果文件
- 对 L3 Path A 的第一次 `local_mode.cal_para_method = 1` 随机 / 有序样本生成，不应为了先得到 `local_mode_PM.dat` 而单独预跑一次；应先确认样本数（例如 `local_mode.nstr_random`），让首轮正式运行自然生成样本特征和 `local_mode_PM.dat`

## 来源章节
- 3.6 `local_mode_PM.dat`
- 锚点：`#local-mode-pm-dat`
