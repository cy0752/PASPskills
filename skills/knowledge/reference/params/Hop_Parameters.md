# block Hop_Parameters

## 含义
输入自定义TB的hopping参数信息，若 Hop_Parameters_specified_using_site 为T（案例1），第一行依次输入发生跃迁的两个原子编号，两原子间的位矢差的x y z分量；另起一行输入跃迁矩阵，两原子中第一个原子的轨道数作为行数，第二个原子的轨道数作为列数（注意这里的轨道数应当与block Orbitals中指定的各元素轨道数一致）。若 Hop_Parameters_specified_using_dis 为T（案例2），第一行依次输入发生跃迁的元素在 cell.str 中对应编号，以及元素间成键长度(略微大于键长也可)，另起一行输入两元素间跃迁矩阵，行数为前面元素轨道数，列数为后面元素轨道数（注意这里的轨道数也应当与block Orbitals中指定的各元素轨道数一致）。另注意， TB.complex_hop 为T时，这里每个跃迁参数以(r,i)形式表示，其中r为实部数值，i为虚部数值。当使用S-K TB时缺省此项。

## 默认值
无默认值，使用自定义TB时不可缺省

## 取值
见描述

## 何时使用
- 当使用 `3.1.9 紧束缚模型方法常用设置项` 相关功能并需要设置 `block Hop_Parameters` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.9 紧束缚模型方法常用设置项
- 锚点：`#id18`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id18>
