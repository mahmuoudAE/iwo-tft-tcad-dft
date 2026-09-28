"""Clean full build with MiKTeX: pdflatex, bibtex, pdflatex x2; then map errors."""
import os, subprocess
from pathlib import Path
R = Path(__file__).resolve().parents[1]
p = (R / 'preamble.tex').read_text(encoding='ascii')
p = p.replace('\\newcommand{\\file}[1]{\\texttt{\\detokenize{#1}}}', '\\DeclareRobustCommand{\\file}[1]{\\texttt{\\detokenize{#1}}}')
(R / 'preamble.tex').write_text(p, encoding='ascii')
for f in list(R.glob('main.*')) + list(R.glob('chapters/*.aux')) + list(R.glob('appendices/*.aux')):
    if f.suffix in ('.aux', '.lof', '.lot', '.toc', '.bbl', '.out', '.blg'): f.unlink()
B = Path(os.environ['LOCALAPPDATA']) / 'Programs/MiKTeX/miktex/bin/x64'
run = lambda *a: subprocess.run([str(B / a[0]), *a[1:]], cwd=R, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
run('pdflatex.exe', '-interaction=nonstopmode', 'main.tex'); run('bibtex.exe', 'main')
run('pdflatex.exe', '-interaction=nonstopmode', 'main.tex'); run('pdflatex.exe', '-interaction=nonstopmode', 'main.tex')
exec((R / 'tools' / 'log_errors.py').read_text())
import re
m = re.search(r'Output written on main.pdf \((\d+) pages', (R / 'main.log').read_text(encoding='latin-1')); print('pages', m.group(1) if m else 'NO PDF')
