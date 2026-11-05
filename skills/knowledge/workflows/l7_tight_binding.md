# L7 Tight-Binding Workflow

本文件是 L7 tight-binding workflow 的稳定运行契约。runtime agent 必须先读 `l7_tight_binding_state_machine.md` 判定状态和 STOP gate；本文件只补充当前状态所需的输入、输出、可调项和 reference handoff。Lecture-7 examples 和 `l7_tight_binding_run_notes.md` 是历史观察，不是当前用户目录事实，也不是参数默认值。

## 目标

构建并使用 PASP `Model TB` 相关紧束缚模型，覆盖首轮 MVP 的五条主分支：
- custom TB：手写 `block Hop_Parameters`
- SKTB：`USE_Slater_Koster_Model` + `block Slater_Koster_Hop_Parameters`
- SKTB plus additional Hamiltonian：`TB.additional_H` + `H_add.dat` / `Hmat_add.dat`
- GSDTB：`TB.find_H_form` / `TB.full_SOC` / `TB.H_spin_expand`
- SKTB plus flat-band CLS：`TB.localized_state` 搜索 `local_cluster.*`

高级分支如 `TB.MLWF`、`TB.TBPM`、`TB.Berry`、`TB.Z2`、parity、Green function 和其他拓扑分析已在源码或 examples 中出现，但本轮只作为 future extension / reference gap，不作为 submit-ready workflow 主线。

## 适用问题

- 我想做 TB / tight-binding / 紧束缚模型。
- 我想从结构和 hopping 参数开始算能带或 DOS。
- 我想做 SKTB / Slater-Koster TB。
- 我想在 SKTB 里额外加哈密顿量矩阵。
- 我想做 GSDTB / spin-dependent TB / 搜索自旋依赖哈密顿量形式。
- 我想做 flat band / CLS / compact localized state 搜索。

## 核心输入包

所有 L7 candidate input package 至少需要：
- `PASP.input`，显式写 `Model TB`。
- 结构路线：直接 `%include cell.str`、其他被 reference/user-authoritative source 支持的结构输入，或当前 workflow 明确记录的等价路线。
- `block SuperCell` 或记录为什么当前 branch 不需要/未确认。
- `block Z_values`。在 TB 模块中它通常表示各元素考虑轨道的电子数；不要把其他 workflow 中的原子序数解释直接套进 TB branch。
- `block Orbitals`。其轨道数决定 custom hopping 矩阵行列数，也决定 SKTB/输出矩阵维度。
- branch-specific hopping / Hamiltonian / search blocks。
- README / PROGRESS，记录 branch、file roles、user confirmation、reference inventory、preflight evidence 和 blocked items。

Environment helpers such as `sub_pasp`, `sub_gnuplot`, scheduler scripts or plotting scripts are helpers, not portable PASP input defaults.

## Branches

### B1：custom TB

Use when the user has explicit hopping matrices rather than Slater-Koster shell integrals.

Hard inputs:
- `PASP.input`
- structure include/route
- `block Orbitals`
- `Different_hop_path`
- exactly one active hopping path interpretation: `Hop_Parameters_specified_using_site` or `Hop_Parameters_specified_using_dis`
- `block Hop_Parameters`

Important checks:
- `USE_Slater_Koster_Model` absent or false.
- `block Hop_Parameters` has one path record per `Different_hop_path`.
- For each path, matrix row count equals the first species/site orbital count from `Orbitals`; column count equals the second species/site orbital count.
- If `TB.complex_hop T`, hopping entries must use complex values accepted by Fortran input.
- Distance-based paths must be compatible with current structure and intended bond distance; site/vector paths must use the correct atom numbering and cell offset convention.

Typical outputs:
- `TB.bands`
- `Eg.dat`
- `energy.dat`
- `dos.dat` when DOS is requested
- `band.agr`, `plot.dat`, `gnuplot.dat` when band plotting is generated
- `wf_kpt_<ik>-band_<ib>.xsf` only when `TB.write_wf T`

### B2：SKTB

Use when hopping is represented by Slater-Koster shell combinations.

Hard inputs:
- `PASP.input`
- structure include/route
- `USE_Slater_Koster_Model T`
- `block Orbitals`
- `block orbitals_nl`
- `Different_hop_path`
- exactly one active SK path interpretation: `Hop_Parameters_specified_using_site` or `Hop_Parameters_specified_using_dis`
- `block Slater_Koster_Hop_Parameters`

Conditionally important:
- `Ylm_form 2` when set. Source currently stops for non-2 forms.
- `use_rotation_matrix` when angular-momentum rotation/SOC branch requires it.
- `overlap.distance` and `Different_overlap_path` only for non-orthogonal or overlap-aware branches; do not require them for every SKTB package.
- `Spin_values`, `spin_noncollinear`, `nspin_directions_set`, `spin_directions_set`, `nsites_SOC`, `magnitude_SOC`, `Sn_basis`, `TB.U` only when the user-confirmed branch includes spin/SOC/Hubbard behavior.

Important checks:
- `Slater_Koster_Hop_Parameters` path count and shell-pair count are consistent with `Different_hop_path`.
- `orbitals_nl` shell entries match the orbital count and shell intent in `Orbitals`.
- For same-species SK paths not using site format, source comments warn that both shell orderings may be needed; if not established, mark blocked / needs user decision.
- `TB.distance_tiny` is a distance matching tolerance for distance-based SK paths, not a production fitting knob to copy from flat-band examples.

### B3：SKTB plus additional Hamiltonian

Use when the user wants to add matrix elements or a full matrix to the TB Hamiltonian.

Base requirements:
- B2 SKTB package must be internally consistent.
- `TB.additional_H T`
- `H_add.dat` and/or `Hmat_add.dat`, with explicit current-branch provenance.

Checks:
- `H_add.dat` rows identify matrix row, column and added value.
- `Hmat_add.dat` is a full matrix compatible with the generated Hamiltonian dimension; source reads it as `2*notot` by `2*notot` in the noncollinear/additional-H path.
- Added matrix intent, basis order and hermiticity expectations are user-confirmed or source/reference-backed.
- No stale `Htot.dat`, `H.dat`, `H_R.dat`, `H_I.dat`, or prior run matrix outputs are mixed into fresh input.

### B4：GSDTB / spin-dependent Hamiltonian search

Use when the user wants the general spin-dependent Hamiltonian form or magnetic anisotropy-style analysis from independent Hamiltonian variables.

Base requirements:
- Usually starts from a current SKTB package.
- `TB.find_H_form T`
- `TB.full_SOC T` when full SOC branch is intended.
- `TB.H_spin_expand T` when explicit spin-expanded Hamiltonian is intended.
- `block GSD_TB_Spin_direction`
- `block TB.H_indep_var`
- `fig.maxk` and `block fig.mdist` for the symmetry search scope.
- Spin/SOC settings such as `Spin_values`, `Sn_basis`, `use_rotation_matrix` as branch-confirmed inputs.

Checks:
- User has confirmed GSDTB target, spin/SOC strategy, independent-variable assignment and whether this is a form-search run or an energy-evaluation run.
- `TB.H_indep_var` must be treated as high-risk: do not invent independent variable counts or values from Lecture-7 examples.
- No stale `cluster-*.Hform`, `H*.dat`, `WF*.dat`, old logs or prior Hamiltonian outputs are present in candidate input unless explicitly validated as current same-run outputs.

Typical outputs:
- `cluster-*.Hform`
- `H_ik_*_i_*_m_*.dat` Hamiltonian-form fragments in some current PASP runs
- Hamiltonian / wavefunction artifact families such as `H.dat`, `H_R.dat`, `H_I.dat`, `Htot.dat`, `WF*.dat`, depending on branch/settings/version.

### B5：flat-band CLS search

Use when the user already has a TB/SKTB model and wants compact localized state evidence for a target flat band.

Base requirements:
- Usually starts from a current SKTB band package.
- `TB.localized_state T`
- `TB.center_atom_localized`
- `TB.rcut_localized`
- `TB.eigen_localized`
- Band path / target eigenvalue evidence sufficient to justify the selected flat band.

Checks:
- `TB.rcut_localized` is a search cutoff radius; larger values cost more. Do not promote Lecture-7 cutoff values as defaults.
- `TB.eigen_localized` must come from user-confirmed target flat-band energy or validated current output, not from a sibling example.
- Source stops after `TB_localized_state` when `TB.localized_state T`; treat this as a separate run target from ordinary band/DOS production.

Successful output evidence:
- log / stdout contains `lgood: T` or equivalent success evidence.
- `local_cluster.xyz`
- `local_cluster.vesta`

## Stages

### S0 / S1：inventory and branch classification

Use the state machine first. Inspect only the user-specified target directory and `knowledge/` unless the user explicitly authorizes cross-example comparison.

Classify:
- branch: B1-B5, MLWF/advanced, output validation, or uncertain.
- actual files and stale outputs.
- direct `%include` graph.
- exact reference cards needed before any write.

### S2 / S3：candidate package and settings confirmation

Candidate packages can be drafted, but they are not submit-ready. Before formal input or run derivation, record:
- `USER_CONFIRMED_L7_TB_SETTINGS=true`
- branch target and stage
- structure route and species order
- `Orbitals` basis intent and source
- hopping / SK / additional-H / GSDTB / CLS settings table
- smoke-test vs production intent
- expected outputs and validation target
- reference gaps

### S4：input preflight

Before promoting candidate files, overwriting formal input, deriving a run directory, preparing external submission artifacts, or submitting a job, use `subskills/pasp-verifier/skill.md` with `mode: input-preflight`.

Minimum L7 preflight:
- `PASP.input` parses structurally and explicitly selects `Model TB`.
- Direct includes resolve inside the candidate package.
- Branch B1-B5 is explicit and user-confirmed.
- `Orbitals` is present and consistent with hopping/SK/additional-H/GSDTB/CLS branch.
- Every explicit keyword/block/file has reference or user-authoritative coverage.
- Branch-specific files are present or blocked.
- Candidate package has no stale outputs.
- README / PROGRESS does not claim submit-ready before gates pass.

### S5：formal input / run / submission preparation

Allowed only after:
- `USER_CONFIRMED_L7_TB_SETTINGS=true`
- `READ_ONLY_SUBAGENT_PREFLIGHT_DONE=true`
- `STAGE_PREFLIGHT_PASS=true`

Then formal `input/`, `runs/<run-id>/`, helper files and submission artifacts may be prepared. Actual submission still requires explicit user submission authorization.

### S6 / S7：output validation and handoff

Before reporting band gaps, plotted bands, DOS, wavefunction files, added-H results, GSDTB forms, Hamiltonian artifacts, or CLS files as usable, run output validation on the exact completed run/output directory.

Validation targets:
- generic TB/SKTB: normal completion evidence, `TB.bands`, `Eg.dat`, `energy.dat`, `dos.dat` when requested, plotting files when generated.
- `TB.write_wf`: `wf_kpt_*-band_*.xsf` same-run evidence.
- additional-H: same-run `Htot.dat` or equivalent Hamiltonian output tied to `H_add.dat` / `Hmat_add.dat`.
- GSDTB: `cluster-*.Hform`, `H_ik_*_i_*_m_*.dat`, `TB_H_symmetry done` log evidence, and Hamiltonian artifact provenance.
- CLS: `lgood: T` and same-run `local_cluster.xyz` / `local_cluster.vesta`.

Output validation cannot retroactively authorize an input package.

Do not treat scheduler / platform success alone as output validation. If `log.out` contains `BAD TERMINATION`, `KILLED BY SIGNAL`, `Error, ...`, or lacks the branch's expected completion evidence, mark outputs as dirty / diagnostic even when expected files exist.

## Reference Handoff

Route exact definitions, defaults, syntax or row formats to reference, especially:
- `modules/tb.md`
- `topics/PASP.input.md`
- `params/Model.md`
- `params/Orbitals.md`
- `params/Z_values.md`
- `params/SuperCell.md`
- `params/Different_hop_path.md`
- `params/Hop_Parameters_specified_using_site.md`
- `params/Hop_Parameters_specified_using_dis.md`
- `params/Hop_Parameters.md`
- `params/TB.complex_hop.md`
- `params/USE_Slater_Koster_Model.md`
- `params/Slater_Koster_Hop_Parameters.md`
- `params/orbitals_nl.md`
- `params/Ylm_form.md`
- `params/use_rotation_matrix.md`
- `params/overlap.distance.md`
- `params/Spin_values.md`
- `params/spin_noncollinear.md`
- `params/nspin_directions_set.md`
- `params/spin_directions_set.md`
- `params/nsites_SOC.md`
- `params/magnitude_SOC.md`
- `params/Sn_basis.md`
- `params/TB.U.md`
- `params/TB.additional_H.md`
- `params/TB.write_wf.md`
- `params/TB.distance_tiny.md`
- `params/TB.localized_state.md`
- `params/TB.center_atom_localized.md`
- `params/TB.rcut_localized.md`
- `params/TB.eigen_localized.md`
- `params/TB.find_H_form.md`
- `params/TB.full_SOC.md`
- `params/TB.H_spin_expand.md`
- `params/GSD_TB_Spin_direction.md`
- `params/TB.H_indep_var.md`
- `params/fig.maxk.md`
- `params/fig.mdist.md`

Known L7-related reference gaps include `Different_overlap_path`, `H_add.dat`, `Hmat_add.dat`, `Htot.dat`, `H_ik_*_i_*_m_*.dat`, `cluster-*.Hform`, `local_cluster.*`, and `wf_kpt_*-band_*.xsf` dedicated file cards. If a card is missing or incomplete, record a reference gap and ask for user/source authority before writing exact content.
