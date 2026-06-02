# MD.E_x, MD.E_y, MD.E_z

## 含义
`MD.E_x`, `MD.E_y`, and `MD.E_z` are the x/y/z components used by the time-dependent electric-field MD path under `Model atomic_effective_H`.

They are interpreted together with `MD.E_type` and related waveform parameters such as `MD.E_omega`, `MD.E_phi`, and, for electrocaloric mode, `Field_for_Electrocaloric`.

## 默认值
Not established by curated reference. Treat missing values through current formal input / `PASP.used_info` evidence and workflow intent.

## 取值
Real numbers.

## 何时使用
- `Model atomic_effective_H`.
- `atom_Heff.MD T`.
- Electric-field MD is active (`MD.E_type > 0`).

## 注意事项
- Unit semantics are a reference gap. Lecture-5 BaTiO3 text labels the example values as `V/A`; source comments and internal conversion notes are not fully consistent in the local audit. Before writing production values, require user-confirmed units and, if possible, authoritative PASP documentation or project-owner confirmation.
- Active electric field can require Born-effective-charge support; preflight must check `Zeff.dat` provenance when polarization / BEC support is active.
- Do not use Lecture-5 BaTiO3 `MD-1` component values as defaults.

## 本地来源
- Source audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-source.md`
- Lecture/example audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-slides.md`

