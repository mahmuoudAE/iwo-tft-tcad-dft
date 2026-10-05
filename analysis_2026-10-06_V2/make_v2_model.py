"""Write config/iwo_material_model_v2.yaml = V1 model with the DFT laws of this work and the V2 calibration (T0).

Changed relative to V1 (everything else is copied unchanged):
  thickness_laws.dEc_eV        NEW: conduction-band shift law through our DFT points (V1: dEc = dEg, partition 1.0)
  thickness_laws.dEg_QC_eV     gap-opening law through our DFT points (V1: Lin 2022 / Si 2021 proxies)
  thickness_laws.mstar_m0      mass increment law through our DFT points (V1: Lin 2022 increments)
  traps.fixed_interface_charge_Qf_cm2   shared Qf re-fitted on the 2 and 13.2 nm anchors (exact transformation, T0)
  thickness_laws.mu0_cm2Vs     anchor mobilities re-scaled to the measured Ion (exact); pre-registered prediction rule
Optional argument: a JSON file of DFT values at thinner films {"0.75": {"dEc": .., "dEg": .., "dm": ..}, ...}; they are
stored as tabulated 'points' (used only at exactly those thicknesses; no extrapolation of the fitted laws below 0.95 nm).
"""
import json
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(HERE))
import t0_prechecks as t0  # noqa: E402

SRC = ('this work: Quantum ESPRESSO 7.5, PBE, PAW, H-terminated In2O3(001) slabs (Lin et al. 2022 recipe), '
       'qe_workflow/cern_htcondor/results/RESULTS_LOG.md')


def main():
    m = yaml.safe_load((PKG / 'config' / 'iwo_material_model.yaml').read_text())
    r = json.loads((HERE / 't0_results.json').read_text())['dft_swap']
    thin = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 else {}
    m['schema'] = 'IWO_material_model_v2'
    m['status'] = ('V2 (2026-10-06): V1 with the conduction-band shift, gap opening and mass laws replaced by laws through '
                   'the DFT points of this work; shared Qf and anchor mobilities re-calibrated by exact transformation of '
                   'runs 0038/0040 (analysis_2026-10-06_V2/T0_PRECHECKS.md) and confirmed by ATLAS (T2)')
    L = m['thickness_laws']
    L['dEg_QC_eV'] = {
        'form': 'a * t_nm^(-p) for t >= 0.95 nm (through the 0.95 and 1.98 nm DFT points); tabulated DFT points below',
        'a': round(t0.a_g, 5), 'p': round(t0.p_g, 5), 'label': 'DFT_PURE_IN2O3_THIS_WORK', 'source': 'this work, PBE slabs',
        'fit_points': [{'t_nm': t, 'dE_eV': v, 'source': SRC} for t, v in t0.DFT['dEg'].items()],
        'points': {float(k): v['dEg'] for k, v in thin.items()},
        'note': ('PBE; HSE06/PBE ratio of the 0.95 nm gap opening 1.06 (1.06-1.11 with the EXX q-grid check); only '
                 'slab-minus-bulk differences are used; pure In2O3 as proxy for IWO; H-terminated slabs in vacuum')}
    L['dEc_eV'] = {
        'form': 'a * t_nm^(-p) for t >= 0.95 nm (through the 0.95 and 1.98 nm DFT points); tabulated DFT points below',
        'a': round(t0.a_c, 5), 'p': round(t0.p_c, 5), 'label': 'DFT_PURE_IN2O3_THIS_WORK', 'source': 'this work, PBE slabs, alignment to bulk',
        'fit_points': [{'t_nm': t, 'dE_eV': v, 'source': SRC} for t, v in t0.DFT['dEc'].items()],
        'points': {float(k): v['dEc'] for k, v in thin.items()},
        'note': ('conduction-band minimum relative to bulk: 1.98 nm by two-step alignment (planar-averaged potential, '
                 'a/2 window; double average +0.287 eV), 0.95 nm = 1.98 nm value + same-termination electron-affinity '
                 'difference (+0.567 eV). Conduction-band share of the gap opening 0.84 (2 nm) and 0.94 (1 nm); V1 assumed 1.0')}
    L['band_edge_partition']['note'] = 'not used in V2 (superseded by dEc_eV)'
    L['mstar_m0'] = {
        'form': 'mstar_bulk_exp + b * t_nm^(-q) for t >= 0.95 nm; tabulated DFT increments below',
        'b': round(t0.b_m, 5), 'q': round(t0.q_m, 5), 'label': 'MEASURED_RELATED_MATERIAL + DFT_PURE_IN2O3_THIS_WORK increment',
        'source': 'Stokey2021 bulk 0.208 + this-work PBE in-plane CB-mass increment (bulk PBE 0.159)',
        'fit_points': [{'t_nm': 0.95, 'dm_m0': round(t0.DFT['mstar'][0.95] - t0.DFT['mstar']['bulk'], 5)},
                       {'t_nm': 1.98, 'dm_m0': round(t0.DFT['mstar'][1.98] - t0.DFT['mstar']['bulk'], 5)}],
        'points': {float(k): v['dm'] for k, v in thin.items()}}
    m['traps']['fixed_interface_charge_Qf_cm2'] = {
        'value': float(f"{r['Qf_V2_cm2']:.5e}"),
        'label': ('FITTED single shared value (V2): least squares on the active log-RMSE of the 2 and 13.2 nm anchors by '
                  'exact rigid-shift transformation of runs 0038/0040 (T0); V1 value 1.73e12')}
    mu = L['mu0_cm2Vs']
    mu['mu_band_fitted'] = {2.0: round(r['films']['2.0']['mu_band_V2'], 4), 13.2: round(r['films']['13.2']['mu_band_V2'], 4)}
    mu['anchor_thicknesses_nm'] = [2.0, 13.2]
    mu['label'] = ('FITTED per anchor film (V2: exact rescale to the measured Ion at 3 V); any other thickness only through '
                   'the pre-registered prediction rule or an explicit scenario value')
    mu['mu_band_prediction_rule'] = {'form': 'mu_band(2 nm) * (t/2)^n, n from the two anchors',
                                     'n': round(r['films']['6.3']['mu_powerlaw_exponent'], 5),
                                     'label': 'PRE-REGISTERED PREDICTION RULE (T3), not a fit'}
    out = PKG / 'config' / 'iwo_material_model_v2.yaml'
    out.write_text(yaml.safe_dump(m, sort_keys=False, width=140))
    print('wrote', out)
    for k in ('dEg_QC_eV', 'dEc_eV', 'mstar_m0'):
        print(k, {x: L[k][x] for x in ('a', 'p', 'b', 'q', 'points') if x in L[k]})
    print('Qf', m['traps']['fixed_interface_charge_Qf_cm2']['value'], 'mu', mu['mu_band_fitted'], 'rule n', mu['mu_band_prediction_rule']['n'])


if __name__ == '__main__':
    main()
