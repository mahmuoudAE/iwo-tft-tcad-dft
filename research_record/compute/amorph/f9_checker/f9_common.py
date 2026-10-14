"""f9_common.py: frozen definitions shared by the D-42 F9 record writers (f9_writers.py) and the checker
(cert_assert.py). Draft v15, 2026-10-14. Standard library only; nothing is imported from the frozen reader rc7.

v4: force-block identities (indices 1..N once, types = input), registered ionic thresholds, export-manifest
binding, HTCondor 'MM/DD HH:MM:SS' headers with year and zone from bound offset evidence, converged_at_cutoff.
v5: D-24 MANIFEST format, archive-member provenance (hashes recomputed from the listed archive), as-run scf.in
hash from the certified lineage file, job dispositions.
v6: attempt artifact inventory (read_attempt_inventory), 'removed_while_held' disposition, terminal_utc; D-24
relaxation-segment member names (relax_s<k>_input.in, relax_s<k>_lineage.log) and the job check.
v7: archive-identity records (run, cluster, k) and the in-job member-time window; export_manifest_final.dat; guard-only
attempts, D-24 transition resets and pre-item-B checkpoints; authorized epoch starts; inherited gate boundaries.
v8: exact registered transitions and triggers (A35/A36), job-history parser, section-3 transition records, first
execution times, mandatory gates from the rescue start (earlier comparisons diagnostic), label-resolved epochs.
v9 (Codex v8 review, FIX_FIRST): the registered fresh start of every relaxation segment (defaults resolved);
bestvalid recomputed from the bound evaluations; section-3 rescues need a registered authorization (once-use,
remaining executions preserved, exhaustion or a prospective suspension rule; transition schema /2); no transition
after a terminal rescue failure; label splits only in the A25/A30/A34 scope; the registered FINAL template.
v10 (Codex v9 review, FIX_FIRST): the DAG allowance is bound from the first attempt (9 node executions; guard-only
attempts count, an eviction inside one cluster does not; A39's administrative rescue adds 9, once per chain, after
exhaustion only); a suspension rule must predate the actual pause start; a result-informed continuation amendment is
its own basis (logged after the pause start, before resumption, preserving the state); relabeling needs the registered
construction (alternating map, balanced counts, construction equivalence, authorized cell and resource route);
system.ntyp leaves the epoch key (a split changes it); an [infra] failure reset keeps the segment input.
v11 (Codex v10 review, FIX_FIRST): a split needs BOTH registered alternating splits (In and O); the rescue file's
remaining RETRY is bound (DAGMAN_RESET_RETRIES_UPON_RESCUE = False plus count enforcement); a historical (A15-era)
rescue is its own basis with its contemporaneous authorization; the resource route is bound to the split segment's
own cluster (request, Requirements, environment).
v12 (Codex v11 review, FIX_FIRST): the Requirements expression must be a top-level conjunction containing the exact
positive H100 clause and the exact negated MIG clause (no OR bypass, no negated H100); environment assignments must be
unique and equal the route's values (A29 permits NV_ACC_MEM_MANAGE=0 for aIO_2p0_s1); the [infra] bestvalid exception
is bound to the D-37 / A34(ii) chains and a rollback (restoration) record.
v13 (Codex v12 review, FIX_FIRST): an escape-aware ClassAd tokenizer (string escapes; no top-level ||, ?: ); both
predicates on the audited GPU attribute TARGET.GPUs_DeviceName; the [infra] bestvalid exception DISABLED until its
restoration evidence (rule, restored input/labels and request, failure evidence) is supported; registered transitions
keyed on the scientific position (node executions before the segment), preserved across administrative renumbering;
A43 count-enforcement files (DAG identity, config, exact RETRY, dry run, dagman.out header).
v14 (Codex v13 review, FIX_FIRST): the A43 submission binding - the reviewed dry-run .condor.sub is exactly one
scheduler-universe DAGMan with the audited executable and run directory and only permitted arguments; the submit record
names one cluster; the submitted DAGMan ad (universe, Cmd, Iwd, Arguments) equals the reviewed file; the A43 dagman.out
names that DAGMan cluster and the first resumed RELAX node cluster.
v15 (Codex 2026-10-14T08:59Z): the arguments of the dry run are parsed with HTCondor's new-syntax quoting rules (whitespace
separates arguments; single quotes group, '' is a literal quote; "" a literal double quote) and every resulting argument is
whitelisted; the submit file may contain only `key = value` lines and one `queue` - include, conditionals, error/warning
directives and line continuations are refused.

Frozen here (D-42 F9 v3):
  * registered dates and tolerances (no command-line override exists anywhere);
  * SETTINGS_FIELDS: the field set of the settings hash;
  * the A39(a6) allowlist reader of QE text output, with its deny assertion;
  * the pw.x input reader (ibrav = 0), the rc7 geometry hash, HTCondor job-log timing with explicit time zones;
  * the restart-gate inventory rule.
"""
import datetime as dt
import gzip
import hashlib
import json
import math
import os
import re
import tarfile

# ---------------------------------------------------------------- frozen constants
RECORD_SCHEMA = 'iwo-f9-evidence/2'
CERT_SCHEMA = 'iwo-amorph-analysis/certificate/2'
CELL_SCHEMA = 'iwo-amorph-analysis/cell/3'
RC7_CODE_SHA256 = 'fff642a13a62db6d0cde3e4704cdbf343913fc1972d9fa95d79f7ad8f4e01158'   # D-32, recomputed 2026-10-12

CUTOFF_UTC = '2026-10-17T10:00:00Z'                  # section 3 relaxation cutoff
QUALIFICATION_DEADLINE_UTC = '2026-10-20T12:00:00Z'   # primary qualifications and single-point controls
EXPLORATORY_EXPORT_DEADLINE_UTC = '2026-10-20T18:00:00Z'   # A39 exploratory read-outs, verified off CERN
LAST_SUBMISSION_UTC = '2026-10-18T22:00:00Z'
ACCESS_END_DATE = '2026-10-21'

REGISTERED_FORC_CONV_THR = 1e-3   # A19/A35/A36: forc_conv_thr (Ry/bohr), required
REGISTERED_ETOT_CONV_THR = 1e-4   # A19/A35/A36: etot_conv_thr (Ry), required
QE_DEFAULT_FORC_CONV_THR = 1e-3   # QE INPUT_PW defaults (used only when the key is absent; recorded as such)
QE_DEFAULT_ETOT_CONV_THR = 1e-4
GATE_DF_RY = 1e-5             # A25/A35 energy tolerance (inclusive)
GATE_DFORCE_RY_BOHR = 1e-3    # A35 max |dF| tolerance over all force components (inclusive)
BOHR_A = 0.529177210903       # rc7 register.BOHR_A
GEOMETRY_HASH_DECIMALS = 4    # rc7 register.GEOMETRY_HASH_DECIMALS

GATED_CELLS = ('aIWO_0p8_s2', 'aIWO_2p0_s2', 'aIWO_2p0_comp_s1')   # A35, A36
GATED_ROUTES = ('A35', 'A36', 'A36-conditional', 'C4-polish')     # C4-polish: D-42 F5 v3 (new)
ROUTES = ('registered-MV', 'registered-Gaussian') + GATED_ROUTES

# The settings hash covers exactly these pw.x fields (namelist.variable, indices kept) plus the cards
# ATOMIC_SPECIES (label, mass, UPF file, in order), K_POINTS (type and values), the per-atom label sequence and the
# cell (A, rounded like the geometry hash). Everything else is excluded on purpose, notably: calculation, title,
# prefix, outdir, pseudo_dir, restart_mode, startingpot, startingwfc, max_seconds, verbosity, disk_io, wf_collect,
# tprnfor, tstress, iprint, forc_conv_thr, etot_conv_thr, nstep, ion_dynamics, upscale, bfgs_ndim, trust_radius_*,
# w_1, w_2 (run control, restart and relaxation-driver keys, which differ legitimately between a relax, its
# qualification SCF and a FINAL). Frozen for F9 v3; any change is a new F9 version.
SETTINGS_FIELDS = (
    'control.tefield', 'control.dipfield', 'control.lelfield', 'control.lorbm',
    'system.ibrav', 'system.nat', 'system.ntyp', 'system.ecutwfc', 'system.ecutrho', 'system.ecutfock',
    'system.occupations', 'system.smearing', 'system.degauss', 'system.nspin', 'system.nbnd', 'system.tot_charge',
    'system.tot_magnetization', 'system.starting_magnetization', 'system.input_dft', 'system.exx_fraction',
    'system.screening_parameter', 'system.nqx1', 'system.nqx2', 'system.nqx3', 'system.assume_isolated',
    'system.edir', 'system.emaxpos', 'system.eopreg', 'system.eamp', 'system.nosym', 'system.noinv',
    'system.vdw_corr', 'system.lda_plus_u', 'system.hubbard_u', 'system.noncolin', 'system.lspinorb',
    'electrons.conv_thr', 'electrons.mixing_beta', 'electrons.mixing_mode', 'electrons.mixing_ndim',
    'electrons.electron_maxstep', 'electrons.diagonalization', 'electrons.diago_full_acc',
    'electrons.scf_must_converge',
)
SETTINGS_CARDS = ('atomic_species', 'k_points', 'labels', 'cell_A')
START_FIELDS = ('electrons.startingpot', 'electrons.startingwfc', 'control.restart_mode')
RUN_NAME_FIELDS = ('control.prefix', 'control.outdir', 'control.title')

# ---------------------------------------------------------------- A39(a6) allowlist for QE text output
_NUM = r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eEdD][-+]?\d+)?'
RX_ENERGY = re.compile(r'^!\s+total energy\s+=\s+(' + _NUM + r')\s+Ry\s*$')
RX_FORCES_HEAD = re.compile(r'^\s*Forces acting on atoms')
RX_FORCE_ROW = re.compile(r'^\s*atom\s+(\d+)\s+type\s+(\d+)\s+force\s+=\s+(' + _NUM + r')\s+(' + _NUM + r')\s+('
                          + _NUM + r')\s*$')
RX_TOTAL_FORCE = re.compile(r'^\s*Total force\s+=\s+(' + _NUM + r')\s+Total SCF correction\s+=\s+(' + _NUM + r')')
RX_SCF_OK = re.compile(r'^\s*convergence has been achieved')
RX_SCF_FAIL = re.compile(r'^\s*convergence NOT achieved')
RX_BFGS_CONV = re.compile(r'^\s*bfgs converged')
RX_BFGS_END = re.compile(r'^\s*End of BFGS Geometry Optimization')
RX_FINAL_BEGIN = re.compile(r'^\s*Begin final coordinates')
RX_FINAL_END = re.compile(r'^\s*End final coordinates')
RX_POS_HEAD = re.compile(r'^\s*ATOMIC_POSITIONS\s*[({]?\s*([A-Za-z_]*)\s*[)}]?\s*$')
RX_POS_ROW = re.compile(r'^\s*([A-Za-z][A-Za-z0-9_]*)\s+(' + _NUM + r')\s+(' + _NUM + r')\s+(' + _NUM + r')'
                        r'(?:\s+[01]\s+[01]\s+[01])?\s*$')
RX_JOB_DONE = re.compile(r'^\s*JOB DONE')
DENY = re.compile(r'fermi energ|bands \(ev\)|highest occupied|lowest unoccupied|eigenval', re.I)


class SightAbort(Exception):
    pass


class DeriveError(Exception):
    """A record cannot be derived from its sources (reason is a short checker-safe phrase)."""


# ---------------------------------------------------------------- hashing and small helpers
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _strip(obj):
    if isinstance(obj, dict):
        return {k: _strip(v) for k, v in obj.items() if k not in ('meta', 'self_sha256')}
    if isinstance(obj, list):
        return [_strip(v) for v in obj]
    return obj


def canonical_sha256(obj):
    """Identical to rc7 certify.canonical_sha256."""
    return hashlib.sha256(json.dumps(_strip(obj), sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def verify_seal(obj):
    try:
        return isinstance(obj, dict) and obj.get('self_sha256') is not None and \
            obj['self_sha256'] == canonical_sha256(obj)
    except (TypeError, ValueError):
        return False


def ffloat(s):
    return float(str(s).strip().lower().replace('d', 'e'))


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def element_of(label):
    """rc7 qeio.element_of: 'In1' -> 'In', 'O2' -> 'O' (A25 split labels)."""
    s = re.sub(r'[^A-Za-z]', '', label)
    return s[:1].upper() + s[1:].lower() if s else s


def geometry_hash(species, pos_A, cell_A):
    """rc7 certify.geometry_hash: species, positions and cell rounded to 1e-4 A, canonical JSON, sha256."""
    d = GEOMETRY_HASH_DECIMALS
    payload = {'species': list(species), 'positions': [[round(float(x), d) + 0.0 for x in p] for p in pos_A],
               'cell': [[round(float(x), d) + 0.0 for x in v] for v in cell_A]}
    return canonical_sha256(payload)


def parse_utc(s):
    if not isinstance(s, str) or not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', s):
        return None
    try:
        return dt.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def fmt_utc(t):
    return t.strftime('%Y-%m-%dT%H:%M:%SZ') if isinstance(t, dt.datetime) else None


def family(s):
    s = str(s or '').strip().lower()
    if s in ('gaussian', 'gauss'):
        return 'gaussian'
    if s in ('mv', 'm-v', 'marzari-vanderbilt', 'cold'):
        return 'mv'
    return s or None


# ---------------------------------------------------------------- registered dates (+ A39(e) extension only)
def registered_dates(extension=None):
    """The registered dates, shifted only by a verified cern_extension record (derived block): every date not yet
    passed when the confirmation was logged moves by delta_days; nothing else moves them."""
    base = {'cutoff': parse_utc(CUTOFF_UTC), 'qualification': parse_utc(QUALIFICATION_DEADLINE_UTC),
            'exploratory_export': parse_utc(EXPLORATORY_EXPORT_DEADLINE_UTC),
            'last_submission': parse_utc(LAST_SUBMISSION_UTC)}
    if not extension:
        return base
    logged = parse_utc(extension.get('logged_utc'))
    delta = extension.get('delta_days')
    if logged is None or not isinstance(delta, int) or isinstance(delta, bool) or delta < 0:
        raise DeriveError('extension_malformed')
    shift = dt.timedelta(days=delta)
    return {k: (v + shift if logged < v else v) for k, v in base.items()}


# ---------------------------------------------------------------- pw.x input
def _strip_comment(line):
    out, q = [], None
    for ch in line:
        if q:
            out.append(ch)
            if ch == q:
                q = None
        elif ch in ('"', "'"):
            q = ch
            out.append(ch)
        elif ch in ('!', '#'):
            break
        else:
            out.append(ch)
    return ''.join(out)


def _norm_value(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
        return v[1:-1].strip().lower()
    lv = v.lower()
    if lv in ('.true.', '.t.', 'true', 't'):
        return True
    if lv in ('.false.', '.f.', 'false', 'f'):
        return False
    try:
        if re.fullmatch(r'[-+]?\d+', v):
            return int(v)
        return ffloat(v)
    except ValueError:
        return lv


def read_pw_input(path):
    """ibrav = 0 pw.x input: namelist fields, cards, labels, positions and cell in A. Never reads an output."""
    with open(path, encoding='utf-8', errors='replace') as f:
        return _parse_pw_input([l.rstrip('\n') for l in f])


def read_pw_input_bytes(data):
    """v7: the same parser on the bytes of an archive member (e.g. a segment's returned relax.in)."""
    return _parse_pw_input(data.decode('utf-8', 'replace').splitlines())


def _parse_pw_input(lines_in):
    raw = [_strip_comment(l) for l in lines_in]
    fields, i, n = {}, 0, len(raw)
    cards_start = None
    while i < n:
        s = raw[i].strip()
        if s.startswith('&'):
            nl = s[1:].split()[0].lower()
            body = []
            i += 1
            while i < n and raw[i].strip() != '/':
                body.append(raw[i])
                i += 1
            text = ' '.join(body)
            for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(\s*([^)]*)\s*\))?\s*=\s*("[^"]*"|\'[^\']*\'|[^,\s]+)',
                                 text):
                key = f'{nl}.{m.group(1).lower()}'
                if m.group(2) is not None:
                    key += '(' + re.sub(r'\s+', '', m.group(2)) + ')'
                if key in fields:
                    raise DeriveError('input_repeated_assignment')
                fields[key] = _norm_value(m.group(3))
        elif s and cards_start is None and not s.startswith('&') and s != '/':
            cards_start = i
            break
        i += 1
    lines = raw[cards_start:] if cards_start is not None else []
    nat = fields.get('system.nat')
    if not isinstance(nat, int) or nat <= 0:
        raise DeriveError('input_nat_missing')
    if fields.get('system.ibrav', 0) != 0:
        raise DeriveError('input_ibrav_not_0')

    def card(name):
        idx = [k for k, l in enumerate(lines) if l.strip().upper().startswith(name)]
        if not idx:
            return None, None
        k = idx[-1]
        unit = re.sub(r'[(){}]', ' ', lines[k]).split()[1:2]
        return k, (unit[0].lower() if unit else '')

    alat = None
    if 'system.celldm(1)' in fields:
        alat = float(fields['system.celldm(1)']) * BOHR_A
    elif 'system.a' in fields:
        alat = float(fields['system.a'])
    k, cu = card('CELL_PARAMETERS')
    if k is None:
        raise DeriveError('input_cell_missing')
    cell = [[ffloat(x) for x in lines[k + j].split()[:3]] for j in (1, 2, 3)]
    if cu == 'bohr':
        cell = [[x * BOHR_A for x in v] for v in cell]
    elif cu in ('alat', ''):
        if alat is None:
            raise DeriveError('input_alat_missing')
        cell = [[x * alat for x in v] for v in cell]
    k, pu = card('ATOMIC_POSITIONS')
    if k is None:
        raise DeriveError('input_positions_missing')
    rows = [l for l in lines[k + 1:] if l.strip()][:nat]
    if len(rows) != nat:
        raise DeriveError('input_positions_count')
    labels, frac = [], []
    for r in rows:
        p = r.split()
        labels.append(p[0])
        frac.append([ffloat(x) for x in p[1:4]])
    pos = to_cartesian(frac, pu or 'alat', cell, alat)
    ks, _ = card('ATOMIC_SPECIES')
    species_block = []
    if ks is not None:
        for l in lines[ks + 1:]:
            p = l.split()
            if len(p) < 3 or p[0].upper() in ('ATOMIC_POSITIONS', 'K_POINTS', 'CELL_PARAMETERS'):
                break
            species_block.append([p[0], ffloat(p[1]), p[2]])
            if len(species_block) == fields.get('system.ntyp'):
                break
    kk, ku = card('K_POINTS')
    kpts = [ku or 'tpiba']
    if kk is not None and ku == 'automatic':
        kpts += [int(x) for x in lines[kk + 1].split()[:6]]
    type_of = {sb[0]: k + 1 for k, sb in enumerate(species_block)}
    atom_types = [type_of.get(l) for l in labels]
    if not species_block or None in atom_types:
        raise DeriveError('input_atom_label_without_atomic_species_entry')
    return {'fields': fields, 'labels': labels, 'species': [element_of(l) for l in labels], 'positions_A': pos,
            'cell_A': cell, 'alat_A': alat, 'atomic_species': species_block, 'k_points': kpts, 'nat': nat,
            'atom_types': atom_types}


def ionic_thresholds(inp):
    """(forc_conv_thr, etot_conv_thr, sources): explicit &CONTROL values, else the QE defaults (1e-3, 1e-4)."""
    f = inp['fields']
    fc, ec = f.get('control.forc_conv_thr'), f.get('control.etot_conv_thr')
    return ((float(fc) if finite(fc) else QE_DEFAULT_FORC_CONV_THR),
            (float(ec) if finite(ec) else QE_DEFAULT_ETOT_CONV_THR),
            {'forc_conv_thr': 'explicit' if finite(fc) else 'qe_default',
             'etot_conv_thr': 'explicit' if finite(ec) else 'qe_default'})


IDENTITY_SCHEMA = 'iwo-f9-archive-identity/1'
RX_ID_RUN = re.compile(r'#\s*run\s+(\S+)\s*')
RX_ID_ENTRY = re.compile(r'([A-Za-z0-9][A-Za-z0-9._+-]*)\s+(\d+)\s+([0-9a-f]{64})\s+cluster\s+(\d+)(?:\s+k\s+(\d+))?\s*')
D24F_ON_EOS = ('XRD_ADLER32', 'XRD_SIZE', 'FUSE_SIZE', 'PULLED')       # steps_final.sh.D24:264-266
D24F_STATUSES = D24F_ON_EOS + ('FAILED', 'SKIPPED')
RX_D24F_HEAD = re.compile(r'#\s*D-24 export of (\S+) \(cluster (\d+)\), (\S+); EOS directory (\S+)\s*')
RX_D24F_ENTRY = re.compile(r'(\S+)\s+(\d+)\s+([0-9a-f]{64})\s+(' + '|'.join(D24F_STATUSES) + r')\s*')


def _read_identity(lines):
    """v7 (Codex v6 review item 3): the archive-identity record of returned archives, one line per archive:
        # iwo-f9-archive-identity/1
        # run <name>
        <basename> <bytes> <sha256> cluster <ClusterId> [k <segment>]
    It binds run, cluster (and k) to each archive's hash; the writers cross-check every claim against the job log
    (execution window of the cluster) and the archive's own members."""
    run, entries, ident = None, [], {}
    for line in lines[1:]:
        m = RX_ID_RUN.fullmatch(line)
        if m:
            if run is not None:
                raise DeriveError('archive_identity_record_malformed')
            run = m.group(1)
            continue
        m = RX_ID_ENTRY.fullmatch(line)
        if not m or m.group(1) in ident:
            raise DeriveError('archive_identity_record_malformed')
        entries.append((m.group(3), m.group(1), int(m.group(2))))
        ident[m.group(1)] = (int(m.group(4)), int(m.group(5)) if m.group(5) is not None else None)
    if run is None or not entries:
        raise DeriveError('archive_identity_record_malformed')
    return {'format': 'identity', 'entries': entries, 'identity': ident, 'run': run, 'cluster': None,
            'written_utc': None, 'eos_dest': None}


def _read_d24_final(lines):
    """v7 (Codex ruling on a missing exp/MANIFEST): export_manifest_final.dat (steps_final.sh.D24:257-270), written
    in-job after the copies: the header '# D-24 export of <name> (cluster <N>), <utc>; EOS directory <dest>' and one
    '<file> <bytes> <sha256> <status>' line per exported file. Only files declared on EOS (XRD_*, FUSE_SIZE, PULLED)
    can bind; FAILED / SKIPPED files are declared but not exported."""
    head, declared = [], []
    for line in lines:
        m = RX_D24F_HEAD.fullmatch(line)
        if m:
            head.append(m)
            continue
        if line.startswith('#'):
            continue
        m = RX_D24F_ENTRY.fullmatch(line)
        if not m:
            raise DeriveError('export_manifest_line_malformed')
        declared.append((m.group(3), m.group(1), int(m.group(2)), m.group(4)))
    if len(head) != 1 or not declared or parse_utc(head[0].group(3)) is None:
        raise DeriveError('export_manifest_final_malformed')
    h = head[0]
    return {'format': 'd24_final', 'run': h.group(1), 'cluster': int(h.group(2)), 'written_utc': parse_utc(h.group(3)),
            'eos_dest': h.group(4), 'declared': declared,
            'entries': [(s, n, b) for s, n, b, st in declared if st in D24F_ON_EOS]}


def read_export_manifest(path):
    """v5: two formats.
      * sha256sum: '<sha256>  [*]<path>' per line;
      * D-24 exp/MANIFEST (steps_final.sh.D24:226-233): '# eos_dest ...', '# run <name> cluster <N> written_utc <t>',
        then '<basename> <bytes> <sha256>' per exported file (archives and compressed files).
    v7: also the archive-identity record (_read_identity) and export_manifest_final.dat (_read_d24_final); the D-24
    MANIFEST's '# eos_dest' is kept.
    Returns {'format', 'entries': [(sha256, basename, bytes|None)], 'run': name|None, 'cluster': int|None, ...}."""
    with open(path, encoding='utf-8', errors='replace') as f:
        lines = [l.rstrip('\r\n') for l in f if l.strip()]
    if lines and lines[0].strip() == '# ' + IDENTITY_SCHEMA:
        return _read_identity(lines)
    if any(RX_D24F_HEAD.fullmatch(l) for l in lines):
        return _read_d24_final(lines)
    entries, run, cluster, fmt, written, dest = [], None, None, None, None, None
    for line in lines:
        m = re.match(r'^#\s*eos_dest\s+(\S+)\s*$', line)
        if m:
            dest = m.group(1)
            continue
        m = re.match(r'^#\s*run\s+(\S+)\s+cluster\s+(\d+)(?:\s+written_utc\s+(\S+))?', line)
        if m:
            run, cluster, written = m.group(1), int(m.group(2)), parse_utc(m.group(3) or '')
            continue
        if line.startswith('#') or not line.strip():
            continue
        m = re.fullmatch(r'([0-9a-f]{64})\s+\*?(\S.*?)\s*', line)
        if m and fmt in (None, 'sha256sum'):
            fmt = 'sha256sum'
            entries.append((m.group(1), m.group(2).replace('\\', '/').rsplit('/', 1)[-1], None))
            continue
        m = re.fullmatch(r'(\S+)\s+(\d+)\s+([0-9a-f]{64})\s*', line)
        if m and fmt in (None, 'd24'):
            fmt = 'd24'
            entries.append((m.group(3), m.group(1), int(m.group(2))))
            continue
        raise DeriveError('export_manifest_line_malformed')
    if not entries:
        raise DeriveError('export_manifest_empty')
    return {'format': fmt, 'entries': entries, 'run': run, 'cluster': cluster, 'written_utc': written,
            'eos_dest': dest}


def _basename(p):
    return str(p).replace('\\', '/').rsplit('/', 1)[-1]


def _listed(manifest, path):
    """The file at `path` is itself listed (basename, sha256, and size where the manifest gives one)."""
    sha, base, size = sha256_file(path), _basename(path), os.path.getsize(path)
    return any(s == sha and n == base and (b is None or b == size) for s, n, b in manifest['entries'])


def _tar_member(archive_path, name, want):
    """(bytes, mtime) of member `name` (basename match, regular files only), read in memory; None if absent."""
    hits = []
    with tarfile.open(archive_path, 'r:*') as t:
        for m in t.getmembers():
            if m.isfile() and _basename(m.name) == name:
                hits.append((t.extractfile(m).read() if want == 'bytes' else None, int(m.mtime)))
    if len(hits) > 1:
        raise DeriveError('archive_member_ambiguous')
    return hits[0] if hits else None


def archive_member_bytes(archive_path, name):
    """v7: the bytes of a tar(.gz) member (never written to disk); None if absent."""
    if not archive_path.endswith(('.tar.gz', '.tgz', '.tar')):
        return None
    hit = _tar_member(archive_path, name, 'bytes')
    return hit[0] if hit else None


def archive_member_mtime(archive_path, name):
    """v7: the mtime (UTC) that tar recorded for a member when the archive was packed (in-job); None if absent."""
    if not archive_path.endswith(('.tar.gz', '.tgz', '.tar')):
        return None
    hit = _tar_member(archive_path, name, 'mtime')
    return dt.datetime.fromtimestamp(hit[1], dt.timezone.utc) if hit else None


def archive_member_sha256(archive_path, name):
    """sha256 of member `name` (basename match, regular files only) recomputed from the archive bytes; None if absent.
    tar(.gz) archives are read in memory (never extracted to disk); a single '.gz' holds one member (name without .gz)."""
    if archive_path.endswith(('.tar.gz', '.tgz', '.tar')):
        data = archive_member_bytes(archive_path, name)
        return hashlib.sha256(data).hexdigest() if data is not None else None
    if archive_path.endswith('.gz'):
        if _basename(archive_path)[:-3] != name:
            return None
        with gzip.open(archive_path, 'rb') as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    return None


# ---------------------------------------------------------------- v6: D-24 relaxation-segment archive members
# Codex 2026-10-13 (blocking 2). Segment k of a chain runs as JOB relax_s<k> (relax_node.sh:16 SEG=${1:-0}; :47
# driver.sh "relax_s${SEG}"; d24_transition.sh:90 JOB=relax_s$k) and returns relax_s<k>_results.tar.gz (:4, :48).
# steps_relax.sh saves the as-run input right after pw.x (:19-20 'run_pw relax 1' / 'cp relax.in "${JOB}_input.in"')
# and then REPLACES relax.in with the final geometry (:30, CONVERGED) or the selected next one (:35, CONTINUE); its
# first lineage line is 'segment ${JOB}: <STATUS>' in ${JOB}_lineage.log (:51-56). lineage_relax.sh.D24:8-10: the
# archive's relax.in is the segment's OUTPUT. Segments without relax_s<k>_input.in (pre-item-B) are a provenance gap.
SEGMENT_ARCHIVE = '{job}_results.tar.gz'
SEGMENT_SAVED_INPUT = '{job}_input.in'
SEGMENT_LINEAGE_LOG = '{job}_lineage.log'
SEGMENT_RETURNED_RELAX_IN = 'relax.in'
RX_SEGMENT_LINEAGE = re.compile(r'^segment (relax_s\d+): (CONVERGED|CONTINUE|FAILED)(?: \[(\w+)\])?')


def segment_job(k):
    return f'relax_s{int(k)}'


def archive_member_first_line(archive_path, name, limit=256):
    """The first line (at most `limit` bytes) of member `name` of a tar(.gz) archive, read in memory; None if absent.
    Nothing else of the member is read."""
    hits = []
    with tarfile.open(archive_path, 'r:*') as t:
        for m in t.getmembers():
            if m.isfile() and _basename(m.name) == name:
                hits.append(t.extractfile(m).read(limit).split(b'\n', 1)[0].decode('utf-8', 'replace'))
    if len(hits) > 1:
        raise DeriveError('archive_member_ambiguous')
    return hits[0] if hits else None


def segment_lineage_job(archive_path, job):
    """The JOB named by the archive's own <job>_lineage.log (first line only: job and status tokens are kept)."""
    first = archive_member_first_line(archive_path, SEGMENT_LINEAGE_LOG.format(job=job))
    if first is None:
        raise DeriveError('segment_lineage_log_missing')
    m = RX_SEGMENT_LINEAGE.match(first)
    if not m or m.group(1) != job:
        raise DeriveError('segment_lineage_log_names_another_job')
    return m.group(1), m.group(2), m.group(3)        # v8: + the FAILED category ([scf], [infra], ...)


def bind_exported(manifest, archives, name, sha, what):
    """v5 (Codex 20:44Z item 4): content `sha` is the exported file `name`: listed directly in the manifest, or a member
    `name` of an archive that is itself listed (sha256 and size), with the member hash RECOMPUTED from the archive.
    A member manifest generated later is never accepted as provenance."""
    # direct listing counts only in the in-job D-24 MANIFEST; a sha256sum list may vouch for archives only (a member
    # list generated later is not historical provenance)
    # v7: export_manifest_final.dat lists only files declared on EOS in 'entries'
    if manifest['format'] in ('d24', 'd24_final') and any(s == sha and n == name for s, n, b in manifest['entries']):
        return 'direct'
    for a in archives or []:
        if _listed(manifest, a) and archive_member_sha256(a, name) == sha:
            return 'member:' + _basename(a)
    raise DeriveError(f'{what}_not_bound_to_the_historical_export')


def bind_exported_file(manifest, archives, path, name, what):
    return bind_exported(manifest, archives, name, sha256_file(path), what)


def bind_run_files(manifest, archives, run_files):
    return {name: bind_exported(manifest, archives, _basename(name), sha, 'certified_run_file')
            for name, sha in sorted(run_files.items())}


RX_ASRUN = re.compile(r'^sha256 ([0-9a-f]{64}) scf\.in as-run \((.*)\)\s*$')


def asrun_scf_input(lineage_path):
    """v5 (Codex item 2): the sha256 of scf.in as pw.x read it, from the D-24 lineage file (steps_final.sh.D24:193-200:
    'sha256 <h> scf.in as-run (max_seconds = ...; identical to the pre-run scf.in apart from max_seconds: yes|NO)').
    Returns (sha256, identical_apart_from_max_seconds). A missing or repeated line is a provenance gap."""
    hits = []
    with open(lineage_path, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = RX_ASRUN.match(line.strip())
            if m:
                hits.append((m.group(1), 'apart from max_seconds: yes' in m.group(2)))
    if len(hits) != 1:
        raise DeriveError('lineage_without_unique_asrun_scf_input')
    return hits[0]


def to_cartesian(rows, unit, cell, alat):
    unit = (unit or 'alat').lower()
    if unit == 'angstrom':
        return [list(map(float, r)) for r in rows]
    if unit == 'bohr':
        return [[x * BOHR_A for x in r] for r in rows]
    if unit == 'crystal':
        return [[sum(r[i] * cell[i][j] for i in range(3)) for j in range(3)] for r in rows]
    if unit == 'alat':
        if alat is None:
            raise DeriveError('positions_alat_without_alat')
        return [[x * alat for x in r] for r in rows]
    raise DeriveError('positions_unit_unsupported')


def input_geometry_hash(inp):
    return geometry_hash(inp['species'], inp['positions_A'], inp['cell_A'])


def settings_block(inp):
    """The frozen settings of an input (SETTINGS_FIELDS + SETTINGS_CARDS), normalised."""
    f = inp['fields']
    out = {}
    for key in SETTINGS_FIELDS:
        for k, v in f.items():
            if k == key or k.startswith(key + '('):
                out[k] = family(v) if k == 'system.smearing' else v
    out['atomic_species'] = [[l, round(m, 6), p] for l, m, p in inp['atomic_species']]
    out['k_points'] = inp['k_points']
    out['labels'] = list(inp['labels'])
    out['cell_A'] = [[round(x, GEOMETRY_HASH_DECIMALS) + 0.0 for x in v] for v in inp['cell_A']]
    return out


def settings_sha256(inp):
    return canonical_sha256(settings_block(inp))


def start_mode(inp):
    f = inp['fields']
    pot, wfc, rm = (f.get('electrons.startingpot'), f.get('electrons.startingwfc'), f.get('control.restart_mode'))
    if pot == 'file':
        return 'density-seeded'
    if pot in (None, 'atomic') and wfc in (None, 'atomic', 'atomic+random', 'random') and \
            rm in (None, 'from_scratch'):
        return 'fresh'
    return 'other'


# v9 (Codex v8 item 1): every relaxation segment is a FRESH start (register A35: 'the first SCF of the new segment (a
# fresh start) recomputes the carried geometry'; the D-24 relax.in files set neither restart_mode nor startingpot;
# A32 warm start is reserved, not registered). The effective values are resolved with the QE INPUT_PW defaults:
# restart_mode 'from_scratch', startingpot 'atomic' ('file' whenever restart_mode = 'restart'), startingwfc
# 'atomic+random'. Checked separately from the settings hash, which excludes these run-control keys on purpose.
QE_START_DEFAULTS = {'control.restart_mode': 'from_scratch', 'electrons.startingpot': 'atomic',
                     'electrons.startingwfc': 'atomic+random'}
FRESH_WFC = ('atomic', 'atomic+random', 'random')


def registered_start(inp):
    """(effective start settings with QE defaults resolved, fresh?)"""
    f = inp['fields']
    rm = str(f.get('control.restart_mode', QE_START_DEFAULTS['control.restart_mode'])).lower()
    pot = str(f.get('electrons.startingpot', 'file' if rm == 'restart' else QE_START_DEFAULTS['electrons.startingpot'])).lower()
    wfc = str(f.get('electrons.startingwfc', QE_START_DEFAULTS['electrons.startingwfc'])).lower()
    eff = {'control.restart_mode': rm, 'electrons.startingpot': 'file' if rm == 'restart' else pot,
           'electrons.startingwfc': wfc}
    fresh = rm == 'from_scratch' and eff['electrons.startingpot'] == 'atomic' and wfc in FRESH_WFC
    return eff, fresh


# v9 (Codex v8 item 4): the registered FINAL template per cell. A FINAL counts for a positive certificate only if its
# as-run settings block, with the width (system.degauss) removed, has the template key registered for its cell. The
# keys are frozen from the A26 / polished-FINAL templates at registration; NONE is registered in this draft, so no
# positive certificate that needs a FINAL can pass until they are (release gate).
REGISTERED_FINAL_TEMPLATES = {}


def final_template_key(block):
    return canonical_sha256({k: v for k, v in block.items() if k != 'system.degauss'})


# ---------------------------------------------------------------- QE text output, allowlist only
def read_qe_output(path, inp):
    """Allowlist reader (A39(a6)): only '!' energies, the first force block after each, total-force lines,
    convergence lines, BFGS lines, ATOMIC_POSITIONS rows and JOB DONE are kept. Every other line is dropped without
    interpretation. The kept stream is checked against DENY; a hit raises SightAbort and nothing is returned."""
    nat = inp['nat']
    kept = []
    pos_left = 0
    in_final = False
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\n')
            if pos_left > 0:
                m = RX_POS_ROW.match(line)
                if m:
                    kept.append(('pos_row', m.groups()))
                    pos_left -= 1
                    continue
                if line.strip():
                    pos_left = 0
            for tag, rx in (('energy', RX_ENERGY), ('forces_head', RX_FORCES_HEAD), ('force_row', RX_FORCE_ROW),
                            ('total_force', RX_TOTAL_FORCE), ('scf_ok', RX_SCF_OK), ('scf_fail', RX_SCF_FAIL),
                            ('bfgs_conv', RX_BFGS_CONV), ('bfgs_end', RX_BFGS_END), ('final_begin', RX_FINAL_BEGIN),
                            ('final_end', RX_FINAL_END), ('pos_head', RX_POS_HEAD), ('job_done', RX_JOB_DONE)):
                m = rx.match(line)
                if m:
                    if DENY.search(line):
                        raise SightAbort('deny pattern in an allowlisted line')
                    kept.append((tag, m.groups()))
                    if tag == 'pos_head':
                        pos_left = nat
                    break
    # structure the kept stream
    evals, cur_geom, pending = [], None, None
    out = {'evaluations': evals, 'bfgs_converged': False, 'final_positions': None, 'scf_ok': 0, 'scf_fail': 0,
           'job_done': False}
    pos_unit, pos_rows, collecting = None, [], False
    force_rows, in_forces = [], False

    types = inp['atom_types']

    def close_forces():
        """v4 (Codex 20:25Z item 1): a block counts only if atom indices are exactly 1..N, each once, and every
        printed type equals the input type of that atom (ATOMIC_SPECIES order). Anything else is a corrupt block."""
        nonlocal pending, force_rows, in_forces
        if pending is not None and in_forces and len(force_rows) == nat:
            idx = [int(r[0]) for r in force_rows]
            if sorted(idx) != list(range(1, nat + 1)):
                raise DeriveError('force_block_atom_indices_not_1_to_N_once')
            if any(int(r[1]) != types[int(r[0]) - 1] for r in force_rows):
                raise DeriveError('force_block_atom_type_differs_from_input')
            by = {int(r[0]): [ffloat(r[2]), ffloat(r[3]), ffloat(r[4])] for r in force_rows}
            pending['forces'] = [by[i] for i in range(1, nat + 1)]
            evals.append(pending)
        pending, force_rows, in_forces = None, [], False

    for tag, g in kept:
        if collecting and tag != 'pos_row':
            geom = (pos_unit, pos_rows)
            if in_final:
                out['final_positions'] = geom
            else:
                cur_geom = geom
            collecting, pos_rows = False, []
        if in_forces and tag != 'force_row':
            close_forces()
        if tag == 'energy':
            pending = {'F_Ry': ffloat(g[0]), 'geom': cur_geom, 'index': len(evals)}
        elif tag == 'forces_head':
            if pending is not None and 'forces' not in pending and not in_forces:
                in_forces, force_rows = True, []
        elif tag == 'force_row':
            if in_forces and len(force_rows) < nat:
                force_rows.append(g)
                if len(force_rows) == nat:
                    close_forces()
        elif tag == 'pos_head':
            pos_unit, pos_rows, collecting = (g[0] or 'alat').lower(), [], True
        elif tag == 'pos_row':
            if collecting:
                pos_rows.append(g)
        elif tag == 'final_begin':
            in_final = True
        elif tag == 'final_end':
            in_final = False
        elif tag == 'bfgs_conv':
            out['bfgs_converged'] = True
        elif tag == 'scf_ok':
            out['scf_ok'] += 1
        elif tag == 'scf_fail':
            out['scf_fail'] += 1
        elif tag == 'job_done':
            out['job_done'] = True
    if collecting:
        if in_final:
            out['final_positions'] = (pos_unit, pos_rows)
        else:
            cur_geom = (pos_unit, pos_rows)
    if in_forces:
        close_forces()
    # geometry hashes (the first SCF of a run is at the input geometry)
    in_hash = input_geometry_hash(inp)
    for e in evals:
        e['geometry_sha256'] = in_hash if e['geom'] is None else _rows_hash(e['geom'], inp)
        del e['geom']
    if out['final_positions'] is not None:
        out['final_geometry_sha256'] = _rows_hash(out['final_positions'], inp)
    else:
        out['final_geometry_sha256'] = None
    del out['final_positions']
    return out


def _rows_hash(geom, inp):
    unit, rows = geom
    if len(rows) != inp['nat']:
        raise DeriveError('positions_block_incomplete')
    labels = [r[0] for r in rows]
    if labels != inp['labels']:
        raise DeriveError('positions_label_order_changed')
    pos = to_cartesian([[ffloat(x) for x in r[1:4]] for r in rows], unit, inp['cell_A'], inp['alat_A'])
    return geometry_hash(inp['species'], pos, inp['cell_A'])


def max_force_component(forces):
    return max(abs(x) for row in forces for x in row)


def compare_evaluations(a, b):
    """(dF in Ry = b - a, max |dF| over all components in Ry/bohr, number of components)."""
    if len(a['forces']) != len(b['forces']):
        raise DeriveError('force_block_size_differs')
    d = max(abs(x - y) for ra, rb in zip(a['forces'], b['forces']) for x, y in zip(ra, rb))
    return b['F_Ry'] - a['F_Ry'], d, 3 * len(a['forces'])


# ---------------------------------------------------------------- HTCondor job logs (explicit time zones)
# v4 (Codex 20:25Z item 6): the real lxplus user-log event header is 'NNN (cluster.proc.sub) MM/DD HH:MM:SS text'
# (no year, no zone; e.g. '005 (12884016.000.000) 10/10 20:36:57 Job terminated.'). The year and the UTC offset are
# taken ONLY from a bound offset-evidence file captured on the submit host; the current clock is never read.
# ISO stamps ('YYYY-MM-DD HH:MM:SS' with 'Z' / '+HH:MM', or naive with the same evidence) are also accepted.
RX_EVENT_ISO = re.compile(r'^(\d{3}) \((\d+)\.(\d+)\.(\d+)\) (\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})(?:\.\d+)?'
                          r'(Z|[+-]\d{2}:?\d{2})?\s')
RX_EVENT_CONDOR = re.compile(r'^(\d{3}) \((\d+)\.(\d+)\.(\d+)\) (\d{2})/(\d{2}) (\d{2}:\d{2}:\d{2})\s')
RX_EVENT_HEAD = re.compile(r'^\d{3} \(\d+\.\d+\.\d+\) ')


class LocalTime:
    """Offset evidence (four lines, captured on the submit host):
         utc <YYYY-MM-DDTHH:MM:SSZ>        local <YYYY-MM-DDTHH:MM:SS+HHMM>   (the same instant)
         valid_from <UTC Z>                valid_to <UTC Z>                     (the interval in which the
                                                                                 offset holds, e.g. until the
                                                                                 end of daylight saving time)
       A naive stamp is converted with the offset and must fall inside the validity window. An MM/DD stamp takes
       the unique year that puts it inside the window (the window must be shorter than a year)."""

    def __init__(self, path):
        utc = loc = vf = vt = None
        with open(path, encoding='utf-8', errors='replace') as f:
            for line in f:
                p = line.split()
                if len(p) != 2:
                    continue
                if p[0] == 'utc':
                    utc = parse_utc(p[1])
                elif p[0] == 'valid_from':
                    vf = parse_utc(p[1])
                elif p[0] == 'valid_to':
                    vt = parse_utc(p[1])
                elif p[0] == 'local':
                    m = re.fullmatch(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})([+-])(\d{2}):?(\d{2})', p[1])
                    if m:
                        off = dt.timedelta(hours=int(m.group(3)), minutes=int(m.group(4)))
                        loc = (dt.datetime.strptime(m.group(1), '%Y-%m-%dT%H:%M:%S'),
                               off if m.group(2) == '+' else -off)
        if None in (utc, loc, vf, vt):
            raise DeriveError('offset_evidence_malformed')
        naive, off = loc
        if abs((naive - off).replace(tzinfo=dt.timezone.utc) - utc) > dt.timedelta(seconds=5):
            raise DeriveError('offset_evidence_inconsistent')
        if not (vf <= utc <= vt) or vt - vf >= dt.timedelta(days=360):
            raise DeriveError('offset_evidence_window_invalid')
        self.offset, self.valid_from, self.valid_to = off, vf, vt

    def to_utc(self, naive):
        t = (naive - self.offset).replace(tzinfo=dt.timezone.utc)
        if not (self.valid_from <= t <= self.valid_to):
            raise DeriveError('joblog_time_outside_offset_validity_window')
        return t

    def from_mmdd(self, month, day, hms):
        hits = []
        for y in sorted({self.valid_from.year, self.valid_to.year}):
            try:
                naive = dt.datetime.strptime(f'{y:04d}-{month:02d}-{day:02d} {hms}', '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
            t = (naive - self.offset).replace(tzinfo=dt.timezone.utc)
            if self.valid_from <= t <= self.valid_to:
                hits.append(t)
        if len(hits) != 1:
            raise DeriveError('joblog_mmdd_year_not_unique_in_offset_window')
        return hits[0]


def read_offset_evidence(path):
    return LocalTime(path)


def _event_time(line, tz):
    m = RX_EVENT_ISO.match(line)
    if m:
        t = dt.datetime.strptime(m.group(5) + ' ' + m.group(6), '%Y-%m-%d %H:%M:%S')
        z = m.group(7)
        if z == 'Z':
            return m.group(1), int(m.group(2)), t.replace(tzinfo=dt.timezone.utc)
        if z:
            zz = z.replace(':', '')
            off = dt.timedelta(hours=int(zz[1:3]), minutes=int(zz[3:5]))
            return m.group(1), int(m.group(2)), (t - (off if zz[0] == '+' else -off)).replace(tzinfo=dt.timezone.utc)
        if tz is None:
            raise DeriveError('joblog_naive_time_without_offset_evidence')
        return m.group(1), int(m.group(2)), tz.to_utc(t)
    m = RX_EVENT_CONDOR.match(line)
    if m:
        if tz is None:
            raise DeriveError('joblog_mmdd_time_without_offset_evidence')
        return m.group(1), int(m.group(2)), tz.from_mmdd(int(m.group(5)), int(m.group(6)), m.group(7))
    if RX_EVENT_HEAD.match(line):
        raise DeriveError('joblog_event_header_format_unknown')
    return None


def all_events(path, tz=None):
    """[(code, cluster, utc)] for every event header of the log, in file order; times must not decrease."""
    out, last = [], None
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            ev = _event_time(line, tz)
            if ev is None:
                continue
            if last is not None and ev[2] < last:
                raise DeriveError('joblog_event_times_decrease')
            last = ev[2]
            out.append(ev)
    return out


def job_events(path, cluster, tz=None):
    return [(c, t) for c, cl, t in all_events(path, tz) if cl == int(cluster)]


def submitted_clusters(path, tz=None):
    return sorted({cl for c, cl, t in all_events(path, tz) if c == '000'})


def terminated_utc(path, cluster, tz=None):
    ev = [t for c, t in job_events(path, cluster, tz) if c == '005']
    if not ev:
        raise DeriveError('joblog_no_termination_event')
    return max(ev)


RX_TERM_NORMAL = re.compile(r'^\s*\(1\) Normal termination \(return value (-?\d+)\)')
RX_TERM_SIGNAL = re.compile(r'^\s*\(0\) Abnormal termination \(signal (\d+)\)')


def disposition(path, cluster, tz=None):
    """v5 (Codex 20:44Z item 1): the terminal disposition of one cluster from its user log: 'normal_exit_<N>',
    'signal_<N>', 'aborted' (009), or None (no terminal event: still queued or running). Only HTCondor's own
    termination lines of the event body are read.
    v6: 'removed_while_held' for a 009 that follows a 012 (held) without a 013 (released). Only 'normal_exit_0' is a
    success; every other disposition is a non-success termination (f9_writers.derive_readout_manifest)."""
    out, pending, held = None, False, False
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            ev = _event_time(line, tz)
            if ev is not None:
                code, cl, t = ev
                pending = cl == int(cluster) and code == '005'
                if cl == int(cluster) and code in ('012', '013'):
                    held = code == '012'
                if cl == int(cluster) and code == '009':
                    out = 'removed_while_held' if held else 'aborted'
                continue
            if pending:
                m = RX_TERM_NORMAL.match(line)
                if m:
                    out, pending = f'normal_exit_{int(m.group(1))}', False
                    continue
                m = RX_TERM_SIGNAL.match(line)
                if m:
                    out, pending = f'signal_{int(m.group(1))}', False
    return out


def terminal_utc(path, cluster, tz=None):
    """v6: the time of the cluster's last terminal event (005 terminated or 009 aborted), or None."""
    ev = [t for c, t in job_events(path, cluster, tz) if c in ('005', '009')]
    return max(ev) if ev else None


# ---------------------------------------------------------------- v7: archive <-> job binding (Codex v6 review item 3)
# A returned archive is bound to its job by the archive-identity record (run, cluster, k) AND by evidence inside the
# archive: tar stores each member's source mtime (not the packing time), so a member written in-job carries a time
# inside that cluster's last execution (its last 001 'executing' event up to its terminal event, from the bound user
# log). An authentic archive of another job (e.g. completed on 18 Oct) cannot borrow a cluster that ended earlier.
ARCHIVE_CLOCK_TOLERANCE_S = 600   # ASSUMED infrastructure tolerance (worker vs submit-host clock); it never
                                  # shifts the cutoff or any registered date (Codex v7 ruling)


def job_window(path, cluster, tz=None):
    """(start, end) of the cluster's last execution: its last 001 before its terminal event (005/009)."""
    ev = job_events(path, cluster, tz)
    end = terminal_utc(path, cluster, tz)
    if end is None:
        raise DeriveError('joblog_no_termination_event')
    starts = [t for c, t in ev if c == '001' and t <= end]
    if not starts:
        raise DeriveError('joblog_no_execution_event')
    return max(starts), end


def check_members_in_window(archive_path, names, window, what):
    tol = dt.timedelta(seconds=ARCHIVE_CLOCK_TOLERANCE_S)
    for n in names:
        t = archive_member_mtime(archive_path, n)
        if t is None:
            raise DeriveError(f'{what}_member_missing')
        if t < window[0] - tol or t > window[1] + tol:
            raise DeriveError(f'{what}_archive_written_outside_the_jobs_execution')


# ---------------------------------------------------------------- v7: guard-only attempts and authorized resets
# relax_node.sh:19-34 stop_now: a guard / stop line ends the job before pw.x; its archive relax_s<k>_results.tar.gz
# holds relax_s<k>_driver.log starting '[<utc>] relax status: FAILED (stopped before pw.x on <host>); ...' (:22),
# relax.in unchanged and no relax.out. Such an attempt keeps its historical index k and is accounted separately.
SEGMENT_DRIVER_LOG = '{job}_driver.log'
RX_GUARD_STOP = re.compile(r'^\[[^\]]*\] relax status: FAILED \(stopped before pw\.x')
# d24_transition.sh:63-67, 82: the only scripted reset. A pre-D-24 segment k re-classified CONTINUE makes relax.in the
# lowest-energy validated geometry of segment k; runs/<name>/d24_transition.log gets
# '<utc> relax_s<k> old=... d24=... input=... action: relax.in = lowest-energy validated geometry (...)'.
RX_D24_RESET = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) relax_s(\d+) .*\baction: relax\.in = '
                          r'lowest-energy validated geometry\b')
# Pre-item-B segments: the as-run input is relax.in in the driver's EOS checkpoint, packed after pw.x and before the
# steps rewrite relax.in (lineage_relax.sh.D24:8-9); the checkpoint also holds the attempt's relax.out
# (README_D24_BD.txt:61-62); --to-eos copies it as relax_s<k>_ckpt_<cluster>.tar.gz (lineage_relax.sh.D24:161).
CHECKPOINT_NAMES = ('relax_s{k}_{cluster}.tar.gz', 'relax_s{k}_ckpt_{cluster}.tar.gz')


def d24_resets(path):
    """[(utc, k)] of the scripted D-24 transition resets in a d24_transition.log (only fixed tokens are read)."""
    out = []
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = RX_D24_RESET.match(line.strip())
            if m:
                out.append((parse_utc(m.group(1)), int(m.group(2))))
    return out


# ---------------------------------------------------------------- v6: artifact inventory of one C3 attempt
# Codex 2026-10-13 (blocking 1): a non-zero exit, a signal or a cancellation does not establish that no usable export
# exists. A D-24 FINAL-type job exports to its own per-cluster EOS directory $EXPORT_EOS/<name>/final_<ClusterId>/
# (steps_final.sh.D24:65 export_dest; :16); before pw.x it writes only exp/eos_probe_start.txt there (:110-115); every
# other file there comes from export_final (:202-273) or export_pull.sh.D24 (:53). The HTCondor output transfer
# (final_results.tar.gz, :5) never carries exp/. The inventory is the listing of that directory, captured off the job
# after its terminal event:
#     # iwo-f9-attempt-inventory/1
#     # run <name> cluster <N> captured_utc <YYYY-MM-DDTHH:MM:SSZ>
#     # location <path ending in /final_<N>> exists|absent
#     <basename> <bytes> <sha256>          one line per regular file (none when empty or absent)
#     # end files <count>
# Any file other than PRE_RUN_EXPORT_FILES means an export exists (it then needs its C3 report).
INVENTORY_SCHEMA = 'iwo-f9-attempt-inventory/1'
PRE_RUN_EXPORT_FILES = ('eos_probe_start.txt',)
RX_INV_RUN = re.compile(r'#\s*run\s+(\S+)\s+cluster\s+(\d+)\s+captured_utc\s+(\S+)\s*')
RX_INV_LOC = re.compile(r'#\s*location\s+(\S+)\s+(exists|absent)\s*')
RX_INV_END = re.compile(r'#\s*end\s+files\s+(\d+)\s*')
RX_INV_FILE = re.compile(r'([A-Za-z0-9][A-Za-z0-9._+-]*)\s+(\d+)\s+([0-9a-f]{64})\s*')


def read_attempt_inventory(path):
    """Strict parser: anything else, a repeated header, a line after the end line or a duplicate name is malformed;
    a missing end line or a count that differs from the listed files is an incomplete (truncated) listing."""
    with open(path, encoding='utf-8', errors='replace') as f:
        lines = [l.rstrip('\r\n') for l in f if l.strip()]
    if not lines or lines[0].strip() != '# ' + INVENTORY_SCHEMA:
        raise DeriveError('attempt_inventory_malformed')
    run = cluster = cap = loc = state = end = None
    files = []
    for line in lines[1:]:
        if end is not None:
            raise DeriveError('attempt_inventory_malformed')
        m = RX_INV_RUN.fullmatch(line)
        if m:
            if run is not None or parse_utc(m.group(3)) is None:
                raise DeriveError('attempt_inventory_malformed')
            run, cluster, cap = m.group(1), int(m.group(2)), parse_utc(m.group(3))
            continue
        m = RX_INV_LOC.fullmatch(line)
        if m:
            if loc is not None or run is None:
                raise DeriveError('attempt_inventory_malformed')
            loc, state = m.group(1), m.group(2)
            continue
        m = RX_INV_END.fullmatch(line)
        if m:
            end = int(m.group(1))
            continue
        m = RX_INV_FILE.fullmatch(line)
        if m and loc is not None:
            files.append((m.group(1), int(m.group(2)), m.group(3)))
            continue
        raise DeriveError('attempt_inventory_malformed')
    names = [n for n, _, _ in files]
    if run is None or loc is None or len(set(names)) != len(names) or (state == 'absent' and files):
        raise DeriveError('attempt_inventory_malformed')
    if end is None or end != len(files):
        raise DeriveError('attempt_inventory_incomplete')
    return {'run': run, 'cluster': cluster, 'captured_utc': cap, 'location': loc,
            'location_name': _basename(loc.rstrip('/')), 'state': state, 'files': files,
            'exported': [n for n in names if n not in PRE_RUN_EXPORT_FILES]}


# ---------------------------------------------------------------- v8: exact registered transitions (Codex v7 item 2)
# A settings change between consecutive pw.x segments is accepted only as one of these registered transitions, with
# the exact state after it, at its registered segment (attempt-1 numbering), once, on the registered route, and with
# its trigger. Sources (HYPOTHESIS_REGISTER.md): A35 diagnosis (s1 on aids from s0, s2 same settings) and A35 settings
# ('smearing = gaussian, degauss = 0.005 ... the only changed line'; aids, local-TF, conv_thr unchanged); A36 settings
# (s2: Gaussian 0.005 plus beta 0.1 / ndim 12 / maxstep 300; comp: the aids, MV 0.01 unchanged; conv_thr, local-TF
# unchanged) and the conditional rescue of aIWO_2p0_s1 (trigger: FAILED [scf] before 17 Oct 10:00 UTC; from that
# segment's relax_s<k>_bestvalid.in; installed per README section 3). mixing_mode, diagonalization, diago_full_acc and
# conv_thr are never permitted to change. A pure label split (A25/A30/A34: same element, UPF and mass per atom) is an
# explicit non-epoch transition.
GAUSS_STATE = {'system.smearing': 'gaussian', 'system.degauss': 0.005}
MV_STATE = {'system.smearing': 'mv', 'system.degauss': 0.01}
AIDS_STATE = {'electrons.mixing_beta': 0.1, 'electrons.mixing_ndim': 12, 'electrons.electron_maxstep': 300}
REGISTERED_TRANSITIONS = {
    # cell: [(k in attempt 1 or None = any k once, route, ref, may change, exact state after, trigger, rescue start)]
    'aIWO_0p8_s2': [(1, 'A35', 'A35-diagnosis-s1-aids', tuple(AIDS_STATE), {**MV_STATE, **AIDS_STATE}, None, False),
                    (3, 'A35', 'A35', tuple(GAUSS_STATE), {**GAUSS_STATE, **AIDS_STATE}, None, True)],
    'aIWO_2p0_s2': [(1, 'A36', 'A36', tuple(GAUSS_STATE) + tuple(AIDS_STATE), {**GAUSS_STATE, **AIDS_STATE}, None,
                     True)],
    'aIWO_2p0_comp_s1': [(1, 'A36', 'A36', tuple(AIDS_STATE), {**MV_STATE, **AIDS_STATE}, None, True)],
    'aIWO_2p0_s1': [(None, 'A36-conditional', 'A36-conditional', tuple(GAUSS_STATE) + tuple(AIDS_STATE),
                     {**GAUSS_STATE, **AIDS_STATE}, 'failed_scf_before_cutoff', True)],
}


def _same(a, b):
    if isinstance(b, float):
        return finite(a) and abs(float(a) - b) <= 1e-12
    return a == b


def registered_transition(cell, route, k, attempt, before, after, used):
    """(index, ref, trigger, rescue, changed keys) of the registered transition matching a settings change, or
    DeriveError. `before` / `after` are settings blocks; `used` holds the indices already used (each applies once)."""
    changed = sorted(x for x in set(before) | set(after) if before.get(x) != after.get(x))
    for i, (rk, rroute, ref, may, state, trig, rescue) in enumerate(REGISTERED_TRANSITIONS.get(cell, [])):
        if i in used or route != rroute or (rk is not None and (attempt != 1 or k != rk)):
            continue
        if any(c not in may for c in changed):
            raise DeriveError('epoch_start_changes_keys_outside_the_registered_transition')
        if any(not _same(after.get(x), v) for x, v in state.items()):
            raise DeriveError('epoch_start_state_differs_from_the_registered_state')
        return i, ref, trig, rescue, changed
    raise DeriveError('settings_change_without_authorized_epoch_start')


# v9 (Codex v8 ruling): relabeling only inside the registered A25/A30/A34 cell scope, with the A25 rule In -> In1/In2
# and O -> O1/O2 (W and H unchanged); A34 (i) (the MACE force-check SCFs) has no relaxation lineage.
LABEL_SPLIT_CELLS = ('aIO_2p0_s1',                                                                      # A25
                     'aIO_1p5_s1', 'aIO_2p0_s2', 'aIWO_1p5_s1', 'aIWO_2p0_comp_s1', 'aIWO_2p0_s1',
                     'aIWO_2p0_s1_bare', 'aIWO_2p0_s2',                                                 # A30
                     'aIWO_1p0_Al2O3_s2')                                                               # A34 (ii)
SPLIT_LABELS = {'In': ('In1', 'In2'), 'O': ('O1', 'O2')}
# v10 (Codex v9 ruling c): the resource (computation) routes that authorize a split, per cell. Kept separate from the
# lineage route (A35/A36 rescue-settings label): a segment declares its resource route with its unsplit input.
SPLIT_ROUTES = {'A25': ('aIO_2p0_s1',),
                'A30': ('aIO_1p5_s1', 'aIO_2p0_s2', 'aIWO_1p5_s1', 'aIWO_2p0_comp_s1', 'aIWO_2p0_s1', 'aIWO_2p0_s1_bare',
                        'aIWO_2p0_s2'),
                'A34': ('aIWO_1p0_Al2O3_s2',)}


# v11 (Codex v10 answer 3): the resource route is bound to the split segment's OWN cluster (condor_history -l): its
# request, Requirements and environment. Registered: A25 (1 x H100 NVL non-MIG; NV_ACC_MEM_MANAGE=0 NOT used), A30 and
# A34 (1 x H100 non-MIG; A29 NV_ACC_MEM_MANAGE=0 and QE_NK=1). The Requirements clause form is ASSUMED from the register
# ('PreVerRequirements regexp("H100") && !regexp("MIG")') until the first real ad is audited.
# v12: per route, required environment values and optional ones (A29 permits NV_ACC_MEM_MANAGE=0 for aIO_2p0_s1, the
# only A25 cell, superseding A25's exclusion; register A29). Any other value of these keys, or conflicting assignments, fail.
ROUTE_RESOURCES = {'A25': {'gpus': 1, 'env_required': {'QE_NK': '1'}, 'env_optional': {'NV_ACC_MEM_MANAGE': '0'}},
                   'A30': {'gpus': 1, 'env_required': {'QE_NK': '1', 'NV_ACC_MEM_MANAGE': '0'}, 'env_optional': {}},
                   'A34': {'gpus': 1, 'env_required': {'QE_NK': '1', 'NV_ACC_MEM_MANAGE': '0'}, 'env_optional': {}}}
# v13 (Codex v12 item 1): the audited GPU attribute (both predicates on it); other forms only after a real-ad audit
AUDITED_GPU_ATTR = 'TARGET.GPUs_DeviceName'
RX_H100 = re.compile(r'^regexp\(\s*"H100"\s*,\s*([A-Za-z_][A-Za-z0-9_.]*)\s*\)$')
RX_NOT_MIG = re.compile(r'^!\s*regexp\(\s*"MIG"\s*,\s*([A-Za-z_][A-Za-z0-9_.]*)\s*\)$')


def _classad_scan(e):
    """Escape-aware scan of a ClassAd expression: yields (index, char, depth, in_string). A string literal runs to the next
    unescaped double quote (backslash escapes the next character). Raises ValueError on an unterminated string or
    unbalanced parentheses."""
    out, depth, q, i = [], 0, False, 0
    while i < len(e):
        ch = e[i]
        if q:
            out.append((i, ch, depth, True))
            if ch == '\\' and i + 1 < len(e):
                out.append((i + 1, e[i + 1], depth, True))
                i += 2
                continue
            if ch == '"':
                q = False
            i += 1
            continue
        if ch == '"':
            q = True
            out.append((i, ch, depth, True))
            i += 1
            continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth < 0:
                raise ValueError('unbalanced')
        out.append((i, ch, depth, False))
        i += 1
    if q or depth != 0:
        raise ValueError('unterminated')
    return out


def _strip_parens(e):
    e = e.strip()
    while e.startswith('(') and e.endswith(')'):
        scan = _classad_scan(e)
        closes = [i for i, ch, d, q in scan if not q and ch == ')' and d == 0]
        if closes != [len(e) - 1]:
            break
        e = e[1:-1].strip()
    return e


def _top_split(expr):
    """(conjuncts, widening) of a ClassAd expression: split on && at depth 0 outside string literals (escape-aware);
    widening is True if a lower-precedence operator appears at depth 0 (||, or the ?: conditional, whose condition would
    then be the whole conjunction)."""
    e = _strip_parens(expr)
    scan = _classad_scan(e)
    parts, cur, widening, k = [], [], False, 0
    while k < len(scan):
        i, ch, d, q = scan[k]
        if not q and d == 0 and ch in '|&' and k + 1 < len(scan) and scan[k + 1][1] == ch and not scan[k + 1][3]:
            if ch == '|':
                widening = True
            parts.append(''.join(c for _, c, _, _ in cur))
            cur, k = [], k + 2
            continue
        if not q and d == 0 and ch in '?:':
            meta = ch == '?' and 0 < k < len(scan) - 1 and scan[k - 1][1] == '=' and scan[k + 1][1] == '='   # =?= operator
            widening = widening or not meta
        cur.append(scan[k])
        k += 1
    parts.append(''.join(c for _, c, _, _ in cur))
    return [_strip_parens(x) for x in parts], widening


def requirements_problem(req):
    try:
        parts, widening = _top_split(req or '')
    except ValueError:
        return 'resource_route_not_the_registered_execution'
    h = [m.group(1) for m in (RX_H100.match(p) for p in parts) if m]
    g = [m.group(1) for m in (RX_NOT_MIG.match(p) for p in parts) if m]
    if widening or AUDITED_GPU_ATTR not in h or AUDITED_GPU_ATTR not in g:
        return 'resource_route_not_the_registered_execution'
    return None


def environment_problem(route, env):
    reg = ROUTE_RESOURCES.get(route) or {}
    vals = {}
    for tok in env.split():
        if '=' not in tok:
            return 'resource_route_not_the_registered_execution'
        k, v = tok.split('=', 1)
        if k in vals and vals[k] != v:
            return 'resource_route_not_the_registered_execution'          # conflicting assignments
        vals[k] = v
    for k, v in (reg.get('env_required') or {}).items():
        if vals.get(k) != v:
            return 'resource_route_not_the_registered_execution'
    for k, v in (reg.get('env_optional') or {}).items():
        if k in vals and vals[k] != v:
            return 'resource_route_not_the_registered_execution'
    return None
RX_AD = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$')


def read_job_ad(path):
    vals = {}
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = RX_AD.match(line)
            if m:
                if m.group(1) in vals:
                    raise DeriveError('job_ad_malformed')
                vals[m.group(1)] = m.group(2)
    return vals


def resource_route_problem(route, cluster, path):
    ad = read_job_ad(path)
    try:
        cl, gpus = int(ad['ClusterId']), int(ad['RequestGpus'])
    except (KeyError, ValueError):
        return 'resource_evidence_malformed'
    if cl != int(cluster):
        return 'resource_evidence_for_another_cluster'
    reg, req, env = ROUTE_RESOURCES.get(route), ad.get('Requirements', ''), ad.get('Environment', '').strip('"')
    if reg is None or gpus != reg['gpus']:
        return 'resource_route_not_the_registered_execution'
    return requirements_problem(req) or environment_problem(route, env)


# v12 (Codex v11 case 3): the [infra] bestvalid exception (A34(ii) and the D-37 guard-ordering fix: a fatal GPU/CUDA error
# after a new validated geometry gives FAILED [infra] with relax_s<k>_bestvalid.in archived) holds only for the chains where
# that fix is installed, and only with a restoration record: the rollback (ROLLBACK.txt / A30 return to the original route)
# applied before the reset is logged.
INFRA_BESTVALID_CELLS = ('aIO_2p0_s1', 'aIO_2p0_s2', 'aIWO_2p0_s1', 'aIWO_2p0_s2', 'aIWO_2p0_comp_s1', 'aIWO_0p7_s1',
                         'aIWO_0p7_s1_bare',                      # D-37 install 2026-10-12T07:16:41Z
                         'aIWO_1p0_Al2O3_s2')                     # A34(ii)
INFRA_BESTVALID_ENABLED = False          # v13 (Codex v12 item 2): disabled until its restoration evidence is supported
ROLLBACK_SCHEMA = 'iwo-f9-rollback/1'
RX_RB_HEAD = re.compile(r'#\s*run\s+(\S+)\s+after\s+(relax_s\d+)\s+restored\s+(\S+)\s+logged_utc\s+(\S+)\s*')


def read_rollback_record(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        lines = [l.rstrip('\r\n') for l in f if l.strip()]
    h = RX_RB_HEAD.fullmatch(lines[1]) if len(lines) == 2 and lines[0].strip() == '# ' + ROLLBACK_SCHEMA else None
    if not h or parse_utc(h.group(4)) is None:
        raise DeriveError('rollback_record_malformed')
    return {'run': h.group(1), 'after': h.group(2), 'restored': h.group(3), 'logged_utc': parse_utc(h.group(4))}


# v11 (Codex v10 answer 1): DAGMAN_RESET_RETRIES_UPON_RESCUE = False writes the remaining retries into a NEW rescue file
# but cannot repair a file already written with reset counts, so every rescue binds its rescue file and its RELAX node's
# remaining RETRY must fit the preserved budget (RETRY + 1 executions <= remaining_after). Format ASSUMED
# ('RETRY RELAX <n>', exactly once) until the first real rescue file is audited.
RX_RESCUE_RETRY = re.compile(r'^\s*RETRY\s+RELAX\s+(\d+)\b')


# v13 (A43 count-enforcement draft, section 5): the A43 continuation DAG and its evidence
A43_CONFIG_LINE = 'DAGMAN_RESET_RETRIES_UPON_RESCUE = False'


def _dag_lines(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return [' '.join(l.split()) for l in f if l.strip() and not l.lstrip().startswith('#')]


# v14: audited submission facts (ASSUMED until the first real .condor.sub and DAGMan ad are audited)
A43_RUN_ROOT = '/afs/cern.ch/user/m/melrashe/iwo_amorph/runs'            # ~/iwo_amorph/runs (README_D24_BD; register A34)
AUDITED_DAGMAN_EXECUTABLES = ('/usr/bin/condor_dagman',)
RX_SUBMIT_ONE = re.compile(r'^\s*(\d+) job\(s\) submitted to cluster (\d+)\.\s*$', re.M)
RX_SUB_KV = re.compile(r'^([A-Za-z_+][A-Za-z0-9_.+]*)\s*=\s*(.*)$')


def parse_condor_args(s):
    """HTCondor new-syntax arguments (the text inside the outer double quotes; htcondor-jdl 'arguments'): whitespace
    separates arguments; a single-quoted section groups text including whitespace, '' inside it is a literal single quote;
    "" is a literal double quote; adjacent quoted and unquoted text form one argument. Raises ValueError on an unterminated
    single quote or a lone double quote."""
    out, cur, started, insq, i = [], [], False, False, 0
    while i < len(s):
        ch = s[i]
        if insq:
            if ch == "'":
                if i + 1 < len(s) and s[i + 1] == "'":
                    cur.append("'")
                    i += 2
                    continue
                insq = False
            else:
                cur.append(ch)
            i += 1
            continue
        if ch.isspace():
            if started:
                out.append(''.join(cur))
                cur, started = [], False
        elif ch == "'":
            insq, started = True, True
        elif ch == '"':
            if i + 1 < len(s) and s[i + 1] == '"':
                cur.append('"')
                started = True
                i += 2
                continue
            raise ValueError('lone double quote')
        else:
            cur.append(ch)
            started = True
        i += 1
    if insq:
        raise ValueError('unterminated single quote')
    if started:
        out.append(''.join(cur))
    return out


RX_CSD_VERSION = re.compile(r'^\$CondorVersion: [^$]*\$$')


def _dagman_args_problem(args, dag):
    """v15: every argument of the parsed list is a permitted condor_dagman option (each once) with its fixed value; the
    -CsdVersion value is one argument of the form '$CondorVersion: ... $'."""
    try:
        argv = parse_condor_args(args)
    except ValueError:
        return 'a43_dry_run_not_bound'
    fixed = {'-p': '0', '-l': '.', '-Lockfile': dag + '.lock', '-AutoRescue': '1', '-DoRescueFrom': '0', '-Dag': dag}
    k, seen = 0, set()
    while k < len(argv):
        t = argv[k]
        if t in seen:
            return 'a43_dry_run_not_bound'
        seen.add(t)
        if t in ('-f', '-Suppress_notification'):
            k += 1
            continue
        if k + 1 >= len(argv):
            return 'a43_dry_run_not_bound'
        v = argv[k + 1]
        if (t in fixed and v == fixed[t]) or (t == '-Dagman' and v in AUDITED_DAGMAN_EXECUTABLES) or \
                (t == '-CsdVersion' and RX_CSD_VERSION.match(v)):
            k += 2
            continue
        return 'a43_dry_run_not_bound'                        # any other option, value or recovery / force setting
    return None if {'-Dag', '-DoRescueFrom'} <= seen else 'a43_dry_run_not_bound'


def a43_submission_problem(dry_run, a43, run, submit_record, dagman_ad, dagman_out, node_cluster, retry):
    """v14 (Codex v13 item 1): the reviewed .condor.sub is one scheduler-universe DAGMan (one queue statement), the audited
    executable, no initialdir other than the chain's run directory, permitted arguments only; the submit record names one
    cluster; the submitted DAGMan ad equals the reviewed file (JobUniverse 7, Cmd, Iwd, Arguments); the A43 dagman.out is
    that DAGMan's (condor_scheduniv_exec.<cluster>), reports the False setting, submitted the first resumed RELAX node and
    retries with n = RETRY."""
    dag, rundir = os.path.basename(a43), f'{A43_RUN_ROOT}/{run}'
    kv, queues = {}, []
    for l in _dag_lines(dry_run):
        if l.endswith('\\'):                                    # v15: no line continuation
            return 'a43_dry_run_not_bound'
        if re.match(r'(?i)^queue\b', l):
            queues.append(l)
            continue
        m = RX_SUB_KV.match(l)
        if not m:                                              # v15: include, if/elif/else/endif, error/warning, ... refused
            return 'a43_dry_run_not_bound'
        key = m.group(1).lower()
        if key in kv or key in ('include', 'if', 'elif', 'else', 'endif'):   # 'error = file' is a normal command
            return 'a43_dry_run_not_bound'
        kv[key] = m.group(2).strip()
    exe, args = kv.get('executable'), kv.get('arguments', '')
    if [q.lower() for q in queues] not in (['queue'], ['queue 1']) or kv.get('universe', '').lower() != 'scheduler' or \
            exe not in AUDITED_DAGMAN_EXECUTABLES or kv.get('initialdir', rundir) != rundir or \
            not (args.startswith('"') and args.endswith('"')) or _dagman_args_problem(args[1:-1], dag):
        return 'a43_dry_run_not_bound'
    with open(submit_record, encoding='utf-8', errors='replace') as f:
        sub = RX_SUBMIT_ONE.findall(f.read())
    ad = read_job_ad(dagman_ad)
    unq = lambda v: ' '.join(str(v or '').strip().strip('"').split())
    if len(sub) != 1 or sub[0][0] != '1' or ad.get('ClusterId') != sub[0][1] or ad.get('JobUniverse') != '7' or \
            unq(ad.get('Cmd')) != exe or unq(ad.get('Iwd')) != rundir or unq(ad.get('Arguments')) != unq(args):
        return 'a43_submission_not_linked'
    with open(dagman_out, encoding='utf-8', errors='replace') as f:
        txt = f.read()
    tries = [int(x) for x in re.findall(r'Retrying node RELAX \(retry #\d+ of (\d+)\)', txt)]
    execs = set(re.findall(r'condor_scheduniv_exec\.(\d+)\.0', txt))
    if execs != {sub[0][1]} or 'DAGMAN_RESET_RETRIES_UPON_RESCUE setting: False' not in txt or \
            'DAGMAN_RESET_RETRIES_UPON_RESCUE setting: True' in txt or any(t != retry for t in tries) or \
            f'ULOG_SUBMIT for HTCondor Node RELAX ({int(node_cluster)}.0.0)' not in txt:
        return 'a43_dagman_header_not_bound'
    return None


def a43_dag_problem(original, a43, config, dry_run, dagman_out, remaining_after):
    """None if <name>.a43.dag equals the original DAG except 'RETRY RELAX <remaining_after - 1>' and one CONFIG line naming
    the bound config (exactly DAGMAN_RESET_RETRIES_UPON_RESCUE = False), the -no_submit dry-run .condor.sub names the A43
    DAG with -DoRescueFrom 0 (format ASSUMED until a real file is audited), and a bound dagman.out (optional, post-run)
    reports the False setting and 'retry #k of <n>' with n = the A43 RETRY."""
    o, n = _dag_lines(original), _dag_lines(a43)
    cfg = [l for l in n if l.split()[0].upper() == 'CONFIG']
    ret = [l for l in n if re.fullmatch(r'RETRY RELAX \d+', l)]
    rest_n = [l for l in n if l not in cfg and l not in ret]
    rest_o = [l for l in o if not re.fullmatch(r'RETRY RELAX \d+', l)]
    if len(cfg) != 1 or len(ret) != 1 or rest_n != rest_o or len([l for l in o if re.fullmatch(r'RETRY RELAX \d+', l)]) != 1 or \
            cfg[0].split()[1:] != [os.path.basename(config)]:
        return 'a43_dag_differs_from_the_original'
    if [' '.join(l.replace('=', ' = ').split()) for l in _dag_lines(config)] != [A43_CONFIG_LINE]:
        return 'a43_dag_config_not_the_registered_setting'
    r = int(ret[0].split()[2])
    if r + 1 != remaining_after:
        return 'a43_dag_retry_not_exactly_the_remaining_count'
    args = None
    for l in _dag_lines(dry_run):
        m = re.fullmatch(r'arguments = "(.*)"', l)
        if m:
            args = m.group(1).split() if args is None else None
    if not args:
        return 'a43_dry_run_not_bound'
    def opt(k):
        return [args[i + 1] for i, x in enumerate(args[:-1]) if x == k]
    if opt('-Dag') != [os.path.basename(a43)] or opt('-DoRescueFrom') != ['0']:
        return 'a43_dry_run_not_bound'
    if dagman_out:
        with open(dagman_out, encoding='utf-8', errors='replace') as f:
            txt = f.read()
        tries = [int(x) for x in re.findall(r'Retrying node RELAX \(retry #\d+ of (\d+)\)', txt)]
        if 'DAGMAN_RESET_RETRIES_UPON_RESCUE setting: False' not in txt or 'DAGMAN_RESET_RETRIES_UPON_RESCUE setting: True' in txt \
                or any(t != r for t in tries):
            return 'a43_dagman_header_not_bound'
    return None


def rescue_file_retry(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        hits = [int(m.group(1)) for m in (RX_RESCUE_RETRY.match(l) for l in f) if m]
    if len(hits) != 1:
        raise DeriveError('rescue_file_malformed')
    return hits[0]


def is_split(inp):
    return any(l != element_of(l) for l in inp['labels'])


def label_split_problem(cell, inp):
    """None if every label is its element name, or the registered split inside the registered cell scope: In -> In1/In2
    and O -> O1/O2 only, every atom of a split element relabelled, alternating X1, X2, X1 ... in atom order (a25_labels.py
    alternating rule), hence balanced counts (|n1 - n2| <= 1)."""
    if not is_split(inp):
        return None
    labs = inp['labels']
    if cell not in LABEL_SPLIT_CELLS or any(l != element_of(l) and l not in SPLIT_LABELS.get(element_of(l), ())
                                            for l in labs):
        return 'label_split_outside_the_registered_scope'
    for el, (a, b) in SPLIT_LABELS.items():         # v11 (Codex v10 case 2): BOTH registered splits, never one alone
        seq = [l for l in labs if element_of(l) == el]
        if not seq:
            continue
        if seq != [(a, b)[i % 2] for i in range(len(seq))] or abs(seq.count(a) - seq.count(b)) > 1:
            return 'label_split_not_the_registered_construction'
    return None


def split_construction_problem(cell, route, split_inp, unsplit_inp):
    """v10 (Codex v9 ruling c): the split input is the registered construction of its unsplit input: authorized cell AND
    resource route; the unsplit input has element labels only; restoring the split labels gives them; geometry, cell,
    k-points, every namelist field apart from ntyp, and the label-resolved settings (epoch key) are identical."""
    if route not in SPLIT_ROUTES or cell not in SPLIT_ROUTES[route]:
        return 'label_split_outside_the_registered_scope'
    p = label_split_problem(cell, split_inp) or (None if is_split(split_inp) else 'label_split_not_the_registered_construction')
    if p:
        return p
    if is_split(unsplit_inp) or [element_of(l) for l in split_inp['labels']] != list(unsplit_inp['labels']):
        return 'split_construction_not_equivalent'
    fa = {k: v for k, v in split_inp['fields'].items() if k != 'system.ntyp'}
    fb = {k: v for k, v in unsplit_inp['fields'].items() if k != 'system.ntyp'}
    if fa != fb or input_geometry_hash(split_inp) != input_geometry_hash(unsplit_inp) or \
            split_inp['k_points'] != unsplit_inp['k_points'] or epoch_key(split_inp) != epoch_key(unsplit_inp):
        return 'split_construction_not_equivalent'
    return None


def epoch_key(inp):
    """The settings hash with labels resolved to (element, UPF, mass) per atom: a pure label split keeps it."""
    b = settings_block(inp)
    b.pop('system.ntyp', None)                         # v10: a split changes ntyp (4 -> 6), not the physics
    spec = {l: (element_of(l), round(m, 6), p) for l, m, p in inp['atomic_species']}
    b['labels'] = [list(spec[l]) for l in inp['labels']]
    b['atomic_species'] = sorted({tuple(v) for v in spec.values()})
    return canonical_sha256(b)


# ---------------------------------------------------------------- v8: job history and transition records
# Codex v7 item 1: a C3 attempt's actual run comes from the scheduler's own record of that cluster (condor_history -l
# <cluster>: 'ClusterId = N', 'IWOJob = "<name>_final"', 'QDate = <unix>'), checked against the slot user log; every
# inventory or export of the attempt must name that run (steps_final.sh.D24:58-62 iwo_name).
RX_HIST = re.compile(r'^\s*(ClusterId|IWOJob|QDate)\s*=\s*(.+?)\s*$')


def read_job_history(path):
    vals = {}
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = RX_HIST.match(line)
            if m:
                if m.group(1) in vals:
                    raise DeriveError('attempt_job_history_malformed')
                vals[m.group(1)] = m.group(2)
    try:
        cl, qd, job = int(vals['ClusterId']), int(vals['QDate']), vals['IWOJob']
    except (KeyError, ValueError):
        raise DeriveError('attempt_job_history_malformed')
    m = re.fullmatch(r'"([A-Za-z0-9][A-Za-z0-9_.+-]*)_final"', job)
    if not m:
        raise DeriveError('attempt_job_is_not_a_final_job')
    return {'cluster': cl, 'run': m.group(1), 'qdate': dt.datetime.fromtimestamp(qd, dt.timezone.utc)}


# README_D24_BD.txt section 3 (lines 70-87): a reset replaces runs/<name>/relax.in (e.g. by relax_s<k>_bestvalid.in,
# backup relax.in.pre_reset_<utc>) and is logged in the work chat; when the DAG has finished, the old tarballs are moved
# ('mkdir attempt<N> && mv relax_s*_results.tar.gz attempt<N>/') and the rescue DAG restarts $(RETRY) at 0. The F9
# transition record states it (written from the work-chat log line and the attempt<N>/ listing):
#     # iwo-f9-transition/1
#     # run <name> kind section3_reset|section3_rescue after relax_s<k> attempt <N> logged_utc <t>
#     # authorization <ref> remaining_before <n> remaining_after <n> prior_rescues <m> terminal_failure no|yes
#                                                (v9: section3_rescue only; Codex v8 item 3)
#     moved <basename> <bytes> <sha256>          (section3_rescue: every archive moved into attempt<N>/)
#     # end moved <count>
# v9: a rescue (rescue DAG, attempt<N+1>) needs a REGISTERED authorization (REGISTERED_RESCUE_AUTHORIZATIONS, frozen;
# empty in this draft): its run, the attempt it follows, the registered node-execution budget of the lineage and its
# basis - 'exhausted' (the previous attempt used all DAG_NODE_EXECUTIONS) or 'suspension' (a prospective suspension
# rule logged no later than the previous attempt's last terminal event, e.g. the ~15 Oct GPU pause). Each authorization
# is used once; the remaining executions carry over (HTCondor resets $(RETRY) on a rescue by default,
# DAGMAN_RESET_RETRIES_UPON_RESCUE; the registered budget never resets); prior rescue use and terminal-failure status
# are restated and must equal the derived values.
TRANSITION_SCHEMA = 'iwo-f9-transition/2'
RX_TR_HEAD = re.compile(r'#\s*run\s+(\S+)\s+kind\s+(section3_reset|section3_rescue)\s+after\s+(relax_s\d+)\s+attempt\s+'
                        r'(\d+)\s+logged_utc\s+(\S+)\s*')
RX_TR_AUTH = re.compile(r'#\s*authorization\s+(\S+)\s+remaining_before\s+(\d+)\s+remaining_after\s+(\d+)\s+'
                        r'prior_rescues\s+(\d+)\s+terminal_failure\s+(no|yes)\s*')
RX_TR_MOVED = re.compile(r'moved\s+(\S+)\s+(\d+)\s+([0-9a-f]{64})\s*')
REGISTERED_RESCUE_AUTHORIZATIONS = {}   # v10: ref -> {run, after_attempt, basis, additional_executions, pause_started_utc,
#                                         rule_logged_utc, result_informed, preserved}; empty in this draft
DAG_NODE_EXECUTIONS = 9                 # Codex v9 ruling (a): the maximum of a fresh RELAX node with RETRY 8, bound from attempt 1;
#                                         one execution = one cluster (an eviction / re-execution inside it is not a DAG retry)
# A39 (logged; register 'Administrative rescue DAG'): after RETRY RELAX 8 is exhausted with the last segment CONTINUE or a
# resumed non-[scf] D-24 category, ONE rescue DAG per chain with at most 9 additional RELAX node executions; never after a
# terminal failure. Encoded as a built-in authorization 'A39' (any run; once per chain).
BUILTIN_RESCUE_AUTHORIZATIONS = {'A39': {'run': None, 'after_attempt': None, 'basis': 'exhausted',
                                         'additional_executions': 9, 'trigger': 'a39'}}
RX_TR_END = re.compile(r'#\s*end\s+moved\s+(\d+)\s*')


def read_transition_record(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        lines = [l.rstrip('\r\n') for l in f if l.strip()]
    if len(lines) < 3 or lines[0].strip() != '# ' + TRANSITION_SCHEMA:
        raise DeriveError('transition_record_malformed')
    h, e = RX_TR_HEAD.fullmatch(lines[1]), RX_TR_END.fullmatch(lines[-1])
    a = RX_TR_AUTH.fullmatch(lines[2]) if len(lines) > 3 else None
    moved = [RX_TR_MOVED.fullmatch(l) for l in lines[(3 if a else 2):-1]]
    if not h or not e or None in moved or int(e.group(1)) != len(moved) or parse_utc(h.group(5)) is None:
        raise DeriveError('transition_record_malformed')
    auth = None if a is None else {'ref': a.group(1), 'remaining_before': int(a.group(2)),
                                   'remaining_after': int(a.group(3)), 'prior_rescues': int(a.group(4)),
                                   'terminal_failure': a.group(5) == 'yes'}
    return {'run': h.group(1), 'kind': h.group(2), 'after': h.group(3), 'attempt': int(h.group(4)),
            'logged_utc': parse_utc(h.group(5)), 'moved': {(m.group(1), m.group(3)) for m in moved}, 'auth': auth}


def first_execution_utc(path, cluster, tz=None):
    """v8 (Codex v7 item 3): the cluster's first 001 'executing' event, when HTCondor transferred its input."""
    ev = [t for c, t in job_events(path, cluster, tz) if c == '001']
    return min(ev) if ev else None


# ---------------------------------------------------------------- restart-gate inventory
def epochs(segments):
    """Maximal runs of consecutive segments with identical settings (v8: label-resolved 'epoch_key' when recorded)."""
    out = []
    key = lambda s: s.get('epoch_key') or s['settings_sha256']
    for s in segments:
        if out and key(out[-1][-1]) == key(s):
            out[-1].append(s)
        else:
            out.append([s])
    return out


def required_gate_boundaries(cell, route, segments):
    """v8 (Codex v7 rulings): the MANDATORY restart gates. For a registered rescue (A35 s3, A36 s1, the conditional
    A36 rescue) they are the boundaries after the rescue start (A35 from s4, A36 from s2), across later explicit
    transitions (label splits, section-3 resets and rescues); for the C4-polish route (D-42 F5) every boundary. Earlier
    boundaries are diagnostics only (diagnostic_boundaries) and never become gates retroactively."""
    if not segments:
        return []
    if route == 'C4-polish':
        rest = segments
    else:
        starts = [i for i, s in enumerate(segments) if s.get('rescue_start')]
        if not starts:
            return []
        rest = segments[starts[0]:]
    return [f'{a["segment"]}->{b["segment"]}' for a, b in zip(rest, rest[1:])]


def diagnostic_boundaries(cell, route, segments):
    """v8: the other boundaries of a lineage with registered transitions or a gated route (e.g. pre-rescue MV
    comparisons): computed and disclosed, never a veto."""
    if not segments or (cell not in REGISTERED_TRANSITIONS and route not in GATED_ROUTES):
        return []
    req = set(required_gate_boundaries(cell, route, segments))
    allb = [f'{a["segment"]}->{b["segment"]}' for a, b in zip(segments, segments[1:])]
    return [b for b in allb if b not in req]


def gate_failed(g):
    """A numerically evaluated gate outside the registered tolerances (inclusive limits)."""
    dF, dm = g.get('delta_F_Ry'), g.get('max_abs_dF_Ry_bohr')
    return finite(dF) and finite(dm) and (abs(dF) > GATE_DF_RY or dm > GATE_DFORCE_RY_BOHR)


def segment_index(name):
    m = re.fullmatch(r'([a-z])(\d+)', name or '')
    return (m.group(1), int(m.group(2))) if m else (None, None)


def converged_at_cutoff(d, cutoff):
    """Relaxation status at the cutoff from a relaxation_lineage derived block (A31(f) role selection; the F9
    'converged' assertions without the later qualification). Returns (bool, [reason codes])."""
    r = []
    conv = d.get('bfgs_converged') is True
    if not conv:
        r.append('bfgs_not_converged')
    else:
        t = parse_utc(d.get('bfgs_converged_utc'))
        if d.get('timing_source') not in ('htcondor_job_log', 'snapshot_completed_utc') or t is None:
            r.append('a19_timing_unverifiable')
        elif t > cutoff:
            r.append('converged_after_cutoff')
        res = d.get('final_residual') or {}
        mf, de = res.get('max_force_component_Ry_bohr'), res.get('energy_change_Ry')
        if not finite(mf) or mf > REGISTERED_FORC_CONV_THR:
            r.append('final_residual_force_above_registered_threshold')
        if de is not None and (not finite(de) or abs(de) > REGISTERED_ETOT_CONV_THR):
            r.append('final_energy_change_above_registered_threshold')
    if d.get('registered_ionic_thresholds') is not True:
        r.append('ionic_thresholds_not_registered')
    if d.get('terminal_scf_failures'):
        r.append('terminal_scf_failure_in_active_epoch')
    req = required_gate_boundaries(d.get('cell'), d.get('route'), d.get('segments') or [])
    gates = {g.get('boundary'): g for g in d.get('gates') or [] if isinstance(g, dict)}
    if req != d.get('required_gates') or set(req) != set(gates):
        r.append('restart_gate_inventory_inconsistent')
    for b in req:          # a missing or unevaluable mandatory gate counts as failed (Codex v7 ruling)
        g = gates.get(b) or {}
        dF, dm = g.get('delta_F_Ry'), g.get('max_abs_dF_Ry_bohr')
        if g.get('error') or not finite(dF) or not finite(dm) or abs(dF) > GATE_DF_RY or dm > GATE_DFORCE_RY_BOHR:
            r.append('restart_gate_failed')
            break
    return not r, r
