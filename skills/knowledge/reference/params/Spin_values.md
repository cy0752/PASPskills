# Spin_values

## 含义
设置各元素对应的自旋或磁矩尺度。

## 写法
```text
%block Spin_values
0 2 0
%endblock Spin_values
```

## 默认值
全部为 1。

## 取值
- 非负实数

## 常见理解
- 常按各元素电子总自旋量子数的二倍填写
- 也常作为近似磁矩大小使用
- 在一些有效哈密顿量流程中，磁性原子常按归一化自旋写为 2

## 何时使用
- 交换路径分析
- 有效哈密顿量建模
- MC / CG 相关任务
- 涉及磁矩尺度或 Zeeman 项的任务

## 注意事项
- 这组值会影响外磁场项的实际物理尺度
- 若采用归一化自旋模型，外磁场相关输入值通常也要按比例理解
- 如果体系中只有部分元素有磁性，非磁性元素一般写 0
- 数值个数必须与当前结构的 `number_of_species` / `Z_values` 元素个数一致。三元素体系即使只有两个磁性元素，也应为非磁性元素写上 `0`，例如 `2 2 0`；不能只写 `2 2`。

## 常见误区
- 把非磁性元素也写成与磁性元素相同的值
- 把它当作与 `isaAB` 相同的元素编号字段
- 忽略它和外磁场项之间的耦合关系
- 三元素体系漏写非磁性元素的 `0`，导致 PASP 继续把 `%endblock Spin_values` 当成数值读取并触发 Fortran list-directed I/O syntax error。

## 相关条目
- `topics/PASP.input.md`
- `params/Z_values.md`
- `params/isaAB.md`

## 来源章节
- 官方文档: `3.1.2.5 自旋大小与外磁场设置`
- 来源页面: https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id5
