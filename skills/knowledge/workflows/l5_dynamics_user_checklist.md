# L5 Dynamics User Checklist

这是给用户快速过一遍的 L5 dynamics checklist，覆盖 generic/new-material `atomic_effective_H` input preparation、Cr2O3 spin-lattice dynamics 和 BaTiO3 electric hysteresis。它不是 `l5_dynamics_state_machine.md` 的替代品，也不能替代 reference-before-write 规则：凡是要写或改 `PASP.input`、`MD.input`、block、文件格式、编号或条件依赖，仍必须先查 `knowledge/reference/`。

BaTiO3 electric hysteresis uses the separate section at the end of this checklist. Do not use the Cr2O3 stage 1 / 2 / 3 handoff rules to validate BaTiO3 `field.dat` / `P_abs.dat` analysis.

For generic/new-material packages, do not borrow Cr2O3 or BaTiO3 values unless the user explicitly identifies that historical material/example as the current task source.

## 1. New-material quick start

For a new material, L5 starts from a prepared or user-authoritative `Model atomic_effective_H` package. It does not generate fitted model products by copying examples.

跑前先让用户或上游证据给出：
- Branch / goal: plain MD, LLG / ASD, SLD, electric-field / polarization response, smoke test, production run, output validation, or downstream handoff.
- Upstream model package: `local_mode_PM.dat`, `J_best.dat`, structures, mode definition, mass definition, species / spin values when applicable, and proof that they share the same material/basis.
- Local-mode masses: mass count/order and effective-mass source, especially for collective soft modes; do not let the agent silently fill `atom_Heff.MASS_local_mode`.
- Initial state, when current settings read one: first-stage `amp_local_mode.in` from user/upstream authority, or validated previous-run `amp_local_mode.out` with run id and validation evidence.
- Conditional physics inputs / dependencies: `Zeff.dat`, `elastic.dat`, `spin_strain.dat`, `Field_for_Electrocaloric`, or `local_mode.MD_mode_range` only when current settings/reference/user authority establish dependency.
- Dynamics settings: timestep, run length, damping, temperature, initial velocity, output cadence, active `SLD.mode` / LLG / field controls, and smoke-test vs production label.
- Finite-temperature statistics: production supercell size, equilibration/sampling window, and finite-size limitations when the target is `<P^2>` vs `T`, polarization fluctuations, or Curie-Weiss-style analysis.
- Expected outputs: `temperature.dat`, `energy.dat`, `amp_local_mode.out`, same-run `field.dat` / `P_abs.dat`, or another user-defined validation target.
- Run environment: command, MPI ranks, scheduler/image/executable path, stdout/stderr paths, queue/walltime. These are environment facts, not portable defaults.

Agent 可以整理 candidate README、file-role inventory、reference inventory、stale-output inventory，以及带标签的 smoke-test candidate。正式 `input/`、`runs/<run-id>/`、submission artifacts 和提交准备仍必须等用户确认表 + read-only input preflight pass。

### If the package comes from L3

Ask for the current-material L3 handoff README / PROGRESS or equivalent output-validation record. It should map:
- `local_mode_PM.dat`: from the successful same-basis L3 shared-basis / Invariant run.
- `J_best.dat`: from the validated fitted-parameter selection, with fitting dataset / settings provenance.
- Structure and basis: `cell.str`, `unit_cell.str` or equivalent route, `SuperCell`, `Z_values`, `Spin_values`, mode definition, and mass definition when used.
- Fitting audit trail: dataset files, lambda / keep / skip settings, selected run id, and known gaps.

Still ask separately for:
- first-stage `amp_local_mode.in`, when current settings read one, and why it is valid for this L5 branch;
- `Zeff.dat` when polarization / electric-field settings require it;
- production dynamics settings, run environment, and scientific acceptance criteria.

Before L5 preflight, confirm that `local_mode_PM.dat`, `J_best.dat`, structure route, mode / mass definition, species / spin values, and initial amplitudes when read all belong to the same current-material basis. If the L3 record does not prove that, keep the package as candidate / blocked.

## 2. Cr2O3: 先确认当前做哪一段

| Stage | `SLD.mode` | 目的 | 定性行为 |
|---|---:|---|---|
| Stage 1 lattice heating | `1` | 加热 lattice / displacement subsystem | lattice relevant，spin frozen by intent |
| Stage 2 spin heating | `2` | 加热 spin subsystem | spin relevant，lattice frozen by intent |
| Stage 3 coupled SLD relaxation | `3` | spin 和 lattice 一起演化 / 弛豫 | both spin and lattice evaluated together |

`SLD.mode` 的精确定义和写法以 `knowledge/reference/params/SLD.mode.md` 为准。

## 3. Cr2O3: 用户或上游必须给齐的文件

每个 stage 的候选输入包至少检查这些文件：

- `PASP.input`
- `MD.input`
- `cell.str`
- `unit_cell.str`
- `local_mode_PM.dat`
- `J_best.dat`
- 所有 `PASP.input` 直接 `%include` 的文件，例如 `mode_def.input`、`mode_mass.input`
- 当前 stage 的 initial `amp_local_mode.in`

上游来源要说清楚：

- `local_mode_PM.dat` 通常来自前序 PASP / L3 effective-Hamiltonian 模型建立。
- `J_best.dat` 通常来自前序 PASP / L3 拟合结果。
- Stage 2 的 `amp_local_mode.in` 必须来自已验证的 Stage 1 `amp_local_mode.out`。
- Stage 3 的 `amp_local_mode.in` 必须来自已验证的 Stage 2 `amp_local_mode.out`。

不要静默覆盖 downstream `amp_local_mode.in`。记录 upstream run id、source `amp_local_mode.out`、validation evidence 和 destination path。

## 4. 跑前快速检查

- `PASP.input` 的 direct includes 都在同一候选包内，路径可解析。
- `MD.input` 里的 `SLD.mode` 和当前 stage 匹配：Stage 1 -> `1`，Stage 2 -> `2`，Stage 3 -> `3`。
- 对纯结构 / 铁电 local-mode MD，确认 `SLD.mode 1` 已显式设置；若目标是 NVT，不要保留不支持 NVT 的 `LLG.method 1`，通常应确认 `LLG.method 2`。
- `%block atom_Heff.MASS_local_mode` 的质量个数等于当前 local-mode count，顺序与 mode basis 一致，并按 reference 写成同一连续列表。
- `amp_local_mode.in` 行数和当前 supercell / local-mode basis 一致；如果做 smoke-test 缩小 supercell，必须同步调整或重建 `amp_local_mode.in`。
- planned MPI ranks 与 supercell factoring rule 兼容：存在 `p1 * p2 * p3 = ranks`，且 `p1 | n1`、`p2 | n2`、`p3 | n3`。例如 `8x8x8` 可用 `64=4x4x4`，但不能用 `54`；不确定时不要准备提交。
- `local_mode_PM.dat`、`J_best.dat`、mode definition、mass definition、结构文件来自同一模型基底，没有混用。
- damping、temperature、time step、run length、output cadence 已由用户确认；历史 example 数值不是 production default。
- smoke-test settings 和 production settings 已明确区分；smoke-test 结果不能写成 production validation。
- 做极化涨落 / `<P^2>` vs `T` 分析时，小超胞和短轨迹只能作为 smoke test；production 分析必须有用户确认的更大超胞、采样时长和接受标准。
- 新 run 目录不要复制旧输出：不要带入旧 `temperature.dat`、`energy.dat`、`amp_local_mode.out`、`PASP.used_info`、`*_used.dat`、旧日志或 historical `complete/` 快照。

正式 input、run 派生、submission preparation 或提交前，还必须满足状态机中的用户确认和 read-only input preflight gate。

## 5. 跑后快速检查

每个 stage 至少检查：

- log / stdout 有正常结束证据，例如 `PASP is finished gracefully` 或当前环境等价 marker。
- `temperature.dat` 存在，包含 spin / lattice subsystem temperature 信息，数据行 step / time 单调。
- `energy.dat` 存在，能形成 energy time series，数据行 step / time 单调。
- `amp_local_mode.out` 存在，行数与当前 stage 的 state size 一致。
- branch-consistent qualitative behavior：
  - Stage 1：重点看 lattice 行为，spin 按 stage intent 解释。
  - Stage 2：重点看 spin 行为，lattice 按 stage intent 解释。
  - Stage 3：spin 和 lattice 一起检查，不只看单列。
- Stage 1 / 2 的 downstream handoff 只能使用通过 output validation 的 `amp_local_mode.out`。

`PASP.used_info` 如果存在要检查；如果它很稀疏或没有完整 effective-setting summary，记录这个限制，并交叉检查 `MD.input`、`PASP.input`、logs 和核心输出。不要只因为 `PASP.used_info` 稀疏就自动 fail，也不要只因为它存在就自动 pass。

## 6. Energy 和阈值

Stage 3 如果按 NVE-like coupled relaxation 设计，报告 `energy.dat` 的 total-energy drift / range。不要使用隐藏阈值判断是否合格；除非用户提供明确阈值，否则只报告数值范围、趋势和风险。

目标温度、弛豫质量、能量漂移是否科学可接受，属于用户 / 科学负责人判断，不由 checklist 自动判定。

## 7. 最小交接记录

向下一 stage 或绘图交接前，记录：

- stage、`SLD.mode`、run id、运行目录；
- formal input 来源和 preflight evidence；
- `local_mode_PM.dat`、`J_best.dat`、结构和 mode / mass 文件来源；
- `amp_local_mode.in` 来源；如果是 Stage 2 / 3，记录 upstream `amp_local_mode.out`；
- completion log、`temperature.dat`、`energy.dat`、`amp_local_mode.out` 检查结果；
- smoke-test 或 production 标签；
- energy drift / range 报告，若当前 stage 需要。

## 8. BaTiO3 electric hysteresis quick check

BaTiO3 electric hysteresis is a single-stage `Model atomic_effective_H` MD electric-field branch. It is not a Cr2O3 `SLD.mode 1/2/3` sequence.

跑前至少确认：
- Branch intent is BaTiO3 electric-field / polarization hysteresis.
- Candidate package contains `PASP.input`, `MD.input`, `cell.str`, `unit_cell.str`, `local_mode_PM.dat`, `J_best.dat`, `amp_local_mode.in`, and all direct `%include` files.
- `Zeff.dat` is present and provenance-checked when `atom_Heff.getP T` or active electric-field behavior requires polarization/BEC support.
- `local_mode_PM.dat`, `J_best.dat`, structure files, mode definition / mass definition, `Z_values`, `amp_local_mode.in`, and `Zeff.dat` all belong to the same model / unit-cell / local-mode basis.
- `SuperCell` and `amp_local_mode.in` row count match the current basis; smoke-test reductions must reduce or regenerate the initial amplitudes consistently.
- Electric-field controls such as `MD.E_type`, `MD.E_x/y/z`, `MD.E_omega`, `MD.E_phi`, and optional `Field_for_Electrocaloric` are user-confirmed and reference-checked before writing.
- For periodic/cosine fields, `atom_Heff.MD_time` covers the intended field period(s); use `T = 2*pi / MD.E_omega` only when the current input/reference confirms units and branch semantics.
- `MD.aft_step` leaves a nonempty sampled window before the total MD steps end. For demos, `aft_step >= total_steps` means no useful loop recording; production equilibration windows must be explicitly confirmed.
- `local_mode.MD_mode_range` is reference/user-authority covered before writing; lower bounds must not exceed upper bounds.
- Scheduler helper, MPI ranks, executable path, module setup, and walltime are environment facts only, not defaults from MD-1; MPI ranks must satisfy the same `p1 * p2 * p3 = ranks` supercell-factor rule before submission.
- Candidate package contains no stale `field.dat`, `P_abs.dat`, `PASP.used_info`, old logs, or historical `complete/` residues.

跑后至少确认：
- Log / stdout has normal PASP completion evidence.
- `PASP.used_info` confirms effective settings when available; if sparse or missing, cross-check `PASP.input`, `MD.input`, logs, and output headers.
- `field.dat` exists, has `step`, `time (ps)`, and electric-field component columns, with monotonic sampled rows.
- `P_abs.dat` exists, has `step`, `time (ps)`, polarization component columns and `P_abs`, with monotonic sampled rows.
- `field.dat` and `P_abs.dat` come from the same run and their sampled `step` / `time (ps)` rows align. Do not mix `output/` and `complete/` or sibling-run files without provenance evidence.
- `energy.dat` and `temperature.dat` may be useful diagnostics, but they do not replace same-run `field.dat` + `P_abs.dat` validation.

Hysteresis plotting is allowed only after validation passes. Record run id, formal input provenance, `Zeff.dat` provenance, effective field settings evidence, and the selected `P_*` versus `E_*` components. Label one-period or short runs as workflow/plotting demonstrations unless the user provides production convergence and acceptance criteria.
