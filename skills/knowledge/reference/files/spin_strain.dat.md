# spin_strain.dat

## 文件作用
提供海森堡交换参数 `J` 对六个应变自由度的导数。

## 何时需要
在 `Model Spin_lattice_interaction` 中考虑交换相互作用随应变变化时使用。

## 关键字段或内容
- 第一行：后续有几行数据
- 每行内容：
  - 第几个相互作用 `J`
  - 该 `J` 对 6 个应变分量的导数
- `J` 的编号对应 `spin_exchange.dat` 第一部分中的定义顺序

## 注意事项
- 导数单位为 eV
- 必须保证 `J` 的编号与 `spin_exchange.dat` 一致

## 来源章节
- 3.14 `spin_strain.dat`
- 锚点：`#spin-strain-dat`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#spin-strain-dat>
