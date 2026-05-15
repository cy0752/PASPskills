# spin_lat.general_J

## 含义
在“Model Spin_lattice_interaction”中，是否以矩阵形式提供J矩阵等参数。主要影响到输入文件 spin_exchange.dat 的格式。取T时，每对原子间的相互作用参数需要提供9个数（矩阵信息）；取F时，每对原子间的相互作用参数仅需提供1个数（即各向同性的J值）。参见3.3节。

## 默认值
F

## 取值
T/F

## 何时使用
- 当使用 `3.1.5.4 MC相关的其他设置` 相关功能并需要设置 `spin_lat.general_J` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.5.4 MC相关的其他设置
- 锚点：`#mc`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#mc>
