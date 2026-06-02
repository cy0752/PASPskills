# Field_for_Electrocaloric

## 含义
`Field_for_Electrocaloric` is a block read by the audited `atomic_effective_H` MD source when `MD.E_type == 4`.

The source audit found that the block provides timing values and three electric-field vectors for a piecewise electrocaloric field schedule.

## 默认值
No default block. If `MD.E_type == 4`, missing or inconsistent block data can stop the run.

## 取值 / 格式
Exact line-by-line syntax is not fully established in curated reference. Treat this as a reference gap for writing.

## 何时使用
- Only when `MD.E_type == 4`.
- Electric-field MD workflow needs a piecewise electrocaloric field schedule.

## 注意事项
- `MD.E_type == 4` has timing consistency checks in source. The audited source stops if the second plateau time is earlier than the first time plus ramp time.
- Do not generate this block from memory or from a similar example. Require authoritative syntax / user-provided source before writing a formal input.
- For BaTiO3 hysteresis with a simple cosine field, this block is not the observed Lecture-5 `MD-1` route.

## 本地来源
- Source audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-source.md`

