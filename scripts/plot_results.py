#!/usr/bin/env python3
"""Plots from the best V1 runs (results/BEST_RUNS_V1.json) and the thickness laws. No simulator call.

Per thickness (plots/<key>/): overlay_log.png, overlay_linear.png, residual.png, band_diagram_eq.png,
band_diagram_near_vth.png, electron_density_depth.png, mobility_vs_vg.png (channel-centre probe: native
electron mobility; with a constant band-mobility model it is flat, which is itself a finding), free_vs_trapped.png
(if avg_n export exists). Global: metrics_vs_thickness.png (Vth, SS, mu, Ion, Ioff exp vs sim), plus the law plots
already written by material_laws.py. Every panel states the data source in its title/legend.
"""
import csv, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_metrics import metrics
ROOT = Path(__file__).resolve().parents[1]

def read2(p):
    pts = []
    for line in Path(p).read_text(errors='replace').splitlines():
        w = line.replace(',', ' ').split()
        if len(w) == 2:
            try: pts.append((float(w[0]), float(w[1])))
            except ValueError: pass
    return np.array(pts) if pts else None

def main():
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    best = json.loads((ROOT / 'results' / 'BEST_RUNS_V1.json').read_text()); g = {}
    for key, b in best.items():
        if not isinstance(b, dict) or 'directory' not in b: continue
        d = ROOT / b['directory']; t = float(b.get('thickness_nm', key.replace('p', '.'))); out = ROOT / 'plots' / key; out.mkdir(parents=True, exist_ok=True)
        cr = list(csv.DictReader((d / 'comparison.csv').open())); vg = np.array([float(r['vg_V']) for r in cr]); me = np.array([float(r['measured_A_per_um']) for r in cr]); si = np.array([float(r['atlas_A_per_um']) for r in cr])
        src = f'measured: workbook Sheet1 | simulated: ATLAS {b["run_id"]}'
        # cutline depth origin: the physical-structure decks start at the top of the 70 nm Air/Pd layer; shift so that the IWO top surface is depth 0
        meta = json.loads((d / 'metadata.json').read_text()) if (d / 'metadata.json').exists() else {}
        d_off = 70.0 if meta.get('full_structure') else 0.0
        fig, ax = plt.subplots(figsize=(6, 4.2)); ax.semilogy(vg, me, 'k.', ms=4, label='measured'); ax.semilogy(vg, np.maximum(si, 1e-40), 'r-', lw=1.3, label='ATLAS V1'); ax.set_ylim(1e-17, 1e-5); ax.set_xlabel('VG (V)'); ax.set_ylabel('ID (A/um), VD = 0.7 V'); ax.set_title(f'{t} nm IWO, log scale\n{src}', fontsize=8); ax.legend(); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(out / 'overlay_log.png', dpi=140); plt.close(fig)
        fig, ax = plt.subplots(figsize=(6, 4.2)); ax.plot(vg, me * 1e6, 'k.', ms=4, label='measured'); ax.plot(vg, si * 1e6, 'r-', lw=1.3, label='ATLAS V1'); ax.set_xlabel('VG (V)'); ax.set_ylabel('ID (uA/um)'); ax.set_title(f'{t} nm IWO, linear scale\n{src}', fontsize=8); ax.legend(); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(out / 'overlay_linear.png', dpi=140); plt.close(fig)
        fig, ax = plt.subplots(1, 2, figsize=(10, 4)); le = np.log10(np.maximum(si, 1e-40)) - np.log10(me); ax[0].plot(vg, np.clip(le, -1.5, 1.5), 'b.-', ms=3, lw=.8); ax[0].axhline(0, color='k', lw=.6); ax[0].set_ylabel('log10(ATLAS/measured) (clipped +/-1.5)'); ax[1].plot(vg, (si - me) * 1e6, 'b.-', ms=3, lw=.8); ax[1].axhline(0, color='k', lw=.6); ax[1].set_ylabel('ATLAS - measured (uA/um)')
        for a in ax: a.set_xlabel('VG (V)'); a.grid(alpha=.3)
        fig.suptitle(f'{t} nm residuals ({b["run_id"]}); native zeros where log residual is clipped', fontsize=9); fig.tight_layout(); fig.savefig(out / 'residual.png', dpi=140); plt.close(fig)
        for tag, title in [('eq', 'equilibrium (VG = VD = 0)'), ('vth', 'near threshold (VG ~ Vth_cc, VD = 0.7 V)'), ('on', 'on-state (VG = +3 V, VD = 0.7 V)')]:
            cb, vb, n = read2(d / f'cb_{tag}.dat') if (d / f'cb_{tag}.dat').exists() else None, read2(d / f'vb_{tag}.dat') if (d / f'vb_{tag}.dat').exists() else None, read2(d / f'n_{tag}.dat') if (d / f'n_{tag}.dat').exists() else None
            if cb is not None and vb is not None:
                fig, ax = plt.subplots(figsize=(6, 4.2)); ax.plot(cb[:, 0] * 1000 - d_off, cb[:, 1], 'b-', label='Ec'); ax.plot(vb[:, 0] * 1000 - d_off, vb[:, 1], 'r-', label='Ev')
                qf = read2(d / f'qfn_{tag}.dat') if (d / f'qfn_{tag}.dat').exists() else None
                if qf is not None: ax.plot(qf[:, 0] * 1000 - d_off, qf[:, 1], 'g--', label='EFn')
                ax.axvline(t, color='gray', lw=.8, ls=':'); ax.axvline(t + 2, color='gray', lw=.8, ls=':'); ax.set_xlim(-3, t + 17 + 3)
                ax.set_xlabel(f'depth from film top surface at x = 12 um (nm): IWO 0..{t} nm | Al2O3 | HfO2 to gate'); ax.set_ylabel('energy (eV)'); ax.set_title(f'{t} nm band diagram, {title}\nATLAS {b["run_id"]} cutline export', fontsize=8); ax.legend(); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(out / f'band_diagram_{tag}.png', dpi=140); plt.close(fig)
            if n is not None:
                fig, ax = plt.subplots(figsize=(6, 4.2)); ax.semilogy(n[:, 0] * 1000 - d_off, np.maximum(n[:, 1], 1e-5), 'k-'); ax.set_xlim(0, t); ax.set_xlabel(f'depth from film top surface (nm), IWO film 0..{t} nm; interface at {t} nm'); ax.set_ylabel('electron concentration (cm^-3)'); ax.set_title(f'{t} nm electron density vs depth, {title}\nATLAS {b["run_id"]}', fontsize=8); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(out / f'electron_density_{tag}.png', dpi=140); plt.close(fig)
        mob = read2(d / 'chan_mobility_vg.dat') if (d / 'chan_mobility_vg.dat').exists() else None
        if mob is not None:
            gm = np.gradient(me, vg); mufe = gm * 20e-4 / (1e-4 * 8.955369814335959e-07 * 0.7)
            fig, ax = plt.subplots(figsize=(6, 4.2)); ax.plot(mob[:, 0], mob[:, 1], 'r-', label='ATLAS channel-centre electron mobility (probe)'); ax.plot(vg, mufe, 'k.', ms=3, label='measured apparent mu_FE = gm L/(W Cox Vd)'); ax.set_xlabel('VG (V)'); ax.set_ylabel('mobility (cm^2/Vs)'); ax.set_ylim(0, None); ax.set_title(f'{t} nm mobility vs VG\n{b["run_id"]}', fontsize=8); ax.legend(fontsize=7); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(out / 'mobility_vs_vg.png', dpi=140); plt.close(fig)
        ne = read2(d / 'chan_electrons_vg.dat') if (d / 'chan_electrons_vg.dat').exists() else None; na = read2(d / 'avg_electrons_vg.dat') if (d / 'avg_electrons_vg.dat').exists() else None
        if ne is not None or na is not None:
            fig, ax = plt.subplots(figsize=(6, 4.2))
            if ne is not None: ax.semilogy(ne[:, 0], np.maximum(ne[:, 1], 1e-5), 'b-', label='free electrons at channel centre (probe)')
            if na is not None: ax.semilogy(na[:, 0], np.maximum(na[:, 1], 1e-5), 'g--', label='free electrons averaged over the film (probe)')
            ax.set_xlabel('VG (V)'); ax.set_ylabel('electron concentration (cm^-3)'); ax.set_title(f'{t} nm free-electron density vs VG (VD = 0.7 V)\nATLAS {b["run_id"]} probes; equilibrium value at VG = 0 is n_FB', fontsize=8); ax.legend(fontsize=7); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(out / 'electron_density_vs_vg.png', dpi=140); plt.close(fig)
        E = metrics(vg, me, False, t); S = metrics(vg, si, True, t)
        if key in ('2p0', '6p3', '13p2', '31p8'): g[t] = (E, S)   # global metrics plot uses the primary entry per thickness
    if g:
        ts = sorted(g); fig, ax = plt.subplots(2, 3, figsize=(13, 7))
        def pair(a, k, lab, log=False):
            e = [g[t][0][k] if g[t][0][k] is not None else np.nan for t in ts]; s_ = [g[t][1][k] if g[t][1][k] is not None else np.nan for t in ts]
            a.plot(ts, e, 'ko-', label='experiment'); a.plot(ts, s_, 'rs--', label='ATLAS V1'); a.set_xscale('log'); a.set_xlabel('t (nm)'); a.set_ylabel(lab); a.grid(alpha=.3); a.legend(fontsize=7)
            if log: a.set_yscale('log')
        pair(ax[0, 0], 'Vth_cc_1e-9_V', 'Vth (const. current 1e-9 A/um) (V)'); pair(ax[0, 1], 'SS_mV_dec', 'SS (mV/dec)'); pair(ax[0, 2], 'mu_FE_cm2Vs', 'mu_FE (cm^2/Vs)'); pair(ax[1, 0], 'Ion_A_per_um', 'Ion (A/um)', True); pair(ax[1, 1], 'Ioff_A_per_um', 'Ioff (A/um; sim = min positive)', True); pair(ax[1, 2], 'Ion_over_Ioff', 'Ion/Ioff (sim lower bound if zeros)', True)
        fig.suptitle('Device metrics vs thickness: experiment (workbook) vs ATLAS V1 best runs, identical extraction', fontsize=10); fig.tight_layout(); fig.savefig(ROOT / 'plots' / 'metrics_vs_thickness.png', dpi=140); plt.close(fig)
    print('plots written for', list(g))

if __name__ == '__main__': main()
