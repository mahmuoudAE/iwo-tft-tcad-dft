"""Map LaTeX errors in main.log to source files and lines."""
import re
from collections import Counter
from pathlib import Path
R = Path(__file__).resolve().parents[1]
log = (R / 'main.log').read_text(encoding='latin-1')
cur = 'main.tex'; out = []; lines = log.splitlines()
for i, ln in enumerate(lines):
    for m in re.finditer(r'\((\./[^\s()]+\.tex)', ln): cur = m.group(1)
    if ln.startswith('! '):
        l = next((re.search(r'l\.(\d+)', x) for x in lines[i:i + 12] if re.search(r'^l\.(\d+)', x)), None)
        ctx = next((x for x in lines[i:i + 12] if re.search(r'^l\.\d+', x)), '')
        out.append((cur, l.group(1) if l else '?', ln[2:60], ctx[:110]))
c = Counter((o[0], o[2]) for o in out)
for k, v in c.most_common(40): print(v, k)
print('---- first per file:')
seen = set()
for o in out:
    if o[0] not in seen: seen.add(o[0]); print(o)
for m in re.finditer(r"(Reference|Citation) `([^']+)' .*undefined", log): print('UNDEF', m.group(2))
