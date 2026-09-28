#!/usr/bin/env python3
"""Run and calibrate REAL local ATLAS evaluations; never substitutes a Python fit.

Examples (from package root):
 python scripts/atlas_workflow.py --mode dry-run --thickness 2
 python scripts/atlas_workflow.py --mode smoke --thickness 2
 python scripts/atlas_workflow.py --mode run --thickness 2
 python scripts/atlas_workflow.py --mode fit --thickness 2 --stage electrostatic

Requires a licensed local ATLAS/DeckBuild installation with relevant TFT features.
The provided argv may need adjustment for the locally installed DeckBuild version.
"""
from __future__ import annotations
import argparse, copy, csv, hashlib, json, re, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from generate_atlas import ROOT,load_config,generate,key_from_thickness,read_data
from local_probe import run as bounded_run

class SimulationError(RuntimeError): pass


def read_xy(path:Path):
    """Read numeric two-column DeckBuild EXTRACT output, skipping text headers.
    Preserve sign. Duplicate bias points: last solver solution is retained.
    """
    if not path.is_file():raise SimulationError(f'Missing ATLAS export: {path}')
    points=[]
    for line in path.read_text(errors='replace').splitlines():
        words=line.replace(',',' ').split()
        if len(words)!=2:continue
        try:x,y=(float(z.replace('D','E').replace('d','e')) for z in words)
        except ValueError:continue
        if np.isfinite(x) and np.isfinite(y):points.append((x,y))
    if len(points)<3:raise SimulationError(f'Fewer than3 numerical rows in {path}; check EXTRACT syntax')
    arr=np.array(points)
    # Do not silently merge a forward/reverse loop into an equilibrium curve.
    if np.any(np.diff(arr[:,0]) < -1e-9):raise SimulationError('Export is not an increasing DC sweep')
    unique={float(x):float(y) for x,y in arr}
    x=np.array(sorted(unique));y=np.array([unique[v] for v in x])
    return x,y


def check_coverage(x:np.ndarray,vg:np.ndarray):
    if x[0]>min(vg)+1e-7 or x[-1]<max(vg)-1e-7:raise SimulationError('Incomplete transfer sweep: endpoint missing')
    # Adaptive inserted points are allowed; every explicitly requested target is required.
    distance=np.min(abs(x[:,None]-vg[None,:]),axis=0)
    if np.any(distance>1e-6):raise SimulationError(f'ATLAS did not export {int((distance>1e-6).sum())} requested gate points')


def execute(cfg:dict,key:str,runner:dict,dest:Path,vg:np.ndarray,smoke=False):
    if dest.exists():raise SimulationError(f'Refusing to reuse a run directory: {dest}')
    text,meta=generate(cfg,key,vg,smoke=smoke)
    bounded_run(runner['argv'],text,key+('_smoke' if smoke else '_full'),runner['timeout_seconds'],dest,cfg,False)
    (dest/'metadata.json').write_text(json.dumps(meta,indent=2))
    try:
        result=validate_run(cfg,key,runner,dest,vg,smoke)
    except SimulationError as exc:
        (dest/'failure.json').write_text(json.dumps({'status':'VALIDATION_FAILED','error':str(exc)},indent=2))
        raise
    return result


def validate_run(cfg,key,runner,dest,vg,smoke=False):
    launch=json.loads((dest/'execution.json').read_text())
    if launch['returncode']!=0:raise SimulationError(f'Launcher failed: {launch["status"]}; inspect {dest}')
    outputs='\n'.join((dest/name).read_text(errors='replace') for name in ['launcher_stdout.txt','launcher_stderr.txt','deckbuild.out'] if (dest/name).exists())
    error_patterns=[r'invalid\s+parameter',r'unknown\s+(?:parameter|statement|material)',r'license.*(?:denied|failed|unavailable)',r'cannot\s+open',r'error\s*#',r'fatal\s+error',r'Error:',r'Error extracting',r'Cannot trap',r'convergence problem',r'can not find a version']
    if any(re.search(pat,outputs,re.I) for pat in error_patterns):
        raise SimulationError(f'Simulator/parser/license error detected; inspect {dest}/deckbuild.out')
    if not re.search(r'ATLAS version .* finished',outputs):raise SimulationError('Missing ATLAS completion evidence')
    for name,expected in (launch['outputs'].items() if isinstance(launch['outputs'],dict) else []):
        if hashlib.sha256((dest/name).read_bytes()).hexdigest()!=expected:raise SimulationError(f'Output hash changed: {name}')
    for name in ['equilibrium.str','final.str']:
        if not (dest/name).is_file():raise SimulationError(f'Missing structure {name}')
    xv,idraw=read_xy(dest/'idvg.dat');xg,ig=read_xy(dest/'igvg.dat');xs,iss=read_xy(dest/'isvg.dat')
    check_coverage(xv,vg);check_coverage(xg,vg);check_coverage(xs,vg)
    ig=np.interp(xv,xg,ig);iss=np.interp(xv,xs,iss)
    active=abs(idraw)>max(max(abs(idraw))*1e-6,1e-18)
    sign=float(runner.get('expected_drain_sign',1))
    if sign not in [-1.,1.]:raise SimulationError('expected_drain_sign must be+1 or-1')
    if np.any(sign*idraw[active]<0):
        raise SimulationError('Unexpected on-state current sign. Inspect terminal conventions; do not hide reversal with abs().')
    denom=np.maximum(abs(idraw)+abs(iss)+abs(ig),1e-30)
    kcl=np.abs(idraw+iss+ig)/denom
    kclmax=float(max(kcl[active])) if active.any() else float('nan')
    # No artificial leakage or current offset is added. Raw signed data retained.
    signed=sign*idraw/cfg['geometry']['simulation_width_um']
    with (dest/'terminal_currents.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['vg_V','id_signed_A','is_signed_A','ig_signed_A','id_A_per_um','kcl_relative'])
        w.writerows(zip(xv,idraw,iss,ig,signed,kcl))
    absolute_limit=runner.get('kcl_absolute_limit_A',1e-18)*cfg['geometry']['simulation_width_um']
    relative_limit=runner.get('kcl_relative_limit',.01)
    kcl_ok=bool(np.all(abs(idraw+iss+ig)<=absolute_limit+relative_limit*denom))
    voltages_ok=None
    if (dest/'vdvg.dat').is_file():
        xd,vd=read_xy(dest/'vdvg.dat');xs,vs=read_xy(dest/'vsvg.dat')
        check_coverage(xd,vg);check_coverage(xs,vg)
        voltages_ok=bool(np.allclose(vd,cfg['shared']['vd_V'],atol=1e-8,rtol=0) and np.allclose(vs,0,atol=1e-8,rtol=0))
    metrics={'status':'LOCAL_ATLAS_EXECUTED_UNCALIBRATED' if not smoke else 'LOCAL_ATLAS_SMOKE_DOS_DISABLED',
        'elapsed_seconds':launch['elapsed_seconds'],'returncode':launch['returncode'],'command':launch['command'],'max_kcl_active':kclmax,
        'deck_sha256':launch['deck_sha256'],'exported_points':len(xv),'gate_leakage_model':False,
        'kcl_absolute_limit_A':absolute_limit,'kcl_relative_limit':relative_limit,'kcl_pass':kcl_ok,
        'max_kcl_absolute_A':float(max(abs(idraw+iss+ig))),'nonpositive_drain_points':int((signed<=0).sum()),
        'terminal_voltages_pass':voltages_ok,'low_current_log_treatment':'magnitude with 1e-40 numerical log guard; signed current retained; not a leakage offset'}
    (dest/'validation.json').write_text(json.dumps(metrics,indent=2))
    if not kcl_ok:raise SimulationError(f'Terminal conservation check failed; see {dest}/validation.json')
    if voltages_ok is False:raise SimulationError('Wrong achieved terminal voltages')
    # Return signed currents; comparisons explicitly disclose magnitude logs.
    idx=np.argmin(abs(xv[:,None]-vg[None,:]),axis=0)
    return signed[idx],metrics


def score(vg,meas,pred,cfg,key):
    c=cfg['curves'][key];o=float(np.median(meas[(vg>=-2)&(vg<=-.5)]))
    active=meas>cfg['calibration']['active_multiplier']*o if c['thickness_nm']<20 else np.ones(len(meas),bool)
    eps=cfg['numerics']['logging_epsilon_A_per_um']
    le=np.log10(np.maximum(abs(pred),eps))-np.log10(meas)
    return {'status':'LOCAL_ATLAS_COMPARISON','rmse_log10_all':float(np.sqrt(np.mean(le**2))),
        'rmse_log10_active':float(np.sqrt(np.mean(le[active]**2))),
        'active_points':int(active.sum()),'points':len(meas),
        'median_abs_relative_active':float(np.median(abs(pred[active]/meas[active]-1))),
        'on_error_3V_percent':float(100*(pred[-1]/meas[-1]-1)),
        'max_abs_log10_active':float(max(abs(le[active]))),'off_reference_A_per_um':o,
        'rmse_linear_all_A_per_um':float(np.sqrt(np.mean((pred-meas)**2))),
        'rmse_linear_active_A_per_um':float(np.sqrt(np.mean((pred[active]-meas[active])**2))),
        'measurement_offset_added':False,'below_log_guard_count':int((abs(pred)<eps).sum()),
        'nonpositive_prediction_count':int((pred<=0).sum()),'log_treatment':'log10(max(abs(I), guard)); no offset in linear comparison'},active,le

STAGES={
 'electrostatic':['delta_vfb_V','mu_band_cm2Vs'],
 'transport':['delta_vfb_V','mu_band_cm2Vs','nta_cm3_eV','wta_eV','theta_Vinv'],
 'carrier':['nd_cm3','mu_band_cm2Vs','theta_Vinv'],
}
LOGPARAM={'mu_band_cm2Vs','nta_cm3_eV','nd_cm3'}
BOUNDS={'delta_vfb_V':(-3.,3.),'mu_band_cm2Vs':(.1,200.),'nta_cm3_eV':(1e16,1e22),'wta_eV':(.006,.20),'theta_Vinv':(0.,3.),'nd_cm3':(1e14,3e20)}
SCALES={'delta_vfb_V':.5,'mu_band_cm2Vs':.5,'nta_cm3_eV':1.,'wta_eV':.05,'theta_Vinv':.5,'nd_cm3':1.}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['dry-run','smoke','run','fit'],default='dry-run')
    p.add_argument('--thickness',type=float,required=True,choices=[2.,6.3,13.2,31.8])
    p.add_argument('--config',type=Path,default=ROOT/'config/model_seed.json')
    p.add_argument('--runner',type=Path,default=ROOT/'config/runner.json')
    p.add_argument('--stage',choices=list(STAGES),default='electrostatic')
    p.add_argument('--max-nfev',type=int,default=30)
    p.add_argument('--out',type=Path)
    a=p.parse_args();cfg=load_config(a.config);key=key_from_thickness(a.thickness)
    runid=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%f')
    dest=a.out or ROOT/'results'/'atlas_local'/f'{key}_{runid}'
    vg,meas=read_data(cfg,key)
    if a.mode=='dry-run':
        dest.mkdir(parents=True,exist_ok=False);text,meta=generate(cfg,key,vg)
        (dest/'device.in').write_text(text);(dest/'metadata.json').write_text(json.dumps(meta,indent=2))
        print(f'Generated only: {dest}. No simulator called.');return
    runner=json.loads(a.runner.read_text())
    if a.mode in ['smoke','run']:
        targets=np.array([-3.,0.,3.]) if a.mode=='smoke' else vg
        pred,info=execute(cfg,key,runner,dest,targets,smoke=a.mode=='smoke')
        if a.mode=='run':
            metrics,mask,err=score(vg,meas,pred,cfg,key)
            (dest/'fit_metrics.json').write_text(json.dumps(metrics,indent=2))
            write_comparison(dest,vg,meas,pred,mask,err)
            print(json.dumps(metrics,indent=2))
        print(dest);return
    # Calibration must not silently optimize a mobility coefficient that local
    # probes showed does not update the already-initialized nodal mobility.
    if cfg['mobility']['mode']!='constant':
        raise SimulationError('Bias-indexed mobility updates are not verified in ATLAS 5.28.1.R. Use an explicitly constant-mobility baseline; transport/theta fitting remains disabled.')
    if a.stage in ['transport','carrier']:
        raise SimulationError('This stage includes unverified mid-run mobility roll-off and is disabled pending a real-solver implementation check.')
    gate=ROOT/'results/local_session_20260910/calibration_gate.json'
    if not gate.is_file() or not json.loads(gate.read_text()).get('all_required_checks_passed',False):
        raise SimulationError('Numerical acceptance gates are incomplete/failed. No calibration solver evaluations were launched.')
    dest.mkdir(parents=True,exist_ok=False)
    names=STAGES[a.stage]
    transform=lambda k,v:np.log10(v) if k in LOGPARAM else v
    inverse=lambda k,v:10**v if k in LOGPARAM else v
    x0=np.array([transform(k,cfg['curves'][key][k]) for k in names])
    lo=np.array([transform(k,BOUNDS[k][0]) for k in names]);hi=np.array([transform(k,BOUNDS[k][1]) for k in names])
    if np.any(x0<lo) or np.any(x0>hi):raise ValueError('Initial parameters outside stage bounds')
    sig=np.array([SCALES[k] for k in names]);cache={};counter=0;best={'cost':float('inf')}
    def evaluate(x):
        nonlocal counter
        ck=tuple(map(float,x))
        if ck in cache:return cache[ck]
        run_cfg=copy.deepcopy(cfg)
        for k,v in zip(names,x):run_cfg['curves'][key][k]=float(inverse(k,v))
        run=dest/f'eval_{counter:04d}';counter+=1
        # A simulator failure stops optimization instead of being hidden by fake data.
        pred,info=execute(run_cfg,key,runner,run,vg)
        metrics,mask,err=score(vg,meas,pred,run_cfg,key)
        weights=np.where(mask,1.,cfg['calibration']['off_weight'])
        prior=cfg['calibration']['prior_weight']*(x-x0)/sig
        r=np.r_[weights*err,cfg['calibration']['linear_weight']*(pred-meas)/max(meas),prior]
        (run/'fit_metrics.json').write_text(json.dumps(metrics,indent=2))
        write_comparison(run,vg,meas,pred,mask,err)
        cost=float(r@r)
        if cost<best['cost']:
            best.update(cost=cost,config=run_cfg,run=str(run),metrics=metrics)
            (dest/'best_config.json').write_text(json.dumps(run_cfg,indent=2))
            (dest/'best_summary.json').write_text(json.dumps({'cost':cost,'run':str(run),'metrics':metrics,'status':'LOCAL_ATLAS_FIT_IN_PROGRESS'},indent=2))
        cache[ck]=r
        print(f'{run.name}: cost={cost:.6g}, active_RMSE={metrics["rmse_log10_active"]:.5g}',flush=True)
        return r
    # Explicit nonzero absolute differences avoid infinitesimal simulator perturbations
    # at an initial zero voltage shift (SciPy's relative diff_step can be too small).
    steps=np.array([.01 if k=='delta_vfb_V' else .003 if k=='wta_eV' else .02 for k in names])
    def jac(x):
        y0=evaluate(x);J=np.empty((len(y0),len(x)))
        for j in range(len(x)):
            d=steps[j] if x[j]+steps[j]<=hi[j] else -steps[j]
            xx=x.copy();xx[j]+=d;J[:,j]=(evaluate(xx)-y0)/d
        return J
    result=least_squares(evaluate,x0,jac=jac,bounds=(lo,hi),max_nfev=a.max_nfev,
        x_scale=sig,ftol=1e-5,xtol=1e-4,gtol=1e-4,verbose=1)
    (dest/'calibrated_config.json').write_text(json.dumps(best['config'],indent=2))
    report={'status':'LOCAL_ATLAS_CALIBRATION_COMPLETED_CHECK_RESIDUALS_NOT_UNIQUE_PHYSICS',
        'scipy_success':bool(result.success),'message':result.message,'stage':a.stage,
        'optimized_parameters':names,'simulator_invocations':counter,'best_run':best['run'],
        'best_metrics':best['metrics'],'jacobian_condition_number':float(np.linalg.cond(result.jac)),
        'warning':'One drain bias per thickness does not uniquely identify DOS, contacts, donor density and mobility. Further independent data and convergence tests required.'}
    (dest/'calibration_summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

def write_comparison(dest,vg,meas,pred,mask,err):
    with (dest/'comparison.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['vg_V','measured_A_per_um','atlas_signed_A_per_um','linear_error_A_per_um','log10_magnitude_error','active_fit_region'])
        w.writerows(zip(vg,meas,pred,pred-meas,err,mask.astype(int)))

if __name__=='__main__':
    try:main()
    except (SimulationError,ValueError,KeyError,RuntimeError) as exc:
        print(f'FAILED: {exc}',file=sys.stderr);sys.exit(2)
