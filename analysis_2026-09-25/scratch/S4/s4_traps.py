"""S4 defect/trap analysis (2026-09-25). Read-only w.r.t. runs; no ATLAS launched.
Parts:
 A  tail-density thickness law: power law vs surface+bulk decomposition; Januar / Kim numbers
 B  subthreshold trap-DOS spectroscopy (charge-sheet inversion that removes the drain-bias and
    free-carrier terms), VALIDATED on ATLAS runs whose DOS is known, then applied to the data
 C  0-D film forward surrogate: SS metrics vs mobility (trap-free) and with the V1 DOS
 D  off-state floors: level, Vg dependence, thickness exponent, sheet conductance
 E  donor electrostatics: uniform-donor fits of Vth_cc(t), Kim2024 Von(t) -> Nd
 F  bias-stress magnitude scaling (Januar PBS numbers)
"""
import re, os, json
import numpy as np
from scipy.interpolate import PchipInterpolator

ROOT = r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1"
OUT = os.path.join(ROOT, r"analysis_2026-09-25\scratch\S4")
q = 1.602176634e-19; kT = 0.025852; LN10 = np.log(10.0)
Cox = 8.955e-7; CoxQ = Cox / q          # cm^-2 V^-1
L = 20e-4; Vd = 0.7; eps0 = 8.8541878e-14; eps_s = 9.3 * eps0
res = {}

def P(*a):
    print(*a)

# ---------------------------------------------------------------- A
P("=== A. tail-density thickness law ===")
law = lambda t: 2e19 * (2.0 / t) ** 0.75
for t in (2.0, 6.3, 13.2):
    P(f"  V1 law t={t:5.1f} nm  Nt={law(t):.3e} cm^-3  sheet={law(t)*t*1e-7:.3e} cm^-2")
S2, S13 = law(2) * 2e-7, law(13.2) * 13.2e-7
Nb = (S13 - S2) / (11.2e-7); Ns = S2 - Nb * 2e-7
P(f"  surface+bulk through V1 anchors: Ns={Ns:.3e} cm^-2, Nb={Nb:.3e} cm^-3")
pred63 = (Ns + Nb * 6.3e-7) / 6.3e-7
P(f"  -> Nt(6.3) = {pred63:.3e} (law {law(6.3):.3e}; ratio {pred63/law(6.3):.3f})")
P(f"  S2 curve-shape partition Nt(6.3)=2.66e19 (B0) is x{2.66e19/law(6.3):.2f} law, x{2.66e19/pred63:.2f} surf+bulk")
# Januar PBS t=0 values
S2j, S10j = 5.3e19 * 2e-7, 3.39e18 * 10e-7
Nbj = (S10j - S2j) / 8e-7
P(f"  Januar PBS devices: sheet(2nm)={S2j:.3e}, sheet(10nm)={S10j:.3e} -> Nb={Nbj:.3e} (NEGATIVE => no non-negative surf+bulk)")
P(f"  Januar PBS ratio Nt2/Nt10 = {5.3e19/3.39e18:.1f}; implied exponent ln(ratio)/ln(5) = {np.log(5.3e19/3.39e18)/np.log(5):.2f}")
P(f"  Januar Fig5a 'x4 from 13.2 to 2': exponent ln4/ln6.6 = {np.log(4)/np.log(6.6):.3f}; sheet ratio 13.2/2 = {6.6/4:.3f}")
# Kim2024: SS-derived Nt (cm^-2 eV^-1) and CNF border traps (cm^-3 eV^-1)
kimT = np.array([10, 20, 30.]); kimNtSS = np.array([3.32e12, 3.96e12, 7.03e12]); kimNbt = np.array([2.37e18, 3.12e18, 14.6e18])
p = np.polyfit(kimT * 1e-7, kimNtSS, 1)
P(f"  Kim2024 SS-Nt linear fit: Ds={p[1]:.3e} cm^-2eV^-1, gb={p[0]:.3e} cm^-3eV^-1; residual 20nm {kimNtSS[1]-np.polyval(p,20e-7):.2e}")
P(f"  Kim2024 step slopes: 10->20 {(kimNtSS[1]-kimNtSS[0])/1e-6:.2e}, 20->30 {(kimNtSS[2]-kimNtSS[1])/1e-6:.2e} cm^-3eV^-1 (accelerating)")

# ---------------------------------------------------------------- helpers
eta_tab = np.linspace(-60, 30, 9001)
_e = np.linspace(0, 80, 8001)
F12 = np.array([2 / np.sqrt(np.pi) * np.trapezoid(np.sqrt(_e) / (1 + np.exp(np.clip(_e - et, -700, 700))), _e) for et in eta_tab[::10]])
eta_c = eta_tab[::10]
logF = PchipInterpolator(eta_c, np.log(F12))
def nfree(u, Nct):  # sheet free density, FD, u = EF-Ec (eV)
    return Nct * np.exp(logF(np.clip(u / kT, -60, 30)))
def u_of_n(n, Nct):
    et = np.linspace(-60, 30, 20001); lf = logF(et)
    return kT * np.interp(np.log(n / Nct), lf, et)

def model_dos(E, t_nm, NTA, WTA=0.04, NGA1=5e16, EGA1=0.6, WGA1=0.15, NGA2=1.16757e19, EGA2=0.301554, WGA2=0.123975, dit_mult=1.0):
    """sheet DOS (cm^-2 eV^-1) vs E-Ec for the V1 deck: tail in both regions, deep Gaussian in region 1,
    regularized interface Gaussian in region 2 (0.25 nm)."""
    t = t_nm * 1e-7; t2 = 0.25e-7; t1 = t - t2
    g = t * NTA * np.exp(E / WTA) + t1 * NGA1 * np.exp(-((E + EGA1) / WGA1) ** 2) + dit_mult * t2 * NGA2 * np.exp(-((E + EGA2) / WGA2) ** 2)
    return np.where(E <= 0, g, 0.0)

Eg = np.linspace(-3.3, 0.0, 6601)
def thermal_D(u, gE):  # dn_t/dEF = int g f(1-f)/kT
    out = []
    for uu in np.atleast_1d(u):
        x = np.clip((Eg - uu) / kT, -700, 700); f = 1 / (1 + np.exp(x))
        out.append(np.trapezoid(gE * f * (1 - f) / kT, Eg))
    return np.array(out)
def trapped(u, gE):
    out = []
    for uu in np.atleast_1d(u):
        f = 1 / (1 + np.exp(np.clip((Eg - uu) / kT, -700, 700))); out.append(np.trapezoid(gE * f, Eg))
    return np.array(out)

# ---------------------------------------------------------------- data I/O
import csv
meas = {}
with open(os.path.join(ROOT, "data", "experimental_clean.csv")) as fh:
    for r in csv.DictReader(fh):
        meas.setdefault(float(r["thickness_nm"]), []).append((float(r["vg_V"]), float(r["id_A_per_um"])))
for k in meas:
    a = np.array(sorted(meas[k])); meas[k] = (a[:, 0], a[:, 1])

def read_sim(run):
    d = os.path.join(ROOT, "results", "runs", run)
    vg, idd = [], []
    for line in open(os.path.join(d, "idvg.dat")):
        m = re.match(r"^\s*(-?[\d.]+(?:e[-+]?\d+)?)\s+(-?[\d.]+e[-+]?\d+)\s*$", line.strip(), re.I)
        if m: vg.append(float(m.group(1))); idd.append(float(m.group(2)))
    deck = open(os.path.join(d, "device.in")).read()
    g = lambda key: float(re.search(key + r"=([\d.e+-]+)", deck).group(1))
    nta = float(re.findall(r"nta=([\d.e+-]+)", deck)[0]); nga2 = float(re.findall(r"nga=([\d.e+-]+)", deck)[1])
    tmin = float(re.search(r"region num=1 user.material=IWO .*?y.min=([-\d.e]+)", deck).group(1))
    return np.array(vg), np.array(idd), dict(nc=g("nc300"), mun=g("mun"), nta=nta, nga2=nga2, t_nm=-tmin * 1e3)

VG = np.round(np.arange(-3.0, 3.0001, 0.05), 3)
def uniform(vg, idd, floor=1e-20):
    ok = idd > 1e-17
    f = PchipInterpolator(vg[ok], np.log10(idd[ok]))
    y = np.full(VG.shape, np.log10(floor)); m = (VG >= vg[ok].min()) & (VG <= vg[ok].max()); y[m] = f(VG[m])
    return 10 ** y

def locslope(y, x, w=2):
    s = np.full_like(y, np.nan)
    for i in range(len(x)):
        a, b = max(0, i - w), min(len(x), i + w + 1)
        if b - a >= 3: s[i] = np.polyfit(x[a:b], y[a:b], 1)[0]
    return s

def spectroscopy(I, mu, Nct, floor=0.0, w=2):
    """charge-sheet inversion: n_s0(Vg) = (L/q mu) sum_k gm(Vg - k Vd); then
    D_trap(u) = CoxQ (dVg/du - 1) - dn_f/du   (Vfb cancels)"""
    Ich = I - floor
    valid = Ich > max(3 * floor, 1e-16)
    lg = np.log10(np.where(valid, Ich, 1e-30))
    s = locslope(lg, VG, w); s[~valid] = 0.0
    gm = LN10 * np.where(valid, Ich, 0) * s * 1e4          # A/V per cm width
    kstep = int(round(Vd / 0.05))
    ns = np.zeros_like(VG)
    for j in range(len(VG)):
        acc = 0.0; k = j
        while k >= 0:
            acc += gm[k]; k -= kstep
        ns[j] = L / (q * mu) * acc
    ok = valid & (ns > 0)
    u = np.full_like(VG, np.nan); u[ok] = u_of_n(ns[ok], Nct)
    dudV = locslope(np.where(ok, u, np.nan), VG, w)
    dnf_du = np.full_like(VG, np.nan)
    # dn_f/du from FD: numerical
    du = 1e-4
    dnf_du[ok] = (nfree(u[ok] + du, Nct) - nfree(u[ok] - du, Nct)) / (2 * du)
    D = CoxQ * (1 / dudV - 1) - dnf_du
    return dict(ns=ns, u=u, D=D, ok=ok & np.isfinite(D) & (dudV > 0), I=I)

# ---------------------------------------------------------------- B: validation on ATLAS
P("\n=== B. trap-DOS spectroscopy: validation on ATLAS runs (known DOS) ===")
runs = {"run_0012_2p0_v2_full_stepped_final": 2.0, "run_0015_6p3_v2_full_stepped_tuned_qf8p7e10_mu11p69": 6.3,
        "run_0014_6p3_v2_full_stepped_validation_shared_params": 6.3, "run_0013_13p2_v2_full_stepped_final": 13.2,
        "run_0033_6p3_hyp_H4_front_Dit_x5": 6.3, "run_0030_6p3_hyp_H3_backQ_m1p64e12": 6.3}
spec = {}
Uq = np.array([-0.30, -0.25, -0.20, -0.15, -0.10, -0.07, -0.05])
def at_u(sp, uq):
    m = sp["ok"] & (sp["I"] > 1e-13) & np.isfinite(sp["u"])
    uu, DD = sp["u"][m], sp["D"][m]
    o = np.argsort(uu); uu, DD = uu[o], DD[o]
    out = []
    for x in uq:
        out.append(np.interp(x, uu, DD) if (uu.min() <= x <= uu.max()) else np.nan)
    return np.array(out), (uu.min(), uu.max())
for run, t in runs.items():
    vg, idd, pr = read_sim(run)
    I = uniform(vg, idd)
    Nct = pr["nc"] * pr["t_nm"] * 1e-7
    sp = spectroscopy(I, pr["mun"], Nct); spec[run] = (sp, pr)
    gE = model_dos(Eg, pr["t_nm"], pr["nta"], NGA2=pr["nga2"])
    rec, rng = at_u(sp, Uq); tru = thermal_D(Uq, gE)
    P(f"  {run[:34]:34s} t={pr['t_nm']:.1f} mu={pr['mun']:.2f}  u-range {rng[0]:.3f}..{rng[1]:.3f} eV")
    for x, a, b in zip(Uq, rec, tru):
        P(f"     u={x:+.2f}  recovered {a:10.3e}  model(thermal) {b:10.3e}  ratio {a/b if b>0 else np.nan:6.2f}")

# ---------------------------------------------------------------- B: measured
P("\n=== B. measured films ===")
floors = {}
for t in (2.0, 6.3, 13.2):
    vg, idd = meas[t]; m = (vg >= -2.0) & (vg <= -0.5); floors[t] = np.median(idd[m])
mu_sets = {"V1 mun": {2.0: 13.3, 6.3: 10.65, 13.2: 59.24}, "S2 partition": {2.0: 19.3 * 0.734, 6.3: 19.6 * 0.911, 13.2: 62.7 * 0.957}}
Nc = {2.0: 3.27444e18, 6.3: 2.54976e18, 13.2: 2.43961e18}
mspec = {}
for lab, mus in mu_sets.items():
    P(f"  mobility set: {lab} {mus}")
    for t in (2.0, 6.3, 13.2):
        vg, idd = meas[t]; I = np.interp(VG, vg, idd)
        sp = spectroscopy(I, mus[t], Nc[t] * t * 1e-7, floor=floors[t]); mspec[(lab, t)] = sp
        rec, rng = at_u(sp, Uq)
        P(f"   t={t:5.1f}  u-range {rng[0]:.3f}..{rng[1]:.3f}")
        for x, a in zip(Uq, rec):
            gE = model_dos(Eg, t, 2e19 * (2 / t) ** 0.75 / 0.04)
            P(f"     u={x:+.2f}  D_meas {a:10.3e} cm^-2eV^-1  per-volume {a/(t*1e-7):10.3e} cm^-3eV^-1  V1-model(thermal) {thermal_D([x], gE)[0]:10.3e}")
# surface+bulk decomposition at fixed u (V1 mobilities)
P("  surface+bulk decomposition of D_meas(u) using 2 and 13.2 nm, predict 6.3 nm:")
for i, x in enumerate(Uq):
    d2 = at_u(mspec[("V1 mun", 2.0)], [x])[0][0]; d13 = at_u(mspec[("V1 mun", 13.2)], [x])[0][0]; d6 = at_u(mspec[("V1 mun", 6.3)], [x])[0][0]
    if np.isfinite(d2) and np.isfinite(d13):
        gb = (d13 - d2) / 11.2e-7; Ds = d2 - gb * 2e-7
        P(f"     u={x:+.2f}: Ds={Ds:10.3e} gb={gb:10.3e}  pred6.3={Ds+gb*6.3e-7:10.3e}  meas6.3={d6:10.3e}")

# SS metrics of measured curves at their own points, and D at SS_min (naive formula)
P("  naive SS inversion (Cox/q)(SS/59.5-1):")
for t, ssmin, sscc in ((2.0, 84.5, 269.9), (6.3, 114.7, 295.4), (13.2, 130.8, 160.0)):
    s0 = LN10 * kT * 1e3
    P(f"     t={t}: SS_min {ssmin} -> D={CoxQ*(ssmin/s0-1):.3e} ({CoxQ*(ssmin/s0-1)/(t*1e-7):.2e} /cm3eV); SS_cc {sscc} -> D={CoxQ*(sscc/s0-1):.3e}")
for mu in (10.65, 13.3, 59.24):
    Istar = mu * Cox * kT ** 2 / L * 1e-4
    P(f"     free-carrier crossover current (C_free=Cox) for mu={mu}: {Istar:.2e} A/um")

# trapped-charge excess at 6.3 nm: measured vs run_0015 between Vth_cc and Vth_lin
P("  6.3 nm gap: extra trapped charge needed = CoxQ*(1.820-1.471 - (0.644-0.651)) = %.3e cm^-2" % (CoxQ * ((1.820 - 0.644) - (1.471 - 0.651))))

# ---------------------------------------------------------------- C: forward surrogate
P("\n=== C. 0-D film forward surrogate (SS metrics) ===")
def forward(t_nm, mu, Nc_, gE=None):
    uu = np.linspace(-1.6, 0.35, 3901)
    nf = nfree(uu, Nc_ * t_nm * 1e-7)
    nt = trapped(uu, gE) if gE is not None else 0 * uu
    x = uu + (nf + nt) / CoxQ
    xs = np.linspace(x.min() + 0.8, x.max(), 4000)
    nfx = np.interp(xs, x, nf)
    cum = np.concatenate([[0], np.cumsum(0.5 * (nfx[1:] + nfx[:-1]) * np.diff(xs))])
    vg = xs[xs >= xs[0] + Vd]
    I = q * mu / L * (np.interp(vg, xs, cum) - np.interp(vg - Vd, xs, cum)) * 1e-4  # A/um
    lg = np.log10(I)
    v10, v8 = np.interp(-10, lg, vg), np.interp(-8, lg, vg)
    ss = np.gradient(vg, lg) * 1e3
    m = (I > 1e-13) & (I < 1e-8)
    return (v8 - v10) / 2 * 1e3, ss[m].min()
for mu in (10.65, 13.3, 59.24):
    P(f"  trap-free t=2 nm mu={mu}: SS_cc={forward(2.0, mu, 3.27e18)[0]:.1f} SS_min={forward(2.0, mu, 3.27e18)[1]:.1f}")
for t, mu, nta, atl in ((2.0, 13.3, 5e20, (289.1, 73.2)), (6.3, 10.65, 2.11464e20, (288.8, 110.8)), (13.2, 59.24, 1.21426e20, (192.5, 151.3))):
    gE = model_dos(Eg, t, nta)
    sc, sm = forward(t, mu, Nc[t], gE)
    P(f"  V1 DOS t={t}: surrogate SS_cc={sc:.1f} SS_min={sm:.1f}   ATLAS SS_cc={atl[0]} SS_min={atl[1]}")
    sc0, sm0 = forward(t, mu, Nc[t], None)
    P(f"          same mu, NO traps: SS_cc={sc0:.1f} SS_min={sm0:.1f}")

# ---------------------------------------------------------------- D: off-state floors
P("\n=== D. off-state floors ===")
fl = {}
for t in (2.0, 6.3, 13.2, 31.8):
    vg, idd = meas[t]
    for a, b in ((-3.0, -2.0), (-2.0, -0.5), (-3.0, -0.5)):
        m = (vg >= a) & (vg <= b)
        sl = np.polyfit(vg[m], np.log10(np.abs(idd[m])), 1)[0]
        P(f"  t={t:5.1f} Vg[{a},{b}] median {np.median(idd[m]):.3e} min {idd[m].min():.3e} max {idd[m].max():.3e} slope {sl:+.3f} dec/V")
    m = (vg >= -2.0) & (vg <= -0.5); fl[t] = np.median(idd[m])
    G = fl[t] * 1e4 * L / Vd
    P(f"     sheet conductance of a parallel path G = {G:.3e} S/sq ; n*mu*t = {G/q:.3e} cm^-2 cm^2/Vs ; total device current {fl[t]*290:.2e} A")
for (a, b) in ((2.0, 6.3), (6.3, 13.2), (2.0, 13.2)):
    P(f"  floor exponent {a}->{b}: {np.log(fl[b]/fl[a])/np.log(b/a):.2f}  (ratio {fl[b]/fl[a]:.1f})")
P(f"  31.8 nm Id(-3V) = {meas[31.8][1][0]:.3e} A/um -> G = {meas[31.8][1][0]*1e4*L/Vd:.3e} S/sq")
# gate leakage FN bound (HfO2 field), for illustration: J = A E^2 exp(-B/E)
Vox = np.array([1.0, 2.0, 3.0]); EOTphys = (15 + 2 * 19.57 / 9.0) * 1e-7
E_hf = Vox / EOTphys
P(f"  HfO2 field at |Vg|=1,2,3 V: {E_hf/1e6} MV/cm ; Al2O3 field x{19.57/9:.2f}")
for phi in (1.0, 1.5, 2.0):
    for mr in (0.2, 0.4):
        B = 6.83e7 * np.sqrt(mr) * phi ** 1.5; A = 1.54e-6 / (mr * phi)
        J = A * E_hf ** 2 * np.exp(-B / E_hf)
        P(f"   FN phi={phi} m*={mr}: J(1,2,3 V) = {J} A/cm^2")
P("  gate-leakage J needed for the floors if the leaking area were 290x100 um^2 (ASSUMED pad, not measured):")
for t in (2.0, 6.3, 13.2):
    P(f"     t={t}: J = {fl[t]*290/(290e-4*100e-4):.2e} A/cm^2")

# ---------------------------------------------------------------- E: donors
P("\n=== E. donor electrostatics ===")
def dV_donor(Nd, t_nm):  # back-surface threshold shift of a fully depleted film with uniform donors
    t = t_nm * 1e-7
    return q * Nd * t / Cox + q * Nd * t * t / (2 * eps_s)
for t in (2.0, 6.3, 13.2, 31.8):
    P(f"  per 1e18 cm^-3: t={t:5.1f}: -dVth={dV_donor(1e18,t):.3f} V (sheet term {q*1e18*t*1e-7/Cox:.3f})")
need = 0.56 / (dV_donor(1e18, 13.2) - dV_donor(1e18, 6.3)) * 1e18
P(f"  Nd needed for dVth_cc(6.3->13.2) = -0.56 V : {need:.2e} cm^-3 ; it predicts dVth(2->6.3) = {-(dV_donor(need,6.3)-dV_donor(need,2)):.3f} V (meas -0.018)")
for t in (2.0, 6.3, 13.2):
    P(f"  Qf=1.73e12 as volumetric donors in t={t}: Nd={1.73e12/(t*1e-7):.2e} cm^-3")
# Kim2024 Von(t) -> Nd  (90 nm SiO2 per Kim; eps_s 9.3 assumed)
CoxK = 3.9 * eps0 / 90e-7
for (t1, t2, dv) in ((10, 20, 2.0), (20, 30, 2.0)):
    a1, a2 = t1 * 1e-7, t2 * 1e-7
    k = q * ((a2 - a1) / CoxK + (a2 ** 2 - a1 ** 2) / (2 * eps_s))
    P(f"  Kim2024 Von {t1}->{t2} nm shift -{dv} V -> Nd = {dv/k:.2e} cm^-3 (CoxK={CoxK:.2e})")
# 31.8 nm always-on: positive sheet that the gate at -3 V cannot remove (order of magnitude)
P(f"  gate charge swing Cox*3V/q = {CoxQ*3:.2e} cm^-2")

# ---------------------------------------------------------------- F: PBS scaling
P("\n=== F. PBS extrapolation to a sweep ===")
for dv, lab in ((1.2, "2 nm IWO"), (0.72, "10 nm IWO")):
    for beta in (0.3, 0.5, 1.0):
        for ts in (10, 60):
            for gamma in (1, 2):
                P(f"  {lab}: dV(1200s,6V)={dv} beta={beta} t={ts}s gamma={gamma} (3V/6V)^g -> {dv*(ts/1200)**beta*(0.5)**gamma:.3f} V")

# ---------------------------------------------------------------- plot
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(16, 5))
cols = {2.0: "C0", 6.3: "C1", 13.2: "C2"}
for t in (2.0, 6.3, 13.2):
    sp = mspec[("V1 mun", t)]; m = sp["ok"] & (sp["I"] > 1e-13)
    ax[0].semilogy(sp["u"][m], sp["D"][m], "o", ms=3, color=cols[t], label=f"meas {t} nm")
    ax[1].semilogy(sp["u"][m], sp["D"][m] / (t * 1e-7), "o", ms=3, color=cols[t], label=f"meas {t} nm")
    sp2 = mspec[("S2 partition", t)]; m2 = sp2["ok"] & (sp2["I"] > 1e-13)
    ax[0].semilogy(sp2["u"][m2], sp2["D"][m2], "x", ms=3, color=cols[t], alpha=0.5)
for run, (sp, pr) in spec.items():
    if run.startswith(("run_0012", "run_0015", "run_0013")):
        t = pr["t_nm"]; m = sp["ok"] & (sp["I"] > 1e-13)
        ax[0].semilogy(sp["u"][m], sp["D"][m], "-", color=cols[round(t, 1)], lw=1)
        gE = model_dos(Eg, t, pr["nta"]); uu = np.linspace(-0.45, 0.0, 91)
        ax[0].semilogy(uu, thermal_D(uu, gE), ":", color=cols[round(t, 1)], lw=2)
ax[0].set_xlabel("EF - Ec at source (eV)"); ax[0].set_ylabel("D_trap (cm^-2 eV^-1)"); ax[0].set_title("markers: data (o V1 mu, x S2 mu); line: inversion of ATLAS; dotted: model input")
ax[1].set_xlabel("EF - Ec (eV)"); ax[1].set_ylabel("D_trap / t (cm^-3 eV^-1)"); ax[1].legend()
for t in (2.0, 6.3, 13.2, 31.8):
    vg, idd = meas[t]; ax[2].semilogy(vg, idd, label=f"{t} nm")
ax[2].set_xlabel("Vg (V)"); ax[2].set_ylabel("Id (A/um)"); ax[2].legend(); ax[2].set_title("measured transfer (floors)")
for a in ax[:2]: a.set_xlim(-0.45, 0.05); a.set_ylim(1e10, 1e15) if a is ax[0] else a.set_ylim(1e16, 1e21); a.grid(alpha=.3)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "s4_trap_spectroscopy.png"), dpi=130)
P("saved plot")
