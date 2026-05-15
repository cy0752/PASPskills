# isaAB

## 含义
指定研究哪两类元素之间的相互作用。

## 写法
```text
%block isaAB
2 2
%endblock isaAB
```

## 格式
- 两个整数
- 取值为 0 或某元素编号
- 元素编号来自 `Z_values` 的顺序编号，从 1 开始

## 默认值
```text
0 0
```

## 何时使用
- 做交换路径分析时
- 只关心某两类元素之间的 pair 或相互作用时

## 注意事项
- `isaAB` 的编号不是原子序数，而是 `Z_values` 中的顺序编号
- 若 `Z_values` 顺序有误，`isaAB` 即使写法正确，也会分析错对象
- 程序可以正常运行，但结果未必是你真正想研究的 pair

## 常见误区
- 直接把原子序数写进 `isaAB`
- 忘记先确认 `Z_values` 中目标元素排第几

## 相关条目
- `topics/PASP.input.md`
- `params/Z_values.md`
- `files/cell.str.md`

## 来源章节
- 官方文档: `3.1.2.4 block isaAB`
- 来源页面: https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#block-isaab
