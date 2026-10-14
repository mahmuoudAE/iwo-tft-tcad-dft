"""Fig. 4: vacuum convergence of the unrelaxed 1 nm In2O3(001) slab (slab1_v15 / v25 / v35; same atoms, 15/25/35 A vacuum).

Per run: HOMO/LUMO of the SCF (3x3x1, includes Gamma), vacuum level from the planar average (two definitions:
(i) points > 5 A from every atom plane, (ii) points within 2 A of the cell boundary, as analyze_slabs.py),
EA = E_vac - CBM, IP = E_vac - VBM, flatness of the vacuum plateau, SCF iterations, total force.
Criterion 6 (PROTOCOL_CERN.md, as quoted in RESULTS_LOG): changes < 10 meV.
"""
import numpy as np

import qeio as q
from figstyle import plt, save, panel, CYCLE

JOBS = [(15, 'slab1_v15'), (25, 'slab1_v25'), (35, 'slab1_v35')]


def evac_boundary(d):
    z, vp, vm, f = q.avg_dat(d)
    c = z.max() + (z[1] - z[0])
    win = np.minimum(z, c - z) * q.BOHR < 2.0
    return float(vp[win].mean() * q.RY), float((vp[win].max() - vp[win].min()) * q.RY * 1000)


def main():
    rows = []
    for vac, job in JOBS:
        d = q.RES / job
        h, l, sg = q.homo_lumo(d / 'scf.out')
        vv = q.slab_vacuum(d)
        eb, sb = evac_boundary(d)
        it, sit = q.scf_iters(d / 'scf.out')
        fm, fi = q.last(d / 'scf.out', r'Total force =\s+([\d.]+)')
        cell, sym, frac, cart, s_in = q.read_struct_in(d / 'scf.in')
        zs = cart[:, 2]
        rows.append({'vacuum_nominal_A': vac, 'job': job, 'cell_c_A': round(float(cell[2, 2]), 3),
                     'slab_extent_A': round(float(zs.max() - zs.min()), 3),
                     'VBM_eV': q.V(h, sg), 'CBM_eV': q.V(l, sg), 'gap_eV': round(l - h, 4),
                     'E_vac_eV': q.V(round(vv['E_vac_eV'], 5), vv['src'], note='> 5 A from every atom plane'),
                     'E_vac_spread_meV': round(vv['spread_meV'], 4), 'E_vac_boundary_eV': round(eb, 5),
                     'vacuum_top_minus_bottom_meV': round((vv['above_top_eV'] - vv['below_bottom_eV']) * 1000, 3) if vv['below_bottom_eV'] else None,
                     'EA_eV': round(vv['E_vac_eV'] - l, 4), 'IP_eV': round(vv['E_vac_eV'] - h, 4),
                     'EA_boundary_eV': round(eb - l, 4), 'scf_iterations': q.V(it, sit),
                     'total_force_Ry_bohr': q.V(float(fm.group(1)), q.src(d / 'scf.out', fi)),
                     'symops': q.V(*q.symops(d / 'scf.out')), 'version': q.version(d / 'scf.out')[0]})
    ref = rows[1]
    for r in rows:
        r['dEA_vs_25_meV'] = round((r['EA_eV'] - ref['EA_eV']) * 1000, 2)
        r['dIP_vs_25_meV'] = round((r['IP_eV'] - ref['IP_eV']) * 1000, 2)
        r['dgap_vs_25_meV'] = round((r['gap_eV'] - ref['gap_eV']) * 1000, 2)
    q.dump('f04_slab_vacuum', {'runs': rows})
    for r in rows:
        print({k: (v['value'] if isinstance(v, dict) else v) for k, v in r.items()})

    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.5), gridspec_kw={'width_ratios': [1.7, 1]})
    for i, (vac, job) in enumerate(JOBS):
        z, vp, vm, f = q.avg_dat(q.RES / job)
        zA = z * q.BOHR
        cell, sym, frac, cart, s_in = q.read_struct_in(q.RES / job / 'scf.in')
        zc = 0.5 * (cart[:, 2].min() + cart[:, 2].max())
        ax[0].plot(zA - zc, vp * q.RY - rows[i]['E_vac_eV']['value'], color=CYCLE[i], lw=0.8, label=f'{vac} Å')
    ax[0].set_xlabel(r'$z - z_{\rm centre}$ (Å)'); ax[0].set_ylabel(r'$\bar V(z) - E_{\rm vac}$ (eV)')
    ax[0].legend(loc='lower right', fontsize=7, title='vacuum', title_fontsize=7)
    panel(ax[0], 'a', x=-0.13)
    x = [r['vacuum_nominal_A'] for r in rows]
    ax[1].plot(x, [r['dEA_vs_25_meV'] for r in rows], 'o-', mfc='none', color=CYCLE[0], label='EA')
    ax[1].plot(x, [r['dIP_vs_25_meV'] for r in rows], 's--', mfc='none', color=CYCLE[1], label='IP')
    ax[1].plot(x, [r['dgap_vs_25_meV'] for r in rows], '^:', mfc='none', color=CYCLE[2], label='gap')
    ax[1].set_ylim(-0.5, 0.5)
    ax[1].set_xlabel('vacuum (Å)'); ax[1].set_ylabel('change vs 25 Å (meV)')
    ax[1].legend(loc='upper right', fontsize=7)
    panel(ax[1], 'b', x=-0.30)
    fig.tight_layout()
    save(fig, 'fig04_slab_vacuum')


if __name__ == '__main__':
    main()
