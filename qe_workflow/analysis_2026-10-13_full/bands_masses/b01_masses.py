"""Effective masses (electrons and holes), non-parabolicity, DOS / conductivity masses and valence-band DOS for every
crystalline system with band data. Writes out/b01_masses.json. Read-only; no DFT run.

Systems and raw sources (paths relative to qe_workflow/):
  bulk In2O3 (PAW-PBE, a = 10.306 A): bulk_In2O3_protocol/bands_gamma.out (Gamma + 10 points along [100], [110], [111],
      |k| <= 0.153 1/A), bands_path.out (80 k, G-H-N-G-P-H|P-N), vcrelax_ecut71_k3.out (final SCF, k3 grid, same potential)
  H-L parent In32O48 (80-atom cell, a = 10.3061 A, QE 7.3.1): analysis_2026-10-13_full/raw_cern/hl/vac/In32O48/{relax,scf}.out
      (k3 / k4 grids; used only for the valence-band DOS and as an independent check of the bulk dispersion)
  slabs (PAW-PBE, relaxed): cern_htcondor/results/{slabL1_relax_v2, slabL2_relax_v2, slab1r_final_cpu, slab2_relax_c2}/bands.out
      (Gamma + 10 points along [100] and [110]) + scf.out (3x3x1 grid); checks: slab1_relax_gpu (GPU twin), slab1_v15/v25/v35
      (unrelaxed, vacuum 15/25/35 A)
  W bulk (80 atoms, W on 8b / 24d): cern_htcondor/results/iwo_W8b, iwo_W24d: bands.out (Gamma-star, CG) + scf_k4.out
  W slabs (1 / 2 nm, W on 24d): iwo_slab1_final_cpu/scf.out, iwo_slab2_final_cpu/scf.out (3x3x1 grid only; no band run)
  HSE06 (SG15 NC, 80 Ry): nc_pbe_bulk_e80, nc_hse_bulk_e80 (q1), nc_hse_bulk_q3_f160_e80, nc_pbe_slab1_e80,
      nc_hse_slab1_f160_e80 (SCF grids only)
Band counting: pure cells VB top = nelec/2, CB bottom = nelec/2 + 1 (1-based). W cells (In 4d10 in the valence, W 5s5p):
  n_pure = (nelec - 1)/2, VB top = n_pure - 1, host CB bottom = n_pure (characters checked with projwfc in ../f09, ../f10).
"""
import math

import numpy as np

import bm
from bm import q, r

R = q.RES
DIRS3 = {'[100]': (1, 0, 0), '[110]': (1, 1, 0), '[111]': (1, 1, 1)}
DIRS2 = {'[100]': (1, 0, 0), '[110]': (1, 1, 0)}


def volume_A3(p):
    m, i = q.last(p, r'unit-cell volume\s*=\s*([\d.]+) \(a\.u\.\)\^3')
    return float(m.group(1)) * q.BOHR ** 3, q.src(p, i)


def symops(p):
    try:
        n, s = q.symops(p)
        return n, s
    except LookupError:
        return None, None


def hole_verdict(fits_top, sep_meV, vbm_at_gamma_meV):
    """A hole mass is called meaningful only if (a) the global VBM of all available k lies at Gamma (within 1 meV),
    (b) the next band is >= kT below at Gamma, (c) the anchored masses of the 2-, 3- and 4-point windows agree within
    +-20 % in every direction, (d) the band falls monotonically in the 4-point window, (e) the print-precision (0.1 meV)
    rounding error of the 3-point anchored mass is < 10 %."""
    fails = []
    if vbm_at_gamma_meV is not None and vbm_at_gamma_meV > 1.0:
        fails.append(f'global VBM {vbm_at_gamma_meV:.1f} meV above VB(Gamma) (off the fit point)')
    if sep_meV is not None and sep_meV < bm.KT * 1000:
        fails.append(f'next band only {sep_meV:.1f} meV below at Gamma (< kT)')
    for d, f in fits_top.items():
        ms = [f['windows'][n]['m_anchored'] for n in ('2', '3', '4') if n in f['windows']]
        if any(m is None or m <= 0 for m in ms):
            fails.append(f'{d}: band rises away from Gamma in the 2-4 point window (camel back)')
            continue
        mean = sum(ms) / len(ms)
        if max(abs(m / mean - 1) for m in ms) > 0.2:
            fails.append(f'{d}: 2/3/4-point masses {ms} differ by > 20 %')
        dE = f['dE_meV'][1:5]
        if any(dE[j + 1] < dE[j] for j in range(len(dE) - 1)):
            fails.append(f'{d}: not monotonic in the 4-point window')
        w3 = f['windows'].get('3', {})
        if w3.get('m_anchored') and w3.get('sigma_round') is not None and w3['sigma_round'] / abs(w3['m_anchored']) > 0.10:
            fails.append(f'{d}: 3-point mass {w3["m_anchored"]} has a print-rounding error {w3["sigma_round"]} (> 10 %)')
    return {'meaningful': not fails, 'reasons': fails}


def line_fits(b, band, dirs, carrier):
    out = {}
    for d, v in dirs.items():
        idx = bm.line_indices(b['K'], v)
        k = np.linalg.norm(b['K'][idx], axis=1)
        e = b['E'][idx, band]
        f = bm.fit_line(k, e, carrier)
        f['src'] = f"{b['src'][idx[0]]} .. {b['src'][idx[-1]]}"
        f['recommended'] = bm.recommended(f)
        if carrier == 'h':
            f['offgamma_max'] = bm.offgamma_max(k, e)
        out[d] = f
    return out


def tensor2d(mx, m110):
    """In-plane mass tensor with principal axes x, y (D2h / C2v slab point groups): 1/m_110 = (1/m_x + 1/m_y)/2."""
    inv_y = 2.0 / m110 - 1.0 / mx
    if inv_y <= 0:
        return None
    my = 1.0 / inv_y
    return {'m_x': r(mx, 4), 'm_y': r(my, 4), 'm_dos_2d': r(math.sqrt(mx * my), 4), 'm_cond_2d': r(2 / (1 / mx + 1 / my), 4),
            'anisotropy_my_over_mx': r(my / mx, 4)}


def kane3pt(p, band, sel=None):
    """Kane fit H2M k^2 = m dE + m alpha dE^2 to the CB of an SCF grid (all non-Gamma points), Gamma first."""
    b = bm.read_bands(p)
    k = np.linalg.norm(b['K'], axis=1)
    assert k[0] < 1e-9, 'first k of the grid must be Gamma'
    dE = b['E'][:, band] - b['E'][0, band]
    i = np.arange(1, len(k)) if sel is None else np.array(sel)
    A = np.vstack([dE[i], dE[i] ** 2]).T
    (m, ma), *_ = np.linalg.lstsq(A, bm.H2M * k[i] ** 2, rcond=None)
    return {'m': r(m, 4), 'alpha_per_eV': r(ma / m, 3), 'k_invA': [r(x, 4) for x in k[i]], 'dE_eV': [r(x, 4) for x in dE[i]],
            'src': f"{b['src'][0]} .. {b['src'][-1]}", 'parabolic_single_point_m': [r(bm.H2M * k[j] ** 2 / dE[j], 4) for j in i]}


def nv_grid(p, vb_top, Ev=None, Ev_note=None):
    """Boltzmann valence-band DOS from an SCF grid; Ev = given reference or the grid maximum."""
    b = bm.read_bands(p)
    w = q.kweights(p)
    assert len(w) == b['nk'] and abs(w.sum() - 2) < 1e-4
    V, sV = volume_A3(p)
    E = b['E'][:, :vb_top]
    gmax = float(E.max())
    ref = gmax if Ev is None else Ev
    nv = bm.boltzmann_nv(E, w, ref, V)
    return {'Nv_cm3': float(f'{nv:.4g}'), 'Ev_ref_eV': r(ref, 4), 'grid_VB_max_eV': r(gmax, 4), 'Ev_note': Ev_note or 'grid maximum',
            'n_k': b['nk'], 'volume_A3': r(V, 3), 'src': f"{b['src'][0]} .. {b['src'][-1]}; {sV}",
            'm_dos_equiv': r(bm.mass_from_nc(nv), 3)}


def nv2d_grid(p_scf, vb_top, Ev, area_A2, t_nm):
    b = bm.read_bands(p_scf)
    w = q.kweights(p_scf)
    E = b['E'][:, :vb_top]
    s = float(np.sum(w[:, None] * np.exp(-np.clip(Ev - E, 0, None) / bm.KT) * (E <= Ev + 1e-6)))
    n2 = s / (area_A2 * 1e-16)
    return {'Nv2D_cm2': float(f'{n2:.4g}'), 'Nv_quasi3D_cm3': float(f'{n2 / (t_nm * 1e-7):.4g}'), 'Ev_ref_eV': r(Ev, 4),
            'n_k': b['nk'], 'src': f"{b['src'][0]} .. {b['src'][-1]}", 'm_dos_equiv_2d': r(n2 / bm.n2d(1.0), 3)}


# ====================================================================== bulk In2O3
def bulk():
    pg = q.BULK / 'bands_gamma.out'
    pp = q.BULK / 'bands_path.out'
    bg, bp = bm.read_bands(pg), bm.read_bands(pp)
    no = int(bg['nelec'] / 2)                     # 176
    cb, vb = no, no - 1                           # 0-based
    out = {'n_occ': no, 'src_gamma': bg['path'], 'src_path': bp['path'], 'alat_A_printed': r(bg['alat_A'], 5),
           'note_alat': 'alat = initial vc-relax |a1| (16.5570 bohr); the cell is the relaxed one (a = 10.306 A)'}
    # --- edges
    ivbm = int(np.argmax(bp['E'][:, vb]))
    out['VBM_eV'] = q.V(r(bp['E'][ivbm, vb]), bp['src'][ivbm])
    out['VBM_k_invA'] = r(np.linalg.norm(bp['K'][ivbm]), 4)
    out['VBM_k_over_GH'] = r(np.linalg.norm(bp['K'][ivbm]) / (2 * np.pi / 10.30609), 4)
    out['CBM_eV'] = q.V(r(bp['E'][:, cb].min()), bp['src'][int(np.argmin(bp['E'][:, cb]))])
    out['VB_Gamma_eV'] = r(bp['E'][0, vb])
    out['Eg_fundamental_eV'] = r(bp['E'][:, cb].min() - bp['E'][ivbm, vb])
    out['Eg_direct_Gamma_eV'] = r(bp['E'][0, cb] - bp['E'][0, vb])
    out['VBM_minus_VBGamma_meV'] = r((bp['E'][ivbm, vb] - bp['E'][0, vb]) * 1000, 2)
    out['top_VB_width_along_path_meV'] = r((bp['E'][:, vb].max() - bp['E'][:, vb].min()) * 1000, 1)
    out['VB_Gamma_degeneracy'] = int(np.sum(np.abs(bg['E'][0, :no] - bg['E'][0, vb]) < 2e-4))
    out['CB_Gamma_degeneracy'] = int(np.sum(np.abs(bg['E'][0, no:] - bg['E'][0, cb]) < 2e-4))
    out['next_VB_below_triplet_meV'] = r((bg['E'][0, vb] - bg['E'][0, vb - out['VB_Gamma_degeneracy']]) * 1000, 1)
    out['CB2_minus_CB1_Gamma_eV'] = r(bg['E'][0, cb + 1] - bg['E'][0, cb])
    # --- electrons
    el = line_fits(bg, cb, DIRS3, 'e')
    out['electron'] = el
    me = [el[d]['recommended']['m'] for d in DIRS3]
    al = [el[d]['kane']['10']['alpha_per_eV'] for d in DIRS3]
    out['electron_summary'] = {
        'm_edge_by_dir': dict(zip(DIRS3, me)), 'm_dos': r(np.prod(me) ** (1 / 3), 4), 'm_cond': r(3 / sum(1 / m for m in me), 4),
        'isotropy_spread_pct': r((max(me) - min(me)) / np.mean(me) * 100, 2),
        'alpha_by_dir': dict(zip(DIRS3, al)), 'alpha_mean_per_eV': r(np.mean(al), 3),
        'm_parabolic_4pt_intercept_by_dir': {d: el[d]['windows']['3']['m_intercept'] for d in DIRS3},
        'note': 'cubic symmetry makes the band-edge mass tensor isotropic; the direction spread is k^4 warping inside the window'}
    # check against the coarser path (G-H, first point 0.0406 1/A) and the independent H-L cell (k4, 0.1524 1/A)
    i1 = bm.line_indices(bp['K'], (0, 0, 1))[1]
    k1 = float(np.linalg.norm(bp['K'][i1]))
    m0e, a0 = out['electron_summary']['m_edge_by_dir']['[100]'], el['[100]']['kane']['10']['alpha_per_eV']
    pred = (-1 + math.sqrt(1 + 4 * a0 * bm.H2M * k1 ** 2 / m0e)) / (2 * a0)
    out['check_path_GH_first_point'] = {'k_invA': r(k1, 4), 'dE_path_meV': r((bp['E'][i1, cb] - bp['E'][0, cb]) * 1000, 2),
                                        'dE_kane_pred_meV': r(pred * 1000, 2), 'src': bp['src'][i1]}
    # --- holes: the three VB bands degenerate at Gamma
    holes = {}
    for n in range(vb - 2, vb + 1):
        holes[str(n + 1)] = line_fits(bg, n, DIRS3, 'h')
    out['hole'] = holes
    sep = (bg['E'][0, vb] - bg['E'][0, vb - out['VB_Gamma_degeneracy']]) * 1000
    out['hole_verdict'] = hole_verdict(holes[str(vb + 1)], None, out['VBM_minus_VBGamma_meV'])
    out['hole_verdict']['reasons'].insert(0, f'top VB {out["VB_Gamma_degeneracy"]}-fold degenerate at Gamma')
    out['hole_verdict']['meaningful'] = False
    out['hole_summary'] = {
        'anchored_4pt_by_band_dir': {bn: {d: f['windows']['4']['m_anchored'] for d, f in hb.items()} for bn, hb in holes.items()},
        'VBM_longitudinal_[100]': holes[str(vb + 1)]['[100]'].get('offgamma_max'),
        'next_band_below_triplet_meV': r(sep, 1)}
    # --- independent check: H-L parent In32O48 (80-atom cell, QE 7.3.1 GPU) at |k| = 0.1524 1/A along [100]
    phl = q.HERE / 'raw_cern' / 'hl' / 'vac' / 'In32O48' / 'scf.out'
    bh = bm.read_bands(phl)
    nh = int(bh['nelec'] / 2)
    kn = np.linalg.norm(bh['K'], axis=1)
    j = [0, int(np.argmin(np.where(kn > 1e-9, kn, np.inf)))]
    if len(j) > 1:
        out['check_HL_cell'] = {'k_invA': r(np.linalg.norm(bh['K'][j[1]]), 4), 'k_dir': np.round(bh['K'][j[1]] / kn[j[1]], 3).tolist(),
                                'dE_CB_meV': r((bh['E'][j[1], nh] - bh['E'][0, nh]) * 1000, 1),
                                'dE_VB_meV': r((bh['E'][j[1], nh - 1] - bh['E'][0, nh - 1]) * 1000, 1),
                                'src': bh['src'][j[1]],
                                'compare_bands_gamma_[100]_last': {'k_invA': el['[100]']['k_invA'][-1], 'dE_CB_meV': el['[100]']['dE_meV'][-1],
                                                                   'dE_VB_meV': r(-holes[str(vb + 1)]['[100]']['dE_meV'][-1], 2)}}
    # --- valence-band DOS (Boltzmann, 300 K) from uniform grids
    pv = q.BULK / 'vcrelax_ecut71_k3.out'
    # convention A (used for the grid comparison): every grid referenced to its own maximum
    out['Nv'] = {
        'prim_k3_vcrelax': nv_grid(pv, no, None),
        'conv80_k3_HL': nv_grid(q.HERE / 'raw_cern/hl/vac/In32O48/relax.out', nh, None),
        'conv80_k4_HL': nv_grid(phl, nh, None),
        'prim_k4_explattice': nv_grid(q.BULK / 'scf_ecut71_k4.out', no, None)}
    # convention B (sensitivity): referenced to the off-Gamma VBM (true VBM of bands_path, or VB(Gamma) + its 4.4 meV offset)
    out['Nv_ref_offGamma_VBM'] = {'prim_k3_vcrelax': nv_grid(pv, no, Ev=bp['E'][ivbm, vb], Ev_note='true VBM from bands_path (same SCF potential)')}
    for key in ('conv80_k3_HL', 'conv80_k4_HL'):
        b_ = bm.read_bands(q.HERE / 'raw_cern/hl/vac/In32O48' / ('relax.out' if 'k3' in key else 'scf.out'))
        g = b_['E'][0, nh - 1] + out['VBM_minus_VBGamma_meV'] / 1000
        out['Nv_ref_offGamma_VBM'][key] = nv_grid(q.HERE / 'raw_cern/hl/vac/In32O48' / ('relax.out' if 'k3' in key else 'scf.out'), nh, Ev=g,
                                                  Ev_note='VB(Gamma) + VBM offset of bands_path')
    vals = [v['Nv_cm3'] for v in out['Nv'].values()]
    out['Nv_note'] = (f'COMPUTED Boltzmann sums on coarse grids: {min(vals):.3g}-{max(vals):.3g} cm^-3 across the four grids (own-maximum reference), '
                      f'80-atom k3 -> k4 {100 * (out["Nv"]["conv80_k4_HL"]["Nv_cm3"] / out["Nv"]["conv80_k3_HL"]["Nv_cm3"] - 1):+.0f} %; convergence error unestablished. '
                      'The DOS-equivalent mass is a temperature-dependent representation of the same sum.')
    return out


# ====================================================================== slabs
SLABS = [('0.51', 'slabL1_relax_v2'), ('0.75', 'slabL2_relax_v2'), ('1.0', 'slab1r_final_cpu'), ('2.0', 'slab2_relax_c2')]
CHECKS = [('1.0 GPU twin', 'slab1_relax_gpu'), ('1.0 unrelaxed v15', 'slab1_v15'), ('1.0 unrelaxed v25', 'slab1_v25'),
          ('1.0 unrelaxed v35', 'slab1_v35')]


def slab(job, f05=None):
    d = R / job
    b = bm.read_bands(d / 'bands.out')
    no = int(b['nelec'] / 2)
    cb, vb = no, no - 1
    cell, sym, frac, cart, s_in = q.read_struct_in(d / 'scf.in')
    a, bb = float(np.linalg.norm(cell[0])), float(np.linalg.norm(cell[1]))
    zH = cart[[i for i, s in enumerate(sym) if s == 'H'], 2]
    t_HH = float(zH.max() - zH.min()) / 10 if len(zH) else None
    ns, sns = symops(d / 'scf.out')
    out = {'job': job, 'bands_src': b['path'], 'n_occ': no, 'nk_bands': b['nk'], 'inplane_A': [r(a, 4), r(bb, 4)],
           'symops': ns, 'symops_src': sns, 't_HH_nm': r(t_HH, 4), 'version_bands': b['version']}
    el = line_fits(b, cb, DIRS2, 'e')
    out['electron'] = el
    mx, m110 = el['[100]']['recommended']['m'], el['[110]']['recommended']['m']
    out['electron_summary'] = {'m_edge_[100]': mx, 'm_edge_[110]': m110,
                               'alpha_[100]': el['[100]']['kane']['10']['alpha_per_eV'], 'alpha_[110]': el['[110]']['kane']['10']['alpha_per_eV'],
                               'm_4pt_intercept_[100]': el['[100]']['windows']['3']['m_intercept'],
                               'm_4pt_intercept_[110]': el['[110]']['windows']['3']['m_intercept'],
                               'tensor_2d': tensor2d(mx, m110),
                               'tensor_note': 'principal axes x, y assumed from the slab point group (8 ops: D2h; 4 ops: C2v); m_y inferred from m_[110]'}
    out['E21_Gamma_eV'] = q.V(r(b['E'][0, cb + 1] - b['E'][0, cb]), b['src'][0])
    out['E31_Gamma_eV'] = r(b['E'][0, cb + 2] - b['E'][0, cb])
    # global edges over bands lines + SCF grid (same SCF potential)
    s = bm.read_bands(d / 'scf.out')
    allv = np.concatenate([b['E'][:, vb], s['E'][:, vb]])
    allc = np.concatenate([b['E'][:, cb], s['E'][:, cb]])
    out['VBM_eV'], out['CBM_eV'] = r(allv.max()), r(allc.min())
    h, l, sh = q.homo_lumo(d / 'scf.out')
    out['scf_HOMO_eV'], out['scf_LUMO_eV'] = q.V(h, sh), q.V(l, sh)
    out['Eg_scf_eV'] = r(l - h)
    out['bands_minus_scf_Gamma_meV'] = {'VB': r((b['E'][0, vb] - s['E'][0, vb]) * 1000, 2), 'CB': r((b['E'][0, cb] - s['E'][0, cb]) * 1000, 2)}
    out['edge_beyond_scf_grid_meV'] = {'VB': r((allv.max() - h) * 1000, 2), 'CB': r((l - allc.min()) * 1000, 2),
                                       'note': 'bands.out (non-SCF) vs scf.out eigenvalues; <= 0.3 meV is diagonalisation noise'}
    out['VB_Gamma_eV'], out['CB_Gamma_eV'] = r(b['E'][0, vb]), r(b['E'][0, cb])
    out['Eg_fundamental_eV'] = r(allc.min() - allv.max())
    out['Eg_direct_Gamma_eV'] = r(b['E'][0, cb] - b['E'][0, vb])
    out['VBM_minus_VBGamma_meV'] = r((allv.max() - b['E'][0, vb]) * 1000, 2)
    iv = int(np.argmax(allv))
    out['VBM_location'] = 'Gamma' if allv.max() - b['E'][0, vb] < 1e-4 else (
        f"bands k {np.round(b['K'][iv], 4).tolist()} 1/A" if iv < b['nk'] else f"SCF grid k {np.round(s['K'][iv - b['nk']], 4).tolist()} 1/A")
    out['VB_sep_Gamma_meV'] = r((b['E'][0, vb] - b['E'][0, vb - 1]) * 1000, 2)
    holes = {str(n + 1): line_fits(b, n, DIRS2, 'h') for n in (vb - 2, vb - 1, vb)}
    out['hole'] = holes
    out['hole_verdict'] = hole_verdict(holes[str(vb + 1)], out['VB_sep_Gamma_meV'], out['VBM_minus_VBGamma_meV'])
    out['hole_verdict']['scope'] = ('local fit screen of the top band at Gamma under the present periodic boundary conditions; the global VBM '
                                    'is established only over the sampled k-points (bands lines + SCF grid)')
    out['hole_verdict']['next_band_boltzmann_factor_300K'] = r(math.exp(-out['VB_sep_Gamma_meV'] / 1000 / bm.KT), 3)
    out['hole_summary'] = {'anchored_by_window_[100]': {n: w['m_anchored'] for n, w in holes[str(vb + 1)]['[100]']['windows'].items()},
                           'anchored_by_window_[110]': {n: w['m_anchored'] for n, w in holes[str(vb + 1)]['[110]']['windows'].items()},
                           'kane_or_quartic_[100]': holes[str(vb + 1)]['[100]']['recommended'],
                           'kane_or_quartic_[110]': holes[str(vb + 1)]['[110]']['recommended']}
    # valence-band DOS of the slab (3x3x1 grid) and the CB 3-point Kane fit on the same grid (calibration for W / HSE)
    if t_HH:
        out['Nv'] = nv2d_grid(d / 'scf.out', no, float(allv.max()), a * bb, t_HH)
    out['cb_grid_kane'] = kane3pt(d / 'scf.out', cb)
    return out


# ====================================================================== W bulk
def wbulk(job):
    d = R / job
    b = bm.read_bands(d / 'bands.out')
    n_pure = int((b['nelec'] - 1) / 2)              # 352
    vb, cb = n_pure - 2, n_pure - 1                 # 0-based: band 351 (VB top), band 352 (host CB)
    ef, sef = q.fermi(d / 'scf_k4.out')
    out = {'job': job, 'bands_src': b['path'], 'n_pure': n_pure, 'VB_top_band': vb + 1, 'host_CB_band': cb + 1,
           'E_F_eV': q.V(ef, sef), 'EF_minus_hostCB_Gamma_eV': r(ef - b['E'][0, cb]),
           'gap_VBtop_hostCB_Gamma_eV': r(b['E'][0, cb] - b['E'][0, vb]),
           'next_band_above_hostCB_Gamma_eV': r(b['E'][0, cb + 1] - b['E'][0, cb])}
    el = line_fits(b, cb, DIRS3, 'e')
    out['electron'] = el
    me = [el[d]['recommended']['m'] for d in DIRS3]
    out['electron_summary'] = {'m_edge_by_dir': dict(zip(DIRS3, me)), 'm_dos': r(np.prod(me) ** (1 / 3), 4),
                               'alpha_by_dir': {d: el[d]['kane']['10']['alpha_per_eV'] for d in DIRS3}}
    holes = {str(vb + 1): line_fits(b, vb, DIRS3, 'h')}
    out['hole'] = holes
    sep = (b['E'][0, vb] - b['E'][0, vb - 1]) * 1000
    out['VB_sep_Gamma_meV'] = r(sep, 2)
    vmax = float(b['E'][:, vb].max())
    out['hole_verdict'] = hole_verdict(holes[str(vb + 1)], sep, (vmax - b['E'][0, vb]) * 1000)
    out['hole_summary'] = {d: f['windows']['4']['m_anchored'] for d, f in holes[str(vb + 1)].items()}
    return out


def band_filling_check(wb, f09cell, alpha, m):
    """Kane estimate of E_F - E_C for the electrons in the host CB of the 80-atom W cell, against DFT."""
    V = 7387.1755 * q.BOHR ** 3                    # 80-atom cell volume (A^3), as printed for these cells (a = 10.306 A)
    out = {}
    for label, ne in (('all 3 donated electrons', 3.0), ('3 minus W-5d projection', 3.0 - f09cell['W5d_projected_electrons'])):
        n = ne / V
        kf2 = (3 * math.pi ** 2 * n) ** (2 / 3)
        g = bm.H2M * kf2 / m
        e_par = g
        e_kane = (-1 + math.sqrt(1 + 4 * alpha * g)) / (2 * alpha)
        out[label] = {'n_cm3': float(f'{n * 1e24:.3e}'), 'EF_minus_EC_parabolic_eV': r(e_par, 3), 'EF_minus_EC_kane_eV': r(e_kane, 3)}
    out['DFT_EF_minus_hostCB_Gamma_eV'] = wb['EF_minus_hostCB_Gamma_eV']
    out['mass_alpha_used'] = {'m': m, 'alpha': alpha, 'source': 'pure bulk Gamma-star Kane fit'}
    return out


# ====================================================================== W slabs and HSE (SCF grids only)
def grid_compare(p_ref, band_ref, p_x, band_x, m_edge_ref, label_ref, label_x):
    """CB dispersion on the same SCF grid: ratio of dE(k) and a calibrated Kane estimate of the band-edge mass of x:
    m_x ~ m_edge_ref * m3pt(x) / m3pt(ref) (calibration ASSUMED transferable)."""
    a = kane3pt(p_ref, band_ref)
    b = kane3pt(p_x, band_x)
    ratio = [r(x / y, 4) for x, y in zip(a['dE_eV'], b['dE_eV'])]
    est = m_edge_ref * b['m'] / a['m'] if a['m'] and b['m'] else None
    # alternative 1: Kane with the reference's alpha at the smallest |k| (same alpha for both)
    j = int(np.argmin(a['k_invA']))
    k1 = a['k_invA'][j]
    m1 = [bm.H2M * k1 ** 2 / (z['dE_eV'][j] * (1 + a['alpha_per_eV'] * z['dE_eV'][j])) for z in (a, b)]
    est_fixed = m_edge_ref * m1[1] / m1[0]
    # alternative 2: parabolic ratio at the smallest |k|
    est_par = m_edge_ref * a['dE_eV'][j] / b['dE_eV'][j]
    ests = [est, est_fixed, est_par]
    return {label_ref: a, label_x: b, 'dE_ref_over_dE_x': ratio, 'm_edge_ref': m_edge_ref,
            'm_edge_estimate_x': r(est, 4), 'calibration_factor': r(m_edge_ref / a['m'], 4),
            'estimate_alpha_fixed_lowest_k': r(est_fixed, 4), 'estimate_parabolic_ratio_lowest_k': r(est_par, 4),
            'estimate_range': [r(min(ests), 4), r(max(ests), 4)], 'lowest_k_invA': k1,
            'label': 'ESTIMATED: COMPUTED SCF-grid dispersion; Kane form, calibration on the reference and transferability ASSUMED; '
                     'not a band-edge fit (three variants: free-alpha 3-point Kane, reference alpha at the lowest k, parabolic ratio at the lowest k)'}


def main():
    out = {'kT_meV': r(bm.KT * 1000, 3), 'windows_points': list(bm.WINDOWS)}
    print('bulk ...')
    out['bulk'] = bulk()
    f05 = bm.load_parent('f05_slab_series')
    out['slabs'] = {}
    for lab, job in SLABS + CHECKS:
        print('slab', lab)
        out['slabs'][lab] = slab(job)
    # thickness comparison with the f05 4-point intercept values (same raw files, independent code)
    out['check_vs_f05'] = {lab: {'b01_4pt_[100]': out['slabs'][lab]['electron_summary']['m_4pt_intercept_[100]'],
                                 'f05_4pt_[100]': f05['slabs'][lab]['mass']['[100]']['m_intercept_m0']} for lab, _ in SLABS}
    print('W bulk ...')
    f09 = bm.load_parent('f09_iwo_bulk')
    out['W_bulk'] = {}
    mb, ab = out['bulk']['electron_summary']['m_edge_by_dir']['[100]'], out['bulk']['electron_summary']['alpha_mean_per_eV']
    for site, job in (('8b', 'iwo_W8b'), ('24d', 'iwo_W24d')):
        wb = wbulk(job)
        wb['band_filling_check'] = band_filling_check(wb, f09[site]['filling'], ab, mb)
        out['W_bulk'][site] = wb
    print('W slabs ...')
    out['W_slabs'] = {}
    for lab, job, pure in (('1 nm', 'iwo_slab1_final_cpu', 'slab1r_final_cpu'), ('2 nm', 'iwo_slab2_final_cpu', 'slab2_relax_c2')):
        bw = bm.read_bands(R / job / 'scf.out')
        n_pure = int((bw['nelec'] - 1) / 2)
        m_ref = out['slabs'][lab.split()[0] + '.0' if lab.startswith('1') else '2.0']['electron_summary']['tensor_2d']['m_dos_2d']
        g = grid_compare(R / pure / 'scf.out', n_pure, R / job / 'scf.out', n_pure - 1, m_ref, 'pure', 'W')
        g['note'] = (f'host CB band {n_pure} of the W slab vs CB band {n_pure + 1} of the pure twin, same 3x3x1 grid; '
                     f'reference mass = pure 2-D DOS band-edge mass (b01 slabs); the W-slab host CB is filled to E_F (self-consistent filling changes the dispersion)')
        out['W_slabs'][lab] = g
    print('HSE ...')
    pb = out['bulk']['electron_summary']['m_dos']
    out['HSE'] = {
        'bulk_PAW_vs_NC_PBE': grid_compare(q.BULK / 'vcrelax_ecut71_k3.out', 176, R / 'nc_pbe_bulk_e80' / 'scf.out', 176, pb, 'PAW_PBE', 'NC_PBE'),
        'bulk_q1': grid_compare(q.BULK / 'vcrelax_ecut71_k3.out', 176, R / 'nc_hse_bulk_e80' / 'scf.out', 176, pb, 'PAW_PBE', 'HSE06_q1'),
        'bulk_q3': grid_compare(q.BULK / 'vcrelax_ecut71_k3.out', 176, R / 'nc_hse_bulk_q3_f160_e80' / 'scf.out', 176, pb, 'PAW_PBE', 'HSE06_q3'),
        'bulk_NCPBE_vs_q1': grid_compare(R / 'nc_pbe_bulk_e80' / 'scf.out', 176, R / 'nc_hse_bulk_e80' / 'scf.out', 176, pb, 'NC_PBE', 'HSE06_q1'),
    }
    ms1 = out['slabs']['1.0']['electron_summary']['tensor_2d']['m_dos_2d']
    out['HSE']['slab1_NCPBE_vs_HSE'] = grid_compare(R / 'nc_pbe_slab1_e80' / 'scf.out', 312, R / 'nc_hse_slab1_f160_e80' / 'scf.out', 312, ms1,
                                                    'NC_PBE', 'HSE06_f160')
    out['HSE']['slab1_PAW_vs_NC_PBE'] = grid_compare(R / 'slab1r_final_cpu' / 'scf.out', 312, R / 'nc_pbe_slab1_e80' / 'scf.out', 312, ms1,
                                                     'PAW_PBE', 'NC_PBE')
    # HSE valence-band DOS (same k3 grid, each run referenced to its own grid maximum) vs NC-PBE
    out['HSE']['Nv_k3_grid_own_max'] = {lab: nv_grid(R / job / 'scf.out', 176, None) for lab, job in
                                       (('NC_PBE', 'nc_pbe_bulk_e80'), ('HSE06_q1', 'nc_hse_bulk_e80'), ('HSE06_q3', 'nc_hse_bulk_q3_f160_e80'))}
    out['HSE']['Nv_k3_grid_own_max']['PAW_PBE'] = nv_grid(q.BULK / 'vcrelax_ecut71_k3.out', 176, None)
    bm.dump('b01_masses', out)
    # console summary
    bs = out['bulk']['electron_summary']
    print('bulk m_e by dir', bs['m_edge_by_dir'], 'alpha', bs['alpha_by_dir'], 'dos', bs['m_dos'])
    for lab in out['slabs']:
        s = out['slabs'][lab]
        print(lab, s['electron_summary']['tensor_2d'], 'alpha', s['electron_summary']['alpha_[100]'], 'E21', s['E21_Gamma_eV']['value'],
              'hole ok', s['hole_verdict']['meaningful'], s['hole_summary']['anchored_by_window_[100]'])
    for site in out['W_bulk']:
        print('W', site, out['W_bulk'][site]['electron_summary']['m_edge_by_dir'], out['W_bulk'][site]['band_filling_check'])
    for lab in out['W_slabs']:
        print('Wslab', lab, out['W_slabs'][lab]['m_edge_estimate_x'], out['W_slabs'][lab]['estimate_range'], out['W_slabs'][lab]['dE_ref_over_dE_x'])
    for k_, v in out['HSE'].items():
        if 'm_edge_estimate_x' in v:
            print('HSE', k_, v['m_edge_estimate_x'], v['estimate_range'], v['dE_ref_over_dE_x'])


if __name__ == '__main__':
    main()
