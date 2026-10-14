"""Command line. Run from compute/amorph:  python -m analysis <command> ...

  cell <export>      read-out of one FINAL export (a directory, or a .tar.gz such as final_results.tar.gz /
                     final_small.tar.gz; several may be given and are searched in order). Writes JSON + text report.
                     Run qualification comes ONLY from --certificate (validated here); without it the relaxation is
                     UNKNOWN, the smearing pending and the manifest unverified, so every primary score is UNRESOLVED.
  certify <export>   (DFT agent) compile an evidence-hashed certificate for one run: hashes of every consumed run file
                     (projections, planar-average inputs, lineage), geometry and pseudopotential hashes, composition
                     manifest (--spec make_specs JSON or --manifest JSON), qualification blocks with evidence.
  validate-cert <export> --certificate C   (automated gate) recompute every hash; exit 0 only for a valid certificate.
  compare <kind>     multi-cell read-outs from sealed cell JSON files of the current code:
                       c3 REF OTHER [--audit-width W] | c4 MV POLISHED | c6 SPIN_A SPIN_B REF |
                       c5 PAW NC HSE [NC_PRODUCTION_MESH] | c2 FULL DILUTED |
                       c1 MAIN P1 P2 P3 PARENT --atom-map M1 M2 M3 | attribution PAIRED PARENT --atom-map MAP |
                       pair AIWO AIO | hg S1 S2 [COMP AIO_S1 AIO_S2] | hh OH BARE | hi IFACE VAC_S1 VAC_S2 |
                       hk T07 T20_S1 T20_S2 [T10] | audit CELL:WIDTH=JSON ...   (A15; three registered cells, widths in Ry)
  series <spec.json> H-N outcome rules over the thickness series (cells and control REPORT FILES; see
                     compare.hn_outcome). Controls must be paths to .json report files; inline objects are refused.
  crystalline        reproduction of the crystalline results (3 % W-5d, Delta E_c 0.281 eV) - legacy extraction
Every class/status is printed with its unresolved checks; every output carries code, register, input and certificate
hashes and its own self-hash; time stamps and local paths are kept in a separate 'meta' block.
"""
import argparse
import json
import os
import shutil
import sys
import tarfile
import tempfile
from pathlib import PurePosixPath, PureWindowsPath

from . import certify as CERT
from . import compare as C
from . import qeio
from .data import attach_lineage, load_export
from .geometry import detect_mode
from .report import cell_result, fmt_checks, text_report, write
from .section1 import Section1


# ---------------------------------------------------------------- export discovery
def _safe_member(name):
    """Normalised member name, or None if it could leave the extraction directory (absolute, drive, '..')."""
    n = name.replace('\\', '/')
    if not n or n.startswith('/') or PureWindowsPath(n).drive or PureWindowsPath(n).is_absolute() or \
            PurePosixPath(n).is_absolute():
        return None
    parts = [x for x in n.split('/') if x not in ('', '.')]
    if not parts or any(x == '..' or ':' in x for x in parts):
        return None
    return '/'.join(parts)


def _extract(tar_path, dest, origins):
    """Regular files only, written by hand (no links, no devices, no attributes), inside dest."""
    root = os.path.realpath(dest)
    with tarfile.open(tar_path) as t:
        for m in t.getmembers():
            if not m.isfile():
                continue
            n = _safe_member(m.name)
            if n is None:
                continue
            target = os.path.realpath(os.path.join(root, *n.split('/')))
            if os.path.commonpath([root, target]) != root:
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            src = t.extractfile(m)
            if src is None:
                continue
            with src, open(target, 'wb') as f:
                shutil.copyfileobj(src, f)
            origins[os.path.normcase(target)] = f'tarball:{os.path.basename(tar_path)}::{n}'


def _dirs(paths, tmp, origins=None):
    """Search directories: given directories as they are; tarballs extracted (safe regular members only) and followed
    by the directory beside the tarball (EOS layout). Directory order wins over name order (qeio.first_existing)."""
    origins = {} if origins is None else origins
    out = []
    for p in paths:
        if os.path.isdir(p):
            out.append(p)
        elif p.endswith(('.tar.gz', '.tgz', '.tar')):
            d = tempfile.mkdtemp(dir=tmp)
            _extract(p, d, origins)
            out.append(d)
            out.append(os.path.dirname(os.path.abspath(p)))
        else:
            raise SystemExit(f'{p}: not a directory or tarball')
    return out


def _mark_origins(data, origins):
    """Record tarball members as 'tarball:<name>::<member>' (deterministic) instead of temporary paths."""
    for v in data.sources.values():
        if isinstance(v, dict) and v.get('path'):
            o = origins.get(os.path.normcase(os.path.realpath(v['path'])))
            if o:
                v['origin'] = o
                v['path'] = o


def _attach_avg(data, dirs, job):
    """The planar average and its two inputs (average.x, pp.x) from ONE directory; all consumed files are bound."""
    avg_p = qeio.first_existing(dirs, [f'{job}_avg.dat'])
    if not avg_p:
        return None
    d = os.path.dirname(avg_p)
    avg_in = qeio.first_existing([d], [f'avg_{job}.in'])
    pp_in = qeio.first_existing([d], [f'pp_{job}.in'])
    for p in (avg_p, avg_in, pp_in):
        if p:
            data.sources[os.path.basename(p)] = {'path': os.path.abspath(p), 'sha256': qeio.sha256(p)}
    return qeio.read_avg(avg_p, avg_in, pp_in)


def prepare(data, st, dirs, name, job='final', mode='auto', origins=None):
    """The shared input path of every entry point (cell, certify, validate-cert, nc_readout --xml): run lineage
    (pseudopotential provenance) and the planar-average files bound as consumed inputs, tarball origins recorded, the
    cell mode decided. Returns (avg, mode)."""
    if not any(k.startswith('lineage_') for k in data.sources):
        attach_lineage(data, dirs, job)
    avg = _attach_avg(data, dirs, job)
    _mark_origins(data, origins or {})
    geo, _ = detect_mode(st, name)
    return avg, (geo if mode == 'auto' else mode)


def read_cell(data, st, dirs, name, certificate=None, job='final', mode='auto', nex=None, w5d='normalised',
              used='xml', notes=(), meta=None, origins=None):
    """Library read-out of one run (the path of 'cell' and of every adapter): prepare(), the certificate gate,
    the manifest only from a VALID gate, Section 1 and the sealed record. Returns (record, Section1, qualification)."""
    notes = list(notes)
    avg, mode = prepare(data, st, dirs, name, job, mode, origins)
    qual = CERT.validate(certificate, name, data, st, mode=mode)
    man = qual['manifest'] if qual['manifest_verified'] and CERT.gate_valid(qual) else None
    if man is not None and nex is not None and int(nex) != int(man['N_ex']):
        raise ValueError(f'--nex {nex} contradicts the certified manifest N_ex {man["N_ex"]}')
    if nex is not None and man is None:
        notes.append(f'N_ex override {nex} (reference / legacy use; unverified)')
    c = Section1(data, st, name=name, nex=nex, mode=mode, avg=avg, w5d_convention=w5d, manifest=man)
    return cell_result(c, used, notes, qual, meta=meta), c, qual


def _load(a, tmp):
    origins = {}
    dirs = _dirs(a.export, tmp, origins)
    data, st, used, notes = load_export(dirs, a.source, a.job)
    avg, mode = prepare(data, st, dirs, a.name, a.job, getattr(a, 'mode', 'auto'), origins)
    return data, st, used, notes, avg, mode


# ---------------------------------------------------------------- commands
def cmd_cell(a):
    tmp = tempfile.mkdtemp(prefix='iwo_analysis_')
    try:
        origins = {}
        dirs = _dirs(a.export, tmp, origins)
        data, st, used, notes = load_export(dirs, a.source, a.job)
        meta = {'certificate_path': os.path.abspath(a.certificate) if a.certificate else None,
                'export_paths': [os.path.abspath(p) for p in a.export]}
        try:
            r, c, qual = read_cell(data, st, dirs, a.name, a.certificate, a.job, a.mode, a.nex, a.w5d, used, notes,
                                   meta, origins)
        except ValueError as e:
            raise SystemExit(str(e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    base = a.out or a.name
    write(r, base + '.json', base + '.txt')
    sys.stdout.write(text_report(r))
    print(f'wrote {base}.json and {base}.txt')


def cmd_certify(a):
    tmp = tempfile.mkdtemp(prefix='iwo_cert_')
    try:
        data, st, used, notes, avg, mode = _load(a, tmp)
        spec = qeio.load_json(a.spec) if a.spec else None
        man = qeio.load_json(a.manifest) if a.manifest else None
        blk = lambda s, ev, extra=None: (s, ev or [], extra) if s else None
        cert = CERT.compile_certificate(
            a.name, data, st, a.out, spec=spec, manifest=man,
            relaxation=blk(a.relaxation, a.relaxation_evidence),
            smearing=blk(a.smearing, a.smearing_evidence,
                         {'width_Ry': a.smearing_width} if a.smearing_width is not None else None),
            geometry=blk(a.geometry, a.geometry_evidence), compiled_by=a.compiled_by, notes=a.notes,
            pseudo_dir=a.pseudo_dir)
        q = CERT.validate(a.out, a.name, data, st, mode=mode)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps({'certificate': a.out, 'source': used, 'run_files': cert['run_files'],
                      'geometry_sha256': cert['geometry_sha256'], 'pseudopotentials': cert['pseudopotentials'],
                      'mode': mode, 'gate': q}, indent=1))


def cmd_validate(a):
    tmp = tempfile.mkdtemp(prefix='iwo_gate_')
    try:
        data, st, used, notes, avg, mode = _load(a, tmp)
        q = CERT.validate(a.certificate, a.name, data, st, mode=mode)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    files = {k: {'sha256': v['sha256'], 'origin': v.get('origin', 'file')} for k, v in data.sources.items()
             if isinstance(v, dict) and 'sha256' in v}
    pv = CERT.provenance_stamp(extra={'run_files': files, 'geometry_sha256': st.geometry_hash(),
                                      'certificate_sha256': q.get('certificate_sha256'), 'source': used,
                                      'mode': mode})
    print(json.dumps(dict(q, provenance=pv), indent=1))
    ok = CERT.gate_valid(q)
    print(f'GATE: {"VALID" if ok else "NOT VALID"}\n'
          f'    problems: {fmt_checks(q["problems"])}\n'
          f'    qualification checks: {fmt_checks(q["reasons"])}')
    sys.exit(0 if ok else 1)


def _norm(p):
    return os.path.normcase(os.path.normpath(os.path.abspath(p)))


def _print_result(res, out, files=()):
    """Record the input files (hashes in provenance, paths in meta), re-seal, write and print."""
    res.setdefault('provenance', CERT.provenance_stamp())
    hashes = {_norm(p): qeio.sha256(p) for p in files if os.path.isfile(p)}
    res['provenance']['input_files_sha256'] = sorted(set(hashes.values()))
    res['meta'] = dict(res.get('meta') or {}, input_files=hashes)
    res = CERT.seal(CERT.json_safe(res))
    s = json.dumps(res, indent=1, allow_nan=False)
    if out:
        with open(out, 'w', encoding='utf-8', newline='\n') as f:
            f.write(s)
    print(s)
    st = res.get('status', res.get('outcome'))
    if st is not None:
        print(f'STATUS: {st}\n    unresolved checks: {fmt_checks(res.get("unresolved_checks", []))}')


def cmd_compare(a):
    k, f = a.kind, a.files
    files = list(f)
    if k == 'audit':
        cells = {}
        files = []
        for x in f:
            cw, p = x.split('=', 1)
            cell, w = cw.split(':', 1)
            cells.setdefault(cell, {})[float(w)] = qeio.load_json(p)
            files.append(p)
        res = C.smearing_audit(cells)
    else:
        r = [qeio.load_json(x) for x in f]
        maps = [qeio.load_json(m) for m in (a.atom_map or [])]
        files += list(a.atom_map or [])
        need = {'c3': (2, 2), 'c4': (2, 2), 'c6': (3, 3), 'c5': (3, 4), 'c2': (2, 2), 'c1': (5, 5),
                'attribution': (2, 2), 'pair': (2, 2), 'hg': (2, 5), 'hh': (2, 2), 'hi': (3, 3), 'hk': (3, 4)}
        if k not in need:
            raise SystemExit(f'unknown comparison {k}')
        lo, hi = need[k]
        if not lo <= len(r) <= hi:
            raise SystemExit(f'compare {k} takes {lo}..{hi} cell files ({len(r)} given)')
        fn = {'c3': lambda: C.c3(r[0], r[1], a.audit_width),
              'c4': lambda: C.c4(*r), 'c6': lambda: C.c6(*r), 'c5': lambda: C.c5(*r), 'c2': lambda: C.c2(*r),
              'c1': lambda: C.c1(r[0], r[1:4], r[4], maps),
              'attribution': lambda: C.attribution(r[0], r[1], maps[0] if len(maps) == 1 else None),
              'pair': lambda: C.hn_pair(*r), 'hg': lambda: C.hg_score(*r), 'hh': lambda: C.hh(*r),
              'hi': lambda: C.hi(*r), 'hk': lambda: C.hk(*r)}
        res = fn[k]()
    _print_result(res, a.json, files)


def cmd_series(a):
    spec = qeio.load_json(a.spec)
    base = os.path.dirname(os.path.abspath(a.spec))
    path = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    files = [a.spec]

    def rd(p):
        files.append(path(p))
        return qeio.load_json(path(p))

    def ctrl_item(v):
        if isinstance(v, list):
            return [ctrl_item(x) for x in v]
        if isinstance(v, str) and v.endswith('.json'):
            return rd(v)
        return 'UNVERIFIED (inline control objects not accepted: give the path of a comparison report file)'
    cells = {lab: ([rd(x) for x in v] if isinstance(v, list) else rd(v)) for lab, v in spec['cells'].items()}
    ctrl = {lab: {c: ctrl_item(v) for c, v in d.items()} for lab, d in spec.get('controls', {}).items()}
    res = C.hn_outcome({'cells': cells, 'controls': ctrl})
    _print_result(res, a.json, files)


def cmd_crystalline(a):
    from .crystalline import reproduce
    res = reproduce(a.root)
    _print_result(res, a.json, [os.path.join(res['root'], k) for k in res.get('input_files', {})])
    if res['status'] != 'REPRODUCED':
        sys.exit(1)


def main(argv=None):
    ap = argparse.ArgumentParser(prog='python -m analysis', description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)

    def export_args(p):
        p.add_argument('export', nargs='+', help='export directory or tarball(s), searched in order')
        p.add_argument('--name', required=True, help='cell name, e.g. aIWO_2p0_s1')
        p.add_argument('--source', default='auto', choices=['auto', 'xml', 'table', 'text'])
        p.add_argument('--job', default='final')
        p.add_argument('--mode', default='auto', choices=['auto', 'bulk', 'slab', 'interface'])
    p = sp.add_parser('cell')
    export_args(p)
    p.add_argument('--certificate', help='run certificate (JSON); validated against the run files and geometry')
    p.add_argument('--nex', type=int, help='N_ex override for reference / legacy runs only (unverified)')
    p.add_argument('--w5d', default='normalised', choices=['normalised', 'raw'])
    p.add_argument('--out', help='output base name (default: the cell name)')
    p.set_defaults(fn=cmd_cell)
    p = sp.add_parser('certify')
    export_args(p)
    p.add_argument('--out', required=True, help='certificate path (evidence paths are stored relative to it)')
    p.add_argument('--spec', help='make_specs.py spec JSON (composition manifest)')
    p.add_argument('--manifest', help='manifest JSON (e.g. a C1 paired cell with its construction block)')
    p.add_argument('--pseudo-dir', help='directory of the UPF files (when the export has no lineage_final.dat)')
    p.add_argument('--relaxation', choices=['converged', 'exploratory'])
    p.add_argument('--relaxation-evidence', nargs='*')
    p.add_argument('--smearing', choices=['qualified'])
    p.add_argument('--smearing-width', type=float, help='certified width (Ry); must equal the run width')
    p.add_argument('--smearing-evidence', nargs='*')
    p.add_argument('--geometry', choices=['polished', 'mv'])
    p.add_argument('--geometry-evidence', nargs='*')
    p.add_argument('--compiled-by', default='')
    p.add_argument('--notes', default='')
    p.set_defaults(fn=cmd_certify)
    p = sp.add_parser('validate-cert')
    export_args(p)
    p.add_argument('--certificate', required=True)
    p.set_defaults(fn=cmd_validate)
    p = sp.add_parser('compare')
    p.add_argument('kind')
    p.add_argument('files', nargs='+')
    p.add_argument('--atom-map', nargs='+', help='C1 atom map JSON(s): three for c1, one for attribution')
    p.add_argument('--audit-width', type=float, help='c3: the A15-audit-selected width (Ry); default 0.002/0.005')
    p.add_argument('--json')
    p.set_defaults(fn=cmd_compare)
    p = sp.add_parser('series')
    p.add_argument('spec')
    p.add_argument('--json')
    p.set_defaults(fn=cmd_series)
    p = sp.add_parser('crystalline')
    p.add_argument('--root', default=None, help='IWO_PHYSICS_CONSTRAINED_MODEL_V1 directory')
    p.add_argument('--json')
    p.set_defaults(fn=cmd_crystalline)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == '__main__':
    main()
