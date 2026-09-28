#!/usr/bin/env python3
"""ATLAS campaign from a JSON plan (2026-09-25 hypothesis / convergence / sensitivity / prediction study).

  python scripts/run_campaign.py config/campaign_A_6p3_hypotheses.json               sequential
  python scripts/run_campaign.py config/campaign_A_6p3_hypotheses.json --workers 4   4 ATLAS runs in parallel
  (parallel added 2026-09-28: each run has its own directory; run IDs, the launch budget and RUN_INDEX writes are
   locked in run_atlas.reserve/append; entries using a {mu:key} placeholder start only after the run producing it)

Plan: {"campaign": name, "purpose": text, "runs": [entry, ...]}; entry keys:
  id, thickness, label, overrides [..], mode "transfer" (default) | "output", output_vgs [..], vd_segments [[end, step], ..],
  timeout (s), purpose (text), mu_used + recal_key (optional: after the run, mu_band is rescaled EXACTLY by
  Ion_meas / Ion_sim - Id is linear in a constant mobility, tables/SENSITIVITY_RESULTS.md mu_band pairs - and stored as
  the placeholder {mu:<recal_key>} for later entries of the same campaign).
Every launch goes through run_atlas.execute / execute_output (same deck generator, validation, RUN_INDEX row). The
summary results/campaigns/<plan stem>.json is rewritten after every launch; a failed launch is recorded and the
campaign continues; the campaign stops at the launch budget.
"""
from __future__ import annotations
import json, sys, time, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_atlas import execute, execute_output, ROOT

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
    return s

def run_entry(e, res, lock):
    rec = {'id': e['id'], 'thickness': e['thickness'], 'label': e['label'], 'purpose': e.get('purpose', ''), 'mode': e.get('mode', 'transfer')}
    t0 = time.time()
    try:
        with lock: ov = fill(e.get('overrides', []), res['placeholders'])
        rec['overrides'] = ov
        if e.get('mode') == 'output':
            dest = execute_output(float(e['thickness']), e['label'], ov, e['output_vgs'], [tuple(x) for x in e.get('vd_segments', [[0.5, 0.05], [3.0, 0.1]])], e.get('timeout'))
        else:
            dest = execute(float(e['thickness']), e['label'], ov, timeout=e.get('timeout'))
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

def main():
    """python run_campaign.py PLAN.json [--workers N]   (N parallel ATLAS processes, default 1 = sequential)"""
    import threading
    from concurrent.futures import ThreadPoolExecutor, FIRST_COMPLETED, wait
    args = sys.argv[1:]; workers = 1
    if '--workers' in args: i = args.index('--workers'); workers = int(args[i + 1]); del args[i:i + 2]
    plan_path = Path(args[0]); plan = json.loads(plan_path.read_text())
    out_dir = ROOT / 'results' / 'campaigns'; out_dir.mkdir(parents=True, exist_ok=True); out = out_dir / f'{plan_path.stem}.json'
    res = {'campaign': plan.get('campaign', plan_path.stem), 'purpose': plan.get('purpose', ''), 'plan_file': str(plan_path), 'placeholders': {}, 'runs': []}
    if out.exists():   # resume: keep finished entries, skip them
        res = json.loads(out.read_text())
    done = {r['id'] for r in res['runs'] if r.get('run_dir')}
    todo = [e for e in plan['runs'] if e['id'] not in done]; lock = threading.Lock(); running = {}; stop = False
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while (todo and not stop) or running:
            for e in [e for e in todo if ready(e, res)][:max(0, workers - len(running))] if not stop else []:
                todo.remove(e); running[pool.submit(run_entry, e, res, lock)] = e
            if not running:
                if todo: print('STOP: remaining entries wait for placeholders that no run produced'); break
                continue
            fin, _ = wait(list(running), return_when=FIRST_COMPLETED)
            for f in fin:
                running.pop(f); rec = f.result()
                with lock:
                    res['runs'].append(rec); out.write_text(json.dumps(res, indent=1, default=float))
                print(json.dumps({k: rec.get(k) for k in ('id', 'run_id', 'status', 'active_rmse_dec', 'Id3V_err_pct', 'error', 'wall_s')}), flush=True)
                if 'launch budget' in rec.get('error', ''): stop = True; print('STOP: budget')
    print('CAMPAIGN DONE', out)

if __name__ == '__main__': main()
