"""Fig. 1: stage-1 convergence of bulk In2O3 (40-atom primitive bixbyite, experimental a = 10.117 A, PAW-PBE).

Reads bulk_In2O3_protocol/scf_ecut{50,60,71,85}_k3.out and scf_ecut71_k{2,3,4}.out. For each run: '!' total energy,
pressure, HOMO/LUMO on the SCF grid, symmetry operations, irreducible k-points, In-O first shell of the input.
Criteria (PROTOCOL.md section 3, fixed before the runs): a further increase changes E by < 1 mRy/atom, P by < 1 kbar,
the KS gap by < 10 meV.
"""
import numpy as np

import qeio as q
from figstyle import plt, save, panel, CYCLE

RUNS = [('ecut', 50, 'scf_ecut50_k3.out'), ('ecut', 60, 'scf_ecut60_k3.out'), ('ecut', 71, 'scf_ecut71_k3.out'),
        ('ecut', 85, 'scf_ecut85_k3.out'), ('k', 2, 'scf_ecut71_k2.out'), ('k', 3, 'scf_ecut71_k3.out'), ('k', 4, 'scf_ecut71_k4.out')]


def main():
    rows = []
    for kind, x, f in RUNS:
        p = q.BULK / f
        E, sE = q.etot(p)
        P, sP = q.pressure(p)
        h, l, sg = q.homo_lumo(p)
        so, sso = q.symops(p)
        nk, snk = q.nks(p)
        nat = int(q.first(p, r'number of atoms/cell\s+=\s+(\d+)')[0].group(1))
        rows.append(dict(kind=kind, x=x, file=f, nat=nat, E_Ry=q.V(E, sE), P_kbar=q.V(P, sP), gap_eV=q.V(round(l - h, 4), sg),
                         symops=q.V(so, sso), nk=q.V(nk, snk), done=q.job_done(p)))
    # structure check of the input cell (experimental lattice, Marezio 1966 Wyckoff parameters)
    cell, sym, frac, cart, s_in = q.read_struct_in(q.BULK / 'scf_ecut71_k3.in')
    a_conv = float(np.linalg.norm(cell[0]) * 2 / np.sqrt(3))
    bonds = sorted({round(d, 3) for i, s in enumerate(sym) if s == 'In' for d in q.neighbours(cell, frac, i, 'O', sym, 2.4)})
    ref_e = next(r for r in rows if r['kind'] == 'ecut' and r['x'] == 85)
    ref_k = next(r for r in rows if r['kind'] == 'k' and r['x'] == 4)
    for r in rows:
        ref = ref_e if r['kind'] == 'ecut' else ref_k
        r['dE_mRy_per_atom'] = round((r['E_Ry']['value'] - ref['E_Ry']['value']) / r['nat'] * 1000, 3)
        r['dP_kbar'] = round(r['P_kbar']['value'] - ref['P_kbar']['value'], 2)
        r['dgap_meV'] = round((r['gap_eV']['value'] - ref['gap_eV']['value']) * 1000, 1)
        r['meets_criteria_vs_ref'] = abs(r['dE_mRy_per_atom']) < 1 and abs(r['dP_kbar']) < 1 and abs(r['dgap_meV']) < 10
    res = {'runs': rows, 'input_cell': {'a_conv_A': round(a_conv, 4), 'src': s_in, 'In_O_distinct_A': bonds},
           'decision': 'lowest ecut meeting all criteria vs 85 Ry; lowest k meeting criteria vs 4x4x4'}
    res['ecut_selected'] = min(r['x'] for r in rows if r['kind'] == 'ecut' and r['meets_criteria_vs_ref'] and r['x'] != 85)
    res['k_selected_lowest'] = min(r['x'] for r in rows if r['kind'] == 'k' and r['meets_criteria_vs_ref'] and r['x'] != 4)
    q.dump('f01_bulk_convergence', res)

    # ---- figure
    e = [r for r in rows if r['kind'] == 'ecut']
    k = [r for r in rows if r['kind'] == 'k']
    fig, ax = plt.subplots(1, 3, figsize=(6.6, 2.2))
    for a_, key, lab, thr in ((ax[0], 'dE_mRy_per_atom', r'$E - E_{\rm ref}$ (mRy atom$^{-1}$)', 1),
                              (ax[1], 'dP_kbar', r'$P - P_{\rm ref}$ (kbar)', 1),
                              (ax[2], 'dgap_meV', r'$E_g - E_{g,\rm ref}$ (meV)', 10)):
        a_.plot([r['x'] for r in e], [r[key] for r in e], 'o-', color=CYCLE[0], mfc='none', label='cutoff (k 3x3x3)')
        a_.axhspan(-thr, thr, color='0.88', lw=0)
        a_.axvline(71, color='0.5', ls=':', lw=0.8)
        a_.set_xlabel('ecutwfc (Ry)')
        a_.set_ylabel(lab)
        a2 = a_.twiny()
        a2.plot([r['x'] for r in k], [r[key] for r in k], 's--', color=CYCLE[1], mfc='none', label='k grid (71 Ry)')
        a2.set_xlim(1.5, 4.5); a2.set_xticks([2, 3, 4]); a2.set_xticklabels(['2', '3', '4'])
        a2.set_xlabel('k grid n (n x n x n)', fontsize=8)
        a2.minorticks_off()
    for i, a_ in enumerate(ax):
        panel(a_, 'abc'[i], y=1.18)
    h1, l1 = ax[0].get_legend_handles_labels()
    h2, l2 = ax[0].get_figure().axes[3].get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.12))
    fig.tight_layout()
    save(fig, 'fig01_bulk_convergence')
    for r in rows:
        print(r['file'], r['E_Ry']['value'], r['P_kbar']['value'], r['gap_eV']['value'], r['symops']['value'], r['nk']['value'],
              r['dE_mRy_per_atom'], r['dP_kbar'], r['dgap_meV'], r['meets_criteria_vs_ref'])
    print('input a', a_conv, 'In-O', bonds, 'selected', res['ecut_selected'], res['k_selected_lowest'])


if __name__ == '__main__':
    main()
