# 06 Integrity check of PLAN_C10_S2_S5_2026-10-14.md (2026-10-14)

**What this file is.** An adversarial read-only check of `PLAN_C10_S2_S5_2026-10-14.md`. It compares the plan with the frozen register (§0, §3, A12/A16, A41, H-B..H-F, H-J), the v4 S4b/S5/H-F freeze, `S2_RUNNER_GATES_2026-10-13.md`, the stop rules in `CAMPAIGN_DESIGN.md` §6, the 200-launch cap, the sealing rules, the amorphous blind rule, the TCAD check rule and the user's ATLAS run preferences.

**How it was done.**
- Nothing was launched, edited (apart from this file), committed or pushed, and CERN was not contacted.
- Not opened: anything under `results/runs/run_0075*`, `run_0076*` or `run_0077*`; anything under `sealed/`; any AFF-6p3 or STRIP-6p3 output; any amorphous DFT quantity.
- Only the run_id and label columns of RUN_INDEX were parsed.
- The S2-11 numbers were recomputed from the allowed `register_scores/hc_mesh_run_0076_run_0067.json`.

**Tags.**
- **MUST-FIX**: fix before Codex review or any launch request.
- **SHOULD-FIX**: fix before the item it concerns.
- **REPORT**: disclose, no change required.

---

## MUST-FIX

### M1. The plan interprets worst-set floor-scale current after the S2-11 FAIL
**Where:** §1.3 l.102–107, §2.5 item 3 l.279–283, §7.6 l.844.

**The rule it breaks.** The S2 stop rule (`campaign_C10_S2_offfloor.json`, applied by DIAG; `CAMPAIGN_DESIGN.md` l.305) says worst-set floor-scale current may be interpreted "only after S2-11 ... agrees within 0.1 dec in log10 I_G". S2-11 FAILED. The plan itself repeats the rule at l.94.

**What the plan does anyway:**
- it compares worst-set |I_G| with the 2.0 nm floor at −2.0 V and −1.8 V;
- it compares the medians with the floor ("6.5 and 6.1 dec below");
- it concludes that "the flatness outcome does not depend on the mesh" and that "flatness fails on both meshes by more than 11 decades";
- it uses this reading to argue that the mesh branch is decision-relevant.

**Why the claim goes beyond the evidence.**
- Only two meshes exist, and neither is converged. Codex 03:36Z: "Neither mesh is thereby established as accurate."
- The window changes are erratic: −0.49 to +2.86 dec (COMPUTED (ATLAS), recomputed here).
- The registered H-C criterion is the slope of I_D (register l.150; design §7.2). A "span of 11.6 decades" is not that criterion.

**A number mismatch.** The medians as quoted (6.5 and 6.1 dec below the floor) do not reproduce:
- median of log10|I_G|: −6.65 / −6.24 dec (CALCULATED from the 16 window points);
- log10 of the median |I_G|: −6.62 / −6.23 dec;
- only the upper middle value gives −6.50 / −6.13 dec.

**Fix.**
- Delete these readings, or move them into a sealed question for Codex marked "not interpreted (S2 stop rule)".
- Justify the decision relevance of the mesh branch without them.

### M2. The plan path does not fit "with one spare"
**Where:** §1.2 l.63–75, §4.3.

**(a) An unlisted assumption.** Block I's plan value of 17 = S6 12 + S7 2 + repairs 3, so it already assumes the S6 early exit. That exit needs S4 to fail *and* S5 to confirm the failure on at least 2 folds (design l.338). The plan path also assumes that S4b runs in full. The assumption list at l.68–72 omits the early exit.
- Without it, S6 rises from 12 to 22 launches, and the plan path becomes 182 + 10 = **192 > 183** (CALCULATED).
- `01` §3 already shows that the full register path is over the cap.

**(b) A registered test is missing.** H-D registers "a nested ℓ = 0 comparison, then native best triples; cost up to 6 confirmation launches" (register l.162 and l.169). The plan maps only S4c (3). If the ℓ = 0 branch needs its own native triple, add 3: 182 + 3 = **185 > 183** even with the early exit (CALCULATED).

**Fix.** State both conditions in the assumption list, and give the fallback cut that applies if they fail.

### M3. The generation null is stated more strongly than the bound allows
**Where:** §1.4 l.113.

**The claim:** "SRH and trap-assisted generation cannot produce the floor", with a margin of ≥ 12.6 dec.

**Why it is too strong.** The bound of 1.1e-27 A/µm rests on σ = 1e-15 cm² and v_th = 1.08e7 cm/s, with no field enhancement (`GENERATOR_AUDIT.md` l.249–256). S2-01/03 test σ = 1e-13 cm², which is ×100. The plan's own m*-based v_n is ×2.15 (§3.6).
- The bound becomes 1.1e-27 × 100 × 2.15 = **2.4e-25 A/µm**, 10.3 dec below 4.61e-15 (CALCULATED).
- With the audit's own illustrative ×1e10 field enhancement it becomes 2.4e-15 A/µm, which is **0.28 dec below** the 2.0 nm floor (CALCULATED).
- The Hurkx enhancement factor is not bounded anywhere.

**Fix.** Restate the claim as "SRH generation at the baseline σ and v_th, with no field enhancement". Report the margin at the extreme set (≥ 10.3 dec without enhancement), and leave trap-assisted generation as conditional or UNRESOLVED.

---

## SHOULD-FIX

1. **PA-2 is result-informed but not labelled so.** It is decided between inv3 and inv4 (l.199), so after S1-06R *and* S2-03 (two-carrier) have been seen.
   - It changes two registered DIAG decks in a plan the plan itself calls "frozen hash-bound", so the gates need re-binding.
   - S2-03 is left unrepaired, although R1 lists it as at risk.
   - Either decide PA-2 before inv3 (A1 already runs first) and cover S2-03, or justify leaving S2-03 out. Label PA-2 result-informed either way.

2. **The mesh branch exceeds Codex's bound.**
   - Codex 03:36Z (work chat l.5497) proposed "one further refinement, then one conditional refinement", which reduces the reserve from 9 to 7.
   - The plan proposes 3 launches planned and 5 at most (T2a, T2b, T3 added), which reduces the reserve from 9 to 6, or to 4 at the maximum.
   - The user did ask for the QT-mesh series, but the plan must state that it goes beyond Codex's bound and ask for an explicit ruling.

3. **A41 scope is broken twice.**
   - E4–E8 are gated on a T1a PASS, but T1a covers only the 2.0 nm worst set at ×0.5. The scored scope "does_not_certify other films; another oxide parameter set" (hc_mesh JSON), and §7.5 says the same.
   - §2.5 item 4 says the worst-set 2.86 dec "does not transfer", then sets it against the nominal 9-decade margin.
   - Fix: drop the T1a gate, or present E4–E8 as unconverged and PROVISIONAL whatever T1a gives.

4. **Two claims are stated as fact without support.**
   - "Mesh-robust" FNORD (§1.4 l.115, §2.5): no FNORD mesh check is planned. Label it ASSUMED (an argument), or add a check.
   - The "≥ 9-decade" nominal margin is stated without condition (l.97, l.286), although Z9 (ALD Al2O3 χ 1.85 / 2.45 eV) is pending. Make it conditional on Z9.

5. **Two T1a/T1b problems.**
   - The Richardson estimate in §7.5 is not defined. Each `oxide_mesh_factor` halving refines Al2O3 by about ×1.5 and HfO2 by about ×2 (DIAG stop rule; hc_mesh JSON `refinement`), so there is no single refinement ratio.
   - The optional `OUTPUT QTUNN.EL` on T1a contradicts T0's rule that the deck differs "only in the mesh lines" and the frozen intervention equality (`deck_statements_changed` = 2).

6. **The budget rule and the plan path disagree** (§4.4). On the plan path, 17 + 39 = 56 launches are used before F13, which leaves 144 (CALCULATED).
   - R_need = 142, so the rule needs R_need + 1 = 143 per item: F13 runs (144), F14 runs (143), F15 does not (142).
   - The rule therefore admits 2 of the 3 BQP and Boltzmann runs that the plan path counts. With S4a at 45 (R_need 145), it admits none.
   - The rule also protects only the early-exit S6. That lets exploratory, kept-out items displace registered S6 entries.

7. **Schottky Option B costs more than "+8".**
   - Profiling is not exact for contacts (design l.233).
   - The frozen v4 code refuses contact folds (`CONTACT_ROUTE_AVAILABLE = False`).
   - An adopted Schottky branch would therefore force native Q_f and MUN through S4 and S5 (the design's D5 route). That cost is not counted.

8. **Two Codex 08:49Z conditions are missing** (work chat l.5739): "Keep DIAG_HF held and contacts/S4c disabled pending their registered protocols and confirmation wrapper" (`S4C_ROUTE_AVAILABLE = False`).
   - The plan treats the v4 freeze as enough to make DIAG_HF runnable.
   - It requires "frozen code unchanged" for S5 without registering the S4c confirmation wrapper.

9. **Three DIAG procedure gaps.**
   - Each state-only DIAG run must be appended to `config/sealed_runs.json` as soon as it starts. Otherwise `regress_sealed_aware.py` exits 2 (l.8–9, l.20). The A41 pre-launch gate is also missing from Z4.
   - The Z2 audit templates fit UNRESOLVED only. A FIRED nominal or SRH gate needs the design's KCL, CR.TOLER and deck audit (l.304).
   - Run `hc_explains` before reading any verdict text for an audit (A41(d): "before any other output of that run is inspected").

10. **The A1 timeout is "set in PA-1".** The register allows only a continuation repair, and §4.2 calls timeout changes without an amendment illegitimate. Log the timeout explicitly as part of the amendment.

11. **Two registered items are missing.** The H-J reporting rule ("two-film fit reported first", register l.302) and the H-D nested ℓ = 0 comparison appear nowhere in blocks G and H.

---

## REPORT

1. **The reserve figures are misleading** (§1.1 and §7.4). The plan path has 37 non-matrix launches: A1 1, C 2, D 3, E3 1, 3-D NC 15, P 12 and repairs 3 (CALCULATED). Against an effective reserve of 9, the "9 → 6/4" figures mislead. Only "183 remaining" binds.

2. **Two savings figures are off** (§4.1).
   - S3-04/07 ("saves 2") are already register keep-outs, so they save nothing against the registered path.
   - The S6 early exit saves 22 − 12 = 10, not "≤ 12" (CALCULATED from Block I).

3. **Block D's minimum of 3 is too high.** T2b is skipped if T2a runs out of memory, and T1a may be predicted to run out of memory. The minimum is 1–2.

4. **T1a has a high out-of-memory risk.** It is predicted at 3.75–3.79 GB against a 3.9 GB rule, from a one-point linear model (ASSUMED). Calibrate the model on an unsealed run before spending the launch.

5. **PA-7 lacks the hold's required form.** The hold requires "its own plan labelled exploratory" for kept-out entries. PA-7 (S2-05/07) does not say this.

6. **The prospective layer is charged to the C10 cap.** The user approved the cap for a "DFT-informed campaign with SRH, tunnelling and realistic models" (`solver.yaml` l.18). Confirm that P1–P4 count under it.

7. **The cut order omits two registered items.** It does not list the 3-D NC branch or S7.

8. **The DIAG time sum is slightly off.** The typical sum from §2.2 is 6.5 h, not 6.3 h (CALCULATED).

9. **IGZO +0.30 runs after S3-10.** That is against register order (step 3 before step 4). The Codex ruling the plan requests should cover the order.

---

## Checks that passed

- **Launch counts.** 77 of 260 global launches used; 17 of 200 C10 launches (run_0061 to run_0077) (CALCULATED from RUN_INDEX run_id and label).
- **DIAG.** The order equals `config/campaign_C10_DIAG.json` (sha256 430a6d1a…, 19 entries, 4 gates). The timeout sum is 37,500 s = 10.42 h (CALCULATED).
- **A41(d).** Labels, DOS2-first order, at most 2 launches per mechanism and at most 6 in total, OOM → UNRESOLVED, and a REG/PIN-only scorer amendment all match the register (l.1785–1843).
- **S2-11 numbers reproduce from the allowed JSON** (COMPUTED (ATLAS); arithmetic CALCULATED):
  - 73 of 75 points > 0.1 dec;
  - −3 V: 2.7461e-12 → 5.67472e-12 A/µm;
  - −2.0 V: +0.26 / +0.50 dec; −1.8 V: −0.81 / +0.70 dec (each relative to the floor, original / halved mesh);
  - window spans 11.62 / 12.23 dec;
  - V_G ≥ −0.45 V: 54 points from −0.44 to −0.17 dec, median −0.351 dec.
- **Block arithmetic.** 138 / 170 / 210 and 150 / 182 / 242 add up (CALCULATED).
- **Sealing.** The plan's handling of runs 0075–0077, AFF-6p3 and STRIP-6p3 (PA-17) matches the work chat (l.4641, 4649).
- **Blind rule.** No amorphous DFT quantity is used. The HSE ratio comes from `dft_inputs.json` and N_v from the crystalline study.
- **TCAD rule and run preferences.**
  - Every new statement form (FNORD, TAT.SLICEPTS, QTX/QTY.MESH, SHAPEOX, BQP, IGZO region fallback, Schottky, nc.f) is routed through Codex plus the 5.28 lines.
  - Launches are sequential, sweeps stepped and structures full.
  - Manual l.13716–13722 and l.14499–14505 match the plan's statements.
