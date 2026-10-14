# Z6: PA-1 and PA-2 amendment drafts (DRAFT, 2026-10-15; NOT LOGGED; for Codex review)

Style follows the register's A41 entry (`codex/work_chat/HYPOTHESIS_REGISTER.md:1568-1600`: heading with timing and approvals, then **Scope**, **Why**, lettered items). Content from `PLAN_C10_S2_S5_2026-10-14.md` §2.1, §2.2 (inv3) and §6 (PA-1, PA-2 rows).
Amendment numbers are not assigned: the last amendment found in the register is A44 (`HYPOTHESIS_REGISTER.md:2085`); the logger assigns the next free A-number and D-number at logging.
User decision relayed 2026-10-15 ("accept all"): "Repair the 13.2 nm two-carrier run (S1-06) first: yes." That is the user's go on the principle; the Codex check and the manual check under the TCAD rule are still required before logging.

---

### A4x (draft PA-1): S1-06 two-carrier continuation repair (one launch, S1-06R) and its placement before DIAG inv3 (DRAFT, to be added after the freeze, <timestamp>, after run_0073 (S1-06, timed out) and before any S2 mechanism output exists; Codex: <pending>; manual check (ATLAS 5.28): <pending>; user go: 2026-10-15 reply 1 ("accept all", item 1), subject to Codex review; decision D-<xx>)

- **Scope.**
  - ATLAS C10, register §3 "S1-06 (two carriers)" (`HYPOTHESIS_REGISTER.md:2168`): "One targeted continuation repair is allowed, preserving current and Poisson accuracy."
  - This amendment:
    - fixes the form of that one repair (item (a));
    - spends one launch, S1-06R, on it (item (b));
    - fixes its place in the launch order (item (c)).
  - It changes no registered prediction, threshold, band or rule text, and no code of the frozen scorer (score_register.py c0f28bb9) or the committed runner (1375164).
  - Electron-only stays ASSUMED until S1-06R succeeds (`HYPOTHESIS_REGISTER.md:2168`).

- **Why.**
  - S1-06 ran once as run_0073. It stalled for 48.6 min between V_G −1.8 and −1.6 V and timed out at 3,600 s with 65 of 76 points (CALCULATED from its `deckbuild.out`, as stated in plan §2.1; not re-read for this draft).
  - The design S1 rule (`CAMPAIGN_DESIGN.md`, S1 block, rule "If S1-06 (two carriers) changes I_D by > 1e-3 relative above 1e-14 A/µm, the electron-only assumption is dropped: all later runs use two carriers, with timeout ×1.5") cannot be evaluated without a completed two-carrier run.
  - Expected outcome (not a result): the rule is not expected to fire, because n_i ≈ 7e-8 cm⁻³ with NV300 1e19 cm⁻³ (ASSUMED) or ≈ 1e-6 cm⁻³ with the COMPUTED N_v (CALCULATED), and μ_p = 0.01 cm²/Vs (ASSUMED) (plan §2.1). Matrix pre-registered expectation: "I_D change < 1e-3 relative everywhere above 1e-14 A/um; hole current < 1e-25 A/um" (`analysis_2026-10-10_campaign/campaign_matrix.json:806`).

#### (a) The repair (one form, fixed before launch)

- **Deck.** The registered S1-06 deck (= S1-02 deck with `carriers=2`; matrix entry `campaign_matrix.json:781-803`, overrides verbatim) plus **one** continuation repair in the bias ramp across V_G −1.8 … −1.6 V.
- **Form.** `<set by Codex>`. Example only (ASSUMED, plan §2.1): finer V_G steps across −1.8 … −1.6 V. The exact SOLVE statements, the step and the deck diff are attached as a dry build before logging.
- **Not relaxed.** Strict CR.TOLER 7.88e-16 A and XANDRNORM are kept (value as cited in plan §2.1; to be confirmed from the deck at dry build). No physical parameter, mesh, model flag or tolerance changes.
- **Timeout.** The matrix value, 3,600 s (`campaign_matrix.json:803`). Any change of the timeout is a separate, explicit item of this amendment: `<none | value and reason>`. The register allows a continuation repair only (plan §2.1 table, last column).
- **Manual basis.** ATLAS 5.28 manual, METHOD/SOLVE sections; SRH l.10141–10175; TRAP.TUNNEL l.37203–37220 (line numbers as cited in plan §6, PA-1 row; to be re-checked against the 5.28 text in the manual check).

#### (b) Launch and label

- One launch, a reserve launch counted against the 200-run cap.
- Entry form: `<--retry S1-06 with the repaired deck | new label c10_s1_06r_13p2>`, chosen by Codex (plan §2.1). If a new label is chosen, it is added to the matrix by a logged generator change with `make_campaign_configs.py --check` and a regression check before launch.
- Typical ≈ 1.0 h (ASSUMED) / timeout 3,600 s.
- Read-out: the design S1 rule above; S1-06R is not sealed (S1 baseline numerics).
- **If S1-06R fails again** (timeout or non-convergence): the electron-only assumption stays ASSUMED and is stated as a limitation; no second repair under this amendment.
- **If the S1 rule fires:** STOP and re-plan with Codex and the user (every later run would become two-carrier with timeout ×1.5; plan §2.1).

#### (c) Placement

- **Hard requirement:** S1-06R completes, and is read, **before DIAG inv3** (S2-03). Reason: PA-2 must be decided before inv3 from S1-06R and run_0073 only (plan §2.1 "Placement").
- **Default (user answer 2026-10-15, "S1-06 first: yes"):** S1-06R is the first launch of the campaign, before DIAG inv1. The plan's alternative (after inv1–inv2, before inv3; plan §2.1) is used only if Codex rules so and the user confirms. *Open point for Codex: the user's "first" and the plan's recommended "after inv1–inv2" differ; both satisfy the hard requirement.*
- Pre-launch checks of Z4 apply (`regress_sealed_aware.py` "unexpected differences 0"; `make_campaign_configs.py --check`; scorer hash c0f28bb9 and selftest; runner = 1375164; the A41 pre-launch gate; no DeckBuild/ATLAS/TonyPlot process).

---

### A4y (draft PA-2): the same continuation in the S2-01, S2-02 and S2-03 decks, decided once before DIAG inv3 (DRAFT, result-informed numerical amendment, to be added after the freeze, <timestamp>, after S1-06R and run_0073 and before any output of S2-03, S2-01 or S2-02 exists; disclosure: "result-informed by run_0073 and S1-06R (numerical evidence only); no S2 output seen"; Codex: <pending>; manual check: <pending>; user go: <pending>; decision D-<xx>)

- **Scope.**
  - ATLAS C10, register H-C, the three two-carrier DIAG entries: S2-03 (B3, inv3), S2-01 (B4, inv4) and S2-02 (B5, inv4) (plan §2.2).
  - It adds the PA-1 continuation, **identical in form**, to these three decks, and nothing else.
  - It changes no physical parameter, model flag, tolerance, prediction, threshold, gate declaration or scorer code. Gates G-S2-03-anomaly and G-S2-01-generation are re-evaluated on the amended runs as declared (`config/campaign_C10_DIAG.json`).
- **Why.**
  - The three decks share the two-carrier set-up that stalled run_0073; without the repair a timeout is likely (B4 "timeout likely if unamended", ASSUMED, plan §2.2), and a timed-out run is invalid for scoring (R1; scorer run validity `score_register.py:87-92`).
  - The matched pair S2-01 / S2-02 (register A9) stays matched only if both carry the same continuation; so PA-2 applies to both or to neither.
- **Condition.** PA-2 is proposed only if S1-06R converged under PA-1. Codex rules whether the same continuation goes into the three decks.
- **One decision, before inv3.**
  - Decided once, before inv3, from S1-06R and run_0073 only.
  - Never decided between inv3 and inv4, because S2-03 would then have been seen (plan §2.1).
  - If S1-06R cannot run before inv3, PA-2 is dropped: S2-01/02/03 run as registered, and a timeout is reported as invalid (R1) and makes the gate UNRESOLVED.
- **Mechanics (after logging, before inv3).**
  - The DIAG plan is regenerated for the three entries by a logged change to the generator (`make_campaign_configs.py`), and their deck hashes are re-bound.
  - `make_campaign_configs.py --check`, `regress_sealed_aware.py` ("unexpected differences 0") and a Codex check follow.
  - The gate binding changes for the two affected gates, so each gives a new evaluation and a new decision id (`campaign_gates.py:31-37`).
- **Confound kept.** G-S2-03-anomaly compares S2-03 (two carriers, now also with the continuation) against S0-01 (run_0061, one carrier, unrepaired). It stays an anomaly checkpoint (Codex D3), and the continuation becomes a second confound. This is stated in the audit (Z2 §4).
- **Manual basis.** As PA-1, plus l.58524–58526 (as cited in plan §6, PA-2 row; to be re-checked).

---

## Z1: hold the S4a config (DRAFT; not applied)

**Target.** `IWO_PHYSICS_CONSTRAINED_MODEL_V1/config/campaign_C10_S4a_spacefilling.json`, key `runnable` (line 3), currently `true`; file sha256 `548fd4d8d3d909efafcd9432564b153d8eb08b051371d7c795c06e9cabb7c731` (COMPUTED, sha256sum, 2026-10-15).

**Why** (plan §2.0 Z1; `01_state_gates_cost.md` §4.9): the plan is marked runnable before S3 exists; its own stop rule says it is "Valid as written only if S3 adopted NO branch; S4A-01-* are then identical to S0-01/S1-01/S1-02 and are NOT launched" (`make_campaign_configs.py:105`). Launching it now breaks register order step 6 and wastes 3 launches.

**The one-line change of the key:**

```diff
--- a/config/campaign_C10_S4a_spacefilling.json
+++ b/config/campaign_C10_S4a_spacefilling.json
@@ -3 +3 @@
- "runnable": true,
+ "runnable": false,
```

**This line must not be hand-edited alone.** The JSON is generated, and `make_campaign_configs.py --check` requires `runnable == (stem not in HOLD)` and `not_runnable_reason == HOLD[stem]` for every non-template plan (`make_campaign_configs.py:338-343`, "RUNNABLE FLAG wrong"). A hand edit would make `--check` fail and block every launch (Z4). The change is made in the generator:

1. Add one entry to the `HOLD` dict (`make_campaign_configs.py:48-75`), draft text:
   ```python
   'campaign_C10_S4a_spacefilling': f'Frozen register ({REG_TAG}) section 3, order step 6: S4a runs only after S3 (steps 3-5) is decided. '
                                    'Valid as written only if S3 adopted no branch; then S4A-01-* equal S0-01/S1-01/S1-02 and are not launched. '
                                    'Regenerate after the S3 branch decision (make_campaign_matrix.py, then this script), then remove this HOLD entry.',
   ```
2. Regenerate: `python analysis_2026-10-10_campaign/make_campaign_configs.py` (no argument writes every plan, `:373-377`). `plan()` (`:284-293`) then sets `runnable` false, appends " NOT RUNNABLE (HOLD): see not_runnable_reason." to `purpose`, prepends `"HOLD: <text>"` to `stop_rules` and adds `not_runnable_reason`. So the generated file differs in four places (runnable, purpose, stop_rules[0], not_runnable_reason), not one; `runs` are unchanged.
3. Verify: `python analysis_2026-10-10_campaign/make_campaign_configs.py --check` must report S4a among "held (runnable=false)" with "verbatim and in matrix order: YES"; confirm by diff that only `campaign_C10_S4a_spacefilling.json` changed (other plans byte-identical); record the old and new sha256 (as A41 did for DIAGa, `HYPOTHESIS_REGISTER.md:1730`).
4. `regress_sealed_aware.py` must print "unexpected differences 0"; Codex check; this is a tracked-file change, so it is logged before any further launch.

`scripts/run_campaign.py` refuses a `runnable=false` plan (`make_campaign_configs.py:22`), so the hold is enforced automatically once regenerated.
