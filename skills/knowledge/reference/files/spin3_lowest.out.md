# spin3_lowest.out / relax-spin3_lowest.out

## 文件作用
`Spin_lattice_interaction` 找到的全局最低能量自旋构型。它是把 PTMC 结果接给 `Model magnon` 的首选 handoff 文件。

## 何时产生
- `spin3_lowest.out`：PTMC 结束后，PASP 汇总各 MPI rank 的最低能量态，在全局最低能量所在 rank 写出。
- `relax-spin3_lowest.out`：`spin_lat.relax_str T` 且 CG 松弛路径成功时，在松弛后再次选择全局最低能量态并写出。

源码位置：
- `Latticemodel/src/output.F90`：选择全局最低节点并写 `spin3_lowest.out` / `relax-spin3_lowest.out`
- `Latticemodel/src/output_sub.F90`：`write_spin_input` 负责具体格式

## 格式
与 `spin3.in` 相同，每个原子一行：

```text
ia sx sy sz
```

源码写格式为 `I6,3f12.8`，并在文件末尾额外写一个空行。校验行数时应统计非空数据行，而不是直接信任 `wc -l`。

## 行数规则
非空数据行数必须等于当前 run 中 PASP 实际超胞的原子数：

```text
nonempty_rows = NumberOfAtoms(cell.str) * det(SuperCell)
```

该文件包含全原子行。非磁性原子通常是零向量，不能因为后续 `magnon` 只求磁性子空间就删行。

## 下游使用
- 默认 handoff：`spin3_lowest.out` 复制为 magnon run 的 `spin3.in`。
- 若用户明确要使用 CG-relaxed 基态，且日志同时满足 `CG finish` 与 `PASP is finished gracefully.`，并且 `relax-spin3_lowest.out` 存在，则可优先复制 `relax-spin3_lowest.out` 为 `spin3.in`。
- 若 `spin3_lowest.out` 缺失，可结合能量记录和 `node_N_spin.out` 找备选；不要默认使用 `node_N_finalspin.out`，它是末态，不保证最低能。

## 注意事项
- 不能把历史 run 的 `spin3_lowest.out` 当成当前目录事实；必须来自当前目标 run 或用户明确指定的上游 run。
- 复制为 `spin3.in` 前必须记录来源 run、来源文件名和行数校验结果。
- 旧 PASP build 曾在 CG/postprocess 路径报错；不要仅凭 `spin3_lowest.out` 存在就声称 CG 成功。

## 来源章节
- PASP 输出约定：`spin3.in` 同格式
- 源码审计：`Latticemodel/src/output.F90`, `Latticemodel/src/output_sub.F90`
