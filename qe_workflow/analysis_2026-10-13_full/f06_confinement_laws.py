"""Fig. 6: confinement laws dEg(t), dEc(t), dm*(t) as used in TCAD, re-fitted from the re-derived DFT points (f05),
and the check that they reproduce the ATLAS deck values.

Laws (config/iwo_material_model_v2.yaml, _v3.yaml): y = a t^-p (dEg, dEc), dm = b t^-q; TCAD: EG300 = 3.05 + dEg(t),
AFFINITY = 4.3 - dEc(t), m* = 0.208 + dm(t) (bulk anchors LITERATURE), NC300 = 2 (2 pi m* m0 kT/h^2)^1.5 (3-D) or
N2D/t = m* m0 kT/(pi hbar^2 t) (quasi-2D, C10 at 2.0 nm only), T = 300 K.
V2: two-point laws through the 1 and 2 nm points at the Lin-label thicknesses 0.95 / 1.98 nm, built from the rounded
logged values 0.900/0.335 (dEg), 0.848/0.281 (dEc), 0.122/0.04715 (dm).
V3 / C10 'fit3': least squares of ln y on ln t through the 0.695 / 0.930 / 1.962 nm points (H-H thickness).
Deck values read from results/runs/<run>/device.in (MATERIAL statement): V2 run_0058 (2.0 nm); C10 runs 0061 (2.0),
0068 (6.3), 0069 (13.2).
"""
import json
import math
import re

import numpy as np

import qeio as q
from figstyle import plt, save, panel, CYCLE

PKG = q.QE.parent
EG_B, CHI_B, M_B = 3.05, 4.3, 0.208
ME, KBJ, HP = 9.1093837015e-31, 1.380649e-23, 6.62607015e-34
HBAR = HP / (2 * math.pi)
T = 300.0
DECKS = [('V2', 2.0, 'run_0058_2p0_v2_anchor_2p0'), ('C10', 2.0, 'run_0061_2p0_c10_s0_01_2p0'),
         ('C10', 6.3, 'run_0068_6p3_c10_s1_01_6p3'), ('C10', 13.2, 'run_0069_13p2_c10_s1_02_13p2')]


def nc3d(m):
    return 2 * (2 * math.pi * m * ME * KBJ * T / HP ** 2) ** 1.5 / 1e6


def nq2d(m, t_nm, e21=None):
    n = m * ME * KBJ * T / (math.pi * HBAR ** 2) / (t_nm * 1e-9) / 1e6
    return n * (1 + math.exp(-e21 / (q.KB * T))) if e21 else n


def fit(t, y):
    A = np.vstack([np.ones(len(t)), -np.log(t)]).T
    (la, p), *_ = np.linalg.lstsq(A, np.log(y), rcond=None)
    return float(math.exp(la)), float(p)


def yaml_val(path, block, key):
    """value of 'key:' inside the yaml block 'block:' (first occurrence after the block line), with file:line."""
    L = q.lines(str(path))
    b = next(i for i, l in enumerate(L) if re.match(rf'\s*{block}:', l))
    for i in range(b + 1, len(L)):
        m = re.match(rf'\s+{key}:\s*([-\d.eE+]+)\s*$', L[i])
        if m:
            return float(m.group(1)), q.src(path, i + 1)
    raise LookupError(block + key)


def deck(run):
    p = PKG / 'results' / 'runs' / run / 'device.in'
    out = {}
    for key in ('eg300', 'affinity', 'nc300'):
        m, i = q.first(p, rf'\b{key}=([-\d.e+]+)')
        out[key] = q.V(float(m.group(1)), q.src(p, i), 'DECK')
    m, i = q.first(p, r'm\* = ([\d.]+) m0')
    out['mstar'] = q.V(float(m.group(1)), q.src(p, i), 'DECK')
    return out


def main():
    f05 = json.loads((q.OUT / 'f05_slab_series.json').read_text())
    f07 = json.loads((q.OUT / 'f07_hse_ratio.json').read_text())
    S = f05['slabs']
    labs = ['0.75', '1.0', '2.0']
    t = np.array([S[l]['thickness_HH_nm']['value'] for l in labs])
    pts = {'dEg': np.array([S[l]['dEg_eV'] for l in labs]), 'dEc': np.array([S[l]['dEc_eV'] for l in labs]),
           'dm': np.array([S[l]['dm_m0'] for l in labs])}
    v2y = q.PKG if hasattr(q, 'PKG') else None
    y2, y3 = PKG / 'config' / 'iwo_material_model_v2.yaml', PKG / 'config' / 'iwo_material_model_v3.yaml'
    cfg = {'V2': {'dEg': (yaml_val(y2, 'dEg_QC_eV', 'a'), yaml_val(y2, 'dEg_QC_eV', 'p')),
                  'dEc': (yaml_val(y2, 'dEc_eV', 'a'), yaml_val(y2, 'dEc_eV', 'p')),
                  'dm': (yaml_val(y2, 'mstar_m0', 'b'), yaml_val(y2, 'mstar_m0', 'q'))},
           'V3': {'dEg': (yaml_val(y3, 'dEg_QC_eV', 'a'), yaml_val(y3, 'dEg_QC_eV', 'p')),
                  'dEc': (yaml_val(y3, 'dEc_eV', 'a'), yaml_val(y3, 'dEc_eV', 'p')),
                  'dm': (yaml_val(y3, 'mstar_m0', 'b'), yaml_val(y3, 'mstar_m0', 'q'))}}
    res = {'points': {l: {'t_HH_nm': float(t[i]), 'dEg_eV': float(pts['dEg'][i]), 'dEc_eV': float(pts['dEc'][i]), 'dm_m0': float(pts['dm'][i])}
                      for i, l in enumerate(labs)}, 'config': {}, 'refit': {}, 'decks': {}}
    for model, d in cfg.items():
        res['config'][model] = {k: {'a': v[0][0], 'p': v[1][0], 'src': [v[0][1], v[1][1]]} for k, v in d.items()}
    # --- V2 two-point laws: from the rounded logged values (what V2 did) and from the unrounded re-derived points
    lin = np.array([0.95, 1.98])
    rounded = {'dEg': [0.900, 0.335], 'dEc': [0.848, 0.281], 'dm': [0.122, 0.04715]}
    for k in ('dEg', 'dEc', 'dm'):
        a_r, p_r = fit(lin, np.array(rounded[k]))
        a_u, p_u = fit(lin, pts[k][1:])
        a3, p3 = fit(t, pts[k])
        a2h, p2h = fit(t[1:], pts[k][1:])
        res['refit'][k] = {'V2_from_rounded_log_values': {'a': round(a_r, 5), 'p': round(p_r, 5)},
                           'V2_form_from_rederived_points': {'a': round(a_u, 5), 'p': round(p_u, 5)},
                           'fit3_rederived': {'a': round(a3, 5), 'p': round(p3, 5),
                                              'rel_residuals': [round(float(v), 4) for v in a3 * t ** -p3 / pts[k] - 1]},
                           'fit2_HH_1and2nm': {'a': round(a2h, 5), 'p': round(p2h, 5)}}
    # --- dipole sensitivity of the 0.75 nm dEc point (polar slab, no dipole correction): +- half the vacuum ramp across the gap
    ramp = abs(S['0.75']['vacuum_ramp_over_gap_meV']) / 1000
    sens = {}
    for sgn in (-1, 1):
        y = pts['dEc'].copy(); y[0] += sgn * ramp / 2
        a_, p_ = fit(t, y)
        sens[f'{sgn * ramp / 2:+.3f}'] = {'a': round(a_, 5), 'p': round(p_, 5), **{str(tt): round(a_ * tt ** -p_, 4) for tt in (2.0, 6.3, 13.2)}}
    res['dEc_0p75_dipole_sensitivity'] = {'half_ramp_eV': round(ramp / 2, 4), 'fits': sens}
    # --- deck values: recompute with the configured laws, with the re-derived laws, and compare with the deck statement
    e21_2 = S['2.0']['mass']['E21_Gamma_eV']['value']
    for model, tt, run in DECKS:
        dk = deck(run)
        c = cfg['V2' if model == 'V2' else 'V3']
        law = lambda k, x: c[k][0][0] * x ** -c[k][1][0]
        m = M_B + law('dm', tt)
        if model == 'V2':
            rf = {k: res['refit'][k]['V2_form_from_rederived_points'] for k in ('dEg', 'dEc', 'dm')}
        else:
            rf = {k: res['refit'][k]['fit3_rederived'] for k in ('dEg', 'dEc', 'dm')}
        lr = lambda k, x: rf[k]['a'] * x ** -rf[k]['p']
        m_r = M_B + lr('dm', tt)
        q2d = (model == 'C10' and tt == 2.0)
        nc_cfg = nq2d(m, tt) if q2d else nc3d(m)
        nc_re = nq2d(m_r, tt) if q2d else nc3d(m_r)
        res['decks'][f'{model}@{tt}'] = {
            'run': run, 'deck': dk,
            'from_config_law': {'eg300': round(EG_B + law('dEg', tt), 5), 'affinity': round(CHI_B - law('dEc', tt), 5),
                                'mstar': round(m, 4), 'nc300': float(f'{nc_cfg:.5e}'), 'nc_form': 'quasi-2D N2D/t' if q2d else '3-D'},
            'from_rederived_law': {'eg300': round(EG_B + lr('dEg', tt), 5), 'affinity': round(CHI_B - lr('dEc', tt), 5),
                                   'mstar': round(m_r, 4), 'nc300': float(f'{nc_re:.5e}')},
            'q2d_with_second_subband': float(f'{nq2d(m, tt, e21_2):.5e}') if q2d else None}
        dd = res['decks'][f'{model}@{tt}']
        dd['config_minus_deck'] = {'eg300_meV': round((dd['from_config_law']['eg300'] - dk['eg300']['value']) * 1000, 3),
                                   'affinity_meV': round((dd['from_config_law']['affinity'] - dk['affinity']['value']) * 1000, 3),
                                   'nc300_rel': round(dd['from_config_law']['nc300'] / dk['nc300']['value'] - 1, 5),
                                   'mstar': round(dd['from_config_law']['mstar'] - dk['mstar']['value'], 4)}
        dd['rederived_minus_deck'] = {'eg300_meV': round((dd['from_rederived_law']['eg300'] - dk['eg300']['value']) * 1000, 3),
                                      'affinity_meV': round((dd['from_rederived_law']['affinity'] - dk['affinity']['value']) * 1000, 3),
                                      'nc300_rel': round(dd['from_rederived_law']['nc300'] / dk['nc300']['value'] - 1, 5)}
    r1, r3 = f07['r_q1'], f07['r_q3_worst']
    res['hse_scaled_fit3_at'] = {str(tt): {'dEg': [round(r * cfg['V3']['dEg'][0][0] * tt ** -cfg['V3']['dEg'][1][0], 4) for r in (1, r1, r3)],
                                           'dEc': [round(r * cfg['V3']['dEc'][0][0] * tt ** -cfg['V3']['dEc'][1][0], 4) for r in (1, r1, r3)]}
                                 for tt in (2.0, 6.3, 13.2)}
    q.dump('f06_confinement_laws', res)
    print(json.dumps(res['refit'], indent=0)); print(res['dEc_0p75_dipole_sensitivity'])
    for k, v in res['decks'].items():
        print(k, {kk: vv['value'] for kk, vv in v['deck'].items()}, v['from_config_law'], v['config_minus_deck'], v['rederived_minus_deck'], v['q2d_with_second_subband'])
    print(res['hse_scaled_fit3_at'])

    # ---- figure
    fig, ax = plt.subplots(1, 3, figsize=(6.8, 2.4))
    tf = np.logspace(np.log10(0.4), np.log10(20), 200)
    names = {'dEg': r'$\Delta E_g$ (eV)', 'dEc': r'$\Delta E_c$ (eV)', 'dm': r'$\Delta m^*$ ($m_0$)'}
    for i, k in enumerate(('dEg', 'dEc', 'dm')):
        a_ = ax[i]
        a_.loglog(t, pts[k], 'o', mfc='none', color='k', label='DFT (H-H)', zorder=5)
        a_.loglog(lin, rounded[k], 'D', mfc='none', color=CYCLE[1], ms=4, label='V2 inputs (Lin labels)')
        if k != 'dm':
            a_.loglog([S['0.51']['thickness_HH_nm']['value']], [S['0.51'][k + '_eV']], 'x', color=GREY_(), label='0.51 nm (excluded)')
        else:
            a_.loglog([S['0.51']['thickness_HH_nm']['value']], [S['0.51']['dm_m0']], 'x', color=GREY_(), label='0.51 nm (excluded)')
        c2, c3 = cfg['V2'][k], cfg['V3'][k]
        a_.loglog(tf, c2[0][0] * tf ** -c2[1][0], '--', color=CYCLE[1], lw=1, label='V2 law')
        a_.loglog(tf, c3[0][0] * tf ** -c3[1][0], '-', color=CYCLE[0], lw=1, label='V3 / C10 fit3')
        if k == 'dEc':
            lo, hi = sens[min(sens)], sens[max(sens)]
            a_.fill_between(tf, lo['a'] * tf ** -lo['p'], hi['a'] * tf ** -hi['p'], color=CYCLE[0], alpha=0.15, lw=0)
        for tt in (2.0, 6.3, 13.2):
            a_.axvline(tt, color='0.6', ls=':', lw=0.7)
        a_.set_xlabel('t (nm)'); a_.set_ylabel(names[k])
        a_.set_xlim(0.4, 20)
        panel(a_, 'abc'[i], x=-0.25)
    ax[0].legend(loc='lower left', fontsize=6)
    fig.tight_layout()
    save(fig, 'fig06_confinement_laws')


def GREY_():
    return '0.45'


if __name__ == '__main__':
    main()
