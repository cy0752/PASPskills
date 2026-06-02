# spin_exchange.dat

## 文件作用
`spin_exchange.dat` 为自旋模型相关流程提供相互作用参数，主要用于 `Model Spin_lattice_interaction`，也会被 `Model magnon` 的 spin-wave 路径读取。

## 何时需要
- `Model Spin_lattice_interaction` 需要 J、可选 `dJ/du`、SIA、DMI 或四阶相互作用时。
- `Model magnon` 需要线性自旋波输入时；当前 L2 magnon workflow 只把 J 矩阵/标量 J 作为输入合同，不把非零四阶纯自旋项纳入 LSWT 输入。

## 全局读取合同
下面规则来自开发时对 `spin_exchange.dat` 解析/诊断逻辑的整理，用于 agent 在 input preflight 中检查文件形状；它不是要求用户安装任何外部工具。

- 文件按固定顺序包含五段：J interaction -> `dJ/du` -> SIA -> DMI -> fourth-order。
- 每段都以一个非负整数 count 行开始；count 行只能有一个数字，不能附加数据字段。
- count 后必须跟随该段声明数量对应的条目。声明数量和实际解析到的条目数不一致时，应视为 preflight fail。
- 数值字段可使用能被解析为实数的写法；编号/count 字段应为整数，除 SIA group id 可为一般整数外，其它 group id、元素 id、类型 id、count 均按非负整数检查。
- `#` 后内容视为注释，不参与字段计数；注释前的数据字段仍必须完整。
- 不要插入任意空行。空行在固定位置会被视为缺字段或导致后续段错位。
- 五段结束后不应再有额外数据行；若有非注释额外内容，应先检查前面各段 count 是否写错。

## 第一段：J interaction

### 段结构
```text
<J_count>
<unit-cell vector a: 3 numbers>
<unit-cell vector b: 3 numbers>
<unit-cell vector c: 3 numbers>
<J entry 1>
...
<J entry J_count>
```

- `J_count`：J 相互作用条目数，非负整数。
- 三行 unit-cell vector：每行 3 个数字，必须与 `unit_cell.str` / `%block unit_cell_in_Ang` 的原胞基矢保持一致；不要写 `cell.str` / `%block LatticeVectors` 的超胞或分析胞基矢。
- 后续每个 J entry 的字段数取决于 `spin_lat.general_j` 的模式。

### 标量 J 模式
当 `spin_lat.general_j` 为 false / 未启用矩阵形式时，每个 J entry 必须有 10 个数据字段：

```text
<J_id> <J_scalar> <element_A_id> <element_B_id> <x_A> <y_A> <z_A> <x_B> <y_B> <z_B>
```

字段含义：
- `J_id`：当前 J 条目编号，非负整数。
- `J_scalar`：标量二体相互作用参数。
- `element_A_id element_B_id`：参与相互作用的两个元素编号，应与 `Z_values` / 结构中的元素编号一致。
- 后 6 个数：两个代表原子的笛卡尔坐标，单位通常按 Å 处理。对来自 `find_J_path_sym` 的 J pair，应使用 `log.out` / 标准输出中的 nearest-image `pair_coord` 或等价上游程序生成的最近像坐标；不要为了让坐标“看起来在同一个 cell 里”手工平移或改写代表 pair 坐标。

### 矩阵 J 模式
当 `spin_lat.general_j` 为 true / 启用矩阵形式时，每个 J entry 必须有 18 个数据字段：

```text
<J_id> <J11> <J12> <J13> <J21> <J22> <J23> <J31> <J32> <J33> <element_A_id> <element_B_id> <x_A> <y_A> <z_A> <x_B> <y_B> <z_B>
```

字段含义：
- `J_id`：当前 J 条目编号，非负整数。
- `J11..J33`：3x3 J 矩阵，按行展开。
- `element_A_id element_B_id`：参与相互作用的两个元素编号。
- 后 6 个数：两个代表原子的笛卡尔坐标。对来自 `find_J_path_sym` 的 J pair，应使用 `log.out` / 标准输出中的 nearest-image `pair_coord` 或等价上游程序生成的最近像坐标；不要手工调整。

preflight 如果无法从同一输入包的 `PASP.input` / include 中确认 `spin_lat.general_j`，应把 J entry 字段数作为待确认项，而不是自动把 10 字段和 18 字段混用。

## 第二段：dJ/du

### 段结构
```text
<djdu_count>
<djdu_group_id> <corresponding_J_id>
<supercell vector a: 3 numbers>
<supercell vector b: 3 numbers>
<supercell vector c: 3 numbers>
<atom_count>
<atom coordinate 1: 3 numbers>
...
<atom coordinate atom_count: 3 numbers>
<dJ/du derivative 1: 3 numbers>
...
<dJ/du derivative atom_count: 3 numbers>
...
```

字段含义：
- `djdu_count`：`dJ/du` 数据组数，非负整数；不用该项时通常写 `0`，且后面直接进入 SIA 段。
- group header 两个字段均为非负整数：当前 `dJ/du` group id，以及它对应第一段中的哪个 `J_id`。
- 3 行 supercell vector：当前 `dJ/du` group 使用的超胞基矢，每行 3 个数字。
- `atom_count`：本 group 中给出坐标和导数的原子数，非负整数。
- 接下来必须有 `atom_count` 行原子笛卡尔坐标，每行 3 个数字。
- 再接下来必须有 `atom_count` 行导数，每行 3 个数字，表示 J 对位移坐标分量的偏导。

preflight 必须同时检查 group 数量、坐标行数量和导数行数量；三者任一不匹配都不能视为 ready。

## 第三段：SIA

### 段结构
```text
<sia_count>
<sia_group_id>
<local basis axis 1: 3 numbers>
<local basis axis 2: 3 numbers>
<local basis axis 3: 3 numbers>
<A> <E> <x> <y> <z>
...
```

字段含义：
- `sia_count`：SIA 数据组数，非负整数；不用 SIA 时写 `0`。
- `sia_group_id`：当前 SIA 条目编号，按整数检查。
- 三行 local basis：局域坐标系基矢，每行 3 个数字。
- 参数行固定 5 个数字：`A`、`E` 两个 SIA 参数，以及代表原子的笛卡尔坐标 `x y z`。

## 第四段：DMI

### 段结构
```text
<dmi_count>
<dmi_group_id> <D_x> <D_y> <D_z> <element_A_id> <element_B_id> <x_A> <y_A> <z_A> <x_B> <y_B> <z_B>
...
```

字段含义：
- `dmi_count`：DMI / DM interaction 数据组数，非负整数；不用 DMI 时写 `0`。
- 每个 DMI entry 固定 12 个字段。
- `D_x D_y D_z`：DM 向量的笛卡尔分量。
- `element_A_id element_B_id`：参与相互作用的两个元素编号，非负整数。
- 后 6 个数：两个代表原子的笛卡尔坐标。

## 第五段：fourth-order

### 段结构
```text
<four_order_count>
<four_order_group_id> <four_order_type> <parameter> <element_A_id> <element_B_id>
<representative coordinates>
...
```

字段含义：
- `four_order_count`：四阶相互作用组数，非负整数；不用四阶项时写 `0`。
- group header 固定 5 个字段：
  - `four_order_group_id`：当前四阶项编号，非负整数。
  - `four_order_type`：只能为 `1`、`2` 或 `3`，分别对应 two-body / three-body / four-body fourth-order forms。
  - `parameter`：当前四阶项强度参数。
  - `element_A_id element_B_id`：参与相互作用的元素编号，非负整数。
- header 后必须跟一行代表原子坐标；字段数由 `four_order_type` 决定：
  - type `1`：6 个数字。
  - type `2`：9 个数字。
  - type `3`：12 个数字。

`Model magnon` 使用该文件时，最后的 fourth-order count 必须为 `0`。不要把含非零四阶项的 `Spin_lattice_interaction` 输入直接复制给 magnon。

## preflight 速记
- 确认五段顺序完整，即使某段不用也要有 count 行 `0`。
- 检查每个 count 行只有一个非负整数。
- 检查 J entry 是全文件一致的标量 10 字段或矩阵 18 字段，不要混写。
- 检查第一段三行 lattice vector 来自 `unit_cell.str` / `%block unit_cell_in_Ang`，不是 `cell.str`。
- 检查 J pair 坐标来自 `find_J_path_sym` 的 nearest-image `pair_coord` / 等价上游输出；如果坐标被 agent 手工平移、四舍五入重构或按代表胞“修正”，结论应为 fail / blocked，要求回到上游输出重建。
- 检查每段 declared count 和 actual count 一致。
- 检查 `dJ/du` 每组的坐标行数和导数行数都等于 `atom_count`。
- 检查 SIA 参数行固定 5 字段、DMI 行固定 12 字段、fourth-order header 固定 5 字段。
- 检查 fourth-order type 只能为 `1`、`2`、`3`，且坐标行字段数分别为 6、9、12。
- 检查没有被 count 漏掉的额外数据行。

## 来源章节
- 3.3 `spin_exchange.dat`
- 锚点：`#spin-exchange-dat`

## 开发时校准来源
- `Latticemodel/src/spin_lat.F90` 的 `read_exchange_para` 读取顺序为：J -> `dJ/du` -> SIA -> DMI -> fourth-order。
- `Latticemodel/src/spin_lat_subs.f90` 写出的基础 `spin_exchange.dat` 以 `0 # higher order interaction` 收尾。
- 本文件的字段数、count mismatch 和 J scalar/matrix preflight 规则已吸收开发时 `spin_exchange.dat` 诊断逻辑；运行时 skill 不需要读取外部源码或工具。
