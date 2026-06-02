# pasp_reference 查询说明（给 Claude / Codex / skills 用）

本文档说明 `pasp_reference/` 这套本地知识库应当如何被 Claude、Codex 或自定义 skill 查询使用。

它不是给最终用户看的手册，而是给“查询它的 agent”看的使用约定。

---

## 1. 这套 reference 的设计目标

`pasp_reference/` 不是网页镜像，而是为了让模型更稳定地回答问题而重组后的知识库。

它主要服务三类查询：

1. **主题查询**
   - `PASP.input 怎么写？`
   - `MC.input 里一般设置什么？`

2. **文件查询**
   - `cell.str 是做什么的？`
   - `spin_exchange.dat 格式是什么？`

3. **参数查询**
   - `Model 是什么意思？`
   - `isaAB 怎么填？`

因此，查询时不要先按网页章节想，而要先判断：
**用户问的是主题、文件、参数，还是模块。**

---

## 0. 写入前必须查 reference

当 Claude / Codex 或其他 agent 准备生成、修改或覆盖 PASP 输入时，只要涉及具体字段、block、文件格式、编号规则或条件依赖，就必须先查本 reference。

这条规则同时适用于：
- skill 开发：编写 workflow、模板、脚本说明或 routing guardrail 时
- runtime 使用：在用户 workspace 中写 `PASP.input`、`cell.str`、`unit_cell.str`、`MC.input`、`MD.input`、`Fitting_*` 等文件时

workflow 可以先判断当前阶段和可调整项，但不能凭 workflow intuition 直接写精确格式。写入前必须确认：
- 字段名、文件名、block 名是否正确
- 行顺序、列含义、单位、编号起点是否正确
- 文件依赖是 hard-required、条件 required，还是 helper
- 当前 reference 是否真的覆盖这个写法

如果 reference 没有覆盖，不要从模板、历史样例、相似文件或记忆类推；应标记为不确定并询问用户。

---

## 2. 查询优先级

### 2.1 如果用户问“一个大主题怎么配置”
优先查：`topics/`

例如：
- `PASP.input 怎么组织？` → `topics/PASP.input.md`
- `MC.input 常用项有哪些？` → `topics/MC.input.md`
- `MD.input 怎么看？` → `topics/MD.input.md`
- `PASP 有哪些方法 / Model 怎么串起来？` → `topics/methods_overview.md`
- `只有 POSCAR 怎么准备 cell.str / unit_cell.str` → `topics/structure_from_poscar.md`
- `怎么从结构找 local_mode.mode_definition 的自旋代表位点` → `topics/symmetry_representative_sites.md`

### 2.2 如果用户问“某个具体文件是干什么的”
优先查：`files/`

例如：
- `cell.str 是什么` → `files/cell.str.md`
- `unit_cell.str 和 cell.str 区别` → `files/unit_cell.str.md` + `files/cell.str.md`
- `POSCAR_UC 怎么来` → `topics/structure_from_poscar.md` + `files/unit_cell.str.md`
- `J_best.dat 是做什么的` → `files/J_best.dat.md`
- `field.dat 和 P_abs.dat 怎么验证` → `files/field.dat.md` + `files/P_abs.dat.md`
- `mode_def.input 是什么` → `files/mode_def.input.md`；block 语法再查 `params/local_mode.mode_definition.md`
- `mode_mass.input 怎么检查` → `files/mode_mass.input.md`；mass block 语义再查 `params/atom_Heff.MASS_local_mode.md`

### 2.3 如果用户问“某个字段是什么意思”
优先查：`params/`

例如：
- `Model 是什么` → `params/Model.md`
- `MD.E_type 是什么` → `params/MD.E_type.md`
- `local_mode.mode_definition 怎么写` → `params/local_mode.mode_definition.md`
- 不确定卡片文件名时，先查 `params/INDEX.md`

如果 `params/` 里还没有对应卡片，再退回：
- `topics/PASP.input.md`
- 或相关 module / file 文档

### 2.4 如果用户问“某个功能模块通常怎么配置”
优先查：`modules/`

例如：
- `TB 通常要配哪些设置` → `modules/tb.md`
- `magnon 主要看哪些输入项` → `modules/magnon.md`
- `effective Hamiltonian 有哪些关键项` → `modules/effective_hamiltonian.md`

如果用户问的是方法族之间的 workflow 关系，而不是单个模块参数，先查 `topics/methods_overview.md`，再进入具体 module 或 param。

### 2.5 如果用户问“官网原文在哪一节”
优先看文档底部：
- `## 来源章节`
- 锚点
- 来源页面

必要时查：
- `toc/site.md`
- `toc/chapter2.md`
- `toc/chapter3.md`

---

## 3. 推荐查询流程

建议 Claude / Codex / skill 采用下面这个顺序判断。

### Step 1：先识别问题类型
把用户问题归到下面四类之一：
- topic
- file
- param
- module

### Step 2：先查最可能命中的目录
- topic → `topics/`
- file → `files/`
- param → `params/`
- module → `modules/`

### Step 3：如果没命中，再扩大一层
例如：
- `params/` 没有 `SuperCell.md`
- 就去 `topics/PASP.input.md` 里找 `SuperCell`

### Step 4：若需要出处，再读来源元数据
- 章节编号
- 锚点
- 来源页面

### Step 5：回答时优先输出重组后的知识，而不是原网页原文
也就是说：
- 先总结结构化含义
- 需要时再附来源
- 不要默认大量复述官网原句

---

## 4. 各目录在查询时的角色

### 4.1 `topics/`：主题入口
角色：**第一层语义入口**

适合：
- 初学者提问
- 范围较大的问题
- 需要整体上下文的问题

优点：
- 上下文完整
- 便于解释字段之间的关系

缺点：
- 对于单个字段，不如 `params/` 精准

### 4.2 `files/`：文件词典
角色：**文件名驱动的说明层**

适合：
- 用户直接提到文件名
- 用户问某个文件何时需要、格式怎么写

优点：
- 文件命中率高
- 对技能系统非常友好

### 4.3 `params/`：字段精查层
角色：**最高精度的参数词典**

适合：
- 单字段问答
- 参数解释
- 默认值、可选值、依赖项说明
- 快速确认某个官网第 3 章字段是否已经被抽成卡片

优点：
- 最短、最精确
- 适合后续做结构化检索
- `params/INDEX.md` 可作为参数卡片总入口

限制：
- 只有已经补卡片的参数才能直接命中

### 4.4 `modules/`：方法族说明层
角色：**模块级中间层**

适合：
- 用户问某个方法家族
- 不是单文件问题，也不是完整 workflow 问题

优点：
- 适合回答“这一类计算通常看哪些设置”

### 4.5 `toc/`：来源地图层
角色：**不直接回答业务问题，而是做定位和回溯**

适合：
- 需要核对官网章节
- 需要把本地条目回链到原文位置
- 后续自动化脚本建立映射

---

## 5. 什么是“主检索内容”，什么是“元数据”

在每个 reference 文档中，大致可以分成两部分。

### 5.1 主检索内容
这些内容是模型最应该依赖来理解语义的：
- 文件名 / 标题
- `文件作用`
- `何时需要`
- `关键字段或内容`
- `注意事项`
- `最小示例`
- `模块用途`
- `常见相关设置`
- `含义`
- `默认值`
- `可选值`

### 5.2 元数据
这些内容主要用来追溯来源，而不是主语义理解：
- `来源章节`
- `锚点`
- `来源页面`

### 5.3 查询时应如何使用
建议：
- **先看主检索内容**，回答用户问题
- **需要引用出处时再看元数据**

也就是说，锚点不是主要检索语义的入口。
锚点更像网页中的 section id，用于跳转原文。

---

## 6. 推荐的查询策略示例

### 例 1：用户问 `Model 是什么意思？`
推荐顺序：
1. 查 `params/Model.md`
2. 若需要补上下文，再查 `topics/PASP.input.md`
3. 若需要原文出处，再看 `来源章节`

### 例 2：用户问 `cell.str 和 unit_cell.str 有什么区别？`
推荐顺序：
1. 查 `files/cell.str.md`
2. 查 `files/unit_cell.str.md`
3. 做对比总结
4. 必要时回到 `topics/PASP.input.md` 看它们和 `%include` 的关系

### 例 3：用户问 `TB 主要配哪些输入项？`
推荐顺序：
1. 查 `modules/tb.md`
2. 若问题涉及某个具体文件，再进入 `files/` 或 `topics/`

### 例 4：用户问 `MC 和 MD 有什么区别？`
推荐顺序：
1. 查 `topics/MC.input.md`
2. 查 `topics/MD.input.md`
3. 做主题级对比

### 例 5：用户问 `spin_exchange.dat 怎么用？`
推荐顺序：
1. 查 `files/spin_exchange.dat.md`
2. 若还需要模块背景，再查 `modules/knb.md` 或相关模块文档

---

## 7. 对 Claude / Codex 的具体建议

### 7.1 不要一上来读整个目录
先根据用户问题猜测最可能的目录。

坏做法：
- 把所有 md 全读一遍

好做法：
- 先按问题类型定位到 `topics/` / `files/` / `params/` / `modules/`
- 只在需要时扩大范围

### 7.2 回答时优先引用“重组后的总结”
这套 reference 已经做过整理。
因此通常应优先回答：
- 文件的作用
- 参数的含义
- 使用条件
- 注意事项

而不是直接长段粘贴网页原文。

### 7.3 缺参数卡片时要学会退回上层文档
如果用户问：
- `Spin_values` 是什么

但 `params/Spin_values.md` 还没建，应该：
1. 去 `topics/PASP.input.md` 里查
2. 找对应字段
3. 给出回答
4. 如有必要，建议后续补参数卡片

### 7.4 当问题明显是 workflow 时，不要强行只靠 reference 回答
如果用户问：
- `我想从结构出发做交换参数拟合，该怎么走？`

这已经是 workflow 问题，不应只用 `files/` 或 `params/` 生拼答案。
应当：
- 明确这是任务流程问题
- 使用未来的 workflow 层知识，或在当前阶段基于多个 reference 做阶段性拼接

---

## 8. 未来可扩展方向

为了让这套 reference 更适合 Claude / Codex 查询，后面可以继续补：

### 8.1 `INDEX.md`
作为全局索引，快速列出：
- topics
- files
- params
- modules

### 8.2 更多参数卡片
优先建议补：
- `SuperCell.md`
- `Z_values.md`
- `isaAB.md`
- `Spin_values.md`
- `ExternalMagneticField.md`
- `fig.maxk.md`

### 8.3 workflow 层
后续新增：
- `workflows/exchange_fitting.md`
- `workflows/monte_carlo.md`
- `workflows/molecular_dynamics.md`
- `workflows/tight_binding.md`
- `workflows/magnon.md`

这样 skill 就能区分：
- reference 查询
- workflow 查询

---

## 9. 一句话操作准则

对 Claude / Codex 来说，这套 `pasp_reference/` 最简单的使用规则是：

- 先判断问题类型
- 优先命中最贴近的目录
- 先读正文回答语义
- 需要出处时再用锚点和来源页面

也就是说：
**正文负责回答，元数据负责追溯。**
