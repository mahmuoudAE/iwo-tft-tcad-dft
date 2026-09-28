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
         ('slab2_relax_gpu1', 'slab2_v25', 'slab_relax', 8, 48000, 40000000, 'testmatch', 259200, 1)]
# memory: every pool holds complete wavefunctions of its k-points. slab2_v25 with 4 pools used 95.8 GB
# (held at a 48 GB limit, 2026-09-27), i.e. ~24 GB per pool, so slab 2 runs with at most 2 pools.
MAXPOOL = {'slab2_v25': 2, 'slab2_relax': 2}
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
         f"  verbosity = '{verbosity}', tprnfor = .true., tstress = .true., max_seconds = 1.0d8"]
    if calc in ('relax', 'vc-relax'):
        L.append('  nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3')
    L += ['/', '&SYSTEM',
          f"  ibrav = 0, nat = {len(st['symbols'])}, ntyp = {len(species)}, ecutwfc = {p['ecut']}, ecutrho = {8 * p['ecut']}"]
    L.append("  occupations = 'fixed'" if p['occ'] == 'fixed'
             else f"  occupations = 'smearing', smearing = 'mv', degauss = {p.get('degauss', 0.01)}")
    if nbnd:
        L.append(f'  nbnd = {nbnd}')
    if nspin == 2:
        L.append(f"  nspin = 2, starting_magnetization({species.index('W') + 1}) = 0.5")
    L += ['/', '&ELECTRONS',
          f"  conv_thr = {p['conv']}, mixing_beta = {p['beta']}, electron_maxstep = {p.get('maxstep', 300)}"
          + (", mixing_mode = 'local-TF'" if p.get('localtf') else '')
          # non-SCF bands: Davidson aborted locally for bulk In2O3 (2026-09-27); CG is robust
          + (", diagonalization = 'cg'" if calc == 'bands' else ''), '/']
    if calc in ('relax', 'vc-relax'):
        L += ['&IONS', "  ion_dynamics = 'bfgs'", '/']
    if calc == 'vc-relax':
        L += ['&CELL', "  cell_dynamics = 'bfgs', cell_dofree = '2Dxy', press_conv_thr = 0.5", '/']
    L.append('ATOMIC_SPECIES')
    L += [f'  {s} {MASS[s]} {UPF[s]}' for s in species]
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


def make_job(name, st, kind, ncpu, out, p):
    d = out / name
    d.mkdir(parents=True, exist_ok=True)
    a = float(np.linalg.norm(st['cell_A'][0]))
    minr = p['min_ranks']
    nelec = sum(ZVAL[s] for s in st['symbols'])
    info = {'job': name, 'kind': kind, 'n_atoms': len(st['symbols']), 'n_electrons': nelec}
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
        if kind == 'bench_scf':
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
        structs = {j[1]: json.loads((sdir / f'{j[1]}.json').read_text()) for j in JOBS}
        jobs = [j for j in JOBS if len(sys.argv) < 4 or j[0] in sys.argv[3].split(',')]
        base = dict(ecut=71, conv='1.0d-9', min_ranks=4, k_bulk=([3, 3, 3], [4, 4, 4]), k_slab=[3, 3, 1])
    table, infos = [], []
    for name, sname, kind, ncpu, mem, disk, flav, limit, *g in jobs:
        gpus = g[0] if g else 0
        p = dict(base)
        # electron_maxstep bounds the cost of an SCF that does not converge (normal: 15-40 iterations)
        if kind == 'iwo_bulk':
            p.update(occ='smearing', beta=0.3, maxstep=100)
        else:
            p.update(occ='smearing' if toy else 'fixed', beta=0.2, localtf=True, maxstep=150)
        infos.append(make_job(name, structs[sname], kind, ncpu, out, p))
        table.append(f'{name} {ncpu} {mem} {disk} {flav} {limit} {gpus}')
    (out / 'jobs.txt').write_text('\n'.join(table) + '\n')
    (out / 'jobs_info.json').write_text(json.dumps(infos, indent=1))
    for f in ('driver.sh', 'qeio.py', 'jobs.sub'):          # LF line endings for the Linux workers
        (out / f).write_bytes((here / 'common' / f).read_bytes().replace(b'\r\n', b'\n'))
    pseudo = out / 'pseudo'
    pseudo.mkdir(exist_ok=True)
    for f in UPF.values():
        shutil.copy(here.parent.parent / 'pseudo' / f, pseudo / f)
    print(json.dumps(infos, indent=1))


if __name__ == '__main__':
    main()
