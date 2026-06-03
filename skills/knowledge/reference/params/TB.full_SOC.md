# TB.full_SOC

## 含义

GSDTB / spin-dependent TB branch 中开启 full SOC 处理的控制项。Lecture-7 将它与 `TB.find_H_form`、`TB.H_spin_expand` 一起用于通用自旋依赖紧束缚模型。

## 默认值

未在当前 reference 中建立独立默认值；写入前需要以源码、用户权威输入或当前 example branch 为依据确认。

## 取值

T/F

## 何时使用

- 用户明确选择 full-SOC GSDTB branch 时。

## 注意事项

- 不要因为 example 有 `TB.full_SOC T` 就自动给普通 SKTB 或 custom TB 打开。
- 需要和 `Spin_values`、`Sn_basis`、`use_rotation_matrix`、SOC magnitude/settings 一起检查。

## 来源

- Lecture-7 GSDTB example.
- Source audit: `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/TB_H_symmetry.f90`.

