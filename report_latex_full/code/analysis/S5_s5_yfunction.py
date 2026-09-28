"""S5: series-resistance / Y-function / contact analysis on the measured IWO transfer curves
and on ideal-contact ATLAS runs (Rsd = 0 by construction, constant mu_band) as a method check.
Inputs: data/experimental_clean.csv, results/runs/<run>/comparison.csv. No parameters invented:
Cox, W, L, Vd from EVIDENCE_BRIEF.md section 1. Outputs to this folder."""
import json, pathlib
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent
COX = 8.955e-7          # F/cm^2 (brief)
L_CM = 20e-4            # cm
VD = 0.7                # V (schematic)
VTH_LIN = {2.0: 1.663, 6.3: 1.820, 13.2: 1.044}   # brief table (scripts/extract_metrics.py)

def load_meas():
    a = np.genfromtxt(ROOT / "data/experimental_clean.csv", delimiter=",", names=True)
    d = {}
    for t in np.unique(a["thickness_nm"]):
        m = a["thickness_nm"] == t
        o = np.argsort(a["vg_V"][m])
        d[float(t)] = (a["vg_V"][m][o], a["id_A_per_um"][m][o])
    return d

def load_sim(run):
    a = np.genfromtxt(ROOT / f"results/runs/{run}/comparison.csv", delimiter=",", names=True)
    return a["vg_V"], a["atlas_A_per_um"]

def gm_of(vg, idw, method):
    if method == "grad":
        return np.gradient(idw, vg)
    return savgol_filter(idw, 7, 2, deriv=1, delta=vg[1] - vg[0])

def vth_lin(vg, idw):
    gm = np.gradient(idw, vg); k = np.argmax(gm)
    return vg[k] - idw[k] / gm[k], gm[k]

def model_theta(vg, A2, vstar, th):
    vov = np.clip(vg - vstar, 1e-6, None)
    return A2 * vov / (1 + th * vov)

def model_alpha_theta(vg, K, v0, alpha, th):
    vov = np.clip(vg - v0, 1e-6, None)
    return K * vov ** alpha / (1 + th * vov)

def analyse(vg, id_um, vstart, label, gmeth="grad"):
    idw = id_um * 1e4                    # A/cm of width
    gm = gm_of(vg, idw, gmeth)
    m = (vg >= vstart - 1e-9) & (vg <= 3.0 + 1e-9) & (gm > 0)
    x, Y = vg[m], idw[m] / np.sqrt(gm[m])
    # Y-function: Y = A (Vg - V*), A^2 = mu0 Cox Vd / L
    pY, cY = np.polyfit(x, Y, 1, cov=True)
    A, b = pY; vstar = -b / A
    mu0 = A ** 2 * L_CM / (COX * VD)
    q2 = np.polyfit(x, Y, 2)
    curv = q2[0] * (x.max() - x.min()) ** 2 / (A * (x.max() - x.min()))   # quadratic term / linear span
    # theta from 1/sqrt(gm) = (1 + th (Vg - V*))/A  -> slope s = th/A
    s = np.polyfit(x, 1 / np.sqrt(gm[m]), 1)[0]
    th_gm = s * A
    # theta from direct Id fit (alpha fixed = 1)
    p, c = curve_fit(model_theta, x, idw[m], p0=[A ** 2, vstar, 0.05], maxfev=20000)
    A2f, vsf, thf = p; sd = np.sqrt(np.diag(c))
    mu0f = A2f * L_CM / (COX * VD)
    rsd_max = thf * L_CM / (mu0f * COX) * 1e4 if thf > 0 else 0.0   # ohm.um (theta0 = 0 bound)
    # H-function (Cerdeira): H = int Id dVg / Id, slope = 1/(alpha+1), no Vt needed
    ic = np.concatenate([[0], np.cumsum(0.5 * (idw[1:] + idw[:-1]) * np.diff(vg))])
    H = ic[m] / idw[m]
    sH = np.polyfit(x, H, 1)[0]
    alphaH = 1 / sH - 1
    # alpha + theta simultaneously (identifiability)
    try:
        p4, c4 = curve_fit(model_alpha_theta, x, idw[m], p0=[A2f, vsf, 1.0, max(thf, 1e-3)], maxfev=40000)
        sd4 = np.sqrt(np.diag(c4)); corr = c4[2, 3] / (sd4[2] * sd4[3])
    except Exception as e:
        p4, sd4, corr = [np.nan] * 4, [np.nan] * 4, np.nan
    ron = VD / id_um[vg.searchsorted(3.0 - 1e-9)]
    rsh_ch = 1 / (mu0f * COX * (3.0 - vsf))          # ohm/sq at the source end (Vd/2 absorbed in V*)
    return dict(label=label, window=[float(x.min()), float(x.max())], npts=int(m.sum()), gm_method=gmeth,
                mu0_Y=mu0, Vstar_Y=vstar, Y_curv_rel=curv, theta_gm=th_gm,
                mu0_fit=mu0f, Vstar_fit=vsf, theta_fit=thf, theta_fit_sd=sd[2], mu0_fit_sd=sd[0] * L_CM / (COX * VD),
                Rsd_max_ohm_um=rsd_max, Ron_ohm_um=ron, Rsd_frac_max=rsd_max / ron,
                alpha_H=alphaH, alpha4=p4[2], theta4=p4[3], alpha4_sd=sd4[2], theta4_sd=sd4[3], corr_alpha_theta=corr,
                Rsh_ch_ohm_sq=rsh_ch)

def run_all():
    meas = load_meas(); res = {"measured": {}, "atlas_ideal_contacts": {}}
    # 31.8 nm: own Vth_lin
    v31, i31 = meas[31.8]; vt31, _ = vth_lin(v31, i31 * 1e4)
    VTH = dict(VTH_LIN); VTH[31.8] = vt31
    for t in (2.0, 6.3, 13.2, 31.8):
        vg, idm = meas[t]; rows = []
        for off in (VD - 0.2, VD, VD + 0.2):        # Vov > Vd window (linear regime), +/- 0.2 V
            for gmeth in ("grad", "sg"):
                vs = max(VTH[t] + off, -3.0)
                if 3.0 - vs < 0.35: continue
                rows.append(analyse(vg, idm, vs, f"{t} nm Vov>{off:.1f}", gmeth))
        rows.append(analyse(vg, idm, VTH[t] + 0.3, f"{t} nm Vov>0.3 (includes sat. region)", "grad"))
        res["measured"][str(t)] = rows
    sims = {"run_0012 (2 nm cal, mu_band 18.13)": ("run_0012_2p0_v2_full_stepped_final", 2.0),
            "run_0016 (2 nm no confinement)": ("run_0016_2p0_sens_no_confinement", 2.0),
            "run_0015 (6.3 nm tuned, mu 11.69)": ("run_0015_6p3_v2_full_stepped_tuned_qf8p7e10_mu11p69", 6.3),
            "run_0014 (6.3 nm validation, mu 12.4)": ("run_0014_6p3_v2_full_stepped_validation_shared_params", 6.3),
            "run_0013 (13.2 nm cal, mu 61.9)": ("run_0013_13p2_v2_full_stepped_final", 13.2)}
    for k, (run, t) in sims.items():
        vg, ids = load_sim(run); vt, _ = vth_lin(vg, ids * 1e4); rows = []
        for off in (VD - 0.2, VD, VD + 0.2):
            vs = vt + off
            if 3.0 - vs < 0.35: continue
            rows.append(analyse(vg, ids, vs, f"{k} Vov>{off:.1f} (sim Vth_lin {vt:.3f})", "grad"))
        res["atlas_ideal_contacts"][k] = rows
    return res, VTH

def contact_table(res):
    """Transfer length and TLM contact resistance for a grid of specific contact resistivities
    (rho_c NOT measured for Pd/IWO; grid spans literature-implied Ni/In2O3 to poor contacts)."""
    out = []
    rhoc_grid = [1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]   # ohm.cm^2
    for t in ("2.0", "6.3", "13.2"):
        r0 = [r for r in res["measured"][t] if r["gm_method"] == "grad" and "Vov>0.7" in r["label"]][0]
        rsh = r0["Rsh_ch_ohm_sq"]; ron = r0["Ron_ohm_um"]
        for rc in rhoc_grid:
            rc_um2 = rc * 1e8                     # ohm.um^2
            LT = np.sqrt(rc_um2 / rsh)            # um
            for Lov in (1.0, 2.0, 5.0):           # overlap NOT reported -> scan
                Rc = np.sqrt(rc_um2 * rsh) / np.tanh(Lov / LT)   # ohm.um per contact
                out.append(dict(t=t, rhoc_ohm_cm2=rc, Rsh_ohm_sq=rsh, LT_um=LT, Lov_um=Lov,
                                Rc_per_contact_ohm_um=Rc, frac_of_Ron=2 * Rc / ron))
    return out

if __name__ == "__main__":
    res, VTH = run_all()
    res["contact_grid"] = contact_table(res)
    # rho_c needed to make Rsd account for the 2 nm vs 13.2 nm on-resistance gap
    r2 = [r for r in res["measured"]["2.0"] if r["gm_method"] == "grad" and "Vov>0.7" in r["label"]][0]
    r13 = [r for r in res["measured"]["13.2"] if r["gm_method"] == "grad" and "Vov>0.7" in r["label"]][0]
    gap = r2["Ron_ohm_um"] - r13["Ron_ohm_um"]
    rsh13 = r13["Rsh_ch_ohm_sq"]
    rc_needed_um2 = (gap / 2) ** 2 / rsh13
    res["rhoc_needed_for_gap"] = dict(Ron_gap_ohm_um=gap, per_contact=gap / 2, Rsh_used=rsh13,
                                      rhoc_ohm_cm2=rc_needed_um2 * 1e-8, LT_um=np.sqrt(rc_needed_um2 / rsh13),
                                      IR_drop_V_at_2nm=gap * 5.08966e-7)
    # vertical access through the film (accumulated) - specific resistance rho*t
    q = 1.602e-19; va = {}
    for t, mu, vov in ((2.0, r2["mu0_fit"], 3.0 - r2["Vstar_fit"]), (13.2, r13["mu0_fit"], 3.0 - r13["Vstar_fit"])):
        ns = COX * vov / q; n = ns / (t * 1e-7)
        va[t] = dict(ns_cm2=ns, n_avg_cm3=n, rho_ohm_cm=1 / (q * n * mu), rho_t_ohm_cm2=t * 1e-7 / (q * n * mu))
    # undepleted/neutral top part of a 13.2 nm film at Nd_eff = 2.97e17 (model law, FITTED) and mu_band 61.9
    va["13.2_neutral_top"] = dict(rho_t_ohm_cm2=13.2e-7 / (q * 2.97e17 * 61.9))
    res["vertical_access"] = va
    res["VTH_used"] = VTH
    (OUT / "s5_results.json").write_text(json.dumps(res, indent=1, default=float))
    # compact print
    for grp in ("measured", "atlas_ideal_contacts"):
        print("==", grp)
        for k, rows in res[grp].items():
            for r in rows:
                print(f"{r['label']:<58s} {r['gm_method']:4s} win {r['window'][0]:.2f}-{r['window'][1]:.2f} n={r['npts']:2d} "
                      f"mu0Y {r['mu0_Y']:6.2f} V*Y {r['Vstar_Y']:6.3f} curv {r['Y_curv_rel']:+.3f} thGm {r['theta_gm']:+.3f} | "
                      f"mu0 {r['mu0_fit']:6.2f}+-{r['mu0_fit_sd']:.2f} th {r['theta_fit']:+.3f}+-{r['theta_fit_sd']:.3f} "
                      f"RsdMax {r['Rsd_max_ohm_um']:.3g} Ron {r['Ron_ohm_um']:.3g} frac {r['Rsd_frac_max']:.3f} | "
                      f"aH {r['alpha_H']:.2f} a4 {r['alpha4']:.2f}+-{r['alpha4_sd']:.2f} th4 {r['theta4']:+.3f}+-{r['theta4_sd']:.3f} "
                      f"corr {r['corr_alpha_theta']:+.2f} Rsh {r['Rsh_ch_ohm_sq']:.3g}")
    print("== rho_c needed", res["rhoc_needed_for_gap"])
    print("== vertical", res["vertical_access"])
    print("== contact grid (Lov = 2 um)")
    for c in res["contact_grid"]:
        if c["Lov_um"] == 2.0:
            print(f"t {c['t']:>4s} rho_c {c['rhoc_ohm_cm2']:.0e} LT {c['LT_um']:.3g} um Rc {c['Rc_per_contact_ohm_um']:.3g} ohm.um 2Rc/Ron {c['frac_of_Ron']:.3g}")
