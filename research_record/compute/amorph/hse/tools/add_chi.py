#!/usr/bin/env python3
"""A23 (ii)/(iii): projection copies of the SG15 ONCV pseudopotentials (standard library only).

usage: python3 add_chi.py <sg15.upf> <paw.UPF> <out.upf> [--labels 5S,5P,5D]

Why: the SG15 ONCV files used for the 2026-10-01 HSE check (In/O/W_ONCV_PBE-1.2.upf) carry no pseudo-atomic
wavefunctions (header number_of_wfc="0", empty <PP_PSWFC>), so projwfc.x has nothing to project on.
What: writes a copy of <sg15.upf> whose <PP_PSWFC> holds the PP_CHI functions (r*chi(r)) of the pslibrary PAW set
of the same element (the set used for every PAW-PBE projwfc in this project), interpolated (4-point Lagrange in
ln r) from the PAW log mesh onto the SG15 linear mesh, and number_of_wfc set accordingly. Nothing else changes:
mesh, local part, projectors and D_ij are copied byte for byte. pw.x is NOT run with these copies; the job swaps
them into the save directory only for projwfc.x (the projection basis), see steps_nc.sh.
Prints per orbital the norm kept inside the SG15 mesh (it ends at ~6 bohr; Loewdin orthonormalisation in projwfc
renormalises the truncated functions).
"""
import hashlib
import math
import re
import sys


def floats(block):
    return [float(x) for x in block.split()]


def get_block(text, tag):
    m = re.search(r'<%s(\s[^>]*)?>(.*?)</%s>' % (re.escape(tag), re.escape(tag)), text, re.S)
    if not m:
        raise SystemExit(f'no <{tag}> block')
    return m.group(1) or '', m.group(2)


def attrs(s):
    return dict(re.findall(r'(\w+)="([^"]*)"', s))


def lagrange_logr(r_src, f_src, r):
    """4-point Lagrange interpolation of f(r) in x = ln r on a monotonic log mesh."""
    if r <= 0.0:
        return 0.0
    if r <= r_src[0]:
        return f_src[0] * r / r_src[0]          # r*chi ~ r^(l+1) -> 0; tiny region, linear is enough
    lo, hi = 0, len(r_src) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if r_src[mid] <= r:
            lo = mid
        else:
            hi = mid
    i0 = min(max(lo - 1, 0), len(r_src) - 4)
    xs = [math.log(r_src[i0 + k]) for k in range(4)]
    ys = [f_src[i0 + k] for k in range(4)]
    x = math.log(r)
    out = 0.0
    for a in range(4):
        w = 1.0
        for b in range(4):
            if b != a:
                w *= (x - xs[b]) / (xs[a] - xs[b])
        out += w * ys[a]
    return out


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    sg15_f, paw_f, out_f = sys.argv[1:4]
    want = None
    if '--labels' in sys.argv:
        want = sys.argv[sys.argv.index('--labels') + 1].upper().split(',')
    sg = open(sg15_f).read()
    paw = open(paw_f).read()
    hdr_sg = attrs(re.search(r'<PP_HEADER(.*?)/>', sg, re.S).group(1))
    hdr_paw = attrs(re.search(r'<PP_HEADER(.*?)/>', paw, re.S).group(1))
    el_sg, el_paw = hdr_sg['element'].strip(), hdr_paw['element'].strip()
    if el_sg != el_paw:
        raise SystemExit(f'element mismatch {el_sg} vs {el_paw}')
    if int(hdr_sg['number_of_wfc'].strip()) != 0:
        raise SystemExit(f'{sg15_f} already has {hdr_sg["number_of_wfc"]} wavefunctions')
    r_sg = floats(get_block(sg, 'PP_R')[1])
    dx = r_sg[2] - r_sg[1]
    r_paw = floats(get_block(paw, 'PP_R')[1])
    if r_sg[0] != 0.0 or any(abs((r_sg[i + 1] - r_sg[i]) - dx) > 1e-6 for i in range(len(r_sg) - 1)):
        raise SystemExit('SG15 mesh is not the expected linear mesh starting at r = 0')
    pswfc = re.search(r'<PP_PSWFC>(.*?)</PP_PSWFC>', paw, re.S).group(1)
    chis = re.findall(r'<(PP_CHI\.\d+)(\s[^>]*)>(.*?)</\1>', pswfc, re.S)
    blocks, report = [], []
    n = 0
    for tag, at, body in chis:
        a = attrs(at)
        if want and a['label'].upper() not in want:
            continue
        f = floats(body)
        if len(f) != len(r_paw):
            raise SystemExit(f'{tag}: {len(f)} values for a {len(r_paw)}-point mesh')
        g = [lagrange_logr(r_paw, f, r) for r in r_sg]
        # norms: full PAW mesh (trapezoid on the log mesh) vs kept inside the SG15 mesh
        full = sum(0.5 * (f[i] ** 2 + f[i + 1] ** 2) * (r_paw[i + 1] - r_paw[i]) for i in range(len(f) - 1))
        kept = sum(0.5 * (g[i] ** 2 + g[i + 1] ** 2) * dx for i in range(len(g) - 1))
        n += 1
        keep = ['label', 'l', 'occupation', 'n', 'pseudo_energy', 'cutoff_radius', 'ultrasoft_cutoff_radius']
        attr_s = ' '.join(f'{k}="{a[k]}"' for k in keep if k in a)
        vals = '\n'.join('  ' + ' '.join('%20.12E' % v for v in g[i:i + 4]) for i in range(0, len(g), 4))
        blocks.append(f'   <PP_CHI.{n} type="real" size="{len(g):5d}" columns="4" index="{n}" {attr_s}>\n'
                      f'{vals}\n   </PP_CHI.{n}>')
        report.append(f'{a["label"]}(l={a["l"]}): norm full-mesh {full:.4f}, inside r<={r_sg[-1]:.2f} bohr {kept:.4f} '
                      f'({100 * kept / full:.1f} %)')
    if n == 0:
        raise SystemExit('no PP_CHI selected')
    md5 = hashlib.md5(paw.encode()).hexdigest()
    new = re.sub(r'<PP_PSWFC>\s*</PP_PSWFC>', '<PP_PSWFC>\n' + '\n'.join(blocks) + '\n </PP_PSWFC>', sg, count=1)
    if new == sg:
        raise SystemExit('empty <PP_PSWFC> block not found')
    new = re.sub(r'number_of_wfc="\s*0"', f'number_of_wfc="{n:4d}"', new, count=1)
    note = (f'    A23 projection copy (not used by pw.x): PP_PSWFC = {n} PP_CHI from {paw_f.split("/")[-1]} '
            f'(md5 {md5}), interpolated onto this mesh by add_chi.py; original SG15 md5 '
            f'{hashlib.md5(sg.encode()).hexdigest()}\n  </PP_INFO>')
    new = new.replace('  </PP_INFO>', note, 1)
    open(out_f, 'w').write(new)
    print(f'{out_f}: {el_sg}, {n} PP_CHI; ' + '; '.join(report))


if __name__ == '__main__':
    main()
