# DM_derivative.dat

## 文件作用
提供 DM 相互作用参数对离子位移的导数。

## 何时需要
在 `Model Spin_lattice_interaction` 中考虑 DM 相互作用随原子位移变化时使用。

## 关键字段或内容
- 第一行：后续有几组数据
- 每组数据包含：
  - 组号
  - 对应第几种 DM 相互作用
  - 3×3 扩胞基矢矩阵（Å）
  - 当前 DM 相互作用对应多少原子位置的偏导信息
  - 各原子笛卡尔坐标（Å）
  - DM 的 x/y/z 分量分别对各原子坐标分量的偏导（eV/Å）

## 注意事项
- DM 编号对应 `spin_exchange.dat` 第四部分中的定义顺序
- 通常原子数等于扩胞后胞内原子数
- 数据量较大，格式必须严格按文档顺序组织

## 来源章节
- 3.15 `DM_derivative.dat`
- 锚点：`#dm-derivative-dat`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#dm-derivative-dat>
