# `Model magnon` Run Notes

> Historical observations from real `magnon` runs.
>
> **重要**：本文件是历史观察记录，不是当前用户工作区的事实。当前判断必须以用户实际目录中的文件和日志为准。

---

## 2026-05-10：NiI2 Lecture-2 FM / spiral examples

**目录**：
- `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/workflow/l2/magnon/runs/20260510-052512-FM`
- `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/workflow/l2/magnon/runs/20260510-052512-spiral`

**关键设置**：
- `Model magnon`
- `Read_init_spin T`
- `spin_lat.general_J T`
- `number_of_qpoints 100`
- FM: `SuperCell = identity`
- spiral: `SuperCell = [[4,0,0],[1,2,0],[0,0,1]]`

**输出验证**：
- 两个 run 的 `log.out` 都包含 `PASP is finished gracefully.`
- 两个 run 都生成 `spin_wave_E.dat` 和 `spin_wave_H_wf.dat`。
- FM run 有一个 `Warning: ia 1`，但最终 graceful finish；当前未确认该 warning 是否影响物理结果，使用时应回看 `log.out` 周边上下文。

**稳定观察**：
- magnon run 不会重写 `spin3.in`。
- 多段路径拼接由 `run.sh` 负责；单次 PASP 输出仍是当前段的 `spin_wave_E.dat`。

