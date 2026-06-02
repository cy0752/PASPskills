# L3 Effective Hamiltonian State Machine

本文件是 L3 workflow 的运行门禁。runtime agent 必须先执行这里的状态机；`l3_effective_hamiltonian.md` 只补充当前状态所需的文件、字段和检查细节，不能覆盖本文件的 STOP 条件。

## 核心原则
- 长 workflow 不是执行计划；本文件才是阶段推进顺序。
- `继续`、`implement the plan`、`按计划执行`、`你来定` 不等于确认 shared-basis 参数。
- `继续`、`ok`、`去提交` 也不等于确认拟合策略，除非 agent 已经先列出完整的拟合设置表并得到用户接受。
- `可以使用 subagent` 只表示允许委派只读事实检查，不等于确认 shared-basis 参数，不等于允许提交，不等于允许 agent 代填物理设置。
- inventory 不是 preflight。目录盘点、VASP 结果清点、脚本状态检查、日志摘要都不能替代输入文件 preflight。
- subagent 只能做只读事实检查，不能决定物理参数、不能改文件、不能提交任务。
- read-only subagent 任务统一使用 `skills/subskills/pasp-verifier/skill.md` 的契约；本文件只指定 L3 阶段门禁和 checklist。
- L3 中，只要用户已经授权 subagent，提交任务前、准备提交脚本前、派生 `<stage>/runs/<run-id>/` 前、提升或覆盖正式 `<stage>/input/` 前，read-only subagent input preflight 是硬依赖。主 agent 的本地检查不能替代它；如果 subagent 工具不可用，应 blocked 并请用户明确是否豁免这条 L3 硬门禁。
- 任何运行探测、外部任务创建、提交脚本生成或提交准备，都必须发生在 stage preflight pass 之后。
- 输出检查不是输入 preflight。运行后若要把结果交给下游，必须单独做 output validation。
- `notes/`、`drafts/`、`*.draft` 是未确认草稿区；`*.candidate` 或 candidate 目录是待 preflight 候选区；`<stage>/input/` 是正式输入基线；`<stage>/runs/<run-id>/` 是实际运行目录。这四类不能混用。
- L3 多阶段目录必须有落盘的进展与目录说明。README / PROGRESS 不是可选整理项；它是告诉用户当前阶段、路径判断、哪些目录可提交、哪些只是候选、哪些文件是下游 handoff 的目录契约。

## README / PROGRESS 硬契约
每次创建、提升、派生或完成一个 L3 关键目录时，必须同步写入或更新 README / PROGRESS；这不是最终收尾动作，而是状态机检查点的一部分。最低字段如下：
- `Status`：当前阶段、Path A / Path B / fitting-only 判断、是否 draft / candidate / formal input / run / handoff-ready。
- `File Roles`：本目录内关键文件分别是什么，哪些是输入基线，哪些是运行复制品，哪些是输出或下游 handoff。
- `Upstream` / `Downstream`：上游来源文件、样本编号规则、下游应该消费哪个文件或目录。
- `Gate Evidence`：用户确认记录、reference 格式比对、read-only subagent preflight / output validation 结论和证据路径。
- `Blocked / TODO`：仍缺哪些确认、哪些失败样本、哪些文件不能提交、下一步允许做什么。

目录级最低要求：
- workflow 根目录 `README.md` 或 `PROGRESS.md` 必须记录 S0 路径判断、全局阶段图、当前进展和下一 STOP gate。
- `<stage>/input/README.md` 必须记录正式输入基线从哪个 candidate 提升而来、通过了哪次 preflight、可否派生 run。
- `<stage>/runs/<run-id>/README.md` 必须记录实际运行命令/脚本、提交状态、输出验证结论和下游 handoff 文件。
- `path_b_inputs/README.md`、`ene_symbol/README.md` 等批量样本池必须记录编号映射、成功/失败统计、汇总文件来源和可清理项。

没有 README / PROGRESS 或字段缺失时，不得把目录描述为 submit-ready、formal input、validated output 或 handoff-ready；只能描述为草稿 / blocked，并补齐记录后再推进。

## 状态机

### S0：目标目录与路径定位
允许自动执行：
- 盘点当前目标目录、阶段目录、`OUTCAR` / `POSCAR` / 脚本 / 历史输出。
- 暂定判断 Path A / Path B / 拟合阶段 / 仅有 DFT 结果起点。
- 在 workflow 根目录写入或更新 `README.md` / `PROGRESS.md`，记录 S0 盘点结果、路径判断依据、当前阶段、已有目录、缺失项和下一步 STOP gate。该文件只能描述当前事实，不得把未 preflight 的候选目录写成 submit-ready。

路径命名硬规则：
- Path A 是 PASP 正向生成样本 / `ene_symbol` 后再配外部 DFT 能量的分支，不是“完整 L3 流程”的同义词。
- Path B 是把已有最终结构 / 磁态 / NCL-DFT 结果通过 method 6 编码回同一 shared basis 的分支。
- 若当前目标目录是扁平或外部的已完成 NCL-DFT 结果集，例如很多 `OUTCAR` / `OSZICAR` / `log`，且看不到当前目录自己的 `0.generaterandomspin/`、`1.vaspncl/`、`ene_symbol/`、`vasp_MAGMOM/`、`3.get_fitting_data/` 或 `4.fit/` 链，必须先判为 Path B 起点。缺少 shared-basis 或 `local_mode_PM.dat` 是 Path B readiness blocked，不是改判 Path A 的理由。
- S0 不检查提交平台、`subpasp*.sh`、PASP executable 或 Inspire 凭据来决定 Path A / Path B；提交准备必须在 S5 preflight pass 之后。

禁止：
- 写正式 `PASP.input`。
- 创建可提交的 `<stage>/input/`。
- 生成提交脚本或提交准备动作。

允许下一步：进入 S1，或在路径判断会改变文件链路时先问用户确认。

如果用户是在复盘上一条回复的路径判断，例如问“为什么会判断成 Path A / Path B”“这不是明显是 B 吗”，这不是继续执行 workflow 的授权。此时只解释路径判断错误、正确判据和下一步建议；不得自动进入 S1、启动 subagent、读取更多任务文件或询问“现在进入 S1 可以吗”，除非用户明确要求继续执行。

### S1：整理候选材料与缺失项
允许自动执行：
- 提取能量、最终磁矩、样本编号、结构摘要。
- 生成缺失文件清单、候选代表点位分析计划、待确认问题。
- 在 `notes/`、`drafts/` 或 `*.draft` 中保存明确标注“待确认 / 不可提交”的候选材料。

优先委派给 `pasp-verifier` read-only subagent 的上下文重任务：
- 目标目录盘点（`mode: directory-inventory`，不能替代 input preflight）。
- 长 `OUTCAR` / 日志摘要。
- 输出文件清点和关键 warning / error 提取。
- `POSCAR`、候选 `POSCAR_UC`、`cell.str`、`unit_cell.str`、`SuperCell` 的结构关系分析。
- 模板与用户候选输入的结构差异对比。

禁止：
- 把候选材料放进正式 `<stage>/input/`。
- 把 README、脚本或目录说明写成 submit-ready。

允许下一步：若要进入 shared-basis，必须进入 S2；否则按当前 stage 的 preflight gate 继续。

### S2：Shared-Basis 参数确认（STOP REQUIRED）
进入 L3 shared-basis 前必须停止询问，除非用户已经逐项给出或明确接受一份逐项设置表。

必须确认：
- 参与自旋建模的元素与非磁性元素。
- `Spin_values`。
- `fig.maxk` 保留到几体。
- `%block fig.mdist` 每个体数的 Bohr 截断。
- `Invariant.power`、`Invariant.strain_power`、`Invariant.pure_strain_power`。
- 是否只做纯自旋，还是包含 strain / phonon / 其他自由度。
- 是否考虑 SOC；若考虑，是否使用默认完整 SOC 枚举，或是否需要显式限制 / 优先保留某些 SOC / DMI / 各向异性项。只有后一种情况才需要确认 `local_mode.special_SOC` 策略。
- `local_mode.mode_definition` 的代表点位来源。
- `POSCAR` / `cell.str` 是否为用于定义模式的原胞/primitive，或是否需要 `POSCAR_UC` / `unit_cell.str`。
- Path A 样本生成和后续 DFT 使用的目标超胞：确认 `cell.str` 本身是否已经是目标 DFT 超胞；若不是，确认 `%block SuperCell` 矩阵、目标原子数或目标 POSCAR 规模。不能因为 `cell.str = unit_cell.str` 或用户只提供了这两个文件就默认不扩胞。
- 如果走 Path A 正向生成样本：确认 `local_mode.cal_para_method = 1`，以及用户想要的随机构型数量 `local_mode.nstr_random` 或等价样本数。不要为了先得到 `local_mode_PM.dat` 而把 Path A 首跑拆成“预跑一次 + 再生成随机样本”两次。

用户确认后，记录：
- `USER_CONFIRMED_L3_SHARED_BASIS_PARAMS=true`
- 具体参数值、来源和未决项。

未满足时允许的唯一下一步：向用户列出缺失确认项。

### S3：代表点位确认（STOP REQUIRED）
写 `%block local_mode.mode_definition` 前，必须已有不等价代表点位证据。

可接受来源：
- 用户提供并确认的代表点位。
- PASP `find_J_path_sym` 或等价 PASP 对称性分析结果。
- agent 使用 pymatgen / spglib 等工具分析后交给用户确认的代表点位清单，必须包含结构来源、`symprec`、元素编号映射、multiplicity。

不可接受来源：
- 直接遍历 `cell.str`、`POSCAR`、半胞或超胞中的所有磁性原子。
- 用旧 example 的代表点位数量套当前结构。

确认后，记录：
- `REPRESENTATIVE_SITES_CONFIRMED=true`
- 代表点位、元素编号、multiplicity、tolerance 或 PASP 分析来源。

注意：如果当前 `POSCAR` / `cell.str` 确实是用于定义模式的 primitive，且所有参与磁性位点经分析确实全部不等价，则 mode 数可能等于“所有参与磁性原子数 × 3”。这不是自动错误；没有证据时才必须停止。

未满足时允许的唯一下一步：做代表点位分析并交给用户确认，或请用户提供代表点位。

### S3a：结构 / 原胞分析（DELEGATE PREFERRED）
当需要判断或生成 `POSCAR_UC`、`unit_cell.str`、primitive cell、`SuperCell` 关系或轴向重排时，优先把结构分析委派给 `pasp-verifier` `mode: structure-analysis`。

subagent 可做：
- 读取当前结构文件并判断是否可能已经是 primitive。
- 比较 `POSCAR`、候选 `POSCAR_UC`、`cell.str`、`unit_cell.str`、`SuperCell` 的轴向和原子映射。
- 给出候选 primitive / supercell mapping、`symprec`、体积比、元素顺序、坐标变换证据。
- 当 pymatgen / spglib 得到的 primitive 与当前 workflow 轴向不同但结构等价时，优先求 rebase / transformation mapping，而不是丢弃自动 primitive。
- 报告 primitive rebase 矩阵 `T`，以及超胞到 primitive 的整数矩阵 `M`（或说明为什么不能唯一确定）；同时报告 `det(M)`、体积比、物种计数、原子映射 tolerance 和最大残差。
- 汇报 pass / fail / blocked 和证据路径。

subagent 不可做：
- 把候选 primitive 直接写成正式 `POSCAR_UC` / `unit_cell.str`。
- 未经用户确认改变结构输入路线，例如从 `cell.str` 路线切到 `READ_POSCAR` 路线。
- 在轴向或 primitive 关系 blocked 时继续生成正式 shared-basis 输入。
- 仅因自动 primitive 的轴顺序不同就否定该 primitive。
- 在没有 transformation mapping 或用户确认的情况下，手工假设“沿 x/y/z 切半”或构造保轴 primitive。

主 agent 审核 subagent 结论并得到必要确认后，才能写候选结构文件；候选结构文件仍必须进入 S5 preflight。

若 `T` / `M`、原子映射或目标轴向不能唯一确定，结构分析结论必须是 `blocked`。此时允许的唯一下一步是向用户确认 primitive cell、超胞矩阵或 `cellabc` 约定；不得继续生成正式 shared-basis 输入。

### S3b：Fitting 设置确认（STOP REQUIRED）
进入 L3 `4.fit` 拟合阶段前，如果要创建或覆盖正式 `4.fit/input/`、派生 `4.fit/runs/<run-id>/`、准备提交脚本、创建外部任务或提交运行，必须先停止询问，除非用户已经逐项给出或明确接受一份逐项拟合设置表。

默认数据切分策略：
- 如果用户没有指定训练 / 测试 / 预测切分，默认按 90/10 拆分可用样本：`Ntrain=floor(0.9*N)`，`Ntest=N-Ntrain`。
- 例如 800 个连续样本默认写成 `720` 训练、`80` 测试 / 预测，而不是 `800/0`。
- 只有用户明确要求全量训练、无测试 / 预测时，才允许 `Ntest=0`。

必须确认或记录：
- 当前拟合目标：只打通流程、正式拟合、筛选稀疏模型，或为后续 MC / MD 准备模型。
- 拟合数据链：`Fitting_Dataset.txt` / `Fitting_Data_for_prediction.txt` 来自哪个 `3.get_fitting_data` 输出、样本编号范围和训练 / 测试 / 预测切分。
- `convert_info.txt` 前两行的训练样本数和测试 / 预测样本数；用户未指定时按 90/10 默认记录。不得默认写成“全部训练、0 测试 / 预测”。如果用户确实要 0 测试 / 预测，也必须显式确认这是本次拟合策略。
- `convert_info.txt` 第三行必须是每个 DFT 超胞 / `cell.str` 中包含的 `unit_cell.str` 原胞个数，用作能量归一化除数；不得写成 `unit_cell.na`、原胞原子数、`NumberOfAtoms`、样本数或 PASP `%block SuperCell`。例如 32 原子原胞、64 原子 DFT 超胞时应写 `2`。
- 数据编号起点：记录当前样本是 0-based 还是 1-based；`Energy.dat`、`ene_symbol/<id>.ene_symbol` 和转换脚本 `--start-id` 必须一致。当前转换范围的编号必须连续。`convert_data.py` 可以接受 `Energy.dat` 行顺序乱序，因为它按第一列 sample id 查表；未修改的 `convert_data.f90` 按行位置读能量，不能接受乱序。不要因为旧 example 或模板从 1 开始，就把 0-based 数据手工重编号；如果使用未修改的 `convert_data.f90`，它默认是 1-based，0-based 数据应改用 `convert_data.py --start-id 0`。
- `Fitting_Set_Lambda.txt` 是否沿用当前范围，还是调整 lambda 扫描、最大参数数或轮数。
- `I_CHECK_DATA` 策略，以及是否接受 PASP 在运行目录中重写数据文件。
- keep 策略：启用 `I_HAVE_KEEP_TERM=1` 并提供 / 确认 `Fitting_Set_Term_Keep.txt` 来源，或明确禁用 `I_HAVE_KEEP_TERM=0`。
- skip 策略：启用 `I_HAVE_SKIP_TERM=1` 并提供 / 确认 `Fitting_Set_Term_Skip.txt` 来源，或明确禁用 `I_HAVE_SKIP_TERM=0`。
- 是否需要预测集输出，以及对应 `Fitting_Data_for_prediction.txt` 是否参与本次运行。

注意：禁用 keep / skip 也是拟合策略选择，不能由 agent 因模板文件存在或缺失而自行决定。`Fitting_Set_Term_Keep.txt` / `Fitting_Set_Term_Skip.txt` 出现在模板或目录中，不等于启用；只有对应 `I_HAVE_*` flag 为 1 且用户确认来源后才可视为 active。

用户确认后，记录：
- `USER_CONFIRMED_L3_FIT_SETTINGS=true`
- 具体拟合设置值、数据来源、keep / skip 启用状态和未决项。

未满足时允许的唯一下一步：向用户列出缺失拟合确认项。不得创建正式 `4.fit/input/`、派生 `4.fit/runs/<run-id>/` 或准备提交。

### S4：候选输入包
只有 S2 和 S3 都满足，才允许生成候选 shared-basis 输入包。

候选包要求：
- 明确标注 candidate / 待 preflight。
- 不写成 submit-ready。
- 候选目录必须包含 `README.md` 或同等说明，记录候选文件清单、字段 reference inventory 状态、用户已确认项、未决项、不得提交的原因和下一步 preflight 需求。
- 不直接提升为正式 `<stage>/input/`。
- 不得创建 `<stage>/runs/<run-id>/`。
- 不得生成提交脚本、提交命令、外部任务配置或提交准备说明。
- 若候选包里包含 `PASP.input`，文件名或所在目录必须体现 candidate / draft 状态；不得放在正式 `<stage>/input/PASP.input`。
- 若候选 `PASP.input` 中任何显式字段、block、`%include`、依赖文件格式或编号规则尚未逐项查过 reference 或用户给定权威来源，候选包不得进入 S5，也不得升级为正式输入。

进入 S4 前必须已有：
- `USER_CONFIRMED_L3_SHARED_BASIS_PARAMS=true`
- `REPRESENTATIVE_SITES_CONFIRMED=true`

若任一 flag 缺失，允许的唯一下一步是返回 S2 / S3 向用户询问缺失确认项；不得用模板值、smoke-test 值、已有 `OUTCAR` 磁矩或 subagent 盘点结论补齐。

允许下一步：进入 S5。

### S5：Stage Preflight（STOP ON FAIL）
候选输入包提升为正式 `<stage>/input/`、覆盖 input、派生 `<stage>/runs/<run-id>/` 或提交运行前，必须做只读 stage preflight。

执行方式：
- 若用户已授权 subagent，必须让 `pasp-verifier` `mode: input-preflight` 检查；主 agent 本地检查不能替代。
- 若 subagent 工具不可用、授权失效或无法完成检查，结论为 `blocked`，并说明缺少 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`。只有用户明确豁免 L3 subagent preflight 硬门禁时，才可改由主 agent 本地按同一 checklist 检查并继续。
- 若尚未获得 subagent 授权，必须先请求授权；在获得授权或用户明确豁免前，不得提升正式 input、派生 run、准备提交或提交任务。

preflight 输入必须点名：
- 目标 stage。
- 实际候选输入文件，例如 `PASP.input`、`cell.str`、`unit_cell.str`、`distortion.pos`、`distortion.MAGMOM`、`Fitting_Settings.txt`、拟合数据文件。
- 使用的 stage-specific checklist。
- PASP 输入字段清单：列出候选 `PASP.input` 中每一个显式 keyword、block、`%include`、依赖文件格式和编号规则，并给出对应 reference 路径或用户提供来源。

若候选输入包包含批处理或运行脚本，preflight 还必须检查脚本是否过度使用通用 Bash strict mode。对 method-6 这类逐样本批跑，默认不应使用全局 `set -u`、`set -euo pipefail` 或大段防御式 shell 框架；除非用户明确要求且环境脚本已验证兼容。理由是集群环境初始化脚本常读取未定义变量，`LD_LIBRARY_PATH` 也可能为空；strict mode 可能让脚本在样本循环前退出，导致没有 per-sample 证据。

结论只能是：
- `pass`
- `fail`
- `blocked`

通过后记录：
- `STAGE_PREFLIGHT_PASS=true`
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- pass / fail / blocked 结论和证据路径。
- 更新对应 stage README / PROGRESS：记录 preflight 范围、检查者（read-only subagent）、结论、证据路径、仍不可做的动作和允许进入的下一状态。

对 `4.fit` stage，preflight 还必须确认 `USER_CONFIRMED_L3_FIT_SETTINGS=true` 已记录，并检查 `Fitting_Settings.txt` 中 `I_HAVE_KEEP_TERM` / `I_HAVE_SKIP_TERM` 与用户确认表、实际 keep / skip 文件存在性一致。若 keep / skip 被禁用，模板中的 keep / skip 文件不得被描述成 active 设置。

对 `4.fit` stage，preflight 还必须检查 `cell.str` 是真实结构文件，而不是模板占位、注释文件、空文件或零体积晶胞。`skills/knowledge/templates/l3_fit/` 不提供占位 `cell.str`；如果正式 `4.fit/input/` 或 run 目录缺少真实 `cell.str`，结论必须是 `fail`，不得为了补齐文件列表临时手写占位结构。

对 `4.fit` stage，preflight 还必须检查训练 / 测试 / 预测切分是否与用户确认一致：
- `Fitting_Dataset.txt` 行数应等于确认的训练样本数。
- `Fitting_Data_for_prediction.txt` 行数应等于确认的测试 / 预测样本数。
- 如果用户没有指定切分，行数应符合 90/10 默认规则。
- 如果测试 / 预测样本数为 0，必须有用户明确确认；不能因为 `Fitting_Data_for_prediction.txt` 为空或 `I_GIVE_PREDICT=0` 就自动接受。
- `Fitting_Settings.txt` 中 `I_GIVE_PREDICT` / `I_ONLY_PREDICT` 必须和是否使用 `Fitting_Data_for_prediction.txt` 一致；当默认 90/10 产生非空测试 / 预测集时，通常应启用 `I_GIVE_PREDICT=1`。

fail 或 blocked 时允许的唯一下一步：输出阻断原因、证据路径和需要用户确认或修正的项。

### S6：正式 input / run / 提交
只有全部前置 flag 存在，才允许进入 S6：
- `USER_CONFIRMED_L3_SHARED_BASIS_PARAMS=true`
- `REPRESENTATIVE_SITES_CONFIRMED=true`
- `STAGE_PREFLIGHT_PASS=true`
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`

若任一 flag 缺失，必须 STOP。允许的唯一下一步是列出缺失 flag 和需要用户确认 / preflight 的事项；不得继续写正式 input、创建 run、准备提交或读取外部任务配置。

S6 才允许：
- 提升正式 `<stage>/input/`。
- 派生 `<stage>/runs/<run-id>/`。
- 生成提交脚本。
- 执行运行探测或提交准备。

进入 S6 时必须同步更新文档：
- 正式 `<stage>/input/README.md` 说明这是已 preflight 的输入基线、来源目录、关键确认 flag、字段/reference inventory 位置和禁止直接在 input 中运行的约定。
- `<stage>/runs/<run-id>/README.md` 说明本 run 从哪个 input 派生、接入了哪些上游产物、实际运行命令/脚本、提交状态、预期输出和下游 handoff 文件。
- workflow 根目录 `README.md` / `PROGRESS.md` 更新当前阶段、已完成项、正在运行项、失败/blocked 项和下一步。

对 `4.fit` stage，进入 S6 还必须有 `USER_CONFIRMED_L3_FIT_SETTINGS=true`。若缺失，必须返回 S3b；不得用“keep/skip 默认关闭”“模板默认值”或事后追问来补齐。

即使 S6 前置 flag 齐全，真正提交外部任务前仍必须得到用户的明确提交授权。`可以使用 subagent`、`继续`、`按计划执行` 都不是提交授权。

### S7：Output Validation（STOP ON FAIL）
运行完成后、结果交给下游前，必须做 output validation。这个检查与 S5 input preflight 分开记录。

优先委派给 `pasp-verifier` `mode: output-validation`：
- 清点目标 run 的实际输出、日志和关键中间文件。
- 检查程序是否正常结束、是否有关键 warning / error。
- 检查当前 stage 的下游 handoff 文件是否存在且来自同一 run / 数据链。
- 对批量样本检查编号连续性、失败样本、缺失输出和汇总表一致性。
- 对拟合阶段检查数据集、lambda / keep / skip 设置与输出结果是否对应。

结论只能是：
- `pass`
- `fail`
- `blocked`

通过后记录：
- `STAGE_OUTPUT_VALIDATION_PASS=true`
- 目标 run、关键输出文件、日志路径和下游 handoff 文件。
- 若下游目标是 L5 dynamics，还必须记录 `L3_TO_L5_HANDOFF_READY=true` 或明确 blocked / TODO，并在 README / PROGRESS 中列出：L3 run id、`local_mode_PM.dat`、拟交给 L5 的 fitted-parameter file（例如 runtime-validated `J_best.dat` 或等价选择记录）、结构 route、`SuperCell`、`Z_values`、`Spin_values`、mode definition、mass definition 来源、fitting dataset / settings provenance、same-basis 检查结论，以及 L3 不提供的 first-stage `amp_local_mode.in`、`Zeff.dat`、production dynamics settings 和 run-environment gaps。

fail 或 blocked 时，不得把结果交给下游 MC / MD / fitting / analysis；只能输出阻断原因、证据路径和需要重跑或人工确认的项。

S7 完成后必须更新 run README / PROGRESS：记录 output validation 结论、实际输出清单、失败样本、关键日志位置、下游可消费文件和可清理的中间文件。没有这份记录时，不得把结果描述成已经完成 handoff。

## Shared-Basis Preflight 最小清单
- 若用户已经授权 subagent，必须有 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true` 和 `STAGE_PREFLIGHT_PASS=true`，才能提升正式 input、派生 run、准备提交或提交任务。`NO_SUBAGENT_PREFLIGHT_AVAILABLE=true` 只能产生 blocked 报告或草稿，不足以继续运行前动作，除非用户明确豁免 L3 subagent preflight 硬门禁。
- 是否有完整的 PASP 输入字段清单；清单中每一个显式 keyword、block、`%include`、依赖文件格式和编号规则是否都有 reference 或用户提供来源。缺任何一项即 fail / blocked。
- reference / 用户来源必须校验“候选值本身”的定义是否正确，不能只检查候选 `PASP.input` 与 `shared_basis_confirmed.md`、README 或 agent 自己写的确认表是否一致。若确认表中的字段值没有可复查 reference 或用户原始指令支撑，该字段仍为 unverified，preflight 必须 fail / blocked。
- 对 `Z_values` 必须明确检查其含义是当前非 TB 任务中的元素数值标签（通常为原子序数），而不是 `species_id`、元素顺序号或 `local_mode.mode_definition` 中的类型编号；同时检查顺序是否与 `cell.str` / 结构文件中的元素首次出现顺序一致。
- 是否存在用户回答或逐项设置表，证明 `Spin_values`、`fig.maxk`、`fig.mdist`、`Invariant.*`、SOC / DMI / 各向异性策略不是 agent 自己代填。
- 如果用户已要求考虑 SOC、DMI 或各向异性，preflight 必须确认 `Invariant.SOC` 设置已经由用户确认；`local_mode.special_SOC` 只在用户明确要求限制 / 优先保留特定 SOC 项、按 interaction type 截断 SOC 阶数，或另一个已确认工作流条件要求显式限制时才需要处理。若用户接受默认完整 SOC 枚举，不得因为缺少 `%block local_mode.special_SOC` 而 blocked。若用户要求显式 SOC 保留策略但尚未明确，必须先问用户：保留哪些几体、每个几体 / interaction type 的 SOC 最高阶数、保留全部枚举类型还是只保留特定类型；不得先用结构分析、脚本或 agent 判断替用户决定策略。若缺少已确认限制策略对应的相互作用类型编号，必须在写入该限制 block 前 blocked，并先通过用户确认、已有同基底 SOC 输出、已有 interaction-type 清单、已验证案例或允许的预分析获得编号；预分析只能把用户已确认的策略映射到 PASP 编号，不能替用户选择保留哪些 SOC 项。不得把 `Invariant.SOC T` 改成 `Invariant.SOC F` 做 preliminary run 来枚举后续限制 block 所需编号。`local_mode.special_SOC` 的首行只应等于后续实际读取的显式设置行数；不要为了“其余不要”自动枚举所有未保留类型并写 `0`，除非用户或已有案例明确要求完整枚举。`local_mode.special_SOC` 第二列是 PASP 枚举出的当前几体 interaction type / 原子对 / 原子簇编号，不是元素编号、species id、磁性元素序号或 `Z_values` 顺序号；即使第一列为 `1`，第二列也不是元素编号或 `local_mode.mode_definition` 代表点位编号。若用户或已验证案例说“保留前 5 个单体二阶项”，应解释为 `1 1 2` 到 `1 5 2`，不要再追问它是两个元素还是五个代表点位。不得因为体系只有 2 个磁性元素就判定 `1 3 2`、`1 4 2`、`1 5 2` 等行多余或对应非磁性元素。
- `Spin_values` 的数值个数是否等于 `number_of_species` / `Z_values` 元素数；非磁性元素也必须有显式 `0`。
- `local_mode.mode_definition` 是否基于用户提供或对称性分析得到的不等价代表点位。
- 单原子 spin mode 的第一行是否全部为 `1 spin`，species id 是否写在下一行；不得把 species id 写到 `spin` 前面。
- mode 总数是否等于“不等价代表点位数 × 3”，且 mode 总数下一行没有空行。
- 如果代表点位数等于结构中所有参与磁性原子数，是否有证据说明当前结构就是用于定义模式的 primitive，且这些位点确实全部不等价。
- `cell.str`、`unit_cell.str`、`POSCAR_UC` 是否处在同一轴向约定；若 PASP `%block SuperCell` 出现，确认它是否确实表示在 `cell.str` 基础上继续扩胞。
- 对 Path A shared-basis，是否存在用户确认的目标 DFT / 样本超胞设置；若候选输入省略 `%block SuperCell`，preflight 必须确认用户明确接受 1×1×1 作为目标样本 / DFT 规模，而不是由 agent 从文件存在性自动推断。
- 对 Path A `local_mode.cal_para_method = 1`，是否存在用户确认的 `local_mode.nstr_random` / 样本数；若候选输入只为了生成 `local_mode_PM.dat` 而没有生成样本计划，preflight 必须 blocked，并返回 S2 询问样本数。
- 对 `Model Invariant` shared-basis / interaction-basis 运行，preflight 必须记录计划使用的进程数。默认应为单进程；若使用 MPI，必须有当前 PASP build 和当前工作流分支的 MPI-safe 证据，否则结论为 blocked 或至少明确警告。若候选输入包含 `%block local_mode.special_SOC`，MPI 视为不安全，除非已经有该 special-SOC 路径的显式验证证据。
- 输入文件之间的相关性是否正确：`PASP.input` 中的 `%include` 是否真实存在并指向同一套结构基准；`cell.str` / `unit_cell.str` / `POSCAR_UC` 是否满足同一 primitive-supercell 映射；PASP `%block SuperCell` 是否没有被误用为 `unit_cell.str -> cell.str` 的关系矩阵；`local_mode.mode_definition` 坐标是否与当前结构坐标系一致；`Z_values`、species id、`Spin_values`、SOC 设置和上游产物来源是否属于同一数据链。类似 `unit_cell.str` 轴向或坐标顺序错误必须 fail / blocked，不能靠提交试跑发现。
- 对 `unit_cell.str` / `cell.str` 的映射检查，可使用 `skills/knowledge/scripts/l3_effective_hamiltonian/rebase_unit_cell.py --relation ...` 做只读验证。这里的 `--relation` 只表示 unit-cell 到 `cell.str` 的验证关系，不是 PASP `%block SuperCell`。若需要重排轴向，该脚本必须在已有用户确认、read-only structure subagent 结论或其他可核查映射来源后使用，并且必须同步处理基矢和原子坐标；不能只旋转 cell 而不旋转后续坐标。
- README、提交脚本、目录名是否把仍有待确认项的候选输入包装成可提交正式输入。
- 对 method-6 批处理脚本，是否保持朴素逐样本循环和显式日志 / `status.tsv`；是否避免默认加入全局 `set -u`、`set -euo pipefail` 或会在环境初始化阶段提前退出的 strict-mode 逻辑。

## Read-Only Subagent Bounded Fact Collection
权限允许或用户已授权时，优先把这些上下文重任务交给 `skills/subskills/pasp-verifier/skill.md` 定义的 read-only verifier：
- `mode: input-preflight`
- `mode: directory-inventory`
- `mode: output-validation`
- `mode: structure-analysis`
- `mode: log-summary`
- `mode: template-compare`
- `mode: reference-check`

所有 subagent 任务都必须是 bounded fact collection。统一输出格式：
- `Scope`: 检查范围和目标 stage / run。
- `Findings`: pass / fail / blocked 或事实结论。
- `Sources`: 文件路径、日志位置、行号或可复查证据。
- `Uncertain`: 不确定项和原因。
- `Needs main-agent decision`: 需要主 agent 或用户决定的事项。
- `Conclusion`: pass / fail / blocked / not-applicable。

subagent 不能：
- 决定 workflow 路径或用户科研目标。
- 选择 `Spin_values`、截断、阶数、SOC、keep/skip 等物理 / 拟合设置。
- 修改文件、提升正式 input、写提交脚本或提交任务。
- 把 output validation 反向当成 input preflight pass。

## Read-Only Subagent Preflight Prompt
给 `pasp-verifier` `mode: input-preflight` 的提示词应只包含事实检查任务，不泄露期望结论。input preflight、output validation 和结构分析应使用不同任务边界。

```text
你是 read-only PASP input preflight checker。不要修改文件，不要提交任务，不要决定物理参数。

目标 stage: <stage>
候选输入文件:
- <path>
- <path>

请按 L3 state machine 和对应 stage checklist 检查：
1. 必需文件是否齐全。
2. 高风险参数是否有用户确认或明确来源；必须核对来源是否证明候选值本身正确，不能只核对候选输入与 agent 自写确认表一致。
3. local_mode / 代表点位 / 编号 / 结构轴向 / 上游产物链路是否自洽。
4. README、脚本、目录名是否把草稿包装成可提交正式输入。
5. 对 `Z_values`，确认它不是 species_id / 元素顺序号；对 SOC 请求，确认 `Invariant.SOC` 是否已确认、`local_mode.special_SOC` 是否未请求 / 已请求并通过 / blocked。
6. 对 `Model Invariant` shared-basis / interaction-basis 运行，确认计划进程数；若要 MPI，说明 MPI-safe 证据，且包含 `local_mode.special_SOC` 时默认 blocked。

只输出 pass / fail / blocked、证据路径、阻断原因和最小修正建议。
```

## Read-Only Subagent Output Validation Prompt
使用 `pasp-verifier` `mode: output-validation`。

```text
你是 read-only PASP output validation checker。不要修改文件，不要提交任务，不要决定物理参数。

目标 stage: <stage>
目标 run / 输出目录:
- <path>

请检查：
1. 程序是否正常结束，日志中是否有关键 error / warning。
2. 当前 stage 预期输出和下游 handoff 文件是否齐全。
3. 输出是否来自同一 run / 数据链，编号和样本范围是否一致。
4. 是否有失败样本、缺失输出、混用旧 run 或缓存文件的迹象。

只输出 pass / fail / blocked、证据路径、阻断原因和下游是否可消费。
```

## Read-Only Subagent Structure Analysis Prompt
使用 `pasp-verifier` `mode: structure-analysis`。

```text
你是 read-only structure / primitive analysis checker。不要修改文件，不要写正式 POSCAR_UC、unit_cell.str 或 PASP.input。

结构文件:
- <POSCAR or cell.str>
- <candidate POSCAR_UC or unit_cell.str if any>

请检查：
1. 当前结构是否可能已经是用于定义模式的 primitive。
2. 候选 primitive / unit cell 与超胞的体积比、元素顺序、原子映射和轴向是否自洽。
3. 若 PASP `%block SuperCell` 出现，检查它是否会在 `cell.str` 基础上重复扩胞或造成轴向不一致；不要把 unit-cell 到 `cell.str` 的关系矩阵误称为 PASP `SuperCell`。
4. 若使用对称性工具，请报告 symprec、代表点位变化和不确定性。
5. 如果自动 primitive 与目标轴向不同，请先尝试求 primitive rebase 矩阵 T 和 supercell 整数矩阵 M；报告 det(M)、体积比、原子映射 tolerance / 最大残差、目标轴向约定和 mapping 是否唯一。
6. 不要因为 pymatgen / spglib primitive 换轴就直接丢弃它；也不要在缺少 mapping 证据时建议手工沿 x/y/z 切半。
7. 如需验证或修复 `unit_cell.str`，建议主 agent 使用 `skills/knowledge/scripts/l3_effective_hamiltonian/rebase_unit_cell.py --relation ...`，并确认 lattice rows 与 atom coordinate components 使用同一个轴向变换；`--relation` 不是 PASP `%block SuperCell`。

只输出 pass / fail / blocked、证据路径、候选 mapping 和需要用户确认的问题。
```

## Read-Only Subagent Long Log Summarizer Prompt
使用 `pasp-verifier` `mode: log-summary`。

```text
你是 read-only PASP / DFT log summarizer。不要修改文件，不要提交任务，不要决定物理参数。

日志或输出文件:
- <path>
- <path>

请只提取：
1. 正常结束或失败的证据。
2. 第一个关键 error / warning 及其附近上下文。
3. 与当前 stage handoff 相关的输出文件名、样本编号、缺失项。
4. 需要主 agent 继续查 reference 或询问用户的问题。

输出格式必须包含 Scope / Findings / Sources / Uncertain / Needs main-agent decision。
不要输出完整日志，不要给最终用户回复。
```
