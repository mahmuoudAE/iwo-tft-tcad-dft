"""H-L registered differences and the A20(ii) smearing sensitivity, parsed from r23.out (raw grep of lxplus files)."""
import re, sys, json
RY = 13.605693122994  # eV per Ry (CODATA 2018, as in QE 7.x)
txt = open(sys.argv[1], encoding='utf8').read()
cells = ['In32O48', 'In31WO48', 'In32O47', 'In31WO47_far', 'In31WO47_near', 'In31WO47_near72']
E, TS, chk = {}, {}, {}
for c in cells:
    blk = txt.split('######## ' + c + '\n')[1].split('########')[0]
    rel, fin, a20 = blk.split('-- relax.out')[1].split('-- FINAL')[0], blk.split('-- FINAL')[1].split('-- A20(ii)')[0], blk.split('-- A20(ii)')[1]
    def last_bang(s):
        return float(re.findall(r'^!\s+total energy\s+=\s+(-?\d+\.\d+) Ry', s, re.M)[-1])
    def smear(s):
        return float(re.findall(r'smearing contrib\. \(-TS\)\s+=\s+(-?\d+\.\d+) Ry', s)[-1])
    E[c] = {'k3_g005': last_bang(rel), 'k4_g005': last_bang(fin), 'k3_g002': last_bang(a20)}
    TS[c] = {'k3_g005': smear(rel), 'k4_g005': smear(fin), 'k3_g002': smear(a20)}
    fe = float(re.search(r'Final energy\s+=\s+(-?\d+\.\d+) Ry', rel).group(1))
    assert abs(fe - E[c]['k3_g005']) < 1e-7, c
    chk[c] = {
        'bfgs_converged': 'bfgs_conv=1' in rel, 'relax_scf_fail0': 'scf_fail=0 ' in rel,
        'final_conv': 'conv=1 notach=0 done=1' in fin, 'a20_conv': 'conv=1 notach=0 done=1' in a20,
        'k4_14_36_30': re.search(r'number of k points=\s+(\d+)', fin).group(1),
        'a20_width': re.search(r'width \(Ry\)=\s+([\d.]+)', a20).group(1),
        'a20_diff_only_k_degauss': a20.count('degauss') == 2 and a20.count('3 3 3 0 0 0') == 1 and len(re.findall(r'^\d+c\d+', a20, re.M)) == 2,
    }
def dloc(s, near='In31WO47_near'):
    return (E[near][s] - E['In31WO47_far'][s]) * RY
def ddop(s):
    return ((E['In31WO47_far'][s] - E['In31WO48'][s]) - (E['In32O47'][s] - E['In32O48'][s])) * RY
out = {'checks': chk, 'cell_shift_g002_minus_g005_k3_meV': {c: (E[c]['k3_g002'] - E[c]['k3_g005']) * RY * 1e3 for c in cells},
       'cell_shift_k4_minus_k3_meV': {c: (E[c]['k4_g005'] - E[c]['k3_g005']) * RY * 1e3 for c in cells},
       'minus_TS_Ry': TS}
for name, f in (('dE_local_O30', lambda s: dloc(s)), ('dE_local_O72_sens', lambda s: dloc(s, 'In31WO47_near72')), ('dE_dop', ddop)):
    v = {s: f(s) for s in ('k3_g005', 'k4_g005', 'k3_g002')}
    v['k3_to_k4_meV'] = (v['k4_g005'] - v['k3_g005']) * 1e3
    v['A20ii_shift_meV'] = (v['k3_g002'] - v['k3_g005']) * 1e3
    out[name] = v
# zero-width estimate (E+F)/2 = F - (-TS)/2, not registered; consistency check of the two widths only
z = {c: {s: (E[c][s] - TS[c][s] / 2) for s in ('k3_g005', 'k3_g002')} for c in cells}
out['E0_estimate_shift_meV'] = {c: (z[c]['k3_g002'] - z[c]['k3_g005']) * RY * 1e3 for c in cells}
print(json.dumps(out, indent=1))
