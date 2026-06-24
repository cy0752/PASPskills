# PASP Skills 开发原则说明

这份文档不是面向最终使用者的 README，而是面向**后续继续建设 PASP skills 的开发者说明**。

它的作用是：在 Lecture 4–8 以及未来新增 workflow 继续标准化时，约束整体架构、目录边界、workflow/reference 分工、模板与脚本纳入原则，以及 Claude / Codex 在修改输入文件时应遵守的行为规则。

---

## 1. 这份文档解决什么问题

当前这套 PASP skills 仍在持续标准化，特别是：
- 整体入口与路由架构已经搭好
- reference 已经有基础框架
- Lecture 2 / Lecture 3 最接近“可直接使用”的标准，已经具备较完整的 workflow 文档、模板与脚本模板
- Lecture 4–8 已经具备基础 workflow / subskill 覆盖，其中 L4 也已有 state machine 与 run-notes；后续重点是继续把 L4–L8 的模板、脚本、调参护栏和 preflight 标准化补到接近 L2 / L3 的完整度

因此现在最需要的不是继续零散补文件，而是先明确：

1. 后续 workflow 应按什么结构写
2. 哪些内容放 workflow，哪些内容放 reference
3. 哪些示例文件值得纳入 `skills/knowledge/templates/` 或 `skills/knowledge/scripts/`
4. 当用户、Claude 或 Codex 正在某个 workflow 中修改输入时，skills 应如何判断“当前能改什么、哪些必须先查 reference”

这份文档就是这套开发原则的统一约束。

---

## 2. 总体设计原则

### 原则 1：始终先分清 workflow 与 reference
- **workflow** 负责回答：
  - 我要做什么
  - 怎么开始
  - 下一步是什么
  - 当前阶段能改哪些设置
  - 改完后应该检查什么
- **reference** 负责回答：
  - 某个字段是什么意思
  - 某个文件怎么写
  - 默认值是什么
  - 编号规则是什么
  - block 格式、文件格式、模块定义是什么

### 原则 2：workflow 先判断阶段，再决定是否查 reference
用户很少一开始就只问字段名。更常见的是：
- 先说自己要做哪个任务
- 然后在当前 workflow 某一步里提出调参或改输入的需求

因此正确行为不是直接跳进 reference，而是：
1. 先判断当前属于哪个 workflow
2. 再判断当前处于哪个 stage
3. 再列出这一阶段哪些设置是正常可调的
4. 如果涉及精确语义、格式、默认值、编号规则，再查 reference

### 原则 3：workflow 不应退化成参数词典
workflow 里可以写：
- 当前阶段可调整项
- 每项控制什么
- 什么时候不要直接改、先查 reference

但 workflow **不应**写成：
- 每个字段的完整默认值表
- 每个 block 的详细语法手册
- reference 文档的重复拷贝

否则后续维护会非常混乱。

### 原则 4：reference 仍然是字段语义的唯一权威来源
当发生下面这些情况时，应默认 reference 才是最终依据：
- 用户问字段的精确定义
- 用户问默认值
- 用户问 block 精确格式
- 用户问文件格式
- Claude / Codex 准备直接改某个复杂字段，但并不确定其精确语义

workflow 可以告诉你“该看哪项”，但不应取代 reference 成为精确定义源。

### 原则 5：workflow 主文档只写稳定契约，历史实跑观察单独放 run-notes
`skills/knowledge/workflows/*.md` 的主文档应只保留稳定、可复用、运行时安全的 workflow 契约，例如：
- 当前阶段输入文件
- 当前阶段已知输出
- 上下游依赖
- 当前阶段可调整项
- 什么时候必须先查 reference
- 修改后要检查什么

不要把下面这些内容直接混在主 workflow 文档的主路径里：
- 某次服务器实跑的具体样本数
- 某次运行日志中的具体数值
- 某次验证使用的 `KPOINTS`、训练/测试切分、能量值、local mode 数
- 某次脚本修正所对应的具体目录布局实例

这些内容应放到单独的 `*_run_notes.md` 文件，例如：
- `skills/knowledge/workflows/l3_effective_hamiltonian_run_notes.md`

主 workflow 文档可以链接到 run-notes，但必须明确：
- run-notes 记录的是历史观察，不是当前用户 workspace 的实时状态
- runtime 回答时，默认先用主 workflow 文档中的稳定契约
- 只有在用户明确需要历史样例、脚本修正记录或实例值时，再引用 run-notes

### 原则 6：开发 skills 时可参考源码，但运行时不能依赖源码
在继续完善 PASP skills、补齐 workflow 行为或解释复杂输出时，开发者和 agent 可以参考本工作区可访问的 PASP / Latticemodel 源码，用源码来确认隐藏逻辑、输出条件、文件生成规则和 warning 的真实触发原因。当前已知源码根目录为：

```text
/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/
```

需要时可在该目录下用 `rg` 按参数名、warning 文本、输出文件名或子程序名查找实现逻辑。

但这些源码只应作为**开发和校准素材**，不能成为部署后 skills 的运行依赖。用户真正使用这套 skills 时，默认只能看到：
- `skills/knowledge/workflows/`
- `skills/knowledge/reference/`
- `skills/knowledge/templates/`
- `skills/knowledge/scripts/`
- 必要的用户工作目录文件和运行日志

因此，从源码中学到的稳定规则必须整理回 workflow、reference、templates 或 scripts 的说明中；不能要求最终用户或运行时 agent 再去读取源码才能正确使用 skill。

### 原则 7：测试或续跑某个 workflow 时，默认只看当前目标目录
当用户已经明确给出当前要处理的 workflow 目录或结果目录时，开发者和 agent 在测试“这个 workflow 能否继续走通”时，默认只能使用两类信息：
- `skills/knowledge/` 中已经整理好的自包含知识
- 用户当前指定的目标目录及其直接产物

在没有用户明确允许之前，不得为了补足判断而去翻看其他 sibling workflow、其他 example、其他历史样例目录，也不得把别的例子里的材料参数、目录组织或文件组合拿来当当前目标目录的内容依据。

这里要刻意区分两种用途：
- **authoring / 抽象沉淀**：可以从历史讲义、源码或 example 中提炼可复用规则，再整理回 `skills/knowledge/`
- **当前目录验证 / 续跑**：必须以当前目标目录为主证据，不能跨目录借例子

如果当前目标目录本身无法支持某个结论，正确动作是：
- 先明确这是当前目录内尚未建立的事实
- 优先退回 `skills/knowledge/` 中已有的稳定契约
- 如果还不够，就问用户，而不是自行去别的例子里找“最像的”目录来套

只有在用户明确授权“可以参考别的例子”后，才允许做跨 example 对比；而且即使这样，其他例子也只能作为**格式或历史参考**，不能直接覆盖当前目标目录已经给出的事实。

对存在多条自然分支的 workflow，这条原则还要再落成**显式目录判据**。例如 L3 effective Hamiltonian：
- 如果当前目标目录只是扁平 DFT 结果集，例如一批 `<id>.OUTCAR` / `<id>.OSZICAR` / `<id>.log`，可选再带一个共享 `POSCAR`，而当前目录自己看不到 `0.generaterandomspin/`、`1.vaspncl/`、`2.get_dft_data/`、`3.get_fitting_data/`、`4.fit/` 这类前序阶段目录，则应先判为 Path B 起点；
- 只有当当前目标目录自己已经出现这类前序阶段链时，看到 DFT 结果才优先解释为拟合链路中的中游阶段；
- 不得因为“别的 sibling 目录里有完整阶段链”就覆盖当前目标目录的路径判断；
- 也不得因为 Path B 当前还缺共享基底前置文件，就把本来已经明显属于 Path B 的目录又改判成“拟合步骤”。

---

## 3. 当前推荐架构

当前结构应保持为：

```text
skills/
├── README.md
├── SKILL.md
├── subskills/
│   ├── pasp-orchestrator/
│   ├── pasp-reference/
│   ├── pasp-verifier/
│   └── workflow-*/
└── knowledge/
    ├── workflows/
    ├── templates/
    ├── scripts/
    └── reference/
```

### 3.1 顶层入口 `SKILL.md`
职责：
- 只做总入口
- 先判断 workflow / reference / mixed
- 把请求交给最小的下游 skill

不要把大量 PASP 领域知识堆在入口层。

语言约定：
- `skills/SKILL.md` 与 `skills/subskills/*/skill.md` 这类路由 / 薄入口文件使用英文，便于稳定触发 intent routing、STOP gate 和 delegation 规则。
- `skills/knowledge/workflows/` 与 `skills/knowledge/reference/` 中的长知识文档可以继续使用中文；路径、文件名、参数名保持英文。
- 不要为了英文入口层而把长 workflow 细节复制进 subskill；入口层只负责路由、硬 gate 和查阅哪个知识文件。

### 3.2 `subskills/pasp-orchestrator/skill.md`
职责：
- 识别任务属于哪个 workflow
- 把“输入修改/调参请求”当作 **workflow-first 的 mixed 问题** 来处理
- 要求 workflow 回答时包含：
  - 当前阶段
  - 当前阶段可调整项
  - 每项控制什么
  - 哪些项必须先查 reference

边界：
- 这一层只负责**路由与早确认**，不负责展开某个 workflow 的内部科学细节
- 如果某个 workflow 内部还存在多条分支、阶段切换或共享基底阻断条件，例如 L3 的路径 A / 路径 B，这些判断规则必须写到对应的 `workflow-*` 子 skill 和 `knowledge/workflows/*.md` 中
- `pasp-orchestrator` 可以说“这里需要继续确认”“这里应交给对应 workflow 子 skill 判断”，但不应自己保存某个 workflow 的详细分支判据、参数清单或材料级建模护栏
- 换句话说：入口层负责“把问题送到哪里”，workflow 子 skill 才负责“到了这里以后怎么判断内部路径”

### 3.3 `subskills/pasp-reference/skill.md`
职责：
- 作为字段/文件/模块/主题查询层
- 查询来源仅限 `skills/knowledge/reference/`

### 3.4 `subskills/pasp-verifier/skill.md`
职责：
- 作为 PASP 包内部的 read-only verifier 契约
- 定义 bounded fact collection 的 mode、输入边界、输出格式和禁止事项
- 被 workflow / reference / orchestrator 在需要委派事实检查时引用

边界：
- 它不是用户任务入口，不负责 intent routing
- 它不是 Codex / Claude 平台注册文件
- 它不能决定 workflow 路由、不能替用户选择物理参数、不能修改文件、不能提升正式 input、不能准备或提交任务、不能输出最终用户答复

平台注册文件由安装脚本生成：
- `<target>/.codex/skills/pasp-helper`：Codex 项目级入口 skill，安装时软链接到工作目录的 `skills/`
- `<target>/.codex/skills/pasp-verifier/SKILL.md`：Codex verifier skill wrapper
- `<target>/.codex/agents/pasp-verifier.toml`：Codex read-only verifier agent
- `<target>/.claude/skills/pasp-helper`：Claude 项目级入口 skill，安装时软链接到工作目录的 `skills/`
- `<target>/.claude/agents/pasp-verifier.md`：Claude read-only verifier agent，使用 `tools: Read, Glob, Grep`

旧版安装可能留下 `$HOME/.claude/skills/pasp-dev`、`$HOME/.claude/skills/paspskills` 或 `$HOME/.claude/skills/pasp-helper` 这类 Claude 用户级入口；当前安装脚本只把它们作为 legacy user-scope entry 检查、警告或在 `--force` 时移除，不把它们作为新安装目标。

这些入口 / agent 文件应保持很薄，只负责暴露或导向 `skills/subskills/pasp-verifier/skill.md`。不要在平台 wrapper 中复制完整 PASP reference、workflow gate 或 verifier mode 细节；否则安装目标和 PASP 包内容会漂移。

### 3.5 `subskills/workflow-*/skill.md`
职责：
- 只负责各自 workflow
- 判断当前阶段
- 给出下一步输入、检查点、可调项
- 需要时明确把用户引到 reference

每个 workflow 子 skill 都应带上“调参护栏”规则，而不仅是“流程概述”。
如果某个 workflow 内部本来就有多条自然分支，例如：
- 路径 A / 路径 B
- `cell.str` / `unit_cell.str` 路线 vs `READ_POSCAR` / `READ_POSCAR_UC` 路线
- 共享基底确认阶段 vs 样本编码阶段

则这些分支的判据、阻断规则和待确认参数，都必须下沉到该 workflow 子 skill 与对应 workflow 文档中；不要上提到 `SKILL.md` 或 `pasp-orchestrator`。

如果某个 workflow 已经变长，且中间存在必须停下来的参数确认、输入 preflight 或代表点位确认，不能只把 STOP 规则埋在长文档中。应新增一个短的 `*_state_machine.md` 或等价 gate 文件，并让对应 `workflow-*` 子 skill 明确要求：
- 先读短 gate 文件判断状态和 STOP 条件；
- 只有当前状态需要细节时，才读长 workflow 的对应部分；
- 长 workflow、模板、脚本说明和 run-notes 都不能覆盖 gate 文件中的 STOP 条件。

这类 gate 文件应写成状态机，而不是说明书：每个状态都要列出允许动作、禁止动作、进入下一状态的前置条件，以及需要记录的确认标志。

对有正式输入、run 目录或提交阶段的 workflow，gate 文件必须把草稿、候选输入、正式 `input/` 和 `runs/<run-id>/` 分开：
- 未确认参数只能进入 `notes/`、`drafts/` 或 `*.draft`
- 已确认参数但未 preflight 的文件只能是 candidate
- 正式 `<stage>/input/` 必须等 input preflight pass
- `<stage>/runs/<run-id>/`、提交脚本、外部任务配置和提交准备必须等正式 input 和所需确认 flag 都满足

如果 workflow 使用 subagent，gate 文件还必须明确：用户授权 subagent 只授权只读事实检查，不等于授权提交，不等于确认物理参数。一般 workflow 缺少 read-only subagent preflight 时，要么记录 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`，要么记录 `NO_SUBAGENT_PREFLIGHT_AVAILABLE=true` 及原因；否则不得提升正式 input 或派生 run。对 L3 这类已定义 subagent preflight 硬门禁的 workflow，用户授权 subagent 后，`NO_SUBAGENT_PREFLIGHT_AVAILABLE=true` 只能导致 blocked 或草稿输出，不能替代 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`。

### 3.6 `knowledge/workflows/*_run_notes.md`
职责：
- 记录历史服务器实跑观察、实例值、脚本修正点、完整样例覆盖范围
- 为后续作者提供“曾经真实出现过什么”的上下文
- 明确这些内容不是 workflow 主契约

运行时默认不应把 `*_run_notes.md` 里的实例值当成当前用户目录已经发生的事实。

---

## 4. 每个 workflow 文档必须具备的结构

后续新增或重写 workflow 时，`knowledge/workflows/*.md` 至少应包括：

1. **目标**
2. **适用问题**
3. **输入前提**
4. **示例驱动的目录结构或阶段结构**
5. **推荐工作流**
6. **当前步骤常见 reference 入口**
7. **不负责回答的内容**

其中最关键的是：

### 在每个关键阶段都加入这四个小节
- **当前阶段可调整项**
- **这些项控制什么**
- **什么时候不要直接改、先查 reference**
- **修改后要检查什么**

这是后续所有 workflow 必须保持一致的结构。

### 4.1 历史观察必须拆到 `*_run_notes.md`
如果某个 workflow 已经有真实服务器实跑、完整样例整理或脚本修正记录：
- 主文档保留稳定契约
- 新建同名前缀的 `*_run_notes.md`
- 把具体实例值、历史日志现象、脚本修正点、目录实例和完整样例范围迁到 run-notes

主文档里允许保留一句短引用，例如：
- “历史实跑观察与实例值见 `./xxx_run_notes.md`”

但不要在主文档里直接保留：
- “本次实跑得到 9 个 local modes”
- “本次验证中样本 `1..3` 的 TOTEN 分别为 ...”
- “完整样例固定使用 `700/300/9`”

### 为什么必须这样写
因为这不仅是给最终用户看的，也是给 Claude / Codex 自己看的。

当 Claude / Codex 需要帮用户改输入文件时，它必须知道：
- 现在处于哪一步
- 此时哪些设置是正常可调的
- 每个设置在 workflow 语境下控制什么
- 什么时候自己不该猜，必须先查 reference

如果 workflow 文档里没有这层结构，agent 很容易：
- 要么不敢改
- 要么乱改
- 要么把 workflow 问题误当成 reference 问题
- 要么把历史实跑实例误当成当前 workspace 的实时结果

### 4.2 每个 workflow 目录都必须附带 README 式说明
workflow 文档本身还不够。只要 agent 在用户 workspace 中正式搭建或整理某个 workflow 目录，就必须同时补齐 README 式目录说明，至少覆盖：

- workflow 根目录的 `README.md`
- 每个关键阶段目录的 `README.md`
- 如果某个目录本身承担的是批量输入池、共享中间产物或运行输出汇总，也应在该目录放 README，说明它不是普通阶段目录

这些 README 至少要说明：
- 这个目录在整个 workflow 中负责什么
- 目录里的 `input/`、`runs/`、中间产物和最终产物分别是什么
- 它依赖哪个上游目录
- 下游应该消费哪个文件或哪个 run 的输出
- 哪些文件是基线输入，哪些文件是运行后生成的，哪些文件不应手工改写
- 如果这是批量运行目录，还要说明运行结束后哪些文件需要保留，哪些只是临时副本或中间文件，可以清理

这条规则要写成默认要求，而不是“必要时再补”。原因很直接：
- 用户要靠目录本身快速判断每一步在做什么
- agent 续跑时要靠 README 避免把基线输入、run 目录和上游产物混在一起
- 后续如果作业失败、切换参数或换人接手，README 是最低成本的交接材料

---

## 5. 模板与脚本纳入原则

### 5.1 什么应放进 `knowledge/templates/`
应该放：
- **最小但完整**的参考输入模板
- 能帮助用户和 agent 在没有原始 examples 目录的情况下，从 0 起步
- 例如：
  - `PASP.input`
  - 配套的 `cell.str` / `unit_cell.str`
  - 拟合阶段的 `Fitting_*.txt`
  - `convert_info.txt`
  - 作业脚本模板 `slurmpasp.sh`

不应放：
- 大量原始 example 数据
- 高度材料特定、不可泛化的庞大输入集合
- 只是“看起来很多”，但没有普适复用价值的文件

### 5.2 什么应放进 `knowledge/scripts/`
应该放：
- examples 中反复出现、可抽象成通用模板的辅助脚本
- 它们不属于 PASP 核心功能，但会影响 workflow 能否实际跑通
- 例如：
  - `postprocess.sh`
  - `createINCAR.sh`
  - `get_ene.sh`
  - 经过抽象后的批量运行模板，例如 method-6 的逐样本顺序批跑脚本

不应放：
- 与某台机器或某个固定路径强耦合、又没有模板价值的脚本
- 大量只对单个 example 有意义的临时脚本
- 当前某一次提交里带有硬编码 workspace 路径、固定 `run-id`、固定共享基底目录的现场脚本原样副本

### 5.3 模板与脚本的写法要求
每个纳入 `templates/` 或 `scripts/` 的文件都应尽量满足：
- 自包含
- 可作为起点
- 明确标出哪些地方需要用户按自己环境修改
- 不依赖外部 `pasp_examples/` 才能理解

必要时应在同目录加一个 `README.md`，说明：
- 这个模板/脚本用于 workflow 的哪一步
- 它依赖哪些输入
- 哪些内容必须用户自行替换

### 5.4 简单批处理不要过度工程化
如果某个 workflow 阶段本质上只是：
- 外层设一次环境
- `for` 循环遍历样本编号
- 为每个样本复制输入
- `cd` 进入样本目录
- 直接执行 `PASP.x` 或等价单程序入口

那么默认应保持为这种直接写法，不要优先引入：
- 额外函数分层
- 复杂严格模式，例如对当前环境不稳定的 `set -e`
- 与当前任务无关的抽象包装
- 为了“通用性”强行加入的大量防御性逻辑

要写进 skills 的应是：
- 这种简洁批跑思路本身
- 一个去掉硬编码后的模板脚本

不应写进 skills 的是：
- 当前用户某一次任务现场使用的完整硬编码脚本原样副本

### 5.5 拟合阶段的强制保留项和跳过项必须先问用户
对 L3 拟合阶段，下面这些不是 agent 可以默认拍板的模板项：
- `I_HAVE_KEEP_TERM`
- `I_HAVE_SKIP_TERM`
- `Fitting_Set_Term_Keep.txt`
- `Fitting_Set_Term_Skip.txt`

默认规则应写死为：
- 只要拟合阶段准备启用强制保留项或强制跳过项，必须先问用户
- 不能因为模板里已有某个默认值，就直接沿用
- 不能因为旧 example、历史 run 或某次实验里用过，就默认当前材料也继续用
- 若用户没有明确要求，默认应先按“不启用 keep/skip”准备拟合输入

### 5.6 Path B 的汇总和转换规则也要固化成默认约束
对 L3 Path B，method-6 批量运行结束后，下面这些规则应作为 skills 的默认契约：

- 每个样本真正有下游价值的特征文件是 `distortion.ene_symbol`
- 进入 `3.get_fitting_data` 时，应把它们汇总成标准命名的 `ene_symbol/<id>.ene_symbol`
- 同时接入上游 `Energy.dat` 和 method-6 的 `status.tsv`
- 在 `status.tsv` 没确认样本成功前，不应直接继续数据转换
- 如果样本编号从 `0` 开始，转换脚本必须显式使用 `--start-id 0`，不要要求用户先手工重编号
- `convert_info.txt` 第三行不是自由调参项；当当前结构链已经确定时，应由结构关系自动推导，而不是再问用户一次

### 5.7 提交后先做最小验活
对会在服务器端长时间运行的 workflow，提交成功不等于真正起跑。开发规范里应默认要求：

- 提交后先检查最小输出是否已经开始出现
- 例如 run 目录是否已生成、样本子目录是否开始出现、`status.tsv` / `batch.log` / `log.out` 是否开始落盘
- 在这些最小迹象出现前，不要过早向用户表述为“任务已经正常在跑”
- 如果只看到空 run 目录或只有头文件，就应优先排查脚本前几行、环境初始化和入口命令，而不是先假设 PASP 本体有问题

### 5.8 阶段间只复制直接依赖
当 workflow 从一个阶段切到下一个阶段时，默认应只复制“当前程序直接读取的文件”，不要把上游所有整理结果整包搬下来。

例如：
- `4.fit` 默认应复制 `Fitting_Dataset.txt` 和 `Fitting_Data_for_prediction.txt`
- `Energy.dat`、`ene_symbol/`、`status.tsv` 这类上游整理上下文，除非用户明确要求完整归档，否则不应默认作为拟合运行硬依赖重复复制

这样做的目的：
- 保持当前阶段输入包最小且清楚
- 避免用户误以为某些上游文件仍被当前程序直接读取
- 减少 run 目录里重复文件造成的干扰

### 5.9 编号起点必须显式记录
只要某个 workflow 或阶段的样本编号不是模板里最常见的 `1..N`，就必须在 README 或阶段说明中显式写清楚。

最少应说明：
- 当前样本编号从 `0` 开始还是从 `1` 开始
- 下游转换脚本是否需要显式传 `--start-id 0`
- `Energy.dat`、`ene_symbol/<id>.ene_symbol`、批量 run 样本目录三者是否使用同一编号体系

这条规则的目的不是增加文档，而是防止 agent 在编号起点上再次“按模板默认值脑补”。

---

## 6. 调参护栏原则

这是当前最重要的新增约束。

### 6.1 什么叫“调参护栏”
当用户、Claude 或 Codex 在 workflow 过程中准备修改输入文件时，skills 必须先帮助回答：
- 当前阶段能调哪些设置
- 这些设置控制什么
- 哪些能直接改
- 哪些必须先看 reference

### 6.2 哪类请求默认是 workflow-first
以下情况默认应先走 workflow，而不是直接走 reference：
- “这一步该改哪些设置？”
- “我现在在拟合阶段，还能调什么？”
- “如果我要减小模型复杂度，该改哪几项？”
- “当前这一步是不是应该先调截断范围，而不是改别的项？”

### 6.3 哪类请求默认是 reference-first
以下情况默认应先走 reference：
- “`fig.maxk` 是什么意思？”
- “`isaAB` 默认值是什么？”
- “`Fitting_Settings.txt` 每一行是什么意思？”
- “`cell.str` 精确格式怎么写？”

### 6.4 workflow 文档里的调参说明必须是“功能级”，不是“词典级”
例如 workflow 里可以写：
- `fig.maxk` 控制最多考虑到几体相互作用
- `fig.mdist` 控制不同体数的截断范围
- `Fitting_Set_Lambda.txt` 控制 lambda 扫描范围

但不要在 workflow 里把所有默认值和所有格式细节重新写一遍。

---

## 7. 阶段输入包与运行目录隔离原则

PASP 运行过程中通常会产生大量输出、中间文件和日志，也可能出现原地修改或覆盖已有文件的行为。为了保证输入可复现、输出可追踪，workflow 应默认区分“阶段输入包”和“实际运行目录”：先保证当前阶段的 `input/` 是完整基线，再复制成独立 `runs/<run-id>/` 目录，并在 run 目录中接入上游产物后运行 PASP 或后处理脚本。

推荐目录模式：

```text
project/
├── <stage>/
│   ├── input/
│   └── runs/
│       └── <run-id>/
└── notes/
```

### 7.1 推荐运行方式
- `<stage>/input/` 保存当前阶段干净输入基线、模板派生文件或人工整理后的起点。
- `<stage>/input/` 必须是当前阶段的完整输入包：凡是 `PASP.input` 或入口文件直接 `%include` / 读取的文件，都应在该输入包中齐全；如果某个文件是运行时生成或由上游覆盖，workflow 必须明确说明。
- 候选输入包提升为正式 `<stage>/input/` 前，必须先做一次只读 stage preflight。一般 workflow 在不能使用 subagent 时，主 agent 也必须按同一清单本地检查并记录“本次未使用 subagent”。若具体 workflow（例如 L3）声明用户授权后 subagent preflight 是硬依赖，则必须由 read-only subagent 检查；不能使用 subagent 时应 blocked，除非用户明确豁免该硬门禁。
- 每次运行前，将对应阶段的 `input/` 完整复制到 `<stage>/runs/<run-id>/`。
- 复制后，再把上游阶段产物接入 run 目录，例如把数据整理阶段生成的 `Fitting_Dataset.txt`、`Fitting_Data_for_prediction.txt` 覆盖到拟合 run 目录。
- 从 `<stage>/input/` 派生 `<stage>/runs/<run-id>/` 前，也必须确认 stage preflight 仍为 pass；如果 run 目录还需要接入上游产物，preflight 应同时检查上游产物来源和版本是否匹配。
- 只在 `runs/<run-id>/` 中运行 PASP、DFT、转换脚本或后处理脚本。
- 每个 `runs/<run-id>/` 应保留本次真实使用的输入文件、输出文件、日志和必要的运行说明。
- 调参、重跑、lambda 扫描或样本规模变化时，优先新建 run 目录，不直接覆盖旧目录。
- 下游阶段应消费明确的上游产物或某个 run 的输出，不应隐式读取被运行污染过的 baseline `input/`。

### 7.2 为什么默认隔离运行
这样做可以避免：
- 原始输入被输出文件污染
- 多次运行的中间文件混在一起
- 无法判断一次结果对应哪版输入
- subagent 盘点目录时难以区分输入、输出和旧残留
- stage `input/` 本身缺文件却被 run 目录临时拼凑掩盖
- run 目录没有接入上游产物，导致下游任务拿到过期或不匹配的数据
- 出错后无法快速回到干净基线

### 7.3 允许原地运行的例外
只有当用户明确知道自己要覆盖当前目录，或当前只是一次临时试跑时，才可以原地运行。即便如此，agent 也应先提醒这会降低可复现性，并建议至少备份关键输入文件。

### 7.4 Stage preflight 检查契约
stage preflight 是事实检查，不是参数决策。subagent 或主 agent 检查者只能输出 pass / fail / blocked、证据路径和阻断原因；不能替用户决定物理参数、不能修改输入、不能提交任务，也不能把运行探测、外部任务创建或提交准备当成 preflight 的替代品。

目录盘点、VASP 结果清点、脚本状态检查、日志摘要都不等于 stage preflight。stage preflight 必须明确点名本次检查的候选 PASP / workflow 输入文件、目标 stage、适用 checklist，并逐项给出结论。只有“目录里有什么”的 inventory 结果，不能作为提交前或提升为正式 input 的依据。

通用 preflight 至少检查：
- 当前阶段必需文件是否存在，且入口文件直接 `%include` / 读取的文件在同一个输入包或明确的上游接入位置中齐全
- 高风险参数、结构转换、编号规则或 keep/skip 等选择是否已有用户确认或明确来源
- 上游产物是否来自预期 stage / run / 数据链，而不是 sibling example、旧 run 或未标注来源的缓存
- README、提交脚本、目录名是否把仍有待确认项的候选输入包装成可提交正式输入
- 脚本期望工作目录、相对路径和输出位置是否与当前 stage 目录契约一致
- 若有 stage-specific checklist，必须一并通过

---

## 8. Claude / Codex 的行为约束

这套 skills 不只是面向人，也是在约束 agent 自己的行为。

### Claude / Codex 在修改输入文件前应遵循：
1. 先判断当前 workflow
2. 再判断当前阶段
3. 再看 workflow 文档里“当前阶段可调整项”
4. 如果准备修改的项不在当前阶段可调项里，先停下来
5. 如果修改涉及：
   - 默认值
   - 精确语义
   - 编号规则
   - block 格式
   - 文件格式
   则必须先看 reference

### 字段 / 文件写入前的 reference gate
无论是在开发 skills，还是在运行时 agent 帮用户生成、修改或覆盖 PASP 输入，只要要把某个字段、block、文件或编号规则实际写进用户目录，就必须先查 `skills/knowledge/reference/` 中对应的权威说明。

这条规则优先级高于模板、历史样例和 agent 记忆：
- workflow 文档只能告诉 agent 当前阶段“应该考虑哪些项”和“这些项控制什么”
- reference 文档才负责告诉 agent 某个字段、block 或文件“精确应该怎么写”
- 模板只能作为起点，不能替代 reference 中的字段/格式规则
- 历史 run-notes 只能说明过去出现过什么，不能替代当前写入前的 reference 查证

实际写入前至少要确认：
- 字段名、block 名、文件名是否正确
- block 起止格式、行顺序、列含义和编号起点是否正确
- 文件是 hard-required、条件 required，还是环境/helper 文件
- 当前 workflow 阶段是否允许改这个项
- 如果当前 reference 没有建立写法或依赖关系，应停下来问用户，而不是从相似字段、相似文件或旧 example 类推

典型反例：
- 不能因为 `cell.str` 有 `NumberOfAtoms` / `LatticeVectors`，就把同样格式复制成 `unit_cell.str`
- 不能因为模板里有某个 keep/skip 文件，就默认当前拟合也启用它
- 不能因为旧 example 中某个编号、默认值或路径成立，就把它当成当前材料的正式设置

### Claude / Codex 不应做的事
- 不应因为用户提出一个目标，就直接随意改复杂字段
- 不应把 workflow 文档里提到的字段，自动当作“都能改”
- 不应在不理解 reference 的情况下修改高风险输入
- 不应把 workflow 文档写成 reference 的替代品

---

## 9. Subagent 委派原则

PASP workflow 往往包含较长的 reference 查询、用户目录盘点、日志阅读、模板对比和源码校准。为了避免主 agent 的上下文被这些材料占满，skills 可以鼓励主 agent 把边界清楚的查证型任务委派给 subagent。

本仓库统一使用 `skills/subskills/pasp-verifier/skill.md` 作为 read-only PASP verifier 契约。workflow / reference 文档需要委派事实检查时，应优先引用它的 mode，而不是在每个 workflow 中重新发明一套 subagent 输出格式。当前标准 mode 包括：
- `reference-check`
- `input-preflight`
- `directory-inventory`
- `output-validation`
- `structure-analysis`
- `log-summary`
- `template-compare`
- `source-audit`

平台安装层必须和这份契约分开：
- Codex agent 注册文件是 `.codex/agents/pasp-verifier.toml`，使用 TOML 格式和 `sandbox_mode = "read-only"`。
- Claude agent 注册文件是 `.claude/agents/pasp-verifier.md`，使用 frontmatter，例如 `tools: Read, Glob, Grep`。
- Codex 项目级 skills 放在 `.codex/skills/`，Claude 项目级 skill 入口放在 `.claude/skills/`；它们都是平台入口 wrapper，不是 PASP runtime 知识源。
- `$HOME/.claude/skills/pasp-dev`、`$HOME/.claude/skills/paspskills` 和 `$HOME/.claude/skills/pasp-helper` 都只是旧版 Claude 用户级入口。当前安装脚本只检查、警告或在 `--force` 时移除它们，不把它们作为新安装目标。

不要手工维护多份 verifier 规则。新增 mode、修改输出格式或改变禁止事项时，先改 `skills/subskills/pasp-verifier/skill.md`，再更新 `scripts/install-pasp-skills.sh` 生成的 Codex / Claude wrapper，让 wrapper 继续引用 canonical 契约。默认使用安装脚本部署，不建议单独复制某一个 `.codex` 或 `.claude` 文件。安装脚本必须支持从源仓库直接运行，也支持把脚本单独复制到目标目录后运行；后者不能依赖脚本相对路径反推源仓库，必要时应通过 `--source` 或 `PASP_SKILLS_SOURCE` 指定源 PASPskills 仓库。

### 9.0 授权优先规则
如果当前运行环境要求用户显式授权才能使用 subagent，workflow skill 不能写成“自动调用 subagent”。正确写法是：
1. 当任务包含全流程新目录验证、长日志摘要、多阶段目录盘点、模板对比、reference 查询或开发期源码查证时，先判断哪些子任务适合委派。
2. 在执行这些子任务前，主 agent 先询问用户是否允许使用 subagent / delegation / parallel agent work。
3. 用户允许后，才把边界清楚的事实收集任务委派给 subagent。
4. 对一般事实收集任务，用户不允许、没有回应或工具不可用时，主 agent 自己完成事实收集，并在最终报告或任务记录中说明“本次未使用 subagent”。若具体 workflow 已把 subagent preflight 定义为运行前硬依赖，则工具不可用不能自动降级为本地检查，应 blocked 并请用户决定是否豁免。

这条规则的目的不是强制所有 workflow 都使用 subagent，而是让 agent 在权限允许时尽量多用 subagent 承担事实收集、日志压缩和目录盘点，减少主模型上下文占用，同时不和运行环境的权限规则冲突。

### 9.1 主 agent 保留的职责
主 agent 必须保留：
- 用户目标和当前 workflow / stage 状态
- workflow-first / reference-on-demand 的路由判断
- 是否需要修改输入文件的最终判断
- 对 subagent 结果的整合、取舍和风险判断
- 面向用户的最终回复

subagent 不应替主 agent 决定最终 workflow 路由，也不应在没有主 agent 审核的情况下直接给出高风险参数修改结论。

### 9.2 适合委派给 subagent 的任务
适合委派的是范围小、可验证、可压缩汇报的任务，例如：
- 用 `pasp-verifier` `mode: reference-check` 在 `skills/knowledge/reference/` 中查询一个参数、文件、topic 或 module 的精确定义
- 用 `pasp-verifier` `mode: directory-inventory` 盘点用户运行目录，识别已有输入、可能的阶段线索、缺失文件和不确定项；它不能替代 input preflight
- 用 `pasp-verifier` `mode: input-preflight` 对候选 `<stage>/input/` 或 `<stage>/runs/<run-id>/` 做只读 stage preflight，检查文件齐全性、上游来源、用户确认记录和 stage-specific checklist
- 用 `pasp-verifier` `mode: output-validation` 对已完成 run 做只读 output validation，清点实际输出、日志、失败样本、下游 handoff 文件和输出数据链一致性
- 用 `pasp-verifier` `mode: structure-analysis` 对 `POSCAR`、候选 `POSCAR_UC`、`cell.str`、`unit_cell.str`、`SuperCell` 做只读结构关系分析，汇报 primitive 判断、轴向、元素顺序、原子映射、体积比和不确定项
- 用 `pasp-verifier` `mode: log-summary` 阅读 PASP 运行日志，提取首个关键错误、相关 warning、出错阶段和可能关联的输入文件
- 用 `pasp-verifier` `mode: template-compare` 将用户输入文件与 `skills/knowledge/templates/` 中的模板做结构差异对比
- 用 `pasp-verifier` `mode: source-audit` 在开发 skills 时检索 PASP / Latticemodel 源码，用于确认隐藏输出、warning 触发条件或文件生成逻辑
- 按 workflow 规范审查某个 `skills/knowledge/workflows/*.md` 是否缺少输入、输出、上下游依赖、可调项或 reference handoff

### 9.3 不适合委派给 subagent 的任务
不应委派给 subagent 独立完成：
- 判断用户真实科研目标
- 最终选择 workflow 或跨 workflow 改路由
- 直接修改复杂 PASP 输入文件，或把候选结构直接提升成正式 `POSCAR_UC` / `unit_cell.str`
- 替用户决定 `Spin_values`、截断半径、展开阶数、SOC 策略、keep/skip 等物理或拟合设置
- 在 reference 不完整时臆测字段默认值、精确语义或文件格式
- 同时修改多个相互依赖的 skill 路由文件

### 9.4 subagent 输出契约
subagent 的输出必须短，并且优先使用 `pasp-verifier` 的统一形状：
- 查证范围
- 结论
- 来源路径或日志位置
- 确定项与不确定项
- 是否需要主 agent 继续查 reference 或询问用户
- pass / fail / blocked / not-applicable 结论（适用时）

subagent 只汇报事实和局部判断，不输出最终用户答复。主 agent 应只把压缩后的事实链纳入上下文，并在最终答复中明确哪些结论来自 curated knowledge、用户文件、运行日志或开发期源码校准。

---

## 10. 后续 workflow 的补全顺序建议

推荐继续补全时按下面顺序做：

1. 先补 workflow 知识文档
2. 再补对应 workflow 子 skill
3. 如果 examples 里有明显可复用的最小输入模板，再补 `templates/`
4. 如果 examples 里有明显可复用的辅助脚本，再补 `scripts/`
5. 最后补 reference 中缺失的字段卡片

不要反过来先堆大量 reference，再去猜 workflow 应该怎么走。

---

## 11. 新增 workflow 时的检查清单

后续新增一个 workflow 前，先确认：
- [ ] 它是否真的是任务型 workflow，而不是 reference/onboarding
- [ ] 是否能用 1 句话说清目标
- [ ] 是否能拆成明确阶段
- [ ] 是否能从 examples 中提炼出最小目录结构
- [ ] 是否存在值得纳入的完整模板
- [ ] 是否存在值得纳入的辅助脚本模板
- [ ] 是否能为每个阶段写出：
  - 当前阶段可调整项
  - 每项控制什么
  - 什么时候先查 reference
  - 修改后要检查什么
- [ ] 如果已有历史实跑观察，是否把实例值、日志现象和脚本修正记录放进独立的 `*_run_notes.md`
- [ ] 主 workflow 文档是否只保留稳定契约，没有把 run-specific 数值混在主路径里

如果做不到这些，就说明当前 workflow 资料还没准备好，不要急着生成 skill 文件。

---

## 12. 当前建议优先延续的标准

Lecture 2 / Lecture 3 目前是最完整的可复用标准；Lecture 4–8 已有基础 workflow / subskill 覆盖，L4 已有 state machine 与 run-notes，但整体仍需要按同一标准继续补齐模板、脚本、调参护栏、preflight 细节，并为 L5–L8 评估是否需要补充 state machine / run-notes。后续几个 workflow 建议尽量延续：

- workflow 文档不是只讲概念，而是要能指导实际执行
- examples 中有复用价值的模板和脚本，应提炼到 `skills/knowledge/`
- workflow 文档中必须有“调参护栏”结构
- reference 继续保持为字段定义和格式规则的权威来源
- skill 路由保持“workflow-first, reference-on-demand”的混合模式

---

## 13. 文档边界说明

这份文档是**原则性约束文件**，不是：
- 最终用户使用说明
- 具体字段手册
- 某个 workflow 的操作模板

它的用途是：
- 约束未来继续开发 PASP skills 时不要跑偏
- 保证后续 workflow 补全时仍然遵守统一标准
- 保证 Claude / Codex 在后续开发和使用时，知道这套系统到底是怎么分层、怎么判断、怎么约束修改行为的
