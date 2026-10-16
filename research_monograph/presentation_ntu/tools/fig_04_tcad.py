"""Figures for section 04 (device simulation) of the NTU presentation.

Reads only repository data:
  data/experimental_clean.csv                          measured transfer curves (Prof. M.-H. Lee's group, NTU)
  results/runs/run_00NN_*/idvg.dat                      ATLAS transfer curves (A/um, V_D = 0.7 V)
      V1 calibration chain:  2.0 nm  run_0001 (laws only, Q_f = 0) -> run_0003 (shared Q_f) -> run_0038 (final)
                             13.2 nm run_0002 -> run_0004 -> run_0040 (final)
      held-out 6.3 nm:       run_0014 (V1, shared laws), run_0060 (V2, variant P, predicted mobility)
  analysis_2026-10-06_V2/t2_t3_results.json             mobilities of V2 variants P and E (E = P scaled to I_on)

The final V1 anchors are scaled exactly to the measured on-current (I_D is linear in the uniform mobility; report
ch. 7, factors 0.999983 and 1.020113); variant E is run_0060 times mu_E/mu_P = 9.902/38.389 = 0.2579
(chapter 14_model_v2_rev, fig. v2_overlays caption). No simulated value is altered otherwise; native solver zeros
(|I_D| < 1e-17 A/um) are not drawn on the log axes.

Both figures are drawn at the size at which they are placed on the slide (half the 140 mm text width, 70 mm), so the
font sizes below are the projected sizes (8-8.5 pt, i.e. the slide's footnotesize).

Writes presentation_ntu/figures/04_calibration.pdf and 04_holdout.pdf.
Run from anywhere:  python3 -I research_monograph/presentation_ntu/tools/fig_04_tcad.py
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
RUNS = ROOT / "results" / "runs"
T3 = ROOT / "analysis_2026-10-06_V2" / "t2_t3_results.json"
MM = 1 / 25.4
MAROON, GREY, LGREY = "#801924", "#7a7a7a", "#b5b5b5"
FLOOR_SIM = 1e-17

RUN = {
    "0001": "run_0001_2p0_v1_baseline_laws",
    "0003": "run_0003_2p0_v1_stage3_qf1p73e12",
    "0038": "run_0038_2p0_recal_dos384_2p0",
    "0002": "run_0002_13p2_v1_baseline_laws",
    "0004": "run_0004_13p2_v1_stage3_qf1p73e12",
    "0040": "run_0040_13p2_recal_dos384_13p2",
    "0014": "run_0014_6p3_v2_full_stepped_validation_shared_params",
    "0060": "run_0060_6p3_v2_T3_prediction_6p3",
}

plt.rcParams.update({
    "font.family": "Liberation Sans",
    "mathtext.fontset": "custom",
    "mathtext.rm": "Liberation Sans",
    "mathtext.it": "Liberation Sans:italic",
    "mathtext.bf": "Liberation Sans:bold",
    "font.size": 8.5,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
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
    "legend.fontsize": 8,
    "lines.linewidth": 1.1,
    "pdf.fonttype": 42,
})


def measured():
    data = {}
    with open(CSV) as f:
        for r in csv.DictReader(f):
            data.setdefault(r["thickness_nm"], []).append((float(r["vg_V"]), float(r["id_A_per_um"])))
    out = {}
    for t, pts in data.items():
        pts.sort()
        out[t] = (np.array([p[0] for p in pts]), np.array([p[1] for p in pts]))
    return out


def atlas(run_id):
    """Two-column numeric rows of idvg.dat (V_G in V, I_D in A/um); header lines are skipped."""
    v, i = [], []
    for line in (RUNS / RUN[run_id] / "idvg.dat").read_text().splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        try:
            a, b = float(parts[0]), float(parts[1])
        except ValueError:
            continue
        v.append(a)
        i.append(b)
    return np.array(v), np.array(i)


def at3v(v, i):
    return float(np.interp(3.0, v, i))


def logmask(i):
    return np.where(i > FLOOR_SIM, i, np.nan)


def fig_calibration(meas):
    """Staged V1 calibration of the two anchor films: laws only -> + shared Q_f (rigid) -> final.

    The final step (run_0003 -> run_0038, run_0004 -> run_0040) is not a pure mobility rescaling: it also refines the
    tail-DOS quadrature (96/48 -> 384/192) and uses the physical deck; the final curve is then scaled exactly to the
    measured on-current."""
    fig, axs = plt.subplots(1, 2, figsize=(70 * MM, 46 * MM), sharey=True)
    chains = {"2.0": ("0001", "0003", "0038"), "13.2": ("0002", "0004", "0040")}
    for ax, t in zip(axs, ["2.0", "13.2"]):
        vm, im = meas[t]
        ax.semilogy(vm, im, ls="none", marker="o", ms=2.3, mfc="white", mec="black", mew=0.5, label="measured")
        r_law, r_qf, r_fin = chains[t]
        v, i = atlas(r_law)
        ax.semilogy(v, logmask(i), color=LGREY, ls=":", lw=1.2, label=r"laws only")
        v, i = atlas(r_qf)
        ax.semilogy(v, logmask(i), color=GREY, ls="--", lw=1.0, label=r"+ shared $Q_f$")
        v, i = atlas(r_fin)
        k = at3v(*meas[t]) / at3v(v, i)          # exact rescaling to the measured on-current
        ax.semilogy(v, logmask(i * k), color=MAROON, ls="-", lw=1.1, label=r"+ $\mu_\mathrm{band}$, DOS 384/192")
        ax.axhline(1e-9, color="black", lw=0.5, ls=(0, (1, 2)))
        ax.set_xlim(-1.0, 3.0)
        ax.set_xticks([-1, 0, 1, 2, 3])
        ax.set_ylim(1e-16, 1e-5)
        ax.set_yticks([1e-15, 1e-13, 1e-11, 1e-9, 1e-7, 1e-5])
        ax.set_xlabel(r"$V_\mathrm{G}$ (V)")
        ax.text(0.95, 0.06, f"{t} nm", transform=ax.transAxes, fontsize=8.5, ha="right", va="bottom",
                fontweight="bold")
    axs[0].set_ylabel(r"$I_\mathrm{D}$ (A/$\mu$m)")
    h, lab = axs[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", ncol=2, bbox_to_anchor=(0.57, 1.02), handlelength=1.8,
               handletextpad=0.5, columnspacing=0.9, labelspacing=0.2)
    fig.subplots_adjust(left=0.175, right=0.975, bottom=0.20, top=0.775, wspace=0.20)
    fig.savefig(OUT / "04_calibration.pdf")
    plt.close(fig)


def fig_holdout(meas):
    """Held-out 6.3 nm film: V1 shared laws (run_0014), V2 variant P (run_0060) and variant E (P scaled to I_on)."""
    t3 = json.loads(T3.read_text())["T3"]
    k_e = t3["E"]["mu_band"] / t3["P"]["mu_band"]
    vm, im = meas["6.3"]
    v14, i14 = atlas("0014")
    v60, i60 = atlas("0060")
    curves = [
        (v14, i14, dict(color=GREY, ls="--", lw=1.0), "model V1"),
        (v60, i60, dict(color=MAROON, ls="--", lw=1.0), r"model V2-P"),
        (v60, i60 * k_e, dict(color=MAROON, ls="-", lw=1.1), r"model V2-E"),
    ]
    fig, (a, b) = plt.subplots(1, 2, figsize=(70 * MM, 43 * MM))
    a.semilogy(vm, im, ls="none", marker="o", ms=2.3, mfc="white", mec="black", mew=0.5, label="measured")
    b.plot(vm, im * 1e6, ls="none", marker="o", ms=2.3, mfc="white", mec="black", mew=0.5, label="measured")
    for v, i, st, lab in curves:
        a.semilogy(v, logmask(i), label=lab, **st)
        b.plot(v, i * 1e6, label=lab, **st)
    a.axhline(1e-9, color="black", lw=0.5, ls=(0, (1, 2)))
    a.set_xlim(-1.0, 3.0)
    a.set_xticks([-1, 0, 1, 2, 3])
    a.set_ylim(1e-16, 1e-5)
    a.set_yticks([1e-15, 1e-12, 1e-9, 1e-6])
    a.set_xlabel(r"$V_\mathrm{G}$ (V)")
    a.set_ylabel(r"$I_\mathrm{D}$ (A/$\mu$m)")
    b.set_xlim(0.0, 3.0)
    b.set_xticks([0, 1, 2, 3])
    b.set_yticks([0, 0.5, 1.0, 1.5])
    b.set_ylim(-0.03, 1.65)
    b.set_xlabel(r"$V_\mathrm{G}$ (V)")
    b.set_ylabel(r"$I_\mathrm{D}$ ($\mu$A/$\mu$m)")
    for ax, lab in ((a, "(a)"), (b, "(b)")):
        ax.text(0.0, 1.03, lab, transform=ax.transAxes, fontsize=8.5, fontweight="bold", va="bottom")
    h, lab = a.get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", ncol=2, bbox_to_anchor=(0.55, 1.02), handlelength=1.8,
               handletextpad=0.5, columnspacing=0.9, labelspacing=0.2)
    fig.subplots_adjust(left=0.175, right=0.975, bottom=0.21, top=0.68, wspace=0.55)
    fig.savefig(OUT / "04_holdout.pdf")
    plt.close(fig)
    return k_e


def main():
    OUT.mkdir(exist_ok=True)
    meas = measured()
    fig_calibration(meas)
    k_e = fig_holdout(meas)
    print("variant E factor", round(k_e, 4))
    print("wrote", sorted(p.name for p in OUT.glob("04_*.pdf")))


if __name__ == "__main__":
    main()
