# knb

## 模块用途
用于自旋序诱导铁电性的统一极化模型，含格点间项、单格点项以及可选的自旋-晶格耦合修正。

## 常见相关设置
- 极化参数与对称化：`GKNB.symP`、`block GKNB_inter_site`、`block GKNB_single_site`、`block GKNB.local_axis`
- 螺旋自旋结构：`GKNB.spiral`、`block GKNB.qvec`、`block GKNB.spiral_plane_vec`
- 自旋-晶格或应力相关：`spin_lat.spin_force`、`spin_lat.Lspin_int_only`、`spin_lat.Lstrain_only`、`spin_lat.spin_int_stress`
- 声子或力常数相关：`phonopy_force_constant`、`phon.lasr`、`phon.sym_born_chg`

## 何时使用
- 需要从给定自旋构型计算极化
- 研究自旋-晶格耦合、应变或离子位移对极化贡献时
- 处理螺旋磁序诱导极化时

## 注意事项
- `GKNB_inter_site` 与 `GKNB_single_site` 都依赖局域坐标系定义；若后续 `GKNB.local_axis` 与参数拟合时所用坐标系不同，程序会做分量变换
- 若启用 `GKNB.spiral = T`，通常还需配套设置 `qvec` 和 `spiral_plane_vec`
- `spin_lat.Lspin_int_only = T` 时会忽略离子位移和应变自由度
- 若用 Born 电荷和力常数，还需注意是否做对称化或 ASR 修正

## 来源章节
- 3.1.10 自旋序诱导铁电性统一极化模型常用设置项
- 锚点：`#id19`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id19>
