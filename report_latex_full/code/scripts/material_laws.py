#!/usr/bin/env python3
"""IWO_material(t, xW): thickness-aware material laws for ~2 at.% W:In2O3 (V1).

No simulator is run. This script (1) fits the thickness laws to the literature/DFT evidence
listed in tables/THICKNESS_LAW_EVIDENCE.csv, (2) evaluates them at the four measured
thicknesses, (3) writes config/iwo_material_model.yaml (consumed by build_iwo_decks.py),
tables/THICKNESS_LAWS.csv and the global thickness plots under plots/.

Evidence labels (docs/PARAMETER_PROVENANCE.md): MEASURED_TARGET_DEVICE, MEASURED_RELATED_MATERIAL,
DFT_TARGET_IWO, DFT_PURE_IN2O3_PROXY, LITERATURE_IWO, LITERATURE_IN2O3_PROXY, CALCULATED, FITTED,
NUMERICAL, ASSUMED.

APPROACH A (thickness-dependent effective material + classical drift-diffusion): the DFT band-edge
confinement enters ONLY through Eg(t), chi(t), m*(t) -> Nc(t); no BQP/Schrodinger correction is
applied on top (no double counting).
"""
import csv, json, math
from pathlib import Path
import numpy as np
try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
KB = 8.617333262e-5; T = 300.0; kT = KB * T
H = 6.62607015e-34; ME = 9.1093837015e-31; KBJ = 1.380649e-23

def nc_3d(mstar_rel, temp=T):
    """Effective conduction-band DOS, 3-D parabolic band, cm^-3."""
    return 2.0 * (2.0 * math.pi * mstar_rel * ME * KBJ * temp / H**2) ** 1.5 / 1e6

# ---------------------------------------------------------------- evidence table
EVIDENCE = [
    # quantity, value, unit, thickness_nm, material, label, source, location
    ('Eg_PBE', 0.94, 'eV', 'bulk', 'In2O3', 'DFT_PURE_IN2O3_PROXY', 'Lin2022_ACSNano', 'Methods, p.21542'),
    ('Eg_PBE', 1.27, 'eV', 1.98, 'In2O3 slab (H-passivated, vacuum)', 'DFT_PURE_IN2O3_PROXY', 'Lin2022_ACSNano', 'Methods, p.21542'),
    ('Eg_PBE', 1.88, 'eV', 0.95, 'In2O3 slab', 'DFT_PURE_IN2O3_PROXY', 'Lin2022_ACSNano', 'Methods, p.21542'),
    ('dEc_PBE', 0.60, 'eV', 1.5, 'In2O3 on Al2O3 slab; Ev ~unchanged', 'DFT_PURE_IN2O3_PROXY', 'Si2021_NanoLett', 'p.504, Fig.4b text'),
    ('mstar', 0.17, 'm0', 'bulk', 'In2O3 (PBE)', 'DFT_PURE_IN2O3_PROXY', 'Lin2022_ACSNano', 'p.21540'),
    ('mstar', 0.19, 'm0', 3.52, 'In2O3 slab (PBE)', 'DFT_PURE_IN2O3_PROXY', 'Lin2022_ACSNano', 'p.21540'),
    ('mstar', 0.23, 'm0', 1.98, 'In2O3 slab (PBE)', 'DFT_PURE_IN2O3_PROXY', 'Lin2022_ACSNano', 'p.21540'),
    ('mstar', 0.30, 'm0', 0.95, 'In2O3 slab (PBE)', 'DFT_PURE_IN2O3_PROXY', 'Lin2022_ACSNano', 'p.21540'),
    ('mstar_exp', 0.208, 'm0', 'bulk', 'In2O3 single crystal, n=2.8e17 (optical Hall)', 'MEASURED_RELATED_MATERIAL', 'Stokey2021_JAP', 'Abstract; Sec. IV.C'),
    ('mstar_exp_0', 0.18, 'm0', 'bulk', 'In2O3 zero-density extrapolation (Feneberg, cited)', 'LITERATURE_IN2O3_PROXY', 'Stokey2021_JAP', 'Sec. I, Eq.(3)'),
    ('eps_DC', 10.55, '-', 'bulk', 'In2O3 single crystal (LST/THz)', 'MEASURED_RELATED_MATERIAL', 'Stokey2021_JAP', 'Abstract; Table II'),
    ('eps_DC', 8.9, '-', 'film', 'evaporated In2O3 films (Hamberg, cited)', 'LITERATURE_IN2O3_PROXY', 'Si2021_NanoLett', 'p.501'),
    ('eps_r', 9.30, '-', 'film', 'IWO of the target process (C-V, SI Fig.S1)', 'MEASURED_TARGET_DEVICE', 'Januar2026_SI (not bundled; value recorded in Astra SOURCES_AND_CORRECTIONS)', 'SI Fig.S1b'),
    ('eps_r', 9.03, '-', 'film', 'In2O3 of the target process (C-V, SI Fig.S1)', 'MEASURED_RELATED_MATERIAL', 'Januar2026_SI (not bundled)', 'SI Fig.S1b'),
    ('eps_r_HfO2', 19.57, '-', 'film', 'HfO2 of the target process', 'MEASURED_TARGET_DEVICE', 'Januar2026_SI (not bundled)', 'SI Fig.S1b'),
    ('Eg_IWO', 3.05, 'eV', 'film', 'sputtered a-IWO, different device (Fan 2021)', 'LITERATURE_IWO', 'Fan2021_Nanomaterials (cited by Astra)', 'Sec.3'),
    ('chi_IWO', 4.30, 'eV', 'film', 'estimate, 96/4 composition mixing (Fan 2021)', 'LITERATURE_IWO', 'Fan2021_Nanomaterials (cited by Astra)', 'Sec.3'),
    ('CNL_above_Ec', 0.4, 'eV', 'bulk', 'In2O3', 'LITERATURE_IN2O3_PROXY', 'Si2021_NanoLett; Lin2022; Wang2022', 'text'),
    ('Dit', 6.0e11, 'cm^-2 eV^-1', 1.2, 'HfO2/In2O3 (from SS 63.5 mV/dec)', 'LITERATURE_IN2O3_PROXY', 'Lin2022_ACSNano', 'p.21539'),
    ('Dit', 6.3e11, 'cm^-2 eV^-1', 3.5, 'HfO2/In2O3 (subthreshold method)', 'LITERATURE_IN2O3_PROXY', 'Wang2022_FrontMater', 'p.4'),
    ('bulk_DOS', 3.3e20, 'cm^-3 eV^-1', 3.5, 'ALD In2O3 (conductance method), ND 1e20', 'LITERATURE_IN2O3_PROXY', 'Wang2022_FrontMater', 'Abstract; p.4-5'),
    ('Nt', 5.3e19, 'cm^-3', 2.0, 'IWO 2 nm (compact-model extraction, unstressed)', 'LITERATURE_IWO (target process, PBS device)', 'Januar2026', 'p.9'),
    ('Nt', 3.39e18, 'cm^-3', 10.0, 'IWO 10 nm (compact-model extraction, unstressed)', 'LITERATURE_IWO (target process, PBS device)', 'Januar2026', 'p.9'),
    ('Nt_ratio_13p2_to_2', 4.0, '-', '2..13.2', 'IWO thickness series', 'LITERATURE_IWO', 'Januar2026', 'Sec.2.8, Fig.5a'),
    ('Delta_sr', 2.87, 'A', 'series', 'IWO effective roughness (fit of mu vs t)', 'LITERATURE_IWO', 'Januar2026', 'Sec.2.9, Fig.5f'),
    ('mu_max', 27.4, 'cm^2/Vs', 13.2, 'IWO peak field-effect mobility', 'LITERATURE_IWO', 'Januar2026', 'Sec.2.8'),
    ('mu_max', 5.1, 'cm^2/Vs', 2.0, 'IWO peak field-effect mobility', 'LITERATURE_IWO', 'Januar2026', 'Sec.2.8'),
    ('Nbk_LFN', 2.37e18, 'cm^-3 eV^-1', 10, 'IWO (1 wt% WO3, SiO2 gate) border traps', 'LITERATURE_IWO (different process)', 'Kim2024_APL', 'p.6'),
    ('Nbk_LFN', 3.12e18, 'cm^-3 eV^-1', 20, 'same', 'LITERATURE_IWO (different process)', 'Kim2024_APL', 'p.6'),
    ('Nbk_LFN', 14.6e18, 'cm^-3 eV^-1', 30, 'same', 'LITERATURE_IWO (different process)', 'Kim2024_APL', 'p.6'),
]

def fit_power(ts, ys):
    """y = a * t^(-p) by log-log least squares."""
    x = np.log(np.array(ts)); y = np.log(np.array(ys))
    p, lna = np.polyfit(x, y, 1)
    return float(math.exp(lna)), float(-p)

def main():
    (ROOT / 'tables').mkdir(exist_ok=True); (ROOT / 'plots').mkdir(exist_ok=True); (ROOT / 'config').mkdir(exist_ok=True)
    with (ROOT / 'tables' / 'THICKNESS_LAW_EVIDENCE.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['quantity', 'value', 'unit', 'thickness_nm', 'material', 'label', 'source', 'location']); w.writerows(EVIDENCE)

    # --- 1. Quantum-confinement band-edge shift (pure In2O3 DFT proxy): dEg_QC(t) = a t^-p
    ts = [0.95, 1.5, 1.98]; dE = [1.88 - 0.94, 0.60, 1.27 - 0.94]
    a_qc, p_qc = fit_power(ts, dE)
    dEg = lambda t: a_qc * t ** (-p_qc)
    # partition: Ev unchanged (Si2021) -> dEc = dEg, chi(t) = chi_bulk - dEc(t)
    # --- 2. Effective mass: m*(t) = m*_bulk,exp + dm*(t), dm* from Lin2022 slab-minus-bulk (PBE)
    tm = [0.95, 1.98, 3.52]; dm = [0.30 - 0.17, 0.23 - 0.17, 0.19 - 0.17]
    b_m, q_m = fit_power(tm, dm)
    mstar = lambda t: 0.208 + b_m * t ** (-q_m)
    # --- 3. Tail density Nt(t) = Nt2 * (2/t)^alpha; Tt shared
    Nt2 = 2.0e19; alpha = 0.75; WTA = 0.040
    Nt = lambda t: Nt2 * (2.0 / t) ** alpha
    # --- 4. Effective background donor density (FITTED law, Kim2024 trend as qualitative support)
    Nd0, tc, k = 2.5e17, 20.0, 4.0
    Nd = lambda t: Nd0 * (1.0 + (t / tc) ** k)
    # --- 5. Mobility: mu0(t) = mu_band(t) * (1 - Dsr/t)^2 ; mu_band per thickness (FITTED, V0 baseline values)
    Dsr = 0.287
    mu_band_fitted = {2.0: 16.8, 6.3: 12.4, 13.2: 57.6, 31.8: 84.0}
    rough = lambda t: (1.0 - Dsr / t) ** 2

    Eg_bulk, chi_bulk, eps_iwo = 3.05, 4.30, 9.30
    rows = []
    for t in [2.0, 6.3, 13.2, 31.8]:
        m = mstar(t)
        rows.append({'thickness_nm': t, 'dEg_QC_eV': round(dEg(t), 4), 'Eg_eV': round(Eg_bulk + dEg(t), 4), 'dEc_eV': round(dEg(t), 4),
                     'chi_eV': round(chi_bulk - dEg(t), 4), 'mstar_m0': round(m, 4), 'Nc300_cm3': f'{nc_3d(m):.3e}',
                     'Nt_cm3': f'{Nt(t):.3e}', 'NTA_cm3_eV': f'{Nt(t) / WTA:.3e}', 'WTA_eV': WTA, 'Tt_K': round(WTA / KB, 0),
                     'Nd_eff_cm3': f'{Nd(t):.3e}', 'roughness_factor': round(rough(t), 4), 'mu_band_cm2Vs_fitted': mu_band_fitted[t],
                     'mu0_cm2Vs': round(mu_band_fitted[t] * rough(t), 2), 'eps_r': eps_iwo})
    with (ROOT / 'tables' / 'THICKNESS_LAWS.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    model = {
        'schema': 'IWO_material_model_v1', 'status': 'V1 physics-constrained seed; electronic values are NOT ATLAS-calibrated until results/ say so',
        'composition': {'xW_at_percent': 2.0, 'definition': 'NOT DETERMINED FROM AVAILABLE DATA: the target paper states "IWO (~2% W)" without specifying atomic %, cation %, mol% WO3 or target composition; treated as a material label, never converted to a donor density.'},
        'temperature_K': {'value': 300.0, 'label': 'ASSUMED', 'note': 'measurement temperature not recorded in workbook'},
        'bulk_reference': {
            'Eg_bulk_eV': {'value': Eg_bulk, 'label': 'LITERATURE_IWO', 'source': 'Fan2021_Nanomaterials Sec.3 (different sputtered IWO device)', 'uncertainty_eV': 0.2},
            'chi_bulk_eV': {'value': chi_bulk, 'label': 'LITERATURE_IWO', 'source': 'Fan2021_Nanomaterials Sec.3 (composition-mixing estimate)', 'uncertainty_eV': 0.3,
                            'consistency_check': 'bulk In2O3 CNL ~0.4 eV above Ec (Si2021/Lin2022/Wang2022); thin-film Ec rises by dEc(t) so TNL appears deeper below Ec -> EF farther below Ec -> n_FB down, Vth up'},
            'mstar_bulk_m0': {'value': 0.208, 'label': 'MEASURED_RELATED_MATERIAL', 'source': 'Stokey2021_JAP optical Hall (pure In2O3 crystal); W-doping increases m* (Januar2026 PBE, qualitative) -> NOT DETERMINED numerically'},
            'eps_r': {'value': eps_iwo, 'label': 'MEASURED_TARGET_DEVICE', 'source': 'Januar2026 SI Fig.S1 (C-V, IWO 9.30+/-0.04; not bundled, recorded by Astra)', 'alternatives': {'bulk_crystal_static': 10.55, 'evaporated_film': 8.9}, 'thickness_dependence': 'none imposed (no evidence)'},
            'Nv300_cm3': {'value': 1.0e19, 'label': 'ASSUMED', 'note': 'holes are not solved (electrons-only DD); enters only ni'},
            'hole_mobility_cm2Vs': {'value': 0.01, 'label': 'ASSUMED'},
            'srh_tau_s': {'value': 1.0e-6, 'label': 'ASSUMED', 'note': 'background SRH, negligible in n-type wide gap'},
        },
        'thickness_laws': {
            'dEg_QC_eV': {'form': 'a * t_nm^(-p)', 'a': round(a_qc, 4), 'p': round(p_qc, 4), 'label': 'DFT_PURE_IN2O3_PROXY',
                          'fit_points': [{'t_nm': t, 'dE_eV': e, 'source': s} for t, e, s in zip(ts, dE, ['Lin2022 slab 0.95 nm', 'Si2021 In2O3/Al2O3 1.5 nm (dEc)', 'Lin2022 slab 1.98 nm'])],
                          'note': 'PBE absolute gaps are NOT used; only slab-minus-bulk shifts. Pure In2O3 proxy for IWO; H-passivated/Al2O3-terminated slabs vs air/Al2O3 in device. Uncertainty ~ +/-50 %.'},
            'band_edge_partition': {'dEc_over_dEg': 1.0, 'label': 'DFT_PURE_IN2O3_PROXY', 'source': 'Si2021: Ec moves up, Ev almost unchanged'},
            'Eg_eV': 'Eg_bulk + dEg_QC(t)', 'chi_eV': 'chi_bulk - dEc(t)',
            'mstar_m0': {'form': 'mstar_bulk_exp + b * t_nm^(-q)', 'b': round(b_m, 4), 'q': round(q_m, 4), 'label': 'MEASURED_RELATED_MATERIAL + DFT_PURE_IN2O3_PROXY increment'},
            'Nc300_cm3': {'form': '2*(2*pi*m*kT/h^2)^1.5', 'label': 'CALCULATED', 'note': '3-D parabolic continuum DOS; at 2 nm the film is quasi-2D, so Nc is an effective continuum parameter'},
            'Nt_cm3': {'form': 'Nt2 * (2/t_nm)^alpha', 'Nt2': Nt2, 'alpha': alpha, 'label': 'FITTED (anchor from real-ATLAS 2 nm fit: NTA*WTA) consistent with LITERATURE_IWO trend (Januar: ~4x from 13.2 to 2 nm; 5.3e19 at 2 nm with theta_t convention)'},
            'WTA_eV': {'value': WTA, 'label': 'FITTED, shared across thickness', 'Tt_K': round(WTA / KB, 0), 'note': 'Januar2026 reports only dTt under stress; absolute Tt NOT DETERMINED FROM AVAILABLE DATA'},
            'NTA_cm3_eV': 'Nt(t)/WTA  (gTA(E)=NTA*exp((E-Ec)/WTA); integral over the gap = NTA*WTA*(1-exp(-Eg/WTA)) ~ NTA*WTA)',
            'Nd_eff_cm3': {'form': 'Nd0 * (1 + (t_nm/tc)^k)', 'Nd0': Nd0, 'tc_nm': tc, 'k': k, 'label': 'FITTED law (effective electrically active background donor density, NOT W concentration)',
                           'support': 'Kim2024 (different IWO process): bulk/border trap density 2.4/3.1/14.6e18 at 10/20/30 nm; Januar2026: EF0 deeper for thinner films'},
            'mu0_cm2Vs': {'form': 'mu_band(t) * (1 - Dsr/t)^2', 'Dsr_nm': Dsr, 'Dsr_label': 'LITERATURE_IWO (Januar2026 Fig.5f, 2.87 A)',
                          'mu_band_fitted': mu_band_fitted, 'label': 'FITTED per thickness (no defensible law; sigmoidal trend attributed to percolation/crystallinity, hypothesis)',
                          'gate_dependence': 'NOT inserted natively: ATLAS 5.28.1.R ignores MOBILITY updates between SOLVEs (Claude run_0008); the free/trapped partition of Eq.(5) is produced self-consistently by the DOS occupancy; the Ando roll-off theta_r*Vov is an approximation gap (see LIMITATIONS)'},
        },
        'traps': {
            'bulk_acceptor_tail': {'atlas': 'DEFECTS NTA WTA (cm^-3/eV, eV), acceptor-like, referenced to Ec', 'capture_cm2': 1e-15, 'capture_label': 'ASSUMED'},
            'bulk_deep_acceptor_gaussian': {'NGA_cm3_eV': 5e16, 'EGA_from_Ec_eV': 0.6, 'WGA_eV': 0.15, 'label': 'ASSUMED (insensitive; Fan2021 range 2.5-3.7e16 for a different device)'},
            'bulk_donor_tail': {'NTD_cm3_eV': 0, 'label': 'ASSUMED zero (valence tail has negligible effect on n-type transfer curves; Fan2021)'},
            'shallow_donor_gaussian': {'NGD_cm3_eV': 0, 'label': 'ASSUMED zero in V1: the effective donor background is represented by Nd_eff(t); a donor Gaussian at fixed absolute energy (EGD referenced to Ev) is the V2 candidate to replace Nd_eff(t) by the confinement mechanism'},
            'interface_acceptor_sheet': {'peak_cm2_eV': 3e11, 'center_from_Ec_eV': 0.3, 'width_eV': 0.12, 'label': 'ASSUMED, shared across thickness; literature Dit(HfO2/In2O3) ~6e11 cm^-2/eV (LITERATURE_IN2O3_PROXY; here IWO/Al2O3)', 'implementation': 'regularized 0.25 nm IWO layer at the Al2O3 interface: volume amplitude = sheet peak / 0.25 nm (numerically verified: layer /2 changes Id by 0.009 dec)'},
            'fixed_interface_charge_Qf_cm2': {'value': 0.0, 'label': 'FITTED single shared value (stage 3); classified as effective electrostatic correction'},
            'back_surface_donor_sheet': {'peak_cm2_eV': 0.0, 'center_from_Ec_eV': 0.02, 'width_eV': 0.05,
                                         'label': 'HYPOTHESIS, 31.8 nm only when non-zero (device-specific, stage 6): donor-like states at the free IWO back surface, regularized in a 0.25 nm layer (region 5). Zero for the thin films. Not identifiable separately from Nd and Qf with one transfer curve (V0 evidence: needed to reproduce the flat always-on baseline).'},
        },
        'contacts': {'gate_workfunction_eV': {'value': 4.70, 'label': 'ASSUMED (TiN 4.5-4.9 eV literature range); degenerate with Qf and chi -> held fixed'},
                     'source_drain': {'model': 'ideal Ohmic (no workfunction)', 'label': 'ASSUMED; underconstrained (no TLM); CNL above Ec in In2O3 supports low-barrier contacts (Si2021/Lin2022)'},
                     'series_resistance_ohm_um': {'2.0': 0, '6.3': 0, '13.2': 0, '31.8': 9.2e4, 'label': '31.8 nm only, FITTED hypothesis (on-state saturation); total device 672 ohm at 3 V bounds it'}},
        'geometry': {'L_um': 20.0, 'W_um': 290.0, 'sim_width_um': 1.0, 'hfo2_nm': 15.0, 'al2o3_nm': 2.0, 'contact_overlap_um': {'value': 2.0, 'label': 'ASSUMED numerical contact geometry (not reported)'},
                     'eps_hfo2': 19.57, 'eps_al2o3': {'value': 9.0, 'label': 'ASSUMED'}, 'top_of_channel': 'AIR (no cap)'},
    }
    if yaml:
        (ROOT / 'config' / 'iwo_material_model.yaml').write_text(yaml.safe_dump(model, sort_keys=False, width=140))
    (ROOT / 'config' / 'iwo_material_model.json').write_text(json.dumps(model, indent=2))

    # --- plots
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        tt = np.linspace(0.8, 35, 400)
        fig, ax = plt.subplots(2, 3, figsize=(13, 7.5))
        ax[0, 0].plot(tt, Eg_bulk + dEg(tt), label='Eg(t) = 3.05 + dEg_QC (proxy)'); ax[0, 0].plot(ts, [Eg_bulk + e for e in dE], 'ko', label='DFT shifts (Lin2022, Si2021)')
        ax[0, 0].set_xscale('log'); ax[0, 0].set_ylabel('Eg (eV)'); ax[0, 0].legend(fontsize=7)
        ax[0, 1].plot(tt, dEg(tt), label='dEc = dEg (Ev fixed)'); ax[0, 1].plot(tt, chi_bulk - dEg(tt), label='chi(t) = 4.30 - dEc'); ax[0, 1].set_xscale('log'); ax[0, 1].set_ylabel('eV'); ax[0, 1].legend(fontsize=7)
        ax[0, 2].plot(tt, mstar(tt), label='m*(t) = 0.208 + dm*(t)'); ax[0, 2].plot([0.95, 1.98, 3.52], [0.208 + d for d in dm], 'ko', label='PBE increments (Lin2022)'); ax[0, 2].set_xscale('log'); ax[0, 2].set_ylabel('m*/m0'); ax[0, 2].legend(fontsize=7)
        ax[1, 0].semilogy(tt, [nc_3d(mstar(x)) for x in tt]); ax[1, 0].set_xscale('log'); ax[1, 0].set_ylabel('Nc (cm^-3)')
        ax[1, 1].loglog(tt, Nt(tt), label='Nt(t) law'); ax[1, 1].loglog([2.0, 10.0], [5.3e19, 3.39e18], 'rs', label='Januar2026 (PBS devices)'); ax[1, 1].loglog([2.0, 6.3, 13.2], [2.0e19, 1.34e19, 4.6e18], 'ko', label='real-ATLAS fits (Claude V0)'); ax[1, 1].set_ylabel('Nt (cm^-3)'); ax[1, 1].legend(fontsize=7)
        ax[1, 2].loglog(tt, Nd(tt), label='Nd_eff(t) law'); ax[1, 2].loglog([2.0, 6.3, 13.2, 31.8], [2e17, 3e17, 3e17, 2.65e18], 'ko', label='real-ATLAS fits (Claude V0)'); ax[1, 2].set_ylabel('Nd_eff (cm^-3)'); ax[1, 2].legend(fontsize=7)
        for a in ax.flat: a.set_xlabel('IWO thickness (nm)'); a.grid(alpha=.3)
        fig.suptitle('IWO_material(t) V1 thickness laws: DFT proxies (pure In2O3), measured bulk m*, fitted Nt/Nd laws')
        fig.tight_layout(); fig.savefig(ROOT / 'plots' / 'thickness_laws_overview.png', dpi=130); plt.close(fig)
        fig, ax = plt.subplots(figsize=(6, 4)); ax.semilogx(tt, rough(tt), label='(1 - Dsr/t)^2, Dsr = 2.87 A')
        for t, mu in mu_band_fitted.items(): ax.plot(t, rough(t), 'ko')
        ax.set_xlabel('t (nm)'); ax.set_ylabel('roughness factor'); ax.legend(); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(ROOT / 'plots' / 'mobility_roughness_factor.png', dpi=130); plt.close(fig)
    except Exception as e:
        print('plots skipped:', e)
    print(f'dEg_QC(t) = {a_qc:.3f} * t^-{p_qc:.3f} eV ; m*(t) = 0.208 + {b_m:.3f} * t^-{q_m:.3f}')
    for r in rows: print(r)

if __name__ == '__main__':
    main()
