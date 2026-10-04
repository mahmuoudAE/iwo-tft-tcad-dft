"""Generate the HTCondor job folders of the CERN stage (IWO bulk, In2O3 slabs) from verified structures.

Usage (WSL, qe env):
  python make_jobs.py <structures folder> <jobs folder>   production inputs
  python make_jobs.py --toy <jobs folder>                  tiny W test systems, same steps (local pipeline test)

Settings (see PROTOCOL.md): PBE, pslibrary 1.0.0 PAW, ecutwfc 71 Ry, ecutrho 568 Ry (stage 1).
  IWO bulk:   80-atom cell at the PBE host lattice constant, Marzari-Vanderbilt smearing 0.01 Ry,
              relax at 3x3x3 (forces < 1e-3 Ry/bohr), then SCF 4x4x4 + PDOS + bands near Gamma,
              then a spin-polarized SCF at 3x3x3 (starting moment on W).
  slabs:      Lin et al. (2022) recipe, fixed occupations, 3x3x1 k-points as in that paper,
              local-TF mixing; SCF + planar-averaged potential + in-plane bands near Gamma;
              relax jobs: vc-relax of atoms and in-plane cell (cell_dofree = '2Dxy').
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import spglib

MASS = {'In': 114.818, 'O': 15.999, 'W': 183.84, 'H': 1.008}          # IUPAC standard atomic weights
UPF = {'In': 'In.pbe-dn-kjpaw_psl.1.0.0.UPF', 'O': 'O.pbe-n-kjpaw_psl.1.0.0.UPF',
       'W': 'W.pbe-spn-kjpaw_psl.1.0.0.UPF', 'H': 'H.pbe-kjpaw_psl.1.0.0.UPF'}
ZVAL = {'In': 13, 'O': 6, 'W': 14, 'H': 1}                           # valence charges of these data sets
# SG15 ONCV norm-conserving v1.2 (M. Schlipf, F. Gygi, Comput. Phys. Commun. 196, 36 (2015); D. R. Hamann,
# Phys. Rev. B 88, 085117 (2013)); used only for the HSE06 check, where exact exchange with PAW proved too slow
UPF_NC = {'In': 'In_ONCV_PBE-1.2.upf', 'O': 'O_ONCV_PBE-1.2.upf', 'W': 'W_ONCV_PBE-1.2.upf', 'H': 'H_ONCV_PBE-1.2.upf'}
ORDER = ['In', 'O', 'W', 'H']
BOHR = 0.529177210903
NUM = {'In': 49, 'O': 8, 'W': 74, 'H': 1}

# name, structure, kind, cpus, memory (MB), disk (KB), flavour, wall-time limit (s)
JOBS = [
    # 2026-09-27 09:10Z: IWO cells and slab1_relax moved to 64 CPUs (2 GB/CPU) to shorten the wall time
    ('iwo_W8b', 'iwo_W8b', 'iwo_bulk', 64, 128000, 40000000, 'testmatch', 259200),
    ('iwo_W24d', 'iwo_W24d', 'iwo_bulk', 64, 128000, 40000000, 'testmatch', 259200),
    ('slab1_v15', 'slab1_v15', 'slab_scf', 16, 32000, 20000000, 'tomorrow', 86400),
    ('slab1_v25', 'slab1_v25', 'slab_scf', 16, 32000, 20000000, 'tomorrow', 86400),
    ('slab1_v35', 'slab1_v35', 'slab_scf', 16, 32000, 20000000, 'tomorrow', 86400),
    ('slab2_v25', 'slab2_v25', 'slab_scf', 32, 80000, 30000000, 'tomorrow', 86400),
    # 14:40Z: jobs with >= 32 CPUs are routed to the 10-slot 'bigmcore' pool (condor_q -better-analyze:
    # 0 slots free); slab1_relax moved to 16 CPUs (normal pool), slab2_relax to 32 CPUs
    ('slab1_relax', 'slab1_v25', 'slab_relax', 16, 32000, 30000000, 'testmatch', 259200),
    # 2026-09-27: 64 CPUs (2 GB/CPU) instead of 32 to shorten the longest job; still 2 pools (memory)
    ('slab2_relax', 'slab2_v25', 'slab_relax', 32, 64000, 40000000, 'nextweek', 604800),
]
# GPU benchmark (2026-09-28): the finished CPU job slab1_v15 (SCF only) repeated with 1 GPU (QE 7.3.1 GPU
# container); accepted if the total energy and gap agree with the CPU run within the protocol tolerances.
# Optional 9th field: number of GPUs (default 0).
JOBS += [('gpu_bench_v15', 'slab1_v15', 'bench_scf', 8, 32000, 20000000, 'workday', 28800, 1)]
# benchmark passed (H100 NVL: 9 min 16 s vs 1 h 16 min on 16 CPUs; dE = 5e-7 Ry, same gap): the slab relaxations
# continue on GPUs from the latest geometry of the CPU runs (inputs updated with qeio.py newgeom before submission)
JOBS += [('slab1_relax_gpu', 'slab1_v25', 'slab_relax', 8, 32000, 30000000, 'testmatch', 259200, 1),
         ('slab2_relax_gpu', 'slab2_v25', 'slab_relax', 16, 64000, 40000000, 'testmatch', 259200, 2),
         # 2-GPU request idle 2.5 h (17:50Z); 1-GPU jobs start within minutes
         ('slab2_relax_gpu1', 'slab2_v25', 'slab_relax', 8, 48000, 40000000, 'testmatch', 259200, 1),
         # 2026-09-30: continue the 32-CPU relaxation on 1 GPU with 8 CPUs from its latest geometry
         ('slab2_relax_gpu8', 'slab2_v25', 'slab_relax', 8, 32000, 60000000, 'testmatch', 259200, 1),
         # 2026-09-30: band edges of the relaxed pure 1 nm slab on CPU (EA/IP lost to the pp.x version clash), and
         # the 1 nm IWO slab: W on the central 24d site of the relaxed slab (In23 W O48 H24), atoms relaxed on GPU,
         # final SCF + planar average + PDOS + bands on the CPU environment
         ('slab1r_final_cpu', 'slab1r_pure', 'slab_scf', 16, 32000, 20000000, 'tomorrow', 86400),
         ('iwo_slab1_W24d', 'slab1r_W24d', 'iwo_slab', 8, 32000, 60000000, 'testmatch', 259200, 1),
         # 2026-09-30 HSE06 check of the PBE confinement (single points at the PBE geometries, GPU):
         # dEg(HSE) vs dEg(PBE); bulk with EXX q-grid 1x1x1 and 3x3x3 (sensitivity), slab with 1x1x1
         ('hse_bulk_nq1', 'bulk_prim', 'hse_scf', 8, 32000, 30000000, 'tomorrow', 86400, 1),
         ('hse_bulk_nq3', 'bulk_prim', 'hse_scf', 8, 32000, 30000000, 'tomorrow', 86400, 1),
         ('hse_slab1', 'slab1r_pure', 'hse_scf', 8, 32000, 60000000, 'testmatch', 259200, 1),
         # chained after the relaxed 2 nm slab (dft_flow.sh chains.txt): its CPU band edges and the 2 nm IWO slab
         # 2026-10-01 HSE06 check moved to SG15 norm-conserving (PAW exact exchange ran on the CPU at 0 % GPU):
         # ratio [dEg(HSE)/dEg(PBE)] in one NC setup at the PAW-PBE geometries; bulk cutoff check 80 vs 100 Ry
         ('nc_pbe_bulk_e80', 'bulk_prim', 'nc_scf', 8, 32000, 20000000, 'workday', 28800, 1),
         ('nc_pbe_bulk_e100', 'bulk_prim', 'nc_scf', 8, 32000, 20000000, 'workday', 28800, 1),
         ('nc_hse_bulk_e80', 'bulk_prim', 'nc_scf', 8, 32000, 20000000, 'tomorrow', 86400, 1),
         ('nc_hse_bulk_q3_e80', 'bulk_prim', 'nc_scf', 8, 32000, 20000000, 'tomorrow', 86400, 1),   # EXX q-grid check
         # ecutfock 160 Ry set (same names + '_f160'): bulk q1, bulk q3, slab q1
         ('nc_hse_bulk_f160_e80', 'bulk_prim', 'nc_scf', 8, 32000, 20000000, 'tomorrow', 86400, 1),
         ('nc_hse_bulk_q3_f160_e80', 'bulk_prim', 'nc_scf', 8, 32000, 20000000, 'tomorrow', 86400, 1),
         ('nc_hse_slab1_f160_e80', 'slab1r_pure', 'nc_scf', 8, 64000, 60000000, 'testmatch', 259200, 1),
         ('nc_pbe_slab1_e80', 'slab1r_pure', 'nc_scf', 8, 32000, 30000000, 'tomorrow', 86400, 1),
         ('nc_hse_slab1_e80', 'slab1r_pure', 'nc_scf', 8, 64000, 60000000, 'testmatch', 259200, 1),
         # 2026-10-02: memory set from the measured 2 nm demand (vc-relax 31.4 GB with occupied+8 bands on 1 GPU; the final
         # SCF with occupied+16 bands 66 GB, which held slab2_relax_x1); CPU run limited to 2 pools (~24 GB per pool)
         ('slab2r_final_cpu', 'slab2r_pure', 'slab_scf', 16, 72000, 20000000, 'tomorrow', 86400),
         ('iwo_slab2_W24d', 'slab2r_W24d', 'iwo_slab', 8, 100000, 80000000, 'testmatch', 259200, 1),
         # 2026-10-02 (user request): the same final SCF + planar average + bands of the relaxed 2 nm slab also on
         # 1 GPU (~8x faster than 16 CPUs); its GPU save is converted to HDF5 for the CPU pp.x (common/dat2h5.py)
         ('slab2r_final_gpu', 'slab2r_pure', 'slab_scf', 8, 100000, 60000000, 'tomorrow', 86400, 1)]
# memory: every pool holds complete wavefunctions of its k-points. slab2_v25 with 4 pools used 95.8 GB
# (held at a 48 GB limit, 2026-09-27), i.e. ~24 GB per pool, so slab 2 runs with at most 2 pools.
MAXPOOL = {'slab2_v25': 2, 'slab2_relax': 2, 'slab2r_final_cpu': 2}
TOY_JOBS = [
    ('toy_bulk', 'toy_bulk', 'iwo_bulk', 2, 0, 0, 'espresso', 3600 * 3),
    ('toy_slab', 'toy_slab', 'slab_relax', 2, 0, 0, 'espresso', 3600 * 3),
]


def frac(st):
    return np.linalg.solve(np.array(st['cell_A']).T, np.array(st['positions_A']).T).T


def n_irr(st, mesh):
    cell = (np.array(st['cell_A']), frac(st), [NUM[s] for s in st['symbols']])
    res = spglib.get_ir_reciprocal_mesh(mesh, cell, is_shift=[0, 0, 0], is_time_reversal=True, symprec=1e-3)
    return len(np.unique(res[0]))


def npool(ncpu, nks, min_ranks):
    return max(d for d in range(1, ncpu + 1) if ncpu % d == 0 and d <= nks and ncpu // d >= min_ranks)


def klist(a_len, dirs, kmax=0.15, n=11):
    """Gamma plus n-1 points along each direction, |k| up to kmax (1/A), in units of 2*pi/alat."""
    pts = [[0.0, 0.0, 0.0]]
    for d in dirs:
        u = np.array(d, float) / np.linalg.norm(d)
        pts += [list(u * kmax * i / (n - 1) * a_len / (2 * np.pi)) for i in range(1, n)]
    return pts


def pw_input(st, calc, prefix, p, kgrid=None, kpts=None, nbnd=None, nspin=1, verbosity='low'):
    species = [s for s in ORDER if s in st['symbols']]
    L = ['&CONTROL',
         f"  calculation = '{calc}', prefix = '{prefix}', outdir = './tmp', pseudo_dir = './'",
         # stress off for hybrids: the exact-exchange stress took 81 % of the 1 nm HSE06 run (review 2026-10-03)
         f"  verbosity = '{verbosity}', tprnfor = .true., tstress = {'.false.' if 'hse' in p.get('extra_sys', '') else '.true.'}, max_seconds = 1.0d8"]
    if calc in ('relax', 'vc-relax'):
        L.append('  nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3')
    L += ['/', '&SYSTEM',
          f"  ibrav = 0, nat = {len(st['symbols'])}, ntyp = {len(species)}, ecutwfc = {p['ecut']}, ecutrho = {p.get('rho_factor', 8) * p['ecut']}"]
    L.append("  occupations = 'fixed'" if p['occ'] == 'fixed'
             else f"  occupations = 'smearing', smearing = 'mv', degauss = {p.get('degauss', 0.01)}")
    if nbnd:
        L.append(f'  nbnd = {nbnd}')
    if p.get('extra_sys'):
        L.append('  ' + p['extra_sys'])
    if nspin == 2:
        L.append(f"  nspin = 2, starting_magnetization({species.index('W') + 1}) = 0.5")
    L += ['/', '&ELECTRONS',
          f"  conv_thr = {p['conv']}, mixing_beta = {p['beta']}, electron_maxstep = {p.get('maxstep', 300)}"
          + (", mixing_mode = 'local-TF'" if p.get('localtf') else '')
          # non-SCF bands: Davidson aborted locally for bulk In2O3 (2026-09-27); CG is robust
          + (", diagonalization = 'cg'" if calc == 'bands' and p.get('bands_cg', True) else ''), '/']
    if calc in ('relax', 'vc-relax'):
        L += ['&IONS', "  ion_dynamics = 'bfgs'", '/']
    if calc == 'vc-relax':
        L += ['&CELL', "  cell_dynamics = 'bfgs', cell_dofree = '2Dxy', press_conv_thr = 0.5", '/']
    L.append('ATOMIC_SPECIES')
    L += [f'  {s} {MASS[s]} {(UPF_NC if p.get("nc") else UPF)[s]}' for s in species]
    L.append('CELL_PARAMETERS angstrom')
    L += ['  %.10f %.10f %.10f' % tuple(v) for v in st['cell_A']]
    L.append('ATOMIC_POSITIONS crystal')
    L += ['  %-3s %.10f %.10f %.10f' % (s, *f) for s, f in zip(st['symbols'], frac(st))]
    if kgrid:
        L += ['K_POINTS automatic', '  %d %d %d 0 0 0' % tuple(kgrid)]
    else:
        L += ['K_POINTS tpiba', f'  {len(kpts)}'] + ['  %.8f %.8f %.8f 1.0' % tuple(k) for k in kpts]
    return '\n'.join(L) + '\n'


STEPS_IWO = """steps() {{
  run_pw relax {nk_rel}
  python qeio.py converged relax.out || {{ log "relaxation did not finish; later steps skipped"; return 0; }}
  for t in scf_k4 bands spin_k3; do python qeio.py newgeom $t.tmpl relax.out > $t.in; done
  clean_tmp
  run_pw scf_k4 {nk_k4} || return 0
  run_pdos iwo "$JOB" "$(python qeio.py fermi scf_k4.out)" {nk_k4}
  run_pw bands {nk_bands}
  clean_tmp
  run_pw spin_k3 {nk_spin}
}}
"""
STEPS_SLAB_SCF = """steps() {{
  run_pw scf {nk} || return 0
  run_ppavg slab "$JOB" {awin:.4f}
  run_pw bands {nk_bands}
}}
"""
STEPS_SLAB_RELAX = """steps() {{
  run_pw vcrelax {nk}
  python qeio.py converged vcrelax.out || {{ log "relaxation did not finish; later steps skipped"; return 0; }}
  for t in scf bands; do python qeio.py newgeom $t.tmpl vcrelax.out > $t.in; done
  clean_tmp
  run_pw scf {nk} || return 0
  run_ppavg slab "$JOB" {awin:.4f}
  run_pw bands {nk_bands}
}}
"""


STEPS_IWO_SLAB = """steps() {{
  run_pw relax 1
  python qeio.py converged relax.out || {{ log "relaxation did not finish; later steps skipped"; return 0; }}
  for t in scf bands; do python qeio.py newgeom $t.tmpl relax.out > $t.in; done
  clean_tmp
  export FORCE_CPU=1   # one QE version (CPU 7.5) for SCF, pp.x and projwfc.x; one pool (NCPU may be odd)
  run_pw scf 1 || return 0
  run_ppavg slab "$JOB" {awin:.4f}
  run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" 1
  run_pw bands 1
}}
"""


def make_job(name, st, kind, ncpu, out, p):
    d = out / name
    d.mkdir(parents=True, exist_ok=True)
    a = float(np.linalg.norm(st['cell_A'][0]))
    minr = p['min_ranks']
    nelec = sum(ZVAL[s] for s in st['symbols'])
    info = {'job': name, 'kind': kind, 'n_atoms': len(st['symbols']), 'n_electrons': nelec}
    if kind == 'nc_scf':   # norm-conserving PBE or HSE06 single point (name contains 'hse' -> HSE06)
        bulk = len(st['symbols']) == 40
        kg = [3, 3, 3] if bulk else p['k_slab']
        occ = nelec // 2
        q = dict(p, nc=True, rho_factor=4, ecut=int(name.split('_e')[-1]) if '_e' in name else 80)
        if 'hse' in name:
            nq = 3 if '_q3' in name else 1
            # ecutfock = 2 x ecutwfc: with the default (ecutrho = 320 Ry) the slab's real-space EXX buffers ran the
            # 94 GB H100 out of memory (nc_hse_slab1_e80, 2026-09-30); bulk and slab use the same value
            q['extra_sys'] = f"input_dft = 'hse', nqx1 = {nq}, nqx2 = {nq}, nqx3 = {nq if bulk else 1}, ecutfock = {2 * q['ecut']}"
        (d / 'scf.in').write_text(pw_input(st, 'scf', 'nc', q, kgrid=kg, nbnd=occ + 16, verbosity='high'))
        (d / 'steps.sh').write_text('steps() {\n  run_pw scf 1\n}\n')
        info.update(k=kg, occupied_bands=occ, ecut=q['ecut'])
        return info
    if kind == 'hse_scf':
        bulk = len(st['symbols']) == 40
        kg = [3, 3, 3] if bulk else p['k_slab']
        nq = 3 if name.endswith('nq3') else 1
        occ = nelec // 2
        q = dict(p, extra_sys=f"input_dft = 'hse', nqx1 = {nq}, nqx2 = {nq}, nqx3 = {nq if bulk else 1}, ecutfock = {4 * p['ecut']}")
        (d / 'scf.in').write_text(pw_input(st, 'scf', 'hse', q, kgrid=kg, nbnd=occ + 16, verbosity='high'))
        (d / 'steps.sh').write_text('steps() {\n  run_pw scf 1\n}\n')
        info.update(k=kg, nq=nq, occupied_bands=occ)
        return info
    if kind == 'iwo_bulk':
        k3, k4 = p['k_bulk']
        n3, n4 = n_irr(st, k3), n_irr(st, k4)
        kb = klist(a, [[1, 0, 0], [1, 1, 0], [1, 1, 1]])
        nk = dict(nk_rel=npool(ncpu, n3, minr), nk_k4=npool(ncpu, n4, minr),
                  nk_bands=npool(ncpu, len(kb), minr), nk_spin=npool(ncpu, 2 * n3, minr))
        (d / 'relax.in').write_text(pw_input(st, 'relax', 'rel', p, kgrid=k3))
        (d / 'scf_k4.tmpl').write_text(pw_input(st, 'scf', 'iwo', p, kgrid=k4, verbosity='high'))
        (d / 'bands.tmpl').write_text(pw_input(st, 'bands', 'iwo', p, kpts=kb, verbosity='high'))
        (d / 'spin_k3.tmpl').write_text(pw_input(st, 'scf', 'spin', dict(p, beta=0.2), kgrid=k3, nspin=2))
        (d / 'steps.sh').write_text(STEPS_IWO.format(**nk))
        info.update(irreducible_k={'k3': n3, 'k4': n4}, pools=nk)
    else:
        ks = p['k_slab']
        n = min(n_irr(st, ks), MAXPOOL.get(name, 99))
        occ = nelec // 2
        kb = klist(a, [[1, 0, 0], [1, 1, 0]])
        awin = a / 4 / BOHR
        nk = dict(nk=npool(ncpu, n, minr), nk_bands=npool(ncpu, len(kb), minr), awin=awin)
        if kind == 'iwo_slab':
            # nbnd explicit (2026-10-03): the QE default for smearing (~1.2 x occupied, ~798 bands at 2 nm) would exceed the
            # 94 GB H100 NVL; the 2 nm vc-relax with occupied+8 = 672 bands already used 86 GB of GPU memory
            (d / 'relax.in').write_text(pw_input(st, 'relax', 'rel', p, kgrid=ks, nbnd=(nelec + 1) // 2 + 12))
            (d / 'scf.tmpl').write_text(pw_input(st, 'scf', 'slab', p, kgrid=ks, nbnd=occ + 24, verbosity='high'))
            (d / 'bands.tmpl').write_text(pw_input(st, 'bands', 'slab', p, kpts=kb, nbnd=occ + 24, verbosity='high'))
            (d / 'steps.sh').write_text(STEPS_IWO_SLAB.format(**nk))
        elif kind == 'bench_scf':
            (d / 'scf.in').write_text(pw_input(st, 'scf', 'slab', p, kgrid=ks, nbnd=occ + 16, verbosity='high'))
            (d / 'steps.sh').write_text('steps() {\n  run_pw scf 1\n}\n')
        elif kind == 'slab_scf':
            (d / 'scf.in').write_text(pw_input(st, 'scf', 'slab', p, kgrid=ks, nbnd=occ + 16, verbosity='high'))
            (d / 'bands.in').write_text(pw_input(st, 'bands', 'slab', p, kpts=kb, nbnd=occ + 16, verbosity='high'))
            (d / 'steps.sh').write_text(STEPS_SLAB_SCF.format(**nk))
        else:
            (d / 'vcrelax.in').write_text(pw_input(st, 'vc-relax', 'vcr', p, kgrid=ks, nbnd=occ + 8))
            (d / 'scf.tmpl').write_text(pw_input(st, 'scf', 'slab', p, kgrid=ks, nbnd=occ + 16, verbosity='high'))
            (d / 'bands.tmpl').write_text(pw_input(st, 'bands', 'slab', p, kpts=kb, nbnd=occ + 16, verbosity='high'))
            (d / 'steps.sh').write_text(STEPS_SLAB_RELAX.format(**nk))
        info.update(irreducible_k=n, occupied_bands=occ, pools=nk)
    return info


def toy_structures():
    a = 3.17
    bulk = {'cell_A': [[a, 0, 0], [0, a, 0], [0, 0, a]], 'symbols': ['W', 'W'],
            'positions_A': [[0, 0, 0], [a / 2 + 0.05, a / 2, a / 2]]}
    c = a + 8.0
    slab = {'cell_A': [[a, 0, 0], [0, a, 0], [0, 0, c]], 'symbols': ['W', 'W', 'W'],
            'positions_A': [[0, 0, 4.0], [a / 2, a / 2, 4.0 + a / 2 + 0.05], [0, 0, 4.0 + a]]}
    return {'toy_bulk': bulk, 'toy_slab': slab}


def main():
    toy = sys.argv[1] == '--toy'
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    here = Path(__file__).resolve().parent
    if toy:
        structs, jobs = toy_structures(), TOY_JOBS
        # W metal needs denser k-points and wider smearing than the doped oxide to converge quickly
        base = dict(ecut=40, conv='1.0d-6', min_ranks=1, k_bulk=([4, 4, 4], [6, 6, 6]), k_slab=[6, 6, 1],
                    degauss=0.02)
    else:
        sdir = Path(sys.argv[1])
        jobs = [j for j in JOBS if len(sys.argv) < 4 or j[0] in sys.argv[3].split(',')]
        # only the selected jobs' structures are loaded (later structures, e.g. the 2 nm IWO slab, may not exist yet)
        structs = {j[1]: json.loads((sdir / f'{j[1]}.json').read_text()) for j in jobs}
        base = dict(ecut=71, conv='1.0d-9', min_ranks=4, k_bulk=([3, 3, 3], [4, 4, 4]), k_slab=[3, 3, 1])
    table, infos = [], []
    for name, sname, kind, ncpu, mem, disk, flav, limit, *g in jobs:
        gpus = g[0] if g else 0
        p = dict(base)
        # electron_maxstep bounds the cost of an SCF that does not converge (normal: 15-40 iterations)
        if kind == 'iwo_bulk':
            p.update(occ='smearing', beta=0.3, maxstep=100)
        elif kind in ('hse_scf', 'nc_scf'):    # insulating, fixed occupations; beta 0.3 bulk-like
            p.update(occ='fixed', beta=0.3, localtf=len(structs[sname]['symbols']) != 40, maxstep=150)
        elif kind == 'iwo_slab':   # W donates 3 electrons: metallic slab -> smearing; Davidson bands (CG ~14 h on slabs)
            p.update(occ='smearing', beta=0.2, localtf=True, maxstep=150, bands_cg=False)
        else:
            p.update(occ='smearing' if toy else 'fixed', beta=0.2, localtf=True, maxstep=150, bands_cg=False)
        infos.append(make_job(name, structs[sname], kind, ncpu, out, p))
        # GPU-save -> HDF5 converter for pp.x; inside the job directory, so continuations and CPU twins
        # (dft_flow.sh copies whole job directories) carry it without a change to jobs.sub
        (out / name / 'dat2h5.py').write_bytes((here / 'common' / 'dat2h5.py').read_bytes().replace(b'\r\n', b'\n'))
        table.append(f'{name} {ncpu} {mem} {disk} {flav} {limit} {gpus}')
    (out / 'jobs.txt').write_text('\n'.join(table) + '\n')
    (out / 'jobs_info.json').write_text(json.dumps(infos, indent=1))
    for f in ('driver.sh', 'qeio.py', 'jobs.sub'):          # LF line endings for the Linux workers
        (out / f).write_bytes((here / 'common' / f).read_bytes().replace(b'\r\n', b'\n'))
    pseudo = out / 'pseudo'
    pseudo.mkdir(exist_ok=True)
    for f in list(UPF.values()) + list(UPF_NC.values()):
        shutil.copy(here.parent.parent / 'pseudo' / f, pseudo / f)
    print(json.dumps(infos, indent=1))


if __name__ == '__main__':
    main()
