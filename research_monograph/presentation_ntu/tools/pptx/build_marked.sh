#!/usr/bin/env bash
# Builds build_pptx/main_marked.pdf: the deck with tools/pptx/marks.tex loaded (colour tags for display math and
# small capitals). Used only by pdf2pptx.py to classify text; slides are always rendered from build/main.pdf.
set -uo pipefail
cd "$(dirname "$0")/../.."
mkdir -p build_pptx
export max_print_line=10000
export BIBINPUTS="build_pptx:.:"
sed 's|^\\usepackage{appendixnumberbeamer}|\\usepackage{appendixnumberbeamer}\\input{tools/pptx/marks.tex}|' main.tex > build_pptx/main_marked.tex
grep -q 'tools/pptx/marks.tex' build_pptx/main_marked.tex || { echo "marks not inserted"; exit 1; }
run() { pdflatex -interaction=nonstopmode -output-directory=build_pptx build_pptx/main_marked.tex >/dev/null 2>&1; }
run; bibtex build_pptx/main_marked >/dev/null 2>&1; run; run
grep -E "^Output written" build_pptx/main_marked.log
echo "errors: $(grep -c '^!' build_pptx/main_marked.log)"
