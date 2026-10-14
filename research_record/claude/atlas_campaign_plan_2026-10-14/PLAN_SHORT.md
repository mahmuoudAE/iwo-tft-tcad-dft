# C10 ATLAS campaign: the short plan (2026-10-15)

This is the one-page summary of `PLAN_C10_S2_S5_2026-10-14.md`, after the three verification checks were applied (its §10). Nothing has been launched.

## Launches and time by stage

183 launches remain (17 of 200 used). Hours are typical solver time on the one licence.

| Stage | What it does | Launches: plan (range) | Hours |
|---|---|---:|---:|
| A | Repair of the 13.2 nm two-carrier run (S1-06) | 1 (1) | 1.0 |
| B | DIAG: off-current mechanisms, gate leakage, oxide traps, strips, confinement checks | 18 (18) | 6.5 |
| C | Registered mesh/DOS re-runs, only if a trigger fires | 2 (0–6) | 1.5 |
| D | Tunnelling-mesh check: oxide refinement or solver-tolerance replay, plus your QT-mesh pair | 3 (2–5) | 1.5 |
| E | FNORD leakage at 2.0/13.2 nm, ITAT slice check | 3 (2–8) | 0.9 |
| F | S3 model forms: IGZO, tail placement; BQP/Boltzmann moved to after S5 | 15 (7–24) | 2.5 |
| G | S4 shared calibration over the three films | 81 (63–89) | 11.6 |
| H | S5 leave-one-film-out | 30 (30) | 4.5 |
| I | S6 sensitivities, S7 31.8 nm, repairs | 17 (14–32) | 3.1 |
| J | Prospective predictions (P1–P4) | 12 (12–32) | 2.5 |
| | **Total** | **182 of 183 (149–245)** | **≈ 36 h** (≈ 110 h if every run hit its timeout) |

**The catch.** The plan path fits with 1 spare only if the shared model fails early. That failure is what we forecast, and it shortens S6 (the "early exit"). If the model calibrates instead, we are **6 launches short** (9 if Codex asks for one extra S4 triple). The pre-set fallback then applies in order:
1. BQP/Boltzmann drop out automatically.
2. P4 does not run while D-07 holds.
3. Three S6 mass runs are replaced by an exact offline transform (an amendment).
4. Any shortfall left (0–6) is your choice: a small cap increase, or cutting 3 more S6 runs.

## First batch: approvable now

- **B1 = S2-04 (2.0 nm) and B2 = S2-06 (13.2 nm)**: gate leakage with nominal oxide values. They are DIAG inv1–inv2, already in the approved DIAG plan. **2 launches, about 1 h** (timeouts 30 + 60 min). Each stops at a known gate for a short audit.
- **Before launch** (no launches): hold the S4a config; write the gate audit templates; run the pre-launch checks, including the sealed-run list; keep DeckBuild and TonyPlot closed. Optionally, a read-only memory logger, if Codex agrees, to settle the memory risk of the tunnelling-mesh run.

## Needs your go (later, in order)

1. The S1-06 repair (A), before DIAG inv3, after Codex checks it.
2. The rest of DIAG (16 launches).
3. The tunnelling-mesh branch (D) and FNORD (E): 6 launches, spent before we know whether the early exit comes.
4. Your rule for the "no early exit" case: a cap increase (C10 200 and max_launches 260 together), or cutting S6 runs.
5. Confirm that the prospective runs P1–P4 count under the C10 cap.
6. Schottky: the registered Option A is recommended. Option B does not fit the budget.
7. D-07 (whether sub-2 nm predictions are allowed); W_T range (keep it, recommended).

## Needs amendments or Codex

- **Codex rulings:** the S1-06 repair and its placement (PA-1); the same repair in S2-01/02/03 (PA-2); the mesh branch, which **exceeds Codex's 2-launch bound** because of your QT-mesh pair (PA-4); FNORD (PA-5); the order of the IGZO +0.30 runs; the extra H-D triple (PA-20); releasing the DIAG_HF config, which Codex asked to keep held.
- **Amendments to log:** PA-0 (config hygiene), PA-3 (only if a trigger fires), PA-6/7, PA-8 (IGZO fallback), PA-10 (BQP/Boltzmann after S5), PA-11 (3-D NC branch), PA-13 (S5 rules and provenance), PA-14 (label and citation fixes), PA-15 (prospective code), PA-17 (unsealing AFF-6p3 and STRIP-6p3), PA-18 (S4c confirmation wrapper), PA-19 (budget fallback).

## Open issues

- S2-11 gate-current changes look partly like solver noise, not only mesh error. The tolerance replay tests this.
- The S4c confirmation route is disabled in the frozen code. Enabling it must not change the frozen file, or S5 scoring refuses the records. A wrapper design is needed (PA-18).
- There is no channel-mesh check at 2.0 or 6.3 nm.
- The oxide-leakage bound with ALD Al2O3 values is not yet recomputed (0 launches).
- We need from the fab: sweep and instrument settings, gate/pad layout, the Pd deposition method, and the SI Fig. S1 text.
- No new measurements are secured, so "predictive" cannot be claimed yet.
