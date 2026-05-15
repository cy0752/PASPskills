# global.heat_bath

## 含义
是否采用heat bath方法，T表示选用heat bath方法，F表示采用默认的Metropolis方法。处理磁性体系时heat bath算法更为高效 18 ；但该算法的使用条件较为局限，所以即使设置为T，也是只有符合适用条件时才会采用这个较高效的算法，而不符合条件时仍采用默认方法。该算法目前仅在“ Model Spin_lattice_interaction ”中支持使用，而在更具通用性的“ Model atomic_effective_H ”中无法使用。

## 默认值
F

## 取值
T/F

## 何时使用
- 当使用 `3.1.5.4 MC相关的其他设置` 相关功能并需要设置 `global.heat_bath` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.5.4 MC相关的其他设置
- 锚点：`#mc`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#mc>
