"""Common tools for the band-structure / effective-mass / TCAD-parameter study (analysis_2026-10-13_full/bands_masses).

Reads raw Quantum ESPRESSO outputs through ../qeio.py (independent parsers with file:line provenance) and the
outputs of the sibling re-derivation scripts (../out/f03, f05, f08, f09, f10 JSON) where a quantity (vacuum level,
two-step alignment, projections) was already re-derived from raw files there.

Conventions
- k in 1/A: k_cart printed by pw.x (units 2 pi/alat) times 2 pi / alat (alat of THAT output; for the bulk band runs
  on the vc-relax save alat = 16.5570 bohr = 8.7616 A, the initial vc-relax |a1|, while the cell is the relaxed one).
- hbar^2/(2 m0) = 3.80998212 eV A^2 (qeio.H2M); kT(300 K) = 25.852 meV.
- Electron masses from E_CB(k) - E_CB(0); hole masses from -(E_VB(k) - E_VB(0)) (positive for a band that goes down).
- Eigenvalues are printed with 4 decimals (0.1 meV): the rounding enters every fit as a uniform error (sigma 0.029 meV
  per value); it is propagated into each anchored-parabola mass (field 'sigma_round') with the shared, rounded E(Gamma)
  treated as correlated across the differences.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import qeio as q  # noqa: E402
import figstyle as fs  # noqa: E402,F401  (sets the plain plotting style)
import matplotlib.pyplot as plt  # noqa: E402

OUT = HERE / 'out'
FIG = HERE / 'figures'
PARENT_OUT = HERE.parent / 'out'
H2M = q.H2M
KB = q.KB
T = 300.0
KT = KB * T
SIG_ONE = 0.1e-3 / math.sqrt(12)                       # eV, rounding error of one printed eigenvalue (4 decimals)
SIG_DIFF = SIG_ONE * math.sqrt(2)                      # eV, of a difference of two printed eigenvalues (kept for reference)
WINDOWS = (2, 3, 4, 6, 10)                            # number of non-Gamma points in the fit window
# constants (CODATA 2018)
HBAR = 1.054571817e-34
M0 = 9.1093837015e-31
QE_ = 1.602176634e-19
KB_J = 1.380649e-23


def save(fig, stem):
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / f'{stem}.pdf')
    fig.savefig(FIG / f'{stem}.png', dpi=300)
    plt.close(fig)
    print('saved', stem)


def dump(name, obj):
    OUT.mkdir(exist_ok=True)
    (OUT / f'{name}.json').write_text(json.dumps(obj, indent=1, default=_default))


def _default(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if hasattr(o, 'tolist'):
        return o.tolist()
    return str(o)


def load_parent(name):
    return json.loads((PARENT_OUT / f'{name}.json').read_text())


def r(x, n=4):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), n)


# ------------------------------------------------------------------ band data
def read_bands(p):
    """Eigenvalues of the last band / SCF section of a pw.x output.
    Returns dict(K [nk x 3] 1/A, E [nk x nb] eV, src [nk], alat_A, nelec, version, path)."""
    p = Path(p)
    bl = q.eig_blocks(p)
    if not bl:
        raise LookupError(f'no eigenvalue blocks in {q.rel(p)}')
    al, sal = q.alat_A(p)
    nb = min(len(b[1]) for b in bl)
    E = np.array([b[1][:nb] for b in bl])
    K = np.array([b[0] for b in bl]) * 2 * np.pi / al
    ne, sne = q.nelec(p)
    ver, _ = q.version(p)
    return {'K': K, 'E': E, 'src': [b[2] for b in bl], 'alat_A': al, 'alat_src': sal, 'nelec': ne, 'nelec_src': sne,
            'version': ver, 'path': q.rel(p), 'nk': len(bl), 'nb': nb}


def line_indices(K, direction, tol=1e-4):
    """Indices of the k-points on the ray from Gamma along `direction` (Cartesian), Gamma first, sorted by |k|."""
    d = np.asarray(direction, float)
    d /= np.linalg.norm(d)
    idx = []
    for i, k in enumerate(K):
        n = np.linalg.norm(k)
        if n < 1e-9:
            if not any(x == 0.0 for x, _ in idx):      # first Gamma only (a path may return to Gamma)
                idx.append((0.0, i))
            continue
        if np.linalg.norm(np.cross(k / n, d)) < tol and np.dot(k, d) > 0:
            idx.append((n, i))
    idx.sort()
    return [i for _, i in idx]


# ------------------------------------------------------------------ mass fits
def fit_line(k, e, carrier='e'):
    """Masses from one line through an extremum at k = 0.
    k: |k| (1/A), k[0] = 0; e: eigenvalues of ONE band (eV). carrier 'e': dE = e - e0; 'h': dE = -(e - e0).
    Returns windows (anchored parabola, free-intercept parabola), quartic, Kane fits and a finite-difference estimate."""
    k = np.asarray(k, float)
    dE = (np.asarray(e, float) - e[0]) * (1.0 if carrier == 'e' else -1.0)
    out = {'k_invA': [r(x, 5) for x in k], 'dE_meV': [r(x * 1000, 2) for x in dE], 'windows': {}}
    for n in WINDOWS:
        if n >= len(k):
            continue
        kk, ee = k[1:n + 1], dE[1:n + 1]
        c = float(np.sum(ee * kk ** 2) / np.sum(kk ** 4))
        s4, s2 = float(np.sum(kk ** 4)), float(np.sum(kk ** 2))
        sig_c = SIG_ONE * math.sqrt(s4 + s2 * s2) / s4   # the rounded E(Gamma) enters every difference (correlated; Codex 2026-10-14)
        A = np.vstack([np.ones(n + 1), k[:n + 1] ** 2]).T
        (c0, c1), *_ = np.linalg.lstsq(A, dE[:n + 1], rcond=None)
        out['windows'][str(n)] = {
            'kmax_invA': r(kk[-1], 4), 'Emax_meV': r(ee[-1] * 1000, 1),
            'm_anchored': r(H2M / c, 4) if c != 0 else None,
            'sigma_round': r(abs(H2M / c) * sig_c / abs(c), 4) if c != 0 else None,   # magnitude (Codex 2026-10-14)
            'm_intercept': r(H2M / c1, 4) if c1 != 0 else None, 'intercept_meV': r(c0 * 1000, 2)}
    kk, ee = k[1:], dE[1:]
    if len(kk) >= 4:
        A = np.vstack([kk ** 2, kk ** 4]).T
        (c2, c4), *_ = np.linalg.lstsq(A, ee, rcond=None)
        out['quartic_all'] = {'m_edge': r(H2M / c2, 4) if c2 != 0 else None, 'c4_eVA4': r(c4, 2), 'n': len(kk)}
    # Kane: H2M k^2 = m dE + m alpha dE^2 (linear in m and m*alpha), windows of >= 4 points
    out['kane'] = {}
    for n in (4, 6, 10):
        if n >= len(k) or np.any(dE[1:n + 1] <= 0):
            continue
        A = np.vstack([dE[1:n + 1], dE[1:n + 1] ** 2]).T
        (m, ma), *_ = np.linalg.lstsq(A, H2M * k[1:n + 1] ** 2, rcond=None)
        resid = H2M * k[1:n + 1] ** 2 - A @ np.array([m, ma])
        out['kane'][str(n)] = {'m_edge': r(m, 4), 'alpha_per_eV': r(ma / m, 3), 'Emax_meV': r(dE[n] * 1000, 1),
                               'rms_resid_meV_equiv': r(math.sqrt(float(np.mean(resid ** 2))) / max(m, 1e-9) * 1000, 3)}
    if len(k) >= 3 and dE[1] != 0:
        k1, k2, e1, e2 = k[1], k[2], dE[1], dE[2]
        c = (e1 * k2 ** 4 - e2 * k1 ** 4) / (k1 ** 2 * k2 ** 4 - k2 ** 2 * k1 ** 4)
        out['fd_edge'] = r(H2M / c, 4) if c != 0 else None
    return out


def recommended(fit):
    """Band-edge mass: Kane fit over the widest window with >= 4 points (k^2 and k^4 terms), else quartic, else anchored n=4.
    Spread: min/max of the anchored-parabola masses over all windows."""
    rec, how = None, None
    for n in ('10', '6', '4'):
        if n in fit.get('kane', {}):
            rec, how = fit['kane'][n]['m_edge'], f'Kane, {n} points'
            break
    if rec is None and fit.get('quartic_all', {}).get('m_edge'):
        rec, how = fit['quartic_all']['m_edge'], 'quartic'
    ms = [w['m_anchored'] for w in fit['windows'].values() if w['m_anchored'] is not None]
    return {'m': rec, 'method': how, 'anchored_min': min(ms) if ms else None, 'anchored_max': max(ms) if ms else None}


def offgamma_max(k, e, npts=5):
    """Interior maximum of a band along a line: parabola E = E0 - H2M (k-k0)^2 / m through the npts points around the
    largest value; returns k0, E0 and the longitudinal (hole) mass, or None if the maximum is at an end point."""
    k, e = np.asarray(k, float), np.asarray(e, float)
    i = int(np.argmax(e))
    if i == 0 or i == len(k) - 1:
        return None
    lo, hi = max(0, i - npts // 2), min(len(k), i + npts // 2 + 1)
    c2, c1, c0 = np.polyfit(k[lo:hi], e[lo:hi], 2)
    if c2 >= 0:
        return None
    k0 = -c1 / (2 * c2)
    # rounding error on the curvature of the 5-point parabola
    X = np.vstack([k[lo:hi] ** 2, k[lo:hi], np.ones(hi - lo)]).T
    sig_c2 = SIG_ONE * math.sqrt(float(np.linalg.inv(X.T @ X)[0, 0]))   # least-squares covariance, independent rounding
    e0 = (c2 * k0 + c1) * k0 + c0
    return {'k0_invA': r(k0, 4), 'E0_minus_Gamma_meV': r((e0 - e[0]) * 1000, 2),
            'm_long': r(H2M / (-c2), 3), 'sigma_round': r(abs(H2M / c2) * sig_c2 / abs(c2), 3), 'points': [lo, hi - 1]}


# ------------------------------------------------------------------ densities of states (300 K)
def nc3d(m, alpha=0.0, T=T):
    """Effective conduction-band density of states (cm^-3), Boltzmann, parabolic (alpha = 0) or Kane:
    Nc = int g(E) exp(-E/kT) dE with g = (2m)^{3/2}/(2 pi^2 hbar^3) sqrt(g(E)) (1 + 2 alpha E), g(E) = E (1 + alpha E)."""
    kT = KB_J * T
    n0 = 2.0 * (2 * math.pi * m * M0 * kT / (2 * math.pi * HBAR) ** 2) ** 1.5 * 1e-6
    if alpha == 0:
        return n0
    x = np.linspace(0, 40, 40001)                      # E / kT
    a = alpha * KB * T
    g = np.sqrt(x * (1 + a * x)) * (1 + 2 * a * x) * np.exp(-x)
    g0 = np.sqrt(x) * np.exp(-x)
    return n0 * float(np.trapezoid(g, x) / np.trapezoid(g0, x))


def n2d(m, alpha=0.0, T=T):
    """2-D effective density of states per subband (cm^-2), Boltzmann: m kT/(pi hbar^2) (1 + 2 alpha kT) (Kane)."""
    kT = KB_J * T
    return m * M0 * kT / (math.pi * HBAR ** 2) * 1e-4 * (1 + 2 * alpha * KB * T)


def mass_from_nc(nc, T=T):
    kT = KB_J * T
    return (nc * 1e6 / 2.0) ** (2 / 3) * (2 * math.pi * HBAR) ** 2 / (2 * math.pi * kT) / M0


def boltzmann_nv(E, w, Ev, volume_A3, T=T):
    """Valence-band effective density of states from the eigenvalues of a uniform k-grid (Boltzmann sum):
    Nv = (1/V) sum_k w_k sum_n exp(-(Ev - E_nk)/kT), sum_k w_k = 2 (spin). Returns cm^-3."""
    s = float(np.sum(w[:, None] * np.exp(-np.clip(Ev - E, 0, None) / (KB * T)) * (E <= Ev + 1e-6)))
    return s / (volume_A3 * 1e-24)


# ------------------------------------------------------------------ power laws
def power_law(t, y):
    """y = a t^-p fitted in log space (equal relative weights). Returns a, p, their 1-sigma errors from the residual
    variance (n > 2), relative residuals and the leave-one-out range (n >= 3)."""
    t, y = np.asarray(t, float), np.asarray(y, float)
    if np.any(y <= 0):
        return {'ok': False, 'reason': 'non-positive values: no power law'}
    X = np.vstack([np.ones_like(t), -np.log(t)]).T
    beta, *_ = np.linalg.lstsq(X, np.log(y), rcond=None)
    a, p = math.exp(beta[0]), float(beta[1])
    res = np.log(y) - X @ beta
    out = {'ok': True, 'a': r(a, 5), 'p': r(p, 4), 'n': len(t), 't_nm': [r(x, 4) for x in t], 'y': [r(x, 5) for x in y],
           'rel_resid': [r(math.exp(x) - 1, 4) for x in res]}
    if len(t) > 2:
        s2 = float(res @ res) / (len(t) - 2)
        cov = s2 * np.linalg.inv(X.T @ X)
        out['sigma_ln_a'] = r(math.sqrt(cov[0, 0]), 4)
        out['sigma_a'] = r(a * math.sqrt(cov[0, 0]), 5)
        out['sigma_p'] = r(math.sqrt(cov[1, 1]), 4)
        out['dof'] = len(t) - 2
        loo = []
        for j in range(len(t)):
            m = np.arange(len(t)) != j
            b, *_ = np.linalg.lstsq(X[m], np.log(y[m]), rcond=None)
            loo.append((math.exp(b[0]), float(b[1])))
        out['loo_a'] = [r(min(x[0] for x in loo), 5), r(max(x[0] for x in loo), 5)]
        out['loo_p'] = [r(min(x[1] for x in loo), 4), r(max(x[1] for x in loo), 4)]
    return out


def law(f, t):
    return f['a'] * t ** (-f['p'])
