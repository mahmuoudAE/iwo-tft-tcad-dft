"""Build a traceable three-thickness delivery, without any simulator launch.

Exactly one explicit completed run is required for 2, 6.3 and 13.2 nm. Supplied
numerical certificates are rechecked against those exact references and their
native controls; an absent certificate is explicitly recorded as absent.
"""
from __future__ import annotations

import argparse
import contextlib
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import shutil
import types

import rebuild_check as check
import rebuild_delivery as delivery
import rebuild_extension_check as extension
import rebuild_overview as visual
import rebuild_report as report

ROOT = check.ROOT
KEYS = ('2p0', '6p3', '13p2')
TARGETS = dict(active_rmse_log10_decades_max=.05, absolute_endpoint_error_percent_lt=5.)


def selected_runs(paths):
    if len(paths) != len(KEYS):
        raise ValueError('Require exactly three explicit completed runs: 2p0, 6p3, 13p2')
    sources = [Path(path).resolve() for path in paths]
    if len(set(sources)) != len(sources):
        raise ValueError('Duplicate selected run path')
    runs = [check.load_run(path) for path in sources]
    keys = [run['key'] for run in runs]
    if len(set(keys)) != len(KEYS) or set(keys) != set(KEYS):
        raise ValueError('Require exactly one run for each of 2p0, 6p3, 13p2; 31p8 is deferred')
    if any(not run['summary']['run_acceptable'] for run in runs):
        raise ValueError('A selected run fails individual native gates')
    return {key: runs[keys.index(key)] for key in KEYS}


def certificate_options(entries):
    """Parse explicit KEY=PATH entries without silently replacing duplicates."""
    result = {}
    for entry in entries:
        key, separator, path = entry.partition('=')
        if not separator or key not in KEYS or not path:
            raise ValueError('Certificate must be KEY=PATH for 2p0, 6p3 or 13p2')
        if key in result:
            raise ValueError('Duplicate certificate key: ' + key)
        result[key] = Path(path).resolve()
    return result


def project_file(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError('Certificate must be an existing project-local file')
    return path


def same_reference(saved, selected):
    """Reload pinned evidence; run identity alone cannot transfer a certificate."""
    reference = extension.pinned_run(saved)
    actual, chosen = reference['summary'], selected['summary']
    if (actual['run_id'] != chosen['run_id'] or reference['key'] != selected['key']
            or Path(actual['directory']).resolve() != Path(chosen['directory']).resolve()
            or actual['evidence_sha256'] != chosen['evidence_sha256']):
        raise ValueError('Numerical certificate reference differs from selected physical candidate')
    return reference


def full_certificate(saved, reference):
    """Recompute all four native controls, including a legitimate trap-free N/A."""
    if saved.get('status') != 'PASS' or saved.get('all_required_checks_passed') is not True:
        raise ValueError('Full numerical certificate is not complete/PASS')
    if saved.get('thresholds') != check.LIMITS:
        raise ValueError('Numerical certificate uses changed thresholds')
    reference = same_reference(saved['reference'], reference)
    checks = {}
    for kind in ('width', 'xmesh', 'ymesh', 'dos'):
        item = saved.get('checks', {}).get(kind, {})
        no_traps = not reference['cfg']['defects']['bulk'] and not reference['cfg']['defects']['interface']
        if kind == 'dos' and no_traps:
            if item.get('status') != 'N/A' or item.get('pass_check') is not True:
                raise ValueError('Trap-free DOS must be explicitly recorded N/A')
            checks[kind] = dict(status='N/A', pass_check=True, applies=False,
                                reason='Both continuous trap families disabled in this reference')
            continue
        if item.get('status') != 'PASS' or item.get('pass_check') is not True:
            raise ValueError('Full certificate lacks passing ' + kind)
        candidate = extension.pinned_run(item['candidate'])
        if extension.atlas_version(candidate) != extension.atlas_version(reference):
            raise ValueError('Numerical control uses a different native ATLAS version')
        checks[kind] = check.compare(reference, candidate, kind)
        if not checks[kind]['pass_check']:
            raise ValueError('Recomputed numerical control failed: ' + kind)
    return dict(status='PASS', validated_scope='DEVICE_WIDTH_X_Y_DOS',
                reference=reference['summary'], thresholds=check.LIMITS, checks=checks,
                per_device_width_test_performed=True, per_device_width_test_passed=True,
                measurement_fit_validated=False, predictive_validity_established=False)


def verified_certificate(path, selected):
    path = project_file(path)
    digest = check.sha(path)
    saved = check.read_json(path)
    reference = same_reference(saved['reference'], selected)
    supporting = []
    if saved.get('status') == 'PASS':
        recalculated = full_certificate(saved, reference)
    elif saved.get('status') == 'PASS_SCOPED_EXTENSION_NUMERICS':
        if saved.get('thresholds') != check.LIMITS:
            raise ValueError('Numerical certificate uses changed thresholds')
        if reference['key'] not in extension.EXTENSION_KEYS:
            raise ValueError('Scoped extension certificate cannot certify the 2 nm reference')
        basis = saved.get('normalization_basis', {})
        basis_path = project_file(basis['source_report'])
        if check.sha(basis_path) != basis.get('source_report_sha256'):
            raise ValueError('Pinned normalization certificate changed')
        base = check.read_json(basis_path)
        basis_reference = extension.pinned_run(base['reference'])
        # The existing scoped checker recomputes the width pair. Recompute all
        # original basis controls here as well before copying this certificate.
        full_certificate(base, basis_reference)
        supporting.append(dict(source_path=str(basis_path), sha256=check.sha(basis_path)))
        candidates = {}
        for kind in extension.SPATIAL_ENERGY_KINDS:
            item = saved.get('checks', {}).get(kind, {})
            if item.get('status') != 'PASS' or item.get('pass_check') is not True:
                raise ValueError('Scoped certificate lacks passing ' + kind)
            candidate = extension.pinned_run(item['candidate'])
            candidates[kind] = candidate['summary']['directory']
        width = None
        if saved.get('per_device_width_test_performed'):
            width = extension.pinned_run(saved['per_device_width_check']['candidate'])['summary']['directory']
        recalculated = extension.assess(reference['summary']['directory'], candidates, basis_path, width)
        if recalculated['status'] != 'PASS_SCOPED_EXTENSION_NUMERICS':
            raise ValueError('Recomputed scoped numerical certificate failed')
        if recalculated['validated_scope'] != saved.get('validated_scope'):
            raise ValueError('Recorded numerical scope differs from recomputed scope')
    else:
        raise ValueError('Only complete passing numerical certificates may be included')
    if check.sha(path) != digest:
        raise ValueError('Certificate changed during revalidation')
    return dict(status='REVERIFIED_FROM_NATIVE_CONTROLS', source_path=str(path),
                source_sha256=digest, selected_run_id=reference['summary']['run_id'],
                validated_scope=recalculated['validated_scope'], recomputed=recalculated,
                supporting_certificates=supporting,
                control_raw_evidence_location='Original project run directories; selected-run raw evidence is copied separately')


def copy_checked(source, target, expected):
    if check.sha(source) != expected:
        raise ValueError('Source changed before copying: ' + str(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    if check.sha(target) != expected:
        raise ValueError('Copied file hash mismatch: ' + str(target))


def reproduce_copied_generator(out, selected):
    """Import only the copied renderer; its ROOT resolves to copied data/configs."""
    path = out / 'scripts/rebuild_model.py'
    module = types.ModuleType('_priority_copied_rebuild_model')
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding='utf-8-sig'), str(path), 'exec'), module.__dict__)
    if Path(module.ROOT).resolve() != out.resolve():
        raise ValueError('Copied generator does not resolve its own delivery root')
    result = {}
    for key, run in selected.items():
        cfg = module.load(out / 'config' / ('iwo_' + key + 'nm.json'))
        regenerated, _ = module.render(cfg, key, plots=False)
        if check.commands(regenerated) != check.commands(run['deck']):
            raise ValueError('Copied generator changed source commands for ' + key)
        target = out / 'reproduction' / ('iwo_' + key + 'nm_batch.in')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(regenerated, encoding='ascii', newline='\n')
        result[key] = dict(source_run_id=run['summary']['run_id'],
                           command_equivalence_pass=True,
                           canonical_commands_sha256=delivery.sha_text('\n'.join(check.commands(regenerated)) + '\n'),
                           regenerated_file=target.relative_to(out).as_posix(),
                           regenerated_sha256=check.sha(target), status='INPUT_REGENERATED_NOT_EXECUTED')
    return result


def generate_reports(paths, out):
    # rebuild_report takes one --runs followed by all paths, not repeated --run.
    with contextlib.redirect_stdout(io.StringIO()):
        code = report.main(['--runs', *map(str, paths), '--out', str(out / 'reports')])
    if code != 0:
        raise ValueError('Native scientific report generation failed')
    summary = visual.overview(paths, out / 'overview')
    if set(summary['selected_keys']) != set(KEYS) or summary['missing_keys'] != ['31p8']:
        raise ValueError('Overview must show exactly the priority three with 31.8 nm missing')
    return dict(scientific_report='reports/summary_all_runs.json',
                visual_manifest='overview/OVERVIEW_MANIFEST.json',
                deferred_31p8_panel='No complete verified run selected')


def assessment_rows(selected, certificates):
    rows = []
    for key, run in selected.items():
        value = delivery.measured_metrics(run)
        active, all_points = value['regions']['active'], value['regions']['all']
        rmse = active['rmse_positive_log10_decades']
        endpoint = value['endpoint']['signed_error_percent']
        active_met = bool(active['positive_log_complete'] and rmse is not None
                          and rmse <= TARGETS['active_rmse_log10_decades_max']
                          and abs(endpoint) < TARGETS['absolute_endpoint_error_percent_lt'])
        certificate = certificates.get(key)
        rows.append(dict(key=key, thickness_nm=run['cfg']['curves'][key]['thickness_nm'],
                         run_id=run['summary']['run_id'], metrics=value,
                         active_fit_targets_met=active_met,
                         numerical_status=certificate['status'] if certificate else 'NOT_SUPPLIED',
                         numerical_scope=certificate['validated_scope'] if certificate else 'NOT_VERIFIED_BY_THIS_DELIVERY',
                         full_curve_fit_established=False, predictive_validity_established=False,
                         native_zero_points=all_points['native_zero_count'],
                         native_negative_points=all_points['native_negative_count']))
    return rows


def write_narrative(out, rows):
    lines = ['# Priority-three IWO assessment', '',
             'These are selected completed native ATLAS runs for 2, 6.3 and 13.2 nm. '
             'The 31.8 nm branch is deferred and excluded from this delivery. '
             'The overview retains its explicitly empty 31.8 nm panel.', '',
             'Active targets are fixed at RMSE ≤0.05 decade and absolute +3 V current error <5%, '
             'with complete positive native current on the original active mask. '
             'Numerical scope and full-curve/predictive validity are separate.', '',
             '| Film | Active log RMSE (points) | +3 V error | All-point linear RMSE (A/µm) | Positive logs / targets | Zero / negative | Active targets | Numerical scope |',
             '|---|---:|---:|---:|---:|---:|---|---|']
    for row in rows:
        active = row['metrics']['regions']['active']
        all_points = row['metrics']['regions']['all']
        value = active['rmse_positive_log10_decades']
        rmse = 'unavailable' if value is None else f'{value:.6g}'
        lines.append(f'| {row["thickness_nm"]:g} nm | {rmse} ({active["positive_log_denominator"]}/{active["target_count"]}) '
                     f'| {row["metrics"]["endpoint"]["signed_error_percent"]:+.5g}% '
                     f'| {all_points["rmse_linear_A_per_um"]:.6g} '
                     f'| {all_points["positive_log_denominator"]}/{all_points["target_count"]} '
                     f'| {row["native_zero_points"]} / {row["native_negative_points"]} '
                     f'| {"MET" if row["active_fit_targets_met"] else "NOT MET"} | {row["numerical_scope"]} |')
    lines += ['', 'Selected native run IDs:', '']
    lines += [f'- {row["thickness_nm"]:g} nm: `{row["run_id"]}`.' for row in rows]
    lines += ['', 'Every original measured point and signed native current is retained. '
              'Zero/negative currents have no log residual: they remain counted and remain '
              'in linear errors, with gaps in log plots. No artificial leakage floor is added. '
              'The active mask is an analyst convention, not an instrument detection limit.', '',
              'Each supplied numerical certificate was reloaded against the exact selected '
              'reference, its pinned evidence and native controls. A prior physical candidate’s '
              'certificate is rejected. NOT_SUPPLIED confers no numerical pass. A transferred '
              'width-unit convention is named explicitly and is not a repeated width test.', '',
              'Active target agreement does not establish the complete measured low-current '
              'curve, unique defect species, contact coefficients, quantum transport, calibrated '
              'sputter chemistry or prediction outside these measured conditions. '
              'Full-curve fit and predictive validity are not granted by this package.', '',
              'Selected-run raw evidence is copied under decks/evidence. Numerical certificate '
              'JSONs and their recomputed results are copied under numerical; raw numerical '
              'control runs remain in their original project directories and are identified '
              'by the recorded paths and hashes. The combined deck was assembled from verified '
              'blocks but was not itself executed by the delivery helper.', '']
    (out / 'ASSESSMENT.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')
    readme = '''# IWO priority-three delivery

Read ASSESSMENT.md and PRIORITY_MANIFEST.json for actual residuals, run IDs,
numerical scope and unresolved physical limits. The 31.8 nm model is deferred.

- Complete sequential input: decks/combined/IWO_SELECTED_ALL.in (three devices).
- Individual inputs: decks/individual/iwo_2p0nm.in, iwo_6p3nm.in, iwo_13p2nm.in.
- Every saved STR and transfer LOG has a TonyPlot command in those inputs.
- Fresh scientific reports: reports/; four PNG/PDF overview pairs: overview/.
- Exact evaluated configurations: config/; unchanged measured CSVs: data/.
- Copied renderer: scripts/rebuild_model.py; verified batch reproductions: reproduction/.
- Selected native evidence and filename-equivalence manifest: decks/evidence/ and
  decks/DELIVERY_MANIFEST.json. This nested base package is preserved unchanged.

The helper launches no simulator. Reproduced inputs are code, not new ATLAS
results. To regenerate one batch input using Python with NumPy, run from this
delivery root and choose a new output path:

```powershell
python scripts/rebuild_model.py --config config/iwo_2p0nm.json --key 2p0 --out reproduced/iwo_2p0nm.in --batch
```

The copied generator was actually imported from this delivery and its generated
commands compared with each of the three evaluated source inputs. Only original
gate targets are read during generation; measured current is not used to create
the device. The assembled delivery inputs differ only in checked output filenames,
TonyPlot calls and intermediate QUIT delimiters.

Actual simulator execution requires a fresh working directory and the user's
legitimate Silvaco installation and current execution allowance. Keep future
outputs separate from the copied evidence. Divide signed native current by the
evaluated simulation width for A/µm; multiply by physical width for total amperes.
Do not divide a width-one current again by the 290 µm physical device width.

No numerical scope is inferred from a good fit, no full low-current fit is
inferred from positive-only logarithms, and no predictive/process-physics
certificate is granted. No licensed installation files or manuals are bundled.
'''
    (out / 'README.md').write_text(readme, encoding='utf-8', newline='\n')


def build(paths, directory, certificate_paths=None):
    certificate_paths = certificate_paths or {}
    if set(certificate_paths) - set(KEYS):
        raise ValueError('Certificates may only name priority-three thicknesses')
    sources = [Path(path).resolve() for path in paths]
    out = delivery.output_location(directory, sources)
    selected = selected_runs(paths)
    certificates = {key: verified_certificate(path, selected[key])
                    for key, path in certificate_paths.items()}
    generator = ROOT / 'scripts/rebuild_model.py'
    generator_hash = check.sha(generator)
    rows = assessment_rows(selected, certificates)
    manifest = dict(status='IN_PROGRESS', created_utc=datetime.now(timezone.utc).isoformat(),
                    selected_keys=list(KEYS), deferred_keys=['31p8'], active_fit_targets=TARGETS,
                    selected_runs=rows, numerical_certificates=certificates,
                    full_curve_fit_established=False, predictive_validity_established=False,
                    simulator_launched_by_helper=False)
    json.dumps(manifest, allow_nan=False)
    out.mkdir(parents=True, exist_ok=False)
    status_path = out / 'BUILD_STATUS.json'
    status_path.write_text(json.dumps(dict(status='IN_PROGRESS')), encoding='utf-8')
    try:
        ordered_paths = [run['summary']['directory'] for run in selected.values()]
        base = delivery.package(ordered_paths, out / 'decks')
        manifest['base_delivery_manifest'] = 'decks/DELIVERY_MANIFEST.json'
        manifest['combined_input'] = 'decks/' + base['combined_file']
        copy_checked(generator, out / 'scripts/rebuild_model.py', generator_hash)
        for key, run in selected.items():
            source = Path(run['summary']['directory'])
            copy_checked(source / 'input_config.json', out / 'config' / ('iwo_' + key + 'nm.json'),
                         run['summary']['evidence_sha256']['input_config.json'])
            copy_checked(ROOT / check.DATA[key], out / check.DATA[key], run['summary']['measurement_sha256'])
        manifest['copied_generator_reproduction'] = reproduce_copied_generator(out, selected)
        for key, value in certificates.items():
            folder = out / 'numerical' / key
            copy_checked(Path(value['source_path']), folder / 'original_certificate.json', value['source_sha256'])
            for index, item in enumerate(value['supporting_certificates'], start=1):
                copy_checked(Path(item['source_path']), folder / f'normalization_basis_{index}.json', item['sha256'])
            (folder / 'reverified_certificate.json').write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')
        manifest['reports'] = generate_reports(ordered_paths, out)
        write_narrative(out, rows)
        (out / 'requirements.txt').write_text('numpy==' + report.np.__version__ + '\n', encoding='ascii')
        manifest['implementation_sha256'] = {name: check.sha(ROOT / 'scripts' / name)
            for name in ('rebuild_priority_delivery.py', 'rebuild_delivery.py', 'rebuild_check.py',
                         'rebuild_extension_check.py', 'rebuild_report.py', 'rebuild_overview.py')}
        manifest['copied_generator_sha256'] = generator_hash
        manifest['status'] = 'COMPLETE_PRIORITY_THREE_DELIVERY_NOT_PREDICTIVE_VALIDATION'
        status_path.write_text(json.dumps(dict(status='COMPLETE', simulator_launched=False)), encoding='utf-8')
        manifest['artifact_sha256'] = {path.relative_to(out).as_posix(): check.sha(path)
                                      for path in sorted(out.rglob('*')) if path.is_file()}
        (out / 'PRIORITY_MANIFEST.json').write_text(json.dumps(manifest, indent=2, allow_nan=False), encoding='utf-8')
    except Exception as exc:
        status_path.write_text(json.dumps(dict(status='FAILED_INCOMPLETE_DELIVERY', error=str(exc),
                                              simulator_launched=False)), encoding='utf-8')
        raise
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='append', required=True,
                        help='Explicit completed native run; exactly one per priority thickness')
    parser.add_argument('--certificate', action='append', default=[], metavar='KEY=PATH',
                        help='Optional passing certificate pinned to this exact selected candidate; repeat per key')
    parser.add_argument('--out', required=True, help='New project-local directory outside raw run evidence')
    args = parser.parse_args(argv)
    try:
        value = build(args.run, args.out, certificate_options(args.certificate))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, 'Priority delivery rejected: ' + str(exc) + '\n')
    print(json.dumps(dict(output=str(Path(args.out).resolve()), status=value['status'],
                          selected_keys=value['selected_keys'], deferred_keys=value['deferred_keys'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
