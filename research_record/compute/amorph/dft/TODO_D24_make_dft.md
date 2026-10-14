# TODO for the main session: the make_dft.py side of D-24 (final-SCF export)

Written 2026-10-11 by the D-24 build agent. make_dft.py was NOT edited (the HfO2 build agent owns it). The change below
makes newly generated run directories match the staged D-24 install; existing run directories get the same result from
`install_D24.sh`.

## 1. final.tmpl: verbosity 'high' (relax.in stays 'low')

`qe_input()` hard-codes `verbosity = 'low'` (line 54) for both relax.in and final.tmpl. Add a parameter and pass
'high' only for the final template, so that scf.out prints the occupations f_nk for every k (register A16):

```python
def qe_input(calc, prefix, cell, atoms, ecut, kpts, slab, nbnd=None, extra_control='', smear=SMEAR_RELAX,
             verbosity='low'):
    ...
    ctrl = [f"  calculation = '{calc}', prefix = '{prefix}', outdir = './tmp', pseudo_dir = './pseudo'",
            f"  verbosity = '{verbosity}', tprnfor = .true., max_seconds = 1.0d8"]
```

and in `make()` (line 135):

```python
(run / 'final.tmpl').write_text(qe_input('scf', 'slab', cell, atoms, 71, k_final, slab, nbnd=nbnd, smear=SMEAR_FINAL,
                                         verbosity='high'))
```

Check after the edit: `python3 make_dft.py <test name>` into a scratch ROOT, then `diff` the new final.tmpl against an
installed one: the only difference must be the geometry. relax.in must still say 'low'.

## 2. steps_final.sh

No code change: make_dft.py copies `common/steps_final.sh` into each run (line 137). Once install_D24.sh has replaced
common/steps_final.sh, new runs get the D-24 version. Optional: one line in the module docstring (line 14), e.g.
"then planar-averaged potential, projwfc and the D-24 export (EOS: atomic_proj.xml, save of the 2.0 nm cells)".

## 3. Not changed by D-24, flagged for a decision before any FINAL release

- final.sub has `request_memory = 100 GB` and `request_disk = 60 GB` for every cell (126 to 414 atoms).
  - Disk: the collected wavefunctions are nk x nbnd x npw x 16 B: ~46 GB at 270 atoms, ~56 GB for the 1.5 nm cells
    (14.9 A in-plane) and ~74 GB at 414 atoms (aIWO_2p0_Al2O3_s2), i.e. at or above request_disk.
  - RAM: QE's own estimate in the RELAX checkpoints of these cells (60 Ry, default nbnd, one process, 4 k) is
    82-86 GB at 149-155 atoms and 130-173 GB at 252-274 atoms. The final uses 71 Ry (npw x1.29) and nbnd = 1.3 x
    occupied (x1.08), so a single-pool final needs roughly 115 GB (150 atoms) to 200-220 GB (270 atoms); steps_final
    runs -nk 4 on 32 CPUs, which holds a Davidson workspace per pool and needs more. 100 GB looks too small for every
    cell; a memory-held job loses its sandbox (lesson of 2026-10-02).
  See the D-24 report for the per-run table.
- The pilot runs/aIO_0p8_s1 has the same steps_final.sh and verbosity 'low'; install_D24.sh leaves it alone.
