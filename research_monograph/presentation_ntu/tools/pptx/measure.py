#!/usr/bin/env python3
"""measure.py -- text placement check: for each slide of a rendered PPTX (PDF from LibreOffice), the vertical and
horizontal offset of the text against build/main.pdf, per horizontal band, in PDF points.
Usage: python3 tools/pptx/measure.py <rendered.pdf> <pdf pages, e.g. 1,2,20>"""
import sys
import numpy as np
import pymupdf
from PIL import Image

ZOOM = 6.0          # px per PDF point


def img(page, zoom):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False, colorspace=pymupdf.csGRAY)
    return 255.0 - np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width).astype(float)


def best_shift(a, b, axis, rng=24):
    pa, pb = a.sum(axis=axis), b.sum(axis=axis)
    if pa.sum() < 1e3 or pb.sum() < 1e3:
        return None
    scores = [((pa * np.roll(pb, d)).sum(), d) for d in range(-rng, rng + 1)]
    return max(scores)[1]


def main():
    rend = pymupdf.open(sys.argv[1])
    orig = pymupdf.open("build/main.pdf")
    pages = [int(p) for p in sys.argv[2].split(",")]
    worst = 0.0
    for i, p in enumerate(pages):
        o = img(orig[p - 1], ZOOM)
        rz = ZOOM * orig[p - 1].rect.width / rend[i].rect.width
        r = img(rend[i], rz)[: o.shape[0], : o.shape[1]]
        H, W = o.shape
        rows = []
        for y0 in range(0, H, H // 10):
            a, b = o[y0:y0 + H // 10], r[y0:y0 + H // 10]
            dy, dx = best_shift(a, b, 1), best_shift(a, b, 0)
            if dy is None:
                continue
            rows.append((dy / ZOOM, dx / ZOOM))
            worst = max(worst, abs(dy / ZOOM), abs(dx / ZOOM))
        print(f"p{p}: " + " ".join(f"({dy:+.1f},{dx:+.1f})" for dy, dx in rows))
    print(f"largest offset {worst:.2f} pt (dy,dx per band: render moved by -value)")


if __name__ == "__main__":
    main()
