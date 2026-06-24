# GA.VASPCMD

## 含义
用于设置 `GA.parallel F` 路径下调用 VASP 的外部命令字符串。

## 默认值
空字符串

## 取值
字符串。内容必须是当前运行环境可执行的 VASP 命令或包装命令。

## 相关逻辑
- 当前源码在 GA 初始化时读取 `GA.VASPCMD`，默认空字符串。
- 当 `GA.parallel F` 时，GA 走逐个结构本地优化路径，VASP 运行依赖 `GA.VASPCMD`。
- 当 `GA.parallel T` 时，GA 会调用 `bash run_pvasp.sh`，此时 `run_pvasp.sh` 承担批量提交/运行和结果组织职责。

## 何时使用
- 使用 `Model GA` 且 `GA.parallel F`，并且候选结构需要由外部 VASP 计算弛豫/评价时。

## 注意事项
- `GA.VASPCMD` 是运行环境事实，不是可移植的科学默认值。它可能依赖模块加载、MPI 命令、容器、队列系统或本机 VASP 路径。
- 如果 `GA.parallel F` 但 `GA.VASPCMD` 为空或未确认，L6 input preflight 应阻断提交准备。
- 磁性 GA、批量候选或希望保持 `vasp_N/` 目录布局时，workflow 常会建议改用 `GA.parallel T` 并确认 `run_pvasp.sh`，但这不改变本参数的语义。

## 来源章节
- Source-audit curated L6 GA behavior
