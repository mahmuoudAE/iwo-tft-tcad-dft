"""End-to-end tests for the D-42 F9 writers (f9_writers.py) and checker (cert_assert.py), draft v20.
v20: the actual rescue / continuation authorizations of the five 2 nm audit-role chains (A43 table (1b); D-27 (2)/A25).
v19: the A15/D-26 historical transition of aIO_1p0_s1 (registered-Gaussian, five keys, rescue start False); an A15
rescue needs no A35-style qualification SCF or restart gate; D-24 failure rules and the MV history are kept.
v18: single quotes, square brackets and curly braces outside double-quoted strings are refused (Codex v17 reply).
v17: ClassAd comment delimiters outside string literals are refused in every traversed expression (Codex v16 reply).
v16: the narrow Requirements resolver (real captured CERN chain; missing/cyclic helpers UNRESOLVED; no OR/negation/
conditional/eval/TARGET evidence; case-insensitive single definitions; one ad per cluster.proc).
v15: HTCondor new-syntax argument parsing (every argument checked); unsupported submit directives refused.
v14: A43 submission binding (one scheduler DAGMan, audited executable and run directory, permitted arguments, submitted ad
and dagman.out linked to the reviewed files and the first resumed node); rescue anchor separate from the execution count;
a guard-only first execution carries the pending transition to the first actual SCF.
v13: escape-aware Requirements parsing on the audited GPU attribute; [infra] bestvalid exception disabled pending evidence;
scientific position across administrative renumbering; A43 count-enforcement files (DAG identity, config, exact RETRY,
dry run, dagman.out header).
v12: Requirements structure and unique environment values; A29 for aIO_2p0_s1; guard-only rescues keep authorization and
terminal checks; no continuation after an A35/A36 SCF failure; [infra] bestvalid exception scope and restoration record.
v11: guard-only first executions of a new attempt need the rescue record; partial splits fail; G* minimum before
deduplication; rescue files' remaining RETRY bound; historical (A15-era) rescues recorded separately; resource-route
evidence from the split segment's own cluster; A34's bestvalid rollback exception for [infra].
v10: initial DAG allowance (guard-only attempts count, evictions do not), A39 administrative rescue, pause-bound suspension
and result-informed continuation amendments, split construction (alternating map, balance, equivalence, cell and route).
v9: registered fresh starts, recomputed bestvalid, rescue authorization / budget / once-use / no revival, label-split
scope, registered FINAL template (synthetic template and authorizations registered TEST ONLY).
v8: job histories of C3 attempts, ordered segment submissions, bestvalid members, split labels, section-3
transition records and attempt<N> rescues.
v7: archive-identity records (run, cluster, k) with in-job tar mtimes, plan v2 (export root, slot runs), per-cluster
eos_dest, pre-item-B checkpoints, guard-only attempts, D-24 transition resets, export_manifest_final.dat, slot scope.
v6: relaxation segments use the real D-24 item-B archive relax_s<k>_results.tar.gz (saved relax_s<k>_input.in, the
returned relax.in replaced by the next geometry, relax.out, relax_s<k>_lineage.log); C3 attempts may carry an
artifact inventory (listing of the per-cluster export directory).

Every fixture is SYNTHETIC and starts from raw files: pw.x inputs, QE text outputs (with decoy Fermi-energy and
eigenvalue lines that the allowlist must drop), HTCondor user logs in the REAL lxplus header format
('NNN (cluster.proc.sub) MM/DD HH:MM:SS ...'; local time) with a bound offset-evidence file, export manifests in
sha256sum format, `analysis certify` stdout JSON, a frozen F10 C3 plan and rc7-shaped sealed reports.

Run:  python -I -B test_cert_assert.py   (stdlib only; the frozen-reader cross-check is skipped)
      python -E -B test_cert_assert.py   (also runs the cross-check against the frozen rc7 certify._evidence_ok)
"""
import copy
import datetime as dt
import glob
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import cert_assert as CA  # noqa: E402
import f9_common as F  # noqa: E402
import f9_writers as W  # noqa: E402

READER_PARENT = os.environ.get(
    'IWO_READER_PARENT',
    r'C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\iwo-tft-research-private\compute\amorph')


def jload(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def H(label):
    return hashlib.sha256(label.encode()).hexdigest()


SPECIES = [('In', 114.818, 'In.pbe-dn-kjpaw_psl.1.0.0.UPF'), ('W', 183.84, 'W.pbe-spn-kjpaw_psl.1.0.0.UPF'),
           ('O', 15.999, 'O.pbe-n-kjpaw_psl.1.0.0.UPF'), ('H', 1.008, 'H.pbe-kjpaw_psl.1.0.0.UPF')]
LABELS = ['In', 'W', 'O', 'H']
PPS = {f: H('upf ' + f) for _, _, f in SPECIES}
CELL = [[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 30.0]]
BASE = [[1.0, 1.0, 10.0], [3.0, 1.5, 10.5], [2.0, 2.0, 11.0], [4.0, 4.0, 12.0]]
# offset evidence captured on the submit host (CEST, valid until the end of daylight saving time)
TZ_TXT = ('utc 2026-10-12T13:00:00Z\nlocal 2026-10-12T15:00:00+0200\n'
          'valid_from 2026-03-29T01:00:00Z\nvalid_to 2026-10-25T01:00:00Z\n')
OFFSET = dt.timedelta(hours=2)
INVENTORY_SCHEMA = 'iwo-f9-attempt-inventory/1'     # v6 (f9_common.INVENTORY_SCHEMA)
EXPORT_ROOT = '/eos/user/t/test/qe/exports'          # synthetic $EXPORT_EOS (steps_final.sh.D24:28)
SEGMENT_MTIME_DEFAULT = True                          # v7: in-job tar mtimes inside the job's execution window
TRANSITION_SCHEMA = getattr(F, 'TRANSITION_SCHEMA', 'iwo-f9-transition/1')   # v9: /2 (authorization line)


def geom(k):
    g = copy.deepcopy(BASE)
    for j in range(1, k + 1):
        g[j % 4][0] = round(g[j % 4][0] + 0.011, 6)
    return g


def forces(k, scale=1.0):
    """Residual-sized forces: largest component 0.0008 * scale / (k + 1) Ry/bohr (below 1e-3 for scale <= 1)."""
    return [[round(scale * 0.0002 * (i + 1) / (k + 1), 8), round(-scale * 0.00012 * (i + 1) / (k + 1), 8),
             round(scale * 0.00005 / (k + 1), 8)] for i in range(4)]


RELAX_NL = {
    'control': {'calculation': "'relax'", 'prefix': "'run'", 'outdir': "'./out'", 'tefield': '.true.',
                'dipfield': '.true.', 'forc_conv_thr': '1.0d-3', 'etot_conv_thr': '1.0d-4'},
    'system': {'ibrav': '0', 'nat': '4', 'ntyp': '4', 'ecutwfc': '60', 'ecutrho': '480', 'occupations': "'smearing'",
               'smearing': "'mv'", 'degauss': '0.01', 'nspin': '1', 'edir': '3', 'emaxpos': '0.95', 'eopreg': '0.04'},
    'electrons': {'conv_thr': '1.0d-7', 'mixing_beta': '0.2', 'electron_maxstep': '200'},
    'ions': {'ion_dynamics': "'bfgs'"}}


def nl(base=RELAX_NL, **over):
    d = copy.deepcopy(base)
    for k, v in over.items():
        n, key = k.split('__')
        if v is None:
            d[n].pop(key, None)
        else:
            d[n][key] = v
    return d


POLISH_NL = nl(system__smearing="'gaussian'", system__degauss='0.005')
GAUSS_NL = POLISH_NL
AIDS = dict(electrons__mixing_beta='0.1', electrons__mixing_ndim='12', electrons__electron_maxstep='300')
FINAL_NL = nl(control__calculation="'scf'", control__forc_conv_thr=None, control__etot_conv_thr=None,
              system__ecutwfc='71', system__ecutrho='568', system__smearing="'gaussian'", system__degauss='0.001',
              system__nbnd='40', electrons__conv_thr='1.0d-8', electrons__mixing_beta='0.1')


def run_files(tag):
    return {'data-file-schema.xml': H(tag + ' xml'), 'atomic_proj.xml': H(tag + ' proj'),
            'projwfc_final.out': H(tag + ' projwfc'), 'final_avg.dat': H(tag + ' avg'),
            'lineage_final.dat': H(tag + ' lineage')}


def entry(cell, files, cert_sha, geometry, width):
    return {'cell': cell, 'kind': 'W-doped', 'schema': F.CELL_SCHEMA, 'result_sha256': H(cell + str(width)),
            'self_sha256': H('self' + cell + str(width)), 'geometry_sha256': geometry, 'certificate_sha256': cert_sha,
            'run_files': dict(files, **{'_internal': None}), 'smearing': 'gaussian', 'degauss_Ry': width, 'nspin': 1,
            'mode': 'slab', 'code_sha256': F.RC7_CODE_SHA256}


class World:
    """Synthetic raw files laid out like the real exports:
      * relaxation segments: 'relax_s<k>_results.tar.gz' holding relax_s<k>_input.in, relax.in (the next geometry),
        relax.out and relax_s<k>_lineage.log (v6); qualification jobs: '<job>_results.tar.gz' holding scf.in/scf.out;
        both listed in a P0 sha256sum record of the ARCHIVE (members are recomputed from the archive);
      * FINAL-type runs: a D-24 exp/ directory (steps_final.sh.D24:202-233) with final_small.tar.gz (scf.in,
        lineage_final.dat with its 'scf.in as-run' line, final_avg.dat), gzipped run files and the in-job MANIFEST
        ('# run <name> cluster <N> written_utc <t>' + '<basename> <bytes> <sha256>' lines)."""

    def __init__(self, root, edits=None, log_fmt='condor'):
        self.root = root
        self.raw = os.path.join(root, 'raw')
        self.ev = os.path.join(root, 'ev')
        os.makedirs(self.raw, exist_ok=True)
        os.makedirs(self.ev, exist_ok=True)
        self.p, self.runs = {}, {}
        self.edits = edits or {}
        self.log_fmt = log_fmt
        self.tz = self.write('tz.txt', TZ_TXT)

    def write(self, name, text):
        path = os.path.join(self.raw, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        self.p[name] = path
        return path

    def pw_in(self, name, nlv, pos, labels=None):
        lines = []
        for n in ('control', 'system', 'electrons', 'ions'):
            lines.append('&' + n.upper())
            lines += [f'  {k} = {v}' for k, v in nlv[n].items()]
            lines.append('/')
        lines.append('ATOMIC_SPECIES')
        lab = labels or LABELS                         # v8: split labels (A25) relabel atoms, same element and UPF
        sp = SPECIES if labels is None else [(lab[i], m, f) for i, (_, m, f) in enumerate(SPECIES)]
        lines += [f'{l} {m} {f}' for l, m, f in sp]
        lines.append('CELL_PARAMETERS angstrom')
        lines += [' '.join(f'{x:.6f}' for x in v) for v in CELL]
        lines.append('ATOMIC_POSITIONS angstrom')
        lines += [f'{l} {x:.6f} {y:.6f} {z:.6f}' for l, (x, y, z) in zip(lab, pos)]
        lines += ['K_POINTS automatic', '2 2 1 0 0 0', '']
        return self.write(name, '\n'.join(lines))

    def qe_out(self, name, evals, final=None, scf_fail=False, rows=None, labels=None):
        lab = labels or LABELS
        L = ['     Program PWSCF v.7.5 starts on 14Oct2026 at  3: 0: 0 ', '']
        for k, (pos, fr, fo) in enumerate(evals):
            if pos is not None:
                L += ['ATOMIC_POSITIONS (angstrom)'] + [f'{l}  {x:14.10f}  {y:14.10f}  {z:14.10f}'
                                                        for l, (x, y, z) in zip(lab, pos)] + ['']
            L += ['          k = 0.0000 0.0000 0.0000 (  1234 PWs)   bands (ev):', '',
                  '   -5.1234  -4.3210   1.2345   2.3456   3.4567', '',
                  '     the Fermi energy is     5.4321 ev', '',
                  '     convergence has been achieved in  12 iterations', '',
                  f'!    total energy              = {fr:18.8f} Ry', '     smearing contrib. (-TS)   =      -0.00012345 Ry',
                  '', '     Forces acting on atoms (cartesian axes, Ry/au):', '']
            ids = rows or [(i + 1, i + 1) for i in range(len(fo))]
            L += [f'     atom {a:4d} type {t:2d}   force = {x:14.8f}{y:14.8f}{z:14.8f}'
                  for (a, t), (x, y, z) in zip(ids, fo)]
            L += ['', '     Total force =     0.012345     Total SCF correction =     0.000123', '']
        if scf_fail:
            L += ['     convergence NOT achieved after 300 iterations: stopping', '']
        if final is not None:
            L += ['     bfgs converged in   5 scf cycles and   4 bfgs steps', '',
                  '     End of BFGS Geometry Optimization', '', 'Begin final coordinates', '',
                  'ATOMIC_POSITIONS (angstrom)'] + [f'{l}  {x:14.10f}  {y:14.10f}  {z:14.10f}'
                                                    for l, (x, y, z) in zip(lab, final)] + \
                 ['End final coordinates', '']
        L += ['     JOB DONE.', '']
        return self.write(name, '\n'.join(L))

    def joblog(self, name, jobs):
        """jobs: [(cluster, submit_utc, end_utc or None[, end])]; end = exit code (default 0), 'signal<N>', 'abort' or
        'hold_abort' (held, then removed). Written in the real lxplus header format (local time) unless log_fmt == 'iso'."""
        ev = []
        for j in jobs:
            cl, sub, term = j[:3]
            end = j[3] if len(j) > 3 else 0
            ev.append((F.parse_utc(sub), '000', cl, 'Job submitted from host: <10.0.0.1:9618>'))
            ev.append((F.parse_utc(sub) + dt.timedelta(minutes=5), '001', cl, 'Job executing on host: <10.0.0.2:9618>'))
            if term:
                if len(j) > 4 and j[4] == 'evict':           # v10: eviction + re-execution inside the same cluster
                    ev.append((F.parse_utc(sub) + dt.timedelta(hours=1), '004', cl, 'Job was evicted.'))
                    ev.append((F.parse_utc(sub) + dt.timedelta(hours=1, minutes=10), '001', cl,
                               'Job executing on host: <10.0.0.3:9618>'))
                if end == 'hold_abort':
                    ev.append((F.parse_utc(term) - dt.timedelta(hours=1), '012', cl,
                               'Job was held.\n\tsynthetic hold reason\n\tCode 21 Subcode 0'))
                    ev.append((F.parse_utc(term), '009', cl, 'Job was aborted.\n\tvia condor_rm (by user test)'))
                elif end == 'abort':
                    ev.append((F.parse_utc(term), '009', cl, 'Job was aborted.\n\tvia condor_rm (by user test)'))
                elif isinstance(end, str) and end.startswith('signal'):
                    ev.append((F.parse_utc(term), '005', cl, f'Job terminated.\n\t(0) Abnormal termination (signal {end[6:]})'))
                else:
                    ev.append((F.parse_utc(term), '005', cl, f'Job terminated.\n\t(1) Normal termination (return value {end})'))
        ev.sort(key=lambda e: e[0])
        L = []
        for t, code, cl, text in ev:
            stamp = ((t + OFFSET).strftime('%m/%d %H:%M:%S') if self.log_fmt == 'condor'
                     else t.strftime('%Y-%m-%d %H:%M:%S') + 'Z')
            L += [f'{code} ({cl}.000.000) {stamp} {text}', '...']
        return self.write(name, '\n'.join(L) + '\n')

    def tarball(self, name, members, mtime=None):
        """mtime (UTC 'YYYY-MM-DDTHH:MM:SSZ'): the member mtimes as tar records them in-job (v7 window check)."""
        path = os.path.join(self.raw, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with tarfile.open(path, 'w:gz') as t:
            for mname, p in members.items():
                if mtime is None:
                    t.add(p, arcname=mname)
                    continue
                ti = t.gettarinfo(p, arcname=mname)
                ti.mtime = int(F.parse_utc(mtime).timestamp())
                with open(p, 'rb') as fh:
                    t.addfile(ti, fh)
        self.p[name] = path
        return path

    def archive_record(self, name, archives, run='run', cluster=0, k=None, idents=None):
        """v7: the archive-identity record of returned ARCHIVES (f9_common._read_identity): the run, then one line
        '<basename> <bytes> <sha256> cluster <N> [k <k>]' per archive; idents {basename: (cluster, k)} overrides."""
        L = ['# iwo-f9-archive-identity/1', f'# run {run}']
        for a in archives:
            cl, kk = (idents or {}).get(os.path.basename(a), (cluster, k))
            L.append(f'{os.path.basename(a)} {os.path.getsize(a)} {F.sha256_file(a)} cluster {cl}'
                     + (f' k {kk}' if kk is not None else ''))
        return self.write(name, '\n'.join(L) + '\n')

    def sha256sum_record(self, name, archives):
        """The v6 P0 sha256sum record (no run or cluster identity): refused for returned archives in v7."""
        return self.write(name, ''.join(f'{F.sha256_file(a)}  {os.path.basename(a)}\n' for a in archives))

    def certify_out(self, name, rf, final_in):
        g = F.input_geometry_hash(F.read_pw_input(final_in))
        return self.write(name, json.dumps({'certificate': 'cert.json', 'source': 'xml', 'run_files': rf,
                                            'geometry_sha256': g, 'pseudopotentials': PPS, 'mode': 'slab',
                                            'gate': {'problems': []}}))

    def sealed(self, name, obj):
        obj = dict(obj)
        obj['self_sha256'] = F.canonical_sha256(obj)
        return self.write(name, json.dumps(obj))

    def relax_archive(self, d, k, saved_in, out, returned, status, job_name=None, saved=True, extra=None, mtime=None,
                      bestvalid=None):
        """v6: the D-24 segment archive relax_s<k>_results.tar.gz (relax_node.sh:47-48) as steps_relax.sh packs it:
        relax_s<k>_input.in (the as-run input, :19-20), relax.in (REPLACED by the next / final geometry, :30/:35),
        relax.out and relax_s<k>_lineage.log ('segment relax_s<k>: <STATUS>', :51-56)."""
        job = f'relax_s{k}'
        lg = self.write(f'{d}/{job}_lineage.log', f'segment {job_name or job}: {status}\ngeomsel: synthetic\n'
                                                  f'geomsel.py md5 {"0" * 32}\npositions md5: input x  next relax.in y\n')
        members = {'relax.in': returned, 'relax.out': out, f'{job}_lineage.log': lg}
        if saved:
            members[f'{job}_input.in'] = saved_in
        if bestvalid:                                       # steps_relax.sh:48 on FAILED (README_D24_BD.txt:62)
            members[f'{job}_bestvalid.in'] = bestvalid
        members.update(extra or {})
        return self.tarball(f'{d}/returned/{job}_results.tar.gz', members, mtime=mtime)

    def segment(self, tag, seg, cluster, nlv, pos, evals, final=None, term='2026-10-12T08:00:00Z', scf_fail=False,
                k=None, job_name=None, saved=True, returned=None, status=None, archive_mtime=None,
                sub=None, layout='item_b', ckpt_cluster=None, ckpt_out=None, labels=None, bestvalid=None,
                attempt=None, evict=False):
        """v6: real D-24 item-B layout. k defaults to the segment's index (JOB relax_s<k>); the returned relax.in is
        the next geometry (CONTINUE: last validated one; CONVERGED: final coordinates; FAILED: unchanged).
        v7: returned / status override the selection (e.g. an old-rule continuation after an SCF failure);
        archive_mtime sets the in-job member mtimes (default: 2 min before the job's termination); sub is the submit
        time; layout 'pre_item_b' writes the pre-D-24 archive (relax.in, relax.out, relax_s<k>_driver.log) plus the
        EOS checkpoint relax_s<k>_ckpt_<cluster>.tar.gz (as-run relax.in, relax.out; lineage_relax.sh.D24:8-9, 161).
        v8: sub defaults to 6 h before the termination (segments run in order); labels gives split labels; bestvalid
        (a geometry) adds relax_s<k>_bestvalid.in; attempt N > 1 marks a section-3 rescue attempt (attempt<N>/)."""
        d = f'{tag}_{seg}' if not attempt or attempt == 1 else f'{tag}_a{attempt}_{seg}'
        k = F.segment_index(seg)[1] if k is None else k
        sub = sub or (F.fmt_utc(F.parse_utc(term) - dt.timedelta(hours=6)) if term else '2026-10-10T00:00:00Z')
        i = self.pw_in(f'{d}/relax_s{k}_input.in', nlv, pos, labels)
        o = self.qe_out(f'{d}/relax.out', evals, final=final, scf_fail=scf_fail, labels=labels)
        status = status or ('FAILED' if scf_fail else ('CONVERGED' if final is not None else 'CONTINUE'))
        nxt = returned or (pos if status.startswith('FAILED') else
                           (final if final is not None else next((e[0] for e in reversed(evals) if e[0] is not None),
                                                                 pos)))
        r = self.pw_in(f'{d}/returned/relax.in', nlv, nxt, labels)
        bv = self.pw_in(f'{d}/relax_s{k}_bestvalid.in', nlv, bestvalid, labels) if bestvalid else None
        lg = self.joblog(f'{d}/relax.log', [(cluster, sub, term, 0, 'evict') if evict else (cluster, sub, term)])
        if archive_mtime is None and term and SEGMENT_MTIME_DEFAULT:
            archive_mtime = F.fmt_utc(F.parse_utc(term) - dt.timedelta(minutes=2))
        if layout == 'pre_item_b':
            drv = self.write(f'{d}/relax_s{k}_driver.log', f'[{term}] relax status: {status}; synthetic old rule\n')
            tar = self.tarball(f'{d}/returned/relax_s{k}_results.tar.gz',
                               {'relax.in': r, 'relax.out': o, f'relax_s{k}_driver.log': drv}, mtime=archive_mtime)
            ckc = cluster if ckpt_cluster is None else ckpt_cluster
            ck = self.tarball(f'{d}/eos/relax_s{k}_ckpt_{ckc}.tar.gz',
                              {'relax.in': i, 'relax.out': ckpt_out or o}, mtime=archive_mtime)
            arcs, idents = [tar, ck], {os.path.basename(ck): (ckc, k)}
        else:
            arcs, idents = [self.relax_archive(d, k, i, o, r, status, job_name, saved, mtime=archive_mtime,
                                               bestvalid=bv)], None
        out = {'segment': seg, 'cluster': cluster, 'relax_in': i, 'relax_out': o, 'joblog': lg,
               'export_manifest': self.archive_record(f'{d}/p0_archives.id', arcs, tag, cluster, k, idents),
               'archives': arcs}
        if attempt:
            out['attempt'] = attempt
        return out

    def guard_segment(self, tag, seg, cluster, nlv, pos, term, sub=None, attempt=None):
        """v7: a guard-only attempt (relax_node.sh:19-34): stopped before pw.x, relax.in packed unchanged."""
        d = f'{tag}_{seg}' if not attempt or attempt == 1 else f'{tag}_a{attempt}_{seg}'
        sub = sub or F.fmt_utc(F.parse_utc(term) - dt.timedelta(minutes=30))
        k = F.segment_index(seg)[1]
        r = self.pw_in(f'{d}/returned/relax.in', nlv, pos)
        drv = self.write(f'{d}/relax_s{k}_driver.log', f'[{term}] relax status: FAILED (stopped before pw.x on node7); '
                                                       'segment_guard: FAILED synthetic [scf]\n')
        tar = self.tarball(f'{d}/returned/relax_s{k}_results.tar.gz', {f'relax_s{k}_driver.log': drv, 'relax.in': r},
                           mtime=F.fmt_utc(F.parse_utc(term) - dt.timedelta(minutes=1)))
        out = {'segment': seg, 'cluster': cluster, 'joblog': self.joblog(f'{d}/relax.log', [(cluster, sub, term, 1)]),
               'export_manifest': self.archive_record(f'{d}/p0_archives.id', [tar], tag, cluster, k),
               'archives': [tar]}
        if attempt:
            out['attempt'] = attempt
        return out

    def job_history(self, name, cluster, run, sub):
        """v8: condor_history -l <cluster> (the keys F9 reads, among others)."""
        q = int(F.parse_utc(sub).timestamp())
        return self.write(name, f'Owner = "test"\nClusterId = {cluster}\nProcId = 0\nIWOJob = "{run}_final"\n'
                                f'QDate = {q}\nJobStatus = 4\n')

    def rollback_record(self, name, run, after, logged, restored='original-route'):
        """v12: the restoration record of the A34 / D-37 [infra] bestvalid exception (ROLLBACK.txt step applied before the
        release; README section 3 reset logged)."""
        return self.write(name, f'# iwo-f9-rollback/1\n# run {run} after {after} restored {restored} logged_utc {logged}\n')

    A43_RUN_ROOT = '/afs/cern.ch/user/m/melrashe/iwo_amorph/runs'
    A43_DAGMAN_EXE = '/usr/bin/condor_dagman'

    def a43_dag_set(self, tag, retry, extra_line=None, config_text=None, dag_in_sub=None, rescue_from=0, node_cluster=80,
                    dagman_cluster=9000, queue='queue', executable=None, initialdir=None, extra_args='', ad=None,
                    submit_cluster=None, dagman_setting='False', dagman_retry_of=None, dagman_node=None, dagman=None, omit=(),
                    args_override=None, extra_sub_lines=()):
        """v13/v14: the A43 count-enforcement files of a chain: the original DAG, the A43 DAG (= original except RETRY RELAX and
        one CONFIG line), the DAG config, the -no_submit dry-run .condor.sub (scheduler universe, audited executable, run
        directory, permitted arguments, one queue), the submit record, the submitted DAGMan ad and the A43 dagman.out
        (header with the DAGMan cluster, the False setting, the first resumed RELAX node and the retry count)."""
        orig = ['JOB RELAX relax.sub', 'VARS RELAX seg="$(RETRY)"', 'RETRY RELAX 8', 'JOB FINAL final.sub', 'RETRY FINAL 1',
                'PARENT RELAX CHILD FINAL']
        a43 = ['CONFIG a43_dagman.config'] + [('RETRY RELAX %d' % retry) if l == 'RETRY RELAX 8' else l for l in orig]
        if extra_line:
            a43.append(extra_line)
        out = {'original_dag': self.write(f'{tag}/{tag}.dag', '\n'.join(orig) + '\n'),
               'dag_config': self.write(f'{tag}/a43_dagman.config', config_text or 'DAGMAN_RESET_RETRIES_UPON_RESCUE = False\n'),
               'rescue_file': self.write(f'{tag}/{tag}.a43.dag', '\n'.join(a43) + '\n')}
        d = dag_in_sub or f'{tag}.a43.dag'
        exe = executable or self.A43_DAGMAN_EXE
        args = (f"-p 0 -f -l . -Lockfile {d}.lock -AutoRescue 1 -DoRescueFrom {rescue_from} -Dag {d} -Suppress_notification "
                f"-CsdVersion $CondorVersion:' '23.0.12' '2024-06-13' 'BuildID:' '739441' '$ -Dagman {self.A43_DAGMAN_EXE}{extra_args}")
        args = args_override or args                                            # v15: hand-written argument strings
        sub = ['# Filename: ' + d + '.condor.sub', 'universe\t= scheduler', f'executable\t= {exe}',
               f'output\t\t= {d}.lib.out', f'error\t\t= {d}.lib.err', f'log\t\t= {d}.dagman.log', 'remove_kill_sig\t= SIGUSR1',
               'copy_to_spool\t= False', f'arguments\t= "{args}"']
        if initialdir:
            sub.append(f'initialdir\t= {initialdir}')
        sub += list(extra_sub_lines)                                            # v15: directives before queue
        sub.append(queue)
        out['dry_run_sub'] = self.write(f'{tag}/{tag}.a43.dag.condor.sub', '\n'.join(sub) + '\n')
        out['submit_record'] = self.write(f'{tag}/submit_a43.txt', f'Submitting job(s).\n1 job(s) submitted to cluster '
                                                                    f'{submit_cluster or dagman_cluster}.\n')
        a = {'ClusterId': str(dagman_cluster), 'ProcId': '0', 'JobUniverse': '7', 'Cmd': f'"{exe}"',
             'Iwd': f'"{self.A43_RUN_ROOT}/{tag}"', 'Arguments': f'"{args}"', **(ad or {})}
        out['dagman_ad'] = self.write(f'{tag}/dagman_ad_{dagman_cluster}.txt', ''.join(f'{k} = {v}\n' for k, v in a.items()))
        if dagman is None:
            dagman = (f'10/15/26 08:00:00 ** condor_scheduniv_exec.{dagman_cluster}.0 (CONDOR_DAGMAN) STARTING UP\n'
                      f'10/15/26 08:00:00 DAGMAN_RESET_RETRIES_UPON_RESCUE setting: {dagman_setting}\n'
                      f'10/15/26 08:00:05 Event: ULOG_SUBMIT for HTCondor Node RELAX ({dagman_node or node_cluster}.0.0) '
                      '{10/15/26 08:00:01}\n')
            if dagman_retry_of is not None:
                dagman += f'10/15/26 09:00:00 Retrying node RELAX (retry #1 of {dagman_retry_of})...\n'
        out['dagman_out'] = self.write(f'{tag}/{tag}.a43.dag.dagman.out', dagman)
        for k in omit:
            out.pop(k, None)
        return out

    def rescue_file(self, name, retry):
        """v11: the DAG rescue file (<name>.dag.rescueNNN) with the RELAX node's remaining RETRY (written with
        DAGMAN_RESET_RETRIES_UPON_RESCUE = False)."""
        return self.write(name, f'# Rescue DAG file, created after running\n#   the dag file\nDONE PREP\nRETRY RELAX {retry}\n')

    def resource_history(self, name, cluster, gpus=1, requirements=None, environment=None, helpers=None, extra=''):
        """v11: condor_history -l of the segment's own cluster (request, Requirements, environment; A29/A30 route).
        v16: helper definitions (default: the PreVerRequirements the default Requirements names) and extra ad lines."""
        req = requirements or ('(PreVerRequirements) && regexp("H100", TARGET.GPUs_DeviceName) && '
                               '!regexp("MIG", TARGET.GPUs_DeviceName)')       # v13: the audited GPU attribute
        env = environment or 'HOME=/afs/cern.ch/user/t/test QE_NK=1 NV_ACC_MEM_MANAGE=0'
        hl = helpers if helpers is not None else {'PreVerRequirements': '(TARGET.Arch == "X86_64")'}
        return self.write(name, f'ClusterId = {cluster}\nProcId = 0\nRequestGpus = {gpus}\nRequestCpus = 27\n'
                                f'RequestMemory = 81000\nRequirements = {req}\nEnvironment = "{env}"\n'
                                + ''.join(f'{k} = {v}\n' for k, v in hl.items()) + extra)

    def transition_record(self, name, run, kind, after, attempt, logged, moved=(), auth=None, schema=None):
        """v8: a section-3 reset / rescue record (README_D24_BD.txt section 3; moved = the archives in attempt<N>/).
        v9: auth = (ref, remaining_before, remaining_after, prior_rescues, terminal_failure) adds the rescue
        authorization and budget line (Codex v8 item 3)."""
        L = [f'# {schema or TRANSITION_SCHEMA}', f'# run {run} kind {kind} after {after} attempt {attempt} logged_utc {logged}']
        if auth is not None:
            L.append('# authorization {} remaining_before {} remaining_after {} prior_rescues {} terminal_failure {}'.format(*auth))
        L += [f'moved {os.path.basename(a)} {os.path.getsize(a)} {F.sha256_file(a)}' for a in moved]
        L.append(f'# end moved {len(moved)}')
        return self.write(name, '\n'.join(L) + '\n')

    def final(self, tag, nlv, pos, cluster=700, written='2026-10-15T23:59:00Z', asrun=True, unused_fresh=None,
              manifest='MANIFEST', statuses=None):
        scf = self.pw_in(f'{tag}/scf.in', nlv, pos)
        lines = [f'sha256 {PPS[f]} pseudo/{f}' for _, _, f in SPECIES] + ['geometry_check PASS']
        if asrun:
            lines.append(f'sha256 {F.sha256_file(scf)} scf.in as-run (max_seconds = 240000; identical to the pre-run '
                         'scf.in apart from max_seconds: yes)')
        lin = self.write(f'{tag}/lineage_final.dat', '\n'.join(lines) + '\n')
        avg = self.write(f'{tag}/final_avg.dat', f'synthetic planar average {tag}\n')
        members = {'scf.in': scf, 'lineage_final.dat': lin, 'final_avg.dat': avg}
        if unused_fresh:
            members['scf_fresh.in'] = unused_fresh
        tar = self.tarball(f'{tag}/exp/final_small.tar.gz', members)
        gz = {}
        for n in ('data-file-schema.xml', 'atomic_proj.xml', 'projwfc_final.out'):
            gp = os.path.join(self.raw, tag, 'exp', n + '.gz')
            with open(gp, 'wb') as fh, gzip.GzipFile(filename='', mode='wb', fileobj=fh, mtime=0) as gzf:
                gzf.write(f'synthetic {tag} {n}\n'.encode())
            gz[n + '.gz'] = gp
        dest = f'{EXPORT_ROOT}/{tag}/final_{cluster}'                       # steps_final.sh.D24:65, :227
        exp = [tar] + list(gz.values())
        if manifest == 'MANIFEST':
            ml = [f'# eos_dest {dest}', f'# run {tag} cluster {cluster} written_utc {written}']
            ml += [f'{os.path.basename(p)} {os.path.getsize(p)} {F.sha256_file(p)}' for p in exp]
            man = self.write(f'{tag}/exp/MANIFEST', '\n'.join(ml) + '\n')
        else:                                                               # v7: export_manifest_final.dat (:257-270)
            st = statuses or {}
            ml = ['# export complete: 4 files on EOS, projection checks passed',
                  f'# D-24 export of {tag} (cluster {cluster}), {written}; EOS directory {dest}',
                  '# status: XRD_ADLER32 / XRD_SIZE / FUSE_SIZE = copied in-job; PULLED = copied by export_pull.sh',
                  '# EOS write probe at job start: OK', '# file bytes sha256 status']
            ml += [f'{os.path.basename(p)} {os.path.getsize(p)} {F.sha256_file(p)} '
                   f'{st.get(os.path.basename(p), "XRD_ADLER32")}' for p in exp]
            man = self.write(f'{tag}/export_manifest_final.dat', '\n'.join(ml) + '\n')
        rf = {n: F.sha256_file(p) for n, p in gz.items()}
        rf.update({'lineage_final.dat': F.sha256_file(lin), 'final_avg.dat': F.sha256_file(avg)})
        run = {'in': scf, 'lineage': lin, 'co': self.certify_out(f'{tag}/certify.json', rf, scf), 'man': man,
               'archives': [tar], 'rf': rf, 'g': F.input_geometry_hash(F.read_pw_input(scf)), 'cluster': cluster,
               'exp': [tar] + list(gz.values())}
        self.runs[tag] = run
        return run

    def inventory(self, name, run, cluster, files=(), state='exists', captured='2026-10-16T06:00:00Z',
                  loc_cluster=None, end=True, extra_line=None, location=None):
        """v6: an attempt's artifact inventory: the listing of its per-cluster export directory
        $EXPORT_EOS/<name>/final_<ClusterId>/ (steps_final.sh.D24:65), captured after the job's terminal event."""
        loc = location or f'{EXPORT_ROOT}/{run}/final_{cluster if loc_cluster is None else loc_cluster}'
        L = [f'# {INVENTORY_SCHEMA}', f'# run {run} cluster {cluster} captured_utc {captured}',
             f'# location {loc} {state}']
        L += [f'{os.path.basename(p)} {os.path.getsize(p)} {F.sha256_file(p)}' for p in files]
        if extra_line:
            L.append(extra_line)
        if end:
            L.append(f'# end files {len(files)}')
        return self.write(name, '\n'.join(L) + '\n')

    def attempt_inventory(self, key, kind, run, cluster, exp_files=()):
        """Inventory variants for one attempt (key e.g. '005b'): probe_only, absent, export and unverifiable ones."""
        probe = self.write(f'inv/{key}/eos_probe_start.txt', f'D-24 EOS write probe: {run} cluster {cluster}\n')
        name = f'inv/{key}/inventory.txt'
        if kind == 'probe_only':
            return self.inventory(name, run, cluster, [probe])
        if kind == 'absent':
            return self.inventory(name, run, cluster, [], state='absent')
        if kind == 'export':
            return self.inventory(name, run, cluster, [probe] + list(exp_files))
        if kind == 'other_cluster':
            return self.inventory(name, run, cluster + 1000, [probe])
        if kind == 'other_location':
            return self.inventory(name, run, cluster, [probe], loc_cluster=cluster + 1000)
        if kind == 'early':
            return self.inventory(name, run, cluster, [probe], captured='2026-10-15T12:00:00Z')
        if kind == 'truncated':
            return self.inventory(name, run, cluster, [probe], end=False)
        if kind == 'malformed':
            return self.inventory(name, run, cluster, [probe], extra_line='free text is not an inventory line')
        if kind == 'wrong_root':           # Codex v6 review item 1: another cell's directory, same final_<cluster>
            return self.inventory(name, 'OTHER_CELL', cluster, [], state='absent',
                                  location=f'/WRONG_ROOT/OTHER_CELL/final_{cluster}')
        if kind == 'other_run':            # the right root, but another run's directory
            return self.inventory(name, 'OTHER_CELL', cluster, [], state='absent')
        if kind == 'other_root':           # the right run name under another root
            return self.inventory(name, run, cluster, [], state='absent',
                                  location=f'/WRONG_ROOT/{run}/final_{cluster}')
        if kind.startswith('run='):        # a run name the plan gives to another slot (ambiguous ownership)
            return self.inventory(name, kind[4:], cluster, [], state='absent')
        raise ValueError(kind)

    @staticmethod
    def fsrc(run, pre=''):
        key_in = {'': 'final_in', 'ref_': 'ref_in', 'comp_': 'comp_in'}[pre]
        return {key_in: run['in'], pre + 'lineage_file': run['lineage'], pre + 'certify_output': run['co'],
                pre + 'export_manifest': run['man'], pre + 'archives': run['archives']}

    def rec(self, name, rtype, params, sources):
        path = os.path.join(self.ev, name + '.json')
        W.build_record(rtype, params, sources, path)
        if name in self.edits:
            with open(path, encoding='utf-8') as f:
                r = json.load(f)
            self.edits[name](r)
            if getattr(self.edits[name], 'rederive', False):      # v7: a consistent forgery (writer output)
                r['derived'] = W.derive(r['type'], r['params'], W.resolve(r['sources'], self.ev))
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(r, f, indent=1)
        self.p[name] = path
        return path

    def cert(self, name, cell, rf, geometry, blocks):
        def block(spec):
            b = {'status': spec[0], 'evidence': [{'file': os.path.relpath(self.p[n], self.root).replace(os.sep, '/'),
                                                  'sha256': F.sha256_file(self.p[n])} for n in spec[1]]}
            if len(spec) > 2:
                b['width_Ry'] = spec[2]
            return b
        c = {'schema': F.CERT_SCHEMA, 'cell': cell, 'run_files': rf, 'geometry_sha256': geometry,
             'pseudopotentials': PPS,
             'manifest': {'kind': 'W-doped', 'film': {'In': 49, 'W': 1, 'O': 84}, 'substrate': {},
                          'passivation': 'dissociated-water', 'N_ex': 1, 'seed': 201, 'spec_name': cell},
             'relaxation': block(blocks['relaxation']) if 'relaxation' in blocks else {'status': 'unknown'},
             'smearing': block(blocks['smearing']) if 'smearing' in blocks else {'status': 'pending'},
             'geometry': block(blocks['geometry']) if 'geometry' in blocks else {'status': 'unknown'},
             'compiled_by': 'test', 'notes': '', 'code_version': '1.0.0-rc7', 'code_sha256': F.RC7_CODE_SHA256,
             'register_sha256': H('register')}
        path = os.path.join(self.root, name + '.json')
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(c, f, indent=1)
        self.p[name] = path
        return path

    def role_lineage(self, cell, term='2026-10-15T00:00:00Z'):
        s = self.segment(cell, 's0', 900 + len(self.p), GAUSS_NL, geom(0),
                         [(None, -50.0, forces(0)), (geom(1), -50.00005, forces(1))], final=geom(1), term=term)
        return self.rec('lin_' + cell, 'relaxation_lineage', {'cell': cell, 'route': 'registered-Gaussian'},
                        {'segments': [s], 'offset_evidence': self.tz})

    def qualification(self, name, cell, cluster, nlv, pos, F_Ry, fo, lineage, term):
        qin = self.pw_in(f'{name}/scf.in', nlv, pos)
        qout = self.qe_out(f'{name}/scf.out', [(None, F_Ry, fo)])
        lg = self.joblog(f'{name}/scf.log', [(cluster, '2026-10-12T00:00:00Z', term)])
        tar = self.tarball(f'{name}/returned/{name}_results.tar.gz', {'scf.in': qin, 'scf.out': qout},
                           mtime=F.fmt_utc(F.parse_utc(term) - dt.timedelta(minutes=2)))
        return self.rec(name, 'qualification_scf', {'cell': cell, 'cluster': cluster},
                        {'scf_in': qin, 'scf_out': qout, 'joblog': lg, 'lineage': lineage, 'offset_evidence': self.tz,
                         'export_manifest': self.archive_record(f'{name}/p0_archives.id', [tar], name, cluster),
                         'archives': [tar]})


def polished_world(root, cell='aIWO_0p7_s1', zero_step=False, qual_dF=2e-6, qual_dforce=1e-4,
                   polish_term='2026-10-14T03:00:00Z', qual_term='2026-10-14T09:00:00Z', mv_term='2026-10-12T08:00:00Z',
                   c3_status=None, comp_start=None, width=0.001, candidate=0.005, polish_nl=None, mv_s1_nl=None,
                   edits=None, qual_fresh=True, polish_last_max=None, role_terms=None, extra_seeded=None,
                   drop_reports=(), drop_attempts=(), log_fmt='condor', tamper_report=None, ref_seeded=False,
                   hide_output=(), extra_noout=None, late_manifest=None, att_end=None, inventories=None,
                   omit_keys=None, foreign_slot=False, plan_runs_dup=False, comp_manifest='MANIFEST', extra_runs=None,
                   hist_sub=None, final_nl=None):
    """MV parent (s0, s1) -> certified MV FINAL -> C4 polish p0 (+ fresh qualification) -> polished FINAL at 0.001 Ry
    and companions 0.002 / 0.005 in frozen-plan slots, A15 audit with derived roles, certificates v1 and v2.
    v6: att_end {attempt: end} sets an attempt's terminal event (exit code, 'signal<N>', 'abort', 'hold_abort');
    inventories {attempt: kind} binds an artifact inventory (World.attempt_inventory); omit_keys {attempt: keys} drops
    evidence keys. Attempts are '<width tag><suffix>' (e.g. '005b'); the extra no-output attempt is '005n'."""
    att_end, inventories, omit_keys = att_end or {}, inventories or {}, omit_keys or {}
    w = World(root, edits, log_fmt)
    c3_status = {**{0.002: 'PASS', 0.005: 'PASS'}, **(c3_status or {})}
    comp_start = {**{0.002: 'fresh', 0.005: 'fresh'}, **(comp_start or {})}
    s0 = w.segment('mv', 's0', 100, RELAX_NL, geom(0), [(None, -1000.0, forces(0)), (geom(1), -1000.001, forces(1))],
                   term='2026-10-11T20:00:00Z')
    s1 = w.segment('mv', 's1', 101, mv_s1_nl or RELAX_NL, geom(1),
                   [(None, -1000.001001, forces(1)), (geom(2), -1000.00105, forces(2))], final=geom(2), term=mv_term)
    w.rec('lin_mv', 'relaxation_lineage', {'cell': cell, 'route': 'registered-MV'},
          {'segments': [s0, s1], 'offset_evidence': w.tz})
    fmv = w.final('final_mv', FINAL_NL, geom(2), cluster=600)
    w.rec('final_run_mv', 'final_run', {'cell': cell}, World.fsrc(fmv))
    w.cert('cert_mv', cell, fmv['rf'], fmv['g'], {'relaxation': ('converged', ['lin_mv']),
                                                  'geometry': ('mv', ['lin_mv'])})
    k_fin = 2 if zero_step else 3
    last_f = forces(3, 0.5) if not zero_step else forces(2, 0.5)
    if polish_last_max is not None:
        last_f = [list(r) for r in last_f]
        last_f[0][0] = polish_last_max
    pol_evals = ([(None, -1000.0016, last_f)] if zero_step else
                 [(None, -1000.0016, forces(2, 0.5)), (geom(3), -1000.00165, last_f)])
    p0 = w.segment('pol', 'p0', 200, polish_nl or POLISH_NL, geom(2), pol_evals, final=geom(k_fin), term=polish_term)
    w.rec('lin_pol', 'relaxation_lineage', {'cell': cell, 'route': 'C4-polish'},
          {'segments': [p0], 'parent': w.p['cert_mv'], 'offset_evidence': w.tz})
    qf = [list(r) for r in pol_evals[-1][2]]
    qf[0][0] = round(qf[0][0] + qual_dforce, 8)
    q_nl = nl(polish_nl or POLISH_NL, control__calculation="'scf'", control__tprnfor='.true.')
    if not qual_fresh:
        q_nl = nl(q_nl, electrons__startingpot="'file'")
    w.qualification('q_pol', cell, 201, q_nl, geom(k_fin), round(pol_evals[-1][1] + qual_dF, 8), qf, w.p['lin_pol'],
                    qual_term)
    c4src = {'parent_certificate': w.p['cert_mv'], 'polish_lineage': w.p['lin_pol'], 'qualification': w.p['q_pol']}
    if zero_step:
        c4src['reused_final'] = w.p['final_run_mv']
    w.rec('c4', 'c4_polish', {'cell': cell}, c4src)
    if zero_step:
        ref, fname = fmv, 'final_run_mv'
    else:
        ref_nl = nl(final_nl or FINAL_NL, electrons__startingpot="'file'") if ref_seeded else (final_nl or FINAL_NL)
        ref, fname = w.final('final_pol', ref_nl, geom(3), cluster=650), 'final_run_pol'
        w.rec('final_run_pol', 'final_run', {'cell': cell}, World.fsrc(ref))
    g_pol = ref['g']
    rt = {'aIO': ('2026-10-15T00:00:00Z', None), 'aIWO': ('2026-10-15T00:00:00Z', None),
          'compensated': ('2026-10-15T00:00:00Z', None), **(role_terms or {})}
    roles_src, chosen = {}, {}
    for role, (prim_cell, back_cell) in W.A15_ROLE_CELLS.items():
        pt, bt = rt[role]
        roles_src[role] = {'primary': w.role_lineage(prim_cell, pt)}
        if bt is not None:
            roles_src[role]['backup'] = w.role_lineage(back_cell, bt)
        cut = F.parse_utc(F.CUTOFF_UTC)
        chosen[role] = prim_cell if F.parse_utc(pt) <= cut else (back_cell if bt and F.parse_utc(bt) <= cut else None)
    names = [n for n in chosen.values() if n]
    w.sealed('audit.json', {'kind': 'A15 smearing audit', 'status': 'PARTIAL',
                            'provisional_width_candidate_Ry': candidate,
                            'provenance': {'code_version': '1.0.0-rc7', 'code_sha256': F.RC7_CODE_SHA256,
                                           'inputs': [entry(n, run_files(n + str(x)), H('c' + n), H('g' + n), x)
                                                      for n in names for x in (0.005, 0.002, 0.001)]}})
    w.rec('a15', 'a15_provisional', {}, {'audit_report': w.p['audit.json'], 'roles': roles_src})
    relax_ev, geo_ev = ['lin_pol', 'q_pol'], ['c4', fname]
    w.cert('cert_pol_v1', cell, ref['rf'], g_pol, {'relaxation': ('converged', relax_ev),
                                                   'geometry': ('polished', geo_ev)})
    v1 = F.sha256_file(w.p['cert_pol_v1'])
    plan_slots, slots, reports, comps = [], [], [], []
    for wd in (0.002, 0.005):
        tag = f'{int(round(wd * 1000)):03d}'
        sid = f'c3_{cell}_{tag}'
        attempts = [('a', 500 + int(tag), comp_start[wd], c3_status[wd])]
        if wd == 0.005 and extra_seeded:
            attempts.append(('b', 520, 'density-seeded', extra_seeded))
        runs = [f'comp_{tag}{x[0]}' for x in attempts] + ([f'comp_{tag}n'] if wd == 0.005 and extra_noout is not None
                                                          else []) + list((extra_runs or {}).get(tag, []))
        plan_slots.append({'slot': sid, 'cell': cell, 'geometry_sha256': g_pol, 'width_Ry': wd, 'runs': runs})
        jobs, atts = [], []
        for suffix, cl, mode, status in attempts:
            over = {'system__degauss': str(wd)}
            if mode == 'density-seeded':
                over['electrons__startingpot'] = "'file'"
            written = late_manifest if late_manifest and (tag + suffix) == '005a' else '2026-10-15T23:59:00Z'
            run = w.final(f'comp_{tag}{suffix}', nl(FINAL_NL, **over), geom(k_fin), cluster=cl, written=written,
                          manifest=comp_manifest)
            jobs.append((cl, '2026-10-15T00:00:00Z', '2026-10-16T00:00:00Z', att_end.get(tag + suffix, 0)))
            name = f'comp_{tag}{suffix}'
            w.rec(name, 'c3_companion_run', {'cell': cell}, {**World.fsrc(ref, 'ref_'), **World.fsrc(run, 'comp_')})
            comps.append(name)
            w.rec(f'final_run_c{tag}{suffix}', 'final_run', {'cell': cell}, World.fsrc(run))
            att = {'cluster': cl, 'export_manifest': run['man'], 'certify_output': run['co'], 'archives': run['archives']}
            if (tag + suffix) in hide_output:                  # Codex 20:44Z attack: keep the cluster, drop the output
                att = {'cluster': cl}
            att['job_history'] = w.job_history(f'hist/{cl}.txt', cl, name,                             # v8
                                               (hist_sub or {}).get(tag + suffix, '2026-10-15T00:00:00Z'))
            for k in omit_keys.get(tag + suffix, ()):
                att.pop(k, None)
            if (tag + suffix) in inventories:
                att['artifact_inventory'] = w.attempt_inventory(tag + suffix, inventories[tag + suffix], name, cl,
                                                                run['exp'])
            if (tag + suffix) not in drop_attempts:
                atts.append(att)
            rep = w.sealed(f'c3_{tag}{suffix}.json', {
                'kind': 'C3', 'roles': ['reference', 'other'], 'status': status, 'widths_Ry': [0.001, wd],
                'items': [{'quantity': 'host gap (eV)', 'reference': 1.234567, 'compared': 1.239876, 'pass': True}],
                'provenance': {'code_version': '1.0.0-rc7', 'code_sha256': F.RC7_CODE_SHA256,
                               'inputs': [entry(cell, ref['rf'], v1, g_pol, 0.001),
                                          entry(cell, run['rf'], H('cc' + tag + suffix), g_pol, wd)]}})
            if tamper_report == tag + suffix:
                with open(rep, encoding='utf-8') as fh:
                    o = json.load(fh)
                o['widths_Ry'] = [0.001, wd, 9]
                with open(rep, 'w', encoding='utf-8') as fh:
                    json.dump(o, fh)
            if (tag + suffix) not in drop_reports and (tag + suffix) not in hide_output:
                reports.append(rep)
        if wd == 0.005 and extra_noout is not None:          # an attempt that produced no output
            term = None if extra_noout == 'running' else '2026-10-16T01:00:00Z'
            jobs.append((530, '2026-10-15T01:00:00Z', term, 0 if extra_noout == 'running' else extra_noout))
            att = {'cluster': 530, 'job_history': w.job_history('hist/530.txt', 530, f'comp_{tag}n',
                                                                '2026-10-15T01:00:00Z')}
            if f'{tag}n' in inventories:
                att['artifact_inventory'] = w.attempt_inventory(f'{tag}n', inventories[f'{tag}n'], f'comp_{tag}n', 530)
            atts.append(att)
        slots.append({'slot': sid, 'joblog': w.joblog(f'slot_{tag}.log', jobs), 'attempts': atts})
    if foreign_slot:                     # v7 scope: another cell's slot with an ordinary unresolved attempt
        plan_slots.append({'slot': 'c3_aIWO_1p0_s1_005', 'cell': 'aIWO_1p0_s1', 'geometry_sha256': H('other'),
                           'width_Ry': 0.005, 'runs': ['other_c3']})
        slots.append({'slot': 'c3_aIWO_1p0_s1_005',
                      'attempts': [{'cluster': 540, 'job_history': w.job_history('hist/540.txt', 540, 'other_c3',
                                                                                 '2026-10-15T00:00:00Z')}],
                      'joblog': w.joblog('slot_other.log', [(540, '2026-10-15T00:00:00Z', '2026-10-16T00:00:00Z', 1)])})
    if plan_runs_dup:                    # v7: one run owned by two slots (ambiguous plan)
        plan_slots[0]['runs'] = plan_slots[0]['runs'] + [plan_slots[1]['runs'][0]]
    plan = w.write('c3_plan.json', json.dumps({'schema': W.PLAN_SCHEMA, 'export_root': EXPORT_ROOT,
                                               'slots': plan_slots}))
    w.rec('manifest', 'readout_manifest', {}, {'plan': plan, 'slots': slots, 'c3_reports': reports,
                                               'offset_evidence': w.tz})
    if abs(width - 0.001) < 1e-12:
        smear_ev = [fname, 'a15', 'manifest', 'cert_pol_v1'] + comps
        w.cert('cert_pol', cell, ref['rf'], g_pol, {'relaxation': ('converged', relax_ev),
                                                    'geometry': ('polished', geo_ev),
                                                    'smearing': ('qualified', smear_ev, width)})
    else:
        tag = f'{int(round(width * 1000)):03d}a'
        w.cert('cert_pol', cell, w.runs['comp_' + tag]['rf'], g_pol,
               {'relaxation': ('converged', relax_ev), 'geometry': ('polished', ['c4', f'final_run_c{tag}']),
                'smearing': ('qualified', [f'final_run_c{tag}', 'a15', 'manifest'] + comps, width)})
    w.g_mv, w.g_pol, w.run_pol, w.run_mv, w.cell, w.ref = fmv['g'], g_pol, ref['rf'], fmv['rf'], cell, ref
    return w


def gated_world(root, gate_dF=3e-6, gate_dforce=2e-4, carried_ok=True, edits=None, qual=True, cell='aIWO_2p0_comp_s1',
                route='A36', s0_nl=None, s12_nl=None, s0_fail=False, s1_fail=False, s2_from_earlier=False, pre=1,
                pre_aids_from=None):
    """A35/A36-type chain: `pre` segments with the original settings, then two rescue segments (one epoch) -> the
    rescue boundary gate is required. v7: an SCF failure is modelled as an old-rule continuation (the returned
    relax.in still moves on), so the chain stays linked; s2_from_earlier restarts the second rescue segment from the
    first rescue segment's first evaluation instead of the selected geometry (Codex v6 review item 2)."""
    w = World(root, edits)
    s12 = s12_nl or nl(**AIDS)
    segs = []
    for j in range(pre):                                   # original-settings segments s0 .. s<pre-1>
        fo = forces(j)
        evals = [(None, round(-2000.0 - 0.001 * j, 8), fo), (geom(j + 1), round(-2000.001 - 0.001 * j, 8),
                                                           forces(j + 1))]
        if j > 0:                                          # first SCF = the previous segment's last one (gate passes)
            evals[0] = (None, round(-2000.001 - 0.001 * (j - 1), 8), forces(j))
        fail = s0_fail and j == 0
        pre_nl = nl(RELAX_NL, **AIDS) if pre_aids_from is not None and j >= pre_aids_from else (s0_nl or RELAX_NL)
        segs.append(w.segment('c', f's{j}', 300 + j, pre_nl, geom(j), evals,
                              term=F.fmt_utc(F.parse_utc('2026-10-12T09:38:54Z') - dt.timedelta(hours=6 * (pre - 1 - j))),
                              scf_fail=fail, returned=geom(j + 1) if fail else None,
                              status='CONTINUE' if fail else None))
    a, b = pre, pre + 1                                    # the two rescue segments
    base = round(-2000.001 - 0.001 * (pre - 1), 8)
    s1 = w.segment('c', f's{a}', 300 + a, s12, geom(a),
                   [(None, round(base - 0.0001, 8), forces(a)), (geom(a + 1), round(base - 0.0005, 8), forces(a + 1))],
                   term='2026-10-13T12:00:00Z', scf_fail=s1_fail, returned=geom(a + 1) if s1_fail else None,
                   status='CONTINUE' if s1_fail else None)
    f2 = [list(r) for r in forces(a + 1)]
    f2[1][1] = round(f2[1][1] + gate_dforce, 8)
    if s2_from_earlier:
        start, first = geom(a), (None, round(base - 0.0001, 8), forces(a))
    else:
        start, first = (geom(a + 1) if carried_ok else geom(5)), (None, round(base - 0.0005 + gate_dF, 8), f2)
    last_F = round(base - (0.00015 if s2_from_earlier else 0.00055), 8)     # residual energy change <= 1e-4 Ry
    s2 = w.segment('c', f's{b}', 300 + b, s12, start, [first, (geom(a + 2), last_F, forces(a + 2))],
                   final=geom(a + 2), term='2026-10-15T12:00:00Z')
    w.rec('lin', 'relaxation_lineage', {'cell': cell, 'route': route}, {'segments': segs + [s1, s2],
                                                                         'offset_evidence': w.tz})
    s12_last = (geom(a + 2), last_F, forces(a + 2))
    w.qualification('q', cell, 399, nl(s12, control__calculation="'scf'", control__tprnfor='.true.'), s12_last[0],
                    s12_last[1], s12_last[2], w.p['lin'], '2026-10-16T00:00:00Z')
    w.cert('cert', cell, run_files('comp'), F.input_geometry_hash(F.read_pw_input(w.p['q/scf.in'])),
           {'relaxation': ('converged', ['lin', 'q'] if qual else ['lin'])})
    return w


class _AnyCell(dict):
    """TEST ONLY: the synthetic FINAL template (FINAL_NL, width excluded) registered for every synthetic cell."""

    def __init__(self, keys):
        super().__init__()
        self.keys_ = tuple(keys)

    def get(self, k, d=None):
        return self.keys_


_TEMPLATE_KEY = []


def final_template_key():
    """v9: the settings key of the synthetic FINAL template (as f9_common.final_template_key computes it)."""
    if not _TEMPLATE_KEY:
        d = tempfile.mkdtemp(prefix='f9tmpl_')
        try:
            path = World(d).pw_in('tmpl/scf.in', FINAL_NL, geom(0))
            _TEMPLATE_KEY.append(F.final_template_key(F.settings_block(F.read_pw_input(path))))
        finally:
            shutil.rmtree(d, ignore_errors=True)
    return _TEMPLATE_KEY[0]


class Base(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='f9v5_')
        self.n = 0
        self._tmpl = getattr(F, 'REGISTERED_FINAL_TEMPLATES', None)
        if hasattr(F, 'final_template_key'):          # v9: the synthetic template is registered (TEST ONLY)
            F.REGISTERED_FINAL_TEMPLATES = _AnyCell([final_template_key()])

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
        if self._tmpl is not None:
            F.REGISTERED_FINAL_TEMPLATES = self._tmpl

    def sub(self):
        self.n += 1
        return os.path.join(self.root, f'w{self.n}')

    def check(self, w, cert='cert_pol', ext=None, reports=()):
        return CA.check_output_allowlist(CA.run(w.p[cert], CA.Ctx(extension=ext), [w.p[r] for r in reports]))

    @staticmethod
    def why(res, block):
        return ' | '.join(res['blocks'][block]['reasons'])

    def assertDowngrade(self, res, block, needle):
        self.assertEqual(res['verdict'], 'DOWNGRADE_REQUIRED', json.dumps(res, indent=1))
        self.assertEqual(res['blocks'][block]['verdict'], 'DOWNGRADE', res['blocks'][block])
        self.assertIn(needle, self.why(res, block))

    def assertNotDerivable(self, fn, code):
        with self.assertRaises(F.DeriveError) as cm:
            fn()
        self.assertEqual(str(cm.exception), code)

    def assertSlotUnresolved(self, w, code):
        """v7 blocking-scope ruling: the record is derived, the attempt and its slot are UNRESOLVED with `code`, and
        the certificate of that cell / geometry is downgraded with it."""
        d = jload(w.p['manifest'])['derived']
        hit = [s for s in d['slots'] if code in s['reasons']]
        self.assertTrue(hit and all(s['status'] == 'unresolved' for s in hit), json.dumps(d['slots'], indent=1))
        res = self.check(w)
        self.assertDowngrade(res, 'smearing', 'C3 inventory UNRESOLVED')
        self.assertIn(code, self.why(res, 'smearing'))
        return d, res


# ================================================================ v7 (Codex v6 review 2026-10-13T02:10Z, FIX_FIRST)
class TestV7CodexV6Review(Base):
    """The four false-accept paths of the v6 review, each written first against v6 (where it was accepted)."""

    def assertUnresolved(self, res, code):
        self.assertDowngrade(res, 'smearing', 'C3 inventory UNRESOLVED')
        self.assertIn(code, self.why(res, 'smearing'))

    # 1. a listing of another directory hides a FAIL exported under the attempt's own destination
    def test_v7_1_wrong_directory_inventory_cannot_hide_a_fail(self):
        for kind, code in (('wrong_root', 'attempt_inventory_run_is_not_this_slots_run'),
                           ('other_run', 'attempt_inventory_run_is_not_this_slots_run'),
                           ('other_root', 'attempt_inventory_destination_is_not_this_runs_export_directory')):
            res = self.check(polished_world(self.sub(), extra_seeded='FAIL', att_end={'005b': 1},
                                            hide_output=('005b',), inventories={'005b': kind}))
            self.assertUnresolved(res, code)

    # 2. unrelated segments: s1 starts from B although s0 returned A
    def test_v7_2_segment_must_continue_the_returned_geometry(self):
        w = World(self.sub())
        s0 = w.segment('u', 's0', 10, RELAX_NL, geom(0), [(None, -1.0, forces(0)), (geom(1), -1.0001, forces(1))],
                       term='2026-10-10T12:00:00Z')                       # returns A = geom(1)
        s1 = w.segment('u', 's1', 11, RELAX_NL, geom(5), [(None, -1.00011, forces(1)), (geom(6), -1.0002, forces(2))],
                       final=geom(6), term='2026-10-11T00:00:00Z')        # starts from unrelated B, converges C
        self.assertNotDerivable(lambda: w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_0p7_s1',
                                                                            'route': 'registered-MV'},
                                              {'segments': [s0, s1], 'offset_evidence': w.tz}),
                                'segment_does_not_continue_the_previous_segment')

    def test_v7_2_gated_restart_from_an_earlier_evaluation_refused(self):
        with self.assertRaises(F.DeriveError) as cm:     # B = s1's first evaluation; D-24 selected A = geom(2)
            gated_world(self.sub(), s2_from_earlier=True)
        self.assertEqual(str(cm.exception), 'segment_does_not_continue_the_previous_segment')

    # 3. an authentic archive written on 18 Oct cannot borrow another cluster's termination on 16 Oct
    def test_v7_3_archive_outside_the_jobs_execution_window_refused(self):
        w = World(self.sub())
        s0 = w.segment('t', 's0', 7, GAUSS_NL, geom(0), [(None, -50.0, forces(0)), (geom(1), -50.00005, forces(1))],
                       final=geom(1), term='2026-10-16T00:00:00Z', archive_mtime='2026-10-18T09:00:00Z')
        self.assertNotDerivable(lambda: w.rec('lin', 'relaxation_lineage', {'cell': 'aIO_2p0_s1',
                                                                            'route': 'registered-Gaussian'},
                                              {'segments': [s0], 'offset_evidence': w.tz}),
                                'segment_archive_written_outside_the_jobs_execution')

    # 4. a settings change cannot erase a failed restart gate; inherited failures survive an authorized epoch
    def _gated_chain(self, cell, route, specs, final_geom, qual_nl):
        w = World(self.sub())
        segs = []
        for k, (nlv, start, evals, final, term) in enumerate(specs):
            segs.append(w.segment('g', f's{k}', 40 + k, nlv, start, evals, final=final, term=term))
        return w, segs

    def _qualify_and_certify(self, w, cell, route, segs, final_geom, qual_nl, F_last, f_last):
        w.rec('lin', 'relaxation_lineage', {'cell': cell, 'route': route}, {'segments': segs, 'offset_evidence': w.tz})
        w.qualification('q', cell, 49, nl(qual_nl, control__calculation="'scf'", control__tprnfor='.true.'),
                        final_geom, F_last, f_last, w.p['lin'], '2026-10-16T00:00:00Z')
        w.cert('cert', cell, run_files('g'), F.input_geometry_hash(F.read_pw_input(w.p['q/scf.in'])),
               {'relaxation': ('converged', ['lin', 'q'])})
        return self.check(w, cert='cert')

    def test_v7_4_unauthorized_settings_change_cannot_drop_a_failed_gate(self):
        G = nl(GAUSS_NL, **AIDS)
        G2 = nl(G, electrons__mixing_beta='0.11')
        f2 = [list(r) for r in forces(2)]
        f2[1][1] = round(f2[1][1] + 0.01, 8)                                  # s1->s2 fails: max |dF| 0.01
        specs = [(RELAX_NL, geom(0), [(None, -3000.0, forces(0)), (geom(1), -3000.001, forces(1))], None,
                  '2026-10-11T00:00:00Z'),
                 (G, geom(1), [(None, -3000.0011, forces(1)), (geom(2), -3000.0015, forces(2))], None,
                  '2026-10-12T00:00:00Z'),
                 (G, geom(2), [(None, -3000.0015, f2), (geom(3), -3000.00155, forces(3))], None,
                  '2026-10-13T00:00:00Z'),
                 (G2, geom(3), [(None, -3000.00155, forces(3)), (geom(4), -3000.0016, forces(4))], geom(4),
                  '2026-10-15T00:00:00Z')]
        w, segs = self._gated_chain('aIWO_2p0_s2', 'A36', specs, geom(4), G2)
        self.assertNotDerivable(lambda: self._qualify_and_certify(w, 'aIWO_2p0_s2', 'A36', segs, geom(4), G2,
                                                                  -3000.0016, forces(4)),
                                'settings_change_without_authorized_epoch_start')

    def test_v7_4_inherited_gate_failure_survives_an_authorized_epoch(self):
        # changed in v8 (Codex v7 ruling): pre-rescue MV comparisons stay diagnostics; A35's mandatory gates begin
        # at s4; a failed or missing mandatory gate vetoes
        G, MVA = nl(GAUSS_NL, **AIDS), nl(RELAX_NL, **AIDS)
        bad = lambda f: [[r[0], round(r[1] + 0.01, 8) if i == 1 else r[1], r[2]] for i, r in enumerate(f)]

        def run(s4_first):
            specs = [(RELAX_NL, geom(0), [(None, -4000.0, forces(0)), (geom(1), -4000.001, forces(1))], None,
                      '2026-10-10T06:00:00Z'),
                     (MVA, geom(1), [(None, -4000.001, forces(1)), (geom(2), -4000.0012, forces(2))], None,
                      '2026-10-11T00:00:00Z'),                                # registered aids at s1 (A35 diagnosis)
                     (MVA, geom(2), [(None, -4000.0012, bad(forces(2))), (geom(3), -4000.0013, forces(3))], None,
                      '2026-10-12T00:00:00Z'),                                # MV s1->s2 outside tolerance
                     (G, geom(3), [(None, -4000.0014, forces(3)), (geom(4), -4000.0015, forces(4))], None,
                      '2026-10-13T00:00:00Z'),                                # A35 starts at s3
                     (G, geom(4), [(None, -4000.0015, s4_first), (geom(5), -4000.00155, forces(5))], geom(5),
                      '2026-10-15T00:00:00Z')]
            w, segs = self._gated_chain('aIWO_0p8_s2', 'A35', specs, geom(5), G)
            return w, self._qualify_and_certify(w, 'aIWO_0p8_s2', 'A35', segs, geom(5), G, -4000.00155, forces(5))
        w, res = run(forces(4))
        self.assertEqual(res['verdict'], 'CLAIMS_OK', json.dumps(res, indent=1))
        self.assertTrue(any('diagnostic comparisons' in x and 's1->s2' in x for x in res['blocks']['relaxation']['notes']))
        d = jload(w.p['lin'])['derived']
        self.assertEqual((d['required_gates'], [e['segment'] for e in d['epoch_starts']]), (['s3->s4'], ['s1', 's3']))
        _, res = run(bad(forces(4)))                                           # mandatory s3->s4 fails
        self.assertDowngrade(res, 'relaxation', 'restart gate s3->s4 FAILED')


# ================================================================ v9 (Codex v8 review 2026-10-13, FIX_FIRST)
class _Registry:
    """Temporarily registers synthetic frozen entries (TEST ONLY) in f9_common; restored afterwards."""

    def __init__(self, **entries):
        self.entries, self.old = entries, {}

    def __enter__(self):
        for k, v in self.entries.items():
            self.old[k] = getattr(F, k, None)
            setattr(F, k, v)
        return self

    def __exit__(self, *a):
        for k, v in self.old.items():
            setattr(F, k, v)


class TestV9CodexV8Review(Base):
    """The four false-accept paths of the Codex v8 review and its rulings, each written first against v8."""
    G = nl(GAUSS_NL, **AIDS)
    MVA = nl(RELAX_NL, **AIDS)

    # 1. a density restart cannot bypass the fresh-restart gate (start mode asserted per segment, defaults included)
    def _a35_s4(self, s4_nl):
        w = World(self.sub())
        segs = [w.segment('e', f's{k}', 30 + k, self.MVA, geom(k), [(None, -7.0 - 0.001 * k, forces(k)),
                                                                     (geom(k + 1), -7.001 - 0.001 * k, forces(k + 1))],
                          term=f'2026-10-1{k}T12:00:00Z', sub=f'2026-10-1{k}T06:00:00Z') for k in range(3)]
        segs.append(w.segment('e', 's3', 33, self.G, geom(3), [(None, -7.0031, forces(3)), (geom(4), -7.0032, forces(4))],
                              term='2026-10-13T12:00:00Z', sub='2026-10-13T06:00:00Z'))
        segs.append(w.segment('e', 's4', 34, s4_nl, geom(4), [(None, -7.0032, forces(4)), (geom(5), -7.00321, forces(5))],
                              final=geom(5), term='2026-10-14T12:00:00Z', sub='2026-10-14T06:00:00Z'))
        return w, lambda: w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_0p8_s2', 'route': 'A35'},
                                {'segments': segs, 'offset_evidence': w.tz})

    def test_v9_1_density_restart_cannot_bypass_the_fresh_restart_gate(self):
        w, fn = self._a35_s4(self.G)
        fn()                                                       # control: the fresh s4 derives, gate s3->s4 required
        self.assertEqual(jload(w.p['lin'])['derived']['required_gates'], ['s3->s4'])
        for over in ({'control__restart_mode': "'restart'", 'electrons__startingpot': "'file'"},
                     {'control__restart_mode': "'restart'"},             # QE: restart implies startingpot='file'
                     {'electrons__startingpot': "'file'"}, {'electrons__startingwfc': "'file'"}):
            self.assertNotDerivable(self._a35_s4(nl(self.G, **over))[1], 'segment_start_is_not_the_registered_fresh_start')

    # 2. bestvalid is recomputed from the bound evaluations, never trusted by name and hash
    def _reset_from(self, bestvalid, start, s0_evals=None, status='FAILED [scf]', cell='aIWO_0p7_s1', rollback=False,
                    rollback_logged='2026-10-10T14:00:00Z'):
        w = World(self.sub())
        ev = s0_evals or [(None, -1.0, forces(0)), (geom(1), -1.0002, forces(1))]
        s0 = w.segment('b', 's0', 70, RELAX_NL, geom(0), ev, term='2026-10-10T12:00:00Z',
                       scf_fail=status.startswith('FAILED'), status=status, bestvalid=bestvalid)
        s1 = w.segment('b', 's1', 71, RELAX_NL, start, [(None, -1.0002, forces(1)), (geom(2), -1.0003, forces(2))],
                       final=geom(2), term='2026-10-11T00:00:00Z')
        s1['transition_record'] = w.transition_record('b/reset1.tr', 'b', 'section3_reset', 'relax_s0', 1,
                                                      '2026-10-10T15:00:00Z')
        if rollback:                                   # v12: restoration evidence of the [infra] bestvalid exception
            s1['rollback_record'] = w.rollback_record('b/rollback.txt', 'b', 'relax_s0', rollback_logged)
        return lambda: w.rec('lin', 'relaxation_lineage', {'cell': cell, 'route': 'registered-MV'},
                             {'segments': [s0, s1], 'offset_evidence': w.tz})

    def test_v9_2_bestvalid_member_must_be_the_validated_minimum(self):
        self._reset_from(geom(1), geom(1))()                       # control: the member is the validated minimum
        self.assertNotDerivable(self._reset_from(geom(5), geom(5)), 'bestvalid_member_is_not_the_validated_minimum')
        self.assertNotDerivable(self._reset_from(geom(0), geom(0)), 'bestvalid_member_is_not_the_validated_minimum')

    def test_v9_2_paused_continue_resumes_from_the_returned_geometry(self):
        ev = [(None, -1.0003, forces(0)), (geom(1), -1.0002, forces(1))]      # lowest energy at g0, returned = g1
        self.assertNotDerivable(self._reset_from(None, geom(0), s0_evals=ev, status='CONTINUE'),
                                'paused_continue_must_resume_from_the_returned_geometry')

    # 3. rescue authorization, once-use, remaining budget, exhaustion / prospective suspension, terminal failure
    def _rescue(self, auth=None, registry=None, third=None, a43=False, a43_kw=None):
        w = World(self.sub())
        s0 = w.segment('m', 's0', 70, RELAX_NL, geom(0), [(None, -1.0, forces(0)), (geom(1), -1.0002, forces(1))],
                       term='2026-10-10T12:00:00Z', scf_fail=True, status='FAILED [scf]', bestvalid=geom(1))
        s1 = w.segment('m', 's1', 71, RELAX_NL, geom(1), [(None, -1.0002, forces(1)), (geom(2), -1.0003, forces(2))],
                       term='2026-10-11T00:00:00Z')
        s1['transition_record'] = w.transition_record('m/reset1.tr', 'm', 'section3_reset', 'relax_s0', 1,
                                                      '2026-10-10T15:00:00Z')
        s2 = w.guard_segment('m', 's2', 72, RELAX_NL, geom(2), '2026-10-11T01:00:00Z')
        last = third is None
        r0 = w.segment('m', 's0', 80, RELAX_NL, geom(2), [(None, -1.0003, forces(2)), (geom(3), -1.00031, forces(3))],
                       final=geom(3) if last else None, term='2026-10-15T12:00:00Z', attempt=2)
        r0['rescue_file'] = w.rescue_file('m/rescue2_rescue.dag'.replace('.tr', ''), 0)
        if a43:                                        # v13: A43 count enforcement (RETRY = remaining_after - 1)
            kw = dict(a43_kw or {})
            r0.update(w.a43_dag_set('m', kw.pop('retry', auth[2] - 1), node_cluster=80, **kw))
        r0['transition_record'] = w.transition_record('m/rescue2.tr', 'm', 'section3_rescue', 'relax_s1', 1,
                                                      '2026-10-13T00:00:00Z', s0['archives'] + s1['archives'] + s2['archives'],
                                                      auth=auth)
        segs = [s0, s1, s2, r0]
        if third is not None:                                      # a successive rescue (attempt 3)
            q0 = w.segment('m', 's0', 90, RELAX_NL, geom(3), [(None, -1.00031, forces(3)), (geom(4), -1.00032, forces(4))],
                           final=geom(4), term='2026-10-16T12:00:00Z', attempt=3)
            q0['rescue_file'] = w.rescue_file('m/rescue3_rescue.dag'.replace('.tr', ''), 0)
            q0['transition_record'] = w.transition_record('m/rescue3.tr', 'm', 'section3_rescue', 'relax_s0', 2,
                                                          '2026-10-16T00:00:00Z', r0['archives'], auth=third)
            segs.append(q0)
        fn = lambda: w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_0p7_s1', 'route': 'registered-MV'},
                           {'segments': segs, 'offset_evidence': w.tz})
        return w, fn

    SUSP = {'R-TEST': {'run': 'm', 'after_attempt': 1, 'basis': 'suspension', 'pause_started_utc': '2026-10-11T00:45:00Z',
                       'rule_logged_utc': '2026-10-11T00:30:00Z', 'additional_executions': 0}}

    def _with(self, registry, fn):
        with _Registry(REGISTERED_RESCUE_AUTHORIZATIONS=registry):
            return fn()

    def test_v9_3_rescue_without_registered_authorization_is_refused(self):
        self.assertNotDerivable(self._rescue()[1], 'rescue_without_a_registered_authorization')
        self.assertNotDerivable(lambda: self._with({}, self._rescue(auth=('R-TEST', 6, 6, 0, 'no'))[1]),
                                'rescue_without_a_registered_authorization')

    def test_v9_3_authorized_rescue_preserves_budget_and_prior_use(self):
        w, fn = self._rescue(auth=('R-TEST', 6, 6, 0, 'no'))
        self._with(self.SUSP, fn)                                  # control: registered, prospective, budget carried
        d = jload(w.p['lin'])['derived']
        self.assertEqual([(x['segment'], x['continuation']) for x in d['segments']][-1], ('a2.s0', 'section3_rescue'))
        for auth, code in ((('R-TEST', 6, 9, 0, 'no'), 'rescue_resets_the_remaining_executions'),
                           (('R-TEST', 7, 7, 0, 'no'), 'rescue_budget_not_preserved'),
                           (('R-TEST', 6, 6, 1, 'no'), 'rescue_prior_use_not_preserved'),
                           (('R-TEST', 6, 6, 0, 'yes'), 'rescue_terminal_failure_status_differs')):
            self.assertNotDerivable(lambda: self._with(self.SUSP, self._rescue(auth=auth)[1]), code)

    def test_v9_3_successive_rescue_needs_its_own_unused_authorization(self):
        reg = dict(self.SUSP)
        fn = self._rescue(auth=('R-TEST', 6, 6, 0, 'no'), third=('R-TEST', 5, 5, 1, 'no'))[1]
        self.assertNotDerivable(lambda: self._with(reg, fn), 'rescue_authorization_already_used')

    def test_v9_3_exhaustion_or_prospective_suspension(self):
        late = {'R-TEST': dict(self.SUSP['R-TEST'], rule_logged_utc='2026-10-12T00:00:00Z')}
        self.assertNotDerivable(lambda: self._with(late, self._rescue(auth=('R-TEST', 6, 6, 0, 'no'))[1]),
                                'suspension_rule_not_prospective')
        exh = {'R-TEST': {'run': 'm', 'after_attempt': 1, 'basis': 'exhausted', 'additional_executions': 9}}
        self.assertNotDerivable(lambda: self._with(exh, self._rescue(auth=('R-TEST', 6, 15, 0, 'no'))[1]),
                                'rescue_without_exhaustion_of_the_previous_attempt')

    def test_v9_3_no_revival_after_a_terminal_rescue_failure(self):
        w = World(self.sub())
        s0 = w.segment('t', 's0', 40, RELAX_NL, geom(0), [(None, -2000.0, forces(0)), (geom(1), -2000.001, forces(1))],
                       term='2026-10-12T09:00:00Z')
        s1 = w.segment('t', 's1', 41, self.MVA, geom(1), [(None, -2000.0011, forces(1)), (geom(2), -2000.0015, forces(2))],
                       term='2026-10-13T09:00:00Z', scf_fail=True, status='FAILED [scf]', bestvalid=geom(2))
        s2 = w.segment('t', 's2', 42, self.MVA, geom(2), [(None, -2000.0015, forces(2)), (geom(3), -2000.00151, forces(3))],
                       final=geom(3), term='2026-10-14T09:00:00Z')
        s2['transition_record'] = w.transition_record('t/r.tr', 't', 'section3_reset', 'relax_s1', 1, '2026-10-13T10:00:00Z')
        self.assertNotDerivable(lambda: w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_2p0_comp_s1', 'route': 'A36'},
                                              {'segments': [s0, s1, s2], 'offset_evidence': w.tz}),
                                'transition_after_a_terminal_rescue_failure')

    # ruling: label splits only inside the A25/A30/A34 cell scope, In -> In1/In2 and O -> O1/O2 only
    def _split(self, cell, labels, route='A30', evidence=True, unsplit_nl=None, unsplit_geom=None, resource=None):
        w = World(self.sub())
        s0 = w.segment('l', 's0', 95, RELAX_NL, geom(0), [(None, -1.0, forces(0)), (geom(1), -1.0001, forces(1))],
                       term='2026-10-10T12:00:00Z')
        s1 = w.segment('l', 's1', 96, RELAX_NL, geom(1), [(None, -1.0001, forces(1)), (geom(2), -1.0002, forces(2))],
                       final=geom(2), term='2026-10-11T00:00:00Z', labels=labels)
        if evidence:                                   # v10: route evidence + the unsplit input of the construction
            s1.update(resource_route=route, unsplit_input=w.pw_in('l/unsplit_s1.in', unsplit_nl or RELAX_NL,
                                                                  unsplit_geom or geom(1)))
            if resource != 'missing':                  # v11: the same cluster's request, Requirements and environment
                s1['resource_history'] = w.resource_history('l/res.txt', **({'cluster': 96, **(resource or {})}))
        return lambda: w.rec('lin', 'relaxation_lineage', {'cell': cell, 'route': 'registered-MV'},
                             {'segments': [s0, s1], 'offset_evidence': w.tz})

    def test_v9_label_split_scope(self):
        self._split('aIWO_2p0_s1', ['In1', 'W', 'O1', 'H'])()          # A30 scope: derives
        self.assertNotDerivable(self._split('aIWO_0p7_s1', ['In1', 'W', 'O1', 'H']), 'label_split_outside_the_registered_scope')
        self.assertNotDerivable(self._split('aIWO_2p0_s1', ['In', 'W1', 'O', 'H']), 'label_split_outside_the_registered_scope')

    # 4. registered FINAL settings: cutoffs, k-mesh, spin, SCF settings cannot drift under a positive certificate
    def test_v9_4_final_settings_must_be_the_registered_template(self):
        self.assertEqual(self.check(polished_world(self.sub()))['verdict'], 'CLAIMS_OK')          # control
        for over in ({'system__ecutwfc': '50', 'system__ecutrho': '400'}, {'system__nspin': '2'},
                     {'electrons__conv_thr': '1.0d-6'}):
            res = self.check(polished_world(self.sub(), final_nl=nl(FINAL_NL, **over)))
            self.assertDowngrade(res, 'geometry', 'registered FINAL template')

    def test_v9_4_no_registered_template_no_positive_final(self):
        with _Registry(REGISTERED_FINAL_TEMPLATES={}):
            res = self.check(polished_world(self.sub()))
        self.assertDowngrade(res, 'geometry', 'registered FINAL template')


# ================================================================ v10 (Codex v9 review 2026-10-13, FIX_FIRST)
def pw6(labels, species, shift=0.0, ecut='60'):
    """A six-atom synthetic pw.x input (two In, two O, W, H) for the split-construction unit tests."""
    pos = [[1.0 + shift, 1.0, 10.0], [3.0, 1.5, 10.5], [2.0, 2.0, 11.0], [4.0, 4.0, 12.0], [5.0, 5.0, 12.5], [6.0, 6.0, 13.0]]
    L = ['&CONTROL', "  calculation = 'relax'", '/', '&SYSTEM', '  ibrav = 0', '  nat = 6', f'  ntyp = {len(species)}',
         f'  ecutwfc = {ecut}', '  ecutrho = 480', "  occupations = 'smearing'", "  smearing = 'mv'", '  degauss = 0.01',
         '/', '&ELECTRONS', '  conv_thr = 1.0d-7', '/', '&IONS', '/', 'ATOMIC_SPECIES']
    L += [f'{l} {m} {f}' for l, m, f in species]
    L += ['CELL_PARAMETERS angstrom'] + [' '.join(f'{x:.6f}' for x in v) for v in CELL] + ['ATOMIC_POSITIONS angstrom']
    L += [f'{l} {x:.6f} {y:.6f} {z:.6f}' for l, (x, y, z) in zip(labels, pos)] + ['K_POINTS automatic', '2 2 1 0 0 0', '']
    return F.read_pw_input_bytes('\n'.join(L).encode())


IN, O, W_, H_ = SPECIES[0], SPECIES[2], SPECIES[1], SPECIES[3]
UNSPLIT6 = (['In', 'In', 'O', 'O', 'W', 'H'], [IN, O, W_, H_])
SPLIT6 = (['In1', 'In2', 'O1', 'O2', 'W', 'H'], [('In1',) + IN[1:], ('In2',) + IN[1:], ('O1',) + O[1:], ('O2',) + O[1:], W_, H_])


class TestV10CodexV9Review(Base):
    """The three cases of the Codex v9 review and its rulings (a), (b), (c), each written first against v9."""

    # 1. the initial execution budget (ruling a): 9 node executions from the first attempt; guard-only attempts count;
    #    an eviction and re-execution inside one cluster does not consume a DAG retry
    def _chain(self, n_pw, guards=(), evict=None, last_status=None, extra=None):
        w = World(self.sub())
        segs, k, g = [], 0, 0
        t0 = F.parse_utc('2026-10-08T00:00:00Z')
        for j in range(n_pw + len(guards)):
            term = F.fmt_utc(t0 + dt.timedelta(hours=7 * (j + 1)))
            if j in guards:
                segs.append(w.guard_segment('c', f's{j}', 1000 + j, RELAX_NL, geom(k), term))
                continue
            st = last_status if (last_status and j == n_pw + len(guards) - 1) else None
            fail = bool(st and st.startswith('FAILED'))
            segs.append(w.segment('c', f's{j}', 1000 + j, RELAX_NL, geom(k),
                                  [(None, round(-3.0 - 0.0001 * k, 8), forces(k)),
                                   (geom(k + 1), round(-3.0001 - 0.0001 * k, 8), forces(k + 1))],
                                  term=term, evict=(evict == j), scf_fail=fail, status=st))
            if not fail:
                k += 1
        if extra:
            segs += extra(w, segs, geom(k))
        return w, lambda: w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_0p7_s1', 'route': 'registered-MV'},
                                {'segments': segs, 'offset_evidence': w.tz})

    def test_v10_1_initial_allowance_is_bound_from_the_first_attempt(self):
        self._chain(9)[1]()                                                       # control: 9 executions
        self.assertNotDerivable(self._chain(10)[1], 'executions_exceed_the_dag_allowance')

    def test_v10_1_guard_only_attempts_count(self):
        self.assertNotDerivable(self._chain(8, guards=(3, 6))[1], 'executions_exceed_the_dag_allowance')

    def test_v10_1_eviction_inside_one_cluster_does_not_count(self):
        w, fn = self._chain(9, evict=4)
        fn()
        self.assertEqual(len(jload(w.p['lin'])['derived']['segments']), 9)

    def _a39(self, n_pw, auth, last_status=None):
        def extra(w, segs, g):
            r0 = w.segment('c', 's0', 2000, RELAX_NL, g, [(None, -4.0, forces(1)), (geom(20), -4.0001, forces(2))],
                           final=geom(20), term='2026-10-14T23:00:00Z', attempt=2)
            moved = [a for s_ in segs for a in s_['archives']]
            r0['rescue_file'] = w.rescue_file('c/rescue_rescue.dag'.replace('.tr', ''), 0)
            r0['transition_record'] = w.transition_record('c/rescue.tr', 'c', 'section3_rescue', f'relax_s{n_pw - 1}', 1,
                                                          '2026-10-14T12:00:00Z', moved, auth=auth)
            return [r0]
        return self._chain(n_pw, extra=extra, last_status=last_status)[1]

    def test_v10_1_a39_administrative_rescue_after_exhaustion(self):
        self._a39(9, ('A39', 0, 9, 0, 'no'))()                                # registered A39: +9 after exhaustion
        self.assertNotDerivable(self._a39(5, ('A39', 4, 13, 0, 'no')), 'rescue_without_exhaustion_of_the_previous_attempt')
        self.assertNotDerivable(self._a39(9, ('A39', 0, 18, 0, 'no')), 'rescue_resets_the_remaining_executions')
        self.assertNotDerivable(self._a39(9, ('A39', 0, 9, 0, 'no'), last_status='FAILED [scf]'), 'a39_trigger_not_met')

    # 2. the suspension rule must predate the actual pause start (not the end of the running segment)
    def _r(self, entry, auth=('R-TEST', 6, 6, 0, 'no'), a43_kw=None):
        fn = TestV9CodexV8Review._rescue(self, auth=auth, a43=entry.get('basis') == 'continuation_amendment', a43_kw=a43_kw)[1]
        return lambda: TestV9CodexV8Review._with(self, {'R-TEST': entry}, fn)

    SUSP = dict(TestV9CodexV8Review.SUSP['R-TEST'])

    def test_v10_2_suspension_rule_must_predate_the_pause_start(self):
        self._r(self.SUSP)()                                                       # control
        late = dict(self.SUSP, pause_started_utc='2026-10-11T00:20:00Z', rule_logged_utc='2026-10-11T00:40:00Z')
        self.assertNotDerivable(self._r(late), 'suspension_rule_not_prospective')    # logged before segment end, after pause
        self.assertNotDerivable(self._r(dict(self.SUSP, additional_executions=3), auth=('R-TEST', 6, 9, 0, 'no')),
                                'suspension_grants_no_additional_executions')

    CONT = {'run': 'm', 'after_attempt': 1, 'basis': 'continuation_amendment', 'result_informed': True,
            'pause_started_utc': '2026-10-11T00:45:00Z', 'rule_logged_utc': '2026-10-13T00:00:00Z',
            'preserved': {'remaining_executions': 6, 'prior_rescues': 0, 'terminal_failure': False}}

    def test_v10_2_result_informed_continuation_amendment(self):
        self._r(self.CONT)()                       # logged after the pause start, before resumption, state preserved
        for over, code in (({'rule_logged_utc': '2026-10-15T07:00:00Z'}, 'continuation_amendment_logged_after_resumption'),
                           ({'rule_logged_utc': '2026-10-11T00:30:00Z'}, 'continuation_amendment_backdated'),
                           ({'result_informed': False}, 'continuation_amendment_not_labelled_result_informed'),
                           ({'preserved': {'remaining_executions': 9, 'prior_rescues': 0, 'terminal_failure': False}},
                            'continuation_does_not_preserve_the_state')):
            self.assertNotDerivable(self._r(dict(self.CONT, **over)), code)

    # 3. relabeling (ruling c): alternating atom map, balanced counts, construction equivalence, authorized cell and route
    def test_v10_3_split_map_must_alternate_and_balance(self):
        good, uns = pw6(*SPLIT6), pw6(*UNSPLIT6)
        self.assertIsNone(F.label_split_problem('aIWO_2p0_s1', good))
        unbal = pw6(['In1', 'In1', 'O1', 'O1', 'W', 'H'], [('In1',) + IN[1:], ('O1',) + O[1:], W_, H_])
        alt = pw6(['In2', 'In1', 'O1', 'O2', 'W', 'H'], SPLIT6[1])
        part = pw6(['In1', 'In', 'O1', 'O2', 'W', 'H'], [('In1',) + IN[1:], IN, ('O1',) + O[1:], ('O2',) + O[1:], W_, H_])
        for bad in (unbal, alt, part):
            self.assertEqual(F.label_split_problem('aIWO_2p0_s1', bad), 'label_split_not_the_registered_construction')
        self.assertEqual(F.epoch_key(good), F.epoch_key(uns))                      # ntyp 4 -> 6 starts no epoch

    def test_v10_3_construction_equivalence_cell_and_route(self):
        good, uns = pw6(*SPLIT6), pw6(*UNSPLIT6)
        self.assertIsNone(F.split_construction_problem('aIWO_2p0_s1', 'A30', good, uns))
        self.assertEqual(F.split_construction_problem('aIWO_2p0_s1', 'A25', good, uns), 'label_split_outside_the_registered_scope')
        self.assertEqual(F.split_construction_problem('aIO_2p0_s1', 'A30', good, uns), 'label_split_outside_the_registered_scope')
        self.assertEqual(F.split_construction_problem('aIWO_2p0_s1', 'A35', good, uns), 'label_split_outside_the_registered_scope')
        for other in (pw6(*UNSPLIT6, shift=0.01), pw6(*UNSPLIT6, ecut='70')):
            self.assertEqual(F.split_construction_problem('aIWO_2p0_s1', 'A30', good, other), 'split_construction_not_equivalent')

    def test_v10_3_split_needs_route_and_construction_evidence(self):
        T = TestV9CodexV8Review
        T._split(self, 'aIWO_2p0_s1', ['In1', 'W', 'O1', 'H'])()                   # control: A30 evidence
        self.assertNotDerivable(T._split(self, 'aIWO_2p0_s1', ['In1', 'W', 'O1', 'H'], evidence=False),
                                'label_split_without_construction_evidence')
        self.assertNotDerivable(T._split(self, 'aIWO_2p0_s1', ['In1', 'W', 'O1', 'H'], route='A25'),
                                'label_split_outside_the_registered_scope')
        self.assertNotDerivable(T._split(self, 'aIWO_2p0_s1', ['In1', 'W', 'O1', 'H'], unsplit_geom=geom(3)),
                                'split_construction_not_equivalent')

    # ruling (b): README section 3 covers a geometry-only failure reset from the verified bestvalid; an [infra] failure
    # keeps the segment input (relax.in is still its input; A30 rollback), and settings changes still need an amendment
    def test_v10_b_infra_failure_reset_keeps_the_input(self):
        T = TestV9CodexV8Review
        T._reset_from(self, geom(1), geom(0), status='FAILED [infra]')()          # control: from the returned input
        self.assertNotDerivable(T._reset_from(self, geom(1), geom(1), status='FAILED [infra]', rollback=True),
                                'infra_bestvalid_exception_disabled')                  # v13: disabled pending evidence
        self.assertNotDerivable(T._reset_from(self, None, geom(1), status='FAILED [infra]'),
                                'infra_failure_reset_must_keep_the_input_geometry')


# ================================================================ v11 (Codex v10 review, FIX_FIRST)
class TestV11CodexV10Review(Base):
    """The three counterexamples of the Codex v10 review and its answers, each written first against v10."""

    # 1. a guard-only first execution of a new attempt cannot bypass the rescue authorization
    def _guard(self, record=True, auth=('R-G', 8, 8, 0, 'no'), retry=7):
        w = World(self.sub())
        s0 = w.segment('g', 's0', 3000, RELAX_NL, geom(0), [(None, -5.0, forces(0)), (geom(1), -5.0001, forces(1))],
                       term='2026-10-10T12:00:00Z')
        g0 = w.guard_segment('g', 's0', 3001, RELAX_NL, geom(1), '2026-10-12T01:00:00Z', attempt=2)
        s1 = w.segment('g', 's1', 3002, RELAX_NL, geom(1), [(None, -5.0001, forces(1)), (geom(2), -5.0002, forces(2))],
                       final=geom(2), term='2026-10-13T12:00:00Z', attempt=2)
        if record:
            g0['transition_record'] = w.transition_record('g/r.tr', 'g', 'section3_rescue', 'relax_s0', 1,
                                                          '2026-10-11T12:00:00Z', s0['archives'], auth=auth)
            if retry is not None:
                g0['rescue_file'] = w.rescue_file('g/g.dag.rescue001', retry)
        reg = {'R-G': {'run': 'g', 'after_attempt': 1, 'basis': 'suspension', 'pause_started_utc': '2026-10-10T13:00:00Z',
                       'rule_logged_utc': '2026-10-10T12:30:00Z'}}

        def fn(registry=reg):
            with _Registry(REGISTERED_RESCUE_AUTHORIZATIONS=registry):
                return w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_0p7_s1', 'route': 'registered-MV'},
                             {'segments': [s0, g0, s1], 'offset_evidence': w.tz})
        return w, fn

    def test_v11_1_guard_only_first_execution_cannot_bypass_the_rescue(self):
        w, fn = self._guard()
        fn()                                                       # control: authorized rescue on the guard-only attempt
        self.assertEqual([x['segment'] for x in jload(w.p['lin'])['derived']['guard_only_attempts']], ['a2.s0'])
        self.assertNotDerivable(self._guard(record=False)[1], 'attempt_change_without_rescue_record')     # Codex case
        self.assertNotDerivable(lambda: self._guard()[1]({}), 'rescue_without_a_registered_authorization')

    # answer 1: DAGMAN_RESET_RETRIES_UPON_RESCUE = False AND count enforcement: the rescue file's remaining RETRY is bound
    def test_v11_rescue_file_retry_within_the_preserved_budget(self):
        self.assertNotDerivable(self._guard(retry=8)[1], 'rescue_file_retry_exceeds_the_preserved_budget')   # 9 > 8
        self.assertNotDerivable(self._guard(retry=None)[1], 'rescue_without_its_rescue_file')

    # answer 2: the A15-era rescue is recorded separately (its contemporaneous authorization), never as A39's +9
    HIST = {'run': 'm', 'after_attempt': 1, 'basis': 'historical_rescue', 'additional_executions': 9,
            'authorization_ref': 'A15 rescue (README_D24_BD.txt:116-125; user go 2026-10-11)', 'rule_logged_utc': '2026-10-11T00:30:00Z'}

    def test_v11_historical_rescue_is_recorded_separately(self):
        R = TestV10CodexV9Review._r
        R(self, self.HIST, auth=('R-TEST', 6, 15, 0, 'no'))()
        self.assertNotDerivable(R(self, dict(self.HIST, authorization_ref=''), auth=('R-TEST', 6, 15, 0, 'no')),
                                'historical_rescue_without_its_contemporaneous_authorization')
        self.assertNotDerivable(R(self, dict(self.HIST, rule_logged_utc='2026-10-15T07:00:00Z'), auth=('R-TEST', 6, 15, 0, 'no')),
                                'historical_rescue_without_its_contemporaneous_authorization')
        self.assertNotDerivable(self._a39_after_historical(), 'rescue_without_exhaustion_of_the_previous_attempt')

    def _a39_after_historical(self):
        """the A15-era rescue is not A39's: A39 stays available once, but A39 cannot be named for the historical rescue"""
        return R_A39(self)

    # 2. a partial split (In split, O unsplit, or the converse) fails: both registered alternating splits are required
    def test_v11_2_partial_split_fails(self):
        in_only = pw6(['In1', 'In2', 'O', 'O', 'W', 'H'], [('In1',) + IN[1:], ('In2',) + IN[1:], O, W_, H_])
        o_only = pw6(['In', 'In', 'O1', 'O2', 'W', 'H'], [IN, ('O1',) + O[1:], ('O2',) + O[1:], W_, H_])
        for bad in (in_only, o_only):
            self.assertEqual(F.label_split_problem('aIWO_2p0_s1', bad), 'label_split_not_the_registered_construction')
            self.assertEqual(F.split_construction_problem('aIWO_2p0_s1', 'A30', bad, pw6(*UNSPLIT6)),
                             'label_split_not_the_registered_construction')
        self.assertNotDerivable(TestV9CodexV8Review._split(self, 'aIWO_2p0_s1', ['In1', 'W', 'O', 'H']),
                                'label_split_not_the_registered_construction')

    # answer 3: the resource route is bound to the same cluster's request, Requirements and environment
    def test_v11_resource_route_evidence(self):
        T = TestV9CodexV8Review
        lab = ['In1', 'W', 'O1', 'H']
        T._split(self, 'aIWO_2p0_s1', lab)()                                     # control
        self.assertNotDerivable(T._split(self, 'aIWO_2p0_s1', lab, resource='missing'), 'label_split_without_resource_evidence')
        self.assertNotDerivable(T._split(self, 'aIWO_2p0_s1', lab, resource={'cluster': 97}), 'resource_evidence_for_another_cluster')
        for bad in ({'gpus': 2}, {'requirements': 'regexp("H100", GPUs_DeviceName)'},
                    {'environment': 'HOME=/afs/x QE_NK=1'}):
            self.assertNotDerivable(T._split(self, 'aIWO_2p0_s1', lab, resource=bad), 'resource_route_not_the_registered_execution')

    # 3. G*: the registered minimum and tie rules over ALL eligible evaluations, before deduplication
    def test_v11_3_gstar_minimum_before_deduplication(self):
        w = World(self.sub())
        s0 = w.segment('gs', 's0', 4100, GAUSS_NL, geom(0), [(None, -2.0, forces(0)), (geom(1), -2.1, forces(1))],
                       term='2026-10-15T00:00:00Z')
        s1 = w.segment('gs', 's1', 4101, GAUSS_NL, geom(1), [(None, -2.0, forces(1)), (geom(2), -2.05, forces(2))],
                       term='2026-10-16T00:00:00Z')
        w.rec('sel', 'cutoff_selection', {'cell': 'aIO_2p0_s1'}, {'segments': [s0, s1], 'offset_evidence': w.tz})
        d = jload(w.p['sel'])['derived']
        self.assertEqual((d['g_star']['segment'], d['g_star']['index'], d['g_star']['F_Ry']), ('s0', 1, -2.1))


def R_A39(self):
    """attempt 1 (3 executions) -> historical A15-era rescue (+9, its own authorization) -> a second rescue naming A39
    is refused: the historical rescue is not A39's exhaustion rescue, and the allowance is not exhausted (14 remain)"""
    w, fn = TestV9CodexV8Review._rescue(self, auth=('R-TEST', 6, 15, 0, 'no'), third=('A39', 14, 23, 1, 'no'))
    return lambda: TestV9CodexV8Review._with(self, {'R-TEST': TestV11CodexV10Review.HIST}, fn)


# ================================================================ v12 (Codex v11 review, FIX_FIRST)
class TestV12CodexV11Review(Base):
    """The three gaps of the Codex v11 review and the false rejection, each written first against v11."""
    T = None

    # 1. resource predicates: the permitted Requirements structure and unique environment values
    def test_v12_1_requirements_structure_cannot_be_bypassed(self):
        S = TestV9CodexV8Review._split
        lab = ['In1', 'W', 'O1', 'H']
        ok_req = ('(PreVerRequirements) && regexp("H100", TARGET.GPUs_DeviceName) && !regexp("MIG", TARGET.GPUs_DeviceName) && '
                  '(GPUs_GlobalMemoryMb >= 94000)')                                 # v13: audited attribute
        S(self, 'aIWO_2p0_s1', lab, resource={'requirements': ok_req})()                   # control: extra conjuncts only narrow
        for bad in ('true || (regexp("H100", GPUs_DeviceName) && !regexp("MIG", GPUs_DeviceName))',
                    '!regexp("H100", GPUs_DeviceName) && !regexp("MIG", GPUs_DeviceName)',
                    'regexp("H100", GPUs_DeviceName) && !regexp("MIG", GPUs_DeviceName) || (Cpus > 0)',
                    '(regexp("H100", GPUs_DeviceName) || regexp("A100", GPUs_DeviceName)) && !regexp("MIG", GPUs_DeviceName)',
                    'regexp("H100", GPUs_DeviceName) && !(!regexp("MIG", GPUs_DeviceName))'):
            self.assertNotDerivable(S(self, 'aIWO_2p0_s1', lab, resource={'requirements': bad}),
                                    'resource_route_not_the_registered_execution')

    def test_v12_1_environment_values_are_unique(self):
        S = TestV9CodexV8Review._split
        lab = ['In1', 'W', 'O1', 'H']
        for env in ('HOME=/afs/x QE_NK=1 NV_ACC_MEM_MANAGE=0 NV_ACC_MEM_MANAGE=1', 'HOME=/afs/x QE_NK=2 NV_ACC_MEM_MANAGE=0 QE_NK=1'):
            self.assertNotDerivable(S(self, 'aIWO_2p0_s1', lab, resource={'environment': env}),
                                    'resource_route_not_the_registered_execution')

    def test_v12_1_a29_permits_nv_acc_mem_manage_for_aio_2p0_s1(self):
        """the false rejection: A29 supersedes A25's exclusion of NV_ACC_MEM_MANAGE=0 for aIO_2p0_s1 (register line 632)"""
        S = TestV9CodexV8Review._split
        S(self, 'aIO_2p0_s1', ['In1', 'W', 'O1', 'H'], route='A25')()                       # A29 environment (with the variable)
        S(self, 'aIO_2p0_s1', ['In1', 'W', 'O1', 'H'], route='A25', resource={'environment': 'HOME=/afs/x QE_NK=1'})()

    # 2. guard-only rescues keep their authorization; terminal-status checks apply at administrative boundaries
    def _a36_fail(self, then='continue', auth=('R-T', 7, 7, 0, 'no')):
        w = World(self.sub())
        MVA = nl(RELAX_NL, **AIDS)
        s0 = w.segment('t', 's0', 5000, RELAX_NL, geom(0), [(None, -2000.0, forces(0)), (geom(1), -2000.001, forces(1))],
                       term='2026-10-12T09:00:00Z')
        s1 = w.segment('t', 's1', 5001, MVA, geom(1), [(None, -2000.0011, forces(1)), (geom(2), -2000.0015, forces(2))],
                       term='2026-10-13T09:00:00Z', scf_fail=True, status='FAILED [scf]', bestvalid=geom(2))   # A36 one attempt
        segs = [s0, s1]
        if then == 'continue':                          # ordinary continuation from the returned input after the failure
            segs.append(w.segment('t', 's2', 5002, MVA, geom(1), [(None, -2000.0011, forces(1)), (geom(3), -2000.0016, forces(3))],
                                  final=geom(3), term='2026-10-14T09:00:00Z'))
        else:                                           # attempt 2 starts with a guard-only node attempt (rescue record)
            g0 = w.guard_segment('t', 's0', 5003, MVA, geom(1), '2026-10-14T01:00:00Z', attempt=2)
            g0['transition_record'] = w.transition_record('t/r.tr', 't', 'section3_rescue', 'relax_s1', 1,
                                                          '2026-10-13T12:00:00Z', s0['archives'] + s1['archives'], auth=auth)
            g0['rescue_file'] = w.rescue_file('t/t.dag.rescue001', 0)
            r1 = w.segment('t', 's1', 5004, MVA, geom(1), [(None, -2000.0011, forces(1)), (geom(3), -2000.0016, forces(3))],
                           final=geom(3), term='2026-10-15T09:00:00Z', attempt=2)
            segs += [g0, r1]
        reg = {'R-T': {'run': 't', 'after_attempt': 1, 'basis': 'suspension', 'pause_started_utc': '2026-10-13T10:00:00Z',
                       'rule_logged_utc': '2026-10-13T09:30:00Z'}}

        def fn():
            with _Registry(REGISTERED_RESCUE_AUTHORIZATIONS=reg):
                return w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_2p0_comp_s1', 'route': 'A36'},
                             {'segments': segs, 'offset_evidence': w.tz})
        return fn

    def test_v12_2_no_continuation_after_an_a36_scf_failure(self):
        self.assertNotDerivable(self._a36_fail('continue'), 'continuation_after_a_terminal_rescue_failure')

    def test_v12_2_guard_only_rescue_keeps_terminal_status_checks(self):
        self.assertNotDerivable(self._a36_fail('guard'), 'transition_after_a_terminal_rescue_failure')
        self.assertNotDerivable(self._a36_fail('guard', auth=('R-T', 7, 7, 0, 'yes')), 'transition_after_a_terminal_rescue_failure')

    def test_v12_2_guard_only_rescue_restated_status_is_checked(self):
        w, fn = TestV11CodexV10Review._guard(self, auth=('R-G', 8, 8, 0, 'yes'))
        self.assertNotDerivable(fn, 'rescue_terminal_failure_status_differs')
        w, fn = TestV11CodexV10Review._guard(self)
        fn()
        g = jload(w.p['lin'])['derived']['guard_only_attempts'][0]
        self.assertEqual((g['continuation'], (g.get('rescue_record') or {}).get('remaining_after')), ('section3_rescue', 8))

    # 3. the [infra] bestvalid exception: registered scope (D-37 / A34(ii) chains) and restoration evidence
    def test_v12_3_infra_bestvalid_exception_scope_and_evidence(self):
        R = TestV9CodexV8Review._reset_from
        for kw in ({'rollback': True}, {}, {'rollback': True, 'cell': 'aIWO_0p8_s2'},
                   {'rollback': True, 'rollback_logged': '2026-10-10T16:00:00Z'}):   # v13: every use refused (disabled)
            self.assertNotDerivable(R(self, geom(1), geom(1), status='FAILED [infra]', **kw), 'infra_bestvalid_exception_disabled')


# ================================================================ v13 (Codex v12 review, FIX_FIRST; A43 count enforcement)
class TestV13CodexV12Review(Base):
    """The Codex v12 counterexamples, the safe A36 continuation rejection, and the A43 count-enforcement checks, each written
    first against v12."""
    LAB = ['In1', 'W', 'O1', 'H']
    H = 'regexp("H100", TARGET.GPUs_DeviceName)'
    M = '!regexp("MIG", TARGET.GPUs_DeviceName)'

    # 1. escape-aware Requirements parsing; both predicates on the audited GPU attribute
    def test_v13_1_ternary_and_escaped_quotes_cannot_widen_the_match(self):
        S = TestV9CodexV8Review._split
        S(self, 'aIWO_2p0_s1', self.LAB, resource={'requirements': f'(PreVerRequirements) && {self.H} && {self.M}'})()   # control
        for bad in (f'{self.H} && {self.M} && true ? true : true',
                    f'{self.H} && {self.M} && regexp("a\\"", Name) || true || regexp("\\"b", Name)',
                    f'{self.H} && {self.M} && (Cpus > 0) ? true : false'):
            self.assertNotDerivable(S(self, 'aIWO_2p0_s1', self.LAB, resource={'requirements': bad}),
                                    'resource_route_not_the_registered_execution')

    def test_v13_1_both_predicates_on_the_audited_gpu_attribute(self):
        S = TestV9CodexV8Review._split
        for bad in ('regexp("H100", MY.JobBatchName) && !regexp("MIG", MY.JobBatchName)',
                    'regexp("H100", TARGET.GPUs_DeviceName) && !regexp("MIG", TARGET.Machine)',
                    'regexp("H100", GPUs_DeviceName) && !regexp("MIG", GPUs_DeviceName)'):     # unaudited form (not yet seen)
            self.assertNotDerivable(S(self, 'aIWO_2p0_s1', self.LAB, resource={'requirements': bad}),
                                    'resource_route_not_the_registered_execution')

    # 2. a rollback record that names an unregistered route is not restoration evidence: the exception stays disabled
    def test_v13_2_unregistered_rollback_route_is_refused(self):
        w_fn = TestV9CodexV8Review._reset_from(self, geom(1), geom(1), status='FAILED [infra]', rollback=True)
        self.assertNotDerivable(w_fn, 'infra_bestvalid_exception_disabled')

    # 3. the registered scientific position survives administrative renumbering (A36 continuation at a2.s0)
    def _a36_resume(self, extra_pre=False):
        w = World(self.sub())
        MVA = nl(RELAX_NL, **AIDS)
        segs = [w.segment('p', 's0', 6000, RELAX_NL, geom(0), [(None, -2000.0, forces(0)), (geom(1), -2000.001, forces(1))],
                          term='2026-10-12T09:00:00Z', scf_fail=True, status='FAILED [scf]', bestvalid=geom(1))]
        k0 = 1
        if extra_pre:                                   # an extra original-settings segment: the rescue would sit at position 2
            segs[0] = w.segment('p', 's0', 6000, RELAX_NL, geom(0), [(None, -2000.0, forces(0)), (geom(1), -2000.001, forces(1))],
                                term='2026-10-11T09:00:00Z')
            segs.append(w.segment('p', 's1', 6005, RELAX_NL, geom(1), [(None, -2000.001, forces(1)), (geom(1), -2000.001, forces(1))],
                                  term='2026-10-12T09:00:00Z', scf_fail=True, status='FAILED [scf]', bestvalid=geom(1)))
            k0 = 2
        r0 = w.segment('p', 's0', 6001, MVA, geom(1), [(None, -2000.0011, forces(1)), (geom(2), -2000.0012, forces(2))],
                       term='2026-10-15T12:00:00Z', attempt=2)
        r0['transition_record'] = w.transition_record('p/r.tr', 'p', 'section3_rescue', f'relax_s{k0 - 1}', 1, '2026-10-13T12:00:00Z',
                                                      [a for x in segs for a in x['archives']], auth=('R-P', 9 - k0, 9 - k0, 0, 'no'))
        r0['rescue_file'] = w.rescue_file('p/p.dag.rescue001', 0)
        r1 = w.segment('p', 's1', 6002, MVA, geom(2), [(None, -2000.0012, forces(2)), (geom(3), -2000.00121, forces(3))],
                       final=geom(3), term='2026-10-16T12:00:00Z', attempt=2)
        reg = {'R-P': {'run': 'p', 'after_attempt': 1, 'basis': 'suspension', 'pause_started_utc': '2026-10-13T03:13:17Z',
                       'rule_logged_utc': '2026-10-13T03:00:00Z'}}

        def fn():
            with _Registry(REGISTERED_RESCUE_AUTHORIZATIONS=reg):
                return w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_2p0_comp_s1', 'route': 'A36'},
                             {'segments': segs + [r0, r1], 'offset_evidence': w.tz})
        return w, fn

    def test_v13_3_a36_continuation_keeps_its_scientific_position(self):
        w, fn = self._a36_resume()
        fn()
        d = jload(w.p['lin'])['derived']
        self.assertEqual(([(e['segment'], e['amendment'], e['rescue']) for e in d['epoch_starts']], d['required_gates']),
                         ([('a2.s0', 'A36', True)], ['a2.s0->a2.s1']))
        self.assertNotDerivable(self._a36_resume(extra_pre=True)[1], 'settings_change_without_authorized_epoch_start')

    # 4. A43 count enforcement (count-enforcement draft section 5): DAG identity, config, exact RETRY, dry run, header
    CONT = None

    def _c(self, **kw):
        return TestV10CodexV9Review._r(self, dict(TestV10CodexV9Review.CONT), a43_kw=kw)

    def test_v13_4_a43_dag_identity_config_and_exact_retry(self):
        self._c()()                                                              # control: RETRY 5 = 6 - 1
        self.assertNotDerivable(self._c(extra_line='RETRY FINAL 2'), 'a43_dag_differs_from_the_original')
        self.assertNotDerivable(self._c(config_text='DAGMAN_RESET_RETRIES_UPON_RESCUE = True\n'), 'a43_dag_config_not_the_registered_setting')
        self.assertNotDerivable(self._c(retry=3), 'a43_dag_retry_not_exactly_the_remaining_count')

    def test_v13_4_a43_dry_run_and_dagman_header(self):
        self.assertNotDerivable(self._c(dag_in_sub='m.dag'), 'a43_dry_run_not_bound')
        self.assertNotDerivable(self._c(rescue_from=2), 'a43_dry_run_not_bound')
        self._c(dagman_retry_of=5)()                                             # v14 fixture: full header
        self.assertNotDerivable(self._c(dagman_setting='True'), 'a43_dagman_header_not_bound')
        self.assertNotDerivable(self._c(dagman_retry_of=8), 'a43_dagman_header_not_bound')


# ================================================================ v14 (Codex v13 review, FIX_FIRST)
class TestV14CodexV13Review(Base):
    """The two gaps of the Codex v13 review, each written first against v13."""

    def _c(self, **kw):
        return TestV13CodexV12Review._c(self, **kw)

    # 1. A43 submission binding: one scheduler-universe DAGMan, audited executable and run directory, permitted arguments,
    #    and the submitted DAGMan ad linked to the reviewed files (and to the first resumed RELAX node)
    def test_v14_1_dry_run_is_one_scheduler_dagman_with_permitted_arguments(self):
        self._c()()                                                               # control
        for kw in ({'queue': 'queue 2'}, {'initialdir': '/afs/cern.ch/user/m/melrashe/iwo_amorph/runs/OTHER'},
                   {'executable': '/afs/cern.ch/user/m/melrashe/bin/not_dagman'}, {'extra_args': ' -DoRecov'},
                   {'extra_args': ' -force'}, {'extra_args': ' -AutoRescue 0'}):
            self.assertNotDerivable(self._c(**kw), 'a43_dry_run_not_bound')

    def test_v14_1_submitted_dagman_ad_is_linked_to_the_reviewed_files(self):
        for kw in ({'ad': {'Arguments': '"-p 0 -f -l . -Dag m.dag"'}}, {'ad': {'JobUniverse': '5'}},
                   {'ad': {'Iwd': '"/tmp/elsewhere"'}}, {'ad': {'Cmd': '"/bin/true"'}}, {'submit_cluster': 9001}):
            self.assertNotDerivable(self._c(**kw), 'a43_submission_not_linked')
        for k in ('dagman_ad', 'submit_record', 'dagman_out'):
            self.assertNotDerivable(self._c(omit=(k,)), 'a43_count_enforcement_files_missing')
        self.assertNotDerivable(self._c(dagman_node=81), 'a43_dagman_header_not_bound')         # another node cluster
        self.assertNotDerivable(self._c(dagman=('10/15/26 08:00:00 ** condor_scheduniv_exec.9999.0 (CONDOR_DAGMAN) STARTING UP\n'
                                                '10/15/26 08:00:00 DAGMAN_RESET_RETRIES_UPON_RESCUE setting: False\n'
                                                '10/15/26 08:00:05 Event: ULOG_SUBMIT for HTCondor Node RELAX (80.0.0) {x}\n')),
                                'a43_dagman_header_not_bound')

    # 2. budget counting separate from the rescue anchor; a guard-only first resumed execution carries the pending A36
    #    bestvalid transition to the first actual SCF
    def _a36_guard_first(self, start=None):
        w = World(self.sub())
        MVA = nl(RELAX_NL, **AIDS)
        s0 = w.segment('q', 's0', 7000, RELAX_NL, geom(0), [(None, -2000.0, forces(0)), (geom(1), -2000.001, forces(1))],
                       term='2026-10-12T09:00:00Z', scf_fail=True, status='FAILED [scf]', bestvalid=geom(1))
        g0 = w.guard_segment('q', 's0', 7001, MVA, geom(1), '2026-10-15T01:00:00Z', attempt=2)
        g0['transition_record'] = w.transition_record('q/r.tr', 'q', 'section3_rescue', 'relax_s0', 1, '2026-10-13T12:00:00Z',
                                                      s0['archives'], auth=('R-Q', 8, 8, 0, 'no'))
        g0['rescue_file'] = w.rescue_file('q/q.dag.rescue001', 7)
        r1 = w.segment('q', 's1', 7002, MVA, start or geom(1), [(None, -2000.0011, forces(1)), (geom(2), -2000.0012, forces(2))],
                       term='2026-10-16T09:00:00Z', attempt=2)
        r2 = w.segment('q', 's2', 7003, MVA, geom(2), [(None, -2000.0012, forces(2)), (geom(3), -2000.00121, forces(3))],
                       final=geom(3), term='2026-10-16T21:00:00Z', attempt=2)
        reg = {'R-Q': {'run': 'q', 'after_attempt': 1, 'basis': 'suspension', 'pause_started_utc': '2026-10-13T03:13:17Z',
                       'rule_logged_utc': '2026-10-13T03:00:00Z'}}

        def fn():
            with _Registry(REGISTERED_RESCUE_AUTHORIZATIONS=reg):
                return w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_2p0_comp_s1', 'route': 'A36'},
                             {'segments': [s0, g0, r1, r2], 'offset_evidence': w.tz})
        return w, fn

    def test_v14_2_guard_only_first_execution_carries_the_a36_transition(self):
        w, fn = self._a36_guard_first()
        fn()
        d = jload(w.p['lin'])['derived']
        self.assertEqual(([(e['segment'], e['amendment'], e['rescue']) for e in d['epoch_starts']], d['required_gates'],
                          [x['continuation'] for x in d['segments']], [g['segment'] for g in d['guard_only_attempts']]),
                         ([('a2.s1', 'A36', True)], ['a2.s1->a2.s2'], [None, 'section3_rescue', 'returned_geometry'], ['a2.s0']))
        self.assertNotDerivable(self._a36_guard_first(start=geom(0) if False else geom(5))[1],
                                'reset_geometry_is_not_the_returned_or_best_valid_geometry')


# ================================================================ v15 (Codex 2026-10-14T08:59Z, checker v14 FIX_FIRST)
class TestV15CodexV14Review(Base):
    """The two submission-parser gaps of the Codex review of v14, each written first against v14."""
    BASE = ("-p 0 -f -l . -Lockfile m.a43.dag.lock -AutoRescue 1 -DoRescueFrom 0 -Dag m.a43.dag -Suppress_notification "
            "-CsdVersion $CondorVersion:' '23.0.12' '2024-06-13' 'BuildID:' '739441' '$ -Dagman /usr/bin/condor_dagman")

    def _c(self, **kw):
        return TestV13CodexV12Review._c(self, **kw)

    # 1. HTCondor argument quoting (new syntax): every resulting argument is checked
    def test_v15_1_quoted_version_argument_cannot_hide_an_option(self):
        self._c(args_override=self.BASE)()                                          # control (the generator's form)
        for args in (self.BASE.replace("-Dagman /usr/bin/condor_dagman",
                                       "-Dagman /usr/bin/condor_dagman -CsdVersion '$CondorVersion: 23.0.12 $' -DoRecov"),
                     "-p 0 -f -l . -Lockfile m.a43.dag.lock -AutoRescue 1 -DoRescueFrom 0 -Dag m.a43.dag -Suppress_notification "
                     "-CsdVersion '$CondorVersion: 23.0.12 2024 $' -DoRecov -Dagman /usr/bin/condor_dagman",
                     self.BASE + " 'unterminated",
                     self.BASE.replace("-DoRescueFrom 0", "-DoRescueFrom '0' -DoRescueFrom 2")):
            self.assertNotDerivable(self._c(args_override=args), 'a43_dry_run_not_bound')

    # 2. unsupported submit directives are refused (include, conditionals, line continuation)
    def test_v15_2_unsupported_submit_directives_are_refused(self):
        for extra in (['include : /afs/cern.ch/user/m/melrashe/evil.sub'], ['include command : echo queue 5'],
                      ['if defined X', 'priority = 99', 'endif'], ['error : stop'], ['priority = 1 \\']):
            self.assertNotDerivable(self._c(extra_sub_lines=extra), 'a43_dry_run_not_bound')


# ================================================================ v16 (Codex 2026-10-14 v15 reply: the narrow Requirements resolver)
REAL_REQ = '(TARGET.Hostgroup =?= "bi/condor/gridworker/gpu") && PreGPURequirements'
REAL_HELPERS = {   # captured read-only from 12920318.0 (condor_q -l, 2026-10-14T09:32Z), verbatim
    'PreAfsRequirements': '(NODE_MOUNTS_CVMFS || CvmfsCustomExpression) && PreCvmfsRequirements',
    'PreCvmfsRequirements': '(OpSysAndVer =?= "AlmaLinux9") && PreVerRequirements',
    'PreGPURequirements': '(TARGET.NODE_MOUNTS_AFS =?= true) && PreAfsRequirements',
    'PreVerRequirements': ('(regexp("H100",TARGET.GPUs_DeviceName) &&  !regexp("MIG",TARGET.GPUs_DeviceName)) && (TARGET.Arch == "X86_64") && '
                           '(TARGET.OpSys == "LINUX") && (TARGET.Disk >= RequestDisk) && (TARGET.Memory >= RequestMemory) && '
                           '(TARGET.Cpus >= RequestCpus) && (TARGET.GPUs >= RequestGPUs) && (TARGET.HasFileTransfer)')}


class TestV16RequirementsResolver(Base):
    """Codex's narrow rule: one complete ad per cluster.proc; case-insensitive single definitions; expand only positive whole
    && conjuncts defined in the same ad; both audited predicates as mandatory conjuncts after expansion; no evidence through
    OR, negation, conditionals, eval, quoted or TARGET.<helper> references; missing or cyclic helpers are UNRESOLVED."""
    LAB = ['In1', 'W', 'O1', 'H']

    def _s(self, req=REAL_REQ, helpers=None, extra='', route='A30', cell='aIWO_2p0_s1'):
        return TestV9CodexV8Review._split(self, cell, self.LAB, route=route,
                                         resource={'requirements': req, 'helpers': REAL_HELPERS if helpers is None else helpers,
                                                   'extra': extra})

    def test_v16_real_captured_chain_resolves(self):
        self._s()()                                                                # the real CERN chain, 4 helpers deep
        ad = {k.lower(): v for k, v in dict(REAL_HELPERS, Requirements=REAL_REQ).items()}
        atoms, path = F.mandatory_conjuncts(ad, 'requirements')
        self.assertEqual(path, ['requirements', 'pregpurequirements', 'preafsrequirements', 'precvmfsrequirements',
                                'preverrequirements'])
        self.assertIn('regexp("H100",TARGET.GPUs_DeviceName)', atoms)
        self.assertIn('!regexp("MIG",TARGET.GPUs_DeviceName)', atoms)

    def test_v16_my_prefix_and_case_insensitive_names(self):
        self._s(req=REAL_REQ.replace('PreGPURequirements', 'MY.pregpurequirements'))()

    def test_v16_missing_or_cyclic_helpers_are_unresolved(self):
        h = dict(REAL_HELPERS); del h['PreCvmfsRequirements']
        self.assertNotDerivable(self._s(helpers=h), 'resource_route_unresolved')
        h = dict(REAL_HELPERS, PreVerRequirements=REAL_HELPERS['PreVerRequirements'] + ' && PreGPURequirements')
        self.assertNotDerivable(self._s(helpers=h), 'resource_route_unresolved')

    def test_v16_duplicate_definitions_after_case_folding(self):
        self.assertNotDerivable(self._s(extra='preverrequirements = (TARGET.Arch == "X86_64")\n'), 'resource_evidence_malformed')

    def test_v16_no_evidence_through_or_negation_conditional_eval_or_target(self):
        for req in ('(TARGET.Hostgroup =?= "x") || PreGPURequirements', '(TARGET.Hostgroup =?= "x") && !PreGPURequirements',
                    'true ? PreGPURequirements : false', '(TARGET.Hostgroup =?= "x") && TARGET.PreGPURequirements',
                    '(TARGET.Hostgroup =?= "x") && eval("PreGPURequirements")', '(TARGET.Hostgroup =?= "x") && "PreGPURequirements"',
                    '(TARGET.Hostgroup =?= "x") && (PreGPURequirements || true)'):
            self.assertNotDerivable(self._s(req=req), 'resource_route_not_the_registered_execution')
        h = dict(REAL_HELPERS, PreVerRequirements=REAL_HELPERS['PreVerRequirements'] + ' || true')       # helper with OR
        self.assertNotDerivable(self._s(helpers=h), 'resource_route_not_the_registered_execution')

    def test_v16_scope_and_request_checks_kept(self):
        self.assertNotDerivable(self._s(route='A25'), 'label_split_outside_the_registered_scope')
        self.assertNotDerivable(self._s(cell='aIWO_0p7_s1'), 'label_split_outside_the_registered_scope')

    def test_v16_one_complete_ad_per_cluster_proc(self):
        self.assertNotDerivable(self._s(extra='ProcId = 1\n'), 'resource_evidence_malformed')            # two ads glued


# ================================================================ v17 (Codex 2026-10-14 v16 reply: comments hide a top-level ||)
PRED = 'regexp("H100",TARGET.GPUs_DeviceName) && !regexp("MIG",TARGET.GPUs_DeviceName)'
CODEX_V16_TAIL = ' && true /* " */ || true /* " */'      # Codex's reproduced counterexample, verbatim


class TestV17CodexV16Review(Base):
    """ClassAd /* */ and // comments are removed before evaluation; a scanner that reads the quotation marks inside them as
    strings hides an unrestricted || true. Comment delimiters outside string literals are refused in every traversed
    expression (the Requirements and each expanded helper); inside string literals they are ordinary characters."""
    LAB = TestV16RequirementsResolver.LAB

    def _s(self, req=REAL_REQ, helpers=None):
        return TestV16RequirementsResolver._s(self, req=req, helpers=helpers)

    def test_v17_codex_counterexample_in_requirements(self):
        req = PRED + CODEX_V16_TAIL
        self.assertNotDerivable(self._s(req=req, helpers={}), 'resource_route_not_the_registered_execution')
        self.assertIsNotNone(F.requirements_problem(req))
        with self.assertRaises(ValueError):
            F.mandatory_conjuncts({'requirements': req}, 'requirements')

    def test_v17_counterexample_inside_an_expanded_helper(self):
        h = dict(REAL_HELPERS, PreVerRequirements=REAL_HELPERS['PreVerRequirements'] + CODEX_V16_TAIL)
        self.assertNotDerivable(self._s(helpers=h), 'resource_route_not_the_registered_execution')
        h = dict(REAL_HELPERS, PreAfsRequirements=REAL_HELPERS['PreAfsRequirements'] + CODEX_V16_TAIL)
        self.assertNotDerivable(self._s(helpers=h), 'resource_route_not_the_registered_execution')

    def test_v17_any_comment_delimiter_outside_strings_is_refused(self):
        for tail in (' /* c */', ' // " || true "', ' && true */', ' && (true /* x */)', '/**/'):
            self.assertNotDerivable(self._s(req=REAL_REQ + tail), 'resource_route_not_the_registered_execution')
            self.assertIsNotNone(F.requirements_problem(PRED + tail))

    def test_v17_delimiters_inside_string_literals_are_characters(self):
        req = REAL_REQ.replace('"bi/condor/gridworker/gpu"', '"bi//condor/*grid*/worker/gpu"')
        self._s(req=req)()                                                   # still resolves
        self.assertIsNone(F.requirements_problem(PRED + ' && (TARGET.Hostgroup =?= "a/*b*/c//d")'))
        self._s()()                                                          # the real captured chain is unaffected


# ================================================================ v18 (Codex 2026-10-14 v17 reply: quoted names, nested records)
CODEX_V17_QUOTED = PRED + " && 'x\"' || true || 'y\"'"                       # quoted attribute names hide || true
CODEX_V17_RECORD = '[ x = true; y = true && ' + PRED + ' && true ].x'        # predicates credited inside an unused field


class TestV18CodexV17Review(Base):
    """The narrow supported grammar: single-quote delimiters (quoted attribute names), square brackets (records, indexing)
    and curly braces (lists) outside double-quoted strings are refused in every traversed expression, without implementing
    their semantics. Inside double-quoted strings they are ordinary characters."""
    LAB = TestV16RequirementsResolver.LAB

    def _s(self, req=REAL_REQ, helpers=None):
        return TestV16RequirementsResolver._s(self, req=req, helpers=helpers)

    def test_v18_codex_quoted_attribute_names(self):
        self.assertNotDerivable(self._s(req=CODEX_V17_QUOTED, helpers={}), 'resource_route_not_the_registered_execution')
        self.assertIsNotNone(F.requirements_problem(CODEX_V17_QUOTED))
        with self.assertRaises(ValueError):
            F.mandatory_conjuncts({'requirements': CODEX_V17_QUOTED}, 'requirements')
        h = dict(REAL_HELPERS, PreVerRequirements=REAL_HELPERS['PreVerRequirements'] + " && 'x\"' || true || 'y\"'")
        self.assertNotDerivable(self._s(helpers=h), 'resource_route_not_the_registered_execution')

    def test_v18_codex_nested_record(self):
        self.assertNotDerivable(self._s(req=CODEX_V17_RECORD, helpers={}), 'resource_route_not_the_registered_execution')
        self.assertIsNotNone(F.requirements_problem(CODEX_V17_RECORD))
        with self.assertRaises(ValueError):
            F.mandatory_conjuncts({'requirements': CODEX_V17_RECORD}, 'requirements')
        h = dict(REAL_HELPERS, PreGPURequirements='(TARGET.NODE_MOUNTS_AFS =?= true) && [ x = true; y = true && '
                                                     'PreAfsRequirements ].x')
        self.assertNotDerivable(self._s(helpers=h), 'resource_route_not_the_registered_execution')
        h = dict(REAL_HELPERS, PreVerRequirements=CODEX_V17_RECORD)
        self.assertNotDerivable(self._s(helpers=h), 'resource_route_not_the_registered_execution')

    def test_v18_other_forms_outside_strings_are_refused(self):
        for tail in (" && 'Name'", ' && {1, 2}', ' && TARGET.X[0]', ' && ]', ' && }', " && (TARGET.Arch == 'X86_64')"):
            self.assertNotDerivable(self._s(req=REAL_REQ + tail), 'resource_route_not_the_registered_execution')
            self.assertIsNotNone(F.requirements_problem(PRED + tail))

    def test_v18_characters_inside_double_quoted_strings_are_kept(self):
        req = REAL_REQ.replace('"bi/condor/gridworker/gpu"', '"bi/condor/\'grid[worker]{gpu}\'"')
        self._s(req=req)()                                                   # still resolves
        self.assertIsNone(F.requirements_problem(PRED + ' && (TARGET.Hostgroup =?= "a\'b[c]{d}")'))
        self._s()()                                                          # the real captured chain is unaffected


# ================================================================ v19 (Codex 2026-10-14: the A15/D-26 transition of aIO_1p0_s1)
A15_NL = nl(GAUSS_NL, **AIDS)                       # D-26: Gaussian 0.005, beta 0.1, ndim 12, maxstep 300


def a15_world(root, cell='aIO_1p0_s1', route='registered-Gaussian', s1_nl=None, blocks=None, s1_scf_fail=False, three=False,
              mv_s1_then_gauss_s2=False):
    """MV s0 -> (D-26 A15 rollout) Gaussian + aids s1 (-> s2 if `three`), A26 FINAL at the final geometry, certificate.
    s1_scf_fail: s1 has an SCF failure and an old-rule continuation (the returned relax.in moves on), s2 converges.
    mv_s1_then_gauss_s2: the settings change happens at s2 instead of s1 (not the registered segment)."""
    w = World(root)
    segs = [w.segment('a', 's0', 100, RELAX_NL, geom(0), [(None, -1000.0, forces(0)), (geom(1), -1000.001, forces(1))],
                      term='2026-10-11T08:00:00Z')]
    g1 = RELAX_NL if mv_s1_then_gauss_s2 else (s1_nl or A15_NL)
    if three or mv_s1_then_gauss_s2:
        segs.append(w.segment('a', 's1', 101, g1, geom(1), [(None, -1000.0011, forces(1)), (geom(2), -1000.0012, forces(2))],
                              term='2026-10-11T14:00:00Z', scf_fail=s1_scf_fail, returned=geom(2) if s1_scf_fail else None,
                              status='CONTINUE' if s1_scf_fail else None))
        segs.append(w.segment('a', 's2', 102, s1_nl or A15_NL, geom(2),
                              [(None, -1000.00121, forces(2)), (geom(3), -1000.00125, forces(3))], final=geom(3),
                              term='2026-10-11T20:00:00Z'))
        last = geom(3)
    else:
        segs.append(w.segment('a', 's1', 101, g1, geom(1), [(None, -1000.0011, forces(1)), (geom(2), -1000.00115, forces(2))],
                              final=geom(2), term='2026-10-11T14:00:00Z'))
        last = geom(2)
    w.rec('lin', 'relaxation_lineage', {'cell': cell, 'route': route}, {'segments': segs, 'offset_evidence': w.tz})
    f = w.final('final', FINAL_NL, last, cluster=600)
    w.cert('cert', cell, f['rf'], f['g'], blocks or {'relaxation': ('converged', ['lin'])})
    return w


class TestV19A15HistoricalTransition(Base):
    """D-26 (A15 rollout; commit 109ea25, 2026-10-11T06:51:50Z, before aIO_1p0_s1's s0 ended and s1 executed) authorizes
    exactly one settings change: aIO_1p0_s1, s1, route registered-Gaussian, the five A15 keys to their exact values. It is
    a historical transition (rescue start False): no A35-style qualification SCF or restart gate; the D-24 failure rules and
    the MV-then-Gaussian history stay; the history establishes neither 'mv' nor 'polished' geometry."""

    def test_v19_a15_d26_transition_is_authorized_without_qualification_or_gates(self):
        w = a15_world(self.sub())
        res = self.check(w, cert='cert')
        self.assertEqual(res['verdict'], 'CLAIMS_OK', json.dumps(res, indent=1))
        d = jload(w.p['lin'])['derived']
        self.assertEqual(d['epoch_starts'], [{'segment': 's1', 'amendment': 'A15-D26', 'changed_keys': sorted(
            ['system.smearing', 'system.degauss', 'electrons.mixing_beta', 'electrons.mixing_ndim',
             'electrons.electron_maxstep']), 'rescue': False, 'historical': True}])
        self.assertEqual(d['required_gates'], [])
        self.assertEqual([h['smearing'] for h in d['smearing_history']], ['mv', 'gaussian'])     # history kept
        self.assertFalse(CA.qualification_needed(d))
        self.assertTrue(any('A15-D26' in n and 'historical' in n for n in res['blocks']['relaxation']['notes']),
                        res['blocks']['relaxation']['notes'])

    def test_v19_scope_is_exactly_the_registered_transition(self):
        self.assertNotDerivable(lambda: a15_world(self.sub(), cell='aIO_0p7_s1'),
                                'settings_change_without_authorized_epoch_start')            # no verifiable authorization
        self.assertNotDerivable(lambda: a15_world(self.sub(), route='registered-MV'),
                                'settings_change_without_authorized_epoch_start')
        self.assertNotDerivable(lambda: a15_world(self.sub(), mv_s1_then_gauss_s2=True),
                                'settings_change_without_authorized_epoch_start')            # not at s1
        self.assertNotDerivable(lambda: a15_world(self.sub(), s1_nl=nl(A15_NL, system__degauss='0.01')),
                                'epoch_start_state_differs_from_the_registered_state')
        self.assertNotDerivable(lambda: a15_world(self.sub(), s1_nl=nl(A15_NL, electrons__mixing_ndim='8')),
                                'epoch_start_state_differs_from_the_registered_state')
        self.assertNotDerivable(lambda: a15_world(self.sub(), s1_nl=nl(A15_NL, electrons__conv_thr='1.0d-8')),
                                'epoch_start_changes_keys_outside_the_registered_transition')

    def test_v19_mv_history_never_gives_mv_or_polished_geometry(self):
        res = self.check(a15_world(self.sub(), blocks={'relaxation': ('converged', ['lin']), 'geometry': ('mv', ['lin'])}),
                         cert='cert')
        self.assertDowngrade(res, 'geometry', 'non-MV relaxation smearing')
        self.assertEqual(res['blocks']['relaxation']['verdict'], 'OK')

    def test_v19_ordinary_d24_failure_rules_are_kept(self):
        res = self.check(a15_world(self.sub(), three=True, s1_scf_fail=True), cert='cert')
        self.assertDowngrade(res, 'relaxation', 'terminal SCF failure in the active epoch')

    def test_v19_qualification_trigger_is_narrowed_only_for_historical_transitions(self):
        h = [{'segment': 's0', 'smearing': 'mv'}, {'segment': 's1', 'smearing': 'gaussian'}]
        a15 = {'segment': 's1', 'amendment': 'A15-D26', 'rescue': False, 'historical': True}
        base = {'route': 'registered-Gaussian', 'cell': 'aIO_1p0_s1', 'smearing_history': h}
        self.assertFalse(CA.qualification_needed(dict(base, epoch_starts=[a15])))
        self.assertTrue(CA.qualification_needed(dict(base, epoch_starts=[])))                           # unexplained mix
        self.assertTrue(CA.qualification_needed(dict(base, epoch_starts=[dict(a15, amendment='A35')])))
        self.assertTrue(CA.qualification_needed(dict(base, epoch_starts=[dict(a15, rescue=True)])))
        self.assertTrue(CA.qualification_needed(dict(base, epoch_starts=[dict(a15, segment='s2')])))
        h3 = h + [{'segment': 's2', 'smearing': 'mv'}]                                                  # a second change
        self.assertTrue(CA.qualification_needed(dict(base, smearing_history=h3, epoch_starts=[a15])))
        for r in ('A35', 'A36', 'A36-conditional', 'C4-polish'):                                       # routes unchanged
            self.assertTrue(CA.qualification_needed(dict(base, route=r, epoch_starts=[a15])))
        self.assertTrue(CA.qualification_needed(dict(base, cell='aIWO_0p8_s2', epoch_starts=[a15])))


# ================================================================ v20 (Codex 2026-10-14 GPU-plan reply: freeze the actual entries)
A43_PAUSE, A43_LOGGED = '2026-10-13T03:13:17Z', '2026-10-14T09:06:10Z'    # segment_stop STOP stamp; commit 920387e (A43/D-46)


def _a43(run, after, remaining, prior):
    return {'run': run, 'after_attempt': after, 'basis': 'continuation_amendment', 'additional_executions': 0,
            'pause_started_utc': A43_PAUSE, 'rule_logged_utc': A43_LOGGED, 'result_informed': True,
            'preserved': {'remaining_executions': remaining, 'prior_rescues': prior, 'terminal_failure': False}}


EXPECTED_AUTH = {
    'D27-2-A25-aIO_2p0_s1': {'run': 'aIO_2p0_s1', 'after_attempt': 1, 'basis': 'historical_rescue',
                             'additional_executions': 9, 'authorization_ref': 'D-27 (2) / A25',
                             'rule_logged_utc': '2026-10-11T08:14:00Z'},
    'A43-aIO_2p0_s1': _a43('aIO_2p0_s1', 2, 5, 1),
    'A43-aIO_2p0_s2': _a43('aIO_2p0_s2', 1, 8, 0),
    'A43-aIWO_2p0_s1': _a43('aIWO_2p0_s1', 1, 8, 0),
    'A43-aIWO_2p0_s2': _a43('aIWO_2p0_s2', 1, 8, 0),
    'A43-aIWO_2p0_comp_s1': _a43('aIWO_2p0_comp_s1', 1, 8, 0),
}


class TestV20A43Authorizations(Base):
    """The frozen registry holds exactly the authorizations of the A43 table (1b): one A43 continuation per 2 nm
    audit-role chain (result-informed, logged 2026-10-14T09:06:10Z after the 03:13:17Z pause, +0, state preserved) and
    the contemporaneous historical rescue of aIO_2p0_s1 (D-27 (2) / A25, logged 08:14Z, before its rescue DAG's first
    execution 09:56:28Z, +9). Each is checked through the writer's own verification, at its real times."""

    @staticmethod
    def _verify(ref, remaining_before, remaining_after, prior, t_first, attempt, executions, allowance, refs=()):
        rec = {'auth': {'ref': ref, 'remaining_before': remaining_before, 'remaining_after': remaining_after,
                        'prior_rescues': prior, 'terminal_failure': False}}
        state = {'executions': executions, 'by_attempt': {}, 'refs': list(refs), 'allowance': allowance, 'clusters': set()}
        run = F.REGISTERED_RESCUE_AUTHORIZATIONS[ref]['run']
        return W._verify_rescue_authorization(rec, run, {'attempt': attempt}, state, F.parse_utc(t_first), None)

    def test_v20_registry_is_exactly_the_a43_table(self):
        self.assertEqual(F.REGISTERED_RESCUE_AUTHORIZATIONS, EXPECTED_AUTH)

    def test_v20_a43_continuations_verify_at_resumption_and_refuse_otherwise(self):
        for c in ('aIO_2p0_s2', 'aIWO_2p0_s1', 'aIWO_2p0_s2', 'aIWO_2p0_comp_s1'):
            ref = f'A43-{c}'
            self._verify(ref, 8, 8, 0, '2026-10-14T14:00:00Z', 1, 1, 9)             # 1 execution used of 9
            self.assertNotDerivable(lambda: self._verify(ref, 8, 8, 0, '2026-10-14T09:00:00Z', 1, 1, 9),
                                    'continuation_amendment_logged_after_resumption')
            self.assertNotDerivable(lambda: self._verify(ref, 9, 9, 0, '2026-10-14T14:00:00Z', 1, 0, 9),
                                    'continuation_does_not_preserve_the_state')
            self.assertNotDerivable(lambda: self._verify(ref, 8, 17, 0, '2026-10-14T14:00:00Z', 1, 1, 9),
                                    'rescue_resets_the_remaining_executions')
        # aIO_2p0_s1: 13 executions of 9 + 9 historical, one prior (historical) rescue, after attempt 2
        self._verify('A43-aIO_2p0_s1', 5, 5, 1, '2026-10-14T14:00:00Z', 2, 13, 18, refs=('D27-2-A25-aIO_2p0_s1',))
        self.assertNotDerivable(lambda: self._verify('A43-aIO_2p0_s1', 5, 5, 0, '2026-10-14T14:00:00Z', 2, 13, 18,
                                                     refs=('D27-2-A25-aIO_2p0_s1',)), 'rescue_prior_use_not_preserved')
        self.assertNotDerivable(lambda: self._verify('A43-aIO_2p0_s1', 5, 5, 0, '2026-10-14T14:00:00Z', 2, 13, 18),
                                'continuation_does_not_preserve_the_state')               # history dropped
        self.assertNotDerivable(lambda: self._verify('A43-aIO_2p0_s1', 5, 5, 1, '2026-10-14T14:00:00Z', 1, 13, 18,
                                                     refs=('D27-2-A25-aIO_2p0_s1',)),
                                'rescue_without_a_registered_authorization')                   # wrong attempt

    def test_v20_historical_rescue_of_aio_2p0_s1(self):
        ref = 'D27-2-A25-aIO_2p0_s1'
        self._verify(ref, 0, 9, 0, '2026-10-11T09:56:28Z', 1, 9, 9)                   # exhausted gen 1, +9
        self.assertNotDerivable(lambda: self._verify(ref, 0, 9, 0, '2026-10-11T08:00:00Z', 1, 9, 9),
                                'historical_rescue_without_its_contemporaneous_authorization')
        self.assertNotDerivable(lambda: self._verify(ref, 0, 18, 0, '2026-10-11T09:56:28Z', 1, 9, 9),
                                'rescue_resets_the_remaining_executions')

    def test_v20_each_authorization_is_used_once_and_only_for_its_run(self):
        self.assertNotDerivable(lambda: self._verify('A43-aIWO_2p0_s1', 8, 8, 0, '2026-10-14T14:00:00Z', 1, 1, 9,
                                                     refs=('A43-aIWO_2p0_s1',)), 'rescue_authorization_already_used')
        rec = {'auth': {'ref': 'A43-aIWO_2p0_s1', 'remaining_before': 8, 'remaining_after': 8, 'prior_rescues': 0,
                        'terminal_failure': False}}
        state = {'executions': 1, 'by_attempt': {}, 'refs': [], 'allowance': 9, 'clusters': set()}
        self.assertNotDerivable(lambda: W._verify_rescue_authorization(rec, 'aIWO_2p0_s2', {'attempt': 1}, state,
                                                                       F.parse_utc('2026-10-14T14:00:00Z'), None),
                                'rescue_without_a_registered_authorization')                   # another run


# v20: the first actual generated A43 DAGMan submission (verbatim; HTCondor 25.0.14, condor_submit_dag -no_submit)
REAL_A43_SUB = '# Filename: aIWO_2p0_comp_s1.a43.dag.condor.sub\n# Generated by condor_submit_dag aIWO_2p0_comp_s1.a43.dag \nuniverse    = scheduler\nexecutable  = /usr/bin/condor_dagman\ngetenv      = CONDOR_CONFIG,_CONDOR_*,PATH,PYTHONPATH,PERL*,PEGASUS_*,TZ,HOME,USER,LANG,LC_ALL,ASAN_OPTIONS,LSAN_OPTIONS,BEARER_TOKEN,BEARER_TOKEN_FILE,XDG_RUNTIME_DIR\noutput      = aIWO_2p0_comp_s1.a43.dag.lib.out\nerror       = aIWO_2p0_comp_s1.a43.dag.lib.err\nlog         = aIWO_2p0_comp_s1.a43.dag.dagman.log\nremove_kill_sig = SIGUSR1\nMy.OtherJobRemoveRequirements = "DAGManJobId =?= $(cluster)"\nMy.IsDaemonCore = True\n# Note: default on_exit_remove expression:\n# (ExitSignal =?= 11 || (ExitCode =!= UNDEFINED && ExitCode >=0 && ExitCode <= 2))\n# attempts to ensure that DAGMan is automatically\n# requeued by the schedd if it exits abnormally or\n# is killed (e.g., during a reboot).\non_exit_remove = (ExitSignal =?= 11 || (ExitCode =!= UNDEFINED && ExitCode >=0 && ExitCode <= 2))\ncopy_to_spool = False\narguments = "-f -l . -Lockfile aIWO_2p0_comp_s1.a43.dag.lock -Dag aIWO_2p0_comp_s1.a43.dag -CsdVersion $CondorVersion:\' \'25.0.14\' \'2026-08-30\' \'BuildID:\' \'947353\' \'PackageID:\' \'25.0.14-1\' \'$ -dagman /usr/bin/condor_dagman -AutoRescue 1 -DoRescueFrom 0"\nenvironment = "_CONDOR_DAGMAN_CONFIG_FILE=/afs/cern.ch/user/m/melrashe/iwo_amorph/runs/aIWO_2p0_comp_s1/a43_dagman.config _CONDOR_DAGMAN_LOG=aIWO_2p0_comp_s1.a43.dag.dagman.out _CONDOR_MAX_DAGMAN_LOG=0 _CONDOR_SCHEDD_ADDRESS_FILE=/var/lib/condor/spool/.schedd_address _CONDOR_SCHEDD_DAEMON_AD_FILE=/var/lib/condor/spool/.schedd_classad"\nqueue\n'


class TestV20RealA43Submission(Base):
    """Codex 2026-10-14 (GPU-plan reply item 4): audit one actual generated DAGMan submission with the checker grammar.
    The real 25.0.14 file spells the DAGMan option '-dagman' (lower case), has the 25.0.14 CsdVersion and no
    My.JobBatchName line. Only that observed spelling is added; every other option, value and case variant stays refused."""
    RUN = 'aIWO_2p0_comp_s1'

    def _grammar(self, text):
        w = World(self.sub())
        sub = w.write('real.condor.sub', text)
        empty = w.write('empty.txt', '')
        return F.a43_submission_problem(sub, f'{self.RUN}.a43.dag', self.RUN, empty, empty, empty, 0, 7)

    def test_v20_real_generated_submission_passes_the_grammar(self):
        self.assertEqual(self._grammar(REAL_A43_SUB), 'a43_submission_not_linked')      # grammar OK; not yet submitted

    def test_v20_variants_of_the_real_file_stay_refused(self):
        for old, new in (('-dagman /usr/bin/condor_dagman', '-DAGMAN /usr/bin/condor_dagman'),
                         ('-dagman /usr/bin/condor_dagman', '-dagman /tmp/condor_dagman'),
                         ('-dagman /usr/bin/condor_dagman', '-dagman /usr/bin/condor_dagman -Dagman /usr/bin/condor_dagman'),
                         ('-DoRescueFrom 0', '-DoRescueFrom 1'),
                         ('-AutoRescue 1 ', '-AutoRescue 1 -DoRecovery '),
                         ('-AutoRescue 1 ', '-AutoRescue 1 -force '),
                         ('-Dag aIWO_2p0_comp_s1.a43.dag', '-Dag aIWO_2p0_comp_s1.dag'),
                         ('universe    = scheduler', 'universe    = vanilla'),
                         ('executable  = /usr/bin/condor_dagman', 'executable  = /tmp/condor_dagman')):
            self.assertIn(old, REAL_A43_SUB)
            self.assertEqual(self._grammar(REAL_A43_SUB.replace(old, new)), 'a43_dry_run_not_bound', new)


class TestV8CodexV7Review(Base):
    """The three false-accept paths of the Codex v7 review, each written first against v7 (where it was accepted)."""
    MVA = nl(RELAX_NL, **AIDS)                                 # MV 0.01 plus the registered aids

    # 1. a sibling run's absent directory hides the FAIL that the job exported under its actual run
    def test_v8_1_sibling_run_listing_cannot_hide_a_fail(self):
        w = polished_world(self.sub(), extra_seeded='FAIL', att_end={'005b': 1}, hide_output=('005b',),
                           inventories={'005b': 'run=comp_005b_sib'}, extra_runs={'005': ['comp_005b_sib']})
        res = self.check(w)
        self.assertDowngrade(res, 'smearing', 'C3 inventory UNRESOLVED')
        self.assertIn('attempt_inventory_run_is_not_the_jobs_actual_run', self.why(res, 'smearing'))

    # 2. epoch starts are checked against the exact registered states and triggers, not key names
    def _a35(self, s3_nl):
        w = World(self.sub())
        segs = [w.segment('e', f's{k}', 30 + k, self.MVA, geom(k), [(None, -7.0 - 0.001 * k, forces(k)),
                                                                     (geom(k + 1), -7.001 - 0.001 * k, forces(k + 1))],
                          term=f'2026-10-1{k}T12:00:00Z', sub=f'2026-10-1{k}T06:00:00Z') for k in range(3)]
        segs.append(w.segment('e', 's3', 33, s3_nl, geom(3), [(None, -7.0031, forces(3)), (geom(4), -7.0032, forces(4))],
                              final=geom(4), term='2026-10-13T12:00:00Z', sub='2026-10-13T06:00:00Z'))
        return lambda: w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_0p8_s2', 'route': 'A35'},
                             {'segments': segs, 'offset_evidence': w.tz})

    def test_v8_2_a35_start_must_be_the_registered_state(self):
        bad = nl(GAUSS_NL, system__degauss='0.1', electrons__mixing_beta='0.9', electrons__mixing_ndim='12',
                 electrons__electron_maxstep='300', electrons__diagonalization="'cg'")
        self.assertNotDerivable(self._a35(bad), 'epoch_start_changes_keys_outside_the_registered_transition')
        self.assertNotDerivable(self._a35(nl(GAUSS_NL, system__degauss='0.1', **AIDS)),
                                'epoch_start_state_differs_from_the_registered_state')

    def test_v8_2_conditional_rescue_needs_a_preceding_scf_failure(self):
        w = World(self.sub())
        s0 = w.segment('c', 's0', 50, RELAX_NL, geom(0), [(None, -9.0, forces(0)), (geom(1), -9.001, forces(1))],
                       term='2026-10-11T12:00:00Z', sub='2026-10-11T06:00:00Z')            # CONTINUE, no failure
        s1 = w.segment('c', 's1', 51, nl(GAUSS_NL, **AIDS), geom(1),
                       [(None, -9.0011, forces(1)), (geom(2), -9.0012, forces(2))], final=geom(2),
                       term='2026-10-12T12:00:00Z', sub='2026-10-12T06:00:00Z')
        self.assertNotDerivable(lambda: w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_2p0_s1',
                                                                            'route': 'A36-conditional'},
                                              {'segments': [s0, s1], 'offset_evidence': w.tz}),
                                'conditional_rescue_without_a_preceding_scf_failure')

    # 3. inverted chronology: s1 starts from G before s0 (which returned G on 18 Oct) has ended
    def test_v8_3_segments_must_run_in_order(self):
        w = World(self.sub())
        s0 = w.segment('o', 's0', 60, GAUSS_NL, geom(0), [(None, -50.0, forces(0)), (geom(1), -50.00002, forces(1))],
                       term='2026-10-18T00:00:00Z', sub='2026-10-17T00:00:00Z')
        s1 = w.segment('o', 's1', 61, GAUSS_NL, geom(1), [(None, -50.00002, forces(1)), (geom(2), -50.00004, forces(2))],
                       final=geom(2), term='2026-10-16T00:00:00Z', sub='2026-10-15T00:00:00Z')
        self.assertNotDerivable(lambda: w.rec('lin', 'relaxation_lineage', {'cell': 'aIO_2p0_s1',
                                                                            'route': 'registered-Gaussian'},
                                              {'segments': [s0, s1], 'offset_evidence': w.tz}),
                                'segment_started_before_the_previous_segment_ended')


class TestV8Rulings(Base):
    """Codex v7 rulings encoded in v8: section-3 resets and attempt<N> rescues as explicit transitions, the conditional
    A36 rescue with its trigger, label splits, and the job-history binding of C3 attempts."""
    LIN = {'cell': 'aIWO_0p7_s1', 'route': 'registered-MV'}

    def _resume(self, moved_drop=0, rescue=True, reset_logged='2026-10-10T15:00:00Z'):
        w = World(self.sub())
        s0 = w.segment('m', 's0', 70, RELAX_NL, geom(0), [(None, -1.0, forces(0)), (geom(1), -1.0002, forces(1))],
                       term='2026-10-10T12:00:00Z', scf_fail=True, status='FAILED [scf]', bestvalid=geom(1))
        s1 = w.segment('m', 's1', 71, RELAX_NL, geom(1), [(None, -1.0002, forces(1)), (geom(2), -1.0003, forces(2))],
                       term='2026-10-11T00:00:00Z')                       # README section 3: from the bestvalid
        s1['transition_record'] = w.transition_record('m/reset1.tr', 'm', 'section3_reset', 'relax_s0', 1, reset_logged)
        s2 = w.guard_segment('m', 's2', 72, RELAX_NL, geom(2), '2026-10-11T01:00:00Z')
        r0 = w.segment('m', 's0', 80, RELAX_NL, geom(2), [(None, -1.0003, forces(2)), (geom(3), -1.00031, forces(3))],
                       final=geom(3), term='2026-10-15T12:00:00Z', attempt=2)    # rescue DAG: s0 again, attempt 2
        moved = (s0['archives'] + s1['archives'] + s2['archives'])[moved_drop:]
        if rescue:
            r0['rescue_file'] = w.rescue_file('m/rescue2_rescue.dag'.replace('.tr', ''), 0)
            r0['transition_record'] = w.transition_record('m/rescue2.tr', 'm', 'section3_rescue', 'relax_s1', 1,
                                                          '2026-10-13T00:00:00Z', moved, auth=('R-TEST', 6, 6, 0, 'no'))
        reg = {'R-TEST': {'run': 'm', 'after_attempt': 1, 'basis': 'suspension', 'pause_started_utc': '2026-10-11T00:45:00Z',
                          'rule_logged_utc': '2026-10-11T00:30:00Z'}}       # v9/v10: a registered authorization (TEST ONLY)

        def fn():
            with _Registry(REGISTERED_RESCUE_AUTHORIZATIONS=reg):
                return w.rec('lin', 'relaxation_lineage', self.LIN, {'segments': [s0, s1, s2, r0], 'offset_evidence': w.tz})
        return w, fn

    def test_section3_reset_and_attempt_rescue_are_explicit_transitions(self):
        w, fn = self._resume()
        fn()
        d = jload(w.p['lin'])['derived']
        self.assertEqual([(x['segment'], x['continuation']) for x in d['segments']],
                         [('s0', None), ('s1', 'section3_reset'), ('a2.s0', 'section3_rescue')])
        self.assertEqual(([x['segment'] for x in d['guard_only_attempts']], d['bfgs_converged']), (['s2'], True))
        for kw, code in (({'moved_drop': 1}, 'rescue_move_record_differs_from_the_previous_attempt'),
                         ({'rescue': False}, 'attempt_change_without_rescue_record'),
                         ({'reset_logged': '2026-10-10T19:00:00Z'}, 'transition_record_time_not_between_the_segments')):
            self.assertNotDerivable(self._resume(**kw)[1], code)

    def _conditional(self, s0_term='2026-10-12T00:00:00Z', start=None):
        w = World(self.sub())
        G = nl(GAUSS_NL, **AIDS)
        s0 = w.segment('k', 's0', 90, RELAX_NL, geom(0), [(None, -9.0, forces(0)), (geom(1), -9.001, forces(1))],
                       term=s0_term, scf_fail=True, status='FAILED [scf]', bestvalid=geom(1))
        st = start or geom(1)
        s1 = w.segment('k', 's1', 91, G, st, [(None, -9.0011, forces(1)), (geom(2), -9.0012, forces(2))],
                       term=F.fmt_utc(F.parse_utc(s0_term) + dt.timedelta(days=1)))
        s1['transition_record'] = w.transition_record('k/r.tr', 'k', 'section3_reset', 'relax_s0', 1,
                                                      F.fmt_utc(F.parse_utc(s0_term) + dt.timedelta(hours=1)))
        s2 = w.segment('k', 's2', 92, G, geom(2), [(None, -9.0012, forces(2)), (geom(3), -9.00121, forces(3))],
                       final=geom(3), term=F.fmt_utc(F.parse_utc(s0_term) + dt.timedelta(days=2)))
        return w, lambda: w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_2p0_s1', 'route': 'A36-conditional'},
                                {'segments': [s0, s1, s2], 'offset_evidence': w.tz})

    def test_conditional_rescue_after_failed_scf_from_its_bestvalid(self):
        w, fn = self._conditional()
        fn()
        d = jload(w.p['lin'])['derived']
        self.assertEqual(([(e['segment'], e['amendment'], e['rescue']) for e in d['epoch_starts']], d['required_gates']),
                         ([('s1', 'A36-conditional', True)], ['s1->s2']))
        self.assertNotDerivable(self._conditional(start=geom(0))[1], 'conditional_rescue_not_from_the_best_valid_geometry')
        self.assertNotDerivable(self._conditional(s0_term='2026-10-17T12:00:00Z')[1],
                                'conditional_rescue_without_a_preceding_scf_failure')

    def test_label_split_is_an_explicit_transition(self):
        w = World(self.sub())
        s0 = w.segment('l', 's0', 95, RELAX_NL, geom(0), [(None, -1.0, forces(0)), (geom(1), -1.0001, forces(1))],
                       term='2026-10-10T12:00:00Z')
        s1 = w.segment('l', 's1', 96, RELAX_NL, geom(1), [(None, -1.0001, forces(1)), (geom(2), -1.0002, forces(2))],
                       final=geom(2), term='2026-10-11T00:00:00Z', labels=['In1', 'W', 'O1', 'H'])   # A25-type split
        s1.update(resource_route='A30', unsplit_input=w.pw_in('l/unsplit_s1.in', RELAX_NL, geom(1)),    # v10 evidence
                  resource_history=w.resource_history('l/res_96.txt', 96))                         # v11 evidence
        w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_2p0_s1', 'route': 'registered-MV'},     # v9: A30 scope
              {'segments': [s0, s1], 'offset_evidence': w.tz})
        d = jload(w.p['lin'])['derived']
        self.assertEqual((d['label_splits'], d['epochs'], d['epoch_starts']), (['s1'], [['s0', 's1']], []))

    def test_job_history_binds_the_attempt(self):
        self.assertSlotUnresolved(polished_world(self.sub(), omit_keys={'005a': ('job_history',)}),
                                  'attempt_job_history_missing')
        self.assertSlotUnresolved(polished_world(self.sub(), hist_sub={'005a': '2026-10-14T00:00:00Z'}),
                                  'attempt_job_history_differs_from_the_user_log')


class TestV7Rulings(Base):
    """Codex rulings on the v6 questions, encoded in v7 (scope, pre-item-B inputs, guard-only attempts, D-24 resets,
    export_manifest_final.dat), plus the identity and epoch-start details."""
    LIN = {'cell': 'aIWO_0p7_s1', 'route': 'registered-MV'}

    # ---- blocking scope (prospective; proposed D-43 wording in the digest)
    def test_unresolved_attempt_blocks_only_its_own_cell(self):
        w = polished_world(self.sub(), foreign_slot=True)
        other = [s for s in jload(w.p['manifest'])['derived']['slots'] if s['cell'] == 'aIWO_1p0_s1'][0]
        self.assertEqual((other['status'], other['reasons']),
                         ('unresolved', ['attempt_failed_without_artifact_inventory']))
        self.assertEqual(self.check(w)['verdict'], 'CLAIMS_OK')

    def test_ambiguous_ownership_blocks_both_slots_and_an_ambiguous_plan_blocks_all(self):
        w = polished_world(self.sub(), extra_noout=1, inventories={'005n': 'run=comp_002a'})
        slots = jload(w.p['manifest'])['derived']['slots']
        self.assertTrue(all(s['status'] == 'unresolved' and 'attempt_evidence_names_a_run_of_another_slot' in
                            s['reasons'] for s in slots))
        self.assertDowngrade(self.check(w), 'smearing', 'attempt_evidence_names_a_run_of_another_slot')
        with self.assertRaises(F.DeriveError) as cm:
            polished_world(self.sub(), plan_runs_dup=True)
        self.assertEqual(str(cm.exception), 'plan_run_owned_by_two_slots')

    def test_fail_in_an_unresolved_slot_still_vetoes(self):
        why = self.why(self.check(polished_world(self.sub(), extra_seeded='FAIL', extra_noout=1)), 'smearing')
        self.assertIn('failed cell-specific C3 check at 0.005 Ry', why)
        self.assertIn('C3 inventory UNRESOLVED', why)

    # ---- pre-item-B inputs from the EOS checkpoint
    def _pre_chain(self, w, **kw):
        s0 = w.segment('p', 's0', 60, RELAX_NL, geom(0), [(None, -1.0, forces(0)), (geom(1), -1.0001, forces(1))],
                       term='2026-10-10T12:00:00Z', layout='pre_item_b', **kw)
        s1 = w.segment('p', 's1', 61, RELAX_NL, geom(1), [(None, -1.00011, forces(1)), (geom(2), -1.0002, forces(2))],
                       final=geom(2), term='2026-10-11T00:00:00Z')
        return s0, s1

    def test_pre_item_b_checkpoint_input(self):
        w = World(self.sub())
        s0, s1 = self._pre_chain(w)
        w.rec('lin', 'relaxation_lineage', self.LIN, {'segments': [s0, s1], 'offset_evidence': w.tz})
        d = jload(w.p['lin'])['derived']
        self.assertEqual([(x['kind'], x['input_member']) for x in d['segments']],
                         [('pre_item_b', 'relax_s0_ckpt_60.tar.gz:relax.in'), ('item_b', 'relax_s1_input.in')])
        other_out = None
        for kw, code in (({'ckpt_cluster': 99}, 'pre_item_b_segment_without_its_checkpoint_input'),
                         ({'ckpt_out': 'other'}, 'checkpoint_output_differs_from_the_returned_output')):
            w = World(self.sub())
            if kw.get('ckpt_out'):
                other_out = w.qe_out('other/relax.out', [(None, -9.0, forces(0))])
                kw = {'ckpt_out': other_out}
            s0, s1 = self._pre_chain(w, **kw)
            self.assertNotDerivable(lambda: w.rec('lin', 'relaxation_lineage', self.LIN,
                                                  {'segments': [s0, s1], 'offset_evidence': w.tz}), code)

    # ---- guard-only attempts keep their historical index
    def test_guard_only_attempt_keeps_its_index(self):
        w = World(self.sub())
        s0 = w.segment('g', 's0', 70, RELAX_NL, geom(0), [(None, -1.0, forces(0)), (geom(1), -1.0001, forces(1))],
                       term='2026-10-10T12:00:00Z')
        s1 = w.guard_segment('g', 's1', 71, RELAX_NL, geom(1), '2026-10-10T13:00:00Z')
        s2 = w.segment('g', 's2', 72, RELAX_NL, geom(1), [(None, -1.00011, forces(1)), (geom(2), -1.0002, forces(2))],
                       final=geom(2), term='2026-10-11T00:00:00Z')
        w.rec('lin', 'relaxation_lineage', self.LIN, {'segments': [s0, s1, s2], 'offset_evidence': w.tz})
        d = jload(w.p['lin'])['derived']
        self.assertEqual(([x['segment'] for x in d['segments']], [x['segment'] for x in d['guard_only_attempts']]),
                         (['s0', 's2'], ['s1']))
        bad = dict(s1, relax_in=s0['relax_in'], relax_out=s0['relax_out'])
        self.assertNotDerivable(lambda: w.rec('lin2', 'relaxation_lineage', self.LIN,
                                              {'segments': [s0, bad, s2], 'offset_evidence': w.tz}),
                                'guard_only_attempt_with_a_claimed_input_or_output')

    # ---- the scripted D-24 transition reset (d24_transition.sh:63-67, 82) is the only accepted break
    @staticmethod
    def _reset_line(t, k=0):
        return (f'{t} relax_s{k} old=CONTINUE d24=CONTINUE; geomsel: synthetic input=tarball relax.in action: '
                'relax.in = lowest-energy validated geometry (best=1; old relax.in kept as relax.in.pre_transition_x)\n')

    def _reset_chain(self, start, evidence=None, s1_sub='2026-10-10T18:00:00Z', layout='pre_item_b'):
        w = World(self.sub())
        s0 = w.segment('r', 's0', 80, RELAX_NL, geom(0),        # old rule returned an unvalidated trial geom(9)
                       [(None, -1.0, forces(0)), (geom(1), -1.0002, forces(1)), (geom(2), -1.0001, forces(2))],
                       term='2026-10-10T12:00:00Z', returned=geom(9), layout=layout)
        s1 = w.segment('r', 's1', 81, RELAX_NL, start, [(None, -1.00021, forces(1)), (geom(3), -1.0003, forces(3))],
                       final=geom(3), term='2026-10-11T12:00:00Z', sub=s1_sub)
        if evidence:
            s1['reset_evidence'] = w.write('r/d24_transition.log', evidence)
        return w, s0, s1

    def test_d24_transition_reset_needs_its_evidence(self):
        w, s0, s1 = self._reset_chain(geom(1), self._reset_line('2026-10-10T15:00:00Z'))
        w.rec('lin', 'relaxation_lineage', self.LIN, {'segments': [s0, s1], 'offset_evidence': w.tz})
        self.assertEqual(jload(w.p['lin'])['derived']['segments'][1]['continuation'], 'd24_transition_reset')
        for args, code in (((geom(1), None), 'segment_does_not_continue_the_previous_segment'),
                           ((geom(1), self._reset_line('2026-10-10T19:00:00Z')),
                            'reset_evidence_time_not_between_the_segments'),
                           ((geom(1), self._reset_line('2026-10-10T15:00:00Z', 5)),
                            'reset_evidence_does_not_name_the_previous_segment'),
                           ((geom(2), self._reset_line('2026-10-10T15:00:00Z')),
                            'reset_geometry_is_not_the_lowest_energy_validated_geometry')):
            w, s0, s1 = self._reset_chain(*args)
            self.assertNotDerivable(lambda: w.rec('lin', 'relaxation_lineage', self.LIN,
                                                  {'segments': [s0, s1], 'offset_evidence': w.tz}), code)
        w, s0, s1 = self._reset_chain(geom(1), self._reset_line('2026-10-10T15:00:00Z'), layout='item_b')
        self.assertNotDerivable(lambda: w.rec('lin', 'relaxation_lineage', self.LIN,
                                              {'segments': [s0, s1], 'offset_evidence': w.tz}),
                                'reset_evidence_for_a_segment_that_ran_the_d24_steps')

    # ---- export_manifest_final.dat when exp/MANIFEST never reached EOS
    def test_export_manifest_final_dat(self):
        w = polished_world(self.sub(), comp_manifest='final_dat')
        self.assertEqual(self.check(w)['verdict'], 'CLAIMS_OK')
        self.assertEqual(jload(w.p['final_run_c005a'])['derived']['provenance']['export_format'], 'd24_final')
        run = w.final('fd', FINAL_NL, geom(3), cluster=881, manifest='final_dat',
                      statuses={'atomic_proj.xml.gz': 'FAILED'})            # declared, but not on EOS
        self.assertNotDerivable(lambda: w.rec('fx', 'final_run', {'cell': w.cell}, World.fsrc(run)),
                                'certified_run_file_not_bound_to_the_historical_export')

    # ---- archive identity (run, cluster, k) for segments and qualifications
    def test_archive_identity_required_and_checked(self):
        w = World(self.sub())
        s = w.segment('i', 's0', 90, GAUSS_NL, geom(0), [(None, -50.0, forces(0)), (geom(1), -50.00005, forces(1))],
                      final=geom(1), term='2026-10-15T00:00:00Z')
        lin = {'cell': 'aIO_2p0_s1', 'route': 'registered-Gaussian'}
        for bad, code in ((dict(s, export_manifest=w.sha256sum_record('i_s0/p0.sha256', s['archives'])),
                           'segment_archive_record_without_run_and_cluster_identity'),
                          (dict(s, export_manifest=w.archive_record('i_s0/p0_91.id', s['archives'], 'i', 91, 0)),
                           'segment_archive_identity_differs_from_the_job'),
                          (dict(s, cluster=91), 'segment_archive_identity_differs_from_the_job')):
            self.assertNotDerivable(lambda: w.rec('l', 'relaxation_lineage', lin,
                                                  {'segments': [bad], 'offset_evidence': w.tz}), code)
        s0 = w.segment('j', 's0', 93, GAUSS_NL, geom(0), [(None, -50.0, forces(0)), (geom(1), -50.00005, forces(1))],
                       term='2026-10-14T00:00:00Z')
        s1 = w.segment('j', 's1', 94, GAUSS_NL, geom(1), [(None, -50.00005, forces(1)), (geom(2), -50.0001, forces(2))],
                       final=geom(2), term='2026-10-15T00:00:00Z')
        s1['export_manifest'] = w.archive_record('j_s1/p0_run.id', s1['archives'], 'another_run', 94, 1)
        self.assertNotDerivable(lambda: w.rec('l2', 'relaxation_lineage', lin,
                                              {'segments': [s0, s1], 'offset_evidence': w.tz}),
                                'segments_from_different_runs')

    def test_qualification_archive_identity_and_window(self):
        w = polished_world(self.sub())
        tar = w.p['q_pol/returned/q_pol_results.tar.gz']
        src = {'scf_in': w.p['q_pol/scf.in'], 'scf_out': w.p['q_pol/scf.out'], 'joblog': w.p['q_pol/scf.log'],
               'lineage': w.p['lin_pol'], 'offset_evidence': w.tz, 'archives': [tar]}
        self.assertNotDerivable(lambda: w.rec('qx', 'qualification_scf', {'cell': w.cell, 'cluster': 201},
                                              dict(src, export_manifest=w.sha256sum_record('q_pol/p0.sha256', [tar]))),
                                'qualification_archive_record_without_run_and_cluster_identity')
        late = w.tarball('q_late/q_pol_results.tar.gz', {'scf.in': src['scf_in'], 'scf.out': src['scf_out']},
                         mtime='2026-10-19T00:00:00Z')                      # the job ended 14 Oct 09:00
        self.assertNotDerivable(lambda: w.rec('qy', 'qualification_scf', {'cell': w.cell, 'cluster': 201},
                                              dict(src, archives=[late], export_manifest=w.archive_record(
                                                  'q_late/p0.id', [late], 'q_pol', 201))),
                                'qualification_archive_written_outside_the_jobs_execution')

    # ---- only the registered epoch starts (A39(a2)) change settings
    def test_epoch_start_must_match_the_registered_amendment(self):
        G = nl(GAUSS_NL, **AIDS)

        def chain(nl1, nl2, route='A36'):
            w = World(self.sub())
            s0 = w.segment('e', 's0', 20, RELAX_NL, geom(0), [(None, -5.0, forces(0)), (geom(1), -5.001, forces(1))],
                           term='2026-10-10T12:00:00Z')
            s1 = w.segment('e', 's1', 21, nl1, geom(1), [(None, -5.0011, forces(1)), (geom(2), -5.0015, forces(2))],
                           term='2026-10-11T00:00:00Z')
            s2 = w.segment('e', 's2', 22, nl2, geom(2), [(None, -5.0015, forces(2)), (geom(3), -5.00155, forces(3))],
                           final=geom(3), term='2026-10-12T00:00:00Z')
            return w, lambda: w.rec('lin', 'relaxation_lineage', {'cell': 'aIWO_2p0_s2', 'route': route},
                                    {'segments': [s0, s1, s2], 'offset_evidence': w.tz})
        w, fn = chain(G, G)
        fn()
        self.assertEqual(jload(w.p['lin'])['derived']['epoch_starts'],
                         [{'segment': 's1', 'amendment': 'A36', 'changed_keys': [
                             'electrons.electron_maxstep', 'electrons.mixing_beta', 'electrons.mixing_ndim',
                             'system.degauss', 'system.smearing'], 'rescue': True,
                       'historical': False}])     # v19: every epoch start states whether it is historical
        for args, code in (((RELAX_NL, G), 'settings_change_without_authorized_epoch_start'),       # at s2, not s1
                           ((G, G, 'registered-MV'), 'settings_change_without_authorized_epoch_start'),
                           ((nl(G, system__ecutwfc='70'), nl(G, system__ecutwfc='70')),
                            'epoch_start_changes_keys_outside_the_registered_transition'),
                           ((nl(RELAX_NL, **AIDS), nl(RELAX_NL, **AIDS)),
                            'epoch_start_state_differs_from_the_registered_state')):
            self.assertNotDerivable(chain(*args)[1], code)


# ================================================================ v6 blockers (Codex 2026-10-13 ~01:45Z)
NONSUCCESS = (1, 'signal9', 'abort', 'hold_abort')


class TestV6Blocker1FailedAttemptInventory(Base):
    """Codex: 'A nonzero exit, signal or cancellation does not establish that no usable export exists.' A failed
    attempt may be 'no_output' only with a bound artifact inventory that shows no export; anything else is UNRESOLVED."""

    def test_codex_counterexample_failed_job_hiding_a_fail_export(self):
        # same bound log (exit 1), complete export and FAIL report supplied: the veto
        res = self.check(polished_world(self.sub(), extra_seeded='FAIL', att_end={'005b': 1}))
        self.assertDowngrade(res, 'smearing', 'failed cell-specific C3 check at 0.005 Ry')
        # the optional evidence omitted: v5 accepted 'no_output' and the FAIL disappeared; unresolved since v6
        # (v7 scope ruling: the slot, not the whole record, is UNRESOLVED)
        for end in NONSUCCESS:
            self.assertSlotUnresolved(polished_world(self.sub(), extra_seeded='FAIL', att_end={'005b': end},
                                                     hide_output=('005b',)),
                                      'attempt_failed_without_artifact_inventory')

    def test_forged_record_hiding_the_failed_export_rejected(self):
        def forge(r):
            for s in r['sources']['slots']:
                s['attempts'] = [a if a['cluster'] != 520 else {'cluster': 520, 'job_history': a['job_history']}
                                 for a in s['attempts']]          # v8: the history stays bound
            r['sources']['c3_reports'] = [x for x in r['sources']['c3_reports'] if 'c3_005b' not in x['file']]
        forge.rederive = True                     # v7: a consistent forgery; the slot stays UNRESOLVED
        res = self.check(polished_world(self.sub(), extra_seeded='FAIL', att_end={'005b': 'signal9'},
                                        edits={'manifest': forge}))
        self.assertDowngrade(res, 'smearing', 'attempt_failed_without_artifact_inventory')

    def test_inventory_listing_the_export_needs_its_report(self):
        self.assertSlotUnresolved(polished_world(self.sub(), extra_seeded='FAIL', att_end={'005b': 1},
                                                 hide_output=('005b',), inventories={'005b': 'export'}),
                                  'attempt_inventory_lists_an_export_without_its_c3_report')

    def test_inventory_without_export_accepts_no_output(self):
        want = {1: 'normal_exit_1', 'signal9': 'signal_9', 'abort': 'aborted', 'hold_abort': 'removed_while_held'}
        for end, kind in [(e, 'probe_only') for e in NONSUCCESS] + [('abort', 'absent')]:
            w = polished_world(self.sub(), extra_noout=end, inventories={'005n': kind})
            att = [a for s in jload(w.p['manifest'])['derived']['slots'] for a in s['attempts']
                   if a['cluster'] == 530][0]
            self.assertEqual((att['result'], att['disposition']), ('no_output', want[end]))
            self.assertEqual(att['artifact_inventory']['sha256'], F.sha256_file(w.p['inv/005n/inventory.txt']))
            self.assertEqual(att['artifact_inventory']['n_exported_files'], 0)
            self.assertEqual(self.check(w)['verdict'], 'CLAIMS_OK', (end, kind))

    def test_unverifiable_inventory_is_unresolved(self):
        cases = {'other_cluster': 'attempt_inventory_is_for_another_cluster',
                 'other_location': 'attempt_inventory_location_is_not_this_jobs_export_directory',
                 'early': 'attempt_inventory_captured_before_the_job_ended',
                 'truncated': 'attempt_inventory_incomplete',
                 'malformed': 'attempt_inventory_malformed'}
        for kind, code in cases.items():                      # v7 scope ruling: the slot is UNRESOLVED
            self.assertSlotUnresolved(polished_world(self.sub(), extra_noout=1, inventories={'005n': kind}), code)
        w = polished_world(self.sub(), extra_noout=1, inventories={'005n': 'probe_only'})
        with open(w.p['inv/005n/inventory.txt'], 'a', encoding='utf-8') as fh:     # edited after the record
            fh.write('\n')
        self.assertDowngrade(self.check(w), 'smearing', 'not derivable from its sources (source_sha256_mismatch)')

    def test_inventory_contradicting_a_supplied_export_rejected(self):
        self.assertSlotUnresolved(polished_world(self.sub(), extra_seeded='PASS', att_end={'005b': 1},
                                                 inventories={'005b': 'probe_only'}),
                                  'attempt_inventory_contradicts_its_export')
        w = polished_world(self.sub(), extra_seeded='PASS', att_end={'005b': 1}, inventories={'005b': 'export'})
        self.assertEqual(self.check(w)['verdict'], 'CLAIMS_OK')

    def test_checker_rechecks_no_output_attempts(self):
        w = polished_world(self.sub(), extra_noout='abort', inventories={'005n': 'probe_only'})
        rec = jload(w.p['manifest'])
        for s in rec['derived']['slots']:
            for a in s['attempts']:
                if a['cluster'] == 530:
                    a.pop('artifact_inventory')
        it = CA.Item(w.p['manifest'], H('m'), 'record', rec)
        it.verified = []                                   # as if verified: the checker's own re-check must catch it
        cert = CA.Cert(w.p['cert_pol'], jload(w.p['cert_pol']), H('c'))
        _, p = CA.c3_inventory(cert, [it], CA.Ctx())
        self.assertIn('C3 inventory UNRESOLVED: attempt 530 has no output', ' | '.join(p))

    def test_aborted_job_manifest_written_after_its_end(self):
        self.assertSlotUnresolved(polished_world(self.sub(), att_end={'005a': 'abort'},
                                                 late_manifest='2026-10-16T05:00:00Z'),
                                  'attempt_export_manifest_written_after_the_job_ended')

    def test_success_path_unchanged_and_not_excused_by_an_inventory(self):
        # exit 0 without output: an inventory does not excuse it (v7 scope ruling: the slot is UNRESOLVED)
        self.assertSlotUnresolved(polished_world(self.sub(), extra_noout=0, inventories={'005n': 'probe_only'}),
                                  'attempt_completed_normally_but_output_missing')
        # exit 0, output given but its export evidence omitted
        self.assertSlotUnresolved(polished_world(self.sub(), extra_seeded='PASS',
                                                 omit_keys={'005b': ('export_manifest',)}),
                                  'attempt_export_provenance_missing')


class TestV6Blocker2SavedSegmentInput(Base):
    """Codex: D-24 saves the segment input as relax_s<k>_input.in and then replaces relax.in with the selected next /
    final geometry (steps_relax.sh:19-20, 30, 35). The expected member is derived from the verified JOB lineage."""
    LIN = {'cell': 'aIWO_0p7_s1', 'route': 'registered-MV'}

    def _chain(self, w, **s1kw):
        s0 = w.segment('x', 's0', 10, RELAX_NL, geom(0), [(None, -1.0, forces(0)), (geom(1), -1.0001, forces(1))],
                       term='2026-10-10T12:00:00Z')
        s1 = w.segment('x', 's1', 11, RELAX_NL, geom(1), [(None, -1.00011, forces(1)), (geom(2), -1.0002, forces(2))],
                       final=geom(2), term='2026-10-11T00:00:00Z', **s1kw)
        return s0, s1

    def test_codex_counterexample_saved_input_and_changed_returned_relax_in(self):
        w = World(self.sub())
        s0, s1 = self._chain(w)
        arc = s1['archives'][0]
        self.assertEqual(os.path.basename(arc), 'relax_s1_results.tar.gz')
        with tarfile.open(arc) as t:
            self.assertLessEqual({'relax_s1_input.in', 'relax.in', 'relax.out', 'relax_s1_lineage.log'},
                                 set(t.getnames()))
        saved, returned = F.archive_member_sha256(arc, 'relax_s1_input.in'), F.archive_member_sha256(arc, 'relax.in')
        self.assertNotEqual(saved, returned)                       # the geometry changed (CONVERGED)
        self.assertEqual(saved, F.sha256_file(s1['relax_in']))
        w.rec('lin', 'relaxation_lineage', self.LIN, {'segments': [s0, s1], 'offset_evidence': w.tz})
        d = jload(w.p['lin'])['derived']
        self.assertEqual([(x['job'], x['input_member']) for x in d['segments']],
                         [('relax_s0', 'relax_s0_input.in'), ('relax_s1', 'relax_s1_input.in')])
        self.assertTrue(d['bfgs_converged'])
        for bad in (s0, s1):                                       # binding to the returned relax.in is refused
            segs = [dict(s, relax_in=w.p[f'x_{s["segment"]}/returned/relax.in']) if s is bad else s for s in (s0, s1)]
            self.assertNotDerivable(lambda: w.rec('lin2', 'relaxation_lineage', self.LIN,
                                                  {'segments': segs, 'offset_evidence': w.tz}),
                                    'relax_in_is_the_returned_next_geometry_not_the_saved_input')

    def test_k_comes_from_the_verified_job_lineage(self):
        cases = [({'k': 0}, 'relax_in_not_bound_to_the_historical_export'),      # relax_s0's archive cannot stand in
                 ({'job_name': 'relax_s7'}, 'segment_lineage_log_names_another_job'),
                 ({'saved': False}, 'segment_saved_input_missing_from_the_job_archive')]   # pre-item-B: a gap
        for kw, code in cases:
            w = World(self.sub())
            s0, s1 = self._chain(w, **kw)
            self.assertNotDerivable(lambda: w.rec('lin', 'relaxation_lineage', self.LIN,
                                                  {'segments': [s0, s1], 'offset_evidence': w.tz}), code)

    def test_lineage_log_missing_is_a_gap(self):
        w = World(self.sub())
        s0, s1 = self._chain(w)
        tar = w.tarball('x_s1/returned/relax_s1_results.tar.gz',
                        {'relax_s1_input.in': s1['relax_in'], 'relax.in': w.p['x_s1/returned/relax.in'],
                         'relax.out': s1['relax_out']}, mtime='2026-10-10T23:58:00Z')
        s1.update({'archives': [tar], 'export_manifest': w.archive_record('x_s1/p0_new.id', [tar], 'x', 11, 1)})
        self.assertNotDerivable(lambda: w.rec('lin', 'relaxation_lineage', self.LIN,
                                              {'segments': [s0, s1], 'offset_evidence': w.tz}),
                                'segment_lineage_log_missing')

    def test_whole_chain_uses_saved_inputs(self):
        w = polished_world(self.sub())
        self.assertEqual(self.check(w)['verdict'], 'CLAIMS_OK')
        d = jload(w.p['lin_mv'])['derived']
        self.assertEqual([x['input_member'] for x in d['segments']], ['relax_s0_input.in', 'relax_s1_input.in'])


# ================================================================ v4 items (Codex 2026-10-12T20:25Z)
class TestV4Item1ForceIdentities(Base):
    def _two_atom(self, rows):
        w = World(self.sub())
        txt = ('&CONTROL\n  calculation = \'relax\'\n/\n&SYSTEM\n  ibrav = 0\n  nat = 2\n  ntyp = 2\n/\n&ELECTRONS\n/\n'
               'ATOMIC_SPECIES\nIn 114.818 In.UPF\nO 15.999 O.UPF\nCELL_PARAMETERS angstrom\n10 0 0\n0 10 0\n0 0 10\n'
               'ATOMIC_POSITIONS angstrom\nIn 1.0 1.0 1.0\nO 2.0 2.0 2.0\nK_POINTS gamma\n')
        inp = F.read_pw_input(w.write('two.in', txt))
        out = w.write('two.out', '!    total energy              =     -10.00000000 Ry\n'
                                 '     Forces acting on atoms (cartesian axes, Ry/au):\n\n'
                      + ''.join(f'     atom {a:4d} type {t:2d}   force =     0.00010000    0.00010000    0.00010000\n'
                                for a, t in rows) + '     JOB DONE.\n')
        return lambda: F.read_qe_output(out, inp)

    def test_valid_two_atom_block(self):
        self.assertEqual(len(self._two_atom([(1, 1), (2, 2)])()['evaluations']), 1)

    def test_atom_1_twice_atom_2_missing_rejected(self):
        self.assertNotDerivable(self._two_atom([(1, 1), (1, 1)]), 'force_block_atom_indices_not_1_to_N_once')

    def test_type_differs_from_input_rejected(self):
        self.assertNotDerivable(self._two_atom([(1, 2), (2, 2)]), 'force_block_atom_type_differs_from_input')

    def test_corrupt_block_blocks_lineage_record(self):
        w = World(self.sub())
        s = w.segment('x', 's0', 1, RELAX_NL, geom(0), [(None, -1.0, forces(0))], final=geom(0),
                      term='2026-10-11T00:00:00Z')
        with open(s['relax_out'], encoding='utf-8') as fh:
            bad = fh.read().replace('atom    2 type  2', 'atom    1 type  1')
        o = w.write('x_bad/relax.out', bad)
        tar = w.relax_archive('x_bad', 0, s['relax_in'], o, w.p['x_s0/returned/relax.in'], 'CONVERGED',
                              mtime='2026-10-10T23:58:00Z')                       # v6 layout, v7 identity
        s.update({'relax_out': o, 'archives': [tar],
                  'export_manifest': w.archive_record('x_bad/p0.id', [tar], 'x', 1, 0)})
        self.assertNotDerivable(lambda: w.rec('l', 'relaxation_lineage', {'cell': 'aIWO_0p7_s1',
                                                                          'route': 'registered-MV'},
                                              {'segments': [s], 'offset_evidence': w.tz}),
                                'force_block_atom_indices_not_1_to_N_once')


class TestV4Item2RegisteredConvergence(Base):
    def test_loose_forc_conv_thr_and_0p01_residual_rejected(self):
        res = self.check(polished_world(self.sub(), polish_nl=nl(POLISH_NL, control__forc_conv_thr='0.1'),
                                        polish_last_max=0.01, qual_dforce=0.0))
        self.assertDowngrade(res, 'relaxation', 'did not use the registered ionic thresholds')
        self.assertIn('final residual force 0.01 Ry/bohr exceeds the registered forc_conv_thr 0.001',
                      self.why(res, 'relaxation'))
        self.assertIn('registered ionic thresholds', self.why(res, 'geometry'))

    def test_loose_etot_conv_thr_alone_rejected(self):
        res = self.check(polished_world(self.sub(), polish_nl=nl(POLISH_NL, control__etot_conv_thr='1.0d-2')))
        self.assertDowngrade(res, 'relaxation', 'etot_conv_thr 1e-4 required')

    def test_qe_defaults_count_as_registered(self):
        res = self.check(polished_world(self.sub(), polish_nl=nl(POLISH_NL, control__forc_conv_thr=None,
                                                                 control__etot_conv_thr=None)))
        self.assertEqual(res['verdict'], 'CLAIMS_OK', json.dumps(res, indent=1))

    def test_a35_terminal_scf_failure_vetoes_later_convergence(self):
        g = nl(GAUSS_NL, **AIDS)
        # v7: the A35 epoch starts at s3 (A39(a2)), so the fixture has three original segments (pre=3)
        res = self.check(gated_world(self.sub(), cell='aIWO_0p8_s2', route='A35', s12_nl=g, s1_fail=True, pre=3,
                                     pre_aids_from=1),
                         cert='cert')
        self.assertDowngrade(res, 'relaxation', 'terminal SCF failure in the active epoch (segment s3)')

    def test_historical_failure_disclosed_not_vetoed(self):
        g = nl(GAUSS_NL, **AIDS)
        res = self.check(gated_world(self.sub(), cell='aIWO_0p8_s2', route='A35', s12_nl=g, s0_fail=True, pre=3,
                                     pre_aids_from=1),
                         cert='cert')
        self.assertEqual(res['verdict'], 'CLAIMS_OK', json.dumps(res, indent=1))
        self.assertTrue(any('historical SCF failures before the active epoch' in x and 's0' in x
                            for x in res['blocks']['relaxation']['notes']))


class TestV4Item3InputProvenance(Base):
    def test_missing_provenance_cannot_be_reconstructed(self):
        w = polished_world(self.sub())
        src = World.fsrc(w.ref)
        del src['export_manifest']
        self.assertNotDerivable(lambda: w.rec('fx', 'final_run', {'cell': w.cell}, src), 'final_input_provenance_missing')
        q = jload(w.p['q_pol'])
        self.assertIn('export_manifest', q['sources'])
        self.assertNotDerivable(lambda: w.rec('qx', 'qualification_scf', {'cell': w.cell, 'cluster': 201},
                                              {'scf_in': w.p['q_pol/scf.in'], 'scf_out': w.p['q_pol/scf.out'],
                                               'joblog': w.p['q_pol/scf.log'], 'lineage': w.p['lin_pol'],
                                               'offset_evidence': w.tz}),
                                'qualification_input_provenance_missing')

    def test_export_must_contain_the_certified_run_files(self):
        w = polished_world(self.sub())
        src = World.fsrc(w.ref)
        src['archives'] = []                       # lineage_final.dat and final_avg.dat live in final_small.tar.gz
        self.assertNotDerivable(lambda: w.rec('fx', 'final_run', {'cell': w.cell}, src),
                                'certified_run_file_not_bound_to_the_historical_export')


# ================================================================ v5 items (Codex 2026-10-12T20:44Z)
class TestV5Item1AttemptDisposition(Base):
    def test_hidden_fail_with_normal_exit_blocks(self):        # v7 scope ruling: the slot is UNRESOLVED
        self.assertSlotUnresolved(polished_world(self.sub(), extra_seeded='FAIL', hide_output=('005b',)),
                                  'attempt_completed_normally_but_output_missing')

    def test_forged_inventory_hiding_the_fail_rejected(self):
        def forge(r):
            for s in r['sources']['slots']:
                s['attempts'] = [a if a['cluster'] != 520 else {'cluster': 520, 'job_history': a['job_history']}
                                 for a in s['attempts']]          # v8: the history stays bound
            r['sources']['c3_reports'] = [x for x in r['sources']['c3_reports'] if 'c3_005b' not in x['file']]
        forge.rederive = True                     # v7: a consistent forgery; the slot stays UNRESOLVED
        res = self.check(polished_world(self.sub(), extra_seeded='FAIL', edits={'manifest': forge}))
        self.assertDowngrade(res, 'smearing', 'attempt_completed_normally_but_output_missing')

    def test_explained_failures_are_accepted(self):
        # changed in v6 (it encoded the v5 defect): a failure event explains a missing output only together with a
        # verified artifact inventory of the attempt's export directory that shows no export (Codex 2026-10-13)
        for end in (1, 'signal9', 'abort'):
            w = polished_world(self.sub(), extra_noout=end, inventories={'005n': 'probe_only'})
            d = jload(w.p['manifest'])['derived']
            att = [a for s in d['slots'] for a in s['attempts'] if a['cluster'] == 530][0]
            self.assertEqual(att['result'], 'no_output')
            self.assertEqual(self.check(w)['verdict'], 'CLAIMS_OK', end)

    def test_unfinished_attempt_blocks(self):                  # v7 scope ruling: the slot is UNRESOLVED
        self.assertSlotUnresolved(polished_world(self.sub(), extra_noout='running'),
                                  'attempt_not_finished_no_terminal_event')

    def test_unexplained_exit_0_without_output_blocks(self):   # v7 scope ruling: the slot is UNRESOLVED
        self.assertSlotUnresolved(polished_world(self.sub(), extra_noout=0),
                                  'attempt_completed_normally_but_output_missing')


class TestV5Item2AsRunInput(Base):
    def test_unused_fresh_input_in_the_export_is_refused(self):
        w = polished_world(self.sub())
        fresh = w.pw_in('unused/scf_fresh.in', nl(FINAL_NL, system__degauss='0.005'), geom(3))
        actual = w.final('comp_x', nl(FINAL_NL, system__degauss='0.005', electrons__startingpot="'file'"), geom(3),
                         cluster=777, unused_fresh=fresh)
        src = {**World.fsrc(w.ref, 'ref_'), **World.fsrc(actual, 'comp_')}
        src['comp_in'] = fresh                     # a member of the same export, same geometry and settings
        self.assertNotDerivable(lambda: w.rec('cx', 'c3_companion_run', {'cell': w.cell}, src),
                                'companion_input_is_not_the_asrun_scf_input')
        src['comp_in'] = actual['in']
        w.rec('cx', 'c3_companion_run', {'cell': w.cell}, src)
        self.assertEqual(jload(w.p['cx'])['derived']['start_mode'], 'density-seeded')

    def test_lineage_must_be_the_certified_run_file(self):
        w = polished_world(self.sub())
        src = World.fsrc(w.ref)
        src['lineage_file'] = w.runs['comp_005a']['lineage']
        self.assertNotDerivable(lambda: w.rec('fx', 'final_run', {'cell': w.cell}, src),
                                'final_lineage_is_not_a_certified_run_file')

    def test_missing_asrun_record_is_an_unresolved_gap(self):
        w = polished_world(self.sub())
        run = w.final('old_final', FINAL_NL, geom(3), cluster=880, asrun=False)
        self.assertNotDerivable(lambda: w.rec('fx', 'final_run', {'cell': w.cell}, World.fsrc(run)),
                                'lineage_without_unique_asrun_scf_input')


class TestV5Item3BothEndpointsFresh(Base):
    def test_density_seeded_reference_does_not_count(self):
        res = self.check(polished_world(self.sub(), ref_seeded=True))
        self.assertDowngrade(res, 'smearing', "C3 coverage missing at ['0.002', '0.005']")
        self.assertTrue(any('reference density-seeded' in x for x in res['blocks']['smearing']['notes']))

    def test_density_seeded_reference_blocks_the_candidate_route(self):
        res = self.check(polished_world(self.sub(), ref_seeded=True, width=0.005))
        self.assertDowngrade(res, 'smearing', 'no fresh C3 PASS with this run as the compared 0.005 Ry width')

    def test_fail_veto_regardless_of_start_mode(self):
        res = self.check(polished_world(self.sub(), ref_seeded=True, c3_status={0.002: 'FAIL'}))
        self.assertDowngrade(res, 'smearing', 'failed cell-specific C3 check at 0.002 Ry')


class TestV5Item4ExportFormats(Base):
    def test_d24_manifest_is_parsed(self):
        w = polished_world(self.sub())
        man = F.read_export_manifest(w.ref['man'])
        self.assertEqual((man['format'], man['run'], man['cluster'], F.fmt_utc(man['written_utc'])),
                         ('d24', 'final_pol', 650, '2026-10-15T23:59:00Z'))
        self.assertEqual({n for _, n, _ in man['entries']},
                         {'final_small.tar.gz', 'data-file-schema.xml.gz', 'atomic_proj.xml.gz', 'projwfc_final.out.gz'})
        d = jload(w.p['final_run_pol'])['derived']['provenance']['run_file_binding']
        self.assertEqual((d['lineage_final.dat'], d['atomic_proj.xml.gz']), ('member:final_small.tar.gz', 'direct'))

    def test_extracted_member_must_equal_the_archive_member(self):
        w = World(self.sub())
        s = w.segment('x', 's0', 1, RELAX_NL, geom(0), [(None, -1.0, forces(0))], final=geom(0),
                      term='2026-10-11T00:00:00Z')
        with open(s['relax_in'], 'a', encoding='utf-8') as fh:
            fh.write('! edited after the export\n')
        self.assertNotDerivable(lambda: w.rec('l', 'relaxation_lineage', {'cell': 'aIWO_0p7_s1',
                                                                          'route': 'registered-MV'},
                                              {'segments': [s], 'offset_evidence': w.tz}),
                                'relax_in_not_bound_to_the_historical_export')

    def test_replaced_archive_is_not_the_listed_one(self):
        w = World(self.sub())
        s = w.segment('x', 's0', 1, RELAX_NL, geom(0), [(None, -1.0, forces(0))], final=geom(0),
                      term='2026-10-11T00:00:00Z')
        w.relax_archive('x_s0', 0, s['relax_in'], s['relax_out'], w.p['x_s0/returned/relax.in'], 'CONVERGED',
                        extra={'extra.txt': w.tz})                  # v6 layout: the listed archive is replaced
        self.assertNotDerivable(lambda: w.rec('l', 'relaxation_lineage', {'cell': 'aIWO_0p7_s1',
                                                                          'route': 'registered-MV'},
                                              {'segments': [s], 'offset_evidence': w.tz}),
                                'relax_in_not_bound_to_the_historical_export')

    def test_newly_generated_member_manifest_is_not_provenance(self):
        w = World(self.sub())
        s = w.segment('x', 's0', 1, RELAX_NL, geom(0), [(None, -1.0, forces(0))], final=geom(0),
                      term='2026-10-11T00:00:00Z')
        s['export_manifest'] = w.write('x_s0/new_members.sha256', f'{F.sha256_file(s["relax_in"])}  relax.in\n'
                                                                  f'{F.sha256_file(s["relax_out"])}  relax.out\n')
        s['archives'] = []
        self.assertNotDerivable(lambda: w.rec('l', 'relaxation_lineage', {'cell': 'aIWO_0p7_s1',
                                                                          'route': 'registered-MV'},
                                              {'segments': [s], 'offset_evidence': w.tz}),
                                'segment_archive_record_without_run_and_cluster_identity')   # v7 (was: not bound)

    def test_final_needs_the_in_job_d24_manifest(self):
        w = polished_world(self.sub())
        src = World.fsrc(w.ref)
        src['export_manifest'] = w.archive_record('final_pol/p0.sha256', w.ref['archives'])
        self.assertNotDerivable(lambda: w.rec('fx', 'final_run', {'cell': w.cell}, src),
                                'final_export_manifest_is_not_the_in_job_d24_manifest')

    def test_attempt_manifest_written_after_the_job_ended(self):   # v7 scope ruling: the slot is UNRESOLVED
        self.assertSlotUnresolved(polished_world(self.sub(), late_manifest='2026-10-16T05:00:00Z'),
                                  'attempt_export_manifest_written_after_the_job_ended')


class TestV4Item4Inventory(Base):
    def test_density_seeded_fail_in_inventory_vetoes(self):
        res = self.check(polished_world(self.sub(), extra_seeded='FAIL'))
        self.assertDowngrade(res, 'smearing', 'failed cell-specific C3 check at 0.005 Ry')

    def test_removing_the_fail_report_is_not_derivable(self):    # v7 scope ruling: the slot is UNRESOLVED
        self.assertSlotUnresolved(polished_world(self.sub(), extra_seeded='FAIL', drop_reports=('005b',)),
                                  'attempt_without_exactly_one_result')

    def test_removing_the_attempt_is_not_derivable(self):        # v7: every submitted cluster is retained
        d, _ = self.assertSlotUnresolved(polished_world(self.sub(), extra_seeded='FAIL', drop_reports=('005b',),
                                                        drop_attempts=('005b',)), 'slot_attempts_differ_from_user_log')
        att = [a for s in d['slots'] for a in s['attempts'] if a['cluster'] == 520]
        self.assertEqual([(a['result'], a['reason']) for a in att],
                         [('unresolved', 'attempt_missing_from_the_inventory')])

    def test_forged_inventory_record_rejected(self):
        def forge(r):
            r['sources']['c3_reports'] = [x for x in r['sources']['c3_reports'] if 'c3_005b' not in x['file']]
        res = self.check(polished_world(self.sub(), extra_seeded='FAIL', edits={'manifest': forge}))
        self.assertDowngrade(res, 'smearing', 'record manifest.json: not reproducible from its bound sources')
        forge.rederive = True                     # v7: re-derived by the writer, the slot is UNRESOLVED
        res = self.check(polished_world(self.sub(), extra_seeded='FAIL', edits={'manifest': forge}))
        self.assertDowngrade(res, 'smearing', 'C3 inventory UNRESOLVED')
        self.assertIn('attempt_without_exactly_one_result', self.why(res, 'smearing'))

    def test_slot_missing_from_frozen_plan_accounting(self):
        def drop(r):
            r['sources']['slots'] = r['sources']['slots'][:1]
        res = self.check(polished_world(self.sub(), edits={'manifest': drop}))
        self.assertDowngrade(res, 'smearing', 'slots_differ_from_frozen_plan')


class TestV4Item5RoleSelection(Base):
    def test_primary_converged_is_selected(self):
        w = polished_world(self.sub(), role_terms={'aIWO': ('2026-10-15T00:00:00Z', '2026-10-15T00:00:00Z')})
        with open(w.p['a15'], encoding='utf-8') as f:
            self.assertEqual(json.load(f)['derived']['roles']['aIWO'], 'aIWO_2p0_s1')
        self.assertEqual(self.check(w)['verdict'], 'CLAIMS_OK')

    def test_backup_selection_while_primary_converged_rejected(self):
        def forge(r):
            r['derived']['roles']['aIWO'] = 'aIWO_2p0_s2'
        w = polished_world(self.sub(), role_terms={'aIWO': ('2026-10-15T00:00:00Z', '2026-10-15T00:00:00Z')},
                           edits={'a15': forge})
        self.assertDowngrade(self.check(w), 'smearing', 'record a15.json: not reproducible from its bound sources')

    def test_backup_derived_when_primary_not_converged(self):
        w = polished_world(self.sub(), role_terms={'aIWO': ('2026-10-18T00:00:00Z', '2026-10-15T00:00:00Z')})
        with open(w.p['a15'], encoding='utf-8') as f:
            d = json.load(f)['derived']
        self.assertEqual(d['roles']['aIWO'], 'aIWO_2p0_s2')
        self.assertIn('converged_after_cutoff', d['selection']['aIWO']['primary']['reasons'])
        self.assertEqual(self.check(w)['verdict'], 'CLAIMS_OK')

    def test_no_converged_role_leaves_a15_unresolved(self):
        w = polished_world(self.sub(), role_terms={'aIWO': ('2026-10-18T00:00:00Z', None)})
        self.assertDowngrade(self.check(w), 'smearing', 'A15 role aIWO unresolved')

    def test_primary_status_record_required(self):
        w = polished_world(self.sub())
        a = {'audit_report': w.p['audit.json'], 'roles': {'aIO': {'backup': w.p['lin_aIO_2p0_s1']}}}
        self.assertNotDerivable(lambda: w.rec('ax', 'a15_provisional', {}, a), 'role_primary_status_record_missing')


class TestV4Item6RealJobLogFormat(Base):
    REAL = ('000 (12884016.000.000) 10/10 14:22:11 Job submitted from host: <10.0.0.1:9618>\n...\n'
            '001 (12884016.000.000) 10/10 15:33:36 Job executing on host: <10.0.0.2:9618>\n...\n'
            '006 (12884016.000.000) 10/10 20:36:57 Image size of job updated: 37458808\n...\n'
            '005 (12884016.000.000) 10/10 20:36:57 Job terminated.\n\t(1) Normal termination (return value 0)\n...\n')

    def test_real_header_with_bound_offset_evidence(self):
        w = World(self.sub())
        log = w.write('relax.log', self.REAL)
        tz = F.read_offset_evidence(w.tz)
        self.assertEqual(F.fmt_utc(F.terminated_utc(log, 12884016, tz)), '2026-10-10T18:36:57Z')
        self.assertEqual(F.submitted_clusters(log, tz), [12884016])

    def test_no_evidence_no_year_or_zone(self):
        w = World(self.sub())
        self.assertNotDerivable(lambda: F.terminated_utc(w.write('r.log', self.REAL), 12884016),
                                'joblog_mmdd_time_without_offset_evidence')

    def test_stamp_outside_evidence_window(self):
        w = World(self.sub())
        log = w.write('r.log', self.REAL.replace('10/10 20:36:57 Job terminated', '10/26 20:36:57 Job terminated'))
        self.assertNotDerivable(lambda: F.terminated_utc(log, 12884016, F.read_offset_evidence(w.tz)),
                                'joblog_mmdd_year_not_unique_in_offset_window')

    def test_decreasing_times_rejected(self):
        w = World(self.sub())
        log = w.write('r.log', self.REAL.replace('10/10 20:36:57 Job terminated', '10/09 20:36:57 Job terminated'))
        self.assertNotDerivable(lambda: F.terminated_utc(log, 12884016, F.read_offset_evidence(w.tz)),
                                'joblog_event_times_decrease')

    def test_unknown_header_format_rejected(self):
        w = World(self.sub())
        log = w.write('r.log', self.REAL.replace('10/10 20:36:57 Job terminated', '2026/10/10 20:36:57 Job terminated'))
        self.assertNotDerivable(lambda: F.terminated_utc(log, 12884016, F.read_offset_evidence(w.tz)),
                                'joblog_event_header_format_unknown')

    def test_offset_evidence_needs_validity_window(self):
        w = World(self.sub())
        bad = w.write('tz2.txt', 'utc 2026-10-12T13:00:00Z\nlocal 2026-10-12T15:00:00+0200\n')
        self.assertNotDerivable(lambda: F.read_offset_evidence(bad), 'offset_evidence_malformed')

    def test_whole_chain_on_real_format_and_on_iso(self):
        self.assertEqual(self.check(polished_world(self.sub()))['verdict'], 'CLAIMS_OK')
        self.assertEqual(self.check(polished_world(self.sub(), log_fmt='iso'))['verdict'], 'CLAIMS_OK')


# ================================================================ v3 coverage (ported)
class TestCodexExample1NumericQualification(Base):
    def test_valid_chain_passes(self):
        res = self.check(polished_world(self.sub()))
        self.assertEqual(res['verdict'], 'CLAIMS_OK', json.dumps(res, indent=1))
        self.assertIn('A15 width provisional (EA not evaluated)', res['blocks']['smearing']['notes'])

    def test_qualification_1e3_Ry_and_0p01_Ry_bohr_rejected(self):
        res = self.check(polished_world(self.sub(), qual_dF=1e-3, qual_dforce=0.01))
        self.assertDowngrade(res, 'relaxation', 'qualification FAILED: |dF| = 0.001 Ry > 1e-05 Ry')
        self.assertIn('qualification FAILED: max |dF| = 0.01 Ry/bohr > 0.001 Ry/bohr', self.why(res, 'relaxation'))

    def test_pass_label_and_edited_numbers_rejected(self):
        def forge(r):
            r['derived'].update({'delta_F_Ry': 2e-6, 'max_abs_dF_Ry_bohr': 1e-4, 'status': 'PASS'})
        res = self.check(polished_world(self.sub(), qual_dF=1e-3, qual_dforce=0.01, edits={'q_pol': forge}))
        self.assertDowngrade(res, 'relaxation', 'not reproducible from its bound sources')

    def test_non_fresh_and_late_qualification(self):
        self.assertDowngrade(self.check(polished_world(self.sub(), qual_fresh=False)), 'relaxation',
                             'not a fresh start')
        self.assertDowngrade(self.check(polished_world(self.sub(), qual_term='2026-10-20T12:00:01Z')), 'relaxation',
                             'after the deadline 2026-10-20T12:00:00Z')


class TestCodexExample2NoDateOverride(Base):
    def test_late_convergence_rejected_and_no_cli_override(self):
        w = polished_world(self.sub(), polish_term='2026-10-17T10:00:01Z', qual_term='2026-10-17T20:00:00Z')
        self.assertDowngrade(self.check(w), 'relaxation', 'after the cutoff 2026-10-17T10:00:00Z')
        r = subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, 'cert_assert.py'), w.p['cert_pol'],
                            '--cutoff', '2026-10-30T00:00:00Z'], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 2)
        self.assertIn('unrecognized arguments', r.stderr)
        with self.assertRaises(TypeError):
            CA.Ctx(cutoff='2026-10-30T00:00:00Z')

    def _ext(self, w, logged, include_sha=True):
        conf = w.write('confirmation.txt', 'CERN confirms access until 2026-10-23 (personal data redacted)\n')
        sha = F.sha256_file(conf)
        w.write('wc_entry.md', f'## {logged[:16]}Z: Claude action note: CERN access extension\n- confirmation '
                               f'sha256 {sha if include_sha else H("other")}\n')
        return w.rec('ext', 'cern_extension', {'confirmed_end_date': '2026-10-23', 'logged_utc': logged},
                     {'confirmation': conf, 'work_chat_entry': w.p['wc_entry.md']})

    def test_verified_extension_shifts_and_forged_one_refused(self):
        w = polished_world(self.sub(), polish_term='2026-10-18T10:00:00Z', qual_term='2026-10-21T09:00:00Z')
        res = self.check(w, ext=self._ext(w, '2026-10-16T12:00:00Z'))
        self.assertEqual((res['verdict'], res['cutoff_utc']), ('CLAIMS_OK', '2026-10-19T10:00:00Z'))
        ext = w.p['ext']
        with open(ext, encoding='utf-8') as f:
            r = json.load(f)
        r['derived']['delta_days'] = 30
        with open(ext, 'w', encoding='utf-8') as f:
            json.dump(r, f)
        with self.assertRaises(CA.Malformed):
            CA.Ctx(extension=ext)
        with self.assertRaises(F.DeriveError):
            self._ext(w, '2026-10-16T12:00:00Z', include_sha=False)


class TestCodexExample3CandidateCannotBypassC3(Base):
    def test_candidate_width_with_c3_fail_rejected(self):
        res = self.check(polished_world(self.sub(), width=0.005, c3_status={0.005: 'FAIL'}))
        self.assertDowngrade(res, 'smearing', 'failed cell-specific C3 check at 0.005 Ry')

    def test_candidate_width_with_fresh_pass_accepted(self):
        self.assertEqual(self.check(polished_world(self.sub(), width=0.005))['verdict'], 'CLAIMS_OK')

    def test_candidate_width_needs_its_own_fresh_c3(self):
        res = self.check(polished_world(self.sub(), width=0.005, comp_start={0.005: 'density-seeded'}))
        self.assertDowngrade(res, 'smearing', 'no fresh C3 PASS with this run as the compared 0.005 Ry width')


class TestGateInventory(Base):
    def test_gate_pass_and_fails(self):
        self.assertEqual(self.check(gated_world(self.sub()), cert='cert')['verdict'], 'CLAIMS_OK')
        self.assertDowngrade(self.check(gated_world(self.sub(), gate_dF=2e-5), cert='cert'), 'relaxation',
                             'restart gate s1->s2 FAILED: |dF|')
        self.assertDowngrade(self.check(gated_world(self.sub(), gate_dforce=2e-3), cert='cert'), 'relaxation',
                             'restart gate s1->s2 FAILED: max |dF|')
        with self.assertRaises(F.DeriveError) as cm:          # v7: an unlinked restart is refused before any gate
            gated_world(self.sub(), carried_ok=False)
        self.assertEqual(str(cm.exception), 'segment_does_not_continue_the_previous_segment')

    def test_omitted_gate_and_dropped_segment(self):
        def drop(r):
            r['derived']['gates'] = []
            r['derived']['required_gates'] = []
        w = gated_world(self.sub(), edits={'lin': drop})
        self.assertDowngrade(self.check(w, cert='cert'), 'relaxation', 'not reproducible from its bound sources')
        with open(w.p['lin'], encoding='utf-8') as f:
            probs = CA.gate_inventory_problems(CA.Item(w.p['lin'], 'x', 'record', json.load(f)), 'relaxation')
        self.assertIn('mandatory restart gate s1->s2 missing', ' | '.join(probs))

        def cut(r):
            r['sources']['segments'] = r['sources']['segments'][1:]
        self.assertDowngrade(self.check(gated_world(self.sub(), edits={'lin': cut}), cert='cert'), 'relaxation',
                             'segments_not_contiguous_from_0')

    def test_a36_cell_needs_qualification(self):
        self.assertDowngrade(self.check(gated_world(self.sub(), qual=False), cert='cert'), 'relaxation',
                             'final qualification missing')


class TestWriters(Base):
    def test_allowlist_drops_decoys_and_settings_hash(self):
        w = World(self.sub())
        inp = F.read_pw_input(w.pw_in('x.in', RELAX_NL, geom(0)))
        q = F.read_qe_output(w.qe_out('x.out', [(None, -1.5, forces(0)), (geom(1), -1.6, forces(1))], final=geom(1)),
                             inp)
        self.assertEqual([e['F_Ry'] for e in q['evaluations']], [-1.5, -1.6])
        self.assertNotIn('5.4321', json.dumps(q))
        b = F.read_pw_input(w.pw_in('b.in', nl(control__calculation="'scf'", control__prefix="'q'",
                                               control__tprnfor='.true.', ions__ion_dynamics=None), geom(0)))
        c = F.read_pw_input(w.pw_in('c.in', nl(electrons__mixing_beta='0.1'), geom(0)))
        self.assertEqual(F.settings_sha256(inp), F.settings_sha256(b))
        self.assertNotEqual(F.settings_sha256(inp), F.settings_sha256(c))

    def _sel(self, snap_utc):
        w = World(self.sub())
        s0 = w.segment('sel', 's0', 400, GAUSS_NL, geom(0),
                       [(None, -100.000000, forces(0, 0.4)), (geom(1), -100.000008, forces(1, 1.0)),
                        (geom(2), -100.000016, forces(2, 4.0))], term='2026-10-16T00:00:00Z')
        i1 = w.pw_in('sel_s1/relax_s1_input.in', GAUSS_NL, geom(2))
        snap = w.qe_out('sel_s1/snapshot/relax.out', [(None, -100.000030, forces(2, 4.0))])
        o1 = w.qe_out('sel_s1/relax.out', [(None, -100.000030, forces(2, 4.0)), (geom(4), -100.000090, forces(4))])
        tar = w.relax_archive('sel_s1', 1, i1, o1, w.pw_in('sel_s1/returned/relax.in', GAUSS_NL, geom(4)),
                              'CONTINUE', mtime='2026-10-17T11:58:00Z')   # v6 layout; v7: ended after the cutoff
        meta = w.write('sel_s1/snapshot.json', json.dumps({'transfer_completed_utc': snap_utc,
                                                           'snapshot_sha256': F.sha256_file(snap),
                                                           'relax_in_sha256': F.sha256_file(i1)}))
        s1 = {'segment': 's1', 'cluster': 401, 'relax_in': i1, 'relax_out': o1,
              'joblog': w.joblog('sel_s1/relax.log', [(401, '2026-10-16T01:00:00Z', '2026-10-17T12:00:00Z')]),
              'export_manifest': w.archive_record('sel_s1/p0.id', [tar], 'sel', 401, 1), 'archives': [tar],
              'snapshot_out': snap, 'snapshot_meta': meta}
        w.rec('sel', 'cutoff_selection', {'cell': 'aIO_2p0_s1'}, {'segments': [s0, s1], 'offset_evidence': w.tz})
        with open(w.p['sel'], encoding='utf-8') as f:
            return w, json.load(f)['derived']

    def test_selection_snapshot_overhang_and_global_minimum_ties(self):
        w, d = self._sel('2026-10-17T09:58:00Z')
        self.assertEqual(((d['g_star']['segment'], d['g_star']['index']), len(d['overhang'])), (('s1', 0), 1))
        w, d = self._sel('2026-10-17T10:00:05Z')
        self.assertEqual(((d['g_star']['segment'], d['g_star']['index']), len(d['overhang'])), (('s0', 1), 2))
        w.cert('cert', 'aIO_2p0_s1', run_files('g'), d['g_star_geometry_sha256'], {'relaxation': ('exploratory', ['sel'])})
        self.assertEqual(self.check(w, cert='cert')['verdict'], 'CLAIMS_OK')


class TestEvidenceSemantics(Base):
    def test_unrelated_file_hash_ok_semantics_fail(self):
        w = polished_world(self.sub())
        w.write('unrelated.txt', 'relax evidence\n')
        w.cert('cert_x', w.cell, w.run_pol, w.g_pol, {'relaxation': ('converged', ['unrelated.txt'])})
        b = self.check(w, cert='cert_x')['blocks']['relaxation']
        self.assertEqual((b['hash_binding'], b['semantic'], b['permitted']), ('OK', 'FAIL', 'unknown'))

    def test_parent_lineage_never_polished_and_zero_step(self):
        with self.assertRaises(F.DeriveError) as cm:          # v7: an unregistered MV -> Gaussian switch is refused
            polished_world(self.sub(), mv_s1_nl=GAUSS_NL)
        self.assertEqual(str(cm.exception), 'settings_change_without_authorized_epoch_start')
        self.assertDowngrade(self.check(polished_world(self.sub(), cell='aIWO_2p0_s2')), 'geometry',
                             'can never be polished')
        self.assertEqual(self.check(polished_world(self.sub(), zero_step=True))['verdict'], 'CLAIMS_OK')

    def test_mv_geometry_not_qualified_by_polished_c3(self):
        w = polished_world(self.sub())
        w.cert('cert_mvq', w.cell, w.run_mv, w.g_mv,
               {'smearing': ('qualified', ['final_run_mv', 'a15', 'manifest', 'comp_002a', 'comp_005a'], 0.001)})
        self.assertDowngrade(self.check(w, cert='cert_mvq'), 'smearing', 'C3 coverage missing')

    def test_c3_alone_never_qualifies(self):
        w = polished_world(self.sub())
        w.cert('cert_x', w.cell, w.run_pol, w.g_pol,
               {'smearing': ('qualified', ['final_run_pol', 'manifest', 'comp_002a', 'comp_005a', 'cert_pol_v1'],
                             0.001)})
        self.assertDowngrade(self.check(w, cert='cert_x'), 'smearing', 'C3 reports alone never qualify')


class TestSightOutputStale(Base):
    def test_forbidden_key_aborts_and_no_echo(self):
        def leak(r):
            r['derived']['fermi_energy_eV'] = 5.123456
        res = self.check(polished_world(self.sub(), edits={'q_pol': leak}))
        self.assertEqual((res['verdict'], res['exit_code']), ('SIGHT_ABORT', 2))
        out = json.dumps(self.check(polished_world(self.sub())))
        for s in ('5.4321', '1.234567', 'host gap', '5.123456'):
            self.assertNotIn(s, out)

    def test_stale_cell_record(self):
        w = polished_world(self.sub())
        for name, cert in (('cell_v1.json', 'cert_pol_v1'), ('cell_v2.json', 'cert_pol')):
            w.sealed(name, {'schema': F.CELL_SCHEMA, 'cell': w.cell, 'geometry_sha256': w.g_pol,
                            'run_qualification': {'certificate_sha256': F.sha256_file(w.p[cert])},
                            'provenance': {'code_sha256': F.RC7_CODE_SHA256,
                                           'files': {k: {'sha256': v} for k, v in w.run_pol.items()}}})
        st = {s['file']: s['status'] for s in self.check(w, reports=['cell_v1.json', 'cell_v2.json'])['stale_reports']}
        self.assertEqual((st['cell_v1.json'], st['cell_v2.json']), ('STALE', 'CURRENT'))


class TestV3RegressionsRetained(Base):
    """v3 checks kept on the v4 fixtures (real-format logs, export manifests, frozen plan, derived roles)."""

    def test_tolerance_edges(self):
        self.assertDowngrade(self.check(polished_world(self.sub(), qual_dF=1.2e-5)), 'relaxation', '> 1e-05 Ry')
        self.assertDowngrade(self.check(polished_world(self.sub(), qual_dforce=1.5e-3)), 'relaxation',
                             '> 0.001 Ry/bohr')

    def _ext(self, w, logged):
        conf = w.write('confirmation.txt', 'CERN confirms access until 2026-10-23 (personal data redacted)\n')
        w.write('wc_entry.md', f'## {logged[:16]}Z: action note\n- confirmation sha256 {F.sha256_file(conf)}\n')
        return w.rec('ext', 'cern_extension', {'confirmed_end_date': '2026-10-23', 'logged_utc': logged},
                     {'confirmation': conf, 'work_chat_entry': w.p['wc_entry.md']})

    def test_late_extension_and_no_revival(self):
        w = polished_world(self.sub(), polish_term='2026-10-18T10:00:00Z', qual_term='2026-10-19T09:00:00Z')
        self.assertDowngrade(self.check(w, ext=self._ext(w, '2026-10-17T12:00:00Z')), 'relaxation',
                             'after the cutoff 2026-10-17T10:00:00Z')
        w = polished_world(self.sub(), qual_dF=1e-3)
        self.assertDowngrade(self.check(w, ext=self._ext(w, '2026-10-16T12:00:00Z')), 'relaxation',
                             'qualification FAILED')

    def test_c3_fail_at_other_width_and_tampered_report(self):
        self.assertDowngrade(self.check(polished_world(self.sub(), width=0.005, c3_status={0.002: 'FAIL'})),
                             'smearing', 'failed cell-specific C3 check at 0.002 Ry')
        self.assertDowngrade(self.check(polished_world(self.sub(), tamper_report='005a')), 'smearing',
                             'is not a sealed rc7 C3 report')

    def test_a15_audit_checks(self):
        self.assertDowngrade(self.check(polished_world(self.sub(), candidate=None)), 'smearing', 'candidate null')

        def other_code(r):
            r['derived']['audit_code_sha256'] = H('rc8')
        self.assertDowngrade(self.check(polished_world(self.sub(), edits={'a15': other_code})), 'smearing',
                             'not reproducible from its bound sources')

    def test_zero_step_reuse_of_another_run_rejected(self):
        w = polished_world(self.sub(), zero_step=True)
        w.rec('c4x', 'c4_polish', {'cell': w.cell},
              {'parent_certificate': w.p['cert_mv'], 'polish_lineage': w.p['lin_pol'], 'qualification': w.p['q_pol'],
               'reused_final': w.p['final_run_c005a']})
        w.cert('cert_x', w.cell, w.run_mv, w.g_mv, {'geometry': ('polished', ['c4x', 'final_run_mv'])})
        self.assertDowngrade(self.check(w, cert='cert_x'), 'geometry', 'zero-step reuse names other run files')

    def test_polish_smearing_parent_reference_and_inherited_failure(self):
        self.assertDowngrade(self.check(polished_world(self.sub(), polish_nl=nl(POLISH_NL, system__degauss='0.002'))),
                             'geometry', 'not a Gaussian 0.005 Ry relaxation')

        def no_parent(r):
            r['sources'].pop('parent')
            r['derived']['has_parent'] = False
        self.assertDowngrade(self.check(polished_world(self.sub(), edits={'lin_pol': no_parent})), 'relaxation',
                             'without a reference to its MV parent certificate')
        res = self.check(polished_world(self.sub(), mv_term='2026-10-18T00:00:00Z'))
        self.assertIn('MV parent relaxation not certified converged', self.why(res, 'geometry'))
        self.assertIn('inherited', self.why(res, 'relaxation'))

    def test_record_of_another_cell_and_other_writer_version(self):
        w = polished_world(self.sub())
        other = polished_world(self.sub(), cell='aIWO_1p0_s1')
        w.p['lin_other'] = other.p['lin_pol']
        w.cert('cert_x', w.cell, w.run_pol, w.g_pol, {'relaxation': ('converged', ['lin_other'])})
        self.assertDowngrade(self.check(w, cert='cert_x'), 'relaxation', 'no verified relaxation_lineage')

        def old(r):
            r['writer_sha256'] = H('older writer')
        self.assertDowngrade(self.check(polished_world(self.sub(), edits={'lin_pol': old})), 'relaxation',
                             'written by another writer version')

    def test_deny_assertion_output_allowlist_and_writer_cli(self):
        w = World(self.sub())
        inp = F.read_pw_input(w.pw_in('x.in', RELAX_NL, geom(0)))
        bad = w.write('bad.out', '!    total energy              =      -1.00000000 Ry\n'
                                 '     Forces acting on atoms (cartesian axes, Ry/au): Fermi energy follows\n')
        with self.assertRaises(F.SightAbort):
            F.read_qe_output(bad, inp)
        res = self.check(polished_world(self.sub()))
        self.assertLessEqual(set(res), set(CA.OUTPUT_KEYS))
        for b in res['blocks'].values():
            self.assertLessEqual(set(b), set(CA.BLOCK_KEYS))
        run = w.final('f', FINAL_NL, geom(2), cluster=5)
        spec = w.write('f/spec.json', json.dumps({'params': {'cell': 'aIWO_0p7_s1'},
                                                  'sources': {'final_in': 'scf.in', 'lineage_file': 'lineage_final.dat',
                                                              'certify_output': 'certify.json',
                                                              'export_manifest': 'exp/MANIFEST',
                                                              'archives': ['exp/final_small.tar.gz']}}))
        out = os.path.join(w.ev, 'fr.json')
        r = subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, 'f9_writers.py'), 'final_run', '--spec',
                            spec, '--out', out], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(os.path.isfile(run['in']) and os.path.isfile(out))

    def test_ungated_route_note(self):
        res = self.check(polished_world(self.sub()), cert='cert_mv')
        self.assertTrue(any('none required' in x for x in res['blocks']['relaxation']['notes']))


def reader_fingerprint(parent):
    d = os.path.join(parent, 'analysis')
    h = hashlib.sha256()
    for p in sorted(glob.glob(os.path.join(d, '*.py'))):
        h.update(os.path.basename(p).encode())
        with open(p, 'rb') as f:
            h.update(f.read())
    cache = os.path.join(d, '__pycache__')
    return h.hexdigest(), sorted(os.listdir(cache)) if os.path.isdir(cache) else []


class TestFrozenReaderCrossCheck(Base):
    def test_rc7_hash_gate_accepts_what_f9_rejects(self):
        if not os.path.isdir(os.path.join(READER_PARENT, 'analysis')):
            self.skipTest('frozen reader not found')
        before = reader_fingerprint(READER_PARENT)
        sys.dont_write_bytecode = True
        sys.path.insert(0, READER_PARENT)
        try:
            from analysis import certify as CERT   # noqa: E402
        except ImportError as e:
            self.skipTest(f'frozen reader not importable in this interpreter mode ({e}); run with python -E -B')
        finally:
            sys.path.remove(READER_PARENT)
        w = polished_world(self.sub(), polish_nl=nl(POLISH_NL, control__forc_conv_thr='0.1'), polish_last_max=0.01)
        with open(w.p['cert_pol'], encoding='utf-8') as f:
            cert = json.load(f)
        ok, prob = CERT._evidence_ok(cert['relaxation'], os.path.dirname(w.p['cert_pol']))
        self.assertTrue(ok, prob)
        self.assertEqual(CERT.geometry_hash(['In'], [[1.23456, 0.0, 0.0]], CELL),
                         F.geometry_hash(['In'], [[1.23456, 0.0, 0.0]], CELL))
        self.assertEqual(self.check(w)['blocks']['relaxation']['semantic'], 'FAIL')
        self.assertEqual(reader_fingerprint(READER_PARENT), before)
        self.assertEqual(before[0], F.RC7_CODE_SHA256)


if __name__ == '__main__':
    unittest.main(verbosity=2)
