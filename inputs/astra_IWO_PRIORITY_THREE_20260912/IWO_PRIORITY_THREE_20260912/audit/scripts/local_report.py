"""Plot real, traceable solver exports; never generates simulated data."""
import argparse,csv,json,re,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parents[1]/'tmp/matplotlib'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from generate_atlas import ROOT,load_config,read_data
from atlas_workflow import read_xy,check_coverage
BASE=ROOT/'results/local_session_20260910'
def masks(cfg,key):
    v,y=read_data(cfg,key)
    off=float(np.median(y[(v>=-2)&(v<=-.5)]))
    active=y>5*off if key!='31p8' else np.ones(len(y),bool)
    low=~active
    sub=active & (y<=.01*y[-1])
    on=active & ~sub
    return v,y,{'all':np.ones(len(y),bool),'active':active,'low_current':low,'subthreshold':sub,'on':on},off
def freeze_masks():
    cfg=load_config();dest=BASE/'measurement_masks.json'
    if dest.exists():return
    result={'definitions':{'active':'I > 5 * median(I for -2 <= Vg <= -0.5), except 31.8 nm all points active','low_current':'complement of active; analyst weighting choice, not instrument resolution','subthreshold':'active and I <= 0.01 * I(+3 V)','on':'active excluding subthreshold'},'curves':{}}
    for key in cfg['curves']:
        v,y,m,off=masks(cfg,key)
        result['curves'][key]={'vg_V':v.tolist(),'off_reference_A_per_um':off,'masks':{k:a.tolist() for k,a in m.items()},'active_sensitivity_counts':{str(mult):int((y>mult*off).sum()) for mult in [2,5,10]}}
    dest.write_text(json.dumps(result,indent=2))
def report(dest,key):
    cfg=json.loads((dest/'input_config.json').read_text()) if (dest/'input_config.json').exists() else load_config()
    v,y,m,off=masks(cfg,key);x,raw=read_xy(dest/'idvg.dat');check_coverage(x,v)
    idx=np.argmin(abs(x[:,None]-v[None,:]),axis=0);pred=raw[idx]/cfg['geometry']['simulation_width_um']
    le=np.log10(np.maximum(abs(pred),1e-40)/y);linear=pred-y
    met={'run_directory':str(dest),'status':'REAL_ATLAS_DIAGNOSTIC_NOT_CALIBRATED','validation':json.loads((dest/'validation.json').read_text()) if (dest/'validation.json').exists() else None,'log_treatment':'magnitude of signed current, guarded at 1e-40 A/um; negative points counted; no additive leakage','negative_points':int((pred<0).sum()),'log_guard_points':int((abs(pred)<1e-40).sum()),'on_error_percent':float(100*(pred[-1]/y[-1]-1)),'regions':{}}
    for name,mask in m.items():
        met['regions'][name]={'count':int(mask.sum()),'rmse_linear_A_per_um':float(np.sqrt(np.mean(linear[mask]**2))) if mask.any() else None,'rmse_log10_decades':float(np.sqrt(np.mean(le[mask]**2))) if mask.any() else None}
    with (dest/'comparison_all_measurements.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['vg_V','measured_A_per_um','atlas_signed_A_per_um','linear_residual_A_per_um','log10_magnitude_residual','active','subthreshold','low_current']);w.writerows(zip(v,y,pred,linear,le,m['active'],m['subthreshold'],m['low_current']))
    (dest/'diagnostic_metrics.json').write_text(json.dumps(met,indent=2))
    for scale in ['linear','log']:
        fig,ax=plt.subplots(figsize=(8,5));ax.plot(v,y,'o',ms=3,label='Original Excel');ax.plot(v,pred if scale=='linear' else np.maximum(abs(pred),1e-40),label='Actual ATLAS (diagnostic)')
        if scale=='log':ax.set_yscale('log')
        ax.set(xlabel='Gate voltage (V)',ylabel='Signed drain current (A/um)' if scale=='linear' else '|Drain current| (A/um)',title=f'{key.replace("p",".")} nm: actual ATLAS, uncalibrated')
        ax.legend();ax.grid(alpha=.25);fig.tight_layout();fig.savefig(dest/f'overlay_{scale}.png',dpi=160);plt.close(fig)
        fig,ax=plt.subplots(figsize=(8,4));ax.plot(v,linear if scale=='linear' else le,'.-');ax.axhline(0,color='k',lw=.7);ax.set(xlabel='Gate voltage (V)',ylabel='Signed current error (A/um)' if scale=='linear' else 'log10(|ATLAS| / measurement)',title='Actual ATLAS residuals at all 121 measurements');ax.grid(alpha=.25);fig.tight_layout();fig.savefig(dest/f'residual_{scale}.png',dpi=160);plt.close(fig)
    print(json.dumps(met,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',type=Path);p.add_argument('--key',default='2p0');a=p.parse_args();freeze_masks()
    if a.folder:report(a.folder,a.key)
