"""Tests of s3_decision_a49.py (register A49): decision logic, pure shift/scale rule, form mapping, roles and pins. Synthetic rows only;
no run directory, no RUN_INDEX row and no measured curve is read.

    & "<venv>\\Scripts\\python.exe" -I -B analysis_2026-10-10_campaign/test_s3_decision_a49.py
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('s3d', HERE / 's3_decision_a49.py'); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)


def row(name, group, sq, arith='ARITHMETIC PASS (also required ...)', conv=True, act=True, pure=False, form=None, g0=None):
    return {'name': name, 'group': group, 'sqrtJ_dec': sq, 'arithmetic': arith, 'converged': conv, 'activation_ok': act,
            'pure_shift_or_scale': pure, 'form': form or ('igzo' if group == 'mobility' else 'bulk'), 'g0': g0}


def prof(vals):
    return {'diagnostic_shape_only': {t: {'shape_only_sqrtJ_dec': v} for t, v in zip(S.FILMS, vals)}}


CASES = []


def case(f): CASES.append(f); return f


@case
def nothing_passes():
    rows = [row('b', 'tail', 0.5, arith='ARITHMETIC FAIL (...)'), row('i', 'mobility', 0.4, arith='ARITHMETIC FAIL (...)', g0=-0.31)]
    f = S.s4a_form(S.decide(rows))
    return f['form'] == 'N' and f['launches'] == 42 and f['lhs'].startswith('2-D seed 20261010'), f


@case
def unverified_is_not_a_pass():
    rows = [row('i', 'mobility', 0.1, arith='UNVERIFIED: ARITHMETIC PASS (...)', g0=-0.31)]
    return S.s4a_form(S.decide(rows))['form'] == 'N', 'UNVERIFIED prefix accepted'


@case
def approximate_is_not_a_pass():
    rows = [row('i', 'mobility', 0.1, arith='APPROXIMATE: ARITHMETIC PASS (...)', g0=-0.31)]
    return S.s4a_form(S.decide(rows))['form'] == 'N', 'APPROXIMATE prefix accepted'


@case
def flags_must_be_established():
    for kw in ({'conv': False}, {'conv': None}, {'act': False}, {'act': None}, {'pure': True}, {'pure': None}):
        if S.decide([row('b', 'tail', 0.2, **kw)])['tail'] is not None: return False, f'accepted with {kw}'
    return True, ''


@case
def tail_lowest_sqrtj():
    rows = [row('bulk', 'tail', 0.40, form='bulk'), row('half', 'tail', 0.35, form='mixed50')]
    c = S.decide(rows); f = S.s4a_form(c)
    return c['tail']['name'] == 'half' and f['form'] == 'T' and f['tail_law'] == 'mixed50' and f['launches'] == 43, f


@case
def igzo_better_gamma0_seeds():
    rows = [row('m031', 'mobility', 0.40, g0=-0.31), row('p030', 'mobility', 0.30, g0=0.30)]
    f = S.s4a_form(S.decide(rows))
    return f['form'] == 'I' and f['gamma0_seed'] == 0.30 and f['lhs'].startswith('3-D seed 20261011') and f['launches'] == 42, f


@case
def both_groups():
    rows = [row('bulk', 'tail', 0.40, form='bulk'), row('m031', 'mobility', 0.30, g0=-0.31)]
    f = S.s4a_form(S.decide(rows))
    return f['form'] == 'TI' and f['launches'] == 45 and f['tail_law'] == 'bulk' and f['gamma0_seed'] == -0.31, f


@case
def failing_member_does_not_block_other():
    rows = [row('m031', 'mobility', 0.20, arith='ARITHMETIC FAIL', g0=-0.31), row('p030', 'mobility', 0.30, g0=0.30)]
    c = S.decide(rows)
    return c['mobility']['name'] == 'p030', c


@case
def unknown_group_refused():
    try: S.decide([row('x', 'contacts', 0.1)]); return False, 'accepted a contacts row'
    except SystemExit: return True, ''


@case
def pure_rule():
    p1, d1 = S.pure_shift_or_scale(prof([0.20, 0.30, 0.10]), prof([0.205, 0.295, 0.10]))
    p2, d2 = S.pure_shift_or_scale(prof([0.20, 0.30, 0.10]), prof([0.20, 0.25, 0.10]))
    p3, _ = S.pure_shift_or_scale({'diagnostic_shape_only': {2.0: {'shape_only_sqrtJ_dec': 0.1}}}, prof([0.1, 0.1, 0.1]))
    p4, _ = S.pure_shift_or_scale(prof([0.20, 0.30, 0.10]), {'diagnostic_shape_only': {str(t): {'shape_only_sqrtJ_dec': v} for t, v in zip(S.FILMS, (0.2, 0.3, 0.1))}})
    return p1 is True and p2 is False and p3 is None and p4 is True, (p1, d1, p2, d2, p3, p4)


@case
def roles_match_frozen_roles():
    """the role table agrees with the frozen H-F v4 roles and the profile_s4s5 confirmation roles (labels and films), read as text"""
    hf = (HERE / 'hf_score_draft.py').read_text(); ps4 = (HERE / 'profile_s4s5.py').read_text()
    bad = []
    for k in ('S0-01', 'S1-01', 'S1-02', 'S3-10', 'S3-11', 'S3-12', 'S3-13'):
        rid, lab, t = S.ROLE[k]
        if f"'{k}': ('{lab}', {t})" not in hf: bad.append(k)
    for k in ('c10_s1_07_2p0', 'c10_s0_01_2p0', 'c10_s3_27_6p3', 'c10_s3_12_6p3'):
        if k not in ps4: bad.append(k)
    labs = {lab for _, lab, _ in S.ROLE.values()}
    ok = not bad and len(labs) == len(S.ROLE) and all(S.ROLE[k][1].endswith(S.TAG[S.ROLE[k][2]]) for k in S.ROLE)
    return ok, bad


@case
def branch_triples_cover_films():
    bad = [b['name'] for b in S.BRANCHES if [S.ROLE[k][2] for k in b['roles']] != list(S.FILMS)]
    return not bad and [S.ROLE[k][2] for k in S.BASE] == list(S.FILMS), bad


@case
def pins_detect_change():
    orig = dict(S.PINS); S.PINS['profile_shared.py'] = '0' * 64
    try: bad = S.check_pins()
    finally: S.PINS.clear(); S.PINS.update(orig)
    return len(bad) == 1 and bad[0].startswith('profile_shared.py'), bad


@case
def pins_match_now():
    bad = S.check_pins(); return not bad, bad


def main():
    n = 0
    for f in CASES:
        try: ok, why = f()
        except Exception as e: ok, why = False, f'{type(e).__name__}: {e}'
        print(f'[{"PASS" if ok else "FAIL"}] {f.__name__}' + ('' if ok else f'  {why}')); n += bool(ok)
    print(f'{n}/{len(CASES)} passed'); return 0 if n == len(CASES) else 1


if __name__ == '__main__':
    sys.exit(main())
