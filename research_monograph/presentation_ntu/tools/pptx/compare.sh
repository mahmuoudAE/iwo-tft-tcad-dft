#!/usr/bin/env bash
# Renders a PPTX with LibreOffice (Arial -> Liberation Sans, metric-compatible) and puts each slide next to the
# matching page of build/main.pdf: <out>/cmp-NNN.png (left: PDF, right: PowerPoint file). Usage:
#   bash tools/pptx/compare.sh <file.pptx> <out_dir> <pdf page list, e.g. 1,2,20 (the PPTX holds these pages)>
set -euo pipefail
cd "$(dirname "$0")/../.."
pptx=$1; out=$2; pages=$3
mkdir -p "$out"
soffice --headless --convert-to pdf --outdir "$out" "$pptx" >/dev/null 2>&1
rendered="$out/$(basename "${pptx%.pptx}").pdf"
pdftoppm -r 110 -png "$rendered" "$out/pp"
i=0
for p in $(echo "$pages" | tr ',' ' '); do
  i=$((i+1))
  pdftoppm -r 110 -png -f "$p" -l "$p" -singlefile build/main.pdf "$out/orig"
  pp=$(ls "$out"/pp-*.png | sort | sed -n "${i}p")
  convert "$out/orig.png" -resize 1760x990! "$out/o.png"; convert "$pp" -resize 1760x990! "$out/r.png"
  montage "$out/o.png" "$out/r.png" -tile 2x1 -geometry +6+6 -background '#888' "$out/cmp-$(printf %03d "$p").png"
done
rm -f "$out"/o.png "$out"/r.png "$out"/orig.png
echo "rendered $(ls "$out"/pp-*.png | wc -l) slides -> $out/cmp-*.png"
