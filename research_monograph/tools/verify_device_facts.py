"""Independent re-derivation of the core device metrics from data/experimental_clean.csv.

Written from the definitions in analysis_2026-10-06_extraction/PROTOCOL.md (not by importing extraction.py), to
check ledger claims C002 (V_th,cc), C003 (off-state floors), C029 (31.8 nm), C030 (saturation-formula mobility
peaks) and the I_D(+3 V) values of 01_CURRENT_STATE.md section D. Output: evidence/derived/device_facts.json.
Run from the repository root:  python3 -I research_monograph/tools/verify_device_facts.py
"""
import csv
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CSV = ROOT / "data" / "experimental_clean.csv"
OUT = ROOT / "research_monograph" / "evidence" / "derived" / "device_facts.json"

COX = 8.9554e-7          # F/cm^2, geometric C_ox of the protocol (HfO2 15 nm eps 19.57 + Al2O3 2 nm eps 9.0)
W_UM, L_UM = 290.0, 20.0
I_CC = 1e-9              # A/um, constant-current threshold level

# ledger / state values to compare with (label in parentheses)
EXPECTED = {
    "vth_cc_V": {"2.0": 0.662, "6.3": 0.644, "13.2": 0.083},                       # C002 (DERIVED)
    "floor_A_per_um": {"2.0": 4.61e-15, "6.3": 1.53e-13, "13.2": 6.60e-12},        # C003 (DERIVED)
    "id_p3V_A_per_um": {"2.0": 5.09e-7, "6.3": 4.03e-7, "13.2": 3.07e-6, "31.8": 3.59e-6},
    "id_m3V_A_per_um": {"2.0": 1.9e-16, "6.3": 1.9e-13, "13.2": 6.8e-12, "31.8": 3.0e-7},
    "mu_sat_peak_cm2_Vs": {"2.0": 5.09, "6.3": 3.86, "13.2": 27.40},                 # C030 (DERIVED)
}


def cox_check():
    eps0 = 8.8541878128e-14  # F/cm
    t_hf, e_hf, t_al, e_al = 15e-7, 19.57, 2e-7, 9.0
    return 1.0 / (t_hf / (e_hf * eps0) + t_al / (e_al * eps0))


def load():
    data = {}
    with open(CSV) as f:
        for r in csv.DictReader(f):
            t = r["thickness_nm"]
            data.setdefault(t, []).append((float(r["vg_V"]), float(r["id_A_per_um"])))
    for t in data:
        data[t].sort()
    return data


def vth_cc(pts):
    """Log-linear interpolation at the last upward crossing of I_CC (the crossing nearest the on-state)."""
    out = None
    for (v0, i0), (v1, i1) in zip(pts, pts[1:]):
        if 0 < i0 < I_CC <= i1:
            out = v0 + (math.log10(I_CC) - math.log10(i0)) * (v1 - v0) / (math.log10(i1) - math.log10(i0))
    return out


def floor(pts):
    vals = sorted(i for v, i in pts if -2.0 - 1e-9 <= v <= -0.5 + 1e-9)
    n = len(vals)
    return vals[n // 2] if n % 2 else 0.5 * (vals[n // 2 - 1] + vals[n // 2])


def mu_sat_peak(pts):
    """Peak of 2L/(W C_ox) (d sqrt(I_D)/dV_G)^2, I_D the total current (A), central differences."""
    v = [p[0] for p in pts]
    s = [math.sqrt(p[1] * W_UM) for p in pts]
    best = (0.0, None)
    for k in range(1, len(v) - 1):
        d = (s[k + 1] - s[k - 1]) / (v[k + 1] - v[k - 1])
        mu = 2.0 * (L_UM * 1e-4) / ((W_UM * 1e-4) * COX) * d * d
        if mu > best[0]:
            best = (mu, v[k])
    return best


def at(pts, vg):
    return min(pts, key=lambda p: abs(p[0] - vg))[1]


def main():
    data = load()
    res = {"cox_recomputed_F_cm2": cox_check(), "films": {}, "comparison": []}
    for t, pts in sorted(data.items(), key=lambda kv: float(kv[0])):
        mu, vpk = mu_sat_peak(pts)
        res["films"][t] = {"n_points": len(pts), "vth_cc_V": vth_cc(pts), "floor_A_per_um": floor(pts),
                           "id_p3V_A_per_um": at(pts, 3.0), "id_m3V_A_per_um": at(pts, -3.0),
                           "on_off_p3_over_m3": at(pts, 3.0) / at(pts, -3.0),
                           "mu_sat_peak_cm2_Vs": mu, "mu_sat_peak_at_V": vpk}
    for q, ref in EXPECTED.items():
        for t, e in ref.items():
            got = res["films"][t][q]
            rel = None if got is None else (got - e) / e
            res["comparison"].append({"quantity": q, "film_nm": t, "expected": e, "recomputed": got,
                                      "rel_diff": rel})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1))
    print("C_ox recomputed %.5e F/cm2 (protocol 8.9554e-07)" % res["cox_recomputed_F_cm2"])
    for c in res["comparison"]:
        r = c["recomputed"]
        print(f"{c['quantity']:22s} {c['film_nm']:>5s}  expected {c['expected']:<10.4g} recomputed "
              f"{(r if r is not None else float('nan')):<12.5g} rel {c['rel_diff'] if c['rel_diff'] is None else round(c['rel_diff'], 4)}")
    print("31.8 nm V_th,cc:", res["films"]["31.8"]["vth_cc_V"], "(expected none)")


if __name__ == "__main__":
    main()
