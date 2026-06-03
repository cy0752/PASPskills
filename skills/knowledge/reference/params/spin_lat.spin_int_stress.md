# spin_lat.spin_int_stress

## 含义
是否计算自旋序导致的晶格应力。

## 默认值
F

## 取值
T/F

## 何时使用
- 当使用 `3.1.10 自旋序诱导铁电性统一极化模型常用设置项` 相关功能并需要设置 `spin_lat.spin_int_stress` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 当前已验证 PASP 源码 / runtime 中，该设置为 `T` 时会走 `read_spin_stress` 路径；该路径在 MPI rank 数大于 1 时会停止并报 `read_spin_stress: MPI version not implemented yet`。因此 L8 spin-lattice ion/strain 分支若启用 `spin_lat.spin_int_stress T`，提交前必须确认 planned MPI ranks 为 1，除非用户提供当前源码已修复并验证 MPI 支持的证据。
- 如果完成日志中出现 `read_spin_stress: MPI version not implemented yet`，即使平台调度状态显示成功，也应判定该 run 的 spin-stress 输出验证失败 / MPI-limited。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.10 自旋序诱导铁电性统一极化模型常用设置项
- 锚点：`#id19`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id19>
