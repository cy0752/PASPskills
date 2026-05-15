# unit_cell.str

## 文件作用
提供原胞信息。文档特别说明：虽然名字叫 `unit_cell`，这里通常实际指 primitive cell（原胞）。

## 何时需要
- 晶胞 `cell.str` 与原胞不一致时，需要单独给出原胞
- 涉及原胞基矢、原胞原子位置等信息时
- 若 `cell.str` 本身就给的是原胞，则通常可省略 `unit_cell.str`

## 关键字段/内容
- `unit_cell.na`：原胞原子数
- `%block unit_cell_in_Ang ... %endblock`：原胞基矢，仅支持 Å
- `%block Atoms_in_unit_cell_Ang ... %endblock`：原胞内原子坐标，仅支持 Å 下的笛卡尔坐标。每行前 4 项读取：`x y z species_id`；通常仍补写元素符号和原子编号以便与 `cell.str` 保持一致
- 也支持 `READ_POSCAR_UC T`，用 `POSCAR_UC` 代替

## 注意事项
- 使用时需在 `PASP.input` 中加入 `%include unit_cell.str`
- 若缺失且未在其他输入中提供，则默认把原胞信息视为与 `cell.str` 相同
- 文档强烈建议：若程序会用到 `unit_cell.str`，则 `cell.str` 也最好统一用 Å 和笛卡尔坐标，即：`LatticeConstant 1 Ang`、`AtomicCoordinatesFormat NotScaledCartesianAng`
- 如果只有超胞 `POSCAR`，不能直接把它当作 `unit_cell.str`。可先用 `pymatgen` 生成 primitive POSCAR / `POSCAR_UC`，再转写 `unit_cell.str`；通用步骤见 `topics/structure_from_poscar.md`
- 如果 `unit_cell.str` 是从 `POSCAR` / `POSCAR_UC` 自动生成的，不要默认它会保留你原来理解中的 `a/b/c` 轴顺序；进入 PASP 前应检查它是否仍与当前 `cell.str`、超胞矩阵和 `cellabc` 轴向约定一致

## 最小示例
```text
unit_cell.na 5

%block unit_cell_in_Ang
4.03331142642247 0 0
0 4.03331142642247 0
0 0 4.03331142642247
%endblock unit_cell_in_Ang

%block Atoms_in_unit_cell_Ang
2.01665571 2.01665571 0.00000000 1 O 1
2.01665571 0.00000000 2.01665571 1 O 2
0.00000000 2.01665571 2.01665571 1 O 3
2.01665571 2.01665571 2.01665571 2 Ti 4
0.00000000 0.00000000 0.00000000 3 Ba 5
%endblock Atoms_in_unit_cell_Ang
```

## 来源章节
- 3.1.4 `unit_cell.str`
- 锚点：`#unit-cell-str`
