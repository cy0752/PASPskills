# State Machine: `Model magnon`

> 运行 `magnon` 前必须先读本文件。它只定义 STOP gate；长流程细节见 `l2_magnon.md`。

---

## L2 deterministic input preflight and bounded verifier

在提升正式 `input/`、覆盖正式 input、派生 `runs/<run-id>/`、创建或编辑提交脚本 / 外部任务配置、或提交任务前，先运行本 skill 自带的确定性检查：

```text
python knowledge/scripts/l2_validate_inputs.py <package-or-run-dir> --workflow magnon
```

它一次性检查有效 FDF/include、字段和 block 形状、物种与 `isaAB` 数量、cell/SuperCell、`spin3.in` 行号、q 端点、有限数值、exchange 五段计数、矩阵 J 宽度、原胞晶格依赖和 magnon 四阶项约束。记录 JSON 结果并修复全部 error，再进入只读科学检查；不要在每个格式性修补后重复相同的人工检查。

`pasp-helper` 原生委派仍须保留。若 pair 坐标来源、结构映射、磁性参考来源或其他科学选择未由上述脚本覆盖，仍委派 `pasp-verifier` `mode: input-preflight`；只有该 bounded verifier 实际通过时才记录 `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true` 和 `STAGE_PREFLIGHT_PASS=true`。脚本 pass 不能替代科学验证。verifier 只读，不确认 q 路径、`SuperCell`、基态或物理参数，也不修改文件或创建 run 目录。

若确定性脚本不可用，必须记录未完成的检查并交由 verifier 或阻塞；若科学 provenance/mapping 问题仍未解决而 verifier 不可用，不能提升或运行。

For completed four-state DFT tasks, also follow `l2_four_state_delivery.md`.
It defines preparation before consolidated scientific questions, deterministic
delivery checks and the bounded container-repair exception. Do not ask again for
facts or authorization already supplied. Assumptions remain explicit and editable;
preparing a candidate is not confirmation of its physical choices. A script pass
never certifies the exchange model, magnetic ground state or quantum spin scale.

Input receipts now include primitive handedness and raw-record checks. Fix a
left-handed basis together with coordinates/site mappings, never just a sign.
The raw exchange/spin formats are not FDF: emit complete numeric records without
internal blanks or comments. See the delivery guide for exact supported scope
and source-snapshot assumptions. Recheck changed packages, not unchanged packages
after report-only edits. Only the actual scientific delta goes back to verifier.

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

本状态的 formal / run / submission 动作必须先有上述脚本的 `pass`；未覆盖的科学问题仍需 `pasp-verifier`。directory inventory 或 output validation 不能替代需要的科学检查。

**Required checks**
- `spin_exchange.dat` 的四阶项计数必须为 `0`。
- `spin3.in` 的非空数据行数必须等于 `det(SuperCell) × NumberOfAtoms_in_cell.str`。
- `Read_init_spin T` 时，`spin3.in` 必须存在。
- `%block qpoints.magnon` 必须有当前线段的起点、终点两行。
- `number_of_qpoints` 在线段模式下必须至少为 2。
- 所有拟写字段必须先查对应 reference 卡；脚本不能替代 reference。

**Forbidden**
- 不得把含非零四阶项的 `Spin_lattice_interaction` 版 `spin_exchange.dat` 直接喂给 `magnon`。
- 不得在未确认磁周期的情况下修改 `SuperCell` 来"适配" `spin3.in` 行数。
- deterministic checker 报错时，不得提升正式 input、覆盖正式 input、创建或编辑提交脚本、准备提交配置、派生 `runs/<run-id>/` 或提交任务。
- 不得在 baseline `inputs/` 中直接跑多段脚本，除非用户明确接受覆盖/污染风险。

**PROMOTE TO FORMAL INPUT ONLY IF**
- 硬输入齐全：`PASP.input`、`cell.str`、`unit_cell.str`、`spin_exchange.dat`、`spin3.in`。
- `spin_exchange.dat` 四阶项为 0。
- `spin3.in` 行数和 `SuperCell` 匹配。
- q 路径和 q 点数已由用户确认。
- deterministic checker 已返回 `pass`；若存在未覆盖的 provenance/mapping gate，必须由只读 verifier 通过，否则保持 blocked，不能提升。

---

## S2. Run And Validate

**Allowed**
- 在 deterministic checker 返回 `pass`，且任何必要的科学 verifier gate 已通过后，将已确认的输入包复制到 `runs/<run-id>/`。
- Under TASK RUNTIME, hand the isolated inputs to the controller and inspect its returned runtime evidence. The controller uses the supplied local launcher; no scheduler or alternative MPI command is needed. Without TASK RUNTIME, follow the user's execution scope; a draft-only request never runs PASP.
- 在用户授权自行运行且非 controller 执行的任务中，在 run 目录内执行 PASP 或用户给定多段路径脚本。
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
- 缺少 deterministic `pass`，或仍有未解决的科学 verifier gate 时，不得派生 run、编辑提交脚本镜像、配置外部任务或提交。
- output validation 不能反向授权 input promotion 或补上缺失的用户确认。
- 不能把历史 FM/spiral run notes 中的成功当成当前 run 成功。
