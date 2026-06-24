# local_mode.mode_range

## 含义
在“local_mode.cal_para_method”取1时，用于设置随机构型的取值范围，以及产生有序构型的相关设置信息。共需“局域模式数+6”行：其中局域模式数应与测试运行时名为 local_mode-*.xsf （ * 处为编号）的输出文件的个数一致，而这个个数未必与“block local_mode.mode_definition”部分定义的局域模式数一致（因为PASP软件可能会根据对称性分析补充对称等价的局域模式）；“+6”部分对应应变的六个自由度。每行内容可以有两种格式：第一种，“最大值 分段数”（此时最小值取缺省值0）；第二种，“最大值 最小值 分段数”。这两种格式可以混用。对于生成有序构型所需的“最大值”和“分段数”两个数据，直接从这里获取，产生有序构型的规则详见“ local_mode.generate_ordered_str ”设置项介绍。对于随机生成构型的部分，各模式先从各自对应的[最小值,最大值]均匀随机取值；在“ local_mode.randstr_randsign ”为T（缺省值为T）时再随机取正负号，否则不随机取正负号。在案例1中，若“ local_mode.randstr_randsign ”取T，则前三种局域模式会在[0,0.276]均匀随机取值后再随机取正负号，这等价于在[-0.276,0.276]均匀随机取值；反之，若使用“ local_mode.randstr_randsign F ”，则前三种局域模式会在[0,0.276]均匀随机取值...

## 默认值
对于各模式，最小值的缺省值为0（注意不是最大值的相反数）；最大值的缺省值一般为0.04，但应变对应的最大值为0.02；分段数缺省值为4。

## 取值
最大值、最小值为实数，分段数为正整数

## 何时使用
- 当使用 `3.1.7.7 随机生成构型或自定义构型的相关设置` 相关功能并需要设置 `local_mode.mode_range` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 不要把默认最大值 `0.04` 当成铁电/声子局域模式的物理合理默认范围。对 PTO 等集体软模，`mode_range` 控制的是 local-mode amplitude，不是直接的 Angstrom 位移。
- 估算范围时，先用当前同基底运行产生的 `def_local_modes.dat` 或 `local_mode-*.xsf` 确认 reduced local-mode 分量；再用目标物理位移除以对应分量估算 amplitude。例如目标 Ti 位移约为 `u_target`，而 `def_local_modes.dat` 中 Ti reduced displacement component 为 `u_reduced`，则候选 amplitude 量级为 `u_target / u_reduced`。安全裕度、是否取对称正负、以及最终数值必须由用户或物理目标确认。
- 对 `local_mode.cal_para_method = 1` 的随机构型，若 `local_mode.randstr_randsign T`，非负区间再随机取符号；不要因为 block 行里只写了正最大值就误以为样本只取正振幅。
- 设定较大范围后，应通过 smoke test 检查生成结构的最小原子间距和物理合理性；不能只凭 PASP 作业成功判断范围合理。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 相关条目
- `files/def_local_modes.dat.md`
- `params/local_mode.mode_definition.md`
- `params/local_mode.nstr_random.md`
- `params/local_mode.randstr_randsign.md`

## 来源章节
- 3.1.7.7 随机生成构型或自定义构型的相关设置
- 锚点：`#id14`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id14>
