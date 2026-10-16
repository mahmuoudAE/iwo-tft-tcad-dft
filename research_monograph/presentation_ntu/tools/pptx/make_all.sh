#!/usr/bin/env bash
# Full PowerPoint conversion and check. Needs build/main.pdf (bash tools/build.sh).
#   1. marked build (colour tags)            -> build_pptx/main_marked.pdf
#   2. conversion                            -> build/IWO_NTU_presentation_{editable,exact}.pptx
#   3. LibreOffice rendering of the editable -> build_pptx/check/IWO_NTU_presentation_editable.pdf
#   4. review images and width check         -> build_pptx/check/img/{pdf,ppt,diff}-NNN.png, widths.txt
set -euo pipefail
cd "$(dirname "$0")/../.."
[ build_pptx/main_marked.pdf -nt build/main.pdf ] || bash tools/pptx/build_marked.sh
python3 tools/pptx/pdf2pptx.py --report build_pptx/report.txt > /dev/null
rm -rf build_pptx/check && mkdir -p build_pptx/check
soffice --headless --convert-to pdf --outdir build_pptx/check build/IWO_NTU_presentation_editable.pptx > /dev/null 2>&1
python3 tools/pptx/review_images.py build_pptx/check/IWO_NTU_presentation_editable.pdf build_pptx/check/img > /dev/null
python3 tools/pptx/widths.py build_pptx/check/IWO_NTU_presentation_editable.pdf "$(seq -s, 1 114)" > build_pptx/check/widths.txt
tail -1 build_pptx/check/widths.txt
ls -la build/IWO_NTU_presentation_*.pptx
echo "make_all done"
