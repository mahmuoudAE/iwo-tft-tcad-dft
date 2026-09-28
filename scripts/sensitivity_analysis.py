#!/usr/bin/env python3
"""One-at-a-time sensitivity of the V1 model in the REAL solver (each case is one ATLAS launch).

  python scripts/sensitivity_analysis.py --thickness 2 --cases chi_m0p1 nd_x2 dit_x3 --stride 2

Each case perturbs one parameter of config/iwo_material_model.yaml (via --override), runs ATLAS through
run_atlas.execute, and records the change of Vth_cc, SS, mu_FE, Ion, Ioff(min positive) and active log RMSE
relative to the reference run given in results/BEST_RUNS_V1.json into tables/SENSITIVITY_RESULTS.csv.
Launch budget is enforced by run_atlas (solver.yaml runner.max_launches).
"""
import argparse, csv, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_atlas import execute, ROOT
from extract_metrics import metrics

CASES = {
    'chi_m0p1': ['bulk_reference.chi_bulk_eV.value=4.20'], 'chi_p0p1': ['bulk_reference.chi_bulk_eV.value=4.40'],
    'wf_p0p1': ['contacts.gate_workfunction_eV.value=4.80'],
    'nd_x2': ['thickness_laws.Nd_eff_cm3.Nd0=5e17'], 'nd_x0p5': ['thickness_laws.Nd_eff_cm3.Nd0=1.25e17'],
    'nt_x1p5': ['thickness_laws.Nt_cm3.Nt2=3e19'], 'wta_p5meV': ['thickness_laws.WTA_eV.value=0.045'],
    'dit_x3': ['traps.interface_acceptor_sheet.peak_cm2_eV=9e11'], 'dit_0': ['traps.interface_acceptor_sheet.peak_cm2_eV=1e9'],
    'eps_10p55': ['bulk_reference.eps_r.value=10.55'], 'mstar_bulk': ['thickness_laws.mstar_m0.b=0'],
    'no_confinement': ['thickness_laws.dEg_QC_eV.a=0', 'thickness_laws.mstar_m0.b=0'],
    'overlap_4um': ['geometry.contact_overlap_um.value=4.0'],
}
OUT = 'SENSITIVITY_OAT.csv'   # one-at-a-time results; merged into SENSITIVITY_RESULTS by sensitivity_from_stage_runs.py

def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--thickness', type=float, required=True); ap.add_argument('--cases', nargs='+', required=True); ap.add_argument('--stride', type=int, default=2); ap.add_argument('--vstep', type=float, default=0.1, help='ATLAS stepped sweep step (V); 0 = per-point solves with --stride'); ap.add_argument('--extra', action='append', default=[]); a = ap.parse_args()
    key = str(a.thickness).replace('.', 'p'); best = json.loads((ROOT / 'results' / 'BEST_RUNS_V1.json').read_text())
    ref = best[key]; shared = best.get('shared_overrides', []) + best.get('per_thickness_overrides', {}).get(key, [])
    rd = ROOT / ref['directory']; cr = list(csv.DictReader((rd / 'comparison.csv').open())); vg = np.array([float(r['vg_V']) for r in cr]); me = np.array([float(r['measured_A_per_um']) for r in cr]); r0 = np.array([float(r['atlas_A_per_um']) for r in cr])
    M0 = metrics(vg, r0, True, a.thickness); rmse0 = json.loads((rd / 'execution.json').read_text())['fit_metrics']['regions']['active']['rmse_log10']
    out = ROOT / 'tables' / OUT; new = not out.exists()
    for c in a.cases:
        ov = shared + CASES[c] + a.extra
        try: d = execute(a.thickness, f'sens_{c}', ov, stride=a.stride, vstep=(a.vstep or None))
        except RuntimeError as e: print('case', c, 'FAILED:', e); continue
        cr = list(csv.DictReader((d / 'comparison.csv').open())); vgs = np.array([float(r['vg_V']) for r in cr]); s = np.array([float(r['atlas_A_per_um']) for r in cr]); M = metrics(vgs, s, True, a.thickness)
        if len(vgs) != len(vg):   # stepped sweep: compare the reference on the same (coarser) grid
            sel = np.isin(np.round(vg, 6), np.round(vgs, 6)); M0 = metrics(vg[sel], r0[sel], True, a.thickness)
        rm = json.loads((d / 'execution.json').read_text())['fit_metrics']['regions']['active']['rmse_log10']
        row = {'thickness_nm': a.thickness, 'case': c, 'overrides': ' '.join(CASES[c]), 'run_id': d.name.split('_')[0] + '_' + d.name.split('_')[1], 'run_ref': ref['run_id'], 'dVth_cc_V': (M['Vth_cc_1e-9_V'] or np.nan) - (M0['Vth_cc_1e-9_V'] or np.nan), 'dSS_mV_dec': (M['SS_mV_dec'] or np.nan) - (M0['SS_mV_dec'] or np.nan), 'dmu_FE_pct': 100 * (M['mu_FE_cm2Vs'] / M0['mu_FE_cm2Vs'] - 1), 'dIon_pct': 100 * (M['Ion_A_per_um'] / M0['Ion_A_per_um'] - 1), 'Ioff_minpos_ratio': (M['Ioff_A_per_um'] or np.nan) / (M0['Ioff_A_per_um'] or np.nan), 'active_log_rmse': rm, 'active_log_rmse_ref': rmse0}
        with out.open('a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(row.keys())); (w.writeheader() if new else None); w.writerow(row); new = False
        print(json.dumps(row, default=float))

if __name__ == '__main__': main()
