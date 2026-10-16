#!/usr/bin/env bash
# Build one section on its own for checking: bash tools/build_section.sh 06
# Output: build/sec_06/wrapper.pdf and PNG renders build/sec_06/png/p-NN.png (one per slide).
# Prints errors, undefined citations, frame overflows (Overfull \vbox = content runs off the slide),
# overfull hboxes > 5pt and missing characters, each with the source line where available.
set -uo pipefail
cd "$(dirname "$0")/.."
N="$1"
F=$(ls sections/${N}_*.tex 2>/dev/null | head -1)
[ -n "$F" ] || { echo "no section file sections/${N}_*.tex"; exit 2; }
OUT=build/sec_$N; mkdir -p "$OUT"; rm -f "$OUT"/png/*.png
W=$OUT/wrapper.tex
sed -n '1,/\\begin{document}/p' main.tex > "$W"
printf '%s\n' "\\input{$F}" '\begin{frame}[allowframebreaks]{References (section check only)}\printbibliography[heading=none]\end{frame}' '\end{document}' >> "$W"
export max_print_line=10000
export BIBINPUTS="$OUT:.:"
run() { pdflatex -interaction=nonstopmode -output-directory="$OUT" "$W" >/dev/null 2>&1; }
run; bibtex "$OUT/wrapper" >/dev/null 2>&1; run; run
L=$OUT/wrapper.log
grep -E "^Output written" "$L" || echo "NO PDF WRITTEN"
echo "errors: $(grep -c '^!' "$L")"; grep -A3 '^!' "$L" | head -30
echo "undefined citations/refs:"; grep -E "Warning: (Citation|Reference) .* undefined|could not be found" "$L" | sort -u | head
echo "frame overflows (Overfull vbox; content does not fit the slide):"; grep -E "Overfull \\\\vbox" "$L" | head -20
echo "overfull hbox > 5pt:"; grep -E "Overfull \\\\hbox \(([5-9]|[1-9][0-9]+)\.[0-9]+pt" "$L" | head -20
echo "missing characters:"; grep "Missing character" "$L" | sort -u | head
mkdir -p "$OUT/png"; pdftoppm -r 60 -png "$OUT/wrapper.pdf" "$OUT/png/p" 2>/dev/null
echo "renders: $(ls "$OUT"/png/*.png 2>/dev/null | wc -l) PNG files in $OUT/png (the last ones are the reference list)"
