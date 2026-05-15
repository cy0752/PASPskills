这些脚本是从 Lecture 3 examples 提炼出来的**辅助脚本模板**，用于帮助组织 effective Hamiltonian 工作流中的外部数据处理。

包含：
- `postprocess.sh`：整理 PASP 生成的 `ene_symbol` 与 `vasp_MAGMOM`
- `createINCAR.sh`：把 `vasp_MAGMOM` 约束拼接进 VASP `INCAR`
- `get_ene.sh`：从各样本目录的 `OUTCAR` 提取总能并生成 `Energy.dat`
- `run_method6_batch.sh`：Path B / method-6 的逐样本顺序批跑模板
- `extract_magmoms.py`：从 `OUTCAR` 提取最终逐原子磁矩，比较是否仍与输入 `MAGMOM` 近似平行，并可直接导出 `distortion.MAGMOM`
- `prepare_path_b_inputs.py`：从单个或批量 `OUTCAR` 中逐样本整理路径 B 所需的 `distortion.pos` / `distortion.MAGMOM`，并可选写出共享 `Energy.dat`
- `rebase_unit_cell.py`：在已经确认 primitive / 轴向映射后，同步重排 `unit_cell.str` 的基矢和原子坐标，或修复“基矢已重排但原子坐标仍是旧轴序”的候选文件，并用用户提供的 unit-cell → `cell.str` 关系矩阵做映射验证。注意这个验证矩阵不是 PASP `%block SuperCell`；PASP `SuperCell` 是基于 `cell.str` 继续扩胞。
- `convert_data.py`：免编译地把 `ene_symbol/` 与 `Energy.dat` 转换成 `Fitting_Dataset.txt` 和 `Fitting_Data_for_prediction.txt`
- `convert_data.f90`：把 `ene_symbol/` 与 `Energy.dat` 转换成 `Fitting_Dataset.txt` 和 `Fitting_Data_for_prediction.txt`

注意：
- 这些脚本不是 PASP 核心功能本身，而是 examples 中用于衔接外部 DFT 计算的模板。
- 复制到服务器后，通常需要按你的目录结构、样本编号范围、VASP 输出格式、作业系统环境调整。
- 对 `run_method6_batch.sh` 这类批处理模板，skills 应沉淀的是“外层设一次环境 + `for` 循环逐样本复制输入并执行 `PASP.x`”这种简洁思路，而不是某次任务里带有固定路径、固定共享基底 run 和固定编号范围的现场脚本原样副本。
- 不要默认给这种脚本加全局 `set -u`、`set -euo pipefail` 或复杂 strict-mode 框架。集群环境初始化脚本和库路径变量经常依赖“变量可为空”的 shell 语义；strict mode 容易让任务在进入样本循环前退出。更可靠的最小检查是：关键输入文件存在、每个样本有 `log.out`、批量目录有 `batch.log` / `status.tsv`，并按样本记录 `ok` / `failed`。
- 最关键的是保持样本编号、`ene_symbol/<id>.ene_symbol`、`Energy.dat` 三者一致。
- 对 Path B 还要记住：method-6 当前样本目录里产出的文件名通常是 `distortion.ene_symbol`，进入 `3.get_fitting_data` 时应统一汇总和重命名为 `ene_symbol/<id>.ene_symbol`

`run_method6_batch.sh` 常见用途：

- 当 `0.shared_basis/` 已经生成可复用的 `local_mode_PM.dat`
- 当 `path_b_inputs/<id>/` 已经为每个样本准备好 `distortion.pos` 和条件性的 `distortion.MAGMOM`
- 当 method-6 本身很快，用户只需要最直接的顺序 `for` 循环批跑，而不是复杂调度逻辑
- 基于当前 L3 服务器实跑，`0.generaterandomspin/input/` 会直接生成原始 `*.ene_symbol` 与 `*.vasp_MAGMOM`；如果脚本模板仍假设源文件位于 `test/` 子目录，需要先按真实目录布局修正再使用。
- `get_ene.sh` 当前同时支持两类 Step 4 目录布局：
  - 编号子目录：`1/OUTCAR`、`2/OUTCAR`、...
  - 扁平结果集：`1.OUTCAR`、`2.OUTCAR`、...；这对批量 `OUTCAR` 的路径 B 起点尤其常见
- `convert_data.py` / `convert_data.f90` 读取 `convert_info.txt` 的前三行作为训练集数、测试 / 预测集数和每个 DFT 超胞中包含的原胞个数；第三行是能量归一化除数，不是 `unit_cell.str` 的原胞原子数。它们要求 `ene_symbol/<start-id>.ene_symbol` 开始的连续编号文件存在，并跳过 `Energy.dat` 第一行标题后按同样编号顺序读取能量。
- 例如 `unit_cell.str` 有 32 个原子、`cell.str` / POSCAR / OUTCAR 是 64 原子且对应 2 个原胞时，`convert_info.txt` 第三行应写 `2`，不是 `32`。若 DFT 能量已经预先按原胞归一化，则需要明确使用 `convert_data.py --no-energy-divide`，而不是把第三行改成原胞原子数。
- `Energy.dat` 的样本编号本身没有固定必须从 0 或 1 开始；硬要求是 `Energy.dat`、`ene_symbol/<id>.ene_symbol` 和转换脚本的起始编号完全一致，并且当前选择的样本编号连续。
- `convert_data.py` 按 `Energy.dat` 第一列的 sample id 建表，因此 `Energy.dat` 行顺序可以乱序，只要没有重复编号且所需编号都存在；但未修改的 `convert_data.f90` 是按文件行位置顺序读取并忽略第一列编号校验，乱序 `Energy.dat` 会造成能量和 `ene_symbol` 错配。
- 生成 `convert_info.txt` 时，如果用户没有指定切分，默认按 90/10 拆分当前可用连续样本：`Ntrain=floor(0.9*N)`，`Ntest=N-Ntrain`。例如 800 个样本应写为 `720` 和 `80`，不要默认写成 `800` 和 `0`。
- 如果当前样本编号是从 `0` 开始的连续编号，例如某些扁平 `results/<id>.OUTCAR` 目录，可在 `convert_data.py` 中使用 `--start-id 0`，不必先手工重编号。
- 优先使用 `convert_data.py`，因为它不依赖 Fortran 编译器或 Intel MPI 运行库。示例：`python3 convert_data.py --workdir .`
- `convert_data.f90` 保留为原始 example 逻辑来源；复制来的 `convert_data` 二进制依赖 Intel MPI 运行库（如 `libmpifort.so.12`），通用本地 shell 可能无法直接运行。未修改的 `convert_data.f90` 默认打开 `ene_symbol/1.ene_symbol`，并以 1-based 样本序列读取；若当前数据是 0-based，必须改用 `convert_data.py --start-id 0` 或显式改写 Fortran 起始编号逻辑，不能直接套旧二进制。
- `convert_data.py` 只负责把全部 `ene_symbol` 特征与能量拼接起来，不应根据某个旧 example 的拟合输入列数主动删除或跳过特征。
- 如果后续拟合目录中的 `Fitting_Dataset.txt` 在 PASP 运行后列数减少，先检查拟合阶段 `log.out` 是否出现 `NEED TO REWRITE DATA`，以及 `Data_Special_Properties_*.txt` 是否记录成比例或冗余变量；不要把这种 Step 6 数据检查重写误认为 Step 5 转换脚本的问题。

`extract_magmoms.py` 常见用法：

- 比较 VASP 最终磁矩方向是否仍和输入 `vasp_MAGMOM` 逐原子近似平行：
  - `python3 extract_magmoms.py sample/OUTCAR --reference ../0.generaterandomspin/vasp_MAGMOM/1.vasp_MAGMOM --show-all`
- 从 `OUTCAR` 直接导出路径 B 所需的 `distortion.MAGMOM`：
  - `python3 extract_magmoms.py sample/OUTCAR --distortion-out distortion.MAGMOM`

`rebase_unit_cell.py` 常见用法：

- 只验证当前 `unit_cell.str` 是否能通过已确认的 unit-cell → `cell.str` 关系矩阵映射到 `cell.str`：
  - `python3 rebase_unit_cell.py --cell cell.str --unit unit_cell.str --relation '2 0 0;0 1 0;0 0 1'`
- 如果已确认需要把 primitive 轴序从旧的 `x,y,z` 改成新的 `y,z,x`，同时重排基矢和原子坐标：
  - `python3 rebase_unit_cell.py --cell cell.str --unit unit_cell.str --relation '2 0 0;0 1 0;0 0 1' --reorder-axes y,z,x --output unit_cell.rebased.str`
- 如果候选 `unit_cell.str` 的基矢已经是目标轴向，但原子坐标仍被错误写成 `y,z,x`，只修复原子坐标分量。例如要把当前 `(y,z,x)` 坐标还原为 `(x,y,z)`，使用 `z,x,y`：
  - `python3 rebase_unit_cell.py --cell cell.str --unit unit_cell.str --relation '2 0 0;0 1 0;0 0 1' --reorder-atom-coords z,x,y --output unit_cell.fixed.str`
- 不要把 `--relation` 的矩阵直接写进 PASP `%block SuperCell`。如果 `cell.str` 已经是目标超胞，PASP `%block SuperCell` 通常应省略或保持单位阵。
- 这个脚本不负责决定 primitive cell 或物理轴向。使用前必须已有用户确认、read-only structure subagent 结论、PASP 分析结果或其他可核查来源。
- 通过标准是报告 `PASS: cell.str is compatible with unit_cell.str under the provided relation`。若报告 `FAIL`，不得把候选 `unit_cell.str` 提升为正式 input，也不得派生 run 或提交。
- 同时做对比并导出，若存在逐原子方向不一致会以非零退出码返回：
  - `python3 extract_magmoms.py sample/OUTCAR --reference 1.vasp_MAGMOM --distortion-out distortion.MAGMOM`

补充说明：
- `--reference` 同时支持 `MAGMOM= ...` 形式的 VASP 输入文件，以及逐行 `x y z` 的 `distortion.MAGMOM`
- 默认把模长小于 `0.1` 的向量视为非磁性；可用 `--min-norm` 调整
- 默认用 `cos(theta) >= 0.95` 判定“方向近似平行”；可用 `--cos-threshold` 调整
- 如果只在 `OUTCAR` 中找到单个磁矩分量块，脚本会按 collinear 模式处理，并提示输出向量被写成 `(m, 0, 0)`

`prepare_path_b_inputs.py` 常见用法：

- 仅凭单个 `OUTCAR` 整理一个路径 B 输入包：
  - `python3 prepare_path_b_inputs.py sample.OUTCAR --output-dir path_b_inputs`

- 如果额外有 `POSCAR`，可把它作为更稳定的物种顺序 / 原子数参考：
  - `python3 prepare_path_b_inputs.py sample.OUTCAR --poscar-reference POSCAR --output-dir path_b_inputs`

- 从扁平 `results/<id>.OUTCAR` 目录批量整理路径 B 输入包：
  - `python3 prepare_path_b_inputs.py results --poscar-reference results/POSCAR --output-dir path_b_inputs`

- 如果只有批量 `OUTCAR`、没有单独保存的 `POSCAR`，也可以直接批量整理：
  - `python3 prepare_path_b_inputs.py results --output-dir path_b_inputs`

- 同时从批量 `OUTCAR` 生成共享 `Energy.dat`：
  - `python3 prepare_path_b_inputs.py results --poscar-reference results/POSCAR --output-dir path_b_inputs --primitive-cells 9`

补充说明：
- 该脚本会为每个样本写出独立子目录，例如 `path_b_inputs/17/distortion.pos` 和 `path_b_inputs/17/distortion.MAGMOM`
- `distortion.pos` 默认写成 POSCAR 风格的 `Cartesian` 坐标，直接复用 `OUTCAR` 最终晶格和最终原子坐标
- 如果没有提供 `--poscar-reference`，脚本会优先从 `OUTCAR` 的 `ions per type` 与 `VRHFIN` 信息中恢复物种顺序和原子数
- 如果你确认下游更适合分数坐标，可加 `--coordinate-mode Direct`
- 这类输出是路径 B 的**逐样本输入包**，不是已经完成共享基底确认的正式 `PASP.input`
