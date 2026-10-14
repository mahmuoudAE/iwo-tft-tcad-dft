"""Fig. 8: PDOS of the relaxed 2 nm In2O3 slab and the surface-state check of the band edges (all slabs with projwfc).

Band-edge character from projwfc (Lowdin projections printed per band and k): weight of each atom = sum of its printed
components; shares are normalised by the sum of all printed components of that band (|psi|^2 printout truncates
components < 0.001). k average: SCF k weights (scf.out); the plain mean over k (the earlier read-out) is also given.
Surface OH group = H atoms + O atoms within 1.15 A of an H. z profile: 8 equal slices between the lowest and highest atom.
Pure slabs: VB top = n_el/2, CB bottom = n_el/2 + 1. W slabs: VB top = n_pure - 1 (In 4d / W 5s5p PAW band count).
PDOS: sum of the ldos columns of projwfc's pdos files per element and l (states/eV/cell, spin-summed).
"""
import json

import numpy as np

import qeio as q
from figstyle import plt, save, panel, CYCLE, EL

CASES = [('0.51', 'slabL1_relax_v2', None), ('0.75', 'slabL2_relax_v2', None), ('2.0', 'slab2r_pdos_cpu', None),
         ('1.0 W (proxy)', 'iwo_slab1_final_cpu', 311), ('2.0 W', 'iwo_slab2_final_cpu', 663)]


def edge_char(job, vb_band=None):
    d = q.RES / job
    cell, sym, frac, cart, s_in = q.read_struct_in(d / 'scf.in')
    nat = len(sym)
    H = [i for i, s in enumerate(sym) if s == 'H']
    ohO = {i for i, s in enumerate(sym) if s == 'O' and q.neighbours(cell, frac, i, 'H', sym, 1.15)}
    surf = set(H) | ohO
    ne, sne = q.nelec(d / 'scf.out')
    vb = vb_band or int(round(ne)) // 2
    wk = q.kweights(d / 'scf.out')
    pf = next(d.glob('projwfc_*.out'))
    states, kb = q.projwfc(pf)
    assert len(kb) == len(wk), (len(kb), len(wk))
    z = cart[:, 2]
    edges = np.linspace(z.min() - 1e-3, z.max() + 1e-3, 9)
    out = {'n_atoms': nat, 'surface_OH_atoms': len(surf), 'surface_OH_number_share': round(len(surf) / nat, 4), 'VB_top_band': vb,
           'k_weights': wk.round(5).tolist(), 'projwfc': q.rel(pf)}
    for name, band in (('VB_top', vb), ('CB_bottom', vb + 1), ('VB_top_minus_20', vb - 20)):
        rec = {}
        for mode, ww in (('kweighted', wk / wk.sum()), ('kmean', np.ones(len(wk)) / len(wk))):
            wa = np.zeros(nat)
            for kk, w in zip(kb, ww):
                comp = kk[band][1]
                tot = sum(comp.values())
                for s_, c in comp.items():
                    wa[states[s_][0]] += w * c / tot
            rec[mode] = {'OH_share': round(float(sum(wa[i] for i in surf)), 4),
                         'by_element': {e: round(float(sum(wa[i] for i in range(nat) if sym[i] == e)), 4) for e in sorted(set(sym))},
                         'z_profile_8': [round(float(wa[(z >= lo) & (z < hi)].sum()), 3) for lo, hi in zip(edges[:-1], edges[1:])]}
        rec['E_Gamma_eV'] = kb[0][band][0]
        rec['src'] = f'{q.rel(pf)}:{kb[0][band][3]}'
        rec['psi2_printed_Gamma'] = kb[0][band][2]
        out[name] = rec
    return out


def main():
    res = {}
    for lab, job, vb in CASES:
        res[lab] = {'job': job, **edge_char(job, vb)}
        r = res[lab]
        print(lab, job, 'OH atoms', r['surface_OH_number_share'], 'VB', r['VB_top_band'])
        for n in ('VB_top', 'CB_bottom', 'VB_top_minus_20'):
            print('   ', n, r[n]['kweighted'], '| kmean OH', r[n]['kmean']['OH_share'])
    # PDOS of the 2 nm slab
    d = q.RES / 'slab2r_pdos_cpu'
    h, l, sg = q.homo_lumo(d / 'scf.out')
    pd = {}
    for name, sel in (('In s', lambda a, e, w, L: e == 'In' and L == 's'), ('In p', lambda a, e, w, L: e == 'In' and L == 'p'),
                      ('In d', lambda a, e, w, L: e == 'In' and L == 'd'), ('O s', lambda a, e, w, L: e == 'O' and L == 's'),
                      ('O p', lambda a, e, w, L: e == 'O' and L == 'p'), ('H s', lambda a, e, w, L: e == 'H')):
        E, y, files = q.pdos_sum(d, sel)
        pd[name] = y
    tot = np.loadtxt(d / 'pdos' / 'slab2r_pdos_cpu.pdos_tot')
    res['pdos_2nm'] = {'VBM_eV': q.V(h, sg), 'CBM_eV': q.V(l, sg), 'pdos_dir': q.rel(d / 'pdos'),
                       'integral_tot_window_states': round(float(np.trapezoid(tot[:, 1], tot[:, 0])), 2)}
    q.dump('f08_slab_pdos_surface', res)

    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.6), gridspec_kw={'width_ratios': [1.5, 1]})
    Er = E - h
    ax[0].plot(Er, tot[:, 1], color='k', lw=0.8, label='total')
    for name, c, ls in (('In s', EL['In'], '-'), ('In d', EL['In'], ':'), ('O p', EL['O'], '-'), ('H s', EL['H'], '-')):
        ax[0].plot(Er, pd[name], color=c, ls=ls, lw=0.9, label=name)
    ax[0].axvline(0, color='0.5', lw=0.6, ls='--'); ax[0].axvline(l - h, color='0.5', lw=0.6, ls='--')
    ax[0].set_xlim(-6, 4); ax[0].set_ylim(0, None)
    ax[0].set_xlabel(r'$E - E_{\rm VBM}$ (eV)'); ax[0].set_ylabel('PDOS (states eV$^{-1}$ cell$^{-1}$)')
    ax[0].legend(loc='upper left', fontsize=6.5, ncol=2)
    panel(ax[0], 'a', x=-0.14)
    r = res['2.0']
    xs = np.arange(1, 9)
    ax[1].plot(xs, r['VB_top']['kweighted']['z_profile_8'], 'o-', mfc='none', color=CYCLE[1], label=f"VB top (band {r['VB_top_band']})")
    ax[1].plot(xs, r['CB_bottom']['kweighted']['z_profile_8'], 's-', mfc='none', color=CYCLE[0], label=f"CB bottom (band {r['VB_top_band'] + 1})")
    ax[1].plot(xs, r['VB_top_minus_20']['kweighted']['z_profile_8'], '^:', mfc='none', color='0.4', label='VB top - 20')
    ax[1].set_xticks(xs); ax[1].minorticks_off(); ax[1].tick_params(axis='y', which='minor', left=True)
    ax[1].set_xlabel('slice (bottom to top)'); ax[1].set_ylabel('projected weight')
    ax[1].set_ylim(0, 0.3)
    ax[1].legend(loc='upper left', fontsize=6.5)
    panel(ax[1], 'b', x=-0.30)
    fig.tight_layout()
    save(fig, 'fig08_slab2_pdos_surface')


if __name__ == '__main__':
    main()
