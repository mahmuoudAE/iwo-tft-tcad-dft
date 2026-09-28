"""Live dashboard for the DFT runs in this folder.  python dashboard.py  ->  http://localhost:8765
Reads the pw.x *.out files and convergence.log every request; the page refreshes every 10 s. Local only."""
import html, re, subprocess
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
D = Path(__file__).resolve().parent
QUEUE = ['scf_ecut50_k3', 'scf_ecut60_k3', 'scf_ecut71_k3', 'scf_ecut85_k3', 'scf_ecut71_k2', 'scf_ecut71_k4']
EXPLAIN = {
 'ecut': 'Plane-wave cutoff test: the same crystal is computed with a larger basis set; the result is converged when the energy stops changing (< 1 mRy/atom).',
 'k': 'k-point test: the Brillouin zone is sampled more finely; converged when energy, pressure and gap stop changing.'}

def parse(name):
    f = D / f'{name}.out'
    if not f.exists(): return {'state': 'waiting'}
    t = f.read_text(errors='replace'); r = {'state': 'done' if 'JOB DONE' in t else 'running'}
    r['acc'] = [float(x) for x in re.findall(r'estimated scf accuracy\s+<\s+([\d.Ee+-]+) Ry', t)]
    r['iters'] = len(re.findall(r'iteration #', t))
    m = re.findall(r'total cpu time spent up to now is\s+([\d.]+) secs', t); r['cpu'] = float(m[-1]) if m else 0
    m = re.search(r'^!\s+total energy\s+=\s+([-\d.]+) Ry', t, re.M); r['E'] = float(m.group(1)) if m else None
    m = re.search(r'highest occupied, lowest unoccupied level \(ev\):\s+([-\d.]+)\s+([-\d.]+)', t)
    r['gap'] = float(m.group(2)) - float(m.group(1)) if m else None
    m = re.search(r'P=\s*([-\d.]+)', t); r['P'] = float(m.group(1)) if m else None
    m = re.search(r'number of k points=\s+(\d+)', t); r['nk'] = m.group(1) if m else '?'
    m = re.search(r'Number of MPI processes:\s+(\d+)', t); r['mpi'] = m.group(1) if m else '?'
    m = re.search(r'PWSCF\s+:\s+(.+?)WALL', t); r['wall'] = m.group(1).split('CPU')[-1].strip() if m else ''
    r['conv_thr'] = 1e-9
    return r

def spark(acc):
    if len(acc) < 2: return ''
    import math
    ys = [math.log10(max(a, 1e-12)) for a in acc]; lo, hi = -10, max(ys) + 0.5
    W, H = 360, 120; pts = ' '.join(f'{10 + i * (W - 20) / max(1, len(ys) - 1):.1f},{H - 10 - (y - lo) / (hi - lo) * (H - 20):.1f}' for i, y in enumerate(ys))
    ythr = H - 10 - (-9 - lo) / (hi - lo) * (H - 20)
    return (f'<svg width="{W}" height="{H}" style="border:1px solid #ccc;background:#fff">'
            f'<line x1="10" x2="{W - 10}" y1="{ythr:.1f}" y2="{ythr:.1f}" stroke="#2E7D32" stroke-dasharray="4"/>'
            f'<text x="{W - 150}" y="{ythr - 4:.1f}" font-size="10" fill="#2E7D32">target 1e-9 Ry</text>'
            f'<polyline fill="none" stroke="#1F4E79" stroke-width="2" points="{pts}"/></svg>')

def page():
    try: nproc = subprocess.run(['wsl', '-d', 'Ubuntu-22.04', '-e', 'pgrep', '-c', 'pw.x'], capture_output=True, text=True, timeout=10).stdout.strip() or '0'
    except Exception: nproc = '?'
    log = (D / 'convergence.log').read_text(errors='replace') if (D / 'convergence.log').exists() else ''
    rows, cur = [], None; done = 0
    for q in QUEUE:
        r = parse(q); done += r['state'] == 'done'
        if r['state'] == 'running': cur = (q, r)
        kind = 'ecut' if q.endswith('_k3') else 'k'
        rows.append(f"<tr><td>{q}</td><td class='{r['state']}'>{r['state']}</td><td>{r.get('iters', '')}</td>"
                    f"<td>{'' if r.get('E') is None else f'{r['E']:.6f}'}</td><td>{'' if r.get('gap') is None else f'{r['gap']:.3f}'}</td>"
                    f"<td>{'' if r.get('P') is None else f'{r['P']:.2f}'}</td><td>{r.get('wall', '')}</td></tr>")
    body = f"""<h1>DFT live progress: bulk In<sub>2</sub>O<sub>3</sub>, stage 1 (convergence tests)</h1>
<p>Updated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC &nbsp;|&nbsp; pw.x processes running: <b>{nproc}</b> &nbsp;|&nbsp; finished {done} / {len(QUEUE)}</p>
<h2>What is happening</h2>
<p>Quantum ESPRESSO (pw.x, PBE-PAW) solves the Kohn-Sham equations for the 40-atom primitive bixbyite cell of In<sub>2</sub>O<sub>3</sub>
(16 In, 24 O, 352 valence electrons). Each calculation is a self-consistent field (SCF) loop: guess the electron density, compute the potential,
solve for the wavefunctions, mix old and new density, repeat. The <i>estimated scf accuracy</i> must fall below 1e-9 Ry; then the total energy,
pressure and band gap are printed. Six calculations run one after another to find the smallest cutoff and k-grid that give converged results
(protocol: PROTOCOL.md).</p>"""
    if cur:
        q, r = cur; kind = 'ecut' if q.endswith('_k3') else 'k'
        body += (f"<h2>Now running: {q}</h2><p>{EXPLAIN[kind]}</p><p>MPI processes {r['mpi']}, irreducible k-points {r['nk']}, "
                 f"SCF iteration {r['iters']}, last accuracy {r['acc'][-1] if r['acc'] else '-'} Ry, CPU time {r['cpu']:.0f} s</p>"
                 f"<p>SCF accuracy per iteration (log scale):</p>{spark(r['acc'])}")
    body += "<h2>Queue and results</h2><table><tr><th>calculation</th><th>state</th><th>SCF iterations</th><th>total energy (Ry)</th><th>KS gap (eV)</th><th>pressure (kbar)</th><th>wall time</th></tr>" + ''.join(rows) + '</table>'
    body += f"<h2>Log</h2><pre>{html.escape(log[-3000:])}</pre>"
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="10"><title>DFT progress</title>
<style>body{{font-family:Georgia,serif;max-width:900px;margin:24px auto;padding:0 16px;color:#222;background:#fafafa}}table{{border-collapse:collapse;width:100%}}
td,th{{border-bottom:1px solid #ddd;padding:6px;text-align:left;font-size:14px}}.done{{color:#2E7D32;font-weight:bold}}.running{{color:#B7791F;font-weight:bold}}.waiting{{color:#888}}pre{{background:#fff;border:1px solid #ddd;padding:8px}}</style></head><body>{body}</body></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        b = page().encode(); self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass
HTTPServer(('127.0.0.1', 8765), H).serve_forever()
