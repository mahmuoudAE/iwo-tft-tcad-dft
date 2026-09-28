#!/usr/bin/env python3
"""Write tables/MATERIAL_PARAMETERS_USED.{csv,md}, tables/PARAMETER_PROVENANCE.csv and
docs/PARAMETER_PROVENANCE.md from config/iwo_material_model.yaml (+ optional calibrated overrides
recorded in results/BEST_RUNS_V1.json). No simulator call.
"""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_iwo_decks import ROOT, load_configs, material_at, set_dotted, cox, KEYS, Q, KB

def main():
    m, g, s = load_configs()
    best = json.loads((ROOT / 'results' / 'BEST_RUNS_V1.json').read_text()) if (ROOT / 'results' / 'BEST_RUNS_V1.json').exists() else {}
    for o in best.get('shared_overrides', []): k, v = o.split('=', 1); set_dotted(m, k, v)
    T = [2.0, 6.3, 13.2, 31.8]; P = {t: material_at(m, t) for t in T}
    for t in T:
        ov = best.get('per_thickness_overrides', {}).get(KEYS[t], [])
        if ov:
            mm = json.loads(json.dumps(m))   # one copy per thickness; ALL of its overrides applied together
            for o in ov: k, v = o.split('=', 1); set_dotted(mm, k, v)
            P[t] = material_at(mm, t)
    Lw = m['thickness_laws']; b = m['bulk_reference']; C = cox(g)
    R = []
    def row(name, sym, kw, unit, vals, law, wdep, src_type, src, loc, label, unc, note):
        R.append({'Parameter': name, 'Symbol': sym, 'ATLAS keyword': kw, 'Units': unit, '2.0 nm': vals[0], '6.3 nm': vals[1], '13.2 nm': vals[2], '31.8 nm': vals[3], 'Thickness law / equation': law, 'W-composition dependence': wdep, 'Temperature': '300 K', 'Source type': src_type, 'Exact source/reference': src, 'Page/Figure/Table': loc, 'Label': label, 'Uncertainty': unc, 'Notes': note})
    f = lambda k, fmt='{:.4g}': [fmt.format(P[t][k]) for t in T]
    row('Bandgap', 'Eg(t)', 'EG300', 'eV', f('Eg_eV'), 'Eg_bulk + dEg_QC(t), dEg_QC = %.3f t^-%.3f' % (Lw['dEg_QC_eV']['a'], Lw['dEg_QC_eV']['p']), 'Eg_bulk from an IWO study; W widens gap (PBE, qualitative)', 'literature + DFT proxy', 'Fan2021 Sec.3 (bulk); Lin2022 Methods; Si2021 Fig.4', 'Lin2022 p.21542; Si2021 p.504', 'LITERATURE_IWO + DFT_PURE_IN2O3_PROXY', '+/-0.2 eV bulk; +/-50 % on dEg', 'PBE absolute gaps not used')
    row('Electron affinity', 'chi(t)', 'AFFINITY', 'eV', f('chi_eV'), 'chi_bulk - dEc(t), dEc = dEg (Ev fixed)', 'chi_bulk composition-mixing estimate (Fan2021)', 'literature + DFT proxy', 'Fan2021 Sec.3; Si2021', 'Si2021 p.504', 'LITERATURE_IWO + DFT_PURE_IN2O3_PROXY', '+/-0.3 eV absolute', 'absolute vacuum alignment not available; relative dEc only')
    row('Relative permittivity', 'eps_r', 'PERMITTIVITY', '-', f('eps_iwo'), 'shared', 'IWO 9.30 vs In2O3 9.03 (same process)', 'measured (C-V) on target process', 'Januar2026 SI Fig.S1 (not bundled; recorded by Astra)', 'SI Fig.S1b', 'MEASURED_TARGET_DEVICE', '+/-0.04 (SI); bulk crystal 10.55 (Stokey2021)', 'no thickness dependence imposed')
    row('Electron effective mass', 'm*(t)', '(none; enters Nc)', 'm0', f('mstar_m0'), '0.208 + %.3f t^-%.3f' % (Lw['mstar_m0']['b'], Lw['mstar_m0']['q']), 'W flattens CBM (PBE, qualitative) -> NOT DETERMINED', 'measured bulk + DFT proxy increment', 'Stokey2021; Lin2022', 'Stokey2021 Sec.IV.C; Lin2022 p.21540', 'MEASURED_RELATED_MATERIAL + DFT_PURE_IN2O3_PROXY', '+/-0.03 m0', 'nonparabolicity ignored')
    row('Effective conduction-band DOS', 'Nc(t)', 'NC300', 'cm^-3', f('Nc_cm3', '{:.3e}'), '2(2 pi m* kT/h^2)^1.5', 'via m*', 'calculated', 'this work', '-', 'CALCULATED', 'x0.8-1.3', '3-D continuum value; quasi-2D at 2 nm')
    row('Effective valence-band DOS', 'Nv', 'NV300', 'cm^-3', f('Nv_cm3', '{:.1e}'), 'shared', '-', 'assumed', '-', '-', 'ASSUMED', 'x10', 'holes not solved')
    row('Band mobility', 'mu_band(t)', '(enters MUN)', 'cm^2/Vs', f('mu_band'), 'per thickness', 'IWO lower than In2O3 (Januar2026)', 'fitted', 'this work (real ATLAS)', '-', 'FITTED', 'see SENSITIVITY_RESULTS', 'no defensible law; percolation/crystallinity hypothesis')
    row('Roughness factor', '(1-Dsr/t)^2', '-', '-', f('rough'), 'Dsr = 2.87 A', 'IWO 2.87 A vs In2O3 3.75 A', 'literature (target process)', 'Januar2026', 'Sec.2.9, Fig.5f', 'LITERATURE_IWO', 'unit ambiguity A vs nm noted', '')
    row('Constant mobility in deck', 'mu0(t)', 'MUN', 'cm^2/Vs', f('mu0'), 'mu_band(t) (1-Dsr/t)^2', '-', 'calculated', 'this work', '-', 'CALCULATED', '-', 'gate roll-off theta_r Vov not native (approximation gap)')
    row('Effective mobility', 'mu_eff(Vg)', '(solver output: n_free/(n_free+n_trap) x mu0)', 'cm^2/Vs', ['solver'] * 4, 'from DOS occupancy', '-', 'simulated', '-', '-', 'CALCULATED', '-', 'reported as mu_FE from gm in EXPERIMENTAL_VS_SIMULATION')
    row('Effective background donor density', 'Nd_eff(t)', 'DOPING N.TYPE CONC', 'cm^-3', f('Nd_cm3', '{:.3e}'), 'Nd0(1+(t/tc)^k), Nd0=%.2g, tc=%g nm, k=%g' % (Lw['Nd_eff_cm3']['Nd0'], Lw['Nd_eff_cm3']['tc_nm'], Lw['Nd_eff_cm3']['k']), 'NOT the W concentration', 'fitted law', 'this work; Kim2024 trend', 'Kim2024 p.6', 'FITTED', 'x2', 'electrically active donors only')
    row('Flat-band carrier density', 'n_FB(t)', '(solver equilibrium n)', 'cm^-3', ['solver'] * 4, 'from equilibrium solution', '-', 'simulated', '-', '-', 'CALCULATED', '-', 'Ioff ~ t n_FB used only as a consistency check')
    row('Bulk tail trap density', 'Nt(t)', '(NTA*WTA)', 'cm^-3', f('Nt_cm3', '{:.3e}'), 'Nt2 (2/t)^alpha, Nt2=%.1e, alpha=%g' % (Lw['Nt_cm3']['Nt2'], Lw['Nt_cm3']['alpha']), 'IWO lower than In2O3 (Januar2026)', 'fitted law (anchor ATLAS) + literature trend', 'this work; Januar2026', 'Januar2026 Sec.2.8/2.10', 'FITTED', 'x2', 'Januar Nt(2 nm)=5.3e19 with theta_t convention')
    row('Tail intercept density', 'NTA(t)', 'NTA', 'cm^-3/eV', f('NTA_cm3_eV', '{:.3e}'), 'Nt/WTA', '-', 'calculated', '-', '-', 'CALCULATED', '-', 'gTA = NTA exp((E-Ec)/WTA)')
    row('Tail energy width', 'WTA = kTt', 'WTA', 'eV', f('WTA_eV'), 'shared', '-', 'fitted', 'this work', '-', 'FITTED', '+/-0.005 eV', 'Tt = %.0f K; absolute Tt not in the paper' % (P[2.0]['WTA_eV'] / KB))
    row('Deep acceptor density', 'NGA', 'NGA', 'cm^-3/eV', f('NGA', '{:.1e}'), 'shared', '-', 'assumed', 'Fan2021 range', 'Fan2021 p.9', 'ASSUMED', 'x10', 'insensitive; EGA from Ec')
    row('Interface trap density', 'Dit', 'regularized NGA in region 2 (sheet/0.25 nm)', 'cm^-2 eV^-1', f('it_peak', '{:.1e}'), 'shared', '-', 'assumed / literature proxy', 'Lin2022; Wang2022 (HfO2/In2O3 6e11)', 'Lin2022 p.21539; Wang2022 p.4', 'ASSUMED', 'x3', 'Gaussian at Ec-0.3 eV, W 0.12 eV; IWO/Al2O3 interface here')
    row('Fixed interface charge', 'Qf', 'INTERFACE QF', 'cm^-2', f('Qf_cm2', '{:.3e}'), 'shared value 1.73e12; 6.3 nm DEVICE-SPECIFIC 8.7e10 (cause NOT DETERMINED)', '-', 'fitted', 'this work', '-', 'FITTED (shared) + FITTED device-specific (6.3 nm)', '-', 'dVfb = -q Qf/Cox = %+.3f V (2 nm), %+.3f V (6.3 nm)' % (-Q * P[2.0]['Qf_cm2'] / C, -Q * P[6.3]['Qf_cm2'] / C))
    row('Capture cross sections', 'sigma', 'SIGTAE.. SIGGDH', 'cm^2', f('sig', '{:.0e}'), 'shared', '-', 'assumed', '-', '-', 'ASSUMED', 'x100', 'not identifiable from DC')
    row('Gate work function', 'Phi_TiN', 'CONTACT WORKFUNCTION', 'eV', f('gate_wf'), 'shared', '-', 'assumed', 'TiN literature range 4.5-4.9', '-', 'ASSUMED', '+/-0.2 eV', 'degenerate with chi and Qf')
    row('S/D contact', 'Pd/IWO', 'CONTACT (no WF) [+RESISTANCE]', 'ohm.um', [f'{P[t]["rs_ohm_um"]:.3g}' for t in T], 'ideal Ohmic; 31.8 nm series R', '-', 'assumed / fitted (31.8)', 'Si2022/Lin2022 (CNL) context', '-', 'ASSUMED (+FITTED for 31.8 nm)', 'underconstrained (no TLM)', '')
    row('SRH lifetimes', 'tau_n, tau_p', 'TAUN0 TAUP0', 's', f('tau_s', '{:.0e}'), 'shared', '-', 'assumed', '-', '-', 'ASSUMED', 'x100', 'negligible')
    row('Channel length / width', 'L / W', 'geometry / MESH WIDTH', 'um', ['20 / 290 (sim 1)'] * 4, '-', '-', 'measured (figure)', 'schematic', '-', 'MEASURED_TARGET_DEVICE', '-', 'A/um normalization')
    row('Gate-stack capacitance', 'Cox', '(from eps and thickness)', 'F/cm^2', [f'{C:.4e}'] * 4, 'eps0/(15 nm/19.57 + 2 nm/9.0)', '-', 'calculated', 'SI Fig.S1 (HfO2), Al2O3 eps assumed', '-', 'CALCULATED', '+/-5 %', 'EOT 3.86 nm')
    with (ROOT / 'tables' / 'MATERIAL_PARAMETERS_USED.csv').open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(R[0].keys())); w.writeheader(); w.writerows(R)
    md = ['# Material parameters used in the simulation (V1)', '', 'Values are those written to the decks (see decks/*_metadata.json). Label = provenance class; no fitted value is called measured.', '',
          '| Parameter | Symbol | ATLAS | Units | 2.0 nm | 6.3 nm | 13.2 nm | 31.8 nm | Law | Label | Source | Uncertainty |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in R: md.append(f"| {r['Parameter']} | {r['Symbol']} | {r['ATLAS keyword']} | {r['Units']} | {r['2.0 nm']} | {r['6.3 nm']} | {r['13.2 nm']} | {r['31.8 nm']} | {r['Thickness law / equation']} | {r['Label']} | {r['Exact source/reference']} | {r['Uncertainty']} |")
    (ROOT / 'tables' / 'MATERIAL_PARAMETERS_USED.md').write_text('\n'.join(md) + '\n')
    prov = [{'parameter': r['Parameter'], 'label': r['Label'], 'source': r['Exact source/reference'], 'location': r['Page/Figure/Table'], 'notes': r['Notes']} for r in R]
    with (ROOT / 'tables' / 'PARAMETER_PROVENANCE.csv').open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(prov[0].keys())); w.writeheader(); w.writerows(prov)
    pm = ['# Parameter provenance (every model parameter carries one label)', '', 'Labels: MEASURED_TARGET_DEVICE, MEASURED_RELATED_MATERIAL, DFT_TARGET_IWO (none available), DFT_PURE_IN2O3_PROXY, LITERATURE_IWO, LITERATURE_IN2O3_PROXY, CALCULATED, FITTED, NUMERICAL, ASSUMED.', '', '| Parameter | Label | Source | Location | Notes |', '|---|---|---|---|---|']
    for p in prov: pm.append(f"| {p['parameter']} | {p['label']} | {p['source']} | {p['location']} | {p['notes']} |")
    pm += ['', '## Numerical (label NUMERICAL, from config/solver.yaml)', '', '| Item | Value | Evidence |', '|---|---|---|',
           '| XANDRNORM + CR.TOLER (strict, depletion) | 1e-17 A scaled by 1e-5 x min active current | Claude run_0006/0009/0010/0011/0018 |', '| CR.TOLER (on-state) | 5e-18 default, ^XANDRNORM | Claude run_0011 |', '| IR.TOL | 1e-19 A | - |', '| MAXTRAPS / ITLIMIT / CLIMIT | 10 / 80 / 1e-6 | documented range |',
           '| DOS levels NUMA/NUMD | 96/48 | x2 check: 0.006 dec (run_0016) |', '| vertical mesh | 0.25 nm (2 nm film), 0.0625 nm at interface layer, graded to 1 nm in thick films | mesh x0.5: 0.005 dec (run_0015); x0.7 for 13.2 nm: 0.004 dec (run_0026) |', '| interface regularization layer | 0.25 nm | layer /2: 0.009 dec (run_0017) |', '| gate step | 0.05 V logged, 0.1 V continuation | - |']
    (ROOT / 'docs' / 'PARAMETER_PROVENANCE.md').write_text('\n'.join(pm) + '\n'); print('tables written:', len(R), 'parameters')

if __name__ == '__main__': main()
