"""Figure mono_threshold_vs_dft: measured V_th,cc against the threshold trend implied by the computed conduction-band
shift alone, anchored at the 2.0 nm device: V_th(t) = V_th(2.0) + [dEc(t) - dEc(2.0)] (rigid 1:1 affinity shift, as in the
registered affinity-only runs). Band: the four dEc fit options of b03 (fit3, fit2, fit3 with the 0.695 nm point at
-/+0.17 eV). Points: measured V_th,cc recomputed from data/experimental_clean.csv (FACT-101..103). Also shown: the three
failed out-of-sample 6.3 nm predictions (C014). Plain style, no text in panels. DERIVED illustration, not a model run.
"""
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("figstyle", ROOT / "qe_workflow/analysis_2026-10-13_full/figstyle.py")
fs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fs)
plt, CYCLE = fs.plt, fs.CYCLE

dev = json.loads((ROOT / "research_monograph/evidence/derived/device_facts.json").read_text())["films"]
LAWS = {"fit3": (0.70176, 1.3176), "fit2": (0.76182, 1.47845), "fit3 low": (0.65386, 1.17918),
        "fit3 high": (0.74509, 1.43496)}
t = [2.0 + 0.1 * i for i in range(113)]
v2 = dev["2.0"]["vth_cc_V"]
curves = {k: [v2 + a * x ** -p - a * 2.0 ** -p for x in t] for k, (a, p) in LAWS.items()}
lo = [min(c[i] for c in curves.values()) for i in range(len(t))]
hi = [max(c[i] for c in curves.values()) for i in range(len(t))]
meas_t = [2.0, 6.3, 13.2]
meas_v = [dev[k]["vth_cc_V"] for k in ("2.0", "6.3", "13.2")]
miss = [-0.29, -0.37, -0.23]  # C014: run_0014 (V1), V2 variant P, V2 variant E

fig, ax = plt.subplots(figsize=(fs.HALF_W * 1.25, fs.HALF_W * 0.95))
ax.fill_between(t, lo, hi, color=CYCLE[0], alpha=0.25, lw=0, label=r"$V_{\rm th}(2.0)+\Delta E_{\rm c}(t)-\Delta E_{\rm c}(2.0)$")
ax.plot(t, curves["fit2"], '-', color=CYCLE[0], lw=1)
ax.plot(meas_t, meas_v, 'o', mfc='none', color='k', label="measured")
ax.plot([6.3] * 3, [meas_v[1] + m for m in miss], 'x', color=CYCLE[1], label="out-of-sample predictions")
ax.set_xlabel("channel thickness (nm)")
ax.set_ylabel(r"$V_{\rm th,cc}$ (V)")
ax.set_xlim(1.5, 14)
ax.legend(frameon=False, fontsize=7, loc="lower left")
fig.tight_layout()
out = ROOT / "research_monograph/figures"
fig.savefig(out / "mono_threshold_vs_dft.pdf")
fig.savefig(out / "mono_threshold_vs_dft.png", dpi=200)
print("saved", out / "mono_threshold_vs_dft.pdf")
