#!/usr/bin/env python3
"""A23 (ii)/(iii): make a pw.x save directory consistent with the swapped-in PP_CHI projection copies.

usage: python3 set_natomwfc.py <prefix.save>

projwfc.x takes the number of atomic wavefunctions from data-file-schema.xml (atomic_structure num_of_atomic_wfc),
which pw.x wrote as 0 with the pristine SG15 files. This recomputes it from the UPF files now in the save
(sum over atoms of (2l+1) for every PP_CHI with occupation >= 0, the QE n_atom_wfc rule) and rewrites that one
attribute (a .orig copy of the XML is kept). Standard library only.
"""
import re
import sys
from pathlib import Path


def main():
    save = Path(sys.argv[1])
    xml = save / 'data-file-schema.xml'
    text = xml.read_text()
    m = re.search(r'<atomic_structure\b[^>]*num_of_atomic_wfc="(\d+)"', text)
    if not m:
        raise SystemExit(f'{xml}: no atomic_structure num_of_atomic_wfc attribute')
    pp = dict(re.findall(r'<species name="([^"]+)">.*?<pseudo_file>\s*([^<\s]+)\s*</pseudo_file>', text, re.S))
    atoms = re.findall(r'<atom name="([^"]+)" index="\d+"', text.split('<atomic_positions>')[1].split('</atomic_positions>')[0])
    per = {}
    for sp, f in pp.items():
        u = (save / f).read_text()
        n = 0
        for at in re.findall(r'<PP_CHI\.\d+\s([^>]*)>', u):
            l = int(re.search(r'\bl="\s*(\d+)"', at).group(1))
            oc = float(re.search(r'occupation="\s*([-0-9.eEdD+]+)"', at).group(1).replace('d', 'e').replace('D', 'e'))
            if oc >= 0:
                n += 2 * l + 1
        per[sp] = n
    total = sum(per[a] for a in atoms)
    if total == 0:
        raise SystemExit(f'no PP_CHI in the UPF files of {save}: the projection copies were not swapped in')
    (save / 'data-file-schema.xml.orig').write_text(text)
    new = text[:m.start(1)] + str(total) + text[m.end(1):]
    xml.write_text(new)
    print(f'{xml}: num_of_atomic_wfc {m.group(1)} -> {total} ({len(atoms)} atoms, per species {per})')


if __name__ == '__main__':
    main()
