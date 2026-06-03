# tb

## 模块用途
用于紧束缚模型计算，支持自定义 hopping 和 Slater-Koster 参数化两种方式。

## 常见相关设置
- `USE_Slater_Koster_Model`
- `overlap.distance`
- `Different_hop_path`
- `Hop_Parameters_specified_using_site`
- `Hop_Parameters_specified_using_dis`
- `TB.complex_hop`
- `TB.write_wf`
- `TB.distance_tiny`
- `TB.additional_H`
- `TB.localized_state`
- `TB.find_H_form`
- `block Hop_Parameters`
- `block Slater_Koster_Hop_Parameters`
- `block orbitals_nl`
- `block GSD_TB_Spin_direction`
- `block TB.H_indep_var`

## 何时使用
- 构建 TB 模型时
- 已知具体 hopping 矩阵时用自定义 TB
- 希望以轨道壳层和 S-K 积分组织参数时用 S-K TB
- 需要额外哈密顿量、通用自旋依赖 TB 或 flat-band CLS 搜索时，先进入 L7 workflow 判断分支和 gate，再查具体字段

## 注意事项
- `Hop_Parameters_specified_using_site` 与 `Hop_Parameters_specified_using_dis` 必须一真一假；文档推荐使用 `...using_dis`
- 自定义 TB 时，`block Hop_Parameters` 不可缺省
- S-K TB 时，`block Slater_Koster_Hop_Parameters` 不可缺省
- 矩阵维度必须与 `block Orbitals` 中各元素或原子的轨道数一致
- 若 `TB.complex_hop = T`，每个 hopping 参数要写成 `(r,i)`
- Lecture/example 数值不是当前材料默认值；hopping、轨道能、SOC、U、CLS 目标能量等必须由用户或当前材料来源确认

## 来源章节
- 3.1.9 紧束缚模型方法常用设置项
- 锚点：`#id18`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id18>
