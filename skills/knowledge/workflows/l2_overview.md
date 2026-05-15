# L2 Overview: Magnetic Effective Hamiltonian

Lecture 2 contains three independent PASP `Model` values. They are related, but they are not one executable workflow.

---

## Three Models

| Model | Main purpose | Typical input | Typical output / handoff |
|---|---|---|---|
| `find_J_path_sym` | Enumerate symmetry-inequivalent magnetic pairs and prepare four-state DFT structures | `PASP.input`, `cell.str`, `unit_cell.str` | `J.POS`, `pair_POS.NNN`, `atat.NNN_Y`, log `MAGMOM` / `M_CONSTR` blocks |
| `Spin_lattice_interaction` | Run PTMC and optionally CG to find a magnetic ground state from a known Hamiltonian | `PASP.input`, `MC.input`, `spin_exchange.dat`, structure files | `spin3_lowest.out`, `node_N_spin.out`, `*_PTMC_K.dat`, XSF visualization |
| `magnon` | Compute linear spin-wave dispersion from a Hamiltonian and a ground-state spin configuration | `PASP.input`, `spin_exchange.dat`, `spin3.in`, structure files | `spin_wave_E.dat`, optional `spin_wave_H_wf.dat` |

---

## Routing Rule

- If the user wants exchange paths or four-state DFT preparation, route to `l2_find_J_path_sym.md`.
- If the user already has `spin_exchange.dat` and wants a ground state or PTMC observables, route to `l2_spin_lattice_interaction_state_machine.md` then `l2_spin_lattice_interaction.md`.
- If the user already has `spin_exchange.dat` and `spin3.in`, route to `l2_magnon_state_machine.md` then `l2_magnon.md`.

When the user asks for "L2 magnetic Hamiltonian" without naming a Model, ask which of these three stages they are in.

---

## Shared Files Are Not Interchangeable

`cell.str` and `unit_cell.str` are shared structural inputs. Edits to atom order, species order, or supercell assumptions affect all downstream models.

`spin_exchange.dat` is shared between `Spin_lattice_interaction` and `magnon`, but the allowed content differs:
- `Spin_lattice_interaction` can consume the Lecture-2 fourth-order spin interaction section.
- `magnon` requires the fourth-order count to be `0`; otherwise the reader can misinterpret later sections.

`spin3.in` for `magnon` should normally come from:
- `Spin_lattice_interaction` `spin3_lowest.out` when present, or
- lowest-node `node_N_spin.out` when `spin3_lowest.out` is absent, or
- a user-confirmed hand-written FM / AFM / spiral configuration.

Do not default to `node_N_finalspin.out`; it is a PTMC final state and is not guaranteed to be the lowest-energy state.

---

## Current Run-Validated Observations

As of the 2026-05-10 NiI2 lecture validation:
- `find_J_path_sym` 5x5 run finished gracefully and produced `J.POS`, `pair_POS.001` through `pair_POS.007`, and `atat.001_1` through `atat.007_4`.
- `magnon` FM and spiral runs finished gracefully and produced `spin_wave_E.dat` plus `spin_wave_H_wf.dat`.
- `Spin_lattice_interaction` with `spin_lat.relax_str T` hit `SIGSEGV` on older runs / old image, but the same NiI2 Lecture-2 input finished gracefully with `paspmpi:v2`, including `CG finish`, `spin3_lowest.out`, and `relax-spin3_lowest.out`.

These are historical observations. Current user-workspace claims must still be grounded in the user's actual files and logs.
