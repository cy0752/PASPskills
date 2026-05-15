# magnon

## 模块用途
用于线性自旋波色散计算。

## 常见相关设置
- `number_of_qpoints`：一条 q 路径上的采样点数
- `block qpoints.magnon`：给出该路径的起点和终点 q 点，采用倒格矢基底下的分数坐标

## 何时使用
- 计算某条高对称路径上的 magnon 或 spin-wave 色散时使用

## 注意事项
- PASP 一次只计算布里渊区中的一条线段；多段路径通常需要分段设置和分别运行
- `block qpoints.magnon` 在实际计算中通常不可缺省

## 来源章节
- 3.1.11 线性自旋波色散计算常用设置项
- 锚点：`#id20`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id20>
