# Structure Preparation from POSCAR

## 适用问题
当用户只有 VASP `POSCAR`，但 PASP workflow 需要 `cell.str`、`unit_cell.str`、`POSCAR_UC` 或 primitive POSCAR 时，先用本主题判断结构来源关系。

常见问题包括：
- 只有一个 `POSCAR`，能不能写 `cell.str`
- 只有超胞 `POSCAR`，怎么得到 primitive POSCAR
- `unit_cell.str` 是否能从当前 `POSCAR` 自动生成
- `READ_POSCAR` / `READ_POSCAR_UC` 应该配合哪些文件

## 先说明边界
这个主题只解决“结构文件从哪里来、各自扮演什么角色”。

它**不能**替代下面这些 workflow 级建模决策：
- 现在到底要做哪个 PASP workflow / Model
- 哪些元素参与磁性或局域模式建模
- 截断范围、体数和展开阶数怎么选
- 是否需要 SOC、strain、phonon 或其他自由度

所以如果用户只有一个 `POSCAR`，却要求“直接生成 `PASP.input` 并开始跑 PASP”，不能只靠本主题自动补齐输入。正确做法是：
- 先用本主题判断 `POSCAR`、`POSCAR_UC`、`cell.str`、`unit_cell.str` 的关系；
- 再进入对应 workflow，先确认最少的建模问题；
- 只有在用户明确接受 smoke-test 默认模板时，才可以把模板默认值临时用于跑通链路，而且必须明确标注这些值还不是正式科研设置。

还要注意：本主题说明“可以使用 `READ_POSCAR` / `READ_POSCAR_UC`”，不等于 agent 可以在已有 workflow 模板和示例已经明确使用 `cell.str` / `unit_cell.str` 时，擅自把输入路线改成 POSCAR 读取路线。

默认原则应是：
- 如果当前 workflow 模板已经明确 `%include cell.str`、`%include unit_cell.str`，优先沿用这条 `str` 文件路线；
- 只有当用户明确要求改成 `READ_POSCAR` / `READ_POSCAR_UC`，或者当前项目根本没有稳定的 `str` 文件路线时，才切到 POSCAR 读取路线；
- agent 不能仅仅因为“从 POSCAR 自动生成更省事”，就把一个基于 `str` 文件的 workflow 自动改写成基于 `READ_POSCAR` 的 workflow。

## 基本判断
- 如果 `POSCAR` 本身就是原胞：可直接作为 `cell.str` 来源，也可作为 `unit_cell.str` / `POSCAR_UC` 来源。
- 如果 `POSCAR` 是计算用超胞：可直接作为 `cell.str` 来源；`unit_cell.str` 不能仅凭肉眼保证唯一，需通过已知超胞矩阵、已有 primitive POSCAR，或对称性工具辅助还原。
- 如果同时有超胞 `POSCAR` 和 primitive POSCAR：通常用超胞 `POSCAR` 生成 `cell.str`，用 primitive POSCAR 生成 `unit_cell.str` 或 `POSCAR_UC`。

## 从 POSCAR 得到 primitive POSCAR

可用 `pymatgen` 对结构做 primitive reduction：

```python
from pymatgen.core import Structure

structure = Structure.from_file("POSCAR")
primitive_structure = structure.get_primitive_structure(tolerance=0.02)
primitive_structure.to(filename="POSCAR_UC", fmt="poscar")
```

如需规范化 VASP 文件格式，可再用 ASE 读写一次：

```python
from ase.io import read, write

atoms = read("POSCAR_UC")
write("POSCAR_UC", atoms)
```

## 建议检查

生成 primitive POSCAR 后，不要只看文件是否存在，还要检查：
- 原子数是否从超胞数量合理缩小到原胞数量
- 元素种类和化学计量是否合理
- 晶格矢量是否与预期 primitive cell 对应
- primitive reduction 后的 `a/b/c` 轴是否仍与你当前 workflow 里默认使用的轴向约定一致
- 空间群或等价原子分组是否没有因 tolerance 选择而异常改变
- 后续 `unit_cell.str` 中的原胞坐标是否与 `cell.str` 使用同一套 Å / Cartesian 约定

这里要特别注意一个常见坑：
- 从 `POSCAR` 自动约简得到的 primitive cell，并不保证保留你原来理解中的 `a`、`b`、`c` 轴标签顺序；
- 对称性工具可能返回一组等价但重新排列过的 primitive lattice vectors，表现成 `a/b/c` 互换，或整体换成另一组等价基矢；
- 如果后续 `cellabc` 轴向理解、`local_mode.mode_definition`、代表位点编号、磁矩方向约定或人工分析步骤默认沿用旧轴系，就不能只因为 primitive 结构“看起来对”就直接继续。

更稳妥的做法是：
- 先把生成的 `POSCAR_UC` / `unit_cell.str` 与你当前 `cell.str`、预期超胞矩阵或已知 primitive 结构逐项对比；
- 确认基矢方向、长度和夹角确实对应你想要的那套轴系；
- 如果只是等价基矢重排，则在进入 PASP 前把 `unit_cell.str` 的基矢顺序和对应原子坐标一起重排到你当前 workflow 使用的轴向约定，而不是直接混用两套坐标系。

### 自动 primitive 后的轴向修正规则

当自动约简得到的 primitive cell 与当前 workflow 轴向不一致时，agent 不能只报告异常，也不能只手工改三行 lattice。
也不能仅因 pymatgen / spglib 返回的 primitive 轴顺序与预期不同，就丢弃这个等价 primitive 并自行构造“沿 x/y/z 切半”的保轴原胞。优先事项是求清楚变换关系。

必须按下面顺序处理：
1. 先判断候选 primitive 与预期 primitive 是否只是等价基矢重排、循环换轴、整数基变换或整体坐标系旋转。
2. 求 primitive rebase 矩阵 `T`，把自动 primitive 的 lattice 和所有原子坐标同步变换到当前 workflow 的目标轴向；不能只改 lattice 三行。
3. 求超胞到修正后 primitive 的整数矩阵 `M`，也就是后续 `%block SuperCell` 应表达的结构关系；确认 `det(M)`、体积比和原子数比例一致。
4. 用物种计数、元素顺序、周期性原子映射 tolerance 和最大残差验证修正后 primitive 与超胞自洽。
5. 只有在 `POSCAR_UC`、`unit_cell.str`、`cell.str`、`local_mode.mode_definition` 和 `SuperCell` 全部处在同一坐标系后，才能把这些文件视为正式输入。

反例：如果原始超胞是 `[a, b, c]`，体积比例显示 primitive 应是 `[a/2, b, c]`，但自动约简输出了 `[c, a/2, b]`，那么不能直接接受这个 `POSCAR_UC`。应把 primitive 基矢和原子坐标一起重排回 `[a/2, b, c]`，并让 `SuperCell` 对应为对角或预期的保轴矩阵；如果无法确认这个判断，就停下来问用户。

另一类反例：看到自动 primitive 是 `[c, a/2, b]` 后，直接放弃它并手工把原超胞沿 x 方向二分，属于未证明的结构假设。除非 `T` / `M` 映射或用户确认已经证明目标就是这个二分关系，否则只能保持 candidate / blocked，不能生成正式 `POSCAR_UC`、`unit_cell.str` 或 shared-basis 输入。

可用 `pymatgen` 做基本对称性检查：

```python
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

structure = Structure.from_file("POSCAR_UC")
sga = SpacegroupAnalyzer(structure, symprec=1e-5)
print(sga.get_space_group_symbol())

symm_structure = sga.get_symmetrized_structure()
for i, equivalent_group in enumerate(symm_structure.equivalent_sites):
    print(f"equivalent group {i + 1}:")
    for site in equivalent_group:
        print(site.species_string, site.frac_coords)
```

如果目标是给 `local_mode.mode_definition` 找参与自旋元素的对称不等价代表位点，继续查 `topics/symmetry_representative_sites.md`。

## tolerance 护栏

`get_primitive_structure(tolerance=0.02)` 是经验起点，不是通用定理。

需要特别谨慎的情况：
- 结构有微小畸变、低对称相或数值噪声
- 磁有序、占位有序或用户有意构造的超胞会被错误“约简”
- primitive 后原子数、空间群或等价原子组与物理预期不一致

如果结果可疑，应调小或调大 `tolerance` 后比较，或要求用户提供已知 primitive cell / 超胞矩阵。

## 和 PASP 输入的对应关系

### 使用 POSCAR 代替 cell.str
如果要让 PASP 读取计算晶胞/超胞的 VASP 结构文件：

```text
READ_POSCAR T
```

此时通常准备文件名为 `POSCAR`。

但在已有 workflow 模板已经稳定使用 `cell.str` 的场景里，这一选项应视为“可选替代路线”，而不是默认推荐路线。

### 使用 POSCAR_UC 代替 unit_cell.str
如果 workflow 需要单独原胞信息，可用 primitive POSCAR：

```text
READ_POSCAR_UC T
```

此时通常准备文件名为 `POSCAR_UC`。

同样地，如果当前 workflow 示例和模板本来就基于 `unit_cell.str`，不要在未征得用户同意时自动切换到 `READ_POSCAR_UC T`。

### 转成 str 文件
如果不使用 `READ_POSCAR` / `READ_POSCAR_UC`，则按文件角色转换：
- `POSCAR` 或目标计算结构 → `cell.str`
- primitive POSCAR / `POSCAR_UC` → `unit_cell.str`

`unit_cell.str` 中的坐标块只支持 Å 下的 Cartesian 坐标；`cell.str` 建议也用 `LatticeConstant 1 Ang` 和 `AtomicCoordinatesFormat NotScaledCartesianAng`，避免两者坐标约定不一致。

## 常见错误
- 把超胞 `POSCAR` 直接当成 `unit_cell.str` 来源，导致原胞信息错误。
- `cell.str` 已经是超胞，又在 `%block SuperCell` 中重复扩胞。
- primitive reduction 后没有检查原子数和对称性，直接用于后续拟合或相互作用分析。
- primitive reduction 后看到原子数和空间群都对，就误以为 `a/b/c` 轴一定没变；结果 `unit_cell.str` 与当前 `cellabc` 轴向约定不一致。
- 误以为 `tolerance=0.02` 对所有材料都可靠。

## 相关 reference
- `files/cell.str.md`
- `files/unit_cell.str.md`
- `topics/PASP.input.md`
- `params/SuperCell.md`
- `topics/symmetry_representative_sites.md`
