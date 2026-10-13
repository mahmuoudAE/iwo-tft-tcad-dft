"""Write the run_campaign.py plan files of the 2026-10-10 campaign from campaign_matrix.json and verify them (NO launch).

Each entry is the matrix 'campaign_entry' copied verbatim (id, thickness, label, overrides, timeout, purpose[, mode]) in
matrix order; annotation keys that run_campaign.py ignores are added (stage, matrix_status, requires_code, depends_on,
pre_registered_expectation, min_set_rank). Stop rules are written as top-level fields: run_campaign.py does NOT enforce
them (it records a failed launch and continues); the main session applies them between plan files (IMPLEMENTATION.md).
2026-10-13: exception, campaign_C10_DIAG.json also carries executable "gates" (GATES below; scripts/campaign_gates.py): the S2 null-test
stop rule, evaluated by run_campaign.py with the frozen scorer, and the "state_only" surface (STATE_ONLY; scripts/campaign_sealed.py);
--check verifies both. Its global rule on stop enforcement is replaced by GATED_GLOBAL_RULE (Codex D8).

  python analysis_2026-10-10_campaign/make_campaign_configs.py            write + verify config/campaign_C10_*.json
  python analysis_2026-10-10_campaign/make_campaign_configs.py --check    verify only
  python analysis_2026-10-10_campaign/make_campaign_configs.py --remaining PLAN.json [SUMMARY.json ...] [--skip ID ...]
        write PLAN_remaining.json without the ids that already have a run_dir in any results/campaigns summary given
        (use after the MIN10 plan, whose ids also appear in the stage plans; run_campaign resumes only per plan file),
        and without the ids after --skip (e.g. S3-04 S3-07, whose decks are solver-identical to S0-01).
Files written: config/campaign_C10_*.json (runnable) and config/campaign_C10_*.template.json (adaptive / after-calibration
entries whose overrides contain {generated}/{frozen model} tokens: NOT runnable until those are resolved). 2026-10-11: also
config/campaign_C10_DIAGa_S2-11.json and campaign_C10_DIAG.json (frozen-register diagnostic set, register order, S2-11 first).
2026-10-11 review: the S2/S3 stage plans and MIN10 are written with runnable=false (HOLD: they hold entries the register keeps out
or makes conditional, and MIN10/S2 do not start with S2-11); the 5 H-F entries are split into campaign_C10_DIAG_HF.json, runnable=false
until the H-F scoring is implemented and frozen. scripts/run_campaign.py refuses a plan with runnable=false.
2026-10-13 (register amendment A41; launch only after A41 is logged and Codex has reviewed it): the matrix entry S0-02-DOS2 (stage
S2_resolution_refinements) is covered by the held stage plan campaign_C10_S2r_resolution.json and runs only from the new state-only plan
config/campaign_C10_DIAGb.json (the S2-11 rerun, then S0-02-DOS2: Codex GO-WITH-CHANGES, work chat 2026-10-13T01:32Z, item 3; the A41
pre-launch gate before EVERY invocation, including a resume; --retry S2-11 by the STARTED-row rule in DIAGB_RULES).
campaign_C10_DIAGa_S2-11.json is now written with runnable=false (HOLD: superseded by DIAGb; invoking it would reuse run_0075, or later the
rerun, and its non-state-only summary would copy that run's metrics into results/campaigns). Every other plan file is unchanged, except the
order wording in the HOLD text of the held campaign_C10_S2r_resolution.json (A41 revision 3); --check verifies DIAGb (ids in launch order,
verbatim entries, runnable, no gates, state_only, stop rules, launch command).
"""
import json
import sys
from pathlib import Path

import campaign_tools as ct

CFG = ct.PKG / 'config'
MIN10 = ['S0-01', 'S0-02', 'S1-01', 'S1-02', 'S2-01', 'S2-08', 'S2-14', 'S2-15', 'S1-07', 'S3-12']   # CAMPAIGN_DESIGN 9, launch order
# 2026-10-11: diagnostic set of the frozen register (register-rev2-frozen-20261010T1833Z, section 3) in its launch order: S2 with S2-11
# first; S3 confinement then AFF; IGZO with S3-27; S3-10. Within S2 after S2-11: nominal leakage, generation, worst/TAT, strips (Claude
# decision 2026-10-10; not frozen). S6-13 and S6-15 (the other 2 of the 26) follow S4c (order step 8, '{frozen model}' template entries).
DIAG = ['S2-11', 'S2-04', 'S2-06', 'S2-03', 'S2-01', 'S2-02', 'S2-08', 'S2-12', 'S2-13', 'S2-14', 'S2-15', 'S2-16', 'S2-17', 'STRIP-6p3',
        'S3-01', 'S3-02', 'S3-03', 'AFF-2p0', 'AFF-6p3', 'S3-11', 'S3-12', 'S3-13', 'S3-27', 'S3-10']
DIAG_HF = DIAG[-5:]   # H-F (IGZO with S3-27, then S3-10): scored by no frozen code yet (register H-F; review 2026-10-11) -> held
DIAG_PLANS = (('campaign_C10_DIAGa_S2-11', DIAG[:1]), ('campaign_C10_DIAG', DIAG[:-5]), ('campaign_C10_DIAG_HF', DIAG_HF))
REG_TAG = 'register-rev2-frozen-20261010T1833Z'
HOLD = {   # 2026-10-11 review: plan files written with runnable=false (scripts/run_campaign.py refuses them); reason in 'not_runnable_reason'
    'campaign_C10_S2_offfloor': f'Frozen register ({REG_TAG}) section 3: this stage plan holds entries the register keeps out (S2-05, S2-07, '
                                'and the FNORD duplicates S2-09, S2-10) and starts with S2-01, not S2-11 (S2 order: S2-11 first). The register route is '
                                'campaign_C10_DIAGa_S2-11, then campaign_C10_DIAG. A kept-out entry needs a logged register amendment and its own plan labelled exploratory.',
    'campaign_C10_S3_branches': f'Frozen register ({REG_TAG}) section 3: this stage plan holds kept-out entries (S3-04, S3-07 duplicates; S3-24, S3-25 BQP; '
                                'S3-26 Boltzmann), the trigger-gated contacts S3-17..S3-23 (H-F trigger: 6.3 nm shape RMSE > 0.15 dec after S3-10..13, not yet '
                                'evaluated) and later-order entries (tail runs S3-05/06/08/09, IGZO GAMMA0 +0.30 S3-14..16). The diagnostic S3/AFF entries run '
                                'from campaign_C10_DIAG / campaign_C10_DIAG_HF. Anything else needs a logged register amendment or the frozen trigger, in its own plan.',
    'campaign_C10_MIN10': f'Superseded by the frozen register order ({REG_TAG}, section 3: S2-11 first): MIN10 would launch S2-01, S2-08, S2-14, S2-15 '
                          'before S2-11. Its launched entries (S0-01, S0-02, S1-01, S1-02, S1-07) are done; the rest run from campaign_C10_DIAG(_HF).',
    'campaign_C10_DIAG_HF': f'H-F entries of the register diagnostic set ({REG_TAG}): no frozen code scores the H-F predictions yet (two-film reference '
                            'shift/scale, baseline shape RMSE, IGZO gain and gamma targets, contact trigger). Implement and freeze that scoring (logged), then '
                            'set runnable to true. Order: after campaign_C10_DIAG (register section 3, steps 3-4).',
    'campaign_C10_S2r_resolution': f'Register amendment A41 (2026-10-13; added to {REG_TAG} after the freeze, not part of the frozen 26-launch diagnostic set): '
                                   'S0-02-DOS2 runs only from campaign_C10_DIAGb (the S2-11 rerun, then S0-02-DOS2), after A41 and the resolution-method '
                                   'sign-off are logged and Codex has reviewed A41. Matched oxide-mesh refinements under the frozen A41 trigger get their own '
                                   'plan only after the trigger has fired and is logged.',
    'campaign_C10_DIAGa_S2-11': 'Superseded by register amendment A41 (2026-10-13): the S2-11 rerun runs from campaign_C10_DIAGb only. S2-11 ran from this '
                                'plan once, as run_0075 (timed out, invalid for scoring under the frozen scorer, sealed, never substituted). Invoking this '
                                'plan would reuse run_0075 (or later the rerun) by its label, and because this plan is not state-only its summary would '
                                'copy that run\'s metrics into results/campaigns/campaign_C10_DIAGa_S2-11.json.'}
GLOBAL_RULES = [
    'Sequential only: python scripts/run_campaign.py <plan> (C10 plans refuse --workers != 1). Every launch counts, failed or not. Hard cap 200: config/solver.yaml max_launches 260 (= 60 used before C10 + 200) and a C10 label counter (c10_* run IDs in RUN_INDEX <= 200) in run_campaign.py.',
    'run_campaign.py (C10 plans) never re-launches an entry whose label already has a RUN_INDEX row, from this or any other C10 plan (MIN10 vs stage plans): a successful earlier launch is reused, a failed one is reported; --retry ID spends a new (reserve) launch on purpose.',
    'Model file for every entry: $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml" (V3 + the overrides = the same solver statements as V2 + the overrides, check_v3_equivalence.py).',
    'After any code change: python analysis_2026-10-10_campaign/regress_all_decks.py must print "unexpected differences 0" before the next launch.',
    'run_campaign.py records a failed launch and CONTINUES; it does not apply any stop rule below. The main session reads results/campaigns/<plan>.json and analysis_2026-10-10_campaign/post_run_checks.py output after each plan and decides.',
]
PLANS = [   # (file stem, stage(s) or ids, stop rules) in launch order
    ('campaign_C10_S0a_smoke', ['S0-01'], [
        'S0 STOP: a syntax error, an option not active (post_run_checks.py OPTION_NOT_ACTIVE, exit 1) or a KCL failure stops the campaign until the code is fixed. UNVERIFIED (exit 3) also stops: read deckbuild.out by hand and record the evidence before going on.',
        'S0-01 deck header must show chi 4.0184 eV, NC300 1.373e19 cm^-3, MUN 12.977 cm2/Vs, Qf 1.383e12 cm^-2 (check_v3_equivalence.py verifies this before launch).',
        'Launch S0b only after S0-01 passed (separate file because run_campaign continues after failures).']),
    ('campaign_C10_S0b_smoke', ['S0-02'], [
        'S0 STOP as above; S0-02 must show a non-zero signed I_G with KCL closing (post_run_checks.py: QTNLSC ACTIVE; I_G was exactly 0 in all 51 earlier runs).',
        'At most 3 reserve launches on S0 repairs. If S0-02 still fails: gate tunnelling is reported as not implementable here; the leakage test falls back to the CALCULATED bounds plus the oxide-TAT runs (remove S2-04..S2-11 from the S2 plan).']),
    ('campaign_C10_S1_baselines', ['S1_baseline_numerics'], [
        'Numerics: mesh x0.7 (S1-03) or DOS x2 (S1-04) changing active RMSE by > 0.01 dec, Vth_cc by > 5 mV or SS by > 3 mV/dec -> adopt the refined setting for every later run (reserve) and repeat the affected baselines. Evaluate with campaign_extract.py compare <S1-03> <S1-02> --rule numerics (and <S1-04> <S0-01>).',
        'S1-05 (3-D NC at 2 nm) must shift Vth_cc by +40..+70 mV vs S0-01 (campaign_extract.py compare <S1-05> <S0-01> --rule s1_05); otherwise audit the NC override before S3.',
        'S1-06 (two carriers) changing I_D by > 1e-3 relative above 1e-14 A/um vs S1-02 (campaign_extract.py compare <S1-06> <S1-02> --rule s1_06) -> all later runs use carriers=2 with timeout x1.5.',
        'S1-07 vs transformed S0-01 (Qf +1e12, MUN x0.6) > 0.01 dec on any J-window point (profile_shared.py check <S1-07> <S0-01>) -> offline profiling is approximate: every S4b candidate is run natively at the profiled Qf and MUN.']),
    ('campaign_C10_S2_offfloor', ['S2_offfloor_mechanisms'], [
        'A NOMINAL or SRH null test producing floor-scale current contradicts the CALCULATED bounds: stop, audit KCL / CR.TOLER / deck, do not fit.',
        'Floor-scale current from the WORST-case oxide set is an allowed result; interpret it only after S2-11 (oxide mesh x0.5) agrees within 0.1 dec in log10 I_G.',
        'Strip decks (S2-14..17) must give I(0.7 V)/I(0.1 V) = 7.0 +- 0.5; otherwise the strip is not ohmic in ATLAS and that is the result.',
        'Verdicts by the pre-registered rule of CAMPAIGN_DESIGN 7.2 (valid points >= 80 %, |d_floor_ratio| <= 0.5 dec, |slope| <= 2|measured| + 2 sigma, KCL); a 2 nm underprediction does not falsify.',
        'S2-12/S2-13 (QTNLSC + oxide TAT, trap charge out of Poisson): post_run_checks.py needs --gate-control S2-04 (2.0 nm) / S2-06 (13.2 nm) to identify ITAT separately; the charged-oxide electrostatics are not tested by these runs.',
        'S2-09/S2-10 (FNORD): F.AE/F.BE are the HfO2-barrier constants transferred to the Al2O3/IWO-segment field (A/r^2, r B, r = 2.1744); still a single-barrier approximation.']),
    ('campaign_C10_S2r_resolution', ['S2_resolution_refinements'], [   # 2026-10-13, register A41 (held; route: campaign_C10_DIAGb)
        'A41: S0-02-DOS2 (run_0067 settings, DOS 768/384) is the I_G resolution pair for S2-11 (score_register.py resolution_pair <S0-02-DOS2 run> <run_0067> ig_raw_A); '
        'it shares run_0067 with the S2-11 comparison (recorded, never independent). A non-qualifying pair leaves S2-11 PROVISIONAL; no second DOS run.']),
    ('campaign_C10_S3_branches', ['S3_model_branches'], [
        'Branch adopted only if sqrt(J) improves by >= 0.03 dec with no film RMSE_sub or RMSE_on worse by > 0.03 dec (profile_shared.py adopt <branch triple> -- <S0-01 S1-01 S1-02>), converged at all 3 films, activation ACTIVE_AS_REQUESTED in post_run_checks.py.',
        'At most two branches; IGZO needs S3-27 within 0.01 dec of the transformed curve for exact profiling; Schottky needs one reserve launch of the same native check.',
        'A branch whose only effect is a rigid shift or uniform scale is rejected. Branch choices are data-selected and reported as such.',
        'If a branch is adopted, S4a candidates must be regenerated with that branch (this plan file assumes NO branch: re-run make_campaign_matrix.py / this script after the decision).']),
    ('campaign_C10_S4a_spacefilling', ['S4a_calibration_spacefilling'], [
        'Valid as written only if S3 adopted NO branch; S4A-01-* are then identical to S0-01/S1-01/S1-02 and are NOT launched (remove them; 3 launches return to the reserve).',
        'After S4a: best sqrt(J) > 0.30 dec with systematic residuals (same-sign 6.3 nm on-state error for >= 80 % of candidates) -> skip S4b, run S4c on the best, go to S5, report the shared model as failed. No per-film rescue parameters.']),
]
TEMPLATES = [
    ('campaign_C10_S4b_adaptive.template', ['S4b_calibration_adaptive'], ['S4b stops early when 3 successive candidates improve sqrt(J) by < 0.01 dec (unused launches return to the reserve).']),
    ('campaign_C10_S4cd_confirm.template', ['S4c_native_confirmation', 'S4d_runner_up_branch'], ['S4c: profiled vs native > 0.01 dec -> native result reported and profiling audited before S5.']),
    ('campaign_C10_S5_loo.template', ['S5_leave_one_film_out'], ['Branches re-selected inside each fold from the training films S3 results only; held-out film never tuned; any held-out film failing CAMPAIGN_DESIGN 5.3 falsifies transferability (reported, not repaired).']),
    ('campaign_C10_S6_sensitivity.template', ['S6_sensitivity_frozen'], ['No stop rule; every result reported. Early exit: if S4 failed and S5 confirms on >= 2 folds, S6 is cut to S6-01..06, S6-23..26 (10 launches).',
                                                                         'S6-27 (in-solver strip) needs solver.physics_options.strip.wl_par_per_um=<(W/L)_par fitted on the S2/S6 strip decks> in its overrides.']),
    ('campaign_C10_S7_31p8.template', ['S7_31p8_stress'], ['No stop rule; failure (31.8 nm never turning off not reproduced) is documented, never fitted.']),
]
KEEP = ('id', 'thickness', 'label', 'overrides', 'timeout', 'purpose', 'mode')
# 2026-10-13: executable stop gates, written into campaign_C10_DIAG.json only (scripts/campaign_gates.py, run_campaign.py "gates"; Codex
# 2026-10-12T13:18Z: "Split or supervise DIAG at the nominal and generation checkpoints"). Rule CAMPAIGN_DESIGN.md:304. States come from
# the FROZEN scorer (sha256 below; the plan is refused if the file differs). Codex rulings 2026-10-12T20:28Z (CODEX_WORK_CHAT): D1 FIRED and
# UNRESOLVED -> stop for the first DIAG execution, resumed only with --ack-gate + --ack-audit citing the completed audit; D2 the stop on a
# resolved registered-bound exceedance is a prospective, stricter operational rule (rule_basis); D3 S2-03 is a carrier-confounded anomaly
# checkpoint with its own rule id, S2-01/S2-02 stays the matched mechanism test; D7 DIAG is state-only (sealed sidecar); D8 text below.
# Every other plan file is unchanged.
GATE_SCORER = 'analysis_2026-10-10_campaign/score_register.py'
GATE_SCORER_SHA256 = 'c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a'
GATE_RULE_REF = ('CAMPAIGN_DESIGN.md:304 (S2: a nominal or SRH null test that produces floor-scale current contradicts the CALCULATED bounds: '
                 'stop, audit KCL, CR.TOLER and the deck; do not fit)')
GATE_RULE_BASIS = ('Codex D2 (2026-10-12T20:28Z): stopping on a resolved exceedance of the registered H-C bound (frozen score_register FAIL) is a '
                   'PROSPECTIVE, STRICTER OPERATIONAL RULE; it is not a verbatim implementation of the floor-scale rule of CAMPAIGN_DESIGN.md:304, and '
                   'a FIRED gate is not itself a hypothesis falsification. UNRESOLVED also stops (D1, first DIAG execution).')
ANOMALY_RULE_REF = ('Carrier-confounded anomaly checkpoint (Codex D3, 2026-10-12T20:28Z): S2-03 (2 carriers, SRH/TAT extreme) against S0-01 (1 carrier) '
                    'is the design-defined pair of CAMPAIGN_DESIGN 7.1; its result cannot isolate generation. The matched mechanism test is S2-01 vs '
                    'S2-02 (G-S2-01-generation, register A9).')


def _gate(gid, after, test, runs, note, rule_id='S2-STOP-NULL', rule_ref=GATE_RULE_REF):
    return {'id': gid, 'rule_id': rule_id, 'rule_ref': rule_ref, 'rule_basis': GATE_RULE_BASIS, 'after': after, 'test': test, 'runs': runs,
            'on_fired': 'stop', 'on_unresolved': 'stop', 'scorer': GATE_SCORER, 'scorer_sha256': GATE_SCORER_SHA256, 'note': note}


GATES = {'campaign_C10_DIAG': [
    _gate('G-S2-04-nominal', 'S2-04', 'hc_nominal', {'run': {'entry': 'S2-04'}}, 'QTNLSC nominal, 2.0 nm: register H-C |I_G(-3 V)| <= 1e-2 x floor'),
    _gate('G-S2-06-nominal', 'S2-06', 'hc_nominal', {'run': {'entry': 'S2-06'}}, 'QTNLSC nominal, 13.2 nm: register H-C |I_G(-3 V)| <= 1e-2 x floor'),
    _gate('G-S2-03-anomaly', 'S2-03', 'hc_generation', {'run': {'entry': 'S2-03'}, 'control': {'run_id': 'run_0061', 'label': 'c10_s0_01_2p0'}},
          'S2-03 against S0-01 (run_0061), carrier-confounded: an anomaly checkpoint, not a generation test', rule_id='S2-ANOMALY-CARRIER',
          rule_ref=ANOMALY_RULE_REF),
    _gate('G-S2-01-generation', 'S2-02', 'hc_generation', {'run': {'entry': 'S2-01'}, 'control': {'entry': 'S2-02'}},
          'SRH/TAT null test, 13.2 nm, against its matched SRH-off control S2-02 (register A9; the matched mechanism test); evaluated once S2-02 has run')]}
STATE_ONLY = {'campaign_C10_DIAG': {'sealed_dir': 'results/sealed/campaigns'},   # Codex blocker 3 / D7: scripts/campaign_sealed.py
              'campaign_C10_DIAGb': {'sealed_dir': 'results/sealed/campaigns'}}  # 2026-10-13 A41 (state-only, no gates; DIAGB below)
GATES_ENFORCED_BY = ('AUTOMATIC in run_campaign.py (Codex D8): the launch budget and C10 cap, refusal of runnable=false plans, and the declared '
                     '"gates" (after S2-04, S2-06, S2-03 and S2-02, frozen score_register.py; FIRED or UNRESOLVED stops before the next launch, exit 3, '
                     'until --ack-gate GATE_ID --ack-audit AUDIT_FILE). Every other stop rule of this plan remains MANUAL (main session).')
GATED_GLOBAL_RULE = ('run_campaign.py records a failed launch and CONTINUES, except for the automatic stops of this plan: the launch budget / C10 cap and '
                     'the declared "gates" (see stop_rules_enforced_by). Every other stop rule below is applied manually: the main session reads the '
                     'state-only results/campaigns/<plan>.json and decides.')
# 2026-10-13, register amendment A41 (launch only after A41 is logged and Codex has reviewed it; user go 2026-10-13 ~00:05Z, recorded in the
# work chat 2026-10-13T00:15Z, subject to that review; Codex GO-WITH-CHANGES under the work-chat heading 2026-10-13T01:32Z, applied in A41
# revision 3): S2-11 is rerun once with the committed runner (public-repo 1375164) because run_0075 is invalid under the frozen scorer's
# timeout rule, and the S0-02 DOS x2 resolution run is added (Codex round 3, adaptive amendment). One state-only plan without gates, S2-11
# FIRST, then S0-02-DOS2 (Codex item 3: keeps the register section 3 order, S2-11 first, and simplifies the rerun bookkeeping; it does not
# replace the resume safeguards). S2-11 keeps its registered entry and label (score_register.py REG['hc_mesh'] is keyed on c10_s2_11_2p0, a
# new label would score as a smoke test); the C10 label-reuse rule is passed on purpose by --retry S2-11 (run_campaign.py:206, :216), and only
# while RUN_INDEX has no c10_s2_11_2p0 row newer than run_0075 (STARTED-row rule, DIAGB_RULES[1]). Before EVERY invocation, including a
# resume, the A41 pre-launch gate must exit 0 (Codex item 2: a runner crash can leave DeckBuild running, and a resume would then start the
# next entry beside it).
DIAGB = ('campaign_C10_DIAGb', ['S2-11', 'S0-02-DOS2'])
DIAGB_COMMAND = ('$env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; <project venv python> scripts/run_campaign.py config/campaign_C10_DIAGb.json '
                 '--retry S2-11   (FIRST invocation only, in PowerShell from the package root, immediately after the A41 pre-launch gate has exited 0 '
                 'in the same session; any re-invocation uses the command the gate prints under the STARTED-row rule in stop_rules; '
                 'IWO_ATLAS_VIEWERS unset = viewer policy record)')
DIAGB_AMENDMENT = ('A41 (2026-10-13): this plan may be invoked only after A41 is logged in the register together with the resolution-method sign-off, '
                   'Codex has reviewed it and the user has given the go for this launch')
STATE_ONLY_GLOBAL_RULE = ('run_campaign.py records a failed launch and CONTINUES (this plan declares no gates); it stops automatically only at the launch '
                          'budget / C10 cap. Every stop rule below is applied manually: the main session reads the state-only results/campaigns/<plan>.json '
                          '(full record sealed under results/sealed/campaigns) and decides.')
STATE_ONLY_ENFORCED_BY = ('main session (manual); run_campaign.py enforces the launch budget and C10 cap, refuses runnable=false plans and applies the '
                          'state-only surface (scripts/campaign_sealed.py); this plan declares no gates')
DIAGB_RULES = [
    'Register amendment ' + DIAGB_AMENDMENT + '. Two new launches, sequential, in this order (Codex GO-WITH-CHANGES, work chat 2026-10-13T01:32Z, '
    'item 3): [1] the S2-11 rerun (label c10_s2_11_2p0, entry unchanged; timeout 5400 s; expected run id run_0076), [2] S0-02-DOS2 (label '
    'c10_s0_02_dos2_2p0: the run_0067 override list with numa/numd 384/192 -> 768/384 and nothing else; timeout 3600 s; expected run id run_0077). '
    'The expected ids hold if nothing else launches first (next free id run_0076 when this plan was written); the actual ids are those of the '
    'STARTED rows. This keeps the register section 3 order (S2-11 first): S0-02-DOS2, a numerical refinement of S0-02 outside the 26-launch '
    'diagnostic set, follows the rerun and precedes every S2 mechanism launch. Budget: C10 15/200 -> 17/200, global 75/260 -> 77/260; effective C10 '
    'reserve after this plan 9 (200 - 17 used - 174 unlaunched matrix entries), 3 if all six A41 trigger launches happen.',
    'Invocation, pre-launch gate and --retry rule. First invocation: ' + DIAGB_COMMAND + '. Before EVERY invocation of this plan, the first one and '
    'any re-invocation (after an interruption, a crash, sleep or a declined hook), in the same PowerShell session and working directory as the '
    'invocation and immediately before it, the A41 pre-launch gate (prelaunch_gate_a41.py, run with python -I; sha256 recorded in A41) must exit 0 '
    '(Codex item 2); if it fails, nothing is invoked and the failure is reported. The gate asserts by explicit equality and fails on any mismatch: '
    'working directory = the package root; IWO_MODEL_FILE = config/iwo_material_model_v3.yaml; IWO_ATLAS_VIEWERS and IWO_ATLAS_JOB unset; the sha256 '
    'of this plan file, of every file in scripts/ (public-repo 1375164), of score_register.py and of regress_all_decks.py; the dry-built deck text '
    'and material text sha256 of both entries (next rule); no running deckbuild, dbascii, atlas, atlas2, atlas3, atlasM, atlasMc, tonyplot, '
    'tonyplot3d, athena, athena1d or devedit process and no python process whose command line names run_atlas or run_campaign (a runner crash can '
    'leave DeckBuild running, and a resume would then start the next entry beside it); the RUN_INDEX state below; every started A41 run listed in '
    'config/sealed_runs.json with its STARTED-row input columns as registered; the launch budget and the C10 cap. It prints the one command to use. '
    '--retry rule (unchanged; RUN_INDEX columns run_id and label only): pass --retry S2-11 if and only if no c10_s2_11_2p0 row with a run id above '
    'run_0075 exists; otherwise never pass it (a rerun start row counts as the one A41 rerun, finished or not; there is no third S2-11 launch), and '
    'never repeat the stored command verbatim once the rerun has a RUN_INDEX row. --retry S2-11 deliberately bypasses the C10 label-reuse rule for '
    'S2-11 only: run_0075 holds that label and its execution.json status is a runner success although it timed out, so without --retry run_campaign '
    'would reuse run_0075 for S2-11 and go on to S0-02-DOS2. S0-02-DOS2 is never relaunched (label rule). A DIAGb record of S2-11 as run_0075 '
    '"reused" is never the registered S2-11 result: it is reported and the --retry rule above is applied. The gate also stops for a main-session '
    'decision on a c10_s0_02_dos2_2p0 row without a rerun row (order not followed), on more than one rerun or S0-02-DOS2 run id, and on any other '
    'launch after run_0075 (expected ids shifted); once both A41 runs have started it reports that nothing remains to launch and exits non-zero.',
    'Before the first invocation (main session, in the same PowerShell session and working directory as the launch, the package root): A41 logged '
    'together with the resolution-method sign-off (register and decision log) after Codex review; the user\'s go for THIS launch; the deck regression '
    'gate in its sealed-aware form, analysis_2026-10-10_campaign/regress_sealed_aware.py (the committed regress_all_decks.py, unchanged, over every run '
    'except the ids of the explicit sealed-run inventory config/sealed_runs.json, whose RUN_INDEX rows and run directories are not read, plus each '
    'sealed run\'s RUN_INDEX deck_sha256 and model_sha256 equal to the inventory and to the current rebuild of its matrix entry; A41 (e)) ending '
    '"unexpected differences 0"; make_campaign_configs.py --check YES; score_register.py sha256 '
    'c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a with selftest 90/90; scripts/run_campaign.py, run_atlas.py, campaign_gates.py, '
    'campaign_sealed.py, proc_guard.py as committed in public-repo 1375164; and the pre-launch gate of the previous rule, which checks, with '
    'IWO_MODEL_FILE set as in the command, that run_campaign.current_deck_text gives deck text sha256 '
    '3034b7e276d40f8f8e3587219cbafe82c97c9db43ce23706938e18b4285ee956 (S2-11) and 09bb893d3254c9f0de24238e5b6f5eca3fa99c549c8d3f9456709eec95ff8e85 '
    '(S0-02-DOS2) and current_material_text sha256 974b23ea65ceaa38185221c1a62bb6f1b4eef54fd4884bb7eaadc38a83f18204 (= RUN_INDEX model_sha256 of '
    'run_0067) for both entries; results/campaigns/campaign_C10_DIAGb.json and results/sealed/campaigns/campaign_C10_DIAGb.full.json / .console.log '
    'absent.',
    'State-only (Codex D7): the console and results/campaigns/campaign_C10_DIAGb.json carry state only; the full record and the launch output are sealed '
    'under results/sealed/campaigns. No current, metric or note of either run is opened, printed or scored before both launches have ended and the '
    'scoring order below starts. The only reads allowed before then are the input columns of each run\'s STARTED row in RUN_INDEX (run_id, label, '
    'deck_sha256, model_sha256 and the STARTED note, written at launch before any output): deck_sha256 must equal the deck hash above for its entry, '
    'model_sha256 974b23ea65ceaa38185221c1a62bb6f1b4eef54fd4884bb7eaadc38a83f18204, and the note must contain model=config/iwo_material_model_v3.yaml. '
    'Sealed-run inventory (Codex item 5): each run of this plan is appended to config/sealed_runs.json (run id, label, entry, the registered deck and '
    'model sha256 above, reason) as soon as its RUN_INDEX STARTED row exists, during or right after the invocation, and before any later regression '
    'check or re-invocation; regress_sealed_aware.py refuses to run while a RUN_INDEX run with a state-only plan label is missing from the inventory, '
    'and the pre-launch gate refuses a re-invocation while a started A41 run is missing. Removing an entry needs a logged decision. Viewer windows '
    'are not looked at; a viewer recorded by the process guard is disclosed.',
    'Failures: run_campaign records a failed launch and continues (no gates). A failed, timed-out or invalid launch is reported and kept, never deleted, '
    'and not relaunched under A41. Validity is read from the RUN_INDEX exit_code of the run\'s finish row or from the frozen scorer\'s run_problems, '
    'never from the state file (its projection carries no timed_out or return code: a timed-out run with complete exports shows as completed with status '
    'REAL_ATLAS_SCORED, as run_0075 did). The viewer risk (policy record) applies to BOTH launches: a viewer holding DeckBuild makes the rerun time out '
    'at 5400 s (invalid; S2-11 UNRESOLVED, QTNLSC convergence not demonstrated) or S0-02-DOS2 time out at 3600 s (invalid; no I_G pair; S2-11 at best '
    'PROVISIONAL). With S2-11 first, the first real launch of runner 1375164 is the rerun itself: a runner defect that ends the invocation costs the one '
    'rerun (S2-11 UNRESOLVED). Any further launch needs a new logged amendment and the user\'s go.',
    'Scoring after both launches (frozen score_register.py c0f28bb9), in this order: (1) runner state and run validity only; (2) resolution_pair '
    '<S0-02-DOS2 run> <run_0067> ig_raw_A -> PAIR.json; if the call raises (e.g. the frozen scorer\'s ZeroDivisionError when the only disagreeing points '
    'are exact zeros in both runs) or writes no JSON, there is no pair; (3) the registered S2-11 score: hc_mesh <S2-11 rerun> <run_0067> --resolution-ig '
    '<candidate_resolution_A_per_um of PAIR.json, verbatim; no larger value may be cited> --resolution-ig-source PAIR.json if the pair qualified, '
    'otherwise hc_mesh <S2-11 rerun> <run_0067> without --resolution-ig (PROVISIONAL). The sha256 of PAIR.json and of the score JSON go into the action '
    'note, with the candidate compared against the deck\'s ir.tol 1e-19 and cr.toler 1e-17 / 5e-18. A qualifying pair is a reproducibility floor under '
    'the DOS quadrature intervention (numa/numd are the energy-level intervals of the continuous-defect integral): it is neither Newton-controlled '
    'accuracy nor an absolute bound on the tunnelling discretization error. The registered S2-11 run is the rerun (pinned by A41; run_0075 is never '
    'substituted); its verdict carries the A41 disclosure label "S1-informed operational method; S2 blinding cannot be demonstrated; possibly exposed; '
    'not viewed according to the user\'s statement" (Codex item 6). The shared run_0067 baseline is recorded (resolution_pair_relation, independent '
    'false).',
    'After this plan: campaign_C10_DIAGa_S2-11 is held (runnable=false, superseded by this plan); campaign_C10_DIAG stays held for its own conditions and, '
    'when launched, reuses S2-11 by label (the highest c10_s2_11_2p0 run id, the rerun). Matched oxide-mesh refinements follow only the frozen A41 trigger '
    '(A41 (d): hc_explains of a QTNLSC mechanism run, read once from its JSON), each in its own plan after the trigger result and the scorer REG/PIN '
    'extension are logged.']


_DUP = None


def duplicates(mx):
    """id -> earlier matrix id whose deck has identical solver statements (V3 + overrides); such an entry need not be launched"""
    global _DUP
    if _DUP is None:
        import hashlib
        first = {}; _DUP = {}
        for r in mx['runs']:
            if r['status'] != 'planned_fixed': continue
            e = r['campaign_entry']; h = (e.get('mode'), hashlib.sha256('\n'.join(ct.statements(ct.entry_deck(e, ct.V3)[0])).encode()).hexdigest())
            if h in first: _DUP[r['id']] = first[h]
            else: first[h] = r['id']
    return _DUP


def plan_entries(mx, sel):
    runs = mx['runs']; ids = {r['id'] for r in runs}
    pick = [next(r for r in runs if r['id'] == i) for i in sel] if all(x in ids for x in sel) else [r for r in runs if r['stage'] in sel]
    out = []
    for r in pick:
        e = dict(r['campaign_entry'])
        e.update({'stage': r['stage'], 'matrix_status': r['status'], 'requires_code': r.get('requires_code', []), 'depends_on': r.get('depends_on'),
                  'pre_registered_expectation': r.get('pre_registered_expectation', ''), 'params_rule': r.get('params_rule', ''),
                  'min_set_rank': (MIN10.index(r['id']) + 1) if r['id'] in MIN10 else None})
        if r['id'] in duplicates(mx):
            e['solver_identical_to'] = duplicates(mx)[r['id']]   # same solver statements: reuse that run instead of launching (main-session decision)
        out.append(e)
    return out


def plan(mx, stem, sel, rules, runnable):
    entries = plan_entries(mx, sel); hold = HOLD.get(stem) if runnable else None; runnable = runnable and hold is None
    p = {'campaign': stem.replace('.template', ''), 'runnable': runnable,
         'purpose': ('2026-10-10 DFT-informed campaign, ' + ', '.join(sel) + '. Generated by analysis_2026-10-10_campaign/make_campaign_configs.py from '
                     'campaign_matrix.json (entries verbatim, matrix order). Design: analysis_2026-10-10_campaign/CAMPAIGN_DESIGN.md.'
                     + ('' if runnable else ' NOT RUNNABLE (HOLD): see not_runnable_reason.' if hold else
                        ' TEMPLATE: overrides contain unresolved {generated}/{frozen model} tokens; resolve them after the named stage, then save without .template and set runnable to true.')),
         'model_file_env': 'IWO_MODEL_FILE=config/iwo_material_model_v3.yaml', 'global_rules': GLOBAL_RULES, 'stop_rules': ([f'HOLD: {hold}'] if hold else []) + rules,
         'stop_rules_enforced_by': 'main session (manual); run_campaign.py enforces the launch budget and refuses runnable=false plans', 'runs': entries}
    if hold: p['not_runnable_reason'] = hold
    if stem in GATES:   # 2026-10-13: gates (and the state-only surface) before 'runs'; only this plan's file changes
        gr = [GATED_GLOBAL_RULE if r.startswith('run_campaign.py records a failed launch and CONTINUES') else r for r in p['global_rules']]
        p = {**{k: v for k, v in p.items() if k != 'runs'}, 'global_rules': gr, 'stop_rules_enforced_by': GATES_ENFORCED_BY, 'gates': GATES[stem],
             **({'state_only': STATE_ONLY[stem]} if stem in STATE_ONLY else {}), 'runs': p['runs']}
    elif stem in STATE_ONLY:   # 2026-10-13 A41: state-only surface WITHOUT gates (campaign_C10_DIAGb); the DIAG branch above is unchanged
        gr = [STATE_ONLY_GLOBAL_RULE if r.startswith('run_campaign.py records a failed launch and CONTINUES') else r for r in p['global_rules']]
        p = {**{k: v for k, v in p.items() if k != 'runs'}, 'purpose': p['purpose'].replace('(entries verbatim, matrix order)', '(entries verbatim, A41 launch order)'),
             'global_rules': gr, 'stop_rules_enforced_by': STATE_ONLY_ENFORCED_BY, 'register_amendment': DIAGB_AMENDMENT,
             'launch_command': DIAGB_COMMAND, 'state_only': STATE_ONLY[stem], 'runs': p['runs']}
    return p


def verify(mx):
    """every matrix entry appears exactly once in the stage plans/templates, verbatim and in matrix order; MIN10 = the design's 10"""
    seen = []; bad = 0
    for stem, sel, _ in PLANS + TEMPLATES:
        p = json.loads((CFG / f'{stem}.json').read_text()); seen += [e['id'] for e in p['runs']]
        for e in p['runs']:
            ref = next(r for r in mx['runs'] if r['id'] == e['id'])['campaign_entry']
            if any(e.get(k) != ref.get(k) for k in KEEP): bad += 1; print('MISMATCH', stem, e['id'])
            if p['runnable'] and any('{' in o or '=' not in o for o in e['overrides']): bad += 1; print('UNRESOLVED TOKEN in runnable plan', stem, e['id'])
            if e.get('mode') not in (None, 'strip'): bad += 1; print('unknown mode', e['id'])
    order = [r['id'] for r in mx['runs']]
    if seen != order: bad += 1; print('ORDER/COVERAGE differs from the matrix:', len(seen), 'vs', len(order))
    m10 = [e['id'] for e in json.loads((CFG / 'campaign_C10_MIN10.json').read_text())['runs']]
    if m10 != MIN10: bad += 1; print('MIN10 differs')
    for stem, ids in DIAG_PLANS:   # 2026-10-11 register diagnostic plans
        if not (CFG / f'{stem}.json').is_file(): continue
        dg = json.loads((CFG / f'{stem}.json').read_text())['runs']
        if [e['id'] for e in dg] != ids: bad += 1; print(stem, 'ids differ')
        for e in dg:
            ref = next(r for r in mx['runs'] if r['id'] == e['id'])['campaign_entry']
            if any(e.get(k) != ref.get(k) for k in KEEP): bad += 1; print('MISMATCH', stem, e['id'])
    stem, ids = DIAGB   # 2026-10-13 A41: the S2-11 rerun / S0-02-DOS2 plan (ids in launch order, entries verbatim, runnable, state-only, no gates)
    if not (CFG / f'{stem}.json').is_file(): bad += 1; print(stem, 'missing')
    else:
        pb = json.loads((CFG / f'{stem}.json').read_text())
        if [e['id'] for e in pb['runs']] != ids: bad += 1; print(stem, 'ids differ')
        for e in pb['runs']:
            ref = next(r for r in mx['runs'] if r['id'] == e['id'])['campaign_entry']
            if any(e.get(k) != ref.get(k) for k in KEEP): bad += 1; print('MISMATCH', stem, e['id'])
        if (pb.get('runnable') is not True or 'gates' in pb or pb.get('launch_command') != DIAGB_COMMAND or pb.get('stop_rules') != DIAGB_RULES
                or pb.get('register_amendment') != DIAGB_AMENDMENT):
            bad += 1; print(stem, 'runnable / gates / launch_command / stop_rules / register_amendment differ from make_campaign_configs (DIAGB)')
    held = []   # 2026-10-11 review: runnable flag = not HOLD for every non-template plan
    for stem in [s for s, _, _ in PLANS] + ['campaign_C10_MIN10'] + [s for s, _ in DIAG_PLANS] + [DIAGB[0]]:
        if not (CFG / f'{stem}.json').is_file(): continue
        p = json.loads((CFG / f'{stem}.json').read_text())
        if p['runnable'] != (stem not in HOLD) or (stem in HOLD and p.get('not_runnable_reason') != HOLD[stem]): bad += 1; print('RUNNABLE FLAG wrong', stem)
        if not p['runnable']: held.append(stem)
        if p.get('gates') != GATES.get(stem): bad += 1; print('GATES differ from make_campaign_configs.GATES', stem)   # 2026-10-13
        if p.get('state_only') != STATE_ONLY.get(stem): bad += 1; print('STATE_ONLY differs from make_campaign_configs.STATE_ONLY', stem)
        if 'gates' in p:
            import campaign_gates as cg   # scripts/ is on sys.path (campaign_tools)
            ge = cg.validate(p)
            if ge: bad += 1; print('GATES INVALID', stem, ge)
        if 'state_only' in p:
            import campaign_sealed as cs
            se = cs.validate(p)
            if se: bad += 1; print('STATE_ONLY INVALID', stem, se)
    runnable = sum(len(json.loads((CFG / f'{s}.json').read_text())['runs']) for s, _, _ in PLANS if s not in HOLD)
    print(f'plans verified: {len(seen)} matrix entries in {len(PLANS)} stage plans ({len(PLANS) - sum(s in HOLD for s, _, _ in PLANS)} runnable, {runnable} entries) + '
          f'{len(TEMPLATES)} templates; verbatim and in matrix order: {"YES" if not bad else "NO"}; MIN10 plan: {m10}; held (runnable=false): {held}; '
          f'register route: ' + ', '.join(f'{s} ({len(i)}{", HELD" if s in HOLD else ""})' for s, i in DIAG_PLANS)
          + f'; A41 plan: {DIAGB[0]} ({" then ".join(DIAGB[1])}, state-only, A41 pre-launch gate before every invocation, --retry S2-11 by the STARTED-row rule)')
    return bad


def remaining(plan_path, args):
    """args: summary files of results/campaigns, optionally followed by --skip ID ... (e.g. the solver-identical S3-04 S3-07)"""
    summaries = args[:args.index('--skip')] if '--skip' in args else args; skip = set(args[args.index('--skip') + 1:]) if '--skip' in args else set()
    done = set(skip)
    for sp in summaries:
        done |= {r['id'] for r in json.loads(Path(sp).read_text())['runs'] if r.get('run_dir')}
    p = json.loads(Path(plan_path).read_text()); p['runs'] = [e for e in p['runs'] if e['id'] not in done]
    p['campaign'] += '_remaining'; out = Path(plan_path).with_name(Path(plan_path).stem + '_remaining.json')
    out.write_text(json.dumps(p, indent=1)); print(out, len(p['runs']), 'entries; skipped', sorted(done))


def main(argv):
    mx = ct.matrix()
    if argv[:1] == ['--remaining']: remaining(argv[1], argv[2:]); return 0
    if argv[:1] != ['--check']:
        for stem, sel, rules in PLANS: (CFG / f'{stem}.json').write_text(json.dumps(plan(mx, stem, sel, rules, True), indent=1))
        for stem, sel, rules in TEMPLATES: (CFG / f'{stem}.json').write_text(json.dumps(plan(mx, stem, sel, rules, False), indent=1))
        m10 = plan(mx, 'campaign_C10_MIN10', MIN10, ['CAMPAIGN_DESIGN 9: the 10-run minimum set in launch order. Its ids also appear in the stage plans: '
                                                       'run_campaign.py reuses their launches there automatically (same label in RUN_INDEX -> no new launch); '
                                                       '--remaining stage plans are optional (shorter files).',
                                                       'S0 rules apply to its first two entries. Recommended: launch campaign_C10_S0a_smoke and S0b_smoke first, then this plan '
                                                       'via --remaining (it then holds the 8 non-smoke runs), because run_campaign continues after a failed launch.'], True)
        (CFG / 'campaign_C10_MIN10.json').write_text(json.dumps(m10, indent=1))
        rules = ['Frozen register (register-rev2-frozen-20261010T1833Z) section 3: 24 of the 26 diagnostic launches, in the register order (S2-11 first), in three '
                 'plans: campaign_C10_DIAGa_S2-11 (S2-11), campaign_C10_DIAG (S2, S3 confinement, AFF: 19 entries, reusing S2-11) and campaign_C10_DIAG_HF (H-F: 5 '
                 'entries, held until the H-F scoring is frozen). S6-13 / S6-15 follow S4c (template entries). An entry already launched under the same label '
                 '(any C10 plan) is reused, never re-launched.',
                 'S2-11 first: launch campaign_C10_DIAGa_S2-11 alone (run_campaign continues after a failure), score it (score_register.py hc_mesh '
                 '<S2-11 run> <run_0067>), then launch campaign_C10_DIAG, which reuses the S2-11 launch by its label.',
                 'S2-11 halves the oxide y.mesh spacing at the 0.002 / 0.017 um lines and keeps the y = 0 line: Al2O3 refined about x1.5, HfO2 about x2. '
                 'Its verdict covers QTNLSC only; S2-12/S2-13 (ITAT) use TAT.SLICEPTS = 12 (default, untested) and cannot count as converged under H-C '
                 'without a logged amendment (e.g. a TAT.SLICEPTS sensitivity launch).',
                 'Scoring is frozen in analysis_2026-10-10_campaign/score_register.py (H-B hb_ratio/hb_transfer, H-C hc_nominal/hc_generation/hc_mesh/hc_worst/'
                 'hc_explains, H-E aff/he_alloff/s3_minus_s105); below-resolution quantities are censored (register section 0), never a pass. H-F: no frozen scorer '
                 'yet (campaign_C10_DIAG_HF is held).',
                 'S2 stop rules of campaign_C10_S2_offfloor apply; IGZO runs need post_run_checks.py activation; no S3 branch is adopted from this plan.']
        for stem, ids in DIAG_PLANS:
            (CFG / f'{stem}.json').write_text(json.dumps(plan(mx, stem, ids, rules, True), indent=1))
        (CFG / f'{DIAGB[0]}.json').write_text(json.dumps(plan(mx, DIAGB[0], DIAGB[1], DIAGB_RULES, True), indent=1))   # 2026-10-13 A41
    return 1 if verify(mx) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
