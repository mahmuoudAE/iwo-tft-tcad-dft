"""Shared helpers for the tests. qualification() builds the run qualification that certify.validate() returns for a
valid certificate (the certificate gate itself is tested in test_certify.py)."""
import itertools

from analysis.certify import qualification_reasons, unqualified
from analysis.report import cell_result
from analysis.section1 import Section1

_SEED = itertools.count(1000)


def manifest(nex=1, kind='W-doped', seed=None):
    return {'kind': kind, 'N_ex': nex, 'seed': next(_SEED) if seed is None else seed}


def pp_hash(name):
    """Synthetic UPF content hash (the same as synth.write_lineage writes)."""
    import hashlib
    return hashlib.sha256(str(name).encode()).hexdigest()


def pp_certified(data, override=None):
    """{UPF file: certified sha256} for the species of a synthetic run (override: {file: hash})."""
    files = sorted({s['pseudo_file'] for s in (data.settings or {}).get('species', []) if s.get('pseudo_file')})
    return {f: (override or {}).get(f, pp_hash(f)) for f in files}


def qualification(man=None, relaxation='converged', smearing=True, geometry='polished', valid=True, pseudos=None):
    q = {'certificate_sha256': f'cert-{next(_SEED)}', 'certificate_valid': valid, 'problems': [],
         'relaxation': relaxation, 'smearing_qualified': smearing, 'smearing_width_Ry': None, 'geometry': geometry,
         'manifest_verified': man is not None, 'manifest': man, 'seed': (man or {}).get('seed'),
         'pseudopotentials_bound': True, 'pseudopotentials': dict(pseudos or {}),
         'construction': (man or {}).get('construction')}
    q['reasons'] = qualification_reasons(q)
    return q


QUALIFIED = qualification(manifest())


def analyse(sc, nelec, name='aIWO_2p0_s1', nex=None, mode='auto', avg=None, w5d='normalised', man=None, **build):
    data = sc.build(nelec, **build)
    return Section1(data, sc.st, name=name, nex=nex, mode=mode, avg=avg, w5d_convention=w5d, manifest=man)


def result(sc, nelec, name='aIWO_2p0_s1', nex=1, kind='W-doped', q=None, avg=None, certified=True, seed=None,
           geometry='polished', relaxation='converged', smearing_ok=True, source='synthetic', **build):
    """A cell result; certified=True gives a valid qualification with a manifest (kind, N_ex = nex, unique seed).
    source='xml' marks a synthetic run as an XML-pair run (C6 input tests)."""
    man = manifest(nex, kind, seed) if certified else None
    data = sc.build(nelec, **build)
    if q is None:
        q = qualification(man, relaxation=relaxation, smearing=smearing_ok, geometry=geometry,
                          pseudos=pp_certified(data)) if certified else unqualified('no certificate given')
    c = Section1(data, sc.st, name=name, nex=None if man else nex, avg=avg, manifest=man)
    return cell_result(c, source, qual=q)
