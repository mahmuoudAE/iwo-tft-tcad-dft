"""Read-only numerical gates for independent rebuild runs; never launches ATLAS.

The sole output is the requested JSON outside the source run directories.
Numerical PASS is not a calibrated-model or measurement-fit claim.
"""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

import numpy as np
from rebuild_model import render

ROOT = Path(__file__).resolve().parents[1]
LIMITS = dict(active_max_log10_decades=.01, ion_relative=.01,
              low_absolute_A_per_um=1e-18, low_relative=.01,
              kcl_absolute_A_per_um=1e-18, kcl_relative=.01,
              export_relative=5.1e-6, export_absolute=1e-30)
DATA = {key: 'data/iwo_' + key + 'nm.csv' for key in ('2p0', '6p3', '13p2', '31p8')}
EXPORT_COLUMNS = {'igvg.dat': 2, 'isvg.dat': 5, 'idvg.dat': 8,
                  'vsvg.dat': 3, 'vdvg.dat': 6, 'mobility_vg.dat': 9,
                  'electrons_vg.dat': 10}
PRPMOB_EXTRA = ('channel_ey', 'front_mobility', 'front_ey', 'back_mobility', 'back_ey')
TRAP_CHARGE_EXTRA = ('bulk_free_electrons', 'bulk_ionized_acceptors', 'bulk_ionized_donors')
DEPTH_ELECTRON_EXTRA = ('bulk_front_electrons', 'bulk_back_electrons')
ALLOWED_EXTRA_SCHEMAS = tuple(
    mobility + charge + depth
    for mobility in ((), PRPMOB_EXTRA)
    for charge in ((), TRAP_CHARGE_EXTRA)
    for depth in ((), DEPTH_ELECTRON_EXTRA))
CONTROLS = {'width': {'geometry.simulation_width_um'},
            'contact_length': {'geometry.contact_length_um'},
            'xmesh': {'numerics.x_spacing_um', 'numerics.contact_edge_spacing_um'},
            'ymesh': {'numerics.channel_intervals', 'numerics.alumina_intervals',
                      'numerics.hafnia_intervals'},
            'dos': {'defects.bulk_levels_a', 'defects.bulk_levels_d',
                    'defects.interface_levels_a', 'defects.interface_levels_d'}}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def table(path):
    with Path(path).open(newline='', encoding='utf-8-sig') as handle:
        return list(csv.DictReader(handle))


def commands(deck):
    joined = re.sub(r'\\\s*\n\s*', ' ', deck)
    return [' '.join(line.split()).lower() for line in joined.splitlines()
            if line.strip() and not line.lstrip().startswith('#')]


def align(a, targets, name):
    if a.ndim != 2 or len(a) < 3 or not np.isfinite(a).all():
        raise ValueError('Missing/nonfinite numeric rows: ' + name)
    if np.any(np.diff(a[:, 0]) < -1e-9):
        raise ValueError('Reverse/nonmonotonic gate sweep: ' + name)
    # Repeated solves at the same bias are retained last, never interpolated.
    unique = {row[0]: row for row in a}
    final = np.array(list(unique.values()))
    ix = np.argmin(abs(final[:, 0, None] - targets[None, :]), axis=0)
    if len(set(ix)) != len(targets) or np.any(abs(final[ix, 0] - targets) > 1e-6):
        raise ValueError('Missing original measurement gate point: ' + name)
    return final[ix]


def raw_xy(path, targets):
    rows = []
    for line in path.read_text(errors='strict').splitlines():
        words = line.replace(',', ' ').split()
        if len(words) != 2:
            continue
        try:
            rows.append([float(x.replace('D', 'E').replace('d', 'e')) for x in words])
        except ValueError:
            continue
    return align(np.asarray(rows), targets, path.name)[:, 1]


def expected_extras(cfg):
    extra = PRPMOB_EXTRA if cfg['transport']['mode'] == 'prpmob' else ()
    for flag, names in [('trap_charge', TRAP_CHARGE_EXTRA), ('depth_electrons', DEPTH_ELECTRON_EXTRA)]:
        enabled = cfg.get('diagnostics', {}).get(flag, False)
        if not isinstance(enabled, bool):
            raise ValueError('diagnostics.' + flag + ' must be a boolean')
        if enabled:
            extra += names
    return extra


def native_export_columns(cfg):
    columns = dict(EXPORT_COLUMNS)
    columns.update({name + '_vg.dat': 11 + index for index, name in enumerate(expected_extras(cfg))})
    if cfg['contacts'].get('resistance_ohm_um', 0) > 0:
        columns.update({'source_internal_vg.dat': 4, 'drain_internal_vg.dat': 7})
    return columns


def native_log(path, targets, expected_extra=()):
    expected_extra = tuple(expected_extra)
    if expected_extra not in ALLOWED_EXTRA_SCHEMAS:
        raise ValueError('Unsupported requested native probe schema')
    lines = path.read_text(errors='strict').splitlines()
    names = [s for s in lines if s.startswith('f ')]
    columns = [s.split()[1:] for s in lines if s.startswith('p ')]
    probes = [s.split()[1:] for s in lines if s.startswith('o ')]
    expected_names = ('channel_mobility', 'channel_electrons') + expected_extra
    expected_columns = [str(9 + len(expected_names)), '2', '601', '20', '3', '602', '21', '4', '603', '22']
    expected_columns += [str(3000 + index) for index in range(len(expected_names))]
    if (len(names) != 1 or re.findall(r'"([^"]+)"', names[0]) != ['gate', 'source', 'drain']
            or columns != [expected_columns]
            or probes != [[str(index), name] for index, name in enumerate(expected_names, start=1)]):
        raise ValueError('Unsupported native terminal/probe column layout')
    rows = np.array([[float(x.replace('D', 'E').replace('d', 'e')) for x in s.split()[1:]]
                     for s in lines if s.startswith('d ')])
    if rows.ndim != 2 or rows.shape[1] != 9 + len(expected_names):
        raise ValueError('Malformed native terminal/probe rows')
    selected = align(rows, targets, path.name)
    for name in DEPTH_ELECTRON_EXTRA:
        if name in expected_names and np.any(rows[:, 9 + expected_names.index(name)] < 0):
            raise ValueError('Negative native depth electron concentration: ' + name)
    return selected, rows


def flatten(value, prefix=''):
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            result.update(flatten(child, prefix + '.' + key if prefix else key))
        return result
    return {prefix: value}


def load_run(folder):
    """Recompute gates from execution-hashed native evidence, without writing."""
    folder = Path(folder).resolve()
    if not folder.is_relative_to(ROOT):
        raise ValueError('Run evidence must remain inside the project')
    execution = read_json(folder / 'execution.json')
    cfg = read_json(folder / 'input_config.json')
    if execution.get('event') != 'finish' or execution.get('returncode') != 0:
        raise ValueError('Run did not finish successfully')
    if execution.get('actual_started_simulator_stages') != ['atlas']:
        raise ValueError('Expected one actually started ATLAS stage')
    if execution.get('deck_sha256') != sha(folder / 'device.in'):
        raise ValueError('Input deck hash mismatch')
    if execution.get('config_sha256') != sha(folder / 'input_config.json'):
        raise ValueError('Input config hash mismatch')
    hashes = execution.get('outputs')
    extra = expected_extras(cfg)
    export_columns = native_export_columns(cfg)
    required = {'deckbuild.out', 'transfer.log', 'geometry.str', 'equilibrium.str', 'off.str', 'final.str'} | set(export_columns)
    if cfg['defects']['bulk']:
        required |= {'bulk_acceptor.dat', 'bulk_donor.dat'}
    if cfg['defects']['interface']:
        required |= {'interface_acceptor.dat', 'interface_donor.dat', 'interface_dos.dat'}
    if not isinstance(hashes, dict) or required - hashes.keys():
        raise ValueError('Required native evidence missing from execution hash manifest')
    for name, expected in hashes.items():
        path = (folder / name).resolve()
        if not path.is_relative_to(folder) or not path.is_file() or sha(path) != expected:
            raise ValueError('Execution output missing or changed: ' + name)
    if any((folder / name).stat().st_size == 0 for name in required):
        raise ValueError('Required native evidence is empty')
    output = (folder / 'deckbuild.out').read_text(errors='replace')
    if not re.search(r'ATLAS version .* finished', output):
        raise ValueError('Missing native ATLAS completion banner')
    if re.findall(r'Version:\s*(atlas|athena)\s+[0-9]', output, re.I) != ['atlas']:
        raise ValueError('Actual raw simulator stages differ from execution record')
    # Recovered TRAP step reductions are permitted only because completion,
    # every original target, native bias and signed KCL are checked below.
    # An exhausted retry or parser/license error is never a recovered solve.
    if re.search(r'Error:|Error\s*#|invalid parameter|unknown parameter|Cannot trap|'
                 r'Could not trap|Cannot reduce bias|fatal error|license.*(?:denied|failed)', output, re.I):
        raise ValueError('Raw simulator parser/convergence/license failure')
    warnings = re.findall(r'^.*Warning:.*$', output, re.M | re.I)
    recovered_steps = len(re.findall(r'Warning:\s*Convergence problem\.\s*Taking smaller bias', output, re.I))
    grid_counts = re.findall(r'Total grid points\s*:\s*(\d+)', output)
    triangle_counts = re.findall(r'Total triangles\s*:\s*(\d+)', output)
    if len(grid_counts) != 1 or len(triangle_counts) != 1 or min(int(grid_counts[0]), int(triangle_counts[0])) <= 0:
        raise ValueError('Missing/unverified native realized mesh counts')
    realized_mesh = dict(grid_points=int(grid_counts[0]), triangles=int(triangle_counts[0]))
    if cfg.get('electrical_domain') != 'screened_active_stack':
        raise ValueError('Only the rebuilt three-terminal screened active stack is supported')

    entries = table(folder / 'comparison_all_measurements.csv')
    vg = np.array([float(r['vg_V']) for r in entries])
    measured = np.array([float(r['measured_A_per_um']) for r in entries])
    reported = np.array([float(r['atlas_signed_A_per_um']) for r in entries])
    if len(vg) != 121 or not np.isfinite([vg, measured, reported]).all() or (measured <= 0).any():
        raise ValueError('Need all 121 finite original measurement/comparison points')
    manifest = read_json(ROOT / 'MANIFEST_SHA256.json')
    matching = []
    for key, relative in DATA.items():
        path = ROOT / relative
        if sha(path) != manifest.get(relative):
            raise ValueError('Original measurement CSV changed: ' + relative)
        original = table(path)
        mv = np.array([float(r['vg_V']) for r in original])
        mi = np.array([float(r['id_A_per_um']) for r in original])
        if np.array_equal(vg, mv) and np.array_equal(measured, mi):
            matching.append(key)
    if len(matching) != 1:
        raise ValueError('Comparison differs from the complete original measured series')
    key = matching[0]
    if (ROOT / cfg['curves'][key]['data']).resolve() != (ROOT / DATA[key]).resolve():
        raise ValueError('Config measurement source differs from the original target')
    if not np.allclose(vg, np.linspace(-3, 3, 121), rtol=0, atol=1e-9):
        raise ValueError('Original gate grid is not the expected 121 points')
    deck = (folder / 'device.in').read_text()
    regenerated, _ = render(cfg, key, plots=False)
    if commands(deck) != commands(regenerated):
        raise ValueError('Actual executable deck differs from regeneration using saved config')
    width = float(cfg['geometry']['simulation_width_um'])
    if not np.isfinite(width) or width <= 0:
        raise ValueError('Invalid simulated width')
    native, all_native = native_log(folder / 'transfer.log', vg, extra)
    exports = {name: raw_xy(folder / name, vg) for name in export_columns}
    for name, column in export_columns.items():
        delta = abs(exports[name] - native[:, column])
        if np.any(delta > LIMITS['export_relative'] * abs(native[:, column]) + LIMITS['export_absolute']):
            raise ValueError('Native log and signed EXTRACT disagree: ' + name)
    if not np.allclose(exports['idvg.dat'] / width, reported, rtol=1e-12, atol=1e-40):
        raise ValueError('Reported drain comparison differs from signed EXTRACT / width')
    off = np.median(measured[(vg >= -2) & (vg <= -.5)])
    active = measured > 5 * off if key != '31p8' else np.ones(len(vg), bool)
    for name, expected in [('active', active), ('low_current', ~active)]:
        if not np.array_equal([r[name].lower() == 'true' for r in entries], expected):
            raise ValueError('Reported comparison mask differs from measured-only definition')
    for name, expected in [('linear_residual_A_per_um', reported - measured),
                           ('log10_magnitude_residual', np.log10(np.maximum(abs(reported), 1e-40) / measured))]:
        if not np.allclose([float(r[name]) for r in entries], expected, rtol=1e-10, atol=1e-28):
            raise ValueError('Reported residual does not recompute: ' + name)

    terminal = {name: native[:, column] / width for name, column in [('ig', 2), ('is', 5), ('id', 8)]}
    every_current = all_native[:, [2, 5, 8]] / width
    kcl = every_current.sum(axis=1)
    bound = LIMITS['kcl_absolute_A_per_um'] + LIMITS['kcl_relative'] * abs(every_current).sum(axis=1)
    kcl_pass = bool(np.all(abs(kcl) <= bound))
    bias_pass = bool(np.allclose(all_native[:, 6], cfg['shared']['vd_V'], rtol=0, atol=1e-8)
                     and np.allclose(all_native[:, 3], 0, rtol=0, atol=1e-8))
    positive_probe_columns = [('channel_mobility', 9), ('channel_electrons', 10)]
    if cfg['transport']['mode'] == 'prpmob':
        positive_probe_columns += [('front_mobility', 12), ('back_mobility', 14)]
    probes = {name: {'positive_at_all_active_points': bool(np.all(native[active, column] > 0)),
                     'nonpositive_active_points': int((native[active, column] <= 0).sum()),
                     'minimum': float(native[:, column].min()), 'maximum': float(native[:, column].max())}
              for name, column in positive_probe_columns}
    probe_pass = all(p['positive_at_all_active_points'] for p in probes.values())
    sign_pass = bool(np.all(terminal['id'][active] > 0))
    summary = dict(run_id=execution['run_id'], directory=str(folder), key=key, width_um=width,
                   gate_points=len(vg), native_rows=len(all_native), active_points=int(active.sum()),
                   realized_mesh=realized_mesh,
                   raw_warning_lines=warnings, recovered_bias_reductions=recovered_steps,
                   recovered_step_policy='Allowed only with completion, all 121 targets, correct native biases and all-row signed KCL; exhausted retry/errors rejected.',
                   kcl_recomputed_pass=kcl_pass, kcl_failed_native_points=int((abs(kcl) > bound).sum()),
                   max_kcl_A_per_um=float(max(abs(kcl))), terminal_voltages_recomputed_pass=bias_pass,
                   native_probes=probes, native_probes_pass=probe_pass, active_signed_drain_positive=sign_pass,
                   native_extra_probes={name: {'minimum': float(native[:, 11+index].min()),
                                               'maximum': float(native[:, 11+index].max())}
                                        for index, name in enumerate(extra)},
                   drain_signs={'positive': int((terminal['id'] > 0).sum()), 'zero': int((terminal['id'] == 0).sum()),
                                'negative': int((terminal['id'] < 0).sum())},
                   measurement_sha256=sha(ROOT / DATA[key]),
                   evidence_sha256={name: sha(folder / name) for name in
                                    ['execution.json', 'device.in', 'input_config.json', 'comparison_all_measurements.csv']},
                   raw_output_sha256=hashes,
                   run_acceptable=bool(kcl_pass and bias_pass and probe_pass and sign_pass))
    return dict(cfg=cfg, key=key, deck=deck, vg=vg, measured=measured, active=active, low=~active,
                terminal=terminal, summary=summary)


def design_check(reference, candidate, kind):
    a, b = flatten(reference['cfg']), flatten(candidate['cfg'])
    missing = object()
    changed = {k: [a.get(k), b.get(k)] for k in sorted(set(a) | set(b))
               if a.get(k, missing) != b.get(k, missing)}
    allowed = CONTROLS[kind]
    valid = bool(changed) and not (set(changed) - allowed)
    valid = valid and reference['key'] == candidate['key']
    if kind == 'width':
        valid = valid and b['geometry.simulation_width_um'] > a['geometry.simulation_width_um'] > 0
    elif kind == 'contact_length':
        old, new = a['geometry.contact_length_um'], b['geometry.contact_length_um']
        valid = valid and np.isfinite([old, new]).all() and min(old, new) > 0 and old != new
        valid = valid and a['geometry.channel_length_um'] == b['geometry.channel_length_um'] == 20
    elif kind == 'xmesh':
        valid = valid and all(0 < b[k] <= a[k] for k in allowed)
    else:
        valid = valid and all(isinstance(b[k], int) and not isinstance(b[k], bool)
                              and b[k] >= a[k] > 0 for k in allowed)
    levels = []
    if kind == 'dos':
        c, d = reference['cfg']['curves'][reference['key']], reference['cfg']['defects']
        populations = {'bulk_levels_a': d['bulk'] and (c['nta_cm3_eV'] > 0 or c['nga_cm3_eV'] > 0),
                       'bulk_levels_d': d['bulk'] and c['ngd_cm3_eV'] > 0,
                       'interface_levels_a': d['interface'] and c['interface_peak_cm2_eV'] > 0,
                       'interface_levels_d': False}
        for name, enabled in populations.items():
            old, new = a['defects.' + name], b['defects.' + name]
            levels.append(dict(control=name, enabled=bool(enabled), reference=old, candidate=new))
            valid = valid and (new >= 2 * old if enabled else new >= old)
        valid = valid and any(populations.values())
    before, after = commands(reference['deck']), commands(candidate['deck'])

    def unchanged_physics(lines):
        result = []
        for line in lines:
            if kind == 'xmesh' and line.startswith('x.mesh '):
                continue
            if kind == 'ymesh' and line.startswith('y.mesh '):
                continue
            if kind == 'width' and line.startswith('mesh '):
                line = re.sub(r'\bwidth=[-+\d.e]+', 'width=CHECK', line)
            if kind == 'dos' and line.startswith(('defects ', 'intdefects ')):
                line = re.sub(r'\b(numa|numd)=[-+\d.e]+', r'\1=CHECK', line)
            result.append(line)
        return result

    regenerated_contact_commands_match = None
    if kind == 'contact_length':
        # Contact overlap changes dependent x boundaries, mesh lines, probe
        # locations and averaging boxes. Verify all those commands against
        # the generator rather than masking arbitrary geometry text away.
        try:
            ref_deck, _ = render(reference['cfg'], reference['key'], plots=False)
            cand_deck, _ = render(candidate['cfg'], candidate['key'], plots=False)
            regenerated_contact_commands_match = before == commands(ref_deck) and after == commands(cand_deck)
        except (ValueError, KeyError, TypeError):
            regenerated_contact_commands_match = False
        valid = valid and before != after and regenerated_contact_commands_match
    else:
        valid = valid and before != after and unchanged_physics(before) == unchanged_physics(after)
    mesh_check = None
    if kind in ('xmesh', 'ymesh'):
        old, new = reference['summary']['realized_mesh'], candidate['summary']['realized_mesh']
        mesh_check = dict(reference=old, candidate=new,
                          pass_check=bool(new['grid_points'] > old['grid_points'] and new['triangles'] > old['triangles']))
        valid = valid and mesh_check['pass_check']
    return dict(pass_check=bool(valid), changed_config=changed, dos_populations=levels,
                realized_mesh_refinement=mesh_check,
                regenerated_contact_commands_match=regenerated_contact_commands_match,
                reason=('Only contact overlap length may change; channel length remains 20 um and all derived deck commands must match saved configs.'
                        if kind == 'contact_length' else
                        'Require isolated requested control change, distinct actual commands, refinement direction, and doubling of every enabled DOS population.'))


def compare(reference, candidate, kind):
    if not np.array_equal(reference['vg'], candidate['vg']) or not np.array_equal(reference['measured'], candidate['measured']):
        raise ValueError('Comparison does not use the same original measurement series')
    design = design_check(reference, candidate, kind)
    active, low = reference['active'], reference['low']
    first, second = reference['terminal']['id'], candidate['terminal']['id']
    positive = bool((first[active] > 0).all() and (second[active] > 0).all())
    maxlog = float(max(abs(np.log10(second[active]) - np.log10(first[active])))) if positive else None
    ion = float(abs(second[-1] / first[-1] - 1)) if min(first[-1], second[-1]) > 0 else None
    lows = {}
    for name in reference['terminal']:
        a, b = reference['terminal'][name], candidate['terminal'][name]
        delta = abs(a - b)
        bound = LIMITS['low_absolute_A_per_um'] + LIMITS['low_relative'] * (abs(a) + abs(b))
        lows[name] = dict(points=int(low.sum()), pass_check=bool(np.all(delta[low] <= bound[low])),
                          failed_points=int((delta[low] > bound[low]).sum()),
                          max_absolute_difference_A_per_um=float(max(delta[low])) if low.any() else None,
                          low_sign_changes=int((np.sign(a[low]) != np.sign(b[low])).sum()))
    passed = (reference['summary']['run_acceptable'] and candidate['summary']['run_acceptable']
              and design['pass_check'] and positive and maxlog <= LIMITS['active_max_log10_decades']
              and ion is not None and ion <= LIMITS['ion_relative'] and all(x['pass_check'] for x in lows.values()))
    return dict(status='PASS' if passed else 'FAIL', pass_check=bool(passed), design=design,
                candidate=candidate['summary'], active_max_log10_difference_decades=maxlog,
                ion_relative_difference=ion, low_current_signed_terminal_comparison=lows,
                all_point_signed_drain_linear_rmse_A_per_um=float(np.sqrt(np.mean((first-second)**2))))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reference', 'width', 'xmesh', 'ymesh'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--dos', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.out.resolve()
    if not out.is_relative_to(ROOT) or out.suffix.lower() != '.json':
        parser.error('--out must be a JSON path inside the project')
    if out.exists():
        parser.error('--out must be new; existing numerical certificates are preserved')
    if out.is_relative_to((ROOT / 'results/local_session_20260910/runs').resolve()):
        parser.error('--out must stay outside the reserved raw-run namespace')
    paths = [getattr(args, n) for n in ('reference', 'width', 'xmesh', 'ymesh', 'dos')]
    if any(p is not None and out.is_relative_to(p.resolve()) for p in paths):
        parser.error('--out must be outside all source run directories')
    if any((parent / 'execution.json').is_file() for parent in out.parents if parent.is_relative_to(ROOT)):
        parser.error('--out cannot overwrite evidence in any existing run directory')
    result = dict(status='INCOMPLETE', all_required_checks_passed=False, thresholds=LIMITS,
                  calibration_eligible=False, measurement_fit_validated=False, checks={},
                  note='Numerical acceptance only. Native raw evidence is rechecked; no simulator runs or measurement fits are produced. A trap-disabled DOS N/A does not validate later trap-enabled models.',
                  mask_definition='Measured I > 5*median(-2<=VG<=-0.5), except 31.8 nm all active; low is complement, not a detection limit.')
    try:
        reference = load_run(args.reference)
        result['reference'] = reference['summary']
    except Exception as exc:
        reference = None
        result['reference_error'] = str(exc)
    for name in ('width', 'xmesh', 'ymesh', 'dos'):
        path = getattr(args, name)
        if reference is None:
            result['checks'][name] = dict(status='BLOCKED_BY_REFERENCE', pass_check=False)
        elif name == 'dos' and not reference['cfg']['defects']['bulk'] and not reference['cfg']['defects']['interface']:
            result['checks'][name] = dict(status='N/A', pass_check=True, applies=False,
                                          reason='Both native trap families disabled in this reference; no DOS convergence claim.',
                                          supplied_candidate_unused=path is not None)
        elif path is None:
            result['checks'][name] = dict(status='MISSING', pass_check=False)
        else:
            try:
                result['checks'][name] = compare(reference, load_run(path), name)
            except Exception as exc:
                result['checks'][name] = dict(status='INVALID_EVIDENCE', pass_check=False, error=str(exc))
    complete = reference is not None and reference['summary']['run_acceptable'] and all(v['pass_check'] for v in result['checks'].values())
    result['all_required_checks_passed'] = bool(complete)
    if complete:
        result['status'] = 'PASS'
    elif reference is None or all(c['status'] != 'MISSING' for c in result['checks'].values()):
        result['status'] = 'FAIL'
    out.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also preserves a certificate created by another writer
    # while this read-only comparison was checking native evidence.
    try:
        with out.open('x', encoding='utf-8') as handle:
            handle.write(json.dumps(result, indent=2, allow_nan=False))
    except FileExistsError:
        parser.error('--out already exists; existing numerical certificates are preserved')
    print(json.dumps(dict(status=result['status'], all_required_checks_passed=bool(complete), output=str(out))))
    return 0 if complete else 2


if __name__ == '__main__':
    raise SystemExit(main())
