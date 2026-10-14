"""Band-structure figures (raw pw.x eigenvalues) and effective-mass figures (from out/b01_masses.json).

BM1 bulk In2O3: (a) G-H-N-G-P-H|P-N path, E - E_VBM; (b) CB near Gamma with the Kane and 4-point parabolic fits;
    (c) top three VBs near Gamma (meV).
BM2 relaxed slabs 0.51 / 0.75 / 1.0 / 2.0 nm: in-plane [110] (left) and [100] (right) lines of bands.out plus the
    3x3x1 SCF-grid points (open symbols), E - E_VBM.
BM3 W bulk (8b, 24d): Gamma-star [110] | [100] || [111], E - E_F, pure-bulk CB overlaid (aligned at its minimum).
BM4 systems with SCF-grid eigenvalues only (no k-path run): W slabs vs pure twins, HSE06 vs PBE bulk and 1 nm slab.
BM5 fit-window sensitivity of the CB masses (bulk, slabs) and of the slab hole masses.
BM6 masses vs thickness and with W / HSE: electron band-edge masses, increments (log-log), hole DOS-equivalent masses.
No text inside the panels except axis and tick labels; the captions are in BANDS_MASSES.md.
"""
import json

import numpy as np

import bm
from bm import q, plt
import figstyle as fs

R = q.RES
D = json.loads((bm.OUT / 'b01_masses.json').read_text())
C = fs.CYCLE
T_LAB = {'0.51': 0.4612, '0.75': 0.6953, '1.0': 0.9303, '2.0': 1.9623}


def mark_edges(ax, xv, yv, xc, yc):
    ax.plot([xv], [yv], 'o', mfc='white', mec='k', ms=4.5, zorder=5)
    ax.plot([xc], [yc], 'o', mfc='k', mec='k', ms=4.0, zorder=5)


def fig_bulk():
    bp = bm.read_bands(q.BULK / 'bands_path.out')
    bg = bm.read_bands(q.BULK / 'bands_gamma.out')
    no = int(bp['nelec'] / 2)
    ev = D['bulk']['VBM_eV']['value']
    K = bp['K']
    dk = np.linalg.norm(np.diff(K, axis=0), axis=1)
    labels = {0: r'$\Gamma$', 15: 'H', 33: 'N', 44: r'$\Gamma$', 57: 'P', 70: 'H|P', 79: 'N'}
    dk[70] = 0.0                                  # H|P discontinuity: no distance between index 70 (H) and 71 (P)
    x = np.concatenate([[0], np.cumsum(dk)])
    fig = plt.figure(figsize=(fs.FULL_W, 2.9))
    gs = fig.add_gridspec(1, 3, width_ratios=[2.2, 1, 1], wspace=0.42)
    ax = fig.add_subplot(gs[0])
    for n in range(no - 40, min(bp['nb'], no + 12)):
        col = 'k' if n < no else fs.ACCENT2
        ax.plot(x, bp['E'][:, n] - ev, color=col, lw=0.7)
    for i in labels:
        ax.axvline(x[i], color=fs.GREY, lw=0.5)
    ax.set_xticks([x[i] for i in labels])
    ax.set_xticklabels(list(labels.values()))
    ax.tick_params(axis='x', which='minor', bottom=False, top=False)
    ivbm = int(np.argmax(bp['E'][:, no - 1]))
    mark_edges(ax, x[ivbm], 0.0, x[0], bp['E'][0, no] - ev)
    ax.annotate('', xy=(x[0] + 0.03, bp['E'][0, no] - ev), xytext=(x[0] + 0.03, 0.0),
                arrowprops=dict(arrowstyle='<->', lw=0.8, color=fs.ACCENT))
    ax.set_xlim(x[0], x[-1])
    ax.set_ylim(-2.0, 4.5)
    ax.set_ylabel(r'$E-E_\mathrm{VBM}$ (eV)')
    fs.panel(ax, 'a', x=-0.13)
    # (b) CB near Gamma, Kane and parabola
    ax = fig.add_subplot(gs[1])
    el = D['bulk']['electron']
    for j, d in enumerate(('[100]', '[110]', '[111]')):
        f = el[d]
        k = np.array(f['k_invA'])
        e = np.array(f['dE_meV']) / 1000
        ax.plot(k, e * 1000, ['o', 's', '^'][j], color=C[j], ms=3.2, mfc='none', label=d)
    kk = np.linspace(0, 0.155, 200)
    m, a = D['bulk']['electron_summary']['m_edge_by_dir']['[100]'], el['[100]']['kane']['10']['alpha_per_eV']
    g = bm.H2M * kk ** 2 / m
    ax.plot(kk, (-1 + np.sqrt(1 + 4 * a * g)) / (2 * a) * 1000, color='k', lw=0.9, label='Kane')
    mp = el['[100]']['windows']['3']['m_anchored']
    ax.plot(kk, bm.H2M * kk ** 2 / mp * 1000, color=fs.GREY, lw=0.9, ls='--', label='parabola')
    ax.set_xlabel(r'$|k|$ (1/$\mathrm{\AA}$)')
    ax.set_ylabel(r'$E-E_\mathrm{CBM}$ (meV)')
    ax.set_xlim(0, 0.16)
    ax.set_ylim(0, 520)
    ax.legend(loc='upper left', handlelength=1.4, fontsize=6.5)
    fs.panel(ax, 'b', x=-0.32)
    # (c) top VBs near Gamma
    ax = fig.add_subplot(gs[2])
    no_g = int(bg['nelec'] / 2)
    e0 = bg['E'][0, no_g - 1]
    for j, (d, v) in enumerate((('[100]', (1, 0, 0)), ('[110]', (1, 1, 0)), ('[111]', (1, 1, 1)))):
        idx = bm.line_indices(bg['K'], v)
        k = np.linalg.norm(bg['K'][idx], axis=1)
        for n in range(no_g - 3, no_g):
            ax.plot(k, (bg['E'][idx, n] - e0) * 1000, ['-', '--', ':'][j], color=C[j], lw=0.9,
                    label=d if n == no_g - 1 else None)
    om = D['bulk']['hole_summary']['VBM_longitudinal_[100]']
    ax.plot([om['k0_invA']], [om['E0_minus_Gamma_meV']], 'o', mfc='white', mec='k', ms=4.5, zorder=5)
    ax.set_xlabel(r'$|k|$ (1/$\mathrm{\AA}$)')
    ax.set_ylabel(r'$E-E_\mathrm{VB}(\Gamma)$ (meV)')
    ax.set_xlim(0, 0.16)
    ax.legend(loc='lower left', handlelength=1.8, fontsize=6.5)
    fs.panel(ax, 'c', x=-0.36)
    bm.save(fig, 'BM1_bulk_bands')


def slab_axes(ax, job, title_t, xmax=0.31, ylo=-1.0, yhi_over_gap=1.2):
    d = R / job
    b = bm.read_bands(d / 'bands.out')
    s = bm.read_bands(d / 'scf.out')
    no = int(b['nelec'] / 2)
    rec = D['slabs'][title_t]
    ev = rec['VBM_eV']
    i100 = bm.line_indices(b['K'], (1, 0, 0))
    i110 = bm.line_indices(b['K'], (1, 1, 0))
    k100 = np.linalg.norm(b['K'][i100], axis=1)
    k110 = np.linalg.norm(b['K'][i110], axis=1)
    for n in range(max(0, no - 30), b['nb']):
        col = 'k' if n < no else fs.ACCENT2
        ax.plot(k100, b['E'][i100, n] - ev, color=col, lw=0.8)
        ax.plot(-k110, b['E'][i110, n] - ev, color=col, lw=0.8)
    # SCF grid points: +x side for k along x or y, -x side for the diagonal
    for j, k in enumerate(s['K']):
        kn = np.linalg.norm(k)
        if kn < 1e-9:
            continue
        diag = abs(k[0]) > 1e-6 and abs(k[1]) > 1e-6 and abs(np.degrees(np.arctan2(abs(k[1]), abs(k[0]))) - 45) < 5
        xs = -kn if diag else kn
        mk = 's' if (abs(k[1]) > 1e-6 and not diag) else 'o'
        for n in range(max(0, no - 30), s['nb']):
            col = 'k' if n < no else fs.ACCENT2
            ax.plot([xs], [s['E'][j, n] - ev], mk, ms=2.6, mfc='none', mec=col, mew=0.6)
    ax.axvline(0, color=fs.GREY, lw=0.5)
    # edges
    allv = [(np.linalg.norm(b['K'][i]), b['E'][i, no - 1]) for i in range(b['nk'])]
    vmax = rec['VBM_eV']
    cmin = rec['CBM_eV']
    ax.plot([0], [rec['VB_Gamma_eV'] - ev], 'o', mfc='white', mec='k', ms=4.5, zorder=5)
    if rec['VBM_minus_VBGamma_meV'] > 0.5:
        # off-Gamma VBM on the SCF grid: mark it
        jj = int(np.argmax(s['E'][:, no - 1]))
        kv = s['K'][jj]
        diag = abs(kv[0]) > 1e-6 and abs(kv[1]) > 1e-6 and abs(np.degrees(np.arctan2(abs(kv[1]), abs(kv[0]))) - 45) < 5
        ax.plot([-np.linalg.norm(kv) if diag else np.linalg.norm(kv)], [0.0], 'o', mfc='white', mec=fs.ACCENT, ms=5.5, mew=1.0, zorder=6)
    ax.plot([0], [cmin - ev], 'o', mfc='k', mec='k', ms=4.0, zorder=5)
    ax.annotate('', xy=(0.012, cmin - ev), xytext=(0.012, 0.0), arrowprops=dict(arrowstyle='<->', lw=0.8, color=fs.ACCENT))
    ax.set_xlim(-xmax, xmax)
    ax.set_ylim(ylo, rec['Eg_fundamental_eV'] + yhi_over_gap)
    ax.set_xticks([-0.3, -0.15, 0, 0.15, 0.3])
    ax.set_xticklabels(['0.3', '', r'$\bar\Gamma$', '', '0.3'])


def fig_slabs():
    fig, axs = plt.subplots(1, 4, figsize=(fs.FULL_W, 2.9), sharey=False)
    for j, (lab, job) in enumerate((('0.51', 'slabL1_relax_v2'), ('0.75', 'slabL2_relax_v2'), ('1.0', 'slab1r_final_cpu'),
                                    ('2.0', 'slab2_relax_c2'))):
        ax = axs[j]
        slab_axes(ax, job, lab)
        ax.set_xlabel(r'$k_{[110]}$ | $k_{[100]}$ (1/$\mathrm{\AA}$)', fontsize=7.5)
        if j == 0:
            ax.set_ylabel(r'$E-E_\mathrm{VBM}$ (eV)')
        fs.panel(ax, 'abcd'[j], x=-0.18)
    fig.subplots_adjust(wspace=0.38)
    bm.save(fig, 'BM2_slab_bands')


def fig_wbulk():
    bg = bm.read_bands(q.BULK / 'bands_gamma.out')
    nop = int(bg['nelec'] / 2)
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_W, 2.9), sharey=True)
    for j, (site, job) in enumerate((('8b', 'iwo_W8b'), ('24d', 'iwo_W24d'))):
        ax = axs[j]
        b = bm.read_bands(R / job / 'bands.out')
        rec = D['W_bulk'][site]
        ef = rec['E_F_eV']['value']
        cb = rec['host_CB_band'] - 1
        vb = rec['VB_top_band'] - 1
        segs = []
        i110 = bm.line_indices(b['K'], (1, 1, 0))
        i100 = bm.line_indices(b['K'], (1, 0, 0))
        i111 = bm.line_indices(b['K'], (1, 1, 1))
        k110 = np.linalg.norm(b['K'][i110], axis=1)
        k100 = np.linalg.norm(b['K'][i100], axis=1)
        k111 = np.linalg.norm(b['K'][i111], axis=1)
        gap = 0.06
        x110 = -k110
        x100 = k100
        x111 = k100[-1] + gap + k111
        for n in range(max(0, vb - 25), b['nb']):
            col = 'k' if n <= vb else (fs.ACCENT2 if n == cb else C[2])
            for idx, xx in ((i110, x110), (i100, x100), (i111, x111)):
                ax.plot(xx, b['E'][idx, n] - ef, color=col, lw=0.8)
        # pure bulk CB aligned at the host CB minimum
        for v, xx in (((1, 1, 0), None), ((1, 0, 0), None), ((1, 1, 1), None)):
            idx = bm.line_indices(bg['K'], v)
            kk = np.linalg.norm(bg['K'][idx], axis=1)
            xp = -kk if v == (1, 1, 0) else (kk if v == (1, 0, 0) else k100[-1] + gap + kk)
            ax.plot(xp, bg['E'][idx, nop] - bg['E'][0, nop] + b['E'][0, cb] - ef, color=fs.GREY, lw=0.9, ls='--')
        ax.axhline(0, color=fs.ACCENT, lw=0.7, ls=':')
        ax.axvline(0, color=fs.GREY, lw=0.5)
        ax.axvline(k100[-1] + gap, color=fs.GREY, lw=0.5)
        ax.plot([0], [b['E'][0, cb] - ef], 'o', mfc=fs.ACCENT2, mec=fs.ACCENT2, ms=4)
        ax.plot([0], [b['E'][0, vb] - ef], 'o', mfc='white', mec='k', ms=4.5)
        ax.set_xticks([-0.15, 0, k100[-1], k100[-1] + gap, k100[-1] + gap + 0.15])
        ax.set_xticklabels(['[110]', r'$\Gamma$', '[100]', r'$\Gamma$', '[111]'], fontsize=7)
        ax.tick_params(axis='x', which='minor', bottom=False, top=False)
        ax.set_xlim(-0.155, k100[-1] + gap + 0.155)
        ax.set_ylim(-3.2, 1.0)
        if j == 0:
            ax.set_ylabel(r'$E-E_\mathrm{F}$ (eV)')
        fs.panel(ax, 'ab'[j], x=-0.13 if j == 0 else -0.06)
    fig.subplots_adjust(wspace=0.12)
    bm.save(fig, 'BM3_W_bulk_bands')


def fig_gridonly():
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_W, 2.7))
    # (a) W slabs vs pure twins: host CB, VB top, W-rich band; E - E_CB(Gamma) of each cell
    ax = axs[0]
    for j, (lab, wjob, pjob) in enumerate((('1 nm', 'iwo_slab1_final_cpu', 'slab1r_final_cpu'), ('2 nm', 'iwo_slab2_final_cpu', 'slab2_relax_c2'))):
        bw = bm.read_bands(R / wjob / 'scf.out')
        bp = bm.read_bands(R / pjob / 'scf.out')
        npure = int((bw['nelec'] - 1) / 2)
        kw = np.linalg.norm(bw['K'], axis=1)
        kp = np.linalg.norm(bp['K'], axis=1)
        ax.plot(kw, bw['E'][:, npure - 1] - bw['E'][0, npure - 1], 'o', color=C[j], ms=4, mfc='none', label=f'W {lab}')
        ax.plot(kp, bp['E'][:, npure] - bp['E'][0, npure], 'x', color=C[j], ms=4, label=f'pure {lab}')
    ax.set_xlabel(r'$|k|$ (1/$\mathrm{\AA}$)')
    ax.set_ylabel(r'$E_\mathrm{CB}(k)-E_\mathrm{CB}(\Gamma)$ (eV)')
    ax.legend(loc='upper left', fontsize=6.5)
    fs.panel(ax, 'a', x=-0.25)
    # (b) bulk HSE vs PBE: CB and VB top relative to VB(Gamma)
    ax = axs[1]
    for j, (lab, p) in enumerate((('PBE (PAW)', q.BULK / 'vcrelax_ecut71_k3.out'), ('PBE (NC)', R / 'nc_pbe_bulk_e80/scf.out'),
                                  ('HSE06 q1', R / 'nc_hse_bulk_e80/scf.out'), ('HSE06 q3', R / 'nc_hse_bulk_q3_f160_e80/scf.out'))):
        b = bm.read_bands(p)
        no = int(b['nelec'] / 2)
        k = np.linalg.norm(b['K'], axis=1)
        mk = ['o', 'x', 's', '^'][j]
        ax.plot(k, b['E'][:, no] - b['E'][0, no - 1], mk, color=C[j], ms=3.8, mfc='none', label=lab)
        ax.plot(k, b['E'][:, no - 1] - b['E'][0, no - 1], mk, color=C[j], ms=3.8, mfc='none')
    ax.set_xlabel(r'$|k|$ (1/$\mathrm{\AA}$)')
    ax.set_ylabel(r'$E-E_\mathrm{VB}(\Gamma)$ (eV)')
    ax.legend(loc='upper left', fontsize=6.0)
    fs.panel(ax, 'b', x=-0.25)
    # (c) 1 nm slab HSE vs PBE
    ax = axs[2]
    for j, (lab, p) in enumerate((('PBE (PAW)', R / 'slab1r_final_cpu/scf.out'), ('PBE (NC)', R / 'nc_pbe_slab1_e80/scf.out'),
                                  ('HSE06', R / 'nc_hse_slab1_f160_e80/scf.out'))):
        b = bm.read_bands(p)
        no = int(b['nelec'] / 2)
        k = np.linalg.norm(b['K'], axis=1)
        mk = ['o', 'x', 's'][j]
        ax.plot(k, b['E'][:, no] - b['E'][0, no - 1], mk, color=C[j], ms=3.8, mfc='none', label=lab)
        ax.plot(k, b['E'][:, no - 1] - b['E'][0, no - 1], mk, color=C[j], ms=3.8, mfc='none')
    ax.set_xlabel(r'$|k|$ (1/$\mathrm{\AA}$)')
    ax.set_ylabel(r'$E-E_\mathrm{VB}(\bar\Gamma)$ (eV)')
    ax.set_ylim(-0.3, 4.9)
    ax.legend(loc='upper left', fontsize=6.0)
    fs.panel(ax, 'c', x=-0.25)
    fig.subplots_adjust(wspace=0.5)
    bm.save(fig, 'BM4_scf_grid_only')


def fig_windows():
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_W, 2.6))
    ax = axs[0]
    for j, d in enumerate(('[100]', '[110]', '[111]')):
        w = D['bulk']['electron'][d]['windows']
        E = [w[n]['Emax_meV'] for n in w]
        ax.plot(E, [w[n]['m_anchored'] for n in w], ['o-', 's--', '^:'][j], color=C[j], ms=3.5, mfc='none', lw=0.9, label=d)
    ax.axhline(D['bulk']['electron_summary']['m_dos'], color='k', lw=0.8)
    ax.set_xscale('log')
    ax.set_xticks([20, 50, 100, 200, 500])
    ax.set_xticklabels(['20', '50', '100', '200', '500'])
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlabel(r'window $E_\mathrm{max}$ (meV)')
    ax.set_ylabel(r'$m^*_e$ ($m_0$)')
    ax.legend(loc='upper left', fontsize=6.5)
    fs.panel(ax, 'a', x=-0.3)
    ax = axs[1]
    for j, lab in enumerate(('0.51', '0.75', '1.0', '2.0')):
        w = D['slabs'][lab]['electron']['[100]']['windows']
        E = [w[n]['Emax_meV'] for n in w]
        m = np.array([w[n]['m_anchored'] for n in w])
        m0 = D['slabs'][lab]['electron_summary']['m_edge_[100]']
        ax.plot(E, m / m0, 'o-', color=C[j], ms=3.5, mfc='none', lw=0.9, label=f'{lab} nm')
    w = D['bulk']['electron']['[100]']['windows']
    ax.plot([w[n]['Emax_meV'] for n in w], np.array([w[n]['m_anchored'] for n in w]) / D['bulk']['electron_summary']['m_edge_by_dir']['[100]'],
            'k^--', ms=3.5, mfc='none', lw=0.9, label='bulk')
    ax.axhline(1, color=fs.GREY, lw=0.6)
    ax.set_xscale('log')
    ax.set_xlabel(r'window $E_\mathrm{max}$ (meV)')
    ax.set_ylabel(r'$m^*_\mathrm{window}/m^*_\mathrm{edge}$')
    ax.legend(loc='upper left', fontsize=6.0)
    fs.panel(ax, 'b', x=-0.3)
    ax = axs[2]
    for j, lab in enumerate(('0.51', '0.75', '1.0', '2.0')):
        s = D['slabs'][lab]
        top = str(s['n_occ'])
        for dd, ls in (('[100]', '-'), ('[110]', '--')):
            w = s['hole'][top][dd]['windows']
            E = [abs(w[n]['Emax_meV']) for n in w]
            m = [w[n]['m_anchored'] for n in w]
            ax.plot(E, m, 'o' + ls, color=C[j], ms=3.2, mfc='white' if not s['hole_verdict']['meaningful'] else C[j], lw=0.8,
                    label=f'{lab} nm' if dd == '[100]' else None)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_ylim(0.8, 300)
    ax.set_xlabel(r'$|\Delta E|_\mathrm{max}$ (meV)')
    ax.set_ylabel(r'$m^*_h$ ($m_0$)')
    ax.legend(loc='upper right', fontsize=5.8, ncol=2, columnspacing=0.8, handlelength=1.2)
    fs.panel(ax, 'c', x=-0.3)
    fig.subplots_adjust(wspace=0.55)
    bm.save(fig, 'BM5_mass_windows')


def fig_mass_thickness():
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_W, 2.6))
    t = np.array([T_LAB[l] for l in ('0.51', '0.75', '1.0', '2.0')])
    me = np.array([D['slabs'][l]['electron_summary']['tensor_2d']['m_dos_2d'] for l in ('0.51', '0.75', '1.0', '2.0')])
    m4 = np.array([D['slabs'][l]['electron_summary']['m_4pt_intercept_[100]'] for l in ('0.51', '0.75', '1.0', '2.0')])
    mb = D['bulk']['electron_summary']['m_dos']
    ax = axs[0]
    ax.plot(t[1:], me[1:], 'o', color=C[0], ms=4.5, label='PBE band edge')
    ax.plot(t[:1], me[:1], 'o', color=C[0], ms=4.5, mfc='white')
    ax.plot(t, m4, 's', color=C[1], ms=3.5, mfc='none', label='PBE 4-pt parabola')
    ax.axhline(mb, color=C[0], lw=0.8, ls='--')
    for lab, wl in (('1 nm', 0.9303), ('2 nm', 1.9623)):
        g = D['W_slabs'][lab]
        ax.errorbar([wl * 1.04], [g['m_edge_estimate_x']], yerr=[[g['m_edge_estimate_x'] - g['estimate_range'][0]],
                    [g['estimate_range'][1] - g['m_edge_estimate_x']]], fmt='D', color=C[2], ms=3.5, mfc='none', lw=0.8,
                    label='W slab (est.)' if lab == '1 nm' else None)
    wbm = np.mean([D['W_bulk'][s]['electron_summary']['m_dos'] for s in ('8b', '24d')])
    ax.axhline(wbm, color=C[2], lw=0.8, ls=':')
    h1 = D['HSE']['slab1_NCPBE_vs_HSE']
    ax.errorbar([0.9303 * 0.96], [h1['m_edge_estimate_x']], yerr=[[h1['m_edge_estimate_x'] - h1['estimate_range'][0]],
                [h1['estimate_range'][1] - h1['m_edge_estimate_x']]], fmt='v', color=C[3], ms=3.8, mfc='none', lw=0.8, label='HSE06 (est.)')
    lin = ([0.95, 1.98], [0.30, 0.23])
    ax.plot(*lin, 'x', color='k', ms=4.5, label='Lin 2022 (PBE)')
    ax.set_xscale('log')
    ax.set_xlabel(r'$t_\mathrm{HH}$ (nm)')
    ax.set_ylabel(r'$m^*_e$ ($m_0$)')
    ax.set_xticks([0.5, 1, 2])
    ax.set_xticklabels(['0.5', '1', '2'])
    ax.set_xlim(0.4, 2.4)
    ax.legend(loc='upper right', fontsize=5.4, handlelength=1.0, borderaxespad=0.3)
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    fs.panel(ax, 'a', x=-0.3)
    ax = axs[1]
    dm = me - mb
    ax.plot(t[1:], dm[1:], 'o', color=C[0], ms=4.5)
    ax.plot(t[:1], dm[:1], 'o', color=C[0], ms=4.5, mfc='white')
    f = bm.power_law(t[1:], dm[1:])
    tt = np.linspace(0.4, 15, 200)
    ax.plot(tt, bm.law(f, tt), color=C[0], lw=0.9)
    cfg = bm.load_parent('f06_confinement_laws')['config']['V3']['dm']
    ax.plot(tt, cfg['a'] * tt ** (-cfg['p']), color=fs.GREY, lw=0.9, ls='--')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'$t_\mathrm{HH}$ (nm)')
    ax.set_ylabel(r'$\Delta m^*_e$ ($m_0$)')
    fs.panel(ax, 'b', x=-0.3)
    ax = axs[2]
    nvb = D['bulk']['Nv']['conv80_k4_HL']['m_dos_equiv']
    mh = [D['slabs'][l]['Nv']['m_dos_equiv_2d'] for l in ('0.51', '0.75', '1.0', '2.0')]
    ax.plot(t, mh, 'o', color=C[1], ms=4.5, mfc='none')
    ax.axhline(nvb, color=C[1], lw=0.8, ls='--')
    for j, l in enumerate(('0.51', '0.75', '1.0', '2.0')):
        s = D['slabs'][l]
        if s['hole_verdict']['meaningful']:
            hs = s['hole_summary']
            ax.plot([t[j]], [hs['anchored_by_window_[100]']['3']], '^', color='k', ms=4)
            ax.plot([t[j]], [hs['anchored_by_window_[110]']['3']], 'v', color='k', ms=4)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'$t_\mathrm{HH}$ (nm)')
    ax.set_ylabel(r'$m^*_h$ ($m_0$)')
    fs.panel(ax, 'c', x=-0.3)
    for a_ in axs[1:]:
        a_.set_xticks([0.5, 1, 2, 5, 10])
        a_.set_xticklabels(['0.5', '1', '2', '5', '10'])
        a_.xaxis.set_minor_formatter(plt.NullFormatter())
        a_.yaxis.set_minor_formatter(plt.NullFormatter())
    axs[1].set_xlim(0.4, 15)
    axs[2].set_xlim(0.4, 2.5)
    axs[2].set_yticks([2, 5, 10, 20, 50])
    axs[2].set_yticklabels(['2', '5', '10', '20', '50'])
    fig.subplots_adjust(wspace=0.55)
    bm.save(fig, 'BM6_masses_thickness')


if __name__ == '__main__':
    fig_bulk()
    fig_slabs()
    fig_wbulk()
    fig_gridonly()
    fig_windows()
    fig_mass_thickness()
