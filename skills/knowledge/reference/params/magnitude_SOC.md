# block magnitude_SOC

## 含义
给每个开启SOC的原子设定SOC强度，数值可借由公式 \(\left(g_s-1\right) \frac{1}{2} \frac{1}{4 \pi \varepsilon_0} \frac{Z e^2}{r^3} \frac{1}{m_e^2 c^2}\) 进行估算。

## 默认值
无

## 取值
见描述

## 何时使用
- 当使用 `3.1.9 紧束缚模型方法常用设置项` 相关功能并需要设置 `block magnitude_SOC` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.9 紧束缚模型方法常用设置项
- 锚点：`#id18`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id18>
