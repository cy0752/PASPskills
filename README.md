# PASP Skills 安装与使用

[![Release](https://img.shields.io/github/v/release/cy0752/PASPskills?sort=semver&cacheSeconds=3600)](https://github.com/cy0752/PASPskills/releases)

这套 skills 帮助 Codex 和 Claude 理解 PASP 计算流程、查询参数与文件格式，并检查输入、输出和日志。

当前版本为 **0.1.15**。安装后的完整内容位于项目的
`.agents/skills/pasp-helper/`，Claude 共用这份内容。新安装不会在项目根目录创建
`skills/`，也不会创建旧的 `.codex/skills/` 入口。

## 获取源码

```bash
git clone https://github.com/cy0752/PASPskills.git PASPskills
```

也可以从 [Releases](https://github.com/cy0752/PASPskills/releases) 下载源码压缩包并解压。
下面的 `/path/to/PASPskills` 指包含 `scripts/install-pasp-skills.sh` 的源码目录；
`/path/to/target-project` 指你实际做计算的项目目录。

源码仓库保留 `skills/` 作为维护与发布目录；安装到用户项目时会使用下面的隐藏目录布局。

## 安装

```bash
/path/to/PASPskills/scripts/install-pasp-skills.sh /path/to/target-project
```

省略目标路径时安装到当前目录。默认复制完整内容，安装完成后可以移动或删除源码目录。
项目内 Claude 入口使用相对软链接，因此文件系统需要支持软链接。

```text
target-project/
├── .agents/skills/
│   ├── pasp-helper/
│   │   ├── SKILL.md
│   │   ├── VERSION
│   │   ├── subskills/
│   │   └── knowledge/
│   └── pasp-verifier/SKILL.md
├── .codex/agents/pasp-verifier.toml
└── .claude/
    ├── skills/pasp-helper -> ../../.agents/skills/pasp-helper
    └── agents/pasp-verifier.md
```

Codex 从 `.agents/skills/` 发现项目技能，参见
[OpenAI 官方文档](https://developers.openai.com/codex/skills/)。Claude 的入口指向同一份
`pasp-helper`。`pasp-verifier` 是只读事实检查契约，供主 agent 做有界委派；
agent 配置的注册方式依平台版本而定，配置文件存在不代表一定已注册。
安装后如平台尚未显示技能，请重新启动该平台。

查看目标项目中的版本：

```bash
cat /path/to/target-project/.agents/skills/pasp-helper/VERSION
```

## 更新已有安装

Git 源码仓库先更新，再重新安装：

```bash
git -C /path/to/PASPskills pull --ff-only
/path/to/PASPskills/scripts/install-pasp-skills.sh --force /path/to/target-project
```

默认仍为复制安装，旧命令中的 `--copy` 也继续有效。自行修改过当前安装内容的用户应先备份。
ZIP 用户下载并解压新版后，从新源码目录运行重新安装命令。

对于旧版根目录 `skills/` 布局，安装脚本仅在识别为旧 PASP 安装且使用 `--force` 时迁移：

- 原来的实际目录会先备份到 `.agents/pasp-install-backups/` 下，再迁走旧位置。
- 识别出的旧软链接会移除，外部源目录会保留。
- 与 PASP 安装无关的根目录 `skills/`、其他 skills 和用户主目录配置会保留。
- 源码仓库自己的 `skills/` 是维护目录；当它作为本次来源时不会被迁走。

备份位于技能扫描目录以外，避免旧副本重复出现在技能列表中。安装脚本会打印备份位置。

## 开发时跟随源码更新

需要直接使用源码目录内容时，显式选择 `--link`：

```bash
/path/to/PASPskills/scripts/install-pasp-skills.sh --link /path/to/target-project
```

这时只有 `.agents/skills/pasp-helper` 直接链接到源包，不经过项目根目录 `skills/`。
更新源码会直接改变目标使用的内容；源码目录必须保持存在。已安装项目切换模式时加 `--force`。

## 安装选项

```text
scripts/install-pasp-skills.sh [--force] [--copy | --link]
  [--source <repo-or-skill-directory>] [target-project-dir]
```

- `--force`：替换项目中已有的 PASP 入口并迁移识别出的旧布局。
- `--copy`：复制包，是默认模式；保留此参数兼容旧安装命令。
- `--link`：直接链接外部源包，适合开发维护。
- `--source <path>`：指定源码仓库或完整 skill 目录。
- `PASP_SKILLS_SOURCE`：通过环境变量指定来源，优先级低于 `--source`。

未指定来源时，脚本先从自身所在位置查找源码，再尝试当前工作目录。
单独复制安装脚本后，应显式提供来源，例如：

```bash
./install-pasp-skills.sh --source /path/to/PASPskills /path/to/target-project
```

## 辅助脚本依赖

安装需要 Unix-like shell 和 `bash`；阅读 workflow/reference 不需要安装 Python 包。
运行辅助脚本建议使用 Python 3.11 或更新版本，L2 原胞生成与部分原生四态法检查需要：

```bash
python3 -m pip install numpy spglib
```

安装脚本不会自动安装 Python 包、PASP、VASP、MPI 或集群调度环境。根据具体 workflow
分别准备计算工具。

## 使用

安装后在目标项目中打开 Codex 或 Claude，例如：

```text
使用 pasp-helper。我想从 POSCAR 开始做 PASP 的交换路径分析，下一步应该准备什么？
```

```text
使用 pasp-helper。解释 MC.input 的 PT.low_temp、PT.high_temp 和 PT.Tmesh。
```

```text
检查当前 PASP.input。修改字段前先查 reference；可以使用 subagent 做只读检查。
```

如果平台没有自动发现入口，可明确要求读取
`.agents/skills/pasp-helper/SKILL.md`。不要在目标根目录另建 `skills/` 来匹配旧提示词。

包内 `knowledge/...` 和 `subskills/...` 路径相对当前加载的 `SKILL.md` 所在目录；
输入、输出与计算阶段目录仍属于用户项目。要从项目根目录执行包内辅助脚本，可以先设置：

```bash
PASP_SKILL_ROOT="$(cd .agents/skills/pasp-helper && pwd -P)"
python3 "$PASP_SKILL_ROOT/knowledge/scripts/l3_effective_hamiltonian/prepare_l3.py" --help
```

## 支持范围与已知限制

已覆盖交换路径与磁相互作用模型、有效哈密顿量、Monte Carlo、动力学、GA 全局结构搜索、
紧束缚模型和自旋诱导极化 7 类 workflow。资料、模板与辅助脚本都在完整 skill 包内部，
运行时不依赖作者的讲义、历史 examples 或本地源码目录。

部分计算仍有既有版本限制：tight-binding 的某类 graph-allocation 路径可能报
`Error, graph already allocated.`；启用 `spin_lat.spin_int_stress T` 的已验证
`read_spin_stress` 路径只支持 1 个 MPI task。没有当前源码修复与验证证据时，
相应 workflow 仍会报告 blocked/failed。

根目录 `VERSION` 和源码 `skills/VERSION` 记录当前分支版本；GitHub Release 是单独发布的
快照，以 Release 页面为准。目录调整不改变科学计算参数或科学验证范围。

继续阅读：[包架构](skills/README.md)、[开发指南](skills/DEVELOPMENT_GUIDE.md)、
[更新记录](CHANGELOG.md)。
