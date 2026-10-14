I've written the response to Codex's review in `claude/responses_to_codex/RQ-001_response.md`. Codex raised 17 objections:

| Class | Count | Objections |
|---|---|---|
| ACCEPTED | 11 | O1, O2, O4, O5, O7, O8, O9, O11, O12, O14, O15 |
| PARTIALLY ACCEPTED | 2 | O10 (validity depends on the threshold definition), O13 (rounding test) |
| EVIDENCE DISAGREES | 0 | — |
| UNRESOLVED | 4 | O3 (paper Fig. 5d), O6 (2 nm switching), O16 (numbers Codex didn't check), O17 (SS might be a fitted parameter) |

Codex's review was not fully blinded: its first-phase assessment saw my interpretation section before it was written. It re-implemented the main numbers independently and found no differences.

**Main corrections:**
- **Paper's mobility formula.** My handoff said the paper "with high probability" took μ_max as the peak of the saturation-formula mobility. It is now only the "leading candidate", with no probability stated. The three matching peaks fix only the combined product of capacitance, width/length and current scaling, and two other formulas also fit with one free factor.
- **Mobility gap explained.** I had written that the earlier factor-of-two mobility gap was "a definition difference, not different data". The revised text says a definition difference is enough to explain it on our curves. Whether the paper used these same curves is not established.
- **Noise test was weaker than I claimed (O5).** Re-reading my own code found two gaps Codex did not name:
  - The Monte Carlo noise test (2000 draws) covered only two estimators, both starting 10× above the off-current floor. It did not test the 1–3× estimators that actually match the paper.
  - It used noise measured at 1e-12 to 1e-10 A/µm. The steep 2 nm section sits 1–2 decades lower.

  "Noise does not create the steep section" is therefore withdrawn. Whether that section is real channel behaviour or an instrument effect is open.
- **Saturation formula's validity (O10).** Codex's threshold voltages from a constant-current criterion give overdrives of 1.09, 1.91 and 0.87 V (2.0, 6.3, 13.2 nm), all above the 0.7 V drain bias. I checked this by hand. The formula is therefore outside its valid range at the 6.3 nm peak under all three threshold definitions, and in every film under this third one. My original wording understated this. The statement is still conditional, because no threshold definition is a measured regime boundary.

**Files changed** (each change logged at the bottom of the file):
- **`handoffs/CLAUDE_TO_CODEX.md`:** HO-002's interpretation section revised in place, with the original wording kept in the change log. Part A (evidence) is unchanged. I also added a short entry at the top pointing to the response.
- **`03_CLAIMS_LEDGER.yaml`:** no status changes; Codex proposed none and I found none warranted. The wording of claim C031 and the caveats of C024, C025 and C030–C033 were revised, each with a history line.
- **`01_CURRENT_STATE.md`:** the two RQ-001 summary points reworded.
- **`04_TASK_QUEUE.yaml`:** RQ-001 is now "REVIEWED (MODIFY); waiting on HUM-001 fab answers".
- **`claude/evidence/RQ-001/README.md`:** fab questions 1 and 3 extended.

Both YAML files still parse. Scripts and their outputs were not touched. No commit, push, ATLAS run or CERN action was made.

**Decisions for you:**
1. **Ask the fab now?** Options: (a) send the six questions now, asking for the original extraction script or spreadsheet and the data behind paper Figs. 1b and 5d; (b) bundle them with the RQ-003 measurement request; (c) don't ask, and report only our own definitions. **I recommend (a).** It is the cheapest way to tell "same recipe" from "numerical coincidence", and it needs no compute.
2. **Repeat measurements of the 2 nm steep section?** These would be finer and repeated sweeps, with gate current and instrument settings recorded. Options: (a) request them now, registering the checks first; (b) request them only if the fab's documents leave the question open; (c) never request them, and report near-floor SS as a value that depends on the method. **I recommend (b), with the registration drafted now** so the checks are fixed before any data arrive. This can share chip time with RQ-003.
3. **Fresh, fully blinded reviewer?** Options: (a) accept the current review; (b) get a reviewer who hasn't seen the interpretation. **I recommend (a) for now, and (b) only if C031 or C032 is to become a central claim in the thesis or a paper.**
