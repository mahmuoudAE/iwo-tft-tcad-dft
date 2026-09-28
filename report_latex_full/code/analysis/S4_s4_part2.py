"""S4 part 2: integrated trap-charge excess at 6.3 nm by energy window (measured vs run_0015, same inversion),
channel current at Vg=0 vs floor, and ratio tables measured/ATLAS-inverted per film."""
import io, contextlib, runpy, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path(os.path.join(HERE, "s4_traps.py"))
VG, mspec, spec, meas, fl = g["VG"], g["mspec"], g["spec"], g["meas"], g["floors"]
pairs = {2.0: "run_0012_2p0_v2_full_stepped_final", 6.3: "run_0015_6p3_v2_full_stepped_tuned_qf8p7e10_mu11p69",
         13.2: "run_0013_13p2_v2_full_stepped_final"}
def curve(sp):
    m = sp["ok"] & (sp["I"] > 1e-13) & np.isfinite(sp["u"])
    u, D = sp["u"][m], sp["D"][m]; o = np.argsort(u); return u[o], D[o]
print("ratio D_meas / D_ATLAS-inverted (same inversion, V1 mobilities) vs u")
grid = np.arange(-0.20, 0.051, 0.025)
for t, run in pairs.items():
    um, Dm = curve(mspec[("V1 mun", t)]); us, Ds = curve(spec[run][0])
    row = []
    for x in grid:
        ok = (um.min() <= x <= um.max()) and (us.min() <= x <= us.max())
        row.append(f"{np.interp(x, um, Dm)/np.interp(x, us, Ds):5.2f}" if ok else "  -  ")
    print(f"  t={t:5.1f}: " + " ".join(row) + "   (u = " + ", ".join(f"{x:+.3f}" for x in grid) + ")")
print("\nintegrated excess trapped sheet charge at 6.3 nm, measured minus run_0015 (cm^-2):")
for lab in ("V1 mun", "S2 partition"):
    um, Dm = curve(mspec[(lab, 6.3)]); us, Ds = curve(spec[pairs[6.3]][0])
    lo, hi = max(um.min(), us.min()), min(um.max(), us.max())
    for a, b in ((lo, -0.10), (-0.10, 0.0), (0.0, hi), (lo, hi)):
        x = np.linspace(a, b, 200)
        ex = np.trapezoid(np.interp(x, um, Dm) - np.interp(x, us, Ds), x)
        print(f"  {lab:12s} u in [{a:+.3f},{b:+.3f}] : {ex:+.3e}")
print("  (needed from the Vth_lin-Vth_cc gap: +1.99e12)")
# where does Vth_lin sit in u? measured 6.3 source-end u at Vg = 1.82 V
for t, vl in ((2.0, 1.663), (6.3, 1.820), (13.2, 1.044)):
    sp = mspec[("V1 mun", t)]
    print(f"  t={t}: u(source) at Vth_lin {vl} V = {np.interp(vl, VG, sp['u']):+.3f} eV ; at Vth_cc: see below")
for t, vc in ((2.0, 0.662), (6.3, 0.644), (13.2, 0.083)):
    sp = mspec[("V1 mun", t)]
    print(f"  t={t}: u(source) at Vth_cc {vc} V = {np.interp(vc, VG, sp['u']):+.3f} eV ; n_s0 = {np.interp(vc, VG, sp['ns']):.2e} cm^-2")
print("\nfloor vs channel current at Vg = 0 V (measured):")
for t in (2.0, 6.3, 13.2):
    vg, idd = meas[t]
    i0 = idd[np.argmin(abs(vg))]
    print(f"  t={t}: Id(0 V) = {i0:.2e} A/um, floor {fl[t]:.2e}, floor/Id(0) = {fl[t]/i0:.3f}")
# tail-pinned Fermi level in an isolated (ungated, neutral) film, V1 parameters, Qf ignored
kT = 0.025852
for t, Nd, Nt, mu, Nc in ((2.0, 2.5e17, 2e19, 13.3, 3.27e18), (6.3, 2.52e17, 8.46e18, 10.65, 2.55e18), (13.2, 2.97e17, 4.86e18, 59.24, 2.44e18)):
    fac = (np.pi * kT / 0.04) / np.sin(np.pi * kT / 0.04)
    u0 = 0.04 * np.log(Nd / (Nt * fac))
    n0 = Nc * np.exp(u0 / kT)
    print(f"  isolated film t={t}: EF-Ec = {u0:+.3f} eV, n0 = {n0:.2e} cm^-3, q n0 mu t = {1.602e-19*n0*mu*t*1e-7:.2e} S/sq")
