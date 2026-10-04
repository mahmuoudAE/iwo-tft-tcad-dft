"""Figures of the DFT chapter (13_dft.tex). Every number is read from the Quantum ESPRESSO outputs in PKG/qe_workflow.
Run: python tools/make_dft_figures.py   (writes figures/dft_*.pdf)
"""
import glob
import re
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

REPORT = Path(__file__).resolve().parents[1]
QE = REPORT.parent / 'qe_workflow'
B, R = QE / 'bulk_In2O3_protocol', QE / 'cern_htcondor' / 'results'
OUT = REPORT / 'figures'
RY, BOHR, H2M = 13.605693122994, 0.529177210903, 3.80998212
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
                     'mathtext.fontset': 'stix', 'font.size': 9, 'axes.linewidth': 0.7, 'lines.linewidth': 1.1,
                     'xtick.direction': 'in', 'ytick.direction': 'in', 'savefig.bbox': 'tight'})
C1, C2, C3, C4 = '#1f4e79', '#b5442c', '#4d7c0f', '#7a5195'


def eig(path, nocc, extra=8):
    t = Path(path).read_text(errors='replace')
    alat = float(re.search(r'lattice parameter \(alat\)\s+=\s+([\d.]+)', t).group(1)) * BOHR
    bl = re.findall(r'k =\s*([-\d. ]+?)\s*\(\s*\d+ PWs\)\s+bands \(ev\):\s+(.*?)(?=\n\s*\n\s*(?:k =|highest|the Fermi|Writing|occupation)|\n\s*\n\s*\n)', t, re.S)
    ks = np.array([[float(x) for x in re.findall(r'-?\d+\.\d+', k.replace('-', ' -'))][:3] for k, _ in bl]) * 2 * np.pi / alat
    ev = np.array([[float(x) for x in re.findall(r'-?\d+\.\d+', e.replace('-', ' -'))][:nocc + extra] for _, e in bl])
    return ks, ev


def gap(path):
    m = re.findall(r'highest occupied, lowest unoccupied level \(ev\):\s+(-?[\d.]+)\s+(-?[\d.]+)', Path(path).read_text(errors='replace'))
    return float(m[-1][1]) - float(m[-1][0]), float(m[-1][0]), float(m[-1][1])


def slab_mass(d):
    """In-plane CB mass of a slab bands run: Gamma + the first 10 points along [100], parabola on |k| <= 0.05 1/A."""
    t = (d / 'bands.out').read_text(errors='replace')
    nocc = int(float(re.search(r'number of electrons\s+=\s+([\d.]+)', t).group(1))) // 2
    ks, ev = eig(d / 'bands.out', nocc, 2)
    k = np.linalg.norm(ks[:11], axis=1); e = ev[:11, nocc] - ev[0, nocc]; s = k <= 0.0501
    return H2M / np.polyfit(k[s] ** 2, e[s], 1)[0]


def fig_bands():
    ks, ev = eig(B / 'bands_path.out', 176, 10)
    step = np.linalg.norm(np.diff(ks, axis=0), axis=1)
    jump = step > 0.3
    d = np.concatenate([[0], np.cumsum(np.where(jump, 0, step))])
    # segment boundaries from the crystal_b card (points per segment)
    card = (B / 'bands_path.in').read_text().split('K_POINTS crystal_b')[1].split('\n')[2:10]
    n = [int(l.split()[-1]) for l in card if l.strip()]
    idx = np.concatenate([[0], np.cumsum(n[:-1])]).astype(int)
    labels = [r'$\Gamma$', 'H', 'N', r'$\Gamma$', 'P', 'H|P', 'N']
    ticks = [d[min(i, len(d) - 1)] for i in idx]
    ticks = [ticks[0], ticks[1], ticks[2], ticks[3], ticks[4], ticks[5], ticks[7]]
    vbm = ev[:, 175].max()
    fig, ax = plt.subplots(figsize=(4.6, 3.3))
    for b in range(ev.shape[1]):
        ax.plot(d, ev[:, b] - vbm, color=C1 if b < 176 else C2, lw=0.8)
    for x in ticks:
        ax.axvline(x, color='0.75', lw=0.5)
    ax.axhline(0, color='0.5', lw=0.5, ls=':')
    ax.set_xticks(ticks); ax.set_xticklabels(labels); ax.set_xlim(d[0], d[-1]); ax.set_ylim(-2.5, 4.0)
    ax.set_ylabel('Energy relative to VBM (eV)')
    g = ev[:, 176].min() - vbm
    ax.text((ticks[1] + ticks[2]) / 2, 0.45, f'PBE, a = 10.306 A\n$E_g$ = {g:.3f} eV', ha='center', va='center', fontsize=8,
            bbox=dict(facecolor='white', edgecolor='none', pad=1.5))
    fig.savefig(OUT / 'dft_bulk_bands.pdf'); plt.close(fig)


def fig_convergence():
    cut, k = [], []
    for f in sorted(B.glob('scf_ecut*_k*.out')):
        m = re.match(r'scf_ecut(\d+)_k(\d)', f.stem)
        t = f.read_text(errors='replace')
        e = float(re.findall(r'^!\s+total energy\s+=\s+([-\d.]+)', t, re.M)[-1])
        p = float(re.findall(r'P=\s*([-\d.]+)', t)[-1])
        g = gap(f)[0]
        rec = (int(m.group(1)), int(m.group(2)), e, p, g)
        (cut if rec[1] == 3 else k).append(rec)
        if rec[0] == 71 and rec[1] == 3:
            k.append(rec)
    cut.sort(); k.sort(key=lambda r: r[1])
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 2.5))
    ec = np.array([r[0] for r in cut]); de = (np.array([r[2] for r in cut]) - cut[-1][2]) * 1000 / 40
    axs[0].plot(ec, de, 'o-', color=C1, ms=3.5, label='$\\Delta E$/atom (mRy)')
    axs[0].plot(ec, np.array([r[3] for r in cut]) - cut[-1][3], 's--', color=C2, ms=3.5, label='$\\Delta P$ (kbar)')
    axs[0].axhspan(-1, 1, color='0.9'); axs[0].axvline(71, color='0.6', lw=0.6, ls=':')
    axs[0].set_xlabel('ecutwfc (Ry), k = 3x3x3'); axs[0].set_ylabel('difference to 85 Ry'); axs[0].legend(fontsize=7, frameon=False)
    kk = np.array([r[1] for r in k]); dk = (np.array([r[2] for r in k]) - k[-1][2]) * 1000 / 40
    axs[1].plot(kk, dk, 'o-', color=C1, ms=3.5, label='$\\Delta E$/atom (mRy)')
    axs[1].plot(kk, (np.array([r[4] for r in k]) - k[-1][4]) * 1000, '^-', color=C3, ms=3.5, label='$\\Delta E_g$ (meV)')
    axs[1].axhspan(-1, 1, color='0.9'); axs[1].set_ylim(-11, 11)
    axs[1].axhline(10, color=C3, lw=0.6, ls=':'); axs[1].axhline(-10, color=C3, lw=0.6, ls=':')
    axs[1].text(4, 9.0, 'gap criterion 10 meV', ha='right', fontsize=6.5, color=C3); axs[1].set_xticks([2, 3, 4]); axs[1].set_xticklabels(['2x2x2', '3x3x3', '4x4x4'])
    axs[1].set_xlabel('k-point grid, 71 Ry'); axs[1].set_ylabel('difference to 4x4x4'); axs[1].legend(fontsize=7, frameon=False)
    fig.tight_layout(); fig.savefig(OUT / 'dft_convergence.pdf'); plt.close(fig)


def fig_planar():
    d = R / 'slab1r_final_cpu'
    z, v, vm = np.loadtxt(next(d.glob('*_avg.dat')), usecols=(0, 1, 2), unpack=True)
    z = z * BOHR; v = v * RY; vm = vm * RY
    c = z.max() + (z[1] - z[0]); evac = v[np.minimum(z, c - z) < 2.0].mean()
    g, vb, cb = gap(d / 'scf.out')
    fig, ax = plt.subplots(figsize=(5.4, 2.8))
    ax.plot(z, v - evac, color='0.55', lw=0.6, label='planar average')
    ax.plot(z, vm - evac, color=C1, lw=1.1, label='macroscopic average')
    ax.axhline(0, color='k', lw=0.6); ax.axhline(cb - evac, color=C2, lw=1.0, ls='--'); ax.axhline(vb - evac, color=C3, lw=1.0, ls='--')
    ax.text(z.max() * 0.99, 0.15, '$E_{\\mathrm{vac}}$', ha='right', fontsize=8)
    ax.text(z.max() * 0.99, cb - evac + 0.15, f'CBM: EA = {evac - cb:.2f} eV', ha='right', fontsize=8, color=C2)
    ax.text(z.max() * 0.99, vb - evac - 0.9, f'VBM: IP = {evac - vb:.2f} eV', ha='right', fontsize=8, color=C3)
    ax.set_xlim(0, z.max()); ax.set_xlabel('z (A)'); ax.set_ylabel('Energy relative to $E_{\\mathrm{vac}}$ (eV)')
    ax.legend(fontsize=7, frameon=False, loc='lower left')
    fig.savefig(OUT / 'dft_planar_potential.pdf'); plt.close(fig)


def fig_confinement():
    t = np.linspace(0.8, 6.5, 300)
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.7))
    ax = axs[0]
    ax.plot(t, 0.9205 * t ** -1.3815, color='0.4', lw=1.0, label='TCAD law (fit to proxies)')
    ax.plot([0.95, 1.98], [0.94, 0.33], 's', color=C2, ms=5, mfc='white', label='Lin 2022 (PBE)')
    ax.plot([1.5], [0.6], 'D', color=C4, ms=4.5, mfc='white', label='Si 2021 ($\\Delta E_c$, PBE, on Al$_2$O$_3$)')
    # thickness: H-H distance of the slab as built (0.99 and 2.02 nm), as for the published points
    tt = np.array([0.99, 2.02])
    pbe = np.array([gap(R / 'slab1r_final_cpu' / 'scf.out')[0], gap(R / 'slab2_relax_c2' / 'scf.out')[0]]) - 0.8887
    ax.plot(tt, pbe, 'o', color=C1, ms=5.5, label='this work, PBE')
    ax.errorbar(tt + 0.04, pbe * 1.085, yerr=[pbe * 0.025, pbe * 0.025], fmt='o', color=C3, ms=4, capsize=2, label='this work, HSE-corrected')
    ax.axvline(2.0, color='0.8', lw=0.6, ls=':'); ax.text(2.12, 0.95, '2.0 nm device', fontsize=7, color='0.4')
    ax.set_xlabel('film thickness t (nm)'); ax.set_ylabel('$\\Delta E_g$ (eV)'); ax.set_ylim(0, 1.25); ax.legend(fontsize=6.5, frameon=False)
    ax = axs[1]
    ax.plot(t, 0.1311 * t ** -1.4121, color='0.4', lw=1.0, label='TCAD law, increment')
    ax.plot([0.95, 1.98, 3.52], [0.13, 0.06, 0.02], 's', color=C2, ms=5, mfc='white', label='Lin 2022 (PBE)')
    ax.plot(tt, [slab_mass(R / 'slab1r_final_cpu') - 0.1590, slab_mass(R / 'slab2_relax_c2') - 0.1590], 'o', color=C1, ms=5.5, label='this work, PBE')
    print(f'   confinement: dEg PBE {np.round(pbe, 4)} eV, dm* {[round(slab_mass(R / j) - 0.159, 4) for j in ("slab1r_final_cpu", "slab2_relax_c2")]} m0')
    ax.set_xlabel('film thickness t (nm)'); ax.set_ylabel('$\\Delta m^*$ ($m_0$)'); ax.set_ylim(0, 0.18); ax.legend(fontsize=6.5, frameon=False)
    fig.tight_layout(); fig.savefig(OUT / 'dft_confinement_vs_thickness.pdf'); plt.close(fig)


def fig_hse():
    vals = {k: gap(R / k / 'scf.out')[0] for k in ('nc_pbe_bulk_e80', 'nc_pbe_slab1_e80', 'nc_hse_bulk_f160_e80', 'nc_hse_slab1_f160_e80')}
    fig, ax = plt.subplots(figsize=(4.2, 2.7))
    x = np.arange(2); w = 0.34
    pb = [vals['nc_pbe_bulk_e80'], vals['nc_pbe_slab1_e80']]; hs = [vals['nc_hse_bulk_f160_e80'], vals['nc_hse_slab1_f160_e80']]
    ax.bar(x - w / 2, pb, w, color=C1, label='PBE'); ax.bar(x + w / 2, hs, w, color=C2, label='HSE06')
    for i in range(2):
        ax.text(x[i] - w / 2, pb[i] + 0.04, f'{pb[i]:.3f}', ha='center', fontsize=7)
        ax.text(x[i] + w / 2, hs[i] + 0.04, f'{hs[i]:.3f}', ha='center', fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels(['bulk (40 atoms)', '1 nm slab (96 atoms)']); ax.set_ylabel('Kohn-Sham gap at $\\Gamma$ (eV)')
    r = (hs[1] - hs[0]) / (pb[1] - pb[0])
    ax.text(0.02, 0.97, f'$\\Delta E_g$: PBE {pb[1] - pb[0]:.3f} eV, HSE06 {hs[1] - hs[0]:.3f} eV\nratio {r:.3f}',
            transform=ax.transAxes, va='top', fontsize=7.5)
    ax.set_ylim(0, 4.1); ax.legend(fontsize=7, frameon=False, loc='upper right', ncol=2)
    fig.savefig(OUT / 'dft_pbe_vs_hse.pdf'); plt.close(fig)


def pdos(d, prefix):
    tot = np.loadtxt(glob.glob(str(d / 'pdos' / f'{prefix}.pdos_tot'))[0], usecols=(0, 1))
    wd = np.loadtxt(sorted(glob.glob(str(d / 'pdos' / f'{prefix}.pdos_atm#*(W)_wfc#*(d)')))[0], usecols=(0, 1))
    ef = float(re.findall(r'the Fermi energy is\s+(-?[\d.]+)', (d / ('scf_k4.out' if (d / 'scf_k4.out').exists() else 'scf.out')).read_text(errors='replace'))[-1])
    return tot, wd, ef


def fig_wpdos():
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.6), sharey=False)
    for ax, (d, pre, title) in zip(axs, ((R / 'iwo_W24d', 'iwo_W24d', 'bulk, W on 24d (80 atoms)'),
                                         (R / 'iwo_slab1_final_cpu', 'iwo_slab1_final_cpu', '1 nm slab, W on central 24d'))):
        tot, wd, ef = pdos(d, pre)
        ax.fill_between(tot[:, 0] - ef, tot[:, 1] / tot[:, 1].max(), color='0.85', label='total DOS (scaled)')
        ax.plot(wd[:, 0] - ef, wd[:, 1] / wd[:, 1].max(), color=C2, label='W 5d PDOS (scaled)')
        ax.axvline(0, color='k', lw=0.6, ls=':'); ax.text(-0.08, 0.97, '$E_F$', fontsize=8, ha='right', va='top')
        ax.set_xlim(-3, 3); ax.set_ylim(0, 1.05); ax.set_title(title, fontsize=8.5)
        ax.set_xlabel('$E - E_F$ (eV)'); ax.set_yticks([])
    axs[0].legend(fontsize=6.5, frameon=False, loc='upper left')
    fig.tight_layout(); fig.savefig(OUT / 'dft_w_pdos.pdf'); plt.close(fig)


def fig_compute():
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 2.4))
    ax = axs[0]
    ax.barh(['CERN CPU\n(core-h)'], [5300], color=C1, label='productive')
    ax.barh(['CERN CPU\n(core-h)'], [3000], left=[5300], color='0.75', label='lost (fixed)')
    ax.set_xlabel('core-hours (CERN weighted, approx.)'); ax.legend(fontsize=7, frameon=False, loc='lower right')
    ax = axs[1]
    labels = ['16 CPU cores', '1 x H100 NVL']; vals = [76.0, 9.27]
    ax.bar(labels, vals, color=[C1, C2]); ax.set_ylabel('wall time (min)')
    for i, v in enumerate(vals):
        ax.text(i, v + 1.5, f'{v:.1f}', ha='center', fontsize=7.5)
    ax.set_ylim(0, max(vals) * 1.15)
    ax.set_title('1 nm slab SCF (96 atoms), identical result: 8.2x', fontsize=8)
    fig.tight_layout(); fig.savefig(OUT / 'dft_computing.pdf'); plt.close(fig)


S = QE / 'structures_v2' / 'relaxed_pbe'
STYLE = {'In': ('#8e7cc3', 1.00), 'O': ('#d62728', 0.62), 'H': ('#f2f2f2', 0.34), 'W': ('#1f77b4', 1.10)}


def side_view(ax, path, title, mark_w=False):
    """x-z projection of a slab (atoms drawn back to front by y); cell outline; H-H thickness and vacuum marked."""
    import json
    st = json.loads(Path(path).read_text())
    cell = np.array(st['cell_A']); pos = np.array(st['positions_A']); sym = st['symbols']
    order = np.argsort(pos[:, 1])
    for i in order:
        col, r = STYLE[sym[i]]
        ax.add_patch(plt.Circle((pos[i, 0] % cell[0, 0], pos[i, 2]), 0.42 * r, facecolor=col, edgecolor='k', lw=0.3,
                                zorder=3 if sym[i] != 'W' else 4))
        if mark_w and sym[i] == 'W':
            ax.add_patch(plt.Circle((pos[i, 0] % cell[0, 0], pos[i, 2]), 0.95, fill=False, edgecolor=C1, lw=1.2, zorder=5))
    a, c = cell[0, 0], cell[2, 2]
    ax.plot([0, a, a, 0, 0], [0, 0, c, c, 0], color='0.4', lw=0.6, ls='--')
    zh = pos[np.array(sym) == 'H', 2]
    ax.annotate('', (a + 0.8, zh.min()), (a + 0.8, zh.max()), arrowprops=dict(arrowstyle='<->', lw=0.7))
    ax.text(a + 1.1, (zh.min() + zh.max()) / 2, f'{(zh.max() - zh.min()) / 10:.2f} nm\n(H to H)', fontsize=6.5, va='center')
    ax.text(a + 1.1, zh.max() + (c - zh.max()) / 2, 'vacuum', fontsize=6.5, va='center', color='0.35')
    ax.text(a + 1.1, zh.min() / 2, 'vacuum', fontsize=6.5, va='center', color='0.35')
    ax.set_xlim(-0.8, a + 5.5); ax.set_ylim(-0.8, c + 0.8); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title, fontsize=8)


def fig_structures():
    fig, axs = plt.subplots(1, 3, figsize=(6.6, 4.6), gridspec_kw={'width_ratios': [1, 1, 1]})
    side_view(axs[0], S / 'slab1r_pure.json', '(a) 1 nm slab, relaxed\nIn$_{24}$O$_{48}$H$_{24}$, 96 atoms')
    side_view(axs[1], S / 'slab2_v25.json', '(b) 2 nm slab, as built\nIn$_{56}$O$_{96}$H$_{24}$, 176 atoms')
    side_view(axs[2], S / 'slab1r_W24d.json', '(c) 1 nm IWO slab, as built\nIn$_{23}$WO$_{48}$H$_{24}$', mark_w=True)
    hs = [plt.Line2D([], [], marker='o', ls='', mfc=STYLE[k][0], mec='k', mew=0.4, ms=5 * STYLE[k][1] + 2, label=k)
          for k in ('In', 'O', 'H', 'W')]
    fig.legend(handles=hs, loc='lower center', ncol=4, fontsize=7, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(OUT / 'dft_structures.pdf'); plt.close(fig)


def fig_mass():
    """Conduction band near Gamma and the parabolic fits that give m* (bulk: 3 directions; slab: in-plane)."""
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.8))
    rows = []
    for ax, (f, nocc, dirs, title) in zip(axs, ((B / 'bands_gamma.out', 176, ['[100]', '[110]', '[111]'], '(a) bulk In$_2$O$_3$'),
                                               (R / 'slab1_relax_gpu' / 'bands.out', 312, ['[100]', '[110]'], '(b) relaxed 1 nm slab, in plane'))):
        ks, ev = eig(f, nocc, 2)
        e0 = ev[0, nocc]
        kk = np.linspace(0, 0.155, 100)
        for n, (dname, col, mk) in enumerate(zip(dirs, (C1, C2, C3), ('o', 's', '^'))):
            idx = [0] + list(range(1 + 10 * n, 11 + 10 * n))
            k = np.linalg.norm(ks[idx], axis=1); e = ev[idx, nocc] - e0
            sel = k <= 0.0501
            c2 = np.polyfit(k[sel] ** 2, e[sel], 1)[0]
            m = H2M / c2
            rows.append((title, dname, m))
            ax.plot(k, e, mk, color=col, ms=3.5, mfc='white', label=f'{dname}: $m^*$ = {m:.3f} $m_0$')
            ax.plot(kk, c2 * kk ** 2, color=col, lw=0.8, ls='--')
        ax.axvspan(0, 0.05, color='0.92', zorder=0)
        ax.text(0.025, 0.95, 'fit window\n$|k| \\leq 0.05$', ha='center', va='top', fontsize=6.5, color='0.4', transform=ax.get_xaxis_transform())
        ax.set_xlim(0, 0.155); ax.set_ylim(0, None)
        ax.set_xlabel('$|k|$ (1/A) from $\\Gamma$'); ax.set_ylabel('$E - E_{\\mathrm{CBM}}$ (eV)')
        ax.set_title(title, fontsize=8.5); ax.legend(fontsize=6.5, frameon=False, loc='lower right')
    fig.tight_layout(); fig.savefig(OUT / 'dft_mass_fit.pdf'); plt.close(fig)
    for r in rows:
        print('   mass', r)


def scf_trace(path):
    t = Path(path).read_text(errors='replace')
    e = [float(x) for x in re.findall(r'^!\s+total energy\s+=\s+([-\d.]+)', t, re.M)]
    g = [float(b) - float(a) for a, b in re.findall(r'highest occupied, lowest unoccupied level \(ev\):\s+(-?[\d.]+)\s+(-?[\d.]+)', t)]
    f = [float(x) for x in re.findall(r'Total force =\s+([\d.]+)', t)]
    n = min(len(e), len(g))
    return np.array(e[:n]), np.array(g[:n]), np.array(f[:n])


def fig_relax():
    """1 nm slab vc-relax: energy, gap and total force at every SCF cycle (CPU steps, then the GPU continuation)."""
    ec, gc, fc = scf_trace(R / 'cpu_relax_snapshots' / 'slab1_relax_vcrelax.out')
    eg, gg, fg = scf_trace(R / 'slab1_relax_gpu' / 'vcrelax.out')
    e = np.concatenate([ec, eg]); g = np.concatenate([gc, gg]); fo = np.concatenate([fc, fg])
    x = np.arange(1, len(e) + 1)
    fig, axs = plt.subplots(1, 3, figsize=(6.8, 2.4))
    axs[0].semilogy(x, (e - e.min()) * RY + 1e-4, '.-', color=C1, ms=3, lw=0.8)
    axs[0].set_ylabel('$E - E_{\\mathrm{final}}$ (eV)')
    axs[1].plot(x, g, '.-', color=C2, ms=3, lw=0.8); axs[1].set_ylabel('Kohn-Sham gap (eV)')
    axs[2].semilogy(x, fo, '.-', color=C3, ms=3, lw=0.8); axs[2].set_ylabel('total force (Ry/bohr)')
    for ax in axs:
        ax.axvline(len(ec) + 0.5, color='0.6', lw=0.6, ls=':'); ax.set_xlabel('SCF cycle (one per geometry)')
    axs[1].text(len(ec) + 1.5, g.min() + 0.05, 'CPU | GPU', fontsize=6.5, color='0.4')
    axs[1].text(0.97, 0.05, f'start {g[0]:.3f} eV\nend {g[-1]:.3f} eV', transform=axs[1].transAxes, ha='right', fontsize=6.5)
    fig.tight_layout(); fig.savefig(OUT / 'dft_relaxation_history.pdf'); plt.close(fig)
    print(f'   relax: {len(ec)} CPU + {len(eg)} GPU SCF cycles; gap {g[0]:.4f} -> {g[-1]:.4f} eV; dE {(e[0] - e[-1]) * RY:.3f} eV')


def gamma_levels(path, nocc, extra):
    """Eigenvalues at Gamma (first k block) of an SCF or bands output: (all levels, VBM, CBM)."""
    ks, ev = eig(path, nocc, extra)
    g = int(np.argmin(np.linalg.norm(ks, axis=1)))
    return ev[g], ev[g, nocc - 1], ev[g, nocc]


def fig_levels():
    """Energy levels at Gamma near the gap: bulk vs unrelaxed vs relaxed 1 nm film (each relative to its VBM)."""
    cols = [('bulk\n(40 atoms)', B / 'bands_gamma.out', 176, 14),
            ('1 nm film\nas built', R / 'slab1_v25' / 'scf.out', 312, 16),
            ('1 nm film\nrelaxed', R / 'slab1r_final_cpu' / 'scf.out', 312, 16),
            ('2 nm film\nrelaxed', R / 'slab2_relax_c2' / 'scf.out', 664, 16)]
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    for i, (lab, f, nocc, extra) in enumerate(cols):
        ev, vbm, cbm = gamma_levels(f, nocc, extra)
        e = ev - vbm
        for n, x in enumerate(e):
            if -1.2 <= x <= 3.3:
                ax.plot([i - 0.32, i + 0.32], [x, x], color=C1 if n < nocc else C2, lw=0.9)
        ax.annotate('', (i + 0.40, 0), (i + 0.40, cbm - vbm), arrowprops=dict(arrowstyle='<->', lw=0.7))
        ax.text(i + 0.44, (cbm - vbm) / 2, f'{cbm - vbm:.3f} eV', fontsize=7, va='center')
        up = np.sort(e[e > cbm - vbm + 1e-6])
        print(f'   levels {lab!r}: gap at Gamma {cbm - vbm:.4f} eV; next CB levels {np.round(up[:2] - (cbm - vbm), 3)} eV above CBM')
    ax.axhline(0, color='0.6', lw=0.5, ls=':')
    ax.set_xticks(range(len(cols))); ax.set_xticklabels([c[0] for c in cols], fontsize=8)
    ax.set_xlim(-0.6, len(cols) - 0.1); ax.set_ylim(-1.2, 3.45)
    ax.set_ylabel('Energy at $\\Gamma$ relative to VBM (eV)')
    ax.plot([], [], color=C1, label='occupied (valence)'); ax.plot([], [], color=C2, label='empty (conduction)')
    ax.legend(fontsize=7, frameon=False, loc='upper left')
    fig.savefig(OUT / 'dft_levels.pdf'); plt.close(fig)


def vac_edges(d, nocc, extra=24):
    """Vacuum level and Gamma levels of a slab job (vacuum window: within 2 A of the cell boundary)."""
    z, v = np.loadtxt(next(d.glob('*_avg.dat')), usecols=(0, 1), unpack=True)
    c = z.max() + (z[1] - z[0])
    evac = v[np.minimum(z, c - z) * BOHR < 2.0].mean() * RY
    ev, vbm, cbm = gamma_levels(d / 'scf.out', nocc, extra)
    ef = re.findall(r'the Fermi energy is\s+(-?[\d.]+)', (d / 'scf.out').read_text(errors='replace'))
    return evac, ev, (float(ef[-1]) if ef else None)


def fig_alignment():
    """Band edges on the vacuum scale with the computed numbers: 1 nm film as built, relaxed, 2 nm relaxed, 1 nm with W."""
    fig, ax = plt.subplots(figsize=(6.6, 3.7))
    w = 0.62
    rows = []
    for i, (lab, d, nocc, extra) in enumerate((('1 nm, as built', R / 'slab1_v25', 312, 16),
                                               ('1 nm, relaxed', R / 'slab1r_final_cpu', 312, 16),
                                               ('2 nm, relaxed', R / 'slab2_relax_c2', 664, 16))):
        evac, ev, _ = vac_edges(d, nocc, extra)
        _, v0, c0 = gap(d / 'scf.out')                   # band edges over the whole k grid, as in the vacuum test
        vb, cb = v0 - evac, c0 - evac
        ax.add_patch(plt.Rectangle((i - w / 2, vb - 0.9), w, 0.9, color=C1, alpha=0.25, lw=0))
        ax.add_patch(plt.Rectangle((i - w / 2, cb), w, 0.9, color=C2, alpha=0.25, lw=0))
        ax.plot([i - w / 2, i + w / 2], [vb, vb], color=C1, lw=1.4); ax.plot([i - w / 2, i + w / 2], [cb, cb], color=C2, lw=1.4)
        ax.text(i, cb + 0.08, f'CBM\nEA = {-cb:.2f} eV', ha='center', va='bottom', fontsize=6.5)
        ax.text(i, vb - 0.08, f'VBM\nIP = {-vb:.2f} eV', ha='center', va='top', fontsize=6.5)
        ax.text(i, (vb + cb) / 2, f'$E_g$ = {cb - vb:.2f} eV', ha='center', va='center', fontsize=7)
        rows.append((lab, -cb, -vb))
    i = 3
    evac, ev, ef = vac_edges(R / 'iwo_slab1_final_cpu', 312, 24)
    vb, ws, hc = ev[311] - evac, ev[312] - evac, ev[313] - evac
    ax.add_patch(plt.Rectangle((i - w / 2, vb - 0.9), w, 0.9, color=C1, alpha=0.25, lw=0))
    ax.add_patch(plt.Rectangle((i - w / 2, hc), w, 0.9, color=C2, alpha=0.25, lw=0))
    ax.plot([i - w / 2, i + w / 2], [vb, vb], color=C1, lw=1.4); ax.plot([i - w / 2, i + w / 2], [hc, hc], color=C2, lw=1.4)
    ax.plot([i - w / 2, i + w / 2], [ws, ws], color=C4, lw=1.6)
    ax.plot([i - w / 2, i + w / 2], [ef - evac] * 2, color='k', lw=0.8, ls='--')
    ax.text(i + w / 2 + 0.03, hc + 0.05, 'host CB', fontsize=6.5, color=C2, va='bottom')
    ax.text(i + w / 2 + 0.03, ws - 0.10, 'W 5d state', fontsize=6.5, color=C4, va='top')
    ax.text(i - w / 2 - 0.03, ef - evac, '$E_F$ (dashed)', fontsize=6.5, va='center', ha='right')
    ax.text(i, vb - 0.08, f'VB top\n{vb:.2f} eV', ha='center', va='top', fontsize=6.5)
    ax.text(i, hc + 0.95, 'preliminary', ha='center', fontsize=6.5, style='italic', color='0.35')
    rows.append(('1 nm IWO', -ws, -vb, -hc, ef - evac))
    ax.axhline(0, color='k', lw=0.8); ax.text(3.55, 0.05, '$E_{\\mathrm{vac}}$', fontsize=8)
    ax.set_xticks([0, 1, 2, 3]); ax.set_xticklabels(['1 nm film\nas built', '1 nm film\nrelaxed', '2 nm film\nrelaxed',
                                                     '1 nm film\nwith W (In$_{23}$WO$_{48}$H$_{24}$)'], fontsize=7.5)
    ax.set_xlim(-0.55, 3.75); ax.set_ylim(-7.3, 0.4)
    ax.set_ylabel('Energy relative to the vacuum level (eV)')
    fig.savefig(OUT / 'dft_alignment.pdf'); plt.close(fig)
    for r in rows:
        print('   alignment', r)


def fig_lin_parity():
    """This work against Lin et al. 2022 (same recipe, PBE): energies, masses, lengths."""
    v = re.findall(r'new unit-cell volume =\s+[\d.]+ a\.u\.\^3 \(\s*([\d.]+) Ang\^3', (B / 'vcrelax_ecut71_k3.out').read_text(errors='replace'))
    a_bulk = (2 * float(v[-1])) ** (1 / 3)
    ks, ev = eig(B / 'bands_path.out', 176, 2); g_bulk = ev[:, 176].min() - ev[:, 175].max()
    g1 = gap(R / 'slab1r_final_cpu' / 'scf.out')[0]
    ks, ev = eig(B / 'bands_gamma.out', 176, 2)
    mb = np.mean([H2M / np.polyfit(np.linalg.norm(ks[ix], axis=1)[np.linalg.norm(ks[ix], axis=1) <= 0.0501] ** 2,
                                   (ev[ix, 176] - ev[0, 176])[np.linalg.norm(ks[ix], axis=1) <= 0.0501], 1)[0]
                  for ix in ([0] + list(range(1 + 10 * n, 11 + 10 * n)) for n in range(3))])
    ks, ev = eig(R / 'slab1_relax_gpu' / 'bands.out', 312, 2)
    k = np.linalg.norm(ks[:11], axis=1); e = ev[:11, 312] - ev[0, 312]; s = k <= 0.0501
    m1 = H2M / np.polyfit(k[s] ** 2, e[s], 1)[0]
    cell = re.findall(r'CELL_PARAMETERS \(angstrom\)\s*\n\s*([-\d.]+)\s+[-\d.]+\s+[-\d.]+\s*\n\s*[-\d.]+\s+([-\d.]+)',
                      (R / 'slab1_relax_gpu' / 'vcrelax.out').read_text(errors='replace'))
    a1 = (float(cell[-1][0]) + float(cell[-1][1])) / 2
    rows = [('bulk lattice constant $a$ (A)', 10.30, a_bulk, 'p. 21542'),
            ('1 nm film, in-plane $a$ (A)', 10.31, a1, 'p. 21542, mean of 10.26 and 10.36'),
            ('bulk gap (eV)', 0.94, g_bulk, 'p. 21542'),
            ('1 nm film gap (eV)', 1.88, g1, 'p. 21542'),
            ('confinement shift $\\Delta E_g$, 1 nm (eV)', 0.94, g1 - g_bulk, 'p. 21542'),
            ('bulk mass $m^*$ ($m_0$)', 0.17, mb, 'p. 21540'),
            ('1 nm film mass $m^*$ ($m_0$)', 0.30, m1, 'p. 21540'),
            ('mass increment $\\Delta m^*$, 1 nm ($m_0$)', 0.13, m1 - mb, 'p. 21540')]
    g2, m2 = gap(R / 'slab2_relax_c2' / 'scf.out')[0], slab_mass(R / 'slab2_relax_c2')
    rows += [('2 nm film gap (eV)', 1.27, g2, 'p. 21542'),
             ('confinement shift $\\Delta E_g$, 2 nm (eV)', 0.33, g2 - g_bulk, 'p. 21542, 1.27 - 0.94'),
             ('2 nm film mass $m^*$ ($m_0$)', 0.23, m2, 'p. 21540'),
             ('mass increment $\\Delta m^*$, 2 nm ($m_0$)', 0.06, m2 - mb, 'p. 21540, 0.23 - 0.17')]
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.axvspan(-5, 5, color='0.92', zorder=0); ax.axvline(0, color='0.4', lw=0.7)
    ax.axhline(3.5, color='0.75', lw=0.5, ls=':')             # rows below: 2 nm
    d2 = 100 * 0.1 / 0.33                                     # same criterion at 1.98 nm (PROTOCOL_CERN item 7): +-30 %, clipped
    ax.plot([-27, 11], [2, 2], color=C3, lw=2.2, alpha=0.5, solid_capstyle='butt', zorder=1)
    ax.text(-26.5, 2.32, f'criterion (0.1 eV = $\\pm${d2:.0f} %, clipped)', fontsize=6, color=C3)
    dg = 100 * 0.1 / 0.94                                     # pre-registered tolerance: dEg within 0.1 eV
    y_dg = len(rows) - 1 - 4
    ax.plot([-dg, dg], [y_dg, y_dg], color=C3, lw=2.2, alpha=0.5, solid_capstyle='butt', zorder=1)
    for n, (name, lin, ours, page) in enumerate(rows):
        y = len(rows) - 1 - n
        d = 100 * (ours / lin - 1)
        ax.plot(d, y, 'o', color=C1, ms=5, zorder=3)
        fmt = '.3f' if lin < 5 else '.3f'
        ax.text(13.0, y, f'{ours:{fmt}} vs {lin:g}   ({d:+.1f} %)', va='center', fontsize=7)
        print(f'   vs Lin: {name}: this work {ours:.4f}, Lin {lin} ({page}) -> {d:+.1f} %')
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=7.5)
    ax.set_xlim(-27, 34); ax.set_xticks([-25, -20, -15, -10, -5, 0, 5, 10])
    ax.set_xlabel('difference, this work relative to Lin et al. 2022 (%)')
    ax.text(13.0, len(rows) - 0.35, 'this work vs Lin et al.', fontsize=7, style='italic', va='bottom')
    ax.text(-dg, y_dg + 0.32, 'criterion', fontsize=6, color=C3)
    ax.set_ylim(-0.6, len(rows) - 0.2)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    fig.savefig(OUT / 'dft_lin_parity.pdf'); plt.close(fig)

def fig_timeline():
    """Every CERN job: queued / running (CPU, GPU) / held, from the monitor log (2026-09-27 09:02Z, 30 min), the status
    history (from 2026-09-28 14:20Z, 5-10 min) and the driver logs (exact run intervals of jobs that returned output)."""
    import json
    from datetime import datetime, timezone

    def ts(s):
        return datetime.strptime(s.strip()[:20], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp()

    def row(name):
        n = re.sub(r'(__cpu|_refetch|_partial|_checkpoint)$', '', name)
        n = re.sub(r'(_x\d|_c\d|_gpu\d*)+$', '', n)
        table = [(r'^slab1_v', '1 nm, vacuum test'), (r'^slab2_v25', '2 nm, unrelaxed SCF'), (r'^slab1_relax', '1 nm relaxation'),
                 (r'^slab2_relax', '2 nm relaxation'), (r'^iwo_W8b', 'W on 8b (bulk)'), (r'^iwo_W24d', 'W on 24d (bulk)'),
                 (r'^gpu_bench', 'GPU benchmark'), (r'^slab1r_final', '1 nm final (CPU)'), (r'^iwo_slab1_W24d', '1 nm IWO relaxation'),
                 (r'^iwo_slab1_final', '1 nm IWO final'), (r'^(hse_|nc_)', 'HSE06 / NC checks'), (r'^canary', 'workflow tests')]
        return next((lab for pat, lab in table if re.match(pat, n)), n)

    samples = []                                          # (time, row, state, gpu)
    cut = ts('2026-09-28T14:19:54Z')
    for line in (QE / 'cern_htcondor' / 'monitor.log').read_text(errors='replace').splitlines():
        m = re.match(r'^(\S+Z) queue: (.*)$', line)
        if m and ts(m.group(1)) < cut:
            t = ts(m.group(1))
            for j, s in re.findall(r'(\S+)=(\w+)', m.group(2)):
                samples.append((t, row(j), {'run': 2, 'idle': 1, 'HELD': 5}.get(s, 0), False))
    for line in (R / 'status_history.jsonl').read_text(errors='replace').splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        t = ts(rec['time'])
        for j in rec['jobs']:
            gpu = str(j.get('gpus', '0')) not in ('0', '', 'None') or bool(re.search(r'gpu|^nc_|^hse_', j['job']) and '__cpu' not in j['job'])
            samples.append((t, row(j['job']), j['state'], gpu))
    runs = []                                             # (start, end, row, gpu, failed)
    for logf in R.rglob('*_driver.log'):
        lines = logf.read_text(errors='replace').splitlines()
        st = [ts(l[1:21]) for l in lines if l.startswith('[20')]
        if len(st) >= 2:
            rc = re.findall(r'end rc=(\d+)', '\n'.join(lines))   # failed = the first step already failed (no result)
        runs.append((st[0], st[-1], row(logf.parent.name), 'GPU mode' in '\n'.join(lines), bool(rc) and rc[0] != '0'))
    rows = ['1 nm, vacuum test', '2 nm, unrelaxed SCF', 'W on 8b (bulk)', 'W on 24d (bulk)', '1 nm relaxation', '2 nm relaxation',
            'GPU benchmark', '1 nm final (CPU)', '1 nm IWO relaxation', '1 nm IWO final', 'HSE06 / NC checks', 'workflow tests']
    t0 = ts('2026-09-27T00:00:00Z'); day = 86400.0
    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    col = {1: '0.80', 5: '#d9a400'}
    by = {}
    for t, r, s, g in samples:
        by.setdefault((r, s, g), []).append(t)
    for (r, s, g), tt in by.items():                      # sampled states as bars of one sampling interval
        if r not in rows or s not in (1, 2, 5):
            continue
        tt = sorted(set(tt)); y = len(rows) - 1 - rows.index(r)
        for a, b in zip(tt, tt[1:] + [tt[-1] + 600]):
            b = min(b, a + (1800 if a < cut else 900))
            c = (C2 if g else C1) if s == 2 else col[s]
            ax.barh(y, (b - a) / day, left=(a - t0) / day, height=0.6 if s == 2 else 0.35, color=c, lw=0)
    for a, b, r, g, failed in runs:                       # exact worker intervals from the driver logs
        if r not in rows:
            continue
        y = len(rows) - 1 - rows.index(r)
        ax.barh(y, max(b - a, 600) / day, left=(a - t0) / day, height=0.6, color='none' if failed else (C2 if g else C1),
                edgecolor='k' if failed else 'none', hatch='////' if failed else None, lw=0.5)
    now = max(t for t, *_ in samples)
    for t, lab in (('2026-09-27T08:46:00Z', 'thread fix'), ('2026-09-28T15:04:36Z', 'GPU validated'),
                   ('2026-09-30T16:45:00Z', 'HSE to NC')):
        x = (ts(t) - t0) / day
        ax.axvline(x, color='0.5', lw=0.5, ls=':'); ax.text(x, 1.01, lab, fontsize=6.5, color='0.35', ha='center', va='bottom', transform=ax.get_xaxis_transform())
    ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows[::-1], fontsize=7)
    ax.set_xlim(0, (now - t0) / day + 0.05); ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xticks(range(0, int((now - t0) / day) + 2)); ax.set_xticklabels([f'{27 + d} Sep' if 27 + d <= 30 else f'{d - 3} Oct' for d in range(0, int((now - t0) / day) + 2)], fontsize=7)
    ax.set_xlabel('date (UTC), 2026')
    hs = [plt.Rectangle((0, 0), 1, 1, color=C1), plt.Rectangle((0, 0), 1, 1, color=C2), plt.Rectangle((0, 0), 1, 1, color='0.80'),
          plt.Rectangle((0, 0), 1, 1, color='#d9a400'), plt.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='k', hatch='////', lw=0.5)]
    ax.legend(hs, ['running, CPU', 'running, GPU', 'queued', 'held', 'failed at the first step'], fontsize=6.5, frameon=False,
              loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=5)
    fig.savefig(OUT / 'dft_timeline.pdf'); plt.close(fig)
    print(f'   timeline: {len(samples)} samples, {len(runs)} driver-log runs, up to {datetime.fromtimestamp(now, timezone.utc):%Y-%m-%d %H:%MZ}')


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    for f in (fig_bands, fig_convergence, fig_planar, fig_confinement, fig_hse, fig_wpdos, fig_compute,
              fig_structures, fig_mass, fig_relax, fig_levels, fig_alignment, fig_lin_parity, fig_timeline):
        try:
            f(); print('ok', f.__name__)
        except Exception as e:
            print('FAILED', f.__name__, type(e).__name__, e)
