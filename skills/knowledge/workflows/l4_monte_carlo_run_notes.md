# L4 Monte Carlo Run Notes

本文件记录 Lecture-4 examples 暴露出来的 L4 MC / PTMC 输入包形态、输出家族和容易误用的经验点。它是历史观察，不是当前用户目录事实，也不是参数默认值来源。

运行时必须优先使用：
- `l4_monte_carlo_state_machine.md`
- `l4_monte_carlo.md`
- `knowledge/reference/`

不要把本文件中的 `SuperCell`、`PT.M`、温度、步数、`Spin_values`、`Z_values`、cutoff、power、mode 数或输出全集直接复制到当前任务。

## Example Inventory

| Example | 主要形态 | 输入特点 | 代表输出 |
|---|---|---|---|
| `MC-1` | BaTiO3-style local-mode / strain / polarization `atomic_effective_H` | `amp_local_mode.in_unitcell`、`Zeff.dat`、inline `local_mode.mode_definition`、`local_mode.MC_mode_range` | `C_PTMC_K.dat`、`P_abs.dat`、`abc_cell_str_K.dat`，complete 中有大量 `T_*_final_.amp` 和 displacement XSF |
| `MC-2` | BiFeO3-style spin-mode `atomic_effective_H` | inline spin `local_mode.mode_definition`，`Read_init_spin F`，`atom_Heff.cal_mag F` | `E_PTMC_K.dat`、`C_PTMC_K.dat`、selected final spin XSF |
| `MC-3` | YIG-style spin-mode `atomic_effective_H` with split include | `mode_def.input` 被 `%include` 引入，说明 preflight 必须追踪任意 direct include | `E_PTMC_K.dat`、`C_PTMC_K.dat`、`M_PTMC_K.dat`、selected final spin XSF |

## Stable Lessons From Examples

- `PASP.input` 常见 direct includes：`cell.str`、`unit_cell.str`、`MC.input`，也可能 include split files，例如 `mode_def.input`。
- `Model atomic_effective_H` 的运行包通常依赖 same-basis `local_mode_PM.dat` 和 `J_best.dat`。
- `local_mode.read_interaction T` 是 L4 消费上游 interaction basis 的常见形态。
- `Read_init_spin T` 在 `atomic_effective_H` 分支对应 local-mode amplitude 初态；example 中出现的 `amp_local_mode.in_unitcell` 应按 `MC.init_spin_unitcell` reference 检查。
- `Zeff.dat` 是 polarization 输出相关的条件输入；不能因为某个 example 有它就要求所有 L4 run 都有。
- `atom_Heff.cal_mag F` 可能是节省计算的输出覆盖选择；如果用户目标包括 magnetization，必须确认是否应开启对应输出。
- `MC-3` 表明不能只检查固定文件名。preflight 必须解析 `PASP.input` 中所有 direct `%include`。
- `output/` 目录通常只是讲义展示用的精选输出；`complete/` 才展示更多运行副产物。workflow 不应要求每个 run 都生成 complete 中的所有文件。
- Lecture-4 run instructions and all three MC `sub_pasp` examples use MPI launch patterns. The example scheduler scripts use `mpirun -np $SLURM_NTASKS ${BIN_DIR}/PASP.x`; the lecture also shows `mpirun -np 8 /path/to/PASP.x` with optional stdout / stderr redirection.
- When turning an example or previous input package into a quick smoke run, keep the run directory clean. Copy only active inputs and required direct/conditional include files into `runs/<run-id>/`; do not copy old outputs such as `PASP.used_info`, `log.out`, `T.dat`, `*_used.dat`, `T_*`, `final_*`, `lowest_ene.*`, or `*_PTMC*`.
- Small `SuperCell` and short MC/PTMC step counts are useful for workflow debugging, but they must be labeled as smoke-test settings and never used as evidence for production thermodynamics.

## Input File Meaning By Example

### Common Files

| 文件 | 观察到的角色 | Workflow 判断 |
|---|---|---|
| `PASP.input` | 模型入口，包含结构 include、`MC.input` include、supercell、species / spin、mode / interaction-reuse 控制 | 必须进入 candidate package；每个显式字段和 block 需 reference-backed preflight |
| `MC.input` | `Model atomic_effective_H`、MC/PTMC/CG、温度、副本数、步数、初始态、输出覆盖 | 必须进入 candidate package；PT/rank、统计长度、初态和输出覆盖是高风险检查项 |
| `cell.str` | 模拟结构基底 | 通常必需；和 `unit_cell.str` / `SuperCell` 的关系需按 reference 检查 |
| `unit_cell.str` | 原胞或 reference cell | 常见必需；不能从 `cell.str` 随意推断 |
| `local_mode_PM.dat` | 上游 interaction / local-mode basis | `atomic_effective_H` L4 重要上游文件；必须和 `J_best.dat` 同源 |
| `J_best.dat` | fitted interaction parameter values | 必须与 interaction numbering / `local_mode_PM.dat` 匹配 |
| `sub_pasp` | example 的提交 helper | 环境脚本，不是科学输入；不可替代 input preflight |

## Submission Helper Observations

All three Lecture-4 MC input directories include a `sub_pasp` script with the same basic shape:

```bash
#SBATCH --ntasks=40
module purge
module load oneapi/2023.2
ulimit -s unlimited
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_STACKSIZE=256M
BIN_DIR=/data/app/sh2025/pasp/bin
mpirun -np $SLURM_NTASKS ${BIN_DIR}/PASP.x
```

Stable lessons:
- L4 MC/PTMC runs can use `mpirun` to launch `PASP.x`.
- In scheduler scripts, `-np` may be tied to `SLURM_NTASKS`; preflight must compare that effective process count with `PT.M`.
- `BIN_DIR`, partition, wall time, module environment and task count are environment choices, not transferable defaults.
- If stdout is not redirected to `log.out`, output validation must inspect the scheduler stdout file such as `pasp.%j.out` and record where normal-completion markers were found.
- Editing a submission helper is allowed only after input preflight for submit-ready work; changing PASP input fields or read files requires returning to candidate input preflight.

### Conditional Files

| 文件 | 出现场景 | Workflow 判断 |
|---|---|---|
| `amp_local_mode.in_unitcell` | `MC-1/input`，配合 `MC.init_spin_unitcell T` | 按 `MC.init_spin_unitcell` reference 检查；文件格式仍需来源或 preflight 证据 |
| `amp_local_mode.in` | reference 中的 `atomic_effective_H` 初态文件 | `Read_init_spin T` 时优先按 reference 检查 |
| `Zeff.dat` | `MC-1/input` polarization run | `atom_Heff.getP T` 或极化目标时检查；不是所有 L4 run 的硬输入 |
| `mode_def.input` | `MC-3/input` split mode definition | direct include 文件；preflight 必须追踪并检查 |
| `seed.in` / `seed_used.in` | optional reproducibility / run evidence | `seed.in` 可选；`seed_used.in` 是 output validation 可记录的运行证据 |

## Example-Specific Input Patterns

### MC-1: Local-Mode / Strain / Polarization

`MC-1/input` contains `PASP.input`, `MC.input`, `cell.str`, `unit_cell.str`, `local_mode_PM.dat`, `J_best.dat`, `amp_local_mode.in_unitcell`, `Zeff.dat`, and `sub_pasp`.

Observed `PASP.input` pattern:
- `%include cell.str`
- `%include unit_cell.str`
- `%include MC.input`
- `%block SuperCell`
- `%block Z_values`
- `local_mode.read_interaction T`
- `Invariant.power` / strain powers / `fig.maxk` / `%block fig.mdist`
- `%block local_mode.MC_mode_range`
- inline `%block local_mode.mode_definition`
- `local_mode.general_model T`
- `local_mode.full_atomic F`

Observed `MC.input` pattern:
- `Model atomic_effective_H`
- `Read_init_spin T`
- `MC.init_spin_unitcell T`
- `atom_Heff.homogeneous_strain T`
- `atom_Heff.inhomogeneous_strain F`
- `atom_Heff.relax_str F`
- `MC T`
- `Parallel_Tempering T`
- `global.heat_bath F`
- `atom_Heff.getP T`
- `atom_Heff.MD F`
- `atom_Heff.auto_adjust_try_amp T`
- `PT.*` and `nblk` / `nbeg_blk` controls

Stable lesson: preflight local-mode, strain, polarization, initial-state, PT and sampling settings together. Do not promote observed values to defaults.

### MC-2: Spin-Mode Atomic Effective Hamiltonian

`MC-2/input` contains `PASP.input`, `MC.input`, `cell.str`, `unit_cell.str`, `local_mode_PM.dat`, `J_best.dat`, and `sub_pasp`.

Observed `PASP.input` pattern:
- `%include cell.str`
- `%include unit_cell.str`
- `%include MC.input`
- `%block SuperCell`
- `%block Spin_values`
- `%block Z_values`
- `local_mode.general_model T`
- `local_mode.read_interaction T`
- `Invariant.SOC F`
- `GSM.maxpower`
- `local_mode.GSM2lm_int T`
- `fig.maxk`
- `%block fig.mdist`
- inline spin-mode `%block local_mode.mode_definition`

Observed `MC.input` pattern:
- `Model atomic_effective_H`
- `MC T`
- `Parallel_Tempering T`
- `Read_init_spin F`
- `global.heat_bath F`
- `PT.*` and `nblk` / `nbeg_blk` controls
- `atom_Heff.cal_mag F`

Stable lesson: spin-mode L4 can still use `Model atomic_effective_H`; do not route solely by the presence of spin variables. Route L2 only when the model branch is `Spin_lattice_interaction` / `spin_exchange.dat`.

### MC-3: Split Mode Definition / Magnetic Observables

`MC-3/input` contains `PASP.input`, `MC.input`, `mode_def.input`, `cell.str`, `unit_cell.str`, `local_mode_PM.dat`, `J_best.dat`, and `sub_pasp`.

Observed `PASP.input` pattern:
- `%include cell.str`
- `%include unit_cell.str`
- `%include MC.input`
- `%include mode_def.input`
- `%block SuperCell`
- `%block Z_values`
- `%block Spin_values`
- `local_mode.general_model T`
- `local_mode.full_atomic F`
- `local_mode.read_interaction T`
- `Invariant.SOC F`
- `fig.maxk`
- `%block fig.mdist`
- invariant power settings

Observed `MC.input` pattern:
- `Model atomic_effective_H`
- `MC T`
- `Parallel_Tempering T`
- `Read_init_spin F`
- `atom_Heff.auto_adjust_try_amp T`
- `atom_Heff.homogeneous_strain F`
- `atom_Heff.inhomogeneous_strain F`
- `atom_Heff.relax_str F`
- optional commented `%block ExternalMagneticField`
- `PT.*` and `nblk` / `nbeg_blk` controls
- `atom_Heff.cal_mag F`

Stable lesson: direct include traversal is mandatory, and output coverage settings must be reconciled with the user's desired observables.

## Output Families Seen In Examples

### Curated `output/` Directories

Lecture `output/` directories are small teaching subsets:

| Example | Files observed | Meaning |
|---|---|---|
| `MC-1/output` | `C_PTMC_K.dat`, `P_abs.dat`, `abc_cell_str_K.dat` | heat capacity, polarization magnitude, lattice-vector trend |
| `MC-2/output` | `C_PTMC_K.dat`, `E_PTMC_K.dat`, selected `T_*_final*spin.xsf` | heat capacity, energy, final spin visualizations |
| `MC-3/output` | `C_PTMC_K.dat`, `E_PTMC_K.dat`, `M_PTMC_K.dat`, selected `T_*_final_originalpos.onlyspin.xsf` | heat capacity, energy, magnetization, final spin visualization |

These files are enough to show the teaching objective, but not enough to prove a current run is complete. Runtime output validation must inspect the actual run directory, logs, `PASP.used_info`, warnings, and required handoff files.

### Complete Directory Output Families

`complete/` directories show broader output families. Presence varies by model, flags and PASP version.

| Family | Examples / names | Meaning |
|---|---|---|
| run metadata | `PASP.used_info`, `seed_used.in`, copied input files | actual resolved settings and reproducibility evidence |
| PTMC statistics | `E_PTMC*`, `E2_PTMC*`, `C_PTMC*`, `M_PTMC*`, `Mabs_PTMC*`, `M2_PTMC*`, `Mz_PTMC*`, `X_PTMC*`, `MCE.dat`, `ECE.dat` | observables versus internal temperature or Kelvin |
| detailed sampling | `Eachstatstep_T*.dat`, `nsample_PTMC.dat`, `EEt_MMt_PTMC.dat` | sample-count and per-step diagnostics |
| local-mode / ferroic observables | `P_abs.dat`, `u_sort_K.dat`, `u_sep_K.dat`, `u_abs_sep_K.dat`, `u2_sep_K.dat`, `strain_K.dat`, `abc_cell_str_K.dat` | polarization, local-mode, strain and lattice trends |
| final state | `T_*_final_.amp`, `T_*_final*.xsf`, `final_amp_ptmc.*`, `final_ene.*`, `final_ene.all` | final-state outputs; not automatically global lowest state |
| lowest state | `lowest_ene.*`, including amplitude, position, energy and convergence files when produced | global / node lowest-state evidence for handoff |
| interaction snapshots | `local_mode_PM_used.dat`, interaction-type snapshots | provenance / resolved interaction evidence |
| spin final-state files | `node_*_finalspin.out`, selected final spin XSF | spin-mode final state; not automatically lowest state |

## Output Meaning Cheat Sheet

- `E_PTMC_K.dat`: energy as a function of temperature in Kelvin; useful for thermodynamic curves.
- `C_PTMC_K.dat`: heat capacity as a function of temperature in Kelvin; peak location is often the teaching target.
- `M_PTMC_K.dat`: magnetization-related observable versus Kelvin; only meaningful if magnetic degrees of freedom and output coverage are active.
- `P_abs.dat`: polarization magnitude-style output; requires the polarization-related setup to be active and `Zeff.dat` provenance to be valid.
- `abc_cell_str_K.dat`: lattice-vector / cell-shape trend versus Kelvin.
- `strain_K.dat`: strain statistics versus Kelvin.
- `u_*_K.dat`: local-mode / displacement statistics versus Kelvin.
- `Eachstatstep_T*.dat`: per-temperature-index sampling trace; useful for diagnosing whether measurement data exist.
- `nsample_PTMC.dat`: sample count evidence; useful before trusting noisy curves.
- `T_*_final_.amp`: final local-mode amplitude at a temperature / replica. It is a final-state file, not automatically a lowest-state file.
- `T_*_final*.xsf`: final-state visualization files; useful for VESTA / OVITO, not proof of global minimum.
- `final_amp_ptmc.*` / `final_ene.*`: final-state PTMC summary families.
- `lowest_ene.amp_local_mode`: preferred atomic effective-Hamiltonian lowest-state amplitude handoff when output validation passes.
- `lowest_ene.str_mode_amp`: lowest-state mode amplitude summary.
- `lowest_ene.pos`: lowest-state position / structure-like handoff.
- `lowest_ene.ene`: lowest-state energy.
- `lowest_ene.ene_symbol`: symbolic-energy style output for downstream model diagnostics when produced.
- `lowest_ene.convergence`: convergence evidence for lowest-state tracking.
- `relax-lowest_ene.*`: relax / CG output family; must be paired with log evidence such as `CG finish` before calling it relaxed.

## Source-Audited Reference Cards Added From Examples

These Lecture-4 example items were not found in the official-doc extracted parameter cards, so local source-audited cards were added:

- `MC.init_spin_unitcell`: see `../reference/params/MC.init_spin_unitcell.md`.
- `atom_Heff.getP`: see `../reference/params/atom_Heff.getP.md`.
- `atom_Heff.cal_mag`: see `../reference/params/atom_Heff.cal_mag.md`.

Remaining example-observed items already have parameter cards or still need only contextual review:
- `PT.ninterval` / `PT.nmeasure`: output cadence / measurement controls seen in examples.
- `local_mode.GSM2lm_int` and `GSM.maxpower`: spin-mode effective-Hamiltonian example controls.
- `local_mode.full_atomic`: example control seen beside `local_mode.general_model`.

Even with these cards, L4 agents must still avoid copying Lecture-4 parameter values into current tasks. The cards support syntax / behavior checks; they do not confirm the user's physical settings.
