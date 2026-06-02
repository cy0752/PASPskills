# MD.E_type

## 含义
`MD.E_type` selects the time-dependent electric-field mode used by the `Model atomic_effective_H` MD driver.

Source audit found valid values `0..6`:
- `0`: no time-dependent electric field.
- `1`: uniform static field.
- `2`: Gaussian pulse.
- `3`: cosine field.
- `4`: piecewise electrocaloric field from `Field_for_Electrocaloric`.
- `5`: site-dependent cosine plane-wave field.
- `6`: site-dependent Gaussian times cosine field.

When `MD.E_type > 0`, source behavior enables electric-field force handling and Born-effective-charge polarization support. Preflight must therefore check the polarization path, including `atom_Heff.getP` / `Zeff.dat` consistency for the current structure and mode basis.

## 默认值
Not established by curated reference. Treat missing value through the active workflow and current `PASP.used_info` / formal input evidence.

## 取值
Integer `0..6`. Values outside this range stop with an invalid-input error in the audited source.

## 何时使用
- `Model atomic_effective_H`.
- `atom_Heff.MD T`.
- The workflow needs an electric-field-driven MD run, such as L5 BaTiO3 electric hysteresis.

## 注意事项
- For BaTiO3 hysteresis, `MD.E_type` only classifies the field waveform. It does not make the branch a Cr2O3 `SLD.mode` stage.
- `MD.E_type 4` requires the `Field_for_Electrocaloric` block and additional timing consistency checks.
- Do not write or change this field from Lecture-5 values unless the user confirms the field plan and the workflow has reference / authoritative coverage for all related fields.

## 本地来源
- Source audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-source.md`
- Lecture/example audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-slides.md`

