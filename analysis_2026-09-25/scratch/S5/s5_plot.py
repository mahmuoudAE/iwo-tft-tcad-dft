"""Figure: Y-function and H-function (threshold-free exponent) for measured curves vs ideal-contact ATLAS runs."""
import pathlib, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
ROOT = pathlib.Path(__file__).resolve().parents[3]; OUT = pathlib.Path(__file__).resolve().parent
a = np.genfromtxt(ROOT / "data/experimental_clean.csv", delimiter=",", names=True)
runs = {2.0: "run_0012_2p0_v2_full_stepped_final", 6.3: "run_0015_6p3_v2_full_stepped_tuned_qf8p7e10_mu11p69",
        13.2: "run_0013_13p2_v2_full_stepped_final"}
fig, ax = plt.subplots(1, 3, figsize=(13, 4))
col = {2.0: "#1f77b4", 6.3: "#d62728", 13.2: "#2ca02c", 31.8: "#7f7f7f"}
for t in (2.0, 6.3, 13.2, 31.8):
    m = a["thickness_nm"] == t; v = a["vg_V"][m]; i = a["id_A_per_um"][m] * 1e4; o = np.argsort(v); v, i = v[o], i[o]
    gm = np.gradient(i, v); ok = (v > 0) & (gm > 0)
    ax[0].plot(v[ok], i[ok] / np.sqrt(gm[ok]) / np.sqrt(i[ok] / np.sqrt(gm[ok])).max() ** 2, "o", ms=3, color=col[t], label=f"{t} nm meas")
    ax[1].plot(v, gm * 1e-4, "-", color=col[t], label=f"{t} nm meas")
    ic = np.concatenate([[0], np.cumsum(0.5 * (i[1:] + i[:-1]) * np.diff(v))]); H = ic / i
    ax[2].plot(v[v > 0], H[v > 0], "-", color=col[t], label=f"{t} nm meas")
    if t in runs:
        s = np.genfromtxt(ROOT / f"results/runs/{runs[t]}/comparison.csv", delimiter=",", names=True)
        vs, isim = s["vg_V"], s["atlas_A_per_um"] * 1e4; g = np.gradient(isim, vs); k = (vs > 0) & (g > 0)
        ax[0].plot(vs[k], isim[k] / np.sqrt(g[k]) / np.sqrt(i[ok] / np.sqrt(gm[ok])).max() ** 2, "--", color=col[t], label=f"{t} nm ATLAS (Rsd=0)")
        ax[1].plot(vs, g * 1e-4, "--", color=col[t])
        ics = np.concatenate([[0], np.cumsum(0.5 * (isim[1:] + isim[:-1]) * np.diff(vs))]); ax[2].plot(vs[vs > 0], (ics / isim)[vs > 0], "--", color=col[t])
ax[0].set(xlabel="Vg (V)", ylabel="Y = Id/sqrt(gm) (normalised)", title="Y-function (linear => const. mu, Rsd via curvature)")
ax[1].set(xlabel="Vg (V)", ylabel="gm (A/V/um)", yscale="log", ylim=(1e-9, 3e-6), title="gm: no roll-off at 2 nm; strong roll-off at 31.8 nm")
ax[2].set(xlabel="Vg (V)", ylabel="H = int(Id dVg)/Id (V)", title="H-function: slope = 1/(alpha+1)")
ax[0].legend(fontsize=7); ax[1].legend(fontsize=7)
fig.tight_layout(); fig.savefig(OUT / "s5_yfunction_hfunction.png", dpi=130)
print("saved", OUT / "s5_yfunction_hfunction.png")
