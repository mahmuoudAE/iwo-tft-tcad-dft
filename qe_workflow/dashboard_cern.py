"""Live dashboard of the CERN / local DFT workflow.  python dashboard_cern.py [port]  ->  http://localhost:8767

Read-only. Serves cern_htcondor/results/{status.json, status_history.jsonl, summary.json} and the tail of
monitor.log; `dft_flow.sh watch` refreshes those files. The page polls every 20 s.
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE / 'cern_htcondor' / 'results'


def load(name, default):
    try:
        return json.loads((RES / name).read_text(encoding='utf-8'))
    except Exception:
        return default


def api():
    hist = []
    try:
        for line in (RES / 'status_history.jsonl').read_text(encoding='utf-8').splitlines()[-300:]:
            try:
                hist.append(json.loads(line))
            except Exception:
                pass
    except FileNotFoundError:
        pass
    try:
        mon = (HERE / 'cern_htcondor' / 'monitor.log').read_text(encoding='utf-8').splitlines()[-40:]
    except FileNotFoundError:
        mon = []
    def txt(p, n=None):
        try:
            t = (HERE / p).read_text(encoding='utf-8', errors='replace')
            return '\n'.join(t.splitlines()[-n:]) if n else t
        except Exception:
            return ''
    docs = {'Results log': txt('cern_htcondor/results/RESULTS_LOG.md'), 'CERN protocol': txt('cern_htcondor/PROTOCOL_CERN.md'),
            'Bulk protocol (stages 1-3)': txt('bulk_In2O3_protocol/PROTOCOL.md'), 'Events': txt('cern_htcondor/events.log', 200),
            'Submissions': txt('cern_htcondor/submit_20260927.log', 150), 'Workflow README': txt('README_WORKFLOW.md')}
    return {'status': load('status.json', {}), 'history': hist, 'summary': load('summary.json', {}), 'monitor': mon,
            'resources': load('resources.json', {}), 'docs': docs}


PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IWO DFT Live</title><style>
:root{--bg:#f7f7f5;--card:#fff;--ink:#1d1d1f;--mute:#6b6b70;--line:#e3e3e0;--acc:#2563eb;--ok:#15803d;--warn:#b45309;--bad:#b91c1c}
@media (prefers-color-scheme:dark){:root{--bg:#121214;--card:#1c1c1f;--ink:#ececef;--mute:#9b9ba3;--line:#2c2c31;--acc:#60a5fa;--ok:#4ade80;--warn:#fbbf24;--bad:#f87171}}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,Segoe UI,sans-serif}
main{max-width:1150px;margin:0 auto;padding:18px 16px 40px}h1{font-size:20px;margin:0 0 2px}h2{font-size:15px;margin:0 0 10px}
.sub{color:var(--mute);font-size:12.5px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px;margin-top:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:5px 7px;border-bottom:1px solid var(--line);white-space:nowrap}
th{color:var(--mute);font-weight:600;font-size:12px}td.n{text-align:right;font-variant-numeric:tabular-nums}
.pill{display:inline-block;padding:1px 8px;border-radius:99px;font-size:12px;font-weight:600}
.run{color:var(--ok);background:color-mix(in srgb,var(--ok) 14%,transparent)}.idle{color:var(--warn);background:color-mix(in srgb,var(--warn) 14%,transparent)}
.held{color:var(--bad);background:color-mix(in srgb,var(--bad) 14%,transparent)}.done{color:var(--acc);background:color-mix(in srgb,var(--acc) 14%,transparent)}
.kpi{display:flex;gap:18px;flex-wrap:wrap}.kpi div{min-width:120px}.kpi b{display:block;font-size:20px}.kpi span{color:var(--mute);font-size:12px}
pre{font-size:11.5px;color:var(--mute);white-space:pre-wrap;margin:0;max-height:260px;overflow:auto}.full{grid-column:1/-1}
svg text{fill:var(--mute);font-size:10px}.err{color:var(--bad);font-weight:600}</style></head><body><main>
<h1>IWO / In&#8322;O&#8323; DFT: live workflow</h1><div class="sub" id="upd">loading...</div>
<div class="grid">
<section class="card full"><h2>Experiment overview</h2>
<p><b>Goal.</b> Replace the borrowed pure-In&#8322;O&#8323; DFT proxies in the IWO TFT TCAD model with our own computed values: the confinement gap shift &Delta;Eg(t), the in-plane mass m*(t), and the effect of W doping. Computed, not validated.</p>
<p><b>Method.</b> Quantum ESPRESSO, PBE, PAW pslibrary 1.0.0, 71/568 Ry. Bixbyite Ia-3 (Marezio 1966). Slabs built with Lin et al., ACS Nano 16, 21536 (2022), p. 21542: In layer removed, 1 H per surface O, 25 &Aring; vacuum, 3&times;3&times;1 k-points. W on 8b and 24d sites of the 80-atom cell (3.1 %). All criteria fixed in advance: see protocols below.</p>
<p><b>Where it runs.</b> Laptop (WSL, 10 MPI) for bulk stages 1&ndash;3. CERN HTCondor for the rest: CPU (Xeon E5-2650 v4 and AMD EPYC nodes) plus GPUs (A100, H100 NVL, H200) via NVIDIA QE 7.3.1. GPU benchmark: identical result (&Delta;E = 5&times;10&#8315;&#8311; Ry), 8.2&times; faster than 16 CPU cores.</p>
<table><tr><th>Date (UTC)</th><th>Milestone</th></tr>
<tr><td>26 Sep</td><td>Stage 1 convergence: 71 Ry, 3&times;3&times;3. CERN set up, QE on EOS, test job OK.</td></tr>
<tr><td>27 Sep 00:54</td><td>Stage 2 vc-relax: a = 10.306 &Aring; (+1.87 %; Lin 10.30)</td></tr>
<tr><td>27 Sep</td><td>First CERN batch. Fixes: MPI/hyperthreads, slab-2 memory, CG bands, OpenBLAS 65 threads (17&ndash;30&times; slowdown), bigmcore queue</td></tr>
<tr><td>27 Sep 17:02</td><td>Stage 3: gap 0.889 eV, m* 0.159 m&#8320;, &alpha; 0.55&ndash;0.63 eV&#8315;&sup1;</td></tr>
<tr><td>27&ndash;28 Sep</td><td>Vacuum test passed (&le; 0.1 meV). W-24d preferred by 0.26 eV; W&ndash;O &asymp; 1.97&ndash;1.98 &Aring; (W&#8310;&#8314;). W-8b moment 0.74 &mu;B (preliminary).</td></tr>
<tr><td>28 Sep</td><td>slab2_v25 lost (24 h limit); EOS checkpoints added. GPU benchmark passed; relaxations moved to GPU; H100/H200 only; one-file workflow with auto-allocation and watchdog.</td></tr></table></section>
<section class="card full"><h2>Jobs (CERN HTCondor)</h2><div id="jobs"></div></section>
<section class="card full"><h2>CERN resources available now</h2><div id="res"></div></section>
<section class="card full"><h2>SCF progress over time (cumulative iterations per job)</h2><div id="chart"></div></section>
<section class="card"><h2>Bulk In&#8322;O&#8323; reference (PBE, local)</h2><div id="bulk"></div></section>
<section class="card"><h2>W in In&#8322;O&#8323; (80-atom cell, 3.1 % W)</h2><div id="iwo"></div></section>
<section class="card full"><h2>Slabs: gap, band edges, mass vs Lin et al. (2022)</h2><div id="slabs"></div></section>
<section class="card full"><h2>Monitor log</h2><pre id="mon"></pre></section>
<section class="card full"><h2>Documents (live from disk)</h2><div id="tabs"></div><pre id="doc" style="max-height:600px"></pre></section></div></main>
<script>
const f=(x,d=3)=>x==null||x==='NA'?'&ndash;':(typeof x==='number'?x.toFixed(d):x);
const ST={1:['idle','idle'],2:['running','run'],5:['held','held']};
function jobs(s){if(s.error)return `<p class="err">${s.error}</p>`;const J=s.jobs||[];
 const run=J.filter(j=>j.state===2),gpu={};run.forEach(j=>{if(j.gpu_hw&&j.gpu_hw!=='none'){const m=j.gpu_hw.split('|')[0];gpu[m]=(gpu[m]||0)+1}});
 const ng=run.reduce((s,j)=>s+(parseInt(j.gpus)||0),0),nc=run.reduce((s,j)=>s+(j.cpus||0),0);
 let h=`<div class="kpi" style="margin-bottom:8px"><div><b>${run.length}</b><span>jobs running</span></div><div><b>${nc}</b><span>CPU cores in use</span></div><div><b>${ng}</b><span>GPUs in use: ${Object.entries(gpu).map(([k,v])=>k.replace(/^\d+x/,'')+(v>1?' &times;'+v:'')).join(', ')||'none'}</span></div></div>`;
 h+='<table><tr><th>Job</th><th>ID</th><th>State</th><th>CPUs</th><th>GPU (util.)</th><th>CPU model</th><th>Step</th><th>SCF it.</th><th>BFGS</th><th>Last energy (Ry)</th><th>SCF acc. (Ry)</th></tr>';
 for(const j of J){const [t,c]=ST[j.state]||[String(j.state),'idle'];h+=`<tr><td>${j.job}</td><td>${j.id}</td><td><span class="pill ${c}">${t}</span></td><td class="n">${j.cpus}</td><td>${(j.gpu_hw||'&ndash;').replace('|',' &middot; ')}</td><td>${j.cpu_hw||'&ndash;'}</td><td>${j.step}</td><td class="n">${j.scf_it}</td><td class="n">${j.bfgs}</td><td class="n">${j.energy}</td><td class="n">${j.acc}</td></tr>`}
 for(const d of s.finished||[])h+=`<tr><td>${d}</td><td></td><td><span class="pill done">finished</span></td><td colspan=7></td></tr>`;
 return h+'</table>'}
function chart(H){const series={};H.forEach(p=>(p.jobs||[]).forEach(j=>{if(j.state!==2)return;(series[j.job+' ('+j.step+')']??=[]).push([Date.parse(p.time),j.scf_it])}));
 const names=Object.keys(series);if(!names.length)return '<p class="sub">history appears after a few watch cycles</p>';
 const W=1080,Hh=220,P=36;let t0=Infinity,t1=-Infinity,y1=1;names.forEach(n=>series[n].forEach(([t,y])=>{t0=Math.min(t0,t);t1=Math.max(t1,t);y1=Math.max(y1,y)}));
 if(t1===t0)t1=t0+1;const X=t=>P+(W-2*P)*(t-t0)/(t1-t0),Y=y=>Hh-P+(-(Hh-2*P))*y/y1;
 const pal=['#2563eb','#15803d','#b45309','#9333ea','#dc2626','#0891b2','#4d7c0f','#be185d'];
 let g=`<svg viewBox="0 0 ${W} ${Hh}" width="100%"><line x1="${P}" y1="${Hh-P}" x2="${W-P}" y2="${Hh-P}" stroke="currentColor" opacity=".25"/><text x="${P}" y="${Hh-P+14}">${new Date(t0).toISOString().slice(5,16)}Z</text><text x="${W-P-80}" y="${Hh-P+14}">${new Date(t1).toISOString().slice(5,16)}Z</text><text x="2" y="${P}">${y1}</text>`;
 names.forEach((n,i)=>{const pts=series[n].map(([t,y])=>X(t)+','+Y(y)).join(' ');g+=`<polyline fill="none" stroke="${pal[i%8]}" stroke-width="2" points="${pts}"/><text x="${W-P-260}" y="${P+12*i}" style="fill:${pal[i%8]}">&#9632; ${n}</text>`});return g+'</svg>'}
function bulk(b,L){if(!b.a_A)return '<p class="sub">no bulk results</p>';
 return `<div class="kpi"><div><b>${f(b.a_A,4)} &Aring;</b><span>a (exp. ${b.a_exp_A}; Lin ${L.a_A})</span></div><div><b>${f(b.gap_fundamental_eV)} eV</b><span>PBE gap (Lin ${L.gap_bulk_eV})</span></div><div><b>${f(b.mstar_m0)} m&#8320;</b><span>CB mass (Lin ${L.mstar_bulk}; exp. 0.18&ndash;0.21)</span></div></div>`}
function iwo(w){if(!w||!w['8b'])return '<p class="sub">waiting for the relaxations</p>';
 let h='<table><tr><th>W site</th><th>E (Ry)</th><th>BFGS</th><th>W&ndash;O (&Aring;)</th><th>mean</th><th>moment (&mu;B)</th><th>source</th></tr>';
 for(const s of ['8b','24d']){const r=w[s];if(!r)continue;h+=`<tr><td>${s}</td><td class="n">${f(r.E_Ry,5)}</td><td class="n">${f(r.bfgs_steps,0)}</td><td>${r.W_O_A.join(', ')}</td><td class="n">${f(r.W_O_mean_A)}</td><td class="n">${f(r.total_magnetization_muB,2)}</td><td>${r.source}</td></tr>`}
 h+='</table>';if(w.dE_8b_minus_24d_eV!=null)h+=`<p><b>Preferred site: ${w.preferred_site}</b> (E(8b) &minus; E(24d) = ${f(w.dE_8b_minus_24d_eV)} eV). Shannon W&ndash;O: W&#8310;&#8314; 1.98, W&#8309;&#8314; 2.00, W&#8308;&#8314; 2.04 &Aring;.</p>`;return h}
function slabs(S,L,b){if(!S||!S.length)return '<p class="sub">no slab results yet</p>';
 let h='<table><tr><th>Job</th><th>relaxed</th><th>gap (eV)</th><th>&Delta;Eg vs bulk</th><th>EA (eV)</th><th>IP (eV)</th><th>m* (m&#8320;)</th><th>force (Ry/bohr)</th></tr>';
 for(const r of S)h+=`<tr><td>${r.job}</td><td>${r.relaxed?'yes':'no'}</td><td class="n">${f(r.gap_eV,4)}</td><td class="n">${f(r.dEg_eV)}</td><td class="n">${f(r.EA_eV)}</td><td class="n">${f(r.IP_eV)}</td><td class="n">${f(r.mstar_m0)}</td><td class="n">${f(r.total_force_Ry_bohr,3)}</td></tr>`;
 return h+`</table><p class="sub">Lin et al. (${L.page}): &Delta;Eg = +${(L.gap_095nm_eV-L.gap_bulk_eV).toFixed(2)} eV (0.95 nm), +${(L.gap_198nm_eV-L.gap_bulk_eV).toFixed(2)} eV (1.98 nm); m* = ${L.mstar_095nm} / ${L.mstar_198nm} m&#8320;. Unrelaxed slabs are preliminary.</p>`}
function res(r){if(!r||!r.time)return '<p class="sub">no resource snapshot yet</p>';
 let h=`<div class="kpi"><div><b>${r.free_cores}</b><span>free CPU cores</span></div><div><b>${r.slots_16c}</b><span>slots &ge;16 cores/32 GB</span></div><div><b>${r.slots_32c}</b><span>slots &ge;32 cores/64 GB</span></div><div><b>${r.slots_64c}</b><span>slots &ge;64 cores</span></div><div><b>${r.gpus_free} / ${r.gpus_total}</b><span>GPUs free / total (${r.gpu_nodes} nodes)</span></div></div>`;
 h+='<table><tr><th>GPU model</th><th>total</th><th>free</th></tr>';for(const [k,v] of Object.entries(r.gpu_models||{}).sort((a,b)=>b[1][1]-a[1][1]))h+=`<tr><td>${k}</td><td class="n">${v[0]}</td><td class="n">${v[1]}</td></tr>`;
 return h+`</table><p class="sub">snapshot ${r.time}</p>`}
let DOCS={},CUR='Results log';
function showDoc(k){CUR=k;document.getElementById('doc').textContent=DOCS[k]||'(empty)';
 document.getElementById('tabs').innerHTML=Object.keys(DOCS).map(n=>`<button onclick="showDoc('${n}')" style="margin:0 6px 8px 0;padding:3px 10px;border-radius:6px;border:1px solid var(--line);background:${n===CUR?'var(--acc)':'var(--card)'};color:${n===CUR?'#fff':'var(--ink)'};cursor:pointer">${n}</button>`).join('')}
async function tick(){try{const d=await (await fetch('/api')).json();document.getElementById('res').innerHTML=res(d.resources);DOCS=d.docs||{};showDoc(CUR);const s=d.status||{},S=d.summary||{},L=S.lin2022||{};
 document.getElementById('upd').textContent=`queue: ${s.time||'n/a'}  |  results: ${S.updated||'n/a'}  |  page refreshes every 20 s`;
 document.getElementById('jobs').innerHTML=jobs(s);document.getElementById('chart').innerHTML=chart(d.history||[]);
 document.getElementById('bulk').innerHTML=bulk(S.bulk||{},L);document.getElementById('iwo').innerHTML=iwo(S.iwo);
 document.getElementById('slabs').innerHTML=slabs(S.slabs,L,S.bulk);document.getElementById('mon').textContent=(d.monitor||[]).join('\n')}
 catch(e){document.getElementById('upd').textContent='dashboard server not reachable'}}
tick();setInterval(tick,20000);
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body, ctype = (json.dumps(api()).encode(), 'application/json') if self.path.startswith('/api') else (PAGE.encode(), 'text/html; charset=utf-8')
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8767
    print(f'dashboard on http://localhost:{port}')
    ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
