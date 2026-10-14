"""Monograph analysis (2026-10-14): tests of simple confinement models against the computed crystalline slab series.

Inputs (all COMPUTED, crystalline PBE, read from the re-derivation JSON):
  bulk band-edge mass and Kane alpha (b01_masses.json: bulk electron [100] Kane 10-point),
  slab dEc / dEv / dEg and in-plane masses and alphas (f05_slab_series.json, b01_masses.json, RESULTS_LOG 2026-10-14),
  HSE ratio (f07_hse_ratio.json), HSE bulk mass estimates (RESULTS_LOG 2026-10-14: 0.159-0.193 m0).
Outputs: evidence/derived/confinement_analysis.json and a printed summary. Labels: every output is DERIVED (model
applied to computed numbers); none is a new computation of the electronic structure.
Run from the repository root:  python3 -I research_monograph/tools/confinement_analysis.py
"""
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
AF = ROOT / "qe_workflow/analysis_2026-10-13_full"
OUT = ROOT / "research_monograph/evidence/derived/confinement_analysis.json"
HB2M = 3.80998  # hbar^2 / (2 m0) in eV A^2
KT = 0.025852   # eV at 300 K

b01 = json.loads((AF / "bands_masses/out/b01_masses.json").read_text())
f05 = json.loads((AF / "out/f05_slab_series.json").read_text())
kane = b01["bulk"]["electron"]["[100]"]["kane"]["10"]
M_B, ALPHA = 0.1541, 0.58        # consolidated band-edge values (RESULTS_LOG 2026-10-14; FACT-004/005)
ALPHA_RANGE = (0.55, 0.63)

# computed slab series (H-H thickness, nm): dEc, dEv (signed), dEg, 2-D DOS band-edge mass, in-plane alpha
SLABS = {
    0.4612: dict(dEc=1.585, dEv=-0.667, dEg=2.2514, m=0.443, a=0.24, note="In8(OH)24, outside laws"),
    0.6953: dict(dEc=1.059, dEv=-0.251, dEg=1.3099, m=0.337, a=0.31, note="polar, dEc +-0.17 eV (assumed)"),
    0.9303: dict(dEc=0.8477, dEv=-0.0521, dEg=0.8998, m=0.279, a=0.36, note=""),
    1.9623: dict(dEc=0.2812, dEv=-0.0540, dEg=0.3352, m=0.203, a=0.47, note=""),
}


def e_kane(eps0, alpha):
    """Energy E solving E(1 + alpha E) = eps0."""
    return (-1.0 + math.sqrt(1.0 + 4.0 * alpha * eps0)) / (2.0 * alpha)


def k_from_e(E, m, alpha):
    return math.sqrt(E * (1 + alpha * E) * m / HB2M)  # 1/A


out = {"inputs": {"m_b": M_B, "alpha": ALPHA, "alpha_range": ALPHA_RANGE, "kane_10pt_[100]": kane}, "slabs": {}}

# 1) in-plane mass of the confined subband: m_par = m_b (1 + 2 alpha dEc); in-plane alpha_par = alpha / (1 + 2 alpha dEc)
for t, s in SLABS.items():
    mp = M_B * (1 + 2 * ALPHA * s["dEc"])
    mp_lo = M_B * (1 + 2 * ALPHA_RANGE[0] * s["dEc"])
    mp_hi = M_B * (1 + 2 * ALPHA_RANGE[1] * s["dEc"])
    ap = ALPHA / (1 + 2 * ALPHA * s["dEc"])
    # 2) effective box width from the bulk Kane band: E(k = pi/t_eff) = dEc
    k = k_from_e(s["dEc"], M_B, ALPHA)
    t_eff = math.pi / k / 10.0  # nm
    # infinite parabolic well with t = H-H
    e_inf = HB2M * (math.pi / (t * 10)) ** 2 / M_B
    e_np = e_kane(e_inf, ALPHA)
    # local power-law exponent of a Kane band at E: p = 2 (1 + aE) / (1 + 2 aE)
    p_loc = 2 * (1 + ALPHA * s["dEc"]) / (1 + 2 * ALPHA * s["dEc"])
    out["slabs"][f"{t:.3f}"] = dict(
        computed=s, m_par_pred=round(mp, 4), m_par_pred_range=[round(mp_lo, 4), round(mp_hi, 4)],
        m_par_rel_err=round(mp / s["m"] - 1, 4), alpha_par_pred=round(ap, 3),
        alpha_par_rel_err=round(ap / s["a"] - 1, 3), t_eff_nm=round(t_eff, 3), t_eff_over_tHH=round(t_eff / t, 3),
        E_infinite_parabolic_eV=round(e_inf, 3), E_infinite_kane_eV=round(e_np, 3), p_local_kane=round(p_loc, 3))

# 3) exponents between 1 and 2 nm: computed dEc, dEg and the Kane prediction with t_eff proportional to t
t1, t2 = 0.9303, 1.9623
r_t = math.log(t2 / t1)
p_dEc = math.log(SLABS[t1]["dEc"] / SLABS[t2]["dEc"]) / r_t
p_dEg = math.log(SLABS[t1]["dEg"] / SLABS[t2]["dEg"]) / r_t
eps2 = SLABS[t2]["dEc"] * (1 + ALPHA * SLABS[t2]["dEc"])
E1_pred = e_kane(eps2 * (t2 / t1) ** 2, ALPHA)
p_kane = math.log(E1_pred / SLABS[t2]["dEc"]) / r_t
# dEg exponent if dEv were exactly constant at its mean value
dEv_mean = 0.5 * (SLABS[t1]["dEv"] + SLABS[t2]["dEv"])
out["exponents_1_2nm"] = dict(p_dEc_computed=round(p_dEc, 4), p_dEg_computed=round(p_dEg, 4),
                              dEc_1nm_kane_pred_from_2nm=round(E1_pred, 4), p_dEc_kane_pred=round(p_kane, 4),
                              dEv_mean=round(dEv_mean, 4))

# 4) effective-mass partition of the opening: CB share = m_h / (m_e + m_h) for a single heavy hole band
shares = {}
for mh in (3.2, 4.4, 7.9, 18.1):
    shares[str(mh)] = round(mh / (M_B + mh), 4)
out["partition"] = dict(cb_share_ema=shares, cb_share_computed={"1.962": 0.84, "0.930": 0.94},
                        dEv_ema_pred_mh3p2={f"{t:.3f}": round(-SLABS[t]["dEc"] * M_B / 3.2, 4) for t in (t1, t2)},
                        # Kane-consistent version (theory review 2026-10-14): the hole sees the same k_z, so its
                        # confinement energy is eps1 * m_b / m_h with eps1 = dEc (1 + alpha dEc) = hbar^2 k_z^2 / 2 m_b.
                        dEv_ema_kane_mh3p2={f"{t:.3f}": round(-SLABS[t]["dEc"] * (1 + ALPHA * SLABS[t]["dEc"]) * M_B / 3.2, 4)
                                            for t in (t1, t2)},
                        cb_share_ema_kane_mh3p2={f"{t:.3f}": round(SLABS[t]["dEc"] / (SLABS[t]["dEc"] + SLABS[t]["dEc"] * (1 + ALPHA * SLABS[t]["dEc"]) * M_B / 3.2), 4)
                                                 for t in (t1, t2)})

# 5) Kane correction factors of the effective densities of states
out["nc_factors"] = dict(nc3d_first_order=round(1 + 3.75 * ALPHA * KT, 4),
                         n2d_first_order_2nm_slab_alpha=round(1 + 2 * SLABS[t2]["a"] * KT, 4))

# 6) HSE ratio from a Kane band with alpha ~ 1/Eg (two-band scaling) and the HSE mass range
eg_pbe, eg_hse = 0.9204, 2.108  # NC-PBE and NC-HSE06 bulk gaps (FACT-032, FACT-031): same pseudopotentials (theory review 2026-10-14)
a_hse = ALPHA * eg_pbe / eg_hse
eps1_pbe = SLABS[t1]["dEc"] * (1 + ALPHA * SLABS[t1]["dEc"])
r = {}
for mh in (0.159, 0.170, 0.193):
    E = e_kane(eps1_pbe * M_B / mh, a_hse)
    r[str(mh)] = round(E / SLABS[t1]["dEc"], 3)
out["hse_ratio_model"] = dict(alpha_hse_assumed=round(a_hse, 3), r_by_hse_mass=r, r_computed=[1.060, 1.107])

# 7) two-band Kane E_P from PBE and what it would predict
ep_pbe = eg_pbe * (1 / M_B - 1)
out["two_band_kane"] = dict(E_P_from_PBE_eV=round(ep_pbe, 2), m_pred_at_HSE_gap=round(1 / (1 + ep_pbe / eg_hse), 3),
                            E_P_implied_by_exp_m0p208_Eg2p8=round(2.8 * (1 / 0.208 - 1), 1))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=1))
for t, d in out["slabs"].items():
    print(t, "m_pred", d["m_par_pred"], "m_comp", d["computed"]["m"], "rel", d["m_par_rel_err"], "| a_par pred",
          d["alpha_par_pred"], "comp", d["computed"]["a"], "| t_eff", d["t_eff_nm"], "ratio", d["t_eff_over_tHH"],
          "| E_inf", d["E_infinite_parabolic_eV"], "E_inf_kane", d["E_infinite_kane_eV"], "| p_loc", d["p_local_kane"])
print("exponents", out["exponents_1_2nm"])
print("partition", out["partition"])
print("Nc factors", out["nc_factors"])
print("HSE model", out["hse_ratio_model"])
print("two-band", out["two_band_kane"])
