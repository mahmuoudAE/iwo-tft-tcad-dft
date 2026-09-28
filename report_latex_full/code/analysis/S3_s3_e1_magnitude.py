"""S3 task 1: magnitude of electron confinement in IWO films (2 / 6.3 / 13.2 nm).

Pure effective-mass estimates, no fitting to the device data.
(a) infinite well, parabolic;  (b) finite asymmetric barriers (Al2O3 below, vacuum/air above),
BenDaniel-Duke finite differences;  (c) Kane non-parabolicity E(1+aE)=hbar^2k^2/2m (a = C = 0.5 eV^-1,
Stokey2021 citing Feneberg: m*(0)=0.18+/-0.02 m0, C=0.5+/-0.02 eV^-1), implemented as an energy-dependent
confinement mass m(E)=m*(1+aK) iterated to self-consistency (exact for the infinite well);
(d) gate-field (triangular) confinement for a given electron sheet density;
(e) consistency of the effective-mass+NP picture with the three PBE slab points used by the ATLAS dEc law;
(f) 'subthreshold-equivalent' rigid Ec shift = the quantity a classical DD model must put into dEc so that
    the non-degenerate free sheet density equals the quantum one (includes the 2-D vs 3-D DOS factor).
Barrier heights are ASSUMED ranges (see report): Al2O3 CBO 2.0 / 3.4 / 4.0 eV (low guess / ATLAS loaded default
chi(Al2O3)=0.9 -> 4.3-0.9 / Si2021 '>4 eV'); vacuum barrier = chi_IWO = 4.3 eV (Fan2021 estimate, model yaml).
Barrier masses ASSUMED: Al2O3 0.4 m0, vacuum 1.0 m0.
"""
import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.optimize import least_squares

H2M = 0.0380998          # hbar^2/(2 m0) in eV nm^2
KT = 0.025852            # eV at 300 K
Q = 1.602177e-19; EPS0 = 8.8541878e-14  # C, F/cm
EPS_IWO = 9.3
TS = [2.0, 6.3, 13.2]
ATLAS_DEC = {2.0: 0.9205 * 2.0**-1.3815, 6.3: 0.9205 * 6.3**-1.3815, 13.2: 0.9205 * 13.2**-1.3815}
ATLAS_MSTAR = {t: 0.208 + 0.1311 * t**-1.412 for t in TS}


def e_inf(m, t, n=1):
    return H2M * (n * np.pi / t) ** 2 / m


def kane(epar, a):
    return epar if a == 0 else (np.sqrt(1 + 4 * a * epar) - 1) / (2 * a)


def fd_levels(t, m_w, a_np=0.0, vb_bot=3.4, mb_bot=0.4, vb_top=4.3, mb_top=1.0, nlev=4, dz=0.005, pad=1.5):
    """BenDaniel-Duke FD eigenvalues of a flat finite well [0,t] (energies from the well bottom).
    Non-parabolicity: confinement mass m_w*(1+a*K), K = E - <V>, iterated per level."""
    z = np.arange(-pad, t + pad + dz / 2, dz)
    V = np.where(z < 0, vb_bot, np.where(z > t, vb_top, 0.0))
    out = []
    for lev in range(nlev):
        K = 0.0
        for _ in range(60):
            mw = m_w * (1 + a_np * K)
            m = np.where(z < 0, mb_bot, np.where(z > t, mb_top, mw))
            mh = 2.0 / (1.0 / m[:-1] + 1.0 / m[1:])            # harmonic mean on half nodes
            c = H2M / (mh * dz * dz)                                # coupling
            diag = V.copy(); diag[:-1] += c; diag[1:] += c
            w, v = eigh_tridiagonal(diag, -c, select='i', select_range=(lev, lev))
            psi2 = v[:, 0] ** 2; psi2 /= psi2.sum()
            Knew = w[0] - float((psi2 * V).sum())
            if abs(Knew - K) < 1e-7:
                break
            K = Knew
        pin = float(psi2[(z >= 0) & (z <= t)].sum())
        out.append((w[0], K, pin))
    return out


def tri_E1(F_Vcm, m):
    """Airy ground state of a triangular well, F in V/cm, m in m0 -> eV; and <z> = 2E1/(3qF) in nm."""
    F = F_Vcm * 1e-7  # V/nm
    e1 = 2.33811 * (H2M / m) ** (1 / 3) * F ** (2 / 3)
    return e1, 2 * e1 / (3 * F)


def ns_2d_rel(levels_K_E, m, t, m_cl):
    """ratio of the non-degenerate quantum sheet density to the classical Nc(m_cl)*t one at the same (E - EF)
    reference (bulk Ec). levels: list of (E_n, m_dos_n)."""
    # 2-D: sum m_n kT/(pi hbar^2) exp(-E_n/kT); 3-D: Nc t = 2 (m kT/(2 pi hbar^2))^1.5 t
    # in units hbar^2/2m0 = H2M: m kT/(pi hbar^2) = m kT /(2 pi H2M) [nm^-2]
    s = sum(mn * KT / (2 * np.pi * H2M) * np.exp(-En / KT) for En, mn in levels_K_E)
    nc_t = 2 * (m_cl * KT / (4 * np.pi * H2M)) ** 1.5 * t
    return s / nc_t


def main():
    print("=== (a,c) infinite well, parabolic vs Kane NP (a=0.5 eV^-1) ; E1 in eV ===")
    print("t_nm  m*   E1_inf  E1_inf_NP   ATLAS_dEc  kT=0.0259")
    for t in TS:
        for m in (0.18, 0.208, 0.257, 0.35):
            print(f"{t:5.1f} {m:5.3f} {e_inf(m, t):7.4f} {kane(e_inf(m, t), 0.5):8.4f}   {ATLAS_DEC[t]:7.4f}")
    print("\n=== (b) finite barriers (BenDaniel-Duke FD), E1 [eV], fraction of |psi|^2 inside film ===")
    print("t   m*    a    VbAl2O3  E1      K1     P_in   E2")
    rows = {}
    for t in TS:
        for m, a in ((0.18, 0.5), (0.18, 0.0), (0.257, 0.0), (0.35, 0.0)):
            for vb in (2.0, 3.4, 4.0):
                lv = fd_levels(t, m, a, vb_bot=vb, nlev=2)
                rows[(t, m, a, vb)] = lv
                print(f"{t:4.1f} {m:5.3f} {a:3.1f} {vb:6.1f}  {lv[0][0]:7.4f} {lv[0][1]:7.4f} {lv[0][2]:6.4f} {lv[1][0]:7.4f}")
    # sensitivity: vacuum barrier 3.0 eV, barrier masses = well mass
    for t in TS:
        lv = fd_levels(t, 0.18, 0.5, vb_bot=3.4, vb_top=3.0, mb_bot=0.18, mb_top=0.18, nlev=1)
        print(f"  sens t={t}: Vtop=3.0 eV, barrier masses = 0.18 m0 -> E1={lv[0][0]:.4f}")

    print("\n=== (e) PBE slab points vs effective-mass + NP with effective width t+delta ===")
    pts = np.array([[0.95, 0.94], [1.5, 0.60], [1.98, 0.33]])  # model yaml fit points (Lin2022, Si2021, Lin2022)
    def model(p, t, m=0.17):
        a, d = p
        return np.array([kane(e_inf(m, tt + d), a) for tt in np.atleast_1d(t)])
    fit = least_squares(lambda p: model(p, pts[:, 0]) - pts[:, 1], x0=[0.5, 0.3], bounds=([0, -0.5], [3, 2]))
    a_fit, d_fit = fit.x
    print(f"m=0.17 (Lin2022 PBE bulk): alpha_fit={a_fit:.3f} eV^-1, delta_fit={d_fit:.3f} nm, residuals={fit.fun}")
    for a_fix in (0.5,):
        f2 = least_squares(lambda p: model([a_fix, p[0]], pts[:, 0]) - pts[:, 1], x0=[0.3])
        print(f"alpha fixed {a_fix}: delta={f2.x[0]:.3f} nm, residuals={f2.fun}")
    for t in TS + [3.0, 4.0, 5.0]:
        pw = 0.9205 * t ** -1.3815
        em = model([a_fit, d_fit], t)[0]
        em5 = model([0.5, f2.x[0]], t)[0]
        print(f"  t={t:5.2f}  ATLAS power law {pw:.4f}  EM+NP(fit) {em:.4f}  EM+NP(a=0.5) {em5:.4f}  ratio law/EM {pw/em:.2f}")
    # local exponent of the physically shaped law
    for t in (2.0, 6.3, 13.2):
        e1, e2 = model([a_fit, d_fit], t * 0.99)[0], model([a_fit, d_fit], t * 1.01)[0]
        print(f"  local exponent d ln E / d ln t at {t}: {np.log(e2/e1)/np.log(1.01/0.99):.2f}")

    print("\n=== (f) subthreshold-equivalent rigid shift dEc_eq = -kT ln(n2D/n3D) [eV] ===")
    print("t   case                         E1      dEc_eq(Nc m=0.208)  dEc_eq(Nc m*(t) ATLAS)  ATLAS dEc")
    for t in TS:
        for lab, m, a, vb in (("finite 3.4eV, m0.18, NP0.5", 0.18, 0.5, 3.4), ("finite 3.4eV, m0.257 par", 0.257, 0.0, 3.4),
                              ("finite 3.4eV, m0.35 par", 0.35, 0.0, 3.4), ("hard wall, m0.18 NP0.5", 0.18, 0.5, None)):
            nl = 12 if t > 6 else 6
            if vb is None:
                levs = [(kane(e_inf(m, t, n), a), m * (1 + 2 * a * kane(e_inf(m, t, n), a))) for n in range(1, nl + 1)]
            else:
                lv = fd_levels(t, m, a, vb_bot=vb, nlev=nl, dz=0.01 if t > 6 else 0.005)
                levs = [(E, m * (1 + 2 * a * K)) for E, K, _ in lv]   # in-plane DOS mass at subband bottom (Kane)
            r208 = ns_2d_rel(levs, m, t, 0.208)
            rat = ns_2d_rel(levs, m, t, ATLAS_MSTAR[t])
            print(f"{t:4.1f} {lab:28s} {levs[0][0]:7.4f}   {-KT*np.log(r208):8.4f}           {-KT*np.log(rat):8.4f}            {ATLAS_DEC[t]:.4f}")

    print("\n=== (d) gate-field (triangular) confinement: n_s -> F = q n_s/(eps_IWO eps0) at the front interface ===")
    print("n_s[cm^-2]  F[V/cm]   E1_tri(m0.18)  <z>_tri[nm]  E1_tri(m0.35) <z>")
    for ns in (1e10, 1e11, 1e12, 3e12, 1e13, 1.3e13):
        F = Q * ns / (EPS_IWO * EPS0)
        e1a, za = tri_E1(F, 0.18); e1b, zb = tri_E1(F, 0.35)
        print(f"{ns:9.1e}  {F:9.2e}  {e1a:8.4f}      {za:7.2f}     {e1b:8.4f}  {zb:6.2f}")
    # n_s at Vg = 3 V ~ Cox (3 - Vth_cc)/q using measured Vth_cc
    cox = 8.955e-7
    for t, vth in ((2.0, 0.662), (6.3, 0.644), (13.2, 0.083)):
        print(f"  t={t}: n_s(Vg=3V) ~ Cox(3-Vth_cc)/q = {cox*(3-vth)/Q:.2e} cm^-2 (upper bound; ignores trapped charge)")

    print("\n=== image-charge (dielectric) confinement, single air interface, eps 9.3/1 ===")
    k = (EPS_IWO - 1) / (EPS_IWO + 1)
    for zz in (0.5, 1.0, 2.0, 3.0):
        vim = Q / (16 * np.pi * EPS0 * 1e2 * EPS_IWO * zz * 1e-9) * k  # eps0 in F/m
        print(f"  z={zz} nm from air side: +{vim*1e3:.1f} meV")


if __name__ == "__main__":
    main()
