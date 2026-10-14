# Complete plan: 10–21 October 2026 (CERN + ATLAS, no new measurements)

Status: PROPOSED by Claude on 2026-10-10. It becomes the plan when Mahmoud records it in `05_DECISION_LOG.md`.
Timeline PDF: `claude/plans/CERN_DFT_timeline_2026-10.pdf`.

## 0. Situation and goal

**Resources:**
- the four measured curves and the published paper (Januar et al. 2026);
- CERN lxplus/HTCondor until **21 Oct** (target: all jobs finished by **15 Oct**);
- local Silvaco ATLAS (60 of 71 launches used).

No new measurements are possible.

**Goal:** the strongest defensible thesis, plus a journal paper. Every fitted TCAD law that can be replaced by a computed one is replaced. Everything that cannot be tested is stated as a limitation or a prediction.

**Checked on 10 Oct:**
- CERN works: tools present, about 5,500 free cores, A100/H100/H200 GPUs, GitHub reachable.
- AFS was cleaned from 86 % to 18 %.
- RQ-001 is closed for now: the paper's mobility and SS numbers can be explained by definitions. Our definitions are reported; the fab's recipe is unconfirmed.

## 1. The questions the defence must answer, and how

| # | Question | Answered by |
|---|---|---|
| Q1 | The DFT is crystalline but the films are amorphous; does that matter? | Amorphous slab series (section 2A) |
| Q2 | Can the thickness laws in the TCAD be computed instead of fitted? (Confinement, tail density and width, conduction-band shift, surface vs interior traps.) | Slab series, studies 1–7 |
| Q3 | Does W really suppress oxygen vacancies, and by how much? | Vacancy jobs |
| Q4 | What do the gate-oxide (Al₂O₃) interface and the top surface do to the channel? | Interface job; surface variants (if time) |
| Q5 | Where does the off-current floor come from? | ATLAS A2 (real geometry); its prediction for drain-voltage dependence is written down for any future measurement |
| Q6 | Why does 31.8 nm never turn off? Where is the "critical thickness"? | ATLAS A3, plus 1-D electrostatics |
| Q7 | Do DFT-derived traps explain the measured mobility shape (12 / 11 / 50 cm²/Vs) without fitting it? | ATLAS A4 (DFT inputs → μ_FE, same protocol) |
| Q8 | Why do our mobility and SS differ from the paper's? | RQ-001 (done): definitions. Report ours with their definitions. |

## 2. Computations

### 2A. CERN DFT: amorphous slab series (priority 1, protected)

Pipeline per structure, one HTCondor DAG:

```
[GPU] ML melt-and-quench (MACE-MP-0) → QC gate → [CPU/GPU] DFT relax (≤20 h segments, restartable) → SCF → DOS/IPR → summary
```

**QC gate:** density, In–O bond lengths and coordination must lie in the expected range before any DFT time is spent.

| Slab | In-plane cell | Atoms (+H) | W | Twin | Estimated DFT time |
|---|---|---|---|---|---|
| 2.0 nm | 1.05 × 1.05 nm | ~170 | 1 W = 1.5 % | a-In₂O₃ | 2–4 days |
| 1.5 nm | 1.05 × 1.05 nm | ~125 | 1 W = 2.0 % | a-In₂O₃ | 1–2 days |
| 1.0 nm | 1.29 × 1.29 nm | ~125 | 1 W = 2.0 % | a-In₂O₃ | 1–2 days |
| 0.8 nm | 1.44 × 1.44 nm | ~125 | 1 W = 2.0 % | a-In₂O₃ | 1–2 days |
| 0.7 nm | 1.54 × 1.54 nm | ~125 | 1 W = 2.0 % | a-In₂O₃ | 1–2 days |

There are 10 structures, one sample each. Surfaces are terminated as in the crystalline slabs (H/OH).

**Studies on every slab:**
1. structure: coordination, defect sites, W site, surface OH;
2. band gap against thickness (HSE-corrected ratio);
3. tail width below the conduction band (against TCAD W_TA = 40 meV);
4. localization (IPR);
5. W donor level, charge and Fermi level;
6. surface against interior DOS (tests N_s + N_b·t);
7. electron affinity against thickness (the ΔE_c law).

**Mobility-related outputs (analysis only):**
- m* against thickness;
- free fraction n_free/n_total against Fermi level;
- surface height fluctuation (roughness Δ).

### 2B. Other CERN jobs

| Priority | Job | Structure | Estimate |
|---|---|---|---|
| 2 | ML-structure check: short DFT MD of the ML-made 80-atom a-bulk; compare bonds, coordination, tails | 80 atoms | ~1 day |
| 3 | Oxygen vacancy near W, far from W, and in pure In₂O₃ (neutral) | 79-atom crystal cells, 3 jobs | ~1 day |
| 4 | a-Al₂O₃ / a-IWO interface, 1 nm per side: band offset, interface states (→ D_it, Q_f) | ~190 atoms, 2 jobs | 2–3 days |
| 5 | Extras, only if on schedule: 0.7 nm surface variants, second samples, HfO₂ interface | — | 1–2 days |
| free | 2 nm crystalline W-slab analysis; Pd barrier estimate = WF(Pd) − EA(IWO) | existing outputs | hours |

### 2C. ATLAS (local; about 15–20 launches; the budget must rise from 71 to about 90, your decision)

| | Task | Needs DFT? | When |
|---|---|---|---|
| A2 | Off-current: real geometry with IWO beyond the gate → floor size and thickness scaling; drain-voltage prediction written down | no | 11–14 Oct |
| A3 | 31.8 nm and the critical thickness: which donor density or back-surface charge makes the gate lose control | no | 11–14 Oct |
| A1 | Surface + bulk traps with shared parameters, leave-one-film-out (fit two films, predict the third) | partly | 13–16 Oct |
| A4 | DFT tails, ΔE_c and interface states replace the fitted values → μ_FE and SS against measured | yes | 15–17 Oct |

## 3. Infrastructure and roles

### 3A. CERN execution (the laptop can be off)
- The ML environment is built once on lxplus and packed to EOS. The QE environment already is.
- All job files and outputs live on **EOS** (1 TB). AFS (2 GB) holds only the deploy key.
- Segments of at most 20 h with restart: every segment starts with fresh Kerberos/EOS credentials.

### 3B. Automatic runner (WF-001 design → WF-002 build)

```
ticket (jobs/requests/<id>.yaml, fixed templates only)
  → Mahmoud merges = approval (works from the phone)
  → acron on lxplus, every ~20 min: validate → submit DAG → record status
  → results pushed to github.com/mahmuoudAE/iwo-dft-jobs (private)
```

**Safety:**
- whitelisted templates only;
- caps on cores, memory and concurrent jobs;
- no new long jobs after 16 Oct; hard stop on 20 Oct;
- a deploy key limited to the jobs repo, created by Mahmoud.

**Wave 1** is submitted by hand today as DAGs, so no CERN time is lost while the runner is built.

### 3C. Who does what

| Role | Work |
|---|---|
| **Claude** | WF-001 design; DFT inputs and templates; QC; analysis; ATLAS; the record (ledger, handoffs) |
| **Codex** (gpt-6.1-sol, high) | Reviews WF-001; owns WF-002 (runner build and test); independent reviews of central results through the relay |
| **Astra** (optional) | Arbitration if Claude and Codex disagree on a central result |
| **Mahmoud** | Approvals (merge tickets); part C (repo and deploy key); acron OK; ATLAS budget; final decisions |

## 4. Timeline

| Date | Work |
|---|---|
| **10 Oct** | Build the ML environment on CERN; ML structures on GPU; QC; timing test; **submit wave 1** (slab series, ML check). Claude writes WF-001; Codex reviews it. |
| **11 Oct** | Submit wave 2 (vacancies, interface). Codex builds the runner (WF-002); Mahmoud does part C; end-to-end test with a 5-min job. ATLAS A2/A3 start. |
| **12–13 Oct** | Short jobs finish and are analysed. Runner live: wave 3 goes through tickets, only if on schedule. |
| **14–15 Oct** | Slab series finishes. **Target: everything done on 15 Oct.** |
| **15–17 Oct** | Full analysis; ATLAS A1/A4 with DFT inputs; Codex reviews the key results (relay). |
| 16 Oct | Last submission of any job longer than 2 days (fallback). |
| 18 Oct | Last submission of any job. |
| 19–20 Oct | All results verified on EOS, GitHub and the PC. |
| 21 Oct | CERN access ends; nothing should still be running. |
| 17 Oct onward | Write-up and thesis figures. |

## 5. Gates and cut order

| Gate | When | Check | If it fails |
|---|---|---|---|
| G1 | 10 Oct | The QC gate on the ML structures passes | Fix the ML protocol, or fall back to a short DFT melt-and-quench for the 0.7–1 nm slabs |
| G2 | 11 Oct | The timing test fits the 15 Oct target | Drop In₂O₃ twins at 1.5 / 0.8 nm, then the interface |
| G3 | 13 Oct | Wave 1 is on schedule | Wave 3 is not submitted |
| G4 | 15 Oct | All protected jobs are finished | Use the fallback dates (16 / 18 Oct) for protected jobs only |

**Cut order:**
1. extras;
2. interface;
3. In₂O₃ twins at 1.5 / 0.8 nm;
4. vacancies.

**Protected:**
- all five a-IWO slabs;
- the 2 nm In₂O₃ twin;
- the ML check.

## 6. Risks

| Risk | Mitigation |
|---|---|
| The ML (GPU) build fails on CERN drivers | Fall back to CPU nodes |
| The ML structures are unrealistic | QC gate plus the ML-structure check; report the comparison |
| Queue waits or GPU shortage | Submit early; CPU fallback; cut order |
| Credential expiry in long jobs | ≤ 20 h segments; restart files; no `condor_release` of jobs running for more than 1 h |
| The runner is not ready in time | Waves 1 and 2 are submitted by hand; the runner only handles wave 3 and later |
| PBE gaps, small cells, single samples | Trends and widths, not absolute values; stated as limitations at the defence |

## 7. Deliverables for the defence and the paper

1. Thickness laws from DFT (amorphous), compared with the fitted TCAD laws: gap, tail density and width, ΔE_c, surface vs interior.
2. W effect: localization (IPR), vacancy energies, donor behaviour; amorphous against crystalline.
3. Gate interface: band offset and interface states, compared with the fitted D_it and Q_f.
4. ATLAS:
   - off-current geometry, with the written-down drain-voltage prediction;
   - critical thickness, including the 31.8 nm device;
   - DFT-informed μ_FE and SS compared with the measurements.
5. The record: RQ-001 (definitions), the claims ledger, the registered predictions, and all reviews and limitations.

## 8. Your checklist

- [ ] **"go"**: ML on CERN, wave 1.
- [ ] Part C: the private `iwo-dft-jobs` repo and the deploy key (commands in the chat of 10 Oct).
- [ ] OK the acron entry once the runner is tested.
- [ ] ATLAS budget from 71 to about 90 launches.
- [ ] Record this plan in `05_DECISION_LOG.md`, or tell Claude to record it.
