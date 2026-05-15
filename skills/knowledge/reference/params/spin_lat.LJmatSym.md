# spin_lat.LJmatSym

## 含义
在“Model Spin_lattice_interaction”中，以矩阵形式提供J矩阵等参数时（即“ spin_lat.general_J ”取T时），是否根据所涉及的原子所满足的空间对称性的要求，将描述两体相互作用的J矩阵（或描述单体项的SIA矩阵）修正成符合对称性的形式。通常在“ spin_lat.general_J ”取T时也应取T。

## 默认值
F

## 取值
T/F

## 何时使用
- 当使用 `3.1.5.4 MC相关的其他设置` 相关功能并需要设置 `spin_lat.LJmatSym` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.5.4 MC相关的其他设置
- 锚点：`#mc`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#mc>
