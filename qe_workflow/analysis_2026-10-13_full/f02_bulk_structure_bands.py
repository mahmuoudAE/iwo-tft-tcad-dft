"""Fig. 2: relaxed bulk In2O3 (PAW-PBE, 71 Ry, 3x3x3): lattice vs experiment, band structure, gap, CB effective mass.

Reads bulk_In2O3_protocol/vcrelax_ecut71_k3.out (final coordinates, enthalpy, pressure, forces), bands_path.out
(Gamma-H-N-Gamma-P-H|P-N, 80 k, crystal_b in bands_path.in) and bands_gamma.out (Gamma + 10 points along [100], [110],
[111]). 176 occupied bands (16 In x 13 + 24 O x 6 = 352 electrons).
Mass: parabolic fit E - E_CBM = c k^2 for |k| <= 0.05 1/A, (i) with a free intercept (as PROTOCOL.md / analyze_mass.py),
(ii) through the origin; Kane fit E(1 + alpha E) = (hbar^2/2m) k^2 over the whole range (|k| <= 0.153 1/A).
"""
import numpy as np

import qeio as q
from figstyle import plt, save, panel, CYCLE

A_EXP = 10.117          # Marezio 1966 (PROTOCOL.md section 2), LITERATURE
NOCC = 176


def kgrid(p):
    alat, s_alat = q.alat_A(p)
    a = q.lattice_alat(p)
    blocks = q.eig_blocks(p)
    k = np.array([b[0] for b in blocks])                  # 2pi/alat, Cartesian
    ev = np.array([b[1] for b in blocks])
    kcr = k @ a.T                                          # crystal coordinates (k . a_i)
    return alat, a, k, kcr, ev, blocks, s_alat


def main():
    res = {}
    # ---- vc-relax
    vr = q.BULK / 'vcrelax_ecut71_k3.out'
    cell, sym, frac, s_fin = q.final_struct_out(vr)
    a_conv = float(2 * abs(cell[0, 0]))
    vol = float(abs(np.linalg.det(cell)))
    m, i = q.last(vr, r'Final enthalpy\s+=\s+(-?[\d.]+) Ry')
    mb, ib = q.last(vr, r'bfgs converged in\s+(\d+) scf cycles and\s+(\d+) bfgs steps')
    P_all = q.grep(vr, r'P=\s+(-?[\d.]+)')
    F_all = q.grep(vr, r'Total force =\s+([\d.]+)')
    so, sso = q.symops(vr)
    # last relaxation step = the P/force lines just before 'bfgs converged'; final SCF = the last ones
    P_relax = [(float(mm.group(1)), ii) for mm, ii in P_all if ii < ib][-1]
    F_relax = [(float(mm.group(1)), ii) for mm, ii in F_all if ii < ib][-1]
    P_fin, F_fin = P_all[-1], F_all[-1]
    E_fin = q.etot(vr)
    # In-O by cation site: 8b = In at the positions (0.5,0.5,0.5),(0.5,0,0),(0,0,0.5),(0,0.5,0) and their equivalents
    sites = {}
    for j, s in enumerate(sym):
        if s != 'In':
            continue
        d = q.neighbours(cell, frac, j, 'O', sym, 2.5)[:6]
        key = '8b' if np.allclose(np.round(d, 3), round(d[0], 3), atol=2e-3) else '24d'
        sites.setdefault(key, set()).add(tuple(np.round(d, 3)))
    res['vcrelax'] = {
        'a_conv_A': q.V(round(a_conv, 5), s_fin, note='a = 2 |a1_x| of the primitive cell in the final coordinates'),
        'volume_prim_A3': q.V(round(vol, 4), s_fin),
        'a_exp_A': q.V(A_EXP, 'PROTOCOL.md section 2 (Marezio 1966)', 'LITERATURE'),
        'deviation_pct': round(100 * (a_conv / A_EXP - 1), 3),
        'final_enthalpy_Ry': q.V(float(m.group(1)), q.src(vr, i)),
        'bfgs': q.V(f'{mb.group(1)} scf cycles, {mb.group(2)} bfgs steps', q.src(vr, ib)),
        'last_step_P_kbar': q.V(P_relax[0], q.src(vr, P_relax[1])), 'last_step_total_force_Ry_bohr': q.V(F_relax[0], q.src(vr, F_relax[1])),
        'final_scf_E_Ry': q.V(E_fin[0], E_fin[1]), 'final_scf_P_kbar': q.V(float(P_fin[0].group(1)), q.src(vr, P_fin[1])),
        'final_scf_total_force_Ry_bohr': q.V(float(F_fin[0].group(1)), q.src(vr, F_fin[1])),
        'symops_primitive': q.V(so, sso),
        'In_O_by_site_A': {k: sorted(v) for k, v in sites.items()}}
    # ---- band path
    pp = q.BULK / 'bands_path.out'
    alat, a, k, kcr, ev, blocks, s_alat = kgrid(pp)
    assert ev.shape[0] == 80 and ev.shape[1] >= NOCC + 2, ev.shape
    nb, snb = q.first(pp, r'number of Kohn-Sham states=\s+(\d+)')
    special = {'G': (0, 0, 0), 'H': (0.5, 0.5, -0.5), 'N': (0, 0, 0.5), 'P': (0.25, 0.25, 0.25)}
    lab = {}
    for j, kc in enumerate(kcr):
        for n_, v in special.items():
            if np.allclose(kc, v, atol=2e-4):
                lab[j] = n_
    dk = np.linalg.norm(np.diff(k, axis=0), axis=1) * 2 * np.pi / alat
    jump = np.array([lab.get(j) == 'H' and lab.get(j + 1) == 'P' for j in range(len(dk))])
    x = np.concatenate([[0], np.cumsum(np.where(jump, 0, dk))])
    vb, cb = ev[:, NOCC - 1], ev[:, NOCC]
    iv, ic = int(vb.argmax()), int(cb.argmin())
    res['bands_path'] = {
        'n_k': 80, 'labels_at_index': lab, 'alat_A': q.V(round(alat, 5), s_alat),
        'VBM_eV': q.V(float(vb[iv]), blocks[iv][2], note=f'k index {iv}, crystal {np.round(kcr[iv], 4).tolist()}'),
        'CBM_eV': q.V(float(cb[ic]), blocks[ic][2], note=f'k index {ic}, crystal {np.round(kcr[ic], 4).tolist()}'),
        'VB_Gamma_eV': q.V(float(vb[0]), blocks[0][2]), 'CB_Gamma_eV': q.V(float(cb[0]), blocks[0][2]),
        'Eg_fundamental_eV': round(float(cb[ic] - vb[iv]), 4), 'Eg_direct_Gamma_eV': round(float(cb[0] - vb[0]), 4),
        'VBM_minus_VBGamma_meV': round(float(vb[iv] - vb[0]) * 1000, 1),
        'VBM_k_cart_2pi_over_a': np.round(k[iv] * 2 * np.pi / alat / (2 * np.pi / a_conv), 4).tolist()}
    # ---- mass
    pg = q.BULK / 'bands_gamma.out'
    alat_g, ag, kg, kcrg, evg, bg, s_alg = kgrid(pg)
    kabs = np.linalg.norm(kg, axis=1) * 2 * np.pi / alat_g
    mass = {}
    for d_, name in enumerate(['[100]', '[110]', '[111]']):
        idx = [0] + list(range(1 + 10 * d_, 11 + 10 * d_))
        kk, ee = kabs[idx], evg[idx, NOCC] - evg[0, NOCC]
        s = kk <= 0.05 + 1e-6
        c1 = np.polyfit(kk[s] ** 2, ee[s], 1)[0]
        c0 = float(np.sum(kk[s] ** 2 * ee[s]) / np.sum(kk[s] ** 4))
        A = np.column_stack([q.H2M * kk[1:] ** 2, -ee[1:] ** 2])
        inv_m, alpha = np.linalg.lstsq(A, ee[1:], rcond=None)[0]
        mass[name] = {'m_parabolic_intercept_m0': round(q.H2M / c1, 4), 'm_parabolic_origin_m0': round(q.H2M / c0, 4),
                      'n_points_fit': int(s.sum()), 'k_max_fit_invA': round(float(kk[s].max()), 4),
                      'm_kane_m0': round(1 / inv_m, 4), 'alpha_kane_per_eV': round(float(alpha), 3),
                      'k_max_invA': round(float(kk.max()), 4), 'E_at_kmax_eV': round(float(ee[-1]), 4),
                      'src': f'{bg[idx[0]][2]} .. {bg[idx[-1]][2]}'}
    res['mass'] = mass
    res['mass']['mean_parabolic_intercept_m0'] = round(float(np.mean([v['m_parabolic_intercept_m0'] for v in mass.values() if isinstance(v, dict)])), 4)
    res['gamma_run'] = {'VB_Gamma_eV': q.V(float(evg[0, NOCC - 1]), bg[0][2]), 'CB_Gamma_eV': q.V(float(evg[0, NOCC]), bg[0][2]),
                        'Eg_direct_Gamma_eV': round(float(evg[0, NOCC] - evg[0, NOCC - 1]), 4)}
    q.dump('f02_bulk_structure_bands', res)

    # ---- figure: (a) bands, (b) CB dispersion with fits
    fig = plt.figure(figsize=(6.6, 3.0))
    ax = fig.add_axes([0.08, 0.15, 0.50, 0.78])
    bx = fig.add_axes([0.70, 0.15, 0.28, 0.78])
    ref = float(vb[iv])
    for b in range(NOCC - 30, min(ev.shape[1], NOCC + 14)):
        ax.plot(x, ev[:, b] - ref, color='k' if b < NOCC else CYCLE[0], lw=0.7)
    for j, n_ in lab.items():
        ax.axvline(x[j], color='0.6', lw=0.5)
    ticks = []
    for j in sorted(lab):
        if lab[j] == 'P' and lab.get(j - 1) == 'H':
            continue
        ticks.append((x[j], 'H|P' if (lab[j] == 'H' and lab.get(j + 1) == 'P') else lab[j]))
    ax.set_xticks([t for t, s in ticks if s]); ax.set_xticklabels([s.replace('G', r'$\Gamma$') for t, s in ticks if s])
    ax.minorticks_off(); ax.tick_params(axis='y', which='minor', left=True, right=True)
    ax.yaxis.set_minor_locator(plt.matplotlib.ticker.AutoMinorLocator())
    ax.set_xlim(x[0], x[-1]); ax.set_ylim(-4, 5)
    ax.set_ylabel(r'$E - E_{\rm VBM}$ (eV)')
    panel(ax, 'a', x=-0.13)
    for d_, name in enumerate(['[100]', '[110]', '[111]']):
        idx = [0] + list(range(1 + 10 * d_, 11 + 10 * d_))
        kk, ee = kabs[idx], (evg[idx, NOCC] - evg[0, NOCC]) * 1000
        bx.plot(kk, ee, ['o', 's', '^'][d_], mfc='none', color=CYCLE[d_], label=name)
    kf = np.linspace(0, 0.155, 100)
    mm = mass['[100]']['m_parabolic_intercept_m0']
    bx.plot(kf, q.H2M / mm * kf ** 2 * 1000, '-', color='k', lw=0.8, label=f'parabolic')
    mk, al = mass['[100]']['m_kane_m0'], mass['[100]']['alpha_kane_per_eV']
    ek = (-1 + np.sqrt(1 + 4 * al * q.H2M / mk * kf ** 2)) / (2 * al)
    bx.plot(kf, ek * 1000, '--', color='k', lw=0.8, label='Kane')
    bx.axvline(0.05, color='0.6', ls=':', lw=0.7)
    bx.set_xlabel(r'$|k|$ (\AA$^{-1}$)'.replace(r'\AA', 'Å')); bx.set_ylabel(r'$E - E_{\rm CBM}$ (meV)')
    bx.set_xlim(0, 0.16); bx.set_ylim(0, 600)
    bx.legend(loc='upper left', fontsize=7)
    panel(bx, 'b', x=-0.30)
    save(fig, 'fig02_bulk_bands_mass')
    print(json_summary(res))


def json_summary(res):
    v = res['vcrelax']; b = res['bands_path']
    return (f"a = {v['a_conv_A']['value']} A ({v['deviation_pct']:+.3f} %), V = {v['volume_prim_A3']['value']}, "
            f"H = {v['final_enthalpy_Ry']['value']}, {v['bfgs']['value']}, P_last {v['last_step_P_kbar']['value']}, "
            f"F_last {v['last_step_total_force_Ry_bohr']['value']}, P_final {v['final_scf_P_kbar']['value']}, ops {v['symops_primitive']['value']}\n"
            f"In-O {v['In_O_by_site_A']}\n"
            f"VBM {b['VBM_eV']}, CBM {b['CBM_eV']}, Eg {b['Eg_fundamental_eV']}, direct {b['Eg_direct_Gamma_eV']}, dVB {b['VBM_minus_VBGamma_meV']} meV, kVBM {b['VBM_k_cart_2pi_over_a']}\n"
            f"labels {b['labels_at_index']}\nmass {res['mass']}\ngamma run {res['gamma_run']}")


if __name__ == '__main__':
    main()
