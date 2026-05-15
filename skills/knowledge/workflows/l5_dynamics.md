# 动力学模拟

## 目标
使用 MD / 自旋动力学 / LLG 相关设置，研究体系随时间的演化、响应与弛豫过程。

## 适用问题
- 我想做 MD
- 我想做自旋动力学或 LLG
- 我想模拟电滞回线
- 我想做自旋-晶格弛豫

## 输入前提
- 已建立好的 effective Hamiltonian 或相关模型
- `PASP.input`
- `MD.input`
- 相关模型或电荷文件

## 典型阶段
1. 确认当前模型支持 MD
2. 准备 `MD.input`
3. 设置时间步长、总时长、阻尼与温度条件
4. 如涉及自旋自由度，选择 `SLD.mode` 与 `LLG.method`
5. 运行动力学模拟
6. 检查时间序列输出、响应曲线或弛豫结果

## 当前步骤常见 reference 入口
- `topics/MD.input.md`
- `topics/PASP.input.md`
- `files/Zeff.dat.md`
- `files/elastic.dat.md`
- `files/spin_strain.dat.md`

## 不负责回答的内容
- `MD.Delta_t`、`LLG.method`、`LLG.damping` 等字段定义
- 文件格式和默认值
这些应转给 reference。