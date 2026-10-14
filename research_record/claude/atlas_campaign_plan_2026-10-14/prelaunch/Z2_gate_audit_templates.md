# Z2: DIAG gate audit templates (DRAFT, 2026-10-15; no launch, nothing logged)

Plan item: `PLAN_C10_S2_S5_2026-10-14.md` §2.0 Z2. Eight templates: four gates × {UNRESOLVED, FIRED}.
Fill the `<...>` fields only. Save the completed copy as its own file (for example `audit_<GATE_ID>_<DECISION_ID>.md`) and pass it with
`python scripts/run_campaign.py config/campaign_C10_DIAG.json --ack-gate <GATE_ID> --ack-audit <file>`.

## 0. Rules every template inherits (sources, not new rules)

- **Acceptance check of the file.** The runner accepts an audit only if the file exists, is non-empty and contains the gate id and the decision id verbatim (`scripts/campaign_gates.py:238-246`, `audit_citation`). The acknowledgement records the path, sha256 and decision id and never carries over to a new decision (`campaign_gates.py:42-43`; `S2_RUNNER_GATES_2026-10-13.md:54-58`, D1).
- **Decision id.** Printed on the STOP line: `GATE <id> [<rule_id>] after <entry>: <state> -> STOP (decision <decision_id>)` (`campaign_gates.py:233`). It is unique per evaluation (`S2_RUNNER_GATES_2026-10-13.md:205`). Copy it from that line; never from an earlier evaluation.
- **State mapping** (`campaign_gates.py:21-26`): FIRED = the frozen-scorer verdict, with a `PROVISIONAL (...): ` prefix removed, starts with `FAIL`. UNRESOLVED = anything else that is not PASS / below resolution (`unresolved`, `invalid`, `not demonstrated`), or a missing run, hash mismatch, error or timeout. Both stop (`config/campaign_C10_DIAG.json`, `on_fired`/`on_unresolved` = `stop`).
- **What the gate shows.** State, token (ok / missing_run / error / timeout / scorer_hash_mismatch / no_state_line), decision id, binding hashes; never a current or verdict text (`S2_RUNNER_GATES_2026-10-13.md:68`). The verdict text below is therefore the registered verdict *family* of the frozen scorer for that state. The scorer's exact string is copied into the audit only when the register's unsealing order allows reading that run's score.
- **Order for the A41(d) screens (G-S2-04, G-S2-06).** `hc_explains` against the matched control is scored *before* any other output of the run is inspected, including verdict text needed for this audit (register l.1798; plan §2.2). Inputs fixed in `01_state_gates_cost.md` §4.1: no `--resolution*` input, `--mesh-score` only if the registered S2-11 score exists.
- **Rule basis (verbatim in every gate declaration, `config/campaign_C10_DIAG.json` `rule_basis`):** stopping on a resolved exceedance of the registered H-C bound is a prospective, stricter operational rule; it is not a verbatim implementation of `CAMPAIGN_DESIGN.md:304`, and a FIRED gate is not itself a hypothesis falsification (Codex D2, 2026-10-12T20:28Z).
- **Expected state (CALCULATED from the frozen code, `01_state_gates_cost.md` §4.1):** every gate stops. Without a demonstrated resolution, `censored_upper` (`score_register.py:645-654`) cannot return PASS or "below resolution, consistent", and `prov` (`:429-434`) adds the PROVISIONAL prefix. UNRESOLVED is the expected state, FIRED the exceptional one.
- **Under the KCL proxy** a FIRED state means a resolved current above max(1e-17 A, 0.1 × floor), i.e. floor-scale (`campaign_gates.py:21-23`; KCL limit `CAMPAIGN_DESIGN.md:356`). That is the literal trigger of `CAMPAIGN_DESIGN.md:304`.
- **Frozen scorer:** `analysis_2026-10-10_campaign/score_register.py`, sha256 `c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a` (`config/campaign_C10_DIAG.json` `scorer_sha256`).
- **No fit, no rescue parameter, in any variant** (`CAMPAIGN_DESIGN.md:304`; plan §8).

Registered thresholds used below (all from the frozen scorer, `score_register.py:187`): NOM_FRAC 1e-2 (×floor); GEN_BOUND 1e-20 A/µm; floor window V_G ∈ [−2, −0.5] V (FLOOR_WIN). Floors: 2.0 nm 4.61e-15 A/µm, 13.2 nm 6.60e-12 A/µm (MEASURED/derived, design §7, as cited in `01_state_gates_cost.md` §4.1; not re-read here).

---

## 1. Common FIRED audit block (nominal and SRH gates; `CAMPAIGN_DESIGN.md:304`: "Stop and audit KCL, CR.TOLER and the deck; do not fit")

This block is done **first**, before any interpretation, for every FIRED template below.

| # | Check | Source of the rule | Result |
|---|---|---|---|
| F1 | KCL per bias point: \|I_D + I_S + I_G\| ≤ max(1e-17 A, 0.1 × floor) + 1 % Σ\|I\| in the scored window; list every KCL-failed point and whether the FAIL came from a KCL-passed point | `CAMPAIGN_DESIGN.md:356`; scorer censoring `score_register.py:88-93` | `<PASS / list>` |
| F2 | CR.TOLER and XANDRNORM in the deck as generated (strict, not relaxed); the value equals the registered one | `CAMPAIGN_DESIGN.md:97`; S1-06 value 7.88e-16 A as cited in plan §2.1 (ASSUMED here, not re-read) | `<value, line in deck>` |
| F3 | Deck identity: deck_sha256 of the run equals the hash bound in the frozen DIAG plan; model file V3; overrides verbatim | `config/campaign_C10_DIAG.json`; `make_campaign_configs.py --check` | `<equal / differs>` |
| F4 | Activation: every requested model ACTIVE in deckbuild.out (no OPTION_NOT_ACTIVE) | `CAMPAIGN_DESIGN.md:293` | `<ACTIVE / list>` |
| F5 | Run validity: status, return code 0, not timed out, completion banner, all points exported, finite values | `score_register.py:87-92` ([C3]) | `<valid / reason>` |
| F6 | Manual check of each deck statement involved against the ATLAS 5.28 manual (governing text) | TCAD check rule (memory); line numbers to be added by the auditor | `<manual lines>` |
| F7 | Codex review of F1–F6 | TCAD check rule | `<work-chat timestamp>` |

Outcome of the block: **(a) defect found** → STOP stands; fix the code or deck; `regress_all_decks.py` / `regress_sealed_aware.py` must print "unexpected differences 0"; any relaunch only as `--retry` under a logged amendment with Codex and user go; this audit records the defect and does **not** acknowledge the gate. **(b) no defect** → the FIRED state is reported as a resolved exceedance of the registered bound (not a falsification, D2) and the decision row of the template applies.

---

## 2. G-S2-04-nominal (after S2-04, 2.0 nm; inv1, B1)

Declaration: `config/campaign_C10_DIAG.json:23-38`; rule `S2-STOP-NULL`; test `hc_nominal` (`score_register.py:782-793`), registered H-C: |I_G(−3 V)| ≤ 1e-2 × floor, only if a numerical ceiling below that bound is demonstrated, otherwise unresolved (`score_register.py:30-31`).

### 2a. G-S2-04-nominal — UNRESOLVED

```
Gate id:        G-S2-04-nominal
Rule id:        S2-STOP-NULL
Decision id:    <decision_id from the STOP line>
Checkpoint:     S2-04   run: <run_NNNN>   label: c10_s2_04_2p0
Gate state:     UNRESOLVED   token: <ok | missing_run | error | timeout | scorer_hash_mismatch | no_state_line>
Order check:    hc_explains S2-04 vs S0-01 scored first: <yes, JSON sha256 ...>   (register l.1798)
Verdict text (registered family, score_register.py:645-654, :782-793, :429-434; exact string only if unsealing allows):
                "PROVISIONAL (resolution not demonstrated): unresolved: below resolution (<res> A/um, not demonstrated), resolution not demonstrated below the bound <bound>"
                | "PROVISIONAL (resolution not demonstrated): unresolved (resolved only against a resolution that is not demonstrated; a pass needs a demonstrated resolution)"
                | "unresolved (KCL-censored at -3 V)" | "unresolved (no value)" | "invalid (<reason>)"
Meaning:        H-C nominal null at 2.0 nm is neither passed nor failed; no ceiling below 1e-2 x floor is demonstrated. Not a falsification.
Token != ok:    the run is invalid for scoring (register R1 / plan §8); no rerun without a logged amendment.
Decision:       ACKNOWLEDGE and continue to inv2 (S2-06). Report H-C nominal 2.0 nm as UNRESOLVED (PROVISIONAL). No fit, no rescue.
Codex check:    <timestamp>     User go for next invocation: <reference>
```

### 2b. G-S2-04-nominal — FIRED

```
Gate id:        G-S2-04-nominal
Rule id:        S2-STOP-NULL
Decision id:    <decision_id from the STOP line>
Checkpoint:     S2-04   run: <run_NNNN>   label: c10_s2_04_2p0
Gate state:     FIRED   token: ok
Order check:    hc_explains S2-04 vs S0-01 scored first: <yes, JSON sha256 ...>   (register l.1798)
Verdict text (registered family, score_register.py:654, :429-434):
                "FAIL" (demonstrated resolution) | "PROVISIONAL (resolution not demonstrated): FAIL"
Meaning:        resolved |I_G(-3 V)| above 1e-2 x floor (2.0 nm floor 4.61e-15 A/um); under the KCL proxy this is floor-scale current,
                which contradicts the CALCULATED leakage bounds (CAMPAIGN_DESIGN.md:304).
Audit block §1: F1 <..> F2 <..> F3 <..> F4 <..> F5 <..> F6 <..> F7 <..>   Outcome: <(a) defect | (b) no defect>
Decision:       (a) do NOT acknowledge; fix, regress, logged amendment, Codex + user go.
                (b) ACKNOWLEDGE only with Codex + user go; report "resolved exceedance of the registered H-C nominal bound at 2.0 nm
                (operational stop, not a falsification, Codex D2)"; re-plan the leakage interpretation with Codex (Z9 bounds) before inv2. No fit.
```

---

## 3. G-S2-06-nominal (after S2-06, 13.2 nm; inv2, B2)

Declaration: `config/campaign_C10_DIAG.json:41-56`; rule `S2-STOP-NULL`; test `hc_nominal`; floor 6.60e-12 A/µm.

### 3a. G-S2-06-nominal — UNRESOLVED

```
Gate id:        G-S2-06-nominal
Rule id:        S2-STOP-NULL
Decision id:    <decision_id from the STOP line>
Checkpoint:     S2-06   run: <run_NNNN>   label: c10_s2_06_13p2
Gate state:     UNRESOLVED   token: <ok | missing_run | error | timeout | scorer_hash_mismatch | no_state_line>
Order check:    hc_explains S2-06 vs S1-02 scored first: <yes, JSON sha256 ...>   (register l.1798)
Verdict text:   as 2a (same hc_nominal families).
Meaning:        H-C nominal null at 13.2 nm unresolved; not a falsification.
Decision:       ACKNOWLEDGE; then Block A / PA-2 decision before inv3 (plan §2.1, §2.2). Report UNRESOLVED (PROVISIONAL). No fit.
Codex check:    <timestamp>     User go for next invocation: <reference>
```

### 3b. G-S2-06-nominal — FIRED

```
Gate id:        G-S2-06-nominal
Rule id:        S2-STOP-NULL
Decision id:    <decision_id from the STOP line>
Checkpoint:     S2-06   run: <run_NNNN>   label: c10_s2_06_13p2
Gate state:     FIRED   token: ok
Order check:    hc_explains S2-06 vs S1-02 scored first: <yes, JSON sha256 ...>
Verdict text:   "FAIL" | "PROVISIONAL (resolution not demonstrated): FAIL"
Meaning:        resolved |I_G(-3 V)| above 1e-2 x 6.60e-12 A/um; floor-scale under the KCL proxy (CAMPAIGN_DESIGN.md:304).
Audit block §1: F1..F7 <..>   Outcome: <(a) | (b)>
Decision:       (a) do NOT acknowledge; fix, regress, amendment, Codex + user go.
                (b) ACKNOWLEDGE only with Codex + user go; report as operational stop, not falsification (D2); re-plan with Codex before inv3. No fit.
```

---

## 4. G-S2-03-anomaly (after S2-03, 2.0 nm, against S0-01 = run_0061; inv3, B3)

Declaration: `config/campaign_C10_DIAG.json:59-78`; rule `S2-ANOMALY-CARRIER` (Codex D3: carrier-confounded anomaly checkpoint, 2 carriers vs 1 carrier; cannot isolate generation; `S2_RUNNER_GATES_2026-10-13.md:62-64`); test `hc_generation` (`score_register.py:834-847`, core `:795-831`): max |ΔI_D| over V_G ∈ [−2, −0.5] V ≤ 1e-20 A/µm.
It is an SRH run (S2-03: `srh`, τ 1e-9 s, σ 1e-13 cm², plan §2.2 B3), so a FIRED state takes the §1 block first.

### 4a. G-S2-03-anomaly — UNRESOLVED

```
Gate id:        G-S2-03-anomaly
Rule id:        S2-ANOMALY-CARRIER
Decision id:    <decision_id from the STOP line>
Checkpoint:     S2-03   run: <run_NNNN>   label: c10_s2_03_2p0   control: run_0061 (c10_s0_01_2p0)
PA-2 state:     <PA-2 applied (deck hashes re-bound) | PA-2 dropped: registered deck>
Gate state:     UNRESOLVED   token: <ok | missing_run | error | timeout | ...>
Verdict text (score_register.py:815-829, :645-654, :429-434):
                "unresolved (no common point in the window)"
                | "unresolved (KCL-censored at V_G [...]: never a pass, not a fail from those points)"
                | "unresolved (one-sided differences at V_G [...]: lower bound <= 1e-20 < upper bound; neither a pass nor a fail)"
                | "PROVISIONAL (resolution not demonstrated): unresolved: below resolution (...)" | "invalid (<reason>)"
Meaning:        anomaly checkpoint neither passed nor fired; carrier-confounded, says nothing about generation alone.
Token timeout:  expected if PA-2 is dropped (plan §8 R1); run invalid, no rerun without a logged amendment.
Decision:       ACKNOWLEDGE; continue to inv4 (S2-01, S2-02). Report UNRESOLVED; the matched test is G-S2-01-generation. No fit.
Codex check:    <timestamp>     User go for next invocation: <reference>
```

### 4b. G-S2-03-anomaly — FIRED

```
Gate id:        G-S2-03-anomaly
Rule id:        S2-ANOMALY-CARRIER
Decision id:    <decision_id from the STOP line>
Checkpoint:     S2-03   run: <run_NNNN>   control: run_0061
Gate state:     FIRED   token: ok
Verdict text:   "FAIL" | "PROVISIONAL (resolution not demonstrated): FAIL"
Meaning:        a resolved |dI_D| lower bound above 1e-20 A/um between a 2-carrier SRH/TAT deck and the 1-carrier S0-01; the cause may be
                the carrier count (and, if PA-2 applied, the continuation) rather than generation (Codex D3).
Audit block §1: F1..F7 <..>, plus F8: compare with the S1-06R two-carrier result (plan §2.1) to separate the carrier effect.
Decision:       (a) defect: do NOT acknowledge; fix, regress, amendment.
                (b) no defect: ACKNOWLEDGE with Codex + user go; report "carrier-confounded anomaly, not a generation result";
                continue to inv4, where G-S2-01-generation is the matched test. No fit.
```

---

## 5. G-S2-01-generation (evaluated after S2-02; S2-01 against S2-02, 13.2 nm; inv4, B4–B5)

Declaration: `config/campaign_C10_DIAG.json:81-98`; rule `S2-STOP-NULL`; test `hc_generation`, matched SRH-on vs SRH-off control (register A9).

### 5a. G-S2-01-generation — UNRESOLVED

```
Gate id:        G-S2-01-generation
Rule id:        S2-STOP-NULL
Decision id:    <decision_id from the STOP line>
Checkpoint:     S2-02   runs: S2-01 <run_NNNN> (c10_s2_01_13p2), control S2-02 <run_NNNN> (c10_s2_02_13p2)
PA-2 state:     <applied identically to S2-01 and S2-02 | dropped>
Gate state:     UNRESOLVED   token: <ok | missing_run | error | timeout | ...>
Verdict text:   as 4a (gen_core families).
Meaning:        extreme generation neither shown <= 1e-20 A/um with a demonstrated resolution nor resolved above it.
Decision:       ACKNOWLEDGE; continue to inv5. Report H-C generation 13.2 nm UNRESOLVED (PROVISIONAL). No fit.
Codex check:    <timestamp>     User go for next invocation: <reference>
```

### 5b. G-S2-01-generation — FIRED

```
Gate id:        G-S2-01-generation
Rule id:        S2-STOP-NULL
Decision id:    <decision_id from the STOP line>
Checkpoint:     S2-02   runs: S2-01 <run_NNNN>, control S2-02 <run_NNNN>
Gate state:     FIRED   token: ok
Verdict text:   "FAIL" | "PROVISIONAL (resolution not demonstrated): FAIL"
Meaning:        an SRH null test produced a resolved |dI_D| above 1e-20 A/um; under the KCL proxy floor-scale current; contradicts the
                CALCULATED bound (matrix pre-registered expectation <= 1e-20 A/um, campaign_matrix.json:984).
Audit block §1: F1..F7 <..>   Outcome: <(a) | (b)>
Decision:       (a) do NOT acknowledge; fix, regress, amendment, Codex + user go.
                (b) ACKNOWLEDGE only with Codex + user go; report as operational stop, not a falsification (D2); re-plan with Codex and
                the user before inv5. No fit.
```
