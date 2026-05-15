# MC.input

## 文件作用
提供蒙特卡洛模拟（MC）、并行回火/并行温度蒙特卡洛（PTMC）以及 CG 局域优化相关设置。

## 何时需要
- 使用 `Model Spin_lattice_interaction`
- 使用 `Model atomic_effective_H`
- 需要进行 MC、PTMC、CG 局域优化、从文件读取初始构型、对局域模式或应变加约束时

## 关键字段/内容
### 基本启用项
- `MC T/F`：是否开启 MC
- `Parallel_Tempering T/F`：是否开启 PTMC
- `Read_init_spin T/F`：是否读取初态
  - `Spin_lattice_interaction`：读 `spin3.in`
  - `atomic_effective_H`：读 `amp_local_mode.in`

### 温度相关
- `Temperature`：普通 MC 温度（Hartree）
- `PT.M`：温度副本数，必须是并行进程数的整数倍
- `PT.low_temp`
- `PT.high_temp`
- `PT.Tmesh`：温度分布方式（`1` 为 1/T 均匀，`2` 为 T 均匀）

### PTMC 步数与统计
- `nblk`
- `PT.nblk_T`
- `nbeg_blk`
- `PT.niter`

### 其他 MC 相关
- `atom_Heff.homogeneous_strain`
- `atom_Heff.inhomogeneous_strain`
- `global.heat_bath`

### CG 局域优化
- `atom_Heff.relax_str`
- `spin_lat.relax_str`
- `opt.NSW`
- `opt.EDIFFG`

### 约束
- `%block local_mode.MC_mode_range`：对局域模式和应变设置硬边界

## 注意事项
- 该文件中的设置也可直接写进 `PASP.input`
- `MC` 与 `MD` 不能同时开启
- `PT.M` 若不是并行进程数的整数倍，会直接报错终止
- PTMC 时 `Temperature` 设置不起作用，温度由 PT 参数控制
- 文档建议先用较小步数测试，确认无误后再增大正式计算参数

## 最小示例
```text
MC T
Parallel_Tempering T
Read_init_spin T
PT.M 64
PT.low_temp 0.000001
PT.high_temp 0.002
PT.Tmesh 2
opt.NSW 1000
opt.EDIFFG -0.1E-06
```

## 来源章节
- 3.1.5 `MC.input`
- 锚点：`#mc-input-cg`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#mc-input-cg>
