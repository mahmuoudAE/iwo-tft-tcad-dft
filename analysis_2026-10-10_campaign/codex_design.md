## Q1. Off-state floor mechanisms

**My leading hypothesis is an ungated or weakly gated conduction path, with an instrumental contribution at 2 nm.** Contact-limited leakage remains plausible. Ordinary thermal generation cannot explain the floors. Defective dielectric leakage deserves measurement before exclusion, but its expected gate-voltage dependence conflicts with the 13.2 nm plateau.

I read the required files and checked the CSV: each thickness has 121 points. No files were changed and no simulator was launched.

### Evidence and conventions

The measured floors are **MEASURED**, extracted as medians over \(V_G=-2\ldots-0.5\) V:

\[
f=(4.60552\times10^{-15},\,1.52759\times10^{-13},\,6.59655\times10^{-12})
\quad\mathrm{A/\mu m}.
\]

For **MEASURED** width \(W=290\,\mu\mathrm m\),

\[
I_{\mathrm{floor,total}}=290f
=(1.336\times10^{-12},\,4.430\times10^{-11},\,1.913\times10^{-9})\ \mathrm A.
\]

These values agree with [results.json](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/analysis_2026-10-06_extraction/results.json:13) and the private [current-state record](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/iwo-tft-research-private/01_CURRENT_STATE.md:213).

Two qualifications matter:

- The 6.3 nm floor has substantial scatter, approximately ±45%, despite little systematic gate dependence. The ±3% statement applies to 13.2 nm. See [SYNTHESIS, lines 112–113](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/analysis_2026-09-25/SYNTHESIS.md:112).
- The 2 nm current at \(-3\) V is below its median plateau. I would treat its floor as an instrumental-scale observation, not a precisely established physical leakage current.

Below, ratios always appear in the order **2.0 / 6.3 / 13.2 nm**. Arithmetic results inherit the classification of their inputs; they are not DFT **COMPUTED** parameters.

### Inputs for the leakage estimates

| Parameter | Classification and source |
|---|---|
| \(L=20\,\mu\mathrm m,\ W=290\,\mu\mathrm m;\ d_H=15\) nm, \(d_A=2\) nm | **MEASURED** nominal geometry; [geometry.yaml, lines 5–15](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/config/geometry.yaml:5). Thickness metrology is unknown. |
| \(\epsilon_H=19.57\) | **MEASURED**, Januar et al. 2026 SI Fig. S1, recorded in geometry.yaml. |
| \(\epsilon_A=9,\ T=300\) K | **ASSUMED**, recorded in geometry.yaml and extraction protocol. |
| Channel gate area \(A_g=WL\) | **ASSUMED** electrically active leakage area: \(290\times20=5800\,\mu\mathrm m^2=5.8\times10^{-5}\,\mathrm{cm^2}\). |
| Contact overlap length \(2\,\mu\mathrm m\) | **ASSUMED**; one contact area \(=290\times2=580\,\mu\mathrm m^2=5.8\times10^{-6}\,\mathrm{cm^2}\). Pad overlap is unknown. |
| Dielectric electron barriers | **LITERATURE**, representative high-\(k\) band-alignment ranges: HfO₂ \(1.5\!-\!2.5\) eV; Al₂O₃ \(2\!-\!3.5\) eV. Robertson 2004; Wilk, Wallace & Anthony 2001. These are working envelopes, not measured TiN/IWO injection barriers. |
| Dielectric tunnelling masses | **LITERATURE**, representative transport-model ranges: HfO₂ \(0.1\!-\!0.2m_0\), Al₂O₃ \(0.3\!-\!0.5m_0\); Robertson 2004/high-\(k\) tunnelling literature. Sensitivity is essential. |
| Physical channel gap \(E_g=2.9\) eV | **ASSUMED** conservative estimate for generation; motivated by **LITERATURE** IWO \(3.05\pm0.2\) eV, Fan et al. 2021, recorded in [material model, lines 13–16](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/config/iwo_material_model.yaml:13). Sensitivity: \(2.7\!-\!3.25\) eV. |
| \(N_C=2.4\times10^{18},\ N_V=10^{19}\,\mathrm{cm^{-3}}\) | **ASSUMED** generation-estimate DOS values; similar to the existing deck. |
| PF optical permittivity \(\epsilon_\infty=4\) | **ASSUMED**, sensitivity \(3.5\!-\!5\); do not substitute the static 19.57 automatically. |
| Schottky barrier \(0.5\!-\!1.0\) eV | **ASSUMED** test range, not a measured Pd/IWO barrier. Schottky–Mott estimates are unreliable where pinning occurs. |

The PBE absolute gap must not be used for thermal generation. Also, the slab confinement calculations use a relaxed bulk reference of \(0.8887\) eV, rather than the separate \(1.19\) eV bulk calculation. The relevant slab-minus-bulk arithmetic is explicitly documented in [RESULTS_LOG, lines 110–118](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/qe_workflow/cern_htcondor/results/RESULTS_LOG.md:110).

### Oxide fields

Ignoring semiconductor voltage drop gives a conservative oxide-field estimate:

\[
E_H=\frac{V_{\rm stack}}{d_H+(\epsilon_H/\epsilon_A)d_A},
\qquad E_A=(19.57/9)E_H.
\]

For \(V_{\rm stack}=3\) V:

\[
E_H=\frac{3}{1.5\times10^{-6}+(19.57/9)2\times10^{-7}}
=1.550\times10^6\ \mathrm{V/cm},
\]

\[
E_A=3.371\times10^6\ \mathrm{V/cm}.
\]

The drain overlap can experience \(|V_{GD}|=3.7\) V even though \(|V_G|\le3\) V:

\[
E_H=1.912\ \mathrm{MV/cm},\qquad E_A=4.158\ \mathrm{MV/cm}.
\]

These are electrostatic estimates, not measured local fields.

### Numerical comparison

| Mechanism | Formula and inputs | Estimated current per µm; total current | Ratio to measured floors | Verdict and drain collection |
|---|---|---|---|---|
| **FN, representative HfO₂ barrier** | \(J=1.54\times10^{-6}E^2/\phi\,\exp[-6.83\times10^7\sqrt{m_r}\phi^{3/2}/E]\). \(\phi=2\) eV, \(m_r=0.2\), \(E=1.912\times10^6\) V/cm gives \(J=6.74\times10^{-14}\,\mathrm{A/cm^2}\). \(I=JA_g\). | \(1.35\times10^{-20}\,\mathrm{A/\mu m}\); \(3.91\times10^{-18}\) A | \(2.9\times10^{-6}/8.8\times10^{-8}/2.0\times10^{-9}\) | Far too small for this barrier. This neglects the additional Al₂O₃ barrier and assigns all gate leakage to the drain, so it is a generous estimate. |
| **FN, optimistic low barrier/mass** | Same formula, \(\phi=1.5\) eV, \(m_r=0.1\). At 3 V: \(J=1.90\times10^{-5}\); at 3.7 V: \(3.66\times10^{-3}\,\mathrm{A/cm^2}\). | At 3 V: \(3.80\times10^{-12}\); \(1.10\times10^{-9}\) A. At 3.7 V: \(7.31\times10^{-10}\); \(2.12\times10^{-7}\) A. | At 3 V: \(824/24.8/0.575\). At 3.7 V: \(1.59\times10^5/4.79\times10^3/111\). | Magnitude alone cannot exclude every barrier choice. These single-layer estimates are not predictions for the bilayer. Strong voltage dependence conflicts with a flat plateau. |
| **Direct tunnelling through intact bilayer, low-field end of plateau** | WKB \(J=J_0e^{-S}\), \(S=\sum_i6.83\times10^7\sqrt{m_i}[\phi_i^{3/2}-(\phi_i-E_id_i)_+^{3/2}]/E_i\). **ASSUMED** \(J_0=10^9\,\mathrm{A/cm^2}\); \(\phi_H=2,\phi_A=2.8\) eV, \(m_H=0.2,m_A=0.35\); \(V_{\rm stack}=1.2\) V. \(E_H=0.620,\ E_A=1.349\) MV/cm gives \(S=104.6,\ J=3.74\times10^{-37}\). | \(7.48\times10^{-44}\); \(2.17\times10^{-41}\) A | \(1.6\times10^{-29}/4.9\times10^{-31}/1.1\times10^{-32}\) | Intact-barrier direct tunnelling cannot sustain the plateau at this field. At higher field the barrier becomes triangular and the FN estimate is more appropriate. |
| **PF / defect-assisted gate leakage** | \(J=J_0\exp[-(E_t-\Delta_{\rm PF})/kT]\), \(\Delta_{\rm PF}=\sqrt{qE/(\pi\epsilon_0\epsilon_\infty)}\). **ASSUMED** \(J_0=10^{-3}\,\mathrm{A/cm^2}\), \(E_t=0.6\!-\!1.0\) eV, \(\epsilon_\infty=4\). At \(E_H=1.912\) MV/cm, \(\Delta=0.525\) eV. Thus \(J=10^{-3}e^{-(0.6-0.525)/0.02585}=5.5\times10^{-5}\), or \(1.0\times10^{-11}\) for \(E_t=1\) eV. | Approximately \(1.1\times10^{-11}\) to \(2.1\times10^{-18}\); \(3.2\times10^{-9}\) to \(6.1\times10^{-16}\) A | Approximately \(2400/72/1.7\), down to \(4.6\times10^{-4}/1.4\times10^{-5}/3.2\times10^{-7}\) | Possible magnitude, unidentifiable without dielectric trap information. PF is thermally assisted emission, not a complete multilayer TAT model. Drain receives an unknown fraction. |
| **Midgap SRH generation, deliberately extreme upper estimate** | \(n_i=\sqrt{N_CN_V}e^{-E_g/(2kT)}=\sqrt{2.4\times10^{37}}e^{-2.9/0.051704}=2.14\times10^{-6}\,\mathrm{cm^{-3}}\). Fully depleted volume \(A_gt=(1.16,3.65,7.66)\times10^{-11}\,\mathrm{cm^3}\). **ASSUMED** \(\tau_n=\tau_p=10^{-12}\) s. \(I=q n_i A_gt/(2\tau)\). | \((6.87\times10^{-27},2.16\times10^{-26},4.53\times10^{-26})\); \((1.99,6.27,13.1)\times10^{-24}\) A | \(1.49\times10^{-12}/1.42\times10^{-13}/6.87\times10^{-15}\) | Excluded as the floor source. Assumes every generated electron reaches the drain. |
| **Ungated IWO strip** | \(I/\mu\mathrm m=V_Dg_\square k\). **ASSUMED** \(k=(w_p/L_p)/W=10^{-4}\,\mu\mathrm m^{-1}\). Required \(g_\square=f/(0.7\times10^{-4})=(6.58\times10^{-11},2.18\times10^{-9},9.42\times10^{-8})\) S/□. | Exactly \(f\); total \(290f\) | \(1/1/1\) by construction | Required conductances are **FITTED** to the three floors, not validated. Drain sees the full source-to-drain parallel current. |
| **Pd/IWO thermionic reverse leakage** | **LITERATURE** thermionic-emission formula, Sze & Ng 2007: \(I=A_c A^{**}T^2e^{-\phi_B/kT}\). **ASSUMED** \(m_r=0.206\), so \(A^{**}=120m_r=24.7\,\mathrm{A\,cm^{-2}K^{-2}}\); \(A_c=5.8\times10^{-6}\,\mathrm{cm^2}\). At \(\phi_B=0.7\) eV: \(I=5.8\times10^{-6}\times24.7\times300^2e^{-0.7/0.02585}\). | \(7.74\times10^{-14}\); \(2.24\times10^{-11}\) A. Barrier 0.5–1.0 eV gives \(1.77\times10^{-10}\) to \(7.06\times10^{-19}\,\mathrm{A/\mu m}\). | At 0.7 eV: \(16.8/0.506/0.0117\) | Plausible magnitude. Requires a conducting connection to the opposite contact; injection into an insulating, depleted channel alone cannot maintain this current. |
| **Contact-to-contact substrate/dielectric/surface shunt** | \(R=V_D/(290f)=0.7/(290f)\). | Required \(R=(5.24\times10^{11},1.58\times10^{10},3.66\times10^8)\,\Omega\); currents \(f,290f\). | \(1/1/1\) by construction | Resistances are **FITTED** requirements. Plausible contamination/edge shunts; drain sees the entire shunt current. Continuous TiN screens the support, so a substrate explanation needs a specified route. |
| **Instrument offset / settling current** | **ASSUMED** total offset \(10^{-12}\) A gives \(10^{-12}/290=3.45\times10^{-15}\,\mathrm{A/\mu m}\). For capacitive settling, \(I=C\,dV/dt\); **ASSUMED** \(C=1\) pF and \(dV/dt=1\) V/s also gives \(10^{-12}\) A. | \(3.45\times10^{-15}\); \(10^{-12}\) A | \(0.75/0.0226/0.00052\) | Plausible at 2 nm. A common pA offset does not explain the 13.2 nm nA floor. |

The WKB calculation uses a deliberately favorable independent barrier drop in each layer; it is an estimate, not a solved TiN/bilayer/IWO band diagram. Unknown injection offsets are a material limitation.

### What the estimates imply

**Gate leakage.** For the channel area, the current densities needed if *all* leakage entered the drain are

\[
J_{\rm req}=\frac{290f}{5.8\times10^{-5}}
=(2.30\times10^{-8},\,7.64\times10^{-7},\,3.30\times10^{-5})
\ \mathrm{A/cm^2}.
\]

These are **FITTED** requirements to the floors. A larger gate-to-pad area reduces the required density proportionally. A \(100\times100\,\mu\mathrm m^2\) overlap, **ASSUMED**, has area \(10^{-4}\,\mathrm{cm^2}\), so its current is \(10^{-4}/5.8\times10^{-5}=1.72\) times the table estimate.

For PF emission, changing the stack voltage from 1.2 to 3.7 V changes the estimated lowering from 0.299 to 0.525 eV:

\[
J(3.7)/J(1.2)\approx e^{(0.525-0.299)/0.02585}
=6.3\times10^3,
\]

before any field prefactor. That strongly contradicts a plateau within 3%. Nevertheless, an injection-limited filament, collection bottleneck, or measurement artifact can hide the usual field dependence. **I reject ordinary homogeneous gate leakage as the leading explanation, but do not categorically exclude defective leakage without \(I_G\).**

The existing simulated \(I_G=0\) does not constrain experimental leakage: the deck has insulating oxides and no tunnelling transport. See [device.in, lines 74–101](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/results/runs/run_0040_13p2_recal_dos384_13p2/device.in:74) and [igvg.dat](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/results/runs/run_0040_13p2_recal_dos384_13p2/igvg.dat:1).

**Thermal generation.** The required SRH lifetimes would be

\[
\tau_{\rm req}=\frac{q n_iA_gt}{2I_{\rm floor}}
=(1.49\times10^{-24},\,1.42\times10^{-25},\,6.87\times10^{-27})\ \mathrm s,
\]

which are physically impossible. Reducing the assumed gap to 2.7 eV increases \(n_i\) only by

\[
e^{(2.9-2.7)/(2kT)}=e^{0.2/0.051704}=47.9.
\]

The conclusion remains unchanged. A trap at \(E_C-0.6\) eV is not midgap in a 2.9 eV semiconductor: balanced-capture SRH generation is smaller than the midgap estimate by roughly

\[
1/\cosh[(1.45-0.6)/0.02585]\approx1.1\times10^{-14}.
\]

A thickness-independent lifetime gives \(I\propto t\), not \(t^{3.85}\). Fitting a lifetime law cannot repair the impossible magnitude.

**Ungated paths.** With **ASSUMED** \(L_p=20\,\mu\mathrm m\), the strip geometry above requires

\[
w_p=kWL_p=10^{-4}\times290\times20=0.58\,\mu\mathrm m,
\]

or two edges of \(0.29\,\mu\mathrm m\) each. That is geometrically plausible, although not established.

Using \(g_\square=q n\mu t\), the required products are

\[
n\mu=\frac{f}{0.7kqt}
=(2.05\times10^{15},\,2.16\times10^{16},\,4.46\times10^{17})
\ \mathrm{cm^{-1}V^{-1}s^{-1}}.
\]

At **ASSUMED** \(\mu=10\,\mathrm{cm^2/Vs}\), this means \(n=2.05\times10^{14},\,2.16\times10^{15},\,4.46\times10^{16}\,\mathrm{cm^{-3}}\). A fixed-\(n,\mu\) strip gives only linear thickness scaling. The observed endpoint ratio requires

\[
\frac{(n\mu)_{13.2}}{(n\mu)_2}
=\frac{f_{13.2}/f_2}{13.2/2}
\approx\frac{1432}{6.6}=217.
\]

At fixed mobility, the corresponding Fermi-level change is only

\[
kT\ln217=0.02585\times5.38=0.139\ \mathrm{eV}.
\]

Thus the scaling is plausible through carrier activation or connectivity changes; it does not prove a universal thickness law.

An unmodulated back layer **inside the gate footprint** is less convincing for the thin films. For **ASSUMED** \(N_D=2.5\times10^{17}\,\mathrm{cm^{-3}}\) and **MEASURED** \(\epsilon_s=9.3\),

\[
L_D=\sqrt{\epsilon_skT/(q^2N_D)}
=\sqrt{9.3(8.854\times10^{-14})(0.02585)/(qN_D)}
=7.29\ \mathrm{nm}.
\]

The 2 nm channel should be strongly gate-coupled throughout. At 31.8 nm, screening and a back accumulation layer become much more plausible.

**Contacts.** Inverting the thermionic formula yields **FITTED** effective barriers of approximately

\[
\phi_B=-kT\ln\!\left[
\frac{290f}{A_cA^{**}T^2}\right]
=(0.773,\,0.682,\,0.585)\ \mathrm{eV}.
\]

These show feasibility, not barrier extraction: contact area, Richardson constant, tunnelling and channel resistance are unknown. Image-force lowering also matters conditionally:

\[
\Delta\phi=\sqrt{\frac{qE}{4\pi\epsilon_s}},
\]

giving \(0.039\) eV at **ASSUMED** \(E=10^5\) V/cm, \(\epsilon_s=9.3\); the enhancement is \(e^{0.039/0.02585}=4.5\). Local contact fields must come from the solve.

**Other mechanisms.**

- **Bulk band-to-band tunnelling:** average lateral field \(0.7/(20\times10^{-4})=350\) V/cm. A triangular-barrier exponent is \(6.83\times10^7\sqrt{0.2}(2.9)^{3/2}/350=4.31\times10^5\). Negligible. Drain-edge tunnelling cannot be excluded by the average field; inspect the local field first.
- **Trap-assisted drain tunnelling/hopping:** plausible only with injection and a connected path. The measured currents require \(I/q=(8.34\times10^6,\,2.77\times10^8,\,1.19\times10^{10})\) electrons/s total. This is not an impossible rate for many defects, but no localization length or barrier distribution is available. Releasing initially occupied traps is a transient, not steady generation.
- **Hole conduction:** with **ASSUMED** \(N_V=10^{19}\,\mathrm{cm^{-3}}\) and \(E_F-E_V\ge2\) eV, \(p\le10^{19}e^{-2/0.02585}=2.5\times10^{-15}\,\mathrm{cm^{-3}}\). Even **ASSUMED** \(\mu_p=1\,\mathrm{cm^2/Vs}\) gives \(I/\mu\mathrm m=q p\mu_p tV_D/L\approx1.9\times10^{-38}\) A/µm at 13.2 nm. Ordinary equilibrium hole conduction is excluded; strong inversion would be a different, gate-dependent phenomenon.

### Where each mechanism belongs

| Treatment | Mechanisms |
|---|---|
| **Inside TCAD** | Gated channel conduction, traps and charge; physically represented Schottky contacts; an actual back layer; contact-edge tunnelling only if local-field evidence warrants it. |
| **Outside the channel solve** | Instrument offset; remote ungated strip; pad/substrate shunt outside the simulated geometry. Report its terminal connection explicitly. |
| **Separate dielectric/expanded-domain solve** | Gate-to-drain leakage. An additive drain current without the corresponding gate current violates the intended terminal accounting. |
| **Exclude as floor explanations** | Ordinary SRH thermal generation, intact-bilayer direct tunnelling at the low-field plateau end, bulk lateral BTBT, ordinary hole conduction. |

The first discriminating measurement should be simultaneous \(I_D,I_S,I_G\) versus \(V_D\) at several off-state \(V_G\), with settling time recorded. For an ohmic shunt, \(I(0.7)/I(0.1)=7\). For the paper’s diffusion form,

\[
\frac{1-e^{-0.7/0.02585}}{1-e^{-0.1/0.02585}}
=1.021.
\]

Mesa isolation, contact-area variation, length variation, temperature dependence and open-device instrument checks then separate the remaining candidates.

## Q2. Model selection

| Model | Physical justification and available constraint | Verdict |
|---|---|---|
| SRH recombination/generation | Legitimate background physics. No lifetime information in one steady transfer curve; cannot explain floors. Two-carrier runs are needed to test generation honestly. | **Keep** a fixed **ASSUMED** background; **exclude** fitted lifetime as a floor remedy. |
| Fermi–Dirac statistics | Accumulation can be degenerate. At **ASSUMED** 2 V overdrive, \(n_s=C_{\rm ox}V/q=8.9554\times10^{-7}\times2/q=1.12\times10^{13}\,\mathrm{cm^{-2}}\). Spread over 2 nm, \(n=5.6\times10^{19}\,\mathrm{cm^{-3}}\), well above the continuum \(N_C\). | **Keep**. Test Boltzmann statistics once as an ablation. |
| Lateral field-dependent mobility | Average field only 350 V/cm; for **ASSUMED** \(\mu=50\), drift speed \(=1.75\times10^4\) cm/s. Saturation velocity is not constrained. | **Exclude** from calibration; retain only if contact-edge fields justify a bounded test. |
| Vertical-field mobility degradation | Can matter physically, but measured \(g_m\) generally rises through the sweep. Silicon surface-mobility laws are not oxide-semiconductor evidence. | **Test** only after trap filling; do not fit a silicon degradation law to absorb the 6.3 nm shape. |
| Ohmic contacts | Plausible default for pinned oxide contacts, but unverified for Pd. One length and one drain bias cannot identify contact resistance. | **Keep** as **ASSUMED** baseline. |
| Schottky contacts | Leakage estimate permits them. Turn-on curvature partly constrains injection, but trades off with DOS and mobility. | **Test** a shared **ASSUMED** barrier grid; do not fit three independent barriers. |
| Schottky barrier lowering | Physical when a Schottky contact is present; use local field and measured/assumed permittivity. | **Keep within the Schottky branch**, with an on/off diagnostic. Do not add a free lowering coefficient. |
| Dielectric/drain TAT | Defects are plausible, but no \(I_G\), temperature or \(V_D\) data constrain a TAT parameter set. | **Exclude from global calibration**. Conditional test only after local fields and measurement support. |
| Thickness confinement | Expected at 2 nm; DFT supplies useful external information. Transfer curves cannot uniquely distinguish it from charge/alignment. | **Keep** DFT-anchored band shifts; **test** their transfer to real films. |
| Additional quantum correction | Charge centroid and quasi-2D DOS matter. Adding a confinement correction on top of DFT gap shifts risks counting confinement twice. | **Test separately**, only with a verified implementation; no fitted quantum coefficient. |
| Interface versus bulk traps | Distinct physics, but current data mostly constrain total active trap capacitance. | **Test** surface-only versus bulk-only/shared mixtures; avoid freely fitting both amplitudes and separate widths. |
| Multiple trapping and release | Near-\(E_C\) tails and trap filling explain rising apparent mobility qualitatively. | **Keep** one exponential acceptor tail. |
| Hopping/percolation mobility | Strong candidate for the residual on-state shape, especially 6.3 nm. Needs temperature, charge or structural data for physical identification. | **Test conditionally** with a genuinely supported local-density law. Never emulate it by MOBILITY statements between SOLVEs. |
| Deep Gaussian and donor-tail additions | Existing deep Gaussian affects threshold only weakly; parameters lack independent evidence. | **Exclude from the primary fit**; one bounded charge-state sensitivity is sufficient. |
| Thickness-dependent donor law | Existing \(1+(t/20)^4\) law is not identified; W composition is not activated-donor density. | **Exclude** that law. Hold a shared donor density **ASSUMED**, then profile sensitivity. |
| Bias history/transient traps | Missing sweep history can alter threshold and shape. No reverse/dwell data constrain kinetics. | Document uncertainty; **exclude fitted kinetics** from this static campaign. |
| Remote parallel floor | Supported as a possibility, not established. | Keep separate from channel scoring; label its parameters **FITTED** wherever used. |

The existing degeneracies and 6.3 nm shape failure are documented in [SYNTHESIS, lines 183–207](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/analysis_2026-09-25/SYNTHESIS.md:183). They should govern model complexity, rather than the number of available ATLAS switches.

## Q3. Campaign design

### Primary model: five shared fitted parameters

I propose a deliberately restrictive model: one shared electrostatic offset, one shared trap spectrum, and a smooth mobility suppression with thickness. Its inability to reproduce the films is a useful result.

| Parameter | Classification; range; calibration target |
|---|---|
| Effective alignment offset \(\Delta V_0\) | **FITTED**, \(-0.5\ldots+0.5\) V, to thin-film active transfer curves. Implement through one QF correction with verified sign. Call it an effective offset, not measured interface charge. |
| \(\mu_\infty\) | **FITTED**, \(20\!-\!100\,\mathrm{cm^2/Vs}\), to all three on-state curves. |
| Mobility suppression length \(\ell\) | **FITTED**, \(0\!-\!30\) nm, through \(\mu(t)=\mu_\infty/(1+\ell/t)\), to relative on-state levels. This is an empirical shared law, not a derived scattering mechanism. |
| Integrated surface-tail density \(N_s\) | **FITTED**, \(10^{12}\!-\!10^{13}\,\mathrm{cm^{-2}}\), to admissible subthreshold curves. Primary implementation \(g_s(E)=N_s/W_T\,e^{-(E_C-E)/W_T}\). |
| Tail width \(W_T\) | **FITTED**, \(0.025\!-\!0.060\) eV, to subthreshold slope and turn-on curvature. |

All five are fitted to the same data in global calibration. None is validated by the resulting agreement.

The **ASSUMED** initial candidate is

\[
(\Delta V_0,\mu_\infty,\ell,N_s,W_T)
=(0,\ 60,\ 6,\ 4\times10^{12},\ 0.040),
\]

with units as above. Its mobilities are

\[
60/(1+6/2)=15,\quad
60/(1+6/6.3)=30.7,\quad
60/(1+6/13.2)=41.3\ \mathrm{cm^2/Vs}.
\]

These are starting values, not forecasts.

For QF implementation,

\[
|\Delta Q_f|=C_{\rm ox}|\Delta V_0|/q,
\]

so a 0.5 V range corresponds to

\[
8.9554\times10^{-7}\times0.5/q=2.80\times10^{12}\ \mathrm{cm^{-2}}.
\]

The global monotonic mobility law is intentionally vulnerable to the 6.3 nm anomaly. I would not replace it with a fitted crossover thickness and three branch amplitudes after seeing a failure.

### Fixed physics and bounded assumptions

- **COMPUTED:** \(\Delta E_g=0.335\) eV, \(\Delta E_C=0.281\) eV and in-plane \(m^*\simeq0.206m_0\) near 2 nm; [RESULTS_LOG, lines 36–43 and 93–118](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/qe_workflow/cern_htcondor/results/RESULTS_LOG.md:36).
- **COMPUTED:** crystalline bulk mass \(0.159m_0\), mass increment \(0.047m_0\); same log.
- **ASSUMED:** transfer those crystalline values to nominal 2 nm IWO.
- **ASSUMED:** above 2 nm use an asymptotic \(t^{-2}\) continuation, rather than treating the two-point fractional power law as established:

\[
\Delta E_g(t)=0.335(2/t)^2,\quad
\Delta E_C(t)=0.281(2/t)^2,
\]
\[
m^*(t)/m_0=0.159+0.04715(2/t)^2.
\]

The resulting values are:

| \(t\), nm | \(\Delta E_g\), eV | \(\Delta E_C\), eV | \(m^*/m_0\) |
|---:|---:|---:|---:|
| 2.0 | 0.335 | 0.281 | 0.2062 |
| 6.3 | \(0.335(2/6.3)^2=0.0338\) | \(0.281(2/6.3)^2=0.0283\) | \(0.159+0.04715(2/6.3)^2=0.1638\) |
| 13.2 | 0.00769 | 0.00645 | 0.1601 |
| 31.8 | 0.00133 | 0.00111 | 0.1592 |

**Only the DFT anchors are COMPUTED. The continuation and device applicability are ASSUMED.**

Other fixed inputs:

- \(E_{g,\rm bulk}=3.05\pm0.2\) eV and \(\chi_{\rm bulk}=4.3\pm0.3\) eV: **LITERATURE**, Fan et al. 2021, as recorded in the material configuration.
- \(\epsilon_s=9.3\): **MEASURED**, SI value recorded in the configuration; source C–V files are not bundled.
- TiN work function 4.7 eV: **ASSUMED**. Do not fit it alongside \(\Delta V_0\).
- Shared \(N_D=2.5\times10^{17}\,\mathrm{cm^{-3}}\): **ASSUMED**, sensitivity \(2.5\times10^{16}\!-\!2.5\times10^{18}\).
- Capture cross sections \(10^{-15}\,\mathrm{cm^2}\), background lifetimes \(10^{-6}\) s, \(N_V=10^{19}\,\mathrm{cm^{-3}}\), \(\mu_p=0.01\,\mathrm{cm^2/Vs}\): **ASSUMED**. Do not fit them to steady electron-only curves.
- Primary bulk-tail amplitude, deep Gaussian amplitude and extra interface Gaussian amplitude: **ASSUMED zero**. Trap partition is tested as an alternative model, not layered onto the five-parameter fit.

### How many degrees of freedom are supported?

There are 363 thin-film points, but they are correlated samples of three curves, not 363 independent physical constraints. Each film supplies approximately an onset, a slope/curvature feature and an on-state level/shape.

I would allow **at most five shared fit directions**, and expect only about **three to four well-conditioned combinations**. Exact rank must be checked numerically. The data do not independently support work function, affinity, fixed charge, donor density, interface density, bulk density, mobility, contact resistance and confinement strength.

### Metrics fixed before launches

Use the same extractor for data and simulation, following [PROTOCOL, lines 30–67 and 87–98](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/analysis_2026-10-06_extraction/PROTOCOL.md:30).

1. **Subthreshold log-RMSE:** measured current from \(10f_t\) to \(10^{-9}\,\mathrm{A/\mu m}\), excluding floor subtraction.
2. **On-state log-RMSE:** \(V_G=1\ldots3\) V.
3. **Equal-film objective:**

\[
J=\frac13\sum_t\frac{
\mathrm{RMSE}_{\rm sub,t}^2+\mathrm{RMSE}_{\rm on,t}^2}{2}.
\]

No film gets extra weight because its current is larger or its window has more points.

Also report signed errors in \(V_{\rm th,cc}\), \(I_D(3)\), and \(g_m\) at 1.5, 2 and 3 V. Report SS in the existing fixed absolute window and the existing measured-\(I_{\rm on}\)-normalized window; do not recalculate its normalization from each trial simulation.

**ASSUMED engineering acceptance thresholds**, not measurement confidence intervals:

- per-film active log-RMSE \(\le0.15\) decade;
- \(|\Delta V_{\rm th,cc}|\le0.10\) V;
- on-current error \(\le30\%\);
- normalized-window SS error \(\le20\%\);
- on-state \(g_m\) shape error \(\le20\%\).

For perspective, \(10^{0.15}=1.41\); a 0.15-decade error is already substantial. These thresholds are intentionally distinguishable from the much smaller numerical/extraction errors.

### Staged campaign

Each “run” means one ATLAS process launch, including failed launches. All launches are sequential.

| Stage | Runs; running total | Films | Varied parameters / design | Metric | Stop/go rule |
|---|---:|---|---|---|---|
| Smoke and numerics | **10; 10** | Three thin films | Q4 launch list: shared baseline, mesh/DOS checks, two-carrier and SRH tests, confinement removal, trap removal | Terminal KCL; convergence; \(V_{\rm th}\), SS, active log-RMSE; local fields and charge | Stop if continuity is unreliable or active metrics change by >0.01 decade, >5 mV threshold or >3 mV/dec SS under refinement. Resolve using reserve before physics fitting. |
| Model ablation | **24; 34** | All three thin films: 8 variants ×3 | Relative to shared baseline: Boltzmann; no confinement; bulk-only tail; 50:50 integrated surface/bulk tail at 6.3 nm; Schottky \(\phi_B=0.2,0.5,0.8\) eV; 0.5 eV Schottky without lowering. All variant settings **ASSUMED** | Raw and offset/scale-aligned residual shape; charge, injection and field profiles | Select one primary trap/contact branch. Do not promote a branch solely because it changes current scale or threshold. Reject unstable or physically inconsistent branches. |
| Global calibration | **84; 118** | Three thin films | 18 shared candidates ×3 =54, then 10 adaptive shared candidates ×3 =30. Five fitted parameters and ranges above; logarithmic sampling of \(N_s,\mu_\infty\), bounded space-filling sampling otherwise | Fixed equal-film objective plus every film’s acceptance metrics | After first 54 launches, abort calibration if remaining errors are systematic and no candidate approaches acceptance. No per-film rescue parameters. Stop refinement if improvement is <0.01 decade for three successive candidates. |
| Retrospective leave-one-film-out | **36; 154** | Three folds | Per fold: five shared training candidates ×2 training films =10 launches; two frozen candidate predictions on omitted film =2. Same bounds, no omitted-film fitting | Separate training and omitted-film metrics; best-training candidate is primary, runner-up reports optimizer uncertainty | Any omitted-film acceptance failure falsifies transferability of this model. Do not tune the omitted film or select the better held-out result as primary. |
| Sensitivity / identifiability | **24; 178** | Three thin films | Four paired assumption profiles ×3 films: confinement ×0/×1.5; mass ×0.8/×1.2; shared donor density ×0.1/×10; Al₂O₃ \(\epsilon=7/11\). Values **ASSUMED**, not fitted | Raw sensitivity plus analytically profiled offset/mobility; finite-difference Jacobian from calibration archive | If a parameter changes materially with negligible objective cost, report a nonidentified combination. Do not claim a unique material parameter. |
| Thick-film stress check | **2; 180** | 31.8 nm | Best frozen shared model; same model with **ASSUMED** shared donor density ×10. No fitted thick-film charge, resistance or back sheet | Whole-curve log-RMSE, \(I(-3)\), \(I(3)\), shape; no threshold/SS where crossings do not exist | Document failure if neither reproduces always-on behavior. A donor sensitivity match is conditional explanation, not validation. |
| Conditional reserve | **≤20; ≤200** | As needed | Numerical failures first. Then at most one supported density-mobility implementation test or a targeted geometry/contact check; no broad TAT fit | Same metrics and verified native mobility/terminal outputs | Every launch counts. Stop at 200. Unused reserve remains unused. |

The nominal wall time is

\[
180\times(5\!-\!20)\ \mathrm{min}=15\!-\!60\ \mathrm h,
\]

or \(16.7\!-\!66.7\) h for 200 launches, excluding setup and unusually slow thick-film runs. The 31.8 nm processes receive the documented 1500 s timeout.

The five-parameter search is a bounded screening and refinement campaign, not a guaranteed global optimization. If fits depend strongly on starting point, that uncertainty must accompany the reported result.

### Identifiability and reporting

Use the calibration archive to construct a scaled residual Jacobian. Report singular values and parameter correlations. An **ASSUMED** warning threshold is condition number \(>100\) or absolute correlation \(>0.95\); these trigger reporting of parameter combinations rather than individual values.

Profile out the two near-exact nuisance directions—horizontal alignment and uniform current scaling—when comparing *shape*. Confirm the final deck natively; do not assume exact mobility scaling once Schottky or nonlinear transport models are introduced.

All comparisons are retrospective. The documented V2 test already failed: 0.270 and 0.417 V versus 0.644 V, and the latter variant matched on-current by construction. See [T2_T3_RESULTS, lines 16–34](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/analysis_2026-10-06_V2/T2_T3_RESULTS.md:16).

A reviewer should receive:

- calibration residuals and retrospective omitted-film residuals separately;
- every failed model branch and the original acceptance rules;
- native terminal currents, numerical checks and parameter profiles;
- the 31.8 nm failure;
- prospective, frozen predictions for a new measurement: preferably off-current versus \(V_D\), low-\(V_D\) output curves, temperature dependence and replicate devices.

A retrospective LOO success would demonstrate some transferability within these four already-seen devices. It would not constitute an independent prediction or establish a thickness mechanism.

The 6.3 nm anomaly should be decomposed into alignment and shape residuals. If a film-specific offset repairs only threshold, the shape failure remains. I would request replicates and sweep-history data before attributing it to a material transition.

### Numerical and deck precautions

The local facts override stale defaults in configuration files; see [current state, lines 280–297](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/iwo-tft-research-private/01_CURRENT_STATE.md:280).

- Launch sequentially, from isolated run directories; count failures.
- Use `MAXTRAPS<=10`. This is a numerical convergence setting, not a limit of ten physical DOS levels.
- Start with the established 384/192 DOS quadrature. Test finer quadrature at 2 nm if memory permits.
- Refine 13.2 nm by ×0.7; never ×0.5 on this installation.
- Use `XANDRNORM` and the proven depletion tolerance `CR.TOLER=7.88e-16`; inspect KCL independently. That tolerance cannot establish a physical \(10^{-15}\,\mathrm{A/\mu m}\) floor.
- Use electron-only production solves unless two-carrier diagnostics demonstrate a need. SRH generation tests require two carriers.
- Declare `tmun` explicitly; **ASSUMED** `tmun=0` for the baseline. A phonon exponent must be a separately labeled hypothesis.
- Do not update MOBILITY between SOLVEs.
- `DEFECTS` amplitudes are \(\mathrm{cm^{-3}eV^{-1}}\); sheet DOS uses \(\mathrm{cm^{-2}eV^{-1}}\). For a regularization layer, divide the sheet amplitude by its thickness in cm.
- Preserve integrated trap charge when changing DOS discretization or layer thickness.
- Audit QF location: the inspected final deck applies QF at the IWO/Air boundary, despite descriptions calling it a front-interface charge. See [device.in, line 98](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/results/runs/run_0040_13p2_recal_dos384_13p2/device.in:98). Do not silently relocate it and compare unlike models.
- Use a common 50 mV gate grid, with smaller continuation steps only where needed. Never score solver zeros through an arbitrary logarithmic floor.
- Save current components, trap/free charge, potential, quasi-Fermi levels and contact-edge fields at off, threshold and on-state biases.

## Q4. The single most informative 10 runs

These are the first ten launches of the campaign. Parameters are the shared **ASSUMED** initial candidate defined above; there is no per-film recalibration.

| Launch | Film and change | What it decides; result that changes the plan |
|---:|---|---|
| 1 | 2.0 nm baseline | Establishes thin-film feasibility and tail occupancy. Convergence failure or an unexpected charge profile blocks physics comparisons. |
| 2 | 6.3 nm identical shared baseline | Tests whether the intermediate film remains the strongest mismatch. Separate rigid displacement from late/steep turn-on. |
| 3 | 13.2 nm identical shared baseline | Tests whether a shared surface-tail model generates sufficient thick-film transport. A common shape failure across films suggests a model-form problem. |
| 4 | 13.2 nm baseline, mesh ×0.7 | If active RMSE changes >0.01 decade or threshold >5 mV, adopt refined mesh before fitting. |
| 5 | 2.0 nm baseline, DOS quadrature doubled | If SS changes >3 mV/dec or active RMSE >0.01 decade, resolve quadrature before interpreting trap parameters. Memory failure establishes the practical limit. |
| 6 | 13.2 nm baseline, two carriers | Tests the electron-only assumption and exposes hole/generation components. A material difference requires investigation rather than immediate fitting. |
| 7 | Same as run 6, background SRH disabled while retaining the trap DOS | Isolates the explicit background SRH contribution. A large floor change would contradict the thermal estimate and trigger a numerical/model-definition audit. |
| 8 | 6.3 nm baseline, confinement shifts removed; mass unchanged | Tests the rigid confinement contribution separately from DOS-mass changes. Shape persistence favors a transport/history explanation. |
| 9 | 6.3 nm baseline, exponential tail removed | Tests whether trap filling creates the late/steep shape. Compare shape after diagnostic offset/scale alignment, not raw on-current alone. |
| 10 | 13.2 nm baseline, shared Schottky barrier 0.7 eV with physical lowering | Tests whether contact injection can produce a plateau of the required scale without destroying on-state transport. A plateau match accompanied by severe on-current suppression rejects that contact-only branch. |

If numerical checks fail, repair them before proceeding down this list; repair launches consume the reserve. If the campaign ends after ten runs, the defensible output is a mechanism and model-form diagnosis, not an optimized material model.

## Key disagreements with the current model

1. **I would retire the fitted thickness laws for donors and trap density from the primary model.** They encode limited anchors and inherited extraction assumptions rather than independently established material laws.
2. **I would not fit per-film mobility and QF while claiming a shared physics explanation.** Their success is calibration; the failed 6.3 nm transfer tests remain central evidence.
3. **The DFT gap opening is not identical to the conduction-band shift.** At 2 nm, the log gives \(0.335\) and \(0.281\) eV respectively.
4. **Integrated \(N_t\) is not DOS amplitude \(N_{TA}\).** At 2 nm, \(N_t=2\times10^{19}\,\mathrm{cm^{-3}}\), while \(N_{TA}=N_t/0.040=5\times10^{20}\,\mathrm{cm^{-3}eV^{-1}}\). See [TRAPS, lines 7–10](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/analysis_2026-10-06_traps/TRAPS.md:7).
5. **Flatness disfavors gate leakage but does not exclude every defective leakage path.** Conversely, ordinary thermal generation is excluded quantitatively.
6. **The ungated strip is a useful circuit hypothesis, not solved device physics or independent validation.** Its geometry must be checked.
7. **I would spend substantially less than 200 runs if shared physics fails early.** Additional fit parameters cannot compensate for missing measurements.

## Assumptions I had to make

The principal **ASSUMED** quantities are temperature, dielectric injection barriers within literature envelopes, tunnelling masses used for illustrative endpoints, leakage collection area and fraction, contact overlap, PF prefactor/trap depth, lifetime bounds, activated donor density, static hole/DOS parameters, surface-tail partition, empirical mobility law, and crystalline-DFT applicability to the real films.

The largest unresolved experimental issues are the actual gate/mesa/pad geometry, dielectric order at the channel interface, thickness metrology, sweep timing/history, contact behavior and device variability. Those uncertainties limit mechanism attribution more strongly than the available ATLAS run budget.