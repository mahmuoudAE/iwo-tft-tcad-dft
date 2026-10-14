"""Writes BANDS_MASSES.md from out/b01_masses.json, out/b03_gaps_laws.json and out/b04_tcad.json.
Every number in the tables is read from these JSON files (which carry the raw file:line sources); the literature values
are typed in below with their citation and were checked against the publisher / Crossref / arXiv records on 2026-10-14.
"""
import json
import math

import bm

D1 = json.loads((bm.OUT / 'b01_masses.json').read_text())
D3 = json.loads((bm.OUT / 'b03_gaps_laws.json').read_text())
D4 = json.loads((bm.OUT / 'b04_tcad.json').read_text())
LAB = ('0.51', '0.75', '1.0', '2.0')


def f(x, n=4):
    if x is None:
        return '-'
    if isinstance(x, (list, tuple)):
        if len(x) == 2 and all(isinstance(v, (int, float)) for v in x):
            x = sorted(x)                      # two-element lists are ranges: print low-high
        return '-'.join(f(v, n) for v in x) if len(x) == 2 else ', '.join(f(v, n) for v in x)
    if isinstance(x, float) and (abs(x) >= 1e5 or (0 < abs(x) < 1e-3)):
        return f'{x:.3g}'
    if isinstance(x, float):
        return f'{x:.{n}f}'.rstrip('0').rstrip('.') if n > 0 else f'{x:.0f}'
    return str(x)


def opt_mass(m, a, n_cm3):
    """Kane band: E_F from n (single valley, spin 2), optical (plasma) mass m(1 + 2 alpha E_F)."""
    kf2 = (3 * math.pi ** 2 * n_cm3 * 1e-24) ** (2 / 3)
    g = bm.H2M * kf2 / m
    e = (-1 + math.sqrt(1 + 4 * a * g)) / (2 * a)
    return e, m * (1 + 2 * a * e)


def main():
    b = D1['bulk']
    bs = b['electron_summary']
    L = []
    w = L.append
    w('# Band structures, effective masses, gaps vs thickness and TCAD-ready parameters (crystalline DFT only)')
    w('')
    w('Analysis of 2026-10-14, read-only, re-derived from the raw Quantum ESPRESSO outputs by the scripts in this folder '
      '(`b01_masses.py`, `b02_band_figures.py`, `b03_gaps_laws.py`, `b04_tcad.py`, `b05_holes.py`, `make_bm_report.py`; `bash run_all.sh`). '
      'Machine-readable results: `out/b01_masses.json`, `out/b03_gaps_laws.json`, `out/b04_tcad.json` (each value carries its raw '
      'file:line source; holes: `out/b05_holes.json`). Figures: `figures/BM1`-`BM9` (PNG 300 dpi + PDF). Hole masses: Section 8. Paths below are relative to `qe_workflow/`.')
    w('')
    w('Scope and sight rule: crystalline cells only (bulk In2O3, H-terminated (001) slabs 0.51 / 0.75 / 1 / 2 nm, W-doped bulk 8b / 24d, '
      'W24d slabs 1 / 2 nm, HSE06 bulk / 1 nm, the H-L parent In32O48 cell as a dispersion and DOS check). No amorphous output was opened. '
      'No DFT was run, nothing was submitted, nothing was committed.')
    w('')
    w('Labels: COMPUTED (a DFT number), FITTED (a law through COMPUTED points), ESTIMATED (COMPUTED data plus a stated model), '
      'CALCULATED (formula applied to COMPUTED or LITERATURE inputs), ASSUMED, LITERATURE, INFERRED. All DFT numbers are PBE (PAW, '
      'pslibrary 1.0.0, 71/568 Ry) unless marked HSE06 (SG15 NC, 80 Ry, PBE geometries). kT = 25.85 meV (300 K).')
    w('')
    # ------------------------------------------------------------------ 1 band structures
    w('## 1. Band structures')
    w('')
    w('| System | Band data | Figure | k-path status |')
    w('|---|---|---|---|')
    w(f"| bulk In2O3 (40-atom primitive, a = 10.306 A) | `{D1['bulk']['src_path']}` (80 k, G-H-N-G-P-H\\|P-N) + `{D1['bulk']['src_gamma']}` "
      '(Gamma + 10 points along [100], [110], [111], abs(k) <= 0.153 1/A) | BM1 | complete |')
    for lab in LAB:
        s = D1['slabs'][lab]
        w(f"| slab {lab} nm (H-H {s['t_HH_nm']} nm, `{s['job']}`) | `{s['bands_src']}` (Gamma + 10 points along [100] and [110], "
          f"abs(k) <= 0.15 1/A) + 3x3x1 SCF grid | BM2 | in-plane lines to 0.15 1/A only (half of Gamma-X); no full 2-D path |")
    for site in ('8b', '24d'):
        x = D1['W_bulk'][site]
        w(f"| W bulk {site} (80 atoms, In31WO48) | `{x['bands_src']}` (Gamma-star, CG) + scf_k4 | BM3 | Gamma-star only; no zone-boundary path |")
    w('| W slabs 1 / 2 nm (W on 24d) | SCF 3x3x1 grid only (`iwo_slab1_final_cpu/scf.out`, `iwo_slab2_final_cpu/scf.out`) | BM4a | '
      '**k-path run missing**: the 1 nm bands step stopped (rc 161: factorisation of the overlap matrix failed in cdiaghg, Davidson; cause unresolved); no 2 nm bands step |')
    w('| HSE06 bulk (q1, q3) and 1 nm slab | SCF grids only (bulk k3, 4 k; slab 3x3x1, 4 k) | BM4b,c | **k-path run missing** |')
    w('| H-L cells (In32O48, In31WO48, vacancy cells) | SCF k3 / k4 grids only | - | **no band run**; the pristine In32O48 grid is used here only as a '
      'dispersion and valence-DOS check |')
    w('')
    w(f"**BM1** (bulk). (a) Band structure along G-H-N-G-P-H|P-N, E - E_VBM. Open circle: VBM at 0.2 G-H "
      f"(abs(k) = {f(b['VBM_k_invA'])} 1/A, {b['VBM_eV']['src']}); filled circle: CBM at Gamma ({b['CBM_eV']['src']}); arrow: fundamental gap "
      f"{f(b['Eg_fundamental_eV'])} eV (direct at Gamma {f(b['Eg_direct_Gamma_eV'])} eV). Black: valence bands, red: conduction bands. "
      f"(b) CB near Gamma along the three directions with the Kane fit (black, m = {bs['m_edge_by_dir']['[100]']} m0, alpha = "
      f"{bs['alpha_by_dir']['[100]']} 1/eV) and the 3-point parabola (dashed). (c) The three VBs degenerate at Gamma: band 176 rises along "
      f"[100] to the VBM {f(b['VBM_minus_VBGamma_meV'], 1)} meV above VB(Gamma) (open circle), i.e. a camel back. COMPUTED.")
    w('')
    w('**BM2** (relaxed slabs (a) 0.51, (b) 0.75, (c) 1.0, (d) 2.0 nm). Lines: bands.out along [110] (left, plotted at -abs(k)) and [100] '
      '(right); open symbols: 3x3x1 SCF-grid eigenvalues (circles on the x / diagonal axes, squares on the y axis, plotted at their abs(k)). '
      'Open circle at Gamma: VB(Gamma); blue open circle in (a): the off-Gamma VBM of the 0.51 nm slab on the SCF grid '
      f"({f(D1['slabs']['0.51']['VBM_minus_VBGamma_meV'], 1)} meV above VB(Gamma)); filled circle: CBM; arrow: gap. E - E_VBM. COMPUTED.")
    w('')
    w('**BM3** (W bulk (a) 8b, (b) 24d). Gamma-star bands, E - E_F (dotted). Black: valence bands (top = band 351 = n_pure - 1), red: host CB '
      '(band 352 = n_pure, filled circle at Gamma), green: bands above (W-5d-rich level and folded host CB). Dashed grey: CB of pure bulk '
      'from bands_gamma.out shifted to the host-CB minimum. COMPUTED.')
    w('')
    w('**BM4** (systems with SCF-grid eigenvalues only). (a) CB dispersion E_CB(k) - E_CB(Gamma) of the W slabs (circles, host CB band '
      'n_pure) and the pure twins (crosses, band n_pure + 1) at the 3x3x1 grid points. (b) Bulk: VB top and CB relative to VB(Gamma) for '
      'PAW-PBE, NC-PBE, HSE06 q1 and q3 at the k3 grid. (c) 1 nm slab: PAW-PBE, NC-PBE, HSE06. The masses derived from these points are '
      'ESTIMATED (Section 2.6), not band-edge fits.')
    w('')
    # ------------------------------------------------------------------ 2 masses
    w('## 2. Effective masses')
    w('')
    w('Method (b01_masses.py). For one band along one line through the extremum: anchored parabola E - E0 = hbar^2 k^2/2m over the first '
      'n points (windows n = 2, 3, 4, 6, 10, i.e. abs(k) up to 0.031 / 0.046 / 0.061 / 0.092 / 0.153 1/A), the free-intercept parabola '
      '(the deck basis is the 3-point window = "4-point incl. Gamma"), a quartic fit (k^2 + k^4) over all points, and the Kane form '
      'hbar^2 k^2/2m = E(1 + alpha E) over 4, 6 and 10 points. The band-edge mass is the 10-point Kane value. The print precision of the '
      'eigenvalues (0.1 meV) is propagated into every anchored mass (sigma_round in the JSON). DOS mass (bulk) = geometric mean, '
      'conductivity mass = harmonic mean of the three directional band-edge masses. Slabs: in-plane tensor with principal axes x, y '
      '(point group D2h for 8 symmetry operations, C2v for 4), m_y from 1/m_[110] = (1/m_x + 1/m_y)/2, 2-D DOS mass sqrt(m_x m_y), '
      'conductivity mass 2/(1/m_x + 1/m_y) = m_[110].')
    w('')
    w('### 2.1 Bulk electrons (COMPUTED)')
    w('')
    w('| Direction | n=2 | n=3 | n=4 | n=6 | n=10 | free intercept n=3 | quartic | Kane m (10 pt) | Kane alpha (1/eV) |')
    w('|---|---|---|---|---|---|---|---|---|---|')
    for d in ('[100]', '[110]', '[111]'):
        e = b['electron'][d]
        ww = e['windows']
        w(f"| {d} | {f(ww['2']['m_anchored'])} | {f(ww['3']['m_anchored'])} | {f(ww['4']['m_anchored'])} | {f(ww['6']['m_anchored'])} | "
          f"{f(ww['10']['m_anchored'])} | {f(ww['3']['m_intercept'])} | {f(e['quartic_all']['m_edge'])} | {f(e['kane']['10']['m_edge'])} | "
          f"{f(e['kane']['10']['alpha_per_eV'], 3)} |")
    w('')
    w(f"Window energies: n = 2 / 3 / 4 / 6 / 10 reach E - E_CBM = {', '.join(f(b['electron']['[100]']['windows'][n]['Emax_meV'], 1) for n in ('2', '3', '4', '6', '10'))} meV "
      f"([100]). Source: `{b['electron']['[100]']['src']}`.")
    w(f"- Band-edge mass {f(bs['m_dos'])} m0 (DOS = conductivity mass; direction spread {f(bs['isotropy_spread_pct'], 2)} %, isotropic as required by cubic "
      f"symmetry). The parabolic mass grows with the window: {f(b['electron']['[100]']['windows']['2']['m_anchored'])} (25 meV) to "
      f"{f(b['electron']['[100]']['windows']['10']['m_anchored'])} m0 (450 meV); the deck basis (3-point free intercept) is {f(bs['m_parabolic_4pt_intercept_by_dir']['[100]'])} m0, "
      f"3 % above the band edge.")
    w(f"- Kane alpha {f(bs['alpha_mean_per_eV'], 3)} 1/eV (direction range {f(min(bs['alpha_by_dir'].values()), 3)}-{f(max(bs['alpha_by_dir'].values()), 3)}).")
    ck = b['check_path_GH_first_point']
    w(f"- Checks: the coarser path (G-H first point, abs(k) = {ck['k_invA']} 1/A) gives {ck['dE_path_meV']} meV against {ck['dE_kane_pred_meV']} meV "
      f"from the Kane fit ({ck['src']}); the independent H-L parent cell In32O48 (80 atoms, QE 7.3.1 GPU) gives CB {b['check_HL_cell']['dE_CB_meV']} meV "
      f"and VB +{b['check_HL_cell']['dE_VB_meV']} meV at {b['check_HL_cell']['k_invA']} 1/A along [001] ({b['check_HL_cell']['src']}) against "
      f"{b['check_HL_cell']['compare_bands_gamma_[100]_last']['dE_CB_meV']} / +{b['check_HL_cell']['compare_bands_gamma_[100]_last']['dE_VB_meV']} meV at "
      f"{b['check_HL_cell']['compare_bands_gamma_[100]_last']['k_invA']} 1/A in bands_gamma.out.")
    m, a = bs['m_dos'], bs['alpha_mean_per_eV']
    e20, mo20 = opt_mass(m, a, 1e20)
    e21, mo21 = opt_mass(m, a, 1e21)
    w(f"- Consequence of alpha (CALCULATED from the COMPUTED m and alpha): the isotropic Kane cyclotron / zero-temperature conductivity (optical) "
      f"mass m(1 + 2 alpha E_F) = {mo20:.3f} m0 at 1e20 cm^-3 "
      f"(E_F - E_C = {e20:.2f} eV) and {mo21:.3f} m0 at 1e21 cm^-3 ({e21:.2f} eV); Feneberg et al. 2016 report 0.4 m0 at 1e21 cm^-3 from the plasma frequency.")
    w('')
    w('### 2.2 Bulk holes: no meaningful single-band hole mass')
    w('')
    hs = b['hole_summary']
    w(f"- The top valence band is {b['VB_Gamma_degeneracy']}-fold degenerate at Gamma (bands 174-176); the next band lies "
      f"{b['next_VB_below_triplet_meV']} meV below. Along [100] one member rises (camel back) to the VBM at abs(k) = "
      f"{hs['VBM_longitudinal_[100]']['k0_invA']} 1/A, {hs['VBM_longitudinal_[100]']['E0_minus_Gamma_meV']} meV above VB(Gamma) "
      f"(six equivalent pockets on <100>; bands_path.out gives {f(b['VBM_minus_VBGamma_meV'], 1)} meV at 0.2 G-H). The whole top band spans "
      f"{b['top_VB_width_along_path_meV']} meV along the path.")
    w(f"- Longitudinal mass at the VBM (parabola through 5 points of bands_gamma [100]): {hs['VBM_longitudinal_[100]']['m_long']} +- "
      f"{hs['VBM_longitudinal_[100]']['sigma_round']} m0 (print-precision error). The transverse masses at the VBM are not computed (no k-points off the line).")
    am = hs['anchored_4pt_by_band_dir']
    w('- Band masses at Gamma (anchored, n = 4; negative = band rises): ' + '; '.join(
        f"band {bn}: " + ', '.join(f"{d} {f(v, 2)}" for d, v in dd.items()) for bn, dd in am.items()) + ' m0.')
    w('- Verdict: ' + '; '.join(b['hole_verdict']['reasons']) + '. A single band-edge hole mass is therefore not a meaningful bulk parameter in PBE; band-resolved curvature masses and the DOS mass are given as numbers in Section 8.')
    nv = b['Nv']
    nvb = b['Nv_ref_offGamma_VBM']
    w(f"- What is meaningful is the valence-band effective density of states from a Boltzmann sum over the computed bands (COMPUTED on the stated "
      f"coarse grids, each referenced to its own grid maximum): Nv(300 K) = {f(nv['conv80_k4_HL']['Nv_cm3'])} cm^-3 (80-atom cell, k4, 14 k), "
      f"{f(nv['prim_k4_explattice']['Nv_cm3'])} (primitive k4, experimental lattice), {f(nv['conv80_k3_HL']['Nv_cm3'])} (80-atom k3), "
      f"{f(nv['prim_k3_vcrelax']['Nv_cm3'])} (primitive k3). Referenced instead to the off-Gamma VBM: {f(nvb['conv80_k4_HL']['Nv_cm3'])} (80-atom k4), "
      f"{f(nvb['conv80_k3_HL']['Nv_cm3'])} (80-atom k3), {f(nvb['prim_k3_vcrelax']['Nv_cm3'])} (primitive k3). Observed variation: {b['Nv_note'].split(': ')[1].split('; convergence')[0]}; "
      f"convergence error unestablished. DOS-equivalent hole mass about {f(nv['conv80_k4_HL']['m_dos_equiv'], 1)} m0 (a temperature-dependent "
      "representation of the same sum, not a band mass). On the same k3 grid HSE06 gives "
      f"{f(D4['bulk']['Nv_HSE_over_PBE_k3_same_grid'][0], 2)} (q1) and {f(D4['bulk']['Nv_HSE_over_PBE_k3_same_grid'][1], 2)} (q3) times the NC-PBE Nv.")
    w('')
    w('### 2.3 Slab electrons (COMPUTED)')
    w('')
    w('| Slab | t_HH (nm) | Kane m_[100] | Kane m_[110] | alpha_[100] / alpha_[110] (1/eV) | m_x / m_y | 2-D DOS = cond. mass | deck-basis 3-pt [100] | anchored n=2 ... n=10 [100] |')
    w('|---|---|---|---|---|---|---|---|---|')
    for lab in LAB + ('1.0 GPU twin', '1.0 unrelaxed v15', '1.0 unrelaxed v25', '1.0 unrelaxed v35'):
        s = D1['slabs'][lab]
        e = s['electron_summary']
        t2 = e['tensor_2d']
        wn = s['electron']['[100]']['windows']
        w(f"| {lab} | {s['t_HH_nm']} | {f(e['m_edge_[100]'])} | {f(e['m_edge_[110]'])} | {f(e['alpha_[100]'], 3)} / {f(e['alpha_[110]'], 3)} | "
          f"{f(t2['m_x'])} / {f(t2['m_y'])} | {f(t2['m_dos_2d'])} | {f(e['m_4pt_intercept_[100]'])} | "
          f"{f(wn['2']['m_anchored'])} ... {f(wn['10']['m_anchored'])} |")
    w('')
    w('Sources: the bands.out of each job (lines in out/b01_masses.json, field `src`). Checks: GPU (QE 7.3.1) and CPU (QE 7.5) runs of the same 1 nm '
      'geometry agree within 0.0006 m0; the unrelaxed 1 nm slab is converged in vacuum (15 / 25 / 35 A: identical to 0.0002 m0); relaxation raises the '
      '1 nm mass from 0.2376 to 0.2793 m0 (+18 %). The 4-point values reproduce ../out/f05 (check_vs_f05 in the JSON). The 0.51 nm cell is '
      'rectangular (10.70 x 10.02 A): m_y/m_x = ' + f(D1['slabs']['0.51']['electron_summary']['tensor_2d']['anisotropy_my_over_mx'], 3) +
      '; all other slabs are isotropic in-plane within 2 %.')
    w('')
    w('### 2.4 Slab holes')
    w('')
    w('| Slab | VBM location | next VB at Gamma (meV) | anchored m_h [100], n = 2/3/4/6/10 | anchored m_h [110], n = 2/3/4/6/10 | passes local fit screens? | reasons | Nv2D (cm^-2) / quasi-3D (cm^-3) |')
    w('|---|---|---|---|---|---|---|---|')
    for lab in LAB:
        s = D1['slabs'][lab]
        h = s['hole_summary']
        w(f"| {lab} | {s['VBM_location']} | {s['VB_sep_Gamma_meV']} | {' / '.join(f(v, 2) for v in h['anchored_by_window_[100]'].values())} | "
          f"{' / '.join(f(v, 2) for v in h['anchored_by_window_[110]'].values())} | {'yes' if s['hole_verdict']['meaningful'] else 'no'} | "
          f"{'; '.join(s['hole_verdict']['reasons']) or '-'} | {f(s['Nv']['Nv2D_cm2'])} / {f(s['Nv']['Nv_quasi3D_cm3'])} |")
    w('')
    s75 = D1['slabs']['0.75']
    w('Local fit screens (written before the slab values were read): global VBM at Gamma within 1 meV (over the sampled k-points only); next band '
      'at least kT below; the 2-, 3- and 4-point masses within +-20 %; monotonic fall over 4 points; print-rounding error of the 3-point mass below '
      '10 % (correlated rounding of E(Gamma) included). Only the 0.75 nm slab passes, which establishes a resolved local curvature of its '
      'OH-derived top valence band (75 % on OH oxygens) under the present periodic boundary conditions: m_h = ' +
      f(s75['hole_summary']['anchored_by_window_[100]']['3'], 2) + ' m0 [100] and ' + f(s75['hole_summary']['anchored_by_window_[110]']['3'], 2) +
      f" m0 [110] (3-point). It does not establish single-band hole transport at 300 K: the next band is {s75['VB_sep_Gamma_meV']} meV lower "
      f"(Boltzmann factor {s75['hole_verdict']['next_band_boltzmann_factor_300K']} before its DOS), and the uncorrected polar field of this slab can "
      'alter its electronic structure, not only the vacuum reference. At 0.51 nm the Gamma masses are resolved (1.14 [100], 2.0 [110] m0) but '
      'a second maximum on the SCF grid lies 1.3 meV higher (multi-valley). At 1 and 2 nm the top two bands are within 3.3 and 9.3 meV: '
      'degenerate on the kT scale. Nv from a 3x3x1 grid (4 k) is COMPUTED on that grid; its convergence error is unestablished.')
    w('')
    w('### 2.5 Effect of W (COMPUTED in bulk; ESTIMATED in slabs)')
    w('')
    w('| Cell | host-CB band | m (Kane, [100] / [110] / [111]) | alpha (1/eV) | E_F - E_C(Gamma) (eV) | VB top to host CB at Gamma (eV) | hole mass |')
    w('|---|---|---|---|---|---|---|')
    for site in ('8b', '24d'):
        x = D1['W_bulk'][site]
        es = x['electron_summary']
        w(f"| bulk {site} | {x['host_CB_band']} | {' / '.join(f(v) for v in es['m_edge_by_dir'].values())} | "
          f"{' / '.join(f(v, 3) for v in es['alpha_by_dir'].values())} | {x['EF_minus_hostCB_Gamma_eV']} | {x['gap_VBtop_hostCB_Gamma_eV']} | "
          f"not meaningful ({'; '.join(x['hole_verdict']['reasons'][:2])}) |")
    w(f"| pure bulk (reference) | 177 | {' / '.join(f(v) for v in bs['m_edge_by_dir'].values())} | {' / '.join(f(v, 3) for v in bs['alpha_by_dir'].values())} | - | "
      f"{b['Eg_direct_Gamma_eV']} | not meaningful |")
    w('')
    for site in ('8b', '24d'):
        bf = D1['W_bulk'][site]['band_filling_check']
        lo, hi = bf['3 minus W-5d projection']['EF_minus_EC_kane_eV'], bf['all 3 donated electrons']['EF_minus_EC_kane_eV']
        dft = bf['DFT_EF_minus_hostCB_Gamma_eV']
        w(f"- Band-filling check ({site}, CALCULATED): with the pure-bulk Kane m and alpha, n = {f(bf['3 minus W-5d projection']['n_cm3'])} - "
          f"{f(bf['all 3 donated electrons']['n_cm3'])} cm^-3 in the host CB gives E_F - E_C = {lo}-{hi} eV (parabolic: "
          f"{bf['3 minus W-5d projection']['EF_minus_EC_parabolic_eV']}-{bf['all 3 donated electrons']['EF_minus_EC_parabolic_eV']} eV) against DFT "
          f"{dft} eV: the Kane form removes most of the parabolic error but still overestimates E_F by {100 * (lo / dft - 1):.0f}-{100 * (hi / dft - 1):.0f} %.")
    for lab in ('1 nm', '2 nm'):
        g = D1['W_slabs'][lab]
        w(f"- W slab {lab} (ESTIMATED from the 3x3x1 grid, Section 2.6 method): host-CB band-edge mass {f(g['m_edge_estimate_x'])} m0 (variants "
          f"{f(g['estimate_range'])}) against the pure twin {f(g['m_edge_ref'])} m0; the pure/W dispersion ratio at the grid points is "
          f"{', '.join(f(v, 3) for v in g['dE_ref_over_dE_x'])}.")
    w('- Reading: W at 3.1 % (bulk) raises the host-CB band-edge mass by about 5 % (0.154 -> 0.161-0.163 m0) and leaves alpha unchanged within '
      'the direction spread; in the slabs the grid estimate gives +6.5 % (1 nm) and +7.5 % (2 nm). These cells hold 1.4e21-3e21 cm^-3 donated '
      'electrons with E_F 1.2-1.8 eV inside the CB, so the curvature includes the self-consistent response to that filling. The W-slab '
      'masses are not band-edge fits (k-path run missing).')
    w('')
    w('### 2.6 HSE06 (ESTIMATED from SCF grids)')
    w('')
    w('Method: a 3-point Kane fit (m, alpha) to the CB at the non-Gamma grid points, calibrated by the same fit on the PAW-PBE grid of the same '
      'cell (whose band-edge mass is known from the band runs): m_HSE ~ m_PBE,edge x m3pt(HSE)/m3pt(PBE). Two variants bracket the model '
      'dependence: alpha fixed to the PBE value at the smallest abs(k), and the plain parabolic ratio at the smallest abs(k).')
    w('')
    w('| Comparison | grid points abs(k) (1/A) | dE_ref/dE_x at the grid points | m estimate (free alpha) | range of variants | calibration factor |')
    w('|---|---|---|---|---|---|')
    for k in ('bulk_PAW_vs_NC_PBE', 'bulk_q1', 'bulk_q3', 'slab1_PAW_vs_NC_PBE', 'slab1_NCPBE_vs_HSE'):
        g = D1['HSE'][k]
        lbl = [x for x in g if isinstance(g[x], dict) and 'k_invA' in g[x]]
        w(f"| {k} ({lbl[0]} -> {lbl[1]}) | {', '.join(f(v, 3) for v in g[lbl[0]]['k_invA'])} | {', '.join(f(v, 3) for v in g['dE_ref_over_dE_x'])} | "
          f"{f(g['m_edge_estimate_x'])} | {f(g['estimate_range'])} | {f(g['calibration_factor'])} |")
    w('')
    w(f"- Validation: on the PAW-PBE k3 grid the same 3-point fit gives {D1['HSE']['bulk_q1']['PAW_PBE']['m']} m0 and alpha "
      f"{D1['HSE']['bulk_q1']['PAW_PBE']['alpha_per_eV']} 1/eV against the band-edge {bs['m_dos']} m0 and {bs['alpha_mean_per_eV']} 1/eV from the band runs "
      f"(calibration factor {D1['HSE']['bulk_q1']['calibration_factor']}). NC-PBE and PAW-PBE dispersions agree within 0.6 %.")
    hb = [D1['HSE']['bulk_q3']['estimate_range'][0], D1['HSE']['bulk_q1']['estimate_range'][1]]
    hs1 = D1['HSE']['slab1_NCPBE_vs_HSE']['estimate_range']
    pb1 = D1['slabs']['1.0']['electron_summary']['tensor_2d']['m_dos_2d']
    w(f"- Reading: the calibrated estimates suggest that HSE06 increases the bulk band-edge mass from {bs['m_dos']} to {hb[0]}-{hb[1]} m0 "
      f"(the variant range is a model sensitivity, not an uncertainty bound; three coarse-grid energies do not establish the k -> 0 curvature; the free-alpha fit gives "
      f"{D1['HSE']['bulk_q3']['m_edge_estimate_x']}-{D1['HSE']['bulk_q1']['m_edge_estimate_x']} m0 with alpha "
      f"{D1['HSE']['bulk_q3']['HSE06_q3']['alpha_per_eV']}-{D1['HSE']['bulk_q1']['HSE06_q1']['alpha_per_eV']} 1/eV) and the 1 nm slab mass from {pb1} to "
      f"{hs1[0]}-{hs1[1]} m0. The HSE confinement increment dm(1 nm) = {hs1[0] - hb[1]:.3f}-{hs1[1] - hb[0]:.3f} m0 brackets the PBE value "
      f"{pb1 - bs['m_dos']:.3f} m0: not resolved. ESTIMATED only: three grid points per cell at 0.2-0.5 1/A (0.45-2.5 eV above the CBM).")
    w('')
    w('### 2.7 Thickness and W trends (Figures BM5, BM6)')
    w('')
    lw = D3['laws']
    w(f"- m*_e rises from {bs['m_dos']} (bulk) to {D1['slabs']['2.0']['electron_summary']['tensor_2d']['m_dos_2d']} (2 nm), "
      f"{D1['slabs']['1.0']['electron_summary']['tensor_2d']['m_dos_2d']} (1 nm), {D1['slabs']['0.75']['electron_summary']['tensor_2d']['m_dos_2d']} (0.75 nm) "
      f"and {D1['slabs']['0.51']['electron_summary']['tensor_2d']['m_dos_2d']} m0 (0.51 nm, In8(OH)24). FITTED: dm = a t^-p with a = "
      f"{lw['dm_e_band_edge']['fit3']['a']} +- {lw['dm_e_band_edge']['fit3']['sigma_a']}, p = {lw['dm_e_band_edge']['fit3']['p']} +- "
      f"{lw['dm_e_band_edge']['fit3']['sigma_p']} (band-edge basis, fit3; relative residuals {', '.join(f(v, 4) for v in lw['dm_e_band_edge']['fit3']['rel_resid'])}); "
      f"deck basis (3-point parabola) a = {lw['dm_e_4pt_deck_basis']['fit3']['a']}, p = {lw['dm_e_4pt_deck_basis']['fit3']['p']} (V3 config: "
      f"{lw['config_V3']['dm']['a']}, {lw['config_V3']['dm']['p']}).")
    al2 = {lab: 0.5 * (D1['slabs'][lab]['electron_summary']['alpha_[100]'] + D1['slabs'][lab]['electron_summary']['alpha_[110]']) for lab in LAB}
    w('- In-plane Kane alpha ([100]/[110] mean) falls with decreasing thickness: ' + ', '.join(f"{al2[l]:.2f} ({l} nm)" for l in ('2.0', '1.0', '0.75', '0.51')) +
      f" against {bs['alpha_mean_per_eV']} 1/eV in bulk: the confined subband is more parabolic in-plane.")
    rel = {lab: D1['slabs'][lab]['electron_summary']['tensor_2d']['m_dos_2d'] / D1['slabs'][lab]['electron_summary']['m_4pt_intercept_[100]'] - 1 for lab in LAB}
    w('- Band-edge (Kane, 2-D DOS) vs 3-point parabola (deck basis): ' + ', '.join(f"{100 * rel[l]:+.1f} % ({l} nm)" for l in LAB) +
      f", {100 * (bs['m_dos'] / bs['m_parabolic_4pt_intercept_by_dir']['[100]'] - 1):+.1f} % (bulk).")
    w('- m*_h: a resolved local curvature only at 0.75 nm (5.9 [100] / 3.3 [110] m0; not a single-band transport mass, see 2.4). The DOS-equivalent '
      'hole mass from Nv is 13-32 m0 in the slabs and about 18 m0 in bulk, without a monotonic trend; no law is fitted.')
    w('- W: +5 % (bulk, COMPUTED), +6.5 / +7.5 % (1 / 2 nm slabs, ESTIMATED). HSE06: the calibrated estimates suggest +3 to +25 % in bulk and '
      '+1 to +5 % at 1 nm (ESTIMATED; model sensitivity, not an uncertainty bound).')
    w('- The quoted sigma of every fitted law is the residual scatter about that law (one residual degree of freedom for fit3); it excludes the '
      'functional, termination, thickness-definition and polar-field errors.')
    w('')
    w('**BM5**. (a) Bulk CB anchored-parabola mass vs the window end energy for [100] / [110] / [111]; horizontal line: Kane band-edge DOS mass. '
      '(b) Slab and bulk [100] window masses divided by the band-edge mass. (c) Slab hole masses (anchored) vs the window drop for [100] (solid) '
      'and [110] (dashed); filled symbols only where the hole mass passes the criteria (0.75 nm).')
    w('')
    w('**BM6**. (a) m*_e vs H-H thickness: band-edge 2-D DOS mass (filled; open = 0.51 nm, In8(OH)24, outside every law), 3-point parabola '
      '(squares), W-slab grid estimates (diamonds, bars = variant range), HSE06 1 nm estimate (triangle), Lin et al. 2022 PBE values at their '
      'labels 0.95 / 1.98 nm (crosses); dashed: bulk band-edge mass, dotted: W-bulk mean. (b) dm_e = m(t) - m_bulk with the band-edge fit3 law '
      '(solid) and the V3 config law (dashed grey, deck basis). (c) Hole DOS-equivalent mass from the Boltzmann Nv (circles; dashed: bulk), '
      'and the 0.75 nm single-band hole masses [100] (up triangle) and [110] (down triangle).')
    w('')
    # ------------------------------------------------------------------ 3 gaps
    w('## 3. Gaps, band edges, EA / IP and subbands vs thickness')
    w('')
    w('| Slab | t_HH (nm) | Eg PBE (eV) | Eg direct Gamma | dEg | dEc | dEv | CB share | EA (eV) | IP (eV) | E1 = dEc | E2 | E3 | E21 | E21/E1 | Eg HSE-corrected | Eg exp.-anchored (2.93 + r dEg) |')
    w('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for lab in LAB:
        x = D3['slabs'][lab]
        w(f"| {lab} | {x['t_HH_nm']} | {f(x['Eg_fundamental_eV'])} | {f(x['Eg_direct_Gamma_eV'])} | {f(x['dEg_eV'])} | {f(x['dEc_eV'])} | {f(x['dEv_eV'])} | "
          f"{f(x['CB_share'], 3)} | {f(x['EA_eV'])} | {f(x['IP_eV'])} | {f(x['E1_eV'])} | {f(x['E2_eV'])} | {f(x['E3_eV'])} | {f(x['E21_eV'])} | "
          f"{f(x['E21_over_E1'], 2)} | {f(x['Eg_HSE_corrected_eV'])} | {f(x['Eg_exp_anchored_eV']['King2009_fundamental'])} |")
    w('')
    bq = D3['bulk']
    w(f"Bulk: Eg = {bq['Eg_fundamental_eV']} eV (indirect by 4.4 meV; direct at Gamma {bq['Eg_direct_Gamma_eV']}), {bq['VBM_src']} / {bq['CBM_src']}. "
      f"Bulk-equivalent EA {D3['bulk_equivalent']['EA_eV']} eV, IP {D3['bulk_equivalent']['IP_eV']} eV (EA(2 nm) + dEc(2 nm), H-(001), PBE). "
      f"HSE06: bulk {D3['hse']['HSE_bulk_q1']['gap_eV']['value']} (q1, {D3['hse']['HSE_bulk_q1']['gap_eV']['src']}) / "
      f"{D3['hse']['HSE_bulk_q3_f160']['gap_eV']['value']} eV (q3, {D3['hse']['HSE_bulk_q3_f160']['gap_eV']['src']}), 1 nm slab "
      f"{D3['hse']['HSE_slab1_f160']['gap_eV']['value']} eV ({D3['hse']['HSE_slab1_f160']['gap_eV']['src']}); r = dEg(HSE)/dEg(PBE) = "
      f"{D3['hse']['r_q1']} (q1) / {D3['hse']['r_q3bulk']} (q3 bulk).")
    w('')
    w('Sources and routes: edges = HOMO/LUMO of each scf.out (bands lines and grid differ by <= 0.3 meV, field edge_beyond_scf_grid_meV); vacuum '
      'level = mean planar potential farther than 5 A from every atom plane (qeio.slab_vacuum, raw *_avg.dat); dEc(2 nm) = two-step alignment '
      '(a/2 window, plateau spread 8 meV); dEc(t) = dEc(2 nm) + EA(2 nm) - EA(t) (same termination); dEv = dEc - dEg. E1 = dEc, E2 = E1 + E21, '
      'E3 = E1 + E31 (CB levels at Gamma relative to the bulk CBM). At 0.51 nm E2 and E3 are degenerate (1.887 / 1.888 eV above E1).')
    w('')
    w(f"Caveats: 0.75 nm is polar without dipole correction: vacuum ramp {D3['slabs']['0.75']['ramp_over_gap_meV']} meV across the vacuum gap, "
      f"EA/IP/dEc +- {D3['slabs']['0.75']['half_ramp_sensitivity_eV']} eV (ASSUMED reference-choice sensitivity, not a bound); dEc(0.695) range "
      f"{f(D3['slabs']['0.75']['dEc_sensitivity_eV'])} eV. 0.51 nm is In8(OH)24 (outside every law). HSE-corrected and experiment-anchored gaps "
      'assume dEg_HSE = r dEg_PBE with r measured at 1 nm only and thickness-independent (ASSUMED); the slab EXX q-convergence is untested.')
    w('')
    w('W slabs (COMPUTED, metallic cells): ' + '; '.join(
        f"{lab}: EA(host CB) {x['EA_hostCB_eV']}, IP(VB top) {x['IP_VBtop_eV']}, work function {x['work_function_eV']} eV, "
        f"E_F - host CB min {x['EF_minus_hostCB_min_eV']} eV, VB-top to host-CB {x['gap_VBtop_hostCB_eV']} eV" for lab, x in D3['W_slabs'].items()) +
      '. ' + ' '.join(
        f"At {lab} W changes EA(host CB) by {D3['W_slabs'][lab]['EA_hostCB_eV'] - D3['slabs'][p]['EA_eV']:+.3f} eV and IP(VB top) by "
        f"{D3['W_slabs'][lab]['IP_VBtop_eV'] - D3['slabs'][p]['IP_eV']:+.3f} eV against the pure slab; the work function lies "
        f"{D3['W_slabs'][lab]['EA_hostCB_eV'] - D3['W_slabs'][lab]['work_function_eV']:.3f} eV below its own EA because E_F is in the CB."
        for lab, p in (('1 nm', '1.0'), ('2 nm', '2.0'))))
    w('')
    w('### 3.1 Laws a t^-p (FITTED; t = H-H thickness in nm)')
    w('')
    w('| Quantity | Fit | Points (t_HH) | a | sigma_a | p | sigma_p | rel. residuals | LOO range a / p | at 2.0 / 6.3 / 13.2 nm |')
    w('|---|---|---|---|---|---|---|---|---|---|')
    for key, nm in (('dEg_eV', 'dEg'), ('dEc_eV', 'dEc'), ('minus_dEv_eV', '-dEv'), ('dm_e_band_edge', 'dm_e (band edge)'), ('dm_e_4pt_deck_basis', 'dm_e (deck basis)')):
        for fk, ff in lw[key].items():
            if not isinstance(ff, dict) or 'a' not in ff:
                continue
            at = ff.get('at_nm', {})
            w(f"| {nm} | {fk} | {', '.join(f(v, 3) for v in ff['t_nm'])} | {ff['a']} | {f(ff.get('sigma_a'))} | {ff['p']} | {f(ff.get('sigma_p'))} | "
              f"{', '.join(f(v, 4) for v in ff['rel_resid'])} | {f(ff.get('loo_a'))} / {f(ff.get('loo_p'))} | "
              f"{' / '.join(f(at.get(k_), 4) for k_ in ('2.0', '6.3', '13.2')) if at else '-'} |")
    w('')
    w('- sigma_a, sigma_p: residual scatter about the law (fit3 has one residual degree of freedom); they exclude functional, termination, '
      'thickness-definition and polar-field errors. LOO = leave-one-out refits.')
    w(f"- dEg: fit3 reproduces the V3 / C10 law ({lw['config_V3']['dEg']['a']}, {lw['config_V3']['dEg']['p']}); fit2 and fit4 (with 0.46 nm) differ "
      'by < 0.001 eV at 2 nm (small residual scatter, sigma_p 0.007).')
    w(f"- dEc: fit3 (frozen V3 / C10 law, {lw['config_V3']['dEc']['a']}, {lw['config_V3']['dEc']['p']}) has sigma_p {lw['dEc_eV']['fit3']['sigma_p']}; the "
      f"two-point fit without the polar 0.695 nm point (the primary fit until a dipole-corrected run exists) gives p = {lw['dEc_eV']['fit2_1and2nm']['p']}; "
      f"at 6.3 nm the options span {lw['dEc_eV']['fit2_1and2nm']['at_nm']['6.3']}-{lw['dEc_eV']['fit3_0p695_low']['at_nm']['6.3']} eV.")
    w('- -dEv: ' + lw['minus_dEv_eV']['verdict'] + '.')
    w('- m*_h: ' + lw['m_h']['verdict'] + '.')
    w(f"- HSE: dEg_HSE(t) = r dEg_PBE(t) (ASSUMED) scales a to {f(lw['HSE_scaled_dEg']['fit3_a_scaled'])} with p unchanged.")
    w('')
    w('**BM7**. (a) Gap vs H-H thickness: PBE (circles; open = 0.51 nm), PBE direct at Gamma (bars), HSE-corrected Eg_HSE,bulk + r dEg_PBE '
      '(diamonds, mean of the two r / bulk-HSE pairings, which differ by <= 0.06 eV), computed HSE06 1 nm (square); dashed: bulk PBE and '
      'bulk HSE06 q3; grey band: experimental fundamental gap 2.93 +- 0.15 eV (King 2009). (b) dEg, dEc and -dEv (log-log) with the fit3 '
      '(solid) and fit2 (dashed) laws; bar at 0.695 nm: +-0.17 eV vacuum-reference sensitivity. (c) EA (circles) and IP (squares) of the pure '
      'slabs, W slabs (diamonds: host-CB EA and VB-top IP); bars: 0.75 nm sensitivity; dashed: bulk-equivalent EA / IP. (d) CB levels at '
      'Gamma relative to the bulk CBM: E1, E2, E3.')
    w('')
    # ------------------------------------------------------------------ 4 TCAD
    w('## 4. TCAD-ready parameters per thickness')
    w('')
    rows = D4['rows']
    w('| t (nm) | source | Eg PBE | Eg HSE-corr. | Eg exp.-anchored | Eg deck basis (3.05 + dEg) | chi PBE vacuum | chi deck basis (4.3 - dEc) | m*_e PBE | m*_e deck basis | Nc 3-D (deck m) | Nc 3-D Kane | Nc quasi-2-D (N2D/t) | Nc q-2-D Kane |')
    w('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for k, x in rows.items():
        chi_d = x.get('chi_deck_basis_eV', x.get('chi_deck_basis_fit3_eV'))
        chi_s = f(chi_d) + (f" (fit2 {f(x['chi_deck_basis_fit2_eV'])})" if 'chi_deck_basis_fit2_eV' in x else '')
        q2 = (f(x['Nc_q2D_deck_mass_cm3']), f(x['Nc_q2D_kane_deck_mass_cm3'])) if x['t_nm'] <= 2.0 else ('n/a (multi-subband)', 'n/a')
        w(f"| {x['t_nm']} | {x['source']} | {f(x['Eg_PBE_eV'])} | {f(x['Eg_HSE_corrected_eV'])} | {f(x['Eg_exp_anchored_eV'])} | {f(x['Eg_deck_basis_eV'])} | "
          f"{f(x.get('chi_PBE_vacuum_eV'))} | {chi_s} | {f(x.get('m_e_PBE_2D_dos', x.get('m_e_PBE_band_edge')))} | {f(x['m_e_deck_basis'])} | "
          f"{f(x['Nc3D_parabolic_deck_mass_cm3'])} | {f(x['Nc3D_kane_deck_mass_cm3'])} | {q2[0]} | {q2[1]} |")
    w('')
    bb = D4['bulk']
    w(f"Bulk: Eg PBE {bb['Eg_PBE_eV']}, HSE06 {f(bb['Eg_HSE_eV'])} eV; m*_e PBE {bb['m_e_PBE_band_edge']} (HSE estimate {f(bb['m_e_HSE_estimate_range'])}) m0; "
      f"alpha {bb['alpha_PBE_per_eV']} 1/eV; chi PBE bulk-equivalent {bb['chi_PBE_bulk_equivalent_eV']} eV; Nc(PBE m) {f(bb['Nc3D_PBE_mass_cm3'])}, "
      f"Nc(0.208) {f(bb['Nc3D_lit_0p208_cm3'])} (Kane {f(bb['Nc3D_lit_0p208_kane_cm3'])}) cm^-3; Nv {f(bb['Nv_cm3_k4_80atom'])} cm^-3 "
      f"(all grids {f(bb['Nv_cm3_range_all_grids'])}).")
    w('')
    w('Labels: Eg PBE, chi PBE vacuum, m*_e PBE, Nv = COMPUTED at the DFT thicknesses and FITTED (laws) at 2.0 / 6.3 / 13.2 nm (6.3 and 13.2 nm '
      'are extrapolations); HSE-corrected and experiment-anchored Eg = CALCULATED with the ASSUMED r rule; deck-basis columns = LITERATURE bulk '
      '(3.05 eV, 4.3 eV, 0.208 m0) + FITTED increments, exactly the V3 construction; Nc = CALCULATED. Quasi-2-D Nc only where a single subband is '
      'justified by a COMPUTED E21 >> kT (t <= 2 nm).')
    w('')
    w('Other TCAD items:')
    w(f"- m* for tunnelling: {D4['tunnelling_mass']['label']}. {D4['tunnelling_mass']['note']}.")
    w(f"- W donor: {D4['W']['TCAD']['donor_level']}; occupation at device densities {D4['W']['TCAD']['occupation_at_device_densities']}. "
      'COMPUTED per cell (level - host CB at Gamma / level - E_F / E_F - host CB, eV): ' + '; '.join(
          f"{k} {v['W_level_minus_hostCB_Gamma_eV']} / {v['W_level_minus_EF_Gamma_eV']} / {v['EF_minus_hostCB_Gamma_eV']}"
          for k, v in D4['W'].items() if isinstance(v, dict) and 'W_level_minus_hostCB_Gamma_eV' in v) +
      f". Deck: {D4['W']['TCAD']['deck']}. W-5d counts are Loewdin projections of occupied above-VB states (0.09-0.43), not a trapped fraction.")
    w('- Surface / OH states: ' + D4['surface_OH']['TCAD'] + '. Per slab (VB-top OH share / CB-bottom OH share): ' + '; '.join(
        f"{k} {v['VB_top_OH_share']} / {v['CB_bottom_OH_share']}" for k, v in D4['surface_OH'].items() if isinstance(v, dict)) + '.')
    w(f"- Fermi level: {D4['fermi_level']['pure_slabs']}; W cells: E_F - host CB at Gamma = " + ', '.join(
        f"{k} {v}" for k, v in D4['fermi_level']['W_cells'].items()) + f" eV ({D4['fermi_level']['W_note']}).")
    w('- Nv: COMPUTED Nv is about 1.9e21 cm^-3 (bulk) and 1.8e21-4.4e21 cm^-3 (quasi-3-D, slabs), about 200 times the deck NV300 = 1e19 '
      '(ASSUMED). Holes are not solved in the decks, so NV300 enters through n_i: n_i grows by sqrt(190) ~ 14 but stays far below 1 cm^-3 for '
      'Eg > 3 eV, so a small absolute contribution is expected; the SRH / trap terms and the registered two-carrier tests still need their '
      'conditional bounds checked before calling it negligible.')
    w('')
    w('### 4.1 Comparison with the deck values')
    w('')
    w('| Deck | run | eg300 deck / here (deck basis) | diff (meV) | affinity deck / here fit3 (fit2) | diff fit3 (meV) | m* deck / here | Nc300 deck / here 3-D / q-2-D (Kane) | Nv300 deck / COMPUTED |')
    w('|---|---|---|---|---|---|---|---|---|')
    for name, c in D4['deck_comparison'].items():
        t = float(name.split('@')[1])
        q2 = f"{f(c['here_Nc_q2D'])} ({f(c['here_Nc_q2D_kane'])})" if t <= 2.0 else 'n/a'
        w(f"| {name} | {c['run']} ({c['deck_src']['eg300']}) | {c['deck']['eg300']} / {c['here_Eg_deck_basis']} | {c['diff_Eg_meV']} | "
          f"{c['deck']['affinity']} / {c['here_chi_fit3']} ({c['here_chi_fit2']}) | {c['diff_chi_fit3_meV']} | {c['deck']['mstar']} / {c['here_m_deck_basis']} | "
          f"{f(c['deck']['nc300'])} / {f(c['here_Nc3D_deck_mass'])} / {q2} | 1e19 / {f(c['here_Nv_bulk'])} |")
    w('')
    w('- The C10 decks (fit3) are reproduced to <= 0.11 meV in Eg and affinity, 0.0002 m0 in m* and 0.1 % in Nc (2 nm quasi-2-D: deck 1.373e19 '
      'vs 1.374e19 here). V2 differs by 3-5 meV because V2 used its two-point laws at the Lin labels (0.95 / 1.98 nm), as recorded in ../out/f06.')
    w('- Not in the decks: (i) the CB non-parabolicity (Kane alpha 0.58 bulk, 0.45-0.50 at 2 nm), which raises Nc by 5.7 % (3-D) or 2.5 % '
      '(quasi-2-D) and the conductivity (optical) mass at degenerate filling, m(1 + 2 alpha E_F); (ii) the HSE r factor in dEg (+6 to +11 %); (iii) the band-edge '
      '(Kane) vs 3-point basis of m* (-3 % bulk to +0.5 % at 0.75 nm); (iv) the computed Nv (x190). None changes the frozen C10 laws; (i) and (ii) are candidate '
      'sensitivities only.')
    w('')
    w('**BM8**. TCAD options at the device thicknesses 2.0 / 6.3 / 13.2 nm (crosses: deck values of runs 0058/0061 at 2.0, 0068 at 6.3 and 0069 '
      'at 13.2 nm). (a) Nc: 3-D parabolic and Kane with the deck-basis mass; quasi-2-D N2D/t (2.0 nm only). (b) Eg: deck basis (3.05 + dEg), '
      'experiment-anchored (2.93 + r dEg), HSE-corrected (Eg_HSE,bulk + r dEg). (c) chi = 4.3 - dEc for fit3 and fit2; grey bars: range over '
      'fit3, fit2 and the +-0.17 eV 0.695 nm sensitivity.')
    w('')
    # ------------------------------------------------------------------ 5 literature
    w('## 5. Literature comparison (checked 2026-10-14)')
    w('')
    w('| Quantity | Literature value (method) | Citation | This work | Why ours differs |')
    w('|---|---|---|---|---|')
    lit = [
        ('Fundamental gap, bixbyite', '2.93 +- 0.15 eV (photoemission + optical, single crystals); HSE03 VBM slightly off Gamma along G-H, VB(Gamma) only ~50 meV below',
         'King et al., PRB 79, 205211 (2009), doi:10.1103/PhysRevB.79.205211',
         f"PBE {D3['bulk']['Eg_fundamental_eV']} eV (indirect by 4.4 meV, VBM at 0.2 G-H); HSE06 {D3['hse']['HSE_bulk_q3_f160']['gap_eV']['value']}-{D3['hse']['HSE_bulk_q1']['gap_eV']['value']} eV",
         'PBE self-interaction error (-2.0 eV); HSE06 (25 % exchange) still -0.8 eV: In2O3 needs a larger mixing or GW; the off-Gamma VBM is reproduced qualitatively, with a smaller offset in PBE'),
        ('Fundamental gap (upper limit)', '<= 2.9 eV; dipole transitions VB top -> CB forbidden or weak, strong absorption about 0.8 eV higher',
         'Walsh et al., PRL 100, 167402 (2008), doi:10.1103/PhysRevLett.100.167402', 'not computed (no dipole matrix elements)',
         'the 0.893 eV "direct gap at Gamma" here is not the optical gap'),
        ('Absorption onset', 'about 2.7 eV at room temperature (melt-grown crystals), proposed indirect', 'Irmscher et al., Phys. Status Solidi A 211, 54 (2014), doi:10.1002/pssa.201330184',
         '-', 'temperature (300 K vs 0 K DFT) and functional'),
        ('Optical (dipole-allowed) onset', '3.8 eV for n <= 1e19 cm^-3', 'Feneberg et al., PRB 93, 045203 (2016), doi:10.1103/PhysRevB.93.045203 (erratum PRB 94, 239905)',
         '-', 'not computed'),
        ('m*_e (band edge)', '0.18 m0 (zero-density, from plasma frequencies); 0.4 m0 at 1e21 cm^-3', 'Feneberg et al. 2016 (above); value from the abstract; the erratum PRB 94, 239905 (doi:10.1103/PhysRevB.94.239905) was not readable here (the Codex review reports that it leaves the results unaffected)',
         f"PBE {bs['m_dos']} m0 (Kane), {bs['m_parabolic_4pt_intercept_by_dir']['[100]']} (3-point); HSE06 estimate 0.16-0.19; PBE Kane optical mass {mo21:.2f} m0 at 1e21",
         'PBE gap too small -> Kane coupling too strong -> band-edge mass 14 % (vs 0.18) to 26 % (vs 0.208) too small; the calibrated HSE06 estimates suggest that most of the difference closes'),
        ('m*_e (band edge)', '0.208 +- 0.006 m0 (optical Hall effect, n = 2.8e17 cm^-3)', 'Stokey et al., J. Appl. Phys. 129, 225102 (2021), doi:10.1063/5.0052848',
         'deck LITERATURE value 0.208 (V3)', 'as above'),
        ('m*_e (DFT-PBE)', '0.17 m0 bulk; 0.23 m0 (1.98 nm) and 0.30 m0 (0.95 nm) H-passivated slabs; gaps 0.94 / 1.27 / 1.88 eV (PBE, ONCV 140 Ry; Wannier interpolation for DOS)',
         'Lin et al., ACS Nano 16, 21536 (2022), doi:10.1021/acsnano.2c10383 (methods text: arXiv:2205.00357)',
         f"bulk 0.154-0.159; 2 nm {D1['slabs']['2.0']['electron_summary']['m_4pt_intercept_[100]']}, 1 nm {D1['slabs']['1.0']['electron_summary']['m_4pt_intercept_[100]']} m0; dEg 0.335 / 0.900 eV",
         'their thickness labels are not H-H thicknesses; their fit window is not stated (our 2 nm anchored masses run from '
         f"{D1['slabs']['2.0']['electron']['[100]']['windows']['2']['m_anchored']} to {D1['slabs']['2.0']['electron']['[100]']['windows']['10']['m_anchored']} m0 "
         f"over 0-{D1['slabs']['2.0']['electron']['[100]']['windows']['10']['Emax_meV']:.0f} meV); ours are 6-10 % lower on the 3-point basis"),
        ('Confinement in atomic-layer In2O3', 'gap opening and Fermi-level shift from quantum confinement, supported by DFT', 'Si et al., Nano Lett. 21, 500 (2021), doi:10.1021/acs.nanolett.0c03967',
         'dEg = 0.815 t^-1.316 eV (PBE, fit3)', 'qualitative agreement; their films are amorphous ALD In2O3'),
        ('m*_h', 'no tabulated value located; the top VB is very flat (both papers above)', 'King 2009; Walsh 2008',
         'single-band hole mass not meaningful (degenerate, camel back); DOS-equivalent ~18 m0; 0.75 nm slab 3.3-5.9 m0', 'not a comparison: flatness confirmed'),
        ('IP / EA', 'IP about 7.0 eV ((111)) and about 7.7 eV ((100), O-dimer termination, O-rich), photoemission + DFT; EA = IP - 2.93 -> about 4.1-4.8 eV (derived here)',
         'Hohmann et al., J. Phys.: Condens. Matter 23, 334203 (2011), doi:10.1088/0953-8984/23/33/334203',
         f"PBE H-(001) bulk-equivalent IP {D3['bulk_equivalent']['IP_eV']} eV, EA {D3['bulk_equivalent']['EA_eV']} eV",
         'PBE places the VBM too high (IP too small by > 1.3 eV) and the termination differs (OH vs bare / O-dimer); EA is the better-behaved PBE edge; the deck uses 4.3 eV (LITERATURE)'),
        ('Resonant donor (analogue)', 'Mo 4d donor states lie high in the In2O3 CB and barely perturb the CBM', 'Swallow et al., Mater. Horiz. 7, 236 (2020), doi:10.1039/c9mh01014a',
         'W 5d level 1.2-1.8 eV above the CBM; host-CB mass +5 % (bulk)', 'consistent picture; W itself: no peer-reviewed DFT located in this search'),
    ]
    for row in lit:
        w('| ' + ' | '.join(row) + ' |')
    w('')
    # ------------------------------------------------------------------ 6 missing
    w('## 6. Not derivable from the existing data: runs needed (none submitted)')
    w('')
    w('Costs are scaled from measured wall times of the same cells (run sheets in ../runs_sep_oct and the protocol outputs); "local" = WSL '
      'Ubuntu-22.04, env qe, 10 MPI ranks, -nk 2.')
    w('')
    w('| # | Missing quantity | Exact run | Cost basis (measured) | Estimate |')
    w('|---|---|---|---|---|')
    miss = [
        ('W-slab band-edge masses, 1 nm', 'SCF (rerun; no save kept) + bands on iwo_slab1_final_cpu geometry, the 21 k tpiba lines of slab1r_final_cpu/bands.in, '
         "diagonalization = 'cg' (the Davidson bands step failed in cdiaghg), nbnd 336", 'SCF 2 h 55 min, 16 CPUs; pure 1 nm bands 4 h 38 min (16 CPUs or one A100)',
         '~3 h SCF + 9-12 h bands (CG ~2x) on 16 CPUs'),
        ('W-slab band-edge masses, 2 nm', 'SCF + bands on iwo_slab2_final_cpu geometry (21 k, CG), conv_thr 1e-8, beta 0.1, ~66 GB', 'SCF 8 h 05 min on 33 CPUs; pure 2 nm bands 8 h 22 min on one H100',
         '~1 h SCF + 15-20 h bands on one H100 (or 2-3 days on 33 CPUs)'),
        ('Transverse hole masses at the bulk VBM', "'bands' on the local vcr save: k0 = (0, 0, 0.2) 2pi/a plus +-0.005 ... 0.03 1/A along [100], [010] and [110]-transverse, about 25 k, CG",
         'bands_gamma.out, 31 k: 4 h 21 min local', '~4 h local'),
        ('Converged Nv / hole DOS (bulk)', "nscf 6x6x6 Gamma-centred (24 operations), nbnd 190, occupations = 'tetrahedra_opt', then dos.x / projwfc.x", 'bands_gamma 31 k: 4.3 h local',
         '~5 h local'),
        ('Slab Nv / 2-D DOS', 'SCF rerun + nscf 6x6x1 (tetrahedra) for 0.75 / 1 / 2 nm', 'SCF 1 h 6 min (0.75 nm, 11 CPUs), 2 h 19 min (1 nm, 16 CPUs), 56 min (2 nm, H100)',
         '1-4 h per slab'),
        ('[010] line of the rectangular 0.51 nm cell', 'SCF + bands, 11 k along [010]', 'slabL1 SCF 28 min + bands 43 min (11 CPUs)', '~1.5 h'),
        ('Dipole-corrected 0.75 nm edges (dEc, EA, IP, VB character)', 'SCF with tefield = .true., dipfield = .true., edir = 3, emaxpos / eopreg inside the vacuum, + planar average + bands + forces',
         'slabL2 SCF 1 h 6 min + bands 1 h 27 min (11 CPUs); vc-relax 9 h 58 min (H100) if the forces exceed 1e-3 Ry/bohr', '~3 h (+10 h if re-relaxed)'),
        ('HSE06 band-edge masses (bulk, 1 nm)', 'HSE06 SCF on a full grid (nosym) + Wannier90 interpolation of the CB, or zero-weight small-k points if pw.x accepts them with EXX (to be tested)',
         'bulk q3 SCF (4 k) 4 h 15 min, 1 nm SCF (4 k) 4 h 0 min on one H100', '1-3 GPU-days per cell (uncertain)'),
        ('HSE06 EA / IP and the HSE dEc / dEv split', 'pp.x plot_num 11 + average.x on the HSE06 1 nm SCF (save needed: rerun) and the HSE bulk <V> via the G = 0 route', '1 nm HSE SCF 4 h on one H100',
         '~4 h GPU'),
        ('r = dEg(HSE)/dEg(PBE) at other thicknesses', 'HSE06 SCF (ecutfock 160) of the 0.75 and 2 nm slabs', '1 nm (96 atoms) 4 h on one H100; default ecutfock ran out of memory at 1 nm',
         '~3 h (0.75 nm); 15-25 h and possibly 2 GPUs (2 nm, 176 atoms)'),
        ('W level vs density (lower W fraction) and spin', '160-atom 1x1x2 cell, 1 W (1.6 %): vc-relax / relax + SCF + projwfc, spin-polarised check; a V0-era input exists in bulk_IWO_1W_1p6pct_112/ (not protocol-checked)',
         '80-atom W24d: relax 23 h 48 min + SCF 3 h on 32 CPUs', '~5 days on 32 CPUs or ~1 day on one H100'),
        ('Tunnelling (evanescent) mass in the gap', 'complex band structure of bulk In2O3 (pwcond.x; check its PAW support, else SG15 NC)', 'no measured basis', 'hours locally (uncertain)'),
        ('Masses of the H-L vacancy cells', 'not needed for H-L; would need band runs of In32O47 / In31WO47', '-', 'not proposed'),
    ]
    for i, row in enumerate(miss, 1):
        w(f'| {i} | ' + ' | '.join(row) + ' |')
    w('')
    # ------------------------------------------------------------------ 7 consistency
    w('## 7. Consistency with RESULTS_LOG, the ledger and the decks')
    w('')
    w('- RESULTS_LOG (2026-10-04 entry): 2 nm in-plane mass 0.2064 [100] / 0.2059 [110] m0, increment +0.047 over 0.159, Lin 0.23 m0 (10 % / 6 % '
      f"lower) are reproduced exactly on the same 3-point basis (here {D1['slabs']['2.0']['electron_summary']['m_4pt_intercept_[100]']} / "
      f"{D1['slabs']['2.0']['electron_summary']['m_4pt_intercept_[110]']}); E2 - E1 = 0.719 eV (2 nm) and 1.499 eV (1 nm) match.")
    w('- C020 (m* 0.206 m0 at 2 nm; 1 nm 0.95-1.00 eV HSE-corrected): matches (r x 0.8998 = 0.954-0.996 eV). The 0.206 is the 3-point parabola; '
      'the Kane band-edge value is 0.2026 (2-D DOS).')
    w('- V3 config "PBE bulk 0.159 m0" is the 3-point parabola; the band-edge (Kane) mass is 0.154 m0 (-3 %). Not an error; a basis definition '
      'to keep consistent.')
    w('- The 2 nm pure slab VBM is bulk-like (OH share 0.001; RESULTS_LOG 2026-10-05 18:23Z entry); in the W slabs the VB top is OH-surface O 2p '
      '(OH share 0.72 at 1 and 2 nm).')
    w('- No new discrepancy with RESULTS_LOG or the ledger was found in this deliverable; the deck NV300 (ASSUMED 1e19) differs from the COMPUTED Nv '
      'by about 190x; a small effect on the electron-only simulations is expected but not yet bounded (SRH / trap terms, two-carrier tests).')
    w('')
    holes_section(w)
    (bm.HERE / 'BANDS_MASSES.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('wrote BANDS_MASSES.md', len(L), 'lines')


def holes_section(w):
    """Section 8 (2026-10-14 request): hole masses as numbers, from out/b05_holes.json (b05_holes.py)."""
    H = json.loads((bm.OUT / 'b05_holes.json').read_text())
    hb = H['bulk']
    dirs = ('[100] (G-H)', '[110] (G-N)', '[111] (G-P)')
    w('## 8. Hole masses (b05_holes.py, figure BM9)')
    w('')
    w('Hole convention: m_h = -hbar^2 / (d^2E/dk^2); a negative value means the band rises away from Gamma. All numbers are PBE (PAW) and COMPUTED '
      'unless labelled otherwise. The valence-band top of In2O3 is a nearly flat O 2p manifold, so curvature masses describe only the immediate '
      'neighbourhood of an extremum; the thermally relevant quantity is the valence-band density of states (8.3).')
    w('')
    w('### 8.1 Bulk: band-resolved directional curvature masses at Gamma (bands 174-176, degenerate at Gamma)')
    w('')
    w(f"Source: `{hb['src_gamma']}` (Gamma + 10 points per direction, steps 0.0153 1/A); check: chord masses from the first points of `{hb['src_path']}` "
      '(steps 0.039-0.041 1/A). Windows: n = 2 / 3 / 4 / 6 / 10 points (|dE| up to the values in out/b05_holes.json).')
    w('')
    w('| Band | Direction | n=2 | n=3 | n=4 | n=6 | n=10 | print-rounding sigma (n=3) | path chord masses (1st-4th point) |')
    w('|---|---|---|---|---|---|---|---|---|')
    for bn, rec in hb['bands'].items():
        for d in dirs:
            x = rec['directions'][d]
            ww = x['windows']
            w(f"| {bn} | {d} | " + ' | '.join(f(ww[n]['m_anchored'], 2) if ww[n]['m_anchored'] is not None else 'flat (dE 0.0 meV)' for n in ('2', '3', '4', '6', '10')) +
              f" | {f(ww['3']['sigma_round'], 2)} | {', '.join(f(v, 2) if v is not None else '-' for v in x['path_check']['chord_mass'])} |")
    w('')
    w('| Band | character | inverse-curvature average under the angular model, m (n = 3 / 4 / 6 / 10) | star-weighted, same data (n = 4) | sampled directional curvature ratio max/min (n = 4) |')
    w('|---|---|---|---|---|')
    char = {'174': 'lightest falling band ("light-hole-like")', '175': 'heavy falling band (strong [110] window dependence)',
            '176': 'camel back: rises along [100] and [110], flat along [111]'}
    for bn, rec in hb['bands'].items():
        ang = rec['angular']
        def av(n):
            a_ = ang[n]
            if a_.get('status') != 'ok':
                return 'UNRESOLVED (' + ', '.join(a_.get('unresolved_directions', [])) + ' printed-flat)'
            return f(a_['m_inverse_curvature_average'], 2) if a_['m_inverse_curvature_average'] else f"net 1/m {f(a_['avg_inv_m'], 3)} < 0"
        a4 = ang['4']
        sw = f(a4.get('m_star_weighted_same_data'), 2) if a4.get('m_star_weighted_same_data') else '-'
        cr = f(a4.get('sampled_directional_curvature_ratio'), 2) if a4.get('sampled_directional_curvature_ratio') else ('mixed signs' if a4.get('status') == 'ok' else 'UNRESOLVED')
        w(f"| {bn} | {char.get(bn, '')} | " + ' / '.join(av(n) for n in ('3', '4', '6', '10')) + f" | {sw} | {cr} |")
    w('')
    w('The directional masses above are the primary result. The "inverse-curvature average under the angular model" expands 1/m in cubic harmonics '
      'through the three directions, 1/m(d) = a + b (S4 - 3/5) + c (S6 - 1/105), and reports 1/a. Three directions fix exactly three coefficients, so the '
      'angular model is not tested: higher terms can vanish in all three sampled directions and still change the spherical average. It is an ESTIMATED '
      'diagnostic with no transport or DOS significance; the star-weighted harmonic mean uses the same data and is not an independent check. The '
      '"sampled directional curvature ratio" is the max/min of 1/m over the three sampled directions (neither the anisotropy nor the warping '
      'parameter in the strict sense). A printed-flat direction (dE 0.0 meV in the window) is UNRESOLVED, not zero curvature.')
    w('')
    om = hb['offgamma_maxima']
    w('### 8.2 Off-Gamma maxima and why curvature masses are not transport masses')
    w('')
    w(f"- [100] (G-H): band 176 peaks at |k| = {om['[100] (G-H)']['k0_invA']} 1/A, {om['[100] (G-H)']['E0_minus_Gamma_meV']} meV above VB(Gamma) "
      f"(global VBM, six pockets on <100>); longitudinal mass {om['[100] (G-H)']['m_long']} +- {om['[100] (G-H)']['sigma_round']} m0 (5-point parabola, print rounding).")
    w(f"- [110] (G-N): a second, lower maximum at |k| = {om['[110] (G-N)']['k0_invA']} 1/A, +{om['[110] (G-N)']['E0_minus_Gamma_meV']} meV "
      f"(coarse path points; bands_gamma reaches +{om['[110] (G-N)']['bands_gamma_end_rise_meV']} meV at 0.153 1/A), longitudinal mass "
      f"{om['[110] (G-N)']['m_long']} +- {om['[110] (G-N)']['sigma_round']} m0.")
    w('- [111] (G-P): Gamma is the maximum of the triplet along this line (bands 174/175 degenerate, 176 nearly flat).')
    w(f"- Transverse masses at the off-Gamma maxima are not computed (no k-points off the lines). All maxima lie within 4.4 meV of VB(Gamma), "
      f"far below kT = {om['kT_meV']} meV: at 300 K holes populate all three bands over |k| up to about 0.2-0.3 1/A, where the bands are strongly "
      'warped and non-parabolic (BM9a). No single band-edge hole mass describes them.')
    tr = hb['triplet_gamma_average']
    def tv(n, key):
        return f(tr[n].get(key), 3) if tr[n].get(key) else 'UNRESOLVED'
    w(f"- Gamma-local averages of the inverse-curvature averages (equal band populations, ESTIMATED diagnostic): the two falling bands give m_h = "
      f"{tv('3', 'm_cond_two_falling_bands')} / {tv('4', 'm_cond_two_falling_bands')} / {tv('6', 'm_cond_two_falling_bands')} m0 (n = 3 / 4 / 6); including the "
      f"camel-back band {tv('3', 'm_cond_triplet_incl_camelback')} / {tv('4', 'm_cond_triplet_incl_camelback')} / "
      f"{tv('6', 'm_cond_triplet_incl_camelback')} m0. {tr['note']}. A thermal conductivity mass (Boltzmann-weighted band velocities over the "
      'zone) needs a dense uniform grid and an interpolation (BoltzTraP2 / Wannier); not available.')
    w('')
    nv = H['bulk_Nv']
    w('### 8.3 Bulk DOS hole mass from the computed valence-band density of states')
    w('')
    w(f"N_V(300 K) = (1/V) sum_k w_k sum_n exp(-(E_ref - E_nk)/kT) over the valence states with E_ref - E_nk <= window: the integral of the grid DOS "
      f"(delta functions at the computed eigenvalues) with the Boltzmann factor; Fermi-Dirac statistics reduce to it for E_F - E_V >> kT (n-type IWO: "
      f"about 3 eV). m_h,DOS = (N_V / N0)^(2/3) m0 with N0 = 2 (2 pi m0 kT / h^2)^1.5 = {nv['N0_cm3']:.5g} cm^-3 (300 K). COMPUTED on the stated grids.")
    w('')
    w('| Grid | E_ref | window 0.05 eV | 0.1 eV | 0.2 eV | all states | m_h,DOS (all) |')
    w('|---|---|---|---|---|---|---|')
    for g, items in nv['grids'].items():
        for x in items:
            bw = x['by_window_eV']
            w(f"| {g} | {x['E_ref_note']} ({x['E_ref_eV']} eV) | {f(bw['0.05']['Nv_cm3'])} | {f(bw['0.1']['Nv_cm3'])} | {f(bw['0.2']['Nv_cm3'])} | "
              f"{f(bw['all']['Nv_cm3'])} | {f(bw['all']['m_h_dos'], 1)} |")
    w('')
    hs = nv['HSE_k3_same_grid']
    w("- Energy window: N_V saturates by 0.2-0.3 eV below E_ref (Boltzmann factor 4.4e-4 at 0.2 eV, below 1e-5 near 0.3 eV); about 80 % comes from the top "
      "0.05 eV. This window saturation is separate from k-mesh convergence, which is not established.")
    w(f"- Spread over grids and references: N_V = {f(nv['Nv_range_cm3'])} cm^-3, m_h,DOS = {f(nv['m_h_dos_range'])} m0. Densest grid (80-atom k4, 14 k): "
      f"{f(nv['grids']['80-atom k4 (14 k, H-L parent)'][0]['by_window_eV']['all']['Nv_cm3'])} cm^-3, "
      f"{f(nv['grids']['80-atom k4 (14 k, H-L parent)'][0]['by_window_eV']['all']['m_h_dos'], 1)} m0 (own maximum) and "
      f"{f(nv['grids']['80-atom k4 (14 k, H-L parent)'][1]['by_window_eV']['all']['m_h_dos'], 1)} m0 (off-Gamma VBM reference). Convergence error unestablished.")
    w(f"- HSE06 on the same k3 grid (own maxima): m_h,DOS {hs['HSE06_q1']['m_h_dos']} (q1) and {hs['HSE06_q3']['m_h_dos']} (q3) m0 against NC-PBE "
      f"{hs['NC_PBE']['m_h_dos']} m0, i.e. x{f(nv['HSE_over_NCPBE_m_h_dos'])} (ESTIMATED: k3 grid only).")
    w(f"- The deck NV300 = 1e19 cm^-3 (ASSUMED) implies m_h,DOS = {nv['deck_implied_m_h_dos']} m0; the computed value is about 30-41 times larger "
      'in mass and 160-270 times larger in N_V.')
    w('')
    w('### 8.4 Slabs and W cells (in-plane)')
    w('')
    w('| Slab | top band: m_h [100] / [110] (n = 3) | 2nd band (n = 3) | 3rd band (n = 3) | top-band tensor m_x / m_y / 2-D DOS / 2-D cond. (n = 3) | passes local screens? | N_V-equivalent m_h,DOS 2-D / quasi-3-D |')
    w('|---|---|---|---|---|---|---|')
    for lab, s in H['slabs'].items():
        bands = list(s['bands_anchored_masses'].keys())
        def mm(bn):
            x = s['bands_anchored_masses'][bn]
            return f"{f(x['[100]'].get('3'), 2)} / {f(x['[110]'].get('3'), 2)}"
        t3 = s['top_band_tensor_n3']
        ts = f"{t3['m_x']} / {t3['m_y']} / {t3['m_dos_2d']} / {t3['m_cond_2d']}" if t3 else 'inconsistent (1/m_y < 0): not a parabolic D2h band'
        w(f"| {lab} nm | {mm(bands[2])} | {mm(bands[1])} | {mm(bands[0])} | {ts} | {'yes' if s['passes_local_fit_screens'] else 'no'} | "
          f"{s['m_h_dos_2d_equiv']} / {s['m_h_dos_3d_equiv_quasi3D']} |")
    w('')
    for lab, s in H['slabs'].items():
        w(f"- {lab} nm: {s['why_not_a_clean_mass_and_fix']}.")
    w('')
    for lab in ('bulk 8b', 'bulk 24d'):
        s = H['W_cells'][lab]
        top = s['bands_anchored_masses'][str(s['VB_top_band'])]
        w(f"- W {lab}: top VB (band {s['VB_top_band']}) n = 3 masses " + ', '.join(f"{d} {f(v.get('3'), 2)}" for d, v in top.items()) +
          f" m0; next band {s['VB_sep_Gamma_meV']} meV below. {s['reason']}")
    for lab in ('W slab 1 nm', 'W slab 2 nm'):
        s = H['W_cells'][lab]
        w(f"- {lab}: {s['label']}. W cell (VB band {s['W']['VB_top_band']}): drops {', '.join(f(v, 1) for v in s['W']['drop_meV'])} meV at "
          f"{', '.join(f(v, 3) for v in s['W']['k_invA'])} 1/A, chord masses {', '.join(f(v, 1) for v in s['W']['chord_mass'])} m0; pure twin "
          f"{', '.join(f(v, 1) for v in s['pure twin']['chord_mass'])} m0. {s['reason']}. Fix: {s['fix']}.")
    w('')
    w('### 8.5 TCAD recommendation for NV300')
    w('')
    w('| t (nm) | NV300 (cm^-3) | form | label |')
    w('|---|---|---|---|')
    for t, row in sorted(H['tcad']['rows'].items(), key=lambda kv: float(kv[0])):
        w(f"| {t} | {f(row['NV300_cm3'])} | {row['form']} | {row['label']}{('; ' + row['note']) if row.get('note') else ''} |")
    imp = H['tcad']['impact']
    w('')
    w('- Recommendation: the crystalline PBE valence-band DOS gives N_V of about 2e21 cm^-3 (COMPUTED on coarse grids: 1.6-2.7e21 in bulk, 1.8-2.9e21 '
      'quasi-3-D in the 0.7-2 nm slabs; HSE06 on the k3 grid suggests 0.6-0.9 times this). A constant NV300 = 2e21 cm^-3 at every device '
      'thickness would be ASSUMED, informed by these COMPUTED crystalline values (bulk-to-film transfer at 6.3 / 13.2 nm, crystalline-to-device '
      'transfer everywhere). A quasi-2-D single-subband N2D/t is not justified for holes (the top valence levels are within 3-30 meV); the slab '
      'values already sum all subbands. The frozen C10 parameters keep NV300 = 1e19 (ASSUMED) unless a sensitivity run is registered.')
    w('- Scope: N_V is a band integral of free (delocalised) valence states. Hybrid-functional work predicts that holes in In2O3 self-trap as small '
      'polarons (Varley et al. 2012); that does not change the band integral, but N_V alone does not describe equilibrium hole populations, hole '
      'mobility or polaron transport. No polaron calculation was done here.')
    w(f"- Effect on the present TCAD (electrons only): {imp['deck_settings']}. n_i at 2 nm: {f(imp['ni_deck_cm3'])} cm^-3 (deck) -> "
      f"{f(imp['ni_with_computed_Nv_cm3'])} cm^-3 (computed N_V); equilibrium SRH generation bound n_i/(2 tau) = {f(imp['max_SRH_generation_cm3_s'])} cm^-3 s^-1; "
      f"hole emission at the centre of the deep acceptor Gaussian (E_C - 0.6 eV) {f(imp['hole_emission_rate_deep_acceptor_Ec_minus_0p6_s'])} s^-1 (not a bound on "
      f"the whole Gaussian or on field-assisted emission). In a two-carrier model the hole density is set by the local hole quasi-Fermi level, not the "
      f"electron one: p > 1e10 cm^-3 needs that level within {imp['E_F_minus_E_V_for_p_1e10_eV']} eV of E_V. CALCULATED with ASSUMED capture parameters "
      '(sigma 1e-15 cm^2, v_th 1e7 cm/s, tau 1e-6 s): small for the electron current in these terms; not a bound on a two-carrier simulation.')
    w('')
    w('### 8.6 Literature on In2O3 holes')
    w('')
    w('| Statement | Citation | Relation to this work |')
    w('|---|---|---|')
    for row in (
        ('Very shallow dispersion of the topmost VB; HSE03 VBM slightly off Gamma along G-H, VB(Gamma) only ~50 meV below', 'King et al., PRB 79, 205211 (2009), doi:10.1103/PhysRevB.79.205211',
         'same topology in PBE (VBM at 0.2 G-H) with a smaller offset (4.4 meV)'),
        ('Upper valence bands of small dispersion; VB-top to CB dipole transitions forbidden or weak', 'Walsh et al., PRL 100, 167402 (2008), doi:10.1103/PhysRevLett.100.167402',
         'flatness confirmed: curvature masses 3-200 m0 near Gamma'),
        ('Hybrid functional: holes self-trap as small polarons in In2O3 (favoured over free holes in all oxides studied except ZnO and SiO2), which prohibits p-type conductivity',
         'Varley, Janotti, Franchini, Van de Walle, PRB 85, 081109(R) (2012), doi:10.1103/PhysRevB.85.081109',
         'band (free-hole) masses are therefore not the transport-relevant quantity for holes in In2O3; polarons not computed here'),
        ('nKTB-mBJ DFT reports heavy- and light-hole masses for bixbyite In2O3 (electron mass 0.31 m0 in the abstract)', 'Halati et al., IET Optoelectron. 20, e70024 (2026), doi:10.1049/ote2.70024',
         'hole values not accessible here (publisher page 403); not compared'),
        ('No experimental In2O3 hole effective mass located in this search', '-', 'no measured benchmark'),
    ):
        w('| ' + ' | '.join(row) + ' |')
    w('')
    w('**BM9**. (a) Bulk bands 174 (blue), 175 (orange), 176 (green) near Gamma along [100] = G-H (solid), [110] = G-N (dashed), [111] = G-P (dotted) '
      'from bands_gamma.out; open circles: the coarser bands_path.out points; open markers: the off-Gamma maxima ([100] circle = global VBM, [110] square). '
      '(b) Directional curvature masses vs fit window for the three bands (circle [100], square [110], triangle [111]); filled = falling band, '
      'open = rising band (absolute value plotted). (c) m_h,DOS from the Boltzmann-integrated valence DOS for four grids (filled: own grid maximum, '
      'open squares: off-Gamma VBM reference; triangles: HSE06 q1 / q3 on the k3 grid); dashed: the value implied by the deck NV300 = 1e19 cm^-3. '
      '(d) Top (solid) and second (dotted) valence band of the four slabs along [110] (left) and [100] (right), relative to VB(Gamma).')
    w('')


if __name__ == '__main__':
    main()
