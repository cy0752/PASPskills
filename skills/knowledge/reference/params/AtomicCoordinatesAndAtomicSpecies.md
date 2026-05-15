# block AtomicCoordinatesAndAtomicSpecies

## 含义
晶胞中原子坐标信息以及元素信息。每行对应原胞中的一个原子，前三个数据是三个坐标分量（格式由“AtomicCoordinatesFormat”内容指定），第四个数据为元素的编号（对于所研究体系中包含的元素，从1开始编号），第五个数据为元素的化学符号。软件只读取每行的前五个数据，后面的数据无效。习惯上，我们常在每行添加第六个数据，这个数据是原子的编号（对于所研究体系中的所有原子，从1开始编号）。

## 默认值
不可缺省（缺省时报错”coo: You must specify the atomic coordinates”）。

## 取值
详见“描述”。

## 何时使用
- 当使用 `3.1.3.6 block AtomicCoordinatesAndAtomicSpecies` 相关功能并需要设置 `block AtomicCoordinatesAndAtomicSpecies` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.3.6 block AtomicCoordinatesAndAtomicSpecies
- 锚点：`#block-atomiccoordinatesandatomicspecies`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#block-atomiccoordinatesandatomicspecies>
