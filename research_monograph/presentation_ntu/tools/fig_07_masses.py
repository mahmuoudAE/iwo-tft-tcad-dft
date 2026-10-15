"""Figures for section 07 (electron and hole masses) of the NTU presentation.

Reads only repository data (no computed number is typed in; model parameters are the registered ones):
  qe_workflow/analysis_2026-10-13_full/bands_masses/out/b01_masses.json   bulk conduction band near Gamma along [100],
      [110], [111] (bands_gamma.out), anchored-parabola masses per window, four-point deck-basis mass, slab in-plane
      band-edge 2-D DOS masses and t_HH, bulk valence bands 174-176 near Gamma, W bulk host-band mass
  qe_workflow/analysis_2026-10-13_full/bands_masses/out/b03_gaps_laws.json   fitted mass law dm_e_band_edge fit3
  qe_workflow/analysis_2026-10-13_full/bands_masses/out/b05_holes.json      off-Gamma valence maxima, N_V by grid and
      reference, HSE06 on the k3 grid, deck N_V = 1e19 cm^-3 and its implied mass
  research_monograph/evidence/derived/confinement_analysis.json             no-fit Kane prediction m_b(1 + 2 alpha dEc)
      (value and alpha range), predicted in-plane non-parabolicity, computed alpha_par
Model parameters (monograph M05/M09; FACT-004, FACT-005): m_b = 0.1541 m0, alpha = 0.58 1/eV.

Writes presentation_ntu/figures/07_bulk_cb.pdf, 07_film_masses.pdf, 07_kanetest.pdf, 07_holes.pdf.
Run from anywhere:  python3 -I research_monograph/presentation_ntu/tools/fig_07_masses.py
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, NullFormatter

HERE = pathlib.Path(__file__).resolve().parent
PRES = HERE.parent
ROOT = PRES.parents[1]
OUT = PRES / "figures"
BM = ROOT / "qe_workflow" / "analysis_2026-10-13_full" / "bands_masses" / "out"
CA = ROOT / "research_monograph" / "evidence" / "derived" / "confinement_analysis.json"

HB2M = 3.80998        # hbar^2 / (2 m0) in eV A^2 (as in research_monograph/tools/confinement_analysis.py)
MM = 1 / 25.4
BLACK, GREY, LGREY, MAROON = "#000000", "#7a7a7a", "#c8c8c8", "#801924"

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

b01 = json.loads((BM / "b01_masses.json").read_text())
b03 = json.loads((BM / "b03_gaps_laws.json").read_text())
b05 = json.loads((BM / "b05_holes.json").read_text())
ca = json.loads(CA.read_text())
MB = ca["inputs"]["m_b"]          # 0.1541
ALPHA = ca["inputs"]["alpha"]     # 0.58
DIRS = ["[100]", "[110]", "[111]"]
DMARK = {"[100]": "o", "[110]": "s", "[111]": "^"}


def save(fig, stem):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f"{stem}.pdf")
    plt.close(fig)
    print("saved", OUT / f"{stem}.pdf")


def panel_label(ax, s):
    ax.text(-0.02, 1.02, s, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, fontweight="bold")


# ------------------------------------------------------------------------------------------------ bulk conduction band
def fig_bulk_cb():
    el = b01["bulk"]["electron"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(68 * MM, 37 * MM))
    # (a) dispersion: computed points along three directions, Kane band and parabola with the same band-edge mass
    k = np.linspace(0, 0.158, 200)
    eps = HB2M * k ** 2 / MB                                     # eV
    ekane = (-1 + np.sqrt(1 + 4 * ALPHA * eps)) / (2 * ALPHA)
    ax1.plot(k, 1e3 * eps, "--", color=GREY, lw=0.9, label="parabola")
    ax1.plot(k, 1e3 * ekane, "-", color=BLACK, lw=1.0, label="Kane")
    for d in DIRS:
        ax1.plot(el[d]["k_invA"], el[d]["dE_meV"], DMARK[d], mfc="white", mec=BLACK, mew=0.7, ms=3.4, label=d)
    ax1.set_xlim(0, 0.16)
    ax1.set_ylim(0, 520)
    ax1.set_xticks([0, 0.05, 0.10, 0.15])
    ax1.set_xticklabels(["0", "0.05", "0.10", "0.15"])
    ax1.set_xlabel(r"$|k|$ (1/$\mathrm{\AA}$)")
    ax1.set_ylabel(r"$E - E_{\mathrm{c}}$ (meV)")
    ax1.minorticks_on()
    ax1.legend(loc="upper left", handlelength=1.6, labelspacing=0.2, borderaxespad=0.3, handletextpad=0.5)
    panel_label(ax1, "(a)")
    # (b) anchored parabola mass against the energy window; dashed: Kane band-edge mass; diamond: four-point deck basis
    ax2.axhline(MB, color=BLACK, ls="--", lw=0.8)
    for d in DIRS:
        w = el[d]["windows"]
        keys = sorted(w, key=lambda s: int(s))
        ax2.plot([w[q]["Emax_meV"] for q in keys], [w[q]["m_anchored"] for q in keys], DMARK[d] + "-", color=GREY,
                 mfc="white", mec=BLACK, mew=0.7, ms=3.4, lw=0.6)
    deck = b01["bulk"]["electron_summary"]["m_parabolic_4pt_intercept_by_dir"]["[100]"]
    deck_E = el["[100]"]["windows"]["3"]["Emax_meV"]            # four points incl. Gamma: window "3"
    ax2.plot(deck_E, deck, "D", color=MAROON, ms=3.6)
    ax2.set_xlim(0, 500)
    ax2.set_xticks([0, 200, 400])
    ax2.minorticks_on()
    ax2.set_ylim(0.150, 0.215)
    ax2.set_yticks([0.15, 0.17, 0.19, 0.21])
    ax2.set_xlabel("fit window (meV)")
    ax2.set_ylabel(r"mass ($m_0$)")
    h = [Line2D([], [], color=GREY, marker="o", mfc="white", mec=BLACK, mew=0.7, ms=3.4, lw=0.6),
         Line2D([], [], color=MAROON, marker="D", ls="none", ms=3.6),
         Line2D([], [], color=BLACK, ls="--", lw=0.8)]
    ax2.legend(h, ["anchored fit", "deck basis", "Kane edge"], loc="upper left",
               handlelength=1.6, labelspacing=0.2, borderaxespad=0.3, handletextpad=0.5)
    panel_label(ax2, "(b)")
    fig.tight_layout(pad=0.3, w_pad=0.8)
    save(fig, "07_bulk_cb")


# ------------------------------------------------------------------------------------------------ film masses
def fig_film_masses():
    keys = ["0.51", "0.75", "1.0", "2.0"]
    S = [b01["slabs"][q] for q in keys]
    t = np.array([s["t_HH_nm"] for s in S])
    m = np.array([s["electron_summary"]["tensor_2d"]["m_dos_2d"] for s in S])
    law = b03["laws"]["dm_e_band_edge"]["fit3"]
    mbulk = b03["laws"]["dm_e_band_edge"]["m_bulk"]
    mw = b01["W_bulk"]["8b"]["electron_summary"]["m_dos"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(68 * MM, 37 * MM))
    # (a) in-plane band-edge mass
    tt = np.linspace(0.62, 2.2, 100)
    ax1.axhline(mbulk, color=BLACK, ls="--", lw=0.8)
    ax1.axhline(mw, color=MAROON, ls="-", lw=0.9)
    ax1.plot(tt, mbulk + law["a"] * tt ** (-law["p"]), "-", color=GREY, lw=0.9)
    ax1.plot(t[1:], m[1:], "o", color=BLACK)
    ax1.plot(t[0], m[0], "o", mfc="white", mec=BLACK, mew=0.8)
    # direct labels (no legend): the two bulk references are 0.008 m0 apart, so one label sits above, one below
    # (x = 0.40: clear of the inward y-axis ticks; the W label sits low enough to stay clear of the 0.2 tick)
    lab = dict(fontsize=6.6, ha="left")
    ax1.text(0.40, mw + 0.006, "bulk, 3.1 % W", color=MAROON, va="bottom", **lab)
    ax1.text(0.40, mbulk - 0.008, "bulk", color=BLACK, va="top", **lab)
    ax1.text(1.08, mbulk + law["a"] * 1.08 ** (-law["p"]) + 0.012, "bulk + law", color=GREY, ha="left", va="bottom",
             fontsize=6.6)
    ax1.text(t[0] + 0.07, m[0], r"In$_8$(OH)$_{24}$", ha="left", va="center", fontsize=6.6)
    ax1.set_xlim(0.3, 2.2)
    ax1.set_ylim(0.10, 0.48)
    ax1.set_xlabel(r"$t_{\mathrm{HH}}$ (nm)")
    ax1.set_ylabel(r"in-plane mass $m_\parallel$ ($m_0$)")
    ax1.minorticks_on()
    panel_label(ax1, "(a)")
    # (b) increase over bulk, log-log, with the fitted law and its extrapolation to the device thicknesses
    for xd, yd in ((6.3, 0.30), (13.2, 0.11)):
        ax2.axvline(xd, color=GREY, ls=":", lw=0.9)
        ax2.text(xd, yd, f"{xd:g}", color=GREY, ha="center", va="center", fontsize=6.6,
                 bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
    t_in = np.geomspace(t[1], t[3], 50)
    t_ex = np.geomspace(t[3], 15, 50)
    ax2.loglog(t_in, law["a"] * t_in ** (-law["p"]), "-", color=BLACK, lw=1.0)
    ax2.loglog(t_ex, law["a"] * t_ex ** (-law["p"]), "--", color=BLACK, lw=0.9)
    ax2.loglog(t[1:], m[1:] - mbulk, "o", color=BLACK)
    ax2.loglog(t[0], m[0] - mbulk, "o", mfc="white", mec=BLACK, mew=0.8)
    ax2.xaxis.set_major_locator(FixedLocator([0.5, 1, 2, 5, 10]))
    ax2.set_xticklabels(["0.5", "1", "2", "5", "10"])
    ax2.xaxis.set_minor_formatter(NullFormatter())
    ax2.set_xlim(0.4, 20)
    ax2.set_ylim(2e-3, 0.5)
    ax2.set_xlabel(r"$t_{\mathrm{HH}}$ (nm)")
    ax2.set_ylabel(r"$\Delta m = m_\parallel - m_b$ ($m_0$)")
    panel_label(ax2, "(b)")
    fig.tight_layout(pad=0.3, w_pad=0.8)
    save(fig, "07_film_masses")


# ------------------------------------------------------------------------------------------------ no-fit Kane test
def fig_kanetest():
    keys = ["0.461", "0.695", "0.930", "1.962"]
    sl = [ca["slabs"][q] for q in keys]
    t = np.array([float(q) for q in keys])
    mc = np.array([s["computed"]["m"] for s in sl])
    mp = np.array([s["m_par_pred"] for s in sl])
    lo = np.array([s["m_par_pred_range"][0] for s in sl])
    hi = np.array([s["m_par_pred_range"][1] for s in sl])
    dev = 100 * (mp / mc - 1)
    dlo, dhi = 100 * (lo / mc - 1), 100 * (hi / mc - 1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(68 * MM, 37 * MM))
    # (a) deviation of the prediction from the computed mass; bars: alpha = 0.55-0.63; maroon bar at 0.695 nm: the
    # +-0.17 eV reference sensitivity of the polar film propagated through m_b(1 + 2 alpha dEc)
    ax1.axhline(0, color=BLACK, lw=0.6)
    h = 0.17
    dec = sl[1]["computed"]["dEc"]
    pol = [100 * (MB * (1 + 2 * ALPHA * (dec + s * h)) / mc[1] - 1) for s in (-1, 1)]
    ax1.plot([t[1]] * 2, pol, "-", color=MAROON, lw=4.0, alpha=0.30, solid_capstyle="butt", zorder=1,
             label=r"$\pm$0.17 eV")
    ax1.errorbar(t, dev, yerr=[dev - dlo, dhi - dev], fmt="none", ecolor=BLACK, elinewidth=0.8, capsize=2.0, zorder=2)
    ax1.plot(t[2:], dev[2:], "o", color=BLACK, label="test", zorder=3)
    ax1.plot(t[:2], dev[:2], "o", mfc="white", mec=BLACK, mew=0.8, label="no test", zorder=3)
    ax1.set_xlim(0.3, 2.2)
    ax1.set_ylim(-16, 19)
    ax1.set_yticks([-10, 0, 10])
    ax1.set_xlabel(r"$t_{\mathrm{HH}}$ (nm)")
    ax1.set_ylabel(r"$m_{\mathrm{Kane}}/m_{\mathrm{comp}} - 1$ (%)")
    ax1.minorticks_on()
    hl, ll = ax1.get_legend_handles_labels()
    ax1.legend([hl[1], hl[2], hl[0]], [ll[1], ll[2], ll[0]], loc="lower right", handlelength=1.0, labelspacing=0.2,
               borderaxespad=0.3, handletextpad=0.4)
    panel_label(ax1, "(a)")
    # (b) in-plane non-parabolicity: computed against alpha / (1 + 2 alpha dEc)
    ac = np.array([s["computed"]["a"] for s in sl])
    ap = np.array([s["alpha_par_pred"] for s in sl])
    ax2.axhline(ALPHA, color=BLACK, ls="--", lw=0.8, label="bulk")
    ax2.plot(t, ac, "o", color=BLACK, label="computed")
    ax2.plot(t, ap, "s", mfc="white", mec=BLACK, mew=0.8, label="predicted")
    ax2.set_xlim(0.3, 2.2)
    ax2.set_ylim(0, 0.65)
    ax2.set_xlabel(r"$t_{\mathrm{HH}}$ (nm)")
    ax2.set_ylabel(r"$\alpha_\parallel$ (eV$^{-1}$)")
    ax2.minorticks_on()
    ax2.legend(loc="lower right", handlelength=1.2, labelspacing=0.2, borderaxespad=0.3, handletextpad=0.4)
    panel_label(ax2, "(b)")
    fig.tight_layout(pad=0.3, w_pad=0.8)
    save(fig, "07_kanetest")


# ------------------------------------------------------------------------------------------------ holes
def fig_holes():
    bands = b05["bulk"]["bands"]
    ls = {"[100]": "-", "[110]": "--", "[111]": ":"}
    col = {"174": BLACK, "175": GREY, "176": MAROON}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(68 * MM, 38 * MM), gridspec_kw={"width_ratios": [1.08, 1]})
    # (a) valence bands near Gamma (energy relative to the triply degenerate VB at Gamma; up = higher electron energy)
    for b in ("174", "175", "176"):
        for dname, d in bands[b]["directions"].items():
            dd = dname.split()[0]
            k = np.array(d["k_invA"])
            e = -np.array(d["dE_meV_hole_convention"])
            ax1.plot(k, e, ls[dd], color=col[b], lw=1.0)
    om = b05["bulk"]["offgamma_maxima"]
    ax1.plot(om["[100] (G-H)"]["k0_invA"], om["[100] (G-H)"]["E0_minus_Gamma_meV"], "o", mfc="white", mec=BLACK,
             mew=0.9, ms=4.4)
    ax1.axhline(0, color=LGREY, lw=0.5, zorder=0)
    # band numbers at the [100] curve ends (175: the three directions end within 2.2 meV of each other)
    kend = bands["174"]["directions"]["[100] (G-H)"]["k_invA"][-1]
    for b, dy in (("174", 0.0), ("175", 1.0), ("176", 0.0)):
        e_end = -bands[b]["directions"]["[100] (G-H)"]["dE_meV_hole_convention"][-1]
        ax1.text(kend + 0.013, e_end + dy, b, color=col[b], ha="left", va="center", fontsize=6.6)
    ax1.set_xlim(0, 0.19)
    ax1.set_ylim(-30, 8)
    ax1.set_xticks([0, 0.05, 0.10, 0.15])
    ax1.set_xticklabels(["0", "0.05", "0.10", "0.15"])
    ax1.set_xlabel(r"$|k|$ (1/$\mathrm{\AA}$)")
    ax1.set_ylabel(r"$E - E_{\mathrm{v}}(\Gamma)$ (meV)")
    ax1.minorticks_on()
    h = [Line2D([], [], color=BLACK, ls="-"), Line2D([], [], color=BLACK, ls="--"), Line2D([], [], color=BLACK, ls=":")]
    ax1.legend(h, DIRS, loc="lower left", handlelength=1.8, labelspacing=0.2, borderaxespad=0.3, handletextpad=0.5)
    panel_label(ax1, "(a)")
    # (b) N_V(300 K) from the Boltzmann-integrated valence DOS, four grids, two VBM references; dashed: deck value
    g = b05["bulk_Nv"]["grids"]
    names = list(g)                                    # b05 order: prim_k3, prim_k4 (exp. lattice), 80-atom k3, k4
    short = ["4", "8*", "6", "14"]                     # irreducible k points of each grid (b05 grid names)
    for i, n in enumerate(names):
        own, off = g[n][0]["by_window_eV"]["all"]["Nv_cm3"], g[n][1]["by_window_eV"]["all"]["Nv_cm3"]
        ax2.plot(i - 0.13, own, "o", color=BLACK)
        ax2.plot(i + 0.13, off, "s", mfc="white", mec=BLACK, mew=0.8)
    deck = b05["bulk_Nv"]["deck_NV300_cm3"]
    ax2.axhline(deck, color=MAROON, ls="--", lw=0.9)
    ax2.set_yscale("log")
    ax2.set_ylim(3e18, 6e21)
    ax2.set_xlim(-0.6, len(names) - 0.4)
    ax2.set_xticks(range(len(names)))
    ax2.set_xticklabels(short, fontsize=7.0)
    ax2.tick_params(axis="x", which="both", top=False, bottom=False)
    for x0, txt in ((0.5, "40"), (2.5, "80")):                  # atoms per cell, one label per pair of grids
        ax2.text(x0, -0.16, txt, transform=ax2.get_xaxis_transform(), ha="center", va="top", fontsize=7.0)
    ax2.set_ylabel(r"$N_{\mathrm{V}}$ at 300 K (cm$^{-3}$)")
    ax2.set_xlabel(r"$k$ points; atoms", labelpad=10.5)
    hh = [Line2D([], [], color=BLACK, marker="o", ls="none"),
          Line2D([], [], marker="s", mfc="white", mec=BLACK, mew=0.8, ls="none"),
          Line2D([], [], color=MAROON, ls="--", lw=0.9)]
    ax2.legend(hh, ["grid max.", r"off-$\Gamma$ VBM", "deck"], loc="center left", bbox_to_anchor=(0.0, 0.42),
               handlelength=1.1, labelspacing=0.2, borderaxespad=0.3, handletextpad=0.4)
    panel_label(ax2, "(b)")
    fig.tight_layout(pad=0.3, w_pad=0.8)
    save(fig, "07_holes")


if __name__ == "__main__":
    fig_bulk_cb()
    fig_film_masses()
    fig_kanetest()
    fig_holes()
