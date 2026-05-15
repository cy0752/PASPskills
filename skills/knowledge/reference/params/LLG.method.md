# LLG.method

## 含义
MD的常用设置。用于选择积分LLG方程（参见2.2.4节）时采用的数值算法，1表示4th-order Runge-Kutta method，2表示Mentink’s SIB method，3表示McLachlan’s SMP method。其中，方法1尚不支持NVT模拟，方法3原则上保证积分过程能量守恒，尚不支持并行计算，因而目前最常用的是方法2。

## 默认值
1

## 取值
1/2/3

## 何时使用
- 当使用 `3.1.6 附属文件MD.input：分子动力学模拟相关设置` 相关功能并需要设置 `LLG.method` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.6 附属文件MD.input：分子动力学模拟相关设置
- 锚点：`#md-input`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#md-input>
