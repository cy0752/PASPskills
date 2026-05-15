# block GKNB.spiral

## 含义
是否对自旋序附加spiral（螺旋）。选T时，利用“block GKNB.qvec”（定义q，采用倒格子基矢下的分数坐标形式）和“block GKNB.spiral_plane_vec”（定义 \(e_1\) 和 \(e_2\) ，采用笛卡尔坐标形式）定义附加的螺旋序。此时位于r（分数坐标形式）、原自旋矢量为S的磁性原子，相位变为 \(\varphi=\operatorname{acos}\left(\frac{S_z}{|S|}\right)+2 \pi \boldsymbol{q} \cdot \boldsymbol{r}\) ，附加螺旋序之后的自旋矢量变为 \(|\boldsymbol{S}|\left(\boldsymbol{e}_1 \cos \varphi+\boldsymbol{e}_2 \sin \varphi\right)\)

## 默认值
F

## 取值
T/F

## 何时使用
- 当使用 `3.1.10 自旋序诱导铁电性统一极化模型常用设置项` 相关功能并需要设置 `block GKNB.spiral` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.10 自旋序诱导铁电性统一极化模型常用设置项
- 锚点：`#id19`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id19>
