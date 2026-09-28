#!/usr/bin/env python3
"""Generate the four ATLAS decks from ONE material model: IWO_material(t, xW).

  python scripts/build_iwo_decks.py                      # decks/iwo_{2p0,6p3,13p2,31p8}nm.in
  python scripts/build_iwo_decks.py --thickness 2 --override traps.fixed_interface_charge_Qf_cm2.value=-3e11

Reads config/iwo_material_model.yaml (thickness laws + provenance), config/geometry.yaml and
config/solver.yaml. Every material parameter written to a deck carries its value, law, status
label and source as a comment. No simulator is run by this script.

Reduced electrical deck (DC): ideal TiN gate boundary at the HfO2 bottom, ideal Pd S/D boundaries on
the IWO top surface. Continuous metals are equipotential in DC, so replacing their volumes by
Dirichlet boundaries changes nothing electrically while removing nodes (Astra kept metal volumes:
identical fits). --full writes decks/full_physical_structure.in with explicit Conductor/Palladium
volumes for TonyPlot.
"""
from __future__ import annotations
import argparse, copy, json, math
from pathlib import Path
import numpy as np, yaml

ROOT = Path(__file__).resolve().parents[1]
EPS0 = 8.8541878128e-14; Q = 1.602176634e-19; KB = 8.617333262e-5
H = 6.62607015e-34; ME = 9.1093837015e-31; KBJ = 1.380649e-23
KEYS = {2.0: '2p0', 6.3: '6p3', 13.2: '13p2', 31.8: '31p8'}

def load_configs():
    m = yaml.safe_load((ROOT / 'config' / 'iwo_material_model.yaml').read_text())
    g = yaml.safe_load((ROOT / 'config' / 'geometry.yaml').read_text())
    s = yaml.safe_load((ROOT / 'config' / 'solver.yaml').read_text())
    return m, g, s

def set_dotted(d, path, value):
    """Override 'a.b.c=value'. A segment in brackets may contain a dot and matches numeric keys:
    thickness_laws.mu0_cm2Vs.mu_band_fitted[2.0]=18.1 sets the float key 2.0 of that mapping."""
    import re
    keys = [a or b for a, b in re.findall(r'\[([^\]]+)\]|([^.\[\]]+)', path)]
    def resolve(c, k):
        if isinstance(c, list): return int(k)
        if k in c: return k
        try:
            fk = float(k)
            for kk in c:
                if isinstance(kk, (int, float)) and not isinstance(kk, bool) and kk == fk: return kk
        except ValueError: pass
        return k
    cur = d
    for k in keys[:-1]:
        cur = cur[resolve(cur, k)]
    last = resolve(cur, keys[-1])
    try: value = float(value)
    except (TypeError, ValueError): pass
    if isinstance(cur, dict) and last in cur and isinstance(cur[last], dict) and 'value' in cur[last]: cur[last]['value'] = value
    else: cur[last] = value

def val(x):
    return x['value'] if isinstance(x, dict) and 'value' in x else x

def nc_3d(mstar, T=300.0):
    return 2.0 * (2.0 * math.pi * mstar * ME * KBJ * T / H ** 2) ** 1.5 / 1e6

def cox(g):
    return EPS0 / (g['stack_bottom_to_top'][2]['thickness_nm'] * 1e-7 / g['stack_bottom_to_top'][2]['eps_r'] + g['stack_bottom_to_top'][3]['thickness_nm'] * 1e-7 / g['stack_bottom_to_top'][3]['eps_r'])

def material_at(m, t):
    """Evaluate IWO_material(t) -> dict of ATLAS-ready values and their provenance strings."""
    L = m['thickness_laws']; b = m['bulk_reference']
    dEg = L['dEg_QC_eV']['a'] * t ** (-L['dEg_QC_eV']['p'])
    dEc = dEg * L['band_edge_partition']['dEc_over_dEg']
    Eg = val(b['Eg_bulk_eV']) + dEg; chi = val(b['chi_bulk_eV']) - dEc
    mstar = val(b['mstar_bulk_m0']) + L['mstar_m0']['b'] * t ** (-L['mstar_m0']['q'])
    Nc = nc_3d(mstar)
    Nt = L['Nt_cm3']['Nt2'] * (2.0 / t) ** L['Nt_cm3']['alpha']; WTA = val(L['WTA_eV']); NTA = Nt / WTA
    Nd = L['Nd_eff_cm3']['Nd0'] * (1.0 + (t / L['Nd_eff_cm3']['tc_nm']) ** L['Nd_eff_cm3']['k'])
    Dsr = L['mu0_cm2Vs']['Dsr_nm']; rough = (1.0 - Dsr / t) ** 2
    mb = L['mu0_cm2Vs']['mu_band_fitted']; mu_band = mb.get(t, mb.get(str(t), None))
    if mu_band is None: mu_band = float(np.interp(t, sorted(float(k) for k in mb), [mb[k] for k in sorted(mb, key=float)]))
    mu0 = mu_band * rough
    tr = m['traps']; ct = m['contacts']
    rs = ct['series_resistance_ohm_um']; rs_t = float(rs.get(str(t), rs.get(t, 0.0)) if isinstance(rs, dict) else 0.0)
    return {'t_nm': t, 'dEg_QC_eV': dEg, 'dEc_eV': dEc, 'Eg_eV': Eg, 'chi_eV': chi, 'mstar_m0': mstar, 'Nc_cm3': Nc, 'Nv_cm3': val(b['Nv300_cm3']),
            'eps_iwo': val(b['eps_r']), 'Nt_cm3': Nt, 'NTA_cm3_eV': NTA, 'WTA_eV': WTA, 'Nd_cm3': Nd, 'rough': rough, 'mu_band': mu_band, 'mu0': mu0,
            'mup': val(b['hole_mobility_cm2Vs']), 'tau_s': val(b['srh_tau_s']),
            'NGA': tr['bulk_deep_acceptor_gaussian']['NGA_cm3_eV'], 'EGA': tr['bulk_deep_acceptor_gaussian']['EGA_from_Ec_eV'], 'WGA': tr['bulk_deep_acceptor_gaussian']['WGA_eV'],
            'NTD': tr['bulk_donor_tail']['NTD_cm3_eV'], 'NGD': tr['shallow_donor_gaussian']['NGD_cm3_eV'],
            'EGD_from_Ec': tr['shallow_donor_gaussian'].get('EGD_from_Ec_eV', 0.1), 'WGD': tr['shallow_donor_gaussian'].get('WGD_eV', 0.1),
            'sig': tr['bulk_acceptor_tail']['capture_cm2'], 'it_peak': tr['interface_acceptor_sheet']['peak_cm2_eV'], 'it_e': tr['interface_acceptor_sheet']['center_from_Ec_eV'], 'it_w': tr['interface_acceptor_sheet']['width_eV'],
            'Qf_cm2': val(tr['fixed_interface_charge_Qf_cm2']), 'gate_wf': val(ct['gate_workfunction_eV']), 'rs_ohm_um': rs_t,
            'bs_peak': tr.get('back_surface_donor_sheet', {}).get('peak_cm2_eV', 0.0), 'bs_e': tr.get('back_surface_donor_sheet', {}).get('center_from_Ec_eV', 0.02), 'bs_w': tr.get('back_surface_donor_sheet', {}).get('width_eV', 0.05),
            'Qb_cm2': float(val(tr.get('back_surface_fixed_charge_cm2', 0.0)) or 0.0),   # fixed charge at the free (air-side) IWO surface; 0 unless a hypothesis run sets it
            'T_K': val(m['temperature_K'])}

def moment_matched_gaussian(a_b, w_b, e_b, a_i, w_i, e_i):
    """Single Gaussian (ATLAS form exp(-((E-E0)/W)^2)) preserving area and first two moments of two overlapping Gaussians."""
    mass = a_b * w_b + a_i * w_i
    if mass <= 0: return e_b, w_b, 0.0
    e = (a_b * w_b * e_b + a_i * w_i * e_i) / mass
    var = (a_b * w_b * (w_b ** 2 / 2 + (e_b - e) ** 2) + a_i * w_i * (w_i ** 2 / 2 + (e_i - e) ** 2)) / mass
    w = math.sqrt(2 * var); return e, w, mass / w

def defects_block(p, region, di_nm, interface, back=False):
    sig = p['sig']
    if back:
        ngd = p['bs_peak'] / (di_nm * 1e-7); egd = p['Eg_eV'] - p['bs_e']
        nga, ega, wga = p['NGA'], p['EGA'], p['WGA']
    else:
        ngd = p['NGD']; egd = p['Eg_eV'] - p['EGD_from_Ec']
        a_i = p['it_peak'] / (di_nm * 1e-7) if interface else 0.0
        ega, wga, nga = moment_matched_gaussian(p['NGA'], p['WGA'], p['EGA'], a_i, p['it_w'], p['it_e'])
    return [f'# Region {region}: continuous DOS. NTA cm^-3/eV at Ec (tail intercept), WTA eV; NGA/NGD Gaussian amplitudes cm^-3/eV;',
            '#   EGA measured from Ec, EGD measured from Ev (installed manual, DEFECTS statement).' + ('  Interface sheet regularized: NGA = sheet peak / layer thickness.' if interface else '') + ('  Back-surface donor sheet regularized.' if back else ''),
            f'defects region={region} continuous numa={{NUMA}} numd={{NUMD}} \\',
            f' nta={p["NTA_cm3_eV"]:.6g} wta={p["WTA_eV"]:.6g} ntd={p["NTD"]:.6g} wtd=0.1 \\',
            f' nga={nga:.6g} ega={ega:.6g} wga={wga:.6g} \\',
            f' ngd={ngd:.6g} egd={egd:.6g} wgd={p["WGD"] if not back else p["bs_w"]:.6g} \\',
            f' sigtae={sig:.3g} sigtah={sig:.3g} sigtde={sig:.3g} sigtdh={sig:.3g} \\',
            f' siggae={sig:.3g} siggah={sig:.3g} siggde={sig:.3g} siggdh={sig:.3g} \\',
            f' afile=acceptor_r{region}.dat dfile=donor_r{region}.dat']

def build_deck(t, m, g, s, meas=None, targets=None, smoke=False, full=False, vstep=None, segments=None, output_vgs=None, vd_segments=None):
    """full: physical structure (Air above the channel, Pd source/drain volumes, Al2O3 and HfO2 regions, Conductor
    gate volume representing TiN). segments: [(end_V, step_V), ...] -> ATLAS stepped sweep blocks
    SOLVE VSTEP=.. VFINAL=.. NAME=gate (one block per segment, split at the METHOD switch and the Vth save);
    vstep: shorthand for a single segment. Neither -> one SOLVE per point (legacy).
    output_vgs: PREDICTION mode (2026-09-25) - ID-VD families at these gate voltages instead of the transfer sweep;
    vd_segments: [(end_V, step_V), ...] drain sweep from 0 V (stepped SOLVE VSTEP/VFINAL NAME=drain blocks)."""
    # Hypothesis option: the PHYSICAL film thickness (geometry AND thickness laws) may differ from the nominal XRR
    # thickness t that labels the measured curve (geometry.film_thickness_override_nm). Default: identical.
    t_nom = t; t = float(g.get('film_thickness_override_nm') or t_nom)
    p = material_at(m, t); key = KEYS[t_nom]
    T_run = 300.0
    import re as _re
    _mt = _re.search(r'temp=([0-9.]+)', s['models'])
    if _mt: T_run = float(_mt.group(1))
    if vstep and not segments: segments = [(float(g['gate_sweep_V']['stop']), float(vstep))]
    st = g['stack_bottom_to_top']; tox_hf = st[2]['thickness_nm'] / 1000.; tox_al = st[3]['thickness_nm'] / 1000.
    tt = t / 1000.; di = g['mesh']['interface_layer_nm'] / 1000.; lc = val(g['contact_overlap_um']); L = g['channel_length_um']; xr = lc + L; xmax = xr + lc
    Cox = cox(g); qf = p['Qf_cm2']
    sweep = g['gate_sweep_V']; vg = np.round(np.arange(sweep['start'], sweep['stop'] + 1e-9, sweep['step']), 6) if targets is None else np.asarray(targets, float)
    if smoke: vg = np.array([-3., 0., 3.])
    back = p['bs_peak'] > 0 and not smoke
    ybulk = -tt + di if back else -tt
    ysp_bulk = min(g['mesh']['y_spacing_bulk_nm'] if isinstance(g['mesh']['y_spacing_bulk_nm'], (int, float)) else 1.0, t / 8) / 1000.
    ysi = g['mesh']['y_spacing_interface_nm'] / 1000.
    ys = ([(-tt, ysi), (-tt + di, ysi), (-tt + 4 * di, ysp_bulk)] if back else [(-tt, ysp_bulk)]) + [(-di, ysi), (-di / 2, ysi), (0., ysi), (tox_al, g['mesh']['y_spacing_al2o3_nm'] / 1000.), (tox_al + tox_hf, g['mesh']['y_spacing_hfo2_nm'] / 1000.)]
    t_pd = st[5]['thickness_nm'] / 1000.; t_tin = st[1]['thickness_nm'] / 1000.; ytop = -tt - t_pd; ygate = tox_al + tox_hf + t_tin
    if full: ys = [(ytop, 0.02)] + ys + [(ygate, 0.02)]
    # strict-acceptance switch voltage from the measured curve
    sa = s['strict_acceptance']; cr_strict = float(sa['cr_toler_A']); switch_v = 0.5
    if meas is not None:
        mv, mi = meas; above = mv[mi >= sa['until_measured_current_A_per_um']]; switch_v = float(above[0]) if len(above) else float('inf')
        off = float(np.median(mi[(mv >= -2) & (mv <= -.5)])); act = mi > s['scoring']['active_multiplier'] * off if t_nom < 20 else np.ones(len(mi), bool)
        if act.any(): cr_strict = max(cr_strict, float(sa['cr_tol_rel_active_min']) * float(mi[act].min()))
    base = f'method {s["method_base"]}'; strict = base + f' \\\n cr.toler={cr_strict:.3g} xandrnorm {s["carriers"]}'; relaxed = base + f' \\\n cr.toler=5e-18 ^xandrnorm {s["carriers"]}'
    P = lambda name, v, unit, label, src: f'# {name} = {v} {unit} | {label} | {src}'
    Lw = m['thickness_laws']; b = m['bulk_reference']
    ls = ['#' + '=' * 78, f'# IWO (~2 at.% W:In2O3) FET, channel t = {t} nm  --  IWO_PHYSICS_CONSTRAINED_MODEL_V1',
          '# Generated by scripts/build_iwo_decks.py from config/iwo_material_model.yaml (ONE material model for all',
          '# thicknesses). Reduced electrical deck: ideal TiN gate / Pd S/D boundaries (equipotential metals, DC).',
          '# MESH WIDTH = 1 um -> currents are A/um. Total 290-um device current = 290 x logged current. Never divide by 290.',
          f'# Cox = {Cox:.4e} F/cm^2 (HfO2 15 nm eps 19.57 + Al2O3 2 nm eps 9.0). Vd = {g["drain_bias_V"]} V, T = {p["T_K"]} K.',
          '# Category labels: A intrinsic, B confinement, D bulk defects, E interface, F transport, G contacts, H numerical.',
          '#' + '=' * 78,
          P('[A] Eg_bulk', val(b['Eg_bulk_eV']), 'eV', b['Eg_bulk_eV']['label'], b['Eg_bulk_eV']['source']),
          P('[B] dEg_QC(t)', f'{p["dEg_QC_eV"]:.4f}', 'eV', Lw['dEg_QC_eV']['label'], f'a*t^-p, a={Lw["dEg_QC_eV"]["a"]}, p={Lw["dEg_QC_eV"]["p"]} (Lin2022 slabs, Si2021)'),
          P('[A+B] EG300', f'{p["Eg_eV"]:.4f}', 'eV', 'CALCULATED', 'Eg_bulk + dEg_QC(t)'),
          P('[A] chi_bulk', val(b['chi_bulk_eV']), 'eV', b['chi_bulk_eV']['label'], b['chi_bulk_eV']['source']),
          P('[A+B] AFFINITY', f'{p["chi_eV"]:.4f}', 'eV', 'CALCULATED', 'chi_bulk - dEc(t), dEc = dEg (Ev unchanged, Si2021)'),
          P('[A+B] m*', f'{p["mstar_m0"]:.4f}', 'm0', Lw['mstar_m0']['label'], 'Stokey2021 bulk 0.208 + Lin2022 PBE increment'),
          P('[A+B] NC300', f'{p["Nc_cm3"]:.4e}', 'cm^-3', 'CALCULATED', '2(2 pi m* kT/h^2)^1.5; effective continuum DOS at 2 nm'),
          P('[A] NV300', f'{p["Nv_cm3"]:.3e}', 'cm^-3', b['Nv300_cm3']['label'], 'holes not solved'),
          P('[A] PERMITTIVITY', p['eps_iwo'], '-', b['eps_r']['label'], b['eps_r']['source']),
          P('[D] Nt(t)', f'{p["Nt_cm3"]:.4e}', 'cm^-3', Lw['Nt_cm3']['label'], f'Nt2*(2/t)^alpha, Nt2={Lw["Nt_cm3"]["Nt2"]}, alpha={Lw["Nt_cm3"]["alpha"]}'),
          P('[D] NTA = Nt/WTA', f'{p["NTA_cm3_eV"]:.4e}', 'cm^-3/eV', 'CALCULATED', 'gTA(E)=NTA exp((E-Ec)/WTA); integral = NTA*WTA*(1-exp(-Eg/WTA))'),
          P('[D] WTA (kTt)', p['WTA_eV'], 'eV', Lw['WTA_eV']['label'], f'Tt = {p["WTA_eV"] / KB:.0f} K; shared across thickness'),
          P('[D] deep acceptor Gaussian', f'{p["NGA"]:.3g} at Ec-{p["EGA"]} eV, W={p["WGA"]}', 'cm^-3/eV', m['traps']['bulk_deep_acceptor_gaussian']['label'], ''),
          P('[D] Nd_eff(t)', f'{p["Nd_cm3"]:.4e}', 'cm^-3', Lw['Nd_eff_cm3']['label'], f'Nd0*(1+(t/tc)^k), Nd0={Lw["Nd_eff_cm3"]["Nd0"]}, tc={Lw["Nd_eff_cm3"]["tc_nm"]} nm, k={Lw["Nd_eff_cm3"]["k"]}; NOT W concentration'),
          P('[E] interface acceptor sheet', f'{p["it_peak"]:.3g} at Ec-{p["it_e"]} eV, W={p["it_w"]} eV', 'cm^-2/eV', m['traps']['interface_acceptor_sheet']['label'], m['traps']['interface_acceptor_sheet']['implementation']),
          P('[E] Qf', f'{qf:.4e}', 'cm^-2', m['traps']['fixed_interface_charge_Qf_cm2']['label'], f'dVfb = -q Qf/Cox = {-Q * qf / Cox:+.4f} V'),
          P('[F] mu_band(t)', p['mu_band'], 'cm^2/Vs', 'FITTED per thickness', Lw['mu0_cm2Vs']['label']),
          P('[F] roughness factor', f'{p["rough"]:.4f}', '-', Lw['mu0_cm2Vs']['Dsr_label'], f'(1 - Dsr/t)^2, Dsr = {Lw["mu0_cm2Vs"]["Dsr_nm"]} nm'),
          P('[F] MUN = mu_band*(1-Dsr/t)^2', f'{p["mu0"]:.4f}', 'cm^2/Vs', 'CALCULATED', Lw['mu0_cm2Vs']['gate_dependence']),
          P('[G] gate work function', p['gate_wf'], 'eV', m['contacts']['gate_workfunction_eV']['label'], ''),
          P('[G] S/D', m['contacts']['source_drain']['model'] + (f'; series R {p["rs_ohm_um"]:.3g} ohm.um total' if p['rs_ohm_um'] > 0 else ''), '', m['contacts']['source_drain']['label'], ''),
          P('[H] capture cross sections', p['sig'], 'cm^2', m['traps']['bulk_acceptor_tail']['capture_label'], 'not identifiable from DC transfer curves'),
          '#' + '=' * 78, 'go atlas', f'mesh width={float(g["simulated_width_um"])}']
    mf = float(g['mesh'].get('spacing_factor', 1.0))   # < 1 refines every spacing (numerical convergence checks only)
    if mf != 1.0: ls.append(f'# NUMERICAL CHECK: all mesh spacings multiplied by {mf:g}')
    xm = g['mesh']['x_um']
    if abs(lc - 2.0) > 1e-9:   # 2026-09-27: mesh follows the contacts when the overlap differs from the 2 um default (run_0027 had a fixed 24 um mesh)
        xm = [(0, 0.3), (lc - 0.2, 0.05), (lc, 0.01), (lc + 0.2, 0.05), (lc + 1, 0.2), (lc + L / 2, 0.7), (xr - 1, 0.2), (xr - 0.2, 0.05), (xr, 0.01), (xr + 0.2, 0.05), (xmax, 0.3)]
    for x, sp in xm: ls.append(f'x.mesh loc={x:.10g} spac={sp * mf:.10g}')
    for y, sp in ys: ls.append(f'y.mesh loc={y:.10g} spac={sp * mf:.10g}')
    ls += [f'region num=1 user.material=IWO x.min=0 x.max={xmax:.9g} y.min={ybulk:.10g} y.max={-di:.10g}',
           f'region num=2 user.material=IWO x.min=0 x.max={xmax:.9g} y.min={-di:.10g} y.max=0']
    if back: ls.append(f'region num=5 user.material=IWO x.min=0 x.max={xmax:.9g} y.min={-tt:.10g} y.max={ybulk:.10g}')
    if full:
        ls += ['# Physical stack of the measured device (bottom gate): TiN 50 nm / HfO2 15 nm / Al2O3 2 nm / IWO / Pd 70 nm S/D, air above the channel.',
               '# TiN is not in the ATLAS metal table: the gate is a Conductor volume whose work function is set on CONTACT (4.70 eV, ASSUMED).',
               f'region num=3 material=Al2O3 x.min=0 x.max={xmax:.9g} y.min=0 y.max={tox_al:.10g}',
               f'region num=4 material=HfO2 x.min=0 x.max={xmax:.9g} y.min={tox_al:.10g} y.max={tox_al + tox_hf:.10g}',
               f'region num=6 material=Conductor x.min=0 x.max={xmax:.9g} y.min={tox_al + tox_hf:.10g} y.max={ygate:.10g}',
               f'region num=7 material=Air x.min=0 x.max={xmax:.9g} y.min={ytop:.10g} y.max={-tt:.10g}',
               f'electrode name=gate x.min=0 x.max={xmax:.9g} y.min={tox_al + tox_hf:.10g} y.max={ygate:.10g}',
               '# Pd S/D volumes on the IWO top surface. No CONTACT work function is set for them -> Ohmic boundary (ASSUMED, no TLM data);',
               '# the 2 nm run of this structure is compared with the reduced-boundary deck (run_0008) to verify electrical equivalence.',
               f'electrode name=source material=Palladium x.min=0 x.max={lc:.9g} y.min={ytop:.10g} y.max={-tt:.10g}',
               f'electrode name=drain material=Palladium x.min={xr:.9g} x.max={xmax:.9g} y.min={ytop:.10g} y.max={-tt:.10g}']
    else:
        ls += [f'region num=3 material=oxide x.min=0 x.max={xmax:.9g} y.min=0 y.max={tox_al:.10g}',
               f'region num=4 material=oxide x.min=0 x.max={xmax:.9g} y.min={tox_al:.10g} y.max={tox_al + tox_hf:.10g}']
        ls += [f'electrode name=source x.min=0 x.max={lc:.9g} y.min={-tt:.10g} y.max={-tt:.10g}',
               f'electrode name=drain x.min={xr:.9g} x.max={xmax:.9g} y.min={-tt:.10g} y.max={-tt:.10g}',
               f'electrode name=gate x.min=0 x.max={xmax:.9g} y.min={tox_al + tox_hf:.10g} y.max={tox_al + tox_hf:.10g}']
    for r in ([1, 2, 5] if back else [1, 2]): ls.append(f'doping uniform n.type conc={p["Nd_cm3"]:.6g} region={r}')
    ls += ['# USER.DEFAULT=silicon is only the parser template; every relevant parameter is overridden above.',
           'material material=IWO user.group=semiconductor user.default=silicon \\',
           f' eg300={p["Eg_eV"]:.6g} affinity={p["chi_eV"]:.6g} permittivity={p["eps_iwo"]:.6g} \\',
           f' nc300={p["Nc_cm3"]:.6g} nv300={p["Nv_cm3"]:.6g} \\', f' mun={p["mu0"]:.6g} mup={p["mup"]:.6g} \\', f' taun0={p["tau_s"]:.3g} taup0={p["tau_s"]:.3g}' + (' egalpha=0' if abs(T_run - 300) > 1e-6 else '') + (f' tmun={float(s["tmun"]):g}' if s.get('tmun') is not None else ''),
           f'# Region 3 = Al2O3 (2 nm), eps {st[3]["eps_r"]} ({st[3]["eps_label"]}); region 4 = HfO2 (15 nm), eps {st[2]["eps_r"]} ({st[2]["eps_label"]}).',
           '# Set explicitly for the named materials too: ATLAS built-in permittivity defaults are NOT the measured values.',
           f'material region=3 permittivity={st[3]["eps_r"]}', f'material region=4 permittivity={st[2]["eps_r"]}',
           f'contact name=gate workfunction={p["gate_wf"]:.6g}']
    if p['rs_ohm_um'] > 0: ls += ['# CONTACT RESISTANCE is in ohm.um for 2-D (installed manual); half of the total per contact.', f'contact name=source resistance={p["rs_ohm_um"] / 2:.6g}', f'contact name=drain resistance={p["rs_ohm_um"] / 2:.6g}']
    ls.append(f'models {s["models"]}')
    if not smoke:
        ls += defects_block(p, 1, g['mesh']['interface_layer_nm'], False) + defects_block(p, 2, g['mesh']['interface_layer_nm'], True)
        if back: ls += defects_block(p, 5, g['mesh']['interface_layer_nm'], False, back=True)
    else: ls.append('# SMOKE: DOS disabled (trap-free diagnostic, not a fit).')
    xc = (lc + xr) / 2; yc = -tt / 2
    ls += [f'interface qf={qf:.6g} x.min=0 x.max={xmax:.9g} y.min=-0.0000001 y.max=0.0000001']
    if p['Qb_cm2'] != 0:
        # HYPOTHESIS (2026-09-25): fixed sheet charge at the free IWO/Air surface of the EXPOSED channel only (between the
        # S/D contacts; the surface under the Pd volumes is metal-covered). Same INTERFACE QF mechanism as the front Qf.
        ls += [f'# [E] HYPOTHESIS back-surface fixed charge Qb = {p["Qb_cm2"]:.4e} cm^-2 at the IWO/Air surface (x = {lc:g}..{xr:g} um)',
               f'interface qf={p["Qb_cm2"]:.6g} x.min={lc:.9g} x.max={xr:.9g} y.min={-tt - 1e-7:.10g} y.max={-tt + 1e-7:.10g}']
    ls += [f'# Strict acceptance (XANDRNORM, cr.toler {cr_strict:.3g}) up to Vg = {switch_v:.10g} V; default acceptance above.', strict,
           f'output {s["output"]}',
           '# Interior probes (channel centre) for mobility / free-electron exports vs Vg (native solver quantities).',
           f'probe name=chan_mob x={xc:.6g} y={yc:.6g} n.mob dir=0', f'probe name=chan_n x={xc:.6g} y={yc:.6g} n.conc',
           f'probe name=avg_n region=1 average n.conc x.min={lc:.6g} x.max={xr:.6g} y.min={ybulk:.10g} y.max={-di:.10g}',
           'solve init', 'save outf=equilibrium.str']
    if output_vgs:
        # PREDICTION MODE: output characteristics at fixed gate voltages (no measured counterpart exists yet).
        vgs = [float(v) for v in output_vgs]; vds = [(float(e), float(st_)) for e, st_ in (vd_segments or [(3.0, 0.1)])]
        tags = [('vg' + f'{v:g}').replace('.', 'p').replace('-', 'm') for v in vgs]
        ls += ['# PREDICTION (recorded before any ID-VD measurement): ID-VD families, default acceptance (on-state currents).', relaxed]
        cur = 0.0
        for v, tag in zip(vgs, tags):
            if abs(v - cur) > 1e-9: ls.append(f'solve vstep={0.1 if v > cur else -0.1:g} vfinal={v:.10g} name=gate'); cur = v
            ls += [f'log outf=idvd_{tag}.log', 'solve vdrain=0']
            ls += [f'solve vstep={st_:g} vfinal={e:.10g} name=drain' for e, st_ in vds]
            ls += ['log off', f'solve vstep=-0.25 vfinal=0 name=drain']
        ls.append('save outf=final_output.str')
        for tag in tags:
            ls += [f'extract init infile="idvd_{tag}.log"',
                   f'extract name="IdVd_{tag}" curve(v."drain",i."drain") outfile="idvd_{tag}.dat"',
                   f'extract name="IsVd_{tag}" curve(v."drain",i."source") outfile="isvd_{tag}.dat"',
                   f'extract name="IgVd_{tag}" curve(v."drain",i."gate") outfile="igvd_{tag}.dat"']
        ls += ['quit', '']
        text = '\n'.join(ls).replace('{NUMA}', str(int(s['dos_levels']['numa']))).replace('{NUMD}', str(int(s['dos_levels']['numd'])))
        meta = {'thickness_nm': t, 'key': key, 'mode': 'output_prediction', 'output_vgs': vgs, 'output_tags': tags, 'vd_segments': vds,
                'material': {k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in p.items()}, 'Cox_F_cm2': Cox,
                'dVfb_from_Qf_V': -Q * qf / Cox, 'full_structure': full, 'status': 'DECK_GENERATED_NOT_SIMULATED'}
        return text, meta
    step = s['continuation_gate_step_V']
    if segments:
        ls.append('# Bias ramp to the sweep start with stepped SOLVE blocks (no per-point statements).')
        if vg[0] != 0: ls.append(f'solve vstep={-step if vg[0] < 0 else step:g} vfinal={vg[0]:.10g} name=gate')
        ls.append(f'solve vstep=0.1 vfinal={g["drain_bias_V"]:.10g} name=drain')
    else:
        if vg[0] != 0:
            n = int(math.ceil(abs(vg[0]) / step))
            for v in np.linspace(0, vg[0], n + 1)[1:]: ls.append(f'solve vgate={v:.10g}')
        for v in np.linspace(0, g['drain_bias_V'], int(math.ceil(g['drain_bias_V'] / .1)) + 1)[1:]: ls.append(f'solve vdrain={v:.10g}')
    ls.append('log outf=transfer.log'); prev = float(vg[0]); relaxed_done = False; vth_saved = False
    vth_target = None
    if meas is not None:
        mv, mi = meas
        for i in range(len(mv) - 1):
            if mi[i] > 0 and mi[i + 1] > 0 and (mi[i] - 1e-9) * (mi[i + 1] - 1e-9) <= 0: vth_target = float(round(mv[i + 1], 6)); break
    if segments:
        # ATLAS stepped sweep: SOLVE [VGATE=<start>] VSTEP=<step> VFINAL=<end> NAME=gate (every step is logged).
        # Blocks follow the requested segments and are split at the strict->default METHOD switch and at the
        # measured Vth (near_vth.str save). Breakpoints inside a segment use that segment's step.
        segs = [(float(e), float(st_)) for e, st_ in segments]
        ls.append('# Stepped sweep (end V, step V): ' + ', '.join(f'({e:g}, {st_:g})' for e, st_ in segs) + ' - scored at the solved points only.')
        extra = {float(round(switch_v, 6))} if math.isfinite(switch_v) else set()
        if vth_target is not None: extra.add(float(vth_target))
        bps = sorted({e for e, _ in segs} | {b for b in extra if vg[0] < b <= vg[-1]})
        a = float(vg[0]); first = True
        for b in bps:
            if b < a - 1e-9: continue
            stp = next(st_ for e, st_ in segs if b <= e + 1e-9)
            if b > a + 1e-9 or first:
                ls.append((f'solve vgate={a:.10g} ' if first else 'solve ') + f'vstep={stp:g} vfinal={b:.10g} name=gate'); first = False
            if vth_target is not None and not vth_saved and b >= vth_target - 1e-9: ls.append('save outf=near_vth.str'); vth_saved = True
            if not relaxed_done and b >= switch_v - 1e-9: ls += ['# On-state: default convergence acceptance.', relaxed]; relaxed_done = True
            a = b
        prev = float(vg[-1])
    else:
      for j, v in enumerate(vg):
        n = max(1, int(math.ceil(abs(v - prev) / step))); vv = np.linspace(prev, v, n + 1)[1:] if j else np.array([v])
        for z in vv:
            if not relaxed_done and z >= switch_v - 1e-9: ls += ['# On-state: default convergence acceptance.', relaxed]; relaxed_done = True
            ls.append(f'solve vgate={z:.10g}')
            if vth_target is not None and not vth_saved and z >= vth_target - 1e-9: ls.append('save outf=near_vth.str'); vth_saved = True
        prev = float(v)
    ls += ['log off', 'save outf=final.str', 'output con.band val.band qfn e.mobility', 'extract init infile="transfer.log"',
           'extract name="IdVg" curve(v."gate",i."drain") outfile="idvg.dat"', 'extract name="IgVg" curve(v."gate",i."gate") outfile="igvg.dat"',
           'extract name="IsVg" curve(v."gate",i."source") outfile="isvg.dat"',
           'extract name="mob_vg" curve(v."gate",probe."chan_mob") outfile="chan_mobility_vg.dat"',
           'extract name="n_vg" curve(v."gate",probe."chan_n") outfile="chan_electrons_vg.dat"',
           'extract name="navg_vg" curve(v."gate",probe."avg_n") outfile="avg_electrons_vg.dat"']
    for tag, fn in [('eq', 'equilibrium.str'), ('vth', 'near_vth.str'), ('on', 'final.str')]:
        if tag == 'vth' and vth_target is None: continue
        ls += [f'extract init infile="{fn}"',
               f'extract name="cb_{tag}" curve(depth, impurity="Conduction Band Energy" material="All" mat.occno=1 x.val={xc:.6g}) outfile="cb_{tag}.dat"',
               f'extract name="vb_{tag}" curve(depth, impurity="Valence Band Energy" material="All" mat.occno=1 x.val={xc:.6g}) outfile="vb_{tag}.dat"',
               f'extract name="n_{tag}" curve(depth, impurity="Electron Conc" material="All" mat.occno=1 x.val={xc:.6g}) outfile="n_{tag}.dat"',
               f'extract name="qfn_{tag}" curve(depth, impurity="Electron QFL" material="All" mat.occno=1 x.val={xc:.6g}) outfile="qfn_{tag}.dat"']
    ls += ['quit', '']
    text = '\n'.join(ls).replace('{NUMA}', str(int(s['dos_levels']['numa']))).replace('{NUMD}', str(int(s['dos_levels']['numd'])))
    meta = {'thickness_nm': t, 'key': key, 'material': {k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in p.items()}, 'Cox_F_cm2': Cox, 'dVfb_from_Qf_V': -Q * qf / Cox,
            'requested_points': int(len(vg)), 'strict_cr_toler_A': cr_strict, 'strict_up_to_V': switch_v, 'smoke': smoke, 'full_structure': full, 'status': 'DECK_GENERATED_NOT_SIMULATED'}
    return text, meta

def read_meas(t):
    import csv
    rows = [r for r in csv.DictReader((ROOT / 'data' / 'experimental_clean.csv').open()) if abs(float(r['thickness_nm']) - t) < 1e-6]
    return np.array([float(r['vg_V']) for r in rows]), np.array([float(r['id_A_per_um']) for r in rows])

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--thickness', type=float, nargs='*', default=[2.0, 6.3, 13.2, 31.8]); ap.add_argument('--out', type=Path, default=ROOT / 'decks')
    ap.add_argument('--override', action='append', default=[], help='dotted path=value into iwo_material_model, e.g. traps.fixed_interface_charge_Qf_cm2.value=-2e11')
    ap.add_argument('--sweep', choices=['config', 'stepped', 'pointwise'], default='config', help='stepped = SOLVE VSTEP/VFINAL blocks (solver.yaml sweep.segments; final form); pointwise = one SOLVE per 0.05 V point (runs 0001-0009)')
    ap.add_argument('--structure', choices=['config', 'full', 'reduced'], default='config', help='full = physical Air/Pd/Al2O3/HfO2/Conductor volumes (final form); reduced = ideal boundaries (runs 0001-0009)')
    ap.add_argument('--smoke', action='store_true'); ap.add_argument('--full', action='store_true', help='alias of --structure full'); a = ap.parse_args()
    m, g, s = load_configs()
    for o in a.override:
        k, v = o.split('=', 1)
        if k.startswith('solver.'): set_dotted(s, k[7:], v)
        elif k.startswith('geometry.'): set_dotted(g, k[9:], v)
        else: set_dotted(m, k, v)
    full = a.full or (a.structure == 'full') or (a.structure == 'config' and str(g.get('structure', 'reduced')).lower() == 'full')
    stepped = (a.sweep == 'stepped') or (a.sweep == 'config' and str(s.get('sweep', {}).get('mode', 'pointwise')) == 'stepped')
    segs = [tuple(x) for x in s['sweep']['segments']] if stepped else None
    a.out.mkdir(parents=True, exist_ok=True)
    for t in a.thickness:
        text, meta = build_deck(t, m, g, s, meas=read_meas(t), smoke=a.smoke, full=full, segments=segs)
        name = f'iwo_{KEYS[t]}nm' + ('_smoke' if a.smoke else '') + ('' if full else '_reduced') + ('' if stepped else '_pointwise')
        (a.out / f'{name}.in').write_text(text, encoding='ascii'); (a.out / f'{name}_metadata.json').write_text(json.dumps(meta, indent=2)); print(a.out / f'{name}.in')
    if not a.smoke:
        tmpl, _ = build_deck(2.0, m, g, s, meas=read_meas(2.0), full=full, segments=segs); (a.out / 'master_template.in').write_text('# MASTER TEMPLATE = the 2.0 nm deck as generated (physical structure, stepped sweep); all decks come from the same generator/material model.\n' + tmpl, encoding='ascii')

if __name__ == '__main__': main()
