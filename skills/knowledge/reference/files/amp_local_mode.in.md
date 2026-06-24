# amp_local_mode.in

## 文件作用
在 `Model atomic_effective_H` 中读取初始构型，包括各局域模式幅值和各 strain 模式大小。

## 何时需要
当 `Model atomic_effective_H` 中 `Read_init_spin = T` 时，需要从该文件读取初始构型。

## 关键字段/内容
文件格式与 MC 输出文件 `lowest_ene.amp_local_mode` 一致，内容包括：
- 逐个原子的局域模式幅值
- 文件末尾一行给出 strain 分量

一般形式：
- 前若干行：`local-mode/site 编号 + 若干局域模式分量`
- 最后一行：strain 的若干分量

## 注意事项
- 行首编号是当前 `atomic_effective_H` local-mode / active site basis 中的连续编号，通常从 1 开始连续递增；它不是原始结构文件中的全局 atom id
- 对纯 spin local-mode / magnetic-site dynamics，非活动原子（例如 O 配位原子）不占用 `amp_local_mode.in` 的行首编号，也不应造成 `1, 2, 5, 6, ...` 这类按全局 atom id 跳号的序列
- 行数必须与当前 `SuperCell` 下的 local-mode/site basis 匹配。缩小 smoke test 的 `SuperCell` 时，不能复用原 production 超胞的 `amp_local_mode.in`
- 原子 / site 编号与坐标对应关系、以及每个 site 的局域模式个数，可在同基底的 `lowest_ene.str_mode_amp`、`amp_local_mode.out`、`def_local_modes.dat`、`mode_def.input` 或 upstream README / PROGRESS 中查询
- 如果最初没有这些文件，文档建议可先不设初态，做一次少步数 MC，先生成相应输出
- `Model Invariant` 在分析指定或随机构型时生成的 `*.amp_local_mode` 文件，与这里要求的格式一致，可直接改名后复用
- 若该文件来自上游 `amp_local_mode.out`，记录上游 run id、source path、output-validation evidence 和 copy/rename 动作；不要只因为文件名相同就认为同基底

## 最小示例
```text
1 2.901785753659 -4.162823203431 3.369777246670
2 3.186716707285 -4.515955600339 3.587299249456
...
0.000000000000 0.000000000000 0.000000000000 0.000000000000 0.000000000000 0.000000000000
```

## 来源章节
- 3.11 `amp_local_mode.in`
- 锚点：`#amp-local-mode-in`
