"""C10 pre-launch gate for stage G1 = S4a (register section 3 step 6, "S4a in batches"; register A49 (decision) and A50 (execution entries),
2026-10-15; no Codex review, D-63; Claude go under D-59). NO launch, NO file written, nothing sealed opened. Run it immediately before EVERY
invocation of config/campaign_C10_S4a_b1.json (S4A-02..06), config/campaign_C10_S4a_b2.json (S4A-07..11) and config/campaign_C10_S4a_b3.json
(S4A-12..15), in the same PowerShell session and working directory (the package root) as the invocation:

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"
    & "<venv>\\Scripts\\python.exe" -I -B "<this file>" [--check]

It loads prelaunch_gate_c10_f.py (sha256 pinned below; d0baaca3, A48) and, through it, prelaunch_gate_c10_de.py (1b67776c, A47) and
prelaunch_gate_c10.py (c173598d, A46) as modules for their constants and helpers (Gate, process functions, amendment_logged, scripts/ and
frozen-file pins, the S1-06R/DIAG, D/E and stage F labels and order); the three earlier gates are unchanged.

Exit codes (ONLY 0 is a pass): 0 the next plan is launchable (prints the ONE command); 1 a check failed or an input is unreadable (fail closed);
3 STOP: a started run has no finish row; 4 nothing to launch (every S4a entry has started); not a pass.

Checks
  interpreter/cwd/env  as the C10 gate (-I, project venv, package root, IWO_MODEL_FILE V3, IWO_ATLAS_VIEWERS / IWO_ATLAS_JOB unset)
  files        the F gate file (pinned) and, through it, the D/E and C10 gate files; scripts/ file set and sha256 (public-repo 1375164 + builder
               734125a8); the C10 gate's OTHER files (frozen scorer c0f28bb9, post_run_checks, regress wrappers, campaign_extract/tools, A41 gate,
               V3 model); the frozen H-F v4 files and profile_shared.py; campaign_matrix.json f06e8d77 (unchanged, form N); the plan generator
               (A50); the A49 driver s3_decision_a49.py and its decision record profile/s3_adoption_A49.json (form N, nothing adopted); the three
               S4a route plans and the held stage plan (pinned here)
  decision     profile/s3_adoption_A49.json: s4a_form.form == 'N', chosen tail/mobility None, verdict 'DECIDED: S4a form N ...'
  plans        each route plan: runnable, no gates, state_only results/sealed/campaigns, ids and labels as registered (A50), in matrix order;
               the stage plan campaign_C10_S4a_spacefilling held (runnable false)
  dry build    run_campaign.current_deck_text / current_material_text for the 42 entries == pinned; PA-12 reuse: the dry-built S4A-01-2p0/6p3/13p2
               entries of the held stage plan == the STARTED-row deck/model sha256 of run_0061 / run_0068 / run_0069 (pinned)
  amendments   register headings '### A<n>: ...' for A49 (S3 decision) and A50 (S4a execution entries) (not draft) and IN FORCE decision-log rows
  processes    as the C10 gate (no Silvaco process, no runner python, every python command line readable)
  RUN_INDEX    run_id/label of every row; for runs above run_0077: the label is S1-06R/DIAG, D/E, stage F or S4a; every stage F entry has started
               and has a finish row (presence only) BEFORE the first S4a run id; S4a labels never at or below run_0113; one run id per label;
               STARTED order == a prefix of the registered S4a order; STARTED-row input columns (deck_sha256, model_sha256, model note) as pinned;
               a finish row for every started S4a run (presence only; else STOP, exit 3); every started S4a run listed in config/sealed_runs.json
               with the pinned values (A41 (e); appended right after each invocation)
  budget       config/solver.yaml exactly one max_launches == 260; C10 cap 200 (gate constant and run_campaign.C10_CAP); distinct run ids + k
               <= 260 and c10 run ids + k <= 200 (k = launches of the next invocation); A49 (h) fit: c10 used + unlaunched S4a + the remaining
               never-cut need 100 (A41(d) 6 + 3-D NC 17 + S4b 18 + S4c/S4d 6 + l = 0 triple 3 + S5 30 + S6 core 12 + S7 2 + repairs 6) <= 200
"""
import csv
import hashlib
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

PKG = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1")
F_GATE = PKG / 'analysis_2026-10-10_campaign' / 'prelaunch_gate_c10_f.py'
F_GATE_SHA = 'd0baaca36b77cbe95c598a641f0a89366d4e2d496cf59a4935aa0ead4de1741d'   # A48 / D-68
B1, B2, B3 = 'config/campaign_C10_S4a_b1.json', 'config/campaign_C10_S4a_b2.json', 'config/campaign_C10_S4a_b3.json'
STAGE = 'config/campaign_C10_S4a_spacefilling.json'
PLAN_SHA = {B1: '941b1b59541d20e471e77f944916c1674f44efad22a300cc7a40d929d1a7ac6d', B2: 'c0397ef56783a48e078ca13d16e9c1b889978c2e025958f1a1fe6d9e051c2b15',
            B3: '97f92ee8370dad3b175a2f086452708a07b51cb3e8d89b016af0d98c650dfca3'}
STAGE_SHA = 'df7b031ead4e420598b0dbed426a7f698f6c6fe95ad098ffd5cf86be762a5daf'
DECISION = 'analysis_2026-10-10_campaign/profile/s3_adoption_A49.json'
FROZEN = {'analysis_2026-10-10_campaign/hf_score_draft.py': '96a2147eae6a07a2ea0afbed2d63476283c2d5bca3ffdfd7f829f248af3a1c81',   # H-F v4 (frozen)
          'analysis_2026-10-10_campaign/profile_s4s5.py': '429b3a3f3f5c1e650d17760e11665ddbce140ef434b5f80f29e7cd2f4fcf0a4e',    # S4b/S5 v4 (frozen)
          'analysis_2026-10-10_campaign/profile_shared.py': '958c3605a316393184f022a80c421505e8b9f99a1d214423ec79b83286209d17',
          'analysis_2026-10-10_campaign/campaign_matrix.json': 'f06e8d7721f75aec3f78da06de1c1686c59307c33725bd8822c3ec3e0f0a443c',   # unchanged (form N)
          'analysis_2026-10-10_campaign/make_campaign_configs.py': 'a1262a6edb6deeeff0f410d3d85e7191eb407112e1e3276efcd4ab2aa9ba1698',   # A50
          'analysis_2026-10-10_campaign/s3_decision_a49.py': '72fb4295ac7d624e2a2d0c63394da651bf845b0b28cab2362108bcd6a3308a42',     # A49 driver
          DECISION: '9ad43a88451082422e7b4faeaa710122aff28f44a94cff5562eeeb33f05b4993'}                                            # A49 record
TAGS = ('2p0', '6p3', '13p2')
FILM = {'2p0': 2.0, '6p3': 6.3, '13p2': 13.2}
TIMEOUT = {'2p0': 1600, '6p3': 2000, '13p2': 3100}
ORDER = [f'S4A-{k:02d}-{t}' for k in range(2, 16) for t in TAGS]   # A50 launch order (matrix order)
PLAN_IDS = {B1: ORDER[0:15], B2: ORDER[15:30], B3: ORDER[30:42]}
PLAN_OF = {k: rel for rel, ids in PLAN_IDS.items() for k in ids}
LABEL = {k: f'c10_{k.lower().replace("-", "_")}_{k.split("-")[-1]}' for k in ORDER}
DECK = {'S4A-02-2p0': 'ab9cb5424e26ed865f33484505ee768c7dee95f4501b3e8d6554f774673bb647', 'S4A-02-6p3': 'e63c3549f3b3100946d6091e57235ea046f505f0bad5902c861bf90becf38907',
        'S4A-02-13p2': 'ec5a1c0e8497e377ce4600527a47bbc3846399045fd4fe2cacb69bf9a6eb7931', 'S4A-03-2p0': 'f507851fbdaf8639c353e4aa75ae7e153e2115dc81c9838a66de39d6c1578159',
        'S4A-03-6p3': '704d8c68137910f877050836047dd2796a6f1582f37cd98768c2d0f5405d1178', 'S4A-03-13p2': 'a3fa0c0a36ddfdc2a008c3ae62bcc14189f6aaac13ca41269cfc5aa6d8a364c0',
        'S4A-04-2p0': 'a8ef888ce526471e4cfad1ca7abe1c077b96ed583e62f49d49f521c64ee95144', 'S4A-04-6p3': '8ef3fffeae783f6ccf6b50afa413c24a380da6078603963dcd1bb3d294b80182',
        'S4A-04-13p2': 'd0a4e8cfa970f0e0cab6696ebb14b81cb7ac9ada371f8c56594d1e325c8068c8', 'S4A-05-2p0': '8b5ab387a069a85b99b831ef48cd1a35c46293409903370119ee3be7c8124368',
        'S4A-05-6p3': '069827e32dee512359547a6b2917af66ec8550cc6c234ef2a0ea6b5f8c7912fa', 'S4A-05-13p2': '2cf71add8db36c104dc4f024d427623de61a7a5c31baa3100571879bf41c854b',
        'S4A-06-2p0': 'bf1c072347b204f9efdbef3bc380d90b0db05026b83297ce4502f8a23990aee6', 'S4A-06-6p3': '925874410fd46ad7359ae86cb9469cf9f2ff81aff6ead3e66a796054c52b65ba',
        'S4A-06-13p2': '6c15e218a03feb9599b9c6c248fa5003178387002f91118a2daf2dcf1bbe78b1', 'S4A-07-2p0': '7fa7f165269fdbb4c813c69a5e229615f0265a607597c71fc6635f1c83642b65',
        'S4A-07-6p3': '0ffa983f056359162070b820c6565a2876ae9238976815be3446609e80dc22a9', 'S4A-07-13p2': '37a81698b84e7ec9dd2a04b6c7594993df39e684b6ef5c40811373c4471cb178',
        'S4A-08-2p0': 'b5842d5c8c553bdf212f53c00ffa538480bd6b8014149e10613316b1cbd05c1a', 'S4A-08-6p3': '03aae8b523f16f849830e51cd00ae25387cef2d08572df88eda4c9d34b3c1b7c',
        'S4A-08-13p2': '8df1dcb673e6de501c24969aa45bdeb858f1e515df3b27c4f1135a378e794c7a', 'S4A-09-2p0': 'b431b3448a531296b2e0b56024d647371557324c381982673127ff88273e56bd',
        'S4A-09-6p3': 'cbeb3b716d4fd702e6e3db8c094abdbaa8b7d5bbb8b6c813b005eab77f5acc8b', 'S4A-09-13p2': '4a54299843f10f27d2b1bf74a9df05a426f152977cf2fe294207a4a4674676bb',
        'S4A-10-2p0': '873b17a6801b3d1886bc2ac05adb33da4db9812da4078925de378495e96ef721', 'S4A-10-6p3': '390d79c7343095990a7d292b2d7567839776ecdbb01513fab0fc2c16a375a8a9',
        'S4A-10-13p2': '3093f45f074311a695ee0776d1eef228fc5e2ab9bd378efa0b3bf09156d99c0e', 'S4A-11-2p0': 'fd90e3821c06c93577c9db13e201776b676aff85c170dabeea36e24a7b8b1d2e',
        'S4A-11-6p3': '01dfd9080669dd776f97866279b9b40e1701aca93009fa95d0d143e0bff842c5', 'S4A-11-13p2': 'bf6adcad4a4ef86d7b27fddaade8839e86febb072a9890021d3203fbfded6b14',
        'S4A-12-2p0': '92bdc32a5e734ab9eba04352f484fe7d68b9997352c23e3bc70d61904925bb75', 'S4A-12-6p3': '01bcbcfe33af896f2818d2a0c2f93abff5c34ca539ea6fdfdcd123277937c298',
        'S4A-12-13p2': 'f8f6310a279d8ea523545daa1fcb824bc6698eaa7bab8280b46baea5fa37e3d5', 'S4A-13-2p0': '96e1c76953ad2831337fc5baf36d0b93c92884a9868e58438a222674f8b4987d',
        'S4A-13-6p3': '47d88d4334d0edd20d96386b4dcb5a7bbb7d88cd1f636b2eae86816b32726007', 'S4A-13-13p2': 'd9f6ee82b36b610af14e6e2c8fcd2913f166e192e2df0ab844204415c88ecdb5',
        'S4A-14-2p0': '41d61e75bcb325e661313001c5ef512bfe743f0da9dd4311a19412ed019df2f6', 'S4A-14-6p3': 'dedffcfcf1d4b9a78b0cbca5ecdf20732469381d7421653ed07d1d635f012d7c',
        'S4A-14-13p2': 'ff39325384e6278a7858d9d809adb677493c96f282afd76e774c7157d19f1f5d', 'S4A-15-2p0': '67a22d761b7523461d74a6fe6dff4a698392beb46e33bc9b74595087c61c79fd',
        'S4A-15-6p3': '66f57f490eb9fda5f8ee0b693fc82e825c9b967ec1b986400203a88ff6eeda50', 'S4A-15-13p2': 'b7aa4290c8de4e3b2e23411ba496eadb69b0a52e7f71368ab27cbbdb6731dbfe'}
MAT_BY_CAND = {'S4A-02': '18b52906318f5004ec0b9201303b0c0a71bef425f2ce777c4798b668b5ce18a7', 'S4A-03': 'a0ebf623e4551f1383d45cef61ce2eb9cb92437da1534cb455156cc3f73a1fec',
               'S4A-04': 'fb1a3f7a837179c2403a1c048ad90557f5d88017952228772ddfbca03da0e835', 'S4A-05': '299f186894c13d197ef66089e1db6d1885e038ad6470f4c2998fd7143abb9a2c',
               'S4A-06': 'ba974ec51efe52fe0b1d262bd69654263eb3e0ab9d5593b6bac5e75878962963', 'S4A-07': 'dcc028b8b6c0421ee49ecb300727c730ea79eaabdab42e19f625d60ec324a499',
               'S4A-08': 'a2fcc4fe487d65a01883df93242999dc1031a75f94f407be4650a9cb75fc7d20', 'S4A-09': '2e8d25cefbe9f081bea0295de5aa703cbd555c96787786254840118972a167c9',
               'S4A-10': 'da8f549316216843a39fdc2a0e688eb80117f911b5682f62479bcdfd90e6aade', 'S4A-11': 'f6b3e118faca7fd7abe5bca2cadba1495a68485381879b82d26831c659de114f',
               'S4A-12': '608d9b7a5ab9ffc8e9e5796df6d3aedef136bea1b7f1c3b159243b65938a6ab2', 'S4A-13': 'e58ac80af73549b187b1b0de4fd1356194ee54bc5aded5e8ff09c6909f7dd082',
               'S4A-14': '021d78ae84d91e213dedc45eae15bb466b57b4b7241845edfe9d039eacf42856', 'S4A-15': '52808e0cde96b5e0daa306d37fd260e47a4f4b326742b8b5c5897ad24a915aed'}
MATERIAL = {k: MAT_BY_CAND[k[:6]] for k in ORDER}
_M0 = '974b23ea65ceaa38185221c1a62bb6f1b4eef54fd4884bb7eaadc38a83f18204'
REUSE = {'S4A-01-2p0': ('run_0061', 'c10_s0_01_2p0', 'd2fd986f9f68b1758013e66b3c04804c6d13ca741a0f79defbfeba9360b20f7a', _M0),   # PA-12 (A49 (e))
         'S4A-01-6p3': ('run_0068', 'c10_s1_01_6p3', '769f173c2f4281d313231ac610cca92da2530b4443637791b4608d867524109b', _M0),
         'S4A-01-13p2': ('run_0069', 'c10_s1_02_13p2', '1bd2ab678fc99d2ea524b0c57f8c81d350d7b9b458e15a0fee28c51469ad7717', _M0)}
A49_HEADING = ['S3 decision', 'PA-8', 'PA-12', 'PA-16', 'PA-20', 'S4a forms']
A49_ROW = ['A49', 's3_decision_a49.py', 'PA-8']
A50_HEADING = ['S4a execution entries', 'form N', 'S4A-02', 'S4A-15', 'prelaunch_gate_c10_g.py']
A50_ROW = ['A50', 'form N', 'campaign_C10_S4a_b1', 'prelaunch_gate_c10_g.py']
LAST_F = 'run_0113'   # last stage F run (S3-09); every S4a run id is above it
SEALED_DIR = 'results/sealed/campaigns'
NEED_AFTER_S4A = 6 + 17 + 18 + 6 + 3 + 30 + 12 + 2 + 6   # A49 (h): never-cut need after S4a = 100


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def f_module():
    spec = importlib.util.spec_from_file_location('prelaunch_gate_c10_f_pinned', F_GATE); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def decision_ok(path):
    """(ok, detail): the A49 decision record selects form N with nothing adopted"""
    try: d = json.loads(Path(path).read_text())
    except Exception as ex: return False, f'unreadable ({type(ex).__name__})'
    f = d.get('s4a_form') or {}; ch = d.get('chosen') or {}
    ok = (f.get('form') == 'N' and f.get('launches') == 42 and ch.get('tail') is None and ch.get('mobility') is None
          and str(d.get('verdict', '')).startswith('DECIDED: S4a form N'))
    return ok, f'form {f.get("form")}, chosen {ch}, verdict {str(d.get("verdict"))[:60]}'


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if fsha(F_GATE) != F_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10_f.py sha256 == {F_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    FG = f_module()
    if fsha(FG.DE_GATE) != FG.DE_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10_de.py sha256 == {FG.DE_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    DE = FG.de_module()
    if fsha(DE.C10_GATE) != DE.C10_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10.py sha256 == {DE.C10_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    C = DE.c10_module(); g = C.Gate()
    try:
        return run(FG, DE, C, g, argv)
    except Exception as ex:   # fail closed
        g.check(False, f'unexpected error: {type(ex).__name__}: {ex}')
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked', flush=True); return 1


def run(FG, DE, C, g, argv):
    check_mode = '--check' in argv
    print('C10 pre-launch gate, stage G1 = S4a (campaign_C10_S4a_b1, _b2, _b3; register A49 / A50; no launch, nothing written)'
          + ('  [CHECK MODE: no invocation follows from this output]' if check_mode else ''), flush=True)
    g.check(True, f'prelaunch_gate_c10_f.py sha256 == {F_GATE_SHA[:8]}... (loaded with the D/E and C10 gates for pins and helpers)')
    g.check(sys.flags.isolated == 1, 'interpreter in isolated mode (python -I)')
    g.check(Path(sys.prefix).resolve() == C.VENV_PY.parents[1].resolve(), 'interpreter is the project venv', sys.prefix)
    g.check(Path.cwd().resolve() == PKG.resolve(), 'working directory is the package root', str(Path.cwd()))
    g.check(os.environ.get('IWO_MODEL_FILE') == C.MODEL_ENV, f'IWO_MODEL_FILE == {C.MODEL_ENV}', repr(os.environ.get('IWO_MODEL_FILE')))
    for k in C.UNSET: g.check(k not in os.environ, f'{k} unset', repr(os.environ.get(k)) if k in os.environ else '')

    files_ok = g.check(fsha(FG.DE_GATE) == FG.DE_GATE_SHA and fsha(DE.C10_GATE) == DE.C10_GATE_SHA,
                       f'prelaunch_gate_c10_de.py sha256 == {FG.DE_GATE_SHA[:8]}... and prelaunch_gate_c10.py sha256 == {DE.C10_GATE_SHA[:8]}...')
    for rel, h in PLAN_SHA.items(): files_ok &= g.check(fsha(PKG / rel) == h, f'{rel} sha256 == {h[:8]}...')
    files_ok &= g.check(fsha(PKG / STAGE) == STAGE_SHA, f'{STAGE} sha256 == {STAGE_SHA[:8]}... (held stage plan, A50 hold text)')
    have = {p.relative_to(PKG / 'scripts').as_posix() for p in (PKG / 'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    files_ok &= g.check(have == set(C.SCRIPTS), 'scripts/ file set == public-repo 1375164 (+ pinned builder)', '' if have == set(C.SCRIPTS) else f'extra {sorted(have - set(C.SCRIPTS))}, missing {sorted(set(C.SCRIPTS) - have)}')
    bad = sorted(f for f in C.SCRIPTS if f in have and fsha(PKG / 'scripts' / f) != C.SCRIPTS[f])
    files_ok &= g.check(not bad, f'scripts/ sha256 as pinned (build_iwo_decks.py {C.SCRIPTS["build_iwo_decks.py"][:8]})', f'differ: {bad}' if bad else '')
    for f, h in {**C.OTHER, **FROZEN}.items(): files_ok &= g.check(fsha(PKG / f) == h, f'{f} sha256 == {h[:8]}...')
    dok, ddet = decision_ok(PKG / DECISION)
    files_ok &= g.check(dok, 'A49 decision record: S4a form N (nothing adopted; 2-D LHS seed 20261010; 42 launches)', ddet)

    plans = {rel: json.loads((PKG / rel).read_text()) for rel in PLAN_SHA}
    plans_ok = True
    for rel, p in plans.items():
        ids = [e['id'] for e in p['runs']]; labs = {e['id']: e['label'] for e in p['runs']}
        tos = {e['id']: e['timeout'] for e in p['runs']}
        plans_ok &= g.check(p.get('runnable') is True and 'gates' not in p and p.get('state_only') == {'sealed_dir': SEALED_DIR} and ids == PLAN_IDS[rel]
                            and labs == {k: LABEL[k] for k in PLAN_IDS[rel]} and tos == {k: TIMEOUT[k.split('-')[-1]] for k in PLAN_IDS[rel]},
                            f'{rel}: runnable, no gates, state_only {SEALED_DIR}, ids {PLAN_IDS[rel][0]}..{PLAN_IDS[rel][-1]} with the registered labels and timeouts',
                            f'{ids[:2]}...')
    stage = json.loads((PKG / STAGE).read_text())
    plans_ok &= g.check(stage.get('runnable') is False and [e['id'] for e in stage['runs']][:3] == list(REUSE), f'{STAGE}: held, starts with S4A-01-*')
    rc_cap = None
    if files_ok and plans_ok:
        sys.path.insert(0, str(PKG / 'scripts')); os.chdir(PKG)
        import run_campaign as rc
        rc_cap = getattr(rc, 'C10_CAP', None)
        ent = {k: next(e for rel in PLAN_SHA for e in plans[rel]['runs'] if e['id'] == k) for k in ORDER}
        bad_d = [k for k, e in ent.items() if C.tsha(rc.current_deck_text(e, e['overrides'])) != DECK[k]]
        bad_m = [k for k, e in ent.items() if C.tsha(rc.current_material_text(e['overrides'])) != MATERIAL[k]]
        g.check(not bad_d, 'dry-built deck text sha256 == pinned for the 42 S4a entries', f'differ: {bad_d}' if bad_d else '')
        g.check(not bad_m, 'dry-built material text sha256 == pinned', f'differ: {bad_m}' if bad_m else '')
        reuse_dry = {e['id']: (C.tsha(rc.current_deck_text(e, e['overrides'])), C.tsha(rc.current_material_text(e['overrides']))) for e in stage['runs'][:3]}
    else:
        g.check(False, 'dry build not run (file or plan check failed)'); reuse_dry = {}

    for words, row, what in ((A49_HEADING, A49_ROW, 'A49'), (A50_HEADING, A50_ROW, 'A50')):
        h, d = C.amendment_logged(words, row)
        g.check(h, f'{what} logged: register heading "### A<n>: ..." naming {", ".join(words)} (not draft)')
        g.check(d, f'{what} logged: decision-log row naming {", ".join(row)}, IN FORCE')

    try:
        procs = C.list_processes() if files_ok else None
        if procs is None: g.check(False, 'process check not run (file check failed)')
    except Exception as ex:
        procs = None; g.check(False, f'process list readable ({type(ex).__name__}: {ex})')
    if procs is not None:
        a = C.a41_module(); me = os.getpid()
        sil = sorted({f'{n} pid {p}' for p, n, _ in procs if n in a.SILVACO})
        pyp = [(p, n, c) for p, n, c in procs if p != me and a.is_python(n)]
        unver = sorted({f'{n} pid {p}' for p, n, c in pyp if not (isinstance(c, str) and c.strip())})
        runners = sorted({f'{n} pid {p}' for p, n, c in pyp if isinstance(c, str) and a.RUNNER_RE.search(c)})
        g.check(not sil, 'no DeckBuild/ATLAS/TonyPlot/Athena/DevEdit process running', ', '.join(sil))
        g.check(not unver, 'every other python process has a readable command line (else UNVERIFIABLE)', ', '.join(unver))
        g.check(not runners, 'no python process running run_atlas / run_campaign', ', '.join(runners))

    # RUN_INDEX: run_id/label of every row; for sealed rows only the STARTED-row input columns and finish-row presence
    c10_labels = set(C.LABEL.values()); de_of = {v: k for k, v in DE.LABEL.items()}; f_of = {v: k for k, v in FG.LABEL.items()}
    s_of = {v: k for k, v in LABEL.items()}
    pairs, rows_s, fin_f, reuse_rows = [], {}, {}, {}
    with C.INDEX.open(newline='') as fh:
        for r in csv.DictReader(fh):
            pairs.append((r['run_id'], r['label']))
            if r['run_id'] in {v[0] for v in REUSE.values()} and r.get('notes', '').startswith('STARTED'):
                reuse_rows.setdefault(r['run_id'], (r['label'], r['deck_sha256'], r['model_sha256']))
            if C.rid_n(r['run_id']) <= C.rid_n(C.LAST_PRE): continue
            if r['label'] in s_of:
                rows_s.setdefault(r['run_id'], []).append({k: r.get(k, '') for k in ('label', 'deck_sha256', 'model_sha256', 'notes', 'exit_code')})
            elif r['label'] in f_of:
                fin_f[r['run_id']] = fin_f.get(r['run_id'], False) or r.get('exit_code', '') != ''
    # PA-12 reuse (A49 (e)): the dry-built S4A-01 entries == the reused runs' STARTED-row inputs
    for k, (rid, lab, dk, mk) in REUSE.items():
        got = reuse_rows.get(rid); dry = reuse_dry.get(k)
        g.check(got is not None and got[0] == lab and got[1] == dk and got[2] == mk and dry is not None and dry == (dk, mk),
                f'PA-12: {k} reused as {rid} ({lab}): dry-built deck/material == its STARTED-row deck_sha256/model_sha256')
    all_ids = sorted({rid for rid, _ in pairs}, key=C.rid_n); nxt = f'run_{C.rid_n(all_ids[-1]) + 1:04d}'
    c10 = len({rid for rid, lab in pairs if lab.startswith('c10_')})
    after = sorted({rid for rid, _ in pairs if C.rid_n(rid) > C.rid_n(C.LAST_PRE)}, key=C.rid_n)
    lab_of = {}
    for rid, lab in pairs: lab_of.setdefault(rid, lab)
    other = [rid for rid in after if lab_of[rid] not in c10_labels and lab_of[rid] not in de_of and lab_of[rid] not in f_of and lab_of[rid] not in s_of]
    g.check(not other, f'RUN_INDEX: every run above {C.LAST_PRE} is S1-06R, a DIAG, D/E, stage F or S4a entry', str(other))
    early = sorted({rid for rid, lab in pairs if lab in s_of and C.rid_n(rid) <= C.rid_n(LAST_F)}, key=C.rid_n)
    g.check(not early, f'RUN_INDEX: no S4a label at or below {LAST_F}', str(early))
    f_started = {}
    for rid in after:
        if lab_of[rid] in f_of: f_started.setdefault(f_of[lab_of[rid]], rid)
    miss = [k for k in FG.ORDER if k not in f_started]; unfin = [f'{f_started[k]} ({k})' for k in FG.ORDER if k in f_started and not fin_f.get(f_started[k])]
    g.check(not miss, 'every stage F entry has started (stage F exhausted before S4a)', f'not started: {miss}' if miss else '')
    g.check(not unfin, 'every started stage F run has a finish row (presence only)', ', '.join(unfin))
    s_ids = [rid for rid in after if rid in rows_s]
    last_f = max([C.rid_n(r) for r in f_started.values()], default=0)
    g.check(all(C.rid_n(r) > last_f for r in s_ids), 'every S4a run id is above the last stage F run id', str(s_ids))
    started = {}
    for rid in s_ids:
        k = s_of[rows_s[rid][0]['label']]
        g.check(k not in started, f'RUN_INDEX: one run id per label ({LABEL[k]})', f'{started.get(k)} and {rid}' if k in started else '')
        started.setdefault(k, rid)
    finished = {}
    for k, rid in started.items():
        first = rows_s[rid][0]; n = first['notes']
        g.check(n.startswith('STARTED') and f'model={C.MODEL_ENV}' in n.split() and first['deck_sha256'] == DECK[k] and first['model_sha256'] == MATERIAL[k],
                f'{rid} ({k}): STARTED-row input columns as pinned (deck_sha256, model_sha256, model note)')
        finished[k] = any(x['exit_code'] != '' for x in rows_s[rid][1:])
    inv = {x['run_id']: x for x in json.loads(C.INVENTORY.read_text())['runs']}
    for k, rid in started.items():
        x = inv.get(rid) or {}
        g.check(x.get('label') == LABEL[k] and x.get('entry') == k and x.get('deck_sha256') == DECK[k] and x.get('model_sha256') == MATERIAL[k]
                and x.get('model_file') == C.MODEL_ENV, f'{rid} ({k}) listed in config/sealed_runs.json with the pinned values (A41 (e), A49 (d))')
    launched = [s_of[rows_s[rid][0]['label']] for rid in s_ids]
    g.check(launched == ORDER[:len(launched)], 'order: STARTED S4a runs == a prefix of the registered order (S4A-02-2p0 ... S4A-15-13p2)',
            ' -> '.join(f'{k} {r}' for k, r in list(zip(launched, s_ids))[-6:]) or 'none')
    unfinished = [f'{started[k]} ({k})' for k in started if not finished[k]]
    todo = [k for k in ORDER if k not in started]
    if unfinished: g.stop(f'started S4a run(s) without a finish row: {unfinished} (a launch in progress, or a runner crash): nothing is invoked; decide by hand')
    plan_rel = PLAN_OF[todo[0]] if todo else None
    nxt_k = [k for k in todo if PLAN_OF[k] == plan_rel] if plan_rel else []

    ms = re.findall(r'^\s*max_launches:\s*(\d+)', C.SOLVER.read_text(), re.M); cap = int(ms[0]) if len(ms) == 1 else -1
    g.check(cap == C.MAX_LAUNCHES == 260, 'config/solver.yaml: exactly one max_launches and it == 260 (D-58 (4): not raised)', f'found {ms}')
    g.check(C.C10_CAP == 200 and rc_cap == 200, 'C10 cap == 200 (gate constant and run_campaign.C10_CAP; D-58 (4): not raised)', f'gate {C.C10_CAP}, runner {rc_cap}')
    g.check(cap > 0 and len(all_ids) + len(nxt_k) <= cap, f'global budget: {len(all_ids)} used + {len(nxt_k)} <= max_launches {cap}')
    g.check(c10 + len(nxt_k) <= 200, f'C10 cap: {c10} used + {len(nxt_k)} <= 200')
    s_left = len(ORDER) - len(started)
    g.check(c10 + s_left + NEED_AFTER_S4A <= 200, f'A49 (h) fit: c10 {c10} + unlaunched S4a {s_left} + never-cut need after S4a {NEED_AFTER_S4A} = '
            f'{c10 + s_left + NEED_AFTER_S4A} <= 200 (six repairs reserved)')
    print(f'[INFO] RUN_INDEX: {len(all_ids)} distinct run ids (max {all_ids[-1]}), c10 {c10}/200; S4a started: {len(started)}/42'
          + (f' (last {launched[-1]} {s_ids[-1]})' if launched else '') + f'; next free id {nxt}', flush=True)

    if g.fails:
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked. Report the failure; a running DeckBuild/ATLAS process is not killed '
              'without the user\'s decision.', flush=True); return 1
    if g.stops:
        print(f'GATE STOP ({len(g.stops)}): a main-session decision is needed; nothing may be invoked.', flush=True); return 3
    if not todo:
        print('NOTHING TO LAUNCH: every S4a entry has started. Do not invoke the S4a route plans again. (Exit 4 is not a pass.)', flush=True); return 4
    cmd = f'& "{C.VENV_PY}" scripts/run_campaign.py {plan_rel}'
    print(f'GATE PASSED. Next plan {plan_rel}: {nxt_k[0]} ({LABEL[nxt_k[0]]}) ... {nxt_k[-1]}, first run id {nxt}; the invocation runs these '
          f'{len(nxt_k)} entr{"y" if len(nxt_k) == 1 else "ies"} in order and stops. Only with the go for THIS launch (the hook asks). '
          + ('Would-be command (check mode, not an instruction)' if check_mode else 'Command (same PowerShell session, package root, IWO_MODEL_FILE as set)')
          + f':\n{cmd}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
