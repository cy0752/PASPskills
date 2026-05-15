# Fitting_Set_Term_Keep.txt

## 文件作用
在 `Model Fitting_one_order` 中指定必须保留的拟合项。

只有当 `Fitting_Settings.txt` 中 `I_HAVE_KEEP_TERM` 设为 `1` 时，PASP 才会读取这个文件。

## 何时需要
- 用户有明确物理先验，认为某些项必须出现在模型中
- 已从前一轮拟合报告、变量映射或人工分析中确定某些关键项不能被搜索过程删除
- 为后续 MC / MD 保留可解释的关键相互作用项

如果只是第一次打通流程，通常不应主动启用新的强制保留项，除非模板或用户目标已经明确要求。

## 文件格式
第 1 行写强制保留项的数量 `K`。

后续 `K` 行每行两个整数：

```text
<row_index> <term_index>
```

- `row_index` 从 `1` 开始，必须按顺序连续写到 `K`
- `term_index` 是要强制保留的项编号
- `term_index = 0` 表示常数项
- 非零 `term_index` 会按当前拟合内部变量映射处理，因此必须来自同一套数据链、拟合报告或变量映射，不能跨 run 混用

## 最小示例
```text
3
1 0
2 6
3 12
```

## 注意事项
- 启用前必须同时检查 `Fitting_Settings.txt` 中 `I_HAVE_KEEP_TERM=1`
- 不要把同一个 `term_index` 同时写进 `Fitting_Set_Term_Keep.txt` 和 `Fitting_Set_Term_Skip.txt`
- 如果 PASP 已经因 `I_CHECK_DATA=1` 重写过数据，项编号要以当前 run 的报告、`Data_Variables_Mapping_*` 或后续确认后的编号为准
- 如果用户只是问逐项物理含义，优先回到拟合报告、变量映射或相关 reference，不要仅凭编号猜测

## 来源依据
- `Model Fitting_one_order` 读取逻辑
- Lecture 3 拟合模板中的 `Fitting_Set_Term_Keep.txt`
