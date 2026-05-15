Lecture 3 拟合阶段参考模板。

包含：
- `PASP.input`：切换到 `Model Fitting_one_order`
- `Fitting_Settings.txt`：拟合策略模板
- `Fitting_Set_Lambda.txt`：lambda 扫描模板
- `Fitting_Set_Term_Keep.txt`：强制保留项模板
- `Fitting_Dataset.txt`：数据集入口占位模板
- `Fitting_Data_for_prediction.txt`：预测集占位模板
- `convert_info.txt`：数据转换控制模板
- `slurmpasp.sh`：作业提交脚本模板

注意：
- 这套模板的目的，是让用户在没有原始 examples 目录时，仍能把拟合阶段搭起来。
- 本模板故意不提供占位 `cell.str`。当前 `PASP.input` 仍然 `%include cell.str`，所以正式 `4.fit/input/` 和实际 `runs/<run-id>/` 必须从共享基底或上游已验证目录复制真实 `cell.str` 后才能通过 preflight。
- 不要创建注释型、零体积或空结构的 `cell.str` 占位文件来“补齐模板”。缺少真实 `cell.str` 应在 preflight 阶段 fail，而不是运行到 PASP 后才报错。
- 其中 `Fitting_Dataset.txt` 和 `Fitting_Data_for_prediction.txt` 强依赖你自己的数据组织方式，因此这里保留为占位模板。
- 生成真实数据集时，若用户没有指定切分，默认按 90/10 拆分当前可用连续样本，并让 `Fitting_Data_for_prediction.txt` 非空；不要默认全量训练、0 测试。
- 实际拟合 input/run 可从本目录复制其他拟合控制文件，再接入真实 `cell.str`，并用 `3.get_fitting_data/` 或对应上游 run 生成的数据集文件覆盖占位数据。
- 真正可否拟合成功，关键不只是这些文件是否存在，而是 `ene_symbol/`、`Energy.dat`、样本编号、转换规则是否严格一致。
