# PASP Skills 包说明

这是一个**可直接复制部署**的 PASP skills 包。

它的目标是把 PASP 相关问答拆成两类：
- **workflow**：回答“我要做什么”“怎么开始”“下一步是什么”这类任务型问题
- **reference**：回答“某个字段/文件/参数是什么意思、怎么写”这类查询型问题

当前这套 skills 是**自包含**的：运行时只依赖 `skills/` 目录内部的内容，不依赖外部的讲义目录或 examples 目录。

---

## 1. 目录结构

```text
skills/
├── README.md
├── DEVELOPMENT_GUIDE.md
├── SKILL.md
├── subskills/
│   ├── pasp-orchestrator/
│   │   └── skill.md
│   ├── pasp-reference/
│   │   └── skill.md
│   ├── pasp-verifier/
│   │   └── skill.md
│   ├── workflow-l2-spin-models/
│   │   └── skill.md
│   ├── workflow-l3-effective-hamiltonian/
│   │   └── skill.md
│   ├── workflow-l4-monte-carlo/
│   │   └── skill.md
│   ├── workflow-l5-dynamics/
│   │   └── skill.md
│   ├── workflow-l6-ga-search/
│   │   └── skill.md
│   ├── workflow-l7-tight-binding/
│   │   └── skill.md
│   └── workflow-l8-spin-induced-polarization/
│       └── skill.md
└── knowledge/
    ├── workflows/
    │   ├── l2_find_J_path_sym.md
    │   ├── l2_find_J_path_sym_run_notes.md
    │   ├── l2_overview.md
    │   ├── l2_spin_lattice_interaction.md
    │   ├── l2_spin_lattice_interaction_state_machine.md
    │   ├── l2_spin_lattice_interaction_run_notes.md
    │   ├── l2_magnon.md
    │   ├── l2_magnon_state_machine.md
    │   ├── l2_magnon_run_notes.md
    │   ├── l3_effective_hamiltonian.md
    │   ├── l3_effective_hamiltonian_state_machine.md
    │   ├── l3_effective_hamiltonian_run_notes.md
    │   ├── l4_monte_carlo.md
    │   ├── l4_monte_carlo_state_machine.md
    │   ├── l4_monte_carlo_run_notes.md
    │   ├── l5_dynamics.md
    │   ├── l5_dynamics_state_machine.md
    │   ├── l5_dynamics_user_checklist.md
    │   ├── l5_dynamics_run_notes.md
    │   ├── l6_ga_search.md
    │   ├── l6_ga_search_state_machine.md
    │   ├── l6_ga_search_run_notes.md
    │   ├── l7_tight_binding.md
    │   ├── l7_tight_binding_state_machine.md
    │   ├── l7_tight_binding_run_notes.md
    │   ├── l8_spin_induced_polarization.md
    │   ├── l8_spin_induced_polarization_state_machine.md
    │   └── l8_spin_induced_polarization_run_notes.md
    ├── templates/
    │   ├── l2_find_J_path_sym/
    │   │   ├── README.md
    │   │   ├── PASP.input
    │   │   ├── cell.str
    │   │   └── unit_cell.str
    │   ├── l2_Spin_lattice_interaction/
    │   │   ├── README.md
    │   │   ├── PASP.input
    │   │   ├── MC.input
    │   │   ├── cell.str
    │   │   ├── unit_cell.str
    │   │   ├── spin_exchange.dat
    │   │   ├── seed.in
    │   │   └── run.sh
    │   ├── l2_magnon_FM/
    │   │   ├── README.md
    │   │   ├── PASP.input
    │   │   ├── cell.str
    │   │   ├── unit_cell.str
    │   │   ├── spin_exchange.dat
    │   │   ├── spin3.in
    │   │   └── run.sh
    │   ├── l2_magnon_spiral/
    │   │   ├── README.md
    │   │   ├── PASP.input
    │   │   ├── cell.str
    │   │   ├── unit_cell.str
    │   │   ├── spin_exchange.dat
    │   │   ├── spin3.in
    │   │   └── run.sh
    │   ├── l3_invariant/
    │   │   ├── README.md
    │   │   ├── PASP.input
    │   │   ├── cell.str
    │   │   └── unit_cell.str
    │   └── l3_fit/
    ├── scripts/
    │   └── l3_effective_hamiltonian/
    └── reference/
        ├── QUERY_GUIDE.md
        ├── STRUCTURE.md
        ├── topics/
        ├── files/
        ├── params/
        ├── modules/
        └── toc/
```

---

## 2. 整体架构

### `SKILL.md`
顶层入口 skill。

职责很简单：
- 识别用户是在问 workflow 还是 reference
- 把请求交给最小、最相关的子 skill

它本身不负责展开大量 PASP 知识。

### `subskills/pasp-orchestrator/skill.md`
任务分流层。

负责识别用户意图，并把任务型问题路由到对应 workflow：
- 交换路径与磁相互作用模型
- 有效哈密顿量建模与拟合
- 蒙特卡洛模拟
- 动力学模拟
- GA 全局结构搜索
- 紧束缚模型
- 自旋诱导极化

### `subskills/pasp-reference/skill.md`
参考查询层。

负责回答：
- 字段是什么意思
- 文件怎么用
- 某个 Model / 模块的作用是什么
- 某个主题通常怎么配置

它不负责完整 workflow 规划。

### `subskills/pasp-verifier/skill.md`
只读事实检查契约。

它不是用户任务入口，而是给主 agent 在获得授权后委派 bounded fact collection 时使用：
- reference-check
- input-preflight
- directory-inventory
- output-validation
- structure-analysis
- log-summary
- template-compare
- source-audit

它只能汇报事实、来源路径、不确定项和 pass / fail / blocked 结论；不能决定 workflow 路由、不能替用户选择物理参数、不能修改文件、不能提升正式 input、不能准备或提交任务，也不能生成最终用户答复。

### `subskills/workflow-*/skill.md`
任务型 workflow 子 skills。

这些子 skills 只负责各自的流程指导，例如：
- 当前处于哪一步
- 下一步需要准备什么
- 哪些问题应该转给 reference
- 当用户、Claude 或 Codex 正在修改输入文件时，识别当前阶段哪些设置可以调整
- 在需要时提示哪些项必须先查 reference 再改

### `knowledge/workflows/`
workflow 知识文档。

每个 workflow 子 skill 都对应一份知识文档，用来描述：
- 目标
- 适用问题
- 输入前提
- 典型阶段
- 当前步骤常见 reference 入口
- 当前阶段可调整项
- 每项控制什么
- 什么时候不要直接改、先查 reference

### `knowledge/templates/`
完整参考输入模板。

这里放的是可直接抄起点的最小完整输入骨架，例如：
- `l2_find_J_path_sym/PASP.input`
- `l3_invariant/PASP.input`
- 配套的 `cell.str` / `unit_cell.str` 占位骨架

它们的作用不是提供通用 reference 定义，而是帮助用户在服务器上快速起第一版可运行输入。

### `knowledge/scripts/`
辅助数据处理脚本模板。

这里放的是从 examples 提炼出来、但不直接依赖外部 examples 目录的脚本模板，例如：
- `l3_effective_hamiltonian/postprocess.sh`
- `l3_effective_hamiltonian/createINCAR.sh`
- `l3_effective_hamiltonian/get_ene.sh`
- `l3_effective_hamiltonian/convert_data.py`
- `l3_effective_hamiltonian/prepare_path_b_inputs.py`

这些脚本主要用于衔接 PASP 与外部 DFT 数据整理流程，通常需要按用户自己的目录结构和集群环境修改。

### `knowledge/reference/`
reference 知识库。

这是运行时唯一使用的 PASP 查询资料来源。

---

## 3. 当前已支持的 7 个 workflow

当前已接入的 workflow 如下：

1. **分析交换路径并构建磁相互作用模型**
2. **构建并拟合有效哈密顿量**
3. **蒙特卡洛模拟**
4. **动力学模拟**
5. **GA全局结构搜索**
6. **紧束缚模型**
7. **自旋诱导极化**

对应的 workflow 知识文件位于：
- `knowledge/workflows/l2_find_J_path_sym.md`：`find_J_path_sym` 子流程
- `knowledge/workflows/l2_find_J_path_sym_run_notes.md`：find_J 历史实跑观察
- `knowledge/workflows/l2_overview.md`：spin-model 子流程的关系总览
- `knowledge/workflows/l2_spin_lattice_interaction.md`：`Spin_lattice_interaction` PTMC / CG IO 骨架
- `knowledge/workflows/l2_spin_lattice_interaction_state_machine.md`：`Spin_lattice_interaction` STOP gate
- `knowledge/workflows/l2_spin_lattice_interaction_run_notes.md`：`Spin_lattice_interaction` 历史实跑观察
- `knowledge/workflows/l2_magnon.md`：`magnon` IO 骨架
- `knowledge/workflows/l2_magnon_state_machine.md`：`magnon` STOP gate
- `knowledge/workflows/l2_magnon_run_notes.md`：`magnon` 历史实跑观察
- `knowledge/workflows/l3_effective_hamiltonian.md`
- `knowledge/workflows/l3_effective_hamiltonian_state_machine.md`：有效哈密顿量运行门禁与 STOP 状态机，必须先于长 workflow 使用
- `knowledge/workflows/l3_effective_hamiltonian_run_notes.md`：有效哈密顿量历史实跑观察，不是当前目录事实
- `knowledge/workflows/l4_monte_carlo.md`
- `knowledge/workflows/l4_monte_carlo_state_machine.md`：MC / PTMC / CG 运行门禁与 STOP 状态机，必须先于长 workflow 使用
- `knowledge/workflows/l4_monte_carlo_run_notes.md`：蒙特卡洛 examples 历史观察、输出家族和 reference gap 线索，不是当前目录事实
- `knowledge/workflows/l5_dynamics.md`
- `knowledge/workflows/l5_dynamics_state_machine.md`：dynamics / generic new-material / Cr2O3 SLD / BaTiO3 electric hysteresis 运行门禁与 STOP 状态机，必须先于长 workflow 使用
- `knowledge/workflows/l5_dynamics_user_checklist.md`：dynamics 用户侧快速 checklist，覆盖 generic new-material、Cr2O3 和 BaTiO3 分支，不替代状态机和 reference-before-write 规则
- `knowledge/workflows/l5_dynamics_run_notes.md`：Cr2O3 / BaTiO3 dynamics examples 历史观察、输出家族和 reference gap 线索，不是当前目录事实
- `knowledge/workflows/l6_ga_search.md`
- `knowledge/workflows/l6_ga_search_state_machine.md`：GA / random-spacegroup / perturbation / magnetic / restart / constrained search 运行门禁与 STOP 状态机，必须先于长 workflow 使用
- `knowledge/workflows/l6_ga_search_run_notes.md`：GA search examples、historical output 和 source-audit 观察，不是当前目录事实
- `knowledge/workflows/l7_tight_binding.md`
- `knowledge/workflows/l7_tight_binding_state_machine.md`：custom TB / SKTB / additional-H / GSDTB / CLS 运行门禁与 STOP 状态机，必须先于长 workflow 使用
- `knowledge/workflows/l7_tight_binding_run_notes.md`：tight-binding examples、historical output 和 source-audit 观察，不是当前目录事实
- `knowledge/workflows/l8_spin_induced_polarization.md`
- `knowledge/workflows/l8_spin_induced_polarization_state_machine.md`：pure electronic KNB / gKNB 与 spin-lattice ion-strain contribution 运行门禁与 STOP 状态机，必须先于长 workflow 使用
- `knowledge/workflows/l8_spin_induced_polarization_run_notes.md`：spin-induced polarization examples、historical output 和 source-audit 观察，不是当前目录事实

说明：
- 基础输入文件、通用概念和入门说明被视为 `reference / onboarding` 层，不单独做成 workflow
- tight-binding 已有 workflow、state machine、run notes 和 verifier 门禁；当前一类 graph-allocation 问题仍记录为 PASP / latt 源码侧待修复限制，不能把失败 run 当作可交付结果
- spin-induced polarization 已覆盖 pure electronic KNB / gKNB 和 spin-lattice ion / strain contribution；其中 `spin_lat.spin_int_stress T` 的 `read_spin_stress` 路径在当前已验证 runtime 中只支持 1 个 MPI task，多 task 运行必须 blocked / failed，除非有源码修复证据

---

## 4. Reference 知识库的组织方式

`knowledge/reference/` 目前按下面几类组织：

### `topics/`
主题级入口。

适合回答：
- `PASP.input` 怎么组织
- `MC.input` 常用项有哪些
- `MD.input` 一般怎么配置

### `files/`
文件级说明。

适合回答：
- `cell.str` 是什么
- `unit_cell.str` 和 `cell.str` 区别是什么
- `J_best.dat` 是做什么的

### `params/`
单字段卡片。

适合回答：
- `Model` 是什么意思
- 某个字段默认值是什么

说明：当前已按第 3 章输入/输出文档批量补齐参数卡片，并由 `params/INDEX.md` 维护入口；若后续官网新增字段或用户问题未命中，再回退到相关 `topics/` 或 `modules/`。

### `modules/`
模块/方法族说明。

适合回答：
- `TB` 是什么
- `GA` 有什么作用
- `knb` 相关设置通常看哪些项

### `toc/`
来源定位和回溯信息。

主要用于：
- 查来源章节
- 做出处定位
- 维护和回溯

一般不是第一优先查询入口。

### 辅助说明文件
- `knowledge/reference/QUERY_GUIDE.md`
- `knowledge/reference/STRUCTURE.md`

这两个文件定义了 reference 层的查询逻辑和目录角色。

---

## 5. 路由规则

### 什么问题走 workflow
如果用户在问：
- 我想做什么计算
- 怎么开始
- 下一步是什么
- 某个任务完整流程怎么走

那么优先走 workflow。

例如：
- “我想从结构出发分析交换路径，怎么开始？”
- “我已经有 DFT 数据了，怎么拟合 effective Hamiltonian？”
- “我想做 MC 模拟，下一步需要哪些输入？”

### 什么问题走 reference
如果用户在问：
- 某个字段是什么意思
- 某个文件怎么用
- 某个参数怎么写
- 某个模块有什么作用

那么优先走 reference。

例如：
- “`Model` 是什么意思？”
- “`cell.str` 怎么写？”
- “`PT.M` 是什么？”
- “`GA.population_size` 是做什么的？”

### 混合问题怎么处理
如果用户同时在问任务和参数：
- 先进入 workflow，判断当前阶段
- 再只补当前步骤所需的 reference 信息

例如：
- “我想做 TB，`block Hop_Parameters` 应该怎么写？”

这类问题应先确认属于紧束缚 workflow，再补 `Hop_Parameters` 的 reference 说明。

---

## 6. 运行时依赖边界

这套 skills 在运行时**只依赖以下目录**：
- `skills/knowledge/workflows/`
- `skills/knowledge/templates/`
- `skills/knowledge/scripts/`
- `skills/knowledge/reference/`

也就是说：
- 不依赖 `pasp_slides_md/`
- 不依赖 `pasp_examples/`
- 不依赖 `pasp_readme/` 外部路径

讲义和 examples 可以作为构建 skills 时的整理素材，但不应作为部署后的运行依赖。

---

## 7. 部署到服务器时的建议

如果你要把这套 skills 拷到服务器：

### 推荐做法
进入目标项目目录后，使用安装脚本把 PASP skills 包、Codex 集成和 Claude 集成都装到当前目录。当前默认使用 symlink 指向本仓库的 `skills/`，方便开发期间同步更新：

```bash
cd /path/to/target-project
/path/to/PASPskills/scripts/install-pasp-skills.sh
```

也可以把脚本复制到目标目录后直接运行：

```bash
cp /path/to/PASPskills/scripts/install-pasp-skills.sh /path/to/target-project/
cd /path/to/target-project
./install-pasp-skills.sh
```

脚本会优先从自身相对路径识别源仓库；如果脚本是单独复制过去的，建议用 `--source /path/to/PASPskills` 或环境变量 `PASP_SKILLS_SOURCE=/path/to/PASPskills` 指定源仓库。最后的默认 fallback 是当前工作目录 `./`。

它会安装：
- `/path/to/target-project/skills/`：PASP runtime skills package
- `/path/to/target-project/.codex/skills/pasp-helper`：Codex 项目级入口 skill，软链接到工作目录的 `skills/`
- `/path/to/target-project/.codex/skills/pasp-verifier/SKILL.md`：Codex verifier skill 包装器
- `/path/to/target-project/.codex/agents/pasp-verifier.toml`：read-only Codex verifier subagent 配置
- `/path/to/target-project/.claude/agents/pasp-verifier.md`：read-only Claude verifier subagent 配置
- `/path/to/target-project/.claude/skills/pasp-helper`：Claude 项目级入口 skill，软链接到工作目录的 `skills/`

如果目标目录已有旧版本，使用：

```bash
/path/to/PASPskills/scripts/install-pasp-skills.sh --force
```

如果希望安装一份独立副本，而不是 symlink，使用：

```bash
/path/to/PASPskills/scripts/install-pasp-skills.sh --copy
```

如果从目标目录里的脚本安装，但源仓库不在当前工作目录，使用：

```bash
./install-pasp-skills.sh --source /path/to/PASPskills
```

如果不使用 Codex / Claude 集成，也可以手动复制整个 `skills/` 目录，但这样不会自动安装 `.codex/skills/`、`.codex/agents/`、`.claude/agents/` 或 `.claude/skills/`。

安装后的分层含义：
- `skills/subskills/pasp-verifier/skill.md` 是 PASP 包内部的 canonical verifier 契约。
- `.codex/skills/pasp-helper` 是 Codex 项目级入口，指向工作目录 `skills/`。
- `.codex/skills/pasp-verifier/SKILL.md` 和 `.codex/agents/pasp-verifier.toml` 是 Codex 平台包装层。
- `.claude/skills/pasp-helper` 是 Claude 项目级入口，指向工作目录 `skills/`。
- `.claude/agents/pasp-verifier.md` 是 Claude 平台包装层。

平台入口 / 包装层只负责暴露或导向 `skills/subskills/pasp-verifier/skill.md`，不要手工把 verifier 规则复制成多份长期维护。

旧版安装可能留下 `$HOME/.claude/skills/pasp-dev`、`$HOME/.claude/skills/paspskills` 或 `$HOME/.claude/skills/pasp-helper` 这类 Claude 用户级入口；当前安装脚本只把它们作为 legacy user-scope entry 检查、警告，或在 `--force` 时移除。新的 Claude 入口安装到目标项目的 `.claude/skills/pasp-helper`。

### 注意事项
1. **保留目录层级不变**
   - `subskills/` 和 `knowledge/` 的相对路径关系不要改
2. **不要随意改文件名和目录名**
   - 当前 skill 文件里使用了相对路径引用
3. **只把顶层 `SKILL.md` 当作注册入口**
   - `subskills/*/skill.md` 是运行时要读取的本地指令文件，不是假定已注册的独立 skill
   - Claude 等环境里不要调用 `pasp-helper:pasp-orchestrator` 这类冒号式嵌套 skill 名；应由 `pasp-helper` 入口读取对应 `subskills/` 文件继续执行
4. **路径名建议保持英文**
   - 更适合服务器、脚本、终端和不同环境下的兼容性
5. **内容说明可以使用中文**
   - 这套 skills 当前就是中文说明为主
   - 对中文使用者维护更自然

---

## 8. 关于中文内容是否可用

可以。

当前这套 skills 的长 workflow 文档和说明文本可以使用中文；`SKILL.md` 与 `subskills/*/skill.md` 这类路由 / 薄入口文件使用英文，以保持 intent routing、STOP gate 和 delegation 规则稳定。

推荐约定是：
- **内容用中文**
- **路径名、目录名、文件名用英文**
- **PASP 参数名、文件名、Model 名保留原文英文**

这样兼顾：
- 维护方便
- 阅读自然
- 路径稳定

---

## 9. 后续维护方式

### 新增一个 workflow 时
通常需要同时修改两处：

1. 新增一个 workflow 子 skill
   - 放到 `subskills/`
2. 新增一份对应的 workflow 知识文档
   - 放到 `knowledge/workflows/`

如果希望入口能识别它，还需要同步更新：
- `SKILL.md`
- `subskills/pasp-orchestrator/skill.md`

### 补充 reference 时
按照内容类型补到：
- `knowledge/reference/topics/`
- `knowledge/reference/files/`
- `knowledge/reference/params/`
- `knowledge/reference/modules/`

如果是新的查询组织规则或来源映射，再考虑更新：
- `knowledge/reference/QUERY_GUIDE.md`
- `knowledge/reference/STRUCTURE.md`

---

## 10. 开发原则文档

后续继续补全已有 workflow 或新增 workflow 时，请先阅读：

- `DEVELOPMENT_GUIDE.md`

它约束了：
- workflow / reference 的分工边界
- 模板与脚本是否应该纳入 `skills/knowledge/`
- workflow 中“当前阶段可调整项 / 每项控制什么 / 何时先查 reference”的写法
- Claude / Codex 在帮助修改输入文件时应遵守的调参护栏

---

## 11. 如何快速检查 README 是否仍然有效

每次修改 skills 后，可以快速核对下面几项：

1. `skills/` 顶层是否仍包含：
   - `SKILL.md`
   - `subskills/`
   - `knowledge/`
2. `subskills/` 下是否仍包含：
   - `pasp-orchestrator`
   - `pasp-reference`
   - `pasp-verifier`
   - 7 个 workflow 子 skill
3. `knowledge/workflows/` 下的 workflow 文件数是否和 README 中列出的清单一致
4. `knowledge/reference/` 下是否仍包含：
   - `topics/`
   - `files/`
   - `params/`
   - `modules/`
   - `toc/`
   - `QUERY_GUIDE.md`
   - `STRUCTURE.md`
5. README 中写到的运行时依赖是否仍然只指向 `skills/knowledge/`

如果这些条件都成立，说明 README 和当前目录结构仍然一致。
