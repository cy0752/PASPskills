# L8 ion/strain XSF outputs

## 文件作用
L8 spin-lattice ion / strain contribution runs may write diagnostic XSF visualization files such as:
- `1.xsf`, `2.xsf`, `3.xsf`
- `01dJ.xsf`, `02dJ.xsf`, `03dJ.xsf`

These files visualize same-run displacement / force / derivative-style vector fields used while analyzing spin-lattice force, stress, strain and related contributions.

## 何时出现
- Observed in L8 `BiFeO3_ion_strain` runs with `Model Spin_lattice_interaction`.
- Presence depends on active branch, settings, PASP version and how far the run progressed before any failure.

## 关键字段或内容
They use XSF-style `CRYSTAL` / `PRIMVEC` / `PRIMCOORD` content:
- coordinates are in Angstrom-style XSF coordinates;
- each atom row includes a vector field with 3 components;
- some files may use atomic numbers as the first column and others element symbols, depending on writer path.

Current L8 validation uses them as visualization diagnostics only. Exact physical interpretation of each numbered file should be tied to the corresponding PASP log section and current source / workflow branch before making quantitative claims.

## 验证用途
- Useful same-run diagnostics for L8 ion / strain calculations.
- Not sufficient as output validation by themselves.
- A valid handoff still requires `log.out` normal completion plus summaries such as `Pion,Pcell`, `Total P_{ion+lattice}`, `P due to spin force`, and `P due to spin stress` when those contributions are active.
- If a run contains `read_spin_stress: MPI version not implemented yet`, these XSF files remain dirty / diagnostic and must not be used as successful spin-stress output evidence.

## 来源
- L8 runtime observation: `BiFeO3_ion_strain_1task` produced `1.xsf`, `2.xsf`, `3.xsf`, `01dJ.xsf`, `02dJ.xsf`, `03dJ.xsf` together with normal completion
- PASP source orientation: XSF writers use `write_xsf_spin_gen`-style vector fields in several spin-lattice / phonon paths
