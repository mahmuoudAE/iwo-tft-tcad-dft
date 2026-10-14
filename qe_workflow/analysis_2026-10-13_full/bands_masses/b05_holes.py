"""Hole masses as numbers, as far as the existing eigenvalues allow (writes out/b05_holes.json and figure BM9).

1. Bulk In2O3: band-resolved directional curvature masses of the three valence bands degenerate at Gamma (bands 174-176) along
   Gamma-H = [100], Gamma-N = [110] and Gamma-P = [111] (bands_gamma.out: 10 points per direction, |k| <= 0.153 1/A; windows 2/3/4/6/10
   points), with the coarser bands_path.out lines as a wider-range check; off-Gamma maxima; warping; the angular average of the inverse
   curvature mass per band from a cubic-harmonic expansion 1/m(d) = a + b (S4(d) - 3/5) + c (S6(d) - 1/105) through the three directions
   (S4 = x^4 + y^4 + z^4, S6 = x^2 y^2 z^2 on the unit sphere; <S4> = 3/5, <S6> = 1/105, so a = <1/m>).
2. Bulk DOS hole mass: N_V(300 K) = (1/V) sum_k w_k sum_n exp(-(E_ref - E_nk)/kT) over the valence states (= the integral of the grid DOS
   with the Boltzmann factor; Fermi-Dirac reduces to it for E_F - E_V >> kT), energy windows 0.05-1.0 eV below E_ref and all states,
   two references (own grid maximum; off-Gamma VBM), four grids; m_h,DOS = (N_V / N0)^(2/3) m0 with N0 = 2 (2 pi m0 kT / h^2)^1.5.
3. Slabs and W cells: band-resolved in-plane masses (top three VBs, [100] and [110]); 2-D tensor (D2h / C2v axes) for the top band; for
   SCF-grid-only cells, chord (secant) masses H2M k^2 / |dE| at the grid points, labelled as such.
"""
import json
import math

import numpy as np

import bm
from bm import q, r, plt
import figstyle as fs

R = q.RES
C = fs.CYCLE
D1 = json.loads((bm.OUT / 'b01_masses.json').read_text())
DIRS3 = {'[100] (G-H)': (1, 0, 0), '[110] (G-N)': (1, 1, 0), '[111] (G-P)': (1, 1, 1)}
PATH_DIR = {'[100] (G-H)': (0, 0, 1), '[110] (G-N)': (1, 1, 0), '[111] (G-P)': (1, 1, 1)}   # bands_path: H = (0,0,1) 2pi/a
S4 = {'[100] (G-H)': 1.0, '[110] (G-N)': 0.5, '[111] (G-P)': 1 / 3}
S6 = {'[100] (G-H)': 0.0, '[110] (G-N)': 0.0, '[111] (G-P)': 1 / 27}
N0 = bm.nc3d(1.0)                                  # 2 (2 pi m0 kT/h^2)^1.5 at 300 K, cm^-3


def angular_average(inv):
    """a = <1/m> from 1/m(d) = a + b (S4 - 3/5) + c (S6 - 1/105) through the three directions."""
    ds = list(DIRS3)
    A = np.array([[1, S4[d] - 0.6, S6[d] - 1 / 105] for d in ds])
    a, b, c = np.linalg.solve(A, np.array([inv[d] for d in ds]))
    return float(a), float(b), float(c)


def star_weighted(inv):
    """Cross-check: <1/m> ~ (6/m100 + 12/m110 + 8/m111)/26 (number of equivalent directions)."""
    ds = list(DIRS3)
    return (6 * inv[ds[0]] + 12 * inv[ds[1]] + 8 * inv[ds[2]]) / 26


def bulk_bands():
    bg = bm.read_bands(q.BULK / 'bands_gamma.out')
    bp = bm.read_bands(q.BULK / 'bands_path.out')
    no = int(bg['nelec'] / 2)
    out = {'bands': {}, 'src_gamma': bg['path'], 'src_path': bp['path']}
    for n in (no - 3, no - 2, no - 1):            # 0-based 173, 174, 175 = bands 174, 175, 176
        rec = {'directions': {}}
        for d, v in DIRS3.items():
            idx = bm.line_indices(bg['K'], v)
            k = np.linalg.norm(bg['K'][idx], axis=1)
            fit = bm.fit_line(k, bg['E'][idx, n], 'h')
            ip = bm.line_indices(bp['K'], PATH_DIR[d])[:5]
            kp = np.linalg.norm(bp['K'][ip], axis=1)
            dp = -(bp['E'][ip, n] - bp['E'][ip[0], n])
            rec['directions'][d] = {
                'windows': {w: {kk: fit['windows'][w][kk] for kk in ('kmax_invA', 'Emax_meV', 'm_anchored', 'sigma_round', 'm_intercept')}
                            for w in fit['windows']},
                'dE_meV_hole_convention': fit['dE_meV'], 'k_invA': fit['k_invA'],
                'path_check': {'k_invA': [r(x, 4) for x in kp[1:]], 'dE_meV': [r(x * 1000, 2) for x in dp[1:]],
                               'chord_mass': [r(bm.H2M * kk * kk / x, 3) if abs(x) > 1e-5 else None for kk, x in zip(kp[1:], dp[1:])]},
                'src': f"{bg['src'][idx[0]]} .. {bg['src'][idx[-1]]}"}
        # windows 3, 4, 6: angular average where all three directional inverse masses exist
        # ESTIMATED diagnostic: inverse-curvature average under the stated angular model (three directions fix three coefficients,
        # so the model is not tested); no transport or DOS significance. An unresolved (printed-flat) direction is UNRESOLVED, not zero.
        rec['angular'] = {}
        for w in ('3', '4', '6', '10'):
            ms = {d: rec['directions'][d]['windows'][w]['m_anchored'] for d in DIRS3}
            if any(m is None for m in ms.values()):
                rec['angular'][w] = {'status': 'UNRESOLVED', 'unresolved_directions': [d for d, m in ms.items() if m is None]}
                continue
            inv = {d: 1.0 / m for d, m in ms.items()}
            a, b_, c_ = angular_average(inv)
            pos = [x for x in inv.values() if x > 0]
            sw = star_weighted(inv)
            rec['angular'][w] = {'status': 'ok', 'inv_m_by_dir': {d: r(x, 4) for d, x in inv.items()}, 'avg_inv_m': r(a, 4),
                                 'm_inverse_curvature_average': r(1 / a, 3) if a > 0 else None,
                                 'm_star_weighted_same_data': r(1 / sw, 3) if sw > 0 else None,
                                 'sampled_directional_curvature_ratio': r(max(inv.values()) / min(inv.values()), 2) if min(inv.values()) > 0 else None,
                                 'all_directions_positive': len(pos) == 3}
        out['bands'][str(n + 1)] = rec
    # off-Gamma maxima of the top band (176): [100] fine line, [110] from the path (G-N), [111] none
    top = no - 1
    om = D1['bulk']['hole_summary']['VBM_longitudinal_[100]']
    ipn = bm.line_indices(bp['K'], (1, 1, 0))
    kn = np.linalg.norm(bp['K'][ipn], axis=1)
    en = bp['E'][ipn, top]
    om110 = bm.offgamma_max(kn, en)
    ipp = bm.line_indices(bp['K'], (1, 1, 1))
    kpp = np.linalg.norm(bp['K'][ipp], axis=1)
    epp = bp['E'][ipp, top]
    out['offgamma_maxima'] = {
        '[100] (G-H)': {**om, 'source': 'bands_gamma.out (5-point parabola)'},
        '[110] (G-N)': {**(om110 or {}), 'source': 'bands_path.out G-N (coarse, 0.039 1/A steps)',
                        'bands_gamma_end_rise_meV': r((bg['E'][bm.line_indices(bg['K'], (1, 1, 0))[-1], top] - bg['E'][0, top]) * 1000, 2)},
        '[111] (G-P)': {'max_at_Gamma': bool(np.argmax(epp) == 0), 'E_drop_at_first_path_point_meV': r((epp[0] - epp[1]) * 1000, 2)},
        'global_VBM_minus_VB_Gamma_meV': D1['bulk']['VBM_minus_VBGamma_meV'], 'kT_meV': r(bm.KT * 1000, 2)}
    # triplet average of the angular-averaged inverse masses (equal Gamma populations)
    trip = {}
    for w in ('3', '4', '6'):
        bl = list(out['bands'])
        ok = [out['bands'][b]['angular'][w].get('status') == 'ok' for b in bl]
        invs = [out['bands'][b]['angular'][w]['avg_inv_m'] if k else None for b, k in zip(bl, ok)]
        rec_w = {'avg_inv_m_bands': invs}
        if ok[0] and ok[1]:
            a2 = float(np.mean(invs[:2]))
            rec_w['m_cond_two_falling_bands'] = r(1 / a2, 3) if a2 > 0 else None
        if all(ok):
            a = float(np.mean(invs))
            rec_w['triplet_avg_inv_m'] = r(a, 4)
            rec_w['m_cond_triplet_incl_camelback'] = r(1 / a, 3) if a > 0 else None
        else:
            rec_w['status_triplet'] = 'UNRESOLVED (a direction of band 176 is printed-flat in this window)'
        trip[w] = rec_w
    trip['note'] = ('Gamma-local averages with equal band populations; the camel-back band 176 has a negative net angular curvature '
                    '(it rises on average from Gamma), so the triplet average mixes signs and is not a transport mass')
    out['triplet_gamma_average'] = trip
    return out


def nv_windows(p, vb_top, Ev, label, note):
    b = bm.read_bands(p)
    w = q.kweights(p)
    m, i = q.last(p, r'unit-cell volume\s*=\s*([\d.]+) \(a\.u\.\)\^3')
    V = float(m.group(1)) * q.BOHR ** 3
    E = b['E'][:, :vb_top]
    ref = float(E.max()) if Ev is None else Ev
    res = {}
    for win in (0.05, 0.1, 0.2, 0.3, 0.5, 1.0, None):
        mask = (E <= ref + 1e-6) & ((ref - E) <= (win if win else 1e9))
        s = float(np.sum(w[:, None] * np.exp(-np.clip(ref - E, 0, None) / bm.KT) * mask))
        nv = s / (V * 1e-24)
        res['all' if win is None else f'{win:g}'] = {'Nv_cm3': float(f'{nv:.4g}'), 'm_h_dos': r((nv / N0) ** (2 / 3), 3),
                                                      'n_states_in_window_per_cell': r(float(np.sum(w[:, None] * mask)), 2)}
    return {'label': label, 'E_ref_eV': r(ref, 4), 'E_ref_note': note, 'n_k': b['nk'], 'volume_A3': r(V, 2),
            'src': f"{b['src'][0]} .. {b['src'][-1]}", 'by_window_eV': res}


def bulk_nv():
    bp = bm.read_bands(q.BULK / 'bands_path.out')
    vbm = float(bp['E'][:, 175].max())
    dvb = D1['bulk']['VBM_minus_VBGamma_meV'] / 1000
    hl = q.HERE / 'raw_cern' / 'hl' / 'vac' / 'In32O48'
    g3 = bm.read_bands(hl / 'relax.out')['E'][0, 351] + dvb
    g4 = bm.read_bands(hl / 'scf.out')['E'][0, 351] + dvb
    gx = bm.read_bands(q.BULK / 'scf_ecut71_k4.out')['E'][0, 175] + dvb
    grids = {
        'prim_k3 (4 k, a = 10.306 A)': [(q.BULK / 'vcrelax_ecut71_k3.out', 176, None, 'own grid maximum (Gamma)'),
                                        (q.BULK / 'vcrelax_ecut71_k3.out', 176, vbm, 'true VBM of bands_path (same SCF potential)')],
        'prim_k4 (8 k, exp. lattice 10.117 A)': [(q.BULK / 'scf_ecut71_k4.out', 176, None, 'own grid maximum'),
                                                 (q.BULK / 'scf_ecut71_k4.out', 176, gx, 'VB(Gamma) + 4.4 meV (offset transferred)')],
        '80-atom k3 (6 k, H-L parent)': [(hl / 'relax.out', 352, None, 'own grid maximum'), (hl / 'relax.out', 352, g3, 'VB(Gamma) + 4.4 meV')],
        '80-atom k4 (14 k, H-L parent)': [(hl / 'scf.out', 352, None, 'own grid maximum'), (hl / 'scf.out', 352, g4, 'VB(Gamma) + 4.4 meV')],
    }
    out = {}
    for g, items in grids.items():
        out[g] = [nv_windows(p, n, ev, g, note) for p, n, ev, note in items]
    allv = [x['by_window_eV']['all']['Nv_cm3'] for v in out.values() for x in v]
    hse = D1['HSE']['Nv_k3_grid_own_max']
    return {'grids': out, 'Nv_range_cm3': [min(allv), max(allv)], 'm_h_dos_range': [r((min(allv) / N0) ** (2 / 3), 2), r((max(allv) / N0) ** (2 / 3), 2)],
            'N0_cm3': float(f'{N0:.5g}'), 'deck_NV300_cm3': 1e19, 'deck_implied_m_h_dos': r((1e19 / N0) ** (2 / 3), 3),
            'HSE_k3_same_grid': {k: {'Nv_cm3': v['Nv_cm3'], 'm_h_dos': r((v['Nv_cm3'] / N0) ** (2 / 3), 2)} for k, v in hse.items()},
            'HSE_over_NCPBE_m_h_dos': [r((hse[k]['Nv_cm3'] / hse['NC_PBE']['Nv_cm3']) ** (2 / 3), 3) for k in ('HSE06_q1', 'HSE06_q3')]}


def tensor2d(mx, m110):
    if mx is None or m110 is None or mx <= 0 or m110 <= 0:
        return None
    inv_y = 2.0 / m110 - 1.0 / mx
    if inv_y <= 0:
        return None
    my = 1 / inv_y
    return {'m_x': r(mx, 3), 'm_y': r(my, 3), 'm_dos_2d': r(math.sqrt(mx * my), 3), 'm_cond_2d': r(2 / (1 / mx + 1 / my), 3)}


SLAB_REASON = {
    '0.51': 'In8(OH)24 layer; the top VB is 98 % OH-oxygen O 2p; a second VB maximum on the 3x3x1 grid ([100], 0.196 1/A) lies 1.3 meV above '
            'VB(Gamma): multi-valley, the masses below are those of the Gamma maximum only. Fix: 6x6x1 nscf + [010] line (rectangular cell)',
    '0.75': 'top VB 75 % on OH oxygens; next band 29.1 meV lower (Boltzmann factor 0.32); polar slab without dipole correction: the curvature '
            'may change with a dipole correction. Fix: dipole-corrected SCF + bands',
    '1.0': 'top two VBs within 3.3 meV at Gamma (degenerate on the kT scale); the top band is extremely flat along [100] (drop 0.1 meV at 0.03 1/A; '
           '3-point mass has a {rel1} % print-rounding error) and crosses the next band near 0.1 1/A. Character of the pure 1 nm VB not projected '
           '(the W twin: 72 % OH). Fix: denser lines (0.005 1/A) with 6 decimals (verbosity high prints 4) or a fitted k.p model; projwfc of the pure 1 nm',
    '2.0': 'VB top bulk-like (OH share 0.001) but the next band is 9.3 meV lower; the top band turns over along [100] (minimum near 0.075 1/A, '
           'rising again): only the n <= 4 window is parabolic. Fix: denser k-lines and a 2-D grid around Gamma',
}


def slabs():
    out = {}
    for lab in ('0.51', '0.75', '1.0', '2.0'):
        s = D1['slabs'][lab]
        no = s['n_occ']
        bands = {}
        for bn in (str(no - 2), str(no - 1), str(no)):
            h = s['hole'][bn]
            bands[bn] = {d: {w: h[d]['windows'][w]['m_anchored'] for w in h[d]['windows']} for d in ('[100]', '[110]')}
            bands[bn]['sigma_round_3pt'] = {d: h[d]['windows']['3']['sigma_round'] for d in ('[100]', '[110]')}
        top = bands[str(no)]
        out[lab] = {'job': s['job'], 't_HH_nm': s['t_HH_nm'], 'VBM_location': s['VBM_location'], 'next_VB_at_Gamma_meV': s['VB_sep_Gamma_meV'],
                    'next_band_boltzmann_factor': r(math.exp(-s['VB_sep_Gamma_meV'] / 1000 / bm.KT), 3), 'bands_anchored_masses': bands,
                    'top_band_tensor_n3': tensor2d(top['[100]'].get('3'), top['[110]'].get('3')),
                    'top_band_tensor_n4': tensor2d(top['[100]'].get('4'), top['[110]'].get('4')),
                    'passes_local_fit_screens': s['hole_verdict']['meaningful'], 'screen_reasons': s['hole_verdict']['reasons'],
                    'Nv2D_cm2': s['Nv']['Nv2D_cm2'], 'Nv_quasi3D_cm3': s['Nv']['Nv_quasi3D_cm3'],
                    'm_h_dos_2d_equiv': s['Nv']['m_dos_equiv_2d'], 'm_h_dos_3d_equiv_quasi3D': r((s['Nv']['Nv_quasi3D_cm3'] / N0) ** (2 / 3), 2),
                    'why_not_a_clean_mass_and_fix': SLAB_REASON[lab].format(
                        rel1=f"{100 * s['hole'][str(no)]['[100]']['windows']['3']['sigma_round'] / abs(s['hole'][str(no)]['[100]']['windows']['3']['m_anchored']):.1f}")}
    return out


def w_cells():
    out = {}
    for site, job in (('bulk 8b', 'iwo_W8b'), ('bulk 24d', 'iwo_W24d')):
        b = bm.read_bands(R / job / 'bands.out')
        npure = int((b['nelec'] - 1) / 2)
        vb = npure - 2
        rec = {}
        for n in (vb - 2, vb - 1, vb):
            rec[str(n + 1)] = {}
            for d, v in (('[100]', (1, 0, 0)), ('[110]', (1, 1, 0)), ('[111]', (1, 1, 1))):
                idx = bm.line_indices(b['K'], v)
                k = np.linalg.norm(b['K'][idx], axis=1)
                f = bm.fit_line(k, b['E'][idx, n], 'h')
                rec[str(n + 1)][d] = {w: f['windows'][w]['m_anchored'] for w in f['windows']}
        out[site] = {'job': job, 'VB_top_band': vb + 1, 'bands_anchored_masses': rec,
                     'VB_sep_Gamma_meV': r((b['E'][0, vb] - b['E'][0, vb - 1]) * 1000, 2),
                     'reason': ('80-atom cubic cell: the bcc H point folds onto Gamma, so the valence states at Gamma mix Gamma and H; the top bands are '
                                'within a few to 20 meV and nearly flat (drops of 0.1-0.3 meV at 0.015 1/A). Masses are listed for completeness only; '
                                'the pure 80-atom H-L cell would be the like-for-like reference (no band run exists).'),
                     'src': b['path']}
    for lab, wjob, pjob in (('W slab 1 nm', 'iwo_slab1_final_cpu', 'slab1r_final_cpu'), ('W slab 2 nm', 'iwo_slab2_final_cpu', 'slab2_relax_c2')):
        rec = {}
        for kind, job, off in (('W', wjob, 2), ('pure twin', pjob, 1)):
            b = bm.read_bands(R / job / 'scf.out')
            n_pure = int((b['nelec'] - 1) / 2) if kind == 'W' else int(b['nelec'] / 2)
            n = n_pure - 2 if kind == 'W' else n_pure - 1        # 0-based VB top: band n_pure - 1 (W cell), n_pure (pure)
            k = np.linalg.norm(b['K'], axis=1)
            dE = b['E'][0, n] - b['E'][:, n]
            rec[kind] = {'VB_top_band': n + 1, 'k_invA': [r(x, 4) for x in k[1:]], 'drop_meV': [r(x * 1000, 2) for x in dE[1:]],
                         'chord_mass': [r(bm.H2M * kk * kk / x, 2) if x > 1e-4 else None for kk, x in zip(k[1:], dE[1:])],
                         'src': f"{b['src'][0]} .. {b['src'][-1]}"}
        out[lab] = {**rec, 'label': 'ESTIMATED chord masses H2M k^2 / drop at the 3x3x1 grid points (0.20-0.29 1/A): NOT band-edge masses',
                    'reason': 'SCF grid only (k-path run missing; the 1 nm bands step failed in cdiaghg); VB top 72 % OH (W slabs)',
                    'fix': 'SCF + bands (CG) on the W-slab geometries (runs 1 and 2 of BANDS_MASSES.md Section 6)'}
    return out


def tcad(nv, sl):
    kT = bm.KT
    rows = {}
    # bulk / thick films: 3-D COMPUTED Nv (80-atom k4 grid, own maximum)
    nvb = nv['grids']['80-atom k4 (14 k, H-L parent)'][0]['by_window_eV']['all']['Nv_cm3']
    for t, src in ((13.2, 'bulk 3-D'), (6.3, 'bulk 3-D')):
        rows[str(t)] = {'NV300_cm3': nvb, 'form': '3-D', 'source': src,
                        'label': ('ASSUMED transfer of the COMPUTED crystalline bulk value (PBE, 80-atom k4 grid, own-maximum reference; '
                                  '1.6-2.7e21 over grids and references) to the device film')}
    for lab in ('0.75', '1.0'):
        rows[str(sl[lab]['t_HH_nm'])] = {'NV300_cm3': sl[lab]['Nv_quasi3D_cm3'], 'form': 'quasi-3-D = Nv2D / t_HH (all subbands, 3x3x1 grid)',
                                         'label': 'COMPUTED on a 4-k grid (coarse)' + ('; polar slab' if lab == '0.75' else ''), 'source': sl[lab]['job']}
    rows['2.0'] = {'NV300_cm3': sl['2.0']['Nv_quasi3D_cm3'], 'form': 'quasi-3-D = Nv2D / t_HH (all subbands, Boltzmann sum on the 3x3x1 grid)',
                   'label': 'COMPUTED on a 4-k grid (coarse; convergence unestablished)', 'source': 'slab2_relax_c2',
                   'note': 'a single-subband quasi-2-D formula is NOT justified for holes: the top VBs are within 9 meV'}
    # n_i and the SRH / trap-emission bound for the electrons-only deck (carriers=1 electrons, models srh)
    out = {'rows': rows}
    dk = bm.load_parent('f06_confinement_laws')['decks']['C10@2.0']['deck']
    eg, nc = dk['eg300']['value'], dk['nc300']['value']
    ni_deck = math.sqrt(nc * 1e19) * math.exp(-eg / (2 * kT))
    ni_new = math.sqrt(nc * rows['2.0']['NV300_cm3']) * math.exp(-eg / (2 * kT))
    tau = 1e-6
    ep = 1e-15 * 1e7 * rows['2.0']['NV300_cm3'] * math.exp(-(eg - 0.6) / kT)
    dE_p = kT * math.log(rows['2.0']['NV300_cm3'] / 1e10)
    out['impact'] = {
        'deck_settings': 'models fermi srh; method ... carriers=1 electrons (run_0061 device.in:81, :103): holes are not solved',
        'ni_deck_cm3': float(f'{ni_deck:.3g}'), 'ni_with_computed_Nv_cm3': float(f'{ni_new:.3g}'),
        'max_SRH_generation_cm3_s': float(f'{ni_new / (2 * tau):.3g}'),
        'hole_emission_rate_deep_acceptor_Ec_minus_0p6_s': float(f'{ep:.3g}'),
        'E_F_minus_E_V_for_p_1e10_eV': r(dE_p, 3),
        'reading': ('With carriers=1 the Nv change enters through n_i (x14): n_i stays ~1e-8 cm^-3 and the equilibrium SRH generation bound '
                    'n_i/(2 tau) is ~3e-3 cm^-3 s^-1. The hole emission rate quoted is evaluated at the centre of the deep acceptor Gaussian '
                    '(E_C - 0.6 eV) only: it does not bound the whole distribution or field-assisted emission. In a two-carrier model the hole '
                    'density is set by the local hole quasi-Fermi level, not by the electron one: p > 1e10 cm^-3 requires that level within ~0.7 eV '
                    'of E_V (at N_V ~ 2e21). Inputs: deck C10@2.0 eg300 and nc300, tau 1e-6 s, sigma 1e-15 cm^2, v_th 1e7 cm/s (ASSUMED rates).')}
    return out


def figure(o):
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_W, 5.0))
    bg = bm.read_bands(q.BULK / 'bands_gamma.out')
    bp = bm.read_bands(q.BULK / 'bands_path.out')
    no = int(bg['nelec'] / 2)
    e0 = bg['E'][0, no - 1]
    ax = axs[0, 0]
    sty = {'[100] (G-H)': '-', '[110] (G-N)': '--', '[111] (G-P)': ':'}
    for j, n in enumerate((no - 3, no - 2, no - 1)):
        for d, v in DIRS3.items():
            idx = bm.line_indices(bg['K'], v)
            k = np.linalg.norm(bg['K'][idx], axis=1)
            ax.plot(k, (bg['E'][idx, n] - e0) * 1000, sty[d], color=C[j], lw=1.0, label=f'band {n + 1}' if d.startswith('[100]') else None)
            ip = bm.line_indices(bp['K'], PATH_DIR[d])[:9]
            kp = np.linalg.norm(bp['K'][ip], axis=1)
            ax.plot(kp, (bp['E'][ip, n] - e0) * 1000, 'o', color=C[j], ms=2.2, mfc='none', mew=0.5)   # same SCF potential as bands_gamma
    for d, mk in (('[100] (G-H)', 'o'), ('[110] (G-N)', 's')):
        om = o['bulk']['offgamma_maxima'][d]
        if om.get('k0_invA'):
            ax.plot([om['k0_invA']], [om['E0_minus_Gamma_meV']], mk, mfc='white', mec='k', ms=5, zorder=5)
    ax.axhline(0, color=fs.GREY, lw=0.5)
    ax.set_xlim(0, 0.33)
    ax.set_ylim(-60, 8)
    ax.set_xlabel(r'$|k|$ (1/$\mathrm{\AA}$)')
    ax.set_ylabel(r'$E-E_\mathrm{VB}(\Gamma)$ (meV)')
    ax.legend(loc='lower left', fontsize=6)
    fs.panel(ax, 'a', x=-0.2)
    ax = axs[0, 1]
    mk = {'[100] (G-H)': 'o', '[110] (G-N)': 's', '[111] (G-P)': '^'}
    for j, (bn, rec) in enumerate(o['bulk']['bands'].items()):
        for d in DIRS3:
            w = rec['directions'][d]['windows']
            E = [abs(w[n]['Emax_meV']) for n in w if w[n]['m_anchored'] is not None]
            m = [w[n]['m_anchored'] for n in w if w[n]['m_anchored'] is not None]
            Ep = [e for e, mm in zip(E, m) if mm > 0]
            mp = [mm for mm in m if mm > 0]
            En = [e for e, mm in zip(E, m) if mm < 0]
            mn = [-mm for mm in m if mm < 0]
            if mp:
                ax.plot(Ep, mp, mk[d] + '-', color=C[j], ms=3.2, lw=0.7)
            if mn:
                ax.plot(En, mn, mk[d] + ':', color=C[j], ms=3.2, lw=0.7, mfc='white')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'window $|\Delta E|_\mathrm{max}$ (meV)')
    ax.set_ylabel(r'$|m^*_h|$ ($m_0$)')
    ax.yaxis.set_minor_formatter(plt.NullFormatter())
    fs.panel(ax, 'b', x=-0.2)
    ax = axs[1, 0]
    labs = list(o['bulk_Nv']['grids'])
    x = np.arange(len(labs))
    for j, ref in enumerate((0, 1)):
        y = [(o['bulk_Nv']['grids'][g][ref]['by_window_eV']['all']['Nv_cm3'] / bm.nc3d(1.0)) ** (2 / 3) for g in labs]
        ax.plot(x + 0.08 * (2 * j - 1), y, 'os'[j], color=C[j], ms=4.5, mfc='none' if j else C[j])
    ax.axhline(o['bulk_Nv']['deck_implied_m_h_dos'], color='k', ls='--', lw=0.8)
    hs = o['bulk_Nv']['HSE_k3_same_grid']
    ax.plot([0.25, 0.3], [hs['HSE06_q1']['m_h_dos'], hs['HSE06_q3']['m_h_dos']], 'v', color=C[3], ms=4.5, mfc='none')
    ax.set_yscale('log')
    ax.set_xticks(x)
    ax.set_xticklabels(['prim k3', 'prim k4\n(exp. a)', '80-at k3', '80-at k4'], fontsize=7)
    ax.tick_params(axis='x', which='minor', bottom=False, top=False)
    ax.set_ylabel(r'$m^*_{h,\mathrm{DOS}}$ ($m_0$)')
    ax.set_ylim(0.3, 50)
    ax.yaxis.set_minor_formatter(plt.NullFormatter())
    fs.panel(ax, 'c', x=-0.2)
    ax = axs[1, 1]
    for j, lab in enumerate(('0.51', '0.75', '1.0', '2.0')):
        job = o['slabs'][lab]['job']
        b = bm.read_bands(R / job / 'bands.out')
        n = int(b['nelec'] / 2) - 1
        i100 = bm.line_indices(b['K'], (1, 0, 0))
        i110 = bm.line_indices(b['K'], (1, 1, 0))
        for idx, sgn in ((i100, 1), (i110, -1)):
            k = np.linalg.norm(b['K'][idx], axis=1)
            for m_, ls in ((n, '-'), (n - 1, ':')):
                ax.plot(sgn * k, (b['E'][idx, m_] - b['E'][0, n]) * 1000, ls, color=C[j], lw=1.0, label=f'{lab} nm' if (sgn == 1 and m_ == n) else None)
    ax.axvline(0, color=fs.GREY, lw=0.5)
    ax.set_xlim(-0.155, 0.155)
    ax.set_ylim(-100, 5)
    ax.set_xticks([-0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15])
    ax.set_xticklabels(['0.15', '', '', r'$\bar\Gamma$', '', '', '0.15'])
    ax.set_xlabel(r'$k_{[110]}$ | $k_{[100]}$ (1/$\mathrm{\AA}$)')
    ax.set_ylabel(r'$E-E_\mathrm{VB}(\bar\Gamma)$ (meV)')
    ax.legend(loc='lower left', fontsize=5.6, ncol=2, columnspacing=0.8, handlelength=1.4)
    fs.panel(ax, 'd', x=-0.2)
    fig.subplots_adjust(wspace=0.35, hspace=0.42)
    bm.save(fig, 'BM9_hole_masses')


def main():
    o = {'kT_meV': r(bm.KT * 1000, 3), 'N0_cm3': float(f'{N0:.5g}')}
    o['bulk'] = bulk_bands()
    o['bulk_Nv'] = bulk_nv()
    o['slabs'] = slabs()
    o['W_cells'] = w_cells()
    o['tcad'] = tcad(o['bulk_Nv'], o['slabs'])
    bm.dump('b05_holes', o)
    for bn, rec in o['bulk']['bands'].items():
        print('band', bn, {d: {w: rec['directions'][d]['windows'][w]['m_anchored'] for w in ('2', '3', '4', '6', '10')} for d in DIRS3})
        print('   angular', {w: (v.get('m_inverse_curvature_average'), v.get('m_star_weighted_same_data'), v.get('sampled_directional_curvature_ratio'), v.get('status')) for w, v in rec['angular'].items()})
        print('   path chord', {d: rec['directions'][d]['path_check']['chord_mass'] for d in DIRS3})
    print('offgamma', o['bulk']['offgamma_maxima'])
    print('triplet', o['bulk']['triplet_gamma_average'])
    print('Nv', o['bulk_Nv']['Nv_range_cm3'], o['bulk_Nv']['m_h_dos_range'], o['bulk_Nv']['HSE_k3_same_grid'], o['bulk_Nv']['deck_implied_m_h_dos'])
    for g, v in o['bulk_Nv']['grids'].items():
        print(g, [(x['E_ref_note'][:20], {w: (y['Nv_cm3'], y['m_h_dos']) for w, y in x['by_window_eV'].items()}) for x in v])
    for lab, s in o['slabs'].items():
        print(lab, s['top_band_tensor_n3'], s['top_band_tensor_n4'], s['m_h_dos_3d_equiv_quasi3D'])
    for lab, s in o['W_cells'].items():
        print(lab, {k: v for k, v in s.items() if k in ('bands_anchored_masses', 'W', 'pure twin')})
    print(o['tcad'])
    figure(o)


if __name__ == '__main__':
    main()
