"""List overfull hboxes wider than a threshold with the source file they occur in (parses build/main.log).
Every "(" pushes a stack entry (the file name if a .tex path follows, else None) and every ")" pops one, so
parentheses in log messages stay balanced; the current file is the innermost named entry.
Usage: python3 -I tools/overfull.py [threshold_pt]   (run from research_monograph/)
"""
import re
import sys

thr = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
log = open("build/main.log", errors="replace").read()
stack, out = [], []
pat = re.compile(r"\((\.{0,2}/[^\s()]+\.tex)?|\)|Overfull \\hbox \(([\d.]+)pt too wide\)[^\n]*?lines (\d+)--(\d+)")
for tok in pat.finditer(log):
    g = tok.group(0)
    if g.startswith("Overfull"):
        if float(tok.group(2)) > thr:
            cur = next((s for s in reversed(stack) if s), "?")
            out.append((cur, tok.group(3), float(tok.group(2))))
    elif g == ")":
        if stack:
            stack.pop()
    else:
        stack.append(tok.group(1))
for f, l, w in out:
    print(f"{w:7.1f}pt  {f}:{l}")
