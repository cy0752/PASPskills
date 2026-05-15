# pasp_reference 目录结构说明

本文档说明 `pasp_reference/` 目录的组织方式、每个子目录的用途，以及这些文件将来如何服务于 PASP skill 查询。

---

## 1. 总体目标

`pasp_reference/` 是 PASP 文档的**本地知识库**，不是网页镜像。

它的目标是把官网文档按更适合查询和 skill 调用的方式重新组织，使后续的 Claude / Codex / 自定义 skill 可以更稳定地回答以下两类问题：

1. **专题型问题**
   - `PASP.input` 怎么写？
   - `MC.input` 里面常用哪些项？
   - `cell.str` 和 `unit_cell.str` 的区别是什么？

2. **细粒度问题**
   - `Model` 是什么意思？
   - `fig.maxk` 是做什么的？
   - `READ_POSCAR` 应该怎么用？

因此，这个目录不是按“网页一页一个文件”来组织，而是按**知识对象**来组织。

---

## 2. 当前目录结构

```text
pasp_reference/
├── toc/
├── topics/
├── params/
├── files/
└── modules/
```

每个子目录分别承担不同层级的知识组织任务。

---

## 3. `toc/`：目录骨架与来源信息

```text
toc/
├── site.md
├── chapter2.md
├── chapter3.md
└── extraction_plan.md
```

### 3.1 这个目录是干什么的
`toc/` 用来保存**官网原始文档结构**，相当于知识库的“地图”。

它不负责回答具体参数含义，而是负责说明：
- 官网有哪些章节
- 各章节的编号是什么
- 各章节的锚点是什么
- 后续抽取时是按什么原则拆分的

### 3.2 里面的文件分别干什么

#### `site.md`
保存 PASP 官网站点级章节入口和本地 coverage 边界。

作用：
- 判断哪些官网章节已经进入本地 reference
- 说明为什么第 1/4/5/6 章暂不纳入通用 skill 知识库
- 避免后续把“第 3 章全量参数覆盖”误认为“全站所有章节全量镜像”

#### `chapter2.md`
保存 PASP 官网第 2 章“功能介绍”的目录树。

作用：
- 定位方法、模型和 workflow 关系
- 给 `topics/methods_overview.md` 提供来源锚点

#### `chapter3.md`
保存 PASP 官网第 3 章的目录树。

作用：
- 快速查看官网有哪些章节
- 给后续知识库文件提供章节编号和锚点映射
- 方便将本地文档回链到官网原文位置

#### `extraction_plan.md`
保存 reference 的抽取策略和拆分原则。

作用：
- 记录为什么知识库要拆成 topics / files / params / modules
- 说明抽取优先级
- 便于后续继续扩展时保持风格一致

### 3.3 什么时候会查这个目录
通常不是最终用户直接查，而是：
- 你维护知识库时查
- 以后做自动化抽取脚本时查
- 需要从本地文档回到官网原文时查

---

## 4. `topics/`：专题文档

```text
topics/
├── PASP.input.md
├── MC.input.md
├── MD.input.md
├── methods_overview.md
├── symmetry_representative_sites.md
└── structure_from_poscar.md
```

### 4.1 这个目录是干什么的
`topics/` 里放的是**一整类输入文件或主题的说明文档**。

这些文件通常比参数卡片更长，能保留上下文，适合回答：
- 一个输入文件整体是做什么的
- 常见设置有哪些
- 这一类内容内部的几个字段之间有什么关系

### 4.2 为什么叫 topics
因为这里的粒度不是“单个参数”，也不是“官网章节镜像”，而是一个相对完整的主题。

例如：
- `PASP.input.md` 不是只解释一个参数，而是解释核心输入文件整体
- `MC.input.md` 是一整套 MC / PTMC / CG 相关设置
- `MD.input.md` 是一整套 MD 相关设置
- `methods_overview.md` 对应官网第 2 章，用来说明 PASP 方法族、`Model` 入口和 workflow 关系
- `symmetry_representative_sites.md` 说明如何从结构对称性分析得到自旋代表位点，并生成 `local_mode.mode_definition` 的 spin mode
- `structure_from_poscar.md` 说明只有 VASP `POSCAR` 时如何判断原胞/超胞关系、生成 primitive POSCAR / `POSCAR_UC`，并衔接 `cell.str` / `unit_cell.str`

### 4.3 适合回答什么问题
例如：
- `PASP.input 大概怎么组织？`
- `MC.input 有哪些常用设置？`
- `MD.input 和 MC.input 的区别是什么？`
- `PASP 的几个 Model 分别对应什么 workflow？`
- `怎么从 POSCAR_UC 找 Gd/Mn 的对称不等价代表位点？`
- `只有 POSCAR 时怎么得到 primitive POSCAR 或 unit_cell.str？`

### 4.4 为什么不把这些放进 `files/`
因为像 `PASP.input`、`MC.input`、`MD.input` 一方面确实是文件，另一方面它们更像**一整个配置主题**。

它们里面包含大量字段、规则和结构化逻辑，和 `seed.in` 这种小文件不太一样。为了让查询更自然，单独放到 `topics/` 更合适。

---

## 5. `params/`：参数卡片

```text
params/
├── INDEX.md
└── Model.md
```

### 5.1 这个目录是干什么的
`params/` 用来放**单个参数的标准化说明卡片**。

每一张卡片只聚焦一个参数，例如：
- `Model`
- `SuperCell`
- `Z_values`
- `isaAB`
- `fig.maxk`
- `local_mode.mode_definition`

### 5.2 参数卡片的作用
参数卡片是为了支持更精确的查询。

它特别适合回答：
- `Model 是什么意思？`
- `SuperCell 怎么写？`
- `fig.maxk 默认值是什么？`
- `某个参数和哪些文件有关？`

相比 `topics/` 里的长文档，参数卡片的优点是：
- 更短
- 更标准化
- 更适合精确检索
- 更适合以后转成结构化数据

`INDEX.md` 是参数卡片总索引，用于在不知道具体文件名时先定位条目。

### 5.3 为什么不能只有 topics
因为如果以后用户经常问的是某个单独字段，模型从一篇长文档中抽会不如直接命中参数卡片稳定。

所以最佳实践通常是：
- `topics/` 保留上下文
- `params/` 提供精确词条

### 5.4 什么时候继续扩展这个目录
当你发现用户常问单独字段时，就应该优先补这类卡片。

当前第 3 章官网参数已批量补齐为 `params/*.md` 卡片；后续维护重点不是继续手动猜缺口，而是更新 `params/INDEX.md` 与覆盖审计，确保新增官网字段不会漏掉。

---

## 6. `files/`：独立输入输出文件说明

```text
files/
├── cell.str.md
├── unit_cell.str.md
├── seed.in.md
├── spin_exchange.dat.md
├── distortion.pos.md
├── distortion.MAGMOM.md
├── local_mode_PM.dat.md
├── J_best.dat.md
├── Fitting_Settings.txt.md
├── Fitting_Set_Lambda.txt.md
├── Fitting_Set_Term_Keep.txt.md
├── Fitting_Set_Term_Skip.txt.md
├── spin3.in.md
├── amp_local_mode.in.md
├── Zeff.dat.md
├── elastic.dat.md
├── spin_strain.dat.md
├── DM_derivative.dat.md
└── PASP.used_info.md
```

### 6.1 这个目录是干什么的
`files/` 用来放**独立输入文件或输出文件的说明**。

它和 `topics/` 的区别在于：
- `topics/` 更强调一个大主题或一个核心配置入口
- `files/` 更强调某个具体文件本身的格式、用途和使用时机

### 6.2 这些文件通常回答什么问题
例如：
- `cell.str 是干什么的？`
- `unit_cell.str 和 POSCAR_UC 的关系是什么？`
- `spin_exchange.dat` 格式怎么理解？`
- `PASP.used_info` 有什么用？`

### 6.3 为什么这些文件适合单独放
因为这些文件很多都有自己独立的：
- 文件名
- 输入格式
- 使用时机
- 依赖关系
- 常见错误

如果混在 `PASP.input.md` 里，会让专题文档太长，也不利于 skill 精准命中。

### 6.4 这类文件的推荐结构
目前多数文件采用：
- 文件作用
- 何时需要
- 关键字段或内容
- 注意事项
- 最小示例（如有）
- 来源章节

这种结构的好处是：
- 人看起来清晰
- 模型检索时也容易提取重点

---

## 7. `modules/`：功能模块说明

```text
modules/
├── effective_hamiltonian.md
├── ga.md
├── tb.md
├── knb.md
└── magnon.md
```

### 7.1 这个目录是干什么的
`modules/` 用来解释 PASP 的**功能模块或方法族**。

这些内容通常介于“workflow”和“参数手册”之间：
- 比单个参数更大
- 比完整 workflow 更聚焦在某一类模型/方法

### 7.2 适合回答什么问题
例如：
- `TB 模块一般要配哪些设置？`
- `effective Hamiltonian 相关的常用字段有哪些？`
- `magnon 计算重点看哪些输入项？`
- `KNB 相关设置通常会涉及哪些块？`

### 7.3 为什么这些内容不放在 topics 或 params
因为这些内容既不是单一文件，也不是单一参数。

它们更像：
- 某个方法家族的常用配置总览
- 某个功能模式的参数分布说明

所以单独放到 `modules/` 可以让 skill 回答“模块层面”的问题时更自然。

### 7.4 它和 workflow 的区别
要注意：`modules/` 不是 workflow。

- `modules/` 关注的是：某个功能模块有哪些常见设置
- `workflow/` 关注的是：为了完成一个任务，要按什么阶段走

例如：
- `tb.md` 讲的是 TB 模块有哪些设置
- 将来如果有 `workflow/tight_binding.md`，那会讲“做一个 TB 任务的完整流程”

---

## 8. 这些目录将来怎么配合使用

可以把整个 `pasp_reference/` 理解成一个分层知识库：

```text
官网目录层
└── toc/

专题说明层
├── topics/
├── files/
└── modules/

参数精查层
└── params/
```

它们的配合关系大致是：

### 8.1 用户问“整体怎么做”
优先查：
- `topics/`
- 未来的 workflow 文档

### 8.2 用户问“某个文件是什么”
优先查：
- `files/`

### 8.3 用户问“某个字段是什么意思”
优先查：
- `params/`

### 8.4 用户问“某个模块通常怎么配”
优先查：
- `modules/`

### 8.5 用户想核对官网出处
查：
- 文档底部的 `来源章节`
- `toc/chapter3.md`

---

## 9. 关于“锚点”和“来源页面”

很多文件底部会写：

```md
## 来源章节
- 3.1.2.1 `Model`
- 锚点：`#model`
- 来源页面：<https://...html#model>
```

这些信息属于**来源元数据**，不是正文内容本身。

### 9.1 它们的作用
- `来源章节`：告诉你整理自官网哪一节
- `锚点`：告诉你网页里该节的定位 id
- `来源页面`：给出能直接跳回官网对应小节的链接

### 9.2 它们不是主要检索内容
真正用于语义检索的，通常还是：
- 文件名
- 标题
- 正文内容

锚点和来源链接更多是为了：
- 回溯原文
- 做引用
- 以后脚本自动处理时做定位

---

## 10. 后续还可以怎么扩展

未来如果这个知识库继续扩展，比较自然的方向有：

### 10.1 增加更多参数卡片
例如：
- `SuperCell.md`
- `Z_values.md`
- `isaAB.md`
- `Spin_values.md`
- `fig.maxk.md`

### 10.2 增加 workflow 层
例如新增：

```text
workflows/
├── exchange_fitting.md
├── monte_carlo.md
├── molecular_dynamics.md
├── magnon.md
└── tight_binding.md
```

这样就能从“reference 查询”进一步升级到“任务导向指导”。

### 10.3 增加总索引文件
例如增加：
- `INDEX.md`
- `files_index.md`
- `params_index.md`

方便 skill 先查总目录，再跳到具体文件。

---

## 11. 一句话总结

`pasp_reference/` 的核心设计思路是：

- `toc/` 保存官网结构
- `topics/` 讲大主题
- `params/` 讲单个参数
- `files/` 讲独立输入输出文件
- `modules/` 讲功能模块

也就是说，它不是“官网镜像”，而是一个更适合 PASP skill 使用的本地 reference 知识库。
