# block local_mode.lamp_strain

## 含义
在使用“Model atomic_effective_H”的MC或CG功能时，可能用到该设置。这里可以设置在MC或CG过程中，各个应变模式的“软边界”（参见3.1.7.5节类型二“lamp”的相关内容，在那里可以设置各个局域声子模式的“软边界”）。这里软边界形式总是采用3.1.7.5节类型二中提到的形式二，即 \(A+Bu+\text{coef}*e^{\text{scale}*\left(u/u_{c}-1\right)}\) 。其中， \(u\) 表示应变的幅度； \(u_{c}\) 为截断幅度，当 \(u>0\) 时取 \(u_{c2}\) ，当 \(u<0\) 时取 \(u_{c1}\) ； \(scale\) （大于0）为输入文件中用“ local_mode.non_polynomial.exp.scale ”设置的值（缺省值为6.0）； \(coef\) （大于0）是输入文件中用“ local_mode.non_polynomial.exp.coefficient ”设置的值（缺省值为1.0）；根据边界 \(u=u_{c1}<0\) 和 \(u=u_{c2}>0\) 处能量（考虑应变的单体能量贡献即可）及其导数连续的条件可以分别在两个边界处解出各自的 \(A\) 和 \(B\) ， \(u>0\) 时采用 \(u=u_{c2}\) 处解出的 \(A\) 和 \(B\) ，而 \(u<0\) 时采用 \(u=u_{c1}\) 处解出的 \(A\) 和 \(B\) 。共需...

## 默认值
不限制取值范围，左边界缺省时取右边界的相反数

## 取值
右边界为正实数，左边界为负实数

## 何时使用
- 当使用 `3.1.5.6 MC和CG中添加约束条件` 相关功能并需要设置 `block local_mode.lamp_strain` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.5.6 MC和CG中添加约束条件
- 锚点：`#mccg`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#mccg>
