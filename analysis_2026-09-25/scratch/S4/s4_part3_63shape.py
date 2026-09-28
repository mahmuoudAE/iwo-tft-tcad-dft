"""S4 part 3: which trap redistribution reproduces the 6.3 nm on-state SHAPE?
0-D charge-sheet surrogate (uniform film potential, FD free electrons, thermal trap occupancy, Vd = 0.7 V
Pao-Sah-type integral). Each variant is rigidly aligned to the measured Vth_cc (0.644 V) - equivalent to a
Qf change, which the brief shows is an exact rigid shift - and scored with the extractor's definitions
(Vth_lin from secant gm_max on the 0.05 V grid). The surrogate's absolute error is first measured on the
tuned ATLAS DOS (run_0015) and reported; conclusions use DIFFERENCES between variants."""
import io, contextlib, runpy, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(os.path.join(HERE, "s4_traps.py"))
nfree, trapped, model_dos, Eg, CoxQ, q, L, Vd = (g[k] for k in ("nfree", "trapped", "model_dos", "Eg", "CoxQ", "q", "L", "Vd"))
T = 6.3; NC = 2.54976e18; NTA0 = 2.11464e20
VG = np.round(np.arange(-3.0, 3.0001, 0.05), 3)

def curve(gE, mu):
    uu = np.linspace(-1.6, 0.45, 4101)
    nf = nfree(uu, NC * T * 1e-7); nt = trapped(uu, gE)
    x = uu + (nf + nt) / CoxQ
    xs = np.linspace(x.min(), x.max(), 8000); nfx = np.interp(xs, x, nf)
    cum = np.concatenate([[0], np.cumsum(0.5 * (nfx[1:] + nfx[:-1]) * np.diff(xs))])
    vg = xs[xs >= xs[0] + Vd]
    I = q * mu / L * (np.interp(vg, xs, cum) - np.interp(vg - Vd, xs, cum)) * 1e-4
    shift = 0.644 - np.interp(-9.0, np.log10(I), vg)
    return np.interp(VG, vg + shift, I, left=1e-30, right=np.nan)

def metrics(I):
    gm = np.gradient(I, VG); i = int(np.nanargmax(gm))
    lg = np.log10(I)
    v10, v8 = np.interp(-10, lg, VG), np.interp(-8, lg, VG)
    return dict(gap=VG[i] - I[i] / gm[i] - 0.644, gm=gm[i], ion=I[-1], sscc=(v8 - v10) / 2e-3, vgm=VG[i])

def gauss(E0, sig, Ns):
    return Ns / (sig * np.sqrt(np.pi)) * np.exp(-((Eg - E0) / sig) ** 2)   # sheet DOS, integral = Ns

meas = dict(gap=1.820 - 0.644, gm=3.431e-7, ion=4.034e-7, sscc=295.4)
atl = dict(gap=1.471 - 0.651, gm=2.639e-7, ion=4.03e-7, sscc=288.8)
base = model_dos(Eg, T, NTA0)
mb = metrics(curve(base, 10.6492))
print(f"surrogate on run_0015 DOS, mu 10.65: gap {mb['gap']:.3f} (ATLAS {atl['gap']:.3f}), gm {mb['gm']:.3e} (ATLAS {atl['gm']:.3e}), Ion {mb['ion']:.3e} (ATLAS {atl['ion']:.3e}), SS_cc {mb['sscc']:.0f} (ATLAS {atl['sscc']})")
print(f"measured 6.3 nm: gap {meas['gap']:.3f}, gm {meas['gm']:.3e}, Ion {meas['ion']:.3e}, SS_cc {meas['sscc']}")
print("targets for surrogate variants (surrogate baseline x measured/ATLAS ratios): "
      f"gap {mb['gap'] + (meas['gap']-atl['gap']):.3f}, gm {mb['gm']*meas['gm']/atl['gm']:.3e}, Ion {mb['ion']*meas['ion']/atl['ion']:.3e}")
tg = dict(gap=mb['gap'] + (meas['gap'] - atl['gap']), gm=mb['gm'] * meas['gm'] / atl['gm'], ion=mb['ion'] * meas['ion'] / atl['ion'])
rows = []
def score(lab, gE, mu):
    m = metrics(curve(gE, mu))
    err = np.sqrt(((m['gap'] - tg['gap']) / 0.05) ** 2 + (np.log(m['gm'] / tg['gm']) / 0.05) ** 2 + (np.log(m['ion'] / tg['ion']) / 0.05) ** 2)
    rows.append((err, lab, m))
# (i) tail scaling (S2-type) with mobility
for f in (1.0, 2.0, 3.14, 4.0):
    for mu in (10.65, 12.4, 14.0, 16.0, 17.86, 20.0):
        score(f"tail NTA x{f:.2f}, mu {mu}", model_dos(Eg, T, NTA0 * f), mu)
# (ii) broader tail at fixed integral Nt (WTA 0.05/0.06)
for w in (0.05, 0.06):
    for f in (1.0, 2.0):
        for mu in (10.65, 12.4, 14.0, 17.86):
            score(f"tail WTA {w} Nt x{f}, mu {mu}", model_dos(Eg, T, NTA0 * 0.04 / w * f, WTA=w), mu)
# (iii) Gaussian acceptor band (bulk or interface - identical in a 0-D film)
for E0 in (-0.15, -0.10, -0.07, -0.05, -0.03):
    for sig in (0.02, 0.04):
        for Ns in (1e12, 2e12, 3e12):
            for mu in (10.65, 12.4, 14.0):
                score(f"band E0 {E0} sig {sig} Ns {Ns:.0e}, mu {mu}", base + gauss(E0, sig, Ns), mu)
# (iv) interface Dit x5 at Ec-0.3 (A4-like)
for mu in (10.65, 12.4):
    score(f"Dit x5 (Ec-0.3), mu {mu}", model_dos(Eg, T, NTA0, dit_mult=5.0), mu)
rows.sort(key=lambda r: r[0])
print("\nbest 15 variants (score: gap/0.05 V, ln gm/0.05, ln Ion/0.05 in quadrature):")
for err, lab, m in rows[:15]:
    print(f"  {err:7.2f}  {lab:45s} gap {m['gap']:.3f} gm {m['gm']:.3e} Ion {m['ion']:.3e} SScc {m['sscc']:.0f} Vg(gm_max) {m['vgm']:.2f}")
print("\nselected reference variants:")
for err, lab, m in rows:
    if lab.startswith(("tail NTA x1.00, mu 10.65", "tail NTA x3.14, mu 17.86", "Dit x5 (Ec-0.3), mu 12.4", "tail NTA x1.00, mu 12.4")):
        print(f"  {err:7.2f}  {lab:45s} gap {m['gap']:.3f} gm {m['gm']:.3e} Ion {m['ion']:.3e} SScc {m['sscc']:.0f}")
