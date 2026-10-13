#!/usr/bin/env python3
"""Build campaign_matrix.json for CAMPAIGN_DESIGN.md (2026-10-10).

Pure arithmetic and JSON output. It imports nothing from scripts/ and never calls deckbuild, run_atlas.py or
run_campaign.py. Every entry carries a ready 'campaign_entry' block in the config/campaign_*.json format of
scripts/run_campaign.py ({id, thickness, label, overrides, timeout, purpose[, mode]}). Overrides that use keys not
yet implemented are listed in 'requires_code' (see CAMPAIGN_DESIGN.md section 8); entries whose parameters depend on
an earlier stage carry 'params_rule' and placeholder tokens of the form {fit:<name>} or {sel:<name>}, which the
implementer resolves before writing the config file.

Run:  <venv>/Scripts/python.exe analysis_2026-10-10_campaign/make_campaign_matrix.py
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
from scipy.stats import qmc

HERE = Path(__file__).resolve().parent
FILMS = (2.0, 6.3, 13.2)
KEY = {2.0: '2p0', 6.3: '6p3', 13.2: '13p2', 31.8: '31p8'}

# ---------------------------------------------------------------- DFT laws (dft_inputs.json 'laws'; FITTED to COMPUTED DFT points)
DEC = (0.70147, 1.31669)      # dEc fit3 (H-H 0.695/0.930/1.962 nm)
DEG = (0.81431, 1.31518)      # dEg 3-point law
DM = (0.11116, 1.26387)       # dm* 3-point law
M_BULK = 0.208                # LITERATURE, Stokey 2021 (V2 convention)
DSR = 0.287                   # LITERATURE, Januar 2026 Fig. 5f (existing generator roughness factor)
CHI_BULK = 4.3                # LITERATURE, Fan 2021

M0, KB, HB, H = 9.1093837015e-31, 1.380649e-23, 1.054571817e-34, 6.62607015e-34

def dEc(t, f=1.0): return f * DEC[0] * t ** -DEC[1]
def dEg(t, f=1.0): return f * DEG[0] * t ** -DEG[1]
def dm(t): return DM[0] * t ** -DM[1]
def mstar(t): return M_BULK + dm(t)
def nc3d(m, T=300.0): return 2.0 * (2 * math.pi * m * M0 * KB * T / H ** 2) ** 1.5 / 1e6
def nc_q2d(t, m, T=300.0): return m * M0 * KB * T / (math.pi * HB ** 2) / 1e4 / (t * 1e-7)
def rough(t): return (1 - DSR / t) ** 2

# ---------------------------------------------------------------- shared start values (ASSUMED start; profiled exactly later)
QF0 = 1.38345e12              # V2 FITTED shared Qf (start only)
NS0, WT0 = 4.0e12, 0.040      # Codex start (= V1 2 nm Nt*t); W_TA V1 FITTED on 2 nm
ND0 = 2.5e17                  # FITTED V1 donor amplitude (Nd0 of the V1 law, fitted to the V0 per-film values; 01_CURRENT_STATE E), kept
                              # fixed; constant thickness dependence ASSUMED (tc -> 1e9 nm switches the (t/20)^4 law off)
ND_LABEL = 'FITTED V1 donor amplitude, kept fixed; constant thickness dependence ASSUMED'
# start (mu_inf, ell) passing exactly through the V2 anchor mu_band values 17.6897 (2.0) and 63.2597 (13.2)
f2, f13 = M_BULK / mstar(2.0), M_BULK / mstar(13.2)
r = 17.6897 / 63.2597; k = f2 / f13
ELL0 = (k - r) / (r / 2 - k / 13.2)
MUINF0 = 63.2597 * (1 + ELL0 / 13.2) / f13

def mu_band(t, mu_inf=MUINF0, ell=ELL0, massfac=True):
    return mu_inf * ((M_BULK / mstar(t)) if massfac else 1.0) / (1 + ell / t)

# ---------------------------------------------------------------- oxide / tunnelling parameter sets
GATE_WF = 4.7  # ASSUMED (TiN)
OX = {
    'nominal': {'hfo2_affinity': 2.5, 'hfo2_eg': 5.8, 'hfo2_me_tunnel': 0.20, 'al2o3_affinity': 1.25, 'al2o3_eg': 8.8,
                'al2o3_me_tunnel': 0.35, 'gate_qtunn_cmass': 1.0,
                'labels': 'chi/Eg LITERATURE (Robertson 2000, JVST B 18, 1785: HfO2 CBO 1.5 eV, Eg ~5.8-6; Al2O3 CBO 2.8 eV, Eg 8.8); '
                          'me.tunnel ASSUMED inside LITERATURE ranges (HfO2 0.1-0.4, Al2O3 0.3-0.5 m0; source to be pinned before publication); '
                          'qtunn.cmass ASSUMED'},
    'worst': {'hfo2_affinity': 3.2, 'hfo2_eg': 5.8, 'hfo2_me_tunnel': 0.10, 'al2o3_affinity': 1.6, 'al2o3_eg': 8.8,
              'al2o3_me_tunnel': 0.30, 'gate_qtunn_cmass': 1.0,
              'labels': 'ASSUMED leakage-maximising bound: TiN/HfO2 barrier 4.7-3.2 = 1.5 eV (below the LITERATURE 1.9-2.7 eV range), '
                        'lightest LITERATURE-range masses; designed so that I_G is large enough for the V_G-slope test'},
}
def fn_constants(phi, mr):
    """FN J = F.AE E^2 exp(-F.BE/E) (A/cm^2, V/cm). CALCULATED (Lenzlinger-Snow form): F.AE = 1.54e-6/(phi*mr) A/V^2,
    F.BE = 6.83e7 sqrt(mr) phi^1.5 V/cm."""
    return 1.54e-6 / (phi * mr), 6.83e7 * math.sqrt(mr) * phi ** 1.5
FN = {'nominal': (2.2, 0.20), 'worst': (1.5, 0.10)}
# 2026-10-10 review fix: ATLAS evaluates the FN field at each insulator-SEMICONDUCTOR segment (PDF p.288, manual text
# l.13034-13038), i.e. in the Al2O3 at the IWO interface. With no charge between the oxides E_Al = R_FN E_Hf, so the
# HfO2-barrier constants (A, B) are written as F.AE = A/R_FN^2, F.BE = R_FN B: J(E_Al) = A E_Hf^2 exp(-B/E_Hf).
EPS_HFO2, EPS_AL2O3 = 19.57, 9.0   # MEASURED (SI Fig. S1) / ASSUMED, as in config/geometry.yaml
R_FN = EPS_HFO2 / EPS_AL2O3
def fn_atlas(phi, mr):
    a, b = fn_constants(phi, mr); return a / R_FN ** 2, b * R_FN

TIMEOUT = {2.0: 1200, 6.3: 1500, 13.2: 2400, 31.8: 3000}

# ---------------------------------------------------------------- primary model flags
PRIMARY_FLAGS = {
    'model_file': 'config/iwo_material_model_v2.yaml (IWO_MODEL_FILE) + overrides below',
    'statistics': 'fermi', 'confinement': 'dft_fit3', 'nc_mode': 'q2d_if_E21>10kT (2.0 nm) else 3d',
    'tail': 'surface_uniform (Nt = Ns/t)', 'deep_gaussian': True, 'dit_sheet': True, 'donors': 'shared_constant',
    'mobility': 'constant per film from shared law mu_inf*(m_bulk/m*(t))/(1+ell/t) x existing roughness', 'tmun': 0,
    'contacts': 'ohmic', 'schottky_lowering': False, 'srh': 'background (tau 1e-6 s, sigma 1e-15 cm2)', 'carriers': 1,
    'trap_tunnel': False, 'poole_frenkel': False, 'gate_tunnelling': 'off', 'oxide_tat': False,
    'quantum_correction': 'off', 'strip': 'off', 'fldmob': False, 'bbt': False, 'prpmob': False,
    'mesh_factor': 1.0, 'dos': '384/192'}

def primary_params(t):
    m = mstar(t)
    nc = nc_q2d(t, m) if t <= 2.0 + 1e-9 else nc3d(m)
    mb = mu_band(t)
    return {'Qf_cm2': QF0, 'Ns_cm2': NS0, 'WT_eV': WT0, 'Nt_cm3': NS0 / (t * 1e-7), 'NTA_cm3_eV': NS0 / (t * 1e-7) / WT0,
            'Nd_cm3': ND0, 'dEc_eV': round(dEc(t), 5), 'dEg_eV': round(dEg(t), 5), 'mstar_m0': round(m, 5),
            'affinity_eV': round(CHI_BULK - dEc(t), 5), 'Nc300_cm3': float(f'{nc:.4g}'),
            'Nc300_3d_cm3': float(f'{nc3d(m):.4g}'), 'mu_inf_cm2Vs': round(MUINF0, 3), 'ell_nm': round(ELL0, 3),
            'mu_band_cm2Vs': round(mb, 4), 'MUN_cm2Vs': round(mb * rough(t), 4), 'tau_s': 1e-6, 'sigma_cm2': 1e-15,
            'gate_wf_eV': GATE_WF}

def base_overrides(t, p, q2d=True, conf_factor=1.0, conf=True, tail='surface', massfac=True, aff_off=False):
    # aff_off (2026-10-11, register H-E AFF runs): only the dEc law amplitude is set to 0 (affinity = chi_bulk); dEg, dm, NC300 and
    # mu_band stay those of the primary baseline, so the override list differs from it in that one string
    ov = []
    if conf:
        ov += [f'thickness_laws.dEc_eV.a={0.0 if aff_off else DEC[0] * conf_factor:.6g}', f'thickness_laws.dEc_eV.p={DEC[1]}',
               f'thickness_laws.dEg_QC_eV.a={DEG[0] * conf_factor:.6g}', f'thickness_laws.dEg_QC_eV.p={DEG[1]}',
               f'thickness_laws.mstar_m0.b={DM[0]}', f'thickness_laws.mstar_m0.q={DM[1]}']
    else:
        ov += ['thickness_laws.dEc_eV.a=0', 'thickness_laws.dEg_QC_eV.a=0', 'thickness_laws.mstar_m0.b=0']
    if tail == 'surface':
        ov += [f'thickness_laws.Nt_cm3.Nt2={p["Ns_cm2"] / 2e-7:.6g}', 'thickness_laws.Nt_cm3.alpha=1']
    elif tail == 'bulk':
        ov += [f'thickness_laws.Nt_cm3.Nt2={p["Ns_cm2"] / 2e-7:.6g}', 'thickness_laws.Nt_cm3.alpha=0']
    elif tail == 'mixed50':
        # half of the 2 nm integrated tail as a surface term (Ns/2 spread as Ns/(2t)), half as a constant bulk density
        ov += [f'thickness_laws.Nt_cm3.Nt2={p["Ns_cm2"] / 2 / 2e-7:.6g}', 'thickness_laws.Nt_cm3.alpha=1',
               f'solver.physics_options.nt_bulk_cm3={p["Ns_cm2"] / 2 / 2e-7:.6g}']
    elif tail == 'none':
        ov += ['thickness_laws.Nt_cm3.Nt2=0', 'thickness_laws.Nt_cm3.alpha=0']
    ov += [f'thickness_laws.WTA_eV.value={p["WT_eV"]}', f'thickness_laws.Nd_eff_cm3.Nd0={p["Nd_cm3"]:.6g}',
           'thickness_laws.Nd_eff_cm3.tc_nm=1e9', f'traps.fixed_interface_charge_Qf_cm2.value={p["Qf_cm2"]:.6g}',
           f'thickness_laws.mu0_cm2Vs.mu_band_fitted[{t}]={p["mu_band_cm2Vs"]:.6g}',
           'solver.dos_levels.numa=384', 'solver.dos_levels.numd=192', 'solver.tmun=0']
    if q2d and conf and t <= 2.0 + 1e-9:
        ov.append(f'solver.physics_options.nc300_override_cm3[{t}]={p["Nc300_cm3"]:.6g}')
    if aff_off: ov.append('solver.physics_options.intervention=affinity_only')   # 2026-10-11 review: provenance header only (comment lines)
    return ov

RUNS = []
def add(id_, stage, t, flags, params, purpose, overrides, requires_code=(), mode='transfer', timeout_mult=1.0,
        params_rule=None, status='planned_fixed', expected=None, depends_on=None):
    lab = f'c10_{id_.lower().replace("-", "_")}_{KEY.get(t, str(t))}'
    to = int(round(TIMEOUT[t] * timeout_mult / 100.0) * 100) if mode != 'strip' else 900
    entry = {'id': id_, 'stage': stage, 'film_nm': t, 'model_flags': flags, 'params': params, 'purpose': purpose,
             'status': status, 'requires_code': list(requires_code), 'timeout_s': to,
             'campaign_entry': {'id': id_, 'thickness': t, 'label': lab, 'overrides': overrides, 'timeout': to,
                                'purpose': purpose, **({'mode': mode} if mode != 'transfer' else {})}}
    if params_rule: entry['params_rule'] = params_rule
    if expected: entry['pre_registered_expectation'] = expected
    if depends_on: entry['depends_on'] = depends_on
    RUNS.append(entry)

def F(**kw):
    d = dict(PRIMARY_FLAGS); d.update(kw); return d

def P(t, **kw):
    d = primary_params(t); d.update(kw); return d

# ================================================================ S0 smoke (2)
p = P(2.0)
add('S0-01', 'S0_smoke', 2.0, F(), p, 'Smoke 1 / primary shared baseline at 2.0 nm: new DFT laws (fit3 dEc/dEg/dm), quasi-2D NC300, '
    'surface tail Nt=Ns/t, constant Nd, shared Qf, mu from the shared law, tmun=0. Checks the new option code path '
    '(nc300_override) and that every override reaches the deck.', base_overrides(2.0, p), ['C1', 'C2', 'C11'])
p = P(2.0, oxide=OX['worst'])
add('S0-02', 'S0_smoke', 2.0, F(gate_tunnelling='qtnlsc_worst'), p,
    'Smoke 2 / gate-leakage code path and first quantitative leakage result: S0-01 + self-consistent direct/FN-regime '
    'tunnelling QTNLSC.EL (qtnl.derivs) through Al2O3/HfO2 with the leakage-maximising oxide set, j.tun logged, oxide '
    'mesh 0.25 nm. Must show non-zero I_G and KCL pass; compares I_D(off) and I_G with the 2 nm floor (the smallest).',
    base_overrides(2.0, p) + ['solver.physics_options.gate_tunnelling.enabled=1', 'solver.physics_options.gate_tunnelling.model=qtnlsc',
                              'solver.physics_options.gate_tunnelling.set=worst'], ['C1', 'C2', 'C4', 'C11'], timeout_mult=1.5,
    expected='I_G at V_G=-3 V of order 1e-15..1e-11 A/um (Codex optimistic FN estimate 3.8e-12 A/um at 3 V), falling by '
             '>=3 decades between -3 and -1 V; I_D(off) slope |dlog10 I_D/dV_G| >= 1 dec/V where I_G dominates. '
             'Either outcome is reported. The worst set is an optimistic scenario (not a rigorous upper bound: no pinholes, thinning '
             'or defects), so floor-scale leakage here is an allowed result, checked by S2-11 (oxide mesh) before it is interpreted.')

# ================================================================ S1 baselines and numerics (6)
for i, t in enumerate((6.3, 13.2), 1):
    p = P(t)
    add(f'S1-0{i}', 'S1_baseline_numerics', t, F(), p, f'Primary shared baseline at {t} nm (same shared parameters as S0-01; '
        'nothing tuned to this film).', base_overrides(t, p), ['C1', 'C11'],
        expected=('6.3 nm: on-current several times too high (law mu 6.3 nm ~4x the V1 per-film value) and V_th,cc '
                  '0.2-0.4 V low, the known V1/V2 failure pattern' if t == 6.3 else None))
p = P(13.2)
add('S1-03', 'S1_baseline_numerics', 13.2, F(mesh_factor=0.7), p, 'Numerics: 13.2 nm baseline with all mesh spacings x0.7 '
    '(x0.5 exceeds 32-bit memory).', base_overrides(13.2, p) + ['geometry.mesh.spacing_factor=0.7'], ['C11'], timeout_mult=1.4,
    expected='|d active RMSE| <= 0.01 dec, |dV_th| <= 5 mV, |dSS| <= 3 mV/dec (runs 0028/0036 showed 0.0004 dec for V1 physics)')
p = P(2.0)
add('S1-04', 'S1_baseline_numerics', 2.0, F(dos='768/384'), p, 'Numerics: 2.0 nm baseline with DOS quadrature doubled '
    '(768/384) - finds the practical memory limit if it fails.', [o for o in base_overrides(2.0, p) if 'dos_levels' not in o]
    + ['solver.dos_levels.numa=768', 'solver.dos_levels.numd=384'], ['C11'], timeout_mult=2.0,
    expected='I_on change <= 1 % (96->384 changed it by 2.5 %)')
p = P(2.0); p['Nc300_cm3'] = p['Nc300_3d_cm3']
add('S1-05', 'S1_baseline_numerics', 2.0, F(nc_mode='3d'), p, 'DFT input check: 2.0 nm with the V2 3-D NC300 instead of the '
    'DFT quasi-2D value (x4.27). Quantifies the quasi-2D choice inside ATLAS.', base_overrides(2.0, p, q2d=False), ['C11'],
    expected='V_th,cc higher by +40..+70 mV than S0-01 (DFT_TO_TCAD.md estimate 37.5 meV ~ 55 mV); SS change <= 3 mV/dec. '
             'A different sign or a shift > 100 mV means the NC override is not doing what is intended.')
p = P(13.2)
add('S1-06', 'S1_baseline_numerics', 13.2, F(carriers=2), p, 'Electron-only assumption: 13.2 nm baseline solved with two '
    'carriers (holes transported, background SRH generation active).', base_overrides(13.2, p) + ['solver.carriers=carriers=2'],
    ['C11'], timeout_mult=1.5, expected='I_D change < 1e-3 relative everywhere above 1e-14 A/um; hole current < 1e-25 A/um')
DQF, MUFAC = 1.0e12, 0.6
p = P(2.0); p['Qf_cm2'] = QF0 + DQF; p['mu_band_cm2Vs'] = round(p['mu_band_cm2Vs'] * MUFAC, 4); p['MUN_cm2Vs'] = round(p['MUN_cm2Vs'] * MUFAC, 4)
add('S1-07', 'S1_baseline_numerics', 2.0, F(), p, 'Native check of the offline profiling (Codex review 2026-10-10): S0-01 with Qf '
    f'+{DQF:.1e} cm-2 (dV = -q dQf/Cox = {-1.602176634e-19 * DQF / 8.955369814e-7:+.4f} V) and MUN x{MUFAC}. The shifted+scaled S0-01 '
    'curve must reproduce this run before profiling is used in S3/S4.', base_overrides(2.0, p), ['C1', 'C2', 'C11'],
    expected='|log10 I_native - log10 I_transformed| <= 0.01 dec on every point of the J windows (continuum argument: exact '
             'except for SRH R and numerics); worse -> profiling is approximate, every S4 optimum is confirmed natively')

# ================================================================ S2 off-floor mechanisms (15)
for i, (t, kind) in enumerate([(13.2, 'extreme'), (13.2, 'suppressed'), (2.0, 'extreme')], 1):
    if kind == 'extreme':
        p = P(t, tau_s=1e-9, sigma_cm2=1e-13, mass_tunnel_m0=round(mstar(t), 4))
        ov = base_overrides(t, p) + ['solver.carriers=carriers=2', 'bulk_reference.srh_tau_s.value=1e-9',
                                     'traps.bulk_acceptor_tail.capture_cm2=1e-13',
                                     f'solver.models=fermi srh temp=300 print trap.tunnel trap.hurkx mass.tunnel={mstar(t):.4f}']
        purp = (f'SRH/TAT null test at {t} nm: two carriers, background lifetime 1e-9 s and capture cross-sections x100 '
                '(1e-13 cm2) - both beyond the reasonable range - plus field-enhanced trap capture (TRAP.TUNNEL, TRAP.HURKX, '
                'MASS.TUNNEL = DFT m*(t)). Upper bound on generation current inside the solver.')
        exp_ = ('I_D(off) - I_D(off, S1-06 or S0-01) <= 1e-20 A/um (COMPUTED bound <= 8e-29 A/um x 1e3 enhancement); '
                'floor ratio <= 1e-5. A floor-scale current would contradict the bound -> numerics audit, not a fit.')
        flags = F(carriers=2, srh='extreme (tau 1e-9 s, sigma 1e-13 cm2)', trap_tunnel=True)
    else:
        p = P(t, sigma_cm2=1e-20)
        ov = base_overrides(t, p) + ['solver.carriers=carriers=2', 'traps.bulk_acceptor_tail.capture_cm2=1e-20',
                                     'solver.models=fermi temp=300 print']
        purp = ('SRH-off reference at 13.2 nm (two carriers): SRH flag removed and all DEFECTS capture cross-sections x1e-5 '
                '(occupancy is unchanged because it depends on the ratio of capture rates). Isolates the recombination term.')
        exp_ = 'I_D identical to S1-06 within 1e-3 relative above 1e-14 A/um'
        flags = F(carriers=2, srh='suppressed')
    add(f'S2-0{i}', 'S2_offfloor_mechanisms', t, flags, p, purp, ov, ['C11'], timeout_mult=1.5, expected=exp_)

j = 4
def leak_entry(t, kind, model):
    global j
    st = OX[kind]
    p = P(t, oxide=st)
    ov = base_overrides(t, p) + ['solver.physics_options.gate_tunnelling.enabled=1', f'solver.physics_options.gate_tunnelling.model={model}',
                                 f'solver.physics_options.gate_tunnelling.set={kind}']
    if model == 'fnord':
        a0, b0 = fn_constants(*FN[kind]); ae, be = fn_atlas(*FN[kind])
        p['fn'] = {'phi_eV': FN[kind][0], 'm_r': FN[kind][1], 'A_HfO2_barrier_A_per_V2': float(f'{a0:.4g}'), 'B_HfO2_barrier_V_per_cm': float(f'{b0:.4g}'),
                   'field_ratio_E_Al2O3_over_E_HfO2': round(R_FN, 5), 'F.AE_A_per_V2': float(f'{ae:.4g}'), 'F.BE_V_per_cm': float(f'{be:.4g}'),
                   'label': 'CALCULATED from the ASSUMED/LITERATURE phi, m_r; HfO2-barrier constants transferred to the Al2O3/IWO-segment field '
                            'where ATLAS evaluates FN (F.AE = A/r^2, F.BE = r B, r = eps_HfO2/eps_Al2O3; 2026-10-10 review fix)'}
        ov += [f'solver.physics_options.gate_tunnelling.f_ae={ae:.4g}', f'solver.physics_options.gate_tunnelling.f_be={be:.4g}']
    exp_ = {('nominal', 'qtnlsc'): 'I_G(-3 V) <= 1e-24 A/um (COMPUTED FN bound 2e-28 A/um for phi 2.2 eV, m 0.2); floor ratio <= 1e-9 at every film',
            ('worst', 'qtnlsc'): 'I_G(-3 V) 1e-15..1e-11 A/um; I_G(-0.5 V)/I_G(-3 V) <= 1e-3 (not flat)',
            ('worst', 'fnord'): 'I_G(-3 V) ~ 1e-12 A/um (Codex: 3.8e-12 A/um at 3 V for phi 1.5, m 0.1); >= 5 decades drop to -0.5 V'}[(kind, model)]
    add(f'S2-{j:02d}', 'S2_offfloor_mechanisms', t, F(gate_tunnelling=f'{model}_{kind}'), p,
        f'Gate leakage, quantitative: {t} nm, {model.upper()} ({"self-consistent direct/FN-regime tunnelling" if model == "qtnlsc" else "self-consistent Fowler-Nordheim, single-barrier F.AE/F.BE from the HfO2 barrier, transferred to the Al2O3/IWO-segment field where ATLAS evaluates FN"}), '
        f'{kind} oxide parameters. Compares I_G and the drain-collected share with the measured floor, and tests flatness in V_G.',
        ov, ['C1', 'C4', 'C11'], timeout_mult=1.5, expected=exp_)
    j += 1
for t in FILMS: leak_entry(t, 'nominal', 'qtnlsc')          # S2-04..06
for t in (6.3, 13.2): leak_entry(t, 'worst', 'qtnlsc')      # S2-07..08
for t in (2.0, 13.2): leak_entry(t, 'worst', 'fnord')       # S2-09..10
# 2026-10-11 (frozen register H-C): S2-11 REDEFINED as device oxide y-mesh x0.5 under automatic slicing. The old QT-mesh halving
# (qt_point_nm=0.25, qt_slice_um=0.1) acted only with qt_mesh=1 and was inert in the automatic-slicing S0-02 form (run_0067).
p = P(2.0, oxide=OX['worst'], oxide_mesh_factor=0.5)
add('S2-11', 'S2_offfloor_mechanisms', 2.0, F(gate_tunnelling='qtnlsc_worst', mesh_factor='oxide y-mesh x0.5 (automatic slicing)'), p,
    'Numerics of the leakage result (register H-C, S2-11 redefined; first S2 launch): S0-02 (run_0067 form: QTNLSC worst set, automatic '
    'slicing, S/D exclude_near) with the device oxide y-mesh spacing halved at the oxide lines (Al2O3 line 0.25 -> 0.125 nm, HfO2 line '
    '1.0 -> 0.5 nm); the y = 0 IWO/Al2O3 line (0.0625 nm, shared with the IWO interface mesh) is unchanged. Actual refinement '
    '(run_0067 equilibrium.str + geometric grading): Al2O3 15 -> about 22 intervals (largest 0.25 -> 0.125 nm, smallest 0.06 nm unchanged), '
    'HfO2 28 -> about 55, i.e. Al2O3 about x1.5 and HfO2 about x2. Timeout x4.5: run_0067 took 1246 s on 9594 nodes and 43 oxide '
    'intervals per slice; this deck has about 13.7k nodes and about 77 (run_0062, 13,689 nodes and 75, ran out of memory at the old 2 GB limit).',
    base_overrides(2.0, p) + ['solver.physics_options.gate_tunnelling.enabled=1', 'solver.physics_options.gate_tunnelling.model=qtnlsc',
                              'solver.physics_options.gate_tunnelling.set=worst', 'solver.physics_options.gate_tunnelling.oxide_mesh_factor=0.5'],
    ['C1', 'C4', 'C11'], timeout_mult=4.5,
    expected='resolved log10 |I_G| changes by <= 0.1 dec at every V_G vs S0-02 (run_0067); points below the demonstrated resolution are '
             'censored, never a pass (register section 0 and H-C; score_register.py hc_mesh)')
for i, t in enumerate((2.0, 13.2)):
    p = P(t, oxide=OX['nominal'], oxide_tat={'region': 'HfO2', 'conc_cm3': 1e19, 'e_level_below_Ec_ox_eV': 1.0, 'tat_poisson': False,
                                             'label': 'ASSUMED high-defect bound; trap charge kept out of Poisson (^tat.poisson) so that the run isolates the TAT current'})
    add(f'S2-{12 + i}', 'S2_offfloor_mechanisms', t, F(gate_tunnelling='qtnlsc_nominal', oxide_tat=True), p,
        f'Defect-assisted gate leakage (Ielmini TAT, ITAT.SC.EL with DOPING TAT.TRAP in HfO2) at {t} nm: ASSUMED 1e19 cm-3 traps '
        '1.0 eV below the HfO2 band edge, nominal oxide set, trap charge OUT of Poisson (MODELS ^tat.poisson, PDF p.323): at full '
        'occupancy the traps would carry 1.5e13 cm-2, far above the fitted Q_f, and the change in I_D would mix an electrostatic '
        'shift with collected leakage (2026-10-10 review fix). Matched gate control: S2-04 (2.0 nm) / S2-06 (13.2 nm). Tests the '
        'leakage path Codex could not exclude without I_G (Poole-Frenkel-like magnitudes). Syntax VERIFIED (PDF p.320-327, '
        'quantumex20), bilayer use UNVERIFIED. The charged-oxide electrostatics are NOT tested by this run.',
        base_overrides(t, p) + ['solver.physics_options.gate_tunnelling.enabled=1', 'solver.physics_options.gate_tunnelling.model=qtnlsc',
                                'solver.physics_options.gate_tunnelling.set=nominal', 'solver.physics_options.oxide_tat.enabled=1',
                                'solver.physics_options.oxide_tat.conc_cm3=1e19', 'solver.physics_options.oxide_tat.e_level_eV=1.0',
                                'solver.physics_options.oxide_tat.poisson=0'],
        ['C1', 'C4', 'C9', 'C11'], timeout_mult=2.0,
        expected='I_G strongly V_G-dependent (Codex PF estimate J(3.7 V)/J(1.2 V) ~ 6e3); flat-floor criterion not met')
for i, t in enumerate((13.2, 2.0)):
    p = P(t, strip={'L_p_um': 20.0, 'vd_V': [0.1, 0.7], 'label': 'geometry ASSUMED; (W/L)_par FITTED after the solve'})
    add(f'S2-{14 + i}', 'S2_offfloor_mechanisms', t, F(strip='separate_deck'), p,
        f'Ungated-strip deck (audit 7.11 A) at {t} nm with the baseline shared parameters: same film/DOS/Nd/Qf on Al2O3/HfO2 '
        'without a gate electrode, V_D stepped 0->0.1->0.7 V. Gives G_strip(t) and I(0.7)/I(0.1). Early run: code check and magnitude; '
        'frozen repeats in S6.', base_overrides(t, p) + ['solver.physics_options.strip.L_p_um=20'], ['C1', 'C8', 'C11'], mode='strip',
        expected='I(0.7 V)/I(0.1 V) = 7.0 +- 0.5 (ohmic film); diffusion form would give 1.02')
for i, t in enumerate((13.2, 2.0)):
    p = P(t, Qf_cm2=0.0, strip={'L_p_um': 20.0, 'vd_V': [0.1, 0.7], 'label': 'geometry ASSUMED; Qf = 0 control (V2 variant D had no Qf)'})
    add(f'S2-{16 + i}', 'S2_offfloor_mechanisms', t, F(strip='separate_deck, Qf=0'), p,
        f'Ungated-strip control at {t} nm with the front Qf removed (Codex review: V2 variant D excluded Qf, variant Q included it and '
        'scaled very differently). Whether the region outside the gate carries the interface charge is unknown, so both are run.',
        base_overrides(t, p) + ['solver.physics_options.strip.L_p_um=20'], ['C1', 'C8', 'C11'], mode='strip',
        expected='G_strip(13.2)/G_strip(2.0) differs from the Qf-on pair; which one approaches the measured floor ratio 1432 is the result')
# 2026-10-11 (frozen register H-B, STRIP-6p3; Codex H02): third Qf-on strip film, same construction as S2-14/S2-15
p = P(6.3, strip={'L_p_um': 20.0, 'vd_V': [0.1, 0.7], 'label': 'geometry ASSUMED; (W/L)_par FITTED after the solve'})
add('STRIP-6p3', 'S2_offfloor_mechanisms', 6.3, F(strip='separate_deck'), p,
    'Ungated-strip deck at 6.3 nm (register H-B STRIP-6p3), built exactly as S2-14/S2-15: baseline shared parameters, Qf on (frozen H-B '
    'branch), no gate electrode, V_D stepped 0->0.1->0.7 V (REG-001). With (W/L)_par fitted on 13.2 nm (S2-14) it gives the 6.3 nm floor prediction.',
    base_overrides(6.3, p) + ['solver.physics_options.strip.L_p_um=20'], ['C1', 'C8', 'C11'], mode='strip',
    expected='I(0.7 V)/I(0.1 V) = 7.0 +- 0.5; with (W/L)_par fitted on S2-14 (13.2 nm) the predicted 6.3 and 2.0 nm floors lie within 0.5 dec '
             'of the measured ones (register H-B; score_register.py hb_ratio / hb_transfer)')

# ================================================================ S2 resolution refinements (register amendment A41, 2026-10-13; launch only after A41 is logged)
# Codex round 3 (CODEX_WORK_CHAT, reply under the 2026-10-12T15:50Z heading), adaptive amendment: ONE S0-02 DOS x2 run, whose I_G comparison
# with run_0067 may qualify the S2-11 hc_mesh verdict. Definition: the S0-02 (run_0067) override list with ONLY the two DOS level counts doubled
# in place, 384/192 -> 768/384 (the S1-04 DOS x2 keys and factor; S1-04 appended them after its base list, here they keep their S0-02 positions;
# the deck and score_register.intervention are order-insensitive). NTD = NGD = 0, so the effective change is the acceptor energy quadrature
# only (NUMD doubling is inert). Own stage and held stage plan, so that the existing stage plans are unchanged; it runs from
# config/campaign_C10_DIAGb.json only. Timeout x3.0 = S0-02's x1.5 doubled, as S1-04 doubled S0-01's x1.0 (S1-04 took 476.8 s vs S0-01
# 395.8 s; run_0067 took 1246 s).
S002_OV = next(r for r in RUNS if r['id'] == 'S0-02')['campaign_entry']['overrides']
DOS2 = {'solver.dos_levels.numa=384': 'solver.dos_levels.numa=768', 'solver.dos_levels.numd=192': 'solver.dos_levels.numd=384'}
assert sum(o in DOS2 for o in S002_OV) == 2, 'S0-02 must carry exactly the two DOS overrides 384/192'
p = P(2.0, oxide=OX['worst'])
add('S0-02-DOS2', 'S2_resolution_refinements', 2.0, F(gate_tunnelling='qtnlsc_worst', dos='768/384'), p,
    'Resolution refinement for S2-11 (register A41): S0-02 exactly as launched in run_0067 (QTNLSC worst set, automatic slicing, S/D exclude_near, '
    'oxide mesh unchanged) with the DOS quadrature doubled (numa/numd 384/192 -> 768/384, the S1-04 DOS x2 knob); nothing else changes. Its I_G '
    'comparison with run_0067 (score_register.py resolution_pair <this run> <run_0067> ig_raw_A) is the candidate I_G ceiling for hc_mesh '
    '<S2-11 rerun> <run_0067>; the shared run_0067 baseline is recorded as NOT independent. Numerical stability under the DOS intervention only, '
    'not an absolute error bound (ASSUMED operational method).',
    [DOS2.get(o, o) for o in S002_OV], ['C1', 'C2', 'C4', 'C11'], timeout_mult=3.0,
    expected='no physics prediction (a numerical refinement): the pair qualifies only under the frozen support rule (>= 3 agreeing points above the '
             'candidate, one within 1 decade of it, full bias coverage, deck ratio tolerance 1e-3); a non-qualifying pair leaves S2-11 PROVISIONAL '
             '(register section 0 censoring; A41)')

# ================================================================ S3 model-form branches (26), fixed start parameters
k3 = 1
def s3(t, flags, p, purpose, ov, code=('C11',), mult=1.0, expected=None):
    global k3
    add(f'S3-{k3:02d}', 'S3_model_branches', t, flags, p, purpose, ov, code, timeout_mult=mult, expected=expected); k3 += 1
for t in FILMS:
    p = P(t, dEc_eV=0.0, dEg_eV=0.0, mstar_m0=M_BULK, affinity_eV=CHI_BULK, Nc300_cm3=float(f'{nc3d(M_BULK):.4g}'),
          mu_band_cm2Vs=round(mu_band(t, massfac=False), 4))
    s3(t, F(confinement='off', nc_mode='3d'), p, f'No confinement at {t} nm: dEc = dEg = dm = 0, 3-D NC300 with the bulk mass, '
       'mobility law without the DFT mass factor. Tests whether the DFT inputs change anything the data can see.',
       base_overrides(t, p, conf=False, q2d=False) + ['solver.physics_options.intervention=confinement_off'])   # 2026-10-11 review: provenance header only
for t in FILMS:
    p = P(t, Nt_cm3=NS0 / 2e-7)
    s3(t, F(tail='bulk (Nt constant = Ns/2 nm)'), p, f'Bulk-only tail at {t} nm: Nt constant (2e19 cm-3, alpha 0) instead of '
       'the surface tail Ns/t. Same density at 2 nm, 3.15x / 6.6x more at 6.3 / 13.2 nm.', base_overrides(t, p, tail='bulk'))
for t in FILMS:
    p = P(t, Nt_cm3=NS0 / 2 / (t * 1e-7) + NS0 / 2 / 2e-7)
    s3(t, F(tail='mixed 50:50 surface/bulk at 2 nm'), p, f'Mixed tail at {t} nm: Nt = (Ns/2)/t + Nb, Nb = (Ns/2)/2 nm '
       '(V1 "untested alternative" Nt*t = Ns + Nb*t).', base_overrides(t, p, tail='mixed50'), ('C1', 'C3', 'C11'))
p = P(6.3, Nt_cm3=0.0)
s3(6.3, F(tail='none'), p, 'No tail at 6.3 nm (Codex run 9): does trap filling create the late/steep 6.3 nm turn-on? Shape '
   'compared after profiling shift and scale.', base_overrides(6.3, p, tail='none'))
for g0 in (-0.31, 0.30):
    for t in FILMS:
        p = P(t, igzo={'gamma0': g0, 'tgamma_K': 178.4, 'ncrit_cm3': 1e20, 'mun': round(mu_band(t) * rough(t), 4), 'tmun': 0,
                       'labels': 'GAMMA0 FITTED later (here a 2-point screen: -0.31 LITERATURE default for IGZO, Abe 2014 via '
                                 'ATLAS; +0.30 ASSUMED); TGAMMA LITERATURE default (no T data); NCRIT ASSUMED, degenerate with MUN'})
        s3(t, F(mobility=f'igzo_tokyo (gamma0 {g0})'), p, f'IGZO.TOKYO carrier-density mobility at {t} nm, GAMMA0 = {g0} '
           f'(gamma = 178.4/300 + GAMMA0 = {178.4 / 300 + g0:.3f}). First 6.3 nm launch also verifies activation for user.material=IWO '
           '(REGIONAL MOBILITY MODEL SUMMARY).',
           base_overrides(t, p) + ['solver.physics_options.mobility.model=igzo_tokyo', f'solver.physics_options.mobility.gamma0={g0}',
                                   'solver.physics_options.mobility.tgamma=178.4', 'solver.physics_options.mobility.ncrit=1e20'],
           ('C1', 'C6', 'C11'), 1.3)
for phib in (0.2, 0.5):
    for t in FILMS:
        p = P(t, schottky={'phiB_eV': phib, 'workfun_eV': round(CHI_BULK - dEc(t) + phib, 4), 'arichn': round(120.17 * mstar(t), 2),
                           'me_tunnel': round(mstar(t), 4), 'lowering': 'image force (BARRIER, no free coefficient)',
                           'labels': 'phiB ASSUMED grid (shared, not per film); ARICHN CALCULATED 120.17*m*(t); me.tunnel = DFT m*(t)'})
        s3(t, F(contacts=f'schottky {phib} eV', schottky_lowering=True), p, f'Schottky Pd S/D at {t} nm, shared barrier {phib} eV, '
           'thermionic + E.TUNNEL + image-force lowering, ^ins.ohmic, top mesh 0.1 nm under the contacts.',
           base_overrides(t, p) + ['solver.physics_options.schottky_sd.enabled=1', f'solver.physics_options.schottky_sd.barrier_eV={phib}',
                                   'solver.physics_options.schottky_sd.lowering=1', 'solver.physics_options.schottky_sd.e_tunnel=1'],
           ('C1', 'C5', 'C11'), 1.5)
p = P(6.3, Qf_cm2=QF0 + DQF, igzo={'gamma0': -0.31, 'tgamma_K': 178.4, 'ncrit_cm3': 1e20, 'mun': round(mu_band(6.3) * rough(6.3) * MUFAC, 4), 'tmun': 0})
p['mu_band_cm2Vs'] = round(mu_band(6.3) * MUFAC, 4)
add('S3-27', 'S3_model_branches', 6.3, F(mobility='igzo_tokyo (gamma0 -0.31)'), p, 'Native check of the offline profiling for the '
    f'IGZO.TOKYO branch: S3-12 with Qf +{DQF:.1e} cm-2 and MUN x{MUFAC}. Needed before IGZO can use exact profiling in S4.',
    base_overrides(6.3, p) + ['solver.physics_options.mobility.model=igzo_tokyo', 'solver.physics_options.mobility.gamma0=-0.31',
                              'solver.physics_options.mobility.tgamma=178.4', 'solver.physics_options.mobility.ncrit=1e20'],
    ['C1', 'C6', 'C11'], timeout_mult=1.3, expected='as S1-07: <= 0.01 dec against the transformed S3-12 curve')
p = P(6.3, schottky={'phiB_eV': 0.5, 'lowering': False})
s3(6.3, F(contacts='schottky 0.5 eV', schottky_lowering=False), p, 'Schottky 0.5 eV at 6.3 nm WITHOUT lowering: on/off '
   'diagnostic of the lowering term.', base_overrides(6.3, p) + ['solver.physics_options.schottky_sd.enabled=1',
   'solver.physics_options.schottky_sd.barrier_eV=0.5', 'solver.physics_options.schottky_sd.lowering=0', 'solver.physics_options.schottky_sd.e_tunnel=1'],
   ('C1', 'C5', 'C11'), 1.5)
for mz, why in ((0.139, 'm_z = 0.139 m0 (MODEL: box fitted to the DFT 1/2 nm subband spacings)'), (round(mstar(2.0), 4), 'quantum mass = in-plane DFT m*(2 nm) (bound)')):
    p = P(2.0, dEc_eV=0.0, dEg_eV=0.0, mstar_m0=M_BULK, affinity_eV=CHI_BULK, Nc300_cm3=float(f'{nc3d(M_BULK):.4g}'),
          mu_band_cm2Vs=round(mu_band(2.0, massfac=False), 4),
          bqp={'ngamma': 1.2, 'nalpha': 0.5, 'qdir': 2, 'quantum_mass_m0': mz, 'labels': 'BQP gamma/alpha ASSUMED (ATLAS defaults, not fitted); ' + why})
    s3(2.0, F(confinement='off (replaced by BQP)', nc_mode='3d', quantum_correction='bqp'), p,
       f'Paired confinement test at 2.0 nm: DFT shifts OFF, Bohm quantum potential ON, {why}. Compare with S0-01 (DFT ON, BQP OFF); '
       'never both ON (double counting).',
       base_overrides(2.0, p, conf=False, q2d=False) + ['solver.physics_options.quantum.model=bqp', f'solver.physics_options.quantum.mass={mz}'],
       ('C1', 'C7', 'C11'), 1.5)
p = P(2.0)
s3(2.0, F(statistics='boltzmann'), p, 'Boltzmann statistics at 2.0 nm (degenerate accumulation check; FERMI kept unless this changes nothing).',
   base_overrides(2.0, p) + ['solver.models=srh temp=300 print'])
# 2026-10-11 (frozen register H-E, A6/A13/A16): affinity-only interventions. S3-01..03 switch ALL confinement inputs off (affinity, E_g,
# mass, NC override, mobility mass factor); these switch off ONLY the confinement affinity shift of the S0-01 / S1-01 baselines.
AFF_BASE = {2.0: ('S0-01', '-281.6'), 6.3: ('S1-01', '-62.2')}   # registered shifts (mV), H-E
for t, (bid, dv) in AFF_BASE.items():
    p = P(t, dEc_eV=0.0, affinity_eV=CHI_BULK)
    add(f'AFF-{KEY[t]}', 'S3_model_branches', t, F(confinement='dft_fit3 with the affinity shift off (dEc = 0)'), p,
        f'Affinity-only intervention at {t} nm (register H-E): {bid} with the confinement affinity shift switched off (dEc law amplitude 0, '
        'affinity = chi_bulk); E_g, m*, the NC300 choice and the mobility law are unchanged, so the deck differs from the baseline only in '
        'AFFINITY. Model-consistency check, not a physics test.', base_overrides(t, p, aff_off=True), ['C11'],
        expected=f'dV_th,cc = {dv} +- 5 mV vs {bid}, rigid within +-5 mV at every frozen AFF current level (A16; score_register.py aff)')

# ================================================================ S4 global shared calibration (69)
lhs2 = qmc.LatinHypercube(d=2, seed=20261010).random(14)
lhs3 = qmc.LatinHypercube(d=3, seed=20261011).random(14)
cands = [(NS0, WT0, -0.31)] + [(10 ** (12 + a[0]), 0.025 + 0.035 * a[1], -0.6 + 1.2 * b[2]) for a, b in zip(lhs2, lhs3)]
cands3 = [(NS0, WT0, -0.31)] + [(10 ** (12 + b[0]), 0.025 + 0.035 * b[1], -0.6 + 1.2 * b[2]) for b in lhs3]
for ci, ((ns, wt, _), (ns3, wt3, g3)) in enumerate(zip(cands, cands3), 1):
    for t in FILMS:
        p = P(t, Ns_cm2=float(f'{ns:.4g}'), WT_eV=round(wt, 4), Nt_cm3=float(f'{ns / (t * 1e-7):.4g}'), NTA_cm3_eV=float(f'{ns / (t * 1e-7) / wt:.4g}'))
        p['if_igzo_branch_adopted'] = {'Ns_cm2': float(f'{ns3:.4g}'), 'WT_eV': round(wt3, 4), 'gamma0': round(g3, 3)}
        add(f'S4A-{ci:02d}-{KEY[t]}', 'S4a_calibration_spacefilling', t, F(mobility='{sel:mobility_branch}', tail='{sel:tail_branch}',
            contacts='{sel:contact_branch}'), p,
            f'Global shared calibration, space-filling candidate {ci}/15 (pre-registered Latin hypercube, seed 20261010/20261011), {t} nm. '
            'Launch dimensions (Ns, WT[, GAMMA0]); Qf (= dV0), mu_inf and ell are profiled EXACTLY offline (rigid shift and '
            'current scaling) on all three films jointly.', base_overrides(t, p), ['C1', 'C11', 'C13', '+ code of the adopted S3 branch (C3/C5/C6)'],
            timeout_mult=1.3, params_rule='branch flags from S3 decision rules; if mobility branch = igzo_tokyo use if_igzo_branch_adopted',
            depends_on=['S3'])
for ci in range(1, 7):
    for t in FILMS:
        add(f'S4B-{ci:02d}-{KEY[t]}', 'S4b_calibration_adaptive', t, F(mobility='{sel:mobility_branch}', tail='{sel:tail_branch}',
            contacts='{sel:contact_branch}'), {'Ns_cm2': '{fit:Ns}', 'WT_eV': '{fit:WT}', 'gamma0': '{fit:gamma0}', 'Qf_cm2': '{fit:Qf}',
            'mu_band_cm2Vs': '{fit:mu_band_' + KEY[t] + '}'},
            f'Adaptive refinement {ci}/6 at {t} nm: next candidate from a quadratic surrogate of the equal-film objective over the '
            'S4a archive (trust region = half the S4a spacing around the best). Stop early if 3 successive candidates improve by < 0.01 dec.',
            ['{generated from the fitted values}'], ['C1', 'C11', 'C13'], timeout_mult=1.3, status='planned_adaptive',
            params_rule='surrogate minimum of J over (Ns, WT[, GAMMA0]); Qf, mu_inf, ell re-profiled exactly', depends_on=['S4a'])
for t in FILMS:
    add(f'S4C-{KEY[t]}', 'S4c_native_confirmation', t, F(mobility='{sel:mobility_branch}', tail='{sel:tail_branch}', contacts='{sel:contact_branch}'),
        {'all': '{fit:best}'}, f'Native confirmation of the best shared model at {t} nm with the profiled Qf and mu_band written into the '
        'deck (checks that the exact-transformation profiling reproduces ATLAS within 0.005 dec).', ['{generated}'], ['C1', 'C11'],
        timeout_mult=1.3, status='planned_adaptive', depends_on=['S4b'])
for t in FILMS:
    add(f'S4D-{KEY[t]}', 'S4d_runner_up_branch', t, F(mobility='{sel:runner_up}', contacts='{sel:runner_up}'), {'all': '{fit:best, runner-up branch}'},
        f'Runner-up S3 branch re-run at the calibrated shared parameters ({t} nm): checks that the branch choice made at the '
        'start values survives calibration.', ['{generated}'], ['C1', 'C11'], timeout_mult=1.3, status='planned_adaptive', depends_on=['S4c'])

# ================================================================ S5 leave-one-film-out (30)
for held in FILMS:
    train = [t for t in FILMS if t != held]
    for ci in range(1, 5):
        for t in train:
            add(f'S5-H{KEY[held]}-{ci}-{KEY[t]}', 'S5_leave_one_film_out', t, F(mobility='{sel:mobility_branch}', contacts='{sel:contact_branch}'),
                {'all': '{fold:' + KEY[held] + ' training candidate ' + str(ci) + '}'},
                f'LOO fold "{held} nm held out": adaptive training candidate {ci}/4 at training film {t} nm, chosen from the S4a '
                f'archive using ONLY the two training films (the S4a design is data-independent, so its archive is shared by all folds; '
                f'S4b is not used because it saw all films).', ['{generated}'], ['C1', 'C11', 'C13'], timeout_mult=1.3,
                status='planned_adaptive', depends_on=['S4a'])
    for rank in ('best', 'runner_up'):
        add(f'S5-H{KEY[held]}-PRED-{rank}', 'S5_leave_one_film_out', held, F(mobility='{sel:mobility_branch}', contacts='{sel:contact_branch}'),
            {'all': '{fold:' + KEY[held] + ' ' + rank + ' frozen}'},
            f'LOO frozen prediction of the held-out {held} nm film with the fold\'s {rank.replace("_", "-")} training candidate '
            '(Qf shared value and mu from the law fitted on the two training films; nothing tuned to this film).',
            ['{generated}'], ['C1', 'C11'], timeout_mult=1.3, status='planned_adaptive', depends_on=[f'S5 fold {KEY[held]} training'])

# ================================================================ S6 sensitivity + frozen predictions (27)
k6 = 1
def s6(t, flags, params, purpose, rule, code=('C1', 'C11'), mult=1.3, mode='transfer'):
    global k6
    add(f'S6-{k6:02d}', 'S6_sensitivity_frozen', t, F(**flags), params, purpose, ['{frozen model} + ' + rule], list(code),
        timeout_mult=mult, status='planned_after_calibration', mode=mode, depends_on=['S4c']); k6 += 1
for t in FILMS:
    s6(t, {'confinement': 'low (box MODEL)'}, {'dEc_eV': {2.0: 0.2344, 6.3: 0.0456, 13.2: 0.0127}[t], 'label': 'MODEL / lower end of the extrapolation spread'},
       f'Confinement low end at {t} nm: dEc from the subband box MODEL (also below Codex (2/t)^2 at 2 nm).', f'thickness_laws.dEc_eV.points[{t}]=<value>')
for t in FILMS:
    s6(t, {'confinement': 'high (fit3 x1.107 HSE)'}, {'dEc_eV': round(dEc(t, 1.1071), 4), 'dEg_eV': round(dEg(t, 1.1071), 4),
       'label': 'COMPUTED HSE/PBE worst-case ratio, ASSUMED transfer to this thickness'},
       f'Confinement high end at {t} nm: dEc and dEg x1.107 (HSE06 worst-case ratio at 1 nm).',
       f'thickness_laws.dEc_eV.a={DEC[0] * 1.1071:.5f}; thickness_laws.dEg_QC_eV.a={DEG[0] * 1.1071:.5f}')
for t in FILMS:
    s6(t, {'confinement': 'dft_fit3, bulk mass PBE'}, {'mstar_m0': round(0.159 + dm(t), 4), 'label': 'COMPUTED PBE bulk mass 0.159 instead of LITERATURE 0.208'},
       f'Bulk-mass choice at {t} nm: m* = 0.159 (PBE) + dm(t) (Codex convention) instead of 0.208 + dm(t); NC300 and the mobility mass factor follow.',
       'bulk_reference.mstar_bulk_m0.value=0.159 (+ nc300_override and mu_band recomputed)')
for fac in (0.1, 10.0):
    for t in FILMS:
        s6(t, {'donors': f'shared_constant x{fac:g}'}, {'Nd_cm3': ND0 * fac, 'label': 'ASSUMED sensitivity'},
           f'Donor density x{fac:g} at {t} nm (W is a fully ionised donor in DFT but the active fraction is unknown).', f'thickness_laws.Nd_eff_cm3.Nd0={ND0 * fac:g}')
for eps in (7.0, 11.0):
    for t in (2.0, 13.2):
        s6(t, {}, {'eps_Al2O3': eps, 'label': 'ASSUMED range around the ASSUMED 9.0'}, f'Al2O3 permittivity {eps:g} at {t} nm (C_ox {"+" if eps > 9 else "-"}).',
           f'geometry.stack_bottom_to_top[3].eps_r={eps:g}')
for t in FILMS:
    s6(t, {'deep_gaussian': False, 'dit_sheet': False}, {'NGA_cm3_eV': 0, 'Dit_peak_cm2_eV': 0, 'label': 'ASSUMED-zero alternative (Codex primary)'},
       f'Deep Gaussian and interface acceptor sheet removed at {t} nm (Codex primary model has them at zero).',
       'traps.bulk_deep_acceptor_gaussian.NGA_cm3_eV=0; traps.interface_acceptor_sheet.peak_cm2_eV=0')
s6(6.3, {'nc_mode': 'q2d box MODEL x1.467'}, {'Nc300_cm3': float(f'{nc3d(mstar(6.3)) * 1.467:.4g}'), 'label': 'MODEL crossover (2-parameter box, untested)'},
   'Quasi-2D crossover at 6.3 nm: NC300 x1.467 from the box MODEL (-10 meV equivalent).', 'solver.physics_options.nc300_override_cm3[6.3]=<value>')
for t in FILMS:
    s6(t, {'strip': 'separate_deck'}, {'L_p_um': 20.0, 'vd_V': [0.1, 0.7]}, f'Frozen ungated-strip deck at {t} nm with the calibrated shared '
       'parameters: G_strip(t), I(0.7)/I(0.1). (W/L)_par FITTED on one film, LOO over films offline (no launch).',
       'mode strip', ('C1', 'C8', 'C11'), 1.0, mode='strip')
s6(13.2, {'strip': 'in_solver'}, {'gap_um': 3.0, 'L_s_um': 2.0}, 'In-solver parallel strip (audit 7.11 B) at 13.2 nm: same-name source/drain '
   'volumes, region mobility scaled by (W/L)_par*L_s. Checks that i."drain" contains the strip current and matches the separate deck.',
   'solver.physics_options.strip.mode=in_solver', ('C1', 'C8', 'C11'), 1.5)

# ================================================================ S7 31.8 nm stress (2)
for i, fac in enumerate((1.0, 10.0), 1):
    add(f'S7-0{i}', 'S7_31p8_stress', 31.8, F(donors=f'shared_constant x{fac:g}'), {'all': '{frozen model}', 'Nd_cm3': ND0 * fac,
        'series_resistance_ohm_um': 0, 'mu_band': 'from the shared law at 31.8 nm'},
        f'31.8 nm stress check with the frozen shared model{" and Nd x10 (ASSUMED)" if fac > 1 else ""}; no fitted thick-film charge, '
        'resistance or back sheet. Whole-curve log-RMSE, I(-3 V), I(+3 V). Failure is documented, nothing is fitted.',
        ['{frozen model}', 'contacts.series_resistance_ohm_um[31.8]=0', f'thickness_laws.Nd_eff_cm3.Nd0={ND0 * fac:g}'],
        ['C1', 'C11'], status='planned_after_calibration', depends_on=['S4c'])

# ---------------------------------------------------------------- write
stages = {}
for e in RUNS: stages[e['stage']] = stages.get(e['stage'], 0) + 1
out = {
    'schema': 'IWO_campaign_matrix_2026-10-10',
    'document': 'analysis_2026-10-10_campaign/CAMPAIGN_DESIGN.md',
    'generator': 'analysis_2026-10-10_campaign/make_campaign_matrix.py (pure arithmetic; launches nothing)',
    'model_file_env': 'IWO_MODEL_FILE=config/iwo_material_model_v2.yaml for every entry',
    'launch_rules': ['sequential only (run_campaign.py --workers 1)', 'every launch counts, failed or not', 'hard cap 200 launches',
                     'regress_all_decks.py must print "unexpected differences 0" after every code change and before the first launch',
                     'entries with status planned_adaptive / planned_after_calibration are written into a config/campaign_*.json only after the '
                     'named stage has been analysed; their {fit:..}/{sel:..}/{fold:..}/{frozen ..} tokens must be resolved first'],
    'shared_start_values': {'Qf_cm2': QF0, 'Ns_cm2': NS0, 'WT_eV': WT0, 'Nd_cm3': ND0, 'mu_inf_cm2Vs': round(MUINF0, 3), 'ell_nm': round(ELL0, 3),
                            'labels': 'ASSUMED start values (Qf, mu_inf, ell from the V2 FITTED anchors; Ns, WT from V1 FITTED); all five are FITTED in S4. '
                                      'Nd_cm3: ' + ND_LABEL + ' (not re-fitted in this campaign; x0.1 / x10 in S6)'},
    'derived_per_film': {KEY[t]: primary_params(t) for t in FILMS},
    'stage_counts': stages, 'planned_launches': len(RUNS), 'reserve_launches': 200 - len(RUNS), 'cap': 200,
    'runs': RUNS}
(HERE / 'campaign_matrix.json').write_text(json.dumps(out, indent=1))
print(json.dumps(stages, indent=1), 'planned', len(RUNS), 'reserve', 200 - len(RUNS))
print('start mu_inf', MUINF0, 'ell', ELL0)
for t in FILMS: print(t, primary_params(t))
for k_, v in FN.items(): print('FN', k_, 'HfO2 barrier', fn_constants(*v), '-> ATLAS (Al2O3/IWO-segment field)', fn_atlas(*v))
