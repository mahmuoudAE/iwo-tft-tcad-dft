"""Fig. 11: register H-L (crystalline oxygen vacancies, six PBE cells) and the A20(ii) smearing sensitivity, re-derived
from the raw lxplus grep archived in cern_htcondor/results/evidence_20261013_HL/r23.out (sha256 570ece79...).

Independent parser (does not import hl_a20ii.py). Per cell block of r23.out: the last '!' total energy of the
'-- relax.out' section (k3, Gaussian 0.005 Ry), of the '-- FINAL' section (k4, G 0.005) and of the '-- A20(ii)' section
(k3, G 0.002); '-TS'; convergence and k-point lines; 'Final energy' must equal the relax '!' energy.
Registered differences (HYPOTHESIS_REGISTER H-L, A17/A19/A20):
  dE_local = E(In31WO47 near O30) - E(In31WO47 far O32)                      prediction >= +0.3 eV
  dE_dop   = [E(far) - E(In31WO48)] - [E(In32O47) - E(In32O48)]              prediction >  +0.05 eV
A20: k3->k4 change > 10 meV = unresolved significance; a sensitivity shift > 50 meV or a flipped verdict = not robust.
Crystalline cells only: no amorphous quantity is read.
"""
import re

import numpy as np

import qeio as q
from figstyle import plt, save, panel, CYCLE

R23 = q.RES / 'evidence_20261013_HL' / 'r23.out'
CELLS = ['In32O48', 'In31WO48', 'In32O47', 'In31WO47_far', 'In31WO47_near', 'In31WO47_near72']
SETS = ['k3_g005', 'k4_g005', 'k3_g002']


def parse():
    L = q.lines(str(R23))
    heads = [i for i, l in enumerate(L) if l.startswith('######## ')]
    out = {}
    for j, h in enumerate(heads):
        name = L[h].split()[1]
        end = heads[j + 1] if j + 1 < len(heads) else len(L)
        sec = {}
        cur = None
        for i in range(h + 1, end):
            l = L[i]
            if l.startswith('-- relax.out'):
                cur = 'k3_g005'
            elif l.startswith('-- FINAL'):
                cur = 'k4_g005'
            elif l.startswith('-- A20(ii)'):
                cur = 'k3_g002'
            elif l.startswith('-- '):
                cur = None if not l.startswith('-- SEGMENT') else None
            if cur is None:
                continue
            s = sec.setdefault(cur, {})
            m = re.match(r'^!\s+total energy\s+=\s+(-?[\d.]+) Ry', l)
            if m:
                s['E'] = (float(m.group(1)), i + 1)
            m = re.search(r'smearing contrib\. \(-TS\)\s+=\s+(-?[\d.]+) Ry', l)
            if m:
                s['mTS'] = (float(m.group(1)), i + 1)
            m = re.search(r'Final energy\s+=\s+(-?[\d.]+) Ry', l)
            if m:
                s['Final'] = (float(m.group(1)), i + 1)
            m = re.search(r'number of k points=\s+(\d+)\s+Gaussian smearing, width \(Ry\)=\s+([\d.]+)', l)
            if m:
                s['nk'] = int(m.group(1)); s['width'] = float(m.group(2))
            m = re.search(r'convergence has been achieved in\s+(\d+)', l)
            if m:
                s['iters'] = int(m.group(1))
            m = re.search(r'number of electrons\s+=\s+([\d.]+)', l)
            if m:
                s['nel'] = float(m.group(1))
            if 'bfgs_conv=' in l:
                s['relax_flags'] = l.strip()
            if l.strip().startswith('conv=') or '] conv=' in l:
                s['flags'] = l.strip().split('] ')[-1]
        out[name] = sec
    return out


def main():
    P = parse()
    rel = q.rel(R23)
    E = {c: {s: P[c][s]['E'][0] for s in SETS} for c in CELLS}
    res = {'source': rel, 'cells': {}}
    for c in CELLS:
        rc = {}
        for s in SETS:
            d = P[c][s]
            rc[s] = {'E_Ry': q.V(d['E'][0], f"{rel}:{d['E'][1]}", 'COMPUTED'), 'minus_TS_Ry': d['mTS'][0], 'nk': d.get('nk'),
                     'width_Ry': d.get('width'), 'iters': d.get('iters'), 'flags': d.get('flags', d.get('relax_flags'))}
        assert abs(P[c]['k3_g005']['Final'][0] - E[c]['k3_g005']) < 1e-7, c
        rc['n_electrons'] = P[c]['k3_g005'].get('nel')
        rc['k3_to_k4_meV'] = round((E[c]['k4_g005'] - E[c]['k3_g005']) * q.RY * 1000, 2)
        rc['g002_minus_g005_k3_meV'] = round((E[c]['k3_g002'] - E[c]['k3_g005']) * q.RY * 1000, 2)
        # zero-width estimate for Gaussian smearing: E0 ~ (E + F)/2 = F + TS/2 = F - (-TS)/2  (diagnostic only)
        z = {s: E[c][s] - rc[s]['minus_TS_Ry'] / 2 for s in ('k3_g005', 'k3_g002')}
        rc['E0_estimate_shift_meV'] = round((z['k3_g002'] - z['k3_g005']) * q.RY * 1000, 2)
        res['cells'][c] = rc

    def dloc(s, near='In31WO47_near'):
        return (E[near][s] - E['In31WO47_far'][s]) * q.RY

    def ddop(s):
        return ((E['In31WO47_far'][s] - E['In31WO48'][s]) - (E['In32O47'][s] - E['In32O48'][s])) * q.RY
    diffs = {}
    for name, f, thr in (('dE_local_O30', dloc, 0.3), ('dE_local_O72_sensitivity', lambda s: dloc(s, 'In31WO47_near72'), None), ('dE_dop', ddop, 0.05)):
        v = {s: round(f(s), 4) for s in SETS}
        v['k3_to_k4_meV'] = round((f('k4_g005') - f('k3_g005')) * 1000, 1)
        v['A20ii_shift_meV'] = round((f('k3_g002') - f('k3_g005')) * 1000, 1)
        v['threshold_eV'] = thr
        if thr is not None:
            v['threshold_met_all_sets'] = all(v[s] >= thr if name.startswith('dE_local') else v[s] > thr for s in SETS)
            v['A20_k_rule'] = 'UNRESOLVED significance (|k3->k4| > 10 meV)' if abs(v['k3_to_k4_meV']) > 10 else 'k-converged within 10 meV'
            v['A20ii_rule'] = 'not robust' if abs(v['A20ii_shift_meV']) > 50 else 'width-robust at k3'
        diffs[name] = v
    res['differences_eV'] = diffs
    res['O72_minus_O30_eV'] = {s: round((E['In31WO47_near72'][s] - E['In31WO47_near'][s]) * q.RY, 4) for s in SETS}
    q.dump('f11_hl_vacancy', res)
    for c, rc in res['cells'].items():
        print(c, {s: (rc[s]['E_Ry']['value'], rc[s]['E_Ry']['src'].split(':')[-1], rc[s]['minus_TS_Ry'], rc[s]['nk'], rc[s]['width_Ry'], rc[s]['iters']) for s in SETS},
              'k3->k4', rc['k3_to_k4_meV'], 'g002', rc['g002_minus_g005_k3_meV'], 'E0', rc['E0_estimate_shift_meV'], 'nel', rc['n_electrons'])
    for k, v in diffs.items():
        print(k, v)
    print('O72-O30', res['O72_minus_O30_eV'])

    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.6), gridspec_kw={'width_ratios': [1.1, 1]})
    names = ['dE_local_O30', 'dE_local_O72_sensitivity', 'dE_dop']
    xl = [r'$\Delta E_{\rm local}$ (O30)', r'$\Delta E_{\rm local}$ (O72)', r'$\Delta E_{\rm dop}$']
    mk = {'k3_g005': ('o', CYCLE[0], 'k 3x3x3, G 0.005 Ry'), 'k4_g005': ('s', CYCLE[1], 'k 4x4x4, G 0.005 Ry'), 'k3_g002': ('^', CYCLE[2], 'k 3x3x3, G 0.002 Ry')}
    for j, s in enumerate(SETS):
        m_, c_, lab = mk[s]
        ax[0].plot(np.arange(3) + (j - 1) * 0.18, [diffs[n][s] for n in names], m_, mfc='none', color=c_, label=lab)
    ax[0].hlines(0.3, -0.4, 1.4, color='0.4', ls='--', lw=0.8)
    ax[0].hlines(0.05, 1.6, 2.4, color='0.4', ls='--', lw=0.8)
    ax[0].set_xticks(range(3)); ax[0].set_xticklabels(xl, fontsize=7.5); ax[0].minorticks_off()
    ax[0].tick_params(axis='y', which='minor', left=True); ax[0].yaxis.set_minor_locator(plt.matplotlib.ticker.AutoMinorLocator())
    ax[0].set_ylabel('energy difference (eV)'); ax[0].set_ylim(0, 1.05); ax[0].set_xlim(-0.5, 2.5)
    ax[0].legend(loc='upper left', fontsize=6.5, ncol=1)
    panel(ax[0], 'a', x=-0.17)
    x = np.arange(len(CELLS))
    ax[1].bar(x - 0.2, [res['cells'][c]['k3_to_k4_meV'] for c in CELLS], 0.38, color='white', edgecolor=CYCLE[1], label='k4 - k3')
    ax[1].bar(x + 0.2, [res['cells'][c]['g002_minus_g005_k3_meV'] for c in CELLS], 0.38, color='white', edgecolor=CYCLE[2], hatch='///', label='G 0.002 - G 0.005 (k3)')
    ax[1].axhline(0, color='k', lw=0.6)
    ax[1].set_xticks(x); ax[1].set_xticklabels(['In32O48', 'In31WO48', 'In32O47', 'far', 'near', 'near72'], rotation=40, ha='right', fontsize=7)
    ax[1].minorticks_off(); ax[1].tick_params(axis='y', which='minor', left=True)
    ax[1].set_ylabel('per-cell energy change (meV)')
    ax[1].legend(loc='lower left', fontsize=6.5)
    panel(ax[1], 'b', x=-0.36)
    fig.tight_layout(w_pad=2.0)
    save(fig, 'fig11_hl_vacancy')


if __name__ == '__main__':
    main()
