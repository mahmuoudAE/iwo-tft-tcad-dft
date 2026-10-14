#!/usr/bin/env python3
"""cert_assert.py: D-42 F9 certificate assertions (draft v18, 2026-10-14). Standalone, standard library only.

v16 (Codex 2026-10-14, v15 reply; enforced in f9_common, re-derived here): the narrow Requirements resolver for split-route
resource evidence (same-ad positive conjunct helpers only; missing or cyclic helpers UNRESOLVED).

v15 (Codex 2026-10-14T08:59Z; enforced in f9_common, re-derived here): HTCondor new-syntax argument parsing for the A43
dry run (every argument whitelisted) and refusal of unsupported submit directives (include, conditionals, continuations).

v14 (Codex v13 review, FIX_FIRST; enforced in f9_writers / f9_common, re-derived here): A43 submission binding (one
scheduler DAGMan, audited executable and run directory, permitted arguments, the submitted ad and dagman.out linked to
the reviewed files and the first resumed node); scientific position anchored at the rescue, separate from the budget;
guard-only rescue starts carry their pending transition to the first actual SCF.

v13 (Codex v12 review, FIX_FIRST; enforced in f9_writers / f9_common, re-derived here): escape-aware Requirements on the
audited GPU attribute; the [infra] bestvalid exception disabled; scientific position across administrative renumbering;
A43 count-enforcement files (DAG identity, config, exact RETRY, dry run, dagman.out header).

v12 (Codex v11 review, FIX_FIRST; enforced in f9_writers / f9_common, re-derived here): structural resource predicates
and unique environment values; guard-only rescues keep authorization and terminal-status checks; no continuation after
an A35/A36 SCF failure; the [infra] bestvalid exception bound to its registered chains and a rollback record.

v11 (Codex v10 review, FIX_FIRST; enforced in f9_writers / f9_common, re-derived here): guard-only first executions of
a new attempt need the verified rescue record; both registered alternating splits; G* minimum over all eligible
evaluations before deduplication; rescue files' remaining RETRY bound; historical rescues recorded separately;
resource-route evidence from the split segment's own cluster.

v10 (Codex v9 review, FIX_FIRST; enforced in f9_writers / f9_common, re-derived here): the DAG allowance from attempt 1
(guard-only attempts count, evictions do not; A39 +9 after exhaustion only), pause-bound suspension rules, result-
informed continuation amendments that preserve the state, and the registered split construction (cell and route).

v9 (Codex v8 review, FIX_FIRST): RELAX asserts the registered fresh start of every segment (start settings with QE
defaults resolved); bestvalid is recomputed from bound evaluations; section-3 rescues need a registered, once-used
authorization with the remaining executions preserved, and nothing revives a terminal rescue failure (f9_writers);
label splits only in the A25/A30/A34 scope; a positive certificate that needs a FINAL requires the registered FINAL
template of its cell (f9_common.REGISTERED_FINAL_TEMPLATES; none registered in this draft: release gate).

v8 (Codex v7 review, FIX_FIRST): C3 attempts bound to their actual run (scheduler history); settings changes only as
the exact registered transitions with their triggers; ordered execution; mandatory gates from the rescue start (A35
s4, A36 s2), earlier comparisons diagnostic; section-3 resets / attempt<N> rescues and label splits as explicit
transitions.

v7 (Codex v6 review 2026-10-13T02:10Z, FIX_FIRST): inventories and exports bound to the exact destination and run of
the frozen plan; segments linked to the geometry the previous segment returned (or a verified D-24 transition reset);
archives bound to run, k and cluster with in-job member times inside the cluster's execution; only registered epoch
starts change settings, and earlier-epoch gate failures are inherited; unresolved C3 slots block only their own cell /
geometry (prospective scope ruling); pre-item-B checkpoint inputs, guard-only attempts, export_manifest_final.dat.

v6 (Codex 2026-10-13 ~01:45Z, FIX_FIRST on v5): a failed C3 attempt counts as 'no_output' only with a verified
artifact inventory showing no export (f9_writers; re-checked here); relaxation segments bind the saved segment input
relax_s<k>_input.in, never the returned relax.in (f9_writers._bind_segment).

NOT part of the frozen reader (rc7); it imports nothing from it. It reads ONE run certificate written by
`python -m analysis certify` and the evidence it binds. certify.py:231-245/347-382 accept any status whose evidence
files exist with the bound sha256; F9 accepts a claim only if the evidence MEANS what the claim needs.

v3 (Codex 2026-10-12T15:56Z, FIX_FIRST):
  * Every F9 record (schema iwo-f9-evidence/2) is RE-DERIVED here from its sha256-bound sources with the frozen
    writers (f9_writers.derive) and rejected if the result differs, or if it was written by another writer version.
    A PASS label, a hand-edited number, an omitted gate or a dropped segment cannot survive.
  * Qualification and restart gates are judged on finite numbers against the registered tolerances
    (|dF| <= 1e-5 Ry, max |dF| <= 1e-3 Ry/bohr, inclusive), never on a label. The mandatory restart-gate inventory is
    derived from the complete lineage (f9_common.required_gate_boundaries); a missing or unevaluable gate fails.
  * Dates come only from the frozen defaults and a verified A39(e) cern_extension record. There is no date option.
  * 'qualified' needs the complete C3 inventory (a readout_manifest record). Any applicable same-cell,
    same-geometry C3 FAIL rejects the claim at every width (A31(e)); the candidate width additionally needs a fresh
    C3 PASS with this run as the compared width; 0.001 Ry needs fresh PASS at 0.002 and 0.005 with this run as
    the reference. Comparisons at another geometry (e.g. a polish) never qualify a moved-from geometry.

Sight rules: only F9 records, certificates and sealed rc7 C3 / A15-audit / cell records are interpreted; any other
file is hashed and rejected. F9 records are scanned for forbidden keys and values; QE output is read only through
the A39(a6) allowlist (f9_common.read_qe_output) with its deny assertion. The output carries only checker-generated
text with validated names, hashes, statuses, UTC stamps, widths and the energy / force differences of the gates.

Usage:  python -I -B cert_assert.py CERT.json [--reports R.json ...] [--extension EXT.json] [--json OUT.json]
        python -I -B cert_assert.py --self-test
Exit:   0 CLAIMS_OK, 1 DOWNGRADE_REQUIRED, 2 MALFORMED or SIGHT_ABORT.
"""
import argparse
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import f9_common as F  # noqa: E402
import f9_writers as W  # noqa: E402

VERSION = 'cert_assert 0.18.0-draft (D-42 F9 v18, 2026-10-14)'
CERT_SCHEMA, CELL_SCHEMA, RECORD_SCHEMA = F.CERT_SCHEMA, F.CELL_SCHEMA, F.RECORD_SCHEMA
RC7_CODE_SHA256 = F.RC7_CODE_SHA256
WIDTH_TOL_RY = 1e-9
C3_REFERENCE_WIDTH_RY = 0.001
C3_PENDING_WIDTHS_RY = (0.002, 0.005)
AUDIT_WIDTHS_RY = (0.001, 0.002, 0.005)
POLISH_WIDTH_RY = 0.005
A15_ROLES = {'aIO': ('aIO_2p0_s1', 'aIO_2p0_s2'), 'aIWO': ('aIWO_2p0_s1', 'aIWO_2p0_s2'),
             'compensated': ('aIWO_2p0_comp_s1',)}
A15_STATUS = W.A15_STATUS
SUBSTITUTION_BASIS = 'A31(f) relaxation status at the cutoff'
POLISH_CELLS = ('aIWO_0p7_s1', 'aIWO_1p0_s1', 'aIWO_2p0_s1')
NEVER_POLISHED = ('aIWO_2p0_s2', 'aIWO_0p8_s2')
QUAL_ROUTES = ('A35', 'A36', 'A36-conditional', 'C4-polish')
QUAL_CELLS = ('aIWO_0p8_s2', 'aIWO_2p0_s2', 'aIWO_2p0_comp_s1')
TIMING_SOURCES = ('htcondor_job_log', 'snapshot_completed_utc')
MAX_PARSE_BYTES = 64 * 1024 * 1024
MAX_DEPTH = 4

FORBIDDEN_KEY = re.compile(r'fermi|eigen|band|homo|lumo|gap|edge|proj|pdos|pr_n|class|f_ext|f_locw|w5d|delta_w|'
                           r'vbm|cbm|f_nk', re.I)
FORBIDDEN_VALUE = re.compile(r'fermi|eigenval|highest occupied|lowest unoccupied|bands \(ev\)', re.I)
SKIP_KEY_SCAN = ('run_files', 'reference_run_files', 'upf_sha256', 'run_file_binding')

OUTPUT_KEYS = ('checker', 'checker_sha256', 'writer_sha256', 'certificate', 'certificate_sha256', 'cell',
               'cutoff_utc', 'qualification_deadline_utc', 'extension', 'structure_problems', 'blocks', 'notes',
               'stale_reports', 'verdict', 'exit_code')
BLOCK_KEYS = ('claimed', 'hash_binding', 'semantic', 'verdict', 'permitted', 'reasons', 'notes')

_NAME = re.compile(r'^[A-Za-z0-9_.+>-]{1,96}$')
_HEX64 = re.compile(r'^[0-9a-f]{64}$')
SightAbort = F.SightAbort


class Malformed(Exception):
    pass


# ---------------------------------------------------------------- helpers
sha256_file, canonical_sha256, verify_seal = F.sha256_file, F.canonical_sha256, F.verify_seal
parse_utc, fmt_utc, family = F.parse_utc, F.fmt_utc, F.family


def is_hex64(x):
    return isinstance(x, str) and bool(_HEX64.match(x))


def tok(x):
    return x if isinstance(x, str) and _NAME.match(x) else '<invalid>'


def short(h):
    return h[:12] if is_hex64(h) else '<invalid>'


def num(x):
    return float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) else None


def same_w(a, b):
    a, b = num(a), num(b)
    return a is not None and b is not None and abs(a - b) <= WIDTH_TOL_RY


def wfmt(x):
    x = num(x)
    return '<invalid>' if x is None else f'{x:g}'


def bound_files(d):
    if not isinstance(d, dict):
        return None
    return {k: v for k, v in d.items() if isinstance(k, str) and not k.startswith('_')}


def hashmap_ok(d):
    return isinstance(d, dict) and bool(d) and all(isinstance(k, str) and is_hex64(v) for k, v in d.items())


def sight_scan(obj, where):
    if isinstance(obj, dict):
        for k, v in obj.items():
            m = FORBIDDEN_KEY.search(str(k))
            if m:
                raise SightAbort(f'{where}: forbidden key pattern {m.group(0).lower()!r} in an F9 record')
            if k in SKIP_KEY_SCAN:
                continue
            sight_scan(v, where)
    elif isinstance(obj, list):
        for v in obj:
            sight_scan(v, where)
    elif isinstance(obj, str):
        m = FORBIDDEN_VALUE.search(obj)
        if m:
            raise SightAbort(f'{where}: forbidden value pattern {m.group(0).lower()!r} in an F9 record')


# ---------------------------------------------------------------- evidence
class Item:
    def __init__(self, path, sha, kind, obj):
        self.path, self.sha256, self.kind, self.obj = path, sha, kind, obj
        self.verified = None          # None: not checked; [] ok; [problems]

    @property
    def name(self):
        b = os.path.basename(self.path)
        return b if _NAME.match(b) else '<file>'

    @property
    def rtype(self):
        return self.obj.get('type') if self.kind == 'record' else None

    @property
    def d(self):
        return (self.obj.get('derived') or {}) if self.kind == 'record' else {}

    def get(self, k, default=None):
        return self.obj.get(k, default) if isinstance(self.obj, dict) else default


class Ctx:
    """Dates are the frozen registered dates, shifted only by a verified cern_extension record (A39(e))."""

    def __init__(self, extension=None):
        self.cache, self.cert_results = {}, {}
        self.extension = {'applied': False}
        ext = None
        if extension is not None:
            it = self.load(extension)
            if it.kind != 'record' or it.rtype != 'cern_extension':
                raise Malformed('extension: not an F9 cern_extension record')
            prob = self.verify(it)
            if prob:
                raise Malformed('extension record not verified: ' + '; '.join(prob))
            ext = it.d
        dates = F.registered_dates(ext)
        self.cutoff, self.qual_deadline = dates['cutoff'], dates['qualification']
        if ext:
            base = F.registered_dates(None)
            self.extension = {'applied': True, 'record_sha256': it.sha256, 'delta_days': ext['delta_days'],
                              'logged_utc': ext['logged_utc'], 'cutoff_shifted': self.cutoff != base['cutoff'],
                              'qualification_deadline_shifted': self.qual_deadline != base['qualification']}

    def load(self, path):
        path = os.path.abspath(path)
        if path in self.cache:
            return self.cache[path]
        sha = sha256_file(path)
        kind, obj = 'other', None
        if os.path.getsize(path) <= MAX_PARSE_BYTES:
            try:
                with open(path, 'rb') as f:
                    o = json.loads(f.read().decode('utf-8'))
            except (ValueError, UnicodeDecodeError):
                o = None
            if isinstance(o, dict):
                if o.get('schema') == RECORD_SCHEMA:
                    sight_scan({k: o.get(k) for k in ('type', 'params', 'derived')}, os.path.basename(path))
                    kind, obj = 'record', o
                elif o.get('schema') == CERT_SCHEMA:
                    kind, obj = 'certificate', o
                elif o.get('kind') in ('C3', 'A15 smearing audit') or o.get('schema') == CELL_SCHEMA:
                    kind, obj = 'rc7', o
        it = Item(path, sha, kind, obj)
        self.cache[path] = it
        return it

    def verify(self, it):
        """Re-derive an F9 record from its bound sources with the frozen writers."""
        if it.verified is not None:
            return it.verified
        p = []
        o = it.obj
        if it.rtype not in W.TYPES:
            p.append(f'record {it.name}: unknown type')
        elif o.get('writer_sha256') != W.writer_fingerprint():
            p.append(f'record {it.name}: written by another writer version (writer sha256 {short(o.get("writer_sha256"))})')
        elif not all(isinstance(o.get(k), dict) for k in ('params', 'sources', 'derived')):
            p.append(f'record {it.name}: params / sources / derived malformed')
        else:
            it.verified = []                     # provisional: guards against reference cycles
            try:
                paths = W.resolve(o['sources'], os.path.dirname(it.path))
                again = W.derive(it.rtype, o['params'], paths)
                if canonical_sha256(again) != canonical_sha256(o['derived']):
                    p.append(f'record {it.name}: not reproducible from its bound sources (edited or stale)')
                # v4: every F9 record the sources reference must itself re-derive (e.g. role-status lineages)
                for f in W.referenced_files(paths):
                    sub = self.load(f)
                    if sub.kind == 'record' and sub is not it:
                        bad = self.verify(sub)
                        if bad:
                            p.append(f'record {it.name}: referenced record {sub.name} not verified')
            except F.DeriveError as e:
                p.append(f'record {it.name}: not derivable from its sources ({tok(str(e))})')
            except (KeyError, TypeError, ValueError, IndexError):
                p.append(f'record {it.name}: not derivable from its sources (malformed)')
        it.verified = p
        return p

    def ref(self, item, key, what):
        """A referenced file from a record's sources (sha256-checked); records are verified too."""
        r = (item.get('sources') or {}).get(key)
        if not isinstance(r, dict) or not isinstance(r.get('file'), str) or not is_hex64(r.get('sha256')):
            return None, f'{what}: reference missing'
        p = r['file'] if os.path.isabs(r['file']) else os.path.join(os.path.dirname(item.path), r['file'])
        if not os.path.isfile(p):
            return None, f'{what}: referenced file missing'
        it = self.load(p)
        if it.sha256 != r['sha256']:
            return None, f'{what}: referenced file sha256 mismatch'
        if it.kind == 'record':
            v = self.verify(it)
            if v:
                return None, f'{what}: ' + '; '.join(v)
        return it, None


class Cert:
    def __init__(self, path, obj, sha):
        self.path, self.obj, self.sha256 = os.path.abspath(path), obj, sha
        self.dir = os.path.dirname(self.path)
        self.cell = obj.get('cell')
        self.run_files = bound_files(obj.get('run_files'))
        self.geometry = obj.get('geometry_sha256')
        self.pps = obj.get('pseudopotentials')
        sm = obj.get('smearing') if isinstance(obj.get('smearing'), dict) else {}
        self.width = sm.get('width_Ry')

    def structure_problems(self):
        p = []
        if self.obj.get('schema') != CERT_SCHEMA:
            p.append(f'schema is not {CERT_SCHEMA}')
        if not isinstance(self.cell, str) or not _NAME.match(self.cell):
            p.append('cell name missing or not a plain name')
        if not hashmap_ok(self.run_files):
            p.append('run_files must map file names to sha256 strings')
        if not is_hex64(self.geometry):
            p.append('geometry_sha256 missing or malformed')
        if not hashmap_ok(self.pps):
            p.append('pseudopotentials must map UPF names to sha256 strings')
        for k in ('relaxation', 'smearing', 'geometry'):
            if self.obj.get(k) is not None and not isinstance(self.obj.get(k), dict):
                p.append(f'{k} block is not an object')
        return p


def bind(block, cert, ctx):
    ev = block.get('evidence')
    if not isinstance(ev, list) or not ev:
        return [], ['no evidence files (a list of {file, sha256} is required)']
    items, prob = [], []
    for e in ev:
        if not isinstance(e, dict) or not isinstance(e.get('file'), str) or not isinstance(e.get('sha256'), str):
            prob.append('malformed evidence entry')
            continue
        p = e['file'] if os.path.isabs(e['file']) else os.path.join(cert.dir, e['file'])
        if not os.path.isfile(p):
            prob.append('evidence file missing')
            continue
        it = ctx.load(p)
        if it.sha256 != e['sha256']:
            prob.append(f'evidence {it.name}: sha256 mismatch')
            continue
        items.append(it)
    return items, prob


def record_problems(items, ctx):
    p = []
    for it in items:
        if it.kind == 'other' or (it.kind == 'record' and it.rtype not in W.TYPES):
            p.append(f'evidence {it.name}: hash-bound but not an F9 evidence record (content not interpreted)')
        elif it.kind == 'record':
            p += ctx.verify(it)
    return p


def records(items, rtype, **match):
    return [it for it in items if it.kind == 'record' and it.rtype == rtype and not it.verified and
            all(it.d.get(k) == v for k, v in match.items())]


def one(cands, what):
    shas = {c.sha256 for c in cands}
    if not cands:
        return None, f'no {what}'
    if len(shas) > 1:
        return None, f'ambiguous: {len(shas)} different {what} records'
    return cands[0], None


def src_sha(item, key):
    r = (item.get('sources') or {}).get(key)
    return r.get('sha256') if isinstance(r, dict) else None


# ---------------------------------------------------------------- lineage, gates, qualification
def families(d):
    return [family(h.get('smearing')) for h in d.get('smearing_history') or [] if isinstance(h, dict)]


def qualification_needed(d):
    return d.get('route') in QUAL_ROUTES or d.get('cell') in QUAL_CELLS or len(set(families(d))) > 1


def gate_inventory_problems(L, label):
    d, p = L.d, []
    req = F.required_gate_boundaries(d.get('cell'), d.get('route'), d.get('segments') or [])
    if req != d.get('required_gates'):
        p.append(f'{label}: restart-gate inventory inconsistent with the lineage')
    gates = {g.get('boundary'): g for g in d.get('gates') or [] if isinstance(g, dict)}
    for b in req:
        g = gates.get(b)
        if g is None:
            p.append(f'{label}: mandatory restart gate {tok(b)} missing (an omitted gate is never "not exercised")')
            continue
        if g.get('error'):
            p.append(f'{label}: restart gate {tok(b)} not evaluable ({tok(g.get("error"))}): counts as failed')
            continue
        dF, dm = num(g.get('delta_F_Ry')), num(g.get('max_abs_dF_Ry_bohr'))
        if dF is None or dm is None or g.get('n_components') != 3 * (d.get('nat') or 0):
            p.append(f'{label}: restart gate {tok(b)} without finite differences over all force components')
            continue
        if abs(dF) > F.GATE_DF_RY:
            p.append(f'{label}: restart gate {tok(b)} FAILED: |dF| = {abs(dF):.3g} Ry > {F.GATE_DF_RY:g} Ry '
                     '(inherited by every descendant, A35)')
        if dm > F.GATE_DFORCE_RY_BOHR:
            p.append(f'{label}: restart gate {tok(b)} FAILED: max |dF| = {dm:.3g} Ry/bohr > '
                     f'{F.GATE_DFORCE_RY_BOHR:g} Ry/bohr (inherited by every descendant, A35)')
    return p


def qualification_problems(L, quals, ctx, label):
    d = L.d
    cands = [q for q in quals if q.kind == 'record' and q.rtype == 'qualification_scf' and not q.verified and
             q.d.get('cell') == d.get('cell') and q.d.get('geometry_sha256') == d.get('final_geometry_sha256')]
    Q, err = one(cands, 'verified qualification_scf record at the final geometry')
    if Q is None:
        return [f'{label}: final qualification missing ({err}); required for route {tok(d.get("route"))} '
                '(A35/A36; D-42 F5 for C4 polishes, zero-step included)']
    q, p = Q.d, []
    if src_sha(Q, 'lineage') != L.sha256:
        p.append(f'{label}: the qualification was derived against another lineage record')
    if q.get('settings_sha256') != d.get('relaxation_settings_sha256'):
        p.append(f'{label}: qualification settings differ from the relaxation settings (frozen settings hash)')
    if q.get('fresh_start') is not True:
        p.append(f'{label}: qualification is not a fresh start')
    if q.get('scf_converged') is not True:
        p.append(f'{label}: qualification SCF not converged (a failed qualification, A35)')
    cw = q.get('compared_with') or {}
    if cw.get('segment') != (d.get('last_evaluation') or {}).get('segment') or \
            cw.get('geometry_sha256') != d.get('final_geometry_sha256'):
        p.append(f'{label}: qualification not compared with the relaxation\'s last SCF at the final geometry')
    dF, dm = num(q.get('delta_F_Ry')), num(q.get('max_abs_dF_Ry_bohr'))
    if dF is None or dm is None or q.get('n_components') != 3 * (d.get('nat') or 0):
        p.append(f'{label}: qualification without finite differences over all force components '
                 f'({tok(q.get("comparison_error")) if q.get("comparison_error") else "missing"})')
    else:
        if abs(dF) > F.GATE_DF_RY:
            p.append(f'{label}: qualification FAILED: |dF| = {abs(dF):.3g} Ry > {F.GATE_DF_RY:g} Ry')
        if dm > F.GATE_DFORCE_RY_BOHR:
            p.append(f'{label}: qualification FAILED: max |dF| = {dm:.3g} Ry/bohr > {F.GATE_DFORCE_RY_BOHR:g} Ry/bohr')
    t = parse_utc(q.get('completed_utc'))
    if q.get('timing_source') not in TIMING_SOURCES or t is None:
        p.append(f'{label}: qualification completion time not verifiable')
    else:
        if t > ctx.qual_deadline:
            p.append(f'{label}: qualification completed {fmt_utc(t)}, after the deadline {fmt_utc(ctx.qual_deadline)}')
        tb = parse_utc(d.get('bfgs_converged_utc'))
        if tb is not None and t < tb:
            p.append(f'{label}: qualification precedes bfgs convergence (inconsistent records)')
    return p


def lineage_problems(L, quals, ctx, depth, label, seen=()):
    d, p = L.d, []
    if d.get('route') not in F.ROUTES:
        p.append(f'{label}: route not recognised')
    if d.get('bfgs_converged') is not True:
        p.append(f'{label}: A19 bfgs converged not printed')
    else:
        t = parse_utc(d.get('bfgs_converged_utc'))
        if d.get('timing_source') not in TIMING_SOURCES or t is None:
            p.append(f'{label}: A19 timing not verifiable')
        elif t > ctx.cutoff:
            p.append(f'{label}: A19 bfgs converged at {fmt_utc(t)}, after the cutoff {fmt_utc(ctx.cutoff)} '
                     '(no retrospective promotion)')
        # v4 (Codex 20:25Z item 2): the registered convergence criterion, as separate assertions
        res = d.get('final_residual') or {}
        mf, de = num(res.get('max_force_component_Ry_bohr')), res.get('energy_change_Ry')
        if mf is None or mf > F.REGISTERED_FORC_CONV_THR:
            p.append(f'{label}: final residual force {"<invalid>" if mf is None else f"{mf:.3g}"} Ry/bohr exceeds '
                     f'the registered forc_conv_thr {F.REGISTERED_FORC_CONV_THR:g} Ry/bohr')
        if de is not None and (num(de) is None or abs(de) > F.REGISTERED_ETOT_CONV_THR):
            p.append(f'{label}: final energy change exceeds the registered etot_conv_thr '
                     f'{F.REGISTERED_ETOT_CONV_THR:g} Ry')
    if d.get('registered_ionic_thresholds') is not True:
        seg_th = [f'{tok(s.get("segment"))}: forc {wfmt((s.get("ionic_thresholds") or {}).get("forc_conv_thr"))}, '
                  f'etot {wfmt((s.get("ionic_thresholds") or {}).get("etot_conv_thr"))}'
                  for s in d.get('segments') or [] if isinstance(s, dict)]
        p.append(f'{label}: the active epoch did not use the registered ionic thresholds (forc_conv_thr 1e-3 AND '
                 f'etot_conv_thr 1e-4 required; {"; ".join(seg_th[-3:])})')
    for s in d.get('terminal_scf_failures') or []:
        p.append(f'{label}: terminal SCF failure in the active epoch (segment {tok(s)}): one-attempt / D-24 rule; '
                 'no later segment can revive it')
    for s in d.get('segments') or []:          # v9 (Codex v8 item 1): the registered fresh start, defaults resolved
        st = s.get('start_settings') if isinstance(s, dict) else None
        if not isinstance(st, dict) or st.get('control.restart_mode') != 'from_scratch' or \
                st.get('electrons.startingpot') != 'atomic' or st.get('electrons.startingwfc') not in F.FRESH_WFC:
            p.append(f'{label}: segment {tok((s or {}).get("segment"))} is not the registered fresh start '
                     '(restart_mode / startingpot / startingwfc)')
    p += gate_inventory_problems(L, label)
    p += inherited_problems(L, ctx, depth, label, seen)
    if qualification_needed(d):
        p += qualification_problems(L, quals, ctx, label)
    return p


def inherited_problems(L, ctx, depth, label, seen=()):
    if not (L.get('sources') or {}).get('parent'):
        if L.d.get('route') == 'C4-polish':
            return [f'{label}: C4-polish lineage without a reference to its MV parent certificate']
        return []
    if depth >= MAX_DEPTH or L.sha256 in seen:
        return [f'{label}: parent chain too deep or cyclic']
    P, err = ctx.ref(L, 'parent', f'{label}: parent')
    if P is None:
        return [err]
    if P.kind == 'certificate':
        r = evaluate(P.path, ctx, depth + 1)
        rel = r['blocks'].get('relaxation', {})
        if rel.get('claimed') != 'converged' or rel.get('verdict') != 'OK':
            sub = '; '.join(rel.get('reasons', [])[:4]) or f'claimed {rel.get("claimed")}'
            return [f'{label}: inherited: parent {tok(r.get("cell"))} relaxation not certified converged ({sub})']
        if L.d.get('route') == 'C4-polish':
            geo = r['blocks'].get('geometry', {})
            if geo.get('claimed') != 'mv' or geo.get('verdict') != 'OK':
                return [f'{label}: inherited: parent geometry not a certified MV geometry']
        return []
    if P.kind == 'record' and P.rtype == 'relaxation_lineage':
        if L.d.get('route') == 'C4-polish':
            return [f'{label}: the parent of a C4 polish must be the MV parent certificate']
        q = gate_inventory_problems(P, f'{label}: inherited from {P.name}')
        q += inherited_problems(P, ctx, depth + 1, f'{label}: inherited', tuple(seen) + (L.sha256,))
        return q
    return [f'{label}: parent is not a certificate or a relaxation_lineage record']


# ---------------------------------------------------------------- block semantics
def lineage_for(cert, items):
    return one(records(items, 'relaxation_lineage', cell=cert.cell, final_geometry_sha256=cert.geometry),
               'verified relaxation_lineage record for this cell ending at the certified geometry')


def sem_relaxation_converged(cert, items, ctx, depth):
    L, err = lineage_for(cert, items)
    if L is None:
        return [f'relaxation: {err} (exact geometry linkage)'], []
    p = lineage_problems(L, items, ctx, depth, 'relaxation')
    notes = [] if L.d.get('required_gates') else [f'restart gates: none required for {tok(L.d.get("cell"))} / '
                                                  f'{tok(L.d.get("route"))} (no boundary in a gated epoch)']
    hist = L.d.get('historical_scf_failures') or []
    if hist:
        notes.append('historical SCF failures before the active epoch (disclosed, not a veto): '
                     + ', '.join(tok(s) for s in hist))
    notes += lineage_disclosures(L.d)
    return p, notes


def lineage_disclosures(d):
    """v7/v8: guard-only attempts, registered transitions, label splits, administrative transitions and the
    diagnostic (non-mandatory) comparisons are disclosed; the writer has verified them, and none of them is a veto."""
    out = []
    g = [tok(x.get('segment')) for x in d.get('guard_only_attempts') or [] if isinstance(x, dict)]
    if g:
        out.append('guard-only attempts (stopped before pw.x; historical indices kept): ' + ', '.join(g))
    for e in d.get('epoch_starts') or []:
        if isinstance(e, dict):
            out.append(f'registered transition at {tok(e.get("segment"))} ({tok(e.get("amendment"))}'
                       f'{"; rescue start, mandatory gates follow" if e.get("rescue") else ""})')
    if d.get('label_splits'):
        out.append('label splits (no epoch): ' + ', '.join(tok(x) for x in d['label_splits']))
    rr = sorted({tok(s.get('resource_route')) for s in d.get('segments') or [] if isinstance(s, dict) and s.get('resource_route')})
    if rr:
        out.append('split-label resource route(s) (construction verified; not a settings change): ' + ', '.join(rr))
    for kind in ('d24_transition_reset', 'section3_reset', 'section3_rescue'):
        r = [tok(s.get('segment')) for s in d.get('segments') or []
             if isinstance(s, dict) and s.get('continuation') == kind]
        if r:
            out.append(f'{kind.replace("_", " ")} before: ' + ', '.join(r) + ' (record verified)')
    dg = [x for x in d.get('diagnostic_comparisons') or [] if isinstance(x, dict)]
    bad = [tok(x.get('boundary')) for x in dg if x.get('error') or F.gate_failed(x)]
    if dg:
        out.append(f'diagnostic comparisons (not gates, never a veto): {len(dg)}'
                   + (f'; outside tolerance or not evaluable: {", ".join(bad)}' if bad else ''))
    return out


def sem_relaxation_exploratory(cert, items, ctx, depth):
    linked = records(items, 'relaxation_lineage', cell=cert.cell, final_geometry_sha256=cert.geometry) + \
        records(items, 'cutoff_selection', cell=cert.cell, g_star_geometry_sha256=cert.geometry)
    if not linked:
        return ['relaxation: exploratory geometry not linked to a verified lineage or A39(a) selection record'], []
    return [], ['exploratory: never counts as resolved coverage (A35/A36; section 3)']


def sem_geometry_mv(cert, items, ctx, depth):
    L, err = lineage_for(cert, items)
    if L is None:
        return [f'geometry mv: {err}'], []
    p = []
    fams = families(L.d)
    if not fams or any(f != 'mv' for f in fams):
        p.append('geometry mv: the lineage contains non-MV relaxation smearing (an MV geometry needs an MV-only '
                 'lineage)')
    if L.d.get('route') == 'C4-polish':
        p.append('geometry mv: a C4 polish lineage is not an MV geometry')
    p += lineage_problems(L, items, ctx, depth, 'geometry mv')
    return p, ['MV describes the geometry; the FINAL smearing stays Gaussian (A26)']


def final_run_problems(cert, items, label, need_width=None, need_a26=False):
    cands = [c for c in records(items, 'final_run', cell=cert.cell, geometry_sha256=cert.geometry)
             if bound_files(c.d.get('run_files')) == cert.run_files]
    Fr, err = one(cands, 'verified final_run record with this run\'s files and geometry')
    if Fr is None:
        return None, [f'{label}: {err} (exact run/geometry/settings linkage)']
    p, d = [], Fr.d
    key = F.final_template_key(d.get('settings') or {})          # v9 (Codex v8 item 4)
    if d.get('template_key') != key or key not in tuple(F.REGISTERED_FINAL_TEMPLATES.get(cert.cell, ()) or ()):
        p.append(f'{label}: the FINAL settings are not the registered FINAL template of {tok(cert.cell)} (cutoffs, '
                 'k-mesh, spin, SCF and every other setting apart from the width; no template registered = no '
                 'positive FINAL)')
    if d.get('upf_sha256') != cert.pps:
        p.append(f'{label}: final_run UPF hashes differ from the certificate (UPF identity)')
    if family(d.get('smearing')) != 'gaussian':
        p.append(f'{label}: the FINAL is not Gaussian (A15/A26 FINALs are Gaussian)')
    if need_width is not None and not same_w(d.get('degauss_Ry'), need_width):
        p.append(f'{label}: FINAL width {wfmt(d.get("degauss_Ry"))} Ry != certified width {wfmt(need_width)} Ry')
    if need_a26 and not same_w(d.get('degauss_Ry'), C3_REFERENCE_WIDTH_RY):
        p.append(f'{label}: a reused FINAL must be the A26 Gaussian 0.001 Ry reference')
    return Fr, p


def sem_geometry_polished(cert, items, ctx, depth):
    p, notes = [], []
    if cert.cell in NEVER_POLISHED:
        p.append(f'geometry polished: {cert.cell} has no MV-converged parent and can never be polished (A36/A37)')
    elif cert.cell not in POLISH_CELLS:
        p.append(f'geometry polished: C4 is defined only for {POLISH_CELLS}')
    P, err = one(records(items, 'c4_polish', cell=cert.cell), 'verified c4_polish record for this cell')
    if P is None:
        return p + [f'geometry polished: {err}'], notes
    PC, e = ctx.ref(P, 'parent_certificate', 'geometry polished: MV parent certificate')
    parent = None
    if PC is None:
        p.append(e + ' (missing MV-parent lineage)')
    elif PC.kind != 'certificate':
        p.append('geometry polished: the MV parent reference is not a certificate')
    else:
        parent = Cert(PC.path, PC.obj, PC.sha256)
        if parent.cell != cert.cell:
            p.append('geometry polished: the MV parent certificate is for another cell')
        r = evaluate(PC.path, ctx, depth + 1)
        rel, geo = r['blocks'].get('relaxation', {}), r['blocks'].get('geometry', {})
        if rel.get('claimed') != 'converged' or rel.get('verdict') != 'OK':
            sub = '; '.join(rel.get('reasons', [])[:4]) or f'claimed {rel.get("claimed")}'
            p.append(f'geometry polished: MV parent relaxation not certified converged ({sub})')
        if geo.get('claimed') != 'mv' or geo.get('verdict') != 'OK':
            sub = '; '.join(geo.get('reasons', [])[:4]) or f'claimed {geo.get("claimed")}'
            p.append(f'geometry polished: MV parent geometry not a certified MV geometry ({sub})')
    PL, e = ctx.ref(P, 'polish_lineage', 'geometry polished: polish lineage')
    Q, eq = ctx.ref(P, 'qualification', 'geometry polished: polish qualification')
    if Q is None:
        p.append(eq + ' (fresh final-geometry qualification required for every C4 polish, zero-step included)')
    if PL is None or PL.rtype != 'relaxation_lineage':
        p.append(e or 'geometry polished: polish lineage is not a relaxation_lineage record')
        return p, notes
    if PL.d.get('cell') != cert.cell or PL.d.get('route') != 'C4-polish':
        p.append('geometry polished: polish lineage is for another cell or not on the C4-polish route')
    hist = PL.d.get('smearing_history') or []
    if not hist or any(family(h.get('smearing')) != 'gaussian' or not same_w(h.get('degauss_Ry'), POLISH_WIDTH_RY)
                       for h in hist if isinstance(h, dict)):
        p.append('geometry polished: the polish is not a Gaussian 0.005 Ry relaxation (A27 C4)')
    if PC is not None and src_sha(PL, 'parent') not in (None, PC.sha256):
        p.append('geometry polished: polish lineage and C4 record name different MV parents')
    if parent is not None and PL.d.get('start_geometry_sha256') != parent.geometry:
        p.append('geometry polished: the polish did not start from the MV parent geometry')
    if PL.d.get('final_geometry_sha256') != cert.geometry:
        p.append('geometry polished: the polish final geometry is not the certified geometry')
    p += lineage_problems(PL, [Q] if Q is not None else [], ctx, depth, 'polish')
    zero = P.d.get('zero_step') is True
    Fr, fp = final_run_problems(cert, items, 'geometry polished', need_a26=zero)
    p += fp
    reuse = P.d.get('zero_step_reuse')
    if zero:
        notes.append('zero-step polish: the existing A26 FINAL is reused as the polished reference (A40 rule 4)')
        if parent is not None and cert.geometry != parent.geometry:
            p.append('geometry polished: zero-step polish but the certified geometry differs from the MV parent')
        if not isinstance(reuse, dict):
            p.append('geometry polished: zero-step polish without newly bound reuse evidence')
        else:
            if bound_files(reuse.get('run_files')) != cert.run_files:
                p.append('geometry polished: zero-step reuse names other run files (exact run identity)')
            if reuse.get('upf_sha256') != cert.pps:
                p.append('geometry polished: zero-step reuse UPF hashes differ (UPF identity)')
            if Fr is not None and reuse.get('final_settings_sha256') != Fr.d.get('settings_sha256'):
                p.append('geometry polished: zero-step reuse settings differ from the reused FINAL (settings identity)')
    elif parent is not None and cert.geometry == parent.geometry:
        p.append('geometry polished: polish moved per its lineage but the certified geometry equals the MV parent')
    return p, notes


def a15_problems(items, ctx):
    """v4 (Codex item 5): the roles are DERIVED by the writer from bound relaxation_lineage status records at the
    cutoff (A31(f): s1 if converged, else the named backup if converged, else unresolved); nothing is copied."""
    A, err = one(records(items, 'a15_provisional'), 'verified a15_provisional (A31(d)) record')
    if A is None:
        return None, [f'smearing qualified: {err}; C3 reports alone never qualify']
    d, p = A.d, []
    roles = d.get('roles')
    if not isinstance(roles, dict) or set(roles) != set(A15_ROLES):
        return None, ['smearing qualified: A15 roles must name exactly aIO, aIWO and compensated']
    for role, name in roles.items():
        if name is None:
            p.append(f'smearing qualified: A15 role {role} unresolved: primary not relaxation-converged at the cutoff '
                     'and no converged named backup (A31(f))')
        elif name not in A15_ROLES[role]:
            p.append(f'smearing qualified: A15 role {role} names {tok(name)}, not one of {A15_ROLES[role]}')
    ws = d.get('widths_Ry') or []
    if len(ws) != 3 or not all(any(same_w(w, a) for w in ws) for a in AUDIT_WIDTHS_RY):
        p.append('smearing qualified: A15 widths must be exactly 0.005, 0.002 and 0.001 Ry')
    cand = d.get('provisional_width_candidate_Ry')
    if not any(same_w(cand, w) for w in C3_PENDING_WIDTHS_RY):
        p.append('smearing qualified: A15 provisional candidate null or not one of 0.002 / 0.005 Ry')
    if d.get('status') != A15_STATUS:
        p.append(f'smearing qualified: A15 record status must be {A15_STATUS!r}')
    if d.get('audit_kind') != 'A15 smearing audit' or d.get('audit_code_sha256') != RC7_CODE_SHA256 or \
            d.get('audit_sealed') is not True:
        p.append('smearing qualified: the audit report is not a sealed rc7 A15 smearing audit')
    if all(isinstance(n, str) for n in roles.values()):
        want = sorted([n, round(w, 9)] for n in roles.values() for w in AUDIT_WIDTHS_RY)
        if sorted(d.get('audit_inputs') or []) != want or d.get('audit_n_inputs') != len(want):
            p.append('smearing qualified: the audit inputs are not exactly the derived roles at the three widths')
    return cand, p


def c3_inventory(cert, items, ctx):
    """v4 (Codex item 4): the C3 reports of every attempt of every frozen-plan slot at this cell AND geometry, from
    the verified readout_manifest record (plan + one user log per slot + reports, all accounted for)."""
    M, err = one(records(items, 'readout_manifest'), 'verified readout_manifest (complete C3 inventory) record')
    if M is None:
        return None, [f'smearing qualified: {err}']
    p, applicable = [], []
    by_sha = {}
    for r in (M.get('sources') or {}).get('c3_reports') or []:
        by_sha[r.get('sha256')] = r['file'] if os.path.isabs(r['file']) else \
            os.path.join(os.path.dirname(M.path), r['file'])
    for s in M.d.get('slots') or []:
        if s.get('cell') != cert.cell or s.get('geometry_sha256') != cert.geometry:
            continue
        # v7 (blocking-scope ruling): an unresolved slot blocks the claims of its own frozen cell / geometry
        if s.get('status') != 'resolved':
            why = '; '.join(tok(x) for x in s.get('reasons') or []) or 'no reason recorded'
            p.append(f'smearing qualified: C3 inventory UNRESOLVED for slot {tok(s.get("slot"))} at this geometry '
                     f'({why})')
        for a in s.get('attempts') or []:
            cl = a.get('cluster') if isinstance(a.get('cluster'), int) else '<invalid>'
            if a.get('result') == 'no_output':
                # v6 (Codex 2026-10-13 blocking 1), defence in depth: the frozen writer already refuses this
                inv = a.get('artifact_inventory')
                if not isinstance(inv, dict) or not is_hex64(inv.get('sha256')) or inv.get('n_exported_files') != 0:
                    p.append(f'smearing qualified: C3 inventory UNRESOLVED: attempt {cl} has no output and no verified '
                             'artifact inventory showing that no export exists')
                continue
            if a.get('result') == 'unresolved':
                p.append(f'smearing qualified: C3 inventory UNRESOLVED: attempt {cl} ({tok(a.get("reason"))})')
                continue
            if a.get('result') != 'report' or a.get('report_sha256') not in by_sha:
                p.append(f'smearing qualified: C3 inventory UNRESOLVED: attempt {cl} has no recognised result')
                continue
            # reports of an unresolved slot are still applied: a FAIL vetoes whatever else is open (Codex ruling)
            it = ctx.load(by_sha[a.get('report_sha256')])
            if it.kind != 'rc7' or it.get('kind') != 'C3' or \
                    (it.get('provenance') or {}).get('code_sha256') != RC7_CODE_SHA256 or not verify_seal(it.obj):
                p.append(f'smearing qualified: inventory entry {it.name} is not a sealed rc7 C3 report')
                continue
            applicable.append(it)
    return applicable, p


def sem_smearing_qualified(cert, items, ctx, depth):
    p, notes = [], []
    w = num(cert.width)
    if w is None:
        return ['smearing qualified: no numeric width_Ry'], notes
    _, fp = final_run_problems(cert, items, 'smearing qualified', need_width=w)
    p += fp
    cand, ap = a15_problems(items, ctx)
    p += ap
    applicable, ip = c3_inventory(cert, items, ctx)
    p += ip
    if applicable is None:
        return p, notes
    comps = records(items, 'c3_companion_run', cell=cert.cell, geometry_sha256=cert.geometry)

    def fresh(ref_files, run_files, width):
        """v5 (Codex 20:44Z item 3): BOTH endpoints must be fresh starts. The companion record (re-derived from the
        as-run inputs of both runs) must name exactly this report's reference run and compared run."""
        cs = [c for c in comps if bound_files(c.d.get('run_files')) == bound_files(run_files) and
              bound_files(c.d.get('reference_run_files')) == bound_files(ref_files) and
              same_w(c.d.get('degauss_Ry'), width)]
        C, _ = one(cs, 'companion')
        if C is None:
            return 'no companion run record for this reference and compared run'
        if (C.d.get('diff_gate') or {}).get('status') != 'PASS':
            return 'diff gate not PASS'
        if C.d.get('reference_start_mode') != 'fresh':
            return f'reference {tok(C.d.get("reference_start_mode"))}'
        return 'fresh' if C.d.get('start_mode') == 'fresh' else f'companion {tok(C.d.get("start_mode"))}'
    preds = {it.sha256 for it in items if it.kind == 'certificate' and it.get('cell') == cert.cell and
             bound_files(it.get('run_files')) == cert.run_files and it.get('geometry_sha256') == cert.geometry}
    preds.add(cert.sha256)
    as_ref, as_cmp = set(), set()
    for it in applicable:
        ref, oth = it.get('provenance')['inputs'][:2]
        wo = next((x for x in AUDIT_WIDTHS_RY if same_w(oth.get('degauss_Ry'), x)), None)
        st = it.get('status')
        if st == 'FAIL':
            p.append(f'smearing qualified: failed cell-specific C3 check at {wfmt(wo)} Ry on this geometry '
                     f'({it.name}); A31(e): a wider width never bypasses it')
            continue
        if st != 'PASS' or wo is None or not same_w(ref.get('degauss_Ry'), C3_REFERENCE_WIDTH_RY):
            notes.append(f'C3 {it.name}: {tok(st)} (not counted)')
            continue
        mode = fresh(ref.get('run_files'), oth.get('run_files'), wo)
        if mode != 'fresh':
            notes.append(f'C3 {wfmt(wo)} Ry: PASS ({mode}; reported, not counted, A40)')
            continue
        if bound_files(ref.get('run_files')) == cert.run_files and ref.get('certificate_sha256') in preds:
            as_ref.add(wo)
        if bound_files(oth.get('run_files')) == cert.run_files:
            as_cmp.add(wo)
    if cand is not None and not ap and same_w(w, cand):
        if not any(same_w(x, cand) for x in as_cmp):
            p.append(f'smearing qualified: no fresh C3 PASS with this run as the compared {wfmt(cand)} Ry width '
                     'against the 0.001 Ry reference at this geometry (A27 C3, A31(e))')
        else:
            notes.append('width = A15 provisional candidate; fresh C3 PASS against 0.001 Ry at this geometry')
    elif same_w(w, C3_REFERENCE_WIDTH_RY):
        missing = [x for x in C3_PENDING_WIDTHS_RY if not any(same_w(x, y) for y in as_ref)]
        if missing:
            p.append(f'smearing qualified: C3 coverage missing at {[wfmt(x) for x in missing]} Ry (fresh-start PASS '
                     'with this run as the 0.001 Ry reference at this geometry required, A31(e)/A40)')
    elif cand is not None:
        p.append(f'smearing qualified: width {wfmt(w)} Ry is neither the A15 candidate nor the A26 0.001 Ry width')
    if not p:
        notes.append(f'A15 width {A15_STATUS}')
    return p, notes


SEMANTIC = {('relaxation', 'converged'): sem_relaxation_converged,
            ('relaxation', 'exploratory'): sem_relaxation_exploratory,
            ('geometry', 'mv'): sem_geometry_mv,
            ('geometry', 'polished'): sem_geometry_polished,
            ('smearing', 'qualified'): sem_smearing_qualified}
DEFAULTS = {'relaxation': 'unknown', 'smearing': 'pending', 'geometry': 'unknown'}
POSITIVE = {'relaxation': ('converged', 'exploratory'), 'smearing': ('qualified',), 'geometry': ('polished', 'mv')}


def permitted(key, claimed, ok, items, cert):
    if ok:
        return claimed
    if key == 'relaxation' and claimed == 'converged':
        return 'exploratory' if records(items, 'relaxation_lineage', cell=cert.cell,
                                        final_geometry_sha256=cert.geometry) else 'unknown'
    return DEFAULTS[key]


# ---------------------------------------------------------------- evaluation
def evaluate(cert_path, ctx, depth=0):
    cert_path = os.path.abspath(cert_path)
    if cert_path in ctx.cert_results:
        return ctx.cert_results[cert_path]
    ctx.cert_results[cert_path] = {'cell': None, 'blocks': {}, 'structure_problems': ['cyclic certificate chain']}
    it = ctx.load(cert_path)
    out = {'certificate': it.name, 'certificate_sha256': it.sha256, 'cell': None, 'blocks': {},
           'structure_problems': []}
    if it.kind != 'certificate':
        out['structure_problems'].append(f'not a {CERT_SCHEMA} certificate')
        ctx.cert_results[cert_path] = out
        return out
    cert = Cert(cert_path, it.obj, it.sha256)
    out['cell'] = tok(cert.cell)
    sp = cert.structure_problems()
    out['structure_problems'] = sp
    if sp:
        ctx.cert_results[cert_path] = out
        return out
    for key in ('relaxation', 'smearing', 'geometry'):
        b = cert.obj.get(key) or {}
        claimed = b.get('status', DEFAULTS[key])
        blk = {'claimed': tok(claimed), 'hash_binding': 'N/A', 'semantic': 'N/A', 'verdict': 'OK',
               'permitted': DEFAULTS[key], 'reasons': [], 'notes': []}
        if claimed == DEFAULTS[key]:
            out['blocks'][key] = blk
            continue
        if claimed not in POSITIVE[key]:
            out['structure_problems'].append(f'{key} status not one of {POSITIVE[key] + (DEFAULTS[key],)}')
            blk['verdict'] = 'MALFORMED'
            out['blocks'][key] = blk
            continue
        items, hp = bind(b, cert, ctx)
        blk['hash_binding'] = 'OK' if not hp else 'FAIL'
        rp = record_problems(items, ctx)
        sem, notes = SEMANTIC[(key, claimed)](cert, items, ctx, depth)
        sem = rp + sem
        blk['semantic'] = 'OK' if not sem else 'FAIL'
        blk['reasons'] = hp + sem
        blk['notes'] = notes
        ok = not hp and not sem
        blk['verdict'] = 'OK' if ok else 'DOWNGRADE'
        blk['permitted'] = permitted(key, claimed, ok, items, cert)
        out['blocks'][key] = blk
    ctx.cert_results[cert_path] = out
    return out


def stale_reports(cert_path, report_paths, ctx):
    it = ctx.load(cert_path)
    cert = it.obj if it.kind == 'certificate' else {}
    files = bound_files(cert.get('run_files'))
    out = []
    for rp in report_paths:
        r = ctx.load(rp)
        entry = {'file': r.name, 'sha256': r.sha256, 'status': 'NOT_BOUND'}
        if r.kind != 'rc7':
            entry['status'] = 'NOT_AN_RC7_RECORD'
            out.append(entry)
            continue
        o = r.obj
        if o.get('schema') == CELL_SCHEMA:
            pf = (o.get('provenance') or {}).get('files') or {}
            ents = [{'cell': o.get('cell'), 'geometry_sha256': o.get('geometry_sha256'),
                     'run_files': {k: v.get('sha256') for k, v in pf.items() if isinstance(v, dict)},
                     'certificate_sha256': (o.get('run_qualification') or {}).get('certificate_sha256')}]
        else:
            ents = [e for e in ((o.get('provenance') or {}).get('inputs') or []) if isinstance(e, dict)]
        mine = [e for e in ents if e.get('cell') == cert.get('cell') and
                e.get('geometry_sha256') == cert.get('geometry_sha256') and bound_files(e.get('run_files')) == files]
        if mine:
            entry['status'] = 'CURRENT' if all(e.get('certificate_sha256') == it.sha256 for e in mine) else 'STALE'
        out.append(entry)
    return out


def run(cert_path, ctx, report_paths=()):
    res = {'checker': VERSION, 'checker_sha256': sha256_file(os.path.abspath(__file__)),
           'writer_sha256': W.writer_fingerprint(), 'cutoff_utc': fmt_utc(ctx.cutoff),
           'qualification_deadline_utc': fmt_utc(ctx.qual_deadline), 'extension': ctx.extension, 'notes': []}
    try:
        r = evaluate(cert_path, ctx)
        res.update({k: r.get(k) for k in ('certificate', 'certificate_sha256', 'cell', 'blocks',
                                          'structure_problems')})
        res['stale_reports'] = stale_reports(cert_path, report_paths, ctx) if report_paths else []
    except SightAbort as e:
        return {'checker': VERSION, 'verdict': 'SIGHT_ABORT', 'exit_code': 2,
                'notes': [f'sight gate: {e}; nothing from the file is printed']}
    if res['structure_problems'] or any(b.get('verdict') == 'MALFORMED' for b in res['blocks'].values()):
        res['verdict'], res['exit_code'] = 'MALFORMED', 2
    elif any(b.get('verdict') != 'OK' for b in res['blocks'].values()) or \
            any(s['status'] == 'STALE' for s in res['stale_reports']):
        res['verdict'], res['exit_code'] = 'DOWNGRADE_REQUIRED', 1
    else:
        res['verdict'], res['exit_code'] = 'CLAIMS_OK', 0
    return res


def check_output_allowlist(res):
    bad = [k for k in res if k not in OUTPUT_KEYS]
    for b in (res.get('blocks') or {}).values():
        bad += [k for k in b if k not in BLOCK_KEYS]
    if bad:
        raise AssertionError(f'output keys outside the allowlist: {bad}')
    return res


def text_summary(res):
    lines = [VERSION, f'certificate {res.get("certificate")} ({short(res.get("certificate_sha256"))}) cell '
             f'{res.get("cell")}', f'cutoff {res.get("cutoff_utc")}; qualification deadline '
             f'{res.get("qualification_deadline_utc")} (frozen; extension: {(res.get("extension") or {}).get("applied")})']
    for p in res.get('structure_problems') or []:
        lines.append(f'  STRUCTURE: {p}')
    for k, b in (res.get('blocks') or {}).items():
        lines.append(f'  {k}: claimed {b["claimed"]}  hash {b["hash_binding"]}  semantic {b["semantic"]}  -> '
                     f'{b["verdict"]} (permitted: {b["permitted"]})')
        lines += [f'      - {x}' for x in b['reasons']]
        lines += [f'      . {x}' for x in b['notes']]
    for s in res.get('stale_reports') or []:
        lines.append(f'  report {s["file"]} ({short(s["sha256"])}): {s["status"]}')
    lines += [f'  note: {x}' for x in res.get('notes') or []]
    lines.append(f'VERDICT: {res.get("verdict")}')
    return '\n'.join(lines) + '\n'


def self_test():
    import unittest
    suite = unittest.defaultTestLoader.loadTestsFromName('test_cert_assert')
    r = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if r.wasSuccessful() else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description='D-42 F9 certificate assertions (standalone; not the frozen reader). '
                                             'Dates are frozen; only a verified cern_extension record shifts them.')
    ap.add_argument('certificate', nargs='?')
    ap.add_argument('--reports', nargs='*', default=[], help='cell records / comparison reports to check for staleness')
    ap.add_argument('--extension', help='F9 cern_extension record (A39(e)); verified by re-derivation')
    ap.add_argument('--json', help='write the result JSON here')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.certificate:
        ap.error('a certificate path is required')
    try:
        ctx = Ctx(extension=a.extension)
        res = run(a.certificate, ctx, a.reports)
    except SightAbort as e:
        res = {'checker': VERSION, 'verdict': 'SIGHT_ABORT', 'exit_code': 2,
               'notes': [f'sight gate: {e}; nothing from the file is printed']}
    except (Malformed, F.DeriveError, OSError) as e:
        res = {'checker': VERSION, 'verdict': 'MALFORMED', 'exit_code': 2, 'notes': [f'{type(e).__name__}: {e}']}
    check_output_allowlist(res)
    sys.stdout.write(text_summary(res))
    if a.json:
        with open(a.json, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(res, f, indent=1, sort_keys=True)
    return res['exit_code']


if __name__ == '__main__':
    sys.exit(main())
