# MD.E_omega

## 含义
`MD.E_omega` is the angular-frequency-like parameter used by time-dependent electric-field modes in the `atomic_effective_H` MD driver.

In the Lecture-5 BaTiO3 example, it is paired with `MD.E_type 3` and described as the cosine-field frequency. The slide notes unit `fs^-1` and relates the period to `2*pi / omega`.

## 默认值
Not established by curated reference.

## 取值
Real number.

## 何时使用
- Electric-field MD waveform needs a frequency parameter, especially `MD.E_type 3`, `5`, or `6`.

## 注意事项
- Confirm the intended waveform and time scale with the user before writing.
- Do not copy the Lecture-5 BaTiO3 value as a default.
- For a non-cosine waveform, check `MD.E_type` semantics first; this field may be irrelevant or insufficient.

## 本地来源
- Source audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-source.md`
- Lecture/example audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-slides.md`

