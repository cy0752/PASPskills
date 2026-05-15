# PASP reference 抽取方案（Step 1）

## 目标
将 PASP 网站文档整理为适合 skill 查询的本地 reference 知识库。

本步骤只定义抽取策略，不开始批量抓取内容。

---

## 一、总体原则

不要把网站内容直接镜像成一个大 markdown。

应该将网站内容重组为两类知识：
1. 面向对象的专题文档
2. 面向字段的参数卡片

这样可以兼顾：
- 用户按“文件/模块”查询
- 用户按“参数名”查询
- skill 做精确检索和交叉引用

---

## 二、分三步抽取

### Step 1：抽目录骨架
先提取网页中的标题树，形成目录索引。

建议保存内容：
- 编号，例如 `3.1.2.1`
- 标题，例如 `Model`
- anchor
- 父级章节
- 页面来源 URL

建议产物：
- `reference/toc.json`
- 或 `reference/toc.md`

作用：
- 确认网站结构是否稳定
- 为后续切块提供主键
- 保留原始来源定位

---

### Step 2：抽专题文档
按“知识对象”而不是“网页页面”生成 markdown。

优先专题类型：
- 输入文件
- 输出文件
- 模块设置
- 通用规则

建议产物目录：

```text
reference/
  inputs/
  files/
  modules/
```

典型文件：
- `inputs/PASP.input.md`
- `inputs/MC.input.md`
- `inputs/MD.input.md`
- `files/cell.str.md`
- `files/unit_cell.str.md`
- `files/spin_exchange.dat.md`
- `modules/effective_hamiltonian.md`
- `modules/tb.md`
- `modules/magnon.md`

每个专题文档中保留：
- 概述
- 相关字段
- 写法示例
- 依赖文件
- 常见误区
- 来源章节

---

### Step 3：抽参数卡片
把适合单独查询的字段整理成独立条目。

适合抽卡片的对象：
- `Model`
- `READ_POSCAR`
- `fig.maxk`
- `block SuperCell`
- `AtomicCoordinatesFormat`
- `Read_init_spin`

建议产物目录：

```text
reference/
  params/
```

建议每个参数条目的字段：
- 参数名
- 所属文件
- 所属模块
- 默认值
- 可选值
- 含义
- 何时使用
- 依赖项
- 相关文件
- 示例
- 常见错误
- 来源 anchor

参数卡片可以用 `.md` 或 `.yaml`。

如果目标是给 skill 直接读，我建议第一版先用 `.md`，后面需要结构化检索时再转 `.yaml`。

---

## 三、为什么不用“整页一个 md”

因为这页同时混合了：
- 规则说明
- 参数说明
- 文件格式
- 模块设置
- 示例输入

如果整页塞进一个 md，会有这些问题：
- 检索命中不精确
- 同一条回答里上下文太杂
- skill 很难区分“文件问题”和“参数问题”
- 后续维护会很痛苦

所以应采用：
- 标题骨架保留网页结构
- 专题文档承接主体内容
- 参数卡片承接细粒度查询

---

## 四、推荐的本地目录结构

```text
reference/
├── toc.json
├── inputs/
│   ├── PASP.input.md
│   ├── MC.input.md
│   └── MD.input.md
│
├── files/
│   ├── cell.str.md
│   ├── unit_cell.str.md
│   ├── POSCAR.md
│   ├── POSCAR_UC.md
│   ├── spin_exchange.dat.md
│   ├── seed.in.md
│   ├── distortion.pos.md
│   ├── distortion.MAGMOM.md
│   ├── local_mode_PM.dat.md
│   ├── J_best.dat.md
│   └── Fitting_Settings.txt.md
│
├── modules/
│   ├── effective_hamiltonian.md
│   ├── ga.md
│   ├── tb.md
│   ├── knb.md
│   └── magnon.md
│
└── params/
    ├── Model.md
    ├── SuperCell.md
    ├── Z_values.md
    ├── isaAB.md
    ├── READ_POSCAR.md
    ├── READ_POSCAR_UC.md
    ├── fig.maxk.md
    └── AtomicCoordinatesFormat.md
```

---

## 五、抽取优先级

为了让第一版尽快可用，建议优先抽这些内容：

### 第一优先级
- `PASP.input`
- `Model`
- `cell.str`
- `unit_cell.str`
- `MC.input`
- `MD.input`

### 第二优先级
- effective Hamiltonian 相关设置
- TB 相关设置
- magnon 相关设置
- `spin_exchange.dat`
- `J_best.dat`

### 第三优先级
- 其余附属文件
- 更细碎的参数项
- 更长的案例说明

---

## 六、第一步之后要做什么

完成本步骤后，下一步建议是：

### Step 2（待执行）
先生成一个 `toc` 骨架，把这个网页里目前能识别到的章节和锚点整理出来。

等你检查通过后，再进入：
- Step 3：从 `PASP.input` 开始拆出第一批专题文档
- Step 4：从 `Model` 等核心参数开始拆参数卡片
