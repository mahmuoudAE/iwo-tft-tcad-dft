"""A44 addendum 1: build the F9 relaxation_lineage records of the 7 cells with the frozen v18 writers (F11 venv, -I -B).
Sealed handling: archive members needed as files (relax.out; saved or checkpoint relax.in) are copied byte-exact into
SEALED and never printed; writer stdout/stderr go to sealed files; only a validated status line is displayed
('wrote', 'NOT WRITTEN: <code>' or 'SIGHT_ABORT'), with the record sha256."""
import hashlib
import json
import os
import re
import subprocess
import tarfile

EV = r'C:\Users\moham\iwo_lineage_evidence_20261014'
AUD = r'C:\Users\moham\iwo_release_audit_20261014\lineage'
SEALED = os.path.join(AUD, 'sealed')
PY = r'C:\Users\moham\iwo_readout_venv_rc7\Scripts\python.exe'
WR = r'C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\iwo-tft-research-private\compute\amorph\f9_checker_v18\f9_writers.py'
OFFSET = (r'C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\iwo-tft-research-private\codex\work_chat\annex'
          r'\A44_add1_offset_evidence_lxplus.txt')
# cell: (route, joblog, [(k, cluster, results archive, checkpoint or None, kind)], reset_evidence_for_k)
CELLS = {
    'aIO_bulk_s1': ('registered-Gaussian', 'logs/relax.log', [(0, 12888463, 'relax_s0_results.tar.gz', 'relax_s0_12888463.tar.gz', 'pre')], {}),
    'aIWO_bulk_s1': ('registered-Gaussian', 'logs/relax.log', [(0, 12888464, 'relax_s0_results.tar.gz', 'relax_s0_12888464.tar.gz', 'pre')], {}),
    'aIO_1p0_s1': ('registered-Gaussian', 'logs/relax.log', [(0, 12883942, 'relax_s0_results.tar.gz', 'relax_s0_12883942.tar.gz', 'pre'),
                                                             (1, 12890833, 'relax_s1_results.tar.gz', 'relax_s1_12890833.tar.gz', 'itemb')],
                   {1: 'd24_transition.log'}),
    'aIWO_1p0_s1': ('registered-MV', 'logs/relax.log', [(0, 12883943, 'relax_s0_results.tar.gz', 'relax_s0_12883943.tar.gz', 'pre')], {}),
    'aIO_0p8_s1': ('registered-Gaussian', 'logs/pilot_relax.log', [(0, 12885853, 'relax_s0_results.tar.gz', None, 'pre'),
                                                                   (1, 12893251, 'relax_s1_results.tar.gz', None, 'pre')], {}),
    'aIO_0p7_s1': ('registered-Gaussian', 'logs/relax.log', [(0, 12884016, 'relax_s0_results.tar.gz', 'relax_s0_12884016.tar.gz', 'pre'),
                                                             (1, 12885905, 'relax_s1_results.tar.gz', None, 'itemb')], {}),
    'aIWO_0p7_s1': ('registered-MV', 'logs/relax.log', [(0, 12883952, 'relax_s0_results.tar.gz', 'relax_s0_12883952.tar.gz', 'pre'),
                                                        (1, 12890944, 'relax_s1_results.tar.gz', None, 'itemb'),
                                                        (2, 12901057, 'relax_s2_results.tar.gz', 'relax_s2_12901057.tar.gz', 'itemb')],
                    {1: 'd24_transition.log'}),
}
STATUS = re.compile(r'^(wrote \S+|NOT WRITTEN: [a-z0-9_]+|SIGHT_ABORT: .{0,200})$')


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def member(arc, name, dest):
    """Byte copy of one archive member (never printed). None if the member is absent."""
    with tarfile.open(arc, 'r:gz') as t:
        try:
            m = t.getmember(name)
        except KeyError:
            return None
        if not m.isfile():
            return None
        data = t.extractfile(m).read()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'wb') as f:
        f.write(data)
    return dest


def build(cell):
    route, joblog, segs, resets = CELLS[cell]
    d, sd = os.path.join(AUD, cell), os.path.join(SEALED, cell)
    os.makedirs(d, exist_ok=True)
    os.makedirs(sd, exist_ok=True)
    ident = ['# iwo-f9-archive-identity/1', f'# run {cell}']
    seg_src = []
    for k, cl, res, ck, kind in segs:
        ra = os.path.join(EV, cell, res)
        arcs = [ra]
        ident.append(f'{res} {os.path.getsize(ra)} {sha(ra)} cluster {cl} k {k}')
        if ck:
            ca = os.path.join(EV, 'eos_checkpoints', ck)
            arcs.append(ca)
            ident.append(f'{ck} {os.path.getsize(ca)} {sha(ca)} cluster {cl} k {k}')
        out = member(ra, 'relax.out', os.path.join(sd, f's{k}_relax.out'))
        if kind == 'itemb':
            rin = member(ra, f'relax_s{k}_input.in', os.path.join(sd, f's{k}_relax_s{k}_input.in'))
        else:
            rin = member(os.path.join(EV, 'eos_checkpoints', ck), 'relax.in', os.path.join(sd, f's{k}_ckpt_relax.in')) if ck else None
        s = {'segment': f's{k}', 'cluster': cl, 'archives': arcs, 'joblog': os.path.join(EV, cell, joblog)}
        if out:
            s['relax_out'] = out
        if rin:
            s['relax_in'] = rin
        if k in resets:
            s['reset_evidence'] = os.path.join(EV, cell, resets[k])
        seg_src.append(s)
    idp = os.path.join(d, f'archive_identity_{cell}.txt')
    with open(idp, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(ident) + '\n')
    for s in seg_src:
        s['export_manifest'] = idp
    spec = {'params': {'cell': cell, 'route': route, 'run': cell},
            'sources': {'segments': seg_src, 'offset_evidence': OFFSET}}
    sp = os.path.join(d, f'spec_lineage_{cell}.json')
    with open(sp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(spec, f, indent=1)
    rec = os.path.join(d, f'relaxation_lineage_{cell}.json')
    so, se = os.path.join(sd, 'writer.stdout'), os.path.join(sd, 'writer.stderr')
    with open(so, 'wb') as fo, open(se, 'wb') as fe:
        rc = subprocess.run([PY, '-I', '-B', WR, 'relaxation_lineage', '--spec', sp, '--out', rec], stdout=fo,
                            stderr=fe).returncode
    txt = open(so, 'rb').read().decode('utf-8', 'replace').replace('\r\n', '\n').strip()
    ok = os.path.getsize(se) == 0 and STATUS.match(txt) and '\n' not in txt
    shown = txt if ok else f'UNEXPECTED OUTPUT (sealed; stdout {sha(so)[:8]}, stderr {sha(se)[:8]})'
    return {'cell': cell, 'route': route, 'exit': rc, 'status': shown,
            'record_sha256': sha(rec) if rc == 0 and os.path.isfile(rec) else None, 'spec_sha256': sha(sp),
            'identity_sha256': sha(idp)}


if __name__ == '__main__':
    os.makedirs(AUD, exist_ok=True)
    res = [build(c) for c in CELLS]
    with open(os.path.join(AUD, 'lineage_build_summary.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(res, f, indent=1)
    for r in res:
        print(r['cell'], r['route'], r['exit'], r['status'], (r['record_sha256'] or '')[:8])
