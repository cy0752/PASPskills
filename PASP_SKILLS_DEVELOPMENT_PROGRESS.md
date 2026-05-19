# PASP Skills 开发进展汇报材料

> 面向对象：用于给本地 agent 生成 PPT 的 Markdown 简报  
> 项目路径：`/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/PASPskills`  
> 当前日期：2026-04-27  
> 建议用途：作为 PPT 内容源，不建议逐字照搬；可由 PPT agent 提炼成 12-18 页演示稿。

---

## 1. 一句话总结

PASP Skills 项目把 PASP 相关知识从“零散讲义 / example / 经验记忆”整理成一套可部署、可路由、可验证的 agent skills 包：顶层只做意图分类，workflow 文档负责流程推进，reference 文档负责字段和文件的精确定义，verifier subagent 负责只读事实检查，安装脚本负责把同一套知识接入 Codex 和 Claude。

---

## 2. 推荐 PPT 结构

1. 项目背景：为什么需要 PASP Skills
2. 核心目标：把 PASP 问答变成可路由、可验证、可部署的系统
3. 总体设计：workflow / reference / verifier 三层分工
4. 当前目录结构：`skills/` 自包含运行包
5. 顶层路由：`SKILL.md` 与 `pasp-orchestrator`
6. Workflow 覆盖：目前支持的 7 类 PASP 工作流
7. Reference 知识库：字段、文件、主题、模块的结构化查询
8. L3 有效哈密顿量：目前最完整、约束最多的 workflow
9. 只读 verifier 契约：为什么引入 subagent
10. 安装与平台接入：Codex / Claude 如何使用同一套知识
11. 当前完成情况：已完成、基本可用、仍需完善的部分
12. 典型使用场景：用户如何从结构、输入文件或报错进入
13. 开发原则：thin routing、reference-before-write、self-contained runtime
14. 风险与下一步：reference 补全、端到端测试、平台兼容性

---

## 3. 项目背景

PASP 计算流程覆盖面很广，既包括交换路径分析、有效哈密顿量、Monte Carlo、Dynamics、GA、TB、KNB 等任务型流程，也包括大量输入文件、参数、block、输出文件和中间文件的精确格式。传统使用方式通常依赖：

- 讲义中的长篇说明；
- 历史 example 目录；
- 人的经验记忆；
- 用户当前目录中不完整的输入 / 输出；
- 临时脚本和手工判断。

这对 agent 来说有几个明显问题：

- **上下文过大**：直接加载讲义、源码或 example 会占用大量上下文。
- **路由不稳定**：用户问“怎么做”和“某字段是什么意思”时，agent 容易混在一起回答。
- **容易误写输入**：PASP 输入字段、block、编号规则和依赖文件复杂，agent 不能只靠模板或记忆直接写正式输入。
- **历史样例污染当前任务**：旧 example 或 run-notes 里的值不一定适用于当前材料。
- **平台接入分散**：Codex 和 Claude 的入口、subagent 配置不同，规则如果重复维护会漂移。

PASP Skills 的开发目标就是把这些问题系统化解决。

---

## 4. 核心开发思路

### 4.1 自包含运行包

运行时只依赖 `skills/` 目录内部内容，不依赖外部讲义目录、example 目录或源码目录。讲义和 examples 可以作为整理素材，但部署后的 agent 应只从 curated knowledge 中取事实。

核心运行依赖包括：

- `skills/SKILL.md`
- `skills/subskills/`
- `skills/knowledge/workflows/`
- `skills/knowledge/reference/`
- `skills/knowledge/templates/`
- `skills/knowledge/scripts/`

### 4.2 Workflow 与 Reference 分离

项目把用户请求分为两类：

- **workflow**：用户想完成任务，例如“怎么开始”“下一步是什么”“从 POSCAR 怎么做有效哈密顿量”。
- **reference**：用户想查询定义，例如“`fig.maxk` 是什么意思”“`unit_cell.str` 怎么写”。

关键原则：

- workflow 负责判断阶段、目标、下一步和可调整项；
- reference 负责精确字段语义、默认值、格式、编号规则和条件依赖；
- mixed 问题先 workflow，再按需 reference；
- 写入正式输入前必须 reference-before-write。

### 4.3 Thin Routing

顶层 `skills/SKILL.md` 不承载 PASP 细节，只做意图分类和最小路由。这样可以降低上下文消耗，并避免入口文件变成难维护的大手册。

`pasp-orchestrator` 是任务分流层，负责把用户任务路由到对应 workflow，但它也不展开每个 workflow 的内部分支细节。内部 Path A / Path B、stage gate、可调整字段等属于对应 workflow subskill。

### 4.4 Reference-Before-Write

任何实际写入、覆盖或提升为正式输入的 PASP 字段、block、文件格式或编号规则，都必须先有 reference 或用户提供的权威来源支持。

这条规则解决的问题是：

- 防止从相似字段类推；
- 防止把模板默认值当成用户确认；
- 防止把历史 example 当成当前材料事实；
- 防止在没有完整依赖关系时生成看似可运行的错误输入。

### 4.5 只读 Verifier Subagent

项目引入 `skills/subskills/pasp-verifier/skill.md` 作为统一的 read-only verifier contract。它不是用户入口，而是主 agent 在需要时委派事实检查的规则。

Verifier 只做：

- reference 查询；
- input preflight；
- directory inventory；
- output validation；
- structure analysis；
- log summary；
- template compare；
- source audit。

Verifier 不做：

- 选择科学参数；
- 决定最终 workflow；
- 修改文件；
- 提升正式 input；
- 创建 run 目录；
- 写 submission 脚本；
- 提交任务；
- 生成最终用户答复。

---

## 5. 当前项目结构

核心目录如下：

```text
skills/
├── README.md
├── DEVELOPMENT_GUIDE.md
├── SKILL.md
├── subskills/
│   ├── pasp-orchestrator/
│   ├── pasp-reference/
│   ├── pasp-verifier/
│   ├── workflow-l2-spin-models/
│   ├── workflow-l3-effective-hamiltonian/
│   ├── workflow-l4-monte-carlo/
│   ├── workflow-l5-dynamics/
│   ├── workflow-l6-ga-search/
│   ├── workflow-l7-tight-binding/
│   └── workflow-l8-spin-induced-polarization/
└── knowledge/
    ├── workflows/
    ├── templates/
    ├── scripts/
    └── reference/
```

平台接入和开发辅助目录包括：

```text
scripts/
└── install-pasp-skills.sh

.codex/
├── agents/
└── skills/

.claude/
├── agents/
└── skills/

.agents/skills/
└── Trellis / Codex 开发辅助 skills

.trellis/spec/
└── 项目开发规范和质量约束
```

注意：`.agents/skills/` 当前主要用于本仓库的 Trellis/Codex 开发辅助技能，不再作为 PASP runtime skill 的主要安装入口。

---

## 6. 核心模块说明

### 6.1 `skills/SKILL.md`

顶层入口 skill，职责很窄：

- 判断用户是在问 workflow 还是 reference；
- 对 mixed 问题执行 workflow-first；
- 读取最小相关 subskill；
- 禁止使用 `pasp-dev:pasp-orchestrator` 这类 colon-qualified nested skill 名称。

它不展开具体 PASP 领域知识，不直接处理复杂参数。

### 6.2 `subskills/pasp-orchestrator/skill.md`

任务路由层，负责：

- 把用户问题分类为 workflow / reference / mixed；
- 根据关键词路由到 L2-L8 workflow；
- 对只有结构文件或 `OUTCAR + POSCAR` 的请求先要求确认 workflow / Model；
- 指导 run directory isolation；
- 规定什么时候可以使用 verifier subagent。

它的设计重点是“路由和安全边界”，不是承载每个 workflow 的详细操作。

### 6.3 `subskills/pasp-reference/skill.md`

reference 查询层，负责：

- 字段含义；
- 文件格式；
- 参数默认值；
- block 语法；
- Model / module 定义；
- reference 目录查询策略。

它避免把 workflow 阶段规划和完整任务执行混进 reference 回答。

### 6.4 `subskills/pasp-verifier/skill.md`

只读事实检查契约。它给 Codex / Claude 的 subagent wrapper 提供统一行为规范，避免各平台维护多份不同规则。

标准输出格式：

```text
Scope:
Findings:
Sources:
Uncertain:
Needs main-agent decision:
Conclusion: pass | fail | blocked | not-applicable
```

### 6.5 `subskills/workflow-*`

每个 workflow subskill 负责一个任务型流程：

- 判断当前阶段；
- 指出下一步；
- 说明当前阶段可调整项；
- 标明哪些项需要 reference；
- 定义 STOP gate；
- 避免直接写入缺少确认的正式输入。

---

## 7. 当前已支持的 Workflows

目前已接入 7 个 PASP workflow：

| 层级 | Workflow | 入口文件 | 知识文件 |
|---|---|---|---|
| L2 | 交换路径与磁相互作用模型 | `workflow-l2-spin-models/skill.md` | `l2_overview.md`, `l2_find_J_path_sym.md`, `l2_spin_lattice_interaction.md`, `l2_magnon.md` |
| L3 | 有效哈密顿量构建与拟合 | `workflow-l3-effective-hamiltonian/skill.md` | `l3_effective_hamiltonian.md` |
| L4 | Monte Carlo 模拟 | `workflow-l4-monte-carlo/skill.md` | `l4_monte_carlo.md` |
| L5 | Dynamics 模拟 | `workflow-l5-dynamics/skill.md` | `l5_dynamics.md` |
| L6 | GA 全局结构搜索 | `workflow-l6-ga-search/skill.md` | `l6_ga_search.md` |
| L7 | Tight-binding 模型 | `workflow-l7-tight-binding/skill.md` | `l7_tight_binding.md` |
| L8 | Spin-induced polarization | `workflow-l8-spin-induced-polarization/skill.md` | `l8_spin_induced_polarization.md` |

其中 L3 是目前开发最深入的 workflow，已经有独立的 state machine 和 run notes：

- `l3_effective_hamiltonian_state_machine.md`
- `l3_effective_hamiltonian.md`
- `l3_effective_hamiltonian_run_notes.md`

---

## 8. L3 有效哈密顿量工作流的开发重点

L3 当前是 PASP Skills 中最复杂、约束最强的一条 workflow。它覆盖有效哈密顿量构建、样本生成、DFT 数据整理、特征编码、fitting 和后续 handoff。

### 8.1 State Machine First

L3 subskill 要求先读 `l3_effective_hamiltonian_state_machine.md`，再按当前阶段读取长 workflow 文档。这样可以避免 agent 在长文档里迷失，也避免跳过 STOP gate。

核心 gate 包括：

- S2 shared-basis 参数确认 STOP；
- S3 representative-site 确认 STOP；
- S3b fitting settings 确认 STOP；
- S5 input preflight STOP ON FAIL；
- S7 output validation STOP ON FAIL。

### 8.2 Path A / Path B 区分

L3 明确定义：

- **Path A**：PASP-forward sample generation，从确认过的 shared basis 出发生成样本和 `ene_symbol`。
- **Path B**：method-6 encoding，把已有 final structures / magnetic states 编码成 fitting 数据。

这避免 agent 因为“流程从早期开始”就误把任务叫成 Path A。

### 8.3 正式输入前的硬门禁

L3 对正式输入、run 目录和提交前动作要求更严格：

- 用户必须确认 shared-basis 参数；
- representative sites 必须确认；
- 所有显式字段、block、include、依赖文件格式必须有 reference 或用户权威来源；
- formal input promotion 前需要 `pasp-verifier` 的 `input-preflight`；
- `directory-inventory` 不能替代 `input-preflight`；
- output validation 不能反向证明 input 合法。

### 8.4 避免历史样例污染

`l3_effective_hamiltonian_run_notes.md` 只记录历史运行观察，不能当作当前目录事实。当前用户目录必须由实际文件证据支持。

---

## 9. Reference 知识库进展

`skills/knowledge/reference/` 是当前 PASP 精确知识查询的核心。

当前结构包括：

- `topics/`：主题级说明；
- `files/`：文件级说明；
- `params/`：单字段卡片；
- `modules/`：模块说明；
- `toc/`：原始文档目录与提取计划；
- `QUERY_GUIDE.md`：查询策略；
- `STRUCTURE.md`：reference 组织规则。

当前统计：

- `params/` 字段卡片：154 个；
- `files/` 文件说明：19 个；
- `topics/` 主题说明：6 个；
- `modules/` 模块说明：5 个。

Reference 当前覆盖的典型对象包括：

- `PASP.input`
- `MC.input`
- `MD.input`
- `cell.str`
- `unit_cell.str`
- `Fitting_Settings.txt`
- `Fitting_Set_Lambda.txt`
- `Fitting_Set_Term_Keep.txt`
- `Fitting_Set_Term_Skip.txt`
- `J_best.dat`
- `spin_exchange.dat`
- `Zeff.dat`
- `local_mode.mode_definition`
- `Invariant.*`
- `GA.*`
- `TB.*`
- `MD.*`
- `MC`
- `SuperCell`
- `Spin_values`

Reference 的价值在于：当 agent 需要写入或解释某个具体字段时，它有明确路径可以查证，而不是从模板或记忆猜测。

---

## 10. Templates 与 Scripts 进展

### 10.1 Templates

当前 reusable templates 包括：

```text
skills/knowledge/templates/l2_find_J_path_sym/
skills/knowledge/templates/l2_Spin_lattice_interaction/
skills/knowledge/templates/l2_magnon_FM/
skills/knowledge/templates/l2_magnon_spiral/
skills/knowledge/templates/l3_invariant/
skills/knowledge/templates/l3_fit/
```

这些模板用于快速生成最小可用骨架，但不能替代 reference：

- 模板提供起点；
- reference 确认精确写法；
- 用户确认决定科学参数。

### 10.2 Scripts

当前 L3 辅助脚本位于：

```text
skills/knowledge/scripts/l3_effective_hamiltonian/
```

包含：

- `convert_data.py`
- `convert_data.f90`
- `extract_magmoms.py`
- `prepare_path_b_inputs.py`
- `rebase_unit_cell.py`
- `createINCAR.sh`
- `get_ene.sh`
- `postprocess.sh`
- `run_method6_batch.sh`

这些脚本用于支撑 L3 数据整理、结构转换、磁矩提取、Path B 输入准备和批量执行辅助。它们被放在 `knowledge/scripts/` 下，定位是 reusable starting point，而不是绑定某一个外部 example。

---

## 11. 安装与平台接入现状

安装脚本：

```text
scripts/install-pasp-skills.sh
```

当前安装目标：

```text
<target>/skills/                         PASP runtime skills package
<target>/.codex/skills/pasp-dev          Codex project skill symlink
<target>/.codex/skills/pasp-verifier/    Codex verifier skill wrapper
<target>/.codex/agents/pasp-verifier.toml Codex read-only subagent config
<target>/.claude/agents/pasp-verifier.md Claude read-only subagent config
<target>/.claude/skills/pasp-dev         Claude project skill symlink
```

默认行为：

- `skills/` 默认软链接到源仓库 `skills/`，方便开发期间同步更新；
- `--copy` 可安装独立副本；
- `--source` 或 `PASP_SKILLS_SOURCE` 可指定源仓库；
- `--force` 用于覆盖旧安装；
- `CLAUDE_SKILLS_DIR` 只用于定位旧版 Claude 用户级入口，便于测试或清理 legacy user-scope entry。

当前设计取舍：

- Codex 通过目标项目下 `.codex/skills/pasp-dev` 识别；
- Claude 通过目标项目下 `.claude/skills/pasp-dev` 识别；
- Codex / Claude 的 verifier subagent 都指向同一个 canonical contract：`skills/subskills/pasp-verifier/skill.md`；
- 避免在平台 wrapper 中复制完整 verifier 规则。

---

## 12. 当前完成情况

### 12.1 已完成

- 搭建了自包含 `skills/` runtime 包。
- 建立了顶层 `SKILL.md` 路由入口。
- 建立了 `pasp-orchestrator` / `pasp-reference` / `pasp-verifier` 三个核心 subskill。
- 接入 7 个 workflow：L2-L8。
- 建立 L3 effective Hamiltonian 的 state-machine-first 机制。
- 建立 reference-before-write 规则。
- 建立 read-only verifier contract 和标准输出格式。
- 建立 Codex / Claude verifier subagent wrapper。
- 建立安装脚本，支持 symlink / copy / force / source。
- 建立 reference 知识库，已有 154 个 param 卡片、19 个 file 卡片、6 个 topic、5 个 module。
- 建立 L2 / L3 模板和 L3 辅助脚本。
- 建立 Trellis spec，记录目录结构、质量规则、workflow skill 设计规则。

### 12.2 基本可用

- 用户询问 workflow 下一步时，可以路由到对应 workflow。
- 用户询问字段 / 文件 / module 时，可以走 reference 查询。
- 用户请求生成或修改输入时，规则会要求先确认 workflow 阶段和 reference 支持。
- L3 workflow 已经能处理较复杂的 Path A / Path B、shared-basis、method-6、fitting、preflight、output validation 约束。
- Codex / Claude 可以通过安装脚本接入同一套 PASP skills。

### 12.3 仍需完善

- L2、L4、L5、L6、L7、L8 的 gate 深度还不如 L3，需要继续补充 state machine 或更细 stage contract。
- Reference 虽已有较多字段，但仍需要持续补全高风险字段、文件格式和条件依赖。
- Templates 需要更多 smoke-test 验证，避免模板被误认为正式科学默认值。
- 安装脚本需要继续在真实 Codex / Claude 测试目录中验证平台识别行为。
- `source-audit` 中发现的源码事实需要继续沉淀回 reference 或 workflow，而不是停留在临时调查结果。

---

## 13. 典型使用场景

### 场景 1：用户问“我有 POSCAR，怎么开始 PASP？”

路由策略：

1. 顶层识别为 workflow。
2. `pasp-orchestrator` 要求先确认目标 workflow / Model。
3. 若进入 L3，需要确认 Path A / Path B、磁性元素、cutoff、body order、SOC 等。
4. 如果只能生成草稿，必须标记为 draft，不能作为正式 input。

### 场景 2：用户问“`fig.maxk` 是什么意思？”

路由策略：

1. 顶层识别为 reference。
2. `pasp-reference` 查 `skills/knowledge/reference/params/fig.maxk.md`。
3. 只回答字段含义、用法和 caveat，不规划完整 workflow。

### 场景 3：用户让 agent 修改 `PASP.input`

路由策略：

1. 先判断当前 workflow 和 stage。
2. Workflow 说明当前阶段哪些项可调。
3. 每个实际写入字段必须 reference-before-write。
4. 如果准备成为 formal input，需要 preflight。

### 场景 4：用户目录很大，需要判断当前进度

路由策略：

1. 主 agent 保留最终判断。
2. 可以请求用户授权 verifier subagent 做 `directory-inventory`。
3. Verifier 只返回事实、路径和不确定项。
4. Inventory 不能替代 input preflight。

---

## 14. 关键工程原则

### 14.1 不把入口文件写成大手册

入口只做路由。长知识进入 `knowledge/workflows/` 或 `knowledge/reference/`。

### 14.2 不把 workflow 写成 reference

Workflow 说明“当前阶段要考虑什么”；reference 说明“具体字段怎么写”。

### 14.3 不把模板当默认答案

模板只是起点。正式输入需要用户确认和 reference 支持。

### 14.4 不把历史 run-notes 当当前事实

Run-notes 只说明过去发生过什么。当前用户目录必须从当前文件证据判断。

### 14.5 不让 subagent 做最终决策

Subagent 只做 bounded fact collection。最终路由、风险判断和用户答复由主 agent 完成。

### 14.6 安装层保持薄

Codex / Claude wrapper 只负责接入，不复制 PASP 规则。核心规则始终在 `skills/`。

---

## 15. 可以在 PPT 中强调的亮点

- **从经验驱动转向结构化知识驱动**：把讲义和 examples 中的知识拆成 workflow、reference、template、script。
- **降低误操作风险**：reference-before-write 和 formal input preflight 防止 agent 直接写错输入。
- **支持复杂 workflow 状态管理**：L3 已经具备 state machine、STOP gate、Path A / Path B、run directory contract。
- **跨平台共享规则**：Codex 和 Claude 通过 wrapper 接入同一份 canonical skills 包。
- **可扩展**：新 workflow 可以沿用 subskill + workflow doc + reference doc + verifier mode 的模式。
- **可验证**：verifier subagent 的输出要求 source path、uncertainty 和 pass/fail/blocked，减少黑箱判断。

---

## 16. 当前风险与下一步计划

### 16.1 风险

- Reference 仍可能有空白；空白处不能靠 agent 记忆补。
- 某些平台对 skill 发现路径敏感，安装脚本需要真实环境测试。
- L3 规则已经较严格，但其他 workflow 还需要类似程度的 gate 化。
- 用户可能把 subagent 授权误解为“可以提交任务”；文档中已经强调授权只读事实检查，但使用中仍需提醒。
- Templates 很方便，但容易被误用为科学默认设置。

### 16.2 下一步

- 对 L2、L4-L8 增加更明确的 stage gate 和 input/output checklist。
- 持续补全 reference，优先补高风险字段、block、文件格式、编号规则。
- 为常见端到端流程增加 smoke-test 目录和验证脚本。
- 继续测试 `install-pasp-skills.sh` 在 Codex / Claude 测试目录中的识别效果。
- 清理开发过程中产生的缓存和非 runtime 文件，保持部署包干净。
- 将更多经过验证的源码 / example 事实沉淀为 reference 卡片。

---

## 17. 给 PPT Agent 的生成建议

生成 PPT 时建议使用“问题 -> 设计 -> 当前成果 -> 下一步”的叙事：

1. 先讲 PASP agent 面临的复杂性：workflow 长、输入复杂、样例容易误导。
2. 再讲设计拆分：workflow 负责做什么，reference 负责怎么写，verifier 负责查事实。
3. 展示目录结构，突出 `skills/` 是 self-contained runtime package。
4. 展示 7 个已支持 workflow 和 reference 统计数字。
5. 单独用 2-3 页讲 L3，因为它最能体现状态机、STOP gate 和 safety guardrail。
6. 用一页讲安装脚本和 Codex / Claude 接入。
7. 最后讲完成情况和下一步。

建议 PPT 视觉元素：

- 一张三层架构图：`入口路由 -> workflow/reference -> verifier/templates/scripts`
- 一张目录树图：展示 `skills/` 核心结构
- 一张 L3 状态机简图：S0-S7 与 STOP gate
- 一张平台接入图：`skills/` 被 Codex / Claude wrapper 共同引用
- 一张完成情况表：已完成 / 基本可用 / 待完善

---

## 18. 可直接作为 PPT 页面的短版提纲

### 页 1：标题

PASP Skills 开发进展：从经验问答到可部署的 PASP Agent 知识系统

### 页 2：为什么做

- PASP workflow 长、输入复杂、参数依赖多
- 讲义 / example / 记忆难以直接用于可靠 agent
- 需要可路由、可查证、可部署的知识包

### 页 3：核心设计

- Workflow：做什么、下一步、当前阶段
- Reference：字段、文件、格式、默认值、编号规则
- Verifier：只读事实检查、preflight、validation

### 页 4：项目结构

展示 `skills/` 目录树，强调 self-contained runtime package。

### 页 5：Workflow 覆盖

L2-L8 共 7 个 workflow，L3 最完整。

### 页 6：Reference 覆盖

- 154 个 params
- 19 个 files
- 6 个 topics
- 5 个 modules

### 页 7：L3 深入建设

- state-machine-first
- Path A / Path B
- shared-basis confirmation
- input preflight
- output validation

### 页 8：安全约束

- reference-before-write
- formal input gate
- run directory isolation
- subagent read-only boundary

### 页 9：平台接入

- Codex：`.codex/skills/pasp-dev`
- Claude：`.claude/skills/pasp-dev`
- Subagent：`.codex/agents` / `.claude/agents`

### 页 10：当前完成情况

列出已完成、基本可用、仍需完善。

### 页 11：下一步

- 补齐其他 workflow gate
- 扩充 reference
- 端到端测试
- 平台安装验证

### 页 12：结论

PASP Skills 已经形成一个可部署、可扩展、具备安全边界的 PASP agent 知识系统雏形。
