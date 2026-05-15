# L3 Effective Hamiltonian Run Notes

这份文件记录 L3 effective Hamiltonian workflow 在历史服务器实跑或完整样例整理中观察到的**实例值**、**目录差异**、**脚本修正点**和**日志现象**。

它不是运行时 workflow 契约，也不是用户当前 workspace 的实时状态。

使用原则：
- 当前用户目录是否已有某个文件，必须以当前 workspace 实际存在的文件为准
- 当前运行会不会产生某个具体数值，必须以本次任务输入和真实运行结果为准
- 本文件中的编号范围、能量值、KPOINTS、local mode 数、训练/测试切分等都只是历史实例
- subagent 摘要只有在已压缩成历史观察时才能写入本文件；必须标注来源 run / log 路径、发生条件、是否已回写为稳定 workflow 契约
- 不得把 subagent 摘要写成当前用户 workspace 的实时事实，也不得把一次 output validation 结果升级成所有后续 run 的稳定结论

subagent 摘要进入本文件时建议使用：
- `来源`: run / log / 输出目录路径
- `发生条件`: stage、输入设置、样本范围或关键开关
- `观察`: 可复查的文件、日志现象或输出形态
- `边界`: 哪些只是实例值，哪些已沉淀回 workflow / reference

## Step 3：生成随机样本与原始特征

### 历史实跑观察
- PASP 直接在运行目录 `0.generaterandomspin/input/` 下生成样本文件，而不是先落到 `test/` 子目录
- 当 `PASP.input` 中 `local_mode.nstr_random = 10` 时，某次实跑得到：
  - `1..10.ene_symbol`
  - `1..10.vasp_MAGMOM`
  - `1..10.vasp`
  - `1..10.distortion`
  - `1..10.cell_info`
  - `1..10.amp_local_mode`
- 同一次实跑的 `log.out` 显示 `Total number of local modes (excluding strain): 9`
- 因此该次实跑还得到：
  - `local_mode-1..9.xsf`
  - `imode-orig-1..9.xsf`
  - `imode-rot-1..9.xsf`
- 同次运行还出现了这些辅助文件：
  - `PASP.used_info`
  - `seed_used.in`
  - `fort.10`
  - `fort.901`
  - `def_local_modes.dat`
  - `all_interaction_type*.dat`
  - `NN_O.dat`
  - `orig.pos`

### 历史脚本修正
- `postprocess.sh` 模板里写死的 `test/${i}.ene_symbol`、`test/${i}.vasp_MAGMOM` 与真实目录布局不一致
- 实际运行时，源文件直接出现在 `0.generaterandomspin/input/`

### 解释边界
- `1..10.*` 与 `1..9.*` 是某次输入设置下的实例值
- 稳定契约仍然只是：
  - 会出现按样本编号命名的文件族
  - 可能出现按 local mode 编号命名的文件族

## Step 4：整理 DFT 数据

### 历史实跑观察
- `createINCAR.sh` 可以从 `../0.generaterandomspin/vasp_MAGMOM/` 动态生成 `INCAR_all/INCAR_<id>`
- 某次 L3 workflow 验证里，为样本 `1..10` 都整理出了可提交目录
- 当时采用的第一版验证 `KPOINTS` 是 `Gamma 5x5x1`
- 同次目录中实际保留的预计算数据只覆盖 `2.get_dft_data/1`、`2`、`3`
- 这三个样本目录里都包含 `OUTCAR` 和 `OSZICAR`

### 历史输出实例
- `INCAR_all/` 可以按样本编号生成 `INCAR_1..10`
- `get_ene.sh` 可以从当前存在的编号目录动态提取能量，不必写死 `1..3`
- 某次保留的样本 `1..3` 成功生成了 `Energy.dat`
- 该次 `Energy.dat` 第一行的 primitive cell 数实例值为 `9`
- 同次从 `OUTCAR` 最后一条 `TOTEN` 提取出的能量分别为：
  - sample `1`: `-358.44402505 eV`
  - sample `2`: `-358.29960579 eV`
  - sample `3`: `-358.38224449 eV`

### 历史脚本修正
- `createINCAR.sh` 需要按真实样本数动态遍历 `vasp_MAGMOM/`，不能写死 `1..2`
- `get_ene.sh` 应按当前存在的编号目录动态遍历
- `Energy.dat` 第一行保留 primitive cell 数，后续各行记录 `<sample_id> <TOTEN>`

### 路径 B 起点样例：扁平最终 DFT 结果集
- 某次作者验证中使用过一类**扁平的最终 DFT 结果集**
- 观察到的稳定特征是：
  - 目录下直接存放连续编号的 `*.OUTCAR`、`*.OSZICAR`、`*.log`
  - 有时同层还会附带一个共享 `POSCAR`
  - 没有路径 A 常见的 `ene_symbol/`、`vasp_MAGMOM/` 或样本子目录
- 这类目录更适合作为**路径 B 的自然起点**，而不是继续假定它还会回到路径 A

### 从该样例静态确认的可提取信息
- `OUTCAR` 最后一条 `TOTEN` 可直接提取到 `Energy.dat`
- `OUTCAR` 中存在非共线 `magnetization (x/y/z)` block，可直接导出逐原子 `distortion.MAGMOM`
- `OUTCAR` 中存在最终 `POSITION ... TOTAL-FORCE` block 和最终 `direct lattice vectors` block，可直接回写 POSCAR 风格的 `distortion.pos`
- 即使没有额外保存的 `POSCAR`，`OUTCAR` 里也能通过 `ions per type` 与 `VRHFIN` 恢复物种顺序和原子数；共享 `POSCAR` 只是更稳妥的辅助参考

### 由该样例沉淀回脚本层的稳定结论
- `get_ene.sh` 不应只支持 `1/OUTCAR` 这类样本子目录，也应支持扁平的 `<id>.OUTCAR` 结果集
- 路径 B 输入整理不应把共享 `POSCAR` 写死成前置条件；更稳妥的 helper 应优先尝试直接从 `OUTCAR` 恢复 `distortion.pos` / `distortion.MAGMOM`
- `distortion.pos` 更像逐样本输入，而不是一个天然的多样本总表；对于 `0..799` 这种结果集，更稳妥的是写成逐样本输入包，例如 `path_b_inputs/<id>/distortion.pos` 与 `distortion.MAGMOM`

### 解释边界
- 上述结论只说明这类扁平最终 DFT 结果集已经足够支持**进入路径 B 的整理阶段**
- 它不等于已经替当前材料完成了共享基底 `PASP.input` 确认，也不等于已经具备可复用的 `local_mode_PM.dat`

## Step 5：生成拟合数据集

### 历史目录组织观察
- `3.get_fitting_data/ene_symbol/` 来自 `0.generaterandomspin/ene_symbol/`
- `3.get_fitting_data/Energy.dat` 来自 `2.get_dft_data/Energy.dat`
- `3.get_fitting_data/` 更像“汇总与转换入口”，而不是重新生成 `ene_symbol` 或重新提取能量的地方

### 历史完整样例
- `3.get_fitting_data/all_data` 中曾保存过一个完整样例
- 其中：
  - `ene_symbol/` 覆盖连续编号 `1..1000`
  - `Energy.dat` 第一行是标题，后续覆盖连续编号 `1..1000`
  - `convert_info.txt` 的实例值为 `700`、`300`、`9`
  - `convert_data.py` / `convert_data.f90` 会把样本 `1..700` 写入 `Fitting_Dataset.txt`
  - `convert_data.py` / `convert_data.f90` 会把样本 `701..1000` 写入 `Fitting_Data_for_prediction.txt`
  - `convert_data.py` / `convert_data.f90` 会把读到的能量除以 `convert_info.txt` 第三行的扩胞数；该完整样例中即除以 `9`

### 历史阶段性约束
- 当 DFT 还没全部算完时，`ene_symbol` 样本总数可以暂时大于 `Energy.dat` 已覆盖的样本数
- 这种“不完全覆盖”在 workflow 推进中是正常中间状态
- 真正需要保证的是：凡是已经写入 `Energy.dat` 的样本编号，都必须能在 `ene_symbol/` 中找到同编号文件
- 当前推荐优先使用 `convert_data.py`，避免依赖 Fortran 编译器或 Intel MPI 运行库

## Step 6：配置并执行拟合

### 历史拟合日志观察
- `log.out` 会打印初始读取到的 `Nn,Nd`
- 当 `Fitting_Settings.txt` 中 `I_CHECK_DATA=1` 且数据检查发现成比例或冗余变量时，PASP 可能打印 `WARNING ::: NEED TO REWRITE DATA::`
- 这种重写发生在 Step 6 拟合阶段，不应归因于 Step 5 的 `convert_data.py`
- 重写原因可在 `Data_Special_Properties_<原始维度>.txt` 中查看
- 变量映射可在 `Data_Variables_Mapping_(1st Reducing)_<原始维度>.txt` 中查看

### 历史实例值
- 某次验证中，输入数据先读到 `Nn=1000, Nd=528`
- 随后因第 `209` 个变量与 `#53` 成比例、第 `211` 个变量与 `#95` 成比例，重写为 `Nd=526`

## 维护说明

后续如果还有新的服务器实跑观察：
- 追加到本文件，不要重新混回 `l3_effective_hamiltonian.md`
- 尽量标清是“历史实例值”“脚本修正”还是“阶段性观察”
- 不要把本文件里的实例值写成稳定契约
