"""Plot explicitly selected complete native runs; never select, fit, or simulate.

The checker revalidates native evidence before any figures are written. Missing
thicknesses remain empty. Nonpositive current stays in linear views and creates
gaps in logarithmic views; it is never replaced by an invented leakage floor.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import textwrap

import rebuild_check as check
from rebuild_report import MASK_DEFINITIONS, metrics, plt, np

ROOT = check.ROOT
THICKNESSES = {'2p0': 2.0, '6p3': 6.3, '13p2': 13.2, '31p8': 31.8}
VIEWS = {
    'overlay_log': 'Transfer curves: logarithmic current',
    'overlay_linear': 'Transfer curves: signed linear current',
    'residual_log': 'Transfer residuals: positive native current only',
    'residual_linear': 'Transfer residuals: all signed native currents',
}
SCOPE = ('Individual native evidence and electrical gates were rechecked. '
         'This overview does not certify mesh/DOS convergence, measurement fit, '
         'unique physical parameters, or experimental process equivalence.')


def validate_output(directory, sources):
    """Accept a new project directory outside any source evidence tree."""
    out = Path(directory).resolve()
    if out == ROOT or not out.is_relative_to(ROOT):
        raise ValueError('Output must be a new directory strictly inside this project')
    if out.exists():
        raise ValueError('Output already exists; choose a new directory')
    # Unfinished neighboring runs have no execution.json but remain immutable
    # native evidence. No overview output belongs anywhere in this namespace.
    if out.is_relative_to((ROOT / 'results/local_session_20260910/runs').resolve()):
        raise ValueError('Output cannot be inside the reserved raw-run namespace')
    for source in sources:
        source = Path(source).resolve()
        if out.is_relative_to(source) or source.is_relative_to(out):
            raise ValueError('Output must be separate from selected source evidence')
    for ancestor in out.parents:
        if (ancestor / 'execution.json').is_file():
            raise ValueError('Output cannot be inside a simulator run directory')
        if ancestor == ROOT:
            break
    return out


def select_runs(paths):
    """Require explicit, unique thicknesses and successful native checks."""
    if not paths:
        raise ValueError('At least one explicit completed run path is required')
    resolved = [Path(path).resolve() for path in paths]
    if len(set(resolved)) != len(resolved):
        raise ValueError('Duplicate source run path')
    selected = {}
    for path in resolved:
        run = check.load_run(path)
        key = run['key']
        if key not in THICKNESSES:
            raise ValueError('Unknown thickness key: ' + str(key))
        if key in selected:
            raise ValueError('More than one run selected for thickness: ' + key)
        if not run['summary']['run_acceptable']:
            raise ValueError('Individual native gates failed: ' + run['summary']['run_id'])
        if len(run['vg']) != 121 or len(run['measured']) != 121:
            raise ValueError('Every selected run must retain all 121 original targets')
        actual_thickness = run['cfg']['curves'][key]['thickness_nm']
        if not np.isclose(actual_thickness, THICKNESSES[key], rtol=0, atol=1e-10):
            raise ValueError('Thickness key and evaluated thickness disagree')
        selected[key] = run
    return {key: selected[key] for key in THICKNESSES if key in selected}


def plotted_data(run):
    """Reuse the report's signed-positive metric policy without changing data."""
    _, linear, logs, regions, _, endpoint = metrics(run)
    current = run['terminal']['id']
    return dict(positive_current=np.where(current > 0, current, np.nan),
                linear_residual=linear, log_residual=logs,
                regions=regions, endpoint=endpoint)


def draw_panel(ax, run, view, values):
    vg, measured, current = run['vg'], run['measured'], run['terminal']['id']
    shared = run['cfg']['shared']
    thickness = THICKNESSES[run['key']]
    title = f'{thickness:g} nm; VD = {shared["vd_V"]:g} V'
    run_id = run['summary']['run_id']
    ax.set_title(title + '\n' + '\n'.join(textwrap.wrap(run_id, width=64)),
                 fontsize=9, pad=8)
    is_log = view.endswith('_log')
    if view.startswith('overlay_'):
        ax.plot(vg, measured, 'o', ms=3.0, color='#222222',
                label='Original measurements (121 points)', zorder=3)
        ax.plot(vg, values['positive_current'] if is_log else current,
                '.-', ms=3.5, lw=1.25, color='#c34d20',
                label='Native ATLAS ID / simulation width')
        if is_log:
            ax.set_yscale('log')
        ax.set_ylabel(('Positive' if is_log else 'Signed') + ' drain current (A/μm)')
        ax.legend(loc='upper left', fontsize=8, framealpha=.95)
    else:
        ax.plot(vg, values['log_residual'] if is_log else values['linear_residual'],
                '.-', ms=3.5, lw=1.0, color='#245a8d')
        ax.axhline(0, color='#222222', lw=.8, ls='--')
        ax.set_ylabel('log₁₀(native ID/W / measured ID)' if is_log
                      else 'Native ID/W − measured ID (A/μm)')
    if not is_log:
        ax.ticklabel_format(axis='y', style='sci', scilimits=(-3, 3))
        if view.startswith('overlay_'):
            ax.axhline(0, color='#888888', lw=.6)
    all_region = values['regions']['all']
    counts = (f'Native: {all_region["native_positive_count"]} positive, '
              f'{all_region["native_zero_count"]} zero, '
              f'{all_region["native_negative_count"]} negative / 121')
    note = counts + ('\nNonpositive values remain gaps; no current floor.' if is_log
                     else '\nAll 121 native signed currents are retained.')
    ax.text(.98, .025, note, ha='right', va='bottom', transform=ax.transAxes,
            fontsize=7.5, bbox=dict(facecolor='white', alpha=.95, edgecolor='#bbbbbb'))
    ax.set(xlabel='Gate voltage, VG (V)', xlim=(float(vg[0]), float(vg[-1])))
    ax.grid(alpha=.22, which='both')
    ax.tick_params(labelsize=9)


def draw_overview(selected, view):
    """Build one figure; missing thicknesses have no substitute data."""
    if view not in VIEWS:
        raise ValueError('Unknown overview view: ' + str(view))
    fig, axes = plt.subplots(2, 2, figsize=(14, 10.5))
    for ax, (key, thickness) in zip(axes.flat, THICKNESSES.items()):
        if key not in selected:
            ax.set_axis_off()
            ax.text(.5, .5, f'{thickness:g} nm\nNo complete verified run selected',
                    ha='center', va='center', fontsize=13, transform=ax.transAxes,
                    color='#555555')
            continue
        run = selected[key]
        draw_panel(ax, run, view, plotted_data(run))
    fig.suptitle('IWO transistor — ' + VIEWS[view], fontsize=15, y=.986)
    fig.text(.5, .040, 'Native currents are divided by the evaluated simulation width; '
             'measurement values are the original A/μm data.', ha='center', fontsize=9)
    fig.text(.5, .020, 'Individual native checks only. Mesh/DOS convergence and '
             'measurement-fit acceptance require separate evidence.', ha='center', fontsize=9)
    fig.tight_layout(rect=(.01, .065, .99, .955), h_pad=2.0, w_pad=2.0)
    return fig


def source_record(run):
    values = plotted_data(run)
    return dict(key=run['key'], thickness_nm=THICKNESSES[run['key']],
                run_id=run['summary']['run_id'],
                source_directory=run['summary']['directory'],
                individual_native_verification=run['summary'],
                source_measurement_file=check.DATA[run['key']],
                measurement_sha256=run['summary']['measurement_sha256'],
                evidence_sha256=run['summary']['evidence_sha256'],
                raw_output_sha256=run['summary']['raw_output_sha256'],
                recomputed_signed_positive_metrics=values['regions'],
                endpoint=values['endpoint'])


def overview(paths, directory):
    # Check destination before expensive evidence reads, then repeat after all
    # checks; mkdir(exist_ok=False) also prevents overwriting a concurrent writer.
    out = validate_output(directory, paths)
    selected = select_runs(paths)
    validate_output(out, [run['summary']['directory'] for run in selected.values()])
    manifest = dict(
        status='OVERVIEW_OF_COMPLETE_NATIVE_RUNS_NOT_A_FIT_CERTIFICATE',
        created_utc=datetime.now(timezone.utc).isoformat(),
        verification_scope=SCOPE,
        selection_policy='Only explicit source run paths; no automatic best-run selection.',
        selected_keys=list(selected), missing_keys=[key for key in THICKNESSES if key not in selected],
        log_policy='Only strictly positive native signed current has a logarithm. Zero and negative '
        'values produce gaps, remain counted, and remain in signed linear views. No current floor, '
        'absolute-value substitution, extrapolation, synthetic current, or preliminary fit is plotted.',
        mask_definitions=MASK_DEFINITIONS,
        source_runs=[source_record(run) for run in selected.values()],
        implementation_sha256={name: check.sha(ROOT / 'scripts' / name)
                               for name in ('rebuild_overview.py', 'rebuild_check.py', 'rebuild_report.py')})
    # Fail on nonserializable/nonfinite metadata before creating the destination.
    json.dumps(manifest, allow_nan=False)
    out.mkdir(parents=True, exist_ok=False)
    for view in VIEWS:
        fig = draw_overview(selected, view)
        try:
            fig.savefig(out / (view + '.png'), dpi=180)
            fig.savefig(out / (view + '.pdf'))
        finally:
            plt.close(fig)
    manifest['figure_sha256'] = {path.name: check.sha(path) for path in sorted(out.iterdir())}
    (out / 'OVERVIEW_MANIFEST.json').write_text(
        json.dumps(manifest, indent=2, allow_nan=False), encoding='utf-8', newline='\n')
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='append', required=True,
                        help='Explicit complete native run path; repeat once per selected thickness')
    parser.add_argument('--out', required=True,
                        help='New project-local output directory, separate from source run evidence')
    args = parser.parse_args(argv)
    try:
        result = overview(args.run, args.out)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, 'Overview rejected: ' + str(exc) + '\n')
    print(json.dumps(dict(output=str(Path(args.out).resolve()), status=result['status'],
                          selected_keys=result['selected_keys'], missing_keys=result['missing_keys'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
