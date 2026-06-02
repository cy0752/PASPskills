# atom_Heff.getP

## 含义
`atom_Heff.getP` 控制 `Model atomic_effective_H` 中是否使用 Born effective charge 相关数据计算极化。

源码中该参数读入变量 `lgetP`，默认值为 `F`。当 `lgetP` 为 `T` 时，`atomic_effective_H` 初始化会调用 `init_BEC_local_mode`，该流程读取 Born charge 数据并为 local mode 构造 `BEC_lm`。在统计 local-mode 平均量时，若 `lgetP` 为 `T`，极化量按 `BEC_lm * local-mode amplitude` 累加；若为 `F`，源码走普通 local-mode amplitude 汇总路径。

Lecture-4 说明在 MC 模拟中计算体系极化强度时可设置 `atom_Heff.getP T`，若设为 `T`，程序将读取 `Zeff.dat` 中的 Born effective charge。

## 默认值
`F`

## 取值
`T/F`

## 何时使用
- 使用 `Model atomic_effective_H`。
- 当前 L4 MC / PTMC 目标需要极化相关输出或极化趋势分析。
- 当前 L5 BaTiO3 electric-field MD / hysteresis branch 需要 `P_abs.dat` 或 polarization-vs-field 分析。
- 输入包中有与当前 `unit_cell.str` / mode definition 对应的 `Zeff.dat`。

## 相关文件与输出
- 输入依赖：`Zeff.dat`。
- 相关统计输出：`P_abs.dat`、`epsilon.dat`、`ECE.dat`，以及 local-mode / strain / lattice 统计输出中的极化解释。

## 注意事项
- `atom_Heff.getP T` 时，preflight 必须检查 `Zeff.dat` 存在并与当前结构、unit cell 和 mode basis 对应。
- `P_abs.dat` 文件出现本身不足以证明极化设置正确；output validation 还应检查 `PASP.used_info` 中 `atom_Heff.getP` 的实际值和 `Zeff.dat` provenance。
- 不需要极化目标时，不要因为 Lecture-4 MC-1 example 使用了该字段就默认开启。
- L5 BaTiO3 branch 中，active electric field may also turn on BEC/polarization support in source behavior. Preflight should still check explicit input intent and `Zeff.dat` provenance rather than relying on file existence.

## 本地来源
- 官网第 3 章参数抽取中未找到该字段；本卡片为 Lecture-4 + 源码审计补充。
- Lecture-4 markdown：`pasp_slides_md/Lecture-4.../full.md` lines 404-421。
- 源码读取默认值：`atom_Heff.F90` lines 370。
- 源码 BEC 初始化：`atom_Heff.F90` lines 228-230 and `atom_Heff_measure.F90` lines 56-116。
- 源码极化累加：`atom_Heff_measure.F90` lines 319-351。
- 源码输出文件：`atom_Heff_measure.F90` lines 433-456。
- Example evidence：`pasp_examples/Lecture-4/MC-1/input/MC.input` and `MC-1/complete/PASP.used_info`.
