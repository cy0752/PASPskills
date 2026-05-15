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
- 对交换路径分析来说，超胞过小会导致较远近邻识别错误

## 常见误区
- 误以为 `SuperCell` 是基于 `unit_cell.str` 扩胞；实际是基于 `cell.str`
- `cell.str` 已经扩过胞，但又在 `SuperCell` 中重复放大，导致体系规模失控
- 在 L3 Path A 中把“输入文件未显式给出扩胞矩阵”误判为“用户不需要扩胞”；正确做法是确认目标 DFT 超胞矩阵、目标原子数或目标 POSCAR 规模

## 相关条目
- `topics/PASP.input.md`
- `files/cell.str.md`
- `files/unit_cell.str.md`

## 来源章节
- 官方文档: `3.1.2.2 block SuperCell`
- 来源页面: https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#block-supercell
