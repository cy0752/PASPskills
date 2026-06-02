# P_abs.dat

## 文件作用
`P_abs.dat` is a polarization / dipole time-series output written when the polarization path is active.

For the L5 BaTiO3 electric-hysteresis branch, it is the polarization side of the validated `field.dat` + `P_abs.dat` pair used for plotting polarization versus field.

## 何时需要
- The workflow requires polarization output or hysteresis plotting.
- `atom_Heff.getP T` or active electric-field behavior requires Born-effective-charge support.

## 关键字段/内容
The observed `MD-1` BaTiO3 output header contains:
- `step`
- `time (ps)`
- `P_x`, `P_y`, `P_z`
- `P_abs`

## 注意事项
- Preflight must check `Zeff.dat` provenance when polarization / BEC support is active.
- File existence alone is not validation. Check completion evidence, effective settings, header, monotonic sampled rows, and same-run provenance with `field.dat`.
- The historical BaTiO3 audit found `output/P_abs.dat` and `complete/P_abs.dat` had the same shape but different numerical values. Do not mix output subsets and complete snapshots without provenance evidence.

## 本地来源
- `skills/knowledge/reference/params/atom_Heff.getP.md`
- Source audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-source.md`
- Example audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-examples.md`

