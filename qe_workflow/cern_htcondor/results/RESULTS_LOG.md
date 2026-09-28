# CERN results log

## 2026-09-28 notes
- **slab2_v25 lost.** Removed at the 24 h wall-time limit during its CG bands step: a single k-point outran the 30 min max_seconds margin, and the job ended without a results tarball. It is not resubmitted; slab2_relax (running since about 09:00Z, Davidson bands, 7-day limit) supersedes it.
- **W site (preliminary).** The relax outputs were copied from the running jobs into `iwo_*_partial/`. At the 3x3x3 k-point grid, both cells relaxed and BFGS converged.
  - Final energies: E(W8b) = -15496.3476466 Ry, E(W24d) = -15496.3666037 Ry.
  - **dE = E(8b) - E(24d) = +0.01896 Ry = +0.258 eV**, so W prefers the 24d site.
  - The protocol k-point check (4x4x4) for W24d is still running.
- **SSH master lost at 12:06Z.** Jobs continue at CERN; the user's re-login is needed to fetch results. (read-out with analyze_slabs.py; criteria in ../PROTOCOL_CERN.md)

## slab1_v35: 1 nm slab, unrelaxed, 35 A vacuum (cluster 12756318, finished 2026-09-27T04:16Z)

**Run:** 16 CPUs, 4 pools. SCF 1 h 48 min wall (77 iterations); bands 1 h 29 min.
- 8 symmetry operations (with inversion); 4 irreducible k-points.

**Band edges:**
- VBM -1.9695 eV, CBM -1.0109 eV, so the KS gap is 0.959 eV.
- E_vac = 2.422 eV; the vacuum plateau is flat to < 0.01 meV.
- EA = 3.433 eV, IP = 4.392 eV.

**Status: preliminary, not a confinement value.**
- The geometry is unrelaxed. The total force is 0.27 Ry/bohr, dominated by the H atoms placed at a fixed 0.97 A.
- Lin et al. report 1.88 eV for their relaxed 0.95 nm slab. The unrelaxed gap is far below this and close to the bulk PBE gap.
- Possible reason: surface or O-H states at the band edges before relaxation. NOT DETERMINED FROM AVAILABLE DATA; decided by slab1_relax.
- The bulk reference gap at a = 10.306 A comes from stage 3.
- The vacuum test itself (EA and IP versus vacuum size) is valid at fixed geometry. It is completed when v15 and v25 finish.

## Vacuum convergence: 1 nm slab, unrelaxed (slab1_v15 and v25 finished 2026-09-27 ~23:50Z)

| vacuum | gap (eV) | EA (eV) | IP (eV) | SCF iterations |
|---|---|---|---|---|
| 15 A | 0.9586 | 3.4331 | 4.3917 | 46 |
| 25 A | 0.9586 | 3.4332 | 4.3918 | 64 |
| 35 A | 0.9586 | 3.4332 | 4.3918 | 77 |

**Criterion 6 (changes < 10 meV) is met by a wide margin:** changes are at most 0.1 meV. This is expected, because the slab is centrosymmetric and non-polar, so it carries no dipole. **25 A (Lin et al.) is confirmed.** The vacuum plateau is flat within 0.01 meV in every case.

**Cost note.** With CG diagonalization, the bands step took 13.7-13.9 h on 16 CPUs, against 1.5 h with Davidson for slab1_v35, which gave no failure. Davidson was therefore restored for the bands step of slab2_relax, which had not started. The jobs already running keep CG, and their max_seconds guard stops a bands run cleanly before the wall-time limit.
