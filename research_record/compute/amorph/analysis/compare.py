"""Read-outs that combine cells: H-N controls C1-C6 (A27), W-centred attribution, H-N outcome rules, H-G scoring,
H-H, H-I, H-K and the A15 audit. Inputs are sealed cell records written by report.cell_result() (JSON files).

rc3 rules (Codex reviews of rc1/rc2 + three adversarial probes):
  * every input must be a sealed 'cell/3' record of the CURRENT code (self-hash valid, normalised W-5d convention);
    run qualification is recomputed from its fields, never trusted from a stored list;
  * an item that applies but cannot be evaluated or bounded makes a comparison UNRESOLVED, never PASS / ROBUST;
    Delta_W comparisons need conclusive difference bounds;
  * each control verifies its prescribed construction and input roles (C3 widths, C6 starts, C5 functional chain,
    C2 dilution, C1 parent / three sites through the immutable atom map); malformed inputs give INVALID / NOT A PASS;
  * a control report binds to a series cell only through its prescribed input role with identical run files and
    certificate (never by geometry); reports of the wrong kind, of other code, or inline objects never count;
  * every output carries the provenance of its inputs (code, register, result, run-file, geometry and certificate
    hashes) and its own self-hash.

A27 quotes used here:
  C3: "Pass: the class is unchanged, edges move <= 0.05 eV, and fractions move <= 5 percentage points. Rule: comparing
      a result with itself is not a pass." "Comparison: the Gaussian 0.001 Ry reference FINAL (A26) against the width
      selected by the A15 audit, or 0.002 and 0.005 Ry if the audit is pending."
  C6: "nspin = 2 single points from two starts: localised (moment on W plus first shell) and delocalised (a small
      uniform moment) ... Pass: the class and the C3 tolerances hold for the lower-energy state."
  C5: "PAW-PBE -> NC-PBE -> HSE06, all at identical geometry and occupation width ... must agree within the C3
      tolerances first ... SG15 NC 80 Ry, ecutfock 160 Ry ... k-mesh of the production FINAL, q equals the k-mesh;
      Gamma with q = 1 only if NC-PBE at Gamma agrees with NC-PBE at the production mesh ... the class must agree
      between NC-PBE and HSE06; otherwise the result is functional-sensitive."
  C2: "a 2 x 1 lateral supercell of a C1 paired cell ... in one image, W is replaced by In and the traceable added O is
      removed ... Robust if: |Delta f_ext| <= 0.15, |Delta Delta_W| <= 0.15 eV, the class is unchanged, and N_eff is
      compared rather than PR_n."
  C1: "three paired cells, on interior In sites with CN >= 5 ... one W replaces one In, and one O is added in the W
      first shell ... the class at t must agree between the independent-quench aIWO_t and at least 2 of the 3 paired
      cells"; "Fewer than three eligible sites: C1 is UNRESOLVED."
  Attribution: "(i) the trapping states (n > N_v, PR_n <= 0.05) carry >= 30 % of their weight on W plus its
      first-shell O; (ii) the paired aIO parent has no localised state (PR_n <= 0.05) within +-0.10 eV carrying >= 30 %
      weight on the same non-W atoms."
"""
import math
import re

import numpy as np

from . import register as R
from .certify import code_fingerprint, gate_valid, json_safe, provenance_stamp, qualification_reasons, seal, verify_seal
from .geometry import Structure, regions
from .qeio import element_of
from .readout import PENDING

ORDER = {'DONOR': 0, 'PARTIAL': 1, 'ECB': 2}
GOOD = {'PASS', 'ROBUST'}
CELL_SCHEMA = 'iwo-amorph-analysis/cell/3'
GAMMA_MESH = [1, 1, 1, 0, 0, 0]


def _t(label):
    return float('inf') if label == 'bulk' else float(label)


def _finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _num(x):
    return float(x) if _finite(x) else None


# ---------------------------------------------------------------- input validation and identity
def input_problems(r):
    """Why a record may not enter a comparison (empty list: acceptable)."""
    if not isinstance(r, dict):
        return ['input is not a JSON object']
    name = r.get('cell')
    p = []
    if r.get('schema') != CELL_SCHEMA:
        p.append(f'{name}: schema {r.get("schema")!r} (expected {CELL_SCHEMA})')
    code = (r.get('provenance') or {}).get('code_sha256')
    if code != code_fingerprint():
        p.append(f'{name}: produced by other code ({str(code)[:12]}), not the current {code_fingerprint()[:12]}')
    if not verify_seal(r):
        p.append(f'{name}: self-hash invalid (edited, corrupted or unsealed record)')
    if (r.get('run_qualification') or {}).get('W5d_convention') != 'normalised':
        p.append(f'{name}: W-5d convention {(r.get("run_qualification") or {}).get("W5d_convention")!r} '
                 '(comparisons accept the normalised primary convention only)')
    return p


def _invalid(out, inputs, problems, status='INVALID'):
    out['status'] = status
    out['unresolved_checks'] = list(problems)
    return _stamp(out, [x for x in inputs if isinstance(x, dict)])


_DEMOTE = {'PASS', 'ROBUST', 'NOT ROBUST', 'FAIL', 'FAILED', 'SUPPORTED', 'W-CENTRED', 'HOST-TRAP-MEDIATED',
           'UNATTRIBUTED', 'CROSSOVER', 'NO CROSSOVER', 'SAMPLE-DEPENDENT', 'PARTIAL', 'REPORTED', 'FUNCTIONAL-SENSITIVE'}


def provenance_reasons(r):
    """rc6: certificate and method provenance of ONE input cell record (every control checks every input it consumes):
    a VALID certificate gate, bound pseudopotential hashes, a verified manifest, the register hash and a converged
    final SCF. Recomputed from the record's fields; reports (non-cell inputs) are checked by _report_problems."""
    if not isinstance(r, dict) or r.get('schema') != CELL_SCHEMA:
        return []
    q, name, out = _q(r), r.get('cell'), []
    if not gate_valid(q) or not q.get('certificate_sha256'):
        out.append(f'{name}: run certificate missing or NOT VALID')
    if q.get('pseudopotentials_bound') is not True or not isinstance(q.get('pseudopotentials'), dict):
        out.append(f'{name}: pseudopotential provenance not bound')
    if q.get('manifest_verified') is not True:
        out.append(f'{name}: composition manifest not verified')
    if q.get('register_missing') or ((r.get('provenance') or {}).get('register') or {}).get('sha256') is None:
        out.append(f'{name}: hypothesis register hash missing')
    if (r.get('run_settings') or {}).get('scf_converged') is not True:
        out.append(f'{name}: final SCF convergence not shown')
    return out


def _demote(out):
    for key in ('status', 'outcome'):
        if out.get(key) in _DEMOTE:
            out[key] = 'UNRESOLVED'
    for k, v in list(out.items()):
        if isinstance(v, dict):
            if v.get('status') in _DEMOTE:
                v['status'] = 'UNRESOLVED'
            elif v and all(isinstance(x, str) for x in v.values()):
                out[k] = {kk: ('UNRESOLVED' if x in _DEMOTE else x) for kk, x in v.items()}
    for k in ('provisional_width_candidate_Ry', 'bracket_nm', 'Delta_E_host_aligned_eV'):
        if k in out:
            out[k] = None


def _stamp(out, inputs):
    """Every control output ends here: input provenance of EVERY consumed cell record is checked (a failing input
    demotes every pass / fail verdict to UNRESOLVED), then the provenance stamp and the self-hash are written."""
    ins = [x for x in inputs if isinstance(x, dict)]
    reasons = [x for r in ins for x in provenance_reasons(r)]
    if reasons:
        key = 'unresolved_checks'
        out[key] = list(out.get(key) or []) + [f'input provenance: {x}' for x in reasons
                                               if f'input provenance: {x}' not in (out.get(key) or [])]
        _demote(out)
    out['provenance'] = provenance_stamp(ins)
    return seal(json_safe(out))


def qual_reasons(r, drop_smearing=False):
    """Run-qualification reasons recomputed from the record's qualification fields (a stored list is not trusted)."""
    q = r.get('run_qualification') or {}
    rs = qualification_reasons(q)
    if drop_smearing:
        rs = [x for x in rs if not x.startswith('smearing qualification pending')]
    return rs


def core_unresolved(r):
    """Unresolved checks of a cell other than its run qualification."""
    hn = r.get('H-N') or {}
    out = list(hn.get('core_unresolved_checks') or [])
    out += [x for x in r.get('section1_unresolved', []) if x not in out]
    if hn.get('class') in (None, 'N/A'):
        for k in ('host_edge', 'host_valence_edge'):
            out += [f'{k}: {x}' for x in (r.get(k) or {}).get('unresolved', [])]
    return out


def run_id(r):
    files = (r.get('provenance') or {}).get('files') or {}
    return tuple(sorted(v['sha256'] for v in files.values() if isinstance(v, dict) and 'sha256' in v))


def same_run(a, b):
    ia = run_id(a)
    return bool(ia) and ia == run_id(b)


def identity_matches(entry, r):
    """A provenance input entry denotes the record r: identical run files and certificate (certificate not None)."""
    if not isinstance(entry, dict) or not isinstance(r, dict):
        return False
    files = {k: v.get('sha256') for k, v in ((r.get('provenance') or {}).get('files') or {}).items() if isinstance(v, dict)}
    cert = (r.get('run_qualification') or {}).get('certificate_sha256')
    return bool(files) and entry.get('run_files') == files and cert is not None and entry.get('certificate_sha256') == cert


def duplicates(results):
    out = []
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            a, b = results[i], results[j]
            if same_run(a, b):
                out.append((a.get('cell'), b.get('cell'), 'same run files'))
            elif a.get('geometry_sha256') and a.get('geometry_sha256') == b.get('geometry_sha256'):
                out.append((a.get('cell'), b.get('cell'), 'same geometry'))
    return out


def _q(r):
    return r.get('run_qualification') or {}


def _gate_ok(r):
    """rc5: certified facts (kind, seed, construction, passivation, polish, relaxation) count only when the record's
    certificate gate is VALID (valid binding and no problem at all) and the manifest is composition-verified."""
    q = _q(r)
    return gate_valid(q) and q.get('manifest_verified') is True


def certified_kind(r):
    return (_q(r).get('manifest') or {}).get('kind') if _gate_ok(r) else None


def certified_seed(r):
    return _q(r).get('seed') if _gate_ok(r) else None


def construction(r):
    c = (_q(r).get('manifest') or {}).get('construction') if _gate_ok(r) else None
    return c if isinstance(c, dict) else None


def certified_geometry(r):
    return _q(r).get('geometry') if gate_valid(_q(r)) else None


def _known(*xs):
    """rc5: two missing values never count as equal; every compared value must be present."""
    return all(x is not None for x in xs)


def _mesh(m, n=6):
    """A known k / q grid: n integers, the first three positive (Monkhorst-Pack offsets 0 or 1); else None."""
    if not isinstance(m, (list, tuple)) or len(m) != n or not all(isinstance(x, int) and not isinstance(x, bool)
                                                                   for x in m):
        return None
    if any(x < 1 for x in m[:3]) or (n == 6 and any(x not in (0, 1) for x in m[3:])):
        return None
    return list(m)


def thickness(r):
    """'bulk' or 'a.b' from the certified spec name (manifest) or the cell name ('_<a>p<b>' pattern)."""
    for name in ((_q(r).get('manifest') or {}).get('spec_name'), r.get('cell')):
        if not isinstance(name, str):
            continue
        if 'bulk' in name:
            return 'bulk'
        m = re.search(r'_(\d+)p(\d+)(?:_|$)', name)
        if m:
            return f'{int(m.group(1))}.{m.group(2)}'
    return None


def width(r):
    rs = r.get('run_settings') or {}
    return (str(rs.get('smearing') or '').lower() or None), _num(rs.get('degauss_Ry'))


def _pseudo_map(r):
    """element -> (UPF file, certified content sha256 or None); None when one element uses two pseudopotentials."""
    q = r.get('run_qualification') or {}
    cert = q.get('pseudopotentials') if q.get('pseudopotentials_bound') is True else None
    cert = cert if isinstance(cert, dict) else {}
    out = {}
    for s in (r.get('run_settings') or {}).get('species', []):
        el = element_of(str(s.get('name', '')))
        f = s.get('pseudo_file')
        if not isinstance(f, str) or not f:
            return None                                  # unknown UPF: identity cannot be established
        ident = (f, cert.get(f) if isinstance(cert.get(f), str) else None)
        if el in out and out[el] != ident:
            return None                                  # one element, two pseudopotentials
        out[el] = ident
    return out


def same_pseudos(a, b):
    """UPF identity: certified content hashes when both runs carry them, else file names (such runs are unqualified,
    so they never reach PASS)."""
    pa, pb = _pseudo_map(a), _pseudo_map(b)
    if not pa or not pb or set(pa) != set(pb):
        return False
    for el in pa:
        (fa, ha), (fb, hb) = pa[el], pb[el]
        if ha is not None and hb is not None:
            if ha != hb:
                return False
        elif fa != fb:
            return False
    return True


def settings_diff(a, b, keys=('functional', 'ecutwfc_Ry', 'ecutrho_Ry', 'k_mesh', 'smearing', 'degauss_Ry', 'lsda'),
                  pseudos=True, hybrid=True, allow_none=()):
    sa, sb = a.get('run_settings') or {}, b.get('run_settings') or {}
    d = [f'{k}: {sa.get(k)} vs {sb.get(k)}' for k in keys if sa.get(k) != sb.get(k)]
    if pseudos and not same_pseudos(a, b):
        d.append('pseudopotentials differ (element -> certified UPF content hash, or file when uncertified)')
    if hybrid and sa.get('hybrid') != sb.get('hybrid'):
        d.append('hybrid settings differ')
    if any(sa.get(k) in (None, '') for k in keys if k not in allow_none) or \
            any(sb.get(k) in (None, '') for k in keys if k not in allow_none):        # rc5: missing never equal
        d.append('settings incomplete (cannot verify)')
    return d


def common_gauge(a, b):
    d = settings_diff(a, b, keys=('functional', 'ecutwfc_Ry', 'ecutrho_Ry', 'k_mesh', 'lsda'))
    if a.get('geometry_sha256') != b.get('geometry_sha256'):
        d.append('geometry differs')
    return not d, d


# ---------------------------------------------------------------- tolerance comparison (C3 tolerances)
def _diff_item(items, name, va, vb, tol, note=None):
    va, vb = _num(va), _num(vb)
    if va is None or vb is None:
        items.append({'quantity': name, 'reference': va, 'compared': vb, 'pass': None,
                      'note': note or 'not evaluable (missing, non-finite, unresolved or only bounded)'})
        return None
    p = R.le(abs(vb - va), tol)
    items.append({'quantity': name, 'reference': va, 'compared': vb, 'difference': vb - va, 'tolerance': tol,
                  'pass': p})
    return p


def _dw_bounds(r):
    d = (r.get('H-N') or {}).get('Delta_W') or {}
    b = d.get('bounds_eV')
    if isinstance(b, list) and len(b) == 2:
        lo, hi = _num(b[0]), _num(b[1])
        return lo, hi
    v = _num(d.get('value_eV'))
    return (v, v) if v is not None else (_num(d.get('lower_bound_eV')), None)


def _frac_bounds(r, f):
    """(lower, upper) of an excess fraction from the flagged-state bounds; the primary value must lie inside."""
    hn = r.get('H-N') or {}
    b = (hn.get('fractions') or {}).get(f + '_bounds')
    v = _num(hn.get(f))
    if not isinstance(b, list) or len(b) != 2 or v is None:
        return None, None
    lo, hi = _num(b[0]), _num(b[1])
    if lo is None or hi is None or not (R.le(lo, v) and R.le(v, hi)):
        return None, None
    return lo, hi


def _interval_item(items, name, ba, bb, tol):
    """Difference of two bounded quantities: conclusive PASS only if the whole difference interval lies within +-tol,
    conclusive FAIL only if it lies wholly outside."""
    (la, ha), (lb, hb) = ba, bb
    if None in (la, lb) or ha is None or hb is None:
        items.append({'quantity': name, 'reference_bounds': [la, ha], 'compared_bounds': [lb, hb], 'pass': None,
                      'note': 'difference unbounded (a value known only as a lower bound, or missing)'})
        return None
    dlo, dhi = lb - ha, hb - la
    if R.le(dhi, tol) and R.ge(dlo, -tol):
        p = True
    elif R.gt(dlo, tol) or R.lt(dhi, -tol):
        p = False
    else:
        p = None
    items.append({'quantity': name, 'reference_bounds': [la, ha], 'compared_bounds': [lb, hb],
                  'difference_bounds': [dlo, dhi], 'tolerance': tol, 'pass': p,
                  **({'note': 'difference bounds straddle the tolerance (flagged states)'} if p is None else {})})
    return p


def _efe(r):
    v = (r.get('H-N') or {}).get('E_F_minus_host_edge_eV') or r.get('E_F_minus_host_edge_eV')
    if not v or (r.get('host_edge') or {}).get('unresolved'):
        return None
    vals = [_num(x) for x in v]
    if None in vals or len(set(round(x, 9) for x in vals)) != 1:
        return None
    return vals[0]


def _gap(r):
    g = r.get('host_gap') or {}
    return _num(g.get('E_g_host_eV')) if g and not g.get('unresolved') else None


def tolerance_compare(a, b, kind, absolute_edges=False, drop_smearing=True):
    """C3-tolerance comparison (a = reference). Absolute edges are scored only when absolute_edges is set (the caller
    has verified a common gauge)."""
    out = {'kind': kind, 'items': [], 'unresolved_checks': []}
    if same_run(a, b):
        out['status'] = 'NOT A PASS'
        out['note'] = 'self-comparison (identical run files) is not a pass (A27 C3 rule)'
        return out
    for r, tag in ((a, 'reference'), (b, 'compared')):
        out['unresolved_checks'] += [f'{tag} ({r.get("cell")}): {x}' for x in core_unresolved(r)]
        out['unresolved_checks'] += [f'{tag} ({r.get("cell")}) qualification: {x}'
                                     for x in qual_reasons(r, drop_smearing=drop_smearing)]
    items = out['items']
    hna, hnb = a.get('H-N') or {}, b.get('H-N') or {}
    applies_hn = hna.get('class') != 'N/A' or hnb.get('class') != 'N/A'
    ok = []
    if applies_hn:
        ca, cb = hna.get('class_if_resolved'), hnb.get('class_if_resolved')
        p = None if (ca in (None, 'N/A') or cb in (None, 'N/A')) else ca == cb
        items.append({'quantity': 'class', 'reference': ca, 'compared': cb, 'pass': p})
        ok.append(p)
        ok.append(_interval_item(items, 'Delta_W (eV)', _dw_bounds(a), _dw_bounds(b), R.C3_EDGE_EV))
        for f in ('f_ext', 'f_locW', 'f_W5d'):
            ok.append(_interval_item(items, f, _frac_bounds(a, f), _frac_bounds(b, f), R.C3_FRACTION))
    ok.append(_diff_item(items, 'E_F - host edge (eV)', _efe(a), _efe(b), R.C3_EDGE_EV))
    ok.append(_diff_item(items, 'host gap (eV)', _gap(a), _gap(b), R.C3_EDGE_EV))
    if absolute_edges:
        for key, lab in (('host_edge', 'host edge (eV, absolute)'), ('host_valence_edge', 'host valence edge (eV, absolute)')):
            ea, eb = a.get(key) or {}, b.get(key) or {}
            ok.append(_diff_item(items, lab, None if ea.get('unresolved') else ea.get('E_eV'),
                                 None if eb.get('unresolved') else eb.get('E_eV'), R.C3_EDGE_EV))
    inputs_unresolved = bool(out['unresolved_checks'])
    if any(p is None for p in ok):
        out['unresolved_checks'].append('applicable comparison item(s) not evaluable: '
                                        + ', '.join(i['quantity'] for i in items if i['pass'] is None))
    failed = any(p is False for p in ok)
    passed = all(p is True for p in ok)
    out['conditional_status'] = 'PASS' if passed else ('FAIL' if failed else None)
    if failed and not inputs_unresolved:
        out['status'] = 'FAIL'
    elif out['unresolved_checks']:
        out['status'] = 'UNRESOLVED'
    else:
        out['status'] = 'PASS' if passed else 'FAIL'
    return out


def _is_gauss(fam):
    return fam in R.GAUSSIAN


def c3(ref, other, audit_width_Ry=None):
    """C3: the Gaussian 0.001 Ry reference FINAL against the audit-selected width (or 0.002 / 0.005 Ry while the A15
    audit is pending), at fixed geometry and otherwise identical settings. Roles: inputs[0] reference, inputs[1] other."""
    out = {'kind': 'C3', 'roles': ['reference', 'other']}
    bad = input_problems(ref) + input_problems(other)
    if bad:
        return _invalid(out, [ref, other], bad)
    if same_run(ref, other):
        return _invalid(out, [ref, other], ['self-comparison (identical run files) is not a pass'], 'NOT A PASS')
    (fr, wr), (fo, wo) = width(ref), width(other)
    p = []
    if not _is_gauss(fr) or wr is None or abs(wr - R.C3_REFERENCE_WIDTH_RY) > R.WIDTH_TOL_RY:
        p.append(f'reference must be the Gaussian {R.C3_REFERENCE_WIDTH_RY} Ry FINAL (got {fr} {wr})')
    allowed = [audit_width_Ry] if audit_width_Ry is not None else list(R.C3_PENDING_WIDTHS_RY)
    if not _is_gauss(fo) or wo is None or not any(abs(wo - w) <= R.WIDTH_TOL_RY for w in allowed):
        p.append(f'other run must be Gaussian at {allowed} Ry (got {fo} {wo})')
    if not _known(ref.get('geometry_sha256')) or ref.get('geometry_sha256') != other.get('geometry_sha256'):
        p.append('C3 compares widths at fixed geometry; the geometry hashes differ')
    d = settings_diff(ref, other, keys=('functional', 'ecutwfc_Ry', 'ecutrho_Ry', 'k_mesh', 'lsda'))
    if d:
        p.append('settings other than the width differ: ' + '; '.join(d))
    if p:
        return _invalid(out, [ref, other], p)
    t = tolerance_compare(ref, other, 'C3', absolute_edges=True)
    out.update({k: v for k, v in t.items() if k != 'kind'})
    out['widths_Ry'] = [wr, wo]
    return _stamp(out, [ref, other])


def c4(mv, polished):
    """C4: classes on both geometries are reported; the crossover must hold on the certified polished one."""
    out = {'kind': 'C4'}
    bad = input_problems(mv) + input_problems(polished)
    if bad:
        return _invalid(out, [mv, polished], bad)
    gp = certified_geometry(polished)
    out.update({'class_MV_geometry': (mv.get('H-N') or {}).get('class'),
                'class_polished': (polished.get('H-N') or {}).get('class'), 'polished_certified': gp == 'polished',
                'status': 'REPORTED' if gp == 'polished' else 'UNRESOLVED',
                'unresolved_checks': [] if gp == 'polished' else [f'polish not certified (geometry {gp})'],
                'note': 'A27 C4: classes reported for both geometries; outcomes use the certified polished one'})
    return _stamp(out, [mv, polished])


def _start_class(r):
    """'localised' (moments only on W and labels whose atoms are all first-shell O of W, W nonzero), 'delocalised'
    (equal nonzero |m| <= 0.2 on every species), else None."""
    sp = (r.get('run_settings') or {}).get('species', [])
    mags = {s.get('name'): _num(s.get('starting_magnetization')) or 0.0 for s in sp}
    if not mags or not any(mags.values()):
        return None
    vals = set(round(v, 10) for v in mags.values())
    if len(vals) == 1 and 0 < abs(next(iter(vals))) <= R.C6_DELOCALISED_MAX_MOMENT:
        return 'delocalised'
    st = r.get('structure') or {}
    labels, species = st.get('labels') or st.get('species') or [], st.get('species') or []
    try:
        S = Structure.from_json(st)
    except (KeyError, TypeError, ValueError):
        return None
    W = [i for i, e in enumerate(species) if e == 'W']
    shell = set()
    for w in W:
        o = np.array([j for j, e in enumerate(species) if e == 'O'])
        if o.size:
            shell.update(int(j) for j in o[R.le(S.distances_from(w, o), R.W_O_FIRST_SHELL_A)])
    on = [lab for lab, m in mags.items() if m]
    w_labels = {lab for lab in mags if element_of(lab) == 'W'}
    if not (w_labels & set(on)):
        return None
    for lab in on:
        if element_of(lab) == 'W':
            continue
        atoms = [i for i, x in enumerate(labels) if x == lab]
        if not atoms or not all(a in shell for a in atoms):
            return None
    return 'localised'


def c6(spin_a, spin_b, ref):
    """C6: one localised and one delocalised nspin = 2 XML-pair start at the reference's geometry and settings, all
    converged; the lower-energy one must keep the class and the C3 tolerances against the nspin = 1 reference.
    An energy difference below the resolution is UNRESOLVED unless both starts give the same class and both pass.
    Roles: inputs[0], inputs[1] spin starts, inputs[2] the nspin = 1 reference."""
    out = {'kind': 'C6', 'roles': ['spin start', 'spin start', 'reference'], 'unresolved_checks': []}
    bad = input_problems(spin_a) + input_problems(spin_b) + input_problems(ref)
    if bad:
        return _invalid(out, [spin_a, spin_b, ref], bad)
    for r, tag in ((spin_a, 'spin start A'), (spin_b, 'spin start B')):
        if (r.get('occupations') or {}).get('nspin') != 2 or (r.get('run_settings') or {}).get('lsda') is not True:
            bad.append(f'{tag} ({r.get("cell")}) is not an nspin = 2 run')
        if (r.get('provenance') or {}).get('source') != 'xml':
            bad.append(f'{tag} ({r.get("cell")}) is not from the XML pair (C6 is XML-only)')
    if (ref.get('occupations') or {}).get('nspin') != 1:
        bad.append(f'reference ({ref.get("cell")}) is not an nspin = 1 run')
    starts = [_start_class(spin_a), _start_class(spin_b)]
    out['start_classes'] = starts
    if sorted(str(s) for s in starts) != ['delocalised', 'localised']:
        bad.append(f'C6 needs one localised and one delocalised start (got {starts})')
    if same_run(spin_a, spin_b):
        bad.append('the two spin runs are the same run')
    geo = {r.get('geometry_sha256') for r in (spin_a, spin_b, ref)}
    if len(geo) != 1 or None in geo:
        bad.append('geometry differs between the three runs')
    for r in (spin_b, ref):
        d = settings_diff(spin_a, r, keys=('functional', 'ecutwfc_Ry', 'ecutrho_Ry', 'k_mesh', 'smearing', 'degauss_Ry'))
        if d:
            bad.append(f'settings of {r.get("cell")} differ from {spin_a.get("cell")}: ' + '; '.join(d))
    for r in (spin_a, spin_b, ref):
        if (r.get('run_settings') or {}).get('scf_converged') is not True:
            bad.append(f'{r.get("cell")}: SCF convergence not shown')
    ea, eb = _num(spin_a.get('total_energy_Ry')), _num(spin_b.get('total_energy_Ry'))
    if ea is None or eb is None:
        bad.append('total energy missing or non-finite for a spin run')
    if bad:
        return _invalid(out, [spin_a, spin_b, ref], bad)
    out.update({'E_spin_runs_Ry': [ea, eb], 'energy_resolution_Ry': R.C6_ENERGY_RESOLUTION_RY,
                'spin_minus_reference_Ry': None if _num(ref.get('total_energy_Ry')) is None
                else min(ea, eb) - ref['total_energy_Ry']})
    if abs(ea - eb) < R.C6_ENERGY_RESOLUTION_RY:
        ta = tolerance_compare(ref, spin_a, 'C6', absolute_edges=True)
        tb = tolerance_compare(ref, spin_b, 'C6', absolute_edges=True)
        out['below_resolution'] = True
        out['comparisons'] = {'start_A': ta, 'start_B': tb}
        same_cls = (spin_a.get('H-N') or {}).get('class_if_resolved') == (spin_b.get('H-N') or {}).get('class_if_resolved')
        if same_cls and ta['status'] == 'PASS' and tb['status'] == 'PASS':
            out['status'] = 'PASS'
        elif ta['status'] == 'FAIL' and tb['status'] == 'FAIL':
            out['status'] = 'FAIL'
        else:
            out['status'] = 'UNRESOLVED'
            out['unresolved_checks'].append(f'the two starts differ by {abs(ea - eb):.2e} Ry < resolution '
                                            f'{R.C6_ENERGY_RESOLUTION_RY} Ry and do not agree')
        return _stamp(out, [spin_a, spin_b, ref])
    low = spin_a if ea < eb else spin_b
    out['lower_energy_start'] = low.get('cell')
    out['lower_energy_start_class'] = starts[0] if low is spin_a else starts[1]
    t = tolerance_compare(ref, low, 'C6', absolute_edges=True)
    out.update({k: v for k, v in t.items() if k not in ('kind',)})
    return _stamp(out, [spin_a, spin_b, ref])


def c5(paw, nc, hse, nc_production=None):
    """C5 (A27): PAW-PBE -> NC-PBE -> HSE06 at identical geometry and width, nspin = 1; NC and HSE share the SG15
    pseudopotentials and the 80 Ry cutoff, HSE ecutfock 160 Ry; k-mesh = the PAW FINAL's with q = k, or Gamma with q = 1
    when an NC-PBE run at the production mesh (nc_production) qualifies Gamma. Roles: inputs[0] PAW, [1] NC, [2] HSE."""
    out = {'kind': 'C5', 'roles': ['PAW-PBE', 'NC-PBE', 'HSE06'] + (['NC-PBE production mesh'] if nc_production else []),
           'unresolved_checks': []}
    ins = [paw, nc, hse] + ([nc_production] if nc_production else [])
    bad = [p for r in ins for p in input_problems(r)]
    if bad:
        return _invalid(out, ins, bad)
    dup = duplicates([paw, nc, hse])
    if any(x[2] == 'same run files' for x in dup):
        bad.append(f'duplicate runs among PAW / NC / HSE: {dup}')
    S = {k: r.get('run_settings') or {} for k, r in (('paw', paw), ('nc', nc), ('hse', hse))}
    if S['paw'].get('paw') is not True:
        bad.append('PAW-PBE input is not a PAW run')
    for k in ('nc', 'hse'):
        if S[k].get('paw') is not False or S[k].get('uspp') is not False:
            bad.append(f'{k.upper()} input is not norm-conserving (paw/uspp flags)')
    for k in ('paw', 'nc'):
        if S[k].get('hybrid') or 'HSE' in str(S[k].get('functional', '')).upper():
            bad.append(f'{k.upper()} input carries hybrid settings')
        if str(S[k].get('functional', '')).upper() != 'PBE':
            bad.append(f'{k.upper()} functional {S[k].get("functional")!r} is not PBE')
    if str(S['hse'].get('functional', '')).strip().upper() != R.C5_HSE_INPUT_DFT or not S['hse'].get('hybrid'):
        bad.append(f'HSE06 input: input_dft {S["hse"].get("functional")!r} (registered {R.C5_HSE_INPUT_DFT!r}) or no '
                   'hybrid block')
    hyb_missing = []
    for key, want in (('exx_fraction', R.C5_EXX_FRACTION), ('screening_parameter', R.C5_SCREENING_BOHR)):
        v = _hyb_param(S['hse'], key)
        if v is None:
            hyb_missing.append(key)
        elif abs(v - want) > R.C5_HYB_TOL:
            bad.append(f'HSE06 {key} {v} (HSE06: {want})')
    for k in S:
        if S[k].get('lsda') is not False:
            bad.append(f'{k.upper()} input is not nspin = 1')
    if not same_pseudos(nc, hse):
        bad.append('NC-PBE and HSE06 pseudopotentials differ')
    if same_pseudos(paw, nc):
        bad.append('PAW-PBE and NC-PBE use the same pseudopotentials')
    for k in ('nc', 'hse'):
        if _num(S[k].get('ecutwfc_Ry')) is None or abs(S[k]['ecutwfc_Ry'] - R.C5_NC_ECUTWFC_RY) > 1e-6:
            bad.append(f'{k.upper()} ecutwfc {S[k].get("ecutwfc_Ry")} Ry (registered {R.C5_NC_ECUTWFC_RY} Ry)')
    if not _known(S['nc'].get('ecutrho_Ry')) or S['nc'].get('ecutrho_Ry') != S['hse'].get('ecutrho_Ry'):
        bad.append('NC-PBE and HSE06 ecutrho differ')
    if _num(S['hse'].get('ecutfock_Ry')) is None or abs(S['hse']['ecutfock_Ry'] - R.C5_ECUTFOCK_RY) > 1e-6:
        bad.append(f'HSE06 ecutfock {S["hse"].get("ecutfock_Ry")} Ry (registered {R.C5_ECUTFOCK_RY} Ry)')
    geo = {r.get('geometry_sha256') for r in (paw, nc, hse)}
    if len(geo) != 1 or None in geo:
        bad.append('geometry differs between PAW, NC-PBE and HSE06')
    if len({width(r) for r in (paw, nc, hse)}) != 1:
        bad.append('occupation family / width differ')
    kp, kn, kh = (_mesh(S[k].get('k_mesh')) for k in ('paw', 'nc', 'hse'))
    q = _mesh(S['hse'].get('q_mesh'), 3)
    unknown = [n for n, v in (('PAW k-mesh', kp), ('NC-PBE k-mesh', kn), ('HSE06 k-mesh', kh), ('HSE06 q-mesh', q))
               if v is None] + [f'{k.upper()} occupation width' for k, r in (('paw', paw), ('nc', nc), ('hse', hse))
                                if None in width(r)]
    if unknown and not bad:
        out['status'] = 'UNRESOLVED'
        out['unresolved_checks'].append(f'sampling / width not known (missing or invalid grids): {unknown}')
        return _stamp(out, ins)
    if unknown:
        return _invalid(out, ins, bad + [f'sampling / width not known: {unknown}'])
    if kn != kh:
        bad.append(f'NC-PBE and HSE06 k-meshes differ ({kn} vs {kh})')
    gamma_route = kn == GAMMA_MESH and kp != GAMMA_MESH
    if not gamma_route and kn != kp:
        bad.append(f'NC/HSE k-mesh {kn} is neither the PAW FINAL mesh {kp} nor the Gamma route')
    want_q = [1, 1, 1] if gamma_route else (list(kh[:3]) if isinstance(kh, list) else None)
    if q != want_q:
        bad.append(f'HSE06 q-mesh {q} (registered: q = k-mesh, or q = 1 at Gamma; expected {want_q})')
    if bad:
        return _invalid(out, ins, bad)
    if hyb_missing:
        out['status'] = 'UNRESOLVED'
        out['unresolved_checks'].append(f'HSE06 effective {hyb_missing} not recorded: the functional is not established')
        return _stamp(out, ins)
    if gamma_route:
        if nc_production is None:
            out['status'] = 'UNRESOLVED'
            out['unresolved_checks'].append('Gamma route: NC-PBE at the production mesh is required to qualify Gamma')
            return _stamp(out, ins)
        sp_ = nc_production.get('run_settings') or {}
        if sp_.get('k_mesh') != kp or settings_diff(nc, nc_production, keys=('functional', 'ecutwfc_Ry', 'ecutrho_Ry',
                                                                            'smearing', 'degauss_Ry', 'lsda')) or \
                nc_production.get('geometry_sha256') != nc.get('geometry_sha256'):
            return _invalid(out, ins, ['NC-PBE production-mesh run does not match NC-PBE at Gamma (mesh, settings or '
                                       'geometry)'])
        gq = tolerance_compare(nc_production, nc, 'C5 Gamma qualification (NC-PBE production mesh vs Gamma)',
                               absolute_edges=True)
        out['Gamma_qualification'] = gq
        if gq['status'] != 'PASS':
            out['status'] = 'UNRESOLVED' if gq['status'] == 'UNRESOLVED' else 'FAIL'
            out['note'] = 'Gamma not qualified against the production mesh'
            return _stamp(out, ins)
    pn = tolerance_compare(paw, nc, 'C5 PAW vs NC-PBE (relative quantities only)')
    out['PAW_vs_NC'] = pn
    cn, ch = (nc.get('H-N') or {}).get('class_if_resolved'), (hse.get('H-N') or {}).get('class_if_resolved')
    unres = [f'{r.get("cell")}: {x}' for r in (nc, hse) for x in core_unresolved(r) + qual_reasons(r, True)]
    out['class_NC_PBE'], out['class_HSE06'] = cn, ch
    if pn['status'] != 'PASS':
        out['status'] = pn['status'] if pn['status'] in ('UNRESOLVED', 'NOT A PASS') else 'FAIL'
        out['note'] = 'PAW and NC-PBE do not agree within the C3 tolerances: the HSE comparison is not reached'
        out['unresolved_checks'] = pn.get('unresolved_checks', [])
    elif unres or cn in (None, 'N/A') or ch in (None, 'N/A'):
        out['status'] = 'UNRESOLVED'
        out['unresolved_checks'] = unres or ['class missing']
    else:
        out['status'] = 'PASS' if cn == ch else 'FUNCTIONAL-SENSITIVE'
    return _stamp(out, ins)


def _hyb_param(S, key):
    """Effective hybrid parameter from the run settings (schema output/input dft hybrid block); None if absent."""
    v = S.get(key)
    if v is None and isinstance(S.get('hybrid'), dict):
        v = S['hybrid'].get(key)
        if isinstance(v, dict):
            v = v.get('text')
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _comp(r):
    return {k: int(v) for k, v in (r.get('composition') or {}).items()}


def _plus(a, b, k=1):
    out = dict(a)
    for e, n in b.items():
        out[e] = out.get(e, 0) + k * n
    return {e: n for e, n in out.items() if n}


def c2(full, diluted):
    """C2 (A27): full = a certified C1 paired cell; diluted = its 2 x 1 lateral supercell with one W -> In and the
    traceable added O removed (certified construction), identical settings. Roles: inputs[0] full, inputs[1] diluted."""
    out = {'kind': 'C2', 'roles': ['full (C1 paired cell)', 'diluted'], 'items': [], 'notes': []}
    bad = input_problems(full) + input_problems(diluted)
    if bad:
        return _invalid(out, [full, diluted], bad)
    if same_run(full, diluted) or full.get('geometry_sha256') == diluted.get('geometry_sha256'):
        return _invalid(out, [full, diluted], ['full and diluted are the same run or geometry'], 'NOT A PASS')
    cf, cd = construction(full), construction(diluted)
    if not cf or cf.get('type') != 'C1-paired':
        bad.append('full input is not a certified C1 paired cell (manifest construction type C1-paired)')
    if not cd or cd.get('type') != 'C2-diluted' or not _known(full.get('geometry_sha256')) or \
            cd.get('source_geometry_sha256') != full.get('geometry_sha256'):
        bad.append('diluted input is not a certified C2 dilution of the full cell (construction type C2-diluted, '
                   'source_geometry_sha256 = full geometry)')
    want = _plus(_plus(_comp(full), _comp(full)), {'In': 1, 'W': -1, 'O': -1})
    if _comp(diluted) != want:
        bad.append(f'composition {_comp(diluted)} != 2 x full + In - W - O {want}')
    try:
        A = np.array(full['structure']['cell_A'], dtype=float)
        B = np.array(diluted['structure']['cell_A'], dtype=float)
        dbl = [i for i in (0, 1) if np.allclose(B[i], 2 * A[i], atol=1e-3) and np.allclose(B[1 - i], A[1 - i], atol=1e-3)]
        if len(dbl) != 1 or not np.allclose(B[2], A[2], atol=1e-3):
            bad.append('diluted cell is not the 2 x 1 lateral supercell (one lateral vector doubled, c unchanged)')
        else:
            kf = (full.get('run_settings') or {}).get('k_mesh') or []
            kd = (diluted.get('run_settings') or {}).get('k_mesh') or []
            i = dbl[0]
            if len(kf) >= 3 and len(kd) >= 3 and (kd[i] != max(1, math.ceil(kf[i] / 2)) or kd[1 - i] != kf[1 - i]
                                                  or kd[2] != kf[2]):
                out['notes'].append(f'k-mesh {kd} not the folded mesh of {kf} along the doubled axis (flag)')
    except (KeyError, TypeError, ValueError):
        bad.append('structure cells missing')
    d = settings_diff(full, diluted, keys=('functional', 'ecutwfc_Ry', 'ecutrho_Ry', 'smearing', 'degauss_Ry', 'lsda'))
    if d:
        bad.append('settings differ: ' + '; '.join(d))
    if bad:
        return _invalid(out, [full, diluted], bad)
    out['unresolved_checks'] = [f'{r.get("cell")}: {x}' for r in (full, diluted)
                                for x in core_unresolved(r) + qual_reasons(r, True)]
    hf, hd = full.get('H-N') or {}, diluted.get('H-N') or {}
    ok = [_interval_item(out['items'], 'f_ext', _frac_bounds(full, 'f_ext'), _frac_bounds(diluted, 'f_ext'), R.C2_FEXT),
          _interval_item(out['items'], 'Delta_W (eV)', _dw_bounds(full), _dw_bounds(diluted), R.C2_DW_EV)]
    ca, cb = hf.get('class_if_resolved'), hd.get('class_if_resolved')
    p = None if (ca in (None, 'N/A') or cb in (None, 'N/A')) else ca == cb
    out['items'].append({'quantity': 'class', 'reference': ca, 'compared': cb, 'pass': p})
    ok.append(p)
    out['N_eff'] = {'full': [s['N_eff'] for s in hf.get('states_used', []) if s.get('role')],
                    'diluted': [s['N_eff'] for s in hd.get('states_used', []) if s.get('role')],
                    'note': 'N_eff = N PR_n is compared, not PR_n (PR_n halves when N doubles for fixed support)'}
    out['trapping_states_N_eff'] = {k: [s['N_eff'] for s in r['attribution_data']['trapping_states']]
                                    for k, r in (('full', full), ('diluted', diluted))}
    if any(x is None for x in ok):
        out['unresolved_checks'].append('applicable item(s) not evaluable or not conclusively bounded: '
                                        + ', '.join(i['quantity'] for i in out['items'] if i['pass'] is None))
    if any(x is False for x in ok) and not core_unresolved(full) and not core_unresolved(diluted) and \
            not any('qualification' in u or 'certificate' in u for u in out['unresolved_checks']):
        out['status'] = 'NOT ROBUST'
    else:
        out['status'] = 'UNRESOLVED' if out['unresolved_checks'] else ('ROBUST' if all(ok) else 'NOT ROBUST')
    out['note'] = 'C2 cannot certify complete image isolation (A27)'
    return _stamp(out, [full, diluted])


# ---------------------------------------------------------------- C1 and W-centred attribution
def check_atom_map(amap, paired, parent):
    """The immutable C1 atom map: {'paired_geometry_sha256', 'parent_geometry_sha256',
    'paired_to_parent': {paired atom (1-based): parent atom (1-based) or null}} from the C1 construction."""
    prob = []
    if not isinstance(amap, dict):
        return None, ['no C1 atom map (immutable atom IDs from the C1 construction are required)']
    if not _known(paired.get('geometry_sha256')) or amap.get('paired_geometry_sha256') != paired.get('geometry_sha256'):
        prob.append('atom map is for another paired geometry')
    if not _known(parent.get('geometry_sha256')) or amap.get('parent_geometry_sha256') != parent.get('geometry_sha256'):
        prob.append('atom map is for another parent geometry')
    try:
        m = {int(k): (None if v is None else int(v)) for k, v in (amap.get('paired_to_parent') or {}).items()}
    except (TypeError, ValueError):
        return None, prob + ['atom map entries are not integers']
    sp_c, sp_p = paired['structure']['species'], parent['structure']['species']
    if sorted(m) != list(range(1, len(sp_c) + 1)):
        prob.append('atom map does not list every paired atom')
    vals = [v for v in m.values() if v is not None]
    if sorted(vals) != list(range(1, len(sp_p) + 1)):
        prob.append('atom map is not a bijection onto the parent atoms')
    added = [k for k, v in m.items() if v is None]
    if len(added) != len(sp_c) - len(sp_p):
        prob.append(f'{len(added)} unmapped (added) atoms, cell sizes differ by {len(sp_c) - len(sp_p)}')
    for k, v in m.items():
        if v is None or not (1 <= k <= len(sp_c)) or not (1 <= v <= len(sp_p)):
            continue
        a, b = sp_c[k - 1], sp_p[v - 1]
        if a != b and (a, b) != ('W', 'In'):
            prob.append(f'atom {k}: {a} maps to parent {b}')
            break
    return (m if not prob else None), prob


def _interior_in_sites(parent):
    """1-based indices of interior In atoms of the parent with In-O coordination >= 5 (the C1 site rule)."""
    S = Structure.from_json(parent['structure'])
    masks, _ = regions(S, parent.get('mode') or 'slab')
    o = np.array([j for j, e in enumerate(S.species) if e == 'O'])
    out = set()
    for i, e in enumerate(S.species):
        if e == 'In' and masks['interior'][i] and o.size:
            if int(R.le(S.distances_from(i, o), R.IN_O_CN_CUT_A).sum()) >= R.C1_SITE_MIN_CN:
                out.add(i + 1)
    return out


def c1(main, paired, parent=None, atom_maps=None):
    """C1 agreement over exactly the three frozen paired constructions of the parent: each paired cell = parent with one
    interior CN >= 5 In -> W and one O added (immutable atom map), distinct sites, certified construction; the main
    (independent-quench) class and >= 2 of the 3 paired classes must agree.
    Roles: inputs[0] main, [1..3] paired cells, [4] parent."""
    paired = list(paired)
    out = {'kind': 'C1', 'roles': ['main', 'paired', 'paired', 'paired', 'parent'], 'n_paired': len(paired),
           'unresolved_checks': [], 'notes': []}
    ins = [main] + paired + ([parent] if parent is not None else [])
    bad = [p for r in ins for p in input_problems(r)]
    if bad:
        return _invalid(out, ins, bad)
    if len(paired) != R.C1_N_PAIRED:
        st = 'UNRESOLVED' if len(paired) < R.C1_N_PAIRED else 'INVALID'
        return _invalid(out, ins, [f'C1 needs exactly {R.C1_N_PAIRED} paired cells ({len(paired)} given)'], st)
    if parent is None or not isinstance(atom_maps, list) or len(atom_maps) != R.C1_N_PAIRED:
        return _invalid(out, ins, ['C1 needs the aIO parent and one immutable atom map per paired cell'])
    dup = duplicates(ins)
    if dup:
        bad.append(f'duplicate inputs: {dup}')
    t = thickness(main)
    if certified_kind(main) != 'W-doped':
        bad.append('main cell is not a certified W-doped cell')
    if certified_kind(parent) != 'undoped' or _comp(parent).get('W', 0):
        bad.append('parent is not a certified undoped (aIO) cell')
    if thickness(parent) != t:
        bad.append(f'parent thickness {thickness(parent)} != main {t}')
    try:
        sites_ok = _interior_in_sites(parent)
    except (KeyError, TypeError, ValueError) as e:
        sites_ok = set()
        bad.append(f'parent structure unusable: {e}')
    sites, ranks = [], []
    for k, (p, amap) in enumerate(zip(paired, atom_maps), 1):
        tag = f'paired {k} ({p.get("cell")})'
        if _comp(p) != _plus(_comp(parent), {'In': -1, 'W': 1, 'O': 1}):
            bad.append(f'{tag}: composition {_comp(p)} != parent + W - In + O')
        cons = construction(p)
        if not cons or cons.get('type') != 'C1-paired' or not _known(parent.get('geometry_sha256')) or \
                cons.get('parent_geometry_sha256') != parent.get('geometry_sha256'):
            bad.append(f'{tag}: not a certified C1 construction of this parent')
        else:
            sites.append(cons.get('site'))
            ranks.append(cons.get('draw_rank'))
        m, prob = check_atom_map(amap, p, parent)
        bad += [f'{tag}: {x}' for x in prob]
        if m is not None and cons:
            wi = [i + 1 for i, e in enumerate(p['structure']['species']) if e == 'W']
            if len(wi) != 1 or m.get(wi[0]) != cons.get('site'):
                bad.append(f'{tag}: the W atom does not map to the recorded parent site {cons.get("site")}')
        if cons and cons.get('site') not in sites_ok:
            bad.append(f'{tag}: site {cons.get("site")} is not an interior In of the parent with CN >= '
                       f'{R.C1_SITE_MIN_CN}')
        if p.get('geometry_sha256') == main.get('geometry_sha256') or \
                (certified_seed(p) is not None and certified_seed(p) == certified_seed(main)):
            bad.append(f'{tag}: same geometry or seed as the main cell')
        fp, fm = (p.get('run_settings') or {}).get('functional'), (main.get('run_settings') or {}).get('functional')
        if None in width(main) or width(p) != width(main) or not _known(fm) or fp != fm:
            bad.append(f'{tag}: width or functional differ from the main cell')
    if len(set(sites)) != len(sites):
        bad.append(f'paired sites are not distinct: {sites}')
    if bad:
        return _invalid(out, ins, bad)
    out['sites'] = sites
    out['draw_ranks'] = ranks
    qp = _q(parent)
    if not gate_valid(qp) or qp.get('relaxation') != 'converged':
        out['status'] = 'UNRESOLVED'
        out['unresolved_checks'] = [f'aIO parent relaxation not certified converged (certificate valid '
                                    f'{qp.get("certificate_valid")}, relaxation {qp.get("relaxation")}): the paired '
                                    'constructions rest on an unproven parent structure']
        return _stamp(out, ins)
    out['notes'].append('the seeded draw order (seed 2711) is recorded by the construction, not recomputed here')
    cm = (main.get('H-N') or {}).get('class')
    cls = [(p.get('H-N') or {}).get('class') for p in paired]
    out.update({'class_main': cm, 'classes_paired': cls})
    unres = [p.get('cell') for p in paired if (p.get('H-N') or {}).get('class') in (None, 'UNRESOLVED', 'N/A')]
    agree = sum(1 for c in cls if c == cm and c not in ('UNRESOLVED', 'N/A'))
    out['n_agree'] = agree
    if cm in (None, 'UNRESOLVED', 'N/A'):
        out['status'] = 'UNRESOLVED'
        out['unresolved_checks'] = ['main cell class not resolved']
    elif agree >= R.C1_MIN_AGREE:
        out['status'] = 'PASS'
    elif agree + len(unres) >= R.C1_MIN_AGREE:
        out['status'] = 'UNRESOLVED'
        out['unresolved_checks'] = [f'paired cells unresolved: {unres}']
    else:
        out['status'] = 'FAIL'
    return _stamp(out, ins)


def _bounded_ge(primary, lo, hi, thr):
    """>= thr decided only when the bounds agree with the primary value; None otherwise."""
    if lo is None or hi is None or primary is None:
        return None
    a, b, c = R.ge(lo, thr), R.ge(primary, thr), R.ge(hi, thr)
    return b if a == b == c else None


def attribution(paired, parent, atom_map=None):
    """A27 W-centred attribution of an ECB in a C1 paired cell against its aIO parent (bounded by completeness)."""
    out = {'kind': 'W-centred attribution', 'paired': paired.get('cell'), 'parent': parent.get('cell'),
           'energy_reference': 'OPERATIONAL comparison: energies relative to each cell host edge',
           'unresolved_checks': []}
    bad = input_problems(paired) + input_problems(parent)
    if bad:
        return _invalid(out, [paired, parent], bad)
    hn = paired.get('H-N') or {}
    if hn.get('class') != 'ECB':
        out['status'] = 'N/A' if hn.get('class_if_resolved') not in (None, 'ECB') else 'UNRESOLVED'
        out['note'] = 'attribution applies to a resolved ECB'
        if out['status'] == 'UNRESOLVED':
            out['unresolved_checks'] = list(hn.get('unresolved_checks', []))
        return _stamp(out, [paired, parent])
    ad, pd = paired['attribution_data'], parent['attribution_data']
    out['excluded_localised_occupation'] = ad.get('excluded_localised_occupation')
    out['unbounded_trap_membership'] = ad.get('unbounded_trap_membership')
    out['trapped_electrons_counted'] = ad.get('trapped_electrons_counted')
    unres = []
    if (ad.get('unbounded_trap_membership') or {}).get('n_states', 0):
        unres.append('flagged occupied states above N_v: trap membership cannot be bounded')
    traps = ad['trapping_states']
    if not traps:
        out['status'] = 'UNRESOLVED' if unres else 'UNATTRIBUTED'
        out['unresolved_checks'] = unres
        out['note'] = 'no trapping state (n > N_v, PR_n <= 0.05) with >= 0.01 e'
        return _stamp(out, [paired, parent])
    occ = np.array([t['electrons'] for t in traps])
    wsh = np.array([t['W_plus_first_shell_O'] for t in traps])
    b = np.array([t.get('W_plus_first_shell_O_bounds', [t['W_plus_first_shell_O']] * 2) for t in traps], dtype=float)
    agg = float((occ * wsh).sum() / occ.sum())
    agg_lo, agg_hi = float((occ * b[:, 0]).sum() / occ.sum()), float((occ * b[:, 1]).sum() / occ.sum())
    ci = _bounded_ge(agg, agg_lo, agg_hi, R.HN_ATTR_WEIGHT)
    out['criterion_i'] = {'occupation_weighted_W_plus_first_shell_O': agg, 'bounds': [agg_lo, agg_hi],
                          'per_state': wsh.tolist(), 'threshold': R.HN_ATTR_WEIGHT, 'pass': ci}
    if ci is None:
        unres.append('criterion (i) not conclusive within the completeness bounds')
    m, prob = check_atom_map(atom_map, paired, parent)
    out['atom_map_problems'] = prob
    unres += prob
    unres += [f'parent qualification: {x}' for x in qual_reasons(parent) + core_unresolved(parent)]
    ec_c, ec_p = (paired.get('host_edge') or {}).get('E_eV'), (parent.get('host_edge') or {}).get('E_eV')
    if _num(ec_c) is None or _num(ec_p) is None or not pd.get('host_edges_resolved'):
        unres.append('host edges unresolved in the paired cell or the parent')
    hits, maybe, need = [], [], []
    if not unres:
        lo_w, hi_w = pd['localised_states_window_eV']
        for t in traps:
            target = t['E_eV'] - ec_c + ec_p
            need.append([target - R.HN_ATTR_WINDOW_EV, target + R.HN_ATTR_WINDOW_EV])
            if target - R.HN_ATTR_WINDOW_EV < lo_w or target + R.HN_ATTR_WINDOW_EV > hi_w:
                unres.append(f'parent search window {lo_w:.3f}..{hi_w:.3f} eV does not cover {target:.3f} +- 0.10 eV')
            if any(abs(e - target) <= R.HN_ATTR_WINDOW_EV for e in pd.get('flagged_states_in_window_eV', [])):
                unres.append(f'flagged parent state(s) within +-0.10 eV of {target:.3f} eV: absence not assertable')
            mapped = lambda key: [m[a] - 1 for a in t.get(key, t['support_nonW_atoms']) if m.get(a) is not None]
            sup, sure = mapped('support_nonW_atoms'), mapped('support_nonW_atoms_sure')
            poss = mapped('support_nonW_atoms_possible')
            for ls in pd['localised_states']:
                if abs(ls['E_eV'] - target) > R.HN_ATTR_WINDOW_EV:
                    continue
                pvec = ls['p']
                w = float(sum(pvec[a] for a in sup))
                cp = min(float(ls.get('completeness', 1.0)), 1.0)
                # bounded by the parent completeness and by the support bounds of the child trap
                lo = float(sum(pvec[a] for a in sure)) * cp
                hi = min(1.0, float(sum(pvec[a] for a in poss)) * cp + max(0.0, 1.0 - cp))
                rec = {'trap_band': t['band'], 'trap_k': t['k'], 'parent_band': ls['band'], 'parent_k': ls['k'],
                       'dE_rel_host_edge_eV': ls['E_eV'] - target, 'weight_on_support': w, 'bounds': [lo, hi]}
                hit = _bounded_ge(w, lo, hi, R.HN_ATTR_WEIGHT)
                if hit is True:
                    hits.append(rec)
                elif hit is None:
                    maybe.append(rec)
    if maybe:
        unres.append('parent state(s) near the 30 % support threshold within the completeness bounds')
    out['criterion_ii'] = {'parent_states_matching': hits, 'parent_states_inconclusive': maybe,
                           'pass': (not hits) if not unres else None, 'window_eV': R.HN_ATTR_WINDOW_EV,
                           'parent_windows_needed_eV': need}
    out['unresolved_checks'] = unres
    if hits:
        out['status'] = 'HOST-TRAP-MEDIATED' if not [u for u in unres if 'atom map' in u or 'qualification' in u] \
            else 'UNRESOLVED'
    elif unres:
        out['status'] = 'UNRESOLVED'
    elif ci:
        out['status'] = 'W-CENTRED'
    else:
        out['status'] = 'UNATTRIBUTED'
    return _stamp(out, [paired, parent])


# ---------------------------------------------------------------- aIO pairing (H-N)
def _aligned(r):
    """The gated aligned host edge (released only for a valid alignment, edge, accounting and qualification)."""
    return _num((r.get('alignment') or {}).get('aligned_host_edge_eV'))


def _gate(r):
    a = r.get('alignment') or {}
    return '; '.join(a.get('gate') or a.get('unresolved') or ['aligned edge not released'])


def hn_pair(aiwo, aio):
    """A27 pairing: the aIO partner supplies the undoped host edge, its tail states at the same energies and
    Delta E_host(t) where the interior alignment is valid. Not part of the basic classification."""
    out = {'kind': 'H-N aIO pairing', 'aIWO': aiwo.get('cell'), 'aIO': aio.get('cell'),
           'energy_reference': 'OPERATIONAL comparison: energies relative to each cell host edge'}
    bad = input_problems(aiwo) + input_problems(aio)
    if bad:
        return _invalid(out, [aiwo, aio], bad)
    a, b = _aligned(aiwo), _aligned(aio)
    out['Delta_E_host_aligned_eV'] = (a - b) if a is not None and b is not None else None
    if out['Delta_E_host_aligned_eV'] is None:
        out['Delta_E_host_note'] = f'unresolved: {aiwo.get("cell")}: {_gate(aiwo)} | {aio.get("cell")}: {_gate(aio)}'
    out['host_edges_eV'] = [(aiwo.get('host_edge') or {}).get('E_eV'), (aio.get('host_edge') or {}).get('E_eV')]
    tails = []
    ec_w, ec_o = (_num(x) for x in out['host_edges_eV'])
    if ec_w is not None and ec_o is not None:
        for t in aiwo['attribution_data']['trapping_states']:
            for ls in aio['attribution_data']['localised_states']:
                de = (ls['E_eV'] - ec_o) - (t['E_eV'] - ec_w)
                if abs(de) <= R.HN_ATTR_WINDOW_EV:
                    tails.append({'aIWO_band': t['band'], 'aIWO_k': t['k'], 'aIO_band': ls['band'], 'aIO_k': ls['k'],
                                  'dE_rel_host_edge_eV': de, 'aIO_PR_n': ls['PR_n']})
    out['aIO_tail_states_at_trap_energies'] = tails
    return _stamp(out, [aiwo, aio])


# ---------------------------------------------------------------- A15 smearing audit
def _gap_trap_count(r):
    g = r.get('gap_states') or {}
    return None if g.get('unresolved') or 'n_qualifying' not in g else g['n_qualifying']


def smearing_audit(cells):
    """A15 audit at fixed geometry on the three registered 2.0 nm cells: cells = {cell: {width_Ry: result}} (the key must
    equal the run's own width). Roles from the certified manifests: one aIO (undoped), one aIWO (W-doped), one
    compensated. Each width is compared with the cell's 0.001 Ry result through c3 (geometry, settings, Gaussian).
    The electron affinity is NOT computed: the audit stays PARTIAL and exposes only a provisional width candidate."""
    out = {'kind': 'A15 smearing audit', 'status': 'PARTIAL', 'cells': {}, 'unresolved_checks': [],
           'not_implemented': ['EA (electron affinity) within 0.05 eV: not computed by this package'],
           'note': 'PARTIAL until EA, trap classes and charge checks pass across all three registered cells'}
    inputs = [r for by_w in cells.values() for r in by_w.values()]
    bad = [p for r in inputs for p in input_problems(r)]
    if bad:
        out['unresolved_checks'] = bad
        out['provisional_width_candidate_Ry'] = None
        return _stamp(out, [r for r in inputs if isinstance(r, dict)])
    roles = {}
    for name, by_w in cells.items():
        any_r = next(iter(by_w.values()), {})
        k = certified_kind(any_r)
        role = {'undoped': 'aIO', 'W-doped': 'aIWO', 'compensated': 'compensated'}.get(k)
        if thickness(any_r) != '2.0':
            out['unresolved_checks'].append(f'{name}: not a 2.0 nm cell')
        roles.setdefault(role, []).append(name)
    if sorted(r for r in roles if r) != ['aIO', 'aIWO', 'compensated'] or any(len(v) != 1 for v in roles.values()):
        out['unresolved_checks'].append(f'the audit needs exactly the three registered 2.0 nm roles (aIO, aIWO, '
                                        f'compensated); got {roles}')
    firsts = [next(iter(v.values())) for v in cells.values() if v]
    if duplicates(firsts):
        out['unresolved_checks'].append(f'duplicate cells: {duplicates(firsts)}')
    passing = None
    for name, by_w in cells.items():
        rec = {'widths_Ry': sorted(by_w), 'comparisons': {}}
        mism = [w for w, r in by_w.items() if width(r)[1] is None or abs(width(r)[1] - w) > R.WIDTH_TOL_RY]
        if mism:
            rec['problem'] = f'entries {mism} carry another run width'
            out['unresolved_checks'].append(f'{name}: width keys {mism} disagree with the runs')
        ref = by_w.get(R.C3_REFERENCE_WIDTH_RY)
        ok_w = set()
        if ref is None:
            rec['problem'] = 'no 0.001 Ry reference result'
            out['unresolved_checks'].append(f'{name}: no 0.001 Ry reference')
        else:
            for w, r in sorted(by_w.items(), reverse=True):
                if abs(w - R.C3_REFERENCE_WIDTH_RY) <= R.WIDTH_TOL_RY or w in mism:
                    continue
                cmp_ = c3(ref, r)
                ta, tb = _gap_trap_count(ref), _gap_trap_count(r)
                trap = {'gap_localised_states': [ta, tb], 'pass': None if None in (ta, tb) else ta == tb}
                rec['comparisons'][str(w)] = {'status': cmp_['status'], 'unresolved_checks':
                                              cmp_.get('unresolved_checks', []), 'items': cmp_.get('items', []),
                                              'trap_class': trap}
                if cmp_['status'] == 'PASS' and trap['pass'] is True:
                    ok_w.add(w)
        out['cells'][name] = rec
        passing = ok_w if passing is None else passing & ok_w
    clean = not out['unresolved_checks']
    out['provisional_width_candidate_Ry'] = max(passing) if (passing and clean) else None
    if not passing:
        out['unresolved_checks'].append('no width larger than 0.001 Ry passes in every cell (self-comparison is not '
                                        'a pass)')
    return _stamp(out, inputs)


# ---------------------------------------------------------------- H-N outcome rules
def _report_problems(rep, kind):
    if not isinstance(rep, dict):
        return [f'UNVERIFIED ({rep!r}: not a comparison report file)']
    p = []
    if rep.get('kind') != kind:
        p.append(f'UNVERIFIED (report kind {rep.get("kind")!r}, slot {kind})')
    if (rep.get('provenance') or {}).get('code_sha256') != code_fingerprint():
        p.append('UNVERIFIED (report produced by other code)')
    if not verify_seal(rep):
        p.append('UNVERIFIED (report self-hash invalid)')
    return p


def _role_inputs(rep):
    return (rep.get('provenance') or {}).get('inputs') or []


def _same_entry(a, b):
    if not isinstance(a, dict) or not isinstance(b, dict) or not a.get('run_files'):
        return False
    return a.get('run_files') == b.get('run_files') and a.get('certificate_sha256') is not None and \
        a.get('certificate_sha256') == b.get('certificate_sha256')


def _bound(rep, idx, cell):
    ins = _role_inputs(rep)
    return 0 <= idx < len(ins) and identity_matches(ins[idx], cell)


def control_status(kind, cell, reports, c1_reports=()):
    """Status of control `kind` for one series cell from a list of reports (C3 needs width coverage; C2 binds through a
    bound C1 report). Returns (status string, details)."""
    if not reports:
        return 'MISSING', []
    det, cand = [], []
    for rep in reports:
        prob = _report_problems(rep, kind)
        if prob:
            det.append('; '.join(prob))
            continue
        cand.append(rep)
    if not cand:
        return det[0], det
    if kind == 'C3':
        fam, w = width(cell)
        if w is not None and abs(w - R.C3_REFERENCE_WIDTH_RY) <= R.WIDTH_TOL_RY:
            bound = [r for r in cand if _bound(r, 0, cell)]
            covered = {round(_role_inputs(r)[1].get('degauss_Ry') or -1, 9) for r in bound if r.get('status') == 'PASS'}
            need = {round(x, 9) for x in R.C3_PENDING_WIDTHS_RY}
            if not bound:
                return 'UNVERIFIED (no C3 report with this cell as the 0.001 Ry reference)', det
            if not need <= covered:
                bad = [r.get('status') for r in bound if r.get('status') != 'PASS']
                return (bad[0] if bad else f'MISSING (C3 widths {sorted(need - covered)} Ry not covered by passing '
                        'reports)'), det
            return 'PASS', det
        bound = [r for r in cand if _bound(r, 1, cell)]
        if not bound:
            return 'UNVERIFIED (no C3 report with this cell as the compared width)', det
        q = _q(cell)
        if q.get('smearing_qualified') is not True or not gate_valid(q):
            return 'UNVERIFIED (cell width not certified as the audit-selected width)', det
        st = [r.get('status') for r in bound]
        return ('PASS' if 'PASS' in st else st[0]), det
    if kind == 'C2':
        # the full cell of the C2 report must be one of the three paired cells of a passing C1 report bound to
        # THIS cell (same run files and certificate)
        c1_here = [x for x in c1_reports if _bound(x, 0, cell)]
        paired_entries = [e for c1r in c1_here for e in _role_inputs(c1r)[1:4]]
        bound = [r for r in cand if _role_inputs(r) and any(_same_entry(_role_inputs(r)[0], e) for e in paired_entries)]
        if not bound:
            return 'UNVERIFIED (no C2 report whose full cell is a paired cell of the bound C1 report)', det
        st = [r.get('status') for r in bound]
        return ('ROBUST' if 'ROBUST' in st else st[0]), det
    idx = {'C6': 2, 'C1': 0, 'C5': 0}[kind]
    bound = [r for r in cand if _bound(r, idx, cell)]
    if not bound:
        return f'UNVERIFIED (no {kind} report with this cell in its prescribed role)', det
    st = [r.get('status') for r in bound]
    return ('PASS' if 'PASS' in st else st[0]), det


def hn_outcome(series):
    """series: {'cells': {label: result | [results]}, 'controls': {label: {kind: report | [reports]}}} with canonical
    labels 'bulk', '2.0', '1.5', '1.0', '0.8', '0.7'. Cells: sealed current-code records, certified W-doped, the label
    thickness in the certified name, bulk mode only in 'bulk', one common width, distinct certified 2.0 nm seeds, C4 =
    certified polish at 2.0 (both), 1.0 and 0.7 nm. Controls: comparison reports bound by role (control_status)."""
    cells, ctrl = series['cells'], series.get('controls', {})
    out = {'hypothesis': 'H-N outcome rules (A27)', 'classes': {}, 'notes': [], 'unresolved_checks': []}
    allres = [r for v in cells.values() for r in (v if isinstance(v, list) else [v])]
    reports = [rep for d in ctrl.values() for v in d.values() for rep in (v if isinstance(v, list) else [v])
               if isinstance(rep, dict)]
    bad = [p for r in allres for p in input_problems(r)]
    if bad:
        out['outcome'] = 'INVALID'
        out['unresolved_checks'] = bad
        return _stamp(out, [r for r in allres if isinstance(r, dict)] + reports)
    for lab in cells:
        if lab not in R.SERIES_LABELS:
            out['unresolved_checks'].append(f'label {lab!r} is not one of {R.SERIES_LABELS}')
    dup = duplicates(allres)
    if dup:
        out['unresolved_checks'].append(f'duplicate inputs: {dup}')

    def results(lab):
        v = cells.get(lab, [])
        return v if isinstance(v, list) else [v]

    for lab, v in cells.items():
        for r in results(lab):
            if thickness(r) != lab:
                out['unresolved_checks'].append(f'{r.get("cell")}: certified thickness {thickness(r)} does not match '
                                                f'the label {lab}')
            want_mode = 'bulk' if lab == 'bulk' else 'slab'
            if r.get('mode') != want_mode:
                out['unresolved_checks'].append(f'{r.get("cell")}: mode {r.get("mode")} in the {lab} slot')
            if certified_kind(r) != 'W-doped':
                out['unresolved_checks'].append(f'{r.get("cell")}: not a certified W-doped cell')
            if (r.get('H-N') or {}).get('class') in (None, 'N/A'):
                out['unresolved_checks'].append(f'{r.get("cell")}: H-N class N/A')
    widths = sorted({width(r) for r in allres}, key=str)
    out['widths'] = [list(w) for w in widths]
    if len(widths) > 1:
        out['unresolved_checks'].append(f'mixed occupation widths {widths}: A26 requires a common width (no automatic '
                                        'sensitivity link)')
    if any(None in w for w in widths):
        out['unresolved_checks'].append('occupation width unknown for some cell (a missing width is never common)')
    cls = {}
    for lab in cells:
        rs = results(lab)
        cls[lab] = [(r.get('H-N') or {}).get('class') for r in rs]
        out['classes'][lab] = [{'cell': r.get('cell'), 'class': (r.get('H-N') or {}).get('class'),
                                'class_if_resolved': (r.get('H-N') or {}).get('class_if_resolved'),
                                'geometry': _q(r).get('geometry'), 'seed': certified_seed(r),
                                'width': list(width(r)),
                                'unresolved_checks': (r.get('H-N') or {}).get('unresolved_checks', [])} for r in rs]
    thick_res = results(R.HN_THICK)
    thick = cls.get(R.HN_THICK, [])
    if len(thick) != 2:
        out['unresolved_checks'].append(f'thick endpoint needs both 2.0 nm seeds ({len(thick)} given)')
    else:
        seeds = [certified_seed(r) for r in thick_res]
        if None in seeds or seeds[0] == seeds[1]:
            out['unresolved_checks'].append(f'the two 2.0 nm cells are not certified distinct seeds (seeds {seeds})')
    sample_dep = len(thick) == 2 and thick[0] != thick[1] and 'UNRESOLVED' not in thick
    if sample_dep:
        out['notes'].append('the two 2.0 nm seeds disagree: sample-dependent, no crossover')

    def polished(lab):
        """C4: every cell of the slot on its certified Gaussian polish (geometry 'polished', Gaussian FINAL)."""
        rs = results(lab)
        return bool(rs) and all(certified_geometry(r) == 'polished' and _is_gauss(width(r)[0]) for r in rs)

    def as_list(v):
        return [] if v is None else (v if isinstance(v, list) else [v])

    def ctrl_ok(lab, crossover):
        need = list(R.HN_CONTROLS_REQUIRED.get(lab, ()))
        if crossover and lab == R.HN_THIN:
            need += list(R.HN_CONTROLS_REQUIRED[R.HN_THIN + '_crossover'])
        st = {}
        for c in need:
            if c == 'C4':
                st[c] = 'PASS' if polished(lab) else 'MISSING (certified Gaussian geometry polish absent)'
                continue
            reps = as_list(ctrl.get(lab, {}).get(c))
            c1r = [x for x in as_list(ctrl.get(lab, {}).get('C1')) if isinstance(x, dict) and not
                   _report_problems(x, 'C1') and x.get('status') == 'PASS' and
                   any(_bound(x, 0, cc) for cc in results(lab))]
            per = [control_status(c, cell, reps, c1r)[0] for cell in results(lab)] or ['MISSING (no cell)']
            st[c] = per[0] if len(set(per)) == 1 else f'{per} (per seed)'
        return all(s in GOOD for s in st.values()), st

    one = lambda lab: cls.get(lab, [None])[0] if len(cls.get(lab, [])) == 1 else None
    labs = sorted([l for l in cells if l != R.HN_THICK and l in R.SERIES_LABELS] + ([R.HN_THICK] if thick else []),
                  key=lambda l: -_t(l))
    seq = []
    for l in labs:
        c = (thick[0] if len(set(thick)) == 1 else None) if l == R.HN_THICK else one(l)
        seq.append((l, c))
    out['sequence'] = seq
    ranks = [(l, ORDER[c]) for l, c in seq if c in ORDER]
    reversal = any(b[1] < a[1] for a, b in zip(ranks, ranks[1:]))
    out['reversal'] = reversal
    donors = [l for l, c in seq if c == 'DONOR']
    ecbs = [l for l, c in seq if c == 'ECB']
    x_ok2, st2 = ctrl_ok(R.HN_THICK, True)
    x_ok7, st7 = ctrl_ok(R.HN_THIN, True)
    n_ok7, _ = ctrl_ok(R.HN_THIN, False)
    ok10, st10 = ctrl_ok('1.0', False)
    out['controls'] = {R.HN_THICK: st2, R.HN_THIN: st7, '1.0': st10}
    clean = not out['unresolved_checks']
    # rc7: register (IMPLEMENTATION_CHOICES['series']): C4 = certified Gaussian polish at 2.0 (both seeds), 1.0 and
    # 0.7 nm is required for CROSSOVER AND for NO CROSSOVER; a class pattern that would claim either without it is
    # UNRESOLVED with the missing polish named
    cross_classes = clean and (one('bulk') == 'DONOR' and len(thick) == 2 and all(c == 'DONOR' for c in thick)
                               and one(R.HN_THIN) == 'ECB')
    no_cross_classes = clean and all((thick == ['DONOR', 'DONOR']) if l == R.HN_THICK else one(l) == 'DONOR'
                                     for l in R.HN_NO_CROSSOVER_SET)
    pol = {lab: polished(lab) for lab in (R.HN_THICK, '1.0', R.HN_THIN)}
    pol_missing = [lab for lab, ok in pol.items() if not ok]
    if (cross_classes or no_cross_classes) and pol_missing:
        out['unresolved_checks'].append(
            f'C4: certified Gaussian polish missing at {pol_missing} nm (required at 2.0 nm for both seeds, 1.0 and '
            f'0.7 nm before {"CROSSOVER" if cross_classes else "NO CROSSOVER"} can be claimed)')
        clean = False
    crossover = cross_classes and clean and x_ok2 and x_ok7 and ok10 and all(pol.values())
    no_cross = no_cross_classes and clean and n_ok7 and ok10 and all(pol.values())
    if crossover:
        out['outcome'] = 'CROSSOVER'
        if reversal:
            out['bracket_nm'] = None
            out['notes'].append('non-monotonic sequence: reversal flagged, no single crossover thickness')
        else:
            out['bracket_nm'] = [min(donors, key=_t) if donors else None, max(ecbs, key=_t) if ecbs else None]
    elif no_cross:
        out['outcome'] = 'NO CROSSOVER'
        if reversal:
            out['notes'].append('non-monotonic sequence flagged')
    else:
        if sample_dep and clean:
            out['outcome'] = 'SAMPLE-DEPENDENT'
        elif (not clean or any(c in (None, 'UNRESOLVED') for l, c in seq)
              or any(l not in cells for l in R.HN_NO_CROSSOVER_SET)):
            out['outcome'] = 'UNRESOLVED'
        else:
            out['outcome'] = 'PARTIAL'
        missing = [l for l in R.HN_NO_CROSSOVER_SET if l not in cells]
        if missing:
            out['notes'].append(f'missing coverage at {missing}: NO CROSSOVER cannot be claimed')
        if one(R.HN_THIN) == 'ECB' and not (x_ok2 and x_ok7 and ok10):
            out['notes'].append('0.7 nm is ECB but the required controls (C3, C4, C6, C1, C2, C5; C4 at 1.0 nm) do '
                                'not all pass: no crossover claim')
    out['scope'] = ('Exploratory (D-28): read-out rules frozen, no direction scored. Classes are assumed operational '
                    'screens; C1 results are restricted to the computed parent networks.')
    return _stamp(out, allres + reports)


# ---------------------------------------------------------------- H-G scoring (historical, separate from A27)
def hg_score(s1, s2, comp=None, aio_s1=None, aio_s2=None):
    """H-G registered predictions over the test cells, keyed by role (historical scoring; A27 variants are not
    substituted). Roles are checked: s1/s2 certified W-doped 2.0 nm distinct seeds; comp certified compensated 2.0 nm;
    aIO s1/s2 certified undoped (n_W 0) 2.0 nm distinct seeds."""
    out = {'hypothesis': 'H-G', 'unresolved_checks': []}
    ins = [x for x in (s1, s2, comp, aio_s1, aio_s2) if x is not None]
    bad = [p for r in ins for p in input_problems(r)]
    if bad:
        return _invalid(out, ins, bad)
    dup = duplicates(ins)
    if dup:
        out['unresolved_checks'].append(f'duplicate inputs: {dup}')
    for role, r, kind in (('s1', s1, 'W-doped'), ('s2', s2, 'W-doped'), ('comp', comp, 'compensated'),
                          ('aIO_s1', aio_s1, 'undoped'), ('aIO_s2', aio_s2, 'undoped')):
        if r is None:
            continue
        if certified_kind(r) != kind:
            out['unresolved_checks'].append(f'{role} ({r.get("cell")}): not a certified {kind} cell')
        if thickness(r) != '2.0':
            out['unresolved_checks'].append(f'{role} ({r.get("cell")}): not a 2.0 nm cell')
    for a, b, tag in ((s1, s2, 'aIWO'), (aio_s1, aio_s2, 'aIO')):
        if a is not None and b is not None:
            sa, sb = certified_seed(a), certified_seed(b)
            if sa is None or sb is None or sa == sb:
                out['unresolved_checks'].append(f'{tag} s1/s2 are not certified distinct seeds ({sa}, {sb})')
    roles_unres = bool(out['unresolved_checks'])
    for key in ('P1_lowest_W5d_state_above_host_edge', 'P2_f_ext', 'claude_host_edge_state_W5d'):
        out[key] = {role: ('UNRESOLVED' if roles_unres else (r.get('H-G') or {}).get(key, {}).get('status'))
                    for role, r in (('s1', s1), ('s2', s2))}
        out[key + '_conditional'] = {role: (r.get('H-G') or {}).get(key, {}).get('conditional_status')
                                     for role, r in (('s1', s1), ('s2', s2))}
        out[key + '_cells'] = {'s1': s1.get('cell'), 's2': s2.get('cell')}
    if comp is not None:
        p3 = (comp.get('H-G') or {}).get('P3_comp_no_occupied_localised_W_state_in_gap', {})
        out['P3_comp'] = {'status': 'UNRESOLVED' if roles_unres or not p3 else p3.get('status'),
                          'conditional_status': p3.get('conditional_status'),
                          'unresolved_checks': p3.get('unresolved_checks', ['P3 not available for this cell'])}
        if aio_s1 is not None and aio_s2 is not None:
            def g(x):
                hg = x.get('H-G') or {}
                return None if hg.get('E_g_host_unresolved') else _num(hg.get('E_g_host_eV'))
            gs = [g(x) for x in (comp, aio_s1, aio_s2)]
            unres = [f'{x.get("cell")}: {q}' for x in (comp, aio_s1, aio_s2) for q in qual_reasons(x) + core_unresolved(x)]
            if None in gs or roles_unres:
                out['claude_Eg_comp'] = {'status': 'UNRESOLVED',
                                         'unresolved_checks': ['host gap unresolved, roles not verified or duplicate '
                                                               'inputs'] + unres}
            else:
                spread = abs(gs[1] - gs[2])
                ref = 0.5 * (gs[1] + gs[2])
                tol = max(R.HG_EG_COMP_EV, spread)
                cond = 'PASS' if R.le(abs(gs[0] - ref), tol) else 'FAIL'
                out['claude_Eg_comp'] = {'E_g_comp_eV': gs[0], 'E_g_aIO_s1_s2_eV': gs[1:], 'reference': 'mean of aIO s1/s2',
                                         'difference_eV': gs[0] - ref, 'tolerance_eV': tol, 'sample_spread_eV': spread,
                                         'conditional_status': cond, 'status': 'UNRESOLVED' if unres else cond,
                                         'unresolved_checks': unres,
                                         'per_seed_pass': [R.le(abs(gs[0] - x), tol) for x in gs[1:]]}
    return _stamp(out, ins)


# ---------------------------------------------------------------- H-H, H-I, H-K
def hh(oh, bare):
    """H-H: interior-aligned host-edge shift (OH - bare) <= 0.15 eV at 2.0 nm; no NEW occupied localised surface
    state within 0.3 eV below the host edge. The passivated cell must be passivated and the bare control not, same
    network (certified seed) and thickness."""
    out = {'hypothesis': 'H-H', 'cells': [oh.get('cell'), bare.get('cell')]}
    bad = input_problems(oh) + input_problems(bare)
    if bad:
        return _invalid(out, [oh, bare], bad)
    if same_run(oh, bare):
        bad.append('the passivated cell and the bare control are the same run')
    po = (_q(oh).get('manifest') or {}).get('passivation') if _gate_ok(oh) else None
    pb = (_q(bare).get('manifest') or {}).get('passivation') if _gate_ok(bare) else None
    if po != 'dissociated-water' or pb != 'none':
        bad.append(f'roles: passivated cell passivation {po}, bare control passivation {pb} (certified)')
    if thickness(oh) != thickness(bare) or thickness(oh) is None:
        bad.append(f'thickness differs ({thickness(oh)} vs {thickness(bare)})')
    if certified_seed(oh) is None or certified_seed(oh) != certified_seed(bare):
        bad.append('the bare control is not the same certified network (seed)')
    if bad:
        return _invalid(out, [oh, bare], bad)
    ea, eb = _aligned(oh), _aligned(bare)
    if ea is None or eb is None:
        out['shift'] = {'status': 'UNRESOLVED', 'unresolved_checks':
                        [f'{r.get("cell")}: {_gate(r)}' for r in (oh, bare) if _aligned(r) is None]}
    else:
        d = ea - eb
        out['shift'] = {'aligned_shift_eV': d, 'threshold_eV': R.HH_SHIFT_EV,
                        'status': 'PASS' if R.le(abs(d), R.HH_SHIFT_EV) else 'FAIL', 'unresolved_checks': []}
        if thickness(oh) != '2.0':
            out['shift']['note'] = 'the 0.15 eV bound is registered at 2.0 nm'
    so, sb = oh['H-H'], bare['H-H']
    unres = so.get('unresolved', []) + sb.get('unresolved', []) + \
        [f'{r.get("cell")}: {q}' for r in (oh, bare) for q in qual_reasons(r)]
    if unres:
        out['new_surface_state'] = {'status': 'UNRESOLVED', 'unresolved_checks': unres}
    elif so.get('n_qualifying', 0) == 0:
        out['new_surface_state'] = {'status': 'PASS', 'n_passivated': 0, 'n_bare': sb.get('n_qualifying'),
                                    'unresolved_checks': []}
    else:
        out['new_surface_state'] = {'status': 'UNRESOLVED', 'n_passivated': so['n_qualifying'],
                                    'n_bare': sb.get('n_qualifying'),
                                    'unresolved_checks': ['qualifying states in the passivated cell: whether they are '
                                                          'NEW relative to the bare control is a manual check '
                                                          '(NOT IMPLEMENTED)'],
                                    'passivated_states': so.get('qualifying'), 'bare_states': sb.get('qualifying')}
    return _stamp(out, [oh, bare])


def hi(iface, vac_s1, vac_s2):
    """H-I: |host-edge difference| <= 0.2 eV at 2.0 nm against the arithmetic mean of BOTH vacuum seeds (aligned, valid
    in all three), no localised interface state within 0.3 eV below the host edge. Roles: the interface cell is in
    interface mode with a non-empty interface region; the vacuum cells are slabs of the same thickness with distinct
    certified seeds; the thickness comes from the cells and is scored only at 2.0 nm. A qualified failure is kept even
    when another criterion is unresolved."""
    out = {'hypothesis': 'H-I', 'cells': [iface.get('cell'), vac_s1.get('cell'), vac_s2.get('cell')],
           'failures': [], 'unresolved_checks': []}
    bad = input_problems(iface) + input_problems(vac_s1) + input_problems(vac_s2)
    if bad:
        return _invalid(out, [iface, vac_s1, vac_s2], bad)
    if iface.get('mode') != 'interface' or not ((iface.get('regions') or {}).get('counts') or {}).get('interface'):
        bad.append(f'{iface.get("cell")}: not an interface cell (mode {iface.get("mode")}, empty interface region)')
    for v in (vac_s1, vac_s2):
        if v.get('mode') != 'slab':
            bad.append(f'{v.get("cell")}: vacuum partner is not a slab (mode {v.get("mode")})')
    t = thickness(iface)
    if thickness(vac_s1) != t or thickness(vac_s2) != t or t is None:
        bad.append(f'thickness differs: interface {t}, vacuum {thickness(vac_s1)} / {thickness(vac_s2)}')
    s1, s2 = certified_seed(vac_s1), certified_seed(vac_s2)
    if s1 is None or s2 is None or s1 == s2:
        bad.append(f'the vacuum partners are not two certified distinct seeds ({s1}, {s2})')
    dup = duplicates([iface, vac_s1, vac_s2])
    if dup:
        bad.append(f'duplicate inputs: {dup}')
    if bad:
        return _invalid(out, [iface, vac_s1, vac_s2], bad)
    out['thickness_nm'] = t
    ei, e1, e2 = _aligned(iface), _aligned(vac_s1), _aligned(vac_s2)
    edge_qualified = None not in (ei, e1, e2)
    if None in (ei, e1, e2):
        out['unresolved_checks'] += [f'{r.get("cell")}: {_gate(r)}' for r in (iface, vac_s1, vac_s2)
                                     if _aligned(r) is None]
    if e1 is not None and e2 is not None:
        spread = abs(e1 - e2)
        out['vacuum_s1_s2_spread_eV'] = spread
        if R.gt(spread, R.HI_SPREAD_EV):
            out['unresolved_checks'].append(f'vacuum s1/s2 spread {spread:.3f} eV > {R.HI_SPREAD_EV} eV')
            edge_qualified = False
    if ei is not None and e1 is not None and e2 is not None:
        mean = 0.5 * (e1 + e2)
        d = ei - mean
        out.update({'host_edge_difference_eV': d, 'reference': 'arithmetic mean of vacuum s1 and s2',
                    'individual_differences_eV': [ei - e1, ei - e2]})
        if edge_qualified and R.gt(abs(d), R.HI_EDGE_EV):
            out['failures'].append(f'|host-edge difference| {abs(d):.3f} eV > {R.HI_EDGE_EV} eV (valid alignment)')
    st = iface['H-I']
    search_unres = st.get('unresolved', []) + [f'{iface.get("cell")}: {q}' for q in qual_reasons(iface)]
    out['interface_states'] = st.get('qualifying')
    out['outer_face_states'] = (st.get('outer_face_states') or {}).get('qualifying')
    if search_unres:
        out['unresolved_checks'] += search_unres
    elif st.get('n_qualifying', 0) > 0:
        out['failures'].append(f'{st["n_qualifying"]} localised interface state(s) within 0.3 eV below the host edge')
    if t != '2.0':
        out['status'] = 'NOT REGISTERED'
        out['note'] = f'H-I is registered at 2.0 nm only; at {t} nm the numbers are reported against the forecast'
    elif out['failures']:
        out['status'] = 'FAILED'
    elif out['unresolved_checks']:
        out['status'] = 'UNRESOLVED'
    else:
        out['status'] = 'SUPPORTED'
    out['seed_spread_note'] = 'the 2.0 nm s1/s2 spread is reported separately and never added to the bound'
    return _stamp(out, [iface, vac_s1, vac_s2])


def hk(t07, t20_s1, t20_s2, t10=None):
    """H-K: E_g(0.7) - E_g(2.0) in 0.6-1.3 eV with sample spread 0.03-0.20 eV (both are the registered prediction);
    aligned host edge rises 0.2-1.0 eV from 2.0 to 1.0 nm where the alignment is valid, against EACH 2.0 nm seed
    (PASS only if all pass, FAIL only if all fail). Two certified distinct 2.0 nm seeds are required."""
    out = {'hypothesis': 'H-K', 'unresolved_checks': []}
    ins = [x for x in (t07, t20_s1, t20_s2, t10) if x is not None]
    if t07 is None or t20_s1 is None or t20_s2 is None:
        return _invalid(out, ins, ['H-K needs the 0.7 nm cell and BOTH 2.0 nm seeds (the sample spread is part of the '
                                   'registered prediction)'])
    bad = [p for r in ins for p in input_problems(r)]
    if bad:
        return _invalid(out, ins, bad)
    for r, lab in ((t07, '0.7'), (t20_s1, '2.0'), (t20_s2, '2.0'), (t10, '1.0')):
        if r is not None and thickness(r) != lab:
            bad.append(f'{r.get("cell")}: thickness {thickness(r)} in the {lab} role')
    dup = duplicates(ins)
    if dup:
        bad.append(f'duplicate inputs: {dup}')
    if bad:
        return _invalid(out, ins, bad)
    unres = [f'{r.get("cell")}: {q}' for r in ins for q in qual_reasons(r) + core_unresolved(r)]
    sa, sb = certified_seed(t20_s1), certified_seed(t20_s2)
    if sa is None or sb is None or sa == sb:
        unres.append(f'the 2.0 nm cells are not certified distinct seeds ({sa}, {sb})')
    g07, g1, g2 = _gap(t07), _gap(t20_s1), _gap(t20_s2)
    if None in (g07, g1, g2):
        out['Eg_difference'] = {'status': 'UNRESOLVED', 'unresolved_checks': ['host gap unresolved'] + unres}
    else:
        d = g07 - 0.5 * (g1 + g2)
        sp = abs(g1 - g2)
        lo, hi_ = R.HK_EG_DIFF_EV
        in_val = R.ge(d, lo) and R.le(d, hi_)
        in_sp = R.ge(sp, R.HK_SPREAD_EV[0]) and R.le(sp, R.HK_SPREAD_EV[1])
        cond = 'PASS' if (in_val and in_sp) else 'FAIL'
        out['Eg_difference'] = {'value_eV': d, 'range_eV': [lo, hi_], 'sample_spread_eV': sp,
                                'spread_range_eV': list(R.HK_SPREAD_EV), 'spread_in_registered_range': in_sp,
                                'conditional_status': cond, 'status': 'UNRESOLVED' if unres else cond,
                                'unresolved_checks': unres}
    if t10 is not None:
        a10 = _aligned(t10)
        a20 = [_aligned(x) for x in (t20_s1, t20_s2)]
        if a10 is None or None in a20:
            out['aligned_edge_rise'] = {'status': 'UNRESOLVED', 'unresolved_checks':
                                        [f'{r.get("cell")}: {_gate(r)}' for r in (t10, t20_s1, t20_s2)
                                         if _aligned(r) is None]}
        else:
            lo, hi_ = R.HK_EDGE_RISE_EV
            rises = [a10 - x for x in a20]
            ok = [R.ge(x, lo) and R.le(x, hi_) for x in rises]
            stt = 'PASS' if all(ok) else ('FAIL' if not any(ok) else 'UNRESOLVED')
            out['aligned_edge_rise'] = {'rises_eV': rises, 'mean_rise_eV': float(np.mean(rises)), 'range_eV': [lo, hi_],
                                        'status': 'UNRESOLVED' if unres else stt, 'conditional_status': stt,
                                        'unresolved_checks': unres + ([] if stt != 'UNRESOLVED' else
                                                                      ['the two 2.0 nm seeds disagree'])}
    return _stamp(out, ins)
