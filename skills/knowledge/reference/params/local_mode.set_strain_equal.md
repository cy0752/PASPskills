# block local_mode.set_strain_equal

## 含义
在使用“Model atomic_effective_H”的MC或CG功能时，或者“Model Invariant”的随机生成构型功能时，可能用到该设置。这里可以设置某些应变模式的取值保持相等。用 \(\eta_{i}(i=1,2, \ldots, 6)\) 表示6种局域模式，则该block的六个数据（T或F）依次表示是否保持 \(\eta_{1}=\eta_{2}, \eta_{1}=\eta_{3}, \eta_{2}=\eta_{3}, \eta_{4}=\eta_{5}, \eta_{4}=\eta_{6}\text{和}\eta_{5}=\eta_{6}\) 。例如案例的设置会自动保持 \(\eta_{2}=\eta_{3}\text {和}\eta_{4}=\eta_{5}=\eta_{6}\) 。注意如果需要保持相等的若干模式所受的力不同，或受到的约束条件不一致（例如硬边界不一致），总是以编号小的模式的受力和取值为准。

## 默认值
F

## 取值
T/F

## 何时使用
- 当使用 `3.1.5.6 MC和CG中添加约束条件` 相关功能并需要设置 `block local_mode.set_strain_equal` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.5.6 MC和CG中添加约束条件
- 锚点：`#mccg`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#mccg>
