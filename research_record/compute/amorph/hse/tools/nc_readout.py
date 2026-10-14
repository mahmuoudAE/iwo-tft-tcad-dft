#!/usr/bin/env python3
"""A23 (ii)/(iii) read-out from projwfc (standard library only).

usage: python3 nc_readout.py --proj atomic_proj_<tag>.xml --pout projwfc_<tag>.out --nv N_v [--json out.json]
                             [--window-lo 3] [--window-hi 15]
                             [--xml data-file-schema_<tag>.xml --name CELL [--certificate CERT] [--nex N_ex]
                              [--hn-json out_hn.json]]

Per state (k, n): Loewdin weights from atomic_proj.xml (|<phi_i^Loewdin|psi_nk>|^2, the projwfc.x definition), grouped by
atom with the state map printed by projwfc.x ("state # i: atom j (X), wfc m (l=..)").
  W-5d weight  = sum over W atoms, l = 2 (register section 1: the Loewdin projection; raw, not renormalised)
  PR_n         = 1 / (N * sum_i p_i^2), p_i = atom weight / total projected weight, N = all atoms (A16 atom domain)
Register section 1 / A16 edges (bulk cell: interior = all atoms, so the interior-weight condition always holds):
  host conduction edge E_c = lowest eigenvalue over all k of a state with band index > N_v and PR_n >= 0.20;
                             unresolved if none within 1.0 eV above the lowest state above N_v
  host valence edge    E_v = highest eigenvalue over all k of a state with band index <= N_v and PR_n >= 0.20
A23 (ii): E(lowest state with W-5d >= 0.30 above N_v) - E_c.   A23 (iii): host-edge gap E_c - E_v.
Completeness (register section 1): the E_v, E_c and W-5d states are flagged when |psi|^2 < 0.90; JSON
'rests_on_flagged_state' = true means the read-out is unresolved.
Spin (A27 C6/C5): nspin = 2 projections are accepted. Every (spin, k, band) is a state; N_v applies to each channel;
the edges and the W-5d search run over both channels; states carry 's' (1 up, 2 down) only when nspin = 2, so the
nspin = 1 output is unchanged.
H-N accounting (A27 C5: "nc_readout.py must be extended for spin and H-N accounting"): with --xml (the run's
data-file-schema.xml) and --nex, the frozen read-out package compute/amorph/analysis (numpy) is called on the same
files: section-1 occupations with the run's own smearing function and spin-correct k-weights, the N_v/N_ex accounting
check, f_ext, f_locW, f_W5d, Delta_W with band coverage, the H-N class with its unresolved checks; written to
--hn-json. Without --xml the stdlib read-out above is unchanged.
LEGACY ADAPTER (rc2): the stdlib read-out above (raw W-5d, band-index domain, no interior rule) is the A23 legacy adapter;
its output is labelled 'primary': false and is NON-PRIMARY for C5. Only the --xml package result (a 'cell/2' record with
its run certificate, --certificate) is accepted by compare.c5. Without a certificate the package result is unqualified
(every primary score UNRESOLVED); --nex is an unverified override for reference cells such as crystalline In31WO48.
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET

RY = 13.605693123


def state_map(pout):
    m = re.findall(r'state #\s*(\d+):\s*atom\s+(\d+)\s*\(\s*(\w+)\s*\)\s*,\s*wfc\s+(\d+)\s*\(l=\s*(\d+)',
                   open(pout, errors='replace').read())
    if not m:
        raise SystemExit(f'{pout}: no "state #" lines (projwfc.x output?)')
    return {int(i): (int(a), s, int(l)) for i, a, s, w, l in m}


def read_proj(path):
    root = ET.parse(path).getroot()
    h = root.find('HEADER')
    nb, nk = int(h.get('NUMBER_OF_BANDS')), int(h.get('NUMBER_OF_K-POINTS'))
    nwfc = int(h.get('NUMBER_OF_ATOMIC_WFC'))
    ef = float(h.get('FERMI_ENERGY')) * RY if h.get('FERMI_ENERGY') else None
    nspin = int(h.get('NUMBER_OF_SPIN_COMPONENTS', '1'))
    if nspin not in (1, 2):
        raise SystemExit(f'{path}: NUMBER_OF_SPIN_COMPONENTS {nspin} not handled (noncollinear?)')
    ks = []
    eig = root.find('EIGENSTATES')
    kp, e = None, None
    for el in eig:
        if el.tag == 'K-POINT':
            kp = (float(el.get('Weight')), [float(x) for x in el.text.split()])
        elif el.tag == 'E':
            e = [float(x) * RY for x in el.text.split()]
        elif el.tag == 'PROJS':
            w, sp = [], set()
            for aw in el.findall('ATOMIC_WFC'):
                v = [float(x) for x in aw.text.split()]
                w.append([v[2 * n] ** 2 + v[2 * n + 1] ** 2 for n in range(nb)])
                if aw.get('spin') is not None:
                    sp.add(int(aw.get('spin')))
            if len(w) != nwfc or len(e) != nb or len(sp) > 1:
                raise SystemExit(f'{path}: inconsistent block ({len(w)} wfc, {len(e)} bands, spin {sorted(sp)})')
            ks.append({'weight': kp[0], 'xk': kp[1], 'e': e, 'w': w, 'spin': sp.pop() if sp else None})
    if nspin == 2:
        # channel of each block: the ATOMIC_WFC 'spin' attribute, else QE order (all up k, then all down k)
        if len(ks) % 2:
            raise SystemExit(f'{path}: odd number of k blocks ({len(ks)}) in a spin-polarised file')
        for j, k in enumerate(ks):
            if k['spin'] is None:
                k['spin'] = 1 if j < len(ks) // 2 else 2
        nper = [sum(1 for k in ks if k['spin'] == s) for s in (1, 2)]
        if nper[0] != nper[1] or nk not in (nper[0], len(ks)):
            raise SystemExit(f'{path}: {nper} k blocks per spin channel, header says {nk} k-points')
    elif len(ks) != nk:
        raise SystemExit(f'{path}: {len(ks)} k-points read, header says {nk}')
    count = {}
    for k in ks:
        s = k['spin'] or 1
        count[s] = count.get(s, 0) + 1
        k['spin'], k['ik'] = s, count[s]
    return nb, nwfc, ef, ks, nspin


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--proj', required=True)
    ap.add_argument('--pout', required=True)
    ap.add_argument('--nv', type=int, required=True)
    ap.add_argument('--json')
    ap.add_argument('--window-lo', type=int, default=3)
    ap.add_argument('--window-hi', type=int, default=15)
    ap.add_argument('--xml', help="the run's data-file-schema.xml: adds the H-N accounting (needs --nex)")
    ap.add_argument('--nex', type=int, help='nominal excess electrons N_ex (register section 1)')
    ap.add_argument('--name', help='cell name for the H-N read-out')
    ap.add_argument('--hn-json', help='JSON output of the H-N read-out')
    ap.add_argument('--certificate', help='run certificate (JSON) for the --xml package read-out')
    a = ap.parse_args()
    if a.xml and a.nex is None and a.certificate is None:
        ap.error('--xml needs --certificate (manifest N_ex) or --nex (unverified override, e.g. 3 for In31WO48)')
    smap = state_map(a.pout)
    nb, nwfc, ef, ks, nspin = read_proj(a.proj)
    if len(smap) != nwfc:
        raise SystemExit(f'state map {len(smap)} != {nwfc} atomic wavefunctions')
    atoms = sorted({v[0] for v in smap.values()})
    species = {v[0]: v[1] for v in smap.values()}
    natom = len(atoms)
    w_idx = [i for i, (at, s, l) in smap.items() if s == 'W' and l == 2]
    states = []
    for k in ks:
        for n in range(nb):
            per = {}
            for i, (at, s, l) in smap.items():
                per[at] = per.get(at, 0.0) + k['w'][i - 1][n]
            tot = sum(per.values())
            pr = 1.0 / (natom * sum((x / tot) ** 2 for x in per.values())) if tot > 0 else 0.0
            w5d = sum(k['w'][i - 1][n] for i in w_idx)
            top = max(per, key=per.get)
            st = {'k': k['ik'], 'band': n + 1, 'E': k['e'][n], 'psi2': tot, 'PR_n': pr, 'W5d': w5d,
                  'top_atom': f'{species[top]}{top}', 'top_w': per[top] / tot if tot else 0.0}
            if nspin == 2:
                st['s'] = k['spin']
            states.append(st)
    above = [s for s in states if s['band'] > a.nv]
    below = [s for s in states if s['band'] <= a.nv]
    res = {'n_atoms': natom, 'n_bands': nb, 'n_k': len(ks) // nspin, 'N_v': a.nv, 'E_F_eV': ef,
           'n_W5d_orbitals': len(w_idx), 'adapter': 'legacy A23 nc_readout (raw W-5d, band-index domain)',
           'primary': False}
    if nspin == 2:
        res['nspin'] = 2
    low = min(above, key=lambda s: s['E']) if above else None
    res['lowest_above_Nv_eV'] = low['E'] if low else None
    cands = [s for s in above if s['PR_n'] >= 0.20]
    ec = min(cands, key=lambda s: s['E']) if cands else None
    res['E_c_eV'] = ec['E'] if ec and low and ec['E'] - low['E'] <= 1.0 else None
    res['E_c_state'] = ec if ec else None
    res['E_c_unresolved'] = res['E_c_eV'] is None
    vcands = [s for s in below if s['PR_n'] >= 0.20]
    ev = max(vcands, key=lambda s: s['E']) if vcands else None
    res['E_v_eV'] = ev['E'] if ev else None
    res['E_v_state'] = ev
    res['gap_host_eV'] = (res['E_c_eV'] - res['E_v_eV']) if res['E_c_eV'] is not None and ev else None
    wst = [s for s in above if s['W5d'] >= 0.30]
    w = min(wst, key=lambda s: s['E']) if wst else None
    res['W5d_state'] = w
    res['W5d_minus_Ec_eV'] = (w['E'] - res['E_c_eV']) if w and res['E_c_eV'] is not None else None
    gapw = [s for s in states if s['W5d'] >= 0.30 and ev and res['E_c_eV'] is not None and ev['E'] < s['E'] < res['E_c_eV']]
    res['W5d_states_in_host_gap'] = gapw
    # register section 1 (A16): completeness = unnormalised projected weight |psi|^2; < 0.90 is flagged, and a test that
    # rests on a flagged state is unresolved
    res['flagged_states'] = {name: s['psi2'] < 0.90 for name, s in (('E_v', ev), ('E_c', ec), ('W5d', w)) if s}
    res['rests_on_flagged_state'] = any(res['flagged_states'].values())
    lo_b, hi_b = a.nv - a.window_lo, a.nv + a.window_hi
    nk_txt = f'{len(ks) // nspin} k' + (' x 2 spin channels' if nspin == 2 else '')
    print('LEGACY A23 ADAPTER OUTPUT (raw W-5d, band-index domain, no interior rule): NOT primary for C5')
    print(f'{a.proj}: {natom} atoms, {nb} bands, {nk_txt}, N_v {a.nv}, E_F {ef:.4f} eV' if ef is not None else a.proj)
    print((' s' if nspin == 2 else '') + ' k  band       E(eV)   |psi|^2   PR_n    W-5d  top atom (share)')
    for s in states:
        if lo_b <= s['band'] <= hi_b:
            print((f"{s['s']:2d}" if nspin == 2 else '')
                  + f"{s['k']:2d} {s['band']:5d} {s['E']:11.4f} {s['psi2']:8.3f} {s['PR_n']:7.3f} {s['W5d']:7.3f}  "
                  f"{s['top_atom']} ({s['top_w']:.2f})")
    f = lambda x: 'UNRESOLVED' if x is None else f'{x:.4f} eV'
    print(f"host valence edge E_v = {f(res['E_v_eV'])}; host conduction edge E_c = {f(res['E_c_eV'])}; "
          f"host-edge gap = {f(res['gap_host_eV'])}")
    if w:
        print(f"lowest W-5d >= 0.30 state above N_v: {'s %d ' % w['s'] if nspin == 2 else ''}k {w['k']} band {w['band']} "
              f"E {w['E']:.4f} eV, W-5d {w['W5d']:.3f}, E - E_c = {f(res['W5d_minus_Ec_eV'])}")
    else:
        print('no state above N_v with W-5d >= 0.30')
    print('completeness (|psi|^2 >= 0.90, register section 1): ' + ', '.join(
        f"{k} {'FLAGGED' if v else 'ok'}" for k, v in res['flagged_states'].items())
        + ('  -> a test resting on a flagged state is UNRESOLVED' if res['rests_on_flagged_state'] else ''))
    if a.json:
        json.dump(res, open(a.json, 'w'), indent=1)
    if a.xml:
        hn_readout(a)


def hn_readout(a):
    """H-N accounting through the frozen package (numpy); prints every class with its unresolved checks."""
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
    from analysis.cli import read_cell
    from analysis.data import from_xml
    from analysis.report import fmt_checks, fmt_class, fmt_status
    data, st = from_xml(a.xml, a.proj, a.pout)
    # rc6: the same library path as 'python -m analysis cell' (lineage, planar average, gate, manifest from a VALID gate)
    dirs = list(dict.fromkeys(os.path.dirname(os.path.abspath(p)) for p in (a.xml, a.proj, a.pout)))
    r, c, qual = read_cell(data, st, dirs, a.name, a.certificate, nex=a.nex,
                           notes=['via nc_readout --xml (package read-out: primary)'])
    if c.N_v != a.nv:
        print(f'WARNING: --nv {a.nv} differs from (N_el - N_ex)/2 = {c.N_v} of the H-N accounting')
    print(f"PRIMARY package read-out; run qualification checks: {fmt_checks(qual['reasons'])}")
    hn = r['H-N']
    print(f"H-N accounting ({a.name or a.xml}): N_el {c.N_el:g}, N_ex {c.N_ex}, N_v {c.N_v}, nspin {data.nspin}; "
          f"electrons above N_v {r['excess_accounting']['electrons_above_Nv']:.4f} "
          f"({r['excess_accounting']['check']}); occupations {r['occupations']['f_source']}")
    if hn.get('class') == 'N/A':
        print(f"H-N class: N/A ({hn.get('note')})")
    else:
        print(f"f_ext {hn['f_ext']}, f_locW {hn['f_locW']}, f_W5d {hn['f_W5d']}, Delta_W {hn['Delta_W'].get('value_eV')} "
              f"(lower bound {hn['Delta_W'].get('lower_bound_eV')}), E_F - host edge {hn['E_F_minus_host_edge_eV']}")
        print(fmt_class('H-N class', hn['class'], hn.get('class_if_resolved'), hn.get('unresolved_checks', [])))
    p1 = r['H-G'].get('P1_lowest_W5d_state_above_host_edge')
    if p1:
        print(fmt_status('A23 (ii) / H-G P1: lowest >= 30 % W-5d state > 0.3 eV above the host edge', p1))
    if a.hn_json:
        with open(a.hn_json, 'w', newline='\n') as fh:
            json.dump(r, fh, indent=1)


if __name__ == '__main__':
    main()
