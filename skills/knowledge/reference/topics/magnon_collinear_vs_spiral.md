# magnon: collinear vs spiral input contract

## 适用范围
本 topic 用于 `Model magnon` 前的输入判断：当前 `spin3.in`、`SuperCell`、`spin_exchange.dat` 和 q 路径是否互相一致。

## 核心区别
collinear/FM/简单 AFM 和 spiral/大周期磁序的区别不在于 `Model` 字段；两者都走 `Model magnon`。关键差异是：

- `SuperCell` 是否需要扩到能容纳磁周期。
- `spin3.in` 是否按该超胞的全原子顺序列出。
- q 路径是否仍代表用户想看的 BZ 路径。

## FM / collinear 情况
通常可以使用较小的 `SuperCell`，但仍必须检查：

```text
rows(spin3.in, nonempty) = NumberOfAtoms(cell.str) * det(SuperCell)
```

不能因为是 FM 就省略非磁性原子行；非磁性原子应保留为零向量。

## Spiral / 大磁周期情况
必须先确认 `SuperCell` 能表达磁周期，再写 `spin3.in`。如果 `spin3.in` 来自 `Spin_lattice_interaction` 的 `spin3_lowest.out`，它的行数和原子顺序通常已经对应上游 run 的超胞；下游 magnon 必须使用兼容的 `cell.str` + `SuperCell`，不能只复制 `spin3.in` 而另改超胞。

## spin_exchange.dat 限制
`magnon` 使用 `spin_exchange.dat` 时，尾部的 fourth-order / higher-order count 必须为 `0`。

原因：
- `spin_exchange.dat` 的读取顺序是 J 矩阵、`dJ/du`、SIA、DM、四阶项。
- PASP 源码会读取四阶项块；但当前 `magnon` workflow 不把四阶纯自旋相互作用纳入 LSWT 输入契约。
- 非零四阶项容易让从 `Spin_lattice_interaction` 借来的文件变成不适合 magnon 的输入。

## q 路径
默认 `spinw` legacy q-path 模式读取 `%block qpoints.magnon` 的两行端点，并用 `number_of_qpoints` 做线性插值。

写入规则：
- `%block qpoints.magnon` 必须有起点和终点两行。
- `number_of_qpoints` 对线段计算应至少为 2。
- 多段路径要分段跑或由脚本分段改端点后拼接输出。

## Preflight 必查
- `PASP.input` 是 `Model magnon`。
- `Read_init_spin T` 时 `spin3.in` 存在。
- `spin3.in` 非空数据行数等于 `NumberOfAtoms(cell.str) * det(SuperCell)`。
- `spin_exchange.dat` 最后的 higher-order count 为 0。
- q 路径端点和 `number_of_qpoints` 已由用户确认，不从 FM/spiral 讲义例子借。

## 常见错误
- 把上游 `Spin_lattice_interaction` 的含四阶项 `spin_exchange.dat` 直接喂给 magnon。
- 只改 `SuperCell` 来匹配行数，却没有确认磁周期。
- 用 `wc -l spin3.in` 时把源码写出的末尾空行也算进去；应统计非空数据行。
- 多段路径拼接时重复端点，导致图上高对称点附近多一行。

## 来源
- `knowledge/reference/files/spin3.in.md`
- `knowledge/reference/files/spin3_lowest.out.md`
- `knowledge/reference/files/spin_exchange.dat.md`
- `knowledge/reference/params/qpoints.magnon.md`
- 源码审计：`Latticemodel/src/spin_lat.F90`, `Latticemodel/src/spinw.f90`, `Latticemodel/src/output_sub.F90`
