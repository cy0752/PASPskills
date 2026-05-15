# PT.nblk_T

## 含义
在并行回火 PTMC 中，一个 PT iteration 包含多少个温度副本交换步。

源码中的运行日志会把它和 `PT.niter`、`nblk` 一起打印：

```text
PT_niter,ns_blk,nblk,nblk_T
One PT iteration contains nblk_T exchange steps
One exchange step contains nblk MCS steps
```

## 默认值
10。

源码位置：
- `Latticemodel/src/PTMC.F90`：`fdf_global_get(nblk_T,'PT.nblk_T',10)`

## 取值
非负整数；生产计算通常需要按体系尺寸、温度区间、统计误差和算力预算增大。

## 与其他字段的关系
- `PT.niter`：外层 PT iteration 数；总交换步约为 `PT.niter * PT.nblk_T`。
- `nblk`：每两个交换步之间执行多少个 MCS。
- `nbeg_blk`：从第几个交换步之后开始进入统计；源码条件是 `nex > nbeg_blk`，所以 `nbeg_blk` 过大时有效统计样本会变少。
- `PT.n_binsize`：若 bin 数不足，运行日志可能提示使用更小的 bin size 或更大的 `PT.nblk_T`。

## 何时使用
- `Model Spin_lattice_interaction`
- 需要增加 PTMC 采样长度、改善热力学统计、减少 bin-method warning 时

## 注意事项
- 修改前必须确认用户的科学目标和算力预算；不要仅凭讲义例子的数值替换当前任务。
- `nbeg_blk` 不应大于等于总交换步数，否则统计阶段可能没有有效样本。
- 增大该值会直接增加 wall time。

## 来源章节
- PASP 文档：3.1.5.3 PTMC 模拟步数与统计相关设置
- 源码审计：`Latticemodel/src/PTMC.F90`, `Latticemodel/src/PTMC_measure.F90`
