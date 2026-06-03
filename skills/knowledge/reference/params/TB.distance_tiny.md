# TB.distance_tiny

## 含义

设置 SKTB 距离匹配时使用的距离容差。源码中 `SK_TB.f90` 对 distance-based Slater-Koster hopping path 使用该值比较实际距离与输入距离。

## 默认值

`1.0d-3`

## 取值

正实数。

## 何时使用

- `Hop_Parameters_specified_using_dis T` 时，距离匹配因结构数值精度导致找不到或误判 hopping path，需要用户确认容差策略时。
- Lecture-7 flat-band example 中使用较大的值用于识别目标跃迁距离，但这只是示例设置。

## 注意事项

- 不是 hopping 强度、不是拟合参数。
- 不要把 flat-band example 里的值当作通用默认值。

## 来源

- Lecture-7 flat-band CLS example.
- Source audit: `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/read_input.F90` and `SK_TB.f90`.

