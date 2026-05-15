# GA全局结构搜索

## 目标
使用 GA 模块进行全局结构搜索，寻找低能结构或给定约束下的候选稳定结构。

## 适用问题
- 我想做全局结构搜索
- 我想用 GA 找低能结构
- 如何设置遗传算法搜索流程

## 输入前提
- `PASP.input`
- 结构文件
- 外部第一性原理计算相关脚本或输入
- 如需复现，可准备 `seed.in`

## 典型阶段
1. 选择随机空间群或微扰空间群思路
2. 准备 `PASP.input` 与结构输入
3. 设置种群规模、代数、交叉/突变概率
4. 若有磁性搜索需求，补充磁构型相关控制项
5. 运行 GA 搜索与外部计算耦合流程
6. 汇总低能结构并做后续筛选

## 当前步骤常见 reference 入口
- `modules/ga.md`
- `topics/PASP.input.md`
- `files/cell.str.md`
- `files/unit_cell.str.md`
- `files/seed.in.md`

## 不负责回答的内容
- `GA.population_size`、`GA.max_generation`、`GA.Pmut` 等字段逐项定义
- 具体 block 和默认值
这些应转给 reference。