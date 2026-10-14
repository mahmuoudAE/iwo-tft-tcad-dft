#!/usr/bin/env python3
"""Frozen comparator for the MACE force-validation ("val") jobs: DFT forces (QE scf.out) against MACE (mace_ref.json).

FROZEN on 2026-10-12 (UTC) by the git commit that adds this file, BEFORE any val output (val_results.tar.gz or the
scf.out of a val job) was read. Plan and limits: claude/plans/ML_VALIDATION.md (fixed 2026-10-10). Job inputs:
compute/amorph/dft/make_val.py. Any change after the freeze needs a logged amendment; every result records VERSION
and the sha256 of this file. Self-test: python3 -I test_compare_val.py (synthetic data only).

usage
  python3 -I compare_val.py [--val-root DIR] [--label-map JOB=PATH ...] [--out result.json] [JOB_DIR ...]
    --val-root DIR  evaluate the eight plan frames DIR/<name>_<tag> (an absent directory or tarball is MISSING)
    JOB_DIR         further val job directories (a plan frame is recognised by its <name>_<tag>)
    --label-map     label map of one job (overrides <JOB_DIR>/a30_label_map.tsv)
  exit code: 0 PASS, 1 FAIL, 3 INCOMPLETE, 2 usage error

inputs per job directory (make_val.py; val.sub / val_gpu.sub return the tarball)
  mace_ref.json       {"tag": ..., "energy_eV": ..., "forces_eV_A": [[fx, fy, fz], ...]} in snapshot atom order
  val_results.tar.gz  driver.sh pack; the member scf.out (QE 7.5 CPU or QE 7.3.1 GPU) is read in memory, never
                      extracted; the member scf.in, if present, is used for a geometry and label cross-check
  a30_label_map.tsv   split-label runs only (A25/A30: In -> In1/In2, O -> O1/O2): gives every atom its element

FROZEN DEFINITIONS
 D1 Units. QE prints forces in Ry/bohr ('Forces acting on atoms (cartesian axes, Ry/au)'). They are converted with
    RYBOHR_TO_EV_A = 13.605693122994 / 0.529177210903 = 25.711033738162943 (CODATA 2018, the constants of QE 7.x).
    (The freeze request quoted 25.71104309541616 for this ratio; that number is not the ratio. The difference,
    3.6e-7 relative, is immaterial to every limit; the ratio of the two CODATA 2018 constants is what is frozen.)
    Lengths: bohr * 0.529177210903 = A. MACE forces are taken as eV/A. Energies are not compared.
 D2 Pairing. Atom i of scf.out is atom i of mace_ref.json (make_val.py writes scf.in in snapshot order; the A25
    label split changes labels only). No reordering, no net-force removal, no rotation, no rescaling.
 D3 Element identity. Unsplit run: the species label must be an element symbol (In, W, Al, Hf, O, H) and is the
    element. Split run (any other label): the element comes from the label map (formats in parse_label_map), and
    it must equal the letters of the label (In1 -> In, O2 -> O); a split label without a map, or any disagreement,
    fails the frame (R11).
 D4 Metrics, DF = F_DFT - F_MACE in eV/A, per Cartesian component:
      RMSE_all = sqrt(mean DF^2) over all atoms and all 3 components
      MAE_all  = mean |DF|       over all atoms and all 3 components
      RMSE_W1  = sqrt(mean DF^2) over the 3 components of every atom of S (each atom once)
 D5 W first shell S = all W atoms + every O atom whose minimum-image distance to at least one W is <= 2.60 A.
    The plan gives no cutoff. A fixed 2.60 A is frozen instead of the first minimum of the W-O RDF, because the few W
    atoms per cell (the plan: W is the least-sampled element) give no usable W-O RDF; 2.60 A lies between the W-O first shell (about 1.7-2.2 A in W
    oxides) and the second shell (beyond about 3 A). Distances: DFT geometry printed in scf.out (cell 'crystal
    axes' x alat, positions in alat units), minimum image over the full 3D periodic cell (exact image search; the
    >= 10 A vacuum of slab cells makes z images irrelevant). H is never in S. A frame without W has RMSE_W1 = N/A
    and that limit is not applied to it. 2.60 A is also the W-O first-shell cutoff of compute/vacancy/make_vac.py.
    The amorphous pipeline counts W-O coordination at 2.45 A (mace_amorph.CUT, analysis/register.py
    W_O_FIRST_SHELL_A); RMSE_W1 at 2.45 A is therefore also printed as INFO (rmse_W1_at_2p45_info_eV_A, with its
    S), but it never enters a verdict. The per-W record lists every O within 2.60 A with its distance.
 D6 Limits (ML_VALIDATION.md; inclusive; compared at full precision, never on rounded numbers):
      RMSE_all <= 0.15 eV/A,  MAE_all <= 0.10 eV/A,  RMSE_W1 <= 0.25 eV/A.
    Applied to each scored frame separately. Scored tags: quenched_300K, slab_annealed, final. Melt frames (tag
    melt_*) are computed and REPORTED, never scored. Frames outside the plan list are OUT_OF_PLAN: metrics only.
 D7 Verdicts. Frame: PASS if all applicable limits hold, else FAIL. Structure (over its plan scored frames): FAIL if
    any frame FAIL; PASS if every one is PASS; otherwise INCOMPLETE (a frame MISSING or FAIL_NOT_SCORED).
    Overall: the same rule over the four plan structures.
 D8 Stop rule (plan): aIWO_2p0_s1 is TRIGGERED if RMSE_all > 0.30 eV/A on any of its scored frames; NOT_TRIGGERED
    if both scored frames are SCORED with RMSE_all <= 0.30; otherwise UNDETERMINED.
 D9 Fail rules. A frame is FAIL_NOT_SCORED (none of its numbers enters any verdict) if
      R1  scf.out contains 'convergence NOT achieved'                                   (reviewer change 2)
      R2  scf.out contains 'Maximum CPU time'                                           (reviewer change 2)
      R3  the forces block is missing                                                    (reviewer change 2)
      R4  the forces block row count differs from nat                                    (reviewer change 2)
      R5  scf.out lacks 'convergence has been achieved'
      R6  more than one forces block, rows not numbered 1..nat in order, or a non-finite value
      R7  nat absent or ambiguous in scf.out, or nat differs from the number of MACE force rows
      R8  scf.out contains a QE error banner ('Error in routine')
      R9  val_results.tar.gz unreadable or empty, or not exactly one scf.out member
      R10 mace_ref.json unreadable or malformed, its tag missing or unknown, or the job directory is not
          <name>_<tag> (or not the expected plan frame)
      R11 label/element problem (D3), including an invalid label map
      R12 no usable geometry (scf.out cell/positions, else scf.in with CELL_PARAMETERS angstrom and
          ATOMIC_POSITIONS angstrom or crystal), or scf.in and scf.out disagree in labels or by more than 1e-3 A
          in a cell vector or position
    A job directory without val_results.tar.gz (job not returned) is MISSING, not FAIL_NOT_SCORED.

FORMAT CHECK before the freeze (no val output involved): the scf.out parser was run on six earlier, non-val
outputs in IWO_PHYSICS_CONSTRAINED_MODEL_V1/qe_workflow/cern_htcondor/results (QE 7.3.1 GPU: gpu_bench_v15 96 atoms,
slab1_relax_gpu 96, nc_pbe_bulk_e80 40; QE 7.5 CPU: iwo_slab1_final_cpu 96, slab1r_final_cpu 96, iwo_slab2_final_cpu
176). In each, no fail rule fired, nat and all nat force rows were read, and the scf.out cell and positions agreed
with scf.in to <= 8.4e-5 A. The pack layout (scf.out and scf.in at the top level of <job>_results.tar.gz) was
checked on gpu_bench_v15_results.tar.gz. The label-map writer (a25_labels.py) is on CERN only; parse_label_map
therefore accepts the plausible TSV forms and refuses anything else (R11: not scored, never guessed).
"""
import argparse
import hashlib
import json
import math
import os
import posixpath
import re
import sys
import tarfile
import zlib

VERSION = '1.0.0'
FROZEN = '2026-10-12 (UTC), commit adding this file; before any val output was read'

RY_EV = 13.605693122994
BOHR_A = 0.529177210903
RYBOHR_TO_EV_A = RY_EV / BOHR_A          # 25.711033738162943

LIMIT_RMSE = 0.15
LIMIT_MAE = 0.10
LIMIT_W1 = 0.25
STOP_RMSE = 0.30
W_SHELL_CUTOFF_A = 2.60
W_SHELL_INFO_A = 2.45                    # mace_amorph.CUT[('W','O')]: INFO only, never in a verdict (D5)
INFO_RADIUS_A = 4.10                     # nearest O beyond the cutoff is reported up to this distance (info only)
GEOM_TOL_A = 1.0e-3

KNOWN_ELEMENTS = ('In', 'W', 'Al', 'Hf', 'O', 'H')
SCORED_TAGS = ('quenched_300K', 'slab_annealed', 'final')
REPORT_PREFIX = 'melt_'
PLAN_FRAMES = (('aIWO_bulk_s1', 'melt_3000K'), ('aIWO_bulk_s1', 'quenched_300K'), ('aIWO_bulk_s1', 'final'),
               ('aIO_bulk_s1', 'quenched_300K'), ('aIO_bulk_s1', 'final'),
               ('aIWO_2p0_s1', 'slab_annealed'), ('aIWO_2p0_s1', 'final'),
               ('aIWO_0p7_s1', 'final'))
PLAN_STRUCTURES = ('aIWO_bulk_s1', 'aIO_bulk_s1', 'aIWO_2p0_s1', 'aIWO_0p7_s1')
STOP_STRUCTURE = 'aIWO_2p0_s1'
TARBALL = 'val_results.tar.gz'
REF_NAME = 'mace_ref.json'
MAP_NAME = 'a30_label_map.tsv'

FORCE_HEADER = 'Forces acting on atoms (cartesian axes, Ry/au)'
_F = r'[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eEdD][-+]?\d+)?'
_FORCE_ROW = re.compile(r'^\s*atom\s+(\d+)\s+type\s+(\d+)\s+force\s*=\s*(%s)\s+(%s)\s+(%s)\s*$' % (_F, _F, _F))
_POS_ROW = re.compile(r'^\s*(\d+)\s+(\S+)\s+tau\(\s*(\d+)\)\s*=\s*\(\s*(%s)\s+(%s)\s+(%s)\s*\)\s*$' % (_F, _F, _F))
_AXIS = r'a\(%d\)\s*=\s*\(\s*(' + _F + r')\s+(' + _F + r')\s+(' + _F + r')\s*\)'
_AXES = re.compile(r'crystal axes: \(cart\. coord\. in units of alat\)\s*\n\s*' + _AXIS % 1 + r'\s*\n\s*'
                   + _AXIS % 2 + r'\s*\n\s*' + _AXIS % 3)


class FrameFail(Exception):
    def __init__(self, code, msg):
        super().__init__(f'{code}: {msg}')
        self.code, self.msg = code, msg


def ffloat(s):
    v = float(s.replace('D', 'E').replace('d', 'e'))
    if not math.isfinite(v):
        raise ValueError(s)
    return v


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def element_of(label):
    """Letters of a species label, capitalised as an element symbol ('In1' -> 'In', 'O2' -> 'O')."""
    s = re.sub(r'[^A-Za-z]', '', label)
    return s[:1].upper() + s[1:].lower() if s else s


# ---------------------------------------------------------------- linear algebra (3x3, stdlib only)
def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(a):
    return math.sqrt(_dot(a, a))


def cell_inverse(cell):
    """Inverse of the matrix whose rows are the cell vectors; fractional f = r . inv."""
    a, b, c = cell
    vol = _dot(a, _cross(b, c))
    if not abs(vol) > 1e-9:
        raise ValueError('degenerate cell')
    bc, ca, ab = _cross(b, c), _cross(c, a), _cross(a, b)
    # inv[j][k]: column k is the reciprocal vector / vol
    return [[bc[0] / vol, ca[0] / vol, ab[0] / vol],
            [bc[1] / vol, ca[1] / vol, ab[1] / vol],
            [bc[2] / vol, ca[2] / vol, ab[2] / vol]], abs(vol)


class MinImage:
    """Exact minimum-image distances in a general (triclinic) periodic cell up to a search radius."""

    def __init__(self, cell, radius):
        self.cell = cell
        self.inv, vol = cell_inverse(cell)
        a, b, c = cell
        widths = [vol / _norm(_cross(b, c)), vol / _norm(_cross(c, a)), vol / _norm(_cross(a, b))]
        self.m = [int(math.ceil(radius / w)) + 1 for w in widths]

    def delta(self, r1, r2):
        d = [r2[k] - r1[k] for k in range(3)]
        f = [d[0] * self.inv[0][k] + d[1] * self.inv[1][k] + d[2] * self.inv[2][k] for k in range(3)]
        f = [x - round(x) for x in f]
        a, b, c = self.cell
        best = None
        for i in range(-self.m[0], self.m[0] + 1):
            for j in range(-self.m[1], self.m[1] + 1):
                for k in range(-self.m[2], self.m[2] + 1):
                    v = [(f[0] + i) * a[q] + (f[1] + j) * b[q] + (f[2] + k) * c[q] for q in range(3)]
                    dd = _dot(v, v)
                    if best is None or dd < best[0]:
                        best = (dd, v)
        return best[1]

    def distance(self, r1, r2):
        return _norm(self.delta(r1, r2))


# ---------------------------------------------------------------- scf.out
def parse_scf_out(text):
    """Checks R1-R8 on the text of scf.out; returns forces (Ry/bohr), labels/geometry if printed, QE info."""
    reasons = []
    if 'convergence NOT achieved' in text:
        reasons.append(('R1', "scf.out contains 'convergence NOT achieved'"))
    if 'Maximum CPU time' in text:
        reasons.append(('R2', "scf.out contains 'Maximum CPU time'"))
    if 'convergence has been achieved' not in text:
        reasons.append(('R5', "scf.out lacks 'convergence has been achieved'"))
    if 'Error in routine' in text:
        reasons.append(('R8', "scf.out contains a QE error banner ('Error in routine')"))
    nats = set(re.findall(r'number of atoms/cell\s*=\s*(\d+)', text))
    nat = int(nats.pop()) if len(nats) == 1 else None
    if nat is None:
        reasons.append(('R7', f'nat absent or ambiguous in scf.out ({len(nats)} values)'))
    lines = text.splitlines()
    heads = [i for i, ln in enumerate(lines) if FORCE_HEADER in ln]
    forces = None
    if not heads:
        reasons.append(('R3', 'forces block missing'))
    elif len(heads) > 1:
        reasons.append(('R6', f'{len(heads)} forces blocks'))
    else:
        j = heads[0] + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        rows = []
        while j < len(lines):
            m = _FORCE_ROW.match(lines[j])
            if not m:
                break
            rows.append(m)
            j += 1
        if nat is not None and len(rows) != nat:
            reasons.append(('R4', f'forces block has {len(rows)} rows, nat = {nat}'))
        elif not rows:
            reasons.append(('R3', 'forces block has no rows'))
        elif [int(m.group(1)) for m in rows] != list(range(1, len(rows) + 1)):
            reasons.append(('R6', 'force rows not numbered 1..nat in order'))
        else:
            try:
                forces = [[ffloat(m.group(k)) for k in (3, 4, 5)] for m in rows]
            except ValueError as e:
                reasons.append(('R6', f'non-finite or unparseable force value {e}'))
    info = {'qe_version': None, 'scf_iterations': None, 'job_done': 'JOB DONE' in text,
            'total_force_ry_bohr': None, 'total_scf_correction_ry_bohr': None}
    m = re.search(r'Program PWSCF v\.(\S+) starts', text)
    if m:
        info['qe_version'] = m.group(1)
    m = re.findall(r'convergence has been achieved in\s+(\d+)\s+iterations', text)
    if m:
        info['scf_iterations'] = int(m[-1])
    m = re.findall(r'Total force =\s*(' + _F + r')\s+Total SCF correction =\s*(' + _F + ')', text)
    if m:
        info['total_force_ry_bohr'], info['total_scf_correction_ry_bohr'] = ffloat(m[-1][0]), ffloat(m[-1][1])
    return {'nat': nat, 'forces_ry_bohr': forces, 'geometry': scf_out_geometry(text, lines, nat),
            'reasons': reasons, 'info': info}


def scf_out_geometry(text, lines, nat):
    """Cell and positions (A) and labels from the scf.out summary; None if anything is absent or incomplete."""
    m = re.search(r'lattice parameter \(alat\)\s*=\s*(' + _F + r')\s*a\.u\.', text)
    ax = _AXES.search(text)
    head = next((i for i, ln in enumerate(lines) if 'site n.' in ln and 'positions (alat units)' in ln), None)
    if not (m and ax and head is not None and nat):
        return None
    try:
        alat_a = ffloat(m.group(1)) * BOHR_A
        g = [ffloat(x) for x in ax.groups()]
        cell = [[alat_a * g[3 * r + q] for q in range(3)] for r in range(3)]
        labels, pos = [], []
        for ln in lines[head + 1:head + 1 + nat]:
            p = _POS_ROW.match(ln)
            if not p or int(p.group(1)) != len(labels) + 1 or int(p.group(3)) != len(labels) + 1:
                return None
            labels.append(p.group(2))
            pos.append([alat_a * ffloat(p.group(k)) for k in (4, 5, 6)])
    except ValueError:
        return None
    return {'cell': cell, 'labels': labels, 'pos': pos} if len(labels) == nat else None


def scf_in_geometry(text):
    """CELL_PARAMETERS angstrom + ATOMIC_POSITIONS angstrom (make_dft.qe_input) or crystal of a pw.x input;
    None for any other form."""
    lines = text.splitlines()
    try:
        ci = next(i for i, ln in enumerate(lines) if ln.strip().upper().startswith('CELL_PARAMETERS'))
        pi = next(i for i, ln in enumerate(lines) if ln.strip().upper().startswith('ATOMIC_POSITIONS'))
        unit = lines[pi].lower()
        if 'angstrom' not in lines[ci].lower() or 'crystal_sg' in unit:
            return None
        crystal = 'crystal' in unit
        if not crystal and 'angstrom' not in unit:
            return None
        cell = [[ffloat(x) for x in lines[ci + 1 + r].split()[:3]] for r in range(3)]
        nat = int(re.search(r'\bnat\s*=\s*(\d+)', text).group(1))
        labels, pos = [], []
        for ln in lines[pi + 1:pi + 1 + nat]:
            f = ln.split()
            labels.append(f[0])
            v = [ffloat(x) for x in f[1:4]]
            pos.append([sum(v[r] * cell[r][q] for r in range(3)) for q in range(3)] if crystal else v)
        if len(labels) != nat or any(len(c) != 3 for c in cell) or any(len(p) != 3 for p in pos):
            return None
    except (StopIteration, AttributeError, ValueError, IndexError):
        return None
    return {'cell': cell, 'labels': labels, 'pos': pos}


# ---------------------------------------------------------------- label map
_IDX_NAMES = {'index', 'idx', 'i', 'atom', 'atomindex', 'atomidx', 'iatom', 'na', 'n', 'site'}
_ELEM_NAMES = {'element', 'elem', 'el', 'original', 'orig', 'originallabel', 'origlabel', 'unsplit',
               'unsplitlabel', 'restored', 'old', 'oldlabel'}
_SPLIT_NAMES = {'split', 'splitlabel', 'label', 'new', 'newlabel', 'qelabel', 'splitspecies'}


def _hname(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def _is_int(s):
    return re.fullmatch(r'[-+]?\d+', s) is not None


def parse_label_map(text):
    """Accepted formats (tab-separated, or whitespace if a line has no tab; '#' lines and blank lines skipped):
      per atom : one row per atom with an integer index (1-based 1..nat or 0-based 0..nat-1), the element (original
                 label) and optionally the split label;
      per label: rows 'split_label  element' (no index), e.g. 'In1  In'.
    An optional header row (no integer field, at least one known column name) names the columns: index
    {index, idx, i, atom, ...}, element {element, original, orig, unsplit, ...}, split label {split, label, new, ...}.
    Without a header the integer column is the index, and of two label columns the one holding only element symbols
    is the element. Anything else is refused (ValueError). Returns ('atom', {index0: (element, split|None)}) or
    ('label', {split_label: element})."""
    rows = []
    for ln in text.lstrip('\ufeff').splitlines():
        s = ln.strip()
        if not s or s.startswith('#'):
            continue
        rows.append([x.strip() for x in s.split('\t')] if '\t' in s else s.split())
    if not rows:
        raise ValueError('label map is empty')
    known = _IDX_NAMES | _ELEM_NAMES | _SPLIT_NAMES
    header = None
    if not any(_is_int(x) for x in rows[0]) and any(_hname(x) in known for x in rows[0]):
        header, rows = [_hname(x) for x in rows[0]], rows[1:]
    if not rows:
        raise ValueError('label map has no data rows')
    ncol = len(header) if header else len(rows[0])
    if any(len(r) != ncol for r in rows):
        raise ValueError('label map rows have different numbers of fields')
    if header:
        def one(names, required):
            cols = [k for k, h in enumerate(header) if h in names]
            if len(cols) > 1 or (required and not cols):
                raise ValueError(f'label map header {header}: {len(cols)} columns for {sorted(names)[:3]}...')
            return cols[0] if cols else None
        ic, ec, sc = one(_IDX_NAMES, False), one(_ELEM_NAMES, True), one(_SPLIT_NAMES, False)
        if ic is not None and not all(_is_int(r[ic]) for r in rows):
            raise ValueError('label map index column is not integer')
    else:
        ints = [k for k in range(ncol) if all(_is_int(r[k]) for r in rows)]
        if len(ints) > 1:
            raise ValueError('label map has more than one integer column')
        ic = ints[0] if ints else None
        labs = [k for k in range(ncol) if k != ic]
        is_el = [all(r[k] in KNOWN_ELEMENTS for r in rows) for k in labs]
        if len(labs) == 1 and is_el[0] and ic is not None:
            ec, sc = labs[0], None
        elif len(labs) == 2 and is_el[0] != is_el[1]:
            ec, sc = (labs[0], labs[1]) if is_el[0] else (labs[1], labs[0])
        elif len(labs) == 2 and is_el[0] and all(r[labs[0]] == r[labs[1]] for r in rows):
            ec, sc = labs
        else:
            raise ValueError('label map columns cannot be identified without a header')
    if ic is not None:
        idx = [int(r[ic]) for r in rows]
        n = len(rows)
        if sorted(idx) == list(range(1, n + 1)):
            base = 1
        elif sorted(idx) == list(range(n)):
            base = 0
        else:
            raise ValueError('label map indices are not a permutation of 1..n or 0..n-1')
        return 'atom', {i - base: (r[ec], r[sc] if sc is not None else None) for i, r in zip(idx, rows)}
    if sc is None:
        raise ValueError('per-label map without a split-label column')
    out = {}
    for r in rows:
        if r[sc] in out and out[r[sc]] != r[ec]:
            raise ValueError(f'label {r[sc]} mapped to two elements')
        out[r[sc]] = r[ec]
    return 'label', out


def resolve_elements(labels, map_text):
    """Element of every atom (D3). Raises FrameFail R11."""
    plain = all(x in KNOWN_ELEMENTS for x in labels)
    if map_text is None:
        if not plain:
            raise FrameFail('R11', f'labels {sorted(set(x for x in labels if x not in KNOWN_ELEMENTS))} '
                                   'are not element symbols and no label map was found')
        return list(labels)
    try:
        kind, mp = parse_label_map(map_text)
    except ValueError as e:
        raise FrameFail('R11', f'invalid label map: {e}')
    els = []
    if kind == 'atom':
        if len(mp) != len(labels):
            raise FrameFail('R11', f'label map has {len(mp)} atoms, scf.out has {len(labels)}')
        for i, lab in enumerate(labels):
            el, sp = mp[i]
            if sp is not None and sp != lab:
                raise FrameFail('R11', f'atom {i + 1}: map split label {sp} != scf.out label {lab}')
            els.append(el)
    else:
        for i, lab in enumerate(labels):
            if lab in mp:
                els.append(mp[lab])
            elif lab in KNOWN_ELEMENTS:
                els.append(lab)
            else:
                raise FrameFail('R11', f'atom {i + 1}: label {lab} not in the label map')
    for i, (lab, el) in enumerate(zip(labels, els)):
        if el not in KNOWN_ELEMENTS:
            raise FrameFail('R11', f'atom {i + 1}: map element {el} is not a known element')
        if element_of(lab) != el:
            raise FrameFail('R11', f'atom {i + 1}: map element {el} disagrees with label {lab}')
    return els


# ---------------------------------------------------------------- metrics
def w_first_shell(geom, elements):
    """S (D5), per-W details and the INFO set at W_SHELL_INFO_A; ([], {}, []) without W."""
    ws = [i for i, e in enumerate(elements) if e == 'W']
    if not ws:
        return [], {}, []
    mi = MinImage(geom['cell'], max(W_SHELL_CUTOFF_A, INFO_RADIUS_A))
    os_ = [j for j, e in enumerate(elements) if e == 'O']
    shell, shell_info, per = set(ws), set(ws), {}
    for w in ws:
        near, beyond = [], None
        for o in os_:
            d = mi.distance(geom['pos'][w], geom['pos'][o])
            if d <= W_SHELL_CUTOFF_A:
                near.append((o + 1, round(d, 4)))
                shell.add(o)
                if d <= W_SHELL_INFO_A:
                    shell_info.add(o)
            elif d <= INFO_RADIUS_A and (beyond is None or d < beyond):
                beyond = d
        per[w + 1] = {'O_within_cutoff': near, 'CN_O': len(near),
                      'nearest_O_beyond_cutoff_A': round(beyond, 4) if beyond is not None else None}
    return sorted(shell), per, sorted(shell_info)


def force_metrics(dft, mace, elements, shell, shell_info=()):
    n = len(dft)
    d = [[dft[i][c] - mace[i][c] for c in range(3)] for i in range(n)]
    sq = [x * x for row in d for x in row]
    ab = [abs(x) for row in d for x in row]
    imax = max(range(3 * n), key=lambda k: ab[k])
    out = {'n_atoms': n, 'n_components': 3 * n,
           'rmse_all_eV_A': math.sqrt(math.fsum(sq) / (3 * n)),
           'mae_all_eV_A': math.fsum(ab) / (3 * n),
           'max_abs_component_eV_A': ab[imax], 'max_abs_at': {'atom': imax // 3 + 1, 'component': 'xyz'[imax % 3]},
           'dft_force_rms_eV_A': math.sqrt(math.fsum(x * x for row in dft for x in row) / (3 * n)),
           'rmse_by_element_eV_A': {}}
    for el in sorted(set(elements)):
        ids = [i for i in range(n) if elements[i] == el]
        out['rmse_by_element_eV_A'][el] = math.sqrt(math.fsum(d[i][c] ** 2 for i in ids for c in range(3)) / (3 * len(ids)))
    if shell:
        out['rmse_W1_eV_A'] = math.sqrt(math.fsum(d[i][c] ** 2 for i in shell for c in range(3)) / (3 * len(shell)))
        out['n_W1_atoms'] = len(shell)
    else:
        out['rmse_W1_eV_A'] = None
        out['n_W1_atoms'] = 0
    out['rmse_W1_at_2p45_info_eV_A'] = (math.sqrt(math.fsum(d[i][c] ** 2 for i in shell_info for c in range(3))
                                                  / (3 * len(shell_info))) if shell_info else None)
    return out


def frame_verdict(m):
    crit = {'rmse_all': m['rmse_all_eV_A'] <= LIMIT_RMSE, 'mae_all': m['mae_all_eV_A'] <= LIMIT_MAE,
            'rmse_W1': None if m['rmse_W1_eV_A'] is None else m['rmse_W1_eV_A'] <= LIMIT_W1}
    return ('PASS' if all(v is not False for v in crit.values()) else 'FAIL'), crit


# ---------------------------------------------------------------- one job
def _read_file(path):
    with open(path, 'rb') as f:
        return f.read()


def _geom_agree(a, b):
    if len(a['labels']) != len(b['labels']):
        return False, f'{len(a["labels"])} atoms against {len(b["labels"])}'
    if a['labels'] != b['labels']:
        k = next(i for i, (x, y) in enumerate(zip(a['labels'], b['labels'])) if x != y)
        return False, f'labels differ, first at atom {k + 1} ({a["labels"][k]} / {b["labels"][k]})'
    for r in range(3):
        if max(abs(a['cell'][r][q] - b['cell'][r][q]) for q in range(3)) > GEOM_TOL_A:
            return False, f'cell vector {r + 1} differs by more than {GEOM_TOL_A} A'
    mi = MinImage(b['cell'], 1.0)
    for i, (p, q) in enumerate(zip(a['pos'], b['pos'])):
        dist = mi.distance(p, q)
        if dist > GEOM_TOL_A:
            return False, f'atom {i + 1} differs by {dist:.4g} A'
    return True, ''


def evaluate_job(job_dir, expected=None, map_path=None):
    """One frame record. expected = (name, tag) of a plan frame requested through --val-root, else None."""
    job = os.path.basename(os.path.normpath(job_dir))
    fr = {'job': job, 'job_dir': os.path.abspath(job_dir), 'name': expected[0] if expected else None,
          'tag': expected[1] if expected else None, 'class': None, 'in_plan': False, 'status': None,
          'verdict': None, 'criteria': None, 'reasons': [], 'metrics': None, 'W_shell': None, 'qe': None,
          'elements_source': None, 'geometry_source': None, 'inputs_sha256': {}}

    def cls_of(tag):
        return 'scored' if tag in SCORED_TAGS else ('report' if tag.startswith(REPORT_PREFIX) else None)

    if expected:
        fr['class'], fr['in_plan'] = cls_of(expected[1]), True
    tar_path = os.path.join(job_dir, TARBALL)
    if not os.path.isdir(job_dir):
        fr['status'], fr['reasons'] = 'MISSING', [['-', 'no job directory']]
        return fr
    if not os.path.exists(tar_path):
        fr['status'], fr['reasons'] = 'MISSING', [['-', f'no {TARBALL} (job output not returned)']]
        return fr
    try:
        ref, n_ref = _load_ref(job_dir, job, expected, fr)
        tar_bytes = _read_file(tar_path)
        fr['inputs_sha256'][TARBALL] = sha256_bytes(tar_bytes)
        scf_out, scf_in = _read_tar(tar_path, fr)
        text = scf_out.decode('utf-8', errors='replace')
        p = parse_scf_out(text)
        fr['qe'] = p['info']
        reasons = list(p['reasons'])
        if p['nat'] is not None and p['nat'] != n_ref:
            reasons.append(('R7', f'nat {p["nat"]} in scf.out, {n_ref} MACE force rows'))
        if reasons:
            raise _Multi(reasons)
        geo_out = p['geometry']
        geo_in = scf_in_geometry(scf_in.decode('utf-8', errors='replace')) if scf_in is not None else None
        if geo_out is not None and geo_in is not None:
            ok, why = _geom_agree(geo_out, geo_in)
            if not ok:
                raise FrameFail('R12', f'scf.in and scf.out disagree: {why}')
            fr['geometry_source'] = 'scf.out (cross-checked against scf.in)'
        elif geo_out is not None:
            fr['geometry_source'] = 'scf.out (no usable scf.in in the tarball)'
        elif geo_in is not None:
            fr['geometry_source'] = 'scf.in (scf.out has no complete geometry)'
        else:
            raise FrameFail('R12', 'no usable geometry in scf.out or scf.in')
        geom = geo_out if geo_out is not None else geo_in
        if len(geom['labels']) != p['nat']:
            raise FrameFail('R12', f'geometry has {len(geom["labels"])} atoms, nat = {p["nat"]}')
        mp = map_path if map_path else (os.path.join(job_dir, MAP_NAME)
                                        if os.path.exists(os.path.join(job_dir, MAP_NAME)) else None)
        map_text = None
        if mp:
            try:
                mb = _read_file(mp)
            except OSError as e:
                raise FrameFail('R11', f'label map {mp} unreadable: {e}')
            fr['inputs_sha256'][os.path.basename(mp)] = sha256_bytes(mb)
            map_text = mb.decode('utf-8', errors='replace')
        elements = resolve_elements(geom['labels'], map_text)
        fr['elements_source'] = f'label map {os.path.abspath(mp)}' if mp else 'scf.out labels (element symbols)'
        fr['composition'] = {e: elements.count(e) for e in sorted(set(elements))}
        shell, per_w, shell_info = w_first_shell(geom, elements)
        fr['W_shell'] = {'cutoff_A': W_SHELL_CUTOFF_A, 'W_atoms': [i + 1 for i, e in enumerate(elements) if e == 'W'],
                         'S_atoms': [i + 1 for i in shell], 'per_W': per_w,
                         'info_cutoff_A': W_SHELL_INFO_A, 'S_atoms_at_2p45_info': [i + 1 for i in shell_info]}
        dft = [[x * RYBOHR_TO_EV_A for x in row] for row in p['forces_ry_bohr']]
        fr['metrics'] = force_metrics(dft, ref['forces_eV_A'], elements, shell, shell_info)
    except _Multi as e:
        fr['status'], fr['reasons'] = 'FAIL_NOT_SCORED', [list(r) for r in e.reasons]
        return fr
    except FrameFail as e:
        fr['status'], fr['reasons'] = 'FAIL_NOT_SCORED', [[e.code, e.msg]]
        return fr
    if not fr['in_plan']:
        fr['status'] = 'OUT_OF_PLAN'
    elif fr['class'] == 'report':
        fr['status'] = 'REPORTED'
    else:
        fr['status'] = 'SCORED'
        fr['verdict'], fr['criteria'] = frame_verdict(fr['metrics'])
    return fr


class _Multi(Exception):
    def __init__(self, reasons):
        super().__init__('; '.join(f'{c}: {m}' for c, m in reasons))
        self.reasons = reasons


def _load_ref(job_dir, job, expected, fr):
    path = os.path.join(job_dir, REF_NAME)
    try:
        b = _read_file(path)
        fr['inputs_sha256'][REF_NAME] = sha256_bytes(b)
        ref = json.loads(b.decode('utf-8-sig'))
    except (OSError, ValueError) as e:
        raise FrameFail('R10', f'{REF_NAME} unreadable: {e}')
    tag = ref.get('tag') if isinstance(ref, dict) else None
    if not isinstance(tag, str) or not tag or not job.endswith('_' + tag) or len(job) <= len(tag) + 1:
        raise FrameFail('R10', f'tag {tag!r} missing or job directory {job} is not <name>_<tag>')
    name = job[:-len(tag) - 1]
    if expected and (name, tag) != tuple(expected):
        raise FrameFail('R10', f'expected plan frame {expected[0]}_{expected[1]}, {REF_NAME} gives {name}_{tag}')
    fr['name'], fr['tag'] = name, tag
    fr['in_plan'] = (name, tag) in PLAN_FRAMES
    fr['class'] = 'scored' if tag in SCORED_TAGS else ('report' if tag.startswith(REPORT_PREFIX) else None)
    if fr['class'] is None:
        raise FrameFail('R10', f'unknown tag {tag!r} (scoring class undefined)')
    f = ref.get('forces_eV_A')
    try:
        ok = isinstance(f, list) and len(f) > 0 and all(
            isinstance(r, list) and len(r) == 3 and all(isinstance(x, (int, float)) and not isinstance(x, bool)
                                                       and math.isfinite(x) for x in r) for r in f)
    except TypeError:
        ok = False
    if not ok:
        raise FrameFail('R10', f'{REF_NAME} forces_eV_A missing or not a list of finite [fx, fy, fz]')
    return ref, len(f)


def _read_tar(tar_path, fr):
    try:
        with tarfile.open(tar_path, 'r:gz') as tf:
            members = [m for m in tf.getmembers() if m.isfile()]
            outs = [m for m in members if posixpath.basename(m.name) == 'scf.out']
            ins = [m for m in members if posixpath.basename(m.name) == 'scf.in']
            if len(outs) != 1:
                raise FrameFail('R9', f'{len(outs)} scf.out members in {TARBALL}')
            scf_out = tf.extractfile(outs[0]).read()
            scf_in = tf.extractfile(ins[0]).read() if len(ins) == 1 else None
    except (OSError, EOFError, tarfile.TarError, zlib.error) as e:
        raise FrameFail('R9', f'{TARBALL} unreadable: {e}')
    fr['inputs_sha256']['scf.out'] = sha256_bytes(scf_out)
    if scf_in is not None:
        fr['inputs_sha256']['scf.in'] = sha256_bytes(scf_in)
    return scf_out, scf_in


# ---------------------------------------------------------------- roll-up and report
def rollup(frames):
    by_key = {}
    for f in frames:
        if f['in_plan'] and f['name'] is not None:
            key = (f['name'], f['tag'])
            if key in by_key:
                raise ValueError(f'plan frame {key[0]}_{key[1]} given twice')
            by_key[key] = f
    structures = {}
    for s in PLAN_STRUCTURES:
        verdicts = []
        for name, tag in PLAN_FRAMES:
            if name != s or tag not in SCORED_TAGS:
                continue
            f = by_key.get((name, tag))
            verdicts.append(f['verdict'] if f is not None and f['status'] == 'SCORED' else None)
        structures[s] = 'FAIL' if 'FAIL' in verdicts else ('PASS' if all(v == 'PASS' for v in verdicts)
                                                           else 'INCOMPLETE')
    vals = list(structures.values())
    overall = 'FAIL' if 'FAIL' in vals else ('PASS' if all(v == 'PASS' for v in vals) else 'INCOMPLETE')
    stop = [by_key.get((n, t)) for n, t in PLAN_FRAMES if n == STOP_STRUCTURE and t in SCORED_TAGS]
    rm = [f['metrics']['rmse_all_eV_A'] for f in stop if f is not None and f['status'] == 'SCORED']
    if any(x > STOP_RMSE for x in rm):
        stop_rule = 'TRIGGERED'
    elif len(rm) == len(stop):
        stop_rule = 'NOT_TRIGGERED'
    else:
        stop_rule = 'UNDETERMINED'
    missing = [f'{n}_{t}' for n, t in PLAN_FRAMES if (n, t) not in by_key]
    return {'structures': structures, 'overall': overall, 'stop_rule_' + STOP_STRUCTURE: stop_rule,
            'plan_frames_not_supplied': missing}


def definitions():
    return {'version': VERSION, 'frozen': FROZEN, 'RYBOHR_TO_EV_A': RYBOHR_TO_EV_A, 'RY_EV': RY_EV, 'BOHR_A': BOHR_A,
            'limits_eV_A': {'rmse_all': LIMIT_RMSE, 'mae_all': LIMIT_MAE, 'rmse_W1': LIMIT_W1},
            'stop_rule': f'{STOP_STRUCTURE}: RMSE_all > {STOP_RMSE} eV/A on any scored frame',
            'W_shell': f'W atoms + O with minimum-image W-O distance <= {W_SHELL_CUTOFF_A} A (H excluded)',
            'W_shell_info_only': f'same at {W_SHELL_INFO_A} A (mace_amorph.CUT W-O), reported, never scored',
            'scored_tags': list(SCORED_TAGS), 'report_only_tags': REPORT_PREFIX + '*',
            'plan_frames': [f'{n}_{t}' for n, t in PLAN_FRAMES]}


def _fmt(x):
    return '-' if x is None else f'{x:.4f}'


def report_text(result):
    out = [f'compare_val.py {VERSION} (sha256 {result["comparator_sha256"][:16]}...)  '
           f'Ry/bohr->eV/A {RYBOHR_TO_EV_A!r}',
           f'limits: RMSE_all <= {LIMIT_RMSE}, MAE_all <= {LIMIT_MAE}, RMSE_W1 <= {LIMIT_W1} eV/A '
           f'(W shell: O within {W_SHELL_CUTOFF_A} A of W)',
           f'{"job":34s} {"status":16s} {"nat":>4s} {"W":>2s} {"|S|":>4s} {"RMSE":>7s} {"MAE":>7s} {"RMSE_W1":>7s}  verdict']
    for f in result['frames']:
        m = f['metrics'] or {}
        nw = len(f['W_shell']['W_atoms']) if f['W_shell'] else None
        out.append(f'{f["job"][:34]:34s} {f["status"]:16s} {str(m.get("n_atoms", "-")):>4s} '
                   f'{"-" if nw is None else str(nw):>2s} {str(m.get("n_W1_atoms", "-")):>4s} '
                   f'{_fmt(m.get("rmse_all_eV_A")):>7s} {_fmt(m.get("mae_all_eV_A")):>7s} '
                   f'{_fmt(m.get("rmse_W1_eV_A")):>7s}  {f["verdict"] or "-"}')
        for c, msg in f['reasons']:
            out.append(f'    {c}: {msg}')
    for s, v in result['rollup']['structures'].items():
        out.append(f'structure {s}: {v}')
    out.append(f'stop rule {STOP_STRUCTURE}: {result["rollup"]["stop_rule_" + STOP_STRUCTURE]}')
    if result['rollup']['plan_frames_not_supplied']:
        out.append('plan frames not supplied: ' + ', '.join(result['rollup']['plan_frames_not_supplied']))
    out.append(f'OVERALL: {result["rollup"]["overall"]}')
    return '\n'.join(out)


def run(job_specs, maps):
    """job_specs: [(job_dir, expected or None)]; maps: {job basename: label map path}."""
    frames = [evaluate_job(d, exp, maps.get(os.path.basename(os.path.normpath(d)))) for d, exp in job_specs]
    try:
        own = sha256_bytes(_read_file(os.path.abspath(__file__)))
    except OSError:
        own = 'unavailable'
    return {'comparator': 'compare_val.py', 'comparator_sha256': own, 'definitions': definitions(),
            'frames': frames, 'rollup': rollup(frames)}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Frozen DFT-vs-MACE force comparator for the val jobs.')
    ap.add_argument('job_dirs', nargs='*')
    ap.add_argument('--val-root')
    ap.add_argument('--label-map', action='append', default=[], metavar='JOB=PATH')
    ap.add_argument('--out')
    a = ap.parse_args(argv)
    if not a.job_dirs and not a.val_root:
        ap.error('give --val-root and/or job directories')
    maps = {}
    for s in a.label_map:
        job, _, path = s.partition('=')
        if not job or not path:
            ap.error(f'--label-map needs JOB=PATH, got {s!r}')
        maps[job] = path
    specs, seen = [], set()
    if a.val_root:
        for n, t in PLAN_FRAMES:
            d = os.path.join(a.val_root, f'{n}_{t}')
            specs.append((d, (n, t)))
            seen.add(os.path.normcase(os.path.abspath(d)))
    for d in a.job_dirs:
        key = os.path.normcase(os.path.abspath(d))
        if key not in seen:
            specs.append((d, None))
            seen.add(key)
    unknown = set(maps) - {os.path.basename(os.path.normpath(d)) for d, _ in specs}
    if unknown:
        ap.error(f'--label-map for jobs not evaluated: {sorted(unknown)}')
    try:
        result = run(specs, maps)
    except ValueError as e:
        ap.error(str(e))
    print(report_text(result))
    if a.out:
        with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(result, f, indent=1)
            f.write('\n')
    return {'PASS': 0, 'FAIL': 1, 'INCOMPLETE': 3}[result['rollup']['overall']]


if __name__ == '__main__':
    sys.exit(main())
