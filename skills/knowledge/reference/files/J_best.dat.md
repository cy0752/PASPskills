# J_best.dat

## 文件作用
在 `Model atomic_effective_H` 中提供相互作用参数的实际取值。

## 何时需要
当已完成相互作用分析，并准备进行 MC 等模拟、需要显式指定所采用的参数集合时使用。

## 关键字段/内容
文件按严格逐行规则读取。

### 第 1 行：两个数据
1. 总相互作用数
2. 模拟中保留的参数个数（不含常数项）

### 后续每行：一个保留参数
每个保留参数一行，写两个数据：

```text
<parameter_id> <value>
```

其中参数编号需与以下输出文件中的编号一致：
- `all_interaction_type_Spin_xyzform.dat`
- `local_mode_PM.dat`

当前 PASP 读取路径使用 list-directed read，每个保留项读取 `parameter_id` 和 `value` 两个数据。未在文件中列出的参数会保持为 0 且不标记为 retained。

## 注意事项
- 不能任意插入空行
- 数据行不要写 `#` 注释或尾注；注释可能被 Fortran list-directed read 当成非法 token 或下一条记录的一部分
- 不要把值为 0 的项写成 retained row，除非用户明确要把该参数作为“保留但数值为 0”的模型选择；通常直接省略，第一行 kept count 也不计入
- 第一行第二个数必须等于后续 retained row 的行数
- 自旋向量默认已归一化，因此相互作用参数单位与能量一致，取 eV
- 如果这些值来自四态法 DFT 交换参数，写入前必须已经换算到当前 `Spin_values` / `local_mode_PM.dat` 所定义的模型自旋尺度；不要把物理自旋 `S` 下的原始 J 直接塞进归一化 spin 模型
- `parameter_id` 必须对应当前同一 `local_mode_PM.dat` / interaction list 的编号。换了结构、mode definition、`fig.maxk`、`fig.mdist`、`Invariant.power`、SOC 策略或 species / spin 顺序后，不能盲目复用旧 `J_best.dat`

## 最小示例
```text
287 4
1 0.1772080263938097E-02
3 -0.8077197635063232E-02
5 0.1859024576895017E-02
15 0.1540675214074116E-02
```

## 来源章节
- 3.7 `J_best.dat`
- 锚点：`#j-best-dat`
