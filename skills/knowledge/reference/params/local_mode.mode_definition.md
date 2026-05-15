# local_mode.mode_definition

## 含义
在有效哈密顿量方法中自定义局域模式。这里的局域模式可以是自旋模式，也可以是局域声子模式等；纯自旋有效哈密顿量通常只需要定义 `spin` 模式。

## 写法骨架
```text
%block local_mode.mode_definition
2   # method, 2 is the general one
N   # num of modes
<mode 1>

<mode 2>

...
%endblock local_mode.mode_definition
```

其中第一行 `2` 表示使用通用定义方式；第二行 `N` 是后面定义的 mode 总数。`N` 后面必须直接接第一个 mode 定义，不要插入空行。不同 mode 定义之间必须保留一行空白分隔行；PASP 的 `read_local_mode_general` 会在读取每个非末尾 mode 后额外读入一行作为分隔行，缺少该空白行会导致后续 mode 被错位读取。

## 自旋模式格式
单个自旋 mode 的常见格式是：

```text
1 spin
<species_id>
x y z  sx sy sz
```

含义：
- `1 spin`：单原子自旋模式
- `<species_id>`：该原子所属元素编号，需与 `Z_values` / 结构文件中的元素顺序对应
- `x y z`：该代表原子的 Cartesian 坐标
- `sx sy sz`：该自旋自由度的方向，例如 `1.0 0.0 0.0`

对一个参与自旋建模的对称不等价位点，通常分别写三个方向：

```text
1 spin
2
4.302767177 5.539013872 2.825058222 1.0 0.0 0.0

1 spin
2
4.302767177 5.539013872 2.825058222 0.0 1.0 0.0

1 spin
2
4.302767177 5.539013872 2.825058222 0.0 0.0 1.0
```

## 局域声子或位移模式
局域声子模式可以用普通模式定义，不写 `spin`。典型结构是先给出该 mode 涉及的原子数，再给相关原子类型和每个原子的坐标与位移方向。此类模式可能还会带 `lamp` 形式，用于处理大振幅模式的软边界。

纯自旋有效哈密顿量通常不需要写这类位移模式；若涉及铁电、声子或自旋-晶格耦合，应回到 workflow 判断当前模型边界后再写。

## 何时使用
- `Model Invariant` 中需要显式定义自旋、局域声子或混合自由度时
- `local_mode.general_model T` 且默认局域模式不足以表达目标自由度时
- 后续 `atomic_effective_H`、MC、MD 等阶段需要复用同一套局域模式定义时

## 自旋有效哈密顿量的生成规则
对纯自旋模型，推荐流程是：
1. 先和用户确认哪些元素参与自旋建模。
2. 对结构做对称性分析，找出参与元素的对称不等价位点；具体脚本和检查见 `topics/symmetry_representative_sites.md`。
3. 每个参与位点取一个代表原子坐标。
4. 每个代表位点写 `x/y/z` 三个 `spin` mode。
5. `num of modes = 参与自旋的对称不等价位点数 × 3`。

例如参与元素为 `Gd` 和 `Mn`，如果对称性分析得到 2 个 Gd 代表位点和 3 个 Mn 代表位点，则自旋 mode 数为 `(2 + 3) × 3 = 15`。

## 注意事项
- 坐标应使用 Cartesian 坐标，并与当前结构文件的坐标系保持一致。
- `<species_id>` 不是原子序号，而是元素/类型编号，需与 `Z_values` 和结构文件中的元素顺序对应。
- 单原子自旋 mode 的第一行应写 `1 spin`；不要把这里的 `1` 改成元素编号。元素编号写在下一行 `<species_id>`。例如 Mn 是 species 2 时也应写成三行 `1 spin` / `2` / `x y z sx sy sz`。
- 参与自旋的元素不能由 agent 擅自决定，应由用户或材料物理目标确认。
- `N` 后面不要空行，应直接接第一段 mode 定义；不同 mode 定义之间必须有一行空白分隔行。
- 如果同时混合自旋模式和位移模式，仍按同一个 mode 总数计数。
- 若使用 `lamp` 形式，需要额外确认大振幅边界和函数形式，不应从纯自旋模板中猜。

## 常见误区
- 遍历所有原子直接写 mode，而不是先取对称不等价代表位点。
- 把 `<species_id>` 写成原子编号。
- 把 mode 第一行的原子数写成 species id，例如为 Mn 写 `2 spin`。这会把单原子自旋模式误写成两原子模式，后续解析或物理语义都会错。
- 忘记为每个自旋代表位点写三个方向。
- 在 mode 总数 `N` 后插入空行；PASP 在 `read_local_mode_general` 做 Fortran list-directed read 时可能读到空记录，并报 `forrtl: severe (24): end-of-file during read`。
- 不同 mode 定义之间没有空白分隔行；PASP 会把下一段 mode 的第一行当作分隔行吞掉，随后从错误位置继续读取，常见报错是 `forrtl: severe (59): list-directed I/O syntax error`。
- 修改 `local_mode.mode_definition` 后，没有同步检查 `Spin_values`、`Z_values`、结构文件和后续 `local_mode_PM.dat` 复用条件。

## 相关日志判读
如果日志已经完成结构读取，并在下面顺序后崩溃：

```text
local_mode_setup begin
read_local_mode_coup
set_up_local_mode_atomic
before read_local_mode_general
forrtl: severe (24): end-of-file during read
```

或类似：

```text
local_mode_setup begin
read_local_mode_coup
set_up_local_mode_atomic
before read_local_mode_general
forrtl: severe (59): list-directed I/O syntax error
```

优先检查 `%block local_mode.mode_definition` 的行结构，尤其是 mode 总数后是否多了空行、不同 mode 之间是否缺少空白分隔行、mode 数是否与实际定义段数一致、`%endblock` 是否过早出现。此类错误通常不是 VASP `OUTCAR` 数据问题，也不应优先归因于 `special_SOC`。如果日志前面出现 `MPI startup(): PMI server not found`，但 PASP 后续已经启动、验证 license 并读取结构，这条一般只是运行环境警告，不是这个崩溃点的主因。

## 相关条目
- `modules/effective_hamiltonian.md`
- `topics/PASP.input.md`
- `topics/symmetry_representative_sites.md`
- `params/Z_values.md`
- `params/Spin_values.md`
- `files/unit_cell.str.md`

## 来源章节
- 3.1.7.5 自定义局域模式 (`block local_mode.mode_definition`)
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#block-local-mode-mode-definition>
