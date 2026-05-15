# block Slater_Koster_Hop_Parameters

## 含义
输入SK TB的hopping参数信息，若 Hop_Parameters_specified_using_site 为T（案例1），第一行依次输入发生跃迁的两个原子编号，两原子间的位矢差的x y z分量；第二行输入跃迁壳层组合数，数值等于 Different_hop_path 项；第三行依次输入第一个原子跃迁壳层的主量子数、角量子数，第二个原子跃迁壳层的主量子数、角量子数；第四行输入相应的S-K TB跃迁积分项（p轨道与p轨道间为 \(V_{ppσ} V_{ppπ}\) , p轨道与d轨道间为 \(V_{pdσ} V_{pdπ}\) ，p轨道与f轨道间为 \(V_{pfσ} V_{pfπ}\) ）等数值，根据结构对称性，表示跃迁的不同矩阵元是这些数值的不同线性组合形式，这一组合过程将由程序完成。若 Hop_Parameters_specified_using_dis 为T（案例2），则第一行依次输入原子种类序数，原子间距离；其余行不变。

## 默认值
无默认值，使用SK TB时不可缺省

## 取值
见描述

## 何时使用
- 当使用 `3.1.9 紧束缚模型方法常用设置项` 相关功能并需要设置 `block Slater_Koster_Hop_Parameters` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.9 紧束缚模型方法常用设置项
- 锚点：`#id18`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id18>
