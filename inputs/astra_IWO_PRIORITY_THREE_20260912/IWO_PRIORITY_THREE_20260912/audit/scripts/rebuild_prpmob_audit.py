"""Read-only local PRPMOB diagnostics from a complete, strictly checked run.

Native current, density, mobility and signed Ey remain distinct from the
comparison law and local conductivity proxy. This never launches a simulator.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import shlex

import numpy as np

from rebuild_check import (ROOT, commands, expected_extras, native_log,
                           load_run as strictload_run, sha)
from rebuild_model import render

Q = 1.602176634e-19
SITES = {
    'front': ('bulk_front_electrons', 'front_mobility', 'front_ey'),
    'middle': ('channel_electrons', 'channel_mobility', 'channel_ey'),
    'back': ('bulk_back_electrons', 'back_mobility', 'back_ey'),
}


def output_path(source, destination):
    source, out = Path(source).resolve(), Path(destination).resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        raise ValueError('Output must be a new directory inside the project')
    if out.is_relative_to(ROOT/'results/local_session_20260910/runs'):
        raise ValueError('Output is inside the reserved raw-run namespace')
    if (out.is_relative_to(source)
            or source.parent.name == 'runs' and out.is_relative_to(source.parent)
            or any((p/'execution.json').exists() for p in out.parents if p.is_relative_to(ROOT))):
        raise ValueError('Output must remain outside preserved native run directories')
    return source, out


def probe_definitions(deck):
    result = {}
    for line in commands(deck):
        words = shlex.split(line)
        if words[0] == 'probe':
            parameters = dict(word.split('=', 1) for word in words[1:] if '=' in word)
            name = parameters['name']
            if name in result:
                raise ValueError('Duplicate native probe name: '+name)
            result[name] = dict(parameters=parameters,
                selectors=[word for word in words[1:] if '=' not in word])
    return result


def prepare(source):
    """Require complete native evidence before interpreting any local field."""
    run = strictload_run(Path(source).resolve())
    if run['summary'].get('run_acceptable') is not True:
        raise ValueError('Strict native evidence is not acceptable')
    cfg, key = run['cfg'], run['key']
    diag = cfg.get('diagnostics', {})
    if (cfg['transport']['mode'] != 'prpmob'
            or diag.get('colocate_prp_probes') is not True
            or diag.get('depth_electrons') is not True):
        raise ValueError('Requires PRPMOB, colocate_prp_probes=true and depth_electrons=true')
    mun = float(cfg['curves'][key]['mu_band_cm2Vs'])
    critical = float(cfg['transport']['critical_field_V_cm'])
    if not all(math.isfinite(value) and value > 0 for value in (mun, critical)):
        raise ValueError('MUN and critical field must be finite and positive')
    regenerated, metadata = render(cfg, key)
    if commands(regenerated) != commands(run['deck']):
        raise ValueError('Native commands differ from regenerated saved configuration')
    definitions = probe_definitions(run['deck'])
    coordinates = metadata['colocated_prp_probe_xy_um']
    t_um = cfg['curves'][key]['thickness_nm']/1000
    for site, names in SITES.items():
        x, y = coordinates[site]
        if not -t_um < y < 0:
            raise ValueError('Probe lies outside strict IWO interior')
        for name, selector, direction in zip(names, ('n.conc', 'n.mob', 'field'), (None, '0', '90')):
            p = definitions[name]
            if (selector not in p['selectors']
                    or abs(float(p['parameters']['x'])-x) > 5e-12
                    or abs(float(p['parameters']['y'])-y) > 5e-12
                    or direction is not None and p['parameters'].get('dir') != direction):
                raise ValueError('Native density/mobility/field probes are not colocated: '+name)
    folder = Path(run['summary']['directory'])
    extra = expected_extras(cfg)
    selected, every = native_log(folder/'transfer.log', run['vg'], extra)
    if len(selected) != 121:
        raise ValueError('Requires every one of the 121 original target points')
    fields = {name: selected[:, 11+i] for i, name in enumerate(extra)}
    fields.update(channel_mobility=selected[:, 9], channel_electrons=selected[:, 10])
    local, statistics = {}, {}
    for site, (n_name, mu_name, ey_name) in SITES.items():
        n, mu, ey = (fields[name] for name in (n_name, mu_name, ey_name))
        if not np.isfinite([n, mu, ey]).all() or np.any(n < 0) or np.any(mu <= 0):
            raise ValueError('Need finite nonnegative n, positive mobility and signed finite Ey: '+site)
        ratio = mu/mun
        comparison = 1/(1+abs(ey)/critical)
        difference = ratio-comparison
        relative = difference/comparison
        conductivity = Q*n*mu
        if not np.isfinite([ratio, comparison, difference, relative, conductivity]).all():
            raise ValueError('Nonfinite local diagnostic arithmetic: '+site)
        local[site] = dict(n=n, mu=mu, ey=ey, ratio=ratio, comparison=comparison,
                           difference=difference, relative=relative, conductivity=conductivity)
        worst = int(np.argmax(abs(difference)))
        statistics[site] = dict(xy_um=coordinates[site],
            max_abs_ratio_difference=float(max(abs(difference))),
            max_abs_relative_ratio_difference=float(max(abs(relative))),
            rmse_ratio_difference=float(np.sqrt(np.mean(difference**2))),
            largest_absolute_discrepancy_gate_V=float(run['vg'][worst]),
            density_zero_points=int((n == 0).sum()),
            native_mu_min_cm2_Vs=float(min(mu)), native_mu_max_cm2_Vs=float(max(mu)),
            native_signed_ey_min_V_per_cm=float(min(ey)), native_signed_ey_max_V_per_cm=float(max(ey)))
    width = float(cfg['geometry']['simulation_width_um'])
    rows = []
    for i, vg in enumerate(run['vg']):
        signed_id = float(selected[i, 8]/width)
        observed = float(run['measured'][i])
        row = dict(original_measurement_index=i, vg_V=float(vg), measured_id_A_per_um=observed,
            original_measurement_active_mask=bool(run['active'][i]),
            native_ig_A=float(selected[i, 2]), native_is_A=float(selected[i, 5]), native_id_A=float(selected[i, 8]),
            native_ig_A_per_um=float(selected[i, 2]/width), native_is_A_per_um=float(selected[i, 5]/width),
            native_id_A_per_um=signed_id, native_source_external_V=float(selected[i, 3]),
            native_source_internal_V=float(selected[i, 4]), native_drain_external_V=float(selected[i, 6]),
            native_drain_internal_V=float(selected[i, 7]), signed_linear_residual_A_per_um=signed_id-observed,
            positive_current_log10_residual=float(math.log10(signed_id/observed)) if signed_id > 0 else None)
        for site, values in local.items():
            row.update({site+'_native_n_cm3': float(values['n'][i]),
                site+'_native_mu_cm2_Vs': float(values['mu'][i]),
                site+'_native_signed_ey_V_per_cm': float(values['ey'][i]),
                site+'_native_mu_over_MUN': float(values['ratio'][i]),
                site+'_diagnostic_mu_ratio_from_abs_Ey': float(values['comparison'][i]),
                site+'_diagnostic_ratio_difference': float(values['difference'][i]),
                site+'_diagnostic_relative_ratio_difference': float(values['relative'][i]),
                site+'_diagnostic_local_conductivity_proxy_S_per_cm': float(values['conductivity'][i])})
        rows.append(row)
    execution = json.loads((folder/'execution.json').read_text(encoding='utf-8-sig'))
    synthetic = ('fixture_notice' in execution or run['summary']['run_id'].startswith('SYNTHETIC'))
    summary = dict(status='LOCAL_PRPMOB_DIAGNOSTIC_NOT_PHYSICAL_OR_FIT_ACCEPTANCE',
        evidence_kind='SYNTHETIC_UNIT_TEST_ONLY' if synthetic else 'NATIVE_ATLAS_LOG_AND_EXPORTS',
        run_id=run['summary']['run_id'], source=str(folder), native_target_points=121,
        all_native_rows=len(every), strict_native_evidence=run['summary'],
        native_probe_definitions={name: definitions[name] for names in SITES.values() for name in names},
        native_probe_coordinates_um=coordinates, MUN_cm2_Vs=mun, ECN_MU_V_per_cm=critical,
        comparison_law='mu/MUN compared with 1/(1+abs(native signed Ey)/ECN.MU), GSURFN=1',
        local_comparison_statistics=statistics,
        native_current_policy='Every terminal current comes from native LOG; signed raw A and width-normalized A/um retained. No calculated current replaces it.',
        conductivity_proxy_policy='q*n*mu is local electron conductivity in S/cm. It is not a terminal-current fraction, an integrated conductance or a model of diffusion current.',
        limitations=['Ey approximates the perpendicular field only where current is predominantly lateral; no Ex/current-direction probe is available here.',
                     'N.MOB and FIELD sampling and local current direction can produce disagreement with the simple pointwise comparison law.',
                     'Agreement at three points does not establish full-depth mobility behaviour or mesh/DOS convergence.',
                     'High field or reduced mobility at a depleted point alone does not demonstrate suppression of terminal current.'],
        interpolation_performed=False, artificial_current_or_density_floor=False,
        mesh_or_DOS_convergence_granted=False, measurement_fit_validated=False)
    return dict(run=run, local=local, rows=rows, summary=summary)


def plots(data, out):
    os.environ['MPLCONFIGDIR'] = str(out/'.matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    vg, local = data['run']['vg'], data['local']
    synthetic = data['summary']['evidence_kind'] == 'SYNTHETIC_UNIT_TEST_ONLY'
    title = 'SYNTHETIC UNIT TEST ONLY' if synthetic else 'Native IWO PRPMOB local diagnostic'
    def save(fig, name, note):
        fig.suptitle(title)
        fig.text(.5, .015, note, ha='center', fontsize=8)
        fig.tight_layout(rect=(0, .05, 1, .95))
        fig.savefig(out/(name+'.png'), dpi=170)
        fig.savefig(out/(name+'.pdf'))
        plt.close(fig)
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True)
    for j, (site, values) in enumerate(local.items()):
        axes[0, j].plot(vg, values['ratio'], label='Native mu / MUN', color='#246992')
        axes[0, j].plot(vg, values['comparison'], '--', label='Diagnostic local Ey law', color='#b14f21')
        axes[1, j].plot(vg, values['difference'], color='#695293')
        axes[1, j].axhline(0, color='#777777', lw=.8)
        axes[0, j].set(title=site.capitalize(), ylabel='Mobility ratio')
        axes[1, j].set(ylabel='Native minus comparison ratio', xlabel='Gate voltage (V)')
        axes[0, j].legend(fontsize=8)
    for ax in axes.flat: ax.grid(alpha=.2)
    save(fig, 'mobility_local_field_comparison', 'Pointwise Ey comparison is a diagnostic; local current direction and native field sampling matter.')
    fig, axes = plt.subplots(3, 3, figsize=(13, 9), sharex=True)
    for j, (site, values) in enumerate(local.items()):
        axes[0, j].semilogy(vg, np.where(values['n'] > 0, values['n'], np.nan), color='#246992')
        axes[1, j].plot(vg, values['ey'], color='#695293')
        axes[2, j].plot(vg, values['mu'], color='#b14f21')
        axes[0, j].set(title=site.capitalize(), ylabel='Native n (cm$^{-3}$)')
        axes[1, j].set(ylabel='Native signed Ey (V/cm)')
        axes[2, j].set(ylabel='Native mu (cm$^2$/Vs)', xlabel='Gate voltage (V)')
    for ax in axes.flat: ax.grid(alpha=.2)
    save(fig, 'native_density_field_mobility', 'n, mu and signed Ey share each physical point. Zero density is omitted only from logarithmic view; CSV retains it.')
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for site, values in local.items():
        axes[0].plot(vg, values['conductivity'], label=site.capitalize())
    axes[0].set(xlabel='Gate voltage (V)', ylabel='Local q n mu proxy (S/cm)')
    for name, label in [('id', 'Drain'), ('is', 'Source'), ('ig', 'Gate')]:
        axes[1].plot(vg, data['run']['terminal'][name], label='Native '+label)
    axes[1].set(xlabel='Gate voltage (V)', ylabel='Signed native terminal current (A/um)')
    for ax in axes: ax.grid(alpha=.2); ax.legend(fontsize=8)
    save(fig, 'local_conductivity_and_native_currents', 'Local conductivity is not a terminal-current fraction. Terminal currents come only from native LOG.')


def create_report(source, destination):
    source, out = output_path(source, destination)
    data = prepare(source)
    # Exclusive creation also prevents overwriting a report created during reads.
    out.mkdir(parents=True, exist_ok=False)
    with (out/'native_prpmob_all_121.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data['rows'][0]))
        writer.writeheader(); writer.writerows(data['rows'])
    plots(data, out)
    data['summary'].update(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(Path(__file__)))
    (out/'audit.json').write_text(json.dumps(data['summary'], indent=2, allow_nan=False)+'\n', encoding='utf-8')
    manifest = {str(p.relative_to(out)): sha(p) for p in out.rglob('*') if p.is_file()}
    (out/'report_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return data['summary']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        summary = create_report(args.run, args.out)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, 'No completed PRPMOB audit: '+str(error)+'\n')
    print(json.dumps(dict(status=summary['status'], evidence_kind=summary['evidence_kind'], output=str(args.out.resolve()))))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
