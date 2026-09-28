# S2 part 3: shape-consistent trap/mobility partition with the 1-D surrogate (benchmarked against ATLAS in part 2).
# For each film: scan the tail-integral factor f (Nt = f x V1 law); the gap Vth_lin - Vth_cc is independent of Qf
# (rigid shift) and of mu (exact scale) -> pick f* that reproduces the MEASURED gap; then mu_band from gm_max,
# Qf from Vth_cc.  Ion and SS_min are NOT fitted and serve as internal consistency checks.
import numpy as np, pathlib, importlib.util, sys
spec = importlib.util.spec_from_file_location('p2', pathlib.Path(__file__).with_name('s2_part2_mtr_temperature.py'))
src = open(pathlib.Path(__file__).with_name('s2_part2_mtr_temperature.py')).read().split("vg = np.round(np.arange(-3, 3.0001, 0.05), 4)")[0]
src = src.replace("OUT = open(pathlib.Path(__file__).with_name('s2_part2_out.txt'), 'w')", "OUT = None")
ns = {'__file__': __file__}; exec(src, ns)
Film, idvg = ns['Film'], ns['idvg']
OUT = open(pathlib.Path(__file__).with_name('s2_part3_out.txt'), 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); OUT.write(s + '\n'); OUT.flush()
COX = 8.955369814335959e-07; L = 20e-4; VD = 0.7
vg = np.round(np.arange(-3, 3.0001, 0.05), 4)
def feats(vg, idv):
    gm = np.gradient(idv, vg); i = int(np.argmax(gm)); g = gm[i]; vlin = vg[i] - idv[i]/g
    lg = np.log10(np.maximum(idv, 1e-40)); j = np.where(lg >= -9)[0][0]
    vcc = vg[j-1] + (-9 - lg[j-1])*(vg[j]-vg[j-1])/(lg[j]-lg[j-1])
    s = np.gradient(lg, vg); m = (idv > 1e-13) & (idv < 1e-8) & (s > 0)
    ss = 1000/np.max(s[m]) if m.any() else np.nan
    return dict(Vcc=vcc, Vlin=vlin, gap=vlin - vcc, gm=g, mu=g*L/(1e-4*COX*VD), Ion=idv[-1], SS=ss)
meas = {2.0: dict(Vcc=0.662, Vlin=1.663, gap=1.001, gm=3.807e-7, Ion=5.09e-7, SS=84.5, mu=12.15),
        6.3: dict(Vcc=0.644, Vlin=1.820, gap=1.176, gm=3.431e-7, Ion=4.03e-7, SS=114.7, mu=10.95),
        13.2: dict(Vcc=0.083, Vlin=1.044, gap=0.962, gm=1.572e-6, Ion=3.07e-6, SS=130.8, mu=50.17)}
base = {2.0: (5e20, 3.27444e18, 2.5e17, 3.9467, 18.13), 6.3: (2.11464e20, 2.54976e18, 2.525e17, 4.2276, 11.69),
        13.2: (1.21426e20, 2.43961e18, 2.974e17, 4.2739, 61.9)}
scan = {2.0: [1.0, 1.25, 1.5, 2.0], 6.3: [1.0, 2.0, 2.5, 3.0, 4.0], 13.2: [0.8, 1.0, 1.25]}
QF0 = 1.73e12
P('Shape-consistent partition (1-D surrogate; WTA 0.040 eV fixed; Nd, chi, Nc from V1 laws; Qf reference 1.73e12)')
summary = {}
for t, facs in scan.items():
    nta, nc, nd, chi, mb = base[t]; R_t = (1 - 0.287/t)**2
    rows = []
    for f in facs:
        F = Film(t, nta*f, 0.04, nc, nd, chi, Qf=QF0); R = F.sweep(); I = idvg(R, mb*R_t, vg); ft = feats(vg, I)
        rows.append((f, ft)); P(f'  t={t} f={f}: gap={ft["gap"]:.3f} Vcc={ft["Vcc"]:.3f} mu_FE={ft["mu"]:.2f} SS_min={ft["SS"]:.1f}')
    gaps = np.array([r[1]['gap'] for r in rows]); fs = np.array(facs)
    if meas[t]['gap'] < gaps.min() or meas[t]['gap'] > gaps.max():
        P(f'  t={t}: measured gap {meas[t]["gap"]} outside scanned range {gaps.min():.3f}-{gaps.max():.3f}; extrapolating log-linearly')
    fstar = float(np.exp(np.polyval(np.polyfit(gaps, np.log(fs), 1), meas[t]['gap'])))
    F = Film(t, nta*fstar, 0.04, nc, nd, chi, Qf=QF0); R = F.sweep(); I = idvg(R, mb*R_t, vg); ft = feats(vg, I)
    k = meas[t]['gm']/ft['gm']; I2 = I*k; f2 = feats(vg, I2)
    dV = meas[t]['Vcc'] - f2['Vcc']; Qf = QF0 - dV/0.179e-12
    I3 = np.interp(vg - dV, vg, I2); f3 = feats(vg, I3)
    summary[t] = (fstar, mb*k, Qf, f3)
    P(f'  ==> t={t}: f*={fstar:.2f} (Nt={fstar*nta*0.04:.2e} cm-3, sheet {fstar*nta*0.04*t*1e-7:.2e} cm-2), mu_band={mb*k:.2f} (V1 fit {mb}), Qf={Qf:.2e}')
    P(f'      check: Vcc {f3["Vcc"]:.3f}/{meas[t]["Vcc"]}  Vlin {f3["Vlin"]:.3f}/{meas[t]["Vlin"]}  mu_FE {f3["mu"]:.2f}/{meas[t]["mu"]}  Ion {f3["Ion"]:.3e}/{meas[t]["Ion"]:.2e} ({100*(f3["Ion"]/meas[t]["Ion"]-1):+.1f} %, not fitted)  SS_min {f3["SS"]:.1f}/{meas[t]["SS"]} (not fitted)')
P('\nSummary: t | Nt factor | Nt (cm-3) | mu_band | Qf')
for t, (fs_, mb_, qf_, f3) in summary.items():
    P(f'  {t} | {fs_:.2f} | {fs_*base[t][0]*0.04:.2e} | {mb_:.2f} | {qf_:.2e}')
OUT.close()
