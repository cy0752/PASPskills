# block atom_Heff.MASS_local_mode

## 含义
MD的常用设置。提供各局域模式的等效相对原子质量信息。提供的的质量数目即为局域模式的总数目（不计入应变模式，这与“Model Invariant”阶段产生的 local_mode-*.xsf 文件个数一致），顺序通常按照“block local_mode.mode_definition”中定义各局域模式时确定的先后顺序（如果实际局域模式数大于定义中写出的局域模式数，这时顺序应当与 local_mode-*.xsf 文件的编号一致）。局域模式仅涉及一个原子时，取元素的相对原子质量；涉及多个原子时，则需要使用相应的有效质量（例如局域声子模式，常以模式定义中各原子位移的平方为权重取相对原子质量的加权平均值）。

## 默认值
缺省时全部赋值为1.0

## 取值
正实数

## 写法示例
质量值应按当前实际 local-mode count 和顺序写成同一个连续列表。推荐格式是把所有 local-mode masses 放在 block 内同一数据行：

```text
%block atom_Heff.MASS_local_mode
33.5219 33.5219 33.5219
%endblock atom_Heff.MASS_local_mode
```

这里的 `3` 个数只对应示例中的 `3` 个 local modes；实际条目数必须等于当前 local-mode 总数。不要写成“每种元素一个质量”，也不要把应变模式计入这个 block。

## 何时使用
- 当使用 `3.1.6 附属文件MD.input：分子动力学模拟相关设置` 相关功能并需要设置 `block atom_Heff.MASS_local_mode` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- block 内的 mass 顺序必须与当前 `local_mode.mode_definition` / `def_local_modes.dat` / `local_mode-*.xsf` 的 local-mode 顺序一致。
- 对集体位移/软模，质量值不能由 Agent 自动取某个元素质量；应由用户提供、材料数据计算或按已确认公式计算有效质量，并记录来源。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 相关条目
- `files/mode_mass.input.md`
- `files/def_local_modes.dat.md`
- `params/local_mode.mode_definition.md`

## 来源章节
- 3.1.6 附属文件MD.input：分子动力学模拟相关设置
- 锚点：`#md-input`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#md-input>
