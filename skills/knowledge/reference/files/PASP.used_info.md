# PASP.used_info

## 文件作用
记录 PASP 实际运行时各设置项的最终取值。

## 何时需要
- 排查输入是否生效
- 确认默认值
- 复现实验条件
- 调试 `%include`、默认值覆盖或单位转换问题

## 关键字段或内容
- 输出运行时解析后的参数值
- 若某项恰好使用默认值，会标注 `# Default value`
- 可能会列出一些与当前功能无关但程序内部仍输出的设置项

## 注意事项
它是核对“程序实际用了什么参数”的最直接输出文件。

## 来源章节
- 3.16 `PASP.used_info`
- 锚点：`#pasp-used-info`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#pasp-used-info>
