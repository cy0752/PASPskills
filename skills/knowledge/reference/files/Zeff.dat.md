# Zeff.dat

## 文件作用
为 `Model Spin_lattice_interaction` 计算自旋序诱导铁电极化时提供 Born 有效电荷张量数据。

## 何时需要
做自旋-晶格耦合导致的极化分析，且需要把离子位移贡献转成极化贡献时使用。

## 关键字段或内容
- 以 `ion N` 标记第 N 个离子
- 每个离子后通常给出 3 行，分别对应 `dF/dEx`、`dF/dEy`、`dF/dEz` 的三个分量
- 实质上是每个离子的 Born 有效电荷相关张量信息

## 注意事项
- 读取按固定字符宽度严格执行，格式不齐会读错
- 数据通常从 VASP 的 DFPT 计算输出 `OUTCAR` 中截取

## 来源章节
- 3.12 `Zeff.dat`
- 锚点：`#zeff-dat`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#zeff-dat>
