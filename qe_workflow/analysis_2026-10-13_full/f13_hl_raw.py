"""Fig. 13: register H-L re-derived from the RAW CERN outputs (copied 2026-10-14 into raw_cern/hl/, sha256-verified
against lxplus; SHA256_REMOTE.txt), replacing the grep evidence r23.out used in f11.

Per cell (crystalline bixbyite, PBE PAW 71/568 Ry, Gaussian smearing, spin-unpolarised, neutral, QE 7.3.1 GPU):
  relax.out (k 3x3x3, G 0.005)   last '!' energy = 'Final energy', BFGS count, SCF failures, largest force component and
                                  total force of the converged step, -TS; final geometry (fixed cell: relax.in cell)
  scf.out   (k 4x4x4, G 0.005)   FINAL '!' energy, -TS, E_F, iterations; geometry = relax final geometry?
  a20/scf.out (k 3x3x3, G 0.002) A20(ii) '!' energy, -TS; input differs from the FINAL input only in degauss / K_POINTS?
Registered differences as in f11. New (crystalline, non-blind): vacancy relaxation (displacements), W-O bonds, and the
FINAL band filling above the VB top (VB top = 160 (In 4d) or 159 (31 In 4d + W 5s5p) + 4 per O; Gaussian occupations
printed by pw.x), first band above the VB top: energy, width, electrons. Band character is NOT projected (no projwfc).
"""
import json
import re

import numpy as np

import qeio as q
from figstyle import plt, save, panel, CYCLE

H = q.HERE / 'raw_cern' / 'hl'
CELLS = ['In32O48', 'In31WO48', 'In32O47', 'In31WO47_far', 'In31WO47_near', 'In31WO47_near72']
SETS = ['k3_g005', 'k4_g005', 'k3_g002']
PARENT = {'In32O47': ('In32O48', 'O17'), 'In31WO47_far': ('In31WO48', 'O32'), 'In31WO47_near': ('In31WO48', 'O30'),
          'In31WO47_near72': ('In31WO48', 'O72')}


def last_forces(p, before_line=None):
    L = q.lines(str(p))
    hdr = [i for i, l in enumerate(L) if 'Forces acting on atoms' in l and (before_line is None or i < before_line)]
    i0 = hdr[-1]
    F = []
    for l in L[i0 + 1:]:
        if 'force =' in l and 'atom' in l:
            F.append(q.nums(l.split('force =')[1])[:3])
        elif F and l.strip():
            break      # the next non-blank, non-atom line ends the total-force block (decomposition blocks follow)
    tf = [(float(m.group(1)), i) for m, i in q.grep(p, r'Total force =\s+([\d.]+)') if i > i0][0]
    return np.abs(np.array(F)), i0 + 1, tf


def vb_count(sym):
    n_in, n_w, n_o = sym.count('In'), sym.count('W'), sym.count('O')
    return 5 * n_in + 4 * n_w + 4 * n_o


def main():
    res = {'source': q.rel(H), 'cells': {}}
    geo = {}
    for c in CELLS:
        r = {}
        rp, sp, ap = H / 'vac' / c / 'relax.out', H / 'vac' / c / 'scf.out', H / 'a20' / c / 'scf.out'
        E = {}
        E['k3_g005'] = q.etot(rp)
        fe, ife = q.last(rp, r'Final energy\s+=\s+(-?[\d.]+) Ry')
        assert abs(float(fe.group(1)) - E['k3_g005'][0]) < 1e-7, c
        E['k4_g005'] = q.etot(sp)
        E['k3_g002'] = q.etot(ap)
        mb, ib = q.last(rp, r'bfgs converged in\s+(\d+) scf cycles and\s+(\d+) bfgs steps')
        Fc, fl, tf = last_forces(rp, ib)
        r['E_Ry'] = {k: q.V(*E[k]) for k in SETS}
        r['minus_TS_Ry'] = {k: float(q.last(p, r'smearing contrib\. \(-TS\)\s+=\s+(-?[\d.]+) Ry')[0].group(1)) for k, p in zip(SETS, (rp, sp, ap))}
        r['nk'] = {k: q.nks(p)[0] for k, p in zip(SETS, (rp, sp, ap))}
        r['width_Ry'] = {k: float(q.first(p, r'width \(Ry\)=\s+([\d.]+)')[0].group(1)) for k, p in zip(SETS, (rp, sp, ap))}
        r['iters_final_a20'] = [q.scf_iters(sp)[0], q.scf_iters(ap)[0]]
        r['bfgs'] = q.V(f'{mb.group(1)} scf, {mb.group(2)} bfgs', q.src(rp, ib))
        r['n_scf_relax'] = len(q.grep(rp, r'^!\s+total energy'))
        r['scf_not_converged_relax'] = len(q.grep(rp, r'convergence NOT achieved'))
        r['max_force_component_Ry_bohr'] = q.V(round(float(Fc.max()), 6), q.src(rp, fl))
        r['total_force_Ry_bohr'] = q.V(tf[0], q.src(rp, tf[1]))
        r['n_electrons'] = q.nelec(sp)[0]
        r['E_F_k4_eV'] = q.V(*q.fermi(sp))
        r['versions'] = [q.version(p)[0] for p in (rp, sp, ap)]
        # geometry
        cell, sym0, frac0, cart0, s0 = q.read_struct_in(H / 'vac' / c / 'relax.in')
        cf, symf, fracf, sf = q.final_struct_out(rp)
        cellS, symS, fracS, cartS, sS = q.read_struct_in(sp.with_suffix('.in'))
        cellA, symA, fracA, cartA, sA = q.read_struct_in(H / 'checks' / 'gpumax_work' / 'a20_g002' / c / 'scf.in')
        d = fracf - frac0; d -= np.rint(d); disp = np.linalg.norm(d @ cell, axis=1)
        dS = fracS - fracf; dS -= np.rint(dS); dA = fracA - fracf; dA -= np.rint(dA)
        r['geometry'] = {'n_atoms': len(symf), 'composition': {e: symf.count(e) for e in sorted(set(symf))},
                         'relax_in_equals_final_A': round(float(disp.max()), 6),
                         'note': 'archived relax.in = converged geometry by construction (RESULTS_LOG 2026-10-13 entry); relaxation measured against the parent',
                         'FINAL_input_minus_relax_final_A': float(np.abs(dS @ cell).max()), 'A20_input_minus_relax_final_A': float(np.abs(dA @ cell).max()),
                         'cell_FINAL_minus_relax_in_A': float(np.abs(cellS - cell).max()), 'src_final': sf}
        if 'W' in symf:
            w = symf.index('W')
            r['geometry']['W_O_A'] = [round(x, 4) for x in q.neighbours(cell, fracf, w, 'O', symf, 2.6)]
        geo[c] = (cell, symf, fracf)
        # A20(ii) input vs FINAL input: changed lines
        a_in = q.lines(str(H / 'checks' / 'gpumax_work' / 'a20_g002' / c / 'scf.in'))
        f_in = q.lines(str(sp.with_suffix('.in')))
        r['a20_input_changed_lines'] = [(i + 1, x.strip(), y.strip()) for i, (x, y) in enumerate(zip(a_in, f_in)) if x != y] + \
                                       ([('length', len(a_in), len(f_in))] if len(a_in) != len(f_in) else [])
        # band filling of the FINAL (k4)
        nvb = vb_count(symf)
        wk = q.kweights(sp)
        b = q.eig_blocks(sp)
        ev = np.array([x[1] for x in b])
        occ = q.occ_blocks(sp)
        f = np.array([o[0] for o in occ])
        ef = r['E_F_k4_eV']['value']
        r['bands_k4'] = {'VB_top_band': nvb, 'electrons_above_VB_top': round(float((wk[:, None] * f[:, nvb:]).sum()), 4),
                         'N_check': round(float((wk[:, None] * f).sum()), 4),
                         'VB_max_minus_EF_eV': round(float(ev[:, nvb - 1].max() - ef), 4),
                         'band_above_VB_min_minus_EF_eV': round(float(ev[:, nvb].min() - ef), 4),
                         'band_above_VB_width_eV': round(float(ev[:, nvb].max() - ev[:, nvb].min()), 4),
                         'band_above_VB_electrons': round(float((wk * f[:, nvb]).sum()), 4),
                         'gap_VBmax_to_next_band_min_eV': round(float(ev[:, nvb].min() - ev[:, nvb - 1].max()), 4),
                         'src': b[0][2]}
        res['cells'][c] = r
    # vacancy neighbourhood: displacement of the atoms around the removed O (position taken from the parent final geometry)
    for c, (par, lab) in PARENT.items():
        cellp, symp, fracp = geo[par]
        cellv, symv, fracv = geo[c]
        # removed O found by order-preserving matching (smallest max displacement); the register labels are 0-based indices
        cand = []
        for kk in range(len(symp)):
            if symp[kk] != 'O':
                continue
            rr = [i for i in range(len(symp)) if i != kk]
            if [symp[i] for i in rr] != symv:
                continue
            dd = fracv - fracp[rr]; dd -= np.rint(dd)
            cand.append((float(np.linalg.norm(dd @ cellv, axis=1).max()), kk))
        cand.sort()
        k = cand[0][1]
        assert k == int(lab[1:]), (c, lab, k)
        vpos = fracp[k]
        rest = [i for i in range(len(symp)) if i != k]
        d = fracv - fracp[rest]; d -= np.rint(d); disp = np.linalg.norm(d @ cellv, axis=1)
        dv = fracp[rest] - vpos; dv -= np.rint(dv); dist = np.linalg.norm(dv @ cellv, axis=1)
        near = np.argsort(dist)[:4]
        res['cells'][c]['vacancy'] = {'removed': f'{lab} of {par} (0-based index; atom {k + 1} counting from 1)',
                                      'match_margin_A': [round(cand[0][0], 3), round(cand[1][0], 3)],
                                      'max_relaxation_vs_parent_A': round(float(disp.max()), 3),
                                      'atom_max_relaxation': f'{symv[int(disp.argmax())]}{int(disp.argmax()) + 1}',
                                      'n_atoms_moved_gt_0p05_A': int((disp > 0.05).sum()), 'first_shell': [
            {'atom': symv[i], 'dist_to_vacancy_A': round(float(dist[i]), 3), 'relaxation_A': round(float(disp[i]), 3),
             'moves_away_A': round(float(np.linalg.norm(((fracv[i] - vpos) - np.rint(fracv[i] - vpos)) @ cellv) - dist[i]), 3)} for i in near]}
    E = {c: {s: res['cells'][c]['E_Ry'][s]['value'] for s in SETS} for c in CELLS}

    def dloc(s, near='In31WO47_near'):
        return (E[near][s] - E['In31WO47_far'][s]) * q.RY

    def ddop(s):
        return ((E['In31WO47_far'][s] - E['In31WO48'][s]) - (E['In32O47'][s] - E['In32O48'][s])) * q.RY
    f11 = json.loads((q.OUT / 'f11_hl_vacancy.json').read_text())
    diffs = {}
    for name, fn in (('dE_local_O30', dloc), ('dE_local_O72_sensitivity', lambda s: dloc(s, 'In31WO47_near72')), ('dE_dop', ddop)):
        v = {s: round(fn(s), 5) for s in SETS}
        v['k3_to_k4_meV'] = round((fn('k4_g005') - fn('k3_g005')) * 1000, 2)
        v['A20ii_shift_meV'] = round((fn('k3_g002') - fn('k3_g005')) * 1000, 2)
        v['max_abs_diff_vs_r23_meV'] = round(max(abs(fn(s) - f11['differences_eV'][name][s]) * 1000 for s in SETS), 4)
        diffs[name] = v
    res['differences_eV'] = diffs
    res['energy_max_abs_diff_vs_r23_Ry'] = max(abs(E[c][s] - f11['cells'][c][s]['E_Ry']['value']) for c in CELLS for s in SETS)
    # input hashes against the RESULTS_LOG table (first 16 hex)
    sha = {}
    for l in (H / 'SHA256_REMOTE.txt').read_text().splitlines():
        t = l.split()
        if len(t) == 2:
            sha[t[1]] = t[0][:16]
    res['input_sha16'] = {c: {'relax.in': sha.get(f'vac/{c}/relax.in'), 'FINAL scf.in': sha.get(f'vac/{c}/scf.in'),
                              'A20 scf.in': sha.get(f'checks/gpumax_work/a20_g002/{c}/scf.in')} for c in CELLS}
    res['final_tarball_scf_equals_vac_scf'] = {c: (q.HERE / 'raw_cern' / 'hl' / 'final' / c / 'scf.out').read_bytes() == (H / 'vac' / c / 'scf.out').read_bytes() for c in CELLS}
    # near attempt 1 (A28): SCF count, failures
    a1 = H / 'vac' / 'In31WO47_near' / 'attempt1' / 'relax.out'
    res['near_attempt1'] = {'n_scf_bang': len(q.grep(a1, r'^!\s+total energy')), 'scf_not_converged': len(q.grep(a1, r'convergence NOT achieved')),
                            'energies_Ry': [float(m.group(1)) for m, _ in q.grep(a1, r'^!\s+total energy\s+=\s+(-?[\d.]+)')],
                            'src': q.rel(a1)}
    # PAW vs NC projection basis validation on crystalline In31WO48 (hse/validation, local QE 7.5 run of 2026-10-11)
    vt = (H / 'hse' / 'validation' / 'chi_compare_In31WO48_gamma.txt').read_text().splitlines()
    res['paw_nc_basis_check'] = {'summary_line': vt[-1].strip(), 'src': q.rel(H / 'hse' / 'validation' / 'chi_compare_In31WO48_gamma.txt') + f':{len(vt)}',
                                 'W5d_donor_states_PAW_NC': [l.split()[-3:-1] for l in vt if l.split()[:2] in (['353', '360'], ['354', '361'])]}
    q.dump('f13_hl_raw', res)
    for c, r in res['cells'].items():
        print(c, {s: r['E_Ry'][s]['value'] for s in SETS}, r['bfgs']['value'], 'maxF', r['max_force_component_Ry_bohr']['value'], 'totF', r['total_force_Ry_bohr']['value'],
              'fail', r['scf_not_converged_relax'], 'nk', r['nk'], 'EF', r['E_F_k4_eV']['value'])
        print('   geo', {k: v for k, v in r['geometry'].items() if k != 'src_final'}, 'a20diff', r['a20_input_changed_lines'])
        print('   bands', r['bands_k4'])
        if 'vacancy' in r:
            print('   vac', r['vacancy'])
    print(json.dumps(diffs, indent=0)); print('E diff vs r23 (Ry)', res['energy_max_abs_diff_vs_r23_Ry'])
    print(res['input_sha16']); print(res['final_tarball_scf_equals_vac_scf']); print(res['near_attempt1']); print(res['paw_nc_basis_check'])

    # ---- figure: (a) first-shell relaxation around each vacancy, (b) band filling above the VB top (k4 FINAL)
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.6))
    vac = list(PARENT)
    for j, c in enumerate(vac):
        sh = res['cells'][c]['vacancy']['first_shell']
        ax[0].plot([j] * len(sh), [x['moves_away_A'] for x in sh], ['o', 's', '^', 'D'][j], mfc='none', color=CYCLE[j], ls='none')
    ax[0].axhline(0, color='0.6', lw=0.6)
    ax[0].set_xticks(range(len(vac))); ax[0].set_xticklabels(['In32O47', 'far (O32)', 'near (O30)', 'near72 (O72)'], fontsize=7.5); ax[0].minorticks_off()
    ax[0].tick_params(axis='y', which='minor', left=True); ax[0].yaxis.set_minor_locator(plt.matplotlib.ticker.AutoMinorLocator())
    ax[0].set_ylabel('radial move of first shell (Å)')
    panel(ax[0], 'a', x=-0.2)
    for j, c in enumerate(CELLS):
        bk = res['cells'][c]['bands_k4']
        ax[1].bar(j - 0.18, bk['electrons_above_VB_top'], 0.34, color='white', edgecolor=CYCLE[0], label='above VB top' if j == 0 else None)
        ax[1].bar(j + 0.18, bk['band_above_VB_electrons'], 0.34, color='white', edgecolor=CYCLE[1], hatch='///', label='first band above VB top' if j == 0 else None)
    ax[1].set_xticks(range(len(CELLS))); ax[1].set_xticklabels(['In32O48', 'In31WO48', 'In32O47', 'far', 'near', 'near72'], rotation=40, ha='right', fontsize=7)
    ax[1].minorticks_off(); ax[1].tick_params(axis='y', which='minor', left=True)
    ax[1].set_ylabel('electrons per cell (k4 FINAL)')
    ax[1].legend(loc='upper left', fontsize=6.5)
    panel(ax[1], 'b', x=-0.3)
    fig.tight_layout(w_pad=2.0)
    save(fig, 'fig13_hl_raw_relax_filling')


if __name__ == '__main__':
    main()
