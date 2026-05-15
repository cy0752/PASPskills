# fig.maxk

## 含义
设置模型最多考虑到几体相互作用。

## 写法
```text
fig.maxk 4
```

## 何时使用
- 在有效哈密顿量建模中控制相互作用体数时
- 在需要显式限制模型复杂度时

## 常见理解
- `2` 表示最多考虑二体项
- `4` 表示最多考虑到四体项

## 注意事项
- 它与 `block fig.mdist` 应配套理解：体数决定考虑几体，相应截断距离决定每一体的空间范围
- 体数越高，模型项数可能增长很快
- 当单体高于 6 阶、二体及以上高于 4 阶时，程序可能变得很慢

## 常见误区
- 只调大 `fig.maxk`，但没有同步评估样本数量和拟合稳定性
- 把它当成“展开阶数”；实际上展开阶数通常由 `Invariant.power` 等字段控制

## 相关条目
- `modules/effective_hamiltonian.md`
- `topics/PASP.input.md`

## 来源章节
- 官方文档: `3.1.7.1 展开体数`
- 来源页面: https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#fig-maxk
