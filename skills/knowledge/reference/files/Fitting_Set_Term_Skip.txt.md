# Fitting_Set_Term_Skip.txt

## 文件作用
在 `Model Fitting_one_order` 中指定必须跳过的拟合项，使搜索过程不选择这些项。

只有当 `Fitting_Settings.txt` 中 `I_HAVE_SKIP_TERM` 设为 `1` 时，PASP 才会读取这个文件。

## 何时需要
- 某些项已经被确认为不合理、不可解释或不应进入当前模型
- 某些项会导致搜索不稳定，且用户已经确认需要排除
- 用户希望在一轮对比实验中固定排除一组候选项

如果只是第一次打通流程，通常不应主动启用强制跳过项。强制跳过会改变搜索空间，必须先和用户确认依据。

## 文件格式
第 1 行写强制跳过项的数量 `K`。

后续 `K` 行每行两个整数：

```text
<row_index> <term_index>
```

- `row_index` 从 `1` 开始，必须按顺序连续写到 `K`
- `term_index` 是要强制跳过的项编号
- `term_index = 0` 表示常数项；通常不要跳过常数项，除非用户明确要求并理解后果
- 非零 `term_index` 会按当前拟合内部变量映射处理，因此必须来自同一套数据链、拟合报告或变量映射，不能跨 run 混用

## 最小示例
```text
2
1 18
2 42
```

## 注意事项
- 启用前必须同时检查 `Fitting_Settings.txt` 中 `I_HAVE_SKIP_TERM=1`
- 不要把同一个 `term_index` 同时写进 `Fitting_Set_Term_Keep.txt` 和 `Fitting_Set_Term_Skip.txt`
- 如果 PASP 已经因 `I_CHECK_DATA=1` 重写过数据，项编号要以当前 run 的报告、`Data_Variables_Mapping_*` 或后续确认后的编号为准
- 强制跳过项会影响模型搜索结果；只有当跳过理由清楚时才使用

## 来源依据
- `Model Fitting_one_order` 读取逻辑
- `Fitting_Settings.txt` 中 `I_HAVE_SKIP_TERM` 的文件依赖
