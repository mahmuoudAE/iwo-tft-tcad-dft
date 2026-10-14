#!/usr/bin/env python3
"""Write one JSON spec per amorphous structure (wave 1, revision 2) and the HTCondor queue list ml_jobs.txt.

Rules (registered in SLAB_PROTOCOL.md before any result):
  * W / (In + W) = 2.0 % exactly in every IWO cell: 50 cations per W, each W compensated with one extra O
    (In(50n-n) W(n) O(75n+n), one extra electron per W). The In2O3 twin has the same cation count, In(50n) O(75n).
  * Smallest n_W whose in-plane edge L = sqrt(V / t) at 7.0 g/cm3 is >= 12.5 A (W image distance), so the W
    volume density is the same at every thickness. The In2O3 twin uses the same L and t (identical cell).
  * Thickness t is the mass-equivalent thickness at 7.0 g/cm3 (the box height before the cleave).
  * Vacuum 2 x 10 A before relaxation (QC needs >= 15 A after relaxation); dipole correction in DFT.
  * Interface: the film on 1 nm a-Al2O3 (3.0 g/cm3); Al2O3 is the layer touching the channel in the device stack.
  * HfO2 control (A18, D-20, hypothesis H-M): the film of aIWO_2p0_Al2O3_s2 on 1 nm a-HfO2 (9.6 g/cm3), round 4.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'specs'
OUT.mkdir(exist_ok=True)
RHO, RHO_AL2O3, L_MIN, X_W = 7.0, 3.0, 12.5, 0.02
RHO_HFO2 = 9.6   # g/cm3, ASSUMED (ALD a-HfO2 is about 9.1-9.7; H-M, A18)
M = {'In': 114.818, 'W': 183.84, 'O': 15.999, 'Al': 26.982, 'Hf': 178.49}
specs = []


def iwo(n_w):
    ncat = round(n_w / X_W)
    return ncat - n_w, n_w, round(1.5 * ncat) + n_w


def lateral(n_w, t_nm):
    n_in, _, n_o = iwo(n_w)
    vol = (n_in * M['In'] + n_w * M['W'] + n_o * M['O']) * 1.66054 / RHO
    return math.sqrt(vol / (10 * t_nm))


def n_w_for(t_nm):
    n = 1
    while lateral(n, t_nm) < L_MIN:
        n += 1
    return n


def al2o3(L, t_nm=1.0):
    fu = round(L * L * 10 * t_nm * RHO_AL2O3 / ((2 * M['Al'] + 3 * M['O']) * 1.66054))
    return dict(n_Al=2 * fu, n_O=3 * fu, thickness_A=fu * (2 * M['Al'] + 3 * M['O']) * 1.66054 / (RHO_AL2O3 * L * L))


def hfo2(L, t_nm=1.0):
    """a-HfO2 substrate of mass-equivalent thickness t_nm at RHO_HFO2 on an L x L cell (analogue of al2o3)."""
    fu = round(L * L * 10 * t_nm * RHO_HFO2 / ((M['Hf'] + 2 * M['O']) * 1.66054))
    return dict(n_Hf=fu, n_O=2 * fu, thickness_A=fu * (M['Hf'] + 2 * M['O']) * 1.66054 / (RHO_HFO2 * L * L))


def add(name, mode, comp, seed, t=None, L=None, passivate=True, substrate=None):
    s = dict(name=name, mode=mode, n_In=comp[0], n_W=comp[1], n_O=comp[2], density_gcc=RHO, seed=seed)
    if mode != 'bulk':
        s.update(thickness_nm=t, lateral_A=round(L, 4), vacuum_A=10.0, passivate=passivate)
    if substrate:
        s['substrate'] = substrate
    specs.append(s)


for t, seeds in ((2.0, (201, 202)), (1.5, (151,)), (1.0, (101,)), (0.8, (81,)), (0.7, (71,))):
    nw = n_w_for(t)
    L = lateral(nw, t)
    tag = str(t).replace('.', 'p')
    for k, seed in enumerate(seeds, 1):   # two independent samples at 2 nm (seed control, PLAN-001 review)
        add(f'aIWO_{tag}_s{k}', 'slab', iwo(nw), seed, t, L)
        add(f'aIO_{tag}_s{k}', 'slab', (50 * nw, 0, 75 * nw), seed + 10, t, L)
    if t in (2.0, 0.7):   # termination control: same seed, surfaces left bare
        add(f'aIWO_{tag}_s1_bare', 'slab', iwo(nw), seeds[0], t, L, passivate=False)
    if t in (2.0, 1.0):   # interface realism: gate-side a-Al2O3 under the film, OH-terminated back channel on top
        add(f'aIWO_{tag}_Al2O3_s1', 'interface', iwo(nw), seeds[0] + 500, t, L, substrate=al2o3(L))
# replacements for structures rejected by QC (SLAB_PROTOCOL.md 7): same recipe, next seed; queued via ml_jobs_r<round>.txt
REPLACE, ROUND = [], {}
for rnd, t, base, seed in ((1, 0.8, 'aIWO_0p8', 82), (1, 2.0, 'aIWO_2p0_Al2O3', 702), (2, 1.0, 'aIWO_1p0_Al2O3', 602)):
    ROUND.setdefault(rnd, []).append(f'{base}_s2')
    nw = n_w_for(t)
    L = lateral(nw, t)
    if 'Al2O3' in base:
        add(f'{base}_s2', 'interface', iwo(nw), seed, t, L, substrate=al2o3(L))
    else:
        add(f'{base}_s2', 'slab', iwo(nw), seed, t, L)
    REPLACE.append(f'{base}_s2')
# extra round 3 (D-15, Codex work chat 2026-10-10): fully compensated 2.0 nm IWO, In98 W2 O153 = 0 excess electrons
# (W6+ on In3+ sites fully compensated by 1.5 extra O per W); same t, L and seed as aIWO_2p0_s1 for pairing
ROUND.setdefault(3, []).append('aIWO_2p0_comp_s1')
add('aIWO_2p0_comp_s1', 'slab', (98, 2, 153), 201, 2.0, lateral(n_w_for(2.0), 2.0))
REPLACE.append('aIWO_2p0_comp_s1')
# round 4 (A18, D-20, hypothesis H-M): HfO2 interface control. Film identical to aIWO_2p0_Al2O3_s2 (In98 W2 O152,
# t = 2.0 nm, same L) on ~1 nm a-HfO2 at RHO_HFO2; SLAB_PROTOCOL.md 5 recipe unchanged; ML seed 902 (frozen in A18)
ROUND.setdefault(4, []).append('aIWO_2p0_HfO2_s1')
L_HF = lateral(n_w_for(2.0), 2.0)
add('aIWO_2p0_HfO2_s1', 'interface', iwo(n_w_for(2.0)), 902, 2.0, L_HF, substrate=hfo2(L_HF))
REPLACE.append('aIWO_2p0_HfO2_s1')
# bulk cells for the DFT force check of the ML potential (2.0 % W as in the films)
add('aIWO_bulk_s1', 'bulk', iwo(1), 901)
add('aIO_bulk_s1', 'bulk', (50, 0, 75), 911)


def sub_txt(sub):
    return (f" + Al{sub['n_Al']}O{sub['n_O']}" if 'n_Al' in sub else f" + Hf{sub['n_Hf']}O{sub['n_O']}")


for s in specs:
    (OUT / f"spec_{s['name']}.json").write_text(json.dumps(s, indent=1), newline='\n')
    extra = f" L={s['lateral_A']:.2f} A" if 'lateral_A' in s else ''
    print(f"{s['name']:22s} In{s['n_In']} W{s['n_W']} O{s['n_O']}{extra}" + (sub_txt(s['substrate']) if 'substrate' in s else ''))
(HERE / 'ml_jobs.txt').write_text(''.join(f"{s['name']}\n" for s in specs if s['name'] not in REPLACE), newline='\n')
for rnd, names in ROUND.items():
    (HERE / f'ml_jobs_r{rnd}.txt').write_text(''.join(f'{n}\n' for n in names), newline='\n')
print(len(specs), 'specs written')
