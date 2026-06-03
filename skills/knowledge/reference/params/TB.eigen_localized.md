# TB.eigen_localized

## 含义

CLS 搜索中指定目标 flat band / localized state 对应的本征能量。

## 默认值

`0.0d0`

## 取值

实数能量值。

## 何时使用

- `TB.localized_state T` 时，用户已经从当前 run 的 band output 或其他 authoritative evidence 确认目标平带能量。

## 注意事项

- 不能把 Lecture-7 Kagome example 的目标能量复制到当前材料。
- 目标能量应来自当前 run validated output 或用户权威来源。

## 来源

- Lecture-7 flat-band CLS example.
- Source audit: `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/TB_flat_band.f90`.

