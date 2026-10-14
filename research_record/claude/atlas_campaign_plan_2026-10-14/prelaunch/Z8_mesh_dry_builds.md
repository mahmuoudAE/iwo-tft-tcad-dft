# Z8: T0 dry builds for the tunnelling-mesh branch D (2026-10-15)

Zero launches. Nothing in `IWO_PHYSICS_CONSTRAINED_MODEL_V1` or in any registered config was modified. No sealed output (run_0075/0076/0077, `results/sealed/`, AFF-6p3/STRIP-6p3) and no RUN_INDEX row of those runs was read. The run_0076 partner deck was **regenerated from its registered overrides** (`config/campaign_C10_DIAGb.json`, entry S2-11) and not read from the run folder.

## 1. Method

- **Decks:** `dry_builds/z8_build.py` calls `analysis_2026-10-10_campaign/campaign_tools.entry_deck` (the same deck path as `run_atlas.execute`, with no simulator call) using `IWO_MODEL_FILE=config/iwo_material_model_v3.yaml` and generator overrides only. Options used: `gate_tunnelling.oxide_mesh_factor`, `qt_mesh`, `qt_point_nm`, `qt_slice_um`, `exclude_near_sd`, `solver.method_base` and `solver.strict_acceptance.cr_toler_A`.
- **Environment note:** the Windows Python 3.13 has no PyYAML. WSL's pure-Python PyYAML 6.0.1 was copied to the scratchpad and put on PYTHONPATH. Validity check: the rebuilt references are statement-identical to the launched decks (run_0067: 104/104 statements; run_0066: 106/106; COMPUTED, `z8_stats.json` "regression").
- **Node counts and oxide intervals:** these come from a mesh-line emulator (`dry_builds/grade.py`). Between consecutive `*.mesh` lines it takes r = (L−h1)/(L−h2) and n = round(ln(h2/h1)/ln r)+1, with geometric spacing scaled to L (algorithm ASSUMED).
  - Validated against run_0067 `equilibrium.str`, 117 x-lines and 82 y-lines, exact. The oxide line positions agree within 0.01 nm (Al2O3) and 0.04 nm (HfO2) (COMPUTED).
  - Validated against run_0062: 117 × 117 = 13,689 nodes, exact against `deckbuild.out` l.206 (MEASURED).
  - All counts below are therefore **CALCULATED (emulator)**. ATLAS confirms them only at launch ("Total grid points").

## 2. Per-deck results (CALCULATED unless labelled)

The x-mesh is unchanged in every deck: 117 lines, 0–24 µm. Interfaces are on mesh lines in every deck, at y (µm): Air/IWO top −0.002, IWO r1/r2 −0.00025, IWO/Al2O3 0, Al2O3/HfO2 0.002, HfO2/gate 0.017.

| Deck (partner) | y-lines | Nodes | Al2O3 intervals (dy nm) | HfO2 intervals (dy nm) | IWO / Air / Conductor intervals | Oxide intervals per slice |
|---|---|---|---|---|---|---|
| REF run_0067 | 82 | 9,594 (MEASURED, deckbuild.out l.206) | 15 (0.061–0.244); MEASURED 15 in equilibrium.str | 28 (0.246–0.985); MEASURED 28 | 17 / 14 / 7 | 43 |
| REF run_0066 (QT mesh) | 82 | 9,594 (MEASURED, l.215) | 15 | 28 | 17 / 14 / 7 | QT grid |
| S2-11 form (run_0076 partner, regenerated) | 117 | 13,689 | 22 (0.063–0.126) | 55 (0.126–0.503) | 17 / 14 / 8 | 77 |
| **T1a** (×0.25) | **185** | **21,645** | **32** (0.0625 uniform) | **111** (0.062–0.249) | 17 / 14 / 10 | **143** |
| T2a (generator) | 82 | 9,594 | 15 | 28 | same | QT 121 × 71 = 8,591 |
| T2a-E (hand edit, run_0066 enclosure) | 82 | 9,594 | 15 | 28 | same | QT 121 × 73 = 8,833 |
| T2b (generator) | 82 | 9,594 | 15 | 28 | same | QT 241 × 71 = 17,111 |
| T0r_tol | 82 | 9,594 | 15 | 28 | same | 43 |

**Refinement ratios** (CALCULATED from the table):
- Al2O3: 15 → 22 → 32, i.e. ×1.467 then ×1.455.
- HfO2: 28 → 55 → 111, i.e. ×1.964 then ×2.018.
- These confirm the plan values (§7.3). The difference is T1a: 185 y-lines and 21,645 nodes, against the plan's 182–184 and 21.3–21.5k.

**QT-mesh lines and enclosure** (the 5.28 manual l.13668–13670 says: "enclose the insulator and to not overextend into the conductor or semiconductor"; statement at l.61739–61765). The oxide spans y 0–0.017 µm and x 0–24 µm.

| Deck | QT mesh lines | y range (µm) | Encloses the oxide | Overextension |
|---|---|---|---|---|
| run_0066 / T2a-E | `qtx.mesh loc=0/24 spac=0.2`; `qty.mesh loc=-0.0005/0.0175 spac=0.0005` (T2a-E: spac=0.00025) | −0.0005 to 0.0175 | yes | 0.5 nm on each side |
| T2a | `qtx … spac=0.2`; `qty.mesh loc=-0.00025 spac=0.00025` and `loc=0.01725 spac=0.00025` | −0.00025 to 0.01725 | yes | 0.25 nm |
| T2b | `qtx … spac=0.1`; qty as for T2a | as T2a | yes | 0.25 nm |
| T1a, T0r | none (automatic slicing, per l.13662) | — | not applicable | — |

**Other Z8 checks** (COMPUTED from the deck text):
- QTNLSC.EL and QTNL.DERIVS are present in every deck.
- The oxide barriers and masses are unchanged: region 3 `affinity=1.6 eg300=8.8 me.tunnel=0.3`, region 4 `affinity=3.2 eg300=5.8 me.tunnel=0.1`.
- S/D `exclude_near` is present on T1a and T0r. It is absent on T2a/T2b, as in run_0066.

## 3. Statement diffs against the partner deck (full unified diffs in `dry_builds/diff_*.diff`)

- **T1a vs S2-11 form:** `y.mesh loc=0.002 spac=0.000125→6.25e-05` and `y.mesh loc=0.017 spac=0.0005→0.00025`. Nothing else changes; this is mesh-only. One comment-only header line still reads "S2-11 = oxide y-mesh x0.5" (stale label, cosmetic).
- **T2a vs run_0066:** `qty.mesh loc=-0.0005 spac=0.0005 → loc=-0.00025 spac=0.00025` and `qty.mesh loc=0.0175 spac=0.0005 → loc=0.01725 spac=0.00025`. **The generator ties the enclosure to qt_point_nm (`build_iwo_decks.py` l.294), so T2a changes the spacing AND shrinks the enclosure.** That is the "second change" the plan excludes (§7.4).
- **T2b:** as T2a, plus `qtx.mesh spac 0.2→0.1`.
- **T2a-E:** spacing only, with the enclosure kept. It is a **hand edit, not generator output**: a proposal only, not launchable under the rule "deck through the package generator".
- **T0r_tol vs run_0067:** `ir.tol 1e-19→1e-21` (×0.01) on both METHOD lines. The strict `cr.toler` goes 1e-17 → **1.37e-18 (×0.137, not ×0.01)**, because the generator's floor is max(cr_toler_A, 1e-5 × smallest measured active current) (l.191). The relaxed `cr.toler=5e-18` is hard-coded (l.192) and **unchanged**. So the plan's "IR.TOL and CR.TOLER ×0.01" is not expressible with the existing options.
- **T0r-step** (finer V_G steps, −2.8…−0.6 V): not built, because Codex picks the variant and the step value.
- **T1b:** not built, because it needs a new generator option (uniform oxide refinement including y = 0).

## 4. Memory against the 3.9 GB gate

**Method:** scaling from the only measured peak, 1.69 GB at 9,594 nodes. That value is reported for run_0067 in `analysis_2026-10-10_campaign/S2_PREP.md` l.150 and `codex/work_chat/CODEX_WORK_CHAT.md` l.48. It is **not present in the run_0067 logs** (`execution.json` has no memory field), so it counts as MEASURED but secondary. The runs run_0062–0067 log no peak memory.

**T1a prediction** (CALCULATED, N = 21,645):

| Scaling | Predicted peak | Gate (≤ 3.9 GB) |
|---|---|---|
| Linear | 3.81 GB | passes, with a 0.09 GB margin |
| N·lnN | 4.15 GB | fails |
| N^1.5 | 5.73 GB | fails |

- **S2-11 form** (13,689 nodes): 2.41 / 2.51 / 2.88 GB.
- **T2 and T0r** keep 9,594 device nodes, so the device-mesh part is ≈ 1.69 GB. The QT-grid memory is UNVERIFIED: run_0066, on a 4,477-point QT grid, logged no memory.

**Measured OOM evidence (READING):**
- run_0062 and run_0063 (13,689 nodes) failed with "Memory allocation failure" at the 2 GB limit: deckbuild.out l.461 and l.229; RUN_INDEX rows 125 and 127.
- run_0064 (9,594 nodes) also failed at 2 GB (l.468), with **the same deck hash as run_0065**, which then ran for 388.7 s once the LAA patch was in place (RUN_INDEX rows 129 and 131).
- So the 9,594-node deck needed more than 2 GB of address space, although its reported peak was 1.69 GB. The address-space demand therefore exceeds the reported peak by at least ×1.18 (CALCULATED, 2/1.69). Applied to T1a, even linear scaling gives ≥ 4.5 GB.

**Verdict:** T1a is **predicted infeasible (OOM) unless Z12 fits b ≈ 1 and the 1.69 GB figure is shown to be address-space, not working set**. This favours the T0r conditional slot.

## 5. Blockers before any branch-D launch

1. **T2a/T2b:** the generator needs an enclosure option independent of qt_point_nm. This is a code change, followed by a regression, a Codex check and a manual check.
2. **T0r (tolerance form):** the generator needs scalable strict and relaxed `cr.toler` values. The current options give ×0.137 and ×1.
3. **T1a:** the memory gate is not met under any superlinear b, and the run_0064/0065 address-space evidence argues against even the linear case.
4. **T1b:** needs a new generator option.
5. The node count is CALCULATED (21,645). The plan's 21.3–21.5k figure should be corrected.

## 6. Files

All under `prelaunch/dry_builds/`:
- **Decks:** `T1a.in`, `T2a.in`, `T2b.in`, `T2a-E_handedit.in`, `T0r_tol.in`, `REF_run0067.in`, `REF_run0066.in`, `REF_S2-11_run0076form.in`.
- **Overrides:** `*_overrides.json` for each generator-built deck.
- **Diffs:** `diff_*.diff`.
- **Statistics:** `z8_stats.json`.
- **Scripts:** `z8_build.py` and `grade.py`.
