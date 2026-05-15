# spin_exchange.dat

## 文件作用
在 `Model Spin_lattice_interaction` 中提供自旋相互作用参数。

## 何时需要
- 使用 `Model Spin_lattice_interaction` 时
- 需要定义 J 矩阵、单离子各向异性（SIA）、可选的 `dJ/du` 以及其他高阶相互作用数据时

## 关键字段/内容
### 第一部分：J 矩阵
1. 第一行：相互作用组数
2. 接着 3 行：原胞基矢信息（与 `unit_cell.str` 一致）
3. 后续每组一行，内容依次为：
   - 第几组相互作用
   - J 矩阵 9 个数（逐行写）
   - 元素编号 2 个数
   - 代表对原子的笛卡尔坐标 6 个数

若代表对原子坐标相同，则这里应填写 SIA 矩阵。

### 第二部分：`dJ/du`
- 不常用，通常写 `0`
- 若使用，则每组需给出对应第几种 J、扩胞后的 3×3 基矢、原子数、各原子坐标、对各坐标分量的偏导（单位 eV/Å）

## 注意事项
- 采用严格逐行读取规则，不能任意空行，也不能删改应有行数
- `#` 后内容为注释；注释符 `#` 需与数据之间用空格或制表符分开
- 文档特别说明：首尾用 `#` 包起来的示意边框行不算正式文件内容
- 参数单位：相互作用参数为 eV，坐标为笛卡尔坐标且单位 Å
- 原胞矢量信息需与 `unit_cell.str` 对应内容保持一致
- `Model magnon` 使用该文件时，最后的 higher-order / fourth-order count 必须为 `0`。当前 L2 magnon workflow 不把四阶纯自旋相互作用纳入 LSWT 输入契约；不要把含非零四阶项的 `Spin_lattice_interaction` 输入直接复制给 magnon。

## 源码补充
- `Latticemodel/src/spin_lat.F90` 的 `read_exchange_para` 读取顺序为：J 矩阵 → `dJ/du` → SIA → DM → 四阶项。
- 当 `model = 'magnon'` 且走 `spinw` 路径时，源码会把 `spin_lat.general_J` 重置为矩阵形式读取，因此 magnon 输入应按 J 矩阵合同准备。
- `Latticemodel/src/spin_lat_subs.f90` 写出的基础 `spin_exchange.dat` 以 `0 # higher order interaction` 收尾。

## 最小示例
文档只给了较长示例，实际填写建议直接参照官方示例。

## 来源章节
- 3.3 `spin_exchange.dat`
- 锚点：`#spin-exchange-dat`
