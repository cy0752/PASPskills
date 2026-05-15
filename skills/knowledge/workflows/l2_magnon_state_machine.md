# State Machine: `Model magnon`

> 运行 `magnon` 前必须先读本文件。它只定义 STOP gate；长流程细节见 `l2_magnon.md`。

---

## L2 read-only input-preflight hard gate

在提升正式 `input/`、覆盖正式 input、派生 `runs/<run-id>/`、创建或编辑提交脚本 / 外部任务配置、或提交任务前，必须通过 `pasp-verifier` `mode: input-preflight` 的 read-only subagent 检查。

必须记录：
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`

subagent 授权只允许只读事实采集；不确认 q 路径、`SuperCell`、基态来源或物理参数，不修改文件，不创建 run 目录，不准备提交，也不授权提交任务。

如果用户已授权但 verifier / subagent 不可用，流程 blocked。只有用户明确豁免 L2 hard gate 时，主 agent 才能按同一 checklist 本地检查；此时必须记录 `L2_PREFLIGHT_HARD_GATE_WAIVED=true`、`LOCAL_PREFLIGHT_DONE=true` 和本地检查证据。

---

## S0. Intent Routed

**Allowed**
- 确认用户要算线性自旋波色散。
- 读取当前目录中的 `PASP.input`、`spin_exchange.dat`、`spin3.in`、`cell.str`、`unit_cell.str`。
- 判断当前目录是 draft、candidate input、formal input，还是已有 run 目录。

**STOP REQUIRED**
- 用户必须确认 `spin3.in` 的来源：手动构造、`Spin_lattice_interaction` 的 `spin3_lowest.out`、还是某个 `node_N_spin.out`。
- 用户必须确认 q 路径端点和 `number_of_qpoints`。
- 如果用户只给了一个目标目录，事实边界就是该目录；不得从 sibling FM/spiral 例子借参数或输出补当前目录缺口。

---

## S1. Input Preflight

本状态的 formal / run / submission 动作必须使用 `pasp-verifier` `mode: input-preflight` 完成只读检查；directory inventory 或 output validation 不能替代 input-preflight。

**Required checks**
- `spin_exchange.dat` 的四阶项计数必须为 `0`。
- `spin3.in` 的非空数据行数必须等于 `det(SuperCell) × NumberOfAtoms_in_cell.str`。
- `Read_init_spin T` 时，`spin3.in` 必须存在。
- `%block qpoints.magnon` 必须有当前线段的起点、终点两行。
- `number_of_qpoints` 在线段模式下必须至少为 2。
- 所有拟写字段必须先查对应 reference 卡。

**Forbidden**
- 不得把含非零四阶项的 `Spin_lattice_interaction` 版 `spin_exchange.dat` 直接喂给 `magnon`。
- 不得在未确认磁周期的情况下修改 `SuperCell` 来"适配" `spin3.in` 行数。
- 缺少 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true` 和 `STAGE_PREFLIGHT_PASS=true` 时，提升正式 input、覆盖正式 input、创建或编辑提交脚本、准备提交配置、派生 `runs/<run-id>/` 或提交任务。
- 不得在 baseline `inputs/` 中直接跑多段脚本，除非用户明确接受覆盖/污染风险。

**PROMOTE TO FORMAL INPUT ONLY IF**
- 硬输入齐全：`PASP.input`、`cell.str`、`unit_cell.str`、`spin_exchange.dat`、`spin3.in`。
- `spin_exchange.dat` 四阶项为 0。
- `spin3.in` 行数和 `SuperCell` 匹配。
- q 路径和 q 点数已由用户确认。
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true` 且 `STAGE_PREFLIGHT_PASS=true`。

---

## S2. Run And Validate

**Allowed**
- 在 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true` 且 `STAGE_PREFLIGHT_PASS=true` 后，将已确认的输入包复制到 `runs/<run-id>/`。
- 在 run 目录内执行 PASP 或用户给定多段路径脚本。
- 修改 run 目录中的提交脚本镜像、队列、核数等环境项。

**Required outputs**
- `log.out`
- `PASP.used_info`
- `spin_wave_E.dat`
- `spin_wave_H_wf.dat`（仅在详细输出开启时）

**STOP ON FAIL**
- `log.out` 中出现 `SIGSEGV`、`abort`、`Error`，不得把色散结果标为成功。
- 若有虚频或明显异常，回到 `Spin_lattice_interaction` 检查基态，而不是直接调 q 路径掩盖问题。

**Required checks**
- `spin_wave_E.dat` 非空行数等于 `number_of_qpoints`。
- 每行列数为 `1 + na_spin`；第一列是 q 点编号。
- 多段路径拼接时记录每段来源，并确认相邻段重复端点已处理。

**Forbidden**
- 缺少 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true` 或 `STAGE_PREFLIGHT_PASS=true` 时派生 run、编辑提交脚本镜像、配置外部任务或提交。
- output validation 不能反向授权 input promotion 或补上缺失的用户确认。
- 不能把历史 FM/spiral run notes 中的成功当成当前 run 成功。
