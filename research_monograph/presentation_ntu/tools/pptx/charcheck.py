#!/usr/bin/env python3
"""charcheck.py -- character-level check of the editable PPTX against build/main.pdf.

Every character that pdf2pptx.py puts in a text box must appear in the LibreOffice rendering of the PPTX, at the
same place. For each page: the number of such characters, how many were found (same character within 4 pt), and
the offsets of the found ones (median and largest |dx|, |dy|, in PDF points). Missing characters are listed.
Usage: python3 tools/pptx/charcheck.py <rendered.pdf> [first pdf page of the rendered file, default 1]
"""
import os
import statistics
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdf2pptx as P  # noqa: E402

EQUIV = {"∗": "*"}


def rendered_chars(page, k):
    out = []
    for b in page.get_text("rawdict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                for c in s["chars"]:
                    if c["c"] != " ":
                        out.append([c["c"], c["origin"][0] / k, c["origin"][1] / k, False])
    return out


def main():
    rend = pymupdf.open(sys.argv[1])
    first = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    real, marked = pymupdf.open(P.REAL_PDF), pymupdf.open(P.MARKED_PDF)
    tot_exp = tot_found = 0
    worst = []
    for i in range(rend.page_count):
        pno = first - 1 + i
        page = real[pno]
        chars = P.page_chars(page, marked[pno])
        regions, _ = P.picture_regions(real, page, chars)
        want = [c for c in chars if c.u != " " and not c.lig and   # a ligature's second letter has no PDF position
                not any(r.contains(pymupdf.Point(c.cx, c.cy)) for r in regions)]
        k = rend[i].rect.width / page.rect.width
        got = rendered_chars(rend[i], k)
        dxs, dys, missing = [], [], []
        for c in want:
            u = EQUIV.get(c.u, c.u)
            if c.cls == "sc":
                u = u.upper()                   # small capitals come out as capitals in the rendered PDF
            best = None
            for g in got:
                if g[3] or g[0] != u:
                    continue
                d = abs(g[1] - c.x0) + abs(g[2] - c.y)
                if d < 4 and (best is None or d < best[0]):
                    best = (d, g)
            if best is None:
                missing.append(c)
                continue
            best[1][3] = True
            dxs.append(best[1][1] - c.x0)
            dys.append(best[1][2] - c.y)
            if os.environ.get("CHARCHECK_VERBOSE") and abs(dxs[-1]) > 1.0:
                print(f"   p{pno + 1} {c.u!r} x={c.x0:.1f} y={c.y:.1f} dx={dxs[-1]:+.2f} font={c.font} cls={c.cls}")
        tot_exp += len(want)
        tot_found += len(want) - len(missing)
        if dxs:
            mdx = max(abs(v) for v in dxs)
            mdy = max(abs(v) for v in dys)
            line = (f"p{pno + 1:03d}: {len(want) - len(missing)}/{len(want)} found; |dx| median "
                    f"{statistics.median(abs(v) for v in dxs):.2f} max {mdx:.2f}; |dy| median "
                    f"{statistics.median(abs(v) for v in dys):.2f} max {mdy:.2f}")
            worst.append((max(mdx, mdy), pno + 1))
        else:
            line = f"p{pno + 1:03d}: {len(want)} expected, none found"
        if missing:
            line += "; MISSING: " + "".join(c.u for c in missing[:60])
        print(line)
    print(f"total: {tot_found}/{tot_exp} characters found")
    worst.sort(reverse=True)
    print("largest offsets (pt, page):", ", ".join(f"{w:.2f} p{p}" for w, p in worst[:10]))


if __name__ == "__main__":
    main()
