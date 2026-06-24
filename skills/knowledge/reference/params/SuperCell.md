# SuperCell

## 含义
定义扩胞矩阵；扩胞基于 `cell.str` 中给出的结构进行。

## 写法
```text
%block SuperCell
2 0 0
0 2 0
0 0 2
%endblock SuperCell
```

## 格式
- 3×3 可逆整数矩阵
- 默认等价于不扩胞，即 1×1×1

## 何时使用
- 需要在 `cell.str` 给出的结构基础上进一步扩胞时
- L3 Path A 需要让 PASP 生成后续 DFT 样本结构 / POSCAR，且目标 DFT 计算应在比当前 `cell.str` 更大的超胞中完成时
- 在 MC、MD、exchange path 分析等任务中经常出现

## 注意事项
- PASP 把 `cell.str` 提供的结构视为输入晶胞，经 `SuperCell` 得到超胞
- 如果 `cell.str` 本身已经是所需大超胞，`SuperCell` 往往可保持为单位阵
- 如果 `cell.str` 与 `unit_cell.str` 内容相同，只能说明当前提供的晶胞和原胞相同；这不等于用户的目标 DFT / 样本生成超胞就是 1×1×1
- 在 L3 Path A 中，`SuperCell` 是目标样本 / DFT 结构规模的建模确认项。不要因为用户只提供了 `cell.str` 和 `unit_cell.str`，或两者相同，就自动省略 `SuperCell`
- 在 `Model atomic_effective_H` MD / SLD 提交前，还必须把计划 MPI ranks 与当前 supercell factors 一起检查。合法 ranks 需要能写成 `p1 * p2 * p3`，且三个 `p_i` 分别整除 supercell 三个方向的 factors；仅仅让 ranks 整除总 site 数或原子数不够。比如 `8x8x8` 可用 `64 = 4x4x4`，但 `54` 不合法；`6x6x6` 可用 `54 = 3x3x6`。
- 对交换路径分析来说，超胞过小会导致较远近邻识别错误
- 对多 species `Model find_J_path_sym`，不要依赖非单位 `SuperCell` 从 primitive / interleaved `cell.str` 自动扩胞，除非已证明扩胞后的全局 `isa` 仍非递减。PASP 会按 cell copy 复制 species id；primitive 顺序如 `1,2,2` 会扩成 `1,2,2,1,2,2...`，再被 `find_J_path_sym` 的 species-order 检查拒绝。安全路线是把完整目标分析超胞直接写入 `cell.str`，按第四列 species id 分组，并在该 `cell.str` 已是目标超胞时保持 identity `SuperCell`。

## 常见误区
- 误以为 `SuperCell` 是基于 `unit_cell.str` 扩胞；实际是基于 `cell.str`
- `cell.str` 已经扩过胞，但又在 `SuperCell` 中重复放大，导致体系规模失控
- 在 L3 Path A 中把“输入文件未显式给出扩胞矩阵”误判为“用户不需要扩胞”；正确做法是确认目标 DFT 超胞矩阵、目标原子数或目标 POSCAR 规模
- 在多 species `find_J_path_sym` 中把非单位 `SuperCell` 当成安全的 primitive 扩胞工具，却没有验证扩胞后的第四列 `isa` 全局仍按 species 分组

## 相关条目
- `topics/PASP.input.md`
- `files/cell.str.md`
- `files/unit_cell.str.md`

## 来源章节
- 官方文档: `3.1.2.2 block SuperCell`
- 来源页面: https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#block-supercell
