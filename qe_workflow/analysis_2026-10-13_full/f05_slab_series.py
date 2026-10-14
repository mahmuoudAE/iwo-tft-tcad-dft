"""Fig. 5: relaxed H/OH-terminated In2O3(001) slabs 0.51 / 0.75 / 1 / 2 nm (Lin et al. 2022 recipe), PAW-PBE.

Per slab (final SCF folder; relaxation from its vcrelax.out):
  relaxation   'bfgs converged' line, final enthalpy, largest force component and total force at the converged step
  geometry     H-H, O-O and In-In thickness, in-plane cell (scf.in), composition, O bonded to H, In-O coordination (< 2.6 A)
  gap          HOMO/LUMO of the SCF (3x3x1, includes Gamma); dEg = gap - bulk fundamental gap (f02)
  EA, IP       vacuum level > 5 A from every atom plane (qeio.slab_vacuum); asymmetry top - bottom
  m*           in-plane CB mass from bands.out: Gamma + 10 points along [100] and 10 along [110], parabolic fit for
               |k| <= 0.05 1/A, with free intercept (as the earlier read-out) and through the origin
  E21          next empty level above the CBM at Gamma (bands.out, first k)
dEc/dEv: 2 nm from the two-step alignment (f03, a/2); thinner films from dEc(t) = dEc(2) + EA(2) - EA(t) (same
termination; RESULTS_LOG 2026-10-05 'EA/IP route'), dEv = dEc - dEg.
"""
import json

import numpy as np

import qeio as q
from figstyle import plt, save, panel, CYCLE

SLABS = [('0.51', 'slabL1_relax_v2', 'slabL1_relax_v2'), ('0.75', 'slabL2_relax_v2', 'slabL2_relax_v2'),
         ('1.0', 'slab1r_final_cpu', 'slab1_relax_gpu'), ('2.0', 'slab2_relax_c2', 'slab2_relax_c2')]
EXTRA = [('1.0', 'slab1_relax_gpu'), ('2.0', 'slab2r_pdos_cpu'), ('2.0', 'slab2r_final_cpu_checkpoint')]


def relax_info(job):
    p = q.RES / job / 'vcrelax.out'
    mb, ib = q.last(p, r'bfgs converged in\s+(\d+) scf cycles and\s+(\d+) bfgs steps')
    mh, ih = q.last(p, r'Final enthalpy\s+=\s+(-?[\d.]+) Ry')
    L = q.lines(str(p))
    # forces of the converged step: the last 'Forces acting on atoms' block before 'bfgs converged'
    fa = max(i for i in range(ib) if 'Forces acting on atoms' in L[i])
    F = []
    for l in L[fa + 1:fa + 2000]:
        if 'force =' in l and 'atom' in l:
            F.append(q.nums(l.split('force =')[1])[:3])
        elif 'Total force' in l:
            tf = float(l.split('=')[1].split()[0]); tl = L.index(l, fa) + 1
            break
    F = np.abs(np.array(F))
    return {'bfgs': q.V(f'{mb.group(1)} scf cycles, {mb.group(2)} bfgs steps', q.src(p, ib)),
            'final_enthalpy_Ry': q.V(float(mh.group(1)), q.src(p, ih)),
            'max_force_component_Ry_bohr': q.V(round(float(F.max()), 6), q.src(p, fa + 1)),
            'total_force_Ry_bohr': q.V(tf, q.src(p, tl)), 'n_atoms_forces': int(len(F))}


def geometry(job):
    cell, sym, frac, cart, s_in = q.read_struct_in(q.RES / job / 'scf.in')
    z = cart[:, 2]

    def ext(el):
        zz = z[[s == el for s in sym]]
        return float(zz.max() - zz.min())
    comp = {e: sym.count(e) for e in sorted(set(sym))}
    # O bonded to H (O-H < 1.15 A) and In coordination by O (< 2.6 A)
    oh = {i for i, s in enumerate(sym) if s == 'O' and q.neighbours(cell, frac, i, 'H', sym, 1.15)}
    cn = [len(q.neighbours(cell, frac, i, 'O', sym, 2.6)) for i, s in enumerate(sym) if s == 'In']
    return {'thickness_HH_nm': q.V(round(ext('H') / 10, 4), s_in), 'thickness_OO_nm': round(ext('O') / 10, 4),
            'thickness_InIn_nm': round(ext('In') / 10, 4), 'inplane_A': [round(float(np.linalg.norm(cell[0])), 4), round(float(np.linalg.norm(cell[1])), 4)],
            'composition': comp, 'O_bonded_to_H': len(oh), 'O_total': comp.get('O', 0),
            'In_CN_mean': round(float(np.mean(cn)), 2), 'In_CN_hist': {str(k): cn.count(k) for k in sorted(set(cn))}}


def mass(job, nocc):
    p = q.RES / job / 'bands.out'
    if not p.exists() or not q.job_done(p):
        return None
    alat, s_al = q.alat_A(p)
    b = q.eig_blocks(p)
    k = np.array([x[0] for x in b]) * 2 * np.pi / alat
    ev = np.array([x[1][:nocc + 3] for x in b])
    out = {'n_k': len(b), 'alat_A': round(alat, 5)}
    for name, idx in (('[100]', list(range(0, 11))), ('[110]', [0] + list(range(11, 21)))):
        kk = np.linalg.norm(k[idx], axis=1); ee = ev[idx, nocc] - ev[0, nocc]
        s = kk <= 0.05 + 1e-6
        c1 = np.polyfit(kk[s] ** 2, ee[s], 1)[0]
        c0 = float(np.sum(kk[s] ** 2 * ee[s]) / np.sum(kk[s] ** 4))
        out[name] = {'m_intercept_m0': round(q.H2M / c1, 4), 'm_origin_m0': round(q.H2M / c0, 4), 'n_fit': int(s.sum()),
                     'kmax_fit_invA': round(float(kk[s].max()), 4)}
    out['E21_Gamma_eV'] = q.V(round(float(ev[0, nocc + 1] - ev[0, nocc]), 4), b[0][2])
    out['CBM_Gamma_bands_eV'] = float(ev[0, nocc])
    out['src'] = f'{b[0][2]} .. {b[20][2]}'
    return out


def main():
    f02 = json.loads((q.OUT / 'f02_bulk_structure_bands.json').read_text())
    f03 = json.loads((q.OUT / 'f03_bulk_alignment.json').read_text())
    eg_b = f02['bands_path']['Eg_fundamental_eV']
    m_b = f02['mass']['[100]']['m_parabolic_intercept_m0']
    m_b0 = f02['mass']['[100]']['m_parabolic_origin_m0']
    res = {'bulk_gap_eV': eg_b, 'bulk_mass_m0': m_b, 'bulk_mass_origin_m0': m_b0, 'slabs': {}, 'extra': {}}
    for lab, job, rjob in SLABS:
        d = q.RES / job
        h, l, sg = q.homo_lumo(d / 'scf.out')
        ne, sne = q.nelec(d / 'scf.out')
        nocc = int(round(ne)) // 2
        vv = q.slab_vacuum(d)
        r = {'job': job, 'relax_job': rjob, 'version': q.version(d / 'scf.out')[0], 'symops': q.V(*q.symops(d / 'scf.out')),
             'n_electrons': q.V(ne, sne), 'n_occ': nocc, 'VBM_eV': q.V(h, sg), 'CBM_eV': q.V(l, sg), 'gap_eV': round(l - h, 4),
             'dEg_eV': round(l - h - eg_b, 4), 'E_vac_eV': q.V(round(vv['E_vac_eV'], 4), vv['src']), 'E_vac_spread_meV': round(vv['spread_meV'], 2),
             'vacuum_top_minus_bottom_meV': round((vv['above_top_eV'] - vv['below_bottom_eV']) * 1000, 2) if vv['below_bottom_eV'] is not None and vv['above_top_eV'] is not None else None,
             'EA_eV': round(vv['E_vac_eV'] - l, 4), 'IP_eV': round(vv['E_vac_eV'] - h, 4),
             'vacuum_ramp_slope_meV_per_A': round(vv['ramp_slope_meV_per_A'], 3), 'vacuum_ramp_over_window_meV': round(vv['ramp_over_window_meV'], 1),
             'vacuum_ramp_over_gap_meV': round(vv['ramp_slope_meV_per_A'] * vv['vacuum_gap_A'], 1),
             'scf_iterations': q.V(*q.scf_iters(d / 'scf.out'))}
        r.update(geometry(job))
        r['relax'] = relax_info(rjob)
        r['mass'] = mass(job, nocc)
        if r['mass']:
            r['dm_m0'] = round(r['mass']['[100]']['m_intercept_m0'] - m_b, 4)
            r['dm_origin_m0'] = round(r['mass']['[100]']['m_origin_m0'] - m_b0, 4)
        res['slabs'][lab] = r
    # extra runs of the same geometries (consistency)
    for lab, job in EXTRA:
        d = q.RES / job
        h, l, sg = q.homo_lumo(d / 'scf.out')
        ne, _ = q.nelec(d / 'scf.out')
        e = {'job': job, 'version': q.version(d / 'scf.out')[0], 'gap_eV': q.V(round(l - h, 4), sg), 'VBM_eV': h, 'CBM_eV': l}
        if any((d).glob('*_avg.dat')):
            vv = q.slab_vacuum(d)
            e.update({'EA_eV': round(vv['E_vac_eV'] - l, 4), 'IP_eV': round(vv['E_vac_eV'] - h, 4)})
        m = mass(job, int(round(ne)) // 2)
        if m:
            e['mass_100_intercept_m0'] = m['[100]']['m_intercept_m0']; e['mass_110_intercept_m0'] = m['[110]']['m_intercept_m0']
            e['E21_Gamma_eV'] = m['E21_Gamma_eV']['value']
        res['extra'][f'{lab}:{job}'] = e
    # dEc / dEv
    ts = f03['two_step']['slab2_relax_c2']['a/2']
    dec2 = ts['dEc_eV']
    ea2 = res['slabs']['2.0']['EA_eV']
    for lab, r in res['slabs'].items():
        if lab == '2.0':
            r['dEc_eV'], r['dEv_eV'], r['dEc_route'] = dec2, ts['dEv_eV'], 'two-step a/2 (f03)'
        else:
            r['dEc_eV'] = round(dec2 + ea2 - r['EA_eV'], 4)
            r['dEv_eV'] = round(r['dEc_eV'] - r['dEg_eV'], 4)
            r['dEc_route'] = '2 nm two-step + EA(2 nm) - EA(t)'
        r['CB_share'] = round(r['dEc_eV'] / r['dEg_eV'], 3)
    # 1 -> 2 nm differences (RESULTS_LOG 2026-10-04 partition)
    s1, s2 = res['slabs']['1.0'], res['slabs']['2.0']
    res['partition_1_to_2'] = {'EA2_minus_EA1': round(s2['EA_eV'] - s1['EA_eV'], 4), 'IP1_minus_IP2': round(s1['IP_eV'] - s2['IP_eV'], 4),
                               'dEg1_minus_dEg2': round(s1['dEg_eV'] - s2['dEg_eV'], 4)}
    q.dump('f05_slab_series', res)
    for lab, r in res['slabs'].items():
        print(lab, r['job'], 'HH', r['thickness_HH_nm']['value'], 'OO', r['thickness_OO_nm'], 'ab', r['inplane_A'], r['composition'],
              'OH', r['O_bonded_to_H'], 'CN', r['In_CN_mean'], r['In_CN_hist'])
        print('   gap', r['gap_eV'], 'dEg', r['dEg_eV'], 'EA', r['EA_eV'], 'IP', r['IP_eV'], 'asym', r['vacuum_top_minus_bottom_meV'], 'spread', r['E_vac_spread_meV'],
              'dEc', r['dEc_eV'], 'dEv', r['dEv_eV'], 'share', r['CB_share'], 'ops', r['symops']['value'])
        print('   relax', r['relax']['bfgs']['value'], r['relax']['final_enthalpy_Ry']['value'], 'maxF', r['relax']['max_force_component_Ry_bohr']['value'],
              'totF', r['relax']['total_force_Ry_bohr']['value'])
        if r['mass']:
            print('   mass', r['mass']['[100]'], r['mass']['[110]'], 'E21', r['mass']['E21_Gamma_eV']['value'], 'dm', r['dm_m0'], r['dm_origin_m0'])
    print(res['extra'])
    print(res['partition_1_to_2'])

    # ---- figure: (a) band edges vs vacuum for each thickness, (b) planar averages
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.7), gridspec_kw={'width_ratios': [1, 1.5]})
    labs = list(res['slabs'])
    for i, lab in enumerate(labs):
        r = res['slabs'][lab]
        ax[0].hlines(-r['EA_eV'], i - 0.3, i + 0.3, color=CYCLE[0], lw=1.6)
        ax[0].hlines(-r['IP_eV'], i - 0.3, i + 0.3, color=CYCLE[1], lw=1.6)
    ax[0].plot([], [], color=CYCLE[0], lw=1.6, label='CBM')
    ax[0].plot([], [], color=CYCLE[1], lw=1.6, label='VBM')
    ax[0].set_xticks(range(len(labs)))
    ax[0].set_xticklabels([f"{res['slabs'][l]['thickness_HH_nm']['value']:.3f}" for l in labs])
    ax[0].minorticks_off(); ax[0].tick_params(axis='y', which='minor', left=True, right=True)
    ax[0].yaxis.set_minor_locator(plt.matplotlib.ticker.AutoMinorLocator())
    ax[0].set_xlabel(r'$t_{\rm H-H}$ (nm)'); ax[0].set_ylabel(r'$E - E_{\rm vac}$ (eV)')
    ax[0].set_xlim(-0.6, len(labs) - 0.4); ax[0].set_ylim(-7, -2)
    ax[0].legend(loc='upper right', fontsize=7)
    panel(ax[0], 'a', x=-0.25)
    for i, lab in enumerate(labs):
        r = res['slabs'][lab]
        z, vp, vm, f = q.avg_dat(q.RES / r['job'])
        cell, sym, frac, cart, s_in = q.read_struct_in(q.RES / r['job'] / 'scf.in')
        zc = 0.5 * (cart[:, 2].min() + cart[:, 2].max())
        ax[1].plot(z * q.BOHR - zc, vp * q.RY - r['E_vac_eV']['value'], color=CYCLE[i], lw=0.7, label=f"{r['thickness_HH_nm']['value']:.3f} nm")
    ax[1].set_xlim(-20, 20)
    ax[1].set_xlabel(r'$z - z_{\rm centre}$ (Å)'); ax[1].set_ylabel(r'$\bar V(z) - E_{\rm vac}$ (eV)')
    ax[1].legend(loc='lower right', fontsize=7)
    panel(ax[1], 'b', x=-0.16)
    fig.tight_layout()
    save(fig, 'fig05_slab_series_levels')


if __name__ == '__main__':
    main()
