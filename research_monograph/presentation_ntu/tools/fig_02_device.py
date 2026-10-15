"""Figures for section 02 (devices and measured data) of the NTU presentation.

Reads only repository data:
  data/experimental_clean.csv                         measured transfer curves (Prof. M.-H. Lee's group, NTU)
  analysis_2026-10-06_extraction/results_a1.json      registered A1 swing windows and values (claim C008)
  research_monograph/evidence/derived/device_facts.json  floors, V_th,cc (FACT-101..103)
Paper values drawn as reference lines are quoted in the ledger (C025/C032: Fig. 1b SS 61.8/87.4/119.3 mV/dec,
digitised; C030: mu_max 5.1/3.73/27.4 cm2/Vs).

Writes presentation_ntu/figures/02_transfer.pdf, 02_local_ss.pdf, 02_mobility.pdf.
Run from anywhere:  python3 -I research_monograph/presentation_ntu/tools/fig_02_device.py
"""
import csv
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
CSV = ROOT / "data" / "experimental_clean.csv"
A1 = ROOT / "analysis_2026-10-06_extraction" / "results_a1.json"
FACTS = ROOT / "research_monograph" / "evidence" / "derived" / "device_facts.json"

COX = 8.955369814335959e-07          # F/cm^2, protocol C_ox (FACT-100)
L_CM, W_CM, VD = 20e-4, 290e-4, 0.7  # schematic
MM = 1 / 25.4

FILMS = ["2.0", "6.3", "13.2", "31.8"]
STYLE = {  # restrained palette: black, grey, NTU maroon, light grey
    "2.0": dict(color="#000000", ls="-", marker="o"),
    "6.3": dict(color="#7a7a7a", ls="--", marker="s"),
    "13.2": dict(color="#801924", ls="-", marker="^"),
    "31.8": dict(color="#b5b5b5", ls="-.", marker="D"),
}

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
    "legend.fontsize": 7,
    "lines.linewidth": 1.1,
    "pdf.fonttype": 42,
})


def load():
    data = {}
    with open(CSV) as f:
        for r in csv.DictReader(f):
            data.setdefault(r["thickness_nm"], []).append((float(r["vg_V"]), float(r["id_A_per_um"])))
    out = {}
    for t, pts in data.items():
        pts.sort()
        out[t] = (np.array([p[0] for p in pts]), np.array([p[1] for p in pts]))
    return out


def fig_transfer(d, facts):
    fig, (a, b) = plt.subplots(1, 2, figsize=(84 * MM, 44 * MM))
    for t in FILMS:
        v, i = d[t]
        s = STYLE[t]
        a.semilogy(v, i, color=s["color"], ls=s["ls"], lw=1.1)
        b.plot(v, i * 1e6, color=s["color"], ls=s["ls"], lw=1.1, label=f"{t} nm")
    # off-state floors: median over -2..-0.5 V (FACT-101..103), drawn over that window
    for t in ["2.0", "6.3", "13.2"]:
        fl = facts["films"][t]["floor_A_per_um"]
        a.plot([-2.0, -0.5], [fl, fl], color=STYLE[t]["color"], lw=2.2, alpha=0.9, solid_capstyle="butt")
    a.axhline(1e-9, color="black", lw=0.6, ls=":")
    a.text(-2.9, 1.6e-9, r"$10^{-9}$ A/$\mu$m", fontsize=6.5, va="bottom")
    a.text(-1.25, 1.6e-17, "floor window", fontsize=6.5, va="bottom", ha="center")
    a.annotate("", xy=(-2.0, 2.5e-16), xytext=(-0.5, 2.5e-16),
               arrowprops=dict(arrowstyle="<->", lw=0.5, shrinkA=0, shrinkB=0))
    a.set_ylim(1e-17, 1e-5)
    a.set_xlim(-3, 3)
    a.set_yticks([1e-17, 1e-15, 1e-13, 1e-11, 1e-9, 1e-7, 1e-5])
    a.set_xlabel(r"$V_\mathrm{G}$ (V)")
    a.set_ylabel(r"$I_\mathrm{D}$ (A/$\mu$m)")
    b.set_xlim(-3, 3)
    b.set_ylim(-0.1, 3.9)
    b.set_xlabel(r"$V_\mathrm{G}$ (V)")
    b.set_ylabel(r"$I_\mathrm{D}$ ($\mu$A/$\mu$m)")
    b.legend(loc="upper left", handlelength=2.2, borderaxespad=0.4, labelspacing=0.3)
    for ax, lab in ((a, "(a)"), (b, "(b)")):
        ax.text(0.0, 1.03, lab, transform=ax.transAxes, fontsize=8, fontweight="bold", va="bottom")
    fig.subplots_adjust(left=0.14, right=0.985, bottom=0.21, top=0.9, wspace=0.42)
    fig.savefig(OUT / "02_transfer.pdf")
    plt.close(fig)


def fig_local_ss(d, facts, a1):
    """Local swing dV_G/dlog10 I_D (protocol S2, a figure only) against I_D/floor, rising branch, I_D <= 1e-9."""
    fig, ax = plt.subplots(figsize=(67 * MM, 46 * MM))
    paper = {"2.0": 61.8, "6.3": 87.4, "13.2": 119.3}            # C032 / C025 (digitised from paper Fig. 1b)
    labels = {"2.0": "2.0 nm", "6.3": "6.3 nm", "13.2": "13.2 nm"}
    for t in ["2.0", "6.3", "13.2"]:
        v, i = d[t]
        fl = facts["films"][t]["floor_A_per_um"]
        lg = np.log10(i)
        ss = 1000.0 / np.gradient(lg, v)             # mV/dec, central differences
        # rising branch: from the first point after which I_D stays above 2 x floor, up to 1e-9 A/um
        above = i > 2 * fl
        k0 = len(v) - 1
        while k0 > 0 and above[k0 - 1]:
            k0 -= 1
        sel = np.arange(len(v)) >= k0
        sel &= i <= 1e-9
        s = STYLE[t]
        ax.plot(i[sel] / fl, ss[sel], color=s["color"], ls="-", lw=0.8, marker=s["marker"], ms=3.2,
                mfc="white" if t == "6.3" else s["color"], mec=s["color"], label=labels[t])
        # registered A1 window: thick bar at the A1 value spanning the window
        r = a1["films"][t]["results"]["main"]
        lo, hi = r["window"]
        ax.plot([lo / fl, hi / fl], [r["measured"], r["measured"]], color=s["color"], lw=3.2, alpha=0.55,
                solid_capstyle="butt")
        # paper Fig. 1b value, drawn over 1-12 x floor
        ax.plot([1, 12], [paper[t], paper[t]], color=s["color"], lw=1.0, ls=(0, (2, 1.5)))
    ax.axhline(59.5, color="black", lw=0.6, ls=":")
    ax.text(2.2e5, 52, r"$k_\mathrm{B}T\,\ln 10$ = 59.5 mV/dec", fontsize=6.5, ha="right", va="top")
    ax.set_xscale("log")
    ax.set_xlim(1, 3e5)
    ax.set_ylim(30, 300)
    ax.set_xlabel(r"$I_\mathrm{D}$ / off-state floor")
    ax.set_ylabel(r"local SS (mV/dec)")
    leg1 = ax.legend(loc="upper left", handlelength=1.6, borderaxespad=0.3, labelspacing=0.25)
    ax.add_artist(leg1)
    from matplotlib.lines import Line2D
    proxies = [Line2D([], [], color="#7a7a7a", lw=3.2, alpha=0.55, solid_capstyle="butt"),
               Line2D([], [], color="#7a7a7a", lw=1.0, ls=(0, (2, 1.5)))]
    # second legend stacked under the first, in the empty region left of the data (no curve passes there)
    ax.legend(proxies, ["window A1", "paper, Fig. 1b"], loc="upper left",
              bbox_to_anchor=(0.0, 0.71), handlelength=1.6, borderaxespad=0.3, labelspacing=0.25)
    fig.subplots_adjust(left=0.155, right=0.97, bottom=0.18, top=0.97)
    fig.savefig(OUT / "02_local_ss.pdf")
    plt.close(fig)


def fig_mobility(d):
    """mu_FE = L g_m/(W C_ox V_D) and the saturation formula 2L/(W C_ox) (d sqrt(I_D)/dV_G)^2 on the same curves."""
    paper = {"2.0": 5.1, "6.3": 3.73, "13.2": 27.4}               # C030 (paper; 3.73 digitised from Fig. 1b)
    ylim = {"2.0": 14, "6.3": 14, "13.2": 56}
    fig, axs = plt.subplots(1, 3, figsize=(80 * MM, 42 * MM))
    for ax, t in zip(axs, ["2.0", "6.3", "13.2"]):
        v, i = d[t]
        itot = i * 290.0                                 # A, total current for W = 290 um
        gm = np.gradient(itot, v)
        mufe = L_CM * gm / (W_CM * COX * VD)
        musat = 2 * L_CM / (W_CM * COX) * np.gradient(np.sqrt(np.clip(itot, 0, None)), v) ** 2
        m = v >= -0.5
        ax.plot(v[m], mufe[m], color="black", lw=1.1, label=r"$\mu_\mathrm{FE}$ (linear, $g_m$)")
        ax.plot(v[m], musat[m], color="#801924", lw=1.1, ls="--", label=r"$\mu_\mathrm{sat}$ formula")
        ax.axhline(paper[t], color="#7a7a7a", lw=0.8, ls=":")
        k = np.argmax(np.where(m, musat, -1))
        ax.plot(v[k], musat[k], marker="o", ms=3.5, mfc="white", mec="#801924", mew=0.9)
        ax.set_xlim(-0.5, 3)
        ax.set_ylim(0, ylim[t])
        ax.set_xticks([0, 1, 2, 3])
        ax.set_xlabel(r"$V_\mathrm{G}$ (V)")
        ax.text(0.04, 0.96, f"{t} nm", transform=ax.transAxes, fontsize=7.5, va="top")
    axs[0].set_ylabel(r"mobility (cm$^2$ V$^{-1}$ s$^{-1}$)")
    axs[0].text(2.95, paper["2.0"] + 0.35, "paper", fontsize=6.3, color="#5a5a5a", ha="right", va="bottom")
    h, lab = axs[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", ncol=2, bbox_to_anchor=(0.55, 1.0), handlelength=2.0,
               columnspacing=1.2)
    fig.subplots_adjust(left=0.125, right=0.985, bottom=0.21, top=0.86, wspace=0.4)
    fig.savefig(OUT / "02_mobility.pdf")
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    d = load()
    facts = json.loads(FACTS.read_text())
    a1 = json.loads(A1.read_text())
    fig_transfer(d, facts)
    fig_local_ss(d, facts, a1)
    fig_mobility(d)
    print("wrote", sorted(p.name for p in OUT.glob("02_*.pdf")))


if __name__ == "__main__":
    main()
