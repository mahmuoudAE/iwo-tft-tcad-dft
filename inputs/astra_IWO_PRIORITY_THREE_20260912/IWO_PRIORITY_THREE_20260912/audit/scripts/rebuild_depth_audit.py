"""Read-only depth/charge diagnostics from complete, strictly verified ATLAS runs.

Front/back probes are point electron densities; ionized trap probes are exposed-
channel box averages (excluding under-contact film). Ionized acceptors are
filled; ionized donors are empty.
No interpolation, leakage floor, or simulator launch occurs.
All report files go in a new --out directory outside preserved native runs.
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
from rebuild_check import (ROOT, DATA, LIMITS, load_run as strictload_run,
                           native_log, expected_extras, sha, commands)
from rebuild_dos_audit import audit as audit_dos

REQUIRED = ('bulk_free_electrons', 'bulk_ionized_acceptors', 'bulk_ionized_donors',
            'bulk_front_electrons', 'bulk_back_electrons')
Q = 1.602176634e-19


def positive_ratio(numerator, denominator):
    """Undefined denominators stay NaN, never a fabricated concentration floor."""
    out = np.full(len(numerator), np.nan)
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        np.divide(numerator, denominator, out=out, where=denominator > 0)
    out[~np.isfinite(out)] = np.nan
    return out


def finite_or_none(value):
    return float(value) if np.isfinite(value) else None


def checked_density(name, values):
    if np.asarray(values).shape != (121,) or not np.isfinite(values).all() or np.any(values < 0):
        raise ValueError('Need 121 finite, nonnegative native density samples: ' + name)
    return values


def current_metrics(vg, measured, simulated, active):
    """Recompute signed original-point metrics; invalid logarithms remain absent."""
    linear = simulated - measured
    logs = np.full(121, np.nan)
    positive = simulated > 0
    logs[positive] = np.log10(simulated[positive]) - np.log10(measured[positive])
    sub = active & (measured <= .01 * measured[-1])
    masks = dict(all=np.ones(121, bool), active=active, low_current=~active,
                 subthreshold=sub, on=active & ~sub)
    stats = {}
    for name, mask in masks.items():
        valid = mask & positive
        count, nlog = int(mask.sum()), int(valid.sum())
        stats[name] = dict(target_count=count, positive_log_denominator=nlog,
            nonpositive_log_excluded=count-nlog, complete_positive_log=(nlog == count and count > 0),
            rmse_linear_A_per_um=float(np.sqrt(np.mean(linear[mask]**2))) if count else None,
            mean_signed_linear_A_per_um=float(np.mean(linear[mask])) if count else None,
            rmse_positive_log10_decades=float(np.sqrt(np.mean(logs[valid]**2))) if nlog else None,
            native_zero_points=int((mask & (simulated == 0)).sum()),
            native_negative_points=int((mask & (simulated < 0)).sum()))
    secants = []
    for a, b in [(-.5,0), (0,.3), (.5,1), (1,1.5), (2.5,3)]:
        ix = [np.flatnonzero(np.isclose(vg, value, rtol=0, atol=1e-9)) for value in (a,b)]
        if any(len(index) != 1 for index in ix):
            raise ValueError('A requested gm endpoint is absent; no interpolation is permitted')
        i, j = int(ix[0][0]), int(ix[1][0])
        secants.append(dict(vg_start_V=a, vg_end_V=b, source_indices=[i,j],
            measured_gm_A_per_um_V=float((measured[j]-measured[i])/(b-a)),
            native_gm_A_per_um_V=float((simulated[j]-simulated[i])/(b-a))))
    return linear, logs, stats, secants


def prepare(run):
    if run['summary'].get('run_acceptable') is not True:
        raise ValueError('Strict native run gates are not acceptable; no depth report generated')
    cfg, key = run['cfg'], run['key']
    if cfg['defects']['bulk'] is not True:
        raise ValueError('Unsupported schema: this depth/charge audit requires enabled continuous bulk DOS')
    extra = expected_extras(cfg)
    if not set(REQUIRED) <= set(extra):
        raise ValueError('Saved run lacks native trap-charge and front/back electron diagnostics')
    folder = Path(run['summary']['directory'])
    native, all_native = native_log(folder/'transfer.log', run['vg'], extra)
    fields = {name: native[:,11+i] for i,name in enumerate(extra)}
    for name in REQUIRED:
        checked_density(name, fields[name])
    checked_density('channel_electrons', native[:,10])
    probe_meta = {}
    for line in commands(run['deck']):
        tokens = shlex.split(line)
        if tokens[0] != 'probe':
            continue
        parameters = {p.split('=',1)[0]:p.split('=',1)[1] for p in tokens[1:] if '=' in p}
        probe_meta[parameters['name']] = dict(parameters=parameters,
            selectors=[p for p in tokens[1:] if '=' not in p])
    thickness_nm = float(cfg['curves'][key]['thickness_nm'])
    t_um, t_cm = thickness_nm * 1e-3, thickness_nm * 1e-7
    for name in ('bulk_front_electrons','bulk_back_electrons'):
        p = probe_meta[name]['parameters']
        if not -t_um < float(p['y']) < 0:
            raise ValueError('Front/back point lies outside the strict IWO interior')
    if float(probe_meta['bulk_front_electrons']['parameters']['y']) <= float(probe_meta['bulk_back_electrons']['parameters']['y']):
        raise ValueError('Front and back coordinates do not follow the direct-stack convention')
    for name in REQUIRED[:3]:
        p = probe_meta[name]
        if ('average' not in p['selectors'] or p['parameters'].get('region') != '2'
                or not math.isclose(float(p['parameters']['y.min']), -t_um, abs_tol=1e-12)
                or float(p['parameters']['y.max']) != 0):
            raise ValueError('Bulk average is not the complete constant-thickness IWO region')
    averages = [probe_meta[name]['parameters'] for name in REQUIRED[:3]]
    if any(any(p[k] != averages[0][k] for k in ('x.min','x.max','y.min','y.max','region')) for p in averages[1:]):
        raise ValueError('Free/occupied native averaging boxes differ')
    capacities = audit_dos(folder, key=key)
    if not capacities['parameter_audit_pass'] or not capacities['simulator_completed']:
        raise ValueError('Native DOS evidence does not verify against saved configuration')
    group = capacities['groups']['bulk']
    if group['enabled']:
        a_cap = group['exports']['afile']['components']['acceptor_total']['analytic_band_truncated_capacity']
        d_cap = group['exports']['dfile']['components']['donor_total']['analytic_band_truncated_capacity']
    else:
        a_cap = d_cap = 0.
    for name, cap in [('bulk_ionized_acceptors',a_cap),('bulk_ionized_donors',d_cap)]:
        if np.any(fields[name] > cap*(1+1e-6)+1e-30):
            raise ValueError('Native ionized population exceeds its available capacity: ' + name)
    n, acc, donor = [fields[name] for name in REQUIRED[:3]]
    front, back = [fields[name] for name in REQUIRED[3:]]
    ratio = positive_ratio(front,back)
    filling = positive_ratio(acc,np.full(121,a_cap))*100
    trapped = positive_ratio(acc,acc+n)*100
    linear, logs, metrics, secants = current_metrics(run['vg'],run['measured'],run['terminal']['id'],run['active'])
    rows = []
    for i, gate in enumerate(run['vg']):
        row = dict(measurement_index=i, vg_V=float(gate),
            measured_A_per_um=float(run['measured'][i]), native_id_A_per_um=float(run['terminal']['id'][i]),
            native_is_A_per_um=float(run['terminal']['is'][i]), native_ig_A_per_um=float(run['terminal']['ig'][i]),
            native_source_external_V=float(native[i,3]), native_source_internal_V=float(native[i,4]),
            native_drain_external_V=float(native[i,6]), native_drain_internal_V=float(native[i,7]),
            channel_electrons_cm3=float(native[i,10]), channel_mobility_cm2_Vs=float(native[i,9]),
            free_sheet_equivalent_cm2=float(n[i]*t_cm), acceptor_sheet_equivalent_cm2=float(acc[i]*t_cm),
            donor_sheet_equivalent_cm2=float(donor[i]*t_cm),
            free_charge_equivalent_C_cm2=float(-Q*n[i]*t_cm),
            acceptor_charge_equivalent_C_cm2=float(-Q*acc[i]*t_cm),
            donor_charge_equivalent_C_cm2=float(Q*donor[i]*t_cm),
            front_to_back_electron_ratio=finite_or_none(ratio[i]),
            acceptor_capacity_occupied_percent=finite_or_none(filling[i]),
            trapped_share_of_free_plus_acceptors_percent=finite_or_none(trapped[i]),
            signed_linear_residual_A_per_um=float(linear[i]), positive_log10_residual=finite_or_none(logs[i]),
            original_measurement_active_mask=bool(run['active'][i]))
        row.update({name+('_cm3' if name.startswith('bulk_') else '_cm2_Vs' if 'mobility' in name else '_V_per_cm'):float(value[i]) for name,value in fields.items()})
        rows.append(row)
    warnings = list(capacities['warnings'])
    for name in REQUIRED[3:]:
        if np.all(fields[name] == 0):
            warnings.append(name+' is zero at every gate; the point probe is uninformative until separately checked')
    summary = dict(status='VERIFIED_NATIVE_DEPTH_AND_AVERAGE_CHARGE_DIAGNOSTIC_NOT_FIT_ACCEPTANCE',
        run_id=run['summary']['run_id'], key=key, thickness_nm=thickness_nm,
        native_gate_points=121, native_raw_rows=len(all_native), source=str(folder),
        measurement_source=str(ROOT/DATA[key]), measurement_sha256=sha(ROOT/DATA[key]),
        strict_native_evidence=run['summary'], probe_definitions=probe_meta, native_DOS_audit=capacities,
        available_bulk_acceptor_capacity_cm3=a_cap, available_bulk_donor_capacity_cm3=d_cap,
        warnings=warnings, current_metrics=metrics, original_endpoint_gm_secants=secants,
        endpoint_error_percent=float(100*(run['terminal']['id'][-1]/run['measured'][-1]-1)),
        depth_point_signatures={name:dict(minimum_cm3=float(fields[name].min()),maximum_cm3=float(fields[name].max()),
            zero_points=int((fields[name]==0).sum())) for name in REQUIRED},
        selected_native_states=[rows[i] for i in range(121) if any(math.isclose(rows[i]['vg_V'],v,abs_tol=1e-9) for v in [-3,-1.5,0,.5,1,2,3])],
        front_back_ionized_trap_density_available=False,
        interpretation='Front/back values are local free-electron densities. Ionized acceptor/donor values are exposed-channel box averages, excluding under-contact film. '
                       'Ionized acceptors are electron-filled and negative; ionized donors are empty and positive. '
                       'Density nonuniformity does not establish a nonuniform ND/material profile or a conducting path. '
                       'Equivalent sheet charge is the native full-thickness box average times thickness, not an independent spatial integral; '
                       'it excludes other Poisson/electrode contributions.',
        probe_unit_reference='ATLAS 5.28.1.R manual: AVERAGE p1530, box integration p1535, REGION p1537, point X/Y p1539.',
        interpolation_performed=False, artificial_current_or_density_floor=False,
        current_log_policy='Signed positive native current only; nonpositive logarithms are null and counted. All121 linear residuals retained.',
        mesh_or_DOS_convergence_granted=False, measurement_fit_validated=False)
    return dict(run=run, native=native, fields=fields, rows=rows, summary=summary, t_cm=t_cm,
                ratio=ratio, filling=filling, trapped=trapped)


def plot_report(data, directory, plt):
    run, fields, t_cm = data['run'], data['fields'], data['t_cm']
    vg = run['vg']; thickness = data['summary']['thickness_nm']
    def save(fig,name):
        fig.tight_layout(rect=(0,.075,1,.93))
        fig.savefig(directory/(name+'.png'),dpi=180)
        fig.savefig(directory/(name+'.pdf'))
        plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5.2))
    for name,label,color in [('bulk_front_electrons','Front: local n near Al2O3','#b14f21'),
                             ('bulk_back_electrons','Back: local n near Air','#246992')]:
        values=fields[name]; ax.semilogy(vg,np.where(values>0,values,np.nan),'.-',ms=3,lw=1.3,label=label,color=color)
    ax.semilogy(vg,np.where(data['native'][:,10]>0,data['native'][:,10],np.nan),ls='--',lw=1,label='Interior point n',color='#695293')
    values=fields['bulk_free_electrons']; ax.semilogy(vg,np.where(values>0,values,np.nan),ls=':',lw=1.8,label='Exposed-channel box average n',color='#444444')
    ax.set(xlabel='Gate voltage (V)',ylabel=r'Native electron density (cm$^{-3}$)',xlim=(-3,3))
    ax.grid(alpha=.2); ax.legend(fontsize=9)
    fig.suptitle(f'IWO {thickness:g} nm: native front/back electron density, VD={run["cfg"]["shared"]["vd_V"]:g} V')
    fig.text(.5,.025,'Local density is not donor density or proof of conduction. Zero values are omitted from log view; CSV retains all121.',ha='center',fontsize=8.5)
    save(fig,'native_front_back_density')
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for name,label,color,sign in [('bulk_free_electrons','Free electrons','#246992',-1),
        ('bulk_ionized_acceptors','Ionized acceptors','#b14f21',-1),('bulk_ionized_donors','Ionized donors','#555555',1)]:
        values=fields[name]*t_cm
        axes[0].plot(vg,values,color=color,label=label,lw=1.6)
        axes[1].plot(vg,sign*Q*values*1e6,color=color,label=label,lw=1.6)
    axes[0].axhline(data['summary']['available_bulk_acceptor_capacity_cm3']*t_cm,ls='--',color='#777777',lw=1,label='Acceptor capacity')
    axes[0].set(ylabel=r'Equivalent sheet number (cm$^{-2}$)')
    axes[1].set(ylabel=r'Equivalent signed charge ($\mu$C/cm$^2$)')
    for ax in axes: ax.set(xlabel='Gate voltage (V)',xlim=(-3,3)); ax.grid(alpha=.2); ax.legend(fontsize=8)
    fig.suptitle(f'IWO {thickness:g} nm: native exposed-channel free and ionized-trap charge')
    fig.text(.5,.025,'Average density × full IWO thickness; not front/back-resolved trapped charge or total gate charge. All native signs retained.',ha='center',fontsize=8.5)
    save(fig,'native_average_charge')
    fig,axes=plt.subplots(1,2,figsize=(12,4.7))
    axes[0].semilogy(vg,np.where(data['ratio']>0,data['ratio'],np.nan),color='#246992',lw=1.7)
    axes[0].axhline(1,color='#777777',ls='--',lw=1); axes[0].set(ylabel='Front / back local electron density')
    axes[1].plot(vg,data['filling'],color='#b14f21',label='Acceptor capacity filled')
    axes[1].plot(vg,data['trapped'],color='#695293',label='Trapped share of free + acceptor electrons')
    axes[1].set(ylabel='Percent',ylim=(0,101)); axes[1].legend(fontsize=8)
    for ax in axes: ax.set(xlabel='Gate voltage (V)',xlim=(-3,3)); ax.grid(alpha=.2)
    fig.suptitle(f'IWO {thickness:g} nm: spatial population contrast and average trap filling')
    fig.text(.5,.025,'Ratios with zero denominator are undefined, not floor-repaired. Contrast alone does not establish material nonuniformity.',ha='center',fontsize=8.5)
    save(fig,'native_depth_and_filling')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs',nargs='+',type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args(argv)
    out=args.out.resolve(); sources=[p.resolve() for p in args.runs]
    if not out.is_relative_to(ROOT) or out.exists():
        parser.error('--out must be a new directory inside the project')
    if out.is_relative_to((ROOT / 'results/local_session_20260910/runs').resolve()):
        parser.error('--out must stay outside the reserved raw-run namespace')
    if len(set(sources)) != len(sources): parser.error('Duplicate source run')
    if (any(out.is_relative_to(path) for path in sources)
            or any(path.parent.name == 'runs' and out.is_relative_to(path.parent) for path in sources)
            or any((p/'execution.json').is_file() for p in out.parents if p.is_relative_to(ROOT))):
        parser.error('--out must be outside every preserved native run directory')
    try:
        prepared=[prepare(strictload_run(path)) for path in sources]
    except (ValueError,KeyError,TypeError,OSError) as error:
        parser.exit(2,'No report generated: '+str(error)+'\n')
    # No output is created before every input has passed strict evidence/schema checks.
    out.mkdir(parents=True,exist_ok=False)
    os.environ['MPLCONFIGDIR']=str(out/'.matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'axes.labelsize':11,'figure.dpi':150})
    summaries=[]
    for i,data in enumerate(prepared,start=1):
        destination=out/f'{i:02d}_{data["run"]["key"]}nm'; destination.mkdir()
        with (destination/'native_depth_all_121.csv').open('w',newline='',encoding='utf-8') as handle:
            writer=csv.DictWriter(handle,fieldnames=list(data['rows'][0])); writer.writeheader(); writer.writerows(data['rows'])
        plot_report(data,destination,plt)
        summary=data['summary']; summary['report_directory']=str(destination)
        (destination/'audit.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        summaries.append(summary)
    overview=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(Path(__file__)),
        status='NATIVE_DEPTH_DIAGNOSTICS_NOT_A_CALIBRATION_CERTIFICATE',runs=summaries,
        limitations=['No front/back ionized-trap probes exist in this schema; ionized charge is an exposed-channel box average.',
                     'Spatially varying electrons do not by themselves establish a spatial donor/material profile.',
                     'Per-run strict checks do not replace independent mesh, width or DOS convergence checks.'])
    (out/'summary.json').write_text(json.dumps(overview,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    (out/'report_manifest.json').write_text(json.dumps({str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=overview['status'],output=str(out),runs=len(prepared))))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
