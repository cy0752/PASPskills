# 紧束缚模型

## 目标
构建并使用 TB / SKTB / GSDTB 等紧束缚模型，分析能带、相互作用或平带相关性质。

## 适用问题
- 我想做 TB 模型
- 我想做 SKTB 或 GSDTB
- 如何设置 hopping 并分析能带
- 我想做平带或 CLS 分析

## 输入前提
- `PASP.input`
- 结构信息
- 轨道与 hopping 相关设置

## 典型阶段
1. 确定使用自定义 TB、SKTB 还是 GSDTB
2. 准备轨道与 hopping 相关输入
3. 在 `PASP.input` 中设置 TB 模块
4. 运行模型并检查矩阵维度、参数格式与输出结果
5. 根据任务继续做能带、磁各向异性或平带分析

## 当前步骤常见 reference 入口
- `modules/tb.md`
- `topics/PASP.input.md`

## 不负责回答的内容
- `USE_Slater_Koster_Model`
- `block Hop_Parameters`
- `block Slater_Koster_Hop_Parameters`
- 具体矩阵格式和字段默认值
这些应转给 reference。