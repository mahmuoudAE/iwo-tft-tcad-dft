"""3D live DFT dashboard (read-only, local):  python dashboard3.py  ->  http://localhost:8766
- interactive 3D crystal (conventional 80-atom and computed 40-atom primitive cell), bonds incl. periodic images,
  atom environments, distance/angle measurement;
- reciprocal space: Brillouin zone of the bcc lattice with the irreducible k-points of the running calculation;
- live SCF evolution, full pw.x setup, PAW data-set details (UPF headers + pw.x), method/reference table,
  finished-run results and the convergence study against the pre-registered criteria.
Static crystallographic data come from structure_display.json (build_display.py, ASE + spglib)."""
import json, math, re, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import dashboard2 as d2

D = d2.D
STRUCT = json.loads((D / 'structure_display.json').read_text())

def upf_info():
    keep = ['element', 'pseudo_type', 'relativistic', 'is_paw', 'core_correction', 'functional', 'z_valence', 'wfc_cutoff', 'rho_cutoff',
            'l_max', 'mesh_size', 'number_of_wfc', 'number_of_proj', 'author', 'date', 'generated']
    out = []
    for f in sorted((D.parent / 'pseudo').glob('*.UPF')):
        t = f.read_text(errors='replace')
        m = re.search(r'<PP_HEADER(.*?)/?>', t, re.S); attrs = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', m.group(1))) if m else {}
        m2 = re.search(r'<PP_INFO>(.*?)</PP_INFO>', t, re.S)
        el = attrs.get('element', '').strip()
        out.append({'file': f.name, 'header': {k: attrs[k].strip() for k in keep if k in attrs},
                    'info': '\n'.join(m2.group(1).strip().splitlines()[:45]) if m2 else '', 'used_now': el in ('In', 'O')})
    return out
UPF = upf_info()

def extra(name):
    f = D / f'{name}.out'
    if not f.exists(): return {}
    t = f.read_text(errors='replace'); hdr = t.split('iteration #')[0]; e = {}
    m = re.search(r'Program PWSCF (v\.[\w.]+)', hdr); e['version'] = m.group(1) if m else None
    m = re.search(r'Exchange-correlation=\s*([^\n]+)\n\s*\(([\d\s]+)\)', hdr)
    e['xc'] = f"{' '.join(m.group(1).split())} = PBE (internal indices {' '.join(m.group(2).split())})" if m else None
    e['pseudo'] = [b.strip() for b in re.findall(r'(PseudoPot\. #.*?)\n\s*\n', hdr, re.S)]
    m = re.search(r'atomic species\s+valence\s+mass\s+pseudopotential\n((?:[ \t]+\w+[ \t]+[\d.]+[ \t]+[\d.]+[ \t]+\S+.*\n)+)', hdr)
    e['species_table'] = m.group(1) if m else ''
    m = re.search(r'lattice parameter \(alat\)\s+=\s+([\d.]+)', hdr); alat = float(m.group(1)) if m else None
    m = re.search(r'number of k points=\s+(\d+)', hdr); nk = int(m.group(1)) if m else 0
    ks = re.findall(r'k\(\s*\d+\) = \(([^)]*)\), wk =\s+([\d.]+)', hdr)
    if alat and ks:
        fac = 2 * math.pi / (alat * 0.529177210903)
        e['kpts'] = [[float(x) * fac for x in re.findall(r'-?\d+\.\d+', c)][:3] + [float(w)] for c, w in ks[:nk]]
    for key, pat in [('dense_grid', r'Dense\s+grid:\s+(\d+ G-vectors\s+FFT dimensions: \([^)]*\))'),
                     ('smooth_grid', r'Smooth grid:\s+(\d+ G-vectors\s+FFT dimensions: \([^)]*\))'),
                     ('ram_total', r'Estimated total dynamical RAM >\s+([\d.]+ \w+)'), ('start_wfc', r'(Starting wfcs are[^\n]*)'),
                     ('start_pot', r'(Initial potential from[^\n]*)'), ('diag', r'(Davidson diagonalization[^\n]*)')]:
        m = re.search(pat, t); e[key] = ' '.join(m.group(1).split()) if m else None
    return e

def api():
    runs = [d2.parse(q) for q in d2.QUEUE]
    log = (D / 'convergence.log').read_text(errors='replace') if (D / 'convergence.log').exists() else ''
    return {'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'runs': runs, 'extra': {q: extra(q) for q in d2.QUEUE}, 'machine': d2.machine(), 'log': log[-2500:]}

PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><title>DFT 3D: bulk In2O3</title><style>
:root{--acc:#1F4E79;--acc2:#B5462E}
body{font-family:Georgia,serif;margin:0;background:#f4f4f2;color:#222}
header{background:var(--acc);color:#fff;padding:10px 20px;position:sticky;top:0;z-index:5}
h1{margin:0;font-size:20px}#hdr{font-size:13px;opacity:.92;margin-top:3px}nav a{color:#fff;margin-right:12px;font-size:13px}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:14px;padding:14px}
section{background:#fff;border:1px solid #ddd;border-radius:4px;padding:12px 14px;min-width:0}.wide{grid-column:1/-1}
h2{font-size:17px;margin:0 0 8px;border-bottom:1px solid #eee;padding-bottom:4px}h3{font-size:14px;margin:10px 0 4px}
table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid #eee;padding:3px 6px;text-align:left;vertical-align:top}
.note{font-size:12.5px;color:#555}.row{display:flex;gap:16px;flex-wrap:wrap}
canvas{background:radial-gradient(#ffffff,#e6eaf0);border:1px solid #ccd;border-radius:4px;cursor:grab;touch-action:none;max-width:100%}
button{font-family:inherit;font-size:12px;margin:2px;padding:3px 8px;border:1px solid #99a;background:#fff;border-radius:3px;cursor:pointer}button.on{background:var(--acc);color:#fff}
.done{color:#2E7D32;font-weight:bold}.running{color:#B7791F;font-weight:bold}.waiting{color:#999}.pass{color:#2E7D32}.fail{color:#B3261E}
pre{font-size:11px;background:#fafafa;border:1px solid #eee;padding:6px;max-height:240px;overflow:auto;white-space:pre-wrap}
.bar{height:10px;background:#e5e5e5;border-radius:5px}.bar>div{height:10px;background:var(--acc);border-radius:5px}
.scf rect{fill:#fff;stroke:#99a}.scf .act rect{fill:#fff3cd;stroke:#B7791F;stroke-width:2}
.legend span{display:inline-block;width:12px;height:12px;border-radius:6px;margin:0 4px -2px 10px}a{color:var(--acc)}
</style></head><body>
<header><h1>Bulk In&#8322;O&#8323; &mdash; live first-principles calculation (Quantum ESPRESSO 7.5, PBE-PAW)</h1><div id="hdr">loading...</div>
<nav><a href="#xtal">3D crystal</a><a href="#now">what is computed now</a><a href="#bz">k-space</a><a href="#method">method &amp; references</a><a href="#paw">PAW data sets</a><a href="#results">results</a></nav></header>
<main>
<section class="wide" id="xtal"><h2>Crystal structure in 3D: cubic bixbyite In&#8322;O&#8323; (space group Ia-3, No. 206)</h2>
<div class="row"><div><canvas id="cv" width="660" height="540"></canvas>
<div><button id="bconv" class="on">Conventional cell (80 atoms)</button><button id="bprim">Primitive cell (40 atoms, the one computed)</button>
<button id="bbonds" class="on">bonds</button><button id="blabels">site labels</button><button id="bauto">auto-rotate</button><button id="bmeas">measure</button><br>
<button data-v="1,0,0">view along [100]</button><button data-v="1,1,0">[110]</button><button data-v="1,1,1">[111]</button><button id="breset">reset view</button>
&nbsp;atom size <input id="size" type="range" min="0.4" max="1.8" step="0.1" value="1"></div>
<div class="legend note"><span style="background:#A67573"></span>In<span style="background:#FF0D0D"></span>O &nbsp;&middot; drag to rotate, mouse wheel to zoom, click an atom to see its environment; in "measure" mode click 2 atoms for a distance, 3 for an angle. Half-bonds at the cell faces point to periodic images.</div></div>
<div style="flex:1;min-width:320px"><h3>Selected atom</h3><div id="selinfo" class="note">Click an atom.</div><h3>Measurement</h3><div id="measinfo" class="note">Enable "measure" and click atoms.</div></div></div>
<div class="row"><div style="flex:1;min-width:340px"><h3>Cell and structure data</h3><div id="celltab"></div></div>
<div style="flex:1;min-width:340px"><h3>Crystallographic definition used (Marezio 1966)</h3><div id="wyck"></div><h3>Interatomic distances (periodic, conventional cell)</h3><div id="dist"></div></div></div></section>
<section class="wide" id="now"><h2>What the computer is calculating now</h2><div class="row"><div id="scfsvg"></div><div style="flex:1;min-width:340px" id="nowtext"></div></div></section>
<section><h2>SCF accuracy per iteration</h2><div id="accplot"></div><p class="note">Estimated SCF accuracy: an upper bound on the energy error caused by a density that is not yet self-consistent. The loop stops below the dashed threshold (1e-9 Ry).</p></section>
<section><h2>Total-energy convergence</h2><div id="eplot"></div><p class="note">|E(n) &minus; E(latest)| per atom on a log scale: the Kohn&ndash;Sham energy approaches its variational minimum as the density becomes self-consistent.</p></section>
<section><h2>Eigensolver effort and time per iteration</h2><div id="dplot"></div><p class="note">Bars: average Davidson iterations per band; line: CPU seconds per SCF step. The Davidson tolerance (ethr) is tightened as the SCF converges.</p></section>
<section><h2>Iteration table</h2><div id="ittab" style="max-height:330px;overflow:auto"></div></section>
<section id="bz"><h2>Reciprocal space: Brillouin zone and k-points</h2><canvas id="cvk" width="470" height="400"></canvas>
<p class="note">First Brillouin zone of the body-centred cubic lattice (a rhombic dodecahedron) with the high-symmetry points &Gamma;, H, N, P. Red points: the irreducible k-points of the current calculation, marker size proportional to the square root of the weight. Coordinates from pw.x (cartesian, 2&pi;/alat), converted to 1/&Aring;.</p><div id="ktab" style="max-height:220px;overflow:auto"></div></section>
<section><h2>Calculation setup reported by pw.x</h2><div id="setup"></div></section>
<section class="wide" id="method"><h2>Method, parameters and references</h2><div id="reftab"></div><p class="note">Every ingredient of the calculation with its primary reference. Settings are read live from the pw.x output where possible. Journal and DOI data are given as commonly cited; confirm them on the publisher's site before citing in a manuscript. Full protocol with pre-registered acceptance criteria: PROTOCOL.md.</p></section>
<section class="wide" id="paw"><h2>PAW data sets (pslibrary 1.0.0): file headers and what pw.x read</h2><div id="pawinfo"></div></section>
<section id="results"><h2>Results of finished runs</h2><select id="sel"></select><div id="final"></div></section>
<section><h2>Band edges at each k-point (finished run)</h2><div id="bands"></div><p class="note">Top valence band (band 176) and bottom conduction band (band 177) at each irreducible k-point.</p></section>
<section class="wide"><h2>Convergence study against the pre-registered criteria (PROTOCOL.md)</h2><div id="conv"></div></section>
<section><h2>Queue</h2><div id="queue"></div></section>
<section><h2>Machine and run log</h2><div id="mach"></div><pre id="log"></pre></section>
</main><script>
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
function table(rows,head){return '<table>'+(head?'<tr>'+head.map(h=>`<th>${h}</th>`).join('')+'</tr>':'')+rows.map(r=>'<tr>'+r.map(c=>`<td>${c??''}</td>`).join('')+'</tr>').join('')+'</table>'}
function plot(series,opt){const W=opt.w||430,H=opt.h||210,L=54,R=12,T=10,B=30;let xs=[],ys=[];series.forEach(s=>s.pts.forEach(p=>{if(isFinite(p[1])){xs.push(p[0]);ys.push(p[1])}}));
 if(!xs.length)return'<p class="note">waiting for data...</p>';let x0=Math.min(...xs),x1=Math.max(...xs),y0=opt.ymin??Math.min(...ys),y1=opt.ymax??Math.max(...ys);if(x1==x0)x1=x0+1;if(y1==y0)y1=y0+1;
 const X=x=>L+(x-x0)/(x1-x0)*(W-L-R),Y=y=>H-B-(y-y0)/(y1-y0)*(H-T-B);let s=`<svg width="${W}" height="${H}" style="background:#fff">`;
 for(let i=0;i<=4;i++){const yv=y0+i*(y1-y0)/4;s+=`<line x1="${L}" x2="${W-R}" y1="${Y(yv)}" y2="${Y(yv)}" stroke="#eee"/><text x="${L-4}" y="${Y(yv)+4}" font-size="10" text-anchor="end">${opt.ylab?opt.ylab(yv):yv.toPrecision(3)}</text>`}
 for(let i=0;i<=4;i++){const xv=x0+i*(x1-x0)/4;s+=`<text x="${X(xv)}" y="${H-B+14}" font-size="10" text-anchor="middle">${Math.round(xv*10)/10}</text>`}
 s+=`<text x="${(L+W)/2}" y="${H-3}" font-size="11" text-anchor="middle">${opt.xl||''}</text><text x="11" y="${H/2}" font-size="11" transform="rotate(-90 11 ${H/2})" text-anchor="middle">${opt.yl||''}</text>`;
 (opt.hlines||[]).forEach(h=>{s+=`<line x1="${L}" x2="${W-R}" y1="${Y(h.y)}" y2="${Y(h.y)}" stroke="${h.c}" stroke-dasharray="5"/><text x="${W-R}" y="${Y(h.y)-3}" font-size="10" fill="${h.c}" text-anchor="end">${h.t}</text>`});
 series.forEach((se,si)=>{const p=se.pts.filter(q=>isFinite(q[1]));if(se.bar){p.forEach(q=>{s+=`<rect x="${X(q[0])-4}" y="${Y(q[1])}" width="8" height="${Math.max(0,H-B-Y(q[1]))}" fill="${se.c}" opacity=".45"/>`})}
  else{s+=`<polyline fill="none" stroke="${se.c}" stroke-width="2" points="${p.map(q=>X(q[0])+','+Y(q[1])).join(' ')}"/>`;p.forEach(q=>{s+=`<circle cx="${X(q[0])}" cy="${Y(q[1])}" r="2.5" fill="${se.c}"/>`})}
  if(se.label)s+=`<text x="${W-R-4}" y="${T+12+14*si}" font-size="11" fill="${se.c}" text-anchor="end">${se.label}</text>`});return s+'</svg>'}
const lg=v=>Math.log10(Math.max(v,1e-14)),expo=v=>'1e'+Math.round(v);
// ---------------- 3D engine (canvas, perspective, painter's algorithm) ----------------
const mv=(M,v)=>[M[0][0]*v[0]+M[0][1]*v[1]+M[0][2]*v[2],M[1][0]*v[0]+M[1][1]*v[1]+M[1][2]*v[2],M[2][0]*v[0]+M[2][1]*v[1]+M[2][2]*v[2]];
const mm=(A,B)=>A.map(r=>[0,1,2].map(j=>r[0]*B[0][j]+r[1]*B[1][j]+r[2]*B[2][j]));
const Rx=t=>[[1,0,0],[0,Math.cos(t),-Math.sin(t)],[0,Math.sin(t),Math.cos(t)]],Ry=t=>[[Math.cos(t),0,Math.sin(t)],[0,1,0],[-Math.sin(t),0,Math.cos(t)]];
const sub=(a,b)=>[a[0]-b[0],a[1]-b[1],a[2]-b[2]],add=(a,b)=>[a[0]+b[0],a[1]+b[1],a[2]+b[2]],mul=(a,s)=>[a[0]*s,a[1]*s,a[2]*s],dot=(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],norm=a=>Math.hypot(a[0],a[1],a[2]),unit=a=>mul(a,1/norm(a));
function lookR(dir,up){const z=unit(dir);let x=cross(up,z);if(norm(x)<1e-6)x=cross([0,1,0],z);x=unit(x);return [x,cross(z,x),z]}
function shade(hex,f){const n=parseInt(hex.slice(1),16);let r=n>>16,g=(n>>8)&255,b=n&255;const t=f<0?0:255,p=Math.abs(f);r=Math.round((t-r)*p+r);g=Math.round((t-g)*p+g);b=Math.round((t-b)*p+b);return `rgb(${r},${g},${b})`}
class V3{constructor(cv,dir){this.cv=cv;this.c=cv.getContext('2d');this.R0=lookR(dir,[0,0,1]);this.R=this.R0;this.zoom=1;this.hits=[];this.onpick=null;this.moved=false;this.s=null;let last=null;
 cv.addEventListener('pointerdown',e=>{last=[e.clientX,e.clientY];this.moved=false;cv.setPointerCapture(e.pointerId)});
 cv.addEventListener('pointermove',e=>{if(!last)return;const dx=e.clientX-last[0],dy=e.clientY-last[1];if(Math.abs(dx)+Math.abs(dy)>1)this.moved=true;this.R=mm(Ry(dx*0.01),mm(Rx(dy*0.01),this.R));last=[e.clientX,e.clientY];this.draw()});
 cv.addEventListener('pointerup',e=>{if(last&&!this.moved&&this.onpick){const r=cv.getBoundingClientRect();this.onpick(this.pick((e.clientX-r.left)*cv.width/r.width,(e.clientY-r.top)*cv.height/r.height))}last=null});
 cv.addEventListener('wheel',e=>{e.preventDefault();this.zoom*=e.deltaY<0?1.1:1/1.1;this.draw()},{passive:false})}
 set(s){this.s=s;this.draw()}
 P(p){const v=mv(this.R,sub(p,this.s.center));const W=this.cv.width,H=this.cv.height,E=this.s.extent,Dd=E*6;const k=Math.min(W,H)/(2.3*E)*this.zoom*Dd/(Dd-v[2]);return [W/2+v[0]*k,H/2-v[1]*k,v[2],k]}
 pick(x,y){let b=null;for(const h of this.hits){if((x-h.x)**2+(y-h.y)**2<=h.r*h.r&&(!b||h.z>b.z))b=h}return b?b.id:null}
 draw(){if(!this.s)return;const c=this.c,W=this.cv.width,H=this.cv.height;c.clearRect(0,0,W,H);const it=[];this.hits=[];
  for(const l of this.s.lines||[]){const A=this.P(l.a),B=this.P(l.b);it.push({z:(A[2]+B[2])/2,f:()=>{c.strokeStyle=l.col;c.lineWidth=l.w||1;c.setLineDash(l.dash||[]);c.beginPath();c.moveTo(A[0],A[1]);c.lineTo(B[0],B[1]);c.stroke();c.setLineDash([])}})}
  for(const b of this.s.bonds||[]){const A=this.P(b.a),B=this.P(b.b),M=[(A[0]+B[0])/2,(A[1]+B[1])/2],w=Math.max(1,(b.w||0.12)*(A[3]+B[3])/2);
   it.push({z:A[2]*0.7+B[2]*0.3,f:()=>{c.strokeStyle=b.ca;c.lineWidth=w;c.lineCap='round';c.beginPath();c.moveTo(A[0],A[1]);c.lineTo(M[0],M[1]);c.stroke()}});
   it.push({z:B[2]*0.7+A[2]*0.3,f:()=>{c.strokeStyle=b.cb;c.lineWidth=w;c.lineCap='round';c.beginPath();c.moveTo(M[0],M[1]);c.lineTo(B[0],B[1]);c.stroke()}})}
  for(const a of this.s.atoms||[]){const Q=this.P(a.p),r=a.r*Q[3];if(a.pick!==false)this.hits.push({x:Q[0],y:Q[1],r:Math.max(r,4),z:Q[2],id:a.id});
   it.push({z:Q[2],f:()=>{c.globalAlpha=a.alpha||1;const g=c.createRadialGradient(Q[0]-r*.35,Q[1]-r*.35,Math.max(r*.1,.1),Q[0],Q[1],Math.max(r,1));g.addColorStop(0,shade(a.col,0.75));g.addColorStop(0.35,a.col);g.addColorStop(1,shade(a.col,-0.5));
    c.fillStyle=g;c.beginPath();c.arc(Q[0],Q[1],Math.max(r,1),0,6.2832);c.fill();c.lineWidth=a.hl?2.5:0.5;c.strokeStyle=a.hl?'#FFC400':'rgba(0,0,0,.4)';c.stroke();c.globalAlpha=1}})}
  it.sort((u,v)=>u.z-v.z).forEach(o=>o.f());
  c.font='12px Georgia';c.textAlign='center';for(const t of this.s.texts||[]){const Q=this.P(t.p);const w=c.measureText(t.t).width;c.fillStyle='rgba(255,255,255,.85)';c.fillRect(Q[0]-w/2-2,Q[1]-11,w+4,14);c.fillStyle=t.col||'#111';c.fillText(t.t,Q[0],Q[1])}
  const O=[46,H-40];(this.s.axes||[]).forEach(([n,d],i)=>{const v=mv(this.R,d);c.strokeStyle=['#c00','#080','#00c'][i];c.lineWidth=2;c.beginPath();c.moveTo(O[0],O[1]);c.lineTo(O[0]+v[0]*28,O[1]-v[1]*28);c.stroke();c.fillStyle=c.strokeStyle;c.fillText(n,O[0]+v[0]*38,O[1]-v[1]*38+4)})}}
// ---------------- crystal ----------------
let STR=null,UPF=[],last=null,mode='conventional',sel=null,meas=[];const ui={bonds:true,labels:false,auto:false,measure:false,size:1};
const COL={In:'#A67573',O:'#FF0D0D'},RAD={In:0.62,O:0.40},MULT={b:8,d:24,e:48};
const V=new V3($('cv'),[1,0.45,0.3]),KV=new V3($('cvk'),[1,0.6,0.35]);
const cart=(L,f)=>[0,1,2].map(k=>f[0]*L[0][k]+f[1]*L[1][k]+f[2]*L[2][k]);
function buildCrystal(){const S=STR[mode],L=S.lattice,pos=S.frac.map(f=>cart(L,f)),sp=S.species;
 const atoms=pos.map((p,i)=>({p,r:RAD[sp[i]]*ui.size,col:COL[sp[i]],id:i,hl:i===sel||meas.includes(i)}));const bonds=[],lines=[],texts=[];
 if(ui.bonds)for(const [i,j,d,s] of S.neighbors){if(d>2.6||sp[i]===sp[j])continue;const zero=!s[0]&&!s[1]&&!s[2];
  if(zero){if(i<j)bonds.push({a:pos[i],b:pos[j],ca:COL[sp[i]],cb:COL[sp[j]],w:0.13})}
  else{const pj=add(pos[j],cart(L,s));bonds.push({a:pos[i],b:mul(add(pos[i],pj),0.5),ca:COL[sp[i]],cb:COL[sp[i]],w:0.13})}}
 const C=[];for(let a=0;a<2;a++)for(let b=0;b<2;b++)for(let c=0;c<2;c++)C.push([a,b,c]);
 for(const u of C)for(const v of C){const df=u.map((x,k)=>v[k]-x);if(df.filter(x=>x!==0).length===1&&df.every(x=>x>=0))lines.push({a:cart(L,u),b:cart(L,v),col:'#333',w:1.2})}
 if(sel!==null){for(const [i,j,d,s] of S.neighbors){if(i!==sel||d>2.6||sp[i]===sp[j])continue;const pj=add(pos[j],cart(L,s));
  bonds.push({a:pos[sel],b:pj,ca:'#FFC400',cb:'#FFC400',w:0.2});if(s.some(x=>x))atoms.push({p:pj,r:RAD[sp[j]]*ui.size,col:COL[sp[j]],id:'img',alpha:.45,pick:false});texts.push({p:mul(add(pos[sel],pj),0.5),t:d.toFixed(3)+' Å'})}}
 if(meas.length>=2){for(let k=0;k<meas.length-1;k++){lines.push({a:pos[meas[k]],b:pos[meas[k+1]],col:'#6a1b9a',w:2.2,dash:[6,4]});texts.push({p:mul(add(pos[meas[k]],pos[meas[k+1]]),0.5),t:norm(sub(pos[meas[k+1]],pos[meas[k]])).toFixed(3)+' Å',col:'#6a1b9a'})}}
 if(ui.labels)pos.forEach((p,i)=>texts.push({p,t:sp[i]+' '+MULT[S.wyckoff[i]]+S.wyckoff[i],col:'#222'}));
 V.set({atoms,bonds,lines,texts,center:cart(L,[.5,.5,.5]),extent:0.5*norm(add(add(L[0],L[1]),L[2]))*1.05,axes:[['x',[1,0,0]],['y',[0,1,0]],['z',[0,0,1]]]})}
function selInfo(){if(sel===null){$('selinfo').innerHTML='Click an atom.';return}const S=STR[mode],sp=S.species,p=cart(S.lattice,S.frac[sel]);
 const g={};S.neighbors.filter(n=>n[0]===sel).sort((a,b)=>a[2]-b[2]).forEach(([i,j,d])=>{const k=sp[j]+'|'+d.toFixed(3);g[k]=(g[k]||0)+1});
 $('selinfo').innerHTML=table([['atom',`#${sel} ${sp[sel]}`],['Wyckoff site',`${MULT[S.wyckoff[sel]]}${S.wyckoff[sel]}, site symmetry ${esc(S.site_symmetry[sel])}`],['fractional coordinates',S.frac[sel].map(x=>x.toFixed(4)).join(', ')],['Cartesian (Å)',p.map(x=>x.toFixed(3)).join(', ')],['coordination',`${S.coordination[sel]} ${sp[sel]==='In'?'O':'In'} neighbours within 2.6 Å`]])
  +'<p class="note">All neighbours within 3.8 Å, periodic images included (first shell drawn in gold, images transparent):</p>'+table(Object.entries(g).map(([k,n])=>{const [e,d]=k.split('|');return [e,d+' Å','× '+n]}),['element','distance','count'])}
function measInfo(){if(!STR)return;const S=STR[mode],pos=S.frac.map(f=>cart(S.lattice,f)),sp=S.species;
 if(meas.length<2){$('measinfo').innerHTML=meas.length?`first atom #${meas[0]} ${sp[meas[0]]}; click a second atom.`:(ui.measure?'Click 2 atoms for a distance, 3 for an angle.':'Enable "measure" and click atoms.');return}
 let h=`#${meas[0]} ${sp[meas[0]]} – #${meas[1]} ${sp[meas[1]]}: <b>${norm(sub(pos[meas[1]],pos[meas[0]])).toFixed(4)} Å</b>`;
 if(meas.length===3){const u=sub(pos[meas[0]],pos[meas[1]]),v=sub(pos[meas[2]],pos[meas[1]]);h+=`<br>#${meas[1]} – #${meas[2]} ${sp[meas[2]]}: <b>${norm(v).toFixed(4)} Å</b><br>angle at #${meas[1]}: <b>${(Math.acos(dot(u,v)/norm(u)/norm(v))*180/Math.PI).toFixed(2)}°</b>`}
 $('measinfo').innerHTML=h+'<p class="note">Straight-line distances inside the displayed cell (no periodic wrapping).</p>'}
V.onpick=id=>{if(id===null||id==='img')return;if(ui.measure){meas.push(id);if(meas.length>3)meas=[id]}else sel=sel===id?null:id;selInfo();measInfo();buildCrystal()};
function tog(id,key){$(id).onclick=()=>{ui[key]=!ui[key];$(id).classList.toggle('on',ui[key]);if(key==='measure'){meas=[];measInfo()}buildCrystal()}}
tog('bbonds','bonds');tog('blabels','labels');tog('bauto','auto');tog('bmeas','measure');
function setMode(m){mode=m;sel=null;meas=[];$('bconv').classList.toggle('on',m==='conventional');$('bprim').classList.toggle('on',m==='primitive');selInfo();measInfo();buildCrystal()}
$('bconv').onclick=()=>setMode('conventional');$('bprim').onclick=()=>setMode('primitive');
document.querySelectorAll('button[data-v]').forEach(b=>b.onclick=()=>{V.R=lookR(b.dataset.v.split(',').map(Number),[0,0,1]);V.draw()});
$('breset').onclick=()=>{V.R=V.R0;V.zoom=1;V.draw()};$('size').oninput=e=>{ui.size=+e.target.value;buildCrystal()};
setInterval(()=>{if(ui.auto){V.R=mm(Ry(0.006),V.R);V.draw()}},30);
function distPlot(pd){const W=460,H=150,L=36,B=26,x0=2.0,x1=3.8,X=d=>L+(d-x0)/(x1-x0)*(W-L-8);let mx=1;Object.values(pd).forEach(a=>a.forEach(([d,n])=>{if(d<=x1)mx=Math.max(mx,n)}));
 const col={'In-O':'#B5462E','In-In':'#A67573','O-O':'#1F4E79'};let s=`<svg width="${W}" height="${H}">`;
 for(let d=2.0;d<=3.81;d+=0.2)s+=`<line x1="${X(d)}" x2="${X(d)}" y1="${H-B}" y2="${H-B+4}" stroke="#555"/><text x="${X(d)}" y="${H-B+15}" font-size="10" text-anchor="middle">${d.toFixed(1)}</text>`;
 s+=`<line x1="${L}" x2="${W-8}" y1="${H-B}" y2="${H-B}" stroke="#555"/><text x="${(L+W)/2}" y="${H-2}" font-size="11" text-anchor="middle">distance (Å)</text><text x="12" y="${(H-B)/2}" font-size="11" transform="rotate(-90 12 ${(H-B)/2})" text-anchor="middle">pairs</text>`;
 for(const [k,a] of Object.entries(pd))for(const [d,n] of a){if(d>x1)continue;const h=n/mx*(H-B-14);s+=`<rect x="${X(d)-2}" y="${H-B-h}" width="4" height="${h}" fill="${col[k]||'#888'}"><title>${k} ${d} Å: ${n} pairs</title></rect>`}
 return s+Object.entries(col).map(([k,c],i)=>`<text x="${W-100}" y="${14+i*14}" font-size="11" fill="${c}">■ ${k}</text>`).join('')+'</svg>'}
function staticTables(){const C=STR.conventional,Pm=STR.primitive;
 $('celltab').innerHTML=table([['space group',`${esc(C.spacegroup)} (No. ${C.number}), point group ${esc(C.pointgroup)}`],['symmetry operations',`${C.n_ops} (conventional cell); ${Pm.n_ops} in the primitive cell, ${Pm.n_ops_with_translation} of them with a fractional translation`],
  ['lattice parameter a',`${STR.a_A} Å (experiment, Marezio 1966); relaxed value follows in stage 2`],['conventional cell',`${C.natoms} atoms, ${C.formula_units} formula units, V = ${C.volume_A3} Å³`],
  ['primitive cell (computed)',`${Pm.natoms} atoms, ${Pm.formula_units} formula units, V = ${Pm.volume_A3} Å³; vectors a/2(−1,1,1), a/2(1,−1,1), a/2(1,1,−1)`],
  ['density from the structure',`${C.density_g_cm3} g/cm³`],['coordination','In: 6 O (distorted octahedra); O: 4 In (distorted tetrahedra)'],['valence electrons (computed cell)','16 In × 13 + 24 O × 6 = 352 → 176 doubly occupied bands']]);
 $('wyck').innerHTML=table(STR.marezio.map(m=>[m.element,MULT[m.wyckoff.slice(-1)]?m.wyckoff:m.wyckoff,m.x,m.y,m.z]),['atom','Wyckoff','x','y','z'])+'<p class="note">In(8b): site symmetry −3, six equal In–O bonds. In(24d): site symmetry 2, three pairs of bonds. O(48e): general position. M. Marezio, Acta Crystallogr. 20, 723 (1966).</p>';
 const pd=C.pair_distances,rows=[];for(const k of ['In-O','In-In','O-O'])(pd[k]||[]).forEach(([d,n])=>rows.push([k,d.toFixed(3)+' Å',n]));
 $('dist').innerHTML=distPlot(pd)+'<div style="max-height:170px;overflow:auto">'+table(rows,['pair','distance','pairs per conventional cell'])+'</div>'}
// ---------------- reciprocal space ----------------
function bzScene(kp){const g=2*Math.PI/STR.a_A,H=[],Pp=[],lines=[];for(const s of [1,-1])H.push([s*g,0,0],[0,s*g,0],[0,0,s*g]);
 for(const a of [1,-1])for(const b of [1,-1])for(const c of [1,-1])Pp.push([a*g/2,b*g/2,c*g/2]);
 for(const h of H)for(const p of Pp){const ax=h.findIndex(v=>v!==0);if(Math.sign(p[ax])===Math.sign(h[ax]))lines.push({a:h,b:p,col:'#555',w:1.2})}
 const atoms=[{p:[0,0,0],r:0.012,col:'#222222',id:'G',pick:false}];(kp||[]).forEach((k,i)=>atoms.push({p:k.slice(0,3),r:0.01+0.06*Math.sqrt(k[3]),col:'#B5462E',id:i}));
 return {atoms,lines,texts:[{p:[0,0,0],t:'Γ'},{p:[g,0,0],t:'H'},{p:[g/2,g/2,g/2],t:'P'},{p:[g/2,g/2,0],t:'N'}],center:[0,0,0],extent:g*1.1,axes:[['kx',[1,0,0]],['ky',[0,1,0]],['kz',[0,0,1]]]}}
// ---------------- SCF loop diagram ----------------
const STEPS=['Electron density n(r)','Kohn-Sham potential V_KS[n]: PAW ionic + Hartree + PBE exchange-correlation','Kohn-Sham Hamiltonian H_k in plane waves at each k-point','Davidson diagonalisation: lowest eigenstates of H_k','Occupy the 176 lowest bands: new density n_out(r)','Broyden mixing of n_in and n_out; accuracy test'];
let scfStep=0,scfState={title:'',sub:''};
function wrapT(t,x,y){const w=t.split(' '),ls=[''];w.forEach(z=>{if((ls[ls.length-1]+' '+z).length>32)ls.push(z);else ls[ls.length-1]=(ls[ls.length-1]+' '+z).trim()});return ls.map((l,i)=>`<text x="${x}" y="${y-(ls.length-1)*6+i*12+4}" font-size="10.5" text-anchor="middle">${esc(l)}</text>`).join('')}
function scfSvg(){const W=530,H=340,cx=W/2,cy=H/2;let s=`<svg width="${W}" height="${H}" class="scf"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#1F4E79"/></marker></defs>`;
 const pt=i=>{const a=-Math.PI/2+i*Math.PI/3;return [cx+178*Math.cos(a),cy+124*Math.sin(a)]};
 for(let i=0;i<6;i++){const [x,y]=pt(i),[x2,y2]=pt((i+1)%6);s+=`<path d="M${x*0.62+x2*0.38} ${y*0.62+y2*0.38} L${x*0.38+x2*0.62} ${y*0.38+y2*0.62}" stroke="#1F4E79" stroke-width="1.6" marker-end="url(#ar)"/>`}
 for(let i=0;i<6;i++){const [x,y]=pt(i);s+=`<g class="${i===scfStep?'act':''}"><rect x="${x-94}" y="${y-24}" width="188" height="48" rx="6"/>${wrapT(STEPS[i],x,y)}</g>`}
 return s+`<text x="${cx}" y="${cy-6}" font-size="15" text-anchor="middle" font-weight="bold">${esc(scfState.title)}</text><text x="${cx}" y="${cy+14}" font-size="12" text-anchor="middle">${esc(scfState.sub)}</text></svg>`}
setInterval(()=>{scfStep=(scfStep+1)%6;$('scfsvg').innerHTML=scfSvg()},900);
function renderNow(d){const run=d.runs.find(r=>r.state==='running');let txt='<p>No calculation is running at the moment.</p>';scfState={title:'idle',sub:'no calculation running'};
 if(run){const it=run.iters||[],done=it.filter(i=>i.acc!=null),la=done[done.length-1]||{},cu=it[it.length-1]||{},su=run.setup||{},n=(run.name.match(/_k(\d)/)||[])[1];scfState={title:`SCF iteration ${cu.n??'-'}`,sub:la.acc?`last accuracy ${la.acc} Ry`:'starting'};
  const a0=it.length&&it[0].acc?Math.log10(it[0].acc):1,prog=la.acc?Math.min(100,Math.max(0,(a0-Math.log10(la.acc))/(a0+9)*100)):0;
  const test=run.name==='scf_ecut71_k3'?'reference point shared by both tests (71 Ry, 3×3×3)':(run.name.endsWith('_k3')?`plane-wave cutoff test at ${su['wavefunction cutoff (Ry)']} Ry`:`k-point test on a ${n}×${n}×${n} grid`);
  txt=`<p><b>${run.name}</b> — ${test}.</p><p>pw.x solves the Kohn–Sham equations [−½∇² + V<sub>KS</sub>[n](r)] ψ<sub>nk</sub>(r) = ε<sub>nk</sub> ψ<sub>nk</sub>(r) for the ${su.electrons??'-'} valence electrons of the ${su.atoms??40}-atom primitive cell (16 In × 13 e + 24 O × 6 e). Each ψ<sub>nk</sub> is a sum of plane waves with kinetic energy up to ${su['wavefunction cutoff (Ry)']??'-'} Ry; the density and potentials use ${su['density cutoff (Ry)']??'-'} Ry on the dense FFT grid (${esc(su['dense FFT grid']??'-')}).</p>
  <p>The Brillouin zone is sampled at ${su['irreducible k-points']??'-'} irreducible k-points (Monkhorst–Pack ${n}×${n}×${n}, reduced by the ${su['symmetry operations']??'-'} symmetry operations). At every k-point ${su['Kohn-Sham states']??'-'} bands are computed and the lowest 176 are filled (fixed occupations, insulator). V<sub>KS</sub> is the sum of the ionic PAW potential, the Hartree potential and the PBE exchange–correlation potential; inside the PAW spheres around each nucleus one-centre corrections restore the all-electron behaviour. The work is split over ${su['MPI processes']??'-'} MPI processes in ${su['k-point pools']??'-'} k-point pools.</p>
  <p>Iteration <b>${cu.n??'-'}</b> is in progress. Last completed iteration ${la.n??'-'}: total energy ${la.E??'-'} Ry, estimated accuracy <b>${la.acc??'-'} Ry</b>, Davidson tolerance ${la.ethr??'-'}, ${la.davidson??'-'} Davidson iterations per band, CPU time ${la.cpu??'-'} s.</p><div class="bar"><div style="width:${prog.toFixed(1)}%"></div></div>
  <p class="note">Progress toward the 1e-9 Ry threshold on a log scale: ${prog.toFixed(0)} %. The loop diagram is a schematic of every SCF iteration (Hohenberg &amp; Kohn 1964; Kohn &amp; Sham 1965; Davidson 1975; Johnson 1988); its highlighted box cycles for illustration and does not follow the sub-steps in real time.</p>`;
  const itc=it.filter(i=>i.cpu!=null),dt=itc.map((i,k)=>[i.n,k?i.cpu-itc[k-1].cpu:i.cpu]),mx=Math.max(1,...it.map(i=>i.davidson||0)),Ef=la.E;
  $('accplot').innerHTML=plot([{pts:it.filter(i=>i.acc!=null).map(i=>[i.n,lg(i.acc)]),c:'#1F4E79'}],{xl:'SCF iteration',yl:'log10 accuracy (Ry)',ylab:expo,ymin:-10,hlines:[{y:-9,c:'#2E7D32',t:'threshold 1e-9 Ry'}]});
  $('eplot').innerHTML=plot([{pts:done.slice(0,-1).filter(i=>i.E!=null).map(i=>[i.n,lg(Math.abs(i.E-Ef)/40)]),c:'#B5462E'}],{xl:'SCF iteration',yl:'log10 |dE| per atom (Ry)',ylab:expo});
  const dmax=Math.max(1,...dt.map(q=>q[1]));$('dplot').innerHTML=plot([{pts:it.map(i=>[i.n,(i.davidson||0)/mx*dmax]),c:'#B7791F',bar:true,label:'Davidson iterations (scaled)'},{pts:dt,c:'#1F4E79',label:'CPU s per step'}],{xl:'SCF iteration',yl:'seconds'});
  $('ittab').innerHTML=table(it.slice().reverse().map(i=>[i.n,i.E,i.acc,i.ethr,i.davidson,i.cpu]),['#','total energy (Ry)','accuracy (Ry)','ethr','Davidson avg','CPU (s)'])}
 $('nowtext').innerHTML=txt;$('scfsvg').innerHTML=scfSvg()}
// ---------------- references ----------------
const REFS=[['Density functional theory','ground-state energy as a functional of the density; Kohn-Sham single-particle equations','P. Hohenberg, W. Kohn, Phys. Rev. 136, B864 (1964); W. Kohn, L. J. Sham, Phys. Rev. 140, A1133 (1965)','10.1103/PhysRev.136.B864; 10.1103/PhysRev.140.A1133'],
 ['Code','Quantum ESPRESSO {version}, pw.x (conda-forge build)','P. Giannozzi et al., J. Phys.: Condens. Matter 21, 395502 (2009); P. Giannozzi et al., J. Phys.: Condens. Matter 29, 465901 (2017)','10.1088/0953-8984/21/39/395502; 10.1088/1361-648X/aa8f79'],
 ['Exchange-correlation','{xc}','J. P. Perdew, K. Burke, M. Ernzerhof, Phys. Rev. Lett. 77, 3865 (1996)','10.1103/PhysRevLett.77.3865'],
 ['Electron-ion interaction','projector augmented-wave (PAW) method','P. E. Blöchl, Phys. Rev. B 50, 17953 (1994); G. Kresse, D. Joubert, Phys. Rev. B 59, 1758 (1999)','10.1103/PhysRevB.50.17953; 10.1103/PhysRevB.59.1758'],
 ['PAW data sets','{pp}','A. Dal Corso, Comput. Mater. Sci. 95, 337 (2014) (pslibrary 1.0.0)','10.1016/j.commatsci.2014.07.043'],
 ['Basis set','plane waves: {ecut}','plane-wave PAW implementation of Giannozzi et al. (2009, 2017)','10.1088/0953-8984/21/39/395502'],
 ['Brillouin-zone sampling','{kgrid}','H. J. Monkhorst, J. D. Pack, Phys. Rev. B 13, 5188 (1976)','10.1103/PhysRevB.13.5188'],
 ['Eigensolver','iterative Davidson diagonalisation with overlap','E. R. Davidson, J. Comput. Phys. 17, 87 (1975)','10.1016/0021-9991(75)90065-0'],
 ['Density mixing','modified Broyden mixing, beta = {beta}','D. D. Johnson, Phys. Rev. B 38, 12807 (1988)','10.1103/PhysRevB.38.12807'],
 ['Crystal structure','bixbyite Ia-3, a = 10.117 Å, Wyckoff sites 8b, 24d, 48e','M. Marezio, Acta Crystallogr. 20, 723 (1966)','10.1107/S0365110X66001749'],
 ['Structure construction','ASE 3.29: space-group expansion and periodic neighbour lists','A. H. Larsen et al., J. Phys.: Condens. Matter 29, 273002 (2017)','10.1088/1361-648X/aa680e'],
 ['Symmetry analysis','spglib 2.7: space group, Wyckoff letters, primitive cell','A. Togo, I. Tanaka, arXiv:1808.01590 (2018)','arXiv:1808.01590'],
 ['Structural relaxation (stage 2)','variable-cell BFGS relaxation','R. M. Wentzcovitch, Phys. Rev. B 44, 2358 (1991)','10.1103/PhysRevB.44.2358'],
 ['Band-gap comparison','experimental fundamental gap about 2.9 eV; PBE is expected to underestimate it','A. Walsh et al., Phys. Rev. Lett. 100, 167402 (2008); P. D. C. King et al., Phys. Rev. B 79, 205211 (2009)','10.1103/PhysRevLett.100.167402; 10.1103/PhysRevB.79.205211'],
 ['Effective-mass comparison','experimental conduction-band mass about 0.18-0.21 m0','M. Feneberg et al., Phys. Rev. B 93, 045203 (2016); M. Stokey et al., J. Appl. Phys. 129, 225102 (2021)','10.1103/PhysRevB.93.045203; 10.1063/5.0052848']];
function renderRefs(cur,ex){const su=cur?cur.setup||{}:{},n=cur?(cur.name.match(/_k(\d)/)||[])[1]:null;
 const live={version:ex.version||'7.5',xc:ex.xc||'PBE',pp:(ex.species_table||'').trim().split('\n').map(l=>l.trim().split(/\s+/).join(' ')).join('; ')||'In.pbe-dn-kjpaw_psl.1.0.0.UPF, O.pbe-n-kjpaw_psl.1.0.0.UPF',
  ecut:su['wavefunction cutoff (Ry)']?`${su['wavefunction cutoff (Ry)']} Ry for wavefunctions, ${su['density cutoff (Ry)']} Ry for the density`:'-',kgrid:n?`Monkhorst-Pack ${n}×${n}×${n}, unshifted: ${su['irreducible k-points']} irreducible k-points`:'-',beta:su['mixing beta']??'-'};
 $('reftab').innerHTML=table(REFS.map(([w,s,r,doi])=>[`<b>${w}</b>`,esc(s.replace(/\{(\w+)\}/g,(m,k)=>live[k]??'')),r,doi.split('; ').map(x=>x.startsWith('arXiv')?`<a href="https://arxiv.org/abs/${x.slice(6)}" target="_blank">${x}</a>`:`<a href="https://doi.org/${x}" target="_blank">${x}</a>`).join('<br>')]),['ingredient','setting in this calculation','reference','identifier'])}
function renderPAW(ex){let h='';for(const u of UPF){const blk=((ex&&ex.pseudo)||[]).find(b=>b.includes(u.file))||'';
 h+=`<h3>${esc(u.header.element)}: ${esc(u.file)} ${u.used_now?'(used in this calculation)':'(prepared for the IWO and slab stages)'}</h3><div class="row"><div style="flex:1;min-width:300px">`+table(Object.entries(u.header).map(([k,v])=>[k,esc(v)]))+
  `</div><div style="flex:1;min-width:320px"><p class="note">Generation record inside the data file (PP_INFO):</p><pre>${esc(u.info)}</pre>`+(blk?`<p class="note">As read by pw.x in this run:</p><pre>${esc(blk)}</pre>`:'')+'</div></div>'}
 $('pawinfo').innerHTML=h+'<p class="note">wfc_cutoff and rho_cutoff are the cutoffs suggested by the data-set author; the convergence study tests whether the chosen cutoffs are sufficient for In₂O₃.</p>'}
// ---------------- results, convergence, queue ----------------
function renderResults(d){const fin=d.runs.filter(r=>r.E!=null),sel=$('sel'),cv=sel.value;sel.innerHTML=fin.map(r=>`<option ${r.name===cv?'selected':''}>${r.name}</option>`).join('');const f=fin.find(r=>r.name===sel.value)||fin[fin.length-1];
 if(f){$('final').innerHTML=table([['total energy (Ry)',f.E],['energy per atom (eV)',(f.E*13.605693/40).toFixed(4)],['HOMO / LUMO (eV)',`${f.homo} / ${f.lumo}`],['Kohn–Sham gap (eV)',f.gap?.toFixed(3)],['pressure (kbar)',f.P],['total force (Ry/Bohr)',f.force],['wall time',f.wall]].concat(Object.entries(f.terms||{}).map(([k,v])=>[k+' (Ry)',v])))+(f.stress_kbar?'<p class="note">stress tensor (kbar)</p>'+table(f.stress_kbar.map(r=>r.map(v=>v.toFixed(2)))):'');
  $('bands').innerHTML=f.edges&&f.edges.length?plot([{pts:f.edges.map((e,i)=>[i+1,e.vb]),c:'#1F4E79',label:'valence-band top'},{pts:f.edges.map((e,i)=>[i+1,e.cb]),c:'#B5462E',label:'conduction-band bottom'}],{xl:'irreducible k-point index',yl:'energy (eV)'}):'<p class="note">eigenvalues not printed yet</p>'}
 else{$('final').innerHTML='<p class="note">no run finished yet</p>';$('bands').innerHTML='<p class="note">waiting for the first finished run</p>'}
 const ec=d.runs.filter(r=>r.name.endsWith('_k3')&&r.E!=null),ref=ec.length?ec[ec.length-1]:null;let cv2='';
 if(ec.length>1)cv2+=plot([{pts:ec.map(r=>[r.setup['wavefunction cutoff (Ry)'],(r.E-ref.E)/40*1000]),c:'#1F4E79',label:'dE per atom vs highest cutoff (mRy)'}],{xl:'cutoff (Ry)',yl:'mRy/atom',w:560,hlines:[{y:1,c:'#2E7D32',t:'criterion 1 mRy/atom'}]});
 cv2+=table(d.runs.map(r=>{const e=r.E!=null&&ref?(r.E-ref.E)/40*1000:null;return [r.name,`<span class="${r.state}">${r.state}</span>`,r.E,e==null?'':e.toFixed(3),r.gap?.toFixed(3),r.P,e==null?'':(Math.abs(e)<1?'<span class="pass">within 1 mRy/atom</span>':'<span class="fail">not converged</span>')]}),['run','state','E (Ry)',`dE per atom vs ${ref?ref.name:'highest cutoff'} (mRy)`,'gap (eV)','P (kbar)','energy criterion']);
 $('conv').innerHTML=cv2+'<p class="note">Criteria fixed before the runs: a further increase of the cutoff or the k-grid must change the energy by less than 1 mRy/atom, the pressure by less than 1 kbar and the gap by less than 10 meV.</p>';
 $('queue').innerHTML=table(d.runs.map(r=>[r.name,`<span class="${r.state}">${r.state}</span>`,r.iters?r.iters.length:'',r.wall]),['run','state','SCF iterations','wall time']);
 const m=d.machine;$('mach').innerHTML=m.err?esc(m.err):table([['CPU cores (logical)',m.cores],['load average (1 min)',m.load1],['memory used',`${m.mem_used_MB} / ${m.mem_total_MB} MB`],['pw.x processes',m.pwx]]);$('log').textContent=d.log}
function renderAll(d){const run=d.runs.find(r=>r.state==='running'),fin=d.runs.filter(r=>r.E!=null),cur=run||fin[fin.length-1],ex=cur?(d.extra[cur.name]||{}):{};
 $('hdr').innerHTML=`updated ${d.time} &middot; finished ${d.runs.filter(r=>r.state==='done').length} / ${d.runs.length} &middot; pw.x processes ${d.machine.pwx??'?'} &middot; load ${d.machine.load1??'?'} &middot; refresh every 5 s`;
 renderNow(d);
 if(ex.kpts&&STR){KV.set(bzScene(ex.kpts));const g=2*Math.PI/STR.a_A;$('ktab').innerHTML=table(ex.kpts.map((k,i)=>[i+1,k.slice(0,3).map(x=>x.toFixed(4)).join(', '),k.slice(0,3).map(x=>(x/g).toFixed(3)).join(', '),k[3].toFixed(5)]),['#','k (1/Å)','k (2π/a)','weight'])}
 if(cur)$('setup').innerHTML=table(Object.entries(cur.setup||{}).concat([['PWSCF version',ex.version],['dense FFT grid',ex.dense_grid],['smooth FFT grid',ex.smooth_grid],['total RAM (estimate)',ex.ram_total],['starting wavefunctions',ex.start_wfc],['starting potential',ex.start_pot],['eigensolver',ex.diag]].filter(r=>r[1])).map(([k,v])=>[k,esc(v)]));
 renderRefs(cur,ex);renderPAW(ex);renderResults(d)}
async function tick(){let d;try{d=await (await fetch('/api')).json()}catch(e){$('hdr').textContent='dashboard server not reachable';return}last=d;renderAll(d)}
$('sel').onchange=()=>{if(last)renderResults(last)};
async function init(){const s=await (await fetch('/static')).json();STR=s.structure;UPF=s.upf;staticTables();buildCrystal();KV.set(bzScene([]));renderPAW(null);tick();setInterval(tick,5000)}
init();
</script></body></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.startswith('/api'): b = json.dumps(api()).encode(); ct = 'application/json'
            elif self.path.startswith('/static'): b = json.dumps({'structure': STRUCT, 'upf': UPF}).encode(); ct = 'application/json'
            else: b = PAGE.encode(); ct = 'text/html; charset=utf-8'
            self.send_response(200)
        except Exception as e:
            b = json.dumps({'error': repr(e)}).encode(); ct = 'application/json'; self.send_response(500)
        self.send_header('Content-Type', ct); self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass

if __name__ == '__main__':
    HTTPServer(('127.0.0.1', 8766), H).serve_forever()
