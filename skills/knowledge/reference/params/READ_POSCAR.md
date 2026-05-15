# READ_POSCAR

## 含义
如果已有晶胞的 POSCAR 文件（VASP软件的常用输入文件之一），也可以直接用它取代 cell.str 作为晶胞结构的输入文件。此时需要在 PASP.input 中将此项设为T；该项设置为T时，还会自动生成相应的 cell.str 文件。这里需要提供的 POSCAR 文件兼容以下两种格式：A.第一行提供任意内容，第五行提供各元素符号，第六行提供各元素的原子个数（参见3.1.3.8节格式A示例文件）；B.第一行提供各元素符号，第五行直接提供各元素的原子个数（参见3.1.3.8节格式B示例文件）。

## 默认值
F

## 取值
T/F

## 何时使用
- 当使用 `3.1.3.7 用POSCAR文件代替cell.str (READ_POSCAR)` 相关功能并需要设置 `READ_POSCAR` 时。

## 注意事项
- 修改前应确认当前 workflow 阶段确实需要该设置，不要用参数调整掩盖结构或文件依赖错误。
- 若涉及精确行格式或复杂示例，应回到来源章节核对。

## 来源章节
- 3.1.3.7 用POSCAR文件代替cell.str (READ_POSCAR)
- 锚点：`#poscarcell-str-read-poscar`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#poscarcell-str-read-poscar>
