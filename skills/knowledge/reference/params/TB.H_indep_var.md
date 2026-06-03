# block TB.H_indep_var

## 含义

GSDTB branch 中为搜索得到的独立 Hamiltonian variables 赋值。Lecture-7 用它把独立参数代入通用自旋依赖 TB Hamiltonian form。

## 默认值

无默认值。

## 何时使用

- 已完成或已有 GSDTB form-search 依据，并且用户要计算特定自旋方向/独立变量取值下的能量或 Hamiltonian 时。

## 注意事项

- 这是高风险 block。变量数量、顺序和值必须来自当前 `cluster-*.Hform` / source-backed form evidence 或用户权威说明。
- 不要从 Lecture-7 example 复制独立变量行到新材料。

## 来源

- Lecture-7 GSDTB example.
- Source audit: `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/TB_H_symmetry.f90`.

