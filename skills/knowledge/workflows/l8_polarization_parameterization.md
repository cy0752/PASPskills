# L8 统一极化模型的 DFT 参数化与 PASP 交接

用于从结构设计 DFT 取样、从已有 DFT 输出提取张量，或把拟合结果交给 PASP。PASP 是下游极化计算的首选。上游 DFT 负责 Berry 相偶极、力、应力和线性响应，后处理负责分支对齐、拟合和输入转换。正式 PASP 输入与输出验收沿用 [L8 状态机](l8_spin_induced_polarization_state_machine.md)。

## 选择目标与参考

| 任务 | 所需数据与计算入口 |
|---|---|
| 固定结构，从给定自旋计算电子极化 | 用四态法提取格点间 `Pij`，需要单格点项时拟合 `Pi`。由 PASP `Model KNB` 计算给定自旋的电子偶极。 |
| 从磁序预测诱导位移、应变和极化 | 提取所需的交换导数和结构响应参数。由 PASP `Model Spin_lattice_interaction` 求位移、应变及离子／晶格极化。 |
| 已有参考和目标结构，求两者间的极化变化 | 用 PASP `Model KNB` 求电子自旋差值，用已知的内部位移和应变评估 Born 与压电贡献。仅在当前 PASP 版本有已验证的对应入口时交给 PASP 做这一步，否则显式后处理并记录来源。 |

确定绝缘参考结构、参考自旋、DFT 与 PASP 的原子和晶胞映射、Cartesian 坐标系、磁性子晶格、截断壳层与自旋长度约定。记录原胞、拟合超胞和应用超胞各自的作用。用当前结构的对称性选取不等价格点和有向键 `i → j`，保存 DFT 原子编号、周期平移像、键向量与局域轴。检查超胞中翻转同一对自旋会否同时翻转多条周期等价键。此时混合差分给出这些键的系数和，需用能分辨各键的超胞或有明确重数的拟合设计。

## 固定结构的 DFT 和 Berry 相分支

1. 同一参数组使用相同晶格、原子位置与顺序、电子设置和背景自旋。保留逐态 manifest，记录目标原子、轴对／方向、正负号、背景自旋、实际输入和输出路径。拟合一般的各向异性项时用约束非共线 SOC。VASP 可用 `LSORBIT`、`MAGMOM`、`M_CONSTR`、`I_CONSTRAINED_M`、`LAMBDA`、`RWIGS` 和 `LCALCPOL`，按当前 VASP 版本验证约束模式、`SAXIS` 对应的自旋坐标和收敛设置。仅拟合各向同性项时可使用有依据的无 SOC 配置。
2. 按态检查电子收敛、绝缘性、最终偶极块、实际磁矩方向和约束质量，包括背景磁矩。确认几何没有改变，确保偶极输出精度和数值收敛足以解析目标差分。记录正常结束和异常终止证据。缺态、磁矩翻转失败或 Berry 分支不明时暂缓提取对应分量。
3. 固定几何的 `Pi/Pij` 拟合取 `OUTCAR` 最后对应收敛态的电子偶极（`p[elc]`，单位 `e Å`）。离子偶极可用于核对几何一致性。直接 DFT 端点跨几何比较时，使用包含离子项的总偶极并按参考路径对齐分支。
4. 四态差分和正反平均前先将偶极对齐到共同 Berry 分支。晶格行向量矩阵为 `A` 时，记录 `D_corr = D_raw − n @ A`，其中 `n` 是整数向量，偶极数值用 `e Å` 表示。固定晶胞且偶极变化远小于量子时可用参考态附近的最近晶格像，斜晶胞按晶格度量判定。有多个合理整数解或变化接近量子时，用连续绝缘路径、中间自旋态或可靠的参考偶极消歧。保存原始和校正偶极、整数平移、锚点与分支依据。

## `Pij` 格点间张量的四态法

对所选有向键 `i → j` 的一个有序轴对 `αβ`，置 `S_i = ±S_i0 e_α`、`S_j = ±S_j0 e_β`，其他自旋保持固定。用已对齐的电子偶极计算

```text
Pij[α,β] = (D++ + D-- − D+- − D-+) / (4 S_i0 S_j0)
```

单位方向自旋下分母为 4。混合差分消去常数和只依赖一个翻转符号的项。在二次模型下，每个 `αβ` 得到一个 Cartesian 偶极三分量。更高阶多自旋项也可能随两个符号一起变号，可用另一背景或等价键交叉检验。完整张量的有序轴对为 `xx xy xz yx yy yz zx zy zz`，每个轴对四态。交换键端点时交换两个自旋指标，并追踪周期像与坐标变换。

格点间张量可含各向同性交换收缩、反对称自旋流和对称各向异性项。具体结构若有键中点反演，可用该对称性约束代表张量。若只拟合 `M(S_i × S_j)`，记录反对称假设，`M` 的三列分别是 `Pij[yz]`、`Pij[zx]`、`Pij[xy]`。BiFeO₃ 的历史模型保留九个有序轴对。求和时每条唯一周期键计算一次，保留其约定方向，反向记录不再重复计入。

## `Pi` 单格点张量的正反自旋拟合

固定几何和背景，仅将一个代表格点置于 `+n` 与 `−n`。取 `[D(+n)+D(−n)]/2` 消去二次模型中关于该格点自旋为奇的格点间项。方向可选 `x,y,z,(x±y)/√2,(x±z)/√2,(y±z)/√2`，共九组正反样本。对单位自旋，各偶极分量拟合同一设计矩阵

```text
[1, nx²−nz², ny²−nz², 2 nx ny, 2 nx nz, 2 ny nz]
```

系数依次为常数背景和 `Pi_xx, Pi_yy, Pi_xy, Pi_xz, Pi_yz`，令 `Pi_zz = −(Pi_xx + Pi_yy)`。固定自旋长度时各向同性对角部分与背景常数简并，采用无迹规范。`Pi` 的两自旋指标对称，完整张量收缩已将非对角项计入两次，写 PASP 行时直接写拟合张量分量。该设计应满秩 6，记录奇异值、残差与使用的自旋幅值。常数背景用于拟合，绝对极化零点另用对齐分支的参考计算给出。用未参与拟合的磁态或不同磁性背景检验迁移性。

## 自旋力、应力与晶格参数

当目标是让 PASP 从磁序求结构响应时，按目标交换模型选择相应的四态。令 `Q(X) = (X++ + X-- − X+- − X-+)/(4 S_i0 S_j0)`。在 `E_spin = +J S_i·S_j` 的标量交换模型下，用合适的共线四态可由 `Q(E)` 提取 `J`，用 `−Q(F)` 提取 `dJ/du`。若 VASP 应力 `σ` 采用压缩为正的约定，用 `−Ω Q(σ)` 提取 `dJ/dη`，其中 `Ω` 是 DFT 超胞体积，应力须转成能量密度。VASP `kbar × Å³` 到 `eV` 的因子约为 `0.00062415`。SOC 下某个共线轴对一般只识别该轴的对角交换分量。用于标量 `J` 前要验证各向同性近似，或另按交换模型提取各向异性分量。符号、重数和自旋归一化随实际能量模型一起核对。

- 按同一交换编号写 [`spin_exchange.dat`](../reference/files/spin_exchange.dat.md)（含 `dJ/du`）和 [`spin_strain.dat`](../reference/files/spin_strain.dat.md)（含 `dJ/dη`）。核对力数组原子顺序、应力收敛、Voigt 顺序及剪切定义。可用少量独立位移／应变有限差分核对导数符号和量级。
- 用 DFPT 或有限差分获得力常数、Born 有效电荷、离子钳制弹性与压电张量、内应变耦合。PASP 对应 [`FORCE_CONSTANTS`](../reference/files/FORCE_CONSTANTS.md)、[`SPOSCAR`](../reference/files/SPOSCAR.md)、[`Zeff.dat`](../reference/files/Zeff.dat.md)、[`elastic.dat`](../reference/files/elastic.dat.md)。核对原胞到超胞映射、Born 张量指标、ASR 选择、声学零模、应变边界条件和体积。启用 `spin_lat.spin_int_stress T` 时遵循当前 L8 状态机的单 MPI rank 限制。
- 若已有参考和目标结构，采用同一原子映射去掉仿射形变，得到周期边界下的内部位移 `Δu`。BiFeO₃ 的小形变实现用解包后的分数坐标差乘参考行晶格矩阵 `A0`。一阶 `D_Born[a] = Σ Z*[i,a,b] Δu[i,b]`，`Z*` 以 `e`、`Δu` 以 `Å` 计。行晶格矩阵下，形变梯度 `F = A.T @ inv(A0.T)`，小应变 `ε = (F + F.T)/2 − I`。历史压电列约定为 `εxx, εyy, εzz, 2εxy, 2εyz, 2εzx`，实际取用前按张量来源核对。用 clamped-ion 压电张量将应变转换成极化，再用参考体积转成偶极。这样内部弛豫只由 Born 项计入一次。该路线直接使用已知位移和应变，无需求解力常数和交换导数。

## PASP 输入与结果交接

1. **保存提取结果。** 交付逐态来源表、Berry 校正、单位、自旋归一化、结构和对称性映射、拟合张量及拟合／收敛证据。独立记录 DFT 原始代表值、提交给 PASP 的代表值和 PASP 实际采用的对称化值。迁移到新材料、磁性背景或较大变形时用独立数据验证。
2. **构造 PASP 候选。** `Model KNB` 中 [`GKNB_inter_site`](../reference/params/GKNB_inter_site.md) 每个代表键写两个 Cartesian 坐标、拟合局域轴和九行 `xx xy xz yx yy yz zx zy zz` 三分量；[`GKNB_single_site`](../reference/params/GKNB_single_site.md) 每个代表格点写坐标、拟合局域轴和六行 `xx yy zz xy xz yz` 三分量。张量以 `e Å` 偶极系数写入。核对 [`GKNB.local_axis`](../reference/params/GKNB_local_axis.md) 与代表值的拟合坐标，以及 `GKNB.symP` 是否适用目标结构的对称性。局域基变化涉及两个自旋指标和输出偶极指标。按实际 `cell.str`、`unit_cell.str` 与 `SuperCell` 关系生成或映射 `spin3.in`，确认 PASP 实际使用的自旋长度符合拟合约定。
3. **用原生 PASP 验证。** 验证新张量时，对参考磁态和独立目标态运行 `Model KNB`，核对方向、代表格点及键数、对称化和实际磁序。用 `spin_FE: Dipole is` 核对胞总电子偶极，用 `Intersite P` 等看分解。必要时用同一结构和自旋对比独立张量收缩，检查坐标、归一化、键计数和打印精度。对 `Model Spin_lattice_interaction` 核对 `Total P_{ion+lattice}`、力／应力分解和位移／应变尺度。PASP 正常结束后，仍需用独立物理数据检查响应的合理性。
4. **统一参考再组合。** 电子自旋差值取目标减参考的 PASP B1 偶极。冻结电子张量时，将目标和参考自旋映射到同一参考几何，保持两次 KNB 的键集和对称性一致。加上同一参考和物理口径下的结构贡献。报告绝对铁电极化时还需要在共同 Berry 分支上的参考零点。明确每个结果是超胞偶极、极化密度还是极轴投影。`D[e Å]` 转为 `P[μC/cm²]` 用 `1602.1766 D / Ω[Å³]`。PASP 日志中的 `μC/m²` 除以 `10^4` 得到 `μC/cm²`。记录体积基准及固定参考偏移的来源。

## Command-line helper

[fit_l8_polarization.py](../scripts/fit_l8_polarization.py) takes completed static VASP calculations and exports candidate `GKNB.fdf` blocks and `fit_report.json`. It requires Python 3.11+ and NumPy. Set `PASP_SKILL_ROOT` to the directory containing the loaded `SKILL.md` before running these commands from your calculation workspace.

```bash
python "$PASP_SKILL_ROOT/knowledge/scripts/fit_l8_polarization.py" template both > states.json
# Edit states.json with the DFT directories and representative atom numbers.
python "$PASP_SKILL_ROOT/knowledge/scripts/fit_l8_polarization.py" fit states.json l8_fit
```

- Choose `template pij` or `template pi` for one term. Each invocation handles one representative per selected term. Use 1-based POSCAR atom numbers. `pij.sites` gives the ordered pair and `image_j` gives the integer lattice translation of the second endpoint relative to the first. Fit only pairs isolated by the DFT design. To use multiple representatives, combine their entries under one block with the correct count before preflight.
- State paths are directories containing `POSCAR` and `OUTCAR`, relative to the manifest or absolute. `pij` expects the nine Cartesian axis pairs and `++`, `+-`, `-+`, `--` for each. `pi` uses `plus` and `minus` states for each listed direction. `xpy` means `(x+y)/sqrt(2)`, `xmy` means `(x−y)/sqrt(2)`, and so on. The fit uses fixed unit spins defined in global Cartesian coordinates and writes identity fitting axes.
- The script checks the final EDIFF marker and dipoles in static runs, matches the reported geometry against POSCAR, and records incomplete timing footers as warnings. Check insulating behavior, actual spin directions and background, consistent DFT settings, and the ordered-bond mapping against the original DFT output. The JSON contains raw and corrected dipoles and the single-site fit residuals.
- Automatic Berry alignment assumes small changes from the first state. In a skew or elongated cell the acceptance radius is half its shortest cell height. To use shifts already resolved from physical evidence, replace each path in the alignment group with a record such as `{"directory": "pij/xy/upup", "berry_shift": [0, 0, 0]}`. The shift is subtracted in lattice-vector units. Supply shifts for all four members of the affected `pij` quartet or all `pi` states.
- The output path must be new. For PASP preflight, check that `GKNB.fdf` coordinates and axes match the calculation cell and the current block layout. Include the file once with `%include GKNB.fdf` in the candidate `Model KNB` input, or merge its blocks into existing ones. Run PASP to evaluate polarization.

## BiFeO₃ 实作记录

- BFO400 的材料参数来自 V06/V07 的 36 个固定结构 SOC 四态（80 原子，代表 Fe18→Fe25 的近邻键），V13 的 18 个 Fe18 单格点 SOC 正反态，以及 V04a 的一次 10 原子 DFPT/PEAD Born 与 clamped-ion 压电计算。`GKNB.symP T` 的历史 PASP 结果包含两个局域单格点代表和 48 条唯一近邻键。原始拟合代表与 PASP 后的实际参数分别归档。V13 只有电子收敛和最终偶极证据，缺少正常结束尾部。早期背景按 Fe 编号奇偶交替，后续才核实真实 G-AFM 子晶格的映射。V14 的真实 G-AFM 检验中，加入 `Pi` 并未普遍改善误差。
- BFO400 在 V09 极性结构附近展开，以 V20 中心对称端点为零点。使用实际给定几何算 Born 与 clamped-ion 压电响应，自旋部分为 `Pi/Pij(目标磁态)−Pi/Pij(参考磁态)`，再加已有 DFT 分支差确定的固定零点转换。85 个历史原生 PASP 算例用于核对电子张量收缩，最大分量差约 `8.16×10⁻⁶ e Å`。400 点用冻结参数的后处理评估，计算对象是整个 80 原子胞的偶极。独立测试标签的整数分支选择使用了 Born/压电先验。如果重现此测试，保持其公共晶胞、零点和单位口径。
- V19 端点比较直接用两个 DFT 结构的位移和应变求 Born／压电贡献。另有一套原生 B2 PASP 算例用 V06 力／应力和 V04a/V04b 响应预测形变，单 rank 正常结束，报告的最大应变约 4.88%，量级显著大于 V19 的实际形变。面向已有几何的预测和由磁序求平衡结构的预测应各自用同目标的 DFT 数据检验。

来源为 PASP 第 8 讲原 PDF 第 14–17、29–30 页，以及 `universaldipole2/BiFeO3/analysis/bfo_paper_package_20261016/docs/METHODS.md`、同包 `parameters/raw_extraction/`、`BiFeO3/analysis/bfo400_pasp/Attempt-001/README.md`。历史原始工作目录中的 `polarization_coefficient_extraction/{pij,pi,born,piezo}/scripts/`、`04_pasp_model/runs/b1_nn_pi_validation_run-001/` 和 `04_pasp_model/table2_comparison/` 提供提取及运行证据。运行本 skill 只需要这里整理的规则和当前材料的输入／输出。
