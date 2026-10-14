"""A44 addendum 1: certify / validate-cert / F9 v18 per cell with the built relaxation_lineage records as evidence.
Reuses the pinned A44 runner (annex A44_audit_runner.py e4593b06: sealing, allowlist validator, rounds) with three
overrides: F9 = frozen v18 (D-49), the audit folder, and the claims/evidence per cell (intent corrected per the A44
correction: relaxation converged for all seven; geometry mv only for aIWO_1p0_s1 and aIWO_0p7_s1)."""
import importlib.util
import json
import os
import sys

REPO = r'C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\iwo-tft-research-private'
spec = importlib.util.spec_from_file_location('a44', os.path.join(REPO, 'codex', 'work_chat', 'annex', 'A44_audit_runner.py'))
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
assert R.sha(spec.origin) == 'e4593b0664ca213ec41e82e4afed75b448a7dcad8f6025f68d4da7235a0cb6df'

LIN = r'C:\Users\moham\iwo_release_audit_20261014\lineage'
R.AUD = os.path.join(LIN, 'certs')
R.F9 = os.path.join(REPO, 'compute', 'amorph', 'f9_checker_v18', 'cert_assert.py')
R.COMPILED_BY = 'A44 addendum 1 lineage audit'
MV = ('aIWO_1p0_s1', 'aIWO_0p7_s1')
EVID = {}


def certify_args(cell, job, cert, claims):
    a = [R.PY, '-E', '-B', '-m', 'analysis', 'certify', R.tarball(cell, job), '--name', cell, '--out', cert,
         '--spec', os.path.join('specs', f'spec_{cell}.json'), '--compiled-by', R.COMPILED_BY]
    rec = EVID.get(cell)
    for k, v in claims.items():
        a += [f'--{k}', v, f'--{k}-evidence'] + ([rec] if rec else [])
    return a


R.certify_args = certify_args


def main():
    build = {r['cell']: r for r in json.load(open(os.path.join(LIN, 'lineage_build_summary.json'), encoding='utf-8'))}
    out = []
    for cell, job in R.CELLS:
        rec = os.path.join(LIN, cell, f'relaxation_lineage_{cell}.json')
        if build[cell]['record_sha256']:
            assert R.sha(rec) == build[cell]['record_sha256']
            EVID[cell] = rec
        R.CLAIMS = {'relaxation': 'converged', **({'geometry': 'mv'} if cell in MV else {})}
        try:
            res = R.one_cell(cell, job)
        except (R.Unexpected, ValueError, KeyError, TypeError, OSError):
            res = {'cell': cell, 'final': job, 'ABORTED': 'unexpected output; sealed, nothing displayed'}
        res['lineage_record'] = build[cell]['status']
        out.append(res)
    with open(os.path.join(R.AUD, 'summary.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, indent=1)
    for s in out:
        if 'ABORTED' in s:
            print(s['cell'], 'ABORTED (sealed)')
            continue
        r1 = s['rounds'][0]
        print(f"{s['cell']}: record [{s['lineage_record']}]; round 1 {r1['claims']}: GATE {r1['validate']['GATE']}, F9 "
              f"{r1['f9']['verdict']} " + '; '.join(f"{k} {b['claimed']}->{b['permitted']}" for k, b in r1['f9']['blocks'].items())
              + f"; rounds {len(s['rounds'])}, last F9 {s['rounds'][-1]['f9']['verdict']}")


if __name__ == '__main__':
    main()
