# Measurement constraints for a new IWO TCAD model

Prepared 2026-09-12. This is numerical analysis of the original measurements, not a TCAD simulation, a replacement transfer curve, or an extraction of a unique microscopic parameter set. No simulator was launched and no source measurement was changed. Reproducible numerical results and source hashes are in `results/rebuild_20260912/measurement_constraints.json`.

**Main conclusion:** the 2 and 6.3 nm devices require substantial continuing current activation over 1–3 V, the 13.2 nm device approaches a nearly linear branch, and the 31.8 nm device approaches a plateau. Merely assigning four mobilities and four flatband shifts to one trap-free, constant-mobility transfer law will not reproduce these shapes. A new model should test charge activation and density-dependent transport separately, then test a distinct limiting mechanism for the thick device. The four measured drain-current sweeps do not uniquely identify which of those mechanisms dominates.

## Data and definitions

All **484 gate/current pairs** in the four CSV files were checked against the original workbook's numerical cells and match exactly. The workbook hash matches `data/provenance.json`: `ce97eccd975207650c5404eff69fa651954cee51d738a60b9811541847d47d12`.

| Channel | Original workbook location, Sheet1 | CSV |
|---|---|---|
| 2.0 nm | G2:H122 | `data/iwo_2p0nm.csv` |
| 6.3 nm | A2:B122 | `data/iwo_6p3nm.csv` |
| 13.2 nm | C2:D122 | `data/iwo_13p2nm.csv` |
| 31.8 nm | E2:F122 | `data/iwo_31p8nm.csv` |

Each sweep contains 121 points from VG=−3 to +3 V at 0.05 V spacing. All stored currents are positive. A/um, VD=0.7 V and W/L=290/20 um come from the user's structure/transfer screenshot; the workbook headings themselves do not establish the current unit. The data do not include simultaneous signed IS/IG, instrument range/uncertainty, sweep dwell times, or independent temperature/contact measurements.

For the numerical diagnostics below, the specified 15 nm HfO2 / 2 nm Al2O3 stack gives Cox=8.95537e−7 F/cm2 using epsilon(HfO2)=19.57 from the target supplement and the stated provisional epsilon(Al2O3)=9. Thus Cox/q=5.58950e12 cm−2/V. These are device assumptions used to interpret slopes; they are not new measured capacitance data.

The low-current comparison band is −2 to −0.5 V, matching the previous report. It is not an instrument detection limit. In particular, its upper end already includes some 31.8 nm turn-on. Constant-current crossings use log-linear interpolation only between adjacent measured points and retain their two source rows in JSON; no extrapolation is used. These descriptive crossings are not simulator outputs or a declaration of electrostatic Vth.

## Current scales and low-bias behavior

| Thickness (nm) | ID at +3 V (A/um) | Median ID, −2..−0.5 V (A/um) | I3 / low-band median | Minimum stored ID (A/um), VG |
|---:|---:|---:|---:|---|
| 2.0 | 5.08966e−7 | 4.60552e−15 | 1.10512e8 | 1.07931e−16 at −2.95 V |
| 6.3 | 4.03448e−7 | 1.52759e−13 | 2.64108e6 | 5.86207e−15 at −0.05 V |
| 13.2 | 3.07069e−6 | 6.59655e−12 | 4.65499e5 | 6.42069e−12 at −0.50 V |
| 31.8 | 3.59034e−6 | 2.74931e−7 | 13.0591 | 2.64862e−7 at −1.55 V |

The low-band median rises by factors **33.17, 1,432, and 5.97e7** relative to 2 nm. A thickness factor of 3.15, 6.6, or 15.9 alone cannot produce this variation while keeping the same free-carrier density and mobility. Thickness-dependent depletion, carrier statistics, defect charge or another separately evidenced conduction path is required. This observation does not identify a microscopic oxygen-vacancy concentration.

- **2 nm:** the negative-bias current is not a perfectly constant plateau: ID increases from 1.87e−16 at −3 V to 5.03e−15 A/um at −0.5 V, with isolated dips. The 31-point low-band standard deviation divided by mean is 13.8%. These may include real bias dependence and measurement effects; they cannot be assigned to a specific leakage law from this dataset.
- **6.3 nm:** low-band relative scatter is 26.1%, and an isolated −0.05 V dip is approximately 26 times below the low-band median. A crossing near that dip is not a useful turn-on threshold. An equilibrium smooth TCAD curve should not be forced through every such excursion by extra defects.
- **13.2 nm:** the negative-bias plateau is much more stable: 2.12% relative scatter in the same band and only 6.42–6.80e−12 A/um range. A successful active-branch fit that tends to exactly zero still fails to explain this measured plateau. The absent signed gate/source currents prevent assigning it uniquely to channel generation, gate leakage, contact injection, or instrument offset.
- **31.8 nm:** the device remains conducting throughout the gate range. ID first falls from 3.00e−7 at −3 V to 2.65e−7 near −1.55 V, then rises. There is no measured multi-decade subthreshold branch. Applying the thin-device subthreshold threshold/floor logic to this curve is inappropriate.

Under the **conditional** uniform Ohmic-film identity `ID/W = q*n*mu*t/L * VD`, the 31.8 nm minimum implies `n*mu=1.4853e19 cm^-1 V^-1 s^-1`. If its actual mobility were 10–50 cm2/Vs, that corresponds to roughly 1.49e18–2.97e17 cm−3. This is an illustrative conductance constraint, not a Hall density: spatial accumulation/depletion and contacts can invalidate the uniform-film assumption. Its total device resistance at VG=3 V is 672 ohm; any proposed series resistance must be compatible with the measured total resistance, not added arbitrarily on top.

## Turn-on and subthreshold shape

| ID criterion (A/um) | 2 nm VG (V) | 6.3 nm VG (V) | 13.2 nm VG (V) | 31.8 nm VG (V) |
|---:|---:|---:|---:|---:|
| 1e−10 | 0.4670 | 0.4340 | −0.0391 | No crossing; always higher |
| 1e−9 | 0.6618 | 0.6440 | 0.0825 | No crossing; always higher |
| 1e−8 | 1.0068 | 1.0248 | 0.2810 | No crossing; always higher |
| 1e−7 | 1.7125 | 1.8682 | 0.6539 | No crossing; always higher |
| 1e−6 | Not reached | Not reached | 1.5857 | −0.2599 |

The 6.3 nm curve crosses 1e−10 A/um **33 mV earlier** than the 2 nm curve, but crosses 1e−7 **156 mV later** and reaches only 79.3% of its +3 V current. A fixed horizontal shift alone cannot align them. The 13.2 nm curve turns on substantially earlier and has about six times the +3 V current of 2 nm.

| Descriptive swing interval | 2 nm (mV/dec) | 6.3 nm (mV/dec) | 13.2 nm (mV/dec) |
|---|---:|---:|---:|
| ID=1e−12 to 1e−10 A/um | 102.9 | 108.3 | Below measured plateau at lower endpoint; do not use |
| ID=1e−10 to 1e−9 A/um | 194.8 | 210.0 | 121.6 |
| ID=1e−10 to 1e−8 A/um | 269.9 | 295.4 | 160.0 |

The changing swing is a measured feature. A single exponential with one constant SS cannot describe the whole turn-on region. The source reports near-thermal switching for ultrathin films, but a best short-range SS must not be used as the slope of the full several-decade transition. A 0.2 V centered secant with both endpoints above five times the low-band median has minimum swings 84.5, 114.7 and 130.8 mV/dec for 2, 6.3 and 13.2 nm; these values depend on window width and the stated weighting rule and are not uncertainty-qualified parameter extractions.

Tail filling and a localized shallow Gaussian can each change differential gate-to-free-charge coupling. A native interface Gaussian changes the sheet charge and can also stretch turn-on. One-temperature ID–VG alone does not identify how much of that response comes from bulk versus interface DOS. Plotting a positive stored current on a log scale does not supply terminal-current polarity or prove a conduction mechanism.

## High-bias slopes: a decisive shape constraint

The table uses direct endpoint differences over 0.5 V intervals. The apparent field-effect mobility is `mu_FE=L_um/(Cox*VD) * d(ID/W_um)/dVG`. It is a convenient slope scale; it is **not** measured microscopic band mobility, and its linear-region interpretation fails when transport is contact-limited or the channel is not uniformly in that regime.

| Thickness (nm) | gm, 1..1.5 V (A/um/V) | gm, 2.5..3 V (A/um/V) | Late / early gm | Apparent mu_FE, early to late (cm2/Vs) |
|---:|---:|---:|---:|---:|
| 2.0 | 1.00814e−7 | 3.65374e−7 | 3.624 | 3.22 to 11.66 |
| 6.3 | 7.73311e−8 | 3.21310e−7 | 4.155 | 2.47 to 10.25 |
| 13.2 | 1.11531e−6 | 1.53518e−6 | 1.376 | 35.58 to 48.98 |
| 31.8 | 1.19586e−6 | 1.91720e−7 | 0.160 | 38.15 to 6.12 |

For 2/6.3 nm, current continues to accelerate well above its first detectable rise. A small trap capacity which is already filled cannot continue to explain that acceleration by trap filling alone. Either appreciable gate charge is still being activated into mobile carriers, mobility increases with density, or a bias-dependent contact/injection process changes the effective transport. Constant band mobility plus a sufficiently substantial, changing DOS **can** produce increasing apparent mobility; the measured gm trend does not by itself disprove constant band mobility.

The 31.8 nm curve has the opposite late trend. Its +3 V current is only 17% larger than the 13.2 nm value, but its late gm is only 12.5% as large. A simple increasing `mu(n)` power law with linearly increasing free charge does not generate this plateau. Candidates include field-dependent mobility reduction, series/contact resistance, a distinct partially depleted conducting body coupled to the gate, or a different DOS response. A constant μ0 rescale does not change curvature. Distinguish the hypotheses using solved free charge, local mobility, contact potential drops and terminal currents instead of hiding the difference in arbitrary threshold shifts.

The 31.8 nm branch also has a shoulder: secant gm is 1.442e−6 A/um/V over −0.5..0 V, 0.600e−6 over 0..0.3 V, then 1.331e−6 over 0.5..1 V. This is not proof of two Gaussian defect species. It is a useful held-out feature for deciding whether one simple DOS family and one transport law explain the data.

## Conditional current powers and density-dependent mobility

To quantify continuing thin-film activation, define a descriptive secant power between measured endpoints:

```text
p = ln(I2/I1) / ln[(VG2-Vturn)/(VG1-Vturn)]
```

Vturn is a chosen switching reference, not an electrostatic threshold extracted from TCAD. The hypotheses 0.1/0.2/0.3 V bracket the thin-film switching rise; for 13.2 nm use −0.2/−0.1/0 V. The JSON retains every interval and every choice.

| Channel | Assumed Vturn values (V) | p over 1..1.5 V | p over 2.5..3 V |
|---|---|---:|---:|
| 2 nm | 0.1 to 0.3 | 4.13 to 3.39 | 2.35 to 2.17 |
| 6.3 nm | 0.1 to 0.3 | 3.77 to 3.09 | 2.68 to 2.48 |
| 13.2 nm | −0.2 to 0 | 2.83 to 2.43 | 1.69 to 1.58 |

Only if (i) free sheet density is proportional to overdrive, (ii) contacts are negligible, and (iii) the device is in the linear transport regime, does `mu proportional to n^s` give approximately `s=p−1`. At VD=0.7 V a mean-channel overdrive `VG−Vturn−VD/2` is the more appropriate simple charge coordinate. Repeating the endpoint calculation on that coordinate gives late-interval conditional s values **0.86–1.04 for 2 nm, 1.12–1.33 for 6.3 nm, and 0.38–0.49 for 13.2 nm**. These are substantially larger than the earlier 2021-derived 300 K density exponent of about 0.117 used in the old trial law. They show why a weak positive density power plus very small trap capacity is unlikely to supply all observed thin-film curvature under that charge interpretation.

This is not evidence that ATLAS should immediately use s=1. A threshold inferred from the late linear secant is approximately 1.26 V for 2 nm and 1.39 V for 6.3 nm, very different from the switching-reference values. Choosing such a high electrostatic threshold lowers the inferred power strongly. But then the model must physically explain the substantial delay between initial switching and the strong-current branch through charge, potential or injection behavior. The power is degenerate with that explanation. The assumption that n is proportional to overdrive is particularly questionable in the very trap-filling regime being investigated.

For 31.8 nm, reference values −1.5..−0.5 V give a late p only 0.23..0.18; the corresponding mean-channel conditional s is negative, about −0.79..−0.84. A universally positive power-law mobility is therefore not a complete four-thickness model under simple gate-charge control. This does not preclude a positive percolation contribution combined with an independently verified mobility/contact-limiting contribution.

## Trap capacity versus the gate charge: which new hypothesis is worth testing?

The old 2 nm seed has approximately:

| Population | Available sheet count (cm−2) | q*N/Cox scale |
|---|---:|---:|
| Bulk conduction tail: NTA=1e20 cm−3/eV, WTA=0.022 eV | 4.40e11 | 0.0787 V |
| Native Gaussian interface: peak 2e11 cm−2/eV, W=0.12 eV | 4.25e10 | 0.00761 V |
| Bulk Gaussian acceptor: peak 5e16 cm−3/eV, W=0.15 eV | 2.65e9 | 0.000475 V |

These are capacities, not actual ionized charges. Their combined acceptor capacity is approximately 4.85e11 cm−2. A 1 V gate-charge interval corresponds to 5.59e12 cm−2, an order of magnitude larger. Once such small populations are filled, they cannot keep absorbing a substantial fraction of the additional on-state gate charge.

A deliberately conditional estimate illustrates the discrepancy. With Vturn=0.2 V, mean-channel VD/2 correction, no separate semiconductor-potential correction, negligible contact resistance and constant band mobility 14 cm2/Vs:

| VG (V) | Assumed total gate-induced sheet population (cm−2) | Free sheet population required by measured current (cm−2) | Difference (cm−2) |
|---:|---:|---:|---:|
| 1 | 2.515e12 | 1.232e11 | 2.392e12 |
| 2 | 8.105e12 | 2.163e12 | 5.942e12 |
| 3 | 1.369e13 | 6.483e12 | 7.211e12 |

The difference is **not an extracted trap density**. Surface potential, depletion, contact drops, nonuniform channel charge, true VFB and nonconstant mobility change it. It does, however, expose the charge budget which a trap-dominated interpretation must demonstrate in the actual solver. Increasing μ0 to 23 or 30 cm2/Vs increases the inferred missing charge under these same assumptions; changing μ0 alone does not remove the ambiguity.

For scale only, obtaining 5e12 cm−2 of capacity in a 2 nm film would require one of the following:

- NTA about **1.14e21 cm−3/eV** at WTA=0.022 eV, if assigned entirely to a uniform exponential tail;
- WTA about **0.25 eV** at NTA=1e20, an order of magnitude broader than the original 22 meV tail;
- a native sheet Gaussian peak about **2.35e13 cm−2/eV** at W=0.12 eV, if assigned entirely to that Gaussian.

The Gaussian number falls inside the broad interface-amplitude range explored in the **different** 2021 IWO oxygen-flow study (8e12–1e14 cm−2/eV). That makes a larger native sheet population a defensible sensitivity hypothesis; it does not make it measured for this IWO/Al2O3 interface. A 0.25 eV conduction tail would substantially alter the energy spectrum and may conflict with the steep onset, so indiscriminate broadening should not be the first adjustment. Increasing peak density while retaining the initial width tests charge capacity more cleanly than simultaneously changing width, center and transport exponent.

**Preferred discrimination:** compare, as separate model classes, (A) adequately resolved increased DOS capacity with constant microscopic mobility and (B) the smaller DOS with a stronger native density-transport response. Save integrated free/trapped sheet charge and actual mobility versus gate for both. A capacity model should absorb and then release/gate-fill the required charge; a mobility model should show the required local mobility evolution without inventing trapped charge. Compare low-current/transition/high-current residuals, not only the +3 V endpoint. An intermediate combination may ultimately be needed, but fitting both freely from the outset would obscure the mechanism and make the parameters nonidentifiable.

The new 2026 IGZO shallow-trap evidence (`docs/combined_revision_20260911/DEFECT_EVIDENCE.md`) supports occupancy-dependent activation and separate tail/Gaussian roles, but not transplanting its Ga–Ga–In peak identities or numerical mobility exponents into IWO. Its effective free/total mobility reduction must not be multiplied a second time into ATLAS drift current when native traps already control the free density.

## Rebuild decisions and acceptance evidence

| Model decision | What the measurements can test | What would remain unproven |
|---|---|---|
| Start with classical transport and the measured stack | Correct sign, normalization, expected smooth turn-on and width behavior | Atomistic sputter chemistry, exact band offsets and contact barrier |
| Add one conduction tail with a charge-budget check | Thin-film continuing activation; thickness scaling of occupied/free populations | Unique microscopic DOS from ID–VG alone |
| Add one native interface Gaussian only as a distinct population | Differential turn-on stretching and sheet-versus-volume thickness trends | Unique chemical identity, interface capture cross sections |
| Compare native density mobility against constant band mobility | Whether measured gm growth is reproduced by actual mobility rather than an undocumented gain | A unique exponent without independent charge/Hall/C–V data |
| Add a thick-device limiting mechanism only when needed | The 31.8 nm shoulder and plateau while preserving the three thinner branches | Distinguishing contact resistance, field scattering and body-channel partition from one VD alone |
| Model low-current leakage separately only with evidence | Plateau level, gate dependence, signed KCL, reproducibility above numerical resolution | Assigning channel/gate/contact/instrument origin without IG/IS and instrument data |
| Keep deep-state kinetics, NBIS, HZO polarization and arbitrary extra defect species inactive | Avoids fitting mechanisms not excited/identified by this measurement | Future stress/light behavior |

A TCAD zero below numerical resolution is not a fit to a positive measured plateau. Conversely, injecting a positive offset to imitate that plateau is not a simulator prediction. Numerical resolution must be diagnosed first, then any remaining missing leakage stated as a model limitation. Calibration scoring should report signed linear residuals for every original point, log residuals with explicit zero/negative handling, and separate low-current and active-branch metrics. No undocumented denominator or added floor should make an unavailable low-current logarithm appear valid.

The four curves support competing, physically bounded models rather than one uniquely identifiable parameter inventory. A robust stopping claim needs real mesh/DOS/width and terminal-current checks, then acceptable residuals across the measured shapes above. Repeated reseeding of the old low-capacity DOS cannot establish that result by itself.
