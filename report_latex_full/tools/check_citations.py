"""Stage 3: check every page citation against digest/papers/<key>.md.
For each \\citep/\\citet[p.~X]{key} (bundled papers only) take the citing sentence, extract its numbers and test
whether they occur on page X. Status: OK (all numbers on page) | PARTIAL | NOT_ON_PAGE (found elsewhere: pages) |
NO_NUMBERS (sentence has no checkable number; needs a reader) | PAGE_MISSING (cited page not in paper).
Writes tools/citation_report.csv and prints a summary."""
import csv, re
from pathlib import Path
R = Path(__file__).resolve().parents[1]
pages = {}
for f in (R / 'digest' / 'papers').glob('*.md'):
    cur = None; d = {}
    for line in f.read_text(encoding='utf-8').splitlines():
        m = re.match(r'## printed page (\S+)', line)
        if m: cur = m.group(1); d[cur] = ''; continue
        if cur: d[cur] += line + ' '
    pages[f.stem] = {k: re.sub(r'\s+', ' ', v.replace('\u2212', '-').replace('\u2009', ' ')) for k, v in d.items()}

def nums(s):
    s = re.sub(r'\\(cref|ref|label|run|file|SI|si)\{[^}]*\}', ' ', s)
    s = re.sub(r'\\citep?t?\[[^\]]*\]\{[^}]*\}', ' ', s)
    out = set()
    for m in re.finditer(r'(\d+\.\d+|\d{2,})(?:\s*\\times\s*10\^\{?-?(\d+)\}?|e[+-]?(\d+))?', s):
        v = m.group(1)
        if re.fullmatch(r'(19|20)\d\d', v): continue      # years
        out.add((v, m.group(2) or m.group(3)))
    return out

def on_page(txt, v, e):
    if e:
        return re.search(re.escape(v) + r'\s*[\u00d7x]\s*10\s*-?\s*' + e, txt) is not None or v in txt
    return re.search(r'(?<![\d.])' + re.escape(v) + r'(?![\d])', txt) is not None

rows = []
for f in sorted(list((R / 'chapters').glob('*.tex')) + list((R / 'appendices').glob('*.tex'))):
    t = f.read_text(encoding='ascii', errors='replace')
    for m in re.finditer(r'\\cite[pt]\[(pp?\.)~?([^\],]+)[^\]]*\]\{([^}]+)\}', t):
        key = m.group(3).split(',')[0].strip(); pg = m.group(2).strip()
        if key not in pages: continue
        pgs = [pg]
        rm = re.match(r'(\d+)-(\d+)-{1,2}(\d+)-(\d+)$', pg) or None
        if '--' in pg and not rm:
            a, b = pg.split('--')[:2]
            if a.isdigit() and b.isdigit(): pgs = [str(x) for x in range(int(a), int(b) + 1)]
            else: pgs = [a, b]
        s0 = max(t.rfind('.', 0, m.start() - 2), t.rfind('\n\n', 0, m.start()), m.start() - 300); sent = t[s0:m.start()] + t[m.end():m.end() + 80]
        ns = nums(sent); line = t[:m.start()].count('\n') + 1
        missing = [p for p in pgs if p not in pages[key]]
        if len(missing) == len(pgs): rows.append([f.name, line, key, pg, 'PAGE_MISSING', '', sent[-160:]]); continue
        txt = ' '.join(pages[key].get(p, '') for p in pgs)
        if not ns: rows.append([f.name, line, key, pg, 'NO_NUMBERS', '', sent[-160:]]); continue
        hit = [n for n in ns if on_page(txt, *n)]
        if len(hit) == len(ns): st, where = 'OK', ''
        else:
            miss = [n for n in ns if n not in hit]
            where = ';'.join(sorted({p for p, tx in pages[key].items() for n in miss if on_page(tx, *n)}))
            st = 'PARTIAL' if hit else ('NOT_ON_PAGE' if where else 'NUMBERS_NOT_IN_PAPER')
            where = f"missing {[n[0] for n in miss]} found on {where or 'no page'}"
        rows.append([f.name, line, key, pg, st, where, sent[-160:].replace('\n', ' ')])
with (R / 'tools' / 'citation_report.csv').open('w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['file', 'line', 'key', 'page', 'status', 'detail', 'context']); w.writerows(rows)
from collections import Counter
print(Counter(r[4] for r in rows)); print('total', len(rows))
