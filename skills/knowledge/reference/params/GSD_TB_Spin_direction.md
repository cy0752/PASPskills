# block GSD_TB_Spin_direction

## 含义

GSDTB branch 中设置用于通用自旋依赖 TB Hamiltonian 的自旋方向信息。Lecture-7 示例将其与 `TB.find_H_form`、`TB.full_SOC` 和 `TB.H_spin_expand` 配套使用。

## 默认值

无通用默认值。

## 何时使用

- GSDTB / spin-dependent Hamiltonian form search。

## 注意事项

- 具体行格式和方向含义必须由当前 branch evidence、source 或用户权威说明确认；不要从 NiO example 直接复制到其他体系。
- 需要和 `Spin_values`、`Sn_basis`、SOC 设置以及 `TB.H_indep_var` 一起验证。

## 来源

- Lecture-7 GSDTB example.
- Source audit: `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/TB_H_symmetry.f90`.

