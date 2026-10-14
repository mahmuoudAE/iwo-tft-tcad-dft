# A23 (ii): W-cell hybrid check, crystalline In31WO48

**Status:** staged on CERN in `~/iwo_amorph/hse/In31WO48/`. **Not submitted.**

**Source:** register `codex/work_chat/HYPOTHESIS_REGISTER.md`, amendment A23 (ii), frozen 2026-10-10T21:06Z.

This is a sensitivity check for H-G. It is not a registered test of H-G, and its result does not change the H-G scores.

## 1. Precondition

The H-L relaxation `~/iwo_amorph/vac/In31WO48` must have converged:

- `relax.out` contains `bfgs converged` and `End final coordinates`;
- `RELAX_STATUS` reads `CONVERGED`.

`launch.sh` refuses to start otherwise.

At staging time (2026-10-11) the RELAX node of DAG 12886354 (job 12886360) was still idle in the queue, so there was no `relax.out` yet.

## 2. Launch

Run these after the relaxation has converged:

```
cd ~/iwo_amorph/hse/In31WO48
bash launch.sh --dry   # builds scf_pbe.in and scf_hse.in from the converged relax.out, checks them, writes In31WO48.dag
bash launch.sh         # the same, then condor_submit_dag; the hook asks for approval
```

`launch.sh [--dry] [relax.out]` takes `~/iwo_amorph/vac/In31WO48/relax.out` by default. It does the following:

- copies `relax.out` to `relax_source.out`;
- takes the positions from the "Begin final coordinates" block and the cell from `vac/In31WO48/relax.in` (fixed-cell relax);
- refuses if the atom order differs from that `relax.in`;
- runs `tools/check_nc.py`;
- records the md5 sums in `LAUNCH_RECORD`;
- refuses a second submission.

## 3. What runs

The DAG `In31WO48.dag` runs **PBE first, then HSE**. Each node uses `RETRY 1 UNLESS-EXIT 2`.

The node script is `tools/nc_node.sh` and the steps are in `tools/steps_nc.sh`. Each node runs one `pw.x` single point and then `projwfc.x`.

**Exit codes:**

| Code | Status | Meaning |
|---|---|---|
| 0 | DONE | finished |
| 2 | SCF_NOT_CONVERGED | not replayed |
| 2 | PROJ_FAILED | not replayed; rerun only projwfc |
| 1 | FAILED | anything else; replayed once |

**Outputs**, back in this directory:

- `scf_{pbe,hse}.out`
- `projwfc_{pbe,hse}.out`
- `atomic_proj_{pbe,hse}.xml`
- `data-file-schema_{pbe,hse}.xml`
- `STATUS_*`
- `In31WO48_{pbe,hse}_results.tar.gz` (inputs, logs, PDOS)

These also go to EOS: `/eos/user/m/melrashe/qe/checkpoints/In31WO48_<tag>_proj_<cluster>.tar.gz` (A14 export).

**Settings.** These are the 2026-10-01 HSE check (RESULTS_LOG) plus A23:

| item | value |
|---|---|
| pseudopotentials | SG15 ONCV 1.2: In_ONCV_PBE-1.2.upf (md5 2123f823...), O_ONCV_PBE-1.2.upf (e36c48de...), W_ONCV_PBE-1.2.upf (b6096f31...); byte-identical copies of `~/qe_jobs_ncf160_20260930_174006/pseudo/` in `~/iwo_amorph/hse/pseudo/` |
| cutoffs | ecutwfc 80 Ry, ecutrho 320 Ry |
| hybrid | `input_dft = 'hse'` (HSE06), nqx 1x1x1, ecutfock 160 Ry (the PBE input is identical without this line) |
| k | 2x2x2 unshifted (8 k-points, checked with pw.x) |
| occupations | Gaussian, degauss 0.005 Ry; spin-unpolarised |
| bands | nbnd 432 (= 1.2 N_el/2); N_el(NC) = 719 |
| SCF | conv_thr 1e-9, beta 0.3, electron_maxstep 150, verbosity 'high' |
| resources | CPU 32, 100 GB, 40 GB disk, flavour testmatch, limit 250000 s; QE 7.5 (conda env) |

**Declared differences from 2026-10-01:**

1. **QE 7.5 on CPU instead of QE 7.3.1 on GPU.** The NGC GPU container (`qe-7.3.1-gpu.sif`) contains only pw.x/cp.x and no projwfc.x. Its `wfc*.dat` save cannot be read by the HDF5 QE 7.5 projwfc.x. One QE version for pw.x and projwfc.x is used, as for the slab finals (FORCE_CPU).
2. **No stress (`tstress` off).** The stress took 3.26 of the 4.0 h of the 96-atom slab HSE run and is not needed.
3. **Gaussian 0.005 instead of fixed occupations.** The W cell is metallic (A23).
4. **Projection basis**, see section 4.

**Electron count, important for band indices.**

- SG15 W carries 28 valence electrons (4f14 5s2 5p6 5d4 6s2); the PAW W set carries 14. So N_el(NC) = 719 and N_el(PAW) = 705.
- N_ex = 3: W6+ sits on an In3+ site with no extra O. This differs from the amorphous aIWO cells, which have N_ex = 1.
- Therefore N_v(NC) = (719 - 3)/2 = **358** and N_v(PAW) = 351 (= n_pure - 1, the pure cell having 352).
- Above the valence band, NC band n corresponds to PAW band n - 7. Never carry PAW band indices over: states are named only from their projections.

## 4. Projection basis (needs sign-off before the read-out is used)

**Problem.** The SG15 files contain no pseudo-atomic wavefunctions: `number_of_wfc="0"` and an empty `<PP_PSWFC>`. projwfc.x stops with "Cannot project on zero atomic wavefunctions!" (reproduced locally, QE 7.5).

**Fix (no download).**

- `tools/add_chi.py` writes projection copies to `~/iwo_amorph/hse/pseudo_proj/`. Each copy holds the PP_CHI functions of the pslibrary PAW set of the same element, which is the basis of every PAW projwfc in this project:
  - In: 5S 5P 4D;
  - O: 2S 2P;
  - W: 5S 6S 5P 6P 5D.
- The functions are interpolated onto the SG15 radial mesh, which ends at 6.01 bohr. The norm kept inside 6.01 bohr is 99.5 % for W 5D, 91 % for In 5P and 77 % for W 6P; Loewdin orthonormalisation in projwfc renormalises.
- pw.x runs with the **pristine** SG15 files. Only after the SCF does `steps_nc.sh` swap the copies into the save, and `tools/set_natomwfc.py` sets `num_of_atomic_wfc` in data-file-schema.xml. This is 484 for In31WO48: 31x9 + 48x4 + 13.
- W 4f has no projector function, so the 7 deep W-4f bands are unprojected. This raises the spilling but does not affect states near the gap.

**Validation (local, QE 7.5, 2026-10-11).** The comparison used In31WO48 at the *unrelaxed* vac geometry, Γ only, Gaussian 0.005, with the same 484 projectors. NC-PBE (SG15, 80 Ry) plus the copies was compared with PAW-PBE (pslibrary, 71/568 Ry), state by state, for PAW bands 345-371 (= NC bands 352-378).

**Mapping.** NC band n = PAW band n + 7 is confirmed. E - E_F agrees to ≤ 0.03 eV.

**W-5d weight.** max |Δ| = 0.016, mean 0.003. For example, the W-5d donor states are 0.474/0.414 (PAW) against 0.486/0.430 (NC).

**PR_n.**

- The valence and conduction edges agree to ≤ 0.015: 0.726 against 0.711 at the conduction edge.
- Higher In-5s/5p conduction states come out lower in NC, by up to 0.16. Typical values are 0.87 against 0.75, and borderline states 0.30 against 0.25. This is the effect of the In-5P tail truncated at 6 bohr.
- Both NC functionals use the same basis, so the bias largely cancels in Δ_a. Still, report any state whose PR_n lies within 0.05 of the 0.20 threshold.

**Other indicators.**

- |psi|² is 0.97-0.985 (NC) against 0.98-0.99 (PAW).
- The spilling parameter is 0.029 (NC, including the 7 unprojected W-4f bands) against 0.0024 (PAW).

**HSE save (smoke test, local QE 7.5, 2026-10-11).** A toy 5-atom In/W/O cell was used (HSE06 nqx 1, ecutfock 80, k 2x2x2, Gaussian 0.005, pristine SG15). Then the copies were swapped into the save, `set_natomwfc.py` was run (0 -> 34), and projwfc.x was run. It finished with JOB DONE and wrote atomic_proj.xml with the In 5S5P4D, W 5S6S5P6P5D and O 2S2P states. So the hybrid save can be projected the same way as the PBE one.

**Completeness (register section 1).** `nc_readout.py` flags the E_v, E_c and W-5d states when |psi|² < 0.90; a read-out that rests on a flagged state is unresolved. In the Γ validation above, every edge state has |psi|² of 0.97-0.99.

**Status.** The read-out is **provisional** until the main session (and Codex, under the check rule) accepts the basis.

## 5. Read-out rule (A23 (ii), frozen)

**Quantity.** The energy of the **lowest state with ≥ 30 % W-5d weight** (Loewdin), relative to the **host conduction edge**, in PBE and in HSE.

**Host conduction edge** (register section 1, A16).

- It is the lowest eigenvalue over all k of any state that:
  - lies above band N_v;
  - has PR_n ≥ 0.20 (atom domain = all N atoms);
  - is interior-weighted. For a bulk cell the interior is all atoms, so this condition always holds.
- It is *unresolved* if no state qualifies within 1.0 eV above the lowest state above N_v.
- PR_n = 1/(N Σ_i p_i²), where p_i is the atom weight divided by the total projected weight.

**Rule.**

- If the W-5d state stays above the host edge in both functionals, the PBE W-donor reading is **functional-robust**.
- If HSE puts it more than 0.1 eV below the host edge, H-G is reported with a **"functional-sensitive"** caveat.
- The H-G registered scores are not changed in either case.

## 6. Analysis steps

1. **Check the runs.**
   - `cat STATUS_pbe STATUS_hse` must both read DONE.
   - The HSE output must contain `!!` (EXX-converged energy) and no `convergence NOT achieved`.
   - Note the projwfc spilling parameter from `projwfc_*.out`.
2. **Read out each functional:**
   ```
   python3 ../tools/nc_readout.py --proj atomic_proj_pbe.xml --pout projwfc_pbe.out --nv 358 --json readout_pbe.json
   python3 ../tools/nc_readout.py --proj atomic_proj_hse.xml --pout projwfc_hse.out --nv 358 --json readout_hse.json
   ```
   Each prints the states N_v-3 to N_v+15 at every k (E, |psi|², PR_n, W-5d, top atom), the host edges E_v and E_c, the host-edge gap, the lowest W-5d ≥ 0.30 state above N_v, and `W5d_minus_Ec_eV`.
3. **Apply the rule** to `W5d_minus_Ec_eV`.
   - Positive in both functionals: functional-robust.
   - HSE value < -0.10 eV: functional-sensitive.
   - Any other outcome is not covered by the A23 text (HSE between -0.10 and 0 eV, or PBE ≤ 0). Report the numbers without a label and pass the case to the main session.
   - If E_c is unresolved, or the JSON says `rests_on_flagged_state: true`, the check is *unresolved*.
   - Also report:
     - `W5d_states_in_host_gap`;
     - the HSE-PBE host-edge gap difference, as a cross-check against Δ_c = 1.188 eV, crystalline In2O3 at Γ;
     - the occupations of the W-5d state, from data-file-schema_*.xml.
4. **Cross-check (PBE only).** The NC-PBE W-5d state vs the PAW-PBE projwfc of the same geometry. The H-L final does not run projwfc, so use the PAW crystalline values in RESULTS_LOG 2026-09-30 (24d: bands 353-355 carry 0.55/0.48/0.30 W weight, PAW numbering) only qualitatively: different geometry and k.
5. **Record.**
   - RESULTS_LOG.md entry with the job ids (DAG and node clusters).
   - Claims ledger entry as COMPUTED, with these caveats:
     - HSE06 with q = 1 (EXX q-sampling error in crystalline In2O3: about -42 meV in the gap);
     - SG15 NC, 80 Ry, PAW-PBE geometry;
     - crystalline, 1 W on 24d (3.1 % W), N_ex = 3, k 2x2x2, Gaussian 0.005;
     - borrowed PP_CHI projection basis.

## 7. Cost

The CPU engine is chosen because of section 3, difference 1. Estimate made on 2026-10-11 (A23 basis plus one local measurement):

- **GPU basis (2026-10-01, QE 7.3.1, 1 H100).** 40-atom bulk HSE (4 k, 192 bands, EXX grid 72³): PBE part 14 s, then 6 EXX cycles of 23-34 s. 96-atom slab (4 k, 328 bands, EXX grid 80×80×270): PBE part 316 s, then 7 EXX cycles of 219-517 s, 0.74 h without the stress (4.0 h with it).
- **CPU factor (measured).** The same 40-atom input on a local i7-12700H, 8 MPI ranks, QE 7.5: PBE part 518 s, first EXX cycle 1409 s, second EXX initialisation 925 s. That is 37-42 times the H100 time. Total energies agree with the GPU run to 3e-9 Ry. A 32-core CERN slot is taken as 2.5-3.5 times faster than 8 local ranks, so CPU ≈ 11-16 times the H100 time.
- **This cell.** 8 k, 432 bands, EXX grid 80³: EXX work per cycle 0.9 times the 96-atom slab's, so about 300 s per cycle on an H100, and the HSE single point about 0.6-0.7 h on an H100.
- **Expected on 32 CPUs:** HSE node 7-12 h, PBE node 1-2 h, plus projwfc (under 0.5 h each). The DAG runs them one after the other, so the total is 8-15 h. The limit is 250000 s (69 h). Memory: pw.x estimates 40 GB in total for HSE at 2 ranks; the measured RSS was 1.6 times the estimate, so 32 ranks should need about 60-80 GB of the 100 GB requested.

## 8. Files

| file | role |
|---|---|
| `launch.sh` | package parameters; calls `../tools/launch_nc.sh` |
| `nc.sub` | submit file (node `../tools/nc_node.sh`) |
| `preview_scf_{pbe,hse}.in` | dry-check inputs at the unrelaxed geometry (not used by the run) |
| `../tools/make_nc.py`, `check_nc.py`, `steps_nc.sh`, `nc_node.sh`, `add_chi.py`, `set_natomwfc.py`, `nc_readout.py`, `test_nc_stage.sh` | shared tools |
