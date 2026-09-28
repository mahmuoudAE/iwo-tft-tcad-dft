"""Portable read-only evidence recheck; never launches a simulator.

Place this file at the copied supplement root, beside verification_inputs.json,
scripts/, data/, MANIFEST_SHA256.json and results/. New reports alone are written
under verification/. Original certificates and native evidence are never edited.
"""
from __future__ import annotations

import argparse
import contextlib
from datetime import datetime, timezone
import hashlib
import importlib
import io
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import sys

DEVICE_KEYS = ('2p0', '6p3', '13p2')
CONTROL_KEYS = {'2p0': ('width', 'xmesh', 'ymesh', 'dos'),
                '6p3': ('xmesh', 'ymesh', 'dos'),
                '13p2': ('xmesh', 'ymesh', 'dos')}
COPIED_MODULES = ('rebuild_model', 'rebuild_check', 'rebuild_extension_check')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative_path(root, value, *, kind):
    """Reject absolute, drive-relative, traversal and resolved escape paths."""
    root = Path(root).resolve()
    if not isinstance(value, str) or not value or '\x00' in value:
        raise ValueError('Expected a nonempty relative path')
    windows = PureWindowsPath(value)
    portable = PurePosixPath(value.replace('\\', '/'))
    if windows.drive or windows.root or portable.is_absolute() or ':' in value:
        raise ValueError('Paths must be relative to the copied supplement root')
    if '..' in portable.parts:
        raise ValueError('Path traversal is not allowed')
    result = (root / Path(*portable.parts)).resolve()
    if result == root or not result.is_relative_to(root):
        raise ValueError('Path resolves outside the copied supplement root')
    if kind == 'file' and not result.is_file():
        raise ValueError('Required copied file missing: ' + value)
    if kind == 'directory' and not result.is_dir():
        raise ValueError('Required copied directory missing: ' + value)
    if kind not in ('file', 'directory', 'new'):
        raise ValueError('Unsupported path validation kind')
    return result


def validate_mapping(root, mapping):
    """Pin each explicit map entry to its untouched copied execution record."""
    if not isinstance(mapping, dict) or set(mapping) != {'schema_version', 'devices'}:
        raise ValueError('Expected schema_version and devices only')
    if type(mapping['schema_version']) is not int or mapping['schema_version'] != 1:
        raise ValueError('Unsupported verification input schema')
    devices = mapping['devices']
    if not isinstance(devices, dict) or set(devices) != set(DEVICE_KEYS):
        raise ValueError('Require exactly the priority three device keys')
    seen = set()
    normalized = {}

    def entry(value):
        if not isinstance(value, dict) or set(value) != {'path', 'run_id'}:
            raise ValueError('Every run entry needs exactly path and run_id')
        expected = value['run_id']
        if not isinstance(expected, str) or not expected or Path(expected).name != expected:
            raise ValueError('Invalid expected native run ID')
        folder = relative_path(root, value['path'], kind='directory')
        if folder in seen:
            raise ValueError('A native run cannot fill two mapped roles')
        seen.add(folder)
        execution_path = relative_path(root, str(folder.relative_to(root) / 'execution.json'), kind='file')
        execution = json.loads(execution_path.read_text(encoding='utf-8-sig'))
        if execution.get('run_id') != expected or folder.name != expected:
            raise ValueError('Copied directory/native run ID differs from explicit mapping')
        return {'path': folder, 'run_id': expected}

    for key in DEVICE_KEYS:
        device = devices[key]
        if not isinstance(device, dict) or set(device) != {'reference', 'controls'}:
            raise ValueError('Each device needs reference and controls only')
        controls = device['controls']
        if not isinstance(controls, dict) or set(controls) != set(CONTROL_KEYS[key]):
            raise ValueError('Wrong control keys for ' + key)
        normalized[key] = {'reference': entry(device['reference']), 'controls': {}}
        for kind in CONTROL_KEYS[key]:
            value = controls[kind]
            if value is None:
                if key != '13p2':
                    raise ValueError('Only unavailable 13.2 nm controls may be null')
                normalized[key]['controls'][kind] = None
            else:
                normalized[key]['controls'][kind] = entry(value)
    return normalized


def load_copied_checkers(root):
    """Refuse cached foreign checkers and verify every transitive local origin."""
    root = Path(root).resolve()
    expected = {name: relative_path(root, 'scripts/' + name + '.py', kind='file')
                for name in COPIED_MODULES}
    for name, path in expected.items():
        cached = sys.modules.get(name)
        if cached is not None and Path(getattr(cached, '__file__', '')).resolve() != path:
            raise ValueError('Foreign cached module refused: ' + name)
    old_path, old_bytecode = sys.path[:], sys.dont_write_bytecode
    sys.path.insert(0, str(root / 'scripts'))
    sys.dont_write_bytecode = True
    try:
        check = importlib.import_module('rebuild_check')
        extension = importlib.import_module('rebuild_extension_check')
    finally:
        sys.path[:] = old_path
        sys.dont_write_bytecode = old_bytecode
    origins = {}
    for name, path in expected.items():
        module = sys.modules.get(name)
        if module is None or Path(getattr(module, '__file__', '')).resolve() != path:
            raise ValueError('Imported module came from outside copied scripts: ' + name)
        if Path(getattr(module, 'ROOT', '')).resolve() != root:
            raise ValueError('Copied module ROOT does not match supplement: ' + name)
        origins[name] = {'path': str(path), 'sha256': digest(path)}
    if extension.load_run is not check.load_run or check.render is not sys.modules['rebuild_model'].render:
        raise ValueError('Copied checker dependencies do not share verified module origins')
    return check, extension, origins


def new_output_directory(root, normalized, stamp=None):
    root = Path(root).resolve()
    parent = relative_path(root, 'verification', kind='new')
    if any((p / 'execution.json').is_file() for p in (parent, *parent.parents) if p.is_relative_to(root)):
        raise ValueError('Verification output cannot be inside native evidence')
    for device in normalized.values():
        for value in [device['reference'], *device['controls'].values()]:
            if value is not None and (parent.is_relative_to(value['path']) or value['path'].is_relative_to(parent)):
                raise ValueError('Verification output and native input directories overlap')
    name = stamp or datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    if not isinstance(name, str) or PurePosixPath(name).name != name or PureWindowsPath(name).name != name or ':' in name or name in ('.', '..'):
        raise ValueError('Invalid verification directory name')
    out = relative_path(root, 'verification/' + name, kind='new')
    out.mkdir(parents=True, exist_ok=False)
    return out


def scope_status(report):
    """Missing controls stay INCOMPLETE; a present failed control remains FAIL."""
    if report.get('status') == 'FAIL':
        return 'FAIL'
    checks = report.get('checks', {})
    if any(item.get('status') != 'MISSING' and not item.get('pass_check', False)
           for item in checks.values()):
        return 'FAIL'
    if any(item.get('status') == 'MISSING' for item in checks.values()):
        return 'INCOMPLETE'
    return 'PASS' if report.get('status') in ('PASS', 'PASS_SCOPED_EXTENSION_NUMERICS') else 'FAIL'


def write_new_json(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def verify(root, inputs='verification_inputs.json'):
    """Recompute from explicit copied evidence; no original absolute paths used."""
    root = Path(root).resolve()
    mapping_file = relative_path(root, inputs, kind='file')
    mapping = json.loads(mapping_file.read_text(encoding='utf-8-sig'))
    normalized = validate_mapping(root, mapping)
    relative_path(root, 'MANIFEST_SHA256.json', kind='file')
    for key in (*DEVICE_KEYS, '31p8'):
        relative_path(root, 'data/iwo_' + key + 'nm.csv', kind='file')
    check, extension, origins = load_copied_checkers(root)
    # Validate every available reference/control before creating any report path.
    # This checks fresh hashes, native completion, all targets, signs and physics.
    pinned = {}
    for key, device in normalized.items():
        for role, value in [('reference', device['reference']), *device['controls'].items()]:
            if value is None:
                continue
            run = check.load_run(value['path'])
            if run['key'] != key or run['summary']['run_id'] != value['run_id']:
                raise ValueError('Mapped native device identity mismatch: ' + key + '/' + role)
            if not run['summary']['run_acceptable']:
                raise ValueError('Mapped native evidence fails electrical checks: ' + key + '/' + role)
            pinned[key + '/' + role] = run['summary']
    out = new_output_directory(root, normalized)
    summary = {'status': 'IN_PROGRESS', 'root': str(root), 'output_directory': str(out),
               'input_mapping_sha256': digest(mapping_file), 'module_origins': origins,
               'thresholds': dict(check.LIMITS), 'simulator_launched': False,
               'original_certificates_edited': False, 'results': {}}
    write_new_json(out / 'verification_inputs_snapshot.json', mapping)
    try:
        two = normalized['2p0']
        basis = out / 'numerical_2_recomputed.json'
        arguments = ['--reference', str(two['reference']['path'])]
        for kind, value in two['controls'].items():
            arguments.extend(['--' + kind, str(value['path'])])
        arguments.extend(['--out', str(basis)])
        with contextlib.redirect_stdout(io.StringIO()):
            check.main(arguments)
        reports = {'2p0': check.read_json(basis)}
        for key in ('6p3', '13p2'):
            device = normalized[key]
            candidates = {kind: value['path'] if value is not None else None
                          for kind, value in device['controls'].items()}
            reports[key] = extension.assess(device['reference']['path'], candidates, basis)
            write_new_json(out / ('numerical_' + key + '_recomputed.json'), reports[key])
        for key, report in reports.items():
            summary['results'][key] = {
                'status': scope_status(report),
                'native_checker_status': report['status'],
                'validated_scope': report.get('validated_scope', 'DEVICE_WIDTH_X_Y_DOS' if report['status'] == 'PASS' else 'NONE'),
                'missing_controls': [kind for kind, item in report['checks'].items() if item['status'] == 'MISSING'],
                'reference_run_id': normalized[key]['reference']['run_id'],
                'per_device_width_test_performed': key == '2p0',
                'measurement_fit_validated': False,
                'predictive_validity_established': False}
        states = [r['status'] for r in summary['results'].values()]
        summary['status'] = 'FAIL' if 'FAIL' in states else ('INCOMPLETE' if 'INCOMPLETE' in states else 'PASS')
        summary['lifecycle_scope'] = 'Numerical evidence only. Separate lifecycle reconciliation sidecars are not retrospective proof of missed helper lineage.'
        # Hash all explicitly pinned native evidence again; do not hide a
        # concurrent edit behind a report generated from a previous file state.
        for role, old in pinned.items():
            new = check.load_run(old['directory'])['summary']
            if new['evidence_sha256'] != old['evidence_sha256'] or new['raw_output_sha256'] != old['raw_output_sha256']:
                raise ValueError('Copied native evidence changed during verification: ' + role)
        if digest(mapping_file) != summary['input_mapping_sha256']:
            raise ValueError('Input mapping changed during verification')
        for name, origin in origins.items():
            if digest(Path(origin['path'])) != origin['sha256']:
                raise ValueError('Copied checker changed during verification: ' + name)
    except Exception as exc:
        summary['status'] = 'FAIL'
        summary['error'] = str(exc)
    write_new_json(out / 'VERIFICATION_SUMMARY.json', summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', default='verification_inputs.json',
                        help='Relative JSON mapping within this copied supplement')
    args = parser.parse_args(argv)
    try:
        result = verify(Path(__file__).resolve().parent, args.inputs)
    except (ValueError, KeyError, OSError, ImportError) as exc:
        parser.exit(2, 'Copied verification refused: ' + str(exc) + '\n')
    print(json.dumps({'status': result['status'], 'output_directory': result['output_directory'],
                      'devices': result['results'], 'module_origins': result['module_origins'],
                      'simulator_launched': False}, indent=2))
    return {'PASS': 0, 'INCOMPLETE': 1, 'FAIL': 2}[result['status']]


if __name__ == '__main__':
    raise SystemExit(main())

