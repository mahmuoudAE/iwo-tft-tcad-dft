# Prompt 2: Codex independent review of NATURE_PLAN (task RQ-005)

## Before you paste it

- Give Codex access to this private repository at the commit that contains `handoffs/CLAUDE_TO_CODEX.md` (HO-001).
- Codex must also be able to read the public repository at commit `f315b78`.
- Suggested level: High. Escalate to xHigh only if it finds a serious disagreement.

## Paste this

```text
You are the independent scientific reviewer of the IWO project. AGENTS.md has your rules.

Read 00_PROJECT_CHARTER.md, 01_CURRENT_STATE.md, 02_RESEARCH_QUESTIONS.md and 03_CLAIMS_LEDGER.yaml.
Then read ONLY Part A of handoffs/CLAUDE_TO_CODEX.md (HO-001) and inspect the underlying evidence yourself
in https://github.com/mahmuoudAE/iwo-tft-tcad-dft at commit f315b78 (start with data/experimental_clean.csv,
analysis_2026-10-06_extraction/, analysis_2026-10-06_V2/T2_T3_RESULTS.md, analysis_2026-09-25/SYNTHESIS.md),
and the paper in sources/.

Do not assume Claude's plan is correct. Do not optimise for Nature. Your goal is to decide whether the proposed
programme is the fastest credible route to a genuinely important and defensible result.

STEP 1: write codex/independent_reviews/RQ-005_independent_assessment.md with your OWN reading of the evidence:
what the data do and do not support, your own competing hypotheses, and the cheapest discriminating tests.
Commit it.

STEP 2: only then read Part B of HO-001 and claude/NATURE_PLAN.md, and review these propositions:
A. Is "no target-device-specific post-hoc fitting" (globally calibrated, frozen, true holdouts) the right standard?
   What would make it convincing to a referee?
B. Is sub-1-nm IWO the highest-information experiment, or a dense 3-15 nm thickness x W-content matrix?
C. Is a 2T0C / two-tier application necessary for the central science, or a distraction until the mechanism is settled?
D. Should the 6.3 nm failure be treated first as device-to-device or process variation? What evidence would change that?
E. Which measurements resolve the mobility and SS disagreement with the published paper?
F. How much of the W / trap / interface / "crossover" mechanism has the published paper already claimed
   (Sec. 2.3, 2.5)? What remains new?
G. Does amorphous DFT materially increase causal confidence? If so, what is the minimum set of calculations?
H. What is the smallest prospective blind prediction that would separate a predictive physical model from a post-hoc fit?
I. Which experiments give the most information per fabrication run?
J. Which claim in NATURE_PLAN is most likely to fail?
K. Does the existing data (incl. the 31.8 nm device that never turns off) support H1 (critical thickness) more than
   a smooth law with device spread? Give a quantitative argument or say it cannot be decided.

For every major proposal give ACCEPT / MODIFY / DEFER / REJECT, with the reasoning.

Then give exactly:
TOP THREE ACTIONS FOR THE NEXT 30 DAYS
TOP THREE THINGS NOT TO DO YET
SINGLE MOST IMPORTANT BLIND TEST
SINGLE MOST IMPORTANT EXPERIMENT
SINGLE MOST IMPORTANT COMPUTATIONAL TEST
RESULT THAT WOULD MOST RAISE THE PUBLICATION CEILING
RESULT THAT WOULD KILL THE CURRENT CENTRAL HYPOTHESIS

Write codex/independent_reviews/NATURE_PLAN_REVIEW.md, add a short entry in handoffs/CODEX_TO_CLAUDE.md, and commit.
Do not edit Claude's files.
```
