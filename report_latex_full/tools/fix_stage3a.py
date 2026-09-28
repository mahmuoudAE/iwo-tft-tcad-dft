"""Stage 3 mechanical fixes: text-safe unit macros; linter follows nested inputs and skips \\ensuremath macros."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
p = (R / 'preamble.tex').read_text(encoding='ascii')
for name in ['dec', 'mVdec', 'Aum', 'cmsq', 'cmcu', 'cmVs']:
    head = '\\newcommand{\\' + name + '}{'
    i = p.find(head)
    if i < 0 or p[i + len(head):].startswith('\\ensuremath'): continue
    j = p.find('}\n', i + len(head)) if False else None
    # body runs to the matching close brace of the definition
    k = i + len(head); d = 1
    while d:
        c = p[k]; d += (c == '{') - (c == '}'); k += 1
    body = p[i + len(head):k - 1]
    p = p[:i] + head + '\\ensuremath{' + body + '}}' + p[k:]
(R / 'preamble.tex').write_text(p, encoding='ascii')

l = (R / 'tools' / 'lint_latex.py').read_text(encoding='ascii')
old = "        if re.search(r'\\\\math(rm|it|sf|bf)"
if "startswith('\\\\ensuremath')" not in l:
    l = l.replace(old, "        if body.startswith('\\\\ensuremath'): continue\n" + old, 1)
old2 = "        fs.append(p)\n    return fs"
new2 = ("        fs.append(p)\n    k = 2\n    while k < len(fs):   # follow nested \\input/\\include\n        if fs[k].exists():\n"
        "            for m in re.finditer(r'\\\\(?:input|include)\\{([^}]+)\\}', strip_comments(fs[k].read_text(encoding='ascii', errors='replace'))):\n"
        "                q = ROOT / (m.group(1) if m.group(1).endswith('.tex') else m.group(1) + '.tex')\n"
        "                if q not in fs: fs.insert(k + 1, q)\n        k += 1\n    return fs")
if 'follow nested' not in l: l = l.replace(old2, new2, 1)
(R / 'tools' / 'lint_latex.py').write_text(l, encoding='ascii')
print([ln for ln in p.splitlines() if 'ensuremath' in ln])
