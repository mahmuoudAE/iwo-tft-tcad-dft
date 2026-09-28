"""Fix: use the last COMPLETED SCF iteration for status/energy reference; full XC description."""
from pathlib import Path
H = Path(__file__).resolve().parent
d3 = (H / 'dashboard3.py').read_text(encoding='utf-8')
old = "if(run){const it=run.iters||[],la=it[it.length-1]||{},su=run.setup||{},n=(run.name.match(/_k(\\d)/)||[])[1];scfState={title:`SCF iteration ${la.n??'-'}`,sub:la.acc?`accuracy ${la.acc} Ry`:'starting'};"
new = ("if(run){const it=run.iters||[],done=it.filter(i=>i.acc!=null),la=done[done.length-1]||{},cu=it[it.length-1]||{},su=run.setup||{},n=(run.name.match(/_k(\\d)/)||[])[1];"
       "scfState={title:`SCF iteration ${cu.n??'-'}`,sub:la.acc?`last accuracy ${la.acc} Ry`:'starting'};")
assert old in d3; d3 = d3.replace(old, new)
old2 = "<p>Iteration <b>${la.n??'-'}</b>: total energy ${la.E??'-'} Ry, estimated accuracy <b>${la.acc??'-'} Ry</b>, Davidson tolerance ${la.ethr??'-'}, ${la.davidson??'-'} Davidson iterations per band, CPU time ${la.cpu??'-'} s.</p>"
new2 = "<p>Iteration <b>${cu.n??'-'}</b> is in progress. Last completed iteration ${la.n??'-'}: total energy ${la.E??'-'} Ry, estimated accuracy <b>${la.acc??'-'} Ry</b>, Davidson tolerance ${la.ethr??'-'}, ${la.davidson??'-'} Davidson iterations per band, CPU time ${la.cpu??'-'} s.</p>"
assert old2 in d3; d3 = d3.replace(old2, new2)
old3 = "$('eplot').innerHTML=plot([{pts:it.slice(0,-1).filter(i=>i.E!=null).map(i=>[i.n,lg(Math.abs(i.E-Ef)/40)]),c:'#B5462E'}]"
new3 = "$('eplot').innerHTML=plot([{pts:done.slice(0,-1).filter(i=>i.E!=null).map(i=>[i.n,lg(Math.abs(i.E-Ef)/40)]),c:'#B5462E'}]"
assert old3 in d3; d3 = d3.replace(old3, new3)
old4 = "    m = re.search(r'Exchange-correlation=\\s*(\\S+)\\s*\\n\\s*\\(([\\d\\s]+)\\)', hdr)\n    e['xc'] = f\"{m.group(1)} (internal indices {' '.join(m.group(2).split())})\" if m else None"
new4 = "    m = re.search(r'Exchange-correlation=\\s*([^\\n]+)\\n\\s*\\(([\\d\\s]+)\\)', hdr)\n    e['xc'] = f\"{' '.join(m.group(1).split())} = PBE (internal indices {' '.join(m.group(2).split())})\" if m else None"
assert old4 in d3; d3 = d3.replace(old4, new4)
(H / 'dashboard3.py').write_text(d3, encoding='utf-8')
d2 = (H / 'dashboard2.py').read_text(encoding='utf-8')
d2 = d2.replace("re.search(r'Exchange-correlation=\\s*(\\S+)', hdr).group(1)", "' '.join(re.search(r'Exchange-correlation=\\s*([^\\n]+)', hdr).group(1).split())")
(H / 'dashboard2.py').write_text(d2, encoding='utf-8')
print('patched')
