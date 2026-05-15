# block unit_cell_in_Ang

## 含义
原胞基矢信息。三行分别提供三个基矢的信息，每行的三个数据是基矢的三个笛卡尔坐标分量，只能以埃作为单位。

## 默认值
缺省时原胞基矢与晶胞基矢相同（由“ block LatticeVectors ”设置，参见3.1.3.4节）。

## 取值
3×3可逆矩阵，矩阵元为实数

## 何时使用
- 当使用 `3.1.4.2 block unit_cell_in_Ang` 相关功能并需要设置 `block unit_cell_in_Ang` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.4.2 block unit_cell_in_Ang
- 锚点：`#block-unit-cell-in-ang`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#block-unit-cell-in-ang>
