# Input inventory and audit (IWO_PHYSICS_CONSTRAINED_MODEL_V1)

Prepared 2026-09-21 on host DELL (Windows 11, DeckBuild 5.0.10.R / ATLAS 5.28.1.R at C:\sedatools; Quantum ESPRESSO NOT installed: `pw.x` absent in Windows and in WSL Ubuntu-22.04, and apt installation needs an interactive sudo password, so no first-principles run was performed). Every input below was opened and read (text extracted with pypdf; PDF page rendering is unavailable on this machine, so figures were read through their captions and the numbers quoted in the text). Reliability = usable for this model as labelled; "proxy" means pure In2O3 or a different IWO process.

## A. Experimental data (ground truth)

| File | Purpose | Origin | Type | Reliability | Contradictions / open questions |
|---|---|---|---|---|---|
| `IWO-TFT (1).xlsx` (sha256 ce97eccd...d47d12; copied to `data/experimental_raw_preserved_IWO-TFT.xlsx`) | four ID-VG sweeps | user (target device) | experimental | HIGH. Sheet1 rows 2-122: A:B 6.3 nm, C:D 13.2 nm, E:F 31.8 nm, G:H 2 nm; 121 points each, -3..+3 V in 0.05 V, all currents positive, Vg strictly increasing (re-extracted independently, `data/data_summary.json`) | Headers give no units; A/um and VDS = 0.7 V come from the screenshot/PPTX only. Sweep direction, dwell, temperature, instrument floor, signed IG/IS: NOT DETERMINED FROM AVAILABLE DATA. Header for 13.2 nm is the number 13.2, not text |
| `device_and_transfer_curves.png` / `IWO_TFT_2.pptx` | device schematic + curve figure | user | experimental (figure) | HIGH for geometry (W/L 290/20 um, VD 0.7 V, TiN 50 / HfO2 15 / Al2O3 2 / IWO / Pd 70) | on/off annotation is approximate; numerical data take precedence |

## B. Target paper

| File | Purpose | Type | Reliability | Notes |
|---|---|---|---|---|
| Januar et al. 2026, Small Structures 7, e202500807 (two byte-different PDF builds of the same 12-page main text; sha c784149... bundled, 45f26d0... uploaded) | process, stack, analytic framework, DFT trends, Nt/Tt/Delta_sr | experimental + compact model + PBE DFT | HIGH for stack/process; MEDIUM for extracted metrics (compact-model derived) | "IWO (~2% W)": composition definition NOT DETERMINED. eps ~9 (SI: IWO 9.30, In2O3 9.03, HfO2 19.57 - SI not bundled; values recorded by Astra from the online SI). Nt(2 nm) 5.3e19 cm^-3 vs Nt(10 nm) 3.39e18 (PBS devices) and "factor ~4 from 13.2 to 2 nm" (thickness series) are from different device sets. Tt absolute values not given (only dTt). Delta_sr 2.87 A (prose) vs nm axis (figure) unit ambiguity noted by Astra. Main-text Eq.(1b)/(1e)/(1f) conventions differ from the SI (Astra SOURCES_AND_CORRECTIONS) |

## C. Supplied literature bundle (PDF -> `inputs/papers_text/*.txt`)

| File | Reference | What was used | Type | Reliability for IWO model |
|---|---|---|---|---|
| nl0c03967.pdf | Si et al., Nano Lett. 21, 500 (2021) | TNL/CNL 0.4 eV above bulk Ec; DFT: Ec up-shift ~0.6 eV at 1.5 nm, Ev unchanged (In2O3/Al2O3 slab, PBE); eps 8.9 (cited Hamberg) | DFT + experimental (ALD In2O3) | proxy (pure In2O3, ALD, amorphous) |
| nn2c10383.pdf | Lin et al., ACS Nano 16, 21536 (2022) | m* 0.17/0.19/0.23/0.30 m0 (bulk/3.52/1.98/0.95 nm, PBE); PBE gaps 0.94/1.27/1.88 (bulk/1.98/0.95 nm); Dit 6e11 cm^-2/eV; n2D up to 7e13; EF 0.5 eV above Ec at 5e13 cm^-2 | DFT + Hall/C-V | proxy (pure In2O3); slab gap at 3.52 nm not printed in text |
| fmats-09-850451 (1).pdf | Wang et al., Front. Mater. 9, 850451 (2022) | Dit(HfO2/In2O3) 6.3e11; bulk subgap DOS 3.3e20 cm^-3/eV; ND 1e20 (ALD In2O3); TCAD tail+Gaussian conventions | experimental (C-V, conductance) + TCAD | proxy (undoped In2O3, HfO2 contact, not Al2O3) |
| fb123ddb-...pdf | Kim et al., APL 125, 173507 (2024) | thickness trend of bulk/border traps (2.4/3.1/14.6e18 at 10/20/30 nm), Vth/SS trend, W6+ XPS | experimental | proxy (RF-sputtered 99:1 wt In2O3:WO3, SiO2 gate, 300 C anneal) |
| 225102_1_online.pdf | Stokey et al., JAP 129, 225102 (2021) | eps_DC 10.55, eps_inf 4.05, m*(0.208 m0) at n 2.8e17; nonparabolicity C 0.5 eV^-1 (cited) | experimental (ellipsometry/optical Hall) + DFPT | proxy (bulk single crystal In2O3) |
| s41928-022-00718-w.pdf | Si et al., Nat. Electron. 5, 164 (2022) | scaling of ALD In2O3 (0.5 nm), CNL/low contact resistance (<0.1 ohm mm), ND 9e19 | experimental | proxy; supports Ohmic-contact assumption qualitatively |
| TED_2025_UT Austin (1).pdf | Pandey et al., IEEE TED 72, 2381 (2025) | 2-D Green's-function model; Sentaurus calibration used trap 1e20 cm^-3 at 0.4 eV above Ec (CNL-like) | analytical + TCAD (In2O3) | methodological reference only |
| A_Physics-Based_Compact_Model_for_IGZO...pdf | Wang et al., IEEE TED 72, 2390 (2025) | shallow-donor Gaussian as positive charge in depletion (Gauss-Fermi treatment); floating-body | compact model (IGZO) | methodological reference; supports donor-Gaussian representation |
| 1-s2.0-S2665917424003672-main.pdf | Anusha & Dwivedi, Meas. Sens. 36, 101391 (2024) | review of IGZO TCAD/compact modelling; SS -> Nss/Dit relation; WIZO mobility vs W content | review | background only |
| 2009_JPhysCondMat_21_395502_quantum-Espresso.pdf | Giannozzi et al., JPCM 21, 395502 (2009) | QE code reference for the (unexecuted) DFT workflow | software reference | not a data source |

## D. GPT Astra 6 package `IWO_PRIORITY_THREE_20260912.zip` (unpacked read-only to `inputs/astra_.../`)

| Item | Purpose | Type | Reliability | Notes |
|---|---|---|---|---|
| `decks/individual/iwo_{2p0,6p3,13p2}nm.in`, `decks/combined/IWO_SELECTED_ALL.in` | executed native ATLAS decks (2/6.3/13.2 nm) | generated + executed | HIGH as numerical baseline (hash-matched runs in `audit/results/...`) | Combined deck itself never executed. 31.8 nm deferred |
| `config/iwo_*.json` | full parameter sets, provenance strings | fitted/assumed | HIGH (self-documented) | shared Eg 3.05 / chi 4.30 / eps 9.3 / Nc 5e18 / Nv 1e19; gate WF 4.765; S/D WF 4.45 + SURF.REC (ARICHN 110 inherited); tail only (NTA 5.5e20/3.71e20/7.14e19, WTA 0.040/0.040/0.035); ND 2e17/1e17/8.9e17; mu 13.3/12/55; no interface traps, no Gaussians |
| `MODEL_AND_RESULTS.md`, `HANDOFF_STATUS.md`, `ASSESSMENT.md`, `RUN_BY_RUN_SUMMARY.md` | results and history (70 invocations) | reports | HIGH | active log RMSE 0.0334/0.0492/0.0490 dec; +3 V error +0.69/+1.97/+2.45 %; 54/54/46 native zeros; 13.2 nm DOS check missing (INCOMPLETE) |
| `audit/docs/rebuild_20260912/MEASUREMENT_CONSTRAINTS.md` | measurement-only constraints (Cox, crossings, gm, powers) | analysis | HIGH (reproducible numbers) | Cox = 8.95537e-7 F/cm^2; 31.8 nm total R 672 ohm at 3 V; 2 nm charge-budget argument |
| `audit/docs/rebuild_20260912/{CONTACT_EMISSION_DEFAULTS,PRIORITY_THREE_OFF_CURRENT_AUDIT,QUANTUM_SENSITIVITY,QUANTUM_CHARGE_VERIFICATION}.md` | contact/Richardson, off-current thermal bound, BQP/Schrodinger diagnostics | audits + one hard-wall SP diagnostic run | HIGH | thermal generation 13-17 decades below measured plateaus; ARICHN 110 -> 41 changes Id by 0.38 %; hard-wall SP at 2 nm is a charge sensitivity only |
| `audit/docs/paper_revision_20260911/{defect_papers,ald_paper,athena_audit}.md` | Fan 2021 DOS table and its printed inconsistencies; Yoo 2024 ALD IWO; ATHENA capabilities | reviews | HIGH (careful) | Fan 2021: Eg 3.05/chi 4.30, NC varied as fit knob, sigma printed 1e12 (sign error), acceptor-energy reference ambiguity |
| `audit/decks_paper_revision/athena/*.in` | ATHENA geometry decks (executed once for 2 nm) | generated | geometry only | no sputter/defect chemistry, as Astra states |
| `audit/config/combined_*.json`, `priority3_*.json` | intermediate configs | fitted | provenance only | |

## E. Claude package `IWO_ATLAS_Model_claude` (this machine, 34 real-ATLAS launches, `results/atlas_local/RUN_INDEX.csv`)

| Item | Purpose | Type | Reliability | Notes |
|---|---|---|---|---|
| `decks/iwo_{2p0,6p3,13p2}nm_CALIBRATED_run_00{13,30,24}.in`, `iwo_31p8nm_BEST_run_0034.in`, `IWO_ATLAS_all_thicknesses_CALIBRATED.in` | executed decks of the best verified runs | generated + executed | HIGH as numerical baseline | active log RMSE 0.019/0.048/0.025/0.093 dec; Id(3 V) -3.3/0.0/0.0/-8.3 % |
| `config/model_seed.json`, `config/calibrated_*.json`, `config/proposal_*.json` | parameters and numerics | fitted/assumed | HIGH | same seed lineage as Astra (Eg 3.05, chi 4.30, eps 9.3, Nc 5e18); differences: gate WF 4.70, Ohmic S/D, regularized interface sheet (2-6e11), per-thickness Nd 2e17/3e17/3e17/2.65e18, mu 12.3/11.3/55.1/82, 31.8 nm back-surface donor sheet + series R |
| `docs/{ENVIRONMENT_REPORT,VALIDATION_CHECKS,PARAMETERS_AND_PROVENANCE,CHANGELOG}.md` | environment, numerical checks, provenance | reports | HIGH | mesh/DOS/interface-layer checks: <0.009 dec (2 nm), 0.004 dec (13.2 nm); KCL floors; ATLAS ignores MOBILITY updates between SOLVEs; 32-bit memory limit ~30k nodes |
| `scripts/{generate_atlas,atlas_workflow,poisson1d_prescreen,...}.py` | generator, runner, surrogates | code | HIGH (17 tests) | reused (copied) by V1 |
| `results/preliminary/*` | analytical Python fits of the compact model | NOT TCAD | do not use as simulation evidence | |

## F. User-pasted ATHENA+ATLAS deck (chat, 2026-09-21)

Unified-law deck (Nt = 5.3e19 (2/t)^0.95, Nd = 6e18/(1+(9/t)^2.2), Dit = 4.9e11 (t/2)^0.35, mu = 30 (1-2.87A/t)^2/(1+0.35 Vov)) with Pd Schottky + UST tunnelling, CVT mobility, V_O ladder from UBPC spectroscopy (Mattson et al., not supplied), INTDEFECTS sheets. Type: generated, never executed here. Reliability: its physics choices are untested in this installation (Schottky/tunnelling, CVT on IGZO material, INTDEFECTS with custom material), `maxtraps=20` exceeds the documented range, and its ATHENA block is not consumed by the ATLAS block. Its thickness-law idea is adopted in V1; its numerical coefficients are not (unsourced).

## G. Contradictions to carry forward

1. Bulk m*: PBE 0.17 (Lin), experiment 0.208 (Stokey), zero-density extrapolation 0.18 (Feneberg) -> V1 uses 0.208 + DFT increment.
2. eps: 9.30 (target IWO, C-V) vs 10.55 (bulk crystal) vs 8.9 (evaporated film) -> 9.30 used, others as sensitivity bounds.
3. Nc: Astra/Claude seed 5e18 corresponds to m* 0.34 m0 (their own consistency note); V1 Nc from m*(t) is 2.4-3.4e18.
4. Nt(2 nm): Januar 5.3e19 (with theta_t) vs real-ATLAS tail integrals 2.0-2.2e19 (Claude/Astra) -> same order; conventions differ.
5. Off-state floors (5e-15 / 1.5e-13 / 6.6e-12 A/um) are not reproducible by intrinsic drift-diffusion (Astra thermal bound; Claude native zeros); origin NOT DETERMINED (no IG/IS data).
6. 31.8 nm: always-on with a saturating on-state; requires a mechanism beyond the thin-film DOS model (back-surface donors + series R in Claude V0; deferred by Astra).
