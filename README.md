# PASP Skills 安装与使用

这个仓库提供一套面向 PASP 计算流程的 agent skills，用于让 Codex 或 Claude 在目标项目中回答 PASP workflow 和 reference 问题。

它主要解决两类问题：

- **workflow**：我要做某类 PASP 计算，应该从哪里开始、当前处于哪一步、下一步要准备什么。
- **reference**：某个 `PASP.input` 字段、输入文件、输出文件、模块或参数是什么意思，应该按什么格式理解。

运行时知识集中在 `skills/` 目录内。安装后，Codex 和 Claude 的项目级入口会指向同一套 `skills/`，避免不同平台各自复制一份知识后发生漂移。

## 快速安装

在目标项目中运行安装脚本：

```bash
/path/to/PASPskills/scripts/install-pasp-skills.sh
```

如果当前 shell 不在目标项目目录，可以把目标目录作为最后一个参数：

```bash
/path/to/PASPskills/scripts/install-pasp-skills.sh /path/to/target-project
```

默认安装方式是把本仓库的 `skills/` 软链接到目标项目的 `skills/`。这适合持续维护：更新本仓库后，目标项目会直接看到最新 skills 内容。

## 安装选项

```bash
scripts/install-pasp-skills.sh [--force] [--copy] [--source <PASPskills-repo-or-skills-dir>] [target-project-dir]
```

常用选项：

- `--force`：覆盖目标项目中已有的安装路径；同时会清理旧版 `.agents/skills/pasp-*` 和旧版 Claude 用户级 `pasp-dev` 入口。
- `--copy`：把 `skills/` 复制进目标项目，而不是创建软链接。适合需要冻结当前版本、或目标项目不能依赖源仓库路径的场景。
- `--source <path>`：显式指定 PASPskills 仓库目录，或直接指定其中的 `skills/` 目录。
- `PASP_SKILLS_SOURCE=/path/to/PASPskills`：不想在命令里写 `--source` 时，可以用环境变量指定来源。
- `[target-project-dir]`：可选目标项目目录；省略时安装到当前工作目录。

来源路径解析顺序是：

1. `--source` 参数
2. `PASP_SKILLS_SOURCE` 环境变量
3. 相对安装脚本的位置查找本仓库
4. 安装脚本内置的源路径兜底

示例：

```bash
# 安装到当前目录，默认软链接
/path/to/PASPskills/scripts/install-pasp-skills.sh

# 安装到指定项目
/path/to/PASPskills/scripts/install-pasp-skills.sh /path/to/project

# 覆盖已有安装
/path/to/PASPskills/scripts/install-pasp-skills.sh --force /path/to/project

# 复制 skills，而不是软链接
/path/to/PASPskills/scripts/install-pasp-skills.sh --copy /path/to/project

# 显式指定来源仓库
/path/to/PASPskills/scripts/install-pasp-skills.sh --source /path/to/PASPskills /path/to/project

# 用环境变量指定来源
PASP_SKILLS_SOURCE=/path/to/PASPskills /path/to/PASPskills/scripts/install-pasp-skills.sh /path/to/project
```

## 安装内容

安装脚本会在目标项目中创建这些入口：

```text
<target>/skills/                          PASP runtime skills package
<target>/.codex/skills/pasp-dev           Codex project skill symlink
<target>/.codex/skills/pasp-verifier/     Codex verifier skill wrapper
<target>/.codex/agents/pasp-verifier.toml Read-only Codex agent config
<target>/.claude/skills/pasp-dev          Claude project skill symlink
<target>/.claude/agents/pasp-verifier.md  Read-only Claude subagent config
```

其中 `pasp-dev` 是用户主要入口；`pasp-verifier` 是只读事实检查契约，供主 agent 在需要检查参考资料、目录、输入文件、输出文件或日志时使用。

## 平台入口

安装到某个项目后，在该项目中打开 Codex 或 Claude。两个平台使用同一套 `skills/` 知识，入口路径不同：

- Codex：`.codex/skills/pasp-dev`，只读 verifier agent 配置在 `.codex/agents/pasp-verifier.toml`。
- Claude：`.claude/skills/pasp-dev`，只读 verifier agent 配置在 `.claude/agents/pasp-verifier.md`。

如果平台环境不会自动触发项目 skill，可以在提示词里明确要求读取本项目的 `skills/SKILL.md` 作为 PASP 入口。

## 使用方式

可以直接问任务型问题：

```text
使用 pasp-dev。我想从 POSCAR 开始做 PASP 的交换路径分析，下一步应该准备什么？
```

也可以问参考型问题：

```text
使用 pasp-dev。PASP.input 里的 Model 字段有哪些常见取值？它们分别对应什么 workflow？
```

如果你正在让 agent 修改或生成输入文件，推荐明确要求它先查 reference：

```text
请帮我检查这个 PASP.input 草稿。修改任何字段前，先用本项目的 PASP reference 确认字段语义和格式。
```

## 典型提示词

Workflow 类：

```text
我现在有 unit_cell.str、cell.str 和一个初始 PASP.input，想做 Monte Carlo 温度扫描。请判断当前阶段、可调整项、必须先确认的 reference 字段，以及下一步检查清单。
```

```text
这个目录里有一批 OUTCAR/OSZICAR 和 POSCAR。我想做 effective Hamiltonian 拟合，请先判断这是哪个入口路径，不要直接生成正式输入文件。
```

```text
解释 spin_exchange.dat 的格式和它在 magnon workflow 里的作用。
```

Reference 类：

```text
解释 MC.input 里 PT.low_temp、PT.high_temp、PT.Tmesh 的含义、关系和常见风险。
```

```text
cell.str 和 unit_cell.str 分别描述什么？从 POSCAR 准备它们时需要注意哪些编号和坐标约定？
```

## 运行时边界

PASP skills 运行时只应依赖目标项目里的：

- `skills/knowledge/workflows/`
- `skills/knowledge/reference/`
- `skills/knowledge/templates/`
- `skills/knowledge/scripts/`
- 用户当前工作目录中的输入、输出和日志

不要要求运行时 agent 读取本仓库之外的讲义目录、历史 examples 或 PASP 源码才能回答用户问题。开发者可以用外部资料校准知识，但稳定规则必须整理回 `skills/knowledge/` 后再作为运行时依据。

## 路径稳定性

默认软链接安装要求源仓库路径保持存在。如果移动或删除 PASPskills 仓库，目标项目中的 `skills/`、`.codex/skills/pasp-dev` 和 `.claude/skills/pasp-dev` 可能失效。

需要长期归档或跨机器使用时，优先使用：

```bash
/path/to/PASPskills/scripts/install-pasp-skills.sh --copy /path/to/project
```

如果只是源仓库位置变了，可以重新安装：

```bash
/new/path/to/PASPskills/scripts/install-pasp-skills.sh --force --source /new/path/to/PASPskills /path/to/project
```

## 继续阅读

- [skills/README.md](skills/README.md)：PASP skills 包架构、workflow/reference 分工、目录结构和当前支持范围。
- [skills/DEVELOPMENT_GUIDE.md](skills/DEVELOPMENT_GUIDE.md)：继续开发、维护和扩展 PASP skills 时必须遵守的原则。
