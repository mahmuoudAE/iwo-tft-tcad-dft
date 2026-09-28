"""S3 task 2: minimal self-consistent 1-D Schrodinger-Poisson (SP) vs classical 3-D Fermi-Dirac model of the
IWO TFT gate stack, channel centre, Vd = 0 (equilibrium with the S/D Fermi level, EF = 0).

Stack (bottom -> top): TiN gate (WF 4.70 eV, ASSUMED as in V1) | HfO2 15 nm eps 19.57 | Al2O3 2 nm eps 9.0 |
IWO t nm eps 9.3, chi_bulk 4.3 eV | air (no charge; Neumann dU/dy = 0 at the IWO top, as in the ATLAS air volume).
Fixed charges as in V1: Qf = +1.73e12 cm^-2 at Al2O3/IWO, Nd_eff(t) uniform ionized donors.
Energies in eV; U(y) = local vacuum level (electron potential energy), Ec(y) = U - chi. d/dy(eps eps0 dU/dy) = +rho.

Electron models
  C0  classical 3-D FD, chi = 4.3 (no confinement), Nc(m = 0.208)                 ~ ATLAS runs 0016 / 0017 / 0034
  C1  classical 3-D FD, chi = 4.3 - dEc_ATLAS(t), Nc(m*(t))                        ~ ATLAS runs 0012 / 0014 / 0013
  Q*  SP: 1-D effective-mass Schrodinger across Al2O3 | IWO | vacuum (1.5 nm), 2-D subband FD statistics,
      in-plane DOS mass m*(1+2 a K_k), confinement mass m*(1+a K_k) (Kane, a = C), predictor-corrector
      (Trellakis-type) Newton outer loop.
      Q1 m*=0.18, a=0.5, finite barriers 3.4 eV (Al2O3, ASSUMED = ATLAS loaded chi 0.9) / 4.3 eV (vacuum),
         barrier mass = well mass (central; reproduces the PBE-slab spill of ~0.15 nm per side, see s3_e1)
      Q2 same, hard wall at the physical film boundaries (upper bound of confinement)
      Q3 same, BenDaniel-Duke with heavy barrier masses 0.4 m0 (Al2O3) / 1.0 m0 (vacuum) (lower bound)
      Q4 m*=0.257 parabolic (ATLAS m*(2 nm)), finite barriers equal mass
      Q5 m*=0.35 parabolic, finite barriers equal mass
Optional traps ("T" suffix): V1 acceptor tail NTA = Nt(t)/WTA, WTA 0.04 eV and the V1 interface acceptor sheet
(3e11 cm^-2 eV^-1 at Ec-0.3 eV, W 0.12 eV) as fixed CLASSICAL DOS referenced to a local edge
Ec_ref = U - chi + shift_ref.  shift_ref = dEc_ATLAS for C1T (as ATLAS does); for QnT two limits:
'conf' shift_ref = flat-band equivalent quantum shift (tail rides with the confined edge, ATLAS-like), and
'bulk' shift_ref = 0 (localized tail states unaffected by confinement).  The deep Gaussian (5e16) is omitted
(< 1 mV). No image-charge, exchange-correlation, disorder, or 2-D (lateral) effects: see report.
"""
import json, sys
import numpy as np
from scipy.linalg import solve_banded, eigh_tridiagonal
if not hasattr(np, 'trapezoid'):
    np.trapezoid = np.trapz

Q = 1.602177e-19; EPS0 = 8.8541878e-14; KT = 0.025852; H2M = 0.0380998
PHI_M, CHI = 4.70, 4.30
T_OX = (15.0, 2.0); EPS_OX = (19.57, 9.0); EPS_S = 9.3
QF = 1.73e12
DZ = 0.02  # nm
VAC_PAD = 1.5
LAW_DEC = lambda t: 0.9205 * t ** -1.3815
LAW_M = lambda t: 0.208 + 0.1311 * t ** -1.412
LAW_NT = lambda t: 2e19 * (2.0 / t) ** 0.75
LAW_ND = lambda t: 2.5e17 * (1 + (t / 20.0) ** 4)
WTA, DIT_PEAK, DIT_E, DIT_W = 0.04, 3e11, 0.3, 0.12


def F12(eta):
    a = eta ** 4 + 33.6 * eta * (1 - 0.68 * np.exp(-0.17 * (eta + 1) ** 2)) + 50
    return 1.0 / (np.exp(-eta) + 0.75 * np.sqrt(np.pi) * a ** (-0.375))


def nc3(m):
    return 2 * (m * KT / (4 * np.pi * H2M)) ** 1.5 * 1e21  # cm^-3


# ---- trap occupancy tables vs x = Ec_ref - EF ------------------------------------------------------------
XG = np.arange(-1.5, 3.5, 0.001)
_u = np.arange(0, 3.0, 0.0005)
TAIL_TAB = np.array([np.trapezoid(np.exp(-_u / WTA) / (1 + np.exp(np.clip((x - _u) / KT, -700, 700))), _u) for x in XG])
_s = np.arange(-0.6, 0.6, 0.0005)
DIT_TAB = np.array([np.trapezoid(DIT_PEAK * np.exp(-(_s / DIT_W) ** 2) / (1 + np.exp(np.clip((x - DIT_E + _s) / KT, -700, 700))), _s) for x in XG])


def tab(tabv, x):
    v = np.interp(x, XG, tabv)
    d = (np.interp(x + 1e-3, XG, tabv) - np.interp(x - 1e-3, XG, tabv)) / 2e-3
    return v, d


class Device:
    def __init__(self, t, nd, nt=0.0, traps=False):
        self.t = t
        n_ox = int(round(sum(T_OX) / DZ)); n_s = int(round(t / DZ))
        self.y = np.arange(n_ox + n_s + 1) * DZ
        self.i_int = n_ox
        yh = 0.5 * (self.y[1:] + self.y[:-1])
        self.eps_h = np.where(yh < T_OX[0], EPS_OX[0], np.where(yh < sum(T_OX), EPS_OX[1], EPS_S))
        self.w = np.zeros_like(self.y)  # IWO volume weight (nm) per node
        self.w[self.i_int + 1:-1] = DZ; self.w[self.i_int] = DZ / 2; self.w[-1] = DZ / 2
        self.iwo = self.w > 0
        self.nd, self.nt, self.traps = nd, nt, traps
        c = EPS0 / (DZ * 1e-7) ** 2 * 1e-7 * DZ  # flux coefficient per node (F/cm^2/nm-ish), see residual
        self.k_h = self.eps_h * EPS0 / (DZ * 1e-7)   # F/cm^2 : flux = k_h * (U_{i+1}-U_i)  [C/cm^2 per V]

    # charge per node (C/cm^2) and derivative wrt U
    def fixed_and_traps(self, U, shift_ref):
        rho = np.zeros_like(U); drho = np.zeros_like(U)
        wcm = self.w * 1e-7
        rho += Q * self.nd * wcm
        rho[self.i_int] += Q * QF
        if self.traps:
            x = U - CHI + shift_ref  # Ec_ref - EF
            v, d = tab(TAIL_TAB, x)
            nta = self.nt / WTA
            rho -= Q * nta * v * wcm; drho -= Q * nta * d * wcm
            vi, di = tab(DIT_TAB, x[self.i_int])
            rho[self.i_int] -= Q * vi; drho[self.i_int] -= Q * di
        return rho, drho

    def newton(self, U, Vg, dens, shift_ref, tol=1e-9, itmax=200):
        """Solve A U = rho(U); dens(U) -> (n [cm^-3] per node, dn/dU)."""
        N = len(U); U = U.copy(); U[0] = PHI_M - Vg
        for it in range(itmax):
            flux = self.k_h * np.diff(U)
            R = np.zeros(N); R[:-1] += flux; R[1:] -= flux   # R_i = flux_{i+1/2} - flux_{i-1/2}
            R = -R  # R_i = -(flux_right - flux_left) ; we need flux_right - flux_left - rho = 0
            rho, drho = self.fixed_and_traps(U, shift_ref)
            n, dn = dens(U)
            wcm = self.w * 1e-7
            rho = rho - Q * n * wcm; drho = drho - Q * dn * wcm
            F = -R - rho       # (flux_r - flux_l) - rho
            F[0] = 0.0
            # Jacobian: d(flux_r - flux_l)/dU_i = -(k_r + k_l); off-diagonals +k
            kl = np.r_[0.0, self.k_h]; kr = np.r_[self.k_h, 0.0]
            diag = -(kl + kr) - drho
            ab = np.zeros((3, N))
            ab[0, 1:] = self.k_h; ab[2, :-1] = self.k_h; ab[1] = diag
            ab[1, 0] = 1.0; ab[0, 1] = 0.0
            dU = solve_banded((1, 1), ab, -F)
            dU = np.clip(dU, -0.2, 0.2)
            U += dU
            if np.max(np.abs(dU)) < tol:
                return U, it
        return U, -1


def classical_dens(dev, dec, m):
    nc = nc3(m)
    def dens(U):
        n = np.zeros_like(U); dn = np.zeros_like(U)
        eta = -(U[dev.iwo] - (CHI - dec)) / KT
        f = F12(eta); fp = (F12(eta + 1e-4) - F12(eta - 1e-4)) / 2e-4
        n[dev.iwo] = nc * f; dn[dev.iwo] = -nc * fp / KT
        return n, dn
    return dens


class SchrodingerSolver:
    def __init__(self, dev, m, a_np, bc, v_al=3.4, mb=(None, None)):
        self.dev, self.m, self.a, self.bc = dev, m, a_np, bc
        self.v_al = v_al; self.mb = mb
        i0 = dev.i_int
        if bc == 'hard':
            self.idx = np.arange(i0 + 1, len(dev.y) - 1)   # psi = 0 at the physical boundaries
            self.nvac = 0; self.nal = 0
        else:
            nal = int(round(T_OX[1] / DZ))
            self.idx = np.arange(i0 - nal, len(dev.y))     # Al2O3 + IWO nodes (interface node = IWO side)
            self.nal = nal; self.nvac = int(round(VAC_PAD / DZ))

    def potential(self, U):
        dev = self.dev
        V = U[self.idx] - CHI
        region = np.zeros(len(self.idx), int)  # 0 IWO, 1 Al2O3, 2 vacuum
        if self.bc != 'hard':
            region[:self.nal] = 1
            V[:self.nal] = U[self.idx[:self.nal]] - (CHI - self.v_al)
            V = np.r_[V, np.full(self.nvac, U[-1] - 0.0)]  # vacuum level above the film
            region = np.r_[region, np.full(self.nvac, 2)]
        return V, region

    def solve(self, U, emax_above_ef=0.35, kmax=40):
        V, region = self.potential(U)
        levels = []
        for k in range(kmax):
            K = 0.1
            for _ in range(4 if self.a > 0 else 1):
                mw = self.m * (1 + self.a * K)
                m = np.where(region == 0, mw, np.where(region == 1, self.mb[0] or mw, self.mb[1] or mw))
                mh = 2 / (1 / m[:-1] + 1 / m[1:]); c = H2M / (mh * DZ * DZ)
                d = V.copy(); d[:-1] += c; d[1:] += c
                if self.bc == 'hard':
                    d[0] += H2M / (mw * DZ * DZ); d[-1] += H2M / (mw * DZ * DZ)
                w, v = eigh_tridiagonal(d, -c, select='i', select_range=(k, k))
                p = v[:, 0] ** 2; p /= p.sum() * DZ
                inside = region == 0
                K = max(w[0] - float((p[inside] * V[inside]).sum() / p[inside].sum()), 1e-4)
            mdos = self.m * (1 + 2 * self.a * K)
            levels.append((w[0], p[:len(self.idx)], mdos, K))
            if w[0] > emax_above_ef:
                break
        return levels


def quantum_dens_factory(dev, levels, U_s, idx):
    def dens(U):
        n = np.zeros_like(U); dn = np.zeros_like(U)
        dU = U[idx] - U_s[idx]
        for E, p, md, K in levels:
            g = md * KT / (2 * np.pi * H2M) * 1e14   # cm^-2
            x = (E + dU) / KT
            N2 = g * np.logaddexp(0, -x)
            sig = 1 / (1 + np.exp(np.clip(x, -700, 700)))
            n[idx] += N2 * p * 1e7            # p in nm^-1 -> cm^-1
            dn[idx] += -g * sig / KT * p * 1e7
        # only IWO nodes carry electrons (penetration into Al2O3/vacuum counted onto IWO boundary is neglected;
        # the Al2O3-side tail is dropped from Poisson, the vacuum tail is not on the grid)
        n[~dev.iwo] = 0; dn[~dev.iwo] = 0
        return n, dn
    return dens


def sweep(dev, mode, vgs, **kw):
    U = np.full(len(dev.y), PHI_M - vgs[0])
    out = []
    shift_ref = kw.get('shift_ref', 0.0)
    for vg in vgs:
        if mode == 'classical':
            dens = classical_dens(dev, kw['dec'], kw['m'])
            U, it = dev.newton(U, vg, dens, shift_ref)
            n, _ = dens(U); levels = None
        else:
            ss = kw['solver']
            for outer in range(80):
                levels = ss.solve(U)
                dens = quantum_dens_factory(dev, levels, U.copy(), ss.idx[:len(ss.idx)])
                Unew, it = dev.newton(U, vg, dens, shift_ref)
                err = np.max(np.abs(Unew - U)); U = Unew
                if err < 1e-6:
                    break
            n, _ = dens(U)
        wcm = dev.w * 1e-7
        ns = float((n * wcm).sum())
        zc = float((n * dev.w * (dev.y - dev.y[dev.i_int])).sum() / max((n * dev.w).sum(), 1e-300))
        rho, _ = dev.fixed_and_traps(U, shift_ref)
        ntr = float(-(rho.sum() - Q * dev.nd * wcm.sum() - Q * QF) / Q)  # trapped electrons, cm^-2
        # Gauss check: gate charge = -(total charge in stack)
        qg = dev.k_h[0] * (U[1] - U[0])  # C/cm^2 field at gate
        out.append(dict(vg=float(vg), ns=ns, zc_nm=zc, ntrap=ntr, E1=(levels[0][0] if levels else None),
                        Ec_int=float(U[dev.i_int] - CHI), gauss=float(qg + (Q * (dev.nd * wcm.sum() + QF - ns - ntr)))))
    return out


def vg_at(res, level):
    vg = np.array([r['vg'] for r in res]); ns = np.array([r['ns'] for r in res])
    ok = ns > 0
    lg = np.log10(ns[ok]); v = vg[ok]
    if level < 10 ** lg.min() or level > 10 ** lg.max():
        return None
    return float(np.interp(np.log10(level), lg, v))


def ceff(res, v1, v2):
    vg = np.array([r['vg'] for r in res]); ns = np.array([r['ns'] for r in res])
    i1, i2 = np.argmin(abs(vg - v1)), np.argmin(abs(vg - v2))
    return Q * (ns[i2] - ns[i1]) / (vg[i2] - vg[i1])


def main(traps=False, thick=(2.0, 6.3, 13.2)):
    vgs = np.round(np.arange(-1.0, 3.0001, 0.04), 4)
    summary = {}
    for t in thick:
        nd = LAW_ND(t); nt = LAW_NT(t)
        dev = Device(t, nd, nt, traps=traps)
        cases = {}
        cases['C0'] = sweep(dev, 'classical', vgs, dec=0.0, m=0.208)
        cases['C1'] = sweep(dev, 'classical', vgs, dec=LAW_DEC(t), m=LAW_M(t), shift_ref=LAW_DEC(t))
        qdefs = {'Q1': (0.18, 0.5, 'finite', (None, None)), 'Q2': (0.18, 0.5, 'hard', (None, None)),
                 'Q3': (0.18, 0.5, 'finite', (0.4, 1.0)), 'Q4': (0.257, 0.0, 'finite', (None, None)),
                 'Q5': (0.35, 0.0, 'finite', (None, None))}
        if traps:
            qdefs = {'Q1': qdefs['Q1'], 'Q2': qdefs['Q2']}
        # flat-band equivalent shift for the 'conf' tail reference: from the no-trap run at n_s=1e10
        for name, (m, a, bc, mb) in qdefs.items():
            ss = SchrodingerSolver(dev, m, a, bc, mb=mb)
            if not traps:
                cases[name] = sweep(dev, 'quantum', vgs, solver=ss)
            else:
                sref = FLAT_SHIFT.get((t, name), 0.0)
                cases[name + '_conf'] = sweep(dev, 'quantum', vgs, solver=ss, shift_ref=sref)
                cases[name + '_bulk'] = sweep(dev, 'quantum', vgs, solver=ss, shift_ref=0.0)
        s = {}
        for k, r in cases.items():
            s[k] = dict(vg_1e10=vg_at(r, 1e10), vg_1e11=vg_at(r, 1e11), vg_1e12=vg_at(r, 1e12),
                        ceff_2_3=ceff(r, 2.0, 3.0), ceff_1p5_2p5=ceff(r, 1.5, 2.5),
                        zc_at_3V=r[-1]['zc_nm'], ns_3V=r[-1]['ns'], ntrap_3V=r[-1]['ntrap'],
                        zc_at_1e12=float(np.interp(np.log10(1e12), np.log10([max(x['ns'], 1e-30) for x in r]), [x['zc_nm'] for x in r])),
                        E1_at_1e10=(float(np.interp(np.log10(1e10), np.log10([max(x['ns'], 1e-30) for x in r]), [x['E1'] - x['Ec_int'] if x['E1'] is not None else np.nan for x in r])) if r[0]['E1'] is not None else None),
                        max_gauss_err_Ccm2=max(abs(x['gauss']) for x in r))
        summary[str(t)] = s
        print(f"\n===== t = {t} nm  (Nd {nd:.3g}, traps={traps}, Nt {nt:.3g}) =====")
        print("case      Vg(1e10)  Vg(1e11)  Vg(1e12)   Ceff(2-3V)/Cox  zc(1e12) zc(3V) nm  ns(3V)    ntrap(3V)  E1-Ec_int@1e10  gaussErr")
        cox = 1 / (T_OX[0] * 1e-7 / (EPS_OX[0] * EPS0) + T_OX[1] * 1e-7 / (EPS_OX[1] * EPS0))
        for k, v in s.items():
            f = lambda z: 'None' if z is None else f"{z:8.4f}"
            print(f"{k:9s} {f(v['vg_1e10'])}  {f(v['vg_1e11'])}  {f(v['vg_1e12'])}   {v['ceff_2_3']/cox:8.4f}      {v['zc_at_1e12']:6.3f} {v['zc_at_3V']:6.3f}  {v['ns_3V']:9.3e} {v['ntrap_3V']:9.3e}  {f(v['E1_at_1e10'])}  {v['max_gauss_err_Ccm2']:.1e}")
        base = s['C0']
        print("shifts vs C0 (V):      d@1e10    d@1e11    d@1e12")
        for k, v in s.items():
            if k == 'C0':
                continue
            d = [None if (v[x] is None or base[x] is None) else v[x] - base[x] for x in ('vg_1e10', 'vg_1e11', 'vg_1e12')]
            print(f"  {k:9s}            " + "  ".join('None' if z is None else f"{z:8.4f}" for z in d))
        summary[str(t) + '_cox'] = cox
        sys.stdout.flush()
    return summary


FLAT_SHIFT = {}
if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'notraps'
    if mode == 'notraps':
        s = main(traps=False)
        json.dump(s, open('s3_sp1d_notraps.json', 'w'), indent=1)
    else:
        # 'conf' tail reference = no-trap Q-vs-C0 shift at n_s = 1e10 (flat-band equivalent quantum shift)
        prev = json.load(open('s3_sp1d_notraps.json'))
        for t in (2.0, 6.3, 13.2):
            for q in ('Q1', 'Q2'):
                FLAT_SHIFT[(t, q)] = prev[str(t)][q]['vg_1e10'] - prev[str(t)]['C0']['vg_1e10']
        print('flat-band equivalent shifts used for tail reference:', FLAT_SHIFT)
        s = main(traps=True)
        json.dump(s, open('s3_sp1d_traps.json', 'w'), indent=1)
