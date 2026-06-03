# TB.center_atom_localized

## 含义

CLS 搜索中指定 localized-state 搜索的中心原子编号。

## 默认值

1

## 取值

正整数原子编号。

## 何时使用

- `TB.localized_state T` 时，用户需要指定从哪个原子附近开始构造 / 搜索 compact localized state。

## 注意事项

- 编号必须对应当前结构和当前 run 的原子顺序。
- 不能从 sibling example 复制中心原子编号。

## 来源

- Lecture-7 flat-band CLS example.
- Source audit: `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/TB_flat_band.f90`.

