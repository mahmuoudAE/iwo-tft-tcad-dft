#!/usr/bin/env python3
"""Identical metric extraction for experimental and simulated ID-VG curves (no simulator call).

Definitions (the target paper does not define its extraction; these are stated conventions):
  Vth_cc     : constant-current threshold, Vg where Id = 1e-9 A/um (log-linear interpolation between
               adjacent points; no extrapolation). 1e-9 A/um x (L/W = 20/290) = 6.9e-11 A per square... reported as A/um.
  Vth_lin    : linear extrapolation of Id at maximum transconductance (secant gm on the 0.05 V grid), Vd = 0.7 V.
  SS         : two definitions, both applied identically to measured and simulated curves:
               SS_min (primary, key SS_mV_dec): minimum over 0.2 V centred windows (5 points) of dVg/dlog10(Id),
                      restricted to Id > 5 x the MEASURED off-band median of the same thickness (applied to the
                      simulated curve as well, so both curves are evaluated over the same current range; the solver
                      reaches 1e-19 A/um whereas the measured floors are 5e-15..6.6e-12) and below 0.01 x Id(+3 V).
               SS_cc  (secondary): average slope between the constant-current crossings at 1e-10 and 1e-8 A/um,
                      SS_cc = [Vg(1e-8) - Vg(1e-10)] / 2 decades, anchored to the same current band as Vth_cc.
  mu_FE      : gm_max * L / (W Cox Vd) with W = 1 um (A/um data), L = 20 um, Cox = 8.955e-7 F/cm^2, Vd = 0.7 V.
               This is the linear-region estimator applied at Vd = 0.7 V; it is an apparent field-effect
               mobility, not the band mobility.
  Ion        : Id at Vg = +3 V.   Ioff : minimum Id over the sweep (experiment); for simulation the minimum
               positive Id together with the count of native zeros (never replaced by a floor).
  Ion/Ioff   : ratio of the above (for a simulated curve with native zeros it is reported as '> Ion/Imin_positive').
Percentage errors are not reported for sign-changing or near-zero quantities (Vth): absolute differences only.
"""
import csv, json, math
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
COX = 8.955369814335959e-07; L_CM = 20e-4; W_CM = 1e-4; VD = 0.7; ICC = 1e-9

def crossing(vg, idv, level):
    for i in range(len(vg) - 1):
        a, b = idv[i], idv[i + 1]
        if a > 0 and b > 0 and (a - level) * (b - level) <= 0 and a != b:
            return float(vg[i] + (vg[i + 1] - vg[i]) * (math.log10(level) - math.log10(a)) / (math.log10(b) - math.log10(a)))
    return None

_EXP_FLOOR = {}
def exp_off_floor(t_nm):
    """Measured off-band median (Vg in [-2, -0.5]) of the given thickness, cached; None if unavailable."""
    if t_nm is None: return None
    if t_nm not in _EXP_FLOOR:
        try:
            vg, idv = load_curve(ROOT / 'data' / 'experimental_clean.csv', t_nm)
            _EXP_FLOOR[t_nm] = float(np.median(idv[(vg >= -2) & (vg <= -.5)]))
        except Exception: _EXP_FLOOR[t_nm] = None
    return _EXP_FLOOR[t_nm]

def metrics(vg, idv, is_sim=False, t_nm=None):
    vg = np.asarray(vg, float); idv = np.asarray(idv, float)
    pos = idv > 0; n_zero = int((~pos).sum())
    off = float(np.median(idv[(vg >= -2) & (vg <= -.5)])) if not is_sim else None
    floor = off if not is_sim else exp_off_floor(t_nm)   # same current range for both curves
    v_lo, v_hi = crossing(vg, idv, ICC / 10), crossing(vg, idv, ICC * 10)
    ss_cc = (None if (v_lo is None or v_hi is None) else (v_hi - v_lo) / 2.0 * 1000.0)
    gm = np.gradient(idv, vg); i_gm = int(np.argmax(gm)); gm_max = float(gm[i_gm])
    vth_lin = float(vg[i_gm] - idv[i_gm] / gm_max) if gm_max > 0 else None
    ion = float(idv[-1])
    thr_lo = (5 * floor) if floor is not None else None
    lg = np.where(pos, np.log10(np.where(pos, idv, 1)), np.nan)
    ss = None
    for i in range(2, len(vg) - 2):
        seg = idv[i - 2:i + 3]
        if np.all(seg > 0) and seg[0] < 0.01 * ion and (thr_lo is None or seg[0] > thr_lo):
            d = (lg[i + 2] - lg[i - 2]); w = vg[i + 2] - vg[i - 2]
            if d > 0:
                cand = w / d * 1000.0; ss = cand if ss is None else min(ss, cand)
    imin = float(idv[pos].min()) if pos.any() else None
    return {'Vth_cc_1e-9_V': crossing(vg, idv, ICC), 'Vth_lin_V': vth_lin, 'SS_mV_dec': ss, 'SS_min_window_mV_dec': ss, 'SS_cc_1e-10_1e-8_mV_dec': ss_cc, 'gm_max_A_V_um': gm_max, 'mu_FE_cm2Vs': gm_max * L_CM / (W_CM * COX * VD),
            'Ion_A_per_um': ion, 'Ioff_A_per_um': imin, 'Ioff_definition': 'min Id over sweep' + (' (min POSITIVE; native zeros counted)' if is_sim else ''), 'native_zero_count': n_zero,
            'Ion_over_Ioff': (ion / imin) if imin else None, 'off_band_median_A_per_um': off}

def load_curve(path_or_rows, thickness=None):
    rows = list(csv.DictReader(Path(path_or_rows).open()))
    if thickness is not None: rows = [r for r in rows if abs(float(r['thickness_nm']) - thickness) < 1e-6]
    return np.array([float(r['vg_V']) for r in rows]), np.array([float(r[[c for c in r if c.startswith('id') or c.startswith('atlas')][0]]) for r in rows])

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--csv', default=str(ROOT / 'data' / 'experimental_clean.csv')); ap.add_argument('--thickness', type=float); ap.add_argument('--sim', action='store_true'); a = ap.parse_args()
    for t in ([a.thickness] if a.thickness else [2.0, 6.3, 13.2, 31.8]):
        vg, idv = load_curve(a.csv, t); print(t, json.dumps(metrics(vg, idv, a.sim, t), indent=1))
