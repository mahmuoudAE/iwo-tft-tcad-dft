"""Fig. 14: amorphous-cell FORCE checks already logged as read (C034 A27-C4 smearing screen, C035 A25 split labels,
C037 MACE-MPA-0 validation frames), re-derived independently.

Sight rule (HYPOTHESIS_REGISTER: blind to every amorphous-DFT electronic target quantity - edges, projections,
localisation, EA, gaps). The pw.x outputs were NOT copied: on lxplus an allowlist kept only '!' energies, -TS,
'Total force' lines, the first force block, convergence lines and k/electron/atom counts (raw_cern/amorph_forces_allowlist,
every line machine-checked against the whitelist). Inputs (scf.in) and MACE forces (mace_ref.json) are copied whole.
Definitions follow the frozen comparators: C034/C035 dF in Ry/bohr per Cartesian component; C037 (compare_val.py D1-D5)
dF = F_DFT - F_MACE in eV/A (1 Ry/bohr = 25.711033738162943 eV/A), RMSE_all, MAE_all over all components, RMSE_W1 over the
components of W and every O within 2.60 A (minimum image) of a W.
"""
import json
import re

import numpy as np

import qeio as q
from figstyle import plt, save, panel, CYCLE

A = q.HERE / 'raw_cern' / 'amorph_forces_allowlist'
RYB = 13.605693122994 / 0.529177210903
FRAMES = [('aIWO_bulk_s1_melt_3000K', 'REPORTED'), ('aIWO_bulk_s1_quenched_300K', 'SCORED'), ('aIWO_bulk_s1_final', 'SCORED'),
          ('aIO_bulk_s1_quenched_300K', 'SCORED'), ('aIO_bulk_s1_final', 'SCORED'), ('aIWO_0p7_s1_final', 'SCORED')]


def allow(p):
    L = q.lines(str(p))
    out = {'F': [], 'E': None, 'mTS': None, 'nat': None, 'tf': None, 'scfcorr': None, 'iters': None, 'done': False}
    for l in L:
        n, _, s = l.partition(': ')
        if 'force =' in s and 'atom' in s:
            out['F'].append(q.nums(s.split('force =')[1])[:3])
        elif s.startswith('!'):
            out['E'] = (float(q.nums(s)[0]), int(n))
        elif 'smearing contrib' in s:
            out['mTS'] = float(q.nums(s)[0])
        elif 'number of atoms/cell' in s:
            out['nat'] = int(s.split('=')[1])
        elif 'Total force' in s:
            v = q.nums(s); out['tf'], out['scfcorr'] = v[0], v[1]
        elif 'convergence has been achieved' in s:
            out['iters'] = int(re.search(r'in\s+(\d+)', s).group(1))
        elif 'JOB DONE' in s:
            out['done'] = True
    out['F'] = np.array(out['F'])
    assert len(out['F']) == out['nat'], (p, len(out['F']), out['nat'])
    return out


def read_in_ang(p):
    L = q.lines(str(p))
    ic = next(i for i, l in enumerate(L) if l.startswith('CELL_PARAMETERS'))
    assert 'angstrom' in L[ic]
    cell = np.array([q.nums(L[ic + j])[:3] for j in (1, 2, 3)])
    ia = next(i for i, l in enumerate(L) if l.startswith('ATOMIC_POSITIONS'))
    assert 'angstrom' in L[ia]
    lab, pos = [], []
    for l in L[ia + 1:]:
        t = l.split()
        if len(t) < 4 or not re.match(r'^[A-Z][a-z]?\d*$', t[0]):
            break
        lab.append(t[0]); pos.append([float(x) for x in t[1:4]])
    return cell, lab, np.array(pos)


def species(lab):
    return [re.sub(r'\d+$', '', x) for x in lab]


def c034():
    mv, ga = allow(A / 'C034' / 'mv' / 'scf.allow.txt'), allow(A / 'C034' / 'gauss' / 'scf.allow.txt')
    cell, lab, pos = read_in_ang(A / 'C034' / 'mv' / 'scf.in')
    sp = species(lab)
    dF = ga['F'] - mv['F']
    k = np.unravel_index(np.abs(dF).argmax(), dF.shape)
    return {'max_abs_dF_Ry_bohr': float(np.abs(dF).max()), 'at': f'{sp[k[0]]}{k[0] + 1} {"xyz"[k[1]]}',
            'rms_dF_Ry_bohr': float(np.sqrt((dF ** 2).mean())), 'max_atom_norm_dF': float(np.linalg.norm(dF, axis=1).max()),
            'n_components': int(dF.size), 'by_species_max': {e: float(np.abs(dF[[s == e for s in sp]]).max()) for e in sorted(set(sp))},
            'max_residual_component_MV_Gauss': [float(np.abs(mv['F']).max()), float(np.abs(ga['F']).max())],
            'E_MV_Ry': mv['E'][0], 'E_MV_minus_relax_Ry': round(mv['E'][0] - (-24232.38894468), 9),
            'iters_MV_Gauss': [mv['iters'], ga['iters']], 'total_scf_correction_MV_Gauss': [mv['scfcorr'], ga['scfcorr']],
            'verdict_A15': 'max|dF| <= 1e-3 Ry/bohr: not a geometry uncertainty' if np.abs(dF).max() <= 1e-3 else 'geometry uncertainty'}


def c035():
    un, sp_ = allow(A / 'C035' / 'unsplit' / 'scf.allow.txt'), allow(A / 'C035' / 'split' / 'scf.allow.txt')
    cu, lu, pu = read_in_ang(A / 'C035' / 'unsplit' / 'scf.in')
    cs, ls, ps = read_in_ang(A / 'C035' / 'split' / 'scf.in')
    assert species(lu) == species(ls) and np.abs(pu - ps).max() < 1e-9 and np.abs(cu - cs).max() < 1e-9
    sp = species(lu)
    dF = sp_['F'] - un['F']
    k = np.unravel_index(np.abs(dF).argmax(), dF.shape)
    return {'E_unsplit_Ry': un['E'][0], 'E_split_Ry': sp_['E'][0], 'abs_dE_Ry': abs(sp_['E'][0] - un['E'][0]),
            'max_abs_dF_Ry_bohr': float(np.abs(dF).max()), 'at': f'atom {k[0] + 1} {"xyz"[k[1]]}', 'n_components': int(dF.size),
            'by_species_max': {e: float(np.abs(dF[[s == e for s in sp]]).max()) for e in sorted(set(sp))},
            'iters_unsplit_split': [un['iters'], sp_['iters']], 'total_scf_correction_printed': [un['scfcorr'], sp_['scfcorr']],
            'geometry_identical': True, 'labels_split': sorted(set(ls)),
            'verdict_A25': 'PASS' if abs(sp_['E'][0] - un['E'][0]) <= 1e-5 and np.abs(dF).max() <= 1e-5 else 'FAIL'}


def c037():
    out = {}
    for fr, status in FRAMES:
        d = A / 'C037' / fr
        dft = allow(d / 'scf.allow.txt')
        mace = json.loads((d / 'mace_ref.json').read_text())
        Fm = np.array(mace['forces_eV_A'])
        Fd = dft['F'] * RYB
        assert Fd.shape == Fm.shape
        cell, lab, pos = read_in_ang(d / 'scf.in')
        sp = species(lab)
        dF = Fd - Fm
        rec = {'status': status, 'nat': dft['nat'], 'RMSE_all': float(np.sqrt((dF ** 2).mean())), 'MAE_all': float(np.abs(dF).mean())}
        W = [i for i, s in enumerate(sp) if s == 'W']
        if W:
            inv = np.linalg.inv(cell)
            S = set(W)
            for i, s in enumerate(sp):
                if s != 'O':
                    continue
                for w in W:
                    f = (pos[i] - pos[w]) @ inv; f -= np.rint(f)
                    if np.linalg.norm(f @ cell) <= 2.60:
                        S.add(i)
            S = sorted(S)
            rec['RMSE_W1'] = float(np.sqrt((dF[S] ** 2).mean())); rec['W1_atoms'] = len(S)
            rest = [i for i in range(len(sp)) if i not in S]
            rec['RMSE_outside_W1'] = float(np.sqrt((dF[rest] ** 2).mean()))
            rec['W1_share_of_squared_error'] = float((dF[S] ** 2).sum() / (dF ** 2).sum())
            rec['W_atom_force_norm_DFT_MACE_eV_A'] = [round(float(np.linalg.norm(Fd[W[0]])), 4), round(float(np.linalg.norm(Fm[W[0]])), 4)]
        else:
            rec['RMSE_W1'] = None
        rec['corr_DFT_MACE'] = float(np.corrcoef(Fd.ravel(), Fm.ravel())[0, 1])
        rec['DFT_force_rms_eV_A'] = float(np.sqrt((Fd ** 2).mean())); rec['MACE_force_rms_eV_A'] = float(np.sqrt((Fm ** 2).mean()))
        if status == 'SCORED':
            ok = rec['RMSE_all'] <= 0.15 and rec['MAE_all'] <= 0.10 and (rec['RMSE_W1'] is None or rec['RMSE_W1'] <= 0.25)
            rec['verdict'] = 'PASS' if ok else 'FAIL'
        rec['_dF'] = dF; rec['_Fd'] = Fd; rec['_Fm'] = Fm
        out[fr] = rec
    return out


def main():
    a, b, c = c034(), c035(), c037()
    res = {'source': q.rel(A), 'C034': a, 'C035': b, 'C037': {k: {kk: vv for kk, vv in v.items() if not kk.startswith('_')} for k, v in c.items()}}
    q.dump('f14_amorph_force_checks', res)
    print('C034', a); print('C035', b)
    for k, v in res['C037'].items():
        print(k, v)

    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.7), gridspec_kw={'width_ratios': [1, 1.2]})
    for j, (fr, st) in enumerate(FRAMES):
        r = c[fr]
        if fr in ('aIWO_bulk_s1_quenched_300K', 'aIO_bulk_s1_quenched_300K', 'aIWO_0p7_s1_final'):
            ax[0].plot(r['_Fm'].ravel(), r['_Fd'].ravel(), '.', ms=1.5, color=CYCLE[j % 10], label=fr.replace('_s1', '').replace('_300K', ''))
    lim = 2.2
    ax[0].plot([-lim, lim], [-lim, lim], color='0.5', lw=0.6)
    ax[0].set_xlim(-lim, lim); ax[0].set_ylim(-lim, lim)
    ax[0].set_xlabel(r'$F_{\rm MACE}$ (eV Å$^{-1}$)'); ax[0].set_ylabel(r'$F_{\rm DFT}$ (eV Å$^{-1}$)')
    ax[0].legend(loc='upper left', fontsize=6, markerscale=4)
    panel(ax[0], 'a', x=-0.22)
    x = np.arange(len(FRAMES))
    ax[1].bar(x - 0.27, [c[f]['RMSE_all'] for f, _ in FRAMES], 0.26, color='white', edgecolor=CYCLE[0], label='RMSE all')
    ax[1].bar(x, [c[f]['MAE_all'] for f, _ in FRAMES], 0.26, color='white', edgecolor=CYCLE[1], hatch='///', label='MAE all')
    ax[1].bar(x + 0.27, [c[f]['RMSE_W1'] or 0 for f, _ in FRAMES], 0.26, color='white', edgecolor=CYCLE[2], hatch='xx', label='RMSE W shell')
    for yv, cc in ((0.15, CYCLE[0]), (0.10, CYCLE[1]), (0.25, CYCLE[2])):
        ax[1].axhline(yv, color=cc, ls='--', lw=0.7)
    ax[1].set_xticks(x); ax[1].set_xticklabels(['aIWO melt', 'aIWO quench', 'aIWO final', 'aIO quench', 'aIO final', 'aIWO 0.7 final'], rotation=35, ha='right', fontsize=7)
    ax[1].minorticks_off(); ax[1].tick_params(axis='y', which='minor', left=True)
    ax[1].set_ylabel(r'force error (eV Å$^{-1}$)')
    ax[1].legend(loc='upper right', fontsize=6.5)
    panel(ax[1], 'b', x=-0.17)
    fig.tight_layout()
    save(fig, 'fig14_amorph_force_checks')


if __name__ == '__main__':
    main()
