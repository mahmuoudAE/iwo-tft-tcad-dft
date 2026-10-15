#!/usr/bin/env bash
# Contact sheets: 6 slides per image (3 x 2) for a quick visual check with few image reads.
# Usage: bash tools/contact_sheet.sh <png_dir>   ->  <png_dir>/sheets/sheet-NN.png
set -euo pipefail
D="$1"; mkdir -p "$D/sheets"; rm -f "$D"/sheets/*.png
mapfile -t F < <(ls "$D"/p-*.png | sort -V)
n=0; for ((i=0; i<${#F[@]}; i+=6)); do n=$((n+1))
  montage "${F[@]:i:6}" -tile 3x2 -geometry +6+6 -background '#888888' "$D/sheets/sheet-$(printf %02d $n).png"; done
echo "$n sheets in $D/sheets (slides in order, 6 per sheet)"
