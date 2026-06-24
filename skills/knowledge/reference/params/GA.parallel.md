# GA.parallel

## 含义
用于设置是否使用并行方法。

## 默认值
F

## 取值
T/F

## 分支依赖
- `GA.parallel F`：走逐个结构本地优化路径。当前源码读取 `GA.VASPCMD`，并用该命令驱动 VASP 计算；如果要用外部 VASP 评价器，必须确认 `GA.VASPCMD` 非空且适配当前环境。
- `GA.parallel T`：走批量/并行结构优化路径。当前源码会调用 `bash run_pvasp.sh`；该脚本、VASP 输入、调度系统、输出目录和清理策略都必须由当前运行环境提供或确认。
- `GA.parallel` 只决定 PASP 如何调用外部结构弛豫流程，不自动保证 VASP/GULP 输入正确、任务提交成功或输出完整。

## 何时使用
- 当使用 `3.1.8 全局结构搜索常用设置项` 相关功能并需要设置 `GA.parallel` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 许多 L6 运行会选择 `GA.parallel T`，把串行/并行和作业系统细节交给 `run_pvasp.sh`，并保持 `vasp_N/` 目录布局一致；这是 workflow 实践建议，不改变源码默认值 `F`。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.8 全局结构搜索常用设置项
- 锚点：`#id17`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id17>
