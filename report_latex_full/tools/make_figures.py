#!/usr/bin/env python3
"""Stage 0b: build every registry figure (CONVENTIONS section 7) from real run/data files.
  python tools/make_figures.py [stem ...]
Writes figures/<stem>.pdf + figures/png/<stem>.png and figures/MANIFEST.md (sources and key numbers)."""
from __future__ import annotations
import csv, json, shutil, sys, traceback
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'figures' / 'src'))
from style import *            # noqa: F401,F403  (plt, FILM, save, panel_label, ...)
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, str(PKG / 'scripts'))
from extract_metrics import metrics   # the package's own extractor (same as for data)

ANA = PKG / 'analysis_2026-09-25'; MAN = []
Q = 1.602176634e-19; COX = 8.955e-7; L_CM = 20e-4; VD = 0.7; KB = 8.617333262e-5
S39 = 11.581987 / 11.41; S40 = 61.604561 / 60.39      # exact mobility rescale of B2/B3 to the recalibrated mu

def meas(t):
    a = np.array([(float(r['vg_V']), float(r['id_A_per_um'])) for r in csv.DictReader(DATA.open()) if abs(float(r['thickness_nm']) - t) < 1e-6])
    return a[:, 0], a[:, 1]

def rdir(rid): return next(RUNS.glob(f'run_{rid}_*'))
def sim(rid, scale=1.0):
    a = np.array([(float(r['vg_V']), float(r['atlas_A_per_um'])) for r in csv.DictReader((rdir(rid) / 'comparison.csv').open())])
    return a[:, 0], a[:, 1] * scale
def met(vg, i, is_sim=True, t=2.0): return metrics(vg, np.asarray(i, float), is_sim, t)
def pos(i): return np.where(np.asarray(i) > 0, i, np.nan)
def logax(ax, lo=1e-15, hi=1e-5, xl=(-1.5, 3.0)):
    ax.set_yscale('log'); ax.set_ylim(lo, hi); ax.set_xlim(*xl); ax.set_xlabel(r'$V_G$ (V)'); ax.set_ylabel(r'$I_D$ (A/$\mu$m)')
def note(stem, text): MAN.append(f'## {stem}\n{text}\n')
def mu_lin(vg, i): return np.gradient(i, vg) * 1e4 * L_CM / (COX * VD)
def mu_sat(vg, i): return 2 * L_CM * np.gradient(np.sqrt(np.clip(i, 0, None) * 1e4), vg) ** 2 / COX
def floor(vg, i): return float(np.median(i[(vg >= -2) & (vg <= -0.5)]))
def fixed_ss(vg, i, lo, hi):
    ok = i > 0; li, v = np.log10(i[ok]), vg[ok]
    def at(x):
        k = np.where((li[:-1] < x) & (li[1:] >= x))[0]
        return None if not len(k) else v[k[0]] + (x - li[k[0]]) * (v[k[0] + 1] - v[k[0]]) / (li[k[0] + 1] - li[k[0]])
    a, b = at(np.log10(lo)), at(np.log10(hi)); return None if a is None or b is None else 1e3 * (b - a) / np.log10(hi / lo)
def ticks_t(a, ts):
    from matplotlib.ticker import NullFormatter, FixedLocator, FixedFormatter
    a.xaxis.set_major_locator(FixedLocator(ts)); a.xaxis.set_major_formatter(FixedFormatter([f'{x:g}' for x in ts])); a.xaxis.set_minor_formatter(NullFormatter())
FILMS = [2.0, 6.3, 13.2]

# ------------------------------------------------------------------ data / device
def stack_schematic():
    fig, ax = plt.subplots(figsize=(FULL_W, 3.0)); ax.set_xlim(0, 24); ax.set_ylim(-0.6, 7.8); ax.axis('off')
    layers = [(0, 1.3, '#9aa3ad', 'TiN gate (Conductor), 50 nm  [region 6, electrode "gate"]'), (1.3, 2.9, '#c9d7e8', r'HfO$_2$, 15 nm, $\varepsilon_r$ = 19.57  [region 4]'),
              (2.9, 3.5, '#e7eef6', r'Al$_2$O$_3$, 2 nm, $\varepsilon_r$ = 9.0  [region 3]'), (3.5, 4.4, '#f3c89b', r'IWO channel, $t$ = 2.0 / 6.3 / 13.2 nm  [regions 1 + 2 (0.25 nm interface layer)]')]
    for y0, y1, c, lab in layers:
        ax.add_patch(Rectangle((0, y0), 24, y1 - y0, fc=c, ec='k', lw=0.6)); ax.text(12, (y0 + y1) / 2, lab, ha='center', va='center', fontsize=7.5)
    for x0, name in [(0, 'Pd source'), (22, 'Pd drain')]:
        ax.add_patch(Rectangle((x0, 4.4), 2, 1.7, fc='#b0b7c3', ec='k', lw=0.6, hatch='///')); ax.text(x0 + 1, 6.35, name + ', 70 nm', ha='center', va='bottom', fontsize=6.5, bbox=dict(fc='white', ec='none', pad=0.5))
    ax.add_patch(Rectangle((2, 4.4), 20, 2.4, fc='white', ec='k', lw=0.4, ls=':')); ax.text(12, 5.7, 'air (no passivation)  [region 7]', ha='center', fontsize=7.5, style='italic')
    ax.annotate('', xy=(2, 7.0), xytext=(22, 7.0), arrowprops=dict(arrowstyle='<->', lw=0.8)); ax.text(12, 7.15, r'$L$ = 20 $\mu$m (channel), overlap 2 $\mu$m each side (assumed); $W$ = 290 $\mu$m (simulated width 1 $\mu$m)', ha='center', fontsize=7.5)
    ax.text(0, -0.45, 'not to scale; bottom-gate, top-contact TFT; ' + r'$V_D$ = 0.7 V', fontsize=7, color=GREY)
    save(fig, 'stack_schematic'); note('stack_schematic', 'Drawn from config/geometry.yaml and docs/DEVICE_STRUCTURE.md; region numbers as in build_iwo_decks.py (full structure).')

def measured_transfer():
    fig, ax = plt.subplots(1, 2, figsize=(FULL_W, 2.7)); lines = []
    for t in [2.0, 6.3, 13.2, 31.8]:
        vg, i = meas(t); ax[0].semilogy(vg, i, color=FILM[t], lw=1.3, label=FILM_LABEL[t]); ax[1].plot(vg, i * 1e6, color=FILM[t], lw=1.3, label=FILM_LABEL[t])
        if t < 20: f = floor(vg, i); ax[0].hlines(f, -3, -0.5, color=FILM[t], ls=':', lw=0.9); lines.append(f'{t} nm floor {f:.2e} A/um')
    ax[0].set_xlabel(r'$V_G$ (V)'); ax[0].set_ylabel(r'$I_D$ (A/$\mu$m)'); ax[0].set_ylim(1e-17, 1e-5); ax[0].legend(loc='lower right')
    ax[1].set_xlabel(r'$V_G$ (V)'); ax[1].set_ylabel(r'$I_D$ ($\mu$A/$\mu$m)'); ax[1].legend(loc='upper left'); panel_label(ax[0], 'a'); panel_label(ax[1], 'b')
    save(fig, 'measured_transfer'); note('measured_transfer', 'data/experimental_clean.csv, Vd 0.7 V. Dotted: off-band median (-2..-0.5 V): ' + '; '.join(lines))

def measured_metrics():
    rows = {}
    for t in [2.0, 6.3, 13.2]:
        vg, i = meas(t); m = met(vg, i, False, t)
        rows[t] = dict(vcc=m['Vth_cc_1e-9_V'], vlin=m['Vth_lin_V'], ss1=fixed_ss(vg, i, 1e-11, 1e-10), ss2=fixed_ss(vg, i, 1e-10, 1e-8), mufe=m['mu_FE_cm2Vs'],
                       musat=float(np.nanmax(mu_sat(vg, i)[vg > -0.5])), ion=m['Ion_A_per_um'], fl=floor(vg, i))
    fig, ax = plt.subplots(2, 3, figsize=(FULL_W, 4.8), gridspec_kw=dict(hspace=0.5, wspace=0.55)); t = np.array(FILMS); g = lambda k: [rows[x][k] for x in FILMS]
    spec = [(ax[0, 0], [('vcc', r'$V_{th,cc}$'), ('vlin', r'$V_{th,lin}$')], 'threshold (V)', False), (ax[0, 1], [('ss1', r'$SS_{[10^{-11},10^{-10}]}$'), ('ss2', r'$SS_{[10^{-10},10^{-8}]}$')], 'SS (mV/dec)', False),
            (ax[0, 2], [('mufe', r'$\mu_{FE}$ (linear)'), ('musat', 'saturation formula')], r'mobility (cm$^2$/Vs)', False), (ax[1, 0], [('ion', r'$I_{on}$ at 3 V')], r'$I_{on}$ (A/$\mu$m)', True),
            (ax[1, 1], [('fl', 'off-band median')], r'off-floor (A/$\mu$m)', True)]
    for a, ks, yl, lg in spec:
        for k, lab in ks: a.plot(t, g(k), 'o-', ms=4, lw=1, label=lab)
        a.set_xlabel('IWO thickness (nm)'); a.set_ylabel(yl); a.set_xticks(FILMS)
        if lg: a.set_yscale('log')
        if len(ks) > 1: a.legend(fontsize=6.5)
    ax[1, 2].axis('off'); ax[1, 2].text(0, 0.95, 'Same extractor for data and\nsimulation (scripts/extract_metrics.py).\n31.8 nm is always on: threshold,\nSS and floor undefined.', va='top', fontsize=7.5)
    for k, a in enumerate(ax.flat[:5]): panel_label(a, 'abcde'[k])
    save(fig, 'measured_metrics'); note('measured_metrics', 'Measured metrics: ' + json.dumps({str(k): {kk: round(v, 4 if kk not in ('ion', 'fl') else 12) for kk, v in r.items()} for k, r in rows.items()}))

# ------------------------------------------------------------------ numerics
def numerics_convergence():
    fig, ax = plt.subplots(2, 2, figsize=(FULL_W, 5.2), gridspec_kw=dict(hspace=0.42, wspace=0.32))
    def dlog(r1, r0, s1=1, s0=1):
        v, a = sim(r1, s1); _, b = sim(r0, s0); ok = (a > 1e-16) & (b > 1e-16); return v[ok], np.log10(a[ok] / b[ok])
    for r, lab in [('0019', 'DOS 192/96 vs 96/48 (run_0019 - run_0012)'), ('0029', 'DOS 384/192 vs 96/48 (run_0029 - run_0012)')]:
        v, d = dlog(r, '0012'); ax[0, 0].plot(v, d, lw=1.2, label=lab)
    ax[0, 0].set_ylabel(r'$\Delta\log_{10} I_D$ (dec)'); ax[0, 0].set_xlabel(r'$V_G$ (V)'); ax[0, 0].legend(fontsize=6, loc='lower right'); ax[0, 0].axhline(0, color='k', lw=0.5)
    for r1, r0, lab, c in [('0028', '0013', '13.2 nm mesh x0.7 (run_0028 - run_0013)', FILM[13.2]), ('0036', '0015', '6.3 nm mesh x0.7 (run_0036 - run_0015)', FILM[6.3])]:
        v, d = dlog(r1, r0); ax[0, 1].plot(v, d, lw=1.2, color=c, label=lab)
    ax[0, 1].set_ylim(-0.02, 0.02); ax[0, 1].set_ylabel(r'$\Delta\log_{10} I_D$ (dec)'); ax[0, 1].set_xlabel(r'$V_G$ (V)'); ax[0, 1].legend(fontsize=6.5); ax[0, 1].axhline(0, color='k', lw=0.5)
    off = {2.0: 2.48, 6.3: 0.95, 13.2: 0.50}
    ax[1, 0].bar([str(t) for t in off], list(off.values()), color=[FILM[t] for t in off]); ax[1, 0].set_ylabel(r'$I_D$(3 V) offset 96/48$\rightarrow$384/192 (%)'); ax[1, 0].set_xlabel('IWO thickness (nm)')
    for k, v in enumerate(off.values()): ax[1, 0].text(k, v + 0.05, f'+{v:.2f} %', ha='center', fontsize=7)
    for r, lab, c in [('0012', r'run_0012 (DOS 96/48, $\mu$ 18.13): $SS_{min}$ 73.2', FILM[2.0]), ('0038', r'run_0038 (DOS 384/192, $\mu$ 17.69): $SS_{min}$ 83.1', ACCENT2)]:
        v, i = sim(r); ok = i > 1e-17; li = np.log10(i[ok]); ssl = 1e3 * np.gradient(v[ok], li); ax[1, 1].plot(li, ssl, lw=1.1, color=c, label=lab)
    ax[1, 1].axvline(np.log10(2.30e-14), color=GREY, ls='--', lw=0.8); ax[1, 1].text(np.log10(2.30e-14) + 0.15, 180, r'5$\times$ floor' + '\nwindow edge', fontsize=6.5, color=GREY)
    ax[1, 1].set_ylim(40, 320); ax[1, 1].set_xlim(-15.5, -6); ax[1, 1].set_xlabel(r'$\log_{10} I_D$ (A/$\mu$m)'); ax[1, 1].set_ylabel('local SS (mV/dec)'); ax[1, 1].legend(fontsize=6, loc='upper left', bbox_to_anchor=(0.0, 1.0))
    for k, a in enumerate(ax.flat): panel_label(a, 'abcd'[k])
    save(fig, 'numerics_convergence'); note('numerics_convergence', 'Runs 0012/0019/0029 (DOS), 0013/0028 and 0015/0036 (mesh), offsets from S6 report section 1 (B1-B3), SS_min artefact threshold 2.30e-14 A/um (S6).')

# ------------------------------------------------------------------ calibration and parameter control
FINAL = {2.0: ('0038', 1.0), 6.3: ('0039', S39), 13.2: ('0040', S40)}
def calibrated_overlays():
    fig, ax = plt.subplots(3, 3, figsize=(FULL_W, 5.8), sharex='col', gridspec_kw=dict(wspace=0.42, hspace=0.18)); txt = []
    for c, t in enumerate(FILMS):
        rid, s = FINAL[t]; vg, im = meas(t); vs, isim = sim(rid, s)
        ax[0, c].semilogy(vg, im, **MEAS); ax[0, c].semilogy(vs, pos(isim), color=FILM[t], **SIM, label=f'run_{rid}' + (f' x{s:.4f}' if s != 1 else ''))
        ax[0, c].set_ylim(1e-16, 1e-5); ax[0, c].legend(fontsize=6); ax[0, c].set_title(FILM_LABEL[t])
        ax[1, c].plot(vg, im * 1e6, **MEAS); ax[1, c].plot(vs, isim * 1e6, color=FILM[t], **SIM)
        r = np.log10(np.interp(vg, vs, np.clip(isim, 1e-40, None)) / im); act = im > 5 * floor(vg, im)
        ax[2, c].plot(vg[act], r[act], '.', color=FILM[t], ms=3); ax[2, c].axhline(0, color='k', lw=0.5); ax[2, c].set_ylim(-0.4, 0.4); ax[2, c].set_xlabel(r'$V_G$ (V)')
        m = met(vs, isim, True, t); txt.append(f"{t} nm: run_{rid} x{s:.6f}: Vth_cc {m['Vth_cc_1e-9_V']:.3f}, Vth_lin {m['Vth_lin_V']:.3f}, mu_FE {m['mu_FE_cm2Vs']:.2f}, Ion {m['Ion_A_per_um']:.4g}; active rms {np.sqrt(np.mean(r[act]**2)):.4f} dec")
    ax[0, 0].set_ylabel(r'$I_D$ (A/$\mu$m)'); ax[1, 0].set_ylabel(r'$I_D$ ($\mu$A/$\mu$m)'); ax[2, 0].set_ylabel(r'$\log_{10}(I_{sim}/I_{meas})$')
    save(fig, 'calibrated_overlays'); note('calibrated_overlays', 'Active region = measured > 5x off-band median. ' + ' | '.join(txt))

def calibration_history():
    fig, ax = plt.subplots(1, 2, figsize=(FULL_W, 2.8))
    for a, t, seq in [(ax[0], 2.0, [('0001', 'laws only'), ('0003', '+ shared Qf'), ('0008', r'+ $\mu_{band}$ 18.13'), ('0012', 'physical structure, stepped'), ('0038', 'DOS 384/192, $\\mu$ 17.69')]),
                      (ax[1], 13.2, [('0002', 'laws only'), ('0004', '+ shared Qf'), ('0009', r'+ $\mu_{band}$ 61.9'), ('0013', 'physical structure, stepped'), ('0040', 'DOS 384/192 (x1.0201)')])]:
        vg, im = meas(t); a.semilogy(vg, im, **MEAS)
        for k, (rid, lab) in enumerate(seq):
            s = S40 if rid == '0040' else 1.0; vs, i = sim(rid, s); a.semilogy(vs, pos(i), lw=1.1, color=plt.cm.viridis(k / 4.5), label=f'run_{rid}: {lab}')
        logax(a, 1e-16, 1e-5); a.legend(fontsize=5.8, loc='lower right'); a.set_title(FILM_LABEL[t])
    panel_label(ax[0], 'a'); panel_label(ax[1], 'b'); save(fig, 'calibration_history'); note('calibration_history', 'Stage runs from results/runs; see ch. 7 table for metrics.')

OAT2 = [('Qf 0 -> 1.73e12', '0001', '0003'), (r'$\mu_{band}$ 16.8 -> 18.13', '0003', '0008'), (r'$\chi$ -0.1 eV', '0012', '0020'), (r'$\chi$ +0.1 eV', '0012', '0021'),
        (r'$N_d$ x2', '0012', '0022'), (r'$N_t$ x1.5', '0012', '0023'), (r'$W_{TA}$ +5 meV', '0012', '0024'), (r'$D_{it}$ x3', '0012', '0025'),
        (r'$\varepsilon_{IWO}$ 10.55', '0012', '0026'), ('confinement off', '0012', '0016'), ('gate WF +0.1 eV', '0038', '0048'), (r'$m^*$ x1.3', '0038', '0050')]
def param_control_2nm():
    fig, ax = plt.subplots(3, 4, figsize=(FULL_W, 5.2), sharex=True, sharey=True); vg, im = meas(2.0)
    for a, (lab, b, p) in zip(ax.flat, OAT2):
        a.semilogy(vg, im, 'o', color='0.65', ms=1.8, mfc='none', mew=0.5); vb, ib = sim(b); vp, ip = sim(p)
        a.semilogy(vb, pos(ib), color=FILM[2.0], lw=1.1, label=f'base {b}'); a.semilogy(vp, pos(ip), color=ACCENT2, lw=1.1, ls='--', label=f'pert {p}')
        a.set_ylim(1e-15, 1e-5); a.set_xlim(-1, 3); a.set_title(lab, fontsize=7.5); a.legend(fontsize=5.2, loc='lower right')
    for a in ax[-1]: a.set_xlabel(r'$V_G$ (V)')
    for a in ax[:, 0]: a.set_ylabel(r'$I_D$ (A/$\mu$m)')
    save(fig, 'param_control_2nm'); note('param_control_2nm', 'Pairs (label, base, perturbed): ' + '; '.join(f'{l}: {b}->{p}' for l, b, p in OAT2) + '. Grey circles: measured 2 nm. run_0027 (overlap) excluded: malformed.')

def param_control_delta():
    fig, ax = plt.subplots(2, 1, figsize=(FULL_W, 6.2), gridspec_kw=dict(height_ratios=[1, 1.15], hspace=0.32)); rows = []
    for k, (lab, b, p) in enumerate(OAT2):
        vb, ib = sim(b); vp, ip = sim(p); ok = (ib > 1e-16) & (ip > 1e-16)
        ax[0].plot(vb[ok], np.log10(ip[ok] / ib[ok]), lw=1.0, color=CYCLE[k % len(CYCLE)] if k < 10 else ('#555555' if k == 10 else '#aa3377'), label=lab)
        mb, mp = met(vb, ib), met(vp, ip)
        rows.append((lab, mp['Vth_cc_1e-9_V'] - mb['Vth_cc_1e-9_V'], (fixed_ss(vp, ip, 1e-10, 1e-9) or np.nan) - (fixed_ss(vb, ib, 1e-10, 1e-9) or np.nan), 100 * (mp['Ion_A_per_um'] / mb['Ion_A_per_um'] - 1)))
    ax[0].axhline(0, color='k', lw=0.5); ax[0].set_ylim(-1.2, 1.2); ax[0].set_xlim(-1, 3); ax[0].set_xlabel(r'$V_G$ (V)'); ax[0].set_ylabel(r'$\Delta\log_{10} I_D$ (dec)'); ax[0].legend(fontsize=6, ncol=1, loc='center left', bbox_to_anchor=(1.01, 0.5))
    y = np.arange(len(rows)); w = 0.27
    ax[1].barh(y - w, [r[1] for r in rows], w, color=ACCENT, label=r'$\Delta V_{th,cc}$ (V)'); ax[1].barh(y, [r[2] / 100 for r in rows], w, color=WARN, label=r'$\Delta SS_{[10^{-10},10^{-9}]}$ /100 (mV/dec)')
    ax[1].barh(y + w, [r[3] / 100 for r in rows], w, color=ACCENT2, label=r'$\Delta I_{on}$ /100 (%)'); ax[1].set_yticks(y); ax[1].set_yticklabels([r[0] for r in rows], fontsize=6); ax[1].invert_yaxis(); ax[1].axvline(0, color='k', lw=0.5)
    ax[1].legend(fontsize=6, loc='center left', bbox_to_anchor=(1.01, 0.5)); ax[1].set_xlabel('change (scaled units: V, mV/dec/100, %/100)'); panel_label(ax[0], 'a', x=-0.1); panel_label(ax[1], 'b', x=-0.27)
    save(fig, 'param_control_delta'); note('param_control_delta', 'Changes (dVth_cc V, dSS 1e-10..1e-9 mV/dec, dIon %): ' + '; '.join(f'{r[0]}: {r[1]:+.3f}, {r[2]:+.1f}, {r[3]:+.1f}' for r in rows))

def param_control_13nm():
    pairs = [('Qf 0 -> 1.73e12', '0002', '0004'), (r'$\mu_{band}$ 57.6 -> 61.9', '0004', '0009'), ('confinement off', '0013', '0017'), ('gate WF +0.1 eV', '0040', '0049'), (r'$m^*$ x1.3', '0040', '0051')]
    fig, ax = plt.subplots(1, 5, figsize=(FULL_W, 1.9), sharey=True); vg, im = meas(13.2)
    for a, (lab, b, p) in zip(ax, pairs):
        a.semilogy(vg, im, 'o', color='0.65', ms=1.8, mfc='none', mew=0.5); vb, ib = sim(b); vp, ip = sim(p)
        a.semilogy(vb, pos(ib), color=FILM[13.2], lw=1.1, label=b); a.semilogy(vp, pos(ip), color=ACCENT2, ls='--', lw=1.1, label=p)
        a.set_ylim(1e-14, 1e-5); a.set_xlim(-1.5, 3); a.set_title(lab, fontsize=7); a.set_xlabel(r'$V_G$ (V)'); a.legend(fontsize=5.5, loc='lower right')
    ax[0].set_ylabel(r'$I_D$ (A/$\mu$m)'); save(fig, 'param_control_13nm'); note('param_control_13nm', 'Pairs: ' + '; '.join(f'{l}: {b}->{p}' for l, b, p in pairs))

# ------------------------------------------------------------------ 6.3 nm
HYP = [('0014', 'shared (validation)', 1.0), ('0015', 'tuned Qf 8.7e10', 1.0), ('0031', 'A1 t = 5.3 nm', 1.0), ('0032', r'A2 $N_d$ removed', 1.0), ('0030', 'A3 back charge', 1.0),
       ('0033', r'A4 $D_{it}$ x5', 1.0), ('0035', 'A5 combination', 1.0), ('0034', 'A6 no confinement', 1.0)]
def hyp_6p3_overlays():
    fig, ax = plt.subplots(1, 2, figsize=(FULL_W, 3.0)); vg, im = meas(6.3)
    for a, lin in [(ax[0], False), (ax[1], True)]:
        a.plot(vg, im * (1e6 if lin else 1), **MEAS)
        for k, (rid, lab, s) in enumerate(HYP):
            vs, i = sim(rid, s); a.plot(vs, (i * 1e6) if lin else pos(i), lw=1.0, color=CYCLE[k], ls='-' if k < 2 else '--', label=f'{rid}: {lab}')
    logax(ax[0], 1e-15, 1e-5); ax[1].set_xlim(0.5, 3); ax[1].set_ylim(0, 0.6); ax[1].set_xlabel(r'$V_G$ (V)'); ax[1].set_ylabel(r'$I_D$ ($\mu$A/$\mu$m)'); ax[0].legend(fontsize=5.4, loc='lower right')
    panel_label(ax[0], 'a'); panel_label(ax[1], 'b'); save(fig, 'hyp_6p3_overlays'); note('hyp_6p3_overlays', 'Runs ' + ', '.join(r for r, _, _ in HYP) + ' vs measured 6.3 nm (DOS 96/48).')

def hyp_6p3_metrics():
    vg, im = meas(6.3); mm = met(vg, im, False, 6.3); ssm = fixed_ss(vg, im, 1e-10, 1e-8); gapm = mm['Vth_lin_V'] - mm['Vth_cc_1e-9_V']
    runs = HYP + [('0037', 'B0 re-partition', 1.0), ('0052', 'C1 near-Ec band', 1.0), ('0039', 'B2 tuned DOS384', S39)]; rows = []
    for rid, lab, s in runs:
        vs, i = sim(rid, s); m = met(vs, i, True, 6.3)
        rows.append((f'{rid} {lab}', m['Vth_cc_1e-9_V'] - mm['Vth_cc_1e-9_V'], (fixed_ss(vs, i, 1e-10, 1e-8) or np.nan) - ssm, (m['Vth_lin_V'] - m['Vth_cc_1e-9_V']) - gapm, 100 * (m['gm_max_A_V_um'] / mm['gm_max_A_V_um'] - 1)))
    fig, ax = plt.subplots(1, 4, figsize=(FULL_W, 3.1), sharey=True); y = np.arange(len(rows))
    for a, k, lab in [(ax[0], 1, r'$\Delta V_{th,cc}$ (V)'), (ax[1], 2, r'$\Delta SS_{[10^{-10},10^{-8}]}$ (mV/dec)'), (ax[2], 3, r'$\Delta$(gap) (V)'), (ax[3], 4, r'$\Delta g_{m,max}$ (%)')]:
        v = [r[k] for r in rows]; a.barh(y, v, color=[OK if abs(x) < {1: 0.05, 2: 20, 3: 0.1, 4: 8}[k] else FAIL for x in v]); a.axvline(0, color='k', lw=0.6); a.set_xlabel(lab, fontsize=7)
    ax[0].set_yticks(y); ax[0].set_yticklabels([r[0] for r in rows], fontsize=6); ax[0].invert_yaxis()
    save(fig, 'hyp_6p3_metrics'); note('hyp_6p3_metrics', f'Errors vs measured 6.3 nm (Vth_cc {mm["Vth_cc_1e-9_V"]:.3f}, SS {ssm:.1f}, gap {gapm:.3f}, gm {mm["gm_max_A_V_um"]:.3e}); green = within 0.05 V / 20 mV/dec / 0.1 V / 8 %: ' + '; '.join(f'{r[0]}: {r[1]:+.3f} V, {r[2]:+.1f}, {r[3]:+.3f} V, {r[4]:+.1f} %' for r in rows))

def shape_6p3():
    vg, im = meas(6.3); fig, ax = plt.subplots(1, 3, figsize=(FULL_W, 2.4)); cases = [('0039', 'B2 tuned (x1.0151)', S39, FILM[6.3]), ('0037', 'B0 re-partition', 1.0, ACCENT), ('0052', 'C1 near-Ec band', 1.0, ACCENT2)]
    ax[0].semilogy(vg, im, **MEAS); ax[1].plot(vg, im * 1e6, **MEAS); ax[2].plot(vg, np.gradient(im, vg) * 1e7, **MEAS)
    for rid, lab, s, c in cases:
        vs, i = sim(rid, s); ax[0].semilogy(vs, pos(i), color=c, lw=1.1, label=f'{rid}: {lab}'); ax[1].plot(vs, i * 1e6, color=c, lw=1.1); ax[2].plot(vs, np.gradient(i, vs) * 1e7, color=c, lw=1.1)
    logax(ax[0], 1e-15, 1e-5); ax[0].legend(fontsize=5.2, loc='upper left'); ax[1].set_xlim(0.5, 3); ax[1].set_ylim(0, 0.5); ax[1].set_ylabel(r'$I_D$ ($\mu$A/$\mu$m)'); ax[1].set_xlabel(r'$V_G$ (V)')
    ax[2].set_xlim(0.5, 3); ax[2].set_ylabel(r'$g_m$ ($10^{-7}$ A/V/$\mu$m)'); ax[2].set_xlabel(r'$V_G$ (V)')
    for k, a in enumerate(ax): panel_label(a, 'abc'[k])
    save(fig, 'shape_6p3'); note('shape_6p3', 'Measured 6.3 nm vs run_0039 (x11.581987/11.41), run_0037 (B0), run_0052 (C1). gm = numerical gradient on the 0.05 V grid.')

def off_floors():
    fig, ax = plt.subplots(1, 2, figsize=(FULL_W, 2.6)); fl = {}
    for t in FILMS:
        vg, i = meas(t); s = vg <= 0; ax[0].semilogy(vg[s], i[s], color=FILM[t], lw=1.2, label=FILM_LABEL[t]); fl[t] = floor(vg, i)
    ax[0].set_xlabel(r'$V_G$ (V)'); ax[0].set_ylabel(r'$I_D$ (A/$\mu$m)'); ax[0].legend(); ax[0].set_xlim(-3, 0)
    t = np.array(FILMS); f = np.array([fl[x] for x in FILMS]); ax[1].loglog(t, f, 'o', color='k', ms=4)
    for x in FILMS: ax[1].plot(x, fl[x], 'o', color=FILM[x], ms=5)
    p = np.polyfit(np.log(t), np.log(f), 1); tt = np.linspace(1.8, 14, 50); ax[1].loglog(tt, np.exp(np.polyval(p, np.log(tt))), '--', color=GREY, lw=0.9, label=rf'fit $\propto t^{{{p[0]:.2f}}}$')
    ax[1].set_xlabel('IWO thickness (nm)'); ax[1].set_ylabel(r'off-floor (A/$\mu$m)'); ax[1].legend(); ticks_t(ax[1], FILMS); panel_label(ax[0], 'a'); panel_label(ax[1], 'b')
    save(fig, 'off_floors'); note('off_floors', f'Floors (median -2..-0.5 V): {fl}; ratio 13.2/2 = {fl[13.2] / fl[2.0]:.0f}; log-log slope {p[0]:.2f} (S4 quotes 3.85).')

# ------------------------------------------------------------------ mechanisms
def vth_budget():
    terms = [('WF - chi', [0.400, 0.400, 0.400]), ('confinement dEc', [0.353, 0.072, 0.026]), ('E_Fn - E_c', [-0.038, -0.039, -0.111]), ('front Qf', [-0.310, -0.310, -0.310]),
             ('q Nd t / Cox', [-0.009, -0.028, -0.070]), ('tail charge', [0.256, 0.226, 0.098]), ('interface traps', [0.012, 0.012, 0.012]), ('free electrons', [0.014, 0.016, 0.005]), ('deep Gaussian', [0.0, 0.001, 0.003])]
    fig, ax = plt.subplots(figsize=(FULL_W, 2.9)); x = np.arange(len(terms)); w = 0.26
    for k, t in enumerate(FILMS): ax.bar(x + (k - 1) * w, [v[k] for _, v in terms], w, color=FILM[t], label=FILM_LABEL[t] + (' (validation run_0014)' if t == 6.3 else ''))
    ax.set_xticks(x); ax.set_xticklabels([n for n, _ in terms], rotation=25, ha='right', fontsize=7); ax.axhline(0, color='k', lw=0.6); ax.set_ylabel('contribution to $V_{th,cc}$ (V)')
    ax.text(0.99, 0.97, 'sum (1-D / ATLAS / measured):\n2.0 nm 0.679 / 0.676 / 0.662\n6.3 nm 0.351 / 0.350 / 0.644\n13.2 nm 0.052 / 0.053 / 0.083', transform=ax.transAxes, ha='right', va='top', fontsize=6.5)
    ax.legend(fontsize=6.5, loc='lower left'); save(fig, 'vth_budget'); note('vth_budget', 'Gauss terms at Vth_cc from S1 report section 1.1 (1-D surrogate matching ATLAS within 3 mV): runs 0012, 0014, 0013.')

def symmetric_calibration():
    req = {'with confinement': [1.81, 0.09, 1.56], 'without confinement': [0.048, -0.27, 1.43]}
    fig, ax = plt.subplots(1, 2, figsize=(FULL_W, 2.6), gridspec_kw=dict(wspace=0.4)); x = np.arange(3); w = 0.36; txt = []
    for k, (lab, v) in enumerate(req.items()):
        ax[0].bar(x + (k - 0.5) * w, v, w, color=[ACCENT, ACCENT2][k], label=lab)
        best = np.mean(v); res = (np.array(v) - best) * 1e12 * Q / COX; txt.append(f'{lab}: best single Qf {best:.3f}e12, residuals {np.round(res, 3).tolist()} V, rms {np.sqrt(np.mean(res**2)):.4f} V')
        ax[1].bar(x + (k - 0.5) * w, res, w, color=[ACCENT, ACCENT2][k], label=f'{lab} (rms {np.sqrt(np.mean(res**2)):.3f} V)')
    for a in ax: a.set_xticks(x); a.set_xticklabels(['2.0 nm', '6.3 nm', '13.2 nm']); a.axhline(0, color='k', lw=0.6); a.legend(fontsize=6.3)
    ax[0].set_ylabel(r'required $Q_f$ ($10^{12}$ cm$^{-2}$)'); ax[1].set_ylabel('single-offset residual (V)'); panel_label(ax[0], 'a'); panel_label(ax[1], 'b')
    save(fig, 'symmetric_calibration'); note('symmetric_calibration', 'Required Qf from S1 key numbers / SYNTHESIS D3. ' + ' | '.join(txt))

def mobility_partition():
    v1 = {2.0: (18.13, 0.734, 0.847, 11.27), 6.3: (11.69, 0.911, 0.791, 8.42), 13.2: (61.9, 0.957, 0.826, 48.95)}; s2 = {2.0: 19.3, 6.3: 19.6, 13.2: 62.7}; mfe = {2.0: 12.15, 6.3: 10.95, 13.2: 50.17}
    fig, ax = plt.subplots(1, 2, figsize=(FULL_W, 2.6)); x = np.arange(3); w = 0.2
    for k, (lab, f) in enumerate([(r'$\mu_{band}$', lambda v: v[0]), (r'$\mu_{band} R(t)$', lambda v: v[0] * v[1]), (r'$\mu_{FE}$ model = $\mu_{band} R P$', lambda v: v[3])]):
        ax[0].bar(x + (k - 1.5) * w, [f(v1[t]) for t in FILMS], w, label=lab, color=[ACCENT, '#6b8fb8', WARN][k])
    ax[0].bar(x + 1.5 * w, [mfe[t] for t in FILMS], w, color='k', label=r'$\mu_{FE}$ measured'); ax[0].set_yscale('log'); ax[0].set_xticks(x); ax[0].set_xticklabels(['2.0', '6.3', '13.2']); ax[0].set_xlabel('IWO thickness (nm)'); ax[0].set_ylabel(r'cm$^2$/Vs'); ax[0].legend(fontsize=6)
    ax[1].plot(FILMS, [v1[t][0] for t in FILMS], 'o-', color=ACCENT, label='V1 (tail law $t^{-0.75}$)'); ax[1].plot(FILMS, [s2[t] for t in FILMS], 's--', color=ACCENT2, label='S2 shape-consistent partition')
    ax[1].set_xlabel('IWO thickness (nm)'); ax[1].set_ylabel(r'fitted $\mu_{band}$ (cm$^2$/Vs)'); ax[1].legend(fontsize=6.5); ax[1].set_xticks(FILMS); panel_label(ax[0], 'a'); panel_label(ax[1], 'b')
    save(fig, 'mobility_partition'); note('mobility_partition', 'V1 decomposition (runs 0012/0015/0013) and S2 partition (1-D surrogate) from S2 report key numbers.')

def thickness_laws():
    t = np.linspace(0.9, 32, 400); hb = 1.054571817e-34; me = 9.1093837015e-31
    fig, ax = plt.subplots(2, 3, figsize=(FULL_W, 5.0), gridspec_kw=dict(hspace=0.45, wspace=0.42)); a = ax[0, 0]
    a.loglog(t, 0.9205 * t ** -1.3815, color=ACCENT, lw=1.4, label=r'ATLAS law 0.9205 $t^{-1.3815}$')
    for m, ls in [(0.18, ':'), (0.26, '--'), (0.35, '-.')]: a.loglog(t, (hb * np.pi) ** 2 / (2 * m * me * (t * 1e-9) ** 2) / Q, ls, color=GREY, lw=0.9, label=rf'infinite well $m^*$={m}')
    a.loglog([1.98, 0.95], [0.33, 0.94], 'o', color='k', ms=4, label='Lin 2022 PBE slabs'); a.loglog([1.5], [0.6], 's', color='k', ms=4, label='Si 2021 PBE')
    a.loglog([2.0, 6.3, 13.2], [0.2556, 0.0359, 0.016], 'D', color=ACCENT2, ms=4, label='S3 SP-equivalent shift (Q1)')
    a.set_ylim(3e-3, 3); a.set_xlabel('t (nm)'); a.set_ylabel(r'$\Delta E_c$ (eV)'); a.legend(fontsize=4.8, loc='lower left')
    a = ax[0, 1]; a.plot(t, 0.208 + 0.1311 * t ** -1.412, color=ACCENT); a.plot([3.52, 1.98, 0.95], [0.228, 0.268, 0.338], 'o', color='k', ms=4, label='0.208 + PBE increments')
    a.legend(fontsize=5, loc='upper right', frameon=True, framealpha=0.92, edgecolor='0.75')   # 2026-10-06: framed; unframed, the legend marker looked like a 4th data point
    a.set_xscale('log'); a.set_xlabel('t (nm)'); a.set_ylabel(r'$m^*/m_0$')
    a = ax[0, 2]; a.loglog(t, 2e19 * (2 / t) ** 0.75, color=ACCENT, label='power law'); a.loglog(t, 2.15e18 + 3.57e12 / (t * 1e-7), '--', color=ACCENT2, label='surface + bulk')
    a.loglog([2.0, 10.0], [5.3e19, 3.39e18], 's', color='k', ms=4, label='Januar 2026'); a.set_xlabel('t (nm)'); a.set_ylabel(r'$N_t$ (cm$^{-3}$)'); a.legend(fontsize=5, loc='lower left', frameon=True, framealpha=0.92, edgecolor='0.75')   # 2026-10-06: framed, in the empty corner
    a = ax[1, 0]; a.semilogy(t, 2.5e17 * (1 + (t / 20) ** 4), color=ACCENT); a.set_xlabel('t (nm)'); a.set_ylabel(r'$N_{d,eff}$ (cm$^{-3}$)')
    a = ax[1, 1]; a.plot(t, (1 - 0.287 / t) ** 2, color=ACCENT); a.set_xscale('log'); a.set_xlabel('t (nm)'); a.set_ylabel(r'$(1-\Delta_{sr}/t)^2$')
    for x in FILMS:
        for aa in (ax[0, 1], ax[0, 2], ax[1, 0], ax[1, 1]): aa.axvline(x, color=FILM[x], lw=0.6, ls=':')
    ax[1, 2].axis('off'); ax[1, 2].text(0, 0.9, 'Dotted verticals: 2.0 / 6.3 / 13.2 nm.\nThe ATLAS dEc law exceeds the\ninfinite-well bound above ~3 nm.', va='top', fontsize=7)
    for k, aa in enumerate(list(ax.flat)[:5]): panel_label(aa, 'abcde'[k])
    save(fig, 'thickness_laws'); note('thickness_laws', 'Laws from config/iwo_material_model.yaml; DFT points tables/THICKNESS_LAW_EVIDENCE.csv; SP shifts scratch/S3/s3_sp1d_notraps_out.txt (Q1 at n_s=1e10).')

def sp_confinement():
    d = json.loads((ANA / 'scratch' / 'S3' / 's3_sp1d_notraps.json').read_text()); cases = ['C1', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5']
    lab = {'C1': 'classical + ATLAS law', 'Q1': r'SP $m^*$ 0.18, NP, finite', 'Q2': 'SP 0.18, NP, hard wall', 'Q3': 'SP 0.18, NP, finite (alt.)', 'Q4': 'SP 0.257, finite', 'Q5': 'SP 0.35, finite'}
    fig, ax = plt.subplots(1, 2, figsize=(FULL_W, 2.6)); x = np.arange(3); w = 0.13; txt = []
    for k, c in enumerate(cases):
        v = [d[str(t)][c]['vg_1e10'] - d[str(t)]['C0']['vg_1e10'] for t in FILMS]; ax[0].bar(x + (k - 2.5) * w, v, w, label=lab[c], color=CYCLE[k]); txt.append(f'{c}: ' + ', '.join(f'{u:.3f}' for u in v))
    ax[0].set_xticks(x); ax[0].set_xticklabels(['2.0 nm', '6.3 nm', '13.2 nm']); ax[0].set_ylabel(r'onset shift vs classical (V) at $n_s=10^{10}$'); ax[0].legend(fontsize=5.3)
    for k, c in enumerate(['C0', 'C1', 'Q1']):
        ax[1].plot(FILMS, [d[str(t)][c].get('zc_at_3V') or np.nan for t in FILMS], 'o-', color=CYCLE[k], label={'C0': 'classical, no dEc', 'C1': 'classical + law', 'Q1': 'SP Q1'}[c])
    ax[1].set_xlabel('IWO thickness (nm)'); ax[1].set_ylabel('charge centroid at 3 V (nm)'); ax[1].legend(fontsize=6); ax[1].set_xticks(FILMS); panel_label(ax[0], 'a'); panel_label(ax[1], 'b')
    save(fig, 'sp_confinement'); note('sp_confinement', 'scratch/S3/s3_sp1d_notraps.json (no traps). Shifts vs C0 at 1e10 cm^-2: ' + ' | '.join(txt))

def mufe_extraction():
    fig, ax = plt.subplots(1, 3, figsize=(FULL_W, 2.3)); txt = []
    for a, t in zip(ax, FILMS):
        vg, i = meas(t); ml, ms = mu_lin(vg, i), mu_sat(vg, i); s = vg > -0.5
        a.plot(vg[s], ml[s], color=FILM[t], lw=1.2, label=r'linear $g_m L/(W C_{ox} V_D)$'); a.plot(vg[s], ms[s], '--', color='k', lw=1.0, label=r'sat. formula $(2L/WC_{ox})(\partial\sqrt{I_D}/\partial V_G)^2$')
        a.set_title(FILM_LABEL[t]); a.set_xlabel(r'$V_G$ (V)'); txt.append(f'{t} nm: max linear {np.nanmax(ml[s]):.2f}, max sat-formula {np.nanmax(ms[s]):.2f}')
    ax[0].set_ylabel(r'mobility (cm$^2$/Vs)'); ax[0].legend(fontsize=5.2, loc='upper left')
    save(fig, 'mufe_extraction'); note('mufe_extraction', 'np.gradient on the measured 0.05 V grid; ' + '; '.join(txt) + ' (paper: 5.1 and 27.4).')

def powerlaw_loo():
    t2, t13 = 2.0, 13.2; m2, m13 = 12.15, 50.17; mm = {2.0: 12.15, 6.3: 10.95, 13.2: 50.17}; tt = np.linspace(1.8, 34, 300)
    b = np.log(m13 / m2) / np.log(t13 / t2); B = (m13 - m2) / (1 / t13 - 1 / t2); A = m2 - B / t2; k = np.log(m13 / m2) / (t13 - t2)
    models = {'power law': m2 * (tt / t2) ** b, 'A + B/t': A + B / tt, 'exponential': m2 * np.exp(k * (tt - t2)), 'step': np.where(tt < 10, m2, m13)}
    fig, ax = plt.subplots(1, 2, figsize=(FULL_W, 2.6)); pred = {}
    for kk, (n, y) in enumerate(models.items()):
        ax[0].plot(tt, y, color=CYCLE[kk], lw=1.1, label=n); pred[n] = float(np.interp(6.3, tt, y))
    ax[0].plot(list(mm), list(mm.values()), 'o', color='k', ms=4, label='measured'); ax[0].set_xscale('log'); ax[0].set_ylim(0, 70); ax[0].set_xlim(1.8, 16); ticks_t(ax[0], FILMS); ax[0].set_xlabel('t (nm)'); ax[0].set_ylabel(r'$\mu_{FE}$ (cm$^2$/Vs)'); ax[0].legend(fontsize=6)
    ion = {2.0: 5.09e-7, 6.3: 4.03e-7, 13.2: 3.07e-6, 31.8: 3.59e-6}; bi = np.log(ion[13.2] / ion[6.3]) / np.log(13.2 / 6.3)
    ax[1].loglog(tt, ion[6.3] * (tt / 6.3) ** bi, '--', color=ACCENT2, label=rf'power law through 6.3/13.2 ($t^{{{bi:.2f}}}$)'); ax[1].loglog(list(ion), list(ion.values()), 'o', color='k', ms=4, label='measured')
    ax[1].set_xlabel('t (nm)'); ax[1].set_ylabel(r'$I_{on}$ (A/$\mu$m)'); ax[1].legend(fontsize=6); ticks_t(ax[1], [2.0, 6.3, 13.2, 31.8]); panel_label(ax[0], 'a'); panel_label(ax[1], 'b')
    save(fig, 'powerlaw_loo'); note('powerlaw_loo', f'Models fitted through 2 and 13.2 nm, predicting 6.3 nm (measured 10.95): {pred}; Ion power exponent {bi:.2f} predicts {ion[6.3] * (31.8 / 6.3) ** bi:.3g} A/um at 31.8 nm (measured 3.59e-6).')

# ------------------------------------------------------------------ predictions
def idvd_predictions():
    fig, axx = plt.subplots(2, 3, figsize=(FULL_W, 4.2), gridspec_kw=dict(height_ratios=[1.6, 1], hspace=0.45)); ax = axx[0]; txt = []
    for a, ins, (t, rid) in zip(ax, axx[1], [(2.0, '0041'), (6.3, '0042'), (13.2, '0043')]):
        rows = np.array([[float(r['vg_V']), float(r['vd_V']), float(r['id_A_per_um'])] for r in csv.DictReader((rdir(rid) / 'output_characteristics.csv').open())])
        for k, vgv in enumerate(sorted(set(rows[:, 0]))):
            s = rows[:, 0] == vgv; a.plot(rows[s, 1], rows[s, 2] * 1e6, color=plt.cm.viridis(k / 4.5), lw=1.1, label=f'{vgv:g} V'); ins.plot(rows[s, 1], rows[s, 2] * 1e6, color=plt.cm.viridis(k / 4.5), lw=0.9)
        ins.set_xlim(0, 0.3); ins.set_ylim(0, None); ins.set_xlabel(r'$V_D$ (V), low-field zoom')
        a.set_title(f'{FILM_LABEL[t]} (run_{rid})'); a.set_xlabel(r'$V_D$ (V)'); txt.append(f'{t} nm run_{rid}: Id(3,3) {rows[(rows[:, 0] == 3) & (np.isclose(rows[:, 1], 3))][0, 2]:.4g} A/um')
    ax[0].set_ylabel(r'$I_D$ ($\mu$A/$\mu$m)'); axx[1, 0].set_ylabel(r'$I_D$ ($\mu$A/$\mu$m)'); ax[0].legend(title=r'$V_G$', fontsize=5.5, title_fontsize=6, loc='upper left')
    save(fig, 'idvd_predictions'); note('idvd_predictions', 'output_characteristics.csv of runs 0041-0043 (recalibrated DOS 384/192). ' + '; '.join(txt))

TRUNS = {2.0: [(300.0, '0038', 1.0), (338.15, '0044', 1.0), (358.15, '0045', 1.0)], 6.3: [(300.0, '0039', S39), (358.15, '0046', 1.0)], 13.2: [(300.0, '0040', S40), (358.15, '0047', 1.0)]}
def temperature_predictions():
    fig, ax = plt.subplots(1, 3, figsize=(FULL_W, 2.6), sharey=True); txt = []
    for a, t in zip(ax, FILMS):
        T0, r0, s0 = TRUNS[t][0]; v0, i0 = sim(r0, s0)
        for T, rid, s in TRUNS[t][1:]:
            vs, i = sim(rid, s); ok = (vs >= -0.5) & (i0 > 1e-15) & (np.interp(vs, vs, i) > 1e-15); c = {338.15: WARN, 358.15: FAIL}[T]
            r = i[ok] / np.interp(vs[ok], v0, i0); a.semilogy(vs[ok], r, color=c, lw=1.2, label=f'{T:g} K, P-phonon'); a.semilogy(vs[ok], r * (T / 300) ** 1.5, color=c, lw=1.2, ls='--', label=f'{T:g} K, P-MTR')
            txt.append(f'{t} nm {T} K: ratio at 3 V P-phonon {r[-1]:.3f}, P-MTR {r[-1] * (T / 300) ** 1.5:.3f}; at 0.5 V P-MTR {np.interp(0.5, vs[ok], r) * (T / 300) ** 1.5:.2f}')
        a.axhline(1, color='k', lw=0.6); a.set_xlim(-0.5, 3); a.set_title(FILM_LABEL[t]); a.set_xlabel(r'$V_G$ (V)')
    ax[0].set_ylabel(r'$I_D(T)/I_D(300\,\mathrm{K})$'); ax[0].legend(fontsize=5.8, loc='upper right')
    save(fig, 'temperature_predictions'); note('temperature_predictions', 'Ratios of runs 0044-0047 (as simulated, ATLAS tmu = 1.5: P-phonon) and x(T/300)^1.5 (P-MTR) to the 300 K references 0038, 0039 x1.015074, 0040 x1.020113; ' + '; '.join(txt))
def activation_energy():
    fig, ax = plt.subplots(figsize=(HALF_W * 1.35, 2.6)); vgrid = np.arange(0.3, 3.01, 0.05); txt = []
    for t in FILMS:
        curves = [(T, *sim(rid, s)) for T, rid, s in TRUNS[t]]
        for var, ls in [('P-MTR', '--'), ('P-phonon', '-')]:
            E = []
            for v in vgrid:
                x = np.array([1 / (KB * T) for T, _, _ in curves]); y = np.array([np.log(np.interp(v, vs, i) * ((T / 300) ** 1.5 if (var == 'P-MTR' and T > 300) else 1)) for T, vs, i in curves])
                E.append(-np.polyfit(x, y, 1)[0] * 1e3)
            ax.plot(vgrid, E, ls, color=FILM[t], lw=1.1, label=f'{FILM_LABEL[t]} {var}'); txt.append(f'{t} {var} Ea(1 V) {np.interp(1.0, vgrid, E):.1f} meV')
    ax.axhline(0, color='k', lw=0.5); ax.set_xlabel(r'$V_G$ (V)'); ax.set_ylabel(r'$E_a$ (meV)'); ax.legend(fontsize=5.3, ncol=2); ax.set_ylim(-60, 200)
    save(fig, 'activation_energy'); note('activation_energy', 'Least-squares Arrhenius over available T (2 nm: 300/338.15/358.15; others 300/358.15); ' + '; '.join(txt))

COPIES = {'band_2p0_eq': PKG / 'plots/2p0/band_diagram_eq.png', 'band_2p0_vth': PKG / 'plots/2p0/band_diagram_vth.png', 'band_2p0_on': PKG / 'plots/2p0/band_diagram_on.png',
          'band_13p2_on': PKG / 'plots/13p2/band_diagram_on.png', 'edens_2p0_vs_vg': PKG / 'plots/2p0/electron_density_vs_vg.png', 'edens_13p2_vs_vg': PKG / 'plots/13p2/electron_density_vs_vg.png',
          'trap_spectroscopy': ANA / 'scratch/S4/s4_trap_spectroscopy.png', 'yfunction': ANA / 'scratch/S5/s5_yfunction_hfunction.png'}
ALL = [stack_schematic, measured_transfer, measured_metrics, numerics_convergence, calibrated_overlays, calibration_history, param_control_2nm, param_control_delta, param_control_13nm,
       hyp_6p3_overlays, hyp_6p3_metrics, shape_6p3, off_floors, vth_budget, symmetric_calibration, mobility_partition, thickness_laws, sp_confinement, mufe_extraction, powerlaw_loo,
       idvd_predictions, temperature_predictions, activation_energy]

if __name__ == '__main__':
    want = set(sys.argv[1:]); fails = []
    for f in ALL:
        if want and f.__name__ not in want: continue
        try: f()
        except Exception: fails.append(f.__name__); traceback.print_exc()
    for stem, src in COPIES.items():
        if want and stem not in want: continue
        shutil.copy2(src, FIG / f'{stem}.png'); (FIG / 'png').mkdir(exist_ok=True); shutil.copy2(src, FIG / 'png' / f'{stem}.png'); note(stem, f'Copied from {src.relative_to(PKG)}')
    mf = FIG / 'MANIFEST.md'; old = mf.read_text(encoding='utf-8') if (mf.exists() and want) else ''
    mf.write_text(old + '\n'.join(MAN), encoding='utf-8'); print('FAILED:', fails)





