"""Figure for section 09 (oxygen vacancies near W, register H-L) of the NTU presentation.

Reads only repository data (no computed number is typed in):
  qe_workflow/analysis_2026-10-13_full/out/f11_hl_vacancy.json
      differences_eV.{dE_local_O30, dE_local_O72_sensitivity, dE_dop}.{k3_g005, k4_g005, k3_g002, threshold_eV}
      cells.<cell>.k3_to_k4_meV and cells.<cell>.g002_minus_g005_k3_meV (per-cell total-energy changes)
  (the JSON is the independent re-parse of cern_htcondor/results/evidence_20261013_HL/r23.out by f11_hl_vacancy.py;
   the same data underlie monograph figure fig11_hl_vacancy, FIGURE_INDEX FIG-Q-fig11_hl_vacancy).

Writes presentation_ntu/figures/09_hl_scores.pdf:
  (a) the three registered or reported differences on the three tested settings, with the registered thresholds
      (+0.3 eV for dE_local at the registered near site O30, +0.05 eV for dE_dop; O72 has no registered rule);
  (b) per-cell total-energy changes k4 - k3 (Gaussian 0.005 Ry) and Gaussian 0.002 - 0.005 Ry (k3).
Run from anywhere:  python3 -I research_monograph/presentation_ntu/tools/fig_09_hl.py
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = pathlib.Path(__file__).resolve().parent
PRES = HERE.parent
ROOT = PRES.parents[1]
OUT = PRES / "figures"
SRC = ROOT / "qe_workflow" / "analysis_2026-10-13_full" / "out" / "f11_hl_vacancy.json"

MM = 1 / 25.4
BLACK, GREY, LGREY, MAROON = "#000000", "#7a7a7a", "#c8c8c8", "#801924"

plt.rcParams.update({
    "font.family": "Liberation Sans",
    "mathtext.fontset": "custom",
    "mathtext.rm": "Liberation Sans",
    "mathtext.it": "Liberation Sans:italic",
    "mathtext.bf": "Liberation Sans:bold",
    "font.size": 7.6,
    "axes.labelsize": 7.6,
    "xtick.labelsize": 6.9,
    "ytick.labelsize": 6.9,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.minor.width": 0.4,
    "ytick.minor.width": 0.4,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": False,
    "ytick.right": True,
    "axes.edgecolor": "black",
    "axes.facecolor": "white",
    "figure.facecolor": "white",
    "legend.frameon": False,
    "legend.fontsize": 6.8,
    "lines.linewidth": 1.0,
    "lines.markersize": 4.4,
    "hatch.linewidth": 0.5,
    "pdf.fonttype": 42,
})

D = json.loads(SRC.read_text())
DIFF = D["differences_eV"]
CELLS = D["cells"]
SETS = ["k3_g005", "k4_g005", "k3_g002"]
SETLAB = {"k3_g005": r"$k3$, G 0.005 Ry", "k4_g005": r"$k4$, G 0.005 Ry", "k3_g002": r"$k3$, G 0.002 Ry"}
SETSTY = {"k3_g005": dict(marker="o", mfc="white", mec=BLACK),
          "k4_g005": dict(marker="s", mfc="white", mec=MAROON),
          "k3_g002": dict(marker="^", mfc="white", mec=GREY)}


def panel_label(ax, s):
    ax.text(-0.02, 1.035, s, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.4, fontweight="bold")


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(74 * MM, 47 * MM), gridspec_kw={"width_ratios": [1.0, 1.08]})

    # (a) differences on the three settings; dashed: registered thresholds
    names = ["dE_local_O30", "dE_local_O72_sensitivity", "dE_dop"]
    xl = ["$\\Delta E_{\\mathrm{local}}$\nO30", "$\\Delta E_{\\mathrm{local}}$\nO72", "$\\Delta E_{\\mathrm{dop}}$"]
    for j, s in enumerate(SETS):
        x = np.arange(3) + (j - 1) * 0.22
        ax1.plot(x, [DIFF[n][s] for n in names], ls="none", mew=0.9, **SETSTY[s])
    for i, n in enumerate(names):
        thr = DIFF[n]["threshold_eV"]
        if thr is not None:
            ax1.hlines(thr, i - 0.42, i + 0.42, color=BLACK, ls="--", lw=0.8)
    ax1.set_xticks(range(3))
    ax1.set_xticklabels(xl, fontsize=6.9)
    ax1.set_xlim(-0.55, 2.55)
    ax1.set_ylim(0, 0.86)
    ax1.set_yticks([0, 0.2, 0.4, 0.6, 0.8])
    ax1.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(2))
    ax1.tick_params(axis="x", which="both", length=0)
    ax1.set_ylabel("difference (eV)")
    panel_label(ax1, "(a)")

    # (b) per-cell total-energy changes
    order = ["In32O48", "In31WO48", "In32O47", "In31WO47_far", "In31WO47_near", "In31WO47_near72"]
    lab = ["In$_{32}$O$_{48}$", "In$_{31}$WO$_{48}$", "In$_{32}$O$_{47}$", "far", "near", "near72"]
    x = np.arange(len(order))
    ax2.bar(x - 0.19, [CELLS[c]["k3_to_k4_meV"] for c in order], 0.36, color="white", edgecolor=BLACK, lw=0.7)
    ax2.bar(x + 0.19, [CELLS[c]["g002_minus_g005_k3_meV"] for c in order], 0.36, color="white", edgecolor=GREY,
            hatch="//////", lw=0.7)
    ax2.axhline(0, color=BLACK, lw=0.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(lab, rotation=45, ha="right", rotation_mode="anchor", fontsize=6.6)
    ax2.tick_params(axis="x", which="both", length=0)
    ax2.set_xlim(-0.6, len(order) - 0.4)
    ax2.set_ylim(-25, 34)
    ax2.set_yticks([-20, -10, 0, 10, 20, 30])
    ax2.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(2))
    ax2.set_ylabel("per-cell change (meV)")
    panel_label(ax2, "(b)")

    # one legend above both panels (no text boxes inside the data area)
    h = [Line2D([], [], ls="none", mew=0.9, **SETSTY[s]) for s in SETS] + \
        [Line2D([], [], color=BLACK, ls="--", lw=0.8),
         Patch(facecolor="white", edgecolor=BLACK, lw=0.7),
         Patch(facecolor="white", edgecolor=GREY, hatch="//////", lw=0.7)]
    lab_ = [SETLAB[s] for s in SETS] + ["(a) registered threshold", r"(b) $k4 - k3$", "(b) G 0.002 $-$ 0.005 Ry"]
    # k3, k4: 3x3x3 and 4x4x4 k-point grids (defined on the slide); G: Gaussian smearing width
    # two legend columns: left = the three settings of panel (a), right = threshold of (a) and the two bars of (b)
    idx = [0, 1, 2, 3, 4, 5]
    fig.tight_layout(pad=0.3, w_pad=1.2, rect=(0, 0, 1, 0.765))
    fig.legend([h[i] for i in idx], [lab_[i] for i in idx], loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=2,
               handlelength=1.3, labelspacing=0.25, columnspacing=1.2, borderaxespad=0.2, handletextpad=0.4,
               fontsize=6.6)
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "09_hl_scores.pdf")
    plt.close(fig)
    print("saved", OUT / "09_hl_scores.pdf")
    for n in names:
        print(n, {s: DIFF[n][s] for s in SETS}, "thr", DIFF[n]["threshold_eV"])
    for c in order:
        print(c, CELLS[c]["k3_to_k4_meV"], CELLS[c]["g002_minus_g005_k3_meV"])


if __name__ == "__main__":
    main()
