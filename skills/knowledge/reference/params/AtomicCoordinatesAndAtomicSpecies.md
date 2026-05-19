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
- 在 `Model find_J_path_sym` 中，该 block 的第四列 `species_id` 必须按 species 分组并非递减：所有 species 1 原子连续写完，再写 species 2，依次类推。PASP 源码会检查 `isa(ia) < isa(ia-1)` 并停止报 `find_J_path_sym: species are not ordered!`。该检查对象是第四列读入的 `isa`，不是第六列 atom index。
- 从 primitive / `unit_cell.str` / POSCAR 扩成 supercell-style `cell.str` 时，不要按超胞 tile 顺序输出 `Ni I I Ni I I ...` 这类 interleaved 原子。应先生成完整坐标集，再按 species id 排序 / 分组输出；第六列 atom index 虽不被 PASP 读取，也应保持唯一有效并可追溯。
- 对多 species `find_J_path_sym`，也不要把 primitive / interleaved `cell.str` 留给 PASP 的非单位 `%block SuperCell` 自动扩胞，除非已经证明扩胞后的全局 `isa` 仍非递减。源码 `coor.F` 会按 cell copy 复制 `isa`，primitive 顺序 `1,2,2` 会成为 `1,2,2,1,2,2...`。稳妥路线是写完整目标超胞版 `cell.str`、按第四列 species id 分组；如果这个 `cell.str` 已经是目标超胞，则 `%block SuperCell` 保持单位阵。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.3.6 block AtomicCoordinatesAndAtomicSpecies
- 锚点：`#block-atomiccoordinatesandatomicspecies`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#block-atomiccoordinatesandatomicspecies>
