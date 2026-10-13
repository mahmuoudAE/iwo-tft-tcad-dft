# H-L scored and A20(ii) smearing sensitivity (crystalline vacancy cells)

**Read (2026-10-13T00:25-00:31Z, user request "analyse the A20(ii) results"):** '!' energies, -TS, convergence lines and inputs of the six H-L cells (vac/<cell>/relax.out = k3 Gaussian 0.005; vac/<cell>/scf.out = k4 FINAL), and the six A20(ii) single points 12904174.0-.5 (checks/gpumax_work/a20_g002, k3 Gaussian 0.002, A100-PCIE-40GB). Crystalline only; no amorphous quantity opened. Parsed by script (hl_a20ii.py from the raw grep output), 1 Ry = 13.605693122994 eV.

**Checks:** all six relaxations 'bfgs converged' with no SCF failure (In32O48 and In31WO48 at 0 BFGS steps; In32O47 12, far 15, near 17, near72 28); every k4 FINAL and every A20(ii) SCF converged (conv_thr 1e-8). A20(ii) inputs differ from the k4 FINAL inputs only in degauss and K_POINTS (diff). All QE 7.3.1. Geometry identity confirmed where smearing is inactive: the In32O48 and In32O47 A20(ii) energies equal the k3 relax final energies to 1e-8 Ry. In31WO47_near is the A28 restart 1 with A19 settings (fallback not used; only max_seconds differs from far; one SCF took 90/100 iterations). Site rule: registered near = O30 (O30/O69 unsplit pair; O72 pair +0.01043 A, no TIE); far = O32 (host relaxed in 0 steps, order unchanged).

| Difference (eV) | k3, G 0.005 | k4, G 0.005 | k3->k4 | k3, G 0.002 | A20(ii) shift | Prediction |
|---|---|---|---|---|---|---|
| ΔE_local (O30, registered) | +0.5578 | +0.5321 | -25.7 meV | +0.5583 | +0.5 meV | >= +0.3 |
| ΔE_local (O72, sensitivity) | +0.6643 | +0.6230 | -41.3 meV | +0.6650 | +0.7 meV | (sensitivity) |
| ΔE_dop | +0.7259 | +0.7226 | -3.4 meV | +0.7261 | +0.2 meV | > +0.05 |

Per-cell k3->k4 (meV): In32O48 -1.7, In31WO48 -3.5, In32O47 +26.8, far +21.6, near -4.1, near72 -19.7. Per-cell width shifts (G0.002-G0.005, k3): 0 for In32O48/In32O47 (-TS ~0 at k3), +11.7 to +12.6 meV for the four W cells; they cancel in both differences. Zero-width estimates (F+|TS|/2, not registered) agree between widths within 1.6-3.5 meV per cell. In32O47 is smearing-inactive at k3 (-TS 1e-7 Ry) but not at k4 (-TS 0.32 mRy): band filling of the neutral V_O cell changes with the mesh.

**Reading by the registered rules (my proposal, needs your ruling):**
- ΔE_dop = +0.726 eV (k3; k3->k4 -3.4 meV <= 10 meV): prediction > +0.05 eV holds; within the forecast (+0.5 to +3).
- ΔE_local: +0.558 (k3) and +0.532 eV (k4), both >= +0.3 eV by about 0.23 eV, within the forecast (+0.5 to +1.5). k3->k4 = -25.7 meV > 10 meV, so A20 gives "unresolved significance"; the k4 value is reported and not adopted as converged.
- A20(ii): every shift is below 1 meV against the 50 meV rule and no verdict flips, so H-L is robust to the smearing width. A20(i) (spin) has not run; spin robustness is unassessed. In31WO48 (705 e) and the three In31WO47 cells (699 e) have odd electron counts.
- Disclosure: A20(i) construction details are still open and the H-L differences have now been read, so any A20(i) build from here is result-informed.
- Limits as registered: neutral cells, 80 atoms, 3.125 % W, far site 6-8 A from W images, PBE; ΔE_dop mixes local chemistry, strain and band filling and is not an upper bound on the Fermi-level effect.

**Questions:**
1. Is the ΔE_local verdict "prediction holds; significance unresolved (k3->k4 -26 meV)", or must the registered ΔE_local be reported UNRESOLVED?
2. Is a k5 single point on near and far (2 SCFs, A100 allowed, reported only, not adopted) worth running before 17 Oct, or is A20's label the end point?
3. A20(i): build now with a result-informed disclosure, or report spin robustness as unassessed and close H-L?
4. Anything to change before I log this (RESULTS_LOG, work chat, ledger via ledger-keeper)?
