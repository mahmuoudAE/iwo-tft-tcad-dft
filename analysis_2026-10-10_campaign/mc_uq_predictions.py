#!/usr/bin/env python3
"""Register A55 (PA-15 uncertainty propagation; plan PLAN_C10 5.4 rows U1, U2, U9; CAMPAIGN_DESIGN 5.2 exact relations): Monte Carlo
bands for the prospective products P1-P4 of campaign C10. Written and frozen (sha256 pinned in A55) BEFORE any P run exists.
NO simulator call, no launch, no edit of any frozen file (profile_s4s5 429b3a3f, profile_shared 958c3605, score_register c0f28bb9 and the
registered extraction are imported after their pins are checked). Reads: the branch archives (S4a archive A51; S4d triple) through the
frozen profile_s4s5.load (runs in config/sealed_runs.json or under results/sealed refused), the measured curves of the three calibration
films (campaign_extract.measured; seen calibration data), the P run directories of a manifest (refused unless every listed P run has
finished and is eligible), and the frozen records named for the LOO-2 floors and the S5 fold statuses (sha256-verified). Writes one JSON.

  python analysis_2026-10-10_campaign/mc_uq_predictions.py bands MANIFEST.json --out OUT.json [--post-hoc REASON]

Method (A55 (a)-(k)):
  parameter set  per branch and per delta in DELTAS (0.01 and 0.03 dec; both ASSUMED, both always reported; plan U1): the profile-
                 likelihood confidence set {candidate c of the branch archive with a valid profile, nuisance x = (dV0 from the anchor,
                 ln mu_inf, ell)} with sqrt(J_c(x)) <= sqrt(J_best) + delta and every film window covered >= 95 %; J = the frozen
                 profile_shared.triple_J (exact Q_f shift and MUN scale of the archive's native curves against the measured curves).
                 No likelihood with an assumed measurement sigma: the S4a residuals are systematic (6.3 nm on-state sign 15/15), so an
                 iid Gaussian likelihood is misspecified and would give spuriously narrow bands.
  sampling       per qualifying candidate (archive index k): scrambled Sobol points (M_PROP, seed SEED + 1000 k + round) in a box
                 around its profiled optimum (half-widths HALF0) clipped to the frozen profile bounds (|dV0| <= 0.5 V from the anchor,
                 mu_inf 10..300 cm2/Vs, ell 0..50 nm); an interior box edge reached by the accepted set (within EDGE x half-width) is
                 doubled, at most MAX_ROUNDS rounds (still reached: OPEN, the band is a lower limit of the width); fewer than N_MIN_ACC
                 accepted points in a box never enlarged: half-widths halved. The profiled optimum is always proposed. N_DRAWS draws
                 (numpy default_rng(SEED)): a candidate uniform over the qualifying candidates (equal weight, ASSUMED), then a point
                 uniform over its accepted pool.
  propagation    U1 (exact relations): each P curve, launched at the base candidate b, is transformed to the draw's Q_f and mu law
                 (V_G -> V_G - q dQ_f / C_ox; I -> I x mu_law(mu_inf, ell, t, m*(t)) / mu_band_run(t), roughness unchanged); draws of
                 candidate b only. U1+U2 (ASSUMED additive N_s / W_T transfer): draws of every qualifying candidate c;
                 q_P = q(T_x P_b) + [q(T_x A_c,f) - q(T_x A_b,f)], A_.,f = archive run of the registered reference film f, in the
                 quantity's additive space (V, mV/dec, dec; log10 for mu_FE); transfer quantities only (output quantities: U2
                 UNRESOLVED, not propagated). GAMMA0 is not sampled (not adopted: A49, S4d SURVIVES).
  output curves  (P1 / P2) the Q_f shift at a fixed V_G = log-linear interpolation in V_G between the run's native gate voltages
                 (ASSUMED; a shifted V_G outside the native range drops the draw, counted); V_D must be a native point; MUN scale exact
                 (it cancels in ratios); I_G is never banded (ranked only, plan 5.3). Runs with a tunnelling / Schottky option:
                 APPROXIMATE (profile_shared premise).
  bands          per quantity: median and the 5 / 95 % quantiles of the finite draws, with the dropped count; a parameter whose accepted
                 set reaches a profile bound (within BOUND_FRAC of its range) makes the band edge on that side one-sided (Spearman rho
                 of that parameter with the quantity over the draws, |rho| > RHO_SIDE; else 'side undetermined'). LOO-2 floors
                 (A45 (f)) are applied as registered: [min(q5, q50 - F), max(q95, q50 + F)] ('pct': relative to q50); raw and floored
                 bands both reported.
  model form     every branch (constant mobility S4A-04 / S4c; IGZO.TOKYO S4d; any registered P1 strip / diffusion or P4 NC-convention
                 branch) is its own manifest branch with its own archive, set and bands: never mixed, pooled or averaged.
  reading        calibration-conditional (the shared model failed in S4a); the S5 fold statuses set the reading label (reading_label).
  timing         refused unless every P run of the manifest is finished and eligible; --post-hoc REASON labels every output POST HOC.
"""
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
PINS = {
    'analysis_2026-10-10_campaign/profile_s4s5.py': '429b3a3f3f5c1e650d17760e11665ddbce140ef434b5f80f29e7cd2f4fcf0a4e',
    'analysis_2026-10-10_campaign/profile_shared.py': '958c3605a316393184f022a80c421505e8b9f99a1d214423ec79b83286209d17',
    'analysis_2026-10-10_campaign/score_register.py': 'c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a',
    'analysis_2026-10-10_campaign/campaign_extract.py': '1f6f324a0841d50bb20baf7f94b6444d688aaf4cbdf71707594a06f26e3e63ba',
    'analysis_2026-10-10_campaign/campaign_tools.py': '3b0403d9c5cc5423cb80dabc3765f9a781b7a06b512082b6f210971a9417ab0d',
    'analysis_2026-10-06_extraction/extraction.py': '1ca61a1c7cec5e97ba221cc344be53c1bc0d1d79edf39817976b80d504c706e1',
    'analysis_2026-10-06_extraction/run_extraction.py': 'de7ff06f3414cb8a2947ce07663234c8b3008765caca00fcc33f376831f02c70'}


def sha_file(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check_pins(pins=PINS, root=PKG):
    bad = [f'{k}: {(sha_file(root / k)[:8] if (root / k).is_file() else "missing")} != {v[:8]}' for k, v in pins.items()
           if not (root / k).is_file() or sha_file(root / k) != v]
    if bad: raise SystemExit('refused: frozen dependency changed: ' + '; '.join(bad))


check_pins()
if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
import profile_s4s5 as P4      # noqa: E402  frozen 429b3a3f
import profile_shared as ps    # noqa: E402  frozen 958c3605
import campaign_extract as ce  # noqa: E402  frozen 1f6f324a
ex, rx = ce.ex, ce.rx          # registered extraction (unchanged)

CODE_SHA = sha_file(__file__)
SEED = 20261016
N_DRAWS = 4000
M_PROP = 4096                                   # 2^12 scrambled Sobol points per box round
DELTAS = (0.01, 0.03)                           # dec on sqrt(J), plan U1 (both ASSUMED, both reported)
PARAMS = ('dV0_from_anchor_V', 'ln_mu_inf', 'ell_nm')
HALF0 = (0.05, 0.15, 5.0)                       # initial box half-widths (V, ln units, nm), ASSUMED
LO_G = (-P4.DV_RANGE_V, math.log(10.0), 0.0)     # frozen profile_films bounds
HI_G = (P4.DV_RANGE_V, math.log(300.0), 50.0)
MAX_ROUNDS, EDGE, N_MIN_ACC, BOUND_FRAC, RHO_SIDE = 6, 0.10, 50, 0.01, 0.10
QUANT = (5.0, 50.0, 95.0)
TRANSFER_Q = ('vth_cc_V', 'ss_fixed_mV_dec', 'ss_a1_mV_dec', 'log10_id_3V', 'mu_fe_1.5', 'mu_fe_2.0', 'mu_fe_3.0')
LOG_SPACE = {'mu_fe_1.5', 'mu_fe_2.0', 'mu_fe_3.0'}
OUTPUT_STATUSES = ('REAL_ATLAS_PREDICTION', 'REAL_ATLAS_SCORED')
FOLDS = ('H6p3', 'H2p0', 'H13p2')
SHARED_FAIL = ('calibration-conditional: the shared model FAILED in S4a (frozen surrogate on the complete inventory of 15: best sqrt(J) '
               '0.623 dec > 0.30, 6.3 nm on-state sign 15/15; A51 (d)); parametric bands, model-form error not included')


# ------------------------------------------------------------------------------------------------ guards
def sealed_ids(root=PKG):
    f = root / 'config' / 'sealed_runs.json'
    return {r['run_id'] for r in json.loads(f.read_text())['runs']} if f.is_file() else set()


def guard(run, sealed):
    """results/sealed (frozen _sealed) and every run id of config/sealed_runs.json are refused before anything is opened"""
    P4._sealed(run)
    rid = '_'.join(Path(str(run)).name.split('_')[:2])
    if rid in sealed: raise SystemExit(f'refused: {run} is a sealed run ({rid}, config/sealed_runs.json): never read')


def verified_source(src, root=PKG, sealed=()):
    p = Path(src['path']); p = p if p.is_absolute() else root / p
    P4._sealed(src['path'])
    if not p.is_file() or sha_file(p) != src['sha256']: raise SystemExit(f'refused: {src["path"]} missing or sha256 differs from {src["sha256"][:8]}')
    return json.loads(p.read_text())


def json_at(d, key):
    for k in key: d = d[int(k)] if isinstance(d, list) else d[k]
    return d


# ------------------------------------------------------------------------------------------------ exact relations
def qf_of(v, cox, anchor=P4.QF_ANCHOR):
    """absolute Q_f of a draw: dV0_from_anchor = -q (Q_f - anchor) / C_ox (frozen profile_films)"""
    return anchor - v * cox / ps.Q


def law_scale(r, mu, ell):
    return ps.mu_law(mu, ell, r['t'], r['mstar']) / r['mu_band']


def transfer_T(r, qf, mu, ell):
    """I_new(V) = s I_run(V + q dQ / C_ox): the native points move to V - q dQ / C_ox and scale by MUN_new / MUN_run"""
    return np.asarray(r['vg'], float) - ps.Q * (qf - r['qf']) / r['cox'], np.asarray(r['i'], float) * law_scale(r, mu, ell)


def q_transfer(vg, i, name, a1=None):
    """registered extraction on a (transformed) transfer curve; None if not extractable"""
    try:
        if name == 'vth_cc_V': return ex.crossing(vg, i, rx.I_CC, True)['v']
        if name == 'ss_fixed_mV_dec': return ex.ss_window(vg, i, *rx.WIN, True)['ss']
        if name == 'ss_a1_mV_dec':
            if a1 is None: raise SystemExit('refused: ss_a1_mV_dec needs the registered A1 window of a measured film')
            return ex.ss_window(vg, i, a1[0], a1[1], True)['ss']
        if name == 'log10_id_3V':
            y = float(ce.log_interp(vg, i, np.array([3.0]))[0]); return y if np.isfinite(y) else None
        if name.startswith('mu_fe_'):
            v = float(name[6:])
            if not (vg[0] - 1e-9 <= v <= vg[-1] + 1e-9): return None
            return float(np.interp(v, vg, ex.MU_FACTOR * ex.gm(vg, i)))
    except SystemExit: raise
    except Exception: return None
    raise SystemExit(f'refused: unknown transfer quantity {name} (registered: {TRANSFER_Q})')


def additive(name, v):
    if v is None or not np.isfinite(v): return None
    if name in LOG_SPACE: return math.log10(v) if v > 0 else None
    return float(v)


def back(name, a): return 10 ** a if name in LOG_SPACE else a


def out_log(r, qf, mu, ell, vg0, vd0, cur):
    """log10 |I_cur| of an output family at (vg0, vd0) after the transform; None if the shifted V_G leaves the native V_G range"""
    if cur not in ('id', 'is'): raise SystemExit(f'refused: {cur}: only id / is are banded (I_G is ranked only, plan 5.3)')
    vstar = vg0 + ps.Q * (qf - r['qf']) / r['cox']; gs = sorted(r['family'])
    if not (gs[0] - 1e-9 <= vstar <= gs[-1] + 1e-9): return None

    def at(g):
        vd, cid, cis = r['family'][g]; k = np.where(np.abs(vd - vd0) < 1e-6)[0]
        if not len(k): raise SystemExit(f'refused: V_D {vd0} is not a native point of {r["run_id"]} at V_G {g}')
        c = (cid if cur == 'id' else cis)[k[0]]
        return math.log10(abs(c)) if c != 0 else None
    hit = [g for g in gs if abs(g - vstar) < 1e-9]
    if hit: y = at(hit[0])
    else:
        ga = max(g for g in gs if g < vstar); gb = min(g for g in gs if g > vstar); ya, yb = at(ga), at(gb)
        if ya is None or yb is None: return None
        y = ya + (yb - ya) * (vstar - ga) / (gb - ga)
    return None if y is None else y + math.log10(law_scale(r, mu, ell))


# ------------------------------------------------------------------------------------------------ confidence set
def centre_of(prof):
    p = prof['profiled']; return np.array([p['dV0_from_anchor_V'], math.log(p['mu_inf_cm2Vs']), p['ell_nm']], float)


def sqrtJ_at(R, info, x, J=ps.triple_J):
    v, lmu, ell = (float(z) for z in x); dQf = qf_of(v, R[0]['cox']) - R[0]['qf']
    j, per = J(R, info, dQf, math.exp(lmu), ell)
    cov = all(min(f['sub']['coverage'], f['on']['coverage']) >= 0.95 for f in per.values())
    return (math.sqrt(j) if np.isfinite(j) and j >= 0 else float('nan')), cov


def near_optimal(R, info, prof, thr, seed, J=ps.triple_J, m=M_PROP):
    from scipy.stats import qmc
    c = centre_of(prof); lo_g, hi_g = np.array(LO_G), np.array(HI_G); half = np.array(HALF0, float); grown = False; hist = []
    A = np.empty((0, 3)); touch = []
    for rnd in range(MAX_ROUNDS):
        lo, hi = np.maximum(c - half, lo_g), np.minimum(c + half, hi_g)
        X = np.vstack([c, lo + qmc.Sobol(3, scramble=True, seed=seed + rnd).random(m) * (hi - lo)])
        ok = []
        for x in X:
            s, cov = sqrtJ_at(R, info, x, J); ok.append(bool(np.isfinite(s) and s <= thr + 1e-12 and cov))
        A = X[np.array(ok)]; touch = []
        for d in range(3):
            w = EDGE * half[d]
            if len(A) and ((lo[d] > lo_g[d] + 1e-12 and A[:, d].min() <= lo[d] + w) or (hi[d] < hi_g[d] - 1e-12 and A[:, d].max() >= hi[d] - w)):
                touch.append(d)
        hist.append({'round': rnd, 'half': half.tolist(), 'n_accepted': int(len(A)), 'interior_edges_reached': [PARAMS[d] for d in touch]})
        if touch and rnd < MAX_ROUNDS - 1:
            half[touch] *= 2; grown = True; continue
        if not touch and len(A) < N_MIN_ACC and not grown and rnd < MAX_ROUNDS - 1:
            half = half / 2; continue
        break
    bound = []
    for d in range(3):
        span = hi_g[d] - lo_g[d]
        if len(A) and (A[:, d] <= lo_g[d] + BOUND_FRAC * span).any(): bound.append([PARAMS[d], 'lower'])
        if len(A) and (A[:, d] >= hi_g[d] - BOUND_FRAC * span).any(): bound.append([PARAMS[d], 'upper'])
    return A, {'rounds': hist, 'n_accepted': int(len(A)), 'open': [PARAMS[d] for d in touch], 'at_profile_bound': bound}


def draw(pools, n=N_DRAWS, seed=SEED):
    ids = sorted(pools); rng = np.random.default_rng(seed); out = []
    for k in rng.integers(0, len(ids), n):
        A = pools[ids[k]]; out.append((ids[k], A[int(rng.integers(0, len(A)))]))
    return out


# ------------------------------------------------------------------------------------------------ bands
def spearman(a, b):
    from scipy.stats import spearmanr
    if len(a) < 3 or np.ptp(a) == 0 or np.ptp(b) == 0: return None
    r = spearmanr(a, b).statistic; return float(r) if np.isfinite(r) else None


def band(vals, params, bound):
    a = np.array([np.nan if v is None else v for v in vals], float); f = np.isfinite(a)
    res = {'n_draws': int(len(a)), 'n_finite': int(f.sum()), 'n_dropped': int((~f).sum())}
    if not f.any(): res['band'] = None; return res
    q5, q50, q95 = (float(z) for z in np.percentile(a[f], QUANT))
    res.update(q05=q5, median=q50, q95=q95, one_sided=[])
    for pname, side in bound:
        rho = spearman(np.asarray(params[pname], float)[f], a[f])
        if rho is None or abs(rho) <= RHO_SIDE: edge = 'side undetermined'
        else: edge = 'q95 open (upper edge one-sided)' if (rho > 0) == (side == 'upper') else 'q05 open (lower edge one-sided)'
        res['one_sided'].append({'parameter': pname, 'profile_bound': side, 'spearman_rho': rho, 'edge': edge})
    return res


def floored(b, F, kind):
    if b.get('median') is None: return None
    m = b['median']; lo, hi = (m * (1 - F / 100), m * (1 + F / 100)) if kind == 'pct' else (m - F, m + F)
    return [min(b['q05'], lo), max(b['q95'], hi)]


def reading_label(folds):
    st = [folds.get(k) for k in FOLDS]
    if any(s not in ('PASS', 'FAIL') for s in st):
        return f'TRANSFERABILITY UNKNOWN (S5 fold statuses {dict(zip(FOLDS, st))}): calibration-conditional parametric sensitivity only'
    bad = [k for k, s in zip(FOLDS, st) if s == 'FAIL']
    if len(bad) >= 2: return f'TRANSFERABILITY FALSIFIED in S5 ({bad} FAIL): calibration-conditional parametric sensitivity only, never a predictive band'
    if bad: return (f'TRANSFERABILITY FAILED in fold {bad[0]}: products resting on that film regime (P4 for H2p0; the film itself otherwise) '
                    'are sensitivity only; the others calibration-conditional with partial retrospective LOO support')
    return 'calibration-conditional with retrospective LOO support (S5 3/3 PASS; LOO-2 floors applied)'


# ------------------------------------------------------------------------------------------------ loading
def load_output(run, sealed):
    guard(run, sealed); d = ce.resolve(run); exj = json.loads((d / 'execution.json').read_text()); probs = []
    if exj.get('status') not in OUTPUT_STATUSES: probs.append(f'status {exj.get("status")}')
    if exj.get('timed_out'): probs.append('timed out')
    if exj.get('returncode') != 0: probs.append(f'returncode {exj.get("returncode")}')
    if (exj.get('scan') or {}).get('errors'): probs.append('simulator errors')
    f = d / 'output_characteristics.csv'; fam = {}
    if not f.is_file(): probs.append('no output_characteristics.csv')
    else:
        rows = list(csv.DictReader(f.open(newline='')))
        if not rows or any(int(r['kcl_pass']) != 1 for r in rows): probs.append('no rows or a KCL failure')
        for g in sorted({float(r['vg_V']) for r in rows}):
            a = np.array([(float(r['vd_V']), float(r['id_A_per_um']), float(r['is_A_per_um'])) for r in rows if float(r['vg_V']) == g])
            a = a[np.argsort(a[:, 0])]; fam[g] = (a[:, 0], a[:, 1], a[:, 2])
    r = P4._meta(d, exj)
    h = hashlib.sha256()
    for n in ('execution.json', 'material_model_used.json', 'output_characteristics.csv'):
        p = d / n; h.update(n.encode()); h.update(p.read_bytes() if p.is_file() else b'<missing>')
    _, _, s = ce.ct.configs(ce.ct.V3, [o for o in r['overrides'] if o.startswith(('solver.', 'geometry.'))])
    r.update(family=fam, po=s.get('physics_options') or {}, eligibility={'eligible': not probs, 'problems': probs}, digest=h.hexdigest())
    return r


def load_transfer(run, sealed):
    guard(run, sealed); return P4.load(run)


def same_point(r, base_c):
    """the P run carries the base candidate's launched coordinates and branch (from its own files)"""
    x, b = P4.coords(r); xb, bb = base_c['x'], base_c['branch']
    ok = abs(x['lNs'] - xb['lNs']) < 1e-6 and abs(x['WT'] - xb['WT']) < 1e-9 and (x['g0'] is None) == (xb['g0'] is None) and \
        (x['g0'] is None or abs(x['g0'] - xb['g0']) < 1e-9) and b == bb
    if not ok: raise SystemExit(f'refused: {r.get("run_id")} is not at the base candidate {base_c["id"]} ({x}, {b} vs {xb}, {bb})')


# ------------------------------------------------------------------------------------------------ one branch
def eval_product(prod, P, draws, cand_cox, base_id, arch_ref, info, mode):
    """values per quantity over the draws; arch_ref[c] = archive run of the product's reference film for candidate c"""
    vals, prm = {}, {k: [] for k in PARAMS}
    for c, x in draws:
        for k, z in zip(PARAMS, x): prm[k].append(float(z))
    if prod['kind'] == 'transfer':
        names = list(prod['quantities']); a1 = info[P['t']]['a1_window'] if P['t'] in P4.FILMS else None
        f = float(prod['u2_reference_film']); a1f = info[f]['a1_window']
        for n in names: vals[n] = []
        for c, x in draws:
            qf, mu, ell = qf_of(x[0], cand_cox), math.exp(x[1]), float(x[2])
            vg, i = transfer_T(P, qf, mu, ell)
            for n in names:
                q = q_transfer(vg, i, n, a1)
                if mode == 'U1+U2' and c != base_id:
                    qc = q_transfer(*transfer_T(arch_ref[c], qf, mu, ell), n, a1f); qb = q_transfer(*transfer_T(arch_ref[base_id], qf, mu, ell), n, a1f)
                    aq, ac, ab = additive(n, q), additive(n, qc), additive(n, qb)
                    q = None if None in (aq, ac, ab) else back(n, aq + ac - ab)
                vals[n].append(q)
    else:
        if mode == 'U1+U2': return None, prm   # U2 UNRESOLVED for output quantities (no archive analogue)
        for pt in prod.get('points', []):
            n = f'log10_{pt["current"]}_vg{pt["vg"]:g}_vd{pt["vd"]:g}'; vals[n] = []
            for c, x in draws: vals[n].append(out_log(P, qf_of(x[0], cand_cox), math.exp(x[1]), float(x[2]), pt['vg'], pt['vd'], pt['current']))
        for rt in prod.get('ratios', []):
            n = f'log10_ratio_{rt["current"]}_vg{rt["vg"]:g}_vd{rt["vd_num"]:g}_over_vd{rt["vd_den"]:g}'; vals[n] = []
            for c, x in draws:
                qf, mu, ell = qf_of(x[0], cand_cox), math.exp(x[1]), float(x[2])
                a = out_log(P, qf, mu, ell, rt['vg'], rt['vd_num'], rt['current']); b = out_log(P, qf, mu, ell, rt['vg'], rt['vd_den'], rt['current'])
                vals[n].append(None if a is None or b is None else a - b)
    return vals, prm


def run_branch(name, cands, base_id, products, info, floors=(), J=ps.triple_J, m=M_PROP, n=N_DRAWS, seed=SEED):
    """cands: [{'id', 'k', 'R': [runs by film], 'prof': profile or None}] in archive order; products: [(prod, P run record)]"""
    valid = [c for c in cands if c['prof'] and c['prof'].get('valid') and c['prof']['profiled'].get('sqrtJ_dec') is not None]
    if base_id not in {c['id'] for c in valid}: raise SystemExit(f'refused: base candidate {base_id} has no valid profile in branch {name}')
    best = min(c['prof']['profiled']['sqrtJ_dec'] for c in valid); byid = {c['id']: c for c in valid}
    out = {'branch': name, 'base_candidate': base_id, 'best_sqrtJ_dec': best, 'sets': {}, 'products': {}}
    fl = {(f['product_id'], f['quantity']): f for f in floors}
    for di, delta in enumerate(DELTAS):
        thr = best + delta; qual = [c for c in valid if c['prof']['profiled']['sqrtJ_dec'] <= thr + 1e-12]
        pools, stats = {}, {}
        for c in qual:
            A, st = near_optimal(c['R'], info, c['prof'], thr, SEED + 1000 * c['k'], J, m); pools[c['id']] = A; stats[c['id']] = st
        bound = sorted({tuple(b) for st in stats.values() for b in st['at_profile_bound']})
        out['sets'][f'{delta:g}'] = {'threshold_sqrtJ_dec': thr, 'qualifying': [c['id'] for c in qual], 'per_candidate': stats,
                                     'open': sorted({p for st in stats.values() for p in st['open']}), 'at_profile_bound': [list(b) for b in bound]}
        cox = byid[base_id]['R'][0]['cox']
        for mode, pl in (('U1', {base_id: pools[base_id]}), ('U1+U2', pools)):
            dr = draw(pl, n, seed)
            bnd_m = sorted({tuple(b) for cid in pl for b in stats[cid]['at_profile_bound']})
            for prod, P in products:
                f = float(prod.get('u2_reference_film', P['t'] if P['t'] in P4.FILMS else 2.0))
                ref = {c['id']: next((r for r in c['R'] if r['t'] == f), None) for c in qual}
                vals, prm = eval_product(prod, P, dr, cox, base_id, ref, info, mode)
                po = out['products'].setdefault(prod['id'], {'product': prod['product'], 'kind': prod['kind'], 'run': P.get('run_id'),
                                                             'labels': _labels(prod, P), 'bands': {}})
                slot = po['bands'].setdefault(f'{delta:g}', {})
                if vals is None:
                    slot[mode] = 'UNRESOLVED: N_s / W_T (U2) not propagated for output quantities (no archive analogue; A55 (e))'; continue
                slot[mode] = {}
                for qn, v in vals.items():
                    b = band(v, prm, bnd_m); k = fl.get((prod['id'], qn))
                    if k: b['loo2_floor'] = {'F': k['floor'], 'kind': k.get('kind', 'abs'), 'floored_band': floored(b, k['floor'], k.get('kind', 'abs'))}
                    slot[mode][qn] = b
    return out


def _labels(prod, P):
    L = ['U1 exact relations (CAMPAIGN_DESIGN 5.2)', 'U1+U2: ASSUMED additive N_s / W_T transfer from the reference film']
    if prod['kind'] == 'output': L.append('Q_f shift at fixed V_G: ASSUMED log-linear interpolation between native gate voltages')
    if P.get('breakers'): L.append(f'APPROXIMATE: tunnelling / Schottky option on ({P["breakers"]}); shift / scale not exact')
    if prod['kind'] == 'transfer': L.append('mu_FE and I_D(3 V) on a shifted curve: interpolated (A10)')
    return L


# ------------------------------------------------------------------------------------------------ manifest
def bands(manifest, out_path, post_hoc=None, root=PKG, info=None):
    mp = Path(manifest); man = json.loads(mp.read_text()); sealed = sealed_ids(root)
    loaded = []   # timing rule first: every P run finished and eligible before any archive work
    for br in man['branches']:
        for prod in br['products']:
            if prod.get('product') not in ('P1', 'P2', 'P3', 'P4'): raise SystemExit(f'refused: {prod.get("id")}: product must be P1..P4')
            if prod['kind'] not in ('transfer', 'output'): raise SystemExit(f'refused: {prod["id"]}: kind {prod["kind"]} needs its own logged extension')
            P = load_transfer(prod['run'], sealed) if prod['kind'] == 'transfer' else load_output(prod['run'], sealed)
            if not (P.get('eligibility') or {}).get('eligible'): raise SystemExit(f'refused: P run {prod["run"]} not finished / eligible: {P["eligibility"]}')
            if prod['kind'] == 'transfer':
                bad = [q for q in prod['quantities'] if q not in TRANSFER_Q or (q == 'ss_a1_mV_dec' and P['t'] not in P4.FILMS)]
                if bad: raise SystemExit(f'refused: {prod["id"]}: quantities {bad} not registered for this film')
                if float(prod['u2_reference_film']) not in P4.FILMS: raise SystemExit(f'refused: {prod["id"]}: reference film must be a measured film')
            loaded.append((br['name'], prod, P))
    s5 = man['s5']; verified_source(s5['source'], root); label = reading_label(s5['folds'])
    floors = man.get('loo2_floors', [])
    for f in floors:
        v = json_at(verified_source(f['source'], root), f['source']['key'])
        if abs(abs(float(v)) - f['floor']) > 1e-9 * max(1.0, abs(f['floor'])): raise SystemExit(f'refused: LOO-2 floor {f} differs from its source value {v}')
    if info is None: info, _ = ce.measured()
    res = {'tool': 'mc_uq_predictions.py (register A55)', 'code_sha256': CODE_SHA, 'pins': PINS, 'manifest': str(mp), 'manifest_sha256': sha_file(mp),
           'seed': SEED, 'n_draws': N_DRAWS, 'm_prop': M_PROP, 'deltas_dec': DELTAS, 'reading': [SHARED_FAIL, label],
           'post_hoc': post_hoc, 'p_runs': {p['id']: {'run_id': P.get('run_id'), 'digest': P.get('digest')} for _, p, P in loaded}, 'branches': []}
    for br in man['branches']:
        ap = Path(br['archive']); ap = ap if ap.is_absolute() else root / ap
        if sha_file(ap) != br['archive_sha256']: raise SystemExit(f'refused: archive {br["archive"]} sha256 differs')
        C = P4.load_archive(str(ap), loader=lambda r: load_transfer(r, sealed))
        PP = P4.profile_pool(C, info)
        cands = [{'id': c['id'], 'k': k, 'R': c['R'], 'prof': p} for k, (c, p, _) in enumerate(PP)]
        base_c = next(c for c in C if c['id'] == br['base_candidate'])
        prods = [(prod, P) for bn, prod, P in loaded if bn == br['name']]
        for _, P in prods: same_point(P, base_c)
        res['branches'].append(run_branch(br['name'], cands, br['base_candidate'], prods, info,
                                          [f for f in floors if any(f['product_id'] == p['id'] for p, _ in prods)]))
    if post_hoc: res['reading'].append(f'POST HOC: {post_hoc} (A55 (k): computed after P outputs were read, or with a change)')
    txt = json.dumps(res, indent=1, default=float); Path(out_path).write_text(txt)
    print(f'wrote {out_path} sha256 {hashlib.sha256(txt.encode()).hexdigest()}'); return res


def main(argv):
    if len(argv) < 2 or argv[0] != 'bands' or '--out' not in argv:
        print(__doc__.split('\n\n')[1]); return 2
    i = argv.index('--out'); out = argv[i + 1]; ph = argv[argv.index('--post-hoc') + 1] if '--post-hoc' in argv else None
    try: bands(argv[1], out, ph)
    except SystemExit as e: print(e); return 3
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
