"""S5 checks: (1) ideal gradual-channel baseline of the H-function exponent in the same windows (Vd = 0.7 V is not
<< Vov), (2) forward effect of a series resistance on the ideal and on the measured-like curve, (3) which mobility
definition could reproduce the paper's 5.1 / 27.4 cm2/Vs from the workbook curves (provenance test)."""
import numpy as np, pathlib
from scipy.optimize import brentq
ROOT = pathlib.Path(__file__).resolve().parents[3]
COX, L, VD, W_L = 8.955e-7, 20e-4, 0.7, 290 / 20

def gca(vov, beta, vd=VD):
    vov = np.maximum(vov, 0)
    return np.where(vov > vd, beta * (vov * vd - vd ** 2 / 2), beta * vov ** 2 / 2)

def alpha_H(vg, i, lo, hi):
    ic = np.concatenate([[0], np.cumsum(0.5 * (i[1:] + i[:-1]) * np.diff(vg))])
    m = (vg >= lo - 1e-9) & (vg <= hi + 1e-9)
    return 1 / np.polyfit(vg[m], ic[m] / i[m], 1)[0] - 1

vg = np.round(np.arange(-3, 3.0001, 0.05), 3)
print("== (1) ideal GCA baseline alpha_H (Vd = 0.7 V), windows Vov in [0.7, Vov_max]")
for t, vt in ((2.0, 1.663), (6.3, 1.820), (13.2, 1.044)):
    i = gca(vg - vt, 1.0)
    print(f"t {t}: Vth {vt}: alpha_H ideal = {alpha_H(vg, i + 1e-30, vt + 0.7, 3.0):.3f}")

print("== (2) forward model: GCA + Rsd, 2 nm-like (mu 8.8, V*~1.45) and 13.2 nm-like (mu 41, Vt 0.85-0.35)")
for lab, mu, vt in (("2 nm", 8.8, 1.10), ("13.2 nm", 41.0, 0.50)):
    beta = mu * COX / L    # A/V^2 per cm width
    for rsd_um in (0, 1e4, 3e4, 9.2e4, 3e5, 1.15e6):
        rsd = rsd_um * 1e-4   # ohm.cm
        I = np.array([brentq(lambda I: I - gca(v - I * rsd / 2 - vt, beta, VD - I * rsd), 0, (VD / rsd if rsd else 10) * 0.999999) for v in vg])
        vtl = vt + 0.35
        gmx = np.gradient(I, vg).max()
        print(f"{lab} Rsd {rsd_um:8.3g} ohm.um: Ion(3V) {I[-1]*1e-4:.3e} A/um, muFE {gmx*L/(COX*VD):6.2f}, "
              f"alpha_H[{vtl+0.7:.2f},3] {alpha_H(vg, I + 1e-30, vtl + 0.7, 3.0):.3f}, IR drop {I[-1]*rsd:.3f} V")

print("== (3) mobility-definition test against paper 5.1 (2 nm) / 27.4 (13.2 nm)")
a = np.genfromtxt(ROOT / "data/experimental_clean.csv", delimiter=",", names=True)
for t, vth_lin, vth_cc in ((2.0, 1.663, 0.662), (13.2, 1.044, 0.083), (6.3, 1.820, 0.644)):
    m = a["thickness_nm"] == t; v = a["vg_V"][m]; i = a["id_A_per_um"][m] * 1e4; o = np.argsort(v); v, i = v[o], i[o]
    gm = np.gradient(i, v)
    mu_lin = gm.max() * L / (COX * VD)
    mu_sat = (np.gradient(np.sqrt(i), v).max()) ** 2 * 2 * L / COX
    mu_eff3_lin = i[-1] * L / (COX * VD * (3 - vth_lin))
    mu_eff3_cc = i[-1] * L / (COX * VD * (3 - vth_cc))
    mu_eff3_cc_half = i[-1] * L / (COX * VD * (3 - vth_cc - VD / 2))
    print(f"t {t}: muFE_lin {mu_lin:.2f}; mu_sat-formula {mu_sat:.2f}; mu_eff(3V,Vth_lin) {mu_eff3_lin:.2f}; "
          f"mu_eff(3V,Vth_cc) {mu_eff3_cc:.2f}; mu_eff(3V,Vth_cc,-Vd/2) {mu_eff3_cc_half:.2f}; "
          f"muFE_lin/paper {mu_lin/{2.0:5.1,13.2:27.4}.get(t, np.nan):.2f}")
