"""Run certificates, the automated validation gate, and provenance hashes.

Workflow (rc2/rc3, Codex reviews):
  1. The DFT agent COMPILES a certificate for each FINAL with  python -m analysis certify ...  : the sha256 of every run
     file the read-out consumes (projections, planar-average inputs), the geometry hash, the pseudopotential sha256
     (from lineage_final.dat or --pseudo-dir), a composition manifest (from the make_specs.py spec or a construction
     manifest such as a C1 paired cell), and one block per qualification (relaxation, smearing, geometry polish), each a
     status plus evidence files (sha256-bound, paths relative to the certificate). Only positive claims need evidence;
     anything unproven stays at its default (relaxation UNKNOWN, smearing pending, geometry unknown).
  2. The GATE (validate(), run by every 'cell' read-out and by  python -m analysis validate-cert) recomputes every hash.
     Any malformed field, unknown status, unbound consumed file, missing pseudopotential provenance, or a smearing
     qualification without a numeric width equal to the width actually used (Gaussian family) is a problem: the gate is
     NOT VALID. A failed binding (cell name, run files, geometry) invalidates the whole certificate.
  3. Codex AUDITS the certificate, its evidence and the hashes recorded in every output (code, register, inputs,
     certificate).
Missing or failed qualification is listed in run_qualification['reasons'] and makes every primary score UNRESOLVED.
Every result carries a self-hash over its content without the non-deterministic 'meta' block (time stamps, paths).
"""
import glob
import hashlib
import json
import math
import os
import re

from . import __version__
from . import qeio
from .register import FORMAL_CHARGE, GAUSSIAN, GEOMETRY_HASH_DECIMALS, RY_EV, WIDTH_TOL_RY

CERT_SCHEMA = 'iwo-amorph-analysis/certificate/2'
KINDS = ('W-doped', 'compensated', 'undoped', 'reference')
RELAX = ('converged', 'exploratory', 'unknown')
SMEAR = ('qualified', 'pending')
GEOM = ('polished', 'mv', 'unknown')
PROJ_SOURCE_KEYS = ('data-file-schema', 'atomic_proj', 'occ_kw_', 'proj_atoms_', 'projwfc_map', 'projwfc_')
NON_BOUND_KEYS = ('_',)                                  # internal entries of data.sources (not files)

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTER_PATH = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'codex', 'work_chat', 'HYPOTHESIS_REGISTER.md'))


# ---------------------------------------------------------------- hashes
def _strip(obj):
    if isinstance(obj, dict):
        return {k: _strip(v) for k, v in obj.items() if k not in ('meta', 'self_sha256')}
    if isinstance(obj, list):
        return [_strip(v) for v in obj]
    return obj


def canonical_sha256(obj):
    """sha256 of the canonical JSON of obj without any 'meta' block or 'self_sha256' (time stamps and paths)."""
    return hashlib.sha256(json.dumps(_strip(obj), sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def json_safe(x):
    """JSON-safe copy: non-finite floats -> None, numpy scalars -> Python (inputs edited by hand may carry NaN)."""
    if isinstance(x, dict):
        return {str(k): json_safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [json_safe(v) for v in x]
    if isinstance(x, bool) or x is None or isinstance(x, (str, int)):
        return x
    try:
        f = float(x)
    except (TypeError, ValueError):
        return str(x)
    if hasattr(x, 'dtype') and getattr(x.dtype, 'kind', '') in 'iu':
        return int(x)
    if hasattr(x, 'dtype') and getattr(x.dtype, 'kind', '') == 'b':
        return bool(x)
    return f if math.isfinite(f) else None


def seal(obj):
    """Add the self-hash (written by every result and report)."""
    obj['self_sha256'] = canonical_sha256(obj)
    return obj


def verify_seal(obj):
    try:
        return obj.get('self_sha256') is not None and obj['self_sha256'] == canonical_sha256(obj)
    except (TypeError, ValueError):
        return False


def code_fingerprint():
    """sha256 over the package's .py files (sorted by name)."""
    h = hashlib.sha256()
    for p in sorted(glob.glob(os.path.join(HERE, '*.py'))):
        h.update(os.path.basename(p).encode())
        with open(p, 'rb') as f:
            h.update(f.read())
    return h.hexdigest()


def register_hash():
    p = os.environ.get('IWO_REGISTER', REGISTER_PATH)
    return {'file': os.path.basename(p), 'sha256': qeio.sha256(p) if os.path.isfile(p) else None}


def input_entry(r):
    """The identity of a result or report as recorded in provenance['inputs']."""
    if r is None:
        return None
    pv = r.get('provenance') or {}
    rs = r.get('run_settings') or {}
    rq = r.get('run_qualification') or {}
    try:
        rh = canonical_sha256(r)
    except (TypeError, ValueError):                      # non-finite or non-JSON content: no identity
        rh = None
    return {'cell': r.get('cell'), 'kind': r.get('kind'), 'schema': r.get('schema'),
            'result_sha256': rh, 'self_sha256': r.get('self_sha256'),
            'geometry_sha256': r.get('geometry_sha256'), 'certificate_sha256': rq.get('certificate_sha256'),
            'run_files': {k: v.get('sha256') for k, v in (pv.get('files') or {}).items() if isinstance(v, dict)},
            'smearing': rs.get('smearing'), 'degauss_Ry': rs.get('degauss_Ry'),
            'nspin': (r.get('occupations') or {}).get('nspin'), 'mode': r.get('mode'),
            'code_sha256': pv.get('code_sha256')}


def provenance_stamp(inputs=(), extra=None):
    """Provenance for every output: code, register and the inputs. Deterministic (no time stamp, no paths)."""
    out = {'code_version': __version__, 'code_sha256': code_fingerprint(), 'register': register_hash(),
           'inputs': [input_entry(r) for r in inputs if r is not None]}
    if extra:
        out.update(extra)
    return out


# ---------------------------------------------------------------- manifest
def manifest_from_spec(spec):
    """Composition manifest from a make_specs.py spec. The kind follows from the composition (formal-charge count of
    the film), never from the name."""
    film = {'In': spec['n_In'], 'W': spec['n_W'], 'O': spec['n_O']}
    nex = sum(FORMAL_CHARGE[e] * n for e, n in film.items())
    kind = ('W-doped' if spec['n_W'] > 0 else 'undoped') if nex != 0 else ('compensated' if spec['n_W'] > 0 else 'undoped')
    sub = {}
    if spec.get('substrate'):
        sub = {k[2:]: v for k, v in spec['substrate'].items() if k.startswith('n_')}
    pas = 'dissociated-water' if (spec.get('mode') != 'bulk' and spec.get('passivate', True)) else 'none'
    return {'kind': kind, 'film': film, 'substrate': sub, 'passivation': pas, 'N_ex': nex, 'seed': spec.get('seed'),
            'spec_name': spec.get('name')}


def _int_map(d):
    return isinstance(d, dict) and all(isinstance(k, str) and isinstance(v, int) and not isinstance(v, bool)
                                       for k, v in d.items())


def check_manifest(man, st):
    """Composition check of a manifest against the structure. Returns (ok, problems)."""
    if not man:
        return False, ['no manifest']
    if not isinstance(man, dict):
        return False, ['manifest is not an object']
    prob = []
    film, sub = man.get('film', {}), man.get('substrate', {})
    if not _int_map(film) or not _int_map(sub):
        return False, ['manifest film / substrate counts must be integers']
    nex = man.get('N_ex')
    if not isinstance(nex, int) or isinstance(nex, bool):
        return False, ['manifest N_ex must be an integer']
    if man.get('kind') not in KINDS:
        prob.append(f'kind {man.get("kind")!r} not one of {KINDS}')
    comp = st.composition()
    for el in ('In', 'W', 'Al', 'Hf'):
        want = film.get(el, 0) + sub.get(el, 0)
        if comp.get(el, 0) != want:
            prob.append(f'{el}: structure {comp.get(el, 0)}, manifest {want}')
    nh = comp.get('H', 0)
    o_want = film.get('O', 0) + sub.get('O', 0)
    if man.get('passivation') == 'dissociated-water':
        if nh % 2:
            prob.append(f'odd H count {nh} for dissociated-water passivation')
        o_want += nh // 2
    elif man.get('passivation') == 'none':
        if nh:
            prob.append(f'{nh} H atoms but passivation none')
    else:
        prob.append(f'passivation {man.get("passivation")!r} not one of dissociated-water / none')
    if comp.get('O', 0) != o_want:
        prob.append(f'O: structure {comp.get("O", 0)}, manifest + passivation {o_want}')
    formal = st.formal_excess()
    if formal is None or formal != nex:
        prob.append(f'formal-charge count {formal} != declared N_ex {nex}')
    nw = comp.get('W', 0)
    k = man.get('kind')
    if k == 'W-doped' and not (nw > 0 and nex == nw):
        prob.append(f'W-doped needs N_ex = n_W > 0 (n_W {nw}, N_ex {nex})')
    if k == 'compensated' and not (nw > 0 and nex == 0):
        prob.append(f'compensated needs n_W > 0 and N_ex = 0 (n_W {nw}, N_ex {nex})')
    if k == 'undoped' and not (nw == 0 and nex == 0):
        prob.append(f'undoped needs n_W = 0 and N_ex = 0 (n_W {nw}, N_ex {nex})')
    return not prob, prob


# ---------------------------------------------------------------- qualification
def unqualified(reason='no certificate'):
    q = {'certificate_sha256': None, 'certificate_valid': False, 'problems': [reason], 'relaxation': 'unknown',
         'smearing_qualified': False, 'smearing_width_Ry': None, 'geometry': 'unknown', 'manifest_verified': False,
         'manifest': None, 'seed': None, 'pseudopotentials_bound': False}
    q['reasons'] = qualification_reasons(q)
    return q


def qualification_reasons(q):
    """Recomputed from the qualification fields (never trusted from a stored list)."""
    r = []
    probs = q.get('problems')
    if not isinstance(probs, list):
        probs = ['problems field malformed']
    # rc5: ANY gate problem (the gate is NOT VALID) disqualifies every primary score, not only a failed binding
    if q.get('certificate_valid') is not True or not q.get('certificate_sha256') or probs:
        r.append('run certificate missing or NOT VALID: ' + '; '.join(str(x) for x in (probs or ['none'])))
    if q.get('relaxation') != 'converged':
        r.append(f'relaxation {str(q.get("relaxation")).upper()} (converged geometry not certified; 17 Oct rule)')
    if q.get('smearing_qualified') is not True:
        r.append('smearing qualification pending (A26/A15; not certified)')
    if q.get('manifest_verified') is not True:
        r.append('composition manifest not verified: N_ex unverified')
    if q.get('pseudopotentials_bound') is not True or not isinstance(q.get('pseudopotentials'), dict):
        r.append('pseudopotential provenance not bound by the certificate')
    if q.get('register_missing') is True:
        r.append('hypothesis register not found (IWO_REGISTER): provenance incomplete')
    return r


def _evidence_ok(block, cert_dir):
    ev = block.get('evidence') or []
    if not isinstance(ev, list) or not ev:
        return False, ['no evidence files (a list of {file, sha256} is required)']
    prob = []
    for e in ev:
        if not isinstance(e, dict) or not isinstance(e.get('file'), str) or not isinstance(e.get('sha256'), str):
            prob.append('malformed evidence entry')
            continue
        p = e['file'] if os.path.isabs(e['file']) else os.path.join(cert_dir, e['file'])
        if not os.path.isfile(p):
            prob.append(f'evidence {e.get("file")!r} missing')
        elif qeio.sha256(p) != e.get('sha256'):
            prob.append(f'evidence {e.get("file")!r} sha256 mismatch')
    return not prob, prob


def is_avg_file(name):
    return name.endswith('_avg.dat') or (name.startswith('avg_') and name.endswith('.in')) or \
        (name.startswith('pp_') and name.endswith('.in'))


def run_width(data):
    """(family, width in Ry) actually used by the read-out (None for fixed occupations)."""
    if data.occupations_kind != 'smearing' or data.degauss_ev is None:
        return None, None
    return (data.smearing or '').strip().lower(), round(data.degauss_ev / RY_EV, 10)


def validate(cert_path, name, data, st, mode=None):
    """The gate: returns the run qualification of this read-out (never raises on a malformed certificate)."""
    if not cert_path:
        return unqualified('no certificate given')
    try:
        cert = qeio.load_json(cert_path)
    except (OSError, ValueError) as e:
        return unqualified(f'certificate unreadable: {e}')
    try:
        return _validate(cert, cert_path, name, data, st, mode)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        q = unqualified(f'malformed certificate: {type(e).__name__}: {e}')
        q['certificate_sha256'] = qeio.sha256(cert_path)
        return q


def _validate(cert, cert_path, name, data, st, mode):
    cdir = os.path.dirname(os.path.abspath(cert_path))
    q = unqualified()
    q['problems'] = []
    q['certificate_sha256'] = qeio.sha256(cert_path)
    if not isinstance(cert, dict):
        raise TypeError('certificate top level is not an object')
    fatal = []
    if cert.get('schema') != CERT_SCHEMA:
        fatal.append(f'schema {cert.get("schema")!r} (expected {CERT_SCHEMA})')
    if cert.get('cell') != name:
        fatal.append(f'certificate is for {cert.get("cell")!r}, read-out is {name!r}')
    listed = cert.get('run_files')
    if not isinstance(listed, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in listed.items()):
        raise TypeError('run_files must map file names to sha256 strings')
    used = {k: v['sha256'] for k, v in data.sources.items()
            if isinstance(v, dict) and 'sha256' in v and not k.startswith(NON_BOUND_KEYS)}
    for k, v in used.items():                           # every consumed file must be bound
        if listed.get(k) != v:
            fatal.append(f'consumed file {k} not bound (certificate {listed.get(k)}, used {v})')
    if not any(k.startswith(PROJ_SOURCE_KEYS) for k in used):
        fatal.append('no projection source among the consumed files')
    if cert.get('geometry_sha256') != st.geometry_hash():
        fatal.append('geometry hash mismatch')
    if fatal:
        q['problems'] = fatal
        q['reasons'] = qualification_reasons(q)
        return q
    q['certificate_valid'] = True
    prob = q['problems']
    if mode is not None and mode != 'bulk' and not any(is_avg_file(k) for k in used):
        prob.append('planar-average inputs (<job>_avg.dat, avg_<job>.in, pp_<job>.in) not consumed: incomplete export')
    for k in ('code_sha256', 'register_sha256'):
        if k not in cert:
            prob.append(f'certificate lacks {k}')
    # pseudopotential provenance: every pseudo file of the run, with sha256 equal to the run lineage when available
    pps = cert.get('pseudopotentials')
    files = sorted({s.get('pseudo_file') for s in data.settings.get('species', []) if s.get('pseudo_file')})
    lin = data.settings.get('pseudo_sha256') or {}
    if not isinstance(pps, dict) or not files:
        prob.append('pseudopotential provenance missing (pseudopotentials: {file: sha256})')
    else:
        miss = [f for f in files if not isinstance(pps.get(f), str)]
        bad = [f for f in files if isinstance(lin.get(f), str) and pps.get(f) != lin[f]]
        unlin = [f for f in files if not isinstance(lin.get(f), str)]
        if miss:
            prob.append(f'pseudopotential sha256 missing for {miss}')
        if bad:
            prob.append(f'pseudopotential sha256 differs from the run lineage for {bad}')
        if not lin:
            prob.append('run lineage (lineage_final.dat) not in the export: pseudopotential hashes not verifiable')
        elif unlin:
            prob.append(f'run lineage does not cover every UPF used (no lineage hash for {unlin})')
        q['pseudopotentials_bound'] = not miss and not bad and not unlin and bool(lin)
        if q['pseudopotentials_bound']:
            q['pseudopotentials'] = {f: pps[f] for f in files}       # certified content hashes (UPF identity)
    man = cert.get('manifest')
    ok, mprob = check_manifest(man, st)
    q['manifest'] = man if isinstance(man, dict) else None
    q['manifest_verified'] = ok
    q['seed'] = man.get('seed') if isinstance(man, dict) else None
    prob += [f'manifest: {p}' for p in mprob]
    blocks = {}
    for key in ('relaxation', 'smearing', 'geometry'):
        b = cert.get(key)
        if b is None:
            b = {}
        if not isinstance(b, dict):
            raise TypeError(f'{key} block must be an object')
        blocks[key] = b
    rel, sm, geo = blocks['relaxation'], blocks['smearing'], blocks['geometry']
    st_rel = rel.get('status', 'unknown')
    if st_rel not in RELAX:
        prob.append(f'relaxation status {st_rel!r} unknown (one of {RELAX})')
    elif st_rel in ('converged', 'exploratory'):
        good, p_ = _evidence_ok(rel, cdir)
        q['relaxation'] = st_rel if good else 'unknown'
        prob += [f'relaxation: {p}' for p in p_]
    st_sm = sm.get('status', 'pending')
    if st_sm not in SMEAR:
        prob.append(f'smearing status {st_sm!r} unknown (one of {SMEAR})')
    elif st_sm == 'qualified':
        good, p_ = _evidence_ok(sm, cdir)
        prob += [f'smearing: {p}' for p in p_]
        w = sm.get('width_Ry')
        fam, rw = run_width(data)
        if isinstance(w, bool) or not isinstance(w, (int, float)) or not math.isfinite(w):
            prob.append(f'smearing: qualified without a numeric width_Ry ({w!r})')
            good = False
        elif rw is None:
            prob.append('smearing: the run width is unknown (fixed occupations or no degauss)')
            good = False
        elif abs(float(w) - rw) > WIDTH_TOL_RY:
            prob.append(f'smearing: certified width {w} Ry != width actually used {rw} Ry')
            good = False
        if fam is not None and fam not in GAUSSIAN:
            prob.append(f'smearing: family {fam!r} is not Gaussian (A15/A26 FINALs are Gaussian)')
            good = False
        q['smearing_qualified'] = good
        q['smearing_width_Ry'] = w if isinstance(w, (int, float)) and not isinstance(w, bool) else None
    st_geo = geo.get('status', 'unknown')
    if st_geo not in GEOM:
        prob.append(f'geometry status {st_geo!r} unknown (one of {GEOM})')
    elif st_geo in ('polished', 'mv'):
        good, p_ = _evidence_ok(geo, cdir)
        q['geometry'] = st_geo if good else 'unknown'
        prob += [f'geometry: {p}' for p in p_]
    q['construction'] = man.get('construction') if isinstance(man, dict) else None
    q['reasons'] = qualification_reasons(q)
    return q


def gate_valid(q):
    return q.get('certificate_valid') is True and not q.get('problems')


def pseudo_hashes(data, pseudo_dir=None):
    """{pseudo file: sha256} from the run lineage, else from a directory of UPF files."""
    files = sorted({s.get('pseudo_file') for s in data.settings.get('species', []) if s.get('pseudo_file')})
    lin = data.settings.get('pseudo_sha256') or {}
    out = {f: lin[f] for f in files if f in lin}
    if pseudo_dir:
        for f in files:
            p = os.path.join(pseudo_dir, f)
            if f not in out and os.path.isfile(p):
                out[f] = qeio.sha256(p)
    return out


def _rel(f, cdir):
    try:
        return os.path.relpath(os.path.abspath(f), cdir).replace(os.sep, '/')
    except ValueError:                                   # other drive / mount (Windows): keep the absolute path
        return os.path.abspath(f)


def compile_certificate(name, data, st, out_path, spec=None, manifest=None, relaxation=None, smearing=None,
                        geometry=None, compiled_by='', notes='', pseudo_dir=None):
    """Write a certificate. relaxation/smearing/geometry: (status, [evidence paths], extra dict) or None."""
    cdir = os.path.dirname(os.path.abspath(out_path))

    def block(item):
        if not item:
            return None
        status, files, extra = item
        b = {'status': status, 'evidence': [{'file': _rel(f, cdir), 'sha256': qeio.sha256(f)} for f in files]}
        b.update(extra or {})
        return b
    man = manifest if manifest is not None else (manifest_from_spec(spec) if spec else None)
    cert = {'schema': CERT_SCHEMA, 'cell': name,
            'run_files': {k: v['sha256'] for k, v in data.sources.items()
                          if isinstance(v, dict) and 'sha256' in v and not k.startswith(NON_BOUND_KEYS)},
            'geometry_sha256': st.geometry_hash(), 'pseudopotentials': pseudo_hashes(data, pseudo_dir),
            'manifest': man,
            'relaxation': block(relaxation) or {'status': 'unknown'},
            'smearing': block(smearing) or {'status': 'pending'},
            'geometry': block(geometry) or {'status': 'unknown'},
            'compiled_by': compiled_by, 'notes': notes, 'code_version': __version__,
            'code_sha256': code_fingerprint(), 'register_sha256': register_hash()['sha256']}
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(cert, f, indent=1)
    return cert


def geometry_hash(species, pos, cell):
    d = GEOMETRY_HASH_DECIMALS
    payload = {'species': list(species), 'positions': [[round(float(x), d) + 0.0 for x in p] for p in pos],
               'cell': [[round(float(x), d) + 0.0 for x in v] for v in cell]}
    return canonical_sha256(payload)


def parse_lineage(path):
    """{pseudo file: sha256} from the 'sha256 <hash> pseudo/<file>' lines of lineage_final.dat (D-24)."""
    out = {}
    with qeio.open_text(path) as fh:
        for line in fh:
            m = re.fullmatch(r'sha256 ([0-9a-f]{64}) pseudo/(\S+)', line.strip())
            if m:
                f, h = m.group(2), m.group(1)
                out[f] = h if out.get(f, h) == h else None      # conflicting entries: not covered (rc5)
    return out
