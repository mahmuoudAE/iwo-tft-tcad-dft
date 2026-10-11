"""Offline checks after a campaign launch (NO simulator call; reads a finished run directory, never writes into it).
Implements the parts of design item C11 that the stop rules need, without changing the runner:
  1. activation parser (S0 stop rule, S3 adoption rule): per requested option ACTIVE / NOT_ACTIVE / UNVERIFIED from positive
     evidence only (solver-printed lines after 'go atlas', never echoed input or comments; REGIONAL MODEL FLAGS / MATERIAL
     PARAMETERS / MOBILITY MODEL SUMMARY, the Contacts table, the terminal currents). Each gate-current model is tested on its
     own; a deck with two (QTNLSC + ITAT) needs --gate-control <same deck without oxide TAT>. Overall status
     ACTIVE_AS_REQUESTED (exit 0) / OPTION_NOT_ACTIVE (exit 1) / UNVERIFIED (exit 3: read deckbuild.out by hand before going on);
  2. off-floor metrics of CAMPAIGN_DESIGN 7.1 (floor_ratio, valid points, floor_slope vs the measured slope +- sigma,
     ig_ratio, |I_G(-3 V)|, d_floor_ratio and pointwise drain_share against an optional matched control run);
  3. strip runs: I(0.7 V)/I(0.1 V) from strip_iv.csv.
  python analysis_2026-10-10_campaign/post_run_checks.py results/runs/run_0061_... [--control results/runs/run_00xx_...] [--gate-control results/runs/run_00yy_...]
Output: printed JSON and analysis_2026-10-10_campaign/post_run/<run_id>.json."""
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np

import campaign_tools as ct

OUT = ct.HERE / 'post_run'
FLOORS = {2.0: 4.61e-15, 6.3: 1.53e-13, 13.2: 6.60e-12}   # MEASURED/DERIVED (median over Vg in [-2, -0.5] V)


def solver_lines(text):
    """lines PRINTED BY THE SOLVER: drops everything before 'go atlas' (DeckBuild repeats the deck header comments there
    without the 'ATLAS>' prefix, e.g. run_0040 deckbuild.out lines 3-31), every echoed statement ('ATLAS>' / 'EXTRACT>'
    prefix) and every comment line ('#'). No 'go atlas' line -> nothing is returned (missing evidence, never a pass)."""
    out, started = [], False
    for l in text.splitlines():
        s = l.strip()
        if not started:
            started = s.lower().startswith('go atlas'); continue
        if not s or s.startswith(('ATLAS>', 'EXTRACT>', '#')): continue
        out.append(l)
    return out


def region_materials(text):
    """{region number: (material, type)} from REGIONAL MATERIAL PARAMETERS"""
    lines = text.splitlines()
    for i, l in enumerate(lines):
        if l.startswith('REGIONAL MATERIAL PARAMETERS'):
            reg = lines[i + 1].split(':', 1)[1].split() if ':' in lines[i + 1] else []
            mat = lines[i + 2].split(':', 1)[1].split() if ':' in lines[i + 2] else []
            typ = lines[i + 3].split(':', 1)[1].split() if ':' in lines[i + 3] else []
            return {r: (mat[k] if k < len(mat) else None, typ[k] if k < len(typ) else None) for k, r in enumerate(reg)}
    return {}


def electron_section(mob_lines):
    """the lines of one region's 'Model for Electrons:' block (up to 'Model for Holes:'), or []"""
    try: j = mob_lines.index('Model for Electrons:')
    except ValueError: return []
    out = []
    for k in mob_lines[j + 1:]:
        if k.startswith('Model for Holes'): break
        out.append(k)
    return out


def electron_mu(mob_lines):
    """electron 'mu = value' of one region of REGIONAL MOBILITY MODEL SUMMARY, or None"""
    for k in electron_section(mob_lines):
        m = re.match(r'mu\s*=\s*([-+0-9.eE]+)$', k)
        if m: return float(m.group(1))
    return None


def parse_out(text):
    """model flags {flag: [T/F per region]}, regions [numbers], mobility {region: electron-model text}, contacts {name: workfn}"""
    lines = text.splitlines(); flags, regions, mob, contacts = {}, [], {}, {}
    for i, l in enumerate(lines):
        if l.startswith('REGIONAL MODEL FLAGS'):
            regions = lines[i + 1].split()[1:]
            for k in lines[i + 2:i + 60]:
                if not k.strip() or k.startswith('Gain'): break
                w = re.match(r'^\s(\S+(?: \S+)?)\s+((?:[TF]\s*)+)$', k)
                if w: flags[w.group(1).strip()] = w.group(2).split()
        if l.startswith('REGIONAL MOBILITY MODEL SUMMARY'):
            cur = None
            for k in lines[i + 1:i + 400]:
                m = re.match(r'\s+Region #(\d+):', k)
                if m: cur = m.group(1); mob[cur] = []; continue
                if k.startswith('Contacts:') or k.startswith('ATLAS>'): break
                if cur and k.strip(): mob[cur].append(k.strip())
        if l.startswith('Contacts:'):
            for k in lines[i + 3:i + 30]:
                w = k.split()
                if len(w) < 3 or not re.match(r'^-?[0-9.]+$', w[2]): break
                contacts[w[0]] = float(w[2])
    return flags, regions, mob, contacts


def electron_model(mob_lines):
    try: j = mob_lines.index('Model for Electrons:'); return ' | '.join(mob_lines[j + 1:j + 4])
    except ValueError: return ''


def model_file_of(run_id):
    """model file of a run from its RUN_INDEX STARTED note ('model=...'; V1 when absent), as main() does for the checked run"""
    idx = (ct.PKG / 'results' / 'RUN_INDEX.csv').read_text(errors='replace'); mfm = re.search(re.escape(run_id) + r',.*STARTED.*?model=(\S+)', idx)
    return mfm.group(1) if mfm else 'config/iwo_material_model.yaml'


def normalized_deck(path, drop_tat):
    """solver statements of a device.in (comments dropped); with drop_tat the oxide-TAT additions are removed (the DOPING
    TAT.TRAP line, 'itat.sc.el' and '^tat.poisson' on MODELS), so a QTNLSC+TAT deck can be compared with its control"""
    if not path.is_file(): return None
    out = []
    for l in path.read_text(errors='replace').splitlines():
        s = l.strip()
        if not s or s.startswith('#'): continue
        if drop_tat:
            if re.match(r'doping region=\d+ uniform tat\.trap', s): continue
            if s.startswith('models '): s = re.sub(r'\s+(itat\.sc\.el|\^tat\.poisson)\b', '', s)
        out.append(s)
    return out


def read_ig(run):
    tc = run / 'terminal_currents.csv'
    if not tc.exists(): return None, None
    rows = list(csv.DictReader(tc.open()))
    return np.array([float(r['vg_V']) for r in rows]), np.array([float(r['ig_raw_A']) for r in rows])


def activation(run, ex, out_text, gate_control=None):
    """Per-option evidence, each ACTIVE / NOT_ACTIVE / UNVERIFIED (2026-10-10 review fix: positive identification only).
    Evidence is taken from solver-printed lines (solver_lines: no echoed input, no comments, nothing before 'go atlas'),
    the REGIONAL tables, the Contacts table and the terminal currents. Missing evidence is UNVERIFIED, never a pass.
    Overall: any NOT_ACTIVE -> OPTION_NOT_ACTIVE; else any UNVERIFIED -> UNVERIFIED; else ACTIVE_AS_REQUESTED."""
    m, g, s = ct.configs(ex.get('model_file', ct.V3), ex.get('overrides', []))
    po = s.get('physics_options') or {}; models = s['models'].lower(); t = float(ex['thickness_nm'])
    flags, regions, mob, contacts = parse_out(out_text); mats = region_materials(out_text); sl = solver_lines(out_text)
    ev = {}
    def put(name, state, evidence): ev[name] = {'state': state, 'evidence': evidence}
    # base MODELS flags (REGIONAL MODEL FLAGS, region 1)
    if not flags: put('base MODELS flags', 'UNVERIFIED', 'REGIONAL MODEL FLAGS table not found (run did not reach the model printout)')
    else:
        bad = []
        if flags.get('Fermi-Dirac', ['?'])[0] != ('T' if 'fermi' in models else 'F'): bad.append('Fermi-Dirac')
        if flags.get('SRH', ['?'])[0] != ('T' if re.search(r'\bsrh\b', models) else 'F'): bad.append('SRH')
        if 'trap.tunnel' in models and flags.get('tat(local)', ['?'])[0] != 'T': bad.append('TRAP.TUNNEL -> tat(local)')
        if 'fermi' not in models and flags.get('Boltzmann', ['?'])[0] != 'T': bad.append('Boltzmann')
        put('base MODELS flags', 'NOT_ACTIVE' if bad else 'ACTIVE', f'mismatch: {bad}' if bad else 'Fermi-Dirac / SRH / tat(local) / Boltzmann flags as requested (region 1)')
    # mobility: IGZO.TOKYO must be named in the region-1 electron model; tmun declared
    mm = str((po.get('mobility') or {}).get('model', 'constant')).lower(); em = electron_model(mob.get('1', []))
    if mm == 'igzo_tokyo':
        if not em: put('IGZO.TOKYO', 'UNVERIFIED', 'REGIONAL MOBILITY MODEL SUMMARY (region 1 electrons) missing')
        elif 'Concentration Independent' in em: put('IGZO.TOKYO', 'NOT_ACTIVE', f'region 1 electrons: {em}')
        elif re.search(r'igzo|tokyo', em, re.I): put('IGZO.TOKYO', 'ACTIVE', f'region 1 electrons: {em}')
        else: put('IGZO.TOKYO', 'UNVERIFIED', f'region 1 electrons: {em} (model not named; read by hand)')
    if s.get('tmun') is not None and mm != 'igzo_tokyo':
        el = electron_section(mob.get('1', []))   # electrons only (a hole 'tmu' line must not certify TMUN)
        tl = [z for z in el if re.match(r'tmu\s*=', z)]
        if not tl: put('tmun', 'UNVERIFIED', 'no electron tmu line in REGIONAL MOBILITY MODEL SUMMARY (region 1)')
        else:
            def num(z):
                try: return float(z.split('=', 1)[1])
                except ValueError: return None
            okt = all(num(z) is not None and abs(num(z) - float(s['tmun'])) <= 1e-9 for z in tl)   # numeric, not text
            put('tmun', 'ACTIVE' if okt else 'NOT_ACTIVE', f'region 1 electron tmu lines: {tl[:2]}')
    # Schottky: the Contacts table must show the requested work function chi(t) + phi_B on source and drain
    sc = po.get('schottky_sd') or {}
    if ct.bd.on(sc.get('enabled')):
        wf = ct.bd.material_at(m, t)['chi_eV'] + float(sc.get('barrier_eV', 0.5))
        got = [contacts.get(n) for n in ('source', 'drain')]
        if any(x is None for x in got): put('Schottky S/D', 'UNVERIFIED', f'Contacts table incomplete: {contacts}')
        elif all(abs(x - wf) <= 2e-3 for x in got): put('Schottky S/D', 'ACTIVE', f'source/drain work fn {got} eV = chi(t) + phi_B = {wf:.4f} eV')
        elif all(abs(x) < 1e-9 for x in got): put('Schottky S/D', 'NOT_ACTIVE', f'source/drain work fn {got} (Ohmic)')
        else: put('Schottky S/D', 'UNVERIFIED', f'source/drain work fn {got} vs requested {wf:.4f} eV')
    # BQP: a solver-printed (not echoed, not comment, not header) line naming BQP / Bohm; a warning naming it -> NOT_ACTIVE
    if str((po.get('quantum') or {}).get('model', 'none')).lower() == 'bqp':
        hits = [l.strip() for l in sl if re.search(r'\bbqp\b|bohm', l, re.I)]
        warn = [h for h in hits if re.search(r'warn|error|ignor|not\s+(?:used|active|supported)', h, re.I)]
        if warn: put('BQP', 'NOT_ACTIVE', warn[:3])
        elif hits: put('BQP', 'ACTIVE', hits[:3])
        else: put('BQP', 'UNVERIFIED', 'no solver-printed line names BQP/Bohm (the activation string of this build is not documented: read deckbuild.out by hand)')
    # in-solver strip: regions 8 and 9 must be IWO semiconductor regions carrying the scaled MUN
    so = po.get('strip') or {}
    if str(so.get('mode', 'none')).lower() == 'in_solver':
        mun = ct.bd.material_at(m, t)['mu0'] * float(so['wl_par_per_um']) * float(so['L_s_um']); bad, unv = [], []
        for r in ('8', '9'):
            mt = mats.get(r)
            if mt is None: unv.append(f'region {r} not in REGIONAL MATERIAL PARAMETERS'); continue
            if mt[0] != 'IWO' or not str(mt[1]).startswith('semicond'): bad.append(f'region {r} is {mt}'); continue
            mu = electron_mu(mob.get(r, []))
            if mu is None: unv.append(f'region {r}: electron mu not in the mobility summary')
            elif abs(mu / mun - 1) > 1e-3: bad.append(f'region {r}: mu {mu} vs requested {mun:.6g}')
        put('in-solver strip', 'NOT_ACTIVE' if bad else 'UNVERIFIED' if unv else 'ACTIVE', bad + unv or f'regions 8/9 IWO semicond., electron mu = {mun:.6g}')
    # gate-current models, each tested on its own: I_G is exactly 0 in all 51 earlier runs without a gate-current model
    gt = po.get('gate_tunnelling') or {}; ot = po.get('oxide_tat') or {}
    gm = ([str(gt.get('model', 'qtnlsc')).upper()] if ct.bd.on(gt.get('enabled')) else []) + (['ITAT.SC.EL'] if ct.bd.on(ot.get('enabled')) else [])
    if gm:
        vg, ig = read_ig(run)
        if ig is None:
            for k in gm: put(k, 'UNVERIFIED', 'no terminal_currents.csv')
        elif len(gm) == 1:
            nz = int(np.sum(ig != 0)); e_ = f'I_G nonzero at {nz}/{len(ig)} points, max |I_G| {np.max(np.abs(ig)):.3g} A (only gate-current model in this deck)'
            if gm[0] == 'FNORD': e_ += f'; ifnvg.dat {"present" if (run / "ifnvg.dat").exists() else "absent"}'
            put(gm[0], 'ACTIVE' if nz else 'NOT_ACTIVE', e_)
        else:   # two gate-current models in one deck (S2-12/13: QTNLSC + ITAT): needs the matched deck without ITAT
            other = gm[0]
            if gate_control is None:
                put(other, 'UNVERIFIED', 'two gate-current models in one deck: pass --gate-control <run without oxide TAT> (S2-04 for S2-12, S2-06 for S2-13)')
                put('ITAT.SC.EL', 'UNVERIFIED', 'needs --gate-control (see above)')
            else:
                cex = json.loads((gate_control / 'execution.json').read_text()); rov, cov = set(ex.get('overrides', [])), set(cex.get('overrides', []))
                extra = rov - cov; why = []
                if (cov - rov) or not extra or not all(o.startswith('solver.physics_options.oxide_tat.') for o in extra):
                    why.append(f'override sets differ beyond oxide_tat.*: {sorted((cov - rov) | extra)[:4]}')
                if abs(float(cex.get('thickness_nm', -1)) - t) > 1e-9: why.append('different thickness')
                mr, mc = run / 'material_model_used.json', gate_control / 'material_model_used.json'
                if not (mr.is_file() and mc.is_file() and mr.read_text() == mc.read_text()): why.append('material_model_used.json differs or is missing')
                if model_file_of(cex['run_id']) != ex.get('model_file'): why.append('different model file')
                _, _, sc_ = ct.configs(model_file_of(cex['run_id']), cex.get('overrides', [])); pc_ = sc_.get('physics_options') or {}
                if ct.bd.on((pc_.get('oxide_tat') or {}).get('enabled')): why.append('oxide TAT is ON in the control')
                if (pc_.get('gate_tunnelling') or {}) != gt: why.append('gate_tunnelling settings differ')
                nr_, nc_ = normalized_deck(run / 'device.in', True), normalized_deck(gate_control / 'device.in', False)
                if nr_ is None or nc_ is None or nr_ != nc_:
                    why.append('the solver statements differ beyond the oxide-TAT lines (device.in)')
                cv, cig = read_ig(gate_control)
                if cig is None or not np.all(np.isfinite(cig)) or cv.min() > vg.min() + 1e-9 or cv.max() < vg.max() - 1e-9:
                    why.append('control currents missing, non-finite or not covering the run gate range')
                if why:
                    put(other, 'UNVERIFIED', f'--gate-control {cex.get("run_id")} is not the same deck without oxide TAT: {why}')
                    put('ITAT.SC.EL', 'UNVERIFIED', 'control mismatch (see above)')
                else:
                    ci = np.interp(vg, cv, cig); d = np.abs(ig - ci)
                    thr = max(1e-20, 1e-3 * float(np.max(np.abs(ci))))
                    put(other, 'ACTIVE' if np.any(cig != 0) else 'NOT_ACTIVE', f'from control {cex["run_id"]} (same {other} lines, no TAT): I_G nonzero at {int(np.sum(cig != 0))}/{len(cig)} points')
                    put('ITAT.SC.EL', 'ACTIVE' if np.any(d > thr) else 'NOT_ACTIVE', f'max |I_G - I_G,control| {np.max(d):.3g} A vs threshold {thr:.3g} A')
    states = [v['state'] for v in ev.values()]
    status = 'OPTION_NOT_ACTIVE' if 'NOT_ACTIVE' in states else 'UNVERIFIED' if 'UNVERIFIED' in states else 'ACTIVE_AS_REQUESTED'
    return {'status': status, 'evidence': ev, 'regions': regions, 'region_materials': mats, 'contacts': contacts, 'electron_mobility_r1': em,
            'missing': [f'{k}: {v["state"]}' for k, v in ev.items() if v['state'] != 'ACTIVE']}


def slope(v, y):
    A = np.vstack([v, np.ones_like(v)]).T; c, r, *_ = np.linalg.lstsq(A, y, rcond=None)
    s2 = float(r[0]) / max(len(v) - 2, 1) if len(r) else 0.0; se = np.sqrt(s2 / max(np.sum((v - v.mean()) ** 2), 1e-30))
    return float(c[0]), float(se)


def floor_metrics(run, t, control=None):
    rows = list(csv.DictReader((run / 'terminal_currents.csv').open())); r = {}
    vg = np.array([float(x['vg_V']) for x in rows]); idv = np.array([float(x['id_A_per_um']) for x in rows]); ig = np.array([float(x['ig_raw_A']) for x in rows])
    fl = FLOORS[t]; w = (vg >= -2 - 1e-9) & (vg <= -0.5 + 1e-9); kcl = max(1e-17, 0.1 * fl)
    valid = w & (idv > kcl); r['valid_fraction'] = float(valid.sum() / max(w.sum(), 1)); r['sign_reversals_vg'] = [float(v) for v in vg[w & (idv < 0)]]
    if valid.any():
        r['floor_ratio_dec'] = float(np.median(np.log10(idv[valid] / fl)))
        if valid.sum() >= 3: r['floor_slope_dec_per_V'], r['floor_slope_se'] = slope(vg[valid], np.log10(idv[valid]))
    mv, mi = ct.bd.read_meas(t); mw = (mv >= -2 - 1e-9) & (mv <= -0.5 + 1e-9) & (mi > 0)
    r['measured_slope_dec_per_V'], r['measured_slope_se'] = slope(mv[mw], np.log10(mi[mw]))
    r['slope_limit_dec_per_V'] = 2 * abs(r['measured_slope_dec_per_V']) + 2 * r['measured_slope_se']
    igw = np.abs(ig[w]); r['ig_ratio_dec'] = float(np.median(np.log10(igw[igw > 0] / fl))) if np.any(igw > 0) else None   # None: I_G exactly 0 (no tunnelling model)
    r['ig_nonzero_fraction'] = float(np.mean(igw > 0)) if igw.size else 0.0; r['abs_IG_at_m3V_A'] = float(abs(ig[np.argmin(abs(vg + 3))]))
    if control is not None:
        crow = list(csv.DictReader((control / 'terminal_currents.csv').open())); cv = np.array([float(x['vg_V']) for x in crow]); ci = np.interp(vg, cv, [float(x['id_A_per_um']) for x in crow])
        d = idv - ci; dv = w & (d > kcl)
        r['d_floor_ratio_dec'] = float(np.median(np.log10(d[dv] / fl))) if dv.any() else None; r['d_valid_fraction'] = float(dv.sum() / max(w.sum(), 1))
        share = w & (np.abs(ig) > kcl); r['drain_share_pointwise'] = {f'{v:g}': float(dd / abs(gg)) for v, dd, gg in zip(vg[share], d[share], ig[share])}
    lim = r['slope_limit_dec_per_V']
    r['verdict_inputs'] = {'valid_ge_80pct': r['valid_fraction'] >= 0.8, 'slope_ok': ('floor_slope_dec_per_V' in r and abs(r['floor_slope_dec_per_V']) <= lim),
                           'd_floor_within_0p5dec': (r.get('d_floor_ratio_dec') is not None and abs(r['d_floor_ratio_dec']) <= 0.5) if control is not None else None}
    return r


def main(argv):
    if not argv: print(__doc__); return 2
    run = Path(argv[0]); run = run if run.is_absolute() else ct.PKG / run
    def arg(flag):
        if flag not in argv: return None
        c = Path(argv[argv.index(flag) + 1]); return c if c.is_absolute() else ct.PKG / c
    control, gate_control = arg('--control'), arg('--gate-control')
    ex = json.loads((run / 'execution.json').read_text()); t = float(ex['thickness_nm'])
    ex['model_file'] = model_file_of(ex['run_id'])
    out = (run / 'deckbuild.out').read_text(errors='replace') if (run / 'deckbuild.out').exists() else ''
    res = {'run_id': ex['run_id'], 'status_runner': ex.get('status'), 'model_file': ex['model_file'], 'activation': activation(run, ex, out, gate_control)}
    if ex.get('mode') == 'strip':
        res['strip'] = ex.get('strip')
    elif (run / 'terminal_currents.csv').exists() and t in FLOORS:
        res['floor_metrics'] = floor_metrics(run, t, control)
        ov = ' '.join(ex.get('overrides', []))
        if 'oxide_tat.enabled=1' in ov and 'oxide_tat.poisson=0' not in ov:
            res['floor_metrics']['drain_share_note'] = ('oxide TAT with trap charge in Poisson (TAT.POISSON default): d_floor_ratio and drain_share mix the '
                                                        'electrostatic shift of the charged oxide with collected leakage; report them only as the combined response of a charged oxide')
    OUT.mkdir(exist_ok=True); (OUT / f'{ex["run_id"]}.json').write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1)); st = res['activation']['status']
    return 0 if st == 'ACTIVE_AS_REQUESTED' else 1 if st == 'OPTION_NOT_ACTIVE' else 3


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
