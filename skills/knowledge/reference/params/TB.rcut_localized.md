# TB.rcut_localized

## 含义

CLS 搜索的局域截断半径。Lecture-7 说明可从小到大尝试，半径越大计算耗时越久。

## 默认值

`0.0d0`

## 取值

非负实数。

## 何时使用

- `TB.localized_state T` 时限定 localized-state 搜索范围。

## 注意事项

- 该值是用户需要确认的搜索策略，不是 flat-band workflow 的通用默认值。
- 如果没有当前 flat-band evidence 和用户确认，不应自动填写。

## 来源

- Lecture-7 flat-band CLS example.
- Source audit: `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/TB_flat_band.f90`.

