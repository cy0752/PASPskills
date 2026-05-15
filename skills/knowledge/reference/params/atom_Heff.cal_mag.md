# atom_Heff.cal_mag

## 含义
`atom_Heff.cal_mag` 控制 `Model atomic_effective_H` 且存在 spin-mode 时，PTMC 统计阶段是否把 local-mode amplitude 转换回结构 / spin 信息来计算磁化相关量。

源码中该参数读入变量 `latomHeff_cal_mag`，默认值为 `T`。在 `PTMC_measure.F90` 中，当 model 为 `atomic_effective_H` 且 `lhave_spin_mode` 为真时，只有 `latomHeff_cal_mag` 为真才调用 `mode_amp_to_str(...)` 将 amplitude 转为 `str`，后续再汇总 `spin3`、`Mt`、`Mts`、`Mzcol` 等磁化相关量。

Lecture-4 的 YIG example 说明，设置 `atom_Heff.cal_mag F` 会导致 `M_PTMC_K.dat` 中平均自旋结果为 0；若需要正确磁化输出，应设置 `atom_Heff.cal_mag T`。

## 默认值
`T`

## 取值
`T/F`

## 何时使用
- 使用 `Model atomic_effective_H`。
- 当前模型包含 spin mode。
- 用户目标包括 `M_PTMC_K.dat`、`Mabs_PTMC*`、`Mz_PTMC*`、`M2_PTMC*` 等磁化相关统计。

## 相关输出
- `M_PTMC.dat` / `M_PTMC_K.dat`
- `Mabs_PTMC.dat` / `Mabs_PTMC_K.dat`
- `Mz_PTMC.dat` / `Mz_PTMC_K.dat`
- `M2_PTMC.dat` / `M2_PTMC_K.dat`
- 其他依赖 spin 汇总的 PTMC 磁性统计输出

## 注意事项
- 若用户需要磁化曲线，不应为了节省计算直接设为 `F`。
- 若设置为 `F`，`M_PTMC_K.dat` 可能仍存在，但数值可能为 0 或不代表真实磁化；output validation 必须检查 `PASP.used_info` 中该字段的实际值。
- 该参数只解决 spin-mode `atomic_effective_H` 的磁化输出覆盖问题；不能替代 mode definition、`Spin_values`、`local_mode_PM.dat` / `J_best.dat` 的一致性检查。

## 本地来源
- 官网第 3 章参数抽取中未找到该字段；本卡片为 Lecture-4 + 源码审计补充。
- Lecture-4 markdown：`pasp_slides_md/Lecture-4.../full.md` lines 2030-2092。
- 源码读取默认值：`atom_Heff.F90` lines 372。
- 源码统计路径：`PTMC_measure.F90` lines 422-462。
- Example evidence：`pasp_examples/Lecture-4/MC-2/input/MC.input`, `MC-3/input/MC.input`, and corresponding `PASP.used_info`.
