# local_mode.cal_para_method

## 含义
在有效哈密顿量方法模块中常用。用于设置采用哪种方式定义构型，可以自定义，也可以随机生成。最常用的设置选项有1、5和6。需要注意的是该项设置仅在“ Invariant.cal_para ”取T时生效；而在“ Invariant.use_alamode_IFC ”取T（缺省值为F）时将自动设置为9（全原子模型）。设置值6是用 distortion.pos （必要文件）和 distortion.MAGMOM （无自旋自由度时可省略）文件提供自定义的构型信息，并在这两个文件内直接提供扩胞后的数据；设置值5是在 PASP.input 文件中用“block local_mode.mode_amp”提供自定义的构型信息，扩胞是利用“ block SuperCell ”设置项或 cell.str 文件完成的；设置值1是自动随机生成（也支持有序生成）多组构型，它也是通过“ block SuperCell ”设置项或 cell.str 文件完成扩胞。

## 默认值
1

## 取值
1/4/5/6/9等（手册目前仅介绍最常用的1、5、6）

## 何时使用
- 当使用 `3.1.7.7 随机生成构型或自定义构型的相关设置` 相关功能并需要设置 `local_mode.cal_para_method` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.7.7 随机生成构型或自定义构型的相关设置
- 锚点：`#id14`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id14>
