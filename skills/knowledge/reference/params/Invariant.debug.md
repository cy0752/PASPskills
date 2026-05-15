# Invariant.debug

## 含义
用于设置“ Model Invariant ”中是否采用debug模式，debug模式下会在标准输出中提供更多相关数据信息。默认建议保持为F，避免产生过多输出；只有在排查具体运行问题、需要额外诊断信息时再临时设为T。

## 默认值
F

## 取值
T/F

## 何时使用
- 当使用 `3.1.7.9 Model Invariant 的其他设置` 相关功能并需要设置 `Invariant.debug` 时。

## 注意事项
- 生成新 invariant 输入或从模板派生输入时，默认不要开启 debug 模式。
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.7.9 Model Invariant 的其他设置
- 锚点：`#model-invariant`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#model-invariant>
