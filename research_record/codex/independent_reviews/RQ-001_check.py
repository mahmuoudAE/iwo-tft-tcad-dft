"""Independent stdlib-only checks; no owner code imported. Run from repo root."""
import csv,math,statistics,json,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
P=Path('../IWO_PHYSICS_CONSTRAINED_MODEL_V1')
rows=list(csv.DictReader(open(P/'data/experimental_clean.csv')))
c=8.8541878128e-14/(15e-7/19.57+2e-7/9)
def grad(x,y):
 return [(y[1]-y[0])/(x[1]-x[0])]+[(y[k+1]-y[k-1])/(x[k+1]-x[k-1]) for k in range(1,len(x)-1)]+[(y[-1]-y[-2])/(x[-1]-x[-2])]
def cross(x,y,level):
 ks=[k for k in range(len(x)-1) if 0<y[k]<level<=y[k+1]]
 if not ks:return None
 k=ks[-1];return x[k]+(x[k+1]-x[k])*math.log10(level/y[k])/math.log10(y[k+1]/y[k])
def ss(x,y,lo):
 a,b=cross(x,y,lo),cross(x,y,10*lo)
 return None if a is None or b is None else 1000*(b-a)
def steep(x,y,f,n,margin):
 vals=[]
 for k in range(len(x)-n+1):
  z=y[k:k+n]
  if min(z)<margin*f or max(z)>min(1e-8,max(y)/10):continue
  xx=x[k:k+n]; yy=list(map(math.log10,z));xm=statistics.mean(xx);ym=statistics.mean(yy)
  slope=sum((a-xm)*(b-ym) for a,b in zip(xx,yy))/sum((a-xm)**2 for a in xx)
  if slope>0:vals.append((1000/slope,x[k],min(z)))
 return min(vals) if vals else None
out={}
with zipfile.ZipFile(P/'data/experimental_raw_preserved_IWO-TFT.xlsx') as z:
 ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 root=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
 cells={a.attrib['r']:float(a.find('m:v',ns).text) for a in root.findall('.//m:c',ns) if a.find('m:v',ns) is not None and a.attrib.get('t')!='s'}
for t,cols in [(2.,('G','H')),(6.3,('A','B')),(13.2,('C','D')),(31.8,('E','F'))]:
 rr=sorted([r for r in rows if float(r['thickness_nm'])==t],key=lambda r:float(r['vg_V']))
 x=[float(r['vg_V']) for r in rr]; y=[float(r['id_A_per_um']) for r in rr]
 f=statistics.median(b for a,b in zip(x,y) if -2<=a<=-.5)
 gm=grad(x,y);ml=[20*g/(c*.7) for g in gm]; ms=[40*g*g/c for g in grad(x,list(map(math.sqrt,y)))]
 peak=lambda v:max((b,a) for a,b in zip(x,v) if 0<=a<=3)
 d=dict(n=len(x),raw_max_abs_v=max(abs(cells[f'{cols[0]}{k+2}']-a) for k,a in enumerate(x)),raw_max_abs_i=max(abs(cells[f'{cols[1]}{k+2}']-a) for k,a in enumerate(y)),floor=f,mu_lin_peak=peak(ml),mu_sat_peak=peak(ms),mu_sat_at3=ms[-1],vcc=cross(x,y,1e-9),ss_A1=ss(x,y,2.15e-5*y[-1]),ss_S1=ss(x,y,5e-11),ss_3floor=ss(x,y,3*f),ss_5floor=ss(x,y,5*f),steep3=steep(x,y,f,3,1),steep5=steep(x,y,f,5,1),corrected_steep4=steep(x,[max(a-f,1e-30) for a in y],f,4,3))
 mins=[1000*(x[k+1]-x[k])/math.log10(y[k+1]/y[k]) for k in range(len(x)-1) if y[k]>=10*f and y[k+1]>y[k] and y[k+1]<=min(1e-8,max(y)/10)]
 d['two_point_10floor']=min(mins) if mins else None
 out[str(t)]=d
print(json.dumps({'cox':c,'films':out},indent=2))
Path('codex/independent_reviews/RQ-001_check_results.json').write_text(json.dumps({'cox':c,'films':out},indent=2)+'\n')
