# Physics model (V1): one thickness-aware IWO material, classical drift-diffusion

    measured stack + workbook  ->  IWO_material(t, xW ~ 2 at.%)  ->  ATLAS 2-D DD  ->  ID-VG  ->  metrics vs experiment

## Parameter categories (never mixed)

| Cat. | Content | V1 treatment |
|---|---|---|
| A intrinsic | Eg_bulk 3.05 eV, chi_bulk 4.30 eV (LITERATURE_IWO, Fan 2021), m*_bulk 0.208 m0 (MEASURED_RELATED_MATERIAL, Stokey 2021), eps_r 9.30 (MEASURED_TARGET_DEVICE, SI), Nv 1e19 (ASSUMED) | fixed |
| B confinement | dEg_QC(t) = 0.921 t^-1.382 eV (t in nm) from PBE slab-minus-bulk shifts (Lin 2022: +0.33 eV at 1.98 nm, +0.94 eV at 0.95 nm; Si 2021: +0.6 eV at 1.5 nm); dEc = dEg (Ev unchanged, Si 2021); chi(t) = chi_bulk - dEc(t); m*(t) = 0.208 + 0.131 t^-1.412 (Lin 2022 increments); Nc(t) = 2(2 pi m* kT/h^2)^1.5 | fixed (DFT_PURE_IN2O3_PROXY). APPROACH A: no BQP/Schrodinger on top |
| C W-dependence | xW ~ 2 % (definition NOT DETERMINED); enters only as the material identity (Eg/chi priors from an IWO study, smoother interface, lower Nt than In2O3 per Januar) | no explicit law; NOT a donor density |
| D bulk defects | acceptor tail gTA(E) = NTA exp((E-Ec)/WTA); Nt(t) = 2e19 (2/t)^0.75 cm^-3 (FITTED law consistent with Januar's ~4x trend), WTA = 0.040 eV shared (Tt = 464 K); deep acceptor Gaussian 5e16 cm^-3/eV at Ec-0.6 eV (ASSUMED, insensitive); donor tail 0; effective background donors Nd_eff(t) = 2.5e17 (1 + (t/20 nm)^4) cm^-3 (FITTED law; Kim 2024 trend) | 2+1+3 law parameters |
| E interface | acceptor sheet 3e11 cm^-2 eV^-1 Gaussian at Ec-0.3 eV, W 0.12 eV (ASSUMED, shared; literature Dit 6e11 for HfO2/In2O3), regularized into a 0.25 nm layer; Qf single shared value (FITTED, stage 3) | 1 fitted |
| F transport | constant band mobility mu0(t) = mu_band(t) (1 - Dsr/t)^2, Dsr = 2.87 A (LITERATURE_IWO); mu_band per thickness (FITTED); free/trapped partition arises self-consistently from the DOS occupancy (this is Eq. 5 of the paper realised by the solver, not applied as a second factor) | 4 fitted |
| G contacts | TiN work function 4.70 eV (ASSUMED, fixed); Pd S/D ideal Ohmic (ASSUMED; CNL above Ec supports low barriers); 31.8 nm: lumped series resistance (FITTED hypothesis) | fixed (+1 for 31.8) |
| G' 31.8 nm only | donor-like back-surface sheet at the free IWO surface (region 5, 0.25 nm regularization; HYPOTHESIS inherited from the V0 evidence that a depletable bulk alone cannot give the flat always-on baseline) and a device-specific Qf | device-specific, not identifiable separately |
| H numerical | Fermi statistics, SRH background, electrons only, XANDRNORM strict acceptance in depletion, 96/48 DOS levels, 0.25/0.0625 nm vertical mesh, 0.1 V continuation, 0.05 V logged targets | verified in V0 (docs/NUMERICAL_CONVERGENCE.md) |

## Why each ATLAS model is (or is not) enabled

- FERMI: accumulation reaches n ~ 1e20 cm^-3 in a 2 nm film with Nc ~ 3e18 -> degenerate; Boltzmann would overestimate n.
- SRH (tau 1 us): background only; thermal generation is 13-17 decades below the measured off-state (Astra bound), so it cannot fit the floors and is not tuned.
- CARRIERS=1 ELECTRONS: Eg > 3 eV, n-type; hole currents were 1e-38..1e-55 A in two-carrier runs (Claude/Astra). Disabling holes removes a numerically meaningless equation; it is stated, not hidden.
- DEFECTS CONTINUOUS: distributed DOS with the manual's conventions (NTA/NTD intercepts at Ec/Ev in cm^-3/eV; NGA/NGD Gaussian amplitudes in cm^-3/eV; EGA from Ec, EGD from Ev). Interface states are represented as a regularized 0.25 nm layer (sheet peak / 0.25 nm), verified numerically (halving the layer changes Id by 0.009 dec).
- Not enabled (no physical justification from these data): BQP/Schrodinger (confinement already in Eg(t), chi(t), m*(t) - double counting), contact tunnelling, dielectric leakage/TAT/Fowler-Nordheim (no IG data), impact ionization, Auger, field-dependent mobility (the installed CVT/Lombardi models are silicon surface-roughness models; the paper's Ando roll-off theta_r Vov is documented as an approximation gap), bias-indexed MOBILITY updates (ignored by ATLAS 5.28.1.R).

## Expected thickness mechanism (to be tested in ATLAS, not assumed)

chi(2 nm) is 0.35 eV lower than chi(13.2 nm) with the same gate work function -> the 2 nm accumulation onset shifts ~+0.3 V relative to 13.2 nm before any change of Nd, Qf or traps. The measured constant-current thresholds differ by 0.58 V (0.66 V vs 0.08 V); the remaining ~0.25 V is expected from the depletion charge of the thicker film (q Nd t / Cox ~ 0.07 V at 13.2 nm) and the tail-charge difference. The 31.8 nm always-on baseline needs an additional mechanism (V0 evidence: back-surface donor sheet + series resistance); it is tested separately and not imposed on the thin films.

### Tested (real ATLAS, runs 0001-0006; details in docs/EXPERIMENTAL_VS_SIMULATION.md)

- With Qf = 0 the laws alone reproduce the SHAPES of the 2 nm and 13.2 nm curves (SS_min within 4 and 15 mV/dec) but both thresholds are too positive by +0.33 V and +0.29 V. The offsets agree to 40 mV, so the 0.35 eV confinement difference between the two films, together with Nd(t), Nt(t), Nc(t), accounts for the measured 0.58 V threshold difference; the common offset is the unknown absolute alignment (chi_bulk / TiN work function / true Qf), absorbed by ONE shared Qf = +1.73e12 cm^-2 (-0.31 V). Result: active log RMSE 0.056 dec (2 nm) and 0.086 dec (13.2 nm), Ion within -7 % at both before the mobility stage.
- Applied unchanged to 6.3 nm the model reproduces the shape (SS_min 108 vs 115 mV/dec) but not the threshold (-0.29 V). The measured 6.3 nm threshold equals the 2 nm one while every monotonic law places it between 2 and 13.2 nm. This is the model's clearest disagreement with the data; its cause is NOT DETERMINED FROM AVAILABLE DATA and the film receives one documented device-specific flat-band offset.
- Applied to 31.8 nm (laws + series resistance) the on-current at +3 V is within -6 % and the on-state slope is reproduced, but the bulk depletes below Vg ~ -1 V (current falls to 1e-12 A/um at -3 V) whereas the measured device stays at 2.7e-7 A/um: the always-on baseline is not a bulk-donor effect at Nd = 1.8e18. The back-surface donor-sheet hypothesis is tested as a device-specific stage.

## Ioff proportional to t_s n_FB (paper Eq. 4)

Used as a consistency check only: the thin-film measured floors (5e-15 / 1.5e-13 / 6.6e-12 A/um) are not diffusion currents of the modelled channel (native DD gives < 1e-17 A); their thickness trend (x33, x1432) exceeds the t x n_FB expectation for any single n_FB, so they are treated as an unmodelled contribution (docs/LIMITATIONS.md).
