# cell.str

## 文件作用
提供晶胞结构信息；也可在某些情况下直接提供原胞或超胞信息。若 `PASP.input` 中使用了 `%block SuperCell`，则是在 `cell.str` 给出的结构基础上扩胞。

## 何时需要
- 需要显式提供晶胞结构时
- 想在 `PASP.input` 外单独维护结构文件时
- 需要从 `cell.str` 出发再做扩胞时
- 也可不单独建文件，把同样内容直接写进 `PASP.input`

## 关键字段/内容
- `NumberOfAtoms`：晶胞原子数
- `number_of_species`：元素种类数
- `LatticeConstant`：基矢单位，如 `1 Ang`
- `%block LatticeVectors ... %endblock`：3×3 晶格基矢
- `AtomicCoordinatesFormat`：坐标格式，常用 `NotScaledCartesianAng`；也支持 `Bohr`、`ScaledCartesian`、`Fractional`
- `%block AtomicCoordinatesAndAtomicSpecies ... %endblock`：原子坐标与元素信息。每行前 5 项有效：`x y z species_id symbol`；第 6 项常写原子编号，但程序不读取

## 注意事项
- 使用该文件时，需要在 `PASP.input` 中写 `%include cell.str`
- 若文件缺失，程序会生成默认 `cell.str`；但只有 `PASP.input` 里确实写了 `%include cell.str` 时，生成内容才会被读取
- 文档明确说明：其中部分设置项不可缺省，尤其原子坐标块不可省
- 若 `PASP.input` 同时写了 `%block SuperCell`，扩胞起点就是这里的 `cell.str`；如果 `cell.str` 本身已经是目标超胞，不要再用非单位阵 `SuperCell` 重复扩胞
- 对 `Model find_J_path_sym`，`%block AtomicCoordinatesAndAtomicSpecies` 还必须按第四列 `species_id` 分组并保持非递减顺序：先写全部 species 1 原子，再写全部 species 2 原子，依次类推。PASP 检查的是第四列读入的 `isa`，不是第六列 atom index。若从 `unit_cell.str` / POSCAR 扩成 supercell-style `cell.str`，不要按 tile-by-tile 输出 `Ni I I Ni I I ...` 这类交错顺序；应先生成所有坐标，再按 species id 分组写出，并保持坐标、species id、元素符号和第六列 atom index / 映射有效。
- 对多 species `find_J_path_sym`，不要依赖非单位 `%block SuperCell` 从 primitive / 交错 `cell.str` 自动扩胞，除非已证明扩胞后的全局 `isa` 仍非递减。`coor.F` 会按 cell copy 复制 species id，因此 primitive 顺序 `1,2,2` 会扩成 `1,2,2,1,2,2...` 并触发后续 order stop。安全写法是让 `cell.str` 直接包含完整目标分析超胞、按 species id 分组；若它已经是目标超胞，`SuperCell` 保持单位阵或等价不扩胞设置。
- 也支持用 `POSCAR` 代替：设置 `READ_POSCAR T`
- 如果只有 VASP `POSCAR`，通常可以把它作为 `cell.str` 的来源；但若该 `POSCAR` 是超胞，不要自动把它也当成 `unit_cell.str` 来源。需要原胞时先看 `topics/structure_from_poscar.md`

## 最小示例
```text
NumberOfAtoms 1
number_of_species 1
LatticeConstant 1 Ang

%block LatticeVectors
1 0 0
0 1 0
0 0 1
%endblock LatticeVectors

%block AtomicCoordinatesAndAtomicSpecies
0 0 0 1 H 1
%endblock AtomicCoordinatesAndAtomicSpecies
```

## 来源章节
- 3.1.3 `cell.str`
- 锚点：`#cell-str`
