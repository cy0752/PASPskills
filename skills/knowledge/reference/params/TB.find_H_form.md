# TB.find_H_form

## 含义

开启基于对称性的 TB Hamiltonian form / general spin-dependent tight-binding form 搜索。Lecture-7 GSDTB branch 使用它来得到由独立参数组成的哈密顿量矩阵形式。

## 默认值

F

## 取值

T/F

## 何时使用

- GSDTB / spin-dependent Hamiltonian form search。
- 需要得到 `cluster-*.Hform` 等独立参数形式输出时。

## 相关设置

- `TB.full_SOC`
- `TB.H_spin_expand`
- `block GSD_TB_Spin_direction`
- `block TB.H_indep_var`
- `fig.maxk`
- `block fig.mdist`

## 注意事项

- 不等于用户已经确认独立变量值或磁各向异性结论。
- `TB.H_indep_var` 的变量数量和值必须来自当前 branch evidence 或用户确认。

## 来源

- Lecture-7 GSDTB example.
- Source audit: `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/TB.f90` and `TB_H_symmetry.f90`.

