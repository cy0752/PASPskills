# TB.write_wf

## 含义

控制 TB run 是否输出每个 k 点、每条能带的波函数 XSF 文件。源码 `TB.f90` 中读取该项后，在每个 eigenstate 循环里写出 `wf_kpt_<ik>-band_<ib>.xsf`。

## 默认值

F

## 取值

T/F

## 何时使用

- 需要查看或可视化 TB wavefunction spatial pattern 时。
- L7 flat-band / CLS 分析前后，若用户希望检查特定能带波函数时。

## 注意事项

- 打开后可能产生大量 `wf_kpt_*-band_*.xsf` 文件。
- 输出文件必须经过当前 run 的 output validation 后才能作为分析依据。

## 来源

- Lecture-7 custom TB / flat-band examples.
- Source audit: `/inspire/qb-ilm/project/cq-scientific-cooperation-zone/ky26048/latt/Latticemodel/src/TB.f90`.

