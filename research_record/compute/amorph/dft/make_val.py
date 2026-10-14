#!/usr/bin/env python3
"""DFT force check of the ML potential (Codex review PLAN-001): one SCF with forces per MACE snapshot.

usage: python3 make_val.py <name>:<tag>[,<tag>...] ...      e.g. aIWO_bulk_s1:melt_3000K,quenched_300K,final
reads  ~/iwo_amorph/results/<name>/<name>_snapshots.xyz (extended XYZ written by mace_amorph.py, with mace_forces)
writes ~/iwo_amorph/val/<name>_<tag>/scf.in, mace_ref.json and ~/iwo_amorph/val/val_jobs.txt + val.sub
Settings as the production relaxation (PBE PAW, 60/480 Ry, mv 0.01 Ry, k 2x2x2 bulk / 2x2x1 slab, dipole
correction for slabs) so that the comparison tests the potential, not different DFT settings.

Pass limits, fixed before any result is seen (recorded in the private repo, claude/plans/ML_VALIDATION.md):
  force RMSE <= 0.15 eV/A and force MAE <= 0.10 eV/A on relaxed/quenched frames; melt frames reported only.

Interface cells, separate job list (register A21 Hf force check; A18 verification fixes, SLAB_PROTOCOL.md 9):
  python3 make_val.py --list hfo2 aIWO_2p0_HfO2_s1:quenched_300K,slab_annealed,final
  * the frames after the cleave (VAC_TAGS: slab_annealed, final) have vacuum and get the relax settings of the cell
    (k 2x2x1, dipole correction); the periodic frames before the cleave (melt_3000K, quenched_300K) get no dipole
    correction and the relax k density (KSPACING) along all three axes (2x2x1 for the 12.91 x 12.91 x 30 A box)
  * the jobs go to val/val_jobs_<list>.txt and val/val_<list>.sub; val_jobs.txt and val.sub are not touched
  * resources: those of the relax of the same cell (make_dft.py rule: > 350 atoms -> 4 H100/H200 GPUs, 128 GB,
    QE_NK=1), because a 400-atom CPU SCF does not fit in the 100 GB of val.sub; disk_io = 'nowf' (no wavefunction
    save, which would be ~60 GB; the forces do not depend on it)
Without --list the behaviour and every output are unchanged (slab and bulk cells as before).
"""
import json
import math
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_dft import qe_input, ROOT, COMMON   # noqa: E402

VAL = ROOT / 'val'
VAC_TAGS = ('slab_annealed', 'final')   # snapshots taken after the cleave (vacuum along z)
KSPACING = 0.25   # 1/A, as make_dft.py


def read_extxyz(path):
    frames, lines, k = [], Path(path).read_text().splitlines(), 0
    while k < len(lines):
        n = int(lines[k])
        head = lines[k + 1]
        lat = [float(x) for x in re.search(r'Lattice="([^"]+)"', head).group(1).split()]
        props = re.search(r'Properties=(\S+)', head).group(1).split(':')
        cols, c = {}, 0
        for i in range(0, len(props), 3):
            name, typ, width = props[i], props[i + 1], int(props[i + 2])
            cols[name] = (c, width)
            c += width
        info = dict(kv.split('=', 1) for kv in shlex.split(head) if '=' in kv)
        atoms, forces = [], []
        for row in lines[k + 2:k + 2 + n]:
            f = row.split()
            s0, _ = cols['species']
            p0, _ = cols['pos']
            atoms.append((f[s0], [float(x) for x in f[p0:p0 + 3]]))
            if 'mace_forces' in cols:
                m0, _ = cols['mace_forces']
                forces.append([float(x) for x in f[m0:m0 + 3]])
        frames.append({'cell': [lat[0:3], lat[3:6], lat[6:9]], 'atoms': atoms, 'forces': forces,
                       'tag': info.get('tag'), 'mace_energy_eV': float(info.get('mace_energy_eV', 'nan'))})
        k += n + 2
    return frames


def interface_settings(fr):
    """k-points and dipole flag of one interface snapshot (separate --list jobs only)."""
    cell = fr['cell']
    if fr['tag'] in VAC_TAGS:
        z = [p[2] for _, p in fr['atoms']]
        if cell[2][2] - (max(z) - min(z)) < 10.0:
            raise SystemExit(f"{fr['tag']}: expected a vacuum gap along z, found {cell[2][2] - (max(z) - min(z)):.1f} A")
        nk = max(1, math.ceil(2 * math.pi / (min(math.hypot(*cell[0]), math.hypot(*cell[1])) * KSPACING)))
        return (nk, nk, 1), True
    return tuple(max(1, math.ceil(2 * math.pi / (math.hypot(*v) * KSPACING))) for v in cell), False


def main():
    args = sys.argv[1:]
    lst = None
    if args and args[0] == '--list':   # separate job list for interface cells (A18 fixes / A21)
        lst = args[1]
        if not re.fullmatch(r'[A-Za-z0-9]+', lst):
            raise SystemExit('--list needs an alphanumeric name')
        args = args[2:]
    jobs, nat_max = [], 0
    for arg in args:
        name, tags = arg.split(':')
        spec = json.loads((ROOT / 'specs' / f'spec_{name}.json').read_text())
        if lst is None and spec['mode'] == 'interface':
            raise SystemExit(f'{name}: interface cells go to a separate list (--list <name>), see the docstring')
        slab = spec['mode'] == 'slab'
        for fr in read_extxyz(ROOT / 'results' / name / f'{name}_snapshots.xyz'):
            if fr['tag'] not in tags.split(','):
                continue
            kpts, dip = interface_settings(fr) if spec['mode'] == 'interface' else ((2, 2, 1) if slab else (2, 2, 2), slab)
            d = VAL / f"{name}_{fr['tag']}"
            (d / 'logs').mkdir(parents=True, exist_ok=True)
            # --list jobs: forces only, no wavefunction save (~60 GB at 400 atoms); disk_io does not change the forces
            (d / 'scf.in').write_text(qe_input('scf', 'val', fr['cell'], fr['atoms'], 60, kpts, dip,
                                               extra_control="  disk_io = 'nowf'" if lst else ''))
            (d / 'mace_ref.json').write_text(json.dumps({'tag': fr['tag'], 'energy_eV': fr['mace_energy_eV'],
                                                         'forces_eV_A': fr['forces']}))
            (d / 'steps_val.sh').write_text((COMMON / 'steps_val.sh').read_text())
            jobs.append(d.name)
            nat_max = max(nat_max, len(fr['atoms']))
    if lst is not None:
        if not jobs:
            raise SystemExit('no matching snapshots: nothing written')
        ngpu = 1 if nat_max <= 200 else (2 if nat_max <= 350 else 4)   # make_dft.py relax rule
        (VAL / f'val_jobs_{lst}.txt').write_text(''.join(j + '\n' for j in jobs))
        (VAL / f'val_{lst}.sub').write_text(f"""universe                = vanilla
initialdir              = {VAL}/$(job)
executable              = {COMMON}/val_node.sh
arguments               = 72000
should_transfer_files   = YES
transfer_input_files    = {COMMON}/driver.sh, {COMMON}/qeio.py, {COMMON}/dat2h5.py, {COMMON}/pseudo, scf.in, steps_val.sh
when_to_transfer_output = ON_EXIT
transfer_output_files   = val_results.tar.gz
output                  = logs/val.$(ClusterId).out
error                   = logs/val.$(ClusterId).err
log                     = {VAL}/val_{lst}.log
request_cpus            = {8 * ngpu}
request_memory          = {'64 GB' if ngpu <= 2 else '128 GB'}
request_disk            = 60 GB
request_gpus            = {ngpu}
environment             = "QE_NK={1 if ngpu > 1 else ''}"
requirements            = regexp("H100|H200", TARGET.GPUs_DeviceName)
+JobFlavour             = "tomorrow"
+IWOJob                 = "val_$(job)"
queue job from {VAL}/val_jobs_{lst}.txt
""")
        print(len(jobs), f'validation jobs in list {lst} ({nat_max} atoms max, {ngpu} GPU):', ', '.join(jobs))
        return
    (VAL / 'val_jobs.txt').write_text(''.join(j + '\n' for j in jobs))
    (VAL / 'val.sub').write_text(f"""universe                = vanilla
initialdir              = {VAL}/$(job)
executable              = {COMMON}/val_node.sh
arguments               = 72000
should_transfer_files   = YES
transfer_input_files    = {COMMON}/driver.sh, {COMMON}/qeio.py, {COMMON}/dat2h5.py, {COMMON}/pseudo, scf.in, steps_val.sh
when_to_transfer_output = ON_EXIT
transfer_output_files   = val_results.tar.gz
output                  = logs/val.$(ClusterId).out
error                   = logs/val.$(ClusterId).err
log                     = {VAL}/val.log
request_cpus            = 32
request_memory          = 100 GB
request_disk            = 40 GB
+JobFlavour             = "tomorrow"
+IWOJob                 = "val_$(job)"
queue job from {VAL}/val_jobs.txt
""")
    print(len(jobs), 'validation jobs:', ', '.join(jobs))


if __name__ == '__main__':
    main()
