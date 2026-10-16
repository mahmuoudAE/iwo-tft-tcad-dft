"""Figure for section 10 (from first principles to the device) of the NTU presentation.

10_rigid.pdf: measured constant-current thresholds against the trend implied by the computed conduction-band shift
alone, anchored at the 2.0 nm device, V_th(t) = V_th(2.0) + [dEc(t) - dEc(2.0)] (rigid 1:1 affinity shift, as in the
registered affinity-only runs). This is the presentation-style redraw of research_monograph/figures/
mono_threshold_vs_dft (generator research_monograph/tools/fig_threshold_vs_dft.py, caption in chapter M12); same data,
plain deck style (black, grey, one maroon accent). DERIVED illustration, not a model run.

Reads only repository data:
  qe_workflow/analysis_2026-10-13_full/bands_masses/out/b03_gaps_laws.json   laws.dEc_eV: fit3, fit2_1and2nm,
                                                                             fit3_0p695_low, fit3_0p695_high
  research_monograph/evidence/derived/device_facts.json                     measured V_th,cc (FACT-101..103;
                                                                             data: Prof. M.-H. Lee's group, NTU)
  research_monograph/evidence/derived/multiscale_budget.json                measured.miss_6p3 (C014)

Writes presentation_ntu/figures/10_rigid.pdf.
Run from anywhere:  python3 -I research_monograph/presentation_ntu/tools/fig_10_multiscale.py
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
PRES = HERE.parent
ROOT = PRES.parents[1]
OUT = PRES / "figures"
B03 = ROOT / "qe_workflow/analysis_2026-10-13_full/bands_masses/out/b03_gaps_laws.json"
DEV = ROOT / "research_monograph/evidence/derived/device_facts.json"
BUD = ROOT / "research_monograph/evidence/derived/multiscale_budget.json"
MM = 1 / 25.4
MAROON, GREY, LGREY = "#801924", "#4d4d4d", "#c8c8c8"

plt.rcParams.update({
    "font.family": "Liberation Sans",
    "mathtext.fontset": "custom",
    "mathtext.rm": "Liberation Sans",
    "mathtext.it": "Liberation Sans:italic",
    "mathtext.bf": "Liberation Sans:bold",
    "font.size": 7.5,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.minor.width": 0.4,
    "ytick.minor.width": 0.4,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "axes.edgecolor": "black",
    "axes.facecolor": "white",
    "figure.facecolor": "white",
    "legend.frameon": False,
    "legend.fontsize": 6.5,
    "lines.linewidth": 1.1,
    "pdf.fonttype": 42,
})


def main():
    laws = json.loads(B03.read_text())["laws"]["dEc_eV"]
    keys = ["fit3", "fit2_1and2nm", "fit3_0p695_low", "fit3_0p695_high"]
    films = json.loads(DEV.read_text())["films"]
    miss = json.loads(BUD.read_text())["measured"]["miss_6p3"]

    v2 = films["2.0"]["vth_cc_V"]
    t = np.linspace(2.0, 13.2, 225)
    curves = {}
    for k in keys:
        a, p = laws[k]["a"], laws[k]["p"]
        curves[k] = v2 + a * t ** -p - a * 2.0 ** -p
    lo = np.min([curves[k] for k in keys], axis=0)
    hi = np.max([curves[k] for k in keys], axis=0)

    meas_t = [2.0, 6.3, 13.2]
    meas_v = [films[k]["vth_cc_V"] for k in ("2.0", "6.3", "13.2")]

    fig, ax = plt.subplots(figsize=(64 * MM, 43 * MM))
    ax.fill_between(t, lo, hi, color=LGREY, lw=0, label=r"rigid $\Delta E_\mathrm{c}$, four fits")
    ax.plot(t, curves["fit2_1and2nm"], "-", color=GREY, lw=0.8, label=r"rigid $\Delta E_\mathrm{c}$, two-point fit")
    ax.plot([6.3] * len(miss), [meas_v[1] + m for m in miss], "x", color=MAROON, ms=5, mew=1.2,
            label="6.3 nm predictions")
    ax.plot(meas_t, meas_v, "o", mfc="white", mec="black", mew=1.0, ms=5, label="measured")
    ax.set_xlabel("channel thickness (nm)")
    ax.set_ylabel(r"$V_\mathrm{th,cc}$ (V)")
    ax.set_xlim(1.0, 14.2)
    ax.set_ylim(0.0, 0.82)
    ax.set_xticks([2, 4, 6, 8, 10, 12, 14])
    ax.minorticks_on()
    ax.legend(loc="upper right", handlelength=1.4, borderaxespad=0.3, labelspacing=0.35)
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.21, top=0.97)
    fig.savefig(OUT / "10_rigid.pdf")
    print("saved", OUT / "10_rigid.pdf")


if __name__ == "__main__":
    main()
