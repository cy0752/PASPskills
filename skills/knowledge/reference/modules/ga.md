# ga

## 模块用途
用于全局结构搜索，当前文档重点是 GA（遗传算法）相关控制参数。

## 常见相关设置
- 演化规模：`GA.population_size`、`GA.max_generation`、`save_str.nsave_str`
- 遗传操作：`GA.perturbation`、`GA.Pher`、`GA.Pmut`、`GA.lchk_mut`
- 对称性与结构比较：`str.init_sym`、`GA.symmetrize_str`、`GA.useBCM`、`GA.tol_BCM`
- 并行与外场：`GA.parallel`、`GA.pressure`
- 空间群随机结构：`GA.gen_ran_str_sym`、`GA.spg_front`、`GA.spg_rear`
- 磁性搜索：`GA.magnetic`、`GA.random_magnetic`、`GA.lAFM_GA`、`GA.lmut_mag_GA`、`GA.flip_spin_rate`、`GA.ldiff_str_with_mag_GA`、`GA.lread_OUTCAR_mag`
- 晶格或晶胞约束：`GA.fixlattice`、`GA.fix_cell`、`GA.biaxial_strain`、`block GA.lat_fix_2D_Ang`

## 何时使用
- 做晶体全局结构搜索
- 需要控制初始结构生成、交叉/突变策略、磁构型搜索或二维应变约束时

## 注意事项
- `GA.fixlattice = T` 时，`GA.fix_cell` 也必须为 `T`
- 若启用随机空间群生成，需要同时关注 `GA.spg_front/rear` 范围
- 做磁性结构搜索时，要明确是否随机生成磁构型，还是按磁空间群生成

## 来源章节
- 3.1.8 全局结构搜索常用设置项
- 锚点：`#id17`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id17>
