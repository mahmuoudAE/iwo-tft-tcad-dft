#!/usr/bin/env python3
"""Digitise the IWO markers (red stars) of Fig. 1b of Januar et al., Small Struct. 7, e202500807 (2026), CC BY.

Reads the embedded raster of page 3 of private:sources/Januar2026_SmallStructures.pdf, finds the inward tick marks
of the left axis of panel (b) and the centroids of the red star markers, and converts them with the axis calibration.
Tick values (read from the figure): mu_max 0/15/30/45; SS 100/1000 (log), dashed line = 60; I_off 1e-14/1e-12/1e-10
(log). Pixel positions below were found by the search in this script and checked by eye on an enlarged crop.

Output: paper_fig1b_digitised.csv
Run: <venv python> digitise_fig1b.py <path to Januar2026_SmallStructures.pdf>
"""
import csv
import io
import sys
from pathlib import Path

import numpy as np
import pypdf
from PIL import Image
from scipy import ndimage

OUT = Path(__file__).resolve().parent
pdf = Path(sys.argv[1] if len(sys.argv) > 1 else OUT.parents[2] / 'sources' / 'Januar2026_SmallStructures.pdf')
img = pypdf.PdfReader(str(pdf)).pages[2].images[0]
im = np.asarray(Image.open(io.BytesIO(img.data)).convert('RGB')).astype(int)
w = im.shape[1]
sub = im[:, int(w * 0.25):int(w * 0.52)]                     # panel (b) and part of (a)
R, G, B = sub[..., 0], sub[..., 1], sub[..., 2]
dark = (R < 110) & (G < 110) & (B < 110)
red = (R > 140) & (G < 80) & (B < 80)

AXIS_COL = int(np.argmax(dark.sum(0)[250:320])) + 250         # left axis line of panel (b)
ticks = [y for y in range(60, 590) if dark[y, AXIS_COL + 3:AXIS_COL + 7].sum() >= 3]
print('axis column', AXIS_COL, 'tick rows', ticks)

# calibration (rows read from the tick list printed above; tick values from the figure)
CAL = {'mu_max_cm2Vs': ('lin', (234, 0.0), (88, 45.0), (73, 240)),
       'SS_mV_dec': ('log', (375, 100.0), (255, 1000.0), (244, 411)),
       'Ioff_A_axis_label': ('log', (558.5, 1e-14), (456, 1e-10), (414, 581))}
X_CAL = None
rows = []
for q, (kind, (ya, va), (yb, vb), (r0, r1)) in CAL.items():
    m = red.copy()
    m[:r0] = 0
    m[r1:] = 0
    m[:, :AXIS_COL + 5] = 0
    lab, n = ndimage.label(m)
    objs = sorted([(ndimage.center_of_mass(m, lab, i), int((lab == i).sum())) for i in range(1, n + 1)], key=lambda o: o[0][1])
    objs = [o for o in objs if o[1] > 25]
    for ((yc, xc), size), t in zip(objs, (2.0, 6.3, 13.2)):
        if kind == 'lin':
            v = va + (yc - ya) * (vb - va) / (yb - ya)
            dv = abs((vb - va) / (yb - ya)) * 1.5                # +-1.5 px
        else:
            lv = np.log10(va) + (yc - ya) * (np.log10(vb) - np.log10(va)) / (yb - ya)
            v = 10 ** lv
            dv = v * (10 ** (abs((np.log10(vb) - np.log10(va)) / (yb - ya)) * 1.5) - 1)
        rows.append(dict(quantity=q, film_nm=t, x_px=round(xc, 1), y_px=round(yc, 1), marker_px=size,
                         value=float(f'{v:.4g}'), pm_1p5px=float(f'{dv:.2g}')))
for r in rows:
    print(r)
# sanity: the dashed 60 mV/dec line must sit where the log calibration puts 60
dash = [y for y in range(244, 411) if dark[y, AXIS_COL + 15:AXIS_COL + 260].sum() > 40]
print('dashed-line rows', dash, 'calibration puts 60 at', 375 + (np.log10(60) - 2) * (255 - 375))
with open(OUT / 'paper_fig1b_digitised.csv', 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    wr.writeheader()
    wr.writerows(rows)
