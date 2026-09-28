"""Run one genuine paper-revision ATLAS trial and retain four-terminal evidence."""
import argparse,csv,hashlib,json,re
from pathlib import Path
import numpy as np
from iwo_model import ROOT,load_config,read_data
from paper_model import render
from local_probe import run
from atlas_workflow import read_xy,check_coverage
from local_report import report


def inspect(dest,cfg,key,allow_recovered_steps=False):
    launch=json.loads((dest/'execution.json').read_text())
    output=(dest/'deckbuild.out').read_text(errors='replace')
    failures=r'Error:|Error #|invalid parameter|unknown parameter|Cannot trap|Could not trap|Cannot reduce bias|fatal error|license.*(?:denied|failed)'
    if not allow_recovered_steps:failures+='|convergence problem'
    if launch['returncode']!=0 or re.search(failures,output,re.I):
        raise RuntimeError('ATLAS launch/parser/convergence failed; inspect raw deckbuild.out')
    if not re.search(r'ATLAS version .* finished',output):raise RuntimeError('Missing actual ATLAS completion banner')
    for name,h in launch['outputs'].items():
        if hashlib.sha256((dest/name).read_bytes()).hexdigest()!=h:raise RuntimeError('Run output changed: '+name)
    vg,meas=read_data(cfg,key)
    curves={}
    has_substrate=cfg.get('electrical_domain')!='screened_active_stack' and cfg.get('substrate_electrical_model')!='ideal_equipotential'
    current_names=['idvg','isvg','igvg']+(['ibvg'] if has_substrate else [])
    for name in current_names+['vdvg','vsvg']+(['vbvg'] if has_substrate else []):
        x,y=read_xy(dest/(name+'.dat'));check_coverage(x,vg)
        idx=np.argmin(abs(x[:,None]-vg[None,:]),axis=0);curves[name]=y[idx]
    current=np.array([curves[n] for n in current_names])
    width=cfg['geometry']['simulation_width_um'];res=current.sum(axis=0)
    limit=1e-18*width+.01*np.abs(current).sum(axis=0)
    valid={
        'status':'REAL_ATLAS_DIAGNOSTIC_NOT_CALIBRATED',
        'gate_points':len(vg),'kcl_pass':bool(np.all(abs(res)<=limit)),
        'kcl_absolute_limit_A_per_um':1e-18,'kcl_relative_limit':.01,
        'kcl_failed_points':int((abs(res)>limit).sum()),
        'max_kcl_absolute_A':float(max(abs(res))),
        'terminal_count':len(current_names),
        'terminal_voltages_pass':bool(np.allclose(curves['vdvg'],cfg['shared']['vd_V'],atol=1e-8,rtol=0) and np.allclose(curves['vsvg'],0,atol=1e-8,rtol=0) and (not has_substrate or np.allclose(curves['vbvg'],vg,atol=1e-8,rtol=0))),
        'nonpositive_drain_points':int((curves['idvg']<=0).sum()),
        'structures_present':all((dest/n).is_file() for n in ['equilibrium.str','off.str','final.str']),
        'native_interface_DOS_export_present':(dest/'interface_dos.dat').is_file(),
        'mesh_width_DOS_sensitivity_complete':False,
        'recovered_step_warnings_allowed':allow_recovered_steps,
        'bias_cutback_warning_count':len(re.findall(r'convergence problem',output,re.I)),
        'cutback_acceptance_basis':'All original gate targets and terminal voltages exported, no unrecovered Cannot trap/fatal error; successful intermediate points may be present' if allow_recovered_steps else 'Strict legacy warning rejection',
    }
    (dest/'validation.json').write_text(json.dumps(valid,indent=2))
    with (dest/'terminal_currents.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['vg_V']+[n[:2]+'_A' for n in current_names]+['kcl_residual_A','kcl_limit_A'])
        w.writerows(zip(vg,*current,res,limit))
    report(dest,key)
    return valid


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--key',default='2p0');p.add_argument('--config',default=str(ROOT/'config/paper_revision.json'));p.add_argument('--label',required=True);p.add_argument('--timeout',type=int,default=300);p.add_argument('--smoke',action='store_true');a=p.parse_args()
    cfg=load_config(a.config);deck,meta=render(cfg,a.key,a.smoke)
    artifacts={'source_athena.str':ROOT/cfg['athena_structure_path']} if cfg.get('athena_structure_path') else None
    dest=run(['C:/sedatools/exe/deckbuild.exe','-run','{deck}','-outfile','{stdout}'],deck,a.label,a.timeout,config=cfg,verbose=False,input_artifacts=artifacts)
    (dest/'model_metadata.json').write_text(json.dumps(meta,indent=2))
    try:print(json.dumps(inspect(dest,cfg,a.key),indent=2))
    except Exception as e:
        (dest/'trial_failure.json').write_text(json.dumps({'error':str(e)},indent=2));print(str(e));raise
