# A23 (iii): amorphous-bulk hybrid check, aIO_bulk_s1

**Status:** staged on CERN in `~/iwo_amorph/hse/aIO_bulk_s1/`. **Not submitted.**

**Source:** register `codex/work_chat/HYPOTHESIS_REGISTER.md`, amendment A23 (iii), frozen 2026-10-10T21:06Z.

This check tests the **offset** between HSE06 and PBE, not the thickness ratio r. An amorphous slab hybrid is out of scope because of cost.

## 1. Precondition

The A23 (i) PBE relaxation `~/iwo_amorph/runs/aIO_bulk_s1` must have converged:

- `relax.out` contains `bfgs converged`;
- `RELAX_STATUS` reads `CONVERGED`.

`launch.sh` refuses to start otherwise. At staging time (2026-10-11), (i) was built but not submitted.

## 2. Launch

Run these after the relaxation has converged:

```
cd ~/iwo_amorph/hse/aIO_bulk_s1
bash launch.sh --dry   # builds scf_pbe.in and scf_hse.in from runs/aIO_bulk_s1/relax.out, checks them, writes aIO_bulk_s1.dag
bash launch.sh         # the same, then condor_submit_dag; the hook asks for approval
```

## 3. What runs

The run is the same as A23 (ii) (see `../In31WO48/README.md`, sections 3 and 4): DAG PBE, then HSE, on CPU with QE 7.5, followed by projwfc with the PP_CHI projection basis. Only these settings differ:

| item | value |
|---|---|
| cell | 125 atoms (In50 O75), cubic 11.8083 A, fixed (the PBE relax is fixed-cell), positions from the converged relax.out |
| k | **Gamma** (`K_POINTS automatic 1 1 1`, complex code path as tested on 2026-10-01) |
| bands | nbnd 660 (= 1.2 N_el/2); N_el(NC) = 1100 = N_el(PAW); N_ex = 0, so N_v = 550 |
| resources | CPU 32, 64 GB, flavour testmatch, limit 250000 s; PBE and HSE with 1 pool |
| Atomic wavefunctions for projwfc | 750 (50x9 + 75x4) |

**Choice of k: Gamma.**

1. **The read-out is a difference.** It is the offset Δ_a = E_g^HSE - E_g^PBE, both taken at the same k set, so k-sampling errors of the gaps cancel to first order.
   - HSE acts mostly as a rigid shift of the conduction edge relative to the valence edge.
   - The supercell Γ point contains the Γ point of the primitive cell, where the In2O3 conduction-band minimum lies.
2. **With nqx = 1 the exchange uses each k with itself only.** So 2x2x2 does not improve the EXX sampling. The Γ-only cell (1646 A³) is in fact a denser EXX sampling than the q = 1 crystalline reference (40-atom primitive cell, 547 A³). There, q = 3 moved the crystalline gap by -42 meV.
3. **Cost and memory.** 2x2x2 has 8 k-points and no symmetry, so it costs about 8 times Γ. Its EXX buffer alone is about 8 x 550 x 0.73-0.88 M x 16 B = 52-62 GB, while Γ needs about 19 GB in total (pw.x estimate 9.63 GB per process at 2 ranks).

The PAW-PBE reference gap of (i) uses k 2x2x2. The NC-PBE Γ gap is therefore not directly comparable to it; it is compared only qualitatively. The A23 rule uses only the NC pair.

## 4. Read-out rule (A23 (iii), frozen)

**Quantity.** The amorphous offset **Δ_a = E_g^HSE - E_g^PBE**, both host-edge gaps from this package (NC, identical settings). It is compared with the crystalline Δ_c = 2.108 - 0.920 = **1.188 eV** (RESULTS_LOG 2026-10-01, Γ gaps, fixed occupations, q = 1).

**Rule.**

- If |Δ_a - Δ_c| ≤ 0.10 eV, the crystalline-based correction is used for the amorphous films.
- Otherwise the amorphous offset is reported and used, with its uncertainty.

**Host edges** (register section 1, A16; bulk cell, so the interior is all atoms and the interior-weight condition always holds):

- **Conduction edge E_c.** The lowest eigenvalue over all k of a state above band N_v (= 550) with PR_n ≥ 0.20. It is *unresolved* if no state qualifies within 1.0 eV above the lowest state above N_v.
- **Valence edge E_v.** The highest eigenvalue over all k of a state at or below band N_v with PR_n ≥ 0.20.
- **Gap.** E_g = E_c - E_v. The KS HOMO-LUMO gap is not used, because tail states distort it.
- **PR_n** = 1/(N Σ_i p_i²) over all N = 125 atoms, where p_i is the atom weight divided by the total projected weight.

## 5. Analysis steps

1. **Check the runs.**
   - `STATUS_pbe` and `STATUS_hse` must both read DONE.
   - The HSE output must contain `!!` and no `convergence NOT achieved`.
   - Note the projwfc spilling parameter.
2. **Read out each functional:**
   ```
   python3 ../tools/nc_readout.py --proj atomic_proj_pbe.xml --pout projwfc_pbe.out --nv 550 --json readout_pbe.json
   python3 ../tools/nc_readout.py --proj atomic_proj_hse.xml --pout projwfc_hse.out --nv 550 --json readout_hse.json
   ```
3. **Compute the offset.** Δ_a = gap_host(HSE) - gap_host(PBE). Report:
   - Δ_a - 1.188 eV and the rule outcome;
   - the KS gaps (for reference only);
   - the number of tail states between E_v and E_c in each functional.
   If either edge is unresolved, or the JSON says `rests_on_flagged_state: true` (|psi|² < 0.90, register section 1), the check is *unresolved*.
4. **Uncertainty to state with Δ_a:**
   - EXX q-sampling: the crystalline q = 1 to q = 3 change was -42 meV;
   - the edge-selection threshold: repeat with PR_n 0.15 and 0.25 as a sensitivity check, not the test;
   - a single amorphous seed.
5. **Record.**
   - RESULTS_LOG.md entry with the job ids.
   - Claims ledger entry as COMPUTED, with these caveats:
     - HSE06 with q = 1;
     - SG15 NC 80 Ry;
     - amorphous (ML-built, one seed), PBE-PAW-relaxed geometry, no W;
     - k = Γ;
     - Gaussian 0.005;
     - borrowed PP_CHI projection basis (see `../In31WO48/README.md` section 4).

## 6. Cost

The basis and the CPU factor (11-16 times the H100 time on 32 CPUs, measured locally on 2026-10-11) are given in `../In31WO48/README.md` section 7.

- **This cell at Γ.** 1 k, 660 bands, 550 occupied, EXX grid 90³: EXX work per cycle about 0.37 times the 96-atom slab's, so about 125 s per cycle on an H100. The PBE part is 0.05-0.1 h, because an amorphous cell may need 1.5-2 times more SCF iterations. The HSE single point is therefore about 0.3 h on an H100.
- **Expected on 32 CPUs:** HSE node 3-5 h, PBE node 0.5-1 h, plus projwfc. In total 4-6 h, against a limit of 250000 s.
- **2x2x2, for comparison.** It would have 8 times the EXX work and the PBE work: about 25-40 h on 32 CPUs, and an EXX buffer of about 52-62 GB. This is why Γ is used (section 3).
