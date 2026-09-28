"""Read-only audit of native classical / hard-wall Schrodinger charge diagnostics.

No simulator launches, numeric STR field identifiers, fitted-current substitution,
absolute-value sign repairs, or writes to raw runs. Outputs are separate JSON/MD.
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
OUT = ROOT / 'results/rebuild_20260912/quantum_audits'
TARGETS = [('0', 0.), ('0p5', .5), ('1', 1.), ('2', 2.), ('3', 3.)]
PHASES = ('classical', 'schrodinger')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project_path(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Input/output must remain inside the project')
    return path


def numeric_export(path):
    lines = path.read_text().splitlines()
    if len(lines) < 5 or not re.fullmatch(r'\d+\s+2\s+2', lines[1].strip()):
        raise ValueError(f'Unsupported native two-column export header: {path.name}')
    expected = int(lines[1].split()[0])
    rows = [list(map(float, line.split())) for line in lines[4:] if line.strip()]
    if len(rows) != expected or any(len(row) != 2 for row in rows):
        raise ValueError(f'Incomplete two-column export: {path.name}')
    if any(not math.isfinite(v) for row in rows for v in row):
        raise ValueError(f'Nonfinite data: {path.name}')
    return rows, {'title': lines[0], 'x_label': lines[2], 'y_label': lines[3]}


def native_log(path):
    lines = path.read_text().splitlines()
    terminals = shlex.split(next(line for line in lines if line.startswith('f ')))[2:]
    probe_lines = [shlex.split(line) for line in lines if line.startswith('o ')]
    probes = [line[2] for line in probe_lines]
    signature = next(line.split() for line in lines if line.startswith('p '))
    # This exact native LOG signature was observed in the genuine candidate run.
    # It is not a numeric STR-field mapping.
    if terminals != ['gate', 'source', 'drain'] or probes != ['qbound_n_avg', 'qbound_n_mid']:
        raise ValueError('Unsupported native terminal/probe declarations')
    if list(map(int, signature[1:])) != [11, 2, 601, 20, 3, 602, 21, 4, 603, 22, 3000, 3001]:
        raise ValueError('Unrecognized native zero-current LOG signature')
    rows = [list(map(float, line.split()[1:])) for line in lines if line.startswith('d ')]
    if len(rows) != 5 or any(len(row) != 11 for row in rows):
        raise ValueError('Expected exactly five native diagnostic bias rows')
    if any(not math.isfinite(v) for row in rows for v in row):
        raise ValueError('Nonfinite native LOG field')
    result = []
    for (_, target), row in zip(TARGETS, rows):
        if not math.isclose(row[0], target, abs_tol=1e-9):
            raise ValueError('Native gate targets differ from the diagnostic specification')
        if any(abs(row[index]) > 1e-12 for index in (3, 4, 6, 7)):
            raise ValueError('Source/drain bias is not zero')
        if row[9] < 0 or row[10] < 0:
            raise ValueError('Negative native electron density; signs have not been repaired')
        result.append(dict(vg_V=row[0], n_avg_cm3=row[9], n_mid_cm3=row[10]))
    return result


def integrate_iwo(rows, top_um, bottom_um, origin_um):
    """Integrate the native ordered polyline, preserving interface discontinuities.

    Native DEPTH with MATERIAL=All starts at the structure top. Vertical segments
    at a repeated interface depth have zero area; retain their order to select
    the physical one-sided segment inside IWO, never average a jump with oxide.
    """
    if any(row[1] < 0 for row in rows):
        raise ValueError('Negative cutline density; no clipping or absolute values allowed')
    data = [[depth + origin_um, n] for depth, n in rows]
    changes = [b[0]-a[0] for a, b in zip(data, data[1:])]
    if all(d <= 0 for d in changes):
        data.reverse()
    elif not all(d >= 0 for d in changes):
        raise ValueError('Native cutline is not monotonic in depth')
    epsilon = 2e-10
    selected = []
    for y, n in data:
        if abs(y-top_um) <= epsilon:
            y = top_um
        if abs(y-bottom_um) <= epsilon:
            y = bottom_um
        if top_um <= y <= bottom_um:
            selected.append((y, n))
    if len(selected) < 3 or selected[0][0] != top_um or selected[-1][0] != bottom_um:
        raise ValueError('Native cutline does not explicitly resolve both IWO boundaries; no extrapolation permitted')
    area = moment = 0.
    for (y0, n0), (y1, n1) in zip(selected, selected[1:]):
        dy = y1-y0
        area += dy*(n0+n1)/2
        moment += dy*(y0*(2*n0+n1)+y1*(n0+2*n1))/6
    if area <= 0:
        raise ValueError('Nonpositive integrated IWO electron density')
    return dict(sheet_electrons_cm2=area*1e-4,
                centroid_y_um=moment/area,
                centroid_distance_from_Al2O3_nm=(bottom_um-moment/area)*1000,
                original_points=len(rows), selected_points=len(selected),
                interface_duplicate_points=sum(a[0] == b[0] for a, b in zip(selected, selected[1:])),
                density_min_cm3=min(v[1] for v in selected), density_max_cm3=max(v[1] for v in selected),
                integration='Piecewise-linear native n(y), exact first moment; dy_um*1e-4 converts to cm. Ordered zero-length boundary jumps retained.')


def sp_evidence(output, qcrit, maximum):
    start = output.find('ATLAS> log outf=qbound_schrodinger.log')
    if start < 0:
        raise ValueError('Quantum log phase not found in native stdout')
    phase = output[start:].split('ATLAS> log off', 1)[0]
    blocks = re.split(r'(?=^ATLAS> solve\b)', phase, flags=re.M)[1:]
    result = []
    for block in blocks:
        target = re.search(r'^ATLAS> solve vgate=([\d.+-]+)', block)
        if not target:
            continue
        found = re.findall(r'^\s*(\d+)\s+(\d+)\s+(S|SP)\s+([+\d.*-]+)\s+([+\d.*-]+)\s*$', block, re.M)
        outer = [v for v in found if v[2] == 'S']
        if not outer:
            raise ValueError('Missing actual Schrodinger outer iteration rows')
        last = outer[-1]
        update, rhs = [float(v.replace('*', '')) for v in last[3:]]
        result.append(dict(vg_V=float(target[1]), final_outer_iteration=int(last[0]),
                           last_S_log10_potential_update=update, last_S_log10_rhs=rhs,
                           last_S_raw=' '.join(last),
                           below_configured_SP_potential_scale=update <= math.log10(qcrit),
                           below_iteration_limit=max(int(v[0]) for v in found) < maximum,
                           ordinary_poisson_rhs_marked_converged='*' in last[4],
                           has_terminal_result_table='Electrode       Va(V)' in block))
    if [v['vg_V'] for v in result] != [v for _, v in TARGETS]:
        raise ValueError('Quantum stdout does not contain all five requested solved-bias blocks')
    return result


def audit(run):
    run = project_path(run)
    cfg = json.loads((run/'input_config.json').read_text())
    detail = cfg['quantum_diagnostic']
    deck = (run/'device.in').read_text()
    output = (run/'deckbuild.out').read_text(errors='replace')
    execution = json.loads((run/'execution.json').read_text())
    result = dict(run_directory=str(run.relative_to(ROOT)), created_utc=datetime.now(timezone.utc).isoformat(),
                  status='PENDING', errors=[], warnings=[], hashes={}, phases={}, comparisons=[],
                  calibration_eligible=False, mesh_and_eigenstate_convergence_verified=False,
                  interpretation='Actual hard-wall charge-confinement diagnostic; not a transfer-current simulation or finite-barrier calibration.')
    expected = ['device.in','input_config.json','deckbuild.out','qbound_geometry.str']
    for phase in PHASES:
        expected += [f'qbound_{phase}.log']
        expected += [f'qbound_{phase}_{kind}.dat' for kind in ('n_avg','n_mid','vd','vs')]
        for tag, _ in TARGETS:
            expected += [f'qbound_{phase}_vg{tag}.str', f'qbound_{phase}_n_y_vg{tag}.dat']
    for name in expected:
        path = run/name
        if not path.is_file():
            result['errors'].append('Missing native output: '+name)
            continue
        digest = sha(path)
        matches = execution.get('outputs', {}).get(name) == digest
        result['hashes'][name] = dict(sha256=digest, matches_execution_manifest=matches)
        if not matches:
            result['errors'].append('Execution hash mismatch: '+name)
    result['engine_start_count'] = len(re.findall(r'Version:\s+atlas\s+5\.28\.1\.R', output))
    result['engine_finished_count'] = len(re.findall(r'ATLAS version 5\.28\.1\.R finished', output))
    if result['engine_start_count'] != 1 or result['engine_finished_count'] != 1 or execution.get('returncode') != 0:
        result['errors'].append('Missing unique genuine startup/completion or nonzero process exit')
    if len(re.findall(r'^go atlas\s*$', deck, re.M)) != 1 or len(re.findall(r'^solve init\s*$', deck, re.M)) != 2:
        result['errors'].append('Unexpected simulator/model-stage structure')
    origin = min(float(v) for v in re.findall(r'^y\.mesh loc=([\deE.+-]+)', deck, re.M))
    top, bottom = map(float, detail['cutline']['IWO_y_um'])
    result['cutline_coordinates'] = dict(native_axis='Depth from top of MATERIAL=All', depth_origin_absolute_y_um=origin,
                                        absolute_IWO_y_um=[top,bottom], native_IWO_depth_um=[top-origin,bottom-origin],
                                        manual_reference='DeckBuild 5.0.10.R Users Manual printed p137: depth starts at top of selected material/occurrence')
    for phase in PHASES:
        try:
            points = native_log(run/f'qbound_{phase}.log')
            for suffix, field in [('n_avg','n_avg_cm3'),('n_mid','n_mid_cm3'),('vd',None),('vs',None)]:
                rows, labels = numeric_export(run/f'qbound_{phase}_{suffix}.dat')
                if len(rows) != len(points):
                    raise ValueError('Native extracted bias count mismatch')
                for (x,y), point in zip(rows, points):
                    expected_y = point[field] if field else 0.
                    if not math.isclose(x,point['vg_V'],abs_tol=1e-9) or not math.isclose(y,expected_y,rel_tol=5e-6,abs_tol=0):
                        raise ValueError('Native EXTRACT curve disagrees with raw LOG')
            for (tag, _), point in zip(TARGETS, points):
                rows, labels = numeric_export(run/f'qbound_{phase}_n_y_vg{tag}.dat')
                if labels['x_label'] != 'Depth' or labels['y_label'] != 'Electron Conc':
                    raise ValueError('Unrecognized native cutline axis/quantity')
                if abs(rows[0][0]) > 1e-9:
                    raise ValueError('MATERIAL=All depth does not start at zero')
                point['IWO_cutline'] = integrate_iwo(rows,top,bottom,origin)
                structure = (run/f'qbound_{phase}_vg{tag}.str').read_text(errors='replace')
                eigen_labels = re.findall(r'^E \d+ "Conduction band energy #[^"]+" "eV"',structure,re.M)
                point['native_named_quantum_energy_fields'] = eigen_labels
                if phase == 'schrodinger' and not eigen_labels:
                    raise ValueError('No native named quantum-energy field in quantum structure')
            result['phases'][phase] = points
        except (ValueError, OSError, StopIteration) as exc:
            result['errors'].append(f'{phase}: {exc}')
    fatal = [line.strip() for line in output.splitlines() if not line.startswith(('ATLAS>','EXTRACT>'))
             and re.search(r'\berror\s*:|fatal|cannot trap|too many iterations in eigenvalue|error in the eigensolver|improperly specified|number of eigenvalues found',line,re.I)]
    result['fatal_or_unresolved_solver_lines'] = fatal
    if fatal:
        result['errors'].append('Native solver error/unresolved eigenvalue diagnostic present')
    try:
        qcrit = float(re.findall(r'qcrit\.negf=([\deE.+-]+)',deck)[-1])
        maxiter = int(re.findall(r'sp\.numiter=(\d+)',deck)[-1])
        sp = sp_evidence(output,qcrit,maxiter)
        result['SP_iteration_evidence'] = sp
        result['SP_potential_scale_pass'] = all(p['below_configured_SP_potential_scale'] and p['below_iteration_limit'] and p['has_terminal_result_table'] for p in sp)
        if not result['SP_potential_scale_pass']:
            result['errors'].append('Configured SP potential-scale/iteration-limit evidence failed')
        if not all(p['ordinary_poisson_rhs_marked_converged'] for p in sp):
            result['warnings'].append('Some last S rows satisfy the configured SP potential scale but do not mark the ordinary displayed Poisson RHS tolerance as met. This is a configured-SP-criterion diagnostic, not proof of tighter Poisson residual convergence.')
    except (ValueError, IndexError) as exc:
        result['errors'].append('SP convergence evidence incomplete: '+str(exc))
    if all(p in result['phases'] for p in PHASES):
        for classic, quantum in zip(result['phases']['classical'],result['phases']['schrodinger']):
            a,b=classic['IWO_cutline'],quantum['IWO_cutline']
            result['comparisons'].append(dict(vg_V=classic['vg_V'], classical_sheet_cm2=a['sheet_electrons_cm2'],
                quantum_sheet_cm2=b['sheet_electrons_cm2'], quantum_sheet_change_percent=100*(b['sheet_electrons_cm2']/a['sheet_electrons_cm2']-1),
                classical_centroid_from_interface_nm=a['centroid_distance_from_Al2O3_nm'],
                quantum_centroid_from_interface_nm=b['centroid_distance_from_Al2O3_nm'],
                classical_region_n_avg_cm3=classic['n_avg_cm3'],quantum_region_n_avg_cm3=quantum['n_avg_cm3']))
    result['evidence_pass'] = not result['errors']
    result['status'] = 'ACTUAL_HARD_WALL_CHARGE_BOUND_WITH_QUALIFICATIONS' if result['evidence_pass'] else 'QUANTUM_DIAGNOSTIC_NOT_VERIFIED'
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_directory',type=Path)
    args=parser.parse_args()
    run=project_path(args.run_directory)
    result=audit(run)
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/(run.name+'.json')
    path.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'output':str(path),'errors':result['errors'],
                      'warnings':result['warnings'],'comparisons':result['comparisons']},indent=2))
    raise SystemExit(0 if result['evidence_pass'] else 2)


if __name__=='__main__':
    main()
