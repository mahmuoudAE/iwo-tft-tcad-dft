"""T4: ultrathin SCENARIOS (0.95, 0.75, 0.51 nm) with model V2, evaluated as pre-registered in T0_PRECHECKS.md.

Inputs: the --predict runs labelled v2_T4_<key> (central: mu_band held at the 2 nm anchor, Nt law alpha 0.75) and
v2_T4_<key>_Nt_alpha0 (Nt held at its 2 nm value). Bounds applied exactly, without launches:
  mobility: power-law rule mu_band(2 nm) (t/2)^n  -> current x (rule / central mu)   (Id linear in a uniform mobility)
  HSE:      dEc x 1.06 and x 1.11                 -> curve shifted right by 0.06 / 0.11 dEc (rigid affinity shift)
Floors: strip variant D at that thickness (V2 mass, scenario mobility), (W/L) from T1; and the measured setup floor of
the 2 nm device (median -2..-0.5 V) as the practical detection limit.
Outputs: t4_results.json, T4_SCENARIOS.md, figures/v2_scenarios.(png|pdf), data/v2_scenarios_raw.csv
"""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PKG / 'scripts'))
import t0_prechecks as t0  # noqa: E402
from extract_metrics import metrics  # noqa: E402

V2 = json.loads((HERE / 't0_results.json').read_text())['dft_swap']
T1 = json.loads((HERE / 't2_t3_results.json').read_text())
MU2 = V2['films']['2.0']['mu_band_V2']
N_RULE = V2['films']['6.3']['mu_powerlaw_exponent']


def runs_by_label():
    out = {}
    for r in csv.DictReader((PKG / 'results' / 'RUN_INDEX.csv').open()):
        if r['label'].startswith('v2_T4_') and r.get('converged'):
            out[r['label']] = PKG / r['output_dir']
    return out


def pred_curve(d):
    a = np.array([(float(r['vg_V']), float(r['atlas_A_per_um'])) for r in csv.DictReader((d / 'prediction.csv').open())])
    return a[:, 0], a[:, 1]


def shifted(vg, i, dv):
    li = np.log10(np.clip(i, 1e-40, None))
    return 10 ** np.interp(np.clip(vg - dv, vg[0], vg[-1]), vg, li)


def m(vg, i):
    x = metrics(vg, i, True, None)
    return {'Vth_cc': x['Vth_cc_1e-9_V'], 'Vth_lin': x['Vth_lin_V'], 'SS_cc': x['SS_cc_1e-10_1e-8_mV_dec'], 'Ion': x['Ion_A_per_um'], 'mu_FE': x['mu_FE_cm2Vs']}


def main():
    runs = runs_by_label()
    model = __import__('yaml').safe_load((PKG / 'config' / 'iwo_material_model_v2.yaml').read_text())
    pts = model['thickness_laws']['dEc_eV'].get('points') or {}
    vgm, im2 = t0.measured(2.0)
    setup_floor = float(np.median(im2[(vgm >= -2) & (vgm <= -0.5)]))
    wl = T1['T1']['W_over_L_per_um']
    res, rows = {}, []
    for lab, d in sorted(runs.items()):
        meta = json.loads((d / 'metadata.json').read_text())
        t = float(meta['thickness_nm']); mat = meta['material']
        vg, i = pred_curve(d)
        dec = mat['dEc_eV']
        mu_rule = MU2 * (t / 2.0) ** N_RULE
        g, ef, n = None, None, None
        ef, n = t0.neutral_ef(t, 'D', mstar=lambda x: mat['mstar_m0'])
        ipar = t0.Q * n * mat['mu0'] * t * 1e-7 * wl * t0.VD
        r = {'thickness_nm': t, 'run': d.name, 'dEc_eV': dec, 'chi_eV': mat['chi_eV'], 'mstar_m0': mat['mstar_m0'], 'Nt_cm3': mat['Nt_cm3'],
             'mu_band': mat['mu_band'], 'mu0': mat['mu0'], 'central': m(vg, i),
             'mu_rule_bound': {**m(vg, i * mu_rule / mat['mu_band']), 'mu_band': mu_rule},
             'HSE_x1.06': m(vg, shifted(vg, i, 0.06 * dec)), 'HSE_x1.11': m(vg, shifted(vg, i, 0.11 * dec)),
             'strip_floor_A_per_um': ipar, 'strip_EF_minus_Ec_eV': ef, 'setup_floor_A_per_um': setup_floor}
        ion = r['central']['Ion']
        r['Ion_over_Ioff_detectable'] = ion / max(ipar, setup_floor)
        res[lab] = r
        for v, x in zip(vg, i):
            rows.append([lab, t, v, x, x + ipar])
    (HERE / 't4_results.json').write_text(json.dumps(res, indent=1, default=float))
    (HERE / 'data').mkdir(exist_ok=True)
    with (HERE / 'data' / 'v2_scenarios_raw.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['label', 'thickness_nm', 'vg_V', 'id_atlas_A_per_um', 'id_with_strip_A_per_um']); w.writerows(rows)
    report(res, pts)
    figure(runs, res)


def report(res, pts):
    L = ['# T4: ultrathin SCENARIOS with model V2 (not predictions: the 6.3 nm held-out test failed, T2_T3_RESULTS.md)', '',
         'Rules pre-registered in T0_PRECHECKS.md section 3 (T4). Central: DFT dEc/dEg/m* at that thickness, Nt law extrapolated, '
         'mu_band held at the 2 nm anchor, roughness factor (1-0.287/t)^2. Bounds: mobility power-law rule and HSE (dEc x1.06-1.11) by exact '
         'transformation; Nt held at its 2 nm value by a separate launch (label suffix _Nt_alpha0).', '',
         '| label | t (nm) | dEc (eV) | m* | Nt (cm^-3) | mu0 | Vth_cc central | Vth_cc HSE x1.06-1.11 | SS_cc | Ion (A/um) | Ion with mu rule | strip floor | Ion/Ioff detectable |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    f = lambda x, p=3: '-' if x is None else f'{x:.{p}f}'
    for lab, r in res.items():
        c = r['central']
        L.append(f"| {lab} | {r['thickness_nm']} | {r['dEc_eV']:.3f} | {r['mstar_m0']:.3f} | {r['Nt_cm3']:.2e} | {r['mu0']:.2f} | {f(c['Vth_cc'])} | "
                 f"{f(r['HSE_x1.06']['Vth_cc'])} - {f(r['HSE_x1.11']['Vth_cc'])} | {f(c['SS_cc'], 0)} | {c['Ion']:.2e} | {r['mu_rule_bound']['Ion']:.2e} | "
                 f"{r['strip_floor_A_per_um']:.1e} | {r['Ion_over_Ioff_detectable']:.1e} |")
    (HERE / 'T4_SCENARIOS.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L))


def figure(runs, res):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(PKG / 'report_latex_full' / 'figures' / 'src'))
    from style import FULL_W  # noqa: E402
    t2 = json.loads((HERE / 't2_t3_results.json').read_text())
    fig, ax = plt.subplots(1, 3, figsize=(FULL_W, 2.6), gridspec_kw=dict(wspace=0.45))
    cmap = plt.cm.plasma
    a2 = next((PKG / 'results' / 'runs').glob(t2['T2']['2.0']['run'] + '*'))
    v, i2 = [np.array(x) for x in zip(*[(float(r['vg_V']), float(r['atlas_A_per_um'])) for r in csv.DictReader((a2 / 'comparison.csv').open())])]
    ax[0].semilogy(v, i2, color='k', lw=1.2, label='2.0 nm (V2 anchor)')
    cen = {lab: r for lab, r in res.items() if not lab.endswith('alpha0')}
    for k, (lab, r) in enumerate(sorted(cen.items(), key=lambda x: -x[1]['thickness_nm'])):
        vg, i = pred_curve(runs[lab])
        ax[0].semilogy(vg, np.clip(i + r['strip_floor_A_per_um'], 1e-17, None), color=cmap(0.15 + 0.3 * k), lw=1.2, label=f"{r['thickness_nm']:g} nm (scenario)")
    ax[0].set_ylim(1e-16, 1e-5); ax[0].set_xlabel(r'$V_G$ (V)'); ax[0].set_ylabel(r'$I_D$ (A/$\mu$m)'); ax[0].legend(fontsize=5.5, loc='lower right')
    ts = sorted(r['thickness_nm'] for r in cen.values())
    get = lambda key, sub='central': [next(r for r in cen.values() if r['thickness_nm'] == t)[sub][key] for t in ts]
    meas = {t: V2['films'][str(t)]['measured'] for t in (2.0, 6.3, 13.2)}
    ax[1].plot(ts, get('Vth_cc'), 'o-', color=cmap(0.3), label='scenario (PBE)')
    ax[1].fill_between(ts, get('Vth_cc', 'HSE_x1.06'), get('Vth_cc', 'HSE_x1.11'), color=cmap(0.3), alpha=0.25, lw=0, label='HSE range')
    ax[1].plot(list(meas), [x['Vth_cc'] for x in meas.values()], 'ks', ms=4, label='measured')
    ax[1].set_xscale('log'); ax[1].set_xlabel('IWO thickness (nm)'); ax[1].set_ylabel(r'$V_{th,cc}$ (V)'); ax[1].legend(fontsize=5.5)
    ax[2].plot(ts, get('Ion'), 'o-', color=cmap(0.3), label=r'$\mu_{band}$ held (2 nm)')
    ax[2].plot(ts, get('Ion', 'mu_rule_bound'), 'o--', color=cmap(0.6), label=r'$\mu_{band}$ power-law rule')
    ax[2].plot(list(meas), [x['Ion'] for x in meas.values()], 'ks', ms=4, label='measured')
    ax[2].set_xscale('log'); ax[2].set_yscale('log'); ax[2].set_xlabel('IWO thickness (nm)'); ax[2].set_ylabel(r'$I_D$(3 V) (A/$\mu$m)'); ax[2].legend(fontsize=5.5)
    (HERE / 'figures').mkdir(exist_ok=True)
    for ext in ('png', 'pdf'):
        fig.savefig(HERE / 'figures' / f'v2_scenarios.{ext}', dpi=200, bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    main()
