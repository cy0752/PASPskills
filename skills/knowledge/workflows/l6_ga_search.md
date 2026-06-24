# Workflow: L6 GA Global Structure Search

> 本 workflow 面向 `Model GA` 的全局结构搜索。正式写 input、派生 run、准备提交或提交前，必须先读 sibling `l6_ga_search_state_machine.md` 并执行其 STOP gate。

## 目标
使用 PASP GA 模块生成、弛豫和筛选候选结构，寻找低能结构或满足用户约束的候选稳定结构。

L6 常见分支包括：
- random / plain structure search：结构框架未知，靠随机结构或随机空间群生成初始种群。
- perturbation structure search：已有结构框架，围绕当前结构或空间群扰动生成候选。
- magnetic GA search：结构搜索同时处理磁构型、磁矩读取或磁性结构比较。
- restart / saved-structure branch：从历史 `strs_saved.dat`、generation-suffixed `CONTCAR` / `OSZICAR` 等继续。
- fixed-lattice / constrained-cell / interface branch：用户明确约束晶格、晶胞、二维应变、表面 / 界面等。

本文档不回答单个字段默认值、精确格式、block 行数、编号规则或文件语法。这些必须转到 `skills/knowledge/reference/`，尤其是写入或修改任何 PASP 字段、block、文件格式、编号规则之前。

## 来源边界
本 workflow 是基于 Lecture-6 slides / examples、当前 reference cards 和 PASP / Latticemodel source audit 整理出的稳定运行契约。运行时只依赖：
- `skills/knowledge/workflows/`
- `skills/knowledge/reference/`
- `skills/subskills/pasp-verifier/skill.md`

Lecture examples、run notes、helper scripts 和源码路径只能作为 authoring 证据。不要把其中的 `SuperCell`、population size、generation count、VASP INCAR / KPOINTS / POTCAR、Slurm partition、PASP executable path、VASP path、job id、candidate energies 或 symmetry labels 当成当前用户任务的默认值。

历史 example 观察、输出家族和 source-audit 线索见：
- `./l6_ga_search_run_notes.md`

## 运行状态机（优先级最高）
运行时先读：
- `./l6_ga_search_state_machine.md`

本长文档只补充当前状态所需细节。任何后文步骤、表格、输出清单都不能绕过这些 STOP 条件：
- S3：`USER_CONFIRMED_L6_GA_SETTINGS=true`
- S4：`READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- S4：`STAGE_PREFLIGHT_PASS=true`
- S5：explicit user submission authorization before any job submission
- S6：output validation pass before low-energy handoff, post-GA optimization claims, plotting, or symmetry reporting

## 输入包与运行目录契约
- `drafts/` / `notes/`：草稿、研究记录、候选设置表，不可提交。
- `candidate/`：待确认 / 待 preflight 的 L6 输入包。可以整理文件角色、reference inventory 和 helper 脚本计划，但不能描述为 submit-ready。
- `input/`：干净、已 preflight 的正式输入基线。`PASP.input` 直接 `%include` 或运行时读取的文件必须在此齐全，或在 README 中明确标注为由上游接入。
- `runs/<run-id>/`：实际运行目录。每次运行从正式 `input/` 完整复制，再接入外部评价 helper、scheduler / command plan，只在 run 目录中运行。

不要在 baseline `input/` 里直接跑 PASP。L6 会写出 candidate POSCAR、generation-suffixed DFT artifacts、low-energy summaries、saved structures、`strs_saved.dat`、`PASP.used_info`、seed files、helper logs 和 scheduler logs，容易污染输入基线。

## Branch Routing

| Branch | Primary classifier | Workflow intent | Next gate |
|---|---|---|---|
| Plain / random search | User wants global search without a known framework; `GA.perturbation F` or no perturbation branch; optional random-spacegroup disabled | Generate broad initial population, then GA evolve / relax | S1 inventory, S3 settings confirmation, S4 preflight |
| Random space group | `GA.gen_ran_str_sym T` or user asks random space group | Generate initial structures from a space-group range | Confirm `GA.spg_front/rear`, composition, volume / cell policy, then preflight |
| Perturbation search | `GA.perturbation T` or user has known framework / perovskite / epitaxial structure | Perturb a meaningful structure framework | Confirm structure route, perturbation intent, constraints, then preflight |
| Magnetic GA | `GA.magnetic T`, magnetic order search, `Spin_values`, magnetic helper scripts, `MAGMOM_*`, or magnetic OUTCAR read | Search structure plus magnetic configuration policy | Confirm magnetic policy and VASP magnetic support, then preflight |
| Restart / saved structures | `GA.read_strs_saved T`, `GA.read_CONTCAR T`, `GA.read_OSZICAR T`, or user wants continue | Continue from same-run saved artifacts | Validate restart artifacts and generation provenance before preflight |
| Fixed / constrained / interface | `GA.fixlattice`, `GA.fix_cell`, `GA.biaxial_strain`, `GA.system interface`, `GA.surfaces`, surface / interface goal | Constrained structure search | Confirm physical constraint and conditional files / blocks, then preflight |
| Output validation | Completed run with logs and outputs | Decide whether outputs can be used or handed to optimization / analysis | S6 output validation |

Branch classification is not material-name driven. Si, NaNbO3 and BiFeO3 examples only show historical package shapes.

## Stage Input Packages

### Core PASP GA candidate package

| 来源 | 文件 / setting | 是否硬性必需 | 说明 |
|---|---|---|---|
| User / upstream / agent draft | `PASP.input` | 必需 | Must explicitly select `Model GA`; exact fields, blocks, includes and defaults require reference before writing |
| User / upstream | Structure route: `cell.str` / `unit_cell.str`, inline blocks, or POSCAR route | 当前 route 必需 | The Lecture-6 package uses `%include cell.str` and `%include unit_cell.str`; other routes are allowed only when reference/user authority establishes them |
| User / upstream | `%block SuperCell` | Usually required in Lecture-style packages | Must be material and branch specific; do not copy example matrices |
| User / upstream | `%block Z_values` | Usually required for material species | Must match species order in the current structure route; exact syntax routes to reference |
| User / upstream | `%block Spin_values` | Magnetic / spin-aware routes only | Required only when current magnetic settings or structure route require it; count/order checks route to reference |
| User / upstream | GA evolution controls | Required for an intentional run | `GA.population_size`, `GA.max_generation`, `save_str.nsave_str`, heredity/mutation and selection controls need user-confirmed intent |
| User / upstream | Branch controls | Branch dependent | `GA.perturbation`, `GA.gen_ran_str_sym`, magnetic flags, restart flags, constraints, `GA.parallel` and external command policy must match user goal |
| User / upstream | `seed.in` | Optional | Reproducibility helper; if present, exact format routes to reference |
| Environment / user | External evaluator inputs / command | Required when local optimization is external | VASP / GULP inputs, `GA.VASPCMD` for `GA.parallel F`, or `run_pvasp.sh` for `GA.parallel T` are environment facts, not workflow defaults |
| Environment / user | Scheduler helpers | Submission only | `pasp.slurm`, `vasp.slurm`, `vasp.pbs`, image / queue / path / module / MPI facts are not scientific defaults |
| Agent | README / PROGRESS, reference inventory, preflight record | Required for formalization | Records branch, file roles, user confirmations, reference gaps and preflight status |

### Conditional files and blocks

| Trigger | Conditional dependency / output expectation | Handling |
|---|---|---|
| `PASP.input` has `%include <file>` | The include target must exist in the candidate package and be regular/readable | Input preflight starts from root `PASP.input`, resolves include graph and catches inactive duplicates |
| `GA.gen_ran_str_sym T` | `GA.spg_front` / `GA.spg_rear`; possible volume / structure placeholders | User must confirm space-group range and physical scope; branch-specific structure looseness is high-risk |
| `GA.perturbation T` | Meaningful current structure framework | Current structure must be user/upstream-owned; do not use arbitrary coordinates from random-spacegroup notes |
| `GA.parallel F` | Nonempty, user-confirmed `GA.VASPCMD`; serial / one-by-one VASP command behavior | Block preflight if VASP optimization is needed but `GA.VASPCMD` is empty, stale, or not current-environment confirmed |
| `GA.parallel T` | `run_pvasp.sh` or equivalent parallel external-evaluation helper; `vasp_N/` runtime provenance | Helper script and VASP inputs are environment-specific and must be checked before submission |
| `GA.Pher` / `GA.Pmut` set | Heredity / mutation / remaining-operation balance | Check `GA.Pher + GA.Pmut`: `> 1` is invalid-risk; `< 1` leaves a `Pperm` remainder and must be user-intended |
| Magnetic branch | `Spin_values`, magnetic GA flags, possible `MAGMOM_*`, magnetic-aware helper, spin-polarized DFT inputs | User confirms magnetic policy; helper must support the selected magnetic workflow |
| `GA.lread_OUTCAR_mag T` | `GA.magnetic T` plus readable `OUTCAR` magnetic moments after external run | Block unless magnetic branch and OUTCAR availability are established |
| Restart from saved structures | `strs_saved.dat`, `CONTCAR.NNN.GGG`, `OSZICAR.NNN.GGG`, generation number / saved-state provenance | Treat as restart branch, not fresh input; validate same-run provenance |
| `GA.system interface` | `%block GA.surfaces` | Conditional hard dependency for interface branch; do not require for bulk GA |
| Fixed lattice / cell / 2D strain | `GA.fixlattice`, `GA.fix_cell`, `GA.biaxial_strain`, `GA.lat_fix_2D_Ang`, related constraints | High-risk physical constraints; confirm with user and reference before writing |

## Typical Stage IO

| State / stage | Required inputs | Expected outputs | Downstream use |
|---|---|---|---|
| S0 inventory | User target directory, task goal | File-role inventory, likely branch, uncertainty list | Decides whether L6 applies and what evidence is missing |
| S1 branch / package inventory | Current `PASP.input`, structure route, helper scripts, existing outputs if any | Branch classification, file-role table, stale-output list | Feeds candidate package planning |
| S2 candidate package | Draft `PASP.input`, direct include files, current structure, optional seed, external evaluator plan | Candidate files plus README / PROGRESS; not submit-ready | Input preflight target |
| S3 settings confirmation | Candidate setting table, user scientific objective, external evaluator plan | `USER_CONFIRMED_L6_GA_SETTINGS=true` | Required before formal input / run derivation |
| S4 input preflight | Exact candidate package, user confirmation record, reference inventory | pass / fail / blocked with evidence | Required before formal input / run / submission prep |
| S5 formal input and run | Preflight-passed `input/`, run helper, executable / scheduler facts, explicit submission authorization | `runs/<run-id>/` with copied clean inputs and runtime helpers | Actual PASP / external evaluation run |
| S6 output validation | Same-run logs, `PASP.used_info`, generated structures, DFT artifacts, saved low-energy files | pass / fail / blocked; handoff-allowed facts | Enables post-GA optimization, analysis, or restart |
| S7 handoff / postprocess | Validated saved structures, low-energy summaries, optional `opt/` outputs | Candidate list, optimization / symmetry-analysis record | User reporting or next calculation stage |

## Adjustable Settings By Goal

These are workflow-level knobs only. Before writing or changing exact values, read the corresponding reference card or ask the user for authoritative settings.

| User goal | First workflow knobs to discuss | High-risk checks |
|---|---|---|
| Quick smoke test | smaller `GA.population_size`, `GA.max_generation`, `save_str.nsave_str`, short external evaluator plan | Must be labeled smoke test; do not call outputs production-quality |
| Production search | population / generations, heredity / mutation balance, saved-structure count, external evaluator convergence | User owns budget / accuracy tradeoff; examples are not defaults |
| Broader structural exploration | random-spacegroup branch, `GA.spg_front/rear`, perturbation off/on, mutation behavior | Composition, volume/cell policy and structure route must be confirmed |
| Known-framework search | `GA.perturbation`, constraints, `SuperCell`, symmetry / similarity filtering | Current structure framework must be meaningful and same-material |
| Magnetic search | `GA.magnetic`, `GA.random_magnetic`, `GA.lAFM_GA`, `GA.lmut_mag_GA`, `GA.flip_spin_rate`, `GA.lread_OUTCAR_mag`, `Spin_values` | Magnetic DFT inputs and helper must support the chosen policy |
| Avoid duplicate structures | `GA.useBCM`, `GA.tol_BCM`, `GA.lchk_mut`, `str.init_sym`, `GA.symmetrize_str` | Exact semantics / thresholds route to reference; do not hide bad structures with loose filters |
| Parallel external evaluation | `GA.parallel`, `run_pvasp.sh`, VASP / GULP command, scheduler facts | Helper layout and output filenames are run-environment facts |
| Fixed lattice / pressure / strain | `GA.fixlattice`, `GA.fix_cell`, `GA.pressure`, `GA.biaxial_strain`, `GA.lat_fix_2D_Ang` | High-risk physics constraints; `GA.fix_cell` source default caveat applies |
| Restart a GA run | `GA.read_strs_saved`, `GA.read_CONTCAR`, `GA.read_OSZICAR`, `GA.generation_saved` | Same-run generation artifacts and saved-state provenance must be validated |

### GA Scale Sanity Guidance

The source/reference defaults for `GA.population_size`, `GA.max_generation` and `save_str.nsave_str` must not be treated as automatic system-size scaling. The runtime agent should ask the user to confirm these values for the current branch and budget.

| Intent | Scale guidance | Required label / warning |
|---|---|---|
| Smoke test | Very small population or generation counts, such as population `10` or generation `2`, only check wiring and helper behavior | Must be explicitly labeled smoke-test; do not report GA convergence or production low-energy claims |
| Modest known-framework perturbation | Search space is smaller; a user-confirmed starting point such as `GA.population_size 20`, `GA.max_generation 10`, `save_str.nsave_str 20` can be reasonable for small systems | Still requires user confirmation and current-structure provenance |
| Broader global search | Usually needs branch-specific scale discussion, not copied defaults | Confirm atom count, composition, random-spacegroup / perturbation policy, external evaluator cost and stopping criteria |

For heredity/mutation, a common robust practice is to keep `GA.Pher + GA.Pmut = 1` when no remainder operation is intended, for example `0.75/0.25` or `0.80/0.20`. This is a workflow guardrail, not a replacement for the reference defaults.

## Reference-before-write Inventory

Before generating or editing an L6 `PASP.input`, build an inventory of every explicit keyword, block, include and read file. Common reference entry points:

| Object | Reference path |
|---|---|
| Model route | `skills/knowledge/reference/params/Model.md` |
| PASP.input syntax, `%include`, blocks, duplicate first-wins behavior | `skills/knowledge/reference/topics/PASP.input.md` |
| GA module overview | `skills/knowledge/reference/modules/ga.md` |
| Structure files | `skills/knowledge/reference/files/cell.str.md`, `skills/knowledge/reference/files/unit_cell.str.md` |
| Optional seed | `skills/knowledge/reference/files/seed.in.md` |
| Species / spin / supercell blocks | `skills/knowledge/reference/params/Z_values.md`, `Spin_values.md`, `SuperCell.md` |
| Evolution scale | `GA.population_size.md`, `GA.max_generation.md`, `save_str.nsave_str.md` |
| Genetic operations | `GA.Pher.md`, `GA.Pmut.md`, `GA.perturbation.md`, `GA.lchk_mut.md` |
| Symmetry / similarity / cutoff | `str.init_sym.md`, `GA.symmetrize_str.md`, `GA.useBCM.md`, `GA.tol_BCM.md`, `rmax_cut.md` |
| Parallel / pressure | `GA.parallel.md`, `GA.VASPCMD.md`, `GA.pressure.md` |
| Parallel VASP helper | `skills/knowledge/reference/files/run_pvasp.sh.md` |
| Random space group | `GA.gen_ran_str_sym.md`, `GA.spg_front.md`, `GA.spg_rear.md` |
| Magnetic search | `GA.magnetic.md`, `GA.random_magnetic.md`, `GA.lAFM_GA.md`, `GA.lmut_mag_GA.md`, `GA.flip_spin_rate.md`, `GA.ldiff_str_with_mag_GA.md`, `GA.lread_OUTCAR_mag.md` |
| Cell / lattice constraints | `GA.fixlattice.md`, `GA.fix_cell.md`, `GA.biaxial_strain.md`, `GA.lat_fix_2D_Ang.md` |
| Effective settings output | `skills/knowledge/reference/files/PASP.used_info.md` |

Known reference gaps: several source-backed or example-observed L6 controls and output artifacts do not yet have dedicated cards, including restart controls, `GA.system`, `GA.surfaces`, `GA.Vcell_init`, `GA.Nadapt`, `GA.Wadapt`, random-spacegroup layer controls, and GA output files such as `Saved_NNN.POS`, `Saved_gen.dat`, `low_ene_strs.dat`, `pc_low_ene_strs.dat`, `strs_saved.dat`, `POSCAR.NNN.GGG`, `CONTCAR.NNN.GGG`, `OSZICAR.NNN.GGG`, `OUTCAR.NNN.GGG`, `MAGMOM.NNN.GGG`, and `vasp_N/`. Do not write those exact settings or claim their file formats as reference-backed unless the user supplies authority or new reference cards are added.

## External VASP Evaluator Guidance

GA structure relaxation/evaluation is an external DFT or optimizer responsibility. The workflow can check that the external evaluator is explicitly planned, but it must not invent production VASP settings.

Required confirmations:
- `GA.parallel F`: `GA.VASPCMD` is present, nonempty, and runnable in the target environment; stdout/stderr and timeout/failure behavior are understood.
- `GA.parallel T`: `run_pvasp.sh` exists in the run directory, matches current candidate naming, waits for jobs to finish, reports failures, and leaves `CONTCAR` / `OSZICAR` / `OUTCAR` / magnetic outputs where PASP expects them.
- `INCAR`, `KPOINTS`, `POTCAR`, scheduler script and VASP executable path come from the user, current project, or an explicitly accepted settings table.

DFT-side recommendations to discuss, not silently apply:
- For GA, the lattice can fluctuate between candidates. An automatic-length `KPOINTS` style is often safer than a fixed mesh that was tuned for one cell.
- Multi-stage relaxation is often preferred: start with looser `PREC` / `EDIFF` / `EDIFFG` / automatic k-point length, then tighten in later stages.
- Values such as automatic lengths `5`, `10`, `15` and staged `PREC=NORMAL/ACCURATE` can be useful starting points only when the user accepts them for the current material and budget.

## Input Preflight Checklist

Use `skills/subskills/pasp-verifier/skill.md`, `mode: input-preflight`, before promoting candidate files to formal `input/`, deriving `runs/<run-id>/`, creating / editing submit-ready helper artifacts, preparing external task configuration, or submitting a job.

The L6 preflight must check:
- root `PASP.input` exists, parses structurally, and explicitly selects `Model GA`;
- every `%include` target resolves from the candidate package, cycles / duplicates / inactive declarations are reported, and edits target the first effective declaration;
- structure route is established: `cell.str` / `unit_cell.str`, inline structure, POSCAR route, or user-authorized equivalent;
- `SuperCell`, `Z_values`, `Spin_values` when present, species order, and structure basis have current-material provenance;
- branch settings match user-confirmed intent: random-spacegroup, perturbation, magnetic, restart, fixed lattice / cell, interface, parallel external evaluation, smoke-test or production;
- GA scale is user-confirmed and labeled as smoke-test or production; very small settings such as population `10` / generation `2` are not accepted as production by default;
- heredity / mutation balance is checked: `GA.Pher + GA.Pmut > 1` blocks, and `< 1` must be recorded as an intentional `Pperm` remainder;
- `str.init_sym`, `GA.symmetrize_str` and `rmax_cut` are treated as explicit current-run choices when present; official/example values such as `T/T/6.5` are not assumed defaults;
- every explicit PASP keyword / block / dependent file format has reference coverage or user-authoritative coverage;
- `seed.in`, if present, is checked as optional reproducibility input, not required by default;
- external evaluator plan is explicit: if `GA.parallel F`, `GA.VASPCMD` is present and current-environment confirmed; if `GA.parallel T`, `run_pvasp.sh` is present and preflighted; VASP / GULP input package, scheduler helper, executable path, stdout / stderr and cleanup behavior are current-environment facts;
- VASP `INCAR`, `KPOINTS` and `POTCAR` have user/project provenance; fixed `KPOINTS` meshes are not treated as GA defaults, and automatic mesh / staged relaxation claims are recorded only when user-confirmed;
- magnetic branch helper can handle `MAGMOM_*` or `OUTCAR` magnetic moment reading when current settings require it;
- restart branch artifacts are same-run and generation-consistent;
- no stale outputs such as old `PASP.used_info`, `Saved_*.POS`, `low_ene_strs.dat`, generation-suffixed DFT artifacts, `vasp_N/`, old logs or old `opt/` products are mixed into a fresh input package;
- README / PROGRESS marks candidate vs formal input, records user confirmations, reference inventory and blocked items.

## Output Validation Checklist

Use `skills/subskills/pasp-verifier/skill.md`, `mode: output-validation`, after a run completes and before reporting low-energy structures as handoff-ready, launching post-GA optimization, plotting, symmetry reporting, or restart from outputs.

The L6 output validation must check same-run evidence:
- PASP stdout / scheduler log exists and shows normal completion or the first decisive failure;
- `PASP.used_info` exists when available and confirms `Model GA`, effective branch settings, external program / parallel policy, population / generation scale and saved-structure settings;
- generation / candidate artifacts are consistent with the branch: `unrelaxed*`, `relaxed*`, `relaxed_child*`, `sym_relaxed*`, `POSCAR.NNN.GGG`, `CONTCAR.NNN.GGG`, `OSZICAR.NNN.GGG`, `OUTCAR.NNN.GGG`, `MAGMOM.NNN.GGG`, or `vasp_N/` as applicable;
- external evaluator results were consumed: missing or incomplete `OSZICAR` / `CONTCAR` / `OUTCAR` are reported by candidate and not hidden by aggregate summaries;
- low-energy outputs exist before handoff: `Saved_NNN.POS`, `Saved_gen.dat`, `low_ene_strs.dat`, `pc_low_ene_strs.dat`, or an explicitly equivalent current-run output;
- `strs_saved.dat` is present and same-run if restart or continuation is planned;
- saved-structure counts and numbering are explainable against `save_str.nsave_str` and actual completed candidates;
- `seed_used.in` or run seed evidence is recorded when reproducibility matters;
- post-GA `opt/` directories, if used, have their own VASP completion / energy evidence before reporting optimized energies or symmetries;
- symmetry-analysis outputs are postprocessing evidence only; they do not prove GA convergence.

Output validation cannot retroactively authorize a candidate package, overwrite formal `input/`, choose scientific settings, or bless a copied historical example.

## Downstream Handoff

After output validation passes, handoff should record:
- validated run id and source directory;
- selected `Saved_NNN.POS` or equivalent structure paths;
- associated generation / candidate / energy rows from `Saved_gen.dat` or low-energy summaries;
- external evaluator provenance, including failed / skipped candidates;
- whether structures are raw GA-retained structures or second-pass optimized structures;
- any symmetry-analysis tool and tolerance used as postprocessing;
- known gaps: no production convergence claim, no thermodynamic guarantee, no current-material default inference from Lecture examples.

If output validation fails or is blocked, the only allowed next steps are failure summary, missing-evidence list, log / helper diagnosis, or returning to candidate input preparation. Do not hand off structures as stable results.
