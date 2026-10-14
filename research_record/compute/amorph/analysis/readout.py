"""Per-cell read-outs: H-N (A27) observables and class, H-G (registered predictions, forecasts), gap-state searches
(H-G compensated cell, H-H, H-I).

H-N, quoted from A27: "f_ext: the fraction of N_ex in extended host states (PR_n >= 0.20, at or above the host edge);
f_locW: the fraction of N_ex in states with n > N_v that are localised (PR_n <= 0.05) and have >= 30 % W-5d weight;
f_W5d: the W-5d share of the excess electrons, n > N_v only; Delta_W: E(lowest state with >= 30 % W-5d among states
above the section-1 host valence edge) - E(host edge). Band coverage: the FINAL nbnd must reach at least 1.0 eV above
the host edge at every k-point. If no qualifying W state lies within the computed bands, Delta_W is reported as a lower
bound ... It counts as > 0.3 eV only if that bound exceeds 0.3 eV. If the coverage rule fails, Delta_W is UNRESOLVED.
Also reported: E_F - host edge, and N_eff = N PR_n for every state used."
Classes: "DONOR: f_ext >= 0.80, Delta_W > 0.3 eV, and f_locW < 0.10. ECB: f_ext < 0.50, or f_locW >= 0.50.
PARTIAL: anything else. UNRESOLVED: any section-1 unresolved condition, a failed band-coverage rule, or a smearing
qualification still pending (A26)."
Every class is returned with its unresolved checks; 'class_if_resolved' is the class the numbers would give once the
listed conditions are cleared. It is NOT a result while 'class' is UNRESOLVED.
Run qualification (certificate: relaxation, smearing, manifest) enters every status through `qual['reasons']`.
"""
import numpy as np

from . import register as R

PENDING = 'smearing qualification pending (A26/A15; not certified)'


def classify(f_ext, dw_gt, f_locw):
    """A27 class from resolved numbers (dw_gt: Delta_W > 0.3 eV as True/False)."""
    if f_ext is None or f_locw is None or dw_gt is None:
        return None
    if R.ge(f_ext, R.HN_DONOR_FEXT) and dw_gt and R.lt(f_locw, R.HN_DONOR_FLOCW):
        return 'DONOR'
    if R.lt(f_ext, R.HN_ECB_FEXT) or R.ge(f_locw, R.HN_ECB_FLOCW):
        return 'ECB'
    return 'PARTIAL'


def qual_reasons(qual):
    """Run-qualification reasons; None means no certificate (relaxation UNKNOWN, smearing pending, manifest unverified)."""
    from .certify import qualification_reasons, unqualified
    if qual is None:
        qual = unqualified('no certificate given')
    return qualification_reasons(qual)


def status(passed, reasons, qual=None):
    """Registered-test status. 'conditional_status' is what the numbers say if the reasons were cleared."""
    rs = list(reasons) + qual_reasons(qual)
    cond = None if passed is None else ('PASS' if passed else 'FAIL')
    return {'status': 'UNRESOLVED' if (rs or passed is None) else cond, 'conditional_status': cond,
            'unresolved_checks': rs}


# ---------------------------------------------------------------- excess-electron fractions
def excess_fractions(c, W5d=None):
    """f_ext, f_locW, f_W5d and region shares of the N_ex nominal excess electrons (n > N_v only), with conservative
    bounds obtained by giving the occupation of flagged states (completeness < 0.90) to either side."""
    W5d = c.W5d if W5d is None else W5d
    if c.N_ex == 0:
        return {'N_ex': 0, 'note': 'N_ex = 0: excess-electron fractions are N/A (section 1)'}
    above = c.n > c.N_v
    fw = np.where(above, c.fw, 0.0)
    nex = float(c.N_ex)
    out = {'N_ex': c.N_ex, 'unresolved': []}
    locw = above & R.le(c.PR, R.PR_LOCALISED) & R.ge(W5d, R.W5D_STATE)
    out['f_locW'] = float(fw[locw].sum() / nex)
    out['f_W5d'] = float((fw * W5d).sum() / nex)
    out['region_shares'] = {k: float((fw * v).sum() / nex) for k, v in c.regw.items()}
    fl = above & c.flagged & (c.fw > 0)
    flag_e = float(fw[fl].sum())
    out['electrons_in_flagged_states'] = flag_e
    out['f_locW_bounds'] = [float(fw[locw & ~fl].sum() / nex), float((fw[locw & ~fl].sum() + flag_e) / nex)]
    w5_lo = np.where(fl, c.W5d_raw, W5d)
    w5_hi = np.where(fl, np.minimum(1.0, c.W5d_raw + np.maximum(0.0, 1.0 - c.compl)), W5d)
    out['f_W5d_bounds'] = [float((fw * w5_lo).sum() / nex), float((fw * w5_hi).sum() / nex)]
    if c.E_c is not None:
        ext = above & R.ge(c.PR, R.PR_EXTENDED) & (c.e >= c.E_c)
        out['f_ext'] = float(fw[ext].sum() / nex)
        can = above & (c.e >= c.E_c)
        out['f_ext_bounds'] = [float(fw[ext & ~fl].sum() / nex), float((fw[ext & ~fl].sum() + fw[fl & can].sum()) / nex)]
        out['electrons_below_host_edge'] = float(fw[above & (c.e < c.E_c)].sum())
        out['electrons_nonextended_at_or_above_edge'] = float(fw[above & (c.e >= c.E_c) & ~R.ge(c.PR, R.PR_EXTENDED)].sum())
    else:
        out['f_ext'] = None
        out['f_ext_bounds'] = None
    if not c.edge_ok('host_edge'):
        out['unresolved'].append('host edge unresolved: ' + '; '.join(c.host_edge['unresolved']))
    return out


# ---------------------------------------------------------------- Delta_W
def _gt(value, lb):
    """Delta_W > 0.3 eV (float-guarded) as True / False / None (unknown: only a lower bound <= 0.3 eV)."""
    if value is not None:
        return R.gt(value, R.HN_DONOR_DW_EV)
    if lb is not None and R.gt(lb, R.HN_DONOR_DW_EV):
        return True
    return None


def _dw_eval(c, q, top_min):
    if q.any():
        i = int(np.argmin(np.where(q, c.e, np.inf)))
        if c.e[i] <= top_min:
            v = float(c.e[i] - c.E_c)
            return {'value_eV': v, 'lower_bound_eV': None, 'index': i, 'gt_0p3': _gt(v, None)}
        lb = float(top_min - c.E_c)       # a lower W state could lie above the top computed band at another k
        return {'value_eV': None, 'lower_bound_eV': lb, 'upper_found_eV': float(c.e[i] - c.E_c), 'index': i,
                'gt_0p3': _gt(None, lb)}
    lb = float(top_min - c.E_c)
    return {'value_eV': None, 'lower_bound_eV': lb, 'index': None, 'gt_0p3': _gt(None, lb)}


def delta_w(c, domain='above_valence_edge', W5d=None, coverage_rule=True):
    """Lowest >= 30 % W-5d state relative to the host edge. domain: 'above_valence_edge' (A27 Delta_W),
    'all_states' (H-G registered wording), 'above_Nv' (band index > N_v: the A23 nc_readout reading).
    Flagged states (completeness < 0.90) are bounded both ways: a flagged state surely qualifies only if its raw W-5d
    weight alone reaches 0.30 (it may LOSE W character), and possibly qualifies if raw + missing weight reaches 0.30
    (it may GAIN W character); the outcome must be the same under both."""
    W5d = c.W5d if W5d is None else W5d
    out = {'domain': domain, 'unresolved': []}
    if c.E_c is None:
        out['unresolved'].append('host edge unresolved')
        out['gt_0p3'] = None
        return out
    if not c.edge_ok('host_edge'):
        out['unresolved'].append('host edge unresolved: ' + '; '.join(c.host_edge['unresolved']))
    if domain == 'above_valence_edge':
        if c.E_v is None:
            out['unresolved'].append('host valence edge unresolved (search domain undefined)')
            out['gt_0p3'] = None
            return out
        if not c.edge_ok('host_valence_edge'):
            out['unresolved'].append('host valence edge unresolved: ' + '; '.join(c.host_valence_edge['unresolved']))
        dom = c.e > c.E_v
    elif domain == 'above_Nv':
        dom = c.n > c.N_v
    else:
        dom = np.ones_like(c.e, dtype=bool)
    top = c.data.e.max(axis=2)                               # highest computed band at every (spin, k)
    top_min = float(top.min())
    cov = top - c.E_c
    out['coverage'] = {'min_top_band_minus_host_edge_eV': float(cov.min()), 'required_eV': R.HN_COVERAGE_EV,
                       'pass': bool(R.ge(cov, R.HN_COVERAGE_EV).all()), 'applied': coverage_rule}
    if coverage_rule and not out['coverage']['pass']:
        out['unresolved'].append(f'band coverage fails: the top computed band is only {cov.min():.3f} eV above the host '
                                 f'edge at some k (needs {R.HN_COVERAGE_EV} eV)')
    fl = c.flagged
    raw_hi = np.minimum(1.0, c.W5d_raw + np.maximum(0.0, 1.0 - c.compl))
    q_prim = dom & R.ge(W5d, R.W5D_STATE)
    q_sure = dom & np.where(fl, R.ge(c.W5d_raw, R.W5D_STATE), R.ge(W5d, R.W5D_STATE))
    q_poss = dom & np.where(fl, R.ge(raw_hi, R.W5D_STATE), R.ge(W5d, R.W5D_STATE))
    prim, sure, poss = (_dw_eval(c, q, top_min) for q in (q_prim, q_sure, q_poss))
    # quantitative bounds (Codex rc2): flagged states gaining W character can only lower Delta_W (q_poss), losing it can
    # only raise it (q_sure); a value known only as a lower bound is unbounded above
    lo = poss['value_eV'] if poss['value_eV'] is not None else poss['lower_bound_eV']
    hi = sure['value_eV'] if sure['value_eV'] is not None else None
    out['bounds_eV'] = [lo, hi]
    out.update({k: prim[k] for k in ('value_eV', 'lower_bound_eV', 'gt_0p3')})
    if 'upper_found_eV' in prim:
        out['upper_found_eV'] = prim['upper_found_eV']
    out['W_state'] = c.state(prim['index']) if prim['index'] is not None else None
    out['gt_0p3_flag_extremes'] = {'flagged_may_gain_W': poss['gt_0p3'], 'flagged_may_lose_W': sure['gt_0p3']}
    out['n_flagged_in_domain'] = int((dom & fl).sum())
    if not (prim['gt_0p3'] == sure['gt_0p3'] == poss['gt_0p3']):
        out['unresolved'].append('Delta_W > 0.3 eV rests on flagged states (completeness < 0.90): flagged states '
                                 f'gaining W character give {poss["gt_0p3"]}, losing it give {sure["gt_0p3"]}')
    if prim['gt_0p3'] is None and not out['unresolved']:
        out['unresolved'].append('Delta_W only bounded below by <= 0.3 eV (no W state within the computed bands)')
    return out


# ---------------------------------------------------------------- gap-state searches (all bands)
def gap_search(c, *, lo, hi, include_lo, occupied, weight_key, weight_min=R.REGION_STATE_WEIGHT,
               pr_max=R.PR_LOCALISED, label=''):
    """States with lo (<= or <) E < hi, PR_n <= pr_max and weight >= weight_min on weight_key ('W5d' or a region),
    occupied (>= 0.01 e in the state, f x 2/nspin) if required; all bands, all k, both spins. Flagged states in the window make the
    search unresolved. States meeting every other criterion with 0 < f < 0.5 are reported as excluded minority
    occupation."""
    out = {'search': label, 'window_eV': [lo, hi], 'include_lower': include_lo,
           'occupied_required': occupied, 'occupied_definition': f'>= {R.TRAP_MIN_OCC_E} e in the state',
           'criteria': f'PR_n <= {pr_max}, {weight_key} >= {weight_min}', 'unresolved': []}
    if lo is None or hi is None:
        out['unresolved'].append('window undefined (host edge or host valence edge unresolved)')
        return out
    win = ((c.e >= lo) if include_lo else (c.e > lo)) & (c.e < hi)
    w = c.W5d if weight_key == 'W5d' else c.regw[weight_key]
    crit = win & R.le(c.PR, pr_max) & R.ge(w, weight_min)
    elec = c.focc * (2.0 / c.data.nspin)               # electrons held by the state (spin factor included)
    q = crit & R.ge(elec, R.TRAP_MIN_OCC_E) if occupied else crit
    out['qualifying'] = [c.state(i) for i in np.where(q)[0]]
    out['n_qualifying'] = int(q.sum())
    if occupied:
        minor = crit & (elec > 0) & ~R.ge(elec, R.TRAP_MIN_OCC_E)
        out['excluded_below_occupation_threshold'] = {'n_states': int(minor.sum()),
                                                      'electrons': float(c.fw[minor].sum())}
    fl = win & c.flagged
    out['n_flagged_in_window'] = int(fl.sum())
    if fl.any():
        out['unresolved'].append(f'{int(fl.sum())} flagged state(s) (completeness < 0.90) in the window')
    if c.approx:
        out['unresolved'].append('approximate (text) projections')
    return out


# ---------------------------------------------------------------- H-N per cell
def _near(name, x, thr, margin):
    return [f'{name} = {x:.3f} within {margin} of the threshold {thr}'] if x is not None and abs(x - thr) < margin else []


def is_compensated(c):
    """Compensated status only from a verified composition-checked manifest (never from the name or an override)."""
    return c.kind == 'compensated' and c.nex_info.get('N_ex_verified') is True


def hn_cell(c, qual=None):
    """A27 observables and the per-cell class of a W-doped cell."""
    out = {'hypothesis': 'H-N (A27, exploratory)', 'W5d_convention': c.w5d_convention}
    if c.st.count('W') > 0 and c.N_ex == 0 and c.nex_info.get('N_ex_verified') is not True:
        out.update({'class': 'UNRESOLVED', 'class_if_resolved': 'N/A',
                    'unresolved_checks': ['N_ex = 0 not verified for a W-containing cell (no composition-checked '
                                          'manifest)'] + list(c.reasons) + qual_reasons(qual),
                    'core_unresolved_checks': ['N_ex = 0 not verified for a W-containing cell']})
        return out
    if c.st.count('W') == 0 or c.N_ex == 0:
        out['class'] = 'N/A'
        out['note'] = 'H-N classes are defined for W-doped cells with N_ex > 0 only'
        out['unresolved_checks'] = list(c.reasons) + qual_reasons(qual)
        out['core_unresolved_checks'] = list(c.reasons)
        return out
    fr = excess_fractions(c)
    dw = delta_w(c)
    ef = c.data.ef
    reasons = list(c.reasons)
    reasons += [f'host edge: {r}' for r in c.host_edge['unresolved']]
    reasons += [f'host valence edge: {r}' for r in c.host_valence_edge['unresolved']]
    reasons += [r for r in dw['unresolved'] if not r.startswith('host')]
    f_ext, f_locw = fr.get('f_ext'), fr.get('f_locW')
    cls = classify(f_ext, dw.get('gt_0p3'), f_locw)
    if cls is not None:
        ext = dw['gt_0p3_flag_extremes']
        combos = {classify(fe, g, fl) for fe in fr['f_ext_bounds'] for fl in fr['f_locW_bounds']
                  for g in (ext['flagged_may_gain_W'], ext['flagged_may_lose_W'], dw['gt_0p3'])}
        out['class_flag_extremes'] = sorted(str(x) for x in combos)
        if combos != {cls}:
            reasons.append('class rests on flagged states (completeness < 0.90): extremes give '
                           + '/'.join(sorted(str(x) for x in combos)))
    alt = None
    if cls is not None:
        other = 'raw' if c.w5d_convention == 'normalised' else 'normalised'
        W_alt = c.W5d_raw if other == 'raw' else c.W5d_norm
        fr_r = excess_fractions(c, W5d=W_alt)
        dw_r = delta_w(c, W5d=W_alt)
        alt = classify(fr_r.get('f_ext'), dw_r.get('gt_0p3'), fr_r.get('f_locW'))
        out['opposite_W5d_convention'] = other
        out['class_with_opposite_W5d'] = alt
        out['class_with_raw_W5d'] = alt if other == 'raw' else cls
        out['f_locW_raw'] = fr_r.get('f_locW') if other == 'raw' else f_locw
        out['f_W5d_raw'] = fr_r.get('f_W5d') if other == 'raw' else fr.get('f_W5d')
        out['Delta_W_opposite'] = {k: dw_r.get(k) for k in ('value_eV', 'lower_bound_eV', 'gt_0p3')}
    all_r = reasons + qual_reasons(qual)
    out.update({
        'class': 'UNRESOLVED' if (all_r or cls is None) else cls,
        'class_if_resolved': cls,
        'unresolved_checks': all_r,
        'core_unresolved_checks': reasons,
        'W5d_convention_sensitive': (alt is not None and alt != cls),
        'f_ext': f_ext, 'f_locW': f_locw, 'f_W5d': fr.get('f_W5d'), 'fractions': fr, 'Delta_W': dw,
        'E_F_minus_host_edge_eV': None if c.E_c is None else [float(x - c.E_c) for x in ef],
        'states_used': _states_used(c, dw),
    })
    prox = []
    prox += _near('f_ext', f_ext, R.HN_DONOR_FEXT, R.NEAR_FRACTION) + _near('f_ext', f_ext, R.HN_ECB_FEXT, R.NEAR_FRACTION)
    prox += _near('f_locW', f_locw, R.HN_DONOR_FLOCW, R.NEAR_FRACTION) + _near('f_locW', f_locw, R.HN_ECB_FLOCW, R.NEAR_FRACTION)
    prox += _near('Delta_W', dw.get('value_eV'), R.HN_DONOR_DW_EV, R.NEAR_EV)
    if dw.get('W_state'):
        prox += _near('W-5d of the Delta_W state', dw['W_state']['W5d'], R.W5D_STATE, R.NEAR_W5D)
    if c.host_edge.get('state'):
        prox += _near('PR_n of the host-edge state', c.host_edge['state']['PR_n'], R.PR_EXTENDED, R.NEAR_PR)
    prox += _near('accounting deviation (e)', abs(c.acc['deviation']), R.ACCOUNTING_TOL_E, 0.01)
    out['threshold_proximity'] = prox
    return out


def _states_used(c, dw):
    """N_eff = N PR_n for every state used: the edges, the Delta_W state and every excess state with >= 1e-3 e."""
    idx = set()
    for e in (c.host_edge, c.host_valence_edge):
        if e.get('index') is not None:
            idx.add(e['index'])
    sel = np.where((c.n > c.N_v) & (c.fw >= 1e-3))[0]
    idx.update(int(i) for i in sel)
    rows = [c.state(i, top=3) for i in sorted(idx, key=lambda j: c.e[j])]
    if dw.get('W_state'):
        rows.append(dict(dw['W_state'], role='Delta_W state'))
    keys = ('spin', 'k', 'band', 'E_eV', 'electrons', 'PR_n', 'N_eff', 'W5d', 'W5d_raw', 'completeness', 'flagged')
    return [dict({k: r[k] for k in keys if k in r}, **({'role': r['role']} if 'role' in r else {})) for r in rows]


# ---------------------------------------------------------------- H-G per cell
def hg_cell(c, qual=None):
    """H-G items computable from one cell (historical registered scoring; A27 variants reported, never substituted).
    Scored over the test cells by compare.hg_score()."""
    out = {'hypothesis': 'H-G (registered, A10/A16)'}
    base = list(c.reasons)
    is_w = c.st.count('W') > 0
    comp = is_w and is_compensated(c)
    if is_w:
        hist = delta_w(c, domain='all_states', coverage_rule=False)
        a27 = delta_w(c, domain='above_valence_edge')
        a23 = delta_w(c, domain='above_Nv', coverage_rule=False)
        r1 = base + hist['unresolved']
        out['P1_lowest_W5d_state_above_host_edge'] = dict(
            status(hist.get('gt_0p3'), r1, qual), value_eV=hist.get('value_eV'),
            lower_bound_eV=hist.get('lower_bound_eV'), W_state=hist.get('W_state'), threshold_eV=R.HG_W_ABOVE_EDGE_EV,
            domain='all states (registered H-G wording; historical score)',
            variants_reported_not_scored={
                'A27_above_host_valence_edge': {k: a27.get(k) for k in ('value_eV', 'lower_bound_eV', 'gt_0p3')},
                'A23_band_index_above_Nv': {k: a23.get(k) for k in ('value_eV', 'lower_bound_eV', 'gt_0p3')}},
            domain_sensitive=len({hist.get('gt_0p3'), a27.get('gt_0p3'), a23.get('gt_0p3')}) > 1)
        lumo = c.e[c.lowest_above] if c.lowest_above is not None else None
        if hist.get('W_state') and lumo is not None:
            out['forecast_W_state_minus_LUMO_eV'] = {'value_eV': hist['W_state']['E_eV'] - float(lumo),
                                                     'forecast': f'>= {R.HG_W_ABOVE_LUMO_EV} eV (Claude)',
                                                     'LUMO': 'lowest state with n > N_v'}
        hs = c.host_edge.get('state')
        out['claude_host_edge_state_W5d'] = dict(status(None if hs is None else R.le(hs['W5d'], R.HG_HOST_EDGE_W5D_MAX),
                                                        base + c.host_edge['unresolved'], qual),
                                                 value=None if hs is None else hs['W5d'],
                                                 threshold=R.HG_HOST_EDGE_W5D_MAX)
    if is_w and not comp:
        fr = excess_fractions(c)
        r2 = base + fr.get('unresolved', [])
        if fr.get('f_ext_bounds') and R.ge(fr['f_ext_bounds'][0], R.HG_FEXT) != R.ge(fr['f_ext_bounds'][1], R.HG_FEXT):
            r2.append('f_ext >= 0.80 rests on flagged states (completeness < 0.90)')
        out['P2_f_ext'] = dict(status(None if fr.get('f_ext') is None else R.ge(fr['f_ext'], R.HG_FEXT), r2, qual),
                               value=fr.get('f_ext'), threshold=R.HG_FEXT, bounds=fr.get('f_ext_bounds'))
        out['forecast_f_W5d'] = {'value': fr.get('f_W5d'), 'forecast': f'<= {R.HG_FW5D_FORECAST}'}
        if c.E_c is not None:
            out['forecast_E_F_minus_host_edge_eV'] = {'value': [float(x - c.E_c) for x in c.data.ef],
                                                      'forecast': list(R.HG_EF_FORECAST_EV)}
    if comp:
        g = gap_search(c, lo=c.E_v, hi=c.E_c, include_lo=False, occupied=True, weight_key='W5d',
                       label='H-G compensated cell: occupied (>= 0.01 e) localised W-5d state in the gap')
        r3 = base + g['unresolved'] + [f'host edge: {r}' for r in c.host_edge['unresolved']] + \
            [f'host valence edge: {r}' for r in c.host_valence_edge['unresolved']]
        out['P3_comp_no_occupied_localised_W_state_in_gap'] = dict(
            status(None if 'n_qualifying' not in g else g['n_qualifying'] == 0, r3, qual), search=g)
    if c.E_c is not None and c.E_v is not None:
        out['E_g_host_eV'] = c.E_c - c.E_v
        out['E_g_host_unresolved'] = c.host_edge['unresolved'] + c.host_valence_edge['unresolved'] + list(c.reasons)
    out['scope'] = ('Neutral, spin-unpolarised PBE cells without +U can show consistency with donor behaviour; they '
                    'cannot establish full ionisation or charge-transition levels (H-G scope).')
    return out


def hh_cell(c):
    """H-H per cell: occupied (>= 0.01 e) localised states with >= 30 % surface weight within 0.3 eV below the host
    edge; the host edge and the host valence reference must both be resolved."""
    lo = None if c.E_c is None else c.E_c - R.GAPSTATE_WINDOW_EV
    g = gap_search(c, lo=lo, hi=c.E_c, include_lo=True, occupied=True, weight_key='surface',
                   label='H-H: occupied (>= 0.01 e) localised surface state within 0.3 eV below the host edge')
    g['unresolved'] += _references(c) + list(c.reasons)
    return g


def _references(c):
    """Unresolved host edge / host valence reference of a gap search (rc4: the valence reference gates the window)."""
    out = [f'host edge: {r}' for r in c.host_edge['unresolved']]
    if c.E_v is None:
        out.append('host valence reference missing (no qualifying state at or below N_v)')
    out += [f'host valence edge: {r}' for r in c.host_valence_edge['unresolved'] if c.E_v is not None]
    return out


def hi_cell(c):
    """H-I per cell: localised interface states (A24 weight, outer face excluded) of ANY occupation (frozen
    interpretation, IMPLEMENTATION_CHOICES['HI_occupation']) within 0.3 eV below the host edge; states with >= 30 % on
    the outer face are reported separately as outer-face states; host edge and valence reference must be resolved."""
    lo = None if c.E_c is None else c.E_c - R.GAPSTATE_WINDOW_EV
    g = gap_search(c, lo=lo, hi=c.E_c, include_lo=True, occupied=False, weight_key='interface',
                   label='H-I: localised interface state (any occupation) within 0.3 eV below the host edge')
    g['unresolved'] += _references(c) + list(c.reasons)
    if c.mode == 'interface':
        o = gap_search(c, lo=lo, hi=c.E_c, include_lo=True, occupied=False, weight_key='outer_face',
                       label='A24 outer-face states (reported, not interface states)')
        g['outer_face_states'] = o
        # A24: 'a state with >= 30 % weight on the outer face is reported as an outer-face state, not an interface
        # state' -> remove those from the interface list
        ids = {(x['spin'], x['k'], x['band']) for x in o.get('qualifying', [])}
        if 'qualifying' in g:
            g['qualifying'] = [x for x in g['qualifying'] if (x['spin'], x['k'], x['band']) not in ids]
            g['n_qualifying'] = len(g['qualifying'])
            g['n_removed_as_outer_face_states'] = len(ids)
    return g
