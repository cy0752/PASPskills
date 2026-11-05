# L6 GA Search Run Notes

本文件记录 Lecture-6 examples、historical output and source-audit observations exposed for GA structure-search workflows. It is historical evidence and reference-gap orientation, not current user directory fact and not a parameter default source.

Runtime agents must prioritize:
- `l6_ga_search_state_machine.md`
- `l6_ga_search.md`
- `knowledge/reference/`

Do not copy this file's `SuperCell`, population size, generation count, probabilities, VASP inputs, Slurm settings, job ids, energies, symmetry labels or helper paths into a current task.

## Example Inventory

| Example | Branch shape | Input package clues | Helper / output clues |
|---|---|---|---|
| `pasp_examples/Lecture-6/Si/` | nonmagnetic, non-perturbation style | `Model GA`, `cell.str`, `unit_cell.str`, `seed.in`, VASP inputs, `GA.perturbation F` | nonmagnetic `run_pvasp.sh`, `opt/` second-pass optimization |
| `pasp_examples/Lecture-6/NaNbO3/` | nonmagnetic perturbation style | `Model GA`, structure includes, `GA.perturbation T` | VASP-coupled helper package |
| `pasp_examples/Lecture-6/BiFeO3/` | magnetic perturbation style | `GA.magnetic T`, `Spin_values`, magnetic GA flags, spin-polarized / LDA+U VASP input | magnetic-aware `run_pvasp.sh` and `opt/opt.sh` that handle `MAGMOM` |
| `pasp_examples/Lecture-6/_output_example/` | historical reduced NaNbO3 run | copied inputs and `PASP.used_info` show a small historical run | GA logs, generation artifacts, `Saved_*.POS`, low-energy summaries, `vasp_N/`, `opt/` outputs |

## Stable Lessons From Examples

- Lecture-style packages use `PASP.input` with explicit `Model GA` and direct `%include cell.str` / `%include unit_cell.str`.
- The examples include `INCAR`, `KPOINTS`, `POTCAR`, `pasp.slurm`, `vasp.slurm`, `run_pvasp.sh`, `seed.in` and `opt/`, but scheduler scripts and VASP paths are environment helpers, not portable defaults.
- `seed.in` is reproducibility-oriented. Reference marks it optional.
- `Z_values` must follow current material species order. Example values are material-specific.
- `SuperCell` differs by material and branch; never copy a matrix without current-structure confirmation.
- Nonmagnetic and magnetic `run_pvasp.sh` helpers have different assumptions. The magnetic helper expects `MAGMOM_<index>` and nested VASP cases.
- Post-GA `opt/opt.sh` is a second-pass optimization helper for retained `Saved_*.POS` structures. It is not proof that every GA run automatically produces optimized final structures.
- `opt/E.sh` is an energy extraction helper from VASP `OSZICAR`; it is not a PASP output contract.
- VASPKIT / findsym symmetry analysis is postprocessing. It does not prove GA convergence or VASP convergence by itself.

## Historical Input Values

Values observed in clean Lecture-6 examples include:
- `GA.population_size 10`
- `GA.max_generation 10`
- `save_str.nsave_str 20`
- `GA.Pher 0.85d0`
- `GA.Pmut 0.15d0`

These are example values, not defaults. Reference/source-confirmed defaults are separate, and production values must be user-confirmed.

The `_output_example` is a reduced historical run, with smaller settings such as population size `2`, max generation `1`, and saved-structure count `2`. Treat those only as smoke / demonstration provenance.

## Historical Output Families

Observed output families include:

| Family | Example names | Use in validation |
|---|---|---|
| effective settings | `PASP.used_info` | Confirms same-run resolved settings such as `Model GA`, branch flags, external program and saved-structure settings |
| seed evidence | `seed_used.in` | Reproducibility evidence when seed matters |
| initial / generation structures | `ini_str_POS.*`, `unrelaxed.*`, `relaxed.*`, `relaxed_child.*`, `sym_relaxed_child.*` | Generation diagnostics; exact presence depends on branch and version |
| external evaluator artifacts | `POSCAR.NNN.GGG`, `CONTCAR.NNN.GGG`, `OSZICAR.NNN.GGG`, `OUTCAR.NNN.GGG`, `MAGMOM.NNN.GGG`, `vasp_N/` | Candidate-level DFT / GULP provenance and failure diagnosis |
| saved structure state | `strs_saved.dat` | Restart / continuation and structure-array snapshot evidence |
| low-energy summaries | `low_ene_strs.dat`, `pc_low_ene_strs.dat`, `Saved_gen.dat` | Handoff tables and saved-candidate mapping |
| saved structures | `Saved_NNN.POS` | Raw retained structures for handoff or second-pass optimization |
| second-pass optimization | `opt/Saved_NNN/OSZICAR`, `CONTCAR`, `OUTCAR` | Separate validation target for optimized energies / symmetry analysis |

The historical log shows normal-completion style evidence including GA generation steps, VASP calculation completion messages, lowest-energy output and graceful finish. Runtime validation should inspect the current run's own logs and not rely on this historical text.

## Source-Audit Lessons Curated Into Workflow

- Runtime model selector is `Model GA`; missing `Model` may default elsewhere, so L6 inputs should write `Model GA` explicitly.
- `GA.parallel T` changes expectations toward `run_pvasp.sh`, `POSCAR_N` / `vasp_N/` style provenance and copied generation-suffixed DFT artifacts.
- `GA.lread_OUTCAR_mag T` is unsafe unless `GA.magnetic T` and readable `OUTCAR` magnetic moments are available.
- Restart controls require same-run provenance for saved or generation-suffixed artifacts; they are not fresh-run inputs.
- `GA.system interface` conditionally requires `GA.surfaces`; this is not required for bulk GA.
- Low-energy retention writes families such as `low_ene_strs.dat`, `pc_low_ene_strs.dat`, `Saved_gen.dat`, and `Saved_NNN.POS`.
- Source says `GA.fix_cell` default is `.FALSE.` and it is forced true when `GA.fixlattice` is true. This corrects the old curated reference value that listed default `T`.

## Reference Gaps To Preserve

Dedicated file cards are not yet available for many GA output artifacts:
- `Saved_NNN.POS`
- `Saved_gen.dat`
- `low_ene_strs.dat`
- `pc_low_ene_strs.dat`
- `strs_saved.dat`
- `POSCAR.NNN.GGG`
- `CONTCAR.NNN.GGG`
- `OSZICAR.NNN.GGG`
- `OUTCAR.NNN.GGG`
- `MAGMOM.NNN.GGG`
- `Atoms_info.dat`
- `POSCAR_N`
- `vasp_N/`
- `run_pvasp.sh`

Several source-backed controls also lack dedicated reference cards. Workflow docs may mention them as branch dependencies or reference gaps, but agents must not write exact lines for them without user authority or new reference coverage.

## Validation Caveats

- Historical output filenames show stable families, but actual presence still depends on PASP version, branch flags, external evaluator path and whether the run completed.
- A `Saved_NNN.POS` file proves retention by the GA run, not second-pass VASP convergence.
- `low_ene_strs.dat` / `Saved_gen.dat` should be tied to the same run directory and logs before handoff.
- Post-GA optimized energies require separate validation of the `opt/` VASP outputs.
- Symmetry labels from VASPKIT / findsym are postprocessing observations with their own tolerance and input provenance.
