# Z_values

## 含义
给出各元素对应的数值标签，通常使用原子序数。

## 写法
```text
%block Z_values
83 26 8
%endblock Z_values
```

## 何时使用
- 几乎所有依赖元素编号的 PASP 流程都会用到
- 当后续还要使用 `isaAB`、`Spin_values` 等按元素编号解释的字段时尤其重要

## 默认行为
- 优先根据 `cell.str` 的元素名自动生成
- 若仍无法确定，则可能全部设为 1

## 注意事项
- 顺序应与 `cell.str` 中各元素首次出现顺序一致
- 元素顺序一旦错位，后续 `isaAB`、`Spin_values` 等都会跟着错位
- 在 TB 模块中，这里通常不是填原子序数，而是填该元素所考虑轨道的电子数

## 常见误区
- 只看化学式顺序，而不看 `cell.str` 里的元素首次出现顺序
- 在 TB 任务中仍按原子序数填写

## 相关条目
- `topics/PASP.input.md`
- `files/cell.str.md`
- `params/Model.md`

## 来源章节
- 官方文档: `3.1.2.3 block Z_values`
- 来源页面: https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#block-z-values
