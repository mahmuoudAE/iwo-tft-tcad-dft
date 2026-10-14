"""A44 blind evidence audit runner (register A44 / D-48). Standard library only; run with the F11 venv: python -I -B.

Runs, per pinned cell, exactly the pinned commands (section B steps 0-2): rc7 `certify` and `validate-cert` (provenance
binding only) and the frozen F9 v15 `cert_assert.py`. Every command's stdout and stderr go to sealed files under
AUD/sealed/ before anything is read. A key/type/value allowlist validator then reads them; only validated hashes, file
names, provenance and qualification-status fields are displayed. Any unexpected output (another key, type or value,
non-empty stderr, a traceback, unparsable output) aborts that cell silently: only the step, the exit code and the sealed
file's sha256 are shown. No `cell`, `compare` or `series` command exists in this script.

Usage:  <venv>/python.exe -I -B a44_audit_runner.py step0|cells
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

REPO = r'C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\iwo-tft-research-private'
AMORPH = os.path.join(REPO, 'compute', 'amorph')
PY = r'C:\Users\moham\iwo_readout_venv_rc7\Scripts\python.exe'
ARCH = r'C:\Users\moham\iwo_exports_final_20261014'
AUD = r'C:\Users\moham\iwo_release_audit_20261014'
REGISTER = os.path.join(REPO, 'codex', 'work_chat', 'HYPOTHESIS_REGISTER.md')
F9 = os.path.join(AMORPH, 'f9_checker', 'cert_assert.py')
RC7_CODE = 'fff642a13a62db6d0cde3e4704cdbf343913fc1972d9fa95d79f7ad8f4e01158'
F9_FROZEN = {'cert_assert.py': 'a9943bdc', 'f9_writers.py': '1830f33a', 'f9_common.py': 'd251700f'}
CELLS = [('aIO_bulk_s1', 12890432), ('aIWO_bulk_s1', 12891160), ('aIO_1p0_s1', 12891132), ('aIWO_1p0_s1', 12889857),
         ('aIO_0p8_s1', 12904001), ('aIO_0p7_s1', 12894279), ('aIWO_0p7_s1', 12902517)]
CLAIMS = {'relaxation': 'converged', 'geometry': 'mv'}       # the registered intent for an A26 FINAL of a converged chain
COMPILED_BY = 'A44 blind evidence audit'

HEX = re.compile(r'^[0-9a-f]{64}$')
NAME = re.compile(r'^[A-Za-z0-9_.:/+\-]{1,200}$')
CERT_KEYS = {'certificate', 'source', 'run_files', 'geometry_sha256', 'pseudopotentials', 'mode', 'gate'}
GATE_KEYS = {'certificate_sha256', 'certificate_valid', 'problems', 'reasons', 'relaxation', 'smearing_qualified',
             'smearing_width_Ry', 'geometry', 'manifest_verified', 'manifest', 'seed', 'pseudopotentials_bound',
             'pseudopotentials', 'construction', 'register_missing'}
PROV_KEYS = {'code_version', 'code_sha256', 'register', 'inputs', 'run_files', 'geometry_sha256', 'certificate_sha256',
             'source', 'mode'}
MANIFEST_KEYS = {'kind', 'film', 'substrate', 'passivation', 'N_ex', 'seed', 'spec_name', 'construction'}
PROBLEM_CATS = [('relaxation: no evidence files', 'relaxation evidence missing'),
                ('geometry: no evidence files', 'geometry evidence missing'),
                ('relaxation: evidence', 'relaxation evidence unbound'), ('geometry: evidence', 'geometry evidence unbound'),
                ('planar-average inputs', 'planar-average inputs not consumed'),
                ('certificate lacks ', 'certificate lacks a field'), ('pseudopotential', 'pseudopotential provenance'),
                ('run lineage', 'run lineage (pseudopotential coverage)'), ('manifest: ', 'composition manifest'),
                ('consumed file ', 'consumed file not bound'), ('no projection source', 'no projection source'),
                ('geometry hash mismatch', 'geometry hash mismatch'), ('schema ', 'certificate schema'),
                ('certificate is for', 'certificate identity'), ('relaxation status', 'relaxation status'),
                ('geometry status', 'geometry status'), ('smearing', 'smearing block')]
REASON_CATS = [('run certificate missing or NOT VALID', 'gate NOT VALID'),
               ('relaxation ', 'relaxation not certified converged'),
               ('smearing qualification pending', 'smearing pending'),
               ('composition manifest not verified', 'manifest not verified'),
               ('pseudopotential provenance not bound', 'pseudopotentials not bound'),
               ('hypothesis register not found', 'register not found')]


class Unexpected(Exception):
    pass


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def run(tag, args, cwd=AMORPH):
    """Run one command with stdout/stderr sealed to files; return (exit code, stdout path, stderr path)."""
    sd = os.path.join(AUD, 'sealed')
    os.makedirs(sd, exist_ok=True)
    out, err = os.path.join(sd, tag + '.stdout'), os.path.join(sd, tag + '.stderr')
    env = dict(os.environ, IWO_REGISTER=REGISTER)
    with open(out, 'wb') as fo, open(err, 'wb') as fe:
        rc = subprocess.run(args, cwd=cwd, stdout=fo, stderr=fe, env=env).returncode
    with open(os.path.join(AUD, 'commands.log'), 'a', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps({'tag': tag, 'args': args, 'cwd': cwd, 'exit': rc, 'stdout_sha256': sha(out),
                            'stderr_sha256': sha(err)}) + '\n')
    return rc, out, err


def need(cond):
    if not cond:
        raise Unexpected()


def cat(text, table):
    need(isinstance(text, str))
    for pre, label in table:
        if text.startswith(pre):
            return label
    return 'unclassified (sealed)'


def check_hash_map(d, names=NAME):
    need(isinstance(d, dict))
    for k, v in d.items():
        need(isinstance(k, str) and names.match(k) and isinstance(v, str) and HEX.match(v))


def check_gate(g):
    need(isinstance(g, dict) and set(g) <= GATE_KEYS)
    need(g.get('certificate_sha256') is None or HEX.match(str(g['certificate_sha256'])))
    for k in ('certificate_valid', 'smearing_qualified', 'manifest_verified', 'pseudopotentials_bound'):
        need(isinstance(g.get(k), bool))
    need('register_missing' not in g or isinstance(g['register_missing'], bool))
    need(g.get('relaxation') in ('unknown', 'converged', 'exploratory'))
    need(g.get('geometry') in ('unknown', 'polished', 'mv'))
    w = g.get('smearing_width_Ry')
    need(w is None or (isinstance(w, (int, float)) and not isinstance(w, bool)))
    m = g.get('manifest')
    need(m is None or (isinstance(m, dict) and set(m) <= MANIFEST_KEYS))
    need(g.get('seed') is None or (isinstance(g['seed'], int) and not isinstance(g['seed'], bool)))
    need(g.get('construction') is None or isinstance(g['construction'], dict))
    if 'pseudopotentials' in g:
        check_hash_map(g['pseudopotentials'])
    for k in ('problems', 'reasons'):
        need(isinstance(g.get(k), list) and all(isinstance(x, str) for x in g[k]))
    return {'certificate_sha256': g.get('certificate_sha256'), 'certificate_valid': g['certificate_valid'],
            'relaxation': g['relaxation'], 'geometry': g['geometry'], 'smearing_qualified': g['smearing_qualified'],
            'manifest_verified': g['manifest_verified'], 'pseudopotentials_bound': g['pseudopotentials_bound'],
            'problem_categories': sorted({cat(x, PROBLEM_CATS) for x in g['problems']}),
            'reason_categories': sorted({cat(x, REASON_CATS) for x in g['reasons']})}


def read_clean(out, err):
    need(os.path.getsize(err) == 0)
    with open(out, 'rb') as f:
        raw = f.read()
    need(len(raw) < 2_000_000)
    return raw.decode('utf-8').replace('\r\n', '\n')              # Windows console line endings


def v_certify(rc, out, err, cert):
    need(rc == 0)
    o = json.loads(read_clean(out, err))
    need(isinstance(o, dict) and set(o) == CERT_KEYS)
    need(o['certificate'] == cert and o['source'] in ('xml', 'table', 'text') and o['mode'] in ('bulk', 'slab', 'interface'))
    check_hash_map(o['run_files'])
    check_hash_map(o['pseudopotentials'])
    need(isinstance(o['geometry_sha256'], str) and HEX.match(o['geometry_sha256']))
    return {'source': o['source'], 'mode': o['mode'], 'run_files': o['run_files'], 'geometry_sha256': o['geometry_sha256'],
            'pseudopotentials': o['pseudopotentials'], 'gate': check_gate(o['gate'])}


def v_validate(rc, out, err):
    need(rc in (0, 1))
    text = read_clean(out, err)
    i = text.rfind('\nGATE: ')
    need(i > 0)
    tail = text[i + 1:].rstrip('\n').split('\n')
    need(len(tail) == 3 and tail[0] in ('GATE: VALID', 'GATE: NOT VALID') and tail[1].startswith('    problems: ')
         and tail[2].startswith('    qualification checks: '))
    need((rc == 0) == (tail[0] == 'GATE: VALID'))
    o = json.loads(text[:i])
    need(isinstance(o, dict) and set(o) <= GATE_KEYS | {'provenance'})
    pv = o.pop('provenance', None)
    need(isinstance(pv, dict) and set(pv) <= PROV_KEYS)
    need(pv.get('code_sha256') == RC7_CODE and isinstance(pv.get('code_version'), str) and NAME.match(pv['code_version']))
    reg = pv.get('register')
    need(isinstance(reg, dict) and set(reg) == {'file', 'sha256'} and reg['file'] == 'HYPOTHESIS_REGISTER.md'
         and isinstance(reg['sha256'], str) and HEX.match(reg['sha256']))
    need(pv.get('inputs') == [])
    rf = pv.get('run_files')
    need(isinstance(rf, dict))
    for k, v in rf.items():
        need(NAME.match(k) and isinstance(v, dict) and set(v) <= {'sha256', 'origin'} and HEX.match(str(v.get('sha256')))
             and NAME.match(str(v.get('origin', 'file'))))
    need(HEX.match(str(pv.get('geometry_sha256'))) and HEX.match(str(pv.get('certificate_sha256'))))
    need(pv.get('source') in ('xml', 'table', 'text') and pv.get('mode') in ('bulk', 'slab', 'interface'))
    return {'GATE': tail[0][6:], 'gate': check_gate(o), 'code_sha256': pv['code_sha256'],
            'register_sha256': reg['sha256'], 'certificate_sha256': pv['certificate_sha256'],
            'run_files': {k: v['sha256'] for k, v in rf.items()}, 'geometry_sha256': pv['geometry_sha256']}


def v_f9(rc, out, err, js):
    sys.path.insert(0, os.path.dirname(F9))
    import cert_assert as CA                                    # the frozen v15 key allowlists
    need(rc in (0, 1, 2))
    read_clean(out, err)
    with open(js, encoding='utf-8') as f:
        o = json.load(f)
    need(isinstance(o, dict) and set(o) <= set(CA.OUTPUT_KEYS))
    for b in (o.get('blocks') or {}).values():
        need(isinstance(b, dict) and set(b) <= set(CA.BLOCK_KEYS))
    need(o.get('verdict') in ('CLAIMS_OK', 'DOWNGRADE_REQUIRED', 'MALFORMED', 'SIGHT_ABORT'))
    need({'CLAIMS_OK': 0, 'DOWNGRADE_REQUIRED': 1}.get(o['verdict'], 2) == rc)
    need(HEX.match(str(o.get('checker_sha256'))) and HEX.match(str(o.get('writer_sha256'))))
    blocks = {k: {x: b.get(x) for x in ('claimed', 'hash_binding', 'semantic', 'verdict', 'permitted', 'reasons')}
              for k, b in (o.get('blocks') or {}).items()}
    return {'verdict': o['verdict'], 'exit': rc, 'checker': o.get('checker'), 'checker_sha256': o['checker_sha256'],
            'writer_sha256': o['writer_sha256'], 'structure_problems': o.get('structure_problems'), 'blocks': blocks}


def certify_args(cell, job, cert, claims):
    a = [PY, '-E', '-B', '-m', 'analysis', 'certify', tarball(cell, job), '--name', cell, '--out', cert,
         '--spec', os.path.join('specs', f'spec_{cell}.json'), '--compiled-by', COMPILED_BY]
    for k, v in claims.items():
        a += [f'--{k}', v, f'--{k}-evidence']
    return a


def tarball(cell, job):
    return os.path.join(ARCH, cell, f'final_{job}', 'final_small.tar.gz')


def one_cell(cell, job):
    d = os.path.join(AUD, cell)
    os.makedirs(d, exist_ok=True)
    res = {'cell': cell, 'final': job, 'tarball_sha256': sha(tarball(cell, job)), 'rounds': []}
    claims = dict(CLAIMS)
    for rnd in (1, 2, 3):
        cert = os.path.join(d, f'cert_{cell}_final_{job}_r{rnd}.json')
        tag = f'{cell}_r{rnd}'
        r = {'round': rnd, 'claims': dict(claims)}
        rc, out, err = run(tag + '_certify', certify_args(cell, job, cert, claims))
        r['certify'] = v_certify(rc, out, err, cert)
        r['certificate_sha256'] = sha(cert)
        rc, out, err = run(tag + '_validate', [PY, '-E', '-B', '-m', 'analysis', 'validate-cert', tarball(cell, job),
                                               '--name', cell, '--certificate', cert])
        r['validate'] = v_validate(rc, out, err)
        need(r['validate']['certificate_sha256'] == r['certificate_sha256'])
        js = os.path.join(d, f'f9_{cell}_r{rnd}.json')
        rc, out, err = run(tag + '_f9', [PY, '-I', '-B', F9, cert, '--json', js])
        r['f9'] = v_f9(rc, out, err, js)
        r['f9_json_sha256'] = sha(js)
        res['rounds'].append(r)
        if r['f9']['verdict'] != 'CLAIMS_OK':
            if r['f9']['verdict'] != 'DOWNGRADE_REQUIRED':
                break
            new = {}
            for k, v in claims.items():                         # recompile with the permitted statuses, never stronger
                p = (r['f9']['blocks'].get(k) or {}).get('permitted')
                if p not in (None, 'unknown', 'pending'):
                    need(p in ('converged', 'exploratory', 'mv', 'polished'))
                    new[k] = p
            claims = new
            continue
        break
    return res


def step0():
    pc = os.path.join(AMORPH, 'analysis', '__pycache__')
    if os.path.isdir(pc):
        shutil.rmtree(pc)
    out = {'pycache_deleted': not os.path.isdir(pc)}
    rc, o, e = run('step0_fingerprint', [PY, '-E', '-B', '-c', 'from analysis import certify; print(certify.code_fingerprint())'])
    out['code_fingerprint_ok'] = rc == 0 and os.path.getsize(e) == 0 and open(o).read().strip() == RC7_CODE
    rc, o, e = run('step0_crystalline', [PY, '-E', '-B', '-m', 'analysis', 'crystalline', '--json',
                                         os.path.join(AUD, 'step0_crystalline.json')])
    with open(o, encoding='utf-8', errors='replace') as f:
        out['crystalline_REPRODUCED'] = rc == 0 and 'REPRODUCED' in f.read()
    rc, o, e = run('step0_f9_selftest', [PY, '-I', '-B', F9, '--self-test'])
    with open(e, encoding='utf-8', errors='replace') as f:
        t = f.read()
    m = re.search(r'\nRan (\d+) tests', t)
    out['f9_selftest'] = {'exit': rc, 'ran': int(m.group(1)) if m else None, 'ok': rc == 0 and t.rstrip().endswith('OK')}
    out['f9_files'] = {n: sha(os.path.join(AMORPH, 'f9_checker', n))[:8] for n in F9_FROZEN}
    out['f9_frozen_ok'] = out['f9_files'] == F9_FROZEN
    out['register_sha256'] = sha(REGISTER)
    out['venv_python'] = PY
    return out


def main():
    os.makedirs(AUD, exist_ok=True)
    if sys.argv[1:] == ['step0']:
        s = step0()
        with open(os.path.join(AUD, 'step0.json'), 'w', encoding='utf-8', newline='\n') as f:
            json.dump(s, f, indent=1)
        print(json.dumps(s, indent=1))
        return
    need(sys.argv[1:] == ['cells'])
    summary = []
    for cell, job in CELLS:
        try:
            summary.append(one_cell(cell, job))
        except (Unexpected, ValueError, KeyError, TypeError, OSError):
            summary.append({'cell': cell, 'final': job, 'ABORTED': 'unexpected output; sealed, nothing displayed'})
    with open(os.path.join(AUD, 'summary.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(summary, f, indent=1)
    with open(os.path.join(AUD, 'hash_table.txt'), 'w', encoding='utf-8', newline='\n') as f:
        for root, _, files in os.walk(AUD):
            for n in sorted(files):
                p = os.path.join(root, n)
                if n not in ('hash_table.txt',):
                    f.write(f'{sha(p)}  {os.path.relpath(p, AUD)}\n')
    for s in summary:
        if 'ABORTED' in s:
            print(f"{s['cell']} {s['final']}: ABORTED (sealed)")
            continue
        for r in s['rounds']:
            g = r['validate']
            print(f"{s['cell']} {s['final']} round {r['round']} claims {r['claims']}: certify gate valid="
                  f"{r['certify']['gate']['certificate_valid']}; validate-cert {g['GATE']}; F9 {r['f9']['verdict']} "
                  + '; '.join(f"{k}: {b['claimed']}->{b['permitted']}" for k, b in r['f9']['blocks'].items()))


if __name__ == '__main__':
    main()
