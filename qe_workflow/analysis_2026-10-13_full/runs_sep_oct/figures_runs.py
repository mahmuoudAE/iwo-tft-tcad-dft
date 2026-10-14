"""Figures for the Sep-Oct run sheets (runs_sep_oct/figures/), from out/<run>.json and out/<run>_arrays.json.gz only.
R1 vc-relax histories (in-plane a, b; pressure; total force), R2 SCF iterations per relaxation step, R3 wall time per pw.x step and
hardware, R4 near-gap bands of every slab band-structure run, R5 Loewdin charges by element. Plain (Origin-like) style.
"""
import gzip
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import figstyle as fs  # noqa: E402
from figstyle import plt, panel, CYCLE  # noqa: E402

OUT = HERE / 'out'
FIG = HERE / 'figures'


def J(run):
    return json.loads((OUT / f'{run}.json').read_text())


def A(run):
    with gzip.open(OUT / f'{run}_arrays.json.gz', 'rt', encoding='utf-8') as g:
        return json.load(g)


def save(fig, stem):
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / f'{stem}.pdf'); fig.savefig(FIG / f'{stem}.png', dpi=300); plt.close(fig); print('saved', stem)


def wall_h(s):
    t = 0.0
    for v, u in re.findall(r'([\d.]+)\s*([dhms])', s or ''):
        t += float(v) * {'d': 24, 'h': 1, 'm': 1 / 60, 's': 1 / 3600}[u]
    return t


def r1():
    sets = [('slab1_relax_gpu', 'vcrelax.out', '1 nm (GPU)'), ('cpu_relax_snapshots', 'slab1_relax_vcrelax.out', '1 nm (CPU snapshot)'),
            ('slab2_relax_c2', 'vcrelax.out', '2 nm (GPU)'), ('cpu_relax_snapshots', 'slab2_relax_vcrelax.out', '2 nm (CPU snapshot)'),
            ('slabL1_relax_v2', 'vcrelax.out', '0.51 nm'), ('slabL2_relax_v2', 'vcrelax.out', '0.75 nm')]
    fig, ax = plt.subplots(1, 3, figsize=(6.8, 2.5))
    for j, (run, f, lab) in enumerate(sets):
        st = J(run)['pw'][f]['steps']
        x = np.arange(len(st))
        a = [s['cell_A'][0][0] if s.get('cell_A') else np.nan for s in st]
        P = [s.get('pressure_kbar', np.nan) for s in st]
        F = [s.get('total_force_Ry_bohr', np.nan) for s in st]
        ls = '-' if 'snapshot' not in lab else ':'
        ax[0].plot(x, a, ls, color=CYCLE[j], lw=0.9, label=lab)
        ax[1].plot(x, P, ls, color=CYCLE[j], lw=0.9)
        ax[2].semilogy(x, F, ls, color=CYCLE[j], lw=0.9)
    ax[0].set_ylabel('in-plane a (Å)'); ax[1].set_ylabel('pressure (kbar)'); ax[2].set_ylabel('total force (Ry/bohr)')
    for i, a_ in enumerate(ax):
        a_.set_xlabel('SCF step'); panel(a_, 'abc'[i], x=-0.3)
    h, l = ax[0].get_legend_handles_labels()
    fig.tight_layout(rect=(0, 0.13, 1, 1)); fig.legend(h, l, loc='lower center', ncol=3, fontsize=6.5)
    save(fig, 'figR1_vcrelax_histories')


def r2():
    sets = [('slab1_relax_gpu', 'vcrelax.out', '1 nm'), ('slab2_relax_c2', 'vcrelax.out', '2 nm'), ('slabL1_relax_v2', 'vcrelax.out', '0.51 nm'),
            ('slabL2_relax_v2', 'vcrelax.out', '0.75 nm'), ('iwo_slab1_W24d_x1', 'relax.out', '1 nm W'), ('iwo_slab2_W24d_checkpoint', 'relax.out', '2 nm W'),
            ('iwo_W24d', 'relax.out', 'bulk W 24d'), ('iwo_W8b', 'relax.out', 'bulk W 8b')]
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.5))
    for j, (run, f, lab) in enumerate(sets):
        st = J(run)['pw'][f]['steps']
        ax[0].plot(np.arange(len(st)), [s.get('iterations', np.nan) for s in st], '-' if j < 4 else '--', color=CYCLE[j % 10], lw=0.9, label=lab)
        tr = A(run)[f]['scf_accuracy_traces']
        if tr and tr[0]:
            ax[1].semilogy(np.arange(1, len(tr[0]) + 1), tr[0], '-' if j < 4 else '--', color=CYCLE[j % 10], lw=0.8)
    ax[0].set_xlabel('SCF step of the relaxation'); ax[0].set_ylabel('SCF iterations')
    ax[1].set_xlabel('iteration (first SCF)'); ax[1].set_ylabel('estimated SCF accuracy (Ry)')
    panel(ax[0], 'a', x=-0.2); panel(ax[1], 'b', x=-0.33)
    h, l = ax[0].get_legend_handles_labels()
    fig.tight_layout(rect=(0, 0.13, 1, 1), w_pad=2.5); fig.legend(h, l, loc='lower center', ncol=4, fontsize=6.5)
    save(fig, 'figR2_scf_iterations')


def r3():
    from extract_runs import RUNS
    from matplotlib.patches import Patch
    rows = []
    for run in RUNS:
        if run in ('live_snapshots', 'iwo_W8b_partial', 'iwo_W24d_partial'):
            continue                      # copies of jobs listed under their own folders
        r = J(run)
        for k, d in r['driver'].items():
            for s in d['steps']:
                w = re.search(r'([\ddhms.\s]+)WALL', s.get('time', ''))
                if not w:
                    continue
                out = {'vcrelax': 'vcrelax.out', 'relax': 'relax.out', 'scf': 'scf.out', 'bands': 'bands.out', 'scf_k4': 'scf_k4.out', 'spin_k3': 'spin_k3.out'}.get(s['step'])
                pw = r['pw'].get(out, {})
                gpu = bool(pw.get('header', {}).get('gpu_lines'))
                rows.append((f"{run}:{s['step']}", wall_h(w.group(1)), gpu, bool(d.get('gpu'))))
    rows = [x for x in rows if x[1] > 0]
    rows.sort(key=lambda x: -x[1])
    fig, ax = plt.subplots(figsize=(6.6, 0.16 * len(rows) + 0.8))
    y = np.arange(len(rows))
    ax.barh(y, [x[1] for x in rows], color=[CYCLE[0] if x[2] else (CYCLE[2] if x[3] else CYCLE[1]) for x in rows], height=0.7)
    ax.set_yticks(y); ax.set_yticklabels([x[0] for x in rows], fontsize=5.5); ax.invert_yaxis(); ax.minorticks_off()
    ax.set_xscale('log'); ax.set_xlabel('wall time of the pw.x step (h)')
    ax.legend(handles=[Patch(color=CYCLE[0], label='pw.x GPU build (QE 7.3.1, 1 rank)'), Patch(color=CYCLE[2], label='CPU build on a GPU node'),
                       Patch(color=CYCLE[1], label='CPU build on a CPU node')], loc='lower right', fontsize=6.5)
    save(fig, 'figR3_wall_times')


def r4():
    sets = [('slab1_v35', 'bands.out', 'unrelaxed 1 nm'), ('slab1r_final_cpu', 'bands.out', '1 nm'), ('slab2_relax_c2', 'bands.out', '2 nm'),
            ('slabL2_relax_v2', 'bands.out', '0.75 nm'), ('slabL1_relax_v2', 'bands.out', '0.51 nm')]
    fig, ax = plt.subplots(1, len(sets), figsize=(6.8, 2.6), sharey=True)
    for j, (run, f, lab) in enumerate(sets):
        rec = J(run)['pw'][f]
        b = rec['bands']
        eg = A(run)[f]['eig']
        e = np.array(eg['eig_eV'])
        alat = float(rec['params']['lattice parameter (alat)'].split()[0]) * 0.529177210903
        k = np.linalg.norm(np.array(eg['k_cart_2pi_alat']), axis=1) * 2 * np.pi / alat
        x = np.concatenate([-k[:11], k[[0] + list(range(11, len(k)))]])
        idx = list(range(11)) + [0] + list(range(11, len(k)))
        no, ref = b['n_occ'], b['VBM_eV']
        for n in range(no - 4, min(no + 4, e.shape[1])):
            ax[j].plot(x[:11], e[:11, n] - ref, color='k' if n < no else CYCLE[0], lw=0.7)
            ax[j].plot(x[11:], e[idx[11:], n] - ref, color='k' if n < no else CYCLE[0], lw=0.7)
        ax[j].axvline(0, color='0.6', lw=0.5)
        ax[j].set_title(lab, fontsize=7.5); ax[j].set_ylim(-1.5, 4)
        ax[j].set_xlabel(r'$k$ (Å$^{-1}$)', fontsize=7)
    ax[0].set_ylabel(r'$E - E_{\rm VBM}$ (eV)')
    fig.tight_layout()
    save(fig, 'figR4_slab_bands_near_gap')


def r5():
    sets = [('iwo_W8b', 'projwfc_iwo_W8b.out', 'bulk W 8b'), ('iwo_W24d', 'projwfc_iwo_W24d.out', 'bulk W 24d'),
            ('iwo_slab1_final_cpu', 'projwfc_iwo_slab1_final_cpu.out', '1 nm W'), ('iwo_slab2_final_cpu', 'projwfc_iwo_slab2_final_cpu.out', '2 nm W'),
            ('slab2r_pdos_cpu', 'projwfc_slab2r_pdos_cpu.out', '2 nm'), ('slabL2_relax_v2', 'projwfc_slabL2_relax_v2.out', '0.75 nm'),
            ('slabL1_relax_v2', 'projwfc_slabL1_relax_v2.out', '0.51 nm')]
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.5))
    els = ['In', 'O', 'W', 'H']
    for j, (run, f, lab) in enumerate(sets):
        q = J(run)['projwfc'][f].get('lowdin_by_element', {})
        for i, e in enumerate(els):
            if e in q:
                ax[0].plot(i + (j - 3) * 0.08, q[e]['total']['mean'], 'os^Dv<>'[j], mfc='none', color=CYCLE[j], ms=4, label=lab if i == 0 or (e == 'W' and 'In' not in q) else None)
        ax[1].bar(j, J(run)['projwfc'][f].get('spilling') or 0, color='white', edgecolor=CYCLE[j])
    ax[0].set_xticks(range(len(els))); ax[0].set_xticklabels(els); ax[0].minorticks_off(); ax[0].set_ylabel('mean Loewdin charge (e)')
    ax[0].legend(fontsize=5.8, loc='upper right')
    ax[1].set_xticks(range(len(sets))); ax[1].set_xticklabels([s[2] for s in sets], rotation=40, ha='right', fontsize=6.5); ax[1].minorticks_off()
    ax[1].set_ylabel('spilling parameter')
    panel(ax[0], 'a', x=-0.2); panel(ax[1], 'b', x=-0.25)
    fig.tight_layout()
    save(fig, 'figR5_lowdin')


if __name__ == '__main__':
    r1(); r2(); r3(); r4(); r5()
