# Ylm_form

## 含义

控制 SKTB 中 spherical / cubic / hexagonal harmonics 的形式选择。当前源码 `SK_TB_data.f90` 只实现 `Ylm_form 2`，即 cubic harmonics。

## 默认值

2

## 取值

- `1`: Ylm
- `2`: Cubic
- `3`: Hexagonal

## 何时使用

- SKTB / GSDTB branch 需要明确 harmonics convention 时。

## 注意事项

- 当前源码检查到非 `2` 会停止；runtime preflight 应阻止非 2 的 candidate 进入 submit-ready 状态，除非用户提供当前版本已支持的权威证据。

## 来源

- Source audit: `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/SK_TB_data.f90`.

