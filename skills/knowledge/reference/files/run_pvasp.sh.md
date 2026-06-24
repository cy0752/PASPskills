# run_pvasp.sh

## 文件作用
`run_pvasp.sh` 是 L6 GA `GA.parallel T` 路径下的外部 VASP 评价 helper。当前源码会调用：

```bash
bash run_pvasp.sh
```

它通常负责把 PASP 生成的 `POSCAR_N` 或同类候选结构分发到 `vasp_N/` 子目录，运行或提交 VASP，等待任务完成，并把 `CONTCAR`、`OSZICAR`、`OUTCAR`、磁性相关文件等整理到 PASP 后续读取的位置。

## 何时需要
- `Model GA` 且 `GA.parallel T`。
- 用户希望把候选结构批量提交到 Slurm/PBS/本地 MPI/容器环境。
- 需要保持 `vasp_N/` 风格的外部评价目录和同一套后处理路径。

## 不是通用默认脚本
- `run_pvasp.sh` 是环境 helper，不是 PASP 科学参数默认值。
- 脚本内容必须适配当前集群、队列系统、VASP 路径、MPI 命令、POTCAR/INCAR/KPOINTS 来源、磁性分支和清理策略。
- Slurm 示例只能作为脚本形状参考，不能直接当作当前环境事实。

## Preflight 应检查
- 脚本存在、可读，并位于 PASP 运行目录期望的位置。
- 脚本处理的候选命名与当前 PASP 输出一致，例如 `POSCAR_N`、`vasp_N/` 或当前版本/分支的等价命名。
- 脚本会提供 PASP 后续读取所需的 `CONTCAR`、`OSZICAR`、必要时 `OUTCAR`、`MAGMOM_*` 或磁性子目录结果。
- `INCAR`、`KPOINTS`、`POTCAR`、`vasp.slurm` 或其他调度文件来自当前用户/环境确认，不是历史示例残留。
- 脚本的等待、失败检测、stdout/stderr、清理行为明确；不能只提交作业却让 PASP 在结果未完成时继续读取。

## VASP 输入建议边界
- GA 中晶格可能随候选结构波动，workflow 常建议优先使用 VASP automatic mesh 风格的 `KPOINTS`，而不是固定尺寸网格。
- 多阶段弛豫可逐步提高 `PREC`、收紧 `EDIFF`、`EDIFFG` 和自动 k 点长度；具体值必须由用户或项目输入确认。
- 本 reference 不提供通用生产 `INCAR` / `KPOINTS` / `POTCAR` 默认值。

## 相关参数
- `GA.parallel`
- `GA.VASPCMD`

## 来源
- Source-audit curated L6 GA external-evaluator behavior
