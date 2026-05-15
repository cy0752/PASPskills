# Fitting_Settings.txt

## 文件作用
用于 `Model Fitting_one_order` 中控制 MLMCH 拟合流程与搜索策略的各项设置。

## 何时需要
在使用 `Model Fitting_one_order` 拟合哈密顿量参数时使用；若缺省，则程序按默认设置运行。

## 关键字段/内容
文档强调逐行读取，顺序固定。除第 3 行读 4 个数据外，其余行通常只读行首数据，后面文字只是注释。

核心设置包括：
- `I_Read_Settings`
- `I_CONVERT_TO_ONE_ORDER`
- `N_UPBOUND_TOTAL,N_UPBOUND_X,N_UPBOUND_THETA,COMBINE_TYPE`
- `I_GIVE_PREDICT`
- `I_ONLY_PREDICT`
- `I_CHECK_SELFPREDICT`
- `MAX_Nncheck_BY_Nn`
- `I_SET_TERM_VALUE`
- `I_HAVE_KEEP_TERM`
- `I_HAVE_SKIP_TERM`
- `I_CHANGE_WEIGHT`
- `I_CHECK_SAMEDATA`
- `I_CHECK_DATA`
- `CHECK_DATA_ACCURACY`
- `I_RANDOM_CHANGE_DATA`
- `I_AUTOINIT`
- `SEARCH_TYPE`
- `I_SET_TERM_DEPENDENT`
- `SHOW_STDOUT`
- `BETA_WEIGHT(Bw)`

### `I_CHECK_DATA`
`I_CHECK_DATA` 控制拟合阶段是否检查数据变量中的特殊关系。当前模板注释建议通常取 `1`；处理已经检查过的数据时可能取 `0`。

基于 L3 服务器实跑，`I_CHECK_DATA=1` 时如果 PASP 检测到成比例或冗余变量，拟合日志可能出现 `WARNING ::: NEED TO REWRITE DATA::`，随后程序会在当前运行目录内重写 `Fitting_Dataset.txt` 和 `Fitting_Data_for_prediction.txt`，并减少用于拟合的变量维度。重写原因可查 `Data_Special_Properties_<原始维度>.txt`，变量映射可查 `Data_Variables_Mapping_(1st Reducing)_<原始维度>.txt`。

这个行为属于 `Model Fitting_one_order` 的数据检查阶段，不代表上游 `convert_data.py` 应该主动删除 `ene_symbol` 特征。排查列数变化时，应区分：
- 运行前列数不匹配：优先检查是否混用了不同截断、SOC 或保留项设置下的数据链。
- 运行后列数变少：优先检查 `log.out`、`I_CHECK_DATA`、`Data_Special_Properties_*.txt` 和变量映射文件。

## 注意事项
- 不允许任意调换顺序、增减行数
- 只读取每行前部有效数据，后面注释可忽略
- `I_HAVE_KEEP_TERM=1` 时会读取 `Fitting_Set_Term_Keep.txt`
- `I_HAVE_SKIP_TERM=1` 时会读取 `Fitting_Set_Term_Skip.txt`
- 强制保留或跳过项之前，应先和用户确认这些项的编号来源；不要跨不同数据链或不同 run 复用编号
- 多数内部算法细节项建议保持默认值
- `SHOW_STDOUT` 虽可输出更多信息，但会明显拖慢速度，文档建议通常取 `0`
- 运行后会自动生成 `Fitting_Settings_Save.txt`，可用来查看实际采用的完整设置

## 最小示例
正式使用时应保持文档规定的完整逐行结构。

## 来源章节
- 3.8 `Fitting_Settings.txt`
- 锚点：`#fitting-settings-txt`
