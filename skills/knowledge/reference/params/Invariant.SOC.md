# Invariant.SOC

## 含义
在有效哈密顿量方法模块中，处理磁性体系时常用。用于设定是否考虑SOC（自旋轨道耦合）。

## 默认值
T

## 取值
T/F

## 何时使用
- 当使用 `3.1.7.4 SOC相关设置` 相关功能并需要设置 `Invariant.SOC` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 在 `Model Invariant` / L3 共享基底中，如果设置 `Invariant.SOC T`，第一次生成相互作用基底的运行必须同时写入 reference-confirmed 的 `%block local_mode.special_SOC`。不能先缺省 `local_mode.special_SOC` 跑一次，再在后续 method-6、拟合、MC 或 MD 阶段补加 SOC 保留策略。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.7.4 SOC相关设置
- 锚点：`#soc`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#soc>
