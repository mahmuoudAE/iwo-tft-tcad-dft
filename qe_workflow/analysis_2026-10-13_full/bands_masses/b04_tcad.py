"""TCAD-ready parameters per thickness, with labels, compared with the deck values (V2 run_0058 at 2.0 nm; C10 fit3 decks
run_0061 / run_0068 / run_0069 at 2.0 / 6.3 / 13.2 nm). Writes out/b04_tcad.json and figure BM8.

Rows: the DFT thicknesses (H-H 0.695 [polar, caveat], 0.930, 1.962 nm; COMPUTED) and the device thicknesses 2.0, 6.3, 13.2 nm
(FITTED laws from b03; 6.3 and 13.2 nm are extrapolations). Bulk row for reference.
Parameter options (each labelled):
  Eg: PBE (COMPUTED / FITTED), HSE-corrected = Eg_HSE,bulk + r dEg_PBE (r in [1.060, 1.107], ASSUMED thickness-independent),
      experiment-anchored = 2.93 eV (King 2009, LITERATURE) + r dEg_PBE, deck basis = 3.05 (LITERATURE, Fan 2021) + dEg_PBE.
  chi: PBE vacuum EA (COMPUTED at DFT slabs, H-(001) termination), deck basis = 4.3 (LITERATURE) - dEc(t) (fit3 or fit2).
  m*_e: PBE in-plane 2-D DOS band-edge mass (COMPUTED / FITTED); deck basis 0.208 (LITERATURE, Stokey 2021) + dm_4pt(t);
      multiplicative alternative 0.208 * m_PBE(t)/m_PBE,bulk (ASSUMED rule).
  Nc: 3-D 2(2 pi m kT/h^2)^1.5 (parabolic, and Kane-corrected with the PBE alpha), quasi-2-D N2D/t (first subband;
      E21 >> kT), both CALCULATED from the masses.
  Nv: Boltzmann sum over the computed valence bands (COMPUTED on coarse grids, convergence +-20 %).
"""
import json
import math

import numpy as np

import bm
from bm import r, plt
import figstyle as fs

D1 = json.loads((bm.OUT / 'b01_masses.json').read_text())
D3 = json.loads((bm.OUT / 'b03_gaps_laws.json').read_text())
C = fs.CYCLE
CHI_BULK_LIT = 4.3
EG_DECK = 3.05
EG_KING = 2.93
M_LIT = 0.208


def main():
    L = D3['laws']
    rr = D3['hse']['r_q1'], D3['hse']['r_q3bulk']
    eg_hse_b = D3['hse']['HSE_bulk_q1']['gap_eV']['value'], D3['hse']['HSE_bulk_q3_f160']['gap_eV']['value']
    egb = D3['bulk']['Eg_fundamental_eV']
    mb = D1['bulk']['electron_summary']['m_dos']
    ab = D1['bulk']['electron_summary']['alpha_mean_per_eV']
    mb4 = L['dm_e_4pt_deck_basis']['m_bulk']
    rows = {}
    # ---------------------------------------------------------------- DFT thicknesses
    for lab in ('0.75', '1.0', '2.0'):
        s = D3['slabs'][lab]
        e = D1['slabs'][lab]['electron_summary']
        t = s['t_HH_nm']
        m2 = e['tensor_2d']['m_dos_2d']
        a2 = 0.5 * (e['alpha_[100]'] + e['alpha_[110]'])
        nv = D1['slabs'][lab]['Nv']
        row = {'t_nm': t, 'source': 'COMPUTED (DFT slab ' + s['job'] + ')',
               'Eg_PBE_eV': s['Eg_fundamental_eV'], 'Eg_HSE_corrected_eV': s['Eg_HSE_corrected_eV'],
               'Eg_exp_anchored_eV': [r(EG_KING + x * s['dEg_eV']) for x in rr], 'Eg_deck_basis_eV': r(EG_DECK + s['dEg_eV']),
               'dEg_eV': s['dEg_eV'], 'dEc_eV': s['dEc_eV'], 'dEv_eV': s['dEv_eV'],
               'chi_PBE_vacuum_eV': s['EA_eV'], 'chi_deck_basis_eV': r(CHI_BULK_LIT - s['dEc_eV']),
               'm_e_PBE_2D_dos': m2, 'm_e_PBE_4pt_[100]': e['m_4pt_intercept_[100]'], 'alpha_2D_per_eV': r(a2, 3),
               'm_e_deck_basis': r(M_LIT + e['m_4pt_intercept_[100]'] - mb4), 'm_e_multiplicative': r(M_LIT * m2 / mb, 4),
               'E21_eV': s['E21_eV'], 'Nv2D_cm2': nv['Nv2D_cm2'], 'Nv_quasi3D_cm3': nv['Nv_quasi3D_cm3']}
        if lab == '0.75':
            row['caveat'] = 'polar slab, no dipole correction: chi and dEc +-0.17 eV (ASSUMED reference sensitivity); excluded from new dEc fits'
        rows[str(t)] = row
    # ---------------------------------------------------------------- device thicknesses via laws
    for t in (2.0, 6.3, 13.2):
        deg = bm.law(L['dEg_eV']['fit3'], t)
        dec3 = bm.law(L['dEc_eV']['fit3'], t)
        dec2 = bm.law(L['dEc_eV']['fit2_1and2nm'], t)
        decs = [bm.law(L['dEc_eV'][k], t) for k in ('fit3_0p695_low', 'fit3_0p695_high', 'fit2_1and2nm', 'fit3')]
        dm = bm.law(L['dm_e_band_edge']['fit3'], t)
        dm4 = bm.law(L['dm_e_4pt_deck_basis']['fit3'], t)
        row = {'t_nm': t, 'source': 'FITTED laws (b03), extrapolated' if t > 2.0 else 'FITTED laws (b03), interpolated',
               'Eg_PBE_eV': r(egb + deg), 'Eg_HSE_corrected_eV': [r(eg_hse_b[0] + rr[0] * deg), r(eg_hse_b[1] + rr[1] * deg)],
               'Eg_exp_anchored_eV': [r(EG_KING + x * deg) for x in rr], 'Eg_deck_basis_eV': r(EG_DECK + deg), 'dEg_eV': r(deg),
               'dEc_fit3_eV': r(dec3), 'dEc_fit2_eV': r(dec2), 'dEc_range_eV': [r(min(decs)), r(max(decs))],
               'chi_deck_basis_fit3_eV': r(CHI_BULK_LIT - dec3), 'chi_deck_basis_fit2_eV': r(CHI_BULK_LIT - dec2),
               'm_e_PBE_band_edge': r(mb + dm, 4), 'm_e_deck_basis': r(M_LIT + dm4, 4), 'm_e_multiplicative': r(M_LIT * (mb + dm) / mb, 4)}
        e2 = D1['slabs']['2.0']['electron_summary']
        row['alpha_2D_per_eV'] = r(0.5 * (e2['alpha_[100]'] + e2['alpha_[110]']), 3) if t == 2.0 else ab
        row['alpha_note'] = 'COMPUTED 2 nm slab value' if t == 2.0 else 'bulk PBE alpha (ASSUMED for 6.3 / 13.2 nm)'
        rows[str(t)] = row
    # ---------------------------------------------------------------- Nc options for every row
    for key, row in rows.items():
        t = row['t_nm']
        m_deck = row['m_e_deck_basis']
        m_pbe = row.get('m_e_PBE_2D_dos', row.get('m_e_PBE_band_edge'))
        a2 = row.get('alpha_2D_per_eV', 0.4)
        row['Nc3D_parabolic_deck_mass_cm3'] = float(f'{bm.nc3d(m_deck):.4g}')
        row['Nc3D_kane_deck_mass_cm3'] = float(f'{bm.nc3d(m_deck, ab):.4g}')
        row['Nc_q2D_deck_mass_cm3'] = float(f'{bm.n2d(m_deck) / (t * 1e-7):.4g}')
        row['Nc_q2D_kane_deck_mass_cm3'] = float(f'{bm.n2d(m_deck, a2) / (t * 1e-7):.4g}')
        row['Nc_q2D_PBE_mass_cm3'] = float(f'{bm.n2d(m_pbe) / (t * 1e-7):.4g}')
        e21 = row.get('E21_eV')
        if e21 is None and t <= 2.0:
            e21 = D3['slabs']['2.0']['E21_eV']
        row['second_subband_factor'] = r(1 + math.exp(-e21 / bm.KT), 6) if e21 else None
        row['q2D_note'] = ('first subband only: E21 = %.3f eV >> kT' % e21) if e21 else 'no computed E21 at this thickness (MODEL needed)'
    bulk = {'Eg_PBE_eV': egb, 'Eg_HSE_eV': list(eg_hse_b), 'm_e_PBE_band_edge': mb, 'alpha_PBE_per_eV': ab,
            'm_e_HSE_estimate_range': [D1['HSE']['bulk_q3']['estimate_range'][0], D1['HSE']['bulk_q1']['estimate_range'][1]],
            'chi_PBE_bulk_equivalent_eV': D3['bulk_equivalent']['EA_eV'], 'IP_PBE_bulk_equivalent_eV': D3['bulk_equivalent']['IP_eV'],
            'Nc3D_PBE_mass_cm3': float(f'{bm.nc3d(mb):.4g}'), 'Nc3D_PBE_kane_cm3': float(f'{bm.nc3d(mb, ab):.4g}'),
            'Nc3D_lit_0p208_cm3': float(f'{bm.nc3d(M_LIT):.4g}'), 'Nc3D_lit_0p208_kane_cm3': float(f'{bm.nc3d(M_LIT, ab):.4g}'),
            'Nv_cm3_k4_80atom': D1['bulk']['Nv']['conv80_k4_HL']['Nv_cm3'], 'Nv_cm3_range_all_grids': [
                min(v['Nv_cm3'] for v in D1['bulk']['Nv'].values()), max(v['Nv_cm3'] for v in D1['bulk']['Nv'].values())],
            'm_h_dos_equiv_k4': D1['bulk']['Nv']['conv80_k4_HL']['m_dos_equiv'],
            'Nv_HSE_over_PBE_k3_same_grid': [r(D1['HSE']['Nv_k3_grid_own_max'][k]['Nv_cm3'] / D1['HSE']['Nv_k3_grid_own_max']['NC_PBE']['Nv_cm3'], 3)
                                             for k in ('HSE06_q1', 'HSE06_q3')]}
    # ---------------------------------------------------------------- W, surface, Fermi level
    f09, f10, f08 = bm.load_parent('f09_iwo_bulk'), bm.load_parent('f10_iwo_slabs'), bm.load_parent('f08_slab_pdos_surface')
    w = {}
    for lab, src in (('bulk 8b', f09['8b']['filling']), ('bulk 24d', f09['24d']['filling']), ('1 nm 24d', f10['1 nm']['filling']),
                     ('2 nm 24d', f10['2 nm']['filling'])):
        w[lab] = {'W_level_minus_hostCB_Gamma_eV': src['W_rich_minus_hostCB_Gamma_eV'], 'W_level_minus_EF_Gamma_eV': src['W_rich_minus_EF_Gamma_eV'],
                  'EF_minus_hostCB_Gamma_eV': src['EF_minus_hostCB_Gamma_eV'], 'W5d_projected_electrons': src['W5d_projected_electrons'],
                  'projwfc': src['projwfc'], 'label': 'COMPUTED at 3 donated electrons per cell (1.4e21-3e21 cm^-3)'}
    w['TCAD'] = {'donor_level': 'resonant, 1.2-1.8 eV above E_C (COMPUTED at the DFT filling only)',
                 'occupation_at_device_densities': ('~0 (fully ionised) ONLY IF the resonant level stays >= 1.2 eV above E_C at device density: '
                                                    'then exp(-(E_D - E_F)/kT) < exp(-1.2/0.0259) ~ 1e-20 for E_F below E_C. INFERRED: a Kohn-Sham resonance '
                                                    'in a filled 3-electron cell does not establish dilute-limit defect ionisation (no charged-defect '
                                                    'calculation, no lower-density cell)'),
                 'deck': 'constant effective Nd0 = 2.5e17 cm^-3 (FITTED V1 amplitude, constant form ASSUMED); no W level in the deck'}
    surf = {}
    for k, lab in (('0.51', '0.51 nm'), ('0.75', '0.75 nm'), ('1.0 W (proxy)', '1 nm (W slab proxy)'), ('2.0', '2 nm pure'), ('2.0 W', '2 nm W')):
        s = f08[k]
        surf[lab] = {'VB_top_OH_share': s['VB_top']['kweighted']['OH_share'], 'CB_bottom_OH_share': s['CB_bottom']['kweighted']['OH_share'],
                     'CB_bottom_H_weight': s['CB_bottom']['kweighted']['by_element'].get('H'), 'src': s['VB_top']['src']}
    surf['TCAD'] = ('no state inside the gap of any OH-terminated slab (gaps clean, COMPUTED); the VB top is OH-surface O 2p at 0.51 / 0.75 nm '
                    'and in the 1 / 2 nm W slabs, bulk-like at 2 nm pure; the CB bottom is In 5s / O 2s with an OH share falling from 0.56 '
                    '(0.51 nm) to 0.008 (2 nm). Ideal OH termination gives no interface trap density: the deck interface sheet (ASSUMED) '
                    'and Qf (FITTED) are not DFT quantities')
    fermi = {'pure_slabs': 'insulating (fixed occupations): no physical E_F; device E_F is set by Nd, traps and bias in TCAD',
             'W_cells': {lab: v['EF_minus_hostCB_Gamma_eV'] for lab, v in w.items() if isinstance(v, dict) and 'EF_minus_hostCB_Gamma_eV' in v},
             'W_note': 'E_F 1.2-1.8 eV inside the host CB at 1.4e21-3e21 cm^-3 (degenerate DFT cells); not a device value'}
    tunnel = {'value_m0': [mb, M_LIT], 'label': 'ASSUMED',
              'note': ('the transport-normal (gate / contact tunnelling) mass of the film is not computed: the slab CB is quantised along z; '
                       'the bulk isotropic band-edge mass (PBE 0.154, HSE estimate 0.16-0.19, experiment 0.18-0.21) is the closest computed '
                       'quantity; the evanescent (imaginary-k) mass in the gap needs a complex-band-structure run. The deck tunnelling masses '
                       '(me.tunnel 0.3 / 0.1, F.AE m 0.10) are those of the Al2O3 / HfO2 barriers, not of IWO')}
    # ---------------------------------------------------------------- deck comparison
    decks = bm.load_parent('f06_confinement_laws')['decks']
    comp = {}
    for name, dk in decks.items():
        t = float(name.split('@')[1])
        row = rows[str(t)]
        dv = {k: v['value'] for k, v in dk['deck'].items()}
        comp[name] = {'run': dk['run'], 'deck': dv, 'deck_src': {k: v['src'] for k, v in dk['deck'].items()},
                      'here_Eg_deck_basis': row['Eg_deck_basis_eV'], 'here_Eg_HSE_corrected': row['Eg_HSE_corrected_eV'],
                      'here_Eg_exp_anchored': row['Eg_exp_anchored_eV'],
                      'here_chi_fit3': row['chi_deck_basis_fit3_eV'], 'here_chi_fit2': row['chi_deck_basis_fit2_eV'],
                      'here_m_deck_basis': row['m_e_deck_basis'], 'here_m_PBE': row['m_e_PBE_band_edge'],
                      'here_Nc3D_deck_mass': row['Nc3D_parabolic_deck_mass_cm3'], 'here_Nc3D_kane': row['Nc3D_kane_deck_mass_cm3'],
                      'here_Nc_q2D': row['Nc_q2D_deck_mass_cm3'], 'here_Nc_q2D_kane': row['Nc_q2D_kane_deck_mass_cm3'],
                      'deck_nv300': 1e19, 'here_Nv_bulk': bulk['Nv_cm3_k4_80atom'],
                      'diff_Eg_meV': r((row['Eg_deck_basis_eV'] - dv['eg300']) * 1000, 2),
                      'diff_chi_fit3_meV': r((row['chi_deck_basis_fit3_eV'] - dv['affinity']) * 1000, 2),
                      'diff_m': r(row['m_e_deck_basis'] - dv['mstar'], 4)}
    out = {'rows': rows, 'bulk': bulk, 'W': w, 'surface_OH': surf, 'fermi_level': fermi, 'tunnelling_mass': tunnel, 'deck_comparison': comp,
           'constants': {'chi_bulk_LITERATURE_eV': CHI_BULK_LIT, 'Eg_deck_LITERATURE_eV': EG_DECK, 'Eg_King2009_eV': EG_KING, 'm_LITERATURE': M_LIT,
                         'r': list(rr), 'Eg_HSE_bulk_eV': list(eg_hse_b), 'kT_eV': r(bm.KT, 6)}}
    bm.dump('b04_tcad', out)
    for k, v in rows.items():
        print(k, {kk: v[kk] for kk in v if kk.startswith(('Eg', 'chi', 'm_e', 'Nc'))})
    for k, v in comp.items():
        print(k, {kk: v[kk] for kk in v if kk.startswith(('diff', 'here_Nc', 'deck'))})
    print(bulk)
    figure(out)


def figure(o):
    rows = o['rows']
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_W, 2.6))
    ts = [2.0, 6.3, 13.2]
    tt = np.array(ts)
    # (a) Nc options at the device thicknesses + decks
    ax = axs[0]
    for j, (key, lab, mk) in enumerate((('Nc3D_parabolic_deck_mass_cm3', '3-D', 'o'), ('Nc3D_kane_deck_mass_cm3', '3-D Kane', 's'),
                                        ('Nc_q2D_deck_mass_cm3', 'quasi-2-D', '^'), ('Nc_q2D_kane_deck_mass_cm3', 'quasi-2-D Kane', 'v'))):
        tsel = ts if '3D' in key else [2.0]        # quasi-2-D (single subband) only where E21 >> kT is computed
        ax.plot(tsel, [rows[str(t)][key] for t in tsel], mk, color=C[j], ms=4, mfc='none', label=lab)
    for name, c in o['deck_comparison'].items():
        t = float(name.split('@')[1])
        ax.plot([t], [c['deck']['nc300']], 'x', color='k', ms=5)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'$t$ (nm)')
    ax.set_ylabel(r'$N_c$ (cm$^{-3}$)')
    ax.legend(loc='upper right', fontsize=5.6)
    fs.panel(ax, 'a', x=-0.33)
    # (b) Eg options
    ax = axs[1]
    for j, (key, lab) in enumerate((('Eg_deck_basis_eV', 'deck basis'), ('Eg_exp_anchored_eV', 'exp.-anchored'), ('Eg_HSE_corrected_eV', 'HSE-corr.'))):
        y = [rows[str(t)][key] for t in ts]
        if isinstance(y[0], list):
            y = [np.mean(v) for v in y]
        ax.plot(tt, y, 'o^s'[j], color=C[j], ms=4, mfc='none', label=lab)
    for name, c in o['deck_comparison'].items():
        ax.plot([float(name.split('@')[1])], [c['deck']['eg300']], 'x', color='k', ms=5)
    ax.set_xscale('log')
    ax.set_xlabel(r'$t$ (nm)')
    ax.set_ylabel(r'$E_g$ (eV)')
    ax.legend(loc='center right', fontsize=5.8)
    fs.panel(ax, 'b', x=-0.33)
    # (c) chi options
    ax = axs[2]
    ax.plot(tt, [rows[str(t)]['chi_deck_basis_fit3_eV'] for t in ts], 'o', color=C[0], ms=4, mfc='none', label='fit3')
    ax.plot(tt, [rows[str(t)]['chi_deck_basis_fit2_eV'] for t in ts], 's', color=C[1], ms=4, mfc='none', label='fit2')
    lo = [4.3 - rows[str(t)]['dEc_range_eV'][1] for t in ts]
    hi = [4.3 - rows[str(t)]['dEc_range_eV'][0] for t in ts]
    ax.vlines(tt, lo, hi, color=fs.GREY, lw=2.0)
    for name, c in o['deck_comparison'].items():
        ax.plot([float(name.split('@')[1])], [c['deck']['affinity']], 'x', color='k', ms=5)
    ax.set_xscale('log')
    ax.set_xlabel(r'$t$ (nm)')
    ax.set_ylabel(r'$\chi$ (eV)')
    ax.legend(loc='lower right', fontsize=5.8)
    fs.panel(ax, 'c', x=-0.33)
    for a_ in axs:
        a_.set_xticks([2, 5, 10])
        a_.set_xticklabels(['2', '5', '10'])
        a_.xaxis.set_minor_formatter(plt.NullFormatter())
        a_.set_xlim(1.6, 16)
    fig.subplots_adjust(wspace=0.55)
    bm.save(fig, 'BM8_tcad_parameters')


if __name__ == '__main__':
    main()
