# Audit of the ATLAS deck generator and runner (2026-10-10)

**Scope.** This audit asks one question: can the campaign add realistic physical models to the decks without breaking the V1/V2 baseline? It covers:
- the deck generator `scripts/build_iwo_decks.py`;
- the runner `scripts/run_atlas.py`;
- the campaign driver `scripts/run_campaign.py`;
- `config/*.yaml` and `config/campaign_*.json`;
- `analysis_2026-10-06_V2/regress_decks.py`;
- the decks and solver logs of runs 0038/0039/0040 (V1) and 0058/0059/0060 (V2);
- the installed ATLAS 5.28.1.R manual and example decks under `C:\sedatools`.

**Nothing was launched.** No `deckbuild.exe`, no `run_atlas.py` and no `run_campaign.py` were run. The only code executed was:
- deck text generation through `build_deck()`. That module contains no `subprocess` or `deckbuild` call (checked with grep);
- arithmetic.

No file in `data/`, `results/` or `config/` was modified.

**Manual citations.** "PDF p. N" is the page marker in `report_latex_full/tools/atlas_manual_pages.txt`, a text extract of `C:\sedatools\lib\atlas\5.28.1.R\docs\atlas_users1.pdf` dated June 25, 2019. In chapter 22 the printed page number is the PDF page minus 6. Example decks are under `C:\sedatools\examples\deckbuild\4.2.5.R\` (© 2019, same release).

**Labels.**
- **VERIFIED.** Found in the 5.28 manual or an example deck, or shown in this installation's own solver output (`deckbuild.out`).
- **UNVERIFIED.** Syntax, or behaviour with our user-defined material, was not confirmed. The first run must check it.

Parameter labels follow the charter: COMPUTED / MEASURED / LITERATURE / FITTED / ASSUMED.

---

## 0. Summary

1. **The baseline is reproducible.** With the current generator, 48 of 49 finished final-form decks regenerate identically, including:
   - V1 runs 0012–0057;
   - the ID-VD runs 0041–0043;
   - V2 runs 0058–0060.

   The one difference is run_0027, the documented malformed overlap run. A new harness, `analysis_2026-10-10_campaign/regress_all_decks.py`, makes this the gate for every code change: it must keep printing `unexpected differences 0`.
2. **SRH and Fermi–Dirac statistics are already on in every V1/V2 deck.**
   - `models fermi srh temp=300 print`;
   - `material … taun0=1e-06 taup0=1e-06` (ASSUMED);
   - DEFECTS capture cross-sections of 1e-15 cm² (ASSUMED), which make the TFT continuous-DOS recombination of Eq. 15-16 active.

   The solver output of run_0040 confirms `SRH T` and `Fermi-Dirac T`. "Adding SRH" therefore means varying lifetimes and cross-sections, or adding holes (`carriers=2`). It is not a new switch.
3. **Bounds on the off-state floors** (§7, COMPUTED from the solver's own parameters):
   - **SRH and TAT/Poole–Frenkel generation:** at most 8e-29 A/µm, 16–17 orders of magnitude below the measured floors (4.61e-15 / 1.53e-13 / 6.60e-12 A/µm, MEASURED/DERIVED). Even a 1e10 field enhancement leaves the current at least 5×10⁵ below every floor.
   - **Fowler–Nordheim and direct tunnelling through the 17 nm stack:** negligible for representative barriers (φ ≥ 2.2 eV). Only an optimistic φ = 1.8 eV, m* = 0.11 reaches the 2 nm floor at −3 V, and that current changes by many decades between −3 and −0.5 V, which contradicts the flat floor.
   - **Ohmic path in parallel:** this is the only candidate in this list that gives a V_G-independent current of the right size. It was tested only after the solver (V2 variant D). Section 7.11 gives two ways to put it inside ATLAS.
4. **The most relevant new model is not on the requested list.** It is the carrier-density-dependent mobility `MOBILITY IGZO.TOKYO`, an amorphous-oxide model with an installed example (`tft/tftex21`). It is relevant to the open mobility-shape problems:
   - 6.3 nm power-law exponent γ = 1.13 measured vs 0.57 in TCAD;
   - the V_G dependence of μ_FE.

   Its use with a `user.material` is UNVERIFIED.
5. **Five silent traps found in the current decks** (§3.3, all VERIFIED from `deckbuild.out` of run_0040 or from the manual). Any new option must set its parameters explicitly:
   - **Insulator band parameters are ATLAS defaults.** HfO2 has χ = 0 eV and Eg = 5.7 eV; Al2O3 has χ = 0.9 eV and Eg = 9 eV.
   - **The IWO material inherits silicon defaults** through `user.default=silicon`:
     - ARICHN = 110 A cm⁻² K⁻²;
     - vsatn = 1.03e7 cm/s;
     - me.tunnel = 0.322, mass.tunnel = 0.25;
     - the band-to-band parameters.
   - **INS.OHMIC defaults to True** (PDF p.1152, p.1158). The Pd source/drain volumes touch both IWO and Air, so a CONTACT WORKFUN on them would be treated as Ohmic unless `^ins.ohmic` is given.
   - **`set_dotted()` turns the string `false` into a truthy value.** It cannot create missing keys either.
   - **The default runner timeout (900 s for t ≤ 20 nm) is shorter than a normal 13.2 nm run at DOS 384/192** (770–1120 s).
6. **Correction to a sibling document.** `codex_design.md` (this folder) says the deck applies QF at the IWO/Air boundary. It does not. The line `interface qf=… y.min=-1e-7 y.max=1e-7` encloses only y = 0, the IWO/Al2O3 boundary. QF is placed on the IWO/Air surface only by the optional back-surface charge, and only for the exposed channel `x ∈ [lc, xr]` (generator lines 250–254).
7. **A documented restriction the existing generator already breaks.** The manual says "distributed or lumped external elements" require `METHOD NEWTON CARRIERS=2` (PDF p.85, VERIFIED).
   - Every 31.8 nm deck (runs 0006 and 0010) emits `contact … resistance=46000` with `carriers=1 electrons`.
   - Any contact-resistance option (§7.8) inherits this restriction.
   - 31.8 nm is excluded from the fits, but runs 0006 and 0010 should be read with this in mind.
8. **One state-file fact is empirical, not documented.** "MOBILITY statements between SOLVEs are ignored" comes from our run_0008. Codex found no such rule in the manual, and neither did this audit. Keep the rule, cite it as EMPIRICAL (run_0008), and put every MOBILITY statement before `solve init`.

---

## 1. Code map

| File | Role | Lines that matter |
|---|---|---|
| `scripts/build_iwo_decks.py` | The single deck generator. `build_deck(t, m, g, s, …)` returns the deck text and metadata. | `material_at()` 76–103 (thickness laws); `defects_block()` 113–130; mesh 148–159 and 205–211; regions and electrodes 212–233; MATERIAL/CONTACT/MODELS 234–243; DEFECTS 244–247; INTERFACE 249–254; METHOD 166 and 255; probes 258–259; bias and log 284–326; extracts 327–339 |
| `scripts/run_atlas.py` | One launch: reserves a run ID, writes `device.in`, runs `deckbuild.exe -run device.in -outfile deckbuild.out`, then validates, scores and appends to RUN_INDEX. `--rescore` re-scores without launching. | overrides 120–124; timeout 148; scan 63–69; KCL validation 100–105; scoring 71–82; ID-VD mode 187–235 |
| `scripts/run_campaign.py` | Runs a JSON plan through `run_atlas.execute`/`execute_output`. `--workers N` gives parallel launches, which failed on this machine (runs 0056/0057); use the default of 1. | 41–59, 66–93 |
| `config/solver.yaml` | MODELS string, carriers, METHOD, acceptance windows, DOS levels, sweep segments, runner argv, timeouts, `max_launches` 271 | — |
| `config/geometry.yaml` | Stack, structure (`full`), mesh, sweep | — |
| `config/iwo_material_model.yaml` / `_v2.yaml` | Material model V1/V2. V2 is selected by `IWO_MODEL_FILE=config/iwo_material_model_v2.yaml`. | — |
| `analysis_2026-10-06_V2/regress_decks.py` | Rebuilds transfer decks from `execution.json` overrides and compares them. Does not cover ID-VD or V2 selection; the caller must set the environment variable. | — |

**Overrides.**
- An override `k=v` is routed to solver.yaml (`solver.`), geometry.yaml (`geometry.`) or the material model (anything else).
- The routing code is copied in four places: `build_iwo_decks.main`, `run_atlas.execute`, `run_atlas.execute_output` and `regress_decks.py`. A new prefix would have to be added in all four, which is why §8 recommends none.
- `set_dotted()`:
  - converts any value that parses as a float;
  - leaves `true`/`false` as strings, and the string `false` counts as True in Python;
  - raises KeyError when an intermediate key does not exist.

**A route that needs no code change.** The override `solver.models=<string>` replaces the whole MODELS line. Campaign B used it for temperature: `solver.models=fermi srh temp=358.15 print`. Every MODELS-only flag can be exercised today this way (TRAP.TUNNEL, TRAP.HURKX, TRAP.COULOMBIC, FNORD, QTNLSC.EL, PRPMOB, BBT.*, BQP.N, …). Two cautions:
- the string must still contain `fermi srh temp=300 print`;
- the generator reads the simulation temperature from it with the regex `temp=([0-9.]+)`.

---

## 2. Baseline regression: byte-identical V1/V2 decks

This was checked on 2026-10-10 with `analysis_2026-10-10_campaign/regress_all_decks.py`, which is new and never calls the simulator.

- **IDENTICAL (48):**
  - transfer runs 0012–0026, 0028–0040, 0044–0057 (V1, model `config/iwo_material_model.yaml`);
  - ID-VD runs 0041–0043;
  - V2 runs 0058–0060 (model taken from the `model=` note in RUN_INDEX).

  These include the decks of the final V1 runs 0038/0039/0040 and the V2 runs. Their hashes match `deck_sha256` in RUN_INDEX: for example run_0058 is `4e70e7b4…` and run_0040 is `50ec4862…`.
- **DIFFERENT (1): run_0027.** The generator change of 2026-09-27 (the x-mesh now follows the contacts) is documented at generator line 208. The corrected rerun is run_0053/0055.
- **SKIPPED:** runs 0001–0011 (reduced structure or pointwise sweep), and any run marked PREDICTION or partial.

**Note on the comparison.** It is on text read in newline-normalised mode, which is the string the RUN_INDEX hash was computed on. On disk, Windows text mode writes CRLF.

**Rule for the campaign.** Every option must default to OFF and emit no line when OFF. The harness must report `unexpected differences 0` after each code change and before any launch.

---

## 3. What the current decks contain

Taken from run_0040, 13.2 nm, V1 recalibration at DOS 384/192. Run_0038/0039 and V2 differ only in values.

### 3.1 Statements

| Statement | As generated | Labels (from the deck header) |
|---|---|---|
| Structure | `mesh width=1.0` (currents in A/µm). Regions: 1 = IWO bulk; 2 = IWO 0.25 nm interface layer; 3 = Al2O3 2 nm; 4 = HfO2 15 nm; 6 = Conductor 50 nm (TiN gate); 7 = Air above the channel. Electrodes: `gate` on region 6; `source`/`drain` are Pd volumes (`material=Palladium`) at x = 0–2 and 22–24 µm on the IWO top. | Geometry MEASURED_TARGET_DEVICE; 2 µm overlap ASSUMED |
| DOPING | `doping uniform n.type conc=Nd_eff(t)` in regions 1 and 2 | FITTED law |
| MATERIAL (IWO) | `user.group=semiconductor user.default=silicon eg300 affinity permittivity nc300 nv300 mun mup taun0 taup0` (+ `egalpha=0` when T ≠ 300 K, + `tmun` when `solver.tmun` is set) | Eg, χ from the thickness laws; MUN FITTED; τ = 1e-6 s ASSUMED |
| MATERIAL (oxides) | Only `material region=3 permittivity=9.0` and `material region=4 permittivity=19.57` | ε_HfO2 MEASURED (SI Fig. S1); ε_Al2O3 ASSUMED |
| CONTACT | `contact name=gate workfunction=4.7` only. The solver prints gate 4.700 eV and source/drain 0.000 eV, i.e. Ohmic. The manual says `ELECTRODE MATERIAL=` "does not apply any electrical property such as workfunction" (ELECTRODE section, PDF p.1213–1217). | TiN 4.7 eV ASSUMED; Ohmic source/drain ASSUMED |
| MODELS | `models fermi srh temp=300 print` | — |
| DEFECTS | Regions 1 and 2: `defects region=n continuous numa numd nta wta ntd wtd nga ega wga ngd egd wgd sig{t,g}{a,d}{e,h}=1e-15 afile dfile`. In region 2 the interface sheet is moment-matched into the Gaussian (NGA = sheet / 0.25 nm). | Units cm⁻³ eV⁻¹ (VERIFIED: TFT chapter, PDF p.880 Table 15-1). Region 1 is the bulk DOS, region 2 adds the interface sheet. |
| INTERFACE | `interface qf=Qf x.min=0 x.max=24 y.min=-1e-7 y.max=1e-7`, the IWO/Al2O3 boundary at y = 0. Optional: Qb on IWO/Air for x ∈ [lc, xr]. | Qf FITTED |
| METHOD | `newton trap maxtraps=10 itlimit=80 climit=1e-6 ir.tol=1e-19`, then `cr.toler=<strict> xandrnorm carriers=1 electrons` up to the switch voltage, then `cr.toler=5e-18 ^xandrnorm`. Strict cr.toler = max(1e-17, 1e-5 × the smallest measured active current), which gives **1e-17 / 2.28e-17 / 7.88e-16 A** for 2.0 / 6.3 / 13.2 nm. Switch voltage = first V_G where the measured current exceeds 1e-9 A/µm. | NUMERICAL. MAXTRAPS range 1–10 VERIFIED (METHOD, PDF p.1395). |
| Probes and outputs | `chan_mob`, `chan_n`, `avg_n` at the channel centre; band and QFL cuts saved at equilibrium, near V_th and in the on-state | — |

### 3.2 What the solver reports (run_0040 `deckbuild.out`, VERIFIED)

- **Grid.** 9,594 / 10,179 / 12,051 points for 2.0 / 6.3 / 13.2 nm.
- **Regional model flags.** `SRH T`, `Fermi-Dirac T`. All of these are F: bbt, bbtnonlocal, tat(local), tatnonlocal, tat(coulombic), impact, incomplete, bgn.
- **Mobility.** "Concentration Independent Mobility", mu = 57.79, `tmu = 1.5`.
- **Intrinsic density.** n_i = 1.48e-10 / 2.99e-8 / 7.18e-8 cm⁻³ (2.0 / 6.3 / 13.2 nm, V1).
- **This printout can verify new options.** It confirms whether a new flag is really active; see §9.

### 3.3 Silent defaults that a new option would expose (VERIFIED in run_0040 `deckbuild.out`)

| Parameter | Value in the solver now | Why it matters |
|---|---|---|
| HfO2 χ / Eg | **0 eV** / 5.7 eV | Gate tunnelling and FN would see a 4.3–4.7 eV barrier. LITERATURE: χ_HfO2 ≈ 2.5 eV and Eg ≈ 5.8 eV (conduction-band offset to Si 1.5 eV; Robertson, J. Vac. Sci. Technol. B 18, 1785 (2000)). |
| Al2O3 χ / Eg | 0.9 eV / 9 eV | LITERATURE (same source): Eg 8.8 eV, offset to Si 2.8 eV, so χ ≈ 1.25 eV. ALD amorphous films have a smaller gap, to be cited before use. |
| IWO ARICHN / ARICHP | 110 / 30 A cm⁻² K⁻² (silicon) | Schottky thermionic emission. COMPUTED replacement: A* = 120·m*/m0 = 24.7 for m* = 0.206 (DFT, `qe_workflow/cern_htcondor/results/RESULTS_LOG.md`). |
| IWO vsatn | 1.03e7 cm/s (silicon) | Used by FLDMOB. Irrelevant at L = 20 µm (§7.4). |
| IWO me.tunnel / mh.tunnel / mass.tunnel | 0.322 / 0.549 / 0.25 (silicon) | Used by TRAP.TUNNEL and band-to-band models. Set from DFT m*. |
| Hole masses, BGN parameters | silicon | BGN is off; holes are not solved. |
| CONTACT INS.OHMIC | True by default | Pd source/drain touch IWO and Air, so a Schottky option needs `^ins.ohmic`. UNVERIFIED in practice. |

---

## 4. How the gate current is reported

- **What is exported now.**
  - The deck extracts `curve(v."gate", i."gate")` into `igvg.dat`.
  - The runner interpolates it onto the drain grid. It validates KCL with |I_D + I_S + I_G| ≤ max(1e-17 A, 0.1 × measured floor) + 1 % Σ|I|, and stores `ig_raw_A` in `terminal_currents.csv`.
  - In every V1/V2 run I_G is exactly 0 (run_0040 `igvg.dat`: all 76 points are 0). The oxides are perfect insulators and no tunnelling model is on, so the TCAD gate current says nothing about the experiment. **No gate current was measured.**
- **Self-consistent tunnelling** (`FNORD`/`FNHOLES`, `QTNLSC.EL`/`QTNLSC.HO`/`QTUNNSC`, `SCHKSC`). The current enters the continuity equations, so the terminal currents, including `i."gate"`, contain it and KCL holds (VERIFIED: PDF p.288 and p.298). This is the variant to use with the current runner.
- **Post-processing tunnelling** (`FNPP`, `QTUNN.EL`, `SCHENK`). The current is computed after convergence and written to the log (`LOG … J.TUN`, PDF p.1305–1307). The direct-tunnelling variable is `Itnl` (A) or `Jtnl` (A/µm) (PDF p.303).
  - DeckBuild's extract can read a Fowler–Nordheim current as `ifn."gate"` (DeckBuild manual, printed p.150).
  - **The manual adds the tunnelling current to the receiving electrode in both forms.**
    - For FN, "for either model, the implementation scheme is the same": the current is added to a segment on the electrode–insulator boundary, and the gate current is the sum over segments (PDF p.288–289).
    - For direct tunnelling, carriers "are added to the current of the electrode into or from which they flow" (PDF p.303).

    Codex reached the same reading. With a post-processing model, `i."gate"` therefore grows while the channel side is not debited. The runner would then report `KCL_FAILED` on a sound solution and waste a launch. This is documented but not yet seen in this installation.
  - **Use the self-consistent variants.** A post-processing run needs a runner flag that leaves the tunnelling current out of the KCL sum.
- **What to compare with the floors.** Compare I_D, not I_G. In the experiment the floor is the drain current. A self-consistent gate current appears in I_D only through the share collected by the drain, so record both I_D and I_G.
- **Installed examples that log `j.tun`.**
  - With self-consistent direct tunnelling: `diode/diodeex12`, `solar/solarex15`.
  - With other tunnelling models: `quantum/quantumex20` (Ielmini TAT), `sonos/*`.

  They show the syntax only. Whether `i."gate"` contains the current in our deck must be checked on the first such run, by comparing it with the J.TUN column.

---

## 5. How the generator builds the mesh, and thin versus thick films

- **x direction** (`geometry.yaml mesh.x_um`): 0.3 µm at the edges, 0.05 µm and then **0.01 µm at the contact edges** (x = 2 and 22 µm), 0.2 µm, and 0.7 µm in mid-channel. When the overlap differs from 2 µm the lines follow the contacts (line 208).
- **y direction** (lines 155–159):
  - one line at the film top y = −t with spacing `min(1.0 nm, t/8)`: 0.25 / 0.79 / 1.0 nm for 2.0 / 6.3 / 13.2 nm;
  - interface layer y ∈ [−0.25 nm, 0] at 0.0625 nm;
  - Al2O3 at 0.25 nm, HfO2 at 1 nm, the Air top and TiN at 20 nm.

  ATLAS grades the spacing between lines. With a back-surface donor sheet the top 0.25 nm becomes region 5, meshed at 0.0625 nm.
- **Mesh convergence of the current physics** (COMPUTED, scored output of existing runs):

  | Check | Run | Active RMSE |
  |---|---|---|
  | 13.2 nm, ×0.7 | run_0028 vs run_0013 | 0.0818 vs 0.0814 dec |
  | 6.3 nm, ×0.7 | run_0036 vs run_0015 | 0.0625 vs 0.0626 dec |

  ×0.5 exceeds the memory of the 32-bit build (state file §K).
- **Thin versus thick: the current settings are adequate for the present physics.** Options that act at the top surface need finer y lines near y = −t, emitted only when the option is on:
  - Schottky or UST contacts: tunnelling range D.TUNNEL = 10 nm by default (PDF p.164);
  - back-surface charge or a strip;
  - density gradient or BQP.

  At 13.2 nm the top spacing is 1 nm, which is too coarse for a 1–3 nm tunnelling region under the contacts. Proposal: add `(-t+3 nm, 0.2 nm)` and set `(-t, 0.05–0.1 nm)` when the option is on. Because y lines run across the whole width, this adds about (number of x lines) × (new y lines) ≈ 1.5–2 k points, staying below about 15 k.
- **Gate tunnelling** needs a fine mesh in the tunnelling direction (PDF p.298). The oxides are at 0.25 nm (Al2O3) and 1 nm (HfO2); refine HfO2 to about 0.25 nm when the option is on. ATLAS-built rectangular meshes get automatic slices, so QTX.MESH/QTY.MESH are optional (PDF p.302).

---

## 6. Run times (from RUN_INDEX.csv, wall clock, sequential)

| Configuration | 2.0 nm | 6.3 nm | 13.2 nm |
|---|---|---|---|
| Transfer, DOS 96/48 (runs 0012–0037) | 125–305 s | 200–390 s | 246–452 s |
| Transfer, DOS 384/192 (final V1/V2 and their sensitivity runs) | 233–612 s, typically 360–440 s (0038: 436; 0058: 360) | 508–739 s (0060: 508; 0052: 538; 0039: 739) | 772–1122 s (0059: 772; 0051: 803; 0049: 976; 0040: 1122) |
| Transfer at 358 K (DOS 384) | 380 s (0045); 1378 s with `tmun=0` (0054) | 664 s | 902 s |
| ID-VD, 5 V_G values (DOS 384) | 1266 s | 1458 s | 1926 s |
| Mesh ×0.7 | — | 787 s | 1068 s |

**Wall time is not deterministic.** The same deck (sha `5e34cef3`) timed out at 902 s as run_0053 and finished in 612 s as run_0055.

**The default timeout is too short at 13.2 nm.** The runner uses 900 s for t ≤ 20 nm, which is below the normal 13.2 nm time at DOS 384. Campaign entries must pass `"timeout": 1500` or more (campaign B did this for B3). Every new physics option adds cost. Suggested defaults: 2.0 nm 1200 s, 6.3 nm 1500 s, 13.2 nm 2400 s, and ×1.5 for gate tunnelling or DG/BQP.

---

## 7. Candidate models

Each subsection gives the deck syntax, 5.28 support, relevance, solver risk and how to expose the model as an option.

**Reference for the bounds below** (MEASURED/DERIVED floors and COMPUTED estimates; script `analysis_2026-10-10_campaign/leakage_bounds.py`, which is pure arithmetic and reproduces every number quoted):

| Film | Floor (A/µm) | Ohmic conductance needed (S/µm) |
|---|---|---|
| 2.0 nm | 4.61e-15 | 6.6e-15 |
| 6.3 nm | 1.53e-13 | 2.2e-13 |
| 13.2 nm | 6.60e-12 | 9.4e-12 |

The conductance is G = I/V_D.

### 7.1 SRH generation and recombination (MODELS SRH, MATERIAL TAUN0/TAUP0, DEFECTS capture)

- **Syntax:**
  - `models … srh` (or `consrh`);
  - `material material=IWO taun0=<s> taup0=<s>`;
  - DEFECTS `sigtae sigtah sigtde sigtdh siggae siggah siggde siggdh` (cm²).
- **5.28 support: VERIFIED.**
  - SRH: PDF p.228–229. CONSRH: p.230.
  - DEFECTS recombination: TFT chapter, Eq. 15-16 (PDF p.883).
  - Capture cross-section table: PDF p.882.
  - Example: `tft/tftex21/tftex21_aux.in` uses `models srh fermi` with `carr=1 electron`.
- **Already ON in V1/V2.** τ = 1e-6 s and σ = 1e-15 cm² are both ASSUMED.
- **Relevance to the floors: none** (COMPUTED). The upper bound for mid-gap generation is G ≤ n_i/(τ_n + τ_p), with the shortest lifetime τ = 1/(σ v_th N_t). Inputs: σ = 1e-15 cm², v_th = 1.08e7 cm/s (solver), N_t = NTA·WTA from the V1 law, n_i from the solver.

  | Film | τ | G_max | I over a 20 µm × t × 1 µm volume | Ratio to floor |
  |---|---|---|---|---|
  | 2.0 nm | 4.6e-12 s | 16 cm⁻³ s⁻¹ | 1.0e-31 A/µm | 2e-17 |
  | 6.3 nm | — | — | 2.8e-29 A/µm | 2e-16 |
  | 13.2 nm | — | — | 8.0e-29 A/µm | 1e-17 |

  A volume generation process would also scale as t, not t^3.85.
- **Solver risk.**
  - Generation needs holes. With `carriers=1 electrons` the hole density comes from a frozen quasi-Fermi level, so the generation term is effectively unbounded by hole transport.
  - A diagnostic with `carriers=2` already works through the existing override `solver.carriers=carriers=2`. Expect poor conditioning: p ≈ 1e-40 cm⁻³, and J_p of 1e-38 to 1e-55 A in earlier runs (solver.yaml comment).
- **Option.** No code needed: `bulk_reference.srh_tau_s.value=<τ>` and `traps.bulk_acceptor_tail.capture_cm2=<σ>` already exist. A two-carrier null test is one launch at 13.2 nm. Codex's run 6 in its design proposes this; the bound above says it will show nothing.

### 7.2 Trap-assisted tunnelling (TRAP.TUNNEL, TRAP.HURKX, TAT.NONLOCAL)

- **Syntax:**
  - `models … trap.tunnel mass.tunnel=<m*/m0>`;
  - optional `trap.hurkx`, which per the manual applies the enhancement for CONTINUOUS DEFECTS and INTDEFECTS to recombination and generation only;
  - or `tat.nonlocal` (which also sets TRAP.TUNNEL), with `tat.nldepth`/`tat.relei`.
- **5.28 support: VERIFIED.**
  - TFT chapter (PDF p.884–885): the Dirac field-enhancement factors multiply the DEFECTS capture cross-sections SIGTAE/SIGGAE/SIGTDE/SIGGDE and the hole ones.
  - Generic TAT: PDF p.132–133 (MASS.TUNNEL default 0.25, MODELS).
  - Flags: PDF p.1460.
  - Example: `tft/tftex12/tftex12.in` with `models srh fldmob print trap.tunnel ^trap.coulombic mass.tunnel=0.1 bbt.std`, an IGZO TFT.
- **Parameter.** MASS.TUNNEL = 0.206 m0, COMPUTED (DFT 2 nm in-plane conduction-band mass; RESULTS_LOG). The bulk alternative is 0.208 m0, MEASURED_RELATED_MATERIAL (Stokey 2021). Never leave the silicon default of 0.25.
- **Relevance.**
  - The off-state current stays negligible: even 1e10 × the SRH bound is ≤ 1e-18 A/µm.
  - Through the occupation functions it can slightly change trapped charge near the Al2O3 interface, where the field is about 1–3 MV/cm. That could touch SS or V_th by a small amount.
  - At most one combined null test, together with 7.3.
- **Solver risk.** Field-dependent capture adds nonlinearity in the strict-acceptance window. TAT.NONLOCAL needs tunnelling slices or QTREGION; QTREGION must come after X/Y.MESH, ELECTRODE and REGION but before DOPING (PDF p.287).
- **Option.** `physics_options.trap_tunnel {enabled, mass_tunnel, variant: local|hurkx|nonlocal}` appends flags to the MODELS line. Zero-code route: `solver.models=fermi srh temp=300 print trap.tunnel mass.tunnel=0.206`.

### 7.3 Poole–Frenkel (TRAP.COULOMBIC)

- **Syntax:** `models … trap.coulombic` with `material material=IWO a.trapcoulombic=<> b.trapcoulombic=<>` (defaults 1.0; Table 15-3).
- **5.28 support: VERIFIED** (PDF p.885–886; MODELS flag p.1460). `tftex12` shows the negation `^trap.coulombic`.
- **Physics caveat.** The manual says the effect "only occurs in traps with a Coulombic potential (such as traps that are neutral when filled)", which means donor-like states. In the generator, NTD = 0 and NGD = 0, so the V1/V2 DOS is purely acceptor-like. ATLAS nevertheless applies the Coulombic factors to all electron capture cross-sections, including SIGTAE (Eq. 15-27). For our acceptor-only DOS that is ASSUMED applicability and is not physical. It becomes meaningful only together with a donor Gaussian, the V2 candidate for replacing Nd_eff.
- **Relevance to the floors:** none (same bound as 7.1).
- **Risk and option:** as in 7.2. `physics_options.poole_frenkel {enabled, a, b}` adds two MATERIAL parameters and one MODELS flag.

### 7.4 Statistics and mobility (FERMI, FLDMOB, concentration-, carrier- and field-dependent mobility)

- **FERMI.** Already ON. Syntax `models fermi` (alias of FERMIDIRAC). VERIFIED: PDF p.78 (Table 2-2), p.109; solver flag `Fermi-Dirac T`. Nothing to add.
- **FLDMOB.**
  - Syntax: `models fldmob` with `material material=IWO vsatn=<cm/s>` (PDF p.225) and `mobility … betan=<>` (PDF p.220). VERIFIED.
  - Relevance: none (COMPUTED). The lateral field is 0.7 V / 20 µm = 350 V/cm, so v = μE ≤ 60 × 350 = 2.1e4 cm/s, far below 1e7 cm/s.
  - Do not spend a launch on it. If ever enabled, set `vsatn`; otherwise the silicon 1.03e7 cm/s is used.
- **Doping-dependent mobility (CONMOB, ANALYTIC, ARORA, KLA).** The manual warns against them in TFT simulations: "Don't use concentration dependent mobility models (CONMOB, ANALYTIC, ARORA, KLA) because they overwrite the low field mobilities set in the MATERIAL statement" (PDF p.896). They also depend on the impurity density, not the carrier density. **Not recommended.**
- **Carrier-density-dependent mobility (IGZO.TOKYO). Recommended.**
  - Syntax, from `tft/tftex21/tftex21_aux.in` lines 124–125: `mobility igzo.tokyo mun=<μ0> mup=0.01 tmun=0 tmup=0 igzo.gamma0=<> igzo.tgamma=<K> igzo.ncrit=<cm⁻³>`.
  - Model: μ_n = μ_n0(T)·(N/IGZO.NCRIT)^(γ/2), with γ = IGZO.TGAMMA/T + IGZO.GAMMA0. Defaults: −0.31, 178.4 K, 1e20 cm⁻³ (PDF p.195–196; MOBILITY parameter list p.1411–1412). VERIFIED for the built-in IGZO.
  - Relevance: this is the native percolation-type model for amorphous oxides (Abe et al., Thin Solid Films 559, 40 (2014), cited in the example). It gives a gate-dependent mobility through n(V_G). That bears directly on the measured exponent γ = 1.13 at 6.3 nm and 0.27 at 13.2 nm, against 0.57 and 0.23 in TCAD, and on the rising μ_FE. Parameters: GAMMA0 and NCRIT **FITTED**. TGAMMA could only be set from the 65/85 °C curves, which we do not have, so it is ASSUMED at the default.
  - UNVERIFIED for our deck:
    - the manual calls it a model "for electrons in InGaZnO material", and whether it applies to a `user.material=IWO` region is unknown;
    - how it interacts with the generator's `material … mun=` is unknown.

    The first run must confirm in `deckbuild.out` → "REGIONAL MOBILITY MODEL SUMMARY" that regions 1 and 2 report the IGZO model rather than "Concentration Independent Mobility". The `chan_mob` probe will show μ(V_G) directly.
  - Constraint: MOBILITY must appear before `solve init` and never between SOLVEs (state file §K).
  - Always declare `tmun=0` (or a labelled value); otherwise the (T/300)^−1.5 factor applies.
- **Perpendicular-field degradation (PRPMOB).**
  - Syntax: `models prpmob` with `mobility gsurfn=<> ecn.mu=<V/cm>`. Model: μ = GSURFN·μ0/√(1 + E⊥/ECN.MU). Defaults GSURFN = 1, ECN.MU = 6.48e4 V/cm (silicon). VERIFIED: PDF p.216–217; flag p.1458.
  - Relevance: an ATLAS proxy for the paper's θ_r roll-off (μ falling with V_G). Our measured μ_FE rises up to 3 V, so this tests that contradiction (§H.1 of the state file); it is not an expected improvement. ECN.MU must be **FITTED**.
  - Whether μ0 is the MATERIAL MUN for a user material is UNVERIFIED; check the mobility summary.
- **CVT / Lombardi, SURFMOB / WATT, YAMAGUCHI, SHIRAHATA, TASCH.** CVT "overrides any other mobility models" (PDF p.196). These models carry silicon inversion-layer parameters. **Not recommended.**
- **Options.**
  - `physics_options.mobility {model: constant|igzo_tokyo|prpmob, …}`. When not `constant`, emit one `mobility material=IWO …` line after the MATERIAL block. Keep `material … mun=` unchanged, so OFF stays byte-identical.
  - The probes and `chan_mobility_vg.dat` already exist.

### 7.5 Gate leakage through HfO2/Al2O3 (FN, direct tunnelling, Schenk, defect-assisted)

- **Syntax.**

  | Model | Syntax | Where in the manual |
  |---|---|---|
  | Fowler–Nordheim, self-consistent | `models fnord [fnholes]` (`fn.cur` = both) with `f.ae=<A/V²> f.be=<V/cm>` | PDF p.288–289. Defaults are Si/SiO₂: F.AE 1.82e-7, F.BE 1.9e8. Examples: `eprom/eprmex01/03`. |
  | Fowler–Nordheim, post-processing | `fnpp` | PDF p.288 |
  | FN localisation | `interface x.min … s.i` | PDF p.289 |
  | Direct quantum tunnelling | `models qtunn.el` (post) or `qtnlsc.el [qtnl.derivs]` (self-consistent) | PDF p.301; works with CARRIERS = 0, 1, 2 |
  | Insulator masses | `material region=3 me.tunnel=<m>` (or `mc=`), region 4 likewise | PDF p.303 |
  | Insulator band parameters | `material region=3 affinity=<eV> eg300=<eV>`, region 4 likewise | Required here (§3.3) |
  | Gate-side mass | `contact name=gate qtunn.cmass=<m>` | PDF p.1158 |
  | Log | `log outf=transfer.log j.tun` | PDF p.1307 |
  | Alternative direct-tunnelling forms | `dt.cur dt.meth=1/2/3` | PDF p.1460 |
  | Schenk image-force model | `schenk` / `schksc` | PDF p.304–305 |
  | Example | `diode/diodeex12.in`: `contact … qtunn.cmass=0.5`, `material oxide mc=0.42 mv=0.2`, `models … qtnlsc.el qtnl.derivs`, `log … j.tun` | — |
  | Defect-assisted insulator leakage (Ielmini TAT) | `doping region=<oxide> uniform tat.trap conc=… e.level=…` with `models itat.sc.el` | PDF p.324–327; example `quantum/quantumex20.in`. UNVERIFIED for a bilayer high-k stack. |

  All rows are VERIFIED unless marked.
- **Relevance** (COMPUTED; all voltage across the stack at V_G = −3 V; E_HfO2 = 1.55 MV/cm, E_Al2O3 = 3.37 MV/cm). FN injection from the TiN gate, J = (q³E²/8πhφ)(m0/m*)·exp[−8π√(2m*)φ^1.5/(3qhE)], over a 24 µm × 1 µm gate:

  | Barrier φ | m* | I (A/µm) | Note |
  |---|---|---|---|
  | 2.7 eV | 0.2 | 2e-38 | — |
  | 2.2 eV | 0.2 | 2e-28 | φ = 4.7 − 2.5 eV for TiN to HfO2: LITERATURE χ, ASSUMED gate work function |
  | 2.2 eV | 0.11 | 7e-21 | — |
  | 1.8 eV | 0.11 | 2e-15 | — |

  - Direct tunnelling through the intact 17 nm bilayer: the WKB factor is ≤ 2e-34.
  - Only an optimistic barrier reaches the 2 nm floor, and FN changes by more than 10 decades between −3 and −0.5 V, whereas the measured floor is flat within 3 % at 13.2 nm.
  - The oxide is the same in all films, so gate leakage cannot give t^3.85.
  - Expected result: a **null test** (`codex_design.md` Q1 reaches the same verdict). Its value is to replace the meaningless I_G = 0 with a bounded I_G for the paper.
- **Solver risk.**
  - Self-consistent tunnelling has "somewhat poor" convergence at high current (PDF p.301); use `qtnl.derivs`.
  - FN uses the field at the semiconductor–insulator segment with a single (F.AE, F.BE) pair, a poor description of a bilayer. Compute F.AE and F.BE from the HfO2 barrier and mass and state that it is an approximation.
  - The insulator defaults must be overridden (§3.3), or the barrier is 4.3–4.7 eV.
- **Option.** `physics_options.gate_tunnelling {enabled, model: qtnlsc|fnord|qtunn_pp, hfo2: {affinity, eg, me_tunnel}, al2o3: {…}, gate_cmass}`. It emits:
  - two MATERIAL lines for regions 3 and 4;
  - one CONTACT line;
  - MODELS flags;
  - ` j.tun` on the LOG line;
  - when FN is chosen, an extra `extract … curve(v."gate", ifn."gate") outfile="ifnvg.dat"`.

  Values: HfO2 χ 2.5 eV, Eg 5.8 eV and Al2O3 Eg 8.8 eV, χ 1.25 eV are LITERATURE (Robertson 2000). Tunnelling masses are LITERATURE ranges, about 0.1–0.4 m0, to be pinned to a cited source before launch; otherwise label them ASSUMED.

### 7.6 Band-to-band tunnelling (BBT.STD, BBT.KL, BBT.NONLOCAL)

- **Syntax:** `models bbt.std` or `bbt.kl` (parameters `bb.a bb.b bb.gamma` on MODELS), or `bbt.nonlocal bbt.nlderivs` with `qtunn.dir` or QTREGION.
- **5.28 support: VERIFIED** (PDF p.80–81, p.275–287). Examples: `tft/tftex05.in` (`bbt.kl bb.b=7.5e6`), `tft/tftex12.in` (`bbt.std`), `quantum/quantumex10/11`.
- **Relevance: none.**
  - Gap 3.1–3.4 eV.
  - The average lateral field is 350 V/cm.
  - No inversion-hole supply and no ambipolar branch in the data.
  - The local models do not check that the potential drop exceeds Eg, so they may create spurious generation where the oxide-side vertical field is high (about 3 MV/cm at the interface at −3 V).
  - With `carriers=1` the generated holes are not transported. That gives an electron source without a hole sink, a numerical artefact rather than physics.
  - The manual itself says BBT.NONLOCAL "is not suitable for application to the unipolar, high-field regions of a device" (PDF p.280), which is exactly our case.
- **Recommendation:** do not include. At most one `carriers=2` + `bbt.nonlocal` diagnostic, if a reviewer demands it.
- **Option:** MODELS flags only, via the `solver.models` override.

### 7.7 Schottky Pd source/drain (WORKFUNCTION, BARRIER, E.TUNNEL, UST, SURF.REC)

- **Syntax:**
  - `contact name=source workfun=<χ_IWO+φ_B> surf.rec [vsurfn=<cm/s>] [barrier alpha=<cm> beta= gamma=] [e.tunnel me.tunnel=<m>] [parabolic] ^ins.ohmic`, and the same for `drain`;
  - `material material=IWO arichn=<A/cm²K²>`;
  - optionally `models ust [ust.bl]` with `material d.tunnel=<cm>`.
- **5.28 support: VERIFIED.**
  - CONTACT parameter list: PDF p.1151–1159.
  - Thermionic emission: PDF p.158–159. Any of SURF.REC, E.TUNNEL, VSURFN, VSURFP or BARRIER enables it.
  - E.TUNNEL "will also enable the SURF.REC boundary condition" (PDF p.1157).
  - UST requires SURF.REC on each contact (PDF p.164).
  - Examples: `diode/diodeex10` (`workfun=5.18 pipinys surf.rec me.tunnel=0.222`), `organic/organicex04` (`surf.rec barrier`), `power/powerex13` (`ust`), `tft/tftex10` (IGZO TFT with `workf=4.33`; its comment notes "without a workfunction the results for ohmic boundaries were not significantly different than the Schottky model").
  - The parameter name is `WORKFUN`. The generator's `workfunction=` is accepted: the solver prints 4.700 for the gate.
- **Parameters.**
  - φ_B **FITTED**, or bounded by LITERATURE: Pd work function 5.12 eV (Michaelson, J. Appl. Phys. 48, 4729 (1977)) minus χ_IWO 3.95–4.27 eV gives 0.85–1.17 eV as the ideal, unpinned value. That would choke the on-current, while In2O3 Fermi-level pinning (charge-neutrality level above E_c) favours near-zero barriers.
  - ARICHN 24.7 COMPUTED (§3.3).
  - me.tunnel 0.206 COMPUTED (DFT).
- **Relevance.** On-state and series-resistance shape, and the V_D dependence of the output curves.
  - It is not a floor mechanism by itself. Reverse thermionic leakage needs a conducting path to the other contact.
  - The mechanism study already showed that a thickness-independent R_sd cannot create the thickness trend (SYNTHESIS: θ_net < 0; 83 % of V_D at 2 nm).
  - Priority: low unless the on-state shape at 6.3 nm motivates it.
- **Solver risk.**
  1. INS.OHMIC: without `^ins.ohmic` the Pd volumes, which touch Air, may stay Ohmic. UNVERIFIED; check the solver's Contacts table, which must show the work function on source/drain.
  2. The mesh at y = −t needs refining (§5).
  3. Thermionic boundaries at a few-nm-thick film edge, combined with the strict `cr.toler` window, may slow or prevent convergence in depletion.
- **Option.** `physics_options.schottky_sd {enabled, barrier_eV, model: te|e_tunnel|ust, me_tunnel, arichn, ins_ohmic: false, mesh_top_nm}`. It emits CONTACT lines after the gate contact, one MATERIAL parameter line, MODELS `ust` if chosen, and the extra y.mesh lines.

### 7.8 Contact resistance

- **Lumped resistance.** `contact name=source resistance=<Ω·µm>` (2D units; state file §K). The generator already emits half of `contacts.series_resistance_ohm_um[t]` per contact, and that is non-zero only for 31.8 nm (FITTED 92 kΩ·µm).
- **Distributed resistance.** `contact name=source con.resist=<Ω·cm²>` (PDF p.1159, §3.5.8 on PDF p.172; example `laser/laserex09.in`: `con.resist=5e-5`). VERIFIED syntax. UNVERIFIED on an electrode that is a metal volume.
- **Method restriction (VERIFIED, PDF p.85).** Lumped and distributed external elements require `METHOD NEWTON CARRIERS=2` in isothermal drift-diffusion. The existing 31.8 nm decks break this. Run_0006 converged; run_0010 produced no export, from an unknown cause.
- **Consequence.** Any contact-resistance option has to run with `carriers=2` (§7.1 conditioning risk), or be replaced by an explicit resistive region. An example is a thin high-resistivity IWO "contact layer" region under each Pd volume, ASSUMED geometry and FITTED resistivity, which stays within `carriers=1`.
- **Relevance.** On-state only. A specific contact resistivity ρ_c would be **FITTED** (no TLM data); a single R_sd cannot create the trend (SYNTHESIS).
- **Option.** `physics_options.contact_resistivity {enabled, ohm_cm2}`. Keep the existing lumped path untouched.

### 7.9 Density gradient and Bohm quantum potential

- **Syntax.**
  - Density gradient: `models quantum` (alias `dg.n`) with `dgn.gamma=<>` `[dglog|dgroot]` `qminconc=<>`. It requires a `solve qfactor=0 … 1.0` ramp after `solve init` (PDF p.837–838; MODELS p.1437, p.1470).
  - BQP: `models bqp.n bqp.ngamma=<> bqp.nalpha=<> bqp.qdir=2`, optionally `method bqp.newton`, then `freezebqpni` on later SOLVEs (PDF p.839–840).
  - Examples: `quantum/quantumex05–09.in` (BQP).
- **5.28 support: VERIFIED** for built-in materials.
  - Example evidence for our combination: `solar/solarex18/solarex18_aux.in` uses `model bqp.n bqp.ngamma=0.4` (line 115) together with continuous `defect reg=… cont …` on `user.default=silicon` materials (lines 77–111). Codex pointed to this example and this audit checked it.
  - The combination with FERMI and electrons-only is still UNVERIFIED for IWO.
- **Relevance and double counting.** The DFT laws already carry confinement as rigid shifts: ΔE_c(t), ΔE_g(t), m*(t), all COMPUTED. DG or BQP would add a second, local quantum shift at both film surfaces, which is double counting unless the DFT ΔE_c is removed in the same run. The physically distinct effect is the dark space: the electron centroid moves about 0.5–1 nm away from the Al2O3 interface, which reduces the effective C_ox at 2 nm.
  - The only clean test is the pair (DFT shift ON, DG OFF) versus (DFT shift OFF, DG ON) at 2 nm.
  - Its γ/α parameters are FITTED, or calibrated against Schrödinger–Poisson, which needs `carriers=0` (PDF p.299).
- **Solver risk.** The QFACTOR ramp adds 5–6 solves. DG is sensitive at low n (`qminconc`). The quantum mass for a user material defaults to silicon and must be set (Table 14-7, PDF p.844). Low priority.
- **Option.** `physics_options.quantum_correction {enabled, model: bqp|dg, gamma, alpha, remove_dft_shift: bool}`. Emits MODELS flags, the QFACTOR SOLVE lines after `solve init` (transfer and ID-VD paths), and the mesh refinement at both film surfaces.

### 7.10 Back-surface fixed charge (exists)

- **Syntax.**
  - `traps.back_surface_fixed_charge_cm2=<Qb>` produces `interface qf=<Qb> x.min=lc x.max=xr y.min=-t-1e-7 y.max=-t+1e-7`, on the exposed IWO/Air channel only (generator lines 250–254).
  - The companion `traps.back_surface_donor_sheet.peak_cm2_eV` creates region 5 (0.25 nm) with a donor Gaussian.
- **Use so far:** runs 0030 and 0035 (Qb, converged) and run_0010 (donor sheet at 31.8 nm, failed after 17.9 s with no export).
- **Note.** A gated back layer cannot give a V_G-flat floor in the thin films. The Debye length at N_D = 2.5e17 cm⁻³ is about 7.3 nm (`codex_design.md`), so the 2 nm film is fully gate-coupled. Keep it as the existing hypothesis option and do not change the defaults.

### 7.11 Ungated parallel conduction: testing the off-floor strip inside the solver

V2 variant D adds G(t)·V_D after the solver, with (W/L)_par = 1.0e-4 µm⁻¹ FITTED on 13.2 nm. Two ways to put it inside ATLAS are proposed.

**(A) Separate two-terminal strip deck. Recommended first.**
- **Deck.** A `mode: strip` in `build_deck()` gives an IWO film of thickness t, length L_p, on the same Al2O3/HfO2 stack, with no gate electrode (the region below HfO2 is insulator), the Pd contacts, the same DEFECTS, Nd_eff(t), Qf and Qb, and the same MODELS/METHOD.
- **Solve.** V_D = 0 → 0.1 → 0.7 V in steps, logged.
- **Cost and reach.** No gate sweep, so a few tens of seconds. It directly predicts the discriminating measurement in §G of the state file: I(0.7 V)/I(0.1 V) = 7 for an ohmic strip, 1.02 for the paper's diffusion form.
- **Floor.** I_floor(t) = I_strip(t) × L_p × (W/L)_par, applied after the solver (geometry ASSUMED; (W/L)_par FITTED on one film).
- **What stays outside the solver.** The physics of n and μ in the strip comes from ATLAS; only the strip width remains a geometric assumption.
- **Syntax.** Only statements already in use (REGION, ELECTRODE, DOPING, MATERIAL, DEFECTS, INTERFACE, SOLVE, LOG, EXTRACT), so the risk is low.

**(B) In-solver parallel strip.**
- **Geometry.** Extend the x-domain past the drain by a gap of at least 3 µm (no gate under it). Add an IWO strip region of thickness t and length L_s ≈ 2 µm on an insulator, with two Pd volumes.
- **Connecting the strip.** The simplest route is to give the two Pd volumes the same names as the main contacts: a second `electrode name=source …` and a second `electrode name=drain …`. VERIFIED:
  - "Multiple electrode statements may have the same electrode name. Nodes that are associated with the same electrode name are treated as being electrically connected" (PDF p.44);
  - "A single current will appear combining the current through both ELECTRODE areas" (PDF p.74).

  This keeps `i."drain"`, the extracts and the runner unchanged. Codex pointed to these pages and this audit checked them.

  The fallback is separate names linked by `contact name=src2 common=source short` (PDF p.74, p.1160–1161; apply the bias only to the COMMON electrode).
- **Width scaling.** Use the region-specific mobility `material region=<strip> mun=<μ·(W/L)_par·L_s>`; MATERIAL REGION= is VERIFIED (PDF p.76). This is an equivalent-conductance device: it scales the mobility, not the electrostatics. Label it ASSUMED.
- **Cost.** About +25–35 % mesh points; the 13.2 nm deck would reach about 16 k, below the about 30 k limit.
- **UNVERIFIED in practice:** that a split Pd electrode made of metal volumes behaves as documented in this full-structure deck. The first launch must check that `i."drain"` includes the strip current; compare with deck A.
- **Risk.** Gate fringing at the strip: keep the gap at least 100× the oxide thickness.
- **Option.** `physics_options.parallel_strip {enabled, mode: separate_deck|in_solver, Ls_um, gap_um, wl_par_per_um}`. When OFF, nothing changes.

**Not usable.** Putting the strip above the Pd/Air (inside the same x-range) is not ungated. Gate–strip coupling through 70 nm of Air, C ≈ ε0/70 nm ≈ 1.3e-7 F/cm², would deplete a 2 nm strip by about 1.7e12 cm⁻² over a 2.5 V swing (COMPUTED).

### 7.12 Summary table

| Model | Deck syntax (5.28) | Supported | Relevance here | Main solver risk | How to expose (OFF by default) |
|---|---|---|---|---|---|
| SRH (already on) | `models srh`; `material taun0 taup0`; DEFECTS sig* | VERIFIED (p.229, p.883) | Floors: none (ratio ≤ 2e-16) | `carriers=2` conditioning | Existing keys; `solver.carriers` |
| TAT | `trap.tunnel mass.tunnel=`; `trap.hurkx`; `tat.nonlocal` | VERIFIED (p.132, p.884, p.1460; tftex12) | Floors: none; small possible change in interface trap occupancy | Nonlinearity; QTREGION placement | MODELS flags |
| Poole–Frenkel | `trap.coulombic`; `material a.trapcoulombic b.trapcoulombic` | VERIFIED (p.885–886) | Inert physically for an acceptor-only DOS | As TAT | MODELS flag + MATERIAL |
| FERMI | `models fermi` | VERIFIED; already on | — | — | — |
| FLDMOB | `fldmob`; `material vsatn`; `mobility betan` | VERIFIED (p.220, p.225) | None at 350 V/cm | — | Skip |
| CONMOB etc. | `conmob`/`analytic`/`arora`/`kla` | VERIFIED; warned against in TFT (p.896) | Wrong physics | Overwrites MUN | Do not use |
| IGZO.TOKYO | `mobility igzo.tokyo mun tmun=0 igzo.gamma0 igzo.tgamma igzo.ncrit` | VERIFIED for IGZO (p.195; tftex21); user material UNVERIFIED | High: μ(n) shape, γ exponents | Check the mobility summary | `mobility` line |
| PRPMOB | `prpmob`; `mobility gsurfn ecn.mu` | VERIFIED (p.216, p.1458) | Tests the θ_r contradiction | μ0 source UNVERIFIED | MODELS + `mobility` |
| FN | `fnord`/`fnpp`; `f.ae f.be`; `log j.tun`; extract `ifn."gate"` | VERIFIED (p.288–289; eprmex01) | Null test; V_G dependence contradicts floors | Single-layer approximation | gate_tunnelling |
| Direct tunnelling | `qtnlsc.el`/`qtunn.el`; insulator `affinity eg300 me.tunnel`; `contact qtunn.cmass` | VERIFIED (p.297–303; diodeex12) | Null test (≤ e^-77) | Insulator defaults; convergence | gate_tunnelling |
| BBT | `bbt.std`/`bbt.kl`/`bbt.nonlocal` | VERIFIED (p.275–287; tftex05, tftex12) | None | Artefacts with carriers=1 | Skip, or one diagnostic |
| Schottky Pd | `contact workfun surf.rec/e.tunnel me.tunnel barrier ^ins.ohmic`; `material arichn`; `models ust` | VERIFIED syntax (p.158–164, p.1151–1159); INS.OHMIC behaviour UNVERIFIED | On-state; not floors | INS.OHMIC; top mesh; convergence | schottky_sd |
| Contact resistance | `contact resistance=` (Ω·µm), `con.resist=` (Ω·cm²) | VERIFIED (p.1153–1159) | On-state only | Requires `newton carriers=2` (p.85); the 31.8 nm decks break this | Existing / contact_resistivity, or a resistive contact-layer region |
| DG / BQP | `quantum dgn.gamma` + QFACTOR ramp; `bqp.n bqp.ngamma bqp.nalpha` | VERIFIED (p.837–840); user material UNVERIFIED | Double counts the DFT shift | Convergence; silicon masses | quantum_correction |
| Back-surface charge | `interface qf= … y=-t` (exists); region 5 donor sheet | VERIFIED (runs 0030/0035) | Hypothesis; cannot make a V_G-flat floor in thin films | — | Existing keys |
| Ungated strip | (A) separate deck; (B) same-name `electrode name=source/drain` volumes + `material region= mun=` | Syntax VERIFIED (p.44, p.74, p.76); behaviour of (B) in our deck UNVERIFIED | Only candidate that gives a flat floor of the right size | Mesh (B) | parallel_strip |

---

## 8. Option architecture that keeps V1/V2 decks byte-identical

1. **Where options live.** A new file `config/physics_options.yaml` with every option `enabled: false`, merged by `load_configs()` into `s['physics_options']`. A missing file means `{}`, i.e. all OFF.
   - Overrides then use the existing `solver.` prefix, for example `solver.physics_options.gate_tunnelling.enabled=1`.
   - No new prefix is needed, so the four copies of the override code (§1) stay untouched.
   - Alternative: add the block to `config/solver.yaml`. It is not a registered file and the decks would not change, but a separate file keeps `max_launches` edits and physics edits apart in history.
2. **Booleans.** Parse with `str(v).strip().lower() in ('1', '1.0', 'true', 'yes', 'on')`. Never use `bool(v)`: `set_dotted()` turns `1` into `1.0` but leaves `false` as a truthy string.
3. **Emission rule.** Each option is one function returning a list of lines, inserted at a fixed place:

   | Place in the deck | What may be added |
   |---|---|
   | After the y.mesh lines | Extra mesh lines |
   | After the electrodes | Strip regions and electrodes |
   | After `material region=4 permittivity=…` | Insulator and IWO MATERIAL parameters, `mobility …` |
   | After `contact name=gate …` | Source/drain CONTACT lines, `contact name=gate qtunn.cmass` |
   | MODELS line | `models {s["models"]}` + `' ' + ' '.join(flags)` only if flags exist |
   | After `solve init` | QFACTOR ramp |
   | LOG line | ` j.tun` |
   | Extract list | `ifnvg.dat` |

   When no option is enabled, every insertion is an empty list, so the text is unchanged. `regress_all_decks.py` must report `unexpected differences 0`.
4. **Provenance.** `material_model_used.json` stores only the material model, and `model_sha256` hashes only that.
   - Add `solver_used.json` and `geometry_used.json` (or an `options` block in `metadata.json`).
   - Add `opts=<sha8>` to the RUN_INDEX notes, but only when an option is on, so the CSV schema stays the same.
   - Every option value in the YAML must carry its label (COMPUTED/MEASURED/LITERATURE/FITTED/ASSUMED) and source, echoed as a `# …` comment line in the deck header like the existing `P(...)` lines. When OFF, nothing is written.
5. **MODELS-only flags can be tried today** without code via `solver.models=fermi srh temp=300 print <flags>`. Use this only for flags that need no MATERIAL or CONTACT companion: TRAP.TUNNEL with MASS.TUNNEL, TRAP.HURKX, PRPMOB with silicon ECN.MU (not meaningful), BBT diagnostics.
   - Gate tunnelling, Schottky contacts, IGZO.TOKYO and the strip need generator code, because of the insulator, contact and mobility lines.

---

## 9. Runner changes needed before the campaign

1. **Timeouts by thickness** (§6). Today 13.2 nm at DOS 384 needs an explicit `"timeout": ≥1500` in every plan entry.
2. **Check that each option is really active.** After the run, parse `deckbuild.out`:
   - "REGIONAL MODEL FLAGS" (tat(local), tat(coulombic), bbt*, Fermi-Dirac, SRH);
   - "REGIONAL MOBILITY MODEL SUMMARY";
   - the "Contacts:" table (work function per electrode).

   Write them to `execution.json` and fail the status (`OPTION_NOT_ACTIVE`) if an enabled option does not appear. Today `scan()` catches only unknown-parameter and syntax errors, not silently ignored settings.
3. **KCL with post-processing tunnelling** (§4). Use self-consistent variants, or exclude the extracted tunnelling current from the KCL sum when a post-processing model is on.
4. **Off-floor metrics.**
   - The `active` mask (measured current > 5 × the floor) deliberately excludes the floor.
   - Non-positive predictions are logged at 1e-40, so `low_current` RMSE is 13–19 decades and carries no information. Every final V1/V2 run has 17–40 non-positive points: the TCAD floor is numerically zero, with noise of about 1e-19 to 1e-18 A/µm.
   - Add `floor_metrics`, computed from `comparison.csv` with no launch:
     - median log10(pred/meas) over V_G ∈ [−2, −0.5] V for pred > 0;
     - the count of non-positive points in that window;
     - the flatness slope d log10 I/dV_G.
   - The solver can resolve floors: the absolute KCL limit is max(1e-17 A, 0.1 × floor), i.e. 4.6e-16 / 1.5e-14 / 6.6e-13 A, and the strict `cr.toler` (1e-17 to 7.88e-16 A) is at least 8× below each floor.
   - Re-scoring old runs with `--rescore` appends RESCORED rows to RUN_INDEX. Leave that to the main session; offline computation from `comparison.csv` is enough for baselines.
5. **Sequential only.** `run_campaign.py --workers 1`. The 2026-09-28 parallel pilot runs 0056/0057 produced no export.
6. **Budget.** RUN_INDEX holds 60 unique run IDs; `max_launches` is 271, so 211 launches remain under the 2026-10-10 approval.

---

## 10. Priorities

1. **Infrastructure, no launch:**
   - option file and emission hooks;
   - boolean parsing;
   - provenance files;
   - activation check, floor metrics and timeouts;
   - `regress_all_decks.py` reporting 0 unexpected differences.
2. **Ungated strip (A):** three cheap strip decks, one per film, each with a V_D step to 0.1 and 0.7 V. This puts the only floor candidate that survives the bounds into ATLAS physics and produces a measurable prediction (ratio 7 vs 1.02).
3. **IGZO.TOKYO:** first one 6.3 nm launch to confirm the model is active for the user material, then a fit of GAMMA0 and NCRIT. Both are FITTED, shared across films if possible, and must be reported as calibration.
4. **One combined null test** at 13.2 nm (`carriers=2`, `trap.tunnel` and `qtnlsc.el` with LITERATURE oxide parameters). Purpose: document that SRH, TAT and gate tunnelling are below the floors inside the solver, as the COMPUTED bounds say, and replace I_G = 0 with a bounded value.
5. **Optional, low priority:** Schottky contacts (only with `^ins.ohmic` and the top-mesh refinement), PRPMOB (θ_r contradiction), DG/BQP (only as the paired confinement test).
6. **Do not spend launches on:** FLDMOB, CONMOB/ANALYTIC/ARORA/KLA, CVT/WATT/YAMAGUCHI, BBT.

---

## 11. Independent cross-check by Codex

**How it was run.** Codex was given a read-only syntax audit of the same manual text and example decks: `codex exec --sandbox read-only`, OpenAI Codex v0.162.0, 2026-10-10. Its answer is kept in the session scratchpad (`codex_syntax_answer.md`). Codex ran no simulator and changed no file.

**Where it agrees with this audit:**
- SRH, CONSRH, TAUN0/TAUP0 and the DEFECTS capture parameters are documented, and DEFECTS recombination (Eq. 15-16) is documented;
- TRAP.TUNNEL and MASS.TUNNEL act on DEFECTS; TRAP.COULOMBIC and TRAP.HURKX are documented;
- FERMI and FERMIDIRAC are both valid;
- FLDMOB with VSATN/BETAN; the CONMOB/ANALYTIC/ARORA/KLA defaults are silicon; CVT overrides other mobility models;
- IGZO.TOKYO is documented and appears in `tftex21`;
- FNORD/FNPP, QTUNN/QTNLSC, Schenk and DT.CUR; J.TUN, and Itnl/Jtnl;
- the BBT models;
- WORKFUN/BARRIER/ALPHA, SURF.REC/VSURFN, E.TUNNEL/ME.TUNNEL, UST with D.TUNNEL;
- RESISTANCE (Ω·µm, 2D) and CON.RESIST (Ω·cm²);
- density gradient (QUANTUM alias DG.N, QFACTOR ramp) and BQP (calibrate against Schrödinger–Poisson with CARRIERS=0);
- MAXTRAPS 1–10;
- no explicit manual recipe exists for an ungated parallel film.

**What Codex added, and what this audit checked:**
- **Same-name ELECTRODE statements** are electrically connected with a combined current (PDF p.44, p.74). Checked; §7.11(B) now uses them.
- **Lumped or distributed elements need `NEWTON CARRIERS=2`** (PDF p.85). Checked; this affects the 31.8 nm decks and §7.8.
- **The tunnelling current is added to the receiving electrode current** (PDF p.289, p.303). Checked; this sharpens the KCL risk of post-processing variants (§4).
- **The "MOBILITY between SOLVEs ignored" rule is not in the manual.** Checked; it is now cited as EMPIRICAL.
- **BQP with continuous DEFECTS on user materials** appears in `solar/solarex18_aux.in`. Checked.
- **The Ielmini TAT model** (`DEFECTS TAT.TRAP`, `ITAT.SC.EL`/`RTAT`, PDF p.320–326) is a documented route to defect-assisted leakage through the insulator.
- **FNCOND** (PDF p.343) handles emission from a conductor region into an insulator.

**Where Codex is UNVERIFIED and this audit agrees:**
- whether the TFT/SRH models strictly require `carriers=2`;
- `NLTUNNEL` and `QTUNN.CMODEL` (not found);
- the `MATERIAL BETAN` spelling (BETAN is a MOBILITY parameter).

**Where this audit goes beyond Codex.** These points come from the solver's own printout or from arithmetic, not the manual:
- the insulator default band parameters (HfO2 χ = 0);
- the silicon-inherited ARICHN, vsatn and tunnelling masses;
- INS.OHMIC on the Pd volumes, which touch Air;
- the COMPUTED leakage bounds;
- the timeout shortfall at 13.2 nm;
- the `set_dotted()` boolean pitfall;
- the byte-identical regression results.

## 12. Evidence

- **Regression harness:** `analysis_2026-10-10_campaign/regress_all_decks.py`. Output on 2026-10-10: identical 48, unexpected differences 0.
- **Leakage and conductance bounds:** `analysis_2026-10-10_campaign/leakage_bounds.py`.
- **Solver output:** `results/runs/run_0040_13p2_recal_dos384_13p2/deckbuild.out` (MODELS PRINT section: material parameters, model flags, mobility summary, contacts) and `igvg.dat` (I_G = 0).
- **Manual:** `report_latex_full/tools/atlas_manual_pages.txt` (pages as cited). DeckBuild extract variables (`ifn."<electrode>"`): `C:\sedatools\lib\deckbuild\5.0.10.R\docs\deckbuild_users1.pdf`, printed p.149–150.
- **Examples:** `C:\sedatools\examples\deckbuild\4.2.5.R\` → `tft/tftex05`, `tftex10`, `tftex12`, `tftex21`; `diode/diodeex10`, `diodeex12`; `eprom/eprmex01`; `quantum/quantumex05–11`, `quantumex20`; `laser/laserex09`; `power/powerex13`; `organic/organicex04`; `solar/solarex18`.
- **Solver output for the 31.8 nm decks:** `results/runs/run_0006_31p8_v1_stage5_shared_qf/device.in` and `deckbuild.out` (lumped `resistance=46000` with `carriers=1`).
- **Run times:** `results/RUN_INDEX.csv`, finished rows of runs 0001–0060.
