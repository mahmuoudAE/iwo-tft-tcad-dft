"""S6 common helpers (read-only use of package files; no simulator call).
Robust metrics: fixed-current crossings (log-linear AND PCHIP-on-log10 interpolation, difference = interpolation
uncertainty), fixed-current SS, on-state shape markers. The package extractor (scripts/extract_metrics.py) is imported
unchanged for the legacy metrics, applied exactly as run_atlas.py does (np.interp of the native simulated grid onto the
0.05 V measurement grid).
"""
import csv, json, math, sys
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator

PKG = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PKG / 'scripts'))
from extract_metrics import metrics as pkg_metrics, load_curve  # noqa: E402

RUNS = PKG / 'results' / 'runs'
COX = 8.955369814335959e-07; L_CM = 20e-4; W_CM = 1e-4; VD = 0.7
K_B = 8.617333262e-5  # eV/K

def run_dir(rid):
    m = list(RUNS.glob(rid + '_*'))
    if len(m) != 1: raise FileNotFoundError(rid)
    return m[0]

def read_idvg(rid):
    rows = (run_dir(rid) / 'idvg.dat').read_text().split('\n')[4:]
    xy = np.array([[float(v) for v in r.split()] for r in rows if r.strip()])
    vg = np.round(xy[:, 0], 6); vg[np.abs(vg) < 1e-9] = 0.0
    return vg, xy[:, 1]

def read_exec(rid):
    return json.loads((run_dir(rid) / 'execution.json').read_text())

def meas(t):
    return load_curve(PKG / 'data' / 'experimental_clean.csv', t)

def floor_med(t):
    vg, i = meas(t); return float(np.median(i[(vg >= -2) & (vg <= -.5)]))

def crossing_lin(vg, idv, level):
    for k in range(len(vg) - 1):
        a, b = idv[k], idv[k + 1]
        if a > 0 and b > 0 and (a - level) * (b - level) <= 0 and a != b:
            return float(vg[k] + (vg[k + 1] - vg[k]) * (math.log10(level) - math.log10(a)) / (math.log10(b) - math.log10(a)))
    return None

def crossing_pchip(vg, idv, level):
    """Monotone cubic on log10(Id) over the monotone positive branch around the first crossing."""
    k0 = None
    for k in range(len(vg) - 1):
        a, b = idv[k], idv[k + 1]
        if a > 0 and b > 0 and (a - level) * (b - level) <= 0 and a != b: k0 = k; break
    if k0 is None: return None
    lo, hi = max(0, k0 - 3), min(len(vg), k0 + 5)
    x, y = vg[lo:hi], idv[lo:hi]
    if np.any(y <= 0) or np.any(np.diff(y) <= 0): return crossing_lin(vg, idv, level)
    f = PchipInterpolator(x, np.log10(y)); xs = np.linspace(vg[k0], vg[k0 + 1], 2001); ys = f(xs)
    j = int(np.argmin(np.abs(ys - math.log10(level)))); return float(xs[j])

def robust(vg, idv, floor_sub=None):
    """Fixed-current markers on a curve (native grid). floor_sub: subtract a constant (measured floor) first."""
    i = np.array(idv, float) - (floor_sub or 0.0)
    out = {}
    for lab, lev in [('V_1e-11', 1e-11), ('V_1e-10', 1e-10), ('V_1e-9', 1e-9), ('V_1e-8', 1e-8), ('V_1e-7', 1e-7), ('V_3e-7', 3e-7)]:
        out[lab] = crossing_lin(vg, i, lev); out[lab + '_pchip'] = crossing_pchip(vg, i, lev)
    def ss(a, b, key=''):
        va, vb = out['V_%s%s' % (a, key)], out['V_%s%s' % (b, key)]
        if va is None or vb is None: return None
        return (vb - va) / (math.log10(float(b)) - math.log10(float(a))) * 1000.0
    out['SS_11_10'] = ss('1e-11', '1e-10'); out['SS_10_9'] = ss('1e-10', '1e-9'); out['SS_9_8'] = ss('1e-9', '1e-8'); out['SS_10_8'] = ss('1e-10', '1e-8')
    out['SS_11_10_pchip'] = ss('1e-11', '1e-10', '_pchip'); out['SS_10_9_pchip'] = ss('1e-10', '1e-9', '_pchip'); out['SS_10_8_pchip'] = ss('1e-10', '1e-8', '_pchip')
    out['gap7'] = (out['V_1e-7'] - out['V_1e-9']) if (out['V_1e-7'] is not None and out['V_1e-9'] is not None) else None
    return out

def legacy(vg_native, id_native, t, is_sim=True):
    """Package metrics exactly as run_atlas.py computes them for a simulation (np.interp onto the 0.05 V grid)."""
    vgm, _ = meas(t)
    if is_sim:
        pred = np.interp(vgm, vg_native, id_native); return pkg_metrics(vgm, pred, True, t)
    return pkg_metrics(vg_native, id_native, False, t)

def all_metrics(vg, idv, t, is_sim=True, floor_sub=None):
    m = legacy(vg, idv, t, is_sim); r = robust(vg, idv, floor_sub)
    m.update(r); m['gap_lin'] = (m['Vth_lin_V'] - m['Vth_cc_1e-9_V']) if (m['Vth_lin_V'] is not None and m['Vth_cc_1e-9_V'] is not None) else None
    m['Ion_over_gm_V'] = m['Ion_A_per_um'] / m['gm_max_A_V_um']
    return m

def fmt(x, f='{:.3f}'):
    return '-' if x is None else f.format(x)
