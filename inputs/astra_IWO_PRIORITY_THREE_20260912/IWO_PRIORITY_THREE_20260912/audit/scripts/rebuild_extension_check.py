"""Scoped extension checks with independently reverified normalization evidence.

No simulator is launched. This is not the four-check certificate issued by
rebuild_check and does not grant predictive, physical, or measurement-fit validity.
"""
import argparse
import json
import re
from pathlib import Path

from rebuild_check import ROOT, LIMITS, compare, load_run, read_json, sha

NORMALIZATION_REPORT = ROOT / 'results/rebuild_20260912/fit04_numerical_validation.json'
EXTENSION_KEYS = {'6p3', '13p2', '31p8'}
SPATIAL_ENERGY_KINDS = ('xmesh', 'ymesh', 'dos')


def atlas_version(run):
    """Use the execution-hashed raw banner, never an executable-path guess."""
    output = (Path(run['summary']['directory']) / 'deckbuild.out').read_text(errors='replace')
    starts = re.findall(r'Version:\s*atlas\s+([^\s]+)', output, re.I)
    finishes = re.findall(r'ATLAS version\s+([^\s]+)\s+finished', output, re.I)
    if len(starts) != 1 or finishes != starts:
        raise ValueError('Missing or inconsistent native ATLAS version banners')
    return starts[0]


def pinned_run(saved):
    run = load_run(Path(saved['directory']))
    if saved.get('run_id') != run['summary']['run_id'] or saved.get('key') != run['key']:
        raise ValueError('Normalization report run identity changed')
    hashes = saved.get('evidence_sha256', {})
    required = {'execution.json', 'device.in', 'input_config.json', 'comparison_all_measurements.csv'}
    if not required <= hashes.keys():
        raise ValueError('Normalization report lacks pinned source evidence hashes')
    folder = Path(run['summary']['directory'])
    for name, expected in hashes.items():
        path = (folder / name).resolve()
        if not path.is_relative_to(folder) or not path.is_file() or sha(path) != expected:
            raise ValueError('Pinned normalization evidence changed: ' + name)
    return run


def normalization_basis(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Normalization report must remain inside the project')
    certificate = read_json(path)
    if certificate.get('status') != 'PASS' or certificate.get('all_required_checks_passed') is not True:
        raise ValueError('The original 2 nm numerical certificate is not complete/PASS')
    if certificate.get('thresholds') != LIMITS:
        raise ValueError('Normalization certificate thresholds differ from unchanged limits')
    for kind in ('width',) + SPATIAL_ENERGY_KINDS:
        saved = certificate.get('checks', {}).get(kind, {})
        if saved.get('status') != 'PASS' or saved.get('pass_check') is not True:
            raise ValueError('Original 2 nm certificate lacks passing ' + kind + ' evidence')
    reference = pinned_run(certificate['reference'])
    width = pinned_run(certificate['checks']['width']['candidate'])
    if reference['key'] != '2p0' or width['key'] != '2p0':
        raise ValueError('Normalization basis must use actual 2 nm runs')
    if reference['summary']['width_um'] != 1:
        raise ValueError('Normalization basis must begin at simulated width 1 um')
    if reference['cfg']['contacts'].get('resistance_ohm_um', 0) != 0:
        raise ValueError('Transferred normalization basis must be resistance-free')
    version = atlas_version(reference)
    if atlas_version(width) != version:
        raise ValueError('Normalization width pair uses different ATLAS versions')
    recalculated = compare(reference, width, 'width')
    if not recalculated['pass_check']:
        raise ValueError('Recomputed actual 2 nm width comparison failed')
    result = dict(status='REVERIFIED_2NM_WIDTH_UNIT_CONVENTION',
                  source_report=str(path), source_report_sha256=sha(path), atlas_version=version,
                  source_reference=reference['summary'], recomputed_width_check=recalculated,
                  source_full_certificate_recorded_pass=True,
                  scope='Actual 2 nm width comparison recomputed from pinned native evidence. Source x/y/DOS PASS records are prerequisites, not transferred device-specific refinements.')
    return reference, result


def contact_form(cfg):
    form = dict(cfg['contacts'])
    form.pop('resistance_ohm_um', None)
    return form


def compatibility(reference, basis_reference, version):
    checks = dict(
        extension_thickness=reference['key'] in EXTENSION_KEYS,
        same_atlas_version=atlas_version(reference) == version,
        simulated_width_one=reference['summary']['width_um'] == 1,
        same_electrical_domain=reference['cfg'].get('electrical_domain') == basis_reference['cfg'].get('electrical_domain') == 'screened_active_stack',
        same_contact_form_without_resistance=contact_form(reference['cfg']) == contact_form(basis_reference['cfg']),
        same_affinity=reference['cfg']['shared']['affinity_eV'] == basis_reference['cfg']['shared']['affinity_eV'])
    return dict(pass_check=all(checks.values()), conditions=checks,
                resistance_ohm_um=reference['cfg']['contacts'].get('resistance_ohm_um', 0))


def assess(reference_path, candidates, normalization_report=NORMALIZATION_REPORT, width_path=None):
    """Recompute source-run evidence. Returned data never implies a fitted model."""
    result = dict(status='INCOMPLETE', validated_scope='NONE', thresholds=LIMITS,
                  spatial_and_energy_checks_passed=False, normalization_check_passed=False,
                  per_device_width_test_performed=False, per_device_width_test_passed=None,
                  measurement_fit_validated=False, predictive_validity_established=False,
                  normalization_basis=None, checks={},
                  scope_note='Transferred unit-convention evidence is not a repeated per-device width test and is not the four-check all-required certificate.')
    try:
        basis_reference, basis = normalization_basis(normalization_report)
        result['normalization_basis'] = basis
    except Exception as exc:
        basis_reference = None
        result['normalization_basis'] = dict(status='INVALID_OR_INCOMPLETE', error=str(exc))
    try:
        reference = load_run(reference_path)
        result['reference'] = reference['summary']
        result['reference_atlas_version'] = atlas_version(reference)
    except Exception as exc:
        reference = None
        result['reference_error'] = str(exc)
    for kind in SPATIAL_ENERGY_KINDS:
        path = candidates.get(kind)
        if reference is None:
            result['checks'][kind] = dict(status='BLOCKED_BY_REFERENCE', pass_check=False)
        elif path is None:
            result['checks'][kind] = dict(status='MISSING', pass_check=False)
        else:
            try:
                candidate = load_run(path)
                if atlas_version(candidate) != atlas_version(reference):
                    raise ValueError('Device control and reference use different ATLAS versions')
                result['checks'][kind] = compare(reference, candidate, kind)
            except Exception as exc:
                result['checks'][kind] = dict(status='INVALID_EVIDENCE', pass_check=False, error=str(exc))
    result['spatial_and_energy_checks_passed'] = bool(reference is not None
        and reference['summary']['run_acceptable'] and all(v['pass_check'] for v in result['checks'].values()))

    compatible = None
    if reference is not None and basis_reference is not None:
        try:
            compatible = compatibility(reference, basis_reference, result['normalization_basis']['atlas_version'])
            result['normalization_basis']['extension_compatibility'] = compatible
        except Exception as exc:
            result['normalization_basis']['extension_compatibility'] = dict(pass_check=False, error=str(exc))
    if width_path is not None and reference is not None:
        try:
            width = load_run(width_path)
            result['per_device_width_test_performed'] = True
            if atlas_version(width) != atlas_version(reference):
                raise ValueError('Per-device width pair uses different ATLAS versions')
            check = compare(reference, width, 'width')
            result['per_device_width_check'] = check
            result['per_device_width_test_passed'] = bool(check['pass_check'])
        except Exception as exc:
            result['per_device_width_check'] = dict(status='INVALID_EVIDENCE', pass_check=False, error=str(exc))
            result['per_device_width_test_passed'] = False
    if compatible is not None and compatible['pass_check']:
        if width_path is not None:
            result['normalization_check_passed'] = result['per_device_width_test_passed'] is True
            result['normalization_basis']['extension_use'] = 'REPEATED_DEVICE_WIDTH_CHECK_REQUIRED_AND_EVALUATED'
        elif compatible['resistance_ohm_um'] != 0:
            result['normalization_basis']['extension_use'] = 'TRANSFER_REJECTED_CONTACT_RESISTANCE_REQUIRES_EXPLICIT_WIDTH_RUN'
        else:
            result['normalization_check_passed'] = True
            result['normalization_basis']['extension_use'] = 'TRANSFERRED_UNIT_CONVENTION_ONLY_PER_DEVICE_WIDTH_NOT_REPEATED'
    passed = result['spatial_and_energy_checks_passed'] and result['normalization_check_passed']
    if passed:
        result['status'] = 'PASS_SCOPED_EXTENSION_NUMERICS'
        result['validated_scope'] = ('DEVICE_X_Y_DOS_AND_REPEATED_WIDTH_CHECK' if result['per_device_width_test_performed']
                                     else 'DEVICE_X_Y_DOS_WITH_TRANSFERRED_WIDTH_UNIT_CONVENTION')
    elif reference is None or basis_reference is None or all(v['status'] != 'MISSING' for v in result['checks'].values()):
        result['status'] = 'FAIL'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reference',) + SPATIAL_ENERGY_KINDS:
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--width', type=Path)
    parser.add_argument('--normalization-report', type=Path, default=NORMALIZATION_REPORT)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.out.resolve()
    if not out.is_relative_to(ROOT) or out.suffix.lower() != '.json':
        parser.error('--out must be a JSON path inside the project')
    if out.exists():
        parser.error('--out must be new; existing artifacts are preserved')
    if out.is_relative_to((ROOT / 'results/local_session_20260910/runs').resolve()):
        parser.error('--out must stay outside the reserved raw-run namespace')
    paths = [args.reference, args.width] + [getattr(args, k) for k in SPATIAL_ENERGY_KINDS]
    if any(p is not None and out.is_relative_to(p.resolve()) for p in paths) or any(
            (parent / 'execution.json').is_file() for parent in out.parents if parent.is_relative_to(ROOT)):
        parser.error('--out must stay outside all raw run directories')
    result = assess(args.reference, {k: getattr(args, k) for k in SPATIAL_ENERGY_KINDS},
                    args.normalization_report, args.width)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps(dict(status=result['status'], validated_scope=result['validated_scope'], output=str(out))))
    return 0 if result['status'] == 'PASS_SCOPED_EXTENSION_NUMERICS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
