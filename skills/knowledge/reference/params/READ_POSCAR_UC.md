# READ_POSCAR_UC

## 含义
如果已有原胞的 POSCAR 文件（VASP软件的常用输入文件之一），也可以直接用它取代 unit_cell.str 作为原胞结构的输入文件。此时需要在 PASP.input 中将此项设为T；该项设置为T时，还会自动生成相应的 unit_cell.str 文件。这里需要提供的 POSCAR_UC 文件兼容以下两种格式：A.第一行提供任意内容，第五行提供各元素符号，第六行提供各元素的原子个数（参见3.1.3.8节格式A示例文件POSCAR）；B.第一行提供各元素符号，第五行直接提供各元素的原子个数（参见3.1.3.8节格式B示例文件POSCAR）。

## 默认值
F

## 取值
T/F

## 何时使用
- 当使用 `3.1.4.4 用POSCAR_UC文件代替unit_cell.str (READ_POSCAR_UC)` 相关功能并需要设置 `READ_POSCAR_UC` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。
- 该设置读取 `POSCAR_UC` 后，自动生成的 `unit_cell.str` 只保证结构等价，不保证一定保留你原先期望的 `a/b/c` 轴标签顺序；若后续 workflow 依赖特定轴向约定，应先检查生成结果是否与当前 `cell.str` / `cellabc` 语境一致。

## 来源章节
- 3.1.4.4 用POSCAR_UC文件代替unit_cell.str (READ_POSCAR_UC)
- 锚点：`#poscar-ucunit-cell-str-read-poscar-uc`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#poscar-ucunit-cell-str-read-poscar-uc>
