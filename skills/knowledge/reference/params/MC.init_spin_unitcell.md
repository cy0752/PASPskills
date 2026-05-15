# MC.init_spin_unitcell

## 含义
`MC.init_spin_unitcell` 控制 `Model atomic_effective_H` 在 `Read_init_spin T` 时从哪类 local-mode amplitude 初态文件读取初始构型。

源码中该参数读入变量 `LRead_init_spin_unitcell`，默认值为 `F`。在 `atomic_effective_H` 的 MC 初始化里：
- `MC.init_spin_unitcell T`：读取 `amp_local_mode.in_unitcell`，并调用 unit-cell amplitude 读取路径。
- `MC.init_spin_unitcell F`：读取 `amp_local_mode.in`。

Lecture-4 说明新版 PASP 中设置 `MC.init_spin_unitcell T` 后，可读取 `amp_local_mode.in_unitcell`；默认超胞中所有位点的局域模式幅值同原胞保持一致。

## 默认值
`F`

## 取值
`T/F`

## 何时使用
- 使用 `Model atomic_effective_H`。
- `Read_init_spin T`。
- 初始 local-mode amplitude 只按 unit cell 给出，希望由 PASP 扩展到当前 supercell。

## 相关文件
- `amp_local_mode.in_unitcell`：`MC.init_spin_unitcell T` 时读取。
- `amp_local_mode.in`：`MC.init_spin_unitcell F` 时读取。
- `MC.input`：Lecture-4 examples 中该参数写在 `MC.input`。

## 注意事项
- 该参数只有在读取初态时才有实际意义；若 `Read_init_spin F`，不要把它当成独立的初始化开关。
- `amp_local_mode.in_unitcell` 的完整格式当前没有官网 reference 卡片。正式写入或修改该文件前，需要用户提供权威来源、已验证 example，或经过 read-only verifier 检查。
- 不要从 Lecture-4 example 直接继承当前任务是否应读取 unit-cell 初态；这属于 L4 设置确认项。

## 本地来源
- 官网第 3 章参数抽取中未找到该字段；本卡片为 Lecture-4 + 源码审计补充。
- Lecture-4 markdown：`pasp_slides_md/Lecture-4.../full.md` lines 611-617。
- 源码读取默认值：`read_input.F90` lines 180-183。
- 源码文件选择：`atom_Heff_MC.F90` lines 1238-1268。
- Example evidence：`pasp_examples/Lecture-4/MC-1/input/MC.input` and `MC-1/complete/PASP.used_info`.
