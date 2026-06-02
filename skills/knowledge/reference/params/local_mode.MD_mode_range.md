# local_mode.MD_mode_range

## 含义
`local_mode.MD_mode_range` defines lower and upper bounds used by the `atomic_effective_H` MD path for local-mode amplitudes.

The audited source stops if any upper bound is smaller than the corresponding lower bound. Lecture-5 BaTiO3 `MD-1` uses a three-row block for three local-mode components, but the general row-count rule for every possible basis is not fully established by curated reference.

## 默认值
Not established by curated reference.

## 取值 / 格式
Block of lower/upper real-number pairs. Exact row count and component mapping must be confirmed against current mode basis, source-backed behavior, or user authority before writing.

## 何时使用
- `Model atomic_effective_H`.
- `atom_Heff.MD T`.
- MD workflow needs hard bounds on local-mode amplitudes.

## 注意事项
- Before formal input promotion, preflight must check row count / component scope against the current local-mode basis.
- Lower bound must be less than or equal to upper bound.
- Lecture-5 `MD-1` values are historical BaTiO3 example settings only, not defaults.

## 本地来源
- Source audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-source.md`
- Lecture/example audit: `.trellis/tasks/06-01-build-l5-batio3-hysteresis-workflow/research/l5-batio3-slides.md`

