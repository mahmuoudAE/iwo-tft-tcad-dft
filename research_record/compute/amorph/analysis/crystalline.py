"""Reproduction of the crystalline results named in register section 3 ("12 Oct 18:00: analysis code frozen. It must
first reproduce the crystalline results: 3 % W-5d, Delta E_c 0.281 eV").

What the two numbers are (traced 2026-10-11):
  * "3 % W-5d": analysis_2026-10-10_campaign/dft_inputs_raw.json, iwo['2.0']['W5d_projected_electrons'] = 0.086 e of
    the 3 donated electrons (0.086 / 3 = 2.9 %) in the crystalline 2 nm W slab (In2O3(001), H-terminated, 1 W on 24d,
    176 atoms; run qe_workflow/cern_htcondor/results/iwo_slab2_final_cpu: QE 7.5 PAW-PBE, MV 0.01 Ry, k 3x3x1 -> 4
    irreducible k). Definition (dft_to_tcad_extract.py): sum over k (weights summing to 2) and over bands n > 663 of
    f_nk(MV, E_F of the run) x W-5d weight (W l = 2 components of the projwfc.x printout, unnormalised). 663 =
    (N_el - N_ex)/2 = (1329 - 3)/2, i.e. the section-1 N_v with N_ex = 3 (W6+ on an In3+ site, no added O).
    Reported as DFT_TO_TCAD.md "97 % of the three donated electrons are in the host conduction band. Only 3 % project
    onto W 5d orbitals".
  * "Delta E_c 0.281 eV": dft_inputs_raw.json slabs['2.0']['dEc_PBE_eV'] = 0.2813 (RESULTS_LOG.md 2026-10-05,
    "2 nm | two-step, a/2 window | +0.281"), pure relaxed 2 nm slab slab2_relax_c2: CBM (pw.x 'highest occupied,
    lowest unoccupied level') - [V_macro(z_c) + (E_c - <V>)_bulk], V_macro = box average of the pp.x plot_num 11 planar
    average over a/2 = 10.306/2 A, z_c = centre of the In z-range, (E_c - <V>)_bulk = 4.7985 eV (logged bulk constant;
    the bulk cube was deleted, so the bulk side is not recomputed, as in the original extraction).

This module recomputes both numbers with the package's own parsers (pw.x input/output, projwfc.x printout, average.x),
occupation function (MV, recomputed), section-1 N_v/N_ex accounting and macroscopic average.
"""
import json
import os
from pathlib import Path

import numpy as np

from . import qeio
from . import register as R
from .data import from_text
from .geometry import Structure, regions
from .section1 import Section1, box_average, macro_average

A_BULK = 10.306                 # A, relaxed PBE bulk lattice constant (dft_to_tcad_extract.A_BULK)
DC_BULK, DV_BULK = 4.7985, 3.9098   # E_c - <V>, E_v - <V> of bulk (eV), RESULTS_LOG.md 2026-10-05
TARGET_W5D_E = 0.086            # dft_inputs_raw.json iwo['2.0']['W5d_projected_electrons'] (3 decimals)
TARGET_DEC = 0.2813             # dft_inputs_raw.json slabs['2.0']['dEc_PBE_eV'] (4 decimals); register: 0.281
TOL_W5D_E = 0.0005              # half a unit of the logged last digit
TOL_DEC = 0.00005               # half a unit of the logged last digit


def default_root():
    env = os.environ.get('IWO_V1_ROOT')
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[4] / 'IWO_PHYSICS_CONSTRAINED_MODEL_V1'


def w5d_share(res_dir):
    d = Path(res_dir)
    data, st = from_text(d / 'scf.in', d / 'scf.out', next(d.glob('projwfc_*.out')))
    c = Section1(data, st, name='crystalline 2 nm W slab (iwo_slab2_final_cpu)', nex=3, mode='slab')
    above = c.n > c.N_v
    raw = float((c.fw[above] * c.W5d_raw[above]).sum())
    norm = float((c.fw[above] * c.W5d_norm[above]).sum())
    band = lambda n: float(c.fw[c.n == n].sum())
    return {
        'run': str(d), 'N_el': c.N_el, 'N_ex': c.N_ex, 'N_v': c.N_v, 'smearing': data.smearing,
        'degauss_eV': data.degauss_ev, 'E_F_eV': float(data.ef[0]),
        'max_abs_f_recomputed_minus_qe': c.occ_info.get('max_abs_f_recomputed_minus_qe'),
        'electrons_above_Nv': c.acc['electrons_above_Nv'], 'accounting_check': c.acc['check'],
        'W5d_electrons_raw': raw, 'W5d_share_raw': raw / 3.0,
        'W5d_electrons_section1_normalised': norm, 'W5d_share_section1_normalised': norm / 3.0,
        'electrons_band_664': band(664), 'electrons_band_665': band(665), 'electrons_band_666': band(666),
    }, c


def two_step_dec(res_dir, window_A=A_BULK / 2):
    d = Path(res_dir)
    avg = qeio.read_avg(next(d.glob('*_avg.dat')))
    out = qeio.read_pw_out(d / 'scf.out')
    g = qeio.read_pw_in(d / 'scf.in')
    vbm, cbm = out['homo_lumo_ev']
    zin = np.array([p[2] for p, s in zip(g['positions_A'], g['species']) if s == 'In']) / R.BOHR_A
    zc = 0.5 * (zin.min() + zin.max())
    vm = macro_average(avg['z_bohr'], avg['planar_ry'], window_A / R.BOHR_A)
    vc = float(np.interp(zc, avg['z_bohr'], vm)) * R.RY_EV
    win = np.abs(avg['z_bohr'] - zc) <= A_BULK / 8 / R.BOHR_A
    return {'run': str(d), 'CBM_eV': cbm, 'VBM_eV': vbm, 'V_macro_centre_eV': vc,
            'dEc_eV': cbm - (vc + DC_BULK), 'dEv_eV': vbm - (vc + DV_BULK),
            'plateau_spread_meV_centre_a_over_4': float(vm[win].max() - vm[win].min()) * R.RY_EV * 1000,
            'window_A': window_A, 'bulk_constants_eV': {'E_c - <V>': DC_BULK, 'E_v - <V>': DV_BULK}}


def plateau_diagnostic(res_dir):
    """The rc3 frozen alignment rule (section1.Section1._alignment: ASSUMED 5.153 A primary, 4.1224 / 6.1836 A
    sensitivity, all three kernels wholly inside the interior, common interval >= ALIGN_MIN_COMMON_SPAN_A = 2.0 A)
    applied to a crystalline slab's planar average. Diagnostic only; the crystalline reproduction uses the legacy
    two-step extraction (two_step_dec)."""
    d = Path(res_dir)
    g = qeio.read_pw_in(d / 'scf.in')
    st = Structure(g['species'], g['positions_A'], g['cell_A'])
    masks, info = regions(st, 'slab')
    avg = qeio.read_avg(next(d.glob('*_avg.dat')))
    from .geometry import z_in_frame
    zr = info['interior_z_range_A']
    widths = (R.ALIGN_PRIMARY_WINDOW_A,) + tuple(R.ALIGN_SENSITIVITY_WINDOWS_A)
    lo, hi = zr[0] + max(widths) / 2, zr[1] - max(widths) / 2
    res = {'run': str(d), 'interior_atoms': info['counts']['interior'], 'interior_z_range_A': zr,
           'common_interval_A': [lo, hi], 'common_span_A': hi - lo, 'required_span_A': R.ALIGN_MIN_COMMON_SPAN_A}
    z = z_in_frame(avg['z_bohr'], info, R.BOHR_A)
    sel = (z >= lo) & (z <= hi)
    if sel.sum() >= 2:
        for w in widths:
            v = box_average(avg['z_bohr'], avg['planar_ry'], w / R.BOHR_A)[sel] * R.RY_EV
            res[f'window_{w:g}_A'] = {'mean_eV': float(v.mean()), 'std_eV': float(v.std())}
        means = [res[f'window_{w:g}_A']['mean_eV'] for w in widths]
        res['mean_variation_eV'] = max(means) - min(means)
    res['rc3_rule_valid'] = bool(hi - lo >= R.ALIGN_MIN_COMMON_SPAN_A and sel.sum() >= 2
                                 and res[f'window_{R.ALIGN_PRIMARY_WINDOW_A:g}_A']['std_eV'] <= R.PLATEAU_STD_EV
                                 and res['mean_variation_eV'] <= R.ALIGN_MEAN_VARIATION_EV) if sel.sum() >= 2 else False
    return res


def reproduce(root=None):
    root = Path(root) if root else default_root()
    res_root = root / 'qe_workflow' / 'cern_htcondor' / 'results'
    out = {'check': 'crystalline reproduction (register section 3)', 'root': str(root)}
    w, c = w5d_share(res_root / 'iwo_slab2_final_cpu')
    t = two_step_dec(res_root / 'slab2_relax_c2')
    out['W5d'] = w
    out['dEc'] = t
    logged = root / 'analysis_2026-10-10_campaign' / 'dft_inputs_raw.json'
    if logged.is_file():
        j = json.loads(logged.read_text())
        out['logged_values'] = {'W5d_projected_electrons': j['iwo']['2.0']['W5d_projected_electrons'],
                                'dEc_PBE_eV': j['slabs']['2.0']['dEc_PBE_eV'],
                                'electrons_above_VB_top': j['iwo']['2.0']['electrons_above_VB_top'],
                                'electrons_in_host_CB_bottom_band': j['iwo']['2.0']['electrons_in_host_CB_bottom_band']}
    checks = {
        'W5d electrons (raw, as logged) = 0.086 +- 0.0005 e': abs(w['W5d_electrons_raw'] - TARGET_W5D_E) <= TOL_W5D_E,
        'W5d share rounds to 3 % (raw)': round(100 * w['W5d_share_raw']) == 3,
        'W5d share rounds to 3 % (section-1 normalised)': round(100 * w['W5d_share_section1_normalised']) == 3,
        'excess accounting: 3 e above N_v within 0.02 e': w['accounting_check'] == 'PASS',
        'Delta E_c = 0.2813 +- 0.00005 eV': abs(t['dEc_eV'] - TARGET_DEC) <= TOL_DEC,
        'Delta E_c rounds to 0.281 eV': round(t['dEc_eV'], 3) == 0.281,
    }
    out['checks'] = checks
    out['tolerances'] = {'W5d_electrons_e': TOL_W5D_E, 'dEc_eV': TOL_DEC,
                         'basis': 'half a unit of the last logged digit (dft_inputs_raw.json)'}
    try:
        out['diagnostic_plateau'] = [plateau_diagnostic(res_root / j) for j in ('slab2_relax_c2', 'slab1r_final_cpu')]
    except (StopIteration, FileNotFoundError, ValueError) as e:
        out['diagnostic_plateau'] = f'not computed: {e}'
    # smoke run of the full section-1 path on the crystalline W slab (text projections: approximate)
    he = c.host_edge
    out['smoke_section1_on_crystalline_W_slab'] = {
        'host_edge_eV': he['E_eV'], 'host_edge_state': he.get('state', {}) and
        {k: he['state'][k] for k in ('k', 'band', 'PR_n', 'W5d')},
        'E_F_minus_host_edge_eV': None if he['E_eV'] is None else float(c.data.ef[0] - he['E_eV']),
        'host_edge_unresolved': he['unresolved'],
        'note': 'text projections (components < 0.001 omitted): approximate; a sanity check, not a target'}
    out['status'] = 'REPRODUCED' if all(checks.values()) else 'NOT REPRODUCED'
    out['unresolved_checks'] = [k for k, v in checks.items() if not v]
    # every consumed input file, hashed (paths relative to the root)
    used = [res_root / 'iwo_slab2_final_cpu' / 'scf.in', res_root / 'iwo_slab2_final_cpu' / 'scf.out',
            next((res_root / 'iwo_slab2_final_cpu').glob('projwfc_*.out')),
            res_root / 'slab2_relax_c2' / 'scf.in', res_root / 'slab2_relax_c2' / 'scf.out',
            next((res_root / 'slab2_relax_c2').glob('*_avg.dat'))]
    if logged.is_file():
        used.append(logged)
    out['input_files'] = {p.relative_to(root).as_posix(): qeio.sha256(p) for p in used}
    return out
