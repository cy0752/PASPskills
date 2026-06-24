# SLD.mode

## 含义
MD的常用设置。用于设置动力学模拟的模式，1表示仅考虑原子位移自由度的传统分子动力学模拟，2表示仅考虑自旋方向自由度的原子自旋动力学模拟，3表示同时考虑两类自由度的自旋晶格动力学模拟，目前MD模拟部分尚不支持模拟除位移自由度和自旋自由度以外的其他自由度。

## 默认值
3

## 取值
1/2/3

## 何时使用
- 当使用 `3.1.6 附属文件MD.input：分子动力学模拟相关设置` 相关功能并需要设置 `SLD.mode` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 默认值是 `3`，即同时考虑位移和自旋自由度。对纯结构型 effective-H / 铁电 local-mode MD，如果目标是只演化 lattice / displacement degrees of freedom，应显式写 `SLD.mode 1`；不要依赖默认值。
- 如果用户目标是 spin-only ASD / LLG，则 `SLD.mode 2` 才匹配；如果目标是 coupled spin-lattice dynamics，才使用 `SLD.mode 3`。
- 对任意 L5 MD 输入，`SLD.mode` 必须与用户确认的 active degrees of freedom 一致，并在 preflight 中检查；不能只看历史 example 或材料名套用。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.6 附属文件MD.input：分子动力学模拟相关设置
- 锚点：`#md-input`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#md-input>
