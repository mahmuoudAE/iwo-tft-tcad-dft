#!/usr/bin/env python3
"""Register A57: measured-data Monte Carlo - extraction uncertainty of the registered quantities of the three calibration films (2.0, 6.3,
13.2 nm) from the measured transfer curves. NO simulator call, no run directory, no sealed file, no DFT data. Reads only
data/experimental_clean.csv (sha256 pinned; through the registered run_extraction.load_measured via campaign_extract.measured) and applies
the registered extraction (analysis_2026-10-06_extraction: extraction.py / run_extraction.py, PROTOCOL.md; amendment A1 window) UNCHANGED
to every replicate. Writes one JSON (--out).

  python analysis_2026-10-10_campaign/mc_measured_extraction.py run [--out OUT.json]

These curves were seen long before (2026-10-06 extraction; every campaign stage is calibrated on them): this is the uncertainty of the
EXTRACTION, not a blind test, and it is not a prediction interval.
Noise model (A57 (b); every element ASSUMED; the fab has not supplied the SMU model or range, so no instrument specification is used):
  residual    y = log10 I_D; s = Savitzky-Golay(SG_WINDOW, SG_ORDER) smooth of y; residuals r = y - s; strata fixed on the original curve
              (off: s < log10(10 x floor); on: V_G >= 1 V; sub: the rest); circular moving-block resampling (BLOCK points) within each
              stratum (i.i.d. if the stratum has fewer than 2 x BLOCK points); y* = s + r*. This replaces the observed point-to-point
              scatter by a resampled one (no double counting of the random instrument noise, which it already contains).
  instrument  per replicate curve: gain error g ~ N(0, GAIN_SIGMA) and offset o ~ N(0, OFFSET_FRAC x floor_film):
              I* = 10^y* (1 + g) + o (systematic terms that the scatter cannot show).
Fixed windows as registered (no re-tuning): I_CC 1e-9 and 5e-10 A/um; SS window 5e-11..5e-10 A/um with the registered floor rule; the A1
window [r, 10 r] x I_on,MEASURED fixed at its value from the original curves; mu_FE at the native points 1.0..3.0 V (V_D 0.7 V, C_ox, W/L
as registered); power-law fit window 1..3 V; off floor = median I_D over V_G -2..-0.5 V. A replicate on which the registered analyse()
raises is counted as failed (never repaired). Output per film and quantity: registered value and registered sigma (from the original curve),
the replicate median and the 95 % percentile interval (2.5 / 97.5 %), valid / failed counts. N = 2000 replicates per film (numpy
default_rng(SEED + film index)); the power-law quantities (V_T, mu0, gamma, mu_ch; about 1 s per fit) on the first N_PL = 400 of them.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
PINS = {
    'data/experimental_clean.csv': 'e27a53e8c72169d5e19cdf666c9203f82185f3f23613d5210b47d92ad999b73c',
    'analysis_2026-10-06_extraction/extraction.py': '1ca61a1c7cec5e97ba221cc344be53c1bc0d1d79edf39817976b80d504c706e1',
    'analysis_2026-10-06_extraction/run_extraction.py': 'de7ff06f3414cb8a2947ce07663234c8b3008765caca00fcc33f376831f02c70',
    'analysis_2026-10-10_campaign/campaign_extract.py': '1f6f324a0841d50bb20baf7f94b6444d688aaf4cbdf71707594a06f26e3e63ba',
    'analysis_2026-10-10_campaign/campaign_tools.py': '3b0403d9c5cc5423cb80dabc3765f9a781b7a06b512082b6f210971a9417ab0d'}


def sha_file(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check_pins(pins=PINS, root=PKG):
    bad = [k for k, v in pins.items() if not (root / k).is_file() or sha_file(root / k) != v]
    if bad: raise SystemExit(f'refused: pinned file missing or changed: {bad}')


check_pins()
if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
import campaign_extract as ce  # noqa: E402  frozen 1f6f324a (measured(): registered loader, floors, A1 windows)
ex, rx = ce.ex, ce.rx          # registered extraction, unchanged

SEED = 20261016
N = 2000
SG_WINDOW, SG_ORDER, BLOCK = 7, 3, 5
GAIN_SIGMA, OFFSET_FRAC = 1e-3, 0.1
N_PL = 400                     # replicates that also carry the power-law fit (about 1 s each): the first N_PL of the same stream
PL_QUANTITIES = ('pl_vt_V', 'pl_mu0', 'pl_gamma', 'mu_ch_2.0', 'mu_ch_3.0')
QUANTITIES = ('vth_cc_V', 'vth_cc_5e-10_V', 'vth_elr_V', 'ss_fixed_mV_dec', 'ss_a1_mV_dec', 'mu_fe_1.0', 'mu_fe_1.5', 'mu_fe_2.0',
              'mu_fe_2.5', 'mu_fe_3.0', 'mu_ch_2.0', 'mu_ch_3.0', 'pl_vt_V', 'pl_mu0', 'pl_gamma', 'off_floor_A_per_um')
LABEL = ('extraction uncertainty of already-seen MEASURED calibration curves (not a blind test, not a prediction interval); noise model '
         'ASSUMED (the fab has not supplied the SMU model / range; instrument terms are not from a specification)')


def strata(vg, s, floor):
    off = s < math.log10(10 * floor); on = vg >= 1.0 - 1e-9
    return {'off': np.where(off & ~on)[0], 'sub': np.where(~off & ~on)[0], 'on': np.where(on)[0]}


def smooth(vg, i):
    from scipy.signal import savgol_filter
    if np.any(~np.isfinite(i)) or np.any(i <= 0): raise SystemExit('refused: non-positive or non-finite measured current (log residuals undefined)')
    y = np.log10(i); return y, savgol_filter(y, SG_WINDOW, SG_ORDER)


def block_resample(res, rng, block=BLOCK):
    n = len(res)
    if n == 0: return res.copy()
    if n < 2 * block: return res[rng.integers(0, n, n)]
    out = []
    while len(out) < n:
        k = int(rng.integers(0, n)); out.extend(res[(k + np.arange(block)) % n])
    return np.array(out[:n])


def replicate(vg, i, floor, rng, gain_sigma=GAIN_SIGMA, offset_frac=OFFSET_FRAC):
    y, s = smooth(vg, i); r = y - s; ys = s.copy()
    for idx in strata(vg, s, floor).values():
        if len(idx): ys[idx] = s[idx] + block_resample(r[idx], rng)
    g = rng.normal(0.0, gain_sigma) if gain_sigma > 0 else 0.0; o = rng.normal(0.0, offset_frac * floor) if offset_frac > 0 else 0.0
    return 10 ** ys * (1 + g) + o


def registered(vg, i, a1):
    """the registered measured-curve analysis exactly as run_extraction.main (analyse(vg, i, False, floor, sig_floor, vg, i), incl. the
    alternative power-law windows of its systematic sigma) + the fixed A1 window: registered values and registered sigmas"""
    fl, sfl = rx.floor_with_sigma(vg, i)
    m = rx.analyse(vg, i, False, fl, sfl, vg, i)
    q = {'vth_cc_V': m['vth_cc']['v'], 'vth_cc_5e-10_V': m['vth_cc_10nA']['v'], 'vth_elr_V': m['elr']['v'], 'ss_fixed_mV_dec': m['ss']['ss'],
         'ss_a1_mV_dec': ex.ss_window(vg, i, a1[0], a1[1], False)['ss'], 'pl_vt_V': m['pl']['vt'], 'pl_mu0': m['pl']['mu0'],
         'pl_gamma': m['pl']['gamma'], 'off_floor_A_per_um': fl}
    for v in ('1.0', '1.5', '2.0', '2.5', '3.0'): q[f'mu_fe_{v}'] = m['mu_fe'][v]['mu_fe']
    for v in ('2.0', '3.0'): q[f'mu_ch_{v}'] = m['mu_ch'][v]['mu_ch']
    sig = {'vth_cc_V': m['vth_cc']['sig'], 'vth_cc_5e-10_V': m['vth_cc_10nA']['sig'], 'vth_elr_V': m['elr']['sig'], 'ss_fixed_mV_dec': m['ss']['sig'],
           'pl_vt_V': m['pl']['tot_vt'], 'pl_mu0': m['pl']['tot_mu0'], 'pl_gamma': m['pl']['tot_gamma'], 'off_floor_A_per_um': sfl}
    for v in ('1.0', '1.5', '2.0', '2.5', '3.0'): sig[f'mu_fe_{v}'] = m['mu_fe'][v]['sig']
    for v in ('2.0', '3.0'): sig[f'mu_ch_{v}'] = m['mu_ch'][v]['sig']
    return {k: (float(v) if v is not None and np.isfinite(v) else None) for k, v in q.items()}, sig


def extract(vg, i, a1, with_pl=True):
    """replicate values: the same registered functions in the same order as run_extraction.analyse (is_sim False), without the shifted
    SS windows and the alternative power-law windows (they feed only the registered systematic sigma, not a quantity); the power-law
    fit (PL_QUANTITIES) only when with_pl. Checked against registered() on the original curve before any replicate (mirror_check)."""
    fl, sfl = rx.floor_with_sigma(vg, i)
    q = {'vth_cc_V': ex.crossing(vg, i, rx.I_CC, False)['v'], 'vth_cc_5e-10_V': ex.crossing(vg, i, rx.I_CC10, False)['v'],
         'ss_fixed_mV_dec': rx.ss_rule(vg, i, *rx.WIN, False, fl, sfl)['ss'], 'ss_a1_mV_dec': ex.ss_window(vg, i, a1[0], a1[1], False)['ss'],
         'off_floor_A_per_um': fl}
    _, sig_pts = ex.gm_sigma(vg, i); q['vth_elr_V'] = ex.vth_elr(vg, i, sig_pts)['v']
    mu = ex.MU_FACTOR * ex.gm(vg, i)
    for v in rx.VG_REPORT:
        k = int(np.argmin(np.abs(vg - v)))
        if abs(vg[k] - v) > 1e-6: raise SystemExit(f'refused: no native point at {v} V')
        q[f'mu_fe_{v:.1f}'] = float(mu[k])
    if with_pl:
        prim = ex.pl_fit(vg, i, *rx.FIT_PRIMARY); m0 = ex.mu_ch(np.array(rx.VG_REPORT), prim)
        q.update(pl_vt_V=prim['vt'], pl_mu0=prim['mu0'], pl_gamma=prim['gamma'],
                 **{f'mu_ch_{v:.1f}': float(m0[j]) for j, v in enumerate(rx.VG_REPORT) if v in (2.0, 3.0)})
    return {k: (float(v) if v is not None and np.isfinite(v) else None) for k, v in q.items()}


def mirror_check(reg, mir):
    bad = [k for k in QUANTITIES if (reg.get(k) is None) != (mir.get(k) is None)
           or (reg.get(k) is not None and abs(reg[k] - mir[k]) > 1e-9 * max(1.0, abs(reg[k])))]
    if bad: raise SystemExit(f'refused: replicate extraction does not reproduce the registered analysis on the original curve: {bad}')


def film_mc(vg, i, floor, a1, n=N, seed=SEED, n_pl=None, **kw):
    n_pl = N_PL if n_pl is None else n_pl
    rng = np.random.default_rng(seed); reg, sig = registered(vg, i, a1); mirror_check(reg, extract(vg, i, a1))
    vals = {k: [] for k in QUANTITIES}; failed = 0
    for j in range(n):
        Is = replicate(vg, i, floor, rng, **kw); pl = j < n_pl
        try: q = extract(vg, Is, a1, with_pl=pl)
        except Exception: failed += 1; q = {}
        for k in QUANTITIES:
            if k in PL_QUANTITIES and not pl: continue
            vals[k].append(q.get(k))
    out = {}
    for k in QUANTITIES:
        a = np.array([np.nan if v is None else v for v in vals[k]], float); f = np.isfinite(a)
        out[k] = {'registered_value': reg.get(k), 'registered_sigma': (float(sig[k]) if sig.get(k) is not None else None), 'n_replicates': int(len(a)),
                  'n_valid': int(f.sum()), 'median': float(np.median(a[f])) if f.any() else None,
                  'ci95': [float(z) for z in np.percentile(a[f], (2.5, 97.5))] if f.any() else None}
    return {'n': n, 'n_pl': n_pl, 'n_failed_replicates': failed, 'fixed_a1_window_A_per_um': list(a1), 'floor_A_per_um': floor, 'quantities': out}


def run(n=N, seed=SEED):
    info, r = ce.measured(); res = {}
    for k, t in enumerate(rx.FILMS):
        M = info[t]; res[str(t)] = film_mc(M['vg'], M['i'], M['floor'], tuple(M['a1_window']), n, seed + k)
    return {'tool': 'mc_measured_extraction.py (register A57)', 'code_sha256': sha_file(__file__), 'pins': PINS, 'seed': SEED, 'n': n,
            'n_pl': N_PL, 'noise_model': {'sg': [SG_WINDOW, SG_ORDER], 'block': BLOCK, 'gain_sigma': GAIN_SIGMA, 'offset_frac_of_floor': OFFSET_FRAC},
            'a1_r': r, 'label': LABEL, 'films': res, 'excluded': '31.8 nm (not a registered extraction film, run_extraction.FILMS)'}


def main(argv):
    if not argv or argv[0] != 'run' or ('--out' in argv and argv.index('--out') + 1 >= len(argv)):
        print(__doc__.split('\n\n')[1]); return 2
    txt = json.dumps(run(), indent=1, default=float)
    if '--out' in argv: Path(argv[argv.index('--out') + 1]).write_text(txt)
    print(f'sha256 {hashlib.sha256(txt.encode()).hexdigest()}'); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
