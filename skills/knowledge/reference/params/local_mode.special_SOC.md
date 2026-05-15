# block local_mode.special_SOC

## 含义
在有效哈密顿量方法模块中，处理磁性体系时可能用到该设置。用于更具体地指定哪些相互作用考虑SOC，哪些不考虑。第一行数据用于指定后面读取多少行信息。后面每行信息有三个数据，分别是几体、相应“几体”的第几种原子对（或原子簇）、该原子对（或原子簇）考虑SOC的相互作用最多保留到几阶（非SOC形式仍可以考虑到更高阶，这由3.1.7.3节各项设置决定）。比如案例中，实际上枚举了截断体数和截断距离内的所有的原子对和原子簇情形。并设置成仅单体项考虑SOC，保留到四阶；其余相互作用项均不考虑SOC。如果希望将最近邻的两体相互作用项保留二阶的SOC相互作用，则将“2 1 0”改成“2 1 2”即可。

## 默认值
由“Invariant.SOC”决定

## 取值
非负整数

## 何时使用
- 当使用 `3.1.7.4 SOC相关设置` 相关功能并需要设置 `block local_mode.special_SOC` 时。

## 注意事项
- 这是 block 类型设置，写入时必须使用 `%block ... %endblock` 结构，并保持 block 内格式完整。
- 第一行只表示后面实际要读取的显式设置行数，不要求覆盖当前截断范围内枚举出的所有相互作用类型。
- 第二列不是元素编号、species id、磁性元素序号或 `Z_values` 顺序号，而是 PASP 在当前几体下枚举出的 interaction type / 原子对 / 原子簇编号。不能因为体系只有 2 个磁性元素，就判定 `1 3 2`、`1 4 2`、`1 5 2` 等行多余，或把这些编号解释成非磁性元素。
- 当第一列为 `1` 时，第二列仍然是 PASP 在一体相互作用中的 interaction type 编号，不是元素编号，也不是 `local_mode.mode_definition` 的代表点位编号。若用户或已验证案例说“保留前 5 个单体二阶项”，通常可直接写 `1 1 2` 到 `1 5 2`；不要再追问它是“Gd/Mn 两个元素”还是“5 个代表点位”。只有当用户没有明确“前 N 个”或没有给出一体 interaction type 范围时，才需要追问或 blocked。
- 在 L3 shared-basis / interaction-basis 场景，是否保留 SOC、保留哪些几体、每个几体 / interaction type 保留到几阶、以及保留全部类型还是特定类型，属于用户建模策略确认项。不要用结构分析、pymatgen 脚本或 agent 物理直觉替用户决定；这些分析只能在策略已确认后辅助映射 PASP 编号。
- 若用户要求“只保留某几种相互作用的 SOC”，通常写这些要保留的相互作用行即可；例如只保留 5 个单体二阶 SOC 时，第一行应写 `5`，后面写 `1 1 2` 到 `1 5 2` 这 5 行。
- 第三列为 `0` 可用于显式关闭某个已列出的相互作用类型的 SOC，但不要为了“其余都不要”自动把所有未保留的类型补成 `0` 行，除非用户或已有案例明确要求这种完整枚举写法。
- 如果不确定“第几种原子对/原子簇”的编号，应优先从已有同基底 `SOC=T` 输出中的 `all_interaction_type_Spin_xyzform.dat`、`local_mode_PM.dat`、用户给定清单或已验证案例中获得类型清单，再补写要显式设置的行。
- 不要为了枚举 `local_mode.special_SOC` 编号而把 `Invariant.SOC T` 改成 `Invariant.SOC F` 做 preliminary run；`SOC=F` 生成的相互作用基底不能作为后续 `SOC=T` 共享基底的替代依据。若当前是 L3 shared-basis / interaction-basis 首跑且需要 SOC，必须在首跑前使用用户给定编号、已有 `SOC=T` 同基底输出、已验证案例或其他可核查来源确认要保留的编号；否则应 blocked，而不是先跑 `SOC=F`。
- 当用户已经明确要求考虑 SOC / DMI / 各向异性策略时，不能因为暂时不知道要保留的类型编号就静默省略该 block 并宣称 preflight 通过；应标记为 blocked。在 `Invariant.SOC T` 的 L3 共享基底首跑场景下，不允许用“先探测运行、后回填 `local_mode.special_SOC`”替代首跑前的显式设置。
- 对 `Model Invariant` / L3 共享基底，若 `Invariant.SOC T`，第一次生成相互作用基底的运行就必须包含 `local_mode.special_SOC` block。不要先在 `Invariant.SOC T` 但缺少 `local_mode.special_SOC` 的情况下运行，再试图在后续 method-6、拟合、MC 或 MD 阶段补加；这会造成共享基底和下游数据链的 SOC 定义不一致。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.7.4 SOC相关设置
- 锚点：`#soc`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#soc>
