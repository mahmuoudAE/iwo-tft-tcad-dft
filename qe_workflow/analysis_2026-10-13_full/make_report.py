"""Writes DFT_FULL_STUDY.md from the JSON outputs of f01-f12 (run those first; run_all.sh does both).

Every re-derived number in the report is read from out/*.json (never typed). Every LOGGED comparison value is quoted
together with its file:line, and the script asserts that the quoted text really appears on that line (lg()), so a
wrong citation stops the build.
"""
import json
import math
from pathlib import Path

import qeio as q

O = {p.stem: json.loads(p.read_text()) for p in sorted(q.OUT.glob('*.json'))}
RL = q.RES / 'RESULTS_LOG.md'
PROT = q.BULK / 'PROTOCOL.md'
LEDGER = q.QE.parents[1] / 'iwo-tft-research-private' / '03_CLAIMS_LEDGER.yaml'
DFTIN = q.QE.parent / 'analysis_2026-10-10_campaign' / 'dft_inputs.json'
ALIGN = q.BULK / 'bulk_alignment.py'
CHECKED = []


# Lines inserted above the RESULTS_LOG entry that was the first one when the references were written (it was at line 3); new
# entries are added at the top (2026-10-14: errata / C021 entry, then the bands / masses entry), original lines unchanged.
RL_INSERTED_TOP = next(i for i, l in enumerate(RL.read_text(encoding='utf-8').splitlines(), 1)
                       if l.startswith('## 2026-10-13 03:40Z: H-L crystalline oxygen-vacancy test scored')) - 3


def lg(path, line, text):
    """Quote 'text' from path:line after checking it is there. RESULTS_LOG line numbers written before 2026-10-14 are moved by
    the 72 lines inserted at the top that day (original lines unchanged); the reference printed is the current line."""
    L = q.lines(str(path))
    if path == RL and text not in L[line - 1] and line + RL_INSERTED_TOP <= len(L) and text in L[line + RL_INSERTED_TOP - 1]:
        line += RL_INSERTED_TOP
    if text not in L[line - 1]:
        # the file changed after the reference was written (e.g. ledger entries edited 2026-10-14): use the unique occurrence
        hits = [i + 1 for i, l in enumerate(L) if text in l]
        assert len(hits) == 1, f'{path.name}: {text!r} not at line {line} and found {len(hits)} times'
        line = hits[0]
    ref = f'{q.rel(path)}:{line}'
    CHECKED.append(ref)
    return ref


def st(new, logged, tol):
    return 'match' if abs(new - logged) <= tol + 1e-12 else f'**DIFFERS** ({new - logged:+.4g})'


def v(x):
    return x['value'] if isinstance(x, dict) and 'value' in x else x


def s(x):
    return x['src'] if isinstance(x, dict) and 'src' in x else ''


def main():
    f1, f2, f3, f4, f5 = (O[k] for k in ('f01_bulk_convergence', 'f02_bulk_structure_bands', 'f03_bulk_alignment', 'f04_slab_vacuum', 'f05_slab_series'))
    f6, f7, f8, f9, f10, f11, f12 = (O[k] for k in ('f06_confinement_laws', 'f07_hse_ratio', 'f08_slab_pdos_surface', 'f09_iwo_bulk',
                                                     'f10_iwo_slabs', 'f11_hl_vacancy', 'f12_relax_traces'))
    S = f5['slabs']
    W = []   # report lines
    a = W.append
    a('# Full non-blind DFT study: re-derived numbers and figures (2026-10-13)\n')
    a('Folder `qe_workflow/analysis_2026-10-13_full/`. Every number below is re-derived from the raw Quantum ESPRESSO outputs by the '
      'scripts in this folder (independent parsers in `qeio.py`; nothing is imported from the earlier analysis scripts). '
      'Re-derived values are cited at the raw-output `file:line` (paths relative to `qe_workflow/`); logged values are quoted with their '
      '`file:line`, and `make_report.py` checks each quotation against that line. '
      'Labels: **COMPUTED** (our DFT output), **FITTED** (fit to the named COMPUTED points), **ASSUMED**, **LITERATURE**, **LOGGED** (value as written in RESULTS_LOG / ledger).\n')
    a('**Blindness.** No amorphous-cell output (aIO_\\*/aIWO_\\* FINALs, relax energies, forces, bands, PDOS) was opened. All cells here are crystalline '
      '(bulk bixbyite, H/OH-terminated (001) slabs, W-substituted cells, the six H-L vacancy cells). The H-L numbers come from the archived '
      'grep `evidence_20261013_HL/r23.out`, which contains crystalline cells only.\n')
    a('**Reproduce.** `python f01_bulk_convergence.py` ... `python f12_relax_traces.py`, then `python make_report.py` (Python 3.13, numpy, matplotlib; '
      'all read-only; writes only `out/`, `figures/` and this file). Method throughout: PAW-PBE (pslibrary 1.0.0; In 4d, W 5s5p in valence), '
      '71/568 Ry, QE 7.5 (CPU) or 7.3.1 (GPU) as noted; HSE06 only as SG15 norm-conserving single points.\n')

    # ------------------------------------------------------------ summary
    a('## Summary of the key numbers\n')
    a('| Quantity | Re-derived | Logged | Status | Label | Source (re-derived) |')
    a('|---|---|---|---|---|---|')
    vr = f2['vcrelax']; bp = f2['bands_path']
    rows = [
        ('bulk a (A), vc-relax', v(vr['a_conv_A']), 10.3061, 5e-5, lg(PROT, 94, 'a = 10.3061 A'), s(vr['a_conv_A'])),
        ('bulk a vs exp 10.117 A (%)', vr['deviation_pct'], 1.87, 5e-3, lg(PROT, 95, '+1.87 %'), s(vr['a_conv_A'])),
        ('bulk Eg fundamental (eV)', bp['Eg_fundamental_eV'], 0.889, 5e-4, lg(PROT, 130, 'Fundamental gap: **0.889 eV**'), f"{s(bp['VBM_eV'])}, {s(bp['CBM_eV'])}"),
        ('bulk Eg direct at Gamma (eV)', bp['Eg_direct_Gamma_eV'], 0.893, 5e-4, lg(PROT, 130, 'Direct gap at Gamma: **0.893 eV**'), s(bp['CB_Gamma_eV'])),
        ('bulk CB mass [100] (m0)', f2['mass']['[100]']['m_parabolic_intercept_m0'], 0.1588, 5e-5, lg(PROT, 111, '0.1588 m0'), f2['mass']['[100]']['src']),
        ('bulk <V> (eV) (UPF G=0 route)', v(f3['bulk']['Vmean_eV']), 4.1687, 5e-5, lg(RL, 349, '<V> = 4.1687 eV'), 'UPF PP_LOCAL + bulk cell; validated on 10 slabs to 0.0 meV'),
        ('bulk E_v - <V> (eV)', f3['bulk']['Ev_minus_V_eV'], 3.9098, 5e-5, lg(RL, 349, 'E_v - <V> = 3.9098 eV'), s(bp['VBM_eV'])),
        ('bulk E_c - <V> (eV)', f3['bulk']['Ec_minus_V_eV'], 4.7985, 5e-5, lg(RL, 349, 'E_c - <V> = 4.7985 eV'), s(bp['CBM_eV'])),
        ('2 nm gap (eV)', S['2.0']['gap_eV'], 1.2239, 5e-5, lg(RL, 435, 'Gap: 1.2239 eV'), s(S['2.0']['CBM_eV'])),
        ('2 nm dEg (eV)', S['2.0']['dEg_eV'], 0.335, 5e-4, lg(RL, 435, '**dEg(2 nm) = +0.335 eV**'), s(S['2.0']['CBM_eV'])),
        ('2 nm dEc, two-step a/2 (eV)', S['2.0']['dEc_eV'], 0.281, 5e-4, lg(RL, 360, '| 2 nm | two-step, a/2 window | +0.281 | -0.054 |'), f3['two_step']['slab2_relax_c2']['avg_src']),
        ('2 nm dEv, two-step a/2 (eV)', S['2.0']['dEv_eV'], -0.054, 5e-4, lg(RL, 360, '-0.054'), f3['two_step']['slab2_relax_c2']['avg_src']),
        ('2 nm EA / IP (eV)', S['2.0']['EA_eV'], 4.495, 5e-4, lg(RL, 436, 'EA = 4.495 eV, IP = 5.719 eV'), s(S['2.0']['E_vac_eV'])),
        ('2 nm m* [100] (m0)', S['2.0']['mass']['[100]']['m_intercept_m0'], 0.2064, 5e-5, lg(RL, 417, '0.2064 m0 [100]'), S['2.0']['mass']['src']),
        ('2 nm E2 - E1 at Gamma (eV)', v(S['2.0']['mass']['E21_Gamma_eV']), 0.719, 5e-4, lg(RL, 418, '0.719 eV above the CBM'), s(S['2.0']['mass']['E21_Gamma_eV'])),
        ('1 nm gap (eV)', S['1.0']['gap_eV'], 1.7885, 5e-5, lg(RL, 522, '| gap, relaxed 1 nm slab | 1.7885 eV'), s(S['1.0']['CBM_eV'])),
        ('1 nm dEg (eV)', S['1.0']['dEg_eV'], 0.900, 5e-4, lg(RL, 523, '**+0.900 eV**'), s(S['1.0']['CBM_eV'])),
        ('1 nm dEc, EA route (eV)', S['1.0']['dEc_eV'], 0.848, 5e-4, lg(RL, 363, '| 1 nm | EA/IP route (recommended) | +0.848 | -0.056 |'), s(S['1.0']['E_vac_eV'])),
        ('1 nm dEv, EA/IP route (eV)', S['1.0']['dEv_eV'], -0.056, 5e-4, lg(RL, 363, '-0.056'), 'dEc - dEg (identity)'),
        ('1 nm m* [100] (m0)', S['1.0']['mass']['[100]']['m_intercept_m0'], 0.281, 5e-4, lg(RL, 524, '0.281 m0'), S['1.0']['mass']['src']),
        ('0.75 nm (H-H 0.695) gap (eV)', S['0.75']['gap_eV'], 2.20, 5e-3, lg(LEDGER, 121, '0.75 nm slab gap 2.20 eV'), s(S['0.75']['CBM_eV'])),
        ('0.51 nm (H-H 0.461) gap (eV)', S['0.51']['gap_eV'], 3.14, 5e-3, lg(LEDGER, 121, '3.14 eV PBE gap'), s(S['0.51']['CBM_eV'])),
        ('HSE/PBE ratio r (q 1)', f7['r_q1'], 1.060, 5e-4, lg(RL, 472, 'Ratio dEg(HSE)/dEg(PBE) = 1.060'), s(f7['runs']['nc_hse_slab1_f160_e80']['gap_eV'])),
        ('HSE/PBE ratio r (worst, q 3 bulk)', f7['r_q3_worst'], 1.107, 5e-4, lg(RL, 476, 'the ratio becomes 1.107'), s(f7['runs']['nc_hse_bulk_q3_f160_e80']['gap_eV'])),
        ('W site E(8b)-E(24d), k4 (eV)', f9['E8b_minus_E24d_eV']['E_scf_k4_Ry'], 0.2577, 5e-5, lg(RL, 543, '+0.2577 eV at 4x4x4'), f"{s(f9['8b']['E_scf_k4_Ry'])}, {s(f9['24d']['E_scf_k4_Ry'])}"),
        ('W site E(8b)-E(24d), k3 (eV)', f9['E8b_minus_E24d_eV']['E_relax_k3_Ry'], 0.2580, 5e-5, lg(RL, 543, '+0.2580 eV at 3x3x3'), f"{s(f9['8b']['E_relax_k3_Ry'])}, {s(f9['24d']['E_relax_k3_Ry'])}"),
        ('H-L dE_local(O30) k3 / k4 (eV)', f11['differences_eV']['dE_local_O30']['k3_g005'], 0.5578, 5e-5, lg(RL, 79, '| +0.5578 | +0.5321 | −25.7 meV | +0.5583 | +0.5 meV |'), f11['source']),
        ('H-L dE_dop k3 / k4 (eV)', f11['differences_eV']['dE_dop']['k3_g005'], 0.7259, 5e-5, lg(RL, 81, '| +0.7259 | +0.7226 | −3.4 meV | +0.7261 | +0.2 meV |'), f11['source']),
    ]
    for name, new, logd, tol, ref, srcs in rows:
        a(f'| {name} | {new:g} | {logd:g} ({ref}) | {st(new, logd, tol)} | COMPUTED | {srcs} |')
    a('')

    # ------------------------------------------------------------ 1 bulk
    a('## 1. Bulk In2O3 protocol (Figs. 1, 2)\n')
    a('**Convergence (Fig. 1).** 40-atom primitive bixbyite at the experimental a = 10.117 A, PROTOCOL.md criteria (fixed in advance): '
      'a further increase changes E by < 1 mRy/atom, P by < 1 kbar, the KS gap by < 10 meV.\n')
    a('| Run | E (Ry) | P (kbar) | KS gap on grid (eV) | dE vs ref (mRy/atom) | dP (kbar) | dgap (meV) | criteria | sym. ops | irr. k | source |')
    a('|---|---|---|---|---|---|---|---|---|---|---|')
    for r in f1['runs']:
        a(f"| {r['file']} | {v(r['E_Ry'])} | {v(r['P_kbar'])} | {v(r['gap_eV'])} | {r['dE_mRy_per_atom']} | {r['dP_kbar']} | {r['dgap_meV']} | "
          f"{'met' if r['meets_criteria_vs_ref'] else 'not met'} | {v(r['symops'])} | {v(r['nk'])} | {s(r['E_Ry'])} |")
    a(f"\nReference: 85 Ry for the cutoff series, 4x4x4 for the k series. Lowest cutoff meeting all criteria: **{f1['ecut_selected']} Ry** "
      f"(60 Ry fails E and P); lowest k grid: {f1['k_selected_lowest']}x{f1['k_selected_lowest']}x{f1['k_selected_lowest']} (3x3x3 kept, as recorded in PROTOCOL.md 7b). "
      f"All values reproduce PROTOCOL.md table 7b ({lg(PROT, 69, '-7573.24296524')}..{lg(PROT, 74, '-7573.35701116')}) to the printed digits. "
      f"Input cell: a = {f1['input_cell']['a_conv_A']} A, In-O {f1['input_cell']['In_O_distinct_A']} A ({f1['input_cell']['src']}), inside the 2.12-2.21 A window; 24 symmetry operations in every run. COMPUTED.\n")
    a(f"**vc-relax (Fig. 2).** {v(vr['bfgs'])} ({s(vr['bfgs'])}); final enthalpy {v(vr['final_enthalpy_Ry'])} Ry; last step P = {v(vr['last_step_P_kbar'])} kbar, "
      f"total force {v(vr['last_step_total_force_Ry_bohr'])} Ry/bohr; final SCF with the new G vectors P = {v(vr['final_scf_P_kbar'])} kbar ({s(vr['final_scf_P_kbar'])}). "
      f"**a = {v(vr['a_conv_A'])} A**, {vr['deviation_pct']:+.3f} % against experiment 10.117 A (LITERATURE, Marezio 1966), inside the expected PBE +1-2 %. "
      f"Primitive volume {v(vr['volume_prim_A3'])} A^3; {v(vr['symops_primitive'])} symmetry operations. "
      f"In-O first shell: 8b {sorted(set(vr['In_O_by_site_A']['8b'][0]))} A, 24d {sorted(set(vr['In_O_by_site_A']['24d'][0]))} A "
      f"(the 2.12-2.21 A window holds for the experimental lattice only; the PBE cell is 1.9 % larger). COMPUTED; matches {lg(PROT, 98, '2.215 A (8b) and 2.167 / 2.240 / 2.256 A (24d)')}.\n")
    a(f"**Band structure and gap (Fig. 2a).** bands_path.out, 80 k on Gamma-H-N-Gamma-P-H|P-N (labels found from the crystal coordinates: {bp['labels_at_index']}). "
      f"CBM {v(bp['CBM_eV'])} eV at Gamma ({s(bp['CBM_eV'])}); VBM {v(bp['VBM_eV'])} eV at k = {bp['VBM_k_cart_2pi_over_a']} 2pi/a on Gamma-H ({s(bp['VBM_eV'])}), "
      f"{bp['VBM_minus_VBGamma_meV']} meV above the VB at Gamma. Fundamental gap **{bp['Eg_fundamental_eV']} eV**, direct gap at Gamma {bp['Eg_direct_Gamma_eV']} eV. COMPUTED (PBE; experiment ~2.9 eV). "
      f"Minor discrepancy: PROTOCOL.md gives the VBM at k = (0, 0, 0.196) 2pi/a ({lg(PROT, 127, '(0, 0, 0.196) 2pi/a')}); the k point is (0, 0, 0.200) 2pi/a with the relaxed a "
      f"(3/15 of Gamma-H); 0.196 = 0.200 x 10.117/10.306 comes from converting with the unrelaxed a in analyze_path.py. No effect on any energy.\n")
    a('**CB effective mass (Fig. 2b).** bands_gamma.out (Gamma + 10 points per direction, |k| <= 0.153 1/A).\n')
    a('| Direction | m* parabolic, free intercept (m0) | m* parabolic, through origin (m0) | points (|k| <= 0.05) | Kane m* (m0) | Kane alpha (1/eV) | E(0.153) - CBM (eV) |')
    a('|---|---|---|---|---|---|---|')
    for d_ in ('[100]', '[110]', '[111]'):
        m = f2['mass'][d_]
        a(f"| {d_} | {m['m_parabolic_intercept_m0']} | {m['m_parabolic_origin_m0']} | {m['n_points_fit']} (max {m['k_max_fit_invA']}) | {m['m_kane_m0']} | {m['alpha_kane_per_eV']} | {m['E_at_kmax_eV']} |")
    a(f"\nSource {f2['mass']['[100]']['src'].split(' ..')[0]} and following blocks. Matches PROTOCOL.md 7d ({lg(PROT, 111, '0.1588 m0')}, {lg(PROT, 112, '0.1587 m0')}, {lg(PROT, 113, '0.1587 m0')}). "
      'The PBE mass is below experiment (0.18-0.21 m0, LITERATURE); TCAD keeps the LITERATURE 0.208 and adds only DFT increments (Sec. 4).\n')

    # ------------------------------------------------------------ 2 alignment
    b = f3['bulk']
    a('## 2. Bulk band-offset split dE_c / dE_v (Fig. 3)\n')
    a(f"The logged bulk constants (E_v - <V> = 3.9098, E_c - <V> = 4.7985 eV, {lg(RL, 349, 'E_v - <V> = 3.9098 eV and E_c - <V> = 4.7985 eV')}) came from bulk_v11.cube, which was deleted on 2026-10-06; "
      f"the bulk save `bulk_In2O3_protocol/tmp/vcr.save` is empty, and C: has < 1 GB free, so pp.x could not be re-run. **Independent route used:** the cell mean of the pp.x plot_num 11 potential "
      f"(V_bare + V_H) is QE's G = 0 term of the local pseudopotential, (4 pi/Omega) sum_atoms int_0^10 bohr r (r V_loc + 2Z) dr, because V_H has no G = 0 component. "
      f"This is computed from the UPF PP_LOCAL data (QE's msh and Simpson rule) and **validated on all ten slab planar averages** (mean of each `*_avg.dat` against the same formula for the slab cell): "
      f"differences {sorted({x['diff_meV'] for x in f3['validation']})} meV (Fig. 3b). Bulk: <V> = **{v(b['Vmean_eV'])} eV** "
      f"(logged 4.1687), E_v - <V> = **{b['Ev_minus_V_eV']}**, E_c - <V> = **{b['Ec_minus_V_eV']}** eV (E_v, E_c from {s(b['E_v_eV'])}, {s(b['E_c_eV'])}). The logged constants are confirmed. COMPUTED.\n")
    a('| Slab (job) | window | Vbar(centre) (eV) | plateau spread +-a/8 (meV) | dEc (eV) | dEv (eV) | logged |')
    a('|---|---|---|---|---|---|---|')
    logged = {('slab2_relax_c2', 'a/2'): f"+0.281 / -0.054 ({lg(RL, 360, '+0.281 | -0.054')})", ('slab2_relax_c2', 'a/2*a/4'): f"+0.287 / -0.049 ({lg(RL, 361, '+0.287 | -0.049')})",
              ('slab2_relax_c2', 'a/4'): f"+0.157 / -0.179, rejected ({lg(RL, 353, 'dEc +0.157, dEv -0.179 eV')})", ('slab1r_final_cpu', 'a/2'): f"+0.819 / -0.081 ({lg(RL, 362, '+0.819 | -0.081')})"}
    for job, t in f3['two_step'].items():
        for w in ('a/2', 'a/2*a/4', 'a/4'):
            x = t[w]
            a(f"| {job} | {w} | {x['Vbar_centre_eV']} | {x['plateau_spread_meV']} | {x['dEc_eV']:+.4f} | {x['dEv_eV']:+.4f} | {logged.get((job, w), '-')} |")
    a(f"\nSource of the slab side: `{f3['two_step']['slab2_relax_c2']['avg_src']}` and `{s(f3['two_step']['slab2_relax_c2']['CBM_eV'])}` (2 nm). The 2 nm CPU rerun (slab2r_pdos_cpu, QE 7.5) gives the same split within 0.5 meV. "
      f"The 1 nm and 0.75 nm films have no bulk-like interior (spread {f3['two_step']['slab1r_final_cpu']['a/2']['plateau_spread_meV']} and {f3['two_step']['slabL2_relax_v2']['a/2']['plateau_spread_meV']} meV), "
      'so their split uses the same-termination EA route (Sec. 3). COMPUTED.\n')

    # ------------------------------------------------------------ 3 slabs
    a('## 3. Crystalline In2O3(001) slabs (Figs. 4, 5, 8, 12)\n')
    a('**Vacuum test, unrelaxed 1 nm slab (Fig. 4).**\n')
    a('| Vacuum (A) | c (A) | gap (eV) | E_vac (eV) | vacuum flatness (meV) | EA (eV) | IP (eV) | dEA / dIP vs 25 A (meV) | SCF iter. | source | logged |')
    a('|---|---|---|---|---|---|---|---|---|---|---|')
    lv = {15: lg(RL, 583, '| 15 A | 0.9586 | 3.4331 | 4.3917 | 46 |'), 25: lg(RL, 584, '| 25 A | 0.9586 | 3.4332 | 4.3918 | 64 |'), 35: lg(RL, 585, '| 35 A | 0.9586 | 3.4332 | 4.3918 | 77 |')}
    for r in f4['runs']:
        a(f"| {r['vacuum_nominal_A']} | {r['cell_c_A']} | {r['gap_eV']} | {v(r['E_vac_eV'])} | {r['E_vac_spread_meV']} | {r['EA_eV']} | {r['IP_eV']} | {r['dEA_vs_25_meV']} / {r['dIP_vs_25_meV']} | "
          f"{v(r['scf_iterations'])} | {s(r['VBM_eV'])} | match {lv[r['vacuum_nominal_A']]} |")
    a(f"\nCriterion 6 (< 10 meV) is met by > 50x. The geometry is unrelaxed (total force {v(f4['runs'][0]['total_force_Ry_bohr'])} Ry/bohr), so these gaps are not confinement values. COMPUTED.\n")
    a('**Relaxed slab series (Fig. 5).** dEg = gap - 0.8887 eV (bulk fundamental). dEc: 2 nm two-step a/2; thinner films dEc(t) = dEc(2 nm) + EA(2 nm) - EA(t); dEv = dEc - dEg. '
      'Vacuum level = mean of the planar average > 5 A from every atom plane.\n')
    a('| Label | job | H-H (nm) | O-O (nm) | in-plane a, b (A) | composition | sym. ops | gap (eV) | dEg (eV) | EA (eV) | IP (eV) | dEc (eV) | dEv (eV) | CB share | m* [100] / [110] (m0) | dm* (m0) | E21 (eV) |')
    a('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for lab, r in S.items():
        m = r['mass']
        a(f"| {lab} | {r['job']} | {v(r['thickness_HH_nm'])} | {r['thickness_OO_nm']} | {r['inplane_A']} | {r['composition']} | {v(r['symops'])} | {r['gap_eV']} | {r['dEg_eV']} | "
          f"{r['EA_eV']} | {r['IP_eV']} | {r['dEc_eV']:+.4f} | {r['dEv_eV']:+.4f} | {r['CB_share']} | {m['[100]']['m_intercept_m0']} / {m['[110]']['m_intercept_m0']} | {r['dm_m0']} | {v(m['E21_Gamma_eV'])} |")
    a('\nSources (gap line, E_vac file, bands.out): ' + '; '.join(f"{lab}: {s(r['CBM_eV'])}, {s(r['E_vac_eV'])}, {r['mass']['src']}" for lab, r in S.items()) + '. COMPUTED.\n')
    a('| Label | relaxation (vcrelax.out) | final enthalpy (Ry) | max force component at convergence (Ry/bohr) | total force (Ry/bohr) | O bonded to H / O | In-O CN |')
    a('|---|---|---|---|---|---|---|')
    for lab, r in S.items():
        rx = r['relax']
        a(f"| {lab} | {v(rx['bfgs'])} ({s(rx['bfgs'])}) | {v(rx['final_enthalpy_Ry'])} | {v(rx['max_force_component_Ry_bohr'])} ({s(rx['max_force_component_Ry_bohr'])}) | {v(rx['total_force_Ry_bohr'])} | {r['O_bonded_to_H']} / {r['O_total']} | {r['In_CN_hist']} |")
    a(f"\nAll four relaxations meet forc_conv_thr = 1e-3 Ry/bohr per component (the logged 'residual force 0.0061 / 0.0072' are norms over all atoms, "
      f"{lg(RL, 529, 'is the norm over all 96 atoms')}). Fig. 12 shows the BFGS histories. "
      f"The 0.51 nm film is exactly In8(OH)24 after relaxation (all {S['0.51']['O_total']} O bonded to H, every In six-fold): the 'In(OH)3-like layer' of C021 ({lg(LEDGER, 121, 'In(OH)3-like layer')}) is confirmed; it stays outside the recipe and out of every law. COMPUTED.\n")
    s1, s2 = S['1.0'], S['2.0']
    a(f"**Cross-checks.** 2 nm: GPU final SCF (QE 7.3.1) gap {S['2.0']['gap_eV']} eV; CPU reruns slab2r_pdos_cpu {v(f5['extra']['2.0:slab2r_pdos_cpu']['gap_eV'])} and "
      f"slab2r_final_cpu {v(f5['extra']['2.0:slab2r_final_cpu_checkpoint']['gap_eV'])} eV ({s(f5['extra']['2.0:slab2r_final_cpu_checkpoint']['gap_eV'])}; logged {lg(RL, 410, 'a gap of 1.2239 eV')}). "
      f"1 nm: slab1_relax_gpu (QE 7.3.1) gap {v(f5['extra']['1.0:slab1_relax_gpu']['gap_eV'])} eV and m* {f5['extra']['1.0:slab1_relax_gpu']['mass_100_intercept_m0']} m0, "
      f"identical to the CPU slab1r_final_cpu values. 1 -> 2 nm with the same termination: EA(2) - EA(1) = {f5['partition_1_to_2']['EA2_minus_EA1']:+.4f} eV, "
      f"IP(1) - IP(2) = {f5['partition_1_to_2']['IP1_minus_IP2']:+.4f} eV, dEg(1) - dEg(2) = {f5['partition_1_to_2']['dEg1_minus_dEg2']:+.4f} eV.\n")
    a(f"**Surface character of the band edges (Fig. 8; projwfc, k-weighted; plain k mean in brackets).**\n")
    a('| Slab | job | OH-group atoms / all | VB top band | VB top: OH share | VB top: element | CB bottom: OH share | CB bottom: element | VB top - 20: OH share |')
    a('|---|---|---|---|---|---|---|---|---|')
    for lab, r in f8.items():
        if lab == 'pdos_2nm':
            continue
        a(f"| {lab} | {r['job']} | {r['surface_OH_number_share']} | {r['VB_top_band']} | {r['VB_top']['kweighted']['OH_share']} ({r['VB_top']['kmean']['OH_share']}) | {r['VB_top']['kweighted']['by_element']} | "
          f"{r['CB_bottom']['kweighted']['OH_share']} ({r['CB_bottom']['kmean']['OH_share']}) | {r['CB_bottom']['kweighted']['by_element']} | {r['VB_top_minus_20']['kweighted']['OH_share']} ({r['VB_top_minus_20']['kmean']['OH_share']}) |")
    r2 = f8['2.0']
    a(f"\n2 nm z profiles (8 slices): VB top {r2['VB_top']['kweighted']['z_profile_8']}, CB bottom {r2['CB_bottom']['kweighted']['z_profile_8']} ({r2['VB_top']['src']}). "
      f"The logged surface check ({lg(RL, 335, '0.2 % (these atoms are 27.3 % of all atoms)')}, {lg(RL, 336, '| CBM (band 665) | 1.4 % |')}, {lg(RL, 337, '| 14 % |')}) "
      f"used the plain k mean: 0.2 / 1.4 / 14 % reproduce as {r2['VB_top']['kmean']['OH_share']*100:.1f} / {r2['CB_bottom']['kmean']['OH_share']*100:.1f} / {r2['VB_top_minus_20']['kmean']['OH_share']*100:.1f} %; "
      f"with k weights they are {r2['VB_top']['kweighted']['OH_share']*100:.1f} / {r2['CB_bottom']['kweighted']['OH_share']*100:.1f} / {r2['VB_top_minus_20']['kweighted']['OH_share']*100:.1f} %. "
      f"Both 2 nm band edges are interior, bulk-like states. At <= 1 nm (and in the 2 nm W slab) the VB top is an OH surface state; the CB bottom is never surface-dominated "
      f"(largest OH share {max(f8[k]['CB_bottom']['kweighted']['OH_share'] for k in ('0.75', '1.0 W (proxy)', '2.0', '2.0 W')):.2f} outside the 0.51 nm In(OH)3 layer). "
      'The pure 1 nm slab has no projwfc run; its W twin is the proxy (bands 311/312). COMPUTED.\n')
    a(f"**New finding: the 0.75 nm slab is polar.** slabL2_relax_v2 has {v(S['0.75']['symops'])} symmetry operations (no inversion; all other slabs 8 with inversion) and no dipole correction. "
      f"Its vacuum planar average is not flat: slope {S['0.75']['vacuum_ramp_slope_meV_per_A']} meV/A, {S['0.75']['vacuum_ramp_over_window_meV']} meV across the > 5 A window and "
      f"~{S['0.75']['vacuum_ramp_over_gap_meV']} meV across the whole vacuum gap (source {s(S['0.75']['E_vac_eV'])}); the other slabs are flat to {max(S[k]['E_vac_spread_meV'] for k in ('0.51', '1.0', '2.0'))} meV. "
      f"The earlier read-out recorded only a 27 meV left/right asymmetry ({lg(DFTIN, 449, 'vacuum asymmetry 27 meV')}). EA(0.75) and therefore dEc(0.695 nm) = {S['0.75']['dEc_eV']} eV carry an "
      f"uncertainty of about +-{f6['dEc_0p75_dipole_sensitivity']['half_ramp_eV']} eV (half the vacuum ramp). This is an ASSUMED vacuum-reference-choice sensitivity, not a bound on a dipole-corrected dEc: the periodic artificial field "
      f"also changes the self-consistent density and eigenvalues (Bengtsson, PRB 59, 12301, 1999). dEg is independent of the vacuum-reference choice; its sensitivity to the "
      f"artificial field remains untested. COMPUTED (ramp); the +- value is ASSUMED. [Wording revised after the Codex review of 2026-10-13.]\n")

    # ------------------------------------------------------------ 4 laws
    a('## 4. Confinement laws used in TCAD, HSE ratio (Figs. 6, 7)\n')
    a(f"**HSE06 check (Fig. 7).** NC PBE: bulk {v(f7['runs']['nc_pbe_bulk_e80']['gap_eV'])}, 1 nm slab {v(f7['runs']['nc_pbe_slab1_e80']['gap_eV'])} eV -> dEg(PBE) {f7['dEg_PBE_NC_eV']} eV. "
      f"HSE06: bulk {v(f7['runs']['nc_hse_bulk_e80']['gap_eV'])} (q 1), {v(f7['runs']['nc_hse_bulk_q3_f160_e80']['gap_eV'])} (q 3x3x3), 1 nm slab {v(f7['runs']['nc_hse_slab1_f160_e80']['gap_eV'])} eV (q 1). "
      f"**r = {f7['r_q1']}** (q 1), **{f7['r_q3_worst']}** worst case (q 3 bulk, slab at q 1). ecutfock 160 vs default: {f7['ecutfock_bulk_160_vs_default_meV']} meV; q3 - q1 bulk gap {f7['q3_minus_q1_bulk_gap_meV']} meV. "
      f"Two runs are unfinished and excluded: nc_hse_bulk_q3_e80 (no output) and nc_hse_slab1_e80 (only the PBE pre-step; its 'gap' equals the PBE value). "
      f"Matches {lg(RL, 469, '| PBE | 0.9204 eV | 1.8068 eV | 0.8864 eV |')}, {lg(RL, 470, '| HSE06 (q = 1, ecutfock 160 Ry) | 2.1080 eV | 3.0475 eV | 0.9395 eV |')}. "
      f"HSE-corrected 1 nm dEg = {S['1.0']['dEg_eV']} x r = {S['1.0']['dEg_eV'] * f7['r_q1']:.3f}-{S['1.0']['dEg_eV'] * f7['r_q3_worst']:.3f} eV (C020 {lg(LEDGER, 115, '0.95-1.00 eV HSE-corrected')}): match. COMPUTED; the transfer of r to other thicknesses is ASSUMED.\n")
    a('**Laws (Fig. 6).** Points: H-H thickness and COMPUTED dEg, dEc, dm* of the 0.75, 1 and 2 nm films (Sec. 3); the 0.51 nm In(OH)3 layer is excluded.\n')
    a('| Law | configured a, p (yaml) | re-fit from re-derived points | rel. residuals of re-fit | V2 2-point re-fit from rounded log values | V2 form from re-derived points |')
    a('|---|---|---|---|---|---|')
    for k, nm in (('dEg', 'dEg = a t^-p'), ('dEc', 'dEc = a t^-p'), ('dm', 'dm* = b t^-q')):
        c3, c2, rf = f6['config']['V3'][k], f6['config']['V2'][k], f6['refit'][k]
        a(f"| {nm} | V3/C10: {c3['a']}, {c3['p']} ({c3['src'][0]}); V2: {c2['a']}, {c2['p']} ({c2['src'][0]}) | {rf['fit3_rederived']['a']}, {rf['fit3_rederived']['p']} | "
          f"{rf['fit3_rederived']['rel_residuals']} | {rf['V2_from_rounded_log_values']['a']}, {rf['V2_from_rounded_log_values']['p']} | {rf['V2_form_from_rederived_points']['a']}, {rf['V2_form_from_rederived_points']['p']} |")
    a('\nLabel: FITTED (to the COMPUTED points; no device data). The V2 laws are reproduced exactly from the rounded logged inputs; the V3/C10 fit3 parameters are reproduced to '
      '< 0.3 % (differences from the 0.1-0.3 meV EA-window and 0.0002 m0 bulk-mass reference choices of the earlier extraction, which used 0.159 m0 from a joint fit of all directions).\n')
    a('**Deck check.** ATLAS MATERIAL statements of the decks against the laws (bulk anchors Eg 3.05 eV, chi 4.3 eV, m* 0.208 m0: LITERATURE; T = 300 K):\n')
    a('| Deck | run (device.in line) | EG300 deck / from config law / from re-derived law | AFFINITY deck / config / re-derived | m* deck / config | NC300 deck / config / re-derived (cm^-3) |')
    a('|---|---|---|---|---|---|')
    for k, d in f6['decks'].items():
        dk, c, r_ = d['deck'], d['from_config_law'], d['from_rederived_law']
        a(f"| {k} | {d['run']} ({dk['eg300']['src'].split(':')[-1]}) | {v(dk['eg300'])} / {c['eg300']} / {r_['eg300']} | {v(dk['affinity'])} / {c['affinity']} / {r_['affinity']} | "
          f"{v(dk['mstar'])} / {c['mstar']} | {v(dk['nc300']):.5e} / {c['nc300']:.5e} ({c['nc_form']}) / {r_['nc300']:.5e} |")
    a('\nEvery deck value is reproduced by its configured law to the printed digits (EG300, AFFINITY within 0.000 meV; NC300 within 4e-5 relative). '
      'The V2 2 nm deck values EG300 3.3805 / AFFINITY 4.0232 eV and the C10 values 3.37725 / 4.01839 (2.0 nm), 3.12236 / 4.23784 (6.3 nm), 3.07735 / 4.27653 (13.2 nm) '
      f"are confirmed; the re-derived laws would move them by at most {max(abs(d['rederived_minus_deck']['eg300_meV']) for d in f6['decks'].values()):.2f} meV (EG300), "
      f"{max(abs(d['rederived_minus_deck']['affinity_meV']) for d in f6['decks'].values()):.2f} meV (AFFINITY) and {100 * max(abs(d['rederived_minus_deck']['nc300_rel']) for d in f6['decks'].values()):.2f} % (NC300). "
      f"The C10 2.0 nm NC300 is the quasi-2D N2D/t; the second subband (E21 = {v(S['2.0']['mass']['E21_Gamma_eV'])} eV) would add a factor "
      f"1 + exp(-E21/kT) = 1 + {math.exp(-v(S['2.0']['mass']['E21_Gamma_eV']) / (q.KB * 300)):.0e}, i.e. nothing.\n")
    sens = f6['dEc_0p75_dipole_sensitivity']['fits']
    lo, hi = sens[min(sens)], sens[max(sens)]
    rng = {k: f'{min(hi[k], lo[k])}-{max(hi[k], lo[k])}' for k in ('2.0', '6.3', '13.2')}
    f2a, f2p = f6['refit']['dEc']['fit2_HH_1and2nm']['a'], f6['refit']['dEc']['fit2_HH_1and2nm']['p']
    f2v = ' / '.join(f'{f2a * tt ** -f2p:.4f}' for tt in (2.0, 6.3, 13.2))
    a(f"**Extrapolation and dipole sensitivity of dEc.** The fit3 dEc law has residuals up to 9 % on three points; at 6.3 and 13.2 nm it is an extrapolation. "
      f"Moving the polar 0.75 nm point by +-{f6['dEc_0p75_dipole_sensitivity']['half_ramp_eV']} eV gives dEc(2.0) = {rng['2.0']}, dEc(6.3) = {rng['6.3']}, "
      f"dEc(13.2) = {rng['13.2']} eV (configured fit3: 0.2816 / 0.0622 / 0.0235). The configured S6 extrapolation band 0.046-0.062 eV at 6.3 nm "
      f"({lg(q.QE.parent / 'config' / 'iwo_material_model_v3.yaml', 159, 'dft_inputs.json laws.dEc_eV.fit3')}) does not include this reference-choice sensitivity (its upper end reaches 0.075 eV). "
      f"Codex review (2026-10-13): exclude the polar point from any new primary dEc fit until a dipole-corrected SCF exists; the available two-point diagnostic "
      f"(H-H 0.930 and 1.962 nm only) is dEc = {f2a} t^-{f2p} -> {f2v} eV at 2.0 / 6.3 / 13.2 nm (FITTED, DIAGNOSTIC ONLY). "
      f"The historical C10 fit3 results stay as run, with this caveat; changing the frozen law or the S6 range needs a result-informed amendment. "
      f"HSE scaling (x{f7['r_q1']}..{f7['r_q3_worst']}, ASSUMED transfer): fit3 dEg(2.0) {f6['hse_scaled_fit3_at']['2.0']['dEg']}, dEc(2.0) {f6['hse_scaled_fit3_at']['2.0']['dEc']} eV (PBE, x r1, x r3).\n")

    # ------------------------------------------------------------ 5 W bulk
    a('## 5. W in bulk In2O3: 8b vs 24d and PDOS (Fig. 9)\n')
    a('| Quantity | W on 8b | W on 24d | source |')
    a('|---|---|---|---|')
    b8, b24 = f9['8b'], f9['24d']
    for nm, key in (('E relax, 3x3x3, MV 0.01 (Ry)', 'E_relax_k3_Ry'), ('E SCF, 4x4x4 (Ry)', 'E_scf_k4_Ry'), ('E spin-polarised, 3x3x3 (Ry)', 'E_spin_k3_Ry'),
                    ('total / absolute magnetisation (muB/cell)', None)):
        if key:
            a(f"| {nm} | {v(b8[key])} | {v(b24[key])} | {s(b8[key])}; {s(b24[key])} |")
        else:
            a(f"| {nm} | {v(b8['M_total_muB'])} / {v(b8['M_abs_muB'])} | {v(b24['M_total_muB'])} / {v(b24['M_abs_muB'])} | {s(b8['M_total_muB'])}; {s(b24['M_total_muB'])} |")
    a(f"| E(spin) - E(no spin), 3x3x3 (meV) | {b8['E_spin_minus_nospin_meV']} | {b24['E_spin_minus_nospin_meV']} | same lines |")
    a(f"| W-O (A) | {b8['W_O_A']['value']} | {b24['W_O_A']['value']} (mean {b24['W_O_mean_A']}) | {s(b8['W_O_A'])}; {s(b24['W_O_A'])} |")
    a(f"| irreducible k (k4 / spin k3); sym. ops (k4) | {b8['nks']['k4']} / {b8['nks']['spin_k3']}; {v(b8['symops_k4'])} | {b24['nks']['k4']} / {b24['nks']['spin_k3']}; {v(b24['symops_k4'])} | scf_k4.out, spin_k3.out |")
    for nm, key in (('E_F (eV)', 'E_F_eV'),):
        a(f"| {nm} | {v(b8['filling'][key])} | {v(b24['filling'][key])} | {s(b8['filling'][key])}; {s(b24['filling'][key])} |")
    for nm, key in (('electrons above the VB top (of 3)', 'electrons_above_VB_top'), ('W-5d-projected electrons (of 3)', 'W5d_projected_electrons'),
                    ('gap VB top (351) -> host CB (352) at Gamma (eV)', 'gap_VBtop_to_hostCB_Gamma_eV'), ('E_F - host CB bottom at Gamma (eV)', 'EF_minus_hostCB_Gamma_eV'),
                    ('first W-5d-rich band (W d >= 0.30 at Gamma)', 'W_rich_band_Gamma'), ('W-rich band - host CB at Gamma (eV)', 'W_rich_minus_hostCB_Gamma_eV'),
                    ('W-rich band - E_F at Gamma (eV)', 'W_rich_minus_EF_Gamma_eV')):
        a(f"| {nm} | {b8['filling'][key]} | {b24['filling'][key]} | {b8['filling'].get('projwfc', '')}; {b24['filling'].get('projwfc', '')} |")
    a(f"\n**Site preference: E(8b) - E(24d) = {f9['E8b_minus_E24d_eV']['E_relax_k3_Ry']} eV (k3), {f9['E8b_minus_E24d_eV']['E_scf_k4_Ry']} eV (k4), {f9['E8b_minus_E24d_eV']['E_spin_k3_Ry']} eV (spin, k3)**; "
      f"k3 -> k4 change {f9['k3_to_k4_change_meV']} meV (criterion 10 meV). Occupation ratio 24d : 8b at 600 K = 3 exp(dE/kT) = {f9['occupation_ratio_24d_to_8b_600K']:.0f} (k4 value, kT = 51.7 meV); "
      f"the log's '430:1' ({lg(RL, 545, 'about 430:1')}) used kT = 52 meV: rounding only. W-O agree with {lg(RL, 538, '| W-O (A) | 6 x 1.972 | 1.892 x 2, 1.902 x 2, 2.152 x 2 (mean 1.982) |')}. "
      f"Electron counts: MV occupations recomputed from the eigenvalues and the printed occupations both sum to 705 (max difference {b24['filling']['max_abs_MV_minus_printed_occ']:.1e}). COMPUTED.\n")
    a('Band characters at Gamma (projwfc; W d, In s, O p weights; electrons per band from the k-weighted occupations):\n')
    a('| Cell | band | E(Gamma) - E_F (eV) | W 5d | In 5s | O 2p | O 2s | W 5d k-avg | width (eV) | electrons | source |')
    a('|---|---|---|---|---|---|---|---|---|---|---|')
    for site in ('24d', '8b'):
        for n, bb in f9[site]['filling']['bands'].items():
            if int(n) < 351 or int(n) > 356:
                continue
            a(f"| {site} | {n} | {bb['E_Gamma_minus_EF_eV']} | {bb['Wd_Gamma']} | {bb['Ins_Gamma']} | {bb['Op_Gamma']} | {bb['Os_Gamma']} | {bb['Wd_kavg']} | {bb['width_eV']} | {bb['electrons']} | {bb['src']} |")
    a(f"\nBand 351 is O 2p (VB top) and band 352 the host CB bottom (In 5s 0.67 / 0.66, O 2s 0.27), as in the 2026-10-05 correction ({lg(RL, 399, 'Band 351 is the VB top and band 352 the host CB (In 5s 0.67)')}). "
      f"The W-5d-rich bands 353-355 carry 0.54 / 0.48 / 0.30 (24d) and 0.50 / 0.50 / 0.58 (8b) W d at Gamma (logged {lg(RL, 506, '0.55 / 0.48 / 0.30')}, {lg(RL, 507, '0.50 / 0.50 / 0.58')}). "
      f"**Electron partition (analysis pending until now):** of the 3 electrons per W, {b24['filling']['bands']['352']['electrons']} (24d) / {b8['filling']['bands']['352']['electrons']} (8b) sit in band 352, "
      f"{b24['filling']['bands']['353']['electrons']} / {b8['filling']['bands']['353']['electrons']} in band 353; the W-5d-projected count is {b24['filling']['W5d_projected_electrons']} / {b8['filling']['W5d_projected_electrons']}. "
      f"E_F lies in the W-rich band (W-rich band - E_F at Gamma {b24['filling']['W_rich_minus_EF_Gamma_eV']} / {b8['filling']['W_rich_minus_EF_Gamma_eV']} eV), {b24['filling']['EF_minus_hostCB_Gamma_eV']} / {b8['filling']['EF_minus_hostCB_Gamma_eV']} eV above the host CB bottom: "
      'in these cells (3.1 % W, 3 e per 1065 A^3 = 2.8e21 cm^-3) the W-5d-rich band lies at E_F at Gamma (COMPUTED, PBE, MV 0.01 Ry, k 4x4x4, no spin); that this placement is caused by the band filling '
      '(pinning) is an interpretation that needs a density series. The W-5d counts are projections of the occupied states above the VB top, not the total W atomic charge or a uniquely '
      'defined trapped-electron fraction; the per-band electron numbers use the MV smearing weights, which are numerical.\n')
    a('Discrepancy with the log (already corrected there, text left in place): the 2026-09-30 entry calls band 352 the VB top ' + f"({lg(RL, 505, 'band 352 (VB top) has 1.5 % W weight')}); "
      'projwfc shows band 352 is the host CB bottom (W d 0.00 at Gamma, 0.10 k-averaged) and band 351 the O 2p VB top.\n')

    # ------------------------------------------------------------ 6 W slabs
    a('## 6. W in the 1 nm and 2 nm slabs (Fig. 10)\n')
    a('| Quantity | 1 nm W slab | 2 nm W slab | source |')
    a('|---|---|---|---|')
    w1, w2 = f10['1 nm'], f10['2 nm']
    a(f"| relaxation | {v(w1['relax']['bfgs'])}, E = {v(w1['relax']['E_final_Ry'])} Ry | {v(w2['relax']['bfgs'])}, E = {v(w2['relax']['E_final_Ry'])} Ry | {s(w1['relax']['bfgs'])}; {s(w2['relax']['bfgs'])} |")
    a(f"| final SCF E - relax E (Ry); SCF iterations | {w1['E_scf_minus_relax_Ry']}; {v(w1['scf_iterations'])} | {w2['E_scf_minus_relax_Ry']}; {v(w2['scf_iterations'])} | {s(w1['E_scf_Ry'])}; {s(w2['E_scf_Ry'])} |")
    a(f"| W-O (A) | {w1['W_O_A']['value']} | {w2['W_O_A']['value']} | {s(w1['W_O_A'])}; {s(w2['W_O_A'])} |")
    a(f"| max displacement / W displacement in the relax (A) | {w1['max_displacement_A']} / {w1['W_displacement_A']} | {w2['max_displacement_A']} / {w2['W_displacement_A']} | relax.in vs final coordinates |")
    a(f"| E_F (eV) | {v(w1['filling']['E_F_eV'])} | {v(w2['filling']['E_F_eV'])} | {s(w1['filling']['E_F_eV'])}; {s(w2['filling']['E_F_eV'])} |")
    for nm, key in (('electrons above the VB top', 'electrons_above_VB_top'), ('W-5d-projected electrons', 'W5d_projected_electrons'),
                    ('gap VB top -> host CB at Gamma (eV)', 'gap_VBtop_to_hostCB_Gamma_eV'), ('E_F - host CB at Gamma (eV)', 'EF_minus_hostCB_Gamma_eV'),
                    ('first W-rich band; - host CB; - E_F (eV)', None)):
        if key:
            a(f"| {nm} | {w1['filling'][key]} | {w2['filling'][key]} | projwfc + scf.out |")
        else:
            a(f"| {nm} | {w1['filling']['W_rich_band_Gamma']}; {w1['filling']['W_rich_minus_hostCB_Gamma_eV']}; {w1['filling']['W_rich_minus_EF_Gamma_eV']} | "
              f"{w2['filling']['W_rich_band_Gamma']}; {w2['filling']['W_rich_minus_hostCB_Gamma_eV']}; {w2['filling']['W_rich_minus_EF_Gamma_eV']} | projwfc |")
    a(f"| E_vac (eV); vacuum flatness (meV) | {v(w1['vacuum']['E_vac_eV'])}; {w1['vacuum']['spread_meV']} | {v(w2['vacuum']['E_vac_eV'])}; {w2['vacuum']['spread_meV']} | {s(w1['vacuum']['E_vac_eV'])}; {s(w2['vacuum']['E_vac_eV'])} |")
    a(f"| EA (host CB) / IP (VB top) / work function (eV) | {w1['EA_hostCB_eV']} / {w1['IP_VBtop_eV']} / {w1['work_function_eV']} | {w2['EA_hostCB_eV']} / {w2['IP_VBtop_eV']} / {w2['work_function_eV']} | E_vac and projwfc energies |")
    a(f"| pure twin gap / EA / IP (eV) | {v(w1['pure_twin']['gap_eV'])} / {w1['pure_twin']['EA_eV']} / {w1['pure_twin']['IP_eV']} | {v(w2['pure_twin']['gap_eV'])} / {w2['pure_twin']['EA_eV']} / {w2['pure_twin']['IP_eV']} | {w1['pure_twin']['job']}; {w2['pure_twin']['job']} |")
    a(f"| W effect: dGap / dEA / dIP (eV) | {w1['W_effect']['dGap_eV']} / {w1['W_effect']['dEA_eV']} / {w1['W_effect']['dIP_eV']} | {w2['W_effect']['dGap_eV']} / {w2['W_effect']['dEA_eV']} / {w2['W_effect']['dIP_eV']} | difference |")
    a(f"| donated electrons per area / per H-H volume | {w1['donated_sheet_density_cm2']:.3e} cm^-2 / {w1['donated_density_cm3_HH']:.3e} cm^-3 | {w2['donated_sheet_density_cm2']:.3e} / {w2['donated_density_cm3_HH']:.3e} | 3 e per cell |")
    a('\n| Slab | band | E(Gamma) - E_F (eV) | W 5d | In 5s | O 2p | O 2s | W 5d k-avg | width (eV) | electrons | source |')
    a('|---|---|---|---|---|---|---|---|---|---|---|')
    for lab, vb in (('1 nm', 311), ('2 nm', 663)):
        for n, bb in f10[lab]['filling']['bands'].items():
            if int(n) < vb or int(n) > vb + 5:
                continue
            a(f"| {lab} | {n} | {bb['E_Gamma_minus_EF_eV']} | {bb['Wd_Gamma']} | {bb['Ins_Gamma']} | {bb['Op_Gamma']} | {bb['Os_Gamma']} | {bb['Wd_kavg']} | {bb['width_eV']} | {bb['electrons']} | {bb['src']} |")
    a(f"\n1 nm: everything logged on 2026-10-05 is reproduced ({lg(RL, 393, 'Band 311 is O 2p at -2.366 eV')}; {lg(RL, 397, 'Gap (VB top to CB bottom) 1.719 eV (pure 1.789). EA 4.069, IP 5.789 eV')}; "
      f"{lg(RL, 485, '1.880 x 2, 1.907 x 2, 2.212 x 2 A')}). 2 nm (analysis pending until now): W-O {w2['W_O_A']['value'][::2]} A, mean {w2['W_O_mean_A']} (logged {lg(RL, 382, 'W-O 1.866, 1.874, 2.19 A, each twice, mean 1.977 A (W6+)')}); "
      f"E_F - host CB {w2['filling']['EF_minus_hostCB_Gamma_eV']} eV ({lg(RL, 405, 'Band 664 (host CB1) is 1.238 eV below E_F at Gamma')}); bands 664 / 665 / 666 hold "
      f"{w2['filling']['bands']['664']['electrons']} / {w2['filling']['bands']['665']['electrons']} / {w2['filling']['bands']['666']['electrons']} e; band 666 (W d {w2['filling']['bands']['666']['Wd_Gamma']} at Gamma) "
      f"lies 0.069 eV or more above E_F at every k (min over the 4 k points; logged {lg(RL, 406, 'at least 0.069 eV above E_F')}), but the MV smearing (0.136 eV) still puts {w2['filling']['bands']['666']['electrons']} e in it, so 'just empty' holds for the band, not for the occupation. "
      f"Only {w2['filling']['W5d_projected_electrons']} of 3 electrons project on W 5d in the 2 nm slab ({w1['filling']['W5d_projected_electrons']} at 1 nm). "
      f"The 2 nm W slab's VB top (663) is an OH surface state (OH share {f8['2.0 W']['VB_top']['kweighted']['OH_share']}), unlike the pure 2 nm slab. COMPUTED.\n")
    a('**W level against C022.** The W-5d-rich level lies ' + f"{w1['filling']['W_rich_minus_hostCB_Gamma_eV']} (1 nm), {w2['filling']['W_rich_minus_hostCB_Gamma_eV']} (2 nm), "
      f"{b24['filling']['W_rich_minus_hostCB_Gamma_eV']} (bulk 24d), {b8['filling']['W_rich_minus_hostCB_Gamma_eV']} (bulk 8b) eV above the host CB bottom at Gamma, matching '1.2-1.8 eV' "
      f"({lg(LEDGER, 127, 'resonant ~1.2-1.8 eV above the CB bottom')}). In every cell this level lies roughly 0.1 eV or less from E_F at Gamma (2 nm: +0.103 eV; this does not describe the whole dispersive band), and E_F is 1.2-1.8 eV into the host CB; "
      'each cell holds 1.4e21-3e21 donated electrons per cm^3. The near-E_F placement is COMPUTED; pinning by the filling is an interpretation. The level position is computed only at this filling; '
      'that it stays above E_C at device densities (E_F below E_C) is INFERRED, not computed (PBE, no HSE for W cells, no lower-density cell). '
      'Suggested caveat for C022 (accepted by Codex with these refinements).\n')

    # ------------------------------------------------------------ 7 H-L
    a('## 7. H-L crystalline vacancy cells and A20(ii) (Fig. 11)\n')
    a(f"Re-derived with an independent parser from `{f11['source']}` (sha256 570ece79..., unchanged; checked against SHA256SUMS). Per-cell energies (Ry) and line numbers:\n")
    a('| Cell | E k3 G0.005 (relax) | E k4 G0.005 (FINAL) | E k3 G0.002 (A20(ii)) | -TS k3 / k4 / k3-G0.002 (Ry) | irr. k k3 / k4 | k3->k4 (meV) | G0.002-G0.005 (meV) | E0 estimate shift (meV) |')
    a('|---|---|---|---|---|---|---|---|---|')
    for c, rc in f11['cells'].items():
        a(f"| {c} | {v(rc['k3_g005']['E_Ry'])} (l.{s(rc['k3_g005']['E_Ry']).split(':')[-1]}) | {v(rc['k4_g005']['E_Ry'])} (l.{s(rc['k4_g005']['E_Ry']).split(':')[-1]}) | "
          f"{v(rc['k3_g002']['E_Ry'])} (l.{s(rc['k3_g002']['E_Ry']).split(':')[-1]}) | {rc['k3_g005']['minus_TS_Ry']} / {rc['k4_g005']['minus_TS_Ry']} / {rc['k3_g002']['minus_TS_Ry']} | "
          f"{rc['k3_g005']['nk']} / {rc['k4_g005']['nk']} | {rc['k3_to_k4_meV']} | {rc['g002_minus_g005_k3_meV']} | {rc['E0_estimate_shift_meV']} |")
    a('\n| Difference (eV) | k3 G0.005 | k4 G0.005 | k3 G0.002 | k3->k4 (meV) | A20(ii) shift (meV) | threshold | A20 k rule | A20(ii) rule | logged |')
    a('|---|---|---|---|---|---|---|---|---|---|')
    lgd = {'dE_local_O30': lg(RL, 79, '| +0.5578 | +0.5321 | −25.7 meV | +0.5583 | +0.5 meV |'), 'dE_local_O72_sensitivity': lg(RL, 80, '| +0.6643 | +0.6230 | −41.3 meV | +0.6650 | +0.7 meV |'),
           'dE_dop': lg(RL, 81, '| +0.7259 | +0.7226 | −3.4 meV | +0.7261 | +0.2 meV |')}
    for k, d in f11['differences_eV'].items():
        a(f"| {k} | {d['k3_g005']:+.4f} | {d['k4_g005']:+.4f} | {d['k3_g002']:+.4f} | {d['k3_to_k4_meV']} | {d['A20ii_shift_meV']} | {d['threshold_eV']} | {d.get('A20_k_rule', '-')} | {d.get('A20ii_rule', '-')} | match {lgd[k]} |")
    a(f"\nO72 - O30: {f11['O72_minus_O30_eV']} eV. Per-cell shifts and -TS match {lg(RL, 90, 'In32O48 −1.7, In31WO48 −3.5, In32O47 +26.8, far +21.6, near −4.1, near72 −19.7')} and "
      f"{lg(RL, 91, 'In32O48 0.0, In31WO48 +11.7, In32O47 0.0, far +11.9, near +12.4, near72 +12.6')}. **Status unchanged: dE_local(O30) UNRESOLVED significance (k3->k4 -25.7 meV > 10 meV; "
      'the +0.3 eV threshold is met at all three settings), dE_dop PASS under registered settings, A20(ii) width-robust at k3, A20(i) spin UNASSESSED, H-L overall UNRESOLVED.** '
      'COMPUTED (PBE PAW, Gaussian, spin-unpolarised, neutral cells, QE 7.3.1 GPU; crystalline; 3.125 % W). The H-L In31WO48 energy (Gaussian, 7.3.1) is not comparable with the iwo_W24d energy (MV, 7.5) and is not mixed with it.\n')

    # ------------------------------------------------------------ discrepancies
    a('## 8. Discrepancies against RESULTS_LOG / ledger (flagged)\n')
    d1 = S['1.0']
    a(f"1. **Sign error in the 1 nm dEv (EA/IP route), 4 meV.** Logged dEv(1 nm) = -0.056 eV ({lg(RL, 363, '+0.848 | -0.056 | 0.94')}) from `bulk_alignment.py` "
      f"(line 105 used `v2 - 0.0019` until the 2026-10-14 fix, now {lg(ALIGN, 107, 'v2 + 0.0019')}); with IP(1) - IP(2) = {f5['partition_1_to_2']['IP1_minus_IP2']} eV the 1 nm VBM is 1.9 meV *higher*, so dEv(1) = dEv(2) + 0.0019 = **{d1['dEv_eV']} eV**. "
      f"Check: dEc - dEv must equal dEg = {d1['dEg_eV']}: {d1['dEc_eV']} - ({d1['dEv_eV']}) = {d1['dEc_eV'] - d1['dEv_eV']:.4f} (re-derived) vs 0.848 + 0.056 = 0.904 (logged). "
      f"The same sign appears in the 2026-10-04 partition ({lg(RL, 440, 'dEv(1) - dEv(2) = IP(1) - IP(2) = -0.002 eV')}): the correct relation is dEv(1) - dEv(2) = IP(2) - IP(1) = +0.002 eV, "
      f"and the gap change is the DIFFERENCE of the edge shifts, dEg(1) - dEg(2) = 0.5665 - 0.0019 = 0.5646 eV (RESULTS_LOG line 441 calls it a sum, which compensates the sign); "
      f"Fixed 2026-10-14 (user go) by a dated erratum entry at the top of RESULTS_LOG that keeps the original lines, and in bulk_alignment.py (rerun: only the 1 nm dEv changes); public commit 46b7229. dft_inputs.json already has -0.052 (dEv = dEc - dEg). No effect on TCAD (dEv is not used; dEc unchanged).\n")
    a(f"2. **0.75 nm slab is polar (new).** Vacuum ramp {S['0.75']['vacuum_ramp_over_gap_meV']} meV across the vacuum gap vs the recorded 27 meV asymmetry ({lg(DFTIN, 449, 'vacuum asymmetry 27 meV')}); "
      f"dEc(0.695 nm) = {S['0.75']['dEc_eV']} +- ~{f6['dEc_0p75_dipole_sensitivity']['half_ramp_eV']} eV; fit3 dEc(6.3 nm) range {rng['6.3']} eV under that ASSUMED reference-choice sensitivity (not a bound), outside the configured 0.046-0.062 eV band. "
      'Not in RESULTS_LOG and not in the C021 caveat.\n')
    a(f"3. **C021 / fit3 inputs not in RESULTS_LOG (resolved 2026-10-14).** The 0.51 and 0.75 nm slabs (slabL1_relax_v2, slabL2_relax_v2) had no RESULTS_LOG entry until 2026-10-14 "
      f"(C021 said so until its update that day), yet the 0.695 nm point enters the V3 / C10 fit3 laws used in the C10 decks. They are now logged ({lg(RL, 1, '0.51 nm and 0.75 nm slabs logged')}). "
      'Their numbers are re-derived here (Sec. 3) and match C021.\n')
    a(f"4. **fit3 parameters reproduced to < 0.3 %, not exactly** (Sec. 4): bulk mass reference 0.1588 ([100], free intercept, as PROTOCOL.md) vs 0.159 in dft_inputs_raw.json; EA window 0.1-0.3 meV. Deck impact <= 0.2 meV, NC300 <= 0.3 %.\n")
    a(f"5. **VBM k point** (0, 0, 0.200) 2pi/a, not 0.196 ({lg(PROT, 127, '(0, 0, 0.196) 2pi/a')}): unit conversion with the unrelaxed a; energies unaffected.\n")
    a(f"6. **Band labels in the 2026-09-30 entries** ({lg(RL, 505, 'band 352 (VB top)')}; {lg(RL, 500, 'about 0.19 eV below the host CB')}) are the pre-correction assignment; the correction entry of 2026-10-05 is right (re-derived). "
      'The superseded text stays in the log without a pointer to the correction.\n')
    a(f"7. **2 nm W slab band 666**: 'just empty' ({lg(RL, 406, 'so just empty')}) holds for the band (>= 0.069 eV above E_F at all k) but MV smearing gives it {w2['filling']['bands']['666']['electrons']} e.\n")
    a(f"8. **Occupation ratio 24d:8b at 600 K**: {f9['occupation_ratio_24d_to_8b_600K']:.0f}:1 (kT = 51.7 meV, k4 dE) vs logged ~430:1 (kT rounded to 52 meV). Rounding only.\n")
    a('9. **C022 wording** (Sec. 6): the "resonant 1.2-1.8 eV above the CB" positions are computed with E_F 1.2-1.8 eV inside the host CB and the W-rich level roughly 0.1 eV or less from E_F at Gamma; pinning by the filling is an interpretation and the behaviour at device densities is INFERRED. Suggest adding this to the C022 caveat.\n')
    a(f"10. **W site preference at k3**: {f9['E8b_minus_E24d_eV']['E_relax_k3_Ry']} eV vs logged +0.2580 ({lg(RL, 543, '+0.2580 eV at 3x3x3')}): "
      "(-15496.3476465985 + 15496.3666036746) Ry = 0.257925 eV, so the log's last digit is a rounding (0.07 meV). The k4 value 0.2577 and the conclusion are unchanged.\n")
    a('No other re-derived number differs from RESULTS_LOG, PROTOCOL.md or the ledger beyond the last printed digit.\n')

    # ------------------------------------------------------------ figures, CERN, open
    a('## 9. Figures (PNG 300 dpi + PDF in `figures/`)\n')
    caps = [
        ('fig01_bulk_convergence', 'Stage-1 convergence of bulk In2O3 at a = 10.117 A. (a) Total energy per atom, (b) pressure, (c) KS gap on the SCF grid, relative to 85 Ry (circles, bottom axis, k 3x3x3) or to the 4x4x4 grid (squares, top axis, 71 Ry). Grey bands: the pre-registered criteria (1 mRy/atom, 1 kbar, 10 meV); dotted line: the selected 71 Ry. COMPUTED. f01.'),
        ('fig02_bulk_bands_mass', '(a) PBE band structure of relaxed bulk In2O3 (a = 10.3061 A) along Gamma-H-N-Gamma-P-H|P-N, energies relative to the VBM (black: occupied, blue: empty). (b) Lowest conduction band near Gamma along [100], [110], [111] (symbols); solid: parabolic fit for |k| <= 0.05 1/A (dotted line) along [100], m* = 0.1588 m0; dashed: Kane fit over the whole range. COMPUTED; the fits are FITTED to these points. f02.'),
        ('fig03_two_step_alignment', '(a) Planar (grey) and a/2 macroscopic (blue) average of the electrostatic potential of the relaxed 2 nm slab; solid horizontal lines: slab CBM (orange) and VBM (green); dashed: bulk CBM and VBM aligned through the slab-centre macroscopic average and the bulk constants. The offsets between solid and dashed are dEc = +0.281 and dEv = -0.054 eV. (b) Validation of the bulk <V> route: z-mean of each slab planar average minus the G = 0 local-pseudopotential term computed from the UPF files (all 0.00 meV). COMPUTED. f03.'),
        ('fig04_slab_vacuum', 'Unrelaxed 1 nm slab with 15, 25 and 35 A vacuum. (a) Planar average relative to the vacuum level (the three curves coincide). (b) Change of EA, IP and gap against 25 A. COMPUTED. f04.'),
        ('fig05_slab_series_levels', '(a) Vacuum-referenced CBM (blue) and VBM (orange) of the relaxed slabs against the H-H thickness (0.461 nm = In(OH)3-like layer, outside the recipe). (b) Planar averages relative to each vacuum level; the 0.695 nm slab (orange) shows the vacuum ramp of a polar slab. COMPUTED. f05.'),
        ('fig06_confinement_laws', 'Thickness laws as used in TCAD (log-log): (a) dEg, (b) dEc, (c) dm*. Circles: re-derived DFT points at the H-H thickness; diamonds: the rounded values at the Lin-label thicknesses used by V2; cross: 0.461 nm film (excluded). Dashed: V2 two-point laws; solid: V3/C10 fit3 laws (configured parameters); shaded in (b): fit3 with the 0.695 nm dEc point moved by +-0.174 eV (polar-slab vacuum ramp). Dotted verticals: device thicknesses 2.0, 6.3, 13.2 nm (6.3 and 13.2 are extrapolations). Points COMPUTED, laws FITTED. f06.'),
        ('fig07_hse_check', 'KS gaps on the SCF grid of bulk and the relaxed 1 nm slab with norm-conserving PBE (hatched) and HSE06 (open). Bar on the bulk HSE: change to EXX q 3x3x3; tick on the slab HSE: slab gap if it moved with the bulk q correction (worst case). r = dEg(HSE)/dEg(PBE) = 1.060 (q 1) to 1.107. COMPUTED. f07.'),
        ('fig08_slab2_pdos_surface', '(a) PDOS of the relaxed 2 nm In2O3 slab (slab2r_pdos_cpu) by element and l, relative to the VBM; dashed: VBM and CBM. (b) Projected weight of the VB top (band 664), CB bottom (665) and a reference band (644) in 8 slices across the slab (k-weighted). COMPUTED. f08.'),
        ('fig09_iwo_bulk_pdos', 'W in bulk In2O3 (80-atom cell, 3.1 % W, PBE, MV 0.01 Ry, k 4x4x4). (a) W on 24d, (b) W on 8b: total, In 5s, O 2p and W 5d (x5) PDOS relative to E_F; dotted blue: host CB bottom at Gamma (band 352). (c) W 5d weight of every band at Gamma against its energy. COMPUTED. f09.'),
        ('fig10_iwo_slabs', 'W in the relaxed (a) 1 nm and (b) 2 nm slabs: PDOS as in Fig. 9; dotted blue: host CB bottom at Gamma (bands 312 / 664). (c) W 5d weight at Gamma against energy for both slabs and bulk 24d. COMPUTED. f10.'),
        ('fig11_hl_vacancy', 'Register H-L (crystalline, PBE, neutral, spin-unpolarised). (a) The registered differences dE_local(O30) and dE_dop and the O72 sensitivity at k 3x3x3 / Gaussian 0.005 Ry (circles), k 4x4x4 (squares) and k 3x3x3 / Gaussian 0.002 Ry (triangles); dashed: the registered thresholds +0.3 and +0.05 eV. (b) Per-cell energy changes k3 -> k4 (open) and G 0.002 - G 0.005 at k3 (hatched). COMPUTED from r23.out. f11.'),
        ('fig12_relax_traces', 'Relaxation histories: (a) energy above the converged value and (b) total force (norm over all atoms) for every SCF of the BFGS runs of the pure slabs (solid) and the W cells (dashed). COMPUTED. f12.'),
        ('fig13_hl_raw_relax_filling', 'H-L cells from the raw CERN outputs (crystalline, PBE). (a) Radial displacement of the four nearest neighbours of each removed O (positive = away from the vacancy), relative to the relaxed parent. (b) Electrons per cell above the VB top (open) and in the first band above the VB top (hatched) in the k 4x4x4 FINALs (Gaussian occupations; band character not projected). COMPUTED. f13.'),
        ('fig14_amorph_force_checks', 'MACE-MPA-0 force validation (C037), re-derived from allowlisted DFT force extracts. (a) DFT against MACE force components for the two quenched bulk frames and the 0.7 nm final frame. (b) RMSE_all, MAE_all and RMSE of the W first shell per frame; dashed: the frozen limits 0.15, 0.10, 0.25 eV/A (the melt frame is reported, not scored). COMPUTED (forces only; no electronic quantity). f14.'),
    ]
    for stem, cap in caps:
        a(f'- `figures/{stem}.png` / `.pdf`: {cap}')
    a('\n## 10. CERN files (updated 2026-10-14)\n')
    a('- Fetched 2026-10-14 read-only through `scratchpad/golist/run_r.sh` (SSH master checked; no authentication, no submits, no deletions), text only, every file sha256-verified against lxplus: '
      'the H-L raw outputs (`raw_cern/hl/`, Sec. 12) and allowlisted force extracts of the amorphous checks C034/C035/C037 (`raw_cern/amorph_forces_allowlist/`, Sec. 13).')
    a('- Crystalline CERN job folders `~/qe_jobs_*` hold only the result tarballs already mirrored in `cern_htcondor/results/`; the failed or superseded attempts (slab2_relax_gpu*/x1/x2/x4/gpu8, PAW HSE hse_*, '
      'thinslab GPU, __cpu twins, early 20260927* runs) left no tarball and no output: nothing further to read (their loss is logged).')
    a('- Not computed anywhere (open work, not files): projwfc of the pure 1 nm slab; bands (mass) of the W slabs (1 nm aborted, 2 nm not run); spin-polarised 4x4x4 W cells; HSE for W cells (A23 (ii) staged in ~/iwo_amorph/hse/In31WO48, not submitted); dipole-corrected 0.75 nm slab.\n')
    a('## 11. Open items\n')
    a('- Re-run the 0.75 nm slab SCF with a dipole correction (or a symmetric 0.75 nm slab) to pin dEc(0.695 nm), checking both surface vacuum plateaus, the gap and the residual forces before deciding on a re-relaxation; until then exclude that point from any new primary dEc fit '
      '(two-point diagnostic in Sec. 4) and keep the C10 fit3 results with the caveat (an amendment is needed to change them).')
    a('- Codex review 2026-10-13 (work chat, model gpt-6.1-sol, effort high): verdict CONCERN; G=0 route and the dEv sign correction accepted; polar-slab +-0.17 eV relabelled as a reference-choice sensitivity; C022 caveat accepted with refinements (applied here). UPF sha256 hashes and the integration convention are stored in out/f03_bulk_alignment.json.')
    a('- DONE 2026-10-14 (user go; public commit 46b7229, private b0850ef): the 1 nm dEv sign corrected in RESULTS_LOG by a dated erratum (original lines kept) and in bulk_alignment.py; '
      'the 0.51 / 0.75 nm slabs logged in RESULTS_LOG with the polar-slab caveat; C021 / C022 caveats updated in the ledger.')
    a('- DONE 2026-10-14: bulk_v11.cube regenerated locally with pp.x for the bulk_alignment.py rerun: <V> = 4.1687 eV, equal to the UPF G = 0 route (4.16867 eV); the cube was deleted again.')
    a('- H-L: raw outputs now archived locally (Sec. 12); A20(i) spin remains staged, not run.\n')
    extension(a, O, f11)
    a(f'Quotations checked against their source lines: {len(CHECKED)}.')
    (q.HERE / 'DFT_FULL_STUDY.md').write_text('\n'.join(W) + '\n', encoding='utf-8')
    print('wrote DFT_FULL_STUDY.md;', len(CHECKED), 'quotations checked')


def extension(a, O, f11):
    """Sections 12-14: the 2026-10-14 extension (raw CERN H-L outputs, amorphous force checks, skipped items)."""
    f13, f14 = O['f13_hl_raw'], O['f14_amorph_force_checks']
    C = f13['cells']
    a('## 12. Extension 2026-10-14: H-L re-derived from the raw CERN outputs (Fig. 13)\n')
    a(f"Source `{f13['source']}` (relax.in/out, FINAL scf.in/out, A20(ii) scf.in and the scf.out member of each a20g002 tarball, the FINAL-tarball copies, "
      "the near-cell attempt-1 archive), sha256-verified against lxplus (`SHA256_REMOTE.txt`). Script f13_hl_raw.py (independent of r23.out and hl_a20ii.py).\n")
    a('| Cell | relax (QE count) | max force comp. / total force (Ry/bohr) | SCF failures | E k3 G0.005 (Ry) | E k4 G0.005 (Ry) | E k3 G0.002 (Ry) | irr. k | E_F k4 (eV) | logged BFGS |')
    a('|---|---|---|---|---|---|---|---|---|---|')
    lb = {'In32O48': lg(RL, 35, '12886359 (0)'), 'In31WO48': lg(RL, 36, '12886360 (0)'), 'In32O47': lg(RL, 37, '12886361 (13)'),
          'In31WO47_far': lg(RL, 38, '12886364 (16)'), 'In31WO47_near': lg(RL, 39, '12892681 (18; A28 restart 1)'), 'In31WO47_near72': lg(RL, 40, '12886363 (29)')}
    for c, r in C.items():
        a(f"| {c} | {v(r['bfgs'])} ({s(r['bfgs'])}) | {v(r['max_force_component_Ry_bohr'])} / {v(r['total_force_Ry_bohr'])} | {r['scf_not_converged_relax']} | "
          f"{v(r['E_Ry']['k3_g005'])} | {v(r['E_Ry']['k4_g005'])} | {v(r['E_Ry']['k3_g002'])} | {r['nk']['k3_g005']} / {r['nk']['k4_g005']} | {v(r['E_F_k4_eV'])} | {lb[c]} |")
    D = f13['differences_eV']
    a(f"\nEvery energy equals the r23.out grep value (largest difference {f13['energy_max_abs_diff_vs_r23_Ry']} Ry), so the registered differences are unchanged: "
      f"dE_local(O30) {D['dE_local_O30']['k3_g005']:+.5f} / {D['dE_local_O30']['k4_g005']:+.5f} / {D['dE_local_O30']['k3_g002']:+.5f} eV (k3 / k4 / k3 G0.002; k3->k4 {D['dE_local_O30']['k3_to_k4_meV']} meV), "
      f"dE_dop {D['dE_dop']['k3_g005']:+.5f} / {D['dE_dop']['k4_g005']:+.5f} / {D['dE_dop']['k3_g002']:+.5f} eV (k3->k4 {D['dE_dop']['k3_to_k4_meV']} meV), "
      f"O72 sensitivity {D['dE_local_O72_sensitivity']['k3_g005']:+.5f} / {D['dE_local_O72_sensitivity']['k4_g005']:+.5f} eV: match ({lg(RL, 79, '+0.5578 | +0.5321')}, {lg(RL, 81, '+0.7259 | +0.7226')}). "
      'Statuses unchanged (dE_local(O30) UNRESOLVED significance, dE_dop PASS under registered settings, A20(ii) width-robust at k3, A20(i) UNASSESSED, H-L UNRESOLVED). COMPUTED.\n')
    ok_sha = all(f13['input_sha16'][c][k] == {'In32O48': ('e89421cc96b92580', 'a9968110956481ed', '11e2e9030d83df0c'), 'In31WO48': ('3b8b7db5fb65ef84', '1bd9105027571e3d', '2e7d010f9e9b5c32'),
                                               'In32O47': ('25a3156ca1494caf', '2bdc62ef2eef85a4', '5f8ebf81b00b52fe'), 'In31WO47_far': ('d98ff7b6d8b0771c', '130ddcb1d0fc9476', '6f593dd5863e57a2'),
                                               'In31WO47_near': ('335e745559fef92d', 'fc417c04dad8a04b', '24a4cf10a178cbf6'), 'In31WO47_near72': ('52a3626d246811ac', '6d460182adfe14a0', 'c114f167b7c6a469')}[c][i]
                 for c in C for i, k in enumerate(('relax.in', 'FINAL scf.in', 'A20 scf.in')))
    for ln, t in ((63, 'e89421cc96b92580'), (64, '3b8b7db5fb65ef84'), (65, '25a3156ca1494caf'), (66, 'd98ff7b6d8b0771c'), (67, '335e745559fef92d'), (68, '52a3626d246811ac')):
        lg(RL, ln, t)
    a(f"**Bindings re-checked from raw files.** Input sha256 (first 16 hex) of all 18 inputs equal the logged table: {ok_sha} (RESULTS_LOG lines 63-68). "
      f"FINAL and A20(ii) input geometries equal the relax final geometry to {max(r['geometry']['FINAL_input_minus_relax_final_A'] for r in C.values())} A; the A20(ii) inputs differ from the FINAL inputs only in "
      f"degauss and K_POINTS (two lines per cell); the FINAL-tarball scf.out is byte-identical to the vac scf.out in every cell: {all(f13['final_tarball_scf_equals_vac_scf'].values())}. "
      f"All relaxations meet forc_conv_thr per component (largest {max(v(r['max_force_component_Ry_bohr']) for r in C.values())} Ry/bohr); no relax SCF failed. "
      f"Near attempt 1 (A28 history): {f13['near_attempt1']['n_scf_bang']} converged SCFs, {f13['near_attempt1']['scf_not_converged']} SCF not converged "
      f"(logged: three validated SCFs, failure at BFGS step 3, {lg(RL, 43, 'It had three validated SCFs')}). The archived relax.in equals the converged geometry by construction ({lg(RL, 55, 'rewrites relax.in before packing')}), "
      "so relaxations are measured against the relaxed parent. Atom labels O17/O30/O32/O72 are 0-based indices; the removed O was identified independently by order-preserving matching and agrees in all four cells.\n")
    a('**New crystalline results (non-blind; analysis not previously logged).**\n')
    a('| Cell | removed O | max relaxation vs parent (A) | atoms moved > 0.05 A | nearest neighbours of the vacancy: dist (A) / radial move (A) | W-O (A) |')
    a('|---|---|---|---|---|---|')
    for c, r in C.items():
        vv = r.get('vacancy')
        sh = '; '.join(f"{x['atom']} {x['dist_to_vacancy_A']} / {x['moves_away_A']:+.3f}" for x in vv['first_shell']) if vv else '-'
        a(f"| {c} | {vv['removed'] if vv else '-'} | {(str(vv['max_relaxation_vs_parent_A']) + ' (' + vv['atom_max_relaxation'] + ')') if vv else '-'} | {vv['n_atoms_moved_gt_0p05_A'] if vv else '-'} | {sh} | {r['geometry'].get('W_O_A', '-')} |")
    a('\n| Cell | VB top band | electrons above VB top | VB max - E_F (eV) | first band above VB: min - E_F (eV) | its width (eV) | its electrons | VB max -> next band min (eV) | source |')
    a('|---|---|---|---|---|---|---|---|---|')
    for c, r in C.items():
        b = r['bands_k4']
        a(f"| {c} | {b['VB_top_band']} | {b['electrons_above_VB_top']} | {b['VB_max_minus_EF_eV']} | {b['band_above_VB_min_minus_EF_eV']} | {b['band_above_VB_width_eV']} | {b['band_above_VB_electrons']} | {b['gap_VBmax_to_next_band_min_eV']} | {b['src']} |")
    a(f"\nReading (COMPUTED, PBE, Gaussian 0.005 Ry, k 4x4x4, spin-unpolarised; character NOT projected, so no band is named a defect state): the pristine cell gives VB max -> CB min "
      f"{C['In32O48']['bands_k4']['gap_VBmax_to_next_band_min_eV']} eV on the 4x4x4 grid (bulk fundamental gap 0.8887 eV, f02); the 'VB top' index is a formal electron count (5 bands per In, 4 per W, 4 per O), so the totals are occupations above that cutoff and do not by themselves establish defect character or mobile-carrier donation (Codex 2026-10-14). "
      f"In In32O47 the 2 electrons above the cutoff sit {C['In32O47']['bands_k4']['band_above_VB_electrons']} in the first band above it (width {C['In32O47']['bands_k4']['band_above_VB_width_eV']} eV, minimum {C['In32O47']['bands_k4']['gap_VBmax_to_next_band_min_eV']} eV above the VB max) "
      f"and {2 - C['In32O47']['bands_k4']['band_above_VB_electrons']:.3f} in higher bands; in the W vacancy cells 5 electrons lie above the cutoff, 2.0 of them in the first band above it. The W in the near cells moves away from the vacancy by {C['In31WO47_near']['vacancy']['first_shell'][0]['moves_away_A']:+.3f} A (O30) and "
      f"{C['In31WO47_near72']['vacancy']['first_shell'][0]['moves_away_A']:+.3f} A (O72) while its In neighbours move toward the vacancy; in In32O47 all four In neighbours move away (+0.02 to +0.14 A); the far cell is mixed. Neutral, periodic, spin-unpolarised PBE cells only; no charge-state, Fermi-level or finite-size information (hybrid work shows the vacancy's electrical activity depends on charge state and Fermi level: Chatratin et al., PRMaterials 3, 074604, 2019). COMPUTED diagnostics outside the registered H-L test.\n")
    pn = f13['paw_nc_basis_check']
    a(f"**PAW/NC projection-basis check on crystalline In31WO48 (A23 (ii) preparation, local QE 7.5, 2026-10-11; read from CERN).** {pn['summary_line']} ({pn['src']}); "
      f"the two W-5d donor states carry {pn['W5d_donor_states_PAW_NC'][0][0]} / {pn['W5d_donor_states_PAW_NC'][1][0]} (PAW) and {pn['W5d_donor_states_PAW_NC'][0][1]} / {pn['W5d_donor_states_PAW_NC'][1][1]} (NC) W-5d weight "
      '(unrelaxed vac geometry, Gamma only). It shows agreement of the tested PBE Gamma-point projection weights only (one geometry, one k point, max |dPR_n| 0.162); it does not establish basis equivalence across k points or functionals, and it is not an HSE result. COMPUTED (by the earlier session).\n')
    # ---- 13 amorphous force checks
    c34, c35, c37 = f14['C034'], f14['C035'], f14['C037']
    a('## 13. Extension 2026-10-14: amorphous force checks already logged as read (Fig. 14)\n')
    a('**Sight rule.** The register blinds every amorphous-DFT electronic target quantity (edges, projections, localisation, EA, gaps; '
      f"{lg(LEDGER.parent / 'codex' / 'work_chat' / 'HYPOTHESIS_REGISTER.md', 35, 'every amorphous-DFT electronic target quantity (edges, projections, localisation, EA, gaps)')}). "
      'C034, C035 and C037 were logged with energies, forces and SCF bookkeeping only. Their pw.x outputs were therefore not copied: on lxplus an allowlist kept only "!" energies, -TS, "internal energy E=F+TS", '
      '"Total force" lines, the first force block, convergence lines, atom/electron/k counts, program/version and JOB DONE lines; every copied line was machine-checked against the whitelist and a keyword scan (Fermi, gap, highest, eigen, band, HOMO) found nothing. '
      f"Inputs and MACE forces were copied whole. The extractor script and the sha256 of every filtered file are kept with the data (EXTRACTOR_copy_amorph_forces.sh, FILTERED_SHA256.txt, next to SHA256_REMOTE.txt). Source `{f14['source']}`; tarball sha256 prefixes equal the logged ones ({lg(RL, 153, 'melt b4e4c7f7, aIWO-q 6e780c02, aIWO-f eee14029, aIO-q c1cc3d63, aIO-f 95ea5d18, 0p7-f e7aa2076')}).\n")
    a('| Check | quantity | re-derived | logged | status |')
    a('|---|---|---|---|---|')
    rows = [('C034 (A27 C4, 1.0 nm aIWO)', 'max abs dF (Gauss - MV), Ry/bohr', c34['max_abs_dF_Ry_bohr'], 2.42e-4, 5e-7, lg(RL, 309, '**2.42e-4 Ry/bohr** (W atom 50, x component)')),
            ('C034', 'RMS dF over 414 components', c34['rms_dF_Ry_bohr'], 6.7e-5, 5e-7, lg(RL, 310, '6.7e-5 Ry/bohr')),
            ('C034', 'max per-atom abs dF', c34['max_atom_norm_dF'], 2.85e-4, 5e-7, lg(RL, 311, '2.85e-4 Ry/bohr')),
            ('C034', 'largest residual component MV', c34['max_residual_component_MV_Gauss'][0], 9.50e-4, 5e-7, lg(RL, 313, 'MV 9.50e-4, Gaussian 9.47e-4')),
            ('C034', 'E(MV) - relax energy, Ry', c34['E_MV_minus_relax_Ry'], 4e-8, 5e-9, lg(RL, 308, '+4e-8 Ry')),
            ('C035 (A25 split, 1.0 nm aIO)', 'abs dE, Ry', c35['abs_dE_Ry'], 1e-8, 5e-9, lg(RL, 274, '**1e-8 Ry**')),
            ('C035', 'max abs dF over 402 components, Ry/bohr', c35['max_abs_dF_Ry_bohr'], 3e-8, 5e-9, lg(RL, 275, '**3e-8 Ry/bohr** (atom 70, y')),
            ]
    fr = [('aIWO_bulk_s1_melt_3000K', 159, '| 0.311 | 0.171 | 1.108 |'), ('aIWO_bulk_s1_quenched_300K', 160, '| 0.121 | 0.068 | **0.434** |'),
          ('aIWO_bulk_s1_final', 161, '| 0.122 | 0.068 | **0.449** |'), ('aIO_bulk_s1_quenched_300K', 162, '| 0.068 | 0.052 | N/A |'),
          ('aIO_bulk_s1_final', 163, '| 0.065 | 0.049 | N/A |'), ('aIWO_0p7_s1_final', 164, '| **0.206** | **0.110** | **0.815** |')]
    for f_, ln, txt in fr:
        ref = lg(RL, ln, txt)
        nums_ = [float(x) for x in txt.replace('*', '').replace('N/A', 'nan').split('|') if x.strip()]
        r = c37[f_]
        for nm, key, lv in (('RMSE_all', 'RMSE_all', nums_[0]), ('MAE_all', 'MAE_all', nums_[1]), ('RMSE_W1', 'RMSE_W1', nums_[2])):
            if r[key] is None:
                continue
            rows.append((f'C037 {f_}', f'{nm}, eV/A', r[key], lv, 5e-4, ref))
    for chk, nm, new, logd, tol, ref in rows:
        a(f"| {chk} | {nm} | {new:.4g} | {logd:g} ({ref}) | {st(new, logd, tol)} |")
    w07 = c37['aIWO_0p7_s1_final']['W_atom_force_norm_DFT_MACE_eV_A']
    a(f"\nVerdicts reproduced: C034 '{c34['verdict_A15']}' (scoped to its tested geometry and the 1e-3 Ry/bohr tolerance); C035 {c35['verdict_A25']}; C037 "
      + ', '.join(f"{k} {c37[k].get('verdict', 'reported')}" for k in c37) + ' (OVERALL FAIL by rule D7). '
      f"W first shell (7 atoms) carries {min(c37[k]['W1_share_of_squared_error'] for k in c37 if 'W1_share_of_squared_error' in c37[k]):.2f}-{max(c37[k]['W1_share_of_squared_error'] for k in c37 if 'W1_share_of_squared_error' in c37[k]):.2f} of the squared error "
      f"({lg(RL, 174, 'it carries 71-75% of the squared force error')}); RMSE outside the shell {c37['aIWO_bulk_s1_quenched_300K']['RMSE_outside_W1']:.3f}/{c37['aIWO_bulk_s1_final']['RMSE_outside_W1']:.3f} (aIWO bulk) "
      f"and {c37['aIWO_0p7_s1_final']['RMSE_outside_W1']:.3f} (0.7 nm) eV/A ({lg(RL, 175, 'RMSE 0.063-0.066 (aIWO bulk) and 0.107 (0.7 nm)')}). "
      f"DFT-MACE component correlation: quenched {c37['aIWO_bulk_s1_quenched_300K']['corr_DFT_MACE']:.3f} / {c37['aIO_bulk_s1_quenched_300K']['corr_DFT_MACE']:.3f}, melt {c37['aIWO_bulk_s1_melt_3000K']['corr_DFT_MACE']:.3f}; "
      f"final frames {c37['aIWO_bulk_s1_final']['corr_DFT_MACE']:.3f} (aIWO), {c37['aIO_bulk_s1_final']['corr_DFT_MACE']:.3f} (aIO), {c37['aIWO_0p7_s1_final']['corr_DFT_MACE']:.3f} (0.7 nm). "
      f"0.7 nm W atom: |F| = {w07[0]} eV/A (DFT) vs {w07[1]} (MACE) as vector norms; the logged '1.05 eV/A in DFT against 0.002 in MACE' ({lg(RL, 174, 'the W atom feels 1.05 eV/A in DFT against 0.002 in MACE')}) "
      "are the largest components (|Fx| 1.049 and 0.0024): wording only. COMPUTED (forces; amorphous melt-quench cells; no electronic quantity read).\n")
    a('## 14. Skipped and why (2026-10-14)\n')
    a('- **The seven amorphous FINALs** (EOS final_12889857, 12890432, 12891132, 12891160, 12894279, 12902517, 12904001) and every amorphous relax/FINAL electronic quantity: blind until release D-43 (D-43 is still reserved, decision log D-44).')
    a('- **C036 (aIWO_0p8_s2 relaxation, restart non-reproducibility):** amorphous and not in the requested list of checks; its outputs are relax segments of a blind cell. Not re-read.')
    a('- **C037 2.0 nm val frames (12890593.0/.1):** no returned tarball on lxplus (pending in the log), so not logged as read; A38 timing rules apply. Not opened.')
    a('- **Amorphous relax segments, geomsel summaries, bulk references (aIO/aIWO_bulk_s1 A23 (i)), probe 12898434 (2.0 nm FINAL probe), hse/aIO_bulk_s1:** amorphous; skipped.')
    a('- **Raw full pw.x outputs of C034/C035/C037:** not copied (they contain Fermi energies and eigenvalues); only allowlisted lines.')
    a('- **C035 per-atom SCF-correction block** (logged 3.7e-7 / 3.3e-7 Ry/bohr): not in the allowlist, so not re-derived; the printed "Total SCF correction" (0.000000) was read.\n')
    a('**Discrepancies added by the extension:** none in the numbers. Wording only: the 0.7 nm W force in RESULTS_LOG line 174 is a component, not the vector norm.\n')
    ck = q.HERE / 'runs_sep_oct' / 'out' / 'checks_vs_results_log.json'
    if ck.exists():
        C = json.loads(ck.read_text())
        dd = [c for c in C if c['status'] != 'match']
        a('## 15. Run-by-run data sheets of the 41 Sep-Oct CERN run folders (2026-10-14)\n')
        a('`runs_sep_oct/`: one sheet per folder (`sheets/<run>.md`), machine-readable records (`out/<run>.json`, `out/<run>_arrays.json.gz`), `MASTER_TABLE.md`, figures R1-R5; '
          'every file and tarball member read (all members byte-identical to the loose copies), the 9.38 GB runaway tar member streamed only. '
          f"{len(C)} per-run RESULTS_LOG values re-derived, {len(C) - len(dd)} match; differing (Codex GO 2026-10-13T22:06Z; dated errata applied 2026-10-14 at the top of RESULTS_LOG, original lines kept, public commit 46b7229):")
        for c in dd:
            a(f"- {c['run']}: {c['quantity']}: re-derived {c['re_derived']}, logged {c['logged']} ({c['reference']}).")
        a('')


if __name__ == '__main__':
    main()
