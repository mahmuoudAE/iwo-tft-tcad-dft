#!/usr/bin/env python3
"""H-L (register amendments A17 and A19, decision D-19): crystalline oxygen-vacancy cells of In2O3 and IWO.

Builds the six H-L cells (the five of A17 plus In31WO47_near72 of A19), checks them, and stages the QE inputs and
HTCondor DAG files that go to CERN ~/iwo_amorph/vac/<name>/. Rerunnable; it writes only below its own folder:

    structures/<name>.json, structures/<name>.xyz   the six starting geometries
    stage/<name>/                                    relax.in, final.tmpl, *.sub, <name>.dag, node and step scripts
    build_facts.json                                 every number quoted in BUILD_REPORT.md

Usage (WSL Ubuntu-22.04, conda env qe: numpy, spglib):  python make_vac.py

Frozen by H-L (codex/work_chat/HYPOTHESIS_REGISTER.md, section "### H-L"): 80-atom conventional bixbyite cell
fixed at a = 10.3061 A; PBE, pslibrary 1.0.0 PAW, 71/568 Ry; k 3x3x3 for the relaxation; Gaussian smearing
0.005 Ry; spin-unpolarised; neutral; forces 1e-3 Ry/bohr, energy 1e-4 Ry; W on 24d; single-point SCF at
k 4x4x4 on every relaxed geometry. Site rules: near = the O with the shortest W-O bond in the relaxed
In31WO48; far = the O with the largest minimum-image distance to W.

A19 (before submission): the stage-4 In31WO48 has two near candidates 0.0105 A apart, O index0 30 (QE #31, W-O
1.8919 A; cell In31WO47_near) and O index0 72 (QE #73, W-O 1.9024 A; cell In31WO47_near72). Both are computed;
select_near.py picks the registered one on the H-L-relaxed In31WO48. Settings fixed for all six cells: conv_thr 1e-8,
plain mixing beta 0.3, electron_maxstep 100, nstep 300, QE 7.3.1 GPU. RELAX is CONVERGED only with 'bfgs converged'
(pilot steps_relax.sh); the k4 FINAL counts only with a converged '!' energy and 'convergence has been achieved'.
"""
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import spglib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                                   # IWO_Local_Codex_Handoff (1)
QEW = ROOT / 'IWO_PHYSICS_CONSTRAINED_MODEL_V1' / 'qe_workflow'
HOST_JSON = QEW / 'structures_v2' / 'relaxed_pbe' / 'bulk_conv.json'
W_JSON = QEW / 'structures_v2' / 'relaxed_pbe' / 'iwo_W24d.json'
W_RELAX_IN = QEW / 'cern_htcondor' / 'results' / 'iwo_W24d' / 'relax.in'
W_RELAX_OUT = QEW / 'cern_htcondor' / 'results' / 'iwo_W24d' / 'relax.out'
PILOT = HERE / 'pilot_copy'        # byte copies of ~/iwo_amorph/runs/aIO_0p8_s1/{relax_node_pilot.sh,steps_relax.sh,geomsel.py}
OUT_STRUCT = HERE / 'structures'
STAGE = HERE / 'stage'
AFS = '/afs/cern.ch/user/m/melrashe/iwo_amorph'

A_HL = 10.3061          # H-L: cell fixed at the stage-2 PBE host value (bulk_In2O3_protocol: a = 10.3061 A)
ZVAL = {'In': 13, 'W': 14, 'O': 6}   # z_valence of the pslibrary 1.0.0 PAW sets (checked in the UPF headers)
MASS = {'In': 114.818, 'O': 15.999, 'W': 183.84}
UPF = {'In': 'In.pbe-dn-kjpaw_psl.1.0.0.UPF', 'O': 'O.pbe-n-kjpaw_psl.1.0.0.UPF', 'W': 'W.pbe-spn-kjpaw_psl.1.0.0.UPF'}
NUM = {'In': 49, 'O': 8, 'W': 74}
TIE = 1e-3              # A: distances that differ by less than this count as equal (symmetry-equivalent sites)
SYMPREC = 1e-3
NAMES = ['In32O48', 'In31WO48', 'In32O47', 'In31WO47_near', 'In31WO47_near72', 'In31WO47_far']
NEAR72 = 72            # A19: second near candidate, O index0 72 (QE #73), W-O 1.9024 A in the stage-4 In31WO48


# ---------------------------------------------------------------- geometry helpers
def load_json(path):
    d = json.loads(Path(path).read_text())
    cell = np.array(d['cell_A'], float)
    return cell, list(d['symbols']), np.array(d['positions_A'], float) @ np.linalg.inv(cell)


def read_cell_in(path):
    lines = Path(path).read_text().splitlines()
    i = next(n for n, l in enumerate(lines) if l.strip().startswith('CELL_PARAMETERS'))
    assert 'angstrom' in lines[i], lines[i]
    return np.array([[float(x) for x in lines[i + k].split()[:3]] for k in (1, 2, 3)])


def read_calc(path):
    for l in Path(path).read_text().splitlines():
        if 'calculation' in l:
            return l.split('calculation')[1].split('=')[1].split(',')[0].strip().strip("'\"")


def read_final_coords(path):
    """Final geometry of a QE relax: symbols and crystal coordinates of the 'Begin final coordinates' block."""
    text = Path(path).read_text(errors='replace')
    assert 'bfgs converged' in text and 'End final coordinates' in text, 'stage-4 relax not converged'
    lines = text.splitlines()
    i = next(n for n, l in enumerate(lines) if 'Begin final coordinates' in l)
    j = next(n for n in range(i, len(lines)) if lines[n].strip().startswith('ATOMIC_POSITIONS'))
    assert 'crystal' in lines[j], lines[j]
    sym, frac = [], []
    for l in lines[j + 1:]:
        s = l.split()
        if not s or s[0] == 'End':
            break
        sym.append(s[0])
        frac.append([float(x) for x in s[1:4]])
    nbfgs = [l for l in lines if 'bfgs converged in' in l][-1].strip()
    efinal = [l for l in lines if 'Final energy' in l][-1].split('=')[1].split()[0]
    return sym, np.array(frac), nbfgs, float(efinal)


def mic_vec(fi, fj, cell):
    d = np.asarray(fj) - np.asarray(fi)
    d -= np.round(d)
    return d @ cell


def dist_matrix(cell, frac):
    d = frac[None, :, :] - frac[:, None, :]
    d -= np.round(d)
    return np.linalg.norm(d @ cell, axis=-1)


def sym_info(cell, sym, frac):
    ds = spglib.get_symmetry_dataset((cell, frac, [NUM[s] for s in sym]), symprec=SYMPREC)
    out = {'spacegroup': f'{ds.international} ({ds.number})', 'n_ops': int(len(ds.rotations)),
           'equivalent_atoms': [int(x) for x in ds.equivalent_atoms]}
    try:
        mapping, grid = spglib.get_ir_reciprocal_mesh([3, 3, 3], (cell, frac, [NUM[s] for s in sym]),
                                                      is_shift=[0, 0, 0], symprec=SYMPREC)
        out['irr_k_333_spglib'] = int(len(np.unique(mapping)))
        mapping, grid = spglib.get_ir_reciprocal_mesh([4, 4, 4], (cell, frac, [NUM[s] for s in sym]),
                                                      is_shift=[0, 0, 0], symprec=SYMPREC)
        out['irr_k_444_spglib'] = int(len(np.unique(mapping)))
    except Exception as e:                                  # informative only
        out['irr_k_error'] = str(e)
    return out


def primitive_ops(cell, sym, frac):
    lat, pos, nums = spglib.find_primitive((cell, frac, [NUM[s] for s in sym]), symprec=SYMPREC)
    ds = spglib.get_symmetry_dataset((lat, pos, nums), symprec=SYMPREC)
    return int(len(nums)), int(len(ds.rotations)), f'{ds.international} ({ds.number})'


def checks(name, cell, sym, frac):
    """Composition, electrons, minimum distances, cation-O first shells, symmetry. Fails loudly."""
    D = dist_matrix(cell, frac)
    n = len(sym)
    iu = np.triu_indices(n, 1)
    comp = {s: sym.count(s) for s in ('In', 'W', 'O') if s in sym}
    pairs = {}
    for a, b in [('In', 'O'), ('W', 'O'), ('O', 'O'), ('In', 'In'), ('In', 'W')]:
        ia = [k for k in range(n) if sym[k] == a]
        ib = [k for k in range(n) if sym[k] == b]
        if not ia or not ib:
            continue
        sub = D[np.ix_(ia, ib)]
        if a == b:
            sub = sub[np.triu_indices(len(ia), 1)]
        pairs[f'{a}-{b}'] = round(float(sub.min()), 4)
    shells = {}
    for c in ('In', 'W'):
        ic = [k for k in range(n) if sym[k] == c]
        io = [k for k in range(n) if sym[k] == 'O']
        if not ic:
            continue
        sub = D[np.ix_(ic, io)]
        cn = [int((row < 2.6).sum()) for row in sub]          # 2.6 A: first-shell cutoff (2nd shell > 3.5 A)
        first6 = np.sort(sub, axis=1)[:, :6]
        shells[c] = {'bond_min': round(float(first6.min()), 4), 'bond_max': round(float(first6.max()), 4),
                     'CN_counts': {str(k): cn.count(k) for k in sorted(set(cn))}}
    info = {'name': name, 'n_atoms': n, 'composition': comp,
            'n_electrons': int(sum(ZVAL[s] for s in sym)),
            'min_distance_A': round(float(D[iu].min()), 4), 'min_pair_A': pairs, 'cation_O_shell': shells}
    info.update({k: v for k, v in sym_info(cell, sym, frac).items() if k != 'equivalent_atoms'})
    assert info['min_distance_A'] > 1.7, f'{name}: atoms too close'
    return info, D


# ---------------------------------------------------------------- writers
def write_struct(name, cell, sym, frac, meta):
    OUT_STRUCT.mkdir(exist_ok=True)
    pos = frac @ cell
    d = {'name': name, 'cell_A': cell.tolist(), 'symbols': sym, 'positions_A': pos.round(8).tolist(),
         'scaled_positions': frac.round(10).tolist(), 'meta': meta}
    (OUT_STRUCT / f'{name}.json').write_text(json.dumps(d, indent=1) + '\n', newline='\n')
    lat = ' '.join('%.10f' % x for x in cell.ravel())
    xyz = [str(len(sym)), f'Lattice="{lat}" Properties=species:S:1:pos:R:3 pbc="T T T" name={name}']
    xyz += ['%-2s %14.8f %14.8f %14.8f' % (s, *p) for s, p in zip(sym, pos)]
    (OUT_STRUCT / f'{name}.xyz').write_text('\n'.join(xyz) + '\n', newline='\n')
    return xyz


def species_block(sym):
    sp = [s for s in ('In', 'O', 'W') if s in sym]
    return sp, ['ATOMIC_SPECIES'] + [f'  {s} {MASS[s]} {UPF[s]}' for s in sp]


def qe_input(calc, cell, sym, frac, kmesh):
    sp, spec = species_block(sym)
    if calc == 'relax':
        control = ["  calculation = 'relax', prefix = 'rel', outdir = './tmp', pseudo_dir = './pseudo'",
                   "  verbosity = 'high', tprnfor = .true., tstress = .true., max_seconds = 1.0d8",
                   "  nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3"]
    else:
        control = ["  calculation = 'scf', prefix = 'scf', outdir = './tmp', pseudo_dir = './pseudo'",
                   "  verbosity = 'high', tprnfor = .true., tstress = .true., max_seconds = 1.0d8"]
    L = ['&CONTROL'] + control + ['/',
         '&SYSTEM',
         f'  ibrav = 0, nat = {len(sym)}, ntyp = {len(sp)}, ecutwfc = 71, ecutrho = 568',
         "  occupations = 'smearing', smearing = 'gaussian', degauss = 0.005",
         '/',
         '&ELECTRONS',
         '  conv_thr = 1.0d-8, mixing_beta = 0.3, electron_maxstep = 100',
         '/']
    if calc == 'relax':
        L += ['&IONS', "  ion_dynamics = 'bfgs'", '/']
    L += spec
    L += ['CELL_PARAMETERS angstrom'] + ['  %.10f %.10f %.10f' % tuple(v) for v in cell]
    L += ['', 'K_POINTS automatic', '  %d %d %d 0 0 0' % kmesh, '']
    L += ['ATOMIC_POSITIONS crystal'] + ['  %-2s %.10f %.10f %.10f' % (s, *f) for s, f in zip(sym, frac)]
    return '\n'.join(L) + '\n'


def relax_sub(name):
    return f"""universe                = vanilla
executable              = {AFS}/vac/{name}/relax_node_vac.sh
arguments               = $(seg) 72000
should_transfer_files   = YES
transfer_input_files    = {AFS}/common/driver.sh, {AFS}/common/qeio.py, {AFS}/common/dat2h5.py, {AFS}/common/pseudo, relax.in, steps_relax.sh, geomsel.py
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
requirements            = regexp("H100|H200", TARGET.GPUs_DeviceName)
+JobFlavour             = "tomorrow"
+IWOJob                 = "vac_{name}_relax_s$(seg)"
queue
"""


def final_sub(name):
    # H-L k-point check node. No 'hold = True': the A15 hold gate belongs to the slab smearing audit only.
    return f"""universe                = vanilla
executable              = {AFS}/vac/{name}/final_node_vac.sh
arguments               = 72000
should_transfer_files   = YES
transfer_input_files    = {AFS}/common/driver.sh, {AFS}/common/qeio.py, {AFS}/common/dat2h5.py, {AFS}/common/pseudo, relax.in, relax.out, final.tmpl, steps_final.sh
when_to_transfer_output = ON_EXIT
transfer_output_files   = final_results.tar.gz, scf.in, scf.out, FINAL_STATUS
output                  = logs/final.$(ClusterId).out
error                   = logs/final.$(ClusterId).err
log                     = logs/final.log
request_cpus            = 8
request_memory          = 64 GB
request_disk            = 60 GB
request_gpus            = 1
environment             = "QE_NK=1"
requirements            = regexp("H100|H200", TARGET.GPUs_DeviceName)
+JobFlavour             = "tomorrow"
+IWOJob                 = "vac_{name}_final"
queue
"""


# FINAL: exit 2 (SCF not converged, or relax.out without 'bfgs converged'; deterministic) is never replayed;
# exit 1 (no energy, e.g. lost node) once (verification finding and A19, 2026-10-11).
DAG = """JOB RELAX relax.sub
VARS RELAX seg="$(RETRY)"
RETRY RELAX 8 UNLESS-EXIT 2
JOB FINAL final.sub
RETRY FINAL 1 UNLESS-EXIT 2
PARENT RELAX CHILD FINAL
"""

STEPS_FINAL = """steps() {
  # H-L k-point check (A17): one SCF at k 4x4x4 on the relaxed geometry of the last RELAX segment; no pp.x / projwfc.x.
  # relax.out is the converged segment's output (FINAL runs only after RELAX exit 0 = CONVERGED).
  python qeio.py converged relax.out || { log "relax.out has no final coordinates: FINAL SCF not run"; return 0; }
  python qeio.py newgeom final.tmpl relax.out > scf.in
  run_pw scf 1 || return 0
}
"""

FINAL_NODE = """#!/bin/bash
# H-L vacancy DAG node FINAL: single-point SCF at k 4x4x4 on the relaxed geometry (GPU, same container as RELAX).
# Based on common/final_node.sh. Differences: no pp.x / projwfc.x; scf.in, scf.out and FINAL_STATUS always exist
# (they are transferred back, a missing file would hold the job). Exit codes (DAG: RETRY FINAL 1 UNLESS-EXIT 2):
#   0 = DONE: 'JOB DONE', a converged total energy (a line starting with '!'), 'convergence has been achieved'
#       and no 'convergence NOT achieved' (A19)
#   2 = not replayed (deterministic, the same input would fail again):
#       SCF_NOT_CONVERGED   'convergence NOT achieved' in scf.out
#       RELAX_NOT_CONVERGED relax.out without 'bfgs converged' (A19); the k4 SCF is not run
#   1 = FAILED: anything else (scf.out empty or missing, no 'JOB DONE', or no '!' energy, e.g. a max_seconds stop
#       inside the SCF, which QE ends with 'JOB DONE' but without 'convergence NOT achieved'); replayed once
LIMIT=${1:-72000}
cd "${_CONDOR_SCRATCH_DIR:-$PWD}" || exit 1
if ! grep -q 'bfgs converged' relax.out 2>/dev/null; then
  touch final_results.tar.gz scf.in scf.out
  echo RELAX_NOT_CONVERGED > FINAL_STATUS; echo "relax.out has no 'bfgs converged': FINAL SCF not run (exit 2, not replayed)"; exit 2
fi
cp steps_final.sh steps.sh
bash driver.sh final "$LIMIT"
[ -f final_results.tar.gz ] || touch final_results.tar.gz
[ -f scf.in ] || touch scf.in
[ -f scf.out ] || touch scf.out
if grep -q 'convergence NOT achieved' scf.out; then
  echo SCF_NOT_CONVERGED > FINAL_STATUS; echo "final SCF not converged (exit 2, not replayed)"; exit 2
fi
if grep -q 'JOB DONE' scf.out && grep -q '^!' scf.out && grep -q 'convergence has been achieved' scf.out; then
  echo DONE > FINAL_STATUS; echo "final SCF done: $(grep '^!' scf.out | tail -1)"; exit 0
fi
echo FAILED > FINAL_STATUS; echo "final SCF failed: no converged energy (exit 1, replayed once)"; exit 1
"""


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- main
def main():
    facts = {'sources': {}, 'cells': {}, 'selection': {}}

    # host: bulk_conv.json (stage-2 PBE vc-relax, a = 10.3060902 A)
    hcell, hsym, hfrac = load_json(HOST_JSON)
    a = hcell[0, 0]
    assert np.allclose(hcell, np.diag([a, a, a]), atol=1e-8), 'host cell not cubic'
    assert abs(a - A_HL) < 5e-5, f'host a = {a} differs from H-L 10.3061'
    hds = spglib.get_symmetry_dataset((hcell, hfrac, [NUM[s] for s in hsym]), symprec=SYMPREC)
    o_orbits = sorted({int(hds.equivalent_atoms[k]) for k in range(len(hsym)) if hsym[k] == 'O'})
    in_orbits = sorted({int(hds.equivalent_atoms[k]) for k in range(len(hsym)) if hsym[k] == 'In'})
    nprim, nops_prim, sg_prim = primitive_ops(hcell, hsym, hfrac)
    assert hds.number == 206 and len(o_orbits) == 1 and len(in_orbits) == 2 and nops_prim == 24
    facts['host'] = {'a_A': float(a), 'spacegroup_conv': f'{hds.international} ({hds.number})',
                     'n_ops_conv_cell': int(len(hds.rotations)), 'primitive_atoms': nprim,
                     'n_ops_primitive': nops_prim, 'primitive_spacegroup': sg_prim,
                     'O_orbits': len(o_orbits), 'In_orbits': len(in_orbits)}
    facts['sources']['host'] = {'file': str(HOST_JSON.relative_to(ROOT)), 'sha256': sha(HOST_JSON)}

    # W cell: relaxed stage-4 iwo_W24d geometry (final coordinates of results/iwo_W24d/relax.out)
    wcell = read_cell_in(W_RELAX_IN)
    assert read_calc(W_RELAX_IN) == 'relax', 'stage-4 run was not a fixed-cell relax'
    assert np.allclose(wcell, hcell, atol=1e-8), 'stage-4 W24d cell differs from the host cell'
    wsym, wfrac, nbfgs, ew = read_final_coords(W_RELAX_OUT)
    jcell, jsym, jfrac = load_json(W_JSON)
    assert jsym == wsym and np.allclose(jcell, wcell, atol=1e-8), 'iwo_W24d.json and relax.out differ in order/cell'
    disp = np.linalg.norm(np.array([mic_vec(f0, f1, wcell) for f0, f1 in zip(jfrac, wfrac)]), axis=1)
    iW = wsym.index('W')
    facts['sources']['W'] = {'geometry': 'RELAXED stage-4 iwo_W24d (relax.out, Begin final coordinates)',
                             'file': str(W_RELAX_OUT.relative_to(ROOT)), 'sha256': sha(W_RELAX_OUT),
                             'bfgs': nbfgs, 'E_final_Ry_stage4': ew,
                             'stage4_settings': "mv smearing 0.01 Ry, conv_thr 1e-9, k 3x3x3, QE 7.5 CPU",
                             'cell_check': 'stage-4 relax.in CELL_PARAMETERS == host cell (|diff| < 1e-8 A); '
                                           'fixed-cell relax, so no rescaling was needed',
                             'max_displacement_vs_unrelaxed_json_A': round(float(disp.max()), 4),
                             'W_displacement_A': round(float(disp[iW]), 4), 'W_index0': iW, 'W_qe1': iW + 1,
                             'note_iwo_W24d_json': ('structures_v2/relaxed_pbe/iwo_W24d.json is the UNRELAXED W '
                                                    'substitution (only the host lattice is PBE-relaxed); the relaxed '
                                                    'In31WO48 geometry is results/iwo_W24d/relax.out'),
                             'max_abs_dfrac_vs_unrelaxed_json': round(float(np.max(np.abs(
                                 (jfrac - wfrac) - np.round(jfrac - wfrac)))), 5)}

    # site selection (H-L definitions) on the relaxed In31WO48
    iO = [k for k in range(len(wsym)) if wsym[k] == 'O']
    dWO = {k: float(np.linalg.norm(mic_vec(wfrac[iW], wfrac[k], wcell))) for k in iO}
    order = sorted(iO, key=lambda k: dWO[k])
    dmin, dmax = dWO[order[0]], dWO[order[-1]]
    near_ties = [k for k in iO if dWO[k] - dmin < TIE]
    far_ties = [k for k in iO if dmax - dWO[k] < TIE]
    near, far = min(near_ties), min(far_ties)
    wds = spglib.get_symmetry_dataset((wcell, wfrac, [NUM[s] for s in wsym]), symprec=SYMPREC)
    eq = wds.equivalent_atoms
    facts['selection']['index_convention'] = ('index0 = 0-based position in the 80-atom list (Python); '
                                              'qe1 = index0 + 1 = the atom number QE prints in its output')
    facts['selection']['W_cell_symmetry'] = f'{wds.international} ({wds.number}), {len(wds.rotations)} ops'
    facts['selection']['W_O_sorted_columns'] = ['index0', 'qe1', 'd_WO_A']
    facts['selection']['W_O_sorted_A'] = [[k, k + 1, round(dWO[k], 4)] for k in order]
    next_near = min(dWO[k] for k in iO if k not in near_ties)
    next_far = max(dWO[k] for k in iO if k not in far_ties)
    facts['selection']['near'] = {'index0': near, 'qe1': near + 1, 'd_WO_A': round(dmin, 4),
                                  'ties_index0': near_ties, 'ties_qe1': [k + 1 for k in near_ties],
                                  'ties_symmetry_equivalent': len({int(eq[k]) for k in near_ties}) == 1,
                                  'next_distinct_A': round(next_near, 4),
                                  'next_distinct_index0': [k for k in iO if abs(dWO[k] - next_near) < TIE],
                                  'next_distinct_qe1': [k + 1 for k in iO if abs(dWO[k] - next_near) < TIE],
                                  'margin_A': round(next_near - dmin, 4),
                                  'frac': wfrac[near].round(6).tolist()}
    facts['selection']['far'] = {'index0': far, 'qe1': far + 1, 'd_WO_A': round(dmax, 4),
                                 'ties_index0': far_ties, 'ties_qe1': [k + 1 for k in far_ties],
                                 'ties_symmetry_equivalent': len({int(eq[k]) for k in far_ties}) == 1,
                                 'next_distinct_A': round(next_far, 4),
                                 'next_distinct_index0': [k for k in iO if abs(dWO[k] - next_far) < TIE],
                                 'next_distinct_qe1': [k + 1 for k in iO if abs(dWO[k] - next_far) < TIE],
                                 'margin_A': round(dmax - next_far, 4),
                                 'frac': wfrac[far].round(6).tolist(),
                                 'max_possible_A': round(float(np.sqrt(3) * a / 2), 4)}
    # A19: second near candidate = the next distinct W-O pair (index0 72/73), lowest index of that pair
    assert wsym[NEAR72] == 'O' and NEAR72 == min(facts['selection']['near']['next_distinct_index0']), 'near72 index'
    assert abs(dWO[NEAR72] - 1.9024) < 1e-4, f'near72 W-O {dWO[NEAR72]}'
    n72_ties = [k for k in iO if abs(dWO[k] - dWO[NEAR72]) < TIE]
    facts['selection']['near72'] = {'index0': NEAR72, 'qe1': NEAR72 + 1, 'd_WO_A': round(dWO[NEAR72], 4),
                                    'ties_index0': n72_ties, 'ties_qe1': [k + 1 for k in n72_ties],
                                    'ties_symmetry_equivalent': len({int(eq[k]) for k in n72_ties}) == 1,
                                    'gap_to_near_A': round(dWO[NEAR72] - dmin, 4),
                                    'rule': ('A19: second near candidate; the registered near cell is chosen by '
                                             'select_near.py on the H-L-relaxed In31WO48'),
                                    'frac': wfrac[NEAR72].round(6).tolist()}
    # In neighbours of the removed O (first shell, < 2.6 A): [symbol, index0, qe1, distance]
    Dw = dist_matrix(wcell, wfrac)
    for tag, k in (('near', near), ('near72', NEAR72), ('far', far)):
        nb = [(wsym[j], int(j), int(j) + 1, round(float(Dw[k, j]), 4))
              for j in np.argsort(Dw[k]) if j != k and Dw[k, j] < 2.6]
        facts['selection'][tag]['cation_neighbours'] = nb

    # host vacancy: O nearest the cell centre (all 48 O are one 48e orbit, so any O is equivalent)
    hO = [k for k in range(len(hsym)) if hsym[k] == 'O']
    dc = {k: float(np.linalg.norm((hfrac[k] - 0.5) @ hcell)) for k in hO}
    cmin = min(dc.values())
    c_ties = [k for k in hO if dc[k] - cmin < TIE]
    hv = min(c_ties)
    facts['selection']['host'] = {'index0': hv, 'qe1': hv + 1, 'd_centre_A': round(cmin, 4),
                                  'ties_index0': c_ties, 'ties_qe1': [k + 1 for k in c_ties],
                                  'frac': hfrac[hv].round(6).tolist(),
                                  'rule': 'O nearest the cell centre (0.5,0.5,0.5); lowest index among ties'}

    cells = {
        'In32O48': (hcell, hsym, hfrac, 'host, bulk_conv.json'),
        'In31WO48': (wcell, wsym, wfrac, 'relaxed stage-4 iwo_W24d'),
        'In32O47': (hcell, [s for k, s in enumerate(hsym) if k != hv],
                    np.delete(hfrac, hv, axis=0), f'In32O48 minus O index0 {hv} (QE atom {hv + 1})'),
        'In31WO47_near': (wcell, [s for k, s in enumerate(wsym) if k != near],
                          np.delete(wfrac, near, axis=0),
                          f'relaxed In31WO48 minus O index0 {near} (QE atom {near + 1}) (near)'),
        'In31WO47_near72': (wcell, [s for k, s in enumerate(wsym) if k != NEAR72],
                            np.delete(wfrac, NEAR72, axis=0),
                            f'relaxed In31WO48 minus O index0 {NEAR72} (QE atom {NEAR72 + 1}) (near72, A19)'),
        'In31WO47_far': (wcell, [s for k, s in enumerate(wsym) if k != far],
                         np.delete(wfrac, far, axis=0),
                         f'relaxed In31WO48 minus O index0 {far} (QE atom {far + 1}) (far)'),
    }
    expect = {'In32O48': ({'In': 32, 'O': 48}, 704), 'In31WO48': ({'In': 31, 'W': 1, 'O': 48}, 705),
              'In32O47': ({'In': 32, 'O': 47}, 698), 'In31WO47_near': ({'In': 31, 'W': 1, 'O': 47}, 699),
              'In31WO47_near72': ({'In': 31, 'W': 1, 'O': 47}, 699),
              'In31WO47_far': ({'In': 31, 'W': 1, 'O': 47}, 699)}

    pilot = {'relax_node_vac.sh': PILOT / 'relax_node_pilot.sh', 'steps_relax.sh': PILOT / 'steps_relax.sh',
             'geomsel.py': PILOT / 'geomsel.py'}
    facts['pilot_copies_sha256'] = {k: sha(v) for k, v in pilot.items()}
    if STAGE.exists():
        shutil.rmtree(STAGE)
    for name in NAMES:
        cell, sym, frac, origin = cells[name]
        info, _ = checks(name, cell, sym, frac)
        assert info['composition'] == expect[name][0] and info['n_electrons'] == expect[name][1], (name, info)
        info['origin'] = origin
        facts['cells'][name] = info
        write_struct(name, cell, sym, frac, {'origin': origin, 'register': 'H-L (A17), D-19'})
        d = STAGE / name
        (d / 'logs').mkdir(parents=True)
        (d / 'logs' / '.keep').write_text('', newline='\n')
        rin, fin = qe_input('relax', cell, sym, frac, (3, 3, 3)), qe_input('scf', cell, sym, frac, (4, 4, 4))
        for txt in (rin, fin):                          # A19 (5): settings fixed for all six cells
            assert 'conv_thr = 1.0d-8, mixing_beta = 0.3, electron_maxstep = 100' in txt and 'mixing_mode' not in txt
        assert 'nstep = 300,' in rin
        (d / 'relax.in').write_text(rin, newline='\n')
        (d / 'final.tmpl').write_text(fin, newline='\n')
        (d / 'relax.sub').write_text(relax_sub(name), newline='\n')
        (d / 'final.sub').write_text(final_sub(name), newline='\n')
        (d / f'{name}.dag').write_text(DAG, newline='\n')
        (d / 'steps_final.sh').write_text(STEPS_FINAL, newline='\n')
        (d / 'final_node_vac.sh').write_text(FINAL_NODE, newline='\n')
        for dst, src in pilot.items():
            shutil.copyfile(src, d / dst)               # byte-identical copies of the repaired pilot scripts
        shutil.copyfile(OUT_STRUCT / f'{name}.xyz', d / f'{name}.xyz')
        for f in ('relax_node_vac.sh', 'final_node_vac.sh'):
            (d / f).chmod(0o755)
    (HERE / 'build_facts.json').write_text(json.dumps(facts, indent=1) + '\n', newline='\n')
    print(json.dumps({k: facts[k] for k in ('host', 'selection')}, indent=1)[:6000])
    for n in NAMES:
        c = facts['cells'][n]
        print(n, c['composition'], c['n_electrons'], 'min', c['min_distance_A'], c['min_pair_A'],
              c['cation_O_shell'], c['spacegroup'], c['n_ops'], 'irrk', c.get('irr_k_333_spglib'),
              c.get('irr_k_444_spglib'))


if __name__ == '__main__':
    main()
