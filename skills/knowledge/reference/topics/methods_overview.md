# PASP 方法与 workflow 总览

本文档对应官网第 2 章“功能介绍”，用于回答“这个 PASP 方法族是做什么的、用哪个 `Model`、后续会接哪些输入/输出文件”这类问题。具体参数写法仍优先查 `params/`、`files/` 和第 3 章相关专题。

## 简单磁性体系有效哈密顿量

适合从若干磁构型能量中提取简单自旋模型，再做 MC 或局域优化。

常见流程：
- 用 `Model find_J_path_sym` 分析对称不等价磁性原子对。
- 根据代表性 pair 生成或组织磁构型，通常接 DFT 总能计算。
- 后处理得到交换参数，常见输入/输出文件包括 `spin_exchange.dat`、`J_best.dat`、`spin3.in`。
- 用 `Model Spin_lattice_interaction` 做 MC、CG 或指定构型能量评估。

查询入口：
- `modules/effective_hamiltonian.md`
- `files/spin_exchange.dat.md`
- `files/J_best.dat.md`
- `topics/MC.input.md`
- `params/magnetic_or_ligand.md`

## 一般性有效哈密顿量

适合构造包含局域模式、自旋、应变或其耦合项的更通用有效哈密顿量。第 3 章参数里对应的核心入口是 `Model Invariant`、`Model Fitting_one_order` 和后续 `Model atomic_effective_H`。

常见流程：
- 用 `Model Invariant` 定义自由度、对称性不变量、展开体数、截断距离和展开阶数。
- 用 `Model Fitting_one_order` 基于训练数据拟合相互作用参数。
- 用 `Model atomic_effective_H` 做 MC、CG 或 MD。

关键判断：
- 只有自旋有效哈密顿量时，`local_mode.mode_definition` 通常只写 `spin`，并为参与建模的磁性元素代表位点写三个自旋方向。
- 若包含铁电/位移/应变自由度，需要同时检查局域模式、应变、SOC 和拟合输入文件，而不是只套自旋模板。

查询入口：
- `modules/effective_hamiltonian.md`
- `params/local_mode.mode_definition.md`
- `params/fig.maxk.md`
- `params/fig.mdist.md`
- `params/Invariant.power.md`
- `topics/MC.input.md`
- `topics/MD.input.md`

## 全局结构搜索

PASP 支持遗传算法类的全局结构搜索。此类任务通常关注初始结构生成、遗传操作、磁性构型搜索、晶格或晶胞约束、以及并行策略。

查询入口：
- `modules/ga.md`
- `params/GA.population_size.md`
- `params/GA.max_generation.md`
- `params/GA.perturbation.md`
- `params/GA.magnetic.md`
- `params/GA.fixlattice.md`

## 紧束缚模型

PASP 的 TB 功能包括自定义 hopping 和 Slater-Koster 参数化两类。第 2 章解释方法关系，第 3 章给出输入字段。

查询入口：
- `modules/tb.md`
- `params/USE_Slater_Koster_Model.md`
- `params/Hop_Parameters.md`
- `params/Slater_Koster_Hop_Parameters.md`
- `params/Orbitals.md`
- `params/kgrid_Monkhorst_Pack.md`
- `params/BandLines.md`

## 自旋序诱导铁电性统一极化模型

用于从自旋结构计算极化，可包含格点间项、单格点项、局域坐标系、螺旋自旋结构，以及自旋-晶格耦合修正。

查询入口：
- `modules/knb.md`
- `params/GKNB_inter_site.md`
- `params/GKNB_single_site.md`
- `params/GKNB_local_axis.md`
- `params/GKNB.spiral.md`
- `params/spin_lat.spin_force.md`

## 线性自旋波色散

用于基于磁相互作用模型计算 magnon / spin-wave 色散。第 3 章主要给出 q 点路径输入。

查询入口：
- `modules/magnon.md`
- `params/number_of_qpoints.md`
- `params/qpoints.magnon.md`

## 使用建议

- 用户问方法原理、workflow 顺序、哪个 `Model` 连接哪个阶段时，先查本文档和 `toc/chapter2.md`。
- 用户问输入字段、默认值、block 格式时，切到 `params/INDEX.md` 和具体参数卡。
- 用户问文件格式或输出文件含义时，切到 `files/`。
- 用户问 lecture/example 的具体可运行配置时，以本地 example 目录为准，第 4 章官方实例只作为外部参考。

## 来源章节

- 官方文档: `2 功能介绍`
- 来源页面: https://hzwtech.com/PASP/2023A/build/html/2%E5%8A%9F%E8%83%BD%E4%BB%8B%E7%BB%8D.html

