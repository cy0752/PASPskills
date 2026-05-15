# PASP.input reference

来源页面：
https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html

对应章节：
- 3.1 核心输入文件PASP.input
- 3.1.1 PASP.input文件读取规则
- 3.1.2 最常用设置项
- 3.1.3 附属文件cell.str：晶胞信息
- 3.1.4 附属文件unit_cell.str：原胞信息

---

## 1. PASP.input 是什么

`PASP.input` 是 PASP 的核心输入文件，用来：
- 选择功能模块（由 `Model` 决定）
- 提供体系结构与参数
- 通过 `%include 文件名` 引入附属文件

常见附属文件：
- `cell.str`：晶胞信息
- `unit_cell.str`：原胞信息
- `MC.input`：MC/CG 设置
- `MD.input`：MD 设置

通常所有输入文件放在同一目录下运行。

---

## 2. 读取规则

### 2.1 基本规则
- 按行读取
- 行首空格、Tab 忽略
- 同一行内各字符串之间可用一个或多个空格或 Tab 分隔
- 关键词大小写不敏感

例如：
```text
numberofatoms 5
```
会被识别为：
```text
NumberOfAtoms 5
```

### 2.2 block 结构
当一行以 `%block` 开始时，程序读取对应块，直到匹配的 `%endblock`。

注意：
- block 外部可空行
- block 内部不能随意空行，需严格按格式写

### 2.3 注释
- `#` 后内容不参与读取
- 建议有效内容与 `#` 之间留空格，便于阅读

### 2.4 include 机制
可用：
```text
%include cell.str
```
程序会跳转读取该文件，结束后再回到原位置继续。

原则上，附属文件内容也可直接写回 `PASP.input`，然后去掉 `%include` 行。

### 2.5 重复关键词
若同一关键词出现多次，只有第一次出现的内容生效。

因此：
- 文件内顺序重要
- `%include` 的位置会影响实际采用的设置

### 2.6 布尔量写法
- True：`T` 或 `.TRUE.`
- False：`F` 或 `.FALSE.`

手册示例通常使用 `T/F`。

---

## 3. 最常用设置项

### 3.1 `Model`

#### 含义
最关键的设置，决定调用哪个功能模块，也决定后续需要读取哪些参数。

#### 默认值
`Charge_ordering`

#### 常见可选值
- `find_J_path_sym`
- `Invariant`
- `Spin_lattice_interaction`
- `atomic_effective_H`
- `GA`
- `TB`
- `KNB`
- `magnon`

#### 建议
建议放在文件最前面。

#### 示例
```text
Model find_J_path_sym
```

### 3.2 `%block SuperCell`

#### 含义
定义扩胞矩阵；扩胞基于 `cell.str` 中给出的结构进行。

#### 格式
- 3×3 可逆整数矩阵
- 默认是不扩胞，即 1×1×1

#### 示例
```text
%block SuperCell
2 0 0
0 2 0
0 0 2
%endblock SuperCell
```

#### 备注
PASP 习惯上把 `cell.str` 提供的结构称为“晶胞”，经 `SuperCell` 得到的称为“超胞”。

### 3.3 `%block Z_values`

#### 含义
给出各元素对应的数值标签，通常是原子序数。

#### 默认行为
- 优先根据 `cell.str` 的 `AtomicCoordinatesAndAtomicSpecies` 第五列元素名自动生成
- 若仍无法确定，则全部设为 1

#### 注意
元素顺序应与 `cell.str` 中原子坐标里各元素首次出现顺序一致，这样元素编号才能正确匹配。

#### 示例
以 BiFeO3 为例：
```text
%block Z_values
83 26 8
%endblock Z_values
```

#### 特别说明
在 TB 模块中，这里不是填原子序数，而是填该元素所考虑轨道的电子数。

### 3.4 `%block isaAB`

#### 含义
指定研究哪两类元素之间的相互作用。

#### 格式
提供两个整数：
- 取值为 0 或某元素编号
- 元素编号来自 `Z_values` 中的顺序编号，从 1 开始

#### 默认值
```text
0 0
```

#### 示例
若研究 BiFeO3 中 Fe–Fe 相互作用，而 Fe 在 `Z_values` 中排第 2：
```text
%block isaAB
2 2
%endblock isaAB
```

### 3.5 `%block Spin_values`

#### 含义
设置各元素对应的自旋或磁矩尺度。

#### 默认值
全部为 1。

#### 取值
非负实数。

#### 常见理解
通常填各元素电子总自旋量子数的二倍；很多磁性计算里也可把它理解为近似磁矩大小（单位近似为 `μB`）。

#### 示例 1：按真实磁矩近似
BiFeO3 中只有 Fe 有磁性，若约为 3：
```text
%block Spin_values
0 3 0
%endblock Spin_values
```

#### 示例 2：自旋归一化模型
若采用归一化自旋矢量模型，磁性原子常设为 2：
```text
%block Spin_values
0 2 0
%endblock Spin_values
```

#### 使用建议
在 `Model Invariant` 或 `Model atomic_effective_H` 这类有效哈密顿量流程中，经常采用归一化自旋，此时磁性原子常写为 2。

### 3.6 `%block ExternalMagneticField`

#### 含义
在 MC 或 CG 中施加外磁场。

#### 单位
T（特斯拉）。

#### 默认值
三个分量都为 0。

#### 示例
z 方向施加 0.1 T：
```text
%block ExternalMagneticField
0 0 0.1
%endblock ExternalMagneticField
```

#### 与 `Spin_values` 的关系
Zeeman 能项会乘以 `Spin_values` 读入的磁矩或自旋尺度，因此：
- 若 `Spin_values` 用真实磁矩值，磁场值可直接按物理量填写
- 若 `Spin_values` 采用归一化模型，则外磁场输入值需按比例修正

网页示例含义：若真实自旋量子数为 3/2，要实现等效 0.1 T，则对应磁场分量需要写成 0.15。

### 3.7 `MD.B_x`, `MD.B_y`, `MD.B_z`

#### 含义
仅用于 MD 或自旋动力学时的外磁场分量设置。

#### 特点
- 单位也是 T
- 使用 MD 时，这组参数生效，`ExternalMagneticField` 不起作用

#### 示例
```text
MD.B_x 0.0d0
MD.B_y 0.0d0
MD.B_z 0.0d0
```

---

## 4. 相关附属文件

### 4.1 `cell.str`

#### 用途
提供晶胞结构；若定义了 `SuperCell`，扩胞就以它为基础。

#### 启用方式
在 `PASP.input` 中写：
```text
%include cell.str
```

#### 常含内容
- `NumberOfAtoms`
- `number_of_species`
- `LatticeConstant`
- `%block LatticeVectors`
- `AtomicCoordinatesFormat`
- `%block AtomicCoordinatesAndAtomicSpecies`

#### 备注
- 也可以不单独写 `cell.str`，而把这些内容直接写进 `PASP.input`
- 也支持用 POSCAR 代替，依赖 `READ_POSCAR T`
- 如果当前只有 VASP `POSCAR`，先判断它是原胞还是超胞；结构准备方法见 `topics/structure_from_poscar.md`

### 4.2 `unit_cell.str`

#### 用途
提供原胞结构。若未提供，程序默认把原胞信息视为与 `cell.str` 一致。

#### 启用方式
在 `PASP.input` 中写：
```text
%include unit_cell.str
```

#### 常含内容
- `unit_cell.na`
- `%block unit_cell_in_Ang`
- `%block Atoms_in_unit_cell_Ang`

#### 适用场景
当 `cell.str` 给的是超胞或非原胞结构，而流程又需要原胞信息时，一般必须提供该文件。

#### 重要约束
- 原胞和晶胞必须使用同一套笛卡尔坐标系
- 原点也必须一致
- 若需要从超胞 `POSCAR` 推导 primitive POSCAR / `POSCAR_UC`，不要直接猜原胞；先按 `topics/structure_from_poscar.md` 做 primitive reduction 和结果检查

---

## 5. 最小实用模板

```text
Model Invariant

%include cell.str
%include unit_cell.str

%block SuperCell
2 0 0
0 2 0
0 0 2
%endblock SuperCell

%block Z_values
83 26 8
%endblock Z_values

%block isaAB
2 2
%endblock isaAB

%block Spin_values
0 2 0
%endblock Spin_values
```

---

## 6. 使用要点速记
- `Model` 决定模块，优先写在最前
- `%include` 的顺序会影响“首次出现即生效”的规则
- `SuperCell` 基于 `cell.str`
- `Z_values` 的顺序要和结构文件中的元素顺序对应
- `isaAB` 用元素编号，不是元素符号
- `Spin_values` 若使用归一化模型，外磁场解释要同步调整
- `cell.str` 管晶胞，`unit_cell.str` 管原胞，两者坐标系必须一致
