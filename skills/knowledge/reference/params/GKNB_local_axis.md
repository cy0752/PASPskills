# block GKNB_local_axis

## 含义
设定新的局域坐标系（通常为单位矩阵）。当与设定 \(\vec{P}_{12}^{\alpha \beta}\) 、 \(\vec{P}_{i}^{\alpha \beta}\) 时采用的局域坐标系不一致时，将采用这里设定的坐标系，并对 \(\vec{P}_{12}^{\alpha \beta}\) 、 \(\vec{P}_{i}^{\alpha \beta}\) 作适当变换（分量变换到新坐标系下的形式）。

## 默认值
单位矩阵

## 取值
正交矩阵

## 何时使用
- 当使用 `3.1.10 自旋序诱导铁电性统一极化模型常用设置项` 相关功能并需要设置 `block GKNB_local_axis` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.10 自旋序诱导铁电性统一极化模型常用设置项
- 锚点：`#id19`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id19>
