# TB.localized_state

## 含义

开启 TB flat-band compact localized state 搜索。源码 `TB.f90` 中若该项为 true，会调用 `TB_localized_state` 后停止普通 TB band/DOS 计算流程。

## 默认值

F

## 取值

T/F

## 何时使用

- 已经有当前 run 的 TB/SKTB band evidence，并希望搜索目标 flat band 对应的 compact localized state 时。

## 相关设置

- `TB.center_atom_localized`
- `TB.rcut_localized`
- `TB.eigen_localized`

## 注意事项

- 这是单独的 CLS 搜索目标，不应与普通 band/DOS production run 混为一个输出验证目标。
- 成功证据应包括 `lgood: T` 或等价日志，以及同一 run 的 `local_cluster.xyz` / `local_cluster.vesta`。

## 来源

- Lecture-7 flat-band CLS example.
- Source audit: `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/TB.f90` and `TB_flat_band.f90`.

