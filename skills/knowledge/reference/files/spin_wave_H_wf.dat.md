# spin_wave_H_wf.dat

## 文件作用
`Model magnon` 的详细诊断输出，包含每个 q 点的自旋波 Hamiltonian / 波函数求解详情。

## 何时产生
仅在 `spinw.write_detail T` 时产生。源码默认值为 `T`：

```text
spinw.write_detail = .TRUE.
```

源码位置：
- `Latticemodel/src/spinw.f90`：读取 `spinw.write_detail`，并在 `lwrite_detail` 为真时写 `spin_wave_H_wf.dat`

## 格式
文本文件，按 q 点分段。每段以分隔线和 `iq` / q 坐标开头，后面由 Colpa 对角化例程输出矩阵与本征信息。

该文件主要用于诊断，不是常规画图的首选输入。

## 下游使用
- 排查虚频、简并、矩阵异常或某个 q 点对角化问题。
- 和 `log.out` 中每个 q 点的求解信息一起定位问题。

## 注意事项
- 文件可能较大；生产长 q 路径时可以考虑关掉 `spinw.write_detail`，但关闭前应确认用户不需要诊断细节。
- 缺少该文件不一定表示 magnon 失败；需要先检查 `spinw.write_detail` 实际值和 `spin_wave_E.dat` 是否完整。

## 来源章节
- PASP 文档：3.1.11 线性自旋波色散计算常用设置项
- 源码审计：`Latticemodel/src/spinw.f90`
