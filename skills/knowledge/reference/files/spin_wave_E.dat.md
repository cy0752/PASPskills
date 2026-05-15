# spin_wave_E.dat

## 文件作用
`Model magnon` 的核心色散输出，记录每个 q 点上的线性自旋波本征值。

## 何时产生
默认 `spinw` 路径运行结束时产生。

源码位置：
- `Latticemodel/src/spinw.f90`：`OPEN(... file='spin_wave_E.dat')`

## 格式
每行对应一个 q 点：

```text
iq E_1 E_2 ... E_na_spin
```

源码写法：
- 第一列 `iq`：`I3`
- 后续 `na_spin` 列：每列 `f20.12`

`na_spin` 是磁性原子自由度数量，不一定等于 `spin3.in` 的全原子行数。

## 行数规则
- 行数应等于 `number_of_qpoints`。
- 每行本征值数量应等于当前超胞中的磁性原子数。

## 下游使用
- 单段路径：直接作为画图输入。
- 多段路径：每段各自生成 `spin_wave_E.dat`，外部脚本可拼成 `spin_wave_E_all.dat`。拼接时需要处理相邻段重复端点。
- 若出现负值/虚频，优先回查 `spin3.in` 基态、`SuperCell` 周期和 `spin_exchange.dat`，不要通过改 q 路径掩盖。

## 注意事项
- PASP 写的是 q 点编号，不写高对称点标签；标签和累计路径长度需要由外部画图脚本维护。
- 单位以当前 PASP build/log 为准；workflow 不应从历史例子硬编码单位。

## 来源章节
- PASP 文档：3.1.11 线性自旋波色散计算常用设置项
- 源码审计：`Latticemodel/src/spinw.f90`
