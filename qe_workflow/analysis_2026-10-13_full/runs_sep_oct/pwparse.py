"""Comprehensive readers for the Sep-Oct 2026 crystalline QE runs (pw.x 7.3.1/7.5 scf, relax, vc-relax, bands, HSE;
projwfc.x; pp.x; average.x; pw.x inputs; driver logs). Written for runs_sep_oct (independent of earlier scripts).

parse_pw(lines) returns everything a reader of the output would note: header/parallelisation, echoed parameters,
pseudopotentials (file, MD5, type, Z), symmetry, k points, FFT grids, RAM estimates, every SCF step (iterations,
accuracy trace, energy and its decomposition, Fermi/HOMO-LUMO, magnetisation, negative rho, forces summary, stress,
BFGS bookkeeping, cell and volume), final eigenvalues and occupations, EXX cycles, timing table, warnings, completion.
Large per-atom/per-iteration arrays go to a separate 'arrays' dict (written gzipped by the caller).
"""
import math
import re

import numpy as np

RY = 13.605693122994
BOHR = 0.529177210903
NUM = re.compile(r'-?\d+\.\d*(?:[eEdD][-+]?\d+)?|-?\d+(?:[eEdD][-+]?\d+)?')
MASS = {'In': 114.818, 'O': 15.999, 'W': 183.84, 'H': 1.008}


def nums(s):
    return [float(x.replace('d', 'e').replace('D', 'e')) for x in NUM.findall(re.sub(r'(?<=\d)-', ' -', s))]


def fnum(s):
    v = nums(s)
    return v[0] if v else None


WARN_PATTERNS = [('message_from_routine', r'Message from routine'), ('warning', r'[Ww]arning|WARNING'),
                 ('c_bands_not_converged', r'c_bands:.*eigenvalues not converged'), ('scf_not_converged', r'convergence NOT achieved'),
                 ('error', r'Error in routine|%%%%%|\bERROR\b'),('ieee', r'ieee_|IEEE'), ('discouraged', r'DISCOURAGED|DEPRECATED'),
                 ('renormalized_wfc', r'renormalized'), ('scf_correction_large', r'SCF correction compared to forces is large'),
                 ('s_matrix', r'S matrix not positive definite|problems computing cholesky'),
                 ('max_steps', r'maximum number of steps has been reached'), ('bfgs_failed', r'bfgs failed|history already reset'),
                 ('trust_radius', r'trust radius too small'), ('not_enough_slots', r'not enough slots'), ('fortran_stop', r'FORTRAN STOP'),
                 ('killed', r'\bKilled\b|SIGTERM|SIGKILL|received signal'), ('max_seconds', r'Maximum CPU time exceeded'),
                 ('cuda_out_of_memory', r'CUDA_ERROR_OUT_OF_MEMORY|cuMemAlloc returned error'), ('accelerator_fatal', r'Accelerator Fatal Error'),
                 ('mpi_init_failed', r'MPI_INIT failed|mca_bml_base_open\(\) failed|"sm" BTL is no longer available'),
                 ('ucx_error', r'UCX\s+ERROR'), ('mpi_abort', r'MPI_ABORT was invoked|prterun has exited|mpirun detected that one or more processes exited')]


def warnings(lines, start=1):
    out = {}
    for name, rx in WARN_PATTERNS:
        r = re.compile(rx)
        hits = [(i + start, l.strip()[:200]) for i, l in enumerate(lines) if r.search(l)]
        if hits:
            out[name] = {'count': len(hits), 'first': hits[:3], 'last': hits[-1]}
    return out


def parse_pw(L):
    R = {'header': {}, 'params': {}, 'pseudos': [], 'species': [], 'kpoints': {}, 'fft': {}, 'ram': {}, 'steps': [], 'bfgs': {},
         'exx': {'cycles': []}, 'timing': {}, 'messages': [], 'final_coordinates': None, 'done': False}
    A = {'scf_accuracy': [], 'forces_final': None, 'eig': None, 'kpts_scf': []}
    H, P = R['header'], R['params']
    cur = None
    closed = True
    i = 0
    n = len(L)
    in_bands_calc = False

    def new_step():
        return {'iterations': 0, 'acc_trace': [], 'ecut': None, 'beta': None}
    while i < n:
        l = L[i]
        s = l.strip()
        # ---------------- header
        if 'Program PWSCF' in l:
            m = re.search(r'Program PWSCF (v\.\S+) starts on\s+(\S+) at\s+(.+)$', l)
            if m:
                H['version'], H['start_date'], H['start_time'] = m.group(1), m.group(2), m.group(3).strip()
        elif 'running on' in l and 'processor cores' in l:
            H['processor_cores'] = int(fnum(l.split('running on')[1]))
            H['parallel_mode'] = l.split('running on')[0].strip()
        elif s.startswith('Number of MPI processes'):
            H['mpi_processes'] = int(fnum(s))
        elif s.startswith('Threads/MPI process'):
            H['threads_per_mpi'] = int(fnum(s))
        elif 'MPI processes distributed on' in s:
            H['nodes'] = int(fnum(s))
        elif s.startswith('K-points division'):
            H['npool'] = int(nums(s)[-1])
        elif s.startswith('R & G space division'):
            H['RG_division'] = s.split('=')[1].strip()
        elif 'available memory on the printing compute node' in s:
            H['node_memory_MiB'] = fnum(s)
        elif 'GPU acceleration is ACTIVE' in s or 'GPU used by master process' in s or 'GPU-aware MPI' in s:
            H.setdefault('gpu_lines', []).append(s)
        elif s.startswith('Reading input from'):
            H['input'] = s.split('from')[1].strip()
        elif s.startswith('Subspace diagonalization'):
            H['subspace_diag'] = s + ' ' + L[i + 1].strip()
        elif s.startswith('Using Slab Decomposition') or s.startswith('Using Pencil Decomposition'):
            H['fft_decomposition'] = s
        elif s.startswith('Message from routine'):
            R['messages'].append((i + 1, s + ' ' + L[i + 1].strip()))
        elif s.startswith('Error in routine'):
            R.setdefault('errors', []).append((i + 1, s + ' ' + L[i + 1].strip()))
        elif s.startswith('prterun has exited') or s.startswith('mpirun has exited') or 'MPI_ABORT' in s:
            R.setdefault('errors', []).append((i + 1, s))
        elif s.startswith('file ') and 'renormalized' in s:
            R['messages'].append((i + 1, s))
        # ---------------- echoed parameters
        elif re.match(r'(bravais-lattice index|lattice parameter \(alat\)|unit-cell volume|number of atoms/cell|number of atomic types|'
                      r'number of electrons|number of Kohn-Sham states|kinetic-energy cutoff|charge density cutoff|cutoff for Fock operator|'
                      r'scf convergence threshold|mixing beta|energy convergence thresh\.|force convergence thresh\.|press convergence thresh\.|'
                      r'nstep|EXX-fraction|screening parameter|number of iterations used)\s*=', s):
            k, v = s.split('=', 1)
            k = k.strip()
            if k not in P:
                P[k] = v.strip()
        elif s.startswith('Exchange-correlation'):
            P.setdefault('Exchange-correlation', s.split('=', 1)[1].strip())
        elif s.startswith('EXX: q-point mesh'):
            P['EXX q-point mesh'] = s.split(':', 1)[1].strip()
        elif re.match(r'celldm\(1\)', s) and 'celldm' not in P:
            P['celldm'] = nums(s.replace('celldm(1)=', '').replace('celldm(2)=', '').replace('celldm(3)=', '').replace('celldm(4)=', '')
                               .replace('celldm(5)=', '').replace('celldm(6)=', '') + ' ' + L[i + 1].replace('celldm(4)=', '').replace('celldm(5)=', '').replace('celldm(6)=', ''))
        elif s.startswith('crystal axes:') and 'axes_alat' not in R:
            R['axes_alat'] = [nums(L[i + j].split('=')[1])[:3] for j in (1, 2, 3)]
        elif s.startswith('reciprocal axes:') and 'recip_2pi_alat' not in R:
            R['recip_2pi_alat'] = [nums(L[i + j].split('=')[1])[:3] for j in (1, 2, 3)]
        elif s.startswith('PseudoPot. #'):
            m = re.search(r'PseudoPot\. #\s*(\d+) for (\w+)\s+read from file', s)
            pp = {'n': int(m.group(1)), 'element': m.group(2), 'file': L[i + 1].strip()}
            for j in range(i + 2, min(i + 12, n)):
                t = L[j].strip()
                if t.startswith('MD5 check sum'):
                    pp['md5'] = t.split(':')[1].strip()
                elif t.startswith('Pseudo is'):
                    pp['type'] = t.split(',')[0].replace('Pseudo is', '').strip(); pp['Zval'] = fnum(t.split('Zval =')[1])
                elif t.startswith('Using radial grid'):
                    pp['radial_grid'] = t
                elif t.startswith('Generated') or t.startswith('Shape of'):
                    pp.setdefault('notes', []).append(t)
            if not any(q.get('element') == pp['element'] and q.get('file') == pp['file'] for q in R['pseudos']):
                R['pseudos'].append(pp)
            else:
                R['pseudo_rereads'] = R.get('pseudo_rereads', 0) + 1
        elif s.startswith('atomic species   valence'):
            j = i + 1
            while j < n and L[j].strip():
                t = L[j].split()
                R['species'].append({'species': t[0], 'valence': float(t[1]), 'mass': float(t[2])})
                j += 1
        elif re.search(r'\d+ Sym\. Ops\.', s) or s.startswith('No symmetry found'):
            R['symmetry'] = s
        elif s.startswith('number of k points='):
            R['kpoints']['n'] = int(nums(s)[0])
            R['kpoints']['line'] = s
            m = re.search(r'(\S+(?:-\S+)? smearing), width \(Ry\)=\s+([\d.]+)', s)
            if m:
                R['kpoints']['smearing'], R['kpoints']['width_Ry'] = m.group(1), float(m.group(2))
            kl = []
            j = i + 1
            while j < n and ('k(' in L[j] or not L[j].strip() or 'cart. coord.' in L[j]):
                if 'k(' in L[j] and 'wk' in L[j]:
                    m2 = re.search(r'=\s*\(([-\d.\s]+)\), wk =\s*([\d.]+)', L[j])
                    if m2:
                        kl.append(nums(m2.group(1))[:3] + [float(m2.group(2))])
                if 'cryst. coord.' in L[j]:
                    break
                j += 1
            R['kpoints']['sum_wk'] = round(sum(k[3] for k in kl), 6) if kl else None
            A['kpts_scf'] = kl
        elif s.startswith('Dense  grid') or s.startswith('Smooth grid'):
            R['fft']['dense' if 'Dense' in s else 'smooth'] = s
        elif s.startswith('Estimated max dynamical RAM') or s.startswith('Estimated total dynamical RAM') or s.startswith('Estimated static dynamical RAM'):
            R['ram'][s.split('>')[0].strip()] = s.split('>')[1].strip()
        elif s.startswith('Dynamical RAM for'):
            R['ram'].setdefault('components', []).append(s)
        elif s.startswith('Starting wfcs') or s.startswith('Initial potential from') or s.startswith('starting charge') or s.startswith('negative starting charge'):
            R.setdefault('start', []).append(s)
        elif s.startswith('Band Structure Calculation'):
            in_bands_calc = True
            R['calc_type'] = 'bands'
            R['bands_calc'] = {'diag': L[i + 1].strip()}
        elif s.startswith('Computing kpt #'):
            R.setdefault('bands_calc', {}).setdefault('kpts_done', 0)
            R['bands_calc']['kpts_done'] += 1
        elif s.startswith('ethr ') and in_bands_calc:
            R['bands_calc'].setdefault('ethr', s)
        # ---------------- SCF iterations
        elif s.startswith('iteration #'):
            if closed:
                cur = new_step(); R['steps'].append(cur); closed = False
            cur['iterations'] += 1
            m = re.search(r'ecut=\s*([\d.]+) Ry\s+beta=\s*([\d.]+)', s)
            if m:
                cur['ecut'], cur['beta'] = float(m.group(1)), float(m.group(2))
        elif s.startswith('estimated scf accuracy') and cur is not None and not closed:
            cur['acc_trace'].append(fnum(s.split('<')[1]))
        elif s.startswith('total energy') and cur is not None and not closed and '=' in s:
            cur.setdefault('E_trace', []).append(fnum(s.split('=')[1]))
        elif s.startswith('!') and 'total energy' in s:
            if cur is None or closed and not s.startswith('!!'):
                cur = new_step(); R['steps'].append(cur)
            key = 'E_bang2_Ry' if s.startswith('!!') else 'E_Ry'
            cur[key] = fnum(s.split('=')[1])
            closed = True
            j = i + 1
            while j < n and j < i + 40:
                t = L[j].strip()
                if t.startswith('iteration #') or t.startswith('!') or t.startswith('Forces acting') or t.startswith('End of'):
                    break
                for k_, rx in (('E_all_electron_Ry', r'total all-electron energy'), ('acc_final_Ry', r'estimated scf accuracy'),
                               ('mTS_Ry', r'smearing contrib'), ('internal_energy_Ry', r'internal energy E=F\+TS'),
                               ('one_electron_Ry', r'one-electron contribution'), ('hartree_Ry', r'hartree contribution'),
                               ('xc_Ry', r'xc contribution'), ('ewald_Ry', r'ewald contribution'), ('paw_one_center_Ry', r'one-center paw contrib'),
                               ('fock_Ry', r'Fock energy'), ('fock2_Ry', r'\+ Fock energy'), ('half_fock_Ry', r'- averaged Fock'),
                               ('hubbard_Ry', r'Hubbard energy'), ('dispersion_Ry', r'Dispersion'), ('efield_Ry', r'electric field correction'),
                               ('total_magnetization', r'total magnetization'), ('absolute_magnetization', r'absolute magnetization'),
                               ('dexx_Ry', r'est\. exchange err')):
                    if re.match(rx, t) or (k_ == 'acc_final_Ry' and t.startswith('estimated scf accuracy')):
                        v = t.split('<')[1] if '<' in t else t.rsplit('=', 1)[1]
                        cur[k_] = fnum(v)
                if t.startswith('convergence has been achieved'):
                    cur['converged_iterations'] = int(nums(t)[0])
                j += 1
        elif s.startswith('convergence has been achieved') and cur is not None:
            cur['converged_iterations'] = int(nums(s)[0])
        elif s.startswith('convergence NOT achieved') and cur is not None:
            cur['not_converged'] = s
            closed = True
        elif s.startswith('the Fermi energy is') and cur is not None:
            cur['E_F_eV'] = fnum(s.split('is')[1])
        elif s.startswith('the spin up/dw Fermi energies') and cur is not None:
            cur['E_F_updw_eV'] = nums(s)[-2:]
        elif s.startswith('highest occupied, lowest unoccupied level') and cur is not None:
            v = nums(s.split(':')[1]); cur['HOMO_eV'], cur['LUMO_eV'] = v[0], v[1]
        elif s.startswith('highest occupied level') and cur is not None:
            cur['HOMO_eV'] = fnum(s.split(':')[1])
        elif s.startswith('total magnetization') and cur is not None:
            cur['total_magnetization'] = fnum(s.split('=')[1])
        elif s.startswith('absolute magnetization') and cur is not None:
            cur['absolute_magnetization'] = fnum(s.split('=')[1])
        elif s.startswith('negative rho') and cur is not None:
            cur['negative_rho'] = nums(s.split(':')[1])[:2]
        elif s.startswith('Forces acting on atoms'):
            F = []
            j = i + 1
            while j < n:
                t = L[j]
                if 'force =' in t and 'atom' in t:
                    F.append(nums(t.split('force =')[1])[:3])
                elif F and t.strip():
                    break
                j += 1
            F = np.array(F)
            if cur is not None and len(F):
                cur['force_max_component_Ry_bohr'] = float(np.abs(F).max())
                cur['force_max_atom_Ry_bohr'] = float(np.linalg.norm(F, axis=1).max())
                cur['force_rms_component_Ry_bohr'] = float(np.sqrt((F ** 2).mean()))
                cur['force_max_atom_index'] = int(np.linalg.norm(F, axis=1).argmax()) + 1
                A['forces_final'] = F.tolist()
            i = j - 1
        elif s.startswith('Total force =') and cur is not None:
            v = nums(s); cur['total_force_Ry_bohr'] = v[0]; cur['total_scf_correction_Ry_bohr'] = v[1] if len(v) > 1 else None
        elif 'total   stress' in s and 'P=' in s and cur is not None:
            cur['pressure_kbar'] = fnum(s.split('P=')[1])
            cur['stress_kbar'] = [nums(L[i + j])[3:6] for j in (1, 2, 3)]
        # ---------------- BFGS
        elif s.startswith('BFGS Geometry Optimization'):
            R['bfgs'].setdefault('started', i + 1)
        elif s.startswith('Energy error') and cur is not None:
            cur['bfgs_energy_error_Ry'] = fnum(s.split('=')[1])
        elif s.startswith('Gradient error') and cur is not None:
            cur['bfgs_gradient_error'] = fnum(s.split('=')[1])
        elif s.startswith('Cell gradient error') and cur is not None:
            cur['bfgs_cell_gradient_error_kbar'] = fnum(s.split('=')[1])
        elif s.startswith('number of scf cycles') and cur is not None:
            cur['bfgs_scf_cycles'] = int(fnum(s.split('=')[1]))
        elif s.startswith('number of bfgs steps') and cur is not None:
            cur['bfgs_steps'] = int(fnum(s.split('=')[1]))
        elif re.match(r'(energy|enthalpy)\s+(old|new)\s+=', s) and cur is not None:
            k_ = '_'.join(s.split('=')[0].split()) + '_Ry'
            cur[k_] = fnum(s.split('=')[1])
        elif s.startswith('CASE:') and cur is not None:
            cur['bfgs_case'] = s
        elif s.startswith('new trust radius') and cur is not None:
            cur['trust_radius_bohr'] = fnum(s.split('=')[1])
        elif s.startswith('new conv_thr') and cur is not None:
            cur['new_conv_thr'] = fnum(s.split('=')[1])
        elif s.startswith('new unit-cell volume') and cur is not None:
            m = re.search(r'\(\s*([\d.]+)\s*Ang', s)
            cur['volume_A3'] = float(m.group(1)) if m else None
        elif s.startswith('density =') and cur is not None:
            cur['density_g_cm3'] = fnum(s.split('=')[1])
        elif s.startswith('CELL_PARAMETERS') and cur is not None and L[i - 1].strip() == '' and 'final' not in R.get('_in_final', ''):
            unit = s
            cellv = [nums(L[i + j])[:3] for j in (1, 2, 3)]
            if 'alat' in unit:
                al = fnum(unit.split('=')[1]) * BOHR
                cellv = (np.array(cellv) * al).tolist()
            cur['cell_A'] = cellv
        elif s.startswith('bfgs converged in'):
            R['bfgs']['converged'] = s; R['bfgs']['line'] = i + 1
        elif s.startswith('(criteria:'):
            R['bfgs']['criteria'] = s
        elif s.startswith('End of BFGS'):
            R['bfgs']['end'] = i + 1
        elif s.startswith('Final energy') or s.startswith('Final enthalpy'):
            R['bfgs']['final_' + s.split()[1]] = fnum(s.split('=')[1])
        elif s.startswith('The maximum number of steps has been reached'):
            R['bfgs']['max_steps_reached'] = True
        elif s.startswith('bfgs failed') or s.startswith('history already reset'):
            R['bfgs']['failure'] = s
        elif s.startswith('Begin final coordinates'):
            R['_in_final'] = 'final'
            blk = []
            j = i + 1
            while j < n and not L[j].strip().startswith('End final coordinates'):
                blk.append(L[j]); j += 1
            R['final_coordinates'] = {'line': i + 1, 'text': blk}
            R['_in_final'] = ''
            i = j
        elif s.startswith('A final scf calculation at the relaxed structure'):
            R['bfgs']['final_scf'] = i + 1
        # ---------------- EXX
        elif s.startswith('EXX: now go back to refine'):
            R['exx']['cycles'].append({'line': i + 1})
        elif s.startswith('est. exchange err (dexx)'):
            R['exx'].setdefault('dexx_trace', []).append(fnum(s.split('=')[1]))
        elif s.startswith('+ Fock energy'):
            R['exx'].setdefault('fock_trace_Ry', []).append(fnum(s.split('=')[1]))
        elif s.startswith('EXX self-consistency reached'):
            R['exx']['reached'] = True
        elif s.startswith('EXX grid:'):
            R['exx']['grid'] = s
        # ---------------- end
        elif re.match(r'^\s*(\S.*?)\s*:\s+[\d.dhms ]+CPU\s+[\d.dhms ]+WALL', l):
            m = re.match(r'^\s*(\S.*?)\s*:\s+(.+?)CPU\s+(.+?)WALL(?:\s*\(\s*(\d+) calls\))?', l)
            R['timing'][m.group(1)] = {'cpu': m.group(2).strip(), 'wall': m.group(3).strip(), 'calls': int(m.group(4)) if m.group(4) else None}
        elif s.startswith('This run was terminated on'):
            R['terminated'] = s.split(':', 1)[1].strip()
        elif s == 'JOB DONE.':
            R['done'] = True
        i += 1
    R.pop('_in_final', None)
    # final eigenvalues
    A['eig'] = final_eigs(L)
    for st in R['steps']:
        A['scf_accuracy'].append(st.pop('acc_trace'))
        st['E_trace_n'] = len(st.pop('E_trace', []))
    R['warnings'] = warnings(L)
    return R, A


def final_eigs(L):
    """k, eigenvalues and occupations printed after the last 'End of self-consistent / band structure calculation'."""
    idx = [i for i, l in enumerate(L) if 'End of self-consistent calculation' in l or 'End of band structure calculation' in l]
    if not idx:
        return None
    start = idx[-1]
    ks, ev, occ = [], [], []
    mode = None
    spin_down = None
    for i in range(start, len(L)):
        l = L[i]
        if 'SPIN DOWN' in l:
            spin_down = len(ks)
        if 'bands (ev)' in l and 'k =' in l:
            ks.append(nums(l.split('(')[0].split('=')[1])[:3]); ev.append([]); occ.append([]); mode = 'e'; continue
        if 'occupation numbers' in l:
            mode = 'o'; continue
        t = l.strip()
        if not t:
            continue
        if re.search(r'[a-zA-Z]', t):
            if mode:
                mode = None
            if t.startswith('highest') or t.startswith('the Fermi') or t.startswith('!') or 'Writing' in t:
                if not ks:
                    continue
            continue
        if mode == 'e':
            ev[-1].extend(nums(t))
        elif mode == 'o':
            occ[-1].extend(nums(t))
    if not ks:
        return None
    return {'k_cart_2pi_alat': ks, 'eig_eV': ev, 'occ': occ if any(occ) else None, 'line': start + 1, 'spin_down_start': spin_down}


def band_analysis(eig, nelec, efermi=None, smearing=False, nocc_override=None):
    if not eig:
        return None
    ev = np.array([e for e in eig['eig_eV']])
    nb = ev.shape[1]
    out = {'n_k': int(ev.shape[0]), 'n_bands': int(nb)}
    if not smearing or nocc_override:
        no = nocc_override or int(round(nelec)) // 2
        if no >= nb:
            out['note'] = 'no empty band printed'
            out['VBM_eV'] = float(ev[:, no - 1].max())
            return out
        vb, cb = ev[:, no - 1], ev[:, no]
        iv, ic = int(vb.argmax()), int(cb.argmin())
        dg = cb - vb
        out.update({'n_occ': no, 'VBM_eV': float(vb[iv]), 'VBM_k_index': iv, 'CBM_eV': float(cb[ic]), 'CBM_k_index': ic,
                    'gap_eV': round(float(cb[ic] - vb[iv]), 5), 'direct_gap_min_eV': round(float(dg.min()), 5), 'direct_gap_k_index': int(dg.argmin()),
                    'gap_type': 'direct' if iv == ic else 'indirect', 'VB_width_top_band_eV': round(float(vb.max() - vb.min()), 4),
                    'CB_width_bottom_band_eV': round(float(cb.max() - cb.min()), 4)})
        if no + 1 < nb:
            out['E2_minus_E1_at_k0_eV'] = round(float(ev[0, no + 1] - ev[0, no]), 5)
    if efermi is not None:
        below = [b for b in range(nb) if ev[:, b].max() < efermi]
        cross = [b for b in range(nb) if ev[:, b].min() <= efermi <= ev[:, b].max()]
        out.update({'E_F_eV': efermi, 'bands_fully_below_EF': len(below), 'bands_crossing_EF_1based': [b + 1 for b in cross]})
        if below:
            top = max(below)
            out['highest_band_below_EF_max_eV'] = float(ev[:, top].max())
        above = [b for b in range(nb) if ev[:, b].min() > efermi]
        if above:
            out['lowest_band_above_EF_min_eV'] = float(ev[:, min(above)].min())
    return out


# ---------------- inputs
def parse_input(text):
    """pw.x input: every namelist variable, cards (species, cell, positions with constraints, k points)."""
    out = {'namelists': {}, 'cards': {}}
    T = text.splitlines()
    i = 0
    while i < len(T):
        s = T[i].strip()
        if s.startswith('&'):
            name = s[1:].strip().upper()
            d = {}
            i += 1
            while i < len(T) and T[i].strip() != '/':
                for part in re.split(r',(?=(?:[^\']*\'[^\']*\')*[^\']*$)', T[i]):
                    if '=' in part:
                        k, v = part.split('=', 1)
                        v = v.strip().strip(',').strip()
                        d[k.strip()] = v.strip("'\"")
                i += 1
            out['namelists'][name] = d
        elif s.upper().startswith('ATOMIC_SPECIES'):
            sp = []
            j = i + 1
            while j < len(T) and len(T[j].split()) == 3 and not T[j].strip().upper().startswith(('CELL', 'ATOMIC', 'K_POINTS')):
                a, m, f = T[j].split(); sp.append({'species': a, 'mass': float(m), 'pseudo': f}); j += 1
            out['cards']['ATOMIC_SPECIES'] = sp
        elif s.upper().startswith('CELL_PARAMETERS'):
            out['cards']['CELL_PARAMETERS'] = {'unit': s.split()[1] if len(s.split()) > 1 else '', 'vectors': [nums(T[i + j])[:3] for j in (1, 2, 3)]}
        elif s.upper().startswith('ATOMIC_POSITIONS'):
            pos, lab, cons = [], [], []
            j = i + 1
            while j < len(T):
                t = T[j].split()
                if len(t) < 4 or not re.match(r'^[A-Z][a-z]?\d*$', t[0]):
                    break
                lab.append(t[0]); pos.append([float(x) for x in t[1:4]])
                cons.append([int(x) for x in t[4:7]] if len(t) >= 7 else None)
                j += 1
            out['cards']['ATOMIC_POSITIONS'] = {'unit': s.split()[1] if len(s.split()) > 1 else '', 'labels': lab, 'positions': pos,
                                                'n_constrained': sum(1 for c in cons if c and min(c) == 0)}
        elif s.upper().startswith('K_POINTS'):
            mode = s.split()[1] if len(s.split()) > 1 else ''
            if 'automatic' in mode:
                out['cards']['K_POINTS'] = {'mode': mode, 'grid': T[i + 1].split()}
            else:
                nk = int(T[i + 1].split()[0])
                pts = [nums(T[i + 2 + j])[:4] for j in range(nk)]
                out['cards']['K_POINTS'] = {'mode': mode, 'n': nk, 'points_first_last': [pts[0], pts[-1]] if pts else None,
                                            'path_points': pts if 'b' in mode else None}
        i += 1
    return out


def struct_from_input(inp):
    c = inp['cards']
    if 'CELL_PARAMETERS' not in c or 'ATOMIC_POSITIONS' not in c:
        return None
    cell = np.array(c['CELL_PARAMETERS']['vectors'])
    if 'bohr' in c['CELL_PARAMETERS']['unit']:
        cell = cell * BOHR
    elif 'alat' in c['CELL_PARAMETERS']['unit']:
        return None
    pos = np.array(c['ATOMIC_POSITIONS']['positions'])
    u = c['ATOMIC_POSITIONS']['unit']
    frac = pos if 'crystal' in u else (pos * (BOHR if 'bohr' in u else 1.0)) @ np.linalg.inv(cell)
    sym = [re.sub(r'\d+$', '', x) for x in c['ATOMIC_POSITIONS']['labels']]
    return cell, sym, frac


def struct_from_final(fc, cell_fallback):
    """'Begin final coordinates' block -> cell (A), symbols, fractional positions."""
    T = fc['text']
    cell = cell_fallback
    for j, t in enumerate(T):
        if t.strip().startswith('CELL_PARAMETERS'):
            v = np.array([nums(T[j + k])[:3] for k in (1, 2, 3)])
            if 'alat' in t:
                v = v * fnum(t.split('=')[1]) * BOHR
            elif 'bohr' in t:
                v = v * BOHR
            cell = v
    ia = next(j for j, t in enumerate(T) if t.strip().startswith('ATOMIC_POSITIONS'))
    unit = T[ia]
    sym, pos = [], []
    for t in T[ia + 1:]:
        x = t.split()
        if len(x) < 4:
            break
        sym.append(re.sub(r'\d+$', '', x[0])); pos.append([float(y) for y in x[1:4]])
    pos = np.array(pos)
    frac = pos if 'crystal' in unit else (pos * (BOHR if 'bohr' in unit else 1.0)) @ np.linalg.inv(cell)
    return cell, sym, frac


def geometry(cell, sym, frac, ref=None):
    """Composition, cell, density, bonds (In-O, W-O <= 2.6 A, O-H <= 1.2 A), coordination, slab thickness/vacuum,
    displacement statistics against ref (cell, sym, frac) if given."""
    cell = np.array(cell); frac = np.array(frac)
    cart = frac @ cell
    nat = len(sym)
    comp = {e: sym.count(e) for e in sorted(set(sym))}
    a = np.linalg.norm(cell, axis=1)
    ang = [math.degrees(math.acos(np.dot(cell[i], cell[j]) / a[i] / a[j])) for i, j in ((1, 2), (0, 2), (0, 1))]
    vol = abs(np.linalg.det(cell))
    dens = sum(MASS.get(e, 0) * c for e, c in comp.items()) * 1.66053906660 / vol
    out = {'n_atoms': nat, 'composition': comp, 'cell_lengths_A': [round(float(x), 5) for x in a], 'cell_angles_deg': [round(x, 3) for x in ang],
           'volume_A3': round(float(vol), 4), 'density_g_cm3': round(float(dens), 4)}
    inv = np.linalg.inv(cell)
    shifts = np.array([[i, j, k] for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1)])

    def dists(i, el, rmax):
        res = []
        for j in range(nat):
            if sym[j] != el or j == i:
                continue
            d = frac[j] - frac[i]; d -= np.rint(d)
            for sh in shifts:
                r = np.linalg.norm((d + sh) @ cell)
                if r < rmax:
                    res.append(r)
        return res
    bonds = {}
    for (a1, a2, rc) in (('In', 'O', 2.6), ('W', 'O', 2.6), ('O', 'H', 1.2), ('In', 'H', 2.0)):
        if a1 in comp and a2 in comp:
            allb, cn = [], []
            for i in range(nat):
                if sym[i] == a1:
                    d = dists(i, a2, rc); allb += d; cn.append(len(d))
            if allb:
                allb = np.array(allb)
                bonds[f'{a1}-{a2}'] = {'cutoff_A': rc, 'n': int(len(allb)), 'min': round(float(allb.min()), 4), 'mean': round(float(allb.mean()), 4),
                                       'max': round(float(allb.max()), 4), 'std': round(float(allb.std()), 4),
                                       f'CN_{a1}_hist': {str(k): cn.count(k) for k in sorted(set(cn))}}
    out['bonds'] = bonds
    if 'O' in comp and ('In' in comp or 'W' in comp):
        cnO = [len(dists(i, 'In', 2.6)) + len(dists(i, 'W', 2.6)) for i in range(nat) if sym[i] == 'O']
        out['CN_O_by_cations_hist'] = {str(k): cnO.count(k) for k in sorted(set(cnO))}
    z = cart[:, 2]
    c = float(np.linalg.norm(cell[2]))
    zs = np.sort(np.mod(z, c))
    gaps = np.diff(np.concatenate([zs, [zs[0] + c]]))
    if gaps.max() > 5.0:
        k = int(gaps.argmax())
        lo = zs[(k + 1) % nat]; hi = zs[k]
        ext = (hi - lo) % c
        out['slab'] = {'vacuum_A': round(float(gaps.max()), 3), 'extent_A': round(float(ext), 3)}
        zz = np.mod(z - lo, c)
        for el in ('H', 'O', 'In', 'W'):
            if el in comp:
                v = zz[[s == el for s in sym]]
                out['slab'][f'thickness_{el}_{el}_A'] = round(float(v.max() - v.min()), 4)
    if ref is not None:
        rc_, rs, rf = ref
        if list(rs) == list(sym):
            d = frac - np.array(rf); d -= np.rint(d)
            dc = np.linalg.norm(d @ cell, axis=1)
            out['displacement_vs_initial'] = {'max_A': round(float(dc.max()), 4), 'atom': f'{sym[int(dc.argmax())]}{int(dc.argmax()) + 1}',
                                              'mean_A': round(float(dc.mean()), 4), 'n_gt_0p1_A': int((dc > 0.1).sum()),
                                              'by_element_max_A': {e: round(float(dc[[s == e for s in sym]].max()), 4) for e in comp}}
            if 'slab' in out:
                zz0 = np.mod(z - z.min(), c)
                surf = (zz0 < 3.0) | (zz0 > zz0.max() - 3.0)
                out['displacement_vs_initial']['outer_3A_mean_A'] = round(float(dc[surf].mean()), 4)
                out['displacement_vs_initial']['interior_mean_A'] = round(float(dc[~surf].mean()), 4) if (~surf).any() else None
        else:
            out['displacement_vs_initial'] = 'atom order/species differ'
    return out


# ---------------- projwfc / pp / average / driver
def parse_projwfc(L):
    out = {'done': any('JOB DONE' in l for l in L)}
    for i, l in enumerate(L):
        s = l.strip()
        if s.startswith('natomwfc') or s.startswith('nbnd') or s.startswith('nkstot') or s.startswith('npwx') or s.startswith('nwfc'):
            k, v = s.split('=', 1); out[k.strip()] = int(fnum(v))
        elif s.startswith('Program PROJWFC'):
            out['version'] = s
        elif s.startswith('Spilling Parameter'):
            out['spilling'] = fnum(s.split(':')[1])
        elif s.startswith('PROJWFC') and 'WALL' in s:
            out['time'] = s
    low = {}
    for l in L:
        m = re.match(r'\s*Atom #\s*(\d+): total charge =\s*([\d.]+), (s|p|d|f) =\s*([\d.]+)', l)
        if m:
            a = int(m.group(1)); low.setdefault(a, {'total': float(m.group(2))})[m.group(3)] = float(m.group(4))
    out['lowdin'] = low
    out['n_states'] = sum(1 for l in L if l.strip().startswith('state #'))
    out['warnings'] = warnings(L)
    return out


def parse_driver(L):
    out = {'lines': [l.strip() for l in L if l.strip()]}
    for l in L:
        m = re.search(r'job (\S+) host (\S+) cpus (\d+) limit (\d+)s', l)
        if m:
            out.update({'host': m.group(2), 'cpus': int(m.group(3)), 'limit_s': int(m.group(4)), 'start': l[1:21]})
        m = re.search(r'GPU mode: (.+)$', l)
        if m:
            out['gpu'] = m.group(1)
        m = re.search(r'steps finished after (\d+) s', l)
        if m:
            out['total_s'] = int(m.group(1))
    out['steps'] = []
    for l in L:
        m = re.search(r'\[(.+?)\] pw\.x (\S+) start \(-nk (\d+), max_seconds (\d+)\)', l)
        if m:
            out['steps'].append({'step': m.group(2), 'start': m.group(1), 'nk': int(m.group(3)), 'max_seconds': int(m.group(4))})
        m = re.search(r'\[(.+?)\] pw\.x (\S+) end rc=(\d+)\s*(.*)$', l)
        if m:
            st = next((x for x in reversed(out['steps']) if x['step'] == m.group(2)), None)
            if st is not None:
                st.update({'end': m.group(1), 'rc': int(m.group(3)), 'time': m.group(4).strip()})
    return out
