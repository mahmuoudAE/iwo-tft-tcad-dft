"""Figures for section 06 (quantum confinement of crystalline In2O3 films) of the NTU presentation.

Reads only repository data (no computed number is typed in; model parameters are the registered ones):
  qe_workflow/analysis_2026-10-13_full/bands_masses/out/b03_gaps_laws.json   slab gaps, EA/IP, dEc/dEv, levels at
      Gamma (E1, E2), fitted thickness laws (fit3 / fit2), bulk-equivalent edges, half-ramp sensitivity (0.695 nm)
  research_monograph/evidence/derived/confinement_analysis.json             computed dEc of the four films
  tables/THICKNESS_LAW_EVIDENCE.csv                                         PBE gaps of Lin et al. (2022), p. 21542
Model parameters (monograph M05_confinement_theory.tex; FACT-004, FACT-005): bulk band-edge mass m_b = 0.1541 m0,
Kane alpha = 0.58 1/eV, box factor t_eff = 1.392 t (fixed at 2 nm, confinement_analysis.json), finite barrier 4 eV
with the free-electron mass outside and continuity of F'/m (M05, correction V4; reproduces 0.25 / 0.63 eV).
Subband spacing: Kane band with the fit2 dEc law (M05 sec. "When is a film two-dimensional?"; reproduces 0.59 / 0.14 /
0.05 eV and 0.088 / 0.021 eV).

Light grey band in 06_laws / 06_subbands: thicknesses beyond the thickest computed film (1.962 nm), i.e. extrapolation.
"frozen C10" = the dEc fit3 law frozen for campaign C10 (the monograph's "V3/C10" law).

Writes presentation_ntu/figures/06_edges.pdf, 06_gaps.pdf, 06_laws.pdf, 06_models.pdf, 06_subbands.pdf.
Run from anywhere:  python3 -I research_monograph/presentation_ntu/tools/fig_06_confinement.py
"""
import csv
import json
import math
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator, NullFormatter, NullLocator
from scipy.optimize import brentq

HERE = pathlib.Path(__file__).resolve().parent
PRES = HERE.parent
ROOT = PRES.parents[1]
OUT = PRES / "figures"
B03 = ROOT / "qe_workflow" / "analysis_2026-10-13_full" / "bands_masses" / "out" / "b03_gaps_laws.json"
CA = ROOT / "research_monograph" / "evidence" / "derived" / "confinement_analysis.json"
LIN = ROOT / "tables" / "THICKNESS_LAW_EVIDENCE.csv"

HB2M = 3.80998        # hbar^2 / (2 m0) in eV A^2 (as in research_monograph/tools/confinement_analysis.py)
KT = 0.025852         # eV at 300 K (as in confinement_analysis.py)
MB, ALPHA = 0.1541, 0.58
BOX = 1.392           # t_eff / t_HH at 1.962 nm (confinement_analysis.json, slabs.1.962.t_eff_over_tHH)
V0 = 4.0              # barrier height of the finite-well check (M05: about the electron affinity)
MM = 1 / 25.4
BLACK, GREY, LGREY, MAROON = "#000000", "#7a7a7a", "#c8c8c8", "#801924"
SHADE = "#efefef"     # light grey band: thicknesses beyond the thickest computed film (1.962 nm), i.e. extrapolation

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
    "legend.fontsize": 6.6,
    "lines.linewidth": 1.1,
    "lines.markersize": 4.5,
    "pdf.fonttype": 42,
})

b03 = json.loads(B03.read_text())
ca = json.loads(CA.read_text())
LABS = ["0.51", "0.75", "1.0", "2.0"]                      # b03 keys, thinnest first
S = [b03["slabs"][k] for k in LABS]
T = [s["t_HH_nm"] for s in S]                             # 0.4612, 0.6953, 0.9303, 1.9623
EG_BULK = b03["bulk"]["Eg_fundamental_eV"]


def law(fit, t):
    return fit["a"] * np.asarray(t, float) ** (-fit["p"])


def ekane(eps, alpha=ALPHA):
    """E solving E (1 + alpha E) = eps."""
    return (-1.0 + np.sqrt(1.0 + 4.0 * alpha * np.asarray(eps, float))) / (2.0 * alpha)


def eps_box(t_nm, n=1):
    """parabolic infinite-well energy (eV) with the bulk band-edge mass, width t (nm)."""
    return HB2M * (n * math.pi / (np.asarray(t_nm, float) * 10.0)) ** 2 / MB


def e_finite(t_nm):
    """lowest even level of a finite well: m_b inside, m0 outside, barrier V0, continuity of F and F'/m."""
    t = t_nm * 10.0
    def f(E):
        k = math.sqrt(E * MB / HB2M)
        kap = math.sqrt((V0 - E) / HB2M)
        return math.tan(k * t / 2.0) - MB * kap / k
    emax = min(HB2M * (math.pi / t) ** 2 / MB * (1 - 1e-9), V0 - 1e-9)
    return brentq(f, 1e-9, emax)


def lin_gaps():
    rows = {}
    with LIN.open() as fh:
        for r in csv.DictReader(fh):
            if r["quantity"] == "Eg_PBE" and r["source"].startswith("Lin2022"):
                rows[r["thickness_nm"]] = float(r["value"])
    bulk = rows.pop("bulk")
    t = sorted(float(k) for k in rows)
    return bulk, t, [rows[f"{x:.2f}"] for x in t]


def save(fig, stem):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f"{stem}.pdf")
    plt.close(fig)
    print("saved", OUT / f"{stem}.pdf")


def logx_ticks(ax, ticks, labels):
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.set_xticklabels(labels)
    ax.xaxis.set_minor_formatter(NullFormatter())


# ------------------------------------------------------------------------------------------------ band edges vs vacuum
def fig_edges():
    fig, ax = plt.subplots(figsize=(56 * MM, 44 * MM))
    x = np.arange(len(S))
    be = b03["bulk_equivalent"]
    ax.axhline(-be["EA_eV"], color=GREY, ls="--", lw=0.8)
    ax.axhline(-be["IP_eV"], color=GREY, ls="--", lw=0.8)
    for i, s in enumerate(S):
        for e in (-s["EA_eV"], -s["IP_eV"]):
            ax.hlines(e, i - 0.3, i + 0.3, color=BLACK, lw=1.8)
        h = s["half_ramp_sensitivity_eV"]
        if h > 0:
            for e in (-s["EA_eV"], -s["IP_eV"]):
                ax.errorbar(i, e, yerr=h, fmt="none", ecolor=MAROON, elinewidth=0.9, capsize=2.5, capthick=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{t:.3f}" for t in T])
    ax.tick_params(axis="x", which="both", top=False)
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlim(-0.6, len(S) - 0.4)
    ax.set_ylim(-6.8, -2.8)
    ax.set_xlabel(r"$t_{\mathrm{HH}}$ (nm)")
    ax.set_ylabel(r"$E - E_{\mathrm{vac}}$ (eV)")
    fig.tight_layout(pad=0.3)
    save(fig, "06_edges")


# ------------------------------------------------------------------------------------------------ gaps against Lin et al.
def fig_gaps():
    lb, lt, lg = lin_gaps()
    fig, ax = plt.subplots(figsize=(58 * MM, 44 * MM))
    ax.axhline(EG_BULK, color=BLACK, ls="--", lw=0.8, label="bulk, this work")
    ax.axhline(lb, color=MAROON, ls=":", lw=0.9, label="bulk, Lin et al.")
    eg = [s["Eg_fundamental_eV"] for s in S]
    ax.plot(T[1:], eg[1:], "o", color=BLACK, label="films, this work (PAW)")
    ax.plot(T[:1], eg[:1], "o", mfc="white", mec=BLACK, label=r"In$_8$(OH)$_{24}$ (excluded)")
    ax.plot(lt, lg, "x", color=MAROON, ms=6, mew=1.3, label="films, Lin et al. (NC)")
    ax.set_xlim(0.3, 2.2)
    ax.set_ylim(0.5, 3.5)
    ax.set_xlabel(r"$t_{\mathrm{HH}}$ (nm)")
    ax.set_ylabel(r"PBE gap $E_{\mathrm{g}}$ (eV)")
    ax.minorticks_on()
    ax.legend(loc="upper right", handlelength=1.8, labelspacing=0.3, borderaxespad=0.4)
    fig.tight_layout(pad=0.3)
    save(fig, "06_gaps")


# ------------------------------------------------------------------------------------------------ thickness laws
def fig_laws():
    L = b03["laws"]
    fig, ax = plt.subplots(figsize=(58 * MM, 46 * MM))
    tt = np.geomspace(0.42, 10.0, 200)
    ax.axvspan(T[3], 10.0, color=SHADE, lw=0, zorder=0)       # beyond the thickest computed film: extrapolation
    ax.axvline(6.3, color=LGREY, ls=":", lw=0.9)
    ax.loglog(tt, law(L["dEg_eV"]["fit3"], tt), "-", color=BLACK, lw=1.0, label=r"$\Delta E_{\mathrm{g}}$ fit3")
    ax.loglog(tt, law(L["dEc_eV"]["fit2_1and2nm"], tt), "-", color=MAROON, lw=1.1,
              label=r"$\Delta E_{\mathrm{c}}$ fit2 (primary)")
    ax.loglog(tt, law(L["dEc_eV"]["fit3"], tt), "--", color=GREY, lw=1.0, label=r"$\Delta E_{\mathrm{c}}$ fit3 (frozen C10)")
    dEg = [s["dEg_eV"] for s in S]
    dEc = [s["dEc_eV"] for s in S]
    ax.plot(T[1:], dEg[1:], "o", color=BLACK, label=r"$\Delta E_{\mathrm{g}}$ computed")
    ax.plot(T[2:], dEc[2:], "s", color=MAROON, label=r"$\Delta E_{\mathrm{c}}$ computed")
    ax.plot(T[0], dEg[0], "o", mfc="white", mec=BLACK)
    ax.plot(T[0], dEc[0], "s", mfc="white", mec=MAROON)
    h = S[1]["half_ramp_sensitivity_eV"]
    ax.errorbar(T[1], dEc[1], yerr=h, fmt="s", mfc="white", mec=MAROON, ecolor=MAROON, elinewidth=0.9, capsize=2.5)
    logx_ticks(ax, [0.5, 1, 2, 5, 10], ["0.5", "1", "2", "5", "10"])
    ax.set_xlim(0.4, 10.0)
    ax.set_ylim(0.02, 4.0)
    ax.set_xlabel(r"$t_{\mathrm{HH}}$ (nm)")
    ax.set_ylabel("shift relative to bulk (eV)")
    ax.legend(loc="lower left", handlelength=2.0, labelspacing=0.25, borderaxespad=0.3)
    fig.tight_layout(pad=0.3)
    save(fig, "06_laws")


# ------------------------------------------------------------------------------------------------ envelope models
def fig_models():
    fig, ax = plt.subplots(figsize=(58 * MM, 46 * MM))
    tt = np.geomspace(0.40, 2.3, 200)
    ax.loglog(tt, eps_box(tt), ":", color=GREY, lw=1.1, label=r"infinite well, parabolic, $t=t_{\mathrm{HH}}$")
    ax.loglog(tt, ekane(eps_box(tt)), "--", color=BLACK, lw=1.0, label="infinite well, Kane")
    ax.loglog(tt, ekane(eps_box(BOX * tt)), "-", color=BLACK, lw=1.0, label=r"Kane, $t_{\mathrm{eff}} = 1.39\,t$")
    ax.loglog(tt, [e_finite(t) for t in tt], "-", color=MAROON, lw=1.1, label="finite barrier 4 eV, parabolic")
    ts = sorted(float(k) for k in ca["slabs"])
    dEc = [ca["slabs"][f"{t:.3f}"]["computed"]["dEc"] for t in ts]
    p1, = ax.plot(ts[2:], dEc[2:], "o", color=BLACK, ms=5, label="DFT (PBE)")
    p2, = ax.plot(ts[:2], dEc[:2], "o", mfc="white", mec=BLACK, ms=5, label="DFT, 0.461, 0.695 nm")
    logx_ticks(ax, [0.5, 1, 2], ["0.5", "1", "2"])
    ax.set_xlim(0.40, 2.3)
    ax.set_ylim(0.1, 60)
    ax.set_xlabel(r"$t_{\mathrm{HH}}$ (nm)")
    ax.set_ylabel(r"$\Delta E_{\mathrm{c}}$ (eV)")
    h, l = ax.get_legend_handles_labels()
    leg = ax.legend(h[:4], l[:4], loc="upper right", handlelength=2.0, labelspacing=0.25, borderaxespad=0.3)
    ax.add_artist(leg)
    ax.legend([p1, p2], [p1.get_label(), p2.get_label()], loc="lower left", handlelength=1.2, labelspacing=0.25,
              borderaxespad=0.3)
    fig.tight_layout(pad=0.3)
    save(fig, "06_models")
    for t in (0.9303, 1.9623):
        print(f"  finite barrier E1({t}) = {e_finite(t):.3f} eV")


# ------------------------------------------------------------------------------------------------ subband spacing
def fig_subbands():
    fit2 = b03["laws"]["dEc_eV"]["fit2_1and2nm"]
    fig, ax = plt.subplots(figsize=(60 * MM, 44 * MM))
    tt = np.geomspace(0.9, 16.0, 200)
    e1 = law(fit2, tt)
    e2 = ekane(4.0 * e1 * (1.0 + ALPHA * e1))
    b1 = ekane(eps_box(BOX * tt))
    b2 = ekane(eps_box(BOX * tt, 2))
    ax.axvspan(T[3], 16.0, color=SHADE, lw=0, zorder=0)       # beyond the thickest computed film: extrapolation
    for x in (2.0, 6.3, 13.2):                                 # device thicknesses; stop below the legend
        ax.axvline(x, ymax=0.64, color=LGREY, ls=":", lw=0.9)
    ax.loglog(tt, e2 - e1, "--", color=BLACK, lw=1.0, label=r"Kane + $\Delta E_{\mathrm{c}}$ fit2 law")
    ax.loglog(tt, b2 - b1, ":", color=MAROON, lw=1.3, label=r"Kane box, $t_{\mathrm{eff}} = 1.39\,t$")
    e21 = [s["E21_eV"] for s in S]
    ax.plot(T[2:], e21[2:], "o", color=BLACK, ms=5, label=r"DFT, $E_2-E_1$ at $\Gamma$")
    ax.plot(T[:2], e21[:2], "o", mfc="white", mec=BLACK, ms=5)
    logx_ticks(ax, [0.5, 1, 2, 5, 10], ["0.5", "1", "2", "5", "10"])
    ax.set_xlim(0.4, 16.0)
    ax.set_ylim(0.01, 20.0)                                    # headroom above the data for the legend
    ax.set_xlabel(r"$t_{\mathrm{HH}}$ (nm)")
    ax.set_ylabel(r"$E_2 - E_1$ (eV)")
    ax.tick_params(axis="y", which="both", right=False)
    ax2 = ax.secondary_yaxis("right", functions=(lambda e: e / KT, lambda n: n * KT))
    ax2.set_ylabel(r"$E_2 - E_1$ ($k_{\mathrm{B}}T$, 300 K)")
    ax2.tick_params(axis="y", which="both", direction="in")
    ax.legend(loc="upper right", handlelength=2.0, labelspacing=0.25, borderaxespad=0.3, frameon=False,
              markerfirst=False)                               # symbols at the right edge, away from the data
    fig.tight_layout(pad=0.3)
    save(fig, "06_subbands")
    for x in (1.9623, 6.3, 13.2):
        a1 = law(fit2, x); a2 = ekane(4 * a1 * (1 + ALPHA * a1))
        c1 = ekane(eps_box(BOX * x)); c2 = ekane(eps_box(BOX * x, 2))
        print(f"  t={x}: Kane+law {a2 - a1:.3f} eV ({(a2 - a1) / KT:.1f} kT); box {c2 - c1:.4f} eV ({(c2 - c1) / KT:.1f} kT)")


if __name__ == "__main__":
    fig_edges()
    fig_gaps()
    fig_laws()
    fig_models()
    fig_subbands()
