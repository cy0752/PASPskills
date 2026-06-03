# TB.H_spin_expand

## 含义

GSDTB branch 中开启显式包含自旋的扩展哈密顿量。Lecture-7 将它作为通用自旋依赖紧束缚模型输入的一部分。

## 默认值

未在当前 reference 中建立独立默认值；写入前需要以源码、用户权威输入或当前 example branch 为依据确认。

## 取值

T/F

## 何时使用

- `TB.find_H_form T` 的 GSDTB / spin-dependent Hamiltonian form search 中，用户确认需要显式 spin-expanded Hamiltonian 时。

## 注意事项

- 需要和 `TB.full_SOC`、`GSD_TB_Spin_direction`、`TB.H_indep_var`、spin/SOC 设置共同验证。

## 来源

- Lecture-7 GSDTB example.
- Source audit: `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/TB_H_symmetry.f90`.

