# local_mode.general_model

## 含义
用于设置“Model Invariant”中分析不等价相互作用时是否采用通用方法。常选T。本手册仅涉及选T的情形；选F时仅适用于钙钛矿（perovskite）情形，现已不常用。

## 默认值
F

## 取值
T/F

## 何时使用
- 当使用 `3.1.7.9 Model Invariant 的其他设置` 相关功能并需要设置 `local_mode.general_model` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.7.9 Model Invariant 的其他设置
- 锚点：`#model-invariant`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#model-invariant>
