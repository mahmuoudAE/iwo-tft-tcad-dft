#!/usr/bin/env python3
"""review_images.py -- images for checking a PowerPoint conversion slide by slide.

For a PPTX rendered to PDF by LibreOffice (bash: soffice --headless --convert-to pdf), writes per page NNN:
  <out>/pdf-NNN.png    the slide from build/main.pdf
  <out>/ppt-NNN.png    the same slide from the PowerPoint file
  <out>/diff-NNN.png   overlay: black where both have ink, RED where only the PDF has ink (missing or moved text),
                       BLUE where only the PowerPoint file has ink (extra or moved text); light grey shading = agree
All three are 1920 x 1080. Also prints, per page, the share of ink pixels that disagree.
Usage: python3 tools/pptx/review_images.py <rendered.pdf> <out_dir> [first pdf page of the rendered file, default 1]
"""
import os
import sys

import numpy as np
import pymupdf
from PIL import Image

W, H = 1920, 1080


def gray(page):
    z = W / page.rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), colorspace=pymupdf.csGRAY, alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)
    img = Image.fromarray(a).resize((W, H))
    return np.asarray(img)


def main():
    rend = pymupdf.open(sys.argv[1])
    out = sys.argv[2]
    first = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    orig = pymupdf.open(os.path.join(os.path.dirname(__file__), "..", "..", "build", "main.pdf"))
    os.makedirs(out, exist_ok=True)
    for i in range(rend.page_count):
        p = first + i
        a, b = gray(orig[p - 1]), gray(rend[i])
        Image.fromarray(a).save(f"{out}/pdf-{p:03d}.png")
        Image.fromarray(b).save(f"{out}/ppt-{p:03d}.png")
        ia, ib = a < 140, b < 140
        rgb = np.full((H, W, 3), 255, np.uint8)
        rgb[(a < 235) & (b < 235)] = (225, 225, 225)
        rgb[ia & ib] = (0, 0, 0)
        rgb[ia & ~ib] = (230, 0, 0)
        rgb[ib & ~ia] = (0, 70, 255)
        Image.fromarray(rgb).save(f"{out}/diff-{p:03d}.png")
        ink = (ia | ib).sum()
        bad = (ia ^ ib).sum()
        print(f"p{p:03d} disagree {100.0 * bad / max(ink, 1):5.1f} % of ink")


if __name__ == "__main__":
    main()
