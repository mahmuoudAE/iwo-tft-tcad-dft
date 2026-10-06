# Parameter-extraction protocol: threshold voltage, subthreshold swing, on-state mobility

Written and committed on 2026-10-06, before any measured-versus-TCAD number of this analysis was computed. Purpose:
recalculate the threshold voltage, the subthreshold swing (SS) in a current window common to data and TCAD, and the
mobility as a function of gate voltage between 1 and 3 V, with methods that are valid at the single available drain
bias, identical code for data and simulation, stated uncertainties, and criteria fixed in advance. Any later change
is listed under "Deviations" in `RESULTS.md` with its reason.

Feasibility of the power-law fit (section 3.3) was checked on the measured curves only, before this protocol was
written: the fit converges for all three films over 1.0-3.0 V with log-residual RMS of 0.4-1.9 %. No TCAD curve was
fitted and no comparison was made at that stage.

## 1 Data

| item | value |
|---|---|
| measured | `data/experimental_clean.csv` (target-device workbook), films 2.0 / 6.3 / 13.2 nm, one device per thickness, V<sub>G</sub> = -3...+3 V on a 0.05 V grid, V<sub>D</sub> = 0.7 V, current per um of width |
| excluded | 31.8 nm (no TCAD model; g<sub>m</sub> has several maxima, report section sec:der-mufe) |
| TCAD | V1 final calibrated runs 0038 (2.0 nm), 0039 x 11.581987/11.41 (6.3 nm), 0040 x 61.604561/60.39 (13.2 nm); currents from `terminal_currents.csv` on the native solver grid (0.05 V for -1...1.5 V, 0.1 V above); 300 K; ideal contacts; no gate current. The rescaling is exact because I<sub>D</sub> is proportional to the uniform mobility. |
| constants | C<sub>ox</sub> = 8.9554e-7 F/cm<sup>2</sup> (15 nm HfO<sub>2</sub>, e<sub>r</sub> 19.57, + 2 nm Al<sub>2</sub>O<sub>3</sub>, e<sub>r</sub> 9.0; geometric), L = 20 um, W = 290 um, V<sub>D</sub> = 0.7 V, T = 300 K, S<sub>th</sub> = (kT/q) ln 10 = 59.52 mV/dec |

## 2 What the TCAD was fitted to (agreement on these is not validation)

- Fitted per film: the band mobility to I<sub>on</sub> = I<sub>D</sub>(3 V) (exact); the fixed charge Q<sub>f</sub> to V<sub>th,cc</sub> (one shared value for 2 and 13.2 nm, a film-specific value for 6.3 nm in run 0039).
- Fitted on the 2 nm film only: tail width W<sub>TA</sub> and tail density N<sub>t</sub>(2 nm), on the 2 nm subthreshold region. N<sub>t</sub> at 6.3 and 13.2 nm follows a thickness law whose exponent comes from the target paper's trap-density ratio.
- Not fitted: the above-threshold shape (g<sub>m</sub>(V<sub>G</sub>), mu<sub>FE</sub>(V<sub>G</sub>), power-law exponent gamma) at every thickness; SS at 6.3 and 13.2 nm (constrained only through the N<sub>t</sub> law).

## 3 Definitions

### 3.1 Threshold voltage

- **T1, primary (model-free).** Constant current: V<sub>th,cc</sub> = V<sub>G</sub> at I<sub>D</sub> = 1e-9 A/um (I<sub>D</sub>L/W = 20 nA), log-linear interpolation between the two grid points that bracket the level. The crossing used is the last upward crossing below +3 V (the one connected to the on-state); the number of crossings is reported. Also reported at 5e-10 A/um (I<sub>D</sub>L/W = 10 nA, the common thin-film-transistor criterion).
- **T2, model-based.** V<sub>T</sub> of the power-law gradual-channel fit of section 3.3.
- **T3, conventional (for comparison with the literature only).** Linear extrapolation in the linear regime with the drain-bias correction: V<sub>th,ELR</sub> = V<sub>G</sub>\* - I<sub>D</sub>(V<sub>G</sub>\*)/g<sub>m,max</sub> - V<sub>D</sub>/2, V<sub>G</sub>\* = argmax g<sub>m</sub>. Flagged "sweep-limited" when g<sub>m,max</sub> - g<sub>m</sub>(3 V) <= 2 sigma<sub>gm</sub> (no maximum resolved inside the sweep); flagged "not linear regime" when V<sub>G</sub>\* - V<sub>th,ELR</sub> < V<sub>D</sub>.

### 3.2 Subthreshold swing

- **S1, primary.** SS = [V<sub>G</sub>(I<sub>hi</sub>) - V<sub>G</sub>(I<sub>lo</sub>)] / log<sub>10</sub>(I<sub>hi</sub>/I<sub>lo</sub>) with I<sub>lo</sub> = 5e-11 and I<sub>hi</sub> = 5e-10 A/um (one decade, proposed by the user). The crossings are computed as in T1.
- **Admissibility of the window, tested per curve.**
  - (i) I<sub>lo</sub> >= 10 x off-floor, where the floor is the median I<sub>D</sub> over V<sub>G</sub> = -2...-0.5 V of the measured device (the floor then contributes at most 10 % at the lower edge).
  - (ii) I<sub>hi</sub> below the T1 level (the window is subthreshold); this holds by construction.
  - (iii) Each level is crossed upward; the number of crossings is reported.
- **When test (i) fails.** The floor-corrected SS, computed on I<sub>D</sub> - floor, is the primary value for the comparison and the uncorrected value is reported next to it. This assumes an additive, gate-independent parallel current; the TCAD contains no such path.
- **Robustness of the comparison.** The difference TCAD - measured is also computed for windows shifted by -0.25 and +0.25 decade ([2.81e-11, 2.81e-10] and [8.89e-11, 8.89e-10] A/um).
- **S2, local SS.** dV<sub>G</sub>/dlog<sub>10</sub>I<sub>D</sub> by central differences, plotted against I<sub>D</sub> to show where the window lies. It is a figure only, not a reported number.
- **Derived quantity.** Equivalent trap density N<sub>SS</sub> = (SS/S<sub>th</sub> - 1) C<sub>ox</sub>/q (cm<sup>-2</sup> eV<sup>-1</sup>). This assumes the depletion capacitance of the ultrathin film is negligible; the value is an upper bound on the interface-trap density.

### 3.3 Mobility in the on-state, V<sub>G</sub> = 1.0-3.0 V

- **M1, primary (model-free).** mu<sub>FE</sub>(V<sub>G</sub>) = L g<sub>m</sub>(V<sub>G</sub>) / (W C<sub>ox</sub> V<sub>D</sub>), with g<sub>m</sub> from `numpy.gradient` (second-order central differences on each curve's own grid, one-sided at the ends). Reported at V<sub>G</sub> = 1.0, 1.5, 2.0, 2.5 and 3.0 V and as curves.
  - mu<sub>FE</sub> equals the carrier mobility only where V<sub>G</sub> - V<sub>T</sub> >= V<sub>D</sub> and the mobility does not depend on V<sub>G</sub>. Everywhere else it is a normalised transconductance, and it is used only to compare data and TCAD.
- **M2, model-based.** Gradual-channel current with a power-law mobility mu(u) = mu<sub>0</sub>(u / 1 V)<sup>gamma</sup>, where u = V<sub>G</sub> - V<sub>T</sub> - V(x) is the local overdrive:
  - I<sub>D</sub> = (W/L) C<sub>ox</sub> mu<sub>0</sub> [u<sub>s</sub><sup>gamma+2</sup> - max(u<sub>s</sub> - V<sub>D</sub>, 0)<sup>gamma+2</sup>] / (gamma + 2), with u<sub>s</sub> = V<sub>G</sub> - V<sub>T</sub>. This covers both the linear and the saturation regime at V<sub>D</sub> = 0.7 V; gamma = 0 gives the square law.
  - Fit: nonlinear least squares on log<sub>10</sub>I<sub>D</sub> over V<sub>G</sub> = 1.0-3.0 V, multi-start, free parameters V<sub>T</sub>, mu<sub>0</sub> and gamma, with the bound V<sub>T</sub> <= lower fit limit - 0.02 V. A solution at that bound is flagged.
  - Channel mobility: mu<sub>ch</sub>(V<sub>G</sub>) = mu<sub>0</sub>(V<sub>G</sub> - V<sub>T</sub>)<sup>gamma</sup>. The linear regime is V<sub>G</sub> >= V<sub>T</sub> + V<sub>D</sub>.
  - Statistical uncertainty: from the Jacobian, scaled by the residual variance.
  - Systematic uncertainty: refits over 1.25-3.0, 1.5-3.0 and 1.0-2.5 V; the largest deviation is quoted. Total = quadrature sum of the two.
  - Adequacy: the log-residual RMS is reported, and an RMS above 0.01 decade (2.3 %) is flagged.
- **TCAD reference.** The solver's free-electron mobility mu<sub>n</sub> = mu<sub>band</sub> R(t) is constant; it is read from the run's mobility probe and multiplied by the rescaling factor.

### 3.4 Uncertainties

- **Measurement noise sigma<sub>log</sub>.** Standard deviation of the residuals of a quadratic fit of log<sub>10</sub>I<sub>D</sub> against V<sub>G</sub> over the 9 grid points centred on each crossing.
- **V<sub>th,cc</sub> and the crossings.** sigma<sub>V</sub> = sigma<sub>log</sub> x local dV<sub>G</sub>/dlog<sub>10</sub>I<sub>D</sub>, combined in quadrature with the interpolation-method difference |log-linear - monotone cubic (PCHIP)|.
- **SS.** Quadrature sum of the two crossing uncertainties divided by the window width in decades, combined in quadrature with the interpolation-method difference.
- **g<sub>m</sub> and mu<sub>FE</sub> (measured).** sigma<sub>gm</sub> = standard deviation of (g<sub>m</sub> - Savitzky-Golay g<sub>m</sub>; window 7, order 2) over 1-3 V, applied per point.
- **TCAD numerical budget** (report table tab:d2-uncertainty): V<sub>th</sub> +-1.5 mV, SS +-1 mV/dec, g<sub>m</sub> +-0.7 %.
- **Not included in data-versus-TCAD differences, stated separately:**
  - C<sub>ox</sub> (dielectric constants);
  - C<sub>eff</sub>/C<sub>ox</sub> = 0.87 (charge centroid and degenerate density of states; mobilities scale with C<sub>ox</sub>/C<sub>eff</sub>);
  - contact resistance (not identifiable from one channel length);
  - device-to-device spread (one device per thickness, so none can be quoted).

### 3.5 Comparison rule

- Difference Delta = TCAD - measured, with sigma<sub>Delta</sub> = sqrt(sigma<sub>meas</sub><sup>2</sup> + sigma<sub>TCAD</sub><sup>2</sup>).
- Verdict: "consistent" if \|Delta\| <= 2 sigma<sub>Delta</sub>, otherwise "differs".
- Each Delta is labelled fitted, constrained or not fitted according to section 2.

## 4 Outputs

`extraction.py` (methods), `run_extraction.py` (driver), `results.json`, `results_table.csv`, `mobility_vs_vg.csv`,
`figures/`, `RESULTS.md` (values, comparison, deviations) and `METHODS_TEXT.md` (methods paragraph with references).
