"""Figure mono_confinement_models: computed crystalline slab series against simple confinement models.

(a) dEc against H-H thickness: computed points; infinite parabolic well (bulk m_b, t = H-H); the same with Kane
non-parabolicity; Kane band with box width t_eff = 1.39 t (fixed at 2 nm). (b) in-plane band-edge mass: computed points
against the no-fit Kane relation m_b (1 + 2 alpha dEc) evaluated with the computed dEc. Plain style, no text in panels.
Data: evidence/derived/confinement_analysis.json (tools/confinement_analysis.py). Output: research_monograph/figures/.
"""
import importlib.util
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("figstyle", ROOT / "qe_workflow/analysis_2026-10-13_full/figstyle.py")
fs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fs)
plt, panel, CYCLE = fs.plt, fs.panel, fs.CYCLE

ca = json.loads((ROOT / "research_monograph/evidence/derived/confinement_analysis.json").read_text())
MB, AL, HB2M = 0.1541, 0.58, 3.80998
ts = sorted(float(k) for k in ca["slabs"])
dEc = [ca["slabs"][f"{t:.3f}"]["computed"]["dEc"] for t in ts]
m = [ca["slabs"][f"{t:.3f}"]["computed"]["m"] for t in ts]
mpred = [ca["slabs"][f"{t:.3f}"]["m_par_pred"] for t in ts]


def ekane(eps):
    return (-1 + math.sqrt(1 + 4 * AL * eps)) / (2 * AL)


tt = [0.4 + 0.02 * i for i in range(90)]
e_par = [HB2M * (math.pi / (t * 10)) ** 2 / MB for t in tt]
e_kan = [ekane(e) for e in e_par]
e_eff = [ekane(HB2M * (math.pi / (1.392 * t * 10)) ** 2 / MB) for t in tt]

fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_W, fs.FULL_W * 0.42))
ax[0].loglog(tt, e_par, ':', color="0.45", lw=1, label="infinite well, parabolic")
ax[0].loglog(tt, e_kan, '--', color=CYCLE[1], lw=1, label="infinite well, Kane")
ax[0].loglog(tt, e_eff, '-', color=CYCLE[0], lw=1, label=r"Kane, $t_{\rm eff}=1.39\,t$")
ax[0].loglog(ts[2:], dEc[2:], 'o', mfc='none', color='k', label="DFT (PBE)")
ax[0].loglog(ts[:2], dEc[:2], 'x', color='k', label="DFT, 0.461 / 0.695 nm")
ax[0].set_xlabel(r"$t_{\rm H-H}$ (nm)")
ax[0].set_ylabel(r"$\Delta E_{\rm c}$ (eV)")
ax[0].set_ylim(0.1, 20)
ax[0].legend(frameon=False, fontsize=7, loc="upper right")
panel(ax[0], "a", x=-0.2)
ax[1].plot(ts, m, 'o', mfc='none', color='k', label="DFT, band-edge 2-D DOS mass")
ax[1].plot(ts, mpred, 's', mfc='none', color=CYCLE[0], label=r"$m_b(1+2\alpha\Delta E_{\rm c})$, no fit")
ax[1].axhline(MB, color="0.45", ls=':', lw=1, label=r"bulk $m_b$")
ax[1].set_xlabel(r"$t_{\rm H-H}$ (nm)")
ax[1].set_ylabel(r"in-plane mass ($m_0$)")
ax[1].set_xlim(0.3, 2.1)
ax[1].set_ylim(0.1, 0.5)
ax[1].legend(frameon=False, fontsize=7)
panel(ax[1], "b", x=-0.2)
fig.tight_layout()
out = ROOT / "research_monograph/figures"
out.mkdir(exist_ok=True)
fig.savefig(out / "mono_confinement_models.pdf")
fig.savefig(out / "mono_confinement_models.png", dpi=200)
print("saved", out / "mono_confinement_models.pdf")
