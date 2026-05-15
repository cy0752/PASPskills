# Model

## 所属文件
`PASP.input`

## 来源章节
- 3.1.2.1 `Model`
- 来源页面：https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#model

## 含义
`Model` 是 PASP 中最关键的设置项，用来决定当前运行启用哪个功能模块。

它通常还会影响：
- 程序后续会读取哪些其他输入项
- 哪些附属文件是必需的
- 当前任务属于哪一类 workflow

## 默认值
`Charge_ordering`

## 可选值
当前网页中明确提到的选项包括：
- `find_J_path_sym`
- `Invariant`
- `Spin_lattice_interaction`
- `atomic_effective_H`
- `GA`
- `TB`
- `KNB`
- `magnon`

注：网页说明这里列出的只是手册中涉及到的选项，不一定是程序全部可用值。

## 何时使用
当你需要指定 PASP 此次运行属于哪种功能模式时，就需要设置 `Model`。

典型场景包括：
- 交换路径或交换参数相关流程
- 有效哈密顿量相关流程
- 全局结构搜索
- 紧束缚模型计算
- 自旋诱导极化计算
- 线性自旋波计算

## 写法
```text
Model find_J_path_sym
```

## 使用建议
- 建议写在 `PASP.input` 的靠前位置，最好是第一行附近
- 不要依赖默认值，最好显式写出
- 在设计 workflow 时，应先确定任务目标，再决定 `Model` 的取值

## 与 workflow 的关系
`Model` 不是 workflow 本身，而是 workflow 某一阶段启用的功能模式。

因此：
- 一个 workflow 可能只用一个 `Model`
- 也可能在不同阶段切换多个 `Model`

这也是为什么不建议把整个 PASP assistant 完全按 `Model` 拆成独立技能。

## 相关项
- `%block SuperCell`
- `%block Z_values`
- `%block isaAB`
- `%block Spin_values`
- `%block ExternalMagneticField`
- `cell.str`
- `unit_cell.str`
- `MC.input`
- `MD.input`

## 常见误区
- 把 `Model` 理解成完整 workflow，而不是某个运行模式
- 没有显式设置 `Model`，结果程序使用默认值
- 先想填参数，再决定 `Model`，导致参数和模式不匹配

## 速记
如果把 PASP 看成一个多功能程序，那么 `Model` 就是在告诉程序：
“这一次你要按哪一种功能模式来运行。”
