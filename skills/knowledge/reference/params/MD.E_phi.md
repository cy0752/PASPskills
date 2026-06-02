# MD.E_phi

## 含义
`MD.E_phi` is the phase parameter used by time-dependent electric-field modes in the `atomic_effective_H` MD driver.

In the Lecture-5 BaTiO3 example, it is paired with `MD.E_type 3` and the cosine electric-field schedule.

## 默认值
Not established by curated reference.

## 取值
Real number. The Lecture-5 example describes the phase in radians, but production writes still require user-confirmed intent.

## 何时使用
- Electric-field MD waveform needs a phase parameter, especially cosine-style field modes.

## 注意事项
- Confirm the intended waveform and phase convention with the user before writing.
- Do not copy the Lecture-5 BaTiO3 value as a default.

## 本地来源
- Source audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-source.md`
- Lecture/example audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-slides.md`

