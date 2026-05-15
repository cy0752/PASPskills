# block ExternalMagneticField

## 含义
该设置项在蒙特卡洛模拟（以及CG局域优化）中可能用到，用于添加外磁场，单位T。由于在蒙特卡洛模拟阶段才用到，所以该设置也常放在 MC.input 中（通过在 PASP.input 中“ %include MC.input ”使其生效）。该设置项可以在蒙特卡洛模拟（以及可能用到的共轭梯度下降优化）中添加外磁场，单位为T。例如在z方向提供0.1 T外磁场时，可以如案例1所示设置。

## 默认值
缺省时全部赋值为0。

## 取值
实数。

## 何时使用
- 当使用 `3.1.2.5 自旋大小与外磁场设置` 相关功能并需要设置 `block ExternalMagneticField` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.2.5 自旋大小与外磁场设置
- 锚点：`#id5`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id5>
