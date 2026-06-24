# MD.input

## 文件作用
提供分子动力学（MD）模拟相关设置。

## 何时需要
- 仅在 `Model atomic_effective_H` 情形下做 MD 时需要
- 当需要设置动力学时间步长、总时长、局域模式质量、NVE/NVT、LLG 算法等时使用

## 关键字段/内容
- `atom_Heff.MD T/F`：是否开启 MD
- `%block atom_Heff.MASS_local_mode`：各局域模式的等效相对原子质量
- `MD.Delta_t`：单步时长，单位 fs，文档建议常用 `0.1–1.0`
- `atom_Heff.MD_time`：总模拟时长，单位 fs
- `SLD.mode`：`1` 仅位移自由度，`2` 仅自旋自由度，`3` 位移+自旋
- `LLG.method`：`1` 4th-order Runge-Kutta，`2` Mentink’s SIB，`3` McLachlan’s SMP
- `LLG.damping`：LLG 阻尼；非零时按 `MD.temperature` 做 NVT
- `MD.damping`：Newton 方程阻尼；非零时做 NVT，零时做 NVE
- `MD.temperature`：NVT 目标温度
- `MD.B_x`、`MD.B_y`、`MD.B_z`：MD 中使用的外磁场分量
- `MD.E_type`、`MD.E_x/y/z`、`MD.E_omega`、`MD.E_phi`：`atomic_effective_H` MD 中的 time-dependent electric-field controls；exact waveform / unit details should be checked in the parameter cards before writing
- `atom_Heff.getP`：开启 Born-effective-charge polarization path；active polarization / electric-field workflows must check `Zeff.dat` provenance
- `local_mode.MD_mode_range`：MD local-mode amplitude bounds；row/component scope must match the current mode basis

## 注意事项
- 该文件中的设置也可直接写入 `PASP.input`
- PASP 当前仅在 `Model atomic_effective_H` 下支持 MD
- MD 与 MC 不能同时开启
- `MD.Delta_t` 过小会导致计算时间过长，过大则会导致动力学失真，尤其 NVE 下总能量难以守恒
- 文档指出 `LLG.method 2` 目前最常用；`method 1` 不支持 NVT，`method 3` 不支持并行
- 对纯结构 / 仅位移自由度的 `atomic_effective_H` MD，通常应显式设置 `SLD.mode 1`，避免默认 `SLD.mode 3` 进入 spin-lattice coupled branch。若目标是 NVT，`LLG.method 1` 不支持 NVT；除非用户明确选择其他 branch，优先确认 `LLG.method 2`。
- `MD.damping` 在 audited `vlt_step` 路径中对应 Langevin-style lattice thermostat 的阻尼/摩擦项；不要把温度漂移先归因于 Nose-Hoover 参数，先检查 `SLD.mode`、`LLG.method`、`MD.damping`、`MD.temperature`、`MD.init_velocity_temp` 和 active degrees of freedom 是否与用户确认的 ensemble 一致。
- `atom_Heff.MASS_local_mode` block 内应按当前 local-mode order 把所有质量值写成同一连续列表；条目数等于 local-mode count，不包含 strain modes。
- `atomic_effective_H` MD 的 MPI ranks 不能只按“越多越好”或总原子数估计。提交前必须确认存在三维进程分解 `p1 * p2 * p3 = ranks`，且 `p1 | n1`、`p2 | n2`、`p3 | n3`，其中 `(n1,n2,n3)` 是 PASP 从当前 `cell` / `unit_cell` 关系得到的 supercell factors。否则会触发类似 `number of nodes is not compatible with the supercell` 的错误。
- BaTiO3 electric hysteresis is an L5 single-stage electric-field MD branch. Do not use its field settings as Cr2O3 SLD defaults, and do not treat Cr2O3 `SLD.mode 1/2/3` handoff rules as BaTiO3 hysteresis validation.
- Electric-field component units are a current reference gap in the local cards. Require user-confirmed units / authoritative source before writing production values.

## 最小示例
```text
atom_Heff.MD T
%block atom_Heff.MASS_local_mode
33.5219 33.5219 33.5219
%endblock atom_Heff.MASS_local_mode
MD.Delta_t 0.5
atom_Heff.MD_time 4.0d3
SLD.mode 1
LLG.method 2
LLG.damping 1.0d-2
MD.damping 4.0d-2
```

## 来源章节
- 3.1.6 `MD.input`
- 锚点：`#md-input`
