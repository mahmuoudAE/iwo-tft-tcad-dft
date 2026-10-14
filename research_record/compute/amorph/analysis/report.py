"""Cell result (JSON) and the human-readable report.

Rule of this module: a class or a test status is never printed without its unresolved checks (fmt_class, fmt_status
are the only printers of classes and statuses, and they always print the checks or 'none').
Every output carries provenance: code version and sha256, register sha256, input file sha256, certificate sha256.
"""
import datetime as _dt
import json

import numpy as np

from . import register as R
from .certify import code_fingerprint, provenance_stamp, qualification_reasons, seal, unqualified  # noqa: F401
from .geometry import first_shell_O
from .readout import gap_search, hg_cell, hh_cell, hi_cell, hn_cell

NOT_IMPLEMENTED = [
    'H-H: whether a qualifying surface state of the passivated cell is NEW relative to the bare control (manual)',
    'H-H forecast |Delta EA| and every electron affinity / vacuum level (EA is not computed; the A15 audit is PARTIAL)',
    'A23: gap anchoring E_g(t) = E_g,anchor + r Delta E_g^PBE(t) (host gaps are reported; the anchoring is not done)',
    'SLAB_PROTOCOL t_rho (electronic thickness from the planar density)',
    'noncollinear / spin-orbit runs',
    'H-L and H-M read-outs',
    'C1 construction, C2 cell building, C4 force screen (structure work, not read-out)',
]


def _clean(x):
    """JSON-safe conversion (numpy scalars, NaN -> None)."""
    if isinstance(x, dict):
        return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, np.ndarray):
        return _clean(x.tolist())
    return x


def support_bounds(p, cp, nonw):
    """Rigorous membership bounds of the 80 % non-W support set when the missing weight m = 1 - completeness can lie
    anywhere (W, non-W atoms, concentrated or spread). Raw weights r = p x cp; atom a (rank order of nonw) is a member
    iff the raw weight ranked above it is < 0.8 x the non-W total. Placing x <= m on non-W atoms changes the total to
    T + x; the weight above a grows at most by x plus every atom that x can lift above a (r_b + m >= r_a), and the
    margin grows with x, so x = m is the worst case. SURE: above_a + m + lift_a < 0.8 (T + m) (member under every
    placement). POSSIBLE: member with m nowhere among non-W atoms, or with all of m on a itself.
    Returns (sure, possible) as 1-based atom lists."""
    cp = min(float(cp), 1.0)
    m = max(0.0, 1.0 - cp)
    r = {a: float(p[a]) * cp for a in nonw}
    T = sum(r.values())
    f = R.ATTR_SUPPORT_FRACTION
    sure, poss, above = [], [], 0.0
    for i, a in enumerate(nonw):
        lift = sum(r[b] for b in nonw[i + 1:] if r[b] + m >= r[a])
        base = above < f * T
        if base and above + m + lift < f * (T + m):
            sure.append(int(a) + 1)
        best = sum(r[b] for b in nonw if r[b] > r[a] + m)
        if base or best < f * (T + m):
            poss.append(int(a) + 1)
        above += r[a]
    return sure, poss


def attribution_data(c):
    """Trapping states (attribution (i) and the support set of (ii)) with their completeness bounds, the localised
    states near the gap with their COMPLETE atomic weights and completeness (for use as a parent), the flagged states of
    the same window, and the excluded and unbounded localised occupation."""
    W = [i for i, s in enumerate(c.st.species) if s == 'W']
    shell = set(W)
    for w in W:
        shell.update(first_shell_O(c.st, w))
    shell = sorted(shell)
    traps = []
    above = c.n > c.N_v
    loc_above = above & R.le(c.PR, R.PR_LOCALISED)
    sel = np.where(loc_above & R.ge(c.fw, R.TRAP_MIN_OCC_E))[0]
    excl = loc_above & (c.fw > 0) & ~R.ge(c.fw, R.TRAP_MIN_OCC_E)
    # flagged occupied states above N_v: their PR_n is not reliable, so trap membership is unbounded
    unb = above & c.flagged & R.ge(c.fw, R.TRAP_MIN_OCC_E)
    for i in sel:
        p = c.p[i]
        nonw = [a for a in np.argsort(-p) if c.st.species[a] != 'W']
        tot = sum(p[a] for a in nonw)
        sup, acc = [], 0.0
        for a in nonw:
            if acc >= R.ATTR_SUPPORT_FRACTION * tot:
                break
            sup.append(int(a) + 1)
            acc += p[a]
        st = c.state(i, top=5)
        wsh = float(p[shell].sum()) if shell else 0.0
        cp = float(c.compl[i])
        st['W_plus_first_shell_O'] = wsh
        # completeness bound: the missing weight (1 - completeness) may lie anywhere
        st['W_plus_first_shell_O_bounds'] = [wsh * min(cp, 1.0), min(1.0, wsh * min(cp, 1.0) + max(0.0, 1.0 - cp))]
        st['support_nonW_atoms'] = sup
        sure, poss = support_bounds(p, cp, nonw)
        st['support_nonW_atoms_possible'] = poss if cp < 1.0 else list(sup)
        st['support_nonW_atoms_sure'] = sure if cp < 1.0 else list(sup)
        traps.append(st)
    if c.E_c is not None and c.E_v is not None:
        lo, hi = c.E_v, c.E_c + 1.5
    else:
        ef = float(np.min(c.data.ef))
        lo, hi = ef - 3.0, ef + 1.5
    loc = []
    win = (c.e >= lo) & (c.e <= hi)
    for i in np.where(R.le(c.PR, R.PR_LOCALISED) & win)[0]:
        loc.append({'spin': int(c.s[i]) + 1, 'k': int(c.k[i]) + 1, 'band': int(c.n[i]), 'E_eV': float(c.e[i]),
                    'PR_n': float(c.PR[i]), 'flagged': bool(c.flagged[i]), 'completeness': float(c.compl[i]),
                    'p': [float(x) for x in c.p[i]]})                 # complete atomic weights (no cut)
    return {'W_atoms': [w + 1 for w in W], 'W_plus_first_shell_atoms': [a + 1 for a in shell],
            'first_shell_cutoff_A': R.W_O_FIRST_SHELL_A, 'trapping_states': traps,
            'trap_definition': f'n > N_v, PR_n <= {R.PR_LOCALISED}, f_nk w_k >= {R.TRAP_MIN_OCC_E} e',
            'excluded_localised_occupation': {'n_states': int(excl.sum()), 'electrons': float(c.fw[excl].sum()),
                                              'note': f'localised states above N_v with < {R.TRAP_MIN_OCC_E} e each'},
            'unbounded_trap_membership': {'n_states': int(unb.sum()), 'electrons': float(c.fw[unb].sum()),
                                          'note': 'flagged occupied states above N_v (PR_n not reliable)'},
            'trapped_electrons_counted': float(c.fw[sel].sum()),
            'localised_states': loc, 'localised_states_window_eV': [lo, hi],
            'flagged_states_in_window_eV': [float(x) for x in c.e[win & c.flagged]],
            'host_edges_resolved': c.edge_ok('host_edge') and c.edge_ok('host_valence_edge')}


CELL_SCHEMA = 'iwo-amorph-analysis/cell/3'


def cell_result(c, source, notes=(), qual=None, meta=None):
    """The JSON record of one cell (deterministic content, self-sealed; time stamps and paths in 'meta').
    qual: the run qualification from certify.validate() (None: unqualified)."""
    qual = dict(qual) if qual is not None else unqualified('no certificate given')
    pv = provenance_stamp(extra={'source': source, 'notes': list(notes),
                                 'certificate_sha256': qual.get('certificate_sha256')})
    if pv['register']['sha256'] is None:
        qual['register_missing'] = True
    reasons = qualification_reasons(qual)
    qual['reasons'] = reasons
    out = c.summary()
    out['schema'] = CELL_SCHEMA
    out['geometry_sha256'] = c.st.geometry_hash()
    files, paths = {}, {}
    for k, v in c.data.sources.items():
        if isinstance(v, dict) and 'sha256' in v:
            files[k] = {'sha256': v['sha256'], 'origin': v.get('origin', 'file')}
            if v.get('path'):
                paths[k] = v['path']
    pv['files'] = files
    out['provenance'] = pv
    out['run_settings'] = c.data.settings
    out['run_qualification'] = dict(qual, W5d_convention=c.w5d_convention, diagnostic_only=c.data.diagnostic_only)
    out['alignment'] = dict(out['alignment'], **c.aligned_edges(reasons))
    out['total_energy_Ry'] = c.data.etot_ry
    out['H-N'] = hn_cell(c, out['run_qualification'])
    out['H-G'] = hg_cell(c, out['run_qualification'])
    out['H-H'] = hh_cell(c)
    out['H-I'] = hi_cell(c)
    gs = gap_search(c, lo=c.E_v, hi=c.E_c, include_lo=False, occupied=False, weight_key='W5d', weight_min=0.0,
                    label='localised states (PR_n <= 0.05) in the host gap, any occupation (A15 trap count)')
    gs['unresolved'] += [f'host edge: {x}' for x in c.host_edge['unresolved']] + \
        [f'host valence edge: {x}' for x in c.host_valence_edge['unresolved']] + list(c.reasons)
    out['gap_states'] = gs
    out['attribution_data'] = attribution_data(c)
    out['structure'] = c.st.to_json()
    out['implementation_choices'] = R.IMPLEMENTATION_CHOICES
    out['not_implemented'] = NOT_IMPLEMENTED
    out = _clean(out)
    out['meta'] = {'written_utc': _dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                   'file_paths': paths, **(meta or {})}
    return seal(out)


# ---------------------------------------------------------------- text
def fmt_checks(checks):
    return 'none' if not checks else '; '.join(checks)


def fmt_class(label, cls, cond, checks):
    s = f'{label}: {cls}'
    if cls == 'UNRESOLVED' and cond:
        s += f'  (class if resolved: {cond}; NOT a result)'
    return s + f'\n    unresolved checks: {fmt_checks(checks)}'


def fmt_status(label, st):
    s = f'{label}: {st.get("status")}'
    if st.get('status') == 'UNRESOLVED' and st.get('conditional_status'):
        s += f'  (if resolved: {st["conditional_status"]}; NOT a result)'
    return s + f'\n    unresolved checks: {fmt_checks(st.get("unresolved_checks", []))}'


def _f(x, nd=3, unit=''):
    return 'n/a' if x is None else (f'{x:.{nd}f}{unit}' if isinstance(x, (int, float)) else str(x))


def text_report(r):
    L = []
    a = L.append
    a(f'IWO amorphous read-out, cell {r.get("cell")}  (mode {r["mode"]}, {r["n_atoms"]} atoms, {r["composition"]})')
    pv = r['provenance']
    a(f'code {pv["code_version"]} sha256 {pv["code_sha256"]}  source {pv["source"]}  written {(r.get("meta") or {}).get("written_utc")}')
    a(f'register sha256 {pv["register"]["sha256"]}; certificate sha256 {pv.get("certificate_sha256")}; '
      f'geometry sha256 {r.get("geometry_sha256")}')
    for k, v in (pv.get('files') or {}).items():
        if isinstance(v, dict) and 'sha256' in v:
            a(f'  input {k} sha256 {v["sha256"]}')
    for n in pv.get('notes', []):
        a(f'  note: {n}')
    q = r['run_qualification']
    a(f'run qualification: certificate valid {q["certificate_valid"]}, smearing qualified {q["smearing_qualified"]}, '
      f'relaxation {q["relaxation"]}, geometry {q["geometry"]}, manifest verified {q["manifest_verified"]}, '
      f'W-5d convention {q["W5d_convention"]}')
    a(f'    qualification checks: {fmt_checks(q.get("reasons", []))}')
    if q.get('diagnostic_only'):
        a(f'  DIAGNOSTIC ONLY: {q["diagnostic_only"]}')
    for w in r.get('warnings', []):
        a(f'  WARNING: {w}')
    a('')
    a('Section 1')
    p = r['accounting_partition']
    a(f'  N_el {p["N_el"]:g}, N_ex {p["N_ex"]} ({p["N_ex_source"]}; formal-charge count {p["N_ex_formal_charge"]}), '
      f'N_v {p["N_v"]:g}')
    o = r['occupations']
    a(f'  occupations: {o["occupations_kind"]} {o.get("smearing")} {_f(o.get("degauss_eV"), 4)} eV; '
      f'E_F {o["E_F_eV"]}; sum f w = {o["sum_f_w"]:.4f}; {o.get("f_source")}')
    if 'max_abs_f_recomputed_minus_qe' in o:
        a(f'  max |f recomputed - f QE| = {o["max_abs_f_recomputed_minus_qe"]:.2e}')
    ac = r['excess_accounting']
    a(f'  excess accounting: {ac["electrons_above_Nv"]:.4f} e above N_v vs N_ex {ac["N_ex"]} -> {ac["check"]} '
      f'(tolerance {ac["tolerance_e"]} e)')
    rg = r['regions']
    a(f'  regions: {rg["counts"]}; interior fraction {rg["interior_fraction"]:.3f}'
      + (f'; z_if {rg["z_if_A"]:.2f} A (A24)' if rg.get('z_if_A') is not None else ''))
    cp = r['completeness']
    a(f'  completeness: {cp["n_flagged"]} of {cp["n_states"]} states flagged (< 0.90), minimum {cp["min_completeness"]:.3f}; '
      f'projections {cp["proj_kind"]}')
    for key, lab in (('host_edge', 'host edge'), ('host_valence_edge', 'host valence edge')):
        e = r[key]
        st = e.get('state') or {}
        a(f'  {lab}: {_f(e["E_eV"], 4, " eV")}  (k {st.get("k")}, band {st.get("band")}, spin {st.get("spin")}, '
          f'PR_n {_f(st.get("PR_n"))}, interior weight {_f((st.get("weights") or {}).get("interior"))}, '
          f'W-5d {_f(st.get("W5d"))})')
        a(f'    unresolved checks: {fmt_checks(e["unresolved"])}')
    g = r.get('host_gap')
    a(f'  host gap: {_f(g["E_g_host_eV"], 4, " eV") if g else "n/a"}')
    al = r['alignment']
    a(f'  interior alignment ({al.get("rule")}): {"VALID" if al.get("valid") else "UNRESOLVED"}; primary std '
      f'{_f(al.get("plateau_std_eV"), 4, " eV")}, mean variation {_f(al.get("mean_variation_eV"), 4, " eV")}, '
      f'common interval {al.get("common_interval_A")} A')
    a(f'    unresolved checks: {fmt_checks(al.get("unresolved", []))}')
    a(f'  aligned host edge {_f(al.get("aligned_host_edge_eV"), 4, " eV")}; release gate: {fmt_checks(al.get("gate", []))}')
    for s in r.get('section1_unresolved', []):
        a(f'  SECTION-1 UNRESOLVED: {s}')
    a('')
    hn = r['H-N']
    a('H-N (A27, exploratory)')
    if hn.get('class') == 'N/A':
        a(f'  class: N/A ({hn.get("note")})')
    else:
        a('  ' + fmt_class('class', hn['class'], hn.get('class_if_resolved'), hn.get('unresolved_checks', [])))
        fr = hn.get('fractions', {})
        a(f'  f_ext {_f(hn.get("f_ext"))} (bounds {fr.get("f_ext_bounds")}), f_locW {_f(hn.get("f_locW"))}, '
          f'f_W5d {_f(hn.get("f_W5d"))} (raw-W5d convention: f_locW {_f(hn.get("f_locW_raw"))}, '
          f'f_W5d {_f(hn.get("f_W5d_raw"))}, class {hn.get("class_with_raw_W5d")})')
        dw = hn.get('Delta_W', {})
        a(f'  Delta_W: value {_f(dw.get("value_eV"), 3, " eV")}, lower bound {_f(dw.get("lower_bound_eV"), 3, " eV")}, '
          f'> 0.3 eV: {dw.get("gt_0p3")}; coverage {dw.get("coverage")}')
        a(f'  E_F - host edge: {hn.get("E_F_minus_host_edge_eV")} eV')
        if hn.get('W5d_convention_sensitive'):
            a('  FLAG: the class changes with the raw W-5d convention (CONVENTION-SENSITIVE)')
        for x in hn.get('threshold_proximity', []):
            a(f'  near threshold: {x}')
        rs = fr.get('region_shares', {})
        a('  excess-electron shares: ' + ', '.join(f'{k} {v:.3f}' for k, v in rs.items()))
        a('  states used (E eV, electrons, PR_n, N_eff, W-5d):')
        for s in hn.get('states_used', []):
            a(f'    s{s["spin"]} k{s["k"]} n{s["band"]}: {s["E_eV"]:.4f}, {s["electrons"]:.4f}, {s["PR_n"]:.3f}, '
              f'{s["N_eff"]:.1f}, {s["W5d"]:.3f}{"  FLAGGED" if s["flagged"] else ""}{"  " + s["role"] if "role" in s else ""}')
    a('')
    a('H-G (registered; scored over the test cells by "compare hg")')
    for k, v in r['H-G'].items():
        if isinstance(v, dict) and 'status' in v:
            a('  ' + fmt_status(k, v))
            if 'value' in v or 'value_eV' in v:
                a(f'    value {v.get("value", v.get("value_eV"))}')
        elif k.startswith('forecast'):
            a(f'  {k}: {v}')
    if 'E_g_host_eV' in r['H-G']:
        a(f'  host gap (for the compensated-cell comparison): {r["H-G"]["E_g_host_eV"]:.4f} eV')
    a('')
    for key in ('H-H', 'H-I'):
        g = r[key]
        a(f'{key} per-cell search: {g["search"]}; window {g["window_eV"]}; qualifying {g.get("n_qualifying")}')
        a(f'    unresolved checks: {fmt_checks(g.get("unresolved", []))}')
    a('')
    a('Implementation choices (not registered):')
    for k, v in r['implementation_choices'].items():
        a(f'  {k}: {v}')
    a('Not implemented:')
    for x in r['not_implemented']:
        a(f'  - {x}')
    return '\n'.join(L) + '\n'


def write(r, json_path=None, text_path=None):
    if json_path:
        with open(json_path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(r, f, indent=1, allow_nan=False)
    if text_path:
        with open(text_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text_report(r))
