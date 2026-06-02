# GA.fix_cell

## 含义
用于设置是否固定晶胞。

## 默认值
F

## 取值
T/F

## 何时使用
- 当使用 `3.1.8 全局结构搜索常用设置项` 相关功能并需要设置 `GA.fix_cell` 时。

## 注意事项
- Source audit found the runtime default is `.FALSE.`. When `GA.fixlattice = T`, PASP forces `GA.fix_cell = T`; otherwise do not assume the cell is fixed unless the current input or user-confirmed setting says so.
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.8 全局结构搜索常用设置项
- 锚点：`#id17`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id17>
