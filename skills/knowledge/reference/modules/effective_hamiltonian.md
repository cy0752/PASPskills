# effective_hamiltonian

## 模块用途
主要用于 `Model Invariant` 构造有效哈密顿量，也常延续到 `Model atomic_effective_H` 的 MC 或 MD 模拟。其中部分设置也用于 `Model find_J_path_sym`。

## 常见相关设置
- `fig.maxk`：最大考虑到几体相互作用
- `block fig.mdist`：各体数相互作用的截断距离，单位 Bohr，通常不可缺省
- 展开阶数：
  - `GSM.maxpower`
  - `Invariant.power`
  - `Invariant.strain_power`
  - `Invariant.pure_strain_power`
  - `block local_mode.power`
- SOC 相关：
  - `Invariant.SOC`
  - `local_mode.GSM2lm_int`
  - `block local_mode.special_SOC`
- 自定义局域模式：`block local_mode.mode_definition`，具体格式见 `params/local_mode.mode_definition.md`
- 读取已有相互作用：`local_mode.read_interaction`

## 何时使用
- 建立局域模式、自旋、应变等自由度的有效模型时
- 需要控制展开体数、截断半径、展开阶数或 SOC 处理方式时

## 注意事项
- `block fig.mdist` 缺省会直接报错
- 需要 `GSM.maxpower` 时最好显式写出，不要依赖不同模型下不一致的默认值
- 单体高于 6 阶、二体及以上高于 4 阶时，程序可能极慢
- 修改 `local_mode.mode_definition` 前应先确认当前模型只需要自旋模式，还是还包含局域声子、位移或混合模式
- MC 或 MD 的额外控制项建议放到 `MC.input` 或 `MD.input`，并通过 `%include` 引入

## 来源章节
- 3.1.7 有效哈密顿量方法常用设置项
- 锚点：`#id12`
- 来源页面：<https://hzwtech.com/PASP/2023A/build/html/3%E8%BE%93%E5%85%A5%E6%96%87%E4%BB%B6%E3%80%81%E8%BE%93%E5%87%BA%E6%96%87%E4%BB%B6%E4%BB%8B%E7%BB%8D.html#id12>
