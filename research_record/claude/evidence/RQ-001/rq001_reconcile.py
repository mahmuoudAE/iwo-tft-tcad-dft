#!/usr/bin/env python3
"""RQ-001: reconcile mobility and SS with the published values (Januar et al., Small Struct. 7, e202500807, 2026).

Reads the rawest file (data/experimental_raw_preserved_IWO-TFT.xlsx of the public repo at f315b78), checks it
against data/experimental_clean.csv, and re-extracts mobility and SS with candidate definitions. The numerical
methods (gm, crossings, two-point SS, power-law fit, ELR) are imported from the registered protocol code
analysis_2026-10-06_extraction/extraction.py; nothing in it is re-implemented.

Outputs (this directory): rq001_results.json, mobility_definitions.csv, mobility_scale_test.csv,
ss_methods.csv, ss_sliding_window.csv, ss_noise_mc.csv, figures/*.png.

Run: <venv python> rq001_reconcile.py <path to public repo checkout>
"""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

PUB = Path(sys.argv[1] if len(sys.argv) > 1 else r'..\..\..\..\IWO_PHYSICS_CONSTRAINED_MODEL_V1').resolve()
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(PUB / 'analysis_2026-10-06_extraction'))
import extraction as ex  # noqa: E402  (registered protocol code, commit 7a61687 / 7ce7116)

import openpyxl  # noqa: E402
from scipy.signal import savgol_filter  # noqa: E402

FILMS = (2.0, 6.3, 13.2, 31.8)
COLS = {6.3: (1, 2), 13.2: (3, 4), 31.8: (5, 6), 2.0: (7, 8)}      # provenance_from_claude_package.json
W_UM, L_UM, VD = 290.0, 20.0, ex.VD
EPS0 = 8.8541878128e-14                                           # F/cm

# Published values. 2.0 and 13.2 nm mobility: text of Sec. 2.2 and 2.8. 6.3 nm mobility and all SS values: digitised
# from Fig. 1b by digitise_fig1b.py (paper_fig1b_digitised.csv). Text: SS "60-70 mV/dec" (Sec. 2.2).
_DIG = {(r['quantity'], float(r['film_nm'])): (float(r['value']), float(r['pm_1p5px']))
        for r in csv.DictReader(open(Path(__file__).resolve().parent / 'paper_fig1b_digitised.csv'))}
PAPER_MU = {13.2: 27.4, 6.3: _DIG[('mu_max_cm2Vs', 6.3)][0], 2.0: 5.1}
PAPER_SS_FILM = {t: _DIG[('SS_mV_dec', t)] for t in (2.0, 6.3, 13.2)}
PAPER_SS = (60.0, 70.0)


def cox(layers):
    """Series capacitance (F/cm^2) of [(thickness_nm, eps_r), ...]."""
    return 1.0 / sum(t * 1e-7 / (EPS0 * e) for t, e in layers)


COX_VARIANTS = {
    'geometric HfO2 15 nm (19.57) + Al2O3 2 nm (9.0) [protocol]': cox([(15, 19.57), (2, 9.0)]),
    'HfO2 15 nm (19.57) only': cox([(15, 19.57)]),
    'HfO2 15 nm (25) + Al2O3 2 nm (9.0)': cox([(15, 25.0), (2, 9.0)]),
    'HfO2 15 nm (16) + Al2O3 2 nm (7.0)': cox([(15, 16.0), (2, 7.0)]),
    'HfO2 + Al2O3 + IWO depletion 2 nm (9.0) in series': cox([(15, 19.57), (2, 9.0), (2, 9.0)]),
    'C_eff = 0.87 C_ox (protocol 3.4)': 0.87 * cox([(15, 19.57), (2, 9.0)]),
}


# ---------------------------------------------------------------- data
def load_raw():
    wb = openpyxl.load_workbook(PUB / 'data' / 'experimental_raw_preserved_IWO-TFT.xlsx', read_only=True, data_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(min_row=2, max_row=122, values_only=True))
    out = {}
    for t, (cv, ci) in COLS.items():
        a = np.array([(float(r[cv - 1]), float(r[ci - 1])) for r in rows])
        out[t] = (a[:, 0], a[:, 1])
    return out


def check_clean(raw):
    with open(PUB / 'data' / 'experimental_clean.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    res = {}
    for t in FILMS:
        c = np.array([(float(r['vg_V']), float(r['id_A_per_um'])) for r in rows if abs(float(r['thickness_nm']) - t) < 1e-6])
        c = c[np.argsort(c[:, 0])]
        vg, i = raw[t]
        res[t] = dict(n=len(c), max_abs_dvg=float(np.max(np.abs(c[:, 0] - vg))),
                      max_rel_di=float(np.max(np.abs(c[:, 1] / i - 1))))
    return res


def w_normalisation(raw):
    """Fraction of points whose I*290 is 'round' (<= 4 significant digits); tests whether the workbook currents were
    divided by W = 290 um."""
    out = {}
    for t in FILMS:
        i = raw[t][1]
        for w in (290.0, 1.0, 20.0, 14.5):
            x = i * w
            m = x / 10 ** np.floor(np.log10(np.abs(x)))
            rnd = np.abs(m * 1e3 - np.round(m * 1e3)) < 2e-3
            out.setdefault(t, {})[str(w)] = float(np.mean(rnd))
    return out


# ---------------------------------------------------------------- mobility
def mobility_curves(vg, i, c, vd=VD):
    """All candidate mobilities (cm^2/Vs) on the measurement grid for C_ox = c and drain bias vd."""
    g = ex.gm(vg, i)
    k = ex.L_CM / ex.W_CM      # currents are per um of width, so W = 1 um (as in extraction.py)
    sig_pts = ex.gm_sigma(vg, i)[1]
    elr = ex.vth_elr(vg, i, sig_pts)
    plf = ex.pl_fit(vg, i, 1.0, 3.0)
    vcc = ex.crossing(vg, i, 1e-9, False)['v']
    out = {'mu_FE_lin (gm)': k * g / (c * vd)}
    sq = np.sqrt(np.clip(i, 0, None))
    out['mu_sat (d sqrt I/dVG)^2'] = 2 * k * np.gradient(sq, vg) ** 2 / c
    vts = {'V_th,cc(1e-9)': vcc, 'V_th,ELR': elr['v'], 'V_T power-law': plf['vt']}
    for name, vt in vts.items():
        if vt is None:
            continue
        ov = vg - vt - vd / 2
        mu = np.where(vg - vt >= vd, k * i / (c * np.where(ov > 0, ov, np.nan) * vd), np.nan)
        out[f'mu_eff, V_T = {name}'] = mu
    # Y-function (Ghibaudo): Y = I/sqrt(gm) = sqrt(k C VD mu0) (VG - VT); fit on VG >= VT,ELR + VD over the top
    m = (vg >= elr['v'] + vd) & (g > 0) & (vg <= 3.0 + 1e-9)
    yfun = dict(n=int(m.sum()))
    if m.sum() >= 5:
        y = i[m] / np.sqrt(g[m])
        p, cov = np.polyfit(vg[m], y, 1, cov=True)
        r2 = 1 - np.sum((y - np.polyval(p, vg[m])) ** 2) / np.sum((y - y.mean()) ** 2)
        mu0 = k * p[0] ** 2 / (c * vd)       # Y^2 slope = (W/L) C V_D mu0, W/L = 1/k
        vt_y = -p[1] / p[0]
        yfun.update(mu0=float(mu0), sig_mu0=float(2 * mu0 * math.sqrt(cov[0, 0]) / abs(p[0])), vt=float(vt_y), r2=float(r2),
                    range=[float(vg[m][0]), float(vg[m][-1])])
    return out, dict(elr=elr, pl=plf, vth_cc=vcc, yfun=yfun, sig_gm_pts=sig_pts)


def mu_sat_sensitivity(vg, i, c):
    """Peak of the saturation-formula mobility for several derivative estimators of sqrt(I_D) (0 <= V_G <= 3 V)."""
    k = ex.L_CM / ex.W_CM
    sq = np.sqrt(np.clip(i, 0, None))
    h = float(np.median(np.diff(vg)))
    ders = {'central (numpy.gradient), baseline': np.gradient(sq, vg),
            'forward difference': np.append(np.diff(sq) / np.diff(vg), np.nan),
            'backward difference': np.insert(np.diff(sq) / np.diff(vg), 0, np.nan),
            'Savitzky-Golay 5 pt, order 2': savgol_filter(sq, 5, 2, deriv=1, delta=h),
            'Savitzky-Golay 7 pt, order 2': savgol_filter(sq, 7, 2, deriv=1, delta=h),
            'Savitzky-Golay 9 pt, order 3': savgol_filter(sq, 9, 3, deriv=1, delta=h)}
    out = {}
    for name, d in ders.items():
        pk, v = peak(vg, 2 * k * d ** 2 / c, vmin=0.0)
        out[name] = dict(peak=pk, vg_peak=v)
    return out


def peak(vg, mu, vmin=None):
    m = np.isfinite(mu) & (vg <= 3.0 + 1e-9)
    if vmin is not None:
        m &= vg >= vmin
    if not m.any():
        return None, None
    k = int(np.nanargmax(np.where(m, mu, -np.inf)))
    return float(mu[k]), float(vg[k])


# ---------------------------------------------------------------- SS
def ss_two_point_min(vg, i, floor, kfloor):
    """Smallest SS between adjacent grid points with both currents >= kfloor*floor and below 1e-9 A/um... and below
    I_on/10, upward steps only."""
    best = None
    for k in range(len(vg) - 1):
        a, b = i[k], i[k + 1]
        if a <= 0 or b <= a or a < kfloor * floor or b > min(1e-8, i.max() / 10):
            continue
        s = 1e3 * (vg[k + 1] - vg[k]) / math.log10(b / a)
        if best is None or s < best[0]:
            best = (s, float(vg[k]), float(a))
    return best


def ss_steepest_n(vg, i, floor, n, kfloor):
    """Smallest SS from a linear regression of log10 I over n consecutive points (all >= kfloor*floor, <= I_on/10)."""
    best = None
    lg = np.log10(np.clip(i, 1e-30, None))
    for k in range(len(vg) - n + 1):
        seg = i[k:k + n]
        if seg.min() < kfloor * floor or seg.max() > min(1e-8, i.max() / 10):
            continue
        p, cov = np.polyfit(vg[k:k + n], lg[k:k + n], 1, cov=True) if n > 3 else (np.polyfit(vg[k:k + n], lg[k:k + n], 1), None)
        if p[0] <= 0:
            continue
        s = 1e3 / p[0]
        se = 1e3 * math.sqrt(cov[0, 0]) / p[0] ** 2 if cov is not None else float('nan')
        if best is None or s < best[0]:
            best = (s, se, float(vg[k]), float(seg.min()))
    return best


def sliding(vg, i, floor, is_corr):
    rows = []
    y = i - floor if is_corr else i
    for lo_exp in np.arange(-15.5, -6.99, 0.25):
        lo, hi = 10 ** lo_exp, 10 ** (lo_exp + 1)
        if hi > i.max() / 3:
            break
        r = ex.ss_window(vg, np.where(y > 0, y, 1e-30), lo, hi, False)
        if r['ss'] is None:
            continue
        rows.append(dict(lo=lo, hi=hi, lo_over_floor=lo / floor, ss=r['ss'], sig=r['sig']))
    return rows


def noise_mc(vg, i, floor, n_mc=2000, seed=1):
    """Bias of the minimum-SS estimators on a noise-free reference curve plus Gaussian noise in log10 I.
    Reference: Savitzky-Golay smoothing of log10 I (window 9, order 3). Noise: sigma_log from ex.noise_log at 1e-12
    and 1e-10 A/um (mean of available levels)."""
    lg = np.log10(i)
    ref = savgol_filter(lg, 9, 3)
    sig = []
    for lvl in (1e-12, 1e-11, 1e-10):
        ks = ex.upward_crossings(vg, i, lvl)
        if ks and lvl > 3 * floor:
            sig.append(ex.noise_log(vg, i, lvl, ks[-1]))
    s_log = float(np.mean(sig)) if sig else float('nan')
    iref = 10 ** ref
    true2 = ss_two_point_min(vg, iref, floor, 10)
    true5 = ss_steepest_n(vg, iref, floor, 5, 10)
    rng = np.random.default_rng(seed)
    m2, m5 = [], []
    for _ in range(n_mc):
        ii = 10 ** (ref + rng.normal(0, s_log, len(ref)))
        a, b = ss_two_point_min(vg, ii, floor, 10), ss_steepest_n(vg, ii, floor, 5, 10)
        if a:
            m2.append(a[0])
        if b:
            m5.append(b[0])
    q = lambda x: [float(v) for v in np.percentile(x, [2.5, 50, 97.5])]
    return dict(sigma_log10=s_log, ref_two_point=true2[0] if true2 else None, ref_steepest5=true5[0] if true5 else None,
                mc_two_point_p2p5_p50_p97p5=q(m2), mc_steepest5_p2p5_p50_p97p5=q(m5),
                observed_two_point=(ss_two_point_min(vg, i, floor, 10) or [None])[0],
                observed_steepest5=(ss_steepest_n(vg, i, floor, 5, 10) or [None])[0])


# ---------------------------------------------------------------- main
def main():
    raw = load_raw()
    res = dict(public_repo=str(PUB), clean_vs_raw=check_clean(raw), w_normalisation=w_normalisation(raw),
               cox_variants={k: v for k, v in COX_VARIANTS.items()}, films={})
    c0 = ex.COX
    assert abs(c0 / COX_VARIANTS['geometric HfO2 15 nm (19.57) + Al2O3 2 nm (9.0) [protocol]'] - 1) < 1e-6
    mob_rows, ss_rows, slide_rows, mc_rows = [], [], [], []
    curves = {}
    for t in FILMS:
        vg, i = raw[t]
        floor = ex.off_floor(vg, i)
        f = res['films'][str(t)] = dict(floor=floor, I_on=float(i[-1]))
        mus, aux = mobility_curves(vg, i, c0)
        curves[t] = (vg, i, mus, aux)
        f['elr'] = {k: aux['elr'][k] for k in ('v', 'vg_star', 'gm_max', 'sweep_limited', 'linear_regime')}
        f['power_law'] = {k: aux['pl'][k] for k in ('vt', 'mu0', 'gamma', 'rms_log10', 'at_bound')}
        f['vth_cc'] = aux['vth_cc']
        f['yfun'] = aux['yfun']
        f['mu_sat_sensitivity'] = mu_sat_sensitivity(vg, i, c0)
        # validity of the saturation formula at its peak (needs V_G - V_T <= V_D) and the protocol's channel
        # mobility (M2, power law, valid in both regimes) at the same V_G and at 1, 2, 3 V
        vpk = peak(vg, mus['mu_sat (d sqrt I/dVG)^2'], vmin=0.0)[1]
        f['mu_sat_peak_validity'] = dict(
            vg_peak=vpk, overdrive_vs_VT_powerlaw=vpk - aux['pl']['vt'],
            overdrive_vs_VT_ELR=vpk - aux['elr']['v'], VD=VD,
            mu_ch_powerlaw_at_peak=float(ex.mu_ch(np.array([vpk]), aux['pl'])[0]),
            mu_ch_powerlaw_at_1_2_3V=[float(x) for x in ex.mu_ch(np.array([1.0, 2.0, 3.0]), aux['pl'])],
            note='mu_ch extrapolated outside the 1-3 V fit range when vg_peak < 1 V')
        f['mobility'] = {}
        for name, mu in mus.items():
            pk, vpk = peak(vg, mu, vmin=0.0)
            at3 = float(mu[-1]) if np.isfinite(mu[-1]) else None
            f['mobility'][name] = dict(peak=pk, vg_peak=vpk, at_3V=at3)
            mob_rows.append(dict(film_nm=t, definition=name, peak_cm2Vs=pk, vg_peak_V=vpk, at_3V_cm2Vs=at3,
                                 paper=PAPER_MU.get(t)))
        if aux['yfun'].get('mu0') is not None:
            mob_rows.append(dict(film_nm=t, definition='Y-function mu0', peak_cm2Vs=aux['yfun']['mu0'], vg_peak_V=None,
                                 at_3V_cm2Vs=None, paper=PAPER_MU.get(t)))
        if t == 31.8:
            continue
        # SS
        a1 = 2.15e-5 * i[-1]
        cand = {
            'registered fixed window 5e-11..5e-10 (S1)': ex.ss_window(vg, i, 5e-11, 5e-10, False),
            'A1 normalised window [2.15e-5, 2.15e-4] I_on': ex.ss_window(vg, i, a1, 10 * a1, False),
        }
        for name, r in cand.items():
            ss_rows.append(dict(film_nm=t, method=name, ss_mV_dec=r['ss'], sig=r.get('sig'), at_V=None, lowest_I=None, kfloor=None))
        for kf in (1, 3, 10):
            b = ss_two_point_min(vg, i, floor, kf)
            if b:
                ss_rows.append(dict(film_nm=t, method='two-point minimum (adjacent points)', ss_mV_dec=b[0], sig=None,
                                    at_V=b[1], lowest_I=b[2], kfloor=kf))
            for n in (3, 4, 5, 7):
                b = ss_steepest_n(vg, i, floor, n, kf)
                if b:
                    ss_rows.append(dict(film_nm=t, method=f'steepest {n} points (regression)', ss_mV_dec=b[0], sig=b[1],
                                        at_V=b[2], lowest_I=b[3], kfloor=kf))
        for corr in (False, True):
            for r in sliding(vg, i, floor, corr):
                slide_rows.append(dict(film_nm=t, floor_corrected=corr, **r))
        # one-decade window whose lower edge sits a fixed multiple of the floor above it
        for mult in (2, 3, 5, 10, 30, 100):
            r = ex.ss_window(vg, i, mult * floor, 10 * mult * floor, False)
            ss_rows.append(dict(film_nm=t, method=f'one-decade window from {mult} x floor', ss_mV_dec=r['ss'], sig=r.get('sig'),
                                at_V=None, lowest_I=mult * floor, kfloor=mult))
        mc = noise_mc(vg, i, floor)
        f['noise_mc'] = mc
        mc_rows.append(dict(film_nm=t, **{k: (json.dumps(v) if isinstance(v, list) else v) for k, v in mc.items()}))
        # where does local SS <= 70 mV/dec occur?
        ii, ssl = ex.local_ss(vg, i)
        m = ssl <= 70
        f['local_ss_le_70'] = dict(n_points=int(m.sum()), currents=[float(x) for x in ii[m]],
                                   currents_over_floor=[float(x / floor) for x in ii[m]], values=[float(x) for x in ssl[m]])
        # floor-corrected (I_D - floor, the analogue of the paper's Eq. 1a with a constant I_off): steepest n points
        icorr = np.where(i - floor > 0, i - floor, 1e-30)
        for kf in (3, 10):
            for n in (3, 4, 5, 7):
                b = ss_steepest_n(vg, icorr, floor, n, kf)
                if b:
                    ss_rows.append(dict(film_nm=t, method=f'floor-corrected steepest {n} points', ss_mV_dec=b[0], sig=b[1],
                                        at_V=b[2], lowest_I=b[3], kfloor=kf))

    # scale test: constant-factor explanations (C_ox, V_D, W/L) need the same mu_paper/mu_ours ratio in every film
    scale_rows = []
    for name in list(curves[2.0][2].keys()) + ['Y-function mu0']:
        vals = {}
        for t in (2.0, 6.3, 13.2):
            if name == 'Y-function mu0':
                vals[t] = res['films'][str(t)]['yfun'].get('mu0')
            else:
                vals[t] = res['films'][str(t)]['mobility'][name]['peak']
        if any(v is None for v in vals.values()):
            continue
        k = {t: PAPER_MU[t] / vals[t] for t in vals}
        kb = math.sqrt(k[2.0] * k[13.2])          # best common factor on the two values stated in the text
        scale_rows.append(dict(definition=name, ours_2p0=vals[2.0], ours_6p3=vals[6.3], ours_13p2=vals[13.2],
                               ratio_13p2_over_2p0_ours=vals[13.2] / vals[2.0], ratio_13p2_over_2p0_paper=27.4 / 5.1,
                               k_2p0=k[2.0], k_6p3=k[6.3], k_13p2=k[13.2],
                               k_spread_13p2_over_2p0=k[13.2] / k[2.0], k_best_2p0_13p2=kb,
                               max_dev_after_k_best_pct=100 * max(abs(kb * vals[t] / PAPER_MU[t] - 1) for t in (2.0, 13.2)),
                               dev_6p3_after_k_best_pct=100 * (kb * vals[6.3] / PAPER_MU[6.3] - 1),
                               max_dev_without_scaling_pct=100 * max(abs(vals[t] / PAPER_MU[t] - 1) for t in (2.0, 13.2))))
    res['scale_test'] = scale_rows
    # C_ox needed for the gm-based peak to hit each paper value
    res['cox_needed_for_gm_peak'] = {str(t): c0 * res['films'][str(t)]['mobility']['mu_FE_lin (gm)']['peak'] / PAPER_MU[t]
                                     for t in (2.0, 6.3, 13.2)}
    res['vd_needed_for_gm_peak_at_protocol_cox'] = {str(t): VD * res['films'][str(t)]['mobility']['mu_FE_lin (gm)']['peak'] / PAPER_MU[t]
                                                    for t in (2.0, 6.3, 13.2)}

    # SS scoring against the digitised Fig. 1b values: every (method, kfloor) with a value in all three films
    score = []
    keys = sorted({(r['method'], r['kfloor']) for r in ss_rows}, key=str)
    for mth, kf in keys:
        v = {r['film_nm']: r['ss_mV_dec'] for r in ss_rows if r['method'] == mth and r['kfloor'] == kf}
        if any(v.get(t) is None for t in (2.0, 6.3, 13.2)):
            continue
        dev = {t: 100 * (v[t] / PAPER_SS_FILM[t][0] - 1) for t in (2.0, 6.3, 13.2)}
        score.append(dict(method=mth, kfloor=kf, ss_2p0=v[2.0], ss_6p3=v[6.3], ss_13p2=v[13.2],
                          dev_2p0_pct=dev[2.0], dev_6p3_pct=dev[6.3], dev_13p2_pct=dev[13.2],
                          max_abs_dev_pct=max(abs(x) for x in dev.values()),
                          below_thermal_limit=any(v[t] < ex.S_TH for t in v)))
    score.sort(key=lambda r: r['max_abs_dev_pct'])
    res['ss_scoring'] = dict(paper_digitised=PAPER_SS_FILM, n_methods=len(score), rows=score)

    def wcsv(name, rows):
        with open(OUT / name, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    wcsv('mobility_definitions.csv', mob_rows)
    wcsv('mobility_scale_test.csv', scale_rows)
    wcsv('ss_methods.csv', ss_rows)
    wcsv('ss_sliding_window.csv', slide_rows)
    wcsv('ss_noise_mc.csv', mc_rows)
    wcsv('ss_method_scoring.csv', score)
    with open(OUT / 'rq001_results.json', 'w') as fh:
        json.dump(res, fh, indent=1, default=lambda o: None)
    make_figures(curves, slide_rows, res)


def make_figures(curves, slide_rows, res):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'Arial', 'font.size': 10, 'axes.linewidth': 1.0, 'xtick.direction': 'in',
                         'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True})
    (OUT / 'figures').mkdir(exist_ok=True)
    col = {2.0: '#000000', 6.3: '#d62728', 13.2: '#1f77b4'}
    # Fig 1: mobility definitions per film
    fig, axs = plt.subplots(1, 3, figsize=(10, 3.3))
    sty = {'mu_FE_lin (gm)': ('k', '-'), 'mu_sat (d sqrt I/dVG)^2': ('#d62728', '-'),
           'mu_eff, V_T = V_th,cc(1e-9)': ('#1f77b4', '--'), 'mu_eff, V_T = V_th,ELR': ('#2ca02c', '--'),
           'mu_eff, V_T = V_T power-law': ('#9467bd', ':')}
    for ax, t, lab in zip(axs, (2.0, 6.3, 13.2), 'abc'):
        vg, i, mus, aux = curves[t]
        for name, (c, ls) in sty.items():
            if name in mus:
                m = (vg >= 0) & np.isfinite(mus[name])
                ax.plot(vg[m], mus[name][m], color=c, ls=ls, lw=1.3)
        if aux['yfun'].get('mu0'):
            ax.plot([aux['yfun']['range'][0], 3.0], [aux['yfun']['mu0']] * 2, color='#ff7f0e', lw=2.0)
        ax.axhline(PAPER_MU[t], color='0.5', lw=1.0, ls='-.')
        ax.set_xlim(0, 3.05)
        ax.set_ylim(0, None)
        ax.set_xlabel('$V_G$ (V)')
        ax.set_title(f'({lab})', loc='left', fontweight='bold')
    axs[0].set_ylabel('mobility (cm$^2$ V$^{-1}$ s$^{-1}$)')
    fig.tight_layout()
    fig.savefig(OUT / 'figures' / 'fig1_mobility_definitions.png', dpi=200)
    plt.close(fig)
    # Fig 2: sliding one-decade SS vs lower edge / floor
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.3), sharey=True)
    for ax, corr, lab in zip(axs, (False, True), 'ab'):
        for t in (2.0, 6.3, 13.2):
            rr = [r for r in slide_rows if r['film_nm'] == t and r['floor_corrected'] == corr
                  and (not corr or r['lo_over_floor'] >= 1.0)]
            x = [r['lo_over_floor'] for r in rr]
            ax.errorbar(x, [r['ss'] for r in rr], yerr=[r['sig'] for r in rr], color=col[t], marker='o', ms=3, lw=1, capsize=0)
        for t in (2.0, 6.3, 13.2):
            ax.axhline(PAPER_SS_FILM[t][0], color=col[t], ls='--', lw=1)
        ax.axhline(ex.S_TH, color='0.4', ls=':', lw=1)
        ax.set_xscale('log')
        ax.set_xlabel('lower window edge / off-state floor')
        ax.set_title(f'({lab})', loc='left', fontweight='bold')
        ax.set_ylim(0, 250)
    axs[0].set_ylabel('SS, one-decade window (mV dec$^{-1}$)')
    fig.tight_layout()
    fig.savefig(OUT / 'figures' / 'fig2_ss_sliding_window.png', dpi=200)
    plt.close(fig)
    # Fig 3: local SS vs I_D, raw and floor corrected
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.3), sharey=True)
    for ax, corr, lab in zip(axs, (False, True), 'ab'):
        for t in (2.0, 6.3, 13.2):
            vg, i, _, _ = curves[t]
            fl = res['films'][str(t)]['floor']
            if corr:      # only where I_D > 2 x floor, so that I_D - floor is defined and positive
                keep = np.arange(len(i)) >= np.max(np.nonzero(i <= 2 * fl)[0]) + 1
                ii, s = ex.local_ss(vg[keep], i[keep] - fl)
            else:
                ii, s = ex.local_ss(vg, i)
            m = (ii > 1e-16) & (ii < 1e-6)
            ax.plot(ii[m], s[m], color=col[t], marker='o', ms=2.5, lw=0.8)
        for t in (2.0, 6.3, 13.2):
            ax.axhline(PAPER_SS_FILM[t][0], color=col[t], ls='--', lw=1)
        ax.axhline(ex.S_TH, color='0.4', ls=':', lw=1)
        ax.set_xscale('log')
        ax.set_ylim(0, 300)
        ax.set_xlabel('$I_D$ (A $\\mu$m$^{-1}$)' if not corr else '$I_D$ - floor (A $\\mu$m$^{-1}$)')
        ax.set_title(f'({lab})', loc='left', fontweight='bold')
    axs[0].set_ylabel('local SS (mV dec$^{-1}$)')
    fig.tight_layout()
    fig.savefig(OUT / 'figures' / 'fig3_local_ss.png', dpi=200)
    plt.close(fig)


if __name__ == '__main__':
    main()
