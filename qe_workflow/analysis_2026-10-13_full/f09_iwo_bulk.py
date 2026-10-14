"""Fig. 9: W in bulk bixbyite In2O3 (80-atom conventional cells In31 W O48, 3.125 % W per cation, fixed PBE lattice
a = 10.3061 A, PAW-PBE 71/568 Ry, MV 0.01 Ry, QE 7.5): site preference 8b vs 24d, W-O bonds, spin, band characters,
electron partition, PDOS.

Files: cern_htcondor/results/iwo_W{8b,24d}/relax.out (3x3x3, relax), scf_k4.out (4x4x4 single point at the relaxed
geometry), spin_k3.out (nspin 2, 3x3x3), projwfc_*.out and pdos/ (from the k4 SCF). VB top = band 351 (n_pure 352 - 1).
"""
import numpy as np

import qeio as q
import iwo_common as iw
from figstyle import plt, save, panel, CYCLE, EL

SITES = ['8b', '24d']


def main():
    res = {}
    for s in SITES:
        d = q.RES / f'iwo_W{s}'
        r = {}
        m, i = q.last(d / 'relax.out', r'Final energy\s+=\s+(-?[\d.]+) Ry')
        mb, ib = q.last(d / 'relax.out', r'bfgs converged in\s+(\d+) scf cycles and\s+(\d+) bfgs steps')
        r['E_relax_k3_Ry'] = q.V(float(m.group(1)), q.src(d / 'relax.out', i))
        r['bfgs'] = q.V(f'{mb.group(1)} scf, {mb.group(2)} bfgs', q.src(d / 'relax.out', ib))
        r['E_scf_k4_Ry'] = q.V(*q.etot(d / 'scf_k4.out'))
        r['E_spin_k3_Ry'] = q.V(*q.etot(d / 'spin_k3.out'))
        mm, im = q.last(d / 'spin_k3.out', r'total magnetization\s+=\s+(-?[\d.]+) Bohr')
        ma, ia = q.last(d / 'spin_k3.out', r'absolute magnetization\s+=\s+(-?[\d.]+) Bohr')
        r['M_total_muB'] = q.V(float(mm.group(1)), q.src(d / 'spin_k3.out', im))
        r['M_abs_muB'] = q.V(float(ma.group(1)), q.src(d / 'spin_k3.out', ia))
        r['E_spin_minus_nospin_meV'] = round((r['E_spin_k3_Ry']['value'] - r['E_relax_k3_Ry']['value']) * q.RY * 1000, 2)
        r['nks'] = {'k4': q.nks(d / 'scf_k4.out')[0], 'spin_k3': q.nks(d / 'spin_k3.out')[0]}
        r['symops_k4'] = q.V(*q.symops(d / 'scf_k4.out'))
        # geometry: relax final coordinates vs scf_k4 input
        cell_f, sym, frac, s_fin = q.final_struct_out(d / 'relax.out')
        cell, sym_in, frac_in, cart_in, s_in = q.read_struct_in(d / 'scf_k4.in')
        if cell_f is None:
            cell_f = cell
        dfr = frac - frac_in; dfr -= np.rint(dfr)
        r['scf_k4_geometry_equals_relax_final_A'] = round(float(np.abs(dfr @ cell).max()), 6)
        w = sym.index('W')
        r['W_O_A'] = q.V([round(x, 4) for x in q.neighbours(cell_f, frac, w, 'O', sym, 2.6)], s_fin)
        r['W_O_mean_A'] = round(float(np.mean(r['W_O_A']['value'])), 4)
        r['a_conv_A'] = round(float(np.linalg.norm(cell_f[0])), 5)
        fl = iw.filling(f'iwo_W{s}', 'scf_k4.out', vb=351)
        r['filling'] = iw.strip(fl)
        r['_fl'] = fl
        res[s] = r
    dE = {k: round((res['8b'][k]['value'] - res['24d'][k]['value']) * q.RY, 4) for k in ('E_relax_k3_Ry', 'E_scf_k4_Ry', 'E_spin_k3_Ry')}
    out = {s: {k: v for k, v in res[s].items() if not k.startswith('_')} for s in SITES}
    out['E8b_minus_E24d_eV'] = dE
    out['k3_to_k4_change_meV'] = round((dE['E_scf_k4_Ry'] - dE['E_relax_k3_Ry']) * 1000, 2)
    kT = q.KB * 600
    out['occupation_ratio_24d_to_8b_600K'] = round(3 * np.exp(dE['E_scf_k4_Ry'] / kT), 0)
    q.dump('f09_iwo_bulk', out)
    print(dE, out['k3_to_k4_change_meV'], out['occupation_ratio_24d_to_8b_600K'])
    for s in SITES:
        r = out[s]; fl = r['filling']
        print(s, 'W-O', r['W_O_A']['value'], r['W_O_mean_A'], 'a', r['a_conv_A'], 'geom diff', r['scf_k4_geometry_equals_relax_final_A'],
              'M', r['M_total_muB']['value'], r['M_abs_muB']['value'], 'dEspin', r['E_spin_minus_nospin_meV'], r['nks'], r['symops_k4']['value'])
        print('  EF', fl['E_F_eV']['value'], 'N', fl['N_from_MV'], fl['N_from_printed_occ'], fl['max_abs_MV_minus_printed_occ'], 'above VB', fl['electrons_above_VB_top'],
              'W5d e', fl['W5d_projected_electrons'], 'gap VB-CB(G)', fl['gap_VBtop_to_hostCB_Gamma_eV'], 'EF-CB', fl['EF_minus_hostCB_Gamma_eV'],
              'Wrich', fl['W_rich_band_Gamma'], fl['W_rich_minus_hostCB_Gamma_eV'], fl['W_rich_minus_EF_Gamma_eV'])
        for n, b in fl['bands'].items():
            print('   ', n, b)

    # ---- figure: (a, b) PDOS around E_F for 24d and 8b; (c) W 5d weight of each band at Gamma vs energy
    fig, ax = plt.subplots(1, 3, figsize=(6.8, 2.5), gridspec_kw={'width_ratios': [1, 1, 0.9]})
    for i, s in enumerate(['24d', '8b']):
        d = q.RES / f'iwo_W{s}'
        ef = out[s]['filling']['E_F_eV']['value']
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
        fl = out[s]['filling']
        a_.axvline(0, color='0.5', ls='--', lw=0.6)
        a_.axvline(fl['bands']['352']['E_Gamma_minus_EF_eV'], color=EL['In'], ls=':', lw=0.8)
        a_.set_xlim(-3, 3); a_.set_ylim(0, ytop)
        a_.set_xlabel(r'$E - E_F$ (eV)')
        if i == 0:
            a_.set_ylabel('PDOS (states eV$^{-1}$ cell$^{-1}$)')
            a_.legend(loc='upper left', fontsize=6.3)
        panel(a_, 'ab'[i], x=-0.2 if i == 0 else -0.12)
    for i, s in enumerate(['24d', '8b']):
        sc = np.array(out[s]['filling']['gamma_scatter'])
        ax[2].plot(sc[:, 0], sc[:, 1], ['o', 's'][i], mfc='none', color=CYCLE[i], ms=3.5, label=f'W on {s}')
    ax[2].axvline(0, color='0.5', ls='--', lw=0.6)
    ax[2].set_xlim(-3, 3); ax[2].set_ylim(-0.02, 0.8)
    ax[2].set_xlabel(r'$E_n(\Gamma) - E_F$ (eV)'); ax[2].set_ylabel(r'W 5d weight at $\Gamma$')
    ax[2].legend(loc='upper left', fontsize=6.5)
    panel(ax[2], 'c', x=-0.25)
    fig.tight_layout()
    save(fig, 'fig09_iwo_bulk_pdos')


if __name__ == '__main__':
    main()
