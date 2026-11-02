# Fitting_Set_Lambda.txt

## 文件作用
为 `Model Fitting_one_order` 的 MLMCH 搜索过程提供一组 λ 设置及每轮允许的最大参数个数。

## 何时需要
当不满足于默认 λ 搜索流程、希望自定义各轮 λ 值与搜索规模时使用；若采用默认 MLMCH，可省略该文件。

## 关键字段/内容
### 第 1 行：两个数据
1. 后续总共提供多少行 λ 配置
2. 从第几行开始使用

### 后续每行 3 个有效数据
1. 行编号 `I`
2. 本轮允许模型包含的最大参数个数 `Nc_p_s(I)`
3. 本轮阈值的乘法因子 `LAMBDAS(I)`，不是加性 ridge 正则化系数

## Automatic Exploration Contract

Each `LAMBDAS(I)` entry successively multiplies the regularization/search
threshold. A factor greater than 1 grows that threshold, below 1 shrinks it,
and 1 leaves it unchanged. Automatic exploration requires finite factors
strictly greater than 1 for every row; the factors themselves need not be
monotone across rows. For example, factors 1.02 and 1.01 both grow the threshold.

`Nc_p_s(I)` is the maximum retained parameter count for that round, not the full
candidate matrix width. In automatic exploration it must not exceed
`min(candidate_feature_count, 150, floor(1.5 * actual_training_rows))`.
The independent full candidate-width gate still applies before any fitting.
Run `prepare_l3.py check-fit` on the actual fit directory before every PASP run.

## 注意事项
- 以下默认设置描述为历史参考，不能用于要求乘法递增阈值的自动探索。
- 文档示例是默认设置，共 20 轮、λ 递减，最后一个 λ 为 `1.0`
- 文档特别提醒：`λ = 1.0` 的最后一轮可能明显变慢
- 若想节省时间，可把首行总轮数从 `20` 改为 `19` 或更小，跳过最后一轮
- 运行后会自动生成 `Fitting_Set_Lambda_Save.txt`，可用于导出实际默认模板

## 最小示例
```text
3 1
1 150 1.30
2 150 1.10
3 150 1.02
```

## 来源章节
- 3.9 `Fitting_Set_Lambda.txt`
- 锚点：`#fitting-set-lambda-txt`
