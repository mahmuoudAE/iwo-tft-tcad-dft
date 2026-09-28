"""S3 task 3: is confinement required by the transfer data?  Uses only existing real ATLAS outputs
(results/runs/<run>/idvg.dat, native A/um) and the measured workbook curves (data/experimental_clean.csv).
1. rigid-shift test: horizontal Vg distance between the confinement-on and confinement-off curves vs current level
   (0012 vs 0016 at 2 nm; 0013 vs 0017 at 13.2 nm). A pure chi shift + Nc(m*) change predicts a constant
   dEc - kT ln(Nc_on/Nc_off).
2. local SS vs log10(Id) for both curves (5-point window, the extractor's definition) -> is the SS_min change a
   property of the curve or of where the minimum falls on the stepped grid?
3. resampling test: shift the confinement-on curve rigidly onto the confinement-off grid and re-extract SS_min.
4. DOS discretisation: level spacing Eg/numa for both runs (numa = 96).
5. 'needed extra Vth' table: measured Vth_cc minus the no-confinement model with the shared Qf.
"""
import sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from extract_metrics import metrics, load_curve  # noqa: E402
RUNS = ROOT / 'results' / 'runs'
KT = 0.025852


def load_run(prefix):
    d = next(p for p in RUNS.iterdir() if p.name.startswith(prefix))
    rows = [l.split() for l in (d / 'idvg.dat').read_text().splitlines()[4:] if l.strip()]
    a = np.array([[float(x) for x in r[:2]] for r in rows])
    # keep the drain-at-0.7 V gate sweep only: the file holds the scored transfer points (as used by the extractor)
    return a[:, 0], a[:, 1], d.name


def logI_interp(vg, idv):
    ok = idv > 0
    return vg[ok], np.log10(idv[ok])


def vg_at_level(vg, idv, lev):
    v, l = logI_interp(vg, idv)
    # first upward crossing on a monotonic segment
    for i in range(len(v) - 1):
        if (l[i] - lev) * (l[i + 1] - lev) <= 0 and l[i + 1] > l[i]:
            return v[i] + (v[i + 1] - v[i]) * (lev - l[i]) / (l[i + 1] - l[i])
    return np.nan


def local_ss(vg, idv):
    out = []
    for i in range(2, len(vg) - 2):
        seg = idv[i - 2:i + 3]
        if np.all(seg > 0):
            d = np.log10(seg[-1]) - np.log10(seg[0])
            if d > 0:
                out.append((np.log10(idv[i]), vg[i], (vg[i + 2] - vg[i - 2]) / d * 1000))
    return np.array(out)


def main():
    pairs = [('run_0012', 'run_0016', 2.0, 0.9205 * 2 ** -1.3815, 3.27444e18, 2.38049e18),
             ('run_0013', 'run_0017', 13.2, 0.9205 * 13.2 ** -1.3815, None, None)]
    for on, off, t, dec, nc_on, nc_off in pairs:
        v1, i1, n1 = load_run(on); v0, i0, n0 = load_run(off)
        if nc_on is None:
            m_on = 0.208 + 0.1311 * t ** -1.412; nc_on, nc_off = m_on ** 1.5, 0.208 ** 1.5
        expect = dec - KT * np.log(nc_on / nc_off)
        print(f"\n=== {n1} (confinement ON) vs {n0} (OFF), t = {t} nm; dEc = {dec:.4f} eV; rigid expectation {expect:.4f} V ===")
        print(" log10 Id   Vg_on    Vg_off   shift (V)")
        for lev in np.arange(-14, -5.99, 0.5):
            a, b = vg_at_level(v1, i1, lev), vg_at_level(v0, i0, lev)
            print(f"  {lev:6.1f}  {a:7.3f}  {b:7.3f}  {a-b:7.3f}")
        m1 = metrics(v1, i1, is_sim=True, t_nm=t); m0 = metrics(v0, i0, is_sim=True, t_nm=t)
        print(f" extractor: SS_min on {m1['SS_mV_dec']:.1f}  off {m0['SS_mV_dec']:.1f} ; SS_cc on {m1['SS_cc_1e-10_1e-8_mV_dec']:.1f} off {m0['SS_cc_1e-10_1e-8_mV_dec']:.1f}")
        s1, s0 = local_ss(v1, i1), local_ss(v0, i0)
        print(" local SS (5-pt) vs log10 Id near the minimum [on | off]:")
        for arr, lab in ((s1, 'on'), (s0, 'off')):
            sel = arr[(arr[:, 0] > -13.5) & (arr[:, 0] < -7)]
            print(f"  {lab}: " + "; ".join(f"{x[0]:.2f}:{x[2]:.0f}" for x in sel))
        # resampling test: ON curve shifted rigidly by the measured Vth_cc shift, evaluated on the OFF grid
        sh = m1['Vth_cc_1e-9_V'] - m0['Vth_cc_1e-9_V']
        va, la = logI_interp(v1, i1)
        for shift in (sh, expect):
            lg = np.interp(v0 + shift, va, la, left=np.nan, right=np.nan)
            ii = np.isfinite(lg)
            mm = metrics(v0[ii], 10 ** lg[ii], is_sim=True, t_nm=t)
            print(f" ON curve shifted by {shift:.3f} V and resampled on the OFF grid: SS_min {mm['SS_mV_dec']:.1f}, SS_cc {mm['SS_cc_1e-10_1e-8_mV_dec']:.1f}")
        eg_on, eg_off = 3.05 + dec, 3.05
        print(f" DOS discretisation (numa=96 over Eg): spacing ON {eg_on/96*1000:.1f} meV, OFF {eg_off/96*1000:.1f} meV (WTA 40 meV, kT 25.9 meV)")

    print("\n=== needed extra Vth_cc beyond the no-confinement model with the shared Qf 1.73e12 ===")
    q_cox = 1.602177e-19 / 8.955369814335959e-07
    meas = {2.0: 0.6618, 6.3: 0.6440, 13.2: 0.0830}
    noqc = {2.0: 0.3608, 13.2: 0.0300}
    # 6.3 nm no-QC at Qf 1.73e12 = A6 (run_0034, Qf 4.76e10) rigidly shifted by -q dQf/Cox (exact rigid Qf shift, brief)
    v34 = 0.5866667963552531
    noqc[6.3] = v34 - q_cox * (1.73e12 - 4.76e10)
    withqc = {2.0: 0.676, 6.3: 0.350, 13.2: 0.053}
    for t in (2.0, 6.3, 13.2):
        need = meas[t] - noqc[t]; qc = withqc[t] - noqc[t]
        print(f" t={t:5.1f}: meas {meas[t]:.3f}  noQC {noqc[t]:.3f}  needed {need:+.3f} V (= {need/q_cox:.2e} cm^-2 of negative charge)"
              f"  ATLAS-QC gives {qc:+.3f}  residual after QC {need-qc:+.3f}")
    print(" one-offset stories: (A) QC + Qf 1.73e12: residuals above; (B) no QC + Qf 4.76e10 (fit on 2 nm):")
    qf_b = 4.76e10
    for t in (2.0, 6.3, 13.2):
        pred = noqc[t] + q_cox * (1.73e12 - qf_b)
        print(f"   t={t:5.1f}: predicted Vth_cc {pred:.3f} vs meas {meas[t]:.3f} -> miss {pred-meas[t]:+.3f} V")


if __name__ == '__main__':
    main()
