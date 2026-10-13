# g5_bind.sh - H-L geometry binding (read-only; crystalline vac/ and checks/gpumax_work/a20_g002 only).
# Parses geometries only: CELL_PARAMETERS, ATOMIC_POSITIONS blocks, header site positions, 'bfgs converged' line.
# Prints NO energies. Tar members are read in memory (python tarfile), nothing is extracted or written remotely.
cd ~/iwo_amorph || exit 1
timeout 240 python3 - <<'PY'
import hashlib, json, os, re, sys, tarfile
from collections import Counter

R = os.path.expanduser('~/iwo_amorph')
CELLS = ['In32O48', 'In31WO48', 'In32O47', 'In31WO47_far', 'In31WO47_near', 'In31WO47_near72']
PARENT = {'In32O47': 'In32O48', 'In31WO47_far': 'In31WO48', 'In31WO47_near': 'In31WO48', 'In31WO47_near72': 'In31WO48'}
MAN = []          # [path, bytes, md5, sha256]
SEEN = set()


def H(b):
    return hashlib.md5(b).hexdigest(), hashlib.sha256(b).hexdigest()


def addman(name, b):
    if name in SEEN:
        return
    SEEN.add(name)
    m, s = H(b)
    MAN.append([name, len(b), m, s])


def rfile(rel):
    p = os.path.join(R, rel)
    if not os.path.isfile(p):
        return None
    b = open(p, 'rb').read()
    addman(rel, b)
    return b.decode('utf-8', 'replace')


def hfile(rel):
    p = os.path.join(R, rel)
    if os.path.isfile(p):
        addman(rel, open(p, 'rb').read())
        return True
    return False


def rtar(rel, member):
    p = os.path.join(R, rel)
    if not os.path.isfile(p):
        return None
    with tarfile.open(p, 'r:gz') as t:
        for mi in t.getmembers():
            if mi.isfile() and os.path.normpath(mi.name) == member:
                b = t.extractfile(mi).read()
                addman(rel + '::' + member, b)
                return b.decode('utf-8', 'replace')
    return None


def sha_of(name):
    for r in MAN:
        if r[0] == name:
            return r[3]
    return None


def unit_of(s):
    t = re.sub(r'[(){}]', ' ', s).split()
    return t[1] if len(t) > 1 else 'alat'


ROW = re.compile(r'^\s*([A-Za-z][A-Za-z0-9_]*)\s+(-?\d+\.\d+(?:[eEdD][-+]?\d+)?)\s+(-?\d+\.\d+(?:[eEdD][-+]?\d+)?)\s+(-?\d+\.\d+(?:[eEdD][-+]?\d+)?)(.*)$')
TAU = re.compile(r'^\s+(\d+)\s+(\S+)\s+tau\(\s*(\d+)\)\s+=\s+\(\s*(\S+)\s+(\S+)\s+(\S+)\s+\)')


def fl(x):
    return float(x.replace('d', 'e').replace('D', 'e'))


def rows_after(L, i, nat):
    rows, j = [], i + 1
    while j < len(L) and len(rows) < nat:
        m = ROW.match(L[j])
        if not m:
            break
        rows.append((m.group(1), fl(m.group(2)), fl(m.group(3)), fl(m.group(4)), m.group(5).split()))
        j += 1
    extra = bool(j < len(L) and ROW.match(L[j]))
    return rows, extra


def parse_in(text):
    L = text.splitlines()
    nat = int(re.search(r'\bnat\s*=\s*(\d+)', text).group(1))
    d = dict(nat=nat, cell=None, cu=None, pos=None, pu=None, extra_rows=False, n_pos_cards=0)
    for i, l in enumerate(L):
        s = l.strip()
        if s.startswith('CELL_PARAMETERS'):
            d['cu'] = unit_of(s)
            d['cell'] = [[fl(x) for x in L[i + k].split()[:3]] for k in (1, 2, 3)]
        elif s.startswith('ATOMIC_POSITIONS'):
            d['pu'] = unit_of(s)
            d['pos'], d['extra_rows'] = rows_after(L, i, nat)
            d['n_pos_cards'] += 1
    d['iffix'] = sum(1 for p in d['pos'] if p[4])
    return d


def parse_out(text):
    L = text.splitlines()
    nat = int(re.search(r'number of atoms/cell\s*=\s*(\d+)', text).group(1))
    d = dict(nat=nat)
    m = re.search(r'celldm\(1\)=\s*([0-9.]+)', text)
    d['celldm1'] = float(m.group(1)) if m else None
    ax = re.findall(r'a\((\d)\) = \(\s*(\S+)\s+(\S+)\s+(\S+)\s+\)', text)
    d['axes_alat'] = [[float(v) for v in a[1:]] for a in ax[:3]] if len(ax) >= 3 else None
    g0 = None
    for i, l in enumerate(L):
        if 'positions (cryst. coord.)' in l:
            g0 = []
            for k in range(i + 1, i + 1 + nat):
                t = TAU.match(L[k])
                if not t:
                    break
                g0.append((t[2], float(t[4]), float(t[5]), float(t[6]), []))
            break
    d['g0'] = g0
    fin = [i for i, l in enumerate(L) if 'Begin final coordinates' in l]
    endf = [i for i, l in enumerate(L) if 'End final coordinates' in l]
    d['n_begin_final'] = len(fin)
    d['n_end_final'] = len(endf)
    fi = fin[-1] if fin else None
    blocks = []
    for i, l in enumerate(L):
        if l.strip().startswith('ATOMIC_POSITIONS'):
            rows, extra = rows_after(L, i, nat)
            blocks.append(dict(line=i + 1, unit=unit_of(l.strip()), pos=rows, final=(fi is not None and i > fi), extra=extra))
    d['blocks'] = blocks
    d['cell_in_final'] = bool(fi is not None and any(l.strip().startswith('CELL_PARAMETERS') for l in L[fi:(endf[-1] if endf else len(L))]))
    d['bfgs_lines'] = [l.strip() for l in L if 'bfgs converged' in l]
    d['n_bfgs_conv'] = len(d['bfgs_lines'])
    d['n_notconv'] = text.count('convergence NOT achieved')
    d['n_bfgs_failed'] = sum(1 for l in L if 'bfgs failed' in l.lower() or 'history already reset' in l)
    steps = re.findall(r'number of bfgs steps\s*=\s*(\d+)', text)
    d['last_bfgs_steps_line'] = int(steps[-1]) if steps else None
    d['n_bfgs_steps_lines'] = len(steps)
    return d


def parse_xyz(text):
    L = text.splitlines()
    nat = int(L[0].split()[0])
    lat = [float(x) for x in re.search(r'Lattice="([^"]+)"', L[1]).group(1).split()]
    A = [lat[0:3], lat[3:6], lat[6:9]]
    Ai = inv3(A)
    pos = []
    for l in L[2:2 + nat]:
        t = l.split()
        r = [float(x) for x in t[1:4]]
        f = [sum(r[k] * Ai[k][j] for k in range(3)) for j in range(3)]
        pos.append((t[0], f[0], f[1], f[2], []))
    return dict(nat=nat, cell=A, pos=pos)


def inv3(A):
    a, b, c = A[0]; d, e, f = A[1]; g, h, i = A[2]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    return [[(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
            [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
            [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det]]


def f10(x):
    s = '%.10f' % x
    return '0.0000000000' if s == '-0.0000000000' else s


def canon(cell, cu, pos, pu):
    L = ['CELL_PARAMETERS ' + cu] + [' '.join(f10(v) for v in r) for r in cell]
    L += ['ATOMIC_POSITIONS ' + pu] + [' '.join([p[0]] + [f10(v) for v in p[1:4]]) for p in pos]
    return '\n'.join(L) + '\n'


def canon_pos(pos, pu):
    return '\n'.join(['ATOMIC_POSITIONS ' + pu] + [' '.join([p[0]] + [f10(v) for v in p[1:4]]) for p in pos]) + '\n'


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def cmp(A, B):
    if A is None or B is None:
        return dict(ok=False, note='missing')
    out = dict(nA=len(A), nB=len(B), species_seq_equal=[a[0] for a in A] == [b[0] for b in B])
    if len(A) != len(B):
        out['ok'] = False
        return out
    raw = max(abs(a[k] - b[k]) for a, b in zip(A, B) for k in (1, 2, 3))
    mi = max(abs((a[k] - b[k]) - round(a[k] - b[k])) for a, b in zip(A, B) for k in (1, 2, 3))
    out.update(max_raw=raw, max_minimage=mi)
    return out


def cmp_cell(C1, C2):
    if C1 is None or C2 is None:
        return None
    return max(abs(C1[i][j] - C2[i][j]) for i in range(3) for j in range(3))


def nongeom(text):
    L = text.splitlines()
    out, skip = [], 0
    for l in L:
        s = l.strip()
        if s.startswith('CELL_PARAMETERS'):
            out.append(s); skip = 3; continue
        if skip:
            skip -= 1; continue
        if ROW.match(l):
            continue
        out.append(l.rstrip())
    return out


def diffset(t1, t2):
    a, b = nongeom(t1), nongeom(t2)
    import difflib
    return [d for d in difflib.unified_diff(a, b, lineterm='', n=0) if d[:1] in '+-' and not d.startswith(('+++', '---'))]


def mi_dist(fa, fb, A):
    df = [(fa[k] - fb[k]) - round(fa[k] - fb[k]) for k in range(3)]
    c = [sum(df[k] * A[k][j] for k in range(3)) for j in range(3)]
    return (c[0] ** 2 + c[1] ** 2 + c[2] ** 2) ** 0.5


def match_parent(P, C, tol=2e-6):
    used, mp = set(), []
    for ci, c in enumerate(C):
        best = None
        for pi, p in enumerate(P):
            if p[0] != c[0] or pi in used:
                continue
            dd = max(abs((c[k] - p[k]) - round(c[k] - p[k])) for k in (1, 2, 3))
            if best is None or dd < best[1]:
                best = (pi, dd)
        mp.append(best)
        if best is not None:
            used.add(best[0])
    missing = [pi for pi in range(len(P)) if pi not in used]
    idx = [m[0] for m in mp]
    expect = [pi for pi in range(len(P)) if pi not in missing]
    return dict(missing=missing, missing_species=[P[i][0] for i in missing], max_match=max(m[1] for m in mp),
                n_over_tol=sum(1 for m in mp if m[1] > tol), order_preserved=(idx == expect))


RES = {}
GEO = {}
for c in CELLS:
    v, a = 'vac/' + c, 'checks/gpumax_work/a20_g002/' + c
    r = dict()
    for f in ['relax_s0_results.tar.gz', 'final_results.tar.gz', 'final.tmpl', 'scf.out']:
        hfile(v + '/' + f)
    hfile(a + '/a20g002_%s_results.tar.gz' % c)
    T = {}
    T['relax.in'] = rfile(v + '/relax.in')
    T['relax.out'] = rfile(v + '/relax.out')
    T['scf.in'] = rfile(v + '/scf.in')
    T['scf.out'] = rfile(v + '/scf.out')
    T['xyz'] = rfile(v + '/%s.xyz' % c)
    T['final.tmpl'] = rfile(v + '/final.tmpl')
    T['ftar:scf.in'] = rtar(v + '/final_results.tar.gz', 'scf.in')
    T['ftar:relax.in'] = rtar(v + '/final_results.tar.gz', 'relax.in')
    T['ftar:relax.out'] = rtar(v + '/final_results.tar.gz', 'relax.out')
    T['ftar:scf.out'] = rtar(v + '/final_results.tar.gz', 'scf.out')
    T['rtar:relax.in'] = rtar(v + '/relax_s0_results.tar.gz', 'relax.in')
    T['rtar:relax.out'] = rtar(v + '/relax_s0_results.tar.gz', 'relax.out')
    T['a20:scf.in'] = rfile(a + '/scf.in')
    T['a20tar:scf.in'] = rtar(a + '/a20g002_%s_results.tar.gz' % c, 'scf.in')
    T['a20tar:scf.out'] = rtar(a + '/a20g002_%s_results.tar.gz' % c, 'scf.out')

    ro = parse_out(T['relax.out'])
    rin = parse_in(T['relax.in'])
    finals = [b for b in ro['blocks'] if b['final']]
    pre = [b for b in ro['blocks'] if not b['final']]
    fb = finals[-1]
    A_pos, A_unit = fb['pos'], fb['unit']
    A_cell, A_cu = rin['cell'], rin['cu']
    r['relax_out'] = dict(nat=ro['nat'], n_bfgs_conv=ro['n_bfgs_conv'], bfgs_line=ro['bfgs_lines'][-1] if ro['bfgs_lines'] else None,
                          n_begin_final=ro['n_begin_final'], n_end_final=ro['n_end_final'], cell_in_final_block=ro['cell_in_final'],
                          n_pos_blocks_before_final=len(pre), last_bfgs_steps_line=ro['last_bfgs_steps_line'],
                          n_notconv=ro['n_notconv'], final_block_line=fb['line'], final_rows=len(A_pos), final_extra_rows=fb['extra'],
                          final_unit=A_unit)
    # final block equals the last geometry printed before it (or geometry 0 for 0-step runs)
    r['final_vs_last_block'] = cmp(A_pos, pre[-1]['pos']) if pre else None
    r['final_vs_g0_header'] = cmp(A_pos, ro['g0'])
    # cell from relax.out header (celldm(1) * axes, bohr -> angstrom) vs relax.in cell
    BOHR = 0.529177210903
    if ro['axes_alat'] and ro['celldm1']:
        cell_out = [[x * ro['celldm1'] * BOHR for x in row] for row in ro['axes_alat']]
        r['cell_relaxout_header_vs_relaxin_A'] = cmp_cell(cell_out, A_cell)
    r['species_counts'] = dict(Counter(p[0] for p in A_pos))
    r['nat_declared_relax_in'] = rin['nat']
    canonA = canon(A_cell, A_cu, A_pos, A_unit)
    r['hash_a'] = sha(canonA)
    r['poshash_a'] = sha(canon_pos(A_pos, A_unit))
    r['cell_A'] = A_cell
    r['cell_unit'] = A_cu
    GEO[c] = dict(pos=A_pos, cell=A_cell)

    comps = {}
    for key in ['scf.in', 'ftar:scf.in', 'a20:scf.in', 'a20tar:scf.in', 'relax.in', 'ftar:relax.in', 'rtar:relax.in']:
        t = T[key]
        if t is None:
            comps[key] = dict(ok=False, note='missing')
            continue
        d = parse_in(t)
        cc = cmp(A_pos, d['pos'])
        cc['nat_declared'] = d['nat']
        cc['pos_unit'] = d['pu']
        cc['cell_unit'] = d['cu']
        cc['max_cell_diff_A'] = cmp_cell(A_cell, d['cell'])
        cc['extra_rows'] = d['extra_rows']
        cc['n_pos_cards'] = d['n_pos_cards']
        cc['if_pos_rows'] = d['iffix']
        cc['species_counts'] = dict(Counter(p[0] for p in d['pos']))
        cc['hash'] = sha(canon(d['cell'], d['cu'], d['pos'], d['pu']))
        cc['hash_equal_a'] = (cc['hash'] == r['hash_a'])
        comps[key] = cc
    # computed geometry: header site positions (crystal, 7 decimals) printed by pw.x in each SCF output
    for key in ['scf.out', 'ftar:scf.out', 'a20tar:scf.out']:
        t = T[key]
        if t is None:
            comps[key] = dict(ok=False, note='missing')
            continue
        o = parse_out(t)
        cc = cmp(A_pos, o['g0'])
        cc['nat_out'] = o['nat']
        if o['axes_alat'] and o['celldm1']:
            cc['max_cell_diff_A'] = cmp_cell([[x * o['celldm1'] * BOHR for x in row] for row in o['axes_alat']], A_cell)
        cc['n_pos_blocks'] = len(o['blocks'])
        comps[key] = cc
    r['cmp'] = comps
    # identical-file checks
    r['same_file'] = {
        'relax.out == relax_s0_tar::relax.out': sha_of(v + '/relax.out') == sha_of(v + '/relax_s0_results.tar.gz::relax.out'),
        'relax.out == final_tar::relax.out': sha_of(v + '/relax.out') == sha_of(v + '/final_results.tar.gz::relax.out'),
        'relax.in == relax_s0_tar::relax.in': sha_of(v + '/relax.in') == sha_of(v + '/relax_s0_results.tar.gz::relax.in'),
        'relax.in == final_tar::relax.in': sha_of(v + '/relax.in') == sha_of(v + '/final_results.tar.gz::relax.in'),
        'scf.in == final_tar::scf.in': sha_of(v + '/scf.in') == sha_of(v + '/final_results.tar.gz::scf.in'),
        'scf.out == final_tar::scf.out': sha_of(v + '/scf.out') == sha_of(v + '/final_results.tar.gz::scf.out'),
        'a20 scf.in == a20_tar::scf.in': sha_of(a + '/scf.in') == sha_of(a + '/a20g002_%s_results.tar.gz::scf.in' % c),
    }
    # non-geometry setting differences (inputs only; no energies)
    r['settings_diff'] = {
        'final.tmpl -> vac scf.in': diffset(T['final.tmpl'], T['scf.in']),
        'vac scf.in -> a20 scf.in': diffset(T['scf.in'], T['a20:scf.in']),
        'a20 scf.in -> a20_tar scf.in': diffset(T['a20:scf.in'], T['a20tar:scf.in']),
        'vac relax.in -> vac scf.in': diffset(T['relax.in'], T['scf.in']),
    }
    # built input geometry (xyz, angstrom -> crystal) vs relax.out geometry 0 (header, 7 decimals)
    X = parse_xyz(T['xyz'])
    r['xyz'] = dict(nat=X['nat'], species_counts=dict(Counter(p[0] for p in X['pos'])),
                    xyz_vs_relaxout_g0=cmp(X['pos'], ro['g0']), cell_diff_A=cmp_cell(X['cell'], A_cell))
    r['g0'] = dict(nat=len(ro['g0']) if ro['g0'] else None, poshash7=sha('\n'.join('%s %.7f %.7f %.7f' % p[:4] for p in ro['g0'])))
    GEO[c]['g0'] = ro['g0']
    GEO[c]['xyz'] = X['pos']
    RES[c] = r

# vacancy site binding: built vacancy cell (xyz, and pw.x geometry 0) vs relaxed parent (a); parent relaxed in 0 BFGS steps
for c, p in PARENT.items():
    P, Acell = GEO[p]['pos'], GEO[p]['cell']
    s = {}
    s['xyz_vs_parent_a'] = match_parent(P, GEO[c]['xyz'])
    if c != 'In31WO47_near':
        s['relaxout_g0_vs_parent_a'] = match_parent(P, GEO[c]['g0'], tol=6e-8)
    miss = s['xyz_vs_parent_a']['missing']
    if p == 'In31WO48' and len(miss) == 1:
        w = [i for i, q in enumerate(P) if q[0] == 'W'][0]
        s['removed_W_O_A'] = round(mi_dist(P[miss[0]][1:4], P[w][1:4], Acell), 5)
    RES[c]['vacancy_site'] = s

# W-O distances in the relaxed parent In31WO48 (a): shortest six and largest four (0-based atom indices)
P, Acell = GEO['In31WO48']['pos'], GEO['In31WO48']['cell']
w = [i for i, q in enumerate(P) if q[0] == 'W']
dl = sorted((round(mi_dist(q[1:4], P[w[0]][1:4], Acell), 5), i) for i, q in enumerate(P) if q[0] == 'O')
WINFO = dict(W_index=w, shortest=dl[:6], largest=dl[-4:], n_O=len(dl))

# In31WO47_near: A28 restart history
N = {}
v = 'vac/In31WO47_near'
TT = {}
for key, rel in [('attempt1/relax.in', v + '/attempt1/relax.in'), ('attempt1/relax.out', v + '/attempt1/relax.out'),
                 ('relax.in.pre_A28', v + '/relax.in.pre_A28_20261011T130452Z'),
                 ('a28/relax.in.A28', v + '/a28_staging/relax.in.A28'),
                 ('a28/relax.in.template_current', v + '/a28_staging/relax.in.template_current'),
                 ('a28/s0/relax.in', v + '/a28_staging/s0/relax.in'), ('a28/s0/relax.out', v + '/a28_staging/s0/relax.out')]:
    TT[key] = rfile(rel)
TT['attempt1_tar:relax.in'] = rtar(v + '/attempt1/relax_s0_results.tar.gz', 'relax.in')
TT['attempt1_tar:relax.out'] = rtar(v + '/attempt1/relax_s0_results.tar.gz', 'relax.out')
hfile(v + '/attempt1/relax_s0_results.tar.gz')
for f in ['a28_staging/MANIFEST.md5', 'a28_staging/apply_A28_near.sh', 'a28_staging/a28_verify.py', 'a28_staging/relax.sub.A28q2', 'a28_staging/final.sub.A28q2', 'relax.sub', 'final.sub']:
    hfile(v + '/' + f)
man28 = dict((l.split()[1], l.split()[0]) for l in open(os.path.join(R, v, 'a28_staging/MANIFEST.md5')).read().splitlines() if l.strip())
N['manifest_check'] = {}
for k, rel in [('relax.in.A28', v + '/a28_staging/relax.in.A28'), ('relax.in.template_current', v + '/a28_staging/relax.in.template_current'),
               ('s0/relax.in', v + '/a28_staging/s0/relax.in'), ('s0/relax.out', v + '/a28_staging/s0/relax.out')]:
    md = [r[2] for r in MAN if r[0] == rel]
    N['manifest_check'][k] = (md[0] == man28.get(k)) if md else None
att_in = parse_in(TT['attempt1/relax.in'])
att_out = parse_out(TT['attempt1/relax.out'])
a28 = parse_in(TT['a28/relax.in.A28'])
cur_out = parse_out(open(os.path.join(R, v, 'relax.out'), errors='replace').read())
N['attempt1_relax_out'] = dict(nat=att_out['nat'], n_bfgs_conv=att_out['n_bfgs_conv'], n_notconv=att_out['n_notconv'],
                               n_pos_blocks=len(att_out['blocks']), n_begin_final=att_out['n_begin_final'])
N['same_file'] = {
    'attempt1/relax.in == relax.in.pre_A28': sha_of(v + '/attempt1/relax.in') == sha_of(v + '/relax.in.pre_A28_20261011T130452Z'),
    'attempt1/relax.in == a28/relax.in.template_current': sha_of(v + '/attempt1/relax.in') == sha_of(v + '/a28_staging/relax.in.template_current'),
    'attempt1/relax.in == a28/s0/relax.in': sha_of(v + '/attempt1/relax.in') == sha_of(v + '/a28_staging/s0/relax.in'),
    'attempt1/relax.in == attempt1_tar::relax.in': sha_of(v + '/attempt1/relax.in') == sha_of(v + '/attempt1/relax_s0_results.tar.gz::relax.in'),
    'attempt1/relax.out == a28/s0/relax.out': sha_of(v + '/attempt1/relax.out') == sha_of(v + '/a28_staging/s0/relax.out'),
    'attempt1/relax.out == attempt1_tar::relax.out': sha_of(v + '/attempt1/relax.out') == sha_of(v + '/attempt1/relax_s0_results.tar.gz::relax.out'),
}
N['attempt1_in_vs_attempt1_g0'] = cmp(att_in['pos'], att_out['g0'])
N['attempt1_in_vs_xyz'] = cmp(att_in['pos'], GEO['In31WO47_near']['xyz'])
N['attempt1_in_vs_parent_a'] = match_parent(GEO['In31WO48']['pos'], att_in['pos'], tol=1e-9)
N['A28_vs_attempt1_blocks'] = [dict(geometry=k + 1, line=b['line'], **cmp(a28['pos'], b['pos'])) for k, b in enumerate(att_out['blocks'])]
N['A28_vs_restart_g0'] = cmp(a28['pos'], cur_out['g0'])
N['A28_vs_attempt1_in_cell_A'] = cmp_cell(a28['cell'], att_in['cell'])
N['A28_settings_diff_vs_attempt1_in'] = diffset(TT['attempt1/relax.in'], TT['a28/relax.in.A28'])
N['A28_hash'] = sha(canon(a28['cell'], a28['cu'], a28['pos'], a28['pu']))
N['attempt1_in_hash'] = sha(canon(att_in['cell'], att_in['cu'], att_in['pos'], att_in['pu']))
N['A28_vs_final_a'] = cmp(a28['pos'], GEO['In31WO47_near']['pos'])

print('JSONSTART')
print(json.dumps(dict(cells=RES, winfo=WINFO, near=N, manifest=MAN), indent=1, default=str))
print('JSONEND')
PY
echo "python rc=$?"
