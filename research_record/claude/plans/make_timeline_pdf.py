#!/usr/bin/env python3
"""CERN/DFT + ATLAS timeline for 10-21 Oct 2026 as a 3-page landscape PDF (plus PNG previews).
Page 1: Gantt chart; page 2: job tables; page 3: dependencies, studies, cut order and rules.
Output: claude/plans/CERN_DFT_timeline_2026-10.pdf"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
PDF = HERE / 'CERN_DFT_timeline_2026-10.pdf'
A4L = (11.69, 8.27)
C = {'you': '#7F7F7F', 'local': '#0072B2', 'cern1': '#D55E00', 'cern2': '#E69F00', 'cern3': '#F0E442',
     'analysis': '#009E73', 'atlas': '#CC79A7', 'write': '#56B4E9'}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})

# (label, start, end, colour key, hatched=conditional). Days are dates in October 2026 (10.0 = 10 Oct 00:00).
TASKS = [
    ('YOU: "go"; part C (jobs repo + deploy key); acron OK', 10.0, 11.4, 'you', False),
    ('CERN: build ML env on EOS; ML melt-quench on GPU; QC gate; timing test', 10.2, 10.9, 'cern1', False),
    ('Runner: WF-001 design (Claude, Codex review) -> WF-002 build + test (Codex)', 10.3, 12.0, 'local', False),
    ('Free analyses: 2 nm crystalline W slab, Pd barrier estimate', 10.5, 11.6, 'local', False),
    ('CERN: a-IWO + a-In$_2$O$_3$ slab 2.0 nm (~170 atoms)', 10.9, 14.4, 'cern1', False),
    ('CERN: a-IWO + a-In$_2$O$_3$ slab 1.5 nm (~125 atoms)', 10.9, 12.9, 'cern1', False),
    ('CERN: a-IWO + a-In$_2$O$_3$ slab 1.0 nm (~125 atoms)', 10.9, 12.9, 'cern1', False),
    ('CERN: a-IWO + a-In$_2$O$_3$ slab 0.8 nm (~125 atoms)', 10.9, 12.7, 'cern1', False),
    ('CERN: a-IWO + a-In$_2$O$_3$ slab 0.7 nm (~125 atoms)', 10.9, 12.7, 'cern1', False),
    ('CERN: ML-structure check (short DFT MD, 80-atom bulk)', 10.9, 12.1, 'cern1', False),
    ('CERN: O vacancy near / far from W (3 jobs)', 11.3, 12.6, 'cern2', False),
    ('CERN: a-Al$_2$O$_3$ / a-IWO interface, 1 nm per side (2 jobs)', 11.3, 13.9, 'cern2', False),
    ('CERN via runner tickets (only if on schedule): 0.7 nm surfaces, 2nd samples, HfO$_2$', 13.0, 15.0, 'cern3', True),
    ('Analyse finished jobs (DOS, tails, IPR, W, surface vs interior, EA)', 12.0, 16.0, 'analysis', False),
    ('ATLAS, no DFT input: off-current geometry, 31.8 nm electrostatics', 11.0, 14.6, 'atlas', False),
    ('ATLAS with DFT inputs: tails, $\\Delta E_c$, interface states -> $\\mu_{FE}$ vs measured', 15.0, 17.6, 'atlas', False),
    ('Copy all CERN results back and verify', 19.0, 20.6, 'local', False),
    ('Write-up and thesis figures', 17.0, 21.0, 'write', False),
]
MILESTONES = [(15.0, '15 Oct: target, all jobs done', 0.35), (16.0, '16 Oct: last long-job submission', 1.05),
              (18.0, '18 Oct: last submission', 0.35), (21.0, '21 Oct: CERN ends', 1.05)]


def page_gantt(pdf):
    fig, ax = plt.subplots(figsize=A4L)
    fig.subplots_adjust(left=0.43, right=0.95, top=0.80, bottom=0.16)
    n = len(TASKS)
    for k, (lab, s, e, col, cond) in enumerate(TASKS):
        y = n - 1 - k
        ax.barh(y, e - s, left=s, height=0.62, color=C[col], edgecolor='0.25', lw=0.5,
                hatch='///' if cond else None, alpha=0.65 if cond else 1.0)
    ax.set_yticks(range(n))
    ax.set_yticklabels([t[0] for t in TASKS][::-1], fontsize=8)
    ax.set_xlim(10, 22)
    ax.set_xticks(range(10, 23))
    ax.set_xticklabels([f'{d} Oct' for d in range(10, 23)], rotation=45, ha='right', fontsize=8)
    ax.set_ylim(-0.8, n - 0.2)
    ax.grid(axis='x', color='0.88', lw=0.6)
    ax.set_axisbelow(True)
    for x, lab, dy in MILESTONES:
        ax.axvline(x, color='k', ls='--', lw=0.9)
        ax.text(x, n - 0.2 + dy, lab, fontsize=7.5, va='bottom', ha='center', clip_on=False,
                bbox=dict(fc='white', ec='none', pad=0.5))
    ax.axvline(10.0, color='0.5', lw=0.8)
    leg = [Patch(facecolor=C['you'], label='You'), Patch(facecolor=C['local'], label='Local (your PC)'),
           Patch(facecolor=C['cern1'], label='CERN wave 1 (protected)'), Patch(facecolor=C['cern2'], label='CERN wave 2'),
           Patch(facecolor=C['cern3'], hatch='///', label='CERN wave 3 (conditional)'),
           Patch(facecolor=C['analysis'], label='Analysis'), Patch(facecolor=C['atlas'], label='ATLAS (local)'),
           Patch(facecolor=C['write'], label='Write-up')]
    fig.legend(handles=leg, loc='lower center', ncol=4, fontsize=8, frameon=False, bbox_to_anchor=(0.6, 0.0))
    fig.suptitle('IWO project: CERN DFT + ATLAS timeline, 10-21 October 2026', fontsize=13, y=0.975, x=0.5)
    fig.text(0.5, 0.925, 'Durations are estimates from past CERN timings (80-atom cell: ~2.5 h per SCF); the timing test on 10 Oct '
             'replaces them with measured values.\nNo new measurements: inputs are the existing curves, the published paper, '
             'CERN (until 21 Oct; ML and DFT both run there) and local Silvaco ATLAS.', ha='center', fontsize=8, color='0.25')
    pdf.savefig(fig)
    fig.savefig(HERE / 'timeline_p1.png', dpi=110)
    plt.close(fig)


def draw_table(ax, cols, rows, widths, title, fs=8):
    ax.axis('off')
    ax.set_title(title, loc='left', fontsize=10.5, fontweight='bold', pad=4)
    t = ax.table(cellText=rows, colLabels=cols, colWidths=widths, loc='upper left', cellLoc='left')
    t.auto_set_font_size(False)
    t.set_fontsize(fs)
    t.scale(1, 1.45)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor('0.7')
        if r == 0:
            cell.set_facecolor('#E8EEF4')
            cell.set_text_props(fontweight='bold')


def page_tables(pdf):
    fig = plt.figure(figsize=A4L)
    fig.suptitle('Jobs: what is built and run', fontsize=13, y=0.97)
    ax1 = fig.add_axes([0.04, 0.62, 0.92, 0.28])
    draw_table(ax1,
               ['Slab', 'In-plane cell', 'Atoms (+H)', 'W content', 'Twin', 'Est. DFT time', 'Priority'],
               [['2.0 nm', '1.05 x 1.05 nm', '~170', '1 W = 1.5 % (2 % needs ~250 atoms)', 'a-In2O3', '2-4 days', '1 (protected)'],
                ['1.5 nm', '1.05 x 1.05 nm', '~125', '1 W = 2.0 %', 'a-In2O3', '1-2 days', '1'],
                ['1.0 nm', '1.29 x 1.29 nm', '~125', '1 W = 2.0 %', 'a-In2O3', '1-2 days', '1'],
                ['0.8 nm', '1.44 x 1.44 nm', '~125', '1 W = 2.0 %', 'a-In2O3', '1-2 days', '1'],
                ['0.7 nm', '1.54 x 1.54 nm', '~125', '1 W = 2.0 %', 'a-In2O3', '1-2 days', '1']],
               [0.08, 0.13, 0.09, 0.30, 0.09, 0.12, 0.12],
               'Amorphous slab series (ML-built on CERN GPUs, DFT-relaxed; 1 sample each; IWO + In2O3 twin = 10 structures)')
    ax2 = fig.add_axes([0.04, 0.10, 0.92, 0.45])
    draw_table(ax2,
               ['Job', 'Structure', 'Question', 'Est. time', 'Priority'],
               [['ML-structure check', '80-atom a-bulk, short DFT MD', 'Is the ML-built structure stable and right under DFT?', '~1 day', '2'],
                ['O vacancy near / far W', '79-atom crystal cells (3 jobs)', 'Does W raise the vacancy formation energy? By how much?', '~1 day', '3'],
                ['Oxide interface', 'a-Al2O3 / a-IWO, 1 nm/side (2 jobs)', 'Band offset, interface states (-> D_it, Q_f in TCAD)', '2-3 days', '4'],
                ['Conditional extras', '0.7 nm surfaces; 2nd samples; HfO2', 'Surface chemistry; statistics; the paper\'s interface', '1-2 days', '5 (if on time)'],
                ['Free (no CERN)', 'existing outputs', '2 nm crystal W slab; Pd barrier = WF(Pd) - EA(IWO)', 'hours', '-']],
               [0.16, 0.27, 0.37, 0.09, 0.11],
               'Other jobs')
    pdf.savefig(fig)
    fig.savefig(HERE / 'timeline_p2.png', dpi=110)
    plt.close(fig)


def page_rules(pdf):
    fig = plt.figure(figsize=A4L)
    fig.suptitle('How the jobs depend on each other, what is computed, and the rules', fontsize=13, y=0.97)
    left = (
        'DEPENDENCIES (serial)\n'
        '  one DAG per structure, all on CERN (laptop can be off):\n'
        '  ML (GPU) -> QC gate -> DFT relax (<=20 h segments) -> SCF -> DOS/IPR\n'
        '  ML-structure check must agree before the slab results are called final\n'
        '  ATLAS runs with DFT inputs wait for the slab analysis\n\n'
        'AUTOMATIC RUNNER (from ~12 Oct)\n'
        '  ticket -> you merge = approve -> acron on lxplus -> DAG\n'
        '  -> results pushed to the private iwo-dft-jobs repo\n\n'
        'PARALLEL\n'
        '  all CERN jobs (no job needs another job\'s result)\n'
        '  local analysis and ATLAS run while CERN computes\n\n'
        'COMPUTED ON EVERY SLAB\n'
        '  1  structure: coordination, defect sites, W site, surface OH\n'
        '  2  band gap vs thickness (confinement), HSE-corrected\n'
        '  3  band tails: width below the conduction band (vs TCAD W_TA = 40 meV)\n'
        '  4  localization (IPR): does W keep states delocalized when thin?\n'
        '  5  W: donor level, charge, Fermi level\n'
        '  6  surface vs interior DOS (tests the N_s + N_b t trap split)\n'
        '  7  electron affinity vs thickness (Delta E_c law for TCAD)\n\n'
        'MOBILITY\n'
        '  not computed by DFT; DFT gives tails, m*, IPR, n_free/n_total;\n'
        '  ATLAS turns them into mu_FE, which is compared with\n'
        '  the measured 12 / 11 / 50 cm2/Vs (2.0 / 6.3 / 13.2 nm)'
    )
    right = (
        'DEADLINES\n'
        '  10 Oct  everything built and wave 1 submitted\n'
        '  11 Oct  wave 2 submitted\n'
        '  13-14 Oct  wave 3 only if wave 1 is on schedule\n'
        '  15 Oct  target: all jobs finished\n'
        '  16 Oct  last submission of a job > 2 days (fallback)\n'
        '  18 Oct  last submission of any job\n'
        '  19-20 Oct  all results copied back and verified\n'
        '  21 Oct  CERN access ends (buffer, nothing running)\n\n'
        'CUT ORDER (if CERN is busy or slipping)\n'
        '  first cut: extras -> interface -> In2O3 twins at 1.5 / 0.8 nm\n'
        '  protected: all five a-IWO slabs, 2 nm In2O3 twin, ML check\n\n'
        'CERN SAFETY (lessons from Sept-Oct)\n'
        '  restart files written regularly;\n'
        '  snapshot_jobs.sh copies outputs every 15 min\n'
        '  (running jobs lose EOS access after ~25 h)\n'
        '  never condor_release a job that ran > 1 h:\n'
        '  resubmit from the snapshot instead\n'
        '  you log in; passwords / 2FA are never handled by an agent\n\n'
        'CAVEATS TO STATE AT THE DEFENCE\n'
        '  PBE gaps are underestimated: trends and widths, not absolute gaps\n'
        '  small cells, fast quench: more defective than real films\n'
        '  1 sample per structure: indicative statistics\n'
        '  slab surfaces are H/OH in vacuum, not the real oxide / air'
    )
    fig.text(0.03, 0.90, left, va='top', ha='left', fontsize=9.2, family='DejaVu Sans Mono', linespacing=1.45)
    fig.text(0.52, 0.90, right, va='top', ha='left', fontsize=9.2, family='DejaVu Sans Mono', linespacing=1.45)
    pdf.savefig(fig)
    fig.savefig(HERE / 'timeline_p3.png', dpi=110)
    plt.close(fig)


with PdfPages(PDF) as pdf:
    page_gantt(pdf)
    page_tables(pdf)
    page_rules(pdf)
    d = pdf.infodict()
    d['Title'] = 'IWO project: CERN DFT + ATLAS timeline, 10-21 October 2026'
print('wrote', PDF)
