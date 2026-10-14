"""Independent check of proj_atoms_final.dat (D-24 v2) against atomic_proj.xml, and an A16 accounting from the AFS
tables alone. usage: python check_tables.py <AFS tarball dir (unpacked)> <atomic_proj.xml> <n_W>
Uses numpy and a separate parser (full DOM, not the streaming code of steps_final.sh)."""
import sys
import xml.etree.ElementTree as ET

import numpy as np

d, apx, n_w = sys.argv[1], sys.argv[2], int(sys.argv[3])
pm = [l.split() for l in open(f'{d}/projwfc_map_final.dat') if not l.startswith('#')]
atom = np.array([int(p[1]) - 1 for p in pm])
isd = np.array([p[2] == 'W' and p[4] == '2' for p in pm])
nat = atom.max() + 1
W, rows = [], []   # per k: (nwfc, nbnd) |proj|^2, ordered by the ATOMIC_WFC index attribute
for ev, el in ET.iterparse(apx, events=('end',)):
    if el.tag == 'ATOMIC_WFC':
        v = np.array(el.text.split(), float)
        rows.append((int(el.get('index')), v[0::2] ** 2 + v[1::2] ** 2))
        el.clear()
    elif el.tag == 'PROJS':
        W.append(np.array([r for i, r in sorted(rows, key=lambda t: t[0])]))
        rows = []
        el.clear()
nks, (nwfc, nb) = len(W), W[0].shape
hdr, tab = [], []
for l in open(f'{d}/proj_atoms_final.dat'):
    (hdr if l.startswith('#') else tab).append(l)
tab = np.array([l.split() for l in tab], float)
watoms = [int(c[3:]) - 1 for c in hdr[-1].split() if c.startswith('d_W')]
print(f'table rows {len(tab)} (nks {nks} x nbnd {nb} = {nks * nb}); columns {tab.shape[1]} = 7 + nat {nat} + W {len(watoms)}')
worst = dict(w=0.0, compl=0.0, pr=0.0, d=0.0)
for r in tab:
    ik, n = int(r[0]) - 1, int(r[1]) - 1
    x = W[ik][:, n]
    wa = np.bincount(atom, weights=x, minlength=nat)
    dw = [x[(atom == a) & isd].sum() for a in watoms]
    t = wa.sum(); prn = t * t / (nat * (wa ** 2).sum())
    worst['w'] = max(worst['w'], np.abs(r[7:7 + nat] - wa * 1e6).max())
    worst['compl'] = max(worst['compl'], abs(r[5] - t))
    worst['pr'] = max(worst['pr'], abs(r[6] - prn))
    if watoms:
        worst['d'] = max(worst['d'], np.abs(r[7 + nat:] - np.array(dw) * 1e6).max())
print('max |table - independent|: w_i (1e-6 units) %.3f, completeness %.2e, PR_n %.2e, d_W (1e-6 units) %.3f'
      % (worst['w'], worst['compl'], worst['pr'], worst['d']))
occ = np.array([l.split() for l in open(f'{d}/occ_kw_final.dat') if not l.startswith('#')], float)
o = {(int(a), int(b)): (e, f, w) for a, b, e, f, w in occ}
print('f_nk, w_k, e identical to occ_kw_final.dat:',
      all(abs(o[(int(r[0]), int(r[1]))][1] - r[3]) < 1e-8 and abs(o[(int(r[0]), int(r[1]))][2] - r[4]) < 1e-8
          and abs(o[(int(r[0]), int(r[1]))][0] - r[2]) < 1e-5 for r in tab))
# A16 accounting from the AFS tables only (bulk test cell: one W, N_ex = n_W)
nel = float([l for l in open(f'{d}/occ_kw_final.dat') if l.startswith('# nelec')][0].split()[2])
nv = (nel - n_w) / 2
above = tab[:, 1] > nv
nex = (tab[above, 3] * tab[above, 4]).sum()
compl = tab[:, 5]
wd = tab[:, 7 + nat:].sum(axis=1) * 1e-6 if watoms else np.zeros(len(tab))
fw = tab[:, 3] * tab[:, 4]
w5d_frac = (fw[above] * wd[above] / compl[above]).sum() / n_w if n_w else float('nan')
pr = tab[:, 6]
print(f'A16 from AFS tables: N_el {nel:.0f}, N_ex {n_w}, N_v {nv:g}; occupation above N_v {nex:.4f} '
      f'(check |.-N_ex| < 0.02: {"PASS" if abs(nex - n_w) < 0.02 else "FAIL"}); W-5d fraction of the excess electrons {w5d_frac:.3f}; '
      f'excess electrons in PR_n >= 0.20 states {(fw[above] * (pr[above] >= 0.2)).sum() / n_w:.3f}; '
      f'states with completeness < 0.90 among those above N_v and occupied > 1e-3: {int(((compl < 0.9) & above & (tab[:, 3] > 1e-3)).sum())}')
