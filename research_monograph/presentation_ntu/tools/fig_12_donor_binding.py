"""Figure for section 12 (alternative explanations and uncertainty) of the NTU presentation.

Strict two-dimensional hydrogenic donor binding in a thin In2O3 film as a function of the mean permittivity of the
surroundings (dielectric confinement), with the bulk three-dimensional binding as reference.

Model (monograph chapter M06_defect_theory.tex, sec:mono-defect-hydrogenic, eq:mono-defect-hyd):
    bulk:       E_D  = (m*/m0) / eps_s^2 * Ry,           a_B* = eps_s / (m*/m0) * a0
    strict 2-D: E_2D = 4 E_D  (screening by the film itself, eps_s)                    [Bastard1981b]
                E_2D(eps_env) = 4 (m*/m0) / eps_env^2 * Ry  (screening set by the surroundings, upper bound)
    eps_env = (eps_1 + eps_2) / 2  (thin-film screening beyond r0 = eps_s t / (eps_1 + eps_2))   [Cudazzo2011]
Inputs (M06 lines 24-25, 42-46): m* = 0.208 m0 and eps_s = 10.55 (Stokey2021, p. 225102-1); Ry = 13.606 eV;
a0 = 0.0529 nm; eps(Al2O3) ~ 9, eps(HfO2) = 19.57, air = 1.
The values plotted are checked against research_monograph/evidence/derived/defect_estimates.json
("exp m 0.208, eps_s 10.55 (Stokey)": E_D_meV 25.4, E_2D_meV 101.7; "strict 2D, env Al2O3/air": eps_env 5.0,
E_2D_upper_bound_eV 0.45) and FACT-080; the HfO2/air value (eps_env 10.3, 0.11 eV) is the one stated in M06 line 45.

Writes presentation_ntu/figures/12_binding.pdf.
Run from anywhere:  python3 -I research_monograph/presentation_ntu/tools/fig_12_donor_binding.py
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator, NullFormatter, NullLocator

HERE = pathlib.Path(__file__).resolve().parent
PRES = HERE.parent
ROOT = PRES.parents[1]
OUT = PRES / "figures"
SRC = ROOT / "research_monograph" / "evidence" / "derived" / "defect_estimates.json"

MM = 1 / 25.4
BLACK, GREY, MAROON = "#000000", "#7a7a7a", "#801924"

plt.rcParams.update({
    "font.family": "Liberation Sans",
    "mathtext.fontset": "custom",
    "mathtext.rm": "Liberation Sans",
    "mathtext.it": "Liberation Sans:italic",
    "mathtext.bf": "Liberation Sans:bold",
    "font.size": 8.4,
    "axes.labelsize": 8.4,
    "xtick.labelsize": 7.9,
    "ytick.labelsize": 7.9,
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
    "lines.linewidth": 1.0,
    "pdf.fonttype": 42,
})

# inputs (M06_defect_theory.tex lines 24-25 and 42-46)
RY_EV = 13.606
A0_NM = 0.0529
M_REL = 0.208
EPS_S = 10.55
EPS_AIR, EPS_AL2O3, EPS_HFO2 = 1.0, 9.0, 19.57


def e2d(eps_env):
    """Strict 2-D hydrogenic binding (eV) with screening set by eps_env."""
    return 4.0 * M_REL / np.asarray(eps_env) ** 2 * RY_EV


def main():
    d = json.loads(SRC.read_text())
    ref = d["exp m 0.208, eps_s 10.55 (Stokey)"]
    env = d["strict 2D, env Al2O3/air"]

    e_bulk = M_REL / EPS_S ** 2 * RY_EV                     # eV
    a_bulk = EPS_S / M_REL * A0_NM                          # nm
    e_2d_film = 4.0 * e_bulk                                # eV, no dielectric contrast
    eps_alair = (EPS_AL2O3 + EPS_AIR) / 2.0
    eps_hfair = (EPS_HFO2 + EPS_AIR) / 2.0
    # cross-checks against the registered estimates (FACT-080, defect_estimates.json)
    assert abs(e_bulk * 1e3 - ref["E_D_meV"]) < 0.06, e_bulk
    assert abs(a_bulk - ref["aB_nm"]) < 0.006, a_bulk
    assert abs(e_2d_film * 1e3 - ref["E_2D_meV"]) < 0.2, e_2d_film
    assert abs(eps_alair - env["eps_env"]) < 1e-9
    assert abs(float(e2d(eps_alair)) - env["E_2D_upper_bound_eV"]) < 0.006
    assert abs(round(eps_hfair, 1) - 10.3) < 1e-9 and abs(round(float(e2d(eps_hfair)), 2) - 0.11) < 1e-9

    fig, ax = plt.subplots(figsize=(48 * MM, 35 * MM))
    # x range stops at 13: beyond eps_bar ~ 21 the strict 2-D bound would fall below the bulk 3-D binding, where the
    # strict 2-D limit has no meaning. No band for the device stack: it lies between the two limiting environments,
    # closer to HfO2/air at large distances (M06 lines 46-48; correction V6), so the accent marks the HfO2/air point and
    # the Al2O3/air upper bound is drawn as an open marker.
    x = np.geomspace(3.0, 13.0, 200)
    ax.plot(x, e2d(x), color=BLACK, lw=1.0, zorder=2)
    ax.axhline(e_bulk, color=BLACK, ls="--", lw=0.8, zorder=1)
    ax.axvline(EPS_S, color=GREY, ls=":", lw=0.8, zorder=1)
    ax.plot([eps_alair], [e2d(eps_alair)], "o", ms=4.6, mfc="white", mec=BLACK, mew=0.9, zorder=3)
    ax.plot([eps_hfair], [e2d(eps_hfair)], "o", ms=4.6, mfc=MAROON, mec=MAROON, zorder=3)
    # point labels (plain text next to the markers; no boxes)
    ax.annotate("Al$_2$O$_3$/air\n0.45 eV", (eps_alair, float(e2d(eps_alair))), xytext=(5, 2),
                textcoords="offset points", ha="left", va="bottom", fontsize=7.6)
    ax.annotate("HfO$_2$/air 0.11 eV", (eps_hfair, float(e2d(eps_hfair))), xytext=(-6, -3),
                textcoords="offset points", ha="right", va="top", fontsize=7.6, color=MAROON)
    ax.text(3.1, e_bulk * 1.12, "bulk (3-D), 25.4 meV", ha="left", va="bottom", fontsize=7.6)
    ax.text(EPS_S * 1.03, 1.25, r"$\varepsilon_s$", ha="left", va="top", fontsize=8.0, color=GREY)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(3.0, 13.0)
    ax.set_ylim(0.015, 1.5)
    ax.xaxis.set_major_locator(FixedLocator([3, 5, 10]))
    ax.xaxis.set_minor_locator(FixedLocator([4, 6, 7, 8, 9, 12]))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%g"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_major_locator(FixedLocator([0.02, 0.05, 0.1, 0.2, 0.5, 1.0]))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%g"))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_xlabel(r"surrounding permittivity $\bar\varepsilon$")
    ax.set_ylabel("2-D binding (eV)")
    fig.tight_layout(pad=0.3)
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "12_binding.pdf")
    plt.close(fig)
    print("saved", OUT / "12_binding.pdf")
    print(f"E_D {e_bulk*1e3:.1f} meV, a_B {a_bulk:.2f} nm, E_2D(film) {e_2d_film*1e3:.1f} meV")
    print(f"Al2O3/air eps {eps_alair:.1f} -> {float(e2d(eps_alair)):.3f} eV; "
          f"HfO2/air eps {eps_hfair:.3f} -> {float(e2d(eps_hfair)):.3f} eV")


if __name__ == "__main__":
    main()
