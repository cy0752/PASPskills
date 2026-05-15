# block qpoints.magnon

## 含义
PASP每次计算布里渊区1条线段上的自旋波色散，本设置项第一行代表这条线段的起始q点（q用以倒格矢展开的系数 \(q_i\) 表示： \(\boldsymbol{q}=\sum_i q_i \boldsymbol{b}_i\) ），第二行代表这条线段的终末q点。

## 默认值
需要用到时不可缺省

## 取值
坐标分量为实数

## 何时使用
- 当使用 `3.1.11 线性自旋波色散计算常用设置项` 相关功能并需要设置 `block qpoints.magnon` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 默认 `spinw` legacy 路径在源码中读取两行端点并线性插值；写入时不要只给一行。
- 对线段计算，`number_of_qpoints` 应至少为 2，否则两端点合同不成立。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.11 线性自旋波色散计算常用设置项
- 锚点：`#id20`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id20>
