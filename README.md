# PASP Skills 安装与使用

[![Release](https://img.shields.io/github/v/release/cy0752/PASPskills?sort=semver&cacheSeconds=3600)](https://github.com/cy0752/PASPskills/releases)

这个仓库提供一套面向 PASP 计算流程的 agent skills，用于让 Codex 或 Claude 在目标项目中回答 PASP workflow 和 reference 问题。

它主要解决两类问题：

- **workflow**：我要做某类 PASP 计算，应该从哪里开始、当前处于哪一步、下一步要准备什么。
- **reference**：某个 `PASP.input` 字段、输入文件、输出文件、模块或参数是什么意思，应该按什么格式理解。

运行时知识集中在 `skills/` 目录内。安装后，Codex 和 Claude 的项目级入口会指向同一套 `skills/`，避免不同平台各自复制一份知识后发生漂移。

## 当前范围

当前包主要包含：

- `skills/`：PASP runtime skills、workflow 知识、reference 知识、模板和辅助脚本。
- `scripts/install-pasp-skills.sh`：把 PASP skills 安装到目标项目，并创建 Codex / Claude 项目级入口。

共享给普通使用者时，通常只需要提供 `skills/` 和 `scripts/`；开发期讲义、examples、源码检查记录和任务管理文件不是运行时依赖。

当前已接入 7 类 workflow：交换路径与磁相互作用模型、有效哈密顿量、蒙特卡洛、动力学、GA 全局结构搜索、紧束缚模型、自旋诱导极化。部分 workflow 仍保留运行时门禁和已知限制，例如：

- 紧束缚模型的一类 graph-allocation 路径在当前已验证 PASP / latt 版本中仍可能触发 `Error, graph already allocated.`，需等待源码侧修复后再重跑确认。
- 自旋诱导极化的 spin-lattice ion / strain 分支若启用 `spin_lat.spin_int_stress T`，当前已验证 `read_spin_stress` 路径只支持 1 个 MPI task；多 task 运行会被 verifier 判为 blocked / failed，除非有源码已修复并验证的证据。

## 获取 PASPskills

安装前，先把本仓库放到本机任意稳定位置。常见方式有两种：

```bash
git clone https://github.com/cy0752/PASPskills.git PASPskills
```

或者在 GitHub 页面下载源码 zip，解压后使用其中包含 `scripts/install-pasp-skills.sh` 的目录：

```bash
unzip <downloaded-source>.zip
```

后续命令里的 `/path/to/PASPskills` 请替换成你本机的实际目录。

## 版本

当前 `main` 分支的 runtime 包版本是 **0.1.14**，记录在根目录 `VERSION` 和 `skills/VERSION`。本次同步包含 L2 四态法原生交付与几何检查、L3 输入准备、拟合交接和模型完整性检查，以及相关 reference 和 workflow 修正。

页面顶部 release badge 和 [Releases](https://github.com/cy0752/PASPskills/releases) 显示单独发布的 GitHub Release；它可能落后于 `main`。查看当前分支的版本请读取 `VERSION`。

安装后，目标项目中的 runtime skills 包会包含 `skills/VERSION`。用户可以在目标项目中查看当前安装版本：

```bash
cat skills/VERSION
```

需要更新时，先更新源仓库，再重新安装目标项目，见下方“更新已有安装”。

## 安装前提

- Unix-like shell 环境，且可以运行 `bash`。
- 安装入口需要文件系统支持软链接。默认模式还会把 runtime 包链接到源仓库；希望目标项目脱离源仓库路径独立使用时，请加 `--copy`，该模式的项目内入口仍使用软链接。
- 只有通过 zip 下载源码时才需要 `unzip`。
- 只阅读 workflow/reference 不需要安装 Python 依赖。运行辅助脚本建议使用 Python 3.11 或更新版本；L2 原胞生成和原生四态法检查还需要 `numpy`、`spglib`，可在自己的 Python 环境中安装：

```bash
python3 -m pip install numpy spglib
```

安装脚本只部署 skills 和平台入口，不会安装 Python 包、PASP、VASP、MPI 或集群调度环境。这些计算工具需根据所用 workflow 单独准备。

## 快速安装

在目标项目中运行安装脚本：

```bash
/path/to/PASPskills/scripts/install-pasp-skills.sh
```

源仓库和目标项目应使用不同目录；不要在 PASPskills 源仓库本身运行覆盖安装。脚本会拒绝覆盖包含源 skills 的目标目录。

如果当前 shell 不在目标项目目录，可以把目标目录作为最后一个参数：

```bash
/path/to/PASPskills/scripts/install-pasp-skills.sh /path/to/target-project
```

默认安装方式是把本仓库的 `skills/` 软链接到目标项目的 `skills/`。这适合持续维护：更新本仓库后，目标项目会直接看到最新 skills 内容。

如果你是从 zip 解压后安装，或之后可能移动/删除 `PASPskills/` 目录，建议使用复制安装：

```bash
/path/to/PASPskills/scripts/install-pasp-skills.sh --copy /path/to/target-project
```

## 更新已有安装

通过 Git 获取的源仓库，先更新到最新 `main`：

```bash
git -C /path/to/PASPskills pull --ff-only
```

然后重新安装，更新 skills 与 Codex / Claude 入口。沿用默认软链接模式：

```bash
/path/to/PASPskills/scripts/install-pasp-skills.sh --force /path/to/target-project
```

沿用复制模式时必须保留 `--copy`，否则会切换为依赖源仓库的软链接模式：

```bash
/path/to/PASPskills/scripts/install-pasp-skills.sh --force --copy /path/to/target-project
cat /path/to/target-project/skills/VERSION
```

`--force` 会替换目标项目已有的 PASP skills 与安装入口；先备份自行修改过的目标 `skills/`。通过 zip 获取的用户应下载并解压新版，再从新目录运行上述重新安装命令。

升级旧版安装时也应重新运行脚本，以创建当前 Codex 使用的 `.agents/skills/` 入口；仅更新软链接源仓库不会自动补建入口。安装后如 Codex 尚未显示 skill，请重新启动 Codex。

## 安装选项

```bash
scripts/install-pasp-skills.sh [--force] [--copy] [--source <PASPskills-repo-or-skills-dir>] [target-project-dir]
```

常用选项：

- `--force`：覆盖目标项目中已有的 PASP 安装路径；同时清理 `.agents/skills/`、`.codex/skills/`、`.claude/skills/` 中旧的 `pasp-dev` / `paspskills` 入口，以及旧版 Claude 用户级 PASP 入口。不会清理其他名称的 skills。
- `--copy`：把 `skills/` 复制进目标项目，而不是创建软链接。适合需要冻结当前版本、或目标项目不能依赖源仓库路径的场景。
- `--source <path>`：显式指定 PASPskills 仓库目录，或直接指定其中的 `skills/` 目录。
- `PASP_SKILLS_SOURCE=/path/to/PASPskills`：不想在命令里写 `--source` 时，可以用环境变量指定来源。
- `[target-project-dir]`：可选目标项目目录；省略时安装到当前工作目录。

来源路径解析顺序是：

1. `--source` 参数
2. `PASP_SKILLS_SOURCE` 环境变量
3. 相对安装脚本的位置查找本仓库
4. 当前工作目录 `./`

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
<target>/.agents/skills/pasp-helper      Codex project skill symlink
<target>/.agents/skills/pasp-verifier/    Codex verifier skill wrapper
<target>/.codex/skills/pasp-helper       Compatibility alias
<target>/.codex/skills/pasp-verifier     Compatibility alias
<target>/.codex/agents/pasp-verifier.toml Read-only Codex agent config
<target>/.claude/skills/pasp-helper      Claude project skill symlink
<target>/.claude/agents/pasp-verifier.md  Read-only Claude subagent config
```

其中 `pasp-helper` 是用户主要入口；`pasp-verifier` 是只读事实检查契约，供主 agent 在需要检查参考资料、目录、输入文件、输出文件或日志时使用。

## 平台入口

安装到某个项目后，在该项目中打开 Codex 或 Claude。两个平台使用同一套 `skills/` 知识，入口路径不同：

- Codex：`.agents/skills/pasp-helper` 和 `.agents/skills/pasp-verifier`。当前 Codex 从项目的 `.agents/skills/` 发现 skills，并支持软链接，参见 [OpenAI 官方 skills 文档](https://developers.openai.com/codex/skills/)。保留 `.codex/skills/` 兼容入口和 `.codex/agents/pasp-verifier.toml` agent 配置；agent 的注册方式取决于所用 Codex 版本，不能仅凭该配置文件存在就判断 agent 已注册。
- Claude：`.claude/skills/pasp-helper`，只读 verifier agent 配置在 `.claude/agents/pasp-verifier.md`。

如果平台环境不会自动触发项目 skill，可以在提示词里明确要求读取本项目的 `skills/SKILL.md` 作为 PASP 入口。

## 使用方式

可以直接问任务型问题：

```text
使用 pasp-helper。我想从 POSCAR 开始做 PASP 的交换路径分析，下一步应该准备什么？
```

也可以问参考型问题：

```text
使用 pasp-helper。PASP.input 里的 Model 字段有哪些常见取值？它们分别对应什么 workflow？
```

如果你正在让 agent 修改或生成输入文件，推荐明确要求它先查 reference：

```text
请帮我检查这个 PASP.input 草稿。修改任何字段前，先用本项目的 PASP reference 确认字段语义和格式。
```

如果任务需要检查当前目录、输入文件、输出文件或运行日志，可以在提示词里写“可以使用subagent”。

## 典型提示词

Workflow 类：

```text
我现在有一些结构文件和初始 PASP.input，想做 Monte Carlo 模拟。帮我判断已经具备哪些输入、还缺哪些文件或参数，以及下一步应该先补什么。可以使用subagent。
```

```text
这个目录里有一批 OUTCAR/OSZICAR 和 POSCAR，我想构建 effective Hamiltonian。可以使用subagent。
```

```text
解释 spin_exchange.dat 的格式和它在 magnon workflow 里的作用。需要时可以使用subagent。
```

Reference 类：

```text
解释 MC.input 里 PT.low_temp、PT.high_temp、PT.Tmesh 的含义、关系和常见风险。需要时可以使用subagent。
```

```text
说明 cell.str 和 unit_cell.str 分别描述什么；从 POSCAR 准备它们时需要注意哪些编号和坐标约定？需要时可以使用subagent。
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

默认软链接安装要求源仓库路径保持存在。如果移动或删除 PASPskills 仓库，目标项目的 `skills/` 以及指向它的 Codex / Claude 入口可能失效。`--copy` 安装的 runtime 包和项目内入口不依赖源仓库路径。

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
