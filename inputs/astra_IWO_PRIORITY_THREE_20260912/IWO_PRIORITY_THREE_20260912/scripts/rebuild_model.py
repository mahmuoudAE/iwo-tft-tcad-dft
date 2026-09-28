"""Independent, explicit ATLAS IWO generator for controlled model discrimination.

Only measurement voltages are read. No analytical or measured current is used
to generate the device. All lengths in commands are micrometres.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def positive(value, name):
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be finite and positive')


def render(cfg, key='2p0', plots=False):
    g, s, n, c = cfg['geometry'], cfg['shared'], cfg['numerics'], cfg['curves'][key]
    richardson_text = ''
    if 'electron_richardson_A_cm2_K2' in s:
        richardson = s['electron_richardson_A_cm2_K2']
        positive(richardson, 'electron_richardson_A_cm2_K2')
        richardson_text = f' arichn={richardson:.12g}'
    for name in ('temperature_K', 'vd_V', 'eps_iwo', 'eps_hfo2', 'eps_al2o3',
                 'eg_eV', 'nc300_cm3', 'nv300_cm3', 'hole_mu_cm2Vs', 'taun_s', 'taup_s'):
        positive(s[name], name)
    if not math.isfinite(c['gate_shift_V']):
        raise ValueError('gate_shift_V must be finite')
    positive(cfg['defects']['capture_cm2'], 'capture_cm2')
    for family in ('bulk', 'interface'):
        if not isinstance(cfg['defects'][family], bool):
            raise ValueError('DOS enable flags must be boolean')
        for carrier in ('a', 'd'):
            name = f'{family}_levels_{carrier}'
            count = cfg['defects'][name]
            if isinstance(count, bool) or not isinstance(count, int) or count < 2:
                raise ValueError(name + ' must be an integer >=2')
    for name in ('channel_length_um', 'contact_length_um', 'simulation_width_um', 'al2o3_nm', 'hfo2_nm',
                 'gate_metal_nm', 'source_drain_metal_nm'):
        positive(g[name], name)
    for name in ('x_spacing_um', 'contact_edge_spacing_um', 'gate_step_V', 'current_tolerance_A'):
        positive(n[name], name)
    for name in ('channel_intervals', 'alumina_intervals', 'hafnia_intervals'):
        if isinstance(n[name], bool) or not isinstance(n[name], int) or n[name] < 2:
            raise ValueError(name + ' must be an integer >= 2')
    for name in ('thickness_nm', 'mu_band_cm2Vs', 'wta_eV', 'wga_eV', 'wgd_eV', 'interface_width_eV'):
        positive(c[name], name)
    for name in ('nd_cm3', 'nta_cm3_eV', 'nga_cm3_eV', 'ngd_cm3_eV', 'interface_peak_cm2_eV'):
        if not math.isfinite(c[name]) or c[name] < 0:
            raise ValueError(name + ' must be finite and nonnegative')
    for name in ('ega_eV_below_Ec', 'egd_eV_below_Ec', 'interface_center_eV_below_Ec'):
        if not 0 <= c[name] <= s['eg_eV']:
            raise ValueError(name + ' must lie in the bandgap')

    t = c['thickness_nm'] / 1000
    al = g['al2o3_nm'] / 1000
    ox = al + g['hfo2_nm'] / 1000
    bottom = ox + g['gate_metal_nm'] / 1000
    top = -t - g['source_drain_metal_nm'] / 1000
    source_end = g['contact_length_um']
    drain_start = source_end + g['channel_length_um']
    xmax = drain_start + source_end
    mid = (source_end + drain_start) / 2
    spacing, edge = n['x_spacing_um'], n['contact_edge_spacing_um']
    # Uniform interior with locally resolved metal-edge fringing fields.
    xm = [(0, spacing), (source_end-.2, min(.1, spacing)), (source_end, edge),
          (source_end+.2, min(.1, spacing)), (mid, spacing),
          (drain_start-.2, min(.1, spacing)), (drain_start, edge),
          (drain_start+.2, min(.1, spacing)), (xmax, spacing)]
    ym = [(top, .015), (-t-.02, .005), (-t-.002, .001)]
    channel_mesh = np.linspace(-t, 0, n['channel_intervals']+1)
    for index, y in enumerate(channel_mesh):
        step = t/n['channel_intervals']
        if n.get('graded_channel_mesh') and index in (0, len(channel_mesh)-1):
            # Resolve accumulation/contact boundaries in thick films without
            # imposing subnanometre cells throughout their neutral interior.
            step = min(step, .002/n['channel_intervals'])
        ym.append((float(y), step))
    ym += [(float(y), al/n['alumina_intervals']) for y in np.linspace(0, al, n['alumina_intervals']+1)[1:]]
    ym += [(float(y), (ox-al)/n['hafnia_intervals']) for y in np.linspace(al, ox, n['hafnia_intervals']+1)[1:]]
    ym += [(bottom, .01)]
    bias = np.genfromtxt(ROOT / c['data'], delimiter=',', names=True)['vg_V']
    if len(bias) != 121 or not np.allclose(bias, np.linspace(-3, 3, 121), atol=1e-9, rtol=0):
        raise ValueError('Measurement gate grid must retain all 121 original targets')
    precision = n.get('precision_bits', 64)
    if precision not in (64, 80, 128):
        raise ValueError('Unsupported arithmetic mode')
    lines = ['go atlas' + (f' simflags="-{precision}"' if precision != 64 else ''),
             f'title IWO {c["thickness_nm"]:g} nm - independent rebuild - uncalibrated',
             '# Units: um. Geometry fixed by the target; electronic parameters are hypotheses.',
             '# n+Si support is screened by ideal TiN and excluded from this electrical domain.',
             '# Physical stack: n+Si / TiN50 / HfO2 15 / Al2O3 2 / IWO / Pd70 nm.',
             '# Air above the exposed channel; no artificial SiO2 overlayer.',
             '# Width-one currents are A/um. Physical device total current is 290 times that.',
             '', '# 1. Direct rectangular mesh; no imported process mesh.',
             f'mesh width={g["simulation_width_um"]:.9g}']
    lines += [f'x.mesh loc={x:.12g} spac={h:.12g}' for x, h in xm]
    lines += [f'y.mesh loc={y:.12g} spac={h:.12g}' for y, h in ym]
    lines += ['', '# 2. Active stack and physical metal volumes.',
              f'region num=1 material=Air y.min={top:.12g} y.max={-t:.12g}',
              f'region num=2 user.material=IWO y.min={-t:.12g} y.max=0',
              f'region num=3 material=Al2O3 y.min=0 y.max={al:.12g}',
              f'region num=4 material=HfO2 y.min={al:.12g} y.max={ox:.12g}',
              f'region num=5 material=Conductor y.min={ox:.12g} y.max={bottom:.12g}',
              f'electrode num=1 name=gate material=Conductor x.min=0 x.max={xmax:.12g} y.min={ox:.12g} y.max={bottom:.12g}',
              f'electrode num=2 name=source material=Palladium x.min=0 x.max={source_end:.12g} y.min={top:.12g} y.max={-t:.12g}',
              f'electrode num=3 name=drain material=Palladium x.min={drain_start:.12g} x.max={xmax:.12g} y.min={top:.12g} y.max={-t:.12g}',
              '', '# 3. Custom IWO; unlisted inherited constants remain a limitation.',
              'material material=IWO user.group=semiconductor user.default=silicon \\',
              f' eg300={s["eg_eV"]:.9g} affinity={s["affinity_eV"]:.9g} permittivity={s["eps_iwo"]:.9g} \\',
              f' nc300={s["nc300_cm3"]:.9g} nv300={s["nv300_cm3"]:.9g} \\',
              f' mun={c["mu_band_cm2Vs"]:.9g} mup={s["hole_mu_cm2Vs"]:.9g} \\',
              f' taun0={s["taun_s"]:.9g} taup0={s["taup_s"]:.9g}' + richardson_text,
              f'material material=Al2O3 permittivity={s["eps_al2o3"]:.9g}',
              f'material material=HfO2 permittivity={s["eps_hfo2"]:.9g}',
              'material material=Air permittivity=1',
              f'doping uniform n.type conc={c["nd_cm3"]:.9g} region=2',
              '', '# 4. Native electrical boundary conditions.',
              f'contact name=gate workfunction={s["gate_workfunction_eV"]+c["gate_shift_V"]:.9g}']
    contact = cfg['contacts']
    resistance = contact.get('resistance_ohm_um', 0)
    if not math.isfinite(resistance) or resistance < 0:
        raise ValueError('Contact resistance must be finite and nonnegative')
    resistance_text = f' resistance={resistance:.9g}' if resistance else ''
    if contact['mode'] == 'schottky':
        barrier = contact['electron_barrier_eV']
        if not 0 < barrier < s['eg_eV']:
            raise ValueError('Effective contact barrier must lie in the gap')
        for name in ('source', 'drain'):
            lines += [f'contact name={name} workfunction={s["affinity_eV"]+barrier:.9g} surf.rec' + resistance_text]
    elif contact['mode'] != 'ohmic':
        raise ValueError('Unknown contact model')
    elif resistance:
        lines += [f'contact name={name}' + resistance_text for name in ('source', 'drain')]
    transverse = ' prpmob' if cfg['transport']['mode'] == 'prpmob' else ''
    lines += [f'models srh fermi temp={s["temperature_K"]:.9g}' + transverse + ' print']
    d = cfg['defects']
    sig = d['capture_cm2']
    if d['bulk']:
        lines += ['', '# 5. Native bulk DOS: peak cm^-3/eV; donor center referenced to Ev.',
                  f'defects region=2 continuous numa={d["bulk_levels_a"]} numd={d["bulk_levels_d"]} \\',
                  f' nta={c["nta_cm3_eV"]:.9g} wta={c["wta_eV"]:.9g} ntd=0 wtd=0.1 \\',
                  f' nga={c["nga_cm3_eV"]:.9g} ega={c["ega_eV_below_Ec"]:.9g} wga={c["wga_eV"]:.9g} \\',
                  f' ngd={c["ngd_cm3_eV"]:.9g} egd={s["eg_eV"]-c["egd_eV_below_Ec"]:.9g} wgd={c["wgd_eV"]:.9g} \\',
                  f' sigtae={sig:.9g} sigtah={sig:.9g} sigtde={sig:.9g} sigtdh={sig:.9g} \\',
                  f' siggae={sig:.9g} siggah={sig:.9g} siggde={sig:.9g} siggdh={sig:.9g} \\',
                  ' afile=bulk_acceptor.dat dfile=bulk_donor.dat']
    if d['interface']:
        lines += ['', '# 6. Native front-interface acceptors; peak cm^-2/eV, not a volume.',
                  'intdefects continuous s.i intnumber="2/3" max.gaussian \\',
                  f' nta=0 ntd=0 nga={c["interface_peak_cm2_eV"]:.9g} ega={c["interface_center_eV_below_Ec"]:.9g} wga={c["interface_width_eV"]:.9g} \\',
                  f' ngd=0 egd=0.4 wgd=0.1 numa={d["interface_levels_a"]} numd={d["interface_levels_d"]} \\',
                  f' siggae={sig:.9g} siggah={sig:.9g} siggde={sig:.9g} siggdh={sig:.9g} \\',
                  f' x.min=0 x.max={xmax:.9g} y.min=-1e-6 y.max=1e-6 \\',
                  ' afile=interface_acceptor.dat dfile=interface_donor.dat tfile=interface_dos.dat']
    mobility = cfg['transport']
    colocated_prp = cfg.get('diagnostics', {}).get('colocate_prp_probes', False)
    if not isinstance(colocated_prp, bool):
        raise ValueError('diagnostics.colocate_prp_probes must be boolean')
    if colocated_prp and (mobility['mode'] != 'prpmob' or
                           cfg.get('diagnostics', {}).get('depth_electrons') is not True):
        raise ValueError('Colocated PRPMOB probes require prpmob and depth_electrons=true')
    if mobility['mode'] == 'tokyo':
        positive(mobility['ncrit_cm3'], 'ncrit_cm3')
        gamma = mobility['gamma0'] + mobility['tgamma_K']/s['temperature_K']
        if not math.isfinite(gamma) or gamma < 0:
            raise ValueError('Tokyo density exponent must be finite and nonnegative in this model')
        lines += [f'mobility region=2 igzo.tokyo mun={c["mu_band_cm2Vs"]:.9g} tmun=1.5 '
                  f'igzo.gamma0={mobility["gamma0"]:.9g} igzo.tgamma={mobility["tgamma_K"]:.9g} '
                  f'igzo.ncrit={mobility["ncrit_cm3"]:.9g} print']
    elif mobility['mode'] == 'prpmob':
        positive(mobility['critical_field_V_cm'], 'critical_field_V_cm')
        lines += [f'mobility region=2 mun={c["mu_band_cm2Vs"]:.9g} mup={s["hole_mu_cm2Vs"]:.9g} '
                  f'tmun=0 tmup=0 gsurfn=1 ecn.mu={mobility["critical_field_V_cm"]:.9g} '
                  'gsurfp=1 ecp.mu=1e30 print']
    elif mobility['mode'] != 'constant':
        raise ValueError('Unknown transport model')
    carrier = n['carrier_equations']
    if carrier not in ('electrons', 'both'):
        raise ValueError('Unknown carrier equation set')
    method = 'method newton' + (' carriers=1 electrons' if carrier == 'electrons' else '')
    lines += ['', '# 7. Numerical controls and independent interior-point diagnostics.',
              method + f' trap maxtrap={n["maxtrap"]} itlimit={n["itlimit"]} climit=1e-6 '
              f'cr.toler={n["current_tolerance_A"]:.9g} ir.tol={n["current_tolerance_A"]:.9g} cx.toler=1e-6',
              'output con.band val.band e.mobility' + (' traps traps.ft int.charge charge' if cfg.get('diagnostics', {}).get('trap_charge') else ''),
              f'probe name=channel_mobility x={mid+.037:.9g} y={-t*.47:.12g} n.mob dir=0',
              f'probe name=channel_electrons x={mid+.037:.9g} y={-t*.47:.12g} n.conc']
    extra_probes = []
    if mobility['mode'] == 'prpmob':
        # Optional new diagnostic layout; default preserves every earlier deck.
        # Align mobility/field with the already defined surface-density probes.
        front_fraction = min(.001, .13*t)/t if colocated_prp else .13
        back_fraction = 1-front_fraction if colocated_prp else .83
        extra_probes = [('channel_ey', .47, 'field dir=90'),
                        ('front_mobility', front_fraction, 'n.mob dir=0'), ('front_ey', front_fraction, 'field dir=90'),
                        ('back_mobility', back_fraction, 'n.mob dir=0'), ('back_ey', back_fraction, 'field dir=90')]
        lines += [f'probe name={name} x={mid+.037:.9g} y={-t*depth:.12g} {quantity}'
                  for name, depth, quantity in extra_probes]
    if cfg.get('diagnostics', {}).get('trap_charge'):
        for name, quantity in [('bulk_free_electrons', 'n.conc'),
                               ('bulk_ionized_acceptors', 'concacc.ctrap'),
                               ('bulk_ionized_donors', 'concdon.ctrap')]:
            lines += [f'probe name={name} region=2 average {quantity} '
                      f'x.min={source_end:.9g} x.max={drain_start:.9g} y.min={-t:.12g} y.max=0']
            extra_probes.append((name, None, quantity))
    depth_electrons = cfg.get('diagnostics', {}).get('depth_electrons', False)
    if not isinstance(depth_electrons, bool):
        raise ValueError('diagnostics.depth_electrons must be boolean')
    if depth_electrons:
        edge_distance = min(.001, .13*t)
        for name, y in [('bulk_front_electrons', -edge_distance),
                        ('bulk_back_electrons', -t+edge_distance)]:
            lines += [f'probe name={name} x={mid+.037:.9g} y={y:.12g} n.conc']
            extra_probes.append((name, None, 'n.conc'))
    lines += ['save outf=geometry.str', 'solve init', 'save outf=equilibrium.str', 'solve vsource=0']
    steps = math.ceil(abs(bias[0]) / n['gate_step_V'])
    lines += [f'solve vgate={v:.10g}' for v in np.linspace(0, bias[0], steps+1)[1:]]
    lines += [f'solve vdrain={v:.10g}' for v in np.linspace(0, s['vd_V'], math.ceil(s['vd_V']/.1)+1)[1:]]
    lines += ['save outf=off.str', '', '# 8. Every original gate point; fresh signed terminal exports.', 'log outf=transfer.log']
    lines += [f'solve vgate={v:.10g}' for v in bias]
    lines += ['log off', 'save outf=final.str', 'extract init infile="transfer.log"']
    for name, terminal in [('idvg', 'drain'), ('isvg', 'source'), ('igvg', 'gate')]:
        lines += [f'extract name="{name}" curve(v."gate",i."{terminal}") outfile="{name}.dat"']
    for name, terminal in [('vdvg', 'drain'), ('vsvg', 'source')]:
        lines += [f'extract name="{name}" curve(v."gate",v."{terminal}") outfile="{name}.dat"']
    for name, probe in [('mobility_vg', 'channel_mobility'), ('electrons_vg', 'channel_electrons')]:
        lines += [f'extract name="{name}" curve(v."gate",probe."{probe}") outfile="{name}.dat"']
    for name, _, _ in extra_probes:
        lines += [f'extract name="{name}_vg" curve(v."gate",probe."{name}") outfile="{name}_vg.dat"']
    if resistance:
        for terminal in ('source', 'drain'):
            lines += [f'extract name="{terminal}_internal_vg" curve(v."gate",vint."{terminal}") outfile="{terminal}_internal_vg.dat"']
    if plots:
        lines += ['tonyplot '+name for name in ['geometry.str', 'equilibrium.str', 'off.str', 'final.str', 'transfer.log']]
    lines += ['quit', '']
    meta = {'status': 'UNVALIDATED_INDEPENDENT_REBUILD', 'key': key,
            'channel_nm': c['thickness_nm'], 'region_ids': {'IWO': 2, 'Al2O3': 3, 'HfO2': 4, 'TiN_ideal': 5},
            'y_boundaries_um': [top, -t, 0, al, ox, bottom],
            'source_end_um': source_end, 'drain_start_um': drain_start,
            'probe_xy_um': [mid+.037, -t*.47], 'native_interface': '2/3 at y=0',
            'extra_probe_names': [entry[0] for entry in extra_probes],
            'surface_density_probe_distance_nm': min(1., .13*c['thickness_nm']) if depth_electrons else None,
            'external_structure_required': False, 'geometry_model': 'Direct ATLAS, screened support excluded',
            'enabled': {'bulk_DOS': d['bulk'], 'interface_DOS': d['interface'], 'mobility': mobility['mode'],
                        'contacts': contact['mode'], 'carrier_equations': carrier}}
    if colocated_prp:
        meta['colocated_prp_probe_xy_um'] = {
            'front': [mid+.037, -min(.001, .13*t)],
            'middle': [mid+.037, -t*.47],
            'back': [mid+.037, -t+min(.001, .13*t)]}
    return '\n'.join(lines), meta


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, default=ROOT/'config/rebuild_seed.json')
    p.add_argument('--key', default='2p0', choices=['2p0', '6p3', '13p2', '31p8'])
    p.add_argument('--out', type=Path, default=ROOT/'decks_rebuild/IWO_REBUILD.in')
    p.add_argument('--batch', action='store_true')
    a = p.parse_args()
    out = a.out.resolve()
    if not out.is_relative_to(ROOT):
        raise ValueError('Output must stay in project')
    deck, meta = render(load(a.config), a.key, not a.batch)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(deck, encoding='ascii')
    out.with_suffix('.json').write_text(json.dumps(meta, indent=2))
    print(out)


if __name__ == '__main__':
    main()
