"""List overfull hboxes wider than a threshold with the source file they occur in (parses build/main.log)."""
import re, sys
thr = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
log = open("build/main.log", errors="replace").read()
stack, out = [], []
for tok in re.finditer(r"\((\.{0,2}/?[^\s()]+\.tex)|\)|Overfull \\hbox \(([\d.]+)pt too wide\)[^\n]*lines (\d+)--(\d+)", log):
    if tok.group(1):
        stack.append(tok.group(1))
    elif tok.group(0) == ")":
        if stack: stack.pop()
    elif tok.group(2) and float(tok.group(2)) > thr:
        out.append((stack[-1] if stack else "?", tok.group(3), float(tok.group(2))))
for f, l, w in out:
    print(f"{w:7.1f}pt  {f}:{l}")
