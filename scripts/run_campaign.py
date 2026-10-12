#!/usr/bin/env python3
"""ATLAS campaign from a JSON plan (2026-09-25 hypothesis / convergence / sensitivity / prediction study).

  python scripts/run_campaign.py config/campaign_A_6p3_hypotheses.json               sequential
  python scripts/run_campaign.py config/campaign_A_6p3_hypotheses.json --workers 4   4 ATLAS runs in parallel
  (parallel added 2026-09-28: each run has its own directory; run IDs, the launch budget and RUN_INDEX writes are
   locked in run_atlas.reserve/append; entries using a {mu:key} placeholder start only after the run producing it)

Plan: {"campaign": name, "purpose": text, "runs": [entry, ...]}; entry keys:
  id, thickness, label, overrides [..], mode "transfer" (default) | "output" | "strip" (2026-10-10: ungated two-terminal
  strip deck, run_atlas.execute_strip), output_vgs [..], vd_segments [[end, step], ..],
  timeout (s), purpose (text), mu_used + recal_key (optional: after the run, mu_band is rescaled EXACTLY by
  Ion_meas / Ion_sim - Id is linear in a constant mobility, tables/SENSITIVITY_RESULTS.md mu_band pairs - and stored as
  the placeholder {mu:<recal_key>} for later entries of the same campaign).
Every launch goes through run_atlas.execute / execute_output (same deck generator, validation, RUN_INDEX row). The
summary results/campaigns/<plan stem>.json is rewritten after every launch; a failed launch is recorded and the
campaign continues; the campaign stops at the launch budget.
C10 plans (2026-10-10 review fix; file stem campaign_C10_* or campaign "C10..."): --workers must be 1; at most 200 C10 launches
(labels c10_* in RUN_INDEX, failed ones included); an entry whose label already has a RUN_INDEX row is not launched again
(earlier success reused, earlier failure reported; --retry ID[,ID] to spend a new launch on purpose).
A plan with "runnable": false (templates; plans held outside the frozen register route, 2026-10-11) is refused before any launch.
Executable stop gates (2026-10-13, opt-in; scripts/campaign_gates.py): a plan with a "gates" list evaluates each gate with the frozen
scorer after its checkpoint entry and before the plan proceeds; a FIRED gate (or an UNRESOLVED one declared on_unresolved "stop") stops
the plan before the next launch (exit code 3) and holds until --ack-gate GATE_ID[,ID] --ack-audit AUDIT_FILE (the completed audit, naming
the gate and decision ids). Decisions are bound to the gate declaration, scorer and input/evidence hashes. Gate output is FIRED /
NOT_FIRED / UNRESOLVED plus ids and hashes only.
State-only surface (2026-10-13, opt-in; scripts/campaign_sealed.py): a plan with "state_only" prints and writes state only (console,
results/campaigns summary, RUN_INDEX finish notes); the full record goes to a sealed sidecar under results/sealed/.
A plan with neither key runs exactly as before (this module does not even import campaign_gates / campaign_sealed for it).
"""
from __future__ import annotations
import contextlib, json, sys, time, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_atlas import execute, execute_output, execute_strip, ROOT

def fill(overrides, ph):
    out = []
    for o in overrides:
        for k, v in ph.items(): o = o.replace('{mu:' + k + '}', f'{v:.6g}')
        if '{mu:' in o: raise RuntimeError(f'unresolved placeholder in {o}')
        out.append(o)
    return out

def summarize(dest):
    ex = json.loads((Path(dest) / 'execution.json').read_text()); s = {'status': ex.get('status'), 'elapsed_s': round(ex.get('elapsed_s', 0), 1)}
    if 'fit_metrics' in ex:
        fm = ex['fit_metrics']; rg = fm['regions']
        s.update({'active_rmse_dec': rg['active'].get('rmse_log10'), 'sub_rmse_dec': rg['subthreshold'].get('rmse_log10'), 'on_rmse_dec': rg['on'].get('rmse_log10'),
                  'Id3V_err_pct': fm['on_error_3V_percent'], 'sim': ex['device_metrics_sim'], 'exp': ex['device_metrics_exp']})
    if 'validation' in ex: s['max_kcl_A'] = ex['validation'].get('max_kcl_abs_A')
    if 'strip' in ex: s['strip'] = ex['strip']   # 2026-10-10 strip mode
    return s

def _sealed_io(log):
    import campaign_sealed as cs
    return cs.sealed_io(log)

def run_entry(e, res, lock, sealed_log=None):
    rec = {'id': e['id'], 'thickness': e['thickness'], 'label': e['label'], 'purpose': e.get('purpose', ''), 'mode': e.get('mode', 'transfer')}
    t0 = time.time()
    try:
        with lock: ov = fill(e.get('overrides', []), res['placeholders'])
        rec['overrides'] = ov
        kw = {'seal_notes': True} if sealed_log else {}   # 2026-10-13 state-only plans: status-only RUN_INDEX notes, launch output sealed
        with (_sealed_io(sealed_log) if sealed_log else contextlib.nullcontext()):
            if e.get('mode') == 'output':
                dest = execute_output(float(e['thickness']), e['label'], ov, e['output_vgs'], [tuple(x) for x in e.get('vd_segments', [[0.5, 0.05], [3.0, 0.1]])], e.get('timeout'), **kw)
            elif e.get('mode') == 'strip':   # 2026-10-10: ungated two-terminal strip deck (run_atlas.execute_strip)
                if 'vd_segments' in e: raise RuntimeError('strip mode takes the drain steps from physics_options.strip.vd_segments, not from the entry')
                dest = execute_strip(float(e['thickness']), e['label'], ov, e.get('timeout'), **kw)
            else:
                dest = execute(float(e['thickness']), e['label'], ov, timeout=e.get('timeout'), **kw)
        rec['run_dir'] = str(Path(dest).relative_to(ROOT)).replace('\\', '/'); rec['run_id'] = Path(dest).name[:8]; rec.update(summarize(dest))
        if e.get('recal_key') and 'sim' in rec:
            mu_new = float(e['mu_used']) * rec['exp']['Ion_A_per_um'] / rec['sim']['Ion_A_per_um']
            with lock: res['placeholders'][e['recal_key']] = mu_new
            rec['mu_recalibrated'] = mu_new
    except Exception as ex:
        rec['error'] = f'{type(ex).__name__}: {ex}'; rec['traceback'] = traceback.format_exc()[-1500:]
    rec['wall_s'] = round(time.time() - t0, 1)
    return rec

def ready(e, res):
    """an entry can start when every {mu:key} placeholder it uses has been produced by an earlier run"""
    return all('{mu:' + k + '}' not in o or k in res['placeholders'] for o in e.get('overrides', []) for k in
               [p.split('}')[0] for p in o.split('{mu:')[1:]] or [''])

# ---- 2026-10-10 C10 campaign guards (review fix): the user approved 200 launches, sequential. Every reserved run ID counts,
# failed or not. config/solver.yaml max_launches 260 (= 60 used before C10 + 200) is the hard global cap in run_atlas.reserve;
# the guards below add, for C10 plans only: workers must be 1; a C10 label counter capped at 200; and an entry whose label
# already has a RUN_INDEX row (launched by THIS or ANY other C10 plan, e.g. MIN10 vs the stage plans) is never launched again
# automatically: a successful earlier launch is reused (summary copied), a failed one is reported. --retry ID[,ID] spends a
# new launch on purpose (reserve).
C10_CAP = 200
SUCCESS = ('REAL_ATLAS_SCORED', 'REAL_ATLAS_STRIP', 'REAL_ATLAS_PREDICTION', 'REAL_ATLAS_PARTIAL_SWEEP')

def is_c10(plan, plan_path): return Path(plan_path).stem.startswith('campaign_C10') or str(plan.get('campaign', '')).upper().startswith('C10')

def _configs(ov):
    from build_iwo_decks import load_configs, set_dotted
    m, g, s = load_configs()
    for o in ov:
        k, v = o.split('=', 1)
        if k.startswith('solver.'): set_dotted(s, k[7:], v)
        elif k.startswith('geometry.'): set_dotted(g, k[9:], v)
        else: set_dotted(m, k, v)
    return m, g, s

def current_material_text(ov):
    """material_model_used.json text that run_atlas.execute* would write now for these overrides (same routing, same dump)"""
    return json.dumps(_configs(ov)[0], indent=2, default=float)

def current_deck_text(e, ov):
    """device.in that run_atlas.execute (default transfer path: stepped segments and structure from the configs) or
    execute_strip would write now for this entry; None for any other mode (then an earlier launch is never reused)"""
    import numpy as np
    from build_iwo_decks import build_deck, read_meas
    m, g, s = _configs(ov); t = float(e['thickness']); full = str(g.get('structure', 'reduced')).lower() == 'full'; vg, meas = read_meas(t)
    if e.get('mode') == 'strip': return build_deck(t, m, g, s, meas=(vg, meas), full=full, strip=True)[0]
    if e.get('mode', 'transfer') != 'transfer' or str(s.get('sweep', {}).get('mode', 'pointwise')) != 'stepped': return None
    segs = [tuple(x) for x in s['sweep']['segments']]; pts = [float(vg[0])]; a = float(vg[0])
    for end, st in segs:
        n = int(round((end - a) / st)); pts += [round(a + i * st, 6) for i in range(1, n + 1)]; a = float(end)
    targets = np.array(sorted(set(pts) & set(np.round(vg, 6).tolist())))
    return build_deck(t, m, g, s, meas=(vg, meas), targets=targets, full=full, segments=segs)[0]

def c10_launches(idx_rows):return len({r['run_id'] for r in idx_rows if str(r.get('label', '')).startswith('c10_')})

def earlier_launch(e, idx_rows, res):
    """C10: record for an entry whose label already has a RUN_INDEX row (no new launch), or None"""
    rids = sorted({r['run_id'] for r in idx_rows if r.get('label') == e['label']})
    if not rids: return None
    rid = rids[-1]; last = [r for r in idx_rows if r['run_id'] == rid][-1]
    rec = {'id': e['id'], 'thickness': e['thickness'], 'label': e['label'], 'purpose': e.get('purpose', ''), 'mode': e.get('mode', 'transfer'),
           'not_relaunched': True, 'earlier_run_ids': rids, 'run_index_note': last.get('notes', '')}
    dest = ROOT / last.get('output_dir', ''); exj = dest / 'execution.json'
    ex = json.loads(exj.read_text()) if last.get('output_dir') and exj.is_file() else {}
    ov = fill(e.get('overrides', []), res['placeholders'])
    if ex:   # the earlier launch must be the same entry: overrides, thickness, mode and the material model actually used
        why = []
        if list(ex.get('overrides', [])) != ov: why.append('overrides')
        if abs(float(ex.get('thickness_nm', -1)) - float(e['thickness'])) > 1e-9: why.append('thickness')
        if {'strip': 'strip', 'output_prediction': 'output'}.get(ex.get('mode'), 'transfer') != e.get('mode', 'transfer'): why.append('mode')
        mu = dest / 'material_model_used.json'
        if not mu.is_file() or mu.read_text() != current_material_text(ov): why.append('material model (model file / config changed since that launch)')
        dk = dest / 'device.in'
        if not why:
            try: same = dk.is_file() and dk.read_text() == current_deck_text(e, ov)
            except Exception as err: same = False; why.append(f'deck rebuild failed ({type(err).__name__})')
            if not same and not why: why.append('deck (device.in differs from the deck the current generator and configs give)')
        if why:
            rec['error'] = (f'label {e["label"]} was launched as {rid} with DIFFERENT {", ".join(why)}; not launched and not reused '
                            f'(resolve by hand; --retry {e["id"]} spends a new launch)'); return rec
    if ex.get('status') in SUCCESS:
        rec['run_dir'] = str(dest.relative_to(ROOT)).replace('\\', '/'); rec['run_id'] = rid; rec.update(summarize(dest)); rec['reused_earlier_launch'] = True
    else:
        rec['error'] = (f'already launched as {rid} (status {ex.get("status", "unknown: no execution.json")}); not re-launched '
                        f'(C10: every launch counts). Use --retry {e["id"]} to spend a new launch on it.')
    return rec

def main():
    """python run_campaign.py PLAN.json [--workers N] [--retry ID[,ID...]] [--ack-gate GATE_ID[,ID] --ack-audit AUDIT_FILE]
    (N parallel ATLAS processes, default 1 = sequential; C10, gated and state-only plans: N must be 1, --retry re-launches named entries)"""
    import threading
    from concurrent.futures import ThreadPoolExecutor, FIRST_COMPLETED, wait
    from run_atlas import rows as index_rows
    args = sys.argv[1:]; workers = 1; retry = set(); acks = set()
    if '--workers' in args: i = args.index('--workers'); workers = int(args[i + 1]); del args[i:i + 2]
    if '--retry' in args: i = args.index('--retry'); retry = {x.strip() for x in args[i + 1].split(',') if x.strip()}; del args[i:i + 2]
    if '--ack-gate' in args: i = args.index('--ack-gate'); acks = {x.strip() for x in args[i + 1].split(',') if x.strip()}; del args[i:i + 2]
    audit = None
    if '--ack-audit' in args: i = args.index('--ack-audit'); audit = args[i + 1]; del args[i:i + 2]
    plan_path = Path(args[0]); plan = json.loads(plan_path.read_text()); c10 = is_c10(plan, plan_path)
    if plan.get('runnable') is False:   # 2026-10-11 review: held plans (outside the frozen register route) and templates are never launched
        sys.exit(f'{plan_path.name}: runnable=false, nothing launched ({plan.get("not_runnable_reason") or "template: unresolved tokens"})')
    if c10 and workers != 1: sys.exit(f'C10 plans are sequential only (user approval: 200 sequential launches); got --workers {workers}')
    gates = plan.get('gates'); gate_stop = None   # 2026-10-13 opt-in executable stop gates (scripts/campaign_gates.py); None -> unchanged runner
    if gates is not None or acks or audit:
        import campaign_gates as cg
        bad = cg.validate(plan, workers) if gates is not None else ['--ack-gate / --ack-audit given for a plan without gates']
        if audit and not acks: bad.append('--ack-audit needs --ack-gate')
        if bad: sys.exit(f'{plan_path.name}: gates refused, nothing launched: ' + '; '.join(bad))
    so = plan.get('state_only'); slog = None   # 2026-10-13 opt-in state-only surface (scripts/campaign_sealed.py; Codex blocker 3 / D7)
    if so is not None:
        import campaign_sealed as cs
        bad = cs.validate(plan, workers)
        if bad: sys.exit(f'{plan_path.name}: state_only refused, nothing launched: ' + '; '.join(bad))
        full, slog = cs.paths(ROOT, plan_path.stem, so)
    out_dir = ROOT / 'results' / 'campaigns'; out_dir.mkdir(parents=True, exist_ok=True); out = out_dir / f'{plan_path.stem}.json'
    res = {'campaign': plan.get('campaign', plan_path.stem), 'purpose': plan.get('purpose', ''), 'plan_file': str(plan_path), 'placeholders': {}, 'runs': []}
    if so is not None and full.exists(): res = json.loads(full.read_text())   # state-only: the full record lives in the sealed sidecar
    elif out.exists():   # resume: keep finished entries, skip them
        res = json.loads(out.read_text())
    def save():   # the default writes exactly as before; state-only: full record -> sealed sidecar, state projection -> out
        if so is None: out.write_text(json.dumps(res, indent=1, default=float))
        else: cs.save(res, out, full, ROOT)
    def line(r, keys):
        return cs.console(r) if so is not None else json.dumps({k: r.get(k) for k in keys})
    if gates:   # a recorded gate stop holds until acknowledged with a cited audit: nothing is launched or reused before that
        res.setdefault('gates', []); hold, probs = cg.held(plan, res, acks, audit, save, out, ROOT, index_rows)
        for m in probs: print(m, flush=True)
        if hold:
            print(f'STOP: gate {hold[0]["gate"]} [{hold[0]["rule_id"]}] decision {hold[0]["decision_id"]} recorded {hold[0]["state"]} at '
                  f'{hold[0]["evaluated_utc"]}; nothing launched. After the audit, resume with {cg.resume_hint(hold[0])}', flush=True); sys.exit(3)
    done = {r['id'] for r in res['runs'] if r.get('run_dir')} - retry   # --retry also re-launches an entry finished in this plan
    todo = [e for e in plan['runs'] if e['id'] not in done]; lock = threading.Lock(); running = {}; stop = False
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while (todo and not stop) or running:
            for e in [e for e in todo if ready(e, res)] if not stop else []:
                if len(running) >= workers: break
                if gates:   # 2026-10-13: pending gates are evaluated before the plan proceeds to its next entry (launch or reuse)
                    gate_stop = cg.check(plan, res, save, out, ROOT, index_rows)
                    if gate_stop: stop = True; break
                if c10:   # sequential (workers == 1), so the RUN_INDEX read here sees every earlier launch
                    idx = index_rows(); prev = earlier_launch(e, idx, res) if e['id'] not in retry else None
                    if prev is not None:
                        todo.remove(e); res['runs'] = [r for r in res['runs'] if not (r['id'] == e['id'] and not r.get('run_dir'))] + [prev]
                        save()
                        print(line(prev, ('id', 'run_id', 'status', 'reused_earlier_launch', 'error')), flush=True); continue
                    if c10_launches(idx) >= C10_CAP: stop = True; print(f'STOP: C10 launch cap {C10_CAP} reached (labels c10_* in RUN_INDEX)'); break
                todo.remove(e); running[pool.submit(run_entry, e, res, lock, *([slog] if slog else []))] = e
            if not running:
                if todo and not stop: print('STOP: remaining entries wait for placeholders that no run produced')
                if todo: break
                continue
            fin, _ = wait(list(running), return_when=FIRST_COMPLETED)
            for f in fin:
                running.pop(f); rec = f.result()
                with lock:
                    if rec['id'] in retry:   # a retried entry: its latest attempt replaces earlier records (a failed retry is not 'done')
                        rec['earlier_records'] = [r for r in res['runs'] if r['id'] == rec['id']]; res['runs'] = [r for r in res['runs'] if r['id'] != rec['id']]
                    res['runs'].append(rec); save()
                print(line(rec, ('id', 'run_id', 'status', 'active_rmse_dec', 'Id3V_err_pct', 'error', 'wall_s')), flush=True)
                if 'launch budget' in rec.get('error', ''): stop = True; print('STOP: budget')
    if gates and gate_stop is None: gate_stop = cg.check(plan, res, save, out, ROOT, index_rows)   # gates on the plan's last record
    if gates and gate_stop:
        print(f'STOP: gate {gate_stop["gate"]} [{gate_stop["rule_id"]}] {gate_stop["state"]} (decision {gate_stop["decision_id"]}); nothing further '
              f'launched. After the audit, resume with {cg.resume_hint(gate_stop)}', flush=True)
        print('CAMPAIGN STOPPED BY GATE', out); sys.exit(3)
    print('CAMPAIGN DONE', out)

if __name__ == '__main__': main()
