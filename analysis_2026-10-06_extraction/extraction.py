#!/usr/bin/env python3
"""Extraction methods of PROTOCOL.md (threshold voltage, subthreshold swing, on-state mobility) for a transfer curve
measured or simulated at one drain bias. Pure functions without I/O; the same code is applied to data and TCAD.

Currents are per um of channel width (A/um), so W = 1 um in every formula below.
"""
import math

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq, least_squares
from scipy.signal import savgol_filter

Q = 1.602176634e-19                   # C
KB = 8.617333262e-5                   # eV/K
COX = 8.955369814335959e-07           # F/cm^2, same constant as scripts/extract_metrics.py
L_CM, W_CM, VD, T = 20e-4, 1e-4, 0.7, 300.0
S_TH = 1e3 * KB * T * math.log(10)    # thermionic limit, mV/dec (59.52 at 300 K)
MU_FACTOR = L_CM / (W_CM * COX * VD)  # mu_FE = MU_FACTOR * gm

# TCAD numerical uncertainty budget (report, table tab:d2-uncertainty)
SIM_SIG_V, SIM_SIG_SS, SIM_REL_GM = 1.5e-3, 1.0, 0.007


# ---------------------------------------------------------------- crossings (threshold, SS)
def upward_crossings(vg, i, level, vmax=3.0):
    """Indices k with 0 < i[k] < level <= i[k+1] and vg[k+1] <= vmax."""
    return [k for k in range(len(vg) - 1)
            if i[k] > 0 and i[k + 1] > 0 and i[k] < level <= i[k + 1] and vg[k + 1] <= vmax + 1e-9]


def cross_loglin(vg, i, level, k):
    a, b = math.log10(i[k]), math.log10(i[k + 1])
    return float(vg[k] + (vg[k + 1] - vg[k]) * (math.log10(level) - a) / (b - a))


def cross_pchip(vg, i, level, k, half=4):
    """Monotone-cubic (PCHIP) interpolation of log10 I over up to 2*half+2 points around the bracket."""
    lo, hi = max(0, k - half), min(len(vg), k + half + 2)
    v, c = vg[lo:hi], i[lo:hi]
    ok = c > 0
    f = PchipInterpolator(v[ok], np.log10(c[ok]))
    return float(brentq(lambda x: f(x) - math.log10(level), vg[k], vg[k + 1]))


def noise_log_quadratic(vg, i, k, n=9):
    """PROTOCOL 3.4 as written: std of the residuals of a quadratic fit of log10 I over n points centred on the
    bracket. Retired (deviation D1 in RESULTS.md): on the noise-free TCAD curves it returns 0.006-0.04 dec, i.e. it
    measures the curvature that a quadratic cannot follow, not noise. Kept for the record."""
    lo = max(0, min(len(vg) - n, k - n // 2 + 1))
    v, c = vg[lo:lo + n], i[lo:lo + n]
    ok = c > 0
    if ok.sum() < 5:
        return float('nan')
    y = np.log10(c[ok]); x = v[ok]
    r = y - np.polyval(np.polyfit(x, y, 2), x)
    return float(np.sqrt(np.sum(r ** 2) / (len(r) - 3)))


def noise_log(vg, i, level, k, span=1.5, half=7, nmin=9, order=4):
    """Noise of log10 I at a current level (deviation D1): robust order-4 difference estimator
    sigma = 1.4826 MAD(D^4 y) / sqrt(C(8, 4)) on the contiguous points within +-span decades of the level and within
    +-half grid points of the bracket (at least nmin points). A 4th difference removes any cubic trend, so a smooth
    curve gives ~0: on the TCAD curves it returns 1e-4 to 2e-3 dec, 0-15 % of the measured values."""
    ok = i > 0
    lg = np.full(len(i), np.nan)
    lg[ok] = np.log10(i[ok])
    ll = math.log10(level)
    a = b = k
    while a - 1 >= max(0, k - half) and ok[a - 1] and abs(lg[a - 1] - ll) <= span:
        a -= 1
    while b + 1 <= min(len(i) - 1, k + 1 + half) and ok[b + 1] and abs(lg[b + 1] - ll) <= span:
        b += 1
    while b - a + 1 < nmin:
        a, b = max(0, a - 1), min(len(i) - 1, b + 1)
    y = lg[a:b + 1]
    y = y[np.isfinite(y)]
    d = np.diff(y, order)
    return float(1.4826 * np.median(np.abs(d - np.median(d))) / math.sqrt(math.comb(2 * order, order)))


def crossing(vg, i, level, is_sim):
    """V_G at I_D = level with its uncertainty (PROTOCOL 3.1, 3.4)."""
    ks = upward_crossings(vg, i, level)
    if not ks:
        return dict(v=None, n_cross=0)
    k = ks[-1]
    v = cross_loglin(vg, i, level, k)
    vp = cross_pchip(vg, i, level, k)
    slope = (vg[k + 1] - vg[k]) / (math.log10(i[k + 1]) - math.log10(i[k]))   # V/dec at the crossing
    s_int = abs(v - vp)
    s_log = noise_log(vg, i, level, k)
    s_log_q = noise_log_quadratic(vg, i, k)
    if is_sim:
        s_noise, s_tot = 0.0, SIM_SIG_V
    else:
        s_noise = s_log * slope
        s_tot = math.hypot(s_noise, s_int)
    return dict(v=v, v_pchip=vp, k=k, n_cross=len(ks), slope_V_per_dec=slope, sigma_log10=s_log,
                sigma_log10_quadratic_retired=s_log_q, sig_noise=s_noise, sig_interp=s_int, sig=s_tot,
                bracket=[(float(vg[k]), float(i[k])), (float(vg[k + 1]), float(i[k + 1]))])


def ss_window(vg, i, lo, hi, is_sim):
    """Two-point SS over [lo, hi] (A/um), mV/dec, with uncertainty (PROTOCOL 3.2, 3.4)."""
    a, b = crossing(vg, i, lo, is_sim), crossing(vg, i, hi, is_sim)
    if a['v'] is None or b['v'] is None:
        return dict(ss=None, lo=a, hi=b)
    dec = math.log10(hi / lo)
    ss = 1e3 * (b['v'] - a['v']) / dec
    ss_p = 1e3 * (b['v_pchip'] - a['v_pchip']) / dec
    if is_sim:
        sig = SIM_SIG_SS
    else:
        sig = math.hypot(1e3 * math.hypot(a['sig_noise'], b['sig_noise']) / dec, abs(ss - ss_p))
    return dict(ss=ss, ss_pchip=ss_p, sig=sig, lo=a, hi=b)


def local_ss(vg, i):
    """Local SS = dV_G/dlog10 I_D (mV/dec) by central differences, for plotting against I_D."""
    ok = i > 0
    v, c = vg[ok], i[ok]
    d = np.gradient(np.log10(c), v)
    m = d > 0
    return c[m], 1e3 / d[m]


def off_floor(vg, i):
    return float(np.median(i[(vg >= -2) & (vg <= -0.5)]))


def n_ss(ss_mv):
    """Equivalent trap density (SS/S_th - 1) C_ox/q in cm^-2 eV^-1 (PROTOCOL 3.2)."""
    return (ss_mv / S_TH - 1.0) * COX / Q


# ---------------------------------------------------------------- transconductance and mobility
def gm(vg, i):
    return np.gradient(i, vg)          # second-order central differences, non-uniform grids allowed


def gm_sigma(vg, i, lo=1.0, hi=3.0, window=7, order=2, local_half=5):
    """Noise of gm from the residual r = central-difference gm - Savitzky-Golay gm (window 7, order 2); uniform grid.
    Returns (global std of r over [lo, hi] = PROTOCOL 3.4 as written, per-point local std of r over +-local_half
    points = deviation D2, used for the values). The one-sided end points get a factor 2 (difference over h, not 2h)."""
    h = float(np.median(np.diff(vg)))
    r = gm(vg, i) - savgol_filter(i, window, order, deriv=1, delta=h)
    m = (vg >= lo - 1e-9) & (vg <= hi + 1e-9)
    glob = float(np.std(r[m], ddof=1))
    loc = np.array([np.std(r[max(0, k - local_half):k + local_half + 1], ddof=1) for k in range(len(vg))])
    loc[0] *= 2.0
    loc[-1] *= 2.0
    return glob, loc


def vth_elr(vg, i, sig_gm_pts):
    """Linear extrapolation with the V_D/2 correction and the two validity flags (PROTOCOL 3.1, T3).
    sig_gm_pts: per-point gm uncertainty (array) or a scalar."""
    g = gm(vg, i)
    s = np.broadcast_to(np.asarray(sig_gm_pts, float), g.shape)
    k = int(np.argmax(g))
    v_int = float(vg[k] - i[k] / g[k])
    v = v_int - VD / 2
    sig_v = float(i[k] * s[k] / g[k] ** 2)            # from the slope; the current term is negligible
    return dict(v=v, v_intercept=v_int, sig=sig_v, vg_star=float(vg[k]), gm_max=float(g[k]), gm_end=float(g[-1]),
                sweep_limited=bool(g[k] - g[-1] <= 2 * s[-1]), linear_regime=bool(vg[k] - v >= VD))


# ---------------------------------------------------------------- power-law gradual-channel model
def pl_current(vg, vt, mu0, gam):
    """I_D (A/um) of the gradual-channel model with mu(u) = mu0 (u/1V)^gam at V_D (PROTOCOL 3.3, M2)."""
    u = np.clip(np.asarray(vg, float) - vt, 0.0, None)
    return (W_CM / L_CM) * COX * mu0 * (u ** (gam + 2) - np.clip(u - VD, 0.0, None) ** (gam + 2)) / (gam + 2)


def pl_fit(vg, i, lo, hi):
    """Least squares on log10 I_D over [lo, hi]; multi-start; returns parameters, uncertainties and fit quality."""
    m = (vg >= lo - 1e-9) & (vg <= hi + 1e-9) & (i > 0)
    x, y = vg[m], np.log10(i[m])
    vt_max = lo - 0.02

    def res(p):
        return np.log10(np.clip(pl_current(x, p[0], math.exp(p[1]), p[2]), 1e-30, None)) - y
    best = None
    for vt0 in np.arange(-1.0, vt_max - 0.03, 0.1):
        for g0 in (0.0, 0.5, 1.0, 2.0):
            r = least_squares(res, [vt0, math.log(10.0), g0],
                              bounds=([-3.0, math.log(1e-3), -0.9], [vt_max, math.log(1e4), 5.0]))
            if best is None or r.cost < best.cost:
                best = r
    p, n = best.x, len(x)
    dof = n - 3
    s2 = 2 * best.cost / dof
    try:
        cov = np.linalg.inv(best.jac.T @ best.jac) * s2
        sd = np.sqrt(np.diag(cov))
        corr = float(cov[0, 2] / (sd[0] * sd[2]))
    except np.linalg.LinAlgError:
        cov, sd, corr = None, [float('nan')] * 3, float('nan')
    mu0 = math.exp(p[1])
    return dict(vt=float(p[0]), mu0=mu0, gamma=float(p[2]), sig_vt=float(sd[0]), sig_mu0=float(mu0 * sd[1]),
                sig_gamma=float(sd[2]), corr_vt_gamma=corr, rms_log10=float(np.sqrt(np.mean(best.fun ** 2))), n=n,
                at_bound=bool(abs(p[0] - vt_max) < 1e-4), range=[lo, hi],
                cov=None if cov is None else cov.tolist())   # covariance of (V_T, ln mu0, gamma)


def mu_ch(vg, fit):
    u = np.asarray(vg, float) - fit['vt']
    return np.where(u > 0, fit['mu0'] * np.clip(u, 1e-12, None) ** fit['gamma'], np.nan)


def mu_ch_sigma(vg, fit):
    """Delta-method standard error of mu_ch(V_G) from the fit covariance."""
    u = np.atleast_1d(np.asarray(vg, float)) - fit['vt']
    out = np.full(u.shape, np.nan)
    if fit.get('cov') is None:
        return out
    m = u > 0
    mu = fit['mu0'] * u[m] ** fit['gamma']
    jac = np.stack([-fit['gamma'] * mu / u[m], mu, mu * np.log(u[m])], axis=1)
    out[m] = np.sqrt(np.einsum('ij,jk,ik->i', jac, np.array(fit['cov']), jac))
    return out
