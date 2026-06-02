# State Machine: `Model Spin_lattice_interaction`

> 运行 `Spin_lattice_interaction` 前必须先读本文件。它只定义 STOP gate；长流程细节见 `l2_spin_lattice_interaction.md`。

---

## L2 read-only input-preflight hard gate

在提升正式 `input/`、覆盖正式 input、派生 `runs/<run-id>/`、创建或编辑提交脚本 / 外部任务配置、或提交任务前，必须通过 `pasp-verifier` `mode: input-preflight` 的 read-only subagent 检查。

必须记录：
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`

subagent 授权只允许只读事实采集；不确认 `spin_exchange.dat` 的物理合理性、不选择 `SuperCell` / PT / MC / CG 参数、不修改文件、不创建 run 目录、不准备提交，也不授权提交任务。

如果用户已授权但 verifier / subagent 不可用，流程 blocked。只有用户明确豁免 L2 hard gate 时，主 agent 才能按同一 checklist 本地检查；此时必须记录 `L2_PREFLIGHT_HARD_GATE_WAIVED=true`、`LOCAL_PREFLIGHT_DONE=true` 和本地检查证据。

---

## S0. Intent Routed

**Allowed**
- 确认用户确实要做 PTMC / CG 找磁基态。
- 读取当前目录中的 `PASP.input`、`MC.input`、`cell.str`、`unit_cell.str`、`spin_exchange.dat`。
- 判断当前目录是 draft、candidate input、formal input，还是已有 run 目录。

**STOP REQUIRED**
- 用户必须确认 `spin_exchange.dat` 的物理来源：DFT 拟合、文献参数、还是手工构造。
- 若 `spin_exchange.dat` 来自 `find_J_path_sym` / DFT handoff，必须确认第一段 lattice vectors 来自 `unit_cell.str` / `unit_cell_in_Ang`，J pair 坐标来自 nearest-image `pair_coord` 或等价上游输出；不得接受 agent 手工调整 pair 坐标作为修复。
- 用户必须确认当前 `SuperCell` 能容纳目标磁周期；不能从 NiI2 模板直接借。
- 如果用户只给了一个目标目录，事实边界就是该目录；不得从 sibling 例子借参数或输出补当前目录缺口。

---

## S1. Candidate Input Package

**Allowed**
- 做只读 preflight：文件齐全性、`PT.M` 与 planned MPI ranks 的整数倍关系、`spin_exchange.dat` 结构、`spin_exchange.dat` 第一段 unit-cell 基矢与 nearest-image pair-coordinate provenance、`SuperCell` 行列式、`Read_init_spin` 依赖。正式 / run / submission 动作前必须使用 `pasp-verifier` `mode: input-preflight`。
- 生成 draft 输入建议。
- 在 `drafts/`、notes 或候选文件中记录建议。

**Forbidden**
- 未经用户确认就改 `spin_exchange.dat`、`SuperCell`、PT 温度范围、MC 步数或 CG 开关。
- 把 `magnon` 用的四阶项裁剪规则反向套到 `Spin_lattice_interaction`。
- 缺少 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true` 和 `STAGE_PREFLIGHT_PASS=true` 时，提升正式 input、覆盖正式 input、创建或编辑提交脚本、准备提交配置、派生 `runs/<run-id>/` 或提交任务。
- 把 baseline `inputs/` 当作运行目录直接提交，除非用户明确接受输出污染风险。

**STOP REQUIRED**
- 修改任何 `MC.input` 数值前，确认科学意图和算力预算。
- 启用 `spin_lat.relax_str T` 前，确认用户接受更高 wall time，并确认运行环境使用已验证的 PASP build（例如 2026-05-10 验证通过的 `paspmpi:v2`）或用户明确要测试当前 build。旧 `paspmpi:1` / 旧 build 曾观察到 CG / 后处理 `SIGSEGV`。
- `Read_init_spin T` 时，必须确认 `spin3.in` 来源和非空数据行数。

**PROMOTE TO FORMAL INPUT ONLY IF**
- 硬输入文件齐全：`PASP.input`、`MC.input`、`cell.str`、`unit_cell.str`、`spin_exchange.dat`。
- `spin_exchange.dat` 结构通过读取顺序检查。
- `spin_exchange.dat` 第一段基矢来自 `unit_cell.str`，不是 `cell.str`；J pair 坐标有 nearest-image `pair_coord` / 等价上游 provenance，且没有手工改坐标。
- `PT.M` 与 planned MPI ranks 已检查：`PT.M` 应为 rank 数的整数倍；若 rank 数未知，必须记录 blocked 或提交前复查，不得直接标为 submit-ready。
- 所有拟修改的字段已查 reference，并有用户确认或明确上游来源。
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true` 且 `STAGE_PREFLIGHT_PASS=true`。

---

## S2. Run Directory

**Allowed**
- 在 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true` 且 `STAGE_PREFLIGHT_PASS=true` 后，将已确认的输入包复制到 `runs/<run-id>/`。
- 在 run 目录内执行 PASP 或用户给定提交脚本。
- 修改 run 目录中的提交脚本镜像、队列、核数等环境项。

**Forbidden**
- 在未确认的 candidate input 中提交。
- 缺少 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true` 或 `STAGE_PREFLIGHT_PASS=true` 时派生 run、编辑提交脚本镜像、配置外部任务或提交。
- 将运行输出回写覆盖 baseline `inputs/`，除非用户明确要求归档某个 validated handoff 文件。

**STOP ON FAIL**
- `log.out` 中出现 `SIGSEGV`、`abort`、`Error` 时，不得把该 run 标为完全成功。
- 如果 PTMC 已经打印 `End of PTMC` 且 `spin3_lowest.out` 存在，可以标记为 "MC complete; CG/postprocess failed" 并继续做有条件的下游 handoff。

---

## S3. Output Validation

**Required checks**
- `log.out` 是否包含 `End of PTMC`。
- 若 `spin_lat.relax_str T`，`log.out` 是否包含 `CG finish` 和 `PASP is finished gracefully.`。
- 是否有 `spin3_lowest.out`；若无，再看 `node_N_spin.out`。
- 若 `spin_lat.relax_str T` 且要使用松弛后构型，是否有 `relax-spin3_lowest.out`。
- `spin3_lowest.out` 的非空数据行数是否等于 `cell.str` 原子数乘以 `det(SuperCell)`。
- `relax-spin3_lowest.out` 若存在并用于 handoff，也必须做同样行数校验。
- 如果要接给 `magnon`，复制为 `spin3.in` 前必须记录来源 run 和文件名。

**Handoff**
- 首选：`spin3_lowest.out` → `magnon/spin3.in`
- CG 成功且用户要松弛后基态：`relax-spin3_lowest.out` → `magnon/spin3.in`
- 备选：最低能量 node 的 `node_N_spin.out` → `magnon/spin3.in`
- 不要默认用 `node_N_finalspin.out`；它是 PTMC 末态，不保证是最低态。

**Forbidden**
- output validation 不能反向授权 input promotion 或补上缺失的用户确认。
- 不能把历史 run notes 中的成功当成当前 run 成功。
