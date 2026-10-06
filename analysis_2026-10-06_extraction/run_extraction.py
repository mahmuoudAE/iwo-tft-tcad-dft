#!/usr/bin/env python3
"""Driver for PROTOCOL.md. Measured (data/experimental_clean.csv) and TCAD (V1 final runs 0038 / 0039 / 0040)
transfer curves at V_D = 0.7 V -> threshold voltages, SS in the common window, mobility versus V_G, the comparison
TCAD - measured, and the machine-readable outputs results.json, results_table.csv, mobility_vs_vg.csv.
"""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(HERE))
import extraction as ex  # noqa: E402

FILMS = (2.0, 6.3, 13.2)
RUNS = {2.0: ('0038', 1.0), 6.3: ('0039', 11.581987 / 11.41), 13.2: ('0040', 61.604561 / 60.39)}
I_CC, I_CC10 = 1e-9, 5e-10
WIN = (5e-11, 5e-10)
SHIFTED = {'-0.25 dec': (WIN[0] * 10 ** -0.25, WIN[1] * 10 ** -0.25), '+0.25 dec': (WIN[0] * 10 ** 0.25, WIN[1] * 10 ** 0.25)}
FIT_PRIMARY, FIT_ALT = (1.0, 3.0), ((1.25, 3.0), (1.5, 3.0), (1.0, 2.5))
VG_REPORT = (1.0, 1.5, 2.0, 2.5, 3.0)
# calibration status of each TCAD quantity (PROTOCOL section 2)
STATUS = {'vth_cc': 'fitted (Q_f)', 'vth_cc_10nA': 'fitted (Q_f, adjacent level)', 'vt_pl': 'constrained (Q_f shift)',
          'gap_pl': 'not fitted', 'vth_elr': 'constrained (Q_f shift)', 'gap_elr': 'not fitted',
          'ss': {2.0: 'fitted (W_TA, N_t at 2 nm)', 6.3: 'not fitted (N_t law)', 13.2: 'not fitted (N_t law)'},
          'gamma': 'not fitted', 'mu0': 'constrained (scale fitted on I_on)', 'mu_fe': 'not fitted (scale from I_on fit)',
          'mu_ch': 'constrained (scale fitted on I_on)'}


def load_measured():
    with open(PKG / 'data' / 'experimental_clean.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    out = {}
    for t in FILMS:
        a = np.array([(float(r['vg_V']), float(r['id_A_per_um'])) for r in rows if abs(float(r['thickness_nm']) - t) < 1e-6])
        a = a[np.argsort(a[:, 0])]
        out[t] = (a[:, 0], a[:, 1])
    return out


def probe(path):
    vals = []
    for line in open(path):
        p = line.split()
        if len(p) == 2:
            try:
                vals.append(float(p[1]))
            except ValueError:
                pass
    return vals


def load_tcad(t):
    rid, s = RUNS[t]
    d = next((PKG / 'results' / 'runs').glob(f'run_{rid}_*'))
    with open(d / 'terminal_currents.csv', newline='') as f:
        a = np.array([(float(r['vg_V']), float(r['id_A_per_um'])) for r in csv.DictReader(f)])
    a = a[np.argsort(a[:, 0])]
    with open(d / 'comparison.csv', newline='') as f:
        c = np.array([(float(r['vg_V']), float(r['atlas_A_per_um'])) for r in csv.DictReader(f)])
    vg, i, vgm, im = a[:, 0], a[:, 1] * s, c[:, 0], c[:, 1] * s
    # native points that lie on the measurement grid must equal comparison.csv (which interpolates in between)
    k = np.isin(np.round(vg, 4), np.round(vgm, 4)) & (np.abs(i) > 1e-15)
    rel = float(np.max(np.abs(np.interp(vg[k], vgm, im) / i[k] - 1)))
    mob = probe(d / 'chan_mobility_vg.dat')
    return dict(run=d.name, scale=s, vg=vg, i=i, vg_m=vgm, i_m=im, check_rel=rel, mu_n=mob[0] * s,
                mu_n_constant=bool(max(mob) - min(mob) < 1e-9 * max(mob)))


def floor_with_sigma(vg, i):
    off = i[(vg >= -2) & (vg <= -0.5)]
    return float(np.median(off)), float(1.2533 * np.std(off, ddof=1) / math.sqrt(len(off)))


def ss_rule(vg, i, lo, hi, is_sim, floor, sig_floor):
    raw = ex.ss_window(vg, i, lo, hi, is_sim)
    res = dict(window=[lo, hi], raw=raw, primary='raw', ss=raw['ss'], sig=raw['sig'])
    if is_sim:
        return res
    res['floor_ratio'] = lo / floor
    res['admissible'] = bool(lo / floor >= 10)
    if not res['admissible']:
        cor = ex.ss_window(vg, i - floor, lo, hi, False)
        hi_f = ex.ss_window(vg, i - (floor + sig_floor), lo, hi, False)['ss']
        lo_f = ex.ss_window(vg, i - (floor - sig_floor), lo, hi, False)['ss']
        s_fl = abs(hi_f - lo_f) / 2
        res.update(corrected=cor, sig_floor_term=s_fl, primary='floor-corrected', ss=cor['ss'], sig=math.hypot(cor['sig'], s_fl))
    return res


def analyse(vg, i, is_sim, floor, sig_floor, vg_fit, i_fit):
    r = dict(vth_cc=ex.crossing(vg, i, I_CC, is_sim), vth_cc_10nA=ex.crossing(vg, i, I_CC10, is_sim))
    r['ss'] = ss_rule(vg, i, *WIN, is_sim, floor, sig_floor)
    r['ss_shifted'] = {k: ss_rule(vg, i, lo, hi, is_sim, floor, sig_floor) for k, (lo, hi) in SHIFTED.items()}
    g = ex.gm(vg, i)
    if is_sim:
        # numerical budget (0.7 %) and the finite-difference grid: native solver grid vs the 0.05 V measurement grid
        g_grid = np.interp(vg, vg_fit, ex.gm(vg_fit, i_fit))
        sig_pts = np.hypot(ex.SIM_REL_GM * np.abs(g), np.abs(g - g_grid))
        r['sig_gm_global_protocol'] = None
    else:
        r['sig_gm_global_protocol'], sig_pts = ex.gm_sigma(vg, i)
    r['elr'] = ex.vth_elr(vg, i, sig_pts)
    mu = ex.MU_FACTOR * g
    pts = {}
    for v in VG_REPORT:
        k = int(np.argmin(np.abs(vg - v)))
        assert abs(vg[k] - v) < 1e-6, (v, vg[k])
        edge = k in (0, len(vg) - 1)
        pts[f'{v:.1f}'] = dict(mu_fe=float(mu[k]), sig=float(ex.MU_FACTOR * sig_pts[k]), one_sided=edge,
                               sig_global_protocol=None if is_sim else float(ex.MU_FACTOR * r['sig_gm_global_protocol']))
    r['mu_fe'] = pts
    r['mu_fe_curve'] = [(float(a), float(b)) for a, b in zip(vg, mu) if 0.95 <= a <= 3.0 + 1e-9]
    prim = ex.pl_fit(vg_fit, i_fit, *FIT_PRIMARY)
    alts = [ex.pl_fit(vg_fit, i_fit, lo, hi) for lo, hi in FIT_ALT]
    for p in ('vt', 'mu0', 'gamma'):
        syst = max(abs(a[p] - prim[p]) for a in alts)
        prim[f'syst_{p}'] = syst
        prim[f'tot_{p}'] = math.hypot(prim[f'sig_{p}'], syst)
    r['pl'], r['pl_alt'] = prim, alts
    vr = np.array(VG_REPORT)
    m0, s0 = ex.mu_ch(vr, prim), ex.mu_ch_sigma(vr, prim)
    syst = np.nanmax(np.abs(np.array([ex.mu_ch(vr, a) for a in alts]) - m0), axis=0)
    r['mu_ch'] = {f'{v:.1f}': dict(mu_ch=float(m0[j]), sig_stat=float(s0[j]), syst=float(syst[j]),
                                   sig=float(math.hypot(s0[j], syst[j])) if np.isfinite(m0[j]) else None,
                                   linear_regime=bool(v - prim['vt'] >= ex.VD)) for j, v in enumerate(VG_REPORT)}
    r['gap_pl'] = prim['vt'] - r['vth_cc']['v']
    r['gap_elr'] = r['elr']['v'] - r['vth_cc']['v']
    return r


def verdict(d, s):
    return 'consistent' if abs(d) <= 2 * s else 'differs'


def main():
    meas = load_measured()
    out = dict(protocol='PROTOCOL.md (commit 7a61687)', constants=dict(Cox_F_cm2=ex.COX, L_um=20, W_norm_um=1, VD_V=ex.VD,
               T_K=ex.T, S_th_mV_dec=ex.S_TH), films={})
    rows, mob_rows = [], []
    for t in FILMS:
        vg, i = meas[t]
        fl, sfl = floor_with_sigma(vg, i)
        tc = load_tcad(t)
        m = analyse(vg, i, False, fl, sfl, vg, i)
        s = analyse(tc['vg'], tc['i'], True, fl, sfl, tc['vg_m'], tc['i_m'])
        out['films'][str(t)] = dict(floor=fl, sig_floor=sfl, tcad=dict(run=tc['run'], scale=tc['scale'], mu_n=tc['mu_n'],
                                    mu_n_constant=tc['mu_n_constant'], native_vs_comparison_max_rel=tc['check_rel']),
                                    measured=m, simulated=s)

        def add(metric, unit, mv, ms, sv, ss, status, note=''):
            d = sv - mv
            sd = math.hypot(ms, ss)
            rows.append(dict(film_nm=t, metric=metric, unit=unit, measured=mv, sig_measured=ms, tcad=sv, sig_tcad=ss,
                             delta_tcad_minus_measured=d, sig_delta=sd, verdict=verdict(d, sd), tcad_status=status, note=note))
        add('Vth,cc at 1e-9 A/um (20 nA W/L)', 'V', m['vth_cc']['v'], m['vth_cc']['sig'], s['vth_cc']['v'], s['vth_cc']['sig'], STATUS['vth_cc'])
        add('Vth,cc at 5e-10 A/um (10 nA W/L)', 'V', m['vth_cc_10nA']['v'], m['vth_cc_10nA']['sig'], s['vth_cc_10nA']['v'],
            s['vth_cc_10nA']['sig'], STATUS['vth_cc_10nA'])
        add('V_T power-law GCA', 'V', m['pl']['vt'], m['pl']['tot_vt'], s['pl']['vt'], s['pl']['tot_vt'], STATUS['vt_pl'])
        add('V_T - Vth,cc (shape)', 'V', m['gap_pl'], math.hypot(m['pl']['tot_vt'], m['vth_cc']['sig']), s['gap_pl'],
            math.hypot(s['pl']['tot_vt'], s['vth_cc']['sig']), STATUS['gap_pl'])
        flags = lambda e: ', '.join([x for x, on in (('sweep-limited', e['sweep_limited']),
                                                     ('not linear regime', not e['linear_regime'])) if on]) or 'ok'
        add('Vth,ELR (with -VD/2)', 'V', m['elr']['v'], m['elr']['sig'], s['elr']['v'], s['elr']['sig'], STATUS['vth_elr'],
            f"measured: {flags(m['elr'])} (VG* {m['elr']['vg_star']:.2f} V); TCAD: {flags(s['elr'])} (VG* {s['elr']['vg_star']:.2f} V)")
        add('Vth,ELR - Vth,cc (shape)', 'V', m['gap_elr'], math.hypot(m['elr']['sig'], m['vth_cc']['sig']), s['gap_elr'],
            math.hypot(s['elr']['sig'], s['vth_cc']['sig']), STATUS['gap_elr'], 'sweep-limited where flagged above')
        add('SS [5e-11, 5e-10] A/um', 'mV/dec', m['ss']['ss'], m['ss']['sig'], s['ss']['ss'], s['ss']['sig'], STATUS['ss'][t],
            f"measured value {m['ss']['primary']}; lower edge / floor = {m['ss']['floor_ratio']:.1f}")
        for k in SHIFTED:
            a, b = m['ss_shifted'][k], s['ss_shifted'][k]
            add(f'SS window shifted {k}', 'mV/dec', a['ss'], a['sig'], b['ss'], b['sig'], STATUS['ss'][t],
                f"measured value {a['primary']}; lower edge / floor = {a['floor_ratio']:.1f}")
        a, b = m['ss'], s['ss']
        add('N_SS = (SS/S_th - 1) Cox/q from the SS window', 'cm-2 eV-1', ex.n_ss(a['ss']), a['sig'] / ex.S_TH * ex.COX / ex.Q,
            ex.n_ss(b['ss']), b['sig'] / ex.S_TH * ex.COX / ex.Q, STATUS['ss'][t], 'upper bound on the interface-trap density')
        add('gamma (power-law exponent)', '-', m['pl']['gamma'], m['pl']['tot_gamma'], s['pl']['gamma'], s['pl']['tot_gamma'], STATUS['gamma'])
        add('mu0 (channel mobility at 1 V overdrive)', 'cm2/Vs', m['pl']['mu0'], m['pl']['tot_mu0'], s['pl']['mu0'], s['pl']['tot_mu0'], STATUS['mu0'])
        # post hoc (not in PROTOCOL 3.5): the fit-range systematic is common to data and TCAD, so it is taken on the
        # paired difference (same fit range for both) instead of adding the two systematics in quadrature
        paired = {}
        for p, lab, unit in (('vt', 'V_T power-law GCA', 'V'), ('gamma', 'gamma (power-law exponent)', '-'),
                             ('mu0', 'mu0 (channel mobility at 1 V overdrive)', 'cm2/Vs')):
            d0 = s['pl'][p] - m['pl'][p]
            ds = [sa[p] - ma[p] for sa, ma in zip(s['pl_alt'], m['pl_alt'])]
            sd = math.hypot(math.hypot(s['pl'][f'sig_{p}'], m['pl'][f'sig_{p}']), max(abs(x - d0) for x in ds))
            paired[p] = dict(delta=d0, delta_alt_ranges=ds, sig=sd, verdict=verdict(d0, sd))
            rows.append(dict(film_nm=t, metric=f'{lab}: paired fit-range difference (post hoc)', unit=unit, measured=m['pl'][p],
                             sig_measured=m['pl'][f'sig_{p}'], tcad=s['pl'][p], sig_tcad=s['pl'][f'sig_{p}'],
                             delta_tcad_minus_measured=d0, sig_delta=sd, verdict=verdict(d0, sd), tcad_status=STATUS.get(p, STATUS['vt_pl']),
                             note='differences for fit ranges 1.25-3 / 1.5-3 / 1.0-2.5 V: ' + ' / '.join(f'{x:+.3g}' for x in ds)))
        out['films'][str(t)]['paired_powerlaw'] = paired
        for v in VG_REPORT:
            a, b = m['mu_fe'][f'{v:.1f}'], s['mu_fe'][f'{v:.1f}']
            add(f'mu_FE at VG = {v:.1f} V', 'cm2/Vs', a['mu_fe'], a['sig'], b['mu_fe'], b['sig'], STATUS['mu_fe'],
                'linear regime (measured fit)' if m['mu_ch'][f'{v:.1f}']['linear_regime'] else 'below V_T + V_D: normalised transconductance, not a mobility')
        for v in VG_REPORT:
            a, b = m['mu_ch'][f'{v:.1f}'], s['mu_ch'][f'{v:.1f}']
            if a['sig'] is not None and b['sig'] is not None:
                add(f'mu_ch at VG = {v:.1f} V (power-law GCA)', 'cm2/Vs', a['mu_ch'], a['sig'], b['mu_ch'], b['sig'], STATUS['mu_ch'])
        for src, r, grid in (('measured', m, vg), ('TCAD', s, tc['vg'])):
            for v_, mu_ in r['mu_fe_curve']:
                mob_rows.append(dict(film_nm=t, source=src, vg_V=v_, mu_FE_cm2Vs=mu_,
                                     mu_ch_powerlaw_cm2Vs=float(ex.mu_ch(np.array([v_]), r['pl'])[0]),
                                     linear_regime=bool(v_ - r['pl']['vt'] >= ex.VD)))
    out['comparison'] = rows
    (HERE / 'results.json').write_text(json.dumps(out, indent=1, default=float))
    with open(HERE / 'results_table.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with open(HERE / 'mobility_vs_vg.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(mob_rows[0].keys())); w.writeheader(); w.writerows(mob_rows)
    for r in rows:
        print(f"{r['film_nm']:5.1f} {r['metric'][:44]:44s} meas {r['measured']:10.4g} +-{r['sig_measured']:.2g} | TCAD {r['tcad']:10.4g} "
              f"+-{r['sig_tcad']:.2g} | D {r['delta_tcad_minus_measured']:+.4g} +-{r['sig_delta']:.2g} {r['verdict']:10s} | {r['tcad_status']} | {r['note']}")
    for t in FILMS:
        f_ = out['films'][str(t)]
        print(t, 'floor', f"{f_['floor']:.3e} +- {f_['sig_floor']:.1e}", 'TCAD', f_['tcad'])


if __name__ == '__main__':
    main()
