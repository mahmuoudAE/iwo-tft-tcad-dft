"""Local validation: NC (SG15 + borrowed PP_CHI) vs PAW projwfc on In31WO48 at Gamma, same geometry.
usage: python compare_chi.py <dir>   (atomic_proj_nc.xml, proj_nc2.out, atomic_proj_paw.xml, proj_paw.out)"""
import sys
sys.path.insert(0, r'C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\iwo-tft-research-private\compute\amorph\hse\tools')
import nc_readout as R

d = sys.argv[1]


def states(xml, pout):
    smap = R.state_map(pout)
    nb, nwfc, ef, ks = R.read_proj(xml)
    atoms = sorted({v[0] for v in smap.values()})
    w_idx = [i for i, (a, s, l) in smap.items() if s == 'W' and l == 2]
    out = []
    k = ks[0]
    for n in range(nb):
        per = {}
        for i, (a, s, l) in smap.items():
            per[a] = per.get(a, 0) + k['w'][i - 1][n]
        tot = sum(per.values())
        pr = 1 / (len(atoms) * sum((x / tot) ** 2 for x in per.values()))
        out.append((n + 1, k['e'][n] - ef, tot, pr, sum(k['w'][i - 1][n] for i in w_idx)))
    return ef, out


efn, nc = states(f'{d}/atomic_proj_nc.xml', f'{d}/proj_nc2.out')
efp, paw = states(f'{d}/atomic_proj_paw.xml', f'{d}/proj_paw.out')
print(f'E_F: NC {efn:.4f} eV, PAW {efp:.4f} eV')
print('  PAW n  NC n   E-EF(PAW) E-EF(NC)  |psi|2 PAW/NC   PR_n PAW/NC     W5d PAW/NC   dW5d')
dw, dpr = [], []
for n in range(345, 372):
    p = paw[n - 1]
    q = nc[n - 1 + 7]
    dw.append(q[4] - p[4]); dpr.append(q[3] - p[3])
    print(f'  {p[0]:5d} {q[0]:5d}  {p[1]:9.3f} {q[1]:9.3f}   {p[2]:6.3f} {q[2]:6.3f}   {p[3]:6.3f} {q[3]:6.3f}   {p[4]:6.3f} {q[4]:6.3f}  {q[4]-p[4]:+6.3f}')
print(f'max |dW5d| = {max(abs(x) for x in dw):.3f}, mean |dW5d| = {sum(abs(x) for x in dw)/len(dw):.3f}; '
      f'max |dPR_n| = {max(abs(x) for x in dpr):.3f}')
