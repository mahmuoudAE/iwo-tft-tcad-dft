"""Scientific reports of verified native rebuild output, without solver launches.

All original points and signed terminal currents are retained. Zero/negative
drain current has no valid logarithmic residual and is never drawn as leakage
at an arbitrary plotting floor. This report does not grant fit acceptance.
"""
import argparse
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parents[1]/'tmp/matplotlib'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from rebuild_check import ROOT, DATA, LIMITS, load_run, native_log, expected_extras, sha, table

MASK_DEFINITIONS = {
    'all': 'All 121 original measured gate points.',
    'active': 'Measured I > 5*median(measured I for -2<=VG<=-0.5 V); 31.8 nm uses all points.',
    'low_current': 'Complement of active; an analysis mask, not an instrument detection limit.',
    'subthreshold': 'Active points with measured I <= 0.01*measured I at +3 V; a scoring region, not a fitted physical threshold.',
    'on': 'Active points excluding the subthreshold scoring region.',
}
GUARD_A_PER_UM = 1e-40
MASK_SENSITIVITY_FACTORS = (1, 3, 5, 10)


def metrics(run):
    """Pure numerical diagnostics. Missing logarithms remain NaN internally."""
    measured, current = run['measured'], run['terminal']['id']
    active = run['active']
    sub = active & (measured <= .01 * measured[-1])
    masks = dict(all=np.ones(len(current), dtype=bool), active=active,
                 low_current=~active, subthreshold=sub, on=active & ~sub)
    positive = current > 0
    linear = current - measured
    logs = np.full(len(current), np.nan)
    logs[positive] = np.log10(current[positive]) - np.log10(measured[positive])
    regions = {}
    for name, mask in masks.items():
        valid = mask & positive
        count, nlog = int(mask.sum()), int(valid.sum())
        regions[name] = dict(
            target_count=count, linear_denominator=count,
            rmse_linear_A_per_um=float(np.sqrt(np.mean(linear[mask]**2))) if count else None,
            mean_signed_linear_residual_A_per_um=float(np.mean(linear[mask])) if count else None,
            max_absolute_linear_residual_A_per_um=float(max(abs(linear[mask]))) if count else None,
            positive_log_denominator=nlog, excluded_nonpositive_log_count=count-nlog,
            positive_log_complete=nlog == count and count > 0,
            rmse_positive_log10_decades=float(np.sqrt(np.mean(logs[valid]**2))) if nlog else None,
            mean_positive_log10_residual=float(np.mean(logs[valid])) if nlog else None,
            max_absolute_positive_log10_residual=float(max(abs(logs[valid]))) if nlog else None,
            native_positive_count=int((mask & (current > 0)).sum()),
            native_zero_count=int((mask & (current == 0)).sum()),
            native_negative_count=int((mask & (current < 0)).sum()))
    guarded = np.log10(np.maximum(abs(current), GUARD_A_PER_UM)) - np.log10(measured)
    diagnostic = dict(
        status='DIAGNOSTIC_ONLY_NOT_A_VALID_SIGNED_CURRENT_LOG_FIT',
        definition='log10(max(abs(native signed ID/W), 1e-40 A/um) / measured ID). Uses magnitudes and a numerical guard, never plotted as simulated leakage.',
        guard_A_per_um=GUARD_A_PER_UM, denominator=len(current),
        guarded_point_count=int((abs(current) < GUARD_A_PER_UM).sum()),
        negative_magnitude_point_count=int((current < 0).sum()),
        rmse_guarded_magnitude_log10_decades=float(np.sqrt(np.mean(guarded**2))))
    endpoint = dict(vg_V=float(run['vg'][-1]), measured_A_per_um=float(measured[-1]),
                    native_signed_A_per_um=float(current[-1]),
                    signed_relative_error=float(current[-1] / measured[-1] - 1),
                    signed_error_percent=float(100 * (current[-1] / measured[-1] - 1)))
    return masks, linear, logs, regions, diagnostic, endpoint


def active_mask_sensitivity(run):
    """Diagnostics for fixed analyst cutoffs; never change the factor-5 mask."""
    vg, measured, current = run['vg'], run['measured'], run['terminal']['id']
    reference_points = (vg >= -2) & (vg <= -.5)
    if not reference_points.any():
        raise ValueError('Mask sensitivity requires measured points from -2 to -0.5 V')
    reference = float(np.median(measured[reference_points]))
    if not np.isfinite(reference) or reference <= 0:
        raise ValueError('Measured low-current reference must be finite and positive')
    thick_all = run['key'] == '31p8'
    acceptance = np.ones(len(current), dtype=bool) if thick_all else measured > 5 * reference
    if not np.array_equal(run['active'], acceptance):
        raise ValueError('Existing active mask differs from fixed factor-5 acceptance definition')
    fields = ('target_count', 'linear_denominator', 'rmse_linear_A_per_um',
              'positive_log_denominator', 'excluded_nonpositive_log_count',
              'positive_log_complete', 'rmse_positive_log10_decades',
              'native_positive_count', 'native_zero_count', 'native_negative_count')
    rows = []
    for factor in MASK_SENSITIVITY_FACTORS:
        mask = np.ones(len(current), dtype=bool) if thick_all else measured > factor * reference
        # A shallow copy changes only the diagnostic mask, preserving all inputs.
        _, _, _, regions, _, _ = metrics(dict(run, active=mask))
        region = regions['active']
        row = dict(reference_multiplier=factor, threshold_A_per_um=factor * reference,
                   is_original_acceptance_mask=factor == 5,
                   all_points_override_for_31p8=thick_all)
        row.update({name: region[name] for name in fields})
        rows.append(row)
    return dict(
        status='DIAGNOSTIC_MASK_SENSITIVITY_NOT_OPTIMIZATION_OR_NEW_ACCEPTANCE',
        definition='Thin films: measured ID > factor times the fixed measured median over -2<=VG<=-0.5 V. '
        '31.8 nm: all original points for every factor. These analyst thresholds are not instrument detection limits.',
        measured_reference_A_per_um=reference, reference_gate_range_V=[-2, -.5],
        original_acceptance_multiplier=5, original_active_mask_preserved=True,
        original_target_count=len(current), all_native_current_points_preserved=True,
        positive_log_policy='Nonpositive native currents stay in signed linear errors and sign counts; '
        'their log residuals are unavailable, with explicit positive-only denominators and completeness.',
        rows=rows)


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def save_figure(fig, path):
    fig.tight_layout()
    fig.savefig(path.with_suffix('.png'), dpi=180)
    fig.savefig(path.with_suffix('.pdf'))
    plt.close(fig)


def plots(run, directory, linear, logs):
    vg, measured, current = run['vg'], run['measured'], run['terminal']['id']
    thickness = run['cfg']['curves'][run['key']]['thickness_nm']
    positive_only = np.where(current > 0, current, np.nan)
    zeros, negatives = int((current == 0).sum()), int((current < 0).sum())
    omission = f'Native zero: {zeros}/121; negative: {negatives}/121\nLog views omit these points; no artificial current floor.'
    title = f'IWO {thickness:g} nm; VD = {run["cfg"]["shared"]["vd_V"]:g} V'
    for scale in ('linear', 'log'):
        fig, ax = plt.subplots(figsize=(8.2, 5.2))
        ax.plot(vg, measured, 'o', color='#202020', ms=3.5, label='Original Excel measurements', zorder=3)
        ax.plot(vg, current if scale == 'linear' else positive_only,
                color='#c04721', lw=1.5, marker='.', ms=3, label='Native ATLAS signed ID / width')
        if scale == 'log':
            ax.set_yscale('log')
            ax.text(.025, .03, omission, transform=ax.transAxes, fontsize=8,
                    va='bottom', bbox=dict(facecolor='white', alpha=.9, edgecolor='#b0b0b0'))
        else:
            ax.axhline(0, color='#888888', lw=.6)
            ax.ticklabel_format(axis='y', style='sci', scilimits=(-3, 3))
        ax.set(xlabel='Gate voltage, VG (V)',
               ylabel='Signed drain current (A/μm)' if scale == 'linear' else 'Positive drain current (A/μm)',
               title=title + '\nNative simulation and measurements; fit acceptance not inferred',
               xlim=(float(vg[0]), float(vg[-1])))
        ax.grid(alpha=.22, which='both')
        ax.legend(loc='best', fontsize=9)
        save_figure(fig, directory / ('overlay_' + scale))

        fig, ax = plt.subplots(figsize=(8.2, 4.6))
        ax.plot(vg, linear if scale == 'linear' else logs, '.-', color='#245a8d', ms=4, lw=1)
        ax.axhline(0, color='#202020', lw=.8, ls='--')
        if scale == 'log':
            ax.text(.025, .03, omission, transform=ax.transAxes, fontsize=8,
                    va='bottom', bbox=dict(facecolor='white', alpha=.9, edgecolor='#b0b0b0'))
        else:
            ax.ticklabel_format(axis='y', style='sci', scilimits=(-3, 3))
        ax.set(xlabel='Gate voltage, VG (V)',
               ylabel='Native ID/W − measured ID (A/μm)' if scale == 'linear'
               else 'log10(positive native ID/W / measured ID)',
               title=title + ('\nSigned residuals: all 121 original points' if scale == 'linear'
                              else '\nValid positive-current logarithmic residuals'),
               xlim=(float(vg[0]), float(vg[-1])))
        ax.grid(alpha=.22)
        save_figure(fig, directory / ('residual_' + scale))

    # Additional zoom uses the frozen measurement-based mask. Full views above
    # retain every original point, including the unresolved low-current region.
    active = run['active']
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 6.8), sharex=True)
    axes[0].semilogy(vg[active], measured[active], 'o', color='#202020', ms=3.5,
                     label='Original Excel measurements')
    axes[0].semilogy(vg[active], positive_only[active], '.-', color='#c04721',
                     ms=4, lw=1.5, label='Native ATLAS ID / width')
    axes[0].set(ylabel='Positive drain current (A/μm)',
                title=title + '\nActive-region detail; low-current results are in the full views')
    axes[0].legend(fontsize=9)
    axes[1].plot(vg[active], logs[active], '.-', color='#245a8d', ms=4, lw=1)
    axes[1].axhline(0, color='#202020', lw=.8, ls='--')
    axes[1].set(xlabel='Gate voltage, VG (V)', ylabel='log10(native / measured)')
    for ax in axes:
        ax.grid(alpha=.22, which='both')
    save_figure(fig, directory / 'active_detail')


def report_run(run, directory):
    directory.mkdir()
    masks, linear, logs, regions, diagnostic, endpoint = metrics(run)
    folder = Path(run['summary']['directory'])
    extra = expected_extras(run['cfg'])
    native, _ = native_log(folder / 'transfer.log', run['vg'], extra)
    original = table(ROOT / DATA[run['key']])
    width = run['summary']['width_um']
    currents = run['terminal']
    kcl = currents['id'] + currents['is'] + currents['ig']
    kcl_bound = LIMITS['kcl_absolute_A_per_um'] + LIMITS['kcl_relative'] * (
        abs(currents['id']) + abs(currents['is']) + abs(currents['ig']))
    rows = []
    for index, vg in enumerate(run['vg']):
        row = dict(measurement_index=index, original_source_row=original[index].get('source_row', ''),
                   vg_V=float(vg), native_vg_V=float(native[index, 0]),
                   native_vd_V=float(native[index, 6]), native_vs_V=float(native[index, 3]),
                   native_vd_internal_V=float(native[index, 7]), native_vs_internal_V=float(native[index, 4]),
                   measured_A_per_um=float(run['measured'][index]), simulation_width_um=width,
                   native_id_signed_A=float(native[index, 8]), native_is_signed_A=float(native[index, 5]),
                   native_ig_signed_A=float(native[index, 2]),
                   native_id_signed_A_per_um=float(currents['id'][index]),
                   native_is_signed_A_per_um=float(currents['is'][index]),
                   native_ig_signed_A_per_um=float(currents['ig'][index]),
                   native_channel_electrons_cm3=float(native[index, 10]),
                   native_channel_mobility_cm2_Vs=float(native[index, 9]),
                   linear_residual_A_per_um=float(linear[index]),
                   positive_log10_residual=float(logs[index]) if np.isfinite(logs[index]) else '',
                   positive_log_valid=bool(np.isfinite(logs[index])),
                   kcl_residual_A_per_um=float(kcl[index]), kcl_bound_A_per_um=float(kcl_bound[index]),
                   kcl_pass=bool(abs(kcl[index]) <= kcl_bound[index]))
        row.update({name: bool(mask[index]) for name, mask in masks.items()})
        row.update({'native_' + name + ('_cm3' if name.startswith('bulk_') else '_cm2_Vs' if 'mobility' in name else '_V_per_cm'):
                    float(native[index, 11+offset]) for offset, name in enumerate(extra)})
        rows.append(row)
    csvpath = directory / 'native_comparison_all_121.csv'
    write_csv(csvpath, rows)
    plots(run, directory, linear, logs)
    summary = dict(run_id=run['summary']['run_id'], key=run['key'],
                   thickness_nm=run['cfg']['curves'][run['key']]['thickness_nm'],
                   source_directory=str(folder), report_directory=str(directory),
                   status='REAL_NATIVE_ATLAS_DIAGNOSTIC_REPORT_NOT_A_FIT_ACCEPTANCE',
                   measurement_fit_validated=False,
                   per_run_raw_evidence=run['summary'], mask_definitions=MASK_DEFINITIONS,
                   off_reference_A_per_um=float(np.median(run['measured'][(run['vg'] >= -2) & (run['vg'] <= -.5)])),
                   positive_log_policy='log10(native signed ID/W / measurement) only where native ID/W > 0. Zero and negative points remain in CSV with a blank logarithmic residual. Positive-only log RMSE must be read with its explicit denominator.',
                   regions=regions, endpoint=endpoint, guarded_all_log_diagnostic=diagnostic,
                   active_mask_sensitivity=active_mask_sensitivity(run),
                   produced_files_sha256={p.name: sha(p) for p in directory.iterdir() if p.is_file()})
    (directory / 'run_summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False), encoding='utf-8')
    return summary


def summary_row(summary):
    raw = summary['per_run_raw_evidence']
    row = dict(run_id=summary['run_id'], key=summary['key'], thickness_nm=summary['thickness_nm'],
               source_directory=summary['source_directory'], report_directory=summary['report_directory'],
               individual_raw_run_acceptable=raw['run_acceptable'], kcl_pass=raw['kcl_recomputed_pass'],
               native_probes_pass=raw['native_probes_pass'], native_zero_points=raw['drain_signs']['zero'],
               native_negative_points=raw['drain_signs']['negative'],
               ion_signed_relative_error=summary['endpoint']['signed_relative_error'])
    for name, values in summary['regions'].items():
        for metric in ('target_count', 'linear_denominator', 'rmse_linear_A_per_um',
                       'positive_log_denominator', 'excluded_nonpositive_log_count', 'rmse_positive_log10_decades'):
            row[name + '_' + metric] = values[metric]
    row['DIAGNOSTIC_guarded_magnitude_all_log_rmse_decades'] = summary['guarded_all_log_diagnostic']['rmse_guarded_magnitude_log10_decades']
    row['DIAGNOSTIC_guarded_magnitude_denominator'] = summary['guarded_all_log_diagnostic']['denominator']
    for entry in summary.get('active_mask_sensitivity', {}).get('rows', []):
        prefix = 'DIAGNOSTIC_mask_factor_' + str(entry['reference_multiplier']) + '_'
        for metric in ('target_count', 'positive_log_denominator', 'excluded_nonpositive_log_count',
                       'positive_log_complete', 'rmse_linear_A_per_um', 'rmse_positive_log10_decades'):
            row[prefix + metric] = entry[metric]
    return row


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', nargs='+', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.out.resolve()
    paths = [p.resolve() for p in args.runs]
    if not out.is_relative_to(ROOT):
        parser.error('--out must stay inside this project')
    if out.exists():
        parser.error('--out must be a new report directory; existing artifacts are preserved')
    # A currently running neighbor lacks execution.json. Reserve every raw-run
    # path regardless of completion state or the selected report sources.
    if out.is_relative_to((ROOT / 'results/local_session_20260910/runs').resolve()):
        parser.error('--out must stay outside the reserved raw-run namespace')
    if len(set(paths)) != len(paths):
        parser.error('Duplicate source run directory')
    if any(out.is_relative_to(p) for p in paths) or any(
            (parent / 'execution.json').is_file() for parent in out.parents if parent.is_relative_to(ROOT)):
        parser.error('--out must be outside every native run directory')
    # Fail before creating reports if any requested source is incomplete/tampered.
    runs = [load_run(path) for path in paths]
    out.mkdir(parents=True, exist_ok=False)
    summaries = []
    for index, run in enumerate(runs, start=1):
        directory = out / f'{index:02d}_{run["key"]}nm'
        summaries.append(report_run(run, directory))
    flat = [summary_row(s) for s in summaries]
    write_csv(out / 'summary_all_runs.csv', flat)
    keys = {s['key'] for s in summaries}
    overview = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                    status='SCIENTIFIC_REPORT_OF_NATIVE_RUNS_NOT_FIT_ACCEPTANCE',
                    all_original_points_retained=True, native_log_currents_used=True,
                    interpolation_or_artificial_leakage_added=False,
                    positive_log_policy='Nonpositive native currents have no logarithm. Denominators are reported for every scoring region; guarded magnitude metrics are separate diagnostics only.',
                    mask_definitions=MASK_DEFINITIONS, measurement_fit_validated=False,
                    included_thickness_keys=sorted(keys), missing_thickness_keys=sorted(set(DATA)-keys),
                    all_four_thicknesses_present=keys == set(DATA),
                    limitations=['Per-run raw gates do not replace independent width/x/y/DOS checks.',
                                 'A positive-only log RMSE cannot characterize omitted zero/negative currents.',
                                 'This report does not establish a unique physical parameter set or a user-approved fit tolerance.'],
                    summary_table=flat, runs=summaries)
    (out / 'summary_all_runs.json').write_text(json.dumps(overview, indent=2, allow_nan=False), encoding='utf-8')
    # Record all report hashes except this manifest itself; native hashes reside in each summary.
    (out / 'report_manifest.json').write_text(json.dumps(
        {str(p.relative_to(out)).replace('\\', '/'): sha(p) for p in out.rglob('*') if p.is_file()}, indent=2), encoding='utf-8')
    print(json.dumps(dict(output=str(out), runs=len(runs), all_four_thicknesses_present=keys == set(DATA))))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
