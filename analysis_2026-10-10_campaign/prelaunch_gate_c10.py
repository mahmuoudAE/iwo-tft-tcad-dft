"""C10 pre-launch gate for S1-06R (config/campaign_C10_S1r_repair.json, PA-1 = register A45 / decision D-60) and the register diagnostic plan
config/campaign_C10_DIAG.json (Codex 2026-10-14T18:00Z, item 1: "Replace the exhausted DIAGb-only gate with a reviewed gate covering the repair
and campaign_C10_DIAG.json: plan/deck/model hashes, STARTED-row inputs, resume state, sealing, budget and process checks. Exit 4 is not a pass.").
Corrected 2026-10-15 for Codex 2026-10-14T19:02Z (b) FIX_FIRST and (d): the frozen run_problems on both S1 comparison endpoints before a PASS is
accepted; STARTED-run order == a prefix of S1-06R -> DIAG; max_launches == 260 and the C10 cap 200; the comparison command with the actual run
directories; check 8 on the complete V_G set, finite values and uniqueness (S1-06R computed and recorded; PA-2 runs by record).
Modelled on prelaunch_gate_a41.py, which stays unchanged (it covers DIAGb only and exits 4 there); its process functions are imported from
the file after its sha256 is checked. NO launch, NO file written, nothing sealed opened. Run it immediately before EVERY invocation of either
plan (the first one and any resume), in the same PowerShell session and working directory (the package root) as the invocation:

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"
    & "<venv>\\Scripts\\python.exe" -I -B "<this file>" [--check] [--ack-audit AUDIT_FILE]

--check labels the output as a check (the printed command is then not an instruction); the checks and exit codes are the same.
--ack-audit: the completed audit of a DIAG gate stop; it must name the gate id and its decision id (as campaign_gates.audit_citation).

Exit codes (ONLY 0 is a pass):
  0  the next run is launchable: every check holds by explicit equality; prints the ONE command to use
  1  a check failed or an input is unreadable (fail closed; any unexpected error is 1)
  3  STOP for a main-session decision: a runner-valid S1-06R or its reference run_0069 fails the frozen run_problems, a runner-valid S1-06R
     or PA-2 run has no passing check 8, the S1 rule fired or has no evaluation record yet,
     a recorded DIAG gate stop is not acknowledged with a cited audit, or a started run has no finish row
  4  nothing to launch (S1-06R and every DIAG entry have started); not a pass

Checks
  interpreter  isolated mode (-I) and the project venv (sys.prefix)
  cwd/env      working directory = package root; IWO_MODEL_FILE = config/iwo_material_model_v3.yaml; IWO_ATLAS_VIEWERS and IWO_ATLAS_JOB unset
  files        sha256 of both plan files; exact file set and sha256 of scripts/ (public-repo 1375164 except build_iwo_decks.py, which carries the
               PA-1/PA-4 builder change and is pinned to 734125a8: Codex 2026-10-14T19:02Z (a) accepted the builder defaults and the
               repair/QT statement diffs; committed with this gate); score_register.py (frozen c0f28bb9; its run_problems and read_cols are
               used below), post_run_checks.py (imported by it), regress_all_decks.py, regress_sealed_aware.py, campaign_extract.py and
               campaign_tools.py (S1-rule evaluator), the A41 gate (process functions), the V3 model file
  plans        S1R: runnable, no gates, not state-only, ids [S1-06R]; DIAG: runnable, state_only results/sealed/campaigns, the four gates with
               the frozen scorer sha256, ids in register order (S2-11 first) with the registered labels
  dry build    run_campaign.current_deck_text / current_material_text (the runner's own code, imported after the file check) for S1-06R and
               all 19 DIAG entries == the pinned deck and material text sha256
  amendments   register (HYPOTHESIS_REGISTER.md) heading '### A<n>: ...' naming S1-06R and a decision-log row naming S1-06R and IN FORCE
               (PA-1), before S1-06R; a heading naming S2-01, S2-02, S2-03 and 'continuation' and an IN FORCE decision row naming S2-01 and
               'continuation' (PA-2), before any DIAG invocation (the DIAG plan carries the PA-2 decks). A heading containing 'draft' never counts.
  processes    as the A41 gate: no deckbuild/dbascii/atlas*/tonyplot*/athena*/devedit process and no python process whose command line names
               run_atlas or run_campaign; every other python process must have a readable command line (UNVERIFIABLE otherwise)
  RUN_INDEX    columns run_id and label of every row (counting); input columns of the first (STARTED) row and the presence of a finish row
               (exit_code) only for runs above run_0077 that carry an S1-06R/DIAG label. No row of run_0075..0077 is read beyond run_id/label.
               Fails on: a run above run_0077 with any other label, two run ids for one label, STARTED runs above run_0077 (run-id order)
               that are not a prefix of S1-06R -> S2-04 -> S2-06 -> ... (LAUNCH_ORDER: DIAG order without S2-11), a third S2-11 launch, a STARTED row whose deck_sha256 / model_sha256 / model note differ from the pins, a started DIAG run missing from
               config/sealed_runs.json (state-only plan) or listed with other values; S2-11 is reused from run_0076 only (inventory entry with
               the A41 deck/model sha256)
  check 8      (manual_checks.md check 8, Codex 18:00Z item 7 and 19:02Z (d): "Audit the complete expected voltage set, finite values and
               uniqueness - not merely row count. Unexpected continuation/cut-back rows make the run UNVERIFIED under this registration; do
               not retrospectively delete them to obtain PASS. Apply that audit to all PA-2 runs too." NO.TRAP stays unset: the dry-built
               S1-06R and PA-2 decks are checked for it.)
               S1-06R (not sealed; runner-valid and both endpoints clean under run_problems, see S1 rule): (i) COMPUTED by the gate from its
               terminal_currents.csv (frozen read_cols; counts and booleans only, no current value printed): the exported V_G set (6 decimals)
               == the registered 76-point grid REG_GRID (-3..-1 by 0.2, -0.95..1.5 by 0.05, 1.6..3 by 0.1), 76 rows, no duplicate V_G, every
               value of every column finite, -1.6 V once, none of -1.75/-1.70/-1.65, no other off-grid row; (ii) the hand-written audit
               analysis_2026-10-10_campaign/audits/S1-06R_check8_<S1-06R run>.json, a JSON object whose keys below hold exactly these values
               (other keys, e.g. auditor and UTC, are allowed): "entry" "S1-06R", "run" <that run id>, "deck_sha256" the pinned S1-06R deck,
               "exported_rows" 76 (terminal_currents.csv data rows), "vg_m1p6_count" 1 (rows at V_G = -1.6 V), "continuation_rows_exported" 0
               (rows at -1.75/-1.70/-1.65 V), "off_grid_trap_rows" 0 (rows at any other V_G off the registered grid, e.g. trap cut-back
               steps), "vg_set_complete" true (every registered V_G present), "vg_unique" true, "values_finite" true, "log_reopen_ok" true
               (deckbuild.out echoes 'log off' and 'log outf=transfer.log append' where frozen; transfer.log parses as one DC log), "result"
               "PASS", and a non-empty "evidence" (file:line for each value). Integers must be JSON integers, booleans JSON true.
               PA-2 runs S2-03, S2-01, S2-02 (DIAG, sealed: the gate never opens their directories): each with a finish row exit_code 0
               needs the record audits/<entry>_check8_<run>.json with the same keys (entry, run and pinned deck of that entry) before any
               later DIAG invocation. Within one DIAG invocation the runner continues past them; the record is therefore checked at the next
               invocation. Missing, unreadable, a failed computed check or any other value -> STOP (exit 3; the run is invalid for scoring,
               UNVERIFIED, no row deleted, no relaunch; a main-session decision is needed). The S1-rule record is read only after check 8.
  S1 rule      after S1-06R (not sealed): RUN_INDEX finish row exit_code and its execution.json status. For a runner-valid S1-06R (exit_code 0,
               REAL_ATLAS_SCORED) the frozen run_problems (score_register.py c0f28bb9: runner status, return code, timeout, simulator
               errors, ATLAS completion banner, every requested point exported, finite values, no duplicate bias point) is applied to BOTH
               comparison endpoints first: S1-06R and the S1-02 reference run_0069 (S1_02_DIR, unsealed; its execution.json run_id and label
               are checked). A problem in either -> STOP (exit 3): the comparison is invalid, electron-only stays ASSUMED, never TESTED. Then
               check 8, then the record analysis_2026-10-10_campaign/extract/compare_<S1-06R run>_vs_run_0069.json, made by the printed
               command "campaign_extract.py compare <S1-06R dir> <run_0069 dir> --rule s1_06" (actual run directories: campaign_extract.resolve
               does not resolve a bare run id): PASS -> electron-only TESTED at 13.2 nm, DIAG may start; FAIL -> STOP (re-plan, exit 3);
               missing/UNVERIFIED -> STOP (exit 3). A runner-invalid S1-06R (non-zero exit or another runner status) is not interpreted:
               electron-only stays ASSUMED and DIAG may start without a check-8 audit (Codex 18:00Z item 2).
  resume       S1R: S1-06R is launched once (no --retry, no relaunch). DIAG: the state projection results/campaigns/campaign_C10_DIAG.json
               (state only) is read for unacknowledged gate stops; the sealed results/sealed/campaigns/campaign_C10_DIAG.* files are tested for
               existence only
  budget       config/solver.yaml carries exactly one max_launches and it equals 260; the C10 cap equals 200 (gate constant and
               run_campaign.C10_CAP); D-58 (4): neither is raised. Distinct run ids + 1 <= 260; c10 run ids + 1 <= 200
"""
import csv
import hashlib
import importlib.util
import json
import math
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # importing scripts/ must not write __pycache__

PKG = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1")
PRIVATE = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\iwo-tft-research-private")
VENV_PY = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_ATLAS_Model_claude\.venv\Scripts\python.exe")
INDEX = PKG / 'results' / 'RUN_INDEX.csv'
INVENTORY = PKG / 'config' / 'sealed_runs.json'
REGISTER = PRIVATE / 'codex' / 'work_chat' / 'HYPOTHESIS_REGISTER.md'
DECISIONS = PRIVATE / '05_DECISION_LOG.md'
A41_GATE = PKG / 'analysis_2026-10-10_campaign' / 'prelaunch_gate_a41.py'
EXTRACT = PKG / 'analysis_2026-10-10_campaign' / 'extract'
AUDITS = PKG / 'analysis_2026-10-10_campaign' / 'audits'   # <entry>_check8_<run>.json (manual check 8), hand-written; the gate only reads it
CHECK8_INT = {'exported_rows': 76, 'vg_m1p6_count': 1, 'continuation_rows_exported': 0, 'off_grid_trap_rows': 0}
CHECK8_TRUE = ('vg_set_complete', 'vg_unique', 'values_finite', 'log_reopen_ok')
REG_GRID = tuple(sorted({round(-3 + 0.2 * k, 6) + 0.0 for k in range(11)} | {round(-0.95 + 0.05 * k, 6) + 0.0 for k in range(50)}
                        | {round(1.6 + 0.1 * k, 6) + 0.0 for k in range(15)}))   # the registered 76-point logged grid (S1-06R_freeze.md section 4)
CONT_VG = (-1.75, -1.7, -1.65)   # continuation points, solved with the log closed (PA-1 (a)); never exported
PA2 = ('S2-03', 'S2-01', 'S2-02')   # DIAG entries carrying the PA-1 continuation (PA-2); sealed (state-only plan)
SOLVER = PKG / 'config' / 'solver.yaml'
MAX_LAUNCHES = 260   # config/solver.yaml max_launches; D-58 (4): not raised
S1_02_DIR = 'results/runs/run_0069_13p2_c10_s1_02_13p2'   # S1-02 (run_0069, unsealed) output directory: the S1-rule reference endpoint
DIAG_STATE = PKG / 'results' / 'campaigns' / 'campaign_C10_DIAG.json'   # state projection (value-free)
SEALED_DIR = PKG / 'results' / 'sealed' / 'campaigns'                  # existence only
S1R_REL, DIAG_REL = 'config/campaign_C10_S1r_repair.json', 'config/campaign_C10_DIAG.json'
PLAN_SHA = {S1R_REL: '6b73ffdd32576d86626cb4694a4bbf4630b5584a483b77b186de29eaff43e852',
            DIAG_REL: 'd1131d8e8da386938f4c816f9827cd92bffa21fea7933c43dca9dcd1258db647'}
DIAG_ORDER = ['S2-11', 'S2-04', 'S2-06', 'S2-03', 'S2-01', 'S2-02', 'S2-08', 'S2-12', 'S2-13', 'S2-14', 'S2-15', 'S2-16', 'S2-17', 'STRIP-6p3',
              'S3-01', 'S3-02', 'S3-03', 'AFF-2p0', 'AFF-6p3']
LAUNCH_ORDER = ['S1-06R'] + DIAG_ORDER[1:]   # STARTED runs above run_0077 must be a prefix (S2-11 is reused from run_0076, never launched again)
DIAG_GATES = ['G-S2-04-nominal', 'G-S2-06-nominal', 'G-S2-03-anomaly', 'G-S2-01-generation']
LABEL = {'S1-06R': 'c10_s1_06r_13p2', 'S2-11': 'c10_s2_11_2p0', 'S2-04': 'c10_s2_04_2p0', 'S2-06': 'c10_s2_06_13p2', 'S2-03': 'c10_s2_03_2p0',
         'S2-01': 'c10_s2_01_13p2', 'S2-02': 'c10_s2_02_13p2', 'S2-08': 'c10_s2_08_13p2', 'S2-12': 'c10_s2_12_2p0', 'S2-13': 'c10_s2_13_13p2',
         'S2-14': 'c10_s2_14_13p2', 'S2-15': 'c10_s2_15_2p0', 'S2-16': 'c10_s2_16_13p2', 'S2-17': 'c10_s2_17_2p0', 'STRIP-6p3': 'c10_strip_6p3_6p3',
         'S3-01': 'c10_s3_01_2p0', 'S3-02': 'c10_s3_02_6p3', 'S3-03': 'c10_s3_03_13p2', 'AFF-2p0': 'c10_aff_2p0_2p0', 'AFF-6p3': 'c10_aff_6p3_6p3'}
DECK = {'S1-06R': '33ebe8d823c6902033083f968cc1e7885e33ff819e09d5c415714a39bfcc15df',
        'S2-11': '3034b7e276d40f8f8e3587219cbafe82c97c9db43ce23706938e18b4285ee956',   # = A41 rerun deck (run_0076)
        'S2-04': '17c3173678cbb88acdbf555fea2c1e3f240a45420943c7a84b0306ff3d6126a8', 'S2-06': '6a45e1c65832d401c5c84f151a84c72806d2b25e9f3c0febd325f6facec2f8d4',
        'S2-03': 'bf291a5f0e3f30986dd837b07eafdf317f29b78bd0a4bc81272af58fa1af882e', 'S2-01': 'cb16ce3f2142d4c49fab5c08e7f42363ae159d118d4df0e25e93197bc1d7bc8b',
        'S2-02': '5737f50ebf4ca900933a5d4376f68d540b742c11ec961907d3e91474ba767122', 'S2-08': '9a2a478161c379eeca3752b2b749187d95bbbbf86611e757b89a3cfaf9cf2954',
        'S2-12': '72233118f83efc5e850b498b1ec8835bb5c22cb69eb40fb35adb73b869ea84ab', 'S2-13': '48dae160e6d5e0473deeeda924316b4d82775717611fef8655289dd93244f5c1',
        'S2-14': '6c8c8a3f4ca2727d7ad27427bac82652de2fb50596ceda73a20dc6e29312dbf3', 'S2-15': 'f25722024bf4fb2519b13c3f65daa7e1eb7028cad2775e98434a4b8110a27a10',
        'S2-16': '771b525b3342f4b72a5171ea326381158d9baf7996995a855507595d71a29ae0', 'S2-17': 'ad35e08c5c88522c01a9a33fa49ce5ecac3090a8a955732266470f2cab82bfdd',
        'STRIP-6p3': 'ce272ecbe65db7154e69709106296d6c6f690e35d0cf5822be694426cbfeab33', 'S3-01': '49953d3dcfc90f58cc9d276badd0f70ff8ec36731c332a8ecfd7ed092320a9e3',
        'S3-02': 'a5570246bb60f40d2c08b63fe04714ba6996b5a59337a781f159ab991b77ed0e', 'S3-03': '6b292e0e4cdf8e05d13b7c8bc9fa98702a5a210de7cf7962e43554f330bbbeb2',
        'AFF-2p0': '5c6aa35b13127cfe819ef97f62557579ab53c4363896965a832a3f105ce5e568', 'AFF-6p3': '33bd6470ea51e2e86eb524b061c145dc20cf62f03ea1f34a0960cbbe2b55fc50'}
_M0, _M1, _M2 = ('974b23ea65ceaa38185221c1a62bb6f1b4eef54fd4884bb7eaadc38a83f18204', 'b4e5432effe75821a299f4ddfe34f2ef89fd36e7d884ab2faf00e9b46963339a',
                 '5ebe5df5893fe4348feee6d45054e6f08d7345b9d1ca0f97c50519b6677d9044')
MATERIAL = {'S1-06R': _M0, 'S2-11': _M0, 'S2-04': _M0, 'S2-06': _M0, 'S2-03': _M1, 'S2-01': _M1,
            'S2-02': 'd3b2b354f8fe4b21a005b15d93bd469733287172ae56c6acb822f256e555f858', 'S2-08': _M0, 'S2-12': _M0, 'S2-13': _M0, 'S2-14': _M0,
            'S2-15': _M0, 'S2-16': _M2, 'S2-17': _M2, 'STRIP-6p3': _M0, 'S3-01': 'f8e0eda460ef62033ab19d338b2d5cc91e58b9ca0928f99ec093183a180f01bf',
            'S3-02': '15d34ce0e70de5a663b33b68c594cae022d99b64870976a34207126b410be3a2', 'S3-03': 'ae73704d9d2723fbe9bf2e40fdfcb6b6a70fa53fdd1001348f0dd249cebb9a11',
            'AFF-2p0': '6a3c2b7fafc381d24ca202f309f4f4e950c9a4fc869fb2a5376b4d878c3d3b7f', 'AFF-6p3': '6a3c2b7fafc381d24ca202f309f4f4e950c9a4fc869fb2a5376b4d878c3d3b7f'}
MODEL_ENV = 'config/iwo_material_model_v3.yaml'
LAST_PRE = 'run_0077'          # last run before this gate's scope (run_0075..0077 sealed: run_id/label only)
S2_11_RUNS = ['run_0075', 'run_0076']   # run_0075 timed out (never substituted); run_0076 = A41 rerun, reused by DIAG by its label
S1_02_RUN = 'run_0069'         # S1-02 (c10_s1_02_13p2), the S1-rule reference
SUCCESS = ('REAL_ATLAS_SCORED',)
C10_CAP = 200
UNSET = ('IWO_ATLAS_VIEWERS', 'IWO_ATLAS_JOB')
BUILDER_1375164 = '97e3199294cd9bf9ad5670b820c52833627bafd0566df65c0a856347540a5190'   # build_iwo_decks.py as committed in public-repo 1375164
SCRIPTS = {   # every file of scripts/ (outside __pycache__), working-tree bytes: public-repo 1375164 except build_iwo_decks.py (2026-10-15 change)
    'build_iwo_decks.py': '734125a8915e2a7790b2794db0c7bf429c477a83238b638a200af2b5fbeeca3c',
    'campaign_gates.py': 'c5e2fd5bb5711f7ab366d85fd8c13cb6bd3efcad387460308ea309e6348c0ceb',
    'campaign_sealed.py': '09d374d220efb17995d12d611aba13c9617ad1f761d3fb8dec95ae1fdbf8608c',
    'compare_experiment_simulation.py': 'b0a1c2ab6778e689d8275c1310c78af505d62f7d6b2d7ac3dd181148ec2c109c',
    'export_report_pdf.py': '9cfb4b364e10d09c2dde0010de436fc366d358c1052bbde5543fad3ddf3696ce',
    'extract_metrics.py': 'a7d0b236ecfa4f67433fc842a2b9cebeb295e4a5946f38ea72643139678edf63',
    'make_provenance_tables.py': '7ec8fc43f3be5006d62c6a89607f9cc072d1c74691e18a00c6aa2dcda527a81b',
    'material_laws.py': '748c2a287ad32b75c733f36b711ab91791aac16b3a3f376c4721ab8f8d261711',
    'plot_results.py': 'bd5c6fa39e157c3659a0fb52fbb4c350bb36942877e7123e8103988cc4f28a77',
    'plot_sensitivity.py': '858834ba2f288d3518d4e68a22250103967cc62e86da5dc51d6bf9e0714b6f69',
    'proc_guard.py': '6ac38ea89e0735d167c4df85e7b3efaeca83427970d172f4dd8b7b9fc48e7d80',
    'qe_build_inputs.py': '35bcbc15875471a80bf4387e72de6ab6d2440762ae6af70ed3f6f2c6fe1e0107',
    'run_atlas.py': 'b7927ac5b9747d5531ac827d220da6004e4a144d672ae16ab9bca2a28f46e6ae',
    'run_campaign.py': 'fb6e802f8c1cb71b56e153ed99504cc8e7e83d4c8eb7af8f13dc421d0fd125ac',
    'sensitivity_analysis.py': 'bb003c6563573f95d98cfdd9c8ca2360c1d318eb34dc4dc2d1009b513fbe88ee',
    'sensitivity_from_stage_runs.py': '81735baba71d06da10a86e5af8c00bb3b10444697da735c49fb9bc871ac1c95f'}
OTHER = {'analysis_2026-10-10_campaign/score_register.py': 'c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a',
         'analysis_2026-10-10_campaign/post_run_checks.py': '39d3d51d3b2470b1396196bcfce34dc4a8f0a6acd3bcb2a213001dc5ec3ed91f',
         'analysis_2026-10-10_campaign/regress_all_decks.py': 'd7f26e9bb44e976c173131c627e7cd7bc7a9e9dcbed6de189d7b26b50ad64603',
         'analysis_2026-10-10_campaign/regress_sealed_aware.py': '9c06581434762a12d1426b9b2333d3b8ffc7191bc6b2117c66b721bd8f1bb41d',
         'analysis_2026-10-10_campaign/campaign_extract.py': '1f6f324a0841d50bb20baf7f94b6444d688aaf4cbdf71707594a06f26e3e63ba',
         'analysis_2026-10-10_campaign/campaign_tools.py': '3b0403d9c5cc5423cb80dabc3765f9a781b7a06b512082b6f210971a9417ab0d',
         'analysis_2026-10-10_campaign/prelaunch_gate_a41.py': '35df463326bd7345236f3807f865d338a30cd2383606ed738643a5ba3449d75e',
         'config/iwo_material_model_v3.yaml': '51b184e8728c4e4ce5ed4110c56d4b1083b5d12f1d4d6b45aef52816ba63961c'}
SCORER_SHA = OTHER['analysis_2026-10-10_campaign/score_register.py']


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tsha(s): return hashlib.sha256(s.encode()).hexdigest()


def rid_n(rid): return int(rid[4:])


class Gate:
    def __init__(self): self.fails = []; self.stops = []

    def check(self, ok, what, detail=''):
        print(f"[{'OK' if ok else 'FAIL'}] {what}" + (f'  ({detail})' if detail else ''), flush=True)
        if not ok: self.fails.append(what)
        return ok

    def stop(self, what):
        print(f'[STOP] {what}', flush=True); self.stops.append(what)


def a41_module():
    """the A41 gate's process functions (merge_processes, list_processes, SILVACO, is_python, RUNNER_RE); loaded from its file, sha256 checked first"""
    spec = importlib.util.spec_from_file_location('prelaunch_gate_a41_procs', A41_GATE); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def list_processes():
    return a41_module().list_processes()


def amendment_logged(heading_words, row_words):
    """(heading found, decision row found): a register heading '### A<n>: ...' containing every word of heading_words and not 'draft', and a
    decision-log row ('| D-..') containing every word of row_words and 'IN FORCE'"""
    reg = REGISTER.read_text(encoding='utf-8', errors='replace').splitlines(); dec = DECISIONS.read_text(encoding='utf-8', errors='replace').splitlines()
    h = any(re.match(r'^###\s+A\d+\s*:', l) and all(w in l for w in heading_words) and 'draft' not in l.lower() for l in reg)
    d = any(l.startswith('| D-') and all(w in l for w in row_words) and 'IN FORCE' in l for l in dec)
    return h, d


def scorer_module():
    """the frozen scorer score_register.py c0f28bb9 (run_problems, read_cols), loaded from its file AFTER its sha256 (and those of the modules
    it imports: campaign_extract, campaign_tools, post_run_checks) is checked; nothing of it is changed or re-implemented here"""
    a = str(PKG / 'analysis_2026-10-10_campaign')
    if a not in sys.path: sys.path.insert(0, a)
    spec = importlib.util.spec_from_file_location('score_register_frozen', PKG / 'analysis_2026-10-10_campaign' / 'score_register.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def load_endpoint(sr, d):
    """(execution.json or None, columns of terminal_currents.csv via the frozen read_cols, or None) of run directory d"""
    d = Path(d); d = d if d.is_absolute() else PKG / d
    exj = json.loads((d / 'execution.json').read_text()) if (d / 'execution.json').is_file() else None
    return exj, sr.read_cols(d / 'terminal_currents.csv')


def grid_audit(c):
    """check 8 COMPUTED from the exported columns c (frozen read_cols) of S1-06R: counts and booleans only (no current value); the keys and the
    required values are those of the hand-written audit (CHECK8_INT, CHECK8_TRUE without log_reopen_ok, which needs deckbuild.out by hand)"""
    if not c or 'vg_V' not in c: return {'exported_rows': 0, 'vg_set_complete': False}
    vg = [float(x) for x in c['vg_V']]; fin = [round(x, 6) + 0.0 for x in vg if math.isfinite(x)]; grid = set(REG_GRID)
    return {'exported_rows': len(vg), 'vg_m1p6_count': fin.count(-1.6), 'continuation_rows_exported': sum(x in CONT_VG for x in fin),
            'off_grid_trap_rows': sum(x not in grid and x not in CONT_VG for x in fin) + (len(vg) - len(fin)),
            'vg_set_complete': len(fin) == len(vg) and set(fin) == grid, 'vg_unique': len(set(fin)) == len(fin),
            'values_finite': all(math.isfinite(float(v)) for col in c.values() for v in col)}


def grid_bad(ga):
    """keys of a computed check-8 audit that differ from the required values"""
    return [k for k, v in CHECK8_INT.items() if ga.get(k) != v] + [k for k in CHECK8_TRUE if k != 'log_reopen_ok' and ga.get(k) is not True]


def c8_path(rid, entry='S1-06R'):
    p = AUDITS / f'{entry}_check8_{rid}.json'; return p.relative_to(PKG).as_posix() if p.is_relative_to(PKG) else str(p)


def check8_audit(rid, entry='S1-06R'):
    """(ok, detail) for the manual check-8 audit record of run rid of entry (AUDITS/<entry>_check8_<rid>.json); strict equality, integers must be
    JSON integers (not booleans or strings), the CHECK8_TRUE keys must be JSON true"""
    p = AUDITS / f'{entry}_check8_{rid}.json'
    if not p.is_file(): return False, f'{p.name} missing'
    try: a = json.loads(p.read_text(encoding='utf-8'))
    except (ValueError, OSError) as ex: return False, f'{p.name} unreadable ({type(ex).__name__})'
    if not isinstance(a, dict): return False, f'{p.name} is not a JSON object'
    want = {'entry': entry, 'run': rid, 'deck_sha256': DECK[entry], 'result': 'PASS'}
    bad = [k for k, v in want.items() if a.get(k) != v]
    bad += [k for k, v in CHECK8_INT.items() if type(a.get(k)) is not int or a.get(k) != v]
    bad += [k for k in CHECK8_TRUE if a.get(k) is not True]
    ev = a.get('evidence')
    if not (isinstance(ev, (str, list, dict)) and ev): bad.append('evidence')
    return (not bad), (f'{p.name}: ' + (f'not as required: {bad}' if bad else 'all values as required'))


def audit_cites(path, gate, decision):
    if not path: return False
    p = Path(path); p = p if p.is_absolute() else PKG / p
    if not p.is_file() or p.stat().st_size == 0: return False
    t = p.read_text(errors='replace'); return gate in t and decision in t


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    g = Gate()
    try:
        return run(g, argv)
    except Exception as ex:   # fail closed
        g.check(False, f'unexpected error: {type(ex).__name__}: {ex}')
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked', flush=True)
        return 1


def run(g, argv):
    check_mode = '--check' in argv
    audit = argv[argv.index('--ack-audit') + 1] if '--ack-audit' in argv and argv.index('--ack-audit') + 1 < len(argv) else None
    print('C10 pre-launch gate, S1-06R (campaign_C10_S1r_repair) and campaign_C10_DIAG (no launch, nothing written)'
          + ('  [CHECK MODE: no invocation follows from this output]' if check_mode else ''), flush=True)
    g.check(sys.flags.isolated == 1, 'interpreter in isolated mode (python -I)')
    g.check(Path(sys.prefix).resolve() == VENV_PY.parents[1].resolve(), 'interpreter is the project venv', sys.prefix)
    g.check(Path.cwd().resolve() == PKG.resolve(), 'working directory is the package root', str(Path.cwd()))
    g.check(os.environ.get('IWO_MODEL_FILE') == MODEL_ENV, f'IWO_MODEL_FILE == {MODEL_ENV}', repr(os.environ.get('IWO_MODEL_FILE')))
    for k in UNSET: g.check(k not in os.environ, f'{k} unset', repr(os.environ.get(k)) if k in os.environ else '')

    # frozen files (before anything is imported from scripts/ or the A41 gate)
    files_ok = True
    for rel, h in PLAN_SHA.items(): files_ok &= g.check(fsha(PKG / rel) == h, f'{rel} sha256 == {h[:8]}...')
    have = {p.relative_to(PKG / 'scripts').as_posix() for p in (PKG / 'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    files_ok &= g.check(have == set(SCRIPTS), 'scripts/ file set == public-repo 1375164', f'extra {sorted(have - set(SCRIPTS))}, missing {sorted(set(SCRIPTS) - have)}' if have != set(SCRIPTS) else '')
    bad = sorted(f for f in SCRIPTS if f in have and fsha(PKG / 'scripts' / f) != SCRIPTS[f])
    files_ok &= g.check(not bad, f'scripts/ sha256 == 1375164, build_iwo_decks.py == pinned bytes {SCRIPTS["build_iwo_decks.py"][:8]} '
                        '(Codex 2026-10-14T19:02Z (a): builder accepted)', f'differ: {bad}' if bad else '')
    print(f'[INFO] build_iwo_decks.py differs from public-repo 1375164 ({BUILDER_1375164[:8]}...) by the PA-1/PA-4 builder change; pinned '
          f'{SCRIPTS["build_iwo_decks.py"][:8]}...', flush=True)
    for f, h in OTHER.items(): files_ok &= g.check(fsha(PKG / f) == h, f'{f} sha256 == {h[:8]}...')

    # plans
    s1r = json.loads((PKG / S1R_REL).read_text()); diag = json.loads((PKG / DIAG_REL).read_text())
    plans_ok = g.check(s1r.get('runnable') is True and 'gates' not in s1r and 'state_only' not in s1r and [e['id'] for e in s1r['runs']] == ['S1-06R']
                       and s1r['runs'][0]['label'] == LABEL['S1-06R'], 'S1R plan: runnable, no gates, not state-only, ids [S1-06R], registered label')
    gl = diag.get('gates') or []
    plans_ok &= g.check(diag.get('runnable') is True and diag.get('state_only') == {'sealed_dir': 'results/sealed/campaigns'}
                        and [x.get('id') for x in gl] == DIAG_GATES and all(x.get('scorer_sha256') == SCORER_SHA for x in gl),
                        'DIAG plan: runnable, state_only results/sealed/campaigns, gates G-S2-04/06/03/01 bound to scorer c0f28bb9')
    ids = [e['id'] for e in diag['runs']]
    plans_ok &= g.check(ids == DIAG_ORDER and all(e['label'] == LABEL[e['id']] for e in diag['runs']), 'DIAG plan: register order (S2-11 first), registered labels', str(ids))

    # dry build with the runner's own functions (after the file check: scripts/ goes on sys.path)
    entries = {**{e['id']: e for e in diag['runs']}, 'S1-06R': s1r['runs'][0]} if plans_ok else {}
    rc_cap = None
    if files_ok and plans_ok:
        sys.path.insert(0, str(PKG / 'scripts')); os.chdir(PKG)
        import run_campaign as rc
        rc_cap = getattr(rc, 'C10_CAP', None)
        texts = {i: rc.current_deck_text(e, e['overrides']) for i, e in entries.items()}
        bad_d = [i for i, t in texts.items() if tsha(t) != DECK[i]]
        bad_m = [i for i, e in entries.items() if tsha(rc.current_material_text(e['overrides'])) != MATERIAL[i]]
        g.check(not bad_d, f'dry-built deck text sha256 == pinned for S1-06R and the {len(DIAG_ORDER)} DIAG entries', f'differ: {bad_d}' if bad_d else '')
        g.check(not bad_m, 'dry-built material text sha256 == pinned for every entry', f'differ: {bad_m}' if bad_m else '')
        nt = [i for i in ('S1-06R',) + PA2 if re.search(r'\bno\.trap\b', texts[i], re.I)]
        g.check(not nt, 'NO.TRAP unset in the S1-06R and PA-2 decks (Codex 19:02Z (d); manual 5.28 l.53197)', f'set in {nt}' if nt else '')
    else:
        g.check(False, 'dry build not run (file or plan check failed)')

    # processes (A41 gate functions, file hash checked above)
    try:
        procs = list_processes() if files_ok else None
        if procs is None: g.check(False, 'process check not run (file check failed)')
    except Exception as ex:
        procs = None; g.check(False, f'process list readable ({type(ex).__name__}: {ex})')
    if procs is not None:
        a = a41_module(); me = os.getpid()
        sil = sorted({f'{n} pid {p}' for p, n, _ in procs if n in a.SILVACO})
        pyp = [(p, n, c) for p, n, c in procs if p != me and a.is_python(n)]
        unver = sorted({f'{n} pid {p}' for p, n, c in pyp if not (isinstance(c, str) and c.strip())})
        runners = sorted({f'{n} pid {p}' for p, n, c in pyp if isinstance(c, str) and a.RUNNER_RE.search(c)})
        g.check(not sil, 'no DeckBuild/ATLAS/TonyPlot/Athena/DevEdit process running', ', '.join(sil))
        g.check(not unver, 'every other python process has a readable command line (else UNVERIFIABLE)', ', '.join(unver))
        g.check(not runners, 'no python process running run_atlas / run_campaign', ', '.join(runners))

    # RUN_INDEX: run_id/label of every row; input columns only for in-scope runs above run_0077
    pairs, rows_new = [], {}
    with INDEX.open(newline='') as fh:
        for r in csv.DictReader(fh):
            pairs.append((r['run_id'], r['label']))
            if rid_n(r['run_id']) > rid_n(LAST_PRE) and r['label'] in LABEL.values():
                rows_new.setdefault(r['run_id'], []).append({k: r.get(k, '') for k in ('label', 'deck_sha256', 'model_sha256', 'notes', 'exit_code', 'output_dir')})
    all_ids = sorted({rid for rid, _ in pairs}, key=rid_n); nxt = f'run_{rid_n(all_ids[-1]) + 1:04d}'
    c10 = len({rid for rid, lab in pairs if lab.startswith('c10_')})
    eid_of = {v: k for k, v in LABEL.items()}
    after = sorted({rid for rid, _ in pairs if rid_n(rid) > rid_n(LAST_PRE)}, key=rid_n)
    other = [rid for rid in after if rid not in rows_new]
    g.check(not other, f'RUN_INDEX: every run above {LAST_PRE} is S1-06R or a DIAG entry', str(other))
    s211 = sorted({rid for rid, lab in pairs if lab == LABEL['S2-11']}, key=rid_n)
    g.check(s211 == S2_11_RUNS, f'RUN_INDEX: c10_s2_11_2p0 only in {S2_11_RUNS} (no third S2-11 launch)', str(s211))
    early = sorted({rid for rid, lab in pairs if lab in LABEL.values() and lab != LABEL['S2-11'] and rid_n(rid) <= rid_n(LAST_PRE)}, key=rid_n)
    g.check(not early, f'RUN_INDEX: no S1-06R/DIAG label at or below {LAST_PRE} other than S2-11', str(early))
    started = {}
    for rid in after:
        if rid not in rows_new: continue
        e = eid_of[rows_new[rid][0]['label']]
        g.check(e not in started, f'RUN_INDEX: one run id per label ({LABEL[e]})', f'{started.get(e)} and {rid}' if e in started else '')
        started.setdefault(e, rid)
    launched = [eid_of[rows_new[rid][0]['label']] for rid in after if rid in rows_new]   # STARTED runs in run-id order
    g.check(launched == LAUNCH_ORDER[:len(launched)], f'order: STARTED runs above {LAST_PRE} == a prefix of S1-06R -> DIAG order '
            '(S1-06R first, D-58 item 1; S2-11 reused from run_0076)', ' -> '.join(f'{e} {r}' for e, r in zip(launched, [r for r in after if r in rows_new])) or 'none')
    finished = {}
    for e, rid in started.items():
        first = rows_new[rid][0]; n = first['notes']
        g.check(n.startswith('STARTED') and f'model={MODEL_ENV}' in n.split() and first['deck_sha256'] == DECK[e] and first['model_sha256'] == MATERIAL[e],
                f'{rid} ({e}): STARTED-row input columns as pinned (deck_sha256, model_sha256, model note)')
        fin = [x for x in rows_new[rid][1:] if x['exit_code'] != '']
        finished[e] = fin[-1]['exit_code'] if fin else None
    inv = {r['run_id']: r for r in json.loads(INVENTORY.read_text())['runs']}
    i76 = inv.get('run_0076', {})
    g.check(i76.get('entry') == 'S2-11' and i76.get('label') == LABEL['S2-11'] and i76.get('deck_sha256') == DECK['S2-11'] and i76.get('model_sha256') == MATERIAL['S2-11'],
            'config/sealed_runs.json: run_0076 = S2-11 rerun with the A41 deck/model sha256 (DIAG reuses it by label; not opened here)')
    for e, rid in started.items():
        if e == 'S1-06R': continue
        s = inv.get(rid, {})
        g.check(s.get('label') == LABEL[e] and s.get('entry') == e and s.get('deck_sha256') == DECK[e] and s.get('model_sha256') == MATERIAL[e]
                and s.get('model_file') == MODEL_ENV, f'config/sealed_runs.json lists started {rid} ({e}) with the pinned values (state-only plan)')

    # sequence: S1-06R first (D-58 item 1), then DIAG in register order
    diag_started = [e for e in DIAG_ORDER[1:] if e in started]
    unfinished = [f'{started[e]} ({e})' for e in started if finished[e] is None]
    plan_rel, todo, ack = None, [], []
    if unfinished:
        g.stop(f'started run(s) without a finish row: {unfinished} (a launch in progress, or a runner crash): nothing is invoked; decide by hand')
    elif 'S1-06R' not in started:   # (a DIAG run without S1-06R first already failed the order check above)
        h, d = amendment_logged(['S1-06R'], ['S1-06R'])
        g.check(h, 'PA-1 logged: register heading "### A<n>: ..." naming S1-06R (not draft)')
        g.check(d, 'PA-1 logged: decision-log row naming S1-06R, IN FORCE')
        plan_rel, todo = S1R_REL, ['S1-06R']
    else:
        rid = started['S1-06R']; ec = finished['S1-06R']
        od = next((x['output_dir'] for x in reversed(rows_new[rid]) if x['output_dir']), ''); exj = PKG / od / 'execution.json' if od else None
        status = json.loads(exj.read_text()).get('status') if exj is not None and exj.is_file() else None
        if ec == '0' and status is None:
            g.stop(f'S1-06R {rid}: exit_code 0 but no readable execution.json under output_dir {od!r}: decide by hand')
        elif ec == '0' and status in SUCCESS:
            # (1) the frozen run_problems on BOTH comparison endpoints before anything is accepted (Codex 19:02Z (b))
            sr = scorer_module()
            exj_r, c_r = load_endpoint(sr, od); exj_0, c_0 = load_endpoint(sr, S1_02_DIR)
            p_r = sr.run_problems(exj_r, c_r)
            p_0 = (['execution.json missing'] if exj_0 is None else sr.run_problems(exj_0, c_0)) + (
                [] if exj_0 is not None and exj_0.get('run_id') == S1_02_RUN and exj_0.get('label') == 'c10_s1_02_13p2' else [f'not {S1_02_RUN} c10_s1_02_13p2'])
            if p_r or p_0:
                g.stop(f'S1 comparison endpoints invalid under the frozen run_problems (score_register.py c0f28bb9): S1-06R {rid}: '
                       f'{"; ".join(p_r) or "none"} | S1-02 {S1_02_RUN} ({S1_02_DIR}): {"; ".join(p_0) or "none"}. No PASS is accepted: '
                       'electron-only stays ASSUMED, never TESTED; S1-06R is UNVERIFIED for PA-1 (no row deleted, no relaunch): decide by hand before DIAG')
            else:
                print(f'[OK] frozen run_problems: none for S1-06R {rid} and S1-02 {S1_02_RUN}', flush=True)
                # (2) check 8: computed from the S1-06R export (complete V_G set, finite, unique), then the hand-written record
                ga = grid_audit(c_r); gb = grid_bad(ga)
                c8_ok, c8_detail = check8_audit(rid)
                if gb:
                    g.stop(f'check 8 COMPUTED from S1-06R {rid} terminal_currents.csv fails {gb} '
                           f'({", ".join(f"{k} {ga.get(k)}" for k in gb)}; V_G set vs the registered 76-point grid): S1-06R is UNVERIFIED under PA-1 '
                           '(unexpected continuation/cut-back rows are not deleted to obtain PASS; no relaunch); electron-only stays ASSUMED: decide by hand')
                elif not c8_ok:
                    g.stop(f'check 8 (continuation log handling) not passed for S1-06R {rid}: {c8_detail}. Required before S1-06R is interpreted '
                           f'and before DIAG: {c8_path(rid)} with exported_rows 76, vg_m1p6_count 1, continuation_rows_exported 0, '
                           'off_grid_trap_rows 0, vg_set_complete/vg_unique/values_finite/log_reopen_ok true, result PASS, evidence. '
                           'A failed check makes S1-06R invalid for scoring (UNVERIFIED, no relaunch): decide by hand')
                else:
                    print(f'[OK] check 8 (S1-06R {rid}): computed V_G set == registered 76-point grid, unique, finite; {c8_detail}', flush=True)
                    # (3) the S1-rule record
                    cp = EXTRACT / f'compare_{rid}_vs_{S1_02_RUN}.json'
                    rec = json.loads(cp.read_text()) if cp.is_file() else None
                    ok_rec = rec is not None and rec.get('run') == rid and rec.get('ref') == S1_02_RUN and str(rec.get('rule', '')).startswith('S1-06')
                    verdict = str(rec.get('verdict')) if ok_rec else None
                    cmp_cmd = (f'& "{VENV_PY}" -B analysis_2026-10-10_campaign/campaign_extract.py compare "{od}" "{S1_02_DIR}" --rule s1_06 '
                               '(package root, IWO_MODEL_FILE as set)')
                    if verdict == 'PASS': print(f'[OK] S1 rule (S1-06R {rid} vs S1-02 {S1_02_RUN}): PASS; electron-only TESTED at 13.2 nm', flush=True)
                    elif verdict and verdict.startswith('FAIL'): g.stop(f'S1 rule FIRED ({cp.name}: {verdict}): STOP and re-plan with Codex and the user (Codex item 2)')
                    else: g.stop(f'S1 rule not evaluated (record {cp.name}: {verdict or "missing"}). Comparison command (actual run directories):\n    {cmp_cmd}')
        else:
            print(f'[INFO] S1-06R {rid} invalid (exit_code {ec}, status {status}): electron-only stays ASSUMED (Codex item 2); not interpreted, so no check-8 audit is required; DIAG may proceed', flush=True)
        h, d = amendment_logged(['S2-01', 'S2-02', 'S2-03', 'continuation'], ['S2-01', 'continuation'])
        g.check(h, 'PA-2 logged: register heading naming S2-01, S2-02, S2-03 and "continuation" (not draft)')
        g.check(d, 'PA-2 logged: decision-log row naming S2-01 and "continuation", IN FORCE')
        for e in PA2:   # check 8 for every PA-2 run that finished with exit_code 0 (record only: the sealed run directory is never opened)
            if e in started and finished.get(e) == '0':
                ok8, det8 = check8_audit(started[e], e)
                if ok8: print(f'[OK] check 8 (PA-2 {e} {started[e]}, record): {det8}', flush=True)
                else: g.stop(f'check 8 (PA-2 continuation log handling) not passed for {e} {started[e]}: {det8}. Required before its gate decision is '
                             f'read and before any later DIAG invocation: {c8_path(started[e], e)} (same keys as for S1-06R, entry {e}, its pinned deck; '
                             'value-free: V_G set, finiteness, uniqueness, log echo). A failed check makes the run invalid for scoring '
                             '(UNVERIFIED; no row deleted, no relaunch): decide by hand')
        todo = [e for e in DIAG_ORDER[1:] if e not in started]
        plan_rel = DIAG_REL if todo else None
        st = DIAG_STATE
        sealed = [p for p in SEALED_DIR.glob('campaign_C10_DIAG.*')]
        print('[INFO] DIAG sealed record files (existence only, not opened): ' + (', '.join(p.name for p in sealed) or 'none'), flush=True)
        if st.is_file():   # state projection only (value-free gate decisions)
            for r in json.loads(st.read_text()).get('gates', []):
                if r.get('action') != 'stop' or r.get('acknowledged_utc') or r.get('superseded_by'): continue
                if audit_cites(audit, r['gate'], r['decision_id']): ack.append(r['gate']); print(f'[OK] gate stop {r["gate"]} decision {r["decision_id"]}: audit cited', flush=True)
                else: g.stop(f'DIAG gate stop {r["gate"]} decision {r["decision_id"]} ({r.get("state")}) not acknowledged: rerun this gate with --ack-audit <completed audit naming both>')
        elif diag_started:
            g.check(False, 'DIAG runs exist but results/campaigns/campaign_C10_DIAG.json (state) is missing')

    ms = re.findall(r'^\s*max_launches:\s*(\d+)', SOLVER.read_text(), re.M); cap = int(ms[0]) if len(ms) == 1 else -1
    g.check(cap == MAX_LAUNCHES, f'config/solver.yaml: exactly one max_launches and it == {MAX_LAUNCHES} (D-58 (4): not raised)', f'found {ms}')
    g.check(C10_CAP == 200 and rc_cap == 200, 'C10 cap == 200 (gate constant and run_campaign.C10_CAP; D-58 (4): not raised)', f'gate {C10_CAP}, runner {rc_cap}')
    k = 1 if todo else 0
    g.check(cap > 0 and len(all_ids) + k <= cap, f'global budget: {len(all_ids)} used + {k} <= max_launches {cap}')
    g.check(c10 + k <= C10_CAP, f'C10 cap: {c10} used + {k} <= {C10_CAP}')
    print(f'[INFO] RUN_INDEX: {len(all_ids)} distinct run ids (max {all_ids[-1]}), c10 {c10}/{C10_CAP}; in-scope started: '
          + (', '.join(f'{e} {r}' for e, r in started.items()) or 'none') + f'; next free id {nxt}', flush=True)

    if g.fails:
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked. Report the failure; a running DeckBuild/ATLAS process is not killed '
              'without the user\'s decision.', flush=True)
        return 1
    if g.stops:
        print(f'GATE STOP ({len(g.stops)}): a main-session decision is needed; nothing may be invoked.', flush=True)
        return 3
    if not todo:
        print('NOTHING TO LAUNCH: S1-06R and every DIAG entry have started. Do not invoke either plan again. (Exit 4 is not a pass.)', flush=True)
        return 4
    cmd = f'& "{VENV_PY}" scripts/run_campaign.py {plan_rel}' + (f' --ack-gate {",".join(ack)} --ack-audit "{audit}"' if ack else '')
    seq = ('S1-06R -> ' + nxt + ' (one launch; the plan has one entry)' if plan_rel == S1R_REL else
           f'{todo[0]} -> {nxt}; the invocation then CONTINUES through the DIAG order ({", ".join(todo[1:]) or "none"}) until a declared gate '
           'stops it (FIRED/UNRESOLVED) or the plan ends: a NOT_FIRED gate does not stop it. S2-11 is reused from run_0076 by label.')
    print(f'GATE PASSED. Next run: {seq}\nOnly with the user\'s go for THIS launch (the hook asks). '
          + ('Would-be command (check mode, not an instruction)' if check_mode else 'Command (same PowerShell session, package root, IWO_MODEL_FILE as set)')
          + f':\n{cmd}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
