# block GA.lat_fix_2D_Ang

## 含义
用于设置固定的面内晶格常数。

## 默认值
缺省时将自动设置该变量为 “ block LatticeVectors ”（参见3.1.3.4节）中给出的前两行数据。

## 取值
6个非负实数

## 何时使用
- 当使用 `3.1.8 全局结构搜索常用设置项` 相关功能并需要设置 `block GA.lat_fix_2D_Ang` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.8 全局结构搜索常用设置项
- 锚点：`#id17`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id17>
