# `Model find_J_path_sym` Run Notes

> Historical observations from real `find_J_path_sym` runs.
>
> **重要**：本文件是**历史观察记录**。它不是当前用户工作区的事实。当前任务的判断必须以用户实际目录中的文件为准；只有在用户的当前结构 / 体系 / 设置与本文件中某条记录的前提匹配时，才把那条记录作为参考。

---

## 文件作用

记录在 `Model find_J_path_sym` 上跑过的真实例子，包括：

- 不同 supercell 大小对近邻收敛的影响
- 不同体系的 PASP 输出文件名是否符合 source-code 描述
- 实际跑过哪些 NiI₂、CrI₃ 等已知材料、得到的近邻距离与文献的对比
- 真实跑过的资源占用（核数、时长、内存）
- 任何与 `workflows/l2_find_J_path_sym.md` 主文档描述不一致的现象，以及当时的处理方式

主 workflow 文档保持稳定契约，不应该混入这些示例特有数值。

---

## 运行记录格式

每次实跑追加一节，模板：

```markdown
### YYYY-MM-DD：<体系名 / 例子名>

**目录**：`<相对路径，例如 workflow/l2-X/find_J_path_sym/runs/...>`

**起始结构**：
- 来源：用户自带 POSCAR / pasp_examples / 文献结构
- primitive cell 是否需要 reduction：是 / 否
- 是否有轴向修正：是 / 否

**关键设置**：
- `cell.str`：<元素 + 超胞规模>
- `Z_values`：<...>
- `isaAB`：<...>
- `Spin_values`：<...>
- `fig.maxk`：<...>
- `fig.mdist`：<...>

**收敛性试验**：
- 跑过的 supercell：<列表>
- 在哪个 supercell 下结果稳定：<...>

**输出验证**：
- 不等价 pair 数：<...>
- 前 N 近邻距离：<...>
- 与文献对照：<...>

**遇到的问题与解决**：
- <...>

**资源消耗**：
- 核数 / 时长 / 内存（如可记）

**与主文档不一致的地方**（如有）：
- <...>
```

---

## 当前已记录的运行

### 2026-05-10：NiI2 5x5 lecture example

**目录**：`/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/paspskills/workflow/l2/find_J_path_sym/runs/20260510-052512-NiI2-5x5`

**关键设置**：
- `Model find_J_path_sym`
- NiI2 lecture example structural inputs
- `cell.str_NiI2_5x5` and `cell.str_NiI2_6x6` were present in the run directory for comparison / provenance

**输出验证**：
- `log.out` ended with `PASP is finished gracefully.`
- Generated `J.POS`
- Generated `pair_POS.001` through `pair_POS.007`
- Generated `atat.001_1` through `atat.007_4`
- The observed filename pattern matches the main workflow contract: `pair_POS.NNN` and `atat.NNN_Y`.

**遇到的问题与解决**：
- No runtime crash observed in this run.

---

## 跨运行的稳定性观察

> 在累积若干次运行之后，把可重复出现的规律提炼到这里。例如：
>
> - 哪些 supercell 大小阈值对哪类材料体系够大
> - PASP 不同版本之间 `pair_POS.NNN` / `atat.NNN_Y` 文件名约定的差异
> - `fig.mdist` 实际能可靠覆盖到多远（与 supercell 尺寸的关系）
>
> 提炼出的稳定结论应当回写到主文档 `l2_find_J_path_sym.md`，本文件只保留这些结论的"运行证据"。

- 2026-05-10 NiI2 5x5 run confirms the stable output filename pattern `J.POS`, `pair_POS.NNN`, and `atat.NNN_Y`.
- A 2026-05 user report on PASP Compile Sat Sep 28 19:47:07 CST 2024 confirmed that `find_J_path_sym` stops with `find_J_path_sym: species are not ordered!` when a generated supercell-style `cell.str` interleaves species by unit-cell copy order (`Ni I I Ni I I ...`). Regrouping `%block AtomicCoordinatesAndAtomicSpecies` by species id allowed PASP to run normally. The stable contract has been curated into the main workflow and `cell.str` reference guidance.

---

## 与主文档的关系

| 问题类型 | 应当查 |
|---|---|
| `find_J_path_sym` 的稳定流程契约 | `workflows/l2_find_J_path_sym.md` |
| 字段定义 / 默认值 / 单位 | `knowledge/reference/` 对应卡 |
| 历史上 NiI₂ 5×5 vs 6×6 第 5 近邻表现 | 本文件 |
| 当前用户工作区中 PASP 跑出来什么 | 用户实际目录中的文件 |

如果当前用户的体系 / 设置 / supercell 与本文件中某条记录不匹配，**不要**把那条记录的具体数值当作"用户应当看到"的结果。
