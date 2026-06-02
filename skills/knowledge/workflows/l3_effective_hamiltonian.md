# 构建并拟合有效哈密顿量

## 目标
从结构、随机构型和 DFT 数据出发，整理拟合数据并构建 effective Hamiltonian。

## 适用问题
- 我想拟合 effective Hamiltonian
- Invariant 建模流程怎么走
- ene_symbol 和 fitting dataset 怎么准备
- 我已经有 DFT 数据了，下一步怎么整理成可拟合数据

## 输入前提
- 基础结构文件
- PASP 模型输入
- 随机构型或局域模式相关输入
- DFT 输出数据

## 来源边界说明
这份 workflow 文档是在 authoring 阶段基于讲义思路、现有模板、辅助脚本说明和原始 examples 的整理结果。

但运行时应只依赖：
- `skills/knowledge/workflows/`
- `skills/knowledge/reference/`
- `skills/knowledge/templates/`
- `skills/knowledge/scripts/`

如果某些依赖只有真实跑过服务器任务后才能确认，会在各阶段标记为“待运行验证的依赖”，而不是假装已经完全确定。

历史实跑观察、目录实例值、脚本修正记录和完整样例数据范围见：
- `./l3_effective_hamiltonian_run_notes.md`

运行时解释当前 workflow 时，应优先使用本文件中的稳定契约；不要把 run-notes 中的历史实例值直接当成用户当前 workspace 的实时结果。

## 运行状态机（优先级最高）
运行时不要先通读本长文档来“完成整个流程”。必须先读并执行短门禁文件：
- `./l3_effective_hamiltonian_state_machine.md`

本文件只补充当前状态所需的文件、字段和检查细节。任何后文步骤、模板、脚本说明或历史 run-notes 都不能绕过短门禁文件中的 STOP 条件：
- S2 shared-basis 参数确认。
- S3 代表点位确认。
- S5 stage preflight。
- S7 output validation。

## 阶段输入包与运行目录契约
L3 workflow 不应只说“新建 run 目录”。每个阶段都要同时维护两个层次：

- `input/`：当前阶段的干净输入基线。凡是本阶段 `PASP.input` 或入口文件直接 `%include` / 读取的文件，都应在 `input/` 中齐全；如果某个文件来自上游或由运行时生成，必须在本 workflow 中明确说明。
- `runs/<run-id>/`：实际执行目录。每次运行前，先完整复制当前阶段 `input/`，再把上游阶段产物接入或覆盖到这个 run 目录中，最后只在 run 目录里运行 PASP、VASP 或辅助脚本。

这样做的目的不是形式上多建一个目录，而是保证：
- 阶段 `input/` 自洽，可作为稳定基线反复派生；
- run 目录记录本次真实使用的完整输入、上游产物、输出和日志；
- 下游任务消费明确的上游产物或某个 run 的输出，而不是隐式依赖被污染的 baseline `input/`；
- subagent 盘点目录时可以区分“基线输入缺失”“run 没接入上游产物”和“运行后输出缺失”这三类问题。

### 全阶段 Stage Preflight
L3 任意阶段的候选输入包在提升为正式 `<stage>/input/`、覆盖已有 input、派生 `<stage>/runs/<run-id>/` 或提交运行前，都必须先做只读 stage preflight。

如果当前运行环境要求用户授权 subagent，主 agent 必须先问用户是否允许。一旦用户已授权，必须按 `skills/subskills/pasp-verifier/skill.md` 的 `mode: input-preflight` 契约执行 read-only subagent preflight；这是 L3 运行前硬依赖，主 agent 本地检查不能替代。若 subagent 工具不可用、授权失效或无法完成检查，应 blocked 并说明缺少 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`；只有用户明确豁免 L3 subagent preflight 硬门禁时，才可改由主 agent 本地按同一 checklist 检查并继续。

stage preflight 只检查事实和自洽性，不替用户决定物理参数、拟合策略或 workflow 路由。检查结论只能是 pass / fail / blocked，并列出证据路径。

用户说“可以使用 subagent”只表示允许 read-only fact collection，不等于确认 shared-basis 参数，不等于授权提交，也不等于允许 agent 代填 `Spin_values`、`fig.maxk`、`fig.mdist`、`Invariant.*` 或 SOC 策略。

shared-basis 输入尤其要机械执行这些前置 flag：
- `USER_CONFIRMED_L3_SHARED_BASIS_PARAMS=true`
- `REPRESENTATIVE_SITES_CONFIRMED=true`
- `STAGE_PREFLIGHT_PASS=true`
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`

缺任一项时，不得提升正式 `<stage>/input/`，不得创建 `<stage>/runs/<run-id>/`，不得生成提交脚本、提交命令、外部任务配置或提交准备说明；只能列出缺失确认项、写 `notes/` / `drafts/` / `*.draft`，或保存明确标注 candidate 的待 preflight 文件。

目录盘点或 VASP `results/` 清点不算 L3 stage preflight。preflight 必须点名本次检查的候选 PASP / workflow 输入文件，例如 `PASP.input`、`cell.str`、`unit_cell.str`、`distortion.pos`、`distortion.MAGMOM`、`Fitting_Settings.txt` 或拟合数据文件，并按对应 stage checklist 逐项给出结论。只说“subagent 已盘点 results/”不能作为提交 PASP、执行运行探测或提升正式 input 的依据。

通用必查项：
- 当前阶段入口文件直接 `%include` / 读取的文件是否在候选输入包中齐全，或明确标注为运行时由上游接入。
- 高风险参数、结构转换、编号规则、keep/skip、lambda 扫描、SOC / DMI / 各向异性等选择是否已有用户确认或明确来源。
- 上游产物是否来自预期 stage / run / 数据链；不能来自未说明来源的 sibling example、旧 run 或缓存目录。
- README、提交脚本、目录名是否把仍有待确认项的候选输入包装成可提交正式输入。
- 作业脚本、批处理脚本和转换脚本的期望工作目录、相对路径和输出位置是否与当前 stage 目录契约一致。
- 当前阶段的 stage-specific checklist 是否全部通过。

L3 stage-specific checklist：
- `0.shared_basis/`：除通用项外，必须通过下文 `Shared-Basis Preflight`；重点检查用户确认记录、`Spin_values`、`fig.maxk`、`fig.mdist`、`Invariant.*`、SOC 策略、代表点位分析、`unit_cell.str` 格式和轴向一致性。
- `1.method6_template/` 或路径 B 样本编码阶段：检查 `local_mode_PM.dat` 是否来自当前材料、当前 shared-basis 的成功 run；`PASP.input` 是否只切换运行控制项而没有改变 shared-basis 定义；每个样本的 `distortion.pos` 和条件性的 `distortion.MAGMOM` 是否存在、编号是否和 `Energy.dat` / `status.tsv` 对齐。
- `3.get_fitting_data/`：检查 `ene_symbol/<id>.ene_symbol`、`Energy.dat`、`convert_info.txt`、样本编号起点、训练/预测切分范围是否一致；不得混用不同 shared-basis、不同截断或不同 SOC 设置下生成的数据。
- `4.fit/`：检查 `Fitting_Dataset.txt`、`Fitting_Data_for_prediction.txt`、`Fitting_Settings.txt`、`Fitting_Set_Lambda.txt` 是否来自同一数据链；启用 `I_HAVE_KEEP_TERM` 或 `I_HAVE_SKIP_TERM` 前必须有用户确认；不应把模板里的 keep/skip 文件自动当成当前 run 启用项。

任何一项 fail 或 blocked，都不得把候选包提升为正式 `<stage>/input/`，不得派生 run 目录，不得执行运行探测、外部任务创建、提交 PASP / DFT / 转换脚本；只能输出缺失确认项、证据路径和修正建议。

### 全阶段 Output Validation
stage preflight 只说明“输入能不能进入运行”，不说明“输出能不能交给下游”。每个 stage 的 run 完成后、结果交给下游前，必须单独做 output validation。

优先让 `pasp-verifier` `mode: output-validation` 做 output validation；如果当前运行环境要求用户授权 subagent，主 agent 必须先问用户是否允许。若不能使用 subagent，主 agent 按同一清单本地检查，并记录“本次未使用 subagent”。

output validation 至少检查：
- 目标 run / 输出目录是否明确，输出是否来自同一 run / 数据链。
- 程序是否正常结束，日志中是否有关键 error / warning。
- 当前 stage 的预期输出和下游 handoff 文件是否齐全。
- 批量样本是否存在失败样本、缺失输出、编号不连续或汇总表错位。
- 拟合输出是否和当前 `Fitting_Dataset.txt`、lambda、keep/skip 设置对应。

output validation 不能反向授权提交、覆盖 input、提升正式输入包，或替用户接受某组物理 / 拟合结果。它只说明运行后事实是否足够支撑下一步 handoff。

任何一项 fail 或 blocked，都不得把输出交给下游 MC / MD / fitting / analysis；只能输出阻断原因、证据路径和需要重跑或人工确认的项。

如果某一步是批量样本运行，还要额外遵守一个收尾原则：
- 运行结束后，默认只保留下游真正要消费的产物、批处理状态汇总和失败排错所需的最小日志；
- 那些只是为运行临时复制进去的重复输入，如每个样本目录里的 `PASP.input`、`cell.str`、`unit_cell.str`、`distortion.*`、`subpasp1.sh`，如果下游不再需要，就不应长期保留；
- 对已经成功、且结果已被提取汇总的样本，也不要默认长期保留整套中间文件和冗余日志；
- workflow README 应明确写出“哪些要留、哪些可删”，避免批量 run 结束后目录长期膨胀成缓存堆。

除目录本体外，还应把目录说明一并落盘：
- workflow 根目录应有 `README.md`，说明整体阶段划分、当前路径（Path A / Path B）、关键产物和推荐运行顺序；
- 每个关键阶段目录也应有自己的 `README.md`，说明这个目录负责什么、`input/` 里放什么、`runs/` 里放什么、上游依赖哪个文件、下游应消费哪个输出；
- 如果存在 `path_b_inputs/` 这类批量样本池目录，也应单独写 README，说明编号规则、每个样本子目录的用途，以及它与正式 run 目录的关系。

不要把这件事视为可选整理项。对 L3 这种多阶段、会反复提交服务器任务的 workflow，README 是目录契约的一部分。README 至少要包含当前 `Status`、`File Roles`、`Upstream` / `Downstream`、`Gate Evidence`、`Blocked / TODO`；如果这些字段缺失，目录不能被描述成 submit-ready、formal input、validated output 或 handoff-ready。

以 Step 6 拟合为例，推荐流程是：
1. 先保证 `4.fit/input/` 中有完整拟合输入包，包括 `PASP.input` 直接引用的真实 `cell.str`、`Fitting_Settings.txt`、`Fitting_Set_Lambda.txt`、`Fitting_Set_Term_Keep.txt`，以及数据集占位或说明。
2. 新建 `4.fit/runs/<run-id>/`，从 `4.fit/input/` 完整复制。
3. 从 Step 5 的 `3.get_fitting_data/` 或其 run 输出复制 `Fitting_Dataset.txt` 和 `Fitting_Data_for_prediction.txt` 到拟合 run 目录。
4. 在拟合 run 目录中提交作业。若作业脚本在更外层，必须确认它的期望工作目录和相对路径。

这里要单独加一条拟合护栏：
- `Fitting_Set_Term_Keep.txt` 和 `Fitting_Set_Term_Skip.txt` 不能因为模板里存在，就默认视为当前 run 要启用；
- 只要准备启用 `I_HAVE_KEEP_TERM` 或 `I_HAVE_SKIP_TERM`，agent 必须先问用户；
- 若用户没有明确要求，agent 不能直接替用户决定“不启用 keep/skip 项”并进入正式 run；应先把“禁用 keep / 禁用 skip”作为拟合设置表的一部分给用户确认。
- 用户确认后记录 `USER_CONFIRMED_L3_FIT_SETTINGS=true`；没有这个确认，不得创建或覆盖正式 `4.fit/input/`，不得派生 `4.fit/runs/<run-id>/`，不得准备提交或提交。
- 拟合阶段真正要复制进 `4.fit/input/` / `runs/<run-id>/` 的，是已经转换好的 `Fitting_Dataset.txt` 和 `Fitting_Data_for_prediction.txt`；`Energy.dat`、`ene_symbol/`、`status.tsv` 属于上游整理上下文，除非用户明确要求完整归档，否则不必作为拟合运行硬依赖重复复制。

## 示例驱动的阶段目录
Lecture 3 的 examples 更接近一个分阶段流水线，而不是单个目录一次完成全部工作。一个典型组织方式是：

```text
project/
├── 0.generaterandomspin/
├── 1.vaspncl/
├── 2.get_dft_data/
├── 3.get_fitting_data/
├── 4.fit/
└── 5.generateBTO/
```

如果你不想从 0 开始组织输入，可以直接参考：
- `skills/knowledge/templates/l3_invariant/PASP.input`
- `skills/knowledge/templates/l3_invariant/cell.str`
- `skills/knowledge/templates/l3_invariant/unit_cell.str`
- `skills/knowledge/templates/l3_fit/PASP.input`
- `skills/knowledge/templates/l3_fit/Fitting_Settings.txt`
- `skills/knowledge/templates/l3_fit/Fitting_Set_Lambda.txt`
- `skills/knowledge/templates/l3_fit/Fitting_Set_Term_Keep.txt`
- `skills/knowledge/templates/l3_fit/Fitting_Dataset.txt`
- `skills/knowledge/templates/l3_fit/Fitting_Data_for_prediction.txt`
- `skills/knowledge/templates/l3_fit/convert_info.txt`
- `skills/knowledge/scripts/l3_effective_hamiltonian/postprocess.sh`
- `skills/knowledge/scripts/l3_effective_hamiltonian/createINCAR.sh`
- `skills/knowledge/scripts/l3_effective_hamiltonian/get_ene.sh`
- `skills/knowledge/scripts/l3_effective_hamiltonian/run_method6_batch.sh`
- `skills/knowledge/scripts/l3_effective_hamiltonian/convert_data.py`
- `skills/knowledge/scripts/l3_effective_hamiltonian/convert_data.f90`

常见含义是：
- `0.generaterandomspin/`：用 `Model Invariant` 生成样本、符号项、局域模式或自旋相关信息
- `1.vaspncl/`：把 PASP 产出的约束信息整理成外部 DFT 可读输入
- `2.get_dft_data/`：从 `OUTCAR`、`OSZICAR` 等文件抽取总能
- `3.get_fitting_data/`：把 `ene_symbol` 与能量表拼成可拟合数据
- `4.fit/`：切换到 `Model Fitting_one_order` 执行拟合
- `5.generateBTO/`：展示另一类 local-mode / ferroic 示例，不是每个项目都必须有

如果 agent 在用户 workspace 中正式搭建这类阶段目录，默认还要同步补齐目录说明：
- `project/README.md`：解释整个 workflow 和阶段关系
- `0.*`、`1.*`、`2.*` 这类阶段目录内的 `README.md`：解释该阶段角色、输入基线、run 目录与上游/下游关系
- 额外样本池目录如 `path_b_inputs/README.md`：解释样本编号和单样本输入包结构

## 开始前先确认
- 你要建的是哪类模型：自旋、局域模式、应变，还是它们的组合
- 你希望模型覆盖到几体、几阶相互作用
- 你当前采用的是哪条构型来源分支：`local_mode.cal_para_method = 1` 的随机/有序生成，还是 `local_mode.cal_para_method = 6` 的自定义构型输入
- 你是从零开始生成样本，还是已经有一批可用的 DFT 结果
- 你当前缺的是“样本生成”“数据整理”还是“拟合配置”这一步

### 目标目录优先的路径判断规则
当用户已经明确给出一个当前目标目录时，L3 路径判断必须优先依赖**这个目标目录自己**的可见结构，不得先去 sibling workflow、别的 example 或历史样例里找“更完整”的阶段痕迹来覆盖当前目录的判断。

这里的 Path A / Path B 是**样本与特征生成分支**，不是“从头到尾完整 workflow”与“半路接入 workflow”的区别：
- Path A：PASP 从已确认 shared-basis 正向生成样本 / `ene_symbol`，随后外部 DFT 能量再与这些样本配对。
- Path B：已有最终结构、最终磁态或已完成 NCL-DFT 结果，需要用 method 6 在同一 shared-basis 下重新编码出与最终态一致的 `ene_symbol`。

因此，不能把“从 S0/S1 开始、后面还要补 shared-basis 和拟合”的完整任务笼统叫 Path A。也不能因为当前 Path B 起点缺少 `local_mode_PM.dat` 或 shared-basis 输入，就把它改判为 Path A；这只是 Path B readiness blocked。

提交平台、`subpasp*.sh`、PASP executable 路径或 Inspire 凭据不参与 Path A / Path B 判定。它们属于 S5 preflight pass 之后的提交准备问题，不能在 S0 抢先检查并改变路径判断。

可直接执行的判据应写得足够硬：

1. 如果当前目标目录只是扁平 DFT 结果集，例如：
- 一批 `<id>.OUTCAR`
- 一批 `<id>.OSZICAR`
- 一批 `<id>.log`
- 可选再带一个共享 `POSCAR`

而且当前目标目录**自己**看不到：
- `0.generaterandomspin/`
- `1.vaspncl/`
- `2.get_dft_data/`
- `3.get_fitting_data/`
- `4.fit/`
- 或其他等价的前序 L3 阶段目录

则默认必须先判成**路径 B 起点**。  
这里的正确动作是：
- 先把这批最终 DFT 结果视为 method-6 候选样本池
- 先整理 `distortion.pos` / `distortion.MAGMOM` / `Energy.dat`
- 再讨论共享基底和 method-6 readiness

不要在这一步先把它说成“拟合步骤”，也不要先因为当前目录缺少 `ene_symbol/` 就把问题改写成“要去别处补拟合链路”。

2. 只有当当前目标目录**自己**已经呈现出完整或近完整的 L3 阶段链，例如存在：
- `0.generaterandomspin/`
- `1.vaspncl/`
- `2.get_dft_data/`
- `3.get_fitting_data/`
- `4.fit/`

此时再看到 DFT 结果，才默认把它理解为：
- 当前目录已经有前序相互作用/样本阶段
- 当前更像路径 A 已存在、共享基底已建立
- DFT 结果更可能是通向 `3.get_fitting_data/` / `4.fit/` 的中游产物

3. 路径判定与 readiness 必须分开处理：
- “当前目录先判 Path B” 是**路径判定**
- “虽然先判 Path B，但还缺 `local_mode_PM.dat` 或共享基底输入，所以还不能正式跑 method 6” 是**前置依赖 readiness 判断**

不能因为 readiness 还没满足，就把已经明显属于 Path B 起点的目录重新解释成“其实这是拟合步骤”。

### 如果起点是 `OUTCAR + POSCAR`
这是 L3 里很常见、但也最容易误把“已有 DFT 数据”等同于“共享基底已经定义好”的起点。

在这种起点下，第一轮不应直接开始写正式 `0.shared_basis/input/PASP.input`、`4.fit/input/PASP.input` 或准备提交，而应先完成下面这组确认：

1. 目标范围
- 当前确实是在做 L3 effective Hamiltonian，而不是别的 workflow
- 当前目标是 smoke test 跑通，还是直接按正式科研参数建模

2. 结构角色
- 当前 `POSCAR` 是原胞还是超胞
- 是否还需要单独准备 `unit_cell.str` / `POSCAR_UC`
- 当前 `POSCAR` 与这些 `OUTCAR` 是否对应同一套结构基准

3. 共享基底的物理定义
- 哪些元素参与磁性或 `local_mode.mode_definition`
- 对参与自旋建模的元素，是否已经完成对称不等价代表点位分析
- 是否只做纯自旋，还是还包含 strain / phonon / 其他自由度
- 是否考虑 SOC
- 保留体数：`fig.maxk`
- 各体数截断半径：`fig.mdist`，单位 Bohr
- `Invariant.power`
- `Invariant.strain_power`
- `Invariant.pure_strain_power`

4. 现有 `OUTCAR` 在数据链中的角色
- 哪些样本只需要提取 `Energy.dat`
- 哪些样本还需要提取最终逐原子磁矩
- 哪些样本可以继续留在路径 A
- 哪些样本应切到路径 B，并重建 `distortion.pos` / `distortion.MAGMOM`

在这组问题没有确认前：
- 可以先盘点 `OUTCAR`、提取能量、提取最终磁矩、检查样本编号；
- 可以先起草一版待确认的共享基底 `PASP.input` 骨架；
- 但不要把模板默认值写成正式共享基底并继续准备提交。

这里要把一个常见误判单独拎出来：
- 用户说“继续做”“你去构建模型”，不等于用户已经接受 agent 自己代填共享基底参数
- 用户说“implement the plan”“按计划执行”“你来定”也不等于确认共享基底参数；plan 里的默认值、假设值、smoke-test 值和 agent 自己提出的候选值，都不能自动升级成用户确认
- 如果用户没有逐项给出值，也没有明确接受一份逐项设置清单，agent 的下一条回复应只做缺失设置确认，不得同时创建正式输入文件或提交脚本
- 只要 `Spin_values`、`fig.maxk`、`fig.mdist`、`Invariant.power`、`Invariant.strain_power`、`Invariant.pure_strain_power`、纯自旋/含 strain / phonon 边界、SOC 保留策略里有任何一项尚未明确，agent 就必须先提问确认
- 对 Path A，如果目标是让 PASP 生成后续 DFT 样本结构 / POSCAR，还必须确认目标 DFT 超胞矩阵、目标原子数或目标 POSCAR 规模；不能因为 `cell.str` 和 `unit_cell.str` 相同，或用户只提供这两个文件，就默认无需 `%block SuperCell`
- 对 Path A，如果本轮要用 `local_mode.cal_para_method = 1` 正向生成样本，还必须确认 `local_mode.nstr_random` 或等价样本数；不要先跑一个只为得到 `local_mode_PM.dat` 的预运行，再回头问样本数
- 只要还没有完成参与自旋元素的对称不等价代表点位分析，agent 就不能生成正式 `%block local_mode.mode_definition`
- `OUTCAR` 中的最终磁矩、reference 中的常见值、模板中的常见值，都只能作为**待确认候选信息**，不能直接升级成正式共享基底参数

#### 必须先问的问题模板
如果上面任一项缺失，agent 应直接停在确认问题，不要继续写正式输入。推荐问题块：
- 请确认参与自旋建模的元素，以及非磁性元素是否固定为 0。
- 请确认 `Spin_values` 的元素顺序和值。
- 请确认 `fig.maxk` 保留到几体。
- 请确认 `%block fig.mdist` 每个体数的 Bohr 截断半径。
- 请确认 `Invariant.power`、`Invariant.strain_power`、`Invariant.pure_strain_power`。
- 请确认是否只做纯自旋模型，还是包含 strain / phonon / 其他自由度。
- 请确认是否考虑 SOC；如果考虑，SOC / DMI / 各向异性项保留策略是什么。
- 请确认 `local_mode.mode_definition` 的代表点位来源：用户提供、PASP `find_J_path_sym`、还是 agent 先做等价点位分析后再给你确认。
- 请确认当前 `POSCAR` / `cell.str` 是用于定义模式的原胞/primitive，还是需要另行生成 `POSCAR_UC` / `unit_cell.str`。
- 如果走 Path A 并需要生成后续 DFT 样本结构，请确认目标 DFT 超胞：`cell.str` 是否已经是目标超胞；若不是，`%block SuperCell` 应写什么矩阵，或目标 POSCAR 应有多少原子。
- 如果走 Path A 正向生成样本，请确认本轮希望生成多少个随机构型，即 `local_mode.nstr_random` 应写多少。

只有用户回答这些问题，或明确接受一份逐项列出并标注来源的设置表后，才能继续生成正式 shared-basis 输入。

#### Shared-Basis Preflight
把候选 shared-basis 输入包提升为正式 `0.shared_basis/input/`、覆盖现有正式 input、派生 `runs/<run-id>/`、准备提交脚本或提交运行前，必须进行一次独立 read-only subagent preflight 检查，使用 `pasp-verifier` `mode: input-preflight`。若当前运行环境要求用户授权 subagent，主 agent 必须先问用户是否允许；一旦用户已经授权，subagent preflight 就是 L3 运行前硬依赖，主 agent 的本地检查不能替代它。若 subagent 工具不可用或授权失效，应 blocked 并说明缺少 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`；只有用户明确豁免这条 L3 硬门禁时，才可改成本地检查并继续，否则不得提升正式 input、派生 run、准备提交或提交任务。

preflight 的职责是检查事实和自洽性，不替用户决定物理设置。检查结论只能是 pass / fail / blocked，并列出证据路径。

preflight 必查项：
- 是否有完整的 `PASP.input` 字段清单；每一个显式 keyword、block、`%include`、依赖文件格式和编号规则是否都有 reference 路径或用户给定权威来源。缺任何一项都不能把输入包装成正式可运行输入。
- 输入文件之间是否自洽：`PASP.input` 的 `%include` 文件是否存在且来自同一结构基准；`cell.str`、`unit_cell.str`、`POSCAR_UC` 是否满足同一 primitive-supercell 映射和轴向约定；PASP `%block SuperCell` 若出现，是否确实表示在 `cell.str` 基础上继续扩胞，而不是误写成 `unit_cell.str -> cell.str` 的关系矩阵；`local_mode.mode_definition` 坐标、mode 数、species id 是否与当前结构、`Z_values`、`Spin_values` 一致；若存在或用户请求 `local_mode.special_SOC`，其限制策略和编号是否来自用户确认或同基底来源；后续阶段输入是否与上游输出属于同一数据链。像 `unit_cell.str` 坐标轴顺序写错这类跨文件不一致必须在 preflight 阶段 fail / blocked。
- 对 `cell.str` / `unit_cell.str` 的 primitive-supercell 映射验证，可使用 `skills/knowledge/scripts/l3_effective_hamiltonian/rebase_unit_cell.py` 的 `--relation` 参数。该 relation 只用于验证 `unit_cell.str` 与 `cell.str` 的关系，不等同于 PASP `%block SuperCell`。如果需要旋转或重排轴向，必须同步变换 lattice 和 atomic coordinates；如果候选文件已经出现“lattice 是目标轴向但 atom 坐标仍是旧轴序”的错误，只能在映射已确认后用该脚本的 atom-coordinate-only 修复模式生成候选文件，再重新 preflight。
- 是否存在用户回答或逐项设置表，证明 `Spin_values`、`fig.maxk`、`fig.mdist`、`Invariant.*`、SOC / DMI / 各向异性策略不是 agent 自己代填。
- 对 Path A，是否存在用户回答或逐项设置表确认目标 DFT / 样本超胞。若候选输入省略 `%block SuperCell`，必须确认用户明确接受 1×1×1，而不是 agent 从 `cell.str = unit_cell.str` 自动推断。
- 对 Path A `local_mode.cal_para_method = 1`，是否存在用户回答或逐项设置表确认 `local_mode.nstr_random` / 样本数；不得把“先拿 `local_mode_PM.dat`”包装成 Path A 首跑目标来跳过样本数确认。
- `Spin_values` 的数值个数是否等于 `number_of_species` / `Z_values` 元素数；三元素体系中非磁性 O 也必须显式写 `0`，不能省略。
- 是否所有 shared-basis 设置都有来源：用户确认、用户给定文件、reference 规则、或明确标注为待确认草稿。
- `local_mode.mode_definition` 是否基于用户提供或对称性分析得到的不等价代表点位，而不是无证据地遍历所有磁性原子。
- `local_mode.mode_definition` 的单原子自旋模式是否使用 `1 spin`，并把 species id 写在下一行；不得把 Mn 这类 species 2 误写成 `2 spin`。
- mode 总数是否等于“不等价代表点位数 × 3”，且 mode 总数下一行没有空行。
- 如果代表点位数等于结构中所有参与磁性原子数，是否有证据说明当前结构就是用于定义模式的原胞/primitive，且这些位点确实全部不等价。
- `cell.str`、`unit_cell.str`、`POSCAR_UC` 和 `SuperCell` 是否处在同一轴向约定；`unit_cell.str` 是否使用 `unit_cell.na` / `%block unit_cell_in_Ang` / `%block Atoms_in_unit_cell_Ang` 格式。
- `0.shared_basis/input/README.md`、提交脚本和目录命名是否把当前输入包装成可提交正式输入；若还有待确认项，应判 fail。

任何一项 fail 或 blocked，都不得把候选包提升为正式 `0.shared_basis/input/`，不得创建可提交的正式 `PASP.input`，不得写提交脚本，不得提交 PASP；只能输出缺失确认项或修正建议。

如果当前目录表现为：
- 一批已经算好的 `OUTCAR`
- 缺少路径 A 常见的 `ene_symbol/`、`vasp_MAGMOM/` 等中间产物

则默认应优先把它理解成**路径 B 的自然起点**，而不是要求用户先证明自己已经在 method 6 里运行过。  
更实际的动作是：
- 先整理共享基底待确认问题清单，必要时只起草明确标注“待确认 / 不可提交”的 shared-basis `PASP.input` 骨架
- 再从每个 `OUTCAR` 提取最终磁矩与最终结构
- 组织逐样本的 `distortion.MAGMOM` / `distortion.pos`
- 等共享基底参数、结构轴向、不等价代表点位和 `local_mode_PM.dat` 来源都确认后，再走 method-6 路径生成与最终态一致的 `ene_symbol`

如果额外还有一个共享 `POSCAR`，它当然可以帮助固定物种顺序、原子数和超胞基准；但它不应被写成路径 B 的绝对前置条件。  
对 runtime agent 来说，更稳妥的规则是：
- 只要用户明确处在 L3 effective Hamiltonian 语境
- 手头是最终 DFT 产物，例如 `OUTCAR`
- 又看不到路径 A 先前产出的 `ene_symbol`

就应默认开始按路径 B 组织输入，而不是先把“缺少 `POSCAR`”当成无法推进的理由。

如果当前目标目录进一步满足：
- 只有扁平 `OUTCAR` / `OSZICAR` / `log` 结果
- 没有 `0.generaterandomspin/`、`1.vaspncl/`、`3.get_fitting_data/`、`4.fit/` 这类前序阶段目录

则这时不只是“更稳妥地偏向 Path B”，而是应该把 Path B 当成**默认的一阶判断**。  
只有在当前目标目录自己已经出现前序 L3 阶段链时，才应把“已有 DFT 结果”优先解释成拟合链路中游，而不是 Path B 起点。

如果这时路径 A / 路径 B 都还说得通，而且不同选择会改变：
- 是否必须先拿到 `local_mode_PM.dat`
- 是否能继续沿用已有 `ene_symbol`
- 当前应该整理 `vasp_MAGMOM`，还是改去准备 `distortion.pos` / `distortion.MAGMOM`

则主 agent 的正确动作不是继续闷头查很多轮，而是：
- 先给出当前暂定判断；
- 明确指出还缺哪个关键前提；
- 立即请用户确认方案。

在用户确认前，只允许做轻量盘点、能量/磁矩提取、缺失文件检查和问题清单整理；不要继续生成正式共享基底输入、正式样本输入或提交脚本。

### `0.shared_basis/input/` 的阻断式检查清单
如果当前正在准备 `0.shared_basis/input/`，而且以下任一问题还没有得到用户明确确认：
- 是否已经有用户回答或逐项设置表，证明 shared-basis 参数不是 agent 自己代填
- 是否已经完成 shared-basis preflight，且结论为 pass
- `POSCAR` 的角色：原胞还是超胞
- 是否继续沿用示例式的 `cell.str` / `unit_cell.str` 路线
- `unit_cell.str` 的轴向约定是否已经与当前 workflow 使用的 `cellabc` / 代表位点 / 模式定义语境对齐
- 自动 primitive reduction 得到的 `POSCAR_UC` / `unit_cell.str` 是否已按当前 workflow 轴向重排；如果出现等价但换轴的 primitive cell，基矢顺序和所有原子坐标是否已经同步变换
- 哪些元素参与磁性或 `local_mode.mode_definition`
- 是否已经按 `topics/symmetry_representative_sites.md` 找出参与自旋元素的对称不等价代表点位
- 是否只做纯自旋，还是还包含 strain / phonon / 其他自由度
- 是否考虑 SOC
- 保留体数：`fig.maxk`
- 各体数截断半径：`fig.mdist`，单位 Bohr
- `Invariant.power`
- `Invariant.strain_power`
- `Invariant.pure_strain_power`

则 Step 2 不能被视为“已经可以落正式输入”。

#### 未确认前禁止动作
- 不得生成正式 `0.shared_basis/input/PASP.input`
- 不得把自动 primitive reduction 得到但轴向未核对的 `unit_cell.str` 当作正式结果
- 不得把轴向已知不一致的 `POSCAR_UC` / `unit_cell.str` 直接复制进正式 `0.shared_basis/input/` 或 `runs/<run-id>/`；若只是等价基矢重排，必须先把基矢和原子坐标一起重排到当前 workflow 的 `cellabc` 约定
- 不得把模板默认值写进看起来可直接提交的共享基底输入
- 不得把 plan 中的假设值、候选值或 smoke-test 值当成用户已经确认的设置
- 不得在同一轮里一边询问这些设置、一边创建正式 `0.shared_basis/input/PASP.input`
- 不得跳过 shared-basis preflight，或在 preflight fail / blocked 时继续生成提交脚本、README 或 run 目录
- 不得把 `OUTCAR` 最终磁矩大小直接写成正式 `Spin_values`
- 不得因为 reference 里“磁性元素常写 2”就默认当前体系正式采用 `Spin_values = 2`
- 不得因为 `fig.maxk`、`fig.mdist`、`Invariant.*` 在某个模板里常见，就把这些值写成当前材料已经确认的共享基底参数
- 不得把 `cell.str`、`POSCAR` 或半胞里的所有磁性原子逐个展开成 `local_mode.mode_definition`
- 不得在没有不等价代表点位清单时生成看起来可提交的 `%block local_mode.mode_definition`
- 不得把“先搭技术骨架”表述成“当前输入已经准备完成”

#### 未确认前允许动作
- 生成结构摘要、目录盘点、样本清单
- 从 `OUTCAR` 提取能量、最终磁矩、路径 A / B 切换线索
- 对 `POSCAR` / `POSCAR_UC` / `cell.str` / `unit_cell.str` 之间的关系做对照分析
- 在用户已确认参与自旋元素后，对这些元素做不等价代表点位分析，并把代表点位、multiplicity、tolerance 和元素编号作为待确认结果列出
- 输出待确认问题列表
- 在文件必须落盘时，只能保存明确标注“待确认 / 不可提交”的分析记录，不能伪装成正式共享基底输入

### `Spin_values` 的待确认语境
对于 L3 纯自旋 effective Hamiltonian，`Spin_values` 至少有两种常见而且物理语义不同的写法：
- 归一化自旋模型：磁性元素常写成 `2`
- 近似按 DFT 磁矩尺度写

workflow 文档应明确告诉 agent：
- 可以先从 `OUTCAR` 整理出各磁性元素的最终磁矩范围，作为给用户确认的背景信息
- 也可以提醒用户 reference 中常见归一化写法是 `2`
- 但不能由 agent 自己决定最终采用哪一种，并写进正式共享基底输入

## 本地已知的模板与脚本映射

### 模板 -> 对应步骤
- Step 2（准备模型生成输入）
  - `skills/knowledge/templates/l3_invariant/PASP.input`
  - `skills/knowledge/templates/l3_invariant/cell.str`
  - `skills/knowledge/templates/l3_invariant/unit_cell.str`
- Step 5 / Step 6（生成拟合数据集 / 配置并执行拟合）
  - `skills/knowledge/templates/l3_fit/PASP.input`
  - `skills/knowledge/templates/l3_fit/Fitting_Settings.txt`
  - `skills/knowledge/templates/l3_fit/Fitting_Set_Lambda.txt`
  - `skills/knowledge/templates/l3_fit/Fitting_Set_Term_Keep.txt`
  - `skills/knowledge/templates/l3_fit/Fitting_Dataset.txt`
  - `skills/knowledge/templates/l3_fit/Fitting_Data_for_prediction.txt`
  - `skills/knowledge/templates/l3_fit/convert_info.txt`

### 脚本 / 模板 -> 对应步骤
- `skills/knowledge/scripts/l3_effective_hamiltonian/postprocess.sh`
  - 主要服务于 Step 3，并把结果交给 Step 4 / Step 5
- `skills/knowledge/scripts/l3_effective_hamiltonian/createINCAR.sh`
  - 主要服务于 Step 4 的 VASP 输入整理
- `skills/knowledge/scripts/l3_effective_hamiltonian/get_ene.sh`
  - 主要服务于 Step 4 到 Step 5 的能量提取
- `skills/knowledge/scripts/l3_effective_hamiltonian/convert_data.py`
  - 主要服务于 Step 5，免编译地把 `ene_symbol/` 与 `Energy.dat` 转换成拟合入口数据
- `skills/knowledge/scripts/l3_effective_hamiltonian/convert_data.f90`
  - 主要服务于 Step 5，保留原始 example 的 Fortran 转换逻辑作为参考
- `skills/knowledge/templates/l3_fit/slurmpasp.sh`
  - 仅作为 Step 6 的**环境相关作业脚本模板**
  - 它不是 workflow 的必需契约，部署到不同服务器时通常需要替换或重写

## 本地可静态确认的最小文件链路
- Step 2 准备：`PASP.input` + `cell.str` + `unit_cell.str`
- Step 3 method 6 条件输入：`distortion.pos`；若自定义构型包含自旋模式，再加 `distortion.MAGMOM`
- Step 3 产出：`ene_symbol/`、`vasp_MAGMOM/`
- Step 4 产出：`Energy.dat`
- Step 5 依赖：`ene_symbol/*.ene_symbol` + `Energy.dat` + `convert_info.txt`
- Step 6 依赖：拟合阶段完整 `input/` 基线 + Step 5 生成的 `Fitting_Dataset.txt` / `Fitting_Data_for_prediction.txt`
- 如果 Step 6 的 `PASP.input` 直接 `%include cell.str`，则 `cell.str` 必须出现在拟合阶段 `input/` 基线和实际 run 目录中；如果某个项目确认该文件由运行时自动生成，workflow 必须把这个行为标成“运行验证依赖”，不能靠猜测省略

这里最关键的静态约束是：
- `ene_symbol/*.ene_symbol` 的样本编号
- `Energy.dat` 中的样本编号
- 训练/测试切分中引用的样本范围
这些必须保持一致。

## L3 共享基底与两条样本路径
当前 workflow 不应再被理解成“只有随机生成样本这一条路”。更稳定的契约是：

- 先固定一套共享的 effective Hamiltonian 基底；
- 后续所有样本都必须在这同一套基底下生成 `ene_symbol`；
- 样本可以来自两条路径：
  - 路径 A：前向生成路径
  - 路径 B：method 6 编码路径

路径 A 对应传统 L3 做法：先由 PASP 生成样本，再做 VASP。  
路径 B 对应 `local_mode.cal_para_method = 6`：直接把某个样本的最终构型编码回 PASP，再生成与该样本一致的 `ene_symbol`。

其中需要特别说明：
- 路径 A 的首轮运行本身就会自然产出 `local_mode_PM.dat` 等相互作用相关文件；
- 因此对路径 A 来说，不需要把“先单独分析一次相互作用项”写成严格前置步骤；
- 如果路径 A 首跑就是 `local_mode.cal_para_method = 1` 的随机/有序生成，应在首跑前直接确认用户想要的 `local_mode.nstr_random` / 样本数，然后一次运行同时生成样本特征和可复用的 `local_mode_PM.dat`；
- 只有当你准备在后续样本中批量复用这套相互作用基底，尤其是进入路径 B 时，才需要把 `local_mode_PM.dat` 明确固化并作为共享输入复用。

这两条路径共享同一个拟合下游；真正必须保持一致的是：
- `PASP.input` 定义的相互作用基底；
- `local_mode.mode_definition`；
- `fig.maxk`、`fig.mdist`；
- `Invariant.*power`；
- SOC 相关设置；
- 结构基准与元素编号规则。

### 路径 B（method 6）的阶段映射
为了避免把 `local_mode.cal_para_method = 6` 理解成“单独的一套 L3 workflow”，更稳妥的理解是把它映射回现有 Step 2 到 Step 6：

- Step 2：先定义共享基底；此时重点仍然是 `PASP.input`、`cell.str`、`unit_cell.str`、`local_mode.mode_definition`、`fig.maxk`、`Invariant.*power` 等共享物理定义，而不是先写 `distortion.pos`
- Step 2.5：若准备批量走路径 B，先确认当前材料、当前共享基底下已经成功产出并固化 `local_mode_PM.dat`
- Step 3：把 `local_mode.cal_para_method` 切到 `6`，并提供 `distortion.pos`；若自定义构型包含自旋模式，再额外提供 `distortion.MAGMOM`
- Step 4：检查当前 `OUTCAR` / 最终磁矩方向是否说明原路径 A 的旧 `ene_symbol` 已不再可直接配对；必要时回填路径 B 所需的最终态信息
- Step 5：只把与最终物理态一致的 `ene_symbol` 和 `Energy.dat` 配对；路径 A 和路径 B 样本可以共存，但都必须来自同一共享基底
- Step 6：拟合阶段不再区分路径 A / B；它只消费已经对齐好的 `Fitting_Dataset.txt` / `Fitting_Data_for_prediction.txt`

如果用户起点是“批量 `OUTCAR`”，这套映射通常应从下面的现实动作开始：
- Step 2：基于 `skills/knowledge/templates/l3_invariant/PASP.input` 起草共享基底骨架
- Step 4 前置整理：从每个 `OUTCAR` 提取最终能量、最终结构和最终逐原子磁矩
- Step 3（路径 B）：把这些最终态逐样本整理为 `distortion.pos` / `distortion.MAGMOM`

但这里要再加一条判据，避免 runtime agent 把目录看反：
- 如果当前目标目录只有这些最终 DFT 结果，而没有当前目录内可见的前序 L3 阶段链，则这里的“批量 `OUTCAR`”应直接理解成 Path B 起点
- 如果当前目标目录自己已经有 `0.generaterandomspin/`、`1.vaspncl/`、`3.get_fitting_data/`、`4.fit/` 等阶段链，再看到 DFT 结果，才优先解释成路径 A / 拟合链路里的中间阶段

这里最重要的工程判断是：
- 这类目录即使还没有 `local_mode.cal_para_method = 6` 的直接输入文件，也应被视为**准备进入路径 B**，而不是只能停在“先盘点一下”的状态

`local_mode.cal_para_method = 5` 虽然在 reference 中已有说明，但当前仓库还没有足够的分支级 workflow 经验，因此这里暂不把它提升成主分支契约。

## 推荐工作流

### Step 1：先确定模型边界
先回答三个问题：
- 自由度是什么
- 相互作用打算保留到什么范围
- 后续模型是只用于拟合，还是还要继续做 MC / MD

如果后续还要做 MC / MD，建模阶段就应该尽量保持输入组织清晰，避免把控制项混进同一个文件里。

#### 当前阶段输入文件
- 任务目标说明或你已有的建模需求
- 当前准备使用的 `PASP.input` 草稿或模板
- 结构相关输入草稿，例如 `cell.str`、`unit_cell.str`

这些输入里，目标说明通常是用户直接给出的；`PASP.input` 和结构文件通常是手写或从模板起步。

#### 当前阶段已知输出
- 一套更明确的模型边界决策
- 一份可继续细化的 `Model Invariant` 输入方向
- 对后续样本生成规模和模型复杂度的初步约束

这些输出主要是设计决策，不是最终数值结果文件。

#### 待运行验证的依赖
- 当前阶段本身通常不产生运行期文件，但后续哪些文件会被真正生成，要到服务器实跑后确认
- 某些高级设置是否会额外引入辅助文件或中间文件，需要到实际运行时确认

#### 上游依赖
- 这是整个 workflow 的起点，通常没有更早的工作流产物依赖
- 但如果你是从已有 DFT 数据继续推进，这一步的边界设置仍然应与现有数据规模保持一致

#### 下游去向
- 这里的模型边界设置会直接约束 Step 2 中 `PASP.input` 的可调项
- 这里的复杂度选择会决定 Step 3 的样本需求和 Step 6 的拟合稳定性

#### 本阶段使用的脚本
- 无强制脚本
- 这一步主要是确定范围，而不是执行转换脚本

#### 当前阶段可调整项
- `fig.maxk`
- `Invariant.power`
- `Invariant.strain_power`
- `Invariant.pure_strain_power`
- 是否启用 SOC 相关项

#### 这些项控制什么
- `fig.maxk`：最多考虑到几体相互作用
- `Invariant.power`：主要展开阶数
- `Invariant.strain_power`：含应变耦合项的展开阶数
- `Invariant.pure_strain_power`：纯应变项的展开阶数
- SOC 相关项：是否把自旋轨道耦合相关项纳入模型

#### 任务目标 -> 推荐调整方向
- 如果目标是**先把流程打通**：优先降低 `fig.maxk` 和各类 power，避免一开始模型过大
- 如果目标是**后续还要做 MC / MD**：优先保证模型组织清晰，不要过早混入大量高风险高级项
- 如果目标是**覆盖更多复杂相互作用**：再逐步提高 `fig.maxk` 与展开阶数，而不是一次全部开大

#### 什么时候必须先查 reference
- 你不确定这些阶数项彼此如何配合时
- 你不确定它们控制的是“体数”还是“展开阶数”时
- 你准备改 SOC、local mode 或其他高级项但不清楚精确语义时

#### 修改后要检查什么
- 当前模型复杂度是否和你已有数据量匹配
- 后续样本规模是否会失控
- 是否已经把高风险项和基础项区分开
- 是否有需要在服务器上重新验证的高级项依赖

#### 服务器实跑后应补录的信息
- 实际运行时哪些高级设置会额外要求辅助文件
- 实际输出中是否出现与模型边界相关的新中间文件
- 哪些复杂设置会显著扩大样本或目录规模

### Step 2：准备共享基底输入
在建模阶段，通常至少需要：
- 结构信息
- `PASP.input`
- 与局域模式、自旋或应变相关的模型设置

基于示例，一个 `Model Invariant` 阶段常见的最小要素包括：
- `Model Invariant`
- `Invariant.type`
- `%include unit_cell.str`
- `%include cell.str`
- `%block SuperCell`
- `%block Z_values`
- `Invariant.power`
- `Invariant.strain_power`
- `Invariant.pure_strain_power`
- `fig.maxk`
- `%block fig.mdist`
- `%block Spin_values`
- `%block local_mode.mode_definition`
- 需要 SOC 时确认 `Invariant.SOC`；`%block local_mode.special_SOC` 是可选的显式 SOC 项限制 / 优先级输入，不是 `Invariant.SOC T` 的必备伴随 block

其中需要特别区分：
- 以上列表主要描述“共享基底”的核心物理定义；
- 如果用户只要求启用默认完整 SOC 枚举，`Invariant.SOC T` 可以不带 `local_mode.special_SOC`；如果用户要求限制特定 SOC interaction type、为不同体数设置最高 SOC 阶数，或另一个已确认工作流条件要求限制 SOC 项，则 `local_mode.special_SOC` 应在同一 shared-basis 定义中确认并写入，不能等到 method-6、拟合、MC 或 MD 阶段临时改变共享基底；
- `local_mode.cal_para_method`、`local_mode.nstr_random`、`local_mode.read_interaction` 更适合视为后续路径阶段的运行控制项，而不是共享基底本身的核心定义；
- 也就是说，路径 A / 路径 B 可以切换，但只要共享基底不变，`local_mode.mode_definition`、体数、截断、展开阶数和 SOC 相关定义就不应变化。

这里的重点不是一次把所有高级设置都补全，而是先得到一套能稳定定义共享基底的输入。后续无论进入路径 A 还是路径 B，都应复用这一套物理定义，而不是为每个样本单独改一份 `PASP.input`。

正式写入 shared-basis `PASP.input` 前，必须先把两类信息分开确认：
- 建模参数：参与磁性元素、`fig.maxk` 保留到几体、`fig.mdist` 中每个体数的 Bohr 截断半径、`Invariant.power`、`Invariant.strain_power`、`Invariant.pure_strain_power`、是否包含 strain / phonon、是否考虑 SOC，以及是否需要显式限制 SOC 项。若用户要求限制 / 优先保留 SOC 项，该策略必须由用户或明确来源先确认，至少包括保留哪些几体、每个几体 / interaction type 的 SOC 最高阶数、保留全部枚举类型还是只保留特定类型；结构分析和脚本只能把已确认策略映射到 PASP 编号，不能替用户决定保留哪些 SOC 项。
- 自旋代表点位：对参与自旋建模的元素，先按 `skills/knowledge/reference/topics/symmetry_representative_sites.md` 做对称不等价代表点位分析，可使用 PASP `Model find_J_path_sym` 或等价对称分析工具；得到代表位点坐标、元素编号、multiplicity 和 tolerance 后，再为每个代表点位写 x/y/z 三个 spin mode。

如果这两类信息还没有确认，agent 可以生成问题清单、代表点位分析报告或明确标注“待确认 / 不可提交”的草稿，但不能把 smoke-test 参数、plan 假设值或遍历所有磁性原子的 mode block 写成正式 `0.shared_basis/input/PASP.input`。如果用户只说“implement the plan”或“按你说的做”，而没有逐项确认这些设置，这一步仍然停在提问阶段。

在 L3 这条 workflow 里，结构输入路线也应保持稳定：
- 如果当前模板和示例已经明确使用 `%include cell.str`、`%include unit_cell.str`，默认应继续沿用这条 `str` 文件路线；
- `READ_POSCAR` / `READ_POSCAR_UC` 只是 reference 中允许的替代写法，不应因为“从 POSCAR 自动生成更方便”就被 agent 擅自切换进来；
- 特别是在你已经开始按照示例目录组织 `0.shared_basis/input/` 时，主 agent 不应把一个基于 `cell.str` / `unit_cell.str` 的流程中途改写成 POSCAR 读取流程，除非用户明确要求这么做。
- 还要额外检查 `cell.str` 与 `%block SuperCell` 是否自洽：`SuperCell` 是在 `cell.str` 给出的结构基础上扩胞，不是在 `unit_cell.str` 上扩胞；因此若当前 `cell.str` 已经是目标超胞，就不能再把 `SuperCell` 写成非单位阵继续放大。

如果当前起点是“已有一批 `OUTCAR` + 一个 `POSCAR`”，这里尤其要注意：
- 现有 `OUTCAR` 只能帮助你确认已有 DFT 样本能提供哪些能量和最终磁矩信息；
- 它们不能自动替你决定共享基底里的磁性元素、截断半径、体数、展开阶数或 SOC 范围；
- 因此在 Step 2 真正落盘 `PASP.input` 前，主 agent 应先把这些共享基底问题和用户确认清楚，而不是直接把模板默认值当正式设置写进 `input/`。
- 如果 `unit_cell.str` 还是由自动 primitive reduction 临时生成，且轴向还没和用户确认，就连这个文件本身也只能算候选结果，不能和正式 `PASP.input` 一起被当作“input 已准备完成”。

#### 当前阶段输入文件
- `PASP.input`
- `cell.str`
- `unit_cell.str`
- 可能还需要与局域模式定义相关的辅助输入片段

其中：
- `PASP.input` 通常是手写或从 `skills/knowledge/templates/l3_invariant/PASP.input` 派生
- `cell.str`、`unit_cell.str` 可从对应模板起步
- 某些 block 内容可能来自上一步的模型边界决定

写入或转换结构文件前必须先查 reference，而不是从另一个结构文件格式类推：
- `skills/knowledge/reference/topics/structure_from_poscar.md`
- `skills/knowledge/reference/files/cell.str.md`
- `skills/knowledge/reference/files/unit_cell.str.md`

尤其注意：`cell.str` 与 `unit_cell.str` 不是同一种格式。`unit_cell.str` 应使用 `unit_cell.na`、`%block unit_cell_in_Ang` 和 `%block Atoms_in_unit_cell_Ang`；不能把 `cell.str` 的 `NumberOfAtoms`、`%block LatticeVectors` 和 `%block AtomicCoordinatesAndAtomicSpecies` 原样复制过去。若当前只有超胞 `POSCAR` 或超胞 `cell.str`，必须先按 reference 判断 primitive / `POSCAR_UC` 来源和轴向约定；在确认前只能保存候选结构，不能把它当成正式共享基底输入。

自动 primitive reduction 之后必须做轴向对齐检查，不能只检查原子数和体积是否正确：
- 对比超胞 `POSCAR`、候选 `POSCAR_UC` / `unit_cell.str`、预期 `SuperCell` 矩阵和当前 workflow 的 `cellabc` 语境；
- 如果 pymatgen / spglib 返回的候选 primitive 只是把等价基矢循环换序、整数基变换或整体换轴，例如把预期的 `[a/2, b, c]` 写成 `[c, a/2, b]`，不能仅因轴顺序不同就丢弃它；必须先求 primitive rebase 矩阵 `T`，并在进入 PASP 前把 primitive 基矢顺序和所有原子坐标同步重排回当前 workflow 使用的轴向；
- 同时必须求超胞到修正后 primitive 的整数矩阵 `M`，确认 `det(M)`、体积比、物种计数、原子数比例和周期性原子映射 tolerance / 最大残差自洽；
- 不能只改 lattice 三行而不变换原子坐标，也不能让 `local_mode.mode_definition`、代表位点坐标或 `SuperCell` 继续混用另一套轴系；
- 不能在缺少 `T` / `M` 映射或用户确认时，手工假设“沿 x/y/z 切半”来构造保轴 primitive；
- 如果无法从当前文件唯一判断应采用哪套轴向，停止生成正式共享基底输入，向用户确认 primitive cell / 超胞矩阵 / `cellabc` 约定。

如果你当前已经决定沿用示例式的 `cell.str` / `unit_cell.str` 组织方式，就不应在这一步把 `PASP.input` 自动改写成 `READ_POSCAR T` / `READ_POSCAR_UC T` 的另一条结构输入路线。
如果 `PASP.input`、`cell.str`、`unit_cell.str` 中任何一个仍处在“待确认轴向 / 待确认参数 / 待确认物理范围”的状态，这一步就还不能输出正式共享基底输入包。

#### 当前阶段已知输出
- 一套可用于建立共享基底的 `Model Invariant` 输入文件
- 对应的结构定义文件
- 一套理论上可在同一基底下生成 `ene_symbol` 与相关样本产物的输入准备状态

这些输出是当前仓库可静态确认的准备结果，不等于已经真实生成样本。

#### 待运行验证的依赖
- PASP 实跑后到底会生成哪些中间文件
- 某些局域模式或 SOC 设置是否要求额外文件
- 真实运行时是否还需要仓库中未显式记录的辅助输入

#### 上游依赖
- 依赖 Step 1 选定的模型边界和复杂度
- 如果这里的 `fig.maxk`、`Invariant.*power` 和 Step 1 不一致，后续样本规模与拟合预期会偏离

#### 下游去向
- 这一步的输入配置会直接决定后续共享基底是否可被稳定复用
- 这一步的输入配置会直接决定 Step 3 路径 A / 路径 B 能否生成处在同一物理基底下的 `ene_symbol`
- `PASP.input` 与结构定义会间接决定后续 `ene_symbol`、`vasp_MAGMOM` 以及 DFT 整理链路是否可用

#### 本阶段使用的脚本
- 当前仓库没有把这一步绑定到固定脚本
- 但它为后面的 `postprocess.sh` 等脚本提供前提输入

#### 当前阶段可调整项
- `SuperCell`
- `local_mode.cal_para_method`
- `local_mode.nstr_random`
- `Z_values`
- `Spin_values`
- `local_mode.mode_definition`
- `fig.maxk`
- `fig.mdist`
- `Invariant.power`
- `Invariant.strain_power`
- `Invariant.pure_strain_power`
- SOC 相关设置

#### 这些项控制什么
- `SuperCell`：样本生成所基于的超胞范围
- `local_mode.cal_para_method`：构型来源；Path A 正向生成通常使用 `1`
- `local_mode.nstr_random`：Path A 随机生成的构型数
- `Z_values`：元素编号与后续元素相关设置的映射
- `Spin_values`：自旋或磁矩尺度
- `local_mode.mode_definition`：局域模式或自由度的具体定义方式；纯自旋模型中应来自对称不等价代表点位，而不是所有磁性原子的逐原子枚举
- `fig.maxk`：保留到几体相互作用
- `fig.mdist`：每个体数对应的截断半径，单位 Bohr
- `Invariant.*power`：展开阶数与 strain 相关项范围
- SOC 相关设置：是否纳入各向异性 / SOC 相关不变量；若用户选择显式限制，则还包括 `local_mode.special_SOC` 的保留范围和 interaction type 编号

#### 任务目标 -> 推荐调整方向
- 如果目标是**先验证输入能跑通**：优先保持 `SuperCell` 和样本规模保守，先别把 `local_mode.mode_definition` 写得过于复杂
- 如果目标是**为路径 A / 路径 B 共用同一套基底**：优先确保 `local_mode.mode_definition`、体数、截断和 SOC 设定已经稳定，而不是先放大样本规模
- 如果目标是**Path A 生成后续 DFT 样本 / POSCAR**：先确认目标 DFT 超胞矩阵或目标原子数；`cell.str = unit_cell.str` 只说明当前输入基准相同，不说明目标样本不需要扩胞
- 如果目标是**Path A 首跑随机样本**：直接确认 `local_mode.nstr_random` 并一次运行生成样本；不要先单独跑一次只为得到 `local_mode_PM.dat`
- 如果目标是**复用已有相互作用信息**：再考虑 `local_mode.read_interaction`，不要拿它去掩盖结构定义错误

#### 什么时候必须先查 reference
- 你准备写、覆盖、提升或派生正式 `PASP.input` 时：必须逐项检查文件中每一个显式字段、block、`%include`、依赖文件格式和编号规则，而不是只检查看起来高风险的字段。
- 你要改 `local_mode.mode_definition` 但不确定 block 语法时
- 你准备写 `local_mode.mode_definition` 前，必须先查 `topics/symmetry_representative_sites.md` 和 `params/local_mode.mode_definition.md`，并先完成不等价代表点位分析
- 你准备写 `fig.maxk`、`fig.mdist`、`Invariant.*`、SOC 相关项时，必须先查对应 reference，并确认它们不是模板默认值或 smoke-test 假设
- 若 `Invariant.SOC T` 但用户没有要求显式限制 SOC 项，不要强行添加 `%block local_mode.special_SOC`；若用户要求限制 / 优先保留特定 SOC 项，则在写入 `%block local_mode.special_SOC` 前必须确认 interaction type 编号和最高阶数，不能先跑一个 restricted-basis 任务后再补改该 block
- 你不确定 `read_interaction`、SOC 相关项或高级 local mode 选项的精确含义时
- 你打算通过乱改 `Z_values`、`Spin_values` 去补救结构定义错误时
- 你准备创建、覆盖或转换 `cell.str`、`unit_cell.str`、`POSCAR_UC` 时；结构文件格式、primitive reduction、轴向约定和 POSCAR 替代路线都必须先查 reference

#### 修改后要检查什么
- `PASP.input` 是否仍和结构文件一致
- `%include` 关系是否清楚
- 结构文件、元素编号和自由度定义是否自洽
- `local_mode.mode_definition` 的 mode 数是否等于对称不等价代表点位数 × 3；是否记录了代表点位来源、tolerance 和元素编号映射
- `unit_cell.str` 是否真的是 `unit_cell.na` / `unit_cell_in_Ang` / `Atoms_in_unit_cell_Ang` 格式，而不是误复制了 `cell.str` 格式
- `cell.str` 是否只是扩胞前的基准结构；若它已经是目标超胞，则 `%block SuperCell` 是否已改成单位阵或等价“不再扩胞”的写法
- 若 `PASP.input` 省略 `%block SuperCell`，是否有用户确认 1×1×1 就是目标 Path A 样本 / DFT 规模
- 若 Path A 使用 `local_mode.cal_para_method = 1`，是否有用户确认的 `local_mode.nstr_random` / 样本数
- 当前设置是否仍适合作为所有样本共用的共享基底
- 计划运行进程数是否已记录：`Model Invariant` shared-basis / interaction-basis 默认单进程；若要 MPI，必须有当前 build 和当前分支的 MPI-safe 证据。若输入包含 `local_mode.special_SOC`，除非该 special-SOC MPI 路径已验证，否则不要准备 MPI 提交。

#### 服务器实跑后应补录的信息
- 实际生成样本前 PASP 是否还要求未记录的中间文件
- 哪些 block 设置会触发额外产物
- 哪些输入错误最常导致样本生成失败

### Step 2.5（可选）：固化共享相互作用基底
这一阶段不是路径 A 的严格前置步骤。它更适合在下面两种情况下单独强调：
- 路径 A 首轮运行已经自然产出了相互作用文件，你准备把它们固化下来供后续样本复用；
- 你准备进入路径 B，或准备批量编码很多样本，希望明确复用同一套相互作用基底。

#### 目标
- 从当前材料的共享基底运行结果中明确保留可复用的 `local_mode_PM.dat`
- 让后续路径 A / 路径 B 都在同一套基底上生成 `ene_symbol`

#### 当前阶段输入文件
- Step 2 确认后的共享 `PASP.input`
- 当前材料一次已成功的共享基底 / Invariant 运行结果
- 其中与共享基底对应的相互作用输出文件

这里更推荐把输入来源理解成“当前材料在这套共享基底下已经成功跑过一次 Invariant，并留下了可复用产物”。

最常见情形当然是：
- 路径 A 首轮成功运行后，自然留下 `local_mode_PM.dat`；

但更一般的静态契约应写成：
- `local_mode_PM.dat` 必须来自当前材料、当前共享基底下的一次成功 Invariant / shared-basis 运行；
- 它不会在什么都还没跑的目录里“自动存在”；
- 如果当前 workspace 里还没有这次成功运行的结果，也没有用户另行提供可复用的 `local_mode_PM.dat`，则不能把路径 B 当成已经具备前置条件。

#### 当前阶段已知输出
- `local_mode_PM.dat`
- 可选的辅助检查文件：
  - `interaction_type.dat`
  - `all_interaction_type*.dat`

其中 `local_mode_PM.dat` 是后续复用已有相互作用时的核心输入；`interaction_type.dat` 更适合作为人类可读的辅助检查输出，而不是主程序硬依赖。

#### 上游依赖
- 依赖 Step 2 已经把共享基底定义稳定下来
- 当前材料在这套共享基底下必须已经有一次成功的 Invariant / shared-basis 运行；若尚未成功产出 `local_mode_PM.dat`，就还不能把这一步视为已完成

#### 下游去向
- 路径 A 和路径 B 都可以复用这一阶段得到的 `local_mode_PM.dat`
- 后续若在 `PASP.input` 中打开 `local_mode.read_interaction T`，就不应为每个样本重复分析相互作用项

#### 当前阶段可调整项
- 是否已经准备好把当前 `PASP.input` 作为共享基底固化下来
- 是否已经从当前材料的首轮成功运行中得到可复用的 `local_mode_PM.dat`

#### 这些项控制什么
- 是否固化共享基底：决定后续样本能否安全地混合到同一个拟合数据集中
- 是否已有可复用的 `local_mode_PM.dat`：决定后续样本阶段能否直接打开 `local_mode.read_interaction T`

#### 任务目标 -> 推荐调整方向
- 如果目标是**只跑路径 A 首轮样本**：不需要先单独完成这一步；首轮运行本身就会自然产出 `local_mode_PM.dat`
- 对路径 A 首轮样本，正确顺序是先确认样本数 / `local_mode.nstr_random`，然后在同一次 preflighted Invariant 运行中生成样本与 `local_mode_PM.dat`
- 如果目标是**后续批量编码样本**：先确认当前材料是否已经在这套共享基底下成功跑出 `local_mode_PM.dat`；若没有，应先补这一步，再进入路径 B 或后续复用阶段
- 在第一次为当前材料运行路径 A 时，不要把 `local_mode.read_interaction` 当成起始开关；它更适合在 `local_mode_PM.dat` 已经生成之后的后续样本阶段开启

#### 什么时候必须先查 reference
- 你不确定 `local_mode.read_interaction` 何时能安全开启时
- 你不确定当前 `PASP.input` 的哪些设置会破坏 `local_mode_PM.dat` 的复用条件时

#### 修改后要检查什么
- `local_mode_PM.dat` 是否成功生成
- 当前相互作用基底是否确实对应你准备长期复用的那套 `PASP.input`
- 后续样本是否仍会保持相同的结构基准、局域模式定义、体数、截断、展开阶数和 SOC 设置
- 如果这一步来自路径 A 首轮运行的自然产物，确认后续没有误把它和另一套不同基底下生成的旧 `local_mode_PM.dat` 混用
- 如果当前目录里还没有这份文件，确认 agent 没有把“将来应当生成”误说成“现在已经可直接读取”

#### 服务器实跑后应补录的信息
- `local_mode_PM.dat` 之外，当前材料还会稳定产出哪些相互作用类型说明文件
- 哪些设置变化最容易使 `local_mode_PM.dat` 失去复用资格

### Step 3：按路径 A / 路径 B 生成或编码样本
目标是让每个样本都在同一套共享基底下得到可信的 `ene_symbol`。路径 A 强调前向生成与输入磁态的一致性；路径 B 强调把样本的最终收敛态重新编码回 PASP。

这一阶段优先关注：
- 当前激活的是路径 A 还是路径 B
- 输出文件是否齐全
- 样本最终是否还能与当前 `ene_symbol` 保持同一物理态

路径 A 下，这一步往往会配合辅助脚本把样本整理成后续 DFT 能直接接收的文件，例如：
- `postprocess.sh`：把生成结果整理成 `ene_symbol/` 与 `vasp_MAGMOM/`
- `*.ene_symbol`：每个样本对应的符号特征表示
- `*.vasp_MAGMOM`：每个样本对应的自旋约束或磁矩输入

路径 B 下，这一步的关键不再是复用旧的 `*.vasp_MAGMOM`，而是把样本的最终收敛态重新组织成：
- `distortion.pos`
- `distortion.MAGMOM`

然后在共享基底下重新生成与该收敛态一致的 `*.ene_symbol`。

但这里有一个不能跳过的前提：
- 路径 B 不是“只要有一批 `OUTCAR` + 一个 `POSCAR` 就能立刻开始”的无前置分支；
- 它仍然要求当前材料、当前共享基底下已经存在可复用的 `local_mode_PM.dat`；
- 这份文件通常来自一次更早的成功 Invariant / shared-basis 运行，最常见就是路径 A 首轮自然产出；
- 如果当前目录什么都还没做，也没有用户提供这份文件，agent 应先明确指出“路径 B 的共享相互作用基底还没准备好”，然后请用户确认是先补这一步，还是另有现成文件可复用。

建议先用一小批数据把这一步打通，确认编号、目录和后处理脚本行为都稳定，再扩大规模或切换到更复杂的构型集合。

#### 当前阶段输入文件
- 共享基线输入：
  - Step 2 准备好的 `PASP.input`
  - Step 2 准备好的 `cell.str`、`unit_cell.str`
  - 与局域模式或自由度定义相关的输入
- 路径 A 额外关注：
  - `local_mode.nstr_random` 或等价的样本规模控制
- 路径 B（`local_mode.cal_para_method = 6`）额外必需输入：
  - 已由当前材料在同一共享基底下的一次成功 Invariant / shared-basis 运行得到的 `local_mode_PM.dat`
  - `distortion.pos`
  - 若当前构型包含自旋模式，再加 `distortion.MAGMOM`

这里必须区分文件类别：
- `local_mode_PM.dat` 是路径 B 的硬前置依赖；如果它还没生成，Step 3 路径 B 还不能视为 ready
- `distortion.pos` 是 method 6 的硬依赖文件，不应被当成 example helper
- `distortion.MAGMOM` 只在自定义构型包含自旋模式时才是条件依赖
- `postprocess.sh` 是连接 Step 3 到 Step 4 / Step 5 的 helper script，不是 PASP 的核心输入文件

对“批量 `OUTCAR`”这一类起点，还要额外说明：
- `distortion.pos` 的 POSCAR 风格内容表明它更像**单样本输入**，不是天然的多样本总表
- 因此当你手头有 `0..N` 多个 `OUTCAR` 时，更稳妥的组织方式是：
  - 为每个样本单独准备一个 method-6 run 输入包
  - 每个输入包内各自放 `distortion.pos` 与条件性的 `distortion.MAGMOM`
  - 再逐样本生成与最终态一致的 `ene_symbol`
- 不要先假定“一个 `distortion.pos` 文件就能同时装下全部样本”
- 如果额外有共享 `POSCAR`，它更适合被当作“固定物种顺序和原子数的辅助参考”，而不是多样本编码的核心载体
- 这类批量 method-6 跑完后，通常应保留：
  - 每个样本最终需要交给下游的 `ene_symbol`
  - 批量级别的 `status.tsv`、`summary.txt`、`batch.log`
  - 失败样本的运行目录与日志
- 通常可以清理：
  - 成功样本目录中为执行临时复制的结构和脚本文件
  - 已成功提取结果后不再需要的冗余 `log.out` 与重复输入副本

对这类 Path B 的顺序批量运行，还应加一条实现护栏：
- 如果任务本质上只是“按样本复制输入并逐个执行 `PASP.x`”，默认优先采用朴素 `for` 循环脚本；
- 环境变量通常只需在批脚本外层设置一次，不必为每个样本重复 `source/export`；
- 不要默认加入全局 `set -u`、`set -euo pipefail` 或复杂 strict-mode 框架；这类设置在普通 CI 脚本中常见，但在 PASP / HPC 环境脚本中容易因未定义的 `LD_LIBRARY_PATH`、`MKLROOT`、MPI 变量或 `source setvars.sh` 内部逻辑而在样本循环前退出；
- 如果用户明确要求 strict mode，必须先验证环境初始化脚本兼容，并用 `${VAR:-}` 这类写法处理可能为空的变量；否则应只做显式文件存在检查、逐样本返回码检查、`log.out`、`batch.log` 和 `status.tsv`；
- 除非用户明确要求复杂调度、并发控制或恢复逻辑，否则不要先把这种批处理写成大段函数包装或高防御 bash 框架；
- 若要沉淀进 skills，应沉淀为去硬编码的模板脚本，而不是用户当前 workspace 的现场脚本逐字副本。

method-6 批量运行完成后，Path B 进入 `3.get_fitting_data` 时还应按下面的固定 handoff 执行：
- 从每个样本目录提取 `distortion.ene_symbol`
- 汇总为标准命名的 `ene_symbol/<id>.ene_symbol`
- 复制 `Energy.dat`
- 复制 `status.tsv`
- 先核对 `status.tsv` 是否满足本次要进入拟合的数据范围，再运行数据转换

这里要把两个常见误判单独拎出来：
- `distortion.ene_symbol` 才是 Path B 当前批跑直接产生的特征文件，不应一边跑出 `distortion.ene_symbol`，一边还要求用户手工改名后才算进入下游
- 当样本编号从 `0` 开始时，转换阶段应直接使用 `convert_data.py --start-id 0`；不要把“模板常见从 1 开始”误讲成必须重编号

`convert_info.txt` 的第三行也应在 workflow 里写成“自动推导项”，不是自由提问项：
- 它表示每个 DFT 超胞 / `cell.str` 中包含多少个 `unit_cell.str` 原胞，用作能量归一化除数
- 这不是 `unit_cell.na`、不是原胞原子数、不是 `NumberOfAtoms`，也不是 PASP `%block SuperCell`
- 一旦当前 `cell.str` / POSCAR 与 `unit_cell.str` 的结构关系已经确认，就应由原子数比、体积比或已验证的 relation 自动得出
- 例如在当前这次 `l3-4` workflow 中，`unit_cell.str` 是 32 原子，DFT `cell.str` / POSCAR 是 64 原子，因此第三行应写成 `2`，不是 `32`
- 只有结构链本身还没确认时，才允许把这项留作待确认

#### 当前阶段已知输出
- 一批样本相关产物
- 一组按样本编号命名的文件族，例如 `*.ene_symbol`、`*.vasp_MAGMOM`、`*.vasp`
- 一组与 local mode / 中间表示相关的辅助产物，例如 `local_mode-*.xsf`、`imode-*.xsf`、`def_local_modes.dat`
- 与样本编号对应的目录组织

这些是从现有 workflow 文档、reference 和脚本 README 中可以静态推断出来的关键输出。路径 B 的主要区别在于：它生成的是“与最终收敛态一致”的 `ene_symbol`，而不是默认继承路径 A 里的输入磁态假设。

如需看历史实跑时某次输入具体生成了哪些样本文件、local mode 文件和辅助产物，请查 `./l3_effective_hamiltonian_run_notes.md`。

#### 待运行验证的依赖
- PASP 原始运行还会不会产生未记录的中间文件
- `postprocess.sh` 模板是否仍假设源文件位于 `test/` 子目录
- 是否所有设置下都会生成 `ene_symbol/` 与 `vasp_MAGMOM/`
- 当 `local_mode.nstr_random`、`local_mode.mode_definition` 或路径 B 的自定义构型集合变化时，样本文件数与 local mode 文件数如何变化
- 路径 B 在不同自由度组合下是否还会额外要求未记录的辅助文件

#### 上游依赖
- 直接依赖 Step 2 的输入文件定义是否有效
- 如果结构、编号或自由度定义错误，这一步的样本产物就会偏移，后续全链路都会受影响
- 路径 B 依赖可复用的 `local_mode_PM.dat` 与当前共享基底兼容
- 对路径 B，`distortion.pos` 与 `distortion.MAGMOM` 的原子顺序和超胞定义也必须与共享基底兼容
- 如果当前目录还没有 `local_mode_PM.dat`，则说明路径 B 的共享基底前置运行尚未完成，不能把后续 method 6 编码说成“已经只差写脚本”

#### 下游去向
- 路径 A 中的原始 `*.ene_symbol` 会在经过整理后进入 `ene_symbol/`，再在 Step 5 中与能量数据拼接成拟合数据集
- 路径 A 中的原始 `*.vasp_MAGMOM` 会在经过整理后进入 `vasp_MAGMOM/`，再被 Step 4 的 `createINCAR.sh` 用于组织 VASP 输入
- 路径 B 中会基于 `distortion.pos` / `distortion.MAGMOM` 重新生成与最终收敛态一致的 `ene_symbol`
- 样本编号会贯穿 Step 4、Step 5、Step 6

#### 本阶段使用的脚本
- `skills/knowledge/scripts/l3_effective_hamiltonian/postprocess.sh`
  - 作用：整理 PASP 生成结果为 `ene_symbol/` 与 `vasp_MAGMOM/`
  - 关键输入：本阶段运行目录中的原始 `*.ene_symbol` 与 `*.vasp_MAGMOM`
  - 关键输出：`ene_symbol/`、`vasp_MAGMOM/`
  - 关键假设：样本编号与命名规则必须稳定
  - 历史实跑中暴露出的目录布局差异与脚本修正记录见 `./l3_effective_hamiltonian_run_notes.md`

#### 当前阶段可调整项
- 共享可调项：
  - 样本编号与输出目录组织方式
  - 路径切换规则是否已经清楚
- 路径 A 常用可调项：
  - `local_mode.nstr_random` 或等价的样本规模控制项
- 路径 B 常用可调项：
  - `distortion.pos` 中提供的自定义构型集合
  - 若涉及自旋，`distortion.MAGMOM` 中与每个原子对应的磁矩方向
  - 是否真的应切到路径 B，而不是继续沿路径 A 使用旧的输入磁态

#### 这些项控制什么
- 路径 A 中的样本数决定构型覆盖度与后续拟合稳定性
- 路径切换规则决定当前样本是沿输入磁态继续，还是改用最终收敛态重编码
- 路径 B 中的 `distortion.pos` 决定本轮到底读取哪些自定义超胞构型
- 路径 B 中的 `distortion.MAGMOM` 决定自旋相关原子的方向输入是否与 `distortion.pos` 一一对应
- 目录与编号规则决定后续 `ene_symbol`、`vasp_MAGMOM`、`Energy.dat` 是否还能对齐

#### 任务目标 -> 推荐调整方向
- 如果目标是**先跑通一条最小链路**：路径 A 优先减少样本数；路径 B 优先减少自定义构型数量，并先确保 `distortion.pos` / `distortion.MAGMOM` 与共享基底一致
- 如果目标是**扩大拟合覆盖范围**：先在编号规则稳定后增加路径 A 样本数，或扩大路径 B 的自定义构型集合
- 如果目标是**定位数据错位问题**：先检查当前样本是否还应留在路径 A，而不是直接乱改模型定义
- 如果目标是**验证路径 B**：先确认 `local_mode.cal_para_method = 6`、`Invariant.cal_para = T`、`local_mode.read_interaction T`、`local_mode_PM.dat`、`distortion.pos` 和条件性的 `distortion.MAGMOM` 是否齐全；若 `local_mode_PM.dat` 还不存在，先停下来确认要不要补做共享基底运行

#### 什么时候必须先查 reference
- 你要改的已经不是样本数，而是样本生成语义本身时
- 你不确定某个样本生成控制项是“数量参数”还是“物理定义参数”时
- 你不确定 `distortion.pos` / `distortion.MAGMOM` 的精确格式、原子顺序规则或适用条件时
- 你不确定当前样本是否还能沿路径 A 使用旧的输入磁态，而不是切到路径 B 时
- 你要改具体输入字段的精确定义时

#### 修改后要检查什么
- 原始 `*.ene_symbol`、`*.vasp_MAGMOM` 是否按预期生成
- 如果运行 `postprocess.sh`，再检查 `ene_symbol/` 与 `vasp_MAGMOM/` 是否按编号对齐
- 样本目录编号是否稳定
- `postprocess.sh` 的输入输出是否仍兼容后续步骤
- 若使用路径 B，再检查 `distortion.pos` 的超胞坐标、`distortion.MAGMOM` 的行数与顺序是否和原子列表一致
- 若使用路径 B，先检查 `local_mode_PM.dat` 是否真的来自当前材料、当前共享基底下的一次成功运行，而不是 agent 凭空假定它已经存在
- 若当前样本原本来自路径 A，再检查 VASP 最终逐原子磁矩方向是否仍与输入方向逐原子近似平行；若不再平行，应切到路径 B

#### 服务器实跑后应补录的信息
- 实际生成的目录结构与文件清单
- `postprocess.sh` 真实读取的源目录模式
- 哪些情况下会漏生成 `ene_symbol` 或 `vasp_MAGMOM`
- 样本规模扩大后最常见的失败点
- 哪些文件数直接受 `local_mode.nstr_random` 影响，哪些文件数受路径 B 自定义构型集合、local mode 数或其他模型设置影响

### Step 4：整理 DFT 数据
这一阶段的核心不是再讨论模型，而是把外部计算结果转成可拟合的数据表。

通常需要确认：
- 能量是否来自一致的计算设置
- 样本编号是否与 PASP 输出的一一对应关系清楚
- 是否已经能把每个样本对应到与其最终物理态一致的 `ene_symbol` 或等价特征表示

路径 A 下，示例里的做法是：
- 在 `1.vaspncl/` 中用 `createINCAR.sh` 把 `vasp_MAGMOM` 结果拼进 `INCAR_all/INCAR_*`
- 在 `2.get_dft_data/` 中用 `get_ene.sh` 从各编号目录的 `OUTCAR` 提取总能，写成 `Energy.dat`
- 必要时配合 `OSZICAR` 检查计算是否正常收敛

路径 B 下，这一步更关键的检查是：
- 当前 `Energy.dat` 对应的是哪个最终收敛态
- 如果 VASP 最终逐原子磁矩方向已经偏离路径 A 的输入磁态，则必须先回到路径 B，重新生成与最终收敛态一致的 `ene_symbol`
- 不能把“路径 A 输入磁态对应的旧 `ene_symbol`”直接和“VASP 最终收敛态能量”强行配对

这里最关键的不是脚本名字，而是编号映射必须保持严格一致：
- 样本目录编号
- `Energy.dat` 里的样本编号
- `ene_symbol/<id>.ene_symbol` 的编号
这三者必须一一对应，否则拟合即使能跑，结果也很容易失真。

#### 当前阶段输入文件
- 路径 A 生成的 `vasp_MAGMOM/`
- 外部 DFT 目录中的 `OUTCAR`、必要时还有 `OSZICAR`
- 样本编号目录
- 路径 B 判断或回填时额外关注：
  - 当前样本对应的最终逐原子磁矩方向信息
  - 若要判断是否还能留在路径 A，保留与该样本对应的输入磁矩参考，例如 `vasp_MAGMOM/<id>.vasp_MAGMOM`
  - 若准备把最终磁矩方向回填为 method 6 输入，可额外使用 helper 脚本生成候选 `distortion.MAGMOM`

这里要刻意区分：
- `Energy.dat` 仍是 Step 4 的稳定主产物
- `distortion.MAGMOM` 不是所有 Step 4 都必须生成的标准输出；它只在你确认需要转入路径 B 时，才会成为有价值的候选 handoff 文件
- `distortion.pos` 的最终重建来源当前仓库还没有统一提取脚本契约，因此不能把“某个样本最终结构能否直接回写为 `distortion.pos`”说成已经静态证明的事实

#### 当前阶段已知输出
- `INCAR_all/INCAR_*` 或等价的 VASP 输入整理结果
- `Energy.dat`
- 与样本编号一致的能量表
- 可选的路径切换判断结果：当前样本是否仍可沿路径 A 使用旧 `ene_symbol`
- 若显式运行逐原子磁矩提取 helper，可额外得到供路径 B 使用的 `distortion.MAGMOM` 候选文件

如需看历史验证时 `INCAR_all/`、`Energy.dat`、示例 `KPOINTS` 和保留样本范围的具体实例值，请查 `./l3_effective_hamiltonian_run_notes.md`。

#### 待运行验证的依赖
- 真实 VASP 目录结构是否与脚本假设一致
- 当前 `KPOINTS` 设置是否足以支撑后续正式总能比较，还是仅适合作为 workflow 验证起步值
- 不同样本是否都会保持相同的 `OUTCAR` `TOTEN` 解析模式
- 是否存在 README 未记录的中间文件或缓存文件
- 当只保留部分样本的 `OUTCAR` / `OSZICAR` 时，下游数据整理是否允许部分样本链路继续推进
- 若决定从路径 A 切到路径 B，最终结构应如何稳定回写成 `distortion.pos`，当前仍缺少统一的静态脚本契约

#### 上游依赖
- 依赖 Step 3 路径 A 的 `vasp_MAGMOM/` 和样本编号组织，或依赖路径 B 已明确样本最终收敛态
- 如果 Step 3 的编号不稳定，Step 4 生成的 `Energy.dat` 就无法可靠对应 `ene_symbol`

#### 下游去向
- `Energy.dat` 会在 Step 5 中与 `ene_symbol/*.ene_symbol` 拼接为拟合数据集
- 本阶段的编号对齐结果以及路径 A / 路径 B 的选择是否正确，决定 Step 6 的拟合是否有物理意义

#### 本阶段使用的脚本
- `skills/knowledge/scripts/l3_effective_hamiltonian/createINCAR.sh`
  - 作用：把 `vasp_MAGMOM` 约束拼接进 VASP `INCAR`
  - 输入：`vasp_MAGMOM/` 与基础 `INCAR`
  - 输出：`INCAR_all/INCAR_*` 或等价结果
  - 假设：样本编号与目录命名一致
  - 边界：它只能把 PASP 生成的 `MAGMOM` / `M_CONSTR` 类约束追加到用户提供或用户确认过的基础 `INCAR`；不能替用户发明生产用 `ENCUT`、电子步收敛、smearing、SOC/NCL、KPOINTS 或 POTCAR 策略
  - 历史实跑中暴露出的脚本修正记录见 `./l3_effective_hamiltonian_run_notes.md`
- `skills/knowledge/scripts/l3_effective_hamiltonian/get_ene.sh`
  - 作用：从样本目录中的 `OUTCAR` 提取总能并生成 `Energy.dat`
  - 输入：各样本目录的 `OUTCAR`
  - 输出：`Energy.dat`
  - 假设：每个样本目录结构一致且能量文件可解析；当前版本也兼容扁平的 `<id>.OUTCAR` 结果集
  - 历史实跑中暴露出的脚本修正记录见 `./l3_effective_hamiltonian_run_notes.md`
- `skills/knowledge/scripts/l3_effective_hamiltonian/extract_magmoms.py`
  - 作用：从 `OUTCAR` 提取最终逐原子磁矩，判断是否仍与输入磁矩方向近似平行，并可导出候选 `distortion.MAGMOM`
  - 输入：样本 `OUTCAR`，以及可选的 `vasp_MAGMOM` 或已有 `distortion.MAGMOM` 参考
  - 输出：方向一致性判断结果，以及可选的 `distortion.MAGMOM`
  - 使用边界：它解决的是“最终磁矩方向是否提示应切换到路径 B”以及“如何导出 method 6 所需的磁矩方向文件”，并不自动解决 `distortion.pos` 的最终来源
- `skills/knowledge/scripts/l3_effective_hamiltonian/prepare_path_b_inputs.py`
  - 作用：从一个 `OUTCAR` 或一批 `OUTCAR` 中逐样本整理路径 B 所需的 `distortion.pos` / `distortion.MAGMOM`，并可选写出共享 `Energy.dat`
  - 输入：单个 `OUTCAR`，或扁平 `<id>.OUTCAR` 目录，或编号子目录 `id/OUTCAR`；可选提供共享 `POSCAR` 作为物种顺序与原子数参考
  - 输出：逐样本的 method-6 输入包，例如 `path_b_inputs/<id>/distortion.pos` 与 `path_b_inputs/<id>/distortion.MAGMOM`
  - 关键假设：如果提供了共享 `POSCAR`，它的物种顺序和原子数应与各 `OUTCAR` 一致；如果没有提供，脚本会尝试直接从 `OUTCAR` 推断这些信息；样本编号需要在后续 `Energy.dat` 和 `ene_symbol` 中继续保持一致
  - 使用边界：它只解决“如何把现成 DFT 最终态整理成路径 B 的 per-sample 输入包”，不替代共享基底 `PASP.input` 的物理设置确认

#### 当前阶段可调整项
- 样本目录组织方式
- `Energy.dat` 的生成范围与编号规则
- `convert_info.txt` 中训练/测试集数量与每个 DFT 超胞包含的原胞个数 / 能量归一化除数
- VASP `KPOINTS` 网格
- 用户确认的 VASP `INCAR` / `KPOINTS` / `POTCAR` 基础设置

#### 这些项控制什么
- 样本目录与编号规则控制特征和能量能否一一匹配
- `Energy.dat` 控制拟合目标值表
- `convert_info.txt` 控制后续数据转换与切分的元信息
- `KPOINTS` 控制当前 VASP 总能的采样精度；对 NCL/SOC 静态总能比较尤其敏感
- `INCAR` / `KPOINTS` / `POTCAR` 是 DFT 端科学设置，必须来自用户、既有项目输入或用户明确接受的设置表；PASP workflow 只提供样本结构和磁约束 handoff，不负责替用户选择生产 DFT 参数

这里要补一个通用护栏：
- `convert_info.txt` 的前两行是训练/测试或预测切分；如果用户没有指定，默认按 90/10 拆分当前可用连续样本：`Ntrain=floor(0.9*N)`，`Ntest=N-Ntrain`
- 例如 800 个样本默认写成 `720` 训练、`80` 测试 / 预测；不要默认写成 `800/0`
- 只有用户明确要求全量训练或无人值守 smoke test 时，才允许测试 / 预测样本数为 0
- `Energy.dat` 的样本编号可以是 0-based 或 1-based，但必须与 `ene_symbol/<id>.ene_symbol` 和转换脚本起点一致，且当前转换范围内编号连续。当前数据从 0 开始时，优先用 `convert_data.py --start-id 0`；不要只因为旧 `convert_data.f90` 或 example 从 1 开始就重编号。
- 对 `convert_data.py`，`Energy.dat` 行顺序可以乱序，因为转换时按 sample id 查能量；对未修改的 `convert_data.f90`，行顺序必须和样本顺序一致，否则能量会按位置错配到错误的 `ene_symbol`。
- 但第三行“每个 DFT 超胞包含的原胞个数 / 能量归一化除数”不是自由调参项，而是 L3 通用的结构派生量
- 只要当前数据链对应的 `cell.str` / POSCAR 与 `unit_cell.str` 的 primitive-supercell relation 已经确认，第三行就应自动写成相应原胞个数，而不是再问用户一次；不要使用 `unit_cell.na` 或原胞原子数
- 只有结构链本身还没确认时，才允许把第三行留作待确认

#### 任务目标 -> 推荐调整方向
- 如果目标是**先确认编号链路正确**：优先检查 `Energy.dat` 的样本编号与 `ene_symbol` 的对应关系
- 如果目标是**准备最小拟合集**：先收紧样本范围，保证少量样本也能严格对齐
- 如果目标是**扩大训练规模**：在编号一致性确认后再扩大 `Energy.dat` 覆盖范围和 `convert_info.txt` 相关设置
- 如果目标是**先验证 workflow 能走通**：可以先像这次一样只保留少量 `OUTCAR` / `OSZICAR` 样本，并使用保守的 `Gamma 5x5x1` 作为起步 k 点

#### 什么时候必须先查 reference
- 你准备改的是某个 fitting 输入文件格式，而不是简单维护编号一致性时
- 你不确定 `convert_info.txt` 每一行含义时
- 你不确定某个外部数据文件格式时
- 你准备把当前 `KPOINTS` 用作正式能量比较，而不是 workflow 验证起步值时
- 你准备生成或修改 VASP NCL / SOC 输入包时，必须先确认基础 `INCAR`、`KPOINTS` 和 `POTCAR` 来源；只能追加 PASP 生成的 `MAGMOM` / `M_CONSTR`，不能自动补齐生产 DFT 参数

但要注意：
- “查 reference” 不等于把 `convert_info.txt` 第三行重新当成自由参数提问
- reference 负责说明它表示什么；一旦结构链已确认，第三行的具体值仍应由 workflow 自动推导

#### 修改后要检查什么
- `Energy.dat` 是否成功生成
- `Energy.dat` 编号是否和样本目录、`ene_symbol` 一一对应
- `createINCAR.sh`、`get_ene.sh` 是否仍适配当前目录结构
- 外部 DFT 数据是否来自一致的计算设置
- 基础 VASP `INCAR` / `KPOINTS` / `POTCAR` 是否已有用户确认；脚本生成的 `INCAR_all/INCAR_*` 是否只是向确认过的 `INCAR` 追加 PASP 磁约束
- 如果只保留了部分样本，确认当前 `Energy.dat` 的样本编号范围与后续数据集切分仍一致
- 如果样本原本来自路径 A，再检查 VASP 最终逐原子磁矩方向是否仍与输入磁态逐原子近似平行；若不平行，应先切到路径 B 再谈能量配对

#### 服务器实跑后应补录的信息
- 实际样本目录格式与脚本假设是否完全一致
- `OUTCAR` / `OSZICAR` 解析时的真实限制
- 失败时最常见的目录缺失或编号错位问题
- workflow 验证用 `KPOINTS` 与正式总能比较所需 `KPOINTS` 的差距

### Step 5：生成拟合数据集
在这一步，目标是形成两类信息：
- 特征项（如 `ene_symbol`）
- 目标值（如 DFT 能量）

如果样本编号、能量单位、文件命名不统一，这一步最容易出错。

示例里这一步至少要检查这些产物：
- `ene_symbol/*.ene_symbol`：每个样本对应的特征表示
- `Energy.dat`：样本编号到能量的映射表
- `convert_info.txt`：训练集数目、测试集数目、每个 DFT 超胞包含的原胞个数 / 能量归一化除数等转换控制信息
- `convert_data.py` 或等价转换程序：把特征和能量转换成拟合输入的程序

可以把这一步理解成“把 PASP 样本输出和 DFT 总能压平成统一数据表”，只有这一步编号完全对齐，后面的拟合输入才可信。
这里还要额外满足一个前提：用于配对的 `ene_symbol` 必须与该样本最终物理态一致。若路径 A 中的输入磁态已经与 VASP 最终逐原子磁矩方向不再近似平行，则应先切到路径 B 重建 `ene_symbol`，而不是继续沿用旧特征。

#### 当前阶段输入文件
- Step 3 的 `ene_symbol/*.ene_symbol`
- Step 4 的 `Energy.dat`
- `convert_info.txt`
- 可能还包括数据切分所需的拟合模板文件

历史目录组织、完整样例覆盖范围和 `convert_info.txt` 的实例值见 `./l3_effective_hamiltonian_run_notes.md`；本阶段的稳定契约仍然是编号必须对齐、转换入口必须明确。

#### 当前阶段已知输出
- 可供拟合阶段引用的数据集组织结果
- `Fitting_Dataset.txt` 所需的上游数据准备状态
- 可选的预测集准备状态

这些输出在当前仓库里更多是“数据已对齐并可写入拟合入口”的状态，而不是统一固定格式的单一文件。

基于这次服务器验证，已经确认的**阶段性约束**是：
- 当 DFT 还没全部算完时，`ene_symbol` 样本总数可以暂时大于 `Energy.dat` 已覆盖的样本数
- 这种“不完全覆盖”是 workflow 推进中的正常中间状态，不应直接判定为目录组织或脚本逻辑有 bug
- 真正需要保证的是：凡是已经写入 `Energy.dat` 的样本编号，都必须能在 `ene_symbol/` 中找到同编号文件
- 如果某个样本最初来自路径 A，但 VASP 最终磁矩方向与输入方向已不再逐原子近似平行，则当前 `ene_symbol` 不应继续直接配对该能量，而应先改走路径 B
- `convert_data.py` 生成的数据集应保留当前 `ene_symbol` 中的全部特征，并在最后一列追加归一化后的能量；不要因为某个旧 example 的拟合输入列数不同，就反向推断转换脚本应该删特征
- 如果某个拟合目录在运行前的输入列数和当前 `ene_symbol` 不一致，应优先怀疑数据来自不同截断或不同 SOC / 保留项设置，不要混用不同来源的数据链
- 如果拟合运行后输入文件列数变少，应先检查 Step 6 日志和 `Data_Special_Properties_*.txt`，不要反向修改 Step 5 转换脚本去删特征

#### 待运行验证的依赖
- 真实 examples 中是否还有额外的数据转换中间文件
- `convert_info.txt` 在实际环境下是否要求更严格的行格式
- 是否存在只在真实运行时才暴露的数据切分依赖
- 当只完成部分 DFT 样本时，`convert_data` 或等价转换步骤是否支持只消费已带能量的样本子集

#### 上游依赖
- 依赖 Step 3 的 `ene_symbol` 编号
- 依赖 Step 4 的 `Energy.dat`
- 依赖编号、命名、样本范围在前两步都保持一致
- 依赖所有样本都来自同一套共享基底；路径 A 和路径 B 可以混合，但不能混入不同 `PASP.input` 定义下生成的 `ene_symbol`
- 在当前目录命名下，可直接理解为：依赖 `0.generaterandomspin -> 3.get_fitting_data/ene_symbol` 和 `2.get_dft_data -> 3.get_fitting_data/Energy.dat` 的拷贝或同步关系

#### 下游去向
- 这一步的数据集整理结果会直接供 Step 6 的 `Fitting_Dataset.txt`、`Fitting_Data_for_prediction.txt` 和拟合输入使用
- 推荐把这一步产生的数据集作为上游产物接入 `4.fit/runs/<run-id>/`，而不是直接把 `3.get_fitting_data/` 当作拟合运行目录
- 如果这里错位，拟合即使能跑也会失真

#### 本阶段使用的脚本
- `skills/knowledge/scripts/l3_effective_hamiltonian/convert_data.py`
  - 作用：读取 `ene_symbol/`、`Energy.dat`、`convert_info.txt`，生成 `Fitting_Dataset.txt` 和 `Fitting_Data_for_prediction.txt`
  - 输入：连续编号的 `ene_symbol/<id>.ene_symbol`、同编号顺序的 `Energy.dat`、三行 `convert_info.txt`
  - 输出：`Fitting_Dataset.txt` 和 `Fitting_Data_for_prediction.txt`
  - 假设：训练集默认从编号 `1` 开始，预测/测试集紧接训练集之后；默认不支持任意跳号或乱序样本
  - 用法：在 `3.get_fitting_data/` 目录中运行 `python3 convert_data.py --workdir .`
  - 历史完整样例的切分范围见 `./l3_effective_hamiltonian_run_notes.md`
- `skills/knowledge/scripts/l3_effective_hamiltonian/convert_data.f90`
  - 作用：保留原始 example 的转换逻辑来源
  - 注意：复制来的 `convert_data` 二进制依赖 Intel MPI 运行库，通用本地 shell 不一定能直接运行

#### 当前阶段可调整项
- `convert_info.txt`
- 训练集/测试集样本范围
- 数据集入口文件中的样本组织方式

#### 这些项控制什么
- `convert_info.txt` 控制数据转换与切分元信息
- 训练/测试集划分控制拟合使用的数据范围
- 数据集入口组织方式决定 Step 6 是否能稳定读取数据
- 默认切分是 90/10；测试 / 预测集不应因为模板为空而被省略

#### 任务目标 -> 推荐调整方向
- 如果目标是**先完成一个可拟合最小数据集**：先减少样本集，保证 `ene_symbol` 与 `Energy.dat` 严格对齐
- 如果用户没有指定切分：按 90/10 生成 `Fitting_Dataset.txt` 和 `Fitting_Data_for_prediction.txt`
- 如果目标是**准备验证集或预测集**：保持或扩大 `Fitting_Data_for_prediction.txt` 对应的数据入口，而不是写成空文件
- 如果目标是**定位拟合失真原因**：优先回头检查数据对齐，而不是直接修改拟合策略文件
- 如果目标是**在 DFT 尚未全部结束时继续整理 workflow**：可以先保留完整 `ene_symbol`，只同步当前已经得到能量的 `Energy.dat`，后续再扩展覆盖范围

#### 什么时候必须先查 reference
- 你不确定 `convert_info.txt` 每一行的精确含义时
- 你要修改数据集入口文件格式，而不是只替换样本内容时
- 你不确定 `Fitting_Dataset.txt`、`Fitting_Data_for_prediction.txt` 的精确组织方式时

#### 修改后要检查什么
- `ene_symbol` 和 `Energy.dat` 是否按同一编号规则组织
- 训练/测试切分是否与样本范围一致
- 数据集入口是否可以直接供 Step 6 使用
- 将数据交给 Step 6 前，确认目标拟合 run 是从 `4.fit/input/` 完整派生出来的，并且只覆盖/接入数据集产物，不遗漏拟合阶段自身的基线输入
- 是否还存在未解决的运行验证依赖
- 如果 `Energy.dat` 只覆盖部分样本，确认转换步骤不会错误读取那些尚未有能量值的编号
- 如果同时混合路径 A 和路径 B 的样本，确认它们都仍然处于同一套共享基底下

#### 服务器实跑后应补录的信息
- 实际数据转换过程中出现的中间文件
- 数据切分失败最常见的原因
- 哪些格式细节必须在 reference 中进一步补卡片

### Step 6：配置并执行拟合
拟合阶段通常会涉及：
- 保留哪些项
- 正则化或筛选策略
- 是否需要预测集或验证集

示例里这一阶段是单独的 `4.fit/` 目录，并切换到 `Model Fitting_one_order`。实际要准备的文件通常包括：
- `PASP.input`：声明当前进入拟合模型阶段
- `Fitting_Settings.txt`：拟合策略、搜索或初始化控制
- `Fitting_Dataset.txt`：训练/测试数据集入口
- `Fitting_Set_Term_Keep.txt`：强制保留的项
- `Fitting_Set_Term_Skip.txt`：强制跳过的项；只有 `Fitting_Settings.txt` 中启用 `I_HAVE_SKIP_TERM` 时才需要
- `Fitting_Set_Lambda.txt`：正则化参数或扫描列表
- `Fitting_Data_for_prediction.txt`：可选的预测集输入

第一次拟合建议先追求流程打通，再逐步优化参数，而不是一开始就追求最优模型。

#### 拟合提交前的用户确认关卡
拟合阶段不要默认“文件齐了就直接提交”。除非用户明确说这是无人值守 smoke test，并且接受使用模板默认设置，否则在创建正式 `4.fit/input/`、创建 `4.fit/runs/<run-id>/` 或提交 PASP 前，应先把拟合选项摘要给用户确认。

至少确认：
- 当前目标是只打通流程、做正式拟合、筛选更稀疏模型，还是为后续 MC / MD 准备可解释模型
- 训练 / 测试 / 预测切分；用户未指定时采用默认 90/10，并在摘要中写明具体行数和样本编号范围
- 是否使用 `Fitting_Set_Term_Keep.txt` 强制保留某些项；如果启用，需要确认这些项来自哪份报告、映射文件或物理先验
- 是否使用 `Fitting_Set_Term_Skip.txt` 强制跳过某些项；如果启用，需要确认跳过依据，避免把必要项或常数项误排除
- 如果不启用 keep / skip，也必须把 `I_HAVE_KEEP_TERM=0`、`I_HAVE_SKIP_TERM=0` 作为明确选择写进确认摘要；不能把“用户没提供 keep/skip”自动解释成已确认禁用
- 是否沿用当前 `Fitting_Set_Lambda.txt` 的 lambda 扫描范围，还是为了省时减少轮数或调整最大参数数
- 是否需要 `Fitting_Data_for_prediction.txt` 参与预测输出；默认 90/10 切分产生非空测试 / 预测集时，`Fitting_Data_for_prediction.txt` 应参与，`I_GIVE_PREDICT` 通常应为 1
- 是否启用 `I_CHECK_DATA`，以及是否接受 PASP 在运行目录中重写数据文件

确认后应记录 `USER_CONFIRMED_L3_FIT_SETTINGS=true`。如果用户只是在 agent 完整列出拟合设置表后说“ok 去提交”，可以视为接受该表；如果 agent 尚未列出训练 / 测试切分、keep/skip、lambda、数据链和 `I_CHECK_DATA` 摘要，则“ok / 继续 / 去提交”不能补齐确认。

确认时应保持 workflow 级别，不要在这里解释每一行精确语义。只要用户准备修改 `Fitting_Settings.txt`、`Fitting_Set_Term_Keep.txt`、`Fitting_Set_Term_Skip.txt` 或 `Fitting_Set_Lambda.txt` 的具体格式，就先查 `skills/knowledge/reference/files/` 中对应文件说明；reference 仍不够时再询问用户或回到运行日志/映射文件确认。

#### 当前阶段输入文件
- 拟合阶段的 `PASP.input`
- `PASP.input` 直接 `%include` 或读取的配套文件；例如当前模板中 `PASP.input` 包含 `%include cell.str`，因此拟合阶段 `input/` 基线中应有 `cell.str`
- `Fitting_Settings.txt`
- `Fitting_Dataset.txt`
- `Fitting_Set_Term_Keep.txt`
- 启用 `I_HAVE_SKIP_TERM` 时需要的 `Fitting_Set_Term_Skip.txt`
- `Fitting_Set_Lambda.txt`
- 可选的 `Fitting_Data_for_prediction.txt`
- 可选的环境相关作业脚本

其中大部分文件都可以从 `skills/knowledge/templates/l3_fit/` 起步，但通常需要按你自己的数据组织方式修改。这里要特别区分三类文件：
- `skills/knowledge/templates/l3_fit/` 故意不提供占位 `cell.str`；正式 `4.fit/input/` 必须从共享基底或上游已验证目录复制真实结构文件。
- `Fitting_Dataset.txt`、`Fitting_Data_for_prediction.txt` 这类数据集入口文件可以先保留占位模板，随后再用 Step 5 的真实数据覆盖；
- `cell.str` 这类被 `PASP.input` 直接 `%include` 的结构文件不是占位入口，而是运行时硬依赖。只要当前拟合模板仍然 `%include cell.str`，就必须在 `4.fit/input/` 和实际 `4.fit/runs/<run-id>/` 中放入与上游 `ene_symbol`、`Fitting_Dataset.txt` 和共享基底一致的真实结构内容。不要为了补齐文件列表创建注释型、零体积或空结构的 `cell.str`。

更稳妥的做法是：拟合阶段直接复制共享基底或上游样本阶段已经验证过的真实 `cell.str`，而不是重新手写一个“看起来像模板”的占位版本。缺少真实 `cell.str` 应让 preflight fail；不要把占位结构带进 PASP run。拟合阶段应先保证 `4.fit/input/` 是完整基线输入包，再复制到 `4.fit/runs/<run-id>/`，最后从 Step 5 接入当前数据集产物。作业提交脚本是否存在、叫什么名字、如何写，应由当前服务器环境决定，不应视为这条 workflow 的固定契约。

#### 当前阶段已知输出
- 一次可执行的拟合任务配置
- 拟合结果文件或参数输出
- 可供后续 MC / MD 使用的模型结果

当前仓库明确知道这一步会产生“拟合结果”，但具体文件清单仍有一部分需要真实运行确认。拟合输入必须来自同一套共享基底数据链，不能把不同 `ene_symbol` 维度或不同截断 / SOC 设置下的旧 `Fitting_Dataset.txt` 混进当前运行。

历史拟合日志中出现过的数据检查与重写实例见 `./l3_effective_hamiltonian_run_notes.md`。运行时应把这类记录视为“可能出现的观察样例”，而不是当前 workspace 必然已经发生的结果。

#### 待运行验证的依赖
- 不同 `Fitting_Settings.txt` 和 `Fitting_Set_Lambda.txt` 下，拟合运行后实际产生的结果文件名与目录结构是否保持一致
- 你所使用的作业提交脚本在服务器环境中的真实依赖
- 某些拟合策略是否会触发额外输出文件
- 结果文件中哪些才是后续 MC / MD 真正需要的最小产物
- 如果运行前输入维度不符合预期，应先检查是否混用了不同来源的数据集
- 如果运行后日志提示数据需要重写，应检查 `I_CHECK_DATA`、`Data_Special_Properties_*.txt` 和变量映射文件，再决定是否需要查 reference 或询问用户

#### 上游依赖
- 依赖 Step 5 提供的拟合数据组织结果
- 依赖 `ene_symbol`、`Energy.dat`、数据切分规则已经严格一致
- 依赖 Step 6 自己的 `input/` 基线完整；上游数据只能补充或覆盖数据集文件，不能替代拟合阶段应自带的 `PASP.input`、include 文件和拟合控制文件
- 如果上游错位，这一步的结果即使数值上可输出，也可能没有物理意义

#### 下游去向
- 拟合结果可能作为后续 MC / MD 的输入模型
- 因此这里不仅要关注误差，还要关注结果是否可解释、是否适合后续模拟使用

#### 本阶段使用的脚本
- 无固定必需脚本
- 如需提交拟合作业，可以参考环境相关模板，例如 `skills/knowledge/templates/l3_fit/slurmpasp.sh`
  - 这类脚本只表示“可能的提交方式”，不是 workflow 固定契约
  - 在不同服务器上通常需要替换或重写
  - 如果脚本位于阶段目录外或项目根目录，提交前必须确认工作目录、相对路径和它是否会在当前 run 目录中读取输入

#### 当前阶段可调整项
- `Fitting_Settings.txt`
- `Fitting_Set_Lambda.txt`
- `Fitting_Set_Term_Keep.txt`
- `Fitting_Set_Term_Skip.txt`
- `Fitting_Dataset.txt`
- `Fitting_Data_for_prediction.txt`

#### 这些项控制什么
- `Fitting_Settings.txt`：拟合搜索、初始化与检查策略
- `Fitting_Set_Lambda.txt`：lambda 扫描范围
- `Fitting_Set_Term_Keep.txt`：哪些项被强制保留
- `Fitting_Set_Term_Skip.txt`：哪些项被强制排除；只有启用 `I_HAVE_SKIP_TERM` 时才参与
- `Fitting_Dataset.txt`：训练/测试数据入口
- `Fitting_Data_for_prediction.txt`：额外预测集入口

#### 任务目标 -> 推荐调整方向
- 如果目标是**先打通拟合流程**：优先保持 `Fitting_Settings.txt` 和 `Fitting_Set_Lambda.txt` 简单，先保证最小数据集能跑通
- 如果目标是**控制模型复杂度**：优先讨论 lambda 范围、最大参数数、是否强制保留关键项、是否强制跳过已知不合理项，而不是直接扩大数据或改高风险格式
- 如果目标是**为后续 MC / MD 做准备**：除了看误差，还要看保留下来的项是否具有可解释性和后续可用性

#### 什么时候必须先查 reference
- 遇到不确定的拟合设置时，先查 `skills/knowledge/reference/`，不要只根据 example 文件名或当前目录文件猜测语义
- 如果 reference 中没有覆盖对应设置、行含义或文件格式，再和用户讨论确认，不要把推断写成 workflow 契约
- 你不确定某一行是布尔开关、计数、阈值还是策略编号时，必须先查 reference
- 你打算修改 `Fitting_Settings.txt`、`Fitting_Set_Lambda.txt`、`Fitting_Set_Term_Keep.txt`、`Fitting_Set_Term_Skip.txt` 或数据集文件格式时，必须先查 reference
- 你准备强制保留或跳过某些项，但还不能把编号追溯到当前 run 的报告、变量映射或物理先验时，必须先停下来确认

#### 修改后要检查什么
- 拟合输入文件是否仍彼此一致
- `4.fit/input/` 是否是完整输入包；其中 `PASP.input` 直接 include 或读取的文件是否都存在
- `cell.str` 是否已经是真实结构内容，而不是注释型、空文件或零体积占位结构
- 实际运行目录是否从 `4.fit/input/` 完整复制而来，并已接入 Step 5 产物
- `Fitting_Dataset.txt` 与上游数据组织是否匹配
- 如果启用了强制保留或强制跳过，确认对应文件存在、行数和编号连续，并且没有同一项同时出现在 keep 和 skip 中
- 运行前，`Fitting_Dataset.txt` 的列数是否等于当前 `ene_symbol` 特征数加 1 个能量列
- 运行后，如果列数变少，先查看 `log.out` 是否有 `NEED TO REWRITE DATA`，再查看 `Data_Special_Properties_*.txt` 确认是否为 PASP 数据检查触发
- 当前使用的作业提交脚本是否适配服务器环境
- 结果是否值得继续供后续 MC / MD 使用
- 哪些结果文件仍需服务器实跑后补录

#### 服务器实跑后应补录的信息
- 实际生成的拟合结果文件清单
- 哪些结果是后续 MC / MD 真正依赖的关键输出
- 当前服务器上的作业提交脚本需要适配的环境相关部分
- 最常见的拟合失败原因和对应缺失项
- 是否发生数据检查重写；如果发生，记录被移除变量、对应 `Data_Special_Properties_*.txt` 和变量映射文件

### Step 7：检查拟合结果是否可用
至少检查：
- 保留下来的项是否符合物理直觉
- 参数量级是否异常
- 拟合误差是否明显失控
- 输出结果是否足以支撑后续 MC / MD

同时要区分两类步骤：
- **PASP 核心步骤**：生成符号项、组织模型、执行拟合
- **示例辅助脚本**：`postprocess.sh`、`createINCAR.sh`、`get_ene.sh` 这类帮助整理外部 DFT 输入输出的脚本

这些辅助脚本非常重要，但它们不代表 PASP 会自动替你完成全部外部 DFT 编排。部署到新环境时，通常需要按你的计算平台、目录结构和作业系统重写或调整这些脚本。

#### 当前阶段输入文件
- Step 6 产生的拟合结果文件
- 拟合日志或误差相关输出
- 当前拟合使用过的输入文件集合

#### 当前阶段已知输出
- 一次关于“该结果是否可继续使用”的判断
- 一组需要回溯的阶段线索
- 可供后续 MC / MD 或进一步拟合迭代的决策

#### 待运行验证的依赖
- 拟合结果的真实文件清单
- 哪些输出是后续模拟的必要最小集合
- 某些结果解释是否还依赖服务器环境中的额外日志文件

#### 上游依赖
- 完整依赖 Step 1–6 的所有文件链路和编号一致性
- 如果这里发现异常，通常要回看更早阶段而不是只盯着拟合输出

#### 下游去向
- 如果结果可用，可以进入后续 MC / MD 等 workflow
- 如果结果不可用，应记录应回溯的具体阶段和文件链路

#### L3 -> L5 dynamics handoff package
当下游目标是 L5 `Model atomic_effective_H` dynamics 时，L3 的输出不能只用“拟合完成”来描述。只有在 S7 output validation pass 后，才能把当前结果记录成 L5 可消费的 handoff evidence。

这个 handoff 是 provenance package，不是自动生成的完整 L5 `input/`。最低应在 run README / PROGRESS 中记录：
- L3 stage / run id、formal input 来源、S7 output-validation 证据路径。
- `local_mode_PM.dat` 的来源：必须来自当前材料、当前 shared-basis 下成功的 Invariant / shared-basis run，不能来自 sibling example、旧 run 或未说明缓存。
- 拟合参数文件来源：L5 / reference 侧消费的是 `J_best.dat` 这类 fitted interaction values；L3 应记录本次拟合实际验证并选择给 L5 的结果文件路径。如果当前 L3 run 还没有 runtime-validated `J_best.dat` 或等价选择记录，应把这一项标为 blocked / TODO，而不是假定模板已经给出。
- 结构与基底：`cell.str`、`unit_cell.str` 或等价结构 route、`SuperCell`、有效 `Z_values` / `Spin_values`、mode definition，以及当前 L5 route 需要的 mass definition 来源。
- 拟合 provenance：`Fitting_Dataset.txt`、`Fitting_Data_for_prediction.txt`、`Fitting_Settings.txt`、`Fitting_Set_Lambda.txt`、keep / skip 设置和数据链来源。这些通常是审计证据，不是 L5 运行时直接读取的核心文件。
- 已知 gaps：缺失的 mode mass、未确认的 first-stage `amp_local_mode.in`、条件性的 `Zeff.dat`、生产 dynamics 设置、运行环境和任何仍需用户确认的科学判断。

L3 -> L5 handoff 前必须做 same-basis 检查：
- `local_mode_PM.dat`、拟合参数文件、structure route、`SuperCell`、`Z_values`、`Spin_values`、mode definition、mass definition 和拟交给 L5 的 initial state 必须属于同一 current-material effective-H basis。
- 改动任一结构、mode definition、cutoff / expansion / SOC 策略、species / spin order 或 fitted-parameter selection 后，不能盲目复用旧 `local_mode_PM.dat` / `J_best.dat` / `amp_local_mode.in`。
- `mode_def.input`、`mode_mass.input` 只是常见 split include 文件名；是否硬必需取决于 L5 `PASP.input` include graph 或等价 inline block。写入或改动 exact block / file format 前必须查 reference。
- L3 生成的 `*.amp_local_mode` 可能提供格式兼容的 initial-state candidate，但 L3 不替 L5 决定 first-stage dynamics initial condition；用户或上游 validation 仍必须说明它为什么适合当前 L5 branch。

L3 不提供或不自动证明：
- L5 production `MD.input` / `LLG.*` / damping / temperature / timestep / run length / output cadence。
- polarization / electric-field branch 需要的 `Zeff.dat`，除非用户或其他上游计算单独提供并验证 provenance。
- scheduler helper、MPI ranks、executable path、queue / image / walltime。
- dynamics 的科学 acceptance threshold。

因此，当 L5 是下游时，S7 pass 后的下一步是把以上 package 作为 L5 S1 provenance inventory 的输入；不能跳过 L5 S3 settings confirmation、S4 input preflight 或 submission authorization。

#### 本阶段使用的脚本
- 无固定通用脚本
- 这一步更多是检查与回溯判断

#### 当前阶段可调整项
- 本阶段不建议直接把“结果检查”本身当成主要改参点
- 真正的调整通常应回到上游步骤执行

#### 这些项控制什么
- 这一阶段主要控制的是“回溯方向”，不是新增参数空间

#### 任务目标 -> 推荐调整方向
- 如果目标是**得到可解释模型**：优先检查保留项和参数量级，再决定是否回到 Step 6
- 如果目标是**结果能供 MC / MD 使用**：优先检查输出是否稳定、是否保留关键相互作用
- 如果目标是**定位错误来源**：按下面的异常现象回溯，不要只在当前阶段反复试错

#### 什么时候必须先查 reference
- 如果你卡在某个具体字段的数值或文件格式含义上
- 如果你需要知道某个结果文件的精确结构

#### 修改后要检查什么
- 回溯判断是否落到明确阶段
- 是否已经区分“模型本身问题”和“数据链路错位问题”
- 是否记录了需要服务器实跑后补录的信息

#### 服务器实跑后应补录的信息
- 实际输出结果文件中哪些最值得沉淀回 workflow 或 reference
- 常见失败模式对应的真实日志特征
- 哪些检查规则可以沉淀为后续 workflow 通用模式

#### 异常现象 -> 优先回溯阶段
- 模型复杂度明显过高、样本需求失控 → 先回看 Step 1 的 `fig.maxk` 与 `Invariant.*power`
- 样本生成出来但后处理接不上 → 先回看 Step 2/3 的 `local_mode.*` 与脚本目录组织
- `ene_symbol` 和能量对不上号 → 先回看 Step 4/5 的编号映射与 `convert_info.txt`
- 拟合能跑但结果明显失真 → 先回看 Step 5/6 的数据集组织与 `Fitting_*` 设置

## 常见坑
### 1. 一开始就把模型开得过大
如果一上来就把体数、阶数、自由度都开得很多，样本需求会迅速膨胀，拟合也更不稳定。

### 2. 样本与 DFT 结果对不上号
这是最常见的数据整理问题之一。症状通常是：
- 拟合程序能跑
- 但结果毫无物理意义，或者误差异常大

### 3. `ene_symbol`、能量文件、样本编号命名不统一
这会让后续数据集构造阶段非常容易错位。

### 4. 把 workflow 问题和字段问题混在一起
例如用户真正卡住的是 `fig.maxk` 或 `Fitting_Settings.txt` 的某个字段，而不是整个流程本身。
这种情况应及时转给 reference，不要在 workflow 里硬解释。

### 5. 拟合结果能跑，但不适合后续模拟
如果目标是后续 MC / MD，还要检查模型是否足够稳定、是否保留了关键相互作用，而不只是看表面误差。

## 什么时候算成功进入下一步
满足以下条件时，可以认为建模与拟合阶段已经基本完成：
- 已有成体系的样本与 DFT 数据对应关系
- `ene_symbol`、`Energy.dat`、样本编号三者已经严格对齐
- 已得到可读、可解释的拟合结果
- 拟合输出能继续提供给后续模拟步骤使用

如果你第一次做这条流程，最稳妥的成功标准不是“大样本高精度”，而是先用一小批样本把 `生成样本 → 提取能量 → 组织数据集 → 拟合` 这条链完整闭环跑通。

## 当前步骤常见 reference 入口
- `modules/effective_hamiltonian.md`
- `topics/PASP.input.md`
- `files/Fitting_Settings.txt.md`
- `files/Fitting_Set_Lambda.txt.md`
- `files/local_mode_PM.dat.md`
- `files/distortion.pos.md`
- `files/distortion.MAGMOM.md`
- `params/local_mode.cal_para_method.md`

如果你当前卡在具体字段上，优先转去查：
- `fig.maxk`
- `Invariant.power`
- `Invariant.strain_power`
- `Invariant.pure_strain_power`
- `local_mode.mode_definition`：见 `params/local_mode.mode_definition.md`
- `local_mode.read_interaction`
- `local_mode.cal_para_method`

## 不负责回答的内容
- 单个展开项参数的定义
- `fig.maxk`、`Invariant.power` 等字段的逐项解释
- 拟合配置文件的字段细节
这些应转给 reference。
