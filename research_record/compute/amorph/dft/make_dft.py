#!/usr/bin/env python3
"""Create the DFT run directory and DAG for one ML-built amorphous structure (standard library only; runs on lxplus).

usage: python3 make_dft.py <name> [<name> ...]
reads  ~/iwo_amorph/results/<name>/<name>_qe.txt and specs/spec_<name>.json
writes ~/iwo_amorph/runs/<name>/: relax.in, final.tmpl, steps_relax.sh, steps_final.sh, relax.sub, final.sub,
       <name>.dag, logs/

Settings (fixed for the whole series):
  relax : PBE PAW (pslibrary 1.0.0), ecutwfc/ecutrho 60/480 Ry, smearing mv 0.01 Ry, BFGS, forc_conv_thr 1e-3 Ry/bohr,
          k 2x2x1 (slabs) / 2x2x2 (bulk), dipole correction along z for slabs; GPU (QE 7.3.1 container), <= 20 h segments
  final : 71/568 Ry (the protocol cutoff of the crystalline study), k from KSPACING (2x2x1 for all registered cells),
          Gaussian 0.005 Ry smearing pending the A15 smearing audit (register A15), FINAL submitted on hold (A15 gate),
          nbnd = 1.3 x occupied, then planar-averaged potential and projwfc (PDOS + per-state projections for IPR); CPU
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path.home() / 'iwo_amorph'
COMMON = ROOT / 'common'
VAL = {'In': 13, 'W': 14, 'Al': 3, 'O': 6, 'H': 1}           # valence electrons of the pslibrary PAW sets
MASS = {'In': 114.818, 'W': 183.84, 'Al': 26.982, 'O': 15.999, 'H': 1.008}
PP = {'In': 'In.pbe-dn-kjpaw_psl.1.0.0.UPF', 'W': 'W.pbe-spn-kjpaw_psl.1.0.0.UPF',
      'O': 'O.pbe-n-kjpaw_psl.1.0.0.UPF', 'H': 'H.pbe-kjpaw_psl.1.0.0.UPF', 'Al': 'Al.pbe-n-kjpaw_psl.1.0.0.UPF'}
# Hf (A18 HfO2 control): pslibrary 1.0.0 PAW, z_valence 12 (5s2 5p6 5d2 6s2; 4f14 frozen in the core)
VAL['Hf'], MASS['Hf'], PP['Hf'] = 12, 178.49, 'Hf.pbe-spn-kjpaw_psl.1.0.0.UPF'
SPECIES_ORDER = ['In', 'W', 'Al', 'Hf', 'O', 'H']   # ATOMIC_SPECIES order (Hf added by A18; others unchanged)
VAC_DFT = 18.0    # A of vacuum in every DFT slab cell
KSPACING = 0.25  # 1/A; n_k = ceil(2 pi / (a * KSPACING)) -> 2x2x1 for every registered cell (a >= 12.5 A)


def read_qe_txt(path):
    lines = Path(path).read_text().splitlines()
    i = lines.index('CELL_PARAMETERS angstrom')
    cell = [[float(x) for x in lines[i + k].split()] for k in (1, 2, 3)]
    j = lines.index('ATOMIC_POSITIONS angstrom')
    atoms = [(l.split()[0], [float(x) for x in l.split()[1:4]]) for l in lines[j + 1:] if l.strip()]
    return cell, atoms


SMEAR_RELAX = "occupations = 'smearing', smearing = 'mv', degauss = 0.01"
SMEAR_FINAL = "occupations = 'smearing', smearing = 'gaussian', degauss = 0.005"   # A15 (2026-10-11); audit may lower degauss


def qe_input(calc, prefix, cell, atoms, ecut, kpts, slab, nbnd=None, extra_control='', smear=SMEAR_RELAX):
    species = sorted({s for s, _ in atoms}, key=SPECIES_ORDER.index)
    sysl = [f"  ibrav = 0, nat = {len(atoms)}, ntyp = {len(species)}, ecutwfc = {ecut}, ecutrho = {ecut * 8}",
            '  ' + smear]
    if nbnd:
        sysl.append(f'  nbnd = {nbnd}')
    ctrl = [f"  calculation = '{calc}', prefix = '{prefix}', outdir = './tmp', pseudo_dir = './pseudo'",
            "  verbosity = 'low', tprnfor = .true., max_seconds = 1.0d8"]
    if calc == 'relax':
        ctrl.append('  nstep = 400, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3')
    if slab:
        # sawtooth discontinuity in the vacuum at 0.95-0.99 of c (slab sits in the middle of the cell)
        ctrl.append('  tefield = .true., dipfield = .true.')
        sysl.append('  edir = 3, emaxpos = 0.95, eopreg = 0.04, eamp = 0.0')
    if extra_control:
        ctrl.append(extra_control)
    out = ['&CONTROL', *ctrl, '/', '&SYSTEM', *sysl, '/',
           '&ELECTRONS', "  conv_thr = 1.0d-7, mixing_beta = 0.2, electron_maxstep = 200, mixing_mode = 'local-TF'", '/']
    if calc == 'relax':
        out += ['&IONS', "  ion_dynamics = 'bfgs'", '/']
    out.append('ATOMIC_SPECIES')
    out += [f'  {s} {MASS[s]} {PP[s]}' for s in species]
    out.append('CELL_PARAMETERS angstrom')
    out += ['  %.10f %.10f %.10f' % tuple(v) for v in cell]
    out += ['', 'K_POINTS automatic', '  %d %d %d 0 0 0' % kpts, '']
    # ATOMIC_POSITIONS last and followed by a blank line: qeio.py reads a card body up to the next blank line
    out.append('ATOMIC_POSITIONS angstrom')
    out += [f'  {s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}' for s, p in atoms]
    out += ['', '']
    return '\n'.join(out)


SUB = """universe                = vanilla
executable              = {common}/{node}_node.sh
arguments               = {args}
should_transfer_files   = YES
transfer_input_files    = {common}/driver.sh, {common}/qeio.py, {common}/dat2h5.py, {common}/pseudo, {inputs}
when_to_transfer_output = ON_EXIT
transfer_output_files   = {outputs}
output                  = logs/{tag}.$(ClusterId).out
error                   = logs/{tag}.$(ClusterId).err
log                     = logs/{node}.log
request_cpus            = {cpus}
request_memory          = {mem}
request_disk            = 60 GB
request_gpus            = {gpus}
environment             = "QE_NK={nk}"
{req}+JobFlavour             = "{flavour}"
+IWOJob                 = "{name}_{tag}"
queue
"""


def make(name):
    res = ROOT / 'results' / name
    spec = json.loads((ROOT / 'specs' / f'spec_{name}.json').read_text())
    qc = json.loads((res / f'{name}_qc.json').read_text())
    reasons = qc.get('QC_reasons') or []
    vac_only = qc.get('QC') == 'FAIL' and reasons and all(r.startswith('vacuum gap') for r in reasons)
    if qc.get('QC') != 'PASS' and not vac_only:
        print(f'{name}: QC {qc.get("QC")} {reasons} -> no DFT run created')
        return False
    cell, atoms = read_qe_txt(res / f'{name}_qe.txt')
    if spec['mode'] != 'bulk':
        # uniform vacuum for every slab (SLAB_PROTOCOL.md 6): c = span + VAC_DFT, slab centred (sawtooth sits at 0.95c)
        z = [p[2] for _, p in atoms]
        c_new = max(z) - min(z) + VAC_DFT
        shift = 0.5 * c_new - 0.5 * (max(z) + min(z))
        cell[2] = [0.0, 0.0, c_new]
        atoms = [(s, [p[0], p[1], p[2] + shift]) for s, p in atoms]
    slab = spec['mode'] in ('slab', 'interface')
    missing = [PP[s] for s in {s for s, _ in atoms} if not (COMMON / 'pseudo' / PP[s]).exists()]
    if missing:
        print(f'{name}: pseudopotential(s) {missing} not in {COMMON / "pseudo"} -> DFT waits')
        return False
    a_inplane = min(math.hypot(*cell[0]), math.hypot(*cell[1]))
    nk = max(1, math.ceil(2 * math.pi / (a_inplane * KSPACING)))
    k_relax = k_final = (nk, nk, 1) if slab else (2, 2, 2)
    nelec = sum(VAL[s] for s, _ in atoms)
    nbnd = int(math.ceil(1.3 * nelec / 2))
    # CPU final (scf + pp.x + projwfc.x, one QE version): cells > 200 atoms get the 3-day queue
    fin_flav, fin_s = ('testmatch', 250000) if len(atoms) > 200 else ('tomorrow', 72000)
    # GPU memory: one 94 GB H100 holds <= ~200 atoms here (270-atom slabs ran out, 2026-10-10). Larger cells get 2 or 4
    # GPUs with QE_NK=1 (plane waves split over the GPUs -> per-GPU memory / n); smaller cells keep 1 GPU, -nk 1.
    ngpu = 1 if len(atoms) <= 200 else (2 if len(atoms) <= 350 else 4)
    run = ROOT / 'runs' / name
    (run / 'logs').mkdir(parents=True, exist_ok=True)
    (run / 'relax.in').write_text(qe_input('relax', 'rlx', cell, atoms, 60, k_relax, slab))
    (run / 'final.tmpl').write_text(qe_input('scf', 'slab', cell, atoms, 71, k_final, slab, nbnd=nbnd, smear=SMEAR_FINAL))
    (run / 'steps_relax.sh').write_text((COMMON / 'steps_relax.sh').read_text())
    (run / 'steps_final.sh').write_text((COMMON / 'steps_final.sh').read_text())
    (run / 'relax.sub').write_text(SUB.format(
        common=COMMON, node='relax', args='$(seg) 72000', inputs='relax.in, steps_relax.sh',
        outputs='relax_s$(seg)_results.tar.gz, relax.in, RELAX_STATUS', tag='relax_s$(seg)', cpus=8 * ngpu,
        mem='64 GB' if ngpu <= 2 else '128 GB', flavour='tomorrow', gpus=ngpu, nk=1 if ngpu > 1 else '', req='requirements            = regexp("H100|H200", TARGET.GPUs_DeviceName)\n', name=name))
    (run / 'final.sub').write_text(SUB.format(
        common=COMMON, node='final', args=str(fin_s), flavour=fin_flav, inputs='relax.in, final.tmpl, steps_final.sh',
        outputs='final_results.tar.gz', tag='final', cpus=32, mem='100 GB', gpus=0, nk='', req='', name=name).replace(
        '\nqueue\n', '\n# A15 gate: FINAL is submitted on hold until the smearing audit fixes degauss; then condor_release\n'
        'hold                    = True\nqueue\n'))
    (run / f'{name}.dag').write_text(
        'JOB RELAX relax.sub\nVARS RELAX seg="$(RETRY)"\nRETRY RELAX 8\n'
        'JOB FINAL final.sub\nRETRY FINAL 1\nPARENT RELAX CHILD FINAL\n')
    print(f'{name}: {len(atoms)} atoms, {nelec} electrons, nbnd {nbnd}, in-plane {a_inplane:.2f} A, '
          f'k relax {k_relax} final {k_final}, relax GPUs {ngpu} -> {run}')
    return True


if __name__ == '__main__':
    ok = [make(n) for n in sys.argv[1:]]
    sys.exit(0 if all(ok) else 1)
