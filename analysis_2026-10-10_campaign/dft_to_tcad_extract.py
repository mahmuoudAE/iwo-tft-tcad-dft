"""DFT -> TCAD extraction (campaign 2026-10-10). Reads EXISTING Quantum ESPRESSO outputs only and writes
dft_inputs.json next to this script. It runs no simulator (no pw.x, no pp.x, no ATLAS/deckbuild) and changes no other
file.

Usage: python dft_to_tcad_extract.py

What it computes (every quantity is PBE unless named HSE):
  bulk       fundamental gap and CB mass (collect_results.bulk: bands_path.out, bands_gamma.out)
  slabs      0.51 / 0.75 / 1 / 2 nm H-terminated In2O3(001) slabs (Lin et al. 2022 recipe):
             gap (last HOMO/LUMO line of scf.out), vacuum level and EA/IP (analyze_slabs.one), H-to-H thickness and
             in-plane lattice length (scf.in), in-plane CB mass (collect_results.slab_mass on bands.out), next empty
             level at Gamma (bands.out, first k-point), surface-state weights (projwfc, same measure as
             cern_htcondor/surface_state_check.py)
  dEc/dEv    2 nm: two-step alignment RE-COMPUTED here from the slab planar average (a/2 window) and the bulk constants
             E_v-<V> = 3.9098 eV, E_c-<V> = 4.7985 eV (logged in RESULTS_LOG.md 2026-10-05; bulk_v11.cube was deleted,
             so the bulk constants are not re-computed). Thinner films: dEc(t) = dEc(2 nm) + EA(2 nm) - EA(t)
             (same-termination EA route, as V2 for 1 nm), dEv = dEc - dEg.
  HSE        gaps of the norm-conserving PBE/HSE06 single points (nc_* folders) and the ratio dEg(HSE)/dEg(PBE)
  IWO        1 nm and 2 nm W slabs, 80-atom bulk cells (W on 24d and 8b): band characters from projwfc (VB top is
             band n_pure - 1, see the PAW band-count pitfall), occupations with the Marzari-Vanderbilt smearing of
             scf.in, electrons per band above the VB top, W-5d-projected electron count, W-5d-rich level relative to the
             host CB bottom at Gamma, EA/IP/work function for the slabs
  Nc         three conventions: V2 (3-D formula, m* = 0.208 + DFT increment), ratio-scaled 3-D, quasi-2-D
             (N2D/t, single subband; only where the DFT subband spacing >> kT)
  laws       power laws through the relaxed-film DFT points (0.695, 0.930, 1.962 nm H-to-H) compared with the V2 laws
  alpha      CB non-parabolicity, Kane form E(1 + alpha E) = hbar^2 k^2 / 2m, first k-direction of each bands run
"""
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
QE = PKG / 'qe_workflow'
R = QE / 'cern_htcondor' / 'results'
sys.path.insert(0, str(QE))
sys.path.insert(0, str(QE / 'cern_htcondor'))
from analyze_slabs import one as slab_one  # noqa: E402
import collect_results as cr  # noqa: E402

RY, BOHR, H2M = 13.605693122994, 0.529177210903, 3.80998212
KB_EV, T = 8.617333262e-5, 300.0
KT = KB_EV * T
ME, KBJ, HP, HBAR = 9.1093837015e-31, 1.380649e-23, 6.62607015e-34, 1.054571817e-34
A_BULK = 10.306                       # relaxed PBE bulk lattice constant used for the averaging windows (A)
DV_B, DC_B = 3.9098, 4.7985           # bulk E_v-<V>, E_c-<V> (eV), RESULTS_LOG.md 2026-10-05 (cube deleted)
MSTAR_EXP_BULK = 0.208                # Stokey et al. 2021 (optical Hall, In2O3), as in V2 (LITERATURE)
EG_BULK_TCAD, CHI_BULK_TCAD = 3.05, 4.3   # V2 bulk values (LITERATURE_IWO, Fan 2021), used only to print EG300/AFFINITY

SLABS = [  # label, folder, role
    ('0.51', 'slabL1_relax_v2', 'one cation plane, relaxes into an In(OH)3-like layer (outside the recipe)'),
    ('0.75', 'slabL2_relax_v2', 'two cation planes'),
    ('1.0', 'slab1r_final_cpu', 'relaxed 1 nm slab (geometry of slab1_relax_gpu), CPU final SCF with planar average'),
    ('2.0', 'slab2_relax_c2', 'relaxed 2 nm slab (GPU final SCF, planar average, bands)'),
]
SURFACE_CHECK = {'0.51': 'slabL1_relax_v2', '0.75': 'slabL2_relax_v2', '2.0': 'slab2r_pdos_cpu'}
IWO = [  # label, folder, scf file, n_pure (occupied bands of the pure twin), pure twin folder for EA/gap comparison
    ('1.0', 'iwo_slab1_final_cpu', 'scf.out', 312, 'slab1r_final_cpu'),
    ('2.0', 'iwo_slab2_final_cpu', 'scf.out', 664, 'slab2r_pdos_cpu'),
    ('bulk_24d', 'iwo_W24d', 'scf_k4.out', 352, None),
    ('bulk_8b', 'iwo_W8b', 'scf_k4.out', 352, None),
]


# ---------------------------------------------------------------- helpers
def read_struct(f):
    inp = Path(f).read_text()
    cell = np.array([[float(x) for x in l.split()] for l in inp.split('CELL_PARAMETERS angstrom')[1].strip().splitlines()[:3]])
    blk = inp.split('ATOMIC_POSITIONS crystal')[1].split('K_POINTS')[0].strip().splitlines()
    sym = [l.split()[0] for l in blk]
    cart = np.array([[float(x) for x in l.split()[1:4]] for l in blk]) @ cell
    return cell, sym, cart


def hh_thickness_nm(job):
    cell, sym, cart = read_struct(R / job / 'scf.in')
    zH = cart[[s == 'H' for s in sym], 2]
    return float((zH.max() - zH.min()) / 10.0), float(np.linalg.norm(cell[0])), float(np.linalg.norm(cell[1]))


def all_eigs(f):
    """k-point weights (sum 2), eigenvalues of every band at every k of the LAST printout, Fermi energy."""
    t = Path(f).read_text(errors='replace')
    nks = int(re.search(r'number of k points=\s+(\d+)', t).group(1))
    wk = np.array([float(x) for x in re.findall(r'k\(\s*\d+\) = \([-\d. ]+\), wk =\s+([\d.]+)', t)[:nks]])
    last = t.rsplit('End of self-consistent calculation', 1)[-1] if 'End of self-consistent calculation' in t \
        else t.rsplit('End of band structure calculation', 1)[-1]
    bl = re.findall(r'k =\s*([-\d. ]+?)\s*\(\s*\d+ PWs\)\s+bands \(ev\):\s+(.*?)(?=\n\s*\n\s*(?:occupation numbers|k =|highest|the Fermi|Writing|the spin)|\n\s*\n\s*\n)', last, re.S)
    ev = [np.array([float(x) for x in re.findall(r'-?\d+\.\d+', e.replace('-', ' -'))]) for _, e in bl]
    ef = re.findall(r'the Fermi energy is\s+(-?[\d.]+)', t)
    nel = float(re.search(r'number of electrons\s+=\s+([\d.]+)', t).group(1))
    return wk, ev, (float(ef[-1]) if ef else None), nel


def wgauss_mv(x):
    """Marzari-Vanderbilt cold smearing occupation (QE wgauss, n = -1); x = (E_F - e)/degauss."""
    xp = x - 1 / math.sqrt(2)
    return 0.5 * math.erf(xp) + 1 / math.sqrt(2 * math.pi) * math.exp(-min(200.0, xp * xp)) + 0.5


def projwfc(f):
    """states {#: (atom, element, l)}; per k-block {band: (E, {element+l: weight}, {atom: weight}, |psi|^2)}"""
    t = Path(f).read_text(errors='replace')
    states = {int(m.group(1)): (int(m.group(2)) - 1, m.group(3), int(m.group(4)))
              for m in re.finditer(r'state #\s*(\d+): atom\s+(\d+) \((\w+)\s*\)\s*, wfc\s+\d+ \(l=(\d)', t)}
    out = []
    for b in re.split(r'\n\s*k =\s+', t)[1:]:
        kb = {}
        for m in re.finditer(r'==== e\(\s*(\d+)\) =\s*(-?[\d.]+) eV ====(.*?)\|psi\|\^2 = ([\d.]+)', b, re.S):
            w, wa = {}, {}
            for c, s in re.findall(r'([\d.]+)\*\[#\s*(\d+)\]', m.group(3)):
                at, el, l = states[int(s)]
                w[f"{el}{'spdf'[l]}"] = w.get(f"{el}{'spdf'[l]}", 0.0) + float(c)
                wa[at] = wa.get(at, 0.0) + float(c)
            kb[int(m.group(1))] = (float(m.group(2)), w, wa, float(m.group(4)))
        out.append(kb)
    return states, out


def vacuum(job):
    """E_vac (eV) on each side of the slab (left / right window within 2 A of the cell boundary) -> dipole check."""
    z, v = np.loadtxt(next((R / job).glob('*_avg.dat')), usecols=(0, 1), unpack=True)
    c = z.max() + (z[1] - z[0])
    left, right = z * BOHR < 2.0, (c - z) * BOHR < 2.0
    return float(v[left | right].mean() * RY), float(v[left].mean() * RY), float(v[right].mean() * RY)


def macro(z, vp, w):
    dz = z[1] - z[0]; n = max(1, int(round(w / dz)))
    ext = np.concatenate([vp[-n:], vp, vp[:n]])
    return np.convolve(ext, np.ones(n) / n, mode='same')[n:-n]


def two_step(job):
    """dEc, dEv relative to bulk by the two-step alignment (a/2 window and double a/2*a/4), slab side re-computed."""
    d = R / job
    z, vp = np.loadtxt(next(d.glob('*_avg.dat')), usecols=(0, 1), unpack=True)
    sc = (d / 'scf.out').read_text(errors='replace')
    vbm, cbm = map(float, re.findall(r'highest occupied, lowest unoccupied level \(ev\):\s+(-?[\d.]+)\s+(-?[\d.]+)', sc)[-1])
    cell, sym, cart = read_struct(d / 'scf.in')
    zin = cart[[s == 'In' for s in sym], 2] / BOHR
    zc = 0.5 * (zin.min() + zin.max())
    res = {}
    for name, vm in (('a/2', macro(z, vp, A_BULK / 2 / BOHR)), ('a/2*a/4', macro(z, macro(z, vp, A_BULK / 4 / BOHR), A_BULK / 2 / BOHR))):
        win = np.abs(z - zc) <= A_BULK / 8 / BOHR
        vc = float(np.interp(zc, z, vm)) * RY
        res[name] = {'dEc_eV': round(cbm - (vc + DC_B), 4), 'dEv_eV': round(vbm - (vc + DV_B), 4),
                     'plateau_spread_meV': round(float(vm[win].max() - vm[win].min()) * RY * 1000, 1)}
    return res


def surface_weights(job, nocc_override=None):
    """Same measure as surface_state_check.py: share of the VBM/CBM projected weight on surface OH groups.
    nocc_override: VB-top band of a W cell (n_pure - 1, PAW band-count pitfall)."""
    d = R / job
    cell, sym, cart = read_struct(d / 'scf.in')
    nat = len(sym)
    H = [i for i, s in enumerate(sym) if s == 'H']; O = [i for i, s in enumerate(sym) if s == 'O']
    oh_O = set()
    for h in H:
        for o in O:
            dv = cart[o] - cart[h]
            dv[:2] -= np.rint(np.linalg.solve(cell[:2, :2].T, dv[:2])) @ cell[:2, :2]
            if np.linalg.norm(dv) < 1.15:
                oh_O.add(o)
    surf = set(H) | oh_O
    t = (d / 'scf.out').read_text(errors='replace')
    nocc = nocc_override or int(round(float(re.search(r'number of electrons\s+=\s+([\d.]+)', t).group(1)))) // 2
    _, kb = projwfc(next(d.glob('projwfc_*.out')))
    z = cart[:, 2]; zs = np.linspace(z.min() - 0.01, z.max() + 0.01, 9)
    out = {'n_atoms': nat, 'surface_OH_number_share': round(len(surf) / nat, 3)}
    for name, band in (('VBM', nocc), ('CBM', nocc + 1), ('VBM-20_reference', nocc - 20)):
        w = np.zeros(nat); nk = 0
        for k in kb:
            if band in k:
                nk += 1
                for a, c in k[band][2].items():
                    w[a] += c
        w /= max(nk, 1); tot = w.sum()
        out[name] = {'band': band, 'weight_on_surface_OH': round(float(sum(w[i] for i in surf) / tot), 3),
                     'by_element': {e: round(float(sum(w[i] for i in range(nat) if sym[i] == e) / tot), 3) for e in ('In', 'O', 'H')},
                     'z_profile_8_slices': [round(float(sum(w[i] for i in range(nat) if lo <= z[i] < hi) / tot), 2) for lo, hi in zip(zs[:-1], zs[1:])]}
    return out


def gamma_levels(job, nocc):
    """CBM at Gamma and the next empty level (first k-point of bands.out is Gamma)."""
    ks, ev = cr.eig(R / job / 'bands.out', nocc)
    g = int(np.argmin(np.linalg.norm(ks, axis=1)))
    return float(ev[g, nocc]), float(ev[g, nocc + 1] - ev[g, nocc])


def nonparabolic(f, nocc, npts=11):
    """Kane fit of the CB along the first k-direction (Gamma + 10 points): E(1 + alpha E) = H2M k^2 / m.
    Linear least squares in the unknowns 1/m and alpha: H2M k^2 = (1/m)^-1 ... rewritten as E = (H2M/m) k^2 - alpha E^2."""
    ks, ev = cr.eig(f, nocc)
    k = np.linalg.norm(ks, axis=1)[:npts]; e = ev[:npts, nocc] - ev[0, nocc]
    A = np.vstack([k ** 2, -e ** 2]).T
    (c, alpha), *_ = np.linalg.lstsq(A[1:], e[1:], rcond=None)
    return {'m0_kane_m0': round(H2M / c, 4), 'alpha_per_eV': round(float(alpha), 3),
            'fit_range_k_invA': round(float(k[-1]), 4), 'fit_range_E_eV': round(float(e[-1]), 3)}


def nc3d(m):
    return 2.0 * (2.0 * math.pi * m * ME * KBJ * T / HP ** 2) ** 1.5 / 1e6


def n2d(m):
    """2-D DOS density m kT/(pi hbar^2), cm^-2 (spin 2, one valley at Gamma)."""
    return m * ME * KBJ * T / (math.pi * HBAR ** 2) / 1e4


def power_fit(ts, ys):
    """least squares of ln y = ln a - p ln t"""
    A = np.vstack([np.ones(len(ts)), -np.log(ts)]).T
    (la, p), *_ = np.linalg.lstsq(A, np.log(ys), rcond=None)
    return float(math.exp(la)), float(p)


# ---------------------------------------------------------------- main
def main():
    out = {'generated_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
           'script': 'analysis_2026-10-10_campaign/dft_to_tcad_extract.py',
           'method': 'Quantum ESPRESSO 7.5, PAW-PBE (In 4d, W 5s5p semicore), relaxed structures; HSE06 only as a '
                     'norm-conserving single-point check of the 1 nm confinement shift'}
    b = cr.bulk()
    out['bulk'] = {'a_A': b['a_A'], 'Eg_fundamental_PBE_eV': b['gap_fundamental_eV'], 'Eg_Gamma_PBE_eV': b['gap_gamma_eV'],
                   'mstar_PBE_m0': b['mstar_m0'], 'E_v_minus_Vavg_eV': DV_B, 'E_c_minus_Vavg_eV': DC_B,
                   'source': 'bulk_In2O3_protocol/vcrelax_ecut71_k3.out, bands_path.out, bands_gamma.out; alignment constants RESULTS_LOG.md 2026-10-05'}
    eg_b, m_b = b['gap_fundamental_eV'], b['mstar_m0']

    # ---- HSE check
    hse = {}
    for j in ('nc_pbe_bulk_e80', 'nc_pbe_slab1_e80', 'nc_hse_bulk_e80', 'nc_hse_bulk_q3_f160_e80', 'nc_hse_slab1_f160_e80'):
        g, done = cr.gap_of(R / j / 'scf.out')
        hse[j] = g
    r1 = (hse['nc_hse_slab1_f160_e80'] - hse['nc_hse_bulk_e80']) / (hse['nc_pbe_slab1_e80'] - hse['nc_pbe_bulk_e80'])
    r3 = (hse['nc_hse_slab1_f160_e80'] - hse['nc_hse_bulk_q3_f160_e80']) / (hse['nc_pbe_slab1_e80'] - hse['nc_pbe_bulk_e80'])
    out['hse_check'] = {'gaps_Gamma_eV': hse, 'ratio_dEg_HSE_over_PBE_q1': round(r1, 4), 'ratio_worst_case_q3_bulk': round(r3, 4),
                        'Eg_bulk_HSE_eV': [hse['nc_hse_bulk_q3_f160_e80'], hse['nc_hse_bulk_e80']],
                        'note': 'SG15 NC, 80 Ry, ecutfock 160 Ry, PBE geometry (a = 10.306 A, 1.9 % above experiment); slab gap HSE at q = 1 only'}

    # ---- pure slabs
    slabs = {}
    for lab, job, role in SLABS:
        r = slab_one(R / job)
        nocc = int(round(float(re.search(r'number of electrons\s+=\s+([\d.]+)', (R / job / 'scf.out').read_text(errors='replace')).group(1)))) // 2
        t_hh, a1, a2 = hh_thickness_nm(job)
        ev_, evl, evr = vacuum(job)
        m = cr.slab_mass(R / job)
        cb_g, e21 = gamma_levels(job, nocc)
        slabs[lab] = {'job': job, 'role': role, 'thickness_HH_nm': round(t_hh, 3), 'inplane_a_A': [round(a1, 4), round(a2, 4)],
                      'n_occ': nocc, 'VBM_eV': r['VBM_eV'], 'CBM_eV': r['CBM_eV'], 'gap_PBE_eV': r['gap_eV'],
                      'dEg_PBE_eV': round(r['gap_eV'] - eg_b, 4), 'E_vac_eV': round(ev_, 4),
                      'vacuum_left_minus_right_meV': round((evl - evr) * 1000, 2), 'EA_eV': r['EA_eV'], 'IP_eV': r['IP_eV'],
                      'mstar_inplane_PBE_m0': m, 'dm_PBE_m0': round(m - m_b, 4) if m else None,
                      'E2_minus_E1_Gamma_eV': round(e21, 4),
                      'residual_total_force_Ry_bohr': r['total_force_Ry_bohr']}
    ts2 = two_step('slab2_relax_c2'); ts1 = two_step('slab1r_final_cpu')
    dec2, dev2 = ts2['a/2']['dEc_eV'], ts2['a/2']['dEv_eV']
    ea2 = slabs['2.0']['EA_eV']
    for lab, s in slabs.items():
        if lab == '2.0':
            s['dEc_PBE_eV'], s['dEv_PBE_eV'], s['dEc_route'] = dec2, dev2, 'two-step alignment, a/2 window (re-computed)'
            s['two_step_detail'] = ts2
        else:
            s['dEc_PBE_eV'] = round(dec2 + ea2 - s['EA_eV'], 4)
            s['dEv_PBE_eV'] = round(s['dEc_PBE_eV'] - s['dEg_PBE_eV'], 4)
            s['dEc_route'] = '2 nm two-step + same-termination EA difference'
        if lab == '1.0':
            s['two_step_detail_no_interior'] = ts1
        s['CB_share'] = round(s['dEc_PBE_eV'] / s['dEg_PBE_eV'], 3)
        s['dEg_HSEcorr_eV'] = [round(r1 * s['dEg_PBE_eV'], 4), round(r3 * s['dEg_PBE_eV'], 4)]
        s['dEc_HSEcorr_eV'] = [round(r1 * s['dEc_PBE_eV'], 4), round(r3 * s['dEc_PBE_eV'], 4)]
        s['Eg_HSE_abs_eV'] = [round(hse['nc_hse_bulk_q3_f160_e80'] + r1 * s['dEg_PBE_eV'], 3), round(hse['nc_hse_bulk_e80'] + r3 * s['dEg_PBE_eV'], 3)]
        # bulk-equivalent vacuum-referenced values for this termination
        s['EA_bulk_equiv_eV'] = round(s['EA_eV'] + s['dEc_PBE_eV'], 4)
        s['IP_bulk_equiv_eV'] = round(s['IP_eV'] + s['dEv_PBE_eV'], 4)
    out['slabs'] = slabs
    out['bulk']['EA_bulk_equiv_PBE_Hterm001_eV'] = round(ea2 + dec2, 4)
    out['bulk']['IP_bulk_equiv_PBE_Hterm001_eV'] = round(slabs['2.0']['IP_eV'] + dev2, 4)

    # ---- surface states
    out['surface_states'] = {lab: surface_weights(job) for lab, job in SURFACE_CHECK.items()}
    # proxy: the pure 1 nm slab has no projwfc; its W twin has (VB top = band 311, host CB bottom = 312)
    out['surface_states']['1.0_proxy_IWO'] = surface_weights('iwo_slab1_final_cpu', 311)
    out['surface_states']['2.0_IWO'] = surface_weights('iwo_slab2_final_cpu', 663)

    # ---- masses and Nc
    nc = {}
    for lab, s in list(slabs.items()) + [('bulk', None)]:
        m_pbe = m_b if lab == 'bulk' else s['mstar_inplane_PBE_m0']
        dm = 0.0 if lab == 'bulk' else s['dm_PBE_m0']
        m_v2 = MSTAR_EXP_BULK + dm
        m_ratio = MSTAR_EXP_BULK * m_pbe / m_b
        rec = {'m_PBE': m_pbe, 'm_V2_convention': round(m_v2, 4), 'm_ratio_convention': round(m_ratio, 4),
               'Nc3D_V2_cm3': float(f'{nc3d(m_v2):.4e}'), 'Nc3D_ratio_cm3': float(f'{nc3d(m_ratio):.4e}')}
        if lab != 'bulk':
            t_nom = float(lab)
            # single-subband quasi-2D: N2D/t (Boltzmann limit), second subband weight exp(-E21/kT)
            w2 = math.exp(-s['E2_minus_E1_Gamma_eV'] / KT)
            for conv, mm in (('V2', m_v2), ('ratio', m_ratio)):
                rec[f'Nc_q2D_{conv}_cm3'] = float(f'{n2d(mm) / (t_nom * 1e-7) * (1 + w2):.4e}')
            rec['N2D_V2_cm2'] = float(f'{n2d(m_v2):.4e}')
            rec['second_subband_Boltzmann_weight'] = float(f'{w2:.2e}')
            rec['q2D_over_3D_V2'] = round(rec['Nc_q2D_V2_cm3'] / rec['Nc3D_V2_cm3'], 3)
            rec['equivalent_band_shift_meV'] = round(-KT * math.log(rec['q2D_over_3D_V2']) * 1000, 1)
        nc[lab] = rec
    out['mass_and_Nc'] = nc
    # CB non-parabolicity (Kane form), bulk [100] and the in-plane [100] direction of the slabs
    npb = {'bulk': nonparabolic(QE / 'bulk_In2O3_protocol' / 'bands_gamma.out', 176)}
    for lab, s in slabs.items():
        npb[lab] = nonparabolic(R / s['job'] / 'bands.out', s['n_occ'])
    out['nonparabolicity'] = npb

    # ---- IWO
    iwo = {}
    for lab, job, scf, npure, twin in IWO:
        d = R / job
        wk, ev, ef, nel = all_eigs(d / scf)
        deg = float(re.search(r'degauss\s*=\s*([\d.eEdD+-]+)', (d / (scf.replace('.out', '.in'))).read_text()).group(1).replace('d', 'e')) * RY
        occ = np.zeros(len(ev[0]))
        for k, w in enumerate(wk):
            for n, e in enumerate(ev[k]):
                occ[n] += w * wgauss_mv((ef - e) / deg)
        _, kb = projwfc(next(d.glob('projwfc_*.out')))
        nv = npure - 1
        g = 0   # first k-point = Gamma for all four grids (checked: k(1) = (0,0,0))
        bands = {}
        for n in range(nv - 1, nv + 7):
            ks = [k for k in kb if n in k]
            bands[n] = {'E_Gamma_minus_EF_eV': round(kb[g][n][0] - ef, 3),
                        'Wd_Gamma': round(kb[g][n][1].get('Wd', 0.0), 3),
                        'Wd_kavg': round(float(np.mean([k[n][1].get('Wd', 0.0) for k in ks])), 3),
                        'Ins_kavg': round(float(np.mean([k[n][1].get('Ins', 0.0) for k in ks])), 3),
                        'Op_kavg': round(float(np.mean([k[n][1].get('Op', 0.0) for k in ks])), 3),
                        'electrons': round(float(occ[n - 1]), 3)}
        vb, cb = kb[g][nv][0], kb[g][nv + 1][0]
        wd_count = sum(w * wgauss_mv((ef - ev[k][n - 1]) / deg) * kb[k][n][1].get('Wd', 0.0)
                       for k, w in enumerate(wk) for n in range(nv + 1, len(ev[k]) + 1) if n in kb[k])
        # W-5d-rich level: lowest band above the host CB bottom with W d weight >= 0.30 at Gamma
        wl = next(n for n in range(nv + 2, nv + 12) if kb[g][n][1].get('Wd', 0.0) >= 0.30)
        cell, sym, cart = read_struct(d / ('scf.in' if scf == 'scf.out' else scf.replace('.out', '.in')))
        n_cat = sum(s in ('In', 'W') for s in sym)
        vol = abs(np.linalg.det(cell)) * 1e-24
        rec = {'job': job, 'n_electrons': nel, 'n_VB_top_band': nv, 'E_F_eV': ef, 'degauss_eV': round(deg, 4),
               'W_cation_fraction': round(1 / n_cat, 4), 'electrons_above_VB_top': round(float(occ[nv:].sum()), 3),
               'electrons_in_host_CB_bottom_band': round(float(occ[nv]), 3),
               'W5d_projected_electrons': round(float(wd_count), 3),
               'gap_VBtop_to_hostCB_Gamma_eV': round(cb - vb, 4), 'EF_minus_hostCB_Gamma_eV': round(ef - cb, 4),
               'W_rich_band': wl, 'W_rich_band_minus_hostCB_Gamma_eV': round(kb[g][wl][0] - cb, 4),
               'W_rich_band_Wd_Gamma': round(kb[g][wl][1].get('Wd', 0.0), 3), 'bands': bands}
        if lab.startswith('bulk'):
            rec['donated_electron_density_cm3'] = float(f'{3 / vol:.3e}')
        else:
            t_hh, a1, a2 = hh_thickness_nm(job)
            area = abs(np.linalg.det(cell[:2, :2])) * 1e-16
            rec['donated_sheet_density_cm2'] = float(f'{3 / area:.3e}')
            rec['donated_electron_density_cm3'] = float(f'{3 / (area * t_hh * 1e-7):.3e}')
            ev_, evl, evr = vacuum(job)
            rec.update({'E_vac_eV': round(ev_, 4), 'vacuum_left_minus_right_meV': round((evl - evr) * 1000, 2),
                        'EA_hostCB_eV': round(ev_ - cb, 4), 'IP_VBtop_eV': round(ev_ - vb, 4), 'work_function_eV': round(ev_ - ef, 4)})
            if twin:
                tw = slab_one(R / twin)
                rec['pure_twin'] = {'job': twin, 'gap_eV': tw['gap_eV'], 'EA_eV': tw['EA_eV'], 'IP_eV': tw['IP_eV']}
                rec['W_effect'] = {'dGap_eV': round(rec['gap_VBtop_to_hostCB_Gamma_eV'] - tw['gap_eV'], 4),
                                   'dEA_eV': round(rec['EA_hostCB_eV'] - tw['EA_eV'], 4), 'dIP_eV': round(rec['IP_VBtop_eV'] - tw['IP_eV'], 4)}
        iwo[lab] = rec
    out['iwo'] = iwo

    # ---- thickness laws (relaxed H-to-H thickness; 0.51 nm excluded: In(OH)3-like, outside the recipe)
    pts = ['0.75', '1.0', '2.0']
    tt = np.array([slabs[l]['thickness_HH_nm'] for l in pts])
    laws = {}
    for key, name in (('dEg_PBE_eV', 'dEg'), ('dEc_PBE_eV', 'dEc'), ('dm_PBE_m0', 'dm')):
        y = np.array([slabs[l][key] for l in pts])
        a3, p3 = power_fit(tt, y)
        a2, p2 = power_fit(tt[1:], y[1:])
        laws[name] = {'fit3_a': round(a3, 5), 'fit3_p': round(p3, 5), 'fit3_points_t_nm': tt.round(3).tolist(),
                      'fit3_rel_residuals': [round(float(v), 3) for v in (a3 * tt ** -p3 / y - 1)],
                      'fit2_1and2nm_a': round(a2, 5), 'fit2_1and2nm_p': round(p2, 5),
                      'at_t_nm': {str(t): {'fit3': round(a3 * t ** -p3, 4), 'fit2_HH': round(a2 * t ** -p2, 4)} for t in (2.0, 6.3, 13.2)}}
    # effective-mass box for E2-E1 through the 1 and 2 nm DFT spacings: E21 = 3 hbar^2 pi^2 / (2 m_z (t + delta)^2)
    e1, e2 = slabs['1.0']['E2_minus_E1_Gamma_eV'], slabs['2.0']['E2_minus_E1_Gamma_eV']
    t1, t2 = slabs['1.0']['thickness_HH_nm'], slabs['2.0']['thickness_HH_nm']
    s_ = math.sqrt(e1 / e2); delta = (t2 - s_ * t1) / (s_ - 1)
    mz = 3 * math.pi ** 2 * H2M / 100 / (e2 * (t2 + delta) ** 2)   # H2M in eV A^2 -> eV nm^2 /100
    box = {'delta_nm': round(delta, 3), 'm_z_m0': round(mz, 4), 'label': 'MODEL fitted to two DFT spacings (2 parameters, 2 points: exact, no test)'}
    v2w = {'V2_dEg': (0.83997, 1.34569), 'V2_dEc': (0.78504, 1.504)}
    tab = {}
    for t in (2.0, 6.3, 13.2):
        e21 = 3 * math.pi ** 2 * H2M / 100 / (mz * (t + delta) ** 2)
        # multi-subband Boltzmann sum with infinite-well level ratios E_n - E_1 = (n^2 - 1) E21 / 3
        ssum = sum(math.exp(-(n * n - 1) * e21 / 3 / KT) for n in range(1, 400))
        m_v2 = MSTAR_EXP_BULK + laws['dm']['at_t_nm'][str(t)]['fit3']
        q2d = n2d(m_v2) / (t * 1e-7) * ssum
        tab[str(t)] = {'E21_box_eV': round(e21, 4), 'subband_sum': round(ssum, 3), 'Nc_q2D_box_cm3': float(f'{q2d:.4e}'),
                       'Nc3D_V2_cm3': float(f'{nc3d(m_v2):.4e}'), 'ratio': round(q2d / nc3d(m_v2), 3),
                       'V2_dEc_eV': round(v2w['V2_dEc'][0] * t ** -v2w['V2_dEc'][1], 4), 'V2_dEg_eV': round(v2w['V2_dEg'][0] * t ** -v2w['V2_dEg'][1], 4)}
    box['at_t_nm'] = tab
    laws['subband_box'] = box
    out['laws'] = laws

    # ---- ATLAS values at the device thicknesses (illustration; V2 bulk anchors)
    atl = {}
    for t in (2.0, 6.3, 13.2):
        dEg = laws['dEg']['at_t_nm'][str(t)]['fit3']; dEc = laws['dEc']['at_t_nm'][str(t)]['fit3']
        atl[str(t)] = {'EG300_eV': round(EG_BULK_TCAD + dEg, 4), 'AFFINITY_eV': round(CHI_BULK_TCAD - dEc, 4),
                       'EG300_HSEscaled_eV': round(EG_BULK_TCAD + r1 * dEg, 4), 'AFFINITY_HSEscaled_eV': round(CHI_BULK_TCAD - r1 * dEc, 4),
                       'NC300_3D_V2conv_cm3': tab[str(t)]['Nc3D_V2_cm3'], 'NC300_q2D_box_cm3': tab[str(t)]['Nc_q2D_box_cm3']}
    out['atlas_at_device_thickness'] = atl
    (HERE / 'dft_inputs_raw.json').write_text(json.dumps(out, indent=1))
    (HERE / 'dft_inputs.json').write_text(json.dumps(curate(out), indent=1))
    print('wrote dft_inputs_raw.json and dft_inputs.json in', HERE)


# ---------------------------------------------------------------- curated, labelled output
RES = 'qe_workflow/cern_htcondor/results/'


def V(value, unit, label, source, note=None):
    d = {'value': value, 'unit': unit, 'label': label, 'source': source}
    if note:
        d['note'] = note
    return d


def curate(o):
    s, nc, npb, ss, iw, lw, hs = o['slabs'], o['mass_and_Nc'], o['nonparabolicity'], o['surface_states'], o['iwo'], o['laws'], o['hse_check']
    r1, r3 = hs['ratio_dEg_HSE_over_PBE_q1'], hs['ratio_worst_case_q3_bulk']
    C = 'COMPUTED'
    cur = {
        'schema': 'IWO_DFT_TO_TCAD_inputs_v1',
        'generated_utc': o['generated_utc'],
        'generator': 'analysis_2026-10-10_campaign/dft_to_tcad_extract.py (reads existing QE outputs only; full machine output in dft_inputs_raw.json)',
        'document': 'analysis_2026-10-10_campaign/DFT_TO_TCAD.md',
        'labels': {'COMPUTED': 'from our DFT output files (file cited)', 'MEASURED': 'measured on the target devices',
                   'LITERATURE': 'published value (cited)', 'FITTED': 'fitted; the data it was fitted to is named',
                   'ASSUMED': 'chosen without data', 'CALCULATED': 'closed-form formula applied to labelled inputs',
                   'MODEL': 'simple physical model with parameters fitted to COMPUTED points (named)'},
        'scope': ('PAW-PBE, crystalline bixbyite In2O3(001) slabs with H/OH termination in vacuum (Lin et al. 2022 recipe) and '
                  'crystalline W cells; the devices are sputtered, largely amorphous IWO on Al2O3. Only slab-minus-bulk '
                  'differences are proposed for TCAD; absolute PBE gaps and vacuum levels are reported, not proposed.'),
        'thickness_definition': ('thickness_HH_nm = distance between the outermost H planes of the relaxed slab (scf.in); '
                                 'labels 0.51/0.75/1.0/2.0 are the build targets; V2 laws used Lin labels 0.95/1.98 for the 1/2 nm films '
                                 '(H-H 0.930/1.962). Device thicknesses 2.0/6.3/13.2 nm are nominal (measurement method unknown).'),
    }
    b = o['bulk']
    cur['bulk'] = {
        'Eg_PBE_eV': V(b['Eg_fundamental_PBE_eV'], 'eV', C, 'qe_workflow/bulk_In2O3_protocol/bands_path.out'),
        'Eg_HSE06_eV': V(hs['Eg_bulk_HSE_eV'], 'eV', C, RES + 'nc_hse_bulk_q3_f160_e80, nc_hse_bulk_e80 (scf.out)',
                         'NC, PBE lattice 10.306 A; range = EXX q-grid 3x3x3 .. 1x1x1; not used for EG300 (below the literature bulk value)'),
        'mstar_PBE_m0': V(b['mstar_PBE_m0'], 'm0', C, 'qe_workflow/bulk_In2O3_protocol/bands_gamma.out'),
        'kane_alpha_PBE_per_eV': V(npb['bulk']['alpha_per_eV'], '1/eV', C, 'bands_gamma.out, [100], E <= 0.45 eV',
                                   'PBE gap too small -> alpha overestimated; not usable in ATLAS DD for a user material'),
        'EA_bulk_equivalent_eV': V(b['EA_bulk_equiv_PBE_Hterm001_eV'], 'eV', C,
                                   RES + 'slab2_relax_c2 (EA) + two-step dEc(2 nm)', 'H/OH-terminated (001) surface, PBE; termination-specific; NOT proposed for AFFINITY'),
        'IP_bulk_equivalent_eV': V(b['IP_bulk_equiv_PBE_Hterm001_eV'], 'eV', C, RES + 'slab2_relax_c2 (IP) + two-step dEv(2 nm)'),
        'alignment_constants_eV': V({'E_v_minus_Vavg': DV_B, 'E_c_minus_Vavg': DC_B}, 'eV', C,
                                    RES + 'RESULTS_LOG.md (2026-10-05)', 'bulk_v11.cube deleted 2026-10-06; constants not re-computed here'),
        'TCAD_Eg_bulk_eV': V(EG_BULK_TCAD, 'eV', 'LITERATURE', 'Fan2021 Nanomaterials Sec. 3 (config/iwo_material_model_v2.yaml)'),
        'TCAD_chi_bulk_eV': V(CHI_BULK_TCAD, 'eV', 'LITERATURE', 'Fan2021 Nanomaterials Sec. 3 (config/iwo_material_model_v2.yaml)',
                              'degenerate with gate work function and Qf (analysis_2026-09-25/SYNTHESIS.md)'),
        'TCAD_mstar_bulk_m0': V(MSTAR_EXP_BULK, 'm0', 'LITERATURE', 'Stokey2021 JAP, optical Hall, In2O3 (V2)'),
        'Nc300_bulk_cm3': V(nc['bulk']['Nc3D_V2_cm3'], 'cm^-3', 'CALCULATED', '2(2 pi m* kT/h^2)^1.5, m* = 0.208'),
    }
    films = {}
    for lab in ('2.0', '1.0', '0.75', '0.51'):
        x, n_, a = s[lab], nc[lab], npb[lab]
        src = RES + x['job']
        f = {
            'job': x['job'],
            'validity': {'2.0': 'bulk-like interior; both band edges interior states (projwfc)',
                         '1.0': 'no bulk-like interior; dEc from the EA route; VB edge is an OH surface state (proxy: W twin projwfc)',
                         '0.75': 'VB edge is an OH surface state at one surface (vacuum asymmetry 27 meV); CB edge not surface-dominated',
                         '0.51': 'OUTSIDE THE RECIPE: relaxes into an In(OH)3-like layer; excluded from all laws'}[lab],
            'thickness_HH_nm': V(x['thickness_HH_nm'], 'nm', C, src + '/scf.in'),
            'inplane_cell_A': V(x['inplane_a_A'], 'A', C, src + '/scf.in', 'bulk 10.306 A'),
            'gap_PBE_eV': V(x['gap_PBE_eV'], 'eV', C, src + '/scf.out (last HOMO/LUMO line)'),
            'dEg_PBE_eV': V(x['dEg_PBE_eV'], 'eV', C, src + '/scf.out minus bulk 0.8887 eV'),
            'dEg_HSEcorrected_eV': V(x['dEg_HSEcorr_eV'], 'eV', 'CALCULATED',
                                     f'PBE dEg x HSE/PBE ratio {r1}..{r3} (measured at 1 nm only)',
                                     None if lab == '1.0' else 'ASSUMED that the 1 nm ratio transfers to this thickness'),
            'dEc_PBE_eV': V(x['dEc_PBE_eV'], 'eV', C, src + ' (' + x['dEc_route'] + ')'),
            'dEv_PBE_eV': V(x['dEv_PBE_eV'], 'eV', C, 'dEc - dEg (identity)'),
            'CB_share': V(x['CB_share'], '-', C, 'dEc/dEg'),
            'dEc_HSEcorrected_eV': V(x['dEc_HSEcorr_eV'], 'eV', 'CALCULATED', f'PBE dEc x {r1}..{r3}',
                                     'ASSUMED: HSE keeps the PBE CB share (no HSE planar average exists)'),
            'EA_eV': V(x['EA_eV'], 'eV', C, src + '/*_avg.dat + scf.out', 'vacuum-referenced CBM = -EA (H/OH termination, PBE)'),
            'IP_eV': V(x['IP_eV'], 'eV', C, src + '/*_avg.dat + scf.out'),
            'vacuum_asymmetry_meV': V(x['vacuum_left_minus_right_meV'], 'meV', C, src + '/*_avg.dat (left minus right plateau)'),
            'mstar_inplane_PBE_m0': V(x['mstar_inplane_PBE_m0'], 'm0', C, src + '/bands.out (|k| <= 0.05 1/A, [100])'),
            'dm_PBE_m0': V(x['dm_PBE_m0'], 'm0', C, 'film minus bulk 0.159'),
            'mstar_TCAD_V2convention_m0': V(n_['m_V2_convention'], 'm0', 'CALCULATED', '0.208 (LITERATURE) + dm (COMPUTED)'),
            'kane_alpha_PBE_per_eV': V(a['alpha_per_eV'], '1/eV', C, src + '/bands.out, in-plane [100]'),
            'E2_minus_E1_Gamma_eV': V(x['E2_minus_E1_Gamma_eV'], 'eV', C, src + '/bands.out (Gamma)', 'subband spacing; >> kT = 0.026 eV'),
            'Nc300_3D_V2_cm3': V(n_['Nc3D_V2_cm3'], 'cm^-3', 'CALCULATED', '2(2 pi m* kT/h^2)^1.5 with the V2-convention mass (what V2 does)'),
            'Nc300_quasi2D_cm3': V(n_['Nc_q2D_V2_cm3'], 'cm^-3', 'CALCULATED',
                                   'N2D/t = m* kT/(pi hbar^2 t), single subband (second-subband weight exp(-E21/kT) included), t = label thickness',
                                   'NEW candidate; Boltzmann-equivalent (subthreshold); in the degenerate on-state the 3-D F1/2 form overstates n'),
            'quasi2D_over_V2_3D': V(n_['q2D_over_3D_V2'], '-', 'CALCULATED', 'ratio of the two NC300 values'),
            'equivalent_Ec_shift_meV': V(n_['equivalent_band_shift_meV'], 'meV', 'CALCULATED', '-kT ln(ratio)'),
        }
        if lab in ss:
            q = ss[lab]
            f['surface_state_check'] = V({'OH_number_share': q['surface_OH_number_share'],
                                          'VBM_OH_weight': q['VBM']['weight_on_surface_OH'], 'CBM_OH_weight': q['CBM']['weight_on_surface_OH'],
                                          'VBM_z_profile': q['VBM']['z_profile_8_slices'], 'CBM_z_profile': q['CBM']['z_profile_8_slices']},
                                         '-', C, RES + ('slab2r_pdos_cpu' if lab == '2.0' else x['job']) + '/projwfc_*.out (measure of surface_state_check.py)')
        if lab == '1.0':
            q = ss['1.0_proxy_IWO']
            f['surface_state_check'] = V({'OH_number_share': q['surface_OH_number_share'],
                                          'VBM_OH_weight': q['VBM']['weight_on_surface_OH'], 'CBM_OH_weight': q['CBM']['weight_on_surface_OH'],
                                          'VBM_z_profile': q['VBM']['z_profile_8_slices'], 'CBM_z_profile': q['CBM']['z_profile_8_slices']},
                                         '-', C, RES + 'iwo_slab1_final_cpu/projwfc (bands 311/312)',
                                         'PROXY: the pure 1 nm slab has no projwfc; W twin used (VB top = band 311, host CB = 312)')
        films[lab] = f
    cur['films'] = films
    wcell = {}
    for lab, x in iw.items():
        e = {'job': x['job'],
             'W_cation_fraction': V(x['W_cation_fraction'], '-', C, RES + x['job'] + '/scf.in'),
             'donated_electron_density_cm3': V(x['donated_electron_density_cm3'], 'cm^-3', 'CALCULATED', '3 electrons per cell / volume (slab: area x H-H thickness)'),
             'VB_top_band': V(x['n_VB_top_band'], '-', C, 'projwfc: O 2p; = n_pure - 1 (PAW band count)'),
             'EF_minus_hostCB_Gamma_eV': V(x['EF_minus_hostCB_Gamma_eV'], 'eV', C, RES + x['job'] + ' (scf + projwfc)'),
             'W5d_rich_level_minus_hostCB_Gamma_eV': V(x['W_rich_band_minus_hostCB_Gamma_eV'], 'eV', C,
                                                       RES + x['job'] + ' projwfc (lowest band above the host CB bottom with W 5d >= 0.30 at Gamma)',
                                                       'positive = resonant in the conduction band (no gap state)'),
             'electrons_in_host_CB_bottom_band': V(x['electrons_in_host_CB_bottom_band'], 'e/cell', C, 'MV smearing occupations of scf eigenvalues'),
             'W5d_projected_electrons_of_3': V(x['W5d_projected_electrons'], 'e/cell', C, 'sum over occupied states above the VB top of occupation x W 5d weight'),
             'gap_VBtop_to_hostCB_Gamma_eV': V(x['gap_VBtop_to_hostCB_Gamma_eV'], 'eV', C, 'projwfc energies at Gamma'),
             }
        if 'EA_hostCB_eV' in x:
            e['EA_hostCB_eV'] = V(x['EA_hostCB_eV'], 'eV', C, RES + x['job'] + '/*_avg.dat')
            e['work_function_eV'] = V(x['work_function_eV'], 'eV', C, 'E_vac - E_F')
            e['W_effect_vs_pure_twin_eV'] = V(x['W_effect'], 'eV', C, 'IWO minus ' + x['pure_twin']['job'],
                                              'at 1.4-3e21 cm^-3 donated electrons (E_F 1.2 eV into the CB): band filling + W potential; NOT transferable to device densities')
        wcell[lab] = e
    cur['W'] = {
        'site_preference': V({'E_8b_minus_E_24d_eV': 0.258, 'preferred': '24d'}, 'eV', C, RES + 'summary.json (iwo_W8b, iwo_W24d relax.out)'),
        'oxidation_state': V('W6+ (mean W-O 1.98 A vs Shannon W6+ 1.98, W4+ 2.04)', '-', C, RES + 'summary.json', 'Shannon 1976 radii LITERATURE'),
        'magnetism': V('0.6-0.7 muB/cell at 3x3x3, ~20 meV below non-magnetic', '-', C, RES + 'RESULTS_LOG.md 2026-09-29', 'preliminary (coarse k sampling)'),
        'cells': wcell,
        'conclusion_for_TCAD': ('INFERRED from COMPUTED level positions: the W-5d-rich level lies 1.2-1.8 eV ABOVE the host CB bottom; '
                                'at device electron densities (<1e19 cm^-3, E_F below E_C) it is empty, so W is a fully ionized donor and '
                                'contributes no gap state and no electron trap. PBE only (no HSE for W cells).'),
    }
    cur['hse_check'] = V({'gaps_Gamma_eV': hs['gaps_Gamma_eV'], 'ratio_q1': r1, 'ratio_worst_case_q3': r3}, '-', C,
                         RES + 'nc_* folders (scf.out)', hs['note'])
    cur['laws'] = {
        'dEg_eV': V({'a': lw['dEg']['fit3_a'], 'p': lw['dEg']['fit3_p'], 'form': 'a * t_HH^-p', 'points_t_HH_nm': lw['dEg']['fit3_points_t_nm'],
                     'rel_residuals': lw['dEg']['fit3_rel_residuals'], 'at_t_nm': {k: v['fit3'] for k, v in lw['dEg']['at_t_nm'].items()}},
                    'eV', 'FITTED to COMPUTED DFT points (H-H 0.695/0.930/1.962 nm), no device data', 'dft_inputs_raw.json laws.dEg',
                    'values at 6.3 and 13.2 nm are extrapolations (no DFT point above 2 nm)'),
        'dEc_eV': V({'fit3': {'a': lw['dEc']['fit3_a'], 'p': lw['dEc']['fit3_p'], 'rel_residuals': lw['dEc']['fit3_rel_residuals'],
                              'at_t_nm': {k: v['fit3'] for k, v in lw['dEc']['at_t_nm'].items()}},
                     'fit2_1and2nm_HH': {'a': lw['dEc']['fit2_1and2nm_a'], 'p': lw['dEc']['fit2_1and2nm_p'],
                                         'at_t_nm': {k: v['fit2_HH'] for k, v in lw['dEc']['at_t_nm'].items()}},
                     'V2_law_labels': {'a': 0.78504, 'p': 1.504, 'at_t_nm': {k: v['V2_dEc_eV'] for k, v in lw['subband_box']['at_t_nm'].items()}},
                     'box_E1_equals_E21_over_3': {k: round(v['E21_box_eV'] / 3, 4) for k, v in lw['subband_box']['at_t_nm'].items()}},
                    'eV', 'FITTED to COMPUTED DFT points, no device data', 'dft_inputs_raw.json laws.dEc',
                    'spread at 6.3 nm 0.046-0.062 eV and at 13.2 nm 0.013-0.024 eV (PBE) = extrapolation uncertainty'),
        'dm_m0': V({'a': lw['dm']['fit3_a'], 'p': lw['dm']['fit3_p'], 'rel_residuals': lw['dm']['fit3_rel_residuals'],
                    'at_t_nm': {k: v['fit3'] for k, v in lw['dm']['at_t_nm'].items()}},
                   'm0', 'FITTED to COMPUTED DFT points, no device data', 'dft_inputs_raw.json laws.dm'),
        'subband_box': V(lw['subband_box'], '-', 'MODEL', 'E21 = 3 hbar^2 pi^2 / (2 m_z (t + delta)^2) through the 1 and 2 nm E21 (2 parameters, 2 points)',
                         'used only to illustrate the 2-D -> 3-D crossover of NC300 at 6.3 and 13.2 nm'),
        'hse_scaling': V([r1, r3], '-', 'ASSUMED transfer of the COMPUTED 1 nm ratio', 'hse_check', 'multiply dEg and dEc'),
    }
    cur['t4_points_for_make_v2_model'] = V({f"{s[l]['thickness_HH_nm']:.3f}": {'dEc': s[l]['dEc_PBE_eV'], 'dEg': s[l]['dEg_PBE_eV'], 'dm': s[l]['dm_PBE_m0'], 'source': s[l]['job']}
                                            for l in ('0.75', '0.51')}, '-', C,
                                           'same format as analysis_2026-10-06_V2/t4_prepare.py (thin_dft.json); not written there',
                                           'T4 is on hold (decision D-07, "not yet"); 0.461 nm film outside the recipe')
    cur['atlas_mapping'] = [
        {'atlas': 'EG300', 'law': 'Eg_bulk + dEg(t)', 'Eg_bulk': 'LITERATURE 3.05 eV (Fan2021)', 'dEg': 'COMPUTED PBE points -> FITTED law; optional HSE x1.06-1.11 (ASSUMED transfer)',
         'V2': 'used (2-point PBE law, Lin labels)', 'new': '0.695 nm point; 3-point law; HSE option', 'effect': 'enters only n_i (holes not solved): negligible for I_D (INFERRED)'},
        {'atlas': 'AFFINITY', 'law': 'chi_bulk - dEc(t)', 'chi_bulk': 'LITERATURE 4.3 eV (Fan2021); DFT bulk-equivalent EA 4.78 eV (PBE, H-(001)) reported but not proposed',
         'dEc': 'COMPUTED PBE (two-step at 2 nm, EA route below) -> FITTED law; optional HSE x1.06-1.11',
         'V2': 'used (0.281 @ 1.98, 0.848 @ 0.95)', 'new': '0.695 nm point 1.059 eV; extrapolation band at 6.3/13.2 nm; HSE option (+17..+31 meV at 2 nm)'},
        {'atlas': 'NC300', 'law': 'V2: 2(2 pi m* kT/h^2)^1.5, m* = 0.208 + dm(t); candidate: N2D/t at t <= 2 nm',
         'inputs': 'dm COMPUTED; E21 COMPUTED (single subband at <= 2 nm); 0.208 LITERATURE',
         'V2': 'used (3-D form)', 'new': 'quasi-2D value 1.38e19 cm^-3 at 2 nm (x4.3 vs V2 3.24e18; -37.5 meV equivalent)'},
        {'atlas': 'ME / ARICHN', 'law': 'ARICHN = 120.17 A/cm^2/K^2 x m*(t)', 'inputs': 'm*(t) as above',
         'V2': 'not used (S/D ideal ohmic)', 'new': 'only if Pd contacts are made Schottky; ME.TUNNEL is an oxide tunnelling mass and does not come from this DFT'},
        {'atlas': 'DOPING / Nd_eff', 'law': 'unchanged FITTED Nd0(1+(t/tc)^k)', 'inputs': 'W: resonant donor (level +1.2..+1.8 eV above E_C), fully ionized; 3 e per W',
         'V2': 'qualitative (Nd_eff kept fitted)', 'new': '2 nm W slab: 97 % of the donated electrons in the host CB, 3 % W-5d projected'},
        {'atlas': 'DEFECTS / INTDEFECTS / INTERFACE QF', 'law': 'unchanged (ASSUMED / FITTED)',
         'inputs': 'no gap state from W; CB edge interior at every t >= 0.695 nm; OH states only at the VB edge (<= 1 nm, and 2 nm with W)',
         'V2': 'not DFT-based', 'new': 'DFT gives no basis for acceptor-like surface states near E_C on an H/OH surface; real interfaces not computed'},
        {'atlas': 'MUN (mu_band)', 'law': 'unchanged FITTED', 'inputs': 'm*(2 nm)/m*(13.2 nm) = 1.20 -> constant-tau mobility ratio 0.83',
         'V2': 'not used', 'new': 'the mass explains at most a factor 0.83 of the fitted mu_band ratio 0.28 (INFERRED)'},
    ]
    cur['v2_used_vs_new'] = {
        'used_by_V2': ['dEg at 0.95/1.98 nm (0.900/0.335 eV, PBE)', 'dEc at 0.95/1.98 nm (0.848/0.281 eV)',
                       'dm at 0.95/1.98 nm (0.122/0.047 m0) on top of the 0.208 literature bulk mass', 'NC300 from the 3-D formula',
                       'HSE ratio only as validation (not applied)', 'W: qualitative (Nd_eff stays fitted)', '2 nm band edges bulk-like (qualitative)'],
        'new_here': ['0.695 nm (and 0.461 nm, outside the recipe) gap, dEc, dm, EA/IP, E21', '3-point laws and extrapolation spread at 6.3/13.2 nm',
                     'HSE-scaled dEg/dEc option', 'quasi-2D NC300 at <= 2 nm from DFT m* and E21', 'subband spacings E21 (0.72 eV at 2 nm)',
                     'CB non-parabolicity (PBE)', 'surface character at 0.695/0.461/1 nm (proxy) and 2 nm with W',
                     '2 nm W slab: filling, W level, W effect on gap/EA', 'electron filling in all four W cells (MV occupations)',
                     'bulk-equivalent EA/IP (PBE, H-(001))', 'two-step dEc(2 nm) re-computed on the slab side'],
    }
    cur['gaps'] = [
        'Absolute Eg and electron affinity of amorphous IWO: PBE gap 0.89 eV, HSE06 2.07-2.11 eV at the PBE lattice; both below the literature bulk value; EA is termination-specific. EG300/AFFINITY bulk anchors stay LITERATURE.',
        'HSE band-edge partition (no HSE planar average); the HSE ratio exists only at 1 nm; the same CB share is ASSUMED.',
        'HSE for W cells: the position of the W 5d level beyond PBE is not computed.',
        'Effective mass of the W slabs (1 nm bands run aborted; 2 nm run without bands).',
        'Films thicker than 2 nm: no slab; dEc/dEg/dm at 6.3 and 13.2 nm are extrapolations (spread given).',
        'Compensation / effective donor density: no V_O, H, O_i or W-defect complexes computed (planned, COMPLETE_PLAN 2B item 3) -> Nd_eff stays FITTED.',
        'Interface states and fixed charge at Al2O3/IWO, and the air-exposed surface: not computed (planned, 2B item 4) -> Dit, Qf stay ASSUMED/FITTED.',
        'Band tails (N_t, W_TA) and localization: crystalline cells have no tails (amorphous series planned, 2A) -> stay FITTED.',
        'Dielectric constant (no DFPT): eps_r stays MEASURED 9.3 (Januar2026 SI).',
        'Mobility / scattering: only m* is computed -> mu_band stays FITTED.',
        'Temperature dependence (EGALPHA/EGBETA), gate-field (Stark) shift of the subbands, Pd/IWO contact barrier: not computed.',
    ]
    cur['crosscheck'] = {
        'by': 'Codex (codex-cli 0.162.0, read-only sandbox, independent scripts), 2026-10-10',
        'record': 'analysis_2026-10-10_campaign/codex_xcheck_2026-10-10.md',
        'agreement': ('gaps, EA, IP, H-H thicknesses, E21 and surface shares identical to the printed digits; masses within 0.001 m0 '
                      '(Codex fits through the origin); 2 nm W slab: VB top band 663, host CB 664, W-rich band 666 at +1.341 eV, '
                      'E_F - CB 1.238 eV, electrons 2.041/0.862/0.097 in bands 664/665/666, EA 4.746 eV - identical'),
    }
    return cur


if __name__ == '__main__':
    main()
