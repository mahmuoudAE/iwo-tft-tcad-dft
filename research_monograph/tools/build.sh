#!/bin/sh
# Build the monograph into build/ (nothing is written into report_latex_full/). Run from research_monograph/.
set -e
cd "$(dirname "$0")/.."
python3 -I tools/check_baseline.py check
mkdir -p build
pdflatex -interaction=nonstopmode -output-directory=build main > build/pass1.txt 2>&1 || true
# bibtex runs in build/ but must find the .bib files relative to research_monograph/
BIBINPUTS=".:..:$BIBINPUTS" bibtex build/main > build/bibtex.txt 2>&1 || true
pdflatex -interaction=nonstopmode -output-directory=build main > build/pass2.txt 2>&1 || true
pdflatex -interaction=nonstopmode -output-directory=build main > build/pass3.txt 2>&1 || true
grep -E "Output written" build/pass3.txt || echo "NO PDF"
echo "errors: $(grep -c '^! ' build/main.log)"; grep -E '^! ' build/main.log | sort | uniq -c | head -20
echo "undefined refs/cites:"; grep -E "(Reference|Citation) .* undefined" build/main.log | sed -E "s/.*(Reference|Citation) \`([^']+)'.*/\1 \2/" | sort -u | head -40
echo "multiply defined:"; grep -E "multiply defined" build/main.log | sort -u | head -20
echo "bibtex warnings:"; grep -c -i warning build/bibtex.txt
