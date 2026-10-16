#!/usr/bin/env bash
# Full build of the presentation into build/main.pdf (build/ is git-ignored). Run from anywhere.
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
export max_print_line=10000
export BIBINPUTS="build:.:"
run() { pdflatex -interaction=nonstopmode -output-directory=build main.tex >/dev/null 2>&1; }
run; bibtex build/main >/dev/null 2>&1; run; run
grep -E "^Output written" build/main.log
echo "errors: $(grep -c '^!' build/main.log)"
grep -A2 '^!' build/main.log | head -20
echo "undefined citations/refs:"; grep -E "Warning: (Citation|Reference) .* undefined|could not be found" build/main.log | sort -u | head -20
echo "frame overflows (Overfull vbox):"; grep -c "Overfull \\\\vbox" build/main.log
echo "overfull hbox > 5pt:"; grep -E "Overfull \\\\hbox \(([5-9]|[1-9][0-9]+)\.[0-9]+pt" build/main.log | wc -l
echo "missing characters:"; grep -c "Missing character" build/main.log
