"""Evaluate the V2 ATLAS runs against the pre-registration (T0_PRECHECKS.md) and add the off-current strip (T1).

T2: V2 anchors (2.0, 13.2 nm) vs the exact-transformation predictions in t0_results.json
    (criteria: Vth_cc within 0.005 V, Ion within 1 %, active RMSE within 0.005 dec).
T3: 6.3 nm held-out prediction, variant P (mu_band from the pre-registered power law, as run) and E (exact rescale of
    the same run to the measured Ion). Criteria: |dVth_cc| <= 0.10 V, |dVth_lin| <= 0.10 V, SS_cc within 20 %,
    active RMSE <= 0.15 dec, and for P also Ion within 30 %.
T1: I_total = I_ATLAS + G_D(t) Vd; G_D from strip variant D with the V2 mass law and the film mobility, (W/L) fitted
    on 13.2 nm (exact for a gate-independent parallel conductance at fixed Vd).
Outputs: t2_t3_results.json, T2_T3_RESULTS.md, figures/v2_overlays.(png|pdf), data/v2_overlays_raw.(csv|xlsx).
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

LABELS = {2.0: 'v2_anchor_2p0', 13.2: 'v2_anchor_13p2', 6.3: 'v2_T3_prediction_6p3'}
T0R = json.loads((HERE / 't0_results_registered.json').read_text())   # the V2 runs use these (registered) values
V2 = T0R['dft_swap']
CORR = json.loads((HERE / 't0_correction.json').read_text())['films']   # T0_CORRECTION.md (end-of-sweep fix)


def run_of(label):
    rows = [r for r in csv.DictReader((PKG / 'results' / 'RUN_INDEX.csv').open()) if r['label'] == label and r.get('converged')]
    if not rows:
        return None
    return PKG / rows[-1]['output_dir']


def curve(d):
    a = np.array([(float(r['vg_V']), float(r['measured_A_per_um']), float(r['atlas_A_per_um'])) for r in csv.DictReader((d / 'comparison.csv').open())])
    return a[:, 0], a[:, 1], a[:, 2]


def mets(vg, im, isim, t):
    floor = np.median(im[(vg >= -2) & (vg <= -0.5)])
    act = im > 5 * floor
    res = np.log10(np.clip(isim, 1e-40, None) / im)
    m = metrics(vg, isim, True, t)
    return {'rmse_active_dec': float(np.sqrt(np.mean(res[act] ** 2))), 'rmse_all_dec': float(np.sqrt(np.mean(res ** 2))),
            'Vth_cc': m['Vth_cc_1e-9_V'], 'Vth_lin': m['Vth_lin_V'], 'SS_cc': m['SS_cc_1e-10_1e-8_mV_dec'], 'Ion': m['Ion_A_per_um'], 'mu_FE': m['mu_FE_cm2Vs']}


def strip_conductance(t, mu_band):
    ef, n = t0.neutral_ef(t, 'D', mstar=t0.mstar_v2)
    return t0.Q * n * mu_band * t0.rough(t) * t * 1e-7, ef, n


def main():
    out = {'T2': {}, 'T3': {}, 'T1': {}}
    runs = {t: run_of(l) for t, l in LABELS.items()}
    missing = [t for t, d in runs.items() if d is None]
    if missing:
        sys.exit(f'runs not finished for {missing}')
    meas_m = {}
    # ---- T2
    for t in (2.0, 13.2):
        vg, im, isim = curve(runs[t])
        got = mets(vg, im, isim, t)
        meas_m[t] = V2['films'][str(t)]['measured']
        out['T2'][t] = {'run': runs[t].name, 'atlas': got}
        for name, pred in (('registered', V2['films'][str(t)]['V2']), ('corrected', CORR[str(t)]['corrected_prediction_at_run_parameters'])):
            chk = {'dVth_cc_V': got['Vth_cc'] - pred['Vth_cc'], 'dIon_pct': 100 * (got['Ion'] / pred['Ion'] - 1),
                   'dRMSE_dec': got['rmse_active_dec'] - pred['rmse_active_dec']}
            ok = abs(chk['dVth_cc_V']) <= 0.005 and abs(chk['dIon_pct']) <= 1.0 and abs(chk['dRMSE_dec']) <= 0.005
            out['T2'][t][name] = {'predicted': pred, 'difference': chk, 'verdict': 'PASS' if ok else 'FAIL'}
        out['T2'][t]['mu_band_final'] = V2['films'][str(t)]['mu_band_V2'] * im[-1] / isim[-1]   # exact Ion rescale (calibration)
    # ---- T3
    t = 6.3
    vg, im, isim = curve(runs[t])
    meas_m[t] = V2['films']['6.3']['measured']
    mu_p = V2['films']['6.3']['mu_P']
    mu_e = mu_p * im[-1] / isim[-1]
    for var, cur in (('P', isim), ('E', isim * mu_e / mu_p)):
        got = mets(vg, im, cur, t)
        mm = meas_m[t]
        crit = {'|dVth_cc| <= 0.10 V': abs(got['Vth_cc'] - mm['Vth_cc']) <= 0.10,
                '|dVth_lin| <= 0.10 V': abs(got['Vth_lin'] - mm['Vth_lin']) <= 0.10,
                'SS_cc within 20 %': abs(got['SS_cc'] / mm['SS_cc'] - 1) <= 0.20,
                'active RMSE <= 0.15 dec': got['rmse_active_dec'] <= 0.15}
        if var == 'P':
            crit['Ion within 30 %'] = abs(got['Ion'] / mm['Ion'] - 1) <= 0.30
        pre = V2['films']['6.3']['V2_P_mu_powerlaw' if var == 'P' else 'V2_E_mu_Ion_normalized']
        cor = CORR['6.3'][f'{var}_corrected']
        out['T3'][var] = {'run': runs[t].name, 'mu_band': mu_p if var == 'P' else mu_e, 'atlas': got, 'measured': mm,
                          'preregistered_prediction': pre, 'corrected_prediction': cor, 'criteria': crit,
                          'verdict': 'PASS' if all(crit.values()) else 'FAIL',
                          'atlas_minus_preregistered': {k: got[k] - pre[k] for k in ('Vth_cc', 'Vth_lin', 'SS_cc', 'rmse_active_dec')},
                          'atlas_minus_corrected': {k: got[k] - cor[k] for k in ('Vth_cc', 'Vth_lin', 'SS_cc', 'rmse_active_dec')}}
    # ---- T1: strip variant D, V2 mass law, film mobility (anchors: V2 mu; 6.3 nm: Ion-normalized mu)
    # final V2 curves: anchors at the exact Ion rescale (calibration, as V1's x1.0151), 6.3 nm in variant E
    scale = {tt: out['T2'][tt]['mu_band_final'] / V2['films'][str(tt)]['mu_band_V2'] for tt in (2.0, 13.2)}
    scale[6.3] = mu_e / mu_p
    mus = {2.0: out['T2'][2.0]['mu_band_final'], 6.3: mu_e, 13.2: out['T2'][13.2]['mu_band_final']}
    g, info = {}, {}
    for tt in (2.0, 6.3, 13.2):
        g[tt], ef, n = strip_conductance(tt, mus[tt])
        info[tt] = {'EF_minus_Ec_eV': ef, 'n_cm3': n}
    vg13, im13, _ = curve(runs[13.2])
    floor13 = np.median(im13[(vg13 >= -2) & (vg13 <= -0.5)])
    wl = floor13 / t0.VD / g[13.2]
    rows = []
    for tt in (2.0, 6.3, 13.2):
        vg, im, isim = curve(runs[tt])
        isim = isim * scale[tt]
        ipar = g[tt] * wl * t0.VD
        tot = isim + ipar
        fl = np.median(im[(vg >= -2) & (vg <= -0.5)])
        out['T1'][tt] = {**info[tt], 'mu_band': mus[tt], 'I_par_A_per_um': ipar, 'measured_floor': fl, 'pred_over_meas': ipar / fl,
                         'with_floor': mets(vg, im, tot, tt), 'without_floor': mets(vg, im, isim, tt)}
        for v, a, b, c in zip(vg, im, isim, tot):
            rows.append([tt, runs[tt].name, v, a, b, ipar, c, math.log10(max(c, 1e-40) / a)])
    out['T1']['W_over_L_per_um'] = wl
    out['T1']['curve_scale_factors'] = scale
    (HERE / 't2_t3_results.json').write_text(json.dumps(out, indent=1, default=float))
    (HERE / 'data').mkdir(exist_ok=True)
    head = ['thickness_nm', 'run', 'vg_V', 'id_measured_A_per_um', 'id_atlas_A_per_um', 'i_parallel_strip_A_per_um', 'id_total_A_per_um', 'log10_total_over_measured']
    with (HERE / 'data' / 'v2_overlays_raw.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(head); w.writerows(rows)
    try:
        from openpyxl import Workbook
        wb = Workbook(); wb.remove(wb.active)
        for tt in (2.0, 6.3, 13.2):
            ws = wb.create_sheet(f'{tt} nm'); ws.append(head)
            for r in rows:
                if r[0] == tt:
                    ws.append(r)
        wb.save(HERE / 'data' / 'v2_overlays_raw.xlsx')
    except ImportError:
        pass
    figure(runs, scale, out)
    report(out)


def figure(runs, scale, out):
    import matplotlib
    matplotlib.use('Agg')
    sys.path.insert(0, str(PKG / 'report_latex_full' / 'figures' / 'src'))
    from style import FILM, FILM_LABEL, MEAS, SIM, FULL_W  # noqa: E402
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(3, 3, figsize=(FULL_W, 6.0), sharex='col', gridspec_kw=dict(wspace=0.42, hspace=0.18))
    for c, t in enumerate((2.0, 6.3, 13.2)):
        vg, im, isim = curve(runs[t])
        lab = runs[t].name.split('_')[0] + '_' + runs[t].name.split('_')[1]
        if t == 6.3:
            ax[0, c].semilogy(vg, np.where(isim > 0, isim, np.nan), color='0.55', lw=0.9, ls='--', label=f'{lab} P (prediction)')
            lab += f' E (x{scale[t]:.4f})'
        else:
            lab += f' x{scale[t]:.4f}'
        isim = isim * scale[t]
        ipar = out['T1'][t]['I_par_A_per_um']
        tot = isim + ipar
        ax[0, c].semilogy(vg, im, **MEAS)
        ax[0, c].semilogy(vg, tot, color=FILM[t], **SIM, label=lab + ' + strip')
        ax[0, c].semilogy(vg, np.where(isim > 0, isim, np.nan), color=FILM[t], lw=0.8, ls=':')
        ax[0, c].set_ylim(1e-16, 1e-5); ax[0, c].legend(fontsize=5.5, loc='lower right'); ax[0, c].set_title(FILM_LABEL[t] + (' (held out)' if t == 6.3 else ''))
        ax[1, c].plot(vg, im * 1e6, **MEAS); ax[1, c].plot(vg, tot * 1e6, color=FILM[t], **SIM)
        r = np.log10(np.clip(tot, 1e-40, None) / im)
        ax[2, c].plot(vg, r, '.', color=FILM[t], ms=3); ax[2, c].axhline(0, color='k', lw=0.5); ax[2, c].set_ylim(-1.0, 1.0); ax[2, c].set_xlabel(r'$V_G$ (V)')
    ax[0, 0].set_ylabel(r'$I_D$ (A/$\mu$m)'); ax[1, 0].set_ylabel(r'$I_D$ ($\mu$A/$\mu$m)'); ax[2, 0].set_ylabel(r'$\log_{10}(I_{sim}/I_{meas})$')
    (HERE / 'figures').mkdir(exist_ok=True)
    for ext in ('png', 'pdf'):
        fig.savefig(HERE / 'figures' / f'v2_overlays.{ext}', dpi=200, bbox_inches='tight')
    plt.close(fig)


def report(out):
    L = ['# V2 results: T2 (anchors), T3 (6.3 nm held-out prediction), T1 (off-current strip)', '',
         'Generated by `t2_t3_evaluate.py` from the ATLAS runs, `t0_results_registered.json` (registered predictions) and `t0_correction.json` '
         '(end-of-sweep fix, registered before the T3 result: `T0_CORRECTION.md`); criteria as pre-registered in `T0_PRECHECKS.md` (hashes in `T0_REGISTRATION.txt`).', '']
    L += ['## T2: ATLAS V2 anchors vs the exact transformations (criteria: Vth_cc 0.005 V, Ion 1 %, RMSE 0.005 dec)', '',
          '| film | run | prediction | Vth_cc ATLAS / predicted | Ion ATLAS / predicted | active RMSE ATLAS / predicted | verdict |', '|---|---|---|---|---|---|---|']
    for t, r in out['T2'].items():
        a = r['atlas']
        for name in ('registered', 'corrected'):
            p = r[name]['predicted']
            L.append(f"| {t} nm | {r['run']} | {name} | {a['Vth_cc']:.4f} / {p['Vth_cc']:.4f} V | {a['Ion']:.4e} / {p['Ion']:.4e} | {a['rmse_active_dec']:.4f} / {p['rmse_active_dec']:.4f} dec | **{r[name]['verdict']}** |")
        L.append(f"| {t} nm | | final anchor mobility (exact Ion rescale) | mu_band = {r['mu_band_final']:.4f} | | | |")
    L += ['', '## T3: 6.3 nm, nothing fitted to this film', '', '| variant | mu_band | Vth_cc | Vth_lin | SS_cc | Ion | active RMSE | verdict |', '|---|---|---|---|---|---|---|---|']
    mm = out['T3']['P']['measured']
    L.append(f"| measured | - | {mm['Vth_cc']:.3f} | {mm['Vth_lin']:.3f} | {mm['SS_cc']:.1f} | {mm['Ion']:.3e} | - | - |")
    for v, r in out['T3'].items():
        a = r['atlas']
        L.append(f"| {v} | {r['mu_band']:.3f} | {a['Vth_cc']:.3f} | {a['Vth_lin']:.3f} | {a['SS_cc']:.1f} | {a['Ion']:.3e} | {a['rmse_active_dec']:.3f} | **{r['verdict']}** |")
    for v, r in out['T3'].items():
        L.append(f"- {v}: criteria " + '; '.join(f"{k}: {'met' if ok else 'NOT met'}" for k, ok in r['criteria'].items())
                 + '. ATLAS minus registered prediction: ' + ', '.join(f'{k} {d:+.4f}' for k, d in r['atlas_minus_preregistered'].items())
                 + '; minus corrected prediction: ' + ', '.join(f'{k} {d:+.4f}' for k, d in r['atlas_minus_corrected'].items()))
    L += ['', '## T1: off-current strip (variant D), added to every curve', '', f"(W/L) per um of width fitted on 13.2 nm: {out['T1']['W_over_L_per_um']:.3e}", '',
          '| film | EF - Ec (eV) | n (cm^-3) | I_par (A/um) | measured floor | pred/meas | RMSE all points, without -> with strip | active RMSE with strip |', '|---|---|---|---|---|---|---|---|']
    for t in (2.0, 6.3, 13.2):
        r = out['T1'][t]
        L.append(f"| {t} nm | {r['EF_minus_Ec_eV']:+.3f} | {r['n_cm3']:.2e} | {r['I_par_A_per_um']:.2e} | {r['measured_floor']:.2e} | {r['pred_over_meas']:.2f} | "
                 f"{r['without_floor']['rmse_all_dec']:.2f} -> {r['with_floor']['rmse_all_dec']:.2f} dec | {r['with_floor']['rmse_active_dec']:.3f} dec |")
    (HERE / 'T2_T3_RESULTS.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
