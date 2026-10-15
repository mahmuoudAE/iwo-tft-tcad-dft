"""Tests of mc_measured_extraction.py (register A57; synthetic curves only: the measured file is never read here (its pin is checked as a
file hash only), no run directory, no Monte Carlo result on real data).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; python -I -B analysis_2026-10-10_campaign/test_mc_measured_extraction.py
"""
import sys
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
import mc_measured_extraction as X  # noqa: E402

results = []
VG = np.round(np.arange(-3.0, 3.0 + 1e-9, 0.05), 10)


def expect(name, got, want):
    ok = got == want; results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}", flush=True)


def refused(f, *a, **k):
    try: f(*a, **k); return None
    except SystemExit as e: return str(e)


def synth(noise=0.02, seed=1):
    u = 0.1 * np.logaddexp(0.0, (VG - 0.4) / 0.1)
    i = 1e-13 + 3e-8 * u ** 1.3 + 1e-9 * 10 ** np.minimum((VG - 0.2) / 0.18, 0.0) * (VG < 0.2)
    return i * 10 ** (np.random.default_rng(seed).normal(0, noise, len(VG)))


def main():
    expect('pins: real pinned files match', X.check_pins() is None, True)
    expect('pins: changed file -> refused', refused(X.check_pins, {'data/experimental_clean.csv': '0' * 64}) is not None, True)
    expect('smooth: non-positive current -> refused', refused(X.smooth, VG, np.where(VG > 0, 1e-9, -1e-15)) is not None, True)
    i = synth(); y, s = X.smooth(VG, i)
    st = X.strata(VG, s, 1e-13)
    expect('strata: partition of every point', sorted(np.concatenate(list(st.values())).tolist()), list(range(len(VG))))
    expect('strata: on = V_G >= 1 V', bool(np.all(VG[st['on']] >= 1.0 - 1e-9)), True)
    rng = np.random.default_rng(4); r = np.arange(30, dtype=float)
    br = X.block_resample(r, rng)
    expect('block_resample: length kept, values from the stratum only', (len(br), set(br) <= set(r)), (30, True))
    expect('block_resample: blocks of consecutive residuals', bool(np.all(np.diff(br[:5]) % 30 == 1)), True)
    expect('block_resample: short stratum -> i.i.d. from the stratum', set(X.block_resample(np.arange(6.0), rng)) <= set(range(6)), True)
    a1 = X.replicate(VG, i, 1e-13, np.random.default_rng(9)); a2 = X.replicate(VG, i, 1e-13, np.random.default_rng(9))
    expect('replicate: deterministic for a fixed seed', bool(np.array_equal(a1, a2)), True)
    yc = -12 + 0.9 * VG + 0.25 * VG ** 2 - 0.02 * VG ** 3                      # cubic in V: SG(7, 3) reproduces it, residuals 0
    ic = 10 ** yc
    expect('replicate: zero residuals and no instrument terms -> curve unchanged',
           bool(np.allclose(X.replicate(VG, ic, 1e-13, np.random.default_rng(2), gain_sigma=0, offset_frac=0), ic, rtol=1e-10, atol=0)), True)
    g = X.replicate(VG, ic, 1e-13, np.random.default_rng(2), gain_sigma=0.01, offset_frac=0)
    expect('replicate: gain term is one factor per curve', bool(np.ptp(g / ic) < 1e-9 and abs(g[0] / ic[0] - 1) > 0), True)
    q, sig = X.registered(VG, i, (2e-11, 2e-10))
    expect('mirror: replicate extraction reproduces the registered analysis', X.mirror_check(q, X.extract(VG, i, (2e-11, 2e-10))), None)
    expect('mirror: a deviating value -> refused', refused(X.mirror_check, q, dict(X.extract(VG, i, (2e-11, 2e-10)), vth_cc_V=0.0)) is not None, True)
    expect('extract without the power-law fit: PL quantities absent', sorted(set(X.QUANTITIES) - set(X.extract(VG, i, (2e-11, 2e-10), with_pl=False))), sorted(X.PL_QUANTITIES))
    expect('extract: every registered quantity present', sorted(q), sorted(X.QUANTITIES))
    expect('extract: V_th,cc and SS finite on the synthetic curve', (q['vth_cc_V'] is not None, q['ss_fixed_mV_dec'] is not None), (True, True))
    expect('extract: off floor = registered median over -2..-0.5 V', abs(q['off_floor_A_per_um'] - float(np.median(i[(VG >= -2) & (VG <= -0.5)]))) < 1e-25, True)
    res = X.film_mc(VG, i, 1e-13, (2e-11, 2e-10), n=20, seed=5, n_pl=3)
    v = res['quantities']['vth_cc_V']
    expect('film_mc: interval brackets the median', v['ci95'][0] <= v['median'] <= v['ci95'][1], True)
    expect('film_mc: fixed A1 window recorded unchanged', res['fixed_a1_window_A_per_um'], [2e-11, 2e-10])
    expect('film_mc: replicate counts (N for crossings, N_PL for the power law)', (v['n_replicates'], res['quantities']['pl_mu0']['n_replicates']), (20, 3))
    expect('film_mc: deterministic for a fixed seed', X.film_mc(VG, i, 1e-13, (2e-11, 2e-10), n=5, seed=5, n_pl=1)['quantities']['vth_cc_V']['median'] ==
           X.film_mc(VG, i, 1e-13, (2e-11, 2e-10), n=5, seed=5, n_pl=1)['quantities']['vth_cc_V']['median'], True)
    z = X.film_mc(VG, ic, 1e-13, (2e-11, 2e-10), n=5, seed=1, n_pl=1, gain_sigma=0, offset_frac=0)['quantities']['vth_cc_V']
    expect('film_mc: noiseless curve -> zero-width interval at the registered value', (abs(z['ci95'][1] - z['ci95'][0]) < 1e-9, abs(z['median'] - z['registered_value']) < 1e-9), (True, True))
    expect('label: not a blind test; SMU spec not supplied', ('not a blind test' in X.LABEL, 'SMU' in X.LABEL), (True, True))
    expect('constants: N, seed, SG, block, gain, offset', (X.N, X.N_PL, X.SEED, X.SG_WINDOW, X.SG_ORDER, X.BLOCK, X.GAIN_SIGMA, X.OFFSET_FRAC), (2000, 400, 20261016, 7, 3, 5, 1e-3, 0.1))
    expect('CLI: no arguments -> 2 (no run)', X.main([]), 2)
    print(f'{sum(results)}/{len(results)} passed'); return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
