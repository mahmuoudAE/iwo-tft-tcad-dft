"""Data sheets for every CERN run folder of 20 Sep - 7 Oct 2026 in qe_workflow/cern_htcondor/results (41 folders).

Reads every file of each folder (loose files AND the members of every *.tar.gz / *.tgz, compared byte-for-byte with the
loose copies), parses every pw.x / projwfc.x / pp.x / average.x output, pw.x input and template, driver log, step script,
planar average and PDOS set, and the HTCondor status history; writes per run
   out/<run>.json          compact machine-readable record (no per-atom/per-k arrays)
   out/<run>_arrays.json.gz eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom
and returns everything for sheets.py. All crystalline (no amorphous cell is in these folders). Read-only.
Usage: python extract_runs.py
"""
import gzip
import hashlib
import io
import json
import re
import sys
import tarfile
from pathlib import Path

import numpy as np

import pwparse as pp

HERE = Path(__file__).resolve().parent
QE = HERE.parents[1]
RES = QE / 'cern_htcondor' / 'results'
OUT = HERE / 'out'
BIG = 300 * 1024 ** 2          # tar members above this are streamed separately (the 9.4 GB runaway scf.out)

RUNS = ['slab1_v15', 'slab1_v25', 'slab1_v35', 'gpu_bench_v15', 'iwo_W8b', 'iwo_W8b_partial', 'iwo_W24d', 'iwo_W24d_partial',
        'slab1_relax_gpu', 'cpu_relax_snapshots', 'slab1r_final_cpu', 'iwo_slab1_W24d_x1', 'iwo_slab1_final_cpu',
        'nc_pbe_bulk_e80', 'nc_pbe_bulk_e100', 'nc_pbe_slab1_e80', 'nc_hse_bulk_e80', 'nc_hse_bulk_f160_e80', 'nc_hse_bulk_q3_e80',
        'nc_hse_bulk_q3_f160_e80', 'nc_hse_slab1_e80', 'nc_hse_slab1_f160_e80', 'slab2_relax_c2', 'iwo_slab2_W24d_checkpoint',
        'slab2r_final_cpu_checkpoint', 'iwo_slab2_final_cpu', 'iwo_slab2_final_cpu_failed_pools', 'slab2r_pdos_cpu',
        'slabL1_relax_gpu', 'slabL2_relax_gpu', 'slabL1_relax_v2', 'slabL2_relax_v2', 'live_snapshots', 'canary_ckpt_checkpoint',
        'canary_cont', 'canary_cont_c1', 'canary_race', 'canary_race__cpu', 'canary_stuck', 'ckpt_write_test_checkpoint', 'failed_20260927a']
JOBNAME = {'iwo_W8b_partial': 'iwo_W8b', 'iwo_W24d_partial': 'iwo_W24d', 'iwo_slab2_W24d_checkpoint': 'iwo_slab2_W24d',
           'slab2r_final_cpu_checkpoint': 'slab2r_final_cpu', 'iwo_slab2_final_cpu_failed_pools': 'iwo_slab2_final_cpu',
           'canary_ckpt_checkpoint': 'canary_ckpt'}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def status_history():
    seen = {}
    for l in open(RES / 'status_history.jsonl', encoding='utf-8'):
        try:
            r = json.loads(l)
        except Exception:
            continue
        for j in r['jobs']:
            k = (j['job'], j['id'])
            e = seen.setdefault(k, {'job': j['job'], 'id': j['id'], 'first': r['time'], 'last': r['time'], 'samples': 0, 'states': {},
                                    'cpus': j.get('cpus'), 'gpus': j.get('gpus'), 'gpu_hw': set(), 'cpu_hw': set(), 'max_scf_it': 0, 'max_bfgs': 0, 'steps': []})
            e['last'] = r['time']; e['samples'] += 1
            e['states'][str(j['state'])] = e['states'].get(str(j['state']), 0) + 1
            for h in ('gpu_hw', 'cpu_hw'):
                if j.get(h) not in (None, 'NA', 'none'):
                    e[h].add(j[h])
            e['max_scf_it'] = max(e['max_scf_it'], j.get('scf_it') or 0); e['max_bfgs'] = max(e['max_bfgs'], j.get('bfgs') or 0)
            if j.get('step') not in (None, 'NA') and (not e['steps'] or e['steps'][-1] != j['step']):
                e['steps'].append(j['step'])
    for e in seen.values():
        e['gpu_hw'], e['cpu_hw'] = sorted(e['gpu_hw']), sorted(e['cpu_hw'])
    return seen


def collect(run):
    """All documents of a run folder: {relpath: {'bytes', 'src', 'size', 'sha256'}} plus tar member bookkeeping."""
    d = RES / run
    docs, tars, pdos_dirs = {}, [], {}
    for f in sorted(d.rglob('*')):
        if f.is_dir():
            continue
        rp = f.relative_to(d).as_posix()
        if '/pdos/' in '/' + rp or rp.startswith('pdos/'):
            pdos_dirs.setdefault(str(f.parent.relative_to(d).as_posix()), []).append(f)
            continue
        if f.name.endswith(('.tar.gz', '.tgz')):
            tars.append(f)
            continue
        b = f.read_bytes()
        docs[rp] = {'bytes': b, 'src': 'loose', 'size': len(b), 'sha256': sha(b)}
    tar_info = []
    for t in tars:
        base = t.parent.relative_to(d).as_posix()
        base = '' if base == '.' else base + '/'
        rec = {'tarball': t.relative_to(d).as_posix(), 'size': t.stat().st_size, 'sha256': sha(t.read_bytes()), 'members': []}
        with tarfile.open(t, 'r:gz') as tf:
            for m in tf.getmembers():
                if not m.isfile():
                    continue
                rp = base + m.name
                mr = {'name': m.name, 'size': m.size}
                if 'pdos_atm#' in m.name or m.name.endswith('pdos_tot'):
                    mr['kind'] = 'pdos'
                    rec['members'].append(mr)
                    continue
                if m.size > BIG:
                    mr['kind'] = 'too large: streamed separately (stream_runaway.py)'
                    rec['members'].append(mr)
                    continue
                b = tf.extractfile(m).read()
                mr['sha256'] = sha(b)
                if rp in docs:
                    mr['equals_loose'] = docs[rp]['sha256'] == mr['sha256']
                else:
                    key = rp if rp not in docs else rp + ' [tar]'
                    docs[key] = {'bytes': b, 'src': 'tar:' + rec['tarball'], 'size': len(b), 'sha256': mr['sha256']}
                    mr['equals_loose'] = None
                rec['members'].append(mr)
        tar_info.append(rec)
    return docs, tar_info, pdos_dirs


def text(doc):
    return doc['bytes'].decode('utf-8', errors='replace')


def classify(name, t):
    if 'Program PWSCF' in t:
        return 'pw_out'
    if 'Program PROJWFC' in t:
        return 'projwfc_out'
    if 'Program POST-PROC' in t:
        return 'pp_out'
    if 'Program AVERAGE' in t:
        return 'avg_out'
    if name.endswith('_avg.dat'):
        return 'avg_dat'
    if name.endswith('driver.log'):
        return 'driver'
    if name.endswith('steps.sh'):
        return 'steps'
    if re.search(r'&control', t, re.I) and (name.endswith('.in') or '.in.' in name or name.endswith('.tmpl') or 'vcrelax_prev' in name):
        return 'pw_in' if not name.endswith('.tmpl') else 'pw_tmpl'
    if re.search(r'&(projwfc|inputpp)', t, re.I):
        return 'post_in'
    if name.endswith('.in') and len(t) < 200:
        return 'avg_in'
    if 'There are not enough slots' in t or 'PRRTE' in t or 'MPI_INIT failed' in t:
        return 'mpi_error'
    return 'other'


def vacuum_from_avg(lines, struct):
    a = np.loadtxt(io.StringIO('\n'.join(lines)))
    z, vp = a[:, 0] * pp.BOHR, a[:, 1] * pp.RY
    out = {'n_points': int(len(z)), 'V_min_eV': round(float(vp.min()), 4), 'V_max_eV': round(float(vp.max()), 4),
           'window_A': round(float(a[1, 0] - a[0, 0]) * pp.BOHR, 5), 'z_mean_V_eV': round(float(vp.mean()), 5)}
    if struct is not None:
        cell, sym, frac = struct
        c = float(np.linalg.norm(cell[2]))
        za = np.mod((frac @ cell)[:, 2], c)
        dist = np.min(np.abs(((z[:, None] - za[None, :]) + c / 2) % c - c / 2), axis=1)
        w = dist > 5.0
        if w.any():
            top = za.max()
            zu = np.where(z > top, z, z + c)[w]
            slope = np.polyfit(zu, vp[w], 1)[0] if w.sum() > 3 else 0.0
            out.update({'E_vac_eV': round(float(vp[w].mean()), 5), 'vacuum_flatness_meV': round(float(vp[w].max() - vp[w].min()) * 1000, 3),
                        'vacuum_slope_meV_per_A': round(float(slope) * 1000, 4)})
    return out


def pdos_summary(files, efermi):
    tot = next((f for f in files if f.name.endswith('pdos_tot')), None)
    res = {'n_files': len(files)}
    if tot is not None:
        a = np.loadtxt(tot, comments='#')
        res['E_window_eV'] = [float(a[0, 0]), float(a[-1, 0])]; res['dE_eV'] = round(float(a[1, 0] - a[0, 0]), 4)
        res['integral_dos_window'] = round(float(np.trapezoid(a[:, 1], a[:, 0])), 3)
        if efermi is not None:
            m = a[:, 0] <= efermi
            res['integral_dos_below_EF_or_VBM'] = round(float(np.trapezoid(a[m, 1], a[m, 0])), 3) if m.sum() > 1 else 0.0
            res['reference_energy_eV'] = efermi
    by = {}
    rx = re.compile(r'pdos_atm#(\d+)\((\w+)\)_wfc#(\d+)\((\w)\)$')
    for f in files:
        m = rx.search(f.name)
        if not m:
            continue
        a = np.loadtxt(f, comments='#')
        key = f'{m.group(2)} {m.group(4)}'
        e = by.setdefault(key, {'files': 0, 'integral_window': 0.0, 'integral_below_ref': 0.0})
        e['files'] += 1
        e['integral_window'] += float(np.trapezoid(a[:, 1], a[:, 0]))
        if efermi is not None:
            mm = a[:, 0] <= efermi
            if mm.sum() > 1:
                e['integral_below_ref'] += float(np.trapezoid(a[mm, 1], a[mm, 0]))
    res['by_element_l'] = {k: {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in sorted(by.items())}
    return res


def step_table(r):
    keys = ['iterations', 'converged_iterations', 'acc_final_Ry', 'E_Ry', 'E_bang2_Ry', 'enthalpy_new_Ry', 'mTS_Ry', 'E_F_eV', 'HOMO_eV', 'LUMO_eV',
            'total_magnetization', 'absolute_magnetization', 'force_max_component_Ry_bohr', 'force_rms_component_Ry_bohr', 'total_force_Ry_bohr',
            'total_scf_correction_Ry_bohr', 'pressure_kbar', 'volume_A3', 'cell_A', 'bfgs_steps', 'bfgs_scf_cycles', 'trust_radius_bohr',
            'bfgs_energy_error_Ry', 'bfgs_gradient_error', 'bfgs_cell_gradient_error_kbar', 'negative_rho', 'not_converged', 'beta']
    return [{k: s[k] for k in keys if k in s} for s in r['steps']]


def run_one(run, sh):
    docs, tars, pdos_dirs = collect(run)
    rec = {'run': run, 'folder': f'cern_htcondor/results/{run}', 'files': [], 'tarballs': tars, 'pw': {}, 'inputs': {}, 'templates': {},
           'projwfc': {}, 'pp_avg': {}, 'avg_dat': {}, 'pdos': {}, 'driver': {}, 'steps_sh': {}, 'other': {}, 'mpi_errors': {}}
    arrays = {}
    kinds = {}
    for name, doc in sorted(docs.items()):
        t = text(doc)
        k = classify(name, t)
        kinds[name] = k
        rec['files'].append({'path': name, 'size': doc['size'], 'sha256_16': doc['sha256'][:16], 'src': doc['src'], 'kind': k})
    # inputs first (geometry of the inputs)
    structs = {}
    for name, k in kinds.items():
        t = text(docs[name])
        if k in ('pw_in', 'pw_tmpl'):
            inp = pp.parse_input(t)
            st = pp.struct_from_input(inp)
            entry = {'namelists': inp['namelists'], 'cards': {c: v for c, v in inp['cards'].items() if c != 'ATOMIC_POSITIONS'}}
            if 'ATOMIC_POSITIONS' in inp['cards']:
                ap = inp['cards']['ATOMIC_POSITIONS']
                entry['atomic_positions_summary'] = {'unit': ap['unit'], 'n': len(ap['labels']), 'labels': sorted(set(ap['labels'])),
                                                     'n_constrained': ap['n_constrained']}
            if st is not None:
                structs[name] = st
                entry['geometry'] = pp.geometry(*st)
            (rec['inputs'] if k == 'pw_in' else rec['templates'])[name] = entry
        elif k == 'driver':
            rec['driver'][name] = pp.parse_driver(t.splitlines())
        elif k == 'steps':
            rec['steps_sh'][name] = t.strip()
        elif k == 'post_in' or k == 'avg_in':
            rec['pp_avg'].setdefault(name, {})['input'] = t.strip()
        elif k == 'mpi_error':
            Lm = t.replace('\x00', '').splitlines()
            rec['mpi_errors'][name] = {'key_lines': [l.strip() for l in Lm if re.search(r'not enough slots|slots that were requested|sm" BTL|MPI_INIT failed|mca_bml|Host:|Component:', l)][:8],
                                       'warnings': pp.warnings(Lm)}
        elif k == 'other':
            rec['other'][name] = t.strip()[:600] if doc_is_text(docs[name]) else f'{docs[name]["size"]} bytes'
    # pw outputs
    for name, k in kinds.items():
        if k != 'pw_out':
            continue
        L = text(docs[name]).splitlines()
        r, a = pp.parse_pw(L)
        P = r['params']
        nel = pp.fnum(P.get('number of electrons', '')) if P.get('number of electrons') else None
        smear = bool(r['kpoints'].get('smearing'))
        last = r['steps'][-1] if r['steps'] else {}
        ef = last.get('E_F_eV')
        d = name.rsplit('/', 1)[0] + '/' if '/' in name else ''
        if ef is None and r.get('calc_type') == 'bands':
            # Fermi energy of the SCF of the same run (metallic W cells)
            for cand in ('scf_k4.out', 'scf.out'):
                if d + cand in docs:
                    rr, _ = pp.parse_pw(text(docs[d + cand]).splitlines())
                    if rr['steps'] and rr['steps'][-1].get('E_F_eV') is not None:
                        ef = rr['steps'][-1]['E_F_eV']; break
        eig = a['eig']
        bands = None
        if eig and nel:
            if eig.get('spin_down_start'):
                n2 = eig['spin_down_start']
                bands = {'spin_up': pp.band_analysis({'eig_eV': eig['eig_eV'][:n2]}, nel, ef, smear),
                         'spin_down': pp.band_analysis({'eig_eV': eig['eig_eV'][n2:]}, nel, ef, smear)}
            else:
                bands = pp.band_analysis(eig, nel, ef, smear)
        entry = {'header': r['header'], 'params': P, 'pseudos': r['pseudos'], 'pseudo_rereads': r.get('pseudo_rereads', 0), 'species': r['species'],
                 'symmetry': r.get('symmetry'), 'kpoints': r['kpoints'], 'fft': r['fft'], 'ram': {k_: v for k_, v in r['ram'].items() if k_ != 'components'},
                 'ram_components': r['ram'].get('components'), 'start': r.get('start'), 'calc_type': r.get('calc_type', 'scf/relax'),
                 'bands_calc': r.get('bands_calc'), 'n_scf_steps': len(r['steps']), 'steps': step_table(r), 'final_step': last, 'bfgs': r['bfgs'],
                 'exx': r['exx'], 'timing': r['timing'], 'terminated': r.get('terminated'), 'done': r['done'], 'messages': r['messages'][:10], 'errors': r.get('errors'),
                 'warnings': r['warnings'], 'bands': bands, 'n_lines': len(L)}
        if r['final_coordinates']:
            ref_name = next((d + c for c in ('vcrelax_initial.in', 'relax.in', 'vcrelax.in') if d + c in structs), None)
            cell0 = structs[ref_name][0] if ref_name else None
            try:
                stf = pp.struct_from_final(r['final_coordinates'], cell0)
                entry['final_geometry'] = pp.geometry(*stf, ref=structs.get(ref_name))
                entry['final_geometry']['reference_input'] = ref_name
                entry['final_coordinates_line'] = r['final_coordinates']['line']
                structs[name + '#final'] = stf
            except Exception as ex:   # noqa: BLE001
                entry['final_geometry'] = f'unreadable: {ex}'
        rec['pw'][name] = entry
        arrays[name] = {'scf_accuracy_traces': a['scf_accuracy'], 'eig': eig, 'forces_final_Ry_bohr': a['forces_final'], 'kpts_scf': a['kpts_scf']}
    # consistency: SCF input geometry vs relax final geometry in the same directory
    for name, st in list(structs.items()):
        if not name.endswith('#final'):
            continue
        d = name.split('#')[0].rsplit('/', 1)[0] + '/' if '/' in name else ''
        for cand in ('scf.in', 'scf_k4.in', 'bands.in', 'spin_k3.in'):
            if d + cand in structs and len(structs[d + cand][1]) == len(st[1]):
                c1, s1, f1 = structs[d + cand]; c2, s2, f2 = st
                df = f1 - f2; df -= np.rint(df)
                rec.setdefault('geometry_consistency', {})[f'{d}{cand} vs final of {name.split("#")[0]}'] = {
                    'max_pos_diff_A': round(float(np.abs(df @ c1).max()), 6), 'max_cell_diff_A': round(float(np.abs(c1 - c2).max()), 6)}
    # projwfc, pp, average
    for name, k in kinds.items():
        L = text(docs[name]).splitlines()
        if k == 'projwfc_out':
            pr = pp.parse_projwfc(L)
            low = pr.pop('lowdin')
            d = name.rsplit('/', 1)[0] + '/' if '/' in name else ''
            sym = None
            for cand in ('scf.in', 'scf_k4.in'):
                if d + cand in structs:
                    sym = structs[d + cand][1]; break
            if sym and low:
                by = {}
                for at, v in low.items():
                    e = sym[at - 1]
                    by.setdefault(e, []).append(v)
                pr['lowdin_by_element'] = {e: {'n': len(v), **{q: {'mean': round(float(np.mean([x.get(q, 0) for x in v])), 4),
                                                                      'min': round(float(np.min([x.get(q, 0) for x in v])), 4),
                                                                      'max': round(float(np.max([x.get(q, 0) for x in v])), 4)}
                                                                  for q in ('total', 's', 'p', 'd')}} for e, v in by.items()}
                pr['lowdin_total_sum'] = round(sum(v['total'] for v in low.values()), 3)
            rec['projwfc'][name] = pr
            arrays.setdefault('_lowdin', {})[name] = low
        elif k in ('pp_out', 'avg_out'):
            rec['pp_avg'].setdefault(name, {})['output'] = {'done': any('JOB DONE' in l for l in L),
                                                             'key_lines': [l.strip() for l in L if re.search(r'plot_num|Writing|Reading|POST-PROC|AVERAGE|Planar|Macroscopic|Calling|terminated', l)][:12],
                                                             'warnings': pp.warnings(L)}
        elif k == 'avg_dat':
            d = name.rsplit('/', 1)[0] + '/' if '/' in name else ''
            st = structs.get(d + 'scf.in')
            rec['avg_dat'][name] = vacuum_from_avg(L, st)
    # PDOS
    for dname, files in pdos_dirs.items():
        d = '' if dname in ('.', 'pdos') else dname.rsplit('/', 1)[0] + '/'
        ref = None
        for cand in ('scf_k4.out', 'scf.out'):
            if d + cand in rec['pw']:
                fs = rec['pw'][d + cand]['final_step']
                ref = fs.get('E_F_eV') if fs.get('E_F_eV') is not None else fs.get('HOMO_eV')
                break
        rec['pdos'][dname] = pdos_summary(files, ref)
    # vacuum-referenced levels
    for name, v in rec['avg_dat'].items():
        d = name.rsplit('/', 1)[0] + '/' if '/' in name else ''
        if 'E_vac_eV' in v and d + 'scf.out' in rec['pw']:
            fs = rec['pw'][d + 'scf.out']['final_step']
            if fs.get('HOMO_eV') is not None and fs.get('LUMO_eV') is not None:
                v['IP_eV'] = round(v['E_vac_eV'] - fs['HOMO_eV'], 4); v['EA_eV'] = round(v['E_vac_eV'] - fs['LUMO_eV'], 4)
            if fs.get('E_F_eV') is not None:
                v['work_function_eV'] = round(v['E_vac_eV'] - fs['E_F_eV'], 4)
    # status history
    jn = JOBNAME.get(run, run)
    rec['condor'] = [dict(v, gpu_hw=v['gpu_hw'], cpu_hw=v['cpu_hw']) for (j, i), v in sh.items() if j == jn or (run == 'live_snapshots' and j.startswith(('slab2', 'iwo_slab2')))]
    return rec, arrays


def doc_is_text(doc):
    try:
        doc['bytes'][:2000].decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False


def main(runs=None):
    OUT.mkdir(exist_ok=True)
    sh = status_history()
    for run in runs or RUNS:
        rec, arrays = run_one(run, sh)
        (OUT / f'{run}.json').write_text(json.dumps(rec, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o)))
        with gzip.open(OUT / f'{run}_arrays.json.gz', 'wt', encoding='utf-8') as g:
            json.dump(arrays, g, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
        print(run, 'files', len(rec['files']), 'pw', len(rec['pw']), 'inputs', len(rec['inputs']), 'projwfc', len(rec['projwfc']), 'tar', len(rec['tarballs']))


if __name__ == '__main__':
    main(sys.argv[1:] or None)
