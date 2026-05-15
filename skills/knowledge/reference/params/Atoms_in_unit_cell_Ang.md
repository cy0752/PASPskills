# block Atoms_in_unit_cell_Ang

## 含义
原胞中原子坐标信息以及元素信息。每行对应原胞中的一个原子，前三个数据是三个坐标分量（只能采用笛卡尔坐标，以埃为单位），第四个数据为元素的编号（对于所研究体系中包含的元素，从1开始编号），之后的数据不读取。为了与cell.str的相应内容保持格式一致，习惯上在每行后面补充两个数据——第五个数据为元素的化学符号，第六个数据为原子的编号（对于所研究体系中的所有原子，从1开始编号）。

## 默认值
缺省时该部分信息与晶胞一致（由“ block AtomicCoordinatesAndAtomicSpecies ”设置，参见3.1.3.6节）。

## 取值
略，详见“描述”

## 何时使用
- 当使用 `3.1.4.3 block Atoms_in_unit_cell_Ang` 相关功能并需要设置 `block Atoms_in_unit_cell_Ang` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.4.3 block Atoms_in_unit_cell_Ang
- 锚点：`#block-atoms-in-unit-cell-ang`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#block-atoms-in-unit-cell-ang>
