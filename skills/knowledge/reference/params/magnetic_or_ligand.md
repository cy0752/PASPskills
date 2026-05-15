# block magnetic_or_ligand

## 含义
在“Model find_J_path_sym”中用到。这里需指出各元素原子是磁性原子还是配位原子。1表示磁性原子，2表示配位原子，其他原子用0表示。以 \(BiFeO_{3}\) 为例，由于Fe是磁性原子取1，O是配位原子取2，Bi是其他原子取0，按Bi、Fe、O的顺序（顺序与block Z_values的内容一致）应分别取0、1、2。

## 默认值
0

## 取值
0/1/2

## 何时使用
- 当使用 `3.1.7.8 Model find_J_path_sym 的其他设置` 相关功能并需要设置 `block magnetic_or_ligand` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.7.8 Model find_J_path_sym 的其他设置
- 锚点：`#model-find-j-path-sym`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#model-find-j-path-sym>
