"""Detailed live DFT dashboard.  python dashboard2.py  ->  http://localhost:8766   (local only, read-only)
Parses the pw.x outputs of this folder on every /api request; the page polls every 5 s and redraws SVG charts."""
import json, math, re, subprocess, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
QUEUE = ['scf_ecut50_k3', 'scf_ecut60_k3', 'scf_ecut71_k3', 'scf_ecut85_k3', 'scf_ecut71_k2', 'scf_ecut71_k4',
         'vcrelax_ecut71_k3', 'bands_gamma', 'bands_path']
RY_EV = 13.605693122994; NAT = 40
_sys = {'t': 0, 'v': {}}

def num(p, t, g=1, f=float):
    m = re.search(p, t, re.M); return f(m.group(g)) if m else None

def parse(name):
    f = D / f'{name}.out'; r = {'name': name, 'state': 'waiting'}
    if not f.exists(): return r
    t = f.read_text(errors='replace'); r['state'] = 'done' if 'JOB DONE' in t else ('error' if 'Error' in t and '%%%%' in t else 'running')
    hdr = t.split('iteration #')[0]
    r['setup'] = {k: v for k, v in {
        'lattice parameter (Bohr)': num(r'lattice parameter \(alat\)\s+=\s+([\d.]+)', hdr),
        'cell volume (Bohr^3)': num(r'unit-cell volume\s+=\s+([\d.]+)', hdr),
        'atoms': num(r'number of atoms/cell\s+=\s+(\d+)', hdr, f=int),
        'electrons': num(r'number of electrons\s+=\s+([\d.]+)', hdr),
        'Kohn-Sham states': num(r'number of Kohn-Sham states=\s+(\d+)', hdr, f=int),
        'wavefunction cutoff (Ry)': num(r'kinetic-energy cutoff\s+=\s+([\d.]+)', hdr),
        'density cutoff (Ry)': num(r'charge density cutoff\s+=\s+([\d.]+)', hdr),
        'SCF threshold (Ry)': num(r'convergence threshold\s+=\s+([\dEe.+-]+)', hdr),
        'mixing beta': num(r'mixing beta\s+=\s+([\d.]+)', hdr),
        'symmetry operations': num(r'(\d+) Sym\. Ops\.', hdr, f=int),
        'irreducible k-points': num(r'number of k points=\s+(\d+)', hdr, f=int),
        'MPI processes': num(r'Number of MPI processes:\s+(\d+)', hdr, f=int),
        'k-point pools': num(r'K-points division:\s+npool\s+=\s+(\d+)', hdr, f=int),
        'dense FFT grid': (re.search(r'Dense\s+grid:\s+(\d+) G-vectors\s+FFT dimensions: \(\s*([\d, ]+)\)', hdr).group(0).split('grid:')[1].strip() if re.search(r'Dense\s+grid', hdr) else None),
        'RAM per process (est.)': (re.search(r'Estimated max dynamical RAM per process >\s+([\d.]+ \w+)', hdr).group(1) if re.search(r'Estimated max dynamical RAM', hdr) else None),
        'XC functional': (' '.join(re.search(r'Exchange-correlation=\s*([^\n]+)', hdr).group(1).split()) if re.search(r'Exchange-correlation=', hdr) else None)}.items() if v is not None}
    its = []
    for blk in t.split('iteration #')[1:]:
        it = {'n': num(r'^\s*(\d+)', blk, f=int), 'ethr': num(r'ethr =\s+([\dEe.+-]+)', blk), 'davidson': num(r'avg # of iterations =\s+([\d.]+)', blk),
              'cpu': num(r'total cpu time spent up to now is\s+([\d.]+)', blk), 'E': num(r'^\s+total energy\s+=\s+([-\d.]+) Ry', blk),
              'acc': num(r'estimated scf accuracy\s+<\s+([\dEe.+-]+) Ry', blk)}
        if it['n'] is not None: its.append(it)
    r['iters'] = its
    fin = t.split('End of self-consistent calculation')[-1] if 'End of self-consistent' in t else ''
    if fin:
        r['E'] = num(r'^!\s+total energy\s+=\s+([-\d.]+) Ry', fin)
        r['terms'] = {k: num(p, fin) for k, p in [('one-electron', r'one-electron contribution =\s+([-\d.]+)'), ('Hartree', r'hartree contribution\s+=\s+([-\d.]+)'),
                      ('exchange-correlation', r'xc contribution\s+=\s+([-\d.]+)'), ('Ewald', r'ewald contribution\s+=\s+([-\d.]+)'), ('one-centre PAW', r'one-center paw contrib\.\s+=\s+([-\d.]+)')]}
        m = re.search(r'highest occupied, lowest unoccupied level \(ev\):\s+([-\d.]+)\s+([-\d.]+)', fin)
        if m: r['homo'], r['lumo'] = float(m.group(1)), float(m.group(2)); r['gap'] = r['lumo'] - r['homo']
        nocc = int(round(r['setup'].get('electrons', 352) / 2)); edges = []
        for km in re.finditer(r'k =\s*([-\d.\s]+?)\s*\(\s*\d+ PWs\)\s+bands \(ev\):\s+([-\d.\s]+?)(?=\n\s*\n\s*(?:k =|highest|the Fermi|occupation))', fin):
            ev = [float(x) for x in re.findall(r'-?\d+\.\d+', km.group(2))]
            if len(ev) > nocc: edges.append({'k': [float(x) for x in re.findall(r'-?\d+\.\d+', km.group(1))], 'vb': ev[nocc - 1], 'cb': ev[nocc]})
        r['edges'] = edges
        r['force'] = num(r'Total force =\s+([\d.]+)', t)
        m = re.search(r'total\s+stress.*P=\s*([-\d.]+)\n((?:\s+[-\d.]+){6}\n(?:\s+[-\d.]+){6}\n(?:\s+[-\d.]+){6})', t)
        if m: r['P'] = float(m.group(1)); r['stress_kbar'] = [[float(x) for x in ln.split()[3:]] for ln in m.group(2).strip().split('\n')]
    m = re.search(r'PWSCF\s+:\s+(.+?)CPU\s+(.+?)WALL', t); r['wall'] = m.group(2).strip() if m else None
    vols = re.findall(r'new unit-cell volume =\s+[\d.]+ a\.u\.\^3 \(\s*([\d.]+) Ang\^3', t)
    if vols or 'number of bfgs steps' in t:          # stage 2 (vc-relax): progress of the relaxation
        Es = re.findall(r'^!\s+total energy\s+=\s+([-\d.]+) Ry', t, re.M)
        Ps = re.findall(r'P=\s*([-\d.]+)', t); Fs = re.findall(r'Total force =\s+([\d.]+)', t)
        steps = re.findall(r'number of bfgs steps\s+=\s+(\d+)', t)
        r['setup'].update({'SCF cycles done': len(Es), 'BFGS steps': int(steps[-1]) if steps else 0,
                           'latest total energy (Ry)': float(Es[-1]) if Es else None,
                           'latest pressure (kbar)': float(Ps[-1]) if Ps else None,
                           'latest total force (Ry/bohr)': float(Fs[-1]) if Fs else None,
                           'latest lattice constant a (A)': round((2 * float(vols[-1])) ** (1 / 3), 5) if vols else None,
                           'relaxation finished': 'End final coordinates' in t})
        if Fs: r['force'] = float(Fs[-1])
        if Ps: r['P'] = float(Ps[-1])
    return r

def structure():
    t = (D / 'scf_ecut71_k3.in').read_text(); a = float(re.search(r'celldm\(1\) = ([\d.]+)', t).group(1)) * 0.529177
    P = a / 2 * np.array([[-1, 1, 1], [1, -1, 1], [1, 1, -1]])
    return [{'s': m.group(1), 'xyz': (np.array(list(map(float, m.group(2, 3, 4)))) @ P).round(3).tolist()} for m in re.finditer(r'^(In|O) ([-\d.]+) ([-\d.]+) ([-\d.]+)$', t, re.M)]

def machine():
    if time.time() - _sys['t'] > 8:
        try:
            o = subprocess.run(['wsl', '-d', 'Ubuntu-22.04', '-e', 'bash', '-lc', 'cat /proc/loadavg; free -m | sed -n 2p; pgrep -c pw.x; nproc'], capture_output=True, text=True, timeout=15).stdout.split('\n')
            mem = o[1].split(); _sys['v'] = {'load1': float(o[0].split()[0]), 'mem_used_MB': int(mem[2]), 'mem_total_MB': int(mem[1]), 'pwx': int(o[2]), 'cores': int(o[3])}
        except Exception as e: _sys['v'] = {'err': str(e)}
        _sys['t'] = time.time()
    return _sys['v']

def api():
    runs = [parse(q) for q in QUEUE]; done = [r for r in runs if r.get('E') is not None]
    conv = []
    ref = next((r for r in runs if r['name'] == 'scf_ecut85_k3' and r.get('E') is not None), None)
    for r in done:
        c = {'name': r['name'], 'E_per_atom_mRy': None if not ref else (r['E'] - ref['E']) / NAT * 1000, 'gap': r.get('gap'), 'P': r.get('P')}
        conv.append(c)
    log = (D / 'convergence.log').read_text(errors='replace') if (D / 'convergence.log').exists() else ''
    return {'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'runs': runs, 'conv': conv, 'machine': machine(), 'log': log[-2500:], 'structure': structure()}

PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><title>DFT live: bulk In2O3</title><style>
body{font-family:Georgia,serif;margin:0;background:#f6f6f4;color:#222}header{background:#1F4E79;color:#fff;padding:14px 22px}h1{margin:0;font-size:22px}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(430px,1fr));gap:14px;padding:14px}section{background:#fff;border:1px solid #ddd;border-radius:4px;padding:12px 14px}
h2{font-size:16px;margin:0 0 8px;border-bottom:1px solid #eee;padding-bottom:4px}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid #eee;padding:4px 6px;text-align:left}
.done{color:#2E7D32;font-weight:bold}.running{color:#B7791F;font-weight:bold}.waiting{color:#999}.pass{color:#2E7D32}.fail{color:#B3261E}p.note{font-size:13px;color:#555;margin:6px 0}
pre{font-size:11px;background:#fafafa;border:1px solid #eee;padding:6px;max-height:180px;overflow:auto}.wide{grid-column:1/-1}.bar{height:10px;background:#e5e5e5;border-radius:5px}.bar>div{height:10px;background:#1F4E79;border-radius:5px}
select{font-family:inherit}</style></head><body>
<header><h1>Live DFT calculation: bulk In&#8322;O&#8323; (PBE-PAW, Quantum ESPRESSO 7.5)</h1><div id="hdr"></div></header><main>
<section class="wide"><h2>What is being computed now</h2><div id="now"></div></section>
<section><h2>SCF convergence: accuracy per iteration</h2><div id="accplot"></div><p class="note">The estimated SCF accuracy is an upper bound on the error in the total energy due to a not-yet-self-consistent density. The run stops when it drops below the dashed threshold (1e-9 Ry).</p></section>
<section><h2>Total energy per iteration</h2><div id="eplot"></div><p class="note">Plotted as |E(n) - E(latest)| per atom on a log scale: the energy approaches its variational minimum as the density becomes self-consistent.</p></section>
<section><h2>Diagonalisation effort and time per iteration</h2><div id="dplot"></div><p class="note">Bars: average Davidson iterations per band (the iterative eigen-solver); line: wall-clock seconds per SCF step. ethr is the diagonalisation tolerance, tightened as the SCF converges.</p></section>
<section><h2>Iteration table</h2><div id="ittab" style="max-height:300px;overflow:auto"></div></section>
<section><h2>Calculation setup (read from pw.x)</h2><div id="setup"></div></section>
<section><h2>Crystal: 40-atom primitive bixbyite cell</h2><div id="xtal"></div><p class="note">Projection on the x-y plane of the primitive cell (In large, O small; shade = depth z). Positions from the experimental structure (Marezio 1966), not yet relaxed.</p></section>
<section><h2>Final results of finished runs</h2><select id="sel"></select><div id="final"></div></section>
<section><h2>Band edges at each k-point (finished run)</h2><div id="bands"></div><p class="note">Top valence band (VB, band 176) and bottom conduction band (CB, band 177) at each irreducible k-point; the gap is the smallest CB minus the largest VB.</p></section>
<section class="wide"><h2>Convergence study against the pre-registered criteria (PROTOCOL.md)</h2><div id="conv"></div></section>
<section><h2>Queue</h2><div id="queue"></div></section>
<section><h2>Machine</h2><div id="mach"></div><h2 style="margin-top:12px">Run log</h2><pre id="log"></pre></section>
</main><script>
const $=id=>document.getElementById(id);
function plot(series,opt){const W=opt.w||420,H=opt.h||200,L=52,R=12,T=10,B=30;let xs=[],ys=[];series.forEach(s=>s.pts.forEach(p=>{if(isFinite(p[1])){xs.push(p[0]);ys.push(p[1])}}));
 if(!xs.length)return'<p class="note">waiting for data...</p>';let x0=Math.min(...xs),x1=Math.max(...xs),y0=opt.ymin??Math.min(...ys),y1=opt.ymax??Math.max(...ys);if(x1==x0)x1=x0+1;if(y1==y0)y1=y0+1;
 const X=x=>L+(x-x0)/(x1-x0)*(W-L-R),Y=y=>H-B-(y-y0)/(y1-y0)*(H-T-B);let s=`<svg width="${W}" height="${H}" style="background:#fff">`;
 for(let i=0;i<=4;i++){const yv=y0+i*(y1-y0)/4;s+=`<line x1="${L}" x2="${W-R}" y1="${Y(yv)}" y2="${Y(yv)}" stroke="#eee"/><text x="${L-4}" y="${Y(yv)+4}" font-size="10" text-anchor="end">${opt.ylab?opt.ylab(yv):yv.toPrecision(3)}</text>`}
 for(let i=0;i<=4;i++){const xv=x0+i*(x1-x0)/4;s+=`<text x="${X(xv)}" y="${H-B+14}" font-size="10" text-anchor="middle">${Math.round(xv*10)/10}</text>`}
 s+=`<text x="${(L+W)/2}" y="${H-4}" font-size="11" text-anchor="middle">${opt.xl||''}</text><text x="10" y="${H/2}" font-size="11" transform="rotate(-90 10 ${H/2})" text-anchor="middle">${opt.yl||''}</text>`;
 (opt.hlines||[]).forEach(h=>{s+=`<line x1="${L}" x2="${W-R}" y1="${Y(h.y)}" y2="${Y(h.y)}" stroke="${h.c}" stroke-dasharray="5"/><text x="${W-R}" y="${Y(h.y)-3}" font-size="10" fill="${h.c}" text-anchor="end">${h.t}</text>`});
 series.forEach(se=>{const p=se.pts.filter(q=>isFinite(q[1]));if(se.bar){p.forEach(q=>{s+=`<rect x="${X(q[0])-4}" y="${Y(q[1])}" width="8" height="${H-B-Y(q[1])}" fill="${se.c}" opacity=".45"/>`})}
  else{s+=`<polyline fill="none" stroke="${se.c}" stroke-width="2" points="${p.map(q=>X(q[0])+','+Y(q[1])).join(' ')}"/>`;p.forEach(q=>{s+=`<circle cx="${X(q[0])}" cy="${Y(q[1])}" r="2.5" fill="${se.c}"/>`})}
  if(se.label)s+=`<text x="${W-R-4}" y="${T+12+14*series.indexOf(se)}" font-size="11" fill="${se.c}" text-anchor="end">${se.label}</text>`});return s+'</svg>'}
const lg=v=>Math.log10(Math.max(v,1e-14));const exp=v=>'1e'+Math.round(v);
function table(rows,head){return '<table>'+(head?'<tr>'+head.map(h=>`<th>${h}</th>`).join('')+'</tr>':'')+rows.map(r=>'<tr>'+r.map(c=>`<td>${c??''}</td>`).join('')+'</tr>').join('')+'</table>'}
let last=null;
async function tick(){let d;try{d=await (await fetch('/api')).json()}catch(e){$('hdr').textContent='dashboard server not reachable';return}last=d;
 const run=d.runs.find(r=>r.state=='running');const nd=d.runs.filter(r=>r.state=='done').length;
 $('hdr').innerHTML=`updated ${d.time} &middot; finished ${nd} / ${d.runs.length} &middot; pw.x processes: ${d.machine.pwx??'?'} &middot; <span style="opacity:.8">refresh every 5 s</span>`;
 if(run){const it=run.iters,la=it[it.length-1]||{};const prog=la.acc?Math.min(100,Math.max(0,(Math.log10(Math.max(it[0].acc,1e-9))-Math.log10(la.acc))/(Math.log10(Math.max(it[0].acc,1e-9))+9)*100)):0;
  const kind=run.name.endsWith('_k3')?`cutoff test: plane-wave basis up to ${run.setup['wavefunction cutoff (Ry)']} Ry (density ${run.setup['density cutoff (Ry)']} Ry)`:`k-point test: ${run.name.slice(-1)}x${run.name.slice(-1)}x${run.name.slice(-1)} Monkhorst-Pack grid`;
  $('now').innerHTML=`<p><b>${run.name}</b> &mdash; ${kind}.</p><p>pw.x is iterating the Kohn-Sham self-consistency loop for ${run.setup.electrons} electrons in ${run.setup['Kohn-Sham states']} Kohn-Sham states at ${run.setup['irreducible k-points']} irreducible k-points, using ${run.setup['MPI processes']} MPI processes in ${run.setup['k-point pools']} k-point pools. Each step: build the potential from the current density &rarr; diagonalise the Hamiltonian (Davidson) &rarr; occupy the lowest 176 states &rarr; new density &rarr; Broyden mixing (beta ${run.setup['mixing beta']}).</p>
  <p>Iteration <b>${la.n??'-'}</b> &middot; accuracy <b>${la.acc??'-'} Ry</b> &middot; total energy ${la.E??'-'} Ry &middot; CPU ${la.cpu??'-'} s</p><div class="bar"><div style="width:${prog.toFixed(1)}%"></div></div><p class="note">progress toward the 1e-9 Ry threshold (log scale): ${prog.toFixed(0)} %</p>`;
  $('accplot').innerHTML=plot([{pts:it.map(i=>[i.n,lg(i.acc)]),c:'#1F4E79'}],{xl:'SCF iteration',yl:'log10 accuracy (Ry)',ylab:exp,ymin:-10,hlines:[{y:-9,c:'#2E7D32',t:'threshold 1e-9 Ry'}]});
  const Ef=la.E;$('eplot').innerHTML=plot([{pts:it.slice(0,-1).map(i=>[i.n,lg(Math.abs(i.E-Ef)/40)]),c:'#B5462E'}],{xl:'SCF iteration',yl:'log10 |dE| per atom (Ry)',ylab:exp});
  const itc=it.filter(i=>i.cpu!=null);const dt=itc.map((i,k)=>[i.n,k?i.cpu-itc[k-1].cpu:i.cpu]);const mx=Math.max(...it.map(i=>i.davidson||0),1);
  $('dplot').innerHTML=plot([{pts:it.map(i=>[i.n,(i.davidson||0)/mx*Math.max(...dt.map(q=>q[1]))]),c:'#B7791F',bar:true,label:'Davidson iters (scaled)'},{pts:dt,c:'#1F4E79',label:'CPU s per step'}],{xl:'SCF iteration',yl:'seconds'});
  $('ittab').innerHTML=table(it.slice().reverse().map(i=>[i.n,i.E,i.acc,i.ethr,i.davidson,i.cpu]),['#','total energy (Ry)','accuracy (Ry)','ethr','Davidson avg','CPU (s)']);
  $('setup').innerHTML=table(Object.entries(run.setup));}
 else{$('now').innerHTML='<p>No calculation running.</p>'}
 const fin=d.runs.filter(r=>r.E!=null);const sel=$('sel');const cur=sel.value;sel.innerHTML=fin.map(r=>`<option ${r.name==cur?'selected':''}>${r.name}</option>`).join('');
 const f=fin.find(r=>r.name==sel.value)||fin[fin.length-1];
 if(f){$('final').innerHTML=table([['total energy (Ry)',f.E],['energy per atom (eV)',(f.E*13.6057/40).toFixed(4)],['HOMO / LUMO (eV)',`${f.homo} / ${f.lumo}`],['Kohn-Sham gap (eV)',f.gap?.toFixed(3)],['pressure (kbar)',f.P],['total force (Ry/Bohr)',f.force],['wall time',f.wall]].concat(Object.entries(f.terms||{}).map(([k,v])=>[k+' (Ry)',v])))+(f.stress_kbar?'<p class="note">stress tensor (kbar)</p>'+table(f.stress_kbar.map(r=>r.map(v=>v.toFixed(2)))):'');
  $('bands').innerHTML=f.edges&&f.edges.length?plot([{pts:f.edges.map((e,i)=>[i+1,e.vb]),c:'#1F4E79',label:'VB top'},{pts:f.edges.map((e,i)=>[i+1,e.cb]),c:'#B5462E',label:'CB bottom'}],{xl:'irreducible k-point index',yl:'energy (eV)'}):'<p class="note">eigenvalues not printed yet</p>'}
 else{$('final').innerHTML='<p class="note">no run finished yet</p>';$('bands').innerHTML='<p class="note">waiting for the first finished run</p>'}
 const ec=d.runs.filter(r=>r.name.endsWith('_k3')&&r.E!=null).map(r=>[r.setup['wavefunction cutoff (Ry)'],r]);const ref=ec.length?ec[ec.length-1][1]:null;
 let cv='';if(ec.length>1){cv+=plot([{pts:ec.map(([e,r])=>[e,(r.E-ref.E)/40*1000]),c:'#1F4E79',label:'dE/atom vs highest cutoff (mRy)'}],{xl:'cutoff (Ry)',yl:'mRy/atom',w:560,hlines:[{y:1,c:'#2E7D32',t:'criterion 1 mRy/atom'}]})}
 cv+=table(d.runs.map(r=>{const e=r.E!=null&&ref?(r.E-ref.E)/40*1000:null;return [r.name,r.state,r.E,e==null?'':e.toFixed(3),r.gap?.toFixed(3),r.P,e==null?'':(Math.abs(e)<1?'<span class=pass>within 1 mRy/atom</span>':'<span class=fail>not converged</span>')]}),['run','state','E (Ry)','dE/atom vs 85 Ry (mRy)','gap (eV)','P (kbar)','energy criterion']);
 cv+='<p class="note">Criteria fixed before the runs: a further increase of cutoff or k-grid must change energy by &lt; 1 mRy/atom, pressure by &lt; 1 kbar and the gap by &lt; 10 meV.</p>';$('conv').innerHTML=cv;
 $('queue').innerHTML=table(d.runs.map(r=>[r.name,`<span class="${r.state}">${r.state}</span>`,r.iters?r.iters.length:'',r.wall]),['run','state','SCF iterations','wall time']);
 const m=d.machine;$('mach').innerHTML=m.err?m.err:table([['CPU cores (logical)',m.cores],['load average (1 min)',m.load1],['memory used',`${m.mem_used_MB} / ${m.mem_total_MB} MB`],['pw.x processes',m.pwx]]);
 $('log').textContent=d.log;
 if(!$('xtal').dataset.done){const a=d.structure,xs=a.map(q=>q.xyz[0]),ys=a.map(q=>q.xyz[1]),zs=a.map(q=>q.xyz[2]);const x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys),z0=Math.min(...zs),z1=Math.max(...zs);
  let s='<svg width="400" height="300" style="background:#fff">';a.slice().sort((p,q)=>p.xyz[2]-q.xyz[2]).forEach(q=>{const x=20+(q.xyz[0]-x0)/(x1-x0)*360,y=280-(q.xyz[1]-y0)/(y1-y0)*260,sh=0.35+0.65*(q.xyz[2]-z0)/(z1-z0);
  s+=q.s=='In'?`<circle cx="${x}" cy="${y}" r="9" fill="rgba(31,78,121,${sh})" stroke="#1F4E79"/>`:`<circle cx="${x}" cy="${y}" r="5" fill="rgba(181,70,46,${sh})" stroke="#B5462E"/>`});
  $('xtal').innerHTML=s+'</svg><p class="note">16 In (blue), 24 O (red)</p>';$('xtal').dataset.done=1}}
$('sel').onchange=()=>tick();tick();setInterval(tick,5000);
</script></body></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api'): b = json.dumps(api()).encode(); ct = 'application/json'
        else: b = PAGE.encode(); ct = 'text/html; charset=utf-8'
        self.send_response(200); self.send_header('Content-Type', ct); self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass
if __name__ == '__main__':
    HTTPServer(('127.0.0.1', 8766), H).serve_forever()
