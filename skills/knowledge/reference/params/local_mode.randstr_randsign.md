# local_mode.randstr_randsign

## 含义
参见上一设置项，在“ local_mode.cal_para_method ”取1时，对于随机生成构型的部分，各模式先从各自对应的[最小值,最大值]均匀随机取值；在“ local_mode.randstr_randsign ”为T（缺省值为T）时再随机取正负号，否则不随机取正负号。

## 默认值
T

## 取值
T/F

## 何时使用
- 当使用 `3.1.7.7 随机生成构型或自定义构型的相关设置` 相关功能并需要设置 `local_mode.randstr_randsign` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.7.7 随机生成构型或自定义构型的相关设置
- 锚点：`#id14`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id14>
