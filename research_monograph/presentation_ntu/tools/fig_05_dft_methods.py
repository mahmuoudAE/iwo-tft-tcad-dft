"""Figures for section 05 (first-principles methods) of the NTU presentation.

Reads only repository data (no numbers are typed in except analytic definitions and registered criteria):
  qe_workflow/analysis_2026-10-13_full/out/f01_bulk_convergence.json   stage-1 convergence runs (raw-output pointers)
  qe_workflow/analysis_2026-10-13_full/out/f03_bulk_alignment.json     two-step alignment constants of the 2 nm slab
  qe_workflow/cern_htcondor/results/slab2_relax_c2/slab2_relax_c2_avg.dat   planar average (pp.x plot_num 11, average.x)
  qe_workflow/cern_htcondor/results/iwo_W8b/scf_k4.out                 occupations printed by pw.x (bulk W cell, MV 0.01 Ry)
Registered criteria (13_dft_rev.tex tab:dft-criteria): 1 mRy/atom, 1 kbar, 10 meV.
Smearing functions: Gaussian 1/2 erfc(x); Marzari-Vanderbilt in the form Quantum ESPRESSO applies (wgauss, ngauss = -1),
checked against the occupations printed by pw.x. Monograph eq. mono-dft-mv (M04_dft_theory.tex) is the mirror image
1 - f(-x) of this function and does not reproduce the printed occupations (flagged for an erratum).

Writes presentation_ntu/figures/05_convergence.pdf, 05_smearing.pdf, 05_alignment.pdf.
Run from anywhere:  python3 -I research_monograph/presentation_ntu/tools/fig_05_dft_methods.py
"""
import json
import math
import pathlib
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import erfc

HERE = pathlib.Path(__file__).resolve().parent
PRES = HERE.parent
ROOT = PRES.parents[1]
OUT = PRES / "figures"
QA = ROOT / "qe_workflow" / "analysis_2026-10-13_full" / "out"
AVG = ROOT / "qe_workflow" / "cern_htcondor" / "results" / "slab2_relax_c2" / "slab2_relax_c2_avg.dat"
W8B = ROOT / "qe_workflow" / "cern_htcondor" / "results" / "iwo_W8b" / "scf_k4.out"   # bulk W cell, MV 0.01 Ry

RY = 13.605693122994          # eV (as in qe_workflow/analysis_2026-10-13_full/qeio.py)
BOHR = 0.529177210903         # angstrom
A_BULK = 10.30609             # relaxed bulk lattice constant, FACT-001 (sets the a/2 averaging window)
MM = 1 / 25.4
BLACK, GREY, LGREY, MAROON = "#000000", "#7a7a7a", "#c8c8c8", "#801924"

plt.rcParams.update({
    "font.family": "Liberation Sans",
    "mathtext.fontset": "custom",
    "mathtext.rm": "Liberation Sans",
    "mathtext.it": "Liberation Sans:italic",
    "mathtext.bf": "Liberation Sans:bold",
    "font.size": 7.5,
    "axes.labelsize": 7.5,
    "xtick.labelsize": 6.8,
    "ytick.labelsize": 6.8,
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
    "pdf.fonttype": 42,
})


def panel_label(ax, s):
    ax.text(0.0, 1.03, s, transform=ax.transAxes, fontsize=7.5, fontweight="bold", va="bottom", ha="left")


# ------------------------------------------------------------------------------------------------ convergence
def fig_convergence():
    d = json.loads((QA / "f01_bulk_convergence.json").read_text())
    ec = [r for r in d["runs"] if r["kind"] == "ecut"]
    kk = [r for r in d["runs"] if r["kind"] == "k"]
    qty = [("dE_mRy_per_atom", "$\\Delta E$\n(mRy/atom)", 1.0, (-1.7, 3.7), [0, 2]),
           ("dP_kbar", "$\\Delta P$\n(kbar)", 1.0, (-14.5, 3.0), [-10, 0]),
           ("dgap_meV", "$\\Delta E_\\mathrm{g}$\n(meV)", 10.0, (-13.0, 13.0), [-10, 0, 10])]
    cols = ((ec, r"$E_\mathrm{cut}$ (Ry)", [50, 60, 71, 85], 71),
            (kk, r"$k$ grid $n\times n\times n$", [2, 3, 4], 3))
    fig, axs = plt.subplots(3, 2, figsize=(74 * MM, 56 * MM), sharey="row")
    for col, (runs, xlab, xt, sel) in enumerate(cols):
        x = np.array([r["x"] for r in runs], float)
        pad = 0.08 * (x.max() - x.min())
        for row, (key, ylab, crit, ylim, yt) in enumerate(qty):
            ax = axs[row, col]
            y = np.array([r[key] for r in runs], float)
            ax.axhspan(-crit, crit, color="#ececec", lw=0, zorder=0)
            ax.axhline(0, color=GREY, lw=0.4, zorder=1)
            ax.axvline(sel, color=MAROON, lw=0.7, ls=":", zorder=1)
            ax.plot(x, y, color=BLACK, lw=0.9, marker="o", ms=3.0, mfc="white", mec=BLACK, mew=0.8, zorder=3)
            ax.set_xticks(xt)
            ax.set_yticks(yt)
            ax.set_ylim(*ylim)
            ax.set_xlim(x.min() - pad, x.max() + pad)
            if row < 2:
                ax.tick_params(labelbottom=False)
            else:
                ax.set_xlabel(xlab, labelpad=1.5)
            if col == 0:
                ax.set_ylabel(ylab, labelpad=2.0, linespacing=1.0)
            ax.tick_params(pad=1.5)
    for ax, s in zip(axs.flat, "abcdef"):
        panel_label(ax, f"({s})")
    fig.subplots_adjust(left=0.165, right=0.975, bottom=0.11, top=0.935, wspace=0.16, hspace=0.36)
    fig.savefig(OUT / "05_convergence.pdf")
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ smearing
def mv_weight(x):
    """Marzari-Vanderbilt weight as Quantum ESPRESSO applies it (wgauss, ngauss = -1), written in x = (eps - mu)/sigma.

    QE uses xq = (mu - eps)/sigma and f = 1/2 erf(xq - 1/sqrt2) + exp(-(xq - 1/sqrt2)^2)/sqrt(2 pi) + 1/2; with u = x + 1/sqrt2
    this is f = 1/2 erfc(u) + exp(-u^2)/sqrt(2 pi). It reproduces every occupation printed by pw.x in the W cells
    (checked on iwo_W8b/scf_k4.out and iwo_slab1_final_cpu/scf.out to 3e-4). Note: monograph eq. mono-dft-mv
    (M04_dft_theory.tex) prints the mirror image 1 - f(-x); it does not reproduce the printed occupations.
    """
    u = np.asarray(x, float) + 1 / math.sqrt(2)
    return 0.5 * erfc(u) + np.exp(-u ** 2) / math.sqrt(2 * math.pi)


def printed_occupations(path):
    """(x, f) of every fractional or above-one occupation of the final SCF block of a pw.x output."""
    txt = path.read_text()
    ef = float(re.findall(r"the Fermi energy is\s+([-\d.]+)", txt)[-1])
    sig = float(re.search(r"width \(Ry\)=\s+([\d.]+)", txt).group(1)) * RY
    blk = txt[txt.rfind("End of self-consistent calculation"):]
    out = []
    for part in re.split(r"\n\s+k =", blk)[1:]:
        if "occupation numbers" not in part:
            continue
        a, b = part.split("occupation numbers")
        ev = [float(v) for v in re.findall(r"-?\d+\.\d+", a.split("\n", 1)[1])]
        oc = [float(v) for v in re.findall(r"-?\d+\.\d+", b.split("the Fermi")[0])][:len(ev)]
        out += [((e - ef) / sig, o) for e, o in zip(ev, oc) if 5e-5 < o < 0.99995 or o > 1.00005 or o < -5e-5]
    return np.array(out), ef, sig


def fig_smearing():
    x = np.linspace(-3.0, 3.0, 1201)
    gauss = 0.5 * erfc(x)
    mv = mv_weight(x)
    occ, ef, sig = printed_occupations(W8B)
    fig, ax = plt.subplots(figsize=(64 * MM, 37 * MM))
    ax.axhline(0, color=GREY, lw=0.5)
    ax.axhline(1, color=LGREY, lw=0.5)
    ax.axvline(0, color=LGREY, lw=0.5)
    ax.plot(x, gauss, color=BLACK, lw=1.1, label="Gaussian")
    ax.plot(x, mv, color=MAROON, lw=1.3, ls="--", label="MV")
    ax.plot(occ[:, 0], occ[:, 1], ls="none", marker="o", ms=2.2, mfc=GREY, mec="none", zorder=5,
            label="pw.x, W cell")
    # characteristic points of the MV weight: f(0); f = 1 crossing; maximum at x = -sqrt2
    xc = x[(x > -1.3) & (x < -0.5)][np.argmin(np.abs(mv[(x > -1.3) & (x < -0.5)] - 1.0))]
    xm = -math.sqrt(2)
    for xx in (0.0, xc, xm):
        ax.plot([xx], [float(mv_weight(xx))], marker="o", ms=3.4, mfc="white", mec=MAROON, mew=0.9, zorder=6)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-0.08, 1.16)
    ax.set_xticks([-3, -2, -1, 0, 1, 2, 3])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel(r"$x = (\varepsilon - \mu)/\sigma$")
    ax.set_ylabel(r"weight $f(x)$")
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, 0.80), handlelength=2.0, borderaxespad=0.3, labelspacing=0.3,
              markerscale=1.6)
    fig.subplots_adjust(left=0.165, right=0.975, bottom=0.215, top=0.975)
    fig.savefig(OUT / "05_smearing.pdf")
    plt.close(fig)
    return dict(f0=float(mv_weight(0.0)), x_cross1=float(xc), fmax=float(mv_weight(xm)), x_max=xm,
                max_eV_below_mu=math.sqrt(2) * 0.01 * RY, n_printed=len(occ), printed_max=float(occ[:, 1].max()),
                printed_min=float(occ[:, 1].min()),
                max_dev=float(np.abs(mv_weight(occ[:, 0]) - occ[:, 1]).max()), ef=ef, sigma_eV=sig)


# ------------------------------------------------------------------------------------------------ alignment
def fig_alignment():
    al = json.loads((QA / "f03_bulk_alignment.json").read_text())
    ts = al["two_step"]["slab2_relax_c2"]
    bulk = al["bulk"]
    a = np.loadtxt(AVG)
    z, vp = a[:, 0], a[:, 1]                      # bohr, Ry
    zc = ts["centre_z_A"] / BOHR
    # macroscopic average over a/2 (periodic running mean, as qeio.macro)
    dz = z[1] - z[0]
    n = max(1, int(round(A_BULK / 2 / BOHR / dz)))
    ext = np.concatenate([vp[-n:], vp, vp[:n]])
    vm = np.convolve(ext, np.ones(n) / n, mode="same")[n:-n]
    L = z[-1] + dz
    # vacuum level: planar average half a cell away from the slab centre
    zf = (zc + L / 2) % L
    evac = float(np.interp(zf, z, vp)) * RY
    zz = ((z - zc + L / 2) % L - L / 2) * BOHR    # angstrom, centred on the slab
    o = np.argsort(zz)
    vbar_c = ts["a/2"]["Vbar_centre_eV"]
    cbm, vbm = ts["CBM_eV"]["value"], ts["VBM_eV"]["value"]
    ec_al = vbar_c + bulk["Ec_minus_V_eV"]
    ev_al = vbar_c + bulk["Ev_minus_V_eV"]
    # drawn at its display size on the slide (0.42 of the text width, about 60 mm), so fonts are not scaled down
    fig = plt.figure(figsize=(60 * MM, 38 * MM))
    gs = fig.add_gridspec(2, 2, width_ratios=[2.9, 1.0], height_ratios=[1, 1], left=0.155, right=0.86,
                          bottom=0.20, top=0.705, wspace=0.10, hspace=0.20)
    ax = fig.add_subplot(gs[:, 0])
    ax.plot(zz[o], vp[o] * RY - evac, color=LGREY, lw=0.6, label=r"planar $\bar V$")
    ax.plot(zz[o], vm[o] * RY - evac, color=BLACK, lw=1.1, label=r"macroscopic $\bar{\bar{V}}$ ($a/2$)")
    w = 5.2
    ax.plot([-w, w], [cbm - evac] * 2, color=MAROON, lw=1.2, label="slab CBM, VBM")
    ax.plot([-w, w], [vbm - evac] * 2, color=MAROON, lw=1.2)
    ax.plot([-w, w], [ec_al - evac] * 2, color=MAROON, lw=1.0, ls=(0, (2.2, 1.4)), label="bulk edges aligned")
    ax.plot([-w, w], [ev_al - evac] * 2, color=MAROON, lw=1.0, ls=(0, (2.2, 1.4)))
    ax.set_xlim(-22.6, 22.6)
    ax.set_ylim(-14.5, 1.5)
    ax.set_xticks([-20, -10, 0, 10, 20])
    ax.set_yticks([-10, -5, 0])
    ax.set_xlabel(r"$z - z_\mathrm{centre}$ ($\mathrm{\AA}$)")
    ax.set_ylabel(r"energy $-\ E_\mathrm{vac}$ (eV)")
    panel_label(ax, "(a)")
    # (b): the four edges magnified (same 0.47 eV span in both windows), arrows from aligned bulk edge to slab edge
    span = 0.47
    wins = ((gs[0, 1], cbm - evac, ec_al - evac, r"$\Delta E_\mathrm{c}$", (-4.8, -4.6, -4.4)),
            (gs[1, 1], vbm - evac, ev_al - evac, r"$\Delta E_\mathrm{v}$", (-5.8, -5.6)))
    for k, (g, ys, yb, lab, yt) in enumerate(wins):
        bx = fig.add_subplot(g)
        mid = 0.5 * (ys + yb)
        bx.set_ylim(mid - span / 2, mid + span / 2)
        bx.set_xlim(0, 1)
        bx.plot([0.08, 0.92], [ys] * 2, color=MAROON, lw=1.2)
        bx.plot([0.08, 0.92], [yb] * 2, color=MAROON, lw=1.0, ls=(0, (2.2, 1.4)))
        bx.annotate("", xy=(0.30, ys), xytext=(0.30, yb),
                    arrowprops=dict(arrowstyle="-|>", color=BLACK, lw=0.7, mutation_scale=6, shrinkA=0, shrinkB=0))
        # label beside a long arrow; below the pair when the two lines are too close for text between them
        ylab = mid if abs(ys - yb) > 0.15 else min(ys, yb) - 0.115
        bx.text(0.40, ylab, lab, ha="left", va="center", fontsize=6.8)
        bx.set_xticks([])
        bx.set_yticks(yt)
        bx.yaxis.tick_right()
        bx.tick_params(axis="y", pad=1.5, right=True, left=True)
        if k == 0:
            panel_label(bx, "(b)")
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, handlelength=1.8, columnspacing=0.8, labelspacing=0.25,
               handletextpad=0.5, bbox_to_anchor=(0.5, 1.0), borderaxespad=0.2)
    fig.savefig(OUT / "05_alignment.pdf")
    plt.close(fig)
    return dict(evac=evac, EA=evac - cbm, IP=evac - vbm, dEc=cbm - ec_al, dEv=vbm - ev_al,
                plateau_meV=ts["a/2"]["plateau_spread_meV"], cell_A=L * BOHR)


def main():
    OUT.mkdir(exist_ok=True)
    fig_convergence()
    sm = fig_smearing()
    info = fig_alignment()
    print("MV weight check:", {k: round(v, 4) for k, v in sm.items()})
    print("alignment check:", {k: round(v, 4) for k, v in info.items()})
    print("wrote", sorted(p.name for p in OUT.glob("05_*.pdf")))


if __name__ == "__main__":
    main()
