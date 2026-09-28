# Astra vs Claude model lineages: parameter-by-parameter audit

Both lineages descend from the same seed (`model_seed.json`: Fan 2021 band priors, SI permittivities, exponential tail, 2 um contact overlap, WIDTH = 1 um). Both are real-ATLAS calibrations on this installation (DeckBuild 5.0.10.R / ATLAS 5.28.1.R). Neither is a thickness-aware physical model: each thickness carries its own NTA/WTA/ND/mu. Values below are the SELECTED runs of each lineage. "Same" means numerically identical in both.

| Parameter | Astra (priority-three, 2026-09-12) | Claude (IWO_ATLAS_Model_claude, 2026-09-21) | Comment |
|---|---|---|---|
| Structure | screened stack; Air / IWO / Al2O3 / HfO2 / Conductor gate volume; Pd S/D as electrode volumes (material=Palladium) | screened stack; IWO / Al2O3 / HfO2; gate = ideal contact at the HfO2 bottom; S/D = ideal contacts on the IWO top surface; no ambient region meshed | electrically equivalent for DC (equipotential metals); Claude has fewer nodes |
| L / W / sim width / overlap | 20 / 290 / 1 um / 2 um (assumed) | same | overlap sensitivity never tested by either |
| Eg / chi / eps_IWO | 3.05 eV / 4.30 eV / 9.30 | same | thickness-independent in both; V1 replaces with Eg(t), chi(t) |
| Nc / Nv | 5e18 / 1e19 cm^-3 | same | 5e18 <-> m* 0.34 m0 (Astra consistency note); literature m* 0.18-0.23 -> V1 Nc 2.4-3.4e18 |
| eps HfO2 / Al2O3 | 19.57 / 9.0 | same | Cox 8.955e-7 F/cm^2 |
| Gate work function | 4.765 eV (fit04 "gate shift" 0.065 folded in) | 4.70 eV + INTERFACE QF (dVfb +0.056/+0.082/-0.204/-2.18 V) | both use an effective flat-band correction; Claude's is per thickness |
| S/D contact | workfunction 4.45 + SURF.REC (0.15 eV effective barrier), ARICHN 110 inherited; sensitivity to 41: 0.38 % | ideal Ohmic; 31.8 nm adds CONTACT RESISTANCE 4.6e4 ohm.um per contact | both underconstrained (no TLM) |
| Bulk tail NTA (cm^-3/eV) / WTA (eV) | 5.5e20/0.040 (2 nm); 3.71e20/0.040 (6.3); 7.14e19/0.035 (13.2) | 4.59e20/0.0438 (2); 3.73e20/0.0360 (6.3); 1.26e20/0.0364 (13.2); 1.04e20/0.15 (31.8, partial) | Nt = NTA*WTA: Astra 2.2e19/1.49e19/2.5e18; Claude 2.0e19/1.34e19/4.6e18 -> consistent decreasing trend ~ t^-0.75 |
| Deep Gaussians | NGA = NGD = 0 | NGA 5e16-2e17 at Ec-0.6 eV (insensitive) | |
| Interface traps | none (INTDEFECTS disabled) | acceptor sheet 2e11-6e11 cm^-2/eV at Ec-0.3 eV regularized into a 0.25 nm layer | Claude's interface-layer check: 0.009 dec effect |
| ND (cm^-3) | 2e17 / 1e17 / 8.9e17 | 2e17 / 3e17 / 3e17 / 2.65e18 (31.8) | both need higher ND for thicker films |
| Band mobility (cm^2/Vs) | 13.3 / 12.0 / 55 | 12.3 / 11.3 / 55.1 / 82 | remarkably consistent between independent fits |
| Mobility model | constant (Tokyo/PRPMOB dormant) | constant (bias-indexed law proven ineffective: run_0008) | |
| Carriers / statistics | electrons only, Fermi, SRH | same | |
| Solver tolerances | cr.toler 1e-20, ir.tol 1e-20, cx.toler 1e-6, itlimit 60 | XANDRNORM + cr.toler 1e-17 (scaled per device) in depletion, default above; ir.tol 1e-19; itlimit 80 | Claude documents why 1e-19/1e-20 never converge with DEFECTS (run_0009) |
| DOS levels | 384/192 (2 nm), 192/96 (6.3, 13.2) | 96/48 (check x2: 0.006 dec) | |
| Vertical mesh in IWO | 0.25 nm uniform (2 nm); graded 0.79/1.65 nm (6.3/13.2) | 0.25 nm (2 nm, 0.0625 nm at interface layer); graded to 1 nm for thick films | |
| Active-region log RMSE | 0.0334 / 0.0492 / 0.0490 dec | 0.019 / 0.048 / 0.025 / 0.093 dec | same active mask definition (5x off-band median) |
| Id(+3 V) error | +0.69 / +1.97 / +2.45 % | -3.3 / 0.0 / 0.0 / -8.3 % | |
| Numerical certificates | 2 nm width/x/y/DOS PASS; 6.3 x/y/DOS PASS; 13.2 DOS MISSING | 2 nm mesh/DOS/interface PASS; 13.2 mesh PASS (x0.7); 6.3 not run; 31.8 none | |
| Off-state plateaus | not reproduced (native zeros 54/54/46) | not reproduced (native zeros 33/26/23) | identical conclusion |
| 31.8 nm | deferred (extension runs: 0.26-0.42 dec) | partial: back-surface donor sheet + series R, 0.093 dec | |
| Quantum | hard-wall Schrodinger-Poisson charge sensitivity (diagnostic only) | none | V1: confinement via Eg(t)/chi(t)/m*(t) (Approach A) |
| Launch accounting | 70 invocations / 75 stages (RUN_BY_RUN_SUMMARY) | 34 launches (RUN_INDEX.csv) | |

## Assessment

- Agreement: two independent calibrations converge on the same effective tail capacity (~2e19 cm^-3 at 2 nm falling ~4x by 13.2 nm), the same band-mobility step between 6.3 and 13.2 nm (~12 -> ~55 cm^2/Vs) and the same conclusion that intrinsic DD cannot produce the off-state floors. These are the robust, lineage-independent findings.
- Disagreement: ND(6.3 nm) 1e17 vs 3e17 and the flat-band treatment (single gate WF vs per-thickness Qf) show the electrostatic degeneracy between chi, Phi_m, ND and Qf. This is exactly what the thickness-aware chi(t) is meant to remove.
- Question for V1: can Eg(t), chi(t), Nc(t) with ONE gate work function, ONE Qf, a Nt(t) law with shared WTA, and a Nd(t) law reproduce the Astra/Claude active-region quality (<=0.05 dec) with fewer independent parameters? Counting: Astra 3 films x (NTA, WTA, ND, mu) + WF = 13; Claude 4 x (NTA, WTA, ND, mu, dVfb) + 31.8-specific = 22+; V1 target: 2 (Nt law) + 1 (WTA) + 3 (Nd law) + 4 (mu_band) + 1 (Qf) + 31.8 extras = 11-13 for four films, with the band parameters fixed by literature.

## Answer to the audit question (2026-09-21, after the V1 runs)

Does the physics-constrained model reproduce the Astra/Claude quality with fewer parameters? Partly. On the two calibrated films it does: 0.037 dec (2 nm) and 0.081 dec (13.2 nm) with ONE shared electrostatic value (Qf 1.73e12 cm^-2) and one band mobility each, where Astra needed per-device Nd/Nt/WTA/mu (0.033 and 0.049 dec) and Claude V0 per-device Nd/NTA/WTA/mu/Qf/Dit (0.019 and 0.025 dec). On 6.3 nm it does not: the shared laws miss the threshold by 0.29 V (0.68 dec), whereas both lineages fitted it (0.049 / 0.048 dec) with a device-specific donor density or flat band; the V1 equivalent with one device-specific Qf reaches 0.082 dec (run_0007). The 31.8 nm device was excluded from V1's final set (Astra deferred it; Claude V0 reached 0.093 dec with a back-surface sheet + series resistance hypothesis). Net: V1 trades ~0.03-0.06 dec of per-device accuracy for cross-thickness structure, and exposes the 6.3 nm anomaly that per-device tuning had hidden.
