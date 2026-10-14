"""Fig. 10: W in the relaxed 1 nm and 2 nm In2O3(001) slabs (one W on a central 24d site; same cell, termination and
settings as the pure twins; MV 0.01 Ry; QE 7.5 CPU final SCF + planar average + projwfc).

1 nm: iwo_slab1_final_cpu (relax: iwo_slab1_W24d_x1/relax.out), VB top = band 311 (pure twin 312 occupied).
2 nm: iwo_slab2_final_cpu (relax: iwo_slab2_W24d_checkpoint/relax.out; final SCF conv_thr 1e-8, beta 0.1 after the
      1e-9 SCF stalled - RESULTS_LOG 2026-10-05), VB top = band 663 (pure twin 664).
Vacuum level as for the pure slabs (> 5 A from every atom plane); EA = E_vac - host CB bottom (Gamma), IP = E_vac - VB top
(Gamma), work function = E_vac - E_F. Pure twins: slab1r_final_cpu, slab2r_pdos_cpu (same geometry family, relaxed pure).
"""
import json

import numpy as np

import qeio as q
import iwo_common as iw
from figstyle import plt, save, panel, CYCLE, EL

CASES = [('1 nm', 'iwo_slab1_final_cpu', 'iwo_slab1_W24d_x1', 311, 'slab1r_final_cpu'),
         ('2 nm', 'iwo_slab2_final_cpu', 'iwo_slab2_W24d_checkpoint', 663, 'slab2r_pdos_cpu')]


def main():
    res = {}
    for lab, job, rjob, vb, twin in CASES:
        d = q.RES / job
        r = {'job': job, 'relax_job': rjob, 'version': q.version(d / 'scf.out')[0]}
        rp = q.RES / rjob / 'relax.out'
        mb, ib = q.last(rp, r'bfgs converged in\s+(\d+) scf cycles and\s+(\d+) bfgs steps')
        me, ie = q.last(rp, r'Final energy\s+=\s+(-?[\d.]+) Ry')
        r['relax'] = {'bfgs': q.V(f'{mb.group(1)} scf, {mb.group(2)} bfgs', q.src(rp, ib)), 'E_final_Ry': q.V(float(me.group(1)), q.src(rp, ie))}
        r['E_scf_Ry'] = q.V(*q.etot(d / 'scf.out'))
        r['E_scf_minus_relax_Ry'] = round(r['E_scf_Ry']['value'] - r['relax']['E_final_Ry']['value'], 8)
        r['scf_iterations'] = q.V(*q.scf_iters(d / 'scf.out'))
        # geometry: W-O bonds and displacements during the relaxation
        cf, sym, frac, s_fin = q.final_struct_out(rp)
        cell0, sym0, frac0, cart0, s0 = q.read_struct_in(q.RES / rjob / 'relax.in')
        cell, symS, fracS, cartS, sS = q.read_struct_in(d / 'scf.in')
        cf = cell0 if cf is None else cf
        w = sym.index('W')
        r['W_O_A'] = q.V([round(x, 4) for x in q.neighbours(cf, frac, w, 'O', sym, 2.6)], s_fin)
        r['W_O_mean_A'] = round(float(np.mean(r['W_O_A']['value'])), 4)
        disp = frac - frac0; disp -= np.rint(disp); disp = np.linalg.norm(disp @ cf, axis=1)
        r['max_displacement_A'] = round(float(disp.max()), 3); r['W_displacement_A'] = round(float(disp[w]), 3)
        dsc = fracS - frac; dsc -= np.rint(dsc)
        r['scf_geometry_minus_relax_final_A'] = float(np.abs(dsc @ cf).max())
        r['composition'] = {e: sym.count(e) for e in sorted(set(sym))}
        fl = iw.filling(job, 'scf.out', vb=vb)
        r['filling'] = iw.strip(fl)
        vv = q.slab_vacuum(d)
        cb_g = fl['bands'][str(vb + 1)]['E_Gamma_minus_EF_eV'] + fl['E_F_eV']['value']
        vb_g = fl['bands'][str(vb)]['E_Gamma_minus_EF_eV'] + fl['E_F_eV']['value']
        r['vacuum'] = {'E_vac_eV': q.V(round(vv['E_vac_eV'], 4), vv['src']), 'spread_meV': round(vv['spread_meV'], 2),
                       'ramp_over_gap_meV': round(vv['ramp_slope_meV_per_A'] * vv['vacuum_gap_A'], 1)}
        r['EA_hostCB_eV'] = round(vv['E_vac_eV'] - cb_g, 4)
        r['IP_VBtop_eV'] = round(vv['E_vac_eV'] - vb_g, 4)
        r['work_function_eV'] = round(vv['E_vac_eV'] - fl['E_F_eV']['value'], 4)
        # pure twin
        tw = q.RES / twin
        h, l, sg = q.homo_lumo(tw / 'scf.out')
        tv = q.slab_vacuum(tw)
        r['pure_twin'] = {'job': twin, 'gap_eV': q.V(round(l - h, 4), sg), 'EA_eV': round(tv['E_vac_eV'] - l, 4), 'IP_eV': round(tv['E_vac_eV'] - h, 4)}
        r['W_effect'] = {'dGap_eV': round(fl['gap_VBtop_to_hostCB_Gamma_eV'] - (l - h), 4), 'dEA_eV': round(r['EA_hostCB_eV'] - r['pure_twin']['EA_eV'], 4),
                         'dIP_eV': round(r['IP_VBtop_eV'] - r['pure_twin']['IP_eV'], 4)}
        cell_area = abs(np.linalg.det(cf[:2, :2])) * 1e-16
        zH = (np.array(frac) @ cf)[[s == 'H' for s in sym], 2]
        r['donated_sheet_density_cm2'] = float(f'{3 / cell_area:.4e}')
        r['donated_density_cm3_HH'] = float(f'{3 / (cell_area * (zH.max() - zH.min()) * 1e-8):.4e}')
        r['_fl'] = fl
        res[lab] = r
    out = {k: {kk: vv for kk, vv in v.items() if not kk.startswith('_')} for k, v in res.items()}
    q.dump('f10_iwo_slabs', out)
    for lab, r in out.items():
        fl = r['filling']
        print(lab, r['relax'], 'Escf-Erelax', r['E_scf_minus_relax_Ry'], 'W-O', r['W_O_A']['value'], r['W_O_mean_A'], 'maxdisp', r['max_displacement_A'], 'W', r['W_displacement_A'],
              'scf-geo', r['scf_geometry_minus_relax_final_A'], r['composition'])
        print('  EF', fl['E_F_eV']['value'], 'N', fl['N_from_MV'], fl['N_from_printed_occ'], 'above VB', fl['electrons_above_VB_top'], 'W5d e', fl['W5d_projected_electrons'],
              'gap', fl['gap_VBtop_to_hostCB_Gamma_eV'], 'EF-CB', fl['EF_minus_hostCB_Gamma_eV'], 'CBmin-EF', fl['hostCB_min_over_k_minus_EF_eV'],
              'Wrich', fl['W_rich_band_Gamma'], fl['W_rich_minus_hostCB_Gamma_eV'], fl['W_rich_minus_EF_Gamma_eV'])
        print('  vac', r['vacuum'], 'EA', r['EA_hostCB_eV'], 'IP', r['IP_VBtop_eV'], 'WF', r['work_function_eV'], 'twin', r['pure_twin'], 'W effect', r['W_effect'],
              'n2D', r['donated_sheet_density_cm2'], 'n3D', r['donated_density_cm3_HH'])
        for n, b in fl['bands'].items():
            print('   ', n, {k: b[k] for k in ('E_Gamma_minus_EF_eV', 'Wd_Gamma', 'Ins_Gamma', 'Op_Gamma', 'Os_Gamma', 'Wd_kavg', 'width_eV', 'electrons')})

    f09 = json.loads((q.OUT / 'f09_iwo_bulk.json').read_text())
    fig, ax = plt.subplots(1, 3, figsize=(6.8, 2.5), gridspec_kw={'width_ratios': [1, 1, 0.9]})
    for i, (lab, job, rjob, vb, twin) in enumerate(CASES):
        d = q.RES / job
        ef = out[lab]['filling']['E_F_eV']['value']
        tot = np.loadtxt(next((d / 'pdos').glob('*.pdos_tot')))
        E, ins, _ = q.pdos_sum(d, lambda a, e, w, L: e == 'In' and L == 's')
        _, opp, _ = q.pdos_sum(d, lambda a, e, w, L: e == 'O' and L == 'p')
        _, wdd, _ = q.pdos_sum(d, lambda a, e, w, L: e == 'W' and L == 'd')
        a_ = ax[i]
        a_.plot(tot[:, 0] - ef, tot[:, 1], color='k', lw=0.7, label='total')
        a_.plot(E - ef, ins, color=EL['In'], lw=0.9, label='In 5s')
        a_.plot(E - ef, opp, color=EL['O'], lw=0.9, label='O 2p')
        a_.plot(E - ef, 5 * wdd, color=EL['W'], lw=1.1, label=r'W 5d $\times$5')
        win = (tot[:, 0] - ef > -2) & (tot[:, 0] - ef < 3)
        ytop = 1.1 * max(tot[win, 1].max(), (5 * wdd)[(E - ef > -2) & (E - ef < 3)].max())
        a_.axvline(0, color='0.5', ls='--', lw=0.6)
        a_.axvline(out[lab]['filling']['bands'][str(vb + 1)]['E_Gamma_minus_EF_eV'], color=EL['In'], ls=':', lw=0.8)
        a_.set_xlim(-3, 3); a_.set_ylim(0, ytop)
        a_.set_xlabel(r'$E - E_F$ (eV)')
        if i == 0:
            a_.set_ylabel('PDOS (states eV$^{-1}$ cell$^{-1}$)')
            a_.legend(loc='upper left', fontsize=6.3)
        panel(a_, 'ab'[i], x=-0.2 if i == 0 else -0.12)
    for i, lab in enumerate(['1 nm', '2 nm']):
        sc = np.array(out[lab]['filling']['gamma_scatter'])
        ax[2].plot(sc[:, 0], sc[:, 1], ['o', 's'][i], mfc='none', color=CYCLE[i], ms=3.5, label=f'{lab} slab')
    sc = np.array(f09['24d']['filling']['gamma_scatter'])
    ax[2].plot(sc[:, 0], sc[:, 1], '^', mfc='none', color='0.45', ms=3.5, label='bulk (24d)')
    ax[2].axvline(0, color='0.5', ls='--', lw=0.6)
    ax[2].set_xlim(-3, 3); ax[2].set_ylim(-0.02, 0.8)
    ax[2].set_xlabel(r'$E_n(\Gamma) - E_F$ (eV)'); ax[2].set_ylabel(r'W 5d weight at $\Gamma$')
    ax[2].legend(loc='upper left', fontsize=6.5)
    panel(ax[2], 'c', x=-0.25)
    fig.tight_layout()
    save(fig, 'fig10_iwo_slabs')


if __name__ == '__main__':
    main()
