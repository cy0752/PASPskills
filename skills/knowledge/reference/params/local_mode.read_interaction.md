# local_mode.read_interaction

## 含义
在有效哈密顿量方法模块中常用（包括后续的MC或MD模拟等）。在这里设置是否直接从 local_mode_PM.dat 文件中读取相互作用信息。这里用到的 local_mode_PM.dat 文件本来是分析不等价相互作用时的输出文件，如果需要再次在相同的原胞结构（参见3.1.4节）、局域模式定义、体数、截断距离、展开阶数、SOC的保留阶数等设置下调用PASP，例如获取不同构型的 *.ene_symbol 文件（允许处理不同的超胞）时，或进行后续的MC和MD模拟时，就可以直接从已有的该文件中读取所需信息。特别是使用MC或MD功能时，因为通常需要并行计算，而使用“ Model Invariant ”获取 local_mode_PM.dat 文件的步骤暂不支持并行，因此在MC或MD阶段常常必须设置该项为T，以便直接读取 local_mode_PM.dat 文件内容。

## 默认值
F

## 取值
T/F

## 何时使用
- 当使用 `3.1.7.6 读取已有相互作用信息 (local_mode.read_interaction)` 相关功能并需要设置 `local_mode.read_interaction` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.7.6 读取已有相互作用信息 (local_mode.read_interaction)
- 锚点：`#local-mode-read-interaction`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#local-mode-read-interaction>
