# Workflow: L5 Dynamics / MD / ASD / SLD

> 本 workflow 面向 `Model atomic_effective_H` 的 MD、spin dynamics、LLG 和 spin-lattice dynamics。正式写 input、派生 run、准备提交或提交前，必须先读 sibling `l5_dynamics_state_machine.md` 并执行其 STOP gate。

## 目标
使用已经建立并拟合好的 effective Hamiltonian 进行时间演化模拟，分析 lattice、spin 或 coupled spin-lattice subsystem 的加热、弛豫、响应和 handoff state。

MVP 聚焦 Cr2O3 spin-lattice relaxation branch：
1. stage 1 lattice heating：`SLD.mode 1`，只演化 lattice / displacement degrees of freedom。
2. stage 2 spin heating：`SLD.mode 2`，只演化 spin degrees of freedom。
3. stage 3 coupled SLD relaxation：`SLD.mode 3`，同时演化 spin and lattice degrees of freedom。

本 workflow 也支持 BaTiO3 electric-hysteresis branch：
- single-stage `Model atomic_effective_H` MD run；
- electric-field controls drive the dynamics；
- `field.dat` and `P_abs.dat` are the primary same-run validation and plotting targets；
- it does not use the Cr2O3 three-stage `amp_local_mode.out` handoff sequence.

本 workflow 还覆盖 generic / new-material `atomic_effective_H` dynamics input preparation。这个路径的前提是：用户或上游 PASP 阶段已经提供当前材料的 effective-H model products and provenance。L5 可以整理、检查、缩小 smoke-test candidate、派生 run 目录和验证输出；L5 不能从 Cr2O3 / BaTiO3 examples 自动合成新材料的 `local_mode_PM.dat`、`J_best.dat`、mode basis、mass definition、`Zeff.dat` 或 production dynamics settings。

## 适用问题
- 我已经有 `local_mode_PM.dat` 和 `J_best.dat`，想做 `atomic_effective_H` 的 MD / ASD / SLD。
- 我有一个新材料的 effective-H package，想知道 L5 运行前还缺哪些文件、哪些设置必须确认、哪些东西只能作为 smoke test。
- 我想做 Cr2O3 spin-lattice relaxation：先 lattice heating，再 spin heating，最后 coupled relaxation。
- 我想确认一个 L5 dynamics run 的输出能不能拿去画 `temperature.dat` / `energy.dat`，或能不能把 `amp_local_mode.out` 交给下一 stage。
- 我想确认 BaTiO3 electric-field MD 的 `field.dat` 和 `P_abs.dat` 能不能成对用于 hysteresis plotting。
- 我想改 `MD.input` 里的 time step、run length、damping、temperature、`SLD.mode` 或 `LLG.*`，但需要知道当前 stage 能不能改。
- 我想改 BaTiO3 branch 的 electric-field controls，例如 `MD.E_type`、`MD.E_x/y/z`、`MD.E_omega`、`MD.E_phi`、`atom_Heff.getP` 或 `local_mode.MD_mode_range`。

本文档不解决：
- effective Hamiltonian 的 shared-basis 构建、样本生成、DFT 数据整理或拟合；这些属于 L3。
- Monte Carlo / PTMC / CG sampling；这些属于 L4。
- 单个字段的默认值、单位、格式、编号规则；这些属于 `skills/knowledge/reference/`。

## 来源边界
本 workflow 是基于 Lecture-5 Cr2O3 / BaTiO3 examples、reference cards、example directory audit 和 source-output audit 整理出的稳定运行契约。运行时只依赖：
- `skills/knowledge/workflows/`
- `skills/knowledge/reference/`
- `skills/subskills/pasp-verifier/skill.md`

Lecture examples、run notes 和源码路径只能作为 authoring 证据；不得把其中的 `SuperCell`、target temperatures、damping constants、time steps、total time、mode count、Slurm 设置或 PASP executable path 当成当前用户任务的默认值。

历史 example 观察、具体实例值和输出家族见：
- `./l5_dynamics_run_notes.md`

用户侧快速检查表见：
- `./l5_dynamics_user_checklist.md`

运行时解释当前 workflow 时，应优先使用本文件中的稳定契约；不要把 run-notes 中的历史实例值直接当成用户当前 workspace 的实时结果。

## 运行状态机（优先级最高）
运行时先读：
- `./l5_dynamics_state_machine.md`

本长文档只补充当前状态所需细节。任何后文步骤、表格、输出清单都不能绕过这些 STOP 条件：
- S3：`USER_CONFIRMED_L5_DYNAMICS_SETTINGS=true`
- S4：`READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- S4：`STAGE_PREFLIGHT_PASS=true`
- S5：explicit user submission authorization before any job submission
- S6：output validation pass before plotting or downstream handoff

## 输入包与运行目录契约
- `input/`：干净、已 preflight 的正式输入基线。`PASP.input` 直接 `%include` 或运行时读取的文件必须在此齐全，或在 README 中明确标注为由上游接入。
- `candidate/`、`notes/`、`drafts/`：待确认 / 待 preflight 的候选材料。不能描述为 submit-ready。
- `runs/<run-id>/`：实际运行目录。每次运行从正式 `input/` 完整复制，再接入 upstream `amp_local_mode` handoff 和提交 helper，只在 run 目录中运行。

不要在 baseline `input/` 里直接跑 PASP。L5 会写出 `temperature.dat`、`energy.dat`、`amp_local_mode.out`、`PASP.used_info`、`*_used.dat`、XSF / diagnostic outputs 和 scheduler logs，容易污染输入基线。

派生 run 目录时要避免把历史输出残留带入新 run。若 `input/` 或 candidate 是从旧 example / complete / previous run 复制来的，先清点文件角色；新 run 只复制当前需要的 `PASP.input`、`MD.input`、direct `%include` files、`local_mode_PM.dat`、`J_best.dat`、`amp_local_mode.in`、条件输入文件和运行 helper。

Smoke-test reduction is allowed only as an explicitly labeled smoke test, not as production validation or a default parameter recommendation. When reducing `SuperCell` for a short run and current settings read an initial state, the `amp_local_mode.in` row count must be consistent with the reduced simulation cell and current local-mode/site basis. Planned MPI ranks must also remain compatible with the current supercell factors before submission is prepared: there must be a decomposition `p1 * p2 * p3 = ranks` with `p1 | n1`, `p2 | n2`, and `p3 | n3`, where `(n1,n2,n3)` are the supercell factors PASP derives from the current `cell` / `unit_cell` relation.

## Generalized new-material input preparation

For a new material, L5 should be treated as a consumer of a prepared `Model atomic_effective_H` package. The agent may help organize and verify the package, but it must not promote historical Cr2O3 or BaTiO3 values into current-material defaults.

| Category | Typical objects | Owner / authority | L5 handling |
|---|---|---|---|
| User scientific intent | branch, active degrees of freedom, smoke-test vs production, output / handoff target | User | Must be explicitly confirmed before formal input, run derivation, or submission preparation |
| Entry inputs | `PASP.input`, `MD.input`, every direct `%include` target | User / upstream / reference-backed edits | Hard-required for the current candidate route; exact writes require reference lookup |
| Structure and basis | `cell.str`, `unit_cell.str`, `SuperCell`, `Z_values`, `Spin_values`, mode definition, mass definition, `fig.maxk`, `fig.mdist`, `Invariant.*`, SOC strategy, mode-info / soft-mode blocks when required | User / upstream structure and model preparation | Same-material / same-basis provenance must be recorded; split vs inline representation follows current `PASP.input` and reference |
| Upstream model products | `local_mode_PM.dat`, `J_best.dat`, optional strain / spin-strain model files | L3 / fitting / user-authoritative model source | Treat as upstream products; do not synthesize or renumber in L5 without authoritative evidence |
| Initial state | first-stage `amp_local_mode.in`, or validated previous-run `amp_local_mode.out` handoff | User / upstream run validation | Required when current settings read an initial state; row count and basis compatibility are preflight checks |
| Conditional physics inputs | `Zeff.dat`, `elastic.dat`, `spin_strain.dat`, `Field_for_Electrocaloric`, other setting-triggered dependencies | Current settings plus reference or user authority | Required only when the active branch/settings establish the dependency; example presence is not enough |
| Runtime helpers | scheduler script, command, executable path, MPI ranks, image / queue / walltime, stdout / stderr paths | User environment | Environment facts only; must be checked before submission preparation but are not scientific defaults |
| Generated outputs | `temperature.dat`, `energy.dat`, `field.dat`, `P_abs.dat`, `amp_local_mode.out`, logs, `PASP.used_info`, `*_used.dat` | Runtime | Never copy into fresh input; validate after run before plotting or handoff |

Agent-derivable artifacts are limited to:
- candidate README / PROGRESS records, file-role inventories, and reference inventory notes;
- include-graph and stale-output inventories;
- clearly labeled smoke-test variants when the user accepts smoke-test intent and reference/user authority supports each exact write;
- formal `input/` and `runs/<run-id>/` only after S3 settings confirmation and S4 read-only preflight pass.

The agent must not derive:
- production physical parameters, field schedules, damping, temperature, timestep, run length, mode counts, masses, or `SuperCell` from examples;
- `local_mode_PM.dat`, `J_best.dat`, `Zeff.dat`, mode definitions, mass definitions, or first-stage `amp_local_mode.in` without upstream evidence;
- submit-ready scripts or external task configuration before preflight flags and explicit submission authorization.

### When the upstream source is L3

If the effective-H package comes from L3, L5 should consume the L3 Step 6 / Step 7 output-validation record and handoff README / PROGRESS as upstream evidence. Historical Lecture examples, run notes, or template filenames are not a substitute for this current-material evidence.

Use the L3 record to map upstream products to L5 requirements:

| L5 requirement | L3 / upstream evidence to look for | L5 interpretation |
|---|---|---|
| `local_mode_PM.dat` | Successful current-material shared-basis / Invariant run under the same structure, mode basis, `fig.maxk`, `fig.mdist`, `Invariant.power` / related powers, and SOC strategy | Upstream model product; usually read through `local_mode.read_interaction T` for dynamics |
| `J_best.dat` or selected fitted-parameter file | Runtime-validated fitting output selected for L5, plus fitting dataset / settings provenance. If values came from L2 four-state DFT, the handoff must include final-`TOTEN` evidence, spin-normalization factor, parameter-id mapping, and `J_best.dat` format check | Fitted / bridged values; numbering must match `local_mode_PM.dat` or the authoritative interaction list, and values must already be in the current model spin basis and units |
| structure and basis | `cell.str`, `unit_cell.str` or equivalent route, `SuperCell`, `Z_values`, `Spin_values`, mode definition, mass definition when used, `fig.maxk`, `fig.mdist`, `Invariant.*`, SOC strategy, and any `fitting.Heff.soft_mode` / mode-info blocks required by the current `atomic_effective_H` package | Must be same-material / same-basis with model files and initial state when read |
| fitting provenance | `Fitting_Dataset.txt`, prediction data, `Fitting_Settings.txt`, lambda scan, keep / skip status, selected run id | Audit evidence for model trust; not normally direct L5 runtime inputs |
| first-stage `amp_local_mode.in` | User / upstream-selected initial state, or candidate from compatible L3-generated `*.amp_local_mode` with provenance | Required only when current settings read an initial state; row count and basis compatibility remain L5 preflight checks |
| `Zeff.dat` | Separate same-basis BEC / polarization upstream evidence | Conditional; required for polarization / electric-field paths only when current settings/reference establish dependency |
| production dynamics settings | User-confirmed L5 settings table | L3 fitting does not choose timestep, damping, temperature, run length, output cadence, field schedule, MPI ranks, or acceptance thresholds |

Before formal L5 input or run derivation, the same-basis check must tie together structure route, `SuperCell`, species / spin values, mode definition, mass definition, `fig.maxk`, `fig.mdist`, `Invariant.*`, SOC strategy, mode-info / `fitting.Heff.soft_mode` requirements, `local_mode_PM.dat`, `J_best.dat`, `local_mode.read_interaction`, `Read_init_spin`, and initial `amp_local_mode.in` when read. If any of these objects changed after the L3 run, treat the handoff as blocked until the user or upstream evidence explains the replacement.

For `atomic_effective_H`, do not assume that `local_mode_PM.dat` and `J_best.dat` alone are enough. If the current package needs shared model-basis settings or `fitting.Heff.soft_mode` / equivalent mode-info blocks to read the effective-H mode information, those settings must appear in `PASP.input` / direct includes or be supplied by a documented upstream-compatible route. A crash such as `read_mode_info: no fitting.Heff.soft_mode block` is a basis-definition failure, not an MD timestep or damping problem.

For pure structural / ferroelectric local-mode MD, the active degrees of freedom should normally be recorded as lattice / displacement only, with `SLD.mode 1` explicitly set and `LLG.method` checked against NVT intent. Do not leave `SLD.mode` implicit, because its default is coupled spin-lattice mode `3`.

For finite-temperature polarization fluctuation or Curie-Weiss-style analysis, system size and sampling length are scientific settings, not example defaults. A small cell such as `2x2x2` may be acceptable only as a labeled smoke test; production analysis must use a user-confirmed larger supercell and trajectory length adequate for the intended statistics.

## Branch routing

| Branch / stage | Primary classifier | Workflow intent | Next gate |
|---|---|---|---|
| Generic new-material MD / ASD / LLG / SLD | User goal plus `Model atomic_effective_H`, `atom_Heff.MD`, active `SLD.mode` / LLG / field controls, and expected outputs | Prepare or validate a material-neutral dynamics package from user/upstream model products | S1 provenance inventory, S3 settings confirmation, then S4 generic preflight |
| Cr2O3 staged SLD | Cr2O3 / Lecture-5 `MD-2` / three-stage heating-relaxation intent | Use the staged `SLD.mode 1/2/3` handoff sequence below | S3 settings confirmation, then S4 Cr2O3 preflight |
| BaTiO3 electric hysteresis | BaTiO3 / Lecture-5 `MD-1` / electric-field / hysteresis / `field.dat` + `P_abs.dat` intent | Single-stage `atomic_effective_H` MD electric-field workflow | S3 settings confirmation, then S4 BaTiO3 preflight |
| Output validation | Completed run with logs and outputs | Check whether outputs can be plotted or handed downstream | S6 output validation |

Generic branch routing is not material-name driven. If the material is neither Cr2O3 nor BaTiO3, classify by model, active degrees of freedom, input files, user goal, and output target. If the user asks for electric-field response in a non-BaTiO3 material, keep it in the generic branch unless they explicitly identify the BaTiO3 historical workflow as the source.

## Cr2O3 branch routing

| Branch / stage | Primary classifier | Workflow intent | Next gate |
|---|---|---|---|
| Stage 1 lattice heating | `SLD.mode 1` | Prepare lattice / displacement subsystem state while spin subsystem is frozen by stage intent | S3 settings confirmation, then S4 preflight |
| Stage 2 spin heating | `SLD.mode 2` | Prepare spin subsystem state while lattice is frozen by stage intent | Validated stage 1 `amp_local_mode.out` required before preflight |
| Stage 3 coupled SLD relaxation | `SLD.mode 3` | Evolve spin and lattice together from validated stage 2 final state | Validated stage 2 `amp_local_mode.out` required before preflight |
| Output validation | Completed run with logs and outputs | Check whether outputs can be plotted or handed downstream | S6 output validation |

`SLD.mode` values and exact semantics must be checked in `skills/knowledge/reference/params/SLD.mode.md` before writing or changing the field.

## Stage input packages

### Generic new-material `atomic_effective_H` candidate package

| 来源 | 文件 / record | 是否硬性必需 | 说明 |
|---|---|---|---|
| 用户 / 上游 | `PASP.input` | 必需 | Selects `Model atomic_effective_H`, structure route, model consumption, includes / inline blocks, high-level package controls, and any shared model-basis settings required to read mode information |
| 用户 / 上游 | `MD.input` | 通常必需 | Required when included or otherwise used for the L5 dynamics driver; controls MD / LLG / ASD / SLD run behavior |
| 用户 / 上游 | `cell.str` / `unit_cell.str` or documented equivalent | 当前 route 必需 | Structure files must match the current basis; exact route follows `PASP.input` reference and user authority |
| L3 / 上游模型 | `local_mode_PM.dat` | setting-dependent but usually required for fitted effective-H dynamics | Upstream interaction / local-mode basis; must match `J_best.dat`, structures, mode basis, `fig.maxk`, `fig.mdist`, `Invariant.*`, and SOC strategy |
| L3 / 上游拟合 | `J_best.dat` | setting-dependent but usually required for fitted effective-H dynamics | Fitted / bridged interaction values; numbering must match `local_mode_PM.dat` or authoritative interaction list, and values must already be in the current model spin basis |
| 用户 / 上游 | mode definition and mass definition | route-dependent | Can be split files or inline blocks; count/order/same-basis checks route through reference before writing |
| 用户 / 上游 | `amp_local_mode.in` | required when the current settings read an initial state | First-stage source is user/upstream-owned; later-stage source must be validated `amp_local_mode.out` handoff |
| 用户 / 上游 | `Zeff.dat` | conditional | Required for polarization/BEC paths such as active electric-field or `atom_Heff.getP` when reference/current settings establish dependency |
| 用户 / 上游 | `elastic.dat`, `spin_strain.dat`, other model files | conditional | Required only when the active settings/reference/user authority establish dependency |
| 环境 | scheduler / run helper / executable plan | submission-preparation gate | Environment helper, not a model input or portable default |
| Agent | README / PROGRESS, reference inventory, smoke-test notes | allowed only as labeled support artifacts | Must record provenance, user confirmations, preflight status, and blocked items |

For generic packages, preflight must answer whether the package is internally consistent for the stated branch. It does not prove the effective Hamiltonian is scientifically valid, that fitted parameters are good, or that production settings are adequate.

For mode masses, exact writes route through `skills/knowledge/reference/params/atom_Heff.MASS_local_mode.md`: all masses should be written as one continuous list in the block, count equals the current local-mode count, and order follows `mode_def.input` / `def_local_modes.dat` / `local_mode-*.xsf` evidence.

### Common required files for Cr2O3 MVP candidate packages

| 来源 | 文件 | 是否硬性必需 | 说明 |
|---|---|---|---|
| 用户 / 上游 | `PASP.input` | 必需 | Selects `Model atomic_effective_H`, includes structure / `MD.input` / split files, and controls model consumption |
| 用户 / 上游 | `MD.input` | 必需 | Controls `atom_Heff.MD`, `SLD.mode`, time step, run length, LLG / MD damping, temperature, output cadence |
| 用户 / 上游 | `cell.str` | 通常必需 | Current simulation structure; exact structure route follows `PASP.input` reference |
| 用户 / 上游 | `unit_cell.str` | 通常必需 | Unit-cell / reference structure; if not used, README must explain structure route |
| L3 / 上游模型 | `local_mode_PM.dat` | `atomic_effective_H` dynamics 通常必需 | Interaction / local-mode basis; should match `J_best.dat`, structure route, mode basis, shared-basis controls, and SOC strategy |
| L3 / 上游拟合 | `J_best.dat` | `atomic_effective_H` dynamics 通常必需 | Fitted / bridged interaction values; numbering must match `local_mode_PM.dat` or corresponding interaction list, and values must already be in the current model spin basis |
| 用户 / 上游 | `amp_local_mode.in` | 必需 for Cr2O3 branch | Stage initial state; stage 2 / 3 source must be validated upstream `amp_local_mode.out` |
| 用户 / 上游 | direct include files | 条件必需 | Any file directly `%include`d by `PASP.input`, such as `mode_def.input` or `mode_mass.input` |
| 用户 / 上游 | `Zeff.dat` | 条件必需 | Needed only when current settings / reference establish polarization-related dependency |
| 用户 / 上游 | `elastic.dat`、`spin_strain.dat` | 条件必需 | Needed only when current settings / reference establish strain / spin-strain dependency |
| 环境 | `run.sh` / `sub_pasp` / scheduler helper | 提交时需要 | Environment helper, not a scientific model input; submit-ready still requires gates and user authorization |

`mode_def.input` and `mode_mass.input` appear in the Cr2O3 historical example as split include files. Their file roles, include-graph checks, row-count / order checks, and verifier expectations are covered by `skills/knowledge/reference/files/mode_def.input.md` and `skills/knowledge/reference/files/mode_mass.input.md`; exact block syntax still routes to `local_mode.mode_definition` and `atom_Heff.MASS_local_mode` param reference before writing.

### Stage-specific handoff

| Stage | `amp_local_mode.in` source | Minimum output needed for next stage |
|---|---|---|
| Stage 1 lattice heating | User-confirmed initial state for the current model | Validated stage 1 `amp_local_mode.out`, `temperature.dat`, `energy.dat`, completion evidence |
| Stage 2 spin heating | Validated stage 1 `amp_local_mode.out`, copied/renamed with run id recorded | Validated stage 2 `amp_local_mode.out`, `temperature.dat`, `energy.dat`, completion evidence |
| Stage 3 coupled SLD relaxation | Validated stage 2 `amp_local_mode.out`, copied/renamed with run id recorded | Validated stage 3 `temperature.dat`, `energy.dat`, `amp_local_mode.out`, completion evidence |

No downstream `amp_local_mode.in` may be overwritten silently. Record:
- upstream run id;
- source `amp_local_mode.out` path;
- output-validation evidence path;
- destination `amp_local_mode.in` path;
- who authorized the handoff or why it is only a draft candidate.

### BaTiO3 electric-hysteresis input package

BaTiO3 uses a single prepared MD run, not Cr2O3 stage 1 -> stage 2 -> stage 3 handoff.

| 来源 | 文件 | 是否硬性必需 | 说明 |
|---|---|---|---|
| 用户 / 上游 | `PASP.input` | 必需 | Selects `Model atomic_effective_H`, includes `MD.input`, structure files, local-mode definition / mass settings, and model-consumption controls |
| 用户 / 上游 | `MD.input` | 必需 | Controls `atom_Heff.MD`, time integration, damping / temperature, electric-field waveform, polarization flag, output cadence, and optional local-mode bounds |
| 用户 / 上游 | `cell.str` | 通常必需 | Current BaTiO3 simulation structure; exact route follows `PASP.input` reference |
| 用户 / 上游 | `unit_cell.str` | 通常必需 | Unit-cell / reference structure used for local-mode and `Zeff.dat` consistency checks |
| L3 / 上游模型 | `local_mode_PM.dat` | `atomic_effective_H` dynamics 通常必需 | Interaction / local-mode basis; should match `J_best.dat`, structure / mode definition, shared-basis controls, and SOC strategy |
| L3 / 上游拟合 | `J_best.dat` | `atomic_effective_H` dynamics 通常必需 | Fitted / bridged interaction values matching the current model basis |
| 用户 / 上游 | `amp_local_mode.in` | 必需 when `Read_init_spin T` or an initial local-mode state is read | Initial local-mode amplitude state; row count must match current `SuperCell` and local-mode/site basis before run derivation |
| 用户 / 上游 | direct include files | 条件必需 | Any file directly `%include`d by `PASP.input`; inline mode definition / mass settings still require param reference before writing |
| 用户 / 上游 | `Zeff.dat` | 条件必需 for polarization path | Required when `atom_Heff.getP T` or active electric-field behavior requires BEC polarization support; check against current `unit_cell.str`, species order, and mode basis |
| 环境 | `run.sh` / `sub_pasp` / scheduler helper | 提交时需要 | Environment helper only; process count, executable path, queue, walltime, and modules are not workflow defaults |

The stable classifier is electric-field / polarization intent under `Model atomic_effective_H`, especially `MD.E_type` or related `MD.E_*` controls plus `field.dat` and `P_abs.dat` output validation. `SLD.mode` may still appear in the MD driver, but BaTiO3 should not be treated as Cr2O3 stage 1 merely because `SLD.mode 1` is present.

Historical Lecture-5 `MD-1` values are stored in run notes. Do not promote observed values such as supercell size, field amplitude, cosine frequency, phase, temperature, damping, total time, output cadence, local-mode bounds, Slurm task count, or PASP executable path to defaults.

For periodic BaTiO3 electric-field plans, explicitly check that the requested `atom_Heff.MD_time` covers the intended field period(s). For the cosine-field branch, use `T = 2*pi / MD.E_omega` only after the current input/reference confirms the frequency units and branch semantics. This is a planning check, not a default value recommendation.

Also check that `MD.aft_step` leaves a nonempty sampled window inside the total MD steps implied by the current `atom_Heff.MD_time` and `MD.Delta_t`. For demonstration loops, `MD.aft_step >= total_steps` means no useful recorded field/polarization window; production runs may intentionally reserve an equilibration window, but that choice must be user-confirmed and reflected in the expected plotting/analysis window.

## Reference-before-write

准备写入或修改任何 PASP 字段、block、文件格式、编号规则时，必须先读对应 reference。常见入口：

| 对象 | Reference |
|---|---|
| `PASP.input` include、structure route、`SuperCell`、`Z_values`、`Spin_values` | `skills/knowledge/reference/topics/PASP.input.md` |
| MD / ASD / SLD 总览 | `skills/knowledge/reference/topics/MD.input.md` |
| `atom_Heff.MD` | `skills/knowledge/reference/params/atom_Heff.MD.md` |
| `MD.Delta_t` | `skills/knowledge/reference/params/MD.Delta_t.md` |
| `atom_Heff.MD_time` | `skills/knowledge/reference/params/atom_Heff.MD_time.md` |
| `SLD.mode` | `skills/knowledge/reference/params/SLD.mode.md` |
| `LLG.method` | `skills/knowledge/reference/params/LLG.method.md` |
| `LLG.damping` | `skills/knowledge/reference/params/LLG.damping.md` |
| `MD.damping` | `skills/knowledge/reference/params/MD.damping.md` |
| `MD.temperature` | `skills/knowledge/reference/params/MD.temperature.md` |
| `MD.init_velocity_temp` | `skills/knowledge/reference/params/MD.init_velocity_temp.md` |
| `MD.aft_step`、`MD.int_step` | `skills/knowledge/reference/params/MD.aft_step.md`, `skills/knowledge/reference/params/MD.int_step.md` |
| `MD.output_amp_lm` | `skills/knowledge/reference/params/MD.output_amp_lm.md` |
| `MD.E_type` | `skills/knowledge/reference/params/MD.E_type.md` |
| `MD.E_x`、`MD.E_y`、`MD.E_z` | `skills/knowledge/reference/params/MD.E_x_MD.E_y_MD.E_z.md` |
| `MD.E_omega` | `skills/knowledge/reference/params/MD.E_omega.md` |
| `MD.E_phi` | `skills/knowledge/reference/params/MD.E_phi.md` |
| `Field_for_Electrocaloric` | `skills/knowledge/reference/params/Field_for_Electrocaloric.md` |
| `atom_Heff.getP` | `skills/knowledge/reference/params/atom_Heff.getP.md` |
| `local_mode.MD_mode_range` | `skills/knowledge/reference/params/local_mode.MD_mode_range.md` |
| `mode_def.input` file role | `skills/knowledge/reference/files/mode_def.input.md` |
| `local_mode.mode_definition` | `skills/knowledge/reference/params/local_mode.mode_definition.md` |
| `mode_mass.input` file role | `skills/knowledge/reference/files/mode_mass.input.md` |
| `atom_Heff.MASS_local_mode` | `skills/knowledge/reference/params/atom_Heff.MASS_local_mode.md` |
| `local_mode_PM.dat` | `skills/knowledge/reference/files/local_mode_PM.dat.md` |
| `J_best.dat` | `skills/knowledge/reference/files/J_best.dat.md` |
| L2 four-state J bridge into `J_best.dat` | `skills/knowledge/reference/topics/four_state_method.md`, `skills/knowledge/reference/files/OUTCAR.md` |
| shared-basis controls consumed from L3 | `skills/knowledge/reference/params/fig.maxk.md`, `skills/knowledge/reference/params/fig.mdist.md`, `skills/knowledge/reference/params/Invariant.power.md` |
| `def_local_modes.dat` | `skills/knowledge/reference/files/def_local_modes.dat.md` |
| `amp_local_mode.in` | `skills/knowledge/reference/files/amp_local_mode.in.md` |
| `cell.str`、`unit_cell.str` | `skills/knowledge/reference/files/cell.str.md`, `skills/knowledge/reference/files/unit_cell.str.md` |
| `Zeff.dat`、`elastic.dat`、`spin_strain.dat` | `skills/knowledge/reference/files/Zeff.dat.md`, `skills/knowledge/reference/files/elastic.dat.md`, `skills/knowledge/reference/files/spin_strain.dat.md` |
| `field.dat`、`P_abs.dat` | `skills/knowledge/reference/files/field.dat.md`, `skills/knowledge/reference/files/P_abs.dat.md` |

如果 reference 没覆盖某个写法，最多写 draft / candidate，并标注需要用户权威来源或 read-only verifier blocked 结论；不得进入 formal input 或 submission preparation。

## Stage 1：Lattice heating (`SLD.mode 1`)

### 当前阶段输入文件
- Candidate or formal stage 1 package with common Cr2O3 files listed above.
- User-confirmed initial `amp_local_mode.in` for the current model.
- User-confirmed dynamics settings table for lattice-heating intent.

### 当前阶段可调整项

| 类别 | 常见对象 | 调整前必须确认 |
|---|---|---|
| stage classifier | `SLD.mode` | Current branch is stage 1 lattice heating; exact value from reference before writing |
| time integration | `MD.Delta_t`、`atom_Heff.MD_time` | runtime cost, stability, smoke-test vs production intent |
| lattice bath / damping | `MD.damping`、`MD.temperature`、`MD.init_velocity_temp` | user-confirmed heating target and ensemble intent |
| spin integration guard | `LLG.method`、`LLG.damping` | stage 1 intent should not accidentally heat spin subsystem |
| output cadence | `MD.aft_step`、`MD.int_step`、`MD.output_amp_lm` | expected output size and validation needs |
| model package | `local_mode_PM.dat`、`J_best.dat`、mode / mass split files | same-basis provenance and reference coverage |

### 修改后要检查什么
- `SLD.mode` matches stage 1 intent.
- `PASP.input` includes resolve inside the candidate package.
- `MD.input` settings match the user-confirmed table; no historical example value is presented as a default.
- `amp_local_mode.in` is the confirmed initial state, not an unrecorded file from another stage or old run.
- Candidate remains marked not submit-ready until S4 preflight passes.

### 预期输出与 handoff
Minimum validation targets:
- completion log evidence;
- `PASP.used_info`;
- `temperature.dat`;
- `energy.dat`;
- `amp_local_mode.out`.

Stage 1 handoff to stage 2 requires output validation pass, then `amp_local_mode.out` may be copied/renamed as stage 2 `amp_local_mode.in` with provenance recorded.

## Stage 2：Spin heating (`SLD.mode 2`)

### 当前阶段输入文件
- Candidate or formal stage 2 package with common Cr2O3 files listed above.
- `amp_local_mode.in` copied/renamed from validated stage 1 `amp_local_mode.out`.
- User-confirmed dynamics settings table for spin-heating intent.

### 当前阶段可调整项

| 类别 | 常见对象 | 调整前必须确认 |
|---|---|---|
| stage classifier | `SLD.mode` | Current branch is stage 2 spin heating; exact value from reference before writing |
| time integration | `MD.Delta_t`、`atom_Heff.MD_time` | runtime cost, stability, smoke-test vs production intent |
| spin bath / damping | `LLG.method`、`LLG.damping`、`MD.temperature` | user-confirmed spin-heating target and LLG method intent |
| lattice guard | `MD.damping`、`MD.init_velocity_temp` | stage 2 intent should not accidentally heat lattice subsystem |
| output cadence | `MD.aft_step`、`MD.int_step`、`MD.output_amp_lm` | expected output size and validation needs |
| handoff | `amp_local_mode.in` | validated stage 1 source path, run id, and evidence |

### 修改后要检查什么
- `SLD.mode` matches stage 2 intent.
- Stage 1 output validation evidence exists before using its `amp_local_mode.out`.
- The stage 2 `amp_local_mode.in` provenance is recorded before overwrite or promotion.
- `MD.input` settings match the user-confirmed table; no historical example value is presented as a default.
- Candidate remains marked not submit-ready until S4 preflight passes.

### 预期输出与 handoff
Minimum validation targets:
- completion log evidence;
- `PASP.used_info`;
- `temperature.dat`;
- `energy.dat`;
- `amp_local_mode.out`.

Stage 2 handoff to stage 3 requires output validation pass, then `amp_local_mode.out` may be copied/renamed as stage 3 `amp_local_mode.in` with provenance recorded.

For `SLD.mode 2`, do not validate handoff by requiring `amp_local_mode.out` to be byte-identical to `amp_local_mode.in`. In observed smoke testing, spin-vector fields changed while local-mode / lattice fields stayed unchanged; branch-consistent validation should focus on successful completion, spin temperature / spin diagnostic evolution, frozen-lattice indicators, row-count consistency, and provenance for the final `amp_local_mode.out`.

## Stage 3：Coupled SLD relaxation (`SLD.mode 3`)

### 当前阶段输入文件
- Candidate or formal stage 3 package with common Cr2O3 files listed above.
- `amp_local_mode.in` copied/renamed from validated stage 2 `amp_local_mode.out`.
- User-confirmed dynamics settings table for coupled spin-lattice relaxation intent.

### 当前阶段可调整项

| 类别 | 常见对象 | 调整前必须确认 |
|---|---|---|
| stage classifier | `SLD.mode` | Current branch is stage 3 coupled SLD relaxation; exact value from reference before writing |
| time integration | `MD.Delta_t`、`atom_Heff.MD_time` | runtime cost, stability, energy-drift risk, smoke-test vs production intent |
| coupled dynamics | `LLG.method`、`LLG.damping`、`MD.damping`、`MD.temperature`、`MD.init_velocity_temp` | whether the run is intended as coupled relaxation, NVE-like dynamics, or another user-confirmed ensemble |
| output cadence | `MD.aft_step`、`MD.int_step`、`MD.output_amp_lm` | expected output size and validation needs |
| handoff | `amp_local_mode.in` | validated stage 2 source path, run id, and evidence |

### 修改后要检查什么
- `SLD.mode` matches stage 3 intent.
- Stage 2 output validation evidence exists before using its `amp_local_mode.out`.
- Damping / temperature / initial velocity choices match the user-confirmed ensemble intent.
- If the user expects NVE-like coupled relaxation, output validation must report `energy.dat` total-energy drift / range as evidence; the workflow does not define hidden acceptance thresholds.
- Candidate remains marked not submit-ready until S4 preflight passes.

### 预期输出与 handoff
Minimum validation targets:
- completion log evidence;
- `PASP.used_info`;
- `temperature.dat`;
- `energy.dat`;
- `amp_local_mode.out`.

Stage 3 outputs can be handed to plotting or scientific review only after S6 output validation pass.

## Output validation details

For Cr2O3 MVP, output validation should check only the current run directory and formal input provenance, not sibling examples or run notes.

Minimum checks:
- Normal PASP completion evidence in log / scheduler output.
- `PASP.used_info` should be checked when present, but sparse or incomplete `PASP.used_info` is not a standalone failure. If it lacks effective-setting details, record that limitation and cross-check `MD.input`, `PASP.input`, completion log evidence, and output files instead.
- `temperature.dat` exists and has subsystem columns sufficient to identify spin and lattice temperatures.
- `energy.dat` exists and has a usable time / energy series.
- `temperature.dat` and `energy.dat` headers match the expected sampled-series role, and data rows have monotonic sampled step / time values consistent with the output cadence actually present.
- Do not require the sampled `temperature.dat` or `energy.dat` rows to include the final MD step exactly. Completion evidence and the sampled rows can be consistent even when the last written sample precedes the final step.
- `amp_local_mode.out` exists and is the candidate final state from this run.
- Stage-specific qualitative check:
  - stage 1: lattice column behavior is relevant; spin column should be interpreted according to stage intent and actual output.
  - stage 2: spin column behavior is relevant; lattice column should be interpreted according to stage intent and actual output.
  - stage 3: spin and lattice temperature / diagnostic columns should evolve or otherwise be evaluated together for branch-consistent validation.
- For NVE-like coupled relaxation, report `energy.dat` total-energy drift / range as evidence. Do not judge it against an implicit threshold unless the user provides one.
- Scientific acceptance of target temperatures, relaxation quality, or energy drift remains user-owned unless the user provides thresholds.

Do not use output validation to retroactively authorize an unconfirmed input, stale `amp_local_mode.in`, missing preflight, or submission without explicit authorization.

## BaTiO3 electric hysteresis branch

### 当前阶段输入文件
- Candidate or formal BaTiO3 package with the BaTiO3 files listed above.
- User-confirmed electric-field / polarization settings table.
- Same-basis evidence for structure, local-mode model files, initial local-mode amplitudes, and `Zeff.dat` when polarization output is active.

### 当前阶段可调整项

| 类别 | 常见对象 | 调整前必须确认 |
|---|---|---|
| branch classifier | `Model`, `atom_Heff.MD`, electric-field intent | Current branch is BaTiO3 electric hysteresis, not Cr2O3 stage 1 / 2 / 3 |
| time integration | `MD.Delta_t`, `atom_Heff.MD_time` | runtime cost, stability, smoke-test vs production intent |
| bath / damping | `MD.damping`, `LLG.damping`, `MD.temperature`, `MD.init_velocity_temp` | user-confirmed ensemble and temperature intent |
| electric-field waveform | `MD.E_type`, `MD.E_x/y/z`, `MD.E_omega`, `MD.E_phi`, `Field_for_Electrocaloric` | exact reference coverage, unit/semantics gaps, and user-confirmed physical field plan |
| polarization output | `atom_Heff.getP`, `Zeff.dat` | BEC data exists and matches current structure / unit cell / mode basis |
| local-mode bounds | `local_mode.MD_mode_range` | exact row/component scope from reference or user authority; lower <= upper |
| output cadence | `MD.aft_step`, `MD.int_step`, `MD.output_amp_lm` | expected output size and validation needs |
| model package | `local_mode_PM.dat`, `J_best.dat`, mode / mass definition, `amp_local_mode.in` | same-basis provenance and row-count consistency |

### 修改后要检查什么
- `PASP.input` direct includes resolve inside the candidate package.
- `MD.input` settings match the user-confirmed table; MD-1 historical values are not described as defaults.
- `atom_Heff.getP` / active electric-field path and `Zeff.dat` provenance are consistent before expecting valid `P_abs.dat`.
- For periodic/cosine field runs, `atom_Heff.MD_time` covers the intended period(s) and `MD.aft_step` leaves a nonempty sampled window for the desired loop; demo-vs-production equilibration intent is explicitly recorded.
- `SuperCell` and `amp_local_mode.in` row count match the current basis, especially after smoke-test reduction.
- Planned MPI ranks and scheduler helper are compatible with the run plan before submission preparation; for `atomic_effective_H` MD this means a valid `p1 * p2 * p3 = ranks` factorization against the current supercell factors.
- Candidate remains marked not submit-ready until S4 preflight passes.

### 预期输出与分析 handoff
Minimum validation targets:
- completion log evidence;
- `PASP.used_info` or combined formal input + log + output evidence;
- `field.dat`;
- `P_abs.dat`.

Optional diagnostics:
- `energy.dat`;
- `temperature.dat`;
- `amp_local_mode.out`;
- warning / stderr and scheduler logs.

Hysteresis plotting is a post-validation analysis step. First validate that `field.dat` and `P_abs.dat` come from the same run and expose aligned sampled step/time series, not only compatible row counts. Then plot the user-confirmed polarization component versus the corresponding electric-field component, for example `P_x` vs `E_x` when that is the selected analysis axis. Report whether the result is a workflow/plotting demonstration or a production scientific analysis; one-period demos can validate the mechanics of the branch and plot but do not establish convergence, equilibration, finite-size adequacy, or acceptance thresholds.

## Generic new-material branch

### 当前阶段输入文件
- Candidate or formal generic L5 package with the generic files listed above.
- User-confirmed branch target: MD, LLG / ASD, SLD, electric-field / polarization response, smoke test, production run, output validation, or handoff.
- Same-basis evidence for structure, `local_mode_PM.dat`, `J_best.dat`, mode definition, mass definition, species / spin values when applicable, and initial state when current settings read one.
- Conditional-file evidence for `Zeff.dat`, `elastic.dat`, `spin_strain.dat`, or branch-specific blocks only when active settings require them.

### 当前阶段可调整项

| 类别 | 常见对象 | 调整前必须确认 |
|---|---|---|
| branch classifier | `Model`, `atom_Heff.MD`, active `SLD.mode`, LLG / ASD controls, electric-field controls | User-confirmed dynamics intent and active degrees of freedom |
| time integration | `MD.Delta_t`, `atom_Heff.MD_time` | runtime cost, stability risk, smoke-test vs production intent |
| bath / damping / ensemble | `LLG.method`, `LLG.damping`, `MD.damping`, `MD.temperature`, `MD.init_velocity_temp` | user-confirmed physical ensemble and target subsystem |
| output cadence | `MD.aft_step`, `MD.int_step`, `MD.output_amp_lm`, field / polarization output target | expected output size, plotting / handoff needs, and validation target |
| finite-size / statistics | `SuperCell`, trajectory length, equilibration / sampling window | user-confirmed analysis target; small cells are smoke tests unless accepted by the user |
| model package | `local_mode_PM.dat`, `J_best.dat`, mode / mass definition, structure files | upstream same-basis provenance; no example-derived model files |
| initial state | `amp_local_mode.in` when current settings read one | first-stage user/upstream authority or validated previous-run handoff |
| conditional physics | `Zeff.dat`, `elastic.dat`, `spin_strain.dat`, `Field_for_Electrocaloric`, `local_mode.MD_mode_range` | active settings plus reference/user authority; exact writes require reference |
| run environment | command, MPI ranks, scheduler / image / executable | environment compatibility before submission preparation |

### 修改后要检查什么
- `PASP.input` direct includes resolve inside the candidate package, with duplicate / inactive declarations reported.
- Every written keyword, block, file format, numbering rule, and conditionally required file has reference coverage or user-authoritative evidence.
- Dynamics settings match the user-confirmed table and are not inherited from Cr2O3 or BaTiO3 examples.
- If current settings read an initial state, `SuperCell`, `amp_local_mode.in`, mode basis, and planned MPI ranks remain compatible, especially for smoke-test reductions; ranks must factor into three process-grid dimensions that divide the current supercell factors.
- For polarization-fluctuation statistics, smoke-test cells must not be promoted to production evidence unless the user explicitly accepts the finite-size and sampling limitations.
- Candidate remains marked not submit-ready until S4 generic input preflight passes.

### 预期输出与 handoff
Generic output validation is branch-specific:
- MD / SLD thermal or relaxation targets usually validate completion, `temperature.dat`, `energy.dat`, logs, and `amp_local_mode.out` when handoff is expected.
- Electric-field / polarization targets validate same-run field and polarization outputs, plus `Zeff.dat` provenance, before plotting.
- Optional diagnostics do not replace the declared primary validation target.

The workflow reports what outputs are present and internally consistent. Scientific acceptance thresholds, convergence, finite-size adequacy, and production readiness remain user-owned unless the user provides explicit criteria.

## 任务目标 -> 推荐调整方向

| 目标 | 优先考虑 | 不要先做 |
|---|---|---|
| 打通 L5 branch / smoke test | 明确标记 short-run / smoke-test settings；先验证 include、MD input 解析、核心输出产生 | 把 smoke-test settings 写成 production relaxation |
| 新材料 L5 input preparation | 先确认 branch、上游 model provenance、initial state、conditional files、reference inventory 和 preflight target | 从 Cr2O3 / BaTiO3 examples 自动套 model files、超胞、时间步、温度、阻尼或提交脚本 |
| Stage 1 lattice heating | 确认 `SLD.mode 1`、lattice damping / temperature intent、initial state provenance | 直接套 Lecture-5 stage 1 数值 |
| Stage 2 spin heating | 先验证 stage 1 output and `amp_local_mode` handoff，再确认 spin damping / temperature intent | 在未验证 stage 1 的情况下覆盖 stage 2 `amp_local_mode.in` |
| Stage 3 coupled relaxation | 先验证 stage 2 output and handoff，再确认 coupled SLD / ensemble intent and output checks | 在未定义能量漂移判断的情况下声称 relaxation 已科学达标 |
| 绘图或分析 `temperature.dat` | 先做 output validation，确认 columns, run provenance, and stage branch | 只因文件存在就画图或 handoff |
| 复现实例 | 用 run notes 理解历史文件家族和 stage order | 把 historical target temperatures, time steps, damping, supercell, or scheduler settings 当默认值 |
| BaTiO3 electric hysteresis | 先确认 electric-field schedule、polarization path、`Zeff.dat` provenance、field/P_abs validation target | 把 Lecture-5 MD-1 values or Slurm helper 当 production defaults |
| 绘制 hysteresis | 先验证 same-run `field.dat` + `P_abs.dat`，再按用户确认组件画 `P` vs `E` | 只因两个文件名存在就混用 output/complete/sibling run |

## Templates and deferred assets

当前 MVP 不新增 Cr2O3 template package。原因：
- Lecture-5 example establishes a stable three-stage workflow shape and file roles.
- Its concrete model files, structure settings, mode counts, masses, target temperatures, damping, time steps, total times, and scheduler helper are material- and environment-specific historical values.
- A reusable template would need placeholders plus reference-backed file cards for every split include and user-confirmed parameter table; that is outside this MVP.

Runtime agents may summarize the required stage package and help prepare draft / candidate files only after reference-before-write checks. They must not copy a historical `complete/` directory as a fresh input or claim that example values are production defaults.

## L5 branch separation

Keep L5 branch boundaries separate:
- Cr2O3: three-stage `SLD.mode 1/2/3` spin-lattice relaxation with `amp_local_mode.out` handoff between stages.
- BaTiO3: one prepared electric-field MD run, with `field.dat` and `P_abs.dat` as the primary validation / plotting pair.
- Generic/new-material: material-neutral `atomic_effective_H` dynamics package whose branch, active degrees of freedom, upstream products, conditional files, initial state, and output targets must be confirmed from current-material evidence.

Do not reuse BaTiO3 field-driving settings for Cr2O3 SLD, and do not use the Cr2O3 handoff checklist to validate BaTiO3 hysteresis outputs.
