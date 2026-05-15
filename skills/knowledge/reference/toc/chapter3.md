# PASP reference TOC（第 3 章）

来源页面：
https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html

---

## 3 输入文件、输出文件介绍
- 锚点：`#id1`

### 3.1 核心输入文件PASP.input
- 锚点：`#pasp-input`

#### 3.1.1 PASP.input文件读取规则
- 锚点：`#id3`

#### 3.1.2 最常用设置项
- 锚点：`#id4`

##### 3.1.2.1 Model
- 锚点：`#model`

##### 3.1.2.2 block SuperCell
- 锚点：`#block-supercell`

##### 3.1.2.3 block Z_values
- 锚点：`#block-z-values`

##### 3.1.2.4 block isaAB
- 锚点：`#block-isaab`

##### 3.1.2.5 自旋大小与外磁场设置
- 锚点：`#id5`

#### 3.1.3 附属文件cell.str：晶胞信息
- 锚点：`#cell-str`

##### 3.1.3.1 NumberOfAtoms
- 锚点：`#numberofatoms`

##### 3.1.3.2 number_of_species
- 锚点：`#number-of-species`

##### 3.1.3.3 LatticeConstant
- 锚点：`#latticeconstant`

##### 3.1.3.4 block LatticeVectors
- 锚点：`#block-latticevectors`

##### 3.1.3.5 AtomicCoordinatesFormat
- 锚点：`#atomiccoordinatesformat`

##### 3.1.3.6 block AtomicCoordinatesAndAtomicSpecies
- 锚点：`#block-atomiccoordinatesandatomicspecies`

##### 3.1.3.7 用POSCAR文件代替cell.str (READ_POSCAR)
- 锚点：`#poscarcell-str-read-poscar`

##### 3.1.3.8 利用原胞的POSCAR文件扩胞
- 锚点：`#poscar`

#### 3.1.4 附属文件unit_cell.str：原胞信息
- 锚点：`#unit-cell-str`

##### 3.1.4.1 unit_cell.na
- 锚点：`#unit-cell-na`

##### 3.1.4.2 block unit_cell_in_Ang
- 锚点：`#block-unit-cell-in-ang`

##### 3.1.4.3 block Atoms_in_unit_cell_Ang
- 锚点：`#block-atoms-in-unit-cell-ang`

##### 3.1.4.4 用POSCAR_UC文件代替unit_cell.str (READ_POSCAR_UC)
- 锚点：`#poscar-ucunit-cell-str-read-poscar-uc`

#### 3.1.5 附属文件MC.input：蒙特卡洛模拟与CG局域优化相关设置
- 锚点：`#mc-input-cg`

##### 3.1.5.1 自定义初态 (Read_init_spin)
- 锚点：`#read-init-spin`

##### 3.1.5.2 PTMC温度相关设置
- 锚点：`#ptmc`

##### 3.1.5.3 PTMC模拟步数与统计相关设置
- 锚点：`#id6`

##### 3.1.5.4 MC相关的其他设置
- 锚点：`#mc`

##### 3.1.5.5 CG局域优化的相关设置
- 锚点：`#cg`

##### 3.1.5.6 MC和CG中添加约束条件
- 锚点：`#mccg`

#### 3.1.6 附属文件MD.input：分子动力学模拟相关设置
- 锚点：`#md-input`

#### 3.1.7 有效哈密顿量方法常用设置项
- 锚点：`#id12`

##### 3.1.7.1 展开体数 (fig.maxk)
- 锚点：`#fig-maxk`

##### 3.1.7.2 截断距离 (block fig.mdist)
- 锚点：`#block-fig-mdist`

##### 3.1.7.3 展开阶数相关设置
- 锚点：`#id13`

##### 3.1.7.4 SOC相关设置
- 锚点：`#soc`

##### 3.1.7.5 自定义局域模式 (block local_mode.mode_definition)
- 锚点：`#block-local-mode-mode-definition`

##### 3.1.7.6 读取已有相互作用信息 (local_mode.read_interaction)
- 锚点：`#local-mode-read-interaction`

##### 3.1.7.7 随机生成构型或自定义构型的相关设置
- 锚点：`#id14`

##### 3.1.7.8 Model find_J_path_sym 的其他设置
- 锚点：`#model-find-j-path-sym`

##### 3.1.7.9 Model Invariant 的其他设置
- 锚点：`#model-invariant`

#### 3.1.8 全局结构搜索常用设置项
- 锚点：`#id17`

#### 3.1.9 紧束缚模型方法常用设置项
- 锚点：`#id18`

#### 3.1.10 自旋序诱导铁电性统一极化模型常用设置项
- 锚点：`#id19`

#### 3.1.11 线性自旋波色散计算常用设置项
- 锚点：`#id20`

### 3.2 输入/输出文件seed.in：随机数种子
- 锚点：`#seed-in`

### 3.3 输入文件spin_exchange.dat
- 锚点：`#spin-exchange-dat`

### 3.4 输入文件distortion.pos
- 锚点：`#distortion-pos`

### 3.5 输入文件distortion.MAGMOM
- 锚点：`#distortion-magmom`

### 3.6 输入/输出文件local_mode_PM.dat
- 锚点：`#local-mode-pm-dat`

### 3.7 输入文件J_best.dat
- 锚点：`#j-best-dat`

### 3.8 输入文件Fitting_Settings.txt
- 锚点：`#fitting-settings-txt`

### 3.9 输入文件Fitting_Set_Lambda.txt
- 锚点：`#fitting-set-lambda-txt`

### 3.10 输入文件spin3.in
- 锚点：`#spin3-in`

### 3.11 输入文件amp_local_mode.in
- 锚点：`#amp-local-mode-in`

### 3.12 输入文件Zeff.dat
- 锚点：`#zeff-dat`

### 3.13 输入文件elastic.dat
- 锚点：`#elastic-dat`

### 3.14 输入文件spin_strain.dat
- 锚点：`#spin-strain-dat`

### 3.15 输入文件DM_derivative.dat
- 锚点：`#dm-derivative-dat`

### 3.16 输出文件PASP.used_info
- 锚点：`#pasp-used-info`
