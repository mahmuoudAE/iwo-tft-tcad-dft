# S2 part 2: semi-analytic 1-D Poisson (floating thin film, Fermi-Dirac free electrons, V1 exponential acceptor tail,
# Nd_eff, Qf, TiN WF 4.70, chi(t)) + gradual-channel Id at Vd = 0.7 V.  Purpose: (i) benchmark against ATLAS
# runs 0012/0015/0013 (same parameters), (ii) trap-limited (MTR) temperature expectation at 350 K with a
# T-independent band mobility, (iii) percolation / phonon analytic factors, (iv) Coulomb and roughness magnitudes.
import numpy as np, pathlib
from scipy.integrate import solve_ivp, quad
OUT = open(pathlib.Path(__file__).with_name('s2_part2_out.txt'), 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); OUT.write(s + '\n')
q = 1.602176634e-19; kB = 8.617333e-5; e0 = 8.8541878e-12; hbar = 1.054571817e-34; m0 = 9.1093837e-31
COX = 8.955369814335959e-07 * 1e4   # F/m^2
EPS = 9.3*e0; L = 20e-4; VD = 0.7

def F12(eta):  # normalised Fermi-Dirac integral of order 1/2 (Aymerich-Humet approximation)
    v = eta**4 + 50 + 33.6*eta*(1 - 0.68*np.exp(-0.17*(eta + 1)**2))
    return 1/(np.exp(-eta) + 3*np.sqrt(np.pi)/4*v**(-3/8))

class Film:
    def __init__(s, t_nm, NTA, WTA, Nc300, Nd, chi, T=300.0, Qf=1.73e12, WF=4.70):
        s.t = t_nm*1e-9; s.NTA = NTA*1e6; s.WTA = WTA; s.T = T; s.kT = kB*T
        s.Nc = Nc300*1e6*(T/300)**1.5; s.Nd = Nd*1e6; s.chi = chi; s.Qf = Qf*1e4; s.WF = WF
        ug = np.linspace(-0.6, 3.0, 1441)       # u = Ec - EF (eV)
        xg = np.linspace(0, 40*WTA, 8001)        # depth below Ec (eV)
        occ = 1/(1 + np.exp(np.clip((ug[:, None] - xg[None, :])/s.kT, -700, 700)))
        nt = np.trapezoid(np.exp(-xg/WTA)[None, :]*occ, xg, axis=1)
        s.ug = ug; s.ntab = s.NTA*np.array(nt)
    def n(s, u): return s.Nc*F12(-u/s.kT)
    def nt(s, u): return np.interp(u, s.ug, s.ntab)
    def solve(s, ubs, nstep=3000):
        # vectorised RK4 from the back surface (x=t, du/dx=0, u=ub) to the gate interface (x=0)
        # d2u/dx2 [V/m2] = q (Nd - n - nt)/EPS ; state y = (u, du, ns_free, ns_trap)
        ub = np.asarray(ubs, float); h = -s.t/nstep
        def f(y):
            u = y[0]; n = s.n(u); nt = s.nt(u)
            return np.array([y[1], q*(s.Nd - n - nt)/EPS, -n, -nt])
        y = np.array([ub, np.zeros_like(ub), np.zeros_like(ub), np.zeros_like(ub)])
        for _ in range(nstep):
            k1 = f(y); k2 = f(y + 0.5*h*k1); k3 = f(y + 0.5*h*k2); k4 = f(y + h*k3)
            y = y + h/6*(k1 + 2*k2 + 2*k3 + k4)
        u0, du0, nsf, nst = y
        Vox = (EPS*du0 - q*s.Qf)/COX
        Vg = Vox + (s.WF - s.chi) - u0
        return np.array([Vg, nsf, nst, u0]).T
    def sweep(s):
        ubs = np.concatenate([np.linspace(-0.25, 0.4, 131), np.linspace(0.4, 2.6, 111)[1:]])
        R = s.solve(ubs)
        for _ in range(40):   # adaptive refinement: no Vg gap > 0.02 V inside [-3.6, 3.6] V
            o = np.argsort(ubs); ubs = ubs[o]; R = R[o]
            va, vb = R[:-1, 0], R[1:, 0]
            m = (np.abs(va - vb) > 0.02) & (np.minimum(va, vb) < 3.6) & (np.maximum(va, vb) > -3.6) & (np.diff(ubs) > 1e-12)
            if not m.any(): break
            new = 0.5*(ubs[:-1][m] + ubs[1:][m])
            ubs = np.concatenate([ubs, new]); R = np.vstack([R, s.solve(new)])
        R = R[np.isfinite(R).all(axis=1)]
        o = np.argsort(R[:, 0]); R = R[o]
        keep = np.concatenate([[True], np.diff(R[:, 0]) > 1e-6]); R = R[keep]
        return R  # columns Vg, ns_free (m^-2), ns_trap, u_surface

def idvg(R, mu_cm2, vg):
    # floating thin film: n_free(Vg, V) = n_free(Vg - V, 0) -> Id/W = q mu/L * integral_{Vg-Vd}^{Vg} n_free(v) dv
    vv = np.linspace(-6, 4, 5001); nf = np.exp(np.interp(vv, R[:, 0], np.log(np.maximum(R[:, 1], 1e-30)), left=-80))*1e-4  # cm^-2
    cum = np.concatenate([[0], np.cumsum(0.5*(nf[1:] + nf[:-1])*np.diff(vv))])
    I = q*mu_cm2/L*(np.interp(vg, vv, cum) - np.interp(vg - VD, vv, cum))  # A/cm width
    return I*1e-4  # A/um
def feats(vg, idv):
    gm = np.gradient(idv, vg); i = int(np.argmax(gm)); g = gm[i]; vlin = vg[i] - idv[i]/g
    lg = np.log10(np.maximum(idv, 1e-40)); j = np.where(lg >= -9)[0][0]
    vcc = vg[j-1] + (-9 - lg[j-1])*(vg[j]-vg[j-1])/(lg[j]-lg[j-1])
    return dict(Vcc=vcc, Vlin=vlin, gm=g, mu=g*L/(1e-4*COX*1e-4*VD), Ion=idv[-1])

vg = np.round(np.arange(-3, 3.0001, 0.05), 4)
cases = {  # t, NTA (cm-3/eV), Nc300, Nd_eff, chi, mun (cm2/Vs, = mu_band*R), Qf, ATLAS reference run
    '2.0 (run_0012)': (2.0, 5e20, 3.27444e18, 2.5e17, 3.9467, 13.30, 1.73e12, dict(Vcc=0.676, Vlin=1.559, mu=11.27, Ion=5.09e-7)),
    '6.3 (run_0015)': (6.3, 2.11464e20, 2.54976e18, 2.525e17, 4.2276, 10.6492, 8.7e10, dict(Vcc=0.651, Vlin=1.471, mu=8.42, Ion=4.03e-7)),
    '13.2 (run_0013)': (13.2, 1.21426e20, 2.43961e18, 2.974e17, 4.2739, 59.2376, 1.73e12, dict(Vcc=0.053, Vlin=0.999, mu=48.95, Ion=3.07e-6)),
    '2.0 Nt x1.5 (run_0023)': (2.0, 7.5e20, 3.27444e18, 2.5e17, 3.9467, 13.30, 1.73e12, dict(Vcc=0.758, Vlin=1.841, mu=10.50, Ion=3.815e-7)),
}
P('=== 1. Benchmark of the 1-D semi-analytic model against ATLAS (same V1 parameters; interface Gaussian, deep Gaussian and 2-D contact effects omitted) ===')
RES = {}
for name, (t, nta, nc, nd, chi, mun, qf, ref) in cases.items():
    F = Film(t, nta, 0.04, nc, nd, chi, Qf=qf); R = F.sweep(); I = idvg(R, mun, vg); f = feats(vg, I); RES[name] = (F, R, I, f)
    P(f"{name}: 1D Vcc={f['Vcc']:.3f} (ATLAS {ref['Vcc']}), Vlin={f['Vlin']:.3f} ({ref['Vlin']}), mu_FE={f['mu']:.2f} ({ref['mu']}), Ion={f['Ion']:.3e} ({ref['Ion']:.3e}); partition mu_FE/mun={f['mu']/mun:.3f}")
    # free/trapped partition at Vg = Vlin(meas-ish) and 3 V
    for v in (1.0, 2.0, 3.0):
        nf = np.interp(v, R[:, 0], R[:, 1]); ntr = np.interp(v, R[:, 0], R[:, 2])
        P(f'      Vg={v:.1f}: n_free={nf*1e-4:.2e} cm-2, n_trap={ntr*1e-4:.2e} cm-2, free fraction={nf/(nf+ntr):.3f}')

P('\n=== 2. Pre-registered 6.3 nm re-partition candidate (from part-1 Jacobian): Nt x2.05 & x1.43, mu_band 17.2, Qf 9.4e11 ===')
for fac in (1.43, 1.72, 2.05):
    F = Film(6.3, 2.11464e20*fac, 0.04, 2.54976e18, 2.525e17, 4.2276, Qf=9.39e11); R = F.sweep()
    I = idvg(R, 17.2*0.911, vg); f = feats(vg, I)
    P(f'  Nt x{fac}: 1D Vcc={f["Vcc"]:.3f} Vlin={f["Vlin"]:.3f} gap={f["Vlin"]-f["Vcc"]:.3f} mu_FE={f["mu"]:.2f} Ion={f["Ion"]:.3e}  (meas 0.644 / 1.820 / 1.176 / 10.95 / 4.03e-7)')
F = Film(6.3, 2.11464e20, 0.04, 2.54976e18, 2.525e17, 4.2276, Qf=8.7e10); R = F.sweep(); I = idvg(R, 10.6492, vg); f = feats(vg, I)
P(f'  reference tuned (Nt law, mu 11.69, Qf 8.7e10): Vcc={f["Vcc"]:.3f} Vlin={f["Vlin"]:.3f} gap={f["Vlin"]-f["Vcc"]:.3f} mu_FE={f["mu"]:.2f} Ion={f["Ion"]:.3e}')

P('\n=== 3. Trap-limited (MTR) temperature expectation, T-independent mu_band, Nc ~ T^1.5, tail/WTA fixed ===')
k1 = 1/(kB*300) - 1/(kB*350)
for name in ('2.0 (run_0012)', '13.2 (run_0013)'):
    t, nta, nc, nd, chi, mun, qf, ref = cases[name]
    F3 = Film(t, nta, 0.04, nc, nd, chi, T=350.0, Qf=qf); R3 = F3.sweep(); I3 = idvg(R3, mun, vg); f3 = feats(vg, I3)
    F0, R0, I0, f0 = RES[name]
    P(f"{name}: 300K Vcc={f0['Vcc']:.3f} Vlin={f0['Vlin']:.3f} mu_FE={f0['mu']:.2f} Ion={f0['Ion']:.3e} | 350K Vcc={f3['Vcc']:.3f} Vlin={f3['Vlin']:.3f} mu_FE={f3['mu']:.2f} Ion={f3['Ion']:.3e}")
    P(f"     dVcc={f3['Vcc']-f0['Vcc']:+.3f} V, dVlin={f3['Vlin']-f0['Vlin']:+.3f} V, mu_FE x{f3['mu']/f0['mu']:.3f}, Ion x{f3['Ion']/f0['Ion']:.3f}")
    line = []
    for v in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        i0 = np.interp(v, vg, I0); i3 = np.interp(v, vg, I3)
        line.append(f'Vg={v}:Ea={np.log(i3/i0)/k1*1000:.0f}meV')
        u0 = np.interp(v, R0[:, 0], R0[:, 3])
        line[-1] += f'(Ec-EF_s={u0*1000:.0f}meV)'
    P('     apparent activation of Id at fixed Vg: ' + ', '.join(line))

P('\n=== 4. Percolation / barrier (Kamiya-type, Gaussian barrier distribution) and phonon factors, 300 -> 350 K ===')
for phi in (0.02, 0.04, 0.06):
    for sig in (0.0, 0.01, 0.02):
        fac = np.exp(-(phi - sig**2/(2*kB*350))/(kB*350) + (phi - sig**2/(2*kB*300))/(kB*300))
        P(f'  phi_m={phi*1000:.0f} meV sigma={sig*1000:.0f} meV: mu(350)/mu(300) = {fac:.3f}; apparent Ea = {np.log(fac)/k1*1000:.1f} meV')
for n in (1.0, 1.5, 2.0):
    P(f'  phonon mu ~ T^-{n}: mu(350)/mu(300) = {(350/300)**-n:.3f}; if phonons are a fraction f of 1/mu: factor = 1/(1-f+f*(350/300)**{n})')
P(f'  grain-boundary barrier needed for a x4.6 band-mobility step at 300 K: dPhi = kT ln 4.6 = {kB*300*np.log(4.6)*1000:.0f} meV;'
  f' then mu(350)/mu(300) differs between films by exp(dPhi*k1) = {np.exp(kB*300*np.log(4.6)*k1):.2f}')

P('\n=== 5. Coulomb scattering from a charge sheet at distance d from a 2DEG (screened, Ando-Fowler-Stern form; zero-thickness 2DEG = upper bound on scattering) ===')
def mu_coul(ns_cm2, nimp_cm2, d_nm, mstar=0.22, epsbar=9.15):
    ns = ns_cm2*1e4; Ni = nimp_cm2*1e4; d = d_nm*1e-9; ms = mstar*m0; eb = epsbar*e0
    kF = np.sqrt(2*np.pi*ns); qTF = q**2*ms/(2*np.pi*eb*hbar**2)
    def integrand(th):  # q = 2 kF sin(th/2)... use q = 2kF x, x in (0,1): dq/sqrt(1-x^2) -> substitute x = sin(a)
        x = np.sin(th); qq = 2*kF*x
        V = q**2/(2*eb*(qq + qTF))
        return V**2*np.exp(-2*qq*d)*qq**2*2*kF
    I = quad(integrand, 0, np.pi/2, limit=200)[0]
    inv_tau = Ni*ms/(2*np.pi*hbar**3*kF**3)*I
    return q/(ms*inv_tau)*1e4  # cm2/Vs
for ns in (3e12, 1e13):
    P(f'  n_s={ns:.0e}: front Qf 1.73e12 at d=0: mu_C={mu_coul(ns, 1.73e12, 0.0):.0f} cm2/Vs;  d=0.5 nm: {mu_coul(ns, 1.73e12, 0.5):.0f}')
    for t in (2.0, 6.3, 13.2):
        P(f'     back-surface sheet 1.64e12 at d = t - 0.5 nm (t={t}), eps_bar=(9.3+1)/2: mu_C={mu_coul(ns, 1.64e12, t-0.5, epsbar=5.15):.3g} cm2/Vs')
P('  Required to make a x4.6 step from 6.3->13.2 with Matthiessen and mu_other = 62: mu_C(6.3) ~ 1/(1/13.5 - 1/62) =', round(1/(1/13.5 - 1/62), 1))

P('\n=== 6. Roughness scattering magnitudes ===')
for t in (2.0, 6.3, 13.2):
    P(f'  (1-Dsr/t)^2, Dsr=0.287 nm: t={t}: {(1-0.287/t)**2:.3f}')
P(f'  ratio 13.2/6.3 = {((1-0.287/13.2)/(1-0.287/6.3))**2:.3f} ; ratio 13.2/2 = {((1-0.287/13.2)/(1-0.287/2))**2:.3f}')
P('  Thickness-fluctuation (Sakaki/Uchida) mu_SR ~ t^6: if mu_SR(6.3) = 16.7 cm2/Vs (needed for x4.6 with mu_other 62), mu_SR(2) =', round(16.7*(2/6.3)**6, 4), 'cm2/Vs (measured ~12-18 at 2 nm) ->', round(12/(16.7*(2/6.3)**6)), 'x contradiction')
for t, ms in ((2.0, 0.257), (6.3, 0.218), (13.2, 0.211)):
    E1 = 0.376/(ms*t*t); P(f'  t={t}: E1(inf. well)={E1*1000:.1f} meV, dE1 for a {0.287} nm thickness step = {2*E1*0.287/t*1000:.2f} meV')
OUT.close()
