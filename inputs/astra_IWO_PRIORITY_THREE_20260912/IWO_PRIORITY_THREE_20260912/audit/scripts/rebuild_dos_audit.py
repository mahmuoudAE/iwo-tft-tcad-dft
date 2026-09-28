"""Read native ATLAS DOS exports; write a separate capacity/parameter audit.

No simulator is launched and raw run files are never changed. AFILE acceptor
energies are below Ec, DFILE donor energies above Ev, and combined TFILE
energies above Ev. No trap occupation is present in these DOS exports.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shlex

ROOT = Path(__file__).resolve().parents[1]
AUDITS = ROOT / 'results' / 'rebuild_20260912' / 'dos_audits'
SIGNATURES = {
    ('bulk', 'a'): [74, 76, 75, 205],
    ('bulk', 'd'): [77, 79, 78, 206],
    ('bulk', 't'): [210, 76, 75, 205, 79, 78, 206],
    ('interface', 'a'): [74, 301, 300, 302],
    ('interface', 'd'): [77, 304, 303, 305],
    ('interface', 't'): [210, 301, 300, 302, 304, 303, 305],
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside_project(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f'Path must stay inside project: {path}')
    return path


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def commands(path):
    """Read only DOS statements; never evaluate DeckBuild expressions."""
    joined = []
    pending = ''
    for line in path.read_text(errors='replace').splitlines():
        line = line.split('#', 1)[0].strip()
        if not line:
            continue
        continuation = line.endswith('\\')
        pending += ' ' + (line[:-1] if continuation else line)
        if not continuation:
            joined.append(pending.strip())
            pending = ''
    result = {'bulk': [], 'interface': []}
    for line in joined:
        tokens = shlex.split(line)
        if not tokens or tokens[0].lower() not in ('defects', 'intdefects'):
            continue
        kind = 'bulk' if tokens[0].lower() == 'defects' else 'interface'
        values = {}
        for token in tokens[1:]:
            key, sep, value = token.partition('=')
            values[key.lower()] = value if sep else True
        result[kind].append(values)
    return result


def expected_config(cfg, key):
    c, s = cfg['curves'][key], cfg['shared']
    eg = float(s['eg_eV'])
    if 'defects' in cfg:
        d = cfg['defects']
        bulk = dict(enabled=d['bulk'], numa=d['bulk_levels_a'], numd=d['bulk_levels_d'],
                    nta=c['nta_cm3_eV'], wta=c['wta_eV'], ntd=0, wtd=.1,
                    nga=c['nga_cm3_eV'], ega=c['ega_eV_below_Ec'], wga=c['wga_eV'],
                    ngd=c['ngd_cm3_eV'], egd=eg-c['egd_eV_below_Ec'], wgd=c['wgd_eV'])
        interface = dict(enabled=d['interface'], numa=d['interface_levels_a'], numd=d['interface_levels_d'],
                         nta=0, wta=.025, ntd=0, wtd=.05,
                         nga=c['interface_peak_cm2_eV'], ega=c['interface_center_eV_below_Ec'],
                         wga=c['interface_width_eV'], ngd=0, egd=.4, wgd=.1)
    elif 'paper_traps' in cfg:
        # Historical paper/combined configs: retained for auditing genuine old exports.
        p = cfg['paper_traps']
        bulk = dict(enabled=True, numa=s['dos_levels_a'], numd=s['dos_levels_d'],
                    nta=c['nta_cm3_eV'], wta=c['wta_eV'], ntd=0, wtd=.1,
                    nga=c['nga_cm3_eV'], ega=p['bulk_acceptor_center_below_Ec_eV'],
                    wga=p['bulk_acceptor_width_eV'], ngd=p['oxygen_donor_peak_cm3_eV'],
                    egd=eg-p['oxygen_donor_center_below_Ec_eV'], wgd=p['oxygen_donor_width_eV'])
        interface = dict(enabled=True, numa=p['interface_levels_a'], numd=p['interface_levels_d'],
                         nta=0, wta=.025, ntd=0, wtd=.05,
                         nga=c['interface_gaussian_peak_cm2_eV'],
                         ega=p['interface_acceptor_center_below_Ec_eV'],
                         wga=p['interface_acceptor_width_eV'], ngd=0, egd=.4, wgd=.1)
    else:
        raise ValueError('Unsupported config schema; expected rebuild defects or paper_traps')
    for group in (bulk, interface):
        for field in ('nta', 'ntd', 'nga', 'ngd'):
            if not math.isfinite(group[field]) or group[field] < 0:
                raise ValueError(f'Invalid {field}')
        for field in ('wta', 'wtd', 'wga', 'wgd'):
            if not math.isfinite(group[field]) or group[field] <= 0:
                raise ValueError(f'Invalid {field}')
    return eg, float(c['thickness_nm']) * 1e-7, {'bulk': bulk, 'interface': interface}


def read_ssf(path, signature):
    rows, header = [], None
    for line in path.read_text(errors='replace').splitlines():
        parts = line.split()
        if parts and parts[0] == 'p':
            if header is not None:
                raise ValueError('Multiple column signatures; unsupported export')
            header = list(map(int, parts[2:]))
            if int(parts[1]) != len(header):
                raise ValueError('Column count in native header does not match')
        elif parts and parts[0] == 'd':
            row = [float(v.replace('D', 'E').replace('d', 'e')) for v in parts[1:]]
            if any(not math.isfinite(v) for v in row):
                raise ValueError('Nonfinite DOS data')
            rows.append(row)
    if header != signature:
        raise ValueError(f'Unsupported native column signature: {header}; expected {signature}')
    if len(rows) < 2 or any(len(row) != len(header) for row in rows):
        raise ValueError('Missing/truncated native DOS rows')
    if any(value < 0 for row in rows for value in row[1:]):
        raise ValueError('Negative density in native DOS export')
    changes = [b[0]-a[0] for a, b in zip(rows, rows[1:])]
    if not (all(v >= 0 for v in changes) or all(v <= 0 for v in changes)):
        raise ValueError('Energy order is not monotonic; unsupported multi-block export')
    unique = {}
    for row in rows:
        if row[0] in unique:
            old = unique[row[0]]
            for a, b in zip(old[1:], row[1:]):
                if abs(a-b) > 1e-5 * max(abs(a), abs(b), 1e-300):
                    raise ValueError('Different DOS values at the same energy')
        else:
            unique[row[0]] = row
    ordered = sorted(unique.values())
    steps = [b[0]-a[0] for a, b in zip(ordered, ordered[1:])]
    grid = dict(raw_rows=len(rows), unique_rows=len(ordered), duplicate_rows=len(rows)-len(ordered),
                energy_min_eV=ordered[0][0], energy_max_eV=ordered[-1][0],
                spacing_min_eV=min(steps), spacing_max_eV=max(steps),
                approximately_uniform=math.isclose(min(steps), max(steps), rel_tol=1e-4, abs_tol=1e-9))
    return ordered, grid


def components(group, a_depth, d_energy, eg):
    at = group['nta'] * math.exp(-a_depth/group['wta'])
    ag = group['nga'] * math.exp(-((a_depth-group['ega'])/group['wga'])**2)
    dt = group['ntd'] * math.exp(-d_energy/group['wtd'])
    dg = group['ngd'] * math.exp(-((d_energy-group['egd'])/group['wgd'])**2)
    return [at, ag, at+ag, dt, dg, dt+dg]


def gaussian_capacity(peak, centre, width, eg):
    return peak * width * math.sqrt(math.pi) / 2 * (math.erf((eg-centre)/width)+math.erf(centre/width))


def capacities(group, eg):
    at = group['nta']*group['wta']*(-math.expm1(-eg/group['wta']))
    ag = gaussian_capacity(group['nga'], group['ega'], group['wga'], eg)
    dt = group['ntd']*group['wtd']*(-math.expm1(-eg/group['wtd']))
    dg = gaussian_capacity(group['ngd'], group['egd'], group['wgd'], eg)
    return [at, ag, at+ag, dt, dg, dt+dg]


def audit_export(path, kind, role, group, eg, thickness_cm, sample_tol, integration_tol):
    rows, grid = read_ssf(path, SIGNATURES[kind, role])
    requested_rows = int(group['numa'] if role == 'a' else group['numd'] if role == 'd' else group['numa']+group['numd'])
    grid['expected_plot_rows_from_NUMA_NUMD'] = requested_rows
    grid['matches_requested_plot_row_count'] = grid['raw_rows'] == requested_rows
    energies = [row[0] for row in rows]
    expected = []
    for energy in energies:
        a_depth, d_energy = (energy, eg-energy) if role == 'a' else (eg-energy, energy)
        all_components = components(group, a_depth, d_energy, eg)
        expected.append(all_components[:3] if role == 'a' else all_components[3:] if role == 'd' else all_components)
    labels = ['acceptor_tail', 'acceptor_gaussian', 'acceptor_total', 'donor_tail', 'donor_gaussian', 'donor_total']
    cap = capacities(group, eg)
    scale = [group['nta'], group['nga'], group['nta']+group['nga'],
             group['ntd'], group['ngd'], group['ntd']+group['ngd']]
    if role == 'a':
        labels, cap, scale = labels[:3], cap[:3], scale[:3]
    elif role == 'd':
        labels, cap, scale = labels[3:], cap[3:], scale[3:]
    detail = {}
    passed = (grid['matches_requested_plot_row_count']
              and math.isclose(min(energies), 0, abs_tol=2e-6)
              and math.isclose(max(energies), eg, abs_tol=2e-6))
    resolution_ok = True
    for j, label in enumerate(labels):
        observed = [row[j+1] for row in rows]
        maximum = max(observed)
        peak_idx = observed.index(maximum)
        error = max(abs(y-exp[j]) for y, exp in zip(observed, expected))
        normalized_error = error / scale[j] if scale[j] else (0 if error == 0 else None)
        parameter_pass = error <= sample_tol*scale[j] if scale[j] else error == 0
        integral = sum((energies[i+1]-energies[i])*(observed[i+1]+observed[i])/2 for i in range(len(rows)-1))
        rel_integral = (integral-cap[j])/cap[j] if cap[j] else (0 if integral == 0 else None)
        sampled = abs(rel_integral) <= integration_tol if rel_integral is not None else False
        passed = passed and parameter_pass
        resolution_ok = resolution_ok and sampled
        entry = dict(sample_formula_pass=parameter_pass, max_error_normalized_to_input_peak=normalized_error,
                     sampled_maximum=maximum, sampled_maximum_energy_eV=energies[peak_idx],
                     expected_value_at_sampled_maximum=expected[peak_idx][j],
                     analytic_band_truncated_capacity=cap[j], sampled_trapezoid_capacity=integral,
                     sampled_integral_relative_error=rel_integral, export_sampling_integral_pass=sampled,
                     analytic_sheet_capacity_cm2=cap[j]*(thickness_cm if kind == 'bulk' else 1),
                     sampled_sheet_capacity_cm2=integral*(thickness_cm if kind == 'bulk' else 1))
        if label.endswith('gaussian') and maximum > 0:
            acceptor = label.startswith('acceptor')
            centre = group['ega'] if acceptor else group['egd']
            width = group['wga'] if acceptor else group['wgd']
            x_at_peak = energies[peak_idx]
            expected_centre = eg-centre if role == 't' and acceptor else centre
            shape = math.exp(-((x_at_peak-expected_centre)/width)**2)
            entry.update(expected_continuum_peak_energy_eV=expected_centre,
                         expected_continuum_peak_amplitude=group['nga' if acceptor else 'ngd'],
                         amplitude_reconstructed_from_nearest_peak_sample=maximum/shape)
        detail[label] = entry
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path), parameter_values_pass=passed,
                energy_axis='below_Ec' if role == 'a' else 'above_Ev',
                density_units='cm^-3 eV^-1' if kind == 'bulk' else 'cm^-2 eV^-1',
                capacity_units='cm^-3' if kind == 'bulk' else 'cm^-2',
                grid=grid, components=detail, export_sampling_integral_pass=resolution_ok)


def audit(run_dir, config_path=None, key='2p0', sample_tol=5e-5, integration_tol=.05):
    run_dir = inside_project(run_dir)
    config_path = inside_project(config_path or run_dir/'input_config.json')
    cfg = load(config_path)
    eg, thickness_cm, groups = expected_config(cfg, key)
    deck_path = run_dir/'device.in'
    if not deck_path.is_file():
        raise ValueError('Expected immutable run input device.in')
    statements = commands(deck_path)
    output = (run_dir/'deckbuild.out').read_text(errors='replace')
    execution = load(run_dir/'execution.json') if (run_dir/'execution.json').exists() else {}
    result = dict(schema_version=1, audit_kind='NATIVE_DOS_PARAMETER_AND_CAPACITY_ONLY',
                  created_utc=datetime.now(timezone.utc).isoformat(), run_directory=str(run_dir.relative_to(ROOT)),
                  configuration=str(config_path.relative_to(ROOT)), config_sha256=digest(config_path),
                  deck_sha256=digest(deck_path), key=key, bandgap_eV=eg, thickness_cm=thickness_cm,
                  simulator_completed=bool(re.search(r'ATLAS version .* finished', output)),
                  sample_peak_normalized_tolerance=sample_tol, export_integral_relative_tolerance=integration_tol,
                  groups={}, errors=[], warnings=[], occupancy_available=False,
                  interpretation='Exports describe available DOS capacity, not occupied/ionized trap charge. '
                                 'A parameter pass does not establish electrical application at the correct interface, '
                                 'solver quadrature convergence, unique defects, or an accepted transfer fit.',
                  degeneracy='No extra spin/charge/chemical degeneracy multiplier is applied. Continuous-DOS '
                             'amplitudes are read in their native stated units; microscopic defect degeneracy '
                             'and charge-state identity are not independently established by these exports.')
    for kind, group in groups.items():
        node = dict(enabled=bool(group['enabled']), expected_parameters=group, exports={})
        result['groups'][kind] = node
        cmds = statements[kind]
        if not group['enabled']:
            if cmds:
                result['errors'].append(f'{kind}: disabled in config but DOS command is present')
            leftovers = [p.name for p in run_dir.glob(kind+'*.dat') if any(s in p.name for s in ['acceptor','donor','dos'])]
            if leftovers:
                result['errors'].append(f'{kind}: disabled but unexpected native DOS files exist: {leftovers}')
            continue
        if len(cmds) != 1:
            result['errors'].append(f'{kind}: expected one DOS statement, found {len(cmds)}; cannot merge populations silently')
            continue
        cmd = cmds[0]
        node['native_region_or_interface_selector'] = cmd.get('intnumber', cmd.get('region'))
        if 'continuous' not in cmd or (kind == 'interface' and 'max.gaussian' not in cmd):
            result['errors'].append(f'{kind}: expected CONTINUOUS and interface MAX.GAUSSIAN conventions')
        for name in ['numa','numd','nta','ntd','nga','ngd','ega','egd','wga','wgd'] + (['wta'] if group['nta'] else []) + (['wtd'] if group['ntd'] else []):
            try:
                actual = float(cmd[name])
                if not math.isclose(actual, float(group[name]), rel_tol=1e-7, abs_tol=1e-12):
                    result['errors'].append(f'{kind}: deck {name}={actual} disagrees with config {group[name]}')
            except (ValueError, KeyError, TypeError):
                result['errors'].append(f'{kind}: missing/nonliteral {name}; no expression evaluation permitted')
        for role in ('a', 'd', 't'):
            field = role+'file'
            if field not in cmd:
                node['exports'][field] = {'requested':False, 'available':False}
                if role != 't': result['errors'].append(f'{kind}: required {field} not requested')
                continue
            try:
                path = (run_dir/str(cmd[field])).resolve()
                if not path.is_relative_to(run_dir):
                    raise ValueError('Native DOS path leaves raw run directory')
                export = audit_export(path, kind, role, group, eg, thickness_cm, sample_tol, integration_tol)
                node['exports'][field] = export
                if not export['parameter_values_pass']:
                    result['errors'].append(f'{kind} {field}: native samples do not match configured DOS')
                if not export['export_sampling_integral_pass']:
                    result['warnings'].append(f'{kind} {field}: coarse export quadrature differs from exact capacity; '
                                              'this is not by itself proof of incorrect simulator integration')
                expected_hash = execution.get('outputs', {}).get(path.name) if isinstance(execution.get('outputs'),dict) else None
                if expected_hash is not None and expected_hash != export['sha256']:
                    result['errors'].append(f'{kind} {field}: current hash differs from execution manifest')
                export['matches_execution_hash'] = None if expected_hash is None else expected_hash == export['sha256']
            except (ValueError, OSError, OverflowError) as exc:
                node['exports'][field] = {'error':str(exc)}
                result['errors'].append(f'{kind} {field}: {exc}')
    result['parameter_audit_pass'] = not result['errors']
    result['enabled_distribution_groups'] = sum(bool(group['enabled']) for group in groups.values())
    result['native_dos_exports_verified'] = bool(result['parameter_audit_pass'] and result['enabled_distribution_groups'])
    result['status'] = ('DOS_AUDIT_FAILED' if not result['parameter_audit_pass'] else
                        'NATIVE_DOS_PARAMETERS_VERIFIED_CAPACITY_ONLY' if result['enabled_distribution_groups'] else
                        'NO_CONTINUOUS_DOS_REQUESTED')
    if not result['simulator_completed']:
        result['warnings'].append('No ATLAS finished banner: DOS audit is not evidence of a completed device run')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_directory', type=Path)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--key', default='2p0')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    run_dir = inside_project(args.run_directory)
    out = (args.out or AUDITS/(run_dir.name+'.json')).resolve()
    if not out.is_relative_to(AUDITS.resolve()) or out.suffix.lower() != '.json':
        raise ValueError(f'Audit output must be a JSON under {AUDITS}; raw runs are immutable')
    result = audit(run_dir, args.config, args.key)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'status':result['status'], 'output':str(out),
                      'errors':result['errors'], 'warnings':result['warnings']}, indent=2))
    raise SystemExit(0 if result['parameter_audit_pass'] else 2)


if __name__ == '__main__':
    main()
