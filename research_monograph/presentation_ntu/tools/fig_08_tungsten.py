"""Figures for section 08 (tungsten as a donor) of the NTU presentation.

Reads only repository data (no computed number is typed in):
  qe_workflow/analysis_2026-10-13_full/out/f09_iwo_bulk.json    bulk W cells (8b, 24d): W-O bonds, filling, the
      eigenvalues at Gamma relative to E_F with their W-5d weight (gamma_scatter), E_F - host CB bottom
  qe_workflow/analysis_2026-10-13_full/out/f10_iwo_slabs.json   W on a central 24d site of the relaxed 1 and 2 nm
      films: the same quantities
  qe_workflow/cern_htcondor/results/iwo_W8b/bands.out, iwo_W24d/bands.out   Gamma-star bands of the bulk W cells
      (read with bands_masses/bm.py, as for BM3), E_F from b01_masses.json (scf_k4.out)
  qe_workflow/bulk_In2O3_protocol/bands_gamma.out    pure-bulk conduction band, shifted to the host-CB minimum (as BM3)
Literature reference values (not computed): Shannon (1976) radius sums for six-fold cations with O2- (1.38 A), as
quoted in research_monograph/chapters/13_dft_rev.tex (W6+ 1.98, W5+ 2.00, W4+ 2.04, In3+ 2.18 A) and M10.

Writes presentation_ntu/figures/08_bonds.pdf, 08_levels.pdf, 08_bands.pdf.
Run from anywhere:  python3 -I research_monograph/presentation_ntu/tools/fig_08_tungsten.py
"""
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
PRES = HERE.parent
ROOT = PRES.parents[1]
OUT = PRES / "figures"
QEA = ROOT / "qe_workflow" / "analysis_2026-10-13_full"
sys.path.insert(0, str(QEA / "bands_masses"))
import bm  # noqa: E402  (raw pw.x band reader used for BM3; also loads the study's plot style, overridden below)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

MM = 1 / 25.4
BLACK, GREY, LGREY, MAROON = "#000000", "#7a7a7a", "#c8c8c8", "#801924"
plt.rcParams.update(matplotlib.rcParamsDefault)
plt.rcParams.update({
    "font.family": "Liberation Sans",
    "mathtext.fontset": "custom",
    "mathtext.rm": "Liberation Sans",
    "mathtext.it": "Liberation Sans:italic",
    "mathtext.bf": "Liberation Sans:bold",
    "font.size": 7.8,
    "axes.labelsize": 7.8,
    "xtick.labelsize": 7.0,
    "ytick.labelsize": 7.0,
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
    "legend.fontsize": 6.8,
    "lines.linewidth": 1.1,
    "lines.markersize": 4.2,
    "pdf.fonttype": 42,
})

f09 = json.loads((QEA / "out" / "f09_iwo_bulk.json").read_text())
f10 = json.loads((QEA / "out" / "f10_iwo_slabs.json").read_text())
b01 = json.loads((QEA / "bands_masses" / "out" / "b01_masses.json").read_text())
# (value, label, label row): 13_dft_rev.tex l.1231 (FACT-041); '{+}' keeps mathtext from spacing '+' as an operator.
# W5+ is labelled one row higher: its line is only 0.02 A from the W6+ line.
SHANNON = [(1.98, r"W$^{6{+}}$", 0), (2.00, r"W$^{5{+}}$", 1), (2.04, r"W$^{4{+}}$", 0), (2.18, r"In$^{3{+}}$", 0)]


def save(fig, stem):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f"{stem}.pdf")
    plt.close(fig)
    print("saved", OUT / f"{stem}.pdf")


def panel_label(ax, s):
    ax.text(0.0, 1.025, s, transform=ax.transAxes, ha="left", va="bottom", fontsize=7.5, fontweight="bold")


# ------------------------------------------------------------------------------------------------ W-O bond lengths
def fig_bonds():
    rows = [("bulk, 24d", f09["24d"]["W_O_A"]["value"]), ("bulk, 8b", f09["8b"]["W_O_A"]["value"]),
            ("1 nm, 24d", f10["1 nm"]["W_O_A"]["value"]), ("2 nm, 24d", f10["2 nm"]["W_O_A"]["value"])]
    fig, ax = plt.subplots(figsize=(60 * MM, 46 * MM))
    for x, _, _ in SHANNON:
        ax.axvline(x, color=GREY, ls=":", lw=0.8, zorder=1)
    for i, (lab, bonds) in enumerate(rows):
        y = len(rows) - 1 - i
        b = np.array(bonds)
        u = np.unique(np.round(b, 3))                         # each value occurs twice (24d) or six times (8b)
        ax.plot(u, [y] * len(u), "o", mfc="white", mec=BLACK, mew=0.8, ms=3.6, zorder=3)
        ax.plot([b.mean()] * 2, [y - 0.28, y + 0.28], "-", color=MAROON, lw=1.6, zorder=4)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1])
    ax.tick_params(axis="y", which="both", length=0)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlim(1.84, 2.24)
    ax.set_xticks([1.85, 1.90, 1.95, 2.00, 2.05, 2.10, 2.15, 2.20])
    ax.set_xticklabels(["1.85", "", "1.95", "", "2.05", "", "2.15", ""])
    ax.minorticks_on()
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_xlabel(r"W$-$O bond length ($\mathrm{\AA}$)")
    # Shannon labels above the frame (outside the panel)
    tr = matplotlib.transforms.blended_transform_factory(ax.transData, ax.transAxes)
    for x, lab, row in SHANNON:
        ax.text(x, 1.03 + 0.10 * row, lab, transform=tr, ha="center", va="bottom", fontsize=7.0)
    ax.tick_params(axis="x", which="both", top=False)
    fig.tight_layout(pad=0.3)
    save(fig, "08_bonds")


# ------------------------------------------------------------------------------------------------ W-5d weight at Gamma
def fig_levels():
    rows = [("1 nm", f10["1 nm"]["filling"]), ("2 nm", f10["2 nm"]["filling"]),
            ("bulk 24d", f09["24d"]["filling"]), ("bulk 8b", f09["8b"]["filling"])]
    fig, axs = plt.subplots(len(rows), 1, figsize=(61 * MM, 42 * MM), sharex=True)
    for ax, (lab, fl) in zip(axs, rows):
        ef_c = fl["EF_minus_hostCB_Gamma_eV"]                 # E_F - E_c (host CB bottom at Gamma)
        sc = np.array(fl["gamma_scatter"])                    # (E_n(Gamma) - E_F, W-5d weight)
        x = sc[:, 0] + ef_c                                   # E_n(Gamma) - E_c
        w = sc[:, 1]
        wr = fl["bands"][str(fl["W_rich_band_Gamma"])]["E_Gamma_minus_EF_eV"] + ef_c
        ax.axhline(0, color=BLACK, lw=0.5)
        ax.axvline(0, color=GREY, lw=0.6)
        ax.axvline(ef_c, color=BLACK, ls="--", lw=0.8, zorder=6)
        for xi in x:                                          # every state at Gamma: a short tick below the baseline
            ax.plot([xi, xi], [-0.10, -0.02], "-", color=GREY, lw=0.5)
        for xi, wi in zip(x, w):
            if wi >= 0.01:
                ax.plot([xi, xi], [0, wi], "-", color=BLACK, lw=0.7)
        m = w >= 0.01
        ax.plot(x[m], w[m], "o", mfc="white", mec=BLACK, mew=0.7, ms=2.6, zorder=3)
        k = np.argmin(np.abs(x - wr))
        ax.plot([x[k], x[k]], [0, w[k]], "-", color=MAROON, lw=1.4, zorder=4)
        ax.plot([x[k]], [w[k]], "o", color=MAROON, ms=3.4, zorder=5)
        ax.set_ylim(-0.12, 0.72)
        ax.set_yticks([0, 0.5])
        ax.set_yticklabels(["0", "0.5"])
        ax.set_xlim(-2.0, 3.0)
        ax.tick_params(axis="y", which="minor", left=False, right=False)
        ax.yaxis.set_label_position("right")
        ax.set_ylabel(lab, rotation=0, ha="left", va="center", labelpad=3)
    axs[-1].set_xticks([-2, -1, 0, 1, 2, 3])
    axs[-1].minorticks_on()
    for ax in axs:
        ax.tick_params(axis="y", which="minor", left=False, right=False)
    axs[-1].set_xlabel(r"$E_n(\Gamma) - E_{\mathrm{c}}$ (eV)")
    fig.supylabel(r"W 5d weight at $\Gamma$", fontsize=7.8, x=0.012)
    fig.tight_layout(pad=0.3, h_pad=0.25)
    fig.subplots_adjust(left=0.14, right=0.80)
    save(fig, "08_levels")


# ------------------------------------------------------------------------------------------------ bulk W bands near Gamma
def fig_bands():
    bg = bm.read_bands(bm.q.BULK / "bands_gamma.out")
    nop = int(bg["nelec"] / 2)
    fig, axs = plt.subplots(1, 2, figsize=(64 * MM, 40 * MM), sharey=True)
    for j, (site, job) in enumerate((("24d", "iwo_W24d"), ("8b", "iwo_W8b"))):   # same order as the slide table
        ax = axs[j]
        b = bm.read_bands(bm.q.RES / job / "bands.out")
        rec = b01["W_bulk"][site]
        ef = rec["E_F_eV"]["value"]
        cb = rec["host_CB_band"] - 1
        vb = rec["VB_top_band"] - 1
        lines = []
        for v, sgn in (((1, 1, 0), -1), ((1, 0, 0), 1)):     # [110] to the left of Gamma, [100] to the right
            idx = bm.line_indices(b["K"], v)
            lines.append((idx, sgn * np.linalg.norm(b["K"][idx], axis=1)))
        ax.axhline(0, color=BLACK, ls=":", lw=0.8)
        for n in range(max(0, vb - 25), b["nb"]):
            if n == cb:
                continue
            col = BLACK if n <= vb else GREY
            for idx, xx in lines:
                ax.plot(xx, b["E"][idx, n] - ef, color=col, lw=0.7)
        for v, sgn in (((1, 1, 0), -1), ((1, 0, 0), 1)):     # pure bulk CB shifted to the host-CB minimum
            idx = bm.line_indices(bg["K"], v)
            kk = sgn * np.linalg.norm(bg["K"][idx], axis=1)
            ax.plot(kk, bg["E"][idx, nop] - bg["E"][0, nop] + b["E"][0, cb] - ef, color=BLACK, lw=0.8,
                    ls=(0, (3, 2)), zorder=5)
        for idx, xx in lines:
            ax.plot(xx, b["E"][idx, cb] - ef, color=MAROON, lw=1.3, zorder=4)
        ax.axvline(0, color=LGREY, lw=0.5, zorder=0)
        ax.plot([0], [b["E"][0, cb] - ef], "o", color=MAROON, ms=3.6, zorder=7)
        ax.plot([0], [b["E"][0, vb] - ef], "o", mfc="white", mec=BLACK, mew=0.8, ms=3.6, zorder=7)
        ax.set_xticks([-0.15, 0, 0.15])
        tl = ax.set_xticklabels(["[110]", r"$\Gamma$", "[100]"])
        tl[0].set_ha("left")                                 # keep the direction labels inside their own panel
        tl[2].set_ha("right")
        ax.set_xlim(-0.155, 0.155)
        ax.set_ylim(-3.1, 1.0)
        ax.minorticks_on()
        ax.tick_params(axis="x", which="both", top=False)
        ax.tick_params(axis="x", which="minor", bottom=False)
        if j == 0:
            ax.set_ylabel(r"$E - E_{\mathrm{F}}$ (eV)")
        panel_label(ax, "(" + "ab"[j] + ")")
    fig.tight_layout(pad=0.3, w_pad=0.9)
    save(fig, "08_bands")


if __name__ == "__main__":
    fig_bonds()
    fig_levels()
    fig_bands()
