"""Gaps, band edges, vacuum-referenced EA / IP, subbands and the a t^-p laws versus thickness. Writes out/b03_gaps_laws.json
and figure BM7.

Sources: band edges from out/b01_masses.json (bands.out lines + SCF grid of each slab, read by b01 from the raw outputs);
vacuum levels re-derived here from the raw *_avg.dat with qeio.slab_vacuum (points > 5 A from every atom plane; ramp of a
polar slab measured); the 2 nm two-step anchor from ../out/f03_bulk_alignment.json (UPF G = 0 bulk reference, a/2 window);
HSE06 gaps from the raw SCF outputs (SG15 NC, 80 Ry, PBE geometries).
Labels: COMPUTED (DFT number), FITTED (law through COMPUTED points), ASSUMED (rule chosen here), LITERATURE.
"""
import json
import math

import numpy as np

import bm
from bm import q, r, plt
import figstyle as fs

R = q.RES
D = json.loads((bm.OUT / 'b01_masses.json').read_text())
C = fs.CYCLE
PURE = [('0.51', 'slabL1_relax_v2'), ('0.75', 'slabL2_relax_v2'), ('1.0', 'slab1r_final_cpu'), ('2.0', 'slab2_relax_c2')]
EG_EXP = {'King2009_fundamental': 2.93, 'deck_Fan2021': 3.05}


def vac(job):
    v = q.slab_vacuum(R / job)
    half_ramp = abs(v['ramp_slope_meV_per_A']) * v['vacuum_gap_A'] / 2 / 1000
    return v, half_ramp


def hse_gaps():
    out = {}
    for lab, job in (('NC_PBE_bulk', 'nc_pbe_bulk_e80'), ('HSE_bulk_q1', 'nc_hse_bulk_e80'), ('HSE_bulk_q3_f160', 'nc_hse_bulk_q3_f160_e80'),
                     ('NC_PBE_slab1', 'nc_pbe_slab1_e80'), ('HSE_slab1_f160', 'nc_hse_slab1_f160_e80')):
        p = R / job / 'scf.out'
        h, l, s = q.homo_lumo(p)
        b = bm.read_bands(p)
        no = int(b['nelec'] / 2)
        out[lab] = {'gap_eV': q.V(r(l - h), s), 'gap_direct_Gamma_eV': r(b['E'][0, no] - b['E'][0, no - 1]),
                    'VB_grid_max_at_k_invA': r(np.linalg.norm(b['K'][int(np.argmax(b['E'][:, no - 1]))]), 4)}
    g = {k: v['gap_eV']['value'] for k, v in out.items()}
    d_pbe = g['NC_PBE_slab1'] - g['NC_PBE_bulk']
    out['dEg_NC_PBE_1nm'] = r(d_pbe)
    out['r_q1'] = r((g['HSE_slab1_f160'] - g['HSE_bulk_q1']) / d_pbe)
    out['r_q3bulk'] = r((g['HSE_slab1_f160'] - g['HSE_bulk_q3_f160']) / d_pbe)
    out['note'] = ('r = dEg(HSE)/dEg(PBE) at 1 nm only (SG15 NC, 80 Ry, PBE-PAW geometries, slab EXX q 1x1x1 with ecutfock 160 Ry; '
                   'bulk q1 and q3 bracket the bulk EXX q-convergence); the slab q-convergence is untested')
    return out


def main():
    out = {}
    bulk = D['bulk']
    egb, egb_dir = bulk['Eg_fundamental_eV'], bulk['Eg_direct_Gamma_eV']
    out['bulk'] = {'Eg_fundamental_eV': egb, 'Eg_direct_Gamma_eV': egb_dir, 'VBM_src': bulk['VBM_eV']['src'], 'CBM_src': bulk['CBM_eV']['src'],
                   'note': 'PAW-PBE, vc-relaxed a = 10.306 A; VBM 4.4 meV above VB(Gamma) at 0.2 G-H: the fundamental gap is formally indirect'}
    f03 = bm.load_parent('f03_bulk_alignment')
    ts = f03['two_step']['slab2_relax_c2']['a/2']
    out['anchor_2nm_two_step'] = {'dEc_eV': ts['dEc_eV'], 'dEv_eV': ts['dEv_eV'], 'plateau_spread_meV': ts['plateau_spread_meV'],
                                  'src': 'out/f03_bulk_alignment.json two_step.slab2_relax_c2.a/2 (UPF G=0 bulk <V> 4.16867 eV)'}
    out['hse'] = hse_gaps()
    rr = [out['hse']['r_q1'], out['hse']['r_q3bulk']]
    eg_hse_b = [out['hse']['HSE_bulk_q1']['gap_eV']['value'], out['hse']['HSE_bulk_q3_f160']['gap_eV']['value']]
    # ---------------------------------------------------------------- slabs
    rows = {}
    for lab, job in PURE:
        s = D['slabs'][lab]
        v, hr = vac(job)
        ev = v['E_vac_eV']
        vbm, cbm = s['scf_HOMO_eV']['value'], s['scf_LUMO_eV']['value']
        rows[lab] = {'job': job, 't_HH_nm': s['t_HH_nm'], 'Eg_fundamental_eV': s['Eg_scf_eV'], 'Eg_direct_Gamma_eV': s['Eg_direct_Gamma_eV'],
                     'Eg_bands_plus_grid_eV': s['Eg_fundamental_eV'], 'edge_beyond_scf_grid_meV': s['edge_beyond_scf_grid_meV'],
                     'VBM_eV': vbm, 'CBM_eV': cbm, 'edges_src': s['scf_HOMO_eV']['src'], 'VBM_location': s['VBM_location'],
                     'E_vac_eV': r(ev), 'vac_src': v['src'], 'vac_spread_meV': r(v['spread_meV'], 2), 'ramp_over_gap_meV': r(2 * hr * 1000, 1),
                     'half_ramp_sensitivity_eV': r(hr), 'EA_eV': r(ev - cbm), 'IP_eV': r(ev - vbm),
                     'dEg_eV': r(s['Eg_scf_eV'] - egb), 'dEg_direct_eV': r(s['Eg_direct_Gamma_eV'] - egb_dir),
                     'E21_eV': s['E21_Gamma_eV']['value'], 'E31_eV': s['E31_Gamma_eV']}
    ea2 = rows['2.0']['EA_eV']
    for lab in rows:
        x = rows[lab]
        x['dEc_eV'] = r(ts['dEc_eV'] + ea2 - x['EA_eV']) if lab != '2.0' else ts['dEc_eV']
        x['dEv_eV'] = r(x['dEc_eV'] - x['dEg_eV'])
        x['dEc_route'] = '2 nm two-step (a/2)' if lab == '2.0' else '2 nm two-step + EA(2 nm) - EA(t) (same termination)'
        x['CB_share'] = r(x['dEc_eV'] / x['dEg_eV'], 3)
        x['E1_eV'] = x['dEc_eV']
        x['E2_eV'] = r(x['dEc_eV'] + x['E21_eV'])
        x['E3_eV'] = r(x['dEc_eV'] + x['E31_eV'])
        x['E21_over_E1'] = r(x['E21_eV'] / x['dEc_eV'], 3)
        x['label'] = 'COMPUTED (PBE)'
        x['Eg_HSE_corrected_eV'] = [r(eg_hse_b[0] + rr[0] * x['dEg_eV']), r(eg_hse_b[1] + rr[1] * x['dEg_eV'])]
        x['Eg_exp_anchored_eV'] = {k: [r(v_ + rr[0] * x['dEg_eV']), r(v_ + rr[1] * x['dEg_eV'])] for k, v_ in EG_EXP.items()}
        x['dEc_HSE_assumed_eV'] = [r(rr[0] * x['dEc_eV']), r(rr[1] * x['dEc_eV'])]
    rows['0.75']['dEc_sensitivity_eV'] = [r(rows['0.75']['dEc_eV'] - rows['0.75']['half_ramp_sensitivity_eV']),
                                          r(rows['0.75']['dEc_eV'] + rows['0.75']['half_ramp_sensitivity_eV'])]
    out['slabs'] = rows
    out['bulk_equivalent'] = {'EA_eV': r(ea2 + ts['dEc_eV']), 'IP_eV': r(ea2 + ts['dEc_eV'] + egb),
                              'note': 'EA(2 nm) + dEc(2 nm): H-(001) termination-specific, PBE'}
    out['check_vs_f05'] = {lab: {'EA_b03': rows[lab]['EA_eV'], 'EA_f05': bm.load_parent('f05_slab_series')['slabs'][lab]['EA_eV'],
                                 'dEc_b03': rows[lab]['dEc_eV'], 'dEc_f05': bm.load_parent('f05_slab_series')['slabs'][lab]['dEc_eV']} for lab in rows}
    # ---------------------------------------------------------------- W slabs
    wsl = {}
    f10 = bm.load_parent('f10_iwo_slabs')
    for lab, job in (('1 nm', 'iwo_slab1_final_cpu'), ('2 nm', 'iwo_slab2_final_cpu')):
        b = bm.read_bands(R / job / 'scf.out')
        npure = int((b['nelec'] - 1) / 2)
        v, hr = vac(job)
        ef, sef = q.fermi(R / job / 'scf.out')
        cbm = float(b['E'][:, npure - 1].min())
        vbm = float(b['E'][:, npure - 2].max())
        wsl[lab] = {'job': job, 'E_vac_eV': r(v['E_vac_eV']), 'vac_spread_meV': r(v['spread_meV'], 2), 'ramp_over_gap_meV': r(2 * hr * 1000, 1),
                    'EA_hostCB_eV': r(v['E_vac_eV'] - cbm), 'IP_VBtop_eV': r(v['E_vac_eV'] - vbm), 'work_function_eV': r(v['E_vac_eV'] - ef),
                    'E_F_eV': q.V(ef, sef), 'gap_VBtop_hostCB_eV': r(cbm - vbm), 'EF_minus_hostCB_min_eV': r(ef - cbm),
                    'f10_EA_hostCB_eV': f10[lab]['EA_hostCB_eV'], 'f10_IP_VBtop_eV': f10[lab]['IP_VBtop_eV'],
                    'note': 'host CB min / VB top over the 3x3x1 grid; metallic cell (3 donated electrons), E_F inside the host CB'}
    out['W_slabs'] = wsl
    # ---------------------------------------------------------------- laws a t^-p
    t3 = [rows[l]['t_HH_nm'] for l in ('0.75', '1.0', '2.0')]
    t2 = t3[1:]
    t4 = [rows['0.51']['t_HH_nm']] + t3
    laws = {}
    for key in ('dEg_eV', 'dEc_eV'):
        y3 = [rows[l][key] for l in ('0.75', '1.0', '2.0')]
        laws[key] = {'fit3': bm.power_law(t3, y3), 'fit2_1and2nm': bm.power_law(t2, y3[1:]),
                     'fit4_with_0p46_diagnostic': bm.power_law(t4, [rows['0.51'][key]] + y3)}
    s75 = rows['0.75']['dEc_sensitivity_eV']
    laws['dEc_eV']['fit3_0p695_low'] = bm.power_law(t3, [s75[0], rows['1.0']['dEc_eV'], rows['2.0']['dEc_eV']])
    laws['dEc_eV']['fit3_0p695_high'] = bm.power_law(t3, [s75[1], rows['1.0']['dEc_eV'], rows['2.0']['dEc_eV']])
    yv = [-rows[l]['dEv_eV'] for l in ('0.75', '1.0', '2.0')]
    laws['minus_dEv_eV'] = {'fit3': bm.power_law(t3, yv), 'fit2_1and2nm': bm.power_law(t2, yv[1:]),
                            'verdict': ('no meaningful power law: -dEv is 0.0521 eV at 0.930 nm and 0.0540 eV at 1.962 nm (equal within the '
                                        '15-30 meV spread of the alignment routes, non-monotonic); VB-top character (../out/f08): OH-surface O 2p '
                                        'at 0.51 nm (OH share 0.98) and 0.75 nm (0.75), 0.72 in the 1 nm W slab (no projection of the pure 1 nm), '
                                        'bulk-like interior O 2p in the pure 2 nm slab (0.001)')}
    me = {l: D['slabs'][l]['electron_summary']['tensor_2d']['m_dos_2d'] for l in rows}
    m4 = {l: D['slabs'][l]['electron_summary']['m_4pt_intercept_[100]'] for l in rows}
    mb = D['bulk']['electron_summary']['m_dos']
    mb4 = D['bulk']['electron_summary']['m_parabolic_4pt_intercept_by_dir']['[100]']
    laws['dm_e_band_edge'] = {'fit3': bm.power_law(t3, [me[l] - mb for l in ('0.75', '1.0', '2.0')]),
                              'fit2_1and2nm': bm.power_law(t2, [me[l] - mb for l in ('1.0', '2.0')]),
                              'm_bulk': mb, 'basis': 'Kane band-edge 2-D DOS mass minus bulk Kane band-edge mass (b01)'}
    laws['dm_e_4pt_deck_basis'] = {'fit3': bm.power_law(t3, [m4[l] - mb4 for l in ('0.75', '1.0', '2.0')]),
                                   'm_bulk': mb4, 'basis': '4-point free-intercept parabola [100] minus bulk 4-point (the V2/V3 deck basis)'}
    laws['m_h'] = {'verdict': 'no law: a single-band hole mass is meaningful only at 0.75 nm (b01 criteria); the hole DOS-equivalent mass '
                              'from the Boltzmann sum does not vary monotonically with t'}
    for k in ('dEg_eV', 'dEc_eV'):
        for fk, f in list(laws[k].items()):
            if isinstance(f, dict) and f.get('ok'):
                f['at_nm'] = {str(t): r(bm.law(f, t), 4) for t in (2.0, 6.3, 13.2)}
    for k in ('dm_e_band_edge', 'dm_e_4pt_deck_basis'):
        for fk, f in list(laws[k].items()):
            if isinstance(f, dict) and f.get('ok'):
                f['at_nm'] = {str(t): r(bm.law(f, t), 4) for t in (2.0, 6.3, 13.2)}
    cfg = bm.load_parent('f06_confinement_laws')['config']
    laws['config_V3'] = cfg['V3']
    laws['config_V2'] = cfg['V2']
    laws['HSE_scaled_dEg'] = {'rule': 'ASSUMED: dEg_HSE(t) = r dEg_PBE(t), r in [r_q1, r_q3bulk], thickness-independent',
                              'r': rr, 'fit3_a_scaled': [r(laws['dEg_eV']['fit3']['a'] * x, 5) for x in rr], 'p': laws['dEg_eV']['fit3']['p']}
    out['laws'] = laws
    bm.dump('b03_gaps_laws', out)
    for l in rows:
        x = rows[l]
        print(l, {k: x[k] for k in ('t_HH_nm', 'Eg_fundamental_eV', 'dEg_eV', 'EA_eV', 'IP_eV', 'dEc_eV', 'dEv_eV', 'E21_eV', 'Eg_HSE_corrected_eV', 'half_ramp_sensitivity_eV')})
    print('bulk-eq', out['bulk_equivalent'], 'W', {k: (v['EA_hostCB_eV'], v['IP_VBtop_eV'], v['work_function_eV']) for k, v in wsl.items()})
    for k in ('dEg_eV', 'dEc_eV', 'minus_dEv_eV', 'dm_e_band_edge', 'dm_e_4pt_deck_basis'):
        for fk, f in laws[k].items():
            if isinstance(f, dict) and 'a' in f:
                print(k, fk, f['a'], f['p'], f.get('sigma_a'), f.get('sigma_p'), f.get('rel_resid'), f.get('at_nm'))
    print('r', rr, 'HSE gaps', {k: v['gap_eV']['value'] for k, v in out['hse'].items() if isinstance(v, dict) and 'gap_eV' in v})
    figure(out)


def figure(o):
    rows = o['slabs']
    labs = ['0.51', '0.75', '1.0', '2.0']
    t = np.array([rows[l]['t_HH_nm'] for l in labs])
    fig, axs = plt.subplots(1, 4, figsize=(fs.FULL_W, 2.6))
    tt = np.linspace(0.4, 15, 300)
    # (a) gaps
    ax = axs[0]
    eg = np.array([rows[l]['Eg_fundamental_eV'] for l in labs])
    egd = np.array([rows[l]['Eg_direct_Gamma_eV'] for l in labs])
    ax.plot(t[1:], eg[1:], 'o', color=C[0], ms=4.5, label='PBE')
    ax.plot(t[:1], eg[:1], 'o', color=C[0], ms=4.5, mfc='white')
    ax.plot(t, egd, '_', color='k', ms=7, label=r'PBE direct $\Gamma$')
    hs = np.array([rows[l]['Eg_HSE_corrected_eV'] for l in labs])
    ax.plot(t, hs.mean(axis=1), 'D', color=C[1], ms=3.6, mfc='none', label=r'HSE-corr. ($r$)')
    ax.plot(0.9303 * 1.08, o['hse']['HSE_slab1_f160']['gap_eV']['value'], 's', color=C[1], ms=3.8, label='HSE06 1 nm')
    ax.axhline(o['bulk']['Eg_fundamental_eV'], color=C[0], ls='--', lw=0.8)
    ax.axhline(o['hse']['HSE_bulk_q3_f160']['gap_eV']['value'], color=C[1], ls='--', lw=0.8)
    ax.axhspan(2.93 - 0.15, 2.93 + 0.15, color=fs.GREY, alpha=0.2, lw=0)
    ax.set_xscale('log')
    ax.set_xlabel(r'$t_\mathrm{HH}$ (nm)')
    ax.set_ylabel(r'$E_g$ (eV)')
    ax.legend(loc='upper right', fontsize=5.2, handlelength=1.2)
    fs.panel(ax, 'a', x=-0.33)
    # (b) dEg, dEc, -dEv with laws
    ax = axs[1]
    L = o['laws']
    for j, (key, lab_) in enumerate((('dEg_eV', r'$\Delta E_g$'), ('dEc_eV', r'$\Delta E_c$'))):
        y = np.array([rows[l][key] for l in labs])
        ax.plot(t[1:], y[1:], 'os'[j], color=C[j], ms=4.2, label=lab_)
        ax.plot(t[:1], y[:1], 'os'[j], color=C[j], ms=4.2, mfc='white')
        ax.plot(tt, bm.law(L[key]['fit3'], tt), color=C[j], lw=0.9)
        ax.plot(tt, bm.law(L[key]['fit2_1and2nm'], tt), color=C[j], lw=0.9, ls='--')
    s = rows['0.75']['dEc_sensitivity_eV']
    ax.vlines(rows['0.75']['t_HH_nm'], s[0], s[1], color=C[1], lw=1.0)
    yv = -np.array([rows[l]['dEv_eV'] for l in labs])
    ax.plot(t[1:], yv[1:], '^', color=C[2], ms=4.2, label=r'$-\Delta E_v$')
    ax.plot(t[:1], yv[:1], '^', color=C[2], ms=4.2, mfc='white')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.4, 15)
    ax.set_ylim(0.01, 4)
    ax.set_xlabel(r'$t_\mathrm{HH}$ (nm)')
    ax.set_ylabel('energy shift (eV)')
    ax.legend(loc='lower left', fontsize=6.0)
    fs.panel(ax, 'b', x=-0.33)
    # (c) EA, IP
    ax = axs[2]
    ea = np.array([rows[l]['EA_eV'] for l in labs])
    ip = np.array([rows[l]['IP_eV'] for l in labs])
    ax.plot(t, ea, 'o', color=C[0], ms=4.5, label='EA')
    ax.plot(t, ip, 's', color=C[1], ms=4.2, label='IP')
    hr = rows['0.75']['half_ramp_sensitivity_eV']
    ax.errorbar([rows['0.75']['t_HH_nm']] * 2, [rows['0.75']['EA_eV'], rows['0.75']['IP_eV']], yerr=hr, fmt='none', ecolor='k', lw=0.8, capsize=2)
    for lab, tw in (('1 nm', 0.9303), ('2 nm', 1.9623)):
        w = o['W_slabs'][lab]
        ax.plot([tw * 1.07], [w['EA_hostCB_eV']], 'D', color=C[0], ms=3.8, mfc='none')
        ax.plot([tw * 1.07], [w['IP_VBtop_eV']], 'D', color=C[1], ms=3.8, mfc='none')
    ax.axhline(o['bulk_equivalent']['EA_eV'], color=C[0], ls='--', lw=0.8)
    ax.axhline(o['bulk_equivalent']['IP_eV'], color=C[1], ls='--', lw=0.8)
    ax.set_xscale('log')
    ax.set_xlabel(r'$t_\mathrm{HH}$ (nm)')
    ax.set_ylabel('energy (eV)')
    ax.legend(loc='lower right', fontsize=6.0)
    fs.panel(ax, 'c', x=-0.33)
    # (d) subbands relative to the bulk CBM
    ax = axs[3]
    for j, key in enumerate(('E1_eV', 'E2_eV', 'E3_eV')):
        y = np.array([rows[l][key] for l in labs])
        ax.plot(t, y, 'o^v'[j], color=C[j], ms=4.2, mfc='none' if j else C[j], label=key[:2])
    ax.set_xscale('log')
    ax.set_xlabel(r'$t_\mathrm{HH}$ (nm)')
    ax.set_ylabel(r'$E-E_\mathrm{CBM,bulk}$ (eV)')
    ax.legend(loc='upper right', fontsize=6.0)
    fs.panel(ax, 'd', x=-0.33)
    for a_ in axs:
        a_.set_xticks([0.5, 1, 2] if a_ is not axs[1] else [0.5, 1, 2, 5, 10])
        a_.set_xticklabels(['0.5', '1', '2'] if a_ is not axs[1] else ['0.5', '1', '2', '5', '10'])
        a_.xaxis.set_minor_formatter(plt.NullFormatter())
    for a_ in (axs[0], axs[2], axs[3]):
        a_.set_xlim(0.4, 2.4)
    fig.subplots_adjust(wspace=0.62)
    bm.save(fig, 'BM7_gaps_edges_laws')


if __name__ == '__main__':
    main()
