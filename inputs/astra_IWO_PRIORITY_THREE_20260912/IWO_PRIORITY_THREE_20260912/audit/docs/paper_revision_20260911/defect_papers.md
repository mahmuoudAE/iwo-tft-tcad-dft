# Evidence from the oxygen-defect and gate-leakage papers

Read-only review of the original supplied PDFs, 2026-09-11. Page numbers below are PDF page numbers, matching the printed pages. Text was extracted with pypdf. Pages 3-6, 9, 11, and 12 of the 2021 paper were rendered and visually inspected to check equations, parameter values, and energy references. This note does not report a simulator run or a calibrated result.

## Sources and transferability

1. *Numerical Analysis of Oxygen-Related Defects in Amorphous In-W-O Nanosheet Thin-Film Transistor*, Nanomaterials 2021, 11, 3070, DOI 10.3390/nano11113070. Original file: `C:/Users/moham/Downloads/TFT_IWO-HfO2_2021_[O2]_Numerical Analysis of Oxygen-Related Defects in Amorphous In-W-O Nanosheet Thin-Film Transistor.pdf`.
2. Lee, Lim, and Kim, *Effects of Unusual Gate Current on the Electrical Properties of Oxide Thin-Film Transistors*, Scientific Reports 2018, 8, 13905, DOI 10.1038/s41598-018-32233-4. Original file: `C:/Users/moham/Downloads/s41598-018-32233-4 (1).pdf`.

The 2021 study is a **4 nm** IWO device with **30 nm HfO2 directly contacting IWO**, Mo gate and S/D, W/L = 80/40 um, 5 um overlap, and SU-8 back-surface passivation (pp. 2-3). IWO was RF magnetron sputtered at room temperature from 96 wt.% In2O3 / 4 wt.% WO3, at 3 mtorr, 50 W, 13.56 MHz. The Mo electrodes were DC sputtered. HfO2 was PEALD deposited at 250 C and annealed in oxygen at 400 C for 30 min. This is **not** the 2026 thickness-series process or its Pd / IWO / Al2O3 / HfO2 / TiN stack. The 2021 oxygen percentages must not be assigned to the four 2026 thicknesses. Its parameter values are priors and sensitivity ranges, not measurements of the 2026 devices.

The 2018 study uses **IGZO**, principally 20 nm, thermally oxidized **200 nm SiO2**, heavily doped p-type Si gate, 100 nm Al S/D, W/L = 1000/50 um, and large active areas of 1.5 or 36 mm2 (pp. 2-3). Further comparisons use 50/100/200 nm SiO2 and IGZO thicknesses 10-80 nm (pp. 5-6). It supplies no calibrated IWO Gaussian DOS parameter table. It supports checking gate leakage and geometry-dependent parasitic current, not transferring SiO2 defect numbers to 2 nm Al2O3 / 15 nm HfO2.

## 2021 DOS equations and interpretation

The model decomposes bulk DOS into conduction-band acceptor tail, valence-band donor tail, donor Gaussian, and acceptor Gaussian (pp. 4-5, equations 11-15):

```
g_TA(E) = N_TA exp[(E - E_C)/W_TA]
g_TD(E) = N_TD exp[(E_V - E)/W_TD]
g_GD(E) = N_GD exp[-((E - E_GD)/W_GD)^2]
g_GA(E) = N_GA exp[-((E - E_GA)/W_GA)^2]
```

Use a single explicit energy coordinate when translating these equations. Figure 1b (p. 3) uses `E - E_V`, with Eg = 3.05 eV. The donor Gaussian at E_GD = 2.95 eV is therefore centered at E_C - 0.10 eV. **The text states E_GA = 0.30 eV, but the figure draws the acceptor Gaussian near E_V + 2.75 eV, consistent with E_C - 0.30 eV.** Thus the paper mixes an apparent conduction-band-relative acceptor parameter with its common-energy equation notation. Use `acceptor_depth_below_Ec = 0.30 eV` as a clearly identified interpretation, not an unquestioned literal energy above Ev. Figure 6 (p. 12) also places front-interface acceptor levels approximately 0.3 eV below local Ec. The interface Gaussian width is not separately tabulated.

| Population | Paper association | Reported seed / variation | Page |
|---|---|---|---|
| Acceptor tail | Metal-ion s-band / disorder near conduction edge | NTA = 5.0e19 cm^-3 eV^-1; WTA = 0.01 eV | 5 |
| Donor tail | Oxygen p-band / deep valence tail | NTD = 8.0e20 cm^-3 eV^-1; WTD = 0.12 eV | 5 |
| Bulk donor Gaussian | Oxygen vacancy VO | NGD = 5.0e16 cm^-3 eV^-1 initially; WGD = 0.05 eV; center Ev + 2.95 eV | 5 |
| Bulk acceptor Gaussian | Combined OH, Oi, metal vacancy contribution, not separately resolved | NGA = 1.0e16 cm^-3 eV^-1 initially; WGA = 0.04 eV; stated EGA = 0.30 eV with reference ambiguity above | 5 |
| Front-interface acceptor Gaussian | Possible oxygen interstitial Oi / electron trapping | NGA = 0, 8.0e12, 8.0e13, 1.0e14 cm^-2 eV^-1 for 3, 7, 10, 13% O2 | 9 |
| Back-interface traps | Assumed absent because SU-8 passivation was present | Zero by the authors' assumption; not experimentally proved universally | 9 |

**NGA and NGD are peak DOS amplitudes**, despite the prose sometimes calling them total densities. For the printed Gaussian convention, `W = sqrt(2)*sigma`; FWHM = `2*sqrt(ln(2))*W`. Full-line integrated population is `N*W*sqrt(pi)`, while the physically used band-gap integral is

```
N_integrated = N*W*sqrt(pi)/2 *
               [erf((Ec-E0)/W) - erf((Ev-E0)/W)]
```

The integral has cm^-3 units for bulk or cm^-2 units for an interface. A bulk distribution averaged into a sheet scales with channel thickness in **cm**; do not copy its numerical amplitude directly into cm^-2 eV^-1 interface settings. Verify the installed ATLAS energy reference and DOS normalization separately before translating any parameters.

The paper identifies VO with donor-like charge: empty donor traps are positive, filled donor traps neutral; increasing VO Gaussian amplitude moved Vth negative (p. 9). Acceptor-like OH/Oi/metal-vacancy states are negative when occupied by electrons and neutral when empty; increasing front-interface acceptor amplitude produced a positive Vth shift and reduced current. These are proposed chemical associations of phenomenological DOS, not a uniquely measured chemical inventory. A Gaussian near Ec is not automatically a deep midgap oxygen defect; the cited donor center is only 0.10 eV below Ec.

## 2021 material, mobility, and fitted oxygen-series values

| Quantity | Reported value | Page / qualification |
|---|---|---|
| IWO band gap / affinity | Eg = 3.05 eV; chi = 4.30 eV | 3; affinity estimated by linear 96/4 composition mixture |
| HfO2 band gap | 5.70 eV | 3 |
| Relative permittivity | IWO 10; HfO2 18 | 4 |
| Electrode work functions | S/D 4.67 eV; gate 4.80 eV | 3; Mo device, not Pd/TiN measurements |
| Initial NC = NV | 2.0e18 cm^-3 | 4; later NC strongly varied as a fitting degree of freedom |
| Richardson coefficients | An = Ap = 41 A cm^-2 K^-2 | 4 |
| Initial Nd | 8e18 cm^-3 at 3% O2 | 3; subsequent fitted value differs |
| Physics | Maxwell-Boltzmann, DD, Poisson, SRH, Bohm quantum potential, S/D Schottky tunneling | 3-4; BQP and tunneling calibration coefficients not supplied here |

Mobility (p. 4, equations 2-3):

```
mu_n = mu_n0 * (n / ncrit)^(gamma / 2)
gamma = gamma0 + Tgamma / TL
ncrit = 1e20 cm^-3; gamma0 = -0.36; Tgamma = 178.4 K; TL = 300 K
```

At 300 K, gamma = 0.2346667 and the concentration exponent is 0.1173333. The authors use experimentally extracted field-effect mobility to guide mu_n0 (p. 6); this does not prove that field-effect mobility equals microscopic transport mobility in the 2026 device. A supported concentration-dependent mobility implementation must actually respond during the solve; bias-indexed changes to a printed material constant are not a substitute.

| O2 ratio | O2 / Ar (sccm) | Vth (V) | muFE (cm2/Vs) | SS (mV/dec) | Nd (cm^-3) | NC (cm^-3) | bulk NGD (cm^-3 eV^-1) | interface NGA (cm^-2 eV^-1) |
|---|---|---|---|---|---|---|---|---|
| 3% | 1 / 29 | 0.287 | 24.0 | 127 | 7.0e18 | 2.0e18 | 5.0e16 | 0 |
| 7% | 2 / 28 | 0.636 | 19.3 | 119 | 1.0e18 | 1.0e18 | 5.3e16 | 8.0e12 |
| 10% | 3 / 27 | 3.065 | 12.0 | 119 | 5.0e15 | 3.0e16 | 5.9e16 | 8.0e13 |
| 13% | 4 / 26 | 4.089 | 5.6 | 143 | 5.0e15 | 8.0e15 | 1.1e17 | 1.0e14 |

Device metrics / gas flows are Table 1, p. 3. Nd is the later controlled value on p. 8; NC and NGD are on p. 9. The paper only gives the bulk NGA range 2.5e16 to 3.7e16 cm^-3 eV^-1 across oxygen ratios (p. 9), not a complete four-value table. Do not invent intermediate values. The very large fitted changes in NC are not independent evidence of a corresponding effective-mass change; NC is not measured directly by Hall concentration. Those parameters and trap amplitudes can compensate each other in a single transfer sweep.

## Published inconsistencies that must not become executable physics

1. **Charge signs:** p. 4 Eq. 4 writes a charge term `+nT - pT`, while describing nT as occupied acceptors and pT as ionized donors. Physical charge under those definitions is `-nT + pT`. Use ATLAS's verified donor/acceptor definitions, not the inconsistent printed signs.
2. **Capture cross section:** p. 4 visibly prints `1 x 10^12 cm2`, not `1 x 10^-12 cm2`. This is physically implausible and likely a missing minus sign; the original cited source would be needed to confirm the intended value. Do not silently call 1e-12 a measured value, and never implement 1e12.
3. **Formation equation:** p. 6 Eq. 16 visibly prints `c = Nsites (-Ef)/kBT`, without an exponential. The usual equilibrium Boltzmann relation would be `c = Nsites exp(-Ef/kBT)`, but **this is a correction, not the printed formula**. No IWO-specific Ef(EF, chemical potential), Nsites, migration barrier, attempt rate, or transition kinetics is provided. The paper maps regions with high quasi-Fermi level to possible Oi formation; it does not derive a quantitative dynamic creation law.
4. **Acceptor energy reference:** see Fig. 1b / text discrepancy above. Peak locations must be expressed relative to a stated band edge and checked in exported DOS.
5. **Trap-charge kinetics:** p. 6 discusses `Oi^0 + 2e -> Oi^(2-)` and negative-U behavior. An ordinary one-electron Gaussian acceptor occupancy is an effective description; it does not explicitly implement a coupled two-electron negative-U defect or metastability. Doubling both density and charge would double count.
6. **Thermal velocity equations:** p. 4 Eq. 10 repeats An and Nc for holes, following Eq. 9, despite separately naming Ap and Nv in the prose. Do not implement this as a validated hole transport law.
7. **XPS interpretation:** p. 6 assigns O 1s components to lattice oxygen, VO, and OH, and pp. 9/15 use them as qualitative relative priors. Peak areas are not absolute electrically active defect densities or separate OH/Oi/metal-vacancy counts. The paper itself combines these species. Its VO-assigned fraction increases with oxygen flow; a blanket rule that more O2 always means fewer VO is inconsistent with its reported series.

## What the 2018 leakage paper supports

The larger-area IGZO samples show substantial gate current and reduced apparent drain conductance; gate current can become comparable to current through the channel (pp. 3-5). Insulator deposition quality and junction area alter leakage. The authors associate the effect with intrinsic defect sites and describe a space-charge-limited-current interpretation based on log-log Ig-Vg slopes greater than 2 (p. 4). They also report the phenomenon in Al2O3 in supplementary figure S7, but that supplementary file was not supplied or read in this subtask.

This motivates recording **signed Id, Is, Ig**, testing Kirchhoff current balance, preserving geometry and active area, and keeping any dielectric leakage mechanism distinct from channel trap charge. It does not provide an oxygen-vacancy activation energy, Gaussian density/width, or tunneling cross section for the 2026 Al2O3/HfO2 stack. Adding dielectric TAT, Poole-Frenkel, SCLC, and tunneling simultaneously from this qualitative evidence would not be a defensible calibration. No measured Ig curve for the 2026 devices has been identified in this subtask.

## Consequences for the model revision

- Start with identifiable families: IWO conduction tail plus donor and acceptor Gaussian candidates, and a separate front-interface Gaussian on the **IWO/Al2O3 interface** of the target stack. Treat the back surface as a separate optional population supported by the target device's actual passivation, not by the 2021 SU-8 assumption.
- Do not duplicate the same electron-trapping population as fixed interface charge, a sheet DOS, and a thin bulk DOS layer. Distinguish net ionized background donors from explicitly modeled donor traps; the same VO population cannot independently supply both fitted donor density and a second full donor DOS.
- Introduce poorly constrained deep states in sensitivity studies, retain them only when supported, and regularize them across thickness. The 2021 paper reports little transfer-curve sensitivity to the valence tail and its bulk deep-acceptor variations (pp. 5, 9); fitting them independently per thickness cannot establish a unique physical mechanism.
- Use four thicknesses jointly to separate bulk and sheet scaling where possible, but single-temperature Id-Vg at one Vd cannot uniquely identify Gaussian amplitude, width, energy, cross sections, mobility, doping, contact barriers, quantum confinement, and leakage. Additional C-V, Hall, signed Ig, output curves, temperature sweeps, or stress transients would be needed for those claims.
- The target DC-sputtering recipe can guide process geometry and parameter priors. Neither reviewed paper supplies an Athena sputtering-to-IWO-DOS constitutive law. A deposited custom layer in a process deck must not be called a predictive simulation of oxygen chemistry or atomic defect formation.

No new simulation, shared source-code change, or shared configuration change was made for this subtask.
