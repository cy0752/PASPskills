# elastic.dat

## 文件作用
为 `Model Spin_lattice_interaction` 提供应变张量、弹性常数、压电张量等信息。

## 何时需要
做自旋序诱导极化，并显式考虑应变、弹性或压电响应时使用。

## 关键字段或内容
- 第一行：原胞中的原子个数，需要手动填写
- 后续内容包括：
  - internal strain tensors
  - ion-clamped elastic constants
  - ion-clamped piezoelectric tensor

## 注意事项
- 第一行需用户手动补上原子数
- 其余主体内容通常从 VASP DFPT 的 `OUTCAR` 中截取

## 来源章节
- 3.13 `elastic.dat`
- 锚点：`#elastic-dat`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#elastic-dat>
