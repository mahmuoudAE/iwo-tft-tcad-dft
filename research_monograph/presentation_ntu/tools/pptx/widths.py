#!/usr/bin/env python3
"""widths.py -- line-width check: for each text line found in both build/main.pdf and a LibreOffice rendering of the
PPTX (same first 30 characters), the ratio rendered/PDF width. Usage: widths.py <rendered.pdf> <pdf pages, 1,5,9>"""
import statistics
import sys

import pymupdf


def lines(page, k=1.0):
    out = {}
    for b in page.get_text("rawdict")["blocks"]:
        for l in b.get("lines", []):
            cs = [c for s in l["spans"] for c in s["chars"]]
            t = "".join(c["c"] for c in cs).strip()
            if len(t) < 12:
                continue
            x0 = min(c["bbox"][0] for c in cs if c["c"] != " ")
            x1 = max(c["bbox"][2] for c in cs if c["c"] != " ")
            out[t[:30]] = (x1 - x0) * k, t
    return out


def main():
    rend, orig = pymupdf.open(sys.argv[1]), pymupdf.open("build/main.pdf")
    pages = [int(p) for p in sys.argv[2].split(",")]
    allr = []
    for i, pg in enumerate(pages):
        k = rend[i].rect.width / orig[pg - 1].rect.width
        a, b = lines(orig[pg - 1], k), lines(rend[i])
        rat = [(b[t][0] / a[t][0], a[t][1]) for t in a if t in b and a[t][0] > 60]
        if not rat:
            print(f"p{pg}: no common lines")
            continue
        allr += [r for r, _ in rat]
        worst = max(rat, key=lambda r: abs(r[0] - 1))
        print(f"p{pg}: {len(rat)} lines, median {statistics.median(r for r, _ in rat):.4f}, "
              f"worst {worst[0]:.4f} {worst[1][:50]!r}")
    if allr:
        print(f"all: {len(allr)} lines, median {statistics.median(allr):.4f}, "
              f"share within 1 %: {sum(abs(r - 1) < 0.01 for r in allr) / len(allr):.2f}")


if __name__ == "__main__":
    main()
