# Symmetry Representative Sites for Spin Modes

## 适用问题

当 `Model Invariant` 的纯自旋有效哈密顿量需要写 `%block local_mode.mode_definition` 时，需要先从结构中找出参与自旋建模元素的对称不等价代表位点。

常见问题包括：
- 如何从 `POSCAR` / `POSCAR_UC` 得到 Gd、Mn 等磁性元素的代表位点
- `local_mode.mode_definition` 中为什么不是所有原子都写
- 如何确定 spin mode 数量
- `<species_id>` 和代表位点坐标应该如何对应

## 核心规则

对纯自旋有效哈密顿量：
- 先和用户确认参与自旋建模的元素，例如 `Gd`、`Mn`。
- 对用于定义局域模式的结构做对称性分析。
- 对每个参与元素，只取对称等价原子组中的一个代表位点。
- 每个代表位点写三个 spin mode，方向分别为 `x/y/z`。
- `num of modes = 参与元素的对称不等价代表位点总数 × 3`。

不要直接遍历所有原子写 mode。PASP 后续会根据晶体对称性扩展到对称等价位点。

## 推荐结构来源

优先使用与 `unit_cell.str` / `POSCAR_UC` 对应的 primitive 或 unit-cell 结构做代表位点分析。

如果当前 workflow 中只有超胞 `POSCAR`，应先判断它是否本身就是原胞；如果不是，应先按 `topics/structure_from_poscar.md` 得到 primitive POSCAR / `POSCAR_UC`，再做对称性分析。

坐标输出应使用 Cartesian 坐标，且坐标系要和 `local_mode.mode_definition` 所依赖的结构文件一致。

## 推荐分析入口

可接受的代表点位来源包括：
- PASP `Model find_J_path_sym` 或同等 PASP 对称性分析流程给出的不等价磁性点位 / 路径信息。
- `pymatgen` / spglib 这类对称性分析工具，在明确 `symprec`、结构来源和元素编号映射后得到的不等价代表点位。
- 用户已有的经过人工或前序计算确认的不等价点位清单。

不可接受的来源：
- 直接遍历 `cell.str`、`POSCAR`、半胞或超胞中的所有磁性原子。
- 只按元素名筛选 Gd/Mn 等磁性原子，却没有做对称等价分组。
- 用某个旧 example 的代表点位数量套到当前材料或当前轴向未确认的结构上。

## pymatgen 示例

下面的脚本会读取结构、按空间群对称性分组，并输出指定元素的代表位点。

```python
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

structure = Structure.from_file("POSCAR_UC")
magnetic_elements = {"Gd", "Mn"}
element_order = ["Gd", "Mn", "O"]  # 与 Z_values / 结构文件元素顺序一致
species_id = {el: i + 1 for i, el in enumerate(element_order)}

sga = SpacegroupAnalyzer(structure, symprec=1e-5)
symm_structure = sga.get_symmetrized_structure()

representatives = []
for equivalent_group in symm_structure.equivalent_sites:
    site = equivalent_group[0]
    element = site.species_string
    if element not in magnetic_elements:
        continue
    representatives.append(
        {
            "element": element,
            "species_id": species_id[element],
            "frac_coords": site.frac_coords,
            "cart_coords": site.coords,
            "multiplicity": len(equivalent_group),
        }
    )

for i, rep in enumerate(representatives, 1):
    x, y, z = rep["cart_coords"]
    print(
        i,
        rep["element"],
        rep["species_id"],
        f"{x:.9f} {y:.9f} {z:.9f}",
        "multiplicity",
        rep["multiplicity"],
    )
```

## 生成 spin mode block

对每个代表位点，生成三个方向：

```text
1 spin
<species_id>
x y z 1.0 0.0 0.0

1 spin
<species_id>
x y z 0.0 1.0 0.0

1 spin
<species_id>
x y z 0.0 0.0 1.0
```

如果代表位点数为 `N_rep`，则 `%block local_mode.mode_definition` 第二行应写 `3 * N_rep`。
`N` 后面必须直接接第一个 mode 定义，不要插入空行；不同 mode 定义之间必须保留一行空白分隔行，否则 PASP 读取 `read_local_mode_general` 时会发生 mode 错位。

## l3-2 判断方式

在 `l3-2` 这类纯自旋有效哈密顿量中，如果参与元素确认为 `Gd` 和 `Mn`，并且对称性分析得到：
- `Gd`: 2 个对称不等价代表位点
- `Mn`: 3 个对称不等价代表位点

则代表位点总数为 `5`，spin mode 总数为 `15`。`local_mode.mode_definition` 中应写 15 个 `spin` mode，顺序可以按代表位点顺序展开，每个位点依次写 `x/y/z` 三个方向。

## tolerance 护栏

`symprec=1e-5` 是严格的起点，适合已经较规范的结构文件。实际结构如果有数值噪声或轻微畸变，可以比较多个 tolerance，例如：
- `1e-5`
- `1e-4`
- `1e-3`

如果代表位点数量随 tolerance 大幅变化，不要直接采用结果；应回到结构来源、primitive reduction、磁有序或有意畸变的物理设置重新判断。

## 检查清单

- 参与元素是否已由用户或物理目标确认，而不是 agent 自行猜测。
- `element_order` 是否与 `Z_values` 和结构文件元素顺序一致。
- `<species_id>` 是否是元素类型编号，而不是原子编号。
- 坐标是否为 Cartesian 坐标。
- 使用的结构是否与 `unit_cell.str` / `POSCAR_UC` 对应。
- 代表位点数量是否和 notebook、PASP 输出或材料对称性直觉一致。
- 生成的 mode 数是否等于 `代表位点数 × 3`。
- `local_mode.mode_definition` 的 `N` 后是否无空行，且不同 mode 定义之间是否有一行空白分隔行。

## 相关 reference

- `params/local_mode.mode_definition.md`
- `topics/structure_from_poscar.md`
- `files/unit_cell.str.md`
- `params/Z_values.md`
- `params/Spin_values.md`
