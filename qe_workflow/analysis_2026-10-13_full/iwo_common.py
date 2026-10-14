"""Shared read-out for the W-containing cells (bulk 80-atom W8b / W24d and the 1 / 2 nm W slabs).

Band count (PAW): In 4d10 is in the valence (5 semicore bands per In), W 5s2 5p6 (4 bands per W), so a W cell has one
occupied band fewer below the gap than its pure twin: VB top = n_pure - 1, host CB bottom = n_pure (checked here with
projwfc: the VB top must be O 2p, the next band In 5s / O 2s).
Occupations: the 'occupation numbers' printed by pw.x (verbosity high) and, independently, QE's Marzari-Vanderbilt
wgauss at the printed Fermi energy and the degauss of the input; both must sum to the electron count.
"""
import re

import numpy as np

import qeio as q


def filling(d, scf='scf.out', vb=None, projwfc=True):
    d = q.RES / d
    p = d / scf
    pin = d / scf.replace('.out', '.in')
    wk = q.kweights(p)
    blocks = q.eig_blocks(p)
    ev = [b[1] for b in blocks]
    ef, sef = q.fermi(p)
    ne, sne = q.nelec(p)
    deg = float(re.search(r'degauss\s*=\s*([\d.eEdD+-]+)', pin.read_text()).group(1).replace('d', 'e')) * q.RY
    occ_p = q.occ_blocks(p)
    nb = len(ev[0])
    f_mv = np.array([[q.wgauss_mv((ef - e) / deg) for e in ev[k]] for k in range(len(wk))])
    f_pr = np.array([o[0] for o in occ_p]) if occ_p else None
    out = {'E_F_eV': q.V(ef, sef), 'n_electrons': q.V(ne, sne), 'degauss_eV': round(deg, 5), 'n_k': len(wk), 'n_bands': nb,
           'sum_wk': round(float(wk.sum()), 6), 'eig_src': blocks[0][2],
           'N_from_MV': round(float((wk[:, None] * f_mv).sum()), 4),
           'N_from_printed_occ': round(float((wk[:, None] * f_pr).sum()), 4) if f_pr is not None else None,
           'max_abs_MV_minus_printed_occ': float(np.abs(f_mv - f_pr).max()) if f_pr is not None else None}
    f = f_pr if f_pr is not None else f_mv
    out['electrons_above_VB_top'] = round(float((wk[:, None] * f[:, vb:]).sum()), 4)
    out['electrons_per_band'] = {str(n): round(float((wk * f[:, n - 1]).sum()), 4) for n in range(vb - 1, vb + 8)}
    if not projwfc:
        return out
    pf = next(d.glob('projwfc_*.out'))
    states, kb = q.projwfc(pf)
    assert len(kb) == len(wk)
    # first k must be Gamma
    k0 = blocks[0][0]
    assert np.allclose(k0, 0), k0

    def ch(kk, n, el, l):
        return sum(c for s, c in kk[n][1].items() if states[s][1] == el and states[s][3] == l)
    wd = np.array([[ch(kb[k], n, 'W', 2) if n in kb[k] else np.nan for n in range(1, nb + 1)] for k in range(len(wk))])
    ins = np.array([[ch(kb[k], n, 'In', 0) if n in kb[k] else np.nan for n in range(1, nb + 1)] for k in range(len(wk))])
    op = np.array([[ch(kb[k], n, 'O', 1) if n in kb[k] else np.nan for n in range(1, nb + 1)] for k in range(len(wk))])
    os_ = np.array([[ch(kb[k], n, 'O', 0) if n in kb[k] else np.nan for n in range(1, nb + 1)] for k in range(len(wk))])
    nproj = min(len(kb[0]), nb)
    occ_above = f[:, vb:nproj]
    out['W5d_projected_electrons'] = round(float(np.nansum(wk[:, None] * occ_above * wd[:, vb:nproj])), 4)
    out['projwfc'] = q.rel(pf)
    bands = {}
    for n in range(vb - 1, vb + 8):
        bands[str(n)] = {'E_Gamma_minus_EF_eV': round(kb[0][n][0] - ef, 4), 'src': f'{q.rel(pf)}:{kb[0][n][3]}',
                         'Wd_Gamma': round(float(wd[0, n - 1]), 3), 'Ins_Gamma': round(float(ins[0, n - 1]), 3),
                         'Op_Gamma': round(float(op[0, n - 1]), 3), 'Os_Gamma': round(float(os_[0, n - 1]), 3),
                         'Wd_kavg': round(float(np.nansum(wk * wd[:, n - 1]) / wk.sum()), 3),
                         'Ins_kavg': round(float(np.nansum(wk * ins[:, n - 1]) / wk.sum()), 3),
                         'Op_kavg': round(float(np.nansum(wk * op[:, n - 1]) / wk.sum()), 3),
                         'width_eV': round(float(max(e[n - 1] for e in ev) - min(e[n - 1] for e in ev)), 4),
                         'electrons': out['electrons_per_band'][str(n)]}
    out['bands'] = bands
    vbE, cbE = kb[0][vb][0], kb[0][vb + 1][0]
    out['gap_VBtop_to_hostCB_Gamma_eV'] = round(cbE - vbE, 4)
    out['EF_minus_hostCB_Gamma_eV'] = round(ef - cbE, 4)
    out['hostCB_min_over_k_minus_EF_eV'] = round(float(min(e[vb] for e in ev) - ef), 4)
    out['VB_top_max_over_k_eV'] = round(float(max(e[vb - 1] for e in ev)), 4)
    wl = next(n for n in range(vb + 2, vb + 15) if wd[0, n - 1] >= 0.30)
    out['W_rich_band_Gamma'] = wl
    out['W_rich_minus_hostCB_Gamma_eV'] = round(kb[0][wl][0] - cbE, 4)
    out['W_rich_minus_EF_Gamma_eV'] = round(kb[0][wl][0] - ef, 4)
    # all bands at Gamma for the scatter plot
    out['gamma_scatter'] = [(round(kb[0][n][0] - ef, 4), round(float(wd[0, n - 1]), 3)) for n in range(vb - 30, min(nproj, vb + 40) + 1)]
    out['_wd'] = wd; out['_ev'] = ev; out['_wk'] = wk
    return out


def strip(o):
    return {k: v for k, v in o.items() if not k.startswith('_')}
