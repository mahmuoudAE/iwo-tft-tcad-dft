"""Wrap macros that already carry a sub/superscript before another _ or ^ (double sub/superscript errors)."""
import re
from pathlib import Path
R = Path(__file__).resolve().parents[1]
pre = (R / 'preamble.tex').read_text(encoding='ascii')
sub, sup = set(), set()
for m in re.finditer(r'\\newcommand\{\\(\w+)\}\{(.*)\}', pre):
    if '_' in m.group(2): sub.add(m.group(1))
    if '^' in m.group(2): sup.add(m.group(1))
n = 0
for f in list((R / 'chapters').glob('*.tex')) + list((R / 'appendices').glob('*.tex')):
    t = f.read_text(encoding='ascii'); t0 = t
    t = re.sub(r'(?<!\{)\\(' + '|'.join(sorted(sub, key=len, reverse=True)) + r')(?![A-Za-z])\s*_', lambda m: '{\\' + m.group(1) + '}_', t)
    t = re.sub(r'(?<!\{)\\(' + '|'.join(sorted(sup, key=len, reverse=True)) + r')(?![A-Za-z])\s*\^', lambda m: '{\\' + m.group(1) + '}^', t)
    if t != t0: f.write_text(t, encoding='ascii'); n += 1
print('files changed', n)
