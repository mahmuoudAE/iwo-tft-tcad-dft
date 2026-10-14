#!/usr/bin/env python3
"""A23 (i): PBE reference run directories for the amorphous bulks (register A23, frozen 2026-10-10T21:06Z).

usage: python3 make_bulkref.py [--root DIR] aIO_bulk_s1 aIWO_bulk_s1

Reads   <root>/results/<name>/<name>_qe.txt (+ _qc.json: QC PASS) and <root>/specs/spec_<name>.json (mode 'bulk').
Copies  the repaired relax machinery of the A15 pilot, read-only, from <root>/runs/aIO_0p8_s1:
          relax_node_pilot.sh -> relax_node_bulk.sh (byte-identical: exit 0 CONVERGED / 1 CONTINUE / 2 FAILED)
          steps_relax.sh (A19: CONVERGED only with 'bfgs converged'), geomsel.py (validated-geometry restart)
        and <root>/common/steps_final.sh (the slab FINAL steps: scf, planar average, projwfc).
Writes  <root>/runs/<name>/: relax.in, final.tmpl, relax.sub, final.sub, <name>.dag, relax_node_bulk.sh,
        steps_relax.sh, geomsel.py, steps_final.sh, PROVENANCE, logs/.  Refuses if runs/<name> exists.
Imports read_qe_txt, qe_input, VAL, PP, SPECIES_ORDER from common/make_dft.py (make_dft.py is not edited).

Settings (A23 (i)):
  relax : atoms only (fixed cell), PAW pslibrary 1.0.0, 60/480 Ry, k 2x2x2, Gaussian 0.005 Ry (both cells; the aIWO
          slabs relaxed with MV 0.01: declared difference), BFGS, forc_conv_thr 1e-3 Ry/bohr; electrons as the A15
          pilot (beta 0.1, local-TF, mixing_ndim 12, electron_maxstep 300, conv_thr 1e-7), verbosity 'high';
          1 GPU (H100|H200|A100, MIG slices excluded as in D-24), <= 20 h segments, DAG 'RETRY RELAX 8 UNLESS-EXIT 2'
  final : 71/568 Ry, k 2x2x2, Gaussian 0.005 Ry, nbnd = ceil(1.3 x N_el/2), verbosity 'high' (D-24 target), CPU 32,
          100 GB, common/final_node.sh + steps_final.sh (A15 gate: submitted with 'hold = True')
"""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

ROOT = Path.home() / 'iwo_amorph'
if '--root' in sys.argv:
    i = sys.argv.index('--root')
    ROOT = Path(sys.argv[i + 1]).resolve()
    del sys.argv[i:i + 2]
COMMON = ROOT / 'common'
PILOT = ROOT / 'runs' / 'aIO_0p8_s1'
sys.path.insert(0, str(COMMON))
import make_dft  # noqa: E402  (read_qe_txt, qe_input, VAL, PP, SPECIES_ORDER; not edited)

GAUSS = "occupations = 'smearing', smearing = 'gaussian', degauss = 0.005"      # A23: both cells, relax and final
ELEC_SERIES = "  conv_thr = 1.0d-7, mixing_beta = 0.2, electron_maxstep = 200, mixing_mode = 'local-TF'"
ELEC_PILOT = ("  conv_thr = 1.0d-7, mixing_beta = 0.1, electron_maxstep = 300, mixing_mode = 'local-TF', "
              "mixing_ndim = 12")
K = (2, 2, 2)
COPY = {'relax_node_bulk.sh': PILOT / 'relax_node_pilot.sh', 'steps_relax.sh': PILOT / 'steps_relax.sh',
        'geomsel.py': PILOT / 'geomsel.py', 'steps_final.sh': COMMON / 'steps_final.sh'}

RELAX_SUB = """universe                = vanilla
executable              = {run}/relax_node_bulk.sh
arguments               = $(seg) 72000
should_transfer_files   = YES
transfer_input_files    = {common}/driver.sh, {common}/qeio.py, {common}/dat2h5.py, {common}/pseudo, relax.in, steps_relax.sh, geomsel.py
when_to_transfer_output = ON_EXIT
transfer_output_files   = relax_s$(seg)_results.tar.gz, relax.in, RELAX_STATUS, relax.out, SEGMENT_SUMMARY
output                  = logs/relax_s$(seg).$(ClusterId).out
error                   = logs/relax_s$(seg).$(ClusterId).err
log                     = logs/relax.log
request_cpus            = 8
request_memory          = 64 GB
request_disk            = 60 GB
request_gpus            = 1
environment             = "QE_NK=1"
requirements            = regexp("H100|H200|A100", TARGET.GPUs_DeviceName) && !regexp("MIG", TARGET.GPUs_DeviceName)
+JobFlavour             = "tomorrow"
+IWOJob                 = "{name}_relax_s$(seg)"
queue
"""

FINAL_SUB = """universe                = vanilla
executable              = {common}/final_node.sh
arguments               = 72000
should_transfer_files   = YES
transfer_input_files    = {common}/driver.sh, {common}/qeio.py, {common}/dat2h5.py, {common}/pseudo, relax.in, final.tmpl, steps_final.sh
when_to_transfer_output = ON_EXIT
transfer_output_files   = final_results.tar.gz
output                  = logs/final.$(ClusterId).out
error                   = logs/final.$(ClusterId).err
log                     = logs/final.log
request_cpus            = 32
request_memory          = 100 GB
request_disk            = 60 GB
request_gpus            = 0
environment             = "QE_NK="
+JobFlavour             = "tomorrow"
+IWOJob                 = "{name}_final"
# A15 gate (as the slabs; A23 (i)): FINAL is submitted on hold; condor_release only after the smearing audit and the
# D-24 export are in place
hold                    = True
queue
"""

DAG = """JOB RELAX relax.sub
VARS RELAX seg="$(RETRY)"
RETRY RELAX 8 UNLESS-EXIT 2
JOB FINAL final.sub
RETRY FINAL 1
PARENT RELAX CHILD FINAL
"""


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def patch(text, old, new):
    if text.count(old) != 1:
        raise SystemExit(f'expected exactly one {old!r} in the generated input (make_dft.qe_input changed?)')
    return text.replace(old, new)


def make(name):
    res = ROOT / 'results' / name
    run = ROOT / 'runs' / name
    if run.exists():
        raise SystemExit(f'{run} exists: refusing to touch it')
    spec = json.loads((ROOT / 'specs' / f'spec_{name}.json').read_text())
    qc = json.loads((res / f'{name}_qc.json').read_text())
    if spec['mode'] != 'bulk' or qc.get('QC') != 'PASS':
        raise SystemExit(f'{name}: mode {spec["mode"]}, QC {qc.get("QC")}: not a QC-PASS bulk cell')
    cell, atoms = make_dft.read_qe_txt(res / f'{name}_qe.txt')
    comp = {s: sum(1 for t, _ in atoms if t == s) for s in {t for t, _ in atoms}}
    want = {k: spec[f'n_{k}'] for k in ('In', 'W', 'O') if spec.get(f'n_{k}')}
    if comp != want or len(atoms) != qc['n_atoms']:
        raise SystemExit(f'{name}: composition {comp} != spec {want} or n_atoms {len(atoms)} != QC {qc["n_atoms"]}')
    missing = [make_dft.PP[s] for s in comp if not (COMMON / 'pseudo' / make_dft.PP[s]).exists()]
    if missing:
        raise SystemExit(f'{name}: pseudopotentials missing in common/pseudo: {missing}')
    nelec = sum(make_dft.VAL[s] for s, _ in atoms)
    nbnd = int(math.ceil(1.3 * nelec / 2))
    relax = make_dft.qe_input('relax', 'rlx', cell, atoms, 60, K, False, smear=GAUSS)
    relax = patch(relax, "verbosity = 'low'", "verbosity = 'high'")
    relax = patch(relax, ELEC_SERIES, ELEC_PILOT)
    final = make_dft.qe_input('scf', 'slab', cell, atoms, 71, K, False, nbnd=nbnd, smear=GAUSS)
    final = patch(final, "verbosity = 'low'", "verbosity = 'high'")
    for txt in (relax, final):
        if 'tefield' in txt or 'dipfield' in txt or GAUSS not in txt:
            raise SystemExit('bulk input has a dipole correction or the wrong smearing')
    (run / 'logs').mkdir(parents=True)
    (run / 'relax.in').write_text(relax)
    (run / 'final.tmpl').write_text(final)
    for dst, src in COPY.items():
        shutil.copyfile(src, run / dst)
    (run / 'relax_node_bulk.sh').chmod(0o755)
    (run / 'relax.sub').write_text(RELAX_SUB.format(run=run, common=COMMON, name=name))
    (run / 'final.sub').write_text(FINAL_SUB.format(common=COMMON, name=name))
    (run / f'{name}.dag').write_text(DAG)
    prov = [f'A23 (i) PBE bulk reference {name}: built by common/make_bulkref.py (md5 {md5(__file__)})',
            f'structure: results/{name}/{name}_qe.txt (md5 {md5(res / f"{name}_qe.txt")}), QC {qc["QC"]}, '
            f'{len(atoms)} atoms {comp}, cell {cell[0][0]:.4f} {cell[1][1]:.4f} {cell[2][2]:.4f} A, '
            f'N_el {nelec} (PAW valence {dict((s, make_dft.VAL[s]) for s in comp)}), nbnd(final) {nbnd}',
            f'make_dft.py imported (not edited): md5 {md5(COMMON / "make_dft.py")}']
    prov += [f'{dst} <- {src} (md5 {md5(src)})' for dst, src in COPY.items()]
    prov += ['relax: fixed cell, 60/480 Ry, k 2x2x2, gaussian 0.005, pilot electrons, verbosity high, 1 GPU '
             'H100|H200|A100 (no MIG); DAG RETRY RELAX 8 UNLESS-EXIT 2',
             'final: 71/568 Ry, k 2x2x2, gaussian 0.005, verbosity high (D-24 target), CPU 32 / 100 GB, hold = True '
             '(A15 gate); export = slab machinery (common/final_node.sh, steps_final.sh)',
             'NOT SUBMITTED by the builder. Submit: cd runs/<name> && condor_submit_dag <name>.dag']
    (run / 'PROVENANCE').write_text('\n'.join(prov) + '\n')
    print(f'{name}: {len(atoms)} atoms {comp}, N_el {nelec}, nbnd {nbnd}, k {K} -> {run}')


if __name__ == '__main__':
    names = sys.argv[1:]
    if not names:
        raise SystemExit(__doc__)
    for n in names:                      # check all first, so a refusal never leaves a half-built set
        if (ROOT / 'runs' / n).exists():
            raise SystemExit(f'{ROOT / "runs" / n} exists: refusing (nothing created)')
    for n in names:
        make(n)
