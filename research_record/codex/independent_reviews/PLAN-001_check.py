from pathlib import Path
import re,json,csv,math,collections
root=Path(__file__).resolve().parents[2]
r=root.parent/'IWO_PHYSICS_CONSTRAINED_MODEL_V1'
d=r/'qe_workflow/cern_htcondor/results'
checks={}
for folder,file in [('iwo_W24d','spin_k3.out'),('iwo_W24d','relax.out'),('iwo_W8b','relax.out'),('slab1r_final_cpu','scf.out'),('iwo_slab2_final_cpu','scf.out'),('slabL2_relax_v2','vcrelax.out'),('slabL2_relax_v2','scf.out'),('slab2_relax_c2','vcrelax.out')]:
 s=(d/folder/file).read_text(errors='replace')
 checks[folder+'/'+file]={k:re.findall(p,s)[-1:] for k,p in {'atoms':r'number of atoms/cell\s*=\s*(\d+)','kpoints':r'number of k points\s*=\s*(\d+)','ranks':r'running on\s+(\d+) processor cores','wall':r'PWSCF\s*:.*?CPU\s+(.*?) WALL','iterations':r'convergence has been achieved in\s+(\d+) iterations'}.items()}
for folder in ['slabL1_relax_v2','slabL2_relax_v2','slab1r_final_cpu','iwo_slab1_final_cpu','iwo_slab2_final_cpu']:
 s=(d/folder/'scf.in').read_text(); block=s.split('ATOMIC_POSITIONS')[1].split('K_POINTS')[0]
 counts=collections.Counter(re.findall(r'^\s*(In|W|O|H)\s+[-\d.]',block,re.M)); checks[folder+'_composition']=dict(counts)
rho=7; av=6.02214076e23; mol=2*114.818+3*15.999
n=rho*av/mol/1e21; metals=2*n; volume=50/metals
checks['density']={'atoms_nm3':5*n,'metals_nm3':metals,'volume_per_W_nm3':volume}
checks['cells']=[{'t_nm':t,'a_nm':a,'volume_nm3':t*a*a,'atoms_estimate':5*n*t*a*a,'W_percent':100/(metals*t*a*a),'a_for_2percent':math.sqrt(volume/t)} for t,a in [(2,1.05),(1.5,1.05),(1,1.29),(.8,1.44),(.7,1.54)]]
rows=list(csv.DictReader((r/'data/experimental_clean.csv').open())); checks['curves']={}
for t in sorted(set(x['thickness_nm'] for x in rows),key=float):
 points=sorted([(float(x['vg_V']),float(x['id_A_per_um'])) for x in rows if x['thickness_nm']==t]); crossings=[]
 for (v,i),(w,j) in zip(points,points[1:]):
  if i<1e-9<=j:crossings.append(v+(w-v)*(math.log10(1e-9)-math.log10(i))/(math.log10(j)-math.log10(i)))
 checks['curves'][t]={'n':len(points),'Ion':points[-1][1],'Iminus3':points[0][1],'cc_threshold_log_interpolation':crossings,'sweep_ratio':points[-1][1]/points[0][1]}
(root/'codex/independent_reviews/PLAN-001_check_results.json').write_text(json.dumps(checks,indent=2)+'\n'); print(json.dumps(checks,indent=2))
