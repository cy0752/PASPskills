# field.dat

## 文件作用
`field.dat` is an MD output time series for applied field components.

For the L5 BaTiO3 electric-hysteresis branch, it is the electric-field side of the validated `field.dat` + `P_abs.dat` pair used for plotting polarization versus field.

## 何时需要
- After an `atomic_effective_H` MD run with electric-field output.
- Before hysteresis plotting or electric-field response analysis.

## 关键字段/内容
The observed `MD-1` BaTiO3 output header contains:
- `step`
- `time (ps)`
- `E_x`, `E_y`, `E_z`
- `B_x`, `B_y`, `B_z`

## 注意事项
- File existence alone is not validation. Check completion evidence, effective settings, header, monotonic sampled rows, and same-run provenance with `P_abs.dat`.
- Do not pair `field.dat` from one run with `P_abs.dat` from another run, sibling output, historical `output/`, or stale `complete/` snapshot.
- `energy.dat` and `temperature.dat` are diagnostics; they do not replace `field.dat` for hysteresis validation.

## 本地来源
- Source audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-source.md`
- Example audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-examples.md`

