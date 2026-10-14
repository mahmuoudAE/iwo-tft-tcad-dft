"""Synthetic projwfc output at the size of the largest final (aIWO_2p0_Al2O3_s2: 414 atoms, In98 O246 Al60 H8 W2,
2134 atomic wavefunctions, nbnd 1928) for a timing / size test of export_tables (D-24 v2). Not physics: random
projections with a random localisation per band. usage: python3 gen_synth.py <dir> <nks>"""
import math
import os
import random
import sys

out, nks = sys.argv[1], int(sys.argv[2])
random.seed(7)
species = ['In'] * 98 + ['W'] * 2 + ['Al'] * 60 + ['O'] * 246 + ['H'] * 8
orbs = {'In': [(0, 1), (1, 3), (2, 5)], 'W': [(0, 1), (1, 3), (2, 5), (0, 1)], 'Al': [(0, 1), (1, 3)],
        'O': [(0, 1), (1, 3)], 'H': [(0, 1)]}
states = []   # (atom, species, wfc, l, m)
for a, s in enumerate(species, 1):
    for w, (l, nm) in enumerate(orbs[s], 1):
        states += [(a, s, w, l, m) for m in range(1, nm + 1)]
nat, nwfc, nbnd = len(species), len(states), 1928
nel = 98 * 13 + 2 * 14 + 60 * 3 + 246 * 6 + 8
HA = 27.211386245988
ef = 0.30
os.makedirs(f'{out}/tmp/slab.save', exist_ok=True)
eig = [sorted(-1.5 + 2.0 * random.random() for _ in range(nbnd)) for _ in range(nks)]
occ = [[1.0 / (1 + math.exp((e - ef) / 0.0025)) for e in ek] for ek in eig]
with open(f'{out}/tmp/slab.save/data-file-schema.xml', 'w') as f:
    f.write('<qes:espresso xmlns:qes="x"><input><bands><smearing degauss="0.0025">gaussian</smearing></bands></input><output>\n')
    f.write(f'<atomic_structure nat="{nat}"><atomic_positions>\n')
    f.writelines(f'<atom name="{s}" index="{i}">0.0 0.0 0.0</atom>\n' for i, s in enumerate(species, 1))
    f.write('</atomic_positions></atomic_structure>\n')
    f.write(f'<band_structure><lsda>false</lsda><nbnd>{nbnd}</nbnd><nelec>{nel}</nelec><fermi_energy>{ef}</fermi_energy>\n')
    for k in range(nks):
        f.write(f'<ks_energies><k_point weight="{2.0 / nks}">0.0 0.0 0.0</k_point><npw>150000</npw>'
                f'<eigenvalues size="{nbnd}">' + ' '.join(f'{e:.15e}' for e in eig[k]) + '</eigenvalues>'
                f'<occupations size="{nbnd}">' + ' '.join(f'{o:.15e}' for o in occ[k]) + '</occupations></ks_energies>\n')
    f.write('</band_structure></output></qes:espresso>\n')
comp = [[0.0] * nbnd for _ in range(nks)]
with open(f'{out}/tmp/slab.save/atomic_proj.xml', 'w') as f:
    f.write(f'<PROJECTIONS>\n<HEADER NUMBER_OF_BANDS="{nbnd}" NUMBER_OF_K-POINTS="{nks}" NUMBER_OF_SPIN_COMPONENTS="1" '
            f'NUMBER_OF_ATOMIC_WFC="{nwfc}"/>\n<EIGENSTATES>\n')
    for k in range(nks):
        f.write(f'<K-POINT Weight="{2.0 / nks}">0 0 0</K-POINT>\n<E>' + ' '.join(f'{e * 2:.15e}' for e in eig[k]) + '</E>\n<PROJS>\n')
        cen = [random.randrange(nat) for _ in range(nbnd)]
        ln = [10 ** random.uniform(0, 3) for _ in range(nbnd)]
        amp = []
        for i, (a, s, w, l, m) in enumerate(states):
            row = []
            for n in range(nbnd):
                env = math.exp(-abs(a - 1 - cen[n]) / ln[n])
                re, im = random.gauss(0, 1) * env, random.gauss(0, 1) * env
                row.append((re, im))
            amp.append(row)
        # normalise each band to a completeness in [0.80, 1.00]
        for n in range(nbnd):
            t = sum(amp[i][n][0] ** 2 + amp[i][n][1] ** 2 for i in range(nwfc)) or 1.0
            c = random.uniform(0.80, 1.0); comp[k][n] = c; sc = math.sqrt(c / t)
            for i in range(nwfc):
                amp[i][n] = (amp[i][n][0] * sc, amp[i][n][1] * sc)
        for i in range(nwfc):
            f.write(f'<ATOMIC_WFC index="{i + 1}" spin="1">\n' + '\n'.join(f'{x:24.15E}{y:24.15E}' for x, y in amp[i]) + '\n</ATOMIC_WFC>\n')
        f.write('</PROJS>\n')
    f.write('</EIGENSTATES>\n</PROJECTIONS>\n')
with open(f'{out}/projwfc_final.out', 'w') as f:
    f.write('     Atomic states used for projection\n')
    f.writelines(f'     state #{i:5d}: atom {a:4d} ({s:<3s}), wfc {w:2d} (l={l} m={m:2d})\n' for i, (a, s, w, l, m) in enumerate(states, 1))
    for k in range(nks):
        f.write(' k =   0.0000000000  0.0000000000  0.0000000000\n')
        for n in range(nbnd):
            f.write(f'==== e({n + 1:5d}) = {eig[k][n] * HA:11.5f} eV ==== \n     psi = 0.5*[#   1]+\n    |psi|^2 = {comp[k][n]:.3f}\n')
print('nat', nat, 'nwfc', nwfc, 'nbnd', nbnd, 'nks', nks, 'nelec', nel)
