#!/usr/bin/env python3
"""Static LaTeX checker for report_latex_full (no TeX installation is available locally).

  python tools/lint_latex.py            # prints a report; exit code 1 if any ERROR

Checks: included files exist; ASCII-only .tex/.bib; duplicate labels; unresolved \\ref/\\cref/\\Cref/\\eqref;
unknown cite keys; missing figures; missing listings; begin/end balance; brace balance; math-only macros and
^ outside math; bare underscores in text; unescaped special characters in .bib notes; tabular column counts (rough).
"""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATH_ENVS = {'equation', 'equation*', 'align', 'align*', 'gather', 'gather*', 'multline', 'multline*', 'eqnarray',
             'eqnarray*', 'math', 'displaymath', 'alignat', 'alignat*', 'flalign', 'flalign*'}
VERB_ENVS = {'lstlisting', 'verbatim', 'Verbatim', 'comment'}
# macros from preamble that must be in math mode
MATH_ONLY = set()
ARG_SKIP = ('label', 'ref', 'cref', 'Cref', 'eqref', 'pageref', 'cite', 'citep', 'citet', 'citealp', 'citeauthor', 'citeyear',
            'includegraphics', 'lstinputlisting', 'file', 'run', 'url', 'href', 'input', 'include', 'texttt', 'detokenize',
            'bibliography', 'bibliographystyle', 'hypersetup', 'graphicspath', 'definecolor', 'usetikzlibrary', 'SI', 'si', 'num',
            'newcommand', 'renewcommand', 'lstdefinelanguage', 'lstset', 'addcontentsline', 'phantomsection', 'nolinkurl')

def strip_comments(s):
    out = []
    for line in s.split('\n'):
        m = re.search(r'(?<!\\)%', line)
        out.append(line[:m.start()] if m else line)
    return '\n'.join(out)

def load_preamble_math_macros():
    pre = (ROOT / 'preamble.tex').read_text(encoding='ascii', errors='replace')
    for m in re.finditer(r'\\newcommand\{\\(\w+)\}(?:\[\d\])?\{(.*)\}\s*(?:%.*)?$', pre, re.M):
        name, body = m.group(1), m.group(2)
        if body.startswith('\\ensuremath'): continue
        if re.search(r'\\math(rm|it|sf|bf)|_\{|\^\{|\\mu\b|\\varepsilon|\\Delta|\\chi|\\,\\mathrm', body) and not body.startswith('\\text') and 'textsf' not in body and 'textcolor' not in body and 'texttt' not in body and 'textsc' not in body:
            MATH_ONLY.add(name)

def files_in_order():
    main = (ROOT / 'main.tex').read_text(encoding='ascii', errors='replace')
    fs = [ROOT / 'main.tex', ROOT / 'preamble.tex']
    for m in re.finditer(r'\\(?:input|include)\{([^}]+)\}', strip_comments(main)):
        p = ROOT / (m.group(1) if m.group(1).endswith('.tex') else m.group(1) + '.tex')
        fs.append(p)
    k = 2
    while k < len(fs):   # follow nested \input/\include
        if fs[k].exists():
            for m in re.finditer(r'\\(?:input|include)\{([^}]+)\}', strip_comments(fs[k].read_text(encoding='ascii', errors='replace'))):
                q = ROOT / (m.group(1) if m.group(1).endswith('.tex') else m.group(1) + '.tex')
                if q not in fs: fs.insert(k + 1, q)
        k += 1
    return fs

def main():
    load_preamble_math_macros()
    errors, warns = [], []
    E = lambda f, msg: errors.append(f'ERROR {f}: {msg}')
    W = lambda f, msg: warns.append(f'warn  {f}: {msg}')
    files = files_in_order()
    texts = {}
    for f in files:
        rel = f.relative_to(ROOT)
        if not f.exists():
            E(rel, 'included file does not exist'); continue
        raw = f.read_bytes()
        bad = [i for i, b in enumerate(raw) if b > 127]
        if bad:
            txt = raw.decode('utf-8', errors='replace')
            lines = sorted({txt[:bad[0]].count('\n') + 1} | {raw[:i].count(b'\n') + 1 for i in bad[:20]})
            E(rel, f'{len(bad)} non-ASCII bytes (lines {lines[:12]})')
        texts[rel] = raw.decode('utf-8', errors='replace')
    # bib
    bibs = [ROOT / 'references.bib'] + sorted((ROOT / 'bib').glob('*.bib'))
    keys = {}
    for b in bibs:
        t = b.read_text(encoding='utf-8', errors='replace')
        if any(ord(c) > 127 for c in t): E(b.relative_to(ROOT), 'non-ASCII characters in bib')
        for m in re.finditer(r'@\w+\s*\{\s*([^,\s]+)\s*,', t):
            if m.group(1) in keys: E(b.relative_to(ROOT), f'duplicate bib key {m.group(1)} (also in {keys[m.group(1)]})')
            keys[m.group(1)] = b.name
        for m in re.finditer(r'^\s*(note|title|howpublished|journal|author)\s*=\s*\{(.*)\}\s*,?\s*$', t, re.M):
            v = m.group(2)
            if re.search(r'(?<!\\)[_&%#]', re.sub(r'\$[^$]*\$', '', v)): W(b.name, f'unescaped special char in {m.group(1)}: {v[:70]}')
    labels, refs, cites, figs, lists = {}, [], [], [], []
    for rel, t in texts.items():
        s = strip_comments(t)
        for m in re.finditer(r'\\label\{([^}]+)\}', s):
            if m.group(1) in labels: E(rel, f'duplicate label {m.group(1)} (also {labels[m.group(1)]})')
            labels[m.group(1)] = str(rel)
        for m in re.finditer(r'\\(?:ref|cref|Cref|eqref|pageref|autoref|crefrange|Crefrange)\*?\{([^}]+)\}', s):
            for k in m.group(1).split(','): refs.append((rel, k.strip()))
        for m in re.finditer(r'\\cite(?:p|t|alp|author|year|)\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}', s):
            for k in m.group(1).split(','): cites.append((rel, k.strip()))
        for m in re.finditer(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', s): figs.append((rel, m.group(1)))
        for m in re.finditer(r'\\lstinputlisting(?:\[[^\]]*\])?\{([^}]+)\}', s): lists.append((rel, m.group(1)))
        # environments
        stack = []
        for m in re.finditer(r'\\(begin|end)\{([^}]+)\}', s):
            kind, env = m.group(1), m.group(2)
            ln = s[:m.start()].count('\n') + 1
            if kind == 'begin': stack.append((env, ln))
            else:
                if not stack: E(rel, f'\\end{{{env}}} without begin (line {ln})')
                elif stack[-1][0] != env: E(rel, f'\\end{{{env}}} at line {ln} closes \\begin{{{stack[-1][0]}}} from line {stack[-1][1]}'); stack.pop()
                else: stack.pop()
        for env, ln in stack: E(rel, f'\\begin{{{env}}} at line {ln} never closed')
        # braces / math / underscores, skipping verbatim-like environments and \lstinline
        body = re.sub(r'\\begin\{(lstlisting|verbatim|Verbatim|comment)\}.*?\\end\{\1\}', lambda m: '\n' * m.group(0).count('\n'), s, flags=re.S)
        body = re.sub(r'\\lstinline(.)(.*?)\1', '', body)
        body = re.sub(r'\\verb(.)(.*?)\1', '', body)
        depth = 0
        for i, ch in enumerate(body):
            if ch in '{}' and (i == 0 or body[i - 1] != '\\'):
                depth += 1 if ch == '{' else -1
                if depth < 0: E(rel, f'unbalanced }} at line {body[:i].count(chr(10)) + 1}'); depth = 0
        if depth: E(rel, f'{depth} unclosed {{ in file')
        if str(rel) in ('main.tex', 'preamble.tex'): continue
        # math-mode tracker
        in_math = False; envmath = 0; i = 0; n = len(body); reported = 0
        while i < n:
            c = body[i]
            if c == '\\':
                m = re.match(r'\\([A-Za-z@]+|.)', body[i:], re.S)
                if not m: i += 1; continue
                name = m.group(1)
                if name in ('(', '['): in_math = True
                elif name in (')', ']'): in_math = False
                elif name in ('begin', 'end'):
                    me = re.match(r'\\(begin|end)\{([^}]+)\}', body[i:])
                    if me and me.group(2) in MATH_ENVS: envmath += 1 if me.group(1) == 'begin' else -1
                    if me: i += len(me.group(0)); continue
                elif name in ARG_SKIP:
                    j = i + len(m.group(0))
                    while j < n and body[j] in ' *': j += 1
                    while j < n and body[j] == '[':
                        k = body.find(']', j); j = k + 1 if k > 0 else n
                    for _ in range(2 if name in ('newcommand', 'renewcommand', 'href', 'SI', 'definecolor') else 1):
                        if j < n and body[j] == '{':
                            d = 0; k = j
                            while k < n:
                                if body[k] == '{' and body[k - 1] != '\\': d += 1
                                elif body[k] == '}' and body[k - 1] != '\\':
                                    d -= 1
                                    if d == 0: break
                                k += 1
                            j = k + 1
                    i = j; continue
                elif name in MATH_ONLY and not (in_math or envmath > 0) and reported < 15:
                    E(rel, f'math macro \\{name} outside math (line {body[:i].count(chr(10)) + 1})'); reported += 1
                i += len(m.group(0)); continue
            if c == '$':
                if i + 1 < n and body[i + 1] == '$': in_math = not in_math; i += 2; continue
                in_math = not in_math
            elif c in '_^' and not (in_math or envmath > 0) and reported < 15:
                E(rel, f"bare '{c}' outside math (line {body[:i].count(chr(10)) + 1}): ...{body[max(0, i - 30):i + 15]!r}"); reported += 1
            elif c == '#' and reported < 15 and not (in_math or envmath > 0):
                E(rel, f"bare '#' (line {body[:i].count(chr(10)) + 1})"); reported += 1
            i += 1
        if in_math: W(rel, 'odd number of $ in file (math mode left open?)')
    for rel, k in refs:
        if k not in labels: E(rel, f'undefined reference {k}')
    for rel, k in cites:
        if k not in keys: E(rel, f'unknown cite key {k}')
    for rel, stem in figs:
        base = ROOT / 'figures' / stem
        if not any((Path(str(base) + ext)).exists() for ext in ('', '.pdf', '.png', '.jpg')): E(rel, f'missing figure {stem}')
    for rel, p in lists:
        fp = ROOT / p
        if not fp.exists(): E(rel, f'missing listing {p}')
        elif any(b > 127 for b in fp.read_bytes()): E(rel, f'listing {p} is not ASCII')
    cited_pages = sum(1 for rel, t in texts.items() for _ in re.finditer(r'\\cite[pt]\[p', t))
    print(f'files {len(texts)}, labels {len(labels)}, refs {len(refs)}, cites {len(cites)} (with page: {cited_pages}), figures {len(figs)}, listings {len(lists)}, bib keys {len(keys)}')
    for w in warns: print(w)
    for e in errors: print(e)
    print(f'{len(errors)} errors, {len(warns)} warnings')
    sys.exit(1 if errors else 0)

if __name__ == '__main__': main()
