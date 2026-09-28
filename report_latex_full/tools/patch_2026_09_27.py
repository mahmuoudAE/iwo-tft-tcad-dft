"""Title page names; generator support for (a) contact overlap other than 2 um (mesh follows the contacts) and
(b) an explicit constant-mobility temperature exponent (solver.tmun); launch cap 52 -> 54."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]; P = R.parent
m = (R / 'main.tex').read_text(encoding='ascii')
m = m.replace('\\newcommand{\\reportauthor}{[Author name -- to be completed]}', '\\newcommand{\\reportauthor}{Mahmoud Elrasheedy}')
m = m.replace('\\newcommand{\\reportsupervisor}{[Supervisor -- to be completed]}', '\\newcommand{\\reportsupervisor}{Chao-Hsin Wu}')
m = m.replace('{\\normalsize Supervisor: \\reportsupervisor\\par}', '{\\normalsize Principal Investigator: \\reportsupervisor\\par}\n  \\vspace{0.2cm}\n  {\\normalsize Mentor: Mukul Kumar\\par}')
(R / 'main.tex').write_text(m, encoding='ascii')

b = (P / 'scripts' / 'build_iwo_decks.py').read_text(encoding='ascii')
old = "    for x, sp in g['mesh']['x_um']: ls.append(f'x.mesh loc={x:.10g} spac={sp * mf:.10g}')"
new = ("    xm = g['mesh']['x_um']\n"
       "    if abs(lc - 2.0) > 1e-9:   # 2026-09-27: mesh follows the contacts when the overlap differs from the 2 um default (run_0027 had a fixed 24 um mesh)\n"
       "        xm = [(0, 0.3), (lc - 0.2, 0.05), (lc, 0.01), (lc + 0.2, 0.05), (lc + 1, 0.2), (lc + L / 2, 0.7), (xr - 1, 0.2), (xr - 0.2, 0.05), (xr, 0.01), (xr + 0.2, 0.05), (xmax, 0.3)]\n"
       "    for x, sp in xm: ls.append(f'x.mesh loc={x:.10g} spac={sp * mf:.10g}')")
assert old in b; b = b.replace(old, new)
old2 = "f' taun0={p[\"tau_s\"]:.3g} taup0={p[\"tau_s\"]:.3g}' + (' egalpha=0' if abs(T_run - 300) > 1e-6 else '')"
new2 = "f' taun0={p[\"tau_s\"]:.3g} taup0={p[\"tau_s\"]:.3g}' + (' egalpha=0' if abs(T_run - 300) > 1e-6 else '') + (f' tmun={float(s[\"tmun\"]):g}' if s.get('tmun') is not None else '')"
assert old2 in b; b = b.replace(old2, new2)
(P / 'scripts' / 'build_iwo_decks.py').write_text(b, encoding='ascii')

s = (P / 'config' / 'solver.yaml').read_text(encoding='ascii')
s = s.replace('max_launches: 52 ', 'max_launches: 54 ')
s = s.replace('# raised from 30 on 2026-09-25', '# raised to 54 on 2026-09-27 (overlap redo + explicit tmun check, user-approved); earlier raised from 30 on 2026-09-25')
(P / 'config' / 'solver.yaml').write_text(s, encoding='ascii')
print('ok')
