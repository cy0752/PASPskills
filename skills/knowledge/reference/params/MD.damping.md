# MD.damping

## 含义
MD的常用设置。用于设置Newton方程（参见2.2.4节）的阻尼系数。该值非零时，程序将基于设定的“ MD.temperature ”参数做NVT模拟，当该值为零时，程序将执行NVE模拟。目前，PASP软件尚不支持除NVT和NVE之外的其他系综模拟。

## 默认值
0.0

## 取值
非负实数

## 何时使用
- 当使用 `3.1.6 附属文件MD.input：分子动力学模拟相关设置` 相关功能并需要设置 `MD.damping` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.6 附属文件MD.input：分子动力学模拟相关设置
- 锚点：`#md-input`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#md-input>
