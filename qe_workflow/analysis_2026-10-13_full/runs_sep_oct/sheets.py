"""Readable data sheets (sheets/<run>.md), the master table (MASTER_TABLE.md, master.json) and the checks against
RESULTS_LOG.md for the 41 Sep-Oct run folders, built from out/<run>.json (extract_runs.py). Every logged value used in
a check is quoted with its RESULTS_LOG line, and the quotation is verified against that line (a wrong citation stops
the build). Usage: python sheets.py
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT, SH = HERE / 'out', HERE / 'sheets'
QE = HERE.parents[1]
RL = QE / 'cern_htcondor' / 'results' / 'RESULTS_LOG.md'
RLL = RL.read_text(encoding='utf-8').splitlines()

PURPOSE = {
    'slab1_v15': 'Vacuum-convergence test, unrelaxed 1 nm In2O3(001) slab (H/OH-terminated, 96 atoms), 15 A vacuum: SCF, planar average, bands (CG).',
    'slab1_v25': 'Vacuum-convergence test, unrelaxed 1 nm slab, 25 A vacuum (the Lin et al. value): SCF, planar average, bands (CG).',
    'slab1_v35': 'Vacuum-convergence test, unrelaxed 1 nm slab, 35 A vacuum: SCF, planar average, bands (Davidson).',
    'gpu_bench_v15': 'GPU benchmark: the slab1_v15 SCF on one H100 NVL (QE 7.3.1 GPU) to compare cost and results with the CPU run.',
    'iwo_W8b': '80-atom bulk IWO (In31 W O48, 3.1 % W) with W on the 8b site: relax (k3), SCF k4, projwfc/PDOS, bands, spin-polarised k3.',
    'iwo_W8b_partial': 'Copy of the running iwo_W8b relax output taken 2026-09-28 (preliminary site preference); plus the k4 SCF and PDOS as fetched later.',
    'iwo_W24d': '80-atom bulk IWO with W on the 24d site: relax (k3), SCF k4, projwfc/PDOS, bands, spin-polarised k3.',
    'iwo_W24d_partial': 'Copy of the running iwo_W24d relax output taken 2026-09-28 (preliminary site preference).',
    'slab1_relax_gpu': 'vc-relax (atoms + in-plane cell, 2Dxy) of the 1 nm slab on a GPU after CPU steps; final SCF, planar average, bands (in-plane CB mass).',
    'cpu_relax_snapshots': 'Snapshots of the CPU vc-relax of slab1_relax and slab2_relax taken before the GPU continuations.',
    'slab1r_final_cpu': 'CPU final SCF of the relaxed 1 nm slab geometry (QE 7.5) with planar average and bands (EA/IP, gap, mass).',
    'iwo_slab1_W24d_x1': '1 nm IWO slab (W on the central 24d site): relax on one H100; the following final SCF wrote a runaway output and was stopped.',
    'iwo_slab1_final_cpu': 'CPU final SCF, planar average, projwfc/PDOS and bands of the relaxed 1 nm IWO slab.',
    'nc_pbe_bulk_e80': 'Norm-conserving (SG15) PBE single point of bulk In2O3 at the PAW-PBE geometry, 80 Ry (HSE reference).',
    'nc_pbe_bulk_e100': 'NC PBE bulk single point at 100 Ry (cutoff check of the NC set).',
    'nc_pbe_slab1_e80': 'NC PBE single point of the relaxed 1 nm slab, 80 Ry.',
    'nc_hse_bulk_e80': 'HSE06 bulk single point (NC, 80 Ry, EXX q 1x1x1, default ecutfock).',
    'nc_hse_bulk_f160_e80': 'HSE06 bulk with ecutfock 160 Ry (ecutfock check).',
    'nc_hse_bulk_q3_e80': 'HSE06 bulk with EXX q 3x3x3 and default ecutfock (did not run to completion).',
    'nc_hse_bulk_q3_f160_e80': 'HSE06 bulk with EXX q 3x3x3 and ecutfock 160 Ry (q-sampling check).',
    'nc_hse_slab1_e80': 'HSE06 1 nm slab, default ecutfock (stopped after the PBE pre-step).',
    'nc_hse_slab1_f160_e80': 'HSE06 1 nm slab, ecutfock 160 Ry (the slab HSE gap used for the ratio).',
    'slab2_relax_c2': 'vc-relax (2Dxy) of the 2 nm slab on one H100 NVL (rerun after the lost slab2_relax_x1), final SCF, planar average, bands.',
    'iwo_slab2_W24d_checkpoint': 'EOS checkpoint of the 2 nm IWO slab relax (one H100 NVL): converged relax.out.',
    'slab2r_final_cpu_checkpoint': 'CPU cross-check SCF of the relaxed 2 nm slab with planar average; its bands step was held for memory.',
    'iwo_slab2_final_cpu': 'Recovery CPU SCF + planar average + projwfc of the relaxed 2 nm IWO slab (conv_thr 1e-8, beta 0.1).',
    'iwo_slab2_final_cpu_failed_pools': 'First attempt of iwo_slab2_final_cpu: stopped after 60 s by an MPI pool error.',
    'slab2r_pdos_cpu': 'CPU SCF + planar average + projwfc of the relaxed 2 nm slab (surface-state check).',
    'slabL1_relax_gpu': 'Superseded 0.51 nm slab relax (marker only; replaced by slabL1_relax_v2).',
    'slabL2_relax_gpu': 'Superseded 0.75 nm slab relax (marker only; replaced by slabL2_relax_v2).',
    'slabL1_relax_v2': '0.51 nm slab (one cation plane): vc-relax, SCF, planar average, projwfc/PDOS, bands.',
    'slabL2_relax_v2': '0.75 nm slab (two cation planes): vc-relax, SCF, planar average, projwfc/PDOS, bands.',
    'live_snapshots': 'Laptop-side 15-min snapshots of the running 2 nm jobs (snapshot_jobs.sh): slab2_relax_c2 (+CPU twin), slab2r_final_cpu (incl. the held bands step), slab2r_pdos_cpu, iwo_slab2_W24d (+CPU twin, incl. its killed final SCF), iwo_slab2_final_cpu.',
    'canary_ckpt_checkpoint': 'Workflow test (toy 2-atom W cell): EOS checkpoint written during a relax.',
    'canary_cont': 'Workflow test (toy 3-atom W slab cell, 2Dxy vc-relax): continuation logic, with nstep = 3 forcing an unconverged stop.',
    'canary_cont_c1': 'Workflow test: second segment of the continuation test (restarts from vcrelax_prev.in).',
    'canary_race': 'Workflow test: GPU half of a GPU/CPU twin race (toy W cell relax).',
    'canary_race__cpu': 'Workflow test: CPU half of the twin race.',
    'canary_stuck': 'Workflow test: a job that only sleeps 4500 s (stuck-job detection).',
    'ckpt_write_test_checkpoint': 'EOS write test from lxplus (one text file).',
    'failed_20260927a': 'First submission of 2026-09-27 (iwo_W8b, iwo_W24d, slab1_relax, slab2_relax, each fetched twice): all failed at MPI start.',
}


FAILURE = {
    'failed_20260927a': 'All eight relax.out files hold only the Open MPI/PRRTE message "There are not enough slots available in the system to satisfy the 32 slots that were requested" (relax.out lines 1-30): mpirun asked for 32 ranks on nodes that granted fewer slots; pw.x never started; every step rc 1. The "_refetch" copies are byte-identical.',
    'iwo_slab2_final_cpu_failed_pools': 'pw.x stopped 60 s after start with "Error in routine mp_start_pools (1): invalid number of pools, parent_nproc /= nproc_pool * npool" (scf.out line 43): 33 MPI ranks cannot be split into -nk 2 pools. This is cluster 12835131; the successful rerun with -nk 1 is cluster 12835211 (folder iwo_slab2_final_cpu).',
    'iwo_slab1_W24d_x1': 'The relax (GPU, 1 rank) converged. The follow-on SCF was started with 11 MPI ranks and never produced pw.x output: UCX reported that InfiniBand memory registration failed (ibv_reg_mr ... Cannot allocate memory; the message suggests raising max locked memory, ulimit -l) and flooded scf.out (a restrictive memlock limit is plausible but its value was not measured); the driver stopped it after 60 s at > 2 GB (rc 143), yet the packed file is 9.38 GB (see below; the NUL-byte count describes the file content, not its cause). The geometry was carried on in iwo_slab1_final_cpu.',
    'iwo_slab1_final_cpu': 'SCF, planar average and projwfc completed; the bands step (Davidson) aborted with "Error in routine cdiaghg (417): problems computing cholesky" (bands.out line 480: factorisation of the computed overlap matrix failed; underlying cause unresolved, not evidence of a defective geometry or pseudopotential) and MPI_ABORT (rc 161). No in-plane mass for the W slab.',
    'nc_hse_bulk_q3_e80': 'MPI_INIT failed before pw.x started (scf.out): the requested "sm" BTL component was not available in that Open MPI runtime and mca_bml_base_open() failed on b9pgpun003; rc 1 after 60 s. The q 3x3x3 bulk HSE was obtained instead by nc_hse_bulk_q3_f160_e80.',
    'nc_hse_slab1_e80': 'The PBE pre-step converged (34 iterations, gap 1.8068 eV); at the first EXX step the GPU ran out of memory: "Accelerator Fatal Error: call to cuMemAlloc returned error 2 (CUDA_ERROR_OUT_OF_MEMORY)" in newd_gpu (scf.out tail), rc 1 after 7 min on one H100 NVL. The default ecutfock (= ecutrho 320 Ry) did not fit; the ecutfock 160 Ry run (nc_hse_slab1_f160_e80) is the one used.',
    'cpu_relax_snapshots': 'Non-fatal: the CPU vc-relax printed UCX errors at start (bnxt_re0: ibv_create_cq failed; uct_iface_open failed) and then ran; the snapshots stop mid-run (no JOB DONE) because the GPU continuations superseded them.',
    'canary_stuck': 'By design: steps() only sleeps 4500 s (stuck-job detection test); no pw.x run.',
    'canary_cont': 'By design: nstep = 3 in vcrelax.in stops the toy 3-atom W vc-relax after 3 SCF steps ("The maximum number of steps has been reached", vcrelax.out line 1607); qeio.py then reports it unconverged and the driver logs "relaxation did not finish; later steps skipped" (the continuation logic under test).',
    'canary_cont_c1': 'By design: the continuation segment starts from the last geometry of canary_cont (vcrelax_prev.in = the previous input; vcrelax.in carries the new positions) with nstep = 3 again, and again stops on the step limit ("relaxation did not finish").',
    'slabL1_relax_gpu': 'Removed 2026-10-05T21:14Z, superseded by slabL1_relax_v2 (identical inputs); no results kept (SUPERSEDED.txt).',
    'slabL2_relax_gpu': 'Removed 2026-10-05T21:14Z, superseded by slabL2_relax_v2 (identical inputs); no results kept (SUPERSEDED.txt).',
    'live_snapshots': 'Snapshots of running jobs: incomplete outputs are expected (no JOB DONE). The iwo_slab2_W24d final SCF (QE 7.5 CPU build: steps.sh exports FORCE_CPU=1 before it; 33 ranks on the H100 node; no GPU line in scf.out) stops at iteration 86 with the accuracy at 8e-9 to 1e-8 Ry: it was removed by the faulty stuck rule (RESULTS_LOG 2026-10-05). The slab2r_final_cpu bands step (-nk 4) stops early: held for memory.',
}


# lines inserted above the entry that was first when the references were written (it was at line 3); original lines kept
RL_INSERTED_TOP = next(i for i, l in enumerate(RLL, 1) if l.startswith('## 2026-10-13 03:40Z: H-L crystalline oxygen-vacancy test scored')) - 3
ERRATA_ORIG_LINES = {384, 403, 420}   # original lines corrected by the 2026-10-14 erratum entry


def lg(line, text):
    if text not in RLL[line - 1]:
        line += RL_INSERTED_TOP
    assert text in RLL[line - 1], f'RESULTS_LOG:{line} lacks {text!r}'
    return f'RESULTS_LOG.md:{line}'


def g(d, *path, default=None):
    for p in path:
        if isinstance(d, dict) and p in d:
            d = d[p]
        elif isinstance(d, list) and isinstance(p, int) and -len(d) <= p < len(d):
            d = d[p]
        else:
            return default
    return d


def wall_h(s):
    """'1d16h53m' / '7h39m' / '46m31.63s' -> hours."""
    if not s:
        return None
    t = 0.0
    for v, u in re.findall(r'([\d.]+)\s*([dhms])', s):
        t += float(v) * {'d': 24, 'h': 1, 'm': 1 / 60, 's': 1 / 3600}[u]
    return round(t, 3)


def CHECKS():
    """(run, what, getter, logged, tolerance or 'eq', reference)."""
    C = []

    def add(run, what, fn, logged, tol, ref):
        C.append((run, what, fn, logged, tol, ref))
    for run, ln, txt, it, gap, ea, ip in (('slab1_v15', 583, '| 15 A | 0.9586 | 3.4331 | 4.3917 | 46 |', 46, 0.9586, 3.4331, 4.3917),
                                          ('slab1_v25', 584, '| 25 A | 0.9586 | 3.4332 | 4.3918 | 64 |', 64, 0.9586, 3.4332, 4.3918),
                                          ('slab1_v35', 585, '| 35 A | 0.9586 | 3.4332 | 4.3918 | 77 |', 77, 0.9586, 3.4332, 4.3918)):
        ref = lg(ln, txt)
        add(run, 'SCF iterations', lambda r: g(r, 'pw', 'scf.out', 'final_step', 'converged_iterations'), it, 'eq', ref)
        add(run, 'gap (eV)', lambda r: round(g(r, 'pw', 'scf.out', 'final_step', 'LUMO_eV') - g(r, 'pw', 'scf.out', 'final_step', 'HOMO_eV'), 4), gap, 5e-5, ref)
        add(run, 'EA (eV)', lambda r, run=run: g(r, 'avg_dat', f'{run}_avg.dat', 'EA_eV'), ea, 1.5e-4, ref)
        add(run, 'IP (eV)', lambda r, run=run: g(r, 'avg_dat', f'{run}_avg.dat', 'IP_eV'), ip, 1.5e-4, ref)
    ref = lg(564, '16 CPUs, 4 pools. SCF 1 h 48 min wall (77 iterations); bands 1 h 29 min')
    add('slab1_v35', 'CPUs (driver)', lambda r: g(r, 'driver', 'slab1_v35_driver.log', 'cpus'), 16, 'eq', ref)
    add('slab1_v35', 'pools', lambda r: g(r, 'pw', 'scf.out', 'header', 'npool'), 4, 'eq', ref)
    add('slab1_v35', 'SCF wall (h)', lambda r: wall_h(g(r, 'pw', 'scf.out', 'timing', 'PWSCF', 'wall')), 1.8, 0.01, ref)
    add('slab1_v35', 'bands wall (h)', lambda r: wall_h(g(r, 'pw', 'bands.out', 'timing', 'PWSCF', 'wall')), 1.4833, 0.01, ref)
    ref = lg(565, '8 symmetry operations (with inversion); 4 irreducible k-points')
    add('slab1_v35', 'symmetry ops', lambda r: int(g(r, 'pw', 'scf.out', 'symmetry').split()[0]), 8, 'eq', ref)
    add('slab1_v35', 'irreducible k', lambda r: g(r, 'pw', 'scf.out', 'kpoints', 'n'), 4, 'eq', ref)
    ref = lg(568, 'VBM -1.9695 eV, CBM -1.0109 eV')
    add('slab1_v35', 'VBM (eV)', lambda r: g(r, 'pw', 'scf.out', 'final_step', 'HOMO_eV'), -1.9695, 5e-5, ref)
    add('slab1_v35', 'CBM (eV)', lambda r: g(r, 'pw', 'scf.out', 'final_step', 'LUMO_eV'), -1.0109, 5e-5, ref)
    add('slab1_v35', 'E_vac (eV)', lambda r: g(r, 'avg_dat', 'slab1_v35_avg.dat', 'E_vac_eV'), 2.422, 5e-4, lg(569, 'E_vac = 2.422 eV'))
    ref = lg(589, 'the bands step took 13.7-13.9 h on 16 CPUs, against 1.5 h with Davidson for slab1_v35')
    for run in ('slab1_v15', 'slab1_v25'):
        add(run, 'bands wall (h), logged range 13.7-13.9', lambda r: wall_h(g(r, 'pw', 'bands.out', 'timing', 'PWSCF', 'wall')), 13.8, 0.1, ref)
    # W bulk
    ref = lg(536, '| E relax, 3x3x3 (Ry) | -15496.3476466 | -15496.3666037 |')
    add('iwo_W8b', 'E relax k3 (Ry)', lambda r: g(r, 'pw', 'relax.out', 'bfgs', 'final_energy'), -15496.3476466, 5e-8, ref)
    add('iwo_W24d', 'E relax k3 (Ry)', lambda r: g(r, 'pw', 'relax.out', 'bfgs', 'final_energy'), -15496.3666037, 5e-8, ref)
    ref = lg(537, '| E SCF, 4x4x4 (Ry) | -15496.34766084 | -15496.36660308 |')
    add('iwo_W8b', 'E SCF k4 (Ry)', lambda r: g(r, 'pw', 'scf_k4.out', 'final_step', 'E_Ry'), -15496.34766084, 5e-9, ref)
    add('iwo_W24d', 'E SCF k4 (Ry)', lambda r: g(r, 'pw', 'scf_k4.out', 'final_step', 'E_Ry'), -15496.36660308, 5e-9, ref)
    ref = lg(539, '| spin-polarized, 3x3x3: E (Ry), M | -15496.34931870, 0.74 muB | -15496.36803594, 0.62 muB |')
    add('iwo_W8b', 'E spin k3 (Ry)', lambda r: g(r, 'pw', 'spin_k3.out', 'final_step', 'E_Ry'), -15496.3493187, 5e-9, ref)
    add('iwo_W24d', 'E spin k3 (Ry)', lambda r: g(r, 'pw', 'spin_k3.out', 'final_step', 'E_Ry'), -15496.36803594, 5e-9, ref)
    add('iwo_W8b', 'total magnetisation', lambda r: g(r, 'pw', 'spin_k3.out', 'final_step', 'total_magnetization'), 0.74, 5e-3, ref)
    add('iwo_W24d', 'total magnetisation', lambda r: g(r, 'pw', 'spin_k3.out', 'final_step', 'total_magnetization'), 0.62, 5e-3, ref)
    ref = lg(538, '6 x 1.972 | 1.892 x 2, 1.902 x 2, 2.152 x 2 (mean 1.982)')
    add('iwo_W8b', 'W-O mean (A)', lambda r: g(r, 'pw', 'relax.out', 'final_geometry', 'bonds', 'W-O', 'mean'), 1.972, 5e-4, ref)
    add('iwo_W24d', 'W-O mean (A)', lambda r: g(r, 'pw', 'relax.out', 'final_geometry', 'bonds', 'W-O', 'mean'), 1.982, 5e-4, ref)
    ref = lg(558, 'dE = E(8b) - E(24d) = +0.01896 Ry')
    add('iwo_W8b_partial', 'E relax (Ry), part of dE 0.01896', lambda r: g(r, 'pw', 'relax.out', 'bfgs', 'final_energy'), -15496.3476466, 5e-8, lg(557, '-15496.3476466'))
    add('iwo_W24d_partial', 'E relax (Ry), part of dE 0.01896', lambda r: g(r, 'pw', 'relax.out', 'bfgs', 'final_energy'), -15496.3666037, 5e-8, lg(557, '-15496.3666037'))
    # 1 nm
    ref = lg(515, 'A100 for 54 BFGS steps, after 13 CPU steps')
    add('slab1_relax_gpu', 'BFGS steps (GPU)', lambda r: int(re.search(r'and\s+(\d+) bfgs', g(r, 'pw', 'vcrelax.out', 'bfgs', 'converged')).group(1)), 54, 'eq', ref)
    add('slab1_relax_gpu', 'GPU model', lambda r: 'A100' in (g(r, 'driver', 'slab1_relax_gpu_driver.log', 'gpu') or ''), True, 'eq', ref)
    add('cpu_relax_snapshots', 'CPU BFGS steps before the GPU (slab1)', lambda r: max((s.get('bfgs_steps') or 0) for s in g(r, 'pw', 'slab1_relax_vcrelax.out', 'steps')), 13, 'eq', ref)
    add('slab1_relax_gpu', 'final enthalpy (Ry)', lambda r: g(r, 'pw', 'vcrelax.out', 'bfgs', 'final_enthalpy'), -11888.81122571, 5e-9, lg(516, '-11888.81122571'))
    add('slab1_relax_gpu', 'total force at convergence (Ry/bohr)', lambda r: conv_step(r, 'vcrelax.out')['total_force_Ry_bohr'], 0.0061, 5e-5, lg(517, 'Residual force 0.0061 Ry/bohr'))
    ref = lg(518, 'In-plane cell 10.336 x 10.335 A')
    add('slab1_relax_gpu', 'in-plane a (A)', lambda r: g(r, 'pw', 'vcrelax.out', 'final_geometry', 'cell_lengths_A', 0), 10.336, 5e-4, ref)
    add('slab1_relax_gpu', 'in-plane b (A) (last-digit rounding allowed)', lambda r: g(r, 'pw', 'vcrelax.out', 'final_geometry', 'cell_lengths_A', 1), 10.335, 6e-4, ref)
    add('slab1r_final_cpu', 'gap (eV)', lambda r: round(g(r, 'pw', 'scf.out', 'final_step', 'LUMO_eV') - g(r, 'pw', 'scf.out', 'final_step', 'HOMO_eV'), 4), 1.7885, 5e-5, lg(522, '1.7885 eV'))
    ref = lg(481, 'relax on GPU 27 BFGS steps, E = -12238.28910896 Ry')
    add('iwo_slab1_W24d_x1', 'BFGS steps', lambda r: int(re.search(r'and\s+(\d+) bfgs', g(r, 'pw', 'relax.out', 'bfgs', 'converged')).group(1)), 27, 'eq', ref)
    add('iwo_slab1_W24d_x1', 'final energy (Ry)', lambda r: g(r, 'pw', 'relax.out', 'bfgs', 'final_energy'), -12238.28910896, 5e-8, ref)
    add('iwo_slab1_W24d_x1', 'W-O mean (A) (log: 1.880 x2, 1.907 x2, 2.212 x2)', lambda r: g(r, 'pw', 'relax.out', 'final_geometry', 'bonds', 'W-O', 'mean'),
        round((1.880 + 1.907 + 2.212) / 3, 4), 5e-4, lg(485, '1.880 x 2, 1.907 x 2, 2.212 x 2 A'))
    add('iwo_slab1_final_cpu', 'bands step rc', lambda r: next(s['rc'] for s in g(r, 'driver', 'iwo_slab1_final_cpu_driver.log', 'steps') if s['step'] == 'bands'),
        161, 'eq', lg(483, 'The bands run aborted (Davidson, rc 161)'))
    # HSE
    ref = lg(469, '| PBE | 0.9204 eV | 1.8068 eV | 0.8864 eV |')
    for run, val in (('nc_pbe_bulk_e80', 0.9204), ('nc_pbe_slab1_e80', 1.8068)):
        add(run, 'gap on SCF grid (eV)', lambda r: round(g(r, 'pw', 'scf.out', 'final_step', 'LUMO_eV') - g(r, 'pw', 'scf.out', 'final_step', 'HOMO_eV'), 4), val, 5e-5, ref)
    ref = lg(470, '| HSE06 (q = 1, ecutfock 160 Ry) | 2.1080 eV | 3.0475 eV | 0.9395 eV |')
    for run, val in (('nc_hse_bulk_e80', 2.108), ('nc_hse_slab1_f160_e80', 3.0475)):
        add(run, 'HSE gap on SCF grid (eV)', lambda r: round(g(r, 'pw', 'scf.out', 'final_step', 'LUMO_eV') - g(r, 'pw', 'scf.out', 'final_step', 'HOMO_eV'), 4), val, 5e-5, ref)
    add('nc_hse_bulk_q3_f160_e80', 'HSE gap q3 (eV), log -42 meV vs q1', lambda r: round(g(r, 'pw', 'scf.out', 'final_step', 'LUMO_eV') - g(r, 'pw', 'scf.out', 'final_step', 'HOMO_eV'), 4),
        2.0662, 5e-5, lg(476, 'bulk HSE gap 2.0662 eV (-42 meV)'))
    # 2 nm
    ref = lg(426, '70 BFGS steps, 72 SCF cycles, 41.5 h wall time')
    add('slab2_relax_c2', 'BFGS steps', lambda r: int(re.search(r'and\s+(\d+) bfgs', g(r, 'pw', 'vcrelax.out', 'bfgs', 'converged')).group(1)), 70, 'eq', ref)
    add('slab2_relax_c2', 'SCF cycles', lambda r: int(re.search(r'in\s+(\d+) scf', g(r, 'pw', 'vcrelax.out', 'bfgs', 'converged')).group(1)), 72, 'eq', ref)
    add('slab2_relax_c2', 'vc-relax wall (h)', lambda r: wall_h(g(r, 'pw', 'vcrelax.out', 'timing', 'PWSCF', 'wall')), 41.5, 0.05, ref)
    add('slab2_relax_c2', 'final enthalpy (Ry)', lambda r: g(r, 'pw', 'vcrelax.out', 'bfgs', 'final_enthalpy'), -27035.66548, 5e-6, lg(427, '-27035.66548 Ry'))
    add('slab2_relax_c2', 'total force at convergence (Ry/bohr)', lambda r: conv_step(r, 'vcrelax.out')['total_force_Ry_bohr'], 0.0072, 5e-5, lg(428, 'Total force: 0.0072 Ry/bohr'))
    ref = lg(429, 'In-plane cell: 10.318 x 10.309 A')
    add('slab2_relax_c2', 'in-plane a (A)', lambda r: g(r, 'pw', 'vcrelax.out', 'final_geometry', 'cell_lengths_A', 0), 10.318, 5e-4, ref)
    add('slab2_relax_c2', 'in-plane b (A) (last-digit rounding allowed)', lambda r: g(r, 'pw', 'vcrelax.out', 'final_geometry', 'cell_lengths_A', 1), 10.309, 6e-4, ref)
    ref = lg(430, 'H to H 19.62 A, O to O 18.21 A')
    add('slab2_relax_c2', 'H-H thickness (A)', lambda r: g(r, 'pw', 'vcrelax.out', 'final_geometry', 'slab', 'thickness_H_H_A'), 19.62, 5e-3, ref)
    add('slab2_relax_c2', 'O-O thickness (A)', lambda r: g(r, 'pw', 'vcrelax.out', 'final_geometry', 'slab', 'thickness_O_O_A'), 18.21, 5e-3, ref)
    add('slab2_relax_c2', 'final SCF wall (h)', lambda r: wall_h(g(r, 'pw', 'scf.out', 'timing', 'PWSCF', 'wall')), 56 / 60, 0.01, lg(432, 'The final SCF ran on the GPU in 56 min'))
    ref = lg(416, 'finished all steps after 182892 s (50.8 h); bands run 8 h 22 min on the GPU, rc 0')
    add('slab2_relax_c2', 'total job time (s)', lambda r: g(r, 'driver', 'slab2_relax_c2_driver.log', 'total_s'), 182892, 'eq', ref)
    add('slab2_relax_c2', 'bands wall (h)', lambda r: wall_h(g(r, 'pw', 'bands.out', 'timing', 'PWSCF', 'wall')), 8 + 22 / 60, 0.01, ref)
    add('slab2_relax_c2', 'gap (eV)', lambda r: round(g(r, 'pw', 'scf.out', 'final_step', 'LUMO_eV') - g(r, 'pw', 'scf.out', 'final_step', 'HOMO_eV'), 4), 1.2239, 5e-5, lg(435, 'Gap: 1.2239 eV'))
    ref = lg(436, 'EA = 4.495 eV, IP = 5.719 eV')
    add('slab2_relax_c2', 'EA (eV)', lambda r: g(r, 'avg_dat', 'slab2_relax_c2_avg.dat', 'EA_eV'), 4.495, 5e-4, ref)
    add('slab2_relax_c2', 'IP (eV)', lambda r: g(r, 'avg_dat', 'slab2_relax_c2_avg.dat', 'IP_eV'), 5.719, 5e-4, ref)
    ref = lg(403, 'The relax converged in 28 BFGS steps (16 h 49 min). Final energy -27385.2061874810 Ry')
    add('iwo_slab2_W24d_checkpoint', 'BFGS steps', lambda r: int(re.search(r'and\s+(\d+) bfgs', g(r, 'pw', 'relax.out', 'bfgs', 'converged')).group(1)), 28, 'eq', ref)
    add('iwo_slab2_W24d_checkpoint', 'relax wall (h)', lambda r: wall_h(g(r, 'pw', 'relax.out', 'timing', 'PWSCF', 'wall')), 16 + 49 / 60, 0.01, ref)
    add('iwo_slab2_W24d_checkpoint', 'final energy (Ry)', lambda r: g(r, 'pw', 'relax.out', 'bfgs', 'final_energy'), -27385.206187481, 5e-9, ref)
    ref = lg(382, 'Max displacement 0.43 A (W 0.09 A). W-O 1.866, 1.874, 2.19 A, each twice, mean 1.977 A (W6+)')
    add('iwo_slab2_W24d_checkpoint', 'max displacement (A)', lambda r: g(r, 'pw', 'relax.out', 'final_geometry', 'displacement_vs_initial', 'max_A'), 0.43, 5e-3, ref)
    add('iwo_slab2_W24d_checkpoint', 'W displacement (A)', lambda r: g(r, 'pw', 'relax.out', 'final_geometry', 'displacement_vs_initial', 'by_element_max_A', 'W'), 0.09, 5e-3, ref)
    add('iwo_slab2_W24d_checkpoint', 'W-O mean (A)', lambda r: g(r, 'pw', 'relax.out', 'final_geometry', 'bonds', 'W-O', 'mean'), 1.977, 5e-4, ref)
    ref = lg(410, 'The SCF (24 CPUs, 9 h 57 min, 70 iterations) gives HOMO/LUMO 0.0474 / 1.2713 eV')
    add('slab2r_final_cpu_checkpoint', 'CPUs (driver)', lambda r: g(r, 'driver', 'slab2r_final_cpu_driver.log', 'cpus'), 24, 'eq', ref)
    add('slab2r_final_cpu_checkpoint', 'SCF wall (h)', lambda r: wall_h(g(r, 'pw', 'scf.out', 'timing', 'PWSCF', 'wall')), 9 + 57 / 60, 0.01, ref)
    add('slab2r_final_cpu_checkpoint', 'SCF iterations', lambda r: g(r, 'pw', 'scf.out', 'final_step', 'converged_iterations'), 70, 'eq', ref)
    add('slab2r_final_cpu_checkpoint', 'HOMO (eV)', lambda r: g(r, 'pw', 'scf.out', 'final_step', 'HOMO_eV'), 0.0474, 5e-5, ref)
    add('slab2r_final_cpu_checkpoint', 'LUMO (eV)', lambda r: g(r, 'pw', 'scf.out', 'final_step', 'LUMO_eV'), 1.2713, 5e-5, ref)
    ref = lg(420, 'Cluster 12827176: slab2r_final_cpu (16 CPUs, 72 GB)')
    add('slab2r_final_cpu_checkpoint', 'CPUs allocated / MPI ranks (driver, HTCondor and pw.x agree on 24; log 410 also says 24; the logged 16 is the request_cpus of cern_htcondor/jobs/gen_iwoslab2/jobs.txt:1, found 2026-10-14)', lambda r: g(r, 'driver', 'slab2r_final_cpu_driver.log', 'cpus'), 16, 'eq', ref)
    ref = lg(450, 'slab2_relax_c2 (H100 NVL) is at 40 BFGS steps after 23 h. Its CPU twin had done 2 steps')
    add('live_snapshots', 'slab2_relax_c2 CPU twin: completed SCF (geometry) steps in its last snapshot (BFGS counter reached 1)', lambda r: sum(1 for s in g(r, 'pw', 'slab2_relax_c2__cpu/vcrelax.out', 'steps') if s.get('E_Ry') is not None), 2, 'eq', ref)
    ref = lg(411, 'held for memory in the bands step (-nk 4, 72 GB) after 10.1 h')
    add('live_snapshots', 'slab2r_final_cpu bands step pools (log -nk 4)', lambda r: next((s['nk'] for s in g(r, 'driver', 'slab2r_final_cpu/slab2r_final_cpu_driver.log', 'steps') if s['step'] == 'bands'), None), 4, 'eq', ref)
    ref = lg(384, 'iwo_slab2_final_cpu (cluster 12835131; 24 CPUs requested, 33 allocated, 100 GB)')
    add('iwo_slab2_final_cpu', 'HTCondor cluster of the run whose outputs are used (log: 12835131)', lambda r: run_cluster(r), '12835131.0', 'eq', ref)
    add('iwo_slab2_final_cpu', 'CPUs allocated', lambda r: g(r, 'driver', 'iwo_slab2_final_cpu_driver.log', 'cpus'), 33, 'eq', ref)
    ref = lg(385, 'conv_thr 1e-8 Ry instead of 1e-9 (5.7e-11 Ry per atom), and mixing_beta 0.1 instead of 0.2')
    add('iwo_slab2_final_cpu', 'conv_thr (input)', lambda r: float(g(r, 'inputs', 'scf.in', 'namelists', 'ELECTRONS', 'conv_thr').replace('d', 'e')), 1e-8, 'eq', ref)
    add('iwo_slab2_final_cpu', 'mixing_beta (input)', lambda r: float(g(r, 'inputs', 'scf.in', 'namelists', 'ELECTRONS', 'mixing_beta')), 0.1, 'eq', ref)
    ref = lg(329, 'SCF (24 CPUs, 2 pools, 10 h 41 min wall)')
    add('slab2r_pdos_cpu', 'CPUs (driver)', lambda r: g(r, 'driver', 'slab2r_pdos_cpu_driver.log', 'cpus'), 24, 'eq', ref)
    add('slab2r_pdos_cpu', 'pools', lambda r: g(r, 'pw', 'scf.out', 'header', 'npool'), 2, 'eq', ref)
    add('slab2r_pdos_cpu', 'SCF wall (h)', lambda r: wall_h(g(r, 'pw', 'scf.out', 'timing', 'PWSCF', 'wall')), 10 + 41 / 60, 0.01, ref)
    ref = lg(379, 'ran its final SCF on the CPU (QE 7.5, 33 MPI, 1 pool, conv_thr 1e-9)')
    add('live_snapshots', 'iwo_slab2_W24d final-SCF snapshot: QE version (log: 7.5 CPU)', lambda r: g(r, 'pw', 'iwo_slab2_W24d/scf.out', 'header', 'version'), 'v.7.5', 'eq', ref)
    add('live_snapshots', 'iwo_slab2_W24d final-SCF snapshot: MPI processes (log: 33)', lambda r: g(r, 'pw', 'iwo_slab2_W24d/scf.out', 'header', 'mpi_processes'), 33, 'eq', ref)
    add('live_snapshots', 'iwo_slab2_W24d final SCF ran on the GPU? (scf.out GPU lines; node had an H100)', lambda r: bool(g(r, 'pw', 'iwo_slab2_W24d/scf.out', 'header', 'gpu_lines')),
        True, 'eq', lg(403, 'The final SCF on the GPU started at 06:42Z'))
    add('live_snapshots', 'iwo_slab2_W24d final-SCF snapshot: SCF iterations reached (log: 86)', lambda r: g(r, 'pw', 'iwo_slab2_W24d/scf.out', 'steps', 0, 'iterations'), 86, 'eq', lg(379, 'At 09:21Z it was at iteration 86'))
    return C


def conv_step(r, name):
    """Step at which BFGS converged (the last step before the final SCF of a vc-relax, else the last step)."""
    st = g(r, 'pw', name, 'steps')
    if g(r, 'pw', name, 'bfgs', 'final_scf'):
        return st[-2]
    return st[-1]


def run_cluster(r):
    """Cluster whose driver start time matches the run (first condor sample within 15 min before the driver start)."""
    import datetime as dt
    drv = next(iter(r['driver'].values()))
    t0 = dt.datetime.fromisoformat(drv['start'].replace('Z', ''))
    best = None
    for c in r['condor']:
        t = dt.datetime.fromisoformat(c['first'].replace('Z', ''))
        if t <= t0 + dt.timedelta(minutes=5) and (best is None or t > best[0]):
            best = (t, c['id'])
    return best[1] if best else None


def evaluate():
    rows = []
    for run, what, fn, logged, tol, ref in CHECKS():
        r = json.loads((OUT / f'{run}.json').read_text())
        try:
            v = fn(r)
        except Exception as ex:   # noqa: BLE001
            v = f'n/a ({type(ex).__name__})'
        if tol == 'eq':
            ok = v == logged
        else:
            ok = isinstance(v, (int, float)) and abs(v - logged) <= tol
        status = 'match' if ok else 'DIFFERS'
        if not ok and int(ref.split(':')[1]) - RL_INSERTED_TOP in ERRATA_ORIG_LINES:
            status = 'DIFFERS (dated erratum 2026-10-14 in RESULTS_LOG)'
        rows.append({'run': run, 'quantity': what, 're_derived': v, 'logged': logged, 'reference': ref, 'status': status})
    return rows


# ------------------------------------------------------------------ sheet rendering
def fmt(x, nd=6):
    if isinstance(x, float):
        return f'{x:.{nd}g}'
    return str(x)


def sheet(r, checks):
    run = r['run']
    W = [f"# {run}", '', f"**Purpose.** {PURPOSE.get(run, '-')}", '', f"Folder `{r['folder']}`; data `runs_sep_oct/out/{run}.json` (+ `{run}_arrays.json.gz`: eigenvalues and "
         'occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).', '']
    # files
    W += ['## Files', '', '| path | bytes | sha256 (16) | source | kind |', '|---|---|---|---|---|']
    for f in r['files']:
        W.append(f"| {f['path']} | {f['size']} | {f['sha256_16']} | {f['src']} | {f['kind']} |")
    for t in r['tarballs']:
        same = [m['name'] for m in t['members'] if m.get('equals_loose') is True]
        diff = [m['name'] for m in t['members'] if m.get('equals_loose') is False]
        only = [m['name'] for m in t['members'] if m.get('equals_loose') is None and 'kind' not in m]
        big = [f"{m['name']} ({m['size']} B: {m['kind']})" for m in t['members'] if 'too large' in m.get('kind', '')]
        npd = sum(1 for m in t['members'] if m.get('kind') == 'pdos')
        W.append(f"\nTarball `{t['tarball']}` ({t['size']} B, sha256 {t['sha256'][:16]}): {len(t['members'])} members; identical to the loose copy: {len(same)}; "
                 f"DIFFERENT from the loose copy: {diff or 'none'}; only in the tarball (parsed from it): {only or 'none'}; pdos members: {npd}" + (f"; not loaded: {big}" if big else ''))
    for k, v in r['pdos'].items():
        W.append(f"\nPDOS set `{k}`: {v['n_files']} files.")
    # resources
    W += ['', '## Resources and run history', '']
    for k, d in r['driver'].items():
        W.append(f"- `{k}`: host {d.get('host')}, {d.get('cpus')} CPUs, wall limit {d.get('limit_s')} s, GPU: {d.get('gpu', 'none (CPU)')}, job total {d.get('total_s')} s, start {d.get('start')}")
        for s in d['steps']:
            W.append(f"  - step {s['step']}: -nk {s['nk']}, max_seconds {s['max_seconds']}, start {s['start']}, end {s.get('end')}, rc {s.get('rc')}, {s.get('time', '')}")
        extra = [l for l in d['lines'] if not re.search(r'pw\.x (\S+) (start|end)|job \S+ host|pw\.x:/|GPU mode|steps finished', l)]
        for l in extra:
            W.append(f"  - log: {l}")
    for c in r['condor']:
        W.append(f"- HTCondor {c['job']} {c['id']}: {c['cpus']} CPUs, {c.get('gpus')} GPU; seen {c['first']} to {c['last']} ({c['samples']} samples); states {c['states']} "
                 f"(1 idle, 2 running, 3 removed, 5 held); max scf_it {c['max_scf_it']}, max BFGS {c['max_bfgs']}; steps {c['steps']}; hw {c['gpu_hw'] or ''} {c['cpu_hw'] or ''}")
    if not r['condor']:
        W.append('- HTCondor: no entry in status_history.jsonl (it starts 2026-09-28T14:19Z).')
    for k, v in r['steps_sh'].items():
        W.append(f"- `{k}`: `{' '.join(v.split())}`")
    if r['mpi_errors']:
        for k, v in r['mpi_errors'].items():
            W.append(f"- MPI start failure in `{k}`: {' / '.join(v['key_lines'][:4])}; signatures {{{', '.join(f'{w}: line {x["first"][0][0]}' for w, x in v['warnings'].items())}}}")
    if run in FAILURE:
        W += ['', f"**What failed and why (from the files above).** {FAILURE[run]}"]
    if run == 'iwo_slab1_W24d_x1':
        rw = json.loads((OUT / 'iwo_slab1_W24d_x1_runaway_scf.json').read_text())
        W += ['', f"**Runaway scf.out (tar member, {rw['member_size_bytes']} B, sha256 {rw['sha256'][:16]}; streamed, never written to disk):** {rw['newline_count']} lines; "
              f"{rw['nul_bytes']} NUL bytes ({100 * rw['nul_bytes'] / rw['member_size_bytes']:.1f} %, first at offset {rw['first_nul_offset']}); marker counts {rw['marker_counts_approx']}; "
              f"most frequent lines: " + '; '.join(f"'{x[0][:110]}' x{x[1]}" for x in rw['top_patterns'][:3]) + '. Source: `out/iwo_slab1_W24d_x1_runaway_scf.json` (stream_runaway.py, stream_runaway_nul.py).']
    # calculations
    for name, p in r['pw'].items():
        H, P, fs = p['header'], p['params'], p['final_step']
        W += ['', f"## Calculation `{name}` ({p['calc_type']})", '']
        W.append(f"QE {H.get('version')} started {H.get('start_date')} {H.get('start_time')}; {H.get('mpi_processes')} MPI x {H.get('threads_per_mpi')} threads on {H.get('nodes')} node(s); "
                 f"pools {H.get('npool', 1)}; R&G division {H.get('RG_division', '-')}; node memory {H.get('node_memory_MiB')} MiB; {H.get('fft_decomposition', '')}; "
                 f"{H.get('subspace_diag', '')}; GPU: {'; '.join(H.get('gpu_lines', [])) or 'no GPU line'}. Completed: {'JOB DONE' if p['done'] else 'NO (no JOB DONE)'}; terminated {p.get('terminated')}; "
                 f"PWSCF time {g(p, 'timing', 'PWSCF')}; output lines {p['n_lines']}.")
        inp = r['inputs'].get(name.replace('.out', '.in'))
        if inp:
            W += ['', '**Input settings** (every namelist variable):', '']
            for nl, d in inp['namelists'].items():
                W.append(f"- &{nl}: " + ', '.join(f'{k} = {v}' for k, v in d.items()))
            for c, v in inp['cards'].items():
                W.append(f"- {c}: {json.dumps(v)[:400]}")
            if 'atomic_positions_summary' in inp:
                W.append(f"- ATOMIC_POSITIONS: {json.dumps(inp['atomic_positions_summary'])}")
        W.append(f"- Echoed parameters: " + '; '.join(f'{k} = {v}' for k, v in P.items()))
        W.append('- Pseudopotentials: ' + '; '.join(f"{q['element']} {q['file'].split('/')[-1]} md5 {q.get('md5')} ({q.get('type')}, Z {q.get('Zval')})" for q in p['pseudos'])
                 + (f" (re-read {p['pseudo_rereads']} times in the final SCF)" if p['pseudo_rereads'] else ''))
        W.append(f"- Symmetry: {p.get('symmetry')}; k points: {g(p, 'kpoints', 'line')} (sum of weights {g(p, 'kpoints', 'sum_wk')}); FFT: {g(p, 'fft', 'dense')} / {g(p, 'fft', 'smooth')}")
        W.append(f"- RAM (pw.x estimate): {p['ram']}; start: {p.get('start')}")
        if p.get('bands_calc'):
            W.append(f"- Band-structure run: {p['bands_calc']}")
        if p['exx']['cycles']:
            W.append(f"- HSE/EXX: {len(p['exx']['cycles'])} outer cycles, dexx trace {p['exx'].get('dexx_trace')}, Fock energy trace (Ry) {p['exx'].get('fock_trace_Ry')}, "
                     f"reached {p['exx'].get('reached', False)}, {p['exx'].get('grid', '')}")
        st = p['steps']
        if st:
            W += ['', f"**Convergence** ({len(st)} SCF{' + BFGS' if p['bfgs'] else ''}): {p['bfgs'].get('converged') or p['bfgs'].get('failure') or ''} "
                  f"{p['bfgs'].get('criteria', '')} final energy {p['bfgs'].get('final_energy')} final enthalpy {p['bfgs'].get('final_enthalpy')} "
                  f"{'max steps reached' if p['bfgs'].get('max_steps_reached') else ''}", '',
                  '| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |',
                  '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
            for j, s in enumerate(st):
                cell = s.get('cell_A')
                ab = f"{cell[0][0]:.4f}, {cell[1][1]:.4f}" if cell else ''
                W.append(f"| {j} | {s.get('iterations')} | {fmt(s.get('acc_final_Ry'), 2)} | {s.get('E_Ry', s.get('E_bang2_Ry'))} | {s.get('enthalpy_new_Ry', '')} | "
                         f"{fmt(s.get('force_max_component_Ry_bohr', ''), 4)} | {fmt(s.get('force_rms_component_Ry_bohr', ''), 3)} | {s.get('total_force_Ry_bohr', '')} | "
                         f"{s.get('total_scf_correction_Ry_bohr', '')} | {s.get('pressure_kbar', '')} | {s.get('volume_A3', '')} | {ab} | {fmt(s.get('trust_radius_bohr', ''), 4)} |")
            W += ['', '**Final energies** (last SCF): ' + ', '.join(f'{k} = {v}' for k, v in fs.items() if k.endswith(('_Ry', '_eV')) or 'magnet' in k or k in ('negative_rho', 'converged_iterations'))]
            if fs.get('stress_kbar'):
                W.append(f"- stress tensor (kbar): {fs['stress_kbar']}")
        b = p.get('bands')
        if b:
            W += ['', f"**Bands** (final eigenvalues, every k in the arrays file): {json.dumps(b)}"]
        if p.get('final_geometry'):
            W += ['', f"**Final geometry** (vs `{g(p, 'final_geometry', 'reference_input')}`): {json.dumps(p['final_geometry'])}"]
        if p['warnings'] or p.get('errors'):
            W += ['', '**Warnings/errors**: ' + '; '.join(f"{k} x{v['count']} (first: line {v['first'][0][0]} '{v['first'][0][1][:90]}')" for k, v in p['warnings'].items())]
            if p.get('errors'):
                W.append(f"- QE/MPI error lines: {p['errors']}")
            if p['messages']:
                W.append(f"- messages: {[m[1][:120] for m in p['messages'][:4]]}")
    if r['inputs']:
        W += ['', '## Input geometries', '']
        for k, v in r['inputs'].items():
            if 'geometry' in v:
                W.append(f"- `{k}`: {json.dumps(v['geometry'])}")
    if r.get('geometry_consistency'):
        W += ['', f"Geometry consistency (input of the follow-on step vs relax final coordinates): {json.dumps(r['geometry_consistency'])}"]
    for k, v in r['projwfc'].items():
        W += ['', f"## projwfc `{k}`", '', f"natomwfc {v.get('natomwfc')}, nbnd {v.get('nbnd')}, nkstot {v.get('nkstot')}, states {v.get('n_states')}, spilling {v.get('spilling')}, "
              f"Loewdin total {v.get('lowdin_total_sum')}, {v.get('time')}, done {v.get('done')}", '',
              '| element | n | total charge mean (min-max) | s | p | d |', '|---|---|---|---|---|---|']
        for e, q in (v.get('lowdin_by_element') or {}).items():
            W.append(f"| {e} | {q['n']} | {q['total']['mean']} ({q['total']['min']}-{q['total']['max']}) | {q['s']['mean']} | {q['p']['mean']} | {q['d']['mean']} |")
    for k, v in r['pdos'].items():
        W += ['', f"## PDOS `{k}`", '', json.dumps({kk: vv for kk, vv in v.items() if kk != 'by_element_l'}), '', '| element, l | files | states in window | states below reference |', '|---|---|---|---|']
        for e, q in v['by_element_l'].items():
            W.append(f"| {e} | {q['files']} | {q['integral_window']} | {q['integral_below_ref']} |")
    for k, v in r['avg_dat'].items():
        W += ['', f"## Planar average `{k}`", '', json.dumps(v)]
    for k, v in r['pp_avg'].items():
        if 'output' in v:
            W.append(f"- `{k}`: done {v['output']['done']}; " + ' / '.join(v['output']['key_lines'][:5]))
        elif 'input' in v:
            W.append(f"- `{k}` input: `{' '.join(v['input'].split())}`")
    if r['other']:
        W += ['', '## Other files', ''] + [f"- `{k}`: {v[:300]!r}" for k, v in r['other'].items()]
    ch = [c for c in checks if c['run'] == run]
    if ch:
        W += ['', '## Checks against RESULTS_LOG', '', '| quantity | re-derived | logged | reference | status |', '|---|---|---|---|---|']
        for c in ch:
            W.append(f"| {c['quantity']} | {c['re_derived']} | {c['logged']} | {c['reference']} | {c['status']} |")
    return '\n'.join(W) + '\n'


def findings(checks):
    """Key findings, every number read from out/*.json."""
    from extract_runs import RUNS
    R = {run: json.loads((OUT / f'{run}.json').read_text()) for run in RUNS}
    nfiles = sum(len(r['files']) for r in R.values())
    pws = [(run, k, p) for run, r in R.items() for k, p in r['pw'].items()]
    md5 = {}
    for _, _, p in pws:
        for q in p['pseudos']:
            md5.setdefault(q['file'].split('/')[-1], set()).add(q.get('md5'))
    diff_tar = [(run, m['name']) for run, r in R.items() for t in r['tarballs'] for m in t['members'] if m.get('equals_loose') is False]
    gb, cb = R['gpu_bench_v15']['pw']['scf.out'], R['slab1_v15']['pw']['scf.out']
    rw = json.loads((OUT / 'iwo_slab1_W24d_x1_runaway_scf.json').read_text())
    hse = R['nc_hse_bulk_e80']['pw']['scf.out']['exx']
    d = [c for c in checks if c['status'] != 'match']
    F = ['## Key findings (read from out/*.json)', '',
         f"- Coverage: {len(R)} folders, {nfiles} files (tarball members included), {len(pws)} pw.x outputs "
         f"({sum(1 for *_, p in pws if p['header'].get('version') == 'v.7.5')} QE 7.5, {sum(1 for *_, p in pws if p['header'].get('version') == 'v.7.3.1')} QE 7.3.1 GPU), "
         f"{sum(len(r['projwfc']) for r in R.values())} projwfc outputs, {sum(len(r['pdos']) for r in R.values())} PDOS sets; every tarball member compared byte-for-byte with its loose copy: "
         f"{'all identical' if not diff_tar else diff_tar}.",
         f"- Each pseudopotential file has one MD5 in every run (PAW pslibrary 1.0.0 set; SG15 ONCV 1.2 set for the NC/HSE checks): " + '; '.join(f"{k} {sorted(v)[0]}" + ('' if len(v) == 1 else f' (+{len(v) - 1} other MD5)') for k, v in sorted(md5.items())) + '.',
         f"- GPU benchmark: the slab1_v15 SCF on one H100 (QE 7.3.1) took {gb['timing']['PWSCF']['wall']} against {cb['timing']['PWSCF']['wall']} on 16 CPU cores (QE 7.5), "
         f"{gb['final_step']['converged_iterations']} vs {cb['final_step']['converged_iterations']} iterations, energy difference {abs(gb['final_step']['E_Ry'] - cb['final_step']['E_Ry']):.1e} Ry.",
         f"- HSE runs converge the EXX loop in {len(hse['cycles'])} outer cycles (bulk, dexx {hse['dexx_trace'][0]:.1e} -> {hse['dexx_trace'][-1]:.1e} Ry).",
         f"- iwo_slab1_W24d_x1: its packed scf.out is {rw['member_size_bytes'] / 1e9:.2f} GB with no pw.x line (Program PWSCF x{rw['marker_counts_approx']['Program PWSCF']}): "
         f"{rw['marker_counts_approx']['UCX  ERROR']} UCX ERROR lines (UCX: InfiniBand memory registration failed; restrictive memlock plausible, not measured) and {rw['nul_bytes'] / 1e9:.2f} GB of NUL bytes from offset {rw['first_nul_offset']}; "
         "the driver log says it stopped the step at > 2 GB after 60 s (rc 143). Streamed only; never written to disk.",
         '- Failure causes identified in the files (details in the sheets): MPI slot shortage (failed_20260927a, 32 ranks), invalid pool split 33/2 (iwo_slab2_final_cpu_failed_pools), '
         'MPI_INIT failure, "sm" BTL not available in that Open MPI runtime (nc_hse_bulk_q3_e80), CUDA out of memory at the first EXX step with the default ecutfock (nc_hse_slab1_e80), '
         'cdiaghg Cholesky factorisation failure in the 1 nm W slab bands (rc 161; cause unresolved), UCX memory-registration error flood (iwo_slab1_W24d_x1 final SCF; cause plausible, not measured).',
         f"- Checks against RESULTS_LOG: {len(checks)} quoted values re-derived, {len(checks) - len(d)} match; {len(d)} differ:"]
    for c in d:
        F.append(f"  - {c['run']}: {c['quantity']}: re-derived {c['re_derived']}, logged {c['logged']} ({c['reference']}).")
    return F


def main():
    SH.mkdir(exist_ok=True)
    checks = evaluate()
    (OUT / 'checks_vs_results_log.json').write_text(json.dumps(checks, indent=1, default=str))
    master = []
    from extract_runs import RUNS
    for run in RUNS:
        r = json.loads((OUT / f'{run}.json').read_text())
        (SH / f'{run}.md').write_text(sheet(r, checks), encoding='utf-8')
        main_pw = max(r['pw'].items(), key=lambda kv: kv[1]['n_scf_steps'], default=(None, None))
        p = main_pw[1] or {}
        fs = p.get('final_step', {}) if p else {}
        drv = next(iter(r['driver'].values()), {}) if r['driver'] else {}
        geo = (p.get('final_geometry') if p else None) or next((v['geometry'] for v in r['inputs'].values() if 'geometry' in v), {})
        master.append({'run': run, 'purpose': PURPOSE.get(run, ''), 'main_output': main_pw[0], 'qe': g(p, 'header', 'version'),
                       'hardware': (drv.get('gpu') or (f"{drv.get('cpus')} CPUs" if drv else '-')), 'host': drv.get('host'),
                       'atoms': g(geo, 'n_atoms'), 'composition': g(geo, 'composition'), 'ecut': g(p, 'params', 'kinetic-energy cutoff'),
                       'k': g(p, 'kpoints', 'n'), 'smearing': g(p, 'kpoints', 'smearing') or 'fixed', 'xc': g(p, 'params', 'Exchange-correlation'),
                       'scf_steps': g(p, 'n_scf_steps'), 'bfgs': g(p, 'bfgs', 'converged'), 'E_final_Ry': fs.get('E_Ry', fs.get('E_bang2_Ry')),
                       'gap_or_EF': (round(fs['LUMO_eV'] - fs['HOMO_eV'], 4) if fs.get('LUMO_eV') is not None and fs.get('HOMO_eV') is not None else fs.get('E_F_eV')),
                       'job_total_s': drv.get('total_s'), 'step_rcs': [s.get('rc') for s in drv.get('steps', [])],
                       'n_pw_outputs': len(r['pw']), 'n_files': len(r['files']), 'checks': sum(1 for c in checks if c['run'] == run),
                       'differs': sum(1 for c in checks if c['run'] == run and c['status'] != 'match')})
    (OUT / 'master.json').write_text(json.dumps(master, indent=1, default=str))
    W = ['# Master table: CERN runs 20 Sep - 7 Oct 2026 (41 folders)', ''] + findings(checks) + ['',
         'One row per folder; details in `sheets/<run>.md` and `out/<run>.json`. Main output = the pw.x output with the most SCF steps. '
         'Gap = LUMO - HOMO of its last SCF (insulators) or E_F (smearing). All crystalline; COMPUTED. Checks: RESULTS_LOG quotations verified line by line.', '',
         '| run | purpose | main output | QE | hardware | atoms | composition | ecut | k | smearing | SCF steps | BFGS | E final (Ry) | gap or E_F (eV) | job s | step rc | checks (differ) |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for m in master:
        W.append(f"| [{m['run']}](sheets/{m['run']}.md) | {m['purpose'][:90]} | {m['main_output']} | {m['qe']} | {m['hardware']} | {m['atoms']} | "
                 f"{m['composition']} | {m['ecut']} | {m['k']} | {m['smearing']} | {m['scf_steps']} | {(m['bfgs'] or '')[16:]} | {m['E_final_Ry']} | {m['gap_or_EF']} | "
                 f"{m['job_total_s']} | {m['step_rcs']} | {m['checks']} ({m['differs']}) |")
    W += ['', '## Checks against RESULTS_LOG (all)', '', '| run | quantity | re-derived | logged | reference | status |', '|---|---|---|---|---|---|']
    for c in checks:
        W.append(f"| {c['run']} | {c['quantity']} | {c['re_derived']} | {c['logged']} | {c['reference']} | {c['status']} |")
    (HERE / 'MASTER_TABLE.md').write_text('\n'.join(W) + '\n', encoding='utf-8')
    print('checks', len(checks), 'differ', sum(1 for c in checks if c['status'] != 'match'))
    for c in checks:
        if c['status'] != 'match':
            print('  DIFF', c['run'], c['quantity'], c['re_derived'], c['logged'], c['reference'])


if __name__ == '__main__':
    main()
