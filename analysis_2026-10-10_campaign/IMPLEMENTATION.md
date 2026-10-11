# Implementation of the 2026-10-10 campaign: generator options, model V3, campaign plans

**Nothing was launched.** No `deckbuild.exe`, no `run_campaign.py`, and no `run_atlas.py` launch (not even `--rescore`). The only code run was:
- deck-text generation through `build_iwo_decks.build_deck()` (no `subprocess` or `deckbuild` in that module);
- the regression harnesses;
- the new check scripts in this folder;
- one mock test of the new strip runner path. In that test `Popen`, run reservation and RUN_INDEX writes were patched out, outputs went to the session scratchpad, and the RUN_INDEX hash was unchanged before and after.

No file in `data/`, `results/RUN_INDEX.csv`, `results/runs/*` or any registered file was changed. Nothing was committed or pushed. Codex was used twice, read-only (§9).

**Labels.**
- COMPUTED: our DFT, file cited.
- MEASURED: measured on the target devices.
- LITERATURE: published value, cited.
- FITTED: fitted; the data are named.
- ASSUMED: chosen without data.
- CALCULATED: closed-form formula applied to labelled inputs.
- MODEL: a 2-parameter fit to COMPUTED points.

Every FITTED value in the new files is named as fitted. The values in V3 are the S4 **start** values. Calibration is never called validation.

---

## 1. Bottom line

1. **Every model in the campaign design is now a generator option, OFF by default.**
   - The options live in `config/physics_options.yaml`, with every option off.
   - A run switches an option on only through the matrix override (`solver.physics_options.<option>.<key>=…`), which is recorded in `execution.json`.
   - With all options OFF, V1 and V2 decks are byte-identical. The documented harness gives IDENTICAL for runs 0038, 0039, 0040, 0012 and 0058; the full harness gives `identical 48; unexpected differences 0` (§7).
2. **`config/iwo_material_model_v3.yaml` wires the DFT inputs, each value labelled and sourced.** Selection is the same as for V2: `$env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"`.
   - For all 98 runnable matrix entries, V3 + overrides and V2 + overrides give **identical solver statements**; only header comments differ.
   - V3 without overrides reproduces the matrix start values within 1.1e-4 (relative).
3. **Campaign plan files reproduce `campaign_matrix.json` exactly.** They are `config/campaign_C10_*.json`.
   - All 181 entries are copied verbatim, in matrix order, and tagged with their stage.
   - 6 runnable plans hold the 98 fixed entries.
   - 5 `.template.json` files hold the 83 adaptive or after-calibration entries.
   - There is also a 10-run minimum-set plan.
   - Stop rules are written into the plans as fields. `run_campaign.py` cannot enforce them, so §6 gives the manual procedure.
4. **Sample decks.**
   - Written to `sample_decks/`: the 2 smoke runs and 3 representative later runs.
   - Written to `sample_decks/extra/`: 6 more decks covering the remaining new statement types.
   - Every new or changed solver statement is mapped to the GENERATOR_AUDIT syntax reference in `sample_decks/NEW_STATEMENTS.md`, with **0 unreviewed**.
5. **Found during implementation: the matrix contains solver-identical duplicates.** S3-04 (bulk-only tail at 2 nm) and S3-07 (50:50 tail at 2 nm) give the same solver statements as S0-01. The 2 nm total N_t is the same by construction, so 2 launches can be saved (§6.4).

---

## 2. Files changed

### 2.1 Changed

Line counts are from `implementation_2026-10-10.diff`, which is in this folder.

**`scripts/build_iwo_decks.py` (+198 / −26)**
- `load_configs()` merges `config/physics_options.yaml` into `s['physics_options']`. A missing file means all options are OFF.
- New helpers:
  - `on()`: explicit boolean parsing (`set_dotted` keeps `'false'` as a string, which is truthy);
  - `pline()`;
  - `campaign_options(p, s, t)`: one function that returns the option lines, MODELS flags and mesh requests. Its lists are empty when every option is OFF.
- `material_at()`: if a thickness has no listed `mu_band` and the model has `mu0_cm2Vs.shared_law` (V3 only), it uses μ∞·(m_ref/m*(t))/(1+ℓ/t).
- `build_deck(..., strip=False)`: options are inserted only at the places fixed by GENERATOR_AUDIT §8.3:
  - option header lines before the closing `#===` line;
  - the oxide y-mesh spacing for gate tunnelling;
  - the top-of-film y-mesh lines for Schottky contacts;
  - strip regions, electrodes, doping and DEFECTS;
  - TAT doping after the donor doping;
  - option parameters continuing the IWO `material` statement (`arichn`, `ml mt1 mt2`);
  - oxide `material region=3/4 …`, the strip `material region=8/9 mun=…` and the `mobility …` line after `material region=4 permittivity` (before `solve init`);
  - the gate `contact … qtunn.cmass` suffix and the Schottky source/drain `contact` lines;
  - MODELS flags appended to the existing line;
  - ` j.tun` on the LOG lines, in both transfer and ID-VD modes;
  - the `ifn."gate"` extract.

  The separate strip deck (`strip=True`) has no gate volume or electrode, a domain ending at the HfO2 bottom, and a stepped drain sweep with its own extracts. Its drain steps are validated by `strip_points()`: whole positive steps, and 0.1 and 0.7 V must be included.
- Guards that raise `ValueError`:
  - BQP together with a non-zero DFT ΔE_c (double counting);
  - in-solver strip together with IGZO.TOKYO;
  - in-solver strip together with a back-surface sheet or Q_b;
  - a strip deck together with gate options;
  - Schottky together with a lumped series R;
  - a model that is not self-consistent tunnelling.

**`scripts/run_atlas.py` (+80 / −0)**
- New `execute_strip()`, a sibling of `execute_output()`.
- The deck is built, and its drain points validated, **before** a run ID is reserved.
- It writes `strip_iv.csv` and stores I(0.1 V), I(0.7 V), their ratio and G in `execution.json['strip']`.
- Statuses: LAUNCH_ERROR, TIMEOUT, SIMULATOR_ERROR, INCOMPLETE_RUN (nonzero exit or no ATLAS completion), NO_EXPORT, INCOMPLETE_EXPORT (malformed rows, conflicting duplicates, non-finite values, mismatched or missing drain points), SIGN_REVERSAL, KCL_FAILED, REAL_ATLAS_STRIP. Each one writes `execution.json` and a closing RUN_INDEX row.
- The KCL limit is the existing rule applied to |I_D + I_S|.
- Existing functions are unchanged.

**`scripts/run_campaign.py` (+7 / −2)**

The line counts of all three scripts are against the copies taken before any edit, after the last fix.
- An entry with `"mode": "strip"` calls `execute_strip`. An entry-level `vd_segments` is rejected in strip mode.
- `summarize()` copies `execution.json['strip']`.
- Existing modes (transfer, output) and the resume and budget logic are unchanged.

**`analysis_2026-10-10_campaign/regress_all_decks.py` (+3)**
- Rebuilds strip-mode runs with `strip=True`, so the gate harness stays valid once strip runs exist.

### 2.2 New

**Config files**

| File | Content |
|---|---|
| `config/physics_options.yaml` | Every option, all OFF, each value labelled, with manual and example references |
| `config/iwo_material_model_v3.yaml` | Model V3 (§4) |
| `config/campaign_C10_S0a_smoke.json`, `…_S0b_smoke.json` | S0-01 and S0-02, one per file (stop-on-failure, §6) |
| `config/campaign_C10_S1_baselines.json` | 7 |
| `config/campaign_C10_S2_offfloor.json` | 17, including 4 strip-mode entries |
| `config/campaign_C10_S3_branches.json` | 27 |
| `config/campaign_C10_S4a_spacefilling.json` | 45, valid as written only if S3 adopts no branch |
| `config/campaign_C10_MIN10.json` | The 10-run minimum set (CAMPAIGN_DESIGN §9) in launch order |
| `config/campaign_C10_S4b_adaptive.template.json`, `…_S4cd_confirm.template.json`, `…_S5_loo.template.json`, `…_S6_sensitivity.template.json`, `…_S7_31p8.template.json` | The 83 entries with `{generated}` / `{frozen model}` tokens. They are not runnable: a token makes `execute()` fail in `split('=')` or `set_dotted` before `reserve()`, so no launch is consumed. |

**Scripts in this folder** (no launch in any of them)

| File | What it does |
|---|---|
| `campaign_tools.py` | Builds an entry's deck exactly as `execute`/`execute_strip` would |
| `make_campaign_configs.py` | Writes and verifies the plans. `--check` only verifies. `--remaining PLAN SUMMARY… [--skip ID…]` writes a trimmed plan. |
| `check_v3_equivalence.py` | Checks V2 vs V3 solver statements for all fixed entries, the S0-01 header values and the V3 start values |
| `make_sample_decks.py` | Writes `sample_decks/` and `NEW_STATEMENTS.md` |
| `post_run_checks.py` | For the main session after each launch: the activation parser (OPTION_NOT_ACTIVE) and the off-floor metrics of CAMPAIGN_DESIGN §7.1. It writes `post_run/<run_id>.json` and never writes into `results/`. Tested read-only on runs 0040 and 0058; the test outputs were removed. |

**Other outputs in this folder**
- `sample_decks/` (5 decks), `sample_decks/extra/` (6 decks), `sample_decks/NEW_STATEMENTS.md`;
- `implementation_2026-10-10.diff`;
- `codex_impl_review_prompt_2026-10-10.md` / `codex_impl_review_2026-10-10.md`;
- `codex_impl_recheck_prompt_2026-10-10.md` / `codex_impl_recheck_2026-10-10.md`.

---

## 3. Options (all OFF in `config/physics_options.yaml`)

| Option key (`solver.physics_options.…`) | Design item | Emits only when ON | Labels | Syntax reference |
|---|---|---|---|---|
| `nc300_override_cm3[t]` | C2 | `nc300=` replaced at listed t; OPTION header line | CALCULATED quasi-2D N2D/t from m*(2 nm) (LITERATURE 0.208 + DFT Δm law); single-subband rule from COMPUTED E21 = 0.7191 eV | existing MATERIAL parameter |
| `nt_bulk_cm3` | C3 | Nt(t) = Nt2·(2/t)^α + Nb; header line | FITTED branch (S3 placement) | existing DEFECTS |
| `gate_tunnelling.{enabled, model qtnlsc\|fnord, set nominal\|worst, f_ae, f_be, oxide_mesh_nm, gate_qtunn_cmass, sets.*}` | C4 | `material region=3/4 affinity eg300 me.tunnel`; `contact name=gate … qtunn.cmass=` (QTNLSC); MODELS `qtnlsc.el qtnl.derivs` or `fnord f.ae f.be`; `log … j.tun`; `extract … ifn."gate"` (FN); oxide y-mesh min(current, 0.25 nm) | nominal: χ/E_g LITERATURE (Robertson 2000), masses ASSUMED in LITERATURE ranges. worst: ASSUMED leakage-maximising scenario. F.AE/F.BE CALCULATED (Lenzlinger–Snow). cmass ASSUMED (default 1). | audit §7.5; PDF p.288–289, p.301–303; diodeex12, eprmex01 |
| `oxide_tat.{enabled, region, conc_cm3, e_level_eV, sign_cm2, sigp_cm2}` | C9 | `doping region=4 uniform tat.trap conc acceptor sign sigp e.level`; MODELS `itat.sc.el`; `j.tun` | ASSUMED high-defect bound; σ ASSUMED (quantumex20 value 1e-13 cm²); E.LEVEL measured from the oxide E_c (manual, DOPING) | audit §7.5; PDF p.323–327; quantumex20 |
| `schottky_sd.{enabled, barrier_eV, lowering, e_tunnel, top_mesh_nm, richardson_A_cm2K2}` | C5 | `contact name=source/drain workfun=χ(t)+φ_B surf.rec [barrier] [e.tunnel me.tunnel=m*(t)] ^ins.ohmic`; `arichn=120.17·m*(t)` on the IWO MATERIAL statement; y-mesh: 0.1 nm at −t, 0.2 nm at −t+3 nm, bulk spacing at −t+6 nm when inside the film | φ_B from an ASSUMED grid, FITTED once selected; ARICHN and me.tunnel CALCULATED | audit §7.7; PDF p.158–161, p.1151–1159; diodeex10, organicex04 |
| `mobility.{model constant\|igzo_tokyo, gamma0, tgamma, ncrit}` | C6 | `mobility material=IWO igzo.tokyo mun=MUN(t) mup tmun=0 tmup=0 igzo.gamma0 igzo.tgamma igzo.ncrit` before `solve init` | GAMMA0 FITTED if adopted (start −0.31 LITERATURE default / +0.30 ASSUMED); TGAMMA LITERATURE default; NCRIT ASSUMED | audit §7.4; PDF p.195–196; tftex21 |
| `quantum.{model none\|bqp, mass, ngamma, nalpha, qdir, set_mass}` | C7 | MODELS `bqp.n bqp.ngamma bqp.nalpha bqp.qdir`; `ml=mt1=mt2=mass` on the IWO MATERIAL statement | γ/α ASSUMED (ATLAS defaults); mass 0.139 MODEL or 0.2543 CALCULATED | audit §7.9; PDF p.835–840; quantumex05, solarex18 |
| `strip.{mode none\|in_solver, L_p_um, vd_segments, gap_um, L_s_um, pad_um, wl_par_per_um, qf_on_strip, bottom_material}`, plus campaign `"mode": "strip"` | C8 | Separate deck: no gate, drain 0 → 0.1 → 0.7 V, extracts `idvd_strip.dat`/`isvd_strip.dat`. In-solver: regions 8 (IWO bulk), 9 (IWO 0.25 nm interface layer with the D_it sheet), 10/11 (Air), 12 (insulator under HfO2 outside the gate); same-name Pd pads; `material region=8/9 mun=MUN·(W/L)_par·L_s`; Q_f on the strip if `qf_on_strip` | geometry ASSUMED; (W/L)_par FITTED (V2 value 1e-4/µm as placeholder) | audit §7.11 A/B; PDF p.44, p.74, p.76 |
| existing `solver.models=…`, `solver.carriers=…`, `bulk_reference.srh_tau_s`, `traps.bulk_acceptor_tail.capture_cm2` | — | SRH/TAT bounds, Boltzmann, two carriers | as in the matrix | audit §7.1–7.2 |

**Acceptance in the strip deck.** The transfer-deck switch rule is applied to the expected strip current, floor/(L_p·(W/L)_par):
- strict (XANDRNORM) at or below 1e-9 A/µm, which covers 2.0 and 6.3 nm;
- default above that, which covers 13.2 nm (3.3e-9 A/µm).

---

## 4. Model V3 (`config/iwo_material_model_v3.yaml`)

It has the same schema as V2, so `material_at()` reads it unchanged.

| Quantity | V3 value | Label and source |
|---|---|---|
| ΔE_g(t) | 0.81431·t^−1.31518 eV | FITTED to COMPUTED DFT points (H–H 0.695 / 0.930 / 1.962 nm; `dft_inputs.json` laws.dEg_eV, films.*.dEg_PBE_eV) |
| ΔE_c(t) | 0.70147·t^−1.31669 eV (fit3) | FITTED to COMPUTED DFT points (`dft_inputs.json` laws.dEc_eV.fit3) |
| m*(t) | 0.208 + 0.11116·t^−1.26387 m0 | 0.208 LITERATURE (Stokey 2021) + increment FITTED to COMPUTED points (laws.dm_m0) |
| NC300 | 3-D formula (CALCULATED); quasi-2D 1.373e19 at 2 nm recorded as `quasi2d_reference_cm3` | Applied **only** through the option, by the pre-registered rule. S1-05 and the no-confinement runs need the 3-D default. |
| N_t | Nt2 = 2e19, α = 1 (N_s = 4e12 cm⁻², N_t = N_s/t) | FITTED shared (S4 start = V1 FITTED 2 nm anchor) |
| W_TA | 0.040 eV | FITTED shared (start) |
| N_D | 2.5e17 cm⁻³, constant (tc = 1e9 nm) | FITTED V1 donor amplitude, kept fixed; constant thickness dependence ASSUMED (corrected after review, §11); W fully ionised is COMPUTED (`dft_inputs.json` W.conclusion_for_TCAD) |
| μ_band | 17.6897 / 44.1956 / 63.2597 cm²/Vs (MUN 12.977 / 40.261 / 60.539), plus `shared_law` μ∞ = 100.005, ℓ = 7.248 nm, m_ref = 0.208 | FITTED shared law (start values); mass factor CALCULATED |
| Q_f | 1.38345e12 cm⁻² | FITTED shared (start = V2 FITTED) |
| E_g,bulk, χ_bulk | 3.05, 4.3 eV | LITERATURE (Fan 2021) |
| ε_IWO | 9.3 | MEASURED (Januar 2026 SI Fig. S1) |
| Deep Gaussian, D_it sheet, σ, τ, N_V, μ_p, gate work function | as V2 | ASSUMED |

---

## 5. Plans versus the matrix

- `make_campaign_configs.py` verifies the plans. For every entry, `id, thickness, label, overrides, timeout, purpose, mode` must equal the matrix `campaign_entry`. The union of stage plans and templates must equal the matrix order, 181 entries. MIN10 must equal the design list.
- Annotation fields are ignored by `run_campaign.py`: `stage`, `matrix_status`, `requires_code`, `depends_on`, `pre_registered_expectation`, `params_rule`, `min_set_rank`, `solver_identical_to`. The same holds for the top-level `runnable`, `model_file_env`, `global_rules`, `stop_rules`.
- The matrix's `model_file_env` names V2. The plans recommend V3. Both give the same solver statements for every fixed entry (`check_v3_equivalence.py`). V3 only fixes the header labels. Launching with V2 is equally valid if exact matrix wording is preferred.

---

## 6. How to launch, stage by stage (main session; PowerShell 7)

### 6.1 Once per shell

```powershell
Set-Location "C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1"
$py = "C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_ATLAS_Model_claude\.venv\Scripts\python.exe"
$env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"
# gates (no launch): all three must pass before the first launch and after any code change
& $py analysis_2026-10-10_campaign/regress_all_decks.py              # last line: identical 48; unexpected differences 0
& $py analysis_2026-10-10_campaign/check_v3_equivalence.py           # 98 identical; S0-01 header OK
& $py analysis_2026-10-10_campaign/make_campaign_configs.py --check  # verbatim and in matrix order: YES
function RunDir($plan, $id) { ((Get-Content "results/campaigns/$plan.json" | ConvertFrom-Json).runs | Where-Object id -eq $id).run_dir }
```

### 6.2 Stages

All launches are sequential (`run_campaign.py` without `--workers`). After each plan, run `post_run_checks.py` on every new run, then apply the stop rules below, which are also written in each plan's `stop_rules` field.

**S0a (1 launch, ≤ 0.33 h)**
```powershell
& $py scripts/run_campaign.py config/campaign_C10_S0a_smoke.json
& $py analysis_2026-10-10_campaign/post_run_checks.py (RunDir campaign_C10_S0a_smoke S0-01)
```
STOP (fix the code) if any of these holds:
- the status is not `REAL_ATLAS_SCORED`;
- post_run_checks reports `OPTION_NOT_ACTIVE` (exit 1), or `UNVERIFIED` (exit 3) until `deckbuild.out` has been read by hand (§11.3);
- KCL fails.

**S0b (1 launch, ≤ 0.5 h)**
```powershell
& $py scripts/run_campaign.py config/campaign_C10_S0b_smoke.json
& $py analysis_2026-10-10_campaign/post_run_checks.py (RunDir campaign_C10_S0b_smoke S0-02) --control (RunDir campaign_C10_S0a_smoke S0-01)
```
Required: I_G non-zero (activation check) and KCL passes. At most 3 reserve launches go to S0 repairs, after which the fallback of the plan's stop rule applies.

**S1 (7 launches, ≤ 4.4 h)**
```powershell
& $py scripts/run_campaign.py config/campaign_C10_S1_baselines.json
```
Apply the S1 rules with `campaign_extract.py compare` and `profile_shared.py check` (commands in §11.7):
- S1-03 / S1-04 numerics: 0.01 dec / 5 mV / 3 mV/dec;
- S1-05: +40 … +70 mV relative to S0-01;
- S1-06: 1e-3 relative above 1e-14 A/µm;
- S1-07: within 0.01 dec of transformed S0-01.

**S2 (17 launches, ≤ 11.4 h)**
```powershell
& $py scripts/run_campaign.py config/campaign_C10_S2_offfloor.json
```
The matched controls for `post_run_checks.py --control` are:
- S0-01 for the 2.0 nm runs;
- S1-01 for 6.3 nm;
- S1-02 for 13.2 nm;
- S1-06 for the two-carrier runs S2-01 and S2-02.

S2-03 (2.0 nm, two carriers) has no two-carrier control. Use S0-01 and note it. Strip runs report the ratio in `execution.json['strip']`. S2-12 / S2-13 also need `--gate-control` = S2-04 / S2-06 to identify ITAT (§11.3).

**S3 (27 launches, ≤ 15.1 h; 25 if the duplicates are skipped, §6.4)**
```powershell
& $py analysis_2026-10-10_campaign/make_campaign_configs.py --remaining config/campaign_C10_S3_branches.json --skip S3-04 S3-07   # only if approved
& $py scripts/run_campaign.py config/campaign_C10_S3_branches_remaining.json    # or config/campaign_C10_S3_branches.json
```
The branch decision follows the plan's rules:
- ≥ 0.03 dec, with no film worse by more than 0.03 dec;
- activation confirmed;
- at most two branches;
- S3-27 within 0.01 dec for IGZO;
- one reserve launch for a Schottky native check.

**S4a (45 launches, ≤ 27.9 h)**

Valid as written only if S3 adopted no branch. In that case, first drop S4A-01-* (solver-identical to S0-01 / S1-01 / S1-02):
```powershell
& $py analysis_2026-10-10_campaign/make_campaign_configs.py --remaining config/campaign_C10_S4a_spacefilling.json --skip S4A-01-2p0 S4A-01-6p3 S4A-01-13p2
& $py scripts/run_campaign.py config/campaign_C10_S4a_spacefilling_remaining.json
```
If a branch is adopted, regenerate the S4a candidates with that branch's overrides (`make_campaign_matrix.py`, then this script) before launching.

**S4b, S4c/S4d, S5, S6, S7**
1. Copy the `.template.json`.
2. Replace every `{generated}` / `{frozen model}` / `<value>` token with the profiled values. This includes S6-27's `solver.physics_options.strip.wl_par_per_um` (the fitted (W/L)_par), and the S7 entries.
3. Save without `.template`.
4. Run `make_campaign_configs.py --check`. It still checks the templates. Then check the new file with `run_campaign.py` only after reading it.

### 6.3 The 10-run minimum set (alternative to S0–S3)

```powershell
& $py scripts/run_campaign.py config/campaign_C10_S0a_smoke.json        # then the S0 checks
& $py scripts/run_campaign.py config/campaign_C10_S0b_smoke.json        # then the S0 checks
& $py analysis_2026-10-10_campaign/make_campaign_configs.py --remaining config/campaign_C10_MIN10.json results/campaigns/campaign_C10_S0a_smoke.json results/campaigns/campaign_C10_S0b_smoke.json
& $py scripts/run_campaign.py config/campaign_C10_MIN10_remaining.json  # S1-01, S1-02, S2-01, S2-08, S2-14, S2-15, S1-07, S3-12
```

`run_campaign.py` resumes only per plan file. So before any stage plan that follows MIN10, trim it:
```powershell
& $py analysis_2026-10-10_campaign/make_campaign_configs.py --remaining config/campaign_C10_S1_baselines.json results/campaigns/campaign_C10_MIN10_remaining.json
```
Do the same for S2 and S3.

### 6.4 Stop rules the runner cannot express (apply manually)

`run_campaign.py` stops only at the launch budget. It records a failed launch and continues, and on resume it re-runs entries without a `run_dir`, so a failed launch is retried and costs a second launch. The following are left to the main session:

1. **Stop on any smoke failure.** Expressed by splitting S0 into two single-entry plans (S0a and S0b).
2. **The numerics limits, the S1-05/06/07 decisions, the S3 adoption rule, and the S4a abort** (√J > 0.30 dec with systematic residuals: no S4b, no per-film rescue). These are decided between plan files from `results/campaigns/<plan>.json`, the `execution.json` fit metrics and `post_run_checks.py`.
3. **S2: a nominal or SRH null test giving floor-scale current means stop and audit.** The S2 plan does not stop by itself. Read each S2 result before trusting the next ones; kill the plan run if needed. Interrupting `run_campaign.py` is safe: the summary is rewritten after every launch.
4. **S4b early stop** (3 candidates each improving by < 0.01 dec) and the **S5 fold logic.** These are decided when the templates are filled.
5. **Early exit for the whole campaign** (S4 failed and confirmed by S5 on ≥ 2 folds → S6 cut to 10 launches).
6. **Duplicates.** S3-04 and S3-07 give the same solver statements as S0-01 (`solver_identical_to` in the plan). The bulk-only and 50:50 tail variants are normalised to the same total N_t at 2.0 nm, so they differ only at 6.3 and 13.2 nm. Skipping them saves 2 launches and loses nothing. **This is a design choice for the main session/user; the plans keep them so that they reproduce the matrix.** S4A-01-* are the documented reuse case.

### 6.5 Budget

| Stage | Launches | Running total | Timeout sum |
|---|---:|---:|---:|
| S0 | 2 | 2 | 0.8 h |
| S1 | 7 | 9 | 4.4 h |
| S2 | 17 | 26 | 11.4 h |
| S3 | 27 | 53 | 15.1 h |
| S4a | 45 | 98 | 27.9 h |
| S4b–d | 24 | 122 | 15.0 h |
| S5 | 30 | 152 | 18.6 h |
| S6 | 27 | 179 | 16.1 h |
| S7 | 2 | 181 | 1.7 h |

181 planned + 19 reserve = 200. After review (§11.2) `max_launches` is 260 (= 60 used + 200), so exactly 200 remain, and `run_campaign.py` also caps C10 launches at 200. Typical wall time is about 43 h (CAMPAIGN_DESIGN).

---

## 7. Regression output (verbatim)

Run as documented: `regress_decks.py <run ids>`, with `IWO_MODEL_FILE` unset for the V1 runs and set to V2 for run_0058. This is the final run, after all code changes:

```
run_0038: IDENTICAL  sha new 59e8fa855bb5c4c1 old 59e8fa855bb5c4c1
run_0039: IDENTICAL  sha new cb85ffe60e81b27e old cb85ffe60e81b27e
run_0040: IDENTICAL  sha new 50ec48626ae5de2f old 50ec48626ae5de2f
run_0012: IDENTICAL  sha new baae40d5416c4c5c old baae40d5416c4c5c
run_0058: IDENTICAL  sha new 4e70e7b4d8d817c3 old 4e70e7b4d8d817c3
```

The full gate, `regress_all_decks.py` (all 49 final-form runs, V1/V2 model taken from RUN_INDEX), ends with:
```
identical 48; unexpected differences 0
```
The one non-identical run is the known run_0027 (the documented mesh fix of 2026-09-27).

---

## 8. Other checks (no launch)

**`check_v3_equivalence.py`:**
```
planned_fixed entries 98: identical solver statements V2 vs V3 98; differing 0; header-comment-only differences 98
S0-01 header values {'chi_eV': '4.01839', 'Nc_cm3': '1.373e+19', 'mu0': '12.977', 'Qf_cm2': '1.38345e+12'} vs {...} -> OK
V3 no-override  2.0 nm: max relative deviation from matrix derived_per_film 4.7e-05 (Nc300_3d_cm3)
V3 no-override  6.3 nm: max relative deviation from matrix derived_per_film 1.1e-04 (Nc300_3d_cm3)
V3 no-override 13.2 nm: max relative deviation from matrix derived_per_film 1.9e-05 (Nc300_3d_cm3)
```

**`make_campaign_configs.py`:**
```
plans verified: 181 matrix entries in 6 runnable plans (98 entries) + 5 templates (83 entries); verbatim and in matrix order: YES
```

**All 98 runnable entries build without error.** That includes every option path: strip mode, Schottky, IGZO, BQP, gate tunnelling, oxide TAT and the tail branches. The 6 guard paths raise as intended.

**Booleans.** `enabled=false` and `enabled=0` leave the decks unchanged.

**Estimated mesh size** (ATLAS grading formula, calibrated on the solver's own counts of 9594 / 10179 / 12051 nodes, within 5 %):

| Deck | Estimated nodes |
|---|---|
| S0-02 (oxide 0.25 nm) | 13.7k |
| S2-11 (oxide 0.125 nm) | 21.5k |
| S2-08 / S2-13 | 16.0k |
| S3-19 (Schottky, 13.2 nm), after the bulk-spacing line | 14.0k (was 20.5k) |
| S6-27 (in-solver strip) | about 26k |

All are below the about 30k limit of the 32-bit build.

**Mock test of `execute_strip`** (patched `Popen`, `reserve` and `append`; scratchpad only; RUN_INDEX unchanged):

| Case | Status |
|---|---|
| ohmic | REAL_ATLAS_STRIP, ratio 7.0 |
| truncated export | INCOMPLETE_EXPORT |
| wrong sign | SIGN_REVERSAL |
| KCL violation | KCL_FAILED |
| missing source export | NO_EXPORT |
| conflicting duplicate row | INCOMPLETE_EXPORT |
| malformed row | INCOMPLETE_EXPORT |
| exit code 1 | INCOMPLETE_RUN |
| `Popen` failure | LAUNCH_ERROR |
| drain grid without 0.7 V | ValueError before any reservation (no run directory) |

Each failure writes `execution.json` and a closing RUN_INDEX row.

---

## 9. Sample decks and syntax check

| Deck | Film | What it shows |
|---|---|---|
| `sample_decks/S0-01_c10_s0_01_2p0.in` | 2.0 nm | Smoke 1: fit3 laws, quasi-2D NC300 1.373e19, N_t = N_s/t, constant N_D, shared Q_f, MUN 12.977, tmun = 0. Same solver statements as the V2 baseline form; no new statement type. |
| `sample_decks/S0-02_c10_s0_02_2p0.in` | 2.0 nm | Smoke 2: QTNLSC worst-case set. HfO2 y-mesh 0.25 nm, oxide MATERIAL lines, gate `qtunn.cmass`, MODELS `qtnlsc.el qtnl.derivs`, `log … j.tun`. |
| `sample_decks/S2-14_c10_s2_14_13p2_strip.in` | 13.2 nm | Separate ungated strip deck: no gate, Neumann bottom, default acceptance by the switch rule, drain 0 → 0.1 → 0.7 V. |
| `sample_decks/S3-12_c10_s3_12_6p3.in` | 6.3 nm | `mobility material=IWO igzo.tokyo …` |
| `sample_decks/S3-17_c10_s3_17_2p0.in` | 2.0 nm | Schottky 0.2 eV: `contact … workfun=4.21839 surf.rec barrier e.tunnel me.tunnel=0.25429 ^ins.ohmic`, `arichn=30.558`, top mesh 0.1 nm |

`sample_decks/extra/` holds:
- S2-08 (QTNLSC worst, 13.2 nm);
- S2-10 (FNORD + `ifn."gate"`);
- S2-12 (QTNLSC nominal + oxide TAT);
- S3-07 (50:50 tail; identical to S0-01, see §6.4);
- S3-24 (BQP with the DFT shifts off);
- S6-27 (in-solver strip). S6-27 is **illustrative**: it is built at the start values with the placeholder (W/L)_par.

`sample_decks/NEW_STATEMENTS.md` lists every new or changed solver statement against the same-film baseline, with its syntax reference (GENERATOR_AUDIT section, manual PDF page, installed example). **0 unreviewed.**

Statements whose syntax is VERIFIED but whose behaviour with our deck is **UNVERIFIED** (to be checked on the first run with `post_run_checks.py`):
- IGZO.TOKYO on `user.material=IWO`;
- `^ins.ohmic` on Pd volumes that touch Air;
- BQP reading ML/MT1/MT2 as its mass tensor;
- QTNLSC/FNORD injection from the Conductor-region gate;
- ITAT in an HfO2/Al2O3 bilayer;
- `material region=8/9 mun=` on user-material regions;
- same-name split electrodes in this structure;
- `extract ifn."gate"`, documented in the DeckBuild manual but not in the ATLAS text.

### Codex review (read-only, codex-cli 0.162.0)

**First pass** (`codex_impl_review_2026-10-10.md`):
- OFF = unchanged: OK, including paths the 48-deck harness does not exercise.
- Statement syntax and order: OK, with a RISK on `ifn."gate"`.

**Fixes adopted from the first pass:**
- **In-solver strip.** It lacked the interface-sheet layer; it now has region 9, a 0.25 nm layer with the D_it DOS. It now refuses a back-surface sheet or Q_b, and the regions are renumbered in increasing order.
- **`qf_on_strip`.** It was ignored by the separate strip deck; it is now honoured.
- **`execute_strip`.** It could accept truncated, timed-out or wrong-sign results and could leave only a STARTED row. Fixed with the statuses listed in §2.
- **Entry `vd_segments` in strip mode** is now rejected.
- **Labels.** The BQP mass 0.2543 is CALCULATED; the Schottky barrier is "ASSUMED grid, FITTED once selected".

**Not changed and listed as risks** (§10):
- the Neumann bottom;
- the 900 s strip timeouts;
- re-runs on resume.

**Second pass** (`codex_impl_recheck_2026-10-10.md`):
- The in-solver strip regions, the `qf_on_strip` fix, the labels and the Schottky mesh were judged OK. The node count is an estimate, not checked by Codex.
- `execute_strip` validation was still incomplete. Its points were then adopted:
  - timeout is checked before scanner errors;
  - a nonzero exit code or no ATLAS completion gives INCOMPLETE_RUN (every finished run in RUN_INDEX has exit code 0);
  - a strict export parser rejects malformed rows and conflicting duplicates;
  - all values must be finite;
  - grids must match exactly (atol 1e-6, rtol 0);
  - the segments are validated before launch, and the deck is built before the reservation;
  - a `Popen` failure is finalised (LAUNCH_ERROR);
  - the ratio is suppressed on a sign reversal.
- Not adopted: writing `converged=no` for SIGN_REVERSAL / KCL_FAILED. The existing runner uses `converged` for "the solver finished" and puts the acceptance in the status; the same convention is kept.

---

## 10. Open risks

1. **First-run activation (UNVERIFIED items, §9).** The S0 stop rule depends on `post_run_checks.py`. It is the C11 activation parser written as an offline script, not a runner change. It has been tested on existing V1/V2 outputs only.
   - IGZO.TOKYO: if REGIONAL MOBILITY MODEL SUMMARY still says "Concentration Independent Mobility", the branch is OPTION_NOT_ACTIVE.
   - Schottky: if the Contacts table shows 0.000 eV for source/drain, `^ins.ohmic` did not take effect.
2. **Gate tunnelling.**
   - Injection from a Conductor-region gate is UNVERIFIED.
   - FNORD applies one (F.AE, F.BE) pair at the semiconductor-interface field, an approximate bilayer estimate. It may not represent gate-to-channel injection at V_G < 0.
   - `ifn."gate"` may not extract. EXTRACT lines are excluded from the runner's error scan, so a missing `ifnvg.dat` does not fail the run.
   - S2-11 at 0.125 nm is the largest gate deck, about 21.5k nodes.
3. **BQP.** The manual says BLOCK iteration is always used with BQP; NEWTON is ignored (PDF p.838). Convergence with `trap maxtraps=10` and continuous DEFECTS is untested, and the S3-24/25 timeout is 1800 s. The mass tensor set through ML/MT1/MT2 is UNVERIFIED (inferred from the manual; there is no BQP mass keyword).
4. **Strip decks.**
   - The bottom is Neumann: an isolated, ungated film, with no substrate capacitance. This is ASSUMED.
   - The 13.2 nm Q_f-on strip may be strongly accumulated. It uses default acceptance by the switch rule, so check its convergence flags.
   - The 900 s timeouts come from the matrix; there are only 8 bias points, but no strip run time is known yet.
   - The in-solver strip (S6-27, about 26k nodes) is an equivalent-conductance device (ASSUMED). It needs the fitted (W/L)_par in its overrides.
   - `execute_strip` has been tested with mocks only (10 cases, §8).
5. **Runner behaviour (changed after review, §11.2).** A failed launch is recorded and the plan continues; on resume a C10 entry that already has a RUN_INDEX row is NOT launched again (`--retry ID` does it on purpose). Originally: on resume the failed entry was launched again. There is no provenance file beyond `execution.json` overrides, so options must only ever be switched on through overrides and `physics_options.yaml` must stay all-OFF. The deck header lists every active option.
6. **Duplicates (§6.4).** Launching S3-04 and S3-07 as written spends 2 launches on decks identical to S0-01.
7. **S4a and later plans depend on S3.** The S4a plan is the no-branch version. Templates must be resolved by hand; `make_campaign_configs.py --check` verifies the stage files but not hand-resolved copies.
8. **V3 versus V2 header text.** Decks differ only in comments, so `deck_sha256` differs from a hypothetical V2 launch of the same entry, and RUN_INDEX notes `model=config/iwo_material_model_v3.yaml`. `regress_all_decks.py` reads that note and rebuilds correctly.
9. **One edit in a sibling harness.** `analysis_2026-10-10_campaign/regress_all_decks.py` gained the strip-mode rebuild (3 lines). `analysis_2026-10-06_V2/regress_decks.py` was not edited; it does not cover strip or output modes.

---

## 11. Fixes after review (2026-10-10)

Seven blocking findings (the main session's own check plus Codex's implementation review, `codex_impl_review_2026-10-10.md`) were applied. **Nothing was launched**: no `deckbuild.exe`, no `run_campaign.py`, no `run_atlas.py` launch. Code was run only as deck-text generation, the regression harnesses, the check scripts in this folder, and mock tests with `Popen` / `reserve` / `append` / `execute*` / `run_atlas.rows` patched and every output in the session scratchpad. `results/RUN_INDEX.csv` has the same SHA-256 before and after (`89300F99…B4A8`). No file in `data/`, `results/runs/*` or any registered file was changed. Nothing was committed or pushed. The full diff is `fixes_after_review_2026-10-10.diff`; the test scripts and their real-data outputs are in `selftest_2026-10-10/`.

### 11.1 Finding 1: the strip parser rejected every real export (main session's finding)

- **Cause.** The nested `strict_xy()` in `execute_strip` raised "malformed row" on any all-numeric line without exactly 2 values. Every DeckBuild extract has such a line, the point count, as its second line (`36 2 2` in `results/runs/run_0041_*/idvd_vg1.dat`). Reproduced read-only: the old logic raises on `'36 2 2'`. Every `mode: strip` launch (S2-14…17, S6-25…27; S2-14 and S2-15 are in MIN10) would have ended as INCOMPLETE_EXPORT and been re-launched on resume.
- **Fix.** `run_atlas.strict_xy(path)` is now module-level. It skips exactly one all-numeric line of three non-negative integers before the first data row, and requires the number of data rows to equal its first value (a truncated export now fails on the count). The other strictness rules are unchanged.
- **Tests (no launch).**
  - All 198 real terminal-current exports under `results/runs` (`i[dgs]v[gd]*.dat`) parse, and in each the count equals the rows.
  - The 10-case mock was repeated, plus 2 cases, with copies of the real exports `run_0041/idvd_vg1.dat` and `isvd_vg1.dat` (count line included). The earlier mock had passed only because its fake exports had no count line.

    | Case | Status |
    |---|---|
    | real exports verbatim | REAL_ATLAS_STRIP |
    | truncated, count line unchanged | INCOMPLETE_EXPORT (count says 36, found 10) |
    | truncated and recounted, no 0.7 V | INCOMPLETE_EXPORT (missing drain points) |
    | wrong sign | SIGN_REVERSAL |
    | KCL violation | KCL_FAILED |
    | missing source export | NO_EXPORT |
    | conflicting duplicate row | INCOMPLETE_EXPORT |
    | malformed data row | INCOMPLETE_EXPORT |
    | exit code 1 | INCOMPLETE_RUN |
    | `Popen` failure | LAUNCH_ERROR |
    | timeout | TIMEOUT |
    | drain grid without 0.7 V | ValueError before any reservation |

### 11.2 Finding 2: the 200-launch, sequential limit is now enforced in code

- `config/solver.yaml` `max_launches` **271 → 260** = 60 distinct run IDs already in RUN_INDEX + the 200 approved. Every reserved run ID counts, failed or not.
- `run_atlas.reserve()` re-reads the cap from `config/solver.yaml` on disk (`file_cap()`), so `--override solver.runner.max_launches=…` can only lower it (Codex review point). Tested: an in-memory cap of 10000 with 260 IDs used still raises "launch budget 260 reached".
- `run_campaign.py`, C10 plans only (file stem `campaign_C10_*`):
  - `--workers` ≠ 1 is refused;
  - a C10 counter (distinct run IDs with a `c10_*` label in RUN_INDEX, failures included) stops the plan at 200;
  - an entry whose label already has a RUN_INDEX row, from this **or any other** C10 plan, is not launched again. A successful earlier launch is reused (its summary is copied, so MIN10 progress is shared with the stage plans). A failed one is reported with its run ID and status. Reuse also requires the same overrides, thickness and mode (transfer / strip / output), the same `material_model_used.json` (recomputed exactly as `run_atlas` writes it) and a byte-identical `device.in` rebuilt with the current generator and configs (`current_deck_text`; checked to reproduce the real launches run_0058 and run_0059). Otherwise the entry is refused, not reused and not launched (Codex review and re-check points);
  - `--retry ID[,ID]` spends a new (reserve) launch on purpose, also for an entry already finished in the same plan. The retry's record replaces the earlier ones (kept under `earlier_records`), so a failed retry is not mistaken for a finished entry on the next resume (Codex re-check point).
- All 181 labels are unique across the plans; the 10 MIN10 entries appear twice with identical definitions.
- Mock test (`selftest_2026-10-10/test_campaign_guards.py`, launcher and RUN_INDEX reader patched): `--workers 2` refused; a resume with earlier S0-01 success / S0-02 failure / S1-01 changed overrides / S1-02 changed thickness / S2-01 stale deck reuses S0-01, reports S0-02, refuses S1-01, S1-02 and S2-01, and launches the 5 new entries; a second resume launches nothing; `--retry S0-02` launches exactly one; a failed `--retry` of the finished S2-08 replaces its record and the next resume reports it instead of treating it as done; 200 `c10_*` IDs in RUN_INDEX stop the plan before any launch.

### 11.3 Finding 3: the activation parser now needs positive evidence

`post_run_checks.py` gives every requested option a state, ACTIVE / NOT_ACTIVE / UNVERIFIED, with the evidence text. Missing evidence is UNVERIFIED, never a pass. The overall status is OPTION_NOT_ACTIVE (exit 1) if any option is NOT_ACTIVE, else UNVERIFIED (exit 3) if any is UNVERIFIED, else ACTIVE_AS_REQUESTED (exit 0).

- **Echo and comments ignored.** Evidence lines come only from `solver_lines()`: nothing before `go atlas` (DeckBuild repeats the deck header comments there without the `ATLAS>` prefix; run_0040 lines 3–31), no `ATLAS>` / `EXTRACT>` echo, no `#` line.
- **BQP.** ACTIVE only if a solver-printed line names BQP / Bohm; a warning naming it gives NOT_ACTIVE. The activation string of this build is not documented (Codex research Q3), so the expected first result is UNVERIFIED and a human reads `deckbuild.out`.
- **In-solver strip.** Regions 8 and 9 must be `IWO` / `semicond.` in REGIONAL MATERIAL PARAMETERS, and their electron `mu` in the mobility summary must equal MUN·(W/L)_par·L_s within 1e-3. In run_0040, regions 8–10 are a Conductor and two Palladium electrodes, which now gives NOT_ACTIVE (it gave ACTIVE before).
- **IGZO.TOKYO.** ACTIVE only if the region-1 electron model names IGZO/Tokyo. "Concentration Independent" gives NOT_ACTIVE. A missing summary gives UNVERIFIED (it passed before).
- **TMUN.** Read from the electron block only, so a hole `tmu` line cannot certify it, and compared as a number, not as text (Codex review and re-check points).
- **Schottky.** The Contacts table must show χ(t) + φ_B on source and drain within 2 meV.
- **Gate-current models, each tested on its own.** I_G is exactly 0 in all 51 earlier runs with terminal currents, so in a deck with one gate-current model a nonzero I_G identifies that model; I_G = 0 gives NOT_ACTIVE. A deck with two (S2-12/13: QTNLSC + ITAT) needs `--gate-control` = the same deck without oxide TAT (S2-04 / S2-06). The control must have the same thickness, model file, `material_model_used.json` and gate-tunnelling settings, with TAT off. Its `device.in` solver statements must equal the run's once the oxide-TAT lines are removed (checked on the generated S2-12/S2-04 and S2-13/S2-06 decks: identical). Its currents must be finite and cover the run's V_G range, so there is no end-point clamping (Codex review and re-check points). QTNLSC is then taken from the control, and ITAT is ACTIVE only if |I_G − I_G,control| exceeds max(1e-20 A, 1e-3·max|I_G,control|). Without a valid control both models are UNVERIFIED.
- **Tests** (`selftest_2026-10-10/test_activation.py`; real run_0040 / run_0058 outputs, requested options injected through scratch copies of `execution.json`):

  | Case | Result |
  |---|---|
  | run_0040 baseline | ACTIVE_AS_REQUESTED |
  | run_0058 with `tmun=0` requested (it was run with 1.5) | NOT_ACTIVE |
  | (a) BQP requested, only the header comment names it | UNVERIFIED (was ACTIVE) |
  | (a2) the same plus a solver-printed Bohm line (synthetic) | ACTIVE |
  | (b) in-solver strip on run_0040 | NOT_ACTIVE (was ACTIVE) |
  | (c) IGZO, summary missing | UNVERIFIED (was ACTIVE) |
  | (c2) IGZO, Concentration Independent | NOT_ACTIVE |
  | (d) QTNLSC + ITAT, no control | UNVERIFIED |
  | (d2) control I_G identical | ITAT NOT_ACTIVE |
  | (d3) I_G above the control | both ACTIVE |
  | (d4) single QTNLSC, I_G nonzero | ACTIVE |
  | (d5) single QTNLSC, I_G = 0 | NOT_ACTIVE |
  | (d6) control with TAT on | UNVERIFIED |
  | (d7) control with a different material model | UNVERIFIED |

- **S0 rule.** S0 now stops on OPTION_NOT_ACTIVE **and** on UNVERIFIED, until a human has read `deckbuild.out` and recorded the evidence (plan stop rules updated).

### 11.4 Finding 4: N_D label

N_D0 = 2.5e17 cm⁻³ is the amplitude of the V1 law, FITTED to the V0 per-film values (`config/iwo_material_model.yaml` "FITTED law"; 01_CURRENT_STATE §E). It is now labelled **"FITTED V1 donor amplitude, kept fixed; constant thickness dependence ASSUMED"** in:
- `config/iwo_material_model_v3.yaml`, with a `provenance` field; the deck header `[D] Nd_eff(t)` line takes this label;
- `make_campaign_matrix.py` (`ND_LABEL`, `shared_start_values.labels`);
- `CAMPAIGN_DESIGN.md` (D12, §3 table, §4.4, §11, where "Not fitted" now says N_D is a fitted value carried over);
- §4 of this file.

It was called ASSUMED / not fitted before. `codex_design.md` keeps its original wording as a historical input.

### 11.5 Finding 5: oxide-TAT runs isolate the TAT current

- **New option.** `oxide_tat.poisson` (default 1 = the ATLAS default TAT.POISSON, emits nothing). `poisson=0` appends `^tat.poisson` to the MODELS line: trap charge out of Poisson, while ITAT.SC.EL still computes and collects the current (PDF p.323, manual text l.14541–14548; example p.327 `MODELS RTAT.SC TAT.SLICEPTS=21 ^TAT.POISSON`; Codex research Q2).
- **S2-12/S2-13** now carry `solver.physics_options.oxide_tat.poisson=0`. The reason: 1e19 cm⁻³ acceptors in 15 nm HfO2 are up to 1.5e13 cm⁻² of charge, far above the fitted Q_f, so ΔI_D and drain_share would mix an electrostatic shift with collected leakage. ITAT is identified against S2-04 / S2-06 (§11.3).
- **Not tested.** The electrostatics of a *charged* oxide are not tested by these runs. A charged variant would be a reserve launch, reported only as the combined response of a charged oxide. `post_run_checks.py` adds that caveat (`drain_share_note`) to any TAT run without `poisson=0`.
- **Syntax table.** The new statement is in `sample_decks/NEW_STATEMENTS.md` (0 unreviewed).

### 11.6 Finding 6: FNORD constants at the field ATLAS uses

- **Where ATLAS evaluates the field.** At each insulator–semiconductor segment (PDF p.288, manual text l.13034–13038; Codex research Q1), i.e. in the Al2O3 at the IWO interface. There E_Al = r·E_Hf, with r = ε_HfO2/ε_Al2O3 = 19.57/9.0 = 2.1744 (D continuity; no charge between the oxides).
- **Fix.** The Lenzlinger–Snow constants (A, B) are CALCULATED for the TiN/HfO2 barrier, so the values written are F.AE = A/r², F.BE = r·B:

  | Set | F.AE (A/V²) | F.BE (V/cm) | Was |
  |---|---|---|---|
  | worst | 2.171e-6 | 8.628e7 | 1.027e-5 / 3.968e7 |
  | nominal | 7.402e-7 | 2.167e8 | 3.50e-6 / 9.97e7 |

  Applied in `config/physics_options.yaml` (both sets, labels), in `make_campaign_matrix.py` (`fn_atlas`, S2-09/S2-10 overrides and params) and in the deck header text. Codex recomputed the same values.
- **Size of the error removed.** Own check: J(as set)/J(physical) = r²·exp[(B/E_Hf)(1 − 1/r)]. At V_G = −3 V, E_Hf ≈ 1.7e6 V/cm, which gives about 1.4e6, i.e. about 6 decades for the worst set. This agrees with the main session's ~6 decades and Codex's +5.5.
- **Still a single-barrier estimate.** The higher Al2O3 barrier is not in FNORD, so it is an upper estimate of injection through the bilayer.

### 11.7 Finding 7: C12 and C13

- **`campaign_extract.py` (C12, new).**
  - It imports the registered `extraction.py` / `run_extraction.py` (unchanged) and calls `run_extraction.analyse()` on the native `terminal_currents.csv`. On an exception it extracts each quantity separately with `invalid` flags.
  - It reports V_th,cc (1e-9 and 5e-10 A/µm), SS in the registered window and in the A1 window [r, 10r]·I_on,**measured** (r recomputed = 2.148e-5), μ_FE at 1–3 V (plus the run's own C_ox for the S6 ε runs), V_th,ELR, the power-law fit and the floor.
  - Campaign metrics: RMSE_sub (measured I_D in [10·floor, 1e-9]) and RMSE_on (1–3 V) on the measured grid, by PCHIP of log I with no extrapolation and coverage reported; the J term; signed errors. Labels are relabelled for the shared campaign.
  - `compare RUN REF --rule numerics|s1_05|s1_06` evaluates the S1 rules.
  - Check: on run_0038 it reproduces the registered `results.json` (V_th,cc 0.680422 V, SS 179.86 mV/dec, μ_FE(2 V) 9.3247, identical; power-law V_T within 3e-9 V). It gives SS_A1 126.4 mV/dec (01_CURRENT_STATE table: 126.4) and V_th,cc 0.270 V for run_0060 (state: 0.270 V). `compare run_0028 run_0013 --rule numerics` (the earlier mesh ×0.7 check) gives Δ active RMSE 0.0004 dec (as documented), ΔV_th,cc −0.36 mV, ΔSS −0.08 / −0.06 mV/dec → PASS.
- **`profile_shared.py` (C13, new, partial).**
  - `check NATIVE REF`: S1-07 / S3-27 / S4c. The transform is read from the two runs' `material_model_used.json`, and every other input must be identical. Each J-window point is compared forward, or inverse where the shift leaves the solved range (S1-07 needs this at the top of the on window). The tolerance is 0.01 dec. An uncovered point gives UNVERIFIED; a tunnelling/Schottky pair gives NOT APPLICABLE.
  - `profile R2 R6 R13`: shared (ΔV₀ via one Q_f, μ∞, ℓ), |ΔV₀| ≤ 0.5 V, μ∞ 10–300, ℓ 0–50 nm, Nelder–Mead from 9 starts. It reports start and profiled √J, per-film RMSE and coverage, and the diagnostic per-film free shift and scale. It is refused without one shared Q_f (relative tolerance 1e-9) / C_ox, and for tunnelling/Schottky runs (detected from the effective settings, defaults included) unless `--allow-approximate` (labelled APPROXIMATE). The verdict is UNVERIFIED if coverage < 95 % or the optimizer did not converge.
  - `adopt BRANCH… -- BASE…`: the S3 arithmetic, ≥ 0.03 dec gain and no film worse by > 0.03 dec.
  - `adopt` passes `--allow-approximate` to both triples and propagates APPROXIMATE or UNVERIFIED from either; flags are no longer read as run arguments.
  - Exit codes: 0 PASS/OK, 1 FAIL, 3 otherwise, refusals included (Codex review and re-check points).
- **Real-data evidence that the transformations are exact** (numerical checks on V1 runs, not model validation):

  | Pair | Difference | Max deviation, J windows | Result |
  |---|---|---|---|
  | run_0003 vs run_0001 | Q_f +1.73e12 only | 9.6e-4 dec | PASS (all 51 points, inverse direction at the top of the on window) |
  | run_0008 vs run_0003 | MUN only | 4.2e-6 dec | PASS |
  | run_0009 vs run_0004 | MUN only | 2.1e-6 dec | PASS |
  | run_0040 vs run_0004 | also differ in solver settings | — | correctly "not a pure pair" |

  Profiling the V2 triple (run_0058/0060/0059) gives √J 0.815 → 0.709 dec, with a 6.3 nm shape-only residual of 0.036 dec at a free shift of +0.24 V. The V1 per-film triple (0038/0039/0040, different Q_f) is refused.
- **Not implemented yet, and disclosed** (module docstring; `surrogate` / `loo` / `jacobian` exit 3): the S4b quadratic surrogate, the S5 LOO candidate selection and the identifiability Jacobian. They are needed only from S4b on, not for the S1 decisions, the S3 adoption or S4a. **They must exist before S4b is launched.**
- **Usage of the new tools:**

  | Decision | Command |
  |---|---|
  | S1 numerics | `campaign_extract.py compare <S1-03> <S1-02> --rule numerics` and `<S1-04> <S0-01>` |
  | S1-05 | `compare <S1-05> <S0-01> --rule s1_05` |
  | S1-06 | `compare <S1-06> <S1-02> --rule s1_06` |
  | S1-07 | `profile_shared.py check <S1-07> <S0-01>` |
  | S3 adoption | `profile_shared.py adopt <branch triple> -- <S0-01 S1-01 S1-02>` |

  These commands are also written into the plan stop rules.

### 11.8 Gates after all fixes (verbatim last lines)

```
regress_all_decks.py:            identical 48; unexpected differences 0
regress_decks.py (documented):   run_0038 / run_0039 / run_0040 / run_0012 / run_0058: IDENTICAL (sha 59e8fa85… cb85ffe6… 50ec4862… baae40d5… 4e70e7b4…)
check_v3_equivalence.py:         planned_fixed entries 98: identical solver statements V2 vs V3 98; differing 0; header-comment-only differences 98; S0-01 header -> OK
make_campaign_configs.py --check: plans verified: 181 matrix entries in 6 runnable plans (98 entries) + 5 templates (83 entries); verbatim and in matrix order: YES
make_sample_decks.py:            unreviewed statements: 0
```

- **Matrix regenerated.** `make_campaign_matrix.py` was first confirmed to be deterministic: the unchanged script reproduced `campaign_matrix.json` byte-identically. The regenerated matrix then differs only in S2-09/S2-10 (F.AE/F.BE, purpose, params), S2-12/S2-13 (`oxide_tat.poisson=0`, purpose, params) and `shared_start_values.labels`.
- **Plans and sample decks regenerated.** In the plans, these entries and the rule texts changed. All sample decks were regenerated: `S2-10` shows `fnord f.ae=2.171e-06 f.be=8.628e+07`, `S2-12` shows `… itat.sc.el ^tat.poisson`, and every deck shows the new N_D label.

### 11.9 Codex (read-only, codex-cli 0.162.0 in WSL)

1. **Manual research** (`codex_fixes_research_prompt_2026-10-10.md` → `codex_fixes_research_2026-10-10.md`):
   - FNORD field location and the r algebra;
   - `^TAT.POISSON` syntax and default; ITAT current kept;
   - `OUTPUT TRAPS.FT` for occupancy;
   - no documented activation string for QTNLSC / FNORD / ITAT / BQP / IGZO.TOKYO, so the parser defaults to UNVERIFIED;
   - `J.TUN` column names UNVERIFIED.
2. **Adversarial review of the fixes** (`codex_fixes_review_prompt_2026-10-10.md` → `codex_fixes_review_2026-10-10.md`).
   - Items 1, 4, 5 and 6 OK; 6 recomputed.
   - Adopted FIX points: `--retry` for finished entries; the cap was overrideable; hole `tmu` could certify TMUN; the gate control was not checked for equal inputs; profiling with unequal Q_f or tunnelling/Schottky only warned; `check`/`adopt` could pass on undercovered windows; exit code always 0; label reuse ignored thickness, mode and model.
   - **All were adopted** (§11.2, 11.3, 11.7).
3. **Re-check** of those responses (`codex_fixes_recheck_prompt_2026-10-10.md` → `codex_fixes_recheck_2026-10-10.md`).
   - OK: the cap override fix and the electron-only TMUN.
   - Adopted FIX points: a failed `--retry` left a stale success record; TMUN compared as text; the gate control did not check deck identity or current coverage; Q_f equality used rounding; breakers were detected from override strings; refusals exited 1; `--allow-approximate` was parsed as a run argument; reuse compared only strip vs non-strip and not the deck.
   - All were adopted (§11.2, 11.3, 11.7) and tested with the self-tests. They were not sent to Codex a third time.

### 11.10 Still open after these fixes

- `profile_shared.py` surrogate / LOO / Jacobian are needed before S4b (§11.7).
- First-run activation evidence: BQP, IGZO.TOKYO naming, `j.tun` columns and the in-solver strip regions 8–12 table are UNVERIFIED until a run prints them. `post_run_checks.py` then reports UNVERIFIED and the main session reads `deckbuild.out`.
- The charged-oxide TAT variant is not in the plan (§11.5).
- FNORD remains a single-barrier estimate (§11.6).

## 12. Review findings not applied

None. All seven findings were judged correct and applied (§11.1–11.7), and so were all Codex follow-up points (§11.9). Two scope notes, not rejections:
- **Finding 7 (C13).** Only the parts needed before the S1 decisions and before S3 were written. The S4b surrogate, the S5 LOO selection and the Jacobian are disclosed as missing (§11.7, §11.10).
- **Finding 5.** It allowed "add a `^tat.poisson` arm or record trap occupancy". The two existing TAT entries were switched to `^tat.poisson` instead of adding launches, so the budget is unchanged. The charged-oxide variant is left to the reserve.