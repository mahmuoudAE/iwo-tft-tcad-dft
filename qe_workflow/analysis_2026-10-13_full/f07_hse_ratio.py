"""Fig. 7: HSE06 check of the PBE confinement shift at 1 nm (SG15 norm-conserving, 80 Ry, PAW-PBE geometries).

Reads cern_htcondor/results/nc_*/scf.out: last HOMO/LUMO line (SCF k grid incl. Gamma: bulk 3x3x3, slab 3x3x1), EXX settings
from scf.in, completion. r = dEg(HSE)/dEg(PBE) with dEg = slab gap - bulk gap (same NC set).
Pairs: r_q1 = (HSE slab, ecutfock 160) - (HSE bulk, q 1x1x1, default ecutfock); r_q3 = same slab against bulk with EXX
q 3x3x3 (ecutfock 160) = worst case if the slab gap did not move with q (slab has q = 1 only).
"""
import re

import numpy as np

import qeio as q
from figstyle import plt, save, panel, CYCLE

JOBS = ['nc_pbe_bulk_e80', 'nc_pbe_bulk_e100', 'nc_pbe_slab1_e80', 'nc_hse_bulk_e80', 'nc_hse_bulk_f160_e80',
        'nc_hse_bulk_q3_e80', 'nc_hse_bulk_q3_f160_e80', 'nc_hse_slab1_e80', 'nc_hse_slab1_f160_e80']


def main():
    res = {}
    for j in JOBS:
        d = q.RES / j
        inp = (d / 'scf.in').read_text()
        dft = re.search(r"input_dft\s*=\s*'(\w+)'", inp)
        nq = re.search(r'nqx1\s*=\s*(\d+)', inp)
        ef = re.search(r'ecutfock\s*=\s*([\d.]+)', inp)
        r = {'functional': dft.group(1) if dft else 'pbe', 'nq': int(nq.group(1)) if nq else None,
             'ecutfock': float(ef.group(1)) if ef else None, 'done': q.job_done(d / 'scf.out')}
        exx_ok = any('EXX self-consistency reached' in l for l in q.lines(str(d / 'scf.out')))
        r['exx_converged'] = exx_ok if r['functional'] == 'hse' else None
        try:
            h, l, s = q.homo_lumo(d / 'scf.out')
            r.update({'VBM_eV': h, 'CBM_eV': l, 'gap_eV': q.V(round(l - h, 4), s)})
        except LookupError:
            r['gap_eV'] = None
        # an unfinished HSE run prints only the PBE pre-step: flag it so it is never used as HSE
        r['usable'] = r['done'] and (r['functional'] != 'hse' or exx_ok)
        res[j] = r
    g = {j: res[j]['gap_eV']['value'] for j in res if res[j]['usable']}
    dpbe = g['nc_pbe_slab1_e80'] - g['nc_pbe_bulk_e80']
    dh1 = g['nc_hse_slab1_f160_e80'] - g['nc_hse_bulk_e80']
    dh3 = g['nc_hse_slab1_f160_e80'] - g['nc_hse_bulk_q3_f160_e80']
    out = {'runs': res, 'dEg_PBE_NC_eV': round(dpbe, 4), 'dEg_HSE_q1_eV': round(dh1, 4), 'dEg_HSE_q3bulk_eV': round(dh3, 4),
           'r_q1': round(dh1 / dpbe, 4), 'r_q3_worst': round(dh3 / dpbe, 4),
           'ecutfock_bulk_160_vs_default_meV': round((g['nc_hse_bulk_f160_e80'] - g['nc_hse_bulk_e80']) * 1000, 2),
           'q3_minus_q1_bulk_gap_meV': round((g['nc_hse_bulk_q3_f160_e80'] - g['nc_hse_bulk_f160_e80']) * 1000, 1),
           'pbe_cutoff_80_vs_100_bulk_gap_meV': round((g['nc_pbe_bulk_e100'] - g['nc_pbe_bulk_e80']) * 1000, 2)}
    q.dump('f07_hse_ratio', out)
    for j, r in res.items():
        print(j, r['functional'], r['nq'], r['ecutfock'], r['done'], r['exx_converged'], r['usable'], r['gap_eV'] and r['gap_eV']['value'])
    print({k: v for k, v in out.items() if k != 'runs'})

    fig, ax = plt.subplots(figsize=(3.3, 2.5))
    x = np.arange(2)
    ax.bar(x - 0.18, [g['nc_pbe_bulk_e80'], g['nc_pbe_slab1_e80']], 0.34, color='white', edgecolor=CYCLE[0], hatch='///', label='PBE (NC)')
    ax.bar(x + 0.18, [g['nc_hse_bulk_e80'], g['nc_hse_slab1_f160_e80']], 0.34, color='white', edgecolor=CYCLE[1], label='HSE06 (NC)')
    ax.plot([1 + 0.18], [g['nc_hse_bulk_q3_f160_e80'] + dh1], '_', color='k', ms=12)
    ax.errorbar([0 + 0.18], [g['nc_hse_bulk_e80']], yerr=[[g['nc_hse_bulk_e80'] - g['nc_hse_bulk_q3_f160_e80']], [0]], fmt='none', ecolor='k', capsize=3, lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(['bulk', '1 nm slab']); ax.minorticks_off()
    ax.tick_params(axis='y', which='minor', left=True); ax.yaxis.set_minor_locator(plt.matplotlib.ticker.AutoMinorLocator())
    ax.set_ylabel('KS gap on the SCF grid (eV)'); ax.set_ylim(0, 3.5)
    ax.legend(loc='upper left', fontsize=7)
    save(fig, 'fig07_hse_check')


if __name__ == '__main__':
    main()
