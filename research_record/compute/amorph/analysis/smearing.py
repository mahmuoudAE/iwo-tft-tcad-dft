"""Occupation functions of Quantum ESPRESSO (Modules/wgauss.f90), recomputed as register section 1 (A16) requires:
"f_nk is computed with the final SCF's own smearing function (Gaussian formulas for a Gaussian run, never the MV
formulas)".

f_nk = wgauss((E_F - e_nk) / degauss, ngauss), with
  ngauss =   0  Gaussian                 0.5 erfc(-x)
  ngauss >=  1  Methfessel-Paxton order n (QE: 'mp' is n = 1)
  ngauss =  -1  Marzari-Vanderbilt (cold)  0.5 erf(x - 1/sqrt2) + exp(-(x - 1/sqrt2)^2)/sqrt(2 pi) + 0.5
  ngauss = -99  Fermi-Dirac              1 / (1 + exp(-x))
QE clips exponent arguments at maxarg = 200; the same is done here.
"""
import math

import numpy as np

MAXARG = 200.0

# smearing names as QE writes them (XML: gaussian / mp / mv / fd; pw.x output and input aliases)
_ALIASES = {
    'gaussian': 0, 'gauss': 0,
    'mp': 1, 'm-p': 1, 'methfessel-paxton': 1,
    'mv': -1, 'm-v': -1, 'marzari-vanderbilt': -1, 'cold': -1,
    'fd': -99, 'f-d': -99, 'fermi-dirac': -99,
}
NAMES = {0: 'gaussian', 1: 'mp', -1: 'mv', -99: 'fd'}


def ngauss_of(name):
    """QE ngauss for a smearing name (case-insensitive); ValueError for anything else (e.g. 'fixed')."""
    key = (name or '').strip().lower()
    if key not in _ALIASES:
        raise ValueError(f'unknown smearing {name!r}')
    return _ALIASES[key]


_erf = np.vectorize(math.erf, otypes=[float])
_erfc = np.vectorize(math.erfc, otypes=[float])


def wgauss(x, ngauss):
    """QE wgauss(x, n), vectorised. x = (E_F - e) / degauss."""
    x = np.asarray(x, dtype=float)
    if ngauss == -99:
        out = np.empty_like(x)
        lo, hi = x < -MAXARG, x > MAXARG
        mid = ~(lo | hi)
        out[lo], out[hi] = 0.0, 1.0
        out[mid] = 1.0 / (1.0 + np.exp(-x[mid]))
        return out
    if ngauss == -1:
        xp = x - 1.0 / math.sqrt(2.0)
        arg = np.minimum(MAXARG, xp * xp)
        return 0.5 * _erf(xp) + 1.0 / math.sqrt(2.0 * math.pi) * np.exp(-arg) + 0.5
    if ngauss < 0:
        raise ValueError(f'unsupported ngauss {ngauss}')
    # Gaussian, then the Methfessel-Paxton Hermite corrections (QE loop, verbatim)
    w = 0.5 * _erfc(-x)
    if ngauss == 0:
        return w
    hd = np.zeros_like(x)
    arg = np.minimum(MAXARG, x * x)
    hp = np.exp(-arg)
    ni = 0
    a = 1.0 / math.sqrt(math.pi)
    for i in range(1, ngauss + 1):
        hd = 2.0 * x * hp - 2.0 * ni * hd
        ni += 1
        a = -a / (i * 4.0)
        w = w - a * hd
        hp = 2.0 * x * hd - 2.0 * ni * hp
        ni += 1
    return w


def occupations(e_ev, ef_ev, degauss_ev, smearing):
    """f_nk in [0, 1] (per spin channel) for eigenvalues e_ev with the run's own smearing function."""
    if degauss_ev <= 0:
        raise ValueError('degauss must be > 0 for a smearing run')
    return wgauss((np.asarray(ef_ev, dtype=float) - np.asarray(e_ev, dtype=float)) / degauss_ev, ngauss_of(smearing))
