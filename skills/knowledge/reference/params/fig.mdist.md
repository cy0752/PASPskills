# block fig.mdist

## 含义
在有效哈密顿量方法模块中常用，在“Model find_J_path_sym”（找不等价作用对）中也会用到。在这里设定相互作用的截断距离，注意单位是Bohr。第一位填1，第二位填两体相互作用的截断距离，第三位填三体相互作用的截断距离（其中任意两个原子的距离都不超过截断距离），以此类推。例如，只考虑到两体相互作用，截断距离为15 Bohr时，只需要填两个数据，如案例所示。

## 默认值
不可缺省！（缺省时报错“read_fig_data: no fig.mdist block”）

## 取值
第一位取1，之后各位为正实数

## 何时使用
- 当使用 `3.1.7.2 截断距离 (block fig.mdist)` 相关功能并需要设置 `block fig.mdist` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.7.2 截断距离 (block fig.mdist)
- 锚点：`#block-fig-mdist`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#block-fig-mdist>
