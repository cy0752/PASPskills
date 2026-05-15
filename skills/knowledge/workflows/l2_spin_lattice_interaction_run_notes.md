# `Model Spin_lattice_interaction` Run Notes

> Historical observations from real `Spin_lattice_interaction` runs.
>
> **重要**：本文件是历史观察记录，不是当前用户工作区的事实。当前判断必须以用户实际目录中的文件和日志为准。

---

## 2026-05-10：NiI2 Lecture-2 PTMC / CG validation（旧镜像 / 旧 build）

**目录**：
- `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/workflow/l2/Spin_lattice_interaction/runs/20260510-052512-NiI2`
- `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/workflow/l2/Spin_lattice_interaction/runs/20260510-065253-NiI2-PTM20`
- `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/workflow/l2/Spin_lattice_interaction/runs/20260510-070712-NiI2-PTM20-mpirun`

**关键设置**：
- `Model Spin_lattice_interaction`
- `SuperCell = [[20,0,0],[10,20,0],[0,0,1]]`
- `PT.M = 40` for first run; `PT.M = 20` for the later two runs
- `spin_lat.relax_str T`
- `opt.NSW 10000`
- `opt.EDIFFG 1.0E-8`

**输出观察**：
- 三个 run 都打印了 `End of PTMC`。
- 三个 run 都生成了 `final_ene.all`、`spin3_lowest.out`、`lowest_onlyspin.xsf`、`lowest_remove_FM.xsf`。
- `spin3_lowest.out` 行数为 1201，和当前 `cell.str` / `SuperCell` 对应的全原子 spin3 格式一致。
- `magnon` 下游 handoff 应优先使用 `spin3_lowest.out`，复制或重命名为 `spin3.in` 后再做行数校验。

**异常**：
- 三个 run 都在 PTMC 完成后出现 `forrtl: severe (174): SIGSEGV, segmentation fault occurred`。
- 日志最后一个 PASP 业务输出为 `M,Mdir:`，对应源码 `output_sub.F90::remove_FM`；`lowest_remove_FM.xsf` 已经写出。
- 未看到 `spin_str_relax` 的正常完成输出，因此本次不能把 `spin_lat.relax_str T` 的 CG 放松结果视为验证通过。

**解释**：
- 这类 run 应标记为：PTMC 主循环完成，最低态文件已可用于有条件下游接力；CG / postprocess 没有干净结束。
- 对旧 `paspmpi:1` / 旧 build 来说，若必须复现旧环境，建议先用 `spin_lat.relax_str F` 做可复现的基态搜索；不要把这条旧环境建议套用到已验证的 `paspmpi:v2` run 上。

**后续待验证**：
- 同一输入换到修复后的 PASP build 后，`spin_lat.relax_str T` 是否能 graceful finish。

---

## 2026-05-10：NiI2 Lecture-2 PTMC / CG validation（`paspmpi:v2` 修复镜像）

**目录**：
- `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/workflow/l2/Spin_lattice_interaction/runs/20260510-101850-NiI2-v2-test`

**提交记录**：
- job id: `hpc-job-c5a182d6-6ffc-41d9-ad05-f71834f20243`
- image: `docker.sii.shaipower.online/inspire-studio/paspmpi:v2`
- resource: `CPU资源-2` / `20核100GB`
- tasks: `20`
- entrypoint: `cd <run-dir> && bash subpasp1.sh`
- final job status: `SUCCEEDED_RETAINING`

**关键设置**：
- `Model Spin_lattice_interaction`
- `SuperCell = [[20,0,0],[10,20,0],[0,0,1]]`
- `PT.M = 40`
- `PT.nblk_T = 400`
- `nbeg_blk = 200`
- `nblk = 100`
- `spin_lat.relax_str T`
- `opt.NSW 10000`
- `opt.EDIFFG 1.0E-8`

**输出观察**：
- `log.out` 打印 `End of PTMC`。
- `log.out` 打印 `CG finish. Node= 0 NSTEP= 126 NSW= 10000`。
- `log.out` 末尾打印 `PASP is finished gracefully.`。
- 未观察到 `SIGSEGV`、`forrtl: severe`、`segmentation fault`。
- 生成了 `spin3_lowest.out`、`relax-spin3_lowest.out`、`node_0_spin.out`、`node_0_finalspin.out`。
- 上述 spin3-family 文件行数均为 1201，和当前 `cell.str` / `SuperCell` 对应的全原子 spin3 格式一致。
- 生成了 `lowest_onlyspin.xsf`、`lowest_remove_FM.xsf`、`relax-lowest_onlyspin.xsf`、`relax-lowest_remove_FM.xsf`。
- 生成了 `C_PTMC.dat` / `C_PTMC_K.dat`、`E_PTMC.dat` / `E_PTMC_K.dat`、`M_PTMC.dat` / `M_PTMC_K.dat`、`X_PTMC.dat` / `X_PTMC_K.dat` 等 PTMC 统计输出。

**解释**：
- 对这组 NiI2 Lecture-2 输入，`paspmpi:v2` 已验证修复旧 build 在 `spin_lat.relax_str T` 的 CG / 后处理崩溃。
- 如果 `spin_lat.relax_str T` 且 `relax-spin3_lowest.out` 存在，应优先把 `relax-spin3_lowest.out` 视为 CG-relaxed ground-state handoff 候选；如用户只需要 MC 最低态或要复现实验前旧流程，可继续使用 `spin3_lowest.out`。
- 旧 run notes 中的 `SIGSEGV` caveat 仍保留为版本化历史记录，不应套用到 `paspmpi:v2` 的成功 run 上。
