"""Branch D read-out: tunnelling-mesh branch (register A45 (c) = PA-4 (b); script registered by A47, 2026-10-15; no Codex review, D-63).

NO launch. Reads two finished, UNSEALED run directories (the branch run and its partner) and writes one JSON (analysis_2026-10-10_campaign/
branch_d/). It is not the frozen scorer (score_register.py c0f28bb9 stays unchanged) and gives no H-C verdict.

    python -I -B analysis_2026-10-10_campaign/branch_d_readout.py KIND RUN_DIR PARTNER_DIR
        KIND  T0r  (c10_s0_02_tolx001_2p0 against run_0067)   tolerance replay
              T2a  (c10_s0_02_qtm2_2p0 against run_0066)      QT point spacing 0.5 -> 0.25 nm
              T2b  (c10_s0_02_qtm3_2p0 against T2a, and against run_0066 as a second call)   QT slice spacing 0.2 -> 0.1 um
    python -I -B analysis_2026-10-10_campaign/branch_d_readout.py selftest     (synthetic directories only)

Registered rule (A45 (c), PA-4 (b), Codex 2026-10-14T19:02Z (c)), as implemented:
  * Quantity: pointwise dlog10|I_G| (terminal_currents.csv ig_raw_A) at the common V_G of the two runs (6-decimal match).
  * Required read-out points: EVERY common V_G of the two registered sweeps plus every V_G exported by one run only (A47: no subset is
    pre-selected, so none can be chosen after the fact). A point is UNRESOLVED (never removed) when |I_G| < IR_TOL = 1e-19 A/um in either
    run (or I_G = 0 / non-finite), when it lies on an inverted |I_G| step in either run, when it is exported by one run only, and, for T0r only,
    when kcl_pass is false in either run (T2a/T2b: KCL waived as declared in A45 (c); reported, not used). Otherwise it is RESOLVED, with
    dlog10 = |log10|I_a| - log10|I_b|| (inf on a sign change).
  * Inverted step (plan Z11): for V_G <= 0, sorted by V_G, a step k -> k+1 with |I_G(k+1)| > |I_G(k)| (leakage rising towards V_G = 0); both
    end points are "on an inverted step" (conservative: more unresolved points, never a PASS-inflating removal). run_0067 has 1 such step.
  * Verdict:
      - a resolved point with dlog10 > 0.1, or (T0r) the partner's inverted steps disappear in the run -> SENSITIVITY DETECTED
        (T0r: "tolerance sensitivity detected on the original mesh"; T2: "T(E) step error unresolved at this QT mesh");
      - (T2a/T2b) I_G, I_D and I_S bit-identical to the partner -> UNRESOLVED ("QT-mesh activation not demonstrated"), never "converged";
      - no resolved point (empty support) -> UNRESOLVED (empty support);
      - any unresolved required point -> UNRESOLVED overall (reported point by point);
      - otherwise STABLE (T0r: "QTNLSC I_G at the run_0067 mesh is stable under x0.01 tolerances"; T2: "post-processed T(E) stable under this
        QT-mesh perturbation").
    A run without terminal_currents.csv (out of memory, timeout without export, simulator error) -> UNRESOLVED, with the reason.
  * Not allowed from any result (A45 (c)): QTNLSC convergence; solver-error attribution of the S2-11 change; automatic-slicing causation;
    a self-consistent or KCL-closed I_G; any H-C verdict; transfer to other films or oxide sets.
Supplementary evidence (reported, never used by the verdict; for manual_checks.md checks 1-5): per logged bias, from deckbuild.out, the Newton
iteration count, the last row of the iteration table (log10 norms) and the electrode table (In, Ic, Itnl, It per electrode); the counts of
"Cannot find interface near specified electrode", "Cannot trap", cut-back and memory-allocation messages; the echoed qtx.mesh / qty.mesh lines;
whether "Must enclose oxide" or QTUNN.DIR appears.
"""
import csv
import hashlib
import json
import math
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'branch_d'
IR_TOL = 1e-19          # A/um (solver.yaml ir.tol; unit ASSUMED A/um, plan Z11)
DEC = 0.1               # dec (PA-4 (b))
KINDS = ('T0r', 'T2a', 'T2b')
COLS = ('vg_V', 'id_raw_A', 'is_raw_A', 'ig_raw_A', 'kcl_pass')
CLAIM = {'T0r': ('tolerance sensitivity detected on the original mesh',
                 'QTNLSC I_G at the run_0067 mesh is stable under x0.01 tolerances'),
         'T2a': ('T(E) step error unresolved at this QT mesh (change > 0.1 dec)',
                 'post-processed T(E) stable under this QT-mesh perturbation (QTY points 0.5 -> 0.25 nm)'),
         'T2b': ('T(E) step error unresolved at this QT mesh (change > 0.1 dec)',
                 'post-processed T(E) stable under this QT-mesh perturbation (QTX slices 0.2 -> 0.1 um)')}
NOT_ALLOWED = ['QTNLSC convergence', 'that the S2-11 change was (partly) solver error', 'automatic-slicing causation of the S2-11 change',
               'a self-consistent or KCL-closed I_G', 'any H-C verdict', 'transfer to other films or oxide sets']


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).is_file() else None


def read_run(d):
    """execution.json (or {}), columns of terminal_currents.csv (or None), deckbuild.out text (or '')"""
    d = Path(d); exj = json.loads((d / 'execution.json').read_text()) if (d / 'execution.json').is_file() else {}
    cols = None; tc = d / 'terminal_currents.csv'
    if tc.is_file():
        with tc.open(newline='') as fh: rows = list(csv.DictReader(fh))
        if rows and all(c in rows[0] for c in COLS):
            cols = {c: [float(r[c]) for r in rows] for c in COLS}
    out = (d / 'deckbuild.out').read_text(errors='replace') if (d / 'deckbuild.out').is_file() else ''
    return exj, cols, out


def key(v): return round(float(v), 6) + 0.0


def inverted(cols):
    """V_G keys (<= 0) that are end points of an inverted |I_G| step, and the number of such steps"""
    p = sorted((key(v), abs(i)) for v, i in zip(cols['vg_V'], cols['ig_raw_A']) if key(v) <= 0 and math.isfinite(i))
    steps = [(p[k][0], p[k + 1][0]) for k in range(len(p) - 1) if p[k + 1][1] > p[k][1]]
    return {v for s in steps for v in s}, steps


def evidence(out):
    """supplementary deckbuild.out evidence of the logged sweep (between 'log outf=' and 'log off'); never used by the verdict"""
    lines = out.splitlines()
    i0 = next((k for k, l in enumerate(lines) if re.match(r'^ATLAS>\s*log\s+outf=', l, re.I)), None)
    i1 = next((k for k, l in enumerate(lines) if i0 is not None and k > i0 and re.match(r'^ATLAS>\s*log\s+off', l, re.I)), len(lines))
    biases, cur = [], None
    for l in (lines[i0:i1] if i0 is not None else []):
        m = re.match(r'^\s*V\(\s*gate\s*\)\s*=\s*(\S+)', l)
        if m: cur = {'vg_V': float(m.group(1)), 'newton_iterations': 0, 'last_norms_log10': None, 'electrodes': {}}; biases.append(cur); continue
        if cur is None: continue
        m = re.match(r'^\s*(\d+)\s+[A-Z]\s+(.*)$', l)
        if m and not cur['electrodes']:
            cur['newton_iterations'] = int(m.group(1)); cur['last_norms_log10'] = m.group(2).split(); continue
        m = re.match(r'^(gate|source|drain)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$', l)
        if m:
            try: cur['electrodes'][m.group(1)] = {'Va': float(m.group(2)), 'In': float(m.group(3)), 'Ic': float(m.group(4)), 'Itnl': float(m.group(5)), 'It': float(m.group(6))}
            except ValueError: pass
    cnt = lambda pat: sum(1 for l in lines if re.search(pat, l, re.I) and not re.match(r'^\s*(ATLAS>\s*)?#', l))   # comment echoes excluded
    return {'logged_bias_blocks': len(biases), 'biases': biases,
            'warnings': {'cannot_find_interface_near_electrode': cnt(r'Cannot find interface near specified electrode'),
                         'cannot_trap': cnt(r'Cannot trap'), 'cut_back': cnt(r'cut back'), 'memory_allocation_failure': cnt(r'Memory allocation failure'),
                         'must_enclose_oxide': cnt(r'Must enclose oxide')},
            'qt_mesh_lines': [l.split('ATLAS>', 1)[1].strip() for l in lines if re.match(r'^ATLAS>\s*qt[xy]\.mesh\b', l, re.I)],
            'qtunn_dir_mentioned': any(re.search(r'qtunn\.dir', l, re.I) and not re.match(r'^\s*(ATLAS>\s*)?#', l) for l in lines),   # comment echoes excluded
            'total_grid_points': next((l.strip() for l in lines if 'Total grid points' in l), None)}


def compare(kind, run, partner):
    if kind not in KINDS: raise SystemExit(f'KIND must be one of {KINDS}')
    ea, ca, oa = read_run(run); eb, cb, ob = read_run(partner)
    res = {'readout': 'branch D (register A45 (c) = PA-4 (b); A47)', 'kind': kind, 'script_sha256': sha(__file__),
           'run': {'dir': str(run), 'run_id': ea.get('run_id'), 'label': ea.get('label'), 'status': ea.get('status'),
                   'files_sha256': {f: sha(Path(run) / f) for f in ('execution.json', 'device.in', 'terminal_currents.csv', 'deckbuild.out')}},
           'partner': {'dir': str(partner), 'run_id': eb.get('run_id'), 'label': eb.get('label'), 'status': eb.get('status'),
                       'files_sha256': {f: sha(Path(partner) / f) for f in ('execution.json', 'device.in', 'terminal_currents.csv', 'deckbuild.out')}},
           'rule': {'ir_tol_A_per_um': IR_TOL, 'dec': DEC, 'kcl': 'censors (unresolved) for T0r; waived for T2a/T2b (A45 (c))',
                    'required_points': 'every common V_G plus every V_G of one run only (A47)'},
           'not_allowed': NOT_ALLOWED, 'evidence_run': evidence(oa), 'evidence_partner': evidence(ob)}
    miss = [n for n, c in (('run', ca), ('partner', cb)) if c is None]
    if miss:
        why = []
        for n, o, e in (('run', oa, ea), ('partner', ob, eb)):
            if n in miss:
                why.append(f'{n} has no terminal_currents.csv (status {e.get("status")}'
                           + ('; out of memory: "Memory allocation failure" in deckbuild.out, feasibility limit of the 32-bit build' if re.search(r'Memory allocation failure', o) else '') + ')')
        res.update({'verdict': 'UNRESOLVED (' + '; '.join(why) + ')', 'claim': None, 'points': []}); return res
    inv_a, st_a = inverted(ca); inv_b, st_b = inverted(cb)
    ia = {key(v): k for k, v in enumerate(ca['vg_V'])}; ib = {key(v): k for k, v in enumerate(cb['vg_V'])}
    pts = []
    for v in sorted(set(ia) | set(ib)):
        p = {'vg_V': v}
        if v not in ia or v not in ib: p['class'] = 'unresolved: exported by one run only'; pts.append(p); continue
        a, b = ca['ig_raw_A'][ia[v]], cb['ig_raw_A'][ib[v]]; p.update({'IG_run': a, 'IG_partner': b})
        why = []
        if not (math.isfinite(a) and math.isfinite(b)) or abs(a) < IR_TOL or abs(b) < IR_TOL: why.append('below ir.tol 1e-19 A/um (or zero / non-finite)')
        if v in inv_a or v in inv_b: why.append('on an inverted |I_G| step')
        kcl_bad = not (ca['kcl_pass'][ia[v]] > 0 and cb['kcl_pass'][ib[v]] > 0)
        if kcl_bad: p['kcl_fail'] = True
        if kcl_bad and kind == 'T0r': why.append('KCL fails in either run')
        if why: p['class'] = 'unresolved: ' + '; '.join(why)
        else: p.update({'class': 'resolved', 'dlog10': float(abs(math.log10(abs(a)) - math.log10(abs(b)))) if a * b > 0 else float('inf')})
        pts.append(p)
    resolved = [p for p in pts if p['class'] == 'resolved']; unres = [p['vg_V'] for p in pts if p['class'] != 'resolved']
    big = [p['vg_V'] for p in resolved if p['dlog10'] > DEC]
    ident = all(ca[c] == cb[c] for c in ('vg_V', 'id_raw_A', 'is_raw_A', 'ig_raw_A'))
    inv_gone = kind == 'T0r' and len(st_b) > 0 and len(st_a) == 0
    sens, stable = CLAIM[kind]
    if big or inv_gone:
        v = 'SENSITIVITY DETECTED' + (f' (resolved change > {DEC} dec at V_G {big})' if big else '') + (' (the partner\'s inverted steps disappear)' if inv_gone else ''); claim = sens
    elif kind != 'T0r' and ident: v = 'UNRESOLVED (bit-identical to the partner: QT-mesh activation not demonstrated; never "converged")'; claim = 'QT-mesh activation not demonstrated'
    elif not resolved: v = 'UNRESOLVED (empty support: no resolved common point)'; claim = None
    elif unres: v = f'UNRESOLVED overall ({len(unres)} unresolved required points; reported point by point)'; claim = None
    else: v = 'STABLE'; claim = stable
    res.update({'verdict': v, 'claim': claim, 'common_points': len(set(ia) & set(ib)), 'resolved_points': len(resolved), 'unresolved_points': len(unres),
                'max_resolved_dlog10': max((p['dlog10'] for p in resolved), default=None), 'resolved_above_0p1_dec_vg': big,
                'inverted_steps': {'run': st_a, 'partner': st_b}, 'bit_identical_currents': ident,
                'kcl_fail_points': [p['vg_V'] for p in pts if p.get('kcl_fail')], 'points': pts})
    return res


def write(res):
    OUT.mkdir(exist_ok=True)
    f = OUT / f'branch_d_{res["kind"]}_{res["run"]["run_id"]}_vs_{res["partner"]["run_id"]}.json'
    f.write_text(json.dumps(res, indent=1, default=float)); return f


def selftest():
    """synthetic run directories only; no run data"""
    ok = []; tmp = Path(tempfile.mkdtemp(prefix='bdr_'))
    vg = [round(-3 + 0.2 * k, 6) for k in range(11)] + [round(-0.95 + 0.05 * k, 6) for k in range(50)] + [round(1.6 + 0.1 * k, 6) for k in range(15)]

    def mk(name, ig, kcl=None, rid='run_9999', drop=()):
        d = tmp / name; d.mkdir()
        (d / 'execution.json').write_text(json.dumps({'run_id': rid, 'label': name, 'status': 'REAL_ATLAS_SCORED'}))
        with (d / 'terminal_currents.csv').open('w', newline='') as fh:
            w = csv.writer(fh); w.writerow(list(COLS) + ['id_A_per_um'])
            for k, v in enumerate(vg):
                if v in drop: continue
                w.writerow([v, 1e-12, -1e-13, ig(v), (1 if kcl is None else kcl(v)), 1e-12])
        return d
    mono = lambda f=1.0: (lambda v: -1e-12 * f * 10 ** (2.0 * (v + 3)) if v <= 0 else -1e-12)   # |I_G| rises with V_G: inverted everywhere
    dec = lambda f=1.0: (lambda v: -f * 1e-11 * 10 ** (-1.0 * (v + 3)) if v <= -1 else -f * 5e-14 * 10 ** (-0.01 * (v + 1)))   # falls monotonically (above ir.tol)
    a = mk('a', dec()); b = mk('b', dec(1.1)); c = mk('c', dec(1.5)); low = mk('low', lambda v: -1e-21)
    def case(name, res, want):
        g = res['verdict'].startswith(want); ok.append(g); print(('ok   ' if g else 'FAIL ') + name + ': ' + res['verdict'])
    case('T0r identical -> STABLE (flat steps are not inverted)', compare('T0r', a, a), 'STABLE')
    case('T2a bit-identical -> activation not demonstrated', compare('T2a', a, a), 'UNRESOLVED (bit-identical')
    case('x1.1 (0.04 dec) -> STABLE', compare('T2a', b, a), 'STABLE')
    case('x1.5 (0.18 dec) -> SENSITIVITY', compare('T2a', c, a), 'SENSITIVITY DETECTED')
    case('all below ir.tol -> empty support', compare('T0r', low, low), 'UNRESOLVED (empty support')
    case('inverted steps everywhere -> unresolved', compare('T2a', mk('m1', mono()), mk('m2', mono(1.01))), 'UNRESOLVED')
    case('missing point -> UNRESOLVED overall', compare('T2a', mk('d1', dec(1.05), drop=(-2.0,)), a), 'UNRESOLVED overall')
    case('KCL fail censors T0r', compare('T0r', mk('k1', dec(1.05), kcl=lambda v: 0 if v == -3.0 else 1), a), 'UNRESOLVED overall')
    case('KCL waived for T2a', compare('T2a', mk('k2', dec(1.05), kcl=lambda v: 0 if v == -3.0 else 1), a), 'STABLE')
    inv1 = mk('i1', lambda v: (dec()(v) * (3.0 if v == -2.6 else 1.0))); case('T0r: partner inverted step disappears -> SENSITIVITY', compare('T0r', a, inv1), 'SENSITIVITY DETECTED')
    oom = tmp / 'oom'; oom.mkdir(); (oom / 'deckbuild.out').write_text('Error: Memory allocation failure.  Try killing processes\n')
    case('no export (OOM) -> UNRESOLVED', compare('T2b', oom, a), 'UNRESOLVED (run has no terminal_currents.csv')
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'selftest {sum(ok)}/{len(ok)}'); return 0 if all(ok) else 1


def main(argv):
    if argv[:1] == ['selftest']: return selftest()
    if len(argv) != 3: print(__doc__); return 2
    res = compare(argv[0], Path(argv[1]), Path(argv[2])); f = write(res)
    print(json.dumps({k: res[k] for k in ('kind', 'verdict', 'claim') if k in res}))
    print(f'run {res["run"]["run_id"]} ({res["run"]["status"]}) vs partner {res["partner"]["run_id"]} ({res["partner"]["status"]}); common '
          f'{res.get("common_points")}, resolved {res.get("resolved_points")}, unresolved {res.get("unresolved_points")}, max resolved dlog10 '
          f'{res.get("max_resolved_dlog10")}; inverted steps run/partner {len(res.get("inverted_steps", {}).get("run", []))}/'
          f'{len(res.get("inverted_steps", {}).get("partner", []))}; written {f.relative_to(HERE.parent)}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
