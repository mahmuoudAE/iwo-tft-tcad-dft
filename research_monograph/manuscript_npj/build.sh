#!/usr/bin/env bash
# Build the npj manuscript framework into build/ (git-ignored). Run from anywhere.
set -euo pipefail
cd "$(dirname "$0")"
python3 -I check_manuscript.py
mkdir -p build
export max_print_line=10000
export BIBINPUTS=".:..:../..:"
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex >/dev/null || true
bibtex build/main >/dev/null || true
pdflatex -interaction=nonstopmode -output-directory=build main.tex >/dev/null || true
pdflatex -interaction=nonstopmode -output-directory=build main.tex >/dev/null || true
grep -E "^Output written" build/main.log || true
echo "errors: $(grep -c '^!' build/main.log || true)"
echo "undefined refs/cites:"; grep -E "Warning: (Reference|Citation) .* undefined" build/main.log | sort -u || true
echo "bibtex warnings:"; grep -c "^Warning" build/main.blg || true
