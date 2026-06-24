# isaAB

## 含义
指定参与当前相互作用分析的两类元素。这里的“两类”来自 `Z_values` 的元素顺序编号，不是原子序数。

在 `find_J_path_sym`、magnon、spin-lattice 这类会用 `alloy_site(isa, isaAB)` 判断活动磁性位点的流程中，`isaAB = A B` 的直接效果是把 species id 等于 `A` 或 `B` 的位点纳入活动集合。因此当 `A` 和 `B` 是两个不同磁性元素时，后续 pair / cluster 搜索会覆盖这两个元素集合内部及二者之间的相互作用，而不是只覆盖交叉的 `A-B` pair。

## 写法
```text
%block isaAB
1 2
%endblock isaAB
```

## 格式
- 两个整数
- 取值为 0 或某元素编号
- 元素编号来自 `Z_values` 的顺序编号，从 1 开始
- 若两个值不同，例如 `1 2`，活动集合为 species 1 和 species 2；相关 workflow 可能同时产生 1-1、1-2、2-2 相互作用项
- 若两个值相同，例如 `2 2`，只选 species 2 这一类元素

## 默认值
```text
0 0
```

`0 0` 是程序默认行为，不应在多元素磁性体系中被解释为“明确分析所有目标磁对”的安全写法。多磁性元素体系应显式写出目标磁性元素的 species id，并在 workflow 记录它们对应的 `Z_values` 元素。

## 何时使用
- 做交换路径分析时
- 需要限定哪些元素参与 pair / cluster / spin interaction 搜索时
- 多磁性元素体系需要同时覆盖这些磁性元素内部和彼此之间相互作用时

## 注意事项
- `isaAB` 的编号不是原子序数，而是 `Z_values` 中的顺序编号
- 若 `Z_values` 顺序有误，`isaAB` 即使写法正确，也会分析错对象
- 对 `Z_values = 25 26 8` 的 Mn-Fe-O 体系，Mn 是 1、Fe 是 2、O 是 3。若要分析 Mn-Mn、Mn-Fe 和 Fe-Fe 磁性相互作用，写 `isaAB = 1 2`；不要写 `0 0`，也不要误以为 `1 2` 只分析 Mn-Fe 交叉 pair。
- 程序可以正常运行，但结果未必是你真正想研究的 pair

## 常见误区
- 直接把原子序数写进 `isaAB`
- 忘记先确认 `Z_values` 中目标元素排第几
- 把 `0 0` 当成“所有磁性 pair”的显式声明
- 把 `isaAB = 1 2` 误解成只保留 species 1 与 species 2 之间的交叉 pair，而漏掉 1-1 / 2-2 磁性 pair 的覆盖

## 相关条目
- `topics/PASP.input.md`
- `params/Z_values.md`
- `params/Spin_values.md`
- `files/cell.str.md`

## 来源章节
- 官方文档: `3.1.2.4 block isaAB`
- 来源页面: https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#block-isaab
